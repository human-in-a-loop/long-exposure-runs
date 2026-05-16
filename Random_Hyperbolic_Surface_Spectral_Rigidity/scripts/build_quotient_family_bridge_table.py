# created: 2026-05-16T06:05:00Z
# cycle: 19
# run_id: run-2026-05-15T153635Z
# agent: worker
# milestone: M8-quotient-family-bridge

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
OUT_CSV = ROOT / "data/extension_candidates/quotient_family_bridge_table.csv"
OUT_PNG = ROOT / "reports/figures/m8_bridge_taxonomy.png"

FIELDNAMES = [
    "source",
    "paper_location",
    "object",
    "template_interpretation",
    "m4_applicability",
    "m7_applicability",
    "bridge_status",
    "main_obstruction",
    "supporting_artifact",
]

ROWS = [
    {
        "source": "M4/M7 baseline",
        "paper_location": "M4 and M7 artifacts, not a Kim--Tao paper object",
        "object": "single independent-permutation conflict-free labelled template",
        "template_interpretation": "A template sampled against independent uniform generator permutations.",
        "m4_applicability": "yes exactly: this is the model certified by the M4 labelled-template expectation identity",
        "m7_applicability": "yes exactly for normalized product-ratio families with controlled support",
        "bridge_status": "covered",
        "main_obstruction": "none inside the toy independent-permutation framework; the obstruction appears when moving to the surface-group random-cover law",
        "supporting_artifact": "reports/extension_candidates/m7_product_ratio_coefficient_bounds.md",
    },
    {
        "source": "Theorem 1 variance",
        "paper_location": "Lemma 3.3, local paper p.17-18",
        "object": "single folded quotient W_r from C_gamma1,gamma2",
        "template_interpretation": "A fixed conflict-free labelled quotient template with injective Schreier embedding constraints.",
        "m4_applicability": "partly: the constraint skeleton matches M4, but the actual expectation is over Hom(Gamma,S_n), not independent permutations",
        "m7_applicability": "partly for growing word-support profiles after the MPvH/Witten-zeta expansion exposes falling-factorial factors",
        "bridge_status": "partially_covered",
        "main_obstruction": "surface-group relation, Witten-zeta normalization, and MPvH embedding expansion are already present before summing many W_r",
        "supporting_artifact": "docs/proof_ledger/two_trace_expansion_ledger.md",
    },
    {
        "source": "Theorem 1 variance",
        "paper_location": "Lemma 3.3",
        "object": "finite sum over quotients R for fixed gamma_1,gamma_2",
        "template_interpretation": "Finite sum of injective quotient-template expectations.",
        "m4_applicability": "partly termwise: M4 covers the independent-permutation analogue of each quotient skeleton",
        "m7_applicability": "partly: each summand has product-ratio support, but the number and cancellation of quotients is external",
        "bridge_status": "partially_covered",
        "main_obstruction": "quotient-count growth up to factorial scale and Witten-zeta/Q_id normalization are not controlled by M7 alone",
        "supporting_artifact": "docs/proof_ledger/proposition31_internal_reconstruction.md",
    },
    {
        "source": "Theorem 1 variance",
        "paper_location": "Corollary 3.4",
        "object": "growing geodesic/word family polynomial p(1/n)",
        "template_interpretation": "Geometry-weighted sum of many two-cycle quotient polynomials Q_gamma1,gamma2.",
        "m4_applicability": "yes only after decomposing into individual quotient embeddings",
        "m7_applicability": "partly: per-template coefficient envelopes apply, not the full weighted sum",
        "bridge_status": "partially_covered",
        "main_obstruction": "geodesic coefficient weights, support-to-degree reduction, cancellations, and denominator Q_id remain outside M7",
        "supporting_artifact": "docs/proof_ledger/proposition31_internal_reconstruction.md",
    },
    {
        "source": "Theorem 1 variance",
        "paper_location": "Lemma 3.3 plus Nau boundedness",
        "object": "full Q_gamma1,gamma2(1/n)/Q_id(1/n) estimate",
        "template_interpretation": "Imported polynomial estimate after quotient summation and Witten-zeta normalization.",
        "m4_applicability": "not directly; M4 covers embedding summands, not the external boundedness step",
        "m7_applicability": "heuristic only: product-ratio language matches falling-factorial pieces but not the black-box denominator control",
        "bridge_status": "heuristic_only",
        "main_obstruction": "MPvH expansion and Nau boundedness hide denominator and negative-power cancellation mechanisms",
        "supporting_artifact": "docs/proof_ledger/two_trace_expansion_ledger.md",
    },
    {
        "source": "Theorem 1 variance",
        "paper_location": "§3.2 identity/diagonal handling",
        "object": "cyclic or diagonal two-trace pairs gamma_1^k1 = gamma_2^k2",
        "template_interpretation": "Special correlated quotient templates inside the same two-cycle formalism.",
        "m4_applicability": "partly termwise if the folded quotient is conflict-free; the surface-group expectation remains external",
        "m7_applicability": "partly: product-ratio control does not isolate their larger correlation contribution",
        "bridge_status": "partially_covered",
        "main_obstruction": "diagonal correlations are absorbed into p rather than separately enumerated and bounded",
        "supporting_artifact": "docs/proof_ledger/two_trace_expansion_ledger.md",
    },
    {
        "source": "Theorem 2 fourth moment",
        "paper_location": "Proposition 4.2 / equation (4.15)",
        "object": "single eight-loop quotient template C_gamma1,...,gamma8 -> W_r",
        "template_interpretation": "An injective labelled quotient template with a common base vertex and up to eight word loops.",
        "m4_applicability": "partly: the fixed quotient has M4-like labelled constraints, but its expectation is still under the surface-group homomorphism model",
        "m7_applicability": "partly for the exposed product-ratio profile; rank-two normalization and MP23 input are external",
        "bridge_status": "partially_covered",
        "main_obstruction": "the surface-group law and the MP23 rank-two replacement enter even for the polynomialized fixed eight-word expectation",
        "supporting_artifact": "docs/proof_ledger/eigenfunction_fourth_moment_ledger.md",
    },
    {
        "source": "Theorem 2 fourth moment",
        "paper_location": "§4.2 diagonal term S",
        "object": "cyclic primitive-power diagonal four-tuples subtracted by S",
        "template_interpretation": "Structured diagonal family removed before rank-two common-fixed-point control.",
        "m4_applicability": "partly for individual independent-permutation template skeletons, but not for the structural subtraction itself",
        "m7_applicability": "partly: product ratios describe terms, not the necessity or size of S",
        "bridge_status": "partially_covered",
        "main_obstruction": "S is a proof-level centering/diagonal subtraction, not just a product-ratio estimate",
        "supporting_artifact": "docs/proof_ledger/eigenfunction_fourth_moment_ledger.md",
    },
    {
        "source": "Theorem 2 fourth moment",
        "paper_location": "Proposition 4.2 / MP23 rank-two replacement",
        "object": "rank-two noncyclic remainder after diagonal removal",
        "template_interpretation": "Eight-word quotient families constrained by existence of two non-commensurable primitive directions.",
        "m4_applicability": "partly termwise for quotient-embedding skeletons",
        "m7_applicability": "heuristic only for the rank-two decay scale",
        "bridge_status": "heuristic_only",
        "main_obstruction": "MP23 common-fixed-point theorem supplies n^-2 decay; M7 does not prove rank-two subgroup fixed-point decay",
        "supporting_artifact": "docs/proof_ledger/eigenfunction_fourth_moment_ledger.md",
    },
    {
        "source": "Theorem 2 fourth moment",
        "paper_location": "Proposition 4.2 full polynomial approximation",
        "object": "p(1/n)/(n^2 Q_id(1/n)) for the eight-word statistic",
        "template_interpretation": "Weighted sum of eight-loop quotient polynomials plus denominator normalization.",
        "m4_applicability": "only termwise before summation",
        "m7_applicability": "partly: fixed-order per-template envelopes apply, not the centered fourth-moment statistic",
        "bridge_status": "partially_covered",
        "main_obstruction": "second-derivative Markov step, rank-two input, diagonal subtraction, and geometry weights are extra axes",
        "supporting_artifact": "docs/proof_ledger/eigenfunction_fourth_moment_ledger.md",
    },
    {
        "source": "Imported polynomial method",
        "paper_location": "MPvH/MP23 inputs invoked in §§3-4",
        "object": "full imported random-cover polynomial estimates",
        "template_interpretation": "Black-box estimates over quotient families, denominators, rank constraints, and cancellations.",
        "m4_applicability": "no as a whole",
        "m7_applicability": "no as a whole",
        "bridge_status": "not_covered",
        "main_obstruction": "the imported theorems prove aggregate boundedness/rank decay not derivable from isolated product-ratio envelopes",
        "supporting_artifact": "reports/final/final_report.md",
    },
]


