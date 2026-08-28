"""
Drive basic-pitch 0.4.0 in the quarantined venv via subprocess.

For every (mix, stem) in {synth_030s, synth_060s, synth_090s} x
{drums, bass, other}, run the venv's _bp_call.py which reads the WAV
(basic-pitch handles stereo->mono internal resampling) and writes:

  data/transcribe/basic_pitch/<mix>/<stem>.mid
  data/transcribe/basic_pitch/<mix>/<stem>.jsonl

Interpreter (this file): /usr/bin/python3.
Interpreter (subprocess target): workspace/basic_pitch_venv/bin/python3.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

assert sys.executable == "/usr/bin/python3", f"interpreter guard: {sys.executable}"

ROOT = Path("/home/user/long-exposure-runs/music-gen")
VENV_PY = ROOT / "workspace/basic_pitch_venv/bin/python3"
BP_CALL = ROOT / "scripts/transcribe/_bp_call.py"

GT_ROOT = ROOT / "data/separation/synth_mix/gt"
OUT_ROOT = ROOT / "data/transcribe/basic_pitch"

MIXES = ["synth_030s", "synth_060s", "synth_090s"]
STEMS = ["drums", "bass", "other"]  # vocals is silent -> skipped


def main() -> None:
    assert VENV_PY.is_file(), f"venv python not found: {VENV_PY}"
    for mix in MIXES:
        for stem in STEMS:
            wav = GT_ROOT / mix / f"{stem}.wav"
            assert wav.is_file(), f"missing input: {wav}"
            out_midi = OUT_ROOT / mix / f"{stem}.mid"
            out_jsonl = OUT_ROOT / mix / f"{stem}.jsonl"
            print(f"[bp] {mix}/{stem}", flush=True)
            subprocess.run(
                [str(VENV_PY), str(BP_CALL), str(wav), str(out_midi), str(out_jsonl)],
                check=True,
            )
    print("basic-pitch baseline complete.")


if __name__ == "__main__":
    main()
