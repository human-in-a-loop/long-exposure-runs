#!/usr/bin/python3
"""v6 Phase 0 — robust tempo estimator; the SOURCE of bpm_v5 for the v5 transcription driver.

created: 2026-10-04
milestone: M-V6-DATA-0/tempo-v6

Per song (mono @ 22050 Hz, onset-strength envelope at hop 512 = 43.07 fps):
  (a) bpm_beat_track : librosa.beat.beat_track(start_bpm=120)                       [the v4/v5 baseline number]
  (b) bpm_autocorr   : dominant onset-autocorrelation peak in [40, 240] BPM, parabolic sub-lag interpolation,
                       half/double-time resolution: the member of {p/2, p, 2p} inside the band [70, 180] with the
                       highest onsets-per-beat plausibility (ties -> stronger autocorrelation)
  (c) bpm_prior      : librosa.feature.tempo with an explicit log-normal prior (median 110 BPM, sigma = ln2/2)
  Drum-ish onset rate = librosa.onset.onset_detect on the PERCUSSIVE (HPSS) onset envelope, in onsets per second;
  onsets-per-beat(bpm) = rate * 60 / bpm.

Resolution rule (pre-declared; FD-1: recorded, never retuned):
  * estimators are compared by OCTAVE CLASS (below); raw and band-folded values are both recorded;
  * a candidate WINS iff its onsets-per-beat lies in [1, 4] (5 % margin) AND it agrees (+/-4 %, octave class) with
    >= 2 of the 3 estimators (itself included); highest agreement wins, ties -> autocorr, beat_track, prior order;
  * else the autocorrelation peak in [70, 180] with the highest onsets-per-beat plausibility (log-Gaussian centred
    on 2 per beat, zero outside [1, 4]) wins with confidence "low";
  * else confidence "ambiguous" and the folded autocorrelation candidate is served (disclosed).
  Agreement is OCTAVE-CLASS agreement (|x / (y * 2^k) - 1| <= 4 % for k in -2..2), so a beat_track 161.5 and an
  autocorr 79.75 count as agreeing; the served value is the winning estimator's OWN value, octave-folded into the band
  only if outside it; another in-band octave {v/2, 2v} is served only when the own octave's onsets-per-beat is outside
  [1, 4] and the alternative's is inside (none plausible -> "ambiguous", own/nearest in-band octave served, disclosed).
  3:2 check (metrical comb; pre-declared, FD-1): comb(x) = mean normalised autocorrelation at lags {1/2, 1, 2, 4} x
  lag(x). If a 3:2 relative r in {1.5 x, x / 1.5} (octave-folded into the band) has comb(r) - comb(x) >= 0.05 AND r is
  supported by >= 1 estimator or top-8 autocorrelation peak (octave-class, 4 %), r replaces x with confidence "low"
  and flag "3_2_resolved_by_metrical_comb" (the Disco A / Walking On A Dream class of error: 80.75 vs 120.27, 84.7 vs
  127.0). Octave relatives are NOT comb-compared (the comb is octave-invariant by construction).
  Refinement: bpm_v6 = parabolic-interpolated autocorrelation peak within +/-4 % of the winner when one exists with
  ac >= 0.5 x the dominant peak (this is the "refined-lag dominant" that produced the operator-adopted Disco A value
  120.272335), else the winner itself. The beat-grid mean inter-beat BPM (beat_track at the winner, tightness 400) and the raw
  lag-quantized value are recorded as cross-checks, never served.
  Beat-grid cross-check: beat_track(start_bpm = bpm_v6, tightness 400) mean inter-beat BPM; octave-class disagreement
  (> 4 %) with bpm_v6 sets flag "grid_disagrees" and caps confidence at "low". Flags never change the served value.
  Overrides (data/v6/corpus/tempo_overrides_v6.json) are applied LAST; the served value is recorded as bpm_v5.

Outputs: data/v6/corpus/<sha16>/tempo_v6.json (full record), data/v5/corpus/<sha16>/tempo_v5.json (bpm_v5 for
scripts/v5/transcribe_full_length.py + generate_v5.donor_tempo), data/v6/corpus/tempo_v6_summary.tsv (+ a copy as
data/v5/corpus/tempo_v5_summary.tsv), data/v6/corpus/tempo_v6_summary.json (validation block).
Validation (reported + exit 1 unless --no-strict): WIG within 2 % of 99.38, Rome within 2 % of 152.0,
Disco A == 120.272335 after override.

Determinism: per-song work is a pure function of the mp3 bytes; multiprocessing (--jobs) only parallelises songs
(each worker inherits the 1-thread BLAS pins). No PRNG. Sorted-key atomic JSON. /usr/bin/python3 guard.
"""
from __future__ import annotations

