# created: 2026-05-16T03:20:00Z
# cycle: 17
# run_id: run-2026-05-15T153635Z
# agent: worker
# milestone: M6-final-synthesis

"""Build final M6 artifact and claim ledgers from explicit manifests."""

from __future__ import annotations

import csv
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_OUT = ROOT / "data/final/final_artifact_index.csv"
CLAIM_OUT = ROOT / "data/final/final_claim_ledger.csv"


ARTIFACT_FIELDS = [
    "milestone_id",
    "cycle",
    "artifact",
    "artifact_type",
    "claim_supported",
    "evidence_level",
    "exists",
    "notes",
]


CLAIM_FIELDS = [
    "claim_id",
    "claim",
    "classification",
    "supporting_artifacts",
    "scope_limit",
]


ARTIFACTS = [
    # M1 paper map
    ("M1-paper-map", "1", "docs/paper_map/cycle1_foundational_map.md", "report", "Paper theorem map and proof architecture", "reconstructed", True, "Canonical M1 narrative."),
    ("M1-paper-map", "1", "docs/paper_map/cycle1_dependency_graph.png", "figure", "Dependency graph for proof architecture", "reconstructed", True, "Rendered from DOT source."),
    ("M1-paper-map", "1", "docs/paper_map/cycle1_open_questions.md", "report", "Initial bottleneck and open-question ledger", "reconstructed", True, "Feeds M2/M5."),
    # M2 proof ledger
    ("M2-proof-ledger", "2", "docs/proof_ledger/theorem1_exponent_flow.md", "report", "Theorem 1 exponent-flow reconstruction", "reconstructed", True, "Tracks Proposition 3.1 to Weyl law."),
    ("M2-proof-ledger", "2", "docs/proof_ledger/weyl_inversion_detail.md", "report", "Weyl inversion near the spectral edge", "reconstructed", True, "Explains alpha_R weakening."),
    ("M2-proof-ledger", "3", "docs/proof_ledger/proposition31_internal_reconstruction.md", "report", "Two-trace expansion and Markov loss", "reconstructed", True, "Localizes q^{2kappa} loss."),
    ("M2-proof-ledger", "3", "docs/proof_ledger/two_trace_expansion_ledger.md", "report", "Two-trace random-cover statistic ledger", "reconstructed", True, "Separates imported inputs."),
    ("M2-proof-ledger", "3", "docs/proof_ledger/markov_loss_reconstruction.md", "report", "Markov interpolation loss reconstruction", "reconstructed", True, "Technical bottleneck."),
    ("M2-proof-ledger", "4", "docs/proof_ledger/delocalization_proof_reconstruction.md", "report", "Theorem 2 delocalization reconstruction", "reconstructed", True, "Pre-trace/fourth-moment pipeline."),
    ("M2-proof-ledger", "4", "docs/proof_ledger/eigenfunction_fourth_moment_ledger.md", "report", "Fourth-moment and diagonal subtraction ledger", "reconstructed", True, "Explains V_n and S."),
    ("M2-proof-ledger", "4", "docs/proof_ledger/pretrace_diagonal_term.md", "report", "Pre-trace diagonal term analysis", "reconstructed", True, "Structural S contribution."),
    ("M2-proof-ledger", "5", "docs/proof_ledger/rigidity_proof_reconstruction.md", "report", "Unified rigidity proof reconstruction", "reconstructed", True, "Canonical M2 Theorem 1 report."),
    ("M2-proof-ledger", "5", "docs/proof_ledger/m2_loss_map.md", "report", "Cross-proof loss map", "reconstructed", True, "Canonical structural/technical/imported split."),
    ("M2-proof-ledger", "5", "docs/proof_ledger/m2_proof_ledger_closure.md", "report", "M2 closure note", "reconstructed", True, "Records imported black boxes."),
    # M3 probes
    ("M3-computational-probes", "6", "scripts/probe_common_fixed_points.py", "script", "Common fixed-point permutation probe", "numerical_evidence", True, "Baseline random-permutation harness."),
    ("M3-computational-probes", "6", "data/polynomial_method/common_fixed_point_summary.csv", "data", "Cyclic versus rank-two fixed-point scaling", "numerical_evidence", True, "Summary table."),
    ("M3-computational-probes", "6", "reports/computational_probes/m3_common_fixed_point_probe.md", "report", "Cycle 6 fixed-point probe interpretation", "numerical_evidence", True, "Includes null composite-word collapse."),
    ("M3-computational-probes", "7", "scripts/probe_folded_word_graphs.py", "script", "Folded quotient profile probe", "numerical_evidence", True, "Quotient-profile diagnostic."),
    ("M3-computational-probes", "7", "data/polynomial_method/folded_word_graph_summary.csv", "data", "Folded graph profile summary", "numerical_evidence", True, "Rare-event limitation recorded."),
    ("M3-computational-probes", "7", "reports/computational_probes/m3_folded_word_graph_probe.md", "report", "Folded quotient report", "numerical_evidence", True, "Canonical Cycle 7 report."),
    ("M3-computational-probes", "8", "scripts/probe_labelled_graph_embeddings.py", "script", "Direct labelled-embedding expectation probe", "numerical_evidence", True, "Avoids rare-event sparsity."),
    ("M3-computational-probes", "8", "data/polynomial_method/labelled_graph_embedding_summary.csv", "data", "Labelled embedding summary", "numerical_evidence", True, "Contains cyclic/rank-two benchmark pair."),
    ("M3-computational-probes", "8", "reports/computational_probes/m3_labelled_graph_embedding_probe.md", "report", "Labelled embedding report", "numerical_evidence", True, "Documents normalization finding."),
    ("M3-computational-probes", "9", "scripts/probe_polynomial_window_diagnostics.py", "script", "Polynomial-window fit diagnostics", "numerical_evidence", True, "Degree/window conditioning probe."),
    ("M3-computational-probes", "9", "data/polynomial_method/polynomial_window_fit_summary.csv", "data", "Polynomial-window fit summary", "numerical_evidence", True, "Degree 3 stable; degree 6/8 stress."),
    ("M3-computational-probes", "9", "reports/computational_probes/m3_polynomial_window_diagnostics.md", "report", "Polynomial-window diagnostic report", "numerical_evidence", True, "Canonical Cycle 9 report."),
    ("M3-computational-probes", "10", "scripts/probe_schreier_spectral_toy.py", "script", "Schreier spectral toy model", "numerical_evidence", True, "Operator-level toy bridge."),
    ("M3-computational-probes", "10", "data/polynomial_method/schreier_spectral_toy_summary.csv", "data", "Schreier spectral summary", "numerical_evidence", True, "Window counts and trace moments."),
    ("M3-computational-probes", "10", "reports/computational_probes/m3_schreier_spectral_toy.md", "report", "Schreier spectral toy report", "numerical_evidence", True, "States non-hyperbolic scope."),
    ("M3-computational-probes", "11", "reports/computational_probes/m3_computational_probe_synthesis.md", "report", "M3 synthesis", "numerical_evidence", True, "Canonical M3 closure."),
    ("M3-computational-probes", "11", "data/polynomial_method/m3_probe_artifact_index.csv", "data", "M3 artifact index", "numerical_evidence", True, "Zero missing paths at creation."),
    ("M3-computational-probes", "11", "reports/figures/m3_probe_ladder_summary.png", "figure", "M3 evidence ladder figure", "numerical_evidence", True, "Generated by plot_m3_probe_ladder_summary.py."),
    # M4 formal certification
    ("M4-formal-certification", "12", "scripts/certify_labelled_embedding_expectation.py", "script", "Exact labelled-template identity certification", "certified", True, "Python exact arithmetic and enumeration."),
    ("M4-formal-certification", "12", "scripts/certify_labelled_embedding_expectation.wls", "script", "Symbolic special-case identity checks", "certified", True, "Historical WLS cross-check; Python remains canonical for final validation."),
    ("M4-formal-certification", "12", "tests/test_labelled_embedding_expectation_identity.py", "test", "M4 regression tests", "certified", True, "Direct python test fallback."),
    ("M4-formal-certification", "12", "data/formal_certification/labelled_embedding_expectation_symbolic.csv", "data", "Symbolic identity outputs", "certified", True, "Generated by Wolfram symbolic cross-check."),
    ("M4-formal-certification", "12", "data/formal_certification/labelled_embedding_expectation_exhaustive.csv", "data", "Exhaustive enumeration outputs", "certified", True, "n <= 4 enumeration."),
    ("M4-formal-certification", "12", "reports/formal_certification/labelled_embedding_expectation_identity.md", "report", "Formal certification report", "certified", True, "Canonical M4 report."),
    # M5 extension
    ("M5-extension-candidates", "13", "scripts/score_m5_extension_candidates.py", "script", "Extension candidate scoring", "conjectural", True, "Ranked candidate selection."),
    ("M5-extension-candidates", "13", "data/extension_candidates/m5_candidate_scores.csv", "data", "Extension candidate matrix", "conjectural", True, "C1 Markov/interpolation selected."),
    ("M5-extension-candidates", "13", "reports/extension_candidates/m5_extension_candidate_ranking.md", "report", "Extension candidate ranking", "conjectural", True, "Rejects direct WP/full trace routes."),
    ("M5-extension-candidates", "14", "scripts/compare_expansions_to_cycle9.py", "script", "Fixed-template expansion comparison", "proved_toy", True, "Compares exact expansions to Cycle 9 fits."),
    ("M5-extension-candidates", "14", "data/extension_candidates/labelled_embedding_expansion_coefficients.csv", "data", "Fixed-template expansion coefficients", "proved_toy", True, "Exact finite toy expansions."),
    ("M5-extension-candidates", "14", "reports/extension_candidates/m5_falling_factorial_expansion_test.md", "report", "Fixed-template expansion test", "proved_toy", True, "Canonical Cycle 14 report."),
    ("M5-extension-candidates", "15", "scripts/plot_growing_template_expansions.py", "script", "Growing-template expansion generator", "proved_toy", True, "Python generator used for canonical final validation."),
    ("M5-extension-candidates", "15", "data/extension_candidates/growing_template_expansion_summary.csv", "data", "Growing-template expansion summary", "proved_toy", True, "L <= 40 exact coefficients through order 8."),
    ("M5-extension-candidates", "15", "reports/extension_candidates/m5_growing_template_expansion_growth.md", "report", "Growing-template expansion report", "proved_toy", True, "Coefficient/radius mechanism."),
    ("M5-extension-candidates", "16", "scripts/plot_m5_extension_synthesis.py", "script", "M5 synthesis figure/data builder", "proved_toy", True, "Builds fixed-vs-growing summary."),
    ("M5-extension-candidates", "16", "data/extension_candidates/m5_extension_synthesis_index.csv", "data", "M5 synthesis artifact index", "proved_toy", True, "Zero missing dependencies."),
    ("M5-extension-candidates", "16", "data/extension_candidates/m5_log_coefficient_summary.csv", "data", "M5 log coefficient summary", "proved_toy", True, "Log coefficient identity data."),
    ("M5-extension-candidates", "16", "reports/figures/m5_fixed_vs_growing_template_mechanism.png", "figure", "Fixed-vs-growing mechanism figure", "proved_toy", True, "Strongest extension figure."),
    ("M5-extension-candidates", "16", "reports/extension_candidates/m5_extension_synthesis_and_toy_principle.md", "report", "M5 synthesis and toy principle", "proved_toy", True, "Canonical M5 closure."),
    # M6 final package
    ("M6-final-synthesis", "17", "scripts/build_final_synthesis_index.py", "script", "Builds final artifact and claim ledgers", "validated", True, "This script."),
    ("M6-final-synthesis", "17", "scripts/plot_final_campaign_summary.py", "script", "Builds final evidence and bottleneck figures", "validated", True, "Companion plotting script."),
    ("M6-final-synthesis", "17", "data/final/final_artifact_index.csv", "data", "Final artifact coverage", "validated", True, "Generated by this script."),
    ("M6-final-synthesis", "17", "data/final/final_claim_ledger.csv", "data", "Final claim classification", "validated", True, "Generated by this script."),
    ("M6-final-synthesis", "17", "reports/figures/final_campaign_evidence_ladder.png", "figure", "Final evidence ladder", "validated", True, "Generated by plot_final_campaign_summary.py."),
    ("M6-final-synthesis", "17", "reports/figures/final_bottleneck_map.png", "figure", "Final bottleneck map", "validated", True, "Generated by plot_final_campaign_summary.py."),
    ("M6-final-synthesis", "17", "reports/final/final_report.md", "report", "Standalone final research record", "validated", True, "Canonical final report."),
    ("M6-final-synthesis", "17", "reports/final/final_file_map.md", "report", "Human-readable file map", "validated", True, "Where to start and known warnings."),
    ("M6-final-synthesis", "17", "audits/final/final_audit_packet.md", "audit", "Final validation checklist", "validated", True, "Audit packet."),
]


