# created: 2026-05-16T18:20:00Z
# cycle: 34
# run_id: run-2026-05-15T153635Z
# agent: worker
# milestone: M23-localized-trace-numerator-quotient-family-model
"""Proxy budget model for localized Corollary 3.4 numerator strata.

This script does not enumerate Kim--Tao surface-group quotients. It builds a
bounded, reproducible schema whose rows are anchored to the paper's variables
(gamma_1, gamma_2, k_1, k_2, transform support, and Q_{gamma_1^k_1,gamma_2^k_2})
and whose quotient annotations are explicit proxies.
"""

from __future__ import annotations

import csv
import math
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
TERMS_CSV = ROOT / "data/extension_candidates/localized_trace_numerator_quotient_terms.csv"
SUMMARY_CSV = ROOT / "data/extension_candidates/localized_trace_numerator_strata_summary.csv"
TAXONOMY_CSV = ROOT / "data/extension_candidates/localized_trace_numerator_weight_taxonomy.csv"
TV_FIG = ROOT / "reports/figures/m23_localized_quotient_strata_tv.png"
GROWTH_FIG = ROOT / "reports/figures/m23_transform_weight_vs_family_growth.png"

SUPPORT_Q = 12.0
MAX_WORD_LENGTH = 10
MAX_PRIMITIVE_POWER = 4
GENUS_PROXY = 2
ENTROPY_PROXY = 0.72


def selberg_geodesic_weight(length: float, exponent: int) -> float:
    t = length * exponent
    return length / (2.0 * math.sinh(t / 2.0))


def transform_weight(model: str, t: float, support_q: float = SUPPORT_Q) -> float:
    if t > support_q:
        return 0.0
    if model == "compact_support":
        return 1.0
    envelope = math.exp(-((t / support_q) ** 2))
    if model == "paley_wiener_scaled":
        return envelope
    if model == "optimistic_decay":
        return envelope * math.exp(-0.18 * t)
    raise ValueError(model)


def quotient_tag(length1: int, length2: int, k1: int, k2: int) -> str:
    if length1 == length2 and k1 == k2:
        return "identity/diagonal"
    if length1 == length2 or (length1 % length2 == 0) or (length2 % length1 == 0):
        return "cyclic"
    if math.gcd(length1, length2) == 1:
        return "rank_two_noncyclic"
    return "unknown_surface_group"


def rank_proxy(tag: str) -> str:
    if tag == "identity/diagonal":
        return "rank_zero_diagonal"
    if tag == "cyclic":
        return "rank_one_cyclic"
    if tag == "rank_two_noncyclic":
        return "rank_two_noncyclic"
    return "surface_group_law_unknown"


def d_proxy(length1: int, length2: int, tag: str) -> tuple[int, int, int]:
    if tag == "identity/diagonal":
        vertices = max(length1, length2)
        constraints = vertices
    elif tag == "cyclic":
        vertices = length1 + length2 - math.gcd(length1, length2)
        constraints = length1 + length2
    elif tag == "rank_two_noncyclic":
        vertices = length1 + length2 - 1
        constraints = length1 + length2
    else:
        vertices = length1 + length2 - math.gcd(length1, length2) // 2
        constraints = length1 + length2 + 1
    return constraints, vertices, constraints - vertices


def family_growth_proxy(length1: int, length2: int, tag: str) -> float:
    base = math.exp(ENTROPY_PROXY * (length1 + length2))
    if tag == "identity/diagonal":
        return 1.0
    if tag == "cyclic":
        return max(1.0, 0.12 * base / (length1 + length2))
    if tag == "rank_two_noncyclic":
        return base
    return 1.75 * base


def polynomial_variation_proxy(d_value: int, tag: str) -> float:
    tag_factor = {
        "identity/diagonal": 0.0,
        "cyclic": 0.35,
        "rank_two_noncyclic": 1.0,
        "unknown_surface_group": 1.4,
    }[tag]
    return tag_factor * (1.0 + max(d_value, 0)) ** 2


def coverage_status(tag: str) -> tuple[str, str]:
    if tag == "identity/diagonal":
        return "partial_M4_M12", "deterministic/diagonal separated; not a new numerator saving"
    if tag == "cyclic":
        return "partial_M4_M12", "cyclic skeleton analogous to earlier toy rows; surface law still not exact"
    if tag == "rank_two_noncyclic":
        return "partial_M9_M15_obstruction", "expected bottleneck; independent-permutation skeleton only"
    return "unknown_surface_group", "not counted as M4-certified because surface-group quotient law is unresolved"


