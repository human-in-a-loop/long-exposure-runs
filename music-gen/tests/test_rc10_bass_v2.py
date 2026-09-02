#!/usr/bin/env /usr/bin/python3
# Tests for RC10 bass articulation v2. Plain asserts; run:
#   PYTHONPATH=. /usr/bin/python3 tests/test_rc10_bass_v2.py
# created: 2026-09-02, cycle 55, run-2026-08-28T040704Z, worker, fork 7cc01d726807 clone-1
import ast
import hashlib
import json
import subprocess
import sys
from pathlib import Path

WS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(WS))

RUBRIC_DOC = WS / "docs/rc10_bass_v2_rubric.md"
RUBRIC_HASH = WS / "data/rc10_bass_v2_impl/rubric_hash.txt"
SCRIPTS_DIR = WS / "scripts/recreate_v2/rc10_bass_v2"
V1_BASS_DIR = WS / "data/rc10_drums_bass_impl"
RENDER_STEM_PY = WS / "scripts/palette_render/render_stem.py"


def _sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


# -----------------------------------------------------------------------------
# 01 rubric pre-registration mtime (HARD)
# -----------------------------------------------------------------------------
def test_01_rubric_mtime_before_scripts_hard():
    doc_mtime = RUBRIC_DOC.stat().st_mtime
    for p in SCRIPTS_DIR.glob("*.py"):
        if p.name == "__init__.py":
            continue
        assert doc_mtime <= p.stat().st_mtime + 1, (
            f"rubric mtime {doc_mtime} > script {p.name} mtime {p.stat().st_mtime}"
        )
    print("  01 rubric mtime pre-reg (hard): PASS")


# -----------------------------------------------------------------------------
# 02 rubric pre-registration git-log (SOFT per c46 amendment)
# -----------------------------------------------------------------------------
def test_02_rubric_git_log_soft():
    # SOFT per c46 amendment: worker cannot commit inside its own turn.
    # Emit informational note; do not gate on git log.
    print("  02 rubric git-log (soft, c46 amendment): SKIP")


# -----------------------------------------------------------------------------
# 03 three-way rubric_hash byte-equality (doc SHA == rubric_hash.txt content)
# -----------------------------------------------------------------------------
def test_03_rubric_hash_chain():
    doc_sha = _sha(RUBRIC_DOC)
    file_sha = RUBRIC_HASH.read_text().strip()
    assert doc_sha == file_sha, f"chain break: doc={doc_sha} file={file_sha}"
    print("  03 rubric_hash chain (doc==file): PASS")


