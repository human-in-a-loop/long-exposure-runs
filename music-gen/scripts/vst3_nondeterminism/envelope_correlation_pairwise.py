#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-29T05:18:30Z
# cycle: 36
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-DAW-SPIKE-1/vst3-render-nondeterminism-characterization
# ---
"""c36 Branch C — compute per-plugin pairwise envelope correlation.

Pearson correlation on the mono-mixed RMS envelopes at hop=512
(librosa.feature.rms). C(5,2)=10 pairs per plugin. Writes
pairwise_env_corr.tsv into the plugin directory.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.vst3_nondeterminism import _shared as sh  # noqa: E402

assert sys.executable == "/usr/bin/python3", sys.executable

N_RUNS = 5
HOP = 512


def _rms_env(y):
    import librosa
    import numpy as np
    # mono mix-down
    if y.ndim == 2:
        m = librosa.to_mono(y.T)
    else:
        m = y
    env = librosa.feature.rms(y=m.astype(np.float32), hop_length=HOP)[0]
    return env


def compute_for(plugin: str) -> Path:
    import numpy as np
    d = sh.REPO / "data" / "vst3_nondeterminism" / "per_plugin" / plugin
    audio = [sh.read_wav_float32(d / f"run{k}.wav") for k in range(1, N_RUNS + 1)]
    envs = [_rms_env(a) for a in audio]
    lines = ["i\tj\tenv_corr\n"]
    for (i, j) in sh.pair_indices(N_RUNS):
        a, b = envs[i], envs[j]
        n = min(len(a), len(b))
        a, b = a[:n], b[:n]
        # Pearson; guard against zero-variance envelope by fallback.
        if float(np.std(a)) < 1e-12 or float(np.std(b)) < 1e-12:
            # If both identical -> 1.0; else 0.0.
            if np.allclose(a, b):
                r = 1.0
            else:
                r = 0.0
        else:
            r = float(np.corrcoef(a, b)[0, 1])
        lines.append(f"{i+1}\t{j+1}\t{r:.9f}\n")
    out = d / "pairwise_env_corr.tsv"
    out.write_text("".join(lines))
    return out


def main() -> int:
    for plugin in sh.PLUGINS:
        p = compute_for(plugin)
        print(f"{plugin}: wrote {p.relative_to(sh.REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
