#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-09-03T00:00:00Z
# cycle: 1
# run_id: run-2026-09-03T000000Z
# agent: worker
# milestone: M-V4-PROFILES/cg-bass-sweep-launched
# ---
"""CLI --help returns 0 for the sweep entrypoint (no live rendering)."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]


def test_coarse_sweep_help_returns_0():
    r = subprocess.run(
        ["/usr/bin/python3", "-m", "scripts.sound_match.coarse_sweep_sf2", "--help"],
        cwd=str(REPO),
        capture_output=True,
    )
    assert r.returncode == 0, (
        r.returncode, r.stderr.decode(errors="replace")[:400]
    )
    out = r.stdout.decode()
    assert "--presets" in out
    assert "--reference-stem" in out
    assert "--sf2" in out
    print("PASS test_coarse_sweep_help_returns_0")


if __name__ == "__main__":
    test_coarse_sweep_help_returns_0()
    print("OK")
