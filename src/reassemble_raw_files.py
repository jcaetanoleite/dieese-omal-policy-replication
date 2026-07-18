"""Reassemble raw files split into browser-safe chunks.

The GitHub web interface documents a 25 MiB per-file limit. To keep a wide
safety margin, this repository stores three larger public-data files as 8 MiB byte chunks. Running this script concatenates
the chunks, verifies SHA-256 checksums, and extracts the POF translator files.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data" / "raw" / "large_files_manifest.json"


def file_sha256(path: Path, chunk_size: int = 1024 * 1024) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while block := f.read(chunk_size):
            h.update(block)
    return h.hexdigest()


def reassemble(entry: dict) -> Path:
    target = ROOT / entry["target"]
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("wb") as out:
        for rel in entry["parts"]:
            out.write((ROOT / rel).read_bytes())
    digest = file_sha256(target)
    if digest != entry["sha256"]:
        target.unlink(missing_ok=True)
        raise RuntimeError(f"Checksum mismatch for {target}: {digest}")
    print(f"Reassembled {target.relative_to(ROOT)} ({target.stat().st_size:,} bytes)")
    return target


def extract_translators() -> None:
    archive = ROOT / "data" / "raw" / "ibge_pof" / "supporting_files" / "Tradutores_20230713.zip"
    out_dir = ROOT / "data" / "raw" / "ibge_pof" / "translators"
    out_dir.mkdir(parents=True, exist_ok=True)
    wanted = {"Tradutor_Despesa_Geral.xls"}
    with ZipFile(archive) as z:
        for member in z.namelist():
            if Path(member).name in wanted:
                destination = out_dir / Path(member).name
                destination.write_bytes(z.read(member))
                print(f"Extracted {destination.relative_to(ROOT)}")


def main() -> None:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    for entry in data["files"]:
        target = ROOT / entry["target"]
        if target.exists() and file_sha256(target) == entry["sha256"]:
            print(f"Already valid: {target.relative_to(ROOT)}")
        else:
            reassemble(entry)
    extract_translators()


if __name__ == "__main__":
    main()
