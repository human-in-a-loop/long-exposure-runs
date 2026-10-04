#!/usr/bin/python3
"""v6 Phase 2 — voicing: four-voice keys realisation by dynamic programming over the chord slots + comping rhythm.

created: 2026-10-04
milestone: M-V6-GEN-2/theory-grounded-composer

Candidates per chord: every strictly ascending 4-note set in KEYS_LO..KEYS_HI (MIDI 52..79) whose pitch classes cover the
chord (triads/sus: one pc doubled; 7th chords: the four pcs once; 9 chords: root, 3rd, 7th, 9th — the 5th is dropped),
adjacent gaps <= MAX_GAP and total span <= MAX_SPAN. The bass is a separate part (bassline.py), so the keys voicing is the
3-4 voices above it. DP (Viterbi) over the sequence minimises
  sum |voice movement| (semitones)
  + HARD (1e3) per parallel perfect 5th/8ve between any voice pair (both voices move, same direction, same perfect interval
    class) and per voice against the bass root line
  + HARD per chord 7th not resolving down by step (held as a common tone is allowed; chord unchanged is exempt)
  + HARD for a leading tone (degree 7, major) at a CADENCE transition not resolving to the tonic (at an AUTHENTIC cadence the
    leading tone must move to the tonic pc or be absent: holding it is not accepted either)
  + HARD per voice crossing/overlap (a voice moving past a neighbour's previous pitch)
  + 2 per adjacent gap > 12 semitones, + 1 for a doubled 3rd, + 2 when a common tone exists but none is kept.
Phase 5: the four rule costs are HARD = 1e3 (movement costs are tens), so the DP accepts a violation only when no
violation-free path exists; every slot records `forced` (the rules violated on the chosen path) and `forced_reason`.
Every rule is also a validator (validators.py re-counts them on the realised output). Comping rhythm per bar: onset
pattern from comping_v5.json's pooled IOI histogram when present, else a template set (whole / half / Charleston /
8th pushes / quarters) chosen by SHA; onsets are forced at chord-change slots; sustain to the next onset minus a gap.
"""
from __future__ import annotations

from itertools import combinations

from scripts.v6.gen.common import SLOTS, draw_from, draw_index, state_pcs, state_root

KEYS_LO, KEYS_HI = 52, 79
N_VOICES = 4
MAX_GAP, MAX_SPAN = 16, 24
HARD = 1000.0  # effectively hard rules: tens of semitones of movement never buy a violation; see voice_sequence's `forced`
COST = {"parallel": HARD, "seventh": HARD, "leading_tone": HARD, "crossing": HARD, "spacing": 2.0, "doubled_third": 1.0, "common_tone": 2.0}
HARD_RULES = ("parallels", "seventh", "leading_tone", "crossing")
FORCED_REASON = "no violation-free path through this chord: the DP minimum (hard cost 1e3 per violation) still violates the listed rules"

TEMPLATES = {"whole": [0], "half": [0, 8], "charleston": [0, 6], "eighth_push": [0, 6, 8, 14], "quarters": [0, 4, 8, 12]}
TEMPLATE_W = {"whole": 0.25, "half": 0.25, "charleston": 0.2, "eighth_push": 0.15, "quarters": 0.15}
GAP_S = 0.02


def chord_tones(state: str, tonic: int) -> dict:
    """{'pcs': required pcs (ordered root, 3rd, 5th, 7th/9th), 'third': pc of the 3rd or None, 'seventh': pc or None, 'root': pc}."""
    pcs = state_pcs(state, tonic)
    if not pcs:
        return {"pcs": [], "third": None, "seventh": None, "root": None}
    q = state.split(":")[1]
    root = pcs[0]
    third = pcs[1] if q in ("maj", "min", "7", "min7", "maj7") else (pcs[2] if q == "9" else None)
    seventh = pcs[3] if q in ("7", "min7", "maj7") else (pcs[4] if q == "9" else None)
    req = [root, pcs[2], pcs[4], pcs[1]] if q == "9" else list(pcs)  # 9 chord: root, 3rd, 7th, 9th (5th dropped)
    return {"pcs": req, "third": third, "seventh": seventh, "root": root}


def candidates(state: str, tonic: int) -> list:
    ct = chord_tones(state, tonic)
    req = ct["pcs"]
    if not req:
        return []
    pool = [p for p in range(KEYS_LO, KEYS_HI + 1) if p % 12 in set(req)]
    out = []
    for combo in combinations(pool, N_VOICES):
        got = {p % 12 for p in combo}
        if got != set(req) or combo[-1] - combo[0] > MAX_SPAN:
            continue
        if any(combo[i + 1] - combo[i] > MAX_GAP for i in range(N_VOICES - 1)):
            continue
        out.append(tuple(combo))
    return out


