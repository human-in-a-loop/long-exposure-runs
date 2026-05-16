# created: 2026-05-16T02:35:00Z
# cycle: 16
# run_id: run-2026-05-15T153635Z
# agent: worker
# milestone: M5-extension-candidates
"""Build the M5 closure index, log-coefficient summary, and synthesis figure."""

from __future__ import annotations

import csv
import math
from fractions import Fraction
from pathlib import Path

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
FIXED_COEFFS = ROOT / "data/extension_candidates/labelled_embedding_expansion_coefficients.csv"
GROWING_SUMMARY = ROOT / "data/extension_candidates/growing_template_expansion_summary.csv"
INDEX_CSV = ROOT / "data/extension_candidates/m5_extension_synthesis_index.csv"
LOG_CSV = ROOT / "data/extension_candidates/m5_log_coefficient_summary.csv"
FIGURE = ROOT / "reports/figures/m5_fixed_vs_growing_template_mechanism.png"


KEY_ARTIFACTS = [
    (13, "scripts/score_m5_extension_candidates.py", "script", "candidate ranking rubric and matrix", "ranked evidence only, not a theorem"),
    (13, "data/extension_candidates/m5_candidate_scores.csv", "data", "seven extension candidates scored", "scores are structured judgment calls"),
    (13, "reports/figures/m5_extension_candidate_matrix.png", "figure", "candidate ranking visualization", "visual summary only"),
    (13, "reports/extension_candidates/m5_extension_candidate_ranking.md", "report", "Markov/interpolation-loss path selected", "does not prove exponent improvement"),
    (13, "reports/extension_candidates/m5_primary_candidate_statement.md", "report", "primary template-expansion candidate stated", "conjectural bridge to Kim--Tao"),
    (14, "scripts/derive_labelled_embedding_expansions.wls", "script", "fixed-template symbolic expansion generator", "Wolfram currently blocked by license in later cycle"),
    (14, "scripts/compare_expansions_to_cycle9.py", "script", "fixed expansions compared to Cycle 9 fits", "comparison limited to fitted templates"),
    (14, "tests/test_labelled_embedding_expansions.py", "test", "fixed-template controls and truncation tested", "finite template scope"),
    (14, "data/extension_candidates/labelled_embedding_expansion_coefficients.csv", "data", "exact fixed-template coefficients through x^4", "fixed profiles only"),
    (14, "data/extension_candidates/labelled_embedding_expansion_fit_comparison.csv", "data", "Cycle 9 comparison table", "not a new empirical sample"),
    (14, "reports/figures/m5_expansion_vs_cycle9_fits.png", "figure", "fixed expansion versus polynomial-window fits", "visualizes selected benchmark pair"),
    (14, "reports/extension_candidates/m5_falling_factorial_expansion_test.md", "report", "fixed-template analyticity/stability result", "does not cover growing support"),
    (15, "scripts/probe_growing_template_expansions.wls", "script", "Wolfram growing-template generator source", "not runnable here due expired license"),
    (15, "scripts/plot_growing_template_expansions.py", "script", "exact Python growing-profile generator", "profile-level count model"),
    (15, "tests/test_growing_template_expansions.py", "test", "cycle/path exact identities and truncation tested", "finite order through 8"),
    (15, "data/extension_candidates/growing_template_expansion_coefficients.csv", "data", "growing-profile coefficients through order 8", "controlled profiles only"),
    (15, "data/extension_candidates/growing_template_expansion_summary.csv", "data", "growing-profile coefficient/radius summary", "radius proxy from product factors"),
    (15, "reports/figures/m5_growing_template_coefficient_growth.png", "figure", "coefficient growth visualization", "descriptive, not asymptotic proof"),
    (15, "reports/figures/m5_growing_template_derivative_growth.png", "figure", "derivative growth visualization", "finite L range"),
    (15, "reports/figures/m5_growing_template_radius_proxy.png", "figure", "shrinking singularity proxy", "product-ratio proxy"),
    (15, "reports/extension_candidates/m5_growing_template_expansion_growth.md", "report", "growing-template amplification result", "toy/profile level"),
    (16, "scripts/plot_m5_extension_synthesis.py", "script", "M5 closure index/log/figure generator", "synthesis only"),
    (16, "data/extension_candidates/m5_extension_synthesis_index.csv", "data", "M5 artifact dependency index", "path-existence audit only"),
    (16, "data/extension_candidates/m5_log_coefficient_summary.csv", "data", "log-coefficient mechanism summary", "orders 1-4 only"),
    (16, "reports/figures/m5_fixed_vs_growing_template_mechanism.png", "figure", "fixed versus growing mechanism comparison", "compact visualization"),
    (16, "reports/extension_candidates/m5_extension_synthesis_and_toy_principle.md", "report", "final M5 toy principle synthesis", "not a Kim--Tao theorem"),
]


