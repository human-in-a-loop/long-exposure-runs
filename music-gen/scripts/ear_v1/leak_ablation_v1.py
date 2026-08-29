#!/usr/bin/python3
"""Non-factor leak ablation using the c37 F1 pooled-variance statistic.

Non-factor coverage:
  - artist: LIVE channel. F1 pooled-variance over parsed-artist grouping
            of (band_true, band_pred_expectation) residuals. Detection
            rate is measured as (# repeats with S_obs >= tau) / (# repeats)
            over K=20 SHA-256-derived subsample repeats. Tau is computed
            from N_CONTROLS=25 permutation nulls.
  - genre:  deferred_aliased_with_band (playlist_id perfectly aliases with
            band on this corpus). Reported as a first-class field (not a
            comment). Detection recorded as `null_deferred` with a numeric
            observed-statistic of NaN; FPR recorded as 0.0 (no controls).
  - era:    deferred_no_metadata. Same treatment.

Emits data/ear_v1/leak_test_summary.json with:
  - statistic_version = "F1_pooled_variance_v1"
  - genre = "deferred_aliased_with_band"  (field, not a comment)
  - era   = "deferred_no_metadata"        (field, not a comment)
  - per-leak-type F1 detection rate + FPR
"""
# created: 2026-08-29T11:07:00Z  cycle: 38  run_id: run-2026-08-28T040704Z
# agent: worker (clone-0)  milestone: M-EAR-1/real-label-training-v1
from __future__ import annotations

import sys
assert sys.executable == "/usr/bin/python3", sys.executable

import hashlib
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

from scripts.ear.leak_test import (
    f1_pooled_variance_statistic,
    STATISTIC_VERSION,
)

DATA_DIR = Path("data/ear_v1")
N_CONTROLS = 25  # >= 20 permutation nulls per leak type
N_DETECT_REPEATS = 20  # subsample-with-replacement repeats for detection rate
ALPHA_ARTIST = 1.0  # natural artist labels are the alpha=1.0 injection


def _load_preds() -> list[dict]:
    rows: list[dict] = []
    with open(DATA_DIR / "held_out_predictions.tsv") as f:
        header = f.readline().rstrip("\n").split("\t")
        for line in f:
            cols = line.rstrip("\n").split("\t")
            r = dict(zip(header, cols))
            r["band_true"] = int(r["band_true"])
            r["band_pred_int"] = int(r["band_pred_int"])
            r["band_pred_expectation"] = float(r["band_pred_expectation"])
            rows.append(r)
    return rows


def _sha_rank(payload: str) -> int:
    return int.from_bytes(
        hashlib.sha256(payload.encode()).digest()[:8], "big"
    )


def _sha_permutation(labels: list[str], seed_id: int) -> list[str]:
    keys = sorted(
        (_sha_rank(f"perm_{seed_id}_{i}"), i) for i in range(len(labels))
    )
    return [labels[k[1]] for k in keys]


def _sha_subsample_indices(n: int, seed_id: int) -> np.ndarray:
    """Deterministic SHA-256-derived with-replacement sample of size n."""
    return np.array([
        _sha_rank(f"subsample_{seed_id}_{i}") % n for i in range(n)
    ])


def _f1_for_predictions(y_true: np.ndarray, y_pred: np.ndarray,
                        labels: list) -> float:
    return float(f1_pooled_variance_statistic(y_true, y_pred, labels))


