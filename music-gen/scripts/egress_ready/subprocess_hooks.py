"""Single injection point for the four downstream subprocess calls.

Tests subclass SubprocessHooks and override any of the four run_* methods
with no-op fakes. The state machine only ever calls hooks through the
SubprocessHooks instance it was constructed with; no direct subprocess.run
lives in state.py.

created: 2026-08-28
cycle: 8
milestone: M-INGEST-1/egress-ready-automation
"""
from __future__ import annotations

import sys
assert sys.executable == "/usr/bin/python3", (
    f"scripts/egress_ready expects /usr/bin/python3, got {sys.executable}"
)

import json
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional


# Module-level constants: the exact argv strings the state machine will run
# in production. Encoded here so the integration test can assert their
# stability as a single-source-of-truth. Sibling refactors must update
# these in ONE place.
HARVEST_CMD: List[str] = ["bash", "workspace/harvest_playlists.sh"]
CHUNKER_CMD: List[str] = [
    "/usr/bin/python3",
    "-m",
    "scripts.ingest.chunker",
    "--manifest",
    "data/ratings/ratings_manifest.tsv",
    "--out",
    "data/chunks/rated/",
]
CLASSIFIER_CMD: List[str] = [
    "/usr/bin/python3",
    "-m",
    "scripts.classifier.classify_batch",
    "--clips",
    "data/chunks/rated/",
    "--out",
    "data/class/rated/",
]
READY_FLAG_PATH = "data/ear/rated_ready.flag"
STDERR_TAIL_BYTES = 4096


@dataclass
class HookResult:
    ok: bool
    stderr_tail: str
    duration_s: float
    returncode: Optional[int] = None


class SubprocessHooks:
    """Default production implementations. Tests inject a mock subclass."""

    def __init__(self, cwd: Optional[Path] = None):
        self.cwd = Path(cwd) if cwd is not None else Path.cwd()

    def _run(self, cmd: List[str]) -> HookResult:
        t0 = time.monotonic()
        try:
            proc = subprocess.run(
                cmd,
                cwd=str(self.cwd),
                capture_output=True,
                text=True,
                check=False,
            )
            stderr_tail = (proc.stderr or "")[-STDERR_TAIL_BYTES:]
            return HookResult(
                ok=(proc.returncode == 0),
                stderr_tail=stderr_tail,
                duration_s=time.monotonic() - t0,
                returncode=proc.returncode,
            )
        except Exception as e:
            return HookResult(
                ok=False,
                stderr_tail=f"exception: {type(e).__name__}: {e}"[-STDERR_TAIL_BYTES:],
                duration_s=time.monotonic() - t0,
                returncode=None,
            )

    def run_harvest(self) -> HookResult:
        return self._run(HARVEST_CMD)

    def run_chunker(self) -> HookResult:
        return self._run(CHUNKER_CMD)

    def run_classifier(self) -> HookResult:
        return self._run(CLASSIFIER_CMD)

    def write_ready_flag(self) -> HookResult:
        t0 = time.monotonic()
        try:
            flag = self.cwd / READY_FLAG_PATH
            flag.parent.mkdir(parents=True, exist_ok=True)
            flag.touch()
            sidecar = flag.with_suffix(".flag.json")
            sidecar.write_text(json.dumps({
                "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "harvest_cmd": HARVEST_CMD,
                "chunker_cmd": CHUNKER_CMD,
                "classifier_cmd": CLASSIFIER_CMD,
                "note": "M-EAR-1 training now has its rated audio ready.",
            }, indent=2) + "\n", encoding="utf-8")
            return HookResult(ok=True, stderr_tail="", duration_s=time.monotonic() - t0, returncode=0)
        except Exception as e:
            return HookResult(
                ok=False,
                stderr_tail=f"exception: {type(e).__name__}: {e}"[-STDERR_TAIL_BYTES:],
                duration_s=time.monotonic() - t0,
                returncode=None,
            )
