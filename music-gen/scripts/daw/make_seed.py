#!/usr/bin/env python3
# ---
# created: 2026-08-28T04:15:00Z
# cycle: 1
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-DAW-SPIKE-1
# ---
"""Seed MIDI + shared chain spec for M-DAW-SPIKE-1.

Writes:
  data/daw_spike/seed.mid           — 8-bar C-major arpeggio + counter-line
  data/daw_spike/chain_spec.yaml    — shared chain spec (both engines read)

Deterministic; sha256 recorded.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import sys

import pretty_midi
import yaml

OUT_DIR = pathlib.Path(__file__).resolve().parents[2] / "data" / "daw_spike"
OUT_DIR.mkdir(parents=True, exist_ok=True)

SEED_MID = OUT_DIR / "seed.mid"
CHAIN_YAML = OUT_DIR / "chain_spec.yaml"


def make_midi() -> pretty_midi.PrettyMIDI:
    """Deterministic 8-bar 120 BPM MIDI: C-major arpeggio + two-note counter."""
    pm = pretty_midi.PrettyMIDI(initial_tempo=120.0)
    # 120 BPM -> 0.5s per beat; 4/4 => 2s per bar; 8 bars => 16s total.
    # But we only render 8s, so pack notes into 8s.
    inst = pretty_midi.Instrument(program=0, name="lead")

    # Arpeggio: C4 E4 G4 C5 repeating, 8th notes @ 120 BPM = 0.25s each.
    arp_pitches = [60, 64, 67, 72]
    n_beats = 32  # 8s @ 4 notes/s
    for i in range(n_beats):
        pitch = arp_pitches[i % 4]
        t0 = i * 0.25
        t1 = t0 + 0.22
        inst.notes.append(
            pretty_midi.Note(velocity=90, pitch=pitch, start=t0, end=t1)
        )

    # Counter-line: sustained G3 -> A3 alternating each bar (every 2s).
    counter_pitches = [55, 57]
    for bar in range(4):  # 4 bars * 2s = 8s
        p = counter_pitches[bar % 2]
        t0 = bar * 2.0
        t1 = t0 + 1.95
        inst.notes.append(
            pretty_midi.Note(velocity=75, pitch=p, start=t0, end=t1)
        )

    pm.instruments.append(inst)
    return pm


def sha256(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


CHAIN_SPEC = {
    "instrument": {
        "kind": "vst3",
        "name": "Surge XT",
        "path": "/usr/lib/vst3/Surge XT.vst3",
        "params": {
            # Surge XT master volume-slider (name resolved at load time).
            "A Volume": 0.7,
        },
    },
    "effect_1": {
        "kind": "vst3",
        "name": "Surge XT Effects",
        "path": "/usr/lib/vst3/Surge XT Effects.vst3",
        "params": {
            # Surge Effects: chorus-ish depth/mix defaults.
            "Mix": 0.35,
        },
    },
    "effect_2": {
        "kind": "lv2",
        "uri": "http://calf.sourceforge.net/plugins/Reverb",
        "name": "Calf Reverb",
        # DawDreamer cannot host LV2 → substitute VST3 documented in
        # data/daw_spike/chain_spec.dawdreamer_overrides.yaml.
        "params": {
            "wet": 0.30,
        },
    },
    "automation": {
        "target": {"processor": "effect_2", "param": "wet"},
        "curve": "linear",
        "from": 0.05,
        "to": 0.60,
        "duration_s": 8.0,
    },
    "render": {
        "sr_hz": 48000,
        "duration_s": 8.0,
        "bit_depth": 24,
        "block_size": 512,
    },
}

# DawDreamer-side substitution: Calf Reverb (LV2) is not hostable in
# DawDreamer's JUCE backend, so DawDreamer substitutes an equivalent
# open-source VST3 reverb. This IS a chain-spec divergence — reported in
# docs/daw_spike_report.md.
OVERRIDES = {
    "effect_2": {
        "kind": "vst3",
        "name": "Dragonfly Room Reverb",
        "candidates": [
            "/usr/lib/vst3/DragonflyRoomReverb-vst3.vst3",
            "/usr/lib/vst3/DragonflyReverb-vst3.vst3",
        ],
        "params_note": (
            "Dragonfly parameter names differ from Calf's; the automation"
            " target is remapped to the Dragonfly 'Dry Level' / 'Wet Level'"
            " parameter (whichever is exposed)."
        ),
    },
    "reason": (
        "DawDreamer's JUCE backend hosts VST3/AU natively but does NOT"
        " host LV2 directly. Substituting Dragonfly Room Reverb keeps the"
        " chain in open-source headless-capable territory per the fixed"
        " decision."
    ),
}


def main() -> int:
    pm = make_midi()
    pm.write(str(SEED_MID))
    CHAIN_YAML.write_text(yaml.safe_dump(CHAIN_SPEC, sort_keys=False))
    (OUT_DIR / "chain_spec.dawdreamer_overrides.yaml").write_text(
        yaml.safe_dump(OVERRIDES, sort_keys=False)
    )

    manifest = {
        "seed_midi": {
            "path": str(SEED_MID.relative_to(OUT_DIR.parents[1])),
            "sha256": sha256(SEED_MID),
            "duration_s": max(n.end for n in pm.instruments[0].notes),
            "n_notes": sum(len(i.notes) for i in pm.instruments),
        },
        "chain_spec": {
            "path": str(CHAIN_YAML.relative_to(OUT_DIR.parents[1])),
            "sha256": sha256(CHAIN_YAML),
        },
        "chain_spec_overrides": {
            "path": "data/daw_spike/chain_spec.dawdreamer_overrides.yaml",
            "sha256": sha256(
                OUT_DIR / "chain_spec.dawdreamer_overrides.yaml"
            ),
        },
    }
    (OUT_DIR / "seed_manifest.json").write_text(json.dumps(manifest, indent=2))
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