CLAIMS = [
    ("C1", "Kim--Tao Theorem 1 rigidity proof reduces to Proposition 3.1, smoothing, Chebyshev/grid control, a Weyl law, and monotone Weyl inversion.", "reconstructed", "docs/proof_ledger/rigidity_proof_reconstruction.md;docs/proof_ledger/theorem1_exponent_flow.md", "Local reconstruction of paper proof; imported MPvH/Nau inputs not reproved."),
    ("C2", "The rigidity exponent weakens at the spectral edge, with a safe conversion alpha_R < 2 alpha_W/3.", "reconstructed", "docs/proof_ledger/weyl_inversion_detail.md", "Conservative exponent bookkeeping, not optimized."),
    ("C3", "Theorem 2 delocalization uses a pre-trace/fourth-moment argument whose structural diagonal term S is distinct from Theorem 1 trace concentration.", "reconstructed", "docs/proof_ledger/delocalization_proof_reconstruction.md;docs/proof_ledger/pretrace_diagonal_term.md", "Local proof architecture only; MP23 rank-two estimate imported."),
    ("C4", "For a finite labelled directed template H, the expected number of injective embeddings is (n)_V times the product over labels of 1/(n)_{C_a}, unless a label constraint is not a partial injection, in which case it is zero.", "certified", "reports/formal_certification/labelled_embedding_expectation_identity.md;tests/test_labelled_embedding_expectation_identity.py", "Toy finite permutation model; not a Selberg trace theorem."),
    ("C5", "The M4 labelled-template identity is a proved toy lemma by elementary permutation counting.", "proved_toy", "scripts/certify_labelled_embedding_expectation.py;data/formal_certification/labelled_embedding_expectation_exhaustive.csv", "Proof is finite-model only."),
    ("C6", "Cyclic/power word families remain order one while rank-two/noncyclic common fixed-point families are suppressed in the permutation probes.", "numerical_evidence", "reports/computational_probes/m3_common_fixed_point_probe.md;data/polynomial_method/common_fixed_point_summary.csv", "Finite Monte Carlo toy evidence."),
    ("C7", "Direct labelled-embedding counts remove rare-event sparsity and show the cyclic/rank-two raw separation is largely explained by constraint dimension after normalization.", "numerical_evidence", "reports/computational_probes/m3_labelled_graph_embedding_probe.md;data/polynomial_method/labelled_graph_embedding_summary.csv", "Expectation estimator, not realized-cover hyperbolic spectrum."),
    ("C8", "Low-degree polynomial-window fits are stable for low-noise labelled embeddings, while degree 6/8 fits expose interpolation conditioning stress.", "numerical_evidence", "reports/computational_probes/m3_polynomial_window_diagnostics.md;data/polynomial_method/polynomial_window_fit_summary.csv", "Toy benchmark; degree choice is diagnostic."),
    ("C9", "Schreier spectral window counts provide an operator-level toy bridge, but centered trace moments are noisy and do not constitute hyperbolic Laplacian evidence.", "numerical_evidence", "reports/computational_probes/m3_schreier_spectral_toy.md;data/polynomial_method/schreier_spectral_toy_summary.csv", "Random permutation Schreier graph only."),
    ("C10", "Fixed conflict-free labelled-template expectations are analytically tame after normalization, while growing support/profile families can amplify coefficients and derivatives because product-ratio zeros/poles approach x=0 at scale 1/L.", "proved_toy", "reports/extension_candidates/m5_extension_synthesis_and_toy_principle.md;data/extension_candidates/m5_log_coefficient_summary.csv", "Strongest new contribution; mechanism benchmark, not a Kim--Tao exponent improvement."),
    ("C11", "The Markov/interpolation-loss pathway is the most credible follow-up target from this campaign.", "conjectural", "reports/extension_candidates/m5_extension_candidate_ranking.md;reports/extension_candidates/m5_primary_candidate_statement.md", "Ranked research judgment based on local evidence."),
    ("C12", "Naive pointwise intersections of composite rank-two words collapse because adding words like ab and aB may impose no extra fixed-point constraints once a and b fix the point.", "negative_result", "reports/computational_probes/m3_common_fixed_point_probe.md", "Null result for naive observable; motivates folded/embedding probes."),
    ("C13", "Independent four/eight-generator common fixed constraints were too rare for ordinary Monte Carlo at the tested sample sizes.", "negative_result", "reports/computational_probes/m3_common_fixed_point_probe.md", "Sampling limitation, not a contradiction."),
    ("C14", "Full Selberg trace formalization, direct Weil--Petersson transfer, and direct hyperbolic spectral simulation were rejected or deferred in this run.", "negative_result", "reports/extension_candidates/m5_extension_candidate_ranking.md", "Deferred for tractability and evidence quality."),
    ("C15", "The campaign does not prove an improved Kim--Tao rigidity exponent.", "non_claim", "reports/extension_candidates/m5_extension_synthesis_and_toy_principle.md;reports/final/final_report.md", "Explicit scope limit."),
    ("C16", "The campaign does not reprove MPvH embedding expansion, Nau boundedness, or MP23 rank-two fixed-point estimates.", "non_claim", "docs/proof_ledger/m2_proof_ledger_closure.md;reports/final/final_report.md", "Imported black boxes remain imported."),
    ("C17", "The computational probes do not validate local spectral statistics for random hyperbolic surfaces.", "non_claim", "reports/computational_probes/m3_computational_probe_synthesis.md;reports/final/final_report.md", "Toy random-permutation and Schreier models only."),
]


