# created: 2026-05-16T01:30:00Z
# cycle: 15
# run_id: run-2026-05-15T153635Z
# agent: worker
# milestone: M5-extension-candidates
"""Generate and plot growing labelled-template expansion diagnostics."""

from __future__ import annotations

import csv
import math
from fractions import Fraction
from pathlib import Path

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
COEFF_CSV = ROOT / "data/extension_candidates/growing_template_expansion_coefficients.csv"
SUMMARY_CSV = ROOT / "data/extension_candidates/growing_template_expansion_summary.csv"
FIG_COEFF = ROOT / "reports/figures/m5_growing_template_coefficient_growth.png"
FIG_DERIV = ROOT / "reports/figures/m5_growing_template_derivative_growth.png"
FIG_RADIUS = ROOT / "reports/figures/m5_growing_template_radius_proxy.png"
MAX_L = 40
MAX_ORDER = 8


def multiply_truncated(a: list[Fraction], b: list[Fraction]) -> list[Fraction]:
    return [sum(a[i] * b[r - i] for i in range(r + 1)) for r in range(MAX_ORDER + 1)]


def factor_coefficients(j: int) -> list[Fraction]:
    return [Fraction(1), Fraction(-j)] + [Fraction(0)] * (MAX_ORDER - 1)


def inverse_factor_coefficients(j: int) -> list[Fraction]:
    return [Fraction(j) ** r for r in range(MAX_ORDER + 1)]


def profile_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for L in range(1, MAX_L + 1):
        rows.append(
            {
                "family": "single_label_cycle_profile",
                "L": L,
                "V": L,
                "constraint_counts": [L],
                "description": "V=L and one label with L constraints; normalized expectation is exactly 1",
            }
        )
        rows.append(
            {
                "family": "single_label_path_profile",
                "L": L,
                "V": L + 1,
                "constraint_counts": [L],
                "description": "V=L+1 and one label with L constraints; normalized expectation is exactly 1-L x",
            }
        )
        rows.append(
            {
                "family": "rank2_balanced_profile",
                "L": L,
                "V": 2 * L - 1,
                "constraint_counts": [L, L],
                "description": "two length-L labels sharing one vertex",
            }
        )
        for k in (2, 3):
            if 2 * L - k >= 1:
                rows.append(
                    {
                        "family": f"rank2_deficit_k{k}",
                        "L": L,
                        "V": 2 * L - k,
                        "constraint_counts": [L, L],
                        "description": f"two length-L labels with fixed vertex deficit k={k}",
                    }
                )
        for s in (3, 4):
            if 4 * L - s >= 1:
                rows.append(
                    {
                        "family": f"rank4_delocalization_toy_s{s}",
                        "L": L,
                        "V": 4 * L - s,
                        "constraint_counts": [L, L, L, L],
                        "description": f"four-label fourth-moment toy profile with fixed deficit s={s}",
                    }
                )
    return rows


def coefficients_for_profile(V: int, counts: list[int]) -> list[Fraction]:
    coeffs = [Fraction(1)] + [Fraction(0)] * MAX_ORDER
    for j in range(1, V):
        coeffs = multiply_truncated(coeffs, factor_coefficients(j))
    for count in counts:
        for j in range(1, count):
            coeffs = multiply_truncated(coeffs, inverse_factor_coefficients(j))
    return coeffs


def normalized_expression_n(V: int, counts: list[int]) -> str:
    count_text = "*".join(f"(n)_{c}" for c in counts) or "1"
    return f"n^({sum(counts) - V})*(n)_{V}/({count_text})"


def nearest_scale(family: str, V: int, counts: list[int]) -> str:
    if family == "single_label_cycle_profile":
        return ""
    max_raw = max([V - 1] + [c - 1 for c in counts])
    return "" if max_raw <= 0 else str(Fraction(1, max_raw))


