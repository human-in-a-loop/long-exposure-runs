#!/usr/bin/python3
"""Phase 4 (instrument realism) — headless Surge XT / Dexed renders through DawDreamer.

created: 2026-10-04
milestone: M-V6-INSTRUMENTS-1

DawDreamer 0.9.0 loads both VST3s ("/usr/lib/vst3/Surge XT.vst3", "/usr/lib/vst3/Dexed.vst3").
Preset handling:
  * Surge XT ships 3008 factory patches as .fxp under /usr/share/surge-xt/patches_factory.
    DawDreamer's load_preset()/load_vst3_preset() do not accept them for the VST3 build, so we
    take the raw 'sub3' patch stream from the .fxp (after its 60-byte fxChunkSet header), wrap it
    in the JUCE host-side state XML (<VST3PluginState><IComponent>JUCE-base64</IComponent>)
    that save_state() produces, and feed that to load_state(). Verified: renders change per patch.
  * Dexed exposes the current cartridge's 32 programs through its 'Program' parameter
    (index 157, normalized i/31). Dexed 1.0.1 ships a default cartridge (no Yamaha ROM1A
    E.PIANO 1); roles below were assigned from an envelope/brightness survey of all 32 programs.

Usage:
  render_vst_test.py                 # register dawdreamer libraries in INVENTORY.json and render them all
  render_vst_test.py --list          # just print the candidate entries
  render_vst_test.py --determinism   # render one Surge + one Dexed entry twice and compare sha256

Caveat: Surge XT is NOT bit-deterministic between renders (unison/LFO/noise randomization), unlike
sfizz_render and fluidsynth; entries carry "deterministic": false.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import struct
import sys
from pathlib import Path

import mido
import numpy as np
import soundfile as sf

sys.path.insert(0, str(Path(__file__).resolve().parent))
from render_patch_test import (INSTR_ROOT, INVENTORY, RENDERS, SAMPLE_RATE,  # noqa: E402
                               analyze_wav, render_entry, write_test_midi)

SURGE_VST3 = "/usr/lib/vst3/Surge XT.vst3"
DEXED_VST3 = "/usr/lib/vst3/Dexed.vst3"
SURGE_PATCHES = Path("/usr/share/surge-xt/patches_factory")
SURGE_STATE_DIR = INSTR_ROOT / "surge_xt" / "states"
DEXED_PROGRAM_PARAM = 157
BLOCK_SIZE = 512

SURGE_ENTRIES = [  # (relative fxp, role, notes)
    ("Pads/Pad 1.fxp", "pad", "classic analog-style pad"),
    ("Pads/MKS-70 Warm Pad.fxp", "pad", "JX-10 style warm pad"),
    ("Pads/Subtle Comb Strings.fxp", "strings_pad", "comb-filter string pad"),
    ("Leads/Classic Lead 1.fxp", "lead", "classic mono-style synth lead"),
    ("Leads/Crisp PWM.fxp", "lead", "PWM lead"),
    ("Keys/DX EP.fxp", "electric_piano", "FM DX-style electric piano"),
    ("Keys/Soft Suitcase.fxp", "electric_piano", "Rhodes suitcase-style e-piano"),
    ("Keys/EP 1.fxp", "electric_piano", "electric piano 1"),
    ("Keys/Organ 1.fxp", "organ", "synth organ"),
    ("Basses/Fingered.fxp", "synth_bass", "fingered-bass style synth bass"),
    ("Basses/Bass 1.fxp", "synth_bass", "analog synth bass"),
    ("Basses/E-Bass.fxp", "synth_bass", "electric-bass style synth bass"),
]
DEXED_ENTRIES = [  # (program index in default cartridge, role, notes)
    (30, "pad", "'Slow3D Pad' — sustained pad"),
    (7, "pad", "'OB GenvivY' — slow-attack sustained pad"),
    (8, "lead", "'SAW EM UP' — bright sustained saw-like lead"),
    (1, "lead", "'LAURIE' — bright sustained lead"),
    (11, "synth_bass", "'Thunder 3' — low, decaying FM bass"),
    (3, "synth_bass", "'PHAROH' — low FM bass/pluck"),
    (4, "electric_piano", "'Chroma 5 Y' — bright decaying FM keys (not an E.PIANO 1 clone)"),
    (15, "electric_piano", "'FLEXI 4' — plucky decaying FM keys"),
]

# ----------------------------------------------------------------------------- JUCE state plumbing
_JUCE_TBL = ".ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+"


def juce_b64(data: bytes) -> str:
    """juce::MemoryBlock::toBase64Encoding — '<size>.' + 6-bit LSB-first chunks over a custom alphabet."""
    n = len(data)
    nchars = ((n << 3) + 5) // 6
    v = int.from_bytes(data, "little")
    return f"{n}." + "".join(_JUCE_TBL[(v >> (6 * i)) & 63] for i in range(nchars))


def fxp_payload(fxp: Path) -> bytes:
    b = fxp.read_bytes()
    if b[:4] != b"CcnK" or b[8:12] != b"FPCh":
        raise ValueError(f"not an opaque-chunk fxp: {fxp}")
    csz = struct.unpack(">I", b[56:60])[0]
    return b[60:60 + csz]


def surge_state_for_fxp(template_state: bytes, fxp: Path) -> bytes:
    n = struct.unpack("<i", template_state[4:8])[0]
    xml = template_state[8:8 + n].decode("utf-8", "replace")
    xml = re.sub(r"<IComponent>[^<]*</IComponent>", "<IComponent>" + juce_b64(fxp_payload(fxp)) + "</IComponent>", xml)
    xml = re.sub(r"<IEditController>[^<]*</IEditController>", "", xml)
    body = xml.encode("utf-8")
    return template_state[:4] + struct.pack("<i", len(body) + 1) + body + b"\0"


# ----------------------------------------------------------------------------- engine
_ENGINE = None
_PLUGINS: dict[str, object] = {}
_SURGE_TEMPLATE: bytes | None = None


def _engine():
    global _ENGINE
    if _ENGINE is None:
        import dawdreamer as daw
        _ENGINE = daw.RenderEngine(SAMPLE_RATE, BLOCK_SIZE)
    return _ENGINE


def _plugin(path: str):
    if path not in _PLUGINS:
        _PLUGINS[path] = _engine().make_plugin_processor(re.sub(r"\W+", "_", Path(path).stem), path)
    return _PLUGINS[path]


def _midi_length_sec(mid: Path) -> float:
    return float(mido.MidiFile(str(mid)).length)


def render_vst_entry(inst: dict, mid: Path, out_wav: Path) -> None:
    """Render a dawdreamer inventory entry: {plugin, preset (Surge .fxp) | program (Dexed)}."""
    global _SURGE_TEMPLATE
    eng = _engine()
    plug = _plugin(inst["plugin"])
    if "preset" in inst:
        if _SURGE_TEMPLATE is None:
            SURGE_STATE_DIR.mkdir(parents=True, exist_ok=True)
            tmpl = SURGE_STATE_DIR / "_default.state"
            plug.save_state(str(tmpl))
            _SURGE_TEMPLATE = tmpl.read_bytes()
        state = SURGE_STATE_DIR / (re.sub(r"\W+", "_", Path(inst["preset"]).stem) + ".state")
        state.write_bytes(surge_state_for_fxp(_SURGE_TEMPLATE, Path(inst["preset"])))
        plug.load_state(str(state))
    if "program" in inst:
        plug.set_parameter(DEXED_PROGRAM_PARAM, float(inst["program"]) / 31.0)
    plug.clear_midi()
    plug.load_midi(str(mid), clear_previous=True, beats=False, all_events=True)
    eng.load_graph([(plug, [])])
    eng.render(_midi_length_sec(mid) + 0.5)
    audio = eng.get_audio()  # (channels, samples) float32
    out_wav.parent.mkdir(parents=True, exist_ok=True)
    sf.write(str(out_wav), np.ascontiguousarray(audio.T), SAMPLE_RATE, subtype="FLOAT")
    plug.clear_midi()


# ----------------------------------------------------------------------------- inventory registration
def dawdreamer_libraries() -> list[dict]:
    import dawdreamer
    surge = []
    for relp, role, notes in SURGE_ENTRIES:
        p = SURGE_PATCHES / relp
        if p.exists():
            surge.append({"name": f"Surge XT: {p.stem}", "role": role, "backend": "dawdreamer", "plugin": SURGE_VST3,
                          "preset": str(p), "path": str(p), "notes": notes + " (factory patch, loaded via JUCE state substitution)",
                          "deterministic": False})
    dexed = []
    if Path(DEXED_VST3).exists():
        plug = _plugin(DEXED_VST3)
        for prog, role, notes in DEXED_ENTRIES:
            plug.set_parameter(DEXED_PROGRAM_PARAM, prog / 31.0)
            pname = plug.get_parameter_text(DEXED_PROGRAM_PARAM).strip()
            dexed.append({"name": f"Dexed: {pname} [{prog}]", "role": role, "backend": "dawdreamer", "plugin": DEXED_VST3,
                          "program": prog, "program_name": pname, "path": f"{DEXED_VST3}#program={prog}",
                          "notes": notes + " (default cartridge)", "deterministic": None})
    libs = []
    if surge:
        libs.append({"slug": "surge_xt", "source_url": "(preinstalled: Surge XT 1.3.4 VST3 + /usr/share/surge-xt/patches_factory)",
                     "license": {"id": "GPL-3.0-only", "url": "https://github.com/surge-synthesizer/surge/blob/main/LICENSE",
                                 "file": "/usr/share/surge-xt/doc/copyright"},
                     "size_mb": 0.0, "format": "dawdreamer", "host": f"dawdreamer {dawdreamer.__version__}",
                     "roles": sorted({e["role"] for e in surge}), "instruments": surge, "preinstalled": True})
    if dexed:
        libs.append({"slug": "dexed", "source_url": "(preinstalled: Dexed 1.0.1 VST3, default cartridge)",
                     "license": {"id": "GPL-3.0-only", "url": "https://github.com/asb2m10/dexed/blob/master/LICENSE", "file": None},
                     "size_mb": 0.0, "format": "dawdreamer", "host": f"dawdreamer {dawdreamer.__version__}",
                     "roles": sorted({e["role"] for e in dexed}), "instruments": dexed, "preinstalled": True})
    return libs


def register(inv_path: Path = INVENTORY) -> dict:
    inv = json.load(open(inv_path, encoding="utf-8"))
    inv["libraries"] = [l for l in inv["libraries"] if l.get("format") != "dawdreamer"] + dawdreamer_libraries()
    with open(inv_path, "w", encoding="utf-8") as fh:
        json.dump(inv, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    return inv


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--determinism", action="store_true")
    args = ap.parse_args(argv)
    try:
        import dawdreamer  # noqa: F401
    except Exception as exc:  # noqa: BLE001
        print(f"dawdreamer unavailable: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 3
    if args.list:
        print(json.dumps(dawdreamer_libraries(), indent=2))
        return 0
    inv = register()
    libs = [l for l in inv["libraries"] if l.get("format") == "dawdreamer"]
    if args.determinism:
        for lib in libs:
            inst = lib["instruments"][0]
            shas = []
            for k in range(2):
                out = RENDERS / "_detcheck" / f"{lib['slug']}_{k}.wav"
                mid = RENDERS / "_detcheck" / f"{lib['slug']}.mid"
                write_test_midi(mid, inst["role"])
                render_vst_entry(inst, mid, out)
                shas.append(hashlib.sha256(out.read_bytes()).hexdigest())
            print(f"{lib['slug']:10} {inst['name']:40} identical={shas[0] == shas[1]}")
        return 0
    summary_path = RENDERS / "_render_summary.json"
    prev = json.load(open(summary_path)) if summary_path.exists() else {}
    n_ok = 0
    for lib in libs:
        for inst in lib["instruments"]:
            rec = render_entry(lib, inst)
            prev[f"{lib['slug']}::{inst['name']}"] = rec
            n_ok += rec["status"] == "ok"
            extra = f"rms={rec.get('rms_dbfs')} peak={rec.get('peak_dbfs')} dur={rec.get('duration_sec')}" \
                if rec["status"] != "error" else rec.get("error", "")[:160]
            print(f"[{rec['status'].upper():6}] {lib['slug']:10} {inst['name'][:40]:40} {extra}", flush=True)
    with open(summary_path, "w", encoding="utf-8") as fh:
        json.dump(prev, fh, indent=2, sort_keys=True)
        fh.write("\n")
    print(f"dawdreamer: {n_ok} ok of {sum(len(l['instruments']) for l in libs)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
