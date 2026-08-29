#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-29T06:10:00Z
# cycle: 35
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-DAW-SPIKE-1/palette-schema-v2-hydration-render
# ---
"""Per-stem renderer with DawDreamer VST3 hydration for Surge XT + Dexed.

Contract: one invocation = one render into `<out_dir>/render.wav`.
Caller (run_all.py) invokes this via subprocess twice per stem into two
FRESH `tempfile.mkdtemp()` directories to prove byte-determinism × 2.
Subprocess isolation is required for DawDreamer determinism: consecutive
VST3 renders within the same process are NOT byte-identical (Surge XT
holds internal LFO/envelope state across engine instances). Fresh Python
process resolves this.

Instrument dispatch:
  * fluidsynth_gm — subprocess to `fluidsynth` (drums; command copied
    verbatim from scripts/palette_render/render_stem.py — that module
    is NOT imported at runtime).
  * surge_xt / dexed — DawDreamer 0.9.0 VST3 dispatched from *this*
    process. Hydration: iterate the c33 P1 anchor and call
    `plugin.set_parameter(int(key.split(':',1)[0]), float(value))`
    for every (key, value) in the anchor's iterated_params dict.
    This is the c33 WORKAROUND_FOUND path.
    FORBIDDEN: get_state, save_state, save_preset, set_state(bytes).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

# BLAS pins BEFORE any numeric import.
import os
for _v in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import numpy as np
import soundfile as sf
import scipy.io.wavfile as scipy_wav

assert sys.executable == "/usr/bin/python3", sys.executable

_REPO = Path(__file__).resolve().parents[2]
SAMPLE_RATE = 44100
DURATION_S = 30.0
SAMPLE_COUNT = int(SAMPLE_RATE * DURATION_S)  # 1_323_000
BLOCK_SIZE = 512

SF2_PATH = Path("/usr/share/sounds/sf2/FluidR3_GM.sf2")
SF2_EXPECTED_SHA = "74594e8f4250680adf590507a306655a299935343583256f3b722c48a1bc1cb0"
FLUIDSYNTH = "/usr/bin/fluidsynth"

VST3_PATHS = {
    "surge_xt": "/usr/lib/vst3/Surge XT.vst3",
    "dexed":    "/usr/lib/vst3/Dexed.vst3",
}

PER_STEM_MIDI = {
    "drums": _REPO / "data" / "transcribe" / "basic_pitch" / "synth_030s" / "drums.mid",
    "bass":  _REPO / "data" / "transcribe" / "basic_pitch" / "synth_030s" / "bass.mid",
    "other": _REPO / "data" / "transcribe" / "basic_pitch" / "synth_030s" / "other.mid",
}

ANCHOR_DIR = _REPO / "data" / "dawdreamer_state" / "per_plugin"
SILENT_PEAK_ABS = 1e-4


def _assert_sf2() -> None:
    if not SF2_PATH.is_file():
        raise RuntimeError(f"SF2 missing: {SF2_PATH}")
    h = hashlib.sha256(SF2_PATH.read_bytes()).hexdigest()
    if h != SF2_EXPECTED_SHA:
        raise RuntimeError(f"SF2 SHA mismatch: got {h}, expected {SF2_EXPECTED_SHA}")


def _canonicalize_wav_deterministic(y: np.ndarray, out_wav: Path) -> None:
    """scipy.io.wavfile writes byte-deterministic PCM (no BEXT/timestamp).
    Pad/trim to exactly SAMPLE_COUNT samples. Stereo float32."""
    if y.ndim == 1:
        y = np.stack([y, y], axis=1)
    if y.shape[1] == 1:
        y = np.concatenate([y, y], axis=1)
    if y.shape[0] > SAMPLE_COUNT:
        y = y[:SAMPLE_COUNT, :]
    elif y.shape[0] < SAMPLE_COUNT:
        pad = np.zeros((SAMPLE_COUNT - y.shape[0], y.shape[1]), dtype=y.dtype)
        y = np.concatenate([y, pad], axis=0)
    scipy_wav.write(str(out_wav), SAMPLE_RATE, y.astype(np.float32))


def render_fluidsynth_once(midi_path: Path, out_wav: Path) -> dict:
    """Fluidsynth CLI dispatch — one render.
    Command line copied verbatim from scripts/palette_render/render_stem.py.
    (That module is NOT imported.)
    """
    _assert_sf2()
    if not midi_path.is_file():
        raise RuntimeError(f"MIDI missing: {midi_path}")
    tmp = out_wav.with_suffix(".raw.wav")
    if tmp.exists():
        tmp.unlink()
    cmd = [
        FLUIDSYNTH, "-a", "null", "-T", "wav",
        "-F", str(tmp),
        "-r", str(SAMPLE_RATE),
        "-g", "1.0",
        "-i",
        str(SF2_PATH), str(midi_path),
    ]
    subprocess.run(cmd, check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    y, got_sr = sf.read(str(tmp), always_2d=True)
    if got_sr != SAMPLE_RATE:
        raise RuntimeError(f"fluidsynth sr={got_sr}, expected {SAMPLE_RATE}")
    _canonicalize_wav_deterministic(y, out_wav)
    tmp.unlink()
    peak_abs = float(np.max(np.abs(y))) if y.size else 0.0
    return {"path": "fluidsynth_gm", "peak_abs": peak_abs,
            "silent": peak_abs < SILENT_PEAK_ABS}


def _load_anchor(plugin_name: str) -> dict:
    p = ANCHOR_DIR / plugin_name / "p1_state_v2.json"
    return json.loads(p.read_text())


def render_dawdreamer_vst3_once(plugin_name: str, midi_path: Path,
                                 out_wav: Path) -> dict:
    """DawDreamer 0.9.0 VST3 render with c33 P1 hydration — one render.

    Hydration (c33 WORKAROUND_FOUND):
        for key, val in anchor.items():
            idx = int(key.split(":", 1)[0])
            plugin.set_parameter(idx, float(val))

    NEVER calls get_state/save_state/save_preset/set_state(bytes) — the
    c31 STILL_GAP anti-pattern surface.
    """
    if plugin_name not in VST3_PATHS:
        raise RuntimeError(f"unknown VST3 plugin: {plugin_name}")
    plugin_path = VST3_PATHS[plugin_name]
    if not Path(plugin_path).exists():
        raise RuntimeError(f"VST3 missing: {plugin_path}")
    if not midi_path.is_file():
        raise RuntimeError(f"MIDI missing: {midi_path}")

    import dawdreamer as daw  # noqa: WPS433 — lazy so AST-grep tests skip it

    engine = daw.RenderEngine(SAMPLE_RATE, BLOCK_SIZE)
    plugin = engine.make_plugin_processor("t", plugin_path)

    anchor = _load_anchor(plugin_name)
    n_params_set = 0
    n_params_skipped = 0
    for key, val in anchor.items():
        try:
            idx_str, _name = key.split(":", 1)
            idx = int(idx_str)
        except (ValueError, IndexError):
            n_params_skipped += 1
            continue
        try:
            plugin.set_parameter(idx, float(val))
            n_params_set += 1
        except Exception:
            n_params_skipped += 1

    plugin.load_midi(str(midi_path))
    engine.load_graph([(plugin, [])])
    engine.render(DURATION_S)
    audio = plugin.get_audio()

    a = np.asarray(audio, dtype=np.float32)
    if a.ndim == 1:
        y = np.stack([a, a], axis=1)
    elif a.shape[0] <= 2 and a.shape[1] > 8:
        y = a.T
        if y.shape[1] == 1:
            y = np.concatenate([y, y], axis=1)
    else:
        y = a
        if y.ndim == 2 and y.shape[1] == 1:
            y = np.concatenate([y, y], axis=1)

    peak_abs = float(np.max(np.abs(y))) if y.size else 0.0
    _canonicalize_wav_deterministic(y, out_wav)

    return {
        "path": f"dawdreamer_vst3:{plugin_name}",
        "plugin_name": plugin_name,
        "n_params_anchor": len(anchor),
        "n_params_set": n_params_set,
        "n_params_skipped": n_params_skipped,
        "peak_abs": peak_abs,
        "n_samples": int(y.shape[0]) if y.ndim == 2 else int(y.size),
        "silent": peak_abs < SILENT_PEAK_ABS,
    }


def render_once(stem: str, instrument: str, out_wav: Path) -> dict:
    """Single-render dispatcher. Writes ONE WAV to out_wav.

    Caller (run_all.py) invokes this via subprocess twice per stem
    into fresh tempdirs to prove byte-determinism.
    """
    if stem not in PER_STEM_MIDI:
        raise RuntimeError(f"unknown stem: {stem}")
    midi_path = PER_STEM_MIDI[stem]
    if instrument == "fluidsynth_gm":
        return render_fluidsynth_once(midi_path, out_wav)
    if instrument in ("surge_xt", "dexed"):
        return render_dawdreamer_vst3_once(instrument, midi_path, out_wav)
    raise RuntimeError(f"unsupported instrument for v2 hydration: {instrument}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stem", required=True, choices=["drums", "bass", "other"])
    ap.add_argument("--instrument", required=True,
                    choices=["fluidsynth_gm", "surge_xt", "dexed"])
    ap.add_argument("--out-wav", required=True,
                    help="Absolute path for the single render output WAV.")
    a = ap.parse_args()
    out_wav = Path(a.out_wav)
    out_wav.parent.mkdir(parents=True, exist_ok=True)
    result = render_once(a.stem, a.instrument, out_wav)
    sha = hashlib.sha256(out_wav.read_bytes()).hexdigest()
    result["wav_path"] = str(out_wav)
    result["sha256"] = sha
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
