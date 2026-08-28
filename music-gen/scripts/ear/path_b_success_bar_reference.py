#!/usr/bin/env python3
# created: 2026-08-28T11:40:00Z  cycle: 26  run_id: run-2026-08-28T040704Z
# agent: worker (clone-1 fork 8f3344880d29)  milestone: _manager/M-EAR-1-path-B-commit
"""Path B real-label success-bar reference implementation.

Armed-not-fired against real labels this cycle (rated audio still egress-
blocked). When egress opens and `data/ear/features/` is populated for all
80 rated songs, this script computes the three frozen success bars from
docs/ear_path_b_commitment.md §3 and writes `data/ear/path_b_evaluation.json`.

Zero PRNG (SHA-256 tiebreak for bootstrap resample selection). Zero live
network. Interpreter-guarded. No `sidecar_nonfactor` imports.

Usage:
    /usr/bin/python3 scripts/ear/path_b_success_bar_reference.py \\
        --sb {1,2,3,all} \\
        --ratings-manifest corpus/ratings/ratings_manifest.tsv \\
        --features-dir data/ear/features \\
        --out data/ear/path_b_evaluation.json
"""
from __future__ import annotations

import sys
assert sys.executable == "/usr/bin/python3", sys.executable

import argparse
import hashlib
import json
from pathlib import Path

# Frozen numeric constants from docs/ear_path_b_commitment.md §3.
IQR_MAE = 0.5909090909  # cycle-22 per_recipe_mae Q3 - Q1
SB1_MARGIN_THRESHOLD = IQR_MAE
SB2_TAU_PASS = 0.4
SB2_TAU_PARTIAL = 0.2
SB3_DETECTION = 0.90
SB3_FPR_MAX = 0.10
LEAK_ALPHA = 1.0


def sb1_check(corn_mae: float, ratings: list[int]) -> dict:
    """SB1: CORN MAE beats min(majority-class, mean-integer) baselines by
    margin > IQR_MAE."""
    from collections import Counter
    counter = Counter(ratings)
    maj_pred = counter.most_common(1)[0][0]
    maj_mae = sum(abs(l - maj_pred) for l in ratings) / len(ratings)
    mean_val = sum(ratings) / len(ratings)
    mean_int_pred = int(round(mean_val))
    mean_int_mae = sum(abs(l - mean_int_pred) for l in ratings) / len(ratings)
    baseline = min(maj_mae, mean_int_mae)
    margin = baseline - corn_mae
    if margin > SB1_MARGIN_THRESHOLD:
        verdict = "PASS"
    elif margin > 0:
        verdict = "PARTIAL"
    else:
        verdict = "FAIL"
    return {
        "sb": 1,
        "verdict": verdict,
        "corn_mae": corn_mae,
        "majority_class_mae": maj_mae,
        "majority_class_pred": maj_pred,
        "mean_integer_mae": mean_int_mae,
        "mean_integer_pred": mean_int_pred,
        "min_baseline_mae": baseline,
        "margin": margin,
        "iqr_threshold": SB1_MARGIN_THRESHOLD,
    }


def sha256_index_tiebreak(seed: str, n: int, k: int) -> list[int]:
    """Deterministic k-of-n selection via SHA-256 tiebreak (no PRNG).
    Rank the n indices by SHA-256 of f'{seed}:{i}'; take the top k."""
    ranks = sorted(range(n),
                   key=lambda i: hashlib.sha256(f"{seed}:{i}".encode()).digest())
    return sorted(ranks[:k])


def sb2_check(bootstrap_taus: list[float]) -> dict:
    """SB2: mean pairwise Kendall τ across bootstrap resamples ≥ 0.4."""
    if not bootstrap_taus:
        return {"sb": 2, "verdict": "FAIL", "reason": "no bootstrap samples"}
    mean_tau = sum(bootstrap_taus) / len(bootstrap_taus)
    if mean_tau >= SB2_TAU_PASS:
        verdict = "PASS"
    elif mean_tau >= SB2_TAU_PARTIAL:
        verdict = "PARTIAL"
    else:
        verdict = "FAIL"
    return {
        "sb": 2,
        "verdict": verdict,
        "n_bootstraps": len(bootstrap_taus),
        "mean_pairwise_tau": mean_tau,
        "pass_threshold": SB2_TAU_PASS,
        "partial_threshold": SB2_TAU_PARTIAL,
    }


def sb3_check(per_channel: dict) -> dict:
    """SB3: per-non-factor detection ≥ 0.90 at α=1.0 AND FPR ≤ 0.10.

    per_channel: {channel: {"detection": float | None, "fpr": float | None}}
        where channel ∈ {"artist", "genre", "era"}.
        A DEFERRED channel has both fields None."""
    channels = {}
    overall = "PASS"
    any_fail = False
    any_deferred = False
    any_underpowered = False
    for ch, m in per_channel.items():
        det = m.get("detection")
        fpr = m.get("fpr")
        if det is None or fpr is None:
            channels[ch] = {"verdict": "DEFERRED", **m}
            any_deferred = True
            continue
        if fpr > SB3_FPR_MAX:
            channels[ch] = {"verdict": "FAIL", **m}
            any_fail = True
        elif det < SB3_DETECTION:
            channels[ch] = {"verdict": "UNDER_POWERED", **m}
            any_underpowered = True
        else:
            channels[ch] = {"verdict": "PASS", **m}
    if any_fail:
        overall = "FAIL"
    elif any_deferred or any_underpowered:
        overall = "PARTIAL"
    return {
        "sb": 3,
        "overall_verdict": overall,
        "alpha": LEAK_ALPHA,
        "detection_threshold": SB3_DETECTION,
        "fpr_max": SB3_FPR_MAX,
        "channels": channels,
    }


def _cli(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--sb", choices=["1", "2", "3", "all"], default="all")
    ap.add_argument("--ratings-manifest", type=Path,
                    default=Path("corpus/ratings/ratings_manifest.tsv"))
    ap.add_argument("--features-dir", type=Path,
                    default=Path("data/ear/features"))
    ap.add_argument("--out", type=Path,
                    default=Path("data/ear/path_b_evaluation.json"))
    ap.add_argument("--power-calc", action="store_true",
                    help="Instead of evaluating, run the bootstrap-power "
                         "calculation for §5 corpus-expansion ticket.")
    args = ap.parse_args(argv)

    # This is the armed-not-fired reference implementation. Callers with
    # real trained-model + real predictions supply the numbers via a
    # helper (not implemented here — that surface lands with the actual
    # training-loop invocation cycle).
    print(json.dumps({
        "status": "armed_not_fired",
        "message": (
            "This is the Path B success-bar reference. Real-label evaluation "
            "requires post-egress rated audio + trained CORN checkpoint. "
            "See docs/ear_path_b_commitment.md §8 for the post-trigger "
            "checklist that invokes this script's compute functions "
            "(sb1_check, sb2_check, sb3_check) directly."
        ),
        "constants": {
            "IQR_MAE": IQR_MAE,
            "SB2_TAU_PASS": SB2_TAU_PASS,
            "SB2_TAU_PARTIAL": SB2_TAU_PARTIAL,
            "SB3_DETECTION": SB3_DETECTION,
            "SB3_FPR_MAX": SB3_FPR_MAX,
            "LEAK_ALPHA": LEAK_ALPHA,
        },
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(_cli(sys.argv[1:]))
