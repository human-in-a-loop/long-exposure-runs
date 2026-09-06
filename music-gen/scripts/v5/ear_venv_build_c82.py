#!/usr/bin/python3
"""c82 P1 — build the ISOLATED ear venv (OPERATOR Decision 5; MANDATORY per operator note 2026-09-06 17:20Z).

created: 2026-09-06T18:15:00Z
cycle: 82
run_id: run-2026-09-06T000000Z
agent: worker
milestone: M-V5-EAR-1/ear-venv-built-c82

Pre-registered in data/v5/ear/venv_build_c82_preregistration.json (written BEFORE this script ran). Steps, each
followed by a df reading in the driver's semantics (used/(used+avail)); any reading >= 90 % aborts and removes the venv:
  1. python3 -m venv workspace/ear_venv
  2. pip install --no-cache-dir "numpy<2" tensorflow tensorflow_hub pyloudnorm   (c79 pinned command)
  3. pip freeze -> data/v5/ear/ear_venv_pip_freeze_c82.txt; sha compared to the c79 receipt a4d23dea... (drift disclosed, not retried)
  4. main-env pip freeze sha must equal the c79 receipt 90ed1d9f... (pre == post)
  5. env pin manifest -> data/v5/ear/env_pin_ear_venv_c82.json
Sequencing: runs while the transcription driver is stopped at a song boundary (the caller records the window).
Discipline: /usr/bin/python3 guard; no PRNG; no sidecar_nonfactor; no VST3 state APIs; main venv pins untouched.
"""
from __future__ import annotations

import datetime
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

if sys.executable != "/usr/bin/python3" and "SUPPRESS_INTERPRETER_GUARD" not in os.environ:
    print(f"FATAL: expected /usr/bin/python3, got {sys.executable}", file=sys.stderr)
    sys.exit(2)

_WS = Path(__file__).resolve().parent.parent.parent
VENV = _WS / "workspace/ear_venv"
OUT = _WS / "data/v5/ear"
LOG = _WS / "data/v5/logs/ear_venv_build_c82.log"
CEILING = 90.0
C79_VENV_FREEZE = "a4d23dea13d7be139221cb4302f6f16073748c7286be78e457e311239b5bcaea"
C79_MAIN_FREEZE = "90ed1d9f0fd0a33e3be35653bf541f82ceadcd4d89c0013b9cdd0228544d639d"
PIP_PKGS = ["numpy<2", "tensorflow", "tensorflow_hub", "pyloudnorm"]


def now() -> str:
    return datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def df() -> dict:
    st = os.statvfs(str(_WS))
    used = (st.f_blocks - st.f_bfree) * st.f_frsize
    avail = st.f_bavail * st.f_frsize
    return {"used_pct": round(100 * used / (used + avail), 2), "avail_gb": round(avail / 1e9, 3), "ts": now()}


def sha_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def log(msg: str) -> None:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a") as f:
        f.write(f"[{now()}] {msg}\n")
    print(msg, flush=True)


