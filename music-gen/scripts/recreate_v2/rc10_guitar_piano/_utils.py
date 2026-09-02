#!/usr/bin/python3
# c53 clone-1 RC10 Branch B — shared utilities.
# NO PRNG. /usr/bin/python3 guard. c48 env flags default OFF.
"""Shared utilities for RC10 guitar+piano candidate matrix.

Provides:
  * env_pins():                canonical env dict for byte-determinism
  * load_stem(path, sr):       mono float32 signal + native sr
  * slice_section(sig, sr, t0, t1)
  * beat_grid(mix_section, sr, start_bpm)
  * chroma_cqt_beat_sync(sig, sr, beats)
  * chroma_cosine_per_beat(orig_beat, rend_beat) -> (mean, median)
  * note_density_ratio(rendered_notes, original_stem_sig, sr, beats)
  * d4_postprocess(notes, sr, bpm, beat_times, orig_sig, freq_lo_hz, freq_hi_hz)
  * pmidi_from_notes(notes, program) -> pretty_midi.PrettyMIDI
  * chord_track_from_chroma(chroma_beat, beats, bpm, program) -> pretty_midi.PrettyMIDI
  * loudness_normalize(sig, sr, target_lufs) -> normalized sig
  * write_wav(path, sig, sr)                 (deterministic 24-bit PCM)
  * midi_notes(pm)                            (extract notes as list of dicts)
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Iterable

# c48 env-var flags default OFF.
os.environ.setdefault("MUSICGEN_LEDGER_SUBSTANTIVE_EXEMPTION", "0")
os.environ.setdefault("MUSICGEN_LEDGER_SUPERSEDES_IN_HASH", "0")

# Byte-determinism pins.
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("PYTHONHASHSEED", "0")
os.environ.setdefault("SOURCE_DATE_EPOCH", "1756463424")
os.environ.setdefault("TZ", "UTC")
os.environ.setdefault("LC_ALL", "C.UTF-8")

if sys.executable != "/usr/bin/python3":
    raise RuntimeError(f"rc10 requires /usr/bin/python3 (got {sys.executable})")

import numpy as np  # noqa: E402
import soundfile as sf  # noqa: E402
import librosa  # noqa: E402
import pretty_midi  # noqa: E402
import pyloudnorm as pyln  # noqa: E402

SR = 22050
HOP = 512
CHROMA_HOP = 512

# 24 major/minor triad templates (Krumhansl-flavored simple binary masks).
_MAJ = np.array([1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0], dtype=np.float32)
_MIN = np.array([1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0], dtype=np.float32)
_TRIAD_TEMPLATES = np.stack(
    [np.roll(_MAJ, i) for i in range(12)]
    + [np.roll(_MIN, i) for i in range(12)],
    axis=0,
)  # shape (24, 12)
_TRIAD_NAMES = [f"maj_{i}" for i in range(12)] + [f"min_{i}" for i in range(12)]

# Triad → pitch classes (root, third, fifth) in 0..11.
_TRIAD_PCS = np.array(
    [[i, (i + 4) % 12, (i + 7) % 12] for i in range(12)]  # major
    + [[i, (i + 3) % 12, (i + 7) % 12] for i in range(12)]  # minor
)


def env_pins() -> dict:
    return {
        "PYTHONHASHSEED": os.environ["PYTHONHASHSEED"],
        "SOURCE_DATE_EPOCH": os.environ["SOURCE_DATE_EPOCH"],
        "TZ": os.environ["TZ"],
        "LC_ALL": os.environ["LC_ALL"],
        "OPENBLAS_NUM_THREADS": os.environ["OPENBLAS_NUM_THREADS"],
        "MKL_NUM_THREADS": os.environ["MKL_NUM_THREADS"],
        "OMP_NUM_THREADS": os.environ["OMP_NUM_THREADS"],
    }


def load_stem(path: Path, sr: int = SR) -> np.ndarray:
    """Load WAV as mono float32 at target sr."""
    sig, native_sr = sf.read(str(path), dtype="float32", always_2d=False)
    if sig.ndim == 2:
        sig = sig.mean(axis=1).astype(np.float32)
    if native_sr != sr:
        sig = librosa.resample(sig, orig_sr=native_sr, target_sr=sr)
    return sig.astype(np.float32)


def slice_section(sig: np.ndarray, sr: int, t0: float, t1: float) -> np.ndarray:
    i0 = max(0, int(round(t0 * sr)))
    i1 = min(len(sig), int(round(t1 * sr)))
    return sig[i0:i1]


def beat_grid(mix_section: np.ndarray, sr: int, start_bpm: float) -> tuple[float, np.ndarray]:
    """Return (estimated_bpm, beat_times_seconds) using librosa.beat.beat_track.

    Deterministic under BLAS pins. `mix_section` is the ORIGINAL mixdown of
    the chosen section (identical grid for both signals so per-beat aggregation
    is comparable).
    """
    tempo, beat_frames = librosa.beat.beat_track(
        y=mix_section,
        sr=sr,
        hop_length=HOP,
        start_bpm=float(start_bpm),
        tightness=100,
        trim=False,
    )
    beat_times = librosa.frames_to_time(beat_frames, sr=sr, hop_length=HOP)
    # tempo may be np.array of shape (1,) in newer librosa versions.
    if hasattr(tempo, "item"):
        try:
            tempo = float(tempo)
        except (TypeError, ValueError):
            tempo = float(np.asarray(tempo).flat[0])
    return float(tempo), np.asarray(beat_times, dtype=np.float64)


def chroma_cqt_beat_sync(sig: np.ndarray, sr: int, beat_times: np.ndarray) -> np.ndarray:
    """Return per-beat chroma (12 × n_beats), mean-aggregated over beat spans."""
    chroma = librosa.feature.chroma_cqt(y=sig, sr=sr, hop_length=CHROMA_HOP)
    beat_frames = librosa.time_to_frames(beat_times, sr=sr, hop_length=CHROMA_HOP)
    beat_frames = np.clip(beat_frames, 0, chroma.shape[1] - 1)
    if beat_frames.size < 2:
        # Degenerate — return raw chroma mean.
        return chroma.mean(axis=1, keepdims=True)
    beat_chroma = librosa.util.sync(chroma, beat_frames, aggregate=np.mean)
    return np.asarray(beat_chroma, dtype=np.float32)


def chroma_cosine_per_beat(orig_beat: np.ndarray, rend_beat: np.ndarray) -> tuple[float, float]:
    """Cosine per beat; return (mean, median) over non-degenerate beats."""
    n = min(orig_beat.shape[1], rend_beat.shape[1])
    a = orig_beat[:, :n]
    b = rend_beat[:, :n]
    na = np.linalg.norm(a, axis=0)
    nb = np.linalg.norm(b, axis=0)
    ok = (na > 1e-9) & (nb > 1e-9)
    if not ok.any():
        return 0.0, 0.0
    cos = np.sum(a[:, ok] * b[:, ok], axis=0) / (na[ok] * nb[ok] + 1e-12)
    # Clip to [0, 1] to guard against float32 rounding above 1.0 exactly.
    cos = np.clip(cos, 0.0, 1.0)
    return float(np.mean(cos)), float(np.median(cos))


def onsets_in_section(sig: np.ndarray, sr: int) -> int:
    onsets = librosa.onset.onset_detect(
        y=sig, sr=sr, hop_length=HOP, backtrack=False, units="frames"
    )
    return int(len(onsets))


def note_density_ratio(
    rendered_notes: list[dict],
    original_stem_section: np.ndarray,
    sr: int,
    n_beats: int,
) -> float:
    if n_beats <= 0:
        return 0.0
    orig_onsets = onsets_in_section(original_stem_section, sr)
    orig_per_beat = orig_onsets / max(1, n_beats)
    rend_per_beat = len(rendered_notes) / max(1, n_beats)
    if orig_per_beat <= 1e-9:
        # If original has effectively zero onsets, ratio is degenerate; return
        # rend_per_beat directly (falls outside [0.5, 2.0] pass band unless
        # rendered is also near-zero).
        return float(rend_per_beat) if rend_per_beat > 1e-6 else 1.0
    return float(rend_per_beat / orig_per_beat)


def d4_postprocess(
    notes: list[dict],
    sr: int,
    bpm: float,
    beat_times: np.ndarray,
    orig_sig: np.ndarray,
    freq_lo_hz: float,
    freq_hi_hz: float,
    beat_snap_tolerance_s: float = 0.050,
) -> tuple[list[dict], dict]:
    """Apply D4 post-processing. Returns (filtered_notes, diagnostic_counts).

    Steps:
      1. snap onsets to beat grid within ±50ms.
      2. drop notes with duration < 60/(bpm*8) s.
      3. derive velocity from stem RMS envelope in note window.
      4. range-filter pitches outside [freq_lo_hz, freq_hi_hz].
    """
    diag = {"n_in": len(notes), "n_snap": 0, "n_short_drop": 0, "n_range_drop": 0}
    if not notes:
        diag["n_out"] = 0
        return [], diag

    min_dur_s = 60.0 / max(1e-6, bpm * 8.0)
    # RMS envelope (hop=512).
    rms_env = librosa.feature.rms(y=orig_sig, hop_length=HOP)[0]
    rms_max = float(rms_env.max() + 1e-9)
    rms_min = float(rms_env.min())
    span = max(1e-9, rms_max - rms_min)

    # Beat times as np array for snap.
    bts = beat_times

    out: list[dict] = []
    for n in notes:
        pitch = int(n["pitch"])
        s = float(n["onset_s"])
        e = float(n["offset_s"])
        # 1. Snap.
        if len(bts) > 0:
            idx = int(np.argmin(np.abs(bts - s)))
            if abs(bts[idx] - s) <= beat_snap_tolerance_s:
                shift = float(bts[idx] - s)
                s = float(bts[idx])
                e = e + shift
                diag["n_snap"] += 1
        # 2. Drop short.
        if (e - s) < min_dur_s:
            diag["n_short_drop"] += 1
            continue
        # 3. Velocity from RMS envelope in [s, e).
        i0 = max(0, int(round(s * sr / HOP)))
        i1 = min(len(rms_env), int(round(e * sr / HOP)) + 1)
        if i1 <= i0:
            local_rms = float(rms_env[min(i0, len(rms_env) - 1)])
        else:
            local_rms = float(rms_env[i0:i1].mean())
        vel_norm = (local_rms - rms_min) / span  # in [0,1]
        vel = int(round(1 + vel_norm * 126))
        vel = max(1, min(127, vel))
        # 4. Range-filter.
        f_hz = 440.0 * (2.0 ** ((pitch - 69) / 12.0))
        if f_hz < freq_lo_hz or f_hz > freq_hi_hz:
            diag["n_range_drop"] += 1
            continue
        out.append({
            "pitch": pitch,
            "onset_s": round(s, 6),
            "offset_s": round(e, 6),
            "velocity": vel,
        })
    diag["n_out"] = len(out)
    out.sort(key=lambda r: (r["onset_s"], r["pitch"]))
    return out, diag


def pmidi_from_notes(notes: list[dict], program: int, is_drum: bool = False) -> pretty_midi.PrettyMIDI:
    """Emit a pretty_midi with a single Instrument on the given GM program."""
    pm = pretty_midi.PrettyMIDI(initial_tempo=120.0)
    inst = pretty_midi.Instrument(program=int(program), is_drum=bool(is_drum))
    for n in notes:
        inst.notes.append(pretty_midi.Note(
            velocity=int(n.get("velocity", 80)),
            pitch=int(n["pitch"]),
            start=float(n["onset_s"]),
            end=float(n["offset_s"]),
        ))
    pm.instruments.append(inst)
    return pm


def midi_notes(pm: pretty_midi.PrettyMIDI) -> list[dict]:
    out = []
    for inst in pm.instruments:
        if inst.is_drum:
            continue
        for note in inst.notes:
            out.append({
                "pitch": int(note.pitch),
                "onset_s": float(note.start),
                "offset_s": float(note.end),
                "velocity": int(note.velocity),
            })
    out.sort(key=lambda r: (r["onset_s"], r["pitch"]))
    return out


def chord_track_from_chroma(
    chroma_beat: np.ndarray,
    beat_times: np.ndarray,
    program: int,
    section_end_s: float,
    octave: int = 4,
) -> pretty_midi.PrettyMIDI:
    """Beat-sync chroma → 24-triad template match → sustained triads on beat grid.

    Renders as `pretty_midi` with the given GM `program`.
    """
    pm = pretty_midi.PrettyMIDI(initial_tempo=120.0)
    inst = pretty_midi.Instrument(program=int(program))
    n_beats = min(chroma_beat.shape[1], len(beat_times))
    if n_beats < 1:
        pm.instruments.append(inst)
        return pm
    # For each beat, pick best-matching triad by cosine.
    for b in range(n_beats):
        vec = chroma_beat[:, b].astype(np.float32)
        n = float(np.linalg.norm(vec))
        if n < 1e-9:
            continue
        scores = _TRIAD_TEMPLATES @ vec
        tri_idx = int(np.argmax(scores))
        pcs = _TRIAD_PCS[tri_idx]
        t_start = float(beat_times[b])
        t_end = float(beat_times[b + 1]) if b + 1 < n_beats else float(min(
            section_end_s, t_start + (beat_times[b] - beat_times[b - 1]) if b > 0 else t_start + 0.5
        ))
        if t_end <= t_start:
            t_end = t_start + 0.25
        for pc in pcs:
            pitch = int(pc) + 12 * octave  # e.g. octave=4 → 48..59 for base C4
            inst.notes.append(pretty_midi.Note(
                velocity=80,
                pitch=int(pitch),
                start=t_start,
                end=t_end,
            ))
    pm.instruments.append(inst)
    return pm


def loudness_normalize(sig: np.ndarray, sr: int, target_lufs: float = -23.0) -> np.ndarray:
    """LUFS-I normalize a mono signal to target_lufs. Returns float32 signal."""
    if len(sig) < int(0.5 * sr):
        # Too short for BS.1770 400ms window; return unchanged.
        return sig.astype(np.float32)
    # pyloudnorm needs 2D for stereo, 1D for mono is fine on Meter.
    meter = pyln.Meter(sr)
    try:
        current = meter.integrated_loudness(sig.astype(np.float32))
    except Exception:
        return sig.astype(np.float32)
    if not np.isfinite(current):
        return sig.astype(np.float32)
    gain_db = target_lufs - current
    gain = 10.0 ** (gain_db / 20.0)
    out = (sig * gain).astype(np.float32)
    # Prevent hard clip.
    peak = float(np.max(np.abs(out)) + 1e-12)
    if peak > 0.99:
        out = (out * (0.99 / peak)).astype(np.float32)
    return out


def write_wav(path: Path, sig: np.ndarray, sr: int) -> None:
    """Write deterministic PCM_24 mono WAV."""
    path.parent.mkdir(parents=True, exist_ok=True)
    sf.write(str(path), sig.astype(np.float32), int(sr), subtype="PCM_24")


def render_notes_to_wav(pm: pretty_midi.PrettyMIDI, sr: int, section_end_s: float) -> np.ndarray:
    """Synthesize a PrettyMIDI to mono float32 audio via `pm.synthesize`.

    pretty_midi's built-in sine synthesizer is deterministic under fixed input;
    audio quality is not the gate here — chroma/density is.
    """
    if not pm.instruments or not any(inst.notes for inst in pm.instruments):
        return np.zeros(int(round(section_end_s * sr)), dtype=np.float32)
    audio = pm.synthesize(fs=sr)
    audio = np.asarray(audio, dtype=np.float32)
    # Pad or trim to section_end_s.
    want = int(round(section_end_s * sr))
    if len(audio) < want:
        audio = np.concatenate([audio, np.zeros(want - len(audio), dtype=np.float32)])
    else:
        audio = audio[:want]
    # Guard against clipping.
    peak = float(np.max(np.abs(audio)) + 1e-12)
    if peak > 0.99:
        audio = (audio * (0.99 / peak)).astype(np.float32)
    return audio


def sha256_file(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def canonical_json_bytes(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")
