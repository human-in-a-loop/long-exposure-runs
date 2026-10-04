#!/usr/bin/python3
"""v6 Phase 4 — MIDI expression so sampled instruments sound played: per-role velocity curves, CC11/CC1 swells, CC64 pedal.

created: 2026-10-04
milestone: M-V6-RENDER-4/realistic-renderer

realize_velocities(): the composer emits a handful of discrete velocities per role (keys 80/88, bass 85/100, melody
85..105). Those are mapped through a per-role curve onto the role's playing range (drums 45..125, bass 55..118, keys
40..112, ...) — rank-normalised input -> gamma curve -> metric accent (downbeat +8, beats +4, 8ths 0, 16th off-beats -4;
hats -10 so the kit breathes) -> per-bar SHA offset (+/-4, slow dynamics) -> per-note SHA jitter (+/-5) -> clamp. If the
realized range still spans < 60 units the velocities are stretched about their mean so the sfz velocity layers are
actually crossed. All draws are SHA-256 uniforms on seed-derived tags (common.u) — no PRNG.
expression_ccs(): CC11 (expression) swells per phrase on pads and sustained keys (organ / strings): 55 -> 100 over the
phrase's first bar, hold, back to 80 over its last beat, 8th-note resolution (+ a slow CC1 0..40 sweep on pads); CC64
sustain pedal for piano / electric-piano comping: down 10 ms after each chord change, up 25 ms before the next one (chord
changes from plan.json chord_slots, falling back to the note-onset groups). Hooks for Phase 3 humanization: notes keep
"offset_ms"/fractional starts (handled in midi_io.pair_events); nothing here quantises time.
"""
from __future__ import annotations

from scripts.v6.gen.common import u

MIN_SPAN = 60
ROLE_RANGE = {"drums": (45, 125), "bass": (55, 118), "keys": (40, 112), "comp_guitar": (45, 112), "melody": (60, 122), "pad": (50, 100), "percussion": (40, 110)}
ROLE_GAMMA = {"drums": 0.9, "bass": 1.0, "keys": 1.1, "comp_guitar": 1.0, "melody": 0.9, "pad": 1.0, "percussion": 1.0}
METRIC_ACCENT = {0: 8, 4: 4, 8: 4, 12: 4}  # 16th position in bar -> accent; 8ths 0; off-16ths -4
DRUM_CLASS_ACCENT = {42: -10, 44: -12, 46: -6, 36: 4, 38: 2, 40: 2}  # closed hat, pedal hat, open hat, kick, snares
SWELL_ROLES = ("pad",)
SWELL_KEYS_INVENTORY = ("organ", "strings_pad", "pad")
PEDAL_INVENTORY = ("piano", "electric_piano")


def pos16(start_s: float, bpm: float) -> int:
    s16 = 60.0 / bpm / 4.0
    return int(round(start_s / s16)) % 16


