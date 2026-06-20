# created: 2026-05-16T11:05:00Z
# cycle: 24
# run_id: run-2026-05-15T153635Z
# agent: worker
# milestone: M13-cancellation-mechanism-diagnostics
"""Diagnose coefficient cancellation mechanisms in the M11 trace-like toy family."""

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


COEFF_CSV = ROOT / "data/extension_candidates/cancellation_coefficient_summary.csv"
GROUP_CSV = ROOT / "data/extension_candidates/cancellation_group_summary.csv"
PAIRING_CSV = ROOT / "data/extension_candidates/cancellation_candidate_pairings.csv"
RATIO_FIG = ROOT / "reports/figures/m13_cancellation_ratios.png"
HEATMAP_FIG = ROOT / "reports/figures/m13_grouped_cancellation_heatmap.png"
BOUND_FIG = ROOT / "reports/figures/m13_bound_mode_comparison.png"

VARIANTS = [
    "all_conflict_free",
    "primitive_non_diagonal",
    "diagonal_cyclic_only",
    "signed_diagonal_subtracted_proxy",
    "rank_two_noncyclic_remainder",
]
WEIGHT_SCHEMES = ["weight_unweighted", "weight_exp_decay_theta_0_5", "weight_length_inverse"]
MAX_ORDER = 4


def num_text(value: float) -> str:
    if abs(value) < 1e-12:
        value = 0.0
    if math.isnan(value):
        return ""
    return f"{value:.12g}"


def n_power(record: m11.PairRecord) -> int:
    return record.skeleton.count_a + record.skeleton.count_b - record.skeleton.vertex_count


def coefficient(record: m11.PairRecord, order: int) -> float:
    return float(m11.profile_coefficients(record.skeleton)[order])


def cyclic_proxy(record: m11.PairRecord) -> str:
    if record.rank_label == "rank_one":
        return "cyclic_proxy_yes"
    degree: dict[int, int] = defaultdict(int)
    for source, _, target in record.skeleton.edges:
        degree[source] += 1
        degree[target] += 1
    if degree and all(value == 2 for value in degree.values()):
        return "cyclic_proxy_yes"
    return "cyclic_proxy_no"


def sign(value: float) -> str:
    if value > 0:
        return "+"
    if value < 0:
        return "-"
    return "0"


def sign_vector(record: m11.PairRecord) -> str:
    return "".join(sign(coefficient(record, order)) for order in range(1, MAX_ORDER + 1))


def primitive_status(record: m11.PairRecord) -> str:
    u_power = record.u.primitive_power_exponent > 1
    v_power = record.v.primitive_power_exponent > 1
    diag = record.diagonal_cyclic
    return f"u_power={int(u_power)}|v_power={int(v_power)}|diagonal={int(diag)}"


def group_value(record: m11.PairRecord, rule: str) -> str:
    if rule == "length_pair":
        return f"{record.u.length},{record.v.length}"
    if rule == "rank_cyclic_proxy":
        return f"{record.rank_label}|{cyclic_proxy(record)}"
    if rule == "primitive_diagonal_status":
        return primitive_status(record)
    if rule == "folded_profile_key":
        return record.skeleton.key
    if rule == "coefficient_sign_vector":
        return sign_vector(record)
    raise ValueError(rule)


def summarize_terms(terms: list[tuple[m11.PairRecord, float, float]], L: int, order: int) -> dict[str, float]:
    signed_sum = sum(weight * coeff for _, weight, coeff in terms)
    coeff_abs_variation = sum(abs(weight * coeff) for _, weight, coeff in terms)
    tv = sum(abs(weight) for _, weight, _ in terms)
    bound = (L ** (2 * order)) * tv
    rho = abs(signed_sum) / coeff_abs_variation if coeff_abs_variation > 0 else math.nan
    theorem_ratio = abs(signed_sum) / max(1.0, bound)
    av_ratio = abs(signed_sum) / max(1.0, coeff_abs_variation)
    return {
        "signed_sum": signed_sum,
        "coeff_abs_variation": coeff_abs_variation,
        "weight_l1": tv,
        "m12_tv_bound_proxy": bound,
        "cancellation_ratio": rho,
        "theorem_bound_ratio": theorem_ratio,
        "absolute_variation_bound_ratio": av_ratio,
    }


def iter_terms(records: list[m11.PairRecord], variant: str, scheme: str, L: int, d: int, order: int) -> list[tuple[m11.PairRecord, float, float]]:
    out = []
    for record in records:
        if record.L != L or n_power(record) != d or not m11.record_in_variant(record, variant):
            continue
        out.append((record, m11.pair_weights(record)[scheme], coefficient(record, order)))
    return out


