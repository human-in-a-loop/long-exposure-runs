# created: 2026-05-16T17:52:00Z
# cycle: 33
# run_id: run-2026-05-15T153635Z
# agent: worker
# milestone: M22-trace-corollary34-uniform-coefficient-variation-target

from __future__ import annotations

import csv
import math
import os
from dataclasses import dataclass
from pathlib import Path
from statistics import median

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
BUDGET_CSV = ROOT / "data/extension_candidates/corollary34_target_budget.csv"
SUMMARY_CSV = ROOT / "data/extension_candidates/corollary34_target_summary.csv"
SUCCESS_FIG = ROOT / "reports/figures/m22_corollary34_target_success_regions.png"
REQUIRED_FIG = ROOT / "reports/figures/m22_required_numerator_saving.png"


@dataclass(frozen=True)
class Target:
    target_type: str
    label: str
    a_offset: float
    sigma: float
    omega: float = 0.0

    def effective_a(self, kappa: float) -> float:
        return 2.0 * kappa - self.a_offset + self.omega


TARGETS = [
    Target("markov_baseline", "baseline A=2k", 0.0, 0.0),
    Target("coefficient_variation", "CV A=2k-2", 2.0, 0.0),
    Target("coefficient_variation", "CV A=2k-4", 4.0, 0.0),
    Target("direct_small_x", "direct sigma=0.25", 0.0, 0.25),
    Target("direct_small_x", "direct sigma=0.75", 0.0, 0.75),
    Target("direct_small_x", "direct A=2k-2 sigma=0.25", 2.0, 0.25),
    Target("stratified_weighted", "stratified A=2k-4 W=q", 4.0, 0.0, 1.0),
    Target("stratified_weighted", "stratified A=2k-4 W=q^-1", 4.0, 0.0, -1.0),
]


def required_beta(kappa: float, d: float, eta: float) -> float:
    return 2.0 * kappa * eta + 2.0 * d - 1.0


def support_valid(d: float, eta: float) -> bool:
    return eta >= d


def endpoint_beating(d: float, alpha_w: float) -> bool:
    return d > alpha_w


def candidate_beta(kappa: float, eta: float, target: Target) -> float:
    return (2.0 * kappa - target.effective_a(kappa)) * eta + target.sigma


def local_window_success(beta: float, beta_req: float, support: bool, endpoint: bool) -> bool:
    return support and endpoint and beta > beta_req


def failure_reason(success: bool, support: bool, endpoint: bool, beta: float, beta_req: float) -> str:
    if success:
        return "conditional_success"
    if not support:
        return "support_invalid"
    if not endpoint:
        return "not_endpoint_beating"
    if beta_req <= 0.0 and beta <= beta_req:
        return "strict_inequality_failure_despite_nonpositive_requirement"
    return "needs_more_numerator_saving"


