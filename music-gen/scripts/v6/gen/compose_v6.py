#!/usr/bin/python3
"""v6 Phase 2 — compose_v6: theory-grounded symbolic composer CLI (plan -> harmony -> voicing -> melody -> bass -> drums -> validate -> render).

created: 2026-10-04
milestone: M-V6-GEN-2/theory-grounded-composer

  /usr/bin/python3 scripts/v6/gen/compose_v6.py --iteration 1 --seed 0 --fixtures --bars 32 --out data/v6/gen/iteration_01
      [--donors <manifest.json | sha16,sha16,...>] [--bpm 100,120,152] [--rules-dir data/v5/rules]
      [--form-plan data/v5/rules/form_plan_v5.json] [--per-song-dir data/v5/rules/per_song_c84] [--no-render] [--prove-replay] [--keep-per-track]
      [--renderer gm|v6|both]   (Phase 4: v6 = scripts/v6/gen/render_v6/render_song.py — patch pools, expression, mix chain; gm default = unchanged Phase-2 output)
      [--humanize [--microtiming-model data/v6/rules/microtiming_v6.json]]

Per song dir <out>/<song_id>_donor_<donor>/: generated_json/{drums,bass,keys,melody}.json (v5 event format), generated_midi/
<stem>.mid (scripts/v5/midi_from_json_events_v5.serialize, velocities), plan.json, validators.json, ab_mix.wav +
ab_mix.manifest.json (+ ab_mix.replay_proof.json with --prove-replay: a second full compose+render into a mkdtemp must be
byte-identical in JSON, MIDI and WAV). <out>/iteration_rollup.json + validators_table.json aggregate the run.
Every label of the form is composed ONCE (tags key on the label) and repeated literally; the arrangement (mutes, fills,
held final bar) is applied on the flattened song. seed_str = f"gen_v6_song_{N}|donor={donor}|seed={seed}". No PRNG.
Phase 3: --humanize (default OFF, Phase-2 outputs stay byte-identical) applies scripts/v6/gen/humanize.py — variation on
label recurrences before flatten, then microtiming (offset_ms -> start_time; the v5 serializer is tick-level, 480 PPQ),
dynamics and articulation — validated by validators.validate_humanized; writes humanize_manifest.json per song.
"""
from __future__ import annotations

import argparse
import sys
import tempfile
import time
from pathlib import Path

_WS = Path(__file__).resolve().parent.parent.parent.parent
if str(_WS) not in sys.path:
    sys.path.insert(0, str(_WS))
from scripts.v6.gen.common import ENV_PIN_SHA256, INSTRUMENT, PINS, SLOTS, STEMS, WS, read_json, sha_file, sha_text, canonical_json, state_pcs, u, write_json_atomic
from scripts.v6.gen import bassline, drums, harmony, humanize, melody, planner, repair, validators, voicing
from scripts.v6.gen.fixtures import FIXTURE_DONORS, load_models

GEN_FILES = ("common", "fixtures", "planner", "harmony", "voicing", "melody", "bassline", "drums", "validators", "render", "compose_v6", "microtiming_model", "humanize", "repair")
MELODY_VEL = {"first": 95, "peak": 105, "last": 90, "other": 85}
HARMONY_JUNCTION_TRIES = 4  # stage 1: re-sample a label whose first chord leaves a predecessor's 7th unresolvable (seventh_resolvable)
JUNCTION_ITERS = 6  # voicing pass 2: re-voice every label with its neighbours' boundary chords until no voicing changes

def generator_sha256() -> str:
    return sha_text("".join(sha_file(Path(__file__).with_name(f"{n}.py")) for n in GEN_FILES))


def velocity_fns(profiles: dict | None) -> dict:
    prof = profiles["profiles"] if profiles else None

    def keys(tag: str, pos: int) -> int:
        if prof:
            return drums.sample_velocity(prof["keys"].get(str(pos % SLOTS)), u(tag))
        return 88 if pos % SLOTS == 0 else 80

    def bass(tag: str, pos: int, coincident: bool) -> int:
        if prof:
            return drums.sample_velocity(prof["bass"]["coincident" if coincident else "other"].get(str(pos % SLOTS)), u(tag))
        return 100 if coincident else 85

    def mel(tag: str, position: str) -> int:
        if prof:
            return drums.sample_velocity(prof["melody"].get(position), u(tag))
        return MELODY_VEL[position]
    return {"keys": keys, "bass": bass, "melody": mel, "source": "velocity_profiles_v5.json quantile ladders" if prof else "accent table"}


