#!/usr/bin/env python3
"""Run the full c37 clone-1 EAR SB3 fallback-statistic evaluation.

Steps:
1. Snapshot anchor SHAs (before).
2. Verify rubric_hash.txt matches current docs/ear_sb3_fallback_statistic_rubric.md.
3. Run scripts/ear_sb3_fallback/evaluate_candidates.py end-to-end.
4. Snapshot anchor SHAs (after) and write anchor_preservation.json.
5. Print verdict.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import sys

if sys.executable != "/usr/bin/python3":
    raise RuntimeError(
        f"Interpreter guard: expected /usr/bin/python3, got {sys.executable}"
    )

_HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent.parent))

DATA_DIR = pathlib.Path("data/ear_sb3_fallback")
ANCHORS = [
    "data/ear/leak_test_summary.json",
    "scripts/ear/leak_test.py",
    "scripts/ear/synthetic_labels.py",
    "scripts/ear/stability_audit.py",
    "docs/ear_path_b_commitment.md",
]


def _sha_file(p: pathlib.Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def snapshot_anchors() -> dict:
    out = {}
    for rel in ANCHORS:
        p = pathlib.Path(rel)
        if p.exists():
            out[rel] = _sha_file(p)
        else:
            out[rel] = None
    return out


def verify_rubric_hash() -> None:
    rubric = pathlib.Path("docs/ear_sb3_fallback_statistic_rubric.md")
    current = hashlib.sha256(rubric.read_bytes()).hexdigest()
    stored = (DATA_DIR / "rubric_hash.txt").read_text().strip()
    if current != stored:
        raise RuntimeError(
            f"rubric_hash drift! stored={stored} current={current} "
            "(rubric doc was edited after freeze)"
        )


def main() -> int:
    before = snapshot_anchors()
    verify_rubric_hash()

    from scripts.ear_sb3_fallback.evaluate_candidates import (
        evaluate_all, apply_rubric, write_comparison_matrix,
    )

    results = evaluate_all()
    verdict = apply_rubric(results)
    write_comparison_matrix(results, verdict)
    (DATA_DIR / "verdict.json").write_text(json.dumps(verdict, indent=2, sort_keys=True))

    after = snapshot_anchors()

    preservation = {
        "anchors_checked": ANCHORS,
        "before_sha256": before,
        "after_sha256": after,
        "all_unchanged": before == after,
    }
    (DATA_DIR / "anchor_preservation.json").write_text(
        json.dumps(preservation, indent=2, sort_keys=True)
    )
    if not preservation["all_unchanged"]:
        raise RuntimeError("Anchor drift detected — refusing to proceed.")

    print("Verdict:", verdict["verdict"])
    print("Chosen candidate:", verdict["chosen_candidate"])
    print("Rubric hash:", verdict["rubric_hash"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
