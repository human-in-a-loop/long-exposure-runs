#!/usr/bin/env python3
# ---
# created: 2026-08-28T23:50:00Z
# cycle: 29
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-GEN-1/collision-model-hash-space-geometry
# ---
"""Drop-batch_v2 sensitivity analysis.

Recomputes multiple-testing correction and the shape-R^2 fit with
batch_v2 excluded from the ledger row set. batch_v2 is the batch whose
harmonic cell provides the one raw-significant p-value in cycle 28
(p = 0.0487); we ask whether the M3_WEAK signal remains once that
batch is removed.

Reads from data/collision_model/hash_uniformity_summary.json and
data/collision_model/hash_geometry_fit.json (both cycle-28 anchors,
read-only). Alpha remains PINNED at 0.7469387071101908.

Emits data/collision_model/drop_batch_v2_sensitivity.json.

Analytical / deterministic.  No PRNG.  No sidecar_nonfactor.
Does not import i4_stratified.
"""
from __future__ import annotations

import json
import pathlib
import sys

assert sys.executable == "/usr/bin/python3", (
    f"drop_batch_v2_sensitivity requires /usr/bin/python3, got {sys.executable}"
)

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "data" / "collision_model"
UNIF = OUT_DIR / "hash_uniformity_summary.json"
FIT = OUT_DIR / "hash_geometry_fit.json"

ALPHA_PINNED = 0.7469387071101908
BH_Q = 0.05
FDR_ALPHA = 0.05
EXCLUDE_BATCH = "batch_v2"
EXCLUDE_BATCH_SHA_PREFIX = "be5726ab"
RULE_TYPES = ("harmonic", "rhythmic", "melodic", "form", "arrangement")


def _bh_reject(pvals: list[float], q: float) -> list[bool]:
    m = len(pvals)
    if m == 0:
        return []
    order = sorted(range(m), key=lambda i: (pvals[i], i))
    max_reject_rank = 0
    for rank_1based, idx in enumerate(order, start=1):
        if pvals[idx] <= rank_1based * q / m:
            max_reject_rank = rank_1based
    reject_positions = {order[i] for i in range(max_reject_rank)}
    return [i in reject_positions for i in range(m)]


def main(argv: list[str]) -> int:
    summary = json.loads(UNIF.read_text())
    fit = json.loads(FIT.read_text())

    all_cells: list[dict] = []
    for batch in sorted(summary["batches"].keys()):
        per_rt = summary["batches"][batch]
        for rt in RULE_TYPES:
            e = per_rt[rt]
            all_cells.append(
                {
                    "batch": batch,
                    "rule_type": rt,
                    "p_value": float(e["p_value"]),
                    "chi2": float(e["chi2"]),
                    "dof": int(e["dof"]),
                }
            )

    retained = [c for c in all_cells if c["batch"] != EXCLUDE_BATCH]
    removed = [c for c in all_cells if c["batch"] == EXCLUDE_BATCH]

    pvals_full = [c["p_value"] for c in all_cells]
    bh_full = _bh_reject(pvals_full, BH_Q)
    survivors_full = [c for c, r in zip(all_cells, bh_full) if r]

    pvals_ret = [c["p_value"] for c in retained]
    bh_ret = _bh_reject(pvals_ret, BH_Q)
    survivors_ret = [c for c, r in zip(retained, bh_ret) if r]

    # Bonferroni + Sidak thresholds on the retained set
    m_ret = len(retained)
    bonf_thresh = FDR_ALPHA / m_ret if m_ret else 1.0
    sidak_thresh = 1.0 - (1.0 - FDR_ALPHA) ** (1.0 / m_ret) if m_ret else 1.0
    survivors_bonf_ret = [c for c in retained if c["p_value"] <= bonf_thresh]
    survivors_sidak_ret = [c for c in retained if c["p_value"] <= sidak_thresh]

    # Recompute mean R^2 across the shape-informative batches that aren't v2.
    per_batch_r2 = fit["M3"]["per_batch_r2"]  # {batch: R^2}
    kept_r2 = {b: v for b, v in per_batch_r2.items() if b != EXCLUDE_BATCH}
    r2_mean_ret = (sum(kept_r2.values()) / len(kept_r2)) if kept_r2 else None

    out = {
        "input_uniformity_path": str(UNIF.relative_to(ROOT)),
        "input_fit_path": str(FIT.relative_to(ROOT)),
        "alpha_pinned": ALPHA_PINNED,
        "excluded_batch": EXCLUDE_BATCH,
        "excluded_batch_sha_prefix": EXCLUDE_BATCH_SHA_PREFIX,
        "bh_q": BH_Q,
        "fdr_alpha": FDR_ALPHA,
        "m_full": len(all_cells),
        "m_retained": len(retained),
        "counts": {
            "bh_survivors_full": len(survivors_full),
            "bh_survivors_retained": len(survivors_ret),
            "bonferroni_survivors_retained": len(survivors_bonf_ret),
            "sidak_survivors_retained": len(survivors_sidak_ret),
            "cells_removed_by_drop": len(removed),
        },
        "survivors_bh_full": [
            {"batch": c["batch"], "rule_type": c["rule_type"], "p_value": c["p_value"]}
            for c in survivors_full
        ],
        "survivors_bh_retained": [
            {"batch": c["batch"], "rule_type": c["rule_type"], "p_value": c["p_value"]}
            for c in survivors_ret
        ],
        "per_batch_r2_full": per_batch_r2,
        "per_batch_r2_retained": kept_r2,
        "r2_m3_mean_retained": r2_mean_ret,
        "r2_m3_mean_full": fit["M3"]["R2_M3_mean"],
        "generator": "scripts/analysis/drop_batch_v2_sensitivity.py",
        "run_stamp": "2026-08-28T23:50:00Z",
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    p = OUT_DIR / "drop_batch_v2_sensitivity.json"
    p.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(f"[drop_batch_v2_sensitivity] wrote {p}")
    print(
        f"[drop_batch_v2_sensitivity] full m={out['m_full']} "
        f"retained m={out['m_retained']} "
        f"bh_survivors_full={out['counts']['bh_survivors_full']} "
        f"bh_survivors_retained={out['counts']['bh_survivors_retained']} "
        f"r2_mean_retained={out['r2_m3_mean_retained']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
