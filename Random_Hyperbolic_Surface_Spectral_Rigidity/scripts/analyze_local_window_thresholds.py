# created: 2026-05-16T13:35:00Z
# cycle: 27
# run_id: run-2026-05-15T153635Z
# agent: worker
# milestone: M16-local-spectral-window-corollaries
"""Analyze local spectral-window thresholds implied by Kim--Tao estimates."""

from __future__ import annotations

import csv
import math
from pathlib import Path

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
THRESHOLD_CSV = ROOT / "data/extension_candidates/local_window_thresholds.csv"
SUMMARY_CSV = ROOT / "data/extension_candidates/local_window_regime_summary.csv"
PHASE_FIG = ROOT / "reports/figures/m16_window_threshold_phase_diagram.png"
DENSITY_FIG = ROOT / "reports/figures/m16_edge_vs_bulk_density.png"

LAMBDA_EDGE = 0.25


def num_text(value: float) -> str:
    if math.isnan(value) or math.isinf(value):
        return str(value)
    if abs(value) < 1e-14:
        value = 0.0
    return f"{value:.12g}"


def spectral_F(lam: float) -> float:
    """Return F(lam)=int_0^sqrt(lam-1/4) r tanh(pi r) dr for lam>=1/4."""
    if lam < LAMBDA_EDGE:
        raise ValueError("lambda must be at least 1/4")
    upper = math.sqrt(max(lam - LAMBDA_EDGE, 0.0))
    if upper == 0.0:
        return 0.0
    intervals = max(200, int(200 * upper))
    if intervals % 2 == 1:
        intervals += 1
    h = upper / intervals
    total = 0.0
    for i in range(intervals + 1):
        r = i * h
        weight = 4.0 if i % 2 == 1 else 2.0
        if i == 0 or i == intervals:
            weight = 1.0
        total += weight * r * math.tanh(math.pi * r)
    return total * h / 3.0


def spectral_density(lam: float) -> float:
    """Derivative F'(lam), with the continuous edge value F'(1/4)=0."""
    if lam < LAMBDA_EDGE:
        raise ValueError("lambda must be at least 1/4")
    if lam == LAMBDA_EDGE:
        return 0.0
    return 0.5 * math.tanh(math.pi * math.sqrt(lam - LAMBDA_EDGE))


def local_mass(lam: float, delta: float, genus: int) -> float:
    """Deterministic per-cover-degree main term for [lam, lam+delta]."""
    return (2.0 * genus - 2.0) * (spectral_F(lam + delta) - spectral_F(lam))


def normalized_endpoint_error(lam: float, delta: float, alpha_w: float, epsilon: float, n: int) -> float:
    """Endpoint-subtraction error after dividing by n, with unit endpoint constant."""
    return 2.0 * (n ** (-alpha_w)) * ((lam + delta) ** (0.5 + epsilon))


def weyl_delta_threshold(lam: float, genus: int, alpha_w: float, epsilon: float, n: int) -> float:
    """Smallest delta where normalized deterministic mass matches inherited endpoint error."""
    def objective(delta: float) -> float:
        return local_mass(lam, delta, genus) - normalized_endpoint_error(lam, delta, alpha_w, epsilon, n)

    hi = max(1e-8, lam - LAMBDA_EDGE + 1e-8)
    while objective(hi) <= 0.0 and hi < 1e8:
        hi *= 2.0
    if hi >= 1e8 and objective(hi) <= 0.0:
        return math.nan
    lo = 0.0
    for _ in range(160):
        mid = 0.5 * (lo + hi)
        if objective(mid) <= 0.0:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def bulk_delta_approx(lam: float, genus: int, alpha_w: float, epsilon: float, n: int) -> float:
    """Bulk linearized threshold, invalid when F'(lam)=0."""
    density = spectral_density(lam)
    if density <= 0.0:
        return math.inf
    return 2.0 * (n ** (-alpha_w)) * (lam ** (0.5 + epsilon)) / ((2.0 * genus - 2.0) * density)


def rigidity_displacement(lam: float, alpha_r: float, epsilon: float, n: int) -> float:
    """Normalized eigenvalue displacement scale with unit theorem constant."""
    return (lam ** (0.5 + epsilon)) * (n ** (-alpha_r))


