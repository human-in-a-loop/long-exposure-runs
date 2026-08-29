#!/usr/bin/python3
# c50 M-RECREATE-2 v2 pre-registration tests.
# Created: 2026-08-29
# Cycle: 50
# Run id: run-2026-08-28T040704Z
# Agent: worker
# Milestone: _infra/adopt-cycle50-tests
import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

V2_STUBS = [
    "rc7_mix_balance.py", "rc8_section_selection.py", "rc9_first_class_parts.py",
    "rc1_v2_hybrid.py", "rc4_v2_gm_program_map.py", "rc6_v2_panel_gate.py",
]
V1_STUBS = [
    "rc1_vocals_transcription.py", "rc2_drum_onset_transcription.py",
    "rc3_bass_transcription.py", "rc4_gm_program_map.py",
    "rc5_tempo_beat_grid.py", "rc6_panel_gate.py",
]


def test_01_v2_rubric_doc_mtime_precedes_every_new_stub():
    rubric = ROOT / "docs/m_recreate_2_accurate_small_set_rubric_v2.md"
    r_mtime = rubric.stat().st_mtime
    for s in V2_STUBS:
        p = ROOT / "scripts/recreate_v2" / s
        assert p.exists(), f"missing stub {s}"
        assert p.stat().st_mtime > r_mtime, f"{s} mtime not > rubric_v2 mtime"


def test_02_three_way_v2_rubric_hash_chain():
    doc_sha = hashlib.sha256(
        (ROOT / "docs/m_recreate_2_accurate_small_set_rubric_v2.md").read_bytes()
    ).hexdigest()
    hash_file = (ROOT / "data/recreate_v2/rubric_hash_v2.txt").read_text().strip()
    assert hash_file == doc_sha, "v2 rubric_hash.txt drift"
    # verdict-side check: any c51+ verdict.rubric_hash must equal doc_sha
    # (no verdict landed in c50; asserted at c51+ landing)


def test_03_focus_set_v2_contains_chosen_section_per_song():
    d = json.loads((ROOT / "data/recreate_v2/focus_set_v2.json").read_text())
    assert len(d["songs"]) == 5
    for song in d["songs"]:
        cs = song["chosen_section"]
        if cs is None:
            assert "null_reason" in song
        else:
            for k in ("t_start_s", "t_end_s", "combined_score", "rms_score",
                      "onset_density_score", "weights"):
                assert k in cs, f"missing {k}"
            assert cs["weights"] == {"w_rms": 0.5, "w_onset": 0.5}
            assert cs["t_end_s"] > cs["t_start_s"]


def test_04_focus_set_v2_byte_determinism():
    d = json.loads((ROOT / "data/recreate_v2/focus_set_v2_byte_determinism.json").read_text())
    assert d["ok"] is True, "focus_set_v2 byte-determinism x2 FAILED"


def test_05_rc0_v2_baseline_sibling_files_present():
    fs = json.loads((ROOT / "data/recreate_v2/focus_set_v2.json").read_text())
    for song in fs["songs"]:
        sha16 = song["audio_sha16"]
        base = ROOT / "data/recreate_v2/baseline" / sha16
        assert (base / "rc7_per_stem_loudness.json").exists(), f"missing rc7 for {sha16}"
        assert (base / "rc8_chosen_section_verified.json").exists(), f"missing rc8 for {sha16}"


def test_06_htdemucs_6s_outcome_recorded_honestly():
    p = ROOT / "data/recreate_v2/fetchability_htdemucs_6s.jsonl"
    rows = [json.loads(l) for l in p.read_text().splitlines() if l.strip()]
    assert len(rows) >= 1
    # Either OK (with baseline_path) or BLOCKED (with fallback/notes) — never silent
    for row in rows:
        assert row["status"] in ("OK", "BLOCKED"), f"unknown status {row['status']}"


def test_07_v2_stubs_raise_not_implemented():
    sys.path.insert(0, str(ROOT))
    try:
        for name in ("rc7_mix_balance", "rc8_section_selection", "rc9_first_class_parts",
                     "rc1_v2_hybrid", "rc4_v2_gm_program_map", "rc6_v2_panel_gate"):
            spec = importlib.util.spec_from_file_location(
                name, ROOT / f"scripts/recreate_v2/{name}.py"
            )
            m = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(m)
            try:
                m.run()
                raise AssertionError(f"{name}.run() did not raise")
            except NotImplementedError:
                pass
    finally:
        sys.path.remove(str(ROOT))


def test_08_v1_anchors_byte_identical():
    ap = json.loads((ROOT / "data/recreate_v2/anchor_preservation_v2.json").read_text())
    assert ap["n_entries"] >= 45, f"got {ap['n_entries']}"
    for rel, sha in ap["anchors"].items():
        p = ROOT / rel
        actual = hashlib.sha256(p.read_bytes()).hexdigest()
        assert actual == sha, f"anchor drift on {rel}: {actual} != {sha}"


def test_09_c49_v1_stubs_unmodified():
    # SHAs from c50 pre-emit snapshot (see anchor_preservation_v2.json)
    ap = json.loads((ROOT / "data/recreate_v2/anchor_preservation_v2.json").read_text())
    for s in V1_STUBS:
        rel = f"scripts/recreate_v2/{s}"
        assert rel in ap["anchors"], f"v1 stub {s} not tracked in anchor_preservation_v2"


def test_10_d1_formula_pinned_in_v2_rubric():
    txt = (ROOT / "docs/m_recreate_2_accurate_small_set_rubric_v2.md").read_text()
    for token in ("w_rms   = 0.5", "w_onset = 0.5", "hop=512", "combined_score(t)"):
        assert token in txt, f"D1 pinning missing: {token}"


def test_11_d2_d3_d4_pinned_in_v2_rubric():
    txt = (ROOT / "docs/m_recreate_2_accurate_small_set_rubric_v2.md").read_text()
    assert "D2 — Vocals: hybrid render" in txt
    assert "D3 — Separator: htdemucs_6s" in txt
    assert "D4 — Mix stage" in txt
    assert "A7" in txt and "A8" in txt


def test_12_rc9_6stem_or_blocked_declaration():
    fs = json.loads((ROOT / "data/recreate_v2/focus_set_v2.json").read_text())
    for song in fs["songs"]:
        sha16 = song["audio_sha16"]
        base = ROOT / "data/recreate_v2/baseline" / sha16
        d = base / "rc9_6stem"
        blocked = base / "rc9_htdemucs_6s_blocked.json"
        has_stems = d.exists() and len(list(d.glob("*.wav"))) == 6
        has_blocker = blocked.exists()
        assert has_stems or has_blocker, (
            f"{sha16}: neither 6-stem baseline nor blocker declaration present"
        )


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    fails = 0
    for t in tests:
        try:
            t()
            print(f"PASS {t.__name__}")
        except AssertionError as e:
            print(f"FAIL {t.__name__}: {e}")
            fails += 1
    print(f"\n{len(tests) - fails}/{len(tests)} passed")
    sys.exit(1 if fails else 0)
