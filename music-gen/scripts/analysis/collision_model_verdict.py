#!/usr/bin/env python3
"""Apply the locked 4-verdict rubric to a bp_fit_results.json.

Rubric locked BEFORE analysis in
docs/collision_generation_model_birthday_paradox.md §2:

  CONFIRMS_BP_PURE   : R^2_pure >= 0.85
  CONFIRMS_BP_SCALED : R^2_pure < 0.85 AND R^2_scaled >= 0.85
                       AND alpha in [0.7, 1.5]
  PARTIAL_BP         : max(R^2_pure, R^2_scaled) in [0.60, 0.85)
  REFUTES_BP         : max(R^2_pure, R^2_scaled) < 0.60
                       (first-class positive finding)
  NOT_TESTABLE_ANCHOR_DRIFT : any of 8 anchors fails preservation check
                              (halt before verdict; handled externally)

Shape verdict (batch-v6 per-rule_type):
  SHAPE_CONFIRMS : shape R^2 >= 0.75
  SHAPE_PARTIAL  : 0.50 <= shape R^2 < 0.75
  SHAPE_REFUTES  : shape R^2 < 0.50

Interpreter-guarded /usr/bin/python3.  No PRNG.  No sidecar_nonfactor.
"""
from __future__ import annotations

import json
import pathlib
import sys

assert sys.executable == "/usr/bin/python3", (
    f"collision_model_verdict requires /usr/bin/python3, got {sys.executable}"
)

ALPHA_LO, ALPHA_HI = 0.7, 1.5
R2_CONFIRM = 0.85
R2_PARTIAL_LO = 0.60
SHAPE_CONFIRM = 0.75
SHAPE_PARTIAL_LO = 0.50


def classify_aggregate(r2_pure, r2_scaled, alpha_hat) -> tuple[str, str]:
    """Return (verdict, reason) tuple."""
    r2p = -1e30 if r2_pure is None else float(r2_pure)
    r2s = -1e30 if r2_scaled is None else float(r2_scaled)
    if r2p >= R2_CONFIRM:
        return (
            "CONFIRMS_BP_PURE",
            f"R^2_pure={r2p:.4f} >= {R2_CONFIRM} (no alpha needed)",
        )
    if (
        r2s >= R2_CONFIRM
        and alpha_hat is not None
        and ALPHA_LO <= float(alpha_hat) <= ALPHA_HI
    ):
        return (
            "CONFIRMS_BP_SCALED",
            f"R^2_pure={r2p:.4f} < {R2_CONFIRM}; R^2_scaled={r2s:.4f} >= {R2_CONFIRM}; alpha={alpha_hat:.4f} in [{ALPHA_LO},{ALPHA_HI}]",
        )
    best = max(r2p, r2s)
    if best >= R2_PARTIAL_LO:
        return (
            "PARTIAL_BP",
            f"max(R^2_pure={r2p:.4f}, R^2_scaled={r2s:.4f}) = {best:.4f} in [{R2_PARTIAL_LO},{R2_CONFIRM}); alpha={alpha_hat}",
        )
    return (
        "REFUTES_BP",
        f"max(R^2_pure={r2p:.4f}, R^2_scaled={r2s:.4f}) = {best:.4f} < {R2_PARTIAL_LO} (first-class positive finding)",
    )


def classify_shape(r2_shape) -> tuple[str, str]:
    if r2_shape is None:
        return ("SHAPE_UNDEFINED", "shape R^2 undefined (zero-variance observed)")
    r = float(r2_shape)
    if r >= SHAPE_CONFIRM:
        return ("SHAPE_CONFIRMS", f"shape R^2={r:.4f} >= {SHAPE_CONFIRM}")
    if r >= SHAPE_PARTIAL_LO:
        return ("SHAPE_PARTIAL", f"shape R^2={r:.4f} in [{SHAPE_PARTIAL_LO},{SHAPE_CONFIRM})")
    return ("SHAPE_REFUTES", f"shape R^2={r:.4f} < {SHAPE_PARTIAL_LO}")


def apply_verdict(fit: dict, shape_batch_id: str = "batch_v6") -> dict:
    verdict, reason = classify_aggregate(
        fit.get("r2_pure"), fit.get("r2_scaled"), fit.get("alpha_hat")
    )
    shape_fit = fit.get("shape_fits", {}).get(shape_batch_id)
    if shape_fit is None:
        shape_verdict, shape_reason = ("SHAPE_UNAVAILABLE", f"no shape fit for {shape_batch_id}")
        shape_r2 = None
    else:
        # Prefer scaled shape R^2 for verdict (matches aggregate-verdict variant that fits best)
        shape_r2 = shape_fit.get("r2_shape_scaled")
        shape_verdict, shape_reason = classify_shape(shape_r2)
    return {
        "verdict": verdict,
        "verdict_reason": reason,
        "shape_verdict": shape_verdict,
        "shape_reason": shape_reason,
        "shape_r2_used": shape_r2,
        "alpha_hat": fit.get("alpha_hat"),
        "r2_pure": fit.get("r2_pure"),
        "r2_scaled": fit.get("r2_scaled"),
        "rubric_thresholds": {
            "alpha_lo": ALPHA_LO,
            "alpha_hi": ALPHA_HI,
            "r2_confirm": R2_CONFIRM,
            "r2_partial_lo": R2_PARTIAL_LO,
            "shape_confirm": SHAPE_CONFIRM,
            "shape_partial_lo": SHAPE_PARTIAL_LO,
        },
    }


if __name__ == "__main__":  # pragma: no cover
    if len(sys.argv) != 3:
        print(
            "usage: collision_model_verdict.py <bp_fit_results.json> <out_verdict.json>",
            file=sys.stderr,
        )
        sys.exit(2)
    with open(sys.argv[1]) as fh:
        fit = json.load(fh)
    out = apply_verdict(fit)
    pathlib.Path(sys.argv[2]).parent.mkdir(parents=True, exist_ok=True)
    with open(sys.argv[2], "w") as fh:
        json.dump(out, fh, indent=2, sort_keys=True)
        fh.write("\n")
    print(f"verdict={out['verdict']}  shape={out['shape_verdict']}")
