#!/usr/bin/python3
"""v2.1 SB3 50-control re-verdict — re-runs the c46 SB3 widening probe.

Reads c45 v2 held_out_predictions.tsv READ-ONLY. Runs the c46
`_detect_at_n_controls` logic at n_controls=50 with the c37 F1
pooled-variance statistic unchanged.

Byte-determinism × 2 mandate: this script is called TWICE by the v2.1
orchestrator into two fresh `tempfile.mkdtemp()` CWDs. Each invocation
writes `sb3_50ctl_verdict_v2p1.json` and `run_manifest.json` to the
directory named by `--out`. The orchestrator SHA-256-compares the two
verdict JSONs.

Env pins per v2.1 rubric §Determinism envelope; the F1 pooled-variance
statistic + SHA-derived null permutations are deterministic given the
same input rows.
"""
# created: 2026-08-29T17:07:00Z  cycle: 47  run_id: run-2026-08-28T040704Z
# agent: worker  milestone: M-EAR-1/real-label-training-v2.1
from __future__ import annotations

import sys

print("[c47:sb3_50ctl_reverdict] starting", flush=True)
assert sys.executable == "/usr/bin/python3", sys.executable

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("PYTHONHASHSEED", "0")
os.environ.setdefault("SOURCE_DATE_EPOCH", "1756463424")
os.environ.setdefault("TZ", "UTC")
os.environ.setdefault("LC_ALL", "C.UTF-8")

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

# READ-ONLY imports of c37/c38 statistic + c46 SB3 widening helpers.
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

N_CONTROLS_V2P1 = 50


def sb3_50ctl(rows: list[dict]) -> dict:
    y_true = np.array([r["band_true"] for r in rows], dtype=np.float64)
    y_pred = np.array([r["band_pred_expectation"] for r in rows],
                      dtype=np.float64)
    artists = [r["artist"] if r["artist"] else f"UNKNOWN_{i}"
               for i, r in enumerate(rows)]
    denom = _artist_denominator_pairs(artists)
    s_obs = float(f1_pooled_variance_statistic(y_true, y_pred, artists))
    null_stats: list[float] = []
    for c in range(N_CONTROLS_V2P1):
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
        "n_controls": N_CONTROLS_V2P1,
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
        "pass": bool(detection_rate >= SB3_DETECT_MIN
                     and fpr <= SB3_FPR_MAX),
        "detection_required": SB3_DETECT_MIN,
        "fpr_max": SB3_FPR_MAX,
        "alpha": ALPHA_ARTIST,
        "statistic_version": STATISTIC_VERSION,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True,
                    help="Output directory (fresh tempfile.mkdtemp()).")
    ap.add_argument("--run-id", type=int, required=True,
                    help="Run identifier (1 or 2), for run_manifest.json.")
    args = ap.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    rows = _load_preds()
    r = sb3_50ctl(rows)
    verdict = {
        "cycle": 47,
        "milestone": "M-EAR-1/real-label-training-v2.1",
        "narrative": (
            f"SB3 50-control re-verdict for v2.1. Detection = "
            f"{r['detection_rate']:.4f}; FPR = {r['fpr']:.4f}. "
            f"Under c26 thresholds: detection PASS iff >= 0.90; "
            f"FPR PASS iff <= 0.10."
        ),
        "at_n_controls_50": r,
        "statistic_version": STATISTIC_VERSION,
        "c46_methodology_chain": [
            "c37_f1_pooled_variance",
            "c38_leak_lift",
            "c46_widening_25_to_50",
        ],
        "c45_verdict_reference": "EAR_v2_PARTIAL_unchanged",
    }
    verdict_path = out_dir / "sb3_50ctl_verdict_v2p1.json"
    verdict_path.write_text(
        json.dumps(verdict, indent=2, sort_keys=True) + "\n"
    )

    manifest = {
        "run_id": int(args.run_id),
        "cwd": os.getcwd(),
        "out_dir": str(out_dir),
        "n_rows_input": len(rows),
        "sb3_50ctl_verdict_v2p1_sha256": hashlib.sha256(
            verdict_path.read_bytes()
        ).hexdigest(),
        "env_pins": {k: os.environ.get(k) for k in [
            "OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS",
            "PYTHONHASHSEED", "SOURCE_DATE_EPOCH", "TZ", "LC_ALL",
        ]},
        "statistic_version": STATISTIC_VERSION,
    }
    (out_dir / "run_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    )
    print(json.dumps({
        "verdict_sha256": manifest["sb3_50ctl_verdict_v2p1_sha256"],
        "detection_rate": r["detection_rate"],
        "fpr": r["fpr"],
        "pass_detection": r["pass_detection"],
        "pass_fpr": r["pass_fpr"],
    }, indent=2))


if __name__ == "__main__":
    main()
