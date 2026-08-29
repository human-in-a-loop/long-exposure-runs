#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-29T05:18:20Z
# cycle: 36
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-DAW-SPIKE-1/vst3-render-nondeterminism-characterization
# ---
"""c36 Branch C — compute per-plugin pairwise RMS diff distribution.

For each plugin's 5 runs, computes all C(5,2)=10 pairs of
sqrt(mean((a_i - a_j)**2)) over the full 8s × stereo × 44100 Hz
canonicalized WAV samples. Writes pairwise_rms.tsv into the plugin
directory. Also computes per-pair max_abs_sample.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.vst3_nondeterminism import _shared as sh  # noqa: E402

assert sys.executable == "/usr/bin/python3", sys.executable

N_RUNS = 5


def compute_for(plugin: str) -> Path:
    import numpy as np
    d = sh.REPO / "data" / "vst3_nondeterminism" / "per_plugin" / plugin
    audio = [sh.read_wav_float32(d / f"run{k}.wav") for k in range(1, N_RUNS + 1)]
    lines = ["i\tj\trms_diff\tmax_abs_sample\n"]
    for (i, j) in sh.pair_indices(N_RUNS):
        a, b = audio[i], audio[j]
        n = min(a.shape[0], b.shape[0])
        diff = a[:n] - b[:n]
        rms = float(np.sqrt(np.mean(diff.astype(np.float64) ** 2)))
        mx = float(np.max(np.abs(diff))) if diff.size else 0.0
        lines.append(f"{i+1}\t{j+1}\t{rms:.9e}\t{mx:.9e}\n")
    out = d / "pairwise_rms.tsv"
    out.write_text("".join(lines))
    return out


def main() -> int:
    for plugin in sh.PLUGINS:
        p = compute_for(plugin)
        print(f"{plugin}: wrote {p.relative_to(sh.REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