def bar_of(start_s: float, bpm: float) -> int:
    return int(start_s // (240.0 / bpm))


def realize_velocities(notes: list, role: str, patch: dict, tag: str, bpm: float) -> tuple[list, dict]:
    if not notes:
        return notes, {"n": 0}
    lo, hi = ROLE_RANGE.get(role, (50, 115))
    g = ROLE_GAMMA.get(role, 1.0)
    vin = [int(n["velocity"]) for n in notes]
    vmin, vmax = min(vin), max(vin)
    out = []
    for n in notes:
        t = (n["velocity"] - vmin) / (vmax - vmin) if vmax > vmin else 0.5
        v = lo + (t ** g) * (hi - lo)
        p = pos16(n["start_s"], bpm)
        v += METRIC_ACCENT.get(p, 0 if p % 2 == 0 else -4)
        if role == "drums":
            v += DRUM_CLASS_ACCENT.get(int(n["pitch"]), 0)
        b = bar_of(n["start_s"], bpm)
        v += (u(f"{tag}|bar_dyn|{b}") - 0.5) * 8.0
        v += (u(f"{tag}|jitter|{n['index']}|{n['pitch']}") - 0.5) * 10.0
        out.append(dict(n, velocity=int(round(max(1.0, min(127.0, v)))), velocity_in=int(n["velocity"])))
    vs = [n["velocity"] for n in out]
    span0 = max(vs) - min(vs)
    stretched = False
    if len(out) >= 2 and span0 < MIN_SPAN:
        mean = sum(vs) / len(vs)
        f = MIN_SPAN / max(span0, 1)
        for n in out:
            n["velocity"] = int(round(max(1.0, min(127.0, mean + (n["velocity"] - mean) * f))))
        vs, stretched = [n["velocity"] for n in out], True
    layers = patch.get("velocity_layers")
    return out, {"n": len(out), "input_range": [vmin, vmax], "role_range": [lo, hi], "gamma": g, "realized_range": [min(vs), max(vs)], "realized_span": max(vs) - min(vs),
                "span_before_stretch": span0, "stretched_to_min_span": stretched, "patch_velocity_layers": layers, "mean_velocity": round(sum(vs) / len(vs), 2)}


def _chord_times(plan: dict | None, notes: list, bpm: float) -> list:
    beat = 60.0 / bpm
    if plan and plan.get("chord_slots"):
        ts = sorted({round((c["bar"] * 4 + c["beat"]) * beat, 6) for c in plan["chord_slots"]})
        return ts
    return sorted({round(n["start_s"], 3) for n in notes})


def _phrases(plan: dict | None, song_len_s: float, bpm: float) -> list:
    bar = 240.0 / bpm
    if plan and plan.get("phrases"):
        return [(ph["start_bar"] * bar, (ph["start_bar"] + ph["n_bars"]) * bar) for ph in plan["phrases"]]
    n = max(1, int(round(song_len_s / bar)))
    return [(b * bar, min(n, b + 4) * bar) for b in range(0, n, 4)]


def _ramp(ccs: list, cc: int, t0: float, t1: float, v0: int, v1: int, step_s: float) -> None:
    n = max(1, int((t1 - t0) / step_s))
    for i in range(n + 1):
        f = i / n
        ccs.append((round(t0 + f * (t1 - t0), 6), cc, int(round(v0 + f * (v1 - v0)))))


def expression_ccs(notes: list, role: str, patch: dict, bpm: float, plan: dict | None, song_len_s: float) -> tuple[list, dict]:
    ccs, info = [], {"cc11_swells": 0, "cc1_sweeps": 0, "cc64_pedal_downs": 0}
    if not notes:
        return ccs, info
    beat, step = 60.0 / bpm, 60.0 / bpm / 2.0
    inv = patch.get("inventory_role", "")
    if role in SWELL_ROLES or (role == "keys" and inv in SWELL_KEYS_INVENTORY):
        for (t0, t1) in _phrases(plan, song_len_s, bpm):
            if not any(t0 - 1e-6 <= n["start_s"] < t1 for n in notes):
                continue
            a1 = min(t0 + 4 * beat, t1 - beat)
            _ramp(ccs, 11, t0, a1, 55, 100, step)
            ccs.append((round(max(a1 + step, t1 - beat) - 1e-3, 6), 11, 100))
            _ramp(ccs, 11, max(a1 + step, t1 - beat), t1 - 0.02, 100, 80, step)
            info["cc11_swells"] += 1
            if role == "pad":
                _ramp(ccs, 1, t0, t1 - 0.02, 0, 40, step * 2)
                info["cc1_sweeps"] += 1
    if role == "keys" and inv in PEDAL_INVENTORY:
        ts = [t for t in _chord_times(plan, notes, bpm) if t < song_len_s] + [song_len_s]
        ends = {}
        for n in notes:
            ends[n["start_s"]] = max(ends.get(n["start_s"], 0.0), n["end_s"])
        for i in range(len(ts) - 1):
            if not any(ts[i] - 1e-6 <= n["start_s"] < ts[i + 1] for n in notes):
                continue
            ccs.append((round(ts[i] + 0.010, 6), 64, 127))
            ccs.append((round(max(ts[i] + 0.05, ts[i + 1] - 0.025), 6), 64, 0))
            info["cc64_pedal_downs"] += 1
    ccs.sort(key=lambda c: (c[0], c[1], c[2]))
    info["n_cc"] = len(ccs)
    return ccs, info


def apply(notes: list, role: str, patch: dict, tag: str, bpm: float, plan: dict | None, song_len_s: float) -> tuple[list, list, dict]:
    notes2, vinfo = realize_velocities(notes, role, patch, f"{tag}|vel|{role}", bpm)
    ccs, cinfo = expression_ccs(notes2, role, patch, bpm, plan, song_len_s)
    return notes2, ccs, {"velocity": vinfo, "cc": cinfo}
