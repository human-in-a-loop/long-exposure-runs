"""
Called INSIDE the quarantined venv (workspace/basic_pitch_venv).
Runs basic-pitch prediction on a WAV and writes a MIDI plus a JSONL
of note events {pitch, onset_s, offset_s, velocity, is_drum:false}.

Usage: python3 _bp_call.py <input_wav> <out_midi> <out_jsonl>
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

# Deterministic-ish TF: single-threaded, fixed seeds.
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")
os.environ.setdefault("TF_ENABLE_ONEDNN_OPTS", "0")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

# Guard: must be the venv interpreter, not /usr/bin/python3.
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
    if len(sys.argv) != 4:
        raise SystemExit("usage: _bp_call.py <wav> <out_midi> <out_jsonl>")
    wav = sys.argv[1]
    out_midi = Path(sys.argv[2])
    out_jsonl = Path(sys.argv[3])
    out_midi.parent.mkdir(parents=True, exist_ok=True)
    out_jsonl.parent.mkdir(parents=True, exist_ok=True)

    model_output, midi_data, note_events = predict(
        wav, model_or_model_path=ICASSP_2022_MODEL_PATH
    )
    # note_events: list of (start_time_s, end_time_s, pitch, amplitude, [pitch_bends])
    # midi_data is a pretty_midi.PrettyMIDI.
    midi_data.write(str(out_midi))

    rows = []
    for ev in note_events:
        s, e, pitch, amp = ev[0], ev[1], int(ev[2]), float(ev[3])
        # Map amplitude in [0,1] to MIDI velocity in [1,127].
        vel = max(1, min(127, int(round(amp * 127))))
        rows.append({
            "pitch": pitch,
            "onset_s": round(float(s), 6),
            "offset_s": round(float(e), 6),
            "velocity": vel,
            "is_drum": False,
        })
    rows.sort(key=lambda r: (r["onset_s"], r["pitch"]))
    payload = "\n".join(json.dumps(r, sort_keys=True, separators=(",", ":")) for r in rows) + "\n"
    out_jsonl.write_text(payload)
    print(f"basic-pitch: {len(rows)} notes -> {out_midi} + {out_jsonl}")


if __name__ == "__main__":
    main()
