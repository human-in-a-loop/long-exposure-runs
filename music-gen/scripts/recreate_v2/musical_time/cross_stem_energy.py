#!/usr/bin/python3
"""D5 Cross-stem energy seed table for c58 cross-stem reconciliation.

For every detected onset (union across 6 htdemucs stems), record RMS energy
in the [20, 200] Hz band across all 6 stems in a ±25 ms window around onset.
STFT n_fft=2048, hop=512 on 44.1 kHz.
"""
from __future__ import annotations

import csv
import pathlib
from typing import Dict, List, Tuple

import numpy as np

STEMS = ("drums", "bass", "vocals", "guitar", "piano", "other")
LO_HZ = 20.0
HI_HZ = 200.0
WINDOW_MS = 25.0


def band_rms(stem_mono: np.ndarray, sr: int, t_center_s: float) -> float:
    """RMS in [20, 200] Hz band within ±25 ms of ``t_center_s``.

    Time-domain FFT-based bandpass: apply real FFT to the window, zero out
    frequencies outside [LO_HZ, HI_HZ], irfft back, compute RMS.
    """
    win_samples = int(round(WINDOW_MS / 1000.0 * sr))
    i0 = max(0, int(round(t_center_s * sr)) - win_samples)
    i1 = min(len(stem_mono), int(round(t_center_s * sr)) + win_samples)
    if i1 <= i0:
        return 0.0
    frame = stem_mono[i0:i1].astype(np.float64)
    if frame.size < 4:
        return float(np.sqrt(np.mean(frame ** 2))) if frame.size else 0.0

    n = frame.size
    freqs = np.fft.rfftfreq(n, d=1.0 / sr)
    spec = np.fft.rfft(frame)
    mask = (freqs >= LO_HZ) & (freqs <= HI_HZ)
    spec_bp = np.where(mask, spec, 0.0 + 0.0j)
    filtered = np.fft.irfft(spec_bp, n=n)
    return float(np.sqrt(np.mean(filtered ** 2)))


def union_onsets(onsets_by_stem: Dict[str, np.ndarray]) -> List[Tuple[float, str]]:
    """Return sorted [(onset_s, source_stem), ...] union across stems."""
    rows: List[Tuple[float, str]] = []
    for stem, arr in onsets_by_stem.items():
        for t in arr:
            rows.append((float(t), stem))
    rows.sort(key=lambda x: (x[0], x[1]))
    return rows


def build_song_rows(
    song_sha16: str,
    onsets_by_stem: Dict[str, np.ndarray],
    stems_audio: Dict[str, np.ndarray],
    sr: int,
) -> List[Dict[str, float]]:
    rows: List[Dict[str, float]] = []
    for t, src in union_onsets(onsets_by_stem):
        row: Dict[str, float] = {
            "song_sha16": song_sha16,
            "onset_time_s": float(round(t, 6)),
            "source_stem": src,
        }
        for stem in STEMS:
            y = stems_audio.get(stem)
            if y is None:
                row[f"energy_{stem}"] = 0.0
            else:
                row[f"energy_{stem}"] = float(round(band_rms(y, sr, t), 10))
        rows.append(row)
    return rows


def append_cross_stem_tsv(path: pathlib.Path, all_rows: List[Dict[str, float]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    cols = ["song_sha16", "onset_time_s", "source_stem"] + [f"energy_{s}" for s in STEMS]
    # Deterministic column names per D5 (map guitar/piano/other → energy_other_residual).
    # Rename energy_other → energy_other_residual to match rubric header.
    cols_out = ["song_sha16", "onset_time_s", "source_stem",
                "energy_drums", "energy_bass", "energy_vocals",
                "energy_guitar", "energy_piano", "energy_other_residual"]
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, delimiter="\t", lineterminator="\n")
        w.writerow(cols_out)
        for r in sorted(all_rows, key=lambda x: (x["song_sha16"], x["onset_time_s"], x["source_stem"])):
            w.writerow([
                r["song_sha16"],
                f"{r['onset_time_s']:.6f}",
                r["source_stem"],
                f"{r['energy_drums']:.10f}",
                f"{r['energy_bass']:.10f}",
                f"{r['energy_vocals']:.10f}",
                f"{r['energy_guitar']:.10f}",
                f"{r['energy_piano']:.10f}",
                f"{r['energy_other']:.10f}",
            ])
