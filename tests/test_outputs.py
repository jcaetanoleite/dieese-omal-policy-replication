from pathlib import Path

import json
import numpy as np
import pandas as pd


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
    """Check repository files, but ignore Git's internal checkout objects."""
    limit = 25 * 1024 * 1024

    manifest_path = ROOT / "data" / "raw" / "large_files_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    reconstructed = {ROOT / entry["target"] for entry in manifest["files"]}

    oversized = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue

        relative = path.relative_to(ROOT)

        # GitHub Actions creates .git/objects/pack files that can exceed 25 MiB.
        # They are not repository payload files and must not be tested here.
        if ".git" in relative.parts:
            continue

        # Ignore common local caches and virtual environments.
        if any(
            part in {".venv", "venv", "__pycache__", ".pytest_cache"}
            for part in relative.parts
        ):
            continue

        # Reassembled source files can exceed the browser-upload limit by design.
        if path in reconstructed:
            continue

        if path.stat().st_size > limit:
            oversized.append(relative)

    assert not oversized, oversized


def test_large_file_manifest_has_three_reassemblies():
    manifest_path = ROOT / "data" / "raw" / "large_files_manifest.json"
    data = json.loads(manifest_path.read_text(encoding="utf-8"))

    assert len(data["files"]) == 3

    expected_targets = {
        "data/raw/ibge_pof/Dados_20230713.zip",
        "data/raw/ibge_ipca/tabela7060_19.xlsx",
        "data/raw/ibge_ipca/tabela7060_20.xlsx",
    }
    targets = {entry["target"] for entry in data["files"]}
    assert targets == expected_targets

    for entry in data["files"]:
        for part in entry["parts"]:
            assert (ROOT / part).exists(), part
