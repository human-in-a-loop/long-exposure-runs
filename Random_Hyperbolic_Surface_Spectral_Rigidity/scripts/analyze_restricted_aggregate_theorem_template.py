# created: 2026-05-16T10:15:00Z
# cycle: 23
# run_id: run-2026-05-15T153635Z
# agent: worker
# milestone: M12-restricted-aggregate-theorem-template
"""Check the M12 restricted aggregate theorem template against M11 data."""

from __future__ import annotations

import csv
import math
import sys
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import enumerate_trace_like_weighted_quotients as m11  # noqa: E402


PROFILE_CSV = ROOT / "data/extension_candidates/trace_like_weighted_quotient_profiles.csv"
SUMMARY_CSV = ROOT / "data/extension_candidates/trace_like_weighted_quotient_summary.csv"
STRATA_CSV = ROOT / "data/extension_candidates/restricted_aggregate_theorem_strata.csv"
BOUND_CSV = ROOT / "data/extension_candidates/restricted_aggregate_theorem_bound_checks.csv"
TV_FIG = ROOT / "reports/figures/m12_stratified_total_variation.png"
RATIO_FIG = ROOT / "reports/figures/m12_coefficient_bound_ratios.png"

VARIANTS = [
    "all_conflict_free",
    "diagonal_cyclic_only",
    "signed_diagonal_subtracted_proxy",
    "rank_two_noncyclic_remainder",
]
WEIGHT_SCHEMES = ["weight_unweighted", "weight_exp_decay_theta_0_5", "weight_length_inverse"]
MAX_ORDER = 4


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def num_text(value: float) -> str:
    if abs(value) < 1e-12:
        value = 0.0
    return f"{value:.12g}"


def n_power(record: m11.PairRecord) -> int:
    return record.skeleton.count_a + record.skeleton.count_b - record.skeleton.vertex_count


