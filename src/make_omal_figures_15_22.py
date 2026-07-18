"""Recreate OMAL figures 15-22 from processed tables."""
from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, PercentFormatter

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed" / "omal"
OUT = ROOT / "outputs" / "figures"
OUT.mkdir(parents=True, exist_ok=True)


def money_fmt(x, _):
    return f"R$ {x:,.0f}"


def save(fig, number: int):
    path = OUT / f"figure{number:02d}.png"
    fig.tight_layout()
    fig.savefig(path, dpi=320, bbox_inches="tight")
    plt.close(fig)
    print(path.relative_to(ROOT))


def main() -> None:
    hh = pd.read_csv(DATA / "omal_fullgroups_latest_household_types.csv")
    monthly = pd.read_csv(DATA / "omal_fullgroups_monthly_2020_2026.csv", parse_dates=["date"])
    comparison = pd.read_csv(DATA / "omal_fullgroups_comparison_old_new.csv")

    standard = hh[hh["household_type"] == "2 adults + 2 children"].copy()
    core = standard[standard["variant"] == "core"].copy()
    expanded = standard[standard["variant"] == "expanded"].copy()
    monthly_core = monthly[(monthly["variant"] == "core") & (monthly["household_type"] == "2 adults + 2 children")].copy()

    group_labels = {
        "g1_food": "Food and beverages", "g2_housing": "Housing",
        "g3_household_articles": "Household articles", "g4_clothing": "Clothing",
        "g5_transport": "Transport", "g6_health_personal": "Health and personal care",
        "g7_personal_expenses": "Personal expenses", "g8_education": "Education",
        "g9_communication": "Communication",
    }
    groups = list(group_labels)

    # Figure 15
    rank = core[["city", "omal_total"]].merge(
        expanded[["city", "omal_total"]].rename(columns={"omal_total": "expanded_total"}), on="city"
    ).sort_values("omal_total")
    fig, ax = plt.subplots(figsize=(10, 7))
    y = np.arange(len(rank))
    ax.barh(y - .18, rank["omal_total"], height=.35, label="Core basket")
    ax.barh(y + .18, rank["expanded_total"], height=.35, label="Expanded basket")
    ax.set_yticks(y); ax.set_yticklabels(rank["city"])
    ax.xaxis.set_major_formatter(FuncFormatter(money_fmt))
    ax.set_title("OMAL by city, June 2026"); ax.set_xlabel("Monthly family budget")
    ax.grid(axis="x", alpha=.3); ax.legend(frameon=False)
    ax.spines[["top", "right"]].set_visible(False)
    save(fig, 15)

    # Figure 16
    components = core[["city"] + groups].sort_values("g2_housing")
    fig, ax = plt.subplots(figsize=(11, 7.2))
    bottom = np.zeros(len(components))
    for g in groups:
        ax.bar(components["city"], components[g], bottom=bottom, label=group_labels[g])
        bottom += components[g].to_numpy()
    ax.set_title("Composition of the core OMAL basket, June 2026")
    ax.set_ylabel("Monthly family budget"); ax.yaxis.set_major_formatter(FuncFormatter(money_fmt))
    ax.tick_params(axis="x", rotation=70); ax.grid(axis="y", alpha=.3)
    ax.legend(frameon=False, bbox_to_anchor=(1.01, 1), loc="upper left")
    ax.spines[["top", "right"]].set_visible(False)
    save(fig, 16)

    # Figure 17
    selected = [core.loc[core.omal_total.idxmax(), "city"], core.loc[core.omal_total.idxmin(), "city"],
                "Rio de Janeiro", "Brasília", "Belém", "Recife"]
    fig, ax = plt.subplots(figsize=(11, 6.5))
    for city, g in monthly_core[monthly_core.city.isin(selected)].groupby("city"):
        ax.plot(g.date, g.omal_total, label=city)
    ax.set_title("Core OMAL over time in selected cities"); ax.set_ylabel("Monthly family budget")
    ax.yaxis.set_major_formatter(FuncFormatter(money_fmt)); ax.grid(axis="y", alpha=.3)
    ax.legend(frameon=False, ncol=2); ax.spines[["top", "right"]].set_visible(False)
    fig.autofmt_xdate(); save(fig, 17)

    # Figure 18
    core["ratio_to_income"] = core.omal_total / core.labour_income_real
    plot = core.dropna(subset=["labour_income_real"]).sort_values("ratio_to_income")
    if plot.empty:
        raise RuntimeError("No matched PNAD labour-income values. Run src/prepare_pnad_city_income.py and src/build_omal_series.py before making figures.")
    fig, ax = plt.subplots(figsize=(8.4, 6.8))
    ax.scatter(plot.labour_income_real, plot.omal_total)
    for _, r in plot.iterrows():
        ax.annotate(r.city, (r.labour_income_real, r.omal_total), fontsize=8, xytext=(3, 4), textcoords="offset points")
    lo = min(plot.labour_income_real.min(), plot.omal_total.min()) * .95
    hi = max(plot.labour_income_real.max(), plot.omal_total.max()) * 1.05
    ax.plot([lo, hi], [lo, hi], linestyle="--"); ax.set_xlim(lo, hi); ax.set_ylim(lo, hi)
    ax.xaxis.set_major_formatter(FuncFormatter(money_fmt)); ax.yaxis.set_major_formatter(FuncFormatter(money_fmt))
    ax.set_title("Mean labour income and the core OMAL")
    ax.set_xlabel("Mean real labour income, 2026 Q1"); ax.set_ylabel("Core OMAL, June 2026")
    ax.grid(alpha=.3); ax.spines[["top", "right"]].set_visible(False)
    save(fig, 18)

    # Figure 19
    chg = comparison[comparison.variant == "core"].sort_values("percent_change")
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.barh(chg.city, chg.percent_change * 100)
    ax.set_title("Effect of using all nine IPCA groups")
    ax.set_xlabel("Percent change relative to the simplified update rule")
    ax.xaxis.set_major_formatter(PercentFormatter()); ax.grid(axis="x", alpha=.3)
    ax.spines[["top", "right"]].set_visible(False)
    save(fig, 19)

    # Figure 20
    ratio = core[["city", "omal_total", "dieese_family_benchmark"]].copy()
    ratio["ratio"] = ratio.omal_total / ratio.dieese_family_benchmark
    ratio = ratio.sort_values("ratio")
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.barh(ratio.city, ratio.ratio * 100)
    ax.set_title("Core OMAL as a share of the DIEESE benchmark")
    ax.set_xlabel("Core OMAL / DIEESE family benchmark")
    ax.xaxis.set_major_formatter(PercentFormatter()); ax.grid(axis="x", alpha=.3)
    ax.spines[["top", "right"]].set_visible(False)
    save(fig, 20)

    # Figure 21
    average = hh[hh.variant == "core"].groupby("household_type", as_index=False).omal_total.mean()
    order = ["1 adult", "1 adult + 1 child", "1 adult + 2 children", "2 adults", "2 adults + 1 child", "2 adults + 2 children"]
    average["household_type"] = pd.Categorical(average.household_type, categories=order, ordered=True)
    average = average.sort_values("household_type")
    fig, ax = plt.subplots(figsize=(10, 6.2))
    ax.bar(average.household_type, average.omal_total)
    ax.set_title("Average core OMAL by household type"); ax.set_ylabel("Monthly family budget")
    ax.yaxis.set_major_formatter(FuncFormatter(money_fmt)); ax.tick_params(axis="x", rotation=35)
    ax.grid(axis="y", alpha=.3); ax.spines[["top", "right"]].set_visible(False)
    save(fig, 21)

    # Figure 22
    compare = core[["city", "omal_total", "labour_income_real", "statutory_minimum"]].dropna().copy()
    compare["per_worker"] = compare.omal_total / 2
    compare = compare.sort_values("per_worker")
    y = np.arange(len(compare))
    fig, ax = plt.subplots(figsize=(11, 7.4))
    ax.barh(y - .25, compare.per_worker, height=.24, label="OMAL per worker (2 workers)")
    ax.barh(y, compare.labour_income_real, height=.24, label="Mean labour income")
    ax.barh(y + .25, compare.statutory_minimum, height=.24, label="Statutory minimum wage")
    ax.set_yticks(y); ax.set_yticklabels(compare.city); ax.xaxis.set_major_formatter(FuncFormatter(money_fmt))
    ax.set_title("Per-worker OMAL, mean earnings and the legal minimum"); ax.set_xlabel("Monthly income")
    ax.grid(axis="x", alpha=.3); ax.legend(frameon=False); ax.spines[["top", "right"]].set_visible(False)
    save(fig, 22)


if __name__ == "__main__":
    main()
