"""Held-out leakage gate for M1.6 domestication staging.

PURPOSE: enforces the falsification-criterion (d) from the M1.6 research
brief: no held-out validation crop may appear in the curated
crop_pedigree training set, or Wave-4 (M3.T4) validation against CGIAR
recommendations becomes uninterpretable.

NORMALIZATION RULE (load-bearing):
    Compare on (genus, species) lowercase only. Subspecies, variety,
    cultivar-group suffixes, and Linnaean authority are stripped before
    comparison. The "x" hybrid prefix on a species token is stripped
    (e.g. "Citrus x sinensis" -> ("citrus", "sinensis")). Comments in
    parentheses are stripped (e.g. "Daucus carota subsp. sativus" ->
    ("daucus", "carota")).

    This is the strictest reasonable normalization: it errs toward
    declaring overlap at species level even if the curated row carries
    a subspecies that the held-out row does not. The intent is that a
    held-out crop and a curated cultivar at the same species are still
    a leak, because Wave-4 will look up "what does the engine recommend
    for Solanum tuberosum" and the engine will have seen the species.

Auditor-blocking. Added cycle 2 in response to cycle-1 leakage failure
(20 of 22 held-out crops were in fact present in curated pedigree).
"""
from pathlib import Path
import csv
import json
import sys

ROOT = Path("substrate/staging/domestication_sources")
HELDOUT = ROOT / "heldout_validation_set.tsv"
CURATED = ROOT / "edges" / "crop_pedigree.tsv"


def normalize_taxon(raw: str) -> tuple:
    """Return (genus, species) lowercase tuple, or None if unparseable."""
    if not raw:
        return None
    s = raw.strip()
    # Strip parenthetical comments: "Pennisetum glaucum (Cenchrus americanus)"
    if "(" in s:
        s = s.split("(")[0].strip()
    # Strip everything after first " subsp.", " var.", " cv.", " f."
    for marker in (" subsp.", " var.", " cv.", " f.", " group"):
        idx = s.lower().find(marker)
        if idx > 0:
            s = s[:idx].strip()
    parts = s.split()
    if len(parts) < 2:
        return None
    genus = parts[0].lower()
    # Drop "x" hybrid prefix
    species_tok = parts[1].lower()
    if species_tok == "x" and len(parts) >= 3:
        species_tok = parts[2].lower()
    return (genus, species_tok)


def load_heldout_keys():
    keys = set()
    rows = 0
    with HELDOUT.open() as f:
        r = csv.DictReader(f, delimiter="\t")
        for row in r:
            rows += 1
            k = normalize_taxon(row["crop_taxon"])
            if k is None:
                print(f"FAIL: unparseable held-out taxon: {row['crop_taxon']!r}")
                sys.exit(1)
            keys.add(k)
    return keys, rows


def load_curated_keys():
    keys = set()
    rows = 0
    with CURATED.open() as f:
        r = csv.DictReader(f, delimiter="\t")
        for row in r:
            rows += 1
            roles = json.loads(row["node_roles_json"])
            # cultivar node_id has form "cultivar:Genus_species[_subspec...]"
            cultivar_node = roles.get("cultivar", "")
            taxon = cultivar_node.replace("cultivar:", "").replace("_", " ")
            k = normalize_taxon(taxon)
            if k is None:
                # also try raw_scientific_name as fallback
                k = normalize_taxon(row.get("raw_scientific_name", ""))
            if k is not None:
                keys.add(k)
    return keys, rows


def test_disjoint():
    heldout, hrows = load_heldout_keys()
    curated, crows = load_curated_keys()
    overlap = heldout & curated
    if overlap:
        print(f"FAIL: LEAKAGE — {len(overlap)} held-out crops appear in curated "
              f"crop_pedigree set:")
        for g, s in sorted(overlap):
            print(f"  ({g}, {s})")
        sys.exit(1)
    if hrows < 22:
        print(f"FAIL: held-out set has {hrows} rows, below ≥22 floor")
        sys.exit(1)
    print(f"PASS: 0 of {hrows} held-out crops appear in {crows} curated "
          f"crop_pedigree rows (normalized on (genus, species) lowercase)")


if __name__ == "__main__":
    test_disjoint()
    print("ALL HELD-OUT LEAKAGE TESTS PASS")
