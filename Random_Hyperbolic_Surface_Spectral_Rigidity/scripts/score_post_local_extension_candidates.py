# created: 2026-05-16T19:32:00Z
# cycle: 37
# run_id: run-2026-05-15T153635Z
# agent: worker
# milestone: M26-post-local-extension-reprioritization

"""Score post-local extension candidates after the M25 branch decision."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
SCORES_CSV = ROOT / "data/extension_candidates/post_local_extension_candidate_scores.csv"
DEPENDENCIES_CSV = ROOT / "data/extension_candidates/post_local_extension_candidate_dependencies.csv"
MATRIX_FIG = ROOT / "reports/figures/m26_post_local_candidate_matrix.png"
DEPENDENCY_FIG = ROOT / "reports/figures/m26_extension_dependency_map.png"

RECOMMENDED_NEXT_MILESTONE = "M27-multiplicity-and-cluster-corollaries-from-rigidity"


@dataclass(frozen=True)
class Candidate:
    candidate_id: str
    family: str
    attachment_point: str
    expected_deliverable: str
    obstruction: str
    required_new_input: str
    classification: str
    one_cycle_feasibility: str
    mathematical_value: int
    tractability: int
    artifact_readiness: int
    dependency_on_open_M25_theorem: int
    novelty: int
    risk: int
    next_milestone_recommended: bool
    evidence_that_would_reverse: str

    @property
    def score(self) -> int:
        return (
            self.mathematical_value
            + self.tractability
            + self.artifact_readiness
            + self.novelty
            - self.dependency_on_open_M25_theorem
            - self.risk
        )


CANDIDATES = [
    Candidate(
        "multiplicity_cluster",
        "multiplicity/spectral-cluster consequences from rigidity",
        "Theorem 1 rigidity; M2 rigidity proof reconstruction; M16 endpoint-subtraction limits",
        "One-cycle theorem note deriving explicit multiplicity and mesoscopic cluster corollaries with scale limitations.",
        "Exact multiplicity can collapse at coincident deterministic reference locations; cluster bounds must keep Lambda and edge/bulk spacing explicit.",
        "No new trace theorem; only Weyl inversion, rigidity displacement, and deterministic spacing bookkeeping.",
        "can be derived from Kim--Tao as a corollary",
        "high",
        5,
        5,
        5,
        1,
        4,
        2,
        True,
        "Reject if the derivation reduces to a tautological restatement of M16 with no nontrivial cluster or multiplicity scale.",
    ),
    Candidate(
        "eigenfunction_lp_mass",
        "eigenfunction Lp/mass-distribution consequences from delocalization",
        "Theorem 2 delocalization; M2 delocalization proof reconstruction; Proposition 4.1 pre-trace variance",
        "Corollary map for Lp, small-ball mass, or averaged mass-distribution statements with explicit norm regimes.",
        "Theorem 2 may already encode the strongest available statement; Lp upgrades may need interpolation or additional local mass input.",
        "Mostly deterministic functional-analysis consequences, with possible need for a new local mass lemma.",
        "can be derived from Kim--Tao as a corollary",
        "medium",
        4,
        4,
        4,
        1,
        4,
        3,
        False,
        "Advance first if multiplicity corollaries are tautological and a clean Lp interpolation statement gives a sharper named consequence.",
    ),
    Candidate(
        "fixed_window_statistics",
        "finite-window but non-shrinking spectral statistics",
        "Theorem 1 rigidity; Proposition 3.1 trace variance; M16 fixed-window threshold analysis",
        "Fixed-energy, fixed-width counting corollaries and variance-to-count checklist that avoids shrinking-window support.",
        "Non-shrinking windows are less novel and may only repackage global rigidity unless the statistic is centered and falsifiable.",
        "No M25 coefficient theorem; may need careful fixed-window smoothing and boundary handling.",
        "can be derived from Kim--Tao as a corollary",
        "medium",
        3,
        4,
        4,
        1,
        3,
        3,
        False,
        "Advance if cluster bounds fail but fixed-window corollaries produce a sharper count fluctuation statement than M16.",
    ),
    Candidate(
        "schreier_graph_theoremization",
        "random-regular-graph/Schreier benchmark theoremization",
        "M3 Schreier benchmarks; M4 labelled-embedding certification; M7 product-ratio bounds",
        "Toy theorem and reproducible benchmark suite for conflict-free labelled-template expectations and spectral-window analogies.",
        "Toy-only unless a transfer map to Kim--Tao quotient families is proved; M15 already exposed the bridge obstruction.",
        "A bounded model theorem is available, but Kim--Tao attachment would require new quotient-family structure.",
        "toy/model evidence only",
        "high",
        3,
        5,
        5,
        2,
        3,
        3,
        False,
        "Advance if a theoremizable benchmark is needed before any further Kim--Tao-facing extension attempt.",
    ),
    Candidate(
        "adjacent_model_transfer",
        "transfer template to adjacent random-surface models",
        "M1 paper map; M2 proof ledger; M15 bridge requirement; M25 obstruction package",
        "Transfer checklist for which Kim--Tao inputs could survive in Weil-Petersson or variable-curvature cover models.",
        "High structural uncertainty; likely requires external model-specific trace, injectivity, and variance theorems.",
        "New model theorems and literature context; not a one-cycle proof deliverable.",
        "requires new theorem",
        "low",
        5,
        2,
        2,
        2,
        5,
        5,
        False,
        "Advance only if the campaign explicitly shifts to model-transfer surveying rather than theorem/probe production.",
    ),
    Candidate(
        "m25_dependent_local_window",
        "M25-dependent shrinking local-window continuation",
        "M21-M25 local-window package; localized Corollary 3.4 numerator target",
        "Direct coefficient-variation theorem for the actual surface-group Corollary 3.4 numerator.",
        "Immediate next step is effectively proving the unresolved localized coefficient-variation theorem.",
        "Actual folded surface-group quotient-family coefficient variation or noncompact trace-tail theorem.",
        "requires new theorem",
        "low",
        5,
        1,
        2,
        5,
        5,
        5,
        False,
        "Reopen only after a new attachment point or exact quotient-family calculation reduces the theorem burden.",
    ),
]


DEPENDENCIES = [
    ("Theorem 1 rigidity", "multiplicity_cluster", "primary attachment"),
    ("M2 rigidity proof reconstruction", "multiplicity_cluster", "loss and exponent ledger"),
    ("M16 local-window corollaries", "multiplicity_cluster", "scale limitation warning"),
    ("Theorem 2 delocalization", "eigenfunction_lp_mass", "primary attachment"),
    ("Proposition 4.1 pre-trace variance", "eigenfunction_lp_mass", "proof-input provenance"),
    ("Theorem 1 rigidity", "fixed_window_statistics", "counting attachment"),
    ("Proposition 3.1 trace variance", "fixed_window_statistics", "variance attachment"),
    ("M3 Schreier benchmarks", "schreier_graph_theoremization", "toy data attachment"),
    ("M4 labelled-embedding certification", "schreier_graph_theoremization", "exact finite identity"),
    ("M7 product-ratio bounds", "schreier_graph_theoremization", "toy theorem input"),
    ("M15 Kim--Tao bridge requirement", "adjacent_model_transfer", "transfer obstruction"),
    ("M25 local-window decision", "adjacent_model_transfer", "negative route reusable"),
    ("M21-M25 local-window package", "m25_dependent_local_window", "open theorem dependency"),
]


def ordered_candidates() -> list[Candidate]:
    return sorted(CANDIDATES, key=lambda c: (-c.score, c.dependency_on_open_M25_theorem, c.risk, c.candidate_id))


def candidate_rows() -> list[dict[str, str]]:
    rows = []
    for rank, candidate in enumerate(ordered_candidates(), start=1):
        row = {
            "candidate_id": candidate.candidate_id,
            "family": candidate.family,
            "attachment_point": candidate.attachment_point,
            "expected_deliverable": candidate.expected_deliverable,
            "obstruction": candidate.obstruction,
            "required_new_input": candidate.required_new_input,
            "classification": candidate.classification,
            "one_cycle_feasibility": candidate.one_cycle_feasibility,
            "mathematical_value": str(candidate.mathematical_value),
            "tractability": str(candidate.tractability),
            "artifact_readiness": str(candidate.artifact_readiness),
            "dependency_on_open_M25_theorem": str(candidate.dependency_on_open_M25_theorem),
            "novelty": str(candidate.novelty),
            "risk": str(candidate.risk),
            "composite_score": str(candidate.score),
            "recommended_order": str(rank),
            "next_milestone_recommended": "yes" if candidate.next_milestone_recommended else "no",
            "evidence_that_would_reverse": candidate.evidence_that_would_reverse,
        }
        rows.append(row)
    return rows


def dependency_rows() -> list[dict[str, str]]:
    return [
        {"source_artifact_or_statement": source, "candidate_id": candidate_id, "dependency_role": role}
        for source, candidate_id, role in DEPENDENCIES
    ]


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def plot_candidate_matrix() -> None:
    ordered = ordered_candidates()
    metrics = [
        ("mathematical_value", "value"),
        ("tractability", "tractability"),
        ("artifact_readiness", "artifact\nreadiness"),
        ("dependency_on_open_M25_theorem", "M25\ndependence"),
        ("novelty", "novelty"),
        ("risk", "risk"),
    ]
    data = np.array([[getattr(candidate, key) for key, _ in metrics] for candidate in ordered], dtype=float)
    fig, ax = plt.subplots(figsize=(10.4, 5.8))
    image = ax.imshow(data, cmap="viridis", vmin=1, vmax=5, aspect="auto")
    ax.set_xticks(range(len(metrics)), [label for _, label in metrics], fontsize=8)
    ax.set_yticks(range(len(ordered)), [f"{i + 1}. {c.candidate_id}" for i, c in enumerate(ordered)], fontsize=8)
    ax.set_title("M26 ranked post-local extension candidates")
    ax.set_xlabel("Score axis, 1=low and 5=high; lower is better for M25 dependence and risk")
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            ax.text(j, i, str(int(data[i, j])), ha="center", va="center", fontsize=9, color="white" if data[i, j] <= 2 else "black")
    cbar = fig.colorbar(image, ax=ax, fraction=0.035, pad=0.02)
    cbar.set_label("Score")
    MATRIX_FIG.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(MATRIX_FIG, dpi=180)
    plt.close(fig)


def plot_dependency_map() -> None:
    ordered = ordered_candidates()
    sources = list(dict.fromkeys(source for source, _, _ in DEPENDENCIES))
    x_lookup = {source: idx for idx, source in enumerate(sources)}
    y_lookup = {candidate.candidate_id: idx for idx, candidate in enumerate(ordered)}
    fig, ax = plt.subplots(figsize=(11.2, 6.6))
    ax.set_xlim(-0.5, len(sources) - 0.5)
    ax.set_ylim(-0.8, len(ordered) - 0.2)
    ax.invert_yaxis()
    ax.set_xticks(range(len(sources)), sources, rotation=35, ha="right", fontsize=7)
    ax.set_yticks(range(len(ordered)), [candidate.candidate_id for candidate in ordered], fontsize=8)
    ax.set_title("M26 dependency map from validated artifacts to candidate branches")
    colors = {"primary attachment": "#4c78a8", "open theorem dependency": "#e45756"}
    for source, candidate_id, role in DEPENDENCIES:
        x = x_lookup[source]
        y = y_lookup[candidate_id]
        color = colors.get(role, "#72b7b2")
        ax.scatter(x, y, s=170, color=color, edgecolor="#333333", linewidth=0.6)
        ax.text(x, y, "x", ha="center", va="center", fontsize=8, color="white")
    ax.grid(axis="x", color="#dddddd", linewidth=0.6)
    ax.grid(axis="y", color="#eeeeee", linewidth=0.6)
    ax.set_xlabel("Validated artifact or paper statement")
    ax.set_ylabel("Candidate branch")
    DEPENDENCY_FIG.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(DEPENDENCY_FIG, dpi=180)
    plt.close(fig)


def validate_inputs() -> None:
    required = {
        "multiplicity/spectral-cluster consequences from rigidity",
        "eigenfunction Lp/mass-distribution consequences from delocalization",
        "finite-window but non-shrinking spectral statistics",
        "random-regular-graph/Schreier benchmark theoremization",
        "transfer template to adjacent random-surface models",
    }
    assert required <= {candidate.family for candidate in CANDIDATES}
    assert sum(1 for candidate in CANDIDATES if candidate.next_milestone_recommended) == 1
    assert all(candidate.attachment_point and candidate.obstruction for candidate in CANDIDATES)
    first = ordered_candidates()[0]
    assert first.candidate_id != "m25_dependent_local_window"
    assert first.next_milestone_recommended


def main() -> int:
    validate_inputs()
    rows = candidate_rows()
    deps = dependency_rows()
    write_csv(SCORES_CSV, rows)
    write_csv(DEPENDENCIES_CSV, deps)
    plot_candidate_matrix()
    plot_dependency_map()
    print(f"wrote {SCORES_CSV.relative_to(ROOT)} ({len(rows)} rows)")
    print(f"wrote {DEPENDENCIES_CSV.relative_to(ROOT)} ({len(deps)} rows)")
    print(f"wrote {MATRIX_FIG.relative_to(ROOT)}")
    print(f"wrote {DEPENDENCY_FIG.relative_to(ROOT)}")
    print(f"recommended_next_milestone={RECOMMENDED_NEXT_MILESTONE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
