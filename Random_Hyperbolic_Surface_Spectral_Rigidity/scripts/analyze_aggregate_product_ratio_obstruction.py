# created: 2026-05-16T07:05:00Z
# cycle: 20
# run_id: run-2026-05-15T153635Z
# agent: worker
# milestone: M9-aggregate-product-ratio-obstruction
"""Generate deterministic aggregate product-ratio obstruction examples."""

from __future__ import annotations

import csv
import math
from fractions import Fraction
from pathlib import Path

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
OUT_CSV = ROOT / "data/extension_candidates/aggregate_product_ratio_obstruction.csv"
REQ_CSV = ROOT / "data/extension_candidates/aggregate_bridge_requirements.csv"
FIG = ROOT / "reports/figures/m9_aggregate_obstruction.png"
L_VALUES = range(2, 41)
COEFFICIENT_ORDER = 1


def path_profile_coefficient(L: int, order: int = COEFFICIENT_ORDER) -> Fraction:
    """Coefficient of x^order in N_L(x)=prod_{j=1}^{L}(1-jx)/prod_{j=1}^{L-1}(1-jx)."""
    if order == 0:
        return Fraction(1)
    if order == 1:
        return Fraction(-L)
    return Fraction(0)


def family_specs(L: int) -> list[dict[str, Fraction | int | str]]:
    base = path_profile_coefficient(L)
    return [
        {
            "family": "single_template_path",
            "template_count": 1,
            "weight_l1": Fraction(1),
            "aggregate_coefficient": base,
            "notes": "one tame path profile; direct per-template control",
        },
        {
            "family": "polynomial_count_path",
            "template_count": L**2,
            "weight_l1": Fraction(L**2),
            "aggregate_coefficient": (L**2) * base,
            "notes": "L^2 positive copies; polynomial count shifts degree by 2",
        },
        {
            "family": "exponential_count_path",
            "template_count": 2**L,
            "weight_l1": Fraction(2**L),
            "aggregate_coefficient": (2**L) * base,
            "notes": "2^L positive copies; per-template bound survives but aggregate grows exponentially",
        },
        {
            "family": "signed_cancelled_pair",
            "template_count": 2,
            "weight_l1": Fraction(2),
            "aggregate_coefficient": Fraction(0),
            "notes": "two identical profiles with weights +1 and -1; cancellation is extra information",
        },
        {
            "family": "rank_decay_toy",
            "template_count": 2**L,
            "weight_l1": Fraction(1),
            "aggregate_coefficient": base,
            "notes": "2^L copies with weight 2^-L each; decay offsets family growth",
        },
        {
            "family": "polynomial_decay_toy_s2",
            "template_count": 2**L,
            "weight_l1": Fraction(2**L, L**2),
            "aggregate_coefficient": Fraction(2**L, L**2) * base,
            "notes": "2^L copies with only L^-2 decay; polynomial decay does not offset exponential count",
        },
    ]


