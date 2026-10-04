#!/usr/bin/python3
"""v6 Phase 2 — compose_v6: theory-grounded symbolic composer CLI (plan -> harmony -> voicing -> melody -> bass -> drums -> validate -> render).

created: 2026-10-04
milestone: M-V6-GEN-2/theory-grounded-composer

  /usr/bin/python3 scripts/v6/gen/compose_v6.py --iteration 1 --seed 0 --fixtures --bars 32 --out data/v6/gen/iteration_01
      [--donors <manifest.json | sha16,sha16,...>] [--bpm 100,120,152] [--rules-dir data/v5/rules]
      [--form-plan data/v5/rules/form_plan_v5.json] [--per-song-dir data/v5/rules/per_song_c84] [--no-render] [--prove-replay] [--keep-per-track]

Per song dir <out>/<song_id>_donor_<donor>/: generated_json/{drums,bass,keys,melody}.json (v5 event format), generated_midi/
<stem>.mid (scripts/v5/midi_from_json_events_v5.serialize, velocities), plan.json, validators.json, ab_mix.wav +
ab_mix.manifest.json (+ ab_mix.replay_proof.json with --prove-replay: a second full compose+render into a mkdtemp must be
byte-identical in JSON, MIDI and WAV). <out>/iteration_rollup.json + validators_table.json aggregate the run.
Every label of the form is composed ONCE (tags key on the label) and repeated literally; the arrangement (mutes, fills,
held final bar) is applied on the flattened song. seed_str = f"gen_v6_song_{N}|donor={donor}|seed={seed}". No PRNG.
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
from scripts.v6.gen import bassline, drums, harmony, melody, planner, validators, voicing
from scripts.v6.gen.fixtures import FIXTURE_DONORS, load_models

GEN_FILES = ("common", "fixtures", "planner", "harmony", "voicing", "melody", "bassline", "drums", "validators", "render", "compose_v6")
MELODY_VEL = {"first": 95, "peak": 105, "last": 90, "other": 85}


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


def compose_labels(models: dict, plan: dict, tonic: int, mode: str, bpm: float, tag: str, vel: dict) -> dict:
    """Stage 1 harmony per label; stage 2 voicings (pass 1 per label, pass 2 with the predecessor sections' final chords as
    entry contexts); stage 3 melody / groove / bass / keys per label. Tags key on the label so repeats reproduce."""
    labels = sorted(set(plan["form"]["labels"]))
    out = {}
    for lab in labels:
        lp = plan["label_plans"][lab]
        ltag = f"{tag}|label={lab}"
        harm = harmony.label_harmony(models["chain"], lp, mode, ltag)
        cad_idx = set()
        for ph in harm["phrases"]:  # the transition INTO a phrase's last slot is its cadence arrival
            last = ph["slots"][-1]
            cad_idx.add(next(i for i, s in enumerate(harm["slots"]) if s["bar"] == last["bar"] and s["beat"] == last["beat"]))
        states = [s["state"] for s in harm["slots"]]
        roots = bassline.root_line(states, tonic)
        out[lab] = {"harmony": harm, "states": states, "root_line": roots, "cadence_flags": [i in cad_idx for i in range(len(states))], "tag": ltag, "plan": lp,
                    "roots_by_slot": {(s["bar"], s["beat"]): r for s, r in zip(harm["slots"], roots) if r is not None}}
    seq = plan["form"]["labels"]
    for lab in labels:
        L = out[lab]
        L["voicings"] = voicing.voice_sequence(L["states"], tonic, mode, L["cadence_flags"], L["root_line"])
    for lab in labels:  # pass 2: junctions
        preds = sorted({seq[i - 1] for i in range(1, len(seq)) if seq[i] == lab})
        ctxs = []
        for pl in preds:
            P = out[pl]
            last = max((i for i, v in enumerate(P["voicings"]) if v["voicing"]), default=None)
            if last is not None:
                ctxs.append({"state": P["states"][last], "voicing": P["voicings"][last]["voicing"], "bass": P["root_line"][last]})
        L = out[lab]
        L["voicings"] = voicing.voice_sequence(L["states"], tonic, mode, L["cadence_flags"], L["root_line"], ctxs)
        L["entry_contexts"] = ctxs
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


def flatten(plan: dict, labels: dict, tonic: int, mode: str, bpm: float, vel: dict, tag: str) -> dict:
    """Song-order symbolic content with the arrangement applied."""
    form, arr = plan["form"], plan["arrangement"]["per_bar"]
    nb = form["bars_per_section"]
    song = {"tonic": tonic, "mode": mode, "bpm": bpm, "n_bars": form["n_bars"], "bars_per_section": nb, "sections": form["sections"], "arrangement": arr,
            "beat_chords": [], "chord_slots": [], "phrases": [], "harmonic_rhythm_planned": [], "melody": [], "bass": [], "keys": [], "drums": [], "groove_bars": []}
    for sec in form["sections"]:
        lab, sb = sec["label"], sec["start_bar"]
        L = labels[lab]
        song["beat_chords"] += [list(r) for r in L["harmony"]["beat_chords"]]
        song["harmonic_rhythm_planned"] += list(L["harmony"]["harmonic_rhythm"])
        song["groove_bars"] += L["groove_bars"]
        for s, v in zip(L["harmony"]["slots"], L["voicings"]):
            song["chord_slots"].append({"bar": s["bar"] + sb, "beat": s["beat"], "state": s["state"], "voicing": v["voicing"], "cost": v["cost"], "section": sec["index"], "label": lab})
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
        t0 = n["slot"] * s16
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


def compose_song(models: dict, song_id: str, donor: str, seed: int, bpm: float, n_bars: int | None) -> dict:
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
    song = flatten(plan, labels, tonic, mode, bpm, vel, tag)
    val = validators.validate(song)
    plan_out = {"schema_version": 1, "seed_str": tag, "song_id": song_id, "donor": donor, "seed": seed, "tempo_bpm": bpm, "tonic": tonic, "mode": mode, "key_source": key_src,
                "form": plan["form"], "ballad": plan["ballad"], "cadence_table": plan["cadence_table"], "harmonic_rhythm": plan["harmonic_rhythm"],
                "label_plans": plan["label_plans"], "arrangement": plan["arrangement"]["info"], "arrangement_per_bar": plan["arrangement"]["per_bar"],
                "phrases": song["phrases"], "chord_slots": song["chord_slots"], "beat_chords": song["beat_chords"],
                "labels": {lab: {"melody_phrases": L["melody"]["phrases"], "comping_rhythm": L["comping_rhythm"], "groove_bars": L["groove_bars"],
                                 "bass": {"n_changes": L["bass"]["n_changes"], "n_forced_onsets": L["bass"]["n_forced_onsets"]}, "root_line": L["root_line"],
                                 "entry_contexts": L["entry_contexts"],
                                 "voicing_cost_total": round(sum(v["cost"]["total_step"] for v in L["voicings"] if v["cost"]), 6)} for lab, L in labels.items()},
                "velocity_source": vel["source"], "model_sources": models["sources"], "model_sha256": models.get("input_sha256", {}), "fixtures_sha256": models.get("fixtures_sha256")}
    return {"song": song, "plan": plan_out, "validators": val, "tag": tag, "bpm": bpm, "tonic": tonic, "mode": mode}


def write_song(res: dict, song_dir: Path, render: bool, keep_per_track: bool) -> dict:
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
    man = {"schema_version": 1, "generator": "theory_grounded_v6", "generator_sha256": generator_sha256(), "seed_str": res["tag"], "tempo_bpm": bpm, "tonic": res["tonic"], "mode": res["mode"],
           "n_bars": song["n_bars"], "form": res["plan"]["form"]["labels"], "json_sha256": json_sha, "midi_sha256": midi_sha, "n_notes": n_notes,
           "serializer": "scripts/v5/midi_from_json_events_v5.py", "model_sources": res["plan"]["model_sources"], "model_sha256": res["plan"]["model_sha256"],
           "fixtures_sha256": res["plan"]["fixtures_sha256"], "validators_all_caps_pass": res["validators"]["all_caps_pass"], "validators_metrics": res["validators"]["metrics"],
           "env_pin_sha256": ENV_PIN_SHA256, "env_pins": dict(PINS), "sampling": "SHA-256 inverse-CDF on seed_str-derived tags (no PRNG)"}
    if render:
        from scripts.v6.gen.render import render_mix
        t0 = time.time()
        info = render_mix(midi_paths, song_dir / "ab_mix.wav", song_dir / "per_track", song["n_bars"] * 4 * 60.0 / bpm, keep_per_track)
        man["render"] = dict(info, wall_s=round(time.time() - t0, 3))
        man["ab_mix_sha256"] = info["ab_mix_sha256"]
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
    ap.add_argument("--keep-per-track", action="store_true")
    ap.add_argument("--prove-replay", action="store_true", help="compose + render a second time into a tempdir; assert byte identity of JSON, MIDI and WAV")
    args = ap.parse_args(argv)
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
    rollup = {"schema_version": 1, "iteration": args.iteration, "seed": args.seed, "generator_sha256": generator_sha256(), "model_sources": models["sources"],
              "model_sha256": models.get("input_sha256", {}), "fixtures_sha256": models.get("fixtures_sha256"), "songs": [], "env_pin_sha256": ENV_PIN_SHA256}
    per_song_val = {}
    for i, donor in enumerate(donors):
        song_id = f"gen_v6_song_{i + 1}"
        bpm, bpm_src = donor_bpm(donor, i, bpms, corpus)
        t0 = time.time()
        res = compose_song(models, song_id, donor, args.seed, bpm, args.bars)
        t_comp = round(time.time() - t0, 3)
        song_dir = out / f"{song_id}_donor_{donor}"
        man = write_song(res, song_dir, not args.no_render, args.keep_per_track)
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
                res2 = compose_song(models, song_id, donor, args.seed, bpm, args.bars)
                man2 = write_song(res2, Path(td) / "song", not args.no_render, False)
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
