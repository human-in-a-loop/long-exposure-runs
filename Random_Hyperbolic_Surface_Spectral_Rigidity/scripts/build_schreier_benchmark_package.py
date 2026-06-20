# created: 2026-05-16T23:18:00Z
# cycle: 44
# run_id: run-2026-05-15T153635Z
# agent: worker
# milestone: M33-schreier-benchmark-package-synthesis
"""Build the M33 standalone Schreier benchmark theorem package indexes."""

from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
DATA_FINAL = ROOT / "data" / "final"
FIGURE_DIR = ROOT / "reports" / "figures"

ARTIFACT_INDEX = DATA_FINAL / "m33_schreier_package_artifact_index.csv"
CLAIM_LEDGER = DATA_FINAL / "m33_schreier_theorem_claim_ledger.csv"
DEPENDENCY_EDGES = DATA_FINAL / "m33_schreier_dependency_edges.csv"
SCOPE_FIREWALL = DATA_FINAL / "m33_schreier_scope_firewall.csv"

DEPENDENCY_FIGURE = FIGURE_DIR / "m33_schreier_theorem_dependency_graph.png"
FIREWALL_FIGURE = FIGURE_DIR / "m33_schreier_scope_firewall.png"
VARIANCE_FIGURE = FIGURE_DIR / "m33_schreier_variance_package_summary.png"


SOURCE_ARTIFACTS = [
    ("M4", "reports/formal_certification/labelled_embedding_expectation_identity.md", "source_proof"),
    ("M30", "docs/proof_ledger/schreier_trace_moment_benchmark.md", "source_proof"),
    ("M30", "reports/extension_candidates/m30_schreier_benchmark_theoremization.md", "source_report"),
    ("M30", "data/extension_candidates/m30_schreier_tree_moments.csv", "source_data"),
    ("M30", "data/extension_candidates/m30_schreier_variance_scaling.csv", "source_data"),
    ("M30", "reports/figures/m30_schreier_variance_scaling.png", "source_figure"),
    ("M31", "docs/proof_ledger/schreier_variance_mechanism.md", "source_proof"),
    ("M31", "reports/extension_candidates/m31_schreier_variance_mechanism.md", "source_report"),
    ("M31", "data/extension_candidates/m31_variance_order_summary.csv", "source_data"),
    ("M32", "docs/proof_ledger/schreier_fixed_pair_covariance_lemma.md", "source_proof"),
    ("M32", "reports/extension_candidates/m32_schreier_fixed_pair_covariance_lemma.md", "source_report"),
    ("M32", "data/extension_candidates/m32_variance_theorem_implication.csv", "source_data"),
    ("M32", "reports/final/schreier_variance_theorem_statement.md", "source_final"),
]

