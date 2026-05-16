# created: 2026-05-16T17:21:00Z
# cycle: 32
# run_id: run-2026-05-15T153635Z
# agent: worker
# milestone: M21-trace-side-long-support-variance-template
"""Trace-side fixed-energy long-support variance theorem-template budgets."""

from __future__ import annotations

import csv
import math
import statistics
from pathlib import Path

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
OUT_CSV = ROOT / "data/extension_candidates/trace_variance_template_budget.csv"
SUMMARY_CSV = ROOT / "data/extension_candidates/trace_variance_template_summary.csv"
THRESHOLD_FIG = ROOT / "reports/figures/m21_trace_template_beta_thresholds.png"
PLAUSIBILITY_FIG = ROOT / "reports/figures/m21_trace_template_plausibility_regions.png"


def num_text(value: float) -> str:
    if math.isinf(value) or math.isnan(value):
        return str(value)
    if abs(value) < 1e-14:
        value = 0.0
    return f"{value:.12g}"


def required_beta(kappa: float, d: float, eta: float) -> float:
    return 2.0 * kappa * eta + 2.0 * d - 1.0


def support_valid(d: float, eta: float) -> bool:
    return eta >= d


def endpoint_beating(d: float, alpha_w: float) -> bool:
    return d > alpha_w


def chebyshev_success(beta: float, beta_req: float) -> bool:
    return beta > beta_req


def beta_model_value(model: str, eta: float, c: float) -> float:
    if model == "no_new_saving":
        return 0.0
    if model == "constant":
        return c
    if model == "linear":
        return c * eta
    if model == "saturation":
        return min(c, 10.0 * eta)
    raise ValueError(f"unknown beta model: {model}")


def plausibility_class(endpoint: bool, support: bool, success: bool, beta_req: float) -> str:
    if not support:
        return "support_invalid"
    if not endpoint:
        return "not_endpoint_beating"
    if success:
        return "conditional_success"
    if beta_req <= 0.0:
        return "fails_strict_beta_despite_nonpositive_threshold"
    if beta_req <= 1.0:
        return "needs_moderate_saving"
    return "needs_large_saving"


def build_rows() -> list[dict[str, str]]:
    kappa_grid = [3.0, 5.0, 8.0]
    alpha_w_grid = [0.004, 0.006, 0.01]
    d_grid = [0.0, 0.002, 0.004, 0.006, 0.008, 0.01, 0.02, 0.05, 0.08, 0.1, 0.15, 0.25]
    eta_grid = [0.0, 0.002, 0.004, 0.006, 0.008, 0.01, 0.02, 0.05, 0.08, 0.1, 0.15, 0.25]
    beta_models = [
        ("no_new_saving", 0.0),
        ("constant", 0.25),
        ("constant", 0.75),
        ("constant", 1.25),
        ("linear", 4.0),
        ("linear", 8.0),
        ("linear", 12.0),
        ("saturation", 0.5),
        ("saturation", 1.0),
    ]

    rows: list[dict[str, str]] = []
    for kappa in kappa_grid:
        for alpha_w in alpha_w_grid:
            for d in d_grid:
                endpoint = endpoint_beating(d, alpha_w)
                for eta in eta_grid:
                    support = support_valid(d, eta)
                    beta_req = required_beta(kappa, d, eta)
                    variance_exponent_no_beta = 1.0 + 2.0 * kappa * eta
                    mean_exponent = 1.0 - d
                    for model, parameter in beta_models:
                        beta = beta_model_value(model, eta, parameter)
                        cheb = chebyshev_success(beta, beta_req)
                        local = endpoint and support and cheb
                        rows.append(
                            {
                                "regime": "fixed_bulk_trace",
                                "kappa": num_text(kappa),
                                "alpha_W": num_text(alpha_w),
                                "Delta_exponent_d": num_text(d),
                                "eta": num_text(eta),
                                "beta_model": model,
                                "beta_model_parameter": num_text(parameter),
                                "endpoint_beating": str(endpoint).lower(),
                                "support_valid": str(support).lower(),
                                "required_beta": num_text(beta_req),
                                "hypothetical_beta": num_text(beta),
                                "variance_exponent_no_beta": num_text(variance_exponent_no_beta),
                                "mean_exponent": num_text(mean_exponent),
                                "chebyshev_success": str(cheb).lower(),
                                "local_window_success": str(local).lower(),
                                "theorem_plausibility_class": plausibility_class(endpoint, support, cheb, beta_req),
                            }
                        )
    return rows


