#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-28T05:20:00Z
# cycle: 4
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-TEX-1/panel
# ---
"""CLI: texture_distance --a X.wav --b Y.wav --out results.json"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

import numpy as np
import soundfile as sf

from .panel import texture_distance


def _load(path: pathlib.Path) -> tuple[np.ndarray, int]:
    audio, sr = sf.read(str(path), always_2d=True)
    # (samples, channels) -> for mel/rms we mono-mix inside; keep native shape
    return audio.astype(np.float32), int(sr)


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--a", required=True, type=pathlib.Path)
    p.add_argument("--b", required=True, type=pathlib.Path)
    p.add_argument("--out", required=True, type=pathlib.Path)
    args = p.parse_args(argv)

    a, sr_a = _load(args.a)
    b, sr_b = _load(args.b)
    result = texture_distance(a, b, sr_a, sr_b=sr_b)
    result["_inputs"] = {"a": str(args.a), "b": str(args.b)}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
