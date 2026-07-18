"""Recreate article figures 1-14 from raw and processed data.

The visual style is intentionally simple. Exact publication PNGs are also tracked
in outputs/figures, so users can compare regenerated and archived versions.
"""
from __future__ import annotations

import re
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, PercentFormatter

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROC = ROOT / "data" / "processed" / "article"
INTERIM = ROOT / "data" / "interim"
OUT = ROOT / "outputs" / "figures"
OUT.mkdir(parents=True, exist_ok=True)

REGIONS = {
    "North": ["Rondônia", "Acre", "Amazonas", "Roraima", "Pará", "Amapá", "Tocantins"],
    "Northeast": ["Maranhão", "Piauí", "Ceará", "Rio Grande do Norte", "Paraíba", "Pernambuco", "Alagoas", "Sergipe", "Bahia"],
    "Southeast": ["Minas Gerais", "Espírito Santo", "Rio de Janeiro", "São Paulo"],
    "South": ["Paraná", "Santa Catarina", "Rio Grande do Sul"],
    "Center-West": ["Mato Grosso do Sul", "Mato Grosso", "Goiás", "Distrito Federal"],
}


def br_number(value: str) -> float:
    return float(value.replace(".", "").replace(",", "."))


def parse_ipea(path: Path, value_name: str) -> pd.DataFrame:
    text = path.read_text(encoding="utf-8-sig")
    rows = [(pd.Timestamp(int(y), int(m), 1), br_number(v)) for y, m, v in re.findall(r"^(\d{4})\.(\d{2})\s+([\d.]+,\d{2})$", text, re.M)]
    return pd.DataFrame(rows, columns=["date", value_name])


def parse_dieese() -> pd.DataFrame:
    text = (RAW / "dieese" / "dieese_minimum_wage_monthly_1994_2026.txt").read_text(encoding="utf-8-sig")
    months = {m: i for i, m in enumerate(["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"], 1)}
    year = None; rows = []
    pattern = re.compile(r"^(Janeiro|Fevereiro|Março|Abril|Maio|Junho|Julho|Agosto|Setembro|Outubro|Novembro|Dezembro)\s+R\$\s*([\d.]+,\d{2})\s+R\$\s*([\d.]+,\d{2})$")
    for line in text.splitlines():
        line = line.strip()
        if re.fullmatch(r"\d{4}", line):
            year = int(line); continue
        match = pattern.match(line)
        if match and year:
            rows.append((pd.Timestamp(year, months[match.group(1)], 1), br_number(match.group(2)), br_number(match.group(3))))
    return pd.DataFrame(rows, columns=["date", "minimum_nominal", "dieese_necessary"])


def money(x, _): return f"R$ {x:,.0f}"

def save(fig, n):
    p = OUT / f"figure{n:02d}_regenerated.png"
    fig.tight_layout(); fig.savefig(p, dpi=300, bbox_inches="tight"); plt.close(fig)
    print(p.relative_to(ROOT))


def state_income_table() -> pd.DataFrame:
    return pd.read_csv(PROC / "state_income_relative_dieese_2025.csv")


def parse_state_labour_income() -> pd.DataFrame:
    raw = pd.read_excel(RAW / "ibge_pnad" / "tabela6472_labour_income.xlsx", sheet_name="Tabela", header=None)
    labels = list(raw.iloc[3, 3:].dropna())
    rows=[]
    for i in range(5, len(raw)):
        if str(raw.iloc[i,0]).strip() != "UF": continue
        state=str(raw.iloc[i,2]).strip(); values=raw.iloc[i,3:3+len(labels)].tolist()
        for label,value in zip(labels,values):
            m=re.match(r"(\d)º trimestre (\d{4})",str(label))
            try: value=float(value)
            except: continue
            if m: rows.append((state,pd.Period(year=int(m.group(2)),quarter=int(m.group(1)),freq="Q"),value))
    return pd.DataFrame(rows,columns=["state","quarter","labour_income_real"])


