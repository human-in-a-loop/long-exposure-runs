#!/usr/bin/python3
"""v2.1 anchor preservation manifest — snapshots 32+ SHA-256 anchors pre/post."""
# created: 2026-08-29T17:08:00Z  cycle: 47  run_id: run-2026-08-28T040704Z
# agent: worker  milestone: M-EAR-1/real-label-training-v2.1
from __future__ import annotations

import sys

print("[c47:anchor_manifest_v2p1] starting", flush=True)
assert sys.executable == "/usr/bin/python3", sys.executable

import argparse
import hashlib
import json
from pathlib import Path

ANCHOR_PATHS = [
    # c6 chassis (7 files)
    "scripts/ear/features.py",
    "scripts/ear/model.py",
    "scripts/ear/corn.py",
    "scripts/ear/leak_test.py",
    "scripts/ear/synthetic_labels.py",
    "scripts/ear/stability_metrics.py",
    "scripts/ear/stability_audit.py",
    # c22 stability harness (1 file)
    "data/ear/stability_audit/stability_report.json",
    # c26 Path B (1 file)
    "docs/ear_path_b_commitment.md",
    # c36 v0 (4 files)
    "docs/ear_v0_real_label_training_rubric.md",
    "data/ear_v0/rubric_hash.txt",
    "data/ear_v0/verdict.json",
    "data/ear_v0/corn_head_v0_real.pt",
    # c38 v1 (4 files)
    "docs/ear_real_label_training_v1_rubric.md",
    "data/ear_v1/rubric_hash.txt",
    "data/ear_v1/verdict.json",
    "data/ear_v1/corn_head_v1.pt",
    # c45 v2 (3 files)
    "docs/ear_real_label_training_v2_rubric.md",
    "data/ear_v2/rubric_hash.txt",
    "data/ear_v2/verdict.json",
    # c46 SB3 widening (2 files)
    "data/ear_v2/sb3_control_widening_result.json",
    "data/ear_v2/determinism_check_c46.json",
    # c45 c46 adjudication (3 files)
    "docs/ear_v2_verdict_adjudication_report.md",
    "data/ear_v2/adjudication_rubric_hash.txt",
    # Rules ledger invariants (3 files)
    "data/rules/ledger.jsonl",
    "data/rules/ledger_i3_dminor.jsonl",
    "data/rules/ledger_rated_corpus.jsonl",
    # c46 policy doc (1 file)
    "docs/pre_registration_gate_policy.md",
    # v2 additional artifacts (leak/SB result)
    "data/ear_v2/leak_test_v2_summary.json",
    "data/ear_v2/sb_v2_verdict.json",
    "data/ear_v2/held_out_folds.json",
    # c45 v2 held-out predictions (used READ-ONLY by SB3 re-verdict)
    "data/ear_v2/held_out_predictions.tsv",
    # c45 v2 training_result (chassis anchor)
    "data/ear_v2/training_result.json",
    "data/ear_v2/corn_head_v2.pt",
]


def snapshot() -> dict:
    entries: dict[str, dict] = {}
    for rel in ANCHOR_PATHS:
        p = Path(rel)
        if not p.is_file():
            entries[rel] = {"present": False}
            continue
        b = p.read_bytes()
        entries[rel] = {
            "present": True,
            "sha256": hashlib.sha256(b).hexdigest(),
            "size_bytes": len(b),
            "mtime": int(p.stat().st_mtime),
        }
    return entries


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--phase", choices=["pre", "post", "final"], required=True)
    ap.add_argument("--pre-manifest", default=None,
                    help="For --phase final, path to the pre-phase manifest.")
    args = ap.parse_args()

    manifest = snapshot()
    p_out = Path(args.out)
    p_out.parent.mkdir(parents=True, exist_ok=True)
    if args.phase == "final" and args.pre_manifest:
        pre_all = json.loads(Path(args.pre_manifest).read_text())
        pre = pre_all.get("entries", pre_all)
        drift: list[dict] = []
        for rel, cur in manifest.items():
            prev = pre.get(rel, {})
            if prev.get("sha256") != cur.get("sha256"):
                drift.append({
                    "path": rel,
                    "pre_sha256": prev.get("sha256"),
                    "post_sha256": cur.get("sha256"),
                    "pre_present": prev.get("present"),
                    "post_present": cur.get("present"),
                })
        out = {
            "cycle": 47,
            "milestone": "M-EAR-1/real-label-training-v2.1/anchor-preservation-verified",
            "n_anchors": len(manifest),
            "unchanged": len(drift) == 0,
            "drift": drift,
            "pre_manifest_sha256": hashlib.sha256(
                Path(args.pre_manifest).read_bytes()
            ).hexdigest(),
            "entries": manifest,
        }
    else:
        out = {"phase": args.phase, "n_anchors": len(manifest),
               "entries": manifest}
    p_out.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "phase": args.phase,
        "n_anchors": len(manifest),
        "n_present": sum(1 for v in manifest.values() if v.get("present")),
        "unchanged": out.get("unchanged"),
        "out": str(p_out),
    }, indent=2))


if __name__ == "__main__":
    main()