def build_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    models = ["compact_support", "paley_wiener_scaled", "optimistic_decay"]
    for length1 in range(1, MAX_WORD_LENGTH + 1):
        for length2 in range(1, MAX_WORD_LENGTH + 1):
            for k1 in range(1, MAX_PRIMITIVE_POWER + 1):
                for k2 in range(1, MAX_PRIMITIVE_POWER + 1):
                    t1 = length1 * k1
                    t2 = length2 * k2
                    tag = quotient_tag(length1, length2, k1, k2)
                    constraints, vertices, d_value = d_proxy(length1, length2, tag)
                    coverage, note = coverage_status(tag)
                    primitive_mult = 1.0 / (k1 * k2)
                    geo = selberg_geodesic_weight(length1, k1) * selberg_geodesic_weight(length2, k2)
                    growth = family_growth_proxy(length1, length2, tag)
                    q_var = polynomial_variation_proxy(d_value, tag)
                    for model in models:
                        tw1 = transform_weight(model, t1)
                        tw2 = transform_weight(model, t2)
                        support_valid = tw1 > 0.0 and tw2 > 0.0
                        weighted_tv = geo * primitive_mult * tw1 * tw2 * growth * q_var
                        rows.append(
                            {
                                "gamma1_proxy": f"primitive_length_{length1}",
                                "gamma2_proxy": f"primitive_length_{length2}",
                                "primitive_exponent_k1": k1,
                                "primitive_exponent_k2": k2,
                                "length_bin_1": length1,
                                "length_bin_2": length2,
                                "support_argument_1": t1,
                                "support_argument_2": t2,
                                "transform_model": model,
                                "support_q": SUPPORT_Q,
                                "support_valid": support_valid,
                                "geodesic_weight_proxy": geo,
                                "primitive_power_multiplicity_proxy": primitive_mult,
                                "transform_weight_1": tw1,
                                "transform_weight_2": tw2,
                                "diagonal_subtraction_status": "diagonal_separated" if tag == "identity/diagonal" else "non_diagonal_remainder",
                                "quotient_control_tag": tag,
                                "quotient_identifier_proxy": f"{tag}|L{length1}_{length2}|k{k1}_{k2}",
                                "rank_proxy": rank_proxy(tag),
                                "cyclic_flag": tag in {"identity/diagonal", "cyclic"},
                                "C_constraints_proxy": constraints,
                                "V_vertices_proxy": vertices,
                                "d_C_minus_V": d_value,
                                "family_growth_proxy": growth,
                                "Q_numerator_type": f"Q_gamma1^{k1}_gamma2^{k2}",
                                "polynomial_variation_proxy": q_var,
                                "weighted_total_variation_proxy": weighted_tv,
                                "coverage_by_M4_M12": coverage,
                                "exact_or_proxy": "paper_indices_exact; weights_and_quotient_fields_proxy",
                                "notes": note,
                            }
                        )
    return rows


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def summarize(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[tuple[str, str, int], list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        if row["support_valid"]:
            grouped[(str(row["transform_model"]), str(row["quotient_control_tag"]), int(row["d_C_minus_V"]))].append(row)
    out: list[dict[str, object]] = []
    for (model, tag, d_value), items in sorted(grouped.items()):
        out.append(
            {
                "transform_model": model,
                "quotient_control_tag": tag,
                "d_C_minus_V": d_value,
                "rows": len(items),
                "total_weighted_tv_proxy": sum(float(r["weighted_total_variation_proxy"]) for r in items),
                "total_family_growth_proxy": sum(float(r["family_growth_proxy"]) for r in items),
                "mean_transform_product": sum(float(r["transform_weight_1"]) * float(r["transform_weight_2"]) for r in items) / len(items),
                "M4_certified_rows": sum(1 for r in items if r["coverage_by_M4_M12"] == "M4_certified"),
                "unknown_surface_group_rows": sum(1 for r in items if r["coverage_by_M4_M12"] == "unknown_surface_group"),
            }
        )
    return out


def taxonomy_rows() -> list[dict[str, str]]:
    return [
        {"field": "gamma_i, k_i", "kind": "exact Kim--Tao summation index", "meaning": "primitive geodesic gamma_i and primitive-power exponent k_i in Corollary 3.4"},
        {"field": "ell_gamma/(2sinh(k ell_gamma/2))", "kind": "paper weight", "meaning": "Selberg geometric weight from Lemma 2.1 and Corollary 3.4"},
        {"field": "(h o f_Lambda0)^vee(k ell_gamma)", "kind": "paper weight with localized proxy", "meaning": "transform value; M23 compares compact support, Paley-Wiener envelope, and optimistic decay"},
        {"field": "Q_{gamma1^k1,gamma2^k2}", "kind": "paper polynomial numerator", "meaning": "Lemma 3.3/Corollary 3.4 random-cover rational numerator"},
        {"field": "quotient_control_tag", "kind": "proxy annotation", "meaning": "identity/diagonal, cyclic, rank-two noncyclic, or unknown surface-group-law bucket"},
        {"field": "d_C_minus_V", "kind": "proxy annotation", "meaning": "template power analogue C-V preserved as a summary stratum"},
        {"field": "coverage_by_M4_M12", "kind": "internal coverage annotation", "meaning": "unknown_surface_group rows are explicitly not M4-certified"},
    ]


def plot_tv(summary_rows: list[dict[str, object]]) -> None:
    TV_FIG.parent.mkdir(parents=True, exist_ok=True)
    models = ["compact_support", "paley_wiener_scaled", "optimistic_decay"]
    tags = ["identity/diagonal", "cyclic", "rank_two_noncyclic", "unknown_surface_group"]
    fig, axes = plt.subplots(1, 3, figsize=(14, 4.8), sharey=True, constrained_layout=True)
    for ax, model in zip(axes, models):
        values = []
        labels = []
        for tag in tags:
            total = sum(float(r["total_weighted_tv_proxy"]) for r in summary_rows if r["transform_model"] == model and r["quotient_control_tag"] == tag)
            values.append(max(total, 1e-12))
            labels.append(tag.replace("_", "\n"))
        ax.bar(labels, values, color=["#4c78a8", "#f28e2b", "#e15759", "#76b7b2"])
        ax.set_yscale("log")
        ax.set_title(model)
        ax.tick_params(axis="x", labelrotation=25)
        ax.grid(True, axis="y", which="both", alpha=0.25)
    axes[0].set_ylabel("weighted total variation proxy")
    fig.suptitle("M23 localized numerator stratum budget")
    fig.text(0.01, 0.01, "Caption: total-variation proxy by localized numerator stratum and transform-weight model.", fontsize=8)
    fig.savefig(TV_FIG, dpi=160)
    plt.close(fig)


def plot_growth(rows: list[dict[str, object]]) -> None:
    GROWTH_FIG.parent.mkdir(parents=True, exist_ok=True)
    models = ["compact_support", "paley_wiener_scaled", "optimistic_decay"]
    bins = sorted({int(r["support_argument_1"]) + int(r["support_argument_2"]) for r in rows if r["support_valid"]})
    fig, ax = plt.subplots(figsize=(9, 5.5), constrained_layout=True)
    growth_by_bin = []
    for b in bins:
        growth_by_bin.append(sum(float(r["family_growth_proxy"]) for r in rows if r["transform_model"] == "compact_support" and r["support_valid"] and int(r["support_argument_1"]) + int(r["support_argument_2"]) == b))
    ax.plot(bins, growth_by_bin, marker="o", color="#333333", label="family growth proxy")
    for model, color in zip(models, ["#4c78a8", "#f28e2b", "#e15759"]):
        values = []
        for b in bins:
            values.append(sum(float(r["weighted_total_variation_proxy"]) for r in rows if r["transform_model"] == model and r["support_valid"] and int(r["support_argument_1"]) + int(r["support_argument_2"]) == b))
        ax.plot(bins, [max(v, 1e-12) for v in values], marker="s", label=model, color=color)
    ax.set_yscale("log")
    ax.set_xlabel("support bin k1*ell1 + k2*ell2")
    ax.set_ylabel("proxy mass")
    ax.set_title("Transform damping versus quotient-family growth")
    ax.grid(True, which="both", alpha=0.25)
    ax.legend(fontsize=8)
    fig.text(0.01, 0.01, "Caption: comparison of localized transform damping against quotient-family growth proxies across support bins.", fontsize=8)
    fig.savefig(GROWTH_FIG, dpi=160)
    plt.close(fig)


def main() -> None:
    rows = build_rows()
    summary_rows = summarize(rows)
    write_csv(TERMS_CSV, rows)
    write_csv(SUMMARY_CSV, summary_rows)
    write_csv(TAXONOMY_CSV, taxonomy_rows())
    plot_tv(summary_rows)
    plot_growth(rows)
    print(f"wrote {len(rows)} rows to {TERMS_CSV}")
    print(f"wrote {len(summary_rows)} summary rows to {SUMMARY_CSV}")
    print(f"wrote taxonomy to {TAXONOMY_CSV}")
    print(f"wrote figures {TV_FIG} and {GROWTH_FIG}")


if __name__ == "__main__":
    main()
