#!/usr/bin/env python3
# ---
# created: 2026-08-28T14:20:00Z
# cycle: 27
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-GEN-1/collision-model-shape-mechanism
# ---
"""Shape-mechanism fit engine.

Reuses cycle-26 BP-scaled predictions and applies two candidate
corrections to the per-rule_type shape residual:

  M1 (coercion-rate reshaping)
      For each rule_type in each batch, correction_factor =
      1 / (1 - coercion_rate) if coercion_rate < 1, else 1.
      Rationale (from cycle-26 handoff): coerced rules 'don't count'
      toward the naive BP per-rule_type distribution because their
      per-rule_type identity is masked at the collision-attribution
      step.  The corrected predicted count = predicted_scaled *
      correction_factor.  In this codebase coercion mutates parameters
      but NOT rule_ids, so this correction is expected to be near-
      identity — a first-class positive/negative finding either way.

  M2 (effective-K substitution)
      For each rule_type in each batch, K_eff replaces K_raw in the
      BP formula; alpha_hat is re-fit against the aggregate totals
      using the same closed-form LS.  Per-rule_type prediction under
      M2 = alpha_hat_M2 * N*(N-1) / (2 * K_eff_clipped) where
      K_eff_clipped = max(K_eff, 1) (documented degeneracy handling).

Both corrections are computed for every batch that carries observed
per-rule_type counts (batch_v2, batch_v3_i3, batch_v6).  Aggregate
per-rule_type R² values are the unweighted mean of per-batch shape
R² values.

Analytical / deterministic.  No PRNG.  No sidecar_nonfactor.
Does not import i4_stratified.
"""
from __future__ import annotations

import json
import pathlib
import sys

assert sys.executable == "/usr/bin/python3", (
    f"shape_mechanism_fit requires /usr/bin/python3, got {sys.executable}"
)

_HERE = pathlib.Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from collision_model_bp import (  # noqa: E402
    bp_pure_predict,
    fit_alpha_ls,
    r_squared,
)

RULE_TYPES = ("A", "F", "H", "M", "R")  # matches observations.json key style
RULE_TYPE_FULL = {
    "A": "arrangement", "F": "form", "H": "harmonic",
    "M": "melodic", "R": "rhythmic",
}


def _load_observations() -> list[dict]:
    p = pathlib.Path("data/collision_model/observations.json")
    return json.loads(p.read_text())


def _load_coercion_rates() -> dict:
    p = pathlib.Path("data/collision_model/coercion_rate_summary.json")
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _load_keff() -> dict:
    p = pathlib.Path("data/collision_model/effective_k_summary.json")
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _shape_r2(observed: list[float], predicted: list[float]) -> float | None:
    return r_squared(observed, predicted)


def _mean_or_none(vals: list[float | None]) -> float | None:
    finite = [v for v in vals if v is not None]
    if not finite:
        return None
    return sum(finite) / len(finite)


def fit_m1_correction(observations, coercion_summary):
    """Apply M1 correction: predicted_scaled_M1 = predicted_scaled / (1 - rate)."""
    # First fit alpha on aggregate totals (unconditioned batches only, matching
    # cycle-26 methodology).
    obs_totals = []
    pred_totals_pure = []
    for obs in observations:
        if obs["sampler"] == "stratified":
            continue
        K_full = {RULE_TYPE_FULL[k]: v for k, v in obs["K_by_rule_type"].items()}
        pred = bp_pure_predict(obs["N"], K_full)
        obs_totals.append(obs["observed_total"])
        pred_totals_pure.append(sum(pred.values()))

    alpha_hat = fit_alpha_ls(obs_totals, pred_totals_pure)
    if alpha_hat is None:
        alpha_hat = 1.0

    per_batch_shape = {}
    per_batch_r2 = {}
    for obs in observations:
        opr = obs.get("observed_per_rule_type")
        if not opr or obs["sampler"] == "stratified":
            continue
        batch_id = obs["batch_id"]
        crates_all = coercion_summary.get("batches", {}).get(batch_id, {})
        crates = crates_all.get("per_rule_type_coercion_rate", {})
        K_full = {RULE_TYPE_FULL[k]: v for k, v in obs["K_by_rule_type"].items()}
        pred_pure = bp_pure_predict(obs["N"], K_full)

        rts = list(opr.keys())
        obs_list = [float(opr[rt]) for rt in rts]
        pred_scaled_list = [alpha_hat * pred_pure[RULE_TYPE_FULL[rt]] for rt in rts]
        # M1 correction: inverse (1 - coercion_rate)
        pred_m1_list = []
        for rt in rts:
            rate = crates.get(RULE_TYPE_FULL[rt], 0.0)
            correction = 1.0 / (1.0 - rate) if rate < 1.0 else 1.0
            pred_m1_list.append(
                alpha_hat * pred_pure[RULE_TYPE_FULL[rt]] * correction
            )

        r2_scaled = _shape_r2(obs_list, pred_scaled_list)
        r2_m1 = _shape_r2(obs_list, pred_m1_list)
        per_batch_shape[batch_id] = {
            "rule_types": rts,
            "observed": obs_list,
            "predicted_scaled": pred_scaled_list,
            "predicted_m1_corrected": pred_m1_list,
            "coercion_rates_per_rule_type": {
                rt: crates.get(RULE_TYPE_FULL[rt], 0.0) for rt in rts
            },
        }
        per_batch_r2[batch_id] = {"r2_scaled": r2_scaled, "r2_m1": r2_m1}
    return {
        "alpha_hat": alpha_hat,
        "per_batch_shape": per_batch_shape,
        "per_batch_r2": per_batch_r2,
        "R2_scaled_mean": _mean_or_none([v["r2_scaled"] for v in per_batch_r2.values()]),
        "R2_M1_mean": _mean_or_none([v["r2_m1"] for v in per_batch_r2.values()]),
    }


