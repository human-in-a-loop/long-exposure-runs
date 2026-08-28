#!/usr/bin/env python3
# ---
# created: 2026-08-28T04:20:00Z
# cycle: 1
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-DAW-SPIKE-1
# ---
"""DawDreamer render for M-DAW-SPIKE-1.

Reads:
  data/daw_spike/chain_spec.yaml
  data/daw_spike/chain_spec.dawdreamer_overrides.yaml   # LV2 → VST3 sub
  data/daw_spike/seed.mid

Renders instrument + delay + reverb (all Surge XT / Surge XT Effects VST3)
with linear ramp automation on the reverb's "Output Mix" parameter.

Writes:
  data/daw_spike/dawdreamer_render.wav
  data/daw_spike/dawdreamer_state.json  — plugin params + automation curve
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import sys

import dawdreamer as daw
import numpy as np
import soundfile as sf
import yaml

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / "data" / "daw_spike"

SR = 48000
BLOCK = 512
DURATION = 8.0

SPEC = yaml.safe_load((OUT / "chain_spec.yaml").read_text())
OVR = yaml.safe_load((OUT / "chain_spec.dawdreamer_overrides.yaml").read_text())

VST_INSTR = SPEC["instrument"]["path"]
VST_FX = "/usr/lib/vst3/Surge XT Effects.vst3"


def find_param_index(processor, name_substr: str) -> int:
    for pd in processor.get_parameters_description():
        if name_substr.lower() in pd["name"].lower():
            return int(pd["index"])
    raise KeyError(f"parameter matching {name_substr!r} not found")


def find_fx_type_index(processor) -> int:
    return find_param_index(processor, "FX Type")


def normalize_fx_type(processor, kind: str) -> float:
    """Search FX Type text labels for a name substring; return normalized value.

    Surge XT Effects' FX Type parameter is enumerated. We iterate normalized
    values across [0,1] and read back get_parameter_text to find the one that
    stringifies to 'Reverb', 'Chorus', etc.
    """
    idx = find_fx_type_index(processor)
    # Try dense sweep 0..1 in 0.02 steps and read text; keep the first match.
    for v in np.linspace(0.0, 1.0, 51):
        processor.set_parameter(idx, float(v))
        try:
            txt = processor.get_parameter_text(idx)
        except Exception:
            txt = ""
        if kind.lower() in txt.lower():
            return float(v)
    return 0.0


def build_engine() -> tuple[daw.RenderEngine, dict]:
    engine = daw.RenderEngine(SR, BLOCK)
    synth = engine.make_plugin_processor("synth", VST_INSTR)
    fx_delay = engine.make_plugin_processor("fx_delay", VST_FX)
    fx_reverb = engine.make_plugin_processor("fx_reverb", VST_FX)

    # Instrument: load MIDI.
    synth.load_midi(str(OUT / "seed.mid"))

    # Set FX Types.
    delay_v = normalize_fx_type(fx_delay, "chorus")
    reverb_v = normalize_fx_type(fx_reverb, "reverb")

    # Static param set on delay: Output Mix = 0.35 (raw / [0,1] param space).
    delay_mix_idx = find_param_index(fx_delay, "Output Mix")
    fx_delay.set_parameter(delay_mix_idx, 0.35)

    # Reverb baseline: Output Mix set to 0.05 (start of automation).
    reverb_mix_idx = find_param_index(fx_reverb, "Output Mix")
    fx_reverb.set_parameter(reverb_mix_idx, 0.05)

    # Automation curve on reverb Output Mix: 0.05 → 0.60 linear over 8 s.
    # DawDreamer expects a per-sample automation array.
    n_samples = int(SR * DURATION)
    auto = np.linspace(0.05, 0.60, n_samples, dtype=np.float32)
    fx_reverb.set_automation(reverb_mix_idx, auto)

    graph = [
        (synth, []),
        (fx_delay, [synth.get_name()]),
        (fx_reverb, [fx_delay.get_name()]),
    ]
    engine.load_graph(graph)

    state = {
        "sr_hz": SR,
        "block_size": BLOCK,
        "duration_s": DURATION,
        "synth": {
            "path": VST_INSTR,
            "midi": "data/daw_spike/seed.mid",
            "n_params": len(synth.get_parameters_description()),
        },
        "fx_delay": {
            "path": VST_FX,
            "fx_type_normalized": delay_v,
            "fx_type_text": fx_delay.get_parameter_text(
                find_fx_type_index(fx_delay)
            ),
            "output_mix": 0.35,
        },
        "fx_reverb": {
            "path": VST_FX,
            "fx_type_normalized": reverb_v,
            "fx_type_text": fx_reverb.get_parameter_text(
                find_fx_type_index(fx_reverb)
            ),
            "automation": {
                "param": "Output Mix",
                "from": 0.05,
                "to": 0.60,
                "n_samples": n_samples,
            },
        },
    }
    return engine, state


def sha256(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def main() -> int:
    engine, state = build_engine()
    engine.render(DURATION)
    audio = engine.get_audio()  # shape (2, n_samples)
    print("audio shape:", audio.shape, "peak:", float(np.max(np.abs(audio))))
    out_wav = OUT / "dawdreamer_render.wav"
    # DawDreamer returns (channels, samples); soundfile wants (samples, channels).
    sf.write(str(out_wav), audio.T, SR, subtype="PCM_24")
    (OUT / "dawdreamer_state.json").write_text(json.dumps(state, indent=2))
    report = {
        "wav": str(out_wav.relative_to(ROOT)),
        "wav_sha256": sha256(out_wav),
        "duration_s": DURATION,
        "sr_hz": SR,
        "peak": float(np.max(np.abs(audio))),
        "rms": float(np.sqrt(np.mean(audio**2))),
        "state": state,
    }
    (OUT / "dawdreamer_report.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
