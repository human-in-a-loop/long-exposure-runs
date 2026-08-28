#!/usr/bin/env python3
# M-RULES-1/extraction/melodic — contour + range + pitch-class histogram.
#
# Author: cyd7bevdr@mozmail.com, cycle 9 (fork f1bae241bde9 / clone-0).
#
# Non-factor AST isolation: this module MUST NOT import
# scripts.classifier.sidecar_nonfactor.

import sys
from typing import List, Dict, Any, Tuple

assert sys.executable == "/usr/bin/python3", f"expected /usr/bin/python3, got {sys.executable}"

import music21

from scripts.rules.extract._common import (
    transcription_event_id, clip_id, measure_to_seconds,
    DEFAULT_TEMPO_BPM, part_group,
)

EXTRACTOR = "extract.melodic"
EXTRACTOR_VERSION = "melodic-v1"


def _pitch_class_histogram(midi_pitches: List[int]) -> List[float]:
    if not midi_pitches:
        # Uniform-zero-ish; return valid shape (single-bin bump so sum == 1).
        h = [0.0] * 12
        h[0] = 1.0
        return h
    counts = [0] * 12
    for p in midi_pitches:
        counts[int(p) % 12] += 1
    total = sum(counts)
    # Sum-to-1 within 1e-6. Divide first then renormalize the last bin
    # to soak up float error.
    hist = [c / total for c in counts]
    err = 1.0 - sum(hist)
    hist[-1] += err
    return hist


def _classify_contour(midi_pitches: List[int]) -> str:
    if len(midi_pitches) < 2:
        return "static"
    diffs = [b - a for a, b in zip(midi_pitches[:-1], midi_pitches[1:])]
    up = sum(1 for d in diffs if d > 0)
    down = sum(1 for d in diffs if d < 0)
    flat = sum(1 for d in diffs if d == 0)
    n = len(diffs)
    if flat >= 0.7 * n:
        return "static"
    if up >= 0.7 * n:
        return "ascending"
    if down >= 0.7 * n:
        return "descending"
    # arch = up-then-down or down-then-up dominance across halves
    half = n // 2
    if half >= 2:
        first_up = sum(1 for d in diffs[:half] if d > 0)
        second_down = sum(1 for d in diffs[half:] if d < 0)
        if first_up > half * 0.5 and second_down > (n - half) * 0.5:
            return "arch"
    return "undulating"


def _part_notes_in_window(part: music21.stream.Part,
                          m_start: int, m_end: int) -> List[int]:
    beats_per_measure = 4
    beat_lo = m_start * beats_per_measure
    beat_hi = m_end * beats_per_measure
    out: List[int] = []
    for n in part.recurse().notes:
        off = float(n.offset)
        # music21 Note.offset is relative to the containing container; use
        # .getOffsetInHierarchy(part) for the global position within the part.
        try:
            off = float(n.getOffsetInHierarchy(part))
        except Exception:
            pass
        if beat_lo <= off < beat_hi:
            if hasattr(n, "pitch"):
                out.append(int(n.pitch.midi))
            elif hasattr(n, "pitches") and n.pitches:
                out.append(int(n.pitches[0].midi))
    return out


def _part_notes(part: music21.stream.Part) -> List[int]:
    out: List[int] = []
    for n in part.recurse().notes:
        if hasattr(n, "pitch"):
            out.append(int(n.pitch.midi))
        elif hasattr(n, "pitches") and n.pitches:
            out.append(int(n.pitches[0].midi))
    return out


def _pick_first(parts, group: str):
    for p in parts:
        if part_group(str(p.id)) == group:
            return p
    return None