def seventh_resolvable(prev_state: str, next_state: str, tonic: int) -> bool:
    """voicing.seventh_resolvable (the one definition; stage 1 inside a label uses the same test through harmony.resolvable_matrix)."""
    return voicing.seventh_resolvable(prev_state, next_state, tonic)


def compose_labels(models: dict, plan: dict, tonic: int, mode: str, bpm: float, tag: str, vel: dict) -> dict:
    """Stage 1 harmony per label (junction-aware: a label whose first chord makes a predecessor's chord 7th unresolvable is re-sampled
    under tag suffix |hretry<k>, up to HARMONY_JUNCTION_TRIES rounds); stage 2 voicings (pass 1 per label, pass 2 iterated with the
    neighbours' boundary chords as entry / exit contexts); stage 3 melody / groove / bass / keys per label. Tags key on the label so
    repeats reproduce."""
    labels = sorted(set(plan["form"]["labels"]))
    seq = plan["form"]["labels"]
    harms = {lab: harmony.label_harmony(models["chain"], plan["label_plans"][lab], mode, f"{tag}|label={lab}") for lab in labels}
    retries = {lab: 0 for lab in labels}
    for _round in range(HARMONY_JUNCTION_TRIES):
        bad = sorted({seq[i] for i in range(1, len(seq)) if not seventh_resolvable(harms[seq[i - 1]]["slots"][-1]["state"], harms[seq[i]]["slots"][0]["state"], tonic)})
        if not bad:
            break
        for lab in bad:
            retries[lab] += 1
            harms[lab] = harmony.label_harmony(models["chain"], plan["label_plans"][lab], mode, f"{tag}|label={lab}|hretry{retries[lab]}")
    unresolvable = [[seq[i - 1], seq[i]] for i in range(1, len(seq)) if not seventh_resolvable(harms[seq[i - 1]]["slots"][-1]["state"], harms[seq[i]]["slots"][0]["state"], tonic)]
    out = {}
    for lab in labels:
        lp = plan["label_plans"][lab]
        ltag = f"{tag}|label={lab}"
        harm = harms[lab]
        cad_idx = {}
        for ph in harm["phrases"]:  # the transition INTO a phrase's last slot is its cadence arrival (flag = the cadence type; "authentic" is strict)
            last = ph["slots"][-1]
            i = next(i for i, s in enumerate(harm["slots"]) if s["bar"] == last["bar"] and s["beat"] == last["beat"])
            cad_idx[i] = ph["cadence_realized"] if ph["cadence_realized"] != "none" else ph["cadence_planned"]
        states = [s["state"] for s in harm["slots"]]
        roots = bassline.root_line(states, tonic)
        out[lab] = {"harmony": harm, "states": states, "root_line": roots, "cadence_flags": [cad_idx.get(i, False) for i in range(len(states))], "tag": ltag, "plan": lp,
                    "roots_by_slot": {(s["bar"], s["beat"]): r for s, r in zip(harm["slots"], roots) if r is not None},
                    "harmony_junction": {"retries": retries[lab], "unresolvable_junctions": unresolvable}}
    for lab in labels:
        L = out[lab]
        L["voicings"] = voicing.voice_sequence(L["states"], tonic, mode, L["cadence_flags"], L["root_line"])
    def boundary(lab: str, first: bool):
        P = out[lab]
        idx = [i for i, v in enumerate(P["voicings"]) if v["voicing"]]
        if not idx:
            return None
        i = idx[0] if first else idx[-1]
        return {"state": P["states"][i], "voicing": list(P["voicings"][i]["voicing"]), "bass": P["root_line"][i]}
    junction = {"iterations": 0, "converged": False, "max_iterations": JUNCTION_ITERS}
    for it in range(JUNCTION_ITERS):  # pass 2: junctions, Gauss-Seidel to a fixed point (predecessors' finals in, successors' firsts out)
        changed = False
        for lab in labels:
            preds = sorted({seq[i - 1] for i in range(1, len(seq)) if seq[i] == lab})
            succs = sorted({seq[i + 1] for i in range(len(seq) - 1) if seq[i] == lab})
            ctxs = [c for c in (boundary(pl, False) for pl in preds if pl != lab) if c]  # the self-junction is solved inside the DP
            exits = [c for c in (boundary(sl, True) for sl in succs if sl != lab) if c]
            L = out[lab]
            new, cyc = voicing.voice_sequence_cyclic(L["states"], tonic, mode, L["cadence_flags"], L["root_line"], ctxs, exits, lab in preds)
            if [v["voicing"] for v in new] != [v["voicing"] for v in L["voicings"]]:
                changed = True
            L["voicings"], L["entry_contexts"], L["exit_contexts"], L["cyclic"] = new, ctxs, exits, cyc
        junction["iterations"] = it + 1
        if not changed:
            junction["converged"] = True
            break
    for lab in labels:
        out[lab]["junction"] = junction
    for lab in labels:
        L = out[lab]
        harm, lp, ltag = L["harmony"], L["plan"], L["tag"]
        vb = {(s["bar"], s["beat"]): v["voicing"] for s, v in zip(harm["slots"], L["voicings"]) if v["voicing"]}
        mel = melody.label_melody(models, lp, harm, tonic, mode, lab, ltag, L["roots_by_slot"])
        groove_bars = drums.sample_groove_bars(models["groove"], f"{ltag}|groove", harm["n_bars"])
        bass = bassline.label_bass(models["bass"], groove_bars, harm["beat_chords"], mel["notes"], vb, tonic, ltag, vel["bass"], L["roots_by_slot"])
        keys, comp_rhythm = voicing.keys_events(harm["beat_chords"], vb, bpm, ltag, models.get("comping"), vel["keys"], [[] for _ in range(harm["n_bars"])])
        L.update({"voicings_by_slot": vb, "melody": mel, "groove_bars": groove_bars, "bass": bass, "keys": keys, "comping_rhythm": comp_rhythm})
    return out


