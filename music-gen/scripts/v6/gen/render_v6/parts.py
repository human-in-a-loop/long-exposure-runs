#!/usr/bin/python3
"""v6 Phase 4 — derived ensemble parts (pad, comp_guitar, percussion) from the composed song + plan.json.

created: 2026-10-04
milestone: M-V6-RENDER-4/realistic-renderer

The Phase-2 composer writes four stems (drums, bass, keys, melody). The ensemble plan (select.ensemble_plan) can add a
pad, a comping guitar and a percussion layer; their notes are DERIVED here, deterministically, from material the composer
already decided — no new harmony, no PRNG (SHA-256 draws on the song tag only for the thinning / instrument choices):
  pad          sustained chord tones from plan.json chord_slots (the voicing's top 3 voices moved into 55..79), each held
               to the next chord change (-30 ms); silent where the arrangement mutes keys; velocity 72.
  comp_guitar  the keys comping thinned: each keys onset group is kept with p = 0.55 (SHA on the onset slot), its top
               <= 3 voices moved into the guitar register 52..79 and strummed 12 ms apart (low -> high); held bars drop
               all but the first onset; silent where the arrangement mutes keys.
  percussion   an 8th-note shaker-style layer on the off-beats (16th slots 2, 6, 10, 14) using ONE mapped key of the
               percussion patch (SHA-chosen per song) with alternating 62/78 velocities; +1 accent hit on slot 0 of every
               second bar; silent where the arrangement mutes drums.
Returned notes use the midi_io note dicts ({index, pitch, velocity, start_s, end_s}).
"""
from __future__ import annotations

from scripts.v6.gen.common import u

PAD_RANGE, GUITAR_RANGE = (55, 79), (52, 79)
COMP_KEEP_P = 0.55
PAD_VELOCITY = 72
PERC_SLOTS = (2, 6, 10, 14)


def _into_range(p: int, lo: int, hi: int) -> int:
    while p < lo:
        p += 12
    while p > hi:
        p -= 12
    return p


def _muted(arr: list, bar: int, stem: str) -> bool:
    return 0 <= bar < len(arr) and stem in (arr[bar].get("mute") or [])


def pad_part(plan: dict, bpm: float) -> list:
    beat = 60.0 / bpm
    arr = plan.get("arrangement_per_bar") or []
    slots = sorted(plan.get("chord_slots") or [], key=lambda c: (c["bar"], c["beat"]))
    n_bars = plan.get("form", {}).get("n_bars") or (len(arr) or 1)
    notes, idx = [], 0
    for i, c in enumerate(slots):
        if not c.get("voicing") or _muted(arr, c["bar"], "keys"):
            continue
        t0 = (c["bar"] * 4 + c["beat"]) * beat
        t1 = ((slots[i + 1]["bar"] * 4 + slots[i + 1]["beat"]) * beat) if i + 1 < len(slots) else n_bars * 4 * beat
        voices = sorted({_into_range(p, *PAD_RANGE) for p in sorted(c["voicing"])[-3:]})
        for p in voices:
            notes.append({"index": idx, "pitch": p, "velocity": PAD_VELOCITY, "start_s": round(t0, 6), "end_s": round(max(t0 + 0.1, t1 - 0.03), 6)})
            idx += 1
    return notes


def comp_guitar_part(keys_notes: list, plan: dict, bpm: float, tag: str) -> list:
    beat = 60.0 / bpm
    arr = plan.get("arrangement_per_bar") or []
    groups = {}
    for n in keys_notes:
        groups.setdefault(round(n["start_s"], 4), []).append(n)
    notes, idx = [], 0
    for t0 in sorted(groups):
        bar = int(t0 // (4 * beat))
        slot = int(round(t0 / (beat / 4)))
        if _muted(arr, bar, "keys"):
            continue
        held = bool(0 <= bar < len(arr) and arr[bar].get("hold"))
        if held and slot % 16 != 0:
            continue
        if not held and u(f"{tag}|comp_guitar|keep|{slot}") >= COMP_KEEP_P:
            continue
        grp = sorted(groups[t0], key=lambda n: n["pitch"])[-3:]
        voices = sorted({_into_range(n["pitch"], *GUITAR_RANGE) for n in grp})
        for j, p in enumerate(voices):
            src = grp[min(j, len(grp) - 1)]
            notes.append({"index": idx, "pitch": p, "velocity": int(src["velocity"]), "start_s": round(t0 + 0.012 * j, 6), "end_s": round(max(src["end_s"], t0 + 0.012 * j + 0.08), 6)})
            idx += 1
    return notes


def percussion_part(plan: dict, bpm: float, patch: dict, tag: str) -> list:
    beat = 60.0 / bpm
    arr = plan.get("arrangement_per_bar") or []
    n_bars = plan.get("form", {}).get("n_bars") or len(arr) or 1
    keys = patch.get("mapped_keys") or list(range(patch.get("note_range", [60, 72])[0] or 60, (patch.get("note_range", [60, 72])[1] or 72) + 1))
    key = keys[int(u(f"{tag}|percussion|key") * len(keys)) % len(keys)]
    notes, idx = [], 0
    for b in range(n_bars):
        if _muted(arr, b, "drums"):
            continue
        for k, s in enumerate(PERC_SLOTS):
            t0 = (b * 16 + s) * beat / 4
            notes.append({"index": idx, "pitch": key, "velocity": 78 if k % 2 == 0 else 62, "start_s": round(t0, 6), "end_s": round(t0 + 0.12, 6)})
            idx += 1
        if b % 2 == 1:
            t0 = b * 16 * beat / 4
            notes.append({"index": idx, "pitch": key, "velocity": 90, "start_s": round(t0, 6), "end_s": round(t0 + 0.12, 6)})
            idx += 1
    return sorted(notes, key=lambda n: (n["start_s"], n["pitch"]))