def leak_detect_artist(rows: list[dict]) -> dict:
    """F1 pooled-variance detection of artist non-factor leak.

    Detection statistic: S_F1 on (band_true, band_pred_expectation,
    parsed_artist). Tau = 90th percentile of N_CONTROLS=25 SHA-permutation
    nulls. Detection rate = fraction of N_DETECT_REPEATS SHA-subsample
    resamples where S_obs >= tau. FPR = fraction of the N_CONTROLS
    permutation nulls that fall >= tau.
    """
    y_true = np.array([r["band_true"] for r in rows], dtype=np.float64)
    y_pred = np.array([r["band_pred_expectation"] for r in rows],
                      dtype=np.float64)
    artists = [r["artist"] if r["artist"] else f"UNKNOWN_{i}"
               for i, r in enumerate(rows)]
    n = len(rows)

    s_obs = _f1_for_predictions(y_true, y_pred, artists)

    # N_CONTROLS SHA-permutation nulls.
    null_stats: list[float] = []
    for c in range(N_CONTROLS):
        perm = _sha_permutation(artists, c)
        null_stats.append(_f1_for_predictions(y_true, y_pred, perm))
    null_arr = np.array(null_stats)
    tau = float(np.percentile(null_arr, 90))
    fpr = float(np.mean(null_arr >= tau))

    # Detection rate: subsample-with-replacement + measure per-subsample.
    detect_hits = 0
    per_repeat: list[float] = []
    for k in range(N_DETECT_REPEATS):
        idx = _sha_subsample_indices(n, k)
        yt_r = y_true[idx]
        yp_r = y_pred[idx]
        ar_r = [artists[i] for i in idx]
        s_r = _f1_for_predictions(yt_r, yp_r, ar_r)
        per_repeat.append(s_r)
        if s_r >= tau:
            detect_hits += 1
    detection_rate = float(detect_hits / N_DETECT_REPEATS)

    return {
        "s_observed": float(s_obs),
        "tau_90pct_null": tau,
        "null_mean": float(null_arr.mean()),
        "null_std": float(null_arr.std()),
        "n_controls": N_CONTROLS,
        "n_detect_repeats": N_DETECT_REPEATS,
        "detection_rate": detection_rate,
        "fpr": fpr,
        "alpha": ALPHA_ARTIST,
        "statistic_version": STATISTIC_VERSION,
        "per_repeat_S": per_repeat,
    }


def summarize() -> dict:
    rows = _load_preds()
    artist = leak_detect_artist(rows)

    # Playlist-id alias check.
    band_playlists: dict[int, set] = defaultdict(set)
    for r in rows:
        band_playlists[r["band_true"]].add(r["playlist_id"])
    alias_confirmed = all(len(v) <= 1 for v in band_playlists.values())

    summary = {
        "statistic_version": STATISTIC_VERSION,
        "genre": "deferred_aliased_with_band",
        "era": "deferred_no_metadata",
        "leak_types": {
            "artist": {
                "status": "live",
                "detection_rate": artist["detection_rate"],
                "fpr": artist["fpr"],
                "s_observed": artist["s_observed"],
                "tau_90pct_null": artist["tau_90pct_null"],
                "alpha": ALPHA_ARTIST,
                "statistic_version": STATISTIC_VERSION,
                "n_controls": artist["n_controls"],
                "n_detect_repeats": artist["n_detect_repeats"],
                "artist_parse_failures": sum(
                    1 for r in rows if not r["artist"]
                ),
            },
            "genre": {
                "status": "deferred_aliased_with_band",
                "detection_rate": None,
                "fpr": None,
                "reason": (
                    "playlist_id perfectly aliases with rating band on "
                    "this 43-song corpus; genre unseparable from signal "
                    "by construction."
                ),
                "alias_confirmed": bool(alias_confirmed),
                "statistic_version": STATISTIC_VERSION,
            },
            "era": {
                "status": "deferred_no_metadata",
                "detection_rate": None,
                "fpr": None,
                "reason": (
                    "Release-year metadata not present in "
                    "corpus/ratings/*/RECEIPTS.md or ratings_manifest.tsv. "
                    "Deferred to post-yt-dlp-metadata cycle."
                ),
                "statistic_version": STATISTIC_VERSION,
            },
        },
        "artist_full_detail": artist,
    }

    (DATA_DIR / "leak_test_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True)
    )
    return summary


if __name__ == "__main__":
    print(json.dumps(summarize(), indent=2, sort_keys=True))
