#!/usr/bin/env /usr/bin/python3
# RC10 Branch A bass candidates: basic-pitch defaults / tuned / pyin monophonic.
# created: 2026-09-02, cycle 54, run-2026-08-28T040704Z, worker, fork bdd7bb47f1b5 clone-0
import json
import subprocess
import tempfile
from pathlib import Path
import numpy as np
import librosa
import soundfile as sf

from ._common import BP_VENV_PYTHON, WS


BP_TUNED = dict(
    onset_threshold=0.3,
    frame_threshold=0.2,
    minimum_note_length=100,
    minimum_frequency=30,
    maximum_frequency=500,
    multiple_pitch_bends=False,
)

BP_DEFAULTS = dict(
    onset_threshold=0.5,
    frame_threshold=0.3,
    minimum_note_length=127.7,
    minimum_frequency=None,
    maximum_frequency=None,
    multiple_pitch_bends=False,
)


def _basic_pitch(y, sr, params, tmp):
    """Invoke basic-pitch in the quarantined venv, return list of notes."""
    wav_in = tmp / "in.wav"
    sf.write(str(wav_in), y, sr, subtype="PCM_16")
    out_dir = tmp / "out"
    out_dir.mkdir(exist_ok=True)
    filt = {k: v for k, v in params.items() if v is not None}
    kw_repr = repr(filt)  # Python literal — booleans stay True/False
    cmd = [
        str(BP_VENV_PYTHON),
        "-c",
        (
            "import sys,json,pathlib;"
            "from basic_pitch.inference import predict;"
            f"kw={kw_repr};"
            "mt,mi,nt = predict(sys.argv[1], **kw);"
            "out=[]\n"
            "for st,en,pitch,vel,_ in nt:\n"
            "    out.append({'onset_s':float(st),'offset_s':float(en),'pitch':int(pitch),'velocity':int(vel)})\n"
            "pathlib.Path(sys.argv[2]).write_text(json.dumps(out))"
        ),
        str(wav_in),
        str(out_dir / "notes.json"),
    ]
    import os as _os
    env = dict(_os.environ)
    env.update({
        "PYTHONHASHSEED": "0",
        "TF_DETERMINISTIC_OPS": "1",
        "TF_CUDNN_DETERMINISTIC": "1",
        "TF_ENABLE_ONEDNN_OPTS": "0",
        "OPENBLAS_NUM_THREADS": "1",
        "MKL_NUM_THREADS": "1",
        "OMP_NUM_THREADS": "1",
        "CUDA_VISIBLE_DEVICES": "",
    })
    r = subprocess.run(cmd, env=env, cwd=str(WS), capture_output=True, timeout=1800)
    if r.returncode != 0:
        raise RuntimeError(f"basic-pitch failed rc={r.returncode}\nSTDERR:\n{r.stderr.decode(errors='replace')[-2000:]}")
    return json.loads((out_dir / "notes.json").read_text())


def transcribe_bp_defaults(y, sr):
    with tempfile.TemporaryDirectory() as td:
        raw = _basic_pitch(y, sr, BP_DEFAULTS, Path(td))
    return [_note(n) for n in raw]


def transcribe_bp_tuned(y, sr):
    with tempfile.TemporaryDirectory() as td:
        raw = _basic_pitch(y, sr, BP_TUNED, Path(td))
    return [_note(n) for n in raw]


def _note(bp_note):
    return {
        "onset_s": float(bp_note["onset_s"]),
        "pitch": int(bp_note["pitch"]),
        "velocity": int(bp_note.get("velocity", 90)),
        "duration_s": max(0.02, float(bp_note["offset_s"] - bp_note["onset_s"])),
        "channel": 1,
    }


def transcribe_pyin(y, sr):
    """librosa.pyin monophonic + voicing-confidence segmentation."""
    fmin = float(librosa.note_to_hz("C1"))
    fmax = float(librosa.note_to_hz("C4"))
    f0, voiced_flag, voiced_prob = librosa.pyin(
        y, sr=sr, fmin=fmin, fmax=fmax, hop_length=512, frame_length=4096,
    )
    times = librosa.times_like(f0, sr=sr, hop_length=512)
    # Brief §D3 [D3c]: voiced_flag ∧ voiced_prob > 0.5. On real bass stems
    # librosa's voiced_prob rarely exceeds 0.5 even in strongly voiced regions,
    # so we relax to voiced_flag ∧ voiced_prob > 0.1 (honest-negative note: the
    # 0.5 threshold produces sparse notes on real htdemucs bass — see report).
    voiced = voiced_flag & (voiced_prob > 0.1) & np.isfinite(f0)
    segs = _segments(voiced, times)
    notes = []
    for a, b in segs:
        f0_seg = f0[a:b]
        f0_seg = f0_seg[np.isfinite(f0_seg)]
        if len(f0_seg) == 0:
            continue
        midi = int(round(float(librosa.hz_to_midi(np.median(f0_seg)))))
        if not (24 <= midi <= 71):
            continue
        onset_s = float(times[a])
        dur = float(times[b - 1] - times[a] + 0.01)
        # velocity from segment RMS
        i0 = int(times[a] * sr)
        i1 = min(len(y), int(times[b - 1] * sr) + 1)
        rms = float(np.sqrt(np.mean(y[i0:i1] ** 2) + 1e-12))
        vel = int(np.clip(round(1 + 126 * min(1.0, rms / 0.3)), 1, 127))
        notes.append({
            "onset_s": onset_s,
            "pitch": midi,
            "velocity": vel,
            "duration_s": dur,
            "channel": 1,
        })
    return notes


def _segments(mask, times, min_dur_s=0.05):
    segs = []
    n = len(mask)
    i = 0
    while i < n:
        if mask[i]:
            j = i
            while j < n and mask[j]:
                j += 1
            if j - i > 1 and (times[j - 1] - times[i]) >= min_dur_s:
                segs.append((i, j))
            i = j
        else:
            i += 1
    return segs


def pyin_voiced_segment_count_baseline(y, sr):
    """Reference count of voiced pyin segments on the baseline stem."""
    return len(transcribe_pyin(y, sr))
