import csv
import hashlib
import json
import subprocess
import unittest
from pathlib import Path

from tools import source_sample_checks as checks


BASE = Path("data/public_taxonomy_sample/v0.1")
REQUIRED_FILES = {
    "seed_names.csv",
    "taxa.csv",
    "names.csv",
    "source_crosswalk.csv",
    "hyperedges.csv",
    "splits.csv",
    "metadata.json",
    "source_coverage.png",
}
REQUIRED_TAXA_COLUMNS = {"local_taxon_id", "source", "source_taxon_id", "canonical_name", "accepted_name", "rank", "parent_id", "status", "query_name"}
REQUIRED_NAME_COLUMNS = {"name_id", "name_string", "accepted_taxon_id", "source", "name_status", "leakage_group_id", "task_visibility"}
REQUIRED_EDGE_COLUMNS = {"edge_id", "edge_family", "node_id", "node_type", "role", "role_weight", "edge_weight", "provenance", "is_synthetic"}


def read_csv(path):
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def digest_outputs():
    names = ["taxa.csv", "names.csv", "source_crosswalk.csv", "hyperedges.csv", "splits.csv", "metadata.json"]
    return {name: hashlib.sha256((BASE / name).read_bytes()).hexdigest() for name in names}


class PublicTaxonomySampleTests(unittest.TestCase):
    def test_required_files_and_schema_exist(self):
        for rel_path in REQUIRED_FILES:
            self.assertTrue((BASE / rel_path).exists(), rel_path)
        for source in ("wfo", "gbif", "opentree"):
            self.assertGreaterEqual(len(list((BASE / "raw" / source).glob("*.json"))), 10)
        self.assertTrue(REQUIRED_TAXA_COLUMNS.issubset(read_csv(BASE / "taxa.csv")[0]))
        self.assertTrue(REQUIRED_NAME_COLUMNS.issubset(read_csv(BASE / "names.csv")[0]))
        self.assertTrue(REQUIRED_EDGE_COLUMNS.issubset(read_csv(BASE / "hyperedges.csv")[0]))

    def test_metadata_hashes_match_artifacts(self):
        metadata = json.loads((BASE / "metadata.json").read_text(encoding="utf-8"))
        actual_files = {str(path.relative_to(BASE)) for path in BASE.rglob("*") if path.is_file() and path.name != "metadata.json"}
        self.assertTrue(actual_files.issubset(set(metadata["hashes"])))
        self.assertEqual({}, checks.hash_mismatches(BASE))

    def test_cached_builder_rerun_is_stable_for_normalized_outputs(self):
        before = digest_outputs()
        subprocess.run(["python3", "scripts/build_public_taxonomy_sample.py", "--out-dir", str(BASE)], check=True, stdout=subprocess.PIPE, text=True)
        after = digest_outputs()
        self.assertEqual(before, after)

    def test_source_coverage_and_disagreement_are_preserved(self):
        coverage = checks.source_coverage_by_seed(BASE)
        self.assertGreaterEqual(sum(1 for count in coverage.values() if count >= 2), 10)
        categories = checks.disagreement_categories(BASE)
        self.assertTrue(categories - {"all_source_agreement"}, categories)
        crosswalk = read_csv(BASE / "source_crosswalk.csv")
        self.assertTrue(any(row["wfo_id"] and row["gbif_key"] and row["ott_id"] for row in crosswalk))

    def test_incidence_rows_are_unique_and_required_families_present(self):
        rows = read_csv(BASE / "hyperedges.csv")
        keys = {(r["edge_id"], r["node_id"], r["role"]) for r in rows}
        self.assertEqual(len(keys), len(rows))
        families = {row["edge_family"] for row in rows}
        self.assertIn("taxonomic_parentage", families)
        self.assertIn("synonym_cluster", families)
        self.assertIn("regional_checklist_context", families)
        self.assertNotIn("occurrence_provenance", families)
        self.assertNotIn("reticulate_or_hybrid_signal", families)

    def test_split_groups_do_not_cross_splits_and_synonym_visibility_is_limited(self):
        groups = checks.leakage_group_splits(BASE)
        self.assertTrue(groups)
        self.assertTrue(all(len(splits) == 1 for splits in groups.values()))
        names = read_csv(BASE / "names.csv")
        self.assertTrue(all(row["task_visibility"] == "name_normalization_only" for row in names))


if __name__ == "__main__":
    unittest.main()