def mean_spacing_proxy(lam: float, genus: int, n: int) -> float:
    density = spectral_density(lam)
    if density <= 0.0:
        return math.inf
    return 1.0 / (n * (2.0 * genus - 2.0) * density)


def build_threshold_rows(
    alpha_w: float = 0.006,
    alpha_r: float = 0.004,
    epsilon: float = 0.1,
    genus: int = 2,
) -> list[dict[str, str]]:
    lambdas = [
        ("edge", 0.25),
        ("near_edge", 0.250001),
        ("moderate_bulk", 1.0),
        ("bulk", 4.0),
        ("high_energy", 25.0),
        ("very_high_energy", 100.0),
    ]
    n_values = [10**4, 10**6, 10**8, 10**10, 10**12]
    rows: list[dict[str, str]] = []
    for regime, lam in lambdas:
        for n in n_values:
            exact_delta = weyl_delta_threshold(lam, genus, alpha_w, epsilon, n)
            bulk_delta = bulk_delta_approx(lam, genus, alpha_w, epsilon, n)
            rigid_delta = rigidity_displacement(lam, alpha_r, epsilon, n)
            spacing = mean_spacing_proxy(lam, genus, n)
            rows.append(
                {
                    "regime": regime,
                    "lambda": num_text(lam),
                    "n": str(n),
                    "genus": str(genus),
                    "alpha_W": num_text(alpha_w),
                    "alpha_R": num_text(alpha_r),
                    "epsilon": num_text(epsilon),
                    "density_F_prime": num_text(spectral_density(lam)),
                    "weyl_subtraction_delta_exact": num_text(exact_delta),
                    "weyl_subtraction_delta_bulk_approx": num_text(bulk_delta),
                    "rigidity_displacement_delta": num_text(rigid_delta),
                    "mean_spacing_proxy": num_text(spacing),
                    "weyl_over_spacing_ratio": num_text(exact_delta / spacing if math.isfinite(spacing) else math.inf),
                    "rigidity_over_spacing_ratio": num_text(rigid_delta / spacing if math.isfinite(spacing) else math.inf),
                    "edge_linearization_valid": "no" if spectral_density(lam) == 0.0 or regime in {"edge", "near_edge"} else "yes",
                    "notes": "Constants are normalized to one endpoint/rigidity constant; compare exponents and regimes, not theorem constants.",
                }
            )
    return rows


def build_summary_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    summary: list[dict[str, str]] = []
    regimes = []
    for row in rows:
        if row["regime"] not in regimes:
            regimes.append(row["regime"])
    for regime in regimes:
        selected = [row for row in rows if row["regime"] == regime]
        first = selected[0]
        last = selected[-1]
        exact_first = float(first["weyl_subtraction_delta_exact"])
        exact_last = float(last["weyl_subtraction_delta_exact"])
        rigid_first = float(first["rigidity_displacement_delta"])
        rigid_last = float(last["rigidity_displacement_delta"])
        n_first = float(first["n"])
        n_last = float(last["n"])
        weyl_slope = math.log(exact_last / exact_first) / math.log(n_last / n_first)
        rigid_slope = math.log(rigid_last / rigid_first) / math.log(n_last / n_first)
        summary.append(
            {
                "regime": regime,
                "lambda": first["lambda"],
                "density_F_prime": first["density_F_prime"],
                "edge_linearization_valid": first["edge_linearization_valid"],
                "weyl_delta_power_slope_vs_n": num_text(weyl_slope),
                "rigidity_delta_power_slope_vs_n": num_text(rigid_slope),
                "expected_bulk_weyl_slope": num_text(-float(first["alpha_W"]) if first["edge_linearization_valid"] == "yes" else -2.0 * float(first["alpha_W"]) / 3.0),
                "expected_rigidity_slope": num_text(-float(first["alpha_R"])),
                "interpretation": regime_interpretation(regime),
            }
        )
    return summary


