# M-SEP-1 scope-closure — UMXHQ byte-determinism probe.
#
# created: 2026-08-28
# cycle: 5 (scope-closure)
# run_id: run-2026-08-28T040704Z
# agent: worker (clone-0 of fork 22b8c654f616)
# milestone: M-SEP-1/alternative
#
# Purpose: rerun openunmix UMXHQ on data/separation/synth_mix/gt/synth_030s/mix.wav
# under a *hard-pinned* single-threaded contract and diff each 4-stem WAV
# against the committed stems at data/separation/runs/openunmix/synth_030s/.
# Structurally parallel to scripts/separation/stale/_determinism_check.py
# (the htdemucs template), but expanded to all 4 stems + emits determinism_report.tsv
# and pinned_rms.json for the integration-test invariant.
#
# Interpreter: /usr/bin/python3 (asserted). Env vars set BEFORE importing torch.
#
# Outputs:
#   data/separation/runs/openunmix/synth_030s_verify/{drums,bass,other,vocals}.wav
#   data/separation/runs/openunmix/synth_030s_verify/determinism_report.tsv
#   data/separation/runs/openunmix/synth_030s/pinned_rms.json
"""UMXHQ byte-determinism probe for M-SEP-1 scope closure."""
from __future__ import annotations

# --- hard-pin threads BEFORE any BLAS-linked import ---
import os
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"

import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np
import soundfile as sf
import torch

assert sys.executable == "/usr/bin/python3", sys.executable
torch.set_num_threads(1)
torch.manual_seed(0)

# Reuse the campaign's torch.hub cache so no fresh weight fetch is needed.
ROOT = Path("/home/user/long-exposure-runs/music-gen")
os.environ.setdefault("TORCH_HOME", str(ROOT / "workspace/_probe/torch_home"))

import openunmix  # noqa: E402

STEM_ORDER = ["vocals", "drums", "bass", "other"]
MIX_WAV = ROOT / "data/separation/synth_mix/gt/synth_030s/mix.wav"
COMMITTED = ROOT / "data/separation/runs/openunmix/synth_030s"
VERIFY_DIR = ROOT / "data/separation/runs/openunmix/synth_030s_verify"
REPORT_TSV = VERIFY_DIR / "determinism_report.tsv"
PINNED_JSON = COMMITTED / "pinned_rms.json"


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def dbfs(x: float) -> float:
    return 20.0 * math.log10(x + 1e-12)


def rms(a: np.ndarray) -> float:
    return float(np.sqrt(np.mean(np.square(a.astype(np.float64)))))


def separate_to(out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    sep = openunmix.umxhq(targets=STEM_ORDER, niter=1, residual=False)
    sep.eval()
    y, sr = sf.read(str(MIX_WAV), always_2d=True)
    assert sr == 44100, sr
    if y.shape[1] == 1:
        y = np.concatenate([y, y], axis=1)
    wav = torch.from_numpy(y.T.astype(np.float32)).unsqueeze(0)
    with torch.no_grad():
        est = sep(wav)
    arr = est[0].numpy()
    for i, name in enumerate(STEM_ORDER):
        stem = arr[i].T  # (samples, channels)
        sf.write(str(out_dir / f"{name}.wav"), stem.astype(np.float32), sr, subtype="FLOAT")


def main() -> int:
    # Rerun UMXHQ under the hard-pinned single-thread contract.
    separate_to(VERIFY_DIR)

    rows = ["\t".join(["stem", "bytes_identical", "arrays_equal",
                       "rms_diff_dbfs", "peak_diff_dbfs", "n_samples_differ",
                       "committed_rms", "committed_rms_dbfs"])]
    pinned = {"generated_by": "scripts/separation/verify_umxhq_determinism.py",
              "committed_stems_dir": str(COMMITTED.relative_to(ROOT)),
              "sample_rate": 44100, "stems": {}}
    n_identical = 0
    max_rms_diff_dbfs = -float("inf")

    for stem in STEM_ORDER:
        a_path = COMMITTED / f"{stem}.wav"
        b_path = VERIFY_DIR / f"{stem}.wav"
        bytes_identical = sha256(a_path) == sha256(b_path)
        a, _ = sf.read(str(a_path), always_2d=True)
        b, _ = sf.read(str(b_path), always_2d=True)
        # Length-align defensively (should always be equal).
        n = min(len(a), len(b))
        a = a[:n].astype(np.float64)
        b = b[:n].astype(np.float64)
        arrays_equal = bool(np.array_equal(a, b))
        diff = a - b
        rms_diff = rms(diff)
        peak_diff = float(np.max(np.abs(diff))) if diff.size else 0.0
        n_diff = int(np.sum(np.any(a != b, axis=1))) if diff.size else 0
        committed_rms = rms(a)
        rms_diff_db = dbfs(rms_diff)
        max_rms_diff_dbfs = max(max_rms_diff_dbfs, rms_diff_db)
        if bytes_identical:
            n_identical += 1
        rows.append("\t".join([
            stem,
            "yes" if bytes_identical else "no",
            "yes" if arrays_equal else "no",
            f"{rms_diff_db:.2f}",
            f"{dbfs(peak_diff):.2f}",
            str(n_diff),
            f"{committed_rms:.6e}",
            f"{dbfs(committed_rms):.2f}",
        ]))
        pinned["stems"][stem] = {
            "rms": committed_rms,
            "rms_dbfs": dbfs(committed_rms),
            "sha256": sha256(a_path),
        }

    REPORT_TSV.write_text("\n".join(rows) + "\n")
    PINNED_JSON.write_text(json.dumps(pinned, indent=2) + "\n")
    # Grep-able single-line summary the auditor can pin.
    print(f"UMXHQ_DETERMINISM: identical={n_identical}/4 "
          f"max_rms_diff_dbfs={max_rms_diff_dbfs:.2f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
