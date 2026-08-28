#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-28T10:50:00Z
# cycle: 9
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-TEX-1/stage-by-stage
# ---
"""Orchestrator for M-TEX-1/stage-by-stage.

Produces three ordered audio stages for one chosen seed:

    original         — the seed's on-disk audio (fallback per brief)
    bare_midi        — fluidsynth-rendered merged-score MIDI
    effects_layered  — DawDreamer-chained bare_midi (Surge XT chorus +
                       reverb + gain ramp; numpy fallback if VST fails)

Measures the M-TEX-1/panel 8-key texture panel across all three ordered
pairs → 24 numbers total, per-family, NO aggregate.

Seed fallback ladder (per brief):
    (a) seed_mid_50s  — REJECTED: on-disk WAV is a 220 Hz sine test tone,
                        not genuinely-recorded audio.
    (b) seed_long_87s — REJECTED: same class of synthetic test-tone
                        seed (peak/RMS ratio characteristic of pure
                        sinusoid content).
    (c) synth_030s    — CHOSEN. Original == fluidsynth-rendered mix from
                        M-SEP-1/ground-truth; caveat carried into the
                        report so the stronger "recorded-original gap"
                        claim is not made.

The chosen path assembles:
    original   = data/separation/synth_mix/gt/synth_030s/mix.wav
    bare_midi  = fluidsynth(FluidR3_GM.sf2, data/score/merged_synth030s.mid)
    effects    = dawdreamer(bare_midi)  or  numpy_fallback(bare_midi)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

for _v in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
os.environ.setdefault("TF_DETERMINISTIC_OPS", "1")
os.environ.setdefault("PYTHONHASHSEED", "0")

assert sys.executable == "/usr/bin/python3", sys.executable

WS = Path(__file__).resolve().parents[2]
if str(WS) not in sys.path:
    sys.path.insert(0, str(WS))

from scripts.tex.render_bare_midi import render_bare_midi
from scripts.tex.render_effects_layered import apply_effects_layered
from scripts.tex.measure_across_stages import measure_pairs, write_tsv


SF2_PATH = Path("/usr/share/sounds/sf2/FluidR3_GM.sf2")
SEED_ID_DEFAULT = "synth_030s"
DURATION_S_DEFAULT = 30.0


def _sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _rel(path: Path) -> str:
    """Workspace-relative path if under WS, else the raw absolute path."""
    p = Path(path).resolve()
    try:
        return str(p.relative_to(WS))
    except ValueError:
        return str(p)


def _copy_wav_deterministic(src: Path, dst: Path) -> None:
    """Copy the seed's mix WAV into the renders dir, rewriting it via
    scipy.io.wavfile so the file-level SHA is stable across environments
    (some source WAVs carry libsndfile timestamp chunks).
    """
    import numpy as np
    import soundfile as sf
    import scipy.io.wavfile as scipy_wav
    y, sr = sf.read(str(src), always_2d=True)
    if y.shape[1] == 1:
        y = np.concatenate([y, y], axis=1)
    scipy_wav.write(str(dst), sr, y.astype(np.float32))


def run(seed_id: str, out_dir: Path, tsv_out: Path,
        duration_s: float = DURATION_S_DEFAULT) -> dict:
    stages = {
        "original": out_dir / "original.wav",
        "bare_midi": out_dir / "bare_midi.wav",
        "effects_layered": out_dir / "effects_layered.wav",
    }
    out_dir.mkdir(parents=True, exist_ok=True)

    # stage 0: original (per fallback ladder)
    if seed_id == "synth_030s":
        src = WS / "data" / "separation" / "synth_mix" / "gt" / "synth_030s" / "mix.wav"
        merged_midi = WS / "data" / "score" / "merged_synth030s.mid"
        caveat_original_is_synth = True
    else:
        raise NotImplementedError(
            f"seed_id={seed_id!r} not implemented on this clone; the "
            "fallback ladder collapses to synth_030s here.")

    _copy_wav_deterministic(src, stages["original"])

    # stage 1: bare_midi (fluidsynth on merged MIDI)
    render_bare_midi(
        midi_path=merged_midi,
        out_wav_path=stages["bare_midi"],
        sf2_path=SF2_PATH,
        sr=44100,
        duration_s=duration_s,
    )

    # stage 2: effects_layered (dawdreamer chain on bare_midi)
    rung = apply_effects_layered(stages["bare_midi"], stages["effects_layered"])

    # Measure the 8-key panel across all three ordered pairs.
    rows = measure_pairs(stages, sr=44100)
    write_tsv(rows, tsv_out)

    manifest = {
        "seed_id": seed_id,
        "original_is_synth_caveat": caveat_original_is_synth,
        "sf2_path": str(SF2_PATH),
        "sf2_sha256": _sha256_of(SF2_PATH),
        "merged_midi_path": _rel(merged_midi),
        "merged_midi_sha256": _sha256_of(merged_midi),
        "effects_rung": rung,
        "sr_hz": 44100,
        "duration_s": duration_s,
        "stage_sha256": {name: _sha256_of(p) for name, p in stages.items()},
        "tsv_path": _rel(tsv_out),
        "tsv_sha256": _sha256_of(tsv_out),
    }
    return manifest


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed-id", default=SEED_ID_DEFAULT)
    ap.add_argument("--out-dir", default=str(WS / "data" / "tex" / "renders" / SEED_ID_DEFAULT))
    ap.add_argument("--tsv-out", default=str(WS / "data" / "tex" / f"stage_by_stage_{SEED_ID_DEFAULT}.tsv"))
    ap.add_argument("--duration-s", type=float, default=DURATION_S_DEFAULT)
    args = ap.parse_args()

    out_dir = Path(args.out_dir)
    tsv_out = Path(args.tsv_out)
    manifest = run(args.seed_id, out_dir, tsv_out, args.duration_s)

    manifest_path = out_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
