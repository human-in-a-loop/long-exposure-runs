"""Provenance-uniformity test for M1.6 domestication staging.

Every staged row must carry the schema §6 provenance block with:
  source_id, source_name, source_version_or_release, access_date,
  license, attribution, source_reliability.
"""
from pathlib import Path
import csv
import json
import sys

ROOT = Path("substrate/staging/domestication_sources")
REQUIRED_PROV_KEYS = {"source_id","source_name","source_version_or_release",
                       "access_date","license","attribution","source_reliability"}

def fail(msg):
    print("FAIL:", msg)
    sys.exit(1)

def check_nodes():
    n = 0
    for p in (ROOT / "nodes").glob("*.tsv"):
        with p.open() as f:
            r = csv.DictReader(f, delimiter="\t")
            for row in r:
                n += 1
                pj = json.loads(row["source_provenance_json"])
                missing = REQUIRED_PROV_KEYS - set(pj.keys())
                if missing:
                    fail(f"{p.name} row {row['node_id']}: missing prov keys {missing}")
    print(f"PASS: {n} node rows have uniform provenance")

def check_edges():
    n = 0
    for p in (ROOT / "edges").glob("*.tsv"):
        with p.open() as f:
            r = csv.DictReader(f, delimiter="\t")
            for row in r:
                n += 1
                for k in ("source_id","source_name","source_version_or_release",
                          "access_date","license","attribution","source_reliability"):
                    if not row.get(k):
                        fail(f"{p.name} row {row['raw_scientific_name']}: missing prov column {k}")
    print(f"PASS: {n} edge rows have uniform provenance")

def check_source_manifest():
    p = ROOT / "normalized" / "source_manifest.tsv"
    n = 0
    with p.open() as f:
        r = csv.DictReader(f, delimiter="\t")
        for row in r:
            n += 1
            for k in ("source_id","source_name","license","attribution","source_reliability","access_date"):
                if not row.get(k):
                    fail(f"source_manifest row {row.get('source_id')}: missing {k}")
    print(f"PASS: {n} sources in manifest with required fields")

if __name__ == "__main__":
    check_source_manifest()
    check_nodes()
    check_edges()
    print("ALL PROVENANCE-UNIFORMITY TESTS PASS")