def regime_interpretation(regime: str) -> str:
    if regime == "edge":
        return "Use F(1/4+Delta)-F(1/4) ~ (pi/3) Delta^(3/2); linear density is zero."
    if regime == "near_edge":
        return "Bulk density is positive but tiny; edge curvature still dominates unless Delta is much smaller than Lambda-1/4."
    if regime in {"moderate_bulk", "bulk"}:
        return "Bulk linearization is valid; Weyl-subtraction threshold scales as n^(-alpha_W)."
    return "High-energy density is near 1/2; lambda^(1/2+epsilon) endpoint error is the main energy dependence."


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def plot_phase(rows: list[dict[str, str]]) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
    keep = [row for row in rows if row["regime"] in {"edge", "moderate_bulk", "high_energy"}]
    colors = {"edge": "#e45756", "moderate_bulk": "#4c78a8", "high_energy": "#54a24b"}
    for regime in ["edge", "moderate_bulk", "high_energy"]:
        selected = [row for row in keep if row["regime"] == regime]
        n_values = [float(row["n"]) for row in selected]
        axes[0].loglog(n_values, [float(row["weyl_subtraction_delta_exact"]) for row in selected], marker="o", color=colors[regime], label=f"{regime}: Weyl")
        axes[0].loglog(n_values, [float(row["rigidity_displacement_delta"]) for row in selected], marker="s", linestyle="--", color=colors[regime], label=f"{regime}: rigidity")
        ratios = [float(row["weyl_over_spacing_ratio"]) if row["weyl_over_spacing_ratio"] != "inf" else math.nan for row in selected]
        axes[1].loglog(n_values, ratios, marker="o", color=colors[regime], label=f"{regime}: Weyl/spacing")
        rigid_ratios = [float(row["rigidity_over_spacing_ratio"]) if row["rigidity_over_spacing_ratio"] != "inf" else math.nan for row in selected]
        axes[1].loglog(n_values, rigid_ratios, marker="s", linestyle="--", color=colors[regime], label=f"{regime}: rigidity/spacing")
    axes[0].set_xlabel("cover degree n")
    axes[0].set_ylabel("window scale Delta")
    axes[0].set_title("Normalized local-window thresholds")
    axes[1].set_xlabel("cover degree n")
    axes[1].set_ylabel("threshold / mean-spacing proxy")
    axes[1].set_title("Thresholds remain mesoscopic")
    for ax in axes:
        ax.grid(True, which="both", alpha=0.25)
        ax.legend(fontsize=8)
    fig.tight_layout()
    PHASE_FIG.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(PHASE_FIG, dpi=180)
    plt.close(fig)


def plot_density() -> None:
    offsets = [10 ** exponent for exponent in [x / 4 for x in range(-24, 17)]]
    lambdas = [LAMBDA_EDGE + offset for offset in offsets]
    densities = [spectral_density(lam) for lam in lambdas]
    edge_asymptotic = [0.5 * math.pi * math.sqrt(offset) for offset in offsets]
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.loglog(offsets, densities, marker="o", label="F'(1/4+t)")
    ax.loglog(offsets, edge_asymptotic, linestyle="--", label="(pi/2) sqrt(t)")
    ax.axhline(0.5, color="black", linewidth=0.8, linestyle=":", label="high-energy limit 1/2")
    ax.set_xlabel("t = Lambda - 1/4")
    ax.set_ylabel("density F'(Lambda)")
    ax.set_title("Edge density vanishes; bulk density saturates")
    ax.grid(True, which="both", alpha=0.25)
    ax.legend()
    fig.tight_layout()
    DENSITY_FIG.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(DENSITY_FIG, dpi=180)
    plt.close(fig)


def main() -> None:
    rows = build_threshold_rows()
    summary = build_summary_rows(rows)
    write_csv(THRESHOLD_CSV, rows)
    write_csv(SUMMARY_CSV, summary)
    plot_phase(rows)
    plot_density()
    print(f"wrote {THRESHOLD_CSV.relative_to(ROOT)} ({len(rows)} rows)")
    print(f"wrote {SUMMARY_CSV.relative_to(ROOT)} ({len(summary)} rows)")
    print(f"wrote {PHASE_FIG.relative_to(ROOT)}")
    print(f"wrote {DENSITY_FIG.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
