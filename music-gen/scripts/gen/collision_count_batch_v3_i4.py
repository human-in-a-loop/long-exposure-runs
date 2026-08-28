#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-28T16:10:00Z
# cycle: 15
# run_id: run-2026-08-28T040704Z
# agent: worker (clone-1, fork 392503ab7d47)
# milestone: M-GEN-1/batch-v3-i4
# ---
"""Collision counter for batch-v3-i4.

Thin wrapper over ``scripts.gen.collision_analysis.analyze`` — reuses the
cycle-13 methodology byte-for-byte (do NOT reimplement counting) — pointed at
``data/gen/batch_v3_i4/``. Writes ``collision_report.json`` with the raw and
coerced pair lists + total counts, plus the frozen verdict rubric
    PASS if <= 3 pairs, PARTIAL if 4..7, FAIL if >= 8
applied to the coerced total (per cycle-13 batch-v2 methodology, which
reported 11 pairs on the coerced projection).
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

os.environ.setdefault("PYTHONHASHSEED", "0")
assert sys.executable == "/usr/bin/python3", sys.executable

_REPO = Path(__file__).resolve().parent.parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from scripts.gen.collision_analysis import analyze, write_tsv  # noqa: E402


PREDICTED_PAIRS = 0  # I4 predicted floor at N=8 (from intervention_proposal.json)


def _verdict(count: int) -> str:
    if count <= 3:
        return "PASS"
    if count <= 7:
        return "PARTIAL"
    return "FAIL"


def _main(argv):
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch-root", type=Path,
                    default=_REPO / "data" / "gen" / "batch_v3_i4")
    args = ap.parse_args(argv)

    result = analyze(args.batch_root)
    coerced_total = result["coerced"]["total_pairwise_collisions"]
    raw_total = result["raw"]["total_pairwise_collisions"]

    report = {
        "milestone": "M-GEN-1/batch-v3-i4",
        "sampler": "i4_stratified_rejection_sha256",
        "predicted_pairs_at_N8": PREDICTED_PAIRS,
        "observed_pairs_raw": raw_total,
        "observed_pairs_coerced": coerced_total,
        "verdict_rubric": {
            "PASS": "<= 3 pairs",
            "PARTIAL": "4..7 pairs",
            "FAIL": ">= 8 pairs",
        },
        "verdict_on_coerced": _verdict(coerced_total),
        "verdict_on_raw": _verdict(raw_total),
        "cycle_13_batch_v2_baseline_coerced": 11,
        "delta_vs_batch_v2": coerced_total - 11,
        "collision_analysis": result,
    }

    args.batch_root.mkdir(parents=True, exist_ok=True)
    (args.batch_root / "collision_report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True))
    # Also drop the standard collision_matrix.tsv for parity with batch_v2.
    write_tsv(result, args.batch_root / "collision_matrix.tsv")

    print(f"[collision_count_batch_v3_i4] raw pairs:     {raw_total}")
    print(f"[collision_count_batch_v3_i4] coerced pairs: {coerced_total}")
    print(f"[collision_count_batch_v3_i4] verdict (coerced): {_verdict(coerced_total)}")
    print(f"[collision_count_batch_v3_i4] batch-v2 baseline was 11 -> delta = {coerced_total - 11}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(sys.argv[1:]))
