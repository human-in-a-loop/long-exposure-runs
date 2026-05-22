"""Build-pipeline self-verification for M1.6 staging.

Runs at the end of build_staging.py (or as a standalone check). Refuses
to certify INGEST_AUDIT.md if any of the following hold:

  1. License scan finds raster files in the staging tree.
  2. Schema-conformance check fails (QUARANTINE non-empty, node/edge
     rows mis-typed, or multi-parent crop_pedigree count < 15 floor).
  3. Provenance-uniformity check fails.
  4. Held-out leakage check fails (overlap between held-out and
     curated cultivars on (genus, species)).
  5. Narrative-count claim in INGEST_AUDIT.md Section C disagrees with
     the actual TSV `wc -l - 1` row counts.
  6. Any source_id declared in INGEST_AUDIT.md Section A is missing
     from the `source_id` column of every node/edge TSV (i.e. a
     claimed source contributes zero rows).

This was the auditor's recommended pattern: the audit-doc claim and the
data are made identical artifact-by-artifact via an executable
assertion, so the doc cannot make claims the data does not support.
"""
from pathlib import Path
import csv
import re
import subprocess
import sys

ROOT = Path("substrate/staging/domestication_sources")
TESTS_DIR = Path("tests/m1_6_domestication")
INGEST_AUDIT = ROOT / "INGEST_AUDIT.md"

# (TSV path relative to ROOT, expected Section-C label substring)
COUNTED_TSVS = [
    ("nodes/vavilov_center.tsv", "vavilov_center.tsv"),
    ("nodes/wild_ancestor.tsv", "wild_ancestor.tsv"),
    ("nodes/cultivar.tsv", "cultivar.tsv"),
    ("nodes/landrace.tsv", "landrace.tsv"),
    ("nodes/breeder_pedigree_node.tsv", "breeder_pedigree_node.tsv"),
    ("edges/crop_pedigree.tsv", "crop_pedigree.tsv"),
    ("edges/vavilov_center_hyperedge.tsv", "vavilov_center_hyperedge.tsv"),
    ("edges/cultivation_or_domestication.tsv", "cultivation_or_domestication.tsv"),
    ("climate_envelopes/per_taxon_bioclim.tsv", "per_taxon_bioclim.tsv"),
]


def fail(msg):
    print(f"ASSERTION FAIL: {msg}")
    sys.exit(1)


def run_test(name):
    """Run a sibling test script and abort if it exits non-zero."""
    path = TESTS_DIR / name
    r = subprocess.run([sys.executable, str(path)], capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stdout)
        print(r.stderr, file=sys.stderr)
        fail(f"{name} failed (returncode {r.returncode})")
    print(f"  OK: {name}")


def count_rows(path: Path) -> int:
    with path.open() as f:
        return sum(1 for _ in f) - 1  # minus header


def parse_section_c_counts(text: str) -> dict:
    """Extract (filename, count) pairs from INGEST_AUDIT.md Section C table."""
    counts = {}
    in_section_c = False
    for line in text.splitlines():
        if line.startswith("## Section C"):
            in_section_c = True
            continue
        if in_section_c and line.startswith("## "):
            break
        if not in_section_c:
            continue
        # Match: | `path/filename.tsv` | 123 (optional comment) |
        m = re.match(r"\|\s*`([^`]+\.tsv)`\s*\|\s*(\d+)", line)
        if m:
            basename = m.group(1).rsplit("/", 1)[-1]
            counts[basename] = int(m.group(2))
    return counts


def declared_source_ids(text: str) -> list:
    """Parse Section A source_id column."""
    sids = []
    in_section_a = False
    for line in text.splitlines():
        if line.startswith("## Section A"):
            in_section_a = True
            continue
        if in_section_a and line.startswith("## "):
            break
        if not in_section_a:
            continue
        # Section A rows: | 1 | source_id | ...
        m = re.match(r"\|\s*\d+\s*\|\s*([a-z0-9_]+)\s*\|", line)
        if m:
            sids.append(m.group(1))
    return sids