def extract(score: music21.stream.Score, tempo_bpm: float = DEFAULT_TEMPO_BPM) -> List[Dict[str, Any]]:
    total_beats = float(score.duration.quarterLength)
    total_measures = max(1, int(round(total_beats / 4.0)))

    bass_part = _pick_first(score.parts, "bass")
    other_part = _pick_first(score.parts, "other")

    rules: List[Dict[str, Any]] = []

    # Row 1: bass whole-song.
    if bass_part is not None:
        pitches = _part_notes(bass_part)
        if pitches:
            rng = max(pitches) - min(pitches)
            rules.append({
                "rule_type": "melodic",
                "scope": {"level": "song", "start_s": 0.0,
                          "end_s": measure_to_seconds(total_measures, tempo_bpm)},
                "provenance_pointers": [{
                    "transcription_event_id": transcription_event_id("bass"),
                    "measure_range": [0, total_measures],
                    "clip_id": clip_id("melodic:bass:song"),
                }],
                "confidence": 0.82,
                "parameters": {
                    "contour": _classify_contour(pitches),
                    "range_semitones": min(48, max(0, int(rng))),
                    "pitch_class_histogram": _pitch_class_histogram(pitches),
                },
            })

    # Rows 2-3: bass windows.
    if bass_part is not None:
        for win_idx, (m_start, m_end) in enumerate([(0, 8), (7, 15)]):
            m_end = min(m_end, total_measures)
            if m_end <= m_start:
                continue
            pitches = _part_notes_in_window(bass_part, m_start, m_end)
            if not pitches:
                continue
            rng = max(pitches) - min(pitches)
            rules.append({
                "rule_type": "melodic",
                "scope": {
                    "level": "measure",
                    "start_s": measure_to_seconds(m_start, tempo_bpm),
                    "end_s": measure_to_seconds(m_end, tempo_bpm),
                },
                "provenance_pointers": [{
                    "transcription_event_id": transcription_event_id("bass"),
                    "measure_range": [m_start, m_end],
                    "clip_id": clip_id(f"melodic:bass:win{win_idx}"),
                }],
                "confidence": 0.75,
                "parameters": {
                    "contour": _classify_contour(pitches),
                    "range_semitones": min(48, max(0, int(rng))),
                    "pitch_class_histogram": _pitch_class_histogram(pitches),
                },
            })

    # Row 4: other whole-song.
    if other_part is not None:
        pitches = _part_notes(other_part)
        if pitches:
            rng = max(pitches) - min(pitches)
            rules.append({
                "rule_type": "melodic",
                "scope": {"level": "song", "start_s": 0.0,
                          "end_s": measure_to_seconds(total_measures, tempo_bpm)},
                "provenance_pointers": [{
                    "transcription_event_id": transcription_event_id("other"),
                    "measure_range": [0, total_measures],
                    "clip_id": clip_id("melodic:other:song"),
                }],
                "confidence": 0.78,
                "parameters": {
                    "contour": _classify_contour(pitches),
                    "range_semitones": min(48, max(0, int(rng))),
                    "pitch_class_histogram": _pitch_class_histogram(pitches),
                },
            })

    # Row 5: other measure window.
    if other_part is not None:
        for win_idx, (m_start, m_end) in enumerate([(0, 8), (7, 15)]):
            m_end = min(m_end, total_measures)
            if m_end <= m_start:
                continue
            pitches = _part_notes_in_window(other_part, m_start, m_end)
            if not pitches:
                continue
            rng = max(pitches) - min(pitches)
            rules.append({
                "rule_type": "melodic",
                "scope": {
                    "level": "measure",
                    "start_s": measure_to_seconds(m_start, tempo_bpm),
                    "end_s": measure_to_seconds(m_end, tempo_bpm),
                },
                "provenance_pointers": [{
                    "transcription_event_id": transcription_event_id("other"),
                    "measure_range": [m_start, m_end],
                    "clip_id": clip_id(f"melodic:other:win{win_idx}"),
                }],
                "confidence": 0.72,
                "parameters": {
                    "contour": _classify_contour(pitches),
                    "range_semitones": min(48, max(0, int(rng))),
                    "pitch_class_histogram": _pitch_class_histogram(pitches),
                },
            })

    return rules
