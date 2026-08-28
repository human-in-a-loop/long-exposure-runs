#!/usr/bin/env python3
# M-RULES-1/schema — synthetic rule instance generator.
#
# Author: cyd7bevdr@mozmail.com, cycle 6 (fork 3168fb0e47a1 / clone-1).
#
# Emits >=5 instances per rule_type into examples/<rule_type>/*.json.
# Every instance:
#   * has a content-derived rule_id (deterministic).
#   * has a deterministic event_id derived from the rule_id (so re-runs
#     produce byte-identical files).
#   * passes validate_row with zero errors.

import hashlib
import json
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO = _HERE.parent.parent.parent.parent  # examples -> schema -> rules -> scripts -> repo

assert sys.executable == "/usr/bin/python3", f"expected /usr/bin/python3, got {sys.executable}"

if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from scripts.rules.rule_id import derive_rule_id, canonical_json  # noqa: E402
from scripts.rules.validate import validate_row  # noqa: E402


EXTRACTOR = "synthetic_examples"
EXTRACTOR_VERSION = "1.0.0"
FIXED_TS = "2026-08-28T00:00:00Z"


def _event_id(rule_id: str) -> str:
    """Deterministic 32-hex event_id derived from rule_id."""
    return hashlib.sha256(f"event::{rule_id}".encode("utf-8")).hexdigest()[:32]


def _transcription_id(tag: str) -> str:
    """32-hex synthetic transcription_event_id."""
    return hashlib.sha256(f"transcription::{tag}".encode("utf-8")).hexdigest()[:32]


def _clip_id(tag: str) -> str:
    """16-hex synthetic clip_id."""
    return hashlib.sha256(f"clip::{tag}".encode("utf-8")).hexdigest()[:16]


def _finish(rule: dict) -> dict:
    """Compute rule_id, event_id, add fixed timestamp / extractor fields."""
    rid = derive_rule_id(rule)
    return {
        "event_type": "rule",
        "schema_v": 1,
        "event_id": _event_id(rid),
        "ts": FIXED_TS,
        "extractor": EXTRACTOR,
        "extractor_version": EXTRACTOR_VERSION,
        "rule_id": rid,
        "rule_type": rule["rule_type"],
        "scope": rule["scope"],
        "provenance_pointers": rule["provenance_pointers"],
        "confidence": rule["confidence"],
        "parameters": rule["parameters"],
    }


# ---------------------------------------------------------------- harmonic
HARMONIC = [
    {
        "rule_type": "harmonic",
        "scope": {"level": "song", "start_s": 0.0, "end_s": 180.0},
        "provenance_pointers": [
            {"transcription_event_id": _transcription_id("h1"), "measure_range": [0, 64], "clip_id": _clip_id("h1c1")}
        ],
        "confidence": 0.92,
        "parameters": {
            "key": "C_major",
            "chord_progression": ["I", "vi", "IV", "V"],
            "cadence": "authentic",
        },
    },
    {
        "rule_type": "harmonic",
        "scope": {"level": "section", "start_s": 30.0, "end_s": 60.0},
        "provenance_pointers": [
            {"transcription_event_id": _transcription_id("h2"), "measure_range": [16, 32]}
        ],
        "confidence": 0.85,
        "parameters": {
            "key": "D_minor",
            "chord_progression": ["ii", "V", "I"],
            "cadence": "authentic",
        },
    },
    {
        "rule_type": "harmonic",
        "scope": {"level": "section", "start_s": 0.0, "end_s": 36.0},
        "provenance_pointers": [
            {"transcription_event_id": _transcription_id("h3"), "measure_range": [0, 12]}
        ],
        "confidence": 0.80,
        "parameters": {
            "key": "A_minor",
            "chord_progression": ["i", "i", "i", "i", "iv", "iv", "i", "i", "V", "iv", "i", "V"],
            "cadence": "half",
        },
    },
    {
        "rule_type": "harmonic",
        "scope": {"level": "section", "start_s": 60.0, "end_s": 90.0},
        "provenance_pointers": [
            {"transcription_event_id": _transcription_id("h4"), "measure_range": [32, 48]}
        ],
        "confidence": 0.70,
        "parameters": {
            "key": "D_dorian",
            "chord_progression": ["i", "IV"],
            "cadence": "plagal",
        },
    },
    {
        "rule_type": "harmonic",
        "scope": {"level": "song", "start_s": 0.0, "end_s": 240.0},
        "provenance_pointers": [
            {"transcription_event_id": _transcription_id("h5"), "measure_range": [0, 96]}
        ],
        "confidence": 0.55,
        "parameters": {
            "key": "F_lydian",
            "chord_progression": ["I", "II", "V"],
            "cadence": "none",
        },
    },
]