import argparse
import math
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

_WS = Path(__file__).resolve().parent.parent.parent
if str(_WS) not in sys.path:
    sys.path.insert(0, str(_WS))
from scripts.v6.v6_data_common import (  # noqa: E402
    ENV_PIN_SHA256, FOCUS, MANIFEST_V5, TEMPO_OVERRIDES_V6, V5_CORPUS, V6_CORPUS, WS, ensure_tempo_overrides_file,
    interpreter_guard, load_tempo_overrides, manifest_songs, pin_env, read_json, sha256_file, write_json_atomic,
    write_text_atomic)

pin_env()
interpreter_guard()

import numpy as np  # noqa: E402

SCHEMA_VERSION = 1
SR = 22050
HOP = 512
BAND = (70.0, 180.0)
AC_SEARCH = (40.0, 240.0)
AGREE_TOL = 0.04
OPB_RANGE = (1.0, 4.0)
OPB_MARGIN = 0.05
OPB_LOG_CENTER = math.log(2.0)
OPB_LOG_SIGMA = 0.5
PRIOR_MEDIAN_BPM = 110.0
PRIOR_SIGMA = math.log(2.0) / 2.0
GRID_TIGHTNESS = 400
N_AC_PEAKS = 8
COMB_MULTS = (0.5, 1.0, 2.0, 4.0)
COMB_MARGIN = 0.05
THREE_TWO = (1.5, 1.0 / 1.5)
REFINE_AC_FRAC = 0.5
VALIDATION = {"252eb21ce7df7328": {"name": "WIG", "reference_bpm": 99.38, "tol_frac": 0.02, "kind": "within_2pct"},
              "51e433ade2a845e1": {"name": "Rome", "reference_bpm": 152.0, "tol_frac": 0.02, "kind": "within_2pct"},
              "cdd2717e52820ff6": {"name": "Disco A", "reference_bpm": 120.272335, "tol_frac": 0.0, "kind": "equals_after_override"}}
PARAMS = {"sr": SR, "hop": HOP, "band": list(BAND), "ac_search_bpm": list(AC_SEARCH), "agree_tol_frac": AGREE_TOL,
          "opb_range": list(OPB_RANGE), "opb_margin_frac": OPB_MARGIN, "opb_plausibility": "exp(-(ln(opb)-ln 2)^2 / (2*0.5^2)) inside [1,4], else 0",
          "prior": {"family": "lognorm", "median_bpm": PRIOR_MEDIAN_BPM, "sigma_ln": PRIOR_SIGMA}, "beat_track_start_bpm": 120.0,
          "grid_tightness": GRID_TIGHTNESS, "n_ac_peaks": N_AC_PEAKS, "onset_rate_source": "HPSS percussive onset envelope -> onset_detect",
          "refinement": "parabolic-interpolated hop-512 autocorrelation peak within +/-4 % of the winner, ac >= 0.5 x dominant peak",
          "agreement": "octave-class (k in -2..2), 4 %", "octave_choice": "winning estimator's own octave unless its opb is outside [1,4] and an in-band octave's is inside", "comb_lag_multiples": list(COMB_MULTS), "comb_margin": COMB_MARGIN,
          "three_two_relatives": [1.5, round(1.0 / 1.5, 6)], "grid_disagree_tol_frac": AGREE_TOL, "resolver_version": "v6.2"}


# ------------------------------------------------------------------------------------------------ pure helpers ----
def lag_to_bpm(lag: float) -> float:
    return 60.0 * SR / (HOP * lag)


def bpm_to_lag(bpm: float) -> float:
    return 60.0 * SR / (HOP * bpm)


def fold_to_band(bpm: float) -> float:
    """Octave-fold into [70, 180]; values that cannot be folded (<35 or >360 after folding) are returned folded as far as possible."""
    if bpm <= 0 or not math.isfinite(bpm):
        return bpm
    b = bpm
    for _ in range(4):
        if b < BAND[0]:
            b *= 2.0
        elif b > BAND[1]:
            b /= 2.0
        else:
            break
    return b


