#!/usr/bin/python3
"""v6 rules — harmony_rules_v6: functional (common-key) chord streams + the corpus Markov chain in the harmony_v5 schema.

created: 2026-10-04
milestone: M-V6-RULES-1/audio-harmony

  /usr/bin/python3 scripts/v6/rules/harmony_rules_v6.py [--chords-dir data/v6/rules/chords] [--v5-rules-dir data/v5/rules]
                                                         [--v6-out-dir data/v6/rules/harmony]

Inputs: data/v6/rules/chords/<sha16>/chords_v6.json (scripts/v6/rules/chords_v6.py: absolute-root beat chord stream from
the first downbeat + the key block of scripts/v6/rules/key_v6.py) for every song of data/v6/corpus/corpus_manifest_v6.json,
in manifest priority order (the order every v5 consumer uses).
  transpose   functional state = f"{(root - tonic) % 12}:{quality}" / "N"  (harmony_v5.analyse_song's convention).
  per song    data/v5/rules/per_song_c84/<sha16>/harmony_v5.json in the harmony_v5 per-song schema (chord_stream entries
              carry beat / root / quality / sim / state / energy; segments; key; n_beats; n_segments; exclusion_rule ...),
              audio provenance in place of the MIDI fields (values disclose the v6 source; key SET is a superset).
  chain       scripts.v5.harmony_v5.markov(streams, segs) — the v5 builder itself (beat-level counts with self-transitions,
              row-normalised with unseen rows uniform, segment-level counts, stationary distribution by power iteration,
              the pre-declared degeneracy test and verdict) — plus the v5 top-level keys (schema_version, cycle, env_pin_sha256,
              gate, per_song, qualities, notes). Written to data/v5/rules/harmony_markov_v5_full.json (the path
              scripts/v6/gen/fixtures.load_models reads) and copied under data/v6/rules/harmony/.
  gate        every song with a chords file is `landed`; `used` = landed minus the PRE-DECLARED exclusions: N fraction
              > MAX_N_FRACTION (0.60) or key confidence < key_v6.LOW_KEY_CONFIDENCE (0.02). Exclusions are disclosed in
              gate.excluded_v6 with the reason; per-song N fraction and key confidence are recorded in gate and per_song.
  LOO         leave-one-song-out cross-entropy (bits/chord) of each used song's beat-level AND segment-level state sequence
              under the chain trained on the other songs (add-ALPHA smoothing over the union state set, ALPHA = 0.5) vs the
              uniform chain log2(S); mean and gap reported (the composition-side scorecard metric later).
No PRNG; sorted-key atomic JSON with schema_version; 7-key env pin; /usr/bin/python3 guard.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

_WS = Path(__file__).resolve().parent.parent.parent.parent
if str(_WS) not in sys.path:
    sys.path.insert(0, str(_WS))
from scripts.v6.v6_data_common import ENV_PIN_SHA256, MANIFEST_V6, WS, interpreter_guard, pin_env, read_json, sha256_file, write_json_atomic  # noqa: E402

pin_env()
interpreter_guard()
import numpy as np  # noqa: E402
from scripts.v5.harmony_v5 import DEGENERACY, MIN_SONGS, QUALITY_ORDER, markov  # noqa: E402  READ-ONLY (chain builder + thresholds)
from scripts.v6.rules.key_v6 import LOW_KEY_CONFIDENCE  # noqa: E402

CYCLE = 600  # v6 rules cycle stamp (v5 chain files carried the c8x cycle numbers)
CHORDS_DIR = WS / "data/v6/rules/chords"
V5_RULES = WS / "data/v5/rules"
V6_OUT = WS / "data/v6/rules/harmony"
CHAIN_NAME, PER_SONG_SUBDIR = "harmony_markov_v5_full.json", "per_song_c84"
MAX_N_FRACTION = 0.60
ALPHA = 0.5
HARMONY_STEMS = ("other", "bass", "vocals")


def manifest_order() -> list[str]:
    man = read_json(MANIFEST_V6)
    return [s["sha16"] for s in sorted(man["songs"], key=lambda s: s["v5_priority_rank"])]


def functional_state(root, quality: str, tonic: int) -> str:
    return "N" if root is None else f"{(int(root) - int(tonic)) % 12}:{quality}"


def segments_of(stream: list) -> list:
    segs = []
    for e in stream:
        if segs and segs[-1]["state"] == e["state"]:
            segs[-1]["n_beats"] += 1
        else:
            segs.append({"state": e["state"], "start_beat": e["beat"], "n_beats": 1})
    return segs


def per_song_record(rec: dict, chords_path: Path) -> dict:
    """harmony_v5 per-song schema from a chords_v6 record (audio provenance in the MIDI fields' places)."""
    tonic = int(rec["key"]["tonic"])
    stream = [{"beat": e["beat"], "root": e["root"], "quality": e["quality"], "sim": e["sim"], "margin_root": e["margin_root"],
               "state": functional_state(e["root"], e["quality"], tonic), "energy": e["rms_db"]} for e in rec["chords"]["chord_stream"]]
    segs = segments_of(stream)
    n_n = sum(1 for e in stream if e["state"] == "N")
    key = {"tonic": tonic, "tonic_name": rec["key"]["tonic_name"], "mode": rec["key"]["mode"], "corr": rec["key"]["corr"], "confidence": rec["key"]["confidence"],
           "mode_margin": rec["key"]["mode_margin"], "modulation_flag": rec["key"]["track"]["modulation_flag"], "method": rec["key"]["method"]}
    return {"schema_version": 1, "cycle": CYCLE, "sha16": rec["sha16"], "title": rec.get("title"), "bpm_v5": float(rec["bpm"]),
            "midi_dir": None, "source": {"kind": "audio", "chords_file": str(chords_path.relative_to(WS)), "chords_sha256": sha256_file(chords_path),
                                         "generator": "scripts/v6/rules/chords_v6.py + key_v6.py + harmony_rules_v6.py", "stems_sha256": rec.get("inputs_sha256")},
            "env_pin_sha256": ENV_PIN_SHA256, "stems": HARMONY_STEMS,
            "per_stem": {s: {"n_notes_midi": None, "note": "audio stem (htdemucs); no symbolic notes"} for s in HARMONY_STEMS},
            "velocity_values_seen": [], "velocity_uniform": None,
            "weighting": "beat-synchronous median CQT chroma of the HPSS-harmonic other+bass+vocals(-6 dB) mix; template cosine + Viterbi (chords_v6)",
            "key": key, "n_beats": len(stream), "n_segments": len(segs),
            "exclusion_rule": {"max_simultaneous_starts_per_stem": None, "excluded_beats": {}, "n_excluded_beats": 0, "n_beats_in_stream": len(stream),
                               "pickup_beats_before_first_downbeat_dropped": rec["chords"]["n_pickup_beats_dropped"],
                               "silent_beats_forced_N": rec["chords"]["n_silent_beats"]},
            "grid": {"bpm": rec["grid"]["bpm"], "phase": rec["grid"]["phase"], "hypermeter_offset": rec["grid"]["hypermeter_offset"], "n_beats_grid": rec["grid"]["n_beats"],
                     "beat_convention": rec["grid"]["bar_convention"]},
            "n_fraction": round(n_n / len(stream), 6) if stream else None, "chord_stream": stream, "segments": segs}


def smoothed_log2(seqs: list[list[str]], states: list[str], alpha: float) -> np.ndarray:
    idx = {s: i for i, s in enumerate(states)}
    C = np.full((len(states), len(states)), alpha)
    for seq in seqs:
        for a, b in zip(seq, seq[1:]):
            C[idx[a], idx[b]] += 1
    return np.log2(C / C.sum(axis=1, keepdims=True))


def cross_entropy(seq: list[str], L: np.ndarray, states: list[str]) -> float | None:
    idx = {s: i for i, s in enumerate(states)}
    pairs = list(zip(seq, seq[1:]))
    return None if not pairs else round(float(-np.mean([L[idx[a], idx[b]] for a, b in pairs])), 6)


def loo_cross_entropy(streams: dict, segs: dict) -> dict:
    """Leave-one-song-out bits/chord at beat level and segment (change-only) level, vs the uniform chain."""
    states = sorted({s for seq in streams.values() for s in seq} | {s for seq in segs.values() for s in seq})
    uniform = round(float(np.log2(len(states))), 6)
    per_song = {}
    for s in sorted(streams):
        Lb = smoothed_log2([streams[t] for t in streams if t != s], states, ALPHA)
        Ls = smoothed_log2([segs[t] for t in segs if t != s], states, ALPHA)
        per_song[s] = {"beat_level_bits": cross_entropy(streams[s], Lb, states), "segment_level_bits": cross_entropy(segs[s], Ls, states),
                       "n_beats": len(streams[s]), "n_segments": len(segs[s])}
    Lb_all = smoothed_log2(list(streams.values()), states, ALPHA)
    Ls_all = smoothed_log2(list(segs.values()), states, ALPHA)
    insample = {"beat_level_bits": round(float(np.mean([cross_entropy(streams[s], Lb_all, states) for s in streams])), 6),
                "segment_level_bits": round(float(np.mean([cross_entropy(segs[s], Ls_all, states) for s in segs if len(segs[s]) > 1])), 6)}
    beat = [v["beat_level_bits"] for v in per_song.values() if v["beat_level_bits"] is not None]
    seg = [v["segment_level_bits"] for v in per_song.values() if v["segment_level_bits"] is not None]
    mean_b, mean_s = round(float(np.mean(beat)), 6), round(float(np.mean(seg)), 6)
    return {"n_states": len(states), "alpha": ALPHA, "uniform_bits": uniform, "per_song": per_song,
            "mean_beat_level_bits": mean_b, "gap_beat_level_bits": round(uniform - mean_b, 6),
            "mean_segment_level_bits": mean_s, "gap_segment_level_bits": round(uniform - mean_s, 6),
            "in_sample_all_songs": insample,
            "definition": "leave-one-song-out: chain (add-alpha smoothed over the union state set) trained on the other used songs; cross-entropy = -mean log2 P(x_t | x_{t-1}) bits/chord; uniform = log2(n_states)"}


def functional_summary(mk: dict) -> dict:
    """Human-readable mass of the main functional moves in the segment-level (change-only) matrix."""
    states, Cs = mk["states"], np.asarray(mk["segment_level_counts"], dtype=float)
    idx = {s: i for i, s in enumerate(states)}

    def mass(from_roots, to_roots) -> float:
        src = [idx[s] for s in states if s != "N" and int(s.split(":")[0]) in from_roots]
        dst = [idx[s] for s in states if s != "N" and int(s.split(":")[0]) in to_roots]
        tot = Cs[src, :].sum()
        return round(float(Cs[np.ix_(src, dst)].sum() / tot), 6) if tot > 0 else None
    top = sorted(((int(Cs[i, j]), states[i], states[j]) for i in range(len(states)) for j in range(len(states)) if i != j and Cs[i, j] > 0), reverse=True)[:15]
    return {"V_to_I": mass({7}, {0}), "V_to_vi": mass({7}, {9}), "IV_to_I": mass({5}, {0}), "IV_to_V": mass({5}, {7}), "ii_to_V": mass({2}, {7}), "I_to_IV": mass({0}, {5}),
            "I_to_V": mass({0}, {7}), "vi_to_IV": mass({9}, {5}), "bVII_to_I": mass({10}, {0}),
            "top_segment_transitions": [{"from": a, "to": b, "count": c} for c, a, b in top],
            "root_mass_stationary": {str(r): round(sum(v for s, v in mk["stationary_distribution"].items() if s != "N" and int(s.split(":")[0]) == r), 6) for r in range(12)}}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="v6 functional chord streams + harmony_v5-schema Markov chain from audio chords")
    ap.add_argument("--chords-dir", default=str(CHORDS_DIR))
    ap.add_argument("--v5-rules-dir", default=str(V5_RULES))
    ap.add_argument("--v6-out-dir", default=str(V6_OUT))
    ap.add_argument("--min-songs", type=int, default=MIN_SONGS)
    args = ap.parse_args(argv)
    cd, v5, v6 = (Path(p) if Path(p).is_absolute() else WS / p for p in (args.chords_dir, args.v5_rules_dir, args.v6_out_dir))
    order = manifest_order()
    landed = [s for s in order if (cd / s / "chords_v6.json").exists()]
    recs = {s: read_json(cd / s / "chords_v6.json") for s in landed}
    excluded = {}
    for s in landed:
        nf, kc = recs[s]["chords"]["n_fraction"], recs[s]["key"]["confidence"]
        reasons = ([f"n_fraction {nf} > {MAX_N_FRACTION}"] if nf is not None and nf > MAX_N_FRACTION else []) + \
                  ([f"key_confidence {kc} < {LOW_KEY_CONFIDENCE}"] if kc < LOW_KEY_CONFIDENCE else [])
        if reasons:
            excluded[s] = {"reasons": reasons, "n_fraction": nf, "key_confidence": kc, "title": recs[s].get("title")}
    used = [s for s in landed if s not in excluded]
    gate = {"cycle": CYCLE, "n_landed": len(landed), "landed": landed, "n_blocked_skipped": 0, "blocked_skipped": [], "n_content_blocked_skipped": 0,
            "content_blocked_skipped": [], "content_gate_present": False, "n_used": len(used), "used": used, "min_songs": args.min_songs,
            "source": "audio (data/v6/stems via scripts/v6/rules/chords_v6.py); landed = songs with a chords_v6.json; no tempo/content block applies",
            "exclusion_rule_v6": {"max_n_fraction": MAX_N_FRACTION, "min_key_confidence": LOW_KEY_CONFIDENCE, "rule": "excluded iff n_fraction > 0.60 OR key confidence < 0.02 (pre-declared)"},
            "excluded_v6": excluded, "n_excluded_v6": len(excluded),
            "n_fraction": {s: recs[s]["chords"]["n_fraction"] for s in landed}, "key_confidence": {s: recs[s]["key"]["confidence"] for s in landed},
            "manifest_v6_sha256": sha256_file(MANIFEST_V6)}
    if len(used) < args.min_songs:
        gate["verdict"] = "GATED_INSUFFICIENT_UNBLOCKED_SONGS"
        write_json_atomic(v5 / "harmony_v5_gated.json", gate)
        print(f"GATED: {len(used)} usable songs < {args.min_songs}")
        return 0
    streams, segs, per_song_summary = {}, {}, {}
    for s in used:
        r = per_song_record(recs[s], cd / s / "chords_v6.json")
        for root in (v5 / PER_SONG_SUBDIR, v6 / PER_SONG_SUBDIR):
            write_json_atomic(root / s / "harmony_v5.json", r)
        streams[s] = [e["state"] for e in r["chord_stream"]]
        segs[s] = [g["state"] for g in r["segments"]]
        per_song_summary[s] = {"title": r["title"], "key": r["key"], "n_beats": r["n_beats"], "n_segments": r["n_segments"], "per_stem": r["per_stem"],
                               "n_excluded_beats": 0, "excluded_beat_fraction": 0.0, "bpm_v5": r["bpm_v5"], "n_fraction": r["n_fraction"],
                               "change_rate_per_bar": recs[s]["chords"]["change_rate_per_bar"], "band": recs[s].get("band"),
                               "top_states": sorted(((streams[s].count(st), st) for st in set(streams[s])), reverse=True)[:5]}
        print(f"{s} {str(r['title'])[:26]:26s} key={r['key']['tonic_name']:2s} {r['key']['mode']:5s} beats={r['n_beats']:4d} segs={r['n_segments']:3d} "
              f"N={r['n_fraction']:.3f} top={per_song_summary[s]['top_states'][:3]}")
    mk = markov(streams, segs)
    loo = loo_cross_entropy(streams, segs)
    mk.update({"schema_version": 1, "cycle": CYCLE, "env_pin_sha256": ENV_PIN_SHA256, "gate": gate, "per_song": per_song_summary, "qualities": list(QUALITY_ORDER),
               "notes": ["v6: states from AUDIO chord recognition (scripts/v6/rules/chords_v6.py) on the shared microtiming beat grid; no symbolic transcription",
                         "chain built by scripts.v5.harmony_v5.markov (unchanged builder; degeneracy thresholds identical)",
                         "per-beat confidence (sim, margin_root) is carried in the per-song chord streams"],
               "source": {"generator": "scripts/v6/rules/harmony_rules_v6.py", "chords_dir": str(cd.relative_to(WS)) if str(cd).startswith(str(WS)) else str(cd),
                          "chords_sha256": {s: sha256_file(cd / s / "chords_v6.json") for s in used}},
               "degeneracy_thresholds_source": "scripts/v5/harmony_v5.DEGENERACY", "loo_cross_entropy": loo, "functional_summary": functional_summary(mk)})
    assert mk["degeneracy_thresholds"] == DEGENERACY
    for root in (v5, v6):
        write_json_atomic(root / CHAIN_NAME, mk)
    write_json_atomic(v6 / "loo_cross_entropy_v6.json", dict(loo, schema_version=1, env_pin_sha256=ENV_PIN_SHA256, generator="scripts/v6/rules/harmony_rules_v6.py"))
    summary = {"schema_version": 1, "generator": "scripts/v6/rules/harmony_rules_v6.py", "milestone": "M-V6-RULES-1/audio-harmony", "env_pin_sha256": ENV_PIN_SHA256,
               "n_songs_landed": len(landed), "n_songs_used": len(used), "excluded": excluded,
               "per_song": {s: {"title": recs[s].get("title"), "band": recs[s].get("band"), "bpm": recs[s]["bpm"], "key": f"{recs[s]['key']['tonic_name']} {recs[s]['key']['mode']}",
                                "tonic": recs[s]["key"]["tonic"], "mode": recs[s]["key"]["mode"], "key_confidence": recs[s]["key"]["confidence"],
                                "key_corr": recs[s]["key"]["corr"], "modulation_flag": recs[s]["key"]["track"]["modulation_flag"],
                                "chord_fit_key": f"{recs[s]['key']['chord_fit']['tonic_name']} {recs[s]['key']['chord_fit']['mode']}",
                                "n_fraction": recs[s]["chords"]["n_fraction"], "change_rate_per_bar": recs[s]["chords"]["change_rate_per_bar"],
                                "n_beats": recs[s]["chords"]["n_beats_stream"], "n_bars": recs[s]["grid"]["n_bars_from_first_downbeat"],
                                "mean_sim": recs[s]["chords"]["mean_sim"], "raw_vs_viterbi_disagreement": recs[s]["chords"]["raw_vs_viterbi_disagreement"],
                                "used_in_chain": s in used, "loo_bits": loo["per_song"].get(s)} for s in landed},
               "chain": {"n_states": len(mk["states"]), "degeneracy_verdict": mk["degeneracy_verdict"], "max_stationary_state": mk["max_stationary_state"],
                         "max_stationary_mass": mk["max_stationary_mass"], "qualities_with_count_ge_threshold": mk["qualities_with_count_ge_threshold"],
                         "segment_counts_by_quality": mk["segment_counts_by_quality"], "top_stationary_states": sorted(mk["stationary_distribution"].items(), key=lambda kv: -kv[1])[:12],
                         "path": str((v5 / CHAIN_NAME).relative_to(WS)) if str(v5).startswith(str(WS)) else str(v5 / CHAIN_NAME)},
               "loo_cross_entropy": {k: v for k, v in loo.items() if k != "per_song"}, "functional_summary": mk["functional_summary"],
               "mode_counts": {m: sum(1 for s in landed if recs[s]["key"]["mode"] == m) for m in ("major", "minor")},
               "key_histogram": {k: sum(1 for s in landed if f"{recs[s]['key']['tonic_name']} {recs[s]['key']['mode']}" == k)
                                 for k in sorted({f"{recs[s]['key']['tonic_name']} {recs[s]['key']['mode']}" for s in landed})}}
    write_json_atomic(WS / "data/v6/rules/harmony_v6_summary.json", summary)
    fs = mk["functional_summary"]
    print(f"corpus chain: {len(mk['states'])} states; max stationary {mk['max_stationary_state']}={mk['max_stationary_mass']}; "
          f"qualities>=8 segs {mk['qualities_with_count_ge_threshold']}; verdict {mk['degeneracy_verdict']}; used {len(used)}/{len(landed)} excluded {sorted(excluded)}")
    print(f"LOO bits/chord: beat {loo['mean_beat_level_bits']} (uniform {loo['uniform_bits']}, gap {loo['gap_beat_level_bits']}); "
          f"segment {loo['mean_segment_level_bits']} (gap {loo['gap_segment_level_bits']})")
    print(f"functional: V->I {fs['V_to_I']} IV->I {fs['IV_to_I']} IV->V {fs['IV_to_V']} ii->V {fs['ii_to_V']} V->vi {fs['V_to_vi']} bVII->I {fs['bVII_to_I']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
