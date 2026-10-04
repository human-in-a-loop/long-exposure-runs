#!/usr/bin/python3
"""v6 rules — shared stem-derived primitives for groove_v6 / bass_pitch_v6 / melody_v6 / velocity_v6.

created: 2026-10-04
milestone: M-V6-RULES-1/audio-derived-groove-bass-melody

  /usr/bin/python3 scripts/v6/rules/stems_common_v6.py [--songs sha16,...] [--workers 2]     # build the onset cache

The FOUR rule scripts need the same per-onset streams the microtiming model was fitted on. data/v6/rules/microtiming_v6.json
stores only sufficient statistics, so this module re-derives the per-onset records by calling scripts/v6/microtiming_v6's OWN
functions (band split, detectors, latency calibration, forced-bpm beat grid + smoothing, slot assignment, downbeat phase,
hypermeter offset, per-(bar, slot) dedup) in the same order — nothing is re-detected differently — and caches them under
data/v6/rules/_onsets/<sha16>.json: {grid: {bpm, phase, hypermeter_offset, beat_times}, streams: {kick, snare, hat, bass,
other: [[bar, slot16, t_s, dev_f16, level_db], ...]}}. The 'other' stream (keys/pads, used only by velocity_v6) runs the same
full-band detector as the bass stem. Consistency with microtiming_v6.json (n_assigned per stream) is recorded per song.

Harmony fallback (DEPENDENCY: replaced by the sibling's data/v6/rules/chords/<sha16>/chords_v6.json when present — see
bass_pitch_v6.chord_stream_for): beat-synchronous chroma (CQT) of other + bass, 24 maj/min templates, Viterbi smoothing, and
a Krumhansl-Schmuckler key on the summed chroma; cached as data/v6/rules/_bassroots/<sha16>.json.
Discipline: /usr/bin/python3 guard (suppressible), 7-key env pins, no PRNG, sorted-key atomic JSON with schema_version.
"""
from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

_WS = Path(__file__).resolve().parent.parent.parent.parent
if str(_WS) not in sys.path:
    sys.path.insert(0, str(_WS))
from scripts.v6.v6_data_common import ENV_PIN_SHA256, WS, interpreter_guard, pin_env, read_json, sha256_file, write_json_atomic  # noqa: E402

pin_env()
interpreter_guard()
import numpy as np  # noqa: E402
from scripts.v6 import microtiming_v6 as MT  # noqa: E402  the SAME grid + detectors (READ-ONLY import)

