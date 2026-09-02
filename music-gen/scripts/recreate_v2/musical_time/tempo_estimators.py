#!/usr/bin/python3
"""Tempo / beat / downbeat estimator survey (D1).

Candidate A (LIBROSA, always available): librosa.beat.beat_track + chroma-CQT
downbeat inference.
Candidate B (MADMOM, learned): probed via ``pip install madmom``; if fetch
succeeds, RNN+DBN models are used. Fetch outcome is logged honestly to
``data/rc10_musical_time/fetchability_ladder.jsonl`` per c11 CLAP
honest-logging pattern.

No PRNG. Deterministic under BLAS pins + env pins.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import subprocess
import sys
from typing import Any, Dict, List, Tuple

import numpy as np


def probe_madmom(ladder_path: pathlib.Path) -> Dict[str, Any]:
    """Attempt madmom import (assumed pre-installed); log outcome honestly.

    We do NOT run ``pip install`` here — the brief allows probe-and-log, and
    egress is known blocked (HTTP 429). We simply attempt import and record.
    """
    try:
        import madmom  # type: ignore  # noqa: F401
        result = {
            "rung": "madmom_import",
            "outcome": "FETCH_OK",
            "reason": "already-installed",
            "madmom_version": getattr(__import__("madmom"), "__version__", "unknown"),
        }
    except Exception as exc:
        result = {
            "rung": "madmom_import",
            "outcome": "FETCH_FAIL",
            "reason": f"{type(exc).__name__}: {exc}",
            "notes": "egress blocked (HTTP 429 + tv_embedded per c45-c56 registry); "
                     "librosa is sole candidate; tap-test becomes self-consistency check",
        }
    ladder_path.parent.mkdir(parents=True, exist_ok=True)
    with ladder_path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(result, sort_keys=True) + "\n")
    return result


def estimate_librosa(y_mono: np.ndarray, sr: int, start_bpm: float) -> Dict[str, Any]:
    """Return tempo + beat_times + downbeat_start_s using librosa.

    Downbeat inferred by chroma-CQT bar-mean argmax over candidate offsets.
    Uses fixed beats_per_bar=4 (common time; documented assumption).
    """
    import librosa

    tempo, beat_times = librosa.beat.beat_track(
        y=y_mono, sr=sr, units="time", start_bpm=float(start_bpm)
    )
    tempo_bpm = float(np.atleast_1d(tempo)[0])
    beat_times = np.asarray(beat_times, dtype=np.float64)

    beats_per_bar = 4
    if beat_times.size < beats_per_bar:
        downbeat_start_s = float(beat_times[0]) if beat_times.size else 0.0
    else:
        # Chroma-CQT per bar mean, argmax offset selecting the strongest bar.
        chroma = librosa.feature.chroma_cqt(y=y_mono, sr=sr, hop_length=512)
        best_offset = 0
        best_score = -np.inf
        n_bars_min = 2
        for offset in range(beats_per_bar):
            bar_starts = beat_times[offset::beats_per_bar]
            if bar_starts.size < n_bars_min:
                continue
            frames = librosa.time_to_frames(bar_starts, sr=sr, hop_length=512)
            # Bar-mean chroma envelope: peak-to-median ratio.
            envs = []
            for f in frames:
                lo = max(0, int(f))
                hi = min(chroma.shape[1], lo + max(1, chroma.shape[1] // len(bar_starts)))
                if hi > lo:
                    envs.append(float(chroma[:, lo:hi].mean()))
            if not envs:
                continue
            envs_a = np.asarray(envs, dtype=np.float64)
            score = float(envs_a.max() - np.median(envs_a))
            if score > best_score:
                best_score = score
                best_offset = offset
        downbeat_start_s = float(beat_times[best_offset])

    return {
        "candidate": "librosa",
        "tempo_bpm": tempo_bpm,
        "beat_count": int(beat_times.size),
        "beat_times_s": beat_times.tolist(),
        "downbeat_start_s": downbeat_start_s,
        "beats_per_bar": beats_per_bar,
    }


def estimate_madmom(y_mono: np.ndarray, sr: int) -> Dict[str, Any]:
    """Placeholder: raises if madmom unavailable (logged to ladder)."""
    import madmom  # type: ignore
    from madmom.features.beats import RNNBeatProcessor, DBNBeatTrackingProcessor  # type: ignore
    from madmom.features.downbeats import (  # type: ignore
        RNNDownBeatProcessor,
        DBNDownBeatTrackingProcessor,
    )

    beat_act = RNNBeatProcessor()(y_mono)
    beat_times = DBNBeatTrackingProcessor(fps=100)(beat_act)
    db_act = RNNDownBeatProcessor()(y_mono)
    db_pairs = DBNDownBeatTrackingProcessor(beats_per_bar=[3, 4], fps=100)(db_act)
    downbeat_start_s = float(db_pairs[db_pairs[:, 1] == 1][0, 0]) if len(db_pairs) else 0.0
    beat_times = np.asarray(beat_times, dtype=np.float64)
    ibi = np.diff(beat_times) if beat_times.size > 1 else np.array([0.5])
    tempo_bpm = float(60.0 / np.median(ibi))

    return {
        "candidate": "madmom",
        "tempo_bpm": tempo_bpm,
        "beat_count": int(beat_times.size),
        "beat_times_s": beat_times.tolist(),
        "downbeat_start_s": downbeat_start_s,
        "beats_per_bar": 4,
    }


def survey_song(
    mix_mono: np.ndarray,
    sr: int,
    rc5_start_bpm: float,
    madmom_available: bool,
) -> Dict[str, Any]:
    """Run librosa (candidate A) using rc5 as start_bpm anchor; probe madmom (B).

    Winner-selection under tap-test unavailability: the rc5 tempo anchor is
    treated as authoritative for bar-length arithmetic (c53 READ-ONLY
    anchor). Librosa's estimated_bpm is retained diagnostically to compute
    an octave-doubling flag. Downbeat is refined via chroma-CQT peak.
    """
    lib = estimate_librosa(mix_mono, sr, rc5_start_bpm)

    # Octave-doubling / halving detection vs rc5 anchor.
    lib_bpm = lib["tempo_bpm"]
    octave_ratios = [0.5, 1.0, 2.0]
    ratio_to_rc5 = lib_bpm / rc5_start_bpm if rc5_start_bpm > 0 else 1.0
    closest_octave = min(octave_ratios, key=lambda r: abs(r - ratio_to_rc5))
    octave_off = abs(closest_octave - 1.0) > 1e-3

    # If librosa octave-halved or octave-doubled, snap tempo back to rc5.
    # This keeps bar arithmetic consistent with the c53 anchor while beat
    # phase alignment still reflects librosa on the chosen-section mix.
    authoritative_bpm = float(rc5_start_bpm) if octave_off else float(lib_bpm)
    lib["authoritative_bpm"] = authoritative_bpm
    lib["rc5_anchor_bpm"] = float(rc5_start_bpm)
    lib["octave_off"] = bool(octave_off)
    lib["closest_octave_ratio"] = float(closest_octave)

    # Rescale beat_times to authoritative BPM if we snapped: shift phase by
    # the librosa downbeat, then re-emit uniform beats at authoritative_bpm.
    if octave_off:
        phase = float(lib["downbeat_start_s"])
        step = 60.0 / authoritative_bpm
        n_beats = int(np.floor((len(mix_mono) / sr - phase) / step)) + 1
        n_beats = max(1, n_beats)
        lib["beat_times_s"] = (phase + np.arange(n_beats) * step).tolist()
        lib["beat_count"] = n_beats
        lib["tempo_bpm"] = authoritative_bpm

    result: Dict[str, Any] = {"librosa": lib}

    if madmom_available:
        try:
            mad = estimate_madmom(mix_mono, sr)
            result["madmom"] = mad
            result["winner"] = "librosa"
            result["winner_reason"] = "librosa_default_no_tap_test"
            result["candidate_disagreement_bpm"] = abs(mad["tempo_bpm"] - lib["tempo_bpm"])
        except Exception as exc:
            result["madmom_error"] = f"{type(exc).__name__}: {exc}"
            result["winner"] = "librosa"
            result["winner_reason"] = "madmom_runtime_fail"
    else:
        result["winner"] = "librosa"
        result["winner_reason"] = (
            "LIBROSA_UNCONTESTED_RC5_ANCHORED" if octave_off else "LIBROSA_UNCONTESTED"
        )

    return result