def build_strata_rows(records: list[m11.PairRecord]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    by_key: dict[tuple[int, str, str, int], list[m11.PairRecord]] = defaultdict(list)
    for record in records:
        for variant in VARIANTS:
            if not m11.record_in_variant(record, variant):
                continue
            for scheme in WEIGHT_SCHEMES:
                by_key[(record.L, variant, scheme, n_power(record))].append(record)

    for (L, variant, scheme, d), items in sorted(by_key.items()):
        coeff_sums = []
        for order in range(1, MAX_ORDER + 1):
            total = 0.0
            for record in items:
                total += m11.pair_weights(record)[scheme] * float(m11.profile_coefficients(record.skeleton)[order])
            coeff_sums.append(total)
        rows.append(
            {
                "L": str(L),
                "variant": variant,
                "weight_scheme": scheme,
                "n_power": str(d),
                "num_profiles": str(len({record.skeleton.key for record in items})),
                "pair_classes": str(len(items)),
                "weight_l1": num_text(sum(abs(m11.pair_weights(record)[scheme]) for record in items)),
                "coeff_order_1": num_text(coeff_sums[0]),
                "coeff_order_2": num_text(coeff_sums[1]),
                "coeff_order_3": num_text(coeff_sums[2]),
                "coeff_order_4": num_text(coeff_sums[3]),
                "notes": "record-level M11 pair data grouped by d=C-V before coefficient aggregation",
            }
        )
    return rows


def build_bound_rows(strata_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for row in strata_rows:
        L = int(row["L"])
        tv = float(row["weight_l1"])
        for order in range(1, MAX_ORDER + 1):
            actual = float(row[f"coeff_order_{order}"])
            bound = (L ** (2 * order)) * tv
            ratio = abs(actual) / max(1.0, bound)
            rows.append(
                {
                    "L": row["L"],
                    "variant": row["variant"],
                    "weight_scheme": row["weight_scheme"],
                    "n_power": row["n_power"],
                    "coefficient_order": str(order),
                    "aggregate_coefficient": num_text(actual),
                    "tv_stratum": num_text(tv),
                    "m7_bound_proxy": str(L ** (2 * order)),
                    "weighted_stratum_bound_proxy": num_text(bound),
                    "empirical_ratio": num_text(ratio),
                    "notes": "ratio uses max(1, L^(2k) TV_{L,d}) to keep zero-TV strata finite",
                }
            )
    return rows


def write_csv(rows: list[dict[str, str]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def plot_tv(strata_rows: list[dict[str, str]]) -> None:
    TV_FIG.parent.mkdir(parents=True, exist_ok=True)
    selected = [
        row
        for row in strata_rows
        if row["weight_scheme"] == "weight_unweighted"
        and row["variant"] in {"all_conflict_free", "signed_diagonal_subtracted_proxy", "rank_two_noncyclic_remainder"}
    ]
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.8), sharey=True, constrained_layout=True)
    colors = {-1: "#59a14f", 0: "#4c78a8", 1: "#e15759", 2: "#f28e2b", 3: "#b07aa1"}
    for ax, variant in zip(axes, ["all_conflict_free", "signed_diagonal_subtracted_proxy", "rank_two_noncyclic_remainder"]):
        variant_rows = [row for row in selected if row["variant"] == variant]
        for d in sorted({int(row["n_power"]) for row in variant_rows}):
            points = [row for row in variant_rows if int(row["n_power"]) == d]
            ax.plot(
                [int(row["L"]) for row in points],
                [float(row["weight_l1"]) for row in points],
                marker="o",
                linewidth=2,
                color=colors.get(d, "#333333"),
                label=f"d={d}",
            )
        ax.set_title(variant.replace("_", " "))
        ax.set_xlabel("length cutoff L")
        ax.grid(True, alpha=0.25)
    axes[0].set_ylabel("unweighted TV by n_power stratum")
    axes[-1].legend(fontsize=8)
    fig.suptitle("M12 stratified total variation by d = C - V")
    fig.text(0.01, 0.01, "Caption: unweighted total variation split by n_power stratum for all conflict-free, diagonal-subtracted, and rank-two remainder variants.", fontsize=8)
    fig.savefig(TV_FIG, dpi=160)
    plt.close(fig)


def plot_ratios(bound_rows: list[dict[str, str]]) -> None:
    RATIO_FIG.parent.mkdir(parents=True, exist_ok=True)
    selected = [
        row
        for row in bound_rows
        if row["weight_scheme"] == "weight_unweighted"
        and row["variant"] in {"all_conflict_free", "signed_diagonal_subtracted_proxy", "rank_two_noncyclic_remainder"}
    ]
    fig, axes = plt.subplots(2, 2, figsize=(11, 8), sharex=True, sharey=True, constrained_layout=True)
    colors = {
        "all_conflict_free": "#4c78a8",
        "signed_diagonal_subtracted_proxy": "#e15759",
        "rank_two_noncyclic_remainder": "#59a14f",
    }
    for order, ax in zip(range(1, MAX_ORDER + 1), axes.ravel()):
        order_rows = [row for row in selected if int(row["coefficient_order"]) == order]
        for variant in colors:
            points = [row for row in order_rows if row["variant"] == variant]
            by_l: dict[int, float] = defaultdict(float)
            for row in points:
                by_l[int(row["L"])] = max(by_l[int(row["L"])], float(row["empirical_ratio"]))
            ax.plot(sorted(by_l), [by_l[L] for L in sorted(by_l)], marker="o", linewidth=2, label=variant.replace("_", " "), color=colors[variant])
        ax.set_title(f"k={order}")
        ax.set_xlabel("length cutoff L")
        ax.set_ylabel("max stratum ratio")
        ax.grid(True, alpha=0.25)
    axes[0, 0].legend(fontsize=8)
    fig.suptitle("M12 empirical coefficient-to-bound ratios")
    fig.text(0.01, 0.01, "Caption: empirical ratios |coefficient| / max(1, L^(2k) TV_{L,d}) by coefficient order, taking the maximum over n_power strata.", fontsize=8)
    fig.savefig(RATIO_FIG, dpi=160)
    plt.close(fig)


def validate_m11_inputs() -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    profile_rows = read_csv(PROFILE_CSV)
    summary_rows = read_csv(SUMMARY_CSV)
    required_profile = {"L", "canonical_key", "n_power", "conflict", "coeff_order_1", "weight_unweighted"}
    required_summary = {"L", "variant", "weight_scheme", "coefficient_order", "aggregate_coefficient", "weight_l1"}
    if not required_profile <= set(profile_rows[0]):
        raise ValueError("M11 profile CSV is missing required M12 columns")
    if not required_summary <= set(summary_rows[0]):
        raise ValueError("M11 summary CSV is missing required M12 columns")
    return profile_rows, summary_rows


def main() -> None:
    validate_m11_inputs()
    records = m11.build_pair_records()
    strata_rows = build_strata_rows(records)
    bound_rows = build_bound_rows(strata_rows)
    write_csv(strata_rows, STRATA_CSV)
    write_csv(bound_rows, BOUND_CSV)
    plot_tv(strata_rows)
    plot_ratios(bound_rows)
    max_ratio = max(float(row["empirical_ratio"]) for row in bound_rows if math.isfinite(float(row["empirical_ratio"])))
    print(f"wrote {STRATA_CSV}")
    print(f"wrote {BOUND_CSV}")
    print(f"wrote {TV_FIG}")
    print(f"wrote {RATIO_FIG}")
    print(f"max empirical_ratio {max_ratio:.6g}")


if __name__ == "__main__":
    main()
