# created: 2026-05-16T05:05:00Z
# cycle: 18
# run_id: run-2026-05-15T153635Z
# agent: worker
# milestone: M7-product-ratio-bounds
"""Analyze deterministic product-ratio bounds against Cycle 15 data."""

from __future__ import annotations

import csv
import math
from fractions import Fraction
from pathlib import Path

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
COEFF_CSV = ROOT / "data/extension_candidates/growing_template_expansion_coefficients.csv"
GROWING_SUMMARY_CSV = ROOT / "data/extension_candidates/growing_template_expansion_summary.csv"
LOG_CSV = ROOT / "data/extension_candidates/m5_log_coefficient_summary.csv"
OUT_CSV = ROOT / "data/extension_candidates/product_ratio_bound_summary.csv"
FIG = ROOT / "reports/figures/m7_product_ratio_bounds.png"
SELECTED_FAMILIES = [
    "single_label_cycle_profile",
    "single_label_path_profile",
    "rank2_balanced_profile",
    "rank2_deficit_k3",
    "rank4_delocalization_toy_s4",
]
SELECTED_ORDERS = [1, 2, 4, 8]


def parse_fraction(text: str | int | float) -> Fraction:
    value = str(text).strip()
    if not value or value.lower() == "nan":
        return Fraction(0)
    return Fraction(value)


def parse_counts(text: str) -> list[int]:
    if not text.strip():
        return []
    return [int(part) for part in text.split(";") if part.strip()]


def supports_from_profile(V: int, counts: list[int]) -> tuple[list[int], list[int]]:
    """Return numerator and denominator support indices for normalized N(x)."""
    numerator = list(range(1, V))
    denominator: list[int] = []
    for count in counts:
        denominator.extend(range(1, count))
    return numerator, denominator


def log_coefficient_from_supports(numerator: list[int], denominator: list[int], order: int) -> Fraction:
    return Fraction(sum(b**order for b in denominator) - sum(a**order for a in numerator), order)


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def slope_estimate(points: list[tuple[int, float]]) -> float:
    positive = [(float(L), value) for L, value in points if L > 0 and value > 0]
    if len(positive) < 2:
        return 0.0
    xs = [math.log(L) for L, _ in positive]
    ys = [math.log(value) for _, value in positive]
    xbar = sum(xs) / len(xs)
    ybar = sum(ys) / len(ys)
    denom = sum((x - xbar) ** 2 for x in xs)
    if denom == 0:
        return 0.0
    return sum((x - xbar) * (y - ybar) for x, y in zip(xs, ys)) / denom


def summarize_quantity(
    family: str,
    quantity: str,
    order: int,
    points: list[tuple[int, Fraction]],
    envelope_power: int,
    notes: str,
) -> dict[str, str]:
    values = [(L, abs(float(value))) for L, value in points]
    max_observed = max((value for _, value in values), default=0.0)
    max_ratio = max((value / (L**envelope_power) for L, value in values if L > 0), default=0.0)
    return {
        "family": family,
        "quantity": quantity,
        "order": str(order),
        "slope_estimate": f"{slope_estimate(values):.6g}",
        "max_observed": f"{max_observed:.12g}",
        "envelope_power": str(envelope_power),
        "max_envelope_ratio": f"{max_ratio:.12g}",
        "notes": notes,
    }


