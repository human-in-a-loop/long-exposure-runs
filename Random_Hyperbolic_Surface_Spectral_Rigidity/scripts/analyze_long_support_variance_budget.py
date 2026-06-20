# created: 2026-05-16T16:35:00Z
# cycle: 31
# run_id: run-2026-05-15T153635Z
# agent: worker
# milestone: M20-long-support-trace-variance-requirement
"""Exponent budgets for long-support local-window trace variance."""

from __future__ import annotations

import csv
import math
import statistics
from pathlib import Path

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
OUT_CSV = ROOT / "data/extension_candidates/long_support_variance_budget.csv"
SUMMARY_CSV = ROOT / "data/extension_candidates/long_support_variance_summary.csv"
SAVING_FIG = ROOT / "reports/figures/m20_required_variance_saving.png"
MAP_FIG = ROOT / "reports/figures/m20_long_support_feasibility_map.png"

ALPHA_W = 0.006


def num_text(value: float) -> str:
    if math.isinf(value) or math.isnan(value):
        return str(value)
    if abs(value) < 1e-14:
        value = 0.0
    return f"{value:.12g}"


def support_requirement(regime: str, d: float) -> float:
    if d < 0:
        return math.inf
    if regime == "edge":
        return 0.5 * d
    return d


def mean_exponent(regime: str, d: float) -> float:
    if regime == "edge":
        return 1.0 - 1.5 * d
    return 1.0 - d


def endpoint_threshold(regime: str) -> float:
    return 2.0 * ALPHA_W / 3.0 if regime == "edge" else ALPHA_W


def q_exponent_from_support(eta: float, lambda0: float) -> float:
    """At exponent level, R <= C Lambda0^(-1/2) q gives q ~ R.

    Lambda0 is fixed on the n-exponent grid, so its square-root factor changes
    constants but not the n-power. The value is still recorded in the CSV.
    """
    if eta < 0 or lambda0 <= 0:
        return math.inf
    return eta


def loss_exponent(architecture: str, kappa: float, q_exponent: float) -> float:
    if architecture == "trace":
        return 2.0 * kappa * q_exponent
    if architecture == "pretrace":
        return 4.0 * kappa * q_exponent
    raise ValueError(f"unknown architecture: {architecture}")


def required_beta(regime: str, d: float, loss: float) -> float:
    return 1.0 + loss - 2.0 * mean_exponent(regime, d)


def chebyshev_passes(variance_exponent: float, mean_exp: float) -> bool:
    return variance_exponent < 2.0 * mean_exp


def feasibility_class(support_met: bool, beta_req: float, beats_endpoint: bool) -> str:
    if not support_met:
        return "impossible_by_support"
    if not beats_endpoint:
        return "outside_current_architecture"
    if beta_req <= 0:
        return "requires_no_extra_saving"
    if beta_req <= 1:
        return "requires_moderate_new_saving"
    return "requires_large_new_saving"


def build_rows() -> list[dict[str, str]]:
    d_grid = [0.0, 0.002, 0.004, 0.006, 0.008, 0.01, 0.02, 0.05, 0.1, 0.25, 0.5]
    eta_grid = [0.0, 0.002, 0.004, 0.006, 0.008, 0.01, 0.02, 0.05, 0.1, 0.25, 0.5]
    kappa_grid = [3.0, 5.0]
    lambda0_grid = [1.0, 4.0, 25.0]
    regimes = ["bulk", "edge", "high_energy"]
    architectures = ["trace", "pretrace"]
    rows: list[dict[str, str]] = []
    for regime in regimes:
        for d in d_grid:
            req_eta = support_requirement(regime, d)
            mu_exp = mean_exponent(regime, d)
            beats_endpoint = d > endpoint_threshold(regime)
            for eta in eta_grid:
                support_met = eta >= req_eta
                for kappa in kappa_grid:
                    for lambda0 in lambda0_grid:
                        q_exp = q_exponent_from_support(eta, lambda0)
                        for architecture in architectures:
                            loss = loss_exponent(architecture, kappa, q_exp)
                            beta_req = required_beta(regime, d, loss)
                            variance_at_beta_zero = 1.0 + loss
                            rows.append(
                                {
                                    "regime": regime,
                                    "architecture": architecture,
                                    "Delta_exponent_d": num_text(d),
                                    "eta": num_text(eta),
                                    "kappa": num_text(kappa),
                                    "Lambda0": num_text(lambda0),
                                    "support_requirement_eta_min": num_text(req_eta),
                                    "support_requirement_met": str(support_met).lower(),
                                    "q_exponent": num_text(q_exp),
                                    "loss_exponent": num_text(loss),
                                    "mean_exponent": num_text(mu_exp),
                                    "variance_exponent_beta_zero": num_text(variance_at_beta_zero),
                                    "required_beta": num_text(beta_req),
                                    "chebyshev_pass_beta_zero": str(chebyshev_passes(variance_at_beta_zero, mu_exp)).lower(),
                                    "beats_endpoint": str(beats_endpoint).lower(),
                                    "feasibility_class": feasibility_class(support_met, beta_req, beats_endpoint),
                                    "notes": "fixed Lambda0 exponent model: R <= C Lambda0^(-1/2) q implies q_exponent=eta",
                                }
                            )
    return rows


