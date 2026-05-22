# created: 2026-05-17T17:05:00Z
# cycle: 2
# run_id: run-phytograph-cycle2-fanout-e34b5b2c1c6c-clone7
# agent: worker
# milestone: M1.9
"""Schema and safety tests for M1.9 Wikidata/Commons staging."""

from __future__ import annotations

import csv
import pathlib

BASE = pathlib.Path(__file__).resolve().parents[1]
DATA = BASE / "data"


def rows(path: pathlib.Path) -> list[dict]:
    with path.open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def test_required_files_exist() -> None:
    for name in ["wikidata_taxon_crosswalk.tsv", "commons_media_metadata.tsv", "image_evidence_edges.tsv"]:
        assert (DATA / name).exists(), name


def test_crosswalk_required_columns_and_threshold_or_data_limited_note() -> None:
    path = DATA / "wikidata_taxon_crosswalk.tsv"
    with path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        required = {"wikidata_qid", "wikidata_url", "taxon_name", "retrieved_at"}
        assert required.issubset(reader.fieldnames or [])
        data = list(reader)
    assert all(row["wikidata_qid"] and row["taxon_name"] for row in data)
    audit = (BASE / "INGEST_AUDIT.md").read_text(encoding="utf-8") if (BASE / "INGEST_AUDIT.md").exists() else ""
    assert len(data) >= 30000 or "Crosswalk status: data-limited" in audit


def test_media_required_columns_and_no_image_bytes() -> None:
    path = DATA / "commons_media_metadata.tsv"
    with path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        required = {
            "wikidata_qid",
            "commons_file_title",
            "commons_page_url",
            "file_url",
            "license_short_name",
            "license_url",
            "attribution",
            "retrieved_at",
        }
        assert required.issubset(reader.fieldnames or [])
        data = list(reader)
    audit = (BASE / "INGEST_AUDIT.md").read_text(encoding="utf-8") if (BASE / "INGEST_AUDIT.md").exists() else ""
    assert len({row["wikidata_qid"] for row in data}) >= 10000 or "Media status: data-limited" in audit
    forbidden_suffixes = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".tif", ".tiff", ".svg"}
    files = [p for p in DATA.rglob("*") if p.is_file()]
    assert not [p for p in files if p.suffix.lower() in forbidden_suffixes]


def test_image_evidence_scope_is_strict() -> None:
    data = rows(DATA / "image_evidence_edges.tsv")
    assert data
    assert {row["edge_type"] for row in data} == {"image_evidence"}
    assert {row["allowed_evidence_scope"] for row in data} == {"media_display;weak_morphology_inspection"}
    assert {
        row["disallowed_evidence_scope"] for row in data
    } == {"taxonomy;distribution;native_status;edibility;toxicity;human_use;biological_importance"}


def test_license_and_attribution_missingness_is_reported() -> None:
    data = rows(DATA / "commons_media_metadata.tsv")
    missing_license = sum(1 for row in data if not row["license_short_name"] and not row["license_url"])
    missing_attribution = sum(1 for row in data if not row["attribution"] and not row["artist"] and not row["credit"])
    audit_path = BASE / "INGEST_AUDIT.md"
    assert audit_path.exists()
    audit = audit_path.read_text(encoding="utf-8")
    assert f"media rows missing license: {missing_license}" in audit
    assert f"media rows missing attribution: {missing_attribution}" in audit
