#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-28T10:45:00Z
# cycle: 9
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-TEX-1/stage-by-stage
# ---
"""Measure the M-TEX-1/panel 8-key texture panel across all three ordered
pairs of the (original, bare_midi, effects_layered) stages.

Ordered pairs (fixed):
    (original,   bare_midi)
    (original,   effects_layered)
    (bare_midi,  effects_layered)

Writes a TSV with three rows and columns:
    a_stage  b_stage  mel_l1_db  spectral_centroid_rmse_hz  rms_env_rmse
    lufs_m_rmse_lu  embedding_cosine_distance  embedding_rung  sr_hz
    n_samples_compared

Explicitly refuses to compute or emit any aggregate.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Dict, Sequence, Tuple

for _v in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
os.environ.setdefault("TF_DETERMINISTIC_OPS", "1")
os.environ.setdefault("PYTHONHASHSEED", "0")

assert sys.executable == "/usr/bin/python3", sys.executable

import numpy as np
import soundfile as sf

# Ensure workspace on path so `scripts.texture.panel` resolves.
_WS = Path(__file__).resolve().parents[2]
if str(_WS) not in sys.path:
    sys.path.insert(0, str(_WS))

from scripts.texture.panel import texture_distance, PUBLIC_KEYS

STAGES: Tuple[str, str, str] = ("original", "bare_midi", "effects_layered")

ORDERED_PAIRS: Tuple[Tuple[str, str], ...] = (
    ("original", "bare_midi"),
    ("original", "effects_layered"),
    ("bare_midi", "effects_layered"),
)

# 8-key contract exposed by M-TEX-1/panel. This is the ONLY allowed key
# set; anything else is a panel regression.
EXPECTED_KEYS = tuple(PUBLIC_KEYS)  # spectral(2) + envelope(2) + embedding(2) + sr + n_samples

# Refusable aggregate keys (defensive — panel already refuses at its own
# layer). If any of these ever appear in a measurement dict we halt.
BANNED_AGGREGATE_KEYS = ("overall", "combined", "mean", "mean_score",
                         "weighted", "aggregate", "score", "total")

SELF_TOL_NUMERIC = 1e-6
SELF_TOL_EMBEDDING = 1e-4


def load_stage(path: Path, sr_expected: int = 44100) -> np.ndarray:
    x, sr = sf.read(str(path), always_2d=True)
    if sr != sr_expected:
        raise RuntimeError(f"{path}: expected sr={sr_expected}, got {sr}")
    if x.shape[1] == 1:
        x = np.concatenate([x, x], axis=1)
    return x.astype(np.float32)


def assert_non_silent(x: np.ndarray, tag: str) -> None:
    peak = float(np.abs(x).max())
    if peak <= 1e-4:
        raise RuntimeError(f"stage '{tag}' is silent (peak={peak:.3e}); "
                           "refusing to measure")


def assert_self_distance(x: np.ndarray, sr: int, tag: str) -> Dict[str, float]:
    d = texture_distance(x, x, sr)
    for k in ("mel_l1_db", "spectral_centroid_rmse_hz",
              "rms_env_rmse", "lufs_m_rmse_lu"):
        v = float(d[k])
        if not np.isfinite(v) or v > SELF_TOL_NUMERIC:
            raise RuntimeError(
                f"panel regression on stage '{tag}': self-distance "
                f"{k}={v} > tol {SELF_TOL_NUMERIC}. Escalate to "
                f"M-TEX-1/panel.")
    cos = d.get("embedding_cosine_distance", None)
    if cos is not None:
        v = float(cos)
        if not np.isfinite(v) or v > SELF_TOL_EMBEDDING:
            raise RuntimeError(
                f"panel regression on stage '{tag}': self-embedding "
                f"cosine={v} > tol {SELF_TOL_EMBEDDING}. Escalate to "
                f"M-TEX-1/panel.")
    return d


def assert_key_contract(d: Dict[str, object], tag: str) -> None:
    keys = set(d.keys())
    if keys != set(EXPECTED_KEYS):
        raise RuntimeError(
            f"panel contract violation at '{tag}': keys are {sorted(keys)}, "
            f"expected {sorted(EXPECTED_KEYS)}")
    for banned in BANNED_AGGREGATE_KEYS:
        if banned in keys:
            raise RuntimeError(
                f"panel contract violation at '{tag}': banned aggregate "
                f"key '{banned}' present")


def measure_pairs(stage_wavs: Dict[str, Path], sr: int = 44100) -> Sequence[Dict[str, object]]:
    """Measure the 8-key panel on each of the three ordered pairs."""
    loaded = {name: load_stage(path, sr_expected=sr)
              for name, path in stage_wavs.items()}

    for name, arr in loaded.items():
        assert_non_silent(arr, name)
        d = assert_self_distance(arr, sr, name)
        assert_key_contract(d, f"self:{name}")

    rows = []
    for a_name, b_name in ORDERED_PAIRS:
        a = loaded[a_name]
        b = loaded[b_name]
        n = min(a.shape[0], b.shape[0])
        d = texture_distance(a[:n], b[:n], sr)
        assert_key_contract(d, f"pair:{a_name}->{b_name}")
        for k in ("mel_l1_db", "spectral_centroid_rmse_hz",
                  "rms_env_rmse", "lufs_m_rmse_lu",
                  "embedding_cosine_distance"):
            v = d.get(k, None)
            if v is None:
                continue
            if not np.isfinite(float(v)):
                raise RuntimeError(
                    f"non-finite {k}={v} on pair {a_name}->{b_name}. "
                    "Halting per brief.")
        row = {"a_stage": a_name, "b_stage": b_name}
        row.update({k: d[k] for k in EXPECTED_KEYS})
        rows.append(row)
    return rows


def write_tsv(rows: Sequence[Dict[str, object]], out_path: Path) -> None:
    header = ["a_stage", "b_stage"] + list(EXPECTED_KEYS)
    lines = ["\t".join(header)]
    for row in rows:
        vals = []
        for k in header:
            v = row.get(k, "")
            if isinstance(v, float):
                vals.append(f"{v:.9g}")
            else:
                vals.append(str(v))
        lines.append("\t".join(vals))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines) + "\n")


def main():  # pragma: no cover
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--original", required=True)
    ap.add_argument("--bare-midi", required=True)
    ap.add_argument("--effects-layered", required=True)
    ap.add_argument("--out-tsv", required=True)
    args = ap.parse_args()
    stages = {
        "original": Path(args.original),
        "bare_midi": Path(args.bare_midi),
        "effects_layered": Path(args.effects_layered),
    }
    rows = measure_pairs(stages, sr=44100)
    write_tsv(rows, Path(args.out_tsv))
    print(f"wrote {args.out_tsv} — {len(rows)} rows × {len(EXPECTED_KEYS)+2} cols")


if __name__ == "__main__":
    main()
