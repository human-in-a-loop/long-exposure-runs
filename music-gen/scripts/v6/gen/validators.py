#!/usr/bin/python3
"""v6 Phase 2 — validators: every composition rule re-counted on the realised symbolic output (+ the documented caps).

created: 2026-10-04
milestone: M-V6-GEN-2/theory-grounded-composer

Input: the `song` dict compose_v6 builds (bpm, tonic, mode, n_bars, chord_slots with voicings, phrases, melody / bass /
keys / drums note lists in song slots, arrangement per bar, sections). Output: per-validator counts/booleans + the cap
table CAPS used later by the scorecard (scripts/v6/scorecard.py, other agent): each cap says the quantity, the operator and
the normalisation ("per_64_bars" scales the count by 64 / n_bars before comparing).
"""
from __future__ import annotations

from scripts.v6.gen.common import SLOTS, state_pcs
from scripts.v6.gen.melody import PHRASE_RANGE, unresolved_leaps
from scripts.v6.gen.voicing import chord_tones, crossings, parallel_perfects, unresolved_sevenths as _unres7

CAPS = {
    "parallel_fifths": {"op": "<=", "cap": 1, "per": "per_64_bars", "doc": "parallel perfect 5ths between keys voices, bass-keys and bass-melody pairs"},
    "parallel_octaves": {"op": "<=", "cap": 1, "per": "per_64_bars", "doc": "parallel octaves/unisons, same pairs"},
    "unresolved_sevenths": {"op": "<=", "cap": 2, "per": "song", "doc": "chord 7th in a keys voice not held or resolved down by step at a chord change"},
    "leading_tone_unresolved_at_cadence": {"op": "<=", "cap": 1, "per": "song", "doc": "degree 7 (major) in keys or melody at a phrase's final transition not moving to the tonic"},
    "melodic_leaps_unresolved": {"op": "<=", "cap": 2, "per": "per_64_bars", "doc": "melody leap > 5 semitones not followed by a step in the opposite direction"},
    "melody_range_violations": {"op": "==", "cap": 0, "per": "song", "doc": "phrases whose melody range exceeds 12 semitones"},
    "melody_strong_beat_non_chord_tones": {"op": "<=", "cap": 0.05, "per": "fraction", "doc": "fraction of melody notes on beats 1/3 or chord changes that are not chord tones (suspensions/anticipations excluded)"},
    "bass_root_missing_on_change": {"op": "==", "cap": 0, "per": "song", "doc": "chord changes (bass not muted) without a bass root onset"},
    "cadences_realized": {"op": "==", "cap": 1.0, "per": "fraction", "doc": "fraction of phrases whose realised cadence equals the planned one"},
    "harmonic_rhythm_realized": {"op": "==", "cap": 1.0, "per": "fraction", "doc": "fraction of bars whose chord-slot count equals the planned harmonic rhythm"},
    "voice_crossing": {"op": "<=", "cap": 2, "per": "per_64_bars", "doc": "keys voice crossings/overlaps between consecutive voicings"},
    "section_repeat_integrity": {"op": "==", "cap": True, "per": "song", "doc": "every recurrence of a label is note-identical outside arrangement-touched bars"},
}


def _sounding(notes: list, slot: int):
    best = None
    for n in notes:
        if n["slot"] <= slot < n["slot"] + n["dur16"]:
            best = n["pitch"]
        elif n["slot"] > slot:
            break
    return best


def _voiced_slots(song: dict) -> list:
    return [c for c in song["chord_slots"] if c.get("voicing")]


