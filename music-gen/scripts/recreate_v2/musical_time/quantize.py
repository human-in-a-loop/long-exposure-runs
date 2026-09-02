#!/usr/bin/python3
"""D2 16th-note grid + micro-timing offsets.

Per song per stem: onsets → nearest 16th grid position + deviation in ms.
Deviations outside [-125, +125] ms are clamped and logged separately (never
silently dropped).
"""
from __future__ import annotations

import json
import pathlib
from typing import Any, Dict, List, Tuple

import numpy as np

CLAMP_LO_MS = -125.0
CLAMP_HI_MS = 125.0
ONSET_DELTA = 0.03


def build_grid_times(downbeat_start_s: float, tempo_bpm: float, duration_s: float) -> np.ndarray:
    """16th-note grid, first 16th on downbeat_start_s."""
    if tempo_bpm <= 0:
        return np.array([downbeat_start_s], dtype=np.float64)
    sixteenth_s = 60.0 / tempo_bpm / 4.0
    n = int(np.floor((duration_s - downbeat_start_s) / sixteenth_s)) + 1
    n = max(1, n)
    return downbeat_start_s + np.arange(n) * sixteenth_s


def detect_onsets(y_mono: np.ndarray, sr: int) -> np.ndarray:
    import librosa
    onset_times = librosa.onset.onset_detect(
        y=y_mono, sr=sr, delta=ONSET_DELTA, backtrack=True, units="time"
    )
    return np.asarray(onset_times, dtype=np.float64)


def quantize_onsets(
    onset_times_s: np.ndarray,
    downbeat_start_s: float,
    tempo_bpm: float,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Return (in_grid_notes, off_grid_records)."""
    in_grid: List[Dict[str, Any]] = []
    off_grid: List[Dict[str, Any]] = []
    if tempo_bpm <= 0:
        for t in onset_times_s:
            off_grid.append({
                "onset_s": float(t),
                "grid_position": None,
                "grid_deviation_ms": None,
                "reason": "tempo_zero",
            })
        return in_grid, off_grid

    sixteenth_s = 60.0 / tempo_bpm / 4.0
    for t in onset_times_s:
        pos = int(round((float(t) - downbeat_start_s) / sixteenth_s))
        expected = downbeat_start_s + pos * sixteenth_s
        dev_ms = (float(t) - expected) * 1000.0
        if pos < 0 or CLAMP_LO_MS > dev_ms or dev_ms > CLAMP_HI_MS:
            off_grid.append({
                "onset_s": float(t),
                "grid_position": int(pos),
                "grid_deviation_ms": float(dev_ms),
                "reason": "outside_clamp" if pos >= 0 else "negative_position",
            })
        else:
            in_grid.append({
                "onset_s": float(t),
                "grid_position": int(pos),
                "grid_deviation_ms": float(dev_ms),
            })
    return in_grid, off_grid


def emit_quantized_notes(out_dir: pathlib.Path, stem: str, notes: List[Dict[str, Any]]) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    p = out_dir / "quantized_notes.json"
    p.write_text(json.dumps({"stem": stem, "notes": notes}, indent=2, sort_keys=True))