def unary_cost(v: tuple, ct: dict) -> dict:
    spacing = sum(1 for i in range(len(v) - 1) if v[i + 1] - v[i] > 12)
    pcs = [p % 12 for p in v]
    doubled_third = 1 if ct["third"] is not None and pcs.count(ct["third"]) > 1 else 0
    return {"spacing": spacing * COST["spacing"], "doubled_third": doubled_third * COST["doubled_third"]}


def parallel_perfects(a: tuple, b: tuple, bass_a=None, bass_b=None) -> int:
    """Parallel perfect 5ths/8ves between voicings a -> b (same voice count, sorted), plus each voice against the bass root
    motion bass_a -> bass_b when given."""
    n = 0
    if bass_a is not None and bass_b is not None and bass_a != bass_b:
        for i in range(len(a)):
            ia, ib = (a[i] - bass_a) % 12, (b[i] - bass_b) % 12
            if ia == ib and ia in (0, 7) and (b[i] - a[i]) != 0 and (b[i] - a[i]) * (bass_b - bass_a) > 0:
                n += 1
    for i in range(len(a)):
        for j in range(i + 1, len(a)):
            ia, ib = (a[j] - a[i]) % 12, (b[j] - b[i]) % 12
            if ia == ib and ia in (0, 7) and (b[i] - a[i]) != 0 and (b[j] - a[j]) != 0 and (b[i] - a[i]) * (b[j] - a[j]) > 0:
                n += 1
    return n


def crossings(a: tuple, b: tuple) -> int:
    n = 0
    for i in range(len(a)):
        if i > 0 and b[i] < a[i - 1]:
            n += 1
        if i < len(a) - 1 and b[i] > a[i + 1]:
            n += 1
    return n


def unresolved_sevenths(a: tuple, b: tuple, ct_a: dict, same_chord: bool) -> int:
    if ct_a["seventh"] is None or same_chord:
        return 0
    n = 0
    for i, p in enumerate(a):
        if p % 12 == ct_a["seventh"]:
            d = b[i] - p
            if not (d == 0 or -2 <= d <= -1):
                n += 1
    return n


def unresolved_leading_tone(a: tuple, b: tuple, tonic: int, mode: str, cadence) -> int:
    """cadence: falsy (not a cadence), True, or the cadence type; at "authentic" the leading tone must reach the tonic pc (holding
    it, e.g. into Imaj7, is not a resolution); at any other cadence holding is accepted (= validators' rule)."""
    if not cadence or str(mode).lower() != "major":
        return 0
    lt, tonic_pc = (tonic + 11) % 12, tonic % 12
    strict = cadence == "authentic"
    return sum(1 for i, p in enumerate(a) if p % 12 == lt and b[i] % 12 != tonic_pc and (strict or b[i] != p))


def transition_cost(a: tuple, b: tuple, ct_a: dict, ct_b: dict, tonic: int, mode: str, cadence, same_chord: bool, bass_a=None, bass_b=None) -> dict:
    move = sum(abs(x - y) for x, y in zip(a, b))
    common = bool(set(ct_a["pcs"]) & set(ct_b["pcs"])) and not any(x == y for x, y in zip(a, b)) and not same_chord
    return {"movement": float(move), "parallels": parallel_perfects(a, b, bass_a, bass_b) * COST["parallel"],
            "seventh": unresolved_sevenths(a, b, ct_a, same_chord) * COST["seventh"],
            "leading_tone": unresolved_leading_tone(a, b, tonic, mode, cadence) * COST["leading_tone"],
            "crossing": crossings(a, b) * COST["crossing"], "common_tone": COST["common_tone"] if common else 0.0}


