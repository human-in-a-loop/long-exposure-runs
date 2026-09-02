"""Inner basic-pitch caller — runs INSIDE workspace/basic_pitch_venv.

Usage: python3 _bp_inner.py <wav> <out_midi> <out_notes_json> <params_json>

Writes a MIDI and a JSON list of note events {pitch, onset_s, offset_s, velocity}.
Deterministic under fixed seeds + single-thread BLAS/TF.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")
os.environ.setdefault("TF_ENABLE_ONEDNN_OPTS", "0")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

# Guard: must be the venv interpreter.
here = Path(sys.executable).resolve()
expected = Path("/home/user/long-exposure-runs/music-gen/workspace/basic_pitch_venv/bin/python3").resolve()
assert here == expected, f"venv guard failed: {here} != {expected}"

import numpy as np
import tensorflow as tf
tf.random.set_seed(0)
np.random.seed(0)
try:
    tf.config.threading.set_intra_op_parallelism_threads(1)
    tf.config.threading.set_inter_op_parallelism_threads(1)
except Exception:
    pass

from basic_pitch.inference import predict
from basic_pitch import ICASSP_2022_MODEL_PATH


def main() -> None:
    if len(sys.argv) != 5:
        raise SystemExit("usage: _bp_inner.py <wav> <out_midi> <out_json> <params_json>")
    wav = sys.argv[1]
    out_midi = Path(sys.argv[2])
    out_json = Path(sys.argv[3])
    params = json.loads(sys.argv[4])

    out_midi.parent.mkdir(parents=True, exist_ok=True)
    out_json.parent.mkdir(parents=True, exist_ok=True)

    # Only pass params the running basic-pitch supports.
    kwargs = {}
    for k in ("onset_threshold", "frame_threshold", "minimum_note_length",
              "minimum_frequency", "maximum_frequency"):
        if k in params and params[k] is not None:
            kwargs[k] = params[k]

    model_output, midi_data, note_events = predict(
        wav, model_or_model_path=ICASSP_2022_MODEL_PATH, **kwargs
    )
    midi_data.write(str(out_midi))

    rows = []
    for ev in note_events:
        s, e, pitch, amp = float(ev[0]), float(ev[1]), int(ev[2]), float(ev[3])
        vel = max(1, min(127, int(round(amp * 127))))
        rows.append({
            "pitch": pitch,
            "onset_s": round(s, 6),
            "offset_s": round(e, 6),
            "velocity": vel,
        })
    rows.sort(key=lambda r: (r["onset_s"], r["pitch"]))
    out_json.write_text(json.dumps(rows, sort_keys=True, separators=(",", ":")))
    print(f"basic-pitch: {len(rows)} notes -> {out_midi} + {out_json}")


if __name__ == "__main__":
    main()
