#!/usr/bin/env python3
# M-RULES-1/extraction/arrangement — instrument entry/exit + density curves.
#
# Author: cyd7bevdr@mozmail.com, cycle 9 (fork f1bae241bde9 / clone-0).
#
# Non-factor AST isolation: this module MUST NOT import
# scripts.classifier.sidecar_nonfactor.

import sys
from typing import List, Dict, Any

assert sys.executable == "/usr/bin/python3", f"expected /usr/bin/python3, got {sys.executable}"

import music21

from scripts.rules.extract._common import (
    transcription_event_id, clip_id, measure_to_seconds,
    DEFAULT_TEMPO_BPM, part_group,
)

EXTRACTOR = "extract.arrangement"
EXTRACTOR_VERSION = "arrangement-v1"


def _density_over_measures(part: music21.stream.Part,
                           total_measures: int) -> List[float]:
    """Per-measure normalized note-count density. 0=empty, 1=peak."""
    counts = [0] * total_measures
    for n in part.recurse().notes:
        try:
            off = float(n.getOffsetInHierarchy(part))
        except Exception:
            off = float(n.offset)
        m = int(off // 4)  # 4/4
        if 0 <= m < total_measures:
            counts[m] += 1
    peak = max(counts) if counts else 0
    if peak == 0:
        return [0.0] * total_measures
    return [round(c / peak, 4) for c in counts]


def _combined_density(group_parts: List[music21.stream.Part],
                     total_measures: int) -> List[float]:
    if not group_parts:
        return [0.0] * total_measures
    combined = [0.0] * total_measures
    for p in group_parts:
        for i, v in enumerate(_density_over_measures(p, total_measures)):
            combined[i] += v
    peak = max(combined) if combined else 0.0
    if peak == 0.0:
        return [0.0] * total_measures
    return [round(v / peak, 4) for v in combined]


def _entry_exit_events(part: music21.stream.Part,
                       total_measures: int,
                       tempo_bpm: float,
                       instrument_label: str) -> List[Dict[str, Any]]:
    """Detect contiguous active runs (measures where the part has any
    note). Emit an 'add' event at the run start and a 'remove' event at
    the run end (unless it runs to the score end)."""
    counts = [0] * total_measures
    for n in part.recurse().notes:
        try:
            off = float(n.getOffsetInHierarchy(part))
        except Exception:
            off = float(n.offset)
        m = int(off // 4)
        if 0 <= m < total_measures:
            counts[m] += 1
    events: List[Dict[str, Any]] = []
    active = False
    for m in range(total_measures):
        is_on = counts[m] > 0
        if is_on and not active:
            events.append({
                "t_s": measure_to_seconds(m, tempo_bpm),
                "op": "add",
                "layer": instrument_label,
            })
            active = True
        elif not is_on and active:
            events.append({
                "t_s": measure_to_seconds(m, tempo_bpm),
                "op": "remove",
                "layer": instrument_label,
            })
            active = False
    return events


def extract(score: music21.stream.Score, tempo_bpm: float = DEFAULT_TEMPO_BPM) -> List[Dict[str, Any]]:
    total_beats = float(score.duration.quarterLength)
    total_measures = max(2, int(round(total_beats / 4.0)))
    end_s_song = measure_to_seconds(total_measures, tempo_bpm)
    scored_te = transcription_event_id("score")

    # Bucket parts by group.
    groups: Dict[str, List[music21.stream.Part]] = {"bass": [], "drums": [], "other": []}
    for p in score.parts:
        g = part_group(str(p.id))
        if g in groups:
            groups[g].append(p)

    present_instruments = [g for g in ("drums", "bass", "other") if groups[g]]
    # `instrumentation` needs a non-empty list. Even if some groups have
    # zero notes on this seed, they exist as Parts in the merged score,
    # which is honest arrangement information.
    if not present_instruments:
        present_instruments = ["other"]

    rules: List[Dict[str, Any]] = []

    # Row 1: whole-song combined density + all entries.
    all_parts = groups["drums"] + groups["bass"] + groups["other"]
    combined = _combined_density(all_parts, total_measures)
    all_events: List[Dict[str, Any]] = []
    for g in ("drums", "bass", "other"):
        for p in groups[g]:
            for ev in _entry_exit_events(p, total_measures, tempo_bpm, g):
                all_events.append(ev)
    # dedup + sort by t_s then op
    seen = set()
    dedup_events = []
    for ev in sorted(all_events, key=lambda e: (e["t_s"], e["op"], e["layer"])):
        key = (ev["t_s"], ev["op"], ev["layer"])
        if key not in seen:
            seen.add(key)
            dedup_events.append(ev)
    rules.append({
        "rule_type": "arrangement",
        "scope": {"level": "song", "start_s": 0.0, "end_s": end_s_song},
        "provenance_pointers": [{
            "transcription_event_id": scored_te,
            "measure_range": [0, total_measures],
            "clip_id": clip_id("arr:song"),
        }],
        "confidence": 0.85,
        "parameters": {
            "instrumentation": present_instruments,
            "density_over_time": combined,
            "layer_events": dedup_events,
        },
    })

    # Rows 2-4: per-instrument density + events (one row per instrument).
    for g in ("drums", "bass", "other"):
        gparts = groups[g]
        density = _combined_density(gparts, total_measures)
        events: List[Dict[str, Any]] = []
        for p in gparts:
            events.extend(_entry_exit_events(p, total_measures, tempo_bpm, g))
        # A row's layer_events must all lie within scope. Song-level scope
        # so all valid.
        rules.append({
            "rule_type": "arrangement",
            "scope": {"level": "song", "start_s": 0.0, "end_s": end_s_song},
            "provenance_pointers": [{
                "transcription_event_id": scored_te,
                "measure_range": [0, total_measures],
                "clip_id": clip_id(f"arr:{g}"),
            }],
            "confidence": 0.70,
            "parameters": {
                "instrumentation": [g],
                "density_over_time": density,
                "layer_events": events[:16],
            },
        })

    # Row 5: first half of song (measure 0 .. half).
    half = max(2, total_measures // 2)
    first_half_events = [ev for ev in dedup_events
                         if ev["t_s"] <= measure_to_seconds(half, tempo_bpm) + 1e-6]
    rules.append({
        "rule_type": "arrangement",
        "scope": {"level": "measure", "start_s": 0.0,
                  "end_s": measure_to_seconds(half, tempo_bpm)},
        "provenance_pointers": [{
            "transcription_event_id": scored_te,
            "measure_range": [0, half],
            "clip_id": clip_id("arr:firsthalf"),
        }],
        "confidence": 0.72,
        "parameters": {
            "instrumentation": present_instruments,
            "density_over_time": combined[:half] if len(combined) >= half else combined,
            "layer_events": first_half_events,
        },
    })

    return rules
