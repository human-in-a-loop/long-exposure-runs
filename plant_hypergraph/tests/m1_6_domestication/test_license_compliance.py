"""License-compliance test for M1.6 domestication staging.

PURPOSE: WorldClim and CHELSA rasters MUST NOT be redistributed in the
substrate. This test scans substrate/staging/domestication_sources/ for any
file extension that would indicate a redistributed raster and fails if any
are found. Auditor-blocking.

Per directive: 'License caveat: WorldClim / CHELSA rasters cannot be
redistributed; stage climate-envelope feature vectors per taxon plus
citation, not raw rasters.'
"""
from pathlib import Path
import sys

ROOT = Path("substrate/staging/domestication_sources")
FORBIDDEN_EXTS = {".tif", ".tiff", ".geotiff", ".nc", ".bil", ".adf", ".asc",
                  ".bsq", ".bip", ".img", ".grd", ".rst", ".envi", ".hdr"}

def test_no_raster_files():
    if not ROOT.exists():
        print(f"FAIL: staging dir {ROOT} does not exist")
        sys.exit(1)
    found = []
    for p in ROOT.rglob("*"):
        if p.is_file() and p.suffix.lower() in FORBIDDEN_EXTS:
            found.append(str(p))
    if found:
        print("FAIL: forbidden raster files in staging tree:")
        for f in found:
            print(f"  {f}")
        sys.exit(1)
    print(f"PASS: no forbidden raster files in {ROOT} "
          f"(scanned for extensions: {sorted(FORBIDDEN_EXTS)})")

def test_citation_present():
    cit = ROOT / "climate_envelopes" / "CITATION.md"
    if not cit.exists():
        print(f"FAIL: required citation file missing: {cit}")
        sys.exit(1)
    text = cit.read_text()
    must_contain = ["WorldClim", "CHELSA", "Fick", "Karger", "CC-BY",
                    "NOT redistributed", "v2.1"]
    missing = [s for s in must_contain if s not in text]
    if missing:
        print(f"FAIL: CITATION.md missing required strings: {missing}")
        sys.exit(1)
    print("PASS: CITATION.md present and contains required attribution strings")

if __name__ == "__main__":
    test_no_raster_files()
    test_citation_present()
    print("ALL LICENSE-COMPLIANCE TESTS PASS")
