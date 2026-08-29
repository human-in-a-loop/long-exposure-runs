#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-29T14:34:50Z
# cycle: 43
# run_id: fork-c320de981fda-clone-0
# agent: worker
# milestone: M-GEN-1/palette-driven-batch-rated-corpus
# ---
"""Snapshot 30+ SHAs pre/post; assert pre==post byte-equal.

Anchors (READ-ONLY, must not drift): c33 palette_render/* + c31
palette/* + c31 palette_probe/* + c33 dawdreamer_state/* + rules
ledger*.jsonl + c37/c39/c40/c42 rubric docs + hashes + c9 effects
chain source. Manifest target ≥30 (c42 parity target 32).
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

assert sys.executable == "/usr/bin/python3", sys.executable

_REPO = Path(__file__).resolve().parents[2]


ANCHOR_FILES = [
    # c33 palette_render (4 files)
    "scripts/palette_render/__init__.py",
    "scripts/palette_render/build_assignments.py",
    "scripts/palette_render/render_stem.py",
    "scripts/palette_render/run_all.py",
    # c31 palette (5 files)
    "scripts/palette/__init__.py",
    "scripts/palette/validate.py",
    "scripts/palette/provenance.py",
    "scripts/palette/schema/palette_v1.json",
    "scripts/palette/schema/palette_v1.yaml",
    # c31 palette_probe (top-level modules only)
    "scripts/palette_probe/__init__.py",
    "scripts/palette_probe/_shared.py",
    "scripts/palette_probe/surge_xt.py",
    "scripts/palette_probe/dexed.py",
    "scripts/palette_probe/sfizz.py",
    "scripts/palette_probe/run_all.py",
    # c33 dawdreamer_state (top-level modules)
    "scripts/dawdreamer_state/__init__.py",
    "scripts/dawdreamer_state/_shared.py",
    "scripts/dawdreamer_state/probe_p1_iterate_parameters.py",
    "scripts/dawdreamer_state/probe_p2_save_preset.py",
    "scripts/dawdreamer_state/probe_p3_metadata_inspection.py",
    "scripts/dawdreamer_state/run_all.py",
    # rules ledgers (preservation invariants)
    "data/rules/ledger.jsonl",
    "data/rules/ledger_i3_dminor.jsonl",
    "data/rules/ledger_rated_corpus.jsonl",
    # rubric docs + hash files (predecessors)
    "docs/recreate_v0_report.md",
    "data/recreate_v0/rubric_hash.txt",
    "data/recreate_v0_batch/rubric_hash.txt",
    "docs/recreate_v0_full_corpus_report.md",
    "data/recreate_v0_full_corpus/rubric_hash.txt",
    "docs/rules_extraction_rated_corpus_report.md",
    "data/rules_rated_corpus/rubric_hash.txt",
    "docs/rules_harmonic_window_refinement_report.md",
    "data/rules_harmonic_window_v2/rubric_hash.txt",
    # c9 effects chain — SHA-tracked but NOT imported
    "scripts/tex/render_effects_layered.py",
]


def snapshot() -> dict:
    """Return {relpath: sha256_hex} for every existing anchor file."""
    out: dict[str, str] = {}
    for rel in ANCHOR_FILES:
        p = _REPO / rel
        if p.is_file():
            out[rel] = hashlib.sha256(p.read_bytes()).hexdigest()
    # v2 shard must remain absent
    absent_rel = "data/rules/ledger_rated_corpus_harmonic_v2.jsonl"
    absent_p = _REPO / absent_rel
    out["_absent_check__" + absent_rel] = "ABSENT" if not absent_p.exists() else "PRESENT_ERROR"
    return out


def diff(pre: dict, post: dict) -> list[dict]:
    """Return list of drift rows; empty on preservation success."""
    drift = []
    for k in sorted(set(pre) | set(post)):
        a = pre.get(k)
        b = post.get(k)
        if a != b:
            drift.append({"path": k, "pre": a, "post": b})
    return drift


def write_pre(out_dir: Path) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    snap = snapshot()
    (out_dir / "_anchor_pre.json").write_text(
        json.dumps(snap, sort_keys=True, indent=2) + "\n"
    )
    return snap


def write_post(out_dir: Path, pre: dict) -> dict:
    post = snapshot()
    (out_dir / "_anchor_post.json").write_text(
        json.dumps(post, sort_keys=True, indent=2) + "\n"
    )
    drift_rows = diff(pre, post)
    result = {
        "count": len(post),
        "unchanged": len(drift_rows) == 0,
        "drift_rows": drift_rows,
    }
    (out_dir / "anchor_preservation.json").write_text(
        json.dumps(result, sort_keys=True, indent=2) + "\n"
    )
    return result


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["pre", "post"], required=True)
    ap.add_argument("--out-dir",
                    default="data/gen_palette_batch_rated_corpus")
    args = ap.parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    if args.mode == "pre":
        s = write_pre(out_dir)
        print(json.dumps({"snapshot_size": len(s)}, sort_keys=True, indent=2))
    else:
        pre_path = out_dir / "_anchor_pre.json"
        pre = json.loads(pre_path.read_text())
        r = write_post(out_dir, pre)
        print(json.dumps({"count": r["count"], "unchanged": r["unchanged"],
                          "drift_row_count": len(r["drift_rows"])},
                         sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