def fit_m2_correction(observations, keff_summary):
    """Fit M2: substitute K_eff for K_raw; refit alpha on aggregate.

    K_eff_clipped = max(K_eff, 1) to keep BP formula bounded when K_eff=0
    (documented degeneracy: happens when every rule of a rule_type would be
    mutated by the coherence gate given the actual sampled other picks).
    """
    # Build K_eff dict per batch
    def keff_for(batch_id):
        b = keff_summary.get("batches", {}).get(batch_id, {})
        raw = {
            "A": b.get("K_eff_mean_per_rule_type", {}).get("arrangement"),
            "F": b.get("K_eff_mean_per_rule_type", {}).get("form"),
            "H": b.get("K_eff_mean_per_rule_type", {}).get("harmonic"),
            "M": b.get("K_eff_mean_per_rule_type", {}).get("melodic"),
            "R": b.get("K_eff_mean_per_rule_type", {}).get("rhythmic"),
        }
        return raw

    def bp_pred_from_keff(N, keff):
        out = {}
        if N < 2:
            for k in keff:
                out[k] = 0.0
            return out
        for k, v in keff.items():
            K = max(v if v is not None else 0.0, 1.0)
            out[k] = N * (N - 1) / (2.0 * K)
        return out

    # Refit alpha for M2 on aggregate totals (unconditioned only).
    obs_totals = []
    pred_totals_m2 = []
    for obs in observations:
        if obs["sampler"] == "stratified":
            continue
        keff = keff_for(obs["batch_id"])
        pred = bp_pred_from_keff(obs["N"], keff)
        obs_totals.append(obs["observed_total"])
        pred_totals_m2.append(sum(pred.values()))
    alpha_m2 = fit_alpha_ls(obs_totals, pred_totals_m2)
    if alpha_m2 is None:
        alpha_m2 = 1.0

    per_batch_shape = {}
    per_batch_r2 = {}
    for obs in observations:
        opr = obs.get("observed_per_rule_type")
        if not opr or obs["sampler"] == "stratified":
            continue
        batch_id = obs["batch_id"]
        keff = keff_for(batch_id)
        pred_pure = bp_pred_from_keff(obs["N"], keff)
        rts = list(opr.keys())
        obs_list = [float(opr[rt]) for rt in rts]
        pred_m2_list = [alpha_m2 * pred_pure[rt] for rt in rts]
        r2_m2 = _shape_r2(obs_list, pred_m2_list)
        per_batch_shape[batch_id] = {
            "rule_types": rts,
            "observed": obs_list,
            "predicted_m2_corrected": pred_m2_list,
            "K_eff_used": {rt: keff[rt] for rt in rts},
            "K_eff_clipped": {rt: max(keff[rt] or 0.0, 1.0) for rt in rts},
        }
        per_batch_r2[batch_id] = {"r2_m2": r2_m2}
    return {
        "alpha_hat_M2": alpha_m2,
        "per_batch_shape": per_batch_shape,
        "per_batch_r2": per_batch_r2,
        "R2_M2_mean": _mean_or_none([v["r2_m2"] for v in per_batch_r2.values()]),
    }


def run() -> dict:
    observations = _load_observations()
    coercion = _load_coercion_rates()
    keff = _load_keff()
    m1 = fit_m1_correction(observations, coercion)
    m2 = fit_m2_correction(observations, keff)
    return {
        "observations_source": "data/collision_model/observations.json",
        "coercion_source": "data/collision_model/coercion_rate_summary.json",
        "keff_source": "data/collision_model/effective_k_summary.json",
        "cycle_26_baseline_R2_shape_scaled_mean": _mean_or_none(
            [v["r2_scaled"] for v in m1["per_batch_r2"].values()]
        ),
        "M1": m1,
        "M2": m2,
        "R2_M1_mean": m1["R2_M1_mean"],
        "R2_M2_mean": m2["R2_M2_mean"],
        "methodology_note": (
            "Aggregate R² is the unweighted mean of per-batch shape R² "
            "across batches with observed_per_rule_type (batch_v2, "
            "batch_v3_i3, batch_v6). K_eff clipped to max(K_eff, 1.0) "
            "when zero to keep the BP formula bounded — this is a "
            "documented degeneracy handling, not an ad-hoc parameter."
        ),
    }


def _write_json(path: pathlib.Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as fh:
        json.dump(obj, fh, indent=2, sort_keys=True)
        fh.write("\n")


if __name__ == "__main__":  # pragma: no cover
    result = run()
    _write_json(pathlib.Path("data/collision_model/shape_mechanism_fit.json"), result)
    print(
        f"R2_M1_mean={result['R2_M1_mean']}  R2_M2_mean={result['R2_M2_mean']}  "
        f"cycle26_R2_shape_scaled_mean={result['cycle_26_baseline_R2_shape_scaled_mean']}"
    )
