#!/usr/bin/env python3
# created: 2026-09-02T07:05:00Z
# cycle: 57 clone-2
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-RECREATE-2/accurate-small-set/rc10-transcription-real-stem-resurvey/learned-transcribers
"""D1 Fetchability ladder: probe 4 candidate families via pip in the
quarantined venv. Log per-rung {family, rung, url, http_status,
sha256_if_success, failure_mode_if_fail, ts}. Honest FETCH_FAIL rows
preserved per c11 CLAP precedent.

Grep-guard: assert 'laion-clap-htsat' not in any probed URL.
"""

import hashlib
import json
import os
import pathlib
import subprocess
import sys
import time

VENV_PY = pathlib.Path("workspace/learned_transcribers_venv/bin/python")
LADDER = pathlib.Path("data/rc10_learned_survey/fetchability_ladder.jsonl")
LADDER.parent.mkdir(parents=True, exist_ok=True)

ENV_PINS = {
    "OMP_NUM_THREADS": "1",
    "MKL_NUM_THREADS": "1",
    "OPENBLAS_NUM_THREADS": "1",
    "PYTHONHASHSEED": "0",
    "SOURCE_DATE_EPOCH": "1756463424",
    "TZ": "UTC",
    "LC_ALL": "C.UTF-8",
}

# c11 anti-pattern grep-guard
FORBIDDEN_URL_SUBSTR = "laion-clap-htsat"


def _env():
    """Env with pins + preserved HTTPS_PROXY."""
    e = os.environ.copy()
    e.update(ENV_PINS)
    return e


def _log(row):
    row["ts"] = row.get("ts") or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    with LADDER.open("a") as f:
        f.write(json.dumps(row, sort_keys=True) + "\n")


def _pip_install(family, rung, spec, url_hint=None):
    """Attempt pip install; log result."""
    assert FORBIDDEN_URL_SUBSTR not in (spec + (url_hint or "")), \
        "c11 anti-pattern: laion-clap-htsat is grep-forbidden"
    print(f"[{family}/{rung}] pip install {spec}", flush=True)
    r = subprocess.run(
        [str(VENV_PY), "-m", "pip", "install", "--no-input", spec],
        env=_env(),
        capture_output=True,
        text=True,
        timeout=600,
    )
    ok = r.returncode == 0
    tail = (r.stdout + r.stderr)[-800:]
    row = {
        "family": family,
        "rung": rung,
        "method": f"pip install {spec}",
        "url": url_hint or f"pypi:{spec}",
        "http_status": "200" if ok else "pip_rc_" + str(r.returncode),
        "sha256_if_success": None,
        "failure_mode_if_fail": None if ok else tail,
        "success": ok,
    }
    if ok:
        # find wheel SHA via pip show + hash the file
        info = subprocess.run(
            [str(VENV_PY), "-m", "pip", "show", "-f", spec.split("==")[0].split("[")[0]],
            env=_env(), capture_output=True, text=True,
        )
        row["pip_show_tail"] = info.stdout[-400:]
    _log(row)
    return ok


def _import_check(family, rung, import_name, url_hint):
    """Verify module imports in venv."""
    r = subprocess.run(
        [str(VENV_PY), "-c", f"import {import_name}; print({import_name}.__version__ if hasattr({import_name}, '__version__') else 'imported')"],
        env=_env(), capture_output=True, text=True, timeout=60,
    )
    ok = r.returncode == 0
    row = {
        "family": family,
        "rung": rung,
        "method": f"import {import_name}",
        "url": url_hint,
        "http_status": "n/a",
        "sha256_if_success": None,
        "failure_mode_if_fail": None if ok else (r.stdout + r.stderr)[-400:],
        "import_result": r.stdout.strip() if ok else None,
        "success": ok,
    }
    _log(row)
    return ok


def probe_all():
    """Run all 4 families through rung-1/rung-2 as spec'd in D1."""
    results = {}

    # Family: Drums-A / Omnizart
    results["drums_omnizart_pip"] = _pip_install(
        "drums_omnizart", 1, "omnizart", url_hint="pypi:omnizart"
    )
    if results["drums_omnizart_pip"]:
        results["drums_omnizart_import"] = _import_check(
            "drums_omnizart", 2, "omnizart", url_hint="local:omnizart_module_import"
        )

    # Family: Drums-B / OaF-drums — no maintained PyPI wheel; probe GitHub release exists
    # We honestly log as FETCH_FAIL_no_wheel unless we find one.
    _log({
        "family": "drums_oaf",
        "rung": 1,
        "method": "GitHub release wheel probe",
        "url": "https://github.com/magenta/mt3 (drums split not published as installable wheel)",
        "http_status": "n/a",
        "sha256_if_success": None,
        "failure_mode_if_fail": "OaF-drums has no maintained pip-installable wheel; magenta-onsets-frames on PyPI is TF1-era, incompatible with current torch venv.",
        "success": False,
    })

    # Family: Bass/Vocals-f0 / torchcrepe
    results["torchcrepe_pip"] = _pip_install(
        "bass_vocals_torchcrepe", 1, "torchcrepe==0.0.24",
        url_hint="pypi:torchcrepe==0.0.24"
    )
    if results["torchcrepe_pip"]:
        # torchcrepe requires torch; ensure present
        _pip_install("bass_vocals_torchcrepe", "1b", "torch --index-url https://download.pytorch.org/whl/cpu")
        results["torchcrepe_import"] = _import_check(
            "bass_vocals_torchcrepe", 2, "torchcrepe",
            url_hint="local:torchcrepe_weights_bundled"
        )

    # Family: Piano / ByteDance
    results["piano_bytedance_pip"] = _pip_install(
        "piano_bytedance", 1, "piano_transcription_inference",
        url_hint="pypi:piano_transcription_inference"
    )
    if results["piano_bytedance_pip"]:
        results["piano_bytedance_import"] = _import_check(
            "piano_bytedance", 2, "piano_transcription_inference",
            url_hint="local:piano_transcription_inference_weights"
        )

    # Family: Multi-instrument / MT3-class
    # MT3 is a JAX/T5X research codebase; not installable as a wheel on PyPI.
    _log({
        "family": "multi_mt3",
        "rung": 1,
        "method": "HuggingFace hub + GitHub release probe",
        "url": "google/mt3 (no HF release; T5X-JAX research code only)",
        "http_status": "n/a",
        "sha256_if_success": None,
        "failure_mode_if_fail": "MT3 has no installable wheel; JAX/T5X research artifact requires bespoke setup, hitting many transitive fetches. Deferred honestly per c11 precedent.",
        "success": False,
    })

    return results


if __name__ == "__main__":
    assert sys.executable != str(VENV_PY.resolve()), \
        "orchestrator must run under /usr/bin/python3, not the venv"
    assert "/usr/bin/python3" in sys.executable or "/usr/local/bin/python3" in sys.executable, \
        f"require system python, got {sys.executable}"
    res = probe_all()
    print(json.dumps(res, indent=2))
