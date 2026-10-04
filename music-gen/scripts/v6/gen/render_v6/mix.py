#!/usr/bin/python3
"""v6 Phase 4 — per-song mix chain (pedalboard) + corpus-derived loudness/tilt targets.

created: 2026-10-04
milestone: M-V6-RENDER-4/realistic-renderer

Per stem (role): high-pass (bass 30 Hz, keys/guitar 80 Hz, pads 120 Hz, drums 25 Hz, melody 100 Hz), gentle compression
(drums 4:1 fast, bass 3:1, keys/guitar/melody 2:1, pad 1.5:1), RMS gain staging to a per-role level (deterministic gain,
clipped [0.05, 8]), stereo placement (bass + drums centre — bass mono, kit keeps its own stereo image; keys +20 %, guitar
-25 %, pad wide (kept stereo + 1.3 side), melody +/-10 % by a SHA draw, percussion -30 %), a shared reverb bus
(pedalboard.Reverb; room_size from the band and the ballad flag/tempo; per-role sends; bass dry), bus compression 2:1, a
mild high-shelf steer of the spectral tilt toward the band's corpus median (|gain| <= 3 dB), loudness normalisation to the
TARGET (corpus median integrated LUFS clamped to -14 +/- 2) and a true-peak limiter at -1 dBTP (pedalboard.Limiter +
4x-oversampled true-peak verification; up to 3 normalise/limit passes so the final LUFS is within +/-0.5 of target).
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
TRUE_PEAK_DBTP = -1.0
HPF_HZ = {"drums": 25.0, "bass": 30.0, "keys": 80.0, "comp_guitar": 80.0, "melody": 100.0, "pad": 120.0, "percussion": 150.0}
COMP = {"drums": (-14.0, 4.0, 3.0, 80.0), "bass": (-16.0, 3.0, 10.0, 120.0), "keys": (-18.0, 2.0, 15.0, 150.0), "comp_guitar": (-18.0, 2.0, 10.0, 120.0),
        "melody": (-18.0, 2.0, 10.0, 150.0), "pad": (-20.0, 1.5, 30.0, 300.0), "percussion": (-16.0, 3.0, 5.0, 100.0)}  # thr dB, ratio, attack ms, release ms
STEM_RMS_DB = {"drums": -18.0, "bass": -18.0, "keys": -22.0, "comp_guitar": -24.0, "melody": -22.0, "pad": -26.0, "percussion": -27.0}
PAN = {"drums": "stereo", "bass": 0.0, "keys": 0.2, "comp_guitar": -0.25, "pad": "wide", "melody": "sha", "percussion": -0.3}
REVERB_SEND = {"drums": 0.12, "bass": 0.0, "keys": 0.22, "comp_guitar": 0.18, "pad": 0.35, "melody": 0.28, "percussion": 0.15}
ROOM_BY_BAND = {4: 0.45, 5: 0.38, 6: 0.42, 7: 0.55}
GAIN_CLIP = (0.05, 8.0)


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


def pan_lr(x: np.ndarray, pan: float) -> np.ndarray:
    """Constant-power pan of a mono signal; pan in [-1, 1] (negative = left). Returns (n, 2)."""
    th = (float(pan) + 1.0) * np.pi / 4.0
    return np.stack([x * np.cos(th), x * np.sin(th)], axis=1)


def place(x: np.ndarray, mode, melody_pan: float) -> np.ndarray:
    """x (n, 2) -> (n, 2) placed stereo signal."""
    if mode == "stereo":
        return x
    if mode == "wide":
        mid, side = (x[:, 0] + x[:, 1]) * 0.5, (x[:, 0] - x[:, 1]) * 0.5 * 1.3
        return np.stack([mid + side, mid - side], axis=1)
    pan = melody_pan if mode == "sha" else float(mode)
    return pan_lr(x.mean(axis=1), pan)


def process_stem(x: np.ndarray, sr: int, role: str, melody_pan: float = 0.1) -> tuple[np.ndarray, dict]:
    """HPF -> compressor -> RMS gain -> placement. x (n, 2) float32. Returns (stereo, info)."""
    import pedalboard as pb
    thr, ratio, att, rel = COMP.get(role, COMP["melody"])
    board = pb.Pedalboard([pb.HighpassFilter(cutoff_frequency_hz=HPF_HZ.get(role, 80.0)), pb.Compressor(threshold_db=thr, ratio=ratio, attack_ms=att, release_ms=rel)])
    y = board(np.ascontiguousarray(x.T, dtype=np.float32), sr).T.astype(np.float64)
    rms = float(np.sqrt((y ** 2).mean())) if y.size else 0.0
    gain = (10 ** (STEM_RMS_DB.get(role, -22.0) / 20.0)) / rms if rms > 1e-9 else 1.0
    gain = float(min(GAIN_CLIP[1], max(GAIN_CLIP[0], gain)))
    y = place(y * gain, PAN.get(role, 0.0), melody_pan)
    info = {"hpf_hz": HPF_HZ.get(role, 80.0), "compressor": {"threshold_db": thr, "ratio": ratio, "attack_ms": att, "release_ms": rel}, "rms_in_dbfs": round(20 * np.log10(max(rms, 1e-9)), 3),
            "gain": round(gain, 6), "gain_db": round(20 * np.log10(gain), 3), "target_rms_dbfs": STEM_RMS_DB.get(role, -22.0), "pan": PAN.get(role, 0.0) if PAN.get(role) != "sha" else melody_pan,
            "reverb_send": REVERB_SEND.get(role, 0.2)}
    return y.astype(np.float32), info


def master(mix: np.ndarray, sr: int, target_lufs: float, tilt_target_db: float | None, passes: int = 3) -> tuple[np.ndarray, dict]:
    import pedalboard as pb
    y = pb.Pedalboard([pb.Compressor(threshold_db=-12.0, ratio=2.0, attack_ms=30.0, release_ms=200.0)])(np.ascontiguousarray(mix.T, dtype=np.float32), sr).T
    tilt_before = spectral_tilt_db(y, sr)
    shelf_db = 0.0
    if tilt_target_db is not None:
        shelf_db = float(min(3.0, max(-3.0, 0.5 * (tilt_target_db - tilt_before))))
        y = pb.Pedalboard([pb.HighShelfFilter(cutoff_frequency_hz=4000.0, gain_db=shelf_db)])(np.ascontiguousarray(y.T, dtype=np.float32), sr).T
    history, out = [], y.astype(np.float64)
    for i in range(passes):
        cur = lufs(out, sr)
        g = 10 ** ((target_lufs - cur) / 20.0)
        lim = pb.Pedalboard([pb.Limiter(threshold_db=TRUE_PEAK_DBTP - 0.3, release_ms=120.0)])
        out = lim(np.ascontiguousarray((out * g).T, dtype=np.float32), sr).T.astype(np.float64)
        tp = true_peak_dbtp(out, sr)
        if tp > TRUE_PEAK_DBTP:
            out *= 10 ** ((TRUE_PEAK_DBTP - tp) / 20.0)
        after = lufs(out, sr)
        history.append({"pass": i + 1, "lufs_before": round(cur, 3), "gain_db": round(20 * np.log10(g), 3), "true_peak_dbtp": round(true_peak_dbtp(out, sr), 3), "lufs_after": round(after, 3)})
        if abs(after - target_lufs) <= 0.2:
            break
    final = np.clip(out, -1.0, 1.0)
    info = {"bus_compressor": {"threshold_db": -12.0, "ratio": 2.0, "attack_ms": 30.0, "release_ms": 200.0}, "tilt_before_db": round(tilt_before, 3), "tilt_target_db": tilt_target_db,
            "tilt_shelf_gain_db": round(shelf_db, 3), "normalise_limit_passes": history, "target_lufs": target_lufs, "lufs_final": round(lufs(final, sr), 3),
            "true_peak_dbtp_final": round(true_peak_dbtp(final, sr), 3), "sample_peak_dbfs_final": round(20 * np.log10(max(float(np.abs(final).max()), 1e-9)), 3),
            "crest_factor_db_final": round(crest_db(final), 3), "spectral_tilt_db_final": round(spectral_tilt_db(final, sr), 3), "clipped_samples": int((np.abs(out) > 1.0).sum())}
    return final.astype(np.float32), info


def mix_song(stems: dict, sr: int, band: int, ballad: bool, bpm: float, melody_pan: float, reference: dict | None = None, length_s: float | None = None) -> tuple[np.ndarray, dict]:
    """stems: {role: (n, 2) float32 at sr}. Returns (master (n, 2) float32, mix_manifest dict)."""
    import pedalboard as pb
    reference = reference or load_reference()
    band_ref = reference.get("per_band", {}).get(str(int(band))) or reference.get("overall", {})
    target = float(reference.get("target_lufs", -14.0))
    tilt_target = band_ref.get("spectral_tilt_db_median")
    n = max([s.shape[0] for s in stems.values()] + [int(round((length_s or 0.0) * sr))])
    bus, send, per_stem = np.zeros((n, 2), np.float64), np.zeros((n, 2), np.float64), {}
    for role in sorted(stems):
        y, info = process_stem(stems[role], sr, role, melody_pan)
        bus[: y.shape[0]] += y
        send[: y.shape[0]] += y * REVERB_SEND.get(role, 0.2)
        per_stem[role] = info
    rs = room_size(band, ballad, bpm)
    rev = pb.Pedalboard([pb.Reverb(room_size=rs, damping=0.5, wet_level=1.0, dry_level=0.0, width=1.0)])
    ret = rev(np.ascontiguousarray(send.T, dtype=np.float32), sr).T.astype(np.float64) * (10 ** (-10.0 / 20.0))
    pre = bus + ret
    out, mi = master(pre.astype(np.float32), sr, target, tilt_target)
    man = {"schema_version": 1, "sample_rate": sr, "band": int(band), "ballad": bool(ballad), "bpm": bpm, "per_stem": per_stem,
           "reverb": {"room_size": rs, "damping": 0.5, "return_db": -10.0, "sends": {r: REVERB_SEND.get(r, 0.2) for r in sorted(stems)}},
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
