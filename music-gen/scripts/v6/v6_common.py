#!/usr/bin/python3
"""v6 Phase 1A shared helpers — hashing, atomic JSON, env/version record, audio-file discovery.

created: 2026-10-04
milestone: M-V6-SCORECARD-1A

Small, dependency-light module imported by `embed_audio.py`, `distribution_metrics.py`
and `baseline_real_vs_real.py`. Nothing here loads models or touches the network.

Conventions enforced here (binding for v6):
  * every output JSON carries "schema_version", "env" (pins + package versions) and the
    sha16 (first 16 hex of sha256) of every input file, and is written atomically;
  * JSON keys are sorted so byte-identical reruns are diff-able.
"""
from __future__ import annotations

import hashlib
import json
import os
import platform
import sys
from pathlib import Path
from typing import Iterable, Sequence

ENV_PIN_KEYS = ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS",
                "PYTHONHASHSEED", "TZ", "LC_ALL", "HF_HUB_OFFLINE", "TRANSFORMERS_OFFLINE")
AUDIO_EXTS = (".wav", ".flac", ".mp3", ".ogg", ".opus", ".m4a", ".aiff", ".aif")
WS = Path(__file__).resolve().parent.parent.parent  # .../music-gen


def sha256_file(path: str | os.PathLike, chunk: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(chunk), b""):
            h.update(block)
    return h.hexdigest()


def sha16_of(sha256_hex: str) -> str:
    return sha256_hex[:16]


def package_versions() -> dict:
    out = {"python": platform.python_version(), "executable": sys.executable}
    for name in ("numpy", "scipy", "sklearn", "torch", "transformers", "librosa", "soundfile"):
        try:
            mod = __import__(name)
            out[name] = str(getattr(mod, "__version__", "?"))
        except Exception as exc:  # pragma: no cover - version probe only
            out[name] = f"unavailable:{type(exc).__name__}"
    return out


def env_record() -> dict:
    """Pins + versions recorded under "env" in every v6 output JSON."""
    return {
        "pins": {k: os.environ.get(k) for k in ENV_PIN_KEYS},
        "versions": package_versions(),
        "platform": platform.platform(),
    }


def write_json_atomic(path: str | os.PathLike, obj: dict) -> None:
    """Sorted-key JSON, written to <path>.tmp then os.replace()'d into place."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, sort_keys=True, indent=2, default=_json_default)
        fh.write("\n")
    os.replace(tmp, path)


def _json_default(o):
    import numpy as np
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    if isinstance(o, Path):
        return str(o)
    raise TypeError(f"not JSON serialisable: {type(o).__name__}")


def read_json(path: str | os.PathLike) -> dict:
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def iter_audio_files(inputs: Iterable[str | os.PathLike],
                     exts: Sequence[str] = AUDIO_EXTS) -> list[Path]:
    """Expand files/dirs into a sorted, de-duplicated list of audio paths (dirs recurse)."""
    found: set[Path] = set()
    for item in inputs:
        p = Path(item)
        if p.is_dir():
            for q in p.rglob("*"):
                if q.is_file() and q.suffix.lower() in exts:
                    found.add(q.resolve())
        elif p.is_file():
            found.add(p.resolve())
        else:
            raise FileNotFoundError(f"input not found: {p}")
    return sorted(found)


def iter_npz_files(inputs: Iterable[str | os.PathLike]) -> list[Path]:
    return iter_audio_files(inputs, exts=(".npz",))


def set_torch_determinism(threads: int = 4, seed: int = 0) -> None:
    import torch
    torch.set_num_threads(threads)
    torch.manual_seed(seed)
    torch.use_deterministic_algorithms(True, warn_only=True)