def format_fraction(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def parse_fraction(text: str) -> Fraction:
    text = str(text).strip()
    if not text or text.lower() == "nan":
        return Fraction(0)
    return Fraction(text)


def write_expansion_csvs(coeff_path: Path = COEFF_CSV, summary_path: Path = SUMMARY_CSV) -> None:
    coeff_path.parent.mkdir(parents=True, exist_ok=True)
    profiles = profile_rows()
    coeff_fields = [
        "family",
        "L",
        "V",
        "constraint_counts",
        "order",
        "coefficient",
        "abs_coefficient",
        "derivative_at_zero",
        "coefficient_l1_norm_order_leq_8",
        "nearest_singularity_scale",
        "normalized_expression_n",
        "description",
    ]
    summary_fields = [
        "family",
        "L",
        "V",
        "constraint_counts",
        "constraint_total",
        "coefficient_l1_norm_order_leq_8",
        "max_abs_coefficient_order_leq_8",
        "max_abs_derivative_order_leq_8",
        "nearest_singularity_scale",
        "normalized_expression_n",
        "description",
    ]

    coeff_rows: list[dict[str, object]] = []
    summary_rows: list[dict[str, object]] = []
    for profile in profiles:
        family = str(profile["family"])
        L = int(profile["L"])
        V = int(profile["V"])
        counts = list(profile["constraint_counts"])
        coeffs = coefficients_for_profile(V, counts)
        l1 = sum(abs(c) for c in coeffs)
        derivatives = [math.factorial(r) * coeffs[r] for r in range(MAX_ORDER + 1)]
        count_text = ";".join(str(c) for c in counts)
        radius = nearest_scale(family, V, counts)
        expr = normalized_expression_n(V, counts)
        for order, coeff in enumerate(coeffs):
            coeff_rows.append(
                {
                    "family": family,
                    "L": L,
                    "V": V,
                    "constraint_counts": count_text,
                    "order": order,
                    "coefficient": format_fraction(coeff),
                    "abs_coefficient": format_fraction(abs(coeff)),
                    "derivative_at_zero": format_fraction(derivatives[order]),
                    "coefficient_l1_norm_order_leq_8": format_fraction(l1),
                    "nearest_singularity_scale": radius,
                    "normalized_expression_n": expr,
                    "description": profile["description"],
                }
            )
        summary_rows.append(
            {
                "family": family,
                "L": L,
                "V": V,
                "constraint_counts": count_text,
                "constraint_total": sum(counts),
                "coefficient_l1_norm_order_leq_8": format_fraction(l1),
                "max_abs_coefficient_order_leq_8": format_fraction(max(abs(c) for c in coeffs)),
                "max_abs_derivative_order_leq_8": format_fraction(max(abs(d) for d in derivatives)),
                "nearest_singularity_scale": radius,
                "normalized_expression_n": expr,
                "description": profile["description"],
            }
        )

    with coeff_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=coeff_fields)
        writer.writeheader()
        writer.writerows(coeff_rows)
    with summary_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=summary_fields)
        writer.writeheader()
        writer.writerows(summary_rows)


def load_coefficients() -> list[dict[str, object]]:
    if not COEFF_CSV.exists() or not SUMMARY_CSV.exists():
        write_expansion_csvs()
    rows: list[dict[str, object]] = []
    with COEFF_CSV.open(newline="") as f:
        for row in csv.DictReader(f):
            parsed: dict[str, object] = dict(row)
            parsed["L"] = int(row["L"])
            parsed["V"] = int(row["V"])
            parsed["order"] = int(row["order"])
            for col in ["coefficient", "abs_coefficient", "derivative_at_zero", "coefficient_l1_norm_order_leq_8"]:
                parsed[col + "_float"] = float(parse_fraction(row[col]))
            parsed["nearest_singularity_scale_float"] = (
                float(parse_fraction(row["nearest_singularity_scale"]))
                if row["nearest_singularity_scale"]
                else math.nan
            )
            rows.append(parsed)
    return rows


def group_by(rows: list[dict[str, object]], key: str) -> dict[str, list[dict[str, object]]]:
    grouped: dict[str, list[dict[str, object]]] = {}
    for row in rows:
        grouped.setdefault(str(row[key]), []).append(row)
    return grouped


def plot_coefficient_growth(rows: list[dict[str, object]]) -> None:
    FIG_COEFF.parent.mkdir(parents=True, exist_ok=True)
    summary = [row for row in rows if row["order"] == 0]
    fig, ax = plt.subplots(figsize=(8, 5), constrained_layout=True)
    for family, group in group_by(summary, "family").items():
        group = sorted(group, key=lambda row: int(row["L"]))
        if family == "single_label_cycle_profile":
            style = {"lw": 1.4, "ls": "--", "alpha": 0.8}
        else:
            style = {"lw": 1.8, "alpha": 0.9}
        ax.plot(
            [row["L"] for row in group],
            [row["coefficient_l1_norm_order_leq_8_float"] for row in group],
            label=family,
            **style,
        )
    ax.set_yscale("log")
    ax.set_xlabel("template size L")
    ax.set_ylabel("L1 norm of coefficients through order 8")
    ax.set_title("Growing-template coefficient growth")
    ax.grid(True, alpha=0.25)
    ax.legend(fontsize=7, ncol=2)
    fig.savefig(FIG_COEFF, dpi=180)
    plt.close(fig)


