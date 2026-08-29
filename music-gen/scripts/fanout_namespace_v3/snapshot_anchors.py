#!/usr/bin/python3
"""Snapshot SHA-256 of key anchor files for c39 Branch C.

Reads current file bytes and writes a JSON report to
data/fanout_namespace_v3/anchor_preservation.json. Run twice:
once BEFORE any edits (labels 'pre'), once after (labels 'post').
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent

import long_exposure.workspace_bootstrap as wb  # noqa: E402
import long_exposure.tools._ledger_schema as ls_mod  # noqa: E402

WB_PATH = pathlib.Path(wb.__file__)
LS_PATH = pathlib.Path(ls_mod.__file__)

TARGETS = [
    ("c14_ledger_schema", LS_PATH),
    ("c33_guard_fixture", ROOT / "tests/fixtures/harness_clone_namespace_guard_rubric_hash.txt"),
    ("c32_convention_doc_v1_prev_path", ROOT / "docs/fanout_namespace_convention.md"),
    ("c32_convention_doc_v1_new_path", ROOT / "docs/fanout_namespace_convention_v1.md"),
    ("c36_convention_doc_v2", ROOT / "docs/fanout_namespace_convention_v2.md"),
    ("c39_convention_doc_v3", ROOT / "docs/fanout_namespace_convention_v3.md"),
    ("c39_rubric_doc", ROOT / "docs/fanout_namespace_convention_v3_rubric.md"),
    ("workspace_bootstrap_source", WB_PATH),
]


def sha256(path: pathlib.Path) -> str | None:
    if not path.exists():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def snapshot(label: str) -> dict:
    return {
        "label": label,
        "targets": {name: sha256(p) for name, p in TARGETS},
        "fanout_infra_prefixes": list(wb._FANOUT_INFRA_PREFIXES),
    }


def main() -> None:
    label = sys.argv[1] if len(sys.argv) > 1 else "pre"
    out = ROOT / "data/fanout_namespace_v3/anchor_preservation.json"
    if out.exists():
        current = json.loads(out.read_text())
    else:
        current = {}
    current[label] = snapshot(label)
    out.write_text(json.dumps(current, indent=2, sort_keys=True) + "\n")
    print(json.dumps(current[label], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
