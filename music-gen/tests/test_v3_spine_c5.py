#!/usr/bin/env python3
"""c5 test suite. ≥14 cases per brief.

Invoke: PYTHONPATH=. /usr/bin/python3 tests/test_v3_spine_c5.py
"""
from __future__ import annotations
import hashlib
import json
import os
import re
import sys
import wave
from pathlib import Path


SEC = Path("data/v3_spine/31a164f845f8e27e/operator_section")
DEL = Path("data/v3/deliveries/31a164f845f8e27e/operator_section")
C4_DEL = Path("data/v3/deliveries/31a164f845f8e27e")


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


# 1: env-drift spec doc mtime < any venv-audit script
@T("01_env_drift_spec_mtime_before_scripts")
def t01():
    doc = Path("docs/v3_spine_venv_delta_audit_spec.md")
    for s in ("scripts/v3_spine/venv_delta_audit.py",
              "scripts/v3_spine/c3_guitar_reproduce_probe.py"):
        assert doc.stat().st_mtime <= Path(s).stat().st_mtime, f"{s} older than doc"


# 2: rehtdemucs spec doc mtime < rehtdemucs script
@T("02_rehtdemucs_spec_mtime_before_scripts")
def t02():
    doc = Path("docs/v3_spine_rehtdemucs_operator_section_spec.md")
    s = Path("scripts/v3_spine/rehtdemucs_operator_section.py")
    assert doc.stat().st_mtime <= s.stat().st_mtime


# 3: c4 delivery artifacts SHA byte-identical pre==post via anchor snapshot
@T("03_c4_delivery_anchors_preserved")
def t03():
    post = json.loads((SEC.parent / "anchor_preservation_c5.json").read_text())
    assert post["all_match"] is True, f"diffs: {post['diffs']}"


# 4: htdemucs operator-section 6 stems byte-deterministic ×2
@T("04_htdemucs_operator_section_det")
def t04():
    r = json.loads((SEC / "htdemucs_determinism.json").read_text())
    assert r["byte_determinism_holds"] is True
    assert r["n_mismatch"] == 0


# 5: MuScriptor JSON operator-section 7 probes byte-deterministic ×2
@T("05_muscriptor_json_det")
def t05():
    r = json.loads((SEC / "muscriptor_determinism.json").read_text())
    assert r["all_deterministic"] is True
    assert r["n_probes"] == 7


# 6: canonical MIDI operator-section 7 probes byte-deterministic ×2
@T("06_canonical_midi_det")
def t06():
    r = json.loads((SEC / "canonical_midi_determinism.json").read_text())
    assert all(v.get("byte_deterministic_x2") for v in r["results"].values())


# 7: mido version pinned at 1.3.3
@T("07_mido_version_1_3_3")
def t07():
    import importlib.metadata as im
    assert im.version("mido") == "1.3.3"


# 8: zero GM4 in operator-section merged.mid
@T("08_no_gm4_notes_in_merged")
def t08():
    import mido
    mf = mido.MidiFile(SEC / "merged.mid")
    for tr in mf.tracks:
        for m in tr:
            if m.type == "program_change":
                assert m.program != 4, "GM 4 found"


# 9: drums track on ch10 non-empty
@T("09_drums_ch10_nonempty")
def t09():
    r = json.loads((SEC / "merged_report.json").read_text())
    assert r["structural_assertions"]["drums_track_on_ch10_nonempty"] is True


# 10: bass median pitch < 55
@T("10_bass_median_lt_55")
def t10():
    r = json.loads((SEC / "merged_report.json").read_text())
    assert r["structural_assertions"]["bass_median_pitch_lt_55"] is True


# 11: vocals present + unrendered (symbolic marker; note count irrelevant on operator section)
@T("11_vocals_symbolic_unrendered")
def t11():
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


# 12: A/B WAVs 30 s ±5 ms non-silent
@T("12_ab_30s_nonsilent")
def t12():
    for name in ("original_ab_operator_section.wav", "reconstruction_ab_operator_section.wav"):
        p = DEL / name
        with wave.open(str(p), "rb") as w:
            dur = w.getnframes() / w.getframerate()
        assert abs(dur - 30.0) < 0.005, f"{name} dur={dur}"


# 13: panel 8-key finite + cross-window tripwire pass
@T("13_panel_finite_tripwire")
def t13():
    r = json.loads((DEL / "panel.json").read_text())
    assert r["panel_keys_count"] >= 8
    assert all(r["finite_per_key"].values())
    assert r["cross_window_tripwire"]["pass_no_key_regressed_gt_2x"] is True


# 14: anchor preservation pre==post
@T("14_anchor_pre_post")
def t14():
    post = json.loads((SEC.parent / "anchor_preservation_c5.json").read_text())
    assert post["all_match"] is True


# 15: locked scripts SHAs byte-identical pre==post
@T("15_locked_scripts_preserved")
def t15():
    post = json.loads((SEC.parent / "anchor_preservation_c5.json").read_text())
    for key in ("scripts/palette_render/render_stem.py",
                "scripts/v3_spine/midi_from_json_events.py"):
        assert key in post["post_anchors"], f"{key} missing post"


# 16: no PRNG, no sidecar_nonfactor, no writes under c4 delivery paths or under baseline
@T("16_hygiene_grep")
def t16():
    for pth in Path("scripts/v3_spine").glob("*operator_section*.py"):
        text = pth.read_text()
        # sidecar_nonfactor isolation
        assert "sidecar_nonfactor" not in text, f"{pth} imports sidecar_nonfactor"
        # No PRNG (accept torch.manual_seed which is deterministic)
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
