#!/usr/bin/env python3
# ---
# created: 2026-08-28T22:55:00Z
# cycle: 28
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-GEN-1/collision-model-hash-space-geometry
# ---
"""Apply the frozen 3-verdict rubric for hash-space-geometry (M3).

Rubric (locked BEFORE analysis, per research brief):

  M3_EXPLAINS
      R2(M3-corrected) >= 0.6 AND at least one (rule_type, batch) has
      chi-squared p < 0.05 non-uniformity.
  M3_WEAK
      R2(M3-corrected) in [0.3, 0.6) OR
      hash-non-uniformity is present but the shape correction is modest.
  M3_REFUTES
      R2(M3-corrected) < 0.3 AND no (rule_type, batch) has significant
      hash-non-uniformity (p < 0.05).

Emits data/collision_model/hash_geometry_verdict.json.
"""
from __future__ import annotations

import json
import pathlib
import sys

assert sys.executable == "/usr/bin/python3", (
    f"hash_geometry_verdict requires /usr/bin/python3, got {sys.executable}"
)

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "data" / "collision_model"

RUBRIC_THRESHOLDS = {
    "r2_explains": 0.6,
    "r2_weak_lower": 0.3,
    "p_value_threshold": 0.05,
}


def classify(r2: float, significant_rule_type_batches: list[tuple[str, str, float]]) -> str:
    any_significant = len(significant_rule_type_batches) > 0
    if r2 >= RUBRIC_THRESHOLDS["r2_explains"] and any_significant:
        return "M3_EXPLAINS"
    if RUBRIC_THRESHOLDS["r2_weak_lower"] <= r2 < RUBRIC_THRESHOLDS["r2_explains"]:
        return "M3_WEAK"
    if any_significant and r2 < RUBRIC_THRESHOLDS["r2_weak_lower"]:
        # "hash-non-uniformity present but shape correction modest"
        return "M3_WEAK"
    return "M3_REFUTES"


def main(argv: list[str]) -> int:
    fit = json.loads((OUT_DIR / "hash_geometry_fit.json").read_text())
    unif = json.loads((OUT_DIR / "hash_uniformity_summary.json").read_text())

    r2 = float(fit["M3"]["R2_M3_mean"])

    per_rule_type_chi2 = []
    for batch, per_rt in unif["batches"].items():
        for rt, e in per_rt.items():
            per_rule_type_chi2.append(
                {
                    "batch": batch,
                    "rule_type": rt,
                    "chi2": e["chi2"],
                    "dof": e["dof"],
                    "p_value": e["p_value"],
                    "deviation_normalized": e["deviation_normalized"],
                    "K": e["K"],
                    "N_salts": e["N_salts"],
                }
            )
    significant = [
        (row["batch"], row["rule_type"], row["p_value"])
        for row in per_rule_type_chi2
        if row["p_value"] < RUBRIC_THRESHOLDS["p_value_threshold"]
    ]

    verdict = classify(r2, significant)

    result = {
        "verdict": verdict,
        "R2_M3": r2,
        "per_batch_r2": fit["M3"]["per_batch_r2"],
        "per_rule_type_chi2": per_rule_type_chi2,
        "significant_at_p_005": [
            {"batch": b, "rule_type": rt, "p_value": p}
            for (b, rt, p) in sorted(significant, key=lambda t: t[2])
        ],
        "rubric_thresholds": RUBRIC_THRESHOLDS,
        "rubric_definitions": {
            "M3_EXPLAINS": "R2 >= 0.6 AND at least one (rule_type, batch) with chi-squared p < 0.05",
            "M3_WEAK": "R2 in [0.3, 0.6) OR (any significant non-uniformity AND R2 < 0.3)",
            "M3_REFUTES": "R2 < 0.3 AND no significant hash-non-uniformity",
        },
        "verdict_reason": (
            f"R2(M3-corrected) mean = {r2:.4f}; "
            f"count of (rule_type, batch) cells with p < 0.05 = {len(significant)}; "
            "verdict follows the rubric above deterministically."
        ),
        "alpha_pinned": fit["M3"]["alpha_pinned"],
        "input_fit_path": "data/collision_model/hash_geometry_fit.json",
        "input_uniformity_path": "data/collision_model/hash_uniformity_summary.json",
        "run_stamp": "2026-08-28T22:55:00Z",
        "generator": "scripts/analysis/hash_geometry_verdict.py",
    }
    out = OUT_DIR / "hash_geometry_verdict.json"
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(f"[hash_geometry_verdict] wrote {out}")
    print(f"[hash_geometry_verdict] verdict = {verdict}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
