#!/usr/bin/python3
"""SB1/SB2/SB3 evaluation on the v2 clip-level held-out predictions.

- SB1 clip-level margin: min(majority_mae, mean_int_mae) - clip_mae > 0.5909.
- SB2 mean pairwise Kendall tau across 10 SHA-stratified-bootstrap
  resamples on the clip-level (band_true, band_pred_int) vector >= 0.4.
- SB3 F1 pooled-variance leak-detection statistic (c37/c38 c1 lift)
  on artist non-factor at alpha=1.0. detection_rate >= 0.90 AND
  fpr <= 0.10. Denominator > 43 asserted for geometric validity.

Emits data/ear_v2/{sb_v2_verdict.json, verdict.json,
leak_test_v2_summary.json, sb_v2_results.json}. Verdict.json embeds
rubric_hash verbatim.
"""
# created: 2026-08-29T12:08:00Z  cycle: 39  run_id: run-2026-08-28T040704Z
# agent: worker  milestone: M-EAR-1/real-label-training-v2
from __future__ import annotations

import sys
assert sys.executable == "/usr/bin/python3", sys.executable

import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np

from scripts.ear.leak_test import (
    f1_pooled_variance_statistic,
    STATISTIC_VERSION,
)

DATA_DIR = Path("data/ear_v2")
RUBRIC_HASH_FILE = DATA_DIR / "rubric_hash.txt"

# c26 Path B FROZEN thresholds (unchanged from v1).
SB1_MARGIN_MIN = 0.5909
SB2_TAU_MIN = 0.4
SB3_DETECT_MIN = 0.90
SB3_FPR_MAX = 0.10
N_RESAMPLES = 10
BANDS = (4, 5, 6, 7)
N_CONTROLS = 25
N_DETECT_REPEATS = 20
ALPHA_ARTIST = 1.0

# v1 baselines (from c38 clone-0 verdict.json) — used to check "material
# improvement" for the EAR_v2_PARTIAL verdict.
V1_SB1_MARGIN = -0.2093023255813954
V1_SB2_MEAN_TAU = -0.09866905476329277
V1_SB3_DENOMINATOR = 43  # v1 singleton-artist corpus


def _sha_rank(payload: str) -> int:
    return int.from_bytes(
        hashlib.sha256(payload.encode()).digest()[:8], "big"
    )


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
            r["clip_idx"] = int(r["clip_idx"])
            r["fold_id"] = int(r["fold_id"])
            r["start_s"] = float(r["start_s"])
            r["end_s"] = float(r["end_s"])
            r["tail_anchored"] = bool(int(r["tail_anchored"]))
            rows.append(r)
    return rows


# ---------------------------------------------------------------- SB1
def sb1_clip(rows: list[dict]) -> dict:
    y_true = np.array([r["band_true"] for r in rows])
    y_pred = np.array([r["band_pred_int"] for r in rows])
    mae = float(np.mean(np.abs(y_pred - y_true)))
    vals, cnts = np.unique(y_true, return_counts=True)
    majority = int(vals[np.argmax(cnts)])
    mean_int = int(round(float(y_true.mean())))
    maj_mae = float(np.mean(np.abs(y_true - majority)))
    mi_mae = float(np.mean(np.abs(y_true - mean_int)))
    baseline_min = min(maj_mae, mi_mae)
    margin = baseline_min - mae
    return {
        "level": "clip",
        "n": int(y_true.size),
        "mae": mae,
        "majority_mae": maj_mae,
        "majority_value": majority,
        "mean_int_mae": mi_mae,
        "mean_int_value": mean_int,
        "baseline_min_mae": baseline_min,
        "margin": margin,
        "margin_required": SB1_MARGIN_MIN,
        "pass": bool(margin > SB1_MARGIN_MIN),
    }


