#!/usr/bin/env python3
# ---
# created: 2026-08-28T14:25:00Z
# cycle: 27
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-GEN-1/collision-model-shape-mechanism
# ---
"""Apply the frozen 4-verdict rubric to shape_mechanism_fit.json.

Rubric (locked BEFORE analysis — see docs/collision_model_shape_mechanism.md):

  M1_EXPLAINS       R2_M1 >= 0.6 AND R2_M2 < R2_M1 - 0.15
  M2_EXPLAINS       R2_M2 >= 0.6 AND R2_M1 < R2_M2 - 0.15
  BOTH_EXPLAIN      R2_M1 >= 0.6 AND R2_M2 >= 0.6 AND |R2_M1 - R2_M2| <= 0.15
  NEITHER_EXPLAINS  max(R2_M1, R2_M2) < 0.6

Analytical / deterministic.  No PRNG.  No sidecar_nonfactor.
"""
from __future__ import annotations

import datetime as _dt
import json
import pathlib
import sys

assert sys.executable == "/usr/bin/python3", (
    f"shape_mechanism_verdict requires /usr/bin/python3, got {sys.executable}"
)

RUBRIC_THRESHOLDS = {
    "r2_min": 0.6,
    "margin": 0.15,
}


def apply_rubric(r2_m1: float | None, r2_m2: float | None) -> dict:
    thresh_r2 = RUBRIC_THRESHOLDS["r2_min"]
    margin = RUBRIC_THRESHOLDS["margin"]

    r1 = float(r2_m1) if r2_m1 is not None else float("-inf")
    r2 = float(r2_m2) if r2_m2 is not None else float("-inf")

    if r1 >= thresh_r2 and r2 >= thresh_r2 and abs(r1 - r2) <= margin:
        v = "BOTH_EXPLAIN"
        reason = (
            f"R2_M1={r1:.4f} and R2_M2={r2:.4f} both >= {thresh_r2}, "
            f"|delta|={abs(r1-r2):.4f} <= {margin}"
        )
    elif r1 >= thresh_r2 and r2 < r1 - margin:
        v = "M1_EXPLAINS"
        reason = (
            f"R2_M1={r1:.4f} >= {thresh_r2}, "
            f"R2_M2={r2:.4f} < R2_M1 - {margin}"
        )
    elif r2 >= thresh_r2 and r1 < r2 - margin:
        v = "M2_EXPLAINS"
        reason = (
            f"R2_M2={r2:.4f} >= {thresh_r2}, "
            f"R2_M1={r1:.4f} < R2_M2 - {margin}"
        )
    elif max(r1, r2) < thresh_r2:
        v = "NEITHER_EXPLAINS"
        reason = (
            f"max(R2_M1={r1:.4f}, R2_M2={r2:.4f}) < {thresh_r2}"
        )
    else:
        # Ambiguous zone: one at threshold but not strictly dominating; treat as NEITHER
        v = "NEITHER_EXPLAINS"
        reason = (
            f"threshold met by one mechanism but no strict dominance: "
            f"R2_M1={r1:.4f}, R2_M2={r2:.4f}"
        )
    return {"verdict": v, "reason": reason}


def run(fit_path: pathlib.Path) -> dict:
    fit = json.loads(fit_path.read_text())
    r2_m1 = fit.get("R2_M1_mean")
    r2_m2 = fit.get("R2_M2_mean")
    rub = apply_rubric(r2_m1, r2_m2)
    return {
        "verdict": rub["verdict"],
        "verdict_reason": rub["reason"],
        "R2_M1": r2_m1,
        "R2_M2": r2_m2,
        "cycle_26_baseline_R2_shape_scaled_mean": fit.get(
            "cycle_26_baseline_R2_shape_scaled_mean"
        ),
        "rubric_thresholds": RUBRIC_THRESHOLDS,
        "rubric_definitions": {
            "M1_EXPLAINS": "R2_M1 >= 0.6 AND R2_M2 < R2_M1 - 0.15",
            "M2_EXPLAINS": "R2_M2 >= 0.6 AND R2_M1 < R2_M2 - 0.15",
            "BOTH_EXPLAIN": "R2_M1 >= 0.6 AND R2_M2 >= 0.6 AND |R2_M1-R2_M2| <= 0.15",
            "NEITHER_EXPLAINS": "max(R2_M1, R2_M2) < 0.6",
        },
        "input_fit_path": str(fit_path),
        "generator": "scripts/analysis/shape_mechanism_verdict.py",
        # Fixed timestamp (analytical / deterministic — no wall-clock leak).
        "run_stamp": "2026-08-28T14:25:00Z",
    }


def _write_json(path: pathlib.Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as fh:
        json.dump(obj, fh, indent=2, sort_keys=True)
        fh.write("\n")


if __name__ == "__main__":  # pragma: no cover
    fit_path = pathlib.Path("data/collision_model/shape_mechanism_fit.json")
    verdict = run(fit_path)
    _write_json(pathlib.Path("data/collision_model/shape_mechanism_verdict.json"), verdict)
    print(
        f"verdict={verdict['verdict']}  R2_M1={verdict['R2_M1']}  "
        f"R2_M2={verdict['R2_M2']}  ({verdict['verdict_reason']})"
    )