def write_csv(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    artifact_rows = []
    missing_required = []
    for row in ARTIFACTS:
        milestone_id, cycle, artifact, artifact_type, claim_supported, evidence_level, required, notes = row
        exists = (ROOT / artifact).exists()
        if required and not exists:
            missing_required.append(artifact)
        artifact_rows.append(
            {
                "milestone_id": milestone_id,
                "cycle": cycle,
                "artifact": artifact,
                "artifact_type": artifact_type,
                "claim_supported": claim_supported,
                "evidence_level": evidence_level,
                "exists": "yes" if exists else "no",
                "notes": notes,
            }
        )

    claim_rows = [
        {
            "claim_id": claim_id,
            "claim": claim,
            "classification": classification,
            "supporting_artifacts": supporting_artifacts,
            "scope_limit": scope_limit,
        }
        for claim_id, claim, classification, supporting_artifacts, scope_limit in CLAIMS
    ]

    write_csv(ARTIFACT_OUT, ARTIFACT_FIELDS, artifact_rows)
    write_csv(CLAIM_OUT, CLAIM_FIELDS, claim_rows)

    categories = {row["classification"] for row in claim_rows}
    required_categories = {
        "reconstructed",
        "certified",
        "numerical_evidence",
        "proved_toy",
        "conjectural",
        "negative_result",
        "non_claim",
    }
    missing_categories = sorted(required_categories - categories)

    print(f"wrote {ARTIFACT_OUT.relative_to(ROOT)}")
    print(f"wrote {CLAIM_OUT.relative_to(ROOT)}")
    print(f"artifact_rows={len(artifact_rows)}")
    print(f"missing_required={len(missing_required)}")
    print(f"claim_rows={len(claim_rows)}")
    print(f"missing_claim_categories={len(missing_categories)}")
    if missing_required:
        print("missing artifacts:")
        for artifact in missing_required:
            print(f"  {artifact}")
    if missing_categories:
        print("missing claim categories:")
        for category in missing_categories:
            print(f"  {category}")
    return 1 if missing_required or missing_categories else 0


if __name__ == "__main__":
    sys.exit(main())