def build_summary_rows() -> list[dict[str, str]]:
    coeff_rows = load_csv(COEFF_CSV)
    log_rows = load_csv(LOG_CSV)
    profile_rows = load_csv(GROWING_SUMMARY_CSV)

    available_profiles = {
        (row["family"], int(row["L"])): (int(row["V"]), parse_counts(row["constraint_counts"]))
        for row in profile_rows
    }
    rows: list[dict[str, str]] = []
    for family in SELECTED_FAMILIES:
        for order in SELECTED_ORDERS:
            coeff_points: list[tuple[int, Fraction]] = []
            deriv_points: list[tuple[int, Fraction]] = []
            for row in coeff_rows:
                if row["family"] == family and int(row["order"]) == order:
                    coeff_points.append((int(row["L"]), parse_fraction(row["abs_coefficient"])))
                    deriv_points.append((int(row["L"]), abs(parse_fraction(row["derivative_at_zero"]))))
            rows.append(
                summarize_quantity(
                    family,
                    "ordinary_coefficient",
                    order,
                    coeff_points,
                    2 * order,
                    "fixed-order Bell-partition envelope",
                )
            )
            rows.append(
                summarize_quantity(
                    family,
                    "derivative_at_zero",
                    order,
                    deriv_points,
                    2 * order,
                    "same envelope up to the fixed factor order!",
                )
            )
            log_points: list[tuple[int, Fraction]] = []
            for row in log_rows:
                if row["family"] == family and int(row["log_coeff_order"]) == order:
                    log_points.append((int(row["L"]), parse_fraction(row["abs_log_coefficient"])))
            if log_points:
                rows.append(
                    summarize_quantity(
                        family,
                        "log_coefficient",
                        order,
                        log_points,
                        order + 1,
                        "power-sum envelope from support size and max index",
                    )
                )

        # Deterministic self-check rows are not written, but this raises on malformed Cycle 15 data.
        for L in (1, 5, 20, 40):
            key = (family, L)
            if key in available_profiles:
                V, counts = available_profiles[key]
                numerator, denominator = supports_from_profile(V, counts)
                for order in (1, 2, 4):
                    _ = log_coefficient_from_supports(numerator, denominator, order)
    return rows


def write_summary(rows: list[dict[str, str]], path: Path = OUT_CSV) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "family",
        "quantity",
        "order",
        "slope_estimate",
        "max_observed",
        "envelope_power",
        "max_envelope_ratio",
        "notes",
    ]
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def plot_summary(rows: list[dict[str, str]], path: Path = FIG) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    selected = [
        row
        for row in rows
        if row["family"] in SELECTED_FAMILIES
        and row["order"] in {"2", "4", "8"}
        and row["quantity"] in {"ordinary_coefficient", "log_coefficient"}
    ]
    labels = [f"{row['family'].replace('_profile', '')}\n{row['quantity'].replace('_', ' ')}, k={row['order']}" for row in selected]
    slopes = [float(row["slope_estimate"]) for row in selected]
    powers = [float(row["envelope_power"]) for row in selected]
    ratios = [max(float(row["max_envelope_ratio"]), 1e-30) for row in selected]

    fig, axes = plt.subplots(2, 1, figsize=(12, 8), constrained_layout=True)
    x = list(range(len(selected)))
    axes[0].bar(x, slopes, color="#4c78a8", label="estimated slope")
    axes[0].scatter(x, powers, color="#d62728", marker="_", s=180, label="envelope power")
    axes[0].set_ylabel("log-log slope in L")
    axes[0].set_title("Observed fixed-order coefficient/log-coefficient growth versus deterministic envelopes")
    axes[0].grid(True, axis="y", alpha=0.25)
    axes[0].legend(fontsize=8)
    axes[0].set_xticks(x)
    axes[0].set_xticklabels([])

    axes[1].bar(x, ratios, color="#59a14f")
    axes[1].set_yscale("log")
    axes[1].set_ylabel("max observed / L^power")
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(labels, rotation=55, ha="right", fontsize=7)
    axes[1].grid(True, axis="y", alpha=0.25)
    axes[1].set_xlabel("Cycle 15 family and quantity")
    fig.text(
        0.01,
        0.01,
        "Caption: observed fixed-order coefficient/log-coefficient growth for Cycle 15 families compared with deterministic L-power envelopes.",
        fontsize=8,
    )
    fig.savefig(path, dpi=180)
    plt.close(fig)


def main() -> None:
    rows = build_summary_rows()
    write_summary(rows)
    plot_summary(rows)
    print(f"wrote {OUT_CSV}")
    print(f"wrote {FIG}")
    print(f"summary_rows={len(rows)}")


if __name__ == "__main__":
    main()
