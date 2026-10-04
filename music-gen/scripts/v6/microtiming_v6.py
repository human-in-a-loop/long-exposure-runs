#!/usr/bin/python3
"""v6 Phase 3 — microtiming_v6: learn per-song and pooled PERFORMANCE models (timing deviations, dynamics, durations) from the
demucs stems in data/v6/stems/<sha16>/ against the known tempo grid. Output: data/v6/rules/microtiming_v6.json + README.

created: 2026-10-04
milestone: M-V6-GEN-3/humanization

  /usr/bin/python3 scripts/v6/microtiming_v6.py [--songs sha16,...] [--out data/v6/rules/microtiming_v6.json]

Per song: (a) beat grid — librosa.beat.beat_track on the drum-stem onset envelope with the KNOWN bpm forced (`bpm=`) and
tightness 400 (follows slow drift, no octave errors), then the beat times are smoothed by a centred local linear fit over
+/-4 beats so within-beat deviations (incl. beat-level onsets) are measured against a locally rigid grid; the downbeat phase
(beat index mod 4) is the one maximising kick-on-1 + snare-on-2/4 counts; 16th slots interpolate between smoothed beats.
Grid-fit confidence from the onset-strength contrast at beats vs midpoints, the fraction of beats with a drum onset within
35 ms, the beat-interval tempo vs the known bpm and the downbeat-phase margin. (b) onsets: librosa.onset.onset_detect on
band-limited onset envelopes (hop 128 = 5.8 ms, peak refined by parabolic interpolation; backtracked frames = attack start,
used for the bass duration proxy): kick < 150 Hz, snare 150 Hz-2 kHz with a broadband (2-8 kHz) transient test and a
not-kick-dominated test, hat > 5 kHz, bass = the bass stem. (c) every onset -> nearest 16th slot (rejected when |dev| >
0.4 x 16th), deviation in ms and fraction-of-16th, slot mod 16, bar, level (dB of the 30 ms local RMS after the onset).
(d)/(e): see scripts/v6/gen/microtiming_model.py (sufficient statistics, exact pooling by band / near_tempo).
"""
from __future__ import annotations

import argparse
import hashlib
import sys
import time
from pathlib import Path

import numpy as np

_WS = Path(__file__).resolve().parent.parent.parent
if str(_WS) not in sys.path:
    sys.path.insert(0, str(_WS))
from scripts.v6.gen.common import WS, read_json, sha_file, write_json_atomic  # noqa: E402
from scripts.v6.gen import microtiming_model as M  # noqa: E402

SR, HOP, N_FFT = 22050, 128, 1024
TIGHTNESS = 400
BANDS = {"kick": (None, 150.0), "snare": (150.0, 2000.0), "high": (2000.0, 8000.0), "hat": (5000.0, None)}
STEMS_DIR = WS / "data/v6/stems"
TEMPO_DIR = WS / "data/v6/corpus"
OUT_DEFAULT = WS / "data/v6/rules/microtiming_v6.json"
NEAR_TEMPO_TARGETS = (100.0, 120.0, 152.0)
HIT_TOL_S = 0.035
LEVEL_WIN_S = 0.030
SMOOTH_W = 4
_LAT: dict = {}


