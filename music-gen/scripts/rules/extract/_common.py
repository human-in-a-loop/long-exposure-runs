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


# ---------------------------------------------------------------------------
# Extraction context (cycle-12, M-RULES-1/extraction/breadth-seeds).
#
# The default context points at the frozen cycle-9 synth_030s inputs
# (SCORE_PATH + BP_DIR above). The breadth-seed orchestrator temporarily
# overrides this via ``set_extraction_context()`` so extractors emit
# provenance_pointers keyed to the alternate seed's merged.musicxml and
# per-stem basic-pitch JSONLs. When ``reset_extraction_context()`` is
# called (or the context was never set) behavior is byte-identical to
# cycle-9 — the cycle-9 anchor rule_ids remain reproducible.
# ---------------------------------------------------------------------------

_ACTIVE_SCORE_PATH: Path = SCORE_PATH
_ACTIVE_BP_DIR: Path = BP_DIR
_ACTIVE_SEED_NAME: str = "synth_030s"


def set_extraction_context(seed_name: str, score_path, bp_dir) -> None:
    """Redirect ``transcription_event_id`` to alternate seed inputs."""
    global _ACTIVE_SCORE_PATH, _ACTIVE_BP_DIR, _ACTIVE_SEED_NAME
    _ACTIVE_SCORE_PATH = Path(score_path)
    _ACTIVE_BP_DIR = Path(bp_dir)
    _ACTIVE_SEED_NAME = str(seed_name)


def reset_extraction_context() -> None:
    """Restore cycle-9 default context (synth_030s)."""
    global _ACTIVE_SCORE_PATH, _ACTIVE_BP_DIR, _ACTIVE_SEED_NAME
    _ACTIVE_SCORE_PATH = SCORE_PATH
    _ACTIVE_BP_DIR = BP_DIR
    _ACTIVE_SEED_NAME = "synth_030s"


def active_seed_name() -> str:
    return _ACTIVE_SEED_NAME


def transcription_event_id(tag: str) -> str:
    """Deterministic 32-hex id derived from stem/source content sha.

    Resolvability: given the stem tag we recompute the same value.

    The path resolution honors the currently-active extraction context.
    When no context has been set, defaults match cycle-9 synth_030s
    (SCORE_PATH / BP_DIR) — byte-identical anchor reproduction.
    """
    if tag in STEMS:
        p = _ACTIVE_BP_DIR / f"{tag}.jsonl"
    elif tag == "score":
        p = _ACTIVE_SCORE_PATH
    else:
        raise ValueError(f"unknown transcription tag: {tag}")
    if not p.exists():
        raise FileNotFoundError(str(p))
    sha = file_sha256(p)
    return hashlib.sha256(f"transcription::{tag}::{sha}".encode("utf-8")).hexdigest()[:32]


class NullWithReason:
    """Marker returned by extractors when content is incompatible.

    Not emitted to the ledger; consumed by the orchestrator to populate
    ``breadth_expansion_summary.json`` honestly rather than fabricating a
    fake rule row.
    """

    __slots__ = ("rule_type", "reason", "detail")

    def __init__(self, rule_type: str, reason: str, detail: str = ""):
        self.rule_type = rule_type
        self.reason = reason
        self.detail = detail

    def to_dict(self) -> dict:
        return {"rule_type": self.rule_type, "reason": self.reason, "detail": self.detail}


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
