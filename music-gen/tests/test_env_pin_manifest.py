#!/usr/bin/env /usr/bin/python3
"""c22 M-V3-SPINE-2/env-pin-manifest invariant tests.

Ships >=8 cases covering: schema completeness, byte-det x2, self-anchor
sha computation, deterministic key ordering, drift-detectability
round-trip.

Runs directly via /usr/bin/python3; no pytest dependency.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import tempfile
from pathlib import Path

WS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WS))

from scripts.v3_spine.v3_pipeline.env_pin import (  # noqa: E402
    build_env_pin_manifest,
    write_env_pin,
)

FAILED: list[str] = []


def _fail(n: str, m: str) -> None:
    FAILED.append(f"[FAIL] {n}: {m}")


def _pass(n: str) -> None:
    print(f"[PASS] {n}")


def test_01_schema_has_all_required_keys() -> None:
    m = build_env_pin_manifest()
    required = {"schema_version", "python", "torch", "numpy", "librosa",
                "mido", "soundfile", "scipy", "muscriptor", "htdemucs",
                "soundfont", "fluidsynth", "model_safetensors", "env",
                "env_pin_sha256"}
    missing = required - set(m)
    if missing:
        return _fail("01_schema_has_all_required_keys", f"missing {missing}")
    _pass("01_schema_has_all_required_keys")


def test_02_byte_det_x2() -> None:
    a = build_env_pin_manifest()
    b = build_env_pin_manifest()
    if a["env_pin_sha256"] != b["env_pin_sha256"]:
        return _fail("02_byte_det_x2", f"drift {a['env_pin_sha256'][:12]} vs {b['env_pin_sha256'][:12]}")
    _pass("02_byte_det_x2")


def test_03_self_anchor_sha() -> None:
    m = build_env_pin_manifest()
    body_dict = {k: v for k, v in m.items() if k != "env_pin_sha256"}
    body = json.dumps(body_dict, sort_keys=True, indent=2)
    expected = hashlib.sha256(body.encode("utf-8")).hexdigest()
    if m["env_pin_sha256"] != expected:
        return _fail("03_self_anchor_sha", f"self-anchor mismatch {m['env_pin_sha256'][:12]} vs {expected[:12]}")
    _pass("03_self_anchor_sha")


def test_04_deterministic_key_ordering() -> None:
    j1 = json.dumps(build_env_pin_manifest(), sort_keys=True, indent=2)
    j2 = json.dumps(build_env_pin_manifest(), sort_keys=True, indent=2)
    if j1 != j2:
        return _fail("04_deterministic_key_ordering", "canonical JSON drift")
    _pass("04_deterministic_key_ordering")


def test_05_write_env_pin_round_trip() -> None:
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "env_pin.json"
        m = write_env_pin(p)
        if not p.exists():
            return _fail("05_write_env_pin_round_trip", "file not written")
        parsed = json.loads(p.read_text())
        if parsed["env_pin_sha256"] != m["env_pin_sha256"]:
            return _fail("05_write_env_pin_round_trip", "sha drift disk vs mem")
    _pass("05_write_env_pin_round_trip")


def test_06_env_vars_captured() -> None:
    m = build_env_pin_manifest()
    env = m.get("env", {})
    required = {"PYTHONHASHSEED", "SOURCE_DATE_EPOCH", "TZ", "LC_ALL",
                "OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"}
    missing = required - set(env)
    if missing:
        return _fail("06_env_vars_captured", f"env missing {missing}")
    _pass("06_env_vars_captured")


def test_07_sf2_sha_anchor_present() -> None:
    m = build_env_pin_manifest()
    sf2 = m.get("soundfont", {}).get("sha256", "")
    if not sf2.startswith("74594e8f"):
        return _fail("07_sf2_sha_anchor_present", f"SF2 SHA drift or missing: {sf2[:16]}")
    _pass("07_sf2_sha_anchor_present")


def test_08_drift_detectability_env_var_mutation() -> None:
    """Round-trip: mutating an env var changes env_pin_sha256."""
    a = build_env_pin_manifest()
    saved = os.environ.get("PYTHONHASHSEED")
    os.environ["PYTHONHASHSEED"] = "99999"
    try:
        b = build_env_pin_manifest()
    finally:
        if saved is None:
            del os.environ["PYTHONHASHSEED"]
        else:
            os.environ["PYTHONHASHSEED"] = saved
    if a["env_pin_sha256"] == b["env_pin_sha256"]:
        return _fail("08_drift_detectability_env_var_mutation",
                     "env_pin_sha256 unchanged after env var mutation")
    _pass("08_drift_detectability_env_var_mutation")


def test_09_python_executable_captured() -> None:
    m = build_env_pin_manifest()
    exe = m.get("python", {}).get("executable")
    if not exe or "python" not in exe:
        return _fail("09_python_executable_captured", f"unexpected exe {exe}")
    _pass("09_python_executable_captured")


def main() -> int:
    for name in sorted(g for g in globals() if g.startswith("test_")):
        globals()[name]()
    if FAILED:
        print("\n".join(FAILED), file=sys.stderr)
        print(f"\n{len(FAILED)} FAILED / 9 total", file=sys.stderr)
        return 1
    print("\n9/9 PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
