"""Run the replication pipeline with Python only.

Examples
--------
Quick rebuild from included processed data:
    python run_all.py --mode quick

Full rebuild from raw public data:
    python run_all.py --mode full
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

QUICK = [
    "src/make_article_figures_01_14.py",
    "src/make_omal_figures_15_22.py",
    "src/build_article.py",
]
FULL = [
    "src/reassemble_raw_files.py",
    "src/build_pof_reference.py",
    "src/extract_ipca_groups.py",
    "src/prepare_pnad_city_income.py",
    "src/build_omal_series.py",
    "src/make_article_figures_01_14.py",
    "src/make_omal_figures_15_22.py",
    "src/build_article.py",
]


def run(script: str) -> None:
    print(f"\n>>> {script}")
    subprocess.run([sys.executable, str(ROOT / script)], cwd=ROOT, check=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["quick", "full", "strict-raw"], default="quick")
    args = parser.parse_args()
    if args.mode == "quick":
        scripts = QUICK
    else:
        scripts = FULL
    for script in scripts:
        if args.mode == "strict-raw" and script == "src/extract_ipca_groups.py":
            print(f"\n>>> {script} --from-xlsx")
            subprocess.run([sys.executable, str(ROOT / script), "--from-xlsx"], cwd=ROOT, check=True)
        else:
            run(script)
    print("\nReplication completed.")


if __name__ == "__main__":
    main()
