#!/usr/bin/env python3
"""Birthday-paradox collision-generation model fit engine.

Analytical / deterministic.  No PRNG.  No sidecar_nonfactor.
Does not import i4_stratified.

Fits two variants against M-GEN-1 batch observations:

  BP-pure:   E[pairs, rule_type] = N*(N-1) / (2 * K_effective[rule_type])
             aggregated by summation across rule_types per batch.  No free
             parameter.

  BP-scaled: scaled by a global alpha fit via least-squares.

K_effective semantics
---------------------
For unconditioned SHA-256-tiebreak sampling, K_effective = raw K per
rule_type from the ledger.

For stratified rejection sampling (I4), K_effective is treated as
"infinite" (no within-rule-type repeat possible until N > K); we
implement this by predicting 0 pairs for those batches.  The stratified-
sampler prediction of 0 is a legitimate closed-form consequence of the
sampler's rejection loop, not an ad-hoc drop.  Observations for those
batches are still included in the fit residuals.

R^2 uses the standard definition 1 - SS_res / SS_tot; when all observed
values are equal (SS_tot == 0) the function returns None and the caller
must flag "R^2 undefined".
"""
from __future__ import annotations

import json
import pathlib
import sys
from typing import Iterable

assert sys.executable == "/usr/bin/python3", (
    f"collision_model_bp requires /usr/bin/python3, got {sys.executable}"
)


# ---------------------------------------------------------------------------
# Analytic predictions
# ---------------------------------------------------------------------------
def bp_pure_predict(N: int, K_by_rule_type: dict[str, int]) -> dict[str, float]:
    """Return per-rule_type expected pair count under raw-K BP.

    E[pairs, r] = N * (N - 1) / (2 * K_r).  If K_r <= 0 the pair count for
    that rule_type is 0 (nothing to draw from -> no pairs).
    """
    if N < 2:
        return {r: 0.0 for r in K_by_rule_type}
    out: dict[str, float] = {}
    for r, K in K_by_rule_type.items():
        if K <= 0:
            out[r] = 0.0
        else:
            out[r] = N * (N - 1) / (2.0 * K)
    return out


def bp_scaled_predict(
    N: int, K_by_rule_type: dict[str, int], alpha: float
) -> dict[str, float]:
    """Return per-rule_type expected pair count scaled by global alpha."""
    base = bp_pure_predict(N, K_by_rule_type)
    return {r: alpha * v for r, v in base.items()}


def predict_total_by_effective_K(
    N: int, K_by_rule_type: dict[str, int], sampler: str
) -> float:
    """Aggregate predicted pair count for a batch.

    sampler in {"unconditioned", "stratified"}.  Stratified sampler returns
    0.0 (K_effective = infinity for within-rule-type collisions).
    """
    if sampler == "stratified":
        return 0.0
    if sampler != "unconditioned":
        raise ValueError(f"unknown sampler: {sampler}")
    return float(sum(bp_pure_predict(N, K_by_rule_type).values()))


# ---------------------------------------------------------------------------
# R^2
# ---------------------------------------------------------------------------
def r_squared(observed: list[float], predicted: list[float]) -> float | None:
    """1 - SS_res / SS_tot on aggregate pair counts.  Returns None when
    SS_tot == 0 (all observed equal — R^2 undefined)."""
    if len(observed) != len(predicted):
        raise ValueError(
            f"r_squared: length mismatch observed={len(observed)} predicted={len(predicted)}"
        )
    if not observed:
        return None
    mean_obs = sum(observed) / len(observed)
    ss_tot = sum((o - mean_obs) ** 2 for o in observed)
    if ss_tot == 0.0:
        return None
    ss_res = sum((o - p) ** 2 for o, p in zip(observed, predicted))
    return 1.0 - (ss_res / ss_tot)


# ---------------------------------------------------------------------------
# alpha fit (closed-form scalar LS)
# ---------------------------------------------------------------------------
def fit_alpha_ls(observed: list[float], predicted_pure: list[float]) -> float | None:
    """Closed-form scalar least squares: alpha_hat = sum(o*p) / sum(p*p).

    Returns None if sum(p*p) == 0 (no signal to scale)."""
    denom = sum(p * p for p in predicted_pure)
    if denom == 0.0:
        return None
    num = sum(o * p for o, p in zip(observed, predicted_pure))
    return num / denom


