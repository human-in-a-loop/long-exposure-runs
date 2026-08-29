#!/usr/bin/python3
"""c51 Branch A tests for RC1 vocals + RC9 first-class parts.

Plain-assert suite (no pytest). Invocation:
    PYTHONPATH=. /usr/bin/python3 tests/test_rc1_rc9_impl.py
"""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

FOCUS_SONGS = [
    "31a164f845f8e27e",  # Chicken Grease (band 6)
    "cdd2717e52820ff6",  # Disco A (band 5)
    "51e433ade2a845e1",  # Dojo Cuts Rome (band 5)
    "252eb21ce7df7328",  # Mura Masa (band 5)
    "88d247468cb6d49f",  # Peach Dream (band 6)
]

def test_01_verdict_present_and_frozen_enum():
    v = json.loads((ROOT / "data/rc1_rc9_impl/verdict.json").read_text())
    assert v["verdict"] in {"RC1_RC9_LANDS", "RC1_RC9_PARTIAL", "RC1_RC9_FAILS"}, v["verdict"]

def test_02_rubric_hash_three_way_byte_equality():
    v = json.loads((ROOT / "data/rc1_rc9_impl/verdict.json").read_text())
    rubric_file = (ROOT / "data/recreate_v2/rubric_hash_v2.txt").read_text().strip()
    doc_sha = sha256_file(ROOT / "docs/m_recreate_2_accurate_small_set_rubric_v2.md")
    assert v["rubric_hash"] == rubric_file, (v["rubric_hash"], rubric_file)
    assert doc_sha == rubric_file, (doc_sha, rubric_file)

def test_03_rc1_five_songs_processed():
    for s in FOCUS_SONGS:
        p = ROOT / f"data/rc1_rc9_impl/per_song/{s}/rc1_result.json"
        assert p.exists(), s
        r = json.loads(p.read_text())
        assert "vocal_note_count" in r
        assert "coverage_ratio" in r
        assert "rc1_accept" in r
        assert isinstance(r["rc1_accept"], bool)

def test_04_rc9_five_songs_processed():
    for s in FOCUS_SONGS:
        p = ROOT / f"data/rc1_rc9_impl/per_song/{s}/rc9_result.json"
        assert p.exists(), s
        r = json.loads(p.read_text())
        assert r["gm_patch_guitar"] in list(range(25, 31)), r["gm_patch_guitar"]
        assert r["gm_patch_piano"] in list(range(0, 5)), r["gm_patch_piano"]
        assert isinstance(r["rc9_accept"], bool)

def test_05_merged_partial_midi_present_and_nonempty():
    import pretty_midi
    for s in FOCUS_SONGS:
        p = ROOT / f"data/rc1_rc9_impl/per_song/{s}/merged_partial.midi"
        assert p.exists(), s
        pm = pretty_midi.PrettyMIDI(str(p))
        total_notes = sum(len(i.notes) for i in pm.instruments)
        assert total_notes > 0, f"{s} merged_partial.midi has no notes"
        assert len(pm.instruments) >= 3, f"{s} needs >= 3 instruments (vocals+guitar+piano+other)"

def test_06_byte_determinism_run1_equals_run2():
    bd = json.loads((ROOT / "data/rc1_rc9_impl/byte_determinism.json").read_text())
    assert bd["verdict_sha_equal"] is True
    assert bd["total_matches"] == bd["total_shas_compared"]
    assert bd["total_matches"] == 15  # 5 songs x 3 artifacts

def test_07_anchor_preservation_covers_readonly_set():
    ap = json.loads((ROOT / "data/rc1_rc9_impl/anchor_preservation.json").read_text())
    assert ap["anchor_count"] >= 34, ap["anchor_count"]
    # Verify rubric chains + do-not-touch render_stem byte-identical.
    for k in [
        "docs/m_recreate_2_accurate_small_set_rubric.md",
        "data/recreate_v2/rubric_hash.txt",
        "docs/m_recreate_2_accurate_small_set_rubric_v2.md",
        "data/recreate_v2/rubric_hash_v2.txt",
        "scripts/palette_render/render_stem.py",  # c33 palette-render — do-not-touch
    ]:
        assert k in ap["anchors"], k
        assert ap["anchors"][k] == sha256_file(ROOT / k), f"{k} SHA drift"

def test_08_c49_v1_rubric_chain_preserved():
    v1 = (ROOT / "data/recreate_v2/rubric_hash.txt").read_text().strip()
    assert v1 == "958ade3886eba560df284878ff5d351e3f6186159ed598f68b82fc7c3fe58b9d"

