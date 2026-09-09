#!/usr/bin/python3
"""c83 S5 — INFORMATIONAL ear scoring of the 15 v4 gen renders + interpolation demo through the amended isolated ear venv.

created: 2026-09-06T21:00:00Z
cycle: 83
run_id: run-2026-09-06T000000Z
agent: worker
milestone: M-V5-GEN-1/gen-renders-ear-scored-informational-c83

Sibling to the READ-ONLY c75 scripts/ear/score_gen_batch.py (untouched). Precondition (asserted): the amended receipt
data/v5/ear/env_pin_ear_venv_c82_amended.json exists and data/v5/ear/ear_probe_c83.json == EAR_VENV_REPRODUCES_CACHE.
For each data/v4/gen/iteration_0{1,2,3}/*/ab_mix.wav and data/v4/gen/interpolation_demo/*/ab_mix.wav: VGGish embeddings via
the venv subprocess running the READ-ONLY c74 extractor (scripts/v4_ear/ear._load_mono_16k + _embed_song), then the c76 v2
wider-linear calibration (READ-ONLY scripts/ear/v4_ear_v2.score_audio_v2) against the FRESH exemplar signatures of
data/v5/ear/ear_probe_c82_fresh_embeddings.npz (the c82 gate's shared raw ceiling). Writes a SIBLING ear_score_v5.json next to
each ab_mix.wav (manifests + WAVs byte-identical, asserted) and a score table. Run x2 into fresh mkdtemp (--table-out) for byte-det.
INFORMATIONAL: L119 is infeasible under VGGish (c76 proof); FD-6 operator ear governs LANDS; no M-V5-GEN-1 passer is declared;
M-V5-GEN-1 stays gated on M-V5-RULES-1. Discipline: /usr/bin/python3 guard; no PRNG; no sidecar_nonfactor; no VST3 state APIs.
"""
from __future__ import annotations

import argparse
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
os.chdir(_WS)
sys.path.insert(0, str(_WS))
import numpy as np  # noqa: E402
from scripts.ear import v4_ear as V1  # noqa: E402  READ-ONLY (c74)
from scripts.ear import v4_ear_v2 as V2  # noqa: E402  READ-ONLY (c76)
from scripts.v4_ear import ear as E  # noqa: E402  READ-ONLY (c74 extractor short ids)

VENV_PY = Path("workspace/ear_venv/bin/python")
RECEIPT = Path("data/v5/ear/env_pin_ear_venv_c82_amended.json")
PROBE = Path("data/v5/ear/ear_probe_c83.json")
FRESH = Path("data/v5/ear/ear_probe_c82_fresh_embeddings.npz")
TABLE_DEFAULT = Path("data/v5/gen/gen_render_ear_scores_c83.json")
ENV_PIN = "2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca"
_PINS = {"PYTHONHASHSEED": "0", "SOURCE_DATE_EPOCH": "1756463424", "TZ": "UTC", "LC_ALL": "C.UTF-8",
         "OMP_NUM_THREADS": "1", "MKL_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1", "TF_ENABLE_ONEDNN_OPTS": "0",
         "TF_DETERMINISTIC_OPS": "1", "TF_CPP_MIN_LOG_LEVEL": "3"}
