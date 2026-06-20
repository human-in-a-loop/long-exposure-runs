# created: 2026-05-16T23:35:00Z
# cycle: 45
# run_id: run-2026-05-15T153635Z
# agent: worker
# milestone: M34-finite-nonshrinking-spectral-statistics

"""Analyze fixed, non-shrinking spectral-window consequences for M34.

The rows are deterministic bookkeeping consequences of the Kim--Tao Weyl
estimate and rigidity event.  Alpha values are representative labels for
regime comparison; no constants or exponents are optimized here.
"""

from __future__ import annotations

import csv
import math
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

EDGE = 0.25
GENUS = 2
EPSILON = 0.05
RUN_ID = "run-2026-05-15T153635Z"

DATA_DIR = Path("data/extension_candidates")
FIGURE_DIR = Path("reports/figures")

THRESHOLDS_PATH = DATA_DIR / "m34_fixed_window_thresholds.csv"
CLASSIFICATION_PATH = DATA_DIR / "m34_fixed_window_classification.csv"
COMPARISON_PATH = DATA_DIR / "m34_endpoint_vs_rigidity_comparison.csv"

RELATIVE_ERROR_FIGURE = FIGURE_DIR / "m34_fixed_window_relative_error.png"
ENDPOINT_RIGIDITY_FIGURE = FIGURE_DIR / "m34_endpoint_vs_rigidity_map.png"
CLASSIFICATION_FIGURE = FIGURE_DIR / "m34_window_regime_classification.png"

ALPHA_MODELS = [
    ("theorem1_representative", 0.006, 0.004, "proved_shape_representative"),
    ("improved_comparison", 0.05, 0.033, "comparison_only_not_proved"),
    ("strong_comparison", 0.20, 0.133, "comparison_only_not_proved"),
]

WINDOW_MODELS = [
    ("edge_fixed", EDGE, EDGE + 0.50, "fixed", "edge_adjacent"),
    ("near_edge_fixed", 0.26, 0.76, "fixed", "edge_adjacent"),
    ("bulk_fixed", 4.00, 4.50, "fixed", "bulk"),
    ("wide_bulk_fixed", 4.00, 6.00, "fixed", "bulk"),
    ("high_energy_fixed", 100.00, 100.50, "fixed", "high_energy"),
    ("bulk_shrinking_excluded", 4.00, 4.00, "shrinking", "outside_m34_scope"),
    ("edge_shrinking_excluded", EDGE, EDGE, "shrinking", "outside_m34_scope"),
]

N_VALUES = [10**4, 10**6, 10**8]
SHRINKING_D = 0.25


def f_prime(lam: float) -> float:
    if lam < EDGE:
        raise ValueError("Lambda must be at least 1/4")
    return 0.5 * math.tanh(math.pi * math.sqrt(max(lam - EDGE, 0.0)))


def f_profile(lam: float, steps: int = 4000) -> float:
    if lam <= EDGE:
        return 0.0
    upper = math.sqrt(lam - EDGE)
    xs = np.linspace(0.0, upper, steps + 1)
    ys = xs * np.tanh(math.pi * xs)
    return float(np.trapezoid(ys, xs))


def f_window(a: float, b: float) -> float:
    if b < a:
        raise ValueError("window endpoint b must be at least a")
    return max(f_profile(b) - f_profile(a), 0.0)


def edge_window_asym(delta: float) -> float:
    if delta < 0:
        raise ValueError("Delta must be nonnegative")
    return math.pi * delta ** 1.5 / 3.0


def fixed_relative_proxy(a: float, b: float) -> float:
    delta_f = f_window(a, b)
    if delta_f <= 0:
        return math.inf
    return b ** (0.5 + EPSILON) / ((2 * GENUS - 2) * delta_f)


def make_window(a: float, b: float, width_kind: str, n: int) -> tuple[float, float, float]:
    if width_kind == "fixed":
        return a, b, b - a
    if "edge" in str(a):
        raise AssertionError("unreachable")
    delta = n ** (-SHRINKING_D)
    return a, a + delta, delta


def classify_window(width_kind: str, regime: str, relative_exponent: float) -> tuple[str, str]:
    if width_kind != "fixed":
        return "outside_m34_scope", "requires_new_variance_input"
    if relative_exponent < 0 and regime in {"bulk", "edge_adjacent", "high_energy"}:
        return "fixed_window_count_asymptotic", "theorem_level_corollary"
    return "endpoint_subtraction_only", "endpoint_bookkeeping"