def main():
    real = parse_ipea(RAW / "ipea" / "ipea_real_minimum_wage_1940_2026.txt", "minimum_real")
    ppp = parse_ipea(RAW / "ipea" / "ipea_ppp_minimum_wage_1940_2026.txt", "minimum_ppp_2011")
    dieese = parse_dieese()

    # 1
    fig,ax=plt.subplots(figsize=(10,5.5)); ax.plot(real.date,real.minimum_real,alpha=.25,label="Monthly value")
    ax.plot(real.date,real.minimum_real.rolling(12).mean(),label="12-month moving average")
    ax.set_title("Brazilian real minimum wage, July 1940 to June 2026"); ax.set_ylabel("R$ of June 2026")
    ax.yaxis.set_major_formatter(FuncFormatter(money)); ax.grid(axis="y",alpha=.3); ax.legend(frameon=False)
    save(fig,1)

    # 2
    food=pd.read_csv(PROC/"food_expenditure_shares.csv")
    x=np.arange(len(food)); fig,ax=plt.subplots(figsize=(9,5.5))
    ax.bar(x-.18,food.lowest_income_group_pct,width=.36,label="Lowest income group")
    ax.bar(x+.18,food.highest_income_group_pct,width=.36,label="Highest income group")
    ax.set_xticks(x);ax.set_xticklabels(food.survey);ax.set_ylabel("Share of consumption expenditure")
    ax.yaxis.set_major_formatter(PercentFormatter());ax.set_title("Food expenditure shares at the bottom and top of the income distribution")
    ax.legend(frameon=False);ax.grid(axis="y",alpha=.3);save(fig,2)

    # 3-4
    q=dieese.merge(real,on="date",how="left"); q["deflator"]=q.minimum_real/q.minimum_nominal
    q["dieese_pc_current"]=q.dieese_necessary/4; q["ratio"]=q.dieese_pc_current/q.minimum_nominal
    fig,ax=plt.subplots(figsize=(10,5.5));ax.plot(q.date,q.dieese_pc_current,label="DIEESE benchmark divided by four");ax.plot(q.date,q.minimum_nominal,label="Statutory minimum wage")
    ax.set_title("Statutory minimum wage and the per-capita DIEESE benchmark, 1994-2026");ax.set_ylabel("Current R$");ax.yaxis.set_major_formatter(FuncFormatter(money));ax.legend(frameon=False);ax.grid(axis="y",alpha=.3);save(fig,3)
    fig,ax=plt.subplots(figsize=(10,5.5));ax.plot(q.date,q.ratio*100);ax.axhline(100,linestyle="--");ax.set_title("Per-capita DIEESE benchmark as a share of the statutory minimum wage, 1994-2026");ax.set_ylabel("Percent");ax.yaxis.set_major_formatter(PercentFormatter());ax.grid(axis="y",alpha=.3);save(fig,4)

    # 5
    s=state_income_table().sort_values("household_income_per_capita_as_pct_of_dieese_per_capita")
    fig,ax=plt.subplots(figsize=(8,10));ax.barh(s.state,s.household_income_per_capita_as_pct_of_dieese_per_capita);ax.axvline(100,linestyle="--")
    ax.xaxis.set_major_formatter(PercentFormatter());ax.set_title("State household income per capita relative to the per-capita DIEESE benchmark, 2025");save(fig,5)

    # quarterly per-person real benchmark and state series, figures 6-10
    q["dieese_pc_real"]=q.dieese_necessary*q.deflator/4; q["quarter"]=q.date.dt.to_period("Q")
    bench=q.groupby("quarter",as_index=False).dieese_pc_real.mean()
    states=parse_state_labour_income().merge(bench,on="quarter",how="left")
    for n,(region,state_list) in enumerate(REGIONS.items(),6):
        g=states[states.state.isin(state_list)];fig,ax=plt.subplots(figsize=(10,5.7))
        for state,h in g.groupby("state"):ax.plot(h.quarter.dt.to_timestamp(),h.labour_income_real,label=state)
        b=g.drop_duplicates("quarter");ax.plot(b.quarter.dt.to_timestamp(),b.dieese_pc_real,linestyle="--",linewidth=2,label="DIEESE benchmark per person")
        ax.set_title(f"{region}: real labour income and the DIEESE benchmark, 2012-2026");ax.set_ylabel("R$ at 2026 Q1 prices");ax.yaxis.set_major_formatter(FuncFormatter(money));ax.legend(frameon=False,ncol=3,fontsize=8);ax.grid(axis="y",alpha=.3);save(fig,n)

    # 11
    inf=pd.read_csv(INTERIM/"informality_dieese_ratio_state_quarter.csv")
    order=list(REGIONS);fig,axes=plt.subplots(3,2,figsize=(10,12),sharex=True,sharey=True);axes=axes.ravel()
    for ax,region in zip(axes,order):
        g=inf[inf.region==region];ax.scatter(g.informality_rate,g.ratio_pct,s=12,alpha=.45)
        if len(g):
            m,b=np.polyfit(g.informality_rate,g.ratio_pct,1);xx=np.linspace(g.informality_rate.min(),g.informality_rate.max(),100);ax.plot(xx,m*xx+b)
        ax.set_title(region);ax.grid(alpha=.25)
    axes[-1].axis("off");fig.supylabel("Average labour income / DIEESE benchmark per person (%)");fig.supxlabel("Informality rate (%)");fig.suptitle("Informality and the distance from the DIEESE benchmark")
    save(fig,11)

    # 12-13
    brazil=pd.read_excel(RAW/"other"/"kaitz_brazil_oecd.xlsx",sheet_name="Brasil_2012_2023")
    fig,ax=plt.subplots(figsize=(9,5.5));ax.plot(brazil.Ano,brazil["Kaitz ampliado — piso legal"]*100,marker="o",label="Statutory minimum / median labour income")
    ax.plot(brazil.Ano,brazil["Sensibilidade DIEESE ÷ 4"]*100,marker="o",label="DIEESE benchmark divided by four / median income")
    ax.yaxis.set_major_formatter(PercentFormatter());ax.set_title("Kaitz-style ratios for Brazil, 2012-2023");ax.legend(frameon=False);ax.grid(axis="y",alpha=.3);save(fig,12)
    oecd=pd.read_excel(RAW/"other"/"kaitz_brazil_oecd.xlsx",sheet_name="OCDE_2025")
    oecd=oecd[oecd["País/economia"]!="OECD"].copy();oecd=oecd.sort_values("Kaitz 2025 ou último (%)")
    extra=pd.DataFrame({"País/economia":["Brazil, statutory minimum (2023)","Brazil, DIEESE divided by four (2023)"],"Kaitz 2025 ou último (%)":[.731,.901962]})
    o=pd.concat([oecd[["País/economia","Kaitz 2025 ou último (%)"]],extra],ignore_index=True).sort_values("Kaitz 2025 ou último (%)")
    fig,ax=plt.subplots(figsize=(8,11));ax.barh(o["País/economia"],o["Kaitz 2025 ou último (%)"]*100);ax.axvline(.555753*100,linestyle="--");ax.xaxis.set_major_formatter(PercentFormatter());ax.set_title("Minimum wages relative to median wages: Brazil and OECD economies");save(fig,13)

    # 14
    annual_real=real.assign(year=real.date.dt.year).groupby("year",as_index=False).minimum_real.mean()
    annual_ppp=ppp.assign(year=ppp.date.dt.year).groupby("year",as_index=False).minimum_ppp_2011.mean()
    factor=annual_ppp.loc[annual_ppp.year==2021,"minimum_ppp_2011"].iloc[0]/annual_real.loc[annual_real.year==2021,"minimum_real"].iloc[0]
    annual=annual_real.copy();annual["minimum_ppp_2021"]=annual.minimum_real*factor
    lines=pd.read_csv(PROC/"world_bank_poverty_lines_2021_ppp.csv"); monthly_lines={r.line:r.international_dollars_per_person_per_day*365/12 for _,r in lines.iterrows()}
    fig,(ax1,ax2)=plt.subplots(2,1,figsize=(10,8),sharex=True)
    ax1.plot(annual.year,annual.minimum_ppp_2021,label="Annual average minimum wage")
    for name,value in monthly_lines.items():ax1.axhline(value,linestyle="--",label=name)
    ax1.set_ylabel("2021 international dollars per month");ax1.legend(frameon=False,ncol=2);ax1.grid(axis="y",alpha=.3)
    for name,value in monthly_lines.items():ax2.plot(annual.year,annual.minimum_ppp_2021/value,label=name)
    ax2.axhline(1,linestyle="--");ax2.set_ylabel("Number of person-month poverty lines");ax2.set_xlabel("Year");ax2.grid(axis="y",alpha=.3);ax2.legend(frameon=False,ncol=2)
    fig.suptitle("Brazilian minimum wage and international poverty lines on a constant 2021-PPP basis");save(fig,14)


if __name__ == "__main__": main()
