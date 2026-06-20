# created: 2026-05-17T18:05:00Z
# cycle: 2
# run_id: run-phytograph-cycle2-fanout-e34b5b2c1c6c-clone1
# agent: worker
# milestone: M1.3

import csv
import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from scripts import reticulation_bulk_intake as intake


COMMON_ARGS = [
    "--source-version",
    "fixture-v1",
    "--access-date",
    "2026-05-17",
    "--license",
    "fixture license, not for biological use",
    "--attribution",
    "PhytoGraph synthetic fixture",
    "--acquisition-route",
    "local synthetic test fixture",
]


def write_csv(path, rows, fields):
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def read_tsv(path):
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def run_intake(argv):
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        return intake.main(argv)


class ReticulationBulkIntakeTests(unittest.TestCase):
    def test_ccdb_fixture_count_forms_do_not_create_events(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            source = tmp_path / "counts.csv"
            out = tmp_path / "out"
            write_csv(
                source,
                [
                    {"scientific_name": "Alpha beta", "chromosome_count": "n=7", "record_id": "ccdb-1"},
                    {"scientific_name": "Gamma delta", "chromosome_count": "2n=14-16", "record_id": "ccdb-2"},
                    {"scientific_name": "Epsilon zeta", "chromosome_count": "ca. 2n=28", "record_id": "ccdb-3"},
                    {"scientific_name": "Eta theta", "chromosome_count": "2n=42+B", "record_id": "ccdb-4"},
                ],
                ["scientific_name", "chromosome_count", "record_id"],
            )
            run_intake(["--source", "ccdb", "--input", str(source), "--output-dir", str(out), *COMMON_ARGS])

            rows = read_tsv(out / "chromosome_count_assertions.tsv")
            self.assertEqual(len(rows), 4)
            self.assertEqual(rows[0]["count_type"], "n")
            self.assertEqual(rows[1]["is_range"], "True")
            self.assertEqual(rows[2]["is_approximate"], "True")
            self.assertEqual(rows[3]["is_mixed_or_irregular"], "True")
            self.assertFalse((out / "polyploidization_events.tsv").exists())
            self.assertTrue(all(row["edge_type"] == "chromosome_count_assertion" for row in rows))

    def test_curated_event_fixture_writes_event_and_evidence_rows(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            source = tmp_path / "events.csv"
            out = tmp_path / "out"
            write_csv(
                source,
                [
                    {
                        "child": "Brassica napus",
                        "event_type": "polyploidization_event",
                        "parent1": "Brassica rapa",
                        "parent2": "Brassica oleracea",
                        "record_id": "evt-1",
                    },
                    {
                        "child": "Spartina anglica",
                        "event_type": "hybridization_event",
                        "parent_taxa_json": json.dumps(["Spartina alterniflora", "Spartina maritima"]),
                        "record_id": "evt-2",
                    },
                ],
                ["child", "event_type", "parent1", "parent2", "parent_taxa_json", "record_id"],
            )
            run_intake(["--source", "curated_events", "--input", str(source), "--output-dir", str(out), *COMMON_ARGS])

            poly = read_tsv(out / "polyploidization_events.tsv")
            hybrid = read_tsv(out / "hybridization_events.tsv")
            evidence = read_tsv(out / "reticulate_inheritance_evidence.tsv")
            self.assertEqual(len(poly), 1)
            self.assertEqual(len(hybrid), 1)
            self.assertEqual(len(evidence), 2)
            roles = json.loads(poly[0]["node_roles_json"])
            self.assertEqual(len(roles["parent_taxa"]), 2)

    def test_plant_cvalues_fixture_stages_caveated_ploidy_context(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            source = tmp_path / "cvalues.csv"
            out = tmp_path / "out"
            write_csv(
                source,
                [{"taxon": "Triticum aestivum", "ploidy": "hexaploid", "record_id": "cval-1"}],
                ["taxon", "ploidy", "record_id"],
            )
            run_intake(["--source", "plant_dna_cvalues", "--input", str(source), "--output-dir", str(out), *COMMON_ARGS])

            rows = read_tsv(out / "ploidy_state_assertions.tsv")
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["edge_type"], "reticulate_inheritance_evidence")
            self.assertEqual(rows[0]["ploidy_assertion_status"], "inferred_supporting_evidence_not_event")
            self.assertTrue(json.loads(rows[0]["caveats_json"])["not_established_source_fact"])

    def test_missing_run_license_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            source = tmp_path / "counts.csv"
            write_csv(source, [{"taxon": "Alpha beta", "count": "2n=14", "record_id": "ccdb-1"}], ["taxon", "count", "record_id"])
            with self.assertRaises(SystemExit):
                run_intake(
                    [
                        "--source",
                        "ccdb",
                        "--input",
                        str(source),
                        "--source-version",
                        "fixture-v1",
                        "--access-date",
                        "2026-05-17",
                        "--license",
                        "",
                        "--attribution",
                        "fixture",
                        "--acquisition-route",
                        "fixture",
                    ]
                )

    def test_missing_row_source_record_id_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            source = tmp_path / "counts.csv"
            write_csv(source, [{"taxon": "Alpha beta", "count": "2n=14"}], ["taxon", "count"])
            with self.assertRaisesRegex(ValueError, "source_record_id"):
                run_intake(["--source", "ccdb", "--input", str(source), "--output-dir", str(tmp_path / "out"), *COMMON_ARGS])

    def test_one_parent_event_rejects_or_demotes_only_when_explicit(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            source = tmp_path / "events.csv"
            write_csv(
                source,
                [{"child": "Hybrid example", "event_type": "hybridization_event", "parent1": "Parent one", "record_id": "evt-1"}],
                ["child", "event_type", "parent1", "record_id"],
            )
            with self.assertRaisesRegex(ValueError, "fewer than two parent"):
                run_intake(["--source", "curated_events", "--input", str(source), "--output-dir", str(tmp_path / "reject"), *COMMON_ARGS])

            out = tmp_path / "demote"
            run_intake(["--source", "curated_events", "--input", str(source), "--output-dir", str(out), "--demote-one-parent", *COMMON_ARGS])
            rows = read_tsv(out / "reticulate_inheritance_evidence.tsv")
            self.assertEqual(len(rows), 1)
            self.assertIn("insufficient parent roles", rows[0]["allowed_evidence_scope"])


if __name__ == "__main__":
    unittest.main()