def flatten(plan: dict, labels: dict, tonic: int, mode: str, bpm: float, vel: dict, tag: str, by_section: dict | None = None) -> dict:
    """Song-order symbolic content with the arrangement applied. by_section {section index: label content} (humanize's varied
    recurrences) overrides the literal per-label repeat."""
    form, arr = plan["form"], plan["arrangement"]["per_bar"]
    nb = form["bars_per_section"]
    song = {"tonic": tonic, "mode": mode, "bpm": bpm, "n_bars": form["n_bars"], "bars_per_section": nb, "sections": form["sections"], "arrangement": arr,
            "beat_chords": [], "chord_slots": [], "phrases": [], "harmonic_rhythm_planned": [], "melody": [], "bass": [], "keys": [], "drums": [], "groove_bars": []}
    for sec in form["sections"]:
        lab, sb = sec["label"], sec["start_bar"]
        L = by_section[sec["index"]] if by_section else labels[lab]
        song["beat_chords"] += [list(r) for r in L["harmony"]["beat_chords"]]
        song["harmonic_rhythm_planned"] += list(L["harmony"]["harmonic_rhythm"])
        song["groove_bars"] += L["groove_bars"]
        for s, v in zip(L["harmony"]["slots"], L["voicings"]):
            song["chord_slots"].append({"bar": s["bar"] + sb, "beat": s["beat"], "state": s["state"], "voicing": v["voicing"], "cost": v["cost"], "section": sec["index"], "label": lab,
                                        "forced": list(v.get("forced") or []), **({"forced_reason": v["forced_reason"]} if v.get("forced") else {})})
        for ph, hp in zip(plan["label_plans"][lab]["phrases"], L["harmony"]["phrases"]):
            song["phrases"].append({"section": sec["index"], "label": lab, "index": ph["index"], "start_bar": sb + ph["start_bar"], "n_bars": ph["n_bars"], "position": ph["position"],
                                    "cadence_planned": hp["cadence_planned"], "cadence_realized": hp["cadence_realized"], "conditioning_ok": hp["conditioning_ok"],
                                    "chords": hp["chords"], "slots": [{"bar": s["bar"] + sb, "beat": s["beat"], "state": s["state"]} for s in hp["slots"]]})
        off = sb * SLOTS
        for stem, notes in (("melody", L["melody"]["notes"]), ("bass", L["bass"]["notes"]), ("keys", L["keys"])):
            for n in notes:
                b = sb + n["slot"] // SLOTS
                a = arr[b]
                if stem in a["mute"]:
                    continue
                if a.get("hold") and (n["slot"] % SLOTS) != 0 and stem in ("bass", "keys"):
                    continue
                n2 = dict(n, slot=n["slot"] + off, section=sec["index"])
                if a.get("hold") and stem in ("bass", "keys"):
                    n2["dur16"] = SLOTS
                    if stem == "bass":
                        st = song["beat_chords"][b][0]
                        n2["pitch"] = bassline.nearest_pitch((state_pcs(st, tonic) or [tonic])[0], n["pitch"], *bassline.REGISTER)
                        n2["cls"] = "root_hold"
                song[stem].append(n2)
    for b, a in enumerate(arr):  # held final bar = ONE chord (the bar's first), so the hold is a single sustained sonority
        if a.get("hold"):
            first = song["beat_chords"][b][0]
            song["beat_chords"][b] = [first] * 4
            song["chord_slots"] = [c for c in song["chord_slots"] if not (c["bar"] == b and c["beat"] > 0)]
            song["harmonic_rhythm_planned"][b] = 1
            for ph in song["phrases"]:
                ph["slots"] = [sl for sl in ph["slots"] if not (sl["bar"] == b and sl["beat"] > 0)] or ph["slots"]
    for n in song["melody"]:
        n["velocity"] = vel["melody"](f"{tag}|melody|vel|{n['slot']}", n["position"])
    song["drums"] = drums.drum_hits(song["groove_bars"], arr, None if not vel.get("profiles") else vel["profiles"], f"{tag}|drums")
    for k in ("melody", "bass", "keys"):
        song[k].sort(key=lambda n: (n["slot"], n["pitch"]))
    return song


