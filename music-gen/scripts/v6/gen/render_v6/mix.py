#!/usr/bin/python3
"""v6 Phase 4 — per-song mix chain (pedalboard) + corpus-derived loudness/tilt targets.

created: 2026-10-04
milestone: M-V6-RENDER-4/realistic-renderer

Per stem (role): high-pass (bass 30 Hz, keys/guitar 80 Hz, pads 120 Hz, drums 25 Hz, melody 100 Hz), RMS gain staging to a
per-role level (deterministic gain, clipped [0.05, 8]), THEN gentle compression with the threshold a fixed headroom above
that level (drums 4:1 fast, bass 3:1, keys/guitar/melody 2:1, pad 1.5:1), stereo placement (bass + drums centre — bass mono, kit keeps its own stereo image; keys +20 % with
their sampled stereo image kept (side x1.25; a mono keys stem gets a 9 ms Haas spread), comping -25 % with an 11 ms L/R
(Haas) delay, pad wide (kept stereo + 1.6 side), melody +/-10 % by a SHA draw, percussion -30 %), a shared reverb bus
(pedalboard.Reverb; room_size from the band and the ballad flag/tempo; per-role sends; bass dry) whose stereo return carries
six deterministic early-reflection taps with DIFFERENT left/right delays (decorrelation), bus compression 1.5:1 from -6 dB, a
mild high-shelf steer of the spectral tilt toward the band's corpus median (|gain| <= 3 dB), loudness normalisation to the
TARGET (corpus median integrated LUFS clamped to -14 +/- 2) and a true-peak limiter at -0.5 dBTP. Phase 5 (iteration 04)
re-targeted the placement / bus / ceiling against the iteration-03 scorecard descriptors: candidates were nearly mono (L/R
correlation 0.973 vs 0.80 in the corpus, width -18.7 vs -12.9 dB), 1.5 dB more compressed (crest 12.6 vs 14.1 dB) and
peaked 2 dB lower (-2.0 vs -0.03 dBFS). The limiter is this
module's own numpy look-ahead design (pedalboard.Limiter adds ~5 dB of make-up gain, which made a normalise/limit loop
diverge): per-sample required gain -> 5 ms running minimum (look-ahead) -> exponential release (80 ms, max-with-decay
computed by log2(n) vectorised doubling passes) -> 5 ms moving average -> 4x-oversampled true-peak check; up to 3
normalise/limit passes so the final integrated LUFS is within +/-0.5 of target.
Reference: measure_reference() reads corpus/ratings/ingest_receipts.jsonl (29 songs; bands 4/5/7), measures integrated
LUFS (pyloudnorm), crest factor (peak dB - RMS dB) and spectral tilt (10*log10 of energy > 4 kHz over 200 Hz - 2 kHz,
Hann 4096 frames) per song and per-band medians, and writes scripts/v6/patches/mix_reference_v6.json (small, tracked)
so renders stay reproducible without the (gitignored) corpus audio. Everything is a pure function of its inputs: no PRNG.
"""
from __future__ import annotations

import json
import os
import time
from pathlib import Path

import numpy as np

WS = Path(__file__).resolve().parents[4]
MIX_REFERENCE = WS / "scripts" / "v6" / "patches" / "mix_reference_v6.json"
RECEIPTS = WS / "corpus" / "ratings" / "ingest_receipts.jsonl"
SR = 44100
TARGET_LUFS_CLAMP = (-16.0, -12.0)
TRUE_PEAK_DBTP = -0.5  # Phase 5: was -1.0 (corpus peaks sit at -0.03 dBFS; candidates at -2.0)
HPF_HZ = {"drums": 25.0, "bass": 30.0, "keys": 80.0, "comp_guitar": 80.0, "melody": 100.0, "pad": 120.0, "percussion": 150.0}
COMP = {"drums": (8.0, 4.0, 3.0, 80.0), "bass": (6.0, 3.0, 10.0, 120.0), "keys": (8.0, 2.0, 15.0, 150.0), "comp_guitar": (8.0, 2.0, 10.0, 120.0),
        "melody": (8.0, 2.0, 10.0, 150.0), "pad": (6.0, 1.5, 30.0, 300.0), "percussion": (8.0, 3.0, 5.0, 100.0)}  # threshold headroom dB above the stem RMS target, ratio, attack ms, release ms
