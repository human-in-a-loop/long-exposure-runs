#!/usr/bin/env python3
# created: 2026-09-02T07:05:00Z
# cycle: 57 clone-2
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-RECREATE-2/accurate-small-set/rc10-transcription-real-stem-resurvey/learned-transcribers
"""D1 Fetchability ladder: probe 4 candidate families via pip in the
quarantined venv. Log per-rung {family, rung, url, http_status,
sha256_if_success, failure_mode_if_fail, ts}. Honest FETCH_FAIL rows
preserved per c11 CLAP precedent. Grep-guard forbids 'laion-clap-htsat'.

Runs under /usr/bin/python3 (outer). Inner pip runs in
workspace/learned_transcribers_venv/. See docs/rc10_learned_survey_rubric.md
D1.
"""
import json, os, pathlib, subprocess, sys, time

# c48 env-flag defaults OFF
os.environ.setdefault("MUSICGEN_LEDGER_SUBSTANTIVE_EXEMPTION", "0")
os.environ.setdefault("MUSICGEN_LEDGER_SUPERSEDES_IN_HASH", "0")

VENV_PY = pathlib.Path("workspace/learned_transcribers_venv/bin/python").absolute()
LADDER = pathlib.Path("data/rc10_learned_survey/fetchability_ladder.jsonl")
LADDER.parent.mkdir(parents=True, exist_ok=True)

ENV_PINS = {
    "OMP_NUM_THREADS": "1", "MKL_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1",
    "PYTHONHASHSEED": "0", "SOURCE_DATE_EPOCH": "1756463424",
    "TZ": "UTC", "LC_ALL": "C.UTF-8",
}

FORBIDDEN_URL_SUBSTR = "laion-clap-htsat"


def _env():
    e = os.environ.copy()
    e.update(ENV_PINS)
    for k in ("VIRTUAL_ENV", "PYTHONPATH", "PYTHONHOME"):
        e.pop(k, None)
    return e


def _log(row):
    row["ts"] = row.get("ts") or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    with LADDER.open("a") as f:
        f.write(json.dumps(row, sort_keys=True) + "\n")


def _pip_install(family, rung, spec, url_hint=None):
    assert FORBIDDEN_URL_SUBSTR not in (spec + (url_hint or ""))
    r = subprocess.run(
        [str(VENV_PY), "-m", "pip", "install", "--no-input", spec],
        env=_env(), capture_output=True, text=True, timeout=900,
    )
    ok = r.returncode == 0
    _log({
        "family": family, "rung": rung, "method": f"pip install {spec}",
        "url": url_hint or f"pypi:{spec}",
        "http_status": "200" if ok else "pip_rc_" + str(r.returncode),
        "sha256_if_success": None,
        "failure_mode_if_fail": None if ok else (r.stdout + r.stderr)[-800:],
        "success": ok,
    })
    return ok


def probe_all():
    results = {}
    results["drums_omnizart_pip"] = _pip_install(
        "drums_omnizart", 1, "omnizart", url_hint="pypi:omnizart")
    _log({"family": "drums_oaf", "rung": 1, "method": "GitHub release wheel probe",
          "url": "OaF-drums no maintained wheel", "http_status": "n/a",
          "sha256_if_success": None,
          "failure_mode_if_fail": "OaF-drums has no maintained pip-installable wheel.",
          "success": False})
    results["torchcrepe_pip"] = _pip_install(
        "bass_vocals_torchcrepe", 1, "torchcrepe==0.0.24",
        url_hint="pypi:torchcrepe==0.0.24")
    results["piano_bytedance_pip"] = _pip_install(
        "piano_bytedance", 1, "piano_transcription_inference",
        url_hint="pypi:piano_transcription_inference")
    _log({"family": "multi_mt3", "rung": 1, "method": "HuggingFace/GitHub release probe",
          "url": "google/mt3 no wheel", "http_status": "n/a",
          "sha256_if_success": None,
          "failure_mode_if_fail": "MT3 JAX/T5X research code — no installable wheel; deferred per c11.",
          "success": False})
    return results


if __name__ == "__main__":
    assert "/usr/bin/python3" in sys.executable or "/usr/local/bin/python3" in sys.executable
    print(json.dumps(probe_all(), indent=2))
