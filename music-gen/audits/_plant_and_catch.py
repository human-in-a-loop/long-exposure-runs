"""Auditor plant-and-catch for M-HEUR-1 isolation test.

Planted violation into scripts/heuristics/battery.py, runs the isolation
test to confirm it FAILS, restores the file, re-runs to confirm PASS.
Ephemeral verification helper (kept under audits/ per STRUCTURE.md).
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BATTERY = ROOT / "scripts" / "heuristics" / "battery.py"
TEST = ROOT / "tests" / "test_heuristics_isolation.py"


def main() -> int:
    orig = BATTERY.read_text()
    plant = "from scripts.classifier import sidecar_nonfactor  # AUDITOR-PLANT\n"
    try:
        BATTERY.write_text(plant + orig)
        r = subprocess.run(
            ["/usr/bin/python3", str(TEST)], capture_output=True, text=True
        )
        planted_rc = r.returncode
        planted_out = r.stdout
    finally:
        BATTERY.write_text(orig)
    r2 = subprocess.run(
        ["/usr/bin/python3", str(TEST)], capture_output=True, text=True
    )
    print("=== planted run ===")
    print("exit", planted_rc)
    for line in planted_out.splitlines()[:10]:
        print("  ", line)
    print("=== post-restore run ===")
    print("exit", r2.returncode)
    print("  ", r2.stdout.splitlines()[0] if r2.stdout else "")
    ok = (planted_rc != 0) and (r2.returncode == 0)
    print("AUDITOR VERDICT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
