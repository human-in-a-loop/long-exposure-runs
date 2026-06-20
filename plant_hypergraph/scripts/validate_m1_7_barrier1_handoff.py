# created: 2026-05-17T17:45:00Z
# cycle: 2
# run_id: fork-e34b5b2c1c6c-clone-5
# agent: worker
# milestone: M1.7
"""Validate M1.7 Barrier-1 handoff and source-bias derivative artifacts."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "substrate" / "staging" / "chemodiversity_ethnobotany_sources"

REQUIRED_ARTIFACTS = [
    "BARRIER1_HANDOFF.md",
    "source_bias_profile.tsv",
    "family_source_matrix.tsv",
    "leave_one_source_out_coverage.tsv",
    "source_bias_heatmap.png",
]

REQUIRED_PHYTO_FIELDS = {
    "source_name",
    "source_record_id",
    "citation",
    "access_date",
    "license_class",
    "allowed_evidence_scope",
    "does_not_support",
    "family_raw",
}

REQUIRED_ETHNO_FIELDS = {
    "source_name",
    "source_record_id",
    "source_citation",
    "access_date",
    "license_class",
    "allowed_evidence_scope",
    "does_not_support",
    "people_group",
    "family_raw",
}


def read_tsv(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def header(name: str) -> list[str]:
    with (OUT / name).open(encoding="utf-8", newline="") as fh:
        return next(csv.reader(fh, delimiter="\t"))


def nonblank(row: dict[str, str], field: str) -> bool:
    return bool((row.get(field) or "").strip())


def main() -> int:
    failures: list[str] = []
    warnings: list[str] = []

    for name in REQUIRED_ARTIFACTS:
        path = OUT / name
        if not path.exists():
            failures.append(f"missing required artifact: {name}")
        elif path.stat().st_size == 0:
            failures.append(f"empty required artifact: {name}")

    phyto_header = set(header("phytochemical_assertion_edges.tsv"))
    ethno_header = set(header("ethnobotanical_use_assertion_edges.tsv"))
    missing_phyto = sorted(REQUIRED_PHYTO_FIELDS - phyto_header)
    missing_ethno = sorted(REQUIRED_ETHNO_FIELDS - ethno_header)
    if missing_phyto:
        failures.append(f"phytochemical_assertion_edges.tsv missing merge-control fields: {','.join(missing_phyto)}")
    if missing_ethno:
        failures.append(f"ethnobotanical_use_assertion_edges.tsv missing merge-control fields: {','.join(missing_ethno)}")

    source_profile = read_tsv("source_bias_profile.tsv")
    family_matrix = read_tsv("family_source_matrix.tsv")
    leave_one = read_tsv("leave_one_source_out_coverage.tsv")

    for idx, row in enumerate(source_profile, start=2):
        count = int(row.get("assertion_count") or 0)
        for field in ["source_name", "edge_domain", "record_identifier_field", "citation_field"]:
            if not nonblank(row, field):
                failures.append(f"source_bias_profile.tsv:{idx} missing {field}")
        if count:
            for field in ["license_classes", "access_dates", "evidence_scopes"]:
                if not nonblank(row, field):
                    failures.append(f"source_bias_profile.tsv:{idx} nonzero row missing {field}")
        scope = (row.get("evidence_scopes") or "").lower()
        if "clinical efficacy" in scope or "clinical bioactivity" in scope or "safety" in scope:
            failures.append(f"source_bias_profile.tsv:{idx} evidence scope appears widened: {row.get('evidence_scopes')}")

    for idx, row in enumerate(family_matrix, start=2):
        total = int(row.get("total_assertions") or 0)
        if total:
            for field in [
                "family_raw",
                "source_name",
                "record_identifier_fields",
                "citation_fields",
                "license_classes",
                "access_dates",
                "evidence_scopes",
            ]:
                if not nonblank(row, field):
                    failures.append(f"family_source_matrix.tsv:{idx} nonzero row missing {field}")
        if "clinical" in (row.get("evidence_scopes") or "").lower():
            failures.append(f"family_source_matrix.tsv:{idx} evidence scope appears widened")

    scenarios = {r.get("scenario", "") for r in leave_one}
    needed = {
        "all_sources",
        "minus_source:Dr. Duke Phytochemical and Ethnobotanical Databases",
        "minus_source:Native American Ethnobotany Database (Moerman), NAEB mirror",
        "phytochemistry_only",
        "ethnobotany_only",
    }
    missing_scenarios = sorted(needed - scenarios)
    if missing_scenarios:
        failures.append(f"leave_one_source_out_coverage.tsv missing scenarios: {missing_scenarios}")

    for row in leave_one:
        if row.get("scenario") == "minus_source:Dr. Duke Phytochemical and Ethnobotanical Databases":
            if int(row["phytochemical_assertions"]) != 0:
                failures.append("minus Dr. Duke should remove all current phytochemical assertions")
        if row.get("scenario") == "minus_source:Native American Ethnobotany Database (Moerman), NAEB mirror":
            if int(row["ethnobotanical_assertions"]) >= 127564:
                failures.append("minus Moerman/NAEB did not reduce ethnobotanical assertions")

    ethno_sample = read_tsv("ethnobotanical_use_assertion_edges.tsv")
    if any(r.get("edge_type") != "ethnobotanical_use_assertion" for r in ethno_sample):
        failures.append("ethnobotanical_use_assertion_edges.tsv contains relabeled non-ethnobotanical edge_type")
    if any("bioactivity" in (r.get("allowed_evidence_scope") or "").lower() for r in ethno_sample):
        failures.append("ethnobotanical_use_assertion_edges.tsv allowed_evidence_scope mentions bioactivity")

    result = {
        "status": "fail" if failures else "pass",
        "checked_artifacts": REQUIRED_ARTIFACTS,
        "source_profile_rows": len(source_profile),
        "family_source_matrix_rows": len(family_matrix),
        "leave_one_source_out_rows": len(leave_one),
        "failures": failures[:100],
        "failure_count": len(failures),
        "warnings": warnings,
    }
    (OUT / "barrier1_handoff_validation_report.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
