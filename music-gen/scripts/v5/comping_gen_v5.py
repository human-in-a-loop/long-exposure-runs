#!/usr/bin/python3
"""c87 F3 — comping-part event builder (guitar / piano / other) from the corpus comping statistics (data/v5/rules/comping_v5.json).

created: 2026-09-10T01:56:00Z
cycle: 87
run_id: run-2026-09-06T000000Z
agent: worker
milestone: M-V5-GEN-1/F3-guitar-piano-other

STANDALONE module (NOT yet wired into scripts/v5/generate_v5.py): the iteration-3 generator image (sha f261690c…) is pinned by the c87
byte-determinism record, the rollup and the listening manifests, so the `--f3` flag is wired in c88 together with iteration 4 (which
also consumes the n=23 harmony chain). Flag-off behaviour is therefore trivially unchanged this cycle (generate_v5.py untouched after
the P0 edit). Disclosed as F3_FLAG_WIRING_DEFERRED_c88.

Design (pre-registered in data/v5/rules/comping_prereg_c87.json as the statistics; generator use disclosed here): per bar, hits are
placed by WALKING inter-onset intervals sampled from the stem's 16th-IOI histogram (SHA-256 inverse-CDF on the caller's `u`); the
16th-slot histogram is NOT used because it is near-uniform (pooled 0.0599..0.0652 vs 0.0625 — structureless; disclosed by the c87
comping teammate). Each hit voices `round(chord_size_mean)` chord tones (capped by the chord's pitch classes, octave-stacked from the
comping register) for `min(sustain_ratio_beats, ioi)` beats. 'N' (no chord) bars rest. Velocities come from an optional callable
(`velocity_fn(tag) -> int`) so the F2 ladder sampler plugs in unchanged.

Public API: build_comp_events(chords, tonic, bpm, model, tag, u, stem="guitar", velocity_fn=None, register_low=52) -> list[event]
Events use the canonical JSON-events schema (index-keyed starts, end events with start_event_index) accepted by both serializers.
No PRNG, no wall-clock, no dict-order dependence.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

if sys.executable != "/usr/bin/python3" and "SUPPRESS_INTERPRETER_GUARD" not in os.environ:
    print(f"FATAL: expected /usr/bin/python3, got {sys.executable}", file=sys.stderr)
    sys.exit(2)

_WS = Path(__file__).resolve().parent.parent.parent
if str(_WS) not in sys.path:
    sys.path.insert(0, str(_WS))

INSTRUMENT = {"guitar": "electric_guitar_clean", "piano": "acoustic_grand_piano", "other": "synth_pad"}
GM_PROGRAM = {"guitar": 27, "piano": 0, "other": 89}  # GM shims (not profiled) — disclosed like SHIMS in generate_v5


def _state_pcs(state: str, tonic: int) -> list | None:
    from scripts.v5.generate_v5 import state_pcs  # READ-ONLY reuse of the c84 chord-state parser
    return state_pcs(state, tonic)


def sample_ioi(hist: list, x: float) -> int:
    """Inverse-CDF over the 16-bin IOI histogram (bins 1..16 sixteenths); x in [0,1)."""
    tot = sum(hist) or 1.0
    acc = 0.0
    for i, h in enumerate(hist):
        acc += h / tot
        if x < acc:
            return i + 1
    return len(hist)


def voice(pcs: list, n: int, register_low: int) -> list:
    """Stack up to n chord tones ascending from register_low (chord tones cycle through octaves; deterministic)."""
    out, k = [], 0
    while len(out) < n and k < 4 * max(1, len(pcs)):
        pc = pcs[k % len(pcs)]
        octave = k // len(pcs)
        pitch = register_low + ((pc - register_low) % 12) + 12 * octave
        if pitch <= 108:
            out.append(pitch)
        k += 1
    return out


def build_comp_events(chords: list, tonic: int, bpm: float, model: dict, tag: str, u, stem: str = "guitar",
                      velocity_fn=None, register_low: int = 52) -> list:
    st = model["stats"][stem]
    hist = st["ioi16_histogram"]
    n_voices = max(1, int(round(st["chord_size_mean"])))
    sustain_beats = float(st["sustain_ratio"])
    beat = 60.0 / bpm
    s16 = beat / 4
    ev, idx = [], 0
    inst = INSTRUMENT[stem]
    for b, state in enumerate(chords):
        pcs = _state_pcs(state, tonic)
        if not pcs:
            continue
        t_bar = b * 4 * beat
        pos = 0
        while pos < 16:
            ioi = sample_ioi(hist, u(f"{tag}|F3|{stem}|bar{b}|pos{pos}"))
            dur_beats = min(sustain_beats, ioi / 4.0)
            t0 = t_bar + pos * s16
            t1 = t0 + max(0.05, dur_beats * beat - 0.01)
            vel = int(velocity_fn(f"{tag}|F3|{stem}|vel|bar{b}|pos{pos}")) if velocity_fn else None
            for pitch in voice(pcs, min(n_voices, 6), register_low):
                s = {"index": idx, "instrument": inst, "pitch": int(pitch), "start_time": round(t0, 6), "type": "start"}
                if vel is not None:
                    s["velocity"] = max(1, min(127, vel))
                ev.append(s)
                ev.append({"start_event_index": idx, "end_time": round(t1, 6), "type": "end"})
                idx += 1
            pos += ioi
    return ev
