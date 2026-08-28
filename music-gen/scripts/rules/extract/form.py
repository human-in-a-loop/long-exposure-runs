#!/usr/bin/env python3
# M-RULES-1/extraction/form — sectionizations of the merged score.
#
# Author: cyd7bevdr@mozmail.com, cycle 9 (fork f1bae241bde9 / clone-0).
#
# Non-factor AST isolation: this module MUST NOT import
# scripts.classifier.sidecar_nonfactor.
#
# Strategy: emit five DISTINCT sectionizations of the same seed. Each row
# carries a different `sections` list, so rule_id (content-hashed) is
# distinct per row. This is honest granularity — 30s is too short for a
# rich narrative form, so we expose several plausible parses and let the
# generator downstream pick.

import sys
from typing import List, Dict, Any

assert sys.executable == "/usr/bin/python3", f"expected /usr/bin/python3, got {sys.executable}"

import music21

from scripts.rules.extract._common import (
    transcription_event_id, clip_id, measure_to_seconds, DEFAULT_TEMPO_BPM,
)

EXTRACTOR = "extract.form"
EXTRACTOR_VERSION = "form-v1"


def _uniform_sections(total_measures: int, block_size: int) -> List[Dict[str, Any]]:
    """Label blocks A, B, C, ..., wrapping labels alphabetically."""
    labels = ["A","B","C","D","E","F","G","H"]
    out: List[Dict[str, Any]] = []
    start = 0
    idx = 0
    while start < total_measures:
        end = min(start + block_size, total_measures)
        if end <= start:
            break
        out.append({
            "label": labels[idx % len(labels)],
            "start_measure": start,
            "end_measure": end,
        })
        start = end
        idx += 1
    if not out:
        out.append({"label": "A", "start_measure": 0, "end_measure": max(1, total_measures)})
    return out


def _abab_sections(total_measures: int, block_size: int) -> List[Dict[str, Any]]:
    """A/B/A/B alternation."""
    out: List[Dict[str, Any]] = []
    start = 0
    idx = 0
    while start < total_measures:
        end = min(start + block_size, total_measures)
        if end <= start:
            break
        out.append({
            "label": "A" if idx % 2 == 0 else "B",
            "start_measure": start,
            "end_measure": end,
        })
        start = end
        idx += 1
    if not out:
        out.append({"label": "A", "start_measure": 0, "end_measure": max(1, total_measures)})
    return out


def extract(score: music21.stream.Score, tempo_bpm: float = DEFAULT_TEMPO_BPM) -> List[Dict[str, Any]]:
    total_beats = float(score.duration.quarterLength)
    total_measures = max(2, int(round(total_beats / 4.0)))

    scored_te = transcription_event_id("score")
    end_s_song = measure_to_seconds(total_measures, tempo_bpm)

    def _wrap(sections: List[Dict[str, Any]], tag: str, conf: float) -> Dict[str, Any]:
        return {
            "rule_type": "form",
            "scope": {"level": "song", "start_s": 0.0, "end_s": end_s_song},
            "provenance_pointers": [{
                "transcription_event_id": scored_te,
                "measure_range": [0, total_measures],
                "clip_id": clip_id(f"form:{tag}"),
            }],
            "confidence": conf,
            "parameters": {"sections": sections},
        }

    rules: List[Dict[str, Any]] = []

    # Row 1: coarse (whole song = A).
    rules.append(_wrap(
        [{"label": "A", "start_measure": 0, "end_measure": total_measures}],
        "monolithic", 0.55,
    ))

    # Row 2: uniform 4-measure blocks (verse/chorus scale).
    rules.append(_wrap(_uniform_sections(total_measures, 4), "u4", 0.70))

    # Row 3: uniform 2-measure blocks (fine grid).
    rules.append(_wrap(_uniform_sections(total_measures, 2), "u2", 0.60))

    # Row 4: ABAB alternation at 4-measure grain.
    rules.append(_wrap(_abab_sections(total_measures, 4), "abab4", 0.65))

    # Row 5: mixed A-B-A halves.
    half = total_measures // 2
    q = total_measures // 4
    sections = [
        {"label": "A", "start_measure": 0, "end_measure": q if q > 0 else 1},
    ]
    if half > q:
        sections.append({"label": "B", "start_measure": q, "end_measure": half})
    if total_measures > half:
        sections.append({"label": "A", "start_measure": half, "end_measure": total_measures})
    # Filter degenerate zero-width sections.
    sections = [s for s in sections if s["end_measure"] > s["start_measure"]]
    if not sections:
        sections = [{"label": "A", "start_measure": 0, "end_measure": total_measures}]
    rules.append(_wrap(sections, "aba", 0.68))

    return rules