def to_events(song: dict, stem: str) -> list:
    beat = 60.0 / song["bpm"]
    s16 = beat / 4
    ev, idx = [], 0
    for n in song[stem]:
        t0 = n["slot"] * s16 + float(n.get("offset_ms", 0.0)) / 1000.0  # offset_ms only present under --humanize
        if stem == "drums":
            t1 = t0 + drums.HIT_S
        elif stem == "bass":
            t1 = t0 + float(n["dur16"]) * s16
        else:
            t1 = t0 + float(n["dur16"]) * s16 - 0.01
        ev.append({"index": idx, "instrument": INSTRUMENT[stem], "pitch": int(n["pitch"]), "start_time": round(t0, 6), "type": "start", "velocity": int(n["velocity"])})
        ev.append({"start_event_index": idx, "end_time": round(max(t1, t0 + 0.02), 6), "type": "end"})
        idx += 1
    return ev


def compose_song(models: dict, song_id: str, donor: str, seed: int, bpm: float, n_bars: int | None, hz: dict | None = None, repair_pass: bool = True) -> dict:
    """hz = {"mt": microtiming_v6.json dict or None (prior), "path", "sha256"} enables Phase-3 humanization. repair_pass=False skips the
    Phase-5 counterpoint repair pass (repair.py; the sweep's "before" table)."""
    tag = f"{song_id}|donor={donor}|seed={seed}"
    key = models["chain"].get("per_song", {}).get(donor, {}).get("key")
    if key:
        tonic, mode, key_src = int(key["tonic"]), str(key.get("mode", "major")), "donor_key_from_chain"
    else:
        tonic, mode, key_src = int(u(f"{tag}|tonic") * 12) % 12, "major", "sha256_derived_(donor not in chain)"
    vel = velocity_fns(models.get("velocity"))
    vel["profiles"] = models.get("velocity")
    plan = planner.build_plan(models, tag, bpm, n_bars)
    labels = compose_labels(models, plan, tonic, mode, bpm, tag, vel)
    # Phase 5: counterpoint repair on the final bass + melody of every label, judged on the flattened song (junctions, mutes, hold)
    reps = repair.repair_labels(models, plan, labels, tonic, mode, lambda: flatten(plan, labels, tonic, mode, bpm, vel, tag)) if repair_pass else None
    hz_out = None
    if hz is not None:
        pool = humanize.select_model(hz.get("mt"), bpm)
        by_section, arr, var_info = humanize.vary_recurrences(models, plan, labels, tonic, mode, bpm, tag, vel)
        plan = dict(plan, arrangement=dict(plan["arrangement"], per_bar=arr))
        if repair_pass:  # pass 2 on the varied recurrences' surface (NCTs / free bass notes only)
            reps = repair.repair_sections(models, plan, by_section, var_info, tonic, mode, lambda: flatten(plan, labels, tonic, mode, bpm, vel, tag, by_section), reps)
        song = flatten(plan, labels, tonic, mode, bpm, vel, tag, by_section)
        hz_out = humanize.apply(song, pool, f"{tag}|humanize")
        hz_out.update({"schema_version": 1, "seed_str": tag, "model_path": hz.get("path"), "model_sha256": hz.get("sha256"), "variation": var_info,
                       "serializer": "scripts/v5/midi_from_json_events_v5.py (start_time seconds -> 480 PPQ ticks, no 16th quantisation)"})
        val = validators.validate_humanized(song, pool)
    else:
        song = flatten(plan, labels, tonic, mode, bpm, vel, tag)
        val = validators.validate(song)
    plan_out = {"schema_version": 1, "seed_str": tag, "song_id": song_id, "donor": donor, "seed": seed, "tempo_bpm": bpm, "tonic": tonic, "mode": mode, "key_source": key_src,
                "form": plan["form"], "ballad": plan["ballad"], "cadence_table": plan["cadence_table"], "harmonic_rhythm": plan["harmonic_rhythm"],
                "label_plans": plan["label_plans"], "arrangement": plan["arrangement"]["info"], "arrangement_per_bar": plan["arrangement"]["per_bar"],
                "phrases": song["phrases"], "chord_slots": song["chord_slots"], "beat_chords": song["beat_chords"],
                "labels": {lab: {"melody_phrases": L["melody"]["phrases"], "comping_rhythm": L["comping_rhythm"], "groove_bars": L["groove_bars"],
                                 "bass": {"n_changes": L["bass"]["n_changes"], "n_forced_onsets": L["bass"]["n_forced_onsets"]}, "root_line": L["root_line"],
                                 "entry_contexts": L["entry_contexts"], "exit_contexts": L["exit_contexts"], "junction": L["junction"], "cyclic": L["cyclic"],
                                 "voicing_cost_total": round(sum(v["cost"]["total_step"] for v in L["voicings"] if v["cost"]), 6),
                                 "voicing_forced_slots": sum(1 for v in L["voicings"] if v.get("forced"))} for lab, L in labels.items()},
                "velocity_source": vel["source"], "model_sources": models["sources"], "model_sha256": models.get("input_sha256", {}), "fixtures_sha256": models.get("fixtures_sha256")}
    if hz_out is not None:
        plan_out["humanize"] = {"model": hz_out["model"], "variation": var_info, "model_path": hz.get("path"), "model_sha256": hz.get("sha256")}
    plan_out["repairs"] = reps if reps is not None else {"schema_version": 1, "passes": [], "n_repairs": 0, "by_rule": {}, "repairs": [], "n_forced": 0, "forced": [], "remaining": [], "skipped": True}
    plan_out["voicing_forced"] = [{"bar": c["bar"], "beat": c["beat"], "state": c["state"], "rules": c["forced"], "reason": c.get("forced_reason")} for c in song["chord_slots"] if c.get("forced")]
    plan_out["realized_keys_violations"] = realized_keys_violations(song)
    plan_out["harmony_junction"] = {lab: L["harmony_junction"] for lab, L in labels.items()}
    return {"song": song, "plan": plan_out, "validators": val, "tag": tag, "bpm": bpm, "tonic": tonic, "mode": mode, "humanize": hz_out}