def voice_sequence(states: list, tonic: int, mode: str, cadence_flags: list, bass: list | None = None, entry_contexts: list | None = None,
                   exit_contexts: list | None = None, first_voicing: tuple | None = None) -> list:
    """DP over chord states (None/'N' -> rest). cadence_flags[t] marks the transition t-1 -> t as a cadence arrival (True or the
    cadence type string: "authentic" makes the leading-tone rule strict, see unresolved_leading_tone); bass[t]
    is the bass root pitch that will sound at slot t (bassline.root_line) so parallels against it are costed too.
    entry_contexts = [{'state','voicing','bass'}] of the chords that precede this sequence in the song (the final chord of every
    section that leads into this label): their transition cost into the first voicing is added (second pass over the form,
    so section junctions obey the same rules while every label still repeats literally); exit_contexts = the same for the chords that
    FOLLOW this sequence (the first chord of every section this label leads into): their transition cost out of the last voicing is
    added to that slot (compose_v6 iterates the junction pass to a fixed point). first_voicing pins the first chord's voicing
    (voice_sequence_cyclic: a label that follows itself).
    Returns per slot {'state','voicing','cost','forced'} with the cost breakdown (unary + transition into this slot); `forced` lists
    the HARD_RULES the chosen (globally minimal) path still violates entering this slot, `forced_reason` says why."""
    T = len(states)
    bass = bass or [None] * T
    entry_contexts, exit_contexts = entry_contexts or [], exit_contexts or []
    cands = [candidates(s, tonic) if s and s != "N" else [] for s in states]
    cts = [chord_tones(s, tonic) if s and s != "N" else None for s in states]
    last_idx = max((t for t in range(T) if cands[t]), default=None)
    if first_voicing is not None and last_idx is not None:
        first_idx = min(t for t in range(T) if cands[t])
        cands[first_idx] = [tuple(first_voicing)] if tuple(first_voicing) in cands[first_idx] else cands[first_idx]
    best = [dict() for _ in range(T)]  # slot -> {voicing: (total, prev_voicing, breakdown)}
    prev_idx = None
    for t in range(T):
        if not cands[t]:
            continue
        for v in cands[t]:
            un = unary_cost(v, cts[t])
            if t == last_idx:
                for ctx in exit_contexts:  # junction costs into the successor sections' first chords
                    tc = transition_cost(v, tuple(ctx["voicing"]), cts[t], chord_tones(ctx["state"], tonic), tonic, mode, False, ctx["state"] == states[t], bass[t], ctx.get("bass"))
                    for k, x in tc.items():
                        un[k] = un.get(k, 0.0) + x / len(exit_contexts)
            if prev_idx is None or not best[prev_idx]:
                br = dict(un)
                for k in ("movement", "parallels", "seventh", "leading_tone", "crossing", "common_tone"):
                    br.setdefault(k, 0.0)
                for ctx in entry_contexts:  # junction costs from the predecessor sections' final chords
                    tc = transition_cost(tuple(ctx["voicing"]), v, chord_tones(ctx["state"], tonic), cts[t], tonic, mode, False, ctx["state"] == states[t], ctx.get("bass"), bass[t])
                    for k, x in tc.items():
                        br[k] = br.get(k, 0.0) + x / len(entry_contexts)
                best[t][v] = (sum(br.values()), None, br)
                continue
            same = states[prev_idx] == states[t]
            opt = None
            for pv, (ptot, _pp, _pb) in best[prev_idx].items():
                tc = transition_cost(pv, v, cts[prev_idx], cts[t], tonic, mode, cadence_flags[t] or False, same, bass[prev_idx], bass[t])
                tot = ptot + sum(un.values()) + sum(tc.values())
                if opt is None or tot < opt[0] or (tot == opt[0] and pv < opt[1]):
                    br = dict(un)
                    for k, x in tc.items():  # exit-context costs already sit in `un` at the last slot: add, never overwrite
                        br[k] = br.get(k, 0.0) + x
                    opt = (tot, pv, br)
            best[t][v] = opt
        prev_idx = t
    # backtrack from the last non-rest slot along the argmin pointers (pv is None at the chain start)
    out = [{"state": s, "voicing": None, "cost": None, "forced": []} for s in states]
    t = prev_idx
    cur = min(best[t], key=lambda v: (best[t][v][0], v)) if t is not None and best[t] else None
    while t is not None and t >= 0 and cur is not None:
        tot, pv, br = best[t][cur]
        br = {k: round(float(x), 6) for k, x in sorted(br.items())}
        br["total_step"] = round(sum(br.values()), 6)
        forced = [k for k in HARD_RULES if br.get(k, 0.0) > 0.0]
        out[t] = {"state": states[t], "voicing": list(cur), "cost": br, "forced": forced}
        if forced:
            out[t]["forced_reason"] = FORCED_REASON
        cur = pv
        t -= 1
        while t >= 0 and not best[t]:
            t -= 1
    return out


def hard_violations(a: tuple, b: tuple, state_a: str, state_b: str, tonic: int, mode: str, bass_a=None, bass_b=None) -> int:
    tc = transition_cost(tuple(a), tuple(b), chord_tones(state_a, tonic), chord_tones(state_b, tonic), tonic, mode, False, state_a == state_b, bass_a, bass_b)
    return sum(1 for k in HARD_RULES if tc[k] > 0)