def validate_supporting_paths(rows: list[dict[str, str]]) -> list[str]:
    missing = []
    for row in rows:
        path = ROOT / row["supporting_artifact"]
        if not path.exists():
            missing.append(row["supporting_artifact"])
    return missing


def write_csv(rows: list[dict[str, str]]) -> None:
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def plot_taxonomy(rows: list[dict[str, str]]) -> None:
    OUT_PNG.parent.mkdir(parents=True, exist_ok=True)
    statuses = ["covered", "partially_covered", "heuristic_only", "not_covered"]
    preferred_sources = ["M4/M7 baseline", "Theorem 1 variance", "Theorem 2 fourth moment", "Imported polynomial method"]
    seen_sources = [row["source"] for row in rows]
    sources = [source for source in preferred_sources if source in seen_sources]
    sources.extend(source for source in seen_sources if source not in sources)
    counts = {(source, status): 0 for source in sources for status in statuses}
    for row in rows:
        counts[(row["source"], row["bridge_status"])] += 1

    colors = {
        "covered": "#2f7d32",
        "partially_covered": "#d18b00",
        "heuristic_only": "#7b61a8",
        "not_covered": "#9a3d34",
    }
    fig, ax = plt.subplots(figsize=(10.5, 5.6))
    y_positions = range(len(sources))
    left = [0] * len(sources)
    for status in statuses:
        values = [counts[(source, status)] for source in sources]
        ax.barh(
            list(y_positions),
            values,
            left=left,
            color=colors[status],
            label=status.replace("_", " "),
            edgecolor="white",
        )
        for idx, value in enumerate(values):
            if value:
                ax.text(left[idx] + value / 2, idx, str(value), ha="center", va="center", color="white", fontsize=10)
        left = [left[idx] + values[idx] for idx in range(len(sources))]

    ax.set_yticks(list(y_positions), sources)
    ax.set_xlabel("number of classified objects")
    ax.set_title("M8 Bridge Taxonomy")
    ax.legend(loc="lower right", frameon=False, ncol=2)
    ax.grid(axis="x", alpha=0.25)
    ax.set_xlim(0, max(left) + 0.8)
    fig.text(
        0.01,
        0.02,
        "Caption: taxonomy of where the product-ratio framework attaches to Kim--Tao quotient/profile objects and where additional trace-expansion structure enters.",
        fontsize=9,
    )
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    fig.savefig(OUT_PNG, dpi=160)
    plt.close(fig)


def main() -> int:
    missing = validate_supporting_paths(ROWS)
    if missing:
        for path in missing:
            print(f"missing supporting artifact: {path}")
        return 1
    write_csv(ROWS)
    plot_taxonomy(ROWS)
    counts = Counter(row["bridge_status"] for row in ROWS)
    print(f"wrote {OUT_CSV}")
    print(f"wrote {OUT_PNG}")
    for status in sorted(counts):
        print(f"{status}: {counts[status]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
