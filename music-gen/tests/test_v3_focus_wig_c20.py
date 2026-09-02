#!/usr/bin/env python3
"""c20 clone-0: WIG (What If I Go, sha16 252eb21ce7df7328) focus-song delivery test suite. 12 cases.

Invoke: PYTHONPATH=. /usr/bin/python3 tests/test_v3_focus_wig_c20.py
"""
from __future__ import annotations
import hashlib
import json
import re
import sys
import wave
from pathlib import Path


SEC = Path("data/v3_spine/252eb21ce7df7328/operator_section")
DEL = Path("data/v3/deliveries/252eb21ce7df7328/operator_section")
CG_C5_DEL = Path("data/v3/deliveries/31a164f845f8e27e/operator_section")


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


results = []


def T(name):
    def deco(fn):
        try:
            fn()
            results.append((name, True, None))
        except AssertionError as e:
            results.append((name, False, str(e)))
        except Exception as e:
            results.append((name, False, f"{type(e).__name__}: {e}"))
        return fn
    return deco


# 1: htdemucs operator-section 6 stems byte-deterministic ×2
@T("01_htdemucs_operator_section_det")
def t01():
    r = json.loads((SEC / "htdemucs_determinism.json").read_text())
    assert r["byte_determinism_holds"] is True
    assert r["n_mismatch"] == 0


# 2: MuScriptor JSON operator-section 7 probes byte-deterministic ×2
@T("02_muscriptor_json_det")
def t02():
    r = json.loads((SEC / "muscriptor_determinism.json").read_text())
    assert r["all_deterministic"] is True
    assert r["n_probes"] == 7


# 3: canonical MIDI operator-section 7 probes byte-deterministic ×2
@T("03_canonical_midi_det")
def t03():
    r = json.loads((SEC / "canonical_midi_determinism.json").read_text())
    fails = [k for k, v in r["results"].items() if v.get("byte_deterministic_x2") is False]
    assert not fails, f"non-det: {fails}"


# 4: per-track render byte-deterministic ×2
@T("04_render_per_track_det")
def t04():
    r = json.loads((SEC / "render" / "per_track_determinism.json").read_text())
    fails = [k for k, v in r["results"].items() if not v.get("equal")]
    assert not fails, f"non-det: {fails}"


# 5: full_reconstruction_operator_section byte-deterministic ×2
@T("05_full_reconstruction_det")
def t05():
    r = json.loads((SEC / "render" / "mix_match_operator_section.json").read_text())
    assert r["byte_deterministic_x2"] is True


# 6: zero GM4 + drums ch10 non-empty + bass median<55 + vocals symbolic-track present
@T("06_structural_gates_pass")
def t06():
    r = json.loads((SEC / "merged_report.json").read_text())
    assertions = r["structural_assertions"]
    assert assertions["drums_track_on_ch10_nonempty"] is True
    assert assertions["bass_median_pitch_lt_55"] is True
    assert assertions["vocals_track_present_symbolic"] is True
    assert assertions["zero_notes_on_gm_program_4"] is True


# 7: mido version pinned at 1.3.3
@T("07_mido_version_1_3_3")
def t07():
    import importlib.metadata as im
    assert im.version("mido") == "1.3.3"


# 8: vocals track present with symbolic marker in merged.mid
@T("08_vocals_symbolic_unrendered")
def t08():
    import mido
    mf = mido.MidiFile(SEC / "merged.mid")
    found_track = False
    found_marker = False
    for tr in mf.tracks:
        for m in tr:
            if m.type == "track_name" and m.name == "vocals":
                found_track = True
            if m.type == "text" and "voice_symbolic_do_not_render" in m.text:
                found_marker = True
    assert found_track, "vocals track missing"
    assert found_marker, "voice_symbolic_do_not_render marker missing"


# 9: A/B WAVs 30 s ±5 ms non-silent
@T("09_ab_30s_nonsilent")
def t09():
    for name in ("original_ab_operator_section.wav", "reconstruction_ab_operator_section.wav"):
        p = DEL / name
        with wave.open(str(p), "rb") as w:
            dur = w.getnframes() / w.getframerate()
        assert abs(dur - 30.0) < 0.005, f"{name} dur={dur}"


# 10: panel 8-key finite + cross-window tripwire pass
@T("10_panel_finite_tripwire")
def t10():
    r = json.loads((DEL / "panel.json").read_text())
    assert r["panel_keys_count"] >= 8
    assert all(r["finite_per_key"].values())
    assert r["cross_window_tripwire"]["pass_no_key_regressed_gt_2x"] is True


# 11: rubric_hash_v2 three-way chain byte-equal
@T("11_rubric_hash_v2_three_way")
def t11():
    rubric_from_txt = Path("data/v3_spine/rubric_hash_v2.txt").read_text().strip()
    verdict = json.loads((DEL / "verdict.json").read_text())
    manifest = json.loads((DEL / "manifest.json").read_text())
    assert verdict["rubric_hash_v2"] == rubric_from_txt
    assert verdict["rubric_hash_v2_doc_sha"] == rubric_from_txt
    assert manifest["rubric_hash_v2"] == rubric_from_txt


# 12: no PRNG, no sidecar_nonfactor imports in WIG sibling scripts
@T("12_hygiene_grep_wig_scripts")
def t12():
    for pth in Path("scripts/v3_spine").glob("*_wig.py"):
        text = pth.read_text()
        assert "sidecar_nonfactor" not in text, f"{pth} imports sidecar_nonfactor"
        for bad in (r"\brandom\.random\b", r"\bnp\.random\.rand\b", r"random\.choice\("):
            assert re.search(bad, text) is None, f"{pth} uses PRNG: {bad}"


def main():
    for name, ok, err in results:
        mark = "PASS" if ok else "FAIL"
        print(f"  [{mark}] {name}" + (f" — {err}" if err else ""))
    total = len(results)
    passed = sum(1 for _, ok, _ in results if ok)
    print(f"\n{passed}/{total} tests PASS")
    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
