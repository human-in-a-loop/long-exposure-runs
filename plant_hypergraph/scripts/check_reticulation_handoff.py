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
BIOLOGICAL_TABLES = {
    "chromosome_count_assertions.tsv": 12,
    "hybridization_events.tsv": 1,
    "polyploidization_events.tsv": 4,
    "reticulate_inheritance_evidence.tsv": 5,
}


def read_rows(path):
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def require(condition, message):
    if not condition:
        raise SystemExit(message)


def main():
    require(READINESS.exists(), f"missing {READINESS}")
    require(HANDOFF.exists(), f"missing {HANDOFF}")

    rows = {row["format"]: row for row in read_rows(READINESS)}
    for fmt in ["csv", "tsv", "json", "xlsx"]:
        require(fmt in rows, f"format_readiness.tsv missing {fmt}")

    for fmt in ["csv", "tsv"]:
        row = rows[fmt]
        require(row["advertised_support"] == "yes", f"{fmt} should be directly supported")
        require(row["dependency_available"] == "yes", f"{fmt} should not require optional dependencies")
        require("openpyxl" not in row["runtime_dependency"].lower(), f"{fmt} should not depend on openpyxl")

    xlsx = rows["xlsx"]
    xlsx_policy = xlsx["recommended_barrier1_policy"].lower()
    require(
        xlsx["dependency_available"].lower() == "yes" or "conversion" in xlsx_policy or "openpyxl" in xlsx_policy,
        "xlsx must be dependency-backed or conversion-required",
    )

    handoff_text = HANDOFF.read_text(encoding="utf-8")
    require("validated/access-limited" in handoff_text, "handoff must state validated/access-limited")
    require("scale-complete" not in handoff_text, "handoff must not use scale-complete framing")

    normalized = BASE / "normalized"
    for filename, expected_rows in BIOLOGICAL_TABLES.items():
        actual = len(read_rows(normalized / filename))
        require(actual == expected_rows, f"{filename} row count changed: expected {expected_rows}, got {actual}")

    print("reticulation handoff readiness checks passed")


if __name__ == "__main__":
    main()
