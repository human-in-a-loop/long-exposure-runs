#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-09-03T00:00:00Z
# cycle: 6
# run_id: run-2026-09-03T000000Z
# agent: worker
# milestone: M-V4-PROFILES-1/cg-bass-family2-stem-sampled
# ---
"""Deterministic replayer for family=stem_sampled_v1 profiles.

Pure function of the profile identity fields + the source MIDI. Reads the
reference stem WAV, extracts a stable slice, pitch-shifts + windows +
sums per MIDI note, LUFS-I normalizes.

Distinct RENDER FAMILY from sf2 (FD-16c). Do NOT extend
scripts/sound_match/replay.py — that module is sf2/sfz-dispatched.
"""
from __future__ import annotations

import hashlib
import os
import sys
from pathlib import Path
from typing import Mapping

# Env pin BEFORE any observed import (numpy/librosa/soundfile)
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

if sys.executable != "/usr/bin/python3":  # pragma: no cover
    raise RuntimeError(f"replay_family2 requires /usr/bin/python3 (got {sys.executable})")

import numpy as np  # noqa: E402
import soundfile as sf  # noqa: E402
import librosa  # noqa: E402
import mido  # noqa: E402


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def _adsr_lite(n: int, sr: int) -> np.ndarray:
    env = np.ones(n, dtype=np.float32)
    edge = max(1, int(0.005 * sr))
    if 2 * edge < n:
        env[:edge] = np.linspace(0.0, 1.0, edge, dtype=np.float32)
        env[-edge:] = np.linspace(1.0, 0.0, edge, dtype=np.float32)
    return env


def _lufs_normalize(y: np.ndarray, sr: int, target_db: float) -> tuple[np.ndarray, str, float]:
    try:
        import pyloudnorm as pyln
        meter = pyln.Meter(sr)
        measured = float(meter.integrated_loudness(y))
        if not np.isfinite(measured):
            raise ValueError("non-finite LUFS")
        gain_db = target_db - measured
        return (y * (10.0 ** (gain_db / 20.0))).astype(np.float32), "pyloudnorm", measured
    except Exception:
        rms = float(np.sqrt(np.mean(y.astype(np.float64) ** 2)) + 1e-12)
        rms_db = 20.0 * np.log10(rms)
        gain_db = target_db - rms_db
        return (y * (10.0 ** (gain_db / 20.0))).astype(np.float32), "rms_fallback", rms_db


def _extract_notes(midi_path: Path) -> list[tuple[float, int, float]]:
    """Return [(onset_s, pitch, duration_s), ...] sorted by onset."""
    mid = mido.MidiFile(str(midi_path))
    tempo = 500000
    tick = 0
    open_notes: dict[int, float] = {}
    events: list[tuple[float, int, float]] = []
    for msg in mido.merge_tracks(mid.tracks):
        tick += msg.time
        if msg.type == "set_tempo":
            tempo = msg.tempo
        elif msg.type == "note_on" and msg.velocity > 0:
            open_notes[msg.note] = mido.tick2second(tick, mid.ticks_per_beat, tempo)
        elif msg.type == "note_off" or (msg.type == "note_on" and msg.velocity == 0):
            if msg.note in open_notes:
                t_on = open_notes.pop(msg.note)
                t_off = mido.tick2second(tick, mid.ticks_per_beat, tempo)
                events.append((t_on, msg.note, max(0.05, t_off - t_on)))
    events.sort()
    return events


def replay_family2(profile: Mapping, midi_path: Path, out_wav_path: Path) -> str:
    """Render midi via profile → out_wav_path; return sha256 of output."""
    assert profile.get("render_family") == "stem_sampled_v1", (
        f"replay_family2 only handles stem_sampled_v1, got {profile.get('render_family')}"
    )
    ident = profile["identity"]
    stem_path = Path(ident["stem_source_path"])
    expected_stem_sha = ident["stem_source_sha256"]
    actual_stem_sha = _sha256(stem_path)
    assert actual_stem_sha == expected_stem_sha, (
        f"stem SHA drift: expected {expected_stem_sha} got {actual_stem_sha}"
    )

    slice_start_s = float(ident["stem_slice_start_s"])
    slice_len_s = float(ident["stem_slice_len_s"])
    stem_f0_hz = float(ident["stem_f0_hz"])
    lufs_target_db = float(ident["post"]["lufs_target_db"])
    gain = float(ident.get("gain", 1.0))

    stem, sr = librosa.load(str(stem_path), sr=None, mono=True)

    slice_i0 = int(slice_start_s * sr)
    slice_i1 = slice_i0 + int(slice_len_s * sr)
    slice_i1 = min(slice_i1, stem.size)
    stem_slice = stem[slice_i0:slice_i1].astype(np.float32)
    if stem_slice.size < int(slice_len_s * sr):
        stem_slice = np.pad(stem_slice, (0, int(slice_len_s * sr) - stem_slice.size))

    events = _extract_notes(midi_path)
    if not events:
        y = np.zeros(int(sr * 0.1), dtype=np.float32)
    else:
        total_s = max(e[0] + e[2] for e in events) + 0.2
        n_out = int(total_s * sr)
        y = np.zeros(n_out, dtype=np.float32)
        for onset_s, pitch, dur_s in events:
            target_hz = float(librosa.midi_to_hz(pitch))
            n_steps = 12.0 * np.log2(target_hz / stem_f0_hz)
            shifted = librosa.effects.pitch_shift(stem_slice, sr=sr, n_steps=n_steps)
            dur_n = int(dur_s * sr)
            if shifted.size < dur_n:
                shifted = np.pad(shifted, (0, dur_n - shifted.size))
            else:
                shifted = shifted[:dur_n]
            env = _adsr_lite(dur_n, sr)
            windowed = (shifted * env * gain).astype(np.float32)
            idx0 = int(onset_s * sr)
            idx1 = idx0 + dur_n
            if idx1 > n_out:
                windowed = windowed[: n_out - idx0]
                idx1 = n_out
            y[idx0:idx1] += windowed

        peak = float(np.max(np.abs(y))) + 1e-12
        if peak > 1.0:
            y = (y / peak).astype(np.float32)

        y, _method, _measured = _lufs_normalize(y, sr, lufs_target_db)

    out_wav_path = Path(out_wav_path)
    out_wav_path.parent.mkdir(parents=True, exist_ok=True)
    sf.write(str(out_wav_path), y, sr, subtype="PCM_16")
    return _sha256(out_wav_path)
