#!/usr/bin/python3
"""c84 P0.2 — shared content-gate refusal for the v5 rules scripts (harmony_v5 / groove_v5 / groove_v5_v2).

created: 2026-09-09T21:00:00Z
cycle: 84
run_id: run-2026-09-06T000000Z
agent: worker
milestone: M-V5-CORPUS-1/content-gate-c84

Reads data/v5/corpus/content_blocked.json (written by scripts/v5/content_gate_v5.py from the pre-registered rules) and
raises ContentBlockedError BEFORE any MIDI of a blocked song is read — the same shape as the tempo-blocked refusal
(recanonicalization_blocked.json). Absent file -> no content block (the gate has not been run); callers record that.
Discipline: /usr/bin/python3 guard (suppressible for tests); no PRNG; no sidecar_nonfactor; no VST3 state APIs.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

if sys.executable != "/usr/bin/python3" and "SUPPRESS_INTERPRETER_GUARD" not in os.environ:
    print(f"FATAL: expected /usr/bin/python3, got {sys.executable}", file=sys.stderr)
    sys.exit(2)

CONTENT_BLOCKED_NAME = "content_blocked.json"


class ContentBlockedError(RuntimeError):
    """Raised when a rules script is asked to consume a NON-MUSIC song (c84 pre-registered content gate)."""


def load_content_blocked(corpus: Path | str = "data/v5/corpus") -> dict:
    p = Path(corpus) / CONTENT_BLOCKED_NAME
    if not p.exists():
        return {}
    return json.loads(p.read_text()).get("blocked_songs", {})


def refuse_if_content_blocked(songs, corpus: Path | str = "data/v5/corpus", who: str = "rules") -> None:
    blocked = load_content_blocked(corpus)
    refused = [s for s in songs if s in blocked]
    if refused:
        raise ContentBlockedError(f"CONTENT_BLOCKED: {who} must not consume non-music songs {refused} "
                                  f"({', '.join(str(blocked[s].get('verdict')) for s in refused)}; see {Path(corpus) / CONTENT_BLOCKED_NAME})")
