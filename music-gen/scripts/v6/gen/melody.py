#!/usr/bin/python3
"""v6 Phase 2 — melody grammar: VOMM rhythm -> chord-tone skeleton with contour control -> non-chord-tone fill -> cadence endings.

created: 2026-10-04
milestone: M-V6-GEN-2/theory-grounded-composer

Per phrase (L = n_bars * 16 slots, cadence slot = start of the phrase's final chord, always <= L - 8):
 1. RHYTHM: an IOI walk sampled from the melody VOMM (scripts.v5.melody_vomm_v5.sample_next, tokens '<deg>|<ioi>'; only the
    ioi is used here), onsets forced at slot 0, every chord-change slot and the cadence slot; weak onsets are dropped with
    probability 1 - density (section A density 1.0, others DENSITY[label]); onsets over 'N' chords are dropped.
 2. SKELETON on strong beats (beats 1 and 3, every chord change, the cadence): pitch class from the VOMM's degree
    distribution (longest matching context) RESTRICTED to the chord tones; octave placement inside [floor, floor + 12]
    (floor drawn in 67..72, so the phrase range is <= 12 by construction) with contour control: one peak whose slot lies
    in the 2nd-3rd quarter of the phrase, ascending preference before it, descending after; a leap > 5 must be followed by
    a step in the opposite direction. Reject-and-resample with REJECT_TRIES deterministic retries (tag suffix), keeping the
    attempt with the fewest violations.
 3. NON-CHORD-TONE grammar on weak onsets: passing (between skeleton notes a 3rd apart), neighbour (step away and back),
    suspension (previous pitch held over the bar line, resolving down by step on beat 2), anticipation (next chord's
    skeleton tone on the last 8th before the change), escape (rare), else a chord tone; weights in P_NCT.
 4. CADENCE note: authentic -> degree 1 (3 / 5 with lower weight), half -> 2 / 5 / 7, plagal -> 1 / 3, deceptive -> 6 / 1 / 3,
    held >= a half note (to the phrase end minus an 8th of breathing room when the cadence slot allows).
 5. Durations: legato (0.9 x inter-onset interval), last note long. Every note carries a `role` so the validators can
    exclude flagged suspensions/anticipations from the strong-beat chord-tone check.
"""
from __future__ import annotations

from scripts.v5.melody_vomm_v5 import IOI_BUCKETS, ctx_key, ioi_bucket, sample_next  # READ-ONLY pure helpers
from scripts.v6.gen.common import SLOTS, degree_of, draw_from, is_step, scale_for, state_pcs, u

REGISTER = (67, 84)
FLOOR_RANGE = (67, 72)
PHRASE_RANGE = 12
MAX_LEAP = 5
REJECT_TRIES = 8
LEGATO = 0.9
DENSITY = {"A": 1.0, "B": 0.8, "C": 0.7}
P_NCT = {"passing": 0.5, "neighbour": 0.3, "anticipation": 0.3, "suspension": 0.25, "escape": 0.05, "chord_tone": 0.35}
CADENCE_DEGREES = {"authentic": {0: 0.6, 2: 0.25, 4: 0.15}, "half": {1: 0.4, 4: 0.4, 6: 0.2}, "plagal": {0: 0.65, 2: 0.35},
                   "deceptive": {5: 0.3, 0: 0.4, 2: 0.3}, "none": {0: 0.5, 2: 0.3, 4: 0.2}}


def token(pitch: int, ioi16: int, tonic: int, mode: str) -> str:
    d = degree_of(pitch, tonic, mode)
    return f"{'c' if d is None else d}|{ioi_bucket(int(ioi16) * 120)}"


def degree_weights(model: dict, ctx: tuple) -> dict:
    """VOMM next-token distribution (longest matching context) marginalised over the degree ('c' dropped)."""
    counts = model["counts"]
    max_order = int(model.get("max_order", 3))
    ctx = tuple(ctx)[-max_order:]
    for o in range(min(max_order, len(ctx)), -1, -1):
        row = counts.get(str(o), {}).get(ctx_key(ctx[len(ctx) - o:]) if o else "")
        if row:
            w: dict = {}
            for t, c in row.items():
                d = t.split("|")[0]
                if d != "c":
                    w[int(d)] = w.get(int(d), 0) + c
            if w:
                return w
    return {d: 1.0 for d in range(7)}


def phrase_rhythm(model: dict, L: int, change_slots: list, cad_slot: int, density: float, tag: str) -> list:
    pos, ctx, out, k = 0, (), [], 0
    while pos < cad_slot:
        tok = sample_next(model, ctx, u(f"{tag}|rhythm|{k}"))
        ioi = max(1, int(tok.split("|")[1]))
        out.append(pos)
        ctx = (ctx + (tok,))[-3:]
        pos += ioi
        k += 1
    forced = {0, cad_slot} | {c for c in change_slots if c < cad_slot}
    kept = []
    for p in sorted(set(out) | forced):
        if p in forced or p % 8 == 0 or u(f"{tag}|density|{p}") < density:
            kept.append(p)
    return kept


