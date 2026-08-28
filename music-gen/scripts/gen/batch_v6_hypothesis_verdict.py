#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-28T23:30:00Z
# cycle: 25
# run_id: run-2026-08-28T040704Z
# agent: worker (clone-0, fork dc8cba4b79eb)
# milestone: M-GEN-1/batch-v6-unconditioned-n16
# ---
"""Apply the frozen 5-verdict rubric for M-GEN-1/batch-v6-unconditioned-n16.

Rubric (locked BEFORE the run in the research brief):
  CONFIRMS_PIGEONHOLE            {form, arrangement} fraction >= 0.90
  PARTIAL_CONFIRM                0.60 <= {form, arrangement} < 0.90
  PARTIAL_CONFIRM_K15_FAMILY     {form, arrangement} < 0.60 AND
                                 {form, arrangement, rhythmic, melodic} >= 0.90
  REFUTES_PIGEONHOLE             K=15 union < 0.90 (>=10% of pairs are harmonic;
                                 K=20 >= N=16 which the pigeonhole forbids)
  NULL_RESULT                    0 collision pairs at N=16 — informative-not-informative

Reads:
    data/gen/batch_v6/collision_analysis.json
Writes:
    data/gen/batch_v6/hypothesis_verdict.json
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
V6_BATCH_ROOT = _REPO / "data" / "gen" / "batch_v6"


def _classify(fraction_form_arr: float, fraction_k15_union: float, total_pairs: int) -> str:
    if total_pairs == 0:
        return "NULL_RESULT"
    if fraction_form_arr >= 0.90:
        return "CONFIRMS_PIGEONHOLE"
    if fraction_form_arr >= 0.60:
        return "PARTIAL_CONFIRM"
    if fraction_k15_union >= 0.90:
        return "PARTIAL_CONFIRM_K15_FAMILY"
    return "REFUTES_PIGEONHOLE"


def emit(batch_root: Path = V6_BATCH_ROOT) -> Dict:
    coll = json.loads((batch_root / "collision_analysis.json").read_text())
    total_pairs = int(coll["coerced"]["total_pairwise_collisions"])
    primary = coll["coerced"]["primary_histogram_tiebreak"]
    any_hist = coll["coerced"]["histogram_any_rt"]
    frac_fa = float(coll["coerced"]["form_arrangement_primary_fraction"])
    frac_k15 = float(coll["coerced"]["k15_union_primary_fraction"])

    verdict_str = _classify(frac_fa, frac_k15, total_pairs)

    interp = {
        "CONFIRMS_PIGEONHOLE": (
            "Cycle-14's specific structural prediction upheld — {form, arrangement} "
            "are the dominant collision contributors at N > K."),
        "PARTIAL_CONFIRM": (
            "Prediction directionally correct; leakage into other rule_types warrants "
            "attribution in §8."),
        "PARTIAL_CONFIRM_K15_FAMILY": (
            "Cycle-14 named the wrong specific rule_types within the K=15 family, but "
            "the underlying pigeonhole model is correct."),
        "REFUTES_PIGEONHOLE": (
            "First-class positive finding — pigeonhole model does not explain observed "
            "collision distribution; at least 10% of pairs are attributed to harmonic "
            "(K=20 >= N=16), which the model forbids."),
        "NULL_RESULT": (
            "Zero collision pairs at N=16. Compatible with the construction proof "
            "(a lower-bound argument, so zero-count is not falsified) but not "
            "informative for attribution. Recommend N=24 follow-up."),
    }[verdict_str]

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
        "form_arrangement_fraction": frac_fa,
        "k15_union_fraction": frac_k15,
        "verdict": verdict_str,
        "interpretation": interp,
        "frozen_rubric": {
            "CONFIRMS_PIGEONHOLE": "{form, arrangement} >= 0.90",
            "PARTIAL_CONFIRM": "0.60 <= {form, arrangement} < 0.90",
            "PARTIAL_CONFIRM_K15_FAMILY": (
                "{form, arrangement} < 0.60 AND "
                "{form, arrangement, rhythmic, melodic} >= 0.90"),
            "REFUTES_PIGEONHOLE": "{form, arrangement, rhythmic, melodic} < 0.90",
            "NULL_RESULT": "total_pairs == 0",
        },
        "K_distribution": {
            "harmonic": 20,
            "rhythmic": 18,
            "melodic": 18,
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
    ap.add_argument("--batch-root", type=Path, default=V6_BATCH_ROOT)
    args = ap.parse_args(argv)
    v = emit(args.batch_root)
    print(f"[batch_v6_hypothesis_verdict] {v['verdict']}  "
          f"pairs={v['observed_pairs']}  "
          f"{{form,arr}} fraction={v['form_arrangement_fraction']:.4f}  "
          f"{{K=15 union}} fraction={v['k15_union_fraction']:.4f}")
    print(f"  attribution primary: {v['attribution']}")
    print(f"  attribution any_rt:  {v['attribution_any_rt']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(sys.argv[1:]))