def realized_keys_violations(song: dict) -> list:
    """Hard voicing rules re-counted on the realised consecutive chord slots of the song (the validators' pairs), with locations."""
    vs = [c for c in song["chord_slots"] if c.get("voicing")]
    bass = sorted(song["bass"], key=lambda n: n["slot"])
    cad = {(p["slots"][-1]["bar"], p["slots"][-1]["beat"]): (p["cadence_realized"] if p["cadence_realized"] != "none" else p["cadence_planned"]) for p in song["phrases"] if len(p["slots"]) >= 2}
    out = []
    for a, b in zip(vs, vs[1:]):
        ba, bb = validators._sounding(bass, a["bar"] * SLOTS + a["beat"] * 4), validators._sounding(bass, b["bar"] * SLOTS + b["beat"] * 4)
        tc = voicing.transition_cost(tuple(a["voicing"]), tuple(b["voicing"]), voicing.chord_tones(a["state"], song["tonic"]), voicing.chord_tones(b["state"], song["tonic"]),
                                     song["tonic"], song["mode"], cad.get((b["bar"], b["beat"]), False), a["state"] == b["state"], ba, bb)
        rules = [k for k in voicing.HARD_RULES if tc[k] > 0]
        if rules:
            out.append({"from": [a["bar"], a["beat"], a["state"]], "to": [b["bar"], b["beat"], b["state"]], "rules": rules, "sections": [a["section"], b["section"]]})
    return out


