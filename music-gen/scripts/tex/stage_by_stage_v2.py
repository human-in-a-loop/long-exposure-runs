#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-28T11:25:00Z
# cycle: 13
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-TEX-1/stage-by-stage
# ---
"""Cycle-13 orchestrator: extend M-TEX-1/stage-by-stage to breadth seeds.

Cycle-9 stage_by_stage.py (validated/high) measured 1 seed (synth_030s).
This v2 orchestrator extends the same measurement over the additional
breadth seeds frozen from cycle-10 M-INGEST-1/breadth-second-seeds:

    seed_mid_50s  — 50 s 44.1 kHz stereo (breadth-pipeline output;
                    on-disk source is a decaying-triad sine test tone)
    synth_060s    — 60 s 44.1 kHz stereo M-SEP-1 fluidsynth mix
                    (drums + bass + piano)

For each seed, three ordered pairs of the (original, bare_midi,
effects_layered) triple are measured with the M-TEX-1/panel 8-key
texture panel (24 numbers per seed).

Cycle-9 pinned DawDreamer chain (scripts/tex/render_effects_layered.py)
is imported and applied verbatim — do NOT modify; that chain is a
cross-branch invariant used by M-GEN-1 as well.

Input identity:
    original  = data/breadth/<seed>/original.wav   (frozen cycle-10)
    bare_midi = data/breadth/<seed>/bare_midi.wav  (frozen cycle-10)
    effects_layered = cycle-9-chain(bare_midi)     (produced here)

The mono→stereo + 22050→44100 shim discussed in the research brief is
NOT required because the M-INGEST-1/breadth-second-seeds cycle-10
pipeline already normalized both seeds to 44.1 kHz stereo. This is
documented in docs/tex_stage_by_stage_widening_report.md §3.
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

from scripts.tex.render_effects_layered import apply_effects_layered
from scripts.tex.measure_across_stages import measure_pairs, write_tsv

BREADTH_SEEDS = ("seed_mid_50s", "synth_060s")


def _sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _rel(path: Path) -> str:
    p = Path(path).resolve()
    try:
        return str(p.relative_to(WS))
    except ValueError:
        return str(p)


def _copy_wav_deterministic(src: Path, dst: Path) -> None:
    """Rewrite via scipy.io.wavfile so file-level SHA is stable."""
    import numpy as np
    import soundfile as sf
    import scipy.io.wavfile as scipy_wav
    y, sr = sf.read(str(src), always_2d=True)
    if y.shape[1] == 1:
        y = np.concatenate([y, y], axis=1)
    scipy_wav.write(str(dst), sr, y.astype(np.float32))


def measure_seed(seed_id: str, out_dir: Path, tsv_out: Path) -> dict:
    """Measure the panel across 3 ordered pairs for one breadth seed."""
    breadth_dir = WS / "data" / "breadth" / seed_id
    src_original = breadth_dir / "original.wav"
    src_bare = breadth_dir / "bare_midi.wav"
    if not src_original.exists():
        raise FileNotFoundError(f"missing frozen input: {src_original}")
    if not src_bare.exists():
        raise FileNotFoundError(f"missing frozen input: {src_bare}")

    out_dir.mkdir(parents=True, exist_ok=True)
    stages = {
        "original": out_dir / "original.wav",
        "bare_midi": out_dir / "bare_midi.wav",
        "effects_layered": out_dir / "effects_layered.wav",
    }

    # Copy the two frozen inputs (rewritten via scipy for SHA stability).
    _copy_wav_deterministic(src_original, stages["original"])
    _copy_wav_deterministic(src_bare, stages["bare_midi"])

    # Apply cycle-9 chain verbatim to bare_midi → effects_layered.
    rung = apply_effects_layered(stages["bare_midi"], stages["effects_layered"])

    # Measure panel across 3 ordered pairs.
    rows = measure_pairs(stages, sr=44100)
    write_tsv(rows, tsv_out)

    manifest = {
        "seed_id": seed_id,
        "src_original": _rel(src_original),
        "src_original_sha256": _sha256_of(src_original),
        "src_bare_midi": _rel(src_bare),
        "src_bare_midi_sha256": _sha256_of(src_bare),
        "effects_rung": rung,
        "sr_hz": 44100,
        "stage_sha256": {name: _sha256_of(p) for name, p in stages.items()},
        "tsv_path": _rel(tsv_out),
        "tsv_sha256": _sha256_of(tsv_out),
    }
    return manifest


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed-id", required=True, choices=BREADTH_SEEDS)
    ap.add_argument("--out-dir", default=None)
    ap.add_argument("--tsv-out", default=None)
    args = ap.parse_args()

    seed_id = args.seed_id
    out_dir = Path(args.out_dir) if args.out_dir else (WS / "data" / "tex" / "renders" / seed_id)
    tsv_out = Path(args.tsv_out) if args.tsv_out else (WS / "data" / "tex" / f"stage_by_stage_{seed_id}.tsv")

    manifest = measure_seed(seed_id, out_dir, tsv_out)
    manifest_path = out_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