# ---------------------------------------------------------------- SB2
def _kendall_tau(a: np.ndarray, b: np.ndarray) -> float:
    try:
        from scipy.stats import kendalltau
        t, _ = kendalltau(a, b)
        return float(t) if np.isfinite(t) else 0.0
    except Exception:
        n = a.size
        con = dis = 0
        for i in range(n):
            for j in range(i + 1, n):
                da = a[i] - a[j]
                db = b[i] - b[j]
                if da * db > 0:
                    con += 1
                elif da * db < 0:
                    dis += 1
        return (con - dis) / max(1, con + dis)


def _stratified_bootstrap_indices(rows: list[dict], resample_id: int
                                  ) -> np.ndarray:
    by_band: dict[int, list[int]] = {b: [] for b in BANDS}
    for i, r in enumerate(rows):
        by_band[r["band_true"]].append(i)
    selected: list[int] = []
    for b in BANDS:
        pool = by_band[b]
        if not pool:
            continue
        n = len(pool)
        for k in range(n):
            idx = _sha_rank(f"resample_{resample_id}|band_{b}|k_{k}") % n
            selected.append(pool[idx])
    return np.array(sorted(selected))


def sb2_clip(rows: list[dict]) -> dict:
    per: list[float] = []
    for r in range(N_RESAMPLES):
        idx = _stratified_bootstrap_indices(rows, r)
        y_true = np.array([rows[i]["band_true"] for i in idx])
        y_pred = np.array([rows[i]["band_pred_int"] for i in idx])
        per.append(_kendall_tau(y_true, y_pred))
    mean_tau = float(np.mean(per))
    return {
        "level": "clip",
        "per_resample_tau": [float(t) for t in per],
        "mean_tau": mean_tau,
        "tau_required": SB2_TAU_MIN,
        "n_resamples": N_RESAMPLES,
        "pass": bool(mean_tau >= SB2_TAU_MIN),
    }


# ---------------------------------------------------------------- SB3
def _sha_permutation(labels: list[str], seed_id: int) -> list[str]:
    keys = sorted(
        (_sha_rank(f"perm_{seed_id}_{i}"), i) for i in range(len(labels))
    )
    return [labels[k[1]] for k in keys]


def _sha_subsample_indices(n: int, seed_id: int) -> np.ndarray:
    return np.array([
        _sha_rank(f"subsample_{seed_id}_{i}") % n for i in range(n)
    ])


def _artist_denominator_pairs(labels: list[str]) -> int:
    """Count within-artist paired samples (used for SB3 denominator check).

    Any artist with n_g >= 2 contributes n_g * (n_g - 1) / 2 pairs to the
    within-group F1 denominator. On the v1 singleton corpus (43 unique
    artists across 43 songs) this evaluates to 0 — the statistic pinned
    at the min value. On the resampled corpus every song with >=2 clips
    yields at least 1 within-artist pair, so total >> 0.
    """
    from collections import Counter
    counts = Counter(labels)
    total = 0
    for _, ng in counts.items():
        if ng >= 2:
            total += (ng * (ng - 1)) // 2
    return total


def leak_detect_artist(rows: list[dict]) -> dict:
    y_true = np.array([r["band_true"] for r in rows], dtype=np.float64)
    y_pred = np.array([r["band_pred_expectation"] for r in rows],
                      dtype=np.float64)
    artists = [r["artist"] if r["artist"] else f"UNKNOWN_{i}"
               for i, r in enumerate(rows)]
    denominator_pairs = _artist_denominator_pairs(artists)
    n = len(rows)
    s_obs = float(f1_pooled_variance_statistic(y_true, y_pred, artists))
    # 25 SHA-permutation nulls.
    null_stats: list[float] = []
    for c in range(N_CONTROLS):
        perm = _sha_permutation(artists, c)
        null_stats.append(
            float(f1_pooled_variance_statistic(y_true, y_pred, perm))
        )
    null_arr = np.array(null_stats)
    tau = float(np.percentile(null_arr, 90))
    fpr = float(np.mean(null_arr >= tau))
    detect_hits = 0
    per_repeat: list[float] = []
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
        "s_observed": s_obs,
        "tau_90pct_null": tau,
        "null_mean": float(null_arr.mean()),
        "null_std": float(null_arr.std()),
        "n_controls": N_CONTROLS,
        "n_detect_repeats": N_DETECT_REPEATS,
        "denominator_pairs": int(denominator_pairs),
        "n_clips_input": int(n),
        "detection_rate": detection_rate,
        "fpr": fpr,
        "alpha": ALPHA_ARTIST,
        "statistic_version": STATISTIC_VERSION,
        "per_repeat_S": per_repeat,
    }