def contour_violations(pitches: list, slots: list, L: int) -> dict:
    """Counts: single_peak (argmax not unique or outside [L/4, 3L/4)), leaps_unresolved, range, direction (dips before / rises after the peak)."""
    out = {"single_peak": 0, "leaps_unresolved": 0, "range": 0, "direction": 0}
    if not pitches:
        return out
    top = max(pitches)
    peaks = [i for i, p in enumerate(pitches) if p == top]
    if len(peaks) != 1 or not (L // 4 <= slots[peaks[0]] < (3 * L) // 4):
        out["single_peak"] = 1
    pk = peaks[0]
    for i in range(1, len(pitches)):
        d = pitches[i] - pitches[i - 1]
        if i <= pk and d < -2:
            out["direction"] += 1
        if i > pk and d > 2:
            out["direction"] += 1
    out["leaps_unresolved"] = unresolved_leaps(pitches)
    out["range"] = 1 if top - min(pitches) > PHRASE_RANGE else 0
    return out


def unresolved_leaps(pitches: list) -> int:
    """A leap > MAX_LEAP must be followed (ignoring repeated pitches) by a step in the opposite direction."""
    n = 0
    seq = [p for i, p in enumerate(pitches) if i == 0 or p != pitches[i - 1]]
    for i in range(1, len(seq) - 1):
        d = seq[i] - seq[i - 1]
        if abs(d) > MAX_LEAP:
            nd = seq[i + 1] - seq[i]
            if not (is_step(seq[i + 1], seq[i]) and nd * d < 0):
                n += 1
    return n


def _place(pc: int, prev, floor: int, phase: str, after_leap: int, peak_pitch: int) -> int:
    """Octave placement inside [floor, floor+12]; every non-peak note stays strictly below the pre-drawn peak pitch."""
    hi = floor + PHRASE_RANGE if phase == "peak" else peak_pitch - 1
    cands = [p for p in range(floor, hi + 1) if p % 12 == pc % 12]
    if not cands:
        cands = [p for p in range(floor, floor + PHRASE_RANGE + 1) if p % 12 == pc % 12]
    if phase == "peak":
        return cands[-1]
    if prev is None:
        return min(cands, key=lambda p: (abs(p - (floor + 5)), p))
    if after_leap:  # a step in the opposite direction when the pc allows it
        steps = [p for p in cands if is_step(p, prev) and (p - prev) * after_leap < 0]
        if steps:
            return steps[0]
    if phase == "up":
        ups = [p for p in cands if p >= prev]
        return ups[0] if ups else cands[-1]
    downs = [p for p in cands if p <= prev]
    return downs[-1] if downs else cands[0]


def _peak_pitch(model: dict, st: str, tonic: int, mode: str, floor: int, tag: str) -> int:
    """Pre-draw the phrase peak: a chord tone whose highest placement in the window is >= floor + 6 (else the highest available)."""
    sc = scale_for(mode)
    pcs = state_pcs(st, tonic) or [(tonic + x) % 12 for x in sc[::2]]
    tops = {pc: max(p for p in range(floor, floor + PHRASE_RANGE + 1) if p % 12 == pc) for pc in pcs}
    high = {pc: t for pc, t in tops.items() if t >= floor + 6} or {max(tops, key=lambda pc: (tops[pc], -pc)): max(tops.values())}
    dw = degree_weights(model, ())
    w = {f"{pc:02d}": float(dw.get(degree_of(pc, tonic, mode), 0.0)) + 0.05 for pc in high}
    return tops[int(draw_from(w, f"{tag}|peakpc"))]


def skeleton(model: dict, positions: list, chords: list, cadence: str, tonic: int, mode: str, L: int, tag: str, prev_pitch) -> dict:
    """positions/chords: parallel lists (slot, state) of the skeleton; the last position is the cadence note."""
    sc = scale_for(mode)
    best = None
    for t in range(REJECT_TRIES):
        tt = f"{tag}|skel|try{t}"
        floor = FLOOR_RANGE[0] + int(u(f"{tt}|floor") * (FLOOR_RANGE[1] - FLOOR_RANGE[0] + 1))
        window = [i for i, s in enumerate(positions) if L // 4 <= s < (3 * L) // 4 and i != len(positions) - 1]
        peak_i = window[int(u(f"{tt}|peak") * len(window))] if window else max(0, (len(positions) - 1) // 2)
        peak_pitch = _peak_pitch(model, chords[peak_i], tonic, mode, floor, tt)
        pitches, ctx, prev, last_leap = [], (), prev_pitch, 0
        for i, (slot, st) in enumerate(zip(positions, chords)):
            pcs = state_pcs(st, tonic) or [(tonic + x) % 12 for x in sc[::2]]
            if i == len(positions) - 1:
                table = CADENCE_DEGREES.get(cadence, CADENCE_DEGREES["none"])
                w = {pc: table.get(degree_of(pc, tonic, mode), 0.05) for pc in pcs}
            else:
                dw = degree_weights(model, ctx)
                w = {pc: float(dw.get(degree_of(pc, tonic, mode), 0.0)) + 0.05 for pc in pcs}
            phase = "peak" if i == peak_i else ("up" if i < peak_i else "down")
            if phase == "peak":
                p = peak_pitch
            else:
                pc = int(draw_from({f"{k:02d}": v for k, v in w.items()}, f"{tt}|pc|{i}"))
                p = _place(pc, prev if (prev is not None and floor <= prev <= floor + PHRASE_RANGE) else None, floor, phase, last_leap, peak_pitch)
            if prev is not None:
                last_leap = (p - prev) if abs(p - prev) > MAX_LEAP else 0
            nxt = positions[i + 1] if i + 1 < len(positions) else L
            ctx = (ctx + (token(p, nxt - slot, tonic, mode),))[-3:]
            pitches.append(p)
            prev = p
        viol = contour_violations(pitches, positions, L)
        score = sum(viol.values())
        if best is None or score < best["score"]:
            best = {"pitches": pitches, "floor": floor, "peak_index": peak_i, "violations": viol, "score": score, "tries": t + 1}
        if score == 0:
            break
    return best


def _passing(a: int, b: int, tonic: int, mode: str):
    lo, hi = min(a, b), max(a, b)
    mids = [p for p in range(lo + 1, hi) if degree_of(p, tonic, mode) is not None]
    return mids[len(mids) // 2] if mids else None


def fill_weak(onsets: list, skel: dict, skel_pos: list, chords_at, change_set: set, floor: int, tonic: int, mode: str, tag: str) -> list:
    """Assign pitches/roles to every onset. Returns [(slot, pitch, role)]."""
    sk = dict(zip(skel_pos, skel["pitches"]))
    notes = []
    prev_pitch = None
    for idx, s in enumerate(onsets):
        if s in sk:
            role = "cadence" if s == skel_pos[-1] else "skeleton"
            p = sk[s]
            # suspension: bar line + chord change, previous pitch a step above this chord tone and not a chord tone
            nxt_on = onsets[idx + 1] if idx + 1 < len(onsets) else None
            pcs = state_pcs(chords_at(s), tonic) or []
            if (role == "skeleton" and s % SLOTS == 0 and s in change_set and prev_pitch is not None and 1 <= prev_pitch - p <= 2
                    and prev_pitch % 12 not in pcs and floor <= prev_pitch <= floor + PHRASE_RANGE and (nxt_on is None or nxt_on > s + 4)
                    and u(f"{tag}|nct|{s}|susp") < P_NCT["suspension"]):
                notes.append((s, prev_pitch, "suspension"))
                notes.append((s + 4, p, "resolution"))
            else:
                notes.append((s, p, role))
            prev_pitch = p
            continue
        # weak onset: next skeleton pitch and the remaining weak onsets before it
        nxt_sk = next((q for q in skel_pos if q > s), None)
        S1 = sk[nxt_sk] if nxt_sk is not None else prev_pitch
        S0 = prev_pitch if prev_pitch is not None else S1
        gap = S1 - S0
        remaining = [q for q in onsets if s < q < (nxt_sk if nxt_sk is not None else 10 ** 9)]
        opts = {"chord_tone": P_NCT["chord_tone"]}
        if not remaining and 3 <= abs(gap) <= 4 and _passing(S0, S1, tonic, mode) is not None:
            opts["passing"] = P_NCT["passing"]
        if abs(gap) <= 3:
            opts["neighbour"] = P_NCT["neighbour"]
            if not remaining:
                opts["escape"] = P_NCT["escape"]
        if not remaining and nxt_sk is not None and nxt_sk in change_set and s == nxt_sk - 2 and abs(gap) <= MAX_LEAP:
            opts["anticipation"] = P_NCT["anticipation"]
        choice = draw_from(opts, f"{tag}|nct|{s}")
        if choice == "passing":
            p = _passing(S0, S1, tonic, mode)
        elif choice == "neighbour":
            up = u(f"{tag}|nct|{s}|dir") < 0.5
            cand = [q for q in (S0 + 2, S0 + 1) if floor <= q <= floor + PHRASE_RANGE and degree_of(q, tonic, mode) is not None] if up else \
                   [q for q in (S0 - 2, S0 - 1) if floor <= q <= floor + PHRASE_RANGE and degree_of(q, tonic, mode) is not None]
            p = cand[0] if cand else S0
            choice = "neighbour" if cand else "chord_tone"
        elif choice == "escape":
            away = -1 if gap >= 0 else 1
            cand = [q for q in (S0 + 2 * away, S0 + away) if floor <= q <= floor + PHRASE_RANGE and degree_of(q, tonic, mode) is not None]
            p = cand[0] if cand else S0
            choice = "escape" if cand else "chord_tone"
        elif choice == "anticipation":
            p = S1
        else:
            pcs = state_pcs(chords_at(s), tonic) or [S0 % 12]
            if u(f"{tag}|nct|{s}|ct") < 0.5 or S0 % 12 not in pcs:
                cands = [q for q in range(floor, floor + PHRASE_RANGE + 1) if q % 12 in pcs and abs(q - S0) <= 4]
                p = min(cands, key=lambda q: (abs(q - S0), q)) if cands else S0
            else:
                p = S0
        notes.append((s, int(p), choice))
        prev_pitch = int(p)
    return notes


def phrase_melody(models: dict, beat_chords: list, phrase: dict, harmony_phrase: dict, tonic: int, mode: str, label: str, tag: str, prev_pitch) -> dict:
    """One phrase. beat_chords = the LABEL's per-bar per-beat chords; phrase = planner entry (start_bar, n_bars, cadence)."""
    model = models["melody"]
    b0, nb = phrase["start_bar"], phrase["n_bars"]
    L = nb * SLOTS
    slots_h = [(r["bar"] - b0) * SLOTS + r["beat"] * 4 for r in harmony_phrase["slots"]]
    change = sorted({s for i, s in enumerate(slots_h) if i == 0 or harmony_phrase["chords"][i] != harmony_phrase["chords"][i - 1]})
    cad_slot = slots_h[-1]
    cadence = harmony_phrase["cadence_realized"] if harmony_phrase["cadence_realized"] != "none" else harmony_phrase["cadence_planned"]

    def chord_at(s: int) -> str:
        return beat_chords[b0 + s // SLOTS][(s % SLOTS) // 4]

    onsets = [s for s in phrase_rhythm(model, L, change, cad_slot, DENSITY.get(label, 0.75), tag) if chord_at(s) != "N"]
    if not onsets:
        return {"notes": [], "skeleton": None, "onsets": [], "cadence_used": cadence, "L": L, "cad_slot": cad_slot}
    skel_pos = sorted({s for s in onsets if s % 8 == 0 or s in change} | {cad_slot, onsets[0]})
    sk = skeleton(model, skel_pos, [chord_at(s) for s in skel_pos], cadence, tonic, mode, L, tag, prev_pitch)
    raw = fill_weak(onsets, sk, skel_pos, chord_at, set(change), sk["floor"], tonic, mode, tag)
    raw.sort()
    notes = []
    for i, (s, p, role) in enumerate(raw):
        if role == "cadence":
            dur = min(L - s, max(8, L - s - 2))
        else:
            nxt = raw[i + 1][0] if i + 1 < len(raw) else L
            dur = max(1.0, (nxt - s) * LEGATO)
        notes.append({"slot": int(s), "pitch": int(p), "dur16": round(float(dur), 4), "role": role, "chord": chord_at(s), "phrase": phrase["index"]})
    peak = max(range(len(notes)), key=lambda i: (notes[i]["pitch"], -i))
    for i, n in enumerate(notes):
        n["position"] = "first" if i == 0 else ("last" if i == len(notes) - 1 else ("peak" if i == peak else "other"))
    return {"notes": notes, "skeleton": {"slots": skel_pos, "pitches": sk["pitches"], "floor": sk["floor"], "violations": sk["violations"], "tries": sk["tries"]},
            "onsets": onsets, "change_slots": change, "cadence_used": cadence, "L": L, "cad_slot": cad_slot}


def label_melody(models: dict, label_plan: dict, harmony: dict, tonic: int, mode: str, label: str, tag: str) -> dict:
    """All phrases of a label; notes carry slots relative to the section start."""
    notes, phrases, prev = [], [], None
    for ph, hp in zip(label_plan["phrases"], harmony["phrases"]):
        r = phrase_melody(models, harmony["beat_chords"], ph, hp, tonic, mode, label, f"{tag}|melody|{ph['index']}", prev)
        off = ph["start_bar"] * SLOTS
        for n in r["notes"]:
            n2 = dict(n)
            n2["slot"] += off
            notes.append(n2)
        if r["notes"]:
            prev = r["notes"][-1]["pitch"]
        phrases.append({k: v for k, v in r.items() if k != "notes"})
    return {"notes": notes, "phrases": phrases}