def build_coefficient_rows(records: list[m11.PairRecord]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    keys = sorted(
        {
            (record.L, variant, scheme, n_power(record), order)
            for record in records
            for variant in VARIANTS
            if m11.record_in_variant(record, variant)
            for scheme in WEIGHT_SCHEMES
            for order in range(1, MAX_ORDER + 1)
        }
    )
    for L, variant, scheme, d, order in keys:
        terms = iter_terms(records, variant, scheme, L, d, order)
        if not terms:
            continue
        stats = summarize_terms(terms, L, order)
        signed_bound = abs(stats["signed_sum"])
        rows.append(
            {
                "L": str(L),
                "variant": variant,
                "weight_scheme": scheme,
                "n_power": str(d),
                "coefficient_order": str(order),
                "num_terms": str(len(terms)),
                "num_profiles": str(len({record.skeleton.key for record, _, _ in terms})),
                "signed_coefficient_sum": num_text(stats["signed_sum"]),
                "coefficient_absolute_variation": num_text(stats["coeff_abs_variation"]),
                "weight_l1": num_text(stats["weight_l1"]),
                "m12_tv_bound_proxy": num_text(stats["m12_tv_bound_proxy"]),
                "absolute_variation_bound_proxy": num_text(stats["coeff_abs_variation"]),
                "signed_bound_proxy": num_text(signed_bound),
                "cancellation_ratio": num_text(stats["cancellation_ratio"]),
                "theorem_bound_ratio": num_text(stats["theorem_bound_ratio"]),
                "absolute_variation_bound_ratio": num_text(stats["absolute_variation_bound_ratio"]),
                "zero_av": "yes" if stats["coeff_abs_variation"] == 0 else "no",
                "notes": "record-level M11 terms grouped by fixed d=C-V before cancellation diagnostics",
            }
        )
    return rows


def build_group_rows(records: list[m11.PairRecord]) -> list[dict[str, str]]:
    grouping_rules = [
        "length_pair",
        "rank_cyclic_proxy",
        "primitive_diagonal_status",
        "folded_profile_key",
        "coefficient_sign_vector",
    ]
    grouped: dict[tuple[str, str, int, str, str, int, int], list[tuple[m11.PairRecord, float, float]]] = defaultdict(list)
    for record in records:
        for variant in VARIANTS:
            if not m11.record_in_variant(record, variant):
                continue
            for scheme in WEIGHT_SCHEMES:
                weight = m11.pair_weights(record)[scheme]
                for order in range(1, MAX_ORDER + 1):
                    coeff = coefficient(record, order)
                    for rule in grouping_rules:
                        key = (rule, group_value(record, rule), record.L, variant, scheme, n_power(record), order)
                        grouped[key].append((record, weight, coeff))

    rows: list[dict[str, str]] = []
    for (rule, value, L, variant, scheme, d, order), terms in sorted(grouped.items()):
        stats = summarize_terms(terms, L, order)
        signs = sorted({sign(coeff) for _, _, coeff in terms})
        rows.append(
            {
                "grouping_rule": rule,
                "group_key": value,
                "L": str(L),
                "variant": variant,
                "weight_scheme": scheme,
                "n_power": str(d),
                "coefficient_order": str(order),
                "coefficient_signs_present": "".join(signs),
                "num_terms": str(len(terms)),
                "num_profiles": str(len({record.skeleton.key for record, _, _ in terms})),
                "signed_coefficient_sum": num_text(stats["signed_sum"]),
                "coefficient_absolute_variation": num_text(stats["coeff_abs_variation"]),
                "weight_l1": num_text(stats["weight_l1"]),
                "cancellation_ratio": num_text(stats["cancellation_ratio"]),
                "notes": "group rows refine ungrouped fixed-stratum signed sums",
            }
        )
    return rows


def build_pairing_rows(records: list[m11.PairRecord]) -> list[dict[str, str]]:
    # A candidate is a structural cell containing both positive and negative terms for the same coefficient order.
    cells: dict[tuple[str, str, int, int, str], list[tuple[m11.PairRecord, float, float]]] = defaultdict(list)
    for record in records:
        if not m11.record_in_variant(record, "rank_two_noncyclic_remainder"):
            continue
        structure = f"length={record.u.length},{record.v.length}|rank={record.rank_label}|primitive={primitive_status(record)}"
        for scheme in WEIGHT_SCHEMES:
            weight = m11.pair_weights(record)[scheme]
            for order in range(1, MAX_ORDER + 1):
                cells[(scheme, structure, n_power(record), order, sign(coefficient(record, order)))].append((record, weight, coefficient(record, order)))

    by_base: dict[tuple[str, str, int, int], dict[str, list[tuple[m11.PairRecord, float, float]]]] = defaultdict(dict)
    for (scheme, structure, d, order, coeff_sign), terms in cells.items():
        by_base[(scheme, structure, d, order)][coeff_sign] = terms

    rows: list[dict[str, str]] = []
    persistent_keys = {
        key
        for key, by_sign in by_base.items()
        if "+" in by_sign and "-" in by_sign and {3, 4, 5} <= {record.L for terms in by_sign.values() for record, _, _ in terms}
    }
    for key, by_sign in sorted(by_base.items()):
        if "+" not in by_sign or "-" not in by_sign:
            continue
        scheme, structure, d, order = key
        terms = by_sign["+"] + by_sign["-"]
        stats = summarize_terms(terms, max(record.L for record, _, _ in terms), order)
        l_values = sorted({record.L for record, _, _ in terms})
        rows.append(
            {
                "weight_scheme": scheme,
                "structure_key": structure,
                "n_power": str(d),
                "coefficient_order": str(order),
                "L_values": ";".join(str(value) for value in l_values),
                "positive_terms": str(len(by_sign["+"])),
                "negative_terms": str(len(by_sign["-"])),
                "positive_abs_variation": num_text(sum(abs(weight * coeff) for _, weight, coeff in by_sign["+"])),
                "negative_abs_variation": num_text(sum(abs(weight * coeff) for _, weight, coeff in by_sign["-"])),
                "combined_signed_sum": num_text(stats["signed_sum"]),
                "combined_abs_variation": num_text(stats["coeff_abs_variation"]),
                "combined_cancellation_ratio": num_text(stats["cancellation_ratio"]),
                "persists_L3_L4_L5": "yes" if key in persistent_keys else "no",
                "notes": "rank-two remainder structural cells with both coefficient signs",
            }
        )
    if not rows:
        rows.append(
            {
                "weight_scheme": "none",
                "structure_key": "no opposite-sign structural pairings found",
                "n_power": "",
                "coefficient_order": "",
                "L_values": "",
                "positive_terms": "0",
                "negative_terms": "0",
                "positive_abs_variation": "0",
                "negative_abs_variation": "0",
                "combined_signed_sum": "0",
                "combined_abs_variation": "0",
                "combined_cancellation_ratio": "",
                "persists_L3_L4_L5": "no",
                "notes": "all tested structural cells were one-sided in coefficient sign",
            }
        )
    return rows


def write_csv(rows: list[dict[str, str]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def plot_cancellation_ratios(rows: list[dict[str, str]]) -> None:
    RATIO_FIG.parent.mkdir(parents=True, exist_ok=True)
    selected = [
        row
        for row in rows
        if row["weight_scheme"] == "weight_unweighted"
        and row["n_power"] == "1"
        and row["variant"] in {"all_conflict_free", "signed_diagonal_subtracted_proxy", "rank_two_noncyclic_remainder"}
        and row["zero_av"] == "no"
    ]
    fig, axes = plt.subplots(2, 2, figsize=(11, 8), sharex=True, sharey=True, constrained_layout=True)
    colors = {"all_conflict_free": "#4c78a8", "signed_diagonal_subtracted_proxy": "#e15759", "rank_two_noncyclic_remainder": "#59a14f"}
    for order, ax in zip(range(1, MAX_ORDER + 1), axes.ravel()):
        for variant, color in colors.items():
            points = [row for row in selected if row["variant"] == variant and row["coefficient_order"] == str(order)]
            xs = [int(row["L"]) for row in points]
            ys = [float(row["cancellation_ratio"]) for row in points]
            ax.plot(xs, ys, marker="o", linewidth=2, label=variant.replace("_", " "), color=color)
        ax.set_title(f"k={order}")
        ax.set_xlabel("length cutoff L")
        ax.set_ylabel("rho = |S| / AV")
        ax.set_ylim(-0.05, 1.05)
        ax.grid(True, alpha=0.25)
    axes[0, 0].legend(fontsize=8)
    fig.suptitle("M13 dominant-stratum cancellation ratios")
    fig.text(0.01, 0.01, "Caption: cancellation ratios rho=|signed coefficient sum|/coefficient absolute variation in the unweighted d=1 stratum.", fontsize=8)
    fig.savefig(RATIO_FIG, dpi=160)
    plt.close(fig)


def plot_group_heatmap(group_rows: list[dict[str, str]]) -> None:
    HEATMAP_FIG.parent.mkdir(parents=True, exist_ok=True)
    rules = ["length_pair", "rank_cyclic_proxy", "primitive_diagonal_status", "folded_profile_key", "coefficient_sign_vector"]
    data = []
    for rule in rules:
        line = []
        for order in range(1, MAX_ORDER + 1):
            rows = [
                row
                for row in group_rows
                if row["grouping_rule"] == rule
                and row["L"] == "5"
                and row["variant"] == "rank_two_noncyclic_remainder"
                and row["weight_scheme"] == "weight_unweighted"
                and row["n_power"] == "1"
                and row["coefficient_order"] == str(order)
                and row["coefficient_absolute_variation"] not in {"", "0"}
            ]
            av = sum(float(row["coefficient_absolute_variation"]) for row in rows)
            weighted_rho = sum(float(row["cancellation_ratio"] or 0) * float(row["coefficient_absolute_variation"]) for row in rows) / av if av else 0.0
            line.append(weighted_rho)
        data.append(line)
    fig, ax = plt.subplots(figsize=(8.5, 4.8), constrained_layout=True)
    image = ax.imshow(data, vmin=0, vmax=1, cmap="viridis")
    ax.set_xticks(range(MAX_ORDER), [f"k={order}" for order in range(1, MAX_ORDER + 1)])
    ax.set_yticks(range(len(rules)), [rule.replace("_", " ") for rule in rules])
    for y, line in enumerate(data):
        for x, value in enumerate(line):
            ax.text(x, y, f"{value:.2f}", ha="center", va="center", color="white" if value < 0.5 else "black", fontsize=9)
    ax.set_title("Grouped cancellation after structural refinement")
    fig.colorbar(image, ax=ax, label="AV-weighted mean group rho")
    fig.text(0.01, 0.01, "Caption: AV-weighted cancellation ratios by grouping rule in the L=5 unweighted d=1 rank-two remainder; 1 means no within-cell sign cancellation.", fontsize=8)
    fig.savefig(HEATMAP_FIG, dpi=160)
    plt.close(fig)


def plot_bound_modes(rows: list[dict[str, str]]) -> None:
    BOUND_FIG.parent.mkdir(parents=True, exist_ok=True)
    selected = [
        row
        for row in rows
        if row["variant"] == "rank_two_noncyclic_remainder"
        and row["n_power"] == "1"
        and row["coefficient_order"] == "1"
        and row["weight_scheme"] in WEIGHT_SCHEMES
    ]
    fig, ax = plt.subplots(figsize=(9.5, 5.5), constrained_layout=True)
    colors = {"weight_unweighted": "#4c78a8", "weight_exp_decay_theta_0_5": "#59a14f", "weight_length_inverse": "#e15759"}
    for scheme, color in colors.items():
        points = [row for row in selected if row["weight_scheme"] == scheme]
        xs = [int(row["L"]) for row in points]
        ax.plot(xs, [float(row["m12_tv_bound_proxy"]) for row in points], linestyle="--", marker="o", color=color, alpha=0.45, label=f"{scheme} TV bound")
        ax.plot(xs, [float(row["coefficient_absolute_variation"]) for row in points], linestyle=":", marker="s", color=color, alpha=0.8, label=f"{scheme} AV")
        ax.plot(xs, [abs(float(row["signed_coefficient_sum"])) for row in points], linestyle="-", marker="^", color=color, label=f"{scheme} signed")
    ax.set_yscale("symlog", linthresh=1)
    ax.set_xlabel("length cutoff L")
    ax.set_ylabel("bound or coefficient magnitude")
    ax.set_title("Bound modes in the dominant d=1 rank-two remainder, k=1")
    ax.grid(True, alpha=0.25)
    ax.legend(fontsize=7, ncol=2)
    fig.text(0.01, 0.01, "Caption: TV-controlled M12 proxy, coefficient absolute variation, and signed coefficient magnitude for length/rank weighted modes in the dominant stratum.", fontsize=8)
    fig.savefig(BOUND_FIG, dpi=160)
    plt.close(fig)


def main() -> None:
    records = m11.build_pair_records()
    coeff_rows = build_coefficient_rows(records)
    group_rows = build_group_rows(records)
    pairing_rows = build_pairing_rows(records)
    write_csv(coeff_rows, COEFF_CSV)
    write_csv(group_rows, GROUP_CSV)
    write_csv(pairing_rows, PAIRING_CSV)
    plot_cancellation_ratios(coeff_rows)
    plot_group_heatmap(group_rows)
    plot_bound_modes(coeff_rows)
    dominant = [
        row
        for row in coeff_rows
        if row["L"] == "5" and row["variant"] == "rank_two_noncyclic_remainder" and row["weight_scheme"] == "weight_unweighted" and row["n_power"] == "1"
    ]
    print(f"wrote {COEFF_CSV}")
    print(f"wrote {GROUP_CSV}")
    print(f"wrote {PAIRING_CSV}")
    print(f"wrote {RATIO_FIG}")
    print(f"wrote {HEATMAP_FIG}")
    print(f"wrote {BOUND_FIG}")
    for row in dominant:
        print(
            "L=5 rank_two d=1 "
            f"k={row['coefficient_order']} signed={row['signed_coefficient_sum']} "
            f"AV={row['coefficient_absolute_variation']} rho={row['cancellation_ratio']}"
        )


if __name__ == "__main__":
    main()
