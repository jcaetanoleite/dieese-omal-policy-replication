"""Extract quarterly mean real labour income for Brazilian capitals from SIDRA table 6472."""
from __future__ import annotations

import re
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data" / "raw" / "ibge_pnad" / "tabela6472_labour_income.xlsx"
OUTPUT = ROOT / "data" / "interim" / "pnad_city_labour_income_quarterly.csv"


def parse_quarter(label: str) -> str | None:
    match = re.match(r"(\d)º trimestre (\d{4})", str(label))
    if not match:
        return None
    return f"{match.group(2)}Q{match.group(1)}"


CITY_RENAMES = {
    "Vitória": "Grande Vitória",
}


def normalize_city(value: str) -> str:
    """Remove the UF suffix used by SIDRA and harmonise OMAL city names."""
    city = re.sub(r"\s*\([A-Z]{2}\)$", "", str(value).strip())
    return CITY_RENAMES.get(city, city)


def main() -> None:
    raw = pd.read_excel(INPUT, sheet_name="Tabela", header=None)
    quarter_labels = list(raw.iloc[3, 3:].dropna())
    rows = []
    for i in range(5, len(raw)):
        if str(raw.iloc[i, 0]).strip() != "MU":
            continue
        city = normalize_city(raw.iloc[i, 2])
        values = raw.iloc[i, 3:3 + len(quarter_labels)].tolist()
        for label, value in zip(quarter_labels, values):
            q = parse_quarter(label)
            try:
                value = float(value)
            except (TypeError, ValueError):
                continue
            if q:
                rows.append({"city": city, "quarter": q, "labour_income_real": value})
    out = pd.DataFrame(rows).sort_values(["city", "quarter"])
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUTPUT, index=False, encoding="utf-8-sig")
    print(f"Wrote {OUTPUT.relative_to(ROOT)} with {len(out):,} rows")


if __name__ == "__main__":
    main()