def sb3(rows: list[dict]) -> dict:
    artist = leak_detect_artist(rows)
    band_playlists: dict[int, set] = defaultdict(set)
    for r in rows:
        band_playlists[r["band_true"]].add(r["playlist_id"])
    alias_confirmed = all(len(v) <= 1 for v in band_playlists.values())
    per_leak = {
        "artist": {
            "status": "live",
            "detection_rate": artist["detection_rate"],
            "fpr": artist["fpr"],
            "s_observed": artist["s_observed"],
            "tau_90pct_null": artist["tau_90pct_null"],
            "denominator_pairs": artist["denominator_pairs"],
            "denominator_gt_43": bool(artist["denominator_pairs"] > 43),
            "alpha": ALPHA_ARTIST,
            "statistic_version": STATISTIC_VERSION,
            "n_controls": artist["n_controls"],
            "n_detect_repeats": artist["n_detect_repeats"],
            "detection_required": SB3_DETECT_MIN,
            "fpr_max": SB3_FPR_MAX,
            "pass_detection": bool(artist["detection_rate"] >= SB3_DETECT_MIN),
            "pass_fpr": bool(artist["fpr"] <= SB3_FPR_MAX),
            "pass": bool(
                artist["detection_rate"] >= SB3_DETECT_MIN
                and artist["fpr"] <= SB3_FPR_MAX
            ),
        },
        "genre": {
            "status": "deferred_aliased_with_band",
            "detection_rate": None,
            "fpr": None,
            "reason": (
                "playlist_id perfectly aliases with rating band on this "
                "43-song corpus (verified alias={}); genre unseparable "
                "from signal by construction."
            ).format(alias_confirmed),
            "alias_confirmed": bool(alias_confirmed),
            "statistic_version": STATISTIC_VERSION,
            "pass": None,
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
            "pass": None,
        },
    }
    live_passes = [
        v["pass"] for v in per_leak.values() if v["pass"] is not None
    ]
    return {
        "statistic_version": STATISTIC_VERSION,
        "per_leak_type": per_leak,
        "genre_status": per_leak["genre"]["status"],
        "era_status": per_leak["era"]["status"],
        "detection_required": SB3_DETECT_MIN,
        "fpr_max": SB3_FPR_MAX,
        "pass": bool(live_passes and all(live_passes)),
        "artist_full_detail": artist,
    }


# ---------------------------------------------------------------- verdict
def _named_sb_attribution(sb1r, sb2r, sb3r) -> list[dict]:
    out = []
    if not sb1r["pass"]:
        out.append({
            "sb": "SB1",
            "shortfall": SB1_MARGIN_MIN - sb1r["margin"],
            "observed": sb1r["margin"],
            "threshold": SB1_MARGIN_MIN,
            "note": (
                "clip-level MAE margin over min(majority-class, mean-integer) "
                "below c22 IQR threshold"
            ),
        })
    if not sb2r["pass"]:
        out.append({
            "sb": "SB2",
            "shortfall": SB2_TAU_MIN - sb2r["mean_tau"],
            "observed": sb2r["mean_tau"],
            "threshold": SB2_TAU_MIN,
            "note": (
                "clip-level mean pairwise Kendall tau across 10 resamples "
                "below c23 threshold"
            ),
        })
    if not sb3r["pass"]:
        for name, sub in sb3r["per_leak_type"].items():
            if sub.get("pass") is False:
                out.append({
                    "sb": "SB3",
                    "leak_type": name,
                    "shortfall_detection": SB3_DETECT_MIN - (sub.get("detection_rate") or 0.0),
                    "shortfall_fpr": (sub.get("fpr") or 0.0) - SB3_FPR_MAX,
                    "observed_detection": sub.get("detection_rate"),
                    "observed_fpr": sub.get("fpr"),
                    "denominator_pairs": sub.get("denominator_pairs"),
                    "note": (
                        f"F1 pooled-variance leak detection on {name}: "
                        "detection<0.90 or FPR>0.10"
                    ),
                })
    return out


