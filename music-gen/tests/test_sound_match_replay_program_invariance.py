#!/usr/bin/env -S /usr/bin/python3
"""c6 regression tests for scripts/sound_match/replay.py program-invariance fix.

Test A: two profiles differing ONLY in identity.program produce DIFFERENT
        replay SHAs on the same MIDI (proves fix took effect).
Test B: same profile invoked twice into fresh tempdirs produces byte-identical
        SHAs (preserves REPLAY_PROOF_HOLDS scoping).
Test C: replaying bass_v2.json (prog 33) against bass.mid (embedding prog 33)
        matches the SHA class of the profile-forced prog-33 render.

No PRNG. No sidecar_nonfactor. Env pins set BEFORE any observed import.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import tempfile
from pathlib import Path

_PINS = {
    "PYTHONHASHSEED": "0",
    "SOURCE_DATE_EPOCH": "1756463424",
    "TZ": "UTC",
    "LC_ALL": "C.UTF-8",
    "OMP_NUM_THREADS": "1",
    "MKL_NUM_THREADS": "1",
    "OPENBLAS_NUM_THREADS": "1",
}
for _k, _v in _PINS.items():
    os.environ.setdefault(_k, _v)

if sys.executable != "/usr/bin/python3":
    raise RuntimeError(f"requires /usr/bin/python3 (got {sys.executable})")

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from scripts.sound_match.replay import replay  # noqa: E402


def _sha(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


BASS_MIDI = REPO / "data/v4/profiles/31a164f845f8e27e/bass_sweep_stage1/inputs/bass.mid"
SF2_PATH = Path("/usr/share/sounds/sf2/FluidR3_GM.sf2")


def _profile(program: int) -> dict:
    return {
        "family": "sf2",
        "identity": {
            "sf2_path": str(SF2_PATH),
            "bank": 0,
            "program": program,
        },
        "params": {"sample_rate": 44100, "gain": 0.5},
    }


def _strip_program_changes(src_midi: Path, out_midi: Path) -> None:
    """Write a copy of src_midi with all program_change events stripped."""
    import mido
    mid = mido.MidiFile(str(src_midi))
    for tr in mid.tracks:
        to_del = [i for i, m in enumerate(tr) if m.type == "program_change"]
        for i in reversed(to_del):
            del tr[i]
    mid.save(str(out_midi))


def test_A_negative_inversion():
    """Two profiles differing ONLY in program produce different SHAs."""
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        stripped = td / "bass_stripped.mid"
        _strip_program_changes(BASS_MIDI, stripped)
        w1 = td / "prog17.wav"
        w2 = td / "prog33.wav"
        sha_17 = replay(_profile(17), stripped, w1)
        sha_33 = replay(_profile(33), stripped, w2)
        assert sha_17 != sha_33, (
            f"Test A FAIL: prog 17 and prog 33 produced identical SHA "
            f"{sha_17} — fix took no effect."
        )
        print(f"Test A PASS: prog17={sha_17[:16]} != prog33={sha_33[:16]}")


def test_B_positive_determinism():
    """Same profile invoked twice into fresh tempdirs → byte-identical SHAs."""
    prof = _profile(33)
    with tempfile.TemporaryDirectory() as td1, tempfile.TemporaryDirectory() as td2:
        w1 = Path(td1) / "r.wav"
        w2 = Path(td2) / "r.wav"
        s1 = replay(prof, BASS_MIDI, w1)
        s2 = replay(prof, BASS_MIDI, w2)
        assert s1 == s2, f"Test B FAIL: byte-determinism broken {s1} != {s2}"
        print(f"Test B PASS: byte-det ×2 SHA {s1[:16]}")


def test_C_existing_midi_neutrality():
    """bass_v2 (prog 33) vs bass.mid (embeds prog 33) → SHA class matches
    forced prog-33 render from Test A on stripped MIDI."""
    v2_path = REPO / "data/v4/profiles/31a164f845f8e27e/bass_v2.json"
    prof_v2 = json.loads(v2_path.read_text())
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        w_v2 = td / "v2.wav"
        s_v2 = replay(prof_v2, BASS_MIDI, w_v2)
        # Comparison target: profile forced prog 33 on the original bass.mid.
        # Post-fix behavior: fluidsynth honors profile.program which is 33;
        # bass.mid's embedded prog=33 is stripped by our rewrite and re-injected
        # as prog=33 → same audio.
        w_forced = td / "forced.wav"
        s_forced = replay(_profile(33), BASS_MIDI, w_forced)
        assert s_v2 == s_forced, (
            f"Test C FAIL: bass_v2 replay {s_v2} != profile-forced prog-33 {s_forced}"
        )
        print(f"Test C PASS: bass_v2 and forced-prog-33 both SHA {s_v2[:16]}")


def main():
    matrix = {}
    for name, fn in [("A", test_A_negative_inversion),
                     ("B", test_B_positive_determinism),
                     ("C", test_C_existing_midi_neutrality)]:
        try:
            fn()
            matrix[name] = "pass"
        except AssertionError as e:
            matrix[name] = f"fail: {e}"
            raise
        except Exception as e:
            matrix[name] = f"error: {type(e).__name__}: {e}"
            raise
    return matrix


if __name__ == "__main__":
    matrix = main()
    out = Path("data/v4/profiles/31a164f845f8e27e/replay_fix_test_matrix.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"test_matrix": matrix}, sort_keys=True, indent=2))
    print(json.dumps(matrix, sort_keys=True, indent=2))