def build_threshold_rows() -> list[dict[str, float | str]]:
    rows: list[dict[str, float | str]] = []
    for n in N_VALUES:
        for alpha_label, alpha_w, alpha_r, alpha_kind in ALPHA_MODELS:
            for label, a0, b0, width_kind, base_regime in WINDOW_MODELS:
                a, b, delta = make_window(a0, b0, width_kind, n)
                if width_kind == "shrinking" and label.startswith("edge"):
                    a = EDGE
                    b = EDGE + delta
                delta_f = f_window(a, b)
                main_term_proxy = (2 * GENUS - 2) * n * delta_f
                endpoint_error_proxy = n ** (1.0 - alpha_w) * b ** (0.5 + EPSILON)
                relative_error_proxy = (
                    endpoint_error_proxy / main_term_proxy if main_term_proxy > 0 else math.inf
                )
                relative_error_exponent = -alpha_w if width_kind == "fixed" else (
                    1.5 * SHRINKING_D - alpha_w
                    if a == EDGE
                    else SHRINKING_D - alpha_w
                )
                main_term_n_exponent = 1.0 if width_kind == "fixed" else (
                    1.0 - 1.5 * SHRINKING_D if a == EDGE else 1.0 - SHRINKING_D
                )
                statement, classification = classify_window(
                    width_kind, base_regime, relative_error_exponent
                )
                rows.append(
                    {
                        "window_label": label,
                        "n": n,
                        "alpha_label": alpha_label,
                        "alpha_kind": alpha_kind,
                        "alpha_W": alpha_w,
                        "alpha_R": alpha_r,
                        "epsilon": EPSILON,
                        "a": a,
                        "b": b,
                        "Delta": delta,
                        "width_kind": width_kind,
                        "regime": base_regime,
                        "F_b_minus_F_a": delta_f,
                        "main_term_proxy": main_term_proxy,
                        "endpoint_error_proxy": endpoint_error_proxy,
                        "relative_error_proxy": relative_error_proxy,
                        "main_term_n_exponent": main_term_n_exponent,
                        "endpoint_error_n_exponent": 1.0 - alpha_w,
                        "relative_error_n_exponent": relative_error_exponent,
                        "fixed_relative_constant_proxy": fixed_relative_proxy(a, b),
                        "density_at_a": f_prime(a),
                        "statement": statement,
                        "classification": classification,
                        "decision": (
                            "advance_fixed_window_corollary"
                            if classification == "theorem_level_corollary"
                            else "exclude_from_m34"
                        ),
                    }
                )
    return rows


def build_classification_rows() -> list[dict[str, str]]:
    return [
        {
            "claim_id": "fixed_window_endpoint_subtraction",
            "statement": "N_Xn([a,b])=(2g-2)n(F(b)-F(a))+O(n^(1-alpha_W)b^(1/2+epsilon)) for fixed 1/4<=a<b.",
            "classification": "theorem_level_corollary",
            "evidence": "simultaneous endpoint subtraction from Kim--Tao Weyl estimate",
            "decision": "keep",
        },
        {
            "claim_id": "fixed_window_centered_bound",
            "statement": "The centered count is O(n^(1-alpha_W)b^(1/2+epsilon)) for fixed intervals.",
            "classification": "theorem_level_deterministic_bound",
            "evidence": "same statement with main term moved left",
            "decision": "keep_but_not_distributional",
        },
        {
            "claim_id": "rigidity_reference_location_count",
            "statement": "Rigidity compares random counts with reference-location counts in intervals expanded by delta_R.",
            "classification": "rigidity_bookkeeping",
            "evidence": "window inclusion from M16, no sharper count scale than endpoint route",
            "decision": "keep_as_comparison",
        },
        {
            "claim_id": "shrinking_window_count",
            "statement": "Delta=n^(-d) windows are controlled below the inherited endpoint threshold.",
            "classification": "requires_new_variance_input",
            "evidence": "M19-M25 obstruction chain remains active",
            "decision": "exclude_from_m34_scope",
        },
        {
            "claim_id": "variance_asymptotics",
            "statement": "Variance asymptotics or concentration at smaller than endpoint-error scale.",
            "classification": "not_claimed",
            "evidence": "Theorem 1 supplies high-probability deterministic count error, not variance",
            "decision": "no_claim",
        },
        {
            "claim_id": "limiting_distribution",
            "statement": "Poisson, Gaussian, GUE/GOE, or other limiting laws for window counts.",
            "classification": "not_claimed",
            "evidence": "no correlation or distributional input in Theorem 1",
            "decision": "no_claim",
        },
        {
            "claim_id": "level_repulsion_or_universality",
            "statement": "Level repulsion, local universality, or mean-spacing statistics.",
            "classification": "not_claimed",
            "evidence": "fixed-window Weyl asymptotics are macroscopic and endpoint-derived",
            "decision": "no_claim",
        },
    ]


def build_comparison_rows() -> list[dict[str, float | str]]:
    rows: list[dict[str, float | str]] = []
    for label, a, b, width_kind, regime in WINDOW_MODELS:
        if width_kind != "fixed":
            continue
        for alpha_label, alpha_w, alpha_r, alpha_kind in ALPHA_MODELS:
            delta_r_exponent = -alpha_r
            endpoint_relative_exp = -alpha_w
            fixed_delta = b - a
            rigidity_useful = fixed_delta > 0
            rows.append(
                {
                    "window_label": label,
                    "alpha_label": alpha_label,
                    "alpha_kind": alpha_kind,
                    "regime": regime,
                    "a": a,
                    "b": b,
                    "Delta": fixed_delta,
                    "endpoint_relative_error_exponent": endpoint_relative_exp,
                    "rigidity_displacement_exponent": delta_r_exponent,
                    "rigidity_expansion_relative_to_fixed_width": "vanishes_as_n_grows"
                    if rigidity_useful
                    else "not_applicable",
                    "endpoint_route_classification": "theorem_level_corollary",
                    "rigidity_route_classification": "rigidity_bookkeeping",
                    "winner": "endpoint_subtraction_for_count_asymptotic",
                }
            )
    return rows