def ac_peaks(ac: np.ndarray, lo_bpm: float, hi_bpm: float, k: int = N_AC_PEAKS) -> list[dict]:
    """Local maxima of the normalised autocorrelation between lo_bpm and hi_bpm, parabolic sub-lag interpolation."""
    lo = int(math.floor(bpm_to_lag(hi_bpm)))
    hi = int(math.ceil(bpm_to_lag(lo_bpm)))
    out = []
    for lag in range(max(2, lo), min(len(ac) - 2, hi) + 1):
        if ac[lag] >= ac[lag - 1] and ac[lag] >= ac[lag + 1]:
            a, b, c = float(ac[lag - 1]), float(ac[lag]), float(ac[lag + 1])
            den = a - 2.0 * b + c
            d = 0.5 * (a - c) / den if abs(den) > 1e-12 else 0.0
            d = max(-0.5, min(0.5, d))
            out.append({"ac": round(b, 6), "lag": lag, "lag_interp": round(lag + d, 4),
                        "bpm_lag": round(lag_to_bpm(lag), 6), "bpm_interp": round(lag_to_bpm(lag + d), 6)})
    out.sort(key=lambda p: (-p["ac"], p["lag"]))
    return out[:k]


def opb_plausibility(opb: float) -> float:
    lo, hi = OPB_RANGE[0] * (1 - OPB_MARGIN), OPB_RANGE[1] * (1 + OPB_MARGIN)
    if not (lo <= opb <= hi) or opb <= 0:
        return 0.0
    return math.exp(-((math.log(opb) - OPB_LOG_CENTER) ** 2) / (2.0 * OPB_LOG_SIGMA ** 2))


def opb_ok(opb: float) -> bool:
    return OPB_RANGE[0] * (1 - OPB_MARGIN) <= opb <= OPB_RANGE[1] * (1 + OPB_MARGIN)


def within(a: float, b: float, tol: float = AGREE_TOL) -> bool:
    return b > 0 and abs(a - b) / b <= tol


def octave_within(a: float, b: float, tol: float = AGREE_TOL) -> bool:
    """True when a is within tol of b x 2^k for some k in -2..2 (octave-class agreement)."""
    if a <= 0 or b <= 0:
        return False
    k = round(math.log2(a / b))
    k = max(-2, min(2, k))
    return abs(a / (b * 2.0 ** k) - 1.0) <= tol


def comb_score(ac: np.ndarray, bpm: float) -> dict:
    """Metrical comb: normalised autocorrelation at {1/2, 1, 2, 4} x the beat lag (bpm / m), mean over the four."""
    vals = {str(m): ac_at(ac, bpm / m, 0.03) for m in COMB_MULTS}
    return {"per_lag_multiple": vals, "mean": round(float(np.mean(list(vals.values()))), 6)}


def octave_members_in_band(v: float) -> list[float]:
    return [round(v * m, 6) for m in (0.5, 1.0, 2.0) if BAND[0] <= v * m <= BAND[1]]


def resolve(est_raw: dict[str, float], onset_rate_hz: float, peaks_in_band: list[dict]) -> dict:
    """Pre-declared resolution over the three raw estimates (order autocorr, beat_track, prior): octave-class agreement;
    the winner's own octave is served (folded into [70, 180] if outside), another in-band octave only if the own one's
    onsets-per-beat is outside [1, 4] and the alternative's is inside."""
    order = ("autocorr", "beat_track", "prior")
    agree = {k: sum(1 for j in order if octave_within(est_raw[j], est_raw[k])) for k in order}
    rows = []
    for k in order:
        members = octave_members_in_band(est_raw[k]) or [round(fold_to_band(est_raw[k]), 6)]
        # own octave first (folded into the band only if outside it); another in-band octave is served only when the own
        # octave's onsets-per-beat is outside [1, 4] and the alternative's is inside (the brief's opb clause, nothing more)
        scored = sorted(((opb_plausibility(onset_rate_hz * 60.0 / m), m) for m in members),
                        key=lambda t: (0 if t[0] > 0 else 1, abs(math.log(t[1] / est_raw[k]))))
        pl, served = scored[0]
        rows.append({"estimator": k, "bpm_raw": est_raw[k], "octave_members_in_band": members, "served_octave_bpm": served,
                     "opb": round(onset_rate_hz * 60.0 / served, 4), "opb_plausibility": round(pl, 6), "opb_ok": pl > 0, "agreement": agree[k]})
    flags: list[str] = []
    cands = [r for r in rows if r["agreement"] >= 2]
    if cands:
        best = sorted(cands, key=lambda r: (-r["agreement"], order.index(r["estimator"])))[0]
        conf = "high" if best["agreement"] == 3 else "medium"
        if not best["opb_ok"]:
            conf = "ambiguous"
            flags.append("opb_implausible_for_every_in_band_octave")
        return {"winner_bpm": best["served_octave_bpm"], "winner_source": best["estimator"], "rule": "octave_class_agreement", "n_agree": best["agreement"],
                "confidence": conf, "candidates": rows, "flags": flags}
    scored = []
    for p in peaks_in_band:
        o = onset_rate_hz * 60.0 / p["bpm_interp"]
        scored.append((opb_plausibility(o), p["ac"], p))
    scored = [t for t in scored if t[0] > 0]
    if scored:
        scored.sort(key=lambda t: (-t[0], -t[1], t[2]["lag"]))
        pl, acv, p = scored[0]
        return {"winner_bpm": p["bpm_interp"], "winner_source": "autocorr_peak_plausibility", "rule": "fallback_opb_plausibility",
                "n_agree": max(agree.values()), "confidence": "low", "candidates": rows, "flags": flags + ["no_estimator_agreement"],
                "fallback": {"plausibility": round(pl, 6), "ac": acv, "peak": p}}
    return {"winner_bpm": rows[0]["served_octave_bpm"], "winner_source": "autocorr_folded_unresolved", "rule": "none",
            "n_agree": max(agree.values()), "confidence": "ambiguous", "candidates": rows, "flags": flags + ["no_estimator_agreement", "no_plausible_ac_peak"]}


