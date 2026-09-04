#!/usr/bin/python3
# ---
# created: 2026-09-04T00:00:00Z
# cycle: 16
# run_id: run-2026-09-04T110000Z
# agent: worker
# milestone: _infra/adopt-cycle14-guitar-stage2-tests-c16-fillin
# ---
"""c16 Track 4 test debt closure for c14 audibility measurement.

Regression pins on c14 piano/other audibility JSONs (per-metric values +
verdict_audible + env_pin_sha256). Orthogonal to embedding-metric-
semantics diagnosis: audibility measurement is a physical dBFS/LUFS
measurement, independent of any Track 1 sign-convention outcome.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUD = ROOT / "data" / "v4" / "profiles" / "31a164f845f8e27e" / "audibility"

ANCHORS = {
    "piano_stem_audibility.json": (
        "af5bb2c03547ca0bf0e677ed3bce800e587f6d2b389b12d3d36c9f729c99d250"
    ),
    "other_stem_audibility.json": (
        "5cc28e7f83c2d7ec6ab9c01e240720c929c4fc8b22c0ad858c88a3c84b46839c"
    ),
}
SCRIPT_ANCHOR = (
    "c40b76e4f7f1af7cebb092a8a4eba474fddd241d8e959d386ce4fac0ede08952"
)


def _sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def test_anchor_sha_regressions():
    for rel, expected in ANCHORS.items():
        assert _sha256(AUD / rel) == expected, f"{rel} SHA drift"


def test_script_sha_readonly():
    p = ROOT / "scripts" / "sound_match" / "measure_stem_audibility.py"
    assert _sha256(p) == SCRIPT_ANCHOR


def test_piano_metrics():
    d = json.loads((AUD / "piano_stem_audibility.json").read_text())
    assert abs(d["rms_dbfs"] - (-81.52990202958773)) < 1e-9
    assert abs(d["peak_dbfs"] - (-55.823481307178575)) < 1e-9
    assert d["verdict_audible"] is False


def test_other_metrics():
    d = json.loads((AUD / "other_stem_audibility.json").read_text())
    assert abs(d["rms_dbfs"] - (-81.7277244656143)) < 1e-9
    assert abs(d["peak_dbfs"] - (-49.13288896567622)) < 1e-9
    assert d["verdict_audible"] is False


def test_both_env_pin_recorded():
    for rel in ANCHORS:
        d = json.loads((AUD / rel).read_text())
        assert d.get("env_pin_sha256"), f"{rel} missing env_pin_sha256"


def test_no_prng_in_measurement_script():
    src = (ROOT / "scripts" / "sound_match" / "measure_stem_audibility.py"
           ).read_text()
    assert not re.search(r"^\s*import\s+random\b", src, re.MULTILINE)
    # Look for actual import statements only, not docstring mentions
    assert not re.search(
        r"^\s*(from|import)\s+.*sidecar_nonfactor\b", src, re.MULTILINE
    )


TESTS = [
    test_anchor_sha_regressions,
    test_script_sha_readonly,
    test_piano_metrics,
    test_other_metrics,
    test_both_env_pin_recorded,
    test_no_prng_in_measurement_script,
]


def main() -> int:
    fails = 0
    for t in TESTS:
        try:
            t()
            print(f"PASS {t.__name__}")
        except AssertionError as e:
            fails += 1
            print(f"FAIL {t.__name__}: {e}")
    print(f"\n{len(TESTS) - fails}/{len(TESTS)} tests passed")
    return 0 if fails == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