def parallel_perfect_intervals(song: dict) -> dict:
    keys5 = keys8 = bk5 = bk8 = bm5 = bm8 = 0
    vs = _voiced_slots(song)
    bass = sorted(song["bass"], key=lambda n: n["slot"])
    mel = sorted(song["melody"], key=lambda n: n["slot"])
    for a, b in zip(vs, vs[1:]):
        va, vb = tuple(a["voicing"]), tuple(b["voicing"])
        for i in range(4):
            for j in range(i + 1, 4):
                ia, ib = (va[j] - va[i]) % 12, (vb[j] - vb[i]) % 12
                if ia == ib and ia in (0, 7) and (vb[i] - va[i]) * (vb[j] - va[j]) > 0:
                    if ia == 7:
                        keys5 += 1
                    else:
                        keys8 += 1
        ba, bb = _sounding(bass, a["bar"] * SLOTS + a["beat"] * 4), _sounding(bass, b["bar"] * SLOTS + b["beat"] * 4)
        if ba is not None and bb is not None and ba != bb:
            for i in range(4):
                ia, ib = (va[i] - ba) % 12, (vb[i] - bb) % 12
                if ia == ib and ia in (0, 7) and (vb[i] - va[i]) * (bb - ba) > 0:
                    if ia == 7:
                        bk5 += 1
                    else:
                        bk8 += 1
    prev = None
    for n in bass:
        m = _sounding(mel, n["slot"])
        if prev is not None and m is not None and prev[1] is not None:
            ia, ib = (prev[1] - prev[0]) % 12, (m - n["pitch"]) % 12
            if ia == ib and ia in (0, 7) and (n["pitch"] - prev[0]) * (m - prev[1]) > 0:
                if ia == 7:
                    bm5 += 1
                else:
                    bm8 += 1
        prev = (n["pitch"], m)
    return {"parallel_fifths": keys5 + bk5 + bm5, "parallel_octaves": keys8 + bk8 + bm8,
            "breakdown": {"keys_fifths": keys5, "keys_octaves": keys8, "bass_keys_fifths": bk5, "bass_keys_octaves": bk8, "bass_melody_fifths": bm5, "bass_melody_octaves": bm8}}


def unresolved_sevenths(song: dict) -> int:
    vs = _voiced_slots(song)
    return sum(_unres7(tuple(a["voicing"]), tuple(b["voicing"]), chord_tones(a["state"], song["tonic"]), a["state"] == b["state"]) for a, b in zip(vs, vs[1:]))


def voice_crossing(song: dict) -> int:
    vs = _voiced_slots(song)
    return sum(crossings(tuple(a["voicing"]), tuple(b["voicing"])) for a, b in zip(vs, vs[1:]))


def leading_tone_unresolved_at_cadence(song: dict) -> dict:
    if str(song["mode"]).lower() != "major":
        return {"count": 0, "keys": 0, "melody": 0, "n_cadences": len(song["phrases"])}
    lt, tonic_pc = (song["tonic"] + 11) % 12, song["tonic"] % 12
    by_pos = {(c["bar"], c["beat"]): c for c in song["chord_slots"]}
    keys_n = mel_n = 0
    mel = sorted(song["melody"], key=lambda n: n["slot"])
    for ph in song["phrases"]:
        sl = ph["slots"]
        if len(sl) < 2:
            continue
        a, b = by_pos.get((sl[-2]["bar"], sl[-2]["beat"])), by_pos.get((sl[-1]["bar"], sl[-1]["beat"]))
        if a and b and a.get("voicing") and b.get("voicing"):
            keys_n += sum(1 for x, y in zip(a["voicing"], b["voicing"]) if x % 12 == lt and y % 12 != tonic_pc and y != x)
        cad_slot = sl[-1]["bar"] * SLOTS + sl[-1]["beat"] * 4
        before = [n for n in mel if sl[-2]["bar"] * SLOTS + sl[-2]["beat"] * 4 <= n["slot"] < cad_slot]
        at = [n for n in mel if n["slot"] == cad_slot]
        if before and at and before[-1]["pitch"] % 12 == lt and at[0]["pitch"] % 12 != tonic_pc:
            mel_n += 1
    return {"count": keys_n + mel_n, "keys": keys_n, "melody": mel_n, "n_cadences": len(song["phrases"])}


