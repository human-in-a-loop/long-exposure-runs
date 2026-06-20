import csv
import hashlib
import tempfile
import unittest
from pathlib import Path

from scripts import run_synthetic_experiments as runner
from tools import baselines


BASE = Path("data/synthetic_benchmark/v0.1")
PUBLIC = Path("data/public_taxonomy_sample/v0.1")


def read_csv(path):
    with Path(path).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class BaselineExperimentTests(unittest.TestCase):
    def test_model_information_budgets_are_constrained(self):
        benchmark = baselines.load_benchmark(BASE)
        tree_families = {row["edge_family"] for row in baselines.allowed_rows_for_model("tree_dag", benchmark["hyperedges"])}
        graph_families = {row["edge_family"] for row in baselines.allowed_rows_for_model("ordinary_graph", benchmark["hyperedges"])}
        self.assertEqual(tree_families, {"taxonomic_parentage"})
        self.assertNotIn("reticulate_or_hybrid_signal", graph_families)
        self.assertIn("trait_syndrome", graph_families)

    def test_synonym_mappings_are_hidden_from_tree_prediction(self):
        benchmark = baselines.load_benchmark(BASE)
        syn_test = next(row for row in benchmark["examples"] if row["split"] == "test" and row["case_type"] == "synonym_or_rename")
        predictions = baselines.predict_examples("tree_dag", benchmark["examples"], benchmark["taxa"], benchmark["names"], benchmark["hyperedges"])
        pred = next(row for row in predictions if row["example_id"] == syn_test["example_id"])
        self.assertNotEqual(pred["prediction"], syn_test["target_accepted_taxon_id"])

    def test_clique_expansion_introduces_extra_pairwise_relationships(self):
        benchmark = baselines.load_benchmark(BASE)
        rows = baselines.clique_false_similarity_rows(benchmark["hyperedges"])
        self.assertTrue(rows)
        self.assertTrue(any(row["edge_family"] == "trait_syndrome" and int(row["introduced_taxon_pairs"]) > 0 for row in rows))

    def test_native_hypergraph_preserves_reticulate_roles(self):
        benchmark = baselines.load_benchmark(BASE)
        indexed = baselines.native_candidate_index(benchmark["hyperedges"])
        reticulate_children = {
            row["node_id"]
            for row in benchmark["hyperedges"]
            if row["edge_family"] == "reticulate_or_hybrid_signal" and row["role"] == "reticulate_child"
        }
        self.assertTrue(reticulate_children)
        child = sorted(reticulate_children)[0]
        roles = {member["role"] for edge in indexed[child] for member in edge if member["edge_family"] == "reticulate_or_hybrid_signal"}
        self.assertIn("reticulate_child", roles)
        self.assertIn("source_lineage", roles)

    def test_public_sample_parses_as_nonsynthetic_plumbing(self):
        check = runner.public_sample_check(PUBLIC)
        self.assertTrue(check["all_is_synthetic_false"])
        self.assertIn("taxonomic_parentage", check["edge_families"])

    def test_strict_negative_control_does_not_disadvantage_tree(self):
        with tempfile.TemporaryDirectory() as tmp:
            strict_dir = runner.make_strict_control(Path(tmp) / "strict", 20260517)
            benchmark = baselines.load_benchmark(strict_dir)
            _, metrics = baselines.run_model_suite(benchmark, ablation="strict_negative_control", seed=20260517)
            by_model = {row["model"]: row for row in metrics}
            self.assertEqual(by_model["tree_dag"]["mean_hierarchy_distance"], by_model["native_hypergraph"]["mean_hierarchy_distance"])

    def test_runner_outputs_are_hash_stable(self):
        with tempfile.TemporaryDirectory() as tmp:
            a = Path(tmp) / "a"
            b = Path(tmp) / "b"
            args_a = type("Args", (), {"benchmark_dir": str(BASE), "public_sample_dir": str(PUBLIC), "out_dir": str(a), "seed": 20260517, "ablation": "all"})()
            args_b = type("Args", (), {"benchmark_dir": str(BASE), "public_sample_dir": str(PUBLIC), "out_dir": str(b), "seed": 20260517, "ablation": "all"})()
            runner.run(args_a)
            runner.run(args_b)
            for name in ["results.csv", "ablation_results.csv", "summary.json"]:
                self.assertEqual(sha(a / name), sha(b / name))

    def test_collapse_ablation_scores_native_as_clique_expansion(self):
        benchmark = baselines.load_benchmark(BASE)
        _, metrics = baselines.run_model_suite(benchmark, ablation="collapse_to_clique_expansion", seed=20260517)
        by_model = {row["model"]: row for row in metrics}
        for key in ["flat_exact_match", "synonym_normalized_exact_match", "mean_hierarchy_distance"]:
            self.assertEqual(by_model["native_hypergraph"][key], by_model["clique_expansion"][key])


if __name__ == "__main__":
    unittest.main()
