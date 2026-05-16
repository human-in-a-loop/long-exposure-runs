# created: 2026-05-16T20:15:00Z
# cycle: 39
# run_id: run-2026-05-15T153635Z
# agent: worker
# milestone: M28-theorem2-lp-mass-distribution-corollaries

"""Generate M28 Lp and mass-distribution consequence tables and figures."""

from __future__ import annotations

import csv
import math
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

DATA_DIR = Path("data/extension_candidates")
FIGURE_DIR = Path("reports/figures")
LP_GRID_PATH = DATA_DIR / "m28_lp_bound_grid.csv"
MASS_GRID_PATH = DATA_DIR / "m28_mass_distribution_grid.csv"
CLASSIFICATION_PATH = DATA_DIR / "m28_corollary_classification.csv"
LP_FIGURE = FIGURE_DIR / "m28_lp_decay_by_p.png"
MASS_FIGURE = FIGURE_DIR / "m28_mass_scale_phase_diagram.png"

EPSILON = 0.05
ALPHA_MODELS = [
    ("direct_theorem2_representative", "direct_lambda_3_over_2", 0.020, 1.5, "proved_shape_representative"),
    ("direct_small_alpha_stress", "direct_lambda_3_over_2", 0.006, 1.5, "proved_shape_representative"),
    ("remark_interpolation_representative", "remark_lambda_1_over_4_plus_eps", 0.012, 0.25 + EPSILON, "proved_shape_distinct_alpha"),
]
P_VALUES = [2, 3, 4, 6, 8, 12, 16, 32, math.inf]
N_VALUES = [10**3, 10**4, 10**5, 10**6, 10**7, 10**8]
LAMBDA_MODELS = [
    ("fixed_low_energy", 1.0, 0.0),
    ("bulk_fixed", 4.0, 0.0),
    ("mild_growth", None, 0.05),
    ("high_growth", None, 0.20),
]
SET_VOLUME_EXPONENTS = [-1.0, 0.0, 0.05, 0.10, 0.25, 0.50, 0.75, 1.0]
BRANCH_DECISION = "advance_theorem2_consequence_branch"


def interpolation_decay_exponent(alpha: float, p: float) -> float:
    if p == math.inf:
        return alpha
    if p < 2:
        raise ValueError("p must be at least 2")
    return alpha * (1.0 - 2.0 / p)


def lambda_value(model_value: float | None, lambda_growth: float, n: int) -> float:
    return float(model_value) if model_value is not None else n**lambda_growth


def sup_envelope(lambda_val: float, n: int, alpha: float, lambda_power: float) -> float:
    return lambda_val**lambda_power * n ** (-alpha)


def lp_bound(lambda_val: float, n: int, alpha: float, lambda_power: float, p: float) -> float:
    m = sup_envelope(lambda_val, n, alpha, lambda_power)
    if p == math.inf:
        return m
    return m ** (1.0 - 2.0 / p)


def effective_support_exponent(alpha: float, lambda_growth: float, lambda_power: float) -> float:
    return 2.0 * alpha - 2.0 * lambda_power * lambda_growth


def small_set_mass_envelope(alpha: float, lambda_growth: float, lambda_power: float, set_volume_exp: float) -> float:
    return set_volume_exp - 2.0 * alpha + 2.0 * lambda_power * lambda_growth


def classify_mass(envelope_exp: float, effective_support_exp: float, set_volume_exp: float) -> str:
    if envelope_exp < 0:
        return "nontrivial_mass_delocalization"
    if effective_support_exp <= 0.0 or set_volume_exp >= 1.0:
        return "bookkeeping_only"
    return "standard_interpolation"


def build_lp_rows() -> list[dict[str, float | str]]:
    rows: list[dict[str, float | str]] = []
    for n in N_VALUES:
        for alpha_label, lambda_model, alpha, lambda_power, alpha_kind in ALPHA_MODELS:
            for energy_label, lam_fixed, lambda_growth in LAMBDA_MODELS:
                lam = lambda_value(lam_fixed, lambda_growth, n)
                for p in P_VALUES:
                    p_label = "infinity" if p == math.inf else str(int(p))
                    decay = interpolation_decay_exponent(alpha, p)
                    value = lp_bound(lam, n, alpha, lambda_power, p)
                    rows.append(
                        {
                            "n": n,
                            "alpha_label": alpha_label,
                            "lambda_model": lambda_model,
                            "alpha_kind": alpha_kind,
                            "alpha": alpha,
                            "lambda_power": lambda_power,
                            "energy_label": energy_label,
                            "lambda_growth_exponent": lambda_growth,
                            "lambda": lam,
                            "p": p_label,
                            "n_decay_exponent_fixed_lambda": decay,
                            "lp_bound_unit_constant": value,
                            "classification": "standard_interpolation" if p != math.inf else "direct_theorem2_corollary",
                        }
                    )
    return rows


