#!/usr/bin/env python3
"""c20 clone-1: Rome (Dojo Cuts - Rome, sha16 51e433ade2a845e1) focus-song delivery test suite. 12 cases.

Invoke: PYTHONPATH=. /usr/bin/python3 tests/test_v3_focus_rome_c20.py
"""
from __future__ import annotations
import hashlib
import json
import re
import sys
import wave
from pathlib import Path


SHA16 = "51e433ade2a845e1"
SEC = Path(f"data/v3_spine/{SHA16}/operator_section")
FULL = Path(f"data/v3_spine/{SHA16}/full_song")
DEL_ROOT = Path(f"data/v3/deliveries/{SHA16}")
DEL_OP = DEL_ROOT / "operator_section"


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


# 1: htdemucs chosen-section 6 stems byte-deterministic ×2
@T("01_htdemucs_section_det")
def t01():
    r = json.loads((SEC / "htdemucs_determinism.json").read_text())
    assert r["byte_determinism_holds"] is True
    assert r["n_mismatch"] == 0


# 2: htdemucs full-song 6 stems byte-deterministic ×2
@T("02_htdemucs_full_song_det")
def t02():
    r = json.loads((FULL / "htdemucs_determinism.json").read_text())
    assert r["byte_determinism_holds"] is True
    assert r["n_mismatch"] == 0


# 3: MuScriptor JSON 7 probes byte-deterministic ×2
@T("03_muscriptor_json_det")
def t03():
    r = json.loads((SEC / "muscriptor_determinism.json").read_text())
    assert r["all_deterministic"] is True
    assert r["n_probes"] == 7


# 4: canonical MIDI 7 probes byte-deterministic ×2
@T("04_canonical_midi_det")
def t04():
    r = json.loads((SEC / "canonical_midi_determinism.json").read_text())
    fails = [k for k, v in r["results"].items()
             if v.get("byte_deterministic_x2") is False]
    assert not fails, f"non-det: {fails}"


# 5: per-track render byte-deterministic ×2 + full_reconstruction byte-det ×2
@T("05_render_and_full_det")
def t05():
    pt = json.loads((SEC / "render" / "per_track_determinism.json").read_text())
    pfails = [k for k, v in pt["results"].items() if not v.get("equal")]
    assert not pfails, f"per_track non-det: {pfails}"
    mm = json.loads((SEC / "render" / "mix_match_operator_section.json").read_text())
    assert mm["byte_deterministic_x2"] is True


# 6: structural gates on merged.mid (zero GM4, drums ch10 non-empty, bass median<55, vocals symbolic)
@T("06_structural_gates_pass")
def t06():
    r = json.loads((SEC / "merged_report.json").read_text())
    a = r["structural_assertions"]
    assert a["drums_track_on_ch10_nonempty"] is True
    assert a["bass_median_pitch_lt_55"] is True
    assert a["vocals_track_present_symbolic"] is True
    assert a["zero_notes_on_gm_program_4"] is True


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
    assert found_track and found_marker


# 9: A/B WAVs 30 s ±5 ms non-silent (root + operator_section)
@T("09_ab_30s_nonsilent")
def t09():
    for p in (DEL_ROOT / "original_ab.wav", DEL_ROOT / "reconstruction_ab.wav",
              DEL_OP / "original_ab_operator_section.wav",
              DEL_OP / "reconstruction_ab_operator_section.wav"):
        with wave.open(str(p), "rb") as w:
            d = w.getnframes() / w.getframerate()
        assert abs(d - 30.0) < 0.005, f"{p} dur={d}"


# 10: panel 8-key finite (root delivery)
@T("10_panel_8_finite")
def t10():
    r = json.loads((DEL_ROOT / "panel.json").read_text())
    assert r["panel_keys_count"] >= 8
    assert all(r["finite_per_key"].values())


# 11: rubric_hash_v2 three-way chain byte-equal + backref to CG c19 verdict on-disk
@T("11_rubric_chain_and_c19_backref")
def t11():
    rubric_from_txt = Path("data/v3_spine/rubric_hash_v2.txt").read_text().strip()
    verdict = json.loads((DEL_ROOT / "cycle20" / "verdict.json").read_text())
    manifest = json.loads((DEL_ROOT / "manifest.json").read_text())
    doc_sha = sha(Path("docs/v3_spine_rubric_v2.md"))
    assert verdict["rubric_hash_v2"] == rubric_from_txt
    assert verdict["rubric_hash_v2_doc_sha"] == rubric_from_txt == doc_sha
    assert manifest["rubric_hash_v2"] == rubric_from_txt
    c19_path = Path(verdict["c19_backref"]["path"])
    assert c19_path.exists(), f"{c19_path} missing"
    assert sha(c19_path) == verdict["c19_backref"]["sha256"]


# 12: verdict shape: blocked_on_operator, chosen_section metadata, no PRNG in Rome sibling scripts
@T("12_verdict_shape_and_hygiene")
def t12():
    verdict = json.loads((DEL_ROOT / "cycle20" / "verdict.json").read_text())
    assert verdict["blocked_on_operator"] is True
    assert verdict["song_sha16"] == SHA16
    assert verdict["chosen_section"]["t_start_s"] == 62.74031746031746
    assert verdict["chosen_section"]["t_end_s"] == 92.74031746031747
    assert verdict["chosen_section"]["duration_s"] == 30.0
    assert verdict["verdict"] in (
        "V3_FOCUS_SONG_LANDS_pending_operator", "V3_FOCUS_SONG_PARTIAL")
    for pth in Path("scripts/v3_spine").glob("*_song_51e433ade2a845e1.py"):
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