# ------------------------------------------------------------------------------------------------- estimation -----
def estimate_from_signal(y: np.ndarray, sr: int, sha16: str = "", overrides: dict | None = None) -> dict:
    """Full per-song record from a mono float signal (tests call this with synthetic clicks)."""
    import librosa
    import scipy.stats
    if sr != SR:
        y = librosa.resample(np.asarray(y, dtype=np.float32), orig_sr=sr, target_sr=SR, res_type="soxr_hq")
        sr = SR
    y = np.asarray(y, dtype=np.float32)
    duration = float(len(y)) / sr
    oenv = librosa.onset.onset_strength(y=y, sr=sr, hop_length=HOP)
    # (a) beat_track baseline
    t_a, _ = librosa.beat.beat_track(onset_envelope=oenv, sr=sr, hop_length=HOP, start_bpm=120.0)
    bpm_a = float(np.atleast_1d(t_a)[0])
    # (b) autocorrelation
    ac = librosa.autocorrelate(oenv)
    ac = ac / (float(ac[0]) + 1e-12)
    peaks = ac_peaks(ac, AC_SEARCH[0], AC_SEARCH[1])
    peaks_band = [p for p in ac_peaks(ac, BAND[0], BAND[1], k=N_AC_PEAKS) if BAND[0] <= p["bpm_interp"] <= BAND[1]]
    # (c) prior-based tempo
    prior = scipy.stats.lognorm(s=PRIOR_SIGMA, scale=PRIOR_MEDIAN_BPM)
    t_c = librosa.feature.tempo(onset_envelope=oenv, sr=sr, hop_length=HOP, prior=prior, aggregate=np.mean)
    bpm_c = float(np.atleast_1d(t_c)[0])
    # drum-ish onset rate (percussive component)
    y_perc = librosa.effects.percussive(y)
    oenv_p = librosa.onset.onset_strength(y=y_perc, sr=sr, hop_length=HOP)
    onsets = librosa.onset.onset_detect(onset_envelope=oenv_p, sr=sr, hop_length=HOP, units="frames")
    onset_rate = float(len(onsets)) / duration if duration > 0 else 0.0
    # (b) half/double-time resolution of the dominant AC peak
    if peaks:
        dom = peaks[0]
        fam = []
        for mult, rel in ((0.5, "half"), (1.0, "same"), (2.0, "double")):
            b = dom["bpm_interp"] * mult
            if BAND[0] <= b <= BAND[1]:
                o = onset_rate * 60.0 / b
                acv = ac_at(ac, b)
                fam.append({"bpm": round(b, 6), "relation": rel, "opb": round(o, 4), "plausibility": round(opb_plausibility(o), 6), "ac_at_lag": acv})
        if fam:
            fam.sort(key=lambda f: (-f["plausibility"], -f["ac_at_lag"]))
            bpm_b = fam[0]["bpm"]
            b_rel = fam[0]["relation"]
        else:  # dominant period has no octave member in band (e.g. 240 BPM -> 120 is in band; this branch is near-unreachable)
            bpm_b = fold_to_band(dom["bpm_interp"])
            b_rel = "folded"
        autocorr_block = {"dominant": dom, "octave_family_in_band": fam, "resolved_bpm": round(bpm_b, 6), "resolved_relation": b_rel,
                          "peaks_top": peaks, "peaks_in_band": peaks_band}
    else:
        bpm_b, autocorr_block = bpm_a, {"dominant": None, "note": "no autocorrelation peak found", "peaks_in_band": []}
    raw = {"beat_track": round(bpm_a, 6), "autocorr": round(bpm_b, 6), "prior": round(bpm_c, 6)}
    folded = {k: round(fold_to_band(v), 6) for k, v in raw.items()}
    res = resolve(raw, onset_rate, peaks_band)
    flags: list[str] = list(res.get("flags", []))
    winner = float(res["winner_bpm"])
    pre_comb_winner = winner
    # 3:2 check (metrical comb) — only against 3:2 relatives supported by an estimator or a top-8 AC peak
    comb_w = comb_score(ac, winner)
    comb = {"winner": {"bpm": round(winner, 6), **comb_w}, "relatives": [], "margin": COMB_MARGIN, "replaced": False}
    support_pool = list(raw.values()) + [p["bpm_interp"] for p in peaks]
    best_rel = None
    for mult in THREE_TWO:
        r = fold_to_band(winner * mult)
        if not (BAND[0] <= r <= BAND[1]):
            continue
        c_r = comb_score(ac, r)
        supported = any(octave_within(r, v) for v in support_pool)
        entry = {"bpm": round(r, 6), "relation": "x1.5" if mult > 1 else "/1.5", **c_r, "delta_vs_winner": round(c_r["mean"] - comb_w["mean"], 6),
                 "supported_by_estimator_or_peak": supported, "opb": round(onset_rate * 60.0 / r, 4)}
        comb["relatives"].append(entry)
        if supported and entry["delta_vs_winner"] >= COMB_MARGIN and (best_rel is None or entry["delta_vs_winner"] > best_rel["delta_vs_winner"]):
            best_rel = entry
    if best_rel is not None:
        winner = float(best_rel["bpm"])
        comb["replaced"] = True
        comb["pre_comb_winner_bpm"] = round(pre_comb_winner, 6)
        flags.append("3_2_resolved_by_metrical_comb")
        res["confidence"] = "low"
        res["winner_source"] = f"metrical_comb({best_rel['relation']} of {res['winner_source']})"
    # refinement: interpolated AC peak within +/-4 % of the winner, strong enough relative to the dominant peak
    refined_from = None
    ac_floor = REFINE_AC_FRAC * (peaks[0]["ac"] if peaks else 0.0)
    near = [p for p in ac_peaks(ac, winner / 1.06, winner * 1.06, k=4) if within(p["bpm_interp"], winner) and p["ac"] >= ac_floor]
    if near:
        near.sort(key=lambda p: -p["ac"])
        bpm_v6 = float(near[0]["bpm_interp"])
        refined_from = near[0]
    else:
        bpm_v6 = winner
    # beat-grid cross-check at the winner
    _t2, beats = librosa.beat.beat_track(onset_envelope=oenv, sr=sr, hop_length=HOP, start_bpm=bpm_v6, tightness=GRID_TIGHTNESS, units="time")
    beats = np.asarray(beats, dtype=float)
    grid = {"n_beats": int(len(beats))}
    if len(beats) > 2:
        iv = np.diff(beats)
        grid.update({"mean_interval_bpm": round(60.0 * (len(beats) - 1) / float(beats[-1] - beats[0]), 6),
                     "median_interval_bpm": round(60.0 / float(np.median(iv)), 6),
                     "interval_cv": round(float(np.std(iv) / np.mean(iv)), 6)})
        grid["mean_within_2pct_of_bpm_v6"] = within(grid["mean_interval_bpm"], bpm_v6, 0.02)
        grid["octave_class_agrees"] = octave_within(grid["mean_interval_bpm"], bpm_v6)
        if not grid["octave_class_agrees"]:
            flags.append("grid_disagrees")
            if res["confidence"] in ("high", "medium"):
                res["confidence"] = "low"
    # overrides last
    overrides = overrides or {}
    override = overrides.get(sha16)
    bpm_served = float(override) if override is not None else bpm_v6
    rec = {"schema_version": SCHEMA_VERSION, "sha16": sha16, "env_pin_sha256": ENV_PIN_SHA256, "params": PARAMS,
           "duration_s": round(duration, 3), "n_onset_frames": int(len(oenv)),
           "estimators_raw": raw, "estimators_folded": folded,
           "onset_rate_hz": round(onset_rate, 6), "n_onsets_percussive": int(len(onsets)),
           "onsets_per_beat_at_bpm_v6": round(onset_rate * 60.0 / bpm_v6, 4) if bpm_v6 > 0 else None,
           "autocorr": autocorr_block, "resolution": res, "winner_bpm": round(winner, 6), "metrical_comb": comb, "flags": flags,
           "refinement": {"bpm_v6": round(bpm_v6, 6), "from_ac_peak": refined_from, "applied": refined_from is not None},
           "beat_grid_check": grid, "bpm_v6_estimate": round(bpm_v6, 6),
           "override": {"applied": override is not None, "bpm": override, "source": "data/v6/corpus/tempo_overrides_v6.json" if override is not None else None},
           "bpm_v5": round(bpm_served, 6), "confidence": res["confidence"] if override is None else "override",
           "estimator_agreement": {"n_agree": res["n_agree"], "rule": res["rule"], "winner_source": res["winner_source"], "flags": flags},
           "octave_relation_to_beat_track": octave_relation(bpm_served, bpm_a)}
    return rec