def frac_text(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def build_obstruction_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for L in L_VALUES:
        per_template_bound = L ** (2 * COEFFICIENT_ORDER)
        for spec in family_specs(L):
            weight_l1 = spec["weight_l1"]
            aggregate_bound = Fraction(per_template_bound) * weight_l1
            rows.append(
                {
                    "family": str(spec["family"]),
                    "L": str(L),
                    "template_count": str(spec["template_count"]),
                    "weight_l1": frac_text(weight_l1),
                    "coefficient_order": str(COEFFICIENT_ORDER),
                    "aggregate_coefficient": frac_text(spec["aggregate_coefficient"]),
                    "per_template_bound_proxy": str(per_template_bound),
                    "aggregate_bound_proxy": frac_text(aggregate_bound),
                    "notes": str(spec["notes"]),
                }
            )
    return rows


def build_requirement_rows() -> list[dict[str, str]]:
    return [
        {
            "requirement": "per-template product-ratio envelope",
            "what_it_controls": "fixed-order coefficient size for each isolated normalized template",
            "sufficient_for_polynomial_aggregate": "no",
            "present_in_m7": "yes",
            "needed_for_kim_tao_bridge": "yes, but not alone",
            "notes": "M7 gives the summand bound C_k L^{2k}; aggregation introduces sum |w_T| or cancellation.",
        },
        {
            "requirement": "polynomial family-count control",
            "what_it_controls": "number of positive or absolute-weighted templates at support scale L",
            "sufficient_for_polynomial_aggregate": "yes, with bounded weights",
            "present_in_m7": "no",
            "needed_for_kim_tao_bridge": "yes",
            "notes": "Without it, 2^L tame templates give exponential aggregate coefficients.",
        },
        {
            "requirement": "polynomial total variation of weights",
            "what_it_controls": "sum_T |w_T| in the weighted quotient-family sum",
            "sufficient_for_polynomial_aggregate": "yes",
            "present_in_m7": "no",
            "needed_for_kim_tao_bridge": "yes or replaced by cancellation/decay",
            "notes": "The conditional lemma is exactly linear in this quantity.",
        },
        {
            "requirement": "signed cancellation",
            "what_it_controls": "coherent cancellation between large positive and negative weighted template contributions",
            "sufficient_for_polynomial_aggregate": "yes, if proved at coefficient level",
            "present_in_m7": "no",
            "needed_for_kim_tao_bridge": "possibly",
            "notes": "The signed pair example cancels exactly despite nonzero total variation.",
        },
        {
            "requirement": "rank-sensitive decay",
            "what_it_controls": "extra probability decay attached to high-rank/noncyclic quotient families",
            "sufficient_for_polynomial_aggregate": "yes, if it offsets family growth",
            "present_in_m7": "no",
            "needed_for_kim_tao_bridge": "yes",
            "notes": "This is the conceptual role of MP23-type rank-two common-fixed-point input.",
        },
        {
            "requirement": "denominator and boundedness control",
            "what_it_controls": "Q_id normalization, negative-power cancellation, and analytic boundedness of full polynomial estimates",
            "sufficient_for_polynomial_aggregate": "not by itself",
            "present_in_m7": "no",
            "needed_for_kim_tao_bridge": "yes",
            "notes": "M8 identified this as part of the MPvH/Witten-zeta/Nau layer outside isolated product ratios.",
        },
    ]


def write_csv(rows: list[dict[str, str]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def signed_abs_int(text: str) -> int:
    return abs(int(Fraction(text)))


def plot_rows(rows: list[dict[str, str]], path: Path = FIG) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    families = [
        "single_template_path",
        "polynomial_count_path",
        "exponential_count_path",
        "signed_cancelled_pair",
        "rank_decay_toy",
        "polynomial_decay_toy_s2",
    ]
    colors = {
        "single_template_path": "#4c78a8",
        "polynomial_count_path": "#59a14f",
        "exponential_count_path": "#e15759",
        "signed_cancelled_pair": "#b07aa1",
        "rank_decay_toy": "#f28e2b",
        "polynomial_decay_toy_s2": "#8cd17d",
    }
    fig, ax = plt.subplots(figsize=(10, 6), constrained_layout=True)
    for family in families:
        points = [row for row in rows if row["family"] == family]
        xs = [int(row["L"]) for row in points]
        ys = [max(signed_abs_int(row["aggregate_coefficient"]), 1e-12) for row in points]
        ax.plot(xs, ys, label=family.replace("_", " "), color=colors[family], linewidth=2)
    ax.plot(list(L_VALUES), [L**3 for L in L_VALUES], "--", color="#333333", linewidth=1, label="L^3 reference")
    ax.set_yscale("log")
    ax.set_xlabel("support/profile scale L")
    ax.set_ylabel("|coefficient of x| in aggregate")
    ax.set_title("Aggregate growth is controlled by family weights, not per-template envelopes alone")
    ax.grid(True, which="both", alpha=0.25)
    ax.legend(fontsize=8)
    fig.text(
        0.01,
        0.01,
        "Caption: aggregate coefficient growth under polynomial family count, exponential family count, exact cancellation, and rank-decay toy weighting.",
        fontsize=8,
    )
    fig.savefig(path, dpi=160)
    plt.close(fig)


def main() -> None:
    obstruction_rows = build_obstruction_rows()
    requirement_rows = build_requirement_rows()
    write_csv(obstruction_rows, OUT_CSV)
    write_csv(requirement_rows, REQ_CSV)
    plot_rows(obstruction_rows, FIG)
    print(f"wrote {OUT_CSV}")
    print(f"wrote {REQ_CSV}")
    print(f"wrote {FIG}")
    for family in sorted({row["family"] for row in obstruction_rows}):
        last = [row for row in obstruction_rows if row["family"] == family and row["L"] == "40"][0]
        print(f"{family}: L=40 coefficient {last['aggregate_coefficient']}, weight_l1 {last['weight_l1']}")


if __name__ == "__main__":
    main()
