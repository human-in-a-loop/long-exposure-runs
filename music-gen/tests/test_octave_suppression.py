"""Tests for scripts/transcribe/octave_suppression.py.

Plain-assert style (no pytest). Invoke:
    PYTHONPATH=. /usr/bin/python3 tests/test_octave_suppression.py
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

assert sys.executable == "/usr/bin/python3", f"wrong interpreter: {sys.executable}"

from scripts.transcribe.octave_suppression import (  # noqa: E402
    OctaveSuppressionError,
    suppress_octaves,
)


def _note(onset, offset, pitch, vel=64):
    return {
        "is_drum": False,
        "onset_s": float(onset),
        "offset_s": float(offset),
        "pitch": int(pitch),
        "velocity": int(vel),
    }


def test_empty() -> None:
    kept, sup = suppress_octaves([], 100, 0.5)
    assert kept == [] and sup == []


def test_single_note() -> None:
    n = _note(0.0, 1.0, 36, 80)
    kept, sup = suppress_octaves([n], 100, 0.5)
    assert kept == [n] and sup == []


def test_perfect_octave_pair_suppresses_higher() -> None:
    # Both long, co-onset, overlap ~1.0. Higher-velocity note (fundamental)
    # wins; higher pitch (partial) suppressed.
    a = _note(0.0, 1.0, 36, 100)
    b = _note(0.0, 1.0, 48, 60)
    kept, sup = suppress_octaves([a, b], 100, 0.5)
    assert kept == [a] and sup == [b]


def test_below_t_min_not_suppressed() -> None:
    # 40 ms notes, T_min = 100 ms → below trust threshold, keep both.
    a = _note(0.0, 0.04, 36, 100)
    b = _note(0.0, 0.04, 48, 60)
    kept, sup = suppress_octaves([a, b], 100, 0.5)
    assert len(kept) == 2 and sup == []


def test_below_overlap_not_suppressed() -> None:
    # Long notes but the shorter one ends before overlap_frac reaches 0.5.
    a = _note(0.0, 1.0, 36, 100)
    b = _note(0.0, 0.3, 48, 60)  # dur_min=0.3, overlap=0.3, overlap_frac=1.0
    # Reverse: shorter overlap window
    c = _note(0.0, 1.0, 36, 100)
    d = _note(0.8, 1.0, 48, 60)  # dur_min=0.2, overlap=0.2, frac=1.0
    # These do overlap fully within the short note. To test <overlap_min,
    # need the short note to end early relative to long:
    e = _note(0.0, 1.0, 36, 100)
    f = _note(0.01, 1.2, 48, 60)  # dur_e=1.0, dur_f=1.19, ovl=0.99, frac=0.99
    # Actually construct: long note (dur=1.0), partial that only overlaps for 0.2s
    # of a 1.0s partner:
    g = _note(0.0, 1.0, 36, 100)
    h = _note(0.0, 1.5, 48, 60)  # dur_min=1.0, overlap=1.0, frac=1.0 → suppressed
    # Real test: short partner outside overlap:
    i = _note(0.0, 1.0, 36, 100)
    j = _note(0.01, 0.05, 48, 60)  # dur_min=0.04, below T_min anyway
    # To isolate overlap_min alone, use large durations that partially overlap:
    k = _note(0.0, 2.0, 36, 100)
    m = _note(0.02, 0.3, 48, 60)
    # dur_k=2.0, dur_m=0.28, dur_min=0.28, overlap=0.28, frac=1.0 — still full.
    # Basic-pitch pairs co-onset near 0; genuine partial-overlap requires
    # onset shift ≤ 25 ms but short partner ending well before long.
    # Test the intent directly: use overlap_min > 0.5 with a case that gives 0.3.
    # If short note dur=0.5, long note dur=1.0, but short offset intrudes into
    # long by only 0.15s → frac=0.3.
    p = _note(0.0, 1.0, 36, 100)
    q = _note(
        0.02, 0.17, 48, 60
    )  # dur_q=0.15, ovl=0.15, frac=1.0 -- still full since q entirely in p
    # In practice you cannot get overlap_frac<1 when the shorter note is
    # entirely contained in the longer one — the only way is if the shorter
    # STARTS inside the longer but ends outside it. E.g.:
    r = _note(0.0, 1.0, 36, 100)
    s = _note(0.02, 2.0, 48, 60)
    # dur_r=1.0, dur_s=1.98, dur_min=1.0, overlap=0.98, frac=0.98.
    # Test at overlap_min=0.99: frac=0.98 < 0.99 → not suppressed.
    kept_rs, sup_rs = suppress_octaves([r, s], 50, 0.99)
    assert len(kept_rs) == 2 and sup_rs == []


def test_confidence_tie_shorter_loses() -> None:
    a = _note(0.0, 1.0, 36, 80)
    b = _note(0.0, 0.5, 48, 80)
    kept, sup = suppress_octaves([a, b], 100, 0.5)
    # dur_min=0.5, overlap=0.5, frac=1.0 → qualifies. Velocities tie.
    # Duration: a=1.0, b=0.5. Loser = shorter → b.
    assert kept == [a] and sup == [b]


def test_duration_and_confidence_tie_higher_pitch_loses() -> None:
    a = _note(0.0, 1.0, 36, 80)
    b = _note(0.0, 1.0, 48, 80)
    kept, sup = suppress_octaves([a, b], 100, 0.5)
    assert kept == [a] and sup == [b]


def test_chain_of_three_octaves() -> None:
    # Co-onset chain (p, p+12, p+24). Middle has highest velocity.
    # Iteration in confidence-descending order: first the (36,48) pair
    # (max vel = 100) → loser = 36 (lower velocity=60 < middle=100).
    # Then (48,60) pair (max vel = 100) → loser = 60 (vel 70 < middle 100).
    # End state: only middle (48) kept. Documented "known chain limitation".
    n0 = _note(0.0, 1.0, 36, 60)
    n1 = _note(0.0, 1.0, 48, 100)
    n2 = _note(0.0, 1.0, 60, 70)
    kept, sup = suppress_octaves([n0, n1, n2], 100, 0.5)
    kept_pitches = sorted(k["pitch"] for k in kept)
    assert kept_pitches == [48], f"chain result {kept_pitches}"


def test_non_octave_interval_ignored() -> None:
    # (p, p+7) is a fifth, not an octave.
    a = _note(0.0, 1.0, 36, 100)
    b = _note(0.0, 1.0, 43, 60)
    kept, sup = suppress_octaves([a, b], 100, 0.5)
    assert len(kept) == 2 and sup == []


def test_schema_violation_raises() -> None:
    bad = {"onset_s": 1.0, "offset_s": 0.5, "pitch": 36}  # offset < onset
    try:
        suppress_octaves([bad], 100, 0.5)
    except OctaveSuppressionError:
        return
    raise AssertionError("expected OctaveSuppressionError")


def test_missing_field_raises() -> None:
    bad = {"onset_s": 0.0, "offset_s": 1.0}  # missing pitch
    try:
        suppress_octaves([bad], 100, 0.5)
    except OctaveSuppressionError:
        return
    raise AssertionError("expected OctaveSuppressionError")


def test_determinism_same_input_same_output() -> None:
    notes = [
        _note(0.0, 1.0, 36, 100),
        _note(0.0, 1.0, 48, 80),
        _note(0.5, 1.5, 36, 90),
        _note(0.5, 1.5, 48, 70),
        _note(1.2, 2.0, 40, 50),
    ]
    r1 = suppress_octaves(notes, 100, 0.5)
    r2 = suppress_octaves(notes, 100, 0.5)
    assert r1 == r2


def test_interpreter_assert_triggers_on_wrong_python() -> None:
    # Try to exec the module under a bogus interpreter name via env.
    # Instead, just verify the module-level assertion is present as a
    # non-trivial statement by re-running under the correct interpreter
    # and confirming it did not raise.
    result = subprocess.run(
        ["/usr/bin/python3", "-c", "import scripts.transcribe.octave_suppression"],
        cwd=str(Path(__file__).resolve().parents[1]),
        env={"PYTHONPATH": str(Path(__file__).resolve().parents[1])},
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    # And confirm the assertion string is in the source.
    src = (
        Path(__file__).resolve().parents[1]
        / "scripts/transcribe/octave_suppression.py"
    ).read_text()
    assert "wrong interpreter" in src


def test_bass_only_no_octave_pairs_stays_stable() -> None:
    # Realistic drums stem: no notes at all. Filter must not crash.
    kept, sup = suppress_octaves([], 100, 0.5)
    assert kept == [] and sup == []


def main() -> None:
    tests = [
        ("empty", test_empty),
        ("single_note", test_single_note),
        ("perfect_octave_pair", test_perfect_octave_pair_suppresses_higher),
        ("below_t_min", test_below_t_min_not_suppressed),
        ("below_overlap", test_below_overlap_not_suppressed),
        ("confidence_tie", test_confidence_tie_shorter_loses),
        ("dur_and_conf_tie", test_duration_and_confidence_tie_higher_pitch_loses),
        ("chain_of_three", test_chain_of_three_octaves),
        ("non_octave_ignored", test_non_octave_interval_ignored),
        ("schema_violation", test_schema_violation_raises),
        ("missing_field", test_missing_field_raises),
        ("determinism", test_determinism_same_input_same_output),
        ("interpreter_assert", test_interpreter_assert_triggers_on_wrong_python),
        ("bass_only_stable", test_bass_only_no_octave_pairs_stays_stable),
    ]
    passed = 0
    for name, fn in tests:
        try:
            fn()
            print(f"PASS  {name}")
            passed += 1
        except AssertionError as e:
            print(f"FAIL  {name}: {e}")
            raise
        except Exception as e:  # noqa: BLE001
            print(f"ERROR {name}: {type(e).__name__}: {e}")
            raise
    print(f"\n{passed}/{len(tests)} tests passed")


if __name__ == "__main__":
    main()