def ac_at(ac: np.ndarray, bpm: float, tol: float = 0.02) -> float:
    lag = bpm_to_lag(bpm)
    lo, hi = max(1, int(math.floor(lag * (1 - tol)))), min(len(ac) - 1, int(math.ceil(lag * (1 + tol))))
    return round(float(ac[lo:hi + 1].max()), 6) if hi >= lo else 0.0


def octave_relation(a: float, b: float) -> str:
    if b <= 0:
        return "other"
    r = a / b
    for target, name in ((1.0, "same"), (2.0, "double"), (0.5, "half"), (1.5, "three_halves"), (2 / 3, "two_thirds")):
        if abs(r - target) / target <= 0.03:
            return name
    return "other"


def estimate_file(audio_path: Path, sha16: str, overrides: dict | None) -> dict:
    import librosa
    y, sr = librosa.load(str(audio_path), sr=SR, mono=True)
    rec = estimate_from_signal(y, sr, sha16, overrides)
    rec["audio_path"] = str(audio_path.relative_to(WS)) if audio_path.is_absolute() and audio_path.is_relative_to(WS) else str(audio_path)
    rec["librosa_version"] = librosa.__version__
    return rec


def _worker(job: tuple) -> dict:
    sha16, path, title, overrides = job
    t0 = time.time()
    rec = estimate_file(WS / path, sha16, overrides)
    rec["title"] = title
    rec["wall_s"] = round(time.time() - t0, 1)
    return rec


