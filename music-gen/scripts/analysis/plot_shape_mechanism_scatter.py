#!/usr/bin/env python3
# ---
# created: 2026-08-28T22:25:00Z
# cycle: 28
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-GEN-1/collision-model-hash-space-geometry
# ---
"""Backfill of the two cycle-27 scatter figures.

Reads cycle-27's `data/collision_model/shape_mechanism_fit.json`.
Emits two PNGs into `docs/figures/`:

  * shape_mechanism_M1_correction.png
  * shape_mechanism_M2_correction.png

Each figure has one panel per shape-informative batch (v2, v3_i3, v6).
Each panel overlays uncorrected BP-scaled predictions and mechanism-
corrected predictions against observed pair counts per rule_type.

Renders the catastrophic-worsening pattern honestly (per cycle-27's
NEITHER_EXPLAINS verdict); do not spin the visualization.

Interpreter-guarded /usr/bin/python3.  No PRNG.  No sidecar_nonfactor.
Does not import i4_stratified.
"""
from __future__ import annotations

import json
import pathlib
import sys

assert sys.executable == "/usr/bin/python3", (
    f"plot_shape_mechanism_scatter requires /usr/bin/python3, got {sys.executable}"
)

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[2]
FIT_PATH = ROOT / "data" / "collision_model" / "shape_mechanism_fit.json"
OBS_PATH = ROOT / "data" / "collision_model" / "observations.json"
FIG_DIR = ROOT / "docs" / "figures"

# Cycle-27 shape-informative batches.
BATCHES = ("batch_v2", "batch_v3_i3", "batch_v6")

# Rule-type single-letter -> full name mapping used by observations.json K_by_rule_type.
RT_MAP = {"H": "harmonic", "R": "rhythmic", "M": "melodic", "F": "form", "A": "arrangement"}


def _bp_scaled(alpha: float, N: int, K: int) -> float:
    if K <= 0:
        return 0.0
    return alpha * N * (N - 1) / (2.0 * K)


def _panel(
    ax, batch: str, mech: str, per_batch_shape: dict, obs: list, alpha_scaled: float
) -> None:
    entry = per_batch_shape[batch]
    rule_types = list(entry["rule_types"])
    observed = list(entry["observed"])
    # Compute BP-scaled (uncorrected) directly from cycle-26 alpha.
    row = next(o for o in obs if o["batch_id"] == batch)
    N = int(row["N"])
    K_by = row["K_by_rule_type"]
    scaled = [_bp_scaled(alpha_scaled, N, int(K_by[rt])) for rt in rule_types]
    if mech == "M1":
        corrected = list(entry["predicted_m1_corrected"])
        title_suffix = "M1 (coercion-rate correction)"
    else:
        corrected = list(entry["predicted_m2_corrected"])
        title_suffix = "M2 (K_eff substitution, alpha_hat_M2 refit)"

    xs = list(range(len(rule_types)))
    width = 0.28
    ax.bar([x - width for x in xs], observed, width, label="observed", color="#333333")
    ax.bar(xs, scaled, width, label="BP-scaled (uncorrected, alpha=0.7469)", color="#4477aa")
    ax.bar([x + width for x in xs], corrected, width, label=f"{mech}-corrected", color="#cc6677")
    ax.set_xticks(xs)
    ax.set_xticklabels(rule_types)
    ax.set_ylabel("collision pairs")
    ax.set_title(f"{batch} - {title_suffix}", fontsize=10)


def _plot(mech: str, out_path: pathlib.Path) -> None:
    fit = json.loads(FIT_PATH.read_text())
    obs = json.loads(OBS_PATH.read_text())
    per_batch_shape = fit[mech]["per_batch_shape"]
    # Use cycle-26 alpha_hat for the "uncorrected" BP-scaled baseline
    # (this is the alpha that produced cycle-26's R^2 = 0.9588 aggregate fit).
    alpha_scaled = float(fit["M1"]["alpha_hat"])  # 0.7469... — pinned across cycles

    n = len(BATCHES)
    fig, axes = plt.subplots(1, n, figsize=(5.0 * n, 4.5), squeeze=False)
    for ax, batch in zip(axes[0], BATCHES):
        _panel(ax, batch, mech, per_batch_shape, obs, alpha_scaled)
    axes[0][0].legend(loc="upper right", fontsize=8)
    r2_mean = fit[mech].get(f"R2_{mech}_mean")
    scaled_mean = fit["cycle_26_baseline_R2_shape_scaled_mean"]
    fig.suptitle(
        f"Shape-mechanism {mech} correction vs observed - R2({mech}) mean {r2_mean:.3f} "
        f"(cycle-26 baseline BP-scaled shape R2 mean {scaled_mean:.3f})",
        fontsize=11,
    )
    fig.tight_layout(rect=[0, 0, 1, 0.94])
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=110)
    plt.close(fig)
    print(f"[plot_shape_mechanism_scatter] wrote {out_path}")


def main(argv: list[str]) -> int:
    _plot("M1", FIG_DIR / "shape_mechanism_M1_correction.png")
    _plot("M2", FIG_DIR / "shape_mechanism_M2_correction.png")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