def parse_fraction(text: str) -> Fraction:
    text = str(text).strip()
    if not text:
        return Fraction(0)
    return Fraction(text)


def write_index() -> None:
    INDEX_CSV.parent.mkdir(parents=True, exist_ok=True)
    fields = ["cycle", "artifact", "artifact_type", "claim_supported", "scope_limit", "exists"]
    with INDEX_CSV.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for cycle, artifact, artifact_type, claim, scope in KEY_ARTIFACTS:
            writer.writerow(
                {
                    "cycle": cycle,
                    "artifact": artifact,
                    "artifact_type": artifact_type,
                    "claim_supported": claim,
                    "scope_limit": scope,
                    "exists": str((ROOT / artifact).exists()).lower(),
                }
            )


def fixed_coefficients() -> dict[str, list[float]]:
    rows: dict[str, list[float]] = {}
    with FIXED_COEFFS.open(newline="") as f:
        for row in csv.DictReader(f):
            rows[row["template"]] = [abs(float(parse_fraction(row[f"coeff_{i}"]))) for i in range(5)]
    return rows


def load_growing_summary() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    with GROWING_SUMMARY.open(newline="") as f:
        for row in csv.DictReader(f):
            parsed: dict[str, object] = dict(row)
            parsed["L"] = int(row["L"])
            parsed["V"] = int(row["V"])
            parsed["constraint_counts_list"] = [int(x) for x in row["constraint_counts"].split(";") if x]
            parsed["l1_float"] = float(parse_fraction(row["coefficient_l1_norm_order_leq_8"]))
            parsed["derivative_float"] = float(parse_fraction(row["max_abs_derivative_order_leq_8"]))
            parsed["radius_float"] = float(parse_fraction(row["nearest_singularity_scale"])) if row["nearest_singularity_scale"] else math.nan
            rows.append(parsed)
    return rows


def power_sum(limit: int, order: int) -> int:
    return sum(j**order for j in range(1, limit))


def log_coefficients(V: int, counts: list[int], max_order: int = 4) -> list[Fraction]:
    coeffs: list[Fraction] = []
    for order in range(1, max_order + 1):
        numerator = sum(power_sum(c, order) for c in counts) - power_sum(V, order)
        coeffs.append(Fraction(numerator, order))
    return coeffs


def write_log_summary(rows: list[dict[str, object]]) -> None:
    LOG_CSV.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "family",
        "L",
        "V",
        "constraint_counts",
        "log_coeff_order",
        "log_coefficient",
        "abs_log_coefficient",
        "nearest_singularity_scale",
        "mechanism_note",
    ]
    selected = {
        "single_label_cycle_profile",
        "single_label_path_profile",
        "rank2_balanced_profile",
        "rank2_deficit_k3",
        "rank4_delocalization_toy_s4",
    }
    with LOG_CSV.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            if row["family"] not in selected:
                continue
            coeffs = log_coefficients(int(row["V"]), list(row["constraint_counts_list"]))
            for order, coeff in enumerate(coeffs, start=1):
                writer.writerow(
                    {
                        "family": row["family"],
                        "L": row["L"],
                        "V": row["V"],
                        "constraint_counts": row["constraint_counts"],
                        "log_coeff_order": order,
                        "log_coefficient": str(coeff.numerator) if coeff.denominator == 1 else f"{coeff.numerator}/{coeff.denominator}",
                        "abs_log_coefficient": str(abs(coeff.numerator)) if coeff.denominator == 1 else f"{abs(coeff.numerator)}/{coeff.denominator}",
                        "nearest_singularity_scale": row["nearest_singularity_scale"],
                        "mechanism_note": "sum_B j^r - sum_A j^r over indices up to O(L)",
                    }
                )


