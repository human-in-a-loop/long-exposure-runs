#!/usr/bin/env python3
"""Render seed.mid through Surge XT VST3 only (no fx).

Produces the audio content that Ardour's audio-track fallback path uses
as a pre-rendered stem, so both Ardour and DawDreamer apply the same
Surge XT Effects chain to identical instrument audio.

Writes: data/daw_spike/seed_synth.wav
"""
import hashlib
import json
import pathlib

import dawdreamer as daw
import numpy as np
import soundfile as sf

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / "data" / "daw_spike"
SR = 48000
DURATION = 8.0

engine = daw.RenderEngine(SR, 512)
synth = engine.make_plugin_processor("synth", "/usr/lib/vst3/Surge XT.vst3")
synth.load_midi(str(OUT / "seed.mid"))
engine.load_graph([(synth, [])])
engine.render(DURATION)
audio = engine.get_audio()
out = OUT / "seed_synth.wav"
sf.write(str(out), audio.T, SR, subtype="PCM_24")
h = hashlib.sha256(out.read_bytes()).hexdigest()
report = {
    "path": str(out.relative_to(ROOT)),
    "sha256": h,
    "sr_hz": SR,
    "duration_s": DURATION,
    "peak": float(np.max(np.abs(audio))),
    "rms": float(np.sqrt(np.mean(audio**2))),
}
(OUT / "seed_synth_report.json").write_text(json.dumps(report, indent=2))
print(json.dumps(report, indent=2))
