#!/usr/bin/python3
"""c81 P1.4 — isolated ear-venv VGGish probe (subprocess; main env untouched).

created: 2026-09-06T17:05:00Z
cycle: 81
run_id: run-2026-09-06T000000Z
agent: worker
milestone: M-V5-EAR-1/ear-venv-built-c81 (or ear-venv-blocked-disk-c81)

Runs the READ-ONLY c74 extractor (scripts/v4_ear/ear.py: 16 kHz mono, 10 s windows @ 5 s hop, VGGish frame
mean-pool) INSIDE workspace/ear_venv by subprocess, x2 into fresh tempfile.mkdtemp(), on the 5 exemplars + 3 band-4
songs of FROZEN data/v4/ear/exemplar_set.json / ear_scores.json, and compares rows to the cached
data/v4/ear/{exemplar_embeddings,band4_embeddings}.npz.
Pre-declared enum: EAR_VENV_REPRODUCES_CACHE iff run1 == run2 AND max |diff| <= 1e-5 on ALL rows;
EAR_VENV_DIFFERS_FROM_CACHE if run1 == run2 but any row differs more (still a valid venv);
EAR_VENV_NONDETERMINISTIC if run1 != run2; EAR_VENV_ABSENT (exit 3) if the venv is not built.
Discipline: /usr/bin/python3 guard; no PRNG; no sidecar_nonfactor; no VST3 state APIs.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

if sys.executable != "/usr/bin/python3" and "SUPPRESS_INTERPRETER_GUARD" not in os.environ:
    print(f"FATAL: expected /usr/bin/python3, got {sys.executable}", file=sys.stderr)
    sys.exit(2)

_WS = Path(__file__).resolve().parent.parent.parent
VENV_PY = _WS / "workspace/ear_venv/bin/python"
OUT = _WS / "data/v5/ear/ear_probe_c81.json"
TOL = 1e-5
_PINS = {"PYTHONHASHSEED": "0", "SOURCE_DATE_EPOCH": "1756463424", "TZ": "UTC", "LC_ALL": "C.UTF-8",
         "OMP_NUM_THREADS": "1", "MKL_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1", "TF_ENABLE_ONEDNN_OPTS": "0",
         "TF_DETERMINISTIC_OPS": "1"}
WORKER = r"""
import sys, numpy as np
from pathlib import Path
sys.path.insert(0, sys.argv[1])
from scripts.v4_ear import ear as E   # READ-ONLY c74 extractor: same exemplar/band-4 paths, 16 kHz, 10 s windows @ 5 s hop
out = {}
for short_id, _name, _band, rel in E.EXEMPLARS:
    out[short_id] = E._embed_song(E._load_mono_16k(Path(sys.argv[1]) / rel))
for short_id, _name, rel in E.BAND_4_SPOT_CHECK:
    out[short_id] = E._embed_song(E._load_mono_16k(Path(sys.argv[1]) / rel))
np.savez(sys.argv[2], **out)
"""


def main() -> int:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    if not VENV_PY.exists():
        rec = {"schema_version": 1, "cycle": 81, "status": "EAR_VENV_ABSENT", "venv_python": str(VENV_PY),
               "reason": "workspace/ear_venv not built (see data/v5/ear/venv_build_c81.json)", "env_pins": _PINS}
        OUT.write_text(json.dumps(rec, sort_keys=True, indent=2) + "\n")
        print("EAR_VENV_ABSENT")
        return 3
    import numpy as np
    env = dict(os.environ); env.update(_PINS)
    runs = []
    for k in (1, 2):
        td = Path(tempfile.mkdtemp(prefix=f"ear_probe_run{k}_"))
        r = subprocess.run([str(VENV_PY), "-c", WORKER, str(_WS), str(td / "emb.npz")], env=env, capture_output=True, text=True)
        if r.returncode != 0:
            rec = {"schema_version": 1, "cycle": 81, "status": "EAR_VENV_PROBE_FAILED", "stderr_tail": r.stderr[-2000:]}
            OUT.write_text(json.dumps(rec, sort_keys=True, indent=2) + "\n")
            print("EAR_VENV_PROBE_FAILED", r.stderr[-500:])
            return 4
        runs.append(td / "emb.npz")
    r1, r2 = np.load(runs[0]), np.load(runs[1])
    same = all(np.array_equal(r1[k], r2[k]) for k in r1.files)
    cache = {}
    for p in ("exemplar_embeddings.npz", "band4_embeddings.npz"):
        z = np.load(_WS / "data/v4/ear" / p)
        cache.update({k: z[k] for k in z.files})
    rows = {}
    for k in r1.files:
        c = cache.get(k)
        rows[k] = {"n_windows_run": int(r1[k].shape[0]), "n_windows_cache": int(c.shape[0]) if c is not None else None,
                   "max_abs_diff_vs_cache": (float(np.max(np.abs(r1[k] - c))) if c is not None and c.shape == r1[k].shape else None)}
    diffs = [v["max_abs_diff_vs_cache"] for v in rows.values()]
    if not same:
        status = "EAR_VENV_NONDETERMINISTIC"
    elif all(d is not None and d <= TOL for d in diffs):
        status = "EAR_VENV_REPRODUCES_CACHE"
    else:
        status = "EAR_VENV_DIFFERS_FROM_CACHE"
    rec = {"schema_version": 1, "cycle": 81, "status": status, "run1_sha256": hashlib.sha256(runs[0].read_bytes()).hexdigest(),
           "run2_sha256": hashlib.sha256(runs[1].read_bytes()).hexdigest(), "run1_eq_run2": same, "tolerance": TOL, "rows": rows,
           "env_pins": _PINS, "venv_python": str(VENV_PY)}
    OUT.write_text(json.dumps(rec, sort_keys=True, indent=2) + "\n")
    print(status, rows)
    return 0


if __name__ == "__main__":
    sys.exit(main())