def grouped(rows: list[dict[str, object]], family: str) -> list[dict[str, object]]:
    return sorted([row for row in rows if row["family"] == family], key=lambda row: int(row["L"]))


def plot_figure(fixed: dict[str, list[float]], growing: list[dict[str, object]]) -> None:
    FIGURE.parent.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 3, figsize=(13.5, 4.2), constrained_layout=True)

    ax = axes[0]
    fixed_names = ["eight_word_cyclic_toy", "eight_word_rank2_toy", "trace_pair_toy"]
    offsets = [-0.22, 0.0, 0.22]
    orders = [1, 2, 3, 4]
    for name, offset in zip(fixed_names, offsets):
        values = fixed[name][1:5]
        ax.bar([order + offset for order in orders], values, width=0.2, label=name)
    ax.set_yscale("symlog", linthresh=1)
    ax.set_xticks(orders)
    ax.set_xlabel("Taylor order")
    ax.set_ylabel("|fixed coefficient|")
    ax.set_title("Fixed templates stay finite")
    ax.legend(fontsize=7)

    ax = axes[1]
    for family in ["single_label_path_profile", "rank2_balanced_profile", "rank4_delocalization_toy_s4"]:
        group = grouped(growing, family)
        ax.plot([row["L"] for row in group], [row["l1_float"] for row in group], label=family, lw=1.8)
    ax.set_yscale("log")
    ax.set_xlabel("profile size L")
    ax.set_ylabel("L1 norm of coefficients through order 8")
    ax.set_title("Growing profiles amplify coefficients")
    ax.legend(fontsize=7)

    ax = axes[2]
    for family in ["single_label_path_profile", "rank2_balanced_profile", "rank4_delocalization_toy_s4"]:
        group = [row for row in grouped(growing, family) if not math.isnan(float(row["radius_float"]))]
        ax.plot([row["L"] for row in group], [row["radius_float"] for row in group], label=family, lw=1.8)
    ax.set_yscale("log")
    ax.set_xlabel("profile size L")
    ax.set_ylabel("nearest zero/pole scale in x")
    ax.set_title("Radius proxy shrinks like 1/L")
    ax.legend(fontsize=7)

    fig.suptitle("M5 mechanism: fixed-template stability versus growing-template singularity drift", fontsize=12)
    fig.savefig(FIGURE, dpi=180)
    plt.close(fig)


def main() -> None:
    fixed = fixed_coefficients()
    growing = load_growing_summary()
    write_log_summary(growing)
    plot_figure(fixed, growing)
    write_index()
    missing = []
    with INDEX_CSV.open(newline="") as f:
        for row in csv.DictReader(f):
            if row["exists"] != "true" and row["artifact"] != "reports/extension_candidates/m5_extension_synthesis_and_toy_principle.md":
                missing.append(row["artifact"])
    print(f"wrote {INDEX_CSV.relative_to(ROOT)}")
    print(f"wrote {LOG_CSV.relative_to(ROOT)}")
    print(f"wrote {FIGURE.relative_to(ROOT)}")
    print(f"indexed_artifacts={len(KEY_ARTIFACTS)}")
    print(f"missing_existing_dependencies={len(missing)}")
    if missing:
        for path in missing:
            print(path)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