def build_summary(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    summary: list[dict[str, str]] = []
    keys = sorted({(r["regime"], r["architecture"], r["kappa"]) for r in rows})
    classes = [
        "impossible_by_support",
        "requires_no_extra_saving",
        "requires_moderate_new_saving",
        "requires_large_new_saving",
        "outside_current_architecture",
    ]
    for regime, architecture, kappa in keys:
        subset = [r for r in rows if (r["regime"], r["architecture"], r["kappa"]) == (regime, architecture, kappa)]
        endpoint = [r for r in subset if r["beats_endpoint"] == "true"]
        support_endpoint = [r for r in endpoint if r["support_requirement_met"] == "true"]
        reqs = [float(r["required_beta"]) for r in support_endpoint]
        row = {
            "regime": regime,
            "architecture": architecture,
            "kappa": kappa,
            "rows": str(len(subset)),
            "endpoint_beating_rows": str(len(endpoint)),
            "support_met_endpoint_rows": str(len(support_endpoint)),
            "min_required_beta_endpoint_support_met": num_text(min(reqs) if reqs else math.inf),
            "median_required_beta_endpoint_support_met": num_text(statistics.median(reqs) if reqs else math.inf),
        }
        for klass in classes:
            row[f"{klass}_rows"] = str(sum(1 for r in subset if r["feasibility_class"] == klass))
        summary.append(row)
    return summary


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def plot_required_saving(rows: list[dict[str, str]]) -> None:
    fig, ax = plt.subplots(figsize=(8.5, 5.2))
    styles = {
        ("bulk", "trace"): ("#4c78a8", "-"),
        ("bulk", "pretrace"): ("#4c78a8", "--"),
        ("edge", "trace"): ("#e45756", "-"),
        ("edge", "pretrace"): ("#e45756", "--"),
    }
    for (regime, architecture), (color, linestyle) in styles.items():
        subset = [
            r for r in rows
            if r["regime"] == regime
            and r["architecture"] == architecture
            and r["kappa"] == "5"
            and r["Lambda0"] == "4"
            and r["support_requirement_met"] == "true"
            and abs(float(r["eta"]) - float(r["support_requirement_eta_min"])) < 1e-12
        ]
        subset.sort(key=lambda r: float(r["Delta_exponent_d"]))
        ax.plot(
            [float(r["Delta_exponent_d"]) for r in subset],
            [float(r["required_beta"]) for r in subset],
            marker="o",
            color=color,
            linestyle=linestyle,
            label=f"{regime} {architecture}, eta=min",
        )
    ax.axhline(1.0, color="black", linewidth=1.0, linestyle=":", label="beta=1")
    ax.axvline(ALPHA_W, color="#666666", linewidth=1.0, linestyle="--", label="bulk endpoint d=alpha_W")
    ax.axvline(2.0 * ALPHA_W / 3.0, color="#999999", linewidth=1.0, linestyle="-.", label="edge endpoint")
    ax.set_xlabel("window exponent d where Delta = n^{-d}")
    ax.set_ylabel("required variance saving beta")
    ax.set_title("Long-support variance saving required at minimal resolving support")
    ax.grid(True, alpha=0.25)
    ax.legend(fontsize=8)
    fig.tight_layout()
    SAVING_FIG.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(SAVING_FIG, dpi=180)
    plt.close(fig)


def plot_feasibility_map(rows: list[dict[str, str]]) -> None:
    subset = [
        r for r in rows
        if r["regime"] == "bulk"
        and r["architecture"] == "trace"
        and r["kappa"] == "5"
        and r["Lambda0"] == "4"
    ]
    d_vals = sorted({float(r["Delta_exponent_d"]) for r in subset})
    eta_vals = sorted({float(r["eta"]) for r in subset})
    class_value = {
        "impossible_by_support": 0,
        "outside_current_architecture": 1,
        "requires_no_extra_saving": 2,
        "requires_moderate_new_saving": 3,
        "requires_large_new_saving": 4,
    }
    matrix = []
    for eta in eta_vals:
        row_vals = []
        for d in d_vals:
            match = next(r for r in subset if float(r["Delta_exponent_d"]) == d and float(r["eta"]) == eta)
            row_vals.append(class_value[match["feasibility_class"]])
        matrix.append(row_vals)
    fig, ax = plt.subplots(figsize=(8.2, 5.6))
    cmap = plt.matplotlib.colors.ListedColormap(["#d73027", "#d9d9d9", "#1a9850", "#fee08b", "#f46d43"])
    im = ax.imshow(matrix, origin="lower", aspect="auto", cmap=cmap, vmin=0, vmax=4)
    ax.set_xticks(range(len(d_vals)), [num_text(v) for v in d_vals], rotation=45, ha="right")
    ax.set_yticks(range(len(eta_vals)), [num_text(v) for v in eta_vals])
    ax.set_xlabel("window exponent d")
    ax.set_ylabel("support exponent eta")
    ax.set_title("Bulk trace feasibility map, kappa=5, fixed Lambda0=4")
    cbar = fig.colorbar(im, ax=ax, ticks=range(5))
    cbar.ax.set_yticklabels([
        "support impossible",
        "not endpoint-beating",
        "no extra saving",
        "moderate saving",
        "large saving",
    ])
    fig.tight_layout()
    MAP_FIG.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(MAP_FIG, dpi=180)
    plt.close(fig)


def main() -> None:
    rows = build_rows()
    summary = build_summary(rows)
    write_csv(OUT_CSV, rows)
    write_csv(SUMMARY_CSV, summary)
    plot_required_saving(rows)
    plot_feasibility_map(rows)
    print(f"wrote {len(rows)} rows to {OUT_CSV.relative_to(ROOT)}")
    print(f"wrote {len(summary)} rows to {SUMMARY_CSV.relative_to(ROOT)}")
    print(f"wrote {SAVING_FIG.relative_to(ROOT)}")
    print(f"wrote {MAP_FIG.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