def build_rows() -> list[dict[str, object]]:
    kappa_grid = [3.0, 5.0, 8.0]
    alpha_w_grid = [0.004, 0.006, 0.01]
    d_grid = [0.0, 0.002, 0.004, 0.006, 0.008, 0.01, 0.02, 0.05, 0.08, 0.1, 0.15, 0.25]
    eta_grid = [0.0, 0.002, 0.004, 0.006, 0.008, 0.01, 0.02, 0.05, 0.08, 0.1, 0.15, 0.25]
    rows: list[dict[str, object]] = []
    for kappa in kappa_grid:
        for alpha_w in alpha_w_grid:
            for d in d_grid:
                for eta in eta_grid:
                    beta_req = required_beta(kappa, d, eta)
                    support = support_valid(d, eta)
                    endpoint = endpoint_beating(d, alpha_w)
                    for target in TARGETS:
                        beta = candidate_beta(kappa, eta, target)
                        success = local_window_success(beta, beta_req, support, endpoint)
                        eff_a = target.effective_a(kappa)
                        rows.append(
                            {
                                "kappa": kappa,
                                "alpha_W": alpha_w,
                                "Delta_exponent_d": d,
                                "eta": eta,
                                "target_type": target.target_type,
                                "target_label": target.label,
                                "effective_A": eff_a,
                                "sigma": target.sigma,
                                "omega": target.omega,
                                "support_valid": support,
                                "endpoint_beating": endpoint,
                                "required_beta": beta_req,
                                "candidate_beta": beta,
                                "variance_exponent_candidate": 1.0 + eff_a * eta - target.sigma,
                                "variance_exponent_baseline": 1.0 + 2.0 * kappa * eta,
                                "mean_square_threshold_exponent": 2.0 - 2.0 * d,
                                "local_window_success": success,
                                "failure_reason": failure_reason(success, support, endpoint, beta, beta_req),
                            }
                        )
    return rows


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def summarize(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    groups: dict[tuple[float, float, str, str], list[dict[str, object]]] = {}
    for row in rows:
        key = (float(row["kappa"]), float(row["alpha_W"]), str(row["target_type"]), str(row["target_label"]))
        groups.setdefault(key, []).append(row)
    summary: list[dict[str, object]] = []
    for (kappa, alpha_w, target_type, label), group in sorted(groups.items()):
        endpoint_support = [r for r in group if r["endpoint_beating"] == True and r["support_valid"] == True]
        reqs = [float(r["required_beta"]) for r in endpoint_support]
        success_rows = sum(1 for r in group if r["local_window_success"] == True)
        summary.append(
            {
                "kappa": kappa,
                "alpha_W": alpha_w,
                "target_type": target_type,
                "target_label": label,
                "rows": len(group),
                "endpoint_support_rows": len(endpoint_support),
                "local_window_success_rows": success_rows,
                "min_required_beta_endpoint_support": min(reqs) if reqs else math.nan,
                "median_required_beta_endpoint_support": median(reqs) if reqs else math.nan,
                "max_required_beta_endpoint_support": max(reqs) if reqs else math.nan,
                "support_invalid_rows": sum(1 for r in group if r["failure_reason"] == "support_invalid"),
                "not_endpoint_beating_rows": sum(1 for r in group if r["failure_reason"] == "not_endpoint_beating"),
                "conditional_success_rows": sum(1 for r in group if r["failure_reason"] == "conditional_success"),
                "needs_more_numerator_saving_rows": sum(1 for r in group if r["failure_reason"] == "needs_more_numerator_saving"),
            }
        )
    return summary


def plot_required(rows: list[dict[str, object]]) -> None:
    sample = [
        r
        for r in rows
        if r["kappa"] == 5.0
        and r["alpha_W"] == 0.006
        and r["target_label"] == "baseline A=2k"
        and r["support_valid"] == True
    ]
    ds = sorted({float(r["Delta_exponent_d"]) for r in sample})
    etas = sorted({float(r["eta"]) for r in sample})
    grid = [[math.nan for _ in etas] for _ in ds]
    for r in sample:
        i = ds.index(float(r["Delta_exponent_d"]))
        j = etas.index(float(r["eta"]))
        grid[i][j] = float(r["required_beta"])

    REQUIRED_FIG.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(7.2, 5.0))
    im = ax.imshow(grid, origin="lower", aspect="auto", cmap="viridis", extent=[min(etas), max(etas), min(ds), max(ds)])
    ax.set_title("Required numerator saving beyond trace baseline")
    ax.set_xlabel("support exponent eta")
    ax.set_ylabel("window exponent d")
    fig.colorbar(im, ax=ax, label="required beta")
    fig.tight_layout()
    fig.savefig(REQUIRED_FIG, dpi=160)
    plt.close(fig)


def plot_success(rows: list[dict[str, object]]) -> None:
    labels = ["baseline A=2k", "direct sigma=0.75", "CV A=2k-4", "stratified A=2k-4 W=q^-1"]
    sample = [
        r
        for r in rows
        if r["kappa"] == 5.0
        and r["alpha_W"] == 0.006
        and r["target_label"] in labels
        and r["support_valid"] == True
    ]
    ds = sorted({float(r["Delta_exponent_d"]) for r in sample})
    etas = sorted({float(r["eta"]) for r in sample})
    SUCCESS_FIG.parent.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(2, 2, figsize=(9.0, 7.0), sharex=True, sharey=True)
    for ax, label in zip(axes.ravel(), labels):
        grid = [[0.0 for _ in etas] for _ in ds]
        for r in sample:
            if r["target_label"] != label:
                continue
            i = ds.index(float(r["Delta_exponent_d"]))
            j = etas.index(float(r["eta"]))
            if r["failure_reason"] == "not_endpoint_beating":
                grid[i][j] = 0.25
            elif r["local_window_success"] == True:
                grid[i][j] = 1.0
            else:
                grid[i][j] = 0.55
        ax.imshow(grid, origin="lower", aspect="auto", cmap="RdYlGn", vmin=0.0, vmax=1.0, extent=[min(etas), max(etas), min(ds), max(ds)])
        ax.set_title(label)
        ax.set_xlabel("eta")
        ax.set_ylabel("d")
    fig.suptitle("M22 conditional success regions")
    fig.tight_layout()
    fig.savefig(SUCCESS_FIG, dpi=160)
    plt.close(fig)


def main() -> None:
    rows = build_rows()
    summary = summarize(rows)
    write_csv(BUDGET_CSV, rows)
    write_csv(SUMMARY_CSV, summary)
    plot_required(rows)
    plot_success(rows)
    print(f"wrote {len(rows)} rows to {BUDGET_CSV.relative_to(ROOT)}")
    print(f"wrote {len(summary)} rows to {SUMMARY_CSV.relative_to(ROOT)}")
    print(f"wrote {REQUIRED_FIG.relative_to(ROOT)}")
    print(f"wrote {SUCCESS_FIG.relative_to(ROOT)}")


if __name__ == "__main__":
    os.environ.setdefault("MPLBACKEND", "Agg")
    main()
