# created: 2026-05-16T15:08:00Z
# cycle: 29
# run_id: run-2026-05-15T153635Z
# agent: worker
# milestone: M18-test-function-localization-feasibility
"""Tradeoff model for local spectral windows versus Kim--Tao test functions."""

from __future__ import annotations

import csv
import math
from pathlib import Path

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
OUT_CSV = ROOT / "data/extension_candidates/test_function_localization_tradeoffs.csv"
SUMMARY_CSV = ROOT / "data/extension_candidates/test_function_localization_regime_summary.csv"
SUPPORT_FIG = ROOT / "reports/figures/m18_localization_support_vs_window.png"
FEASIBILITY_FIG = ROOT / "reports/figures/m18_markov_loss_feasibility_map.png"

LAMBDA_EDGE = 0.25


def num_text(value: float) -> str:
    if math.isinf(value) or math.isnan(value):
        return str(value)
    if abs(value) < 1e-14:
        value = 0.0
    return f"{value:.12g}"


def exact_delta_r(lam: float, delta: float) -> float:
    if lam < LAMBDA_EDGE or delta < 0:
        raise ValueError("lambda must be >= 1/4 and delta must be nonnegative")
    return math.sqrt(lam + delta - LAMBDA_EDGE) - math.sqrt(lam - LAMBDA_EDGE)


def bulk_delta_r_approx(lam: float, delta: float) -> float:
    r = math.sqrt(lam - LAMBDA_EDGE)
    if r <= 0:
        return math.inf
    return delta / (2.0 * r)


def classify_regime(lam: float, delta: float) -> str:
    gap = lam - LAMBDA_EDGE
    if gap <= 0 or gap <= delta:
        return "edge_or_transition"
    if lam >= 25.0:
        return "high_energy"
    return "bulk"


def r_required_exponent(model: str, d: float, lam: float, delta: float, log_constant: float = 1.0) -> float:
    """Return exponent a in R ~ n^a, suppressing constants and log factors."""
    if model == "compact_support_R_inverse_width":
        dr = exact_delta_r(lam, delta)
        if dr == 0:
            return math.inf
        if classify_regime(lam, delta) == "edge_or_transition":
            # The edge has delta_r = sqrt(Delta), hence inverse width n^(d/2).
            # For nearby transition rows, use the exact n=1e6 scale recorded in the table.
            return max(0.0, -math.log10(dr) / 6.0)
        return d
    if model == "logarithmic_support":
        return 0.0
    if model == "polynomial_q_loss_proxy":
        return r_required_exponent("compact_support_R_inverse_width", d, lam, delta)
    raise ValueError(f"unknown support model: {model}")


def loss_exponent(side: str, support_exponent: float, kappa: float = 5.0) -> float:
    if math.isinf(support_exponent):
        return math.inf
    if side == "trace_2kappa":
        return 2.0 * kappa * support_exponent
    if side == "pretrace_4kappa":
        return 4.0 * kappa * support_exponent
    raise ValueError(f"unknown side: {side}")


def m17_variance_budget_exponent(regime: str, d: float) -> float:
    """Largest variance exponent v allowed by sqrt(Var) << mean."""
    if regime == "edge_or_transition":
        return 2.0 - 3.0 * d
    return 2.0 - 2.0 * d


def endpoint_threshold_exponent(regime: str, alpha_w: float) -> float:
    return 2.0 * alpha_w / 3.0 if regime == "edge_or_transition" else alpha_w


def outcome(side: str, support_model: str, regime: str, d: float, support_exp: float, alpha_w: float, kappa: float) -> str:
    if support_model == "logarithmic_support":
        return "requires new random-cover variance estimate"
    if d <= endpoint_threshold_exponent(regime, alpha_w):
        return "compatible with existing architecture"
    budget = m17_variance_budget_exponent(regime, d)
    penalty = loss_exponent(side, support_exp, kappa)
    if penalty >= budget:
        return "blocked by support/interpolation growth"
    return "requires new test-function construction"


def build_rows(alpha_w: float = 0.006, alpha_r: float = 0.004, kappa: float = 5.0) -> list[dict[str, str]]:
    lambda_grid = [0.25, 0.250001, 1.0, 4.0, 25.0]
    d_grid = [0.0, 0.002, 0.004, 0.006, 0.008, 0.01, 0.02, 0.05, 0.1, 0.25, 0.5]
    support_models = [
        "compact_support_R_inverse_width",
        "logarithmic_support",
        "polynomial_q_loss_proxy",
    ]
    sides = ["trace_2kappa", "pretrace_4kappa"]
    rows: list[dict[str, str]] = []
    for lam in lambda_grid:
        for d in d_grid:
            delta = 1.0 if d == 0 else 10.0 ** (-6.0 * d)
            # The exponent tables use Delta=n^{-d}; n=10^6 gives concrete scale columns.
            dr_exact = exact_delta_r(lam, delta)
            dr_approx = bulk_delta_r_approx(lam, delta)
            approximation_ratio = dr_approx / dr_exact if math.isfinite(dr_approx) and dr_exact > 0 else math.inf
            regime = classify_regime(lam, delta)
            threshold = endpoint_threshold_exponent(regime, alpha_w)
            variance_budget = m17_variance_budget_exponent(regime, d)
            for support_model in support_models:
                support_exp = r_required_exponent(support_model, d, lam, delta)
                for side in sides:
                    penalty = loss_exponent(side, support_exp, kappa)
                    rows.append(
                        {
                            "Lambda": num_text(lam),
                            "Delta_exponent_d": num_text(d),
                            "Delta_at_n_1e6": num_text(delta),
                            "r_width_exact": num_text(dr_exact),
                            "r_width_bulk_approx": num_text(dr_approx),
                            "bulk_approx_over_exact": num_text(approximation_ratio),
                            "regime": regime,
                            "support_model": support_model,
                            "support_exponent_R_n_power": num_text(support_exp),
                            "paper_q_dependency": "supp((h o f_Lambda0)^vee) <= c0 Lambda0^(-1/2) q; polynomial degree is q",
                            "architecture_side": side,
                            "markov_loss_exponent_proxy": num_text(penalty),
                            "m17_allowed_variance_exponent": num_text(variance_budget),
                            "endpoint_threshold_exponent": num_text(threshold),
                            "beats_m16_endpoint": str(d > threshold).lower(),
                            "classification": outcome(side, support_model, regime, d, support_exp, alpha_w, kappa),
                            "parameters": f"alpha_W={alpha_w}; alpha_R={alpha_r}; kappa={kappa}; n_for_scale_columns=1e6",
                        }
                    )
    return rows


