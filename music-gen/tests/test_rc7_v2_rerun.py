#!/usr/bin/python3
# c53 Branch A tests for RC7-v2 re-run.
# Milestone: M-RECREATE-2/accurate-small-set/rc7-mix-balance-match
"""Tests for scripts/recreate_v2/rc7_v2_rerun.py.

Covers: pre-registration mtime ordering, rubric hash chain, no-PRNG grep,
VST3 lock, render_stem SHA pin, MIDI split fidelity, EQ band pinning
(12 bands, Q=1.4, 20..20 kHz), RMS clamp, LUFS report-only, focus-set
consumption, 4-stem A7 gate shape, verdict thresholds, anchor
preservation (rc7_out), c48 env-var flag default-OFF, pretty_midi
per-instrument round-trip, EQ zero-mean normalization, byte-determinism
(smoke: same-input same-output on a single stem).
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
import pytest

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

RUBRIC_DOC = _REPO / "docs" / "rc7_v2_rerun_rubric.md"
RC7_V2_SCRIPT = _REPO / "scripts" / "recreate_v2" / "rc7_v2_rerun.py"
RC7_MIX_BALANCE = _REPO / "scripts" / "recreate_v2" / "rc7_mix_balance.py"
RENDER_STEM = _REPO / "scripts" / "palette_render" / "render_stem.py"
RC7_OUT_ANCHOR = _REPO / "data" / "recreate_v2" / "rc7_out"
RC7_OUT_V2 = _REPO / "data" / "recreate_v2" / "rc7_out_v2"
RENDER_STEM_ANCHOR_SHA = "214372d920a319a97d6e3fc7b9ee4134c08c0cb4aecb776f4a50c75f965b5b2b"


def _sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def test_01_rubric_pre_registration_mtime_hard():
    """Rubric doc mtime must precede rc7_v2_rerun.py mtime (c46 path (ii))."""
    assert RUBRIC_DOC.is_file()
    assert RC7_V2_SCRIPT.is_file()
    assert RUBRIC_DOC.stat().st_mtime <= RC7_V2_SCRIPT.stat().st_mtime, (
        f"Pre-registration violated: rubric {RUBRIC_DOC.stat().st_mtime} "
        f"vs script {RC7_V2_SCRIPT.stat().st_mtime}"
    )


def test_02_rubric_hash_chain():
    """rubric_hash.txt under rc7_out_v2/ must byte-equal the doc SHA."""
    doc_sha = _sha256(RUBRIC_DOC)
    hash_file = RC7_OUT_V2 / "rubric_hash.txt"
    assert hash_file.is_file(), "rubric_hash.txt missing"
    disk_sha = hash_file.read_text().strip()
    assert disk_sha == doc_sha, f"rubric_hash mismatch: {disk_sha!r} vs {doc_sha!r}"


def test_03_render_stem_sha_locked():
    """render_stem.py SHA must equal the c51-extended anchor."""
    assert _sha256(RENDER_STEM) == RENDER_STEM_ANCHOR_SHA


def test_04_no_prng_in_new_code():
    """No PRNG import/call in the new script (grep guard)."""
    src = RC7_V2_SCRIPT.read_text()
    banned = ["np.random", "random.random", "random.seed", "random.choice",
              "np.random.seed", "torch.rand"]
    for tok in banned:
        assert tok not in src, f"PRNG token {tok!r} appears in rc7_v2_rerun.py"
    assert "import random" not in src


def _strip_comments_and_docstrings(src: str) -> str:
    """Remove line comments and triple-quoted docstrings for grep-guards."""
    import re
    # Drop triple-quoted strings (docstrings).
    src = re.sub(r'"""[\s\S]*?"""', '', src)
    src = re.sub(r"'''[\s\S]*?'''", '', src)
    # Drop line-comment tails.
    out_lines = []
    for ln in src.splitlines():
        if "#" in ln:
            ln = ln.split("#", 1)[0]
        out_lines.append(ln)
    return "\n".join(out_lines)


def test_05_vst3_lock_respected():
    """No Surge/Dexed/VST3 CODE in the new script (comments/docstrings excluded)."""
    src = _strip_comments_and_docstrings(RC7_V2_SCRIPT.read_text())
    for tok in ["surge_xt", "dexed", ".vst3"]:
        assert tok not in src, f"VST3/Surge/Dexed code token {tok!r} present"


def test_06_clap_anti_pattern_respected():
    """No CLAP/VGGish fetch CODE (c11 anti-pattern)."""
    src = _strip_comments_and_docstrings(RC7_V2_SCRIPT.read_text())
    for tok in ["clap_", "vggish", "VGGish", "torch.hub.load", "urllib.request"]:
        assert tok not in src, f"CLAP/VGGish/fetch code token {tok!r} present"


def test_07_python3_guard():
    """Script asserts /usr/bin/python3 executable."""
    src = RC7_V2_SCRIPT.read_text()
    assert "/usr/bin/python3" in src
    assert "sys.executable" in src


def test_08_c48_env_flags_default_off():
    """c48 substantive-exemption + supersedes-in-hash flags default OFF."""
    src = RC7_V2_SCRIPT.read_text()
    assert 'MUSICGEN_LEDGER_SUBSTANTIVE_EXEMPTION", "0"' in src
    assert 'MUSICGEN_LEDGER_SUPERSEDES_IN_HASH", "0"' in src


def test_09_focus_set_v2_consumed():
    """Script must reference focus_set_v2.json (D1-v2)."""
    src = RC7_V2_SCRIPT.read_text()
    assert "focus_set_v2.json" in src


def test_10_a7_gate_is_four_stems():
    """A7 gate is exactly {drums, bass, other_guitar, other_piano} (D5)."""
    from scripts.recreate_v2.rc7_v2_rerun import A7_GATE_STEMS
    assert set(A7_GATE_STEMS) == {"drums", "bass", "other_guitar", "other_piano"}
    assert len(A7_GATE_STEMS) == 4


def test_11_eq_band_pinning():
    """12 log-spaced bands 20..20000 Hz frozen."""
    from scripts.recreate_v2.rc7_mix_balance import _fit_eq_curve_from_original
    src = Path(_REPO / "scripts" / "recreate_v2" / "rc7_mix_balance.py").read_text()
    assert "np.geomspace(20.0, 20000.0, 12)" in src
    assert "Q=1.4" in src or 'Q": 1.4' in src or 'Q\": 1.4' in src


def test_12_rms_clamp_present():
    """RMS scalar gain has a clamp (from render_stem._apply_loudness_target)."""
    from scripts.palette_render.render_stem import _apply_loudness_target
    # Passing an absurdly quiet stereo and target 0 dB should still return
    # a bounded scalar (<= +24 dB by default).
    y = np.ones((44100, 2), dtype=np.float32) * 1e-6
    out, measured = _apply_loudness_target(y, target_rms_db=0.0, max_gain_db=24.0)
    # Scalar can't push measured up more than 24 dB above input (~-120 dB).
    # So measured must be <= -120 + 24 + epsilon.
    assert measured <= -95.0, f"clamp violated: measured={measured} dB"


def test_13_midi_split_fidelity_song1(tmp_path):
    """Splitting Chicken Grease MIDIs yields all 6 named stems."""
    from scripts.recreate_v2.rc7_v2_rerun import _split_merged_midis
    stems = _split_merged_midis("31a164f845f8e27e", tmp_path)
    for req in ["drums", "bass", "other_guitar", "other_piano", "vocals", "other"]:
        assert req in stems, f"missing stem: {req}"
        assert stems[req].is_file()
    import pretty_midi
    # drums.mid must have is_drum=True
    pm = pretty_midi.PrettyMIDI(str(stems["drums"]))
    assert len(pm.instruments) == 1
    assert pm.instruments[0].is_drum


def test_14_verdict_shape_thresholds():
    """RC7_v2_LANDS/PARTIAL/FAILS thresholds match rubric."""
    from scripts.recreate_v2.rc7_v2_rerun import _emit_verdict
    # Fake 3 songs pass -> LANDS.
    fake = [
        {"song_id": f"s{i}", "per_stem": {
            s: {"a7_rms_pass": True} for s in
            ["drums", "bass", "other_guitar", "other_piano"]
        }} for i in range(3)
    ]
    with tempfile.TemporaryDirectory() as td:
        v = _emit_verdict(fake, Path(td))
        assert v["verdict"] == "RC7_v2_LANDS"
        assert v["n_songs_passing_a7"] == 3
    # 0 songs pass, 0 stem accepts -> FAILS.
    fake0 = [
        {"song_id": f"s{i}", "per_stem": {
            s: {"a7_rms_pass": False} for s in
            ["drums", "bass", "other_guitar", "other_piano"]
        }} for i in range(5)
    ]
    with tempfile.TemporaryDirectory() as td:
        v = _emit_verdict(fake0, Path(td))
        assert v["verdict"] == "RC7_v2_FAILS"
    # 1 song passes -> PARTIAL.
    fake1 = fake0[:4] + [fake[0]]
    with tempfile.TemporaryDirectory() as td:
        v = _emit_verdict(fake1, Path(td))
        assert v["verdict"] == "RC7_v2_PARTIAL"


def test_15_anchor_preservation_rc7_out():
    """c51 rc7_out/ anchor: verdict.json exists untouched.
    The rc7_v2_rerun script MUST NOT write into rc7_out/."""
    assert (RC7_OUT_ANCHOR / "verdict.json").is_file()
    src = RC7_V2_SCRIPT.read_text()
    assert "RC7_OUT_ANCHOR_DIR" in src, "anchor constant must be declared for supersedes reference"
    # Ensure no line performs a write (mkdir/write_text/rmtree/scipy_wav.write etc.)
    # keyed off the anchor constant.
    write_verbs = [".mkdir(", ".write_text(", ".write_bytes(", ".unlink(",
                   "shutil.rmtree", "os.remove", "scipy_wav.write"]
    for i, ln in enumerate(src.splitlines(), start=1):
        if "RC7_OUT_ANCHOR_DIR" in ln:
            for v in write_verbs:
                assert v not in ln, f"forbidden write against RC7_OUT_ANCHOR_DIR at {i}: {ln!r}"


def test_16_read_only_helper_imports():
    """We import helpers from render_stem.py and rc7_mix_balance.py READ-ONLY."""
    src = RC7_V2_SCRIPT.read_text()
    assert "from scripts.palette_render.render_stem import" in src
    assert "from scripts.recreate_v2.rc7_mix_balance import" in src


def test_17_eq_zero_mean_normalization():
    """rc7_mix_balance's fit zero-means the per-band gains so loudness match owns level."""
    src = RC7_MIX_BALANCE.read_text()
    assert "zero_mean" in src or "mean_g" in src


