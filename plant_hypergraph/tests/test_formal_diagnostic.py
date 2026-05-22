import tempfile
import unittest
from pathlib import Path

from scripts import verify_formal_diagnostic as diagnostic


M6_DIAGNOSTIC = Path("data/experiments/synthetic_v0.1/clique_false_similarity.csv")


class FormalDiagnosticTests(unittest.TestCase):
    def test_pair_count_formula(self):
        for k, expected in [(0, 0), (1, 0), (2, 1), (3, 3), (5, 10)]:
            self.assertEqual(diagnostic.pair_count(k), expected)

    def test_zero_and_singleton_edges_introduce_zero_pairs(self):
        rows = {row["example_id"]: row for row in diagnostic.finite_examples()}
        self.assertEqual(rows["arity_0_empty_context"]["introduced_pairs"], "0")
        self.assertEqual(rows["arity_1_singleton_context"]["introduced_pairs"], "0")
        self.assertEqual(rows["arity_0_empty_context"]["unlicensed_pair_ratio"], "0.000000")
        self.assertEqual(rows["arity_1_singleton_context"]["unlicensed_pair_ratio"], "0.000000")

    def test_k2_equivalence_requires_pairwise_semantics(self):
        rows = {row["example_id"]: row for row in diagnostic.finite_examples()}
        safe = rows["arity_2_pairwise_trait_safe"]
        self.assertEqual(safe["introduced_pairs"], "1")
        self.assertEqual(safe["licensed_pairs"], "1")
        self.assertEqual(safe["unlicensed_pair_ratio"], "0.000000")

    def test_context_hyperedges_with_k_at_least_3_can_be_unlicensed(self):
        rows = {row["example_id"]: row for row in diagnostic.finite_examples()}
        context = rows["arity_3_context_only"]
        self.assertEqual(context["introduced_pairs"], "3")
        self.assertEqual(context["licensed_pairs"], "0")
        self.assertEqual(context["unlicensed_pair_ratio"], "1.000000")

    def test_m6_diagnostic_summary_is_deterministic(self):
        first = diagnostic.summarize_m6(M6_DIAGNOSTIC)
        second = diagnostic.summarize_m6(M6_DIAGNOSTIC)
        self.assertEqual(first, second)
        by_family = {row["edge_family"]: row for row in first}
        self.assertEqual(by_family["regional_checklist_context"]["introduced_pairs"], "40")
        self.assertEqual(by_family["reticulate_or_hybrid_signal"]["introduced_pairs"], "21")
        self.assertEqual(by_family["trait_syndrome"]["introduced_pairs"], "22")
        self.assertEqual(by_family["reticulate_or_hybrid_signal"]["pairwise_similarity_licensed_by_schema"], "partial_role_dependent")

    def test_run_writes_expected_outputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            args = type("Args", (), {"m6_diagnostic": str(M6_DIAGNOSTIC), "out_dir": tmp})()
            diagnostic.run(args)
            for name in [
                "finite_examples.csv",
                "m6_clique_diagnostic_summary.csv",
                "formal_diagnostic_summary.json",
                "clique_warning_diagnostic.png",
            ]:
                self.assertTrue((Path(tmp) / name).exists())


if __name__ == "__main__":
    unittest.main()
