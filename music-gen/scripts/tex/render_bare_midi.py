#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-28T10:30:00Z
# cycle: 9
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-TEX-1/stage-by-stage
# ---
"""Thin wrapper around fluidsynth for bare-MIDI rendering.

Contract:
    render_bare_midi(midi_path, out_wav_path, sf2_path, sr=44100,
                     duration_s=None) -> None

Invocation flags are copied verbatim from scripts/separation/synth_gt.py
(M-SEP-1/ground-truth) so the two paths remain byte-comparable:

    fluidsynth -a null -T wav -F <out> -r 44100 -g 1.0 -i <sf2> <midi>

The SF2 sha-256 is asserted before rendering (74594e8f...1cb0). Rendering
is refused otherwise — the M-SEP-1 pinning contract holds here too.
"""
from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path

import numpy as np
import soundfile as sf
import scipy.io.wavfile as scipy_wav

assert sys.executable == "/usr/bin/python3", sys.executable

SF2_EXPECTED_SHA = "74594e8f4250680adf590507a306655a299935343583256f3b722c48a1bc1cb0"


def _assert_sf2(sf2_path: Path) -> None:
    h = hashlib.sha256(sf2_path.read_bytes()).hexdigest()
    if h != SF2_EXPECTED_SHA:
        raise RuntimeError(
            f"SF2 sha mismatch on {sf2_path}: got {h}, expected "
            f"{SF2_EXPECTED_SHA}. Refusing to render (M-SEP-1 pin).")


def render_bare_midi(midi_path: Path, out_wav_path: Path, sf2_path: Path,
                     sr: int = 44100, duration_s: float | None = None) -> None:
    """Render midi_path with fluidsynth to a stereo 44.1 kHz WAV.

    If duration_s is given, trim/pad the output to exactly that many
    samples. Otherwise, keep the fluidsynth output length verbatim.
    """
    midi_path = Path(midi_path)
    out_wav_path = Path(out_wav_path)
    sf2_path = Path(sf2_path)
    _assert_sf2(sf2_path)

    tmp = out_wav_path.with_suffix(".raw.wav")
    if tmp.exists():
        tmp.unlink()
    if out_wav_path.exists():
        out_wav_path.unlink()

    cmd = [
        "fluidsynth", "-a", "null", "-T", "wav",
        "-F", str(tmp),
        "-r", str(sr),
        "-g", "1.0",
        "-i",
        str(sf2_path), str(midi_path),
    ]
    subprocess.run(cmd, check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    y, got_sr = sf.read(str(tmp), always_2d=True)
    if got_sr != sr:
        raise RuntimeError(f"expected sr={sr}, got {got_sr}")
    if y.shape[1] == 1:
        y = np.concatenate([y, y], axis=1)

    if duration_s is not None:
        n_target = int(round(duration_s * sr))
        if y.shape[0] < n_target:
            pad = np.zeros((n_target - y.shape[0], y.shape[1]), dtype=y.dtype)
            y = np.concatenate([y, pad], axis=0)
        else:
            y = y[:n_target]

    # Use scipy.io.wavfile so no BEXT/timestamp metadata is written; this
    # makes file-level SHA byte-identical across runs (libsndfile writes a
    # creation-date chunk that would otherwise drift).
    scipy_wav.write(str(out_wav_path), sr, y.astype(np.float32))
    tmp.unlink()


def main():  # pragma: no cover
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--midi", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--sf2", default="/usr/share/sounds/sf2/FluidR3_GM.sf2")
    ap.add_argument("--sr", type=int, default=44100)
    ap.add_argument("--duration", type=float, default=None)
    args = ap.parse_args()
    render_bare_midi(Path(args.midi), Path(args.out), Path(args.sf2),
                     sr=args.sr, duration_s=args.duration)
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