BUS_COMP = {"threshold_db": -6.0, "ratio": 1.5, "attack_ms": 10.0, "release_ms": 150.0}  # Phase 5: eased from -10 dB / 2:1 (crest +~1.5 dB wanted)
LIMITER = {"lookahead_ms": 5.0, "release_ms": 80.0}
STEM_GROUP = {"drums": "drums", "percussion": "drums", "bass": "bass", "keys": "other", "comp_guitar": "other", "melody": "other", "pad": "other"}  # Demucs-style groups (--keep-stems)
STEM_RMS_DB = {"drums": -18.0, "bass": -18.0, "keys": -22.0, "comp_guitar": -24.0, "melody": -22.0, "pad": -26.0, "percussion": -27.0}
PAN = {"drums": "stereo", "bass": 0.0, "keys": ("stereo_pan", 0.2, 1.25), "comp_guitar": ("haas", -0.25, 11.0), "pad": "wide", "melody": "sha", "percussion": -0.3}
WIDE_SIDE = 1.6  # Phase 5: was 1.3
HAAS_MONO_KEYS_MS, HAAS_GAIN_DB = 9.0, -6.0  # a mono keys stem gets a quiet delayed copy on the far channel
EARLY_REFLECTIONS_MS = {"L": (7.1, 13.3, 23.9), "R": (9.7, 17.9, 29.3)}  # reverb return: distinct L/R taps -> decorrelated early field
EARLY_REFLECTION_DB, REVERB_RETURN_DB = -12.0, -9.0  # Phase 5: return was -10 dB, no early reflections
REVERB_SEND = {"drums": 0.12, "bass": 0.0, "keys": 0.22, "comp_guitar": 0.18, "pad": 0.35, "melody": 0.28, "percussion": 0.15}
ROOM_BY_BAND = {4: 0.45, 5: 0.38, 6: 0.42, 7: 0.55}
GAIN_CLIP = (0.05, 8.0)
# Iteration 05 — pre-registered changes (docs/v6_iteration_05_diagnostics.md section 5):
TILT_STEER = {"strength": 1.0, "cap_db": 6.0}  # was 0.5 x the difference, |gain| <= 3 dB: iteration 04 masters sat 4-6 dB brighter than the band target (shelf saturated at -2.5 dB)
SONG_VARIATION = {"lufs": "per-song target = SHA inverse-CDF over the band's per-song corpus LUFS values (mix_reference per_song), clamped to TARGET_LUFS_CLAMP",
                  "room_jitter": 0.08, "return_jitter_db": 2.0}  # per-song room size +/- jitter and reverb return +/- dB (SHA draws on the song tag)


# ------------------------------------------------------------------------------------------------------- measures ----
def lufs(x: np.ndarray, sr: int) -> float:
    import pyloudnorm as pyln
    v = float(pyln.Meter(sr).integrated_loudness(np.asarray(x, dtype=np.float64)))
    return v if np.isfinite(v) else -70.0


def crest_db(x: np.ndarray) -> float:
    a = np.asarray(x, dtype=np.float64)
    peak, rms = float(np.abs(a).max()) if a.size else 0.0, float(np.sqrt((a ** 2).mean())) if a.size else 0.0
    return 20.0 * np.log10(max(peak, 1e-9) / max(rms, 1e-9))


