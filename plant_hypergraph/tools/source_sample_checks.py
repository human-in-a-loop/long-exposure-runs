# created: 2026-05-17T01:45:00Z
# cycle: 3
# run_id: run-2026-05-17T004540Z
# agent: worker
# milestone: M6
"""Validation helpers for the public taxonomy sample; not a baseline implementation."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def load_metadata(base: Path) -> dict:
    return json.loads((base / "metadata.json").read_text(encoding="utf-8"))


def hash_mismatches(base: Path) -> dict[str, tuple[str | None, str]]:
    metadata = load_metadata(base)
    mismatches = {}
    for rel_path, expected in metadata.get("hashes", {}).items():
        path = base / rel_path
        actual = sha256_file(path) if path.exists() else None
        if actual != expected:
            mismatches[rel_path] = (actual, expected)
    return mismatches


def leakage_group_splits(base: Path) -> dict[str, set[str]]:
    groups: dict[str, set[str]] = {}
    for row in read_csv(base / "splits.csv"):
        groups.setdefault(row["leakage_group_id"], set()).add(row["split"])
    for row in read_csv(base / "names.csv"):
        groups.setdefault(row["leakage_group_id"], set()).add(
            next(split["split"] for split in read_csv(base / "splits.csv") if split["leakage_group_id"] == row["leakage_group_id"])
        )
    return groups


def disagreement_categories(base: Path) -> set[str]:
    return {row["disagreement_category"] for row in read_csv(base / "source_crosswalk.csv")}


def source_coverage_by_seed(base: Path) -> dict[str, int]:
    return {row["query_name"]: int(row["sources_matched"]) for row in read_csv(base / "source_crosswalk.csv")}
