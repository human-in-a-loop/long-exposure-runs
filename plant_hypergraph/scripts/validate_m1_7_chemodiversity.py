# created: 2026-05-17T17:05:00Z
# cycle: 2
# run_id: fork-e34b5b2c1c6c-clone-5
# agent: worker
# milestone: M1.7
"""Validate M1.7 chemodiversity and ethnobotany staging outputs."""

from __future__ import annotations

import csv
import json
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "substrate" / "staging" / "chemodiversity_ethnobotany_sources"

REQUIRED_PHYTO = [
    "edge_id",
    "edge_type",
    "taxon_label_raw",
    "compound_id",
    "compound_label",
    "source_name",
    "source_record_id",
    "citation",
    "license_class",
    "access_date",
    "allowed_evidence_scope",
    "does_not_support",
    "confidence",
    "caveats",
]

REQUIRED_ETHNO = [
    "edge_id",
    "edge_type",
    "taxon_label_raw",
    "people_group",
    "source_name",
    "source_record_id",
    "source_citation",
    "license_class",
    "access_date",
    "allowed_evidence_scope",
    "does_not_support",
    "sovereignty_flag",
    "confidence",
    "caveats",
]


def read_tsv(name: str) -> list[dict[str, str]]:
    path = OUT / name
    if not path.exists():
        raise FileNotFoundError(path)
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def missing(row: dict[str, str], fields: list[str]) -> list[str]:
    return [field for field in fields if not (row.get(field) or "").strip()]


def main() -> int:
    failures: list[str] = []
    warnings: list[str] = []
    phyto = read_tsv("phytochemical_assertion_edges.tsv")
    ethno = read_tsv("ethnobotanical_use_assertion_edges.tsv")

    for idx, row in enumerate(phyto, start=2):
        blank = missing(row, REQUIRED_PHYTO)
        if blank:
            failures.append(f"phytochemical_assertion_edges.tsv:{idx} missing {','.join(blank)}")
        if row.get("edge_type") != "phytochemical_assertion":
            failures.append(f"phytochemical_assertion_edges.tsv:{idx} wrong edge_type={row.get('edge_type')}")
        forbidden = (row.get("does_not_support") or "").lower()
        for phrase in ["clinical efficacy", "safety", "taxon-typical"]:
            if phrase not in forbidden:
                failures.append(f"phytochemical_assertion_edges.tsv:{idx} does_not_support lacks '{phrase}'")

    sovereignty_sources = {"Native American Ethnobotany Database (Moerman), NAEB mirror", "PROTA", "PROSEA"}
    for idx, row in enumerate(ethno, start=2):
        blank = missing(row, REQUIRED_ETHNO)
        if blank:
            failures.append(f"ethnobotanical_use_assertion_edges.tsv:{idx} missing {','.join(blank)}")
        if row.get("edge_type") != "ethnobotanical_use_assertion":
            failures.append(f"ethnobotanical_use_assertion_edges.tsv:{idx} wrong edge_type={row.get('edge_type')}")
        if row.get("source_name") in sovereignty_sources:
            critical = missing(row, ["people_group", "source_citation", "access_date"])
            if critical:
                failures.append(f"ethnobotanical_use_assertion_edges.tsv:{idx} sovereignty-critical missing {','.join(critical)}")
            if row.get("sovereignty_flag") != "yes":
                failures.append(f"ethnobotanical_use_assertion_edges.tsv:{idx} sovereignty source missing sovereignty_flag=yes")
        forbidden = (row.get("does_not_support") or "").lower()
        for phrase in ["clinical bioactivity", "safety", "universality"]:
            if phrase not in forbidden:
                failures.append(f"ethnobotanical_use_assertion_edges.tsv:{idx} does_not_support lacks '{phrase}'")

    distinct_taxa = len({r["taxon_label_raw"] for r in phyto})
    distinct_compounds = len({r["compound_id"] for r in phyto})
    family_counts = Counter((r.get("family_raw") or "unknown").strip() for r in phyto)
    families_100 = sum(1 for count in family_counts.values() if count >= 100)

    if distinct_taxa < 1000:
        failures.append(f"coverage floor missed: distinct phytochemical taxa {distinct_taxa} < 1000")
    if distinct_compounds < 300:
        failures.append(f"coverage floor missed: distinct compounds {distinct_compounds} < 300")
    if families_100 < 8:
        failures.append(f"coverage floor missed: families with >=100 phytochemical assertions {families_100} < 8")

    if any("KNApSAcK" in r.get("source_name", "") or "NPASS" in r.get("source_name", "") for r in phyto):
        warnings.append("Restricted-source assertion rows present; verify they came from permitted local assertion TSVs, not raw bulk dumps.")

    result = {
        "status": "fail" if failures else "pass",
        "phytochemical_assertions": len(phyto),
        "ethnobotanical_assertions": len(ethno),
        "distinct_phytochemical_taxa": distinct_taxa,
        "distinct_compounds": distinct_compounds,
        "families_with_100_phytochemical_assertions": families_100,
        "top_family_counts": family_counts.most_common(20),
        "failures": failures[:200],
        "failure_count": len(failures),
        "warnings": warnings,
    }
    (OUT / "validation_report.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