def write_song(res: dict, song_dir: Path, render: bool, keep_per_track: bool, renderer: str = "gm", iteration: int = 1) -> dict:
    """renderer: gm (Phase-2 FluidR3 shims, manifest unchanged) | v6 (render_v6.render_song: patch pools + mix chain) | both (ab_mix.wav = v6, ab_mix_gm.wav = gm)."""
    from scripts.v5.midi_from_json_events_v5 import serialize as serialize_v5  # READ-ONLY sibling serializer (velocity field)
    song, bpm = res["song"], res["bpm"]
    jd, md = song_dir / "generated_json", song_dir / "generated_midi"
    jd.mkdir(parents=True, exist_ok=True)
    md.mkdir(parents=True, exist_ok=True)
    json_sha, midi_sha, midi_paths, n_notes = {}, {}, {}, {}
    for stem in STEMS:
        ev = to_events(song, stem)
        (jd / f"{stem}.json").write_text(canonical_json(ev, compact=True))
        json_sha[stem] = sha_file(jd / f"{stem}.json")
        n_notes[stem] = len(song[stem])
        if ev:
            serialize_v5(str(jd / f"{stem}.json"), str(md / f"{stem}.mid"), float(bpm), (4, 4))
            midi_sha[stem] = sha_file(md / f"{stem}.mid")
            midi_paths[stem] = md / f"{stem}.mid"
        else:
            midi_sha[stem] = None
            midi_paths[stem] = None
    write_json_atomic(song_dir / "plan.json", res["plan"])
    write_json_atomic(song_dir / "validators.json", res["validators"])
    if res.get("humanize"):
        write_json_atomic(song_dir / "humanize_manifest.json", res["humanize"])
    man = {"schema_version": 1, "generator": "theory_grounded_v6", "generator_sha256": generator_sha256(), "seed_str": res["tag"], "tempo_bpm": bpm, "tonic": res["tonic"], "mode": res["mode"],
           "n_bars": song["n_bars"], "form": res["plan"]["form"]["labels"], "json_sha256": json_sha, "midi_sha256": midi_sha, "n_notes": n_notes,
           "serializer": "scripts/v5/midi_from_json_events_v5.py", "model_sources": res["plan"]["model_sources"], "model_sha256": res["plan"]["model_sha256"],
           "fixtures_sha256": res["plan"]["fixtures_sha256"], "validators_all_caps_pass": res["validators"]["all_caps_pass"], "validators_metrics": res["validators"]["metrics"],
           "env_pin_sha256": ENV_PIN_SHA256, "env_pins": dict(PINS), "sampling": "SHA-256 inverse-CDF on seed_str-derived tags (no PRNG)"}
    if res.get("humanize"):
        man["humanize"] = {"applied": True, "model": res["humanize"]["model"], "model_path": res["humanize"]["model_path"], "model_sha256": res["humanize"]["model_sha256"],
                           "n_varied_sections": sum(1 for v in res["humanize"]["variation"].values() if v["varied"])}
    if render and renderer in ("gm", "both"):
        from scripts.v6.gen.render import render_mix
        t0 = time.time()
        gm_wav, gm_dir = ("ab_mix.wav", "per_track") if renderer == "gm" else ("ab_mix_gm.wav", "per_track_gm")
        info = render_mix(midi_paths, song_dir / gm_wav, song_dir / gm_dir, song["n_bars"] * 4 * 60.0 / bpm, keep_per_track)
        man["render" if renderer == "gm" else "render_gm"] = dict(info, wall_s=round(time.time() - t0, 3))
        man["ab_mix_sha256"] = info["ab_mix_sha256"]
    if render and renderer in ("v6", "both"):
        from scripts.v6.gen.render_v6.render_song import render_song
        t0 = time.time()
        rman = render_song(song_dir, res["plan"]["donor"], iteration, int(res["plan"]["seed"]), keep_per_track=keep_per_track, log=lambda *a: None)
        man["render"] = {"renderer": "v6", "ab_mix_sha256": rman["ab_mix_sha256"], "ab_mix_duration_s": rman["ab_mix_duration_s"], "band": rman["band"], "ensemble": rman["ensemble"],
                         "patches": {r: v.get("patch_id") for r, v in rman["roles"].items()}, "mix_master": rman["mix_master"], "pool_sha256": rman["pool_sha256"],
                         "deterministic_backends_only": rman["deterministic_backends_only"], "manifests": ["patch_plan.json", "mix_manifest.json", "render_manifest.json"],
                         "wall_s": round(time.time() - t0, 3)}
        man["ab_mix_sha256"], man["renderer"] = rman["ab_mix_sha256"], renderer
        if renderer == "both":
            man["ab_mix_gm_sha256"] = man["render_gm"]["ab_mix_sha256"]
    write_json_atomic(song_dir / "ab_mix.manifest.json", man)
    return man


