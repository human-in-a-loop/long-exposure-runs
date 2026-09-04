#!/usr/bin/python3
# ------------------------------------------------------------------
# c15 Track 2 primary: CG guitar family-2 stem-sampled builder.
#
# Sibling to c5/c6 family2_stem_sampled_builder.py (bass; READ-ONLY)
# and c12 family2_stem_sampled_drums_builder.py (drums; READ-ONLY).
# Guitar-specific per the c15 research brief:
#
#   * Onset detect on guitar stem via librosa.onset.onset_detect
#     (units='samples', backtrack=True).
#   * Fixed 400 ms slices per onset (matches drums c12 shape).
#   * Guitar IS pitched — sample bank indexed by MIDI pitch derived
#     via librosa.pyin median per slice (matches bass c5/c6
#     pitch-shift path).
#   * At render time, for the k-th occurrence of MIDI pitch P, use
#     bank[Q][k % len(bank[Q])] where Q = nearest available pitch;
#     pitch-shift by (P - Q) semitones via librosa.effects.pitch_shift.
#   * Deterministic (no PRNG); splice at note onset; soft peak-limit
#     0.99.
#   * Output 44.1 kHz mono to match reference stem.
#
# Public API:
#     render(ref_stem_path: Path, midi_path: Path, out_wav: Path,
#            *, window_ms: int = 400) -> dict
#
# Family-2 IS a distinct RENDER FAMILY from sf2 per FD-16(c) — needs
# its own per-song replay proof (double-run byte-determinism).
#
# created: 2026-09-04
# cycle: 15
# run_id: run-2026-09-04T100000Z
# agent: worker
# milestone: M-V4-PROFILES-1/cg-guitar-family2-stem-sampled
# ------------------------------------------------------------------

from __future__ import annotations

import hashlib
import json
import os
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Tuple

# Env pins (7-key canonical) applied at import time for determinism.
for _k, _v in {
    "PYTHONHASHSEED": "0",
    "SOURCE_DATE_EPOCH": "1756463424",
    "TZ": "UTC",
    "LC_ALL": "C.UTF-8",
    "OMP_NUM_THREADS": "1",
    "MKL_NUM_THREADS": "1",
    "OPENBLAS_NUM_THREADS": "1",
}.items():
    os.environ.setdefault(_k, _v)

import librosa  # noqa: E402
import mido  # noqa: E402
import numpy as np  # noqa: E402
import soundfile as sf  # noqa: E402

_WORKSPACE = Path(__file__).resolve().parents[2]

# Min voicing confidence for accepting a pyin pitch estimate.
_VOICING_MIN = 0.5
# Guitar-range pyin bounds (E1..E7 covers 6-string range with margin).
_PYIN_FMIN = 41.0
_PYIN_FMAX = 2637.0


def _sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def _to_mono(y: np.ndarray) -> np.ndarray:
    if y.ndim == 1:
        return y
    return y.mean(axis=0)


def _hz_to_midi_int(hz: float) -> int:
    # Round to nearest MIDI semitone; librosa.hz_to_midi returns float.
    return int(round(float(librosa.hz_to_midi(hz))))


def build_sample_bank(
    ref_stem_path: Path, *, window_ms: int = 400,
) -> Tuple[Dict[int, List[np.ndarray]], int, dict]:
    """Extract per-MIDI-pitch sample bank from the reference guitar stem.

    Returns (bank_by_pitch, sr, diagnostics).
    """
    y, sr = librosa.load(str(ref_stem_path), sr=None, mono=False)
    y = _to_mono(y)
    onset_samples = librosa.onset.onset_detect(
        y=y, sr=sr, units="samples", backtrack=True)
    win_n = int(sr * window_ms / 1000)
    bank: Dict[int, List[np.ndarray]] = defaultdict(list)
    n_voiced = 0
    n_unvoiced = 0
    n_too_short = 0
    for s in onset_samples:
        seg = y[int(s):int(s) + win_n]
        if seg.size < win_n // 2:
            n_too_short += 1
            continue
        if seg.size < win_n:
            seg = np.concatenate(
                [seg, np.zeros(win_n - seg.size, dtype=np.float32)])
        seg = seg.astype(np.float32)
        # Pyin over the slice; take median voiced pitch.
        f0, voiced_flag, voiced_prob = librosa.pyin(
            seg, sr=sr, fmin=_PYIN_FMIN, fmax=_PYIN_FMAX)
        voiced_mask = (voiced_flag) & (voiced_prob >= _VOICING_MIN)
        voiced_hz = f0[voiced_mask]
        voiced_hz = voiced_hz[~np.isnan(voiced_hz)]
        if voiced_hz.size == 0:
            n_unvoiced += 1
            continue
        med_hz = float(np.median(voiced_hz))
        midi_p = _hz_to_midi_int(med_hz)
        bank[midi_p].append(seg)
        n_voiced += 1
    diag = {
        "sample_rate": int(sr),
        "duration_s": round(float(len(y)) / sr, 4),
        "n_onsets": int(len(onset_samples)),
        "n_slices_voiced": n_voiced,
        "n_slices_unvoiced_dropped": n_unvoiced,
        "n_slices_too_short_dropped": n_too_short,
        "window_ms": window_ms,
        "pyin_fmin_hz": _PYIN_FMIN,
        "pyin_fmax_hz": _PYIN_FMAX,
        "voicing_min": _VOICING_MIN,
        "n_unique_pitches": len(bank),
    }
    return dict(bank), int(sr), diag


