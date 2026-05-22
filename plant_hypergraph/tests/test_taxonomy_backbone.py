import subprocess
import unittest
from pathlib import Path

import pandas as pd

from tools.taxonomy_backbone_checks import check_base


BASE = Path("substrate/staging/taxonomy_backbone")
SMOKE = Path("substrate/staging/taxonomy_backbone_smoke")
M5_SAMPLE = Path("data/public_taxonomy_sample/v0.1")


class TaxonomyBackboneTests(unittest.TestCase):
    def test_full_staging_contract(self):
        messages = check_base(BASE, min_accepted=50_000)
        self.assertTrue(any(msg.startswith("accepted_taxa=") for msg in messages))

    def test_crosswalk_has_required_id_fields_and_nulls_are_preserved(self):
        crosswalk = pd.read_parquet(BASE / "source_crosswalk.parquet")
        for col in ("wfo_id", "ott_id", "powo_id", "gbif_taxon_key"):
            self.assertIn(col, crosswalk.columns)
        self.assertTrue((crosswalk[["ott_id", "powo_id", "gbif_taxon_key"]] == "").any().any())
        self.assertIn("wfo_only_not_attempted", set(crosswalk["disagreement_category"]))

    def test_synonym_rows_are_name_normalization_only(self):
        synonyms = pd.read_parquet(BASE / "synonym_clusters.parquet")
        self.assertFalse(synonyms.empty)
        self.assertTrue(synonyms["task_visibility"].eq("name_normalization_only").all())
        self.assertTrue(synonyms["allowed_evidence_scope"].str.contains("does not support trait").all())

    def test_smoke_run_outputs_pass_checks(self):
        subprocess.run(
            [
                "python3",
                "scripts/ingest_taxonomy_backbone.py",
                "--out-dir",
                str(SMOKE),
                "--limit",
                "250",
                "--crosswalk-limit",
                "20",
            ],
            check=True,
            stdout=subprocess.PIPE,
            text=True,
        )
        check_base(SMOKE, min_accepted=250)

    def test_prior_m5_public_sample_still_passes(self):
        result = subprocess.run(
            ["python3", "-m", "unittest", "tests/test_public_taxonomy_sample.py"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        self.assertIn("OK", result.stdout)
        self.assertTrue((M5_SAMPLE / "source_crosswalk.csv").exists())


if __name__ == "__main__":
    unittest.main()
