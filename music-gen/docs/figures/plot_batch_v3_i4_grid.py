#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-28T16:50:00Z
# cycle: 15
# run_id: run-2026-08-28T040704Z
# agent: worker (clone-1, fork 392503ab7d47)
# milestone: M-GEN-1/batch-v3-i4
# ---
"""8-song batch-v3-i4 grid: waveform strips + heuristics + panel numbers."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import wave


def _read_wav(path):
    """Minimal RIFF/WAVE reader supporting PCM (fmt=1) and IEEE float (fmt=3)."""
    with open(path, "rb") as f:
        data = f.read()
    assert data[:4] == b"RIFF" and data[8:12] == b"WAVE"
    i = 12
    fmt_tag = 1
    ch = 1
    sr = 44100
    bps = 16
    pcm = b""
    while i < len(data):
        cid = data[i:i+4]
        csz = int.from_bytes(data[i+4:i+8], "little")
        cbody = data[i+8:i+8+csz]
        if cid == b"fmt ":
            fmt_tag = int.from_bytes(cbody[0:2], "little")
            ch = int.from_bytes(cbody[2:4], "little")
            sr = int.from_bytes(cbody[4:8], "little")
            bps = int.from_bytes(cbody[14:16], "little")
        elif cid == b"data":
            pcm = cbody
        i += 8 + csz + (csz & 1)
    if fmt_tag == 1 and bps == 16:
        y = np.frombuffer(pcm, dtype=np.int16).astype(np.float32) / 32768.0
    elif fmt_tag == 1 and bps == 32:
        y = np.frombuffer(pcm, dtype=np.int32).astype(np.float32) / (2**31)
    elif fmt_tag == 3 and bps == 32:
        y = np.frombuffer(pcm, dtype=np.float32).copy()
    else:
        raise ValueError(f"unsupported WAV: fmt={fmt_tag} bps={bps}")
    if ch > 1:
        y = y.reshape(-1, ch)
    else:
        y = y.reshape(-1, 1)
    return y, sr

_REPO = Path(__file__).resolve().parent.parent.parent
BATCH = _REPO / "data" / "gen" / "batch_v3_i4"


def main():
    fig, axes = plt.subplots(8, 2, figsize=(14, 12), sharex="col")
    for salt in range(8):
        d = BATCH / f"song_{salt}"
        y_bare, sr = _read_wav(d / "bare_midi.wav")
        y_fx, _ = _read_wav(d / "effects_layered.wav")
        y_bare_m = y_bare.mean(axis=1)
        y_fx_m = y_fx.mean(axis=1)
        t = np.arange(len(y_bare_m)) / sr

        scoring = json.loads((d / "scoring.json").read_text())
        heur = scoring.get("heuristics", {})
        panel = scoring.get("texture_panel_bare_vs_effects", {})

        axes[salt, 0].plot(t, y_bare_m, lw=0.4, color="#4B7BE5")
        axes[salt, 0].set_ylabel(f"salt={salt}\nbare", fontsize=8)
        axes[salt, 0].set_ylim(-1.05, 1.05)
        axes[salt, 0].tick_params(labelsize=7)

        t_fx = np.arange(len(y_fx_m)) / sr
        axes[salt, 1].plot(t_fx, y_fx_m, lw=0.4, color="#E5734B")
        axes[salt, 1].set_ylabel("effects", fontsize=8)
        axes[salt, 1].set_ylim(-1.05, 1.05)
        axes[salt, 1].tick_params(labelsize=7)

        def _g(name):
            v = heur.get(name, {}).get("mess_scale")
            return "—" if v is None else f"{v:.2f}"

        def _p(name):
            v = panel.get(name)
            return "—" if v is None else (f"{float(v):.2f}" if not isinstance(v, str) else v)

        caption = (
            f"heur: mel={_g('melody_quality')} tim={_g('timbre_quality')} "
            f"form={_g('form_quality')} dyn={_g('dynamics_quality')}   "
            f"panel: mel_l1_db={_p('mel_l1_db')} rms_env={_p('rms_env_rmse')} "
            f"cent={_p('spectral_centroid_rmse_hz')}Hz"
        )
        axes[salt, 1].text(1.02, 0.5, caption, transform=axes[salt, 1].transAxes,
                           fontsize=7, va="center", ha="left")

    axes[-1, 0].set_xlabel("time (s)", fontsize=8)
    axes[-1, 1].set_xlabel("time (s)", fontsize=8)

    fig.suptitle(
        "batch-v3-i4: 8-song grid (salts 0..7) rendered via I4 stratified sampler. "
        "Left: bare-MIDI (fluidsynth SF2). Right: cycle-9 pinned DawDreamer chain. "
        "All 8 songs distinct: unique SHA on musicxml/midi/bare/effects.",
        fontsize=10, y=0.995)
    fig.tight_layout(rect=(0, 0, 0.85, 0.97))

    out = os.environ.get("FIGURE_OUT",
                          str(_REPO / "docs" / "figures" / "batch_v3_i4_grid.png"))
    fig.savefig(out, dpi=120)
    print(f"[plot_batch_v3_i4_grid] wrote {out}")


if __name__ == "__main__":
    main()
