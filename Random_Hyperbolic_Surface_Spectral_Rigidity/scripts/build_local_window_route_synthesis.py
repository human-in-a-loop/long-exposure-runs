# created: 2026-05-16T19:12:00Z
# cycle: 36
# run_id: run-2026-05-15T153635Z
# agent: worker
# milestone: M25-local-window-route-synthesis-and-branch-decision

"""Build M25 local-window evidence and branch-decision artifacts."""

from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_CSV = ROOT / "data/extension_candidates/local_window_route_evidence_index.csv"
DECISION_CSV = ROOT / "data/extension_candidates/local_window_route_decision_table.csv"
CHAIN_FIG = ROOT / "reports/figures/m25_local_window_obstruction_chain.png"
MATRIX_FIG = ROOT / "reports/figures/m25_branch_decision_matrix.png"

ALLOWED_LABELS = {
    "proved from Kim--Tao",
    "conditional theorem template",
    "toy/proxy evidence",
    "analytic obstruction",
    "open theorem",
}

FINAL_DECISION = "preserve_as_followup_problem"
ALLOWED_DECISIONS = {
    "continue_compact_coefficient_variation",
    "pivot_noncompact_trace_tail",
    "close_local_window_branch",
    "preserve_as_followup_problem",
}

EVIDENCE_ROWS = [
    {
        "milestone": "M16-local-spectral-window-corollaries",
        "claim_type": "proved from Kim--Tao",
        "primary_artifact": "docs/proof_ledger/local_window_from_rigidity.md",
        "status": "validated",
        "implication": "Inherited global Weyl/rigidity estimates control only windows above endpoint-subtraction scales.",
    },
    {
        "milestone": "M17-local-window-variance-input",
        "claim_type": "conditional theorem template",
        "primary_artifact": "docs/proof_ledger/local_window_variance_input.md",
        "status": "validated",
        "implication": "Endpoint-beating local windows need a direct smoothed-window variance saving.",
    },
    {
        "milestone": "M18-test-function-localization-feasibility",
        "claim_type": "analytic obstruction",
        "primary_artifact": "docs/proof_ledger/test_function_localization_feasibility.md",
        "status": "validated",
        "implication": "Retuning Kim--Tao's original test functions is not enough; trace-side localization is the plausible route.",
    },
    {
        "milestone": "M19-smoothed-window-paley-wiener-lemma",
        "claim_type": "analytic obstruction",
        "primary_artifact": "docs/proof_ledger/smoothed_window_paley_wiener_obstruction.md",
        "status": "validated",
        "implication": "Bulk window Delta=n^-d requires polynomial support q=n^eta with eta>=d, and small leakage needs eta>d.",
    },
    {
        "milestone": "M20-long-support-trace-variance-requirement",
        "claim_type": "conditional theorem template",
        "primary_artifact": "docs/proof_ledger/long_support_trace_variance_requirement.md",
        "status": "validated",
        "implication": "Long-support trace variance must beat a beta-saving budget once polynomial support is accepted.",
    },
    {
        "milestone": "M21-trace-side-long-support-variance-template",
        "claim_type": "conditional theorem template",
        "primary_artifact": "docs/proof_ledger/trace_side_long_support_variance_template.md",
        "status": "validated",
        "implication": "The fixed-energy trace-side theorem LSTV_trace(eta,beta) is sufficient if beta>2 kappa eta+2d-1.",
    },
    {
        "milestone": "M22-trace-corollary34-uniform-coefficient-variation-target",
        "claim_type": "open theorem",
        "primary_artifact": "docs/proof_ledger/trace_corollary34_localized_numerator_target.md",
        "status": "validated",
        "implication": "The variance theorem reduces upstream to localized Corollary 3.4 numerator control for the actual Q family.",
    },
    {
        "milestone": "M23-localized-trace-numerator-quotient-family-model",
        "claim_type": "toy/proxy evidence",
        "primary_artifact": "docs/proof_ledger/localized_trace_numerator_quotient_family_model.md",
        "status": "validated",
        "implication": "Proxy quotient-family growth dominates absent extra damping; unknown surface-group rows remain outside toy certification.",
    },
    {
        "milestone": "M24-localized-transform-geodesic-weight-decay-obstruction",
        "claim_type": "analytic obstruction",
        "primary_artifact": "docs/proof_ledger/localized_transform_geodesic_weight_decay.md",
        "status": "validated",
        "implication": "Compact-support transform/geodesic weights do not supply M23's optimistic damping; decay is in t delta_r, not t.",
    },
]

DECISION_ROWS = [
    {
        "branch": "compact_support_coefficient_variation",
        "decision": "preserve_as_followup_problem",
        "claim_type": "open theorem",
        "required_new_input": "Uniform small-x or coefficient-variation control for the actual Lemma 3.3 / Corollary 3.4 quotient-polynomial numerator.",
        "rate_condition": "candidate_beta=(2 kappa-A) eta+sigma must satisfy candidate_beta>2 kappa eta+2d-1.",
        "evidence_basis": "M21-M24",
        "rationale": "This is the only compact-support route left, but proving it requires new surface-group quotient-family structure.",
    },
    {
        "branch": "noncompact_trace_tail",
        "decision": "preserve_as_followup_problem",
        "claim_type": "open theorem",
        "required_new_input": "A noncompact trace-tail theorem with spectral localization and controlled omitted geometric side.",
        "rate_condition": "geometric tail rate must exceed the relevant geodesic/family growth rate from M23/M24.",
        "evidence_basis": "M19,M23,M24",
        "rationale": "Potentially viable only after replacing the compact-support trace architecture.",
    },
    {
        "branch": "branch_closure_obstruction_statement",
        "decision": "preserve_as_followup_problem",
        "claim_type": "analytic obstruction",
        "required_new_input": "None for closing transform-damping and retuned-test-function subroutes.",
        "rate_condition": "No compatible transform-weight rate beats positive support/family growth.",
        "evidence_basis": "M16-M24",
        "rationale": "Immediate same-branch empirical continuation is not justified; preserve as a precise problem package.",
    },
]

