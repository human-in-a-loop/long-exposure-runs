# created: 2026-05-16T16:07:00Z
# cycle: 30
# run_id: run-2026-05-15T153635Z
# agent: worker
# milestone: M19-smoothed-window-paley-wiener-lemma
"""Leakage tradeoffs for smoothed local spectral windows."""

from __future__ import annotations

import csv
import math
from pathlib import Path

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
OUT_CSV = ROOT / "data/extension_candidates/smoothed_window_leakage_tradeoffs.csv"
SUMMARY_CSV = ROOT / "data/extension_candidates/smoothed_window_leakage_summary.csv"
LEAKAGE_FIG = ROOT / "reports/figures/m19_kernel_leakage_profiles.png"
PHASE_FIG = ROOT / "reports/figures/m19_support_resolution_phase_diagram.png"

LAMBDA_EDGE = 0.25
SMALL_LEAKAGE_THRESHOLD = 1e-2


def num_text(value: float) -> str:
    if math.isinf(value) or math.isnan(value):
        return str(value)
    if abs(value) < 1e-14:
        value = 0.0
    return f"{value:.12g}"


def exact_delta_r(lam: float, delta_lambda: float) -> float:
    if lam < LAMBDA_EDGE or delta_lambda < 0:
        raise ValueError("lambda must be >= 1/4 and delta must be nonnegative")
    return math.sqrt(lam + delta_lambda - LAMBDA_EDGE) - math.sqrt(lam - LAMBDA_EDGE)


def classify_regime(lam: float, delta_lambda: float) -> str:
    gap = lam - LAMBDA_EDGE
    if gap <= 0 or gap <= delta_lambda:
        return "edge"
    if lam >= 25.0:
        return "high_energy"
    return "bulk"


def delta_r_exponent(regime: str, d: float) -> float:
    if regime == "edge":
        return d / 2.0
    return d


def support_value(model: str, n: float, eta: float) -> tuple[float, float, str]:
    if model == "log_n":
        return math.log(n), 0.0, "sub_polynomial"
    if model == "n_eta":
        return n**eta, eta, "polynomial"
    raise ValueError(f"unknown support model: {model}")


def gaussian_tail(x: float) -> float:
    """Two-sided normalized L1 tail for exp(-u^2/2)."""
    return math.erfc(max(x, 0.0) / math.sqrt(2.0))


def exponential_tail(x: float) -> float:
    """Two-sided normalized L1 tail for exp(-|u|)."""
    return math.exp(-max(x, 0.0))


def fejer_transition_proxy(x: float) -> float:
    """Compact-Fourier smoothing proxy: unresolved until R*delta reaches 1."""
    return max(0.0, 1.0 - max(x, 0.0))


def leakage_proxy(kernel: str, r_delta: float) -> float:
    if kernel == "gaussian_fourier_tail":
        return gaussian_tail(r_delta)
    if kernel == "exponential_tail_proxy":
        return exponential_tail(r_delta)
    if kernel == "compact_fejer_transition_proxy":
        return fejer_transition_proxy(r_delta)
    raise ValueError(f"unknown kernel: {kernel}")


def asymptotic_relation(r_exponent: float, width_exponent: float, model: str) -> str:
    if model == "log_n":
        if width_exponent == 0:
            return "diverges_logarithmically"
        return "goes_to_zero"
    diff = r_exponent - width_exponent
    if diff > 1e-12:
        return "goes_to_infinity"
    if diff < -1e-12:
        return "goes_to_zero"
    return "stays_bounded"


def classification(model: str, support_exponent: float, width_exponent: float) -> str:
    relation = asymptotic_relation(support_exponent, width_exponent, model)
    if relation in {"goes_to_infinity", "diverges_logarithmically"}:
        return "small leakage asymptotically"
    if relation == "stays_bounded":
        return "fixed-quality only"
    return "negative obstruction"


def build_rows() -> list[dict[str, str]]:
    n_grid = [10.0**6, 10.0**12]
    lambda_grid = [0.25, 4.0, 25.0]
    d_grid = [0.0, 0.002, 0.004, 0.006, 0.008, 0.01, 0.02, 0.05, 0.1, 0.25, 0.5]
    eta_grid = [0.0, 0.002, 0.004, 0.006, 0.008, 0.01, 0.02, 0.05, 0.1, 0.25, 0.5]
    kernels = ["gaussian_fourier_tail", "exponential_tail_proxy", "compact_fejer_transition_proxy"]
    support_models = ["log_n", "n_eta"]
    rows: list[dict[str, str]] = []
    for n in n_grid:
        for lam in lambda_grid:
            for d in d_grid:
                delta_lambda = 1.0 if d == 0 else n ** (-d)
                dr = exact_delta_r(lam, delta_lambda)
                regime = classify_regime(lam, delta_lambda)
                width_exp = delta_r_exponent(regime, d)
                for support_model in support_models:
                    etas = [0.0] if support_model == "log_n" else eta_grid
                    for eta in etas:
                        support, support_exp, support_type = support_value(support_model, n, eta)
                        r_delta = support * dr
                        relation = asymptotic_relation(support_exp, width_exp, support_model)
                        resolved = relation in {"stays_bounded", "goes_to_infinity", "diverges_logarithmically"}
                        for kernel in kernels:
                            leakage = leakage_proxy(kernel, r_delta)
                            rows.append(
                                {
                                    "n": num_text(n),
                                    "Lambda": num_text(lam),
                                    "regime": regime,
                                    "Delta_exponent_d": num_text(d),
                                    "Delta_lambda": num_text(delta_lambda),
                                    "delta_r_exact": num_text(dr),
                                    "delta_r_exponent": num_text(width_exp),
                                    "support_model": support_model,
                                    "support_type": support_type,
                                    "eta": num_text(eta),
                                    "support_R": num_text(support),
                                    "support_exponent": num_text(support_exp),
                                    "R_delta_r": num_text(r_delta),
                                    "R_delta_exponent": num_text(support_exp - width_exp),
                                    "asymptotic_R_delta": relation,
                                    "kernel": kernel,
                                    "leakage_proxy": num_text(leakage),
                                    "resolved_flag": str(resolved).lower(),
                                    "small_leakage_flag": str(leakage < SMALL_LEAKAGE_THRESHOLD).lower(),
                                    "classification": classification(support_model, support_exp, width_exp),
                                }
                            )
    return rows


