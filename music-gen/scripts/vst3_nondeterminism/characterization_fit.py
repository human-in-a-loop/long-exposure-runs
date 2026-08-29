#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-29T05:18:40Z
# cycle: 36
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-DAW-SPIKE-1/vst3-render-nondeterminism-characterization
# ---
"""c36 Branch C — mel_l1_db pairwise + aggregate summary per plugin.

Uses `scripts.texture.spectral_panel.mel_l1_db_multiscale` READ-ONLY
(returns per-scale dict + `mean`). Writes pairwise_mel_l1_db.tsv and
summary.json per plugin.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.vst3_nondeterminism import _shared as sh  # noqa: E402
from scripts.texture.spectral_panel import mel_l1_db_multiscale  # noqa: E402

assert sys.executable == "/usr/bin/python3", sys.executable

N_RUNS = 5


def _to_mono_float32(y):
    import numpy as np
    if y.ndim == 2:
        m = y.mean(axis=1)
    else:
        m = y
    return m.astype(np.float32)


def compute_for(plugin: str) -> dict:
    """Compute pairwise mel_l1_db, aggregate metrics; write per-plugin
    outputs; return the aggregate summary dict."""
    import numpy as np
    d = sh.REPO / "data" / "vst3_nondeterminism" / "per_plugin" / plugin
    audio = [sh.read_wav_float32(d / f"run{k}.wav") for k in range(1, N_RUNS + 1)]
    monos = [_to_mono_float32(a) for a in audio]

    mel_lines = ["i\tj\tmel_l1_db_mean\n"]
    mel_vals = []
    for (i, j) in sh.pair_indices(N_RUNS):
        res = mel_l1_db_multiscale(monos[i], monos[j], sh.SAMPLE_RATE)
        val = float(res["mean"])
        mel_vals.append(val)
        mel_lines.append(f"{i+1}\t{j+1}\t{val:.9f}\n")
    (d / "pairwise_mel_l1_db.tsv").write_text("".join(mel_lines))

    # Aggregate: read back rms + env_corr TSVs.
    rms_vals = []
    max_abs_vals = []
    for line in (d / "pairwise_rms.tsv").read_text().splitlines()[1:]:
        parts = line.split("\t")
        rms_vals.append(float(parts[2]))
        max_abs_vals.append(float(parts[3]))
    env_vals = []
    for line in (d / "pairwise_env_corr.tsv").read_text().splitlines()[1:]:
        parts = line.split("\t")
        env_vals.append(float(parts[2]))

    # Per-run SHAs
    shas = [(d / f"run{k}_wav_sha").read_text().strip() for k in range(1, N_RUNS + 1)]
    all_distinct = len(set(shas)) == N_RUNS
    all_equal = len(set(shas)) == 1

    summary = {
        "plugin": plugin,
        "n_runs": N_RUNS,
        "n_pairs": len(rms_vals),
        "run_shas": shas,
        "all_shas_distinct": all_distinct,
        "all_shas_equal": all_equal,
        "rms": {
            "max": max(rms_vals), "min": min(rms_vals),
            "median": float(np.median(rms_vals)), "mean": float(np.mean(rms_vals)),
            "values": rms_vals,
        },
        "max_abs_sample": {
            "max": max(max_abs_vals), "min": min(max_abs_vals),
            "median": float(np.median(max_abs_vals)),
            "values": max_abs_vals,
        },
        "env_corr": {
            "max": max(env_vals), "min": min(env_vals),
            "median": float(np.median(env_vals)), "mean": float(np.mean(env_vals)),
            "values": env_vals,
        },
        "mel_l1_db": {
            "max": max(mel_vals), "min": min(mel_vals),
            "median": float(np.median(mel_vals)), "mean": float(np.mean(mel_vals)),
            "values": mel_vals,
        },
    }
    (d / "summary.json").write_text(
        json.dumps(summary, sort_keys=True, indent=2) + "\n"
    )
    return summary


def main() -> int:
    for plugin in sh.PLUGINS:
        s = compute_for(plugin)
        print(f"{plugin}: max_rms={s['rms']['max']:.3e} "
              f"max_mel={s['mel_l1_db']['max']:.3f}dB "
              f"min_env_corr={s['env_corr']['min']:.4f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
