#!/usr/bin/env python3
# c41 harmonic-window-refinement wrapper.
#
# Non-destructive wrapper around c9's scripts/rules/extract/harmonic.py.
#
# Design (revised after c9-ledger inspection):
#   - c9 itself DOES NOT apply a uniqueness gate; it emits single-chord windows.
#     The uniqueness coercion is a c12 post-processor (breadth_seeds) and c40
#     (rated_corpus). This wrapper keeps those two concerns separated:
#
#     _raw_c9(score)                  → identity delegation, byte-equal to c9
#     _raw_finer(score, hop)          → alternate windowing, no gate applied
#     extract(score, hop, policy)     → _raw_* then apply progression_min_unique
#
#   - Anti-cheat identity contract: _raw_c9(synth_030s) reproduces c9's raw
#     synth_030s harmonic anchor rule_ids byte-identically. Test-enforced.
#
# NO PRNG. Interpreter-guarded. No sidecar_nonfactor imports.

import sys
from pathlib import Path
from typing import List, Dict, Any, Tuple

assert sys.executable == "/usr/bin/python3", f"expected /usr/bin/python3, got {sys.executable}"

_HERE = Path(__file__).resolve().parent
REPO = _HERE.parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

import music21  # noqa: E402
from music21 import chord as m21_chord, roman as m21_roman  # noqa: E402

# READ-ONLY imports from c9.
from scripts.rules.extract import harmonic as c9_harmonic  # noqa: E402
from scripts.rules.extract._common import (  # noqa: E402
    measure_to_seconds, transcription_event_id, clip_id, DEFAULT_TEMPO_BPM,
)


GRID_CELLS: List[Tuple[float, str]] = [
    (5.0, "2"),
    (5.0, "1_with_repeat_allowed"),
    (2.5, "2"),
    (2.5, "1_with_repeat_allowed"),
    (2.0, "2"),
    (2.0, "1_with_repeat_allowed"),
]


def cell_key(window_hop_s: float, progression_min_unique: str) -> str:
    """Canonical cell key: 'hop{HOP}_uniq{POLICY}'."""
    hop = f"{window_hop_s:g}".replace(".", "p")
    return f"hop{hop}_uniq{progression_min_unique}"


def _uniqueness_ok(progression: List[str], policy: str) -> bool:
    """Return True if the progression passes the uniqueness gate."""
    if not progression:
        return False
    uniq = set(progression)
    if policy == "2":
        return len(uniq) >= 2
    if policy == "1_with_repeat_allowed":
        if len(uniq) >= 2:
            return True
        return len(uniq) == 1 and len(progression) >= 2
    raise ValueError(f"unknown uniqueness policy: {policy!r}")


def _raw_c9(score, tempo_bpm: float = DEFAULT_TEMPO_BPM) -> List[Dict[str, Any]]:
    """Identity delegation: byte-equal to c9's harmonic.extract()."""
    return c9_harmonic.extract(score, tempo_bpm=tempo_bpm)


def _raw_finer(score, window_hop_s: float,
               tempo_bpm: float = DEFAULT_TEMPO_BPM) -> List[Dict[str, Any]]:
    """Alternate windowing: hop = window width; non-overlapping.

    Returns ALL candidate rows (no uniqueness gate); the caller applies the
    policy filter downstream in extract().
    """
    k = score.analyze("key")
    key_str = c9_harmonic._key_string(k)
    chordified = score.chordify()
    chords = list(chordified.recurse().getElementsByClass(m21_chord.Chord))

    timeline: List[Tuple[float, str]] = []
    prev_fig = None
    for c in chords:
        try:
            rn = m21_roman.romanNumeralFromChord(c, k)
        except Exception:
            continue
        fig = c9_harmonic._normalize_roman(rn.figure)
        if fig == prev_fig:
            continue
        timeline.append((float(c.offset), fig))
        prev_fig = fig

    total_beats = float(score.duration.quarterLength)
    beats_per_second = tempo_bpm / 60.0
    total_seconds = total_beats / beats_per_second
    total_measures = max(1, int(round(total_beats / 4.0)))
    end_s_song = measure_to_seconds(total_measures, tempo_bpm)

    scored_te = transcription_event_id("score")

    rules: List[Dict[str, Any]] = []

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
            "cadence": c9_harmonic._classify_cadence(prog_song),
        },
    })

    win_idx = 0
    s = 0.0
    while s + 1e-9 < total_seconds:
        s_end = min(s + window_hop_s, total_seconds)
        beat_start = s * beats_per_second
        beat_end = s_end * beats_per_second
        win_fig = [fig for off, fig in timeline if beat_start <= off < beat_end]
        deduped: List[str] = []
        for f in win_fig:
            if not deduped or deduped[-1] != f:
                deduped.append(f)
        if deduped:
            m_start = int(beat_start // 4)
            m_end = max(m_start + 1, int(-(-beat_end // 4)))
            rules.append({
                "rule_type": "harmonic",
                "scope": {
                    "level": "measure",
                    "start_s": round(s, 6),
                    "end_s": round(s_end, 6),
                },
                "provenance_pointers": [{
                    "transcription_event_id": scored_te,
                    "measure_range": [m_start, m_end],
                    "clip_id": clip_id(f"harmonic:hop{window_hop_s:g}:win{win_idx}"),
                }],
                "confidence": 0.75,
                "parameters": {
                    "key": key_str,
                    "chord_progression": deduped[:6],
                    "cadence": c9_harmonic._classify_cadence(deduped),
                },
            })
        s += window_hop_s
        win_idx += 1

    return rules


def extract(score, window_hop_s: float, progression_min_unique: str,
            tempo_bpm: float = DEFAULT_TEMPO_BPM) -> List[Dict[str, Any]]:
    """Return a list of candidate rule dicts for one (score, cell)."""
    if abs(window_hop_s - 5.0) < 1e-9:
        raw = _raw_c9(score, tempo_bpm=tempo_bpm)
    else:
        raw = _raw_finer(score, window_hop_s, tempo_bpm=tempo_bpm)
    # Apply uniqueness policy AFTER raw extraction, uniformly across cells.
    # Song-level rows always pass (they preserve c9's original 8-chord slice).
    kept: List[Dict[str, Any]] = []
    for r in raw:
        if r["scope"]["level"] == "song":
            kept.append(r)
            continue
        prog = r.get("parameters", {}).get("chord_progression") or []
        if _uniqueness_ok(prog, progression_min_unique):
            kept.append(r)
    return kept