def melody_checks(song: dict) -> dict:
    mel = sorted(song["melody"], key=lambda n: n["slot"])
    leaps = range_v = strong = strong_nct = 0
    for ph in song["phrases"]:
        s0, s1 = ph["start_bar"] * SLOTS, (ph["start_bar"] + ph["n_bars"]) * SLOTS
        notes = [n for n in mel if s0 <= n["slot"] < s1]
        if not notes:
            continue
        leaps += unresolved_leaps([n["pitch"] for n in notes])
        if max(n["pitch"] for n in notes) - min(n["pitch"] for n in notes) > PHRASE_RANGE:
            range_v += 1
    change = {c["bar"] * SLOTS + c["beat"] * 4 for c in song["chord_slots"]}
    for n in mel:
        if (n["slot"] % 8 == 0 or n["slot"] in change) and n.get("role") not in ("suspension", "anticipation"):
            pcs = state_pcs(song["beat_chords"][n["slot"] // SLOTS][(n["slot"] % SLOTS) // 4], song["tonic"])
            if pcs:
                strong += 1
                if n["pitch"] % 12 not in pcs:
                    strong_nct += 1
    return {"melodic_leaps_unresolved": leaps, "melody_range_violations": range_v, "melody_strong_beats": strong,
            "melody_strong_beat_non_chord_tones": strong_nct, "melody_strong_beat_nct_fraction": round(strong_nct / strong, 6) if strong else 0.0}


def bass_root_missing_on_change(song: dict) -> dict:
    by_slot = {}
    for n in song["bass"]:
        by_slot.setdefault(n["slot"], []).append(n["pitch"] % 12)
    missing = total = 0
    prev = None
    for b in range(song["n_bars"]):
        if "bass" in song["arrangement"][b]["mute"]:
            prev = song["beat_chords"][b][3]
            continue
        for bt in range(4):
            st = song["beat_chords"][b][bt]
            if st != prev and st != "N":
                total += 1
                root = state_pcs(st, song["tonic"])[0]
                if root not in by_slot.get(b * SLOTS + bt * 4, []):
                    missing += 1
            prev = st
    return {"count": missing, "n_changes": total}


def cadences_realized(song: dict) -> dict:
    ph = song["phrases"]
    ok = sum(1 for p in ph if p["cadence_realized"] == p["cadence_planned"])
    cond = sum(1 for p in ph if p["conditioning_ok"])
    return {"n_phrases": len(ph), "n_realized": ok, "fraction": round(ok / len(ph), 6) if ph else 1.0, "n_conditioning_ok": cond,
            "by_type": {t: sum(1 for p in ph if p["cadence_planned"] == t) for t in ("authentic", "half", "plagal", "deceptive")}}


def harmonic_rhythm_realized(song: dict) -> dict:
    per_bar = {}
    for c in song["chord_slots"]:
        per_bar[c["bar"]] = per_bar.get(c["bar"], 0) + 1
    planned = song["harmonic_rhythm_planned"]
    eq = sum(1 for b in range(song["n_bars"]) if per_bar.get(b, 0) == planned[b])
    return {"n_bars": song["n_bars"], "n_equal": eq, "fraction": round(eq / song["n_bars"], 6), "realized": [per_bar.get(b, 0) for b in range(song["n_bars"])]}


def section_repeat_integrity(song: dict) -> dict:
    nb = song["bars_per_section"]
    secs = song["sections"]
    touched = {b for b, a in enumerate(song["arrangement"]) if a["mute"] or a.get("fill") or a.get("hold")}
    stems = {k: sorted(song[k], key=lambda n: (n["slot"], n["pitch"])) for k in ("melody", "bass", "keys", "drums")}

    def core(sec: dict) -> list:
        s0 = sec["start_bar"] * SLOTS
        out = []
        for k, notes in stems.items():
            for n in notes:
                b = n["slot"] // SLOTS
                if sec["start_bar"] <= b < sec["start_bar"] + nb and b not in touched:
                    out.append((k, n["slot"] - s0, n["pitch"], round(float(n.get("dur16", 0)), 4), n.get("velocity")))
        return sorted(out)

    by_label: dict = {}
    for sec in secs:
        by_label.setdefault(sec["label"], []).append(sec)
    pairs = mismatches = 0
    for lab, group in by_label.items():
        if len(group) < 2:
            continue
        touched_rel = {(b - s["start_bar"]) for s in group for b in range(s["start_bar"], s["start_bar"] + nb) if b in touched}
        cores = []
        for s in group:
            c = [x for x in core(s) if (x[1] // SLOTS) not in touched_rel]
            cores.append(c)
        for c in cores[1:]:
            pairs += 1
            if c != cores[0]:
                mismatches += 1
    return {"ok": mismatches == 0, "n_pairs": pairs, "n_mismatches": mismatches}


def _cap_pass(name: str, value, n_bars: int) -> bool:
    c = CAPS[name]
    v = value
    if c["per"] == "per_64_bars":
        v = float(value) * 64.0 / max(1, n_bars)
    return v <= c["cap"] if c["op"] == "<=" else v == c["cap"]


def validate(song: dict) -> dict:
    par = parallel_perfect_intervals(song)
    mel = melody_checks(song)
    lt = leading_tone_unresolved_at_cadence(song)
    br = bass_root_missing_on_change(song)
    cad = cadences_realized(song)
    hr = harmonic_rhythm_realized(song)
    rep = section_repeat_integrity(song)
    metrics = {"parallel_fifths": par["parallel_fifths"], "parallel_octaves": par["parallel_octaves"], "unresolved_sevenths": unresolved_sevenths(song),
               "leading_tone_unresolved_at_cadence": lt["count"], "melodic_leaps_unresolved": mel["melodic_leaps_unresolved"],
               "melody_range_violations": mel["melody_range_violations"], "melody_strong_beat_non_chord_tones": mel["melody_strong_beat_nct_fraction"],
               "bass_root_missing_on_change": br["count"], "cadences_realized": cad["fraction"], "harmonic_rhythm_realized": hr["fraction"],
               "voice_crossing": voice_crossing(song), "section_repeat_integrity": rep["ok"]}
    passes = {k: _cap_pass(k, v, song["n_bars"]) for k, v in metrics.items()}
    return {"schema_version": 1, "n_bars": song["n_bars"], "metrics": metrics, "cap_pass": passes, "all_caps_pass": all(passes.values()), "caps": CAPS,
            "detail": {"parallels": par["breakdown"], "melody": mel, "leading_tone": lt, "bass_roots": br, "cadences": cad, "harmonic_rhythm": {k: v for k, v in hr.items() if k != "realized"},
                       "section_repeat": rep}}


def aggregate(per_song: dict) -> dict:
    """{song_id: validators dict} -> table rows + per-validator pass counts."""
    names = list(CAPS)
    rows = {sid: {k: v["metrics"][k] for k in names} for sid, v in sorted(per_song.items())}
    pass_counts = {k: sum(1 for v in per_song.values() if v["cap_pass"][k]) for k in names}
    return {"schema_version": 1, "n_songs": len(per_song), "validators": names, "rows": rows, "cap_pass_counts": pass_counts,
            "songs_all_caps_pass": sum(1 for v in per_song.values() if v["all_caps_pass"]), "caps": CAPS}


def format_table(agg: dict) -> str:
    names = agg["validators"]
    short = {n: n[:18] for n in names}
    head = "song".ljust(22) + " ".join(short[n].rjust(18) for n in names)
    lines = [head]
    for sid, row in agg["rows"].items():
        lines.append(sid[:22].ljust(22) + " ".join((f"{row[n]:.3f}" if isinstance(row[n], float) else str(row[n])).rjust(18) for n in names))
    lines.append("cap_pass".ljust(22) + " ".join(f"{agg['cap_pass_counts'][n]}/{agg['n_songs']}".rjust(18) for n in names))
    return "\n".join(lines)