CHAIN = [
    ("M16", "endpoint\nsubtraction"),
    ("M17", "variance\nrequirement"),
    ("M19", "support\nscaling"),
    ("M21", "long-support\ntrace budget"),
    ("M22", "localized\nnumerator"),
    ("M23", "quotient-family\ngrowth"),
    ("M24", "transform damping\nobstruction"),
]


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def plot_chain() -> None:
    fig, ax = plt.subplots(figsize=(11.0, 3.2))
    ax.axis("off")
    xs = [i for i in range(len(CHAIN))]
    for idx, ((milestone, label), x) in enumerate(zip(CHAIN, xs)):
        color = "#4c78a8" if idx < 2 else "#f58518" if idx < 5 else "#e45756"
        ax.text(
            x,
            0.5,
            f"{milestone}\n{label}",
            ha="center",
            va="center",
            fontsize=9,
            color="white",
            bbox={"boxstyle": "round,pad=0.35", "facecolor": color, "edgecolor": "#333333", "linewidth": 1.0},
        )
        if idx + 1 < len(CHAIN):
            ax.annotate(
                "",
                xy=(x + 0.72, 0.5),
                xytext=(x + 0.28, 0.5),
                arrowprops={"arrowstyle": "->", "color": "#333333", "linewidth": 1.3},
            )
    ax.text(
        3,
        0.08,
        "Obstruction chain: endpoint scale -> variance saving -> polynomial support -> numerator control -> growth without compatible damping",
        ha="center",
        va="center",
        fontsize=9,
        color="#333333",
    )
    ax.set_xlim(-0.6, len(CHAIN) - 0.4)
    ax.set_ylim(0, 1)
    CHAIN_FIG.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(CHAIN_FIG, dpi=180)
    plt.close(fig)


def plot_matrix() -> None:
    branches = [
        "compact\ncoefficient\nvariation",
        "noncompact\ntrace tail",
        "closure /\nfollow-up\npackage",
    ]
    criteria = ["uses current\narchitecture", "new theorem\nburden", "immediate\nnext-cycle fit", "research\nvalue"]
    scores = [
        [3, 1, 1, 3],
        [1, 1, 1, 3],
        [3, 3, 3, 2],
    ]
    fig, ax = plt.subplots(figsize=(7.4, 4.2))
    im = ax.imshow(scores, cmap="YlGn", vmin=0, vmax=3)
    ax.set_xticks(range(len(criteria)), criteria, fontsize=8)
    ax.set_yticks(range(len(branches)), branches, fontsize=8)
    for i, row in enumerate(scores):
        for j, value in enumerate(row):
            ax.text(j, i, str(value), ha="center", va="center", fontsize=10, color="#222222")
    ax.set_title("M25 branch decision matrix (3=best, 1=weak)")
    ax.text(
        1.5,
        3.0,
        f"final decision: {FINAL_DECISION}",
        ha="center",
        va="center",
        fontsize=9,
        color="#333333",
    )
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    fig.tight_layout()
    MATRIX_FIG.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(MATRIX_FIG, dpi=180)
    plt.close(fig)


def validate_inputs() -> list[str]:
    errors = []
    milestones = {row["milestone"] for row in EVIDENCE_ROWS}
    expected = {
        f"M{i}-{suffix}"
        for i, suffix in [
            (16, "local-spectral-window-corollaries"),
            (17, "local-window-variance-input"),
            (18, "test-function-localization-feasibility"),
            (19, "smoothed-window-paley-wiener-lemma"),
            (20, "long-support-trace-variance-requirement"),
            (21, "trace-side-long-support-variance-template"),
            (22, "trace-corollary34-uniform-coefficient-variation-target"),
            (23, "localized-trace-numerator-quotient-family-model"),
            (24, "localized-transform-geodesic-weight-decay-obstruction"),
        ]
    }
    if milestones != expected:
        errors.append(f"milestone coverage mismatch: {sorted(expected - milestones)} missing")
    bad_labels = sorted({row["claim_type"] for row in EVIDENCE_ROWS + DECISION_ROWS} - ALLOWED_LABELS)
    if bad_labels:
        errors.append(f"bad evidence labels: {bad_labels}")
    if FINAL_DECISION not in ALLOWED_DECISIONS:
        errors.append(f"bad final decision: {FINAL_DECISION}")
    for row in EVIDENCE_ROWS:
        if not (ROOT / row["primary_artifact"]).exists():
            errors.append(f"missing artifact: {row['primary_artifact']}")
    return errors


def main() -> int:
    errors = validate_inputs()
    write_csv(EVIDENCE_CSV, EVIDENCE_ROWS)
    write_csv(DECISION_CSV, DECISION_ROWS)
    plot_chain()
    plot_matrix()
    print(f"wrote {EVIDENCE_CSV.relative_to(ROOT)} ({len(EVIDENCE_ROWS)} rows)")
    print(f"wrote {DECISION_CSV.relative_to(ROOT)} ({len(DECISION_ROWS)} rows)")
    print(f"wrote {CHAIN_FIG.relative_to(ROOT)}")
    print(f"wrote {MATRIX_FIG.relative_to(ROOT)}")
    print(f"final_decision={FINAL_DECISION}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
