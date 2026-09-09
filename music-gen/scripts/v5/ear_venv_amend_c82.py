#!/usr/bin/python3
"""c82 P1 AMENDMENT (disclosed deviation from the c79-pinned build command).

created: 2026-09-06T20:05:00Z   cycle: 82   run_id: run-2026-09-06T000000Z   agent: worker   milestone: M-V5-EAR-1/ear-venv-built-c82

The c79-pinned command (`pip install "numpy<2" tensorflow tensorflow_hub pyloudnorm`) built a venv whose pip-freeze
sha matched the c79 receipt (a4d23dea…), but the FIRST probe run of the READ-ONLY c74 extractor
(scripts/v4_ear/ear.py) inside it failed at import time: `ModuleNotFoundError: No module named 'librosa'`
(data/v5/ear/ear_probe_c82.json, status EAR_VENV_PROBE_FAILED, kept byte-identical as the pinned-command outcome).
c79 only import-probed tensorflow/tensorflow_hub/numpy and never exercised the extractor, so the omission is a
receipt bug, not a falsified criterion. This script adds `librosa` (and only what pip pulls for it) to the venv,
records pre/post pip-freeze SHAs + df, aborts at the 90 % ceiling, and touches nothing in the main environment.
"""
import datetime
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

if sys.executable != "/usr/bin/python3":
    sys.exit("interpreter guard: run with /usr/bin/python3")
os.chdir(Path(__file__).resolve().parents[2])
VENV = Path("workspace/ear_venv")
PIP = VENV / "bin/pip"
PY = VENV / "bin/python"
OUT = Path("data/v5/ear/venv_amend_c82.json")
FREEZE_OUT = Path("data/v5/ear/ear_venv_pip_freeze_c82_amended.txt")
CEILING = 90.0


def now():
    return datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def df():
    st = os.statvfs(".")
    used = (st.f_blocks - st.f_bfree) * st.f_frsize
    avail = st.f_bavail * st.f_frsize
    return dict(used_pct=round(100.0 * used / (used + avail), 2), avail_gb=round(avail / 1e9, 3), ts=now())


def freeze(py):
    r = subprocess.run([str(py), "-m", "pip", "freeze"], capture_output=True, text=True)
    txt = "\n".join(sorted(l for l in r.stdout.splitlines() if l.strip())) + "\n"
    return txt, hashlib.sha256(txt.encode()).hexdigest()


rec = dict(schema_version=1, cycle=82, agent="worker", run_id="run-2026-09-06T000000Z", milestone="M-V5-EAR-1/ear-venv-built-c82",
           reason="READ-ONLY c74 extractor scripts/v4_ear/ear.py imports librosa at _load_mono_16k; the c79-pinned command omits it",
           pinned_command_probe_record="data/v5/ear/ear_probe_c82.json", pinned_command_probe_status="EAR_VENV_PROBE_FAILED",
           deviation="pre-declared c82 P1 amendment: pip install librosa into workspace/ear_venv AFTER the pinned build; c79 receipt sha no longer matches by design",
           amend_command='workspace/ear_venv/bin/pip install --no-cache-dir "librosa"', abort_ceiling_pct=CEILING, steps=[])
pre_txt, pre_sha = freeze(PY)
main_pre = freeze(Path("/usr/bin/python3"))[1]
rec.update(pip_freeze_sha256_pre=pre_sha, main_env_pip_freeze_sha256_pre=main_pre, df_pre=df())
rec["steps"].append(dict(step="open", df=rec["df_pre"]))
if rec["df_pre"]["used_pct"] >= CEILING:
    rec["status"] = "EAR_VENV_AMEND_ABORTED_DF"
    OUT.write_text(json.dumps(rec, sort_keys=True, indent=2) + "\n")
    sys.exit(3)
t0 = datetime.datetime.utcnow()
r = subprocess.run([str(PIP), "install", "--no-cache-dir", "librosa"], capture_output=True, text=True)
rec["steps"].append(dict(step="pip_install_librosa", rc=r.returncode, wall_s=round((datetime.datetime.utcnow() - t0).total_seconds(), 1),
                         stdout_tail=r.stdout[-1200:], stderr_tail=r.stderr[-600:], df=df()))
post_txt, post_sha = freeze(PY)
FREEZE_OUT.write_text(post_txt)
main_post = freeze(Path("/usr/bin/python3"))[1]
probe = subprocess.run([str(PY), "-c", "import librosa, soundfile, numpy, tensorflow, tensorflow_hub, pyloudnorm, importlib.metadata as m; "
                        "print(json.dumps({p: m.version(p) for p in ['librosa','soundfile','numpy','tensorflow','tensorflow_hub','pyloudnorm']}))"
                        .replace("import librosa", "import json, librosa")], capture_output=True, text=True)
rec.update(pip_freeze_sha256_post=post_sha, pip_freeze_path_amended=str(FREEZE_OUT), n_packages_post=len(post_txt.splitlines()),
           added_packages=sorted(set(post_txt.splitlines()) - set(pre_txt.splitlines())),
           main_env_pip_freeze_sha256_post=main_post, main_env_unchanged=(main_pre == main_post),
           import_probe_rc=probe.returncode, import_probe_stdout=probe.stdout.strip()[-600:], import_probe_stderr_tail=probe.stderr[-300:],
           df_final=df(), venv_size_bytes=sum(p.stat().st_size for p in VENV.rglob("*") if p.is_file()), finished_utc=now())
rec["status"] = "EAR_VENV_AMENDED" if (r.returncode == 0 and probe.returncode == 0 and rec["df_final"]["used_pct"] < CEILING) else "EAR_VENV_AMEND_FAILED"
OUT.write_text(json.dumps(rec, sort_keys=True, indent=2) + "\n")
print(json.dumps({k: rec[k] for k in ("status", "pip_freeze_sha256_pre", "pip_freeze_sha256_post", "added_packages", "main_env_unchanged", "df_pre", "df_final", "import_probe_stdout")}, indent=1))
sys.exit(0 if rec["status"] == "EAR_VENV_AMENDED" else 1)
