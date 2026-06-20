"""Ad-hoc auditor verification — confirms default telemetry_path is cwd-invariant.
Not part of the standard pytest run; intended for one-shot manual execution.
"""
import os
import sys
from pathlib import Path

HARNESS_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HARNESS_ROOT))

from harness.client import FMClient, _DEFAULT_TELEMETRY_PATH

print("default path:", _DEFAULT_TELEMETRY_PATH)
print("is absolute:", _DEFAULT_TELEMETRY_PATH.is_absolute())
print("exists:", _DEFAULT_TELEMETRY_PATH.exists())

c = FMClient(cycle_id="cycle-2-smoke-demo")
expected = 6e-05 + 3e-05 + 2.9e-05 + 0.0
print("replay spent (cwd=workspace):", c.spent_usd, "expected:", expected)
print("replay correct:", abs(c.spent_usd - expected) < 1e-10)

# Switch cwd; new client should still see the canonical telemetry.
os.chdir("/tmp")
c2 = FMClient(cycle_id="cycle-2-smoke-demo")
print("replay spent (cwd=/tmp):", c2.spent_usd)
print("cwd-invariant:", abs(c2.spent_usd - c.spent_usd) < 1e-12)
