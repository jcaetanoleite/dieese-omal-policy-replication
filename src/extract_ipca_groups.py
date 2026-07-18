"""Prepare local monthly IPCA series for all nine expenditure groups.

Default mode combines the browser-safe parsed extracts included in data/interim.
Use ``--from-xlsx`` to parse the two original SIDRA workbooks directly. The
second workbook is very large and can take several minutes to stream.
"""
from __future__ import annotations

import argparse
import csv
import re
import time
from pathlib import Path
from zipfile import ZipFile
from lxml import etree

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "ibge_ipca"
INTERIM = ROOT / "data" / "interim"
INTERIM.mkdir(parents=True, exist_ok=True)

TARGET_TERRITORIES = {
    "Rio Branco (AC)": "Rio Branco", "São Luís (MA)": "São Luís", "Aracaju (SE)": "Aracaju",
    "Campo Grande (MS)": "Campo Grande", "Goiânia (GO)": "Goiânia", "Brasília (DF)": "Brasília",
    "Belém (PA)": "Belém", "Fortaleza (CE)": "Fortaleza", "Recife (PE)": "Recife", "Salvador (BA)": "Salvador",
    "Belo Horizonte (MG)": "Belo Horizonte", "Grande Vitória (ES)": "Grande Vitória",
    "Rio de Janeiro (RJ)": "Rio de Janeiro", "São Paulo (SP)": "São Paulo",
    "Curitiba (PR)": "Curitiba", "Porto Alegre (RS)": "Porto Alegre",
}
IPCA_CATEGORIES = {
    "Índice geral": "general", "1.Alimentação e bebidas": "g1_food", "2.Habitação": "g2_housing",
    "3.Artigos de residência": "g3_household_articles", "4.Vestuário": "g4_clothing",
    "5.Transportes": "g5_transport", "6.Saúde e cuidados pessoais": "g6_health_personal",
    "7.Despesas pessoais": "g7_personal_expenses", "8.Educação": "g8_education", "9.Comunicação": "g9_communication",
}
NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
MONTHS_PT = {"janeiro":1,"fevereiro":2,"março":3,"abril":4,"maio":5,"junho":6,"julho":7,"agosto":8,"setembro":9,"outubro":10,"novembro":11,"dezembro":12}
FIELDS = ["city","territory","category","group_key","date","monthly_change_pct"]


def parse_month(value):
    if not value: return None
    match = re.match(r"([a-zç]+)\s+(\d{4})", str(value).strip().lower())
    if not match: return None
    return f"{int(match.group(2)):04d}-{MONTHS_PT[match.group(1)]:02d}-01"


def col_idx(ref):
    letters = "".join(ch for ch in ref if ch.isalpha()); n = 0
    for ch in letters: n = n * 26 + (ord(ch.upper()) - 64)
    return n - 1


def load_shared(z):
    values = []
    with z.open("xl/sharedStrings.xml") as f: tree = etree.parse(f)
    for si in tree.getroot().iter(NS + "si"):
        values.append("".join((t.text or "") for t in si.iter(NS + "t")))
    return values


def cell_value(cell, shared):
    kind = cell.get("t"); value = cell.find(NS + "v")
    if value is None:
        inline = cell.find(NS + "is")
        return "".join((t.text or "") for t in inline.iter(NS + "t")) if inline is not None else None
    raw = value.text
    if kind == "s":
        try: return shared[int(raw)]
        except Exception: return None
    try: return float(raw)
    except Exception: return raw


def extract_xlsx(path: Path, wanted: set[str]):
    rows = []; nrows = 0; started = time.time()
    with ZipFile(path) as z:
        shared = load_shared(z)
        with z.open("xl/worksheets/sheet1.xml") as f:
            context = etree.iterparse(f, events=("end",), tag=NS + "row")
            current_category = current_territory = current_month = None
            for _, row in context:
                nrows += 1; values = [None] * 7
                for cell in row.iter(NS + "c"):
                    j = col_idx(cell.get("r", "A1"))
                    if j < 7: values[j] = cell_value(cell, shared)
                c0, _, _, c3, c4, c5, c6 = values
                if c0 is not None: current_category = str(c0).strip()
                if c3 is not None: current_territory = str(c3).strip()
                if c4 is not None: current_month = str(c4).strip()
                if current_category in wanted and current_territory in TARGET_TERRITORIES and c5 == "IPCA - Variação mensal (%)":
                    date = parse_month(current_month)
                    try: value = float(c6)
                    except Exception: value = None
                    if date and value is not None:
                        rows.append({"city":TARGET_TERRITORIES[current_territory],"territory":current_territory,"category":current_category,"group_key":IPCA_CATEGORIES[current_category],"date":date,"monthly_change_pct":value})
                row.clear()
                while row.getprevious() is not None: del row.getparent()[0]
    print(path.name, f"{nrows:,} rows scanned", f"{len(rows):,} observations", f"{time.time()-started:.1f}s")
    return rows


def read_extract(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def add_cumulative_index(rows):
    rows.sort(key=lambda r: (r["city"], r["group_key"], r["date"]))
    last = None; index = 1.0
    for row in rows:
        key = (row["city"], row["group_key"])
        if key != last: index = 1.0; last = key
        index *= 1 + float(row["monthly_change_pct"]) / 100
        row["cum_index"] = index
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--from-xlsx", action="store_true", help="Parse original workbooks instead of included CSV extracts")
    args = parser.parse_args()
    if args.from_xlsx:
        rows = extract_xlsx(RAW / "tabela7060_19.xlsx", {"Índice geral", "1.Alimentação e bebidas"})
        rows += extract_xlsx(RAW / "tabela7060_20.xlsx", set(IPCA_CATEGORIES) - {"Índice geral", "1.Alimentação e bebidas"})
        for name, subset in [("ipca_groups_part19.csv", rows[:0])]:
            pass
    else:
        rows = read_extract(INTERIM / "ipca_groups_part19.csv") + read_extract(INTERIM / "ipca_groups_part20.csv")
        print("Using included parsed IPCA extracts. Add --from-xlsx for a strict raw-workbook parse.")
    rows = add_cumulative_index(rows)
    output = INTERIM / "ipca_all_groups_city_monthly.csv"
    with output.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS + ["cum_index"])
        writer.writeheader(); writer.writerows(rows)
    print(f"Wrote {output.relative_to(ROOT)} with {len(rows):,} rows")


if __name__ == "__main__":
    main()
