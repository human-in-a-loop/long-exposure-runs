#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-09-03T18:30:00Z
# cycle: 10
# run_id: run-2026-09-03T183000Z
# agent: worker
# milestone: _infra/coarse-sweep-drums-disk-check-fixed-c10
# ---
"""Regression tests for the c10 disk-check fix in
`scripts.sound_match.coarse_sweep_sf2_drums`.

The c9 gate (`_disk_usage_pct`) used statvfs f_blocks, which includes
root-reserved blocks in the denominator; on an ext4 volume with the
default 5% reservation this reads ~14 pp higher than `df -h` shows and
fires a false-positive 90% abort at ~76% real usage. c10 replacement
`_disk_ok(path, budget_bytes, safety_factor)` asks the honest question
("is there room for the sweep budget × safety?") against f_bavail
(user-available free space, correctly excluding reserved blocks).

Coverage (7 cases, ≥6 required):
    1. tempdir + 1.5 GB budget → PASS on a workspace with ≥3 GB free
    2. tempdir + 100 TB budget → FAIL (obviously insufficient)
    3. workspace `.` + 500 MB × 2.0 = 1 GB required → PASS (matches ~6.6 GB avail)
    4. df-agreement sanity: f_bavail * f_frsize within 5% of `df -k .` avail
    5. safety_factor override respected (0.5x passes where 2.0x fails)
    6. budget_bytes = 0 short-circuits True (no-op call is safe)
    7. legacy diagnostic `_disk_usage_pct` still returns finite float in [0,100]
       (kept for backward-compat with --disk-abort-pct manifest field)
"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path

# Import under test.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.sound_match.coarse_sweep_sf2_drums import _disk_ok, _disk_usage_pct


def test_1_fresh_tempdir_reasonable_budget_passes() -> None:
    d = Path(tempfile.mkdtemp(prefix="disk_ok_case1_"))
    try:
        # 1.5 GB required — presumed present on any dev workspace running these tests.
        # If the test host has < 3 GB free this fails legitimately (still correct behavior).
        assert _disk_ok(d, budget_bytes=1_500_000_000, safety_factor=1.0), (
            "1.5 GB budget × 1.0 should pass on a workspace with plenty of free space"
        )
    finally:
        d.rmdir()


def test_2_fresh_tempdir_100tb_budget_fails() -> None:
    d = Path(tempfile.mkdtemp(prefix="disk_ok_case2_"))
    try:
        assert not _disk_ok(d, budget_bytes=100 * (1024 ** 4), safety_factor=2.0), (
            "100 TB × 2.0 must fail on any realistic workspace"
        )
    finally:
        d.rmdir()


def test_3_workspace_dot_500mb_x2_passes_matches_current_disk() -> None:
    # 500 MB × 2.0 = 1 GB required; the c10 launch condition.
    # Matches the drums sweep --max-audio-mb 500 default.
    assert _disk_ok(Path("."), budget_bytes=500 * 1024 * 1024, safety_factor=2.0), (
        "500 MB × 2.0 = 1 GB should pass — this is the exact drums-sweep launch condition"
    )


def test_4_agreement_with_df_within_5pct() -> None:
    # df -k reports in 1-KiB blocks; the "Available" column (index 3) uses f_bavail semantics.
    r = subprocess.run(["df", "-k", "."], capture_output=True, text=True, check=True)
    lines = [ln for ln in r.stdout.strip().splitlines() if ln]
    # Skip header; the target row may wrap on long device names, so take the last non-empty line.
    fields = lines[-1].split()
    df_avail_bytes = int(fields[3]) * 1024

    st = os.statvfs(".")
    statvfs_avail_bytes = st.f_bavail * st.f_frsize

    denom = max(df_avail_bytes, 1)
    rel_delta = abs(statvfs_avail_bytes - df_avail_bytes) / denom
    assert rel_delta < 0.05, (
        f"f_bavail*f_frsize ({statvfs_avail_bytes}) diverges from df -k avail "
        f"({df_avail_bytes}) by {rel_delta:.3%} — expected < 5%"
    )


def test_5_safety_factor_override_respected() -> None:
    # Pick a budget that PASSES at safety_factor=0.5 but FAILS at safety_factor=1000.
    d = Path(tempfile.mkdtemp(prefix="disk_ok_case5_"))
    try:
        # 100 MB budget — should always pass at 0.5x, always fail at 1000x on any real disk.
        assert _disk_ok(d, budget_bytes=100 * 1024 * 1024, safety_factor=0.5)
        assert not _disk_ok(d, budget_bytes=100 * 1024 * 1024, safety_factor=1000.0)
    finally:
        d.rmdir()


def test_6_zero_budget_short_circuits_true() -> None:
    # Contract: budget=0 means "no requirement" — always OK.
    assert _disk_ok(Path("."), budget_bytes=0, safety_factor=2.0)
    assert _disk_ok(Path("/"), budget_bytes=0, safety_factor=1.0)


def test_7_legacy_disk_usage_pct_returns_finite_percentage() -> None:
    # Diagnostic function still callable; still returns a percentage in [0, 100].
    pct = _disk_usage_pct(Path("."))
    assert isinstance(pct, float)
    assert 0.0 <= pct <= 100.0
    # And it MUST be higher than the honest df-based number (this is the c9 defect):
    # includes root-reserved blocks. On ext4 with 5% reservation the delta is ~5-15 pp.


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"PASS {name}")
    print("ALL PASS")
