#!/usr/bin/python3
"""v6 rules — velocity_v6: velocity_profiles_v5 quantile ladders from the microtiming onset LEVELS of the corpus stems.

created: 2026-10-04
milestone: M-V6-RULES-1/audio-derived-groove-bass-melody

  /usr/bin/python3 scripts/v6/rules/velocity_v6.py [--songs sha16,...] [--out-v5 data/v5/rules/velocity_profiles_v5.json]
      [--out-v6 data/v6/rules/velocity_v6.json]

Levels: the per-onset 30 ms post-onset RMS (dB) of the shared onset cache (scripts/v6/rules/stems_common_v6.py — the same
levels microtiming_v6 pools as relative dB) for kick / snare / hat (drum stem bands), bass (bass stem), 'other' (keys/pads)
and the melody notes of melody_v6 (_pitch/<sha16>_melody.json). Mapping per (song, stream): MIDI velocity linear in dB with
p5 -> 40 and p95 -> 110 (the v5 anchors; v5 interpolated in midrank, v6 in dB so the SHAPE of a song's dynamics survives),
rounded, clipped to [1, 127]; a degenerate stream (p95 - p5 < 1e-6 dB) maps to 80. Ladders (velocity_profiles_v5 schema):
drums[kick|snare|hat][slot16], bass[coincident|other][slot16] (kick within 30 ms), melody[first|peak|last|other] (phrases =
gaps >= 2 beats, as v5), keys[slot16] from the 'other' stream; quantile levels [0, 10, 25, 50, 75, 90, 100] (composer:
drums.sample_velocity / compose_v6.velocity_fns). R1 / R2 diagnostics as velocity_v5 (R1 on >= 80 % of N songs). No PRNG.
"""
from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

_WS = Path(__file__).resolve().parent.parent.parent.parent
if str(_WS) not in sys.path:
    sys.path.insert(0, str(_WS))
from scripts.v6.rules import stems_common_v6 as SC  # noqa: E402  (pins + guard at import)
from scripts.v6.v6_data_common import ENV_PIN_SHA256, WS, read_json, sha256_file, write_json_atomic  # noqa: E402

V_LO, V_HI, P_LO, P_HI = 40.0, 110.0, 5.0, 95.0
DEGENERATE_DB = 1e-6
R1_MIN_SPREAD_DB, R1_MIN_FRAC = 6.0, 0.8
QUANTS = [0, 10, 25, 50, 75, 90, 100]
KICK_COINCIDENT_S = 0.030
PHRASE_GAP_BEATS = 2.0
DRUM_CLASSES = {"kick": (35, 36), "snare": (37, 38, 39, 40), "hat": (42, 44, 46)}
ROUTE2 = {"drums": {"kick": {"on": 110, "off": 85}, "snare": {"on": 110, "off": 85}, "hat": {"even": 90, "odd": 55}},
          "bass": {"coincident": 100, "other": 80}, "melody": {"peak": 105, "other": 85}, "keys": {"all": 90}}
MELODY_DIR = SC.RULES_V6 / "_pitch"
OUT_V5 = WS / "data/v5/rules/velocity_profiles_v5.json"
OUT_V6 = WS / "data/v6/rules/velocity_v6.json"


# -------------------------------------------------------------------------------------------------------- mapping ----
def percentile(xs: list, q: float) -> float:
    s = sorted(float(x) for x in xs)
    pos = (len(s) - 1) * q / 100.0
    lo, hi = int(math.floor(pos)), min(int(math.floor(pos)) + 1, len(s) - 1)
    return s[lo] + (s[hi] - s[lo]) * (pos - lo)


def db_to_velocity(db: float, p5: float, p95: float) -> int:
    """Monotone (non-decreasing) linear-in-dB map: p5 -> 40, p95 -> 110, rounded, clipped to [1, 127]; degenerate -> 80."""
    if p95 - p5 < DEGENERATE_DB:
        return 80
    v = V_LO + (V_HI - V_LO) * (db - p5) / (p95 - p5)
    return int(max(1, min(127, round(v))))


def map_levels(levels: list) -> tuple[list, dict]:
    if not levels:
        return [], {"n": 0, "p5_db": None, "p95_db": None, "spread_db": None, "degenerate": None}
    p5, p95 = percentile(levels, P_LO), percentile(levels, P_HI)
    spread = p95 - p5
    st = {"n": len(levels), "p5_db": round(p5, 6), "p95_db": round(p95, 6), "spread_db": round(spread, 6), "degenerate": spread < DEGENERATE_DB}
    return [db_to_velocity(x, p5, p95) for x in levels], st


