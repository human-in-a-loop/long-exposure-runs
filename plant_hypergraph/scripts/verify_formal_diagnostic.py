# created: 2026-05-17T03:00:00Z
# cycle: 5
# run_id: run-2026-05-17T004540Z
# agent: worker
# milestone: M7

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path


M6_NATIVE_DISTANCE = "1.772727"
M6_CLIQUE_DISTANCE = "2.090909"
M6_COLLAPSED_NATIVE_DISTANCE = "2.090909"
M6_COLLAPSE_DISTANCE_DELTA = "0.318182"


FIELDNAMES = [
    "example_id",
    "edge_family",
    "k",
    "introduced_pairs",
    "licensed_pairs",
    "unlicensed_pairs",
    "unlicensed_pair_ratio",
    "semantic_claim",
]


def pair_count(k):
    if k < 0:
        raise ValueError("hyperedge arity k must be non-negative")
    return k * (k - 1) // 2


def finite_examples():
    specs = [
        ("arity_0_empty_context", "regional_checklist_context", 0, 0, "empty context carries no taxon-taxon claim"),
        ("arity_1_singleton_context", "regional_checklist_context", 1, 0, "singleton context carries no taxon-taxon claim"),
        ("arity_2_pairwise_trait_safe", "trait_syndrome", 2, 1, "pairwise equivalence only when the task asks for shared trait-state membership"),
        ("arity_3_context_only", "regional_checklist_context", 3, 0, "shared checklist context is not mutual biological or taxonomic similarity"),
        ("arity_5_context_only", "regional_checklist_context", 5, 0, "larger context hyperedges create many unlicensed taxon-taxon adjacencies"),
        ("regional_context_example", "regional_checklist_context", 5, 0, "regional checklist membership supports source-scoped context, not global similarity"),
        ("reticulate_role_example", "reticulate_or_hybrid_signal", 3, 2, "child-to-source-lineage near-miss is role-licensed; source-source similarity is not"),
        ("trait_convergence_trap", "trait_syndrome", 3, 0, "shared convergent trait state must not become taxonomic closeness"),
    ]
    rows = []
    for example_id, edge_family, k, licensed_pairs, claim in specs:
        introduced = pair_count(k)
        if licensed_pairs > introduced:
            raise ValueError(f"{example_id} licenses more pairs than clique expansion introduces")
        unlicensed = introduced - licensed_pairs
        ratio = 0.0 if introduced == 0 else unlicensed / introduced
        rows.append(
            {
                "example_id": example_id,
                "edge_family": edge_family,
                "k": str(k),
                "introduced_pairs": str(introduced),
                "licensed_pairs": str(licensed_pairs),
                "unlicensed_pairs": str(unlicensed),
                "unlicensed_pair_ratio": f"{ratio:.6f}",
                "semantic_claim": claim,
            }
        )
    return rows


def summarize_m6(path):
    groups = defaultdict(lambda: {"hyperedges": 0, "taxon_members": 0, "introduced_pairs": 0})
    with Path(path).open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            family = row["edge_family"]
            groups[family]["hyperedges"] += 1
            groups[family]["taxon_members"] += int(row["taxon_members"])
            groups[family]["introduced_pairs"] += int(row["introduced_taxon_pairs"])

    summary = []
    for family in sorted(groups):
        data = groups[family]
        introduced = data["introduced_pairs"]
        licensed, license_label, note = license_for_family(family, data)
        unlicensed = max(0, introduced - licensed)
        ratio = 0.0 if introduced == 0 else unlicensed / introduced
        summary.append(
            {
                "edge_family": family,
                "hyperedges": str(data["hyperedges"]),
                "taxon_members": str(data["taxon_members"]),
                "introduced_pairs": str(introduced),
                "licensed_pairs": str(licensed),
                "unlicensed_pairs": str(unlicensed),
                "unlicensed_pair_ratio": f"{ratio:.6f}",
                "pairwise_similarity_licensed_by_schema": license_label,
                "semantic_note": note,
            }
        )
    return summary


