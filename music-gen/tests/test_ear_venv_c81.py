#!/usr/bin/python3
"""c81 P5 tests — ear venv decision record shape; main-env pip freeze unchanged; probe enum.

created: 2026-09-06T17:20:00Z
cycle: 81
run_id: run-2026-09-06T000000Z
agent: worker
milestone: _infra/adopt-cycle81-tests

Run: PYTHONPATH=. /usr/bin/python3 tests/test_ear_venv_c81.py
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
os.chdir(_ROOT)
C79_MAIN_FREEZE = "90ed1d9f0fd0a33e3be35653bf541f82ceadcd4d89c0013b9cdd0228544d639d"
ENUM_BUILD = ("VENV_BLOCKED_DISK", "VENV_BUILD_ALLOWED")
ENUM_PROBE = ("EAR_VENV_REPRODUCES_CACHE", "EAR_VENV_DIFFERS_FROM_CACHE", "EAR_VENV_NONDETERMINISTIC", "EAR_VENV_ABSENT", "EAR_VENV_PROBE_FAILED")


def test_01_venv_decision_record_shape() -> None:
    d = json.loads((_ROOT / "data/v5/ear/venv_build_c81.json").read_text())
    for k in ("verdict", "df", "arithmetic", "binding_ceiling_pct", "venv_size_bytes_c79_receipt", "operator_request_one_line",
              "main_env_pip_freeze_sha256", "main_env_unchanged_vs_c79", "build_command_pinned", "pause_exercised"):
        assert k in d, k
    assert d["verdict"] in ENUM_BUILD and d["binding_ceiling_pct"] == 90.0
    a = d["arithmetic"]
    if d["verdict"] == "VENV_BLOCKED_DISK":
        assert a["post_build_used_pct"] >= 90.0 and a["consumable_before_ceiling_gb"] < d["venv_size_bytes_c79_receipt"] / 1e9
        assert d["operator_request_one_line"].startswith("OPERATOR:") and d["pause_exercised"] is False
    assert d["main_env_pip_freeze_sha256_c79_receipt"] == C79_MAIN_FREEZE
    print(f"test_01 PASS: venv_build_c81.json verdict={d['verdict']} post_build={a['post_build_used_pct']}% consumable={a['consumable_before_ceiling_gb']} GB")


def test_02_main_env_pip_freeze_unchanged() -> None:
    freeze = subprocess.run(["/usr/bin/python3", "-m", "pip", "freeze"], capture_output=True, text=True).stdout
    sha = hashlib.sha256(freeze.encode()).hexdigest()
    d = json.loads((_ROOT / "data/v5/ear/venv_build_c81.json").read_text())
    assert sha == d["main_env_pip_freeze_sha256"] == C79_MAIN_FREEZE, "main-env pins must be untouched (pre == post == c79)"
    print(f"test_02 PASS: main-env pip freeze sha {sha[:12]}… == c79 receipt")


def test_03_probe_record_enum_and_venv_absent_branch() -> None:
    p = _ROOT / "data/v5/ear/ear_probe_c81.json"
    d = json.loads(p.read_text())
    assert d["status"] in ENUM_PROBE
    venv = (_ROOT / "workspace/ear_venv/bin/python").exists()
    if not venv:
        assert d["status"] == "EAR_VENV_ABSENT"
        env = dict(os.environ); env.pop("SUPPRESS_INTERPRETER_GUARD", None); env["PYTHONPATH"] = "."
        r = subprocess.run(["/usr/bin/python3", "scripts/v5/ear_probe_v5.py"], env=env, capture_output=True, text=True)
        assert r.returncode == 3 and "EAR_VENV_ABSENT" in r.stdout
    else:
        # c82: the c81 record stays ABSENT as history; the live probe record is the newest ear_probe_c<N>.json (c82+)
        newest = sorted(_ROOT.glob("data/v5/ear/ear_probe_c*.json"))[-1]
        d = json.loads(newest.read_text())
        assert d["status"] != "EAR_VENV_ABSENT" and "rows" in d, (newest, d["status"])
    print(f"test_03 PASS: probe status {d['status']} (venv present={venv})")


def test_04_amended_receipt_c83() -> None:
    """c83 S2 (closes c82 audit F2): the amended receipt exists, its freeze sha matches the on-disk freeze file,
    the pinned command names the librosa amendment (via the amended freeze file), supersede is a str (c14 lemma),
    and the main-env freeze sha is unchanged vs the c79 receipt. Additive; c81-c82 records untouched."""
    p = _ROOT / "data/v5/ear/env_pin_ear_venv_c82_amended.json"
    assert p.exists(), "amended receipt missing (c83 S2)"
    d = json.loads(p.read_text())
    freeze = _ROOT / d["pip_freeze_path"]
    assert hashlib.sha256(freeze.read_bytes()).hexdigest() == d["pip_freeze_sha256"], "receipt freeze sha != on-disk freeze file"
    assert "librosa==" in freeze.read_text() and d["librosa_pin"].startswith("librosa==")
    assert d["pip_freeze_path"] in d["pinned_command"] and "pip install" in d["pinned_command"], "pinned command must install the amended freeze"
    assert isinstance(d["supersedes_path"], str) and d["supersedes_path"] == "data/v5/ear/env_pin_ear_venv_c82.json"
    assert d["main_env_pip_freeze_sha256"] == C79_MAIN_FREEZE and d["main_env_unchanged"] is True
    assert d["versions_from_venv_subprocess"].get("librosa") == d["librosa_pin"].split("==")[1]
    if (_ROOT / "data/v5/ear/ear_probe_c83.json").exists():
        assert json.loads((_ROOT / "data/v5/ear/ear_probe_c83.json").read_text())["status"] in ENUM_PROBE
    print(f"test_04 PASS: amended receipt freeze {d['pip_freeze_sha256'][:12]}… librosa {d['librosa_pin']} main-env unchanged")


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for t in tests:
        t()
    print(f"\n{len(tests)}/{len(tests)} ear_venv_c81 tests PASS")
