#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-29T04:34:00Z
# cycle: 33
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-TEX-1/palette-driven-bare-render
# ---
"""Per-stem renderer dispatched on assignment.instrument.

Instrument dispatch:
  * fluidsynth_gm — direct subprocess call to `fluidsynth` (c9 anchored
    invocation pattern, copied via documented comment from
    scripts/tex/render_bare_midi.py — that module is NOT imported).
  * sfizz — subprocess call to `sfizz_render` (c31 palette_probe/sfizz.py
    invocation pattern, copied via documented comment — that module is
    NOT imported at runtime).

Output: a 44.1 kHz stereo WAV at `out_dir/render.wav`, canonicalized
through the stdlib `wave` module so header bytes are byte-deterministic
across runs.

NO PRNG. /usr/bin/python3 guarded. No sidecar_nonfactor imports.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np
import soundfile as sf
import scipy.io.wavfile as scipy_wav

assert sys.executable == "/usr/bin/python3", sys.executable

_REPO = Path(__file__).resolve().parents[2]
SAMPLE_RATE = 44100
DURATION_S = 30.0
SAMPLE_COUNT = int(SAMPLE_RATE * DURATION_S)  # 1_323_000

SF2_PATH = Path("/usr/share/sounds/sf2/FluidR3_GM.sf2")
SF2_EXPECTED_SHA = "74594e8f4250680adf590507a306655a299935343583256f3b722c48a1bc1cb0"
SFZ_PATH = _REPO / "data" / "texture" / "test.sfz"
SFIZZ_RENDER = "/usr/bin/sfizz_render"
FLUIDSYNTH = "/usr/bin/fluidsynth"

# Per-stem MIDIs (c6/c9 anchor): basic-pitch transcriptions of the
# synth_030s M-SEP-1 ground-truth stems. These are the "cycle-9 30 s
# synth seed" per-stem inputs. Read-only reads.
PER_STEM_MIDI = {
    "drums": _REPO / "data" / "transcribe" / "basic_pitch" / "synth_030s" / "drums.mid",
    "bass":  _REPO / "data" / "transcribe" / "basic_pitch" / "synth_030s" / "bass.mid",
    "other": _REPO / "data" / "transcribe" / "basic_pitch" / "synth_030s" / "other.mid",
}


def _assert_sf2() -> None:
    """SF2 SHA pin — copied from scripts/tex/render_bare_midi.py verbatim.

    (That module is NOT imported here to satisfy the anti-anchor-import
    contract; the check is duplicated to keep the M-SEP-1 pin
    respected.)
    """
    if not SF2_PATH.is_file():
        raise RuntimeError(f"SF2 missing: {SF2_PATH}")
    h = hashlib.sha256(SF2_PATH.read_bytes()).hexdigest()
    if h != SF2_EXPECTED_SHA:
        raise RuntimeError(f"SF2 SHA mismatch: got {h}, expected {SF2_EXPECTED_SHA}")


def _canonicalize_wav_deterministic(y: np.ndarray, out_wav: Path) -> None:
    """Write a byte-deterministic PCM WAV via scipy.io.wavfile.

    scipy.io.wavfile writes no BEXT/timestamp chunks, so the file-level
    SHA is byte-identical across runs (libsndfile would drift).
    Copied invocation-style from scripts/tex/render_bare_midi.py:83.
    """
    if y.ndim == 1:
        y = np.stack([y, y], axis=1)
    if y.shape[1] == 1:
        y = np.concatenate([y, y], axis=1)
    # trim/pad to exactly SAMPLE_COUNT
    if y.shape[0] > SAMPLE_COUNT:
        y = y[:SAMPLE_COUNT, :]
    elif y.shape[0] < SAMPLE_COUNT:
        pad = np.zeros((SAMPLE_COUNT - y.shape[0], y.shape[1]), dtype=y.dtype)
        y = np.concatenate([y, pad], axis=0)
    scipy_wav.write(str(out_wav), SAMPLE_RATE, y.astype(np.float32))


def render_fluidsynth(midi_path: Path, out_wav: Path) -> None:
    """Fluidsynth CLI dispatch. Command line copied verbatim from
    scripts/tex/render_bare_midi.py:70 — that module is NOT imported.
    """
    _assert_sf2()
    if not midi_path.is_file():
        raise RuntimeError(f"MIDI missing: {midi_path}")
    tmp = out_wav.with_suffix(".raw.wav")
    if tmp.exists():
        tmp.unlink()
    cmd = [
        FLUIDSYNTH, "-a", "null", "-T", "wav",
        "-F", str(tmp),
        "-r", str(SAMPLE_RATE),
        "-g", "1.0",
        "-i",
        str(SF2_PATH), str(midi_path),
    ]
    subprocess.run(cmd, check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    y, got_sr = sf.read(str(tmp), always_2d=True)
    if got_sr != SAMPLE_RATE:
        raise RuntimeError(f"fluidsynth sr={got_sr}, expected {SAMPLE_RATE}")
    _canonicalize_wav_deterministic(y, out_wav)
    tmp.unlink()


def render_sfizz(midi_path: Path, out_wav: Path,
                 block_size: int = 512) -> None:
    """sfizz_render CLI dispatch. Command line copied via documented
    comment from scripts/palette_probe/sfizz.py:82 — that module is
    NOT imported.

    Note: sfizz_render doesn't have a --duration flag; it renders MIDI
    to completion. If the MIDI is shorter than 30s we pad; longer we
    trim. Both happen inside _canonicalize_wav_deterministic.
    """
    if not SFZ_PATH.is_file():
        raise RuntimeError(f"SFZ missing: {SFZ_PATH}")
    if not midi_path.is_file():
        raise RuntimeError(f"MIDI missing: {midi_path}")
    if not Path(SFIZZ_RENDER).is_file():
        raise RuntimeError(f"sfizz_render binary missing: {SFIZZ_RENDER}")
    raw = out_wav.with_suffix(".raw.wav")
    if raw.exists():
        raw.unlink()
    cmd = [
        SFIZZ_RENDER,
        "--sfz", str(SFZ_PATH),
        "--midi", str(midi_path),
        "--wav", str(raw),
        "-b", str(block_size),
        "-s", str(SAMPLE_RATE),
        "-q", "1",
        "-p", "64",
    ]
    subprocess.run(cmd, check=True, capture_output=True, text=True)
    # sfizz_render writes int16 mono/stereo — read via soundfile as float.
    data, sr = sf.read(str(raw), always_2d=True)
    if sr != SAMPLE_RATE:
        raise RuntimeError(f"sfizz sr={sr}, expected {SAMPLE_RATE}")
    _canonicalize_wav_deterministic(data.astype(np.float32), out_wav)
    raw.unlink()


def render_stem(stem: str, instrument: str, out_dir: Path) -> dict:
    """Render one stem twice, verify byte-determinism, save SHAs.

    Returns dict:
      {"stem": stem, "instrument": instrument,
       "midi_path": str, "midi_sha": str,
       "render_run1_sha": str, "render_run2_sha": str,
       "sha_equal": bool, "run1_wav_path": str}
    """
    if stem not in PER_STEM_MIDI:
        raise RuntimeError(f"unknown stem {stem}")
    midi_path = PER_STEM_MIDI[stem]
    if not midi_path.is_file():
        raise RuntimeError(f"per-stem MIDI missing: {midi_path}")

    out_dir.mkdir(parents=True, exist_ok=True)
    out1 = out_dir / "render_run1.wav"
    out2 = out_dir / "render_run2.wav"

    if instrument == "fluidsynth_gm":
        render_fluidsynth(midi_path, out1)
        render_fluidsynth(midi_path, out2)
    elif instrument == "sfizz":
        render_sfizz(midi_path, out1)
        render_sfizz(midi_path, out2)
    else:
        raise RuntimeError(f"unsupported instrument {instrument} for palette-render "
                           f"(Surge XT / Dexed excluded per c31 STILL_GAP)")

    sha1 = hashlib.sha256(out1.read_bytes()).hexdigest()
    sha2 = hashlib.sha256(out2.read_bytes()).hexdigest()
    (out_dir / "render_run1.wav.sha").write_text(sha1 + "\n")
    (out_dir / "render_run2.wav.sha").write_text(sha2 + "\n")

    midi_sha = hashlib.sha256(midi_path.read_bytes()).hexdigest()
    pinned = {
        "stem": stem,
        "instrument": instrument,
        "midi_input_sha256": midi_sha,
        "sample_rate": SAMPLE_RATE,
        "sample_count": SAMPLE_COUNT,
        "sha_equal": sha1 == sha2,
    }
    (out_dir / "pinned_state.json").write_text(
        json.dumps(pinned, sort_keys=True, indent=2) + "\n")

    return {
        "stem": stem, "instrument": instrument,
        "midi_path": str(midi_path), "midi_sha": midi_sha,
        "render_run1_sha": sha1, "render_run2_sha": sha2,
        "sha_equal": sha1 == sha2,
        "run1_wav_path": str(out1), "run2_wav_path": str(out2),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stem", required=True, choices=["drums", "bass", "other"])
    ap.add_argument("--instrument", required=True)
    ap.add_argument("--out-dir", required=True)
    a = ap.parse_args()
    result = render_stem(a.stem, a.instrument, Path(a.out_dir))
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
