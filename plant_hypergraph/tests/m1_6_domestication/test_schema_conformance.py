"""Schema conformance test for M1.6 domestication staging.

Validates that every staged row conforms to phytograph_schema.md v1.0
domestication-edge/node specs. QUARANTINE must be empty.
"""
from pathlib import Path
import csv
import json
import sys

ROOT = Path("substrate/staging/domestication_sources")

# Allowed edge types and required role keys per schema v1.0
EDGE_ROLE_REQUIREMENTS = {
    "crop_pedigree": {"required_any_of": [["cultivar"], ["taxon"]],
                      "required": ["wild_ancestors", "selection_traits", "region", "source"]},
    "vavilov_center_hyperedge": {"required": ["crop_taxon", "vavilov_center", "region", "source"]},
    "cultivation_or_domestication": {"required": ["taxon", "cultivation_status", "region", "source"]},
}
NODE_TYPES = {"cultivar", "wild_ancestor", "landrace", "breeder_pedigree_node", "vavilov_center"}

def fail(msg):
    print("FAIL:", msg)
    sys.exit(1)

def check_quarantine_empty():
    q = ROOT / "QUARANTINE"
    contents = [p for p in q.rglob("*") if p.is_file()]
    if contents:
        fail(f"QUARANTINE not empty: {len(contents)} files")
    print("PASS: QUARANTINE empty")

def check_node_files():
    n = 0
    for p in (ROOT / "nodes").glob("*.tsv"):
        with p.open() as f:
            r = csv.DictReader(f, delimiter="\t")
            for row in r:
                n += 1
                if row["node_type"] not in NODE_TYPES:
                    fail(f"{p.name}: unknown node_type {row['node_type']}")
                if not row["node_id"]:
                    fail(f"{p.name}: empty node_id")
                if not row["allowed_evidence_scope"]:
                    fail(f"{p.name}: empty allowed_evidence_scope")
                try:
                    json.loads(row["source_provenance_json"])
                except Exception as e:
                    fail(f"{p.name}: source_provenance_json not valid JSON: {e}")
    print(f"PASS: {n} node rows conform")

def check_edge_files():
    n = 0
    for p in (ROOT / "edges").glob("*.tsv"):
        et = p.stem
        if et not in EDGE_ROLE_REQUIREMENTS:
            fail(f"{p.name}: edge type {et} not in schema requirements")
        spec = EDGE_ROLE_REQUIREMENTS[et]
        with p.open() as f:
            r = csv.DictReader(f, delimiter="\t")
            for row in r:
                n += 1
                if row["edge_type"] != et:
                    fail(f"{p.name}: edge_type mismatch in row")
                try:
                    roles = json.loads(row["node_roles_json"])
                except Exception as e:
                    fail(f"{p.name}: node_roles_json not valid JSON: {e}")
                for key in spec.get("required", []):
                    if key not in roles:
                        fail(f"{p.name}: missing required role key '{key}' in row "
                             f"(roles={list(roles.keys())})")
                if "required_any_of" in spec:
                    if not any(all(k in roles for k in alt) for alt in spec["required_any_of"]):
                        fail(f"{p.name}: missing required_any_of group")
                if et == "crop_pedigree":
                    wa = roles.get("wild_ancestors", [])
                    if not wa:
                        fail(f"crop_pedigree row has no wild_ancestors: {row['raw_scientific_name']}")
    print(f"PASS: {n} edge rows conform")

def check_multi_parent_floor():
    p = ROOT / "edges" / "crop_pedigree.tsv"
    multi = 0
    with p.open() as f:
        r = csv.DictReader(f, delimiter="\t")
        for row in r:
            roles = json.loads(row["node_roles_json"])
            if len(roles.get("wild_ancestors", [])) >= 2:
                multi += 1
    if multi < 15:
        fail(f"multi-parent crop_pedigree count {multi} below 15 floor for non-data-limited")
    print(f"PASS: {multi} multi-parent crop_pedigree edges (>=15 floor)")

if __name__ == "__main__":
    check_quarantine_empty()
    check_node_files()
    check_edge_files()
    check_multi_parent_floor()
    print("ALL SCHEMA-CONFORMANCE TESTS PASS")
