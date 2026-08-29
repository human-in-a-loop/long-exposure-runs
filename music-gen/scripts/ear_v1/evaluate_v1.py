#!/usr/bin/python3
"""Evaluate SB1/SB2/SB3 against c26-frozen thresholds and emit verdict.

SB1: aggregate MAE margin over min(majority-class, mean-integer) > 0.5909
     (c22 recipe-envelope IQR).
SB2: mean pairwise Kendall tau over 10 SHA-256-seeded stratified
     bootstrap resamples >= 0.4.
SB3: F1 pooled-variance detection >= 0.90 at alpha=1.0 per leak type
     AND FPR <= 0.10 per leak type. Deferred leak types (genre, era)
     are surfaced with status fields but do not gate the verdict —
     rubric explicitly names them as deferred structural pathologies.

Emits:
  - data/ear_v1/sb_results.json
  - data/ear_v1/verdict.json  (embeds rubric_hash verbatim)
"""
# created: 2026-08-29T11:08:00Z  cycle: 38  run_id: run-2026-08-28T040704Z
# agent: worker (clone-0)  milestone: M-EAR-1/real-label-training-v1
from __future__ import annotations

import sys
assert sys.executable == "/usr/bin/python3", sys.executable

import hashlib
import json
import math
from pathlib import Path

import numpy as np

DATA_DIR = Path("data/ear_v1")
RUBRIC_HASH_FILE = DATA_DIR / "rubric_hash.txt"
SB1_MARGIN_MIN = 0.5909
SB2_TAU_MIN = 0.4
SB3_DETECT_MIN = 0.90
SB3_FPR_MAX = 0.10
N_RESAMPLES = 10
BANDS = (4, 5, 6, 7)


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
            rows.append(r)
    return rows


def sb1(rows: list[dict]) -> dict:
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


def sb2(rows: list[dict]) -> dict:
    per: list[float] = []
    for r in range(N_RESAMPLES):
        idx = _stratified_bootstrap_indices(rows, r)
        y_true = np.array([rows[i]["band_true"] for i in idx])
        y_pred = np.array([rows[i]["band_pred_int"] for i in idx])
        per.append(_kendall_tau(y_true, y_pred))
    mean_tau = float(np.mean(per))
    return {
        "per_resample_tau": [float(t) for t in per],
        "mean_tau": mean_tau,
        "tau_required": SB2_TAU_MIN,
        "n_resamples": N_RESAMPLES,
        "pass": bool(mean_tau >= SB2_TAU_MIN),
    }


def sb3() -> dict:
    """Load leak_test_summary.json and evaluate per-leak-type
    (detection >= 0.90) AND (FPR <= 0.10).

    Deferred leak types (genre, era) are surfaced as status fields;
    the rubric explicitly does not gate on them. The verdict is
    computed over LIVE leak types only.
    """
    summary = json.loads(
        (DATA_DIR / "leak_test_summary.json").read_text()
    )
    per_leak: dict[str, dict] = {}
    for name, sub in summary["leak_types"].items():
        status = sub.get("status", "live")
        if status != "live":
            per_leak[name] = {
                "status": status,
                "detection_rate": None,
                "fpr": None,
                "pass_detection": None,
                "pass_fpr": None,
                "pass": None,  # not evaluated
            }
            continue
        det = float(sub.get("detection_rate") or 0.0)
        fpr = float(sub.get("fpr") or 0.0)
        pass_det = bool(det >= SB3_DETECT_MIN)
        pass_fpr = bool(fpr <= SB3_FPR_MAX)
        per_leak[name] = {
            "status": status,
            "detection_rate": det,
            "fpr": fpr,
            "detection_required": SB3_DETECT_MIN,
            "fpr_max": SB3_FPR_MAX,
            "pass_detection": pass_det,
            "pass_fpr": pass_fpr,
            "pass": bool(pass_det and pass_fpr),
        }
    live_passes = [v["pass"] for v in per_leak.values() if v["pass"] is not None]
    all_live_pass = bool(live_passes and all(live_passes))
    return {
        "statistic_version": summary["statistic_version"],
        "per_leak_type": per_leak,
        "genre_status": summary["genre"],
        "era_status": summary["era"],
        "detection_required": SB3_DETECT_MIN,
        "fpr_max": SB3_FPR_MAX,
        "pass": all_live_pass,
    }


