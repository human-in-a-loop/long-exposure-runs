#!/usr/bin/python3
"""v6 Phase 3 — humanize: microtiming, dynamics, variation on repeats and articulation applied to the composed song dict
(compose_v6.flatten output, BEFORE to_events serialisation). Every draw is SHA-256 (common.u); z ~ N(0,1) by Box-Muller.

created: 2026-10-04
milestone: M-V6-GEN-3/humanization

Model: the near_tempo pool of data/v6/rules/microtiming_v6.json (songs within +/-15 % of the song's bpm, else pooled-all),
or microtiming_model.prior_model() in fixture mode. Per note:
 (i)  MICROTIMING offset_ms = per-stream per-slot RESIDUAL mean + swing (odd-8th slots 2/6/10/14 only; the pool's median
      per-song drums swing ratio converted to ms at the song's bpm) + std x z, clipped to +/-35 % of a 16th. Bass at a slot
      with a kick hit follows that kick's offset + the learned bass-vs-kick lag; keys chords land 5..12 ms late (one draw
      per chord onset); melody N(+2, 6) ms with a phrase-end ritardando (+6 / +14 ms on the last two notes of a phrase).
 (ii) DYNAMICS velocity = base x metric weight (learned velocity-by-slot dB per stream; keys/melody use the drum streams'
      beat-class means at half strength) x hypermeter (learned bar-in-8 dB), + linear crescendo into the cadence bar (up to
      +12; kick/snare at half), ghost notes (weak 16th hats and kick doubles -> 40..55), melody phrase peak +8, + 4 x z jitter.
      dB -> multiplier 10^(dB/40) (FluidR3-style amplitude ~ velocity^2), dB clipped to +/-6, multiplier to [0.7, 1.3].
(iii) VARIATION ON REPEATS (vary_recurrences, before flatten): for every recurrence r >= 1 of a label, harmony, keys
      voicings, the bass line and the melody skeleton (incl. suspension decisions) stay identical; re-drawn with the tag suffix
      "|rec=r": melody non-skeleton onsets + non-chord-tone choices, comping rhythm, hat row of every bar, the section fill,
      and (through the tags) every dynamics/microtiming draw. Open hat (GM 46) on slot 14 with p = 0.3 per bar.
 (iv) ARTICULATION: melody 0.85..0.95 of the IOI (0.8 before the phrase's last note; cadence hold kept); keys sustain
      0.6..0.95 of the IOI (prior 0.6 + 0.35 u^0.7); bass from the learned duration-proxy histogram (inverse CDF, clipped
      0.5..0.9 of the IOI, x 0.7 on syncopated slots); drums unchanged (one-shots).
Serialisation: scripts/v5/midi_from_json_events_v5 rounds start_time seconds to 480-PPQ ticks (no 16th quantisation), so
compose_v6.to_events carries offset_ms straight into start_time.
"""
from __future__ import annotations

import math

from scripts.v6.gen import bassline as BL
from scripts.v6.gen import drums as DR
from scripts.v6.gen import melody as MEL
from scripts.v6.gen import microtiming_model as M
from scripts.v6.gen import voicing as VO
from scripts.v6.gen.common import SLOTS, draw_from, u

CLIP_F16 = 0.35
KEYS_LATE_MS = (5.0, 12.0)
MEL_MEAN_MS, MEL_STD_MS = 2.0, 6.0
RIT_MS = (6.0, 14.0)
LAG_STD_CAP_MS = 10.0
STD_SCALE = 0.6
CRESC_MAX = 12.0
GHOST = (40, 55)
PEAK_BONUS = 8.0
VEL_JITTER = 4.0
DB_CLIP, MULT_CLIP = 6.0, (0.7, 1.3)
P_OPEN_HAT, OPEN_HAT, OPEN_HAT_SLOT = 0.3, 46, 14
MEL_LEGATO = (0.85, 0.95)
BREATH = 0.8
COMP_SUSTAIN = (0.6, 0.35, 0.7)  # lo + span * u ** k
BASS_DUR_CLIP, STACCATO = (0.5, 0.9), 0.7
DRUM_STREAM = {DR.KICK: "kick", DR.SNARE: "snare", DR.HAT: "hat", OPEN_HAT: "hat"}
REPHRASE_TRIES = 6
SKELETON_ROLES = ("skeleton", "cadence", "suspension", "resolution")


