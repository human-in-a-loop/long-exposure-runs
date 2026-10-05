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
    "unresolved_sevenths": {"op": "<=", "cap": 2, "per": "song", "doc": "at a chord change, a keys voice on the chord 7th that is neither RETAINED (its pitch still sounds in the next voicing: a common tone, hence a chord tone of the next chord) nor moved DOWN BY STEP (1-2 semitones); a 7th released into a rest (an N slot between the chords) is exempt; voicing.unresolved_sevenths is the single definition used by the DP cost, this validator and the stage-1 harmony mask (harmony.resolvable_matrix / voicing.seventh_resolvable)"},
    "leading_tone_unresolved_at_cadence": {"op": "<=", "cap": 1, "per": "song", "doc": "degree 7 (major) in keys or melody at a phrase's final transition not moving to the tonic"},
    "melodic_leaps_unresolved": {"op": "<=", "cap": 2, "per": "per_64_bars", "doc": "melody leap > 5 semitones not followed by a step in the opposite direction"},
    "melody_range_violations": {"op": "==", "cap": 0, "per": "song", "doc": "phrases whose melody range exceeds 12 semitones"},
    "melody_strong_beat_non_chord_tones": {"op": "<=", "cap": 0.05, "per": "fraction", "doc": "fraction of melody notes on beats 1/3 or chord changes that are not chord tones (suspensions/anticipations excluded)"},
    "bass_root_missing_on_change": {"op": "==", "cap": 0, "per": "song", "doc": "chord changes (bass not muted) without a bass root onset"},
    "cadences_realized": {"op": "==", "cap": 1.0, "per": "fraction", "doc": "fraction of phrases whose realised cadence equals the planned one"},
    "harmonic_rhythm_realized": {"op": "==", "cap": 1.0, "per": "fraction", "doc": "fraction of bars whose chord-slot count equals the planned harmonic rhythm"},
    "voice_crossing": {"op": "<=", "cap": 2, "per": "per_64_bars", "doc": "keys voice crossings/overlaps between consecutive voicings"},
    "section_repeat_integrity": {"op": "==", "cap": True, "per": "song", "doc": "every recurrence of a label is note-identical outside arrangement-touched bars (under --humanize: harmony + bass root line + melody skeleton identical while surface events differ)"},
}
# Phase 3 (--humanize) additions: validate_humanized() appends these to the metrics / cap_pass of a humanized song.
HUMANIZE_CAPS = {
    "timing_ks_max": {"op": "<=", "cap": 0.25, "per": "song", "doc": "max over streams (kick/snare/hat/bass, n >= 10) of the two-sample KS statistic between the humanized offsets (fraction of a 16th) and the model's reference histogram for that stream; the reference is SLOT-MIX REWEIGHTED: the model's per-slot offset distributions (slot_hist_f16) mixed with the song's own onset count per 16th slot (microtiming_model.reference_hist), so the song's odd/even-8th slot occupancy cannot shift the statistic; a model without per-slot distributions (the corpus pooled model) is compared against its pooled hist_f16 unchanged"},
    "velocity_std_min": {"op": ">=", "cap": 8.0, "per": "song", "doc": "min over non-empty stems of the velocity standard deviation (dynamics not flat)"},
    "swing_in_corpus_iqr": {"op": "==", "cap": True, "per": "song", "doc": "humanized drums swing ratio within [Q1 - 0.02, Q3 + 0.02] of the near-tempo corpus songs' swing ratios"},
    "section_repeat_skeleton_integrity": {"op": "==", "cap": True, "per": "song", "doc": "harmony, bass root line, keys pitch sets per bar and melody skeleton identical across label recurrences (comparable bars only)"},
    "section_repeat_surface_differs": {"op": "==", "cap": True, "per": "song", "doc": "at least one comparable recurrence pair differs in its surface events (None = nothing comparable, counts as pass)"},
}
ALL_CAPS = {**CAPS, **HUMANIZE_CAPS}


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
    """voicing.unresolved_sevenths over consecutive voiced chord slots; an unvoiced ('N') slot between two voiced ones is a rest
    (the 7th was released into silence: exempt, exactly as the DP costs it)."""
    n, prev, rest = 0, None, False
    for c in song["chord_slots"]:
        if not c.get("voicing"):
            rest = prev is not None
            continue
        if prev is not None:
            n += _unres7(tuple(prev["voicing"]), tuple(c["voicing"]), chord_tones(prev["state"], song["tonic"]), prev["state"] == c["state"], rest)
        prev, rest = c, False
    return n


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
    c = ALL_CAPS[name]
    v = value
    if c["per"] == "per_64_bars":
        v = float(value) * 64.0 / max(1, n_bars)
    if c["op"] == ">=":
        return v is not None and v >= c["cap"]
    if c["op"] == "==" and c["cap"] is True and v is None:
        return True  # not applicable (e.g. no comparable recurrence pair)
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
    names = list(CAPS) + [k for k in HUMANIZE_CAPS if per_song and all(k in v["metrics"] for v in per_song.values())]
    rows = {sid: {k: v["metrics"][k] for k in names} for sid, v in sorted(per_song.items())}
    pass_counts = {k: sum(1 for v in per_song.values() if v["cap_pass"][k]) for k in names}
    return {"schema_version": 1, "n_songs": len(per_song), "validators": names, "rows": rows, "cap_pass_counts": pass_counts,
            "songs_all_caps_pass": sum(1 for v in per_song.values() if v["all_caps_pass"]), "caps": {k: ALL_CAPS[k] for k in names}}


