#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-28T22:00:00Z
# cycle: 23
# run_id: run-2026-08-28T040704Z
# agent: worker (clone-0, fork 3fbd8c1ab57c)
# milestone: M-GEN-1/batch-v5-n16
# ---
"""Apply the frozen 3-verdict rubric for M-GEN-1/batch-v5-n16.

Reads:
    data/gen/batch_v5_n16/collision_analysis.json
Writes:
    data/gen/batch_v5_n16/hypothesis_verdict.json

Rubric (locked BEFORE the run in the research brief):
  CONFIRMS_CONSTRUCTION   fraction >= 0.90
  PARTIAL_CONFIRM         0.60 <= fraction < 0.90
  CONFIRMS_H2_LARGER      fraction  < 0.60
  fraction = primary_attribution_tiebreak({form, arrangement}) / total_pairs

If total_pairs == 0, the rubric is technically inapplicable (nothing to
attribute); emit a zero-pair verdict record with an explanatory note.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Dict

os.environ.setdefault("PYTHONHASHSEED", "0")
assert sys.executable == "/usr/bin/python3", sys.executable

_REPO = Path(__file__).resolve().parent.parent.parent
V5_BATCH_ROOT = _REPO / "data" / "gen" / "batch_v5_n16"


def _classify(fraction: float) -> str:
    if fraction >= 0.90:
        return "CONFIRMS_CONSTRUCTION"
    if fraction >= 0.60:
        return "PARTIAL_CONFIRM"
    return "CONFIRMS_H2_LARGER"


def emit(batch_root: Path = V5_BATCH_ROOT) -> Dict:
    coll = json.loads((batch_root / "collision_analysis.json").read_text())
    total_pairs = int(coll["coerced"]["total_pairwise_collisions"])
    primary = coll["coerced"]["primary_histogram_tiebreak"]
    any_hist = coll["coerced"]["histogram_any_rt"]
    fraction = float(coll["coerced"]["form_arrangement_primary_fraction"])

    if total_pairs == 0:
        verdict_str = "NULL_RESULT_NO_COLLISIONS_AT_N16"
        note = ("Zero collision pairs observed at N=16. Consistent with the "
                "cycle-14 construction proof (a lower-bound argument, so a "
                "zero-count is not falsified) but not informative — the "
                "attribution rubric requires at least one pair to evaluate. "
                "Likely cause: the I4 stratified rejection sampler's "
                "`already_picked` exclusion set prevents within-rule_type "
                "collisions at N <= K. Recommend N=24 (or larger) follow-up "
                "where at least two rule_types have N > K.")
    else:
        verdict_str = _classify(fraction)
        note = ("Attribution from cycle-13 tiebreak methodology: first rule_type "
                "in declaration order that matches counts once per pair. "
                "any_rt histogram counts every (i,j,rt) hit; primary histogram "
                "uses tiebreak.")

    verdict = {
        "observed_pairs": total_pairs,
        "attribution": {
            rt: int(primary[rt]) for rt in
            ("harmonic", "rhythmic", "melodic", "form", "arrangement")
        },
        "attribution_any_rt": {
            rt: int(any_hist[rt]) for rt in
            ("harmonic", "rhythmic", "melodic", "form", "arrangement")
        },
        "form_arrangement_fraction": fraction,
        "verdict": verdict_str,
        "frozen_rubric": {
            "CONFIRMS_CONSTRUCTION": ">=0.90",
            "PARTIAL_CONFIRM": "[0.60, 0.90)",
            "CONFIRMS_H2_LARGER": "<0.60",
            "NULL_RESULT_NO_COLLISIONS_AT_N16": "total_pairs == 0",
        },
        "note": note,
        "K_distribution": {
            "harmonic": 20,
            "rhythmic": 15,
            "melodic": 15,
            "form": 15,
            "arrangement": 15,
        },
        "N": 16,
    }
    (batch_root / "hypothesis_verdict.json").write_text(
        json.dumps(verdict, indent=2, sort_keys=True))
    return verdict


def _main(argv):
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch-root", type=Path, default=V5_BATCH_ROOT)
    args = ap.parse_args(argv)
    v = emit(args.batch_root)
    print(f"[batch_v5_hypothesis_verdict] {v['verdict']}  "
          f"pairs={v['observed_pairs']}  "
          f"{{form,arr}} fraction={v['form_arrangement_fraction']:.4f}")
    print(f"  attribution primary: {v['attribution']}")
    print(f"  attribution any_rt:  {v['attribution_any_rt']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(sys.argv[1:]))
