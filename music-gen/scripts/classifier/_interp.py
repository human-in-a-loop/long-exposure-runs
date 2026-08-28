"""Interpreter guard — every classifier script imports this first.

The workspace's ML stack (librosa, torch, panns_inference, tensorflow)
lives at /usr/bin/python3, NOT the harness venv. Wrong interpreter =
opaque import errors 5 minutes into a run. Fail fast, fail loud.
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


# Run at import time so the fail-fast is unavoidable.
assert_system_python()
