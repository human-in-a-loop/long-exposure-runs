#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-29T02:25:00Z
# cycle: 31
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-DAW-SPIKE-1/palette-instrument-determinism
# ---
"""Cycle-31 probe: sfizz SFZ-sampler determinism.

sfizz is not shipped as a VST3 or LV2 plugin in this workspace, so the
DawDreamer VST3 pathway is not available. The fetchability ladder
(§3 of the report) is honest about this: we use the `sfizz_render`
CLI as the loader_pathway. This preserves the "sfizz as a palette
instrument" concept and probes its determinism under the exact same
protocol as Surge XT / Dexed (fixed MIDI, 8s @ 44.1 kHz stereo).

The reference SFZ is `data/texture/test.sfz` (single-region sawtooth
sampler pointing at `test_saw.wav`). No PRNG. /usr/bin/python3
guarded.
"""
from __future__ import annotations

import argparse
import hashlib
import subprocess
import sys
import wave
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.palette_probe import _shared as sh  # noqa: E402

assert sys.executable == "/usr/bin/python3", sys.executable

WORKSPACE = Path(__file__).resolve().parents[2]
SFZ_PATH = WORKSPACE / "data" / "texture" / "test.sfz"
SFIZZ_RENDER = "/usr/bin/sfizz_render"
PLUGIN_NAME = "sfizz"
LOADER_PATHWAY = "sfizz_render_cli"


def _sfz_bundle_sha() -> str:
    """SHA of the SFZ file + its referenced sample(s)."""
    if not SFZ_PATH.exists():
        return "SFZ_MISSING"
    h = hashlib.sha256()
    h.update(SFZ_PATH.read_bytes())
    # Referenced sample: parse "sample=..." tokens.
    text = SFZ_PATH.read_text()
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("sample="):
            samp = s.split("=", 1)[1].strip()
            samp_path = SFZ_PATH.parent / samp
            if samp_path.exists():
                h.update(b"\n---SAMPLE---\n")
                h.update(samp_path.read_bytes())
    return h.hexdigest()


def _canonicalize_wav(src: Path, dst: Path) -> None:
    """Read src via `wave`, re-write dst so header bytes are canonical.

    sfizz_render's WAV writer may include metadata chunks or vary the
    header format across builds. Round-tripping through the stdlib
    `wave` module ensures a byte-deterministic 44-byte-header PCM WAV
    with exactly SAMPLE_COUNT frames.
    """
    import soundfile as sf
    import numpy as np
    data, sr = sf.read(str(src), dtype="int16", always_2d=True)
    if sr != sh.SAMPLE_RATE:
        raise RuntimeError(f"sfizz_render produced sr={sr}; expected {sh.SAMPLE_RATE}")
    if data.shape[1] == 1:
        data = np.repeat(data, 2, axis=1)
    if data.shape[0] > sh.SAMPLE_COUNT:
        data = data[: sh.SAMPLE_COUNT, :]
    elif data.shape[0] < sh.SAMPLE_COUNT:
        pad = np.zeros((sh.SAMPLE_COUNT - data.shape[0], data.shape[1]), dtype=np.int16)
        data = np.concatenate([data, pad], axis=0)
    with wave.open(str(dst), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(sh.SAMPLE_RATE)
        w.writeframes(data.tobytes(order="C"))


def probe(out_dir: Path, block_size: int = sh.DEFAULT_BLOCK_SIZE) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    midi_path = sh.write_test_midi(out_dir / "input.mid")
    raw_wav = out_dir / "_sfizz_raw.wav"
    render_wav = out_dir / "render.wav"

    cmd = [
        SFIZZ_RENDER,
        "--sfz", str(SFZ_PATH),
        "--midi", str(midi_path),
        "--wav", str(raw_wav),
        "-b", str(block_size),
        "-s", str(sh.SAMPLE_RATE),
        "-q", "1",  # pinned quality
        "-p", "64",  # pinned polyphony
    ]
    subprocess.run(cmd, check=True, capture_output=True, text=True)
    _canonicalize_wav(raw_wav, render_wav)
    # Remove the raw intermediate to keep the out-dir contents stable.
    try:
        raw_wav.unlink()
    except FileNotFoundError:
        pass

    # sfizz_render doesn't expose parameters the way a VST does; the
    # "parameter_dict" records the CLI-invocation-visible pinned state.
    parameter_dict = {
        "cli_block_size": float(block_size),
        "cli_polyphony": 64.0,
        "cli_quality": 1.0,
        "cli_sample_rate": float(sh.SAMPLE_RATE),
    }

    ext_sha = _sfz_bundle_sha()  # SHA of sfz + samples; not the "external state"
    # sfizz_render binary version — extract from --help output if we can
    plugin_version = _sfizz_version()

    state = {
        "block_size": block_size,
        "external_state_sha256": ext_sha,  # SFZ+sample bundle hash
        "loader_pathway": LOADER_PATHWAY,
        "midi_input_sha256": sh.sha256_of_path(midi_path),
        "parameter_dict": parameter_dict,
        "plugin_binary_sha256": _binary_sha(),
        "plugin_name": PLUGIN_NAME,
        "plugin_version": plugin_version,
        "preset_name": SFZ_PATH.name,
        "sample_count": sh.SAMPLE_COUNT,
        "sample_rate": sh.SAMPLE_RATE,
        "stereo": True,
    }
    sh.write_pinned_state(out_dir, state)


def _sfizz_version() -> str | None:
    try:
        r = subprocess.run([SFIZZ_RENDER, "--version"], capture_output=True, text=True, timeout=5)
        s = (r.stdout or r.stderr).strip().splitlines()
        return s[0] if s else None
    except Exception:
        return None


def _binary_sha() -> str:
    p = Path(SFIZZ_RENDER)
    if not p.exists():
        return "BINARY_MISSING"
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--block-size", type=int, default=sh.DEFAULT_BLOCK_SIZE)
    a = ap.parse_args()
    probe(Path(a.out_dir), block_size=a.block_size)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
