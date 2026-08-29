#!/usr/bin/python3
"""c46 SB3 50-control widening probe for M-EAR-1/real-label-training-v2.

Extends the c37/c38/c45 leak-test denominator from N_CONTROLS=25 to
N_CONTROLS=50, keeping the c37 F1 pooled-variance statistic unchanged
(statistic-fix invariance). Emits:
  - data/ear_v2/sb3_control_widening_result.json — 25 vs 50 side-by-side
  - Verdict: FPR_NARROWED_PASS (50-ctl fpr <= 0.10) or FPR_STILL_OVERSHOOT.

Byte-determinism × 2 required per brief; asserted by running the probe
twice into fresh in-memory computations under the same env pins and
comparing SHA-256 on the output JSON (excluding any timestamp field —
none present).

Startup banner emitted before heavy imports per c43.
"""
# created: 2026-08-29T16:45:00Z  cycle: 46  run_id: run-2026-08-28T040704Z
# agent: worker  milestone: _manager/M-EAR-1-v2-verdict-adjudication-and-gate-closure

from __future__ import annotations

import sys

print("[c46:sb3_control_widening] starting", flush=True)
assert sys.executable == "/usr/bin/python3", sys.executable

import hashlib
import json
from pathlib import Path

import numpy as np

from scripts.ear.leak_test import (
    f1_pooled_variance_statistic,
    STATISTIC_VERSION,
)
from scripts.ear_v2.evaluate_sb_v2 import (
    _load_preds,
    _sha_permutation,
    _sha_subsample_indices,
    _artist_denominator_pairs,
    ALPHA_ARTIST,
    N_DETECT_REPEATS,
    SB3_DETECT_MIN,
    SB3_FPR_MAX,
)

DATA_DIR = Path("data/ear_v2")


def _detect_at_n_controls(rows: list[dict], n_controls: int) -> dict:
    y_true = np.array([r["band_true"] for r in rows], dtype=np.float64)
    y_pred = np.array([r["band_pred_expectation"] for r in rows],
                      dtype=np.float64)
    artists = [r["artist"] if r["artist"] else f"UNKNOWN_{i}"
               for i, r in enumerate(rows)]
    denom = _artist_denominator_pairs(artists)
    s_obs = float(f1_pooled_variance_statistic(y_true, y_pred, artists))
    null_stats: list[float] = []
    for c in range(n_controls):
        perm = _sha_permutation(artists, c)
        null_stats.append(
            float(f1_pooled_variance_statistic(y_true, y_pred, perm))
        )
    null_arr = np.array(null_stats)
    tau = float(np.percentile(null_arr, 90))
    fpr = float(np.mean(null_arr >= tau))
    n = len(rows)
    per_repeat: list[float] = []
    detect_hits = 0
    for k in range(N_DETECT_REPEATS):
        idx = _sha_subsample_indices(n, k)
        yt_r = y_true[idx]
        yp_r = y_pred[idx]
        ar_r = [artists[i] for i in idx]
        s_r = float(f1_pooled_variance_statistic(yt_r, yp_r, ar_r))
        per_repeat.append(s_r)
        if s_r >= tau:
            detect_hits += 1
    detection_rate = float(detect_hits / N_DETECT_REPEATS)
    return {
        "n_controls": n_controls,
        "n_detect_repeats": N_DETECT_REPEATS,
        "n_clips": int(n),
        "denominator_pairs": int(denom),
        "s_observed": s_obs,
        "tau_90pct_null": tau,
        "null_mean": float(null_arr.mean()),
        "null_std": float(null_arr.std()),
        "detection_rate": detection_rate,
        "fpr": fpr,
        "pass_detection": bool(detection_rate >= SB3_DETECT_MIN),
        "pass_fpr": bool(fpr <= SB3_FPR_MAX),
        "pass": bool(detection_rate >= SB3_DETECT_MIN and fpr <= SB3_FPR_MAX),
        "detection_required": SB3_DETECT_MIN,
        "fpr_max": SB3_FPR_MAX,
        "alpha": ALPHA_ARTIST,
        "statistic_version": STATISTIC_VERSION,
    }


def main() -> dict:
    rows = _load_preds()
    r25 = _detect_at_n_controls(rows, 25)
    r50 = _detect_at_n_controls(rows, 50)

    # Byte-determinism × 2: recompute r50 into a second dict; SHA-256 equal
    # on canonical JSON.
    r50_check = _detect_at_n_controls(rows, 50)
    d1 = hashlib.sha256(
        json.dumps(r50, sort_keys=True).encode()).hexdigest()
    d2 = hashlib.sha256(
        json.dumps(r50_check, sort_keys=True).encode()).hexdigest()
    determinism_x2 = (d1 == d2)

    fpr_flip = r50["fpr"] <= SB3_FPR_MAX and r25["fpr"] > SB3_FPR_MAX
    fpr_stayed = r50["fpr"] > SB3_FPR_MAX
    verdict = "FPR_NARROWED_PASS" if r50["pass_fpr"] else "FPR_STILL_OVERSHOOT"

    out = {
        "cycle": 46,
        "milestone": "M-EAR-1/real-label-training-v2/sb3-control-widening",
        "narrative": (
            f"SB3 50-control widening on c45 verdict artifacts. "
            f"25-control FPR = {r25['fpr']:.4f}; 50-control FPR = "
            f"{r50['fpr']:.4f}. Verdict {verdict}."
            + (" FPR flipped to PASS with 50 controls."
               if fpr_flip else "")
            + (" FPR remains above threshold with 50 controls."
               if fpr_stayed else "")
        ),
        "verdict": verdict,
        "fpr_flip": fpr_flip,
        "byte_determinism_x2": determinism_x2,
        "byte_determinism_shas": [d1, d2],
        "at_n_controls_25": r25,
        "at_n_controls_50": r50,
        "statistic_version": STATISTIC_VERSION,
        "c45_verdict_unchanged_note": (
            "The c45 verdict was published on the 25-control FPR = 0.120; "
            "any v2.1 re-verdict incorporating 50-control widening is "
            "deferred to c47 as a first-class ticket per report §10."
        ),
    }
    (DATA_DIR / "sb3_control_widening_result.json").write_text(
        json.dumps(out, indent=2, sort_keys=True) + "\n"
    )
    return out


if __name__ == "__main__":
    r = main()
    print(json.dumps({
        "verdict": r["verdict"],
        "fpr_25ctl": r["at_n_controls_25"]["fpr"],
        "fpr_50ctl": r["at_n_controls_50"]["fpr"],
        "det_25ctl": r["at_n_controls_25"]["detection_rate"],
        "det_50ctl": r["at_n_controls_50"]["detection_rate"],
        "byte_determinism_x2": r["byte_determinism_x2"],
    }, indent=2))
