#!/usr/bin/env python3
"""Probe VST3 parameter surfaces via DawDreamer."""
import dawdreamer as daw
import json
import sys

engine = daw.RenderEngine(48000, 512)


def dump(name, path):
    try:
        p = engine.make_plugin_processor(name, path)
    except Exception as e:
        print(f"[{name}] load failed: {e}")
        return
    try:
        params = p.get_parameters_description()
    except Exception as e:
        print(f"[{name}] get_parameters_description failed: {e}")
        return
    print(f"=== {name} ({len(params)} params) ===")
    for pd in params[:40]:
        print(f"  {pd.get('index'):>4}  {pd.get('name'):<40}  default={pd.get('defaultValue')}  min={pd.get('min')} max={pd.get('max')}")
    if len(params) > 40:
        print(f"  ... {len(params)-40} more")


dump("Surge XT", "/usr/lib/vst3/Surge XT.vst3")
dump("Surge XT Effects", "/usr/lib/vst3/Surge XT Effects.vst3")