def det_noise(n: int, tag: str) -> np.ndarray:
    """Deterministic white noise in [-1, 1) from chained SHA-256 digests (no PRNG)."""
    chunks = []
    for k in range((n + 7) // 8):
        d = hashlib.sha256(f"{tag}|{k}".encode()).digest()
        chunks.append(np.frombuffer(d, dtype=np.uint32).astype(np.float64) / 2 ** 31 - 1.0)
    return np.concatenate(chunks)[:n]


def _hit(kind: str) -> np.ndarray:
    tt = np.arange(int(0.15 * SR)) / SR
    env = np.exp(-tt * (20 if kind in ("kick", "bass") else 40))
    if kind == "kick":
        sig = np.sin(2 * np.pi * 55 * tt)
    elif kind == "bass":
        sig = np.sin(2 * np.pi * 55 * tt)
        env[: int(0.01 * SR)] *= np.linspace(0, 1, int(0.01 * SR))
    elif kind == "snare":
        sig = det_noise(tt.size, "snare") * 0.6
    else:
        from scipy.signal import butter, sosfilt
        sig = sosfilt(butter(4, 6000 / (SR / 2), "highpass", output="sos"), det_noise(tt.size, "hat")) * 0.6
    return (sig * env).astype(np.float32)


def calibrate() -> dict:
    """Detector latency (ms) per stream pipeline and for the full-band grid envelope, from isolated synthetic hits at known
    times; subtracted from every onset / beat so streams are comparable (the kick band peaks ~7 ms before the others)."""
    if _LAT:
        return _LAT
    truth = [0.5 + i * 0.6 + (i % 7) * 0.0137 for i in range(20)]
    y = {k: np.zeros(int(SR * 13), np.float32) for k in ("kick", "snare", "hat", "bass")}
    for k in y:
        sig = _hit(k)
        for t in truth:
            s0 = int(round(t * SR))
            y[k][s0: s0 + sig.size] += sig
    pipes = {"kick": lambda a: band(a, *BANDS["kick"]), "snare": lambda a: band(a, *BANDS["snare"]), "hat": lambda a: band(a, *BANDS["hat"]), "bass": lambda a: a}
    for k, f in pipes.items():
        times, _fr, _bt = detect(norm(onset_env(f(y[k]))))
        _LAT[k] = round(float(np.median([(times[np.argmin(np.abs(times - t))] - t) * 1000.0 for t in truth])), 3) if times.size else 0.0
    mix = y["kick"] + y["snare"] + y["hat"]
    times, _fr, _bt = detect(onset_env(mix))
    _LAT["grid"] = round(float(np.median([(times[np.argmin(np.abs(times - t))] - t) * 1000.0 for t in truth])), 3) if times.size else 0.0
    return _LAT


def band(y: np.ndarray, lo, hi) -> np.ndarray:
    from scipy.signal import butter, sosfiltfilt
    nyq = SR / 2.0
    if lo is None:
        sos = butter(4, hi / nyq, btype="lowpass", output="sos")
    elif hi is None:
        sos = butter(4, lo / nyq, btype="highpass", output="sos")
    else:
        sos = butter(4, [lo / nyq, hi / nyq], btype="bandpass", output="sos")
    return sosfiltfilt(sos, y).astype(np.float32)


def onset_env(y: np.ndarray) -> np.ndarray:
    import librosa
    return librosa.onset.onset_strength(y=y, sr=SR, hop_length=HOP, n_fft=N_FFT)


def norm(env: np.ndarray) -> np.ndarray:
    p = float(np.percentile(env, 95)) if env.size else 1.0
    return env / (p if p > 1e-9 else 1.0)


def detect(env: np.ndarray) -> tuple:
    """(refined onset times [s], peak frames, backtracked attack-start times [s])."""
    import librosa
    if env.size < 8:
        return np.zeros(0), np.zeros(0, dtype=int), np.zeros(0)
    frames = librosa.onset.onset_detect(onset_envelope=env, sr=SR, hop_length=HOP, units="frames", backtrack=False)
    frames = frames[(frames > 0) & (frames < env.size - 1)]
    a, b, c = env[frames - 1], env[frames], env[frames + 1]
    den = a - 2 * b + c
    off = np.where(np.abs(den) > 1e-12, 0.5 * (a - c) / np.where(np.abs(den) > 1e-12, den, 1.0), 0.0)
    off = np.clip(off, -0.5, 0.5)
    times = (frames + off) * HOP / SR
    bt = librosa.onset.onset_backtrack(frames, env) if frames.size else frames
    return times, frames, bt * HOP / SR


def levels_db(y: np.ndarray, times: np.ndarray) -> np.ndarray:
    n = int(LEVEL_WIN_S * SR)
    out = np.zeros(times.size)
    for i, t in enumerate(times):
        s = int(t * SR)
        seg = y[s: s + n]
        out[i] = 20 * np.log10(float(np.sqrt(np.mean(seg.astype(np.float64) ** 2))) + 1e-9) if seg.size else -180.0
    return out


def smooth_beats(beats: np.ndarray, w: int = SMOOTH_W) -> np.ndarray:
    n = beats.size
    out = np.array(beats, dtype=float)
    for i in range(n):
        lo, hi = max(0, i - w), min(n, i + w + 1)
        if hi - lo < 3:
            continue
        j = np.arange(lo, hi, dtype=float)
        A = np.vstack([j, np.ones_like(j)]).T
        coef, *_ = np.linalg.lstsq(A, beats[lo:hi], rcond=None)
        out[i] = coef[0] * i + coef[1]
    return out


def beat_grid(env: np.ndarray, bpm: float, onset_times_all: np.ndarray) -> tuple:
    import librosa
    _tempo, frames = librosa.beat.beat_track(onset_envelope=env, sr=SR, hop_length=HOP, bpm=float(bpm), tightness=TIGHTNESS, trim=False, units="frames")
    raw = frames.astype(float) * HOP / SR
    if raw.size < 8:
        return raw, raw, {"n_beats": int(raw.size), "confidence": "low", "beat_contrast": None, "beat_hit_frac": None, "tempo_ratio": None}
    beats = smooth_beats(raw)
    fr = beats * SR / HOP
    mid = (fr[:-1] + fr[1:]) / 2
    at_beats = float(np.mean(np.interp(fr, np.arange(env.size), env)))
    at_mid = float(np.mean(np.interp(mid, np.arange(env.size), env)))
    contrast = (at_beats - at_mid) / (at_beats + at_mid + 1e-9)
    hit = float(np.mean([np.min(np.abs(onset_times_all - b)) <= HIT_TOL_S for b in beats])) if onset_times_all.size else 0.0
    iv = np.diff(beats)
    tempo_ratio = float((60.0 / np.median(iv)) / bpm)
    info = {"n_beats": int(beats.size), "beat_contrast": round(contrast, 4), "beat_hit_frac": round(hit, 4), "tempo_ratio": round(tempo_ratio, 5),
            "interval_cv": round(float(np.std(iv) / np.mean(iv)), 5), "raw_vs_smoothed_rms_ms": round(float(np.sqrt(np.mean((raw - beats) ** 2)) * 1000), 2), "tightness": TIGHTNESS}
    return beats, raw, info


def assign(times: np.ndarray, beats: np.ndarray) -> list:
    """Per onset: (beat_idx, sub16, dev_f16, dev_ms, status) with status in {'ok', 'rejected', 'out_of_grid'}."""
    out = []
    for t in times:
        i = int(np.searchsorted(beats, t, side="right")) - 1
        if i < 0 or i >= beats.size - 1:
            out.append((None, None, None, None, "out_of_grid"))
            continue
        s16 = (beats[i + 1] - beats[i]) / 4.0
        sub_f = (t - beats[i]) / s16
        sub = int(round(sub_f))
        dev = sub_f - sub
        if sub == 4:
            i, sub = i + 1, 0
        out.append((i, sub, float(dev), float(dev * s16 * 1000.0), "ok" if abs(dev) <= M.REJECT_F16 else "rejected"))
    return out


def choose_phase(kick: list, snare: list) -> tuple:
    scores = []
    for p in range(4):
        k0 = sum(1 for a in kick if a[4] == "ok" and a[1] == 0 and (a[0] - p) % 4 == 0)
        s13 = sum(1 for a in snare if a[4] == "ok" and a[1] == 0 and (a[0] - p) % 4 in (1, 3))
        s02 = sum(1 for a in snare if a[4] == "ok" and a[1] == 0 and (a[0] - p) % 4 in (0, 2))
        scores.append(k0 + s13 - 0.5 * s02)
    best = int(np.argmax(scores))
    srt = sorted(scores, reverse=True)
    margin = (srt[0] - srt[1]) / max(1.0, srt[0]) if len(srt) > 1 else 1.0
    return best, round(float(margin), 4), [round(float(s), 1) for s in scores]


def hyper_offset(drum_assigned: list, phase: int) -> int:
    """Bar offset in 0..7 maximising last-beat onset density on bars == 3 mod 4 (then the better of o / o+4 for mod 8)."""
    bars = {}
    for a in drum_assigned:
        if a[4] != "ok":
            continue
        b = (a[0] - phase) // 4
        slot = ((a[0] - phase) % 4) * 4 + a[1]
        bars.setdefault(b, [0, 0])
        bars[b][0] += 1
        bars[b][1] += 1 if slot >= 12 else 0
    if not bars:
        return 0

    def dens(mod: int, o: int) -> float:
        bd = [v[1] for b, v in bars.items() if (b - o) % mod == mod - 1]
        ot = [v[1] for b, v in bars.items() if (b - o) % mod != mod - 1]
        return (np.mean(bd) if bd else 0.0) - (np.mean(ot) if ot else 0.0)
    o4 = int(np.argmax([dens(4, o) for o in range(4)]))
    return o4 if dens(8, o4) >= dens(8, o4 + 4) else o4 + 4


def stream_stats(assigned: list, lev: np.ndarray, phase: int, hoff: int) -> tuple:
    """Fill a microtiming_model stream from assigned onsets; returns (stream, [(bar, slot16, t_idx)] of accepted onsets)."""
    st = M.empty_stream()
    st["n_detected"] = len(assigned)
    ok_idx = [i for i, a in enumerate(assigned) if a[4] == "ok"]
    st["n_rejected"] = sum(1 for a in assigned if a[4] == "rejected")
    st["n_out_of_grid"] = sum(1 for a in assigned if a[4] == "out_of_grid")
    st["n_assigned"] = len(ok_idx)
    best: dict = {}  # one onset per (bar, slot): the smallest |dev| (a double peak of one hit is not two hits)
    for i in ok_idx:
        bi, sub, dev, _dm, _ = assigned[i]
        key = ((bi - phase) // 4 - hoff, ((bi - phase) % 4) * 4 + sub)
        if key not in best or abs(dev) < abs(assigned[best[key]][2]):
            best[key] = i
    st["n_duplicate"] = len(ok_idx) - len(best)
    ok_idx = sorted(best.values())
    st["n_assigned"] = len(ok_idx)
    mean_db = float(np.mean(lev[ok_idx])) if ok_idx else 0.0
    st["level_mean_db"] = round(mean_db, 3)
    placed = []
    for i in ok_idx:
        bi, sub, dev, dev_ms, _ = assigned[i]
        bar = (bi - phase) // 4 - hoff
        slot = ((bi - phase) % 4) * 4 + sub
        rel = float(lev[i]) - mean_db
        M.add_cell(st["ms"][slot], dev_ms)
        M.add_cell(st["f16"][slot], dev)
        M.add_cell(st["db"][slot], rel)
        M.add_cell(st["bar_mod4_db"][bar % 4], rel)
        M.add_cell(st["bar_mod8_db"][bar % 8], rel)
        M.add_cell(st["beat_class_db"][M.beat_class(slot)], rel)
        st["hist_f16"][M.hist_index(dev)] += 1
        placed.append((bar, slot, i))
    return st, placed


def bass_duration(bass_y: np.ndarray, times: np.ndarray, attack: np.ndarray, placed: list) -> dict:
    """Decay proxy: frames until the 30 ms RMS envelope falls 20 dB below the post-onset peak (or the next onset), / IOI."""
    import librosa
    rms = librosa.feature.rms(y=bass_y, frame_length=int(LEVEL_WIN_S * SR) // 2 * 2, hop_length=HOP)[0]
    db = 20 * np.log10(rms + 1e-9)
    hist = [0] * M.DUR_BINS
    cls = {"on_beat": {"n": 0, "s": 0.0, "ss": 0.0}, "syncopated": {"n": 0, "s": 0.0, "ss": 0.0}}
    fr = lambda t: int(t * SR / HOP)  # noqa: E731
    order = np.argsort(times)
    nxt = {int(order[k]): float(times[order[k + 1]]) for k in range(len(order) - 1)}
    for bar, slot, i in placed:
        if i not in nxt:
            continue
        f0, f1 = fr(attack[i] if attack[i] < times[i] else times[i]), fr(nxt[i])
        if f1 - f0 < 2 or f1 >= db.size:
            continue
        seg = db[f0:f1]
        pk = int(np.argmax(seg[: min(seg.size, 12)]))
        below = np.where(seg[pk:] < seg[pk] - 20.0)[0]
        dur_frames = (pk + int(below[0])) if below.size else seg.size
        frac = min(1.0, dur_frames / float(f1 - f0))
        hist[min(M.DUR_BINS - 1, int(frac * M.DUR_BINS))] += 1
        M.add_cell(cls["on_beat" if slot in M.EVEN_8TH else "syncopated"], frac)
    n = sum(hist)
    return {"hist": hist, "n": n, "mean_frac": round(sum((i + 0.5) / M.DUR_BINS * c for i, c in enumerate(hist)) / n, 4) if n else None,
            "by_class": {c: {"n": v["n"], "s": round(v["s"], 6), "ss": round(v["ss"], 6)} for c, v in cls.items()}}


def fill_density(drum_placed: list) -> dict:
    bars: dict = {}
    for bar, slot, _ in drum_placed:
        bars.setdefault(bar, [0, 0])
        bars[bar][0] += 1
        bars[bar][1] += 1 if slot >= 12 else 0
    out = {}
    for mod in (4, 8):
        bd = [v[1] for b, v in bars.items() if b % mod == mod - 1]
        ot = [v[1] for b, v in bars.items() if b % mod != mod - 1]
        out[f"mod{mod}"] = {"boundary_onsets": int(sum(bd)), "boundary_bars": len(bd), "other_onsets": int(sum(ot)), "other_bars": len(ot),
                            "ratio": round((np.mean(bd) / np.mean(ot)), 4) if bd and ot and np.mean(ot) > 0 else None}
    return out


def analyze_arrays(drums: np.ndarray, bass: np.ndarray, bpm: float, sha16: str = "synthetic", band_rating=None) -> dict:
    """The whole per-song analysis on in-memory mono 22.05 kHz arrays (used by the driver and by the synthetic test)."""
    env_all = onset_env(drums)
    be = {k: norm(onset_env(band(drums, *BANDS[k]))) for k in BANDS}
    t = {k: detect(be[k]) for k in ("kick", "snare", "hat")}
    bass_t, bass_fr, bass_attack = detect(onset_env(bass))

    def nf(k, frames):  # normalised flux of band k at the given frames
        return be[k][np.clip(frames, 0, be[k].size - 1)]
    keep = {"kick": nf("kick", t["kick"][1]) >= 0.5 * nf("snare", t["kick"][1]),
            "snare": (nf("high", t["snare"][1]) >= 0.15) & (nf("snare", t["snare"][1]) >= 0.6 * nf("kick", t["snare"][1])) & (nf("snare", t["snare"][1]) >= 0.5 * nf("high", t["snare"][1])),
            "hat": nf("hat", t["hat"][1]) >= 0.3 * nf("snare", t["hat"][1])}
    lat = calibrate()
    times = {k: t[k][0][keep[k]] - lat[k] / 1000.0 for k in keep}
    bass_t = bass_t - lat["bass"] / 1000.0
    bass_attack = bass_attack - lat["bass"] / 1000.0
    ysig = {"kick": band(drums, *BANDS["kick"]), "snare": band(drums, *BANDS["snare"]), "hat": band(drums, *BANDS["hat"])}
    lev = {k: levels_db(ysig[k], times[k]) for k in times}
    all_drum_t = np.sort(np.concatenate([times[k] for k in times])) if any(times[k].size for k in times) else np.zeros(0)
    beats, raw, ginfo = beat_grid(env_all, bpm, all_drum_t)
    beats = beats - lat["grid"] / 1000.0
    ginfo["latency_ms"] = dict(lat)
    asg = {k: assign(times[k], beats) for k in times}
    phase, margin, scores = choose_phase(asg["kick"], asg["snare"])
    hoff = hyper_offset(asg["kick"] + asg["snare"] + asg["hat"], phase)
    streams, placed = {}, {}
    for k in ("kick", "snare", "hat"):
        streams[k], placed[k] = stream_stats(asg[k], lev[k], phase, hoff)
    bass_asg = assign(bass_t, beats)
    bass_lev = levels_db(bass, bass_t)
    streams["bass"], placed["bass"] = stream_stats(bass_asg, bass_lev, phase, hoff)
    kick_at = {(b, s): times["kick"][i] for b, s, i in placed["kick"]}
    lag = {"n": 0, "s": 0.0, "ss": 0.0}
    lag_vals = []
    for b, s, i in placed["bass"]:
        if (b, s) in kick_at:
            d = float(bass_t[i] - kick_at[(b, s)]) * 1000.0
            M.add_cell(lag, d)
            lag_vals.append(d)
    n_bars = (max([b for k in placed for b, _, _ in placed[k]], default=0) + 1)
    conf = "high" if (ginfo.get("beat_contrast") or 0) > 0.3 and (ginfo.get("beat_hit_frac") or 0) > 0.6 and abs((ginfo.get("tempo_ratio") or 0) - 1) < 0.02 and margin > 0.1 else \
        ("medium" if (ginfo.get("beat_contrast") or 0) > 0.15 and (ginfo.get("beat_hit_frac") or 0) > 0.4 and abs((ginfo.get("tempo_ratio") or 0) - 1) < 0.04 else "low")
    swing = {k: M.swing_of(streams[k]["ms"], streams[k]["f16"]) for k in M.STREAMS}
    drums_ms = M.merge_cells(M.merge_cells(streams["kick"]["ms"], streams["snare"]["ms"]), streams["hat"]["ms"])
    drums_f = M.merge_cells(M.merge_cells(streams["kick"]["f16"], streams["snare"]["f16"]), streams["hat"]["f16"])
    swing["drums"] = M.swing_of(drums_ms, drums_f)
    return {"sha16": sha16, "band": band_rating, "grid": dict(ginfo, bpm=float(bpm), phase=phase, phase_margin=margin, phase_scores=scores, hypermeter_offset=int(hoff),
                                                           n_bars=int(n_bars), confidence=conf),
            "streams": streams, "swing": swing,
            "bass_kick_lag": dict(lag, mean_ms=round(M.cell_mean(lag), 3) if lag["n"] else None, std_ms=round(M.cell_std(lag), 3) if lag["n"] > 1 else None,
                                  median_ms=round(float(np.median(lag_vals)), 3) if lag_vals else None),
            "bass_duration": bass_duration(bass, bass_t, bass_attack, placed["bass"]), "fill_density": fill_density(placed["kick"] + placed["snare"] + placed["hat"]),
            "n_onsets": {k: int(times[k].size) for k in times} | {"bass": int(bass_t.size)}}


def load_mono(p: Path) -> np.ndarray:
    import soundfile as sf
    y, sr = sf.read(str(p), dtype="float32", always_2d=True)
    y = y.mean(axis=1)
    if sr != SR:
        import librosa
        y = librosa.resample(y, orig_sr=sr, target_sr=SR)
    return y.astype(np.float32)


def song_bpm(sha16: str) -> float:
    t = read_json(TEMPO_DIR / sha16 / "tempo_v6.json")
    if t.get("override", {}).get("applied"):
        return float(t["override"]["bpm"])
    return float(t.get("bpm_v6_estimate") or t["bpm_v5"])


def write_readme(mt: dict, path: Path) -> None:
    from scripts.v6.microtiming_report_v6 import render_readme
    path.write_text(render_readme(mt), encoding="utf-8")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="v6 microtiming / dynamics model from corpus stems")
    ap.add_argument("--songs", default=None, help="comma-separated sha16 subset (default: every song in data/v6/stems/manifest.json)")
    ap.add_argument("--out", default=str(OUT_DEFAULT))
    args = ap.parse_args(argv)
    man = read_json(STEMS_DIR / "manifest.json")
    shas = [s.strip() for s in args.songs.split(",")] if args.songs else sorted(man["songs"])
    per_song, inputs = {}, {}
    for sha in shas:
        t0 = time.time()
        d = STEMS_DIR / sha
        bpm = song_bpm(sha)
        e = analyze_arrays(load_mono(d / "drums.wav"), load_mono(d / "bass.wav"), bpm, sha, man["songs"][sha].get("band"))
        e["title"] = man["songs"][sha].get("title")
        e["wall_s"] = round(time.time() - t0, 1)
        per_song[sha] = e
        inputs[sha] = {k: man["songs"][sha]["stems"][k]["sha256"] for k in ("drums", "bass")}
        g = e["grid"]
        print(f"{sha} bpm={bpm:.1f} conf={g['confidence']} contrast={g['beat_contrast']} hit={g['beat_hit_frac']} ratio={g['tempo_ratio']} phase_margin={g['phase_margin']} "
              f"swing_hat={e['swing']['hat']['ratio']} drums={e['swing']['drums']['ratio']} lag={e['bass_kick_lag']['mean_ms']} n={e['n_onsets']} wall={e['wall_s']}s", flush=True)
    pooled = {"all": M.pool(per_song, "all")}
    for b in sorted({str(e["band"]) for e in per_song.values()}):
        pooled[f"band_{b}"] = M.pool({s: e for s, e in per_song.items() if str(e["band"]) == b}, f"band_{b}")
    pooled["near_tempo"] = {str(int(t)): M.pool(M.near_tempo_entries(per_song, t), "near_tempo", t) for t in NEAR_TEMPO_TARGETS}
    mt = {"schema_version": 1, "generator": "scripts/v6/microtiming_v6.py", "milestone": "M-V6-GEN-3/humanization",
          "params": {"sr": SR, "hop": HOP, "n_fft": N_FFT, "tightness": TIGHTNESS, "bands_hz": {k: list(v) for k, v in BANDS.items()}, "reject_f16": M.REJECT_F16,
                     "hist_edges_f16": M.HIST_EDGES, "level_window_s": LEVEL_WIN_S, "beat_smoothing_halfwidth": SMOOTH_W, "hit_tolerance_s": HIT_TOL_S,
                     "detector_latency_ms": calibrate(), "dedup": "one onset per stream per (bar, slot): smallest |dev| kept",
                     "near_tempo_frac": M.NEAR_TEMPO_FRAC, "near_tempo_targets": list(NEAR_TEMPO_TARGETS), "velocity_db": "20*log10(RMS over 30 ms after the onset), relative to the stream mean"},
          "inputs_sha256": inputs, "stems_manifest_sha256": sha_file(STEMS_DIR / "manifest.json"), "n_songs": len(per_song), "pooled": pooled, "per_song": per_song}
    out = Path(args.out) if Path(args.out).is_absolute() else WS / args.out
    write_json_atomic(out, mt)
    write_readme(mt, out.with_name(out.stem + "_README.md"))
    print(f"wrote {out} ({len(per_song)} songs) + README")
    return 0


if __name__ == "__main__":
    sys.exit(main())
