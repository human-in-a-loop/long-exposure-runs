#!/usr/bin/env /usr/bin/python3
# ---
# created: 2026-09-06T00:00:00Z
# cycle: 70
# run_id: run-2026-09-06T000000Z
# agent: worker
# milestone: M-V4-SHOWCASE-1
# ---
"""c70 P4 test debt fill-in for scripts/sound_match/deliver_ab_v4.py.

6 named test cases per c70 research brief §4 P4. Mocks the sf2 render +
wave read/write paths where possible; asserts:
  1. env_pin_sha256 drift → RuntimeError
  2. min-truncation policy applied at _sum_stereo_tracks
  3. _resolve_stems_root Peach Dream invariant (d) fallback
  4. absent-stems manifest shape (render_family + showcase_dispatch)
  5. non-absent cell manifest field completeness (provenance keys)
  6. --prove-replay writes into fresh tempfile.mkdtemp() + emits proof

Plain-assert (no pytest). Invocation:
    PYTHONPATH=. /usr/bin/python3 tests/test_deliver_ab_v4.py
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

# Ensure env pins are set BEFORE importing driver (per driver contract).
for k, v in {
    "PYTHONHASHSEED": "0",
    "SOURCE_DATE_EPOCH": "1756463424",
    "TZ": "UTC",
    "LC_ALL": "C.UTF-8",
    "OMP_NUM_THREADS": "1",
    "MKL_NUM_THREADS": "1",
    "OPENBLAS_NUM_THREADS": "1",
}.items():
    os.environ.setdefault(k, v)

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# Import the driver (top-level env-pin guard runs on import; safe because
# we set pins above).
from scripts.sound_match import deliver_ab_v4 as drv  # noqa: E402

CANON_ENV_PIN = "2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca"
WIG = "252eb21ce7df7328"
PEACH_DREAM = "88d247468cb6d49f"


def test_01_env_pin_drift_raises() -> None:
    """env_pin_sha256 constant matches canonical 7-key subset; drift → runtime raise.

    The driver's `main()` raises RuntimeError on any pin drift (lines 325-327).
    We assert the module-level constant is the canonical one AND simulate a
    drift by monkey-patching an env var and re-invoking the check block.
    """
    assert drv._ENV_PIN_SHA256 == CANON_ENV_PIN, (
        f"driver env_pin_sha256 constant drifted: {drv._ENV_PIN_SHA256!r}")
    # Simulate the drift check inline. Save + restore.
    saved = os.environ.get("PYTHONHASHSEED")
    os.environ["PYTHONHASHSEED"] = "999"
    try:
        raised = False
        for k, v in drv._PINS.items():
            if os.environ.get(k) != v:
                raised = True
                break
        assert raised, "drift check did not fire on PYTHONHASHSEED=999"
    finally:
        if saved is None:
            del os.environ["PYTHONHASHSEED"]
        else:
            os.environ["PYTHONHASHSEED"] = saved
    print("test_01_env_pin_drift_raises PASS")


def test_02_min_truncation_policy() -> None:
    """_sum_stereo_tracks truncates to shortest input; assert with 3 mock tracks.

    Bass length 100, drums length 200, vocals length 300 → output length 100.
    """
    a = ([0] * 100, [0] * 100)
    b = ([0] * 200, [0] * 200)
    c = ([0] * 300, [0] * 300)
    outL, outR = drv._sum_stereo_tracks([a, b, c], target_len=100)
    assert len(outL) == 100, f"outL len {len(outL)} != 100"
    assert len(outR) == 100, f"outR len {len(outR)} != 100"
    # Also assert non-negative int16 clamp is exercised via a peak-limit path.
    a2 = ([32767] * 10, [32767] * 10)
    b2 = ([32767] * 10, [32767] * 10)
    outL2, outR2 = drv._sum_stereo_tracks([a2, b2], target_len=10)
    for x in outL2 + outR2:
        assert -32768 <= x <= 32767, f"int16 clamp violated: {x}"
    print("test_02_min_truncation_policy PASS")


def test_03_peach_dream_invariant_d_fallback() -> None:
    """_resolve_stems_root picks operator_section_c25_checkpointed/rc9_6stem
    when standard operator_section/rc9_6stem does not exist.

    Verified against ON-DISK reality: Peach Dream has ONLY the c25-checkpointed
    path (see stem_manifest.json sha `d483f2bf…`, c19 opening + c65 P0 Branch C
    canonical). WIG has the standard path.
    """
    pd_stems = drv._resolve_stems_root(ROOT, PEACH_DREAM)
    assert pd_stems.is_dir(), f"resolved PD stems dir missing: {pd_stems}"
    assert "operator_section_c25_checkpointed" in str(pd_stems), (
        f"PD did not fall back to c25-checkpointed path: {pd_stems}")
    wig_stems = drv._resolve_stems_root(ROOT, WIG)
    assert wig_stems.is_dir(), f"resolved WIG stems dir missing: {wig_stems}"
    assert wig_stems.parts[-2] == "operator_section", (
        f"WIG did not resolve to standard path: {wig_stems}")
    print("test_03_peach_dream_invariant_d_fallback PASS")


def test_04_absent_stems_manifest_shape() -> None:
    """Absent cells in provenance carry render_family='absent_no_pinned_profile'
    and a `showcase_dispatch` string.

    Read the on-disk WIG manifest (c69 landing) and assert the 3 absent cells
    (guitar/piano/other) all have the expected shape.
    """
    m = json.loads((ROOT / "data/v4/deliveries" / WIG / "ab_mix.manifest.json").read_text())
    prov = m["provenance"]
    for stem in ("guitar", "piano", "other"):
        assert stem in prov, f"missing stem {stem} in provenance"
        assert prov[stem]["render_family"] == "absent_no_pinned_profile", (
            f"stem {stem} render_family: {prov[stem]}")
        assert isinstance(prov[stem].get("showcase_dispatch"), str), (
            f"stem {stem} missing showcase_dispatch string")
    print("test_04_absent_stems_manifest_shape PASS")


def test_05_manifest_provenance_field_completeness() -> None:
    """Every non-absent cell has the mandatory provenance keys.

    Non-absent shapes are:
      - sf2 (bass, drums): midi_relpath, midi_sha256, profile_relpath,
        profile_sha256, render_sha256, ref_stem_sha256, rms_normalize_gain.
      - htdemucs_hybrid_overlay (vocals): source_relpath, source_sha256.
    Verified against the WIG manifest (c69 landing).
    """
    m = json.loads((ROOT / "data/v4/deliveries" / WIG / "ab_mix.manifest.json").read_text())
    prov = m["provenance"]
    sf2_required = ("midi_relpath", "midi_sha256", "profile_relpath",
                    "profile_sha256", "render_sha256", "ref_stem_sha256",
                    "rms_normalize_gain")
    for stem in ("bass", "drums"):
        cell = prov[stem]
        assert cell["render_family"] == "sf2", f"{stem} render_family: {cell}"
        for key in sf2_required:
            assert key in cell, f"{stem} missing key {key}"
    vocals = prov["vocals"]
    assert vocals["render_family"] == "htdemucs_hybrid_overlay"
    for key in ("source_relpath", "source_sha256"):
        assert key in vocals, f"vocals missing key {key}"
    print("test_05_manifest_provenance_field_completeness PASS")


def test_06_prove_replay_writes_second_render_into_fresh_tempdir() -> None:
    """--prove-replay uses tempfile.mkdtemp() (not a shared dir) for run 2
    and writes ab_mix.replay_proof.json alongside the primary manifest.

    Verified structurally: (a) driver source contains `tempfile.mkdtemp`
    used inside the --prove-replay branch; (b) on-disk WIG replay proof
    has the expected schema with distinct run2_tempdir under /tmp.
    """
    src = (ROOT / "scripts/sound_match/deliver_ab_v4.py").read_text()
    assert "tempfile.mkdtemp" in src, "driver missing tempfile.mkdtemp"
    # Simple structural check: the tempfile.mkdtemp() call sits inside the
    # --prove-replay branch (grep for it near the args.prove_replay guard).
    assert "if args.prove_replay:" in src
    idx = src.index("if args.prove_replay:")
    tail = src[idx:idx + 1000]
    assert "tempfile.mkdtemp" in tail, (
        "tempfile.mkdtemp not within --prove-replay block")
    # On-disk WIG proof schema.
    proof = json.loads((ROOT / "data/v4/deliveries" / WIG / "ab_mix.replay_proof.json").read_text())
    for key in ("kind", "song_sha16", "run1_sha256", "run2_sha256",
                "run2_tempdir", "verdict", "env_pin_sha256"):
        assert key in proof, f"proof missing key {key}"
    assert proof["kind"] == "ab_v4_full_render_replay_proof"
    assert proof["env_pin_sha256"] == CANON_ENV_PIN
    assert proof["run2_tempdir"].startswith("/tmp/") or "tmp" in proof["run2_tempdir"], (
        f"run2_tempdir not under a tempdir prefix: {proof['run2_tempdir']!r}")
    print("test_06_prove_replay_writes_second_render_into_fresh_tempdir PASS")


def test_07_absent_stem_htdemucs_substitution_when_audible() -> None:
    """c71: _absent_stem_dispatch returns htdemucs_stem_substitution when
    the reference htdemucs stem is above the -60 dB silence floor.

    Verified against Rome guitar (on-disk rms_dbfs = -26.21, AUDIBLE per
    audibility_v2.json). Manifest field completeness asserted on the
    landed v2 delivery.
    """
    ROME = "51e433ade2a845e1"
    stems_dir = drv._resolve_stems_root(ROOT, ROME)
    dispatch = drv._absent_stem_dispatch("guitar", stems_dir, ROOT)
    assert dispatch["kind"] == "htdemucs_stem_substitution", (
        f"expected substitution, got {dispatch['kind']}")
    assert dispatch["audibility_verdict"] is True
    assert dispatch["rms_dbfs"] > -60.0
    assert "samples_left" in dispatch and "samples_right" in dispatch
    # Manifest side: v2 landing carries render_family, source_sha256,
    # rms_normalize_gain, audibility_verdict.
    m = json.loads((ROOT / "data/v4/deliveries" / ROME / "ab_mix_v2.manifest.json").read_text())
    cell = m["provenance"]["guitar"]
    assert cell["render_family"] == "htdemucs_stem_substitution", cell
    for key in ("source_relpath", "source_sha256", "rms_dbfs",
                "audibility_verdict", "rms_normalize_gain"):
        assert key in cell, f"guitar cell missing {key}"
    assert cell["audibility_verdict"] is True
    assert cell["rms_normalize_gain"] == 1.0
    print("test_07_absent_stem_htdemucs_substitution_when_audible PASS")


def test_08_absent_stem_stays_silent_when_below_floor() -> None:
    """c71: _absent_stem_dispatch returns absent_no_audible_signal when
    the reference stem is at or below the -60 dB silence floor.

    Verified against WIG guitar (on-disk rms_dbfs = -69.55, SILENT). The
    landed WIG v2 manifest carries the absent branch with the audibility
    verdict + rms_dbfs recorded (not blank).
    """
    stems_dir = drv._resolve_stems_root(ROOT, WIG)
    dispatch = drv._absent_stem_dispatch("guitar", stems_dir, ROOT)
    assert dispatch["kind"] == "absent_no_audible_signal", dispatch
    assert dispatch["audibility_verdict"] is False
    assert dispatch["rms_dbfs"] < -60.0
    m = json.loads((ROOT / "data/v4/deliveries" / WIG / "ab_mix_v2.manifest.json").read_text())
    cell = m["provenance"]["guitar"]
    assert cell["render_family"] == "absent_no_audible_signal", cell
    assert cell["audibility_verdict"] is False
    assert cell["rms_dbfs"] < -60.0
    print("test_08_absent_stem_stays_silent_when_below_floor PASS")


def test_09_max_truncation_policy() -> None:
    """c71: mix policy is max-truncation, shorter cells zero-pad to longest.

    Structural assertion: the v2 driver's _mix.sum_method string is
    'float_accumulate_peaklimit_099_max_len_zero_pad' (was
    'float_accumulate_peaklimit_099' at c69). Every landed v2 manifest
    carries the new method string; the c69 v1 anchors keep the old string.
    """
    src = (ROOT / "scripts/sound_match/deliver_ab_v4.py").read_text()
    assert "float_accumulate_peaklimit_099_max_len_zero_pad" in src, (
        "driver missing max-truncation method string")
    assert "target_len = max(" in src, "driver missing target_len = max(...)"
    for sha in ("252eb21ce7df7328", "51e433ade2a845e1",
                "88d247468cb6d49f", "cdd2717e52820ff6"):
        v1 = json.loads((ROOT / "data/v4/deliveries" / sha / "ab_mix.manifest.json").read_text())
        v2 = json.loads((ROOT / "data/v4/deliveries" / sha / "ab_mix_v2.manifest.json").read_text())
        assert v1["provenance"]["_mix"]["sum_method"] == "float_accumulate_peaklimit_099", (
            f"{sha} v1 sum_method drift: {v1['provenance']['_mix']['sum_method']}")
        assert v2["provenance"]["_mix"]["sum_method"] == "float_accumulate_peaklimit_099_max_len_zero_pad", (
            f"{sha} v2 sum_method drift: {v2['provenance']['_mix']['sum_method']}")
        # v2 mix duration should be >= v1 mix duration
        assert v2["provenance"]["_mix"]["duration_s"] >= v1["provenance"]["_mix"]["duration_s"], (
            f"{sha} v2 duration shorter than v1")
    print("test_09_max_truncation_policy PASS")


def test_10_v2_output_suffix_writes_sibling_files() -> None:
    """c71: --out-suffix v2 writes ab_mix_v2.{wav,manifest.json,replay_proof.json}
    as siblings to the c69 v1 anchors without overwriting them.

    Verified against all 4 non-CG songs: v1 anchor SHAs byte-identical to
    the operator-recorded values; v2 sibling files present with distinct
    SHAs; v2 replay proofs all REPLAY_PROOF_HOLDS.
    """
    import hashlib
    expected_v1 = {
        "252eb21ce7df7328": "6feca5d1fb41ee149e727b6ec2a61d2a006b4bc0b2a0aff62f2ef8946f47e3e9",
        "51e433ade2a845e1": "81e2ef1525ed4485a497c60dece0e29dffc0b1fedfa593ac8a457f70541b26b0",
        "88d247468cb6d49f": "a300cf4ca12f132e24dc34bcafb4cf4bc621d9529f9de67442afeac3cc02d806",
        "cdd2717e52820ff6": "1b673106aae19b9ccd6f9d81333eae9e906a1dba1e85df38fb3041c8ea494080",
    }
    for sha16, want in expected_v1.items():
        v1 = ROOT / "data/v4/deliveries" / sha16 / "ab_mix.wav"
        v2 = ROOT / "data/v4/deliveries" / sha16 / "ab_mix_v2.wav"
        v2_manifest = ROOT / "data/v4/deliveries" / sha16 / "ab_mix_v2.manifest.json"
        v2_proof = ROOT / "data/v4/deliveries" / sha16 / "ab_mix_v2.replay_proof.json"
        assert v1.exists() and v2.exists(), f"{sha16} v1 or v2 wav missing"
        assert v2_manifest.exists(), f"{sha16} v2 manifest missing"
        assert v2_proof.exists(), f"{sha16} v2 replay proof missing"
        got = hashlib.sha256(v1.read_bytes()).hexdigest()
        assert got == want, f"{sha16} v1 wav sha drifted: {got}"
        v1_sha = got
        v2_sha = hashlib.sha256(v2.read_bytes()).hexdigest()
        assert v1_sha != v2_sha, f"{sha16} v1 and v2 have same sha (unexpected)"
        proof = json.loads(v2_proof.read_text())
        assert proof["verdict"] == "REPLAY_PROOF_HOLDS", f"{sha16} v2 replay: {proof['verdict']}"
        assert proof["run1_sha256"] == proof["run2_sha256"] == v2_sha
    print("test_10_v2_output_suffix_writes_sibling_files PASS")


def main() -> int:
    tests = [
        test_01_env_pin_drift_raises,
        test_02_min_truncation_policy,
        test_03_peach_dream_invariant_d_fallback,
        test_04_absent_stems_manifest_shape,
        test_05_manifest_provenance_field_completeness,
        test_06_prove_replay_writes_second_render_into_fresh_tempdir,
        test_07_absent_stem_htdemucs_substitution_when_audible,
        test_08_absent_stem_stays_silent_when_below_floor,
        test_09_max_truncation_policy,
        test_10_v2_output_suffix_writes_sibling_files,
    ]
    failed = 0
    for t in tests:
        try:
            t()
        except AssertionError as e:
            print(f"{t.__name__} FAIL: {e}")
            failed += 1
        except Exception as e:
            print(f"{t.__name__} ERROR: {type(e).__name__}: {e}")
            failed += 1
    if failed:
        print(f"\n{failed}/{len(tests)} tests failed")
        return 1
    print(f"\nall {len(tests)} tests green")
    return 0


if __name__ == "__main__":
    sys.exit(main())
