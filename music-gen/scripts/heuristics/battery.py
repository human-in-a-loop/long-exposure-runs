# battery — orchestrates the four clip-level heuristics on one clip
# created: 2026-08-28T05:20:00Z  cycle: 4  run_id: run-2026-08-28T040704Z
# agent: worker (clone-1)  milestone: M-HEUR-1
"""Clip battery: runs melody / timbre / form / dynamics on a single clip."""
from __future__ import annotations

from pathlib import Path

import librosa
import numpy as np

from .dynamics import dynamics_quality
from .form import form_quality
from .mess_scale import HeuristicResult
from .melody import melody_quality
from .timbre import timbre_quality


HEURISTICS = ("melody_quality", "timbre_quality", "form_quality", "dynamics_quality")


def run_battery(y: np.ndarray, sr: int) -> dict[str, HeuristicResult]:
    return {
        "melody_quality": melody_quality(y, sr),
        "timbre_quality": timbre_quality(y, sr),
        "form_quality": form_quality(y, sr),
        "dynamics_quality": dynamics_quality(y, sr),
    }


def load_clip(path: Path, target_sr: int = 22050) -> tuple[np.ndarray, int]:
    y, sr = librosa.load(str(path), sr=target_sr, mono=True)
    return y, sr