def plot_derivative_growth(rows: list[dict[str, object]]) -> None:
    FIG_DERIV.parent.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(12, 5), constrained_layout=True)
    selected = [
        "single_label_path_profile",
        "rank2_balanced_profile",
        "rank2_deficit_k3",
        "rank4_delocalization_toy_s4",
    ]
    for order in (1, 2, 4, 8):
        ax = axes[0]
        for family in selected:
            group = sorted(
                [row for row in rows if row["family"] == family and row["order"] == order],
                key=lambda row: int(row["L"]),
            )
            if group:
                ax.plot(
                    [row["L"] for row in group],
                    [abs(float(row["derivative_at_zero_float"])) for row in group],
                    label=f"{family}, r={order}",
                )
    axes[0].set_yscale("log")
    axes[0].set_xlabel("template size L")
    axes[0].set_ylabel("|N^(r)(0)|")
    axes[0].set_title("Derivative growth by profile")
    axes[0].grid(True, alpha=0.25)
    axes[0].legend(fontsize=6)

    order8 = [row for row in rows if row["order"] == 8 and row["family"] in selected]
    for family, group in group_by(order8, "family").items():
        group = sorted(group, key=lambda row: int(row["L"]))
        axes[1].plot(
            [row["L"] for row in group],
            [abs(float(row["derivative_at_zero_float"])) for row in group],
            label=family,
        )
    positive_L = sorted({int(row["L"]) for row in order8})
    if positive_L:
        ref_L = [float(value) for value in positive_L]
        y0 = max(
            [
                abs(float(row["derivative_at_zero_float"]))
                for row in order8
                if int(row["L"]) == max(positive_L)
            ]
            + [1.0]
        )
        scale = y0 / (max(positive_L) ** 16)
        axes[1].plot(ref_L, [scale * value**16 for value in ref_L], color="black", ls=":", label="reference L^(2r), r=8")
    axes[1].set_yscale("log")
    axes[1].set_xlabel("template size L")
    axes[1].set_ylabel("|N^(8)(0)|")
    axes[1].set_title("Order-8 derivative versus Markov-type scale")
    axes[1].grid(True, alpha=0.25)
    axes[1].legend(fontsize=7)
    fig.savefig(FIG_DERIV, dpi=180)
    plt.close(fig)


def plot_radius_proxy(rows: list[dict[str, object]]) -> None:
    FIG_RADIUS.parent.mkdir(parents=True, exist_ok=True)
    summary = [
        row for row in rows
        if row["order"] == 0 and not math.isnan(float(row["nearest_singularity_scale_float"]))
    ]
    fig, ax = plt.subplots(figsize=(8, 5), constrained_layout=True)
    for family, group in group_by(summary, "family").items():
        group = sorted(group, key=lambda row: int(row["L"]))
        ax.plot(
            [row["L"] for row in group],
            [row["nearest_singularity_scale_float"] for row in group],
            label=family,
        )
    Ls = [float(value) for value in sorted({int(row["L"]) for row in summary})]
    if Ls:
        ax.plot(Ls, [1 / value for value in Ls], color="black", ls=":", label="reference 1/L")
    ax.set_yscale("log")
    ax.set_xscale("log")
    ax.set_xlabel("template size L")
    ax.set_ylabel("nearest falling-factorial zero/pole scale")
    ax.set_title("Radius proxy shrinks with growing profiles")
    ax.grid(True, alpha=0.25)
    ax.legend(fontsize=7, ncol=2)
    fig.savefig(FIG_RADIUS, dpi=180)
    plt.close(fig)


def main() -> None:
    write_expansion_csvs()
    rows = load_coefficients()
    plot_coefficient_growth(rows)
    plot_derivative_growth(rows)
    plot_radius_proxy(rows)
    print(f"wrote {COEFF_CSV}")
    print(f"wrote {SUMMARY_CSV}")
    print(f"wrote {FIG_COEFF}")
    print(f"wrote {FIG_DERIV}")
    print(f"wrote {FIG_RADIUS}")


if __name__ == "__main__":
    main()