def spectral_tilt_db(x: np.ndarray, sr: int, n_fft: int = 4096) -> float:
    """10*log10( E(>4 kHz) / E(200 Hz..2 kHz) ) of the time-averaged Hann power spectrum (mono)."""
    m = np.asarray(x, dtype=np.float64)
    m = m.mean(axis=1) if m.ndim == 2 else m
    n = (len(m) // n_fft) * n_fft
    if n == 0:
        return 0.0
    frames = m[:n].reshape(-1, n_fft) * np.hanning(n_fft)
    p = (np.abs(np.fft.rfft(frames, axis=1)) ** 2).mean(axis=0)
    f = np.fft.rfftfreq(n_fft, 1.0 / sr)
    hi, mid = p[f >= 4000.0].sum(), p[(f >= 200.0) & (f < 2000.0)].sum()
    return 10.0 * np.log10(max(hi, 1e-18) / max(mid, 1e-18))


def true_peak_dbtp(x: np.ndarray, sr: int) -> float:
    from scipy.signal import resample_poly
    a = np.asarray(x, dtype=np.float64)
    up = resample_poly(a, 4, 1, axis=0)
    return 20.0 * np.log10(max(float(np.abs(up).max()), 1e-9))


def measure_track(path: Path) -> dict:
    import soundfile as sf
    x, sr = sf.read(str(path), dtype="float32", always_2d=True)
    a = x.astype(np.float64)
    return {"path": str(path), "sr": int(sr), "duration_s": round(x.shape[0] / sr, 3), "lufs_integrated": round(lufs(a, sr), 3), "crest_factor_db": round(crest_db(a), 3),
            "spectral_tilt_db": round(spectral_tilt_db(a, sr), 3), "peak_dbfs": round(20.0 * np.log10(max(float(np.abs(a).max()), 1e-9)), 3),
            "rms_dbfs": round(20.0 * np.log10(max(float(np.sqrt((a ** 2).mean())), 1e-9)), 3)}


def _median_block(rows: list) -> dict:
    out = {"n": len(rows)}
    for k in ("lufs_integrated", "crest_factor_db", "spectral_tilt_db"):
        vals = [r[k] for r in rows]
        out[k + "_median"] = round(float(np.median(vals)), 3) if vals else None
        out[k + "_iqr"] = [round(float(np.percentile(vals, 25)), 3), round(float(np.percentile(vals, 75)), 3)] if vals else None
    return out


def clamp_target(lufs_median: float) -> float:
    return float(min(TARGET_LUFS_CLAMP[1], max(TARGET_LUFS_CLAMP[0], lufs_median)))


def measure_reference(receipts: Path = RECEIPTS, out_json: Path = MIX_REFERENCE, log=print) -> dict:
    rows = []
    for line in Path(receipts).read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        p = WS / r["path"]
        if not p.exists():
            log(f"[mix-ref] missing {p}")
            continue
        t0 = time.time()
        m = measure_track(p)
        m.update({"sha16": r["sha16"], "band": int(r["band"]), "title": r.get("title"), "path": r["path"], "wall_s": round(time.time() - t0, 2)})
        rows.append(m)
        log(f"[mix-ref] band={m['band']} {m['sha16']} LUFS={m['lufs_integrated']} crest={m['crest_factor_db']} tilt={m['spectral_tilt_db']} {m['wall_s']}s")
    rows.sort(key=lambda r: (r["band"], r["sha16"]))
    bands = sorted({r["band"] for r in rows})
    per_band = {str(b): _median_block([r for r in rows if r["band"] == b]) for b in bands}
    overall = _median_block(rows)
    ref = {"schema_version": 1, "source": str(Path(receipts).relative_to(WS)) if str(receipts).startswith(str(WS)) else str(receipts), "n_songs": len(rows),
           "per_song": rows, "per_band": per_band, "overall": overall, "target_lufs": clamp_target(overall["lufs_integrated_median"]) if rows else -14.0,
           "target_lufs_rule": f"corpus median integrated LUFS clamped to [{TARGET_LUFS_CLAMP[0]}, {TARGET_LUFS_CLAMP[1]}]", "true_peak_dbtp": TRUE_PEAK_DBTP,
           "tilt_definition": "10*log10(E(>4kHz)/E(200Hz-2kHz)), Hann 4096, time-averaged power spectrum, mono"}
    out_json = Path(out_json)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    tmp = out_json.with_name(out_json.name + ".tmp")
    tmp.write_text(json.dumps(ref, sort_keys=True, indent=1) + "\n", encoding="utf-8")
    os.replace(tmp, out_json)
    return ref


def load_reference(path: Path = MIX_REFERENCE) -> dict:
    if Path(path).exists():
        return json.loads(Path(path).read_text(encoding="utf-8"))
    return {"schema_version": 1, "n_songs": 0, "per_band": {}, "overall": {"lufs_integrated_median": -14.0, "crest_factor_db_median": None, "spectral_tilt_db_median": None},
            "target_lufs": -14.0, "true_peak_dbtp": TRUE_PEAK_DBTP, "source": "absent (defaults)"}


# ----------------------------------------------------------------------------------------------------------- chain ----
def room_size(band: int, ballad: bool, bpm: float) -> float:
    r = ROOM_BY_BAND.get(int(band), 0.42) + (0.15 if (ballad or bpm < 90.0) else 0.0) - (0.10 if bpm > 130.0 else 0.0)
    return float(min(0.75, max(0.25, r)))


def _u(tag: str) -> float:
    from scripts.v6.gen.common import u
    return u(tag)


def song_target_lufs(reference: dict, band: int, tag: str) -> tuple[float, dict]:
    """Iteration 05: one loudness target PER SONG, drawn (SHA inverse-CDF, sorted values) from the band's per-song corpus LUFS list
    (fallback: all songs), clamped to TARGET_LUFS_CLAMP. Iteration 04 songs all sat at the one target (sd 0.55 LU vs 3.4 in the corpus)."""
    rows = [r for r in reference.get("per_song", []) if int(r.get("band", -1)) == int(band)] or list(reference.get("per_song", []))
    vals = sorted(float(r["lufs_integrated"]) for r in rows if r.get("lufs_integrated") is not None)
    fixed = float(reference.get("target_lufs", -14.0))
    if not vals:
        return fixed, {"rule": "fixed (no per-song reference)", "target_lufs": fixed}
    x = _u(f"{tag}|mix|target_lufs")
    raw = vals[min(len(vals) - 1, int(x * len(vals)))]
    t = clamp_target(raw)
    return t, {"rule": SONG_VARIATION["lufs"], "draw_u": round(x, 9), "raw_lufs": raw, "target_lufs": t, "pool": {"band": int(band), "n": len(vals), "min": vals[0], "max": vals[-1]},
               "clamp": list(TARGET_LUFS_CLAMP), "fixed_target_lufs": fixed}


def song_room(band: int, ballad: bool, bpm: float, tag: str) -> tuple[float, float, dict]:
    """Iteration 05: per-song room size (+/- room_jitter) and reverb return (+/- return_jitter_db) around the band / tempo rule."""
    base = room_size(band, ballad, bpm)
    ur, ug = _u(f"{tag}|mix|room"), _u(f"{tag}|mix|return")
    rs = float(min(0.75, max(0.25, base + SONG_VARIATION["room_jitter"] * (2.0 * ur - 1.0))))
    ret = REVERB_RETURN_DB + SONG_VARIATION["return_jitter_db"] * (2.0 * ug - 1.0)
    return rs, ret, {"base_room_size": base, "room_size": rs, "return_db": round(ret, 3), "draw_u": [round(ur, 9), round(ug, 9)], "jitter": [SONG_VARIATION["room_jitter"], SONG_VARIATION["return_jitter_db"]]}


def pan_lr(x: np.ndarray, pan: float) -> np.ndarray:
    """Constant-power pan of a mono signal; pan in [-1, 1] (negative = left). Returns (n, 2)."""
    th = (float(pan) + 1.0) * np.pi / 4.0
    return np.stack([x * np.cos(th), x * np.sin(th)], axis=1)


def _delay(x: np.ndarray, sr: int, ms: float) -> np.ndarray:
    d = int(round(sr * ms / 1000.0))
    return np.concatenate([np.zeros(d), x[: len(x) - d]]) if 0 < d < len(x) else x.copy()


def place(x: np.ndarray, mode, melody_pan: float, sr: int = SR) -> np.ndarray:
    """x (n, 2) -> (n, 2) placed stereo signal. Modes: "stereo" (kept), "wide" (side x WIDE_SIDE), ("stereo_pan", pan, width): the
    stem's own mid/side kept (side x width; a mono stem gets a HAAS_MONO_KEYS_MS delayed copy at HAAS_GAIN_DB on the far channel)
    and the mid panned constant-power; ("haas", pan, ms): constant-power pan of the mono sum with the far channel delayed by ms
    (precedence-effect width); a float / "sha": constant-power pan of the mono sum."""
    if mode == "stereo":
        return x
    if mode == "wide":
        mid, side = (x[:, 0] + x[:, 1]) * 0.5, (x[:, 0] - x[:, 1]) * 0.5 * WIDE_SIDE
        return np.stack([mid + side, mid - side], axis=1)
    if isinstance(mode, (tuple, list)):
        kind, pan, param = mode
        th = (float(pan) + 1.0) * np.pi / 4.0
        mid = (x[:, 0] + x[:, 1]) * 0.5
        if kind == "stereo_pan":
            side = (x[:, 0] - x[:, 1]) * 0.5
            e_mid, e_side = float((mid ** 2).sum()), float((side ** 2).sum())
            if e_mid > 0.0 and e_side < 1e-3 * e_mid:  # effectively mono: Haas spread
                side = _delay(mid, sr, HAAS_MONO_KEYS_MS) * (10 ** (HAAS_GAIN_DB / 20.0)) * 0.5
            side = side * float(param)
            return np.stack([mid * np.cos(th) + side, mid * np.sin(th) - side], axis=1)
        if kind == "haas":
            far = _delay(mid, sr, float(param))
            L, R = (mid, far) if pan <= 0.0 else (far, mid)
            return np.stack([L * np.cos(th), R * np.sin(th)], axis=1)
        raise ValueError(mode)
    pan = melody_pan if mode == "sha" else float(mode)
    return pan_lr(x.mean(axis=1), pan)


def early_reflections(send: np.ndarray, sr: int) -> np.ndarray:
    """Six deterministic taps of the mono send with different L/R delays (EARLY_REFLECTIONS_MS) at EARLY_REFLECTION_DB: a decorrelated
    early field that widens the return without touching the direct sound."""
    m = send.mean(axis=1)
    g = 10 ** (EARLY_REFLECTION_DB / 20.0)
    L = sum(_delay(m, sr, ms) for ms in EARLY_REFLECTIONS_MS["L"]) * g / len(EARLY_REFLECTIONS_MS["L"])
    R = sum(_delay(m, sr, ms) for ms in EARLY_REFLECTIONS_MS["R"]) * g / len(EARLY_REFLECTIONS_MS["R"])
    return np.stack([L, R], axis=1)


def process_stem(x: np.ndarray, sr: int, role: str, melody_pan: float = 0.1) -> tuple[np.ndarray, dict]:
    """HPF -> compressor -> RMS gain -> placement. x (n, 2) float32. Returns (stereo, info)."""
    import pedalboard as pb
    head, ratio, att, rel = COMP.get(role, COMP["melody"])
    target = STEM_RMS_DB.get(role, -22.0)
    y = pb.Pedalboard([pb.HighpassFilter(cutoff_frequency_hz=HPF_HZ.get(role, 80.0))])(np.ascontiguousarray(x.T, dtype=np.float32), sr).T.astype(np.float64)
    rms = float(np.sqrt((y ** 2).mean())) if y.size else 0.0
    gain = (10 ** (target / 20.0)) / rms if rms > 1e-9 else 1.0
    gain = float(min(GAIN_CLIP[1], max(GAIN_CLIP[0], gain)))
    thr = target + head
    y = pb.Pedalboard([pb.Compressor(threshold_db=thr, ratio=ratio, attack_ms=att, release_ms=rel)])(np.ascontiguousarray((y * gain).T, dtype=np.float32), sr).T.astype(np.float64)
    mode = PAN.get(role, 0.0)
    y = place(y, mode, melody_pan, sr)
    pan = melody_pan if mode == "sha" else (mode[1] if isinstance(mode, (tuple, list)) else mode)
    info = {"hpf_hz": HPF_HZ.get(role, 80.0), "compressor": {"threshold_db": thr, "ratio": ratio, "attack_ms": att, "release_ms": rel}, "rms_in_dbfs": round(20 * np.log10(max(rms, 1e-9)), 3),
            "rms_out_dbfs": round(20 * np.log10(max(float(np.sqrt((y ** 2).mean())), 1e-9)), 3), "peak_out_dbfs": round(20 * np.log10(max(float(np.abs(y).max()), 1e-9)), 3),
            "gain": round(gain, 6), "gain_db": round(20 * np.log10(gain), 3), "target_rms_dbfs": STEM_RMS_DB.get(role, -22.0), "pan": pan,
            "placement": {"mode": mode[0], "pan": mode[1], "param": mode[2]} if isinstance(mode, (tuple, list)) else {"mode": mode if isinstance(mode, str) else "pan", "pan": pan},
            "reverb_send": REVERB_SEND.get(role, 0.2)}
    return y.astype(np.float32), info


def peak_limit(x: np.ndarray, sr: int, ceiling_db: float = TRUE_PEAK_DBTP, lookahead_ms: float = 5.0, release_ms: float = 80.0) -> tuple[np.ndarray, dict]:
    """Deterministic look-ahead peak limiter on (n, 2): gain = min(1, ceiling/|x|) -> running min over +/-L -> exponential
    release (max-with-decay, log2(n) doubling passes) -> L-point moving average -> x * gain -> true-peak trim."""
    from scipy.ndimage import minimum_filter1d, uniform_filter1d
    a = np.asarray(x, dtype=np.float64)
    ceil = 10 ** (ceiling_db / 20.0) * 0.98  # 0.2 dB of margin for the inter-sample peaks the oversampled check catches
    L = max(1, int(sr * lookahead_ms / 1000.0))
    need = np.minimum(1.0, ceil / np.maximum(np.abs(a).max(axis=1), 1e-12))
    g = minimum_filter1d(need, size=2 * L + 1, mode="nearest")
    d = 1.0 - g  # gain-reduction depth; release: d[n] = max_k d[n-k] * r**k
    r = float(np.exp(-1.0 / (release_ms / 1000.0 * sr)))
    step = 1
    while step < len(d):
        shifted = np.empty_like(d)
        shifted[:step], shifted[step:] = 0.0, d[:-step] * (r ** step)
        d = np.maximum(d, shifted)
        step *= 2
    g = uniform_filter1d(1.0 - d, size=L, mode="nearest")
    y = a * g[:, None]
    tp = true_peak_dbtp(y, sr)
    trim = 10 ** ((ceiling_db - tp) / 20.0) if tp > ceiling_db else 1.0
    y *= trim
    return y, {"ceiling_dbtp": ceiling_db, "lookahead_ms": lookahead_ms, "release_ms": release_ms, "max_gain_reduction_db": round(-20 * np.log10(max(float(g.min()), 1e-9)), 3),
               "fraction_samples_reduced": round(float((g < 0.999).mean()), 6), "true_peak_trim_db": round(20 * np.log10(trim), 3),
               "_gain": g * trim}  # per-sample gain (numpy; popped by master() before the manifest): lets group stems share the master's limiting


def _bus_shelf(x: np.ndarray, sr: int, shelf_db: float) -> np.ndarray:
    """Bus compressor (BUS_COMP) then the tilt-steer high shelf (skipped at 0 dB): the master's pre-normalise processing."""
    import pedalboard as pb
    y = pb.Pedalboard([pb.Compressor(**BUS_COMP)])(np.ascontiguousarray(x.T, dtype=np.float32), sr).T.astype(np.float64)
    if shelf_db != 0.0:
        y = pb.Pedalboard([pb.HighShelfFilter(cutoff_frequency_hz=4000.0, gain_db=shelf_db)])(np.ascontiguousarray(y.T, dtype=np.float32), sr).T.astype(np.float64)
    return y


def master(mix: np.ndarray, sr: int, target_lufs: float, tilt_target_db: float | None, passes: int = 3, groups: dict | None = None) -> tuple[np.ndarray, dict]:
    """Bus comp -> tilt shelf -> normalise/limit passes. `groups` (optional, iteration 05 diagnostics): {name: (n, 2) pre-master
    group bus} is REPLACED in place by the group's mastered version: bus comp + shelf per group, the master's final gain and the
    master's own per-sample limiter gain curve (so the groups sum to the master up to the bus compressor's per-group action).
    The master output itself is unchanged by `groups`."""
    import pedalboard as pb
    y = pb.Pedalboard([pb.Compressor(**BUS_COMP)])(np.ascontiguousarray(mix.T, dtype=np.float32), sr).T.astype(np.float64)
    tilt_before = spectral_tilt_db(y, sr)
    shelf_db = 0.0
    if tilt_target_db is not None:
        cap = TILT_STEER["cap_db"]
        shelf_db = float(min(cap, max(-cap, TILT_STEER["strength"] * (tilt_target_db - tilt_before))))
        y = pb.Pedalboard([pb.HighShelfFilter(cutoff_frequency_hz=4000.0, gain_db=shelf_db)])(np.ascontiguousarray(y.T, dtype=np.float32), sr).T.astype(np.float64)
    pre_lufs = lufs(y, sr)
    history, gain_db, out, linfo, gcurve = [], target_lufs - pre_lufs, y, {}, None
    for i in range(passes):
        out, linfo = peak_limit(y * (10 ** (gain_db / 20.0)), sr, TRUE_PEAK_DBTP, **LIMITER)
        gcurve = linfo.pop("_gain")
        after = lufs(out, sr)
        history.append({"pass": i + 1, "gain_db": round(gain_db, 3), "lufs_after": round(after, 3), "limiter": linfo})
        if abs(after - target_lufs) <= 0.2:
            break
        gain_db += (target_lufs - after)
    final = np.clip(out, -1.0, 1.0)
    if groups is not None:
        lin = 10 ** (history[-1]["gain_db"] / 20.0)
        for name in sorted(groups):
            gx = np.zeros_like(y)
            gx[: groups[name].shape[0]] = groups[name]
            groups[name] = np.clip(_bus_shelf(gx, sr, shelf_db if tilt_target_db is not None else 0.0) * lin * gcurve[:, None], -1.0, 1.0).astype(np.float32)
    info = {"bus_compressor": dict(BUS_COMP), "tilt_before_db": round(tilt_before, 3), "tilt_target_db": tilt_target_db, "tilt_shelf_gain_db": round(shelf_db, 3), "tilt_steer": dict(TILT_STEER),
            "lufs_pre_normalise": round(pre_lufs, 3), "normalise_limit_passes": history, "target_lufs": target_lufs, "lufs_final": round(lufs(final, sr), 3),
            "true_peak_dbtp_final": round(true_peak_dbtp(final, sr), 3), "sample_peak_dbfs_final": round(20 * np.log10(max(float(np.abs(final).max()), 1e-9)), 3),
            "crest_factor_db_final": round(crest_db(final), 3), "spectral_tilt_db_final": round(spectral_tilt_db(final, sr), 3), "clipped_samples": int((np.abs(out) > 1.0).sum()),
            "limiter": linfo}
    return final.astype(np.float32), info


def mix_song(stems: dict, sr: int, band: int, ballad: bool, bpm: float, melody_pan: float, reference: dict | None = None, length_s: float | None = None,
             groups: dict | None = None, tag: str | None = None) -> tuple[np.ndarray, dict]:
    """stems: {role: (n, 2) float32 at sr}. Returns (master (n, 2) float32, mix_manifest dict). `groups` (optional, a dict to fill;
    iteration 05 `--keep-stems`): on return holds {STEM_GROUP name: mastered (n, 2) float32} — each group = its roles' processed stems
    + its own share of the reverb return (the reverb is linear: reverb(sum of sends) = sum of reverb(send) up to float rounding),
    through master(groups=...). The master output is byte-identical with or without `groups`. `tag` (iteration 05; render_song passes the
    patch-plan tag): per-song loudness target (song_target_lufs) and room / return draw (song_room); without a tag the fixed corpus
    target and the band room apply (unchanged pre-iteration-05 behaviour)."""
    import pedalboard as pb
    reference = reference or load_reference()
    band_ref = reference.get("per_band", {}).get(str(int(band))) or reference.get("overall", {})
    target = float(reference.get("target_lufs", -14.0))
    tilt_target = band_ref.get("spectral_tilt_db_median")
    variation = None
    if tag is not None:
        target, vl = song_target_lufs(reference, band, tag)
        rs_song, ret_db, vr = song_room(band, ballad, bpm, tag)
        variation = {"tag": tag, "loudness": vl, "room": vr}
    n = max([s.shape[0] for s in stems.values()] + [int(round((length_s or 0.0) * sr))])
    bus, send, per_stem = np.zeros((n, 2), np.float64), np.zeros((n, 2), np.float64), {}
    gbus = {g: np.zeros((n, 2), np.float64) for g in sorted(set(STEM_GROUP.get(r, "other") for r in stems))} if groups is not None else {}
    gsend = {g: np.zeros((n, 2), np.float64) for g in gbus}
    for role in sorted(stems):
        y, info = process_stem(stems[role], sr, role, melody_pan)
        bus[: y.shape[0]] += y
        send[: y.shape[0]] += y * REVERB_SEND.get(role, 0.2)
        per_stem[role] = info
        if groups is not None:
            gbus[STEM_GROUP.get(role, "other")][: y.shape[0]] += y
            gsend[STEM_GROUP.get(role, "other")][: y.shape[0]] += y * REVERB_SEND.get(role, 0.2)
    rs, return_db = (rs_song, ret_db) if variation else (room_size(band, ballad, bpm), REVERB_RETURN_DB)
    rev = pb.Pedalboard([pb.Reverb(room_size=rs, damping=0.5, wet_level=1.0, dry_level=0.0, width=1.0)])
    ret = rev(np.ascontiguousarray(send.T, dtype=np.float32), sr).T.astype(np.float64) * (10 ** (return_db / 20.0)) + early_reflections(send, sr)
    pre = bus + ret
    if groups is not None:
        for g in gbus:
            rev_g = pb.Pedalboard([pb.Reverb(room_size=rs, damping=0.5, wet_level=1.0, dry_level=0.0, width=1.0)])
            groups[g] = gbus[g] + rev_g(np.ascontiguousarray(gsend[g].T, dtype=np.float32), sr).T.astype(np.float64) * (10 ** (return_db / 20.0)) + early_reflections(gsend[g], sr)
    out, mi = master(pre.astype(np.float32), sr, target, tilt_target, groups=groups)
    man = {"schema_version": 1, "sample_rate": sr, "band": int(band), "ballad": bool(ballad), "bpm": bpm, "per_stem": per_stem,
           "reverb": {"room_size": rs, "damping": 0.5, "return_db": round(return_db, 3), "early_reflections_ms": EARLY_REFLECTIONS_MS, "early_reflection_db": EARLY_REFLECTION_DB,
                      "sends": {r: REVERB_SEND.get(r, 0.2) for r in sorted(stems)}},
           "song_variation": variation, "iteration_05": {"tilt_steer": dict(TILT_STEER), "song_variation_rules": dict(SONG_VARIATION), "applied_song_variation": variation is not None},
           "phase5_targets": {"true_peak_dbtp": TRUE_PEAK_DBTP, "bus_comp": dict(BUS_COMP), "wide_side": WIDE_SIDE, "keys_width": PAN["keys"][2], "comp_haas_ms": PAN["comp_guitar"][2],
                              "iteration_03_gap": "lr_corr 0.973 vs 0.80, width -18.7 vs -12.9 dB, crest 12.6 vs 14.1 dB, peak -2.0 vs -0.03 dBFS"},
           "pre_master": {"peak_dbfs": round(20 * np.log10(max(float(np.abs(pre).max()), 1e-9)), 3), "lufs": round(lufs(pre, sr), 3)},
           "reference": {"source": reference.get("source"), "n_songs": reference.get("n_songs"), "overall": reference.get("overall"), "band_used": band_ref,
                         "target_lufs_rule": reference.get("target_lufs_rule"), "true_peak_dbtp": TRUE_PEAK_DBTP},
           "master": mi, "duration_s": round(out.shape[0] / sr, 4)}
    return out, man


if __name__ == "__main__":  # pragma: no cover
    import sys
    ref = measure_reference()
    print(json.dumps({"n": ref["n_songs"], "overall": ref["overall"], "per_band": ref["per_band"], "target_lufs": ref["target_lufs"]}, indent=1))
    sys.exit(0)
