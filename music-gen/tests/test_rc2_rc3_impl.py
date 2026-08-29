"""c51 clone-1 RC2 + RC3 implementation test suite."""
from __future__ import annotations

import ast
import hashlib
import json
import os
import sys
from pathlib import Path

WS = Path(__file__).resolve().parent.parent

CHICKEN_GREASE_SHA16 = "31a164f845f8e27e"


def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def _grep_no_import(path_pattern: str, forbidden: list[str]) -> list[str]:
    hits = []
    for py in sorted(Path(WS).glob(path_pattern)):
        src = py.read_text()
        for f in forbidden:
            if f in src:
                hits.append(f"{py}: {f}")
    return hits


def test_01_classifier_bands_mtime_before_scripts():
    bands = WS / "data/recreate_v2/rc2_classifier_bands.json"
    for sc in ("rc2_drum_onset_transcription.py", "rc3_bass_transcription.py"):
        s = WS / f"scripts/recreate_v2/{sc}"
        assert bands.stat().st_mtime <= s.stat().st_mtime, f"{sc} mtime must be >= bands mtime"


def test_02_three_way_rubric_hash_byte_equality():
    doc_sha = sha(WS / "docs/rc2_rc3_impl_rubric.md")
    hash_txt = (WS / "data/rc2_rc3_impl/rubric_hash.txt").read_text().strip()
    v = json.loads((WS / "data/rc2_rc3_impl/verdict.json").read_text())
    assert doc_sha == hash_txt == v["rubric_hash"], (doc_sha, hash_txt, v["rubric_hash"])


def test_03_parent_rubric_v2_preserved_in_verdict():
    v = json.loads((WS / "data/rc2_rc3_impl/verdict.json").read_text())
    assert v["parent_rubric_hash_v2"] == "0e11f704e12c62f85cfb9d58d6e6890227209ffb43247239e735a22acfdebe1f"


def test_04_c49_v1_rubric_sha_unchanged():
    doc = sha(WS / "docs/m_recreate_2_accurate_small_set_rubric.md")
    pin = (WS / "data/recreate_v2/rubric_hash.txt").read_text().strip()
    assert doc == pin == "958ade3886eba560df284878ff5d351e3f6186159ed598f68b82fc7c3fe58b9d"


def test_05_no_prng_in_rc_scripts():
    hits = _grep_no_import(
        "scripts/recreate_v2/rc[23]_*.py",
        ["numpy.random", "np.random", "random.random", "random.seed"],
    )
    assert hits == [], hits


def test_06_no_sidecar_nonfactor_import():
    hits = _grep_no_import("scripts/recreate_v2/rc[23]_*.py", ["sidecar_nonfactor"])
    assert hits == [], hits


def test_07_no_render_effects_layered_import():
    hits = _grep_no_import("scripts/recreate_v2/rc[23]_*.py", ["scripts.tex.render_effects_layered"])
    assert hits == [], hits


def test_08_no_palette_render_import():
    hits = _grep_no_import("scripts/recreate_v2/rc[23]_*.py", ["scripts.palette_render.render_stem", "palette_render.render_stem"])
    assert hits == [], hits


def test_09_interpreter_guard_present():
    for sc in ("rc2_drum_onset_transcription.py", "rc3_bass_transcription.py"):
        src = (WS / f"scripts/recreate_v2/{sc}").read_text()
        assert 'sys.executable == "/usr/bin/python3"' in src


def test_10_byte_determinism_x2():
    bd = json.loads((WS / "data/rc2_rc3_impl/byte_determinism.json").read_text())
    assert bd["byte_determinism_pass"] is True, bd


def test_11_rc2_f1_finite_per_song():
    v = json.loads((WS / "data/rc2_rc3_impl/verdict.json").read_text())
    for r in v["per_song"]:
        f1 = r["rc2"]["onset_f1"]
        assert 0.0 <= float(f1) <= 1.0, r


def test_12_rc3_count_finite():
    v = json.loads((WS / "data/rc2_rc3_impl/verdict.json").read_text())
    for r in v["per_song"]:
        assert int(r["rc3"]["bass_note_count"]) >= 0


def test_13_rc3_correlation_range():
    v = json.loads((WS / "data/rc2_rc3_impl/verdict.json").read_text())
    for r in v["per_song"]:
        c = float(r["rc3"]["low_band_correlation"])
        assert -1.0 <= c <= 1.0


def test_14_median_midi_lt_55():
    v = json.loads((WS / "data/rc2_rc3_impl/verdict.json").read_text())
    for r in v["per_song"]:
        m = r["rc3"]["median_midi_pitch"]
        if m is not None:
            assert int(m) < 55, r


def test_15_rc5_bpm_finite():
    rc5 = json.loads((WS / "data/recreate_v2/rc5_tempo_bpm_observed.json").read_text())
    for k, v in rc5["per_song"].items():
        bpm = v["estimated_bpm"]
        assert bpm is not None and float(bpm) > 0


def test_16_chicken_grease_count_gt_27():
    v = json.loads((WS / "data/rc2_rc3_impl/verdict.json").read_text())
    cg = [r for r in v["per_song"] if r["song_id"] == CHICKEN_GREASE_SHA16][0]
    assert cg["rc2"]["drum_note_count"] > 27, cg


def test_17_focus_set_chicken_grease_section_preserved():
    fs = json.loads((WS / "data/recreate_v2/focus_set_v2.json").read_text())
    cg = [s for s in fs["songs"] if s["song_id"] == CHICKEN_GREASE_SHA16][0]
    assert cg["chosen_section"]["t_start_s"] == 233.63918367346938
    assert cg["chosen_section"]["t_end_s"] == 263.63918367346935


def test_18_verdict_in_frozen_enum():
    v = json.loads((WS / "data/rc2_rc3_impl/verdict.json").read_text())
    assert v["verdict"] in {"RC2_RC3_LANDS", "RC2_RC3_PARTIAL", "RC2_RC3_FAILS"}


def test_19_anchor_preservation_count_ge_30():
    a = json.loads((WS / "data/rc2_rc3_impl/anchor_preservation.json").read_text())
    assert a["anchor_count"] >= 30, a["anchor_count"]


def test_20_palette_render_untouched():
    # sanity: rc2/rc3 scripts never mention palette_render/render_stem
    for sc in ("rc2_drum_onset_transcription.py", "rc3_bass_transcription.py"):
        src = (WS / f"scripts/recreate_v2/{sc}").read_text()
        assert "palette_render" not in src


if __name__ == "__main__":
    fns = [g for g in globals() if g.startswith("test_")]
    n_pass = 0
    n_fail = 0
    for name in sorted(fns):
        try:
            globals()[name]()
            n_pass += 1
            print(f"PASS {name}")
        except Exception as e:
            n_fail += 1
            print(f"FAIL {name}: {e}")
    print(f"\nSummary: {n_pass}/{n_pass + n_fail} PASS")
    sys.exit(0 if n_fail == 0 else 1)