def resolve_donors(spec: str | None, fixtures: bool) -> list:
    if not spec:
        return sorted(FIXTURE_DONORS) if fixtures else []
    p = Path(spec)
    if p.exists():
        d = read_json(p)
        songs = d.get("songs", d if isinstance(d, list) else [])
        return [s.get("donor_song_sha16") or s.get("sha16") for s in songs]
    return [x.strip() for x in spec.split(",") if x.strip()]


def donor_bpm(donor: str, i: int, bpms: list, corpus: Path) -> tuple[float, str]:
    if bpms:
        return float(bpms[i % len(bpms)]), "--bpm"
    tp = corpus / donor / "tempo_v5.json"
    if tp.exists():
        return float(read_json(tp)["bpm_v5"]), str(tp)
    if donor in FIXTURE_DONORS:
        return float(FIXTURE_DONORS[donor]["bpm"]), "fixture"
    return 120.0, "default_120"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="v6 theory-grounded symbolic composer")
    ap.add_argument("--iteration", type=int, default=1)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--donors", default=None, help="donor manifest JSON or comma-separated sha16 list (default with --fixtures: the 3 fixture donors)")
    ap.add_argument("--rules-dir", default="data/v5/rules")
    ap.add_argument("--form-plan", default=None)
    ap.add_argument("--per-song-dir", default=None, help="per-song harmony_v5.json dir (harmonic-rhythm learning); default <rules-dir>/per_song_c84")
    ap.add_argument("--corpus-dir", default="data/v5/corpus")
    ap.add_argument("--fixtures", action="store_true", help="use synthetic models for any rule file that is absent")
    ap.add_argument("--bars", type=int, default=None, help="total bars (multiple of 8); default: form plan length or 32")
    ap.add_argument("--bpm", default=None, help="comma-separated BPM per donor (overrides donor tempo)")
    ap.add_argument("--out", default=None, help="default data/v6/gen/iteration_NN")
    ap.add_argument("--no-render", action="store_true")
    ap.add_argument("--skip-existing", action="store_true", help="resume: skip donors whose song dir already has ab_mix.manifest.json + validators.json")
    ap.add_argument("--keep-per-track", action="store_true")
    ap.add_argument("--prove-replay", action="store_true", help="compose + render a second time into a tempdir; assert byte identity of JSON, MIDI and WAV")
    ap.add_argument("--renderer", choices=["gm", "v6", "both"], default="gm", help="gm: Phase-2 FluidR3 shims (default, outputs unchanged); v6: realistic renderer (render_v6); both: v6 + ab_mix_gm.wav for A/B")
    ap.add_argument("--humanize", action="store_true", help="Phase 3: microtiming / dynamics / repeat variation / articulation (default off)")
    ap.add_argument("--microtiming-model", default="data/v6/rules/microtiming_v6.json", help="learned model (scripts/v6/microtiming_v6.py); absent + --fixtures -> built-in prior")
    args = ap.parse_args(argv)
    hz = None
    if args.humanize:
        mp = Path(args.microtiming_model) if Path(args.microtiming_model).is_absolute() else WS / args.microtiming_model
        if mp.exists():
            hz = {"mt": read_json(mp), "path": str(mp.relative_to(WS)) if str(mp).startswith(str(WS)) else str(mp), "sha256": sha_file(mp)}
        elif args.fixtures:
            hz = {"mt": None, "path": None, "sha256": None}
        else:
            ap.error(f"--humanize: model {mp} not found (run scripts/v6/microtiming_v6.py or pass --fixtures for the prior)")
    out = Path(args.out) if args.out else WS / f"data/v6/gen/iteration_{args.iteration:02d}"
    out = out if out.is_absolute() else WS / out
    rules = Path(args.rules_dir) if Path(args.rules_dir).is_absolute() else WS / args.rules_dir
    models = load_models(rules, args.fixtures, args.form_plan, args.per_song_dir)
    donors = resolve_donors(args.donors, args.fixtures)
    if not donors:
        ap.error("no donors: pass --donors or --fixtures")
    bpms = [float(x) for x in args.bpm.split(",")] if args.bpm else []
    corpus = Path(args.corpus_dir) if Path(args.corpus_dir).is_absolute() else WS / args.corpus_dir
    out.mkdir(parents=True, exist_ok=True)
    rollup = {"schema_version": 1, "iteration": args.iteration, "seed": args.seed, "generator_sha256": generator_sha256(), "model_sources": models["sources"], "humanize": bool(hz),
              "microtiming_model": (hz or {}).get("path"),
              "model_sha256": models.get("input_sha256", {}), "fixtures_sha256": models.get("fixtures_sha256"), "songs": [], "env_pin_sha256": ENV_PIN_SHA256}
    per_song_val = {}
    for i, donor in enumerate(donors):
        song_id = f"gen_v6_song_{i + 1}"
        bpm, bpm_src = donor_bpm(donor, i, bpms, corpus)
        _sd = out / f"{song_id}_donor_{donor}"
        if args.skip_existing and (_sd / "ab_mix.manifest.json").exists() and (_sd / "validators.json").exists() and (args.no_render or (_sd / "ab_mix.wav").exists()):
            _val = per_song_val[song_id] = read_json(_sd / "validators.json"); _rp = _sd / "ab_mix.replay_proof.json"
            rollup["songs"].append({"song_id": song_id, "donor": donor, "dir": str(_sd), "tempo_bpm": bpm, "resumed_from_disk": True, "validators_all_caps_pass": _val.get("all_caps_pass"),
                                    "ab_mix_sha256": read_json(_sd / "ab_mix.manifest.json").get("ab_mix_sha256"), "replay_proof": read_json(_rp).get("verdict") if _rp.exists() else None}); print(f"{song_id} donor={donor} SKIP (existing output reused)"); continue
        t0 = time.time()
        res = compose_song(models, song_id, donor, args.seed, bpm, args.bars, hz)
        t_comp = round(time.time() - t0, 3)
        song_dir = out / f"{song_id}_donor_{donor}"
        man = write_song(res, song_dir, not args.no_render, args.keep_per_track, args.renderer, args.iteration)
        man["tempo_source"] = bpm_src
        entry = {"song_id": song_id, "donor": donor, "dir": str(song_dir.relative_to(WS)) if str(song_dir).startswith(str(WS)) else str(song_dir), "tempo_bpm": bpm, "tonic": res["tonic"], "mode": res["mode"],
                 "n_bars": res["song"]["n_bars"], "form": "".join(res["plan"]["form"]["labels"]), "compose_wall_s": t_comp, "render_wall_s": man.get("render", {}).get("wall_s"),
                 "ab_mix_sha256": man.get("ab_mix_sha256"), "ab_mix_duration_s": man.get("render", {}).get("ab_mix_duration_s"), "validators_all_caps_pass": res["validators"]["all_caps_pass"],
                 "cadences": [(p["cadence_planned"], p["cadence_realized"]) for p in res["song"]["phrases"]]}
        per_song_val[song_id] = res["validators"]
        print(f"{song_id} donor={donor} bpm={bpm:.2f} tonic={res['tonic']} {res['mode']} form={entry['form']} bars={entry['n_bars']} compose={t_comp}s "
              f"render={entry['render_wall_s']}s mix={str(man.get('ab_mix_sha256'))[:12]} caps_pass={res['validators']['all_caps_pass']}")
        if args.prove_replay:
            with tempfile.TemporaryDirectory(prefix="gen_v6_replay_") as td:
                res2 = compose_song(models, song_id, donor, args.seed, bpm, args.bars, hz)
                man2 = write_song(res2, Path(td) / "song", not args.no_render, False, args.renderer, args.iteration)
            same = {"json": man2["json_sha256"] == man["json_sha256"], "midi": man2["midi_sha256"] == man["midi_sha256"],
                    "wav": (man2.get("ab_mix_sha256") == man.get("ab_mix_sha256")) if not args.no_render else None,
                    "plan": canonical_json(res2["plan"]) == canonical_json(res["plan"])}
            verdict = "REPLAY_PROOF_HOLDS" if all(v in (True, None) for v in same.values()) else "REPLAY_PROOF_FAILS"
            write_json_atomic(song_dir / "ab_mix.replay_proof.json", {"schema_version": 1, "verdict": verdict, "equal": same, "run1_ab_mix_sha256": man.get("ab_mix_sha256"),
                                                                        "run2_ab_mix_sha256": man2.get("ab_mix_sha256"), "env_pin_sha256": ENV_PIN_SHA256})
            entry["replay_proof"] = verdict
            print(f"  {verdict} {same}")
        rollup["songs"].append(entry)
    agg = validators.aggregate(per_song_val)
    write_json_atomic(out / "validators_table.json", agg)
    rollup["validators_table"] = {"rows": agg["rows"], "cap_pass_counts": agg["cap_pass_counts"], "songs_all_caps_pass": agg["songs_all_caps_pass"]}
    write_json_atomic(out / "iteration_rollup.json", rollup)
    print(validators.format_table(agg))
    return 0


if __name__ == "__main__":
    sys.exit(main())
