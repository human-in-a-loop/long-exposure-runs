#!/usr/bin/python3
"""v6 rules — chords_v6: audio-derived beat-level chord recognition on the shared beat grid (per song).

created: 2026-10-04
milestone: M-V6-RULES-1/audio-harmony

  /usr/bin/python3 scripts/v6/rules/chords_v6.py [--songs sha16,...] [--out-dir data/v6/rules/chords]

Per song (data/v6/stems/<sha16>/{drums,bass,other,vocals}.wav, mono 22.05 kHz; bpm from data/v6/corpus/<sha16>/tempo_v6.json
exactly as microtiming_v6.song_bpm reads it):
  grid      the SAME beat grid as scripts/v6/microtiming_v6.py: its onset_env / band / detect / calibrate / beat_grid /
            assign / choose_phase / hyper_offset are imported and run in the same order on the drum stem (fit_shared_grid),
            so beats, downbeat phase and hypermeter offset are identical to data/v6/rules/microtiming_v6.json per_song.grid
            (asserted and recorded as grid.matches_microtiming). Per-bar kick/snare/hat 16th masks are kept for form_v6.
  audio     harmonic mix = other + bass + vocals at -6 dB (drums excluded) -> librosa.effects.harmonic (HPSS) ->
            librosa.feature.chroma_cqt (hop 512, 36 bins/octave -> 12 chroma) -> beat-synchronous MEDIAN chroma;
            beat RMS (dB) of the harmonic mix for the silence rule.
  chords    85 states: 12 roots x the harmony_v5 QUALITIES (maj min 7 min7 maj7 9 sus) as binary L2 templates + an 'N'
            template with flat energy. Per beat: cosine similarity to every template. Viterbi over the 85 states with
            self-transition SELF_P = 0.85 per beat and the remaining mass uniform over the other states; log-emission =
            sim / TAU (TAU = 0.05), the N template's sim reduced by N_PENALTY = 0.15 (its cosine is a flatness score that
            sits at ~0.7 on leaky real chroma, so without the penalty Viterbi parks on N); beats whose RMS is below the
            song's 95th percentile - SILENCE_DB are forced to 'N'.
            Output: beat-level chord stream (absolute roots, from the first downbeat so beat % 4 == 0 is a downbeat) with
            per-beat confidence (sim of the chosen chord, margin over the best chord with another root), chord-change
            positions, harmonic rhythm (chord onsets per bar), the raw-argmax vs Viterbi disagreement fraction.
  key       scripts/v6/rules/key_v6.annotate (global KK key + 8-bar key track) written into the same per-song file.
Output: data/v6/rules/chords/<sha16>/chords_v6.json (sorted keys, schema_version). No PRNG anywhere; 7-key env pin.
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

_WS = Path(__file__).resolve().parent.parent.parent.parent
if str(_WS) not in sys.path:
    sys.path.insert(0, str(_WS))
from scripts.v6.v6_data_common import ENV_PIN_SHA256, WS, interpreter_guard, pin_env, read_json, write_json_atomic  # noqa: E402

pin_env()
interpreter_guard()
import numpy as np  # noqa: E402
from scripts.v5.harmony_v5 import PC_NAMES, QUALITIES, QUALITY_ORDER  # noqa: E402  READ-ONLY (chord vocabulary)
from scripts.v6 import microtiming_v6 as MT  # noqa: E402  READ-ONLY (shared beat grid)
from scripts.v6.rules import key_v6 as K  # noqa: E402

SR, HOP, BINS_PER_OCTAVE = 22050, 512, 36
VOCALS_GAIN_DB = -6.0
SELF_P, TAU, SILENCE_DB = 0.85, 0.05, 40.0
N_PENALTY = 0.15  # the flat template's cosine is a FLATNESS score (~0.65-0.75 on leaky real chroma); N wins only when flatter than the best chord by this
STEMS_DIR = WS / "data/v6/stems"
OUT_DIR = WS / "data/v6/rules/chords"
MICROTIMING = WS / "data/v6/rules/microtiming_v6.json"
STATES = [(r, q) for r in range(12) for q in QUALITY_ORDER] + [(None, "N")]  # index 84 = N
N_INDEX = len(STATES) - 1


def chord_name(root, quality: str) -> str:
    return "N" if root is None else f"{PC_NAMES[int(root)]}:{quality}"


def templates() -> np.ndarray:
    """(85, 12) L2-normalised templates: harmony_v5 binary chord templates + a flat 'N' template."""
    T = np.zeros((len(STATES), 12))
    for i, (r, q) in enumerate(STATES):
        if r is None:
            T[i, :] = 1.0
        else:
            for iv in QUALITIES[q]:
                T[i, (r + iv) % 12] = 1.0
    return T / np.linalg.norm(T, axis=1, keepdims=True)


TEMPLATES = templates()


# ----------------------------------------------------------------------------------------------------- shared grid ----
def fit_shared_grid(drums: np.ndarray, bpm: float) -> dict:
    """microtiming_v6.analyze_arrays steps (a)-(c) for the drum stem, verbatim order, up to phase + hypermeter offset."""
    env_all = MT.onset_env(drums)
    be = {k: MT.norm(MT.onset_env(MT.band(drums, *MT.BANDS[k]))) for k in MT.BANDS}
    t = {k: MT.detect(be[k]) for k in ("kick", "snare", "hat")}

    def nf(k, frames):
        return be[k][np.clip(frames, 0, be[k].size - 1)]
    keep = {"kick": nf("kick", t["kick"][1]) >= 0.5 * nf("snare", t["kick"][1]),
            "snare": (nf("high", t["snare"][1]) >= 0.15) & (nf("snare", t["snare"][1]) >= 0.6 * nf("kick", t["snare"][1])) & (nf("snare", t["snare"][1]) >= 0.5 * nf("high", t["snare"][1])),
            "hat": nf("hat", t["hat"][1]) >= 0.3 * nf("snare", t["hat"][1])}
    lat = MT.calibrate()
    times = {k: t[k][0][keep[k]] - lat[k] / 1000.0 for k in keep}
    all_drum_t = np.sort(np.concatenate([times[k] for k in times])) if any(times[k].size for k in times) else np.zeros(0)
    beats, _raw, ginfo = MT.beat_grid(env_all, bpm, all_drum_t)
    beats = beats - lat["grid"] / 1000.0
    asg = {k: MT.assign(times[k], beats) for k in times}
    phase, margin, scores = MT.choose_phase(asg["kick"], asg["snare"])
    hoff = MT.hyper_offset(asg["kick"] + asg["snare"] + asg["hat"], phase)
    return {"beats": beats, "phase": int(phase), "phase_margin": margin, "phase_scores": scores, "hypermeter_offset": int(hoff), "info": ginfo, "assigned": asg}


def drum_masks(asg: dict, phase: int, n_bars: int) -> dict:
    """Per stream-bar (bar 0 = first downbeat) 16-bit onset masks (bit j = 16th slot j, groove_v5_v2.bits convention)."""
    out = {k: [0] * n_bars for k in ("kick", "snare", "hat")}
    for k in out:
        for bi, sub, _dev, _dms, status in asg[k]:
            if status != "ok" or bi < phase:
                continue
            bar, slot = (bi - phase) // 4, ((bi - phase) % 4) * 4 + sub
            if 0 <= bar < n_bars:
                out[k][bar] |= 1 << slot
    return out


# ---------------------------------------------------------------------------------------------------------- chroma ----
def harmonic_mix(other: np.ndarray, bass: np.ndarray, vocals: np.ndarray) -> np.ndarray:
    n = min(other.size, bass.size, vocals.size)
    return (other[:n] + bass[:n] + vocals[:n] * (10.0 ** (VOCALS_GAIN_DB / 20.0))).astype(np.float32)


def beat_features(y: np.ndarray, beats: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """(beat_chroma (n_beats, 12) median CQT chroma of the HPSS-harmonic part, beat_rms_db (n_beats,))."""
    import librosa
    harm = librosa.effects.harmonic(y)
    chroma = librosa.feature.chroma_cqt(y=harm, sr=SR, hop_length=HOP, bins_per_octave=BINS_PER_OCTAVE, n_chroma=12)
    rms = librosa.feature.rms(y=harm, frame_length=2048, hop_length=HOP)[0]
    frames = librosa.time_to_frames(beats, sr=SR, hop_length=HOP)
    frames = np.clip(frames, 0, chroma.shape[1] - 1)
    bc = librosa.util.sync(chroma, frames, aggregate=np.median)[:, 1:]  # column 0 = before the first beat
    br = librosa.util.sync(rms[None, :], frames, aggregate=np.mean)[0, 1:]
    return bc.T, 20.0 * np.log10(br + 1e-9)


# ------------------------------------------------------------------------------------------------------- recogniser ----
def similarities(beat_chroma: np.ndarray) -> np.ndarray:
    C = np.asarray(beat_chroma, dtype=float)
    n = np.linalg.norm(C, axis=1, keepdims=True)
    U = np.divide(C, n, out=np.zeros_like(C), where=n > 0)
    return U @ TEMPLATES.T  # (n_beats, 85)


def viterbi(log_emit: np.ndarray, self_p: float = SELF_P) -> np.ndarray:
    """Most likely state path under a uniform-change transition (self_p on the diagonal) — ties -> lowest state index."""
    n, S = log_emit.shape
    log_self, log_other = np.log(self_p), np.log((1.0 - self_p) / (S - 1))
    delta = log_emit[0].copy()
    back = np.zeros((n, S), dtype=int)
    for t in range(1, n):
        best_prev = int(np.argmax(delta))  # argmax returns the first (lowest) index on ties
        stay = delta + log_self
        move = delta[best_prev] + log_other
        use_stay = stay >= move
        back[t] = np.where(use_stay, np.arange(S), best_prev)
        delta = np.where(use_stay, stay, move) + log_emit[t]
    path = np.zeros(n, dtype=int)
    path[-1] = int(np.argmax(delta))
    for t in range(n - 1, 0, -1):
        path[t - 1] = back[t, path[t]]
    return path


def recognise(beat_chroma: np.ndarray, beat_rms_db: np.ndarray | None = None) -> dict:
    """Template sims + Viterbi path + silence rule over ALL grid beats. Returns raw argmax, path, sims, silent mask."""
    sims = similarities(beat_chroma)
    n = sims.shape[0]
    silent = np.zeros(n, dtype=bool)
    if beat_rms_db is not None and n:
        silent = np.asarray(beat_rms_db) < (float(np.percentile(beat_rms_db, 95)) - SILENCE_DB)
    log_emit = sims.copy()
    log_emit[:, N_INDEX] -= N_PENALTY
    log_emit = log_emit / TAU
    log_emit[silent, :] = -1e9
    log_emit[silent, N_INDEX] = 0.0
    path = viterbi(log_emit) if n else np.zeros(0, dtype=int)
    raw = np.argmax(log_emit, axis=1) if n else np.zeros(0, dtype=int)  # penalised, un-smoothed argmax
    return {"sims": sims, "path": path, "raw": raw, "silent": silent}


def chord_stream(rec: dict, phase: int, beat_rms_db: np.ndarray) -> list:
    """Beat-level stream from the first downbeat: beat = grid index - phase (so beat % 4 == 0 is a downbeat)."""
    sims, path = rec["sims"], rec["path"]
    out = []
    for gi in range(phase, len(path)):
        s = int(path[gi])
        root, q = STATES[s]
        sim = float(sims[gi, s])
        if root is None:
            margin = float(sim - np.max(sims[gi, :N_INDEX])) if N_INDEX else 0.0
        else:
            same_root = [i for i, (r, _q) in enumerate(STATES) if r == root]
            other = [i for i, (r, _q) in enumerate(STATES) if r is not None and r != root]
            margin = float(np.max(sims[gi, same_root]) - np.max(sims[gi, other]))
        out.append({"beat": gi - phase, "grid_beat": gi, "bar": (gi - phase) // 4, "root": root, "root_name": None if root is None else PC_NAMES[root],
                    "quality": q, "chord": chord_name(root, q), "sim": round(sim, 6), "margin_root": round(margin, 6),
                    "rms_db": round(float(beat_rms_db[gi]), 3), "raw_chord": chord_name(*STATES[int(rec["raw"][gi])]), "silent": bool(rec["silent"][gi])})
    return out


def harmonic_rhythm(stream: list) -> dict:
    """Chord onsets per complete bar (a change at beat 0 vs the previous bar's last beat counts as an onset)."""
    n_bars = len(stream) // 4
    per_bar = []
    for b in range(n_bars):
        onsets = 0
        for k in range(4):
            i = 4 * b + k
            if i == 0 or stream[i]["chord"] != stream[i - 1]["chord"]:
                onsets += 1
        per_bar.append(onsets)
    hist = {str(k): per_bar.count(k) for k in range(5)}
    classes = {"1": sum(1 for x in per_bar if x <= 1), "2": sum(1 for x in per_bar if x == 2), "4": sum(1 for x in per_bar if x >= 3)}
    return {"n_bars": n_bars, "onsets_per_bar": per_bar, "histogram": hist, "mean_onsets_per_bar": round(float(np.mean(per_bar)), 6) if per_bar else None,
            "planner_classes_124": classes, "changes_per_bar_mean": round(float(np.mean([max(0, x - 1) for x in per_bar])), 6) if per_bar else None}


def analyse_arrays(drums: np.ndarray, harm: np.ndarray, bpm: float, sha16: str = "synthetic") -> dict:
    """Whole per-song analysis on in-memory mono 22.05 kHz arrays (driver + synthetic tests)."""
    g = fit_shared_grid(drums, bpm)
    beats = g["beats"]
    bc, br = beat_features(harm, beats)
    rec = recognise(bc, br)
    phase = g["phase"]
    stream = chord_stream(rec, phase, br)
    changes = [e["beat"] for i, e in enumerate(stream) if i == 0 or e["chord"] != stream[i - 1]["chord"]]
    n_bars = len(stream) // 4
    counts: dict = {}
    for e in stream:
        counts[e["chord"]] = counts.get(e["chord"], 0) + 1
    out = {"schema_version": 1, "generator": "scripts/v6/rules/chords_v6.py", "milestone": "M-V6-RULES-1/audio-harmony", "env_pin_sha256": ENV_PIN_SHA256,
           "sha16": sha16, "bpm": float(bpm),
           "params": {"sr": SR, "hop": HOP, "bins_per_octave": BINS_PER_OCTAVE, "vocals_gain_db": VOCALS_GAIN_DB, "self_p": SELF_P, "tau": TAU, "silence_db_below_p95": SILENCE_DB, "n_penalty": N_PENALTY,
                      "harmonic_mix": "other + bass + vocals*10^(-6/20); drums excluded; librosa.effects.harmonic (HPSS)", "beat_aggregate": "median chroma / mean RMS per beat",
                      "templates": "harmony_v5 QUALITIES binary L2 templates x 12 roots + flat N (85 states)", "qualities": list(QUALITY_ORDER),
                      "viterbi": "self_p on the diagonal, (1-self_p)/84 elsewhere; log-emission = (cosine_sim - n_penalty*[state==N]) / tau; silent beats forced to N"},
           "grid": {"bpm": float(bpm), "n_beats": int(beats.size), "phase": phase, "phase_margin": g["phase_margin"], "phase_scores": g["phase_scores"],
                    "hypermeter_offset": g["hypermeter_offset"], "first_downbeat_grid_beat": phase, "n_bars_from_first_downbeat": n_bars,
                    "beat_times": [round(float(b), 4) for b in beats], "fit": g["info"], "source": "scripts/v6/microtiming_v6 functions (fit_shared_grid)",
                    "bar_convention": "stream beat = grid beat - phase; bar = beat // 4; form/hypermeter bar = bar - hypermeter_offset"},
           "beat_chroma": [[round(float(x), 4) for x in row] for row in bc], "beat_rms_db": [round(float(x), 3) for x in br],
           "drum_masks": dict(drum_masks(g["assigned"], phase, n_bars), bit_convention="bit j = 16th slot j of the stream bar"),
           "chords": {"vocabulary": [chord_name(r, q) for r, q in STATES], "n_states": len(STATES), "chord_stream": stream, "n_beats_stream": len(stream),
                      "n_pickup_beats_dropped": phase, "n_fraction": round(sum(1 for e in stream if e["quality"] == "N") / len(stream), 6) if stream else None,
                      "n_silent_beats": int(rec["silent"].sum()), "chord_changes_beats": changes, "n_changes": len(changes),
                      "change_rate_per_bar": round(len(changes) / n_bars, 6) if n_bars else None,
                      "raw_vs_viterbi_disagreement": round(float(np.mean([e["raw_chord"] != e["chord"] for e in stream])), 6) if stream else None,
                      "mean_sim": round(float(np.mean([e["sim"] for e in stream])), 6) if stream else None,
                      "mean_margin_root": round(float(np.mean([e["margin_root"] for e in stream if e["quality"] != "N"])), 6) if any(e["quality"] != "N" for e in stream) else None,
                      "chord_counts": dict(sorted(counts.items())), "harmonic_rhythm": harmonic_rhythm(stream)}}
    return K.annotate(out)


def check_microtiming(out: dict, sha16: str) -> dict | None:
    if not MICROTIMING.exists():
        return None
    g = read_json(MICROTIMING)["per_song"].get(sha16, {}).get("grid")
    if not g:
        return None
    same = {"phase": g["phase"] == out["grid"]["phase"], "hypermeter_offset": g["hypermeter_offset"] == out["grid"]["hypermeter_offset"],
            "n_beats": g["n_beats"] == out["grid"]["n_beats"], "bpm": abs(float(g["bpm"]) - out["grid"]["bpm"]) < 1e-6}
    return {"matches": all(same.values()), "fields": same, "microtiming_confidence": g.get("confidence")}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="v6 audio chord recognition per song (shared beat grid)")
    ap.add_argument("--songs", default=None, help="comma-separated sha16 subset (default: every song in data/v6/stems/manifest.json)")
    ap.add_argument("--out-dir", default=str(OUT_DIR))
    ap.add_argument("--force", action="store_true", help="recompute songs whose output exists")
    args = ap.parse_args(argv)
    man = read_json(STEMS_DIR / "manifest.json")
    shas = [s.strip() for s in args.songs.split(",")] if args.songs else sorted(man["songs"])
    out_dir = Path(args.out_dir) if Path(args.out_dir).is_absolute() else WS / args.out_dir
    for sha in shas:
        op = out_dir / sha / "chords_v6.json"
        if op.exists() and not args.force:
            print(f"{sha} exists, skipped", flush=True)
            continue
        t0 = time.time()
        d = STEMS_DIR / sha
        bpm = MT.song_bpm(sha)
        drums = MT.load_mono(d / "drums.wav")
        harm = harmonic_mix(MT.load_mono(d / "other.wav"), MT.load_mono(d / "bass.wav"), MT.load_mono(d / "vocals.wav"))
        out = analyse_arrays(drums, harm, bpm, sha)
        ms = man["songs"][sha]
        out.update({"title": ms.get("title"), "band": ms.get("band"), "inputs_sha256": {k: ms["stems"][k]["sha256"] for k in ("drums", "bass", "other", "vocals")},
                    "wall_s": round(time.time() - t0, 1)})
        out["grid"]["matches_microtiming"] = check_microtiming(out, sha)
        write_json_atomic(op, out)
        c, k = out["chords"], out["key"]
        print(f"{sha} {str(out['title'])[:26]:26s} bpm={bpm:.1f} beats={out['grid']['n_beats']} phase={out['grid']['phase']} hoff={out['grid']['hypermeter_offset']} "
              f"mt_match={(out['grid']['matches_microtiming'] or {}).get('matches')} key={k['tonic_name']} {k['mode']} conf={k['confidence']:.3f} "
              f"N={c['n_fraction']:.3f} chg/bar={c['change_rate_per_bar']:.2f} sim={c['mean_sim']:.3f} raw!=vit={c['raw_vs_viterbi_disagreement']:.3f} wall={out['wall_s']}s", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