def v5_record(rec: dict) -> dict:
    """The small per-song file the v5 driver + generator read (key bpm_v5)."""
    return {"schema_version": SCHEMA_VERSION, "source": "scripts/v6/tempo_v6.py", "sha16": rec["sha16"], "title": rec.get("title"),
            "env_pin_sha256": ENV_PIN_SHA256, "bpm_v5": rec["bpm_v5"], "bpm_v6_estimate": rec["bpm_v6_estimate"],
            "bpm_librosa": rec["estimators_raw"]["beat_track"], "estimators_raw": rec["estimators_raw"],
            "confidence": rec["confidence"], "override_applied": rec["override"]["applied"], "override_bpm": rec["override"]["bpm"],
            "octave_relation_to_librosa": rec["octave_relation_to_beat_track"], "flags": rec.get("flags", []), "full_record": f"data/v6/corpus/{rec['sha16']}/tempo_v6.json",
            "note": "bpm_v5 is the value consumed by scripts/v5/transcribe_full_length.py (bar grid) and generate_v5.donor_tempo"}


def _flag_tally(records: dict) -> dict:
    t: dict[str, int] = {}
    for r in records.values():
        for f in r.get("flags", []):
            t[f] = t.get(f, 0) + 1
    return dict(sorted(t.items()))


