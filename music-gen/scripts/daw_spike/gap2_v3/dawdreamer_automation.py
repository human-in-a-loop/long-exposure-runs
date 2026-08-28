#!/usr/bin/env python3
"""DawDreamer-native automation renderer for GAP-2 v3.

Loads a VST3 plugin, authors an audio-rate automation curve on a single
parameter via `PluginProcessor.set_automation(parameter_index, ndarray,
ppqn=0)` (DawDreamer 0.9.0 API), and renders deterministically at
44.1 kHz stereo through a RenderEngine graph:

  wav_source -> plugin -> [render_engine output]

The automation curve is a piecewise-linear interpolation of the caller's
3-point (t_sec, value) list, sampled at audio rate (sample rate =
render sr). Values are in the plugin's NORMALIZED parameter space
[0.0, 1.0].

Interpreter-guarded /usr/bin/python3. Env pins (OMP/MKL/OPENBLAS=1,
PYTHONHASHSEED=0) set BEFORE any torch/dawdreamer import. torch and
numpy seeds pinned to 0.

Does NOT import from scripts.tex.render_effects_layered (the cycle-9
pinned chain). Verified by tests/test_integration_cross_branch.py §26.
"""
from __future__ import annotations

import os
import sys

os.environ.setdefault('OMP_NUM_THREADS', '1')
os.environ.setdefault('MKL_NUM_THREADS', '1')
os.environ.setdefault('OPENBLAS_NUM_THREADS', '1')
os.environ.setdefault('PYTHONHASHSEED', '0')

assert sys.executable == '/usr/bin/python3', sys.executable

import pathlib
from typing import List, Tuple

import numpy as np
import soundfile as sf
import torch

torch.set_num_threads(1)
torch.manual_seed(0)
np.random.seed(0)

import dawdreamer as dd


def build_automation_curve(curve_points: List[Tuple[float, float]], duration_s: float, sr: int) -> np.ndarray:
    """Piecewise-linear interpolation of 3+ (t_sec, value) points at audio rate.

    Returns float32 array of length int(duration_s * sr). Values outside
    the [first_t, last_t] range hold at the boundary values (constant
    extrapolation).
    """
    n = int(round(duration_s * sr))
    t = np.arange(n, dtype=np.float64) / sr
    xs = np.asarray([p[0] for p in curve_points], dtype=np.float64)
    ys = np.asarray([p[1] for p in curve_points], dtype=np.float64)
    out = np.interp(t, xs, ys).astype(np.float32)
    return out


def render_automated(
    plugin_path: pathlib.Path,
    parameter_index: int,
    curve_points: List[Tuple[float, float]],
    input_wav: pathlib.Path,
    out_wav: pathlib.Path,
    sr: int = 44100,
    duration_s: float = 10.0,
    block_size: int = 512,
) -> dict:
    """Render `input_wav` through `plugin_path` with time-varying automation on
    parameter `parameter_index`. Writes stereo 44.1 kHz WAV to `out_wav`.

    Returns a diagnostic dict: {plugin_path, parameter_index, parameter_name,
    curve_points, duration_s, sr, block_size, automation_len, peak, rms}.
    """
    engine = dd.RenderEngine(sr, block_size)
    plugin = engine.make_plugin_processor('fx', str(plugin_path))
    param_name = plugin.get_parameter_name(parameter_index)
    # Author audio-rate automation for the wet-mix parameter.
    curve = build_automation_curve(curve_points, duration_s, sr)
    ok = plugin.set_automation(parameter_index, curve, ppqn=0)
    if not ok:
        raise RuntimeError(f'set_automation(parameter_index={parameter_index}) returned False')

    # Playback processor: reads input WAV, feeds plugin.
    playback = engine.make_playback_processor('src', _load_wav_as_dawdreamer(input_wav, sr))
    graph = [
        (playback, []),
        (plugin, ['src']),
    ]
    engine.load_graph(graph)
    engine.render(duration_s)
    out = engine.get_audio()  # shape (channels, samples)
    if out.ndim == 1:
        out = np.stack([out, out], axis=0)
    out_stereo = out[:2].T.astype(np.float32)
    out_wav.parent.mkdir(parents=True, exist_ok=True)
    sf.write(str(out_wav), out_stereo, sr, subtype='PCM_16')
    peak = float(np.max(np.abs(out_stereo)))
    rms = float(np.sqrt(np.mean(out_stereo.astype(np.float64) ** 2)))
    return {
        'plugin_path': str(plugin_path),
        'parameter_index': parameter_index,
        'parameter_name': param_name,
        'curve_points': curve_points,
        'duration_s': duration_s,
        'sr': sr,
        'block_size': block_size,
        'automation_len': int(len(curve)),
        'peak': peak,
        'rms': rms,
    }


def render_fixed(
    plugin_path: pathlib.Path,
    parameter_index: int,
    fixed_value: float,
    input_wav: pathlib.Path,
    out_wav: pathlib.Path,
    sr: int = 44100,
    duration_s: float = 5.0,
    block_size: int = 512,
) -> dict:
    """Render at a single fixed parameter value; used for reference construction."""
    engine = dd.RenderEngine(sr, block_size)
    plugin = engine.make_plugin_processor('fx', str(plugin_path))
    plugin.set_parameter(parameter_index, float(fixed_value))
    playback = engine.make_playback_processor('src', _load_wav_as_dawdreamer(input_wav, sr, duration_samples=int(duration_s * sr)))
    graph = [
        (playback, []),
        (plugin, ['src']),
    ]
    engine.load_graph(graph)
    engine.render(duration_s)
    out = engine.get_audio()
    if out.ndim == 1:
        out = np.stack([out, out], axis=0)
    out_stereo = out[:2].T.astype(np.float32)
    out_wav.parent.mkdir(parents=True, exist_ok=True)
    sf.write(str(out_wav), out_stereo, sr, subtype='PCM_16')
    return {
        'plugin_path': str(plugin_path),
        'parameter_index': parameter_index,
        'fixed_value': fixed_value,
        'duration_s': duration_s,
        'sr': sr,
        'peak': float(np.max(np.abs(out_stereo))),
        'rms': float(np.sqrt(np.mean(out_stereo.astype(np.float64) ** 2))),
    }


def _load_wav_as_dawdreamer(path: pathlib.Path, sr: int, duration_samples: int | None = None) -> np.ndarray:
    """Read WAV as (channels, samples) float32 array for DawDreamer playback."""
    x, x_sr = sf.read(str(path), always_2d=True, dtype='float32')
    assert x_sr == sr, f'input sr mismatch: {x_sr} != {sr}'
    if duration_samples is not None:
        if x.shape[0] < duration_samples:
            pad = np.zeros((duration_samples - x.shape[0], x.shape[1]), dtype=np.float32)
            x = np.concatenate([x, pad], axis=0)
        else:
            x = x[:duration_samples]
    # DawDreamer expects (channels, samples)
    return np.ascontiguousarray(x.T)
