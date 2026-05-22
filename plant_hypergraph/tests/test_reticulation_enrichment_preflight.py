# created: 2026-05-17T20:10:00Z
# cycle: 2
# run_id: run-phytograph-cycle2-fanout-e34b5b2c1c6c-clone1
# agent: worker
# milestone: M2.T1-preflight

import csv
from pathlib import Path


BASE = Path("tracks/track1/reticulation_enrichment")
FEATURES = BASE / "seed_enrichment_features.tsv"
EXPECTATIONS = BASE / "seed_case_expectations.tsv"
AUDIT = BASE / "PREFLIGHT_AUDIT.md"
FIGURE = BASE / "plots" / "seed_evidence_class_matrix.png"

ALLOWED_EVIDENCE_CLASSES = {
    "chromosome_count_assertion",
    "ploidy_context",
    "hybridization_event",
    "polyploidization_event",
    "reticulate_inheritance_evidence",
}

REQUIRED_PROVENANCE = {
    "source_count",
    "source_ids",
    "source_names",
    "source_versions",
    "access_dates",
    "licenses",
    "allowed_support_summary",
}


def read_rows(path):
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def feature_by_name():
    return {row["raw_scientific_name"]: row for row in read_rows(FEATURES)}


def test_preflight_outputs_exist():
    assert FEATURES.exists()
    assert EXPECTATIONS.exists()
    assert AUDIT.exists()
    assert FIGURE.exists()
    assert FIGURE.stat().st_size > 1000


def test_canonical_event_supported_positive_controls():
    rows = feature_by_name()
    for name in [
        "Triticum aestivum",
        "Brassica napus",
        "Spartina anglica",
        "Tragopogon mirus",
        "Tragopogon miscellus",
    ]:
        row = rows[name]
        assert row["reticulation_seed_flag"] == "true"
        assert row["event_supported_flag"] == "true"
        assert int(row["explicit_parent_count"]) >= 2
        assert (
            int(row["hybridization_event_count"])
            + int(row["polyploidization_event_count"])
            + int(row["reticulate_inheritance_evidence_count"])
        ) > 0


def test_count_only_taxa_remain_event_free():
    rows = feature_by_name()
    count_only_taxa = [
        name
        for name, row in rows.items()
        if row["count_only_flag"] == "true"
    ]
    assert count_only_taxa
    for name in count_only_taxa:
        row = rows[name]
        assert int(row["chromosome_count_assertion_count"]) > 0
        assert row["event_supported_flag"] == "false"
        assert int(row["hybridization_event_count"]) == 0
        assert int(row["polyploidization_event_count"]) == 0
        assert int(row["reticulate_inheritance_evidence_count"]) == 0


def test_arabidopsis_negative_control_has_no_event_support():
    row = feature_by_name()["Arabidopsis thaliana"]
    assert row["canonical_node_id"] == "raw_name:Arabidopsis_thaliana"
    assert row["reticulation_seed_flag"] == "true"
    assert row["count_only_flag"] == "false"
    assert row["event_supported_flag"] == "false"
    assert int(row["hybridization_event_count"]) == 0
    assert int(row["polyploidization_event_count"]) == 0
    assert int(row["reticulate_inheritance_evidence_count"]) == 0


def test_no_schema_drift_or_taxonomy_backbone_ids():
    for row in read_rows(FEATURES):
        assert row["canonical_node_id"].startswith("raw_name:")
        assert not row["canonical_node_id"].startswith(("WFO:", "GBIF:", "OTT:"))
        evidence_classes = set(row["evidence_classes"].split("|"))
        assert evidence_classes <= ALLOWED_EVIDENCE_CLASSES


def test_required_provenance_summaries_present():
    for row in read_rows(FEATURES):
        for field in REQUIRED_PROVENANCE:
            assert row[field], f"{row['raw_scientific_name']} missing {field}"
        assert int(row["source_count"]) >= 1


def test_case_expectations_match_observed_features():
    for row in read_rows(EXPECTATIONS):
        assert row["expected_reticulation_seed_flag"] == row["observed_reticulation_seed_flag"]
        assert row["expected_event_supported_flag"] == row["observed_event_supported_flag"]
        assert row["expected_count_only_flag"] == row["observed_count_only_flag"]


def test_audit_is_scale_honest():
    text = AUDIT.read_text(encoding="utf-8")
    assert "seed-scale" in text
    assert "validated/access-limited" in text
    assert "production-scale complete" not in text
