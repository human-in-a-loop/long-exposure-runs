#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-29T05:18:10Z
# cycle: 36
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-DAW-SPIKE-1/vst3-render-nondeterminism-characterization
# ---
"""c36 Branch C probe — Dexed VST3, N=5 renders per-run isolated temp dirs.

Same contract as probe_surge_xt.py; the plugin key is the only change.
"""
from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.vst3_nondeterminism import _shared as sh  # noqa: E402

assert sys.executable == "/usr/bin/python3", sys.executable

PLUGIN = "dexed"
N_RUNS = 5


def main() -> int:
    out_dir = sh.REPO / "data" / "vst3_nondeterminism" / "per_plugin" / PLUGIN
    out_dir.mkdir(parents=True, exist_ok=True)
    for k in range(1, N_RUNS + 1):
        wav = out_dir / f"run{k}.wav"
        with tempfile.TemporaryDirectory(prefix=f"vst3nd_{PLUGIN}_{k}_") as td:
            _prev_cwd = os.getcwd()
            os.chdir(td)
            try:
                info = sh.render_vst3_once_p1(PLUGIN, wav)
            finally:
                os.chdir(_prev_cwd)
        sha = sh.sha256_of_path(wav)
        (out_dir / f"run{k}_wav_sha").write_text(sha + "\n")
        print(f"{PLUGIN} run{k}: peak={info['peak_abs']:.4f} "
              f"set={info['n_params_set']}/{info['n_params_anchor']} sha={sha[:12]}...")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
