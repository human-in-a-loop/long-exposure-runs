#!/usr/bin/python3
"""v6 Phase 5 — repair: deterministic counterpoint repair pass over the FINAL bass + melody, evaluated on the flattened song exactly
as validators.py counts (so section junctions, mutes and the held final bar are all seen).

created: 2026-10-04
milestone: M-V6-GEN-5/hardening

Rules repaired (validators' definitions, re-counted here WITH locations): bass-melody parallel perfect 5ths / 8ves / unisons
between consecutive bass onsets (melody note sounding at each), melodic leaps > melody.MAX_LEAP not followed by a step in the
opposite direction (per phrase, repeated pitches collapsed), degree 7 (major) at a phrase's final transition not moving to the
tonic. The phrase range (<= 12) and the strong-beat chord-tone rule are counted too so no repair may break them.
Every candidate is TRIED on the label content, the song re-flattened and all rules re-counted; it is accepted only when the
targeted violation disappears and the total count strictly decreases (termination guaranteed; a violation with no feasible
alternative is recorded as FORCED with the branches tried). Branch priority:
  parallel:     (a) the second, then the first bass onset when FREE (not a forced root on a chord slot): class re-picked among the
                bassline.class_pitch candidates (same tag), chosen by draw_from over the model row's weights under the class tag
                + "|repair"; (b) the melody note sounding at the second, then the first onset when NON-skeleton: nearest allowed
                pitch (chord tones; scale tones too off the strong beats); (c) skeleton notes: another chord tone inside the phrase
                window (contour-preserving first) and the phrase re-realised from the repaired skeleton with melody.fill_weak under
                the original tags, so humanize's recurrences inherit it; (d) forced.
  leap:         the following note (non-skeleton: a step back), the leap note, the preceding note; then skeleton alternatives; forced.
  leading tone: cadence note -> tonic when the final chord holds it (authentic / plagal / deceptive; skeleton re-realisation), else
                the note before (non-skeleton re-pick excluding degree 7, then skeleton alternative); forced.
repair_labels() runs on the per-label content BEFORE humanize.vary_recurrences; repair_sections() runs on the varied recurrences
and touches only non-skeleton melody notes and free bass notes (bass copied on write) so the skeleton stays label-identical.
No PRNG: nearest-pitch order everywhere, SHA draws (common.draw_from) for the bass class.
"""
from __future__ import annotations

import copy

from scripts.v6.gen import bassline as BL
from scripts.v6.gen import melody as MEL
from scripts.v6.gen.common import SLOTS, degree_of, draw_from, is_step, state_pcs

SKELETON_ROLES = ("skeleton", "cadence", "suspension", "resolution")
GUARD_RULES = ("range", "strong_beat_nct")


def _sounding(notes: list, slot: int):
    best = None
    for n in notes:
        if n["slot"] <= slot < n["slot"] + n["dur16"]:
            best = n
        elif n["slot"] > slot:
            break
    return best