# --------------------------------------------------------------- rhythmic
RHYTHMIC = [
    {
        "rule_type": "rhythmic",
        "scope": {"level": "section", "start_s": 0.0, "end_s": 30.0},
        "provenance_pointers": [{"transcription_event_id": _transcription_id("r1"), "measure_range": [0, 16]}],
        "confidence": 0.90,
        "parameters": {"tempo_bpm": 120.0, "meter": "4/4", "pattern": ["kick", "hihat", "snare", "hihat"], "swing_ratio": 0.5},
    },
    {
        "rule_type": "rhythmic",
        "scope": {"level": "section", "start_s": 30.0, "end_s": 60.0},
        "provenance_pointers": [{"transcription_event_id": _transcription_id("r2"), "measure_range": [16, 32]}],
        "confidence": 0.88,
        "parameters": {"tempo_bpm": 90.0, "meter": "3/4", "pattern": ["kick", "snare", "snare"], "swing_ratio": 0.5},
    },
    {
        "rule_type": "rhythmic",
        "scope": {"level": "section", "start_s": 60.0, "end_s": 90.0},
        "provenance_pointers": [{"transcription_event_id": _transcription_id("r3"), "measure_range": [32, 48]}],
        "confidence": 0.82,
        "parameters": {"tempo_bpm": 180.0, "meter": "6/8", "pattern": ["kick", "hihat", "hihat", "snare", "hihat", "hihat"], "swing_ratio": 0.67},
    },
    {
        "rule_type": "rhythmic",
        "scope": {"level": "section", "start_s": 90.0, "end_s": 120.0},
        "provenance_pointers": [{"transcription_event_id": _transcription_id("r4"), "measure_range": [48, 64]}],
        "confidence": 0.75,
        "parameters": {"tempo_bpm": 140.0, "meter": "7/8", "pattern": ["kick", "hihat", "snare", "hihat", "kick", "snare", "hihat"], "swing_ratio": 0.5},
    },
    {
        "rule_type": "rhythmic",
        "scope": {"level": "section", "start_s": 120.0, "end_s": 150.0},
        "provenance_pointers": [{"transcription_event_id": _transcription_id("r5"), "measure_range": [64, 80]}],
        "confidence": 0.85,
        "parameters": {"tempo_bpm": 80.0, "meter": "4/4", "pattern": ["kick", "rest", "rest", "rest", "snare", "rest", "rest", "rest"], "swing_ratio": 0.5},
    },
]


# ---------------------------------------------------------------- melodic
def _pch(indices_weights):
    """Build 12-element PCH normalized to sum 1.0 exactly."""
    v = [0.0] * 12
    for i, w in indices_weights:
        v[i] = w
    s = sum(v)
    # Normalize: if s != 0, scale so sum is exactly 1.0 in float — then adjust
    # element 0 by the residual so sum-to-1 holds within tolerance.
    if s > 0:
        v = [x / s for x in v]
    # Force exact sum-to-1 by absorbing float residual into the largest bin.
    residual = 1.0 - sum(v)
    imax = max(range(12), key=lambda i: v[i])
    v[imax] += residual
    return v