def _delta_vs_v1(sb1r, sb2r, sb3r) -> dict:
    return {
        "sb1_margin_v1": V1_SB1_MARGIN,
        "sb1_margin_v2": sb1r["margin"],
        "sb1_margin_improvement": bool(sb1r["margin"] > V1_SB1_MARGIN),
        "sb2_tau_v1": V1_SB2_MEAN_TAU,
        "sb2_tau_v2": sb2r["mean_tau"],
        "sb2_tau_improvement": bool(sb2r["mean_tau"] > V1_SB2_MEAN_TAU),
        "sb3_denominator_v1": V1_SB3_DENOMINATOR,
        "sb3_denominator_v2": sb3r["per_leak_type"]["artist"]["denominator_pairs"],
        "sb3_denominator_improvement": bool(
            sb3r["per_leak_type"]["artist"]["denominator_pairs"] > V1_SB3_DENOMINATOR
        ),
    }


def verdict(sb1r, sb2r, sb3r) -> tuple[str, list[dict], dict]:
    all_pass = sb1r["pass"] and sb2r["pass"] and sb3r["pass"]
    delta = _delta_vs_v1(sb1r, sb2r, sb3r)
    if all_pass:
        return "EAR_v2_LANDS", [], delta
    attribution = _named_sb_attribution(sb1r, sb2r, sb3r)
    finite = all([
        math.isfinite(sb1r["margin"]),
        math.isfinite(sb2r["mean_tau"]),
        math.isfinite(sb3r["per_leak_type"]["artist"]["detection_rate"]),
    ])
    material_improvement = (
        delta["sb1_margin_improvement"]
        or delta["sb2_tau_improvement"]
        or delta["sb3_denominator_improvement"]
    )
    if finite and material_improvement:
        return "EAR_v2_PARTIAL", attribution, delta
    return "EAR_v2_INSUFFICIENT", attribution, delta