def build_mass_rows() -> list[dict[str, float | str]]:
    rows: list[dict[str, float | str]] = []
    for alpha_label, lambda_model, alpha, lambda_power, alpha_kind in ALPHA_MODELS:
        for energy_label, _lam_fixed, lambda_growth in LAMBDA_MODELS:
            eff_exp = effective_support_exponent(alpha, lambda_growth, lambda_power)
            for set_exp in SET_VOLUME_EXPONENTS:
                env_exp = small_set_mass_envelope(alpha, lambda_growth, lambda_power, set_exp)
                rows.append(
                    {
                        "alpha_label": alpha_label,
                        "lambda_model": lambda_model,
                        "alpha_kind": alpha_kind,
                        "alpha": alpha,
                        "lambda_power": lambda_power,
                        "energy_label": energy_label,
                        "lambda_growth_exponent": lambda_growth,
                        "set_volume_exponent_a": set_exp,
                        "small_set_mass_exponent": env_exp,
                        "small_set_bound_nontrivial": env_exp < 0,
                        "effective_support_exponent": eff_exp,
                        "support_fraction_exponent_vs_cover": eff_exp - 1.0,
                        "classification": classify_mass(env_exp, eff_exp, set_exp),
                    }
                )
    return rows


def build_classification(lp_rows: list[dict[str, float | str]], mass_rows: list[dict[str, float | str]]) -> list[dict[str, float | str]]:
    nontrivial = sum(1 for row in mass_rows if row["small_set_bound_nontrivial"] is True)
    high_energy_erased = sum(1 for row in mass_rows if float(row["effective_support_exponent"]) <= 0.0)
    return [
        {
            "item": "theorem2_sup_norm_input",
            "classification": "direct_theorem2_corollary",
            "evidence": "Theorem 2 and Remark 1.1 provide the two amplitude envelopes.",
            "decision": "",
        },
        {
            "item": "lp_interpolation",
            "classification": "standard_interpolation",
            "evidence": f"generated {len(lp_rows)} Lp grid rows with exact p=2 and p=infinity endpoints",
            "decision": "",
        },
        {
            "item": "small_set_mass",
            "classification": "nontrivial_mass_delocalization",
            "evidence": f"{nontrivial} grid rows have M^2 vol(A)<1",
            "decision": "",
        },
        {
            "item": "high_energy_limitations",
            "classification": "bookkeeping_only",
            "evidence": f"{high_energy_erased} rows have nonpositive effective-support exponent due to Lambda growth",
            "decision": "",
        },
        {
            "item": "qe_or_equidistribution",
            "classification": "unsupported_stronger_claim",
            "evidence": "Sup-norm control alone gives upper mass bounds on sets, not lower mass in specified regions.",
            "decision": "",
        },
        {
            "item": "branch_decision",
            "classification": "nontrivial_mass_delocalization",
            "evidence": "Fixed-energy Theorem 2 excludes unit-mass concentration below polynomial volume n^(2 alpha).",
            "decision": BRANCH_DECISION,
        },
    ]


def write_csv(path: Path, rows: list[dict[str, float | str | bool]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def plot_lp_decay() -> None:
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    finite_p = np.linspace(2.0, 32.0, 250)
    fig, ax = plt.subplots(figsize=(8, 5))
    for alpha_label, _lambda_model, alpha, _lambda_power, _alpha_kind in ALPHA_MODELS:
        y = [interpolation_decay_exponent(alpha, float(p)) for p in finite_p]
        ax.plot(finite_p, y, label=f"{alpha_label} alpha={alpha:g}")
        ax.scatter([32.8], [alpha], s=26)
    ax.set_xlabel("p")
    ax.set_ylabel("fixed-Lambda n-decay exponent")
    ax.set_title("Theorem 2 Lp interpolation decay")
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(LP_FIGURE, dpi=180)
    plt.close(fig)


def plot_mass_phase() -> None:
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    alpha_grid = np.linspace(0.0, 0.08, 161)
    set_grid = np.linspace(0.0, 1.0, 161)
    aa, ss = np.meshgrid(alpha_grid, set_grid)
    z = ss - 2.0 * aa
    fig, ax = plt.subplots(figsize=(7.5, 5))
    mesh = ax.contourf(alpha_grid, set_grid, z < 0.0, levels=[-0.5, 0.5, 1.5], colors=["#d8dde6", "#2d7f72"], alpha=0.85)
    ax.plot(alpha_grid, 2.0 * alpha_grid, color="black", linewidth=1.5, label="a = 2 alpha threshold")
    ax.set_xlabel("Theorem 2 alpha")
    ax.set_ylabel("set-volume exponent a in vol(A) ~ n^a")
    ax.set_title("Small-set mass bound is nontrivial below a = 2 alpha")
    ax.set_ylim(0.0, 0.18)
    ax.grid(True, alpha=0.25)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(MASS_FIGURE, dpi=180)
    plt.close(fig)


def main() -> None:
    lp_rows = build_lp_rows()
    mass_rows = build_mass_rows()
    classification = build_classification(lp_rows, mass_rows)
    write_csv(LP_GRID_PATH, lp_rows)
    write_csv(MASS_GRID_PATH, mass_rows)
    write_csv(CLASSIFICATION_PATH, classification)
    plot_lp_decay()
    plot_mass_phase()
    print(f"wrote {LP_GRID_PATH} ({len(lp_rows)} rows)")
    print(f"wrote {MASS_GRID_PATH} ({len(mass_rows)} rows)")
    print(f"wrote {CLASSIFICATION_PATH} ({len(classification)} rows)")
    print(f"wrote {LP_FIGURE}")
    print(f"wrote {MASS_FIGURE}")
    print(f"decision={BRANCH_DECISION}")


if __name__ == "__main__":
    main()