def build_summary(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    keys = sorted({(r["kappa"], r["alpha_W"], r["beta_model"], r["beta_model_parameter"]) for r in rows})
    classes = [
        "support_invalid",
        "not_endpoint_beating",
        "conditional_success",
        "fails_strict_beta_despite_nonpositive_threshold",
        "needs_moderate_saving",
        "needs_large_saving",
    ]
    summary: list[dict[str, str]] = []
    for key in keys:
        subset = [
            r for r in rows
            if (r["kappa"], r["alpha_W"], r["beta_model"], r["beta_model_parameter"]) == key
        ]
        endpoint_support = [
            r for r in subset
            if r["endpoint_beating"] == "true" and r["support_valid"] == "true"
        ]
        reqs = [float(r["required_beta"]) for r in endpoint_support]
        successes = [r for r in endpoint_support if r["local_window_success"] == "true"]
        row = {
            "kappa": key[0],
            "alpha_W": key[1],
            "beta_model": key[2],
            "beta_model_parameter": key[3],
            "rows": str(len(subset)),
            "endpoint_support_rows": str(len(endpoint_support)),
            "local_window_success_rows": str(len(successes)),
            "min_required_beta_endpoint_support": num_text(min(reqs) if reqs else math.inf),
            "median_required_beta_endpoint_support": num_text(statistics.median(reqs) if reqs else math.inf),
            "max_required_beta_endpoint_support": num_text(max(reqs) if reqs else math.inf),
        }
        for klass in classes:
            row[f"{klass}_rows"] = str(sum(1 for r in subset if r["theorem_plausibility_class"] == klass))
        summary.append(row)
    return summary


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def plot_thresholds() -> None:
    d_values = [i / 1000.0 for i in range(0, 251, 5)]
    eta_multipliers = [1.0, 1.5, 2.0]
    colors = ["#4c78a8", "#f58518", "#54a24b"]
    fig, ax = plt.subplots(figsize=(8.3, 5.2))
    for mult, color in zip(eta_multipliers, colors):
        values = [required_beta(5.0, d, mult * d) for d in d_values]
        ax.plot(d_values, values, color=color, label=f"eta={mult:g}d")
    ax.axhline(0.0, color="black", linewidth=1.0)
    ax.axhline(1.0, color="#666666", linewidth=1.0, linestyle=":")
    ax.axvline(0.006, color="#777777", linewidth=1.0, linestyle="--", label="alpha_W=0.006")
    ax.set_xlabel("window exponent d where Delta=n^{-d}")
    ax.set_ylabel("required beta: 2 kappa eta + 2d - 1")
    ax.set_title("Trace-side beta threshold for kappa=5")
    ax.grid(True, alpha=0.25)
    ax.legend(fontsize=9)
    fig.tight_layout()
    THRESHOLD_FIG.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(THRESHOLD_FIG, dpi=180)
    plt.close(fig)


def plot_plausibility(rows: list[dict[str, str]]) -> None:
    subset = [
        r for r in rows
        if r["kappa"] == "5"
        and r["alpha_W"] == "0.006"
        and r["beta_model"] == "linear"
        and r["beta_model_parameter"] == "8"
    ]
    d_vals = sorted({float(r["Delta_exponent_d"]) for r in subset})
    eta_vals = sorted({float(r["eta"]) for r in subset})
    class_to_value = {
        "support_invalid": 0,
        "not_endpoint_beating": 1,
        "conditional_success": 2,
        "fails_strict_beta_despite_nonpositive_threshold": 3,
        "needs_moderate_saving": 4,
        "needs_large_saving": 5,
    }
    grid = []
    for eta in eta_vals:
        row = []
        for d in d_vals:
            item = next(
                r for r in subset
                if abs(float(r["Delta_exponent_d"]) - d) < 1e-12 and abs(float(r["eta"]) - eta) < 1e-12
            )
            row.append(class_to_value[item["theorem_plausibility_class"]])
        grid.append(row)

    cmap = plt.matplotlib.colors.ListedColormap(["#d0d0d0", "#f2cf5b", "#4c78a8", "#b279a2", "#f58518", "#e45756"])
    fig, ax = plt.subplots(figsize=(8.4, 5.4))
    ax.imshow(grid, origin="lower", aspect="auto", cmap=cmap, vmin=-0.5, vmax=5.5)
    ax.set_xticks(range(len(d_vals)))
    ax.set_xticklabels([num_text(v) for v in d_vals], rotation=45, ha="right", fontsize=8)
    ax.set_yticks(range(len(eta_vals)))
    ax.set_yticklabels([num_text(v) for v in eta_vals], fontsize=8)
    ax.set_xlabel("window exponent d")
    ax.set_ylabel("support exponent eta")
    ax.set_title("Plausibility regions, linear beta=8 eta, kappa=5")
    labels = [
        ("support invalid", "#d0d0d0"),
        ("not endpoint-beating", "#f2cf5b"),
        ("conditional success", "#4c78a8"),
        ("strict beta fail", "#b279a2"),
        ("needs moderate saving", "#f58518"),
        ("needs large saving", "#e45756"),
    ]
    handles = [plt.Rectangle((0, 0), 1, 1, color=color) for _, color in labels]
    ax.legend(handles, [label for label, _ in labels], loc="upper left", bbox_to_anchor=(1.02, 1.0), fontsize=8)
    fig.tight_layout()
    PLAUSIBILITY_FIG.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(PLAUSIBILITY_FIG, dpi=180)
    plt.close(fig)


def main() -> None:
    rows = build_rows()
    summary = build_summary(rows)
    write_csv(OUT_CSV, rows)
    write_csv(SUMMARY_CSV, summary)
    plot_thresholds()
    plot_plausibility(rows)
    print(f"wrote {len(rows)} rows to {OUT_CSV}")
    print(f"wrote {len(summary)} rows to {SUMMARY_CSV}")
    print(f"wrote {THRESHOLD_FIG}")
    print(f"wrote {PLAUSIBILITY_FIG}")


if __name__ == "__main__":
    main()
