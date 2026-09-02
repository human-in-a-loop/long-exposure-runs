#!/usr/bin/python3
# ---
# created: 2026-09-02T00:00:00Z
# cycle: 58
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-V3-SPINE
# ---
"""MuScriptor instrument-label → GM program lookup for the v3 spine.

MuScriptor emits one track per detected instrument, with a label drawn from
its fixed group vocabulary (`muscriptor list-instruments`, 35 entries).
This module maps every MuScriptor label to a General MIDI program (0..127),
and flags drums which are dispatched to MIDI channel 10 (program is
ignored for that channel in GM).

Fixed decisions honored:
- FD1 (per-stem MuScriptor + recombine): we get a label per detected
  instrument regardless of stem.
- FD3 (GM render with drums ch10): drums → channel 10; every other label
  → an explicit GM program.
- Never default to GM 4 (Electric Piano 1) — that's the RC4 failure mode.

A missing label raises `UnknownInstrumentError` so the pipeline reports the
gap honestly instead of silently mapping to the wrong instrument.

READ-ONLY sibling of scripts/recreate_v2/rc4_v2_gm_program_map.py (which is
a stub only). This module extends the map for MuScriptor's group vocabulary.
"""
from __future__ import annotations

import sys

if sys.executable != "/usr/bin/python3":
    raise RuntimeError(f"gm_program_map_v3 requires /usr/bin/python3 (got {sys.executable})")


class UnknownInstrumentError(ValueError):
    """Raised when a MuScriptor label has no GM mapping."""


# Every entry: MuScriptor group label → (gm_program, is_drum, gm_name).
# Programs picked from the GM Level-1 spec (bank 0). Selections aim for
# the most recognizable timbre inside each MuScriptor group.
GM_PROGRAM_MAP: dict[str, tuple[int, bool, str]] = {
    "acoustic_piano":            (0,   False, "Acoustic Grand Piano"),
    "electric_piano":            (4,   False, "Electric Piano 1"),
    "chromatic_percussion":      (11,  False, "Vibraphone"),
    "organ":                     (17,  False, "Percussive Organ"),
    "acoustic_guitar":           (24,  False, "Acoustic Guitar (nylon)"),
    "clean_electric_guitar":     (27,  False, "Electric Guitar (clean)"),
    "distorted_electric_guitar": (30,  False, "Distortion Guitar"),
    "acoustic_bass":             (32,  False, "Acoustic Bass"),
    "electric_bass":             (33,  False, "Electric Bass (finger)"),
    "violin":                    (40,  False, "Violin"),
    "viola":                     (41,  False, "Viola"),
    "cello":                     (42,  False, "Cello"),
    "contrabass":                (43,  False, "Contrabass"),
    "orchestral_harp":           (46,  False, "Orchestral Harp"),
    "timpani":                   (47,  False, "Timpani"),
    "string_ensemble":           (48,  False, "String Ensemble 1"),
    "synth_strings":             (50,  False, "SynthStrings 1"),
    "voice":                     (52,  False, "Choir Aahs"),
    "orchestra_hit":             (55,  False, "Orchestra Hit"),
    "trumpet":                   (56,  False, "Trumpet"),
    "trombone":                  (57,  False, "Trombone"),
    "tuba":                      (58,  False, "Tuba"),
    "french_horn":               (60,  False, "French Horn"),
    "brass_section":             (61,  False, "Brass Section"),
    "soprano_and_alto_sax":      (64,  False, "Soprano Sax"),
    "tenor_sax":                 (66,  False, "Tenor Sax"),
    "baritone_sax":              (67,  False, "Baritone Sax"),
    "oboe":                      (68,  False, "Oboe"),
    "english_horn":              (69,  False, "English Horn"),
    "bassoon":                   (70,  False, "Bassoon"),
    "clarinet":                  (71,  False, "Clarinet"),
    "flutes":                    (73,  False, "Flute"),
    "synth_lead":                (80,  False, "Lead 1 (square)"),
    "synth_pad":                 (88,  False, "Pad 1 (new age)"),
    "drums":                     (0,   True,  "Standard Drum Kit (channel 10)"),
}

# Stem name → MuScriptor `--instruments` whitelist (comma-separated).
# Vocals stem is transcribed (per operator D2) but not synthesized in the
# instrumental render (hybrid overlay path).
STEM_WHITELIST: dict[str, str] = {
    "drums":  "drums",
    "bass":   "acoustic_bass,electric_bass",
    "guitar": "acoustic_guitar,clean_electric_guitar,distorted_electric_guitar",
    "piano":  "acoustic_piano,electric_piano,organ",
    "other":  ",".join([
        "chromatic_percussion", "orchestral_harp", "timpani",
        "string_ensemble", "synth_strings", "orchestra_hit",
        "trumpet", "trombone", "tuba", "french_horn", "brass_section",
        "soprano_and_alto_sax", "tenor_sax", "baritone_sax",
        "oboe", "english_horn", "bassoon", "clarinet", "flutes",
        "synth_lead", "synth_pad",
    ]),
    "vocals": "voice",
}


def lookup(label: str) -> tuple[int, bool, str]:
    """Return (program, is_drum, gm_name) for a MuScriptor label. Raises on unknown."""
    if label not in GM_PROGRAM_MAP:
        raise UnknownInstrumentError(
            f"MuScriptor label {label!r} not in GM_PROGRAM_MAP; extend this table before rendering"
        )
    return GM_PROGRAM_MAP[label]


def whitelist_for(stem: str) -> str:
    if stem not in STEM_WHITELIST:
        raise KeyError(f"unknown stem {stem!r}; known: {sorted(STEM_WHITELIST)}")
    return STEM_WHITELIST[stem]


if __name__ == "__main__":
    for name, (prog, drum, gm_name) in sorted(GM_PROGRAM_MAP.items()):
        marker = "DRUMS/ch10" if drum else f"program {prog:3d}"
        print(f"{name:30s} → {marker:14s}  {gm_name}")