MELODIC = [
    {
        "rule_type": "melodic",
        "scope": {"level": "section", "start_s": 0.0, "end_s": 20.0},
        "provenance_pointers": [{"transcription_event_id": _transcription_id("m1"), "measure_range": [0, 8]}],
        "confidence": 0.86,
        "parameters": {
            "contour": "arch",
            "range_semitones": 12,
            "pitch_class_histogram": _pch([(0, 3), (2, 2), (4, 2), (5, 1), (7, 3), (9, 2), (11, 1)]),
        },
    },
    {
        "rule_type": "melodic",
        "scope": {"level": "section", "start_s": 20.0, "end_s": 40.0},
        "provenance_pointers": [{"transcription_event_id": _transcription_id("m2"), "measure_range": [8, 16]}],
        "confidence": 0.78,
        "parameters": {
            "contour": "static",
            "range_semitones": 4,
            "pitch_class_histogram": _pch([(0, 5), (2, 1), (4, 3), (5, 1)]),
        },
    },
    {
        "rule_type": "melodic",
        "scope": {"level": "song", "start_s": 0.0, "end_s": 200.0},
        "provenance_pointers": [{"transcription_event_id": _transcription_id("m3"), "measure_range": [0, 80]}],
        "confidence": 0.65,
        "parameters": {
            "contour": "ascending",
            "range_semitones": 24,
            "pitch_class_histogram": _pch([(i, 1) for i in range(12)]),
        },
    },
    {
        "rule_type": "melodic",
        "scope": {"level": "section", "start_s": 40.0, "end_s": 60.0},
        "provenance_pointers": [{"transcription_event_id": _transcription_id("m4"), "measure_range": [16, 24]}],
        "confidence": 0.72,
        "parameters": {
            "contour": "undulating",
            "range_semitones": 10,
            "pitch_class_histogram": _pch([(0, 4), (3, 3), (5, 2), (7, 4), (10, 2)]),  # A minor pentatonic-ish
        },
    },
    {
        "rule_type": "melodic",
        "scope": {"level": "song", "start_s": 0.0, "end_s": 300.0},
        "provenance_pointers": [{"transcription_event_id": _transcription_id("m5"), "measure_range": [0, 120]}],
        "confidence": 0.60,
        "parameters": {
            "contour": "descending",
            "range_semitones": 48,
            "pitch_class_histogram": _pch([(i, 1) for i in range(12)]),  # fully chromatic
        },
    },
]


# ------------------------------------------------------------------- form
FORM = [
    {
        "rule_type": "form",
        "scope": {"level": "song", "start_s": 0.0, "end_s": 180.0},
        "provenance_pointers": [{"transcription_event_id": _transcription_id("f1"), "measure_range": [0, 64]}],
        "confidence": 0.90,
        "parameters": {
            "sections": [
                {"label": "A", "start_measure": 0, "end_measure": 16},
                {"label": "B", "start_measure": 16, "end_measure": 32},
                {"label": "A", "start_measure": 32, "end_measure": 48},
                {"label": "B", "start_measure": 48, "end_measure": 64},
            ],
        },
    },
    {
        "rule_type": "form",
        "scope": {"level": "song", "start_s": 0.0, "end_s": 150.0},
        "provenance_pointers": [{"transcription_event_id": _transcription_id("f2"), "measure_range": [0, 48]}],
        "confidence": 0.85,
        "parameters": {
            "sections": [
                {"label": "A", "start_measure": 0, "end_measure": 16},
                {"label": "B", "start_measure": 16, "end_measure": 32},
                {"label": "A1", "start_measure": 32, "end_measure": 48},
            ],
        },
    },
    {
        "rule_type": "form",
        "scope": {"level": "song", "start_s": 0.0, "end_s": 60.0},
        "provenance_pointers": [{"transcription_event_id": _transcription_id("f3"), "measure_range": [0, 16]}],
        "confidence": 0.60,
        "parameters": {
            "sections": [
                {"label": "A", "start_measure": 0, "end_measure": 16},
            ],
        },
    },
    {
        "rule_type": "form",
        "scope": {"level": "song", "start_s": 0.0, "end_s": 240.0},
        "provenance_pointers": [{"transcription_event_id": _transcription_id("f4"), "measure_range": [0, 96]}],
        "confidence": 0.80,
        "parameters": {
            "sections": [
                {"label": "A", "start_measure": 0, "end_measure": 16},
                {"label": "B", "start_measure": 16, "end_measure": 48},
                {"label": "C", "start_measure": 48, "end_measure": 64},
                {"label": "B", "start_measure": 64, "end_measure": 96},
            ],
        },
    },
    {
        "rule_type": "form",
        "scope": {"level": "song", "start_s": 0.0, "end_s": 300.0},
        "provenance_pointers": [{"transcription_event_id": _transcription_id("f5"), "measure_range": [0, 120]}],
        "confidence": 0.82,
        "parameters": {
            "sections": [
                {"label": "A", "start_measure": 0, "end_measure": 24},
                {"label": "B", "start_measure": 24, "end_measure": 48},
                {"label": "A", "start_measure": 48, "end_measure": 72},
                {"label": "C", "start_measure": 72, "end_measure": 96},
                {"label": "A", "start_measure": 96, "end_measure": 120},
            ],
        },
    },
]