# ---------------------------------------------------------------------------
# High-level driver
# ---------------------------------------------------------------------------
def fit_bp(observations: list[dict]) -> dict:
    """Run BP-pure and BP-scaled fits.

    Each observation dict must have keys:
      batch_id (str), N (int), K_by_rule_type (dict[str,int]),
      sampler (str: "unconditioned" or "stratified"),
      observed_total (int|float),
      observed_per_rule_type (dict[str,int]|None).

    Returns a nested dict with per-batch predictions, aggregate R^2 values
    for BP-pure and BP-scaled, alpha_hat, and per-rule_type shape fit for
    any batch that carried observed_per_rule_type.
    """
    per_batch = []
    for obs in observations:
        pred_total_pure = predict_total_by_effective_K(
            obs["N"], obs["K_by_rule_type"], obs["sampler"]
        )
        per_type_pure = (
            {r: 0.0 for r in obs["K_by_rule_type"]}
            if obs["sampler"] == "stratified"
            else bp_pure_predict(obs["N"], obs["K_by_rule_type"])
        )
        per_batch.append(
            {
                "batch_id": obs["batch_id"],
                "N": obs["N"],
                "sampler": obs["sampler"],
                "K_by_rule_type": dict(obs["K_by_rule_type"]),
                "observed_total": float(obs["observed_total"]),
                "predicted_total_pure": pred_total_pure,
                "per_type_pure": per_type_pure,
                "observed_per_rule_type": obs.get("observed_per_rule_type"),
            }
        )

    observed_totals = [b["observed_total"] for b in per_batch]
    predicted_totals_pure = [b["predicted_total_pure"] for b in per_batch]

    r2_pure = r_squared(observed_totals, predicted_totals_pure)
    alpha_hat = fit_alpha_ls(observed_totals, predicted_totals_pure)
    if alpha_hat is None:
        predicted_totals_scaled = [0.0 for _ in observed_totals]
    else:
        predicted_totals_scaled = [alpha_hat * p for p in predicted_totals_pure]
    r2_scaled = r_squared(observed_totals, predicted_totals_scaled)

    for b, p_scaled in zip(per_batch, predicted_totals_scaled):
        b["predicted_total_scaled"] = p_scaled

    # Shape fit (per-rule_type) for any batch that provided a breakdown
    shape_fits: dict[str, dict] = {}
    for b in per_batch:
        opr = b.get("observed_per_rule_type")
        if not opr:
            continue
        if b["sampler"] == "stratified":
            continue  # per-type shape prediction is 0 for stratified sampler
        rule_types = list(opr.keys())
        obs_list = [float(opr[r]) for r in rule_types]
        pred_pure_list = [b["per_type_pure"][r] for r in rule_types]
        if alpha_hat is None:
            pred_scaled_list = [0.0 for _ in pred_pure_list]
        else:
            pred_scaled_list = [alpha_hat * p for p in pred_pure_list]
        shape_fits[b["batch_id"]] = {
            "rule_types": rule_types,
            "observed": obs_list,
            "predicted_pure": pred_pure_list,
            "predicted_scaled": pred_scaled_list,
            "r2_shape_pure": r_squared(obs_list, pred_pure_list),
            "r2_shape_scaled": r_squared(obs_list, pred_scaled_list),
        }

    return {
        "alpha_hat": alpha_hat,
        "r2_pure": r2_pure,
        "r2_scaled": r2_scaled,
        "per_batch": per_batch,
        "shape_fits": shape_fits,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def _load_observations(path: pathlib.Path) -> list[dict]:
    with path.open("r") as fh:
        return json.load(fh)


def _write_json(path: pathlib.Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as fh:
        json.dump(obj, fh, indent=2, sort_keys=True)
        fh.write("\n")


if __name__ == "__main__":  # pragma: no cover
    if len(sys.argv) != 3:
        print(
            "usage: collision_model_bp.py <observations.json> <out_bp_fit_results.json>",
            file=sys.stderr,
        )
        sys.exit(2)
    obs = _load_observations(pathlib.Path(sys.argv[1]))
    result = fit_bp(obs)
    _write_json(pathlib.Path(sys.argv[2]), result)
    print(
        f"alpha_hat={result['alpha_hat']} r2_pure={result['r2_pure']} r2_scaled={result['r2_scaled']}"
    )