STEMS_DIR = WS / "data/v6/stems"
RULES_V6 = WS / "data/v6/rules"
RULES_V5 = WS / "data/v5/rules"
ONSETS_DIR = RULES_V6 / "_onsets"
BASSROOTS_DIR = RULES_V6 / "_bassroots"
CHORDS_DIR = RULES_V6 / "chords"
MICROTIMING_JSON = RULES_V6 / "microtiming_v6.json"
PPQ, TICKS_16TH, SLOTS = 480, 120, 16
STREAM_COLUMNS = ["bar", "slot16", "t_s", "dev_f16", "level_db"]
CHROMA_HOP = 512
STAY_P = 0.8          # Viterbi self-transition for the beat-level chord root
N_FLOOR_DB = -45.0    # beats whose other+bass RMS is below this are 'N'
KS_MAJOR = (6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88)
KS_MINOR = (6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17)
PC_NAMES = ("C", "C#", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B")
NEAR_TEMPO_TARGETS = tuple(MT.NEAR_TEMPO_TARGETS)
NEAR_TEMPO_FRAC = 0.15


def hash_uniform(tag: str) -> float:
    """SHA-256 inverse-CDF driver (identical to scripts.v5.groove_v5_v2.hash_uniform)."""
    return int(hashlib.sha256(tag.encode()).hexdigest()[:16], 16) / float(1 << 64)


def sha_rank(tag: str, sha16: str) -> str:
    return hashlib.sha256(f"{tag}|{sha16}".encode()).hexdigest()


def corpus_songs() -> list[str]:
    return sorted(read_json(STEMS_DIR / "manifest.json")["songs"])


def song_meta(sha16: str) -> dict:
    m = read_json(STEMS_DIR / "manifest.json")["songs"][sha16]
    return {"title": m.get("title"), "band": m.get("band"), "stems_sha256": {k: v["sha256"] for k, v in m["stems"].items()}}


def stem(sha16: str, name: str) -> np.ndarray:
    return MT.load_mono(STEMS_DIR / sha16 / f"{name}.wav")


def near_tempo(bpm: float, target: float, frac: float = NEAR_TEMPO_FRAC) -> bool:
    return abs(float(bpm) - target) <= frac * target


# ------------------------------------------------------------------------------------------------- onset streams ----
def _pack(placed: list, times: np.ndarray, assigned: list, lev: np.ndarray) -> list:
    rows = [[int(bar), int(slot), round(float(times[i]), 6), round(float(assigned[i][2]), 5), round(float(lev[i]), 3)] for bar, slot, i in placed]
    return sorted(rows, key=lambda r: (r[0], r[1]))


def extract_onsets(drums: np.ndarray, bass: np.ndarray, bpm: float, other: np.ndarray | None = None) -> dict:
    """microtiming_v6.analyze_arrays' detection + grid + assignment stages, returning the per-onset records it aggregates."""
    env_all = MT.onset_env(drums)
    be = {k: MT.norm(MT.onset_env(MT.band(drums, *MT.BANDS[k]))) for k in MT.BANDS}
    t = {k: MT.detect(be[k]) for k in ("kick", "snare", "hat")}
    bass_t, _fr, _attack = MT.detect(MT.onset_env(bass))

    def nf(k, frames):
        return be[k][np.clip(frames, 0, be[k].size - 1)]
    keep = {"kick": nf("kick", t["kick"][1]) >= 0.5 * nf("snare", t["kick"][1]),
            "snare": (nf("high", t["snare"][1]) >= 0.15) & (nf("snare", t["snare"][1]) >= 0.6 * nf("kick", t["snare"][1])) & (nf("snare", t["snare"][1]) >= 0.5 * nf("high", t["snare"][1])),
            "hat": nf("hat", t["hat"][1]) >= 0.3 * nf("snare", t["hat"][1])}
    lat = MT.calibrate()
    times = {k: t[k][0][keep[k]] - lat[k] / 1000.0 for k in keep}
    bass_t = bass_t - lat["bass"] / 1000.0
    lev = {k: MT.levels_db(MT.band(drums, *MT.BANDS[k]), times[k]) for k in times}
    all_drum_t = np.sort(np.concatenate([times[k] for k in times])) if any(times[k].size for k in times) else np.zeros(0)
    beats, _raw, ginfo = MT.beat_grid(env_all, bpm, all_drum_t)
    beats = beats - lat["grid"] / 1000.0
    asg = {k: MT.assign(times[k], beats) for k in times}
    phase, margin, scores = MT.choose_phase(asg["kick"], asg["snare"])
    hoff = MT.hyper_offset(asg["kick"] + asg["snare"] + asg["hat"], phase)
    streams, n_assigned, level_mean = {}, {}, {}
    for k in ("kick", "snare", "hat"):
        st, placed = MT.stream_stats(asg[k], lev[k], phase, hoff)
        streams[k], n_assigned[k], level_mean[k] = _pack(placed, times[k], asg[k], lev[k]), st["n_assigned"], st["level_mean_db"]
    bass_asg, bass_lev = MT.assign(bass_t, beats), MT.levels_db(bass, bass_t)
    st, placed = MT.stream_stats(bass_asg, bass_lev, phase, hoff)
    streams["bass"], n_assigned["bass"], level_mean["bass"] = _pack(placed, bass_t, bass_asg, bass_lev), st["n_assigned"], st["level_mean_db"]
    if other is not None:  # keys / pads: same full-band stem detector + latency as the bass stem (velocity_v6 only)
        ot, _f, _a = MT.detect(MT.onset_env(other))
        ot = ot - lat["bass"] / 1000.0
        o_asg, o_lev = MT.assign(ot, beats), MT.levels_db(other, ot)
        st, placed = MT.stream_stats(o_asg, o_lev, phase, hoff)
        streams["other"], n_assigned["other"], level_mean["other"] = _pack(placed, ot, o_asg, o_lev), st["n_assigned"], st["level_mean_db"]
    bars = [r[0] for k in streams for r in streams[k]]
    grid = {"bpm": float(bpm), "phase": int(phase), "phase_margin": margin, "phase_scores": scores, "hypermeter_offset": int(hoff),
            "n_beats": int(beats.size), "beat_times": [round(float(b), 6) for b in beats], "latency_ms": dict(lat),
            "bar_min": int(min(bars)) if bars else 0, "bar_max": int(max(bars)) if bars else 0,
            "downbeat_phase_offset_16th": int((4 * phase) % SLOTS), "tempo_ratio": ginfo.get("tempo_ratio"), "beat_hit_frac": ginfo.get("beat_hit_frac")}
    return {"grid": grid, "streams": streams, "n_assigned": n_assigned, "level_mean_db": level_mean, "columns": list(STREAM_COLUMNS)}


def build_onsets(sha16: str) -> dict:
    bpm = MT.song_bpm(sha16)
    rec = extract_onsets(stem(sha16, "drums"), stem(sha16, "bass"), bpm, stem(sha16, "other"))
    meta = song_meta(sha16)
    mt_song = read_json(MICROTIMING_JSON)["per_song"].get(sha16) if MICROTIMING_JSON.exists() else None
    consistent = None
    if mt_song:
        consistent = {k: rec["n_assigned"][k] == mt_song["streams"][k]["n_assigned"] for k in ("kick", "snare", "hat", "bass")}
        consistent["grid"] = (rec["grid"]["phase"] == mt_song["grid"]["phase"] and rec["grid"]["hypermeter_offset"] == mt_song["grid"]["hypermeter_offset"]
                              and rec["grid"]["n_beats"] == mt_song["grid"]["n_beats"])
        rec["grid"]["confidence"] = mt_song["grid"].get("confidence")
    out = {"schema_version": 1, "generator": "scripts/v6/rules/stems_common_v6.py", "sha16": sha16, "title": meta["title"], "band": meta["band"],
           "env_pin_sha256": ENV_PIN_SHA256, "inputs_sha256": meta["stems_sha256"], "microtiming_consistent": consistent, **rec}
    write_json_atomic(ONSETS_DIR / f"{sha16}.json", out)
    return out


def load_onsets(sha16: str, compute: bool = True) -> dict:
    p = ONSETS_DIR / f"{sha16}.json"
    if p.exists():
        return read_json(p)
    if not compute:
        raise FileNotFoundError(f"onset cache missing: {p} (run scripts/v6/rules/stems_common_v6.py)")
    return build_onsets(sha16)


def time_to_grid(t: float, beats: list | np.ndarray):
    """(beat_index, sub16 0..3, frac) on the cached grid, or None when t is outside the fitted beats."""
    b = np.asarray(beats, dtype=float)
    i = int(np.searchsorted(b, t, side="right")) - 1
    if i < 0 or i >= b.size - 1:
        return None
    frac = (t - b[i]) / (b[i + 1] - b[i])
    sub = int(round(frac * 4))
    if sub == 4:
        i, sub = i + 1, 0
    return i, sub, float(frac)


def grid_tick(t: float, beats) -> int | None:
    """v5 tick (PPQ 480, beat index = grid beat index) of a time, quantised to the 16th grid."""
    g = time_to_grid(t, beats)
    return None if g is None else g[0] * PPQ + g[1] * TICKS_16TH


def bar_slot(beat_index: int, sub16: int, grid: dict) -> tuple[int, int]:
    rel = beat_index - grid["phase"]
    return rel // 4 - grid["hypermeter_offset"], (rel % 4) * 4 + sub16


# -------------------------------------------------------------------------------------------- harmony fallback ----
def beat_chroma(y: np.ndarray, beats: list) -> tuple[np.ndarray, np.ndarray]:
    """(12 x n_beats) mean CQT chroma per beat interval and the per-beat RMS in dBFS."""
    import librosa
    C = librosa.feature.chroma_cqt(y=y, sr=MT.SR, hop_length=CHROMA_HOP)
    rms = librosa.feature.rms(y=y, frame_length=2048, hop_length=CHROMA_HOP)[0]
    fr = librosa.time_to_frames(np.asarray(beats, dtype=float), sr=MT.SR, hop_length=CHROMA_HOP)
    n = len(beats) - 1
    out, db = np.zeros((12, n)), np.full(n, -120.0)
    for i in range(n):
        a, b = int(max(0, fr[i])), int(min(C.shape[1], max(fr[i] + 1, fr[i + 1])))
        if b > a:
            out[:, i] = C[:, a:b].mean(axis=1)
            db[i] = 20.0 * np.log10(float(np.sqrt(np.mean(rms[a:b] ** 2))) + 1e-9)
    return out, db


def krumhansl_key(chroma_sum: np.ndarray) -> dict:
    """Krumhansl-Schmuckler: best Pearson correlation over 24 rotated profiles (ties -> lowest tonic, major first)."""
    x = np.asarray(chroma_sum, dtype=float)
    best = None
    for mode, prof in (("major", KS_MAJOR), ("minor", KS_MINOR)):
        for tonic in range(12):
            p = np.roll(np.asarray(prof), tonic)
            r = float(np.corrcoef(x, p)[0, 1]) if np.std(x) > 0 else 0.0
            if best is None or r > best["corr"] + 1e-12:
                best = {"tonic": tonic, "mode": mode, "tonic_name": PC_NAMES[tonic], "corr": round(r, 6)}
    return best


def chord_roots_viterbi(chroma: np.ndarray, db: np.ndarray, stay_p: float = STAY_P, floor_db: float = N_FLOOR_DB) -> list[dict]:
    """Beat-level [{beat, root, quality, state, score}] from 24 maj/min templates + Viterbi (self-transition stay_p)."""
    n = chroma.shape[1]
    T = np.zeros((24, 12))
    for r in range(12):
        T[r, [r, (r + 4) % 12, (r + 7) % 12]] = (1.0, 0.8, 0.8)
        T[12 + r, [r, (r + 3) % 12, (r + 7) % 12]] = (1.0, 0.8, 0.8)
    T /= np.linalg.norm(T, axis=1, keepdims=True)
    X = chroma / (np.linalg.norm(chroma, axis=0, keepdims=True) + 1e-9)
    S = T @ X  # 24 x n cosine scores
    logE = np.log(np.clip(S, 1e-3, None))
    logA = np.full((24, 24), np.log((1.0 - stay_p) / 23.0))
    np.fill_diagonal(logA, np.log(stay_p))
    delta, back = logE[:, 0].copy(), np.zeros((24, n), dtype=int)
    for i in range(1, n):
        cand = delta[:, None] + logA
        back[:, i] = np.argmax(cand, axis=0)
        delta = cand[back[:, i], np.arange(24)] + logE[:, i]
    path = np.zeros(n, dtype=int)
    path[-1] = int(np.argmax(delta))
    for i in range(n - 1, 0, -1):
        path[i - 1] = back[path[i], i]
    out = []
    for i in range(n):
        if db[i] < floor_db:
            out.append({"beat": i, "root": None, "quality": None, "state": "N", "score": None})
        else:
            s = int(path[i])
            out.append({"beat": i, "root": s % 12, "quality": "maj" if s < 12 else "min", "state": "ok", "score": round(float(S[s, i]), 4)})
    return out


def build_bassroots(sha16: str, onsets: dict | None = None) -> dict:
    onsets = onsets or load_onsets(sha16)
    beats = onsets["grid"]["beat_times"]
    y = stem(sha16, "other") + stem(sha16, "bass")
    chroma, db = beat_chroma(y, beats)
    stream = chord_roots_viterbi(chroma, db)
    voc = stem(sha16, "vocals")
    cv, _ = beat_chroma(voc, beats)
    key = krumhansl_key(chroma.sum(axis=1) + cv.sum(axis=1))
    roots = [c["root"] for c in stream if c["root"] is not None]
    hist = {str(pc): roots.count(pc) for pc in range(12)}
    out = {"schema_version": 1, "generator": "scripts/v6/rules/stems_common_v6.py", "sha16": sha16, "source": "fallback_chroma_template_viterbi",
           "dependency": "SWAP-IN: data/v6/rules/chords/<sha16>/chords_v6.json (sibling chords_v6/key_v6) replaces this file when present; "
                         "bass_pitch_v6.chord_stream_for prefers it automatically",
           "env_pin_sha256": ENV_PIN_SHA256, "key": key, "chord_stream": stream, "n_beats": len(stream), "n_N": sum(1 for c in stream if c["state"] == "N"),
           "root_pc_histogram": hist, "n_changes": sum(1 for a, b in zip(stream, stream[1:]) if a["root"] != b["root"]),
           "params": {"chroma": "librosa chroma_cqt hop 512 on other+bass, beat-synchronous mean", "templates": "24 maj/min (root 1.0, third 0.8, fifth 0.8), cosine",
                      "viterbi_stay_p": STAY_P, "n_floor_db": N_FLOOR_DB, "key": "Krumhansl-Schmuckler on summed chroma (other+bass+vocals)"},
           "beat_times_sha256": hashlib.sha256(str(beats).encode()).hexdigest()}
    write_json_atomic(BASSROOTS_DIR / f"{sha16}.json", out)
    return out


def load_bassroots(sha16: str, onsets: dict | None = None, compute: bool = True) -> dict:
    p = BASSROOTS_DIR / f"{sha16}.json"
    if p.exists():
        return read_json(p)
    if not compute:
        raise FileNotFoundError(f"bassroots cache missing: {p}")
    return build_bassroots(sha16, onsets)


# ------------------------------------------------------------------------------------------------------- driver ----
def run_parallel(fn, shas: list, workers: int) -> dict:
    """Deterministic fan-out: results keyed by sha16; order of completion is irrelevant (no shared state)."""
    if workers <= 1 or len(shas) <= 1:
        return {s: fn(s) for s in shas}
    import multiprocessing as mp
    with mp.get_context("fork").Pool(workers) as pool:
        res = pool.map(fn, shas, chunksize=1)
    return dict(zip(shas, res))


def _one(sha16: str) -> dict:
    import time
    t0 = time.time()
    rec = build_onsets(sha16)
    rec["wall_s"] = round(time.time() - t0, 1)
    print(f"{sha16} bpm={rec['grid']['bpm']:.2f} phase={rec['grid']['phase']} hoff={rec['grid']['hypermeter_offset']} "
          f"n={rec['n_assigned']} consistent={rec['microtiming_consistent']} wall={rec['wall_s']}s", flush=True)
    return {"n_assigned": rec["n_assigned"], "consistent": rec["microtiming_consistent"], "wall_s": rec["wall_s"]}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="build the per-onset cache shared by the v6 audio-derived rule scripts")
    ap.add_argument("--songs", default=None)
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args(argv)
    shas = [s.strip() for s in args.songs.split(",")] if args.songs else corpus_songs()
    todo = [s for s in shas if args.force or not (ONSETS_DIR / f"{s}.json").exists()]
    res = run_parallel(_one, todo, args.workers)
    bad = [s for s, r in res.items() if r["consistent"] and not all(r["consistent"].values())]
    print(f"built {len(res)} onset caches ({len(shas) - len(todo)} already present); inconsistent with microtiming_v6.json: {bad}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
