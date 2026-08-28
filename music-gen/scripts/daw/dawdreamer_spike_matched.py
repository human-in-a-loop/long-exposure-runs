#!/usr/bin/env python3
"""DawDreamer render matched to the Ardour chain — 220 Hz sine → Chorus →
Reverb (with automated Output Mix) + master-track gain ramp 0.25→1.4.

The Ardour side sources audio from the SinGen LuaProcessor (built-in
Ardour tone generator) and applies the same chain, so this render is
the twin used for cross-engine agreement.

Writes: data/daw_spike/dawdreamer_render_matched.wav
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
BLOCK = 512
DUR = 8.0
N = int(SR * DUR)

# Generate a matched sine source: 220 Hz, gain -12 dB (as per SinGen).
t = np.arange(N, dtype=np.float32) / SR
amp = 10 ** (-12 / 20)   # -12 dB
sine = amp * np.sin(2 * np.pi * 220.0 * t).astype(np.float32)
stereo = np.stack([sine, sine], axis=0)  # (2, N)

# Write sine to a temp WAV so PlaybackProcessor can load it.
sine_wav = OUT / "sine_source.wav"
sf.write(str(sine_wav), stereo.T, SR, subtype="PCM_24")

engine = daw.RenderEngine(SR, BLOCK)
playback = engine.make_playback_processor("sine", stereo)  # (2, N)
fx_chorus = engine.make_plugin_processor("fx_chorus", "/usr/lib/vst3/Surge XT Effects.vst3")
fx_reverb = engine.make_plugin_processor("fx_reverb", "/usr/lib/vst3/Surge XT Effects.vst3")

# Configure FX Types on Surge XT Effects (normalized values).
# Chorus at 0.28, Reverb 1 at 0.02 (matches ardour_spike.lua).
def _find(p, needle):
    for pd in p.get_parameters_description():
        if needle.lower() in pd["name"].lower():
            return int(pd["index"])
    raise KeyError(needle)

fx_chorus.set_parameter(_find(fx_chorus, "FX Type"), 0.28)
fx_chorus.set_parameter(_find(fx_chorus, "Output Mix"), 0.35)
fx_reverb.set_parameter(_find(fx_reverb, "FX Type"), 0.02)
fx_reverb.set_parameter(_find(fx_reverb, "Output Mix"), 0.05)

# Automation: reverb Output Mix 0.05→0.60 linear.
auto_rev = np.linspace(0.05, 0.60, N, dtype=np.float32)
fx_reverb.set_automation(_find(fx_reverb, "Output Mix"), auto_rev)

# Track-gain ramp equivalent to Ardour's Amp automation (0.25→1.4 linear
# coefficient). DawDreamer doesn't expose a "track gain" separate from the
# graph output; we apply this ramp post-hoc as an amplitude envelope.
graph = [
    (playback, []),
    (fx_chorus, [playback.get_name()]),
    (fx_reverb, [fx_chorus.get_name()]),
]
engine.load_graph(graph)
engine.render(DUR)
audio = engine.get_audio()   # (2, N)

# Apply track-gain envelope 0.25→1.4 linear.
env = np.linspace(0.25, 1.4, N, dtype=np.float32)
audio = audio * env[np.newaxis, :]

out_wav = OUT / "dawdreamer_render_matched.wav"
sf.write(str(out_wav), audio.T, SR, subtype="PCM_24")

report = {
    "wav": str(out_wav.relative_to(ROOT)),
    "wav_sha256": hashlib.sha256(out_wav.read_bytes()).hexdigest(),
    "sr_hz": SR,
    "duration_s": DUR,
    "peak": float(np.max(np.abs(audio))),
    "rms": float(np.sqrt(np.mean(audio**2))),
    "chain": {
        "source": "220 Hz sine @ -12 dB (2 ch)",
        "fx_chorus": "Surge XT Effects VST3 FX_Type=Chorus (0.28), Output Mix=0.35",
        "fx_reverb": "Surge XT Effects VST3 FX_Type=Reverb 1 (0.02), Output Mix 0.05→0.60 automated",
        "post_env": "track-gain 0.25→1.4 linear (matches Ardour Amp automation)",
    },
}
(OUT / "dawdreamer_matched_report.json").write_text(json.dumps(report, indent=2))
print(json.dumps(report, indent=2))