def test_09_no_prng_in_rc_scripts():
    # PRNG _use_ (sampling) is forbidden; _seeding_ calls (set_seed, manual_seed) are permitted.
    import re
    forbidden = re.compile(
        r"\b(random\.random|random\.choice|random\.randint|random\.sample|random\.shuffle|"
        r"numpy\.random|np\.random|"
        r"torch\.rand\b|torch\.randn\b|torch\.randint\b)"
    )
    for rel in [
        "scripts/recreate_v2/rc1_v2_hybrid.py",
        "scripts/recreate_v2/rc9_first_class_parts.py",
        "tools/stale/c51_run_rc1_rc9.py",
    ]:
        src = (ROOT / rel).read_text()
        matches = [m.group() for m in forbidden.finditer(src)]
        assert not matches, f"PRNG usage in {rel}: {matches}"

def test_10_interpreter_guard_present():
    for rel in [
        "scripts/recreate_v2/rc1_v2_hybrid.py",
        "scripts/recreate_v2/rc9_first_class_parts.py",
        "tools/stale/c51_run_rc1_rc9.py",
    ]:
        src = (ROOT / rel).read_text()
        assert "/usr/bin/python3" in src, rel

def test_11_render_stem_untouched_by_c51():
    # The c33 palette-render render_stem.py must be preserved byte-exact (do-not-touch invariant).
    ap = json.loads((ROOT / "data/rc1_rc9_impl/anchor_preservation.json").read_text())
    k = "scripts/palette_render/render_stem.py"
    expected = ap["anchors"].get(k)
    assert expected is not None, f"{k} missing from anchors"
    actual = sha256_file(ROOT / k)
    assert expected == actual, f"{k} was modified: expected {expected[:16]}, got {actual[:16]}"

def test_12_no_vggish_reintroduced():
    import re
    for rel in [
        "scripts/recreate_v2/rc1_v2_hybrid.py",
        "scripts/recreate_v2/rc9_first_class_parts.py",
        "tools/stale/c51_run_rc1_rc9.py",
    ]:
        src = (ROOT / rel).read_text()
        assert not re.search(r"\bvggish\b", src, re.IGNORECASE), f"VGGish reintroduced in {rel}"

def test_13_verdict_rollup_matches_per_song():
    v = json.loads((ROOT / "data/rc1_rc9_impl/verdict.json").read_text())
    rc1_pass = sum(1 for s in v["per_song"] if s["rc1_accept"])
    rc9_pass = sum(1 for s in v["per_song"] if s["rc9_accept"])
    both = sum(1 for s in v["per_song"] if s["rc1_accept"] and s["rc9_accept"])
    assert v["rc1_pass_count"] == rc1_pass
    assert v["rc9_pass_count"] == rc9_pass
    assert v["both_pass_count"] == both
    # Verdict rule
    if both >= 3:
        assert v["verdict"] == "RC1_RC9_LANDS"

def test_14_fetchability_ladder_has_three_probes():
    p = ROOT / "data/rc1_rc9_impl/fetchability_ladder.jsonl"
    rows = [json.loads(l) for l in p.read_text().splitlines() if l.strip()]
    assert len(rows) == 3, len(rows)
    outcomes = {r["outcome"] for r in rows}
    assert outcomes == {"OK"}

def test_15_gm_patch_deterministic_tiebreak():
    # SHA-256 tiebreak: the pick for a fixed (song, stem) must be stable
    import hashlib
    def tb(pool, salt):
        scored = [(hashlib.sha256(f"{salt}|{i}".encode()).hexdigest(), pool[i]) for i in range(len(pool))]
        scored.sort()
        return scored[0][1]
    for s in FOCUS_SONGS:
        r = json.loads((ROOT / f"data/rc1_rc9_impl/per_song/{s}/rc9_result.json").read_text())
        assert r["gm_patch_guitar"] == tb(list(range(25, 31)), f"{s}|guitar")
        assert r["gm_patch_piano"] == tb(list(range(0, 5)), f"{s}|piano")

if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    passed = 0
    failed = []
    for name, fn in tests:
        try:
            fn()
            print(f"PASS  {name}")
            passed += 1
        except AssertionError as e:
            print(f"FAIL  {name}: {e}")
            failed.append(name)
        except Exception as e:
            print(f"ERROR {name}: {type(e).__name__}: {e}")
            failed.append(name)
    print(f"\n{passed}/{len(tests)} pass")
    sys.exit(0 if not failed else 1)
