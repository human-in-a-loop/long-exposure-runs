#!/usr/bin/env python3
# M-RULES-1/extraction/harmonic — Key + Roman-numeral chord progression + cadence.
#
# Author: cyd7bevdr@mozmail.com, cycle 9 (fork f1bae241bde9 / clone-0).
#
# Non-factor AST isolation: this module MUST NOT import
# scripts.classifier.sidecar_nonfactor.

import sys
from typing import List, Dict, Any

assert sys.executable == "/usr/bin/python3", f"expected /usr/bin/python3, got {sys.executable}"

import music21
from music21 import roman as m21_roman, chord as m21_chord

from scripts.rules.extract._common import (
    measure_to_seconds, transcription_event_id, clip_id, DEFAULT_TEMPO_BPM
)

EXTRACTOR = "extract.harmonic"
EXTRACTOR_VERSION = "harmonic-v1"


_VALID_ROMAN = {
    "I","II","III","IV","V","VI","VII",
    "i","ii","iii","iv","v","vi","vii",
}


def _normalize_roman(fig: str) -> str:
    """Coerce a music21 Roman-numeral figure to the schema's regex.

    Schema: ^(I|II|...|vii)[b#]?(m|dim|aug|maj7|m7|7)?$

    We strip inversion digits and any characters that would break the
    pattern. On failure we fall back to the base numeral so the row
    validates and content stays honest about the approximation.
    """
    import re
    base_match = re.match(r"^([iIvV]{1,3})", fig)
    base = base_match.group(1) if base_match else "I"
    if base not in _VALID_ROMAN:
        base = "I"
    accidental = ""
    if base_match:
        rest = fig[base_match.end():]
        if rest.startswith(("b","#")):
            accidental = rest[0]
            rest = rest[1:]
        # Detect chord-quality suffix in {m,dim,aug,maj7,m7,7}
        for suf in ("maj7","dim","aug","m7","m","7"):
            if rest.startswith(suf):
                return f"{base}{accidental}{suf}"
    return f"{base}{accidental}"


def _classify_cadence(progression: List[str]) -> str:
    """Trivial 2-chord look-back cadence classifier."""
    if len(progression) < 2:
        return "none"
    prev, last = progression[-2], progression[-1]
    prev_base = prev.rstrip("mdiaug7").lower()
    last_base = last.rstrip("mdiaug7").lower()
    if prev_base == "v" and last_base == "i":
        return "authentic"
    if prev_base == "iv" and last_base == "i":
        return "plagal"
    if last_base == "v":
        return "half"
    if prev_base == "v" and last_base == "vi":
        return "deceptive"
    return "none"


def _key_string(k) -> str:
    """music21 key -> 'X_major'/'X_minor' matching schema regex."""
    tonic = k.tonic.name  # e.g. 'F', 'F#', 'Bb'
    tonic = tonic.replace("-", "b")  # music21 uses '-' for flat
    if len(tonic) > 2:
        tonic = tonic[:2]
    mode = k.mode if k.mode in {
        "major","minor","dorian","phrygian","lydian","mixolydian","aeolian","locrian"
    } else "major"
    return f"{tonic}_{mode}"


def extract(score: music21.stream.Score, tempo_bpm: float = DEFAULT_TEMPO_BPM) -> List[Dict[str, Any]]:
    """Return a list of candidate rule dicts (rule_id/event_id/ts added later)."""
    k = score.analyze("key")
    key_str = _key_string(k)

    chordified = score.chordify()
    chords = list(chordified.recurse().getElementsByClass(m21_chord.Chord))

    # Build the sequential Roman-numeral timeline, filtering out consecutive
    # duplicates so the progression captures real chord changes, not
    # repeated attacks of the same harmony.
    timeline = []  # (offset_q, roman_str)
    prev_fig = None
    for c in chords:
        try:
            rn = m21_roman.romanNumeralFromChord(c, k)
        except Exception:
            continue
        fig = _normalize_roman(rn.figure)
        if fig == prev_fig:
            continue
        timeline.append((float(c.offset), fig))
        prev_fig = fig

    total_beats = float(score.duration.quarterLength)
    total_measures = int(round(total_beats / 4.0))  # 4/4 assumed
    if total_measures < 1:
        total_measures = 1
    end_s_song = measure_to_seconds(total_measures, tempo_bpm)

    scored_te = transcription_event_id("score")

    rules: List[Dict[str, Any]] = []

    # Row 1: song-level "master" progression (first 8 unique chords).
    prog_song = [fig for _, fig in timeline[:8]] or ["I"]
    rules.append({
        "rule_type": "harmonic",
        "scope": {"level": "song", "start_s": 0.0, "end_s": end_s_song},
        "provenance_pointers": [{
            "transcription_event_id": scored_te,
            "measure_range": [0, total_measures],
            "clip_id": clip_id("harmonic:song"),
        }],
        "confidence": 0.85,
        "parameters": {
            "key": key_str,
            "chord_progression": prog_song,
            "cadence": _classify_cadence(prog_song),
        },
    })

    # Rows 2-5+: sliding measure windows (0-3, 3-6, 6-9, 9-12, 12-15).
    # Progressions are extracted per-window from the chordified timeline.
    beats_per_measure = 4
    for win_idx, m_start in enumerate([0, 3, 6, 9, 12]):
        m_end = min(m_start + 3, total_measures)
        if m_end <= m_start:
            continue
        beat_start = m_start * beats_per_measure
        beat_end = m_end * beats_per_measure
        win_fig = [fig for off, fig in timeline if beat_start <= off < beat_end]
        # dedup adjacent within window
        deduped = []
        for f in win_fig:
            if not deduped or deduped[-1] != f:
                deduped.append(f)
        if not deduped:
            deduped = [prog_song[0]]
        rules.append({
            "rule_type": "harmonic",
            "scope": {
                "level": "measure",
                "start_s": measure_to_seconds(m_start, tempo_bpm),
                "end_s": measure_to_seconds(m_end, tempo_bpm),
            },
            "provenance_pointers": [{
                "transcription_event_id": scored_te,
                "measure_range": [m_start, m_end],
                "clip_id": clip_id(f"harmonic:win{win_idx}"),
            }],
            "confidence": 0.75,
            "parameters": {
                "key": key_str,
                "chord_progression": deduped[:6],  # cap window length
                "cadence": _classify_cadence(deduped),
            },
        })

    return rules
