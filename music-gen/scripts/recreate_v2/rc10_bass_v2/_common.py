#!/usr/bin/env /usr/bin/python3
# RC10 bass v2 shared constants & helpers.
# created: 2026-09-02, cycle 55, run-2026-08-28T040704Z, worker, fork 7cc01d726807 clone-1
import json
import os
import sys
import hashlib
from pathlib import Path

if sys.executable != "/usr/bin/python3":
    raise RuntimeError(f"interpreter guard: expected /usr/bin/python3, got {sys.executable}")

WS = Path(__file__).resolve().parents[3]
FOCUS_V2 = WS / "data/recreate_v2/focus_set_v2.json"
BASELINE_DIR = WS / "data/recreate_v2/baseline"
IMPL_DIR = WS / "data/rc10_bass_v2_impl"
AB_DIR = WS / "data/recreate_v2/ab_pairs"
RUBRIC_HASH = WS / "data/rc10_bass_v2_impl/rubric_hash.txt"
RUBRIC_DOC = WS / "docs/rc10_bass_v2_rubric.md"
V1_SCORECARD = WS / "data/rc10_drums_bass_impl/scorecard.tsv"
SF2 = Path("/usr/share/sounds/sf2/FluidR3_GM.sf2")

# c48 env-var flags default OFF (os.environ.setdefault, do not overwrite operator env)
os.environ.setdefault("PYTHONHASHSEED", "0")
os.environ.setdefault("SOURCE_DATE_EPOCH", "1756463424")
os.environ.setdefault("TZ", "UTC")
os.environ.setdefault("LC_ALL", "C.UTF-8")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")

MIN_DURATION_S = 0.040
FMIN_HZ = 41.203444533148245  # librosa.note_to_hz("E1")
FMAX_HZ = 329.6275569128699   # librosa.note_to_hz("E4")


def load_focus_songs():
    return json.loads(FOCUS_V2.read_text())["songs"]


def sha256_of(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def slice_and_load(wav_path, t_start_s, t_end_s):
    """Load a stem clip in [t_start_s, t_end_s] at native sr, mono. Same clamp
    semantics as c54 branch A's _common.slice_and_load (chosen section may
    exceed 30 s stem — clamp to intersection; fall back to full stem if <5 s)."""
    import soundfile as sf
    import numpy as np
    info = sf.info(str(wav_path))
    sr = info.samplerate
    stem_dur = info.frames / sr
    a = max(0.0, min(float(t_start_s), stem_dur))
    b = max(a, min(float(t_end_s), stem_dur))
    if b - a < 5.0:
        a, b = 0.0, stem_dur
    start = int(round(a * sr))
    end = int(round(b * sr))
    y, sr = sf.read(str(wav_path), start=start, stop=end, always_2d=False)
    if y.ndim == 2:
        y = y.mean(axis=1)
    return y.astype(np.float32), sr


def write_json_canonical(path, obj):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(obj, sort_keys=True, indent=2) + "\n")
