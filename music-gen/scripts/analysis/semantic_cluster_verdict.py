#!/usr/bin/env python3
# ---
# created: 2026-08-29T00:50:00Z
# cycle: 30
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-GEN-1/collision-model-semantic-cluster-overlap
# ---
"""Apply the frozen 3-verdict rubric to
data/collision_model/semantic_cluster_fit.json.

Verdicts (locked in
docs/collision_model_semantic_cluster_overlap_rubric.md §6):

- M4_EXPLAINS: mean per-batch shape R² ≥ 0.60 AND aggregate
  total-count R² ≥ (0.9588 - 0.05) = 0.9088
- M4_WEAK: mean per-batch shape R² in [0, 0.60)
- M4_REFUTES: mean per-batch shape R² ≤ 0

Rubric SHA-256 recorded in output JSON.

Deterministic. No PRNG. Alpha not refit.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import sys

assert sys.executable == "/usr/bin/python3", sys.executable

ROOT = pathlib.Path(__file__).resolve().parents[2]
FIT_JSON = ROOT / "data" / "collision_model" / "semantic_cluster_fit.json"
RUBRIC_DOC = (ROOT / "docs"
              / "collision_model_semantic_cluster_overlap_rubric.md")
OUT_JSON = ROOT / "data" / "collision_model" / "semantic_cluster_verdict.json"

ALPHA_PINNED = 0.7469387071101908
CYCLE_26_AGGREGATE_R2 = 0.958818977481073
AGGREGATE_DEGRADATION_TOL = 0.05
R2_MIN_EXPLAINS = 0.60


def _dispatch(mean_r2_shape, aggregate_r2):
    if mean_r2_shape <= 0.0:
        return "M4_REFUTES", (
            f"mean per-batch shape R² M4 = {mean_r2_shape:.4f} ≤ 0. "
            "Semantic-cluster overlap does not explain the residual."
        )
    if (mean_r2_shape >= R2_MIN_EXPLAINS
            and aggregate_r2 >= (CYCLE_26_AGGREGATE_R2
                                 - AGGREGATE_DEGRADATION_TOL)):
        return "M4_EXPLAINS", (
            f"mean per-batch shape R² M4 = {mean_r2_shape:.4f} ≥ 0.60 AND "
            f"aggregate R² = {aggregate_r2:.4f} ≥ 0.9088."
        )
    if 0.0 < mean_r2_shape < R2_MIN_EXPLAINS:
        return "M4_WEAK", (
            f"mean per-batch shape R² M4 = {mean_r2_shape:.4f} ∈ "
            f"[0, 0.60). Partial explanation."
        )
    # Fallthrough: passed EXPLAINS shape threshold but aggregate
    # degraded — treat as WEAK per rubric spirit.
    return "M4_WEAK", (
        f"mean per-batch shape R² M4 = {mean_r2_shape:.4f} ≥ 0.60 but "
        f"aggregate R² = {aggregate_r2:.4f} < 0.9088 — degrades total "
        "counts more than 0.05 below cycle-26 anchor."
    )


def main():
    fit = json.loads(FIT_JSON.read_text())
    rubric_sha = hashlib.sha256(RUBRIC_DOC.read_bytes()).hexdigest()

    mean_r2 = fit["r2_shape_m4_mean"]
    agg_r2 = fit["aggregate_r2_m4_total_counts"]
    verdict, reason = _dispatch(mean_r2, agg_r2)

    baseline_per_batch = {
        "batch_v2": 0.09705609888773847,
        "batch_v3_i3": -0.2522824360406397,
        "batch_v6": -0.8689834729839461,
    }
    per_batch_delta = {}
    for bid, base in baseline_per_batch.items():
        m4 = fit["r2_shape_m4_per_batch"].get(bid)
        if m4 is not None:
            per_batch_delta[bid] = {
                "baseline_r2_shape_scaled": base,
                "m4_r2_shape": m4,
                "delta": m4 - base,
            }

    payload = {
        "generator": "scripts/analysis/semantic_cluster_verdict.py",
        "alpha_pinned": ALPHA_PINNED,
        "rubric_doc":
            "docs/collision_model_semantic_cluster_overlap_rubric.md",
        "rubric_hash": rubric_sha,
        "inputs": {
            "semantic_cluster_fit": "data/collision_model/semantic_cluster_fit.json",
            "semantic_cluster_thresholds":
                "data/collision_model/semantic_cluster_thresholds.json",
            "effective_k_semantic":
                "data/collision_model/effective_k_semantic.tsv",
            "semantic_equivalence_classes":
                "data/collision_model/semantic_equivalence_classes.tsv",
            "rule_structural_fingerprints":
                "data/collision_model/rule_structural_fingerprints.tsv",
        },
        "rubric_thresholds": {
            "r2_min_explains": R2_MIN_EXPLAINS,
            "aggregate_degradation_tolerance": AGGREGATE_DEGRADATION_TOL,
            "cycle_26_aggregate_r2_anchor": CYCLE_26_AGGREGATE_R2,
        },
        "rubric_definitions": {
            "M4_EXPLAINS":
                ("mean per-batch shape R² ≥ 0.60 AND aggregate "
                 "R² ≥ 0.9088"),
            "M4_WEAK": "mean per-batch shape R² ∈ [0, 0.60)",
            "M4_REFUTES": "mean per-batch shape R² ≤ 0",
        },
        "per_rule_type_r2_baseline_reference_batch_v6":
            -0.8689834729839461,
        "per_rule_type_r2_m4_corrected": fit["r2_shape_m4_per_batch"],
        "aggregate_r2_before": CYCLE_26_AGGREGATE_R2,
        "aggregate_r2_after": agg_r2,
        "per_batch_delta_baseline_vs_m4": per_batch_delta,
        "mean_per_batch_r2_shape_m4": mean_r2,
        "verdict": verdict,
        "verdict_reason": reason,
        "arc_close_triggered": (verdict == "M4_REFUTES"),
    }
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True))
    sha = hashlib.sha256(OUT_JSON.read_bytes()).hexdigest()
    print(f"WROTE {OUT_JSON.relative_to(ROOT)}")
    print(f"  VERDICT = {verdict}")
    print(f"  reason: {reason}")
    print(f"  rubric_sha = {rubric_sha[:16]}")
    print(f"sha256={sha[:16]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
