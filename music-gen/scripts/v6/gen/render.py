#!/usr/bin/python3
"""v6 Phase 2 — thin audio render: per-stem sf2 replay (scripts.sound_match.replay, READ-ONLY) + the v5 RMS/mix helpers.

created: 2026-10-04
milestone: M-V6-GEN-2/theory-grounded-composer

generate_v5's helpers (write_wav_int16, rms_norm, the float-accumulate + 0.99 peak-limit mix) are re-implemented here
(~40 lines) because importing scripts/v5/generate_v5.py chdir()s the process and pulls the whole v5 generator in at import.
Profiles: FluidR3_GM shims — bass program 33 (Fingered Bass), keys 4 (Electric Piano 1), melody 11 (Vibraphone), drums
bank 128 program 0 (Standard Kit; channel 10 selects the drum bank under fluidsynth's GS mode). RMS targets -18 dBFS for
bass/drums, -22 dBFS for keys/melody; gain clipped to [0.05, 4]; 16-bit stereo PCM via stdlib wave. Deterministic.
"""
from __future__ import annotations

import struct
import wave
from pathlib import Path

import numpy as np
import soundfile as sf

from scripts.v6.gen.common import sha_file

SF2_PATH = "/usr/share/sounds/sf2/FluidR3_GM.sf2"
SF2_SHA256 = "74594e8f4250680adf590507a306655a299935343583256f3b722c48a1bc1cb0"
PROGRAMS = {"bass": {"bank": 0, "program": 33, "name": "GM Fingered Bass (shim)"}, "keys": {"bank": 0, "program": 4, "name": "GM Electric Piano 1 (shim)"},
            "melody": {"bank": 0, "program": 11, "name": "GM Vibraphone (shim)"}, "drums": {"bank": 128, "program": 0, "name": "GM Standard Kit (shim)"}}
TARGET_RMS_DB = {"bass": -18.0, "drums": -18.0, "keys": -22.0, "melody": -22.0}
SR = 44100


def profile(stem: str, sf2_path: str = SF2_PATH, sf2_sha: str = SF2_SHA256) -> dict:
    p = PROGRAMS[stem]
    return {"family": "sf2", "identity": {"sf2_path": sf2_path, "sf2_sha256": sf2_sha, "bank": p["bank"], "program": p["program"]},
            "params": {"sample_rate": SR, "gain": 0.8}, "note": p["name"]}


def write_wav_int16(path: Path, data: np.ndarray, sr: int) -> None:
    a = np.asarray(data, dtype=np.float32)
    if a.ndim == 1:
        a = np.stack([a, a], axis=-1)
    a = np.clip(a, -1.0, 1.0)
    ai = np.round(a * 32767.0).astype(np.int16)
    raw = struct.pack("<" + "h" * ai.size, *ai.reshape(-1).tolist())
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(raw)


def rms_norm(wav: Path, target_db: float) -> tuple:
    data, sr = sf.read(str(wav), dtype="float32", always_2d=True)
    cur = float(np.sqrt((data.astype(np.float64) ** 2).mean())) if data.size else 0.0
    gain = (10 ** (target_db / 20.0)) / cur if cur > 1e-9 else 1.0
    gain = max(0.05, min(4.0, gain))
    return data * gain, sr, gain


def render_mix(midi_paths: dict, out_wav: Path, per_track_dir: Path, song_len_s: float, keep_per_track: bool = False, sf2_path: str = SF2_PATH) -> dict:
    """midi_paths = {stem: Path}; stems with no MIDI (empty) render as silence. Returns the manifest block."""
    from scripts.sound_match.replay import replay as sf2_replay  # READ-ONLY (requires /usr/bin/python3)
    per_track_dir.mkdir(parents=True, exist_ok=True)
    sf2_sha = sha_file(Path(sf2_path)) if Path(sf2_path).exists() else ""
    tracks, info = [], {"per_track_wav_sha256": {}, "gains": {}, "profiles": {}}
    sr = SR
    for stem in ("drums", "bass", "keys", "melody"):
        wav = per_track_dir / f"{stem}.wav"
        prof = profile(stem, sf2_path, sf2_sha)
        info["profiles"][stem] = prof
        if midi_paths.get(stem) is None:
            write_wav_int16(wav, np.zeros((int(SR * song_len_s), 2), dtype=np.float32), SR)
        else:
            sf2_replay(prof, str(midi_paths[stem]), str(wav))
        info["per_track_wav_sha256"][stem] = sha_file(wav)
        data, sr, g = rms_norm(wav, TARGET_RMS_DB[stem])
        info["gains"][stem] = round(g, 6)
        tracks.append(data)
    max_len = max(t.shape[0] for t in tracks)
    acc = np.zeros((max_len, 2), dtype=np.float64)
    for t in tracks:
        acc[: t.shape[0], :] += t.astype(np.float64)
    peak = float(np.abs(acc).max())
    if peak > 0.99:
        acc *= 0.99 / peak
    mix = acc.astype(np.float32)
    write_wav_int16(out_wav, mix, sr)
    deleted = []
    if not keep_per_track:
        for p in sorted(per_track_dir.glob("*")):
            deleted.append(p.name)
            p.unlink()
    info.update({"ab_mix_sha256": sha_file(out_wav), "ab_mix_duration_s": round(len(mix) / sr, 4), "sample_rate": sr, "peak_before_limit": round(peak, 6),
                 "target_rms_dbfs": TARGET_RMS_DB, "sum_method": "float_accumulate_peaklimit_099_max_len_zero_pad", "per_track_deleted_after_mix": deleted,
                 "sf2_path": sf2_path, "sf2_sha256": sf2_sha})
    return info