def ladder(vals: list) -> dict:
    if not vals:
        return {"n": 0, "mean": None, "std": None, "quantiles": None}
    n = len(vals)
    m = sum(vals) / n
    return {"n": n, "mean": round(m, 4), "std": round(math.sqrt(sum((v - m) ** 2 for v in vals) / n), 4), "quantiles": [round(percentile(vals, q), 2) for q in QUANTS]}


def sample_velocity(lad: dict, u: float) -> int:
    """Generation-time inverse-CDF on the ladder (pure re-implementation of velocity_v5.sample_velocity / drums.sample_velocity)."""
    q = lad.get("quantiles") if lad else None
    if not q:
        return 100
    x = u * 100.0
    if x <= QUANTS[0]:
        return int(max(1, min(127, round(q[0]))))
    for i in range(1, len(QUANTS)):
        if x <= QUANTS[i]:
            t = (x - QUANTS[i - 1]) / (QUANTS[i] - QUANTS[i - 1])
            return int(max(1, min(127, round(q[i - 1] + t * (q[i] - q[i - 1])))))
    return int(max(1, min(127, round(q[-1]))))


# ------------------------------------------------------------------------------------------------------- per song ----
def song_velocities(onsets: dict, melody: dict | None) -> dict:
    """{stream: {"rows": [[slot16, t_s, velocity, bar], ...], "stats": {...}}} + melody [[t_s, midi, velocity]]."""
    out = {}
    for k in ("kick", "snare", "hat", "bass", "other"):
        rows = onsets["streams"].get(k, [])
        vels, st = map_levels([r[4] for r in rows])
        st["r1_spread_ge_6db"] = bool(st["spread_db"] is not None and st["spread_db"] >= R1_MIN_SPREAD_DB)
        out[k] = {"rows": [[int(r[1]), float(r[2]), int(v), int(r[0])] for r, v in zip(rows, vels)], "stats": st}
    notes = (melody or {}).get("notes", [])
    vels, st = map_levels([n["level_db"] for n in notes])
    st["r1_spread_ge_6db"] = bool(st["spread_db"] is not None and st["spread_db"] >= R1_MIN_SPREAD_DB)
    out["melody"] = {"rows": [[float(n["onset_s"]), int(n["midi"]), int(v)] for n, v in zip(notes, vels)], "stats": st, "source_stem": (melody or {}).get("source_stem")}
    return out


def _nearest(sorted_times: list, t: float) -> float:
    import bisect
    i = bisect.bisect_left(sorted_times, t)
    best = min((abs(sorted_times[j] - t) for j in (i - 1, i) if 0 <= j < len(sorted_times)), default=float("inf"))
    return best