def write_csv(path: Path, rows: list[dict[str, float | str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def plot_relative_error(rows: list[dict[str, float | str]]) -> None:
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(8.2, 5.0))
    filtered = [
        row
        for row in rows
        if row["width_kind"] == "fixed"
        and row["alpha_label"] == "theorem1_representative"
        and int(row["n"]) == 10**8
    ]
    labels = [str(row["window_label"]) for row in filtered]
    values = [float(row["relative_error_n_exponent"]) for row in filtered]
    constants = [float(row["fixed_relative_constant_proxy"]) for row in filtered]
    bars = ax.bar(labels, values, color=["#3973ac", "#62a87c", "#d99a3d", "#8f6fb3", "#b55353"])
    ax.axhline(0.0, color="black", linewidth=1.0)
    ax.set_ylabel("relative error exponent in n")
    ax.set_title("M34 fixed-window relative error exponent")
    ax.set_ylim(min(values) - 0.01, 0.01)
    ax.tick_params(axis="x", rotation=25)
    for bar, const in zip(bars, constants):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() - 0.001,
            f"C~{const:.1f}",
            ha="center",
            va="top",
            fontsize=8,
            color="white",
        )
    fig.tight_layout()
    fig.savefig(RELATIVE_ERROR_FIGURE, dpi=180)
    plt.close(fig)


def plot_endpoint_vs_rigidity(rows: list[dict[str, float | str]]) -> None:
    labels = ["endpoint_subtraction", "rigidity_location"]
    window_labels = [row[0] for row in WINDOW_MODELS if row[3] == "fixed"]
    matrix = np.zeros((len(window_labels), len(labels)))
    matrix[:, 0] = 2.0
    matrix[:, 1] = 1.0
    fig, ax = plt.subplots(figsize=(7.0, 4.8))
    image = ax.imshow(matrix, cmap="cividis", vmin=0, vmax=2, aspect="auto")
    ax.set_xticks(range(len(labels)), labels, rotation=20, ha="right")
    ax.set_yticks(range(len(window_labels)), window_labels)
    ax.set_title("M34 endpoint route versus rigidity-location route")
    for i in range(len(window_labels)):
        ax.text(0, i, "count\nasymptotic", ha="center", va="center", color="white", fontsize=8)
        ax.text(1, i, "comparison\nbookkeeping", ha="center", va="center", color="white", fontsize=8)
    cbar = fig.colorbar(image, ax=ax, ticks=[1, 2])
    cbar.ax.set_yticklabels(["bookkeeping", "theorem corollary"])
    fig.tight_layout()
    fig.savefig(ENDPOINT_RIGIDITY_FIGURE, dpi=180)
    plt.close(fig)


def plot_classification(class_rows: list[dict[str, str]]) -> None:
    labels = [row["claim_id"] for row in class_rows]
    categories = sorted({row["classification"] for row in class_rows})
    code = {category: idx for idx, category in enumerate(categories)}
    matrix = np.array([[code[row["classification"]]] for row in class_rows])
    fig, ax = plt.subplots(figsize=(8.4, 5.0))
    image = ax.imshow(matrix, cmap="viridis", aspect="auto")
    ax.set_xticks([0], ["classification"])
    ax.set_yticks(range(len(labels)), labels)
    ax.set_title("M34 fixed-window statement classification")
    for i, row in enumerate(class_rows):
        ax.text(0, i, row["classification"], ha="center", va="center", fontsize=7, color="white")
    cbar = fig.colorbar(image, ax=ax, ticks=list(code.values()))
    cbar.ax.set_yticklabels(categories)
    fig.tight_layout()
    fig.savefig(CLASSIFICATION_FIGURE, dpi=180)
    plt.close(fig)


def main() -> None:
    threshold_rows = build_threshold_rows()
    classification_rows = build_classification_rows()
    comparison_rows = build_comparison_rows()
    write_csv(THRESHOLDS_PATH, threshold_rows)
    write_csv(CLASSIFICATION_PATH, classification_rows)
    write_csv(COMPARISON_PATH, comparison_rows)
    plot_relative_error(threshold_rows)
    plot_endpoint_vs_rigidity(comparison_rows)
    plot_classification(classification_rows)
    print(f"wrote {THRESHOLDS_PATH} ({len(threshold_rows)} rows)")
    print(f"wrote {CLASSIFICATION_PATH} ({len(classification_rows)} rows)")
    print(f"wrote {COMPARISON_PATH} ({len(comparison_rows)} rows)")
    print(f"wrote {RELATIVE_ERROR_FIGURE}")
    print(f"wrote {ENDPOINT_RIGIDITY_FIGURE}")
    print(f"wrote {CLASSIFICATION_FIGURE}")
    print("decision=advance_fixed_window_corollary_preserve_no_local_statistics_claim")


if __name__ == "__main__":
    main()
