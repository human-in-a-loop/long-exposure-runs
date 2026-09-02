#!/usr/bin/env /usr/bin/python3
# RC10 Branch A A/B pair rendering: candidate MIDI → fluidsynth WAV → LUFS-I -23 normalization.
# created: 2026-09-02, cycle 54, run-2026-08-28T040704Z, worker, fork bdd7bb47f1b5 clone-0
import subprocess
import tempfile
from pathlib import Path
import numpy as np
import soundfile as sf
import pretty_midi
import pyloudnorm as pln

from ._common import SF2


def notes_to_midi(notes, kind, path):
    """Write a MIDI file. drums → channel 10 (ch=9 in pm indexing); bass → prog 33."""
    pm = pretty_midi.PrettyMIDI()
    if kind == "drums":
        inst = pretty_midi.Instrument(program=0, is_drum=True, name="Drums")
    else:
        inst = pretty_midi.Instrument(program=33, is_drum=False, name="Bass")  # electric bass finger
    for n in notes:
        start = float(n["onset_s"])
        end = start + max(0.02, float(n["duration_s"]))
        inst.notes.append(pretty_midi.Note(
            velocity=int(n["velocity"]),
            pitch=int(n["pitch"]),
            start=start,
            end=end,
        ))
    pm.instruments.append(inst)
    pm.write(str(path))


def fluidsynth_render(midi_path, wav_out, sr=44100):
    """Render MIDI to WAV via fluidsynth CLI. Deterministic given identical env."""
    cmd = [
        "/usr/bin/fluidsynth", "-a", "file", "-F", str(wav_out),
        "-r", str(sr), "-g", "0.5", "-q", "-i",
        str(SF2), str(midi_path),
    ]
    subprocess.run(cmd, check=True, capture_output=True, timeout=300)


def loudness_normalize(y, sr, target_lufs=-23.0):
    """LUFS-I normalize a mono/stereo array."""
    if y.ndim == 1:
        yy = y.astype(np.float32).reshape(-1, 1)
    else:
        yy = y.astype(np.float32)
    meter = pln.Meter(sr)
    loudness = meter.integrated_loudness(yy)
    if not np.isfinite(loudness):
        return y.astype(np.float32), None
    gain_db = target_lufs - loudness
    gain = 10 ** (gain_db / 20.0)
    out = (y.astype(np.float32) * gain).astype(np.float32)
    peak = float(np.max(np.abs(out)) or 1.0)
    if peak > 0.98:
        out = out * (0.98 / peak)
    return out, float(loudness)


def write_ab_pair(y_original, sr, notes, kind, out_dir):
    """Write LUFS-normalized original.wav + rendered.wav (from candidate MIDI)."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    # Original
    y_orig_norm, lo = loudness_normalize(y_original, sr)
    sf.write(str(out_dir / "original.wav"), y_orig_norm, sr, subtype="PCM_16")
    # Rendered
    midi_p = out_dir / "candidate.mid"
    wav_p = out_dir / "_render_raw.wav"
    notes_to_midi(notes, kind, midi_p)
    try:
        fluidsynth_render(midi_p, wav_p, sr=sr)
        yr, srr = sf.read(str(wav_p))
        if yr.ndim == 2:
            yr = yr.mean(axis=1)
        yr_norm, lr = loudness_normalize(yr, srr)
        sf.write(str(out_dir / "rendered.wav"), yr_norm, srr, subtype="PCM_16")
        wav_p.unlink()
        return {"orig_lufs": lo, "rendered_lufs": lr, "ok": True}
    except Exception as e:
        return {"orig_lufs": lo, "rendered_lufs": None, "ok": False, "error": str(e)}
