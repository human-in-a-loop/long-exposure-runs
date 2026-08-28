#!/usr/bin/env python3
# ---
# created: 2026-08-28T23:55:00Z
# cycle: 29
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-GEN-1/collision-model-hash-space-geometry
# ---
"""Leave-one-cell-out contribution analysis.

For each of the 35 (rule_type x batch) cells: hold that cell out,
recompute BH survival on the remaining 34 cells, and record whether
any survivor remains. Also sum chi-squared across the retained cells
as a rough aggregate concentration measure. This tells us whether any
single cell is carrying the multiple-testing signal.

Reads data/collision_model/hash_uniformity_summary.json (cycle-28
anchor, read-only).

Emits data/collision_model/leave_one_cell_out.json.

Analytical / deterministic.  No PRNG.  No sidecar_nonfactor.
Does not import i4_stratified.
"""
from __future__ import annotations

import json
import pathlib
import sys

assert sys.executable == "/usr/bin/python3", (
    f"leave_one_cell_out_contribution requires /usr/bin/python3, got {sys.executable}"
)

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "data" / "collision_model"
UNIF = OUT_DIR / "hash_uniformity_summary.json"

BH_Q = 0.05
RULE_TYPES = ("harmonic", "rhythmic", "melodic", "form", "arrangement")


def _bh_reject_count(pvals: list[float], q: float) -> int:
    m = len(pvals)
    if m == 0:
        return 0
    order = sorted(range(m), key=lambda i: (pvals[i], i))
    max_reject_rank = 0
    for rank_1based, idx in enumerate(order, start=1):
        if pvals[idx] <= rank_1based * q / m:
            max_reject_rank = rank_1based
    return max_reject_rank


def main(argv: list[str]) -> int:
    summary = json.loads(UNIF.read_text())
    cells: list[dict] = []
    for batch in sorted(summary["batches"].keys()):
        per_rt = summary["batches"][batch]
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

    m = len(cells)
    baseline_bh_reject_count = _bh_reject_count([c["p_value"] for c in cells], BH_Q)
    baseline_chi2_sum = sum(c["chi2"] for c in cells)

    per_cell: list[dict] = []
    for i, held in enumerate(cells):
        rest_p = [cells[j]["p_value"] for j in range(m) if j != i]
        rest_chi2_sum = sum(cells[j]["chi2"] for j in range(m) if j != i)
        loco_bh_reject = _bh_reject_count(rest_p, BH_Q)
        per_cell.append(
            {
                "batch": held["batch"],
                "rule_type": held["rule_type"],
                "p_value_held_out": held["p_value"],
                "chi2_held_out": held["chi2"],
                "bh_survivors_when_held_out": loco_bh_reject,
                "chi2_sum_of_remaining": rest_chi2_sum,
                "delta_bh_survivors": loco_bh_reject - baseline_bh_reject_count,
                "delta_chi2_sum": rest_chi2_sum - baseline_chi2_sum,
            }
        )

    # Identify cells whose removal changes the BH survivor count.
    changers = [c for c in per_cell if c["delta_bh_survivors"] != 0]
    single_cell_dependent = any(
        c["bh_survivors_when_held_out"] == 0 and baseline_bh_reject_count > 0
        for c in per_cell
    )
    concentration_note = (
        f"baseline BH-survivors = {baseline_bh_reject_count}; changers under LOCO = "
        f"{len(changers)}"
    )

    out = {
        "input_uniformity_path": str(UNIF.relative_to(ROOT)),
        "bh_q": BH_Q,
        "m_cells": m,
        "baseline_bh_survivors": baseline_bh_reject_count,
        "baseline_chi2_sum": baseline_chi2_sum,
        "per_cell": per_cell,
        "changers_under_loco": changers,
        "single_cell_carries_signal": single_cell_dependent,
        "concentration_note": concentration_note,
        "generator": "scripts/analysis/leave_one_cell_out_contribution.py",
        "run_stamp": "2026-08-28T23:55:00Z",
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    p = OUT_DIR / "leave_one_cell_out.json"
    p.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(f"[leave_one_cell_out] wrote {p}")
    print(
        f"[leave_one_cell_out] baseline BH survivors = {baseline_bh_reject_count}; "
        f"LOCO changers = {len(changers)}; "
        f"single-cell dependent = {single_cell_dependent}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
