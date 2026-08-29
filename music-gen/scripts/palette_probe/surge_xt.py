#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-29T02:15:00Z
# cycle: 31
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-DAW-SPIKE-1/palette-instrument-determinism
# ---
"""Cycle-31 probe: Surge XT instrument (VST3) determinism.

Loads Surge XT.vst3 as a plugin instrument in DawDreamer, plays the fixed
8s ascending-diatonic MIDI at 44.1 kHz stereo, renders `render.wav`, and
serializes the pinned plugin state to `pinned_state.json`.

No PRNG. The cycle-9 DawDreamer effects chain is a read-only anchor
for this branch and is never imported here. Interpreter guard forces
/usr/bin/python3.
"""
from __future__ import annotations

import argparse
import sys
import wave
from pathlib import Path

# Import _shared FIRST — it sets BLAS pins before dawdreamer arrives.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.palette_probe import _shared as sh  # noqa: E402

assert sys.executable == "/usr/bin/python3", sys.executable

PLUGIN_PATH = "/usr/lib/vst3/Surge XT.vst3"
PLUGIN_NAME = "Surge XT"
LOADER_PATHWAY = "dawdreamer_vst3"


def _render_pcm16(
    out_dir: Path,
    block_size: int = sh.DEFAULT_BLOCK_SIZE,
    state_bytes: bytes | None = None,
) -> tuple[bytes, dict, bytes | None]:
    """Run the render; return (int16 PCM stereo bytes, parameter_dict, saved_state)."""
    import numpy as np  # noqa: F401 — imported by dawdreamer transitively
    import dawdreamer as daw

    engine = daw.RenderEngine(sh.SAMPLE_RATE, block_size)
    synth = engine.make_plugin_processor("surge_xt", PLUGIN_PATH)
    if state_bytes is not None:
        try:
            synth.load_state(state_bytes)
        except Exception as exc:
            print(f"WARN: Surge XT load_state failed: {exc}", file=sys.stderr)
    try:
        saved_state = synth.get_state()
        if isinstance(saved_state, str):
            saved_state = saved_state.encode()
    except Exception:
        saved_state = None

    # Enumerate and record parameters (pinned state).
    param_desc = synth.get_parameters_description()
    parameter_dict: dict = {}
    for pd in param_desc:
        # Deterministic key: name string; value: current numeric value.
        name = pd.get("name", f"index_{pd.get('index','?')}")
        idx = pd.get("index")
        try:
            val = float(synth.get_parameter(idx))
        except Exception:
            val = None
        parameter_dict[name] = val

    # Build the MIDI note list. DawDreamer's add_midi_note is deterministic.
    for note, on_s, off_s in sh.note_events_seconds():
        dur = off_s - on_s
        synth.add_midi_note(int(note), int(sh.VELOCITY), float(on_s), float(dur))

    engine.load_graph([(synth, [])])
    engine.render(sh.DURATION_S)
    audio = engine.get_audio()  # shape (channels, samples), float32/64
    # Ensure stereo; DawDreamer may return (2, N).
    import numpy as np
    audio = np.asarray(audio)
    if audio.ndim == 1:
        audio = np.stack([audio, audio], axis=0)
    if audio.shape[0] == 1:
        audio = np.repeat(audio, 2, axis=0)
    # Trim / pad to exactly SAMPLE_COUNT samples.
    if audio.shape[1] > sh.SAMPLE_COUNT:
        audio = audio[:, : sh.SAMPLE_COUNT]
    elif audio.shape[1] < sh.SAMPLE_COUNT:
        pad = np.zeros((audio.shape[0], sh.SAMPLE_COUNT - audio.shape[1]), dtype=audio.dtype)
        audio = np.concatenate([audio, pad], axis=1)
    # Convert to int16 PCM interleaved (byte-deterministic; wave writer
    # emits stable header bytes).
    clipped = np.clip(audio, -1.0, 1.0)
    pcm = (clipped * 32767.0).astype(np.int16)
    interleaved = pcm.T.tobytes(order="C")
    return interleaved, parameter_dict, saved_state


def _write_wave(out_path: Path, pcm_bytes: bytes) -> None:
    with wave.open(str(out_path), "wb") as w:
        w.setnchannels(sh.CHANNELS)
        w.setsampwidth(2)
        w.setframerate(sh.SAMPLE_RATE)
        w.writeframes(pcm_bytes)


def probe(
    out_dir: Path,
    block_size: int = sh.DEFAULT_BLOCK_SIZE,
    state_in: Path | None = None,
    state_out: Path | None = None,
) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    midi_path = sh.write_test_midi(out_dir / "input.mid")
    state_bytes = state_in.read_bytes() if state_in and state_in.exists() else None
    pcm, params, saved_state = _render_pcm16(out_dir, block_size=block_size, state_bytes=state_bytes)
    _write_wave(out_dir / "render.wav", pcm)
    ext_sha = None
    if state_bytes is not None:
        import hashlib as _hl
        ext_sha = _hl.sha256(state_bytes).hexdigest()
    if state_out is not None and saved_state is not None:
        state_out.parent.mkdir(parents=True, exist_ok=True)
        state_out.write_bytes(saved_state)
    state = {
        "block_size": block_size,
        "external_state_sha256": ext_sha,
        "loader_pathway": LOADER_PATHWAY,
        "midi_input_sha256": sh.sha256_of_path(midi_path),
        "parameter_dict": dict(sorted(params.items())),
        "plugin_binary_sha256": _plugin_binary_sha(),
        "plugin_name": PLUGIN_NAME,
        "plugin_version": None,  # DawDreamer 0.9 does not expose VST3 version
        "preset_name": None,     # no preset loaded — factory init state
        "sample_count": sh.SAMPLE_COUNT,
        "sample_rate": sh.SAMPLE_RATE,
        "stereo": True,
    }
    sh.write_pinned_state(out_dir, state)


def _plugin_binary_sha() -> str:
    """SHA-256 of a stable descriptor of the plugin bundle.

    VST3 is a bundle (directory), not a single file. We hash a
    sorted listing of file names + sizes inside the bundle so the
    value is stable across runs but sensitive to plugin replacement.
    """
    import hashlib, os
    root = Path(PLUGIN_PATH)
    if not root.exists():
        return "PLUGIN_MISSING"
    h = hashlib.sha256()
    entries = []
    for dp, dns, fns in os.walk(root):
        dns.sort()
        for fn in sorted(fns):
            fp = Path(dp) / fn
            try:
                sz = fp.stat().st_size
            except OSError:
                sz = -1
            entries.append(f"{fp.relative_to(root)}\t{sz}")
    for line in sorted(entries):
        h.update(line.encode())
        h.update(b"\n")
    return h.hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--block-size", type=int, default=sh.DEFAULT_BLOCK_SIZE)
    ap.add_argument("--state-in", default=None)
    ap.add_argument("--state-out", default=None)
    a = ap.parse_args()
    probe(
        Path(a.out_dir),
        block_size=a.block_size,
        state_in=Path(a.state_in) if a.state_in else None,
        state_out=Path(a.state_out) if a.state_out else None,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
