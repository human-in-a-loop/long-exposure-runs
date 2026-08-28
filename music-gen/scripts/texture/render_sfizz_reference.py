#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-28T05:20:00Z
# cycle: 4
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-TEX-1/panel
# ---
"""Render the fluidsynth-vs-sfizz same-MIDI validation pair.

Emits:
    data/texture/test.mid          — C-major arpeggio, 4 quarter notes/bar,
                                     120 BPM, 8 s total
    data/texture/test_midi_sha.txt — SHA-256 of the MIDI file
    data/texture/test.sfz          — minimal SFZ mapping notes to a saw wave
    data/texture/test_saw.wav      — one-cycle saw sample used by test.sfz
    data/texture/fluid_render.wav  — fluidsynth render (FluidR3_GM.sf2)
    data/texture/sfizz_render.wav  — sfizz_render on test.sfz + test.mid

Both renders at 48 kHz stereo. Same MIDI, same SR. Different tone
generators → known-different by texture, matched by content.
"""
from __future__ import annotations

import hashlib
import pathlib
import shutil
import subprocess
import sys

import numpy as np
import pretty_midi
import soundfile as sf

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / "data" / "texture"
SR = 48000
BPM = 120
DURATION_S = 8.0
SOUNDFONT = "/usr/share/sounds/sf2/FluidR3_GM.sf2"


def build_midi(path: pathlib.Path) -> None:
    pm = pretty_midi.PrettyMIDI(initial_tempo=BPM)
    inst = pretty_midi.Instrument(program=0)  # Acoustic Grand Piano for fluid
    # C-major arpeggio: C4 E4 G4 C5, repeated. Quarter notes at 120 BPM = 0.5 s each.
    notes = [60, 64, 67, 72]
    q = 60.0 / BPM
    t = 0.0
    idx = 0
    while t + q <= DURATION_S:
        pitch = notes[idx % len(notes)]
        inst.notes.append(pretty_midi.Note(
            velocity=100, pitch=pitch, start=t, end=t + q * 0.95,
        ))
        t += q
        idx += 1
    pm.instruments.append(inst)
    pm.write(str(path))


def build_saw(path: pathlib.Path) -> None:
    # One-cycle saw @ 261.626 Hz (C4); SFZ resamples across the keyboard.
    freq = 261.6255653005986
    n = int(round(SR / freq))
    x = np.linspace(-1.0, 1.0, n, endpoint=False).astype(np.float32) * 0.7
    sf.write(str(path), x, SR, subtype="PCM_16")


def build_sfz(path: pathlib.Path, sample_name: str) -> None:
    # Root key 60 (C4). sfizz will pitch-shift to cover the whole keyboard.
    sfz = (
        "<region>\n"
        f"sample={sample_name}\n"
        "pitch_keycenter=60\n"
        "lokey=0 hikey=127\n"
        "loop_mode=loop_continuous\n"
        "ampeg_attack=0.005\n"
        "ampeg_release=0.05\n"
    )
    path.write_text(sfz)


def sha256(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def render_fluidsynth(midi: pathlib.Path, out: pathlib.Path) -> None:
    if not pathlib.Path(SOUNDFONT).exists():  # pragma: no cover
        raise RuntimeError(f"soundfont missing: {SOUNDFONT}")
    cmd = [
        "fluidsynth", "-ni", "-F", str(out), "-r", str(SR),
        "-T", "wav", SOUNDFONT, str(midi),
    ]
    subprocess.run(cmd, check=True, capture_output=True)


def render_sfizz(sfz: pathlib.Path, midi: pathlib.Path, out: pathlib.Path) -> None:
    # sfizz_render CLI. Duration is inferred from MIDI + release tail.
    cmd = [
        "sfizz_render",
        "--wav", str(out),
        "--sfz", str(sfz),
        "--midi", str(midi),
        "--samplerate", str(SR),
        "--use-eot",
    ]
    r = subprocess.run(cmd, check=False, capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(
            f"sfizz_render failed rc={r.returncode}\n"
            f"stdout={r.stdout.decode(errors='replace')}\n"
            f"stderr={r.stderr.decode(errors='replace')}"
        )


def ensure_stereo_48k(path: pathlib.Path) -> None:
    """Both renders must be stereo @ 48 kHz. Post-process if needed."""
    audio, sr = sf.read(str(path), always_2d=True)
    changed = False
    if sr != SR:  # pragma: no cover
        import librosa
        audio = librosa.resample(audio.T, orig_sr=sr, target_sr=SR).T
        sr = SR
        changed = True
    if audio.shape[1] == 1:
        audio = np.concatenate([audio, audio], axis=1)
        changed = True
    # trim/pad to exactly 8 s
    target = int(DURATION_S * SR)
    if audio.shape[0] < target:
        pad = np.zeros((target - audio.shape[0], audio.shape[1]), dtype=audio.dtype)
        audio = np.concatenate([audio, pad], axis=0)
        changed = True
    elif audio.shape[0] > target:
        audio = audio[:target]
        changed = True
    if changed:
        sf.write(str(path), audio, SR, subtype="PCM_16")


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    mid = OUT / "test.mid"
    sfz = OUT / "test.sfz"
    saw = OUT / "test_saw.wav"
    fluid = OUT / "fluid_render.wav"
    sfizz_out = OUT / "sfizz_render.wav"

    build_midi(mid)
    build_saw(saw)
    build_sfz(sfz, saw.name)
    (OUT / "test_midi_sha.txt").write_text(sha256(mid) + "  " + mid.name + "\n")

    render_fluidsynth(mid, fluid)
    render_sfizz(sfz, mid, sfizz_out)

    ensure_stereo_48k(fluid)
    ensure_stereo_48k(sfizz_out)

    for p in (fluid, sfizz_out):
        info = sf.info(str(p))
        print(f"  {p.name}: sr={info.samplerate} ch={info.channels} frames={info.frames}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
