from pathlib import Path
import json
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OMAL = ROOT / "data" / "processed" / "omal"


def test_omal_summary_has_sixteen_cities():
    df = pd.read_csv(OMAL / "omal_fullgroups_summary_june2026.csv")
    assert len(df) == 16
    assert df["city"].nunique() == 16


def test_nine_components_sum_to_total():
    df = pd.read_csv(OMAL / "omal_fullgroups_latest_household_types.csv")
    groups = [c for c in df.columns if c.startswith("g") and c[1:2].isdigit()]
    assert len(groups) == 9
    difference = (df[groups].sum(axis=1) - df["omal_total"]).abs().max()
    assert difference < 1e-6


def test_reference_values():
    df = pd.read_csv(OMAL / "omal_fullgroups_summary_june2026.csv")
    assert np.isclose(df["statutory_minimum"].dropna().iloc[0], 1621.0)
    assert np.isclose(df["dieese_family_benchmark"].dropna().iloc[0], 8110.92)
    assert df["date"].max().startswith("2026-06")


def test_all_article_figures_are_present():
    for number in range(1, 23):
        assert (ROOT / "outputs" / "figures" / f"figure{number:02d}.png").exists()


def test_browser_safe_file_sizes():
    limit = 25 * 1024 * 1024
    manifest = json.loads((ROOT / "data" / "raw" / "large_files_manifest.json").read_text(encoding="utf-8"))
    reconstructed = {ROOT / entry["target"] for entry in manifest["files"]}
    oversized = [
        p for p in ROOT.rglob("*")
        if p.is_file() and p.stat().st_size > limit and p not in reconstructed
    ]
    assert not oversized, oversized


def test_large_file_manifest_has_three_reassemblies():
    data = json.loads((ROOT / "data" / "raw" / "large_files_manifest.json").read_text(encoding="utf-8"))
    targets = {entry["target"] for entry in data["files"]}
    assert targets == {
        "data/raw/ibge_pof/Dados_20230713.zip",
        "data/raw/ibge_ipca/tabela7060_19.xlsx",
        "data/raw/ibge_ipca/tabela7060_20.xlsx",
    }


def test_pnad_city_names_match_omal_cities():
    pnad = pd.read_csv(ROOT / "data" / "interim" / "pnad_city_labour_income_quarterly.csv")
    summary = pd.read_csv(OMAL / "omal_fullgroups_summary_june2026.csv")
    assert set(summary["city"]).issubset(set(pnad["city"]))
    assert summary["labour_income_real"].notna().all()