def validate(records: dict[str, dict]) -> dict:
    out = {}
    for sha16, v in VALIDATION.items():
        r = records.get(sha16)
        if r is None:
            out[sha16] = {"name": v["name"], "present": False, "pass": None}
            continue
        if v["kind"] == "equals_after_override":
            ok = abs(r["bpm_v5"] - v["reference_bpm"]) < 1e-9
            out[sha16] = {"name": v["name"], "present": True, "kind": v["kind"], "reference_bpm": v["reference_bpm"], "bpm_v5": r["bpm_v5"],
                          "bpm_v6_estimate": r["bpm_v6_estimate"], "estimate_delta_frac": round((r["bpm_v6_estimate"] - v["reference_bpm"]) / v["reference_bpm"], 6),
                          "pass": ok}
        else:
            d = (r["bpm_v5"] - v["reference_bpm"]) / v["reference_bpm"]
            out[sha16] = {"name": v["name"], "present": True, "kind": v["kind"], "reference_bpm": v["reference_bpm"], "bpm_v5": r["bpm_v5"],
                          "bpm_v6_estimate": r["bpm_v6_estimate"], "delta_frac": round(d, 6), "tol_frac": v["tol_frac"], "pass": abs(d) <= v["tol_frac"],
                          "override_needed": abs(d) > v["tol_frac"]}
    out["all_pass"] = all(x.get("pass") for x in out.values() if isinstance(x, dict))
    return out


TSV_HDR = ["rank", "sha16", "title", "band", "bpm_v5", "bpm_v6_estimate", "confidence", "n_agree", "rule", "winner_source",
           "bpm_beat_track", "bpm_autocorr", "bpm_prior", "folded_beat_track", "folded_autocorr", "folded_prior",
           "onset_rate_hz", "opb_at_bpm_v6", "grid_mean_bpm", "grid_cv", "comb_winner", "comb_best_3_2", "flags", "override", "octave_vs_librosa", "wall_s"]


