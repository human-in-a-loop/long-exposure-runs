"""
Schema-conformance test for paleobotany_sources clone staged output.

Stdlib-only (pytest not available in sandbox). Run as:
    python3 -m unittest substrate.staging.paleobotany_sources.tests.test_schema_conformance -v
or:
    python3 substrate/staging/paleobotany_sources/tests/test_schema_conformance.py
"""

from __future__ import annotations
import unittest, os, sys, json, glob

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)  # paleobotany_sources/
sys.path.insert(0, ROOT)
from _lib.provenance import (
    ALLOWED_NODE_TYPES, ALLOWED_EDGE_TYPES, REQUIRED_PROV_FIELDS, read_jsonl,
)


SIDECAR_BASENAMES = {"source_citations.jsonl"}


def all_jsonl(root):
    paths = []
    for d, _, fs in os.walk(root):
        if "/QUARANTINE" in d or "/tests" in d or "/_lib" in d:
            continue
        for f in fs:
            if f.endswith(".jsonl") and f not in SIDECAR_BASENAMES:
                paths.append(os.path.join(d, f))
    return paths


class TestSchemaConformance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = []
        for path in all_jsonl(ROOT):
            for r in read_jsonl(path):
                cls.rows.append((path, r))
        assert len(cls.rows) > 0, "no rows staged — something is wrong"

    def test_row_kind_present(self):
        for path, r in self.rows:
            with self.subTest(path=path):
                self.assertIn("row_kind", r)
                self.assertIn(r["row_kind"], {"node", "edge"})

    def test_node_types_allowed(self):
        for path, r in self.rows:
            if r["row_kind"] != "node":
                continue
            self.assertIn(r["node_type"], ALLOWED_NODE_TYPES,
                          msg=f"unknown node_type {r['node_type']} in {path}")

    def test_edge_types_allowed(self):
        for path, r in self.rows:
            if r["row_kind"] != "edge":
                continue
            self.assertIn(r["edge_type"], ALLOWED_EDGE_TYPES,
                          msg=f"unknown edge_type {r['edge_type']} in {path}")

    def test_provenance_fields(self):
        for path, r in self.rows:
            with self.subTest(path=path, kind=r["row_kind"]):
                self.assertIn("provenance", r)
                p = r["provenance"]
                missing = REQUIRED_PROV_FIELDS - set(p.keys())
                self.assertEqual(missing, set(),
                                 msg=f"missing provenance fields {missing} in {path}")
                # confidence and source_reliability ∈ [0,1]
                self.assertGreaterEqual(p["confidence"], 0.0)
                self.assertLessEqual(p["confidence"], 1.0)
                self.assertGreaterEqual(p["source_reliability"], 0.0)
                self.assertLessEqual(p["source_reliability"], 1.0)

    def test_extinct_fauna_have_T_and_range(self):
        """Per brief: ≥200 extinct_fauna nodes WITH BOTH T and a non-null range citation."""
        ef_with_T_and_range = []
        for path, r in self.rows:
            if r.get("node_type") != "extinct_fauna":
                continue
            has_T = "T" in r and isinstance(r["T"], dict) and len(r["T"]) > 0
            has_range = (r.get("C", {}).get("geographic_scope") not in (None, "")
                         or r.get("attrs", {}).get("continent_or_region") not in (None, ""))
            if has_T and has_range:
                ef_with_T_and_range.append(r["node_id"])
        self.assertGreaterEqual(
            len(ef_with_T_and_range), 200,
            msg=f"M1.4 floor not met: only {len(ef_with_T_and_range)} extinct_fauna nodes with T+range"
        )

    def test_anachronism_edges_all_cited(self):
        """Falsification condition: any anachronism_candidate_edge without
        an explicit literature citation invalidates this clone."""
        uncited = []
        for path, r in self.rows:
            if r.get("edge_type") != "anachronism_candidate_edge":
                continue
            cav = r.get("C", {})
            cite = cav.get("primary_citation_short")
            full = cav.get("primary_citation_full")
            page = cav.get("primary_citation_page")
            if not (cite and full and page):
                uncited.append((path, r["edge_id"]))
        self.assertEqual(uncited, [],
                         msg=f"FALSIFICATION: anachronism edges without citation: {uncited}")

    def test_distribution_edges_have_range_type_code(self):
        """Faurby & Svenning present-natural vs current must be preserved verbatim."""
        bad = []
        for path, r in self.rows:
            if r.get("edge_type") != "distribution":
                continue
            cav = r.get("C", {})
            if "range_type_code" not in cav:
                bad.append((path, r["edge_id"]))
        self.assertEqual(bad, [], msg=f"distribution edges missing range_type_code: {bad}")

    def test_iucn_polygons_not_redistributed(self):
        """Falsification condition: raw IUCN polygons in staging dir."""
        # Check for any geojson or shapefile under iucn/
        bad = []
        for d, _, fs in os.walk(os.path.join(ROOT, "iucn")):
            for f in fs:
                if f.endswith((".geojson", ".shp", ".kml", ".gpkg")):
                    bad.append(os.path.join(d, f))
        self.assertEqual(bad, [], msg=f"IUCN raw polygon found in staging (license violation): {bad}")

    def test_provenance_clone_id_uniform(self):
        from _lib.provenance import CLONE_ID
        for path, r in self.rows:
            with self.subTest(path=path):
                self.assertEqual(r["provenance"]["ingest_clone_id"], CLONE_ID)

    def test_confidence_not_collapsed_to_scalar_for_T(self):
        """Per brief: every T block carries verbatim source-stated range, not a scalar collapse."""
        bad = []
        for path, r in self.rows:
            if r.get("node_type") not in ("extinct_fauna", "paleo_context"):
                continue
            T = r.get("T")
            if T is None:
                continue
            # T must be a dict with at least 2 fields beyond a single date
            if not isinstance(T, dict) or len(T) < 2:
                bad.append((path, r.get("node_id"), T))
        self.assertEqual(bad, [], msg=f"T blocks collapsed to scalar (forbidden): {bad}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
