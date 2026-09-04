#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-09-04T06:00:00Z
# cycle: 20
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-V4-RULES-1/scaffold-c20
# purpose: c20 Track 1 scaffold-only extractor for M-V4-RULES-1. Any call
#          raises NotImplementedError('c21+ substantive implementation').
#          Follows c9 M-RULES-1/schema pattern + c23 M-V3-RULES-1 scaffold
#          pattern (READ-ONLY anchors cited in module docstring).
# ---
"""M-V4-RULES-1 extractor scaffold (c20).

STUB ONLY. Any invocation raises NotImplementedError; substantive
extraction is c21+ scope. This module establishes the extractor
surface expected by the c21+ implementation:

    extract_rules_v4(corpus_manifest, out_dir, *, env_pin_sha256) -> dict

Doctrine (from campaign prompt):
    * Model A — statistical style model over canonical MIDI + tempo
      maps + audio descriptors (per-song extraction, aggregated to
      typed rule rows across 5 categories: harmonic / rhythmic /
      melodic / form / arrangement).
    * Model B — lightweight learned sequence model (CA bar-transition
      first, VOMM comparison). Retain CA unless clearly fails.

READ-ONLY citation anchors (M-V3-RULES-1 c23 clone-2 first activation,
validated/high per POR M-V3-RULES-1/first-activation):
    * scripts/v3_rules/extract_rules.py         sha 9af3e37cfbe3338f...
    * data/v3/rules/rules_artifact.jsonl        sha e19fb205b282dabb...
      (76 v3-rendered corpus rules across the 5 doctrine categories)
    * data/v3/rules/rubric_hash.txt             sha 01... (three-way
      rubric_hash_v3_rules chain, held byte-equal at c23)

Substantive implementation deferred to c21+. See campaign prompt
`music_gen_v4_prompt.md` for the closure-milestone ordering
(M-V4-CERT → M-V4-PROFILES → M-V4-SHOWCASE → M-V4-RULES → M-V4-EAR
→ M-V4-GEN → M-V4-CLOSE).
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any

__all__ = (
    "extract_rules_v4",
    "list_corpus_songs",
    "compute_rule_id",
)

# Canonical 7-key env-pin (matches c17/c18/c19 v4 chain + c22 unified driver).
_CANONICAL_ENV_PIN_SHA = (
    "2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca"
)

_C21_PLUS_DEFERRAL_MESSAGE = "c21+ substantive implementation"

# Doctrine categories per campaign prompt v4 rules layer.
RULE_CATEGORIES = ("harmonic", "rhythmic", "melodic", "form", "arrangement")


def _assert_interpreter() -> None:
    """Interpreter guard per docs/interpreter_guard_policy.md (c13+)."""
    if sys.executable != "/usr/bin/python3":
        raise RuntimeError(
            f"interpreter guard: expected /usr/bin/python3, got {sys.executable}"
        )


def extract_rules_v4(
    corpus_manifest: Any = None,
    out_dir: Any = None,
    *,
    env_pin_sha256: str = _CANONICAL_ENV_PIN_SHA,
) -> dict:
    """Scaffold stub for M-V4-RULES-1 extraction.

    c21+ contract (documented; not implemented at c20):
        * Read corpus_manifest (list of song deliveries + tempo maps +
          per-stem canonical MIDIs).
        * For each song: run Model A (statistical) + Model B (CA
          sequence) extractors, emit typed rule rows.
        * Content-derived rule_id via SHA-256 of canonical-JSON params
          (matches c9 M-RULES-1/schema and c23 M-V3-RULES-1 shape).
        * Byte-deterministic ×2 given fixed env_pin_sha256.
        * Write `rules_artifact.jsonl` + `rules_artifact.sha256` under
          out_dir; parallel to c23 data/v3/rules/ layout.

    Raises:
        NotImplementedError: always (c20 scaffold).
    """
    raise NotImplementedError(_C21_PLUS_DEFERRAL_MESSAGE)


def list_corpus_songs(*args, **kwargs):
    """Scaffold stub. c21+ will enumerate the 4 operator-approved v3
    deliveries (CG + WIG + Rome + Disco A) plus any newly-accepted
    songs. See c23 CORPUS constant in scripts/v3_rules/extract_rules.py
    for the READ-ONLY predecessor shape."""
    raise NotImplementedError(_C21_PLUS_DEFERRAL_MESSAGE)


def compute_rule_id(*args, **kwargs):
    """Scaffold stub. c21+ will content-hash canonical-JSON of typed
    rule params via SHA-256 (matches c9 M-RULES-1/schema pattern)."""
    raise NotImplementedError(_C21_PLUS_DEFERRAL_MESSAGE)


def _canonical_env_pin_sha256() -> str:
    """Return the canonical 7-key env_pin_sha256 constant (audit-visible)."""
    return _CANONICAL_ENV_PIN_SHA


if __name__ == "__main__":
    _assert_interpreter()
    print("M-V4-RULES-1 scaffold (c20). Substantive implementation is c21+.")
    print(f"env_pin_sha256 = {_CANONICAL_ENV_PIN_SHA}")
    sys.exit(0)