def voice_sequence_cyclic(states: list, tonic: int, mode: str, cadence_flags: list, bass: list, entry_contexts: list, exit_contexts: list,
                          self_adjacent: bool, top_k: int = 4) -> tuple[list, dict]:
    """voice_sequence for a label that may FOLLOW ITSELF in the form (A A ...): the junction last -> first lies inside one DP, so a
    stale context oscillates. Lazy exact treatment: run the free DP; if last -> first has a hard violation, re-run with the first
    voicing pinned and used as its own exit context, for the current first voicing then the top_k alternatives (ranked by entry-context
    + unary cost), keeping the cheapest run (a hard-free self-junction stops the search). Returns (voicings, info)."""
    out = voice_sequence(states, tonic, mode, cadence_flags, bass, entry_contexts, exit_contexts)
    info = {"self_adjacent": self_adjacent, "runs": 1, "pinned_first": None, "self_junction_hard": 0}
    idx = [t for t, v in enumerate(out) if v["voicing"]]
    if not self_adjacent or len(idx) < 2:
        return out, info
    f, l = idx[0], idx[-1]
    hv = hard_violations(out[l]["voicing"], out[f]["voicing"], states[l], states[f], tonic, mode, bass[l], bass[f])
    if hv == 0:
        return out, info
    ct_f = chord_tones(states[f], tonic)

    def entry_cost(v: tuple) -> float:
        c = sum(unary_cost(v, ct_f).values())
        for ctx in entry_contexts:
            c += sum(transition_cost(tuple(ctx["voicing"]), v, chord_tones(ctx["state"], tonic), ct_f, tonic, mode, False, ctx["state"] == states[f], ctx.get("bass"), bass[f]).values()) / max(1, len(entry_contexts))
        return c
    ranked = sorted(candidates(states[f], tonic), key=lambda v: (entry_cost(v), v))
    tries = [tuple(out[f]["voicing"])] + [v for v in ranked if v != tuple(out[f]["voicing"])][:top_k]
    best = None
    for v0 in tries:
        self_ctx = {"state": states[f], "voicing": list(v0), "bass": bass[f]}
        o = voice_sequence(states, tonic, mode, cadence_flags, bass, entry_contexts, exit_contexts + [self_ctx], v0)
        info["runs"] += 1
        tot = sum(x["cost"]["total_step"] for x in o if x["cost"])
        h = hard_violations(o[l]["voicing"], o[f]["voicing"], states[l], states[f], tonic, mode, bass[l], bass[f])
        if best is None or tot < best[0]:
            best = (tot, o, v0, h)
        if h == 0:
            break
    info.update({"pinned_first": list(best[2]), "self_junction_hard": best[3]})
    return best[1], info


def comping_onsets(bar_hr: int, change_pos: list, tag: str, comping: dict | None) -> list:
    """16th positions of the keys onsets in one bar: a template (or IOI walk from comping_v5.json) merged with the chord-change slots."""
    if comping and comping.get("stats", {}).get("pooled", {}).get("ioi16_histogram"):
        hist = comping["stats"]["pooled"]["ioi16_histogram"]
        pos, out = 0, []
        while pos < SLOTS:
            out.append(pos)
            pos += draw_index(hist, f"{tag}|ioi|{pos}") + 1
        name = "comping_v5_ioi_walk"
    else:
        name = draw_from(TEMPLATE_W, f"{tag}|template")
        out = list(TEMPLATES[name])
    return sorted(set(out) | set(change_pos)), name


def keys_events(beat_chords: list, voicings_by_slot: dict, bpm: float, tag: str, comping: dict | None, velocity_fn, mute: list) -> tuple[list, list]:
    """Keys note list [(slot16, pitch, dur16, bar)] over a label's bars; voicings_by_slot {(bar, beat): voicing}."""
    beat = 60.0 / bpm
    s16 = beat / 4
    notes, rhythm = [], []
    n_bars = len(beat_chords)
    for b in range(n_bars):
        if "keys" in mute[b]:
            continue
        changes = [bt * 4 for bt in range(4) if (b, bt) in voicings_by_slot and (bt > 0 or b == 0 or beat_chords[b][0] != beat_chords[b - 1][3])]
        if b > 0 and beat_chords[b][0] != beat_chords[b - 1][3] and 0 not in changes:
            changes.append(0)
        hr = len([1 for bt in range(4) if (b, bt) in voicings_by_slot])
        onsets, name = comping_onsets(hr, changes, f"{tag}|comp|bar{b}", comping)
        rhythm.append({"bar": b, "template": name, "onsets": onsets})
        for k, pos in enumerate(onsets):
            bt = pos // 4
            v = None
            for bb in range(bt, -1, -1):
                if (b, bb) in voicings_by_slot:
                    v = voicings_by_slot[(b, bb)]
                    break
            if v is None:
                for bb in range(b - 1, -1, -1):
                    for bbt in (3, 2, 1, 0):
                        if (bb, bbt) in voicings_by_slot:
                            v = voicings_by_slot[(bb, bbt)]
                            break
                    if v is not None:
                        break
            if not v or beat_chords[b][bt] == "N":
                continue
            nxt = onsets[k + 1] if k + 1 < len(onsets) else SLOTS
            dur = max(1, nxt - pos)
            for p in v:
                notes.append({"slot": b * SLOTS + pos, "pitch": int(p), "dur16": dur, "bar": b, "velocity": velocity_fn(f"{tag}|keys|vel|bar{b}|pos{pos}", pos)})
    return notes, rhythm
