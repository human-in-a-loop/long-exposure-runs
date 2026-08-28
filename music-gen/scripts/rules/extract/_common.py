#!/usr/bin/env python3
# M-RULES-1/extraction — shared helpers.
#
# Author: cyd7bevdr@mozmail.com, cycle 9 (fork f1bae241bde9 / clone-0).
#
# Non-factor AST isolation: this module MUST NOT import
# scripts.classifier.sidecar_nonfactor.

import hashlib
import sys
from pathlib import Path

assert sys.executable == "/usr/bin/python3", f"expected /usr/bin/python3, got {sys.executable}"

_HERE = Path(__file__).resolve().parent
REPO = _HERE.parent.parent.parent  # extract -> rules -> scripts -> repo

# The frozen inputs on disk (M-SCORE-1/merged-full-song deliverable +
# M-TRANS-1/basic-pitch cycle-6 outputs).
SCORE_PATH = REPO / "data" / "score" / "merged_synth030s.musicxml"
BP_DIR = REPO / "data" / "transcribe" / "basic_pitch" / "synth_030s"
STEMS = ("drums", "bass", "other")

# Fixed run timestamp so byte-identical re-runs produce byte-identical
# ledger appends. The rule_id itself is content-derived; ts is a
# constant chosen once for this cycle.
FIXED_TS = "2026-08-28T10:30:00Z"

# Fixed tempo/meter defaults for the seed (probed 2026-08-28: F major,
# 4/4, 120 BPM constant). Extractors may override via score inspection.
DEFAULT_TEMPO_BPM = 120.0
DEFAULT_METER = "4/4"


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def transcription_event_id(tag: str) -> str:
    """Deterministic 32-hex id derived from stem/source content sha.

    Resolvability: given the stem tag we recompute the same value.
    """
    if tag in STEMS:
        p = BP_DIR / f"{tag}.jsonl"
    elif tag == "score":
        p = SCORE_PATH
    else:
        raise ValueError(f"unknown transcription tag: {tag}")
    if not p.exists():
        raise FileNotFoundError(str(p))
    sha = file_sha256(p)
    return hashlib.sha256(f"transcription::{tag}::{sha}".encode("utf-8")).hexdigest()[:32]


def clip_id(tag: str) -> str:
    """Deterministic 16-hex clip id (informational; not required by schema)."""
    return hashlib.sha256(f"clip::{tag}".encode("utf-8")).hexdigest()[:16]


def event_id_for(rule_id: str) -> str:
    """32-hex event_id derived from rule_id — deterministic."""
    return hashlib.sha256(f"event::{rule_id}".encode("utf-8")).hexdigest()[:32]


def measure_to_seconds(measure: int, tempo_bpm: float = DEFAULT_TEMPO_BPM,
                       beats_per_measure: int = 4) -> float:
    """Convert 0-indexed measure number to seconds (4/4, quarter-note beat)."""
    seconds_per_beat = 60.0 / tempo_bpm
    return round(measure * beats_per_measure * seconds_per_beat, 6)


def part_group(part_id: str) -> str:
    """Map a MusicXML part id like 'bass__v1' to its instrument group."""
    if part_id.startswith("bass"):
        return "bass"
    if part_id.startswith("drums"):
        return "drums"
    if part_id.startswith("other"):
        return "other"
    return "unknown"
