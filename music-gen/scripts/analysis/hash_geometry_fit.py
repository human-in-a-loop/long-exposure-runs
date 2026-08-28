#!/usr/bin/env python3
# ---
# created: 2026-08-28T22:50:00Z
# cycle: 28
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-GEN-1/collision-model-hash-space-geometry
# ---
"""Hash-space-geometry fit (Mechanism M3).

Reuses cycle-26's BP formula.  Substitutes K -> K_eff_hash_clipped per
rule_type per batch (produced by effective_k_hash.py).  ALPHA IS PINNED
at cycle-26's alpha_hat = 0.7469387071101908 (not refit) -- this branch
tests a CORRECTION to K under fixed alpha, not a new joint fit.

Per-batch shape R^2 is computed on the three shape-informative batches
(batch_v2, batch_v3_i3, batch_v6), matching cycle-27's methodology.
The mean of per-batch shape R^2 is the headline "R2(M3-corrected)"
value the frozen 3-verdict rubric fires on.

Emits data/collision_model/hash_geometry_fit.json.

Analytical / deterministic.  No PRNG.  No sidecar_nonfactor.
Does not import i4_stratified.
"""
from __future__ import annotations

import json
import pathlib
import sys

assert sys.executable == "/usr/bin/python3", (
    f"hash_geometry_fit requires /usr/bin/python3, got {sys.executable}"
)

_HERE = pathlib.Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from collision_model_bp import r_squared  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "data" / "collision_model"

# alpha pinned at cycle-26 -- test-asserted.
ALPHA_PINNED = 0.7469387071101908

RULE_TYPES_FULL = ("harmonic", "rhythmic", "melodic", "form", "arrangement")
RT_SHORT = {"harmonic": "H", "rhythmic": "R", "melodic": "M", "form": "F", "arrangement": "A"}
SHORT_ORDER = ("H", "R", "M", "F", "A")  # cycle-27's per_batch_shape order

SHAPE_BATCHES = ("batch_v2", "batch_v3_i3", "batch_v6")


def _bp(N: int, K: float, alpha: float) -> float:
    if K <= 0:
        return 0.0
    return alpha * N * (N - 1) / (2.0 * K)


def _load_keff_hash() -> dict[str, dict[str, float]]:
    """Return {batch_id: {rule_type_full: K_eff_clipped}}."""
    path = OUT_DIR / "effective_k_hash.tsv"
    out: dict[str, dict[str, float]] = {}
    lines = path.read_text().strip().splitlines()
    header = lines[0].split("\t")
    idx = {h: i for i, h in enumerate(header)}
    for ln in lines[1:]:
        f = ln.split("\t")
        b = f[idx["batch_id"]]
        rt = f[idx["rule_type"]]
        keff = float(f[idx["K_eff_hash_clipped"]])
        out.setdefault(b, {})[rt] = keff
    return out


def main(argv: list[str]) -> int:
    obs_list = json.loads((OUT_DIR / "observations.json").read_text())
    obs_by = {o["batch_id"]: o for o in obs_list}
    keff_hash = _load_keff_hash()

    per_batch = {}
    per_batch_r2 = {}
    for batch in SHAPE_BATCHES:
        row = obs_by[batch]
        N = int(row["N"])
        observed_short = row["observed_per_rule_type"]  # {"H":.., ...}
        observed = [float(observed_short[s]) for s in SHORT_ORDER]
        keff_by_rt = keff_hash[batch]
        predicted = [
            _bp(N, keff_by_rt[full], ALPHA_PINNED)
            for full in (
                "harmonic",
                "rhythmic",
                "melodic",
                "form",
                "arrangement",
            )
        ]
        r2 = r_squared(observed, predicted)
        per_batch[batch] = {
            "rule_types": list(SHORT_ORDER),
            "observed": observed,
            "predicted_m3_corrected": predicted,
            "K_eff_hash_clipped": [
                keff_by_rt["harmonic"],
                keff_by_rt["rhythmic"],
                keff_by_rt["melodic"],
                keff_by_rt["form"],
                keff_by_rt["arrangement"],
            ],
            "N": N,
        }
        per_batch_r2[batch] = r2

    # Mean of per-batch shape R^2 (skip None from all-equal observed).
    valid = [v for v in per_batch_r2.values() if v is not None]
    R2_M3_mean = (sum(valid) / len(valid)) if valid else None

    fit = {
        "M3": {
            "alpha_pinned": ALPHA_PINNED,
            "per_batch_r2": per_batch_r2,
            "R2_M3_mean": R2_M3_mean,
            "per_batch_shape": per_batch,
        },
        "cycle_26_baseline_R2_shape_scaled_mean": -0.34140327004561577,
        "cycle_27_baseline_R2_M1_mean": -6.272900969942068,
        "cycle_27_baseline_R2_M2_mean": -10.694541781993612,
        "keff_source": "data/collision_model/effective_k_hash.tsv",
        "hash_uniformity_source": "data/collision_model/hash_uniformity_summary.json",
        "observations_source": "data/collision_model/observations.json",
        "methodology_note": (
            "R^2 computed with alpha pinned at cycle-26's alpha_hat "
            "(0.7469387071101908) and K replaced by K_eff_hash_clipped = "
            "max(K*(1 - min(1, chi2/(N*(K-1)))), 1). ALPHA IS NOT REFIT. "
            "Per-batch shape R^2 computed on the three shape-informative "
            "batches (batch_v2, batch_v3_i3, batch_v6); mean is unweighted. "
            "See docs/collision_model_hash_space_geometry.md for the frozen "
            "3-verdict rubric that fires on R2_M3_mean and per-rule_type "
            "chi-squared p-values."
        ),
    }

    out = OUT_DIR / "hash_geometry_fit.json"
    out.write_text(json.dumps(fit, indent=2, sort_keys=True) + "\n")
    print(f"[hash_geometry_fit] wrote {out}")
    print(f"[hash_geometry_fit] R2(M3-corrected) mean = {R2_M3_mean}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