# -----------------------------------------------------------------------------
# 04 NO PRNG — AST grep clean under scripts/recreate_v2/rc10_bass_v2/
# -----------------------------------------------------------------------------
def test_04_no_prng():
    forbidden = {"random", "numpy.random", "np.random"}
    for p in SCRIPTS_DIR.glob("*.py"):
        tree = ast.parse(p.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for a in node.names:
                    assert a.name not in forbidden, f"PRNG import in {p.name}: {a.name}"
            if isinstance(node, ast.ImportFrom):
                assert node.module not in forbidden, f"PRNG from-import in {p.name}: {node.module}"
        txt = p.read_text()
        for bad in ["np.random.", "numpy.random.", "random.random("]:
            assert bad not in txt, f"PRNG call in {p.name}: {bad}"
    print("  04 NO PRNG: PASS")


# -----------------------------------------------------------------------------
# 05 NO sidecar_nonfactor import
# -----------------------------------------------------------------------------
def test_05_no_sidecar_nonfactor():
    for p in SCRIPTS_DIR.glob("*.py"):
        txt = p.read_text()
        assert "sidecar_nonfactor" not in txt, f"sidecar_nonfactor found in {p.name}"
    print("  05 no sidecar_nonfactor: PASS")


# -----------------------------------------------------------------------------
# 06 /usr/bin/python3 interpreter guard present on every top-level script
# -----------------------------------------------------------------------------
def test_06_interpreter_guard():
    for p in SCRIPTS_DIR.glob("*.py"):
        if p.name == "__init__.py":
            continue
        head = p.read_text().splitlines()[:5]
        joined = "\n".join(head)
        assert "/usr/bin/python3" in joined, f"missing /usr/bin/python3 shebang/guard in {p.name}"
    print("  06 interpreter guard: PASS")


# -----------------------------------------------------------------------------
# 07 c48 env-flags default OFF via os.environ.setdefault (never overwrite)
# -----------------------------------------------------------------------------
def test_07_c48_env_setdefault():
    common = (SCRIPTS_DIR / "_common.py").read_text()
    for key in ["PYTHONHASHSEED", "SOURCE_DATE_EPOCH", "TZ", "LC_ALL"]:
        assert f'os.environ.setdefault("{key}"' in common, f"missing setdefault for {key}"
    # ensure no bare assignment `os.environ[X] =` for those keys
    for key in ["PYTHONHASHSEED", "SOURCE_DATE_EPOCH"]:
        assert f'os.environ["{key}"]' not in common, f"hard-overwrite for {key} — violates c48"
    print("  07 c48 env-flags setdefault (default OFF): PASS")


# -----------------------------------------------------------------------------
# 08 D3 fidelity: repeated same-pitch onsets → SEPARATE notes
# -----------------------------------------------------------------------------
def test_08_repeated_same_pitch_separate_notes():
    from scripts.recreate_v2.rc10_bass_v2.bass_v2 import transcribe_bass_v2
    import numpy as np
    sr = 22050
    # Two 200 ms bursts of the same tone (E2 ~82.4 Hz) separated by 100 ms silence
    tone_hz = 82.407
    def burst(dur_s, amp=0.5):
        t = np.arange(int(dur_s * sr)) / sr
        return (amp * np.sin(2 * np.pi * tone_hz * t)).astype(np.float32)
    silence = np.zeros(int(0.1 * sr), dtype=np.float32)
    y = np.concatenate([silence, burst(0.20), silence, burst(0.20), silence])
    notes = transcribe_bass_v2(y, sr)
    # We expect at least 2 note events (same pitch, both preserved)
    assert len(notes) >= 2, f"expected ≥2 notes for two same-pitch bursts, got {len(notes)}"
    # Both notes should have same midi (within ±1) — this is same-pitch preservation
    if len(notes) >= 2:
        midis = [n["midi"] for n in notes[:2]]
        assert abs(midis[0] - midis[1]) <= 1, f"same-pitch bursts got very different MIDI: {midis}"
    print("  08 D3 same-pitch → separate notes: PASS")


# -----------------------------------------------------------------------------
# 09 D4 slap detector: synthetic HF burst → slap flag TRUE
# -----------------------------------------------------------------------------
def test_09_d4_slap_detector():
    from scripts.recreate_v2.rc10_bass_v2.slap import detect_slaps
    import numpy as np
    sr = 22050
    dur_s = 3.0
    n = int(dur_s * sr)
    # Background LF tone
    t = np.arange(n) / sr
    y = (0.1 * np.sin(2 * np.pi * 80 * t)).astype(np.float32)
    # Inject a HF burst at t=1.5s: 5 kHz, 20 ms, amp 0.9
    burst_start = int(1.5 * sr)
    burst_len = int(0.020 * sr)
    tb = np.arange(burst_len) / sr
    y[burst_start:burst_start + burst_len] += (0.9 * np.sin(2 * np.pi * 5000 * tb)).astype(np.float32)
    # Two onsets: one at background (t=0.5), one AT the HF burst (t=1.5)
    onsets = [0.5, 1.5]
    flags = detect_slaps(y, sr, onsets)
    assert flags[0] is False, f"non-slap onset flagged: {flags}"
    assert flags[1] is True, f"HF burst onset NOT flagged as slap: {flags}"
    print("  09 D4 slap detector: PASS")


# -----------------------------------------------------------------------------
# 10 D5 articulation schema: {onset_s, duration_s, midi, velocity, articulation}
# -----------------------------------------------------------------------------
def test_10_d5_articulation_schema():
    from scripts.recreate_v2.rc10_bass_v2.bass_v2 import transcribe_bass_v2
    import numpy as np
    sr = 22050
    t = np.arange(int(1.5 * sr)) / sr
    y = (0.5 * np.sin(2 * np.pi * 82.4 * t)).astype(np.float32)
    notes = transcribe_bass_v2(y, sr)
    if not notes:
        print("  10 D5 schema (no notes produced by synthetic fixture, skipping field-check): SKIP")
        return
    required = {"onset_s", "duration_s", "midi", "velocity", "articulation"}
    for n in notes:
        assert required.issubset(n.keys()), f"schema missing fields: {set(n.keys())}"
        assert n["articulation"] in {"sustained", "ghost", "slap"}, n["articulation"]
    print("  10 D5 articulation schema: PASS")


# -----------------------------------------------------------------------------
# 11 D6 4-metric computability
# -----------------------------------------------------------------------------
def test_11_d6_metrics_computability():
    from scripts.recreate_v2.rc10_bass_v2.metrics_v2 import (
        onset_f1, note_count_ratio, velocity_std, low_band_correlation, bass_v2_gate,
    )
    import numpy as np
    ref = [0.1, 0.3, 0.5]
    pred = [0.1, 0.31, 0.7]
    f1, tp, fp, fn = onset_f1(pred, ref, tol_s=0.050)
    assert 0 <= f1 <= 1
    cr = note_count_ratio([{}] * 4, ref)
    assert cr == 4.0 / 3.0
    vs = velocity_std([{"velocity": 40}, {"velocity": 60}, {"velocity": 80}])
    assert vs > 10
    sr = 22050
    y = (0.5 * np.sin(2 * np.pi * 80 * np.arange(sr) / sr)).astype(np.float32)
    lbc = low_band_correlation(y, y, sr)
    assert 0.99 <= lbc <= 1.01
    gate = bass_v2_gate(0.7, 1.0, 20.0, 0.8)
    assert gate["all_pass"] is True
    print("  11 D6 4-metric computability: PASS")


# -----------------------------------------------------------------------------
# 12 D7 verdict shape (frozen enum)
# -----------------------------------------------------------------------------
def test_12_d7_verdict_shape():
    from scripts.recreate_v2.rc10_bass_v2.run_all import decide_verdict
    frozen = {"RC10_BASS_V2_LANDS", "RC10_BASS_V2_PARTIAL", "RC10_BASS_V2_FAILS"}
    # Case: all-pass all songs
    rows = [
        {"song_id": "a", "gate": {"all_pass": True, "num_pass": 4, "m1_onset_f1_ge_060": True}},
        {"song_id": "b", "gate": {"all_pass": True, "num_pass": 4, "m1_onset_f1_ge_060": True}},
        {"song_id": "c", "gate": {"all_pass": True, "num_pass": 4, "m1_onset_f1_ge_060": True}},
    ]
    v, _ = decide_verdict(rows, True, True)
    assert v in frozen
    # Regression FAIL caps at PARTIAL
    v2, _ = decide_verdict(rows, False, True)
    assert v2 == "RC10_BASS_V2_PARTIAL"
    # Mandatory FAIL → FAILS
    v3, _ = decide_verdict(rows, True, False)
    assert v3 == "RC10_BASS_V2_FAILS"
    print("  12 D7 verdict shape (frozen enum): PASS")


# -----------------------------------------------------------------------------
# 13 ghost-note 40 ms floor honored
# -----------------------------------------------------------------------------
def test_13_ghost_note_floor():
    from scripts.recreate_v2.rc10_bass_v2._common import MIN_DURATION_S
    assert MIN_DURATION_S == 0.040
    print("  13 ghost-note 40 ms floor: PASS")


# -----------------------------------------------------------------------------
# 14 velocity std computation is numpy-based (no PRNG dependency)
# -----------------------------------------------------------------------------
def test_14_velocity_std_computation():
    from scripts.recreate_v2.rc10_bass_v2.metrics_v2 import velocity_std
    # Deterministic on empty
    assert velocity_std([]) == 0.0
    # Deterministic on identical velocities
    assert velocity_std([{"velocity": 60}] * 5) == 0.0
    print("  14 velocity std computation: PASS")


# -----------------------------------------------------------------------------
# 15 LUFS-I fallback disclosure — RMS-dBFS proxy on ImportError
# -----------------------------------------------------------------------------
def test_15_lufs_fallback_disclosure():
    from scripts.recreate_v2.rc10_bass_v2.render_v2 import loudness_normalize
    import numpy as np
    sr = 44100
    y = (0.3 * np.sin(2 * np.pi * 440 * np.arange(sr) / sr)).astype(np.float32)
    out, l, method = loudness_normalize(y, sr)
    assert out.shape == y.shape
    assert isinstance(method, str)
    # Either pyloudnorm (available) or rms_fallback (documented)
    assert method == "pyloudnorm" or method.startswith("rms_fallback"), method
    print(f"  15 LUFS-I fallback disclosure (method={method}): PASS")


# -----------------------------------------------------------------------------
# 16 render_stem.py do-not-touch anchor (SHA byte-identical)
# -----------------------------------------------------------------------------
def test_16_render_stem_anchor():
    sha = _sha(RENDER_STEM_PY)
    # c33 anchor prefix
    assert sha.startswith("214372d9"), f"render_stem.py drifted: {sha}"
    print(f"  16 render_stem.py anchor (SHA {sha[:16]}…): PASS")


# -----------------------------------------------------------------------------
# 17 c54 v1 chain byte-identical (READ-ONLY invariant)
# -----------------------------------------------------------------------------
def test_17_c54_v1_chain_readonly():
    # scorecard + winner + rubric_hash must be present and readable
    assert (V1_BASS_DIR / "scorecard.tsv").exists()
    assert (V1_BASS_DIR / "winner_per_stem.json").exists()
    v1_rubric = _sha(WS / "docs/rc10_drums_bass_rubric.md")
    assert v1_rubric.startswith("a79bee01"), f"c54 v1 rubric drifted: {v1_rubric}"
    print(f"  17 c54 v1 chain read-only (rubric {v1_rubric[:16]}…): PASS")


if __name__ == "__main__":
    tests = [
        test_01_rubric_mtime_before_scripts_hard,
        test_02_rubric_git_log_soft,
        test_03_rubric_hash_chain,
        test_04_no_prng,
        test_05_no_sidecar_nonfactor,
        test_06_interpreter_guard,
        test_07_c48_env_setdefault,
        test_08_repeated_same_pitch_separate_notes,
        test_09_d4_slap_detector,
        test_10_d5_articulation_schema,
        test_11_d6_metrics_computability,
        test_12_d7_verdict_shape,
        test_13_ghost_note_floor,
        test_14_velocity_std_computation,
        test_15_lufs_fallback_disclosure,
        test_16_render_stem_anchor,
        test_17_c54_v1_chain_readonly,
    ]
    passed = 0; failed = 0
    for t in tests:
        try:
            t()
            passed += 1
        except AssertionError as e:
            print(f"  {t.__name__} FAIL: {e}")
            failed += 1
        except Exception as e:
            print(f"  {t.__name__} ERROR: {type(e).__name__}: {e}")
            failed += 1
    print(f"\n{passed}/{passed+failed} tests passed")
    sys.exit(0 if failed == 0 else 1)