def license_for_family(family, data):
    if family == "regional_checklist_context":
        return 0, "no", "checklist co-membership is source context, not pairwise taxon similarity"
    if family == "reticulate_or_hybrid_signal":
        # M6 synthetic reticulate rows are k=3: one child plus two source lineages.
        # Only child-source near-miss pairs are role-licensed; source-source adjacency is not.
        return data["hyperedges"] * 2, "partial_role_dependent", "role labels license child-source near-miss, not all clique pairs"
    if family == "trait_syndrome":
        return 0, "no_for_taxonomic_similarity", "shared trait state is a convergence stressor, not taxonomic identity"
    return 0, "unknown", "family not classified by M7 diagnostic"


def write_csv(path, rows, fieldnames):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def render_plot(path, finite_rows):
    import matplotlib.pyplot as plt

    ordered = [row for row in finite_rows if row["example_id"].startswith("arity_")]
    labels = [row["k"] for row in ordered]
    licensed = [int(row["licensed_pairs"]) for row in ordered]
    unlicensed = [int(row["unlicensed_pairs"]) for row in ordered]

    fig, ax = plt.subplots(figsize=(7.0, 4.4))
    x = range(len(labels))
    ax.bar(x, licensed, label="licensed pairs", color="#3b7c5f")
    ax.bar(x, unlicensed, bottom=licensed, label="unlicensed pairs", color="#b64b4b")
    ax.set_xticks(list(x))
    ax.set_xticklabels([f"k={label}" for label in labels])
    ax.set_ylabel("introduced taxon pairs")
    ax.set_xlabel("hyperedge arity")
    ax.set_title("Clique expansion pair claims by hyperedge arity")
    ax.legend(frameon=False)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def run(args):
    out_dir = Path(args.out_dir)
    finite_rows = finite_examples()
    m6_rows = summarize_m6(args.m6_diagnostic)

    finite_path = out_dir / "finite_examples.csv"
    m6_path = out_dir / "m6_clique_diagnostic_summary.csv"
    summary_path = out_dir / "formal_diagnostic_summary.json"
    figure_path = out_dir / "clique_warning_diagnostic.png"

    write_csv(finite_path, finite_rows, FIELDNAMES)
    write_csv(
        m6_path,
        m6_rows,
        [
            "edge_family",
            "hyperedges",
            "taxon_members",
            "introduced_pairs",
            "licensed_pairs",
            "unlicensed_pairs",
            "unlicensed_pair_ratio",
            "pairwise_similarity_licensed_by_schema",
            "semantic_note",
        ],
    )
    render_plot(figure_path, finite_rows)

    summary = {
        "created": "2026-05-17T03:00:00Z",
        "cycle": 5,
        "milestone": "M7",
        "finite_example_rows": len(finite_rows),
        "m6_family_rows": len(m6_rows),
        "m6_numeric_anchors": {
            "native_hypergraph_mean_hierarchy_distance": M6_NATIVE_DISTANCE,
            "clique_expansion_mean_hierarchy_distance": M6_CLIQUE_DISTANCE,
            "collapsed_native_mean_hierarchy_distance": M6_COLLAPSED_NATIVE_DISTANCE,
            "collapse_to_clique_distance_delta": M6_COLLAPSE_DISTANCE_DELTA,
        },
        "finite_checks": {
            "pair_count_formula": "k * (k - 1) / 2",
            "k0_pairs": pair_count(0),
            "k1_pairs": pair_count(1),
            "k2_pairs": pair_count(2),
            "k3_pairs": pair_count(3),
            "k5_pairs": pair_count(5),
        },
        "m6_summary": m6_rows,
        "outputs": {
            "finite_examples": str(finite_path),
            "m6_clique_diagnostic_summary": str(m6_path),
            "figure": str(figure_path),
        },
    }
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"out_dir": str(out_dir), "finite_rows": len(finite_rows), "m6_rows": len(m6_rows)}, sort_keys=True))


def parse_args():
    parser = argparse.ArgumentParser(description="Verify finite clique-expansion diagnostic examples.")
    parser.add_argument("--m6-diagnostic", default="data/experiments/synthetic_v0.1/clique_false_similarity.csv")
    parser.add_argument("--out-dir", default="data/formal_diagnostic")
    return parser.parse_args()


if __name__ == "__main__":
    run(parse_args())