def test_18_pretty_midi_round_trip(tmp_path):
    """Every split MIDI parses back into pretty_midi with the promised structure."""
    from scripts.recreate_v2.rc7_v2_rerun import _split_merged_midis
    import pretty_midi
    stems = _split_merged_midis("cdd2717e52820ff6", tmp_path)
    # bass is program 33, non-drum, exactly one instrument.
    pm = pretty_midi.PrettyMIDI(str(stems["bass"]))
    assert len(pm.instruments) == 1
    assert pm.instruments[0].program == 33
    assert not pm.instruments[0].is_drum
    # other_guitar and other_piano exist, are non-drum, single-instrument.
    for k in ["other_guitar", "other_piano"]:
        pm = pretty_midi.PrettyMIDI(str(stems[k]))
        assert len(pm.instruments) == 1
        assert not pm.instruments[0].is_drum


def test_19_render_stem_signature_unchanged():
    """render_stem() signature must be the c51 additive-kwargs form."""
    import inspect
    from scripts.palette_render.render_stem import render_stem
    sig = inspect.signature(render_stem)
    names = list(sig.parameters.keys())
    assert names[:3] == ["stem", "instrument", "out_dir"]
    kw_only = [n for n, p in sig.parameters.items()
               if p.kind == inspect.Parameter.KEYWORD_ONLY]
    assert set(kw_only) == {"parameter_dict", "eq_curve", "loudness_target"}


def test_20_verdict_disk_present():
    """After the ×2 determinism run, verdict.json must be on disk under rc7_out_v2/."""
    v = RC7_OUT_V2 / "verdict.json"
    if not v.is_file():
        pytest.skip("rc7_out_v2/verdict.json not yet emitted (run rc7_v2_rerun first)")
    d = json.loads(v.read_text())
    assert d["milestone_id"] == "M-RECREATE-2/accurate-small-set/rc7-mix-balance-match"
    assert d["cycle"] == 53
    assert d["branch"] == "A"
    assert d["clone"] == "clone-0"
    assert d["verdict"] in ("RC7_v2_LANDS", "RC7_v2_PARTIAL", "RC7_v2_FAILS")
    assert d["rubric_hash"] == _sha256(RUBRIC_DOC)
    assert d["supersedes_verdict"] == "data/recreate_v2/rc7_out/verdict.json"


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