# ------------------------------------------------------------------------------------------------------- draws ----
def z(tag: str) -> float:
    """Deterministic standard normal: Box-Muller on two SHA-256 uniforms, clipped to +/-3."""
    u1, u2 = u(f"{tag}|z1"), u(f"{tag}|z2")
    r = math.sqrt(-2.0 * math.log(1.0 - u1))
    return max(-3.0, min(3.0, r * math.cos(2.0 * math.pi * u2)))


def vel_mult(db) -> float:
    if db is None:
        return 1.0
    d = max(-DB_CLIP, min(DB_CLIP, float(db)))
    return max(MULT_CLIP[0], min(MULT_CLIP[1], 10.0 ** (d / 40.0)))


def _nn(v, default=0.0) -> float:
    return default if v is None else float(v)


def _median(xs: list, default: float) -> float:
    xs = sorted(x for x in xs if x is not None)
    return xs[len(xs) // 2] if xs else default


def select_model(mt: dict | None, bpm: float) -> dict:
    """The learned near-tempo pool, or the prior built with THIS humanizer's std scale (its histograms then describe what is drawn)."""
    return M.model_for_bpm(mt, bpm) if mt else M.prior_model(bpm, std_scale=STD_SCALE)


def swing_ms_of(pool: dict, s16_ms: float) -> float:
    """Pool median of the per-song drums swing ratios -> odd-8th offset in ms at this tempo (d_f16 = 2 (r - 1) / (r + 1))."""
    r = pool["swing_ratios_drums"].get("0.5")
    if r is None:
        r = pool["streams"]["hat"]["swing"]["ratio"] or 1.0
    return 2.0 * (r - 1.0) / (r + 1.0) * s16_ms


def stream_offset(pool: dict, stream: str, slot: int, swing_ms: float, tag: str) -> float:
    st = pool["streams"][stream]
    i = slot % SLOTS
    resid = _nn(st["slot_resid_mean_ms"][i])
    std = _nn(st["slot_std_ms"][i], _median(st["slot_std_ms"], 8.0)) * STD_SCALE
    return resid + (swing_ms if i in M.ODD_8TH else 0.0) + std * z(tag)


# --------------------------------------------------------------------------------------------- variation on repeats ----
def _violations(mel_notes: list, bass_notes: list) -> int:
    """Bass-melody parallel perfects (validators' rule, melody note sounding at each bass onset) + unresolved melodic leaps."""
    mel = sorted(mel_notes, key=lambda n: n["slot"])
    n_par, prev = 0, None
    for b in sorted(bass_notes, key=lambda n: n["slot"]):
        m = BL.sounding(mel, b["slot"])
        if prev is not None and m is not None and prev[1] is not None and BL.is_parallel_perfect(prev[0], prev[1], b["pitch"], m):
            n_par += 1
        prev = (b["pitch"], m)
    return n_par + MEL.unresolved_leaps([n["pitch"] for n in mel])


def _rephrase_melody(models: dict, L: dict, lab: str, tonic: int, mode: str, rtag: str) -> tuple[list, list]:
    """Re-draw the non-skeleton onsets and the non-chord-tone choices of every phrase; skeleton (slots, pitches, suspension
    decisions) identical to the first occurrence. Reject-and-resample (REPHRASE_TRIES tag suffixes) against the label's
    (unchanged) bass line: the attempt with the fewest bass-melody parallels + unresolved leaps wins (first on ties)."""
    harm, lp = L["harmony"], L["plan"]
    notes, tries = [], []
    for ph, hp, mph in zip(lp["phrases"], harm["phrases"], L["melody"]["phrases"]):
        if not mph.get("skeleton"):
            continue
        b0, Lslots = ph["start_bar"], mph["L"]
        change, cad_slot, skel_pos = mph["change_slots"], mph["cad_slot"], mph["skeleton"]["slots"]
        otag, ntag = f"{L['tag']}|melody|{ph['index']}", f"{rtag}|melody|{ph['index']}"
        s0, s1 = b0 * SLOTS, (b0 + ph["n_bars"]) * SLOTS
        bass_in = [n for n in L["bass"]["notes"] if s0 <= n["slot"] < s1]

        def chord_at(s: int) -> str:
            return harm["beat_chords"][b0 + s // SLOTS][(s % SLOTS) // 4]
        best = None
        for t in range(REPHRASE_TRIES):
            tt = f"{ntag}|try{t}"
            rhythm = MEL.phrase_rhythm(models["melody"], Lslots, change, cad_slot, MEL.DENSITY.get(lab, 0.75), tt)
            weak = {s for s in rhythm if s % 8 != 0 and s not in change and s < cad_slot and chord_at(s) != "N"}
            onsets = sorted(set(skel_pos) | weak)
            raw = MEL.fill_weak(onsets, {"pitches": mph["skeleton"]["pitches"]}, skel_pos, chord_at, set(change), mph["skeleton"]["floor"], tonic, mode, tt, susp_tag=otag)
            cand = MEL.finalize_notes(raw, Lslots, chord_at, ph["index"])
            for n in cand:
                n["slot"] += s0
            score = _violations(cand, bass_in)
            if best is None or score < best[0]:
                best = (score, cand, t + 1)
            if score == 0:
                break
        notes += best[1]
        tries.append({"phrase": ph["index"], "tries": best[2], "violations": best[0]})
    return notes, tries


def vary_recurrences(models: dict, plan: dict, labels: dict, tonic: int, mode: str, bpm: float, tag: str, vel: dict) -> tuple[dict, list, dict]:
    """-> (content by section index, arrangement per_bar with re-drawn fills, info). Recurrence 0 of a label is untouched."""
    gm = models["groove"]["model"] if "model" in models["groove"] else models["groove"]
    arr = [dict(a) for a in plan["arrangement"]["per_bar"]]
    nb = plan["form"]["bars_per_section"]
    seen: dict = {}
    by_section, info = {}, {}
    for sec in plan["form"]["sections"]:
        lab, idx = sec["label"], sec["index"]
        r = seen.get(lab, 0)
        seen[lab] = r + 1
        L = labels[lab]
        if r == 0:
            by_section[idx] = L
            info[str(idx)] = {"label": lab, "recurrence": 0, "tag": L["tag"], "varied": False}
            continue
        rtag = f"{L['tag']}|rec={r}"
        groove = [dict(g, hat=DR.draw_row(DR.row_for(gm["hat_given_kick_snare"], f"{g['kick']}|{g['snare']}"), f"{rtag}|groove|bar{i}|hat|{g['kick']}|{g['snare']}"))
                  for i, g in enumerate(L["groove_bars"])]
        keys, comp = VO.keys_events(L["harmony"]["beat_chords"], L["voicings_by_slot"], bpm, rtag, models.get("comping"), vel["keys"], [[] for _ in range(L["harmony"]["n_bars"])])
        mel_notes, mel_tries = _rephrase_melody(models, L, lab, tonic, mode, rtag)
        pool = models["fill_pool"]
        e = pool[int(draw_from({f"{j:03d}": float(x["count"]) for j, x in enumerate(pool)}, f"{tag}|fill|section{idx}|rec={r}"))]
        fb = sec["start_bar"] + nb - 1
        if arr[fb].get("fill"):
            arr[fb]["fill"] = {"snare": int(e["snare"]), "hat": int(e["hat"])}
        L2 = dict(L, groove_bars=groove, keys=keys, comping_rhythm=comp, melody={"notes": mel_notes, "phrases": L["melody"]["phrases"]})
        by_section[idx] = L2
        info[str(idx)] = {"label": lab, "recurrence": r, "tag": rtag, "varied": True,
                          "n_hat_bars_changed": sum(1 for a, b in zip(L["groove_bars"], groove) if a["hat"] != b["hat"]),
                          "n_melody_notes": [len(L["melody"]["notes"]), len(mel_notes)], "melody_rephrase": mel_tries, "n_keys_notes": [len(L["keys"]), len(keys)],
                          "fill": arr[fb].get("fill"), "comping_templates": [c["template"] for c in comp]}
    return by_section, arr, info


# ------------------------------------------------------------------------------------------------- apply (flattened) ----
def _phrase_of(song: dict, bar: int):
    for ph in song["phrases"]:
        if ph["start_bar"] <= bar < ph["start_bar"] + ph["n_bars"]:
            return ph
    return None


def _cresc(song: dict, bar: int) -> float:
    ph = _phrase_of(song, bar)
    if not ph or ph["n_bars"] < 2:
        return 0.0
    return CRESC_MAX * (bar - ph["start_bar"]) / float(ph["n_bars"] - 1)


def _drum_class_db(pool: dict, slot: int) -> float:
    vals = [pool["streams"][s]["vel_by_beat_class_db"].get(M.beat_class(slot)) for s in M.DRUM_STREAMS]
    return 0.5 * _median(vals, 0.0)


def _hyper_db(pool: dict, stream: str | None, bar: int) -> float:
    if stream:
        return _nn(pool["streams"][stream]["vel_by_bar_mod8_db"][bar % 8])
    return 0.5 * _median([pool["streams"][s]["vel_by_bar_mod8_db"][bar % 8] for s in M.DRUM_STREAMS], 0.0)


def _timing(song: dict, pool: dict, tag: str, s16_ms: float) -> dict:
    clip = CLIP_F16 * s16_ms
    swing = swing_ms_of(pool, s16_ms)
    lag = pool["bass_kick_lag_ms"]
    kick_off: dict = {}
    for h in song["drums"]:
        st = DRUM_STREAM.get(h["pitch"], "hat")
        h["offset_ms"] = max(-clip, min(clip, stream_offset(pool, st, h["slot"], swing, f"{tag}|t|drums|{h['slot']}|{h['pitch']}")))
        if st == "kick":
            kick_off[h["slot"]] = h["offset_ms"]
    for n in song["bass"]:
        t = f"{tag}|t|bass|{n['slot']}"
        if n["slot"] in kick_off:
            off = kick_off[n["slot"]] + _nn(lag["mean"]) + min(LAG_STD_CAP_MS, _nn(lag["std"], 0.0)) * z(t)
            n["follows_kick"] = True
        else:
            off = stream_offset(pool, "bass", n["slot"], swing, t)
        n["offset_ms"] = max(-clip, min(clip, off))
    for n in song["keys"]:
        late = KEYS_LATE_MS[0] + (KEYS_LATE_MS[1] - KEYS_LATE_MS[0]) * u(f"{tag}|t|keys|{n['slot']}")
        n["offset_ms"] = max(-clip, min(clip, late))
    mel = sorted(song["melody"], key=lambda n: n["slot"])
    for n in mel:
        n["offset_ms"] = MEL_MEAN_MS + MEL_STD_MS * z(f"{tag}|t|melody|{n['slot']}")
    for ph in song["phrases"]:
        s0, s1 = ph["start_bar"] * SLOTS, (ph["start_bar"] + ph["n_bars"]) * SLOTS
        inph = [n for n in mel if s0 <= n["slot"] < s1]
        for k, add in zip(inph[-2:][::-1], RIT_MS[::-1]):
            k["offset_ms"] += add
            k["ritardando"] = True
    for n in mel:
        n["offset_ms"] = max(-clip, min(clip, n["offset_ms"]))
    for stem in ("drums", "bass", "keys", "melody"):  # the song cannot start before t = 0 (the serializer clamps ticks at 0)
        for n in song[stem]:
            n["offset_ms"] = max(n["offset_ms"], -n["slot"] * s16_ms)
    return {"swing_ms": round(swing, 3), "clip_ms": round(clip, 3), "bass_kick_lag_ms": lag, "n_bass_following_kick": sum(1 for n in song["bass"] if n.get("follows_kick"))}


def _dynamics(song: dict, pool: dict, tag: str) -> None:
    kick_slots = {h["slot"] for h in song["drums"] if h["pitch"] == DR.KICK}
    for stem in ("drums", "bass", "keys", "melody"):
        for n in song[stem]:
            slot, bar = n["slot"], n["slot"] // SLOTS
            st = DRUM_STREAM.get(n["pitch"], "hat") if stem == "drums" else ("bass" if stem == "bass" else None)
            metric = _nn(pool["streams"][st]["vel_by_slot_db"][slot % SLOTS], _nn(pool["streams"][st]["vel_by_beat_class_db"].get(M.beat_class(slot)))) if st else _drum_class_db(pool, slot)
            v = float(n["velocity"]) * vel_mult(metric) * vel_mult(_hyper_db(pool, st, bar))
            t = f"{tag}|v|{stem}|{slot}|{n['pitch']}"
            if stem == "drums":
                v += _cresc(song, bar) * (0.5 if st in ("kick", "snare") else 0.0)
                if st == "hat" and slot % 2 == 1:
                    v = GHOST[0] + (GHOST[1] - GHOST[0]) * u(f"{t}|ghost")
                    n["ghost"] = True
                if st == "kick" and slot % 4 != 0 and (slot - 2 in kick_slots or slot - 1 in kick_slots):
                    v = GHOST[0] + (GHOST[1] - GHOST[0]) * u(f"{t}|ghost")
                    n["ghost"] = True
            else:
                v += _cresc(song, bar)
                if stem == "melody" and n.get("position") == "peak":
                    v += PEAK_BONUS
            v += VEL_JITTER * z(t)
            n["velocity_base"] = int(n["velocity"])
            n["velocity"] = int(max(1, min(127, round(v))))


def _articulation(song: dict, pool: dict, tag: str) -> None:
    mel = sorted(song["melody"], key=lambda n: n["slot"])
    for ph in song["phrases"]:
        s0, s1 = ph["start_bar"] * SLOTS, (ph["start_bar"] + ph["n_bars"]) * SLOTS
        inph = [n for n in mel if s0 <= n["slot"] < s1]
        for i, n in enumerate(inph[:-1]):
            ioi = inph[i + 1]["slot"] - n["slot"]
            f = MEL_LEGATO[0] + (MEL_LEGATO[1] - MEL_LEGATO[0]) * u(f"{tag}|a|melody|{n['slot']}")
            n["dur16"] = round(max(0.5, ioi * (BREATH if i == len(inph) - 2 else f)), 4)
    onsets = sorted({n["slot"] for n in song["keys"]})
    nxt = {s: (onsets[i + 1] if i + 1 < len(onsets) else s + SLOTS) for i, s in enumerate(onsets)}
    for n in song["keys"]:
        ioi = min(nxt[n["slot"]] - n["slot"], SLOTS - n["slot"] % SLOTS) if nxt[n["slot"]] > n["slot"] else 1
        if song["arrangement"][n["slot"] // SLOTS].get("hold"):
            continue
        sus = COMP_SUSTAIN[0] + COMP_SUSTAIN[1] * (u(f"{tag}|a|keys|{n['slot']}") ** COMP_SUSTAIN[2])
        n["dur16"] = round(max(0.5, ioi * sus), 4)
    bass = sorted(song["bass"], key=lambda n: n["slot"])
    hist = pool["bass_duration"]["hist"]
    for i, n in enumerate(bass):
        if song["arrangement"][n["slot"] // SLOTS].get("hold"):
            continue
        ioi = (bass[i + 1]["slot"] - n["slot"]) if i + 1 < len(bass) else float(n["dur16"])
        q = M.hist_quantile(hist, 0.0, 1.0, u(f"{tag}|a|bass|{n['slot']}")) if sum(hist) else 0.7
        frac = max(BASS_DUR_CLIP[0], min(BASS_DUR_CLIP[1], _nn(q, 0.7)))
        if n["slot"] % SLOTS not in M.EVEN_8TH:
            frac *= STACCATO
        n["dur16"] = round(max(0.5, ioi * frac), 4)


def _open_hats(song: dict, tag: str) -> int:
    n = 0
    for h in song["drums"]:
        if h["pitch"] == DR.HAT and h["slot"] % SLOTS == OPEN_HAT_SLOT and u(f"{tag}|openhat|bar{h['slot'] // SLOTS}") < P_OPEN_HAT:
            h["pitch"], h["cls"] = OPEN_HAT, "hat_open"
            n += 1
    return n


def offset_stats(song: dict, s16_ms: float) -> dict:
    out = {}
    groups = {"kick": [], "snare": [], "hat": [], "bass": [n["offset_ms"] for n in song["bass"]], "keys": [n["offset_ms"] for n in song["keys"]], "melody": [n["offset_ms"] for n in song["melody"]]}
    for h in song["drums"]:
        groups[DRUM_STREAM.get(h["pitch"], "hat")].append(h["offset_ms"])
    for k, xs in groups.items():
        if not xs:
            out[k] = {"n": 0}
            continue
        m = sum(xs) / len(xs)
        sd = math.sqrt(max(0.0, sum(x * x for x in xs) / len(xs) - m * m))
        out[k] = {"n": len(xs), "mean_ms": round(m, 3), "std_ms": round(sd, 3), "min_ms": round(min(xs), 3), "max_ms": round(max(xs), 3), "mean_f16": round(m / s16_ms, 5), "std_f16": round(sd / s16_ms, 5)}
    return out


def apply(song: dict, pool: dict, tag: str) -> dict:
    """Mutates the flattened song (offset_ms, velocity, dur16, open hats). Returns the per-song humanize manifest block."""
    s16_ms = 60000.0 / float(song["bpm"]) / 4.0
    n_open = _open_hats(song, tag)
    timing = _timing(song, pool, tag, s16_ms)
    _dynamics(song, pool, tag)
    _articulation(song, pool, tag)
    vel = {}
    for stem in ("drums", "bass", "keys", "melody"):
        vs = [n["velocity"] for n in song[stem]]
        if vs:
            m = sum(vs) / len(vs)
            vel[stem] = {"n": len(vs), "mean": round(m, 2), "std": round(math.sqrt(max(0.0, sum(v * v for v in vs) / len(vs) - m * m)), 3), "min": min(vs), "max": max(vs)}
    return {"model": {"variant": pool["variant"], "target_bpm": pool.get("target_bpm"), "n_songs": pool["n_songs"], "songs": pool["songs"]},
            "params": {"clip_f16": CLIP_F16, "std_scale": STD_SCALE, "keys_late_ms": list(KEYS_LATE_MS), "melody_ms": [MEL_MEAN_MS, MEL_STD_MS], "ritardando_ms": list(RIT_MS),
                       "lag_std_cap_ms": LAG_STD_CAP_MS, "cresc_max": CRESC_MAX, "ghost": list(GHOST), "peak_bonus": PEAK_BONUS, "vel_jitter": VEL_JITTER, "db_clip": DB_CLIP,
                       "mult_clip": list(MULT_CLIP), "p_open_hat": P_OPEN_HAT, "melody_legato": list(MEL_LEGATO), "breath": BREATH, "comp_sustain": list(COMP_SUSTAIN),
                       "bass_dur_clip": list(BASS_DUR_CLIP), "staccato": STACCATO, "z": "Box-Muller on two SHA-256 uniforms, clipped +/-3"},
            "timing": timing, "s16_ms": round(s16_ms, 4), "offset_stats": offset_stats(song, s16_ms), "velocity_stats": vel, "n_open_hats": n_open,
            "n_ghost": sum(1 for h in song["drums"] if h.get("ghost"))}