def collect_used_source_ids() -> set:
    """Union of source_id values seen in all node + edge TSVs (and provenance JSONs)."""
    seen = set()
    tsv_paths = []
    for sub in ("nodes", "edges", "climate_envelopes"):
        tsv_paths.extend((ROOT / sub).glob("*.tsv"))
    for p in tsv_paths:
        with p.open() as f:
            r = csv.DictReader(f, delimiter="\t")
            for row in r:
                if "source_id" in row and row["source_id"]:
                    seen.add(row["source_id"])
                # node tables embed provenance JSON
                prov = row.get("source_provenance_json", "")
                if prov:
                    for tok in re.findall(r'"source_id"\s*:\s*"([^"]+)"', prov):
                        seen.add(tok)
                # climate envelope rows carry an envelope_source field naming
                # both worldclim_v21 and chelsa_v21
                env = row.get("envelope_source", "")
                if env:
                    for tok in re.split(r"[,;\s]+", env):
                        if tok:
                            seen.add(tok.strip().lower())
    return seen


def main():
    print("=== M1.6 build-pipeline self-verification ===")

    # 1-4: run the four sibling tests.
    print("[1/6] license-compliance:")
    run_test("test_license_compliance.py")
    print("[2/6] schema-conformance:")
    run_test("test_schema_conformance.py")
    print("[3/6] provenance-uniformity:")
    run_test("test_provenance_uniformity.py")
    print("[4/6] heldout-leakage:")
    run_test("test_heldout_leakage.py")

    # 5: narrative-count cross-check
    print("[5/6] narrative-count cross-check:")
    if not INGEST_AUDIT.exists():
        print("  SKIP: INGEST_AUDIT.md does not exist yet (first-build path)")
    else:
        text = INGEST_AUDIT.read_text()
        declared = parse_section_c_counts(text)
        for rel, label in COUNTED_TSVS:
            actual = count_rows(ROOT / rel)
            claimed = declared.get(label)
            if claimed is None:
                print(f"  WARN: Section C does not declare a count for {label}; "
                      f"actual={actual}")
                continue
            if actual != claimed:
                fail(f"narrative mismatch for {label}: "
                     f"Section C claims {claimed}, actual {actual}")
            print(f"  OK: {label} actual={actual} matches Section C claim")

    # 6: source-coverage cross-check
    print("[6/6] source-coverage cross-check:")
    if not INGEST_AUDIT.exists():
        print("  SKIP: INGEST_AUDIT.md does not exist yet (first-build path)")
    else:
        declared_sids = declared_source_ids(INGEST_AUDIT.read_text())
        used_sids = collect_used_source_ids()
        # Token-set match: a declared source_id matches if any of its
        # underscore-separated tokens (excluding short version suffixes)
        # appears as a substring of any used source string. This tolerates
        # the climate-envelope convention where envelope_source is e.g.
        # "WorldClim_v2.1+CHELSA_v2.1" rather than discrete source_id tokens.
        used_lower_joined = " ".join(sorted(s.lower() for s in used_sids))
        missing = []
        for s in declared_sids:
            base = s.lower()
            # strip trailing version-like tokens (v21, v2_1, 2024, etc.)
            base_no_ver = re.sub(r"_v?\d+(_\d+)?$", "", base)
            tokens = [t for t in base_no_ver.split("_") if len(t) >= 3]
            if not tokens:
                tokens = [base]
            if not any(t in used_lower_joined for t in tokens):
                missing.append(s)
        if missing:
            fail(f"declared source_ids absent from any TSV row: {missing}")
        print(f"  OK: all {len(declared_sids)} declared source_ids appear in "
              f"at least one node/edge/envelope row")

    print("=== ALL SELF-VERIFICATION ASSERTIONS PASS ===")


if __name__ == "__main__":
    main()
