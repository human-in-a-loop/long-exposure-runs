#!/usr/bin/env python3
# ---
# created: 2026-08-29T00:45:00Z
# cycle: 30
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-GEN-1/collision-model-semantic-cluster-overlap
# ---
"""Refit BP-scaled per rule_type with K → K_eff-semantic, α PINNED at
cycle-26's α̂ = 0.7469387071101908.

Reads:
- data/collision_model/effective_k_semantic.tsv
- data/collision_model/bp_fit_results.json (cycle-26 anchor;
  observed_per_rule_type + N per batch)

Emits: data/collision_model/semantic_cluster_fit.json

Prediction per (batch, rule_type):
    E_shape[rt] = ALPHA * N*(N-1) / (2 * K_eff-semantic[rt])
K_eff-semantic is clipped to max(K_eff, 1) to keep BP formula bounded
— documented degeneracy handling, identical to cycle-27.

Per-batch shape R² across the 5 rule_types (H, R, M, F, A):
    R² = 1 - SS_res / SS_tot
Where SS_tot uses per-batch mean of observed (matches cycle-26 and
cycle-27 conventions).

Deterministic. No PRNG. Alpha not refit.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import sys

assert sys.executable == "/usr/bin/python3", sys.executable

ROOT = pathlib.Path(__file__).resolve().parents[2]
KEFF_TSV = ROOT / "data" / "collision_model" / "effective_k_semantic.tsv"
BP_FIT = ROOT / "data" / "collision_model" / "bp_fit_results.json"
OUT_JSON = ROOT / "data" / "collision_model" / "semantic_cluster_fit.json"

ALPHA_PINNED = 0.7469387071101908  # cycle-26 anchor. DO NOT REFIT.

# Batch → source-ledger mapping.
BATCH_LEDGER = {
    "batch_v1": "76row",
    "batch_v2": "76row",
    "batch_v3_i3": "86row_i3",
    "batch_v3_i4": "86row_i3",
    "batch_v4": "86row_i3",
    "batch_v5_n16": "86row_i3",
    "batch_v6": "86row_i3",
}

RT_ORDER_SHORT = ("H", "R", "M", "F", "A")
RT_LONG = {"H": "harmonic", "R": "rhythmic", "M": "melodic",
           "F": "form", "A": "arrangement"}


def _read_keff():
    """{(source, short): K_eff-semantic}."""
    out = {}
    with open(KEFF_TSV, "r") as f:
        _ = f.readline()
        for line in f:
            source, rt_long, rt_short, keff = line.rstrip("\n").split("\t")
            out[(source, rt_short)] = int(keff)
    return out


def _r2(obs, pred):
    """R² with SS_tot = sum((obs_i - mean(obs))²).
    Returns 1.0 if SS_tot == 0 and SS_res == 0; else 0.0.
    Otherwise 1 - SS_res / SS_tot (may be < 0)."""
    n = len(obs)
    mean = sum(obs) / n
    ss_tot = sum((o - mean) ** 2 for o in obs)
    ss_res = sum((o - p) ** 2 for o, p in zip(obs, pred))
    if ss_tot == 0.0:
        return 1.0 if ss_res == 0.0 else 0.0
    return 1.0 - ss_res / ss_tot


def main():
    keff = _read_keff()
    bp = json.loads(BP_FIT.read_text())
    per_batch = bp["per_batch"]

    shape_fits = {}
    r2_per_batch = {}
    for entry in per_batch:
        obs_map = entry.get("observed_per_rule_type")
        if not obs_map:
            continue  # v1 (no per-rt obs), v3_i4/v4 (0 pairs by construction)
        batch_id = entry["batch_id"]
        N = int(entry["N"])
        source = BATCH_LEDGER[batch_id]
        obs = []
        pred_m4 = []
        keff_used = {}
        for short in RT_ORDER_SHORT:
            keff_raw = keff[(source, short)]
            keff_clip = max(1, keff_raw)
            keff_used[short] = keff_clip
            obs.append(float(obs_map[short]))
            e_shape = ALPHA_PINNED * N * (N - 1) / (2.0 * keff_clip)
            pred_m4.append(e_shape)
        r2 = _r2(obs, pred_m4)
        shape_fits[batch_id] = {
            "N": N,
            "source_ledger": source,
            "K_eff_semantic": keff_used,
            "observed": obs,
            "predicted_m4_corrected": pred_m4,
            "rule_types_order": list(RT_ORDER_SHORT),
            "r2_shape_m4_corrected": r2,
        }
        r2_per_batch[batch_id] = r2

    r2_mean = sum(r2_per_batch.values()) / len(r2_per_batch)

    # Aggregate total-collision-count R² under M4:
    # total_pred = sum(pred_m4 across rule_types) per batch; compare
    # against observed_total across the same 3 batches for a
    # baseline-consistent aggregate R².
    obs_tot = []
    pred_tot_m4 = []
    for entry in per_batch:
        if not entry.get("observed_per_rule_type"):
            continue
        obs_tot.append(float(entry["observed_total"]))
        pred_tot_m4.append(sum(shape_fits[entry["batch_id"]]
                               ["predicted_m4_corrected"]))
    aggregate_r2_m4 = _r2(obs_tot, pred_tot_m4)

    payload = {
        "generator": "scripts/analysis/semantic_cluster_fit.py",
        "alpha_pinned": ALPHA_PINNED,
        "inputs": {
            "effective_k_semantic_tsv":
                "data/collision_model/effective_k_semantic.tsv",
            "bp_fit_results_json":
                "data/collision_model/bp_fit_results.json",
        },
        "shape_fits": shape_fits,
        "r2_shape_m4_per_batch": r2_per_batch,
        "r2_shape_m4_mean": r2_mean,
        "aggregate_r2_m4_total_counts": aggregate_r2_m4,
        "cycle_26_baseline": {
            "r2_shape_scaled_mean": -0.34140327004561577,
            "aggregate_r2_scaled": 0.958818977481073,
        },
        "note": (
            "Per-batch shape R² over 5 rule_types (H,R,M,F,A). Aggregate "
            "R² is on total-collision-count across the 3 batches with "
            "observed_per_rule_type (batch_v2, batch_v3_i3, batch_v6). "
            "Alpha PINNED at 0.7469387071101908 — never refit."
        ),
    }
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True))
    sha = hashlib.sha256(OUT_JSON.read_bytes()).hexdigest()
    print(f"WROTE {OUT_JSON.relative_to(ROOT)}")
    for bid in sorted(r2_per_batch):
        print(f"  {bid}: R2_shape_M4 = {r2_per_batch[bid]:+.4f}")
    print(f"  MEAN R2_shape_M4 = {r2_mean:+.4f}")
    print(f"  AGGREGATE R2_M4 (total counts) = {aggregate_r2_m4:+.4f}")
    print(f"sha256={sha[:16]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
