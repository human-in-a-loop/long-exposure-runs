"""Evaluate the three cycle-26 frozen success bars against real-label output.

SB1 — held-out mean MAE beats min(majority-class MAE, mean-integer MAE)
      by a margin > 0.5909 (cycle-22 recipe-envelope IQR).
SB2 — mean pairwise Kendall tau >= 0.4 across 10 SHA-256-seeded
      stratified bootstrap resamples per c23 threshold.
SB3 — leak-test detection >= 0.90 at alpha=1.0 on 'artist' column.
      Delegated to scripts.ear_v0.leak_ablation_v0.

All SB2 randomness derived from SHA-256(f"resample_{r}|{song_sha}")
rank — NO PRNG.
"""
# created: 2026-08-29T07:25:00Z  cycle: 36  run_id: run-2026-08-28T040704Z
# agent: worker (clone-0, fork 87da4f517029)  milestone: M-EAR-1/real-label-training-v0
from __future__ import annotations
import sys
assert sys.executable == "/usr/bin/python3", sys.executable

import hashlib
import json
from pathlib import Path

import numpy as np

DATA_DIR = Path("data/ear_v0")
SB1_MARGIN_MIN = 0.5909  # cycle-22 recipe-envelope IQR
SB2_TAU_MIN = 0.4
SB3_DETECT_MIN = 0.90
N_RESAMPLES = 10
BANDS = (4, 5, 6, 7)


def _load_preds() -> list[dict]:
    rows = []
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


def _majority_class_mae(y_true: np.ndarray) -> tuple[float, int]:
    """MAE if we always predict the modal band."""
    vals, cnt = np.unique(y_true, return_counts=True)
    mode = int(vals[np.argmax(cnt)])
    return float(np.mean(np.abs(y_true - mode))), mode


def _mean_integer_mae(y_true: np.ndarray) -> tuple[float, int]:
    """MAE if we always predict the rounded population mean."""
    mean_int = int(round(float(y_true.mean())))
    return float(np.mean(np.abs(y_true - mean_int))), mean_int


def _kendall_tau(a: np.ndarray, b: np.ndarray) -> float:
    """Tau-b via scipy fallback to pure numpy if unavailable."""
    try:
        from scipy.stats import kendalltau
        t, _ = kendalltau(a, b)
        return float(t) if np.isfinite(t) else 0.0
    except Exception:
        n = a.size
        con = 0
        dis = 0
        for i in range(n):
            for j in range(i + 1, n):
                da = a[i] - a[j]
                db = b[i] - b[j]
                if da * db > 0:
                    con += 1
                elif da * db < 0:
                    dis += 1
        return (con - dis) / max(1, con + dis)


def _sha_rank(payload: str) -> int:
    return int.from_bytes(
        hashlib.sha256(payload.encode()).digest()[:8], "big"
    )


def sb1(rows: list[dict]) -> dict:
    y_true = np.array([r["band_true"] for r in rows])
    y_pred = np.array([r["band_pred_int"] for r in rows])
    mae = float(np.mean(np.abs(y_pred - y_true)))
    mc_mae, mc_val = _majority_class_mae(y_true)
    mi_mae, mi_val = _mean_integer_mae(y_true)
    baseline_min = min(mc_mae, mi_mae)
    margin = baseline_min - mae
    return {
        "mae": mae,
        "majority_mae": mc_mae, "majority_value": mc_val,
        "mean_int_mae": mi_mae, "mean_int_value": mi_val,
        "baseline_min_mae": baseline_min,
        "margin": margin,
        "margin_required": SB1_MARGIN_MIN,
        "pass": bool(margin > SB1_MARGIN_MIN),
    }


def _stratified_bootstrap_indices(
    rows: list[dict], resample_id: int
) -> np.ndarray:
    """SHA-256-derived per-band stratified resample (with replacement)."""
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
            payload = f"resample_{resample_id}|band_{b}|k_{k}"
            idx = _sha_rank(payload) % n
            selected.append(pool[idx])
    return np.array(sorted(selected))


def sb2(rows: list[dict]) -> dict:
    """Mean pairwise Kendall tau of resample predictions vs truths."""
    per_resample: list[float] = []
    for r in range(N_RESAMPLES):
        idx = _stratified_bootstrap_indices(rows, r)
        y_true = np.array([rows[i]["band_true"] for i in idx])
        y_pred = np.array([rows[i]["band_pred_int"] for i in idx])
        tau = _kendall_tau(y_true, y_pred)
        per_resample.append(tau)
    mean_tau = float(np.mean(per_resample))
    return {
        "per_resample_tau": [float(t) for t in per_resample],
        "mean_tau": mean_tau,
        "tau_required": SB2_TAU_MIN,
        "n_resamples": N_RESAMPLES,
        "pass": bool(mean_tau >= SB2_TAU_MIN),
    }


def sb3() -> dict:
    """Delegate to leak_ablation_v0.summary()."""
    from scripts.ear_v0.leak_ablation_v0 import summarize
    summary = summarize()
    detect = float(summary.get("artist", {}).get("detection_rate", 0.0))
    return {
        "artist_detection": detect,
        "detection_required": SB3_DETECT_MIN,
        "genre_status": summary.get("genre", {}).get("status",
                                                    "deferred_aliased_with_band"),
        "era_status": summary.get("era", {}).get("status",
                                                 "deferred_no_metadata"),
        "artist_parse_failures": summary.get("artist_parse_failures", 0),
        "pass": bool(detect >= SB3_DETECT_MIN),
    }


def verdict(sb1r, sb2r, sb3r) -> str:
    if not sb1r["pass"]:
        return "EAR_v0_INSUFFICIENT"
    other_pass = sum(1 for x in [sb2r["pass"], sb3r["pass"]] if x)
    if other_pass == 2:
        return "EAR_v0_LANDS"
    if other_pass == 1:
        return "EAR_v0_PARTIAL"
    return "EAR_v0_INSUFFICIENT"


def evaluate() -> dict:
    rows = _load_preds()
    r1 = sb1(rows)
    r2 = sb2(rows)
    r3 = sb3()
    v = verdict(r1, r2, r3)
    with open("data/ear_v0/rubric_hash.txt") as f:
        rh = f.read().strip()
    with open("data/ear_v0/training_result.json") as f:
        tres = json.load(f)
    out = {
        "verdict": v,
        "rubric_hash": rh,
        "sb1": r1,
        "sb2": r2,
        "sb3": r3,
        "scale_bounds": tres["scale_bounds"],
        "corpus_size": tres["corpus_size"],
        "class_distribution": tres["class_distribution"],
        "model_label": tres["model_label"],
    }
    with open(DATA_DIR / "verdict.json", "w") as f:
        json.dump(out, f, indent=2, sort_keys=True)
    return out


if __name__ == "__main__":
    r = evaluate()
    print(json.dumps({"verdict": r["verdict"],
                      "sb1_margin": r["sb1"]["margin"],
                      "sb2_mean_tau": r["sb2"]["mean_tau"],
                      "sb3_artist_detection": r["sb3"]["artist_detection"]},
                     indent=2))
