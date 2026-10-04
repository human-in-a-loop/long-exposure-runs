#!/usr/bin/python3
"""v6 Phase 2 — drums: v5 joint-groove sampling (kick8 -> snare16|kick8 -> hat16|kick8,snare16 -> bass16|kick8) + F1 fills.

created: 2026-10-04
milestone: M-V6-GEN-2/theory-grounded-composer

Bars are sampled per LABEL (literal repeats reproduce) by SHA-256 inverse-CDF over the groove tables (scripts.v5.groove_v5_v2
row_for/draw semantics, re-implemented in common.draw_row so no heavy import is needed). The bass16 mask of every bar is
handed to bassline.py. Arrangement effects at flatten time: fills (snare/hat masks from the pool) in the last bar of every
section, a held final bar (one kick), mutes. Velocities from velocity_profiles_v5.json quantile ladders when present
(sample_velocity = np.interp re-implemented in pure Python) else the accent table ACCENTS.
"""
from __future__ import annotations

from scripts.v6.gen.common import draw_row, u

KICK, SNARE, HAT = 36, 38, 42
HIT_S = 0.1
ACCENTS = {"kick_downbeat": 110, "kick": 100, "snare_backbeat": 105, "snare_ghost": 45, "hat_on": 70, "hat_off": 55, "fill_snare": 100}
QUANTS = (0, 10, 25, 50, 75, 90, 100)
BACKBEAT = (4, 12)


def row_for(tbl: dict, ctx: str) -> dict:
    if ctx in tbl["probs"]:
        return tbl["probs"][ctx]
    v = tbl["vocab"]
    return {o: 1.0 / len(v) for o in v}


def bits(x: int, n: int = 16) -> list:
    return [i for i in range(n) if int(x) >> i & 1]


def sample_bar(model: dict, tag: str, i: int) -> dict:
    k = draw_row(row_for(model["kick_marginal"], "*"), f"{tag}|bar{i}|kick|*")
    s = draw_row(row_for(model["snare_given_kick"], str(k)), f"{tag}|bar{i}|snare|{k}")
    h = draw_row(row_for(model["hat_given_kick_snare"], f"{k}|{s}"), f"{tag}|bar{i}|hat|{k}|{s}")
    b = draw_row(row_for(model["bass_given_kick"], str(k)), f"{tag}|bar{i}|bass|{k}")
    return {"kick": k, "snare": s, "hat": h, "bass": b}


def sample_groove_bars(groove: dict, tag: str, n: int) -> list:
    model = groove["model"] if "model" in groove else groove
    return [sample_bar(model, tag, i) for i in range(n)]


def interp(x: float, xs, ys) -> float:
    if x <= xs[0]:
        return float(ys[0])
    for i in range(1, len(xs)):
        if x <= xs[i]:
            t = (x - xs[i - 1]) / (xs[i] - xs[i - 1])
            return float(ys[i - 1]) + t * (float(ys[i]) - float(ys[i - 1]))
    return float(ys[-1])


def sample_velocity(ladder: dict | None, x: float) -> int:
    q = ladder.get("quantiles") if ladder else None
    if not q:
        return 100
    return int(max(1, min(127, round(interp(x * 100.0, QUANTS, q)))))


def drum_velocity(profiles: dict | None, cls: str, pos: int, tag: str) -> int:
    if profiles:
        lad = profiles["profiles"]["drums"].get(cls, {}).get(str(pos))
        return sample_velocity(lad, u(tag))
    if cls == "kick":
        return ACCENTS["kick_downbeat"] if pos == 0 else ACCENTS["kick"]
    if cls == "snare":
        return ACCENTS["snare_backbeat"] if pos in BACKBEAT else ACCENTS["snare_ghost"]
    return ACCENTS["hat_on"] if pos % 2 == 0 else ACCENTS["hat_off"]


def drum_hits(groove_bars: list, arrangement_bars: list, profiles: dict | None, tag: str) -> list:
    """[{slot, pitch, cls, velocity}] over the SONG's bars (groove_bars already flattened to song order)."""
    hits = []
    for b, (g0, a) in enumerate(zip(groove_bars, arrangement_bars)):
        if "drums" in a["mute"]:
            continue
        g = dict(g0)
        if a.get("fill"):
            g["snare"], g["hat"] = int(a["fill"]["snare"]), int(a["fill"]["hat"])
        if a.get("hold"):
            hits.append({"slot": b * 16, "pitch": KICK, "cls": "kick", "velocity": drum_velocity(profiles, "kick", 0, f"{tag}|drums|{b}|kick|0")})
            continue
        for j in bits(g["kick"], 8):
            hits.append({"slot": b * 16 + 2 * j, "pitch": KICK, "cls": "kick", "velocity": drum_velocity(profiles, "kick", 2 * j, f"{tag}|drums|{b}|kick|{2 * j}")})
        for p in bits(g["snare"]):
            v = drum_velocity(profiles, "snare", p, f"{tag}|drums|{b}|snare|{p}")
            if a.get("fill") and not profiles:
                v = ACCENTS["fill_snare"]
            hits.append({"slot": b * 16 + p, "pitch": SNARE, "cls": "snare", "velocity": v})
        for p in bits(g["hat"]):
            hits.append({"slot": b * 16 + p, "pitch": HAT, "cls": "hat", "velocity": drum_velocity(profiles, "hat", p, f"{tag}|drums|{b}|hat|{p}")})
    return sorted(hits, key=lambda h: (h["slot"], h["pitch"]))
