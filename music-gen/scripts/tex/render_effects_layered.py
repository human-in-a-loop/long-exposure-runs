#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-28T10:35:00Z
# cycle: 9
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-TEX-1/stage-by-stage
# ---
"""Apply the pinned M-DAW-SPIKE-1 DawDreamer chain to a WAV.

The chain is the cycle-1 Ardour↔DawDreamer agreement-check chain:
    input → Surge XT Effects (Chorus, FX Type=0.28, Output Mix=0.35)
          → Surge XT Effects (Reverb, FX Type=0.02,
             Output Mix ramp 0.05→0.60 linear over the input duration)
          → track-gain envelope 0.25→1.4 linear (applied post-hoc)

The chain runs at the input WAV's sample-rate and stereo layout (this
clone's bare-MIDI stage renders at 44.1 kHz stereo per the M-SEP-1
ground-truth contract; the cycle-1 chain originally ran at 48 kHz, but
Surge XT is sample-rate agnostic and the exact same normalized parameter
values are used here so the sonic identity is preserved).

Determinism pins (must be applied BEFORE any dawdreamer import; the
runtime pin below is a defensive belt-and-braces guard for cases where
this module is imported directly rather than launched fresh):

    OMP_NUM_THREADS=1  MKL_NUM_THREADS=1  OPENBLAS_NUM_THREADS=1
    torch.set_num_threads(1)
    torch.manual_seed(0)
    numpy.random.seed(0)

If the VST3 is missing or the plugin fails to load, the caller is
expected to fall back to `apply_numpy_effects_fallback` — DO NOT
fabricate a graph.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

# Belt-and-braces determinism pins.
for _v in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

assert sys.executable == "/usr/bin/python3", sys.executable

import numpy as np
import soundfile as sf
import scipy.io.wavfile as scipy_wav

try:
    import torch
    torch.set_num_threads(1)
    torch.manual_seed(0)
except Exception:  # pragma: no cover
    pass
np.random.seed(0)

SURGE_VST3 = "/usr/lib/vst3/Surge XT Effects.vst3"


def _find_param(p, needle: str) -> int:
    for pd in p.get_parameters_description():
        if needle.lower() in pd["name"].lower():
            return int(pd["index"])
    raise KeyError(needle)


def apply_dawdreamer_chain(in_wav_path: Path, out_wav_path: Path) -> None:
    """Apply the pinned chain to in_wav; write stereo WAV at input SR."""
    import dawdreamer as daw  # imported after pins are in place

    audio, sr = sf.read(str(in_wav_path), always_2d=True)
    if audio.shape[1] == 1:
        audio = np.concatenate([audio, audio], axis=1)
    audio = audio.astype(np.float32)
    n = audio.shape[0]
    stereo_channels_first = audio.T.copy()  # (2, N)

    block = 512
    engine = daw.RenderEngine(sr, block)
    playback = engine.make_playback_processor("src", stereo_channels_first)
    fx_chorus = engine.make_plugin_processor("fx_chorus", SURGE_VST3)
    fx_reverb = engine.make_plugin_processor("fx_reverb", SURGE_VST3)

    fx_chorus.set_parameter(_find_param(fx_chorus, "FX Type"), 0.28)
    fx_chorus.set_parameter(_find_param(fx_chorus, "Output Mix"), 0.35)
    fx_reverb.set_parameter(_find_param(fx_reverb, "FX Type"), 0.02)
    fx_reverb.set_parameter(_find_param(fx_reverb, "Output Mix"), 0.05)

    auto_rev = np.linspace(0.05, 0.60, n, dtype=np.float32)
    fx_reverb.set_automation(_find_param(fx_reverb, "Output Mix"), auto_rev)

    graph = [
        (playback, []),
        (fx_chorus, [playback.get_name()]),
        (fx_reverb, [fx_chorus.get_name()]),
    ]
    engine.load_graph(graph)
    dur_s = n / float(sr)
    engine.render(dur_s)
    out = engine.get_audio()  # (2, N)

    env = np.linspace(0.25, 1.4, n, dtype=np.float32)
    out = out * env[np.newaxis, :]

    # Match the length in case the engine returned a slightly different N
    # (dawdreamer may pad; clip back to input length so downstream panels
    # compare the same duration).
    if out.shape[1] > n:
        out = out[:, :n]
    elif out.shape[1] < n:
        pad = np.zeros((2, n - out.shape[1]), dtype=np.float32)
        out = np.concatenate([out, pad], axis=1)

    scipy_wav.write(str(out_wav_path), sr, out.T.astype(np.float32))


def apply_numpy_effects_fallback(in_wav_path: Path, out_wav_path: Path) -> None:
    """Deterministic numpy-only chain used only if DawDreamer fails.

    Escape hatch documented in the research brief. Chain:
      - short IR-style comb-filter (500-tap sparse comb at 30ms delays)
        for a chorus-flavored effect
      - simple recirculating feedback delay for a reverb-flavored tail
        (Schroeder-inspired, single-comb single-allpass)
      - gain ramp 0.25→1.4 across the duration
    All coefficients are hard-coded here; every seed is set. Byte-
    deterministic across two runs.
    """
    audio, sr = sf.read(str(in_wav_path), always_2d=True)
    if audio.shape[1] == 1:
        audio = np.concatenate([audio, audio], axis=1)
    audio = audio.astype(np.float32)
    n = audio.shape[0]

    def _chorus(x: np.ndarray) -> np.ndarray:
        # LFO-modulated 20ms delay, depth 5ms, rate 1.5 Hz.
        base = int(round(0.020 * sr))
        depth = int(round(0.005 * sr))
        t = np.arange(n) / sr
        lfo = (0.5 * (1 + np.sin(2 * np.pi * 1.5 * t))).astype(np.float32)
        out = np.zeros_like(x)
        for i in range(n):
            d = base + int(depth * lfo[i])
            if i - d >= 0:
                out[i] = 0.65 * x[i] + 0.35 * x[i - d]
            else:
                out[i] = x[i]
        return out

    def _reverb(x: np.ndarray) -> np.ndarray:
        # Two-comb feedback delays 37ms and 41ms with g=0.6.
        d1 = int(round(0.037 * sr))
        d2 = int(round(0.041 * sr))
        g = 0.6
        y = x.copy()
        for i in range(d1, n):
            y[i] += g * y[i - d1]
        for i in range(d2, n):
            y[i] += g * y[i - d2]
        # Mix 0.05→0.60 automation across duration.
        mix = np.linspace(0.05, 0.60, n, dtype=np.float32)
        return (1 - mix[:, np.newaxis]) * x + mix[:, np.newaxis] * y

    # Apply per channel.
    out = np.stack([_reverb(_chorus(audio[:, ch])) for ch in range(2)], axis=1)
    env = np.linspace(0.25, 1.4, n, dtype=np.float32)
    out = out * env[:, np.newaxis]
    # Clip to prevent inf on downstream mel; DawDreamer clips too.
    out = np.clip(out, -4.0, 4.0)
    scipy_wav.write(str(out_wav_path), sr, out.astype(np.float32))


def apply_effects_layered(in_wav_path: Path, out_wav_path: Path) -> str:
    """Try DawDreamer chain; on failure fall back to numpy chain.

    Returns the rung used: "dawdreamer" or "numpy_fallback".
    """
    in_wav_path = Path(in_wav_path)
    out_wav_path = Path(out_wav_path)
    if os.path.isdir(SURGE_VST3):
        try:
            apply_dawdreamer_chain(in_wav_path, out_wav_path)
            return "dawdreamer"
        except Exception as exc:  # pragma: no cover
            print(f"[effects_layered] DawDreamer chain failed: {exc}; "
                  "falling back to numpy chain", file=sys.stderr)
    else:  # pragma: no cover
        print(f"[effects_layered] Surge XT VST3 missing at {SURGE_VST3}; "
              "using numpy chain", file=sys.stderr)
    apply_numpy_effects_fallback(in_wav_path, out_wav_path)
    return "numpy_fallback"


def main():  # pragma: no cover
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--in-wav", required=True)
    ap.add_argument("--out-wav", required=True)
    args = ap.parse_args()
    rung = apply_effects_layered(Path(args.in_wav), Path(args.out_wav))
    print(f"wrote {args.out_wav} (rung={rung})")


if __name__ == "__main__":
    main()
