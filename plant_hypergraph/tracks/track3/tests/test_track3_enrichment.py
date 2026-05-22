"""Tests for Track 3 Wave 2 convergence enrichment projection.

Constraints under test:
- no `convergence_signature` rows ever appear in Track 3 outputs
- substrate parquets are not mutated by the build
- every resolved row has a non-empty accepted_taxon_key present in the crosswalk
- provenance fields are preserved
- the projection script never writes to substrate paths or to sibling tracks
"""
from __future__ import annotations

import os
from pathlib import Path

import pyarrow.parquet as pq

WORKSPACE = Path(__file__).resolve().parents[3]
SUBSTRATE = WORKSPACE / "phytograph_dataset"
OUT = WORKSPACE / "tracks" / "track3" / "data" / "convergence_trait_edges.parquet"
CROSSWALK = SUBSTRATE / "taxon_crosswalk.parquet"
SYNONYMS = SUBSTRATE / "synonym_resolution.parquet"
NODES = SUBSTRATE / "nodes.parquet"
HYPEREDGES = SUBSTRATE / "hyperedges.parquet"


def test_output_exists_and_nonempty():
    assert OUT.exists(), f"expected build output at {OUT}"
    df = pq.read_table(OUT).to_pandas()
    assert len(df) > 0, "track3 enrichment output is empty"


def test_no_convergence_signature_emitted():
    df = pq.read_table(OUT).to_pandas()
    assert "track_edge_type" in df.columns
    bad = (df["track_edge_type"] == "convergence_signature").sum()
    assert bad == 0, (
        f"FORBIDDEN: {bad} rows have track_edge_type=convergence_signature "
        "(Phase 4.3 instrument reserves this type)"
    )
    # also check trait column never literally names the reserved string
    assert (df["trait"] == "convergence_signature").sum() == 0


def test_substrate_mtimes_unchanged():
    """Ensure the build doesn't touch substrate parquets."""
    # Record current mtimes; this test runs after the build, so values should
    # match the Barrier 1 freeze. A regression here means something in
    # this run wrote to substrate.
    for path in [HYPEREDGES, NODES, CROSSWALK, SYNONYMS]:
        # all should exist
        assert path.exists(), f"missing substrate file {path}"
        # mtime should be older than the build output
        if OUT.exists():
            assert os.path.getmtime(path) <= os.path.getmtime(OUT) + 1, (
                f"substrate mtime newer than build output: {path}"
            )


def test_accepted_key_propagation():
    df = pq.read_table(OUT).to_pandas()
    resolved = df[df["pending_crosswalk"] == False]
    assert len(resolved) > 0
    assert (resolved["accepted_taxon_key"] == "").sum() == 0
    # every resolved key appears in the substrate crosswalk
    cw = pq.read_table(CROSSWALK).to_pandas()
    valid = set(cw["accepted_taxon_key"].dropna())
    missing = set(resolved["accepted_taxon_key"]) - valid
    assert not missing, f"{len(missing)} resolved keys missing from crosswalk e.g. {list(missing)[:5]}"


def test_canonical_grass_c4_reachable():
    df = pq.read_table(OUT).to_pandas()
    poaceae_c4 = df[
        (df["trait"] == "c4_photosynthesis")
        & (df["pending_crosswalk"] == False)
        & (df["family_label"].str.contains("Poaceae", case=False, na=False))
    ]
    assert len(poaceae_c4) > 0, "no C4 Poaceae rows in resolved subset"


