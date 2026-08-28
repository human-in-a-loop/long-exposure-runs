"""Interpreter guard — every ear script imports this first.

The workspace's ML stack (torch, panns_inference, librosa) lives at
/usr/bin/python3, not the harness venv. Wrong interpreter = opaque
import errors five minutes into a run. Fail fast, fail loud.
"""
from __future__ import annotations
import sys

REQUIRED = "/usr/bin/python3"


def assert_system_python() -> None:
    if sys.executable != REQUIRED:
        raise SystemExit(
            f"WRONG INTERPRETER: sys.executable={sys.executable!r}, "
            f"required={REQUIRED!r}. "
            f"Re-run as: /usr/bin/python3 {' '.join(sys.argv)}"
        )


assert_system_python()
