# created: 2026-05-16T14:32:00Z
# cycle: 28
# run_id: run-2026-05-15T153635Z
# agent: worker
# milestone: M17-local-window-variance-input
"""Exponent-level requirements for localized spectral-window variance input."""

from __future__ import annotations

import csv
import math
from pathlib import Path

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
OUT_CSV = ROOT / "data/extension_candidates/local_window_variance_requirements.csv"
FIG = ROOT / "reports/figures/m17_variance_requirement_phase_diagram.png"

LAMBDA_EDGE = 0.25


def num_text(value: float) -> str:
    if math.isnan(value) or math.isinf(value):
        return str(value)
    if abs(value) < 1e-14:
        value = 0.0
    return f"{value:.12g}"


def spectral_density(lam: float) -> float:
    if lam < LAMBDA_EDGE:
        raise ValueError("lambda must be at least 1/4")
    if lam == LAMBDA_EDGE:
        return 0.0
    return 0.5 * math.tanh(math.pi * math.sqrt(lam - LAMBDA_EDGE))


def endpoint_threshold_exponent(regime: str, alpha_w: float) -> float:
    """Delta_global = n^{-returned exponent}, constants and lambda factors suppressed."""
    return 2.0 * alpha_w / 3.0 if regime == "edge" else alpha_w


def mean_mass_exponent(regime: str, delta_exponent: float) -> float:
    """Exponent of n in the deterministic mass n * local Weyl mass."""
    if regime == "edge":
        return 1.0 - 1.5 * delta_exponent
    return 1.0 - delta_exponent


def variance_exponent(model: str, delta_exponent: float, alpha_w: float) -> float:
    """Exponent of n in a hypothetical Var Z_n law for Delta=n^{-delta_exponent}."""
    if model == "poisson_global_V_n":
        return 1.0
    if model == "poisson_window_V_nDelta":
        return 1.0 - delta_exponent
    if model == "mild_gain_beta_0p25_theta_1":
        return 0.75 - delta_exponent
    if model == "strong_gain_beta_0p75_theta_1":
        return 0.25 - delta_exponent
    if model == "delta_squared_gain_beta_0p25_theta_2":
        return 0.75 - 2.0 * delta_exponent
    if model == "pessimistic_global_trace_proxy":
        return 2.0 - 2.0 * alpha_w
    raise ValueError(f"unknown variance model: {model}")


def chebyshev_passes(mean_exponent: float, var_exponent: float, margin: float = 1e-12) -> bool:
    """Return whether sqrt(Var)=o(mean) at exponent level."""
    return 0.5 * var_exponent < mean_exponent - margin


def beats_endpoint(delta_exponent: float, threshold_exponent: float, margin: float = 1e-12) -> bool:
    """Delta=n^{-delta_exponent} is below Delta_global=n^{-threshold_exponent}."""
    return delta_exponent > threshold_exponent + margin


def build_rows(alpha_w: float = 0.006, epsilon: float = 0.1, genus: int = 2) -> list[dict[str, str]]:
    regimes = [
        ("edge", 0.25),
        ("near_edge", 0.250001),
        ("moderate_bulk", 1.0),
        ("bulk", 4.0),
        ("high_energy", 25.0),
    ]
    delta_exponents = [0.0, 0.002, 0.004, 0.006, 0.008, 0.01, 0.02, 0.05, 0.1, 0.25, 0.5, 0.75]
    models = [
        "poisson_global_V_n",
        "poisson_window_V_nDelta",
        "mild_gain_beta_0p25_theta_1",
        "strong_gain_beta_0p75_theta_1",
        "delta_squared_gain_beta_0p25_theta_2",
        "pessimistic_global_trace_proxy",
    ]
    rows: list[dict[str, str]] = []
    for regime, lam in regimes:
        threshold = endpoint_threshold_exponent(regime, alpha_w)
        density = spectral_density(lam)
        for delta_exp in delta_exponents:
            mean_exp = mean_mass_exponent(regime, delta_exp)
            for model in models:
                var_exp = variance_exponent(model, delta_exp, alpha_w)
                pass_flag = chebyshev_passes(mean_exp, var_exp)
                beat_flag = beats_endpoint(delta_exp, threshold)
                rows.append(
                    {
                        "regime": regime,
                        "Lambda": num_text(lam),
                        "density_F_prime": num_text(density),
                        "Delta_exponent": num_text(delta_exp),
                        "mean_exponent": num_text(mean_exp),
                        "endpoint_threshold_exponent": num_text(threshold),
                        "variance_model": model,
                        "variance_exponent": num_text(var_exp),
                        "chebyshev_pass": str(pass_flag).lower(),
                        "beats_endpoint": str(beat_flag).lower(),
                        "useful_new_input": str(pass_flag and beat_flag).lower(),
                        "parameters": f"alpha_W={alpha_w}; epsilon={epsilon}; genus={genus}; constants suppressed",
                    }
                )
    return rows


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def plot_phase(rows: list[dict[str, str]]) -> None:
    selected = [row for row in rows if row["regime"] == "bulk"]
    models = []
    for row in selected:
        if row["variance_model"] not in models:
            models.append(row["variance_model"])
    delta_values = sorted({float(row["Delta_exponent"]) for row in selected})
    threshold = float(selected[0]["endpoint_threshold_exponent"])

    fig, ax = plt.subplots(figsize=(8.5, 5.2))
    required = [2.0 * mean_mass_exponent("bulk", d) for d in delta_values]
    ax.plot(delta_values, required, color="black", linewidth=2.0, label="required: Var exponent < 2 mean exponent")
    colors = ["#4c78a8", "#f58518", "#54a24b", "#e45756", "#72b7b2", "#b279a2"]
    for color, model in zip(colors, models):
        vals = [variance_exponent(model, d, alpha_w=0.006) for d in delta_values]
        ax.plot(delta_values, vals, marker="o", linewidth=1.4, color=color, label=model)
    ax.axvline(threshold, color="black", linestyle="--", linewidth=1.2, label="M16 endpoint threshold")
    ax.fill_between(delta_values, -1.0, required, color="#d8f0d2", alpha=0.35, label="Chebyshev pass region")
    ax.set_xlabel("window exponent d where Delta = n^{-d}")
    ax.set_ylabel("variance exponent v where Var Z_n ~ n^v")
    ax.set_title("Bulk smoothed-window variance requirements")
    ax.set_ylim(-0.4, 2.2)
    ax.grid(True, alpha=0.25)
    ax.legend(fontsize=7, loc="lower left")
    fig.tight_layout()
    FIG.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIG, dpi=180)
    plt.close(fig)


def main() -> None:
    rows = build_rows()
    write_csv(OUT_CSV, rows)
    plot_phase(rows)
    print(f"wrote {OUT_CSV.relative_to(ROOT)} ({len(rows)} rows)")
    print(f"wrote {FIG.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