WORKER = r"""
import sys, json, numpy as np
from pathlib import Path
sys.path.insert(0, sys.argv[1])
from scripts.v4_ear import ear as E   # READ-ONLY c74 extractor
paths = json.loads(Path(sys.argv[2]).read_text())
out = {}
for key, rel in paths.items():
    out[key] = E._embed_song(E._load_mono_16k(Path(sys.argv[1]) / rel))
np.savez(sys.argv[3], **out)
"""


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def render_list(globs: list | None = None) -> list:
    rows = []
    if globs:  # c84 additive: score an arbitrary render set (e.g. data/v5/gen/iteration_01/*/ab_mix.wav)
        wavs = sorted(w for g in globs for w in Path(".").glob(g))
    else:
        wavs = sorted(Path("data/v4/gen").glob("iteration_0*/*/ab_mix.wav")) + sorted(Path("data/v4/gen/interpolation_demo").glob("*/ab_mix.wav"))
    for w in wavs:
        rows.append({"key": w.parent.parent.name + "/" + w.parent.name, "wav": str(w), "manifest": str(w.with_name("ab_mix.manifest.json"))})
    return rows


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--table-out", type=Path, default=TABLE_DEFAULT)
    ap.add_argument("--no-siblings", action="store_true", help="do not write per-render ear_score_v5.json (byte-det second run)")
    ap.add_argument("--renders-glob", action="append", default=None, help="c84 additive: glob(s) of ab_mix.wav to score instead of the c83 v4 set")
    a = ap.parse_args(argv)
    assert RECEIPT.exists(), "SCORING_BLOCKED_ON_RECEIPT: amended receipt absent"
    assert json.loads(PROBE.read_text())["status"] == "EAR_VENV_REPRODUCES_CACHE", "SCORING_BLOCKED_ON_RECEIPT: c83 probe not REPRODUCES_CACHE"
    assert VENV_PY.exists()
    rows = render_list(a.renders_glob)
    assert rows, "no renders matched"
    pre = {r["wav"]: _sha(Path(r["wav"])) for r in rows}
    pre.update({r["manifest"]: _sha(Path(r["manifest"])) for r in rows})
    td = Path(tempfile.mkdtemp(prefix="score_gen_v5_"))
    (td / "paths.json").write_text(json.dumps({r["key"]: r["wav"] for r in rows}))
    env = dict(os.environ); env.update(_PINS)
    r = subprocess.run([str(VENV_PY), "-c", WORKER, str(_WS), str(td / "paths.json"), str(td / "emb.npz")], env=env, capture_output=True, text=True)
    if r.returncode != 0:
        rec = {"schema_version": 1, "agent": "worker", "cycle": 83, "status": "SCORING_EXTRACTOR_FAILED", "stderr_tail": r.stderr[-2000:]}
        a.table_out.parent.mkdir(parents=True, exist_ok=True)
        a.table_out.write_text(json.dumps(rec, sort_keys=True, indent=2) + "\n")
        print("SCORING_EXTRACTOR_FAILED", r.stderr[-600:])
        return 4
    z = np.load(td / "emb.npz")
    fz = np.load(FRESH)
    ex_ids = [x[0] for x in E.EXEMPLARS]
    b4_ids = [x[0] for x in E.BAND_4_SPOT_CHECK]
    fresh_sig = {k: fz[k].astype("float64").tolist() for k in ex_ids}
    raw = {}
    for held in fresh_sig:
        rest = {k: v for k, v in fresh_sig.items() if k != held}
        raw[held] = V1._max_over_exemplar_windows(fresh_sig[held], rest)
    raw_max = max(raw.values())
    loo = V2.leave_one_out_v2(V1.load_exemplar_set(), exemplar_signatures=fresh_sig)
    band4 = {k: round(V2.score_audio_v2(fz[k].astype("float64").tolist(), fresh_sig, raw_max), 4) for k in b4_ids}
    scores = {}
    for rw in rows:
        emb = z[rw["key"]].astype("float64")
        stat = V1._max_over_exemplar_windows(emb.tolist(), fresh_sig)
        sc = V2.calibrate_wider_linear(stat, raw_max)
        scores[rw["key"]] = {"ear_score_v2": round(sc, 4), "raw_statistic": round(float(stat), 6), "n_windows": int(emb.shape[0]),
                             "wav_sha256": pre[rw["wav"]], "manifest_sha256": pre[rw["manifest"]], "ge_6": bool(sc >= 6.0)}
        if not a.no_siblings:
            sib = {"schema_version": 1, "agent": "worker", "cycle": 83, "run_id": "run-2026-09-06T000000Z",
                   "milestone": "M-V5-GEN-1/gen-renders-ear-scored-informational-c83", "informational_only": True,
                   "framing": "INFORMATIONAL: L119 infeasible under VGGish (c76); FD-6 operator ear governs LANDS; not an M-V5-GEN-1 passer declaration",
                   "calibration": V2.module_env_manifest_v2(), "exemplar_signatures": "data/v5/ear/ear_probe_c82_fresh_embeddings.npz (fresh, venv)",
                   "shared_raw_ceiling": round(raw_max, 6), "venv_receipt": str(RECEIPT), "env_pins": _PINS, **scores[rw["key"]]}
            Path(rw["wav"]).with_name("ear_score_v5.json").write_text(json.dumps(sib, sort_keys=True, indent=2) + "\n")
    post = {p: _sha(Path(p)) for p in pre}
    assert post == pre, "ab_mix.wav / manifest bytes changed — must be byte-identical"
    gen15 = [k for k in scores if not k.startswith("interpolation_demo")]
    table = {"schema_version": 1, "agent": "worker", "cycle": 83, "run_id": "run-2026-09-06T000000Z",
             "milestone": "M-V5-GEN-1/gen-renders-ear-scored-informational-c83", "status": "GEN_RENDERS_SCORED_INFORMATIONAL",
             "informational_only": True, "env_pin_sha256": ENV_PIN, "env_pins_subprocess": _PINS,
             "framing": "INFORMATIONAL: L119 infeasible under VGGish (c76 proof); FD-6 operator ear governs LANDS; M-V5-GEN-1 stays gated on M-V5-RULES-1; no passer declared",
             "venv_receipt": str(RECEIPT), "venv_receipt_sha256": _sha(RECEIPT), "probe_c83_status": "EAR_VENV_REPRODUCES_CACHE",
             "fresh_exemplar_npz_sha256": _sha(FRESH), "calibration": V2.module_env_manifest_v2(), "shared_raw_ceiling": round(raw_max, 6),
             "exemplar_loo_v2_context": {k: round(v, 4) for k, v in loo.items()}, "band4_v2_context": band4,
             "scores": scores, "n_scored": len(scores), "n_gen_renders": len(gen15), "n_gen_ge_6": sum(scores[k]["ge_6"] for k in gen15),
             "interpolation_demo": {k: scores[k] for k in scores if k.startswith("interpolation_demo")},
             "embeddings_npz_sha256": _sha(td / "emb.npz"), "wav_and_manifest_bytes_unchanged": post == pre}
    a.table_out.parent.mkdir(parents=True, exist_ok=True)
    a.table_out.write_text(json.dumps(table, sort_keys=True, indent=2) + "\n")
    print(json.dumps({k: table[k] for k in ("n_scored", "n_gen_ge_6", "exemplar_loo_v2_context", "band4_v2_context")}, indent=1))
    for k, v in scores.items():
        print(f"  {v['ear_score_v2']:6.3f} raw={v['raw_statistic']:.4f} {k}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