def build_summary(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    summary: list[dict[str, str]] = []
    keys = sorted({(r["regime"], r["support_model"], r["architecture_side"]) for r in rows})
    for regime, support_model, side in keys:
        subset = [r for r in rows if r["regime"] == regime and r["support_model"] == support_model and r["architecture_side"] == side]
        useful = [r for r in subset if r["beats_m16_endpoint"] == "true"]
        blocked = [r for r in useful if r["classification"] == "blocked by support/interpolation growth"]
        summary.append(
            {
                "regime": regime,
                "support_model": support_model,
                "architecture_side": side,
                "rows": str(len(subset)),
                "beats_endpoint_rows": str(len(useful)),
                "blocked_rows": str(len(blocked)),
                "dominant_classification": max(
                    {r["classification"] for r in subset},
                    key=lambda c: sum(1 for r in subset if r["classification"] == c),
                ),
            }
        )
    return summary


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def plot_support(rows: list[dict[str, str]]) -> None:
    fig, ax = plt.subplots(figsize=(8.5, 5.2))
    styles = {
        "edge_or_transition": ("#e45756", "edge/transition"),
        "bulk": ("#4c78a8", "bulk"),
        "high_energy": ("#54a24b", "high energy"),
    }
    for regime, (color, label) in styles.items():
        subset = [
            r for r in rows
            if r["regime"] == regime
            and r["support_model"] == "compact_support_R_inverse_width"
            and r["architecture_side"] == "trace_2kappa"
            and float(r["Lambda"]) in ({0.25, 1.0, 25.0} if regime != "edge_or_transition" else {0.25})
        ]
        if not subset:
            continue
        x = [float(r["Delta_exponent_d"]) for r in subset]
        y = [float(r["support_exponent_R_n_power"]) for r in subset]
        ax.plot(x, y, marker="o", color=color, label=label)
    ax.axvline(0.006, color="black", linestyle="--", linewidth=1.2, label="bulk M16 endpoint exponent")
    ax.set_xlabel("window exponent d where Delta = n^{-d}")
    ax.set_ylabel("required support exponent a where R ~ n^a")
    ax.set_title("Localization support scale forced by r-window resolution")
    ax.grid(True, alpha=0.25)
    ax.legend(fontsize=8)
    fig.tight_layout()
    SUPPORT_FIG.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(SUPPORT_FIG, dpi=180)
    plt.close(fig)


def plot_feasibility(rows: list[dict[str, str]]) -> None:
    subset = [
        r for r in rows
        if r["Lambda"] == "4"
        and r["support_model"] == "polynomial_q_loss_proxy"
        and r["regime"] == "bulk"
    ]
    d_values = sorted({float(r["Delta_exponent_d"]) for r in subset})
    fig, ax = plt.subplots(figsize=(8.5, 5.2))
    budget = [m17_variance_budget_exponent("bulk", d) for d in d_values]
    ax.plot(d_values, budget, color="black", linewidth=2, label="M17 allowed variance exponent")
    for side, color in [("trace_2kappa", "#4c78a8"), ("pretrace_4kappa", "#e45756")]:
        vals = [loss_exponent(side, d, kappa=5.0) for d in d_values]
        ax.plot(d_values, vals, marker="o", color=color, label=f"{side} proxy")
    ax.axvline(0.006, color="black", linestyle="--", linewidth=1.2, label="M16 endpoint threshold")
    ax.fill_between(d_values, 0, budget, color="#d8f0d2", alpha=0.35, label="variance budget region")
    ax.set_xlabel("window exponent d where Delta = n^{-d}")
    ax.set_ylabel("exponent proxy")
    ax.set_title("Kim--Tao-style Markov loss versus M17 variance budget")
    ax.set_ylim(0, max(2.2, max(loss_exponent("pretrace_4kappa", d, 5.0) for d in d_values) * 1.05))
    ax.grid(True, alpha=0.25)
    ax.legend(fontsize=8)
    fig.tight_layout()
    FEASIBILITY_FIG.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(FEASIBILITY_FIG, dpi=180)
    plt.close(fig)


def main() -> None:
    rows = build_rows()
    summary = build_summary(rows)
    write_csv(OUT_CSV, rows)
    write_csv(SUMMARY_CSV, summary)
    plot_support(rows)
    plot_feasibility(rows)
    print(f"wrote {OUT_CSV.relative_to(ROOT)} ({len(rows)} rows)")
    print(f"wrote {SUMMARY_CSV.relative_to(ROOT)} ({len(summary)} rows)")
    print(f"wrote {SUPPORT_FIG.relative_to(ROOT)}")
    print(f"wrote {FEASIBILITY_FIG.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
