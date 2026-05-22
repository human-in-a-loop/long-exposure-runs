import csv
import hashlib
import tempfile
import unittest
from pathlib import Path

from scripts import generate_synthetic_benchmark as gen


REQUIRED_TAXA_COLUMNS = {"taxon_id", "accepted_name", "rank", "parent_taxon_id", "family_id", "genus_id", "is_synthetic", "source_layer"}
REQUIRED_NAME_COLUMNS = {"name_id", "name_string", "accepted_taxon_id", "name_status", "source_layer", "leakage_group_id"}
REQUIRED_EDGE_COLUMNS = {"edge_id", "edge_family", "node_id", "node_type", "role", "role_weight", "edge_weight", "provenance", "is_synthetic"}
REQUIRED_EXAMPLE_COLUMNS = {"example_id", "observed_features_json", "noisy_label", "target_accepted_taxon_id", "target_rank_path", "case_type", "split", "leakage_group_id"}


def read_csv(path):
    with Path(path).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def digest_dir(path):
    hashes = {}
    for file_path in sorted(Path(path).glob("*")):
        if file_path.is_file():
            hashes[file_path.name] = hashlib.sha256(file_path.read_bytes()).hexdigest()
    return hashes


def make_args(out_dir, **overrides):
    defaults = {
        "seed": 777,
        "out_dir": str(out_dir),
        "n_families": 4,
        "genera_per_family": 3,
        "species_per_genus": 5,
        "synonym_rate": 0.45,
        "missing_rank_rate": 0.18,
        "reticulation_rate": 0.12,
        "trait_convergence_rate": 0.16,
        "occurrence_noise_rate": 0.12,
    }
    defaults.update(overrides)
    return type("Args", (), defaults)()


class SyntheticBenchmarkTests(unittest.TestCase):
    def test_generation_is_hash_stable_for_same_seed(self):
        with tempfile.TemporaryDirectory() as tmp:
            a = Path(tmp) / "a"
            b = Path(tmp) / "b"
            gen.generate(make_args(a))
            gen.generate(make_args(b))
            self.assertEqual(digest_dir(a), digest_dir(b))

    def test_required_columns_and_edge_families_exist(self):
        base = Path("data/synthetic_benchmark/v0.1")
        self.assertTrue(REQUIRED_TAXA_COLUMNS.issubset(read_csv(base / "taxa.csv")[0]))
        self.assertTrue(REQUIRED_NAME_COLUMNS.issubset(read_csv(base / "names.csv")[0]))
        self.assertTrue(REQUIRED_EDGE_COLUMNS.issubset(read_csv(base / "hyperedges.csv")[0]))
        self.assertTrue(REQUIRED_EXAMPLE_COLUMNS.issubset(read_csv(base / "examples.csv")[0]))
        families = {row["edge_family"] for row in read_csv(base / "hyperedges.csv")}
        self.assertTrue(set(gen.REQUIRED_EDGE_FAMILIES).issubset(families))

    def test_no_orphan_incidence_rows(self):
        base = Path("data/synthetic_benchmark/v0.1")
        taxa = {row["taxon_id"] for row in read_csv(base / "taxa.csv")}
        names = {row["name_id"] for row in read_csv(base / "names.csv")}
        allowed_prefixes = ("rank:", "trait:", "region:", "occ:", "observation:", "source:", "phylo:")
        for row in read_csv(base / "hyperedges.csv"):
            node_id = row["node_id"]
            self.assertTrue(node_id in taxa or node_id in names or node_id.startswith(allowed_prefixes), node_id)

    def test_split_leakage_groups_are_not_cross_split(self):
        base = Path("data/synthetic_benchmark/v0.1")
        split_by_group = {row["leakage_group_id"]: row["split"] for row in read_csv(base / "splits.csv")}
        self.assertEqual(len(split_by_group), len(read_csv(base / "splits.csv")))
        for row in read_csv(base / "examples.csv"):
            self.assertEqual(row["split"], split_by_group[row["leakage_group_id"]])

    def test_mechanisms_can_be_toggled_off_for_negative_control(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "negative"
            gen.generate(
                make_args(
                    out,
                    synonym_rate=0,
                    missing_rank_rate=0,
                    reticulation_rate=0,
                    trait_convergence_rate=0,
                    occurrence_noise_rate=0,
                )
            )
            edges = read_csv(out / "hyperedges.csv")
            names = read_csv(out / "names.csv")
            self.assertFalse(any(row["edge_family"] == "reticulate_or_hybrid_signal" for row in edges))
            self.assertFalse(any(row["edge_family"] == "missing_rank_bridge" for row in edges))
            self.assertFalse(any(row["provenance"] == "synthetic_trait_convergence_trap" for row in edges))
            self.assertFalse(any(row["name_status"] in {"synonym", "renamed_label"} for row in names))

    def test_reticulate_edges_have_two_source_lineages_and_convergence_is_distant(self):
        base = Path("data/synthetic_benchmark/v0.1")
        taxa = {row["taxon_id"]: row for row in read_csv(base / "taxa.csv")}
        edge_rows = read_csv(base / "hyperedges.csv")
        by_edge = {}
        for row in edge_rows:
            by_edge.setdefault(row["edge_id"], []).append(row)
        reticulate = [rows for rows in by_edge.values() if rows[0]["edge_family"] == "reticulate_or_hybrid_signal"]
        self.assertTrue(reticulate)
        for rows in reticulate:
            sources = [r["node_id"] for r in rows if r["role"] == "source_lineage"]
            self.assertGreaterEqual(len(set(sources)), 2)
        convergence = [rows for rows in by_edge.values() if rows[0]["provenance"] == "synthetic_trait_convergence_trap"]
        self.assertTrue(convergence)
        for rows in convergence:
            taxon_members = [r["node_id"] for r in rows if r["node_type"] == "taxon"]
            families = {taxa[t]["family_id"] for t in taxon_members}
            self.assertGreaterEqual(len(families), 2)


if __name__ == "__main__":
    unittest.main()