def build_summary(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    keys = sorted({(r["regime"], r["support_model"], r["kernel"]) for r in rows})
    summary: list[dict[str, str]] = []
    for regime, support_model, kernel in keys:
        subset = [r for r in rows if (r["regime"], r["support_model"], r["kernel"]) == (regime, support_model, kernel)]
        negative = [r for r in subset if r["classification"] == "negative obstruction"]
        fixed = [r for r in subset if r["classification"] == "fixed-quality only"]
        small = [r for r in subset if r["classification"] == "small leakage asymptotically"]
        summary.append(
            {
                "regime": regime,
                "support_model": support_model,
                "kernel": kernel,
                "rows": str(len(subset)),
                "negative_obstruction_rows": str(len(negative)),
                "fixed_quality_rows": str(len(fixed)),
                "small_leakage_asymptotic_rows": str(len(small)),
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


def plot_leakage_profiles() -> None:
    xs = [10 ** (-2 + i * 4 / 240) for i in range(241)]
    fig, ax = plt.subplots(figsize=(8.2, 5.0))
    ax.plot(xs, [gaussian_tail(x) for x in xs], color="#4c78a8", label="Gaussian Fourier tail")
    ax.plot(xs, [exponential_tail(x) for x in xs], color="#e45756", label="Exponential tail proxy")
    ax.plot(xs, [fejer_transition_proxy(x) for x in xs], color="#54a24b", label="Compact Fejer transition proxy")
    ax.axhline(SMALL_LEAKAGE_THRESHOLD, color="black", linestyle="--", linewidth=1, label="small-leakage threshold")
    ax.axvline(1.0, color="gray", linestyle=":", linewidth=1.2, label="R delta_r = 1")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("scaled support R delta_r")
    ax.set_ylabel("normalized leakage proxy")
    ax.set_title("Leakage decreases only after the support resolves the window")
    ax.grid(True, alpha=0.25)
    ax.legend(fontsize=8)
    fig.tight_layout()
    LEAKAGE_FIG.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(LEAKAGE_FIG, dpi=180)
    plt.close(fig)


def plot_phase_diagram() -> None:
    d_values = [i / 200 for i in range(0, 101)]
    fig, ax = plt.subplots(figsize=(8.2, 5.0))
    ax.plot(d_values, d_values, color="#4c78a8", linewidth=2, label="bulk/high energy threshold eta = d")
    ax.plot(d_values, [d / 2 for d in d_values], color="#e45756", linewidth=2, label="edge threshold eta = d/2")
    ax.fill_between(d_values, d_values, 0.5, color="#d8f0d2", alpha=0.35, label="bulk small-leakage side")
    ax.fill_between(d_values, [d / 2 for d in d_values], 0.5, color="#f5d6d3", alpha=0.20, label="edge small-leakage side")
    ax.set_xlim(0, 0.5)
    ax.set_ylim(0, 0.5)
    ax.set_xlabel("lambda-window exponent d where Delta = n^{-d}")
    ax.set_ylabel("support exponent eta where R = n^eta")
    ax.set_title("Polynomially shrinking windows require polynomial support")
    ax.grid(True, alpha=0.25)
    ax.legend(fontsize=8)
    fig.tight_layout()
    PHASE_FIG.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(PHASE_FIG, dpi=180)
    plt.close(fig)


def main() -> None:
    rows = build_rows()
    summary = build_summary(rows)
    write_csv(OUT_CSV, rows)
    write_csv(SUMMARY_CSV, summary)
    plot_leakage_profiles()
    plot_phase_diagram()
    print(f"wrote {OUT_CSV.relative_to(ROOT)} ({len(rows)} rows)")
    print(f"wrote {SUMMARY_CSV.relative_to(ROOT)} ({len(summary)} rows)")
    print(f"wrote {LEAKAGE_FIG.relative_to(ROOT)}")
    print(f"wrote {PHASE_FIG.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