def abort(rec: dict, step: str, reading: dict) -> int:
    rec.update({"status": "EAR_VENV_ABORTED_DF", "abort_step": step, "abort_reading": reading})
    if VENV.exists():
        shutil.rmtree(VENV, ignore_errors=True)
        rec["venv_removed"] = True
    rec["df_after_removal"] = df()
    (OUT / "venv_build_c82.json").write_text(json.dumps(rec, sort_keys=True, indent=2) + "\n")
    log(f"ABORT at {step}: {reading} -> venv removed; df now {rec['df_after_removal']}")
    return 5


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    prereg = json.loads((OUT / "venv_build_c82_preregistration.json").read_text())
    main_pre = sha_bytes(subprocess.run(["/usr/bin/python3", "-m", "pip", "freeze"], capture_output=True, text=True).stdout.encode())
    rec = {"schema_version": 1, "cycle": 82, "agent": "worker", "run_id": "run-2026-09-06T000000Z", "milestone": "M-V5-EAR-1/ear-venv-built-c82",
           "preregistration_sha256": sha_bytes((OUT / "venv_build_c82_preregistration.json").read_bytes()),
           "predicted_post_build_used_pct": prereg["predicted_post_build_used_pct"], "abort_ceiling_pct": CEILING,
           "build_command_pinned": prereg["build_command_pinned"], "main_env_pip_freeze_sha256_pre": main_pre,
           "main_env_pip_freeze_sha256_c79_receipt": C79_MAIN_FREEZE, "steps": [], "started_utc": now()}
    d0 = df(); rec["steps"].append({"step": "open", "df": d0})
    log(f"open df={d0}")
    if d0["used_pct"] >= CEILING:
        return abort(rec, "open", d0)
    if VENV.exists():
        log("venv already exists -> reusing (no rebuild)")
    else:
        subprocess.run(["/usr/bin/python3", "-m", "venv", str(VENV)], check=True)
    d1 = df(); rec["steps"].append({"step": "venv_create", "df": d1}); log(f"venv_create df={d1}")
    if d1["used_pct"] >= CEILING:
        return abort(rec, "venv_create", d1)
    t0 = datetime.datetime.utcnow()
    r = subprocess.run([str(VENV / "bin/pip"), "install", "--no-cache-dir"] + PIP_PKGS, capture_output=True, text=True)
    wall = (datetime.datetime.utcnow() - t0).total_seconds()
    LOG.open("a").write(r.stdout[-4000:] + "\n" + r.stderr[-4000:] + "\n")
    d2 = df(); rec["steps"].append({"step": "pip_install", "rc": r.returncode, "wall_s": round(wall, 1), "df": d2}); log(f"pip_install rc={r.returncode} wall={wall:.0f}s df={d2}")
    if r.returncode != 0:
        rec.update({"status": "EAR_VENV_PIP_FAILED", "stderr_tail": r.stderr[-2000:]})
        (OUT / "venv_build_c82.json").write_text(json.dumps(rec, sort_keys=True, indent=2) + "\n")
        return 4
    if d2["used_pct"] >= CEILING:
        return abort(rec, "pip_install", d2)
    freeze = subprocess.run([str(VENV / "bin/pip"), "freeze"], capture_output=True, text=True).stdout
    (OUT / "ear_venv_pip_freeze_c82.txt").write_text(freeze)
    fsha = sha_bytes(freeze.encode())
    probe = subprocess.run([str(VENV / "bin/python"), "-c",
                            "import numpy, tensorflow, tensorflow_hub, pyloudnorm; print(numpy.__version__, tensorflow.__version__, tensorflow_hub.__version__, pyloudnorm.__version__)"],
                           capture_output=True, text=True)
    versions = probe.stdout.strip().split()
    size = sum(p.stat().st_size for p in VENV.rglob("*") if p.is_file())
    main_post = sha_bytes(subprocess.run(["/usr/bin/python3", "-m", "pip", "freeze"], capture_output=True, text=True).stdout.encode())
    rec.update({"status": "EAR_VENV_BUILT", "venv_path": "workspace/ear_venv", "venv_size_bytes": size, "pip_freeze_path": "data/v5/ear/ear_venv_pip_freeze_c82.txt",
                "pip_freeze_sha256": fsha, "pip_freeze_sha256_c79_receipt": C79_VENV_FREEZE, "pip_freeze_matches_c79": fsha == C79_VENV_FREEZE,
                "n_packages": len([l for l in freeze.splitlines() if l.strip()]), "import_probe_rc": probe.returncode, "import_probe_stdout": probe.stdout.strip()[-300:],
                "versions": dict(zip(("numpy", "tensorflow", "tensorflow_hub", "pyloudnorm"), versions)) if len(versions) == 4 else {"raw": probe.stdout, "stderr": probe.stderr[-500:]},
                "main_env_pip_freeze_sha256_post": main_post, "main_env_unchanged": main_pre == main_post == C79_MAIN_FREEZE, "finished_utc": now(), "df_final": df()})
    (OUT / "venv_build_c82.json").write_text(json.dumps(rec, sort_keys=True, indent=2) + "\n")
    env_pin = {"schema_version": 1, "cycle": 82, "agent": "worker", "venv_path": "workspace/ear_venv", "python_exe": "workspace/ear_venv/bin/python",
               "python_version": subprocess.run([str(VENV / "bin/python"), "--version"], capture_output=True, text=True).stdout.strip(),
               "build_command": prereg["build_command_pinned"], "pip_freeze_sha256": fsha, "pip_freeze_matches_c79_receipt": fsha == C79_VENV_FREEZE,
               "versions": rec["versions"], "invocation": "subprocess only (scripts/v5/ear_probe_v5.py); the main venv never imports from it",
               "main_env_pip_freeze_sha256": main_post, "size_bytes_installed": size, "built_utc": rec["finished_utc"],
               "c79_receipt": "data/v5/ear/env_pin_ear_venv.json (built, verified, removed for disk hygiene at 92.2 %)"}
    (OUT / "env_pin_ear_venv_c82.json").write_text(json.dumps(env_pin, sort_keys=True, indent=2) + "\n")
    log(f"BUILT size={size/1e9:.2f}GB freeze_sha={fsha[:12]} matches_c79={fsha == C79_VENV_FREEZE} versions={rec['versions']} main_env_unchanged={rec['main_env_unchanged']} df={rec['df_final']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
