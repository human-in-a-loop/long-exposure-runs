#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-09-04T06:00:00Z
# cycle: 20
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-V4-RULES-1/scaffold-c20
# purpose: c20 Track 1 scaffold-only package init for M-V4-RULES-1. Any
#          call raises NotImplementedError('c21+ substantive implementation')
#          per campaign prompt v4 rules doctrine (two models in parallel:
#          A statistical style model, B lightweight learned sequence model).
# ---
"""M-V4-RULES-1 scaffold (c20).

Per campaign prompt (docs/specs/v4_rules_and_ear_spec.md when landed):
two rules models remain available to the generator — (A) statistical
style model over canonical MIDI + tempo maps + audio descriptors; (B)
lightweight learned sequence model (CA bar-transition first, VOMM
comparison). Retain CA unless it clearly fails.

Scaffold contract for cycle 20 (per c19 audit brief Track 3 promotion
to c20 Track 1):
    * Both `extract_v4:extract_rules_v4` and any exported entry point
      raise NotImplementedError('c21+ substantive implementation').
    * No PRNG imports (AST-scannable).
    * No `sidecar_nonfactor` imports.
    * No VST3 state APIs (`get_state`, `save_state`, `save_preset`,
      `load_state`, `set_state`).
    * `/usr/bin/python3` interpreter guard on every top-level script.

READ-ONLY citation anchors (M-V3-RULES-1 c23 clone-2, per campaign
POR M-V3-RULES-1/first-activation validated/high):
    * scripts/v3_rules/extract_rules.py (sha 9af3e37cfbe3338f...)
    * data/v3/rules/rules_artifact.jsonl  (sha e19fb205b282dabb...,
      76 v3-rendered corpus rules across 5 doctrine categories)

Substantive extraction (Model A + Model B) is c21+ scope. This module
is scaffold-only and intentionally raises on call.
"""
from __future__ import annotations

__all__ = ("extract_rules_v4",)

_CYCLE = 20
_SCAFFOLD_ONLY = True
_C21_PLUS_DEFERRAL_MESSAGE = "c21+ substantive implementation"


def extract_rules_v4(*args, **kwargs):  # noqa: D401 - stub
    """Scaffold stub. Raises NotImplementedError until c21+."""
    raise NotImplementedError(_C21_PLUS_DEFERRAL_MESSAGE)
