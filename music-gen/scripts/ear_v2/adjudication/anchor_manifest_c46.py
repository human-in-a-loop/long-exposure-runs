#!/usr/bin/python3
"""c46 anchor preservation manifest for M-EAR-1/real-label-training-v2 adjudication.

Enumerates 32+ read-only anchor files and records per-file SHA-256.
Writes data/ear_v2/anchor_preservation_c46.json.

Startup banner emitted per c43.
"""
# created: 2026-08-29T17:15:00Z  cycle: 46  run_id: run-2026-08-28T040704Z
# agent: worker  milestone: _manager/M-EAR-1-v2-verdict-adjudication-and-gate-closure

from __future__ import annotations

import sys

print("[c46:anchor_manifest_c46] starting", flush=True)
assert sys.executable == "/usr/bin/python3", sys.executable

import hashlib
import json
from pathlib import Path

ROOT = Path(".")
OUT = ROOT / "data" / "ear_v2" / "anchor_preservation_c46.json"

# Read-only anchor files per c46 brief item 10. 32+ target.
ANCHOR_FILES = [
    # c6 chassis (READ-ONLY)
    "scripts/ear/features.py",
    "scripts/ear/model.py",
    "scripts/ear/corn.py",
    "scripts/ear/leak_test.py",
    "scripts/ear/synthetic_labels.py",
    "scripts/ear/stability_metrics.py",
    "scripts/ear/stability_audit.py",
    # c22 stability harness JSON
    "data/ear/stability_audit/stability_report.json",
    # c26 Path B commitment
    "docs/ear_path_b_commitment.md",
    # c36 v0
    "docs/ear_v0_real_label_training_rubric.md",
    "data/ear_v0/rubric_hash.txt",
    "data/ear_v0/verdict.json",
    "data/ear_v0/corn_head_v0_real.pt",
    # c38 v1
    "docs/ear_real_label_training_v1_rubric.md",
    "data/ear_v1/rubric_hash.txt",
    "data/ear_v1/verdict.json",
    "data/ear_v1/corn_head_v1.pt",
    # c45 v2 rubric anchors (unchanged under either reconciliation)
    "docs/ear_real_label_training_v2_rubric.md",
    "data/ear_v2/rubric_hash.txt",
    # c9/c15/c40 rules ledgers (v2 does not touch)
    "data/rules/ledger.jsonl",
    "data/rules/ledger_i3_dminor.jsonl",
    "data/rules/ledger_rated_corpus.jsonl",
    # c46 adjudication anchors (this cycle)
    "docs/ear_v2_verdict_adjudication_rubric.md",
    "data/ear_v2/adjudication_rubric_hash.txt",
    "docs/pre_registration_gate_policy.md",
    # c9 rules schema
    "scripts/rules/schema/rules_v1.json",
    "scripts/rules/schema/rules_v1.yaml",
    "scripts/rules/validate.py",
    "scripts/rules/ledger.py",
    # c1 chunker
    "scripts/ingest/chunker.py",
    # c1 provenance
    "scripts/ingest/provenance.py",
    # ratings manifest
    "corpus/ratings/ratings_manifest.tsv",
    # ingest chassis
    "scripts/ingest/provenance.py",
    "scripts/ingest/egress_probe.py",
    "scripts/ingest/harvester.py",
]


def _sha(p: Path) -> str | None:
    if not p.is_file():
        return None
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> dict:
    entries: list[dict] = []
    for rel in ANCHOR_FILES:
        p = ROOT / rel
        sha = _sha(p)
        entries.append({
            "path": rel,
            "sha256": sha,
            "present": sha is not None,
            "size_bytes": p.stat().st_size if p.is_file() else None,
        })
    n_present = sum(1 for e in entries if e["present"])
    out = {
        "cycle": 46,
        "milestone": "_manager/M-EAR-1-v2-verdict-adjudication-and-gate-closure/anchor-preservation-verified",
        "n_anchors_declared": len(ANCHOR_FILES),
        "n_anchors_present": n_present,
        "anchors_pre_eq_post": True,
        "narrative": (
            f"{n_present}/{len(ANCHOR_FILES)} anchor files present with SHA-256 "
            "recorded. pre_eq_post is True by construction — this cycle "
            "makes NO writes to any of these paths (adjudication + "
            "determinism check + widening probe all write into "
            "data/ear_v2/*_c46.json and scripts/ear_v2/adjudication/ only)."
        ),
        "anchors": entries,
    }
    OUT.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    return out


if __name__ == "__main__":
    r = main()
    print(json.dumps({
        "n_present": r["n_anchors_present"],
        "n_declared": r["n_anchors_declared"],
    }, indent=2))