def find_violations(song: dict) -> list:
    """Location-aware re-count (validators.parallel_perfect_intervals bass-melody part, melody_checks, leading_tone melody part)."""
    out = []
    bass = sorted(song["bass"], key=lambda n: n["slot"])
    mel = sorted(song["melody"], key=lambda n: n["slot"])
    prev = None
    for n in bass:
        m = _sounding(mel, n["slot"])
        if prev is not None and m is not None and prev[1] is not None and BL.is_parallel_perfect(prev[0]["pitch"], prev[1]["pitch"], n["pitch"], m["pitch"]):
            rule = "parallel_fifth" if (prev[1]["pitch"] - prev[0]["pitch"]) % 12 == 7 else "parallel_octave"
            out.append({"rule": rule, "key": ("par", prev[0]["slot"], n["slot"]), "slot": n["slot"], "bass": [prev[0], n], "melody": [prev[1], m]})
        prev = (n, m)
    change = {c["bar"] * SLOTS + c["beat"] * 4 for c in song["chord_slots"]}
    lt, tonic_pc, major = (song["tonic"] + 11) % 12, song["tonic"] % 12, str(song["mode"]).lower() == "major"
    for ph in song["phrases"]:
        s0, s1 = ph["start_bar"] * SLOTS, (ph["start_bar"] + ph["n_bars"]) * SLOTS
        notes = [n for n in mel if s0 <= n["slot"] < s1]
        if notes:
            pitches = [n["pitch"] for n in notes]
            idx = [i for i, p in enumerate(pitches) if i == 0 or p != pitches[i - 1]]
            seq = [pitches[i] for i in idx]
            for i in range(1, len(seq) - 1):
                d = seq[i] - seq[i - 1]
                if abs(d) > MEL.MAX_LEAP and not (is_step(seq[i + 1], seq[i]) and (seq[i + 1] - seq[i]) * d < 0):
                    out.append({"rule": "leap_unresolved", "key": ("leap", s0, notes[idx[i]]["slot"]), "slot": notes[idx[i]]["slot"],
                                "notes": [notes[idx[i - 1]], notes[idx[i]], notes[idx[i + 1]]], "sign": 1 if d > 0 else -1})
            if max(pitches) - min(pitches) > MEL.PHRASE_RANGE:
                out.append({"rule": "range", "key": ("range", s0), "slot": s0})
        sl = ph["slots"]
        if major and len(sl) >= 2:
            pen, cad = sl[-2]["bar"] * SLOTS + sl[-2]["beat"] * 4, sl[-1]["bar"] * SLOTS + sl[-1]["beat"] * 4
            before = [n for n in mel if pen <= n["slot"] < cad]
            at = [n for n in mel if n["slot"] == cad]
            if before and at and before[-1]["pitch"] % 12 == lt and at[0]["pitch"] % 12 != tonic_pc:
                cadence = ph["cadence_realized"] if ph["cadence_realized"] != "none" else ph["cadence_planned"]
                out.append({"rule": "leading_tone_unresolved", "key": ("lt", s0), "slot": cad, "before": before[-1], "at": at[0], "cadence": cadence, "final_state": sl[-1]["state"]})
    for n in mel:
        if (n["slot"] % 8 == 0 or n["slot"] in change) and n.get("role") not in ("suspension", "anticipation"):
            pcs = state_pcs(song["beat_chords"][n["slot"] // SLOTS][(n["slot"] % SLOTS) // 4], song["tonic"])
            if pcs and n["pitch"] % 12 not in pcs:
                out.append({"rule": "strong_beat_nct", "key": ("nct", n["slot"]), "slot": n["slot"]})
    return sorted(out, key=lambda v: (v["slot"], v["rule"]))


class _Ctx:
    def __init__(self, models, plan, labels, by_section, tonic, mode, flatten_fn, touch_skeleton: bool, varied: set | None):
        self.models, self.plan, self.labels, self.by_section, self.tonic, self.mode = models, plan, labels, by_section, tonic, mode
        self.flatten, self.touch_skeleton, self.varied = flatten_fn, touch_skeleton, varied
        self.sections = {s["index"]: s for s in plan["form"]["sections"]}

    def content(self, sec: int) -> dict:
        return self.by_section[sec] if self.by_section is not None else self.labels[self.sections[sec]["label"]]

    def locate(self, song_note: dict, stem: str):
        """song note -> (content, label-relative note dict, section)."""
        sec = song_note["section"]
        rel = song_note["slot"] - self.sections[sec]["start_bar"] * SLOTS
        c = self.content(sec)
        notes = c["bass"]["notes"] if stem == "bass" else c["melody"]["notes"]
        n = next((x for x in notes if x["slot"] == rel), None)
        return c, n, sec

    def touchable(self, sec: int, kind: str) -> bool:
        if self.varied is not None and sec not in self.varied:
            return False
        return self.touch_skeleton or kind != "skeleton"


def _phrase_of(content: dict, note: dict):
    k = note["phrase"]
    return content["melody"]["phrases"][k], content["plan"]["phrases"][k]


def _chord_at(content: dict, b0: int):
    bc = content["harmony"]["beat_chords"]
    return lambda s: bc[b0 + s // SLOTS][(s % SLOTS) // 4]


def _window(content: dict, k: int, exclude_slot) -> tuple:
    mph = content["melody"]["phrases"][k]
    floor = mph["skeleton"]["floor"]
    ps = [n["pitch"] for n in content["melody"]["notes"] if n["phrase"] == k and n["slot"] != exclude_slot]
    lo = max(floor, max(ps) - MEL.PHRASE_RANGE) if ps else floor
    hi = min(floor + MEL.PHRASE_RANGE, min(ps) + MEL.PHRASE_RANGE) if ps else floor + MEL.PHRASE_RANGE
    return lo, hi


def _refresh_positions(content: dict, k: int) -> None:
    ns = sorted((n for n in content["melody"]["notes"] if n["phrase"] == k), key=lambda n: n["slot"])
    if ns:
        peak = max(range(len(ns)), key=lambda i: (ns[i]["pitch"], -i))
        for i, n in enumerate(ns):
            n["position"] = "first" if i == 0 else ("last" if i == len(ns) - 1 else ("peak" if i == peak else "other"))


def nct_candidates(ctx: _Ctx, content: dict, note: dict, exclude_pcs=(), step_back=None) -> list:
    """Nearest-first pitches for a non-skeleton melody note: chord tones (only those on strong beats / chord changes), scale tones
    elsewhere, inside the phrase window; step_back = (anchor, sign) restricts to a step against `sign` from anchor."""
    mph, ph = _phrase_of(content, note)
    rel = note["slot"] - ph["start_bar"] * SLOTS
    strong = rel % 8 == 0 or rel in mph["change_slots"]
    pcs = state_pcs(note["chord"], ctx.tonic) or []
    lo, hi = _window(content, note["phrase"], note["slot"])
    out = []
    for p in range(lo, hi + 1):
        if p == note["pitch"] or p % 12 in exclude_pcs:
            continue
        if not (p % 12 in pcs or (not strong and degree_of(p, ctx.tonic, ctx.mode) is not None)):
            continue
        if step_back is not None and not (is_step(p, step_back[0]) and (p - step_back[0]) * step_back[1] < 0):
            continue
        out.append(p)
    return sorted(out, key=lambda p: (abs(p - note["pitch"]), 0 if p % 12 in pcs else 1, p))


def skeleton_candidates(ctx: _Ctx, content: dict, k: int, i: int, exclude_pcs=(), only_pcs=None) -> list:
    """Other chord tones for skeleton position i of phrase k inside the window; contour-preserving (below the peak / the peak stays
    the top) first, each group nearest-first."""
    mph = content["melody"]["phrases"][k]
    slots, pitches, floor = mph["skeleton"]["slots"], mph["skeleton"]["pitches"], mph["skeleton"]["floor"]
    pcs = state_pcs(_chord_at(content, content["plan"]["phrases"][k]["start_bar"])(slots[i]), ctx.tonic) or []
    others = [p for j, p in enumerate(pitches) if j != i]
    lo = max(floor, max(others) - MEL.PHRASE_RANGE) if others else floor
    hi = min(floor + MEL.PHRASE_RANGE, min(others) + MEL.PHRASE_RANGE) if others else floor + MEL.PHRASE_RANGE
    cur, peak_i = pitches[i], max(range(len(pitches)), key=lambda j: (pitches[j], -j))
    base = [p for p in range(lo, hi + 1) if p % 12 in pcs and p != cur and p % 12 not in exclude_pcs and (only_pcs is None or p % 12 in only_pcs)]
    contour = [p for p in base if (p > max(others) if i == peak_i else p < pitches[peak_i])] if others else list(base)
    rest = [p for p in base if p not in contour]
    key = lambda p: (abs(p - cur), p)  # noqa: E731
    return sorted(contour, key=key) + sorted(rest, key=key)


def rerealize_phrase(content: dict, k: int, pitches: list, tonic: int, mode: str) -> None:
    """Rebuild phrase k's notes from the (repaired) skeleton pitches with the original tags (= melody.phrase_melody's surface draws).
    Non-skeleton notes an EARLIER repair re-picked keep their repaired pitch/role (same onsets: fill_weak only re-draws pitches), so a
    skeleton repair never undoes a previous NCT repair in the same phrase; if the kept pitch no longer fits, the loop repairs it anew."""
    mph, ph = content["melody"]["phrases"][k], content["plan"]["phrases"][k]
    b0, chord_at = ph["start_bar"], _chord_at(content, ph["start_bar"])
    kept = {n["slot"]: n for n in content["melody"]["notes"] if n["phrase"] == k and n.get("repaired") and n.get("role") not in SKELETON_ROLES}
    raw = MEL.fill_weak(mph["onsets"], {"pitches": list(pitches)}, mph["skeleton"]["slots"], chord_at, set(mph["change_slots"]), mph["skeleton"]["floor"],
                        tonic, mode, f"{content['tag']}|melody|{ph['index']}")
    notes = MEL.finalize_notes(raw, mph["L"], chord_at, ph["index"])
    for n in notes:
        n["slot"] += b0 * SLOTS
        old = kept.get(n["slot"])
        if old is not None and n["role"] not in SKELETON_ROLES:
            n["pitch"], n["role"], n["repaired"] = old["pitch"], old["role"], old["repaired"]
    content["melody"]["notes"] = sorted([n for n in content["melody"]["notes"] if n["phrase"] != k] + notes, key=lambda n: (n["slot"], n["pitch"]))
    _refresh_positions(content, k)
    mph["skeleton"]["pitches"] = list(pitches)
    mph["skeleton"]["violations"] = MEL.contour_violations(list(pitches), mph["skeleton"]["slots"], mph["L"])


def bass_candidates(ctx: _Ctx, content: dict, note: dict) -> tuple[dict, str]:
    """{cls: (pitch, model weight)} from bassline.class_pitch under the onset's original tag, and the class-draw tag."""
    notes = content["bass"]["notes"]
    j = notes.index(note)
    prev = notes[j - 1]["pitch"] if j > 0 else None
    b, p = note["slot"] // SLOTS, note["slot"] % SLOTS
    pcs = state_pcs(note["chord"], ctx.tonic)
    root_pc = pcs[0] if pcs else ctx.tonic
    nxt_pcs = state_pcs(notes[j + 1]["chord"], ctx.tonic) if j + 1 < len(notes) else None
    next_root = nxt_pcs[0] if nxt_pcs and nxt_pcs[0] != root_pc else None
    model = ctx.models["bass"]
    row = model.get("conditional", {}).get(f"{p % 4}|{int(next_root is not None)}") or model["marginal"]
    base = dict(row["probs"])
    base["repeat"] = base.pop("other", 0.0)
    out = {}
    for cls in BL.CLASSES:
        if cls == "approach" and next_root is None:
            continue
        pitch = BL.class_pitch(cls, root_pc, pcs or [root_pc], next_root, prev, f"{content['tag']}|bass|{b}|{p}")
        if pitch is not None and pitch != note["pitch"]:
            out[cls] = (int(pitch), float(base.get(cls, 0.0)))
    return out, f"{content['tag']}|bass|cls|{b}|{p}|repair"


# ------------------------------------------------------------------------------------------------------- trials ----
def _snapshot(content: dict):
    return (copy.deepcopy(content["melody"]["notes"]), copy.deepcopy(content["bass"]["notes"]),
            [list(ph["skeleton"]["pitches"]) if ph.get("skeleton") else None for ph in content["melody"]["phrases"]])


def _restore(content: dict, snap) -> None:
    content["melody"]["notes"], content["bass"]["notes"] = snap[0], snap[1]
    for ph, pit in zip(content["melody"]["phrases"], snap[2]):
        if pit is not None:
            ph["skeleton"]["pitches"] = pit


def _trial(ctx: _Ctx, content: dict, mutate, key, total: int) -> bool:
    snap = _snapshot(content)
    mutate()
    viols = find_violations(ctx.flatten())
    if key not in {v["key"] for v in viols} and len(viols) < total:
        return True
    _restore(content, snap)
    return False


def _entry(v: dict, branch: str, stem: str, sec: int, label: str, before, after, note_slot: int, extra: dict | None = None) -> dict:
    e = {"rule": v["rule"], "branch": branch, "stem": stem, "section": sec, "label": label, "bar": note_slot // SLOTS, "slot": note_slot, "before": before, "after": after}
    return dict(e, **(extra or {}))


def _try_bass(ctx: _Ctx, v: dict, song_note: dict, total: int, branch: str):
    """Branch (a): every class candidate is judged from the same state; the passing classes are drawn by the model row's weights."""
    content, note, sec = ctx.locate(song_note, "bass")
    if note is None or note.get("on_change") or not ctx.touchable(sec, "bass_free"):
        return None
    cands, dtag = bass_candidates(ctx, content, note)
    base = (note["pitch"], note["cls"])
    passing = {}
    for cls in sorted(cands):
        note["pitch"], note["cls"] = cands[cls][0], cls
        viols = find_violations(ctx.flatten())
        note["pitch"], note["cls"] = base
        if v["key"] not in {x["key"] for x in viols} and len(viols) < total:
            passing[cls] = cands[cls][1]
    if not passing:
        return None
    cls = draw_from(passing if sum(passing.values()) > 0 else {c: 1.0 for c in passing}, dtag)
    note["pitch"], note["cls"], note["repaired"] = cands[cls][0], cls, v["rule"]
    return _entry(v, branch, "bass", sec, ctx.sections[sec]["label"], base[0], note["pitch"], song_note["slot"], {"cls": cls, "draw_tag": dtag})


def _try_nct(ctx: _Ctx, v: dict, song_note: dict, total: int, branch: str, exclude_pcs=(), step_back=None):
    content, note, sec = ctx.locate(song_note, "melody")
    if note is None or note.get("role") in SKELETON_ROLES or not ctx.touchable(sec, "nct"):
        return None
    before = note["pitch"]
    for p in nct_candidates(ctx, content, note, exclude_pcs, step_back):
        pcs = state_pcs(note["chord"], ctx.tonic) or []

        def mut(p=p):
            prev = [n for n in content["melody"]["notes"] if n["phrase"] == note["phrase"] and n["slot"] < note["slot"]]
            note["pitch"] = p
            note["role"] = "chord_tone" if p % 12 in pcs else ("neighbour" if prev and is_step(p, prev[-1]["pitch"]) else "passing")
            note["repaired"] = v["rule"]
            _refresh_positions(content, note["phrase"])
        if _trial(ctx, content, mut, v["key"], total):
            return _entry(v, branch, "melody", sec, ctx.sections[sec]["label"], before, p, song_note["slot"], {"role": note["role"]})
    return None


def _try_skeleton(ctx: _Ctx, v: dict, song_note: dict, total: int, branch: str, exclude_pcs=(), only_pcs=None):
    content, note, sec = ctx.locate(song_note, "melody")
    if note is None or note.get("role") not in SKELETON_ROLES or not ctx.touchable(sec, "skeleton"):
        return None
    mph, ph = _phrase_of(content, note)
    rel = note["slot"] - ph["start_bar"] * SLOTS
    if note["role"] == "resolution":
        rel -= 4  # the resolution realises the skeleton pitch of the suspended slot
    if rel not in mph["skeleton"]["slots"]:
        return None
    i = mph["skeleton"]["slots"].index(rel)
    before = mph["skeleton"]["pitches"][i]
    for p in skeleton_candidates(ctx, content, note["phrase"], i, exclude_pcs, only_pcs):
        def mut(p=p):
            pit = list(mph["skeleton"]["pitches"])
            pit[i] = p
            rerealize_phrase(content, note["phrase"], pit, ctx.tonic, ctx.mode)
        if _trial(ctx, content, mut, v["key"], total):
            mph.setdefault("repairs", []).append({"skeleton_index": i, "before": before, "after": p, "rule": v["rule"]})
            return _entry(v, branch, "melody", sec, ctx.sections[sec]["label"], before, p, song_note["slot"], {"skeleton_index": i, "phrase_rerealized": True})
    return None


def _attack(ctx: _Ctx, v: dict, total: int):
    r = v["rule"]
    if r in ("parallel_fifth", "parallel_octave"):
        b0, b1 = v["bass"]
        m0, m1 = v["melody"]
        plan = [("a_bass_free", _try_bass, b1), ("a_bass_free", _try_bass, b0), ("b_melody_nct", _try_nct, m1), ("b_melody_nct", _try_nct, m0),
                ("c_melody_skeleton", _try_skeleton, m1), ("c_melody_skeleton", _try_skeleton, m0)]
        for branch, fn, n in plan:
            e = fn(ctx, v, n, total, branch)
            if e:
                return e
        return None
    if r == "leap_unresolved":
        a, b, c = v["notes"]
        e = _try_nct(ctx, v, c, total, "leap_following_nct_step_back", step_back=(b["pitch"], v["sign"]))
        plan = [("leap_following_nct", _try_nct, c), ("leap_note_nct", _try_nct, b), ("leap_preceding_nct", _try_nct, a),
                ("leap_note_skeleton", _try_skeleton, b), ("leap_following_skeleton", _try_skeleton, c), ("leap_preceding_skeleton", _try_skeleton, a)]
        for branch, fn, n in plan:
            if e:
                break
            e = fn(ctx, v, n, total, branch)
        return e
    if r == "leading_tone_unresolved":
        lt, tonic_pc = (ctx.tonic + 11) % 12, ctx.tonic % 12
        final_pcs = state_pcs(v["final_state"], ctx.tonic) or []
        e = None
        if tonic_pc in final_pcs:  # authentic / plagal / deceptive: the cadence note resolves to the tonic
            e = _try_skeleton(ctx, v, v["at"], total, "lt_cadence_note_to_tonic", only_pcs={tonic_pc})
        e = e or _try_nct(ctx, v, v["before"], total, "lt_before_nct", exclude_pcs=(lt,))
        e = e or _try_skeleton(ctx, v, v["before"], total, "lt_before_skeleton", exclude_pcs=(lt,))
        return e
    return None  # guard rules are never targeted directly


def _loop(ctx: _Ctx, pass_name: str) -> dict:
    log, forced, gave_up = [], [], set()
    while True:
        viols = find_violations(ctx.flatten())
        todo = [v for v in viols if v["key"] not in gave_up and v["rule"] not in GUARD_RULES]
        if not todo:
            break
        v = todo[0]
        e = _attack(ctx, v, len(viols))
        if e:
            log.append(dict(e, **{"pass": pass_name}))
            continue
        gave_up.add(v["key"])
        kinds = {"parallel_fifth": "bass free (a) / melody NCT (b) / melody skeleton (c)", "parallel_octave": "bass free (a) / melody NCT (b) / melody skeleton (c)",
                 "leap_unresolved": "following / leap / preceding note (NCT then skeleton)", "leading_tone_unresolved": "cadence note -> tonic / note before (NCT then skeleton)"}[v["rule"]]
        sec = (v.get("bass") or v.get("notes") or [v.get("at")])[-1]["section"]
        forced.append({"pass": pass_name, "rule": v["rule"], "bar": v["slot"] // SLOTS, "slot": v["slot"], "section": sec, "label": ctx.sections[sec]["label"],
                       "reason": f"no candidate in any branch ({kinds}) removes it without creating another violation"
                                 + ("" if ctx.touch_skeleton else "; skeleton notes untouchable in the recurrence pass")})
    remaining = [{"rule": v["rule"], "slot": v["slot"]} for v in find_violations(ctx.flatten()) if v["rule"] not in GUARD_RULES]
    return {"pass": pass_name, "repairs": log, "forced": forced, "remaining": remaining}


def _summary(parts: list) -> dict:
    reps = [e for p in parts for e in p["repairs"]]
    by_rule: dict = {}
    for e in reps:
        by_rule[e["rule"]] = by_rule.get(e["rule"], 0) + 1
    forced = [f for p in parts for f in p["forced"]]
    return {"schema_version": 1, "passes": [p["pass"] for p in parts], "n_repairs": len(reps), "by_rule": by_rule, "repairs": reps, "n_forced": len(forced), "forced": forced,
            "remaining": parts[-1]["remaining"] if parts else []}


def repair_labels(models: dict, plan: dict, labels: dict, tonic: int, mode: str, flatten_fn) -> dict:
    """Pass 1: repair the per-label bass / melody content in place (every recurrence inherits it). flatten_fn() -> song dict."""
    ctx = _Ctx(models, plan, labels, None, tonic, mode, flatten_fn, True, None)
    return _summary([_loop(ctx, "labels")])


def repair_sections(models: dict, plan: dict, by_section: dict, var_info: dict, tonic: int, mode: str, flatten_fn, prev: dict | None = None) -> dict:
    """Pass 2 (--humanize): repair the varied recurrences' surface (non-skeleton melody notes, free bass notes; bass copied on write)."""
    varied = {int(k) for k, v in var_info.items() if v.get("varied")}
    for idx in sorted(varied):
        L2 = by_section[idx]
        L2["bass"] = dict(L2["bass"], notes=[dict(n) for n in L2["bass"]["notes"]])
    ctx = _Ctx(models, plan, None, by_section, tonic, mode, flatten_fn, False, varied)
    part = _loop(ctx, "sections")
    parts = ([{"pass": "labels", "repairs": prev["repairs"], "forced": prev["forced"], "remaining": prev["remaining"]}] if prev else []) + [part]
    return _summary(parts)