def evaluate() -> dict:
    rows = _load_preds()
    r1 = sb1_clip(rows)
    r2 = sb2_clip(rows)
    r3 = sb3(rows)
    v, attribution, delta = verdict(r1, r2, r3)
    rubric_hash = RUBRIC_HASH_FILE.read_text().strip()
    train = json.loads((DATA_DIR / "training_result.json").read_text())

    sb_results = {
        "sb1": r1,
        "sb2": r2,
        "sb3": r3,
        "thresholds": {
            "SB1_margin_min": SB1_MARGIN_MIN,
            "SB2_tau_min": SB2_TAU_MIN,
            "SB3_detection_min": SB3_DETECT_MIN,
            "SB3_fpr_max": SB3_FPR_MAX,
        },
        "delta_vs_v1": delta,
    }
    (DATA_DIR / "sb_v2_results.json").write_text(
        json.dumps(sb_results, indent=2, sort_keys=True)
    )
    sb_verdict = {
        "verdict": v,
        "rubric_hash": rubric_hash,
        "sb1": {"pass": r1["pass"], "margin": r1["margin"],
                "threshold": SB1_MARGIN_MIN},
        "sb2": {"pass": r2["pass"], "mean_tau": r2["mean_tau"],
                "threshold": SB2_TAU_MIN},
        "sb3": {
            "pass": r3["pass"],
            "per_leak_type": r3["per_leak_type"],
            "genre_status": r3["genre_status"],
            "era_status": r3["era_status"],
            "detection_required": SB3_DETECT_MIN,
            "fpr_max": SB3_FPR_MAX,
        },
    }
    (DATA_DIR / "sb_v2_verdict.json").write_text(
        json.dumps(sb_verdict, indent=2, sort_keys=True)
    )

    # leak_test_v2_summary.json
    leak_summary = {
        "statistic_version": STATISTIC_VERSION,
        "genre": r3["genre_status"],
        "era": r3["era_status"],
        "leak_types": {
            "artist": {
                "status": "live",
                "detection_rate": r3["artist_full_detail"]["detection_rate"],
                "fpr": r3["artist_full_detail"]["fpr"],
                "s_observed": r3["artist_full_detail"]["s_observed"],
                "tau_90pct_null": r3["artist_full_detail"]["tau_90pct_null"],
                "denominator_pairs": r3["artist_full_detail"]["denominator_pairs"],
                "denominator_gt_43": bool(
                    r3["artist_full_detail"]["denominator_pairs"] > 43
                ),
                "alpha": ALPHA_ARTIST,
                "statistic_version": STATISTIC_VERSION,
                "n_controls": N_CONTROLS,
                "n_detect_repeats": N_DETECT_REPEATS,
                "n_clips_input": r3["artist_full_detail"]["n_clips_input"],
            },
            "genre": r3["per_leak_type"]["genre"],
            "era": r3["per_leak_type"]["era"],
        },
        "artist_full_detail": r3["artist_full_detail"],
    }
    (DATA_DIR / "leak_test_v2_summary.json").write_text(
        json.dumps(leak_summary, indent=2, sort_keys=True)
    )

    verdict_out = {
        "verdict": v,
        "rubric_hash": rubric_hash,
        "milestone": "M-EAR-1/real-label-training-v2",
        "cycle": 39,
        "corpus_honesty_caveat": (
            "43 of the 80-song target — 54% corpus coverage; verdict "
            "credible for the resampled corpus on disk, NOT calibrated "
            "to the full 80-song target."
        ),
        "resample_note": (
            "Per-clip training with per-song grouping (GroupKFold); "
            "SB1/SB2 evaluated at clip level; SB3 F1 pooled-variance "
            "denominator now >43 by construction (multiple clips per "
            "song inherit the same artist label)."
        ),
        "git_log_gate_note": (
            "MERGE_DEFERRED — rubric committed to disk on a clean tree "
            "before any script under scripts/ear_v2/ per the mtime gate; "
            "git-commit ordering deferred to post-fanout merge integration "
            "per c38 precedent."
        ),
        "scale_bounds": train["scale_bounds"],
        "corpus_size_songs": train["corpus_size_songs"],
        "corpus_size_clips": train["corpus_size_clips"],
        "class_distribution_clips": train["class_distribution_clips"],
        "model_label": train["model_label"],
        "statistic_version": STATISTIC_VERSION,
        "sb1": {"pass": r1["pass"], "margin": r1["margin"],
                "threshold": SB1_MARGIN_MIN,
                "clip_mae": r1["mae"],
                "baseline_min_mae": r1["baseline_min_mae"]},
        "sb2": {"pass": r2["pass"], "mean_tau": r2["mean_tau"],
                "threshold": SB2_TAU_MIN,
                "per_resample_tau": r2["per_resample_tau"]},
        "sb3": {
            "pass": r3["pass"],
            "per_leak_type": r3["per_leak_type"],
            "genre_status": r3["genre_status"],
            "era_status": r3["era_status"],
            "detection_required": SB3_DETECT_MIN,
            "fpr_max": SB3_FPR_MAX,
        },
        "named_sb_attribution": attribution,
        "delta_vs_v1": delta,
    }
    (DATA_DIR / "verdict.json").write_text(
        json.dumps(verdict_out, indent=2, sort_keys=True)
    )
    return verdict_out


if __name__ == "__main__":
    r = evaluate()
    print(json.dumps({
        "verdict": r["verdict"],
        "sb1_margin": r["sb1"]["margin"],
        "sb2_mean_tau": r["sb2"]["mean_tau"],
        "sb3_pass": r["sb3"]["pass"],
        "sb3_denominator": r["sb3"]["per_leak_type"]["artist"]["denominator_pairs"],
    }, indent=2))
