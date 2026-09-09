#!/usr/bin/python3
"""c83 S2 (P0, closes c82 audit F2) — amended isolated-ear-venv pin receipt.

created: 2026-09-06T20:40:00Z
cycle: 83
run_id: run-2026-09-06T000000Z
agent: worker
milestone: M-V5-EAR-1/ear-venv-receipt-amended-c83

The c82 receipt `data/v5/ear/env_pin_ear_venv_c82.json` describes the c79-pinned build command, but the venv that
actually reproduces the cache (`ear_probe_c82_amended.json` = EAR_VENV_REPRODUCES_CACHE) is the AMENDED venv
(+ librosa 0.11.0 and 17 deps, freeze sha 40243a56…). This script writes the sibling receipt
`data/v5/ear/env_pin_ear_venv_c82_amended.json` whose pinned command is the c79 command FOLLOWED BY
`pip install -r data/v5/ear/ear_venv_pip_freeze_c82_amended.txt` (the freeze file is the authoritative pin; the
librosa amendment command is recorded alongside for provenance). Every version is read from the venv by subprocess;
the freeze sha is recomputed from the on-disk file; the main-env freeze sha is recomputed and asserted unchanged
(c79 receipt 90ed1d9f…). `supersedes_path` is a str (c14 lemma). No install, no pip, no write outside data/v5/ear/.
Discipline: /usr/bin/python3 guard; no PRNG; no sidecar_nonfactor; no VST3 state APIs.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

if sys.executable != "/usr/bin/python3" and "SUPPRESS_INTERPRETER_GUARD" not in os.environ:
    print(f"FATAL: expected /usr/bin/python3, got {sys.executable}", file=sys.stderr)
    sys.exit(2)

_WS = Path(__file__).resolve().parent.parent.parent
os.chdir(_WS)
VENV = Path("workspace/ear_venv")
VENV_PY = VENV / "bin/python"
FREEZE = Path("data/v5/ear/ear_venv_pip_freeze_c82_amended.txt")
C82_RECEIPT = Path("data/v5/ear/env_pin_ear_venv_c82.json")
C82_AMEND = Path("data/v5/ear/venv_amend_c82.json")
OUT = Path("data/v5/ear/env_pin_ear_venv_c82_amended.json")
C79_MAIN_FREEZE = "90ed1d9f0fd0a33e3be35653bf541f82ceadcd4d89c0013b9cdd0228544d639d"
VERSION_PROBE = ("import json,sys,numpy,tensorflow,tensorflow_hub,librosa,soundfile,pyloudnorm;"
                 "print(json.dumps({'python': sys.version.split()[0], 'numpy': numpy.__version__, 'tensorflow': tensorflow.__version__,"
                 " 'tensorflow_hub': tensorflow_hub.__version__, 'librosa': librosa.__version__, 'soundfile': soundfile.__version__,"
                 " 'pyloudnorm': getattr(pyloudnorm, '__version__', 'no __version__ attr (0.2.0 per freeze)')}))")


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> int:
    if not VENV_PY.exists():
        print("FATAL: workspace/ear_venv absent; receipt cannot be amended against a missing venv", file=sys.stderr)
        return 3
    c82 = json.loads(C82_RECEIPT.read_text())
    amend = json.loads(C82_AMEND.read_text())
    freeze_sha = _sha(FREEZE)
    assert freeze_sha == amend["pip_freeze_sha256_post"], (freeze_sha, amend["pip_freeze_sha256_post"])
    # c82 amend record used `<venv python> -m pip freeze`; `bin/pip freeze` emits the same 52 lines in a different order
    live_freeze = subprocess.run([str(VENV_PY), "-m", "pip", "freeze"], capture_output=True, text=True, check=True).stdout
    live_freeze_sha = hashlib.sha256(live_freeze.encode()).hexdigest()
    live_set_equal = sorted(live_freeze.split()) == sorted(FREEZE.read_text().split())
    env = dict(os.environ); env["TF_CPP_MIN_LOG_LEVEL"] = "3"; env["TF_ENABLE_ONEDNN_OPTS"] = "0"
    vr = subprocess.run([str(VENV_PY), "-c", VERSION_PROBE], capture_output=True, text=True, env=env)
    versions = json.loads(vr.stdout.strip().splitlines()[-1]) if vr.returncode == 0 else {"error": vr.stderr[-800:]}
    main_freeze = subprocess.run(["/usr/bin/python3", "-m", "pip", "freeze"], capture_output=True, text=True).stdout
    main_sha = hashlib.sha256(main_freeze.encode()).hexdigest()
    rec = {
        "schema_version": 2,
        "agent": "worker",
        "cycle": 83,
        "run_id": "run-2026-09-06T000000Z",
        "milestone": "M-V5-EAR-1/ear-venv-receipt-amended-c83",
        "written_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "supersedes_path": str(C82_RECEIPT),
        "supersede_scope": "the receipt clause of M-V5-EAR-1/ear-venv-built-c82: the c82 receipt describes the c79 pinned command, not the venv that reproduces the cache; this receipt pins the amended venv",
        "venv_path": str(VENV),
        "python_exe": str(VENV_PY),
        "pinned_command": (c82["build_command"] + " && " + f"{VENV}/bin/pip install --no-cache-dir -r {FREEZE}"),
        "pinned_command_form": "c79 command FOLLOWED BY pip install -r <amended freeze file>; the freeze file (not the bare `librosa` name) is the pin because pip resolved 18 packages at c82",
        "c82_amendment_command_as_run": amend["amend_command"],
        "c82_amendment_added_packages": amend["added_packages"],
        "librosa_pin": next(p for p in amend["added_packages"] if p.startswith("librosa==")),
        "pip_freeze_path": str(FREEZE),
        "pip_freeze_sha256": freeze_sha,
        "pip_freeze_sha256_matches_c82_amend_record": freeze_sha == amend["pip_freeze_sha256_post"],
        "live_venv_pip_freeze_sha256": live_freeze_sha,
        "live_venv_freeze_matches_file": live_freeze_sha == freeze_sha,
        "live_venv_freeze_package_set_equals_file": live_set_equal,
        "live_venv_freeze_method": "<venv python> -m pip freeze (c82 amend method); bin/pip freeze yields the same 52 lines re-ordered",
        "c79_receipt_pip_freeze_sha256": c82["pip_freeze_sha256"],
        "c79_receipt_note": "a4d23dea… (c79/c82 pinned command, 34 packages) differs from 2228bfcf… (c82 amend pre-sha) only by line ordering — verified at c82; both superseded by this amended pin",
        "versions_from_venv_subprocess": versions,
        "version_probe_rc": vr.returncode,
        "main_env_pip_freeze_sha256": main_sha,
        "main_env_pip_freeze_sha256_c79_receipt": C79_MAIN_FREEZE,
        "main_env_unchanged": main_sha == C79_MAIN_FREEZE,
        "main_env_freeze_method": "/usr/bin/python3 -m pip freeze | sha256 (the c82 venv_amend record's 98873ad0… used a different freeze invocation; this receipt uses the c79/c81/c82-receipt method)",
        "reproducibility_records": {
            "pinned_command_probe": "data/v5/ear/ear_probe_c82.json (EAR_VENV_PROBE_FAILED — permanent record)",
            "amended_probe_c82": "data/v5/ear/ear_probe_c82_amended.json (EAR_VENV_REPRODUCES_CACHE)",
            "amended_probe_c83": "data/v5/ear/ear_probe_c83.json (this cycle, read-only re-probe x2 fresh mkdtemp)",
            "gate": "data/v5/ear/ear_gate_v5_c82.json (EAR_GATE_RUN)",
        },
        "invocation": "subprocess only; the main venv never imports from workspace/ear_venv",
        "install_this_cycle": False,
        "size_bytes_installed": sum(f.stat().st_size for f in VENV.rglob("*") if f.is_file()),
    }
    assert rec["main_env_unchanged"], f"main env drifted: {main_sha}"
    OUT.write_text(json.dumps(rec, sort_keys=True, indent=2) + "\n")
    print(json.dumps({k: rec[k] for k in ("pip_freeze_sha256", "live_venv_freeze_matches_file", "versions_from_venv_subprocess",
                                           "main_env_unchanged", "librosa_pin", "size_bytes_installed")}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
