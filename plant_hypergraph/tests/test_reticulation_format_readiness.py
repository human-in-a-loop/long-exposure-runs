# created: 2026-05-17T19:08:00Z
# cycle: 2
# run_id: run-phytograph-cycle2-fanout-e34b5b2c1c6c-clone1
# agent: worker
# milestone: M1.3

import csv
from pathlib import Path


BASE = Path("substrate/staging/reticulation_sources")
READINESS = BASE / "normalized" / "format_readiness.tsv"
HANDOFF = BASE / "BARRIER1_HANDOFF.md"


def read_readiness():
    with READINESS.open(newline="", encoding="utf-8") as handle:
        return {row["format"]: row for row in csv.DictReader(handle, delimiter="\t")}


def test_format_readiness_file_declares_xlsx_policy():
    assert READINESS.exists()
    rows = read_readiness()
    assert "xlsx" in rows
    xlsx = rows["xlsx"]
    assert xlsx["advertised_support"] in {"conditional", "yes"}
    policy = xlsx["recommended_barrier1_policy"].lower()
    dependency_available = xlsx["dependency_available"].lower()
    assert dependency_available == "yes" or "conversion" in policy or "openpyxl" in policy


def test_csv_tsv_supported_without_optional_spreadsheet_dependency():
    rows = read_readiness()
    for fmt in ["csv", "tsv"]:
        row = rows[fmt]
        assert row["advertised_support"] == "yes"
        assert row["dependency_available"] == "yes"
        assert "openpyxl" not in row["runtime_dependency"].lower()


def test_handoff_language_preserves_access_limited_not_scale_complete():
    text = HANDOFF.read_text(encoding="utf-8")
    assert "validated/access-limited" in text
    assert "scale-complete" not in text

