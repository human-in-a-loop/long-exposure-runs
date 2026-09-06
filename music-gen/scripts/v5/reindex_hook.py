#!/usr/bin/python3
"""c81 P0.5 — post-canonicalize reindex hook + sidecar writer (lossless at birth).

created: 2026-09-06T17:00:00Z
cycle: 81
run_id: run-2026-09-06T000000Z
agent: worker
milestone: M-V5-CORPUS-1/reindex-hygiene-c81

Closes the c80 gap: the c79 driver's canonicalize stage composes the READ-ONLY
c22 chunk merge + c4 index-keyed serializer and therefore writes the LOSSY
`canonical_midi_full/`. This module is called by `transcribe_full_length.py`
immediately after canonicalize (additive call; READ-ONLY modules untouched) so
every later landing is re-indexed at birth into `canonical_v5_reindexed/` and
carries the additive sidecar `canonical_v5_reindexed_sha256.json` next to
`transcription_manifest.json`. The c79/c80 manifests' bytes are never rewritten.

Because PID 5201 runs the OLD driver image, the hook only takes effect on a
natural restart; `reindex_landed(...)` is the idempotent catch-up loop that
covers landings until then (c81 P0.2).

Discipline: /usr/bin/python3 guard (suppressible for tests); no PRNG; no
sidecar_nonfactor; no VST3 state APIs.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path

if sys.executable != "/usr/bin/python3" and "SUPPRESS_INTERPRETER_GUARD" not in os.environ:
    print(f"FATAL: expected /usr/bin/python3, got {sys.executable}", file=sys.stderr)
    sys.exit(2)

_WS = Path(__file__).resolve().parent.parent.parent
if str(_WS) not in sys.path:
    sys.path.insert(0, str(_WS))
from scripts.v5.reindex_canonical_v5 import process_song, PROBES, OUT_SUBDIR  # noqa: E402

SIDECAR_NAME = "canonical_v5_reindexed_sha256.json"
HOOK_VERSION = "c81.1"


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def write_sidecar(sha16: str, corpus: Path) -> dict:
    """Additive sidecar next to transcription_manifest.json: per-stem reindexed MIDI SHAs + reindex_manifest SHA."""
    d = corpus / sha16
    rd = d / OUT_SUBDIR
    rm = rd / "reindex_manifest.json"
    if not rm.exists():
        raise FileNotFoundError(f"MISSING_REINDEX: {rm} absent for {sha16}")
    tm = d / "transcription_manifest.json"
    try:
        rd_rel = str(rd.resolve().relative_to(_WS))
    except ValueError:  # fixture corpus outside the workspace (tests)
        rd_rel = str(rd)
    side = {
        "schema_version": 1, "hook_version": HOOK_VERSION, "sha16": sha16,
        "reindexed_dir": rd_rel,
        "reindex_manifest_sha256": sha(rm),
        "transcription_manifest_sha256": sha(tm) if tm.exists() else None,
        "midi_sha256": {p: sha(rd / f"{p}.mid") for p in PROBES if (rd / f"{p}.mid").exists()},
        "reindexed_json_sha256": {p: sha(rd / f"{p}.reindexed.json") for p in PROBES if (rd / f"{p}.reindexed.json").exists()},
        "note": "additive sidecar; the c79/c80 transcription_manifest.json bytes are never rewritten; consumers read canonical_v5_reindexed/",
    }
    (d / SIDECAR_NAME).write_text(json.dumps(side, sort_keys=True, indent=2) + "\n")
    return side


def post_canonicalize(sha16: str, corpus: Path | str = "data/v5/corpus") -> dict:
    """Hook called by the driver right after its canonicalize stage: reindex + sidecar."""
    corpus = Path(corpus)
    rec = process_song(sha16, corpus)
    side = write_sidecar(sha16, corpus)
    return {"reindex": {p: {k: v for k, v in s.items() if k in ("n_starts_in", "n_paired", "n_unpaired_starts")}
                        for p, s in rec["probes"].items()}, "sidecar": side}


def reindex_landed(corpus: Path | str = "data/v5/corpus", force: bool = False) -> list:
    """Idempotent catch-up: every song with transcription_manifest.json and no reindex_manifest.json (or no sidecar)."""
    corpus = Path(corpus)
    out = []
    for tm in sorted(corpus.glob("*/transcription_manifest.json")):
        s = tm.parent.name
        have_r = (tm.parent / OUT_SUBDIR / "reindex_manifest.json").exists()
        have_s = (tm.parent / SIDECAR_NAME).exists()
        if force or not have_r:
            post_canonicalize(s, corpus)
            out.append((s, "reindexed+sidecar"))
        elif not have_s:
            write_sidecar(s, corpus)
            out.append((s, "sidecar"))
        else:
            out.append((s, "present"))
    return out


if __name__ == "__main__":
    os.chdir(_WS)
    for s, what in reindex_landed():
        print(f"{s}: {what}")
