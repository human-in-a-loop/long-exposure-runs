#!/usr/bin/env python3
# ---
# created: 2026-08-28T23:45:00Z
# cycle: 29
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-GEN-1/collision-model-hash-space-geometry
# ---
"""Multiple-testing correction for the cycle-28 35-cell p-vector.

Reads the 35 (rule_type x batch) p-values from
data/collision_model/hash_uniformity_summary.json (cycle-28 anchor,
read-only) and applies three corrections at alpha = 0.05:

  * Bonferroni: reject if p_i <= alpha / m
  * Sidak:      reject if p_i <= 1 - (1 - alpha)^(1/m)
  * Benjamini-Hochberg (BH-FDR at q=0.05): sort ascending; the largest
    rank i with p_(i) <= i * q / m defines the reject set (all j <= i).

Emits data/collision_model/multiple_testing_correction.json.

Analytical / deterministic.  No PRNG.  No sidecar_nonfactor.
Does not import i4_stratified.
"""
from __future__ import annotations

import json
import pathlib
import sys

assert sys.executable == "/usr/bin/python3", (
    f"multiple_testing_correction requires /usr/bin/python3, got {sys.executable}"
)

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "data" / "collision_model"
UNIF = OUT_DIR / "hash_uniformity_summary.json"

ALPHA = 0.05
Q = 0.05
RULE_TYPES = ("harmonic", "rhythmic", "melodic", "form", "arrangement")


def load_cells() -> list[dict]:
    """Return the 35 cells as list of {batch, rule_type, p_value, chi2, dof, K, N_salts}."""
    s = json.loads(UNIF.read_text())
    cells: list[dict] = []
    for batch in sorted(s["batches"].keys()):
        per_rt = s["batches"][batch]
        for rt in RULE_TYPES:
            e = per_rt[rt]
            cells.append(
                {
                    "batch": batch,
                    "rule_type": rt,
                    "p_value": float(e["p_value"]),
                    "chi2": float(e["chi2"]),
                    "dof": int(e["dof"]),
                    "K": int(e["K"]),
                    "N_salts": int(e["N_salts"]),
                }
            )
    return cells


def bonferroni(cells: list[dict], alpha: float) -> tuple[list[bool], float]:
    m = len(cells)
    thresh = alpha / m
    return [c["p_value"] <= thresh for c in cells], thresh


def sidak(cells: list[dict], alpha: float) -> tuple[list[bool], float]:
    m = len(cells)
    thresh = 1.0 - (1.0 - alpha) ** (1.0 / m)
    return [c["p_value"] <= thresh for c in cells], thresh


def benjamini_hochberg(cells: list[dict], q: float) -> tuple[list[bool], list[dict]]:
    """Return (per_cell_reject, per_cell_rank_annotation)."""
    m = len(cells)
    order = sorted(range(m), key=lambda i: (cells[i]["p_value"], i))
    # Find largest rank i (1-indexed) with p_(i) <= i * q / m.
    max_reject_rank = 0
    for rank_1based, idx in enumerate(order, start=1):
        threshold_i = rank_1based * q / m
        if cells[idx]["p_value"] <= threshold_i:
            max_reject_rank = rank_1based
    reject_positions = {order[i] for i in range(max_reject_rank)}
    per_cell = [(i in reject_positions) for i in range(m)]
    rank_annot: list[dict] = [dict() for _ in range(m)]
    for rank_1based, idx in enumerate(order, start=1):
        rank_annot[idx] = {
            "bh_rank": rank_1based,
            "bh_threshold_i": rank_1based * q / m,
        }
    return per_cell, rank_annot


def main(argv: list[str]) -> int:
    cells = load_cells()
    m = len(cells)
    assert m == 35, f"expected 35 cells, got {m}"

    bonf_reject, bonf_thresh = bonferroni(cells, ALPHA)
    sidak_reject, sidak_thresh = sidak(cells, ALPHA)
    bh_reject, bh_annot = benjamini_hochberg(cells, Q)

    per_cell: list[dict] = []
    for i, c in enumerate(cells):
        row = dict(c)
        row["bonferroni_reject"] = bool(bonf_reject[i])
        row["sidak_reject"] = bool(sidak_reject[i])
        row["bh_reject"] = bool(bh_reject[i])
        row.update(bh_annot[i])
        per_cell.append(row)

    survivors_bonf = [c for c, r in zip(cells, bonf_reject) if r]
    survivors_sidak = [c for c, r in zip(cells, sidak_reject) if r]
    survivors_bh = [c for c, r in zip(cells, bh_reject) if r]

    out = {
        "input_uniformity_path": str(UNIF.relative_to(ROOT)),
        "alpha": ALPHA,
        "q_bh": Q,
        "m_cells": m,
        "bonferroni_threshold": bonf_thresh,
        "sidak_threshold": sidak_thresh,
        "bh_max_reject_rank": sum(1 for r in bh_reject if r),
        "counts": {
            "bonferroni_survivors": len(survivors_bonf),
            "sidak_survivors": len(survivors_sidak),
            "bh_survivors": len(survivors_bh),
        },
        "survivors_bh": [
            {"batch": c["batch"], "rule_type": c["rule_type"], "p_value": c["p_value"]}
            for c in survivors_bh
        ],
        "survivors_bonferroni": [
            {"batch": c["batch"], "rule_type": c["rule_type"], "p_value": c["p_value"]}
            for c in survivors_bonf
        ],
        "survivors_sidak": [
            {"batch": c["batch"], "rule_type": c["rule_type"], "p_value": c["p_value"]}
            for c in survivors_sidak
        ],
        "per_cell": per_cell,
        "generator": "scripts/analysis/multiple_testing_correction.py",
        "run_stamp": "2026-08-28T23:45:00Z",
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    p = OUT_DIR / "multiple_testing_correction.json"
    p.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(f"[multiple_testing_correction] wrote {p}")
    print(
        f"[multiple_testing_correction] m={m} bonferroni_survivors="
        f"{out['counts']['bonferroni_survivors']} sidak_survivors="
        f"{out['counts']['sidak_survivors']} bh_survivors="
        f"{out['counts']['bh_survivors']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