M33_ARTIFACTS = [
    ("M33", "docs/proof_ledger/schreier_benchmark_theorem_package.md", "m33_proof"),
    ("M33", "reports/extension_candidates/m33_schreier_benchmark_package_synthesis.md", "m33_report"),
    ("M33", "reports/final/schreier_benchmark_theorem_package.md", "m33_final"),
    ("M33", "scripts/build_schreier_benchmark_package.py", "m33_script"),
    ("M33", "tests/test_schreier_benchmark_package.py", "m33_test"),
    ("M33", "data/final/m33_schreier_package_artifact_index.csv", "m33_data"),
    ("M33", "data/final/m33_schreier_theorem_claim_ledger.csv", "m33_data"),
    ("M33", "data/final/m33_schreier_dependency_edges.csv", "m33_data"),
    ("M33", "data/final/m33_schreier_scope_firewall.csv", "m33_data"),
    ("M33", "reports/figures/m33_schreier_theorem_dependency_graph.png", "m33_figure"),
    ("M33", "reports/figures/m33_schreier_scope_firewall.png", "m33_figure"),
    ("M33", "reports/figures/m33_schreier_variance_package_summary.png", "m33_figure"),
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def artifact_rows() -> list[dict[str, object]]:
    rows = []
    for milestone, rel_path, role in SOURCE_ARTIFACTS + M33_ARTIFACTS:
        path = ROOT / rel_path
        rows.append(
            {
                "milestone": milestone,
                "artifact_path": rel_path,
                "role": role,
                "exists": path.exists(),
                "package_required": True,
            }
        )
    return rows


def claim_rows() -> list[dict[str, object]]:
    return [
        {
            "claim_id": "fixed_k_expectation",
            "claim_type": "theorem",
            "statement": "For fixed k, E[n^{-1}Tr(A_n^k)] = m_k + O_k(n^{-1}).",
            "status": "proved_for_schreier_benchmark",
            "source": "M30 + M4",
            "scope": "two independent uniform permutations; k fixed",
        },
        {
            "claim_id": "tree_word_separation",
            "claim_type": "lemma",
            "statement": "Words freely reducing to identity have Fix(w)=n deterministically and contribute the 4-regular tree moment m_k.",
            "status": "proved_for_schreier_benchmark",
            "source": "M30",
            "scope": "free group on a,b; deterministic for every sample",
        },
        {
            "claim_id": "pair_variance_expansion",
            "claim_type": "identity",
            "statement": "Var(n^{-1}Tr(A_n^k)) = n^{-2} sum_{u,v} Cov(Fix(u),Fix(v)).",
            "status": "proved_for_schreier_benchmark",
            "source": "M31",
            "scope": "finite length-k word sum",
        },
        {
            "claim_id": "fixed_pair_covariance",
            "claim_type": "lemma",
            "statement": "For fixed nontrivial reduced u,v, Cov(Fix(u),Fix(v))=O_{u,v}(1).",
            "status": "proved_for_schreier_benchmark",
            "source": "M32 + M4",
            "scope": "conflict-free quotient templates only; conflicts contribute zero",
        },
        {
            "claim_id": "fixed_k_variance",
            "claim_type": "theorem",
            "statement": "For fixed k, Var(n^{-1}Tr(A_n^k))=O_k(n^{-2}).",
            "status": "proved_for_schreier_benchmark",
            "source": "M31 + M32",
            "scope": "finite word sum after deterministic tree-word separation",
        },
        {
            "claim_id": "m30_variance_slopes",
            "claim_type": "numerical_evidence",
            "statement": "M30 empirical centered-trace variance slopes for k=2,4,6 are close to n^{-2}.",
            "status": "illustrative_only",
            "source": "M30",
            "scope": "finite sample benchmark; not used in proof",
        },
        {
            "claim_id": "no_hyperbolic_transfer",
            "claim_type": "scope_firewall",
            "statement": "No Kim--Tao random-cover, Selberg-trace, or surface-group quotient-family theorem follows from this package.",
            "status": "not_claimed",
            "source": "M30-M32",
            "scope": "negative boundary",
        },
    ]


def dependency_rows() -> list[dict[str, object]]:
    return [
        {"source": "M4 labelled-template expectation identity", "target": "M30 fixed-k expectation", "relation": "computes fixed-word expectation order"},
        {"source": "M30 tree-word separation", "target": "M30 fixed-k expectation", "relation": "identifies m_k"},
        {"source": "M30 trace word expansion", "target": "M31 variance expansion", "relation": "expands trace into fixed-point counts"},
        {"source": "M31 deterministic covariance separation", "target": "M31 variance expansion", "relation": "removes identity-word covariance terms"},
        {"source": "M4 labelled-template expectation identity", "target": "M32 fixed-pair covariance", "relation": "gives quotient-template exponent"},
        {"source": "M32 exponent lemma", "target": "M32 fixed-pair covariance", "relation": "bounds every nontrivial fixed pair by O(1)"},
        {"source": "M31 variance expansion", "target": "M33 fixed-k variance theorem", "relation": "supplies n^-2 finite pair sum"},
        {"source": "M32 fixed-pair covariance", "target": "M33 fixed-k variance theorem", "relation": "bounds all nonidentity covariance terms"},
        {"source": "M30 fixed-k expectation", "target": "M33 theorem package", "relation": "expectation theorem"},
        {"source": "M33 no-transfer firewall", "target": "M33 theorem package", "relation": "scope boundary"},
    ]


def firewall_rows() -> list[dict[str, object]]:
    return [
        {
            "boundary_item": "two_permutation_schreier_benchmark",
            "classification": "proved",
            "package_position": "inside_scope",
            "statement": "A_n=P_a+P_a^{-1}+P_b+P_b^{-1} with independent uniform permutations.",
        },
        {
            "boundary_item": "fixed_k_expectation_and_variance",
            "classification": "proved",
            "package_position": "inside_scope",
            "statement": "Expectation is m_k+O_k(n^{-1}); normalized variance is O_k(n^{-2}).",
        },
        {
            "boundary_item": "hyperbolic_random_covers",
            "classification": "not_claimed",
            "package_position": "outside_scope",
            "statement": "No theorem for Kim--Tao random hyperbolic covers is proved.",
        },
        {
            "boundary_item": "selberg_trace_transfer",
            "classification": "not_claimed",
            "package_position": "outside_scope",
            "statement": "No Selberg trace variance or quotient-family estimate follows from this free-Schreier result.",
        },
        {
            "boundary_item": "adjacency_to_laplacian_transfer",
            "classification": "not_claimed",
            "package_position": "outside_scope",
            "statement": "No adjacency-to-Laplacian transfer theorem is proved.",
        },
        {
            "boundary_item": "shrinking_local_spectral_windows",
            "classification": "not_claimed",
            "package_position": "outside_scope",
            "statement": "No shrinking-window local spectral statistics result is proved.",
        },
        {
            "boundary_item": "surface_group_quotient_family",
            "classification": "open",
            "package_position": "outside_scope",
            "statement": "Surface-group quotient-family coefficient variation remains a separate open target.",
        },
    ]


def plot_dependency_graph(rows: list[dict[str, object]]) -> None:
    levels = {
        "M4 labelled-template expectation identity": (0, 3.0),
        "M30 tree-word separation": (0, 2.2),
        "M30 trace word expansion": (0, 1.4),
        "M31 deterministic covariance separation": (1, 1.4),
        "M32 exponent lemma": (1, 3.0),
        "M30 fixed-k expectation": (2, 2.3),
        "M31 variance expansion": (2, 1.4),
        "M32 fixed-pair covariance": (2, 3.0),
        "M33 fixed-k variance theorem": (3, 2.2),
        "M33 no-transfer firewall": (3, 0.9),
        "M33 theorem package": (4, 1.8),
    }
    fig, ax = plt.subplots(figsize=(15, 6.5))
    ax.axis("off")
    for name, (x, y) in levels.items():
        color = "#d7ecff" if "M33" not in name else "#e8f5dc"
        ax.text(x, y, name, ha="center", va="center", bbox=dict(boxstyle="round,pad=0.35", fc=color, ec="#40566b"))
    for row in rows:
        s, t = row["source"], row["target"]
        if s in levels and t in levels:
            x1, y1 = levels[s]
            x2, y2 = levels[t]
            ax.annotate("", xy=(x2 - 0.18, y2), xytext=(x1 + 0.18, y1), arrowprops=dict(arrowstyle="->", color="#40566b", lw=1.5))
    ax.set_title("M33 Schreier theorem package dependency graph", fontsize=14)
    fig.subplots_adjust(left=0.03, right=0.97, top=0.9, bottom=0.08)
    fig.savefig(DEPENDENCY_FIGURE, dpi=180)
    plt.close(fig)


def plot_firewall(rows: list[dict[str, object]]) -> None:
    labels = [r["boundary_item"].replace("_", "\n") for r in rows]
    colors = ["#2f8f57" if r["package_position"] == "inside_scope" else "#b64b4b" for r in rows]
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.bar(range(len(rows)), [1] * len(rows), color=colors)
    ax.axvline(1.5, color="#222222", lw=2)
    ax.text(0.5, 1.08, "proved inside package", ha="center", fontsize=11)
    ax.text(4.2, 1.08, "explicitly outside package", ha="center", fontsize=11)
    ax.set_xticks(range(len(rows)))
    ax.set_xticklabels(labels, fontsize=8)
    ax.set_yticks([])
    ax.set_ylim(0, 1.18)
    ax.set_title("Scope firewall: free-Schreier theorem versus non-claimed transfers", fontsize=14)
    fig.tight_layout()
    fig.savefig(FIREWALL_FIGURE, dpi=180)
    plt.close(fig)


def plot_variance_summary() -> None:
    rows = [r for r in read_csv(ROOT / "data" / "extension_candidates" / "m30_schreier_variance_scaling.csv") if r["k"] in {"2", "4", "6"}]
    slopes: dict[int, float] = {}
    for row in rows:
        slopes[int(row["k"])] = float(row["loglog_variance_slope_for_k"])
    ks = sorted(slopes)
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.bar([str(k) for k in ks], [slopes[k] for k in ks], color="#6f8fb8", label="M30 empirical slope")
    ax.axhline(-2.0, color="#1f6b3a", linestyle="--", lw=2, label="theorem order O_k(n^-2)")
    ax.axhline(-1.0, color="#9b5b32", linestyle=":", lw=2, label="O(n^-1) reference")
    ax.set_xlabel("moment k")
    ax.set_ylabel("log-log variance slope")
    ax.set_title("Schreier variance package summary")
    ax.legend()
    fig.tight_layout()
    fig.savefig(VARIANCE_FIGURE, dpi=180)
    plt.close(fig)


def main() -> None:
    DATA_FINAL.mkdir(parents=True, exist_ok=True)
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)

    artifacts = artifact_rows()
    claims = claim_rows()
    deps = dependency_rows()
    firewall = firewall_rows()

    write_csv(ARTIFACT_INDEX, artifacts, ["milestone", "artifact_path", "role", "exists", "package_required"])
    write_csv(CLAIM_LEDGER, claims, ["claim_id", "claim_type", "statement", "status", "source", "scope"])
    write_csv(DEPENDENCY_EDGES, deps, ["source", "target", "relation"])
    write_csv(SCOPE_FIREWALL, firewall, ["boundary_item", "classification", "package_position", "statement"])

    plot_dependency_graph(deps)
    plot_firewall(firewall)
    plot_variance_summary()

    print(f"wrote {ARTIFACT_INDEX.relative_to(ROOT)} ({len(artifacts)} rows)")
    print(f"wrote {CLAIM_LEDGER.relative_to(ROOT)} ({len(claims)} rows)")
    print(f"wrote {DEPENDENCY_EDGES.relative_to(ROOT)} ({len(deps)} rows)")
    print(f"wrote {SCOPE_FIREWALL.relative_to(ROOT)} ({len(firewall)} rows)")
    print(f"wrote {DEPENDENCY_FIGURE.relative_to(ROOT)}")
    print(f"wrote {FIREWALL_FIGURE.relative_to(ROOT)}")
    print(f"wrote {VARIANCE_FIGURE.relative_to(ROOT)}")
    print("decision=preserve_as_standalone_benchmark_theorem_package")


if __name__ == "__main__":
    main()