def tsv_row(rank: int, s: dict, r: dict) -> list:
    g = r["beat_grid_check"]
    return [rank, r["sha16"], s.get("title"), s.get("band"), r["bpm_v5"], r["bpm_v6_estimate"], r["confidence"], r["estimator_agreement"]["n_agree"],
            r["estimator_agreement"]["rule"], r["estimator_agreement"]["winner_source"],
            r["estimators_raw"]["beat_track"], r["estimators_raw"]["autocorr"], r["estimators_raw"]["prior"],
            r["estimators_folded"]["beat_track"], r["estimators_folded"]["autocorr"], r["estimators_folded"]["prior"],
            r["onset_rate_hz"], r["onsets_per_beat_at_bpm_v6"], g.get("mean_interval_bpm"), g.get("interval_cv"),
            r["metrical_comb"]["winner"]["mean"], max((x["mean"] for x in r["metrical_comb"]["relatives"]), default=None),
            ";".join(r.get("flags", [])), r["override"]["bpm"], r["octave_relation_to_beat_track"], r.get("wall_s")]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="v6 tempo estimator (source of bpm_v5 for the v5 pipeline)")
    ap.add_argument("--manifest", default=str(MANIFEST_V5))
    ap.add_argument("--out-dir-v6", default=str(V6_CORPUS))
    ap.add_argument("--out-dir-v5", default=str(V5_CORPUS))
    ap.add_argument("--overrides", default=str(TEMPO_OVERRIDES_V6))
    ap.add_argument("--songs", nargs="*", default=None, help="subset of sha16")
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--force", action="store_true", help="re-estimate even when tempo_v6.json exists for the same audio sha")
    ap.add_argument("--no-strict", action="store_true", help="do not exit 1 when the WIG / Rome / Disco A validation fails")
    args = ap.parse_args(argv)
    out6, out5 = Path(args.out_dir_v6), Path(args.out_dir_v5)
    ensure_tempo_overrides_file(Path(args.overrides))
    overrides = load_tempo_overrides(Path(args.overrides))
    songs = manifest_songs(Path(args.manifest))
    if args.songs:
        keep = set(args.songs)
        songs = [s for s in songs if s["sha16"] in keep]
    records: dict[str, dict] = {}
    jobs = []
    for s in songs:
        p6 = out6 / s["sha16"] / "tempo_v6.json"
        if p6.exists() and not args.force:
            prev = read_json(p6)
            if prev.get("audio_sha256") == s["audio_sha256"] and prev.get("params") == PARAMS:
                prev_override = overrides.get(s["sha16"])
                if prev["override"]["bpm"] == prev_override:  # cached + same override -> reuse
                    records[s["sha16"]] = prev
                    continue
                # same estimate, different override: re-apply without re-estimating
                prev["override"] = {"applied": prev_override is not None, "bpm": prev_override,
                                    "source": "data/v6/corpus/tempo_overrides_v6.json" if prev_override is not None else None}
                prev["bpm_v5"] = round(float(prev_override), 6) if prev_override is not None else prev["bpm_v6_estimate"]
                prev["confidence"] = "override" if prev_override is not None else prev["resolution"]["confidence"]
                records[s["sha16"]] = prev
                continue
        jobs.append((s["sha16"], s["audio_path"], s.get("title"), overrides))
    t0 = time.time()
    if jobs:
        print(f"estimating {len(jobs)} songs with {args.jobs} workers ({len(records)} cached)", flush=True)
        if args.jobs > 1:
            with ProcessPoolExecutor(max_workers=args.jobs) as ex:
                for rec in ex.map(_worker, jobs):
                    records[rec["sha16"]] = rec
        else:
            for job in jobs:
                records[job[0]] = _worker(job)
    by_sha = {s["sha16"]: s for s in songs}
    for sha16, rec in records.items():
        rec["audio_sha256"] = by_sha[sha16]["audio_sha256"]
        rec["title"] = by_sha[sha16].get("title")
        write_json_atomic(out6 / sha16 / "tempo_v6.json", rec)
        write_json_atomic(out5 / sha16 / "tempo_v5.json", v5_record(rec))
    lines = ["\t".join(TSV_HDR)]
    for s in songs:
        r = records[s["sha16"]]
        lines.append("\t".join("" if v is None else str(v) for v in tsv_row(s["v5_priority_rank"], s, r)))
        print(f"{s['v5_priority_rank']:2d} {s['sha16']} {str(s.get('title'))[:26]:26s} bpm_v5={r['bpm_v5']:8.3f} est={r['bpm_v6_estimate']:8.3f} "
              f"{r['confidence']:9s} agree={r['estimator_agreement']['n_agree']} a={r['estimators_raw']['beat_track']:7.2f} "
              f"b={r['estimators_raw']['autocorr']:7.2f} c={r['estimators_raw']['prior']:7.2f} opb={r['onsets_per_beat_at_bpm_v6']} "
              f"grid={r['beat_grid_check'].get('mean_interval_bpm')} flags={','.join(r.get('flags', [])) or '-'} ovr={r['override']['bpm']}")
    tsv = "\n".join(lines) + "\n"
    write_text_atomic(out6 / "tempo_v6_summary.tsv", tsv)
    write_text_atomic(out5 / "tempo_v5_summary.tsv", tsv)
    val = validate(records)
    conf_tally: dict[str, int] = {}
    for r in records.values():
        conf_tally[r["confidence"]] = conf_tally.get(r["confidence"], 0) + 1
    summary = {"schema_version": SCHEMA_VERSION, "env_pin_sha256": ENV_PIN_SHA256, "params": PARAMS, "n_songs": len(records),
               "overrides_path": str(Path(args.overrides).relative_to(WS)) if Path(args.overrides).is_relative_to(WS) else args.overrides,
               "overrides_sha256": sha256_file(args.overrides), "overrides": overrides,
               "confidence_tally": dict(sorted(conf_tally.items())), "validation": val,
               "per_song": {k: {"bpm_v5": v["bpm_v5"], "bpm_v6_estimate": v["bpm_v6_estimate"], "confidence": v["confidence"],
                                "n_agree": v["estimator_agreement"]["n_agree"], "flags": v.get("flags", []), "title": v.get("title")} for k, v in sorted(records.items())},
               "flag_tally": _flag_tally(records),
               "focus_names": {k: v["name"] for k, v in FOCUS.items()}, "wall_s_this_run": round(time.time() - t0, 1)}
    write_json_atomic(out6 / "tempo_v6_summary.json", summary)
    print(f"confidence tally {summary['confidence_tally']}; wrote {out6 / 'tempo_v6_summary.tsv'} and {out5 / 'tempo_v5_summary.tsv'}")
    for sha16, v in val.items():
        if isinstance(v, dict):
            print(f"  validation {v['name']:8s} {'PASS' if v.get('pass') else 'FAIL'}: {v}")
    if not val["all_pass"]:
        print("VALIDATION FAILED (add an override to data/v6/corpus/tempo_overrides_v6.json only for songs missed by > 2 %)", file=sys.stderr)
        return 0 if args.no_strict else 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
