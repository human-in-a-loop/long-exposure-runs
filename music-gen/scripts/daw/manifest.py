#!/usr/bin/env python3
"""Assemble data/daw_spike/manifest.json — reproducibility record."""
import hashlib
import json
import pathlib
import subprocess

OUT = pathlib.Path("data/daw_spike")


def sh(p):
    if not p.exists():
        return None
    h = hashlib.sha256()
    h.update(p.read_bytes())
    return h.hexdigest()


def size(p):
    if not p.exists():
        return None
    return p.stat().st_size


artifacts = [
    "seed.mid",
    "chain_spec.yaml",
    "chain_spec.dawdreamer_overrides.yaml",
    "seed_synth.wav",
    "sine_source.wav",
    "ardour_render.wav",
    "dawdreamer_render.wav",
    "dawdreamer_render_matched.wav",
    "agreement.json",
    "agreement.png",
    "ardour_state.json",
    "dawdreamer_state.json",
    "dawdreamer_matched_report.json",
    "seed_synth_report.json",
    "dawdreamer_report.json",
]

scripts = [
    "scripts/daw/make_seed.py",
    "scripts/daw/dawdreamer_spike.py",
    "scripts/daw/dawdreamer_spike_matched.py",
    "scripts/daw/render_synth_only.py",
    "scripts/daw/ardour_spike.lua",
    "scripts/daw/patch_session_range.py",
    "scripts/daw/agreement.py",
    "scripts/daw/inspect_renders.py",
    "scripts/daw/probe_plugins.py",
]

# Tool versions.
def tool_ver(cmd, args):
    try:
        r = subprocess.run([cmd] + args, capture_output=True, text=True, timeout=10)
        return (r.stdout + r.stderr).strip().splitlines()[0]
    except Exception as e:
        return f"err: {e}"


manifest = {
    "milestone": "M-DAW-SPIKE-1",
    "cycle": 1,
    "run_id": "run-2026-08-28T040704Z",
    "sr_hz": 48000,
    "duration_s": 8.0,
    "artifacts": {
        f: {"sha256": sh(OUT / f), "bytes": size(OUT / f)}
        for f in artifacts
    },
    "scripts": {s: {"sha256": sh(pathlib.Path(s))} for s in scripts},
    "tools": {
        "ardour8-lua": tool_ver("ardour8-lua", ["-V"]),
        "python3": tool_ver("/usr/bin/python3", ["-V"]),
        "dawdreamer": "0.9.0 (pip; per PROVISIONING_REPORT)",
        "surge-xt": "1.3.4 (deb; per PROVISIONING_REPORT)",
    },
}
(OUT / "manifest.json").write_text(json.dumps(manifest, indent=2))
print(json.dumps(manifest, indent=2)[:2000])
