# created: 2026-05-16T19:52:00Z
# cycle: 38
# run_id: run-2026-05-15T153635Z
# agent: worker
# milestone: M27-multiplicity-and-cluster-corollaries-from-rigidity

"""Compute rigidity-scale multiplicity and cluster envelopes for M27.

The calculations are deterministic consequences of the Kim--Tao reference
locations.  The alpha values below are representative labels for regime
comparison; they are not optimized or improved theorem exponents.
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
C_RIGIDITY = 1.0
RUN_ID = "run-2026-05-15T153635Z"

DATA_DIR = Path("data/extension_candidates")
FIGURE_DIR = Path("reports/figures")
GRID_PATH = DATA_DIR / "m27_cluster_bound_grid.csv"
CLASSIFICATION_PATH = DATA_DIR / "m27_cluster_regime_classification.csv"
BOUND_FIGURE = FIGURE_DIR / "m27_cluster_bound_vs_n.png"
PHASE_FIGURE = FIGURE_DIR / "m27_regime_phase_diagram.png"

ALPHA_MODELS = [
    ("theorem1_representative", 0.006, "proved_shape_representative"),
    ("edge_weakened_representative", 0.004, "proved_shape_representative"),
    ("bounded_loss_hypothetical", 0.20, "comparison_only_not_proved"),
]

ENERGY_MODELS = [
    ("edge_delta_n_alpha", "edge_power", None),
    ("near_edge_fixed", "fixed", 0.26),
    ("bulk_fixed", "fixed", 4.0),
    ("high_energy", "fixed", 100.0),
]


def f_prime(lam: float) -> float:
    if lam < EDGE:
        raise ValueError("Lambda must be at least 1/4")
    return 0.5 * math.tanh(math.pi * math.sqrt(max(lam - EDGE, 0.0)))


def f_edge_asym(delta: float) -> float:
    if delta < 0:
        raise ValueError("Delta must be nonnegative")
    return math.pi * delta ** 1.5 / 3.0


def f_profile(lam: float, steps: int = 2000) -> float:
    if lam <= EDGE:
        return 0.0
    upper = math.sqrt(lam - EDGE)
    xs = np.linspace(0.0, upper, steps + 1)
    ys = xs * np.tanh(math.pi * xs)
    return float(np.trapezoid(ys, xs))


def rigidity_radius(lam: float, n: int, alpha: float) -> float:
    return C_RIGIDITY * lam ** (0.5 + EPSILON) * n ** (-alpha)


def reference_count_envelope(center: float, width: float, n: int, alpha: float) -> float:
    radius = rigidity_radius(max(center, EDGE), n, alpha)
    lo = max(EDGE, center - 0.5 * width - radius)
    hi = max(EDGE, center + 0.5 * width + radius)
    area = max(f_profile(hi) - f_profile(lo), 0.0)
    return 1.0 + (2 * GENUS - 2) * n * area


def edge_reference_count(delta: float, radius: float, n: int) -> float:
    hi_delta = max(delta + radius, 0.0)
    return 1.0 + (2 * GENUS - 2) * n * f_edge_asym(hi_delta)


def classify(row: dict[str, float | str]) -> str:
    envelope = float(row["cluster_envelope"])
    n = float(row["n"])
    density = float(row["density"])
    radius = float(row["rigidity_radius"])
    energy = str(row["energy_label"])
    alpha_kind = str(row["alpha_kind"])
    lam = float(row["lambda"])
    if alpha_kind == "comparison_only_not_proved":
        return "hypothetical_comparison_only"
    if energy == "edge_delta_n_alpha":
        return "edge_endpoint_equivalent"
    if lam >= 50.0 and radius > 0.1:
        return "high_energy_loss_dominated"
    if envelope >= 0.5 * n:
        return "tautological_or_endpoint_only"
    if density * radius * n > 10.0:
        return "rigidity_scale_cluster_bound"
    return "nontrivial_small_cluster_envelope"


def build_rows() -> list[dict[str, float | str]]:
    rows: list[dict[str, float | str]] = []
    for n in [10**3, 10**4, 10**5, 10**6, 10**7, 10**8]:
        for alpha_label, alpha, alpha_kind in ALPHA_MODELS:
            edge_delta = n ** (-0.25)
            for energy_label, energy_kind, fixed_lam in ENERGY_MODELS:
                lam = EDGE + edge_delta if energy_kind == "edge_power" else float(fixed_lam)
                density = f_prime(lam)
                radius = rigidity_radius(lam, n, alpha)
                mean_spacing = math.inf if density == 0 else 1.0 / ((2 * GENUS - 2) * n * density)
                if energy_kind == "edge_power":
                    envelope = edge_reference_count(edge_delta, radius, n)
                else:
                    envelope = reference_count_envelope(lam, 0.0, n, alpha)
                row: dict[str, float | str] = {
                    "n": n,
                    "g": GENUS,
                    "epsilon": EPSILON,
                    "alpha_label": alpha_label,
                    "alpha_kind": alpha_kind,
                    "alpha": alpha,
                    "energy_label": energy_label,
                    "lambda": lam,
                    "density": density,
                    "mean_spacing": mean_spacing,
                    "rigidity_radius": radius,
                    "cluster_envelope": envelope,
                    "normalized_envelope": envelope / n,
                }
                row["classification"] = classify(row)
                rows.append(row)
    return rows


def write_csv(path: Path, rows: list[dict[str, float | str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def build_classification(rows: list[dict[str, float | str]]) -> list[dict[str, float | str]]:
    grouped: dict[tuple[str, str], list[dict[str, float | str]]] = {}
    for row in rows:
        grouped.setdefault((str(row["alpha_label"]), str(row["energy_label"])), []).append(row)
    out: list[dict[str, float | str]] = []
    for (alpha_label, energy_label), group in grouped.items():
        last = group[-1]
        out.append(
            {
                "alpha_label": alpha_label,
                "energy_label": energy_label,
                "classification": last["classification"],
                "envelope_at_n_1e8": last["cluster_envelope"],
                "radius_at_n_1e8": last["rigidity_radius"],
                "density_at_n_1e8": last["density"],
                "decision": "preserve_as_bookkeeping_corollary",
            }
        )
    return out


def plot_bound(rows: list[dict[str, float | str]]) -> None:
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(8, 5))
    for alpha_label in ["theorem1_representative", "bounded_loss_hypothetical"]:
        for energy_label in ["edge_delta_n_alpha", "bulk_fixed", "high_energy"]:
            subset = [
                row
                for row in rows
                if row["alpha_label"] == alpha_label and row["energy_label"] == energy_label
            ]
            ax.loglog(
                [row["n"] for row in subset],
                [row["cluster_envelope"] for row in subset],
                marker="o",
                label=f"{alpha_label}: {energy_label}",
            )
    ax.set_xlabel("cover degree n")
    ax.set_ylabel("reference-count envelope for zero-width multiplicity")
    ax.set_title("M27 rigidity-scale cluster envelope")
    ax.grid(True, which="both", alpha=0.25)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(BOUND_FIGURE, dpi=180)
    plt.close(fig)


def plot_phase(rows: list[dict[str, float | str]]) -> None:
    labels = sorted({str(row["classification"]) for row in rows})
    code = {label: idx for idx, label in enumerate(labels)}
    alpha_labels = [label for label, _, _ in ALPHA_MODELS]
    energy_labels = [label for label, _, _ in ENERGY_MODELS]
    matrix = np.zeros((len(energy_labels), len(alpha_labels)))
    last_rows = build_classification(rows)
    by_pair = {(row["alpha_label"], row["energy_label"]): row for row in last_rows}
    for i, energy_label in enumerate(energy_labels):
        for j, alpha_label in enumerate(alpha_labels):
            matrix[i, j] = code[str(by_pair[(alpha_label, energy_label)]["classification"])]

    fig, ax = plt.subplots(figsize=(7.5, 4.8))
    image = ax.imshow(matrix, cmap="viridis", aspect="auto")
    ax.set_xticks(range(len(alpha_labels)), alpha_labels, rotation=25, ha="right")
    ax.set_yticks(range(len(energy_labels)), energy_labels)
    ax.set_title("M27 regime classification at n=1e8")
    cbar = fig.colorbar(image, ax=ax, ticks=list(code.values()))
    cbar.ax.set_yticklabels(labels)
    for i in range(len(energy_labels)):
        for j in range(len(alpha_labels)):
            ax.text(j, i, int(matrix[i, j]), ha="center", va="center", color="white", fontsize=9)
    fig.tight_layout()
    fig.savefig(PHASE_FIGURE, dpi=180)
    plt.close(fig)


def main() -> None:
    rows = build_rows()
    classification = build_classification(rows)
    write_csv(GRID_PATH, rows)
    write_csv(CLASSIFICATION_PATH, classification)
    plot_bound(rows)
    plot_phase(rows)
    print(f"wrote {GRID_PATH} ({len(rows)} rows)")
    print(f"wrote {CLASSIFICATION_PATH} ({len(classification)} rows)")
    print(f"wrote {BOUND_FIGURE}")
    print(f"wrote {PHASE_FIGURE}")
    print("decision=preserve_as_bookkeeping_corollary")


if __name__ == "__main__":
    main()