def format_table(agg: dict) -> str:
    names = agg["validators"]
    short = {n: n[:18] for n in names}
    head = "song".ljust(22) + " ".join(short[n].rjust(18) for n in names)
    lines = [head]
    for sid, row in agg["rows"].items():
        lines.append(sid[:22].ljust(22) + " ".join((f"{row[n]:.3f}" if isinstance(row[n], float) else str(row[n])).rjust(18) for n in names))
    lines.append("cap_pass".ljust(22) + " ".join(f"{agg['cap_pass_counts'][n]}/{agg['n_songs']}".rjust(18) for n in names))
    return "\n".join(lines)


# ----------------------------------------------------------------------------------------------- Phase 3: --humanize ----
_DRUM_STREAM = {36: "kick", 38: "snare", 42: "hat", 46: "hat"}
_SKELETON_ROLES = ("skeleton", "cadence", "suspension", "resolution")


def humanized_offsets_f16(song: dict) -> dict:
    """{stream: [offset in fractions of a 16th]} for the streams the corpus model knows (kick, snare, hat, bass)."""
    s16_ms = 60000.0 / float(song["bpm"]) / 4.0
    out = {"kick": [], "snare": [], "hat": [], "bass": [float(n.get("offset_ms", 0.0)) / s16_ms for n in song["bass"]]}
    for h in song["drums"]:
        out[_DRUM_STREAM.get(h["pitch"], "hat")].append(float(h.get("offset_ms", 0.0)) / s16_ms)
    return out


def humanized_slot_counts(song: dict) -> dict:
    """{stream: [onset count per 16th slot (16)]} — the song's own slot occupancy, the weights of the slot-mix reference."""
    out = {"kick": [0] * 16, "snare": [0] * 16, "hat": [0] * 16, "bass": [0] * 16}
    for n in song["bass"]:
        out["bass"][n["slot"] % SLOTS] += 1
    for h in song["drums"]:
        out[_DRUM_STREAM.get(h["pitch"], "hat")][h["slot"] % SLOTS] += 1
    return out