def _midi_note_events(midi_path: Path) -> List[Tuple[float, int, int]]:
    """Return sorted (time_s, pitch, channel) for note_on with vel>0."""
    mid = mido.MidiFile(str(midi_path))
    tempo_us = 500000
    ticks_per_beat = mid.ticks_per_beat
    events: List[Tuple[float, int, int]] = []
    for track in mid.tracks:
        now_ticks = 0
        for msg in track:
            now_ticks += msg.time
            if msg.type == "set_tempo":
                tempo_us = msg.tempo
            elif msg.type == "note_on" and msg.velocity > 0:
                t_s = mido.tick2second(
                    now_ticks, ticks_per_beat, tempo_us)
                events.append((t_s, msg.note, msg.channel))
    events.sort(key=lambda e: (e[0], e[1]))
    return events


def _nearest_bank_pitch(target: int, available: List[int]) -> int:
    # Deterministic: on ties (equal absolute distance), prefer lower
    # pitch so sort order is total.  available is guaranteed non-empty.
    return min(available, key=lambda q: (abs(q - target), q))


def render(
    ref_stem_path: Path,
    midi_path: Path,
    out_wav: Path,
    *,
    window_ms: int = 400,
) -> dict:
    """Concatenative render with per-pitch bank + pitch-shift.

    Deterministic selection: for the k-th occurrence of MIDI pitch P
    routed to bank pitch Q, use bank[Q][k % len(bank[Q])].  No PRNG.
    """
    bank, sr, diag = build_sample_bank(ref_stem_path, window_ms=window_ms)
    if not bank:
        raise RuntimeError(
            "empty sample bank — reference stem produced no voiced "
            "slices; family-2 stem-sampled cannot render.")
    events = _midi_note_events(midi_path)
    win_n = int(sr * window_ms / 1000)
    max_event_end = max(
        (int(t * sr) + win_n for t, _, _ in events), default=0)
    out_n = max(max_event_end, int(diag["duration_s"] * sr))
    out = np.zeros(out_n, dtype=np.float32)

    available_pitches = sorted(bank.keys())
    per_bucket_k: Counter = Counter()
    per_target_pitch_uses: Counter = Counter()
    n_events_routed = 0

    for t_s, pitch, _ch in events:
        q = _nearest_bank_pitch(pitch, available_pitches)
        k = per_bucket_k[q]
        per_bucket_k[q] += 1
        per_target_pitch_uses[pitch] += 1
        seg = bank[q][k % len(bank[q])]
        semitone_delta = pitch - q
        if semitone_delta != 0:
            seg = librosa.effects.pitch_shift(
                seg, sr=sr, n_steps=float(semitone_delta))
        pos = int(t_s * sr)
        end = pos + seg.size
        if end > out.size:
            new_out = np.zeros(end, dtype=np.float32)
            new_out[: out.size] = out
            out = new_out
        out[pos:end] += seg.astype(np.float32)
        n_events_routed += 1

    peak = float(np.max(np.abs(out))) if out.size else 0.0
    if peak > 0.99:
        out = out * (0.99 / peak)

    out_wav.parent.mkdir(parents=True, exist_ok=True)
    sf.write(str(out_wav), out, sr, subtype="PCM_16")
    render_sha = _sha256_file(out_wav)

    return {
        "render_sha256": render_sha,
        "sample_rate": int(sr),
        "output_samples": int(out.size),
        "peak_abs": peak,
        "n_midi_events": len(events),
        "n_events_routed": n_events_routed,
        "per_target_pitch_uses": {
            int(k): int(v) for k, v in per_target_pitch_uses.items()},
        "bank_diagnostics": diag,
    }


def main() -> int:
    ref_stem = (
        _WORKSPACE
        / "data/v3/deliveries/31a164f845f8e27e/cert_run1/stems_6s/guitar.wav"
    )
    midi = (
        _WORKSPACE
        / "data/v4/profiles/31a164f845f8e27e/"
        / "guitar_sweep_stage1/guitar_excerpt.mid"
    )
    out_dir = (
        _WORKSPACE
        / "data/v4/profiles/31a164f845f8e27e/guitar_family2_render"
    )
    out_wav = out_dir / "render.wav"
    r = render(ref_stem, midi, out_wav)
    manifest = {
        "schema_version": "v1.0",
        "milestone_id": (
            "M-V4-PROFILES-1/cg-guitar-family2-stem-sampled/render"),
        "cycle": 15,
        "ref_stem_path": str(ref_stem.relative_to(_WORKSPACE)),
        "ref_stem_sha256": _sha256_file(ref_stem),
        "midi_path": str(midi.relative_to(_WORKSPACE)),
        "midi_sha256": _sha256_file(midi),
        "out_wav_path": str(out_wav.relative_to(_WORKSPACE)),
        **r,
    }
    (out_dir / "render_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(json.dumps(
        {"render_sha256": r["render_sha256"],
         "peak_abs": r["peak_abs"],
         "n_events": r["n_midi_events"],
         "n_events_routed": r["n_events_routed"],
         "bank_diag": r["bank_diagnostics"]},
        indent=2))
    print(f"WROTE {out_wav}")
    print(f"WROTE {out_dir / 'render_manifest.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