def build_profiles(per_song: dict[str, dict], bpms: dict[str, float]) -> tuple[dict, dict]:
    pooled = {"drums": {c: {s: [] for s in range(16)} for c in DRUM_CLASSES}, "bass": {"coincident": {s: [] for s in range(16)}, "other": {s: [] for s in range(16)}},
              "melody": {"first": [], "peak": [], "last": [], "other": []}, "keys": {s: [] for s in range(16)}}
    per_song_fig, r1 = {}, {}
    for sha in sorted(per_song):
        v = per_song[sha]
        kicks = sorted(r[1] for r in v["kick"]["rows"])
        fig = {"drums": {c: {s: [] for s in range(16)} for c in DRUM_CLASSES}, "bass": {s: [] for s in range(16)}, "keys": {s: [] for s in range(16)}, "melody": {s: [] for s in range(16)}, "bpm": bpms[sha]}
        for c in DRUM_CLASSES:
            for slot, _t, vel, _bar in v[c]["rows"]:
                pooled["drums"][c][slot].append(vel); fig["drums"][c][slot].append(vel)
        for slot, t, vel, _bar in v["bass"]["rows"]:
            coin = kicks and _nearest(kicks, t) <= KICK_COINCIDENT_S
            pooled["bass"]["coincident" if coin else "other"][slot].append(vel); fig["bass"][slot].append(vel)
        for slot, _t, vel, _bar in v["other"]["rows"]:
            pooled["keys"][slot].append(vel); fig["keys"][slot].append(vel)
        beat = 60.0 / bpms[sha]
        phrases, cur = [], []
        for t, p, vel in sorted(v["melody"]["rows"]):
            if cur and t - cur[-1][0] >= PHRASE_GAP_BEATS * beat:
                phrases.append(cur); cur = []
            cur.append((t, p, vel))
        if cur:
            phrases.append(cur)
        for ph in phrases:
            peak_i = max(range(len(ph)), key=lambda i: (ph[i][1], -i))
            for i, (t, p, vel) in enumerate(ph):
                pos = "first" if i == 0 else ("last" if i == len(ph) - 1 else ("peak" if i == peak_i else "other"))
                pooled["melody"][pos].append(vel)
        per_song_fig[sha] = {"drums": {c: {str(s): (round(sum(x) / len(x), 2) if x else None) for s, x in d.items()} for c, d in fig["drums"].items()},
                             **{k: {str(s): (round(sum(x) / len(x), 2) if x else None) for s, x in fig[k].items()} for k in ("bass", "keys")}, "bpm": fig["bpm"]}
        r1[sha] = {k: v[k]["stats"] for k in ("kick", "snare", "hat", "bass", "other", "melody")}
    prof = {"drums": {c: {str(s): ladder(pooled["drums"][c][s]) for s in range(16)} for c in DRUM_CLASSES},
            "bass": {k: {str(s): ladder(pooled["bass"][k][s]) for s in range(16)} for k in ("coincident", "other")},
            "melody": {k: ladder(pooled["melody"][k]) for k in ("first", "peak", "last", "other")}, "keys": {str(s): ladder(pooled["keys"][s]) for s in range(16)}}
    n = len(per_song)
    need = int(math.ceil(R1_MIN_FRAC * n)) if n else 0
    r1_pass = {stem: sum(1 for s in r1 if r1[s][stem]["r1_spread_ge_6db"]) for stem in ("kick", "snare", "hat", "bass", "other", "melody")}
    r1_pass["drums"] = min(r1_pass["kick"], r1_pass["snare"], r1_pass["hat"])
    verdict = {stem: (r1_pass[stem] >= need and n > 0) for stem in ("drums", "bass")}

    def mean(xs):
        return (sum(xs) / len(xs)) if xs else None
    slot_mean = {s: mean([x for c in DRUM_CLASSES for x in pooled["drums"][c][s]]) for s in range(16)}
    back = [slot_mean[s] for s in (4, 12) if slot_mean[s] is not None]
    odd = [slot_mean[s] for s in range(1, 16, 2) if slot_mean[s] is not None]
    hat_even = [x for s in range(0, 16, 2) for x in pooled["drums"]["hat"][s]]
    hat_odd = [x for s in range(1, 16, 2) for x in pooled["drums"]["hat"][s]]
    bass_c = [x for s in range(16) for x in pooled["bass"]["coincident"][s]]
    bass_o = [x for s in range(16) for x in pooled["bass"]["other"][s]]
    means = [m for m in slot_mean.values() if m is not None]
    sd = math.sqrt(sum((m - mean(means)) ** 2 for m in means) / len(means)) if means else None
    r2 = {"drums_backbeat_mean_slots_4_12": round(mean(back), 3) if back else None, "drums_odd_slot_mean": round(mean(odd), 3) if odd else None,
          "backbeat_minus_odd": round(mean(back) - mean(odd), 3) if back and odd else None, "backbeat_ge_plus_10": bool(back and odd and (mean(back) - mean(odd)) >= 10.0),
          "hat_even_mean": round(mean(hat_even), 3) if hat_even else None, "hat_odd_mean": round(mean(hat_odd), 3) if hat_odd else None,
          "hat_odd_lower_than_even": bool(hat_even and hat_odd and mean(hat_odd) < mean(hat_even)),
          "bass_kick_coincident_mean": round(mean(bass_c), 3) if bass_c else None, "bass_non_coincident_mean": round(mean(bass_o), 3) if bass_o else None,
          "bass_coincident_gt_non": bool(bass_c and bass_o and mean(bass_c) > mean(bass_o)), "drums_slot_profile_std": round(sd, 3) if sd is not None else None,
          "structureless_std_lt_5": bool(sd is not None and sd < 5.0)}
    man = read_json(SC.STEMS_DIR / "manifest.json")
    v5 = {"schema_version": 1, "cycle": "v6", "agent": "worker", "run_id": "v6-rules-2026-10-04", "milestone": "M-V6-RULES-1/audio-derived-groove-bass-melody",
          "route": "ROUTE_1_STEM_AUDIO", "prereg_path": None, "prereg_sha256": None, "env_pin_sha256": ENV_PIN_SHA256, "songs": sorted(per_song),
          "grid": {"slots_per_bar": 16, "slot": "microtiming_v6 grid slot16 (stems_common_v6 onset cache; downbeat phase + hypermeter offset applied)", "phase_offset_source": "microtiming_v6 grid"},
          "quantile_levels": QUANTS, "sampling": "sample_velocity(ladder, u): interp(u*100, levels, quantiles), u = SHA-256 uniform",
          "drum_classes": {k: list(v) for k, v in DRUM_CLASSES.items()}, "kick_coincident_s": KICK_COINCIDENT_S, "phrase_gap_beats": PHRASE_GAP_BEATS,
          "profiles": prof, "per_song_slot_means": per_song_fig, "per_song_stem_stats": r1,
          "R1": {"min_spread_db": R1_MIN_SPREAD_DB, "songs_passing_per_stem": r1_pass, "drums_bass_pass_ge_4_of_5": verdict, "route_2_fallback_stems": [s for s in ("drums", "bass") if not verdict[s]],
                 "rule_v6": f"drums + bass spread >= {R1_MIN_SPREAD_DB} dB on >= {int(R1_MIN_FRAC * 100)} % of N={n} songs (ceil = {need})", "n_songs": n, "min_songs_required": need,
                 "drums_bass_pass_ge_80pct": verdict},
          "R2": r2, "route_2_ladders_if_needed": ROUTE2, "per_song_separation": {s: dict(man["demucs"], stems_sha256={k: v["sha256"] for k, v in man["songs"][s]["stems"].items()}) for s in sorted(per_song) if s in man["songs"]},
          "mapping": f"velocity = {V_LO:.0f} + {V_HI - V_LO:.0f} * (dB - p5) / (p95 - p5) per (song, stream), round, clip [1, 127]; degenerate (p95 - p5 < {DEGENERATE_DB}) -> 80",
          "level_definition": "20*log10(RMS over 30 ms after the onset) on the stream's stem band (microtiming_v6.levels_db)", "generator": "scripts/v6/rules/velocity_v6.py",
          "source": "audio stems (no symbolic transcription)", "wrapper": {"script": "scripts/v6/rules/velocity_v6.py", "songs": sorted(per_song), "n_songs": n, "r1_min_frac": R1_MIN_FRAC}}
    med = {"drums": {c: [prof["drums"][c][str(s)]["quantiles"][3] if prof["drums"][c][str(s)]["quantiles"] else None for s in range(16)] for c in DRUM_CLASSES},
           "bass": {k: [prof["bass"][k][str(s)]["quantiles"][3] if prof["bass"][k][str(s)]["quantiles"] else None for s in range(16)] for k in ("coincident", "other")},
           "keys": [prof["keys"][str(s)]["quantiles"][3] if prof["keys"][str(s)]["quantiles"] else None for s in range(16)],
           "melody": {k: prof["melody"][k]["quantiles"][3] if prof["melody"][k]["quantiles"] else None for k in ("first", "peak", "last", "other")}}
    v6 = {"schema_version": 1, "generator": "scripts/v6/rules/velocity_v6.py", "milestone": v5["milestone"], "env_pin_sha256": ENV_PIN_SHA256, "n_songs": n, "songs": sorted(per_song),
          "mapping": v5["mapping"], "median_velocity_by_slot": med, "profiles": prof, "R1": v5["R1"], "R2": r2,
          "per_song": {s: {"stats": r1[s], "melody_source_stem": per_song[s]["melody"].get("source_stem"), "bpm": bpms[s]} for s in sorted(per_song)}, "v5_file": str(OUT_V5.relative_to(WS))}
    return v5, v6


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--songs", default=None)
    ap.add_argument("--out-v5", default=str(OUT_V5))
    ap.add_argument("--out-v6", default=str(OUT_V6))
    args = ap.parse_args(argv)
    shas = [s.strip() for s in args.songs.split(",")] if args.songs else SC.corpus_songs()
    per_song, bpms, no_mel = {}, {}, []
    for s in shas:
        on = SC.load_onsets(s, compute=False)
        mp = MELODY_DIR / f"{s}_melody.json"
        if not mp.exists():
            no_mel.append(s)
        per_song[s] = song_velocities(on, read_json(mp) if mp.exists() else None)
        bpms[s] = on["grid"]["bpm"]
    v5, v6 = build_profiles(per_song, bpms)
    if no_mel:
        v5["disclosures"] = v6["disclosures"] = [f"melody notes missing for {no_mel} (run scripts/v6/rules/melody_v6.py first); melody ladders from the other songs"]
    write_json_atomic(args.out_v5, v5)
    write_json_atomic(args.out_v6, v6)
    print(f"N={len(shas)}; R1 {v5['R1']['drums_bass_pass_ge_80pct']} per stem {v5['R1']['songs_passing_per_stem']}; R2 {v5['R2']}")
    for k, row in v6["median_velocity_by_slot"]["drums"].items():
        print(f"  {k} median velocity by slot: {row}")
    print(f"  bass coincident {v6['median_velocity_by_slot']['bass']['coincident']}\n  bass other {v6['median_velocity_by_slot']['bass']['other']}\n  keys {v6['median_velocity_by_slot']['keys']}\n  melody {v6['median_velocity_by_slot']['melody']}")
    print(f"wrote {args.out_v5}, {args.out_v6}" + (f"; melody missing for {len(no_mel)} songs" if no_mel else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