def timing_ks(song: dict, pool: dict, min_n: int = 10) -> dict:
    """Per stream: KS between the humanized offsets and microtiming_model.reference_hist (per-slot distributions mixed with the
    song's slot counts when the model carries them, else the pooled histogram); see HUMANIZE_CAPS["timing_ks_max"]."""
    from scripts.v6.gen.microtiming_model import ks_vs_hist, reference_hist
    per = {}
    counts = humanized_slot_counts(song)
    for st, xs in humanized_offsets_f16(song).items():
        ref, kind = reference_hist(pool["streams"][st], counts[st])
        per[st] = dict(ks_vs_hist(xs, ref) if len(xs) >= min_n else {"D": None, "n": len(xs)}, reference=kind, slot_n=counts[st])
    ds = [v["D"] for v in per.values() if v["D"] is not None]
    return {"per_stream": per, "max_D": max(ds) if ds else None}


def velocity_std(song: dict) -> dict:
    out = {}
    for stem in ("drums", "bass", "keys", "melody"):
        vs = [float(n["velocity"]) for n in song[stem]]
        if vs:
            m = sum(vs) / len(vs)
            out[stem] = round((max(0.0, sum(v * v for v in vs) / len(vs) - m * m)) ** 0.5, 3)
    return {"per_stem": out, "min": min(out.values()) if out else None}


def humanized_swing(song: dict, pool: dict) -> dict:
    """Drums swing ratio from the humanized offsets (odd-8th vs even-8th slots) vs the pool's per-song IQR (+/-0.02 slack)."""
    s16_ms = 60000.0 / float(song["bpm"]) / 4.0
    odd = [h["offset_ms"] for h in song["drums"] if h["slot"] % 16 in (2, 6, 10, 14) and "offset_ms" in h]
    even = [h["offset_ms"] for h in song["drums"] if h["slot"] % 16 in (0, 4, 8, 12) and "offset_ms" in h]
    if len(odd) < 5 or len(even) < 5:
        return {"ratio": None, "offset_ms": None, "in_iqr": None, "n_odd": len(odd), "n_even": len(even)}
    d = (sum(odd) / len(odd) - sum(even) / len(even))
    df = max(-1.5, min(1.5, d / s16_ms))
    ratio = (2 + df) / (2 - df)
    q = pool["swing_ratios_drums"]
    lo, hi = q.get("0.25"), q.get("0.75")
    ok = None if lo is None or hi is None else (lo - 0.02 <= ratio <= hi + 0.02)
    return {"ratio": round(ratio, 4), "offset_ms": round(d, 3), "in_iqr": ok, "iqr": [lo, hi], "n_odd": len(odd), "n_even": len(even)}