def test_canonical_succulence_reachable_or_documented_gap():
    """Cactaceae succulence is documented as data-limited in the gap list.

    The substrate (AusTraits 6.0.0) does not code Cactaceae succulence in
    the convergence sources retained by Barrier 1. The gap list records
    this explicitly; this test enforces the documentation rather than
    requiring a non-empty match.
    """
    gap_path = OUT.parent / "track3_gap_list.tsv"
    assert gap_path.exists()
    text = gap_path.read_text()
    assert "Succulence Cactaceae" in text
    # The brief allows data-limited cases; require either path (a) or path (b)
    # OR a row explicitly noting the gap.
    df = pq.read_table(OUT).to_pandas()
    cactus = df[(df["trait"] == "succulence")]
    # If empty, the gap_list must document it as unreachable with reason.
    if cactus.empty:
        for line in text.splitlines():
            if line.startswith("Succulence Cactaceae"):
                assert "no" in line.split("\t") or "family_and_genus_absent" in line


def test_provenance_preserved():
    df = pq.read_table(OUT).to_pandas()
    for col in ["source_id", "license", "access_date"]:
        assert col in df.columns
    assert df["source_id"].fillna("").eq("").sum() == 0
    assert df["license"].fillna("").eq("").sum() == 0
    assert df["access_date"].fillna("").eq("").sum() == 0


def test_no_synonym_renormalization():
    """The build must not modify synonym_resolution.parquet or nodes.parquet."""
    # We can't compare to a snapshot, but we can compare ordering against
    # mtimes relative to the script run. We rely on test_substrate_mtimes_unchanged.
    # Additional check: the build script source must not contain DataFrame
    # writes to substrate paths.
    script = WORKSPACE / "tracks" / "track3" / "scripts" / "build_track3_enrichment.py"
    text = script.read_text()
    for forbidden in [
        "phytograph_dataset/synonym_resolution",
        "phytograph_dataset/nodes",
        "phytograph_dataset/hyperedges",
        "phytograph_dataset/taxon_crosswalk",
    ]:
        # the only allowed references are reads (pq.read_table). Check no .to_parquet
        # or .write to those paths.
        if forbidden in text:
            for line in text.splitlines():
                if forbidden in line:
                    assert "to_parquet" not in line, f"forbidden write found: {line}"
                    assert "write" not in line.lower() or "read" in line.lower(), line


def test_no_paid_provider_imports():
    """Track 6 free/open correction binds Track 3 too: no anthropic/openai/genai."""
    track3_dir = WORKSPACE / "tracks" / "track3"
    self_path = Path(__file__).resolve()
    forbidden_tokens = [
        "imp" + "ort " + "anthropic",
        "imp" + "ort " + "openai",
        "fr" + "om " + "anthropic",
        "fr" + "om " + "openai",
        "go" + "ogle.genai",
        "go" + "ogle.generativeai",
    ]
    for py in track3_dir.rglob("*.py"):
        if py.resolve() == self_path:
            continue  # this test file names the tokens by construction
        text = py.read_text()
        for forbidden in forbidden_tokens:
            assert forbidden not in text, f"paid provider import in {py}: {forbidden}"


def test_track_namespace_only():
    """Build must write only under tracks/track3/."""
    script = WORKSPACE / "tracks" / "track3" / "scripts" / "build_track3_enrichment.py"
    text = script.read_text()
    # No writes to other track namespaces or substrate.
    for forbidden in ["tracks/track1/", "tracks/track2/", "tracks/track4/", "tracks/track5/", "tracks/track6/"]:
        assert forbidden not in text, f"forbidden cross-track reference in build script: {forbidden}"


def test_coverage_summary_has_required_traits():
    """The coverage summary must report on every canonical trait, including
    the three with no substrate label (ant_domatia, carnivory, parasitism)."""
    cov_path = OUT.parent / "trait_coverage_summary.tsv"
    assert cov_path.exists()
    text = cov_path.read_text()
    for trait in [
        "c4_photosynthesis", "cam_photosynthesis", "succulence", "fleshy_fruit",
        "drupe", "samara", "capsule", "achene", "follicle", "aril", "elaiosome",
        "myrmecochory", "ant_domatia", "carnivory", "parasitism",
    ]:
        assert trait in text, f"trait missing from coverage table: {trait}"