# -------------------------------------------------------------- arrangement
ARRANGEMENT = [
    {
        "rule_type": "arrangement",
        "scope": {"level": "song", "start_s": 0.0, "end_s": 180.0},
        "provenance_pointers": [{"transcription_event_id": _transcription_id("a1"), "measure_range": [0, 64]}],
        "confidence": 0.88,
        "parameters": {
            "instrumentation": ["drums", "bass", "piano"],
            "density_over_time": [0.5, 0.5, 0.5, 0.5],
            "layer_events": [],
        },
    },
    {
        "rule_type": "arrangement",
        "scope": {"level": "song", "start_s": 0.0, "end_s": 240.0},
        "provenance_pointers": [{"transcription_event_id": _transcription_id("a2"), "measure_range": [0, 96]}],
        "confidence": 0.80,
        "parameters": {
            "instrumentation": ["drums", "bass", "piano", "strings", "vocals"],
            "density_over_time": [0.2, 0.4, 0.6, 0.8, 1.0],
            "layer_events": [
                {"t_s": 60.0, "op": "add", "layer": "strings"},
                {"t_s": 120.0, "op": "add", "layer": "vocals"},
            ],
        },
    },
    {
        "rule_type": "arrangement",
        "scope": {"level": "song", "start_s": 0.0, "end_s": 200.0},
        "provenance_pointers": [{"transcription_event_id": _transcription_id("a3"), "measure_range": [0, 80]}],
        "confidence": 0.75,
        "parameters": {
            "instrumentation": ["piano", "bass", "drums", "guitar"],
            "density_over_time": [0.25, 0.5, 0.75, 1.0],
            "layer_events": [
                {"t_s": 40.0, "op": "add", "layer": "bass"},
                {"t_s": 80.0, "op": "add", "layer": "drums"},
                {"t_s": 120.0, "op": "add", "layer": "guitar"},
            ],
        },
    },
    {
        "rule_type": "arrangement",
        "scope": {"level": "section", "start_s": 60.0, "end_s": 120.0},
        "provenance_pointers": [{"transcription_event_id": _transcription_id("a4"), "measure_range": [16, 32]}],
        "confidence": 0.70,
        "parameters": {
            "instrumentation": ["synth_pad", "synth_lead"],
            "density_over_time": [0.4, 0.6, 0.4],
            "layer_events": [
                {"t_s": 90.0, "op": "swap", "layer": "synth_lead"},
            ],
        },
    },
    {
        "rule_type": "arrangement",
        "scope": {"level": "song", "start_s": 0.0, "end_s": 210.0},
        "provenance_pointers": [{"transcription_event_id": _transcription_id("a5"), "measure_range": [0, 84]}],
        "confidence": 0.85,
        "parameters": {
            "instrumentation": ["drums", "bass", "electric_guitar", "hammond_organ", "vocals"],
            "density_over_time": [0.6, 0.9, 0.6, 0.9, 0.3, 0.9],
            "layer_events": [
                {"t_s": 30.0, "op": "add", "layer": "hammond_organ"},
                {"t_s": 150.0, "op": "remove", "layer": "hammond_organ"},
                {"t_s": 180.0, "op": "add", "layer": "hammond_organ"},
            ],
        },
    },
]


ALL = {
    "harmonic": HARMONIC,
    "rhythmic": RHYTHMIC,
    "melodic": MELODIC,
    "form": FORM,
    "arrangement": ARRANGEMENT,
}


def build_and_write():
    total = 0
    errors_seen = 0
    for rule_type, examples in ALL.items():
        outdir = _HERE / rule_type
        outdir.mkdir(parents=True, exist_ok=True)
        for i, ex in enumerate(examples, start=1):
            row = _finish(ex)
            errs = validate_row(row)
            if errs:
                errors_seen += 1
                print(f"[VALIDATION FAILURE] {rule_type}/{i:02d}: {errs}", file=sys.stderr)
                continue
            path = outdir / f"{rule_type}_{i:02d}_{row['rule_id']}.json"
            with open(path, "w") as f:
                json.dump(row, f, sort_keys=True, indent=2)
                f.write("\n")
            total += 1
    print(f"Wrote {total} synthetic rule instances across {len(ALL)} types. Validation errors: {errors_seen}")
    return errors_seen == 0


if __name__ == "__main__":
    ok = build_and_write()
    sys.exit(0 if ok else 1)