def _named_sb_attribution(sb1r, sb2r, sb3r) -> list[dict]:
    out = []
    if not sb1r["pass"]:
        out.append({
            "sb": "SB1",
            "shortfall": SB1_MARGIN_MIN - sb1r["margin"],
            "observed": sb1r["margin"],
            "threshold": SB1_MARGIN_MIN,
            "note": (
                "held-out MAE margin over min(majority-class, mean-integer) "
                "below c22 IQR threshold"
            ),
        })
    if not sb2r["pass"]:
        out.append({
            "sb": "SB2",
            "shortfall": SB2_TAU_MIN - sb2r["mean_tau"],
            "observed": sb2r["mean_tau"],
            "threshold": SB2_TAU_MIN,
            "note": "mean pairwise Kendall tau across 10 resamples below c23 threshold",
        })
    if not sb3r["pass"]:
        # Attribution is per live leak type.
        for name, sub in sb3r["per_leak_type"].items():
            if sub.get("pass") is False:
                out.append({
                    "sb": "SB3",
                    "leak_type": name,
                    "shortfall_detection": SB3_DETECT_MIN - (sub.get("detection_rate") or 0.0),
                    "shortfall_fpr": (sub.get("fpr") or 0.0) - SB3_FPR_MAX,
                    "observed_detection": sub.get("detection_rate"),
                    "observed_fpr": sub.get("fpr"),
                    "note": (
                        f"F1 pooled-variance leak detection on {name}: "
                        "detection<0.90 or FPR>0.10"
                    ),
                })
    return out


def verdict(sb1r, sb2r, sb3r) -> tuple[str, list[dict]]:
    all_pass = sb1r["pass"] and sb2r["pass"] and sb3r["pass"]
    if all_pass:
        return "EAR_v1_LANDS", []
    attribution = _named_sb_attribution(sb1r, sb2r, sb3r)
    # Distinguish PARTIAL (at least one SB short but measurement credible)
    # vs INSUFFICIENT (chassis/corpus pathology blocks credible measurement).
    # On this corpus (43/80 songs = 54%), all three SBs failing is a
    # measurable partial result, not a chassis pathology — SB1 has a well-
    # defined MAE, SB2 has finite tau, SB3 has finite F1 detection. Report
    # PARTIAL with named-SB attribution.
    finite_measurements = all([
        math.isfinite(sb1r["margin"]),
        math.isfinite(sb2r["mean_tau"]),
        all(math.isfinite(v["detection_rate"])
            for v in sb3r["per_leak_type"].values()
            if v.get("detection_rate") is not None),
    ])
    if finite_measurements:
        return "EAR_v1_PARTIAL", attribution
    return "EAR_v1_INSUFFICIENT", attribution


def evaluate() -> dict:
    rows = _load_preds()
    r1 = sb1(rows)
    r2 = sb2(rows)
    r3 = sb3()
    v, attribution = verdict(r1, r2, r3)
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
    }
    (DATA_DIR / "sb_results.json").write_text(
        json.dumps(sb_results, indent=2, sort_keys=True)
    )

    verdict_out = {
        "verdict": v,
        "rubric_hash": rubric_hash,
        "milestone": "M-EAR-1/real-label-training-v1",
        "cycle": 38,
        "corpus_honesty_caveat": (
            "43 of the 80-song target — 54% corpus coverage; "
            "verdict credible for the corpus on disk, NOT calibrated "
            "to the full 80-song target."
        ),
        "scale_bounds": train["scale_bounds"],
        "corpus_size": train["corpus_size"],
        "class_distribution": train["class_distribution"],
        "model_label": train["model_label"],
        "statistic_version": "F1_pooled_variance_v1",
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
        "named_sb_attribution": attribution,
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
    }, indent=2))
