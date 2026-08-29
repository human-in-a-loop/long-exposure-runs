#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-29T05:17:00Z
# cycle: 36
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-DAW-SPIKE-1/vst3-render-nondeterminism-characterization
# ---
"""Shared helpers for c36 Branch C VST3 nondeterminism characterization.

Zero PRNG. No c9/c13/c15/c22/c26-c30 imports. c33/c34/c35/c31 anchors
are READ-ONLY. The c33 P1 iterate hydration loop is inline-copied
byte-verbatim from scripts/palette_v2_render/render_stem_v2.py
(the c35 Branch A activation that surfaced the finding this branch
characterizes) — that module is NOT imported at runtime.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

# BLAS pins BEFORE any numeric import.
for _v in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

# Interpreter guard.
assert sys.executable == "/usr/bin/python3", (
    f"vst3_nondeterminism requires /usr/bin/python3; got {sys.executable}"
)

REPO = Path(__file__).resolve().parents[2]

# c31 fixed 8s ascending-diatonic MIDI parameters (read via helper below).
SAMPLE_RATE = 44100
DURATION_S = 8.0
SAMPLE_COUNT = int(SAMPLE_RATE * DURATION_S)  # 352800
CHANNELS = 2
BLOCK_SIZE = 512

VST3_PATHS: Dict[str, str] = {
    "surge_xt": "/usr/lib/vst3/Surge XT.vst3",
    "dexed":    "/usr/lib/vst3/Dexed.vst3",
}
PLUGINS: Tuple[str, ...] = ("surge_xt", "dexed")

ANCHOR_DIR = REPO / "data" / "dawdreamer_state" / "per_plugin"


def sha256_of_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha256_of_path(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def canonical_json_bytes(obj: Any) -> bytes:
    return (json.dumps(obj, sort_keys=True, indent=2, separators=(",", ": ")) + "\n").encode()


def load_p1_anchor(plugin_name: str) -> Dict[str, float]:
    """Load the c33 P1 iterated-parameters anchor for a plugin.

    This is a READ-ONLY read of the c33 anchor file. Never mutates the
    file. The keys look like '00042:PolyLimit' and values are floats.
    """
    p = ANCHOR_DIR / plugin_name / "p1_state_v2.json"
    return json.loads(p.read_text())


def get_test_midi_path() -> Path:
    """Write (idempotent) the c31 fixed 8s ascending-diatonic MIDI to
    `data/vst3_nondeterminism/test_input.mid` and return the path.

    Delegates the actual byte-construction to
    `scripts.palette_probe._shared.write_test_midi` — which is a
    READ-ONLY import (we do not mutate that module).
    """
    sys.path.insert(0, str(REPO))
    from scripts.palette_probe import _shared as pp_sh  # noqa: E402
    out = REPO / "data" / "vst3_nondeterminism" / "test_input.mid"
    if not out.exists():
        pp_sh.write_test_midi(out)
    return out


def read_wav_float32(wav_path: Path):
    """Read a WAV file as float32 array shape (n_samples, 2)."""
    import numpy as np
    import scipy.io.wavfile as scipy_wav
    sr, y = scipy_wav.read(str(wav_path))
    if sr != SAMPLE_RATE:
        raise RuntimeError(f"sr={sr}, expected {SAMPLE_RATE}")
    y = y.astype(np.float32)
    if y.ndim == 1:
        y = np.stack([y, y], axis=1)
    return y


def canonicalize_wav_deterministic(y, out_wav: Path) -> None:
    """Byte-deterministic WAV write: scipy.io.wavfile, no BEXT/timestamps.
    Trim/pad to SAMPLE_COUNT, stereo float32.
    """
    import numpy as np
    import scipy.io.wavfile as scipy_wav
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


def render_vst3_once_p1(plugin_name: str, out_wav: Path) -> Dict[str, Any]:
    """Render one VST3 rendering into `out_wav` under c33 P1 hydration.

    Hydration loop is inline byte-verbatim from c35's
    `render_stem_v2.py:render_dawdreamer_vst3_once`. Does not touch
    the c31 STILL_GAP + c35 A state-extraction anti-pattern surface;
    see the test suite's forbidden-call list.

    Uses `engine.get_audio()` for output (c31 pattern). Returns a
    small diagnostic dict.
    """
    import numpy as np  # noqa: F401  (transitively required)
    import dawdreamer as daw

    if plugin_name not in VST3_PATHS:
        raise RuntimeError(f"unknown plugin: {plugin_name}")
    plugin_path = VST3_PATHS[plugin_name]
    if not Path(plugin_path).exists():
        raise RuntimeError(f"VST3 missing: {plugin_path}")

    midi_path = get_test_midi_path()

    engine = daw.RenderEngine(SAMPLE_RATE, BLOCK_SIZE)
    plugin = engine.make_plugin_processor("t", plugin_path)

    # c33 P1 iterate hydration — inline copy of c35 render_stem_v2.py.
    anchor = load_p1_anchor(plugin_name)
    n_set = 0
    n_skip = 0
    for key, val in anchor.items():
        try:
            idx_str, _name = key.split(":", 1)
            idx = int(idx_str)
        except (ValueError, IndexError):
            n_skip += 1
            continue
        try:
            plugin.set_parameter(idx, float(val))
            n_set += 1
        except Exception:
            n_skip += 1

    plugin.load_midi(str(midi_path))
    engine.load_graph([(plugin, [])])
    engine.render(DURATION_S)
    audio = plugin.get_audio()

    a = np.asarray(audio, dtype=np.float32)
    if a.ndim == 1:
        y = np.stack([a, a], axis=1)
    elif a.shape[0] <= 2 and a.shape[1] > 8:
        # (channels, samples) → (samples, channels)
        y = a.T
        if y.shape[1] == 1:
            y = np.concatenate([y, y], axis=1)
    else:
        y = a
        if y.ndim == 2 and y.shape[1] == 1:
            y = np.concatenate([y, y], axis=1)

    peak_abs = float(np.max(np.abs(y))) if y.size else 0.0
    canonicalize_wav_deterministic(y, out_wav)

    return {
        "plugin": plugin_name,
        "n_params_anchor": len(anchor),
        "n_params_set": n_set,
        "n_params_skipped": n_skip,
        "peak_abs": peak_abs,
    }


def pair_indices(n: int) -> List[Tuple[int, int]]:
    """Return all C(n,2) pairs (i, j) with i < j."""
    out = []
    for i in range(n):
        for j in range(i + 1, n):
            out.append((i, j))
    return out