def section_repeat_relaxed(song: dict) -> dict:
    """Per label recurrence pair and per stem, over the bars where the stem is unmuted in both sections (no hold; no fill for
    drums): harmony (beat chords), bass root-line (forced roots), keys pitch set per bar and melody skeleton notes must be
    identical; the full surface (slots, pitches, velocities, offsets, durations) is compared for difference."""
    nb, arr = song["bars_per_section"], song["arrangement"]
    by_label: dict = {}
    for sec in song["sections"]:
        by_label.setdefault(sec["label"], []).append(sec)
    stems = {k: sorted(song[k], key=lambda n: (n["slot"], n["pitch"])) for k in ("melody", "bass", "keys", "drums")}

    def notes_in(stem: str, s0: int, rel_bars: set) -> list:
        return [n for n in stems[stem] if (n["slot"] // SLOTS) - s0 in rel_bars]

    def surface(stem: str, s0: int, rel: set) -> list:
        return sorted((n["slot"] - s0 * SLOTS, n["pitch"], n.get("velocity"), round(float(n.get("offset_ms", 0.0)), 3), round(float(n.get("dur16", 0)), 4)) for n in notes_in(stem, s0, rel))

    def skeleton(stem: str, s0: int, rel: set):
        ns = notes_in(stem, s0, rel)
        if stem == "melody":
            return sorted((n["slot"] - s0 * SLOTS, n["pitch"]) for n in ns if n.get("role") in _SKELETON_ROLES)
        if stem == "bass":
            return sorted((n["slot"] - s0 * SLOTS, n["pitch"]) for n in ns if n.get("cls") in ("root", "root_hold") and n.get("on_change", True))
        if stem == "keys":
            return sorted({((n["slot"] // SLOTS) - s0, n["pitch"]) for n in ns})
        return sorted((n["slot"] - s0 * SLOTS, n["pitch"]) for n in ns if n["pitch"] == 36)  # drums: the kick pattern
    pairs, mism, differ, comparable, detail = 0, 0, 0, 0, []
    for lab, group in by_label.items():
        for other in group[1:]:
            a, b = group[0]["start_bar"], other["start_bar"]
            pairs += 1
            rec = {"label": lab, "sections": [group[0]["index"], other["index"]], "harmony_ok": None, "stems": {}}
            hb = [k for k in range(nb) if not arr[a + k].get("hold") and not arr[b + k].get("hold")]
            rec["harmony_ok"] = all(song["beat_chords"][a + k] == song["beat_chords"][b + k] for k in hb)
            if not rec["harmony_ok"]:
                mism += 1
            for stem in ("melody", "bass", "keys", "drums"):
                rel = {k for k in range(nb) if stem not in arr[a + k]["mute"] and stem not in arr[b + k]["mute"] and not arr[a + k].get("hold") and not arr[b + k].get("hold")
                       and not (stem == "drums" and (arr[a + k].get("fill") or arr[b + k].get("fill")))}
                if not rel or (not notes_in(stem, a, rel) and not notes_in(stem, b, rel)):
                    rec["stems"][stem] = {"comparable": False}
                    continue
                comparable += 1
                sk_ok = skeleton(stem, a, rel) == skeleton(stem, b, rel)
                sf_diff = surface(stem, a, rel) != surface(stem, b, rel)
                mism += 0 if sk_ok else 1
                differ += 1 if sf_diff else 0
                rec["stems"][stem] = {"comparable": True, "n_bars": len(rel), "skeleton_identical": sk_ok, "surface_differs": sf_diff}
            detail.append(rec)
    return {"skeleton_ok": mism == 0, "surface_differs": (differ > 0) if comparable else None, "n_pairs": pairs, "n_comparable_stem_pairs": comparable,
            "n_skeleton_mismatches": mism, "n_surface_differing": differ, "pairs": detail}


def validate_humanized(song: dict, pool: dict) -> dict:
    """validate() + the HUMANIZE_CAPS metrics; section_repeat_integrity relaxed to skeleton-identical AND surface-differs."""
    res = validate(song)
    rep = section_repeat_relaxed(song)
    ks = timing_ks(song, pool)
    vs = velocity_std(song)
    sw = humanized_swing(song, pool)
    m = res["metrics"]
    m["section_repeat_integrity"] = bool(rep["skeleton_ok"] and rep["surface_differs"] in (True, None))
    m["section_repeat_skeleton_integrity"] = bool(rep["skeleton_ok"])
    m["section_repeat_surface_differs"] = rep["surface_differs"]
    m["timing_ks_max"] = ks["max_D"] if ks["max_D"] is not None else 0.0
    m["velocity_std_min"] = vs["min"]
    m["swing_in_corpus_iqr"] = sw["in_iqr"]
    res["cap_pass"] = {k: _cap_pass(k, v, song["n_bars"]) for k, v in m.items()}
    res["all_caps_pass"] = all(res["cap_pass"].values())
    res["caps"] = dict(ALL_CAPS)
    res["humanized"] = True
    res["detail"]["humanize"] = {"section_repeat_relaxed": rep, "timing_ks": ks, "velocity_std": vs, "swing": sw, "model_variant": pool.get("variant"), "model_n_songs": pool.get("n_songs")}
    return res
