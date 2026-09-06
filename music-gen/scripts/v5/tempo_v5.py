#!/usr/bin/python3
"""c79 P2 — tempo estimator v5 (onset-autocorrelation-validated, octave-resolved).

created: 2026-09-06T00:00:00Z
cycle: 79
run_id: run-2026-09-06T000000Z
agent: worker
milestone: M-V5-CORPUS-1/tempo-v5-landed-c79

Pre-registered algorithm (c79 research brief §P2, frozen before running):
  1. Load full-length mix mono @ 22050 Hz; onset-strength envelope (hop=512).
  2. Baseline `bpm_librosa` = librosa.beat.beat_track (start_bpm=120 prior) — the
     v4 number that produced WIG 50.17.
  3. Candidates = {bpm_librosa * k : k in (0.5, 1, 2, 4/3, 3/4)} U top-3 onset
     autocorrelation peaks in [70, 180]. Score = normalized autocorrelation at
     the candidate lag (max over integer lags within +/-2 % of the exact lag)
     times plausibility weight (1 in [70,180]; 0.5 in [55,70] U [180,220]; 0
     outside). argmax; ties by SHA-256 of f"{sha16}|{bpm:.4f}" (no PRNG).
  4. Beat-grid consistency: beat_track(start_bpm=chosen, tightness=200);
     beat-interval CV; CV > 0.25 -> grid_unstable.
  5. Per-song JSON + corpus TSV. Falsification targets evaluated as flags only;
     the criterion is NEVER adjusted post hoc (FD-1).

Discipline: /usr/bin/python3 guard; no PRNG; no sidecar_nonfactor; no VST3 state
APIs; c53 rc5 module + c57 musical_time modules are READ-ONLY and NOT imported
(no pure functions reusable for this algorithm).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

_PINS = {"PYTHONHASHSEED": "0", "SOURCE_DATE_EPOCH": "1756463424", "TZ": "UTC",
         "LC_ALL": "C.UTF-8", "OMP_NUM_THREADS": "1", "MKL_NUM_THREADS": "1",
         "OPENBLAS_NUM_THREADS": "1"}
for _k, _v in _PINS.items():
    os.environ.setdefault(_k, _v)

if sys.executable != "/usr/bin/python3" and "SUPPRESS_INTERPRETER_GUARD" not in os.environ:
    print(f"FATAL: expected /usr/bin/python3, got {sys.executable}", file=sys.stderr)
    sys.exit(2)

import numpy as np  # noqa: E402
import librosa  # noqa: E402

_WS = Path(__file__).resolve().parent.parent.parent
ENV_PIN_SHA256 = "2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca"
SR = 22050
HOP = 512
BAND = (70.0, 180.0)
HALF_BAND_LO = (55.0, 70.0)
HALF_BAND_HI = (180.0, 220.0)
MULTIPLIERS = ((0.5, "half"), (1.0, "same"), (2.0, "double"), (4.0 / 3.0, "four_thirds"), (0.75, "three_quarters"))
LAG_WINDOW_FRAC = 0.02
GRID_CV_UNSTABLE = 0.25

# Frozen anchors (operator / prior-cycle tempi). rc5 baseline dir
# data/recreate_v2/baseline/ is ABSENT on this instance (invariant (d)); the
# values below are the on-disk tempo_choice.json numbers.
ANCHORS = {
    "31a164f845f8e27e": {"name": "Chicken Grease", "anchor_bpm": 90.7258064516129,
                         "source": "rc5 anchor via data/v3_spine/31a164f845f8e27e/tempo_choice.json (c4, delta_vs_rc5=0.0); c5 section 90.6661",
                         "tolerance_bpm": 2.0},
    "88d247468cb6d49f": {"name": "Peach Dream", "anchor_bpm": 123.046875,
                         "source": "c20/c25 tempo_choice.json detected_bpm", "tolerance_bpm": 2.0},
    "51e433ade2a845e1": {"name": "Rome", "anchor_bpm": 151.99908088235293,
                         "source": "c20 tempo_choice.json drums_operator_section_bpm (rc5 full-song 152.027)", "tolerance_bpm": 2.0},
    "cdd2717e52820ff6": {"name": "Disco A", "anchor_bpm": 120.18531976744185,
                         "source": "c21 tempo_choice.json drums_operator_section_bpm (rc5 full-song 119.681)", "tolerance_bpm": 2.0},
    "252eb21ce7df7328": {"name": "What If I Go", "anchor_bpm": 50.17445388349515,
                         "source": "c20 tempo_choice.json drums_operator_section_bpm (KNOWN half-time mis-estimate; full-mix section 99.384; rc5 full-song 200.893)",
                         "tolerance_bpm": None,
                         "falsification": "bpm_v5 NOT in [45,56] AND within +/-3 of 100.35 (2 x 50.17) OR disclosed autocorr-dominant alternative in [70,180]"},
}


def plausibility(bpm: float) -> float:
    if BAND[0] <= bpm <= BAND[1]:
        return 1.0
    if HALF_BAND_LO[0] <= bpm < HALF_BAND_LO[1] or HALF_BAND_HI[0] < bpm <= HALF_BAND_HI[1]:
        return 0.5
    return 0.0


def bpm_to_lag(bpm: float) -> float:
    return 60.0 * SR / (HOP * bpm)


def lag_to_bpm(lag: float) -> float:
    return 60.0 * SR / (HOP * lag)


def ac_at_bpm(ac: np.ndarray, bpm: float) -> tuple[float, int]:
    """Max normalized autocorrelation over integer lags within +/-2 % of the exact lag."""
    lag = bpm_to_lag(bpm)
    lo = max(1, int(np.floor(lag * (1 - LAG_WINDOW_FRAC))))
    hi = min(len(ac) - 1, int(np.ceil(lag * (1 + LAG_WINDOW_FRAC))))
    if hi < lo:
        return 0.0, int(round(lag))
    seg = ac[lo:hi + 1]
    i = int(np.argmax(seg))
    return float(seg[i]), lo + i


def top_ac_peaks(ac: np.ndarray, k: int = 3) -> list[dict]:
    lag_lo = int(np.floor(bpm_to_lag(BAND[1])))
    lag_hi = int(np.ceil(bpm_to_lag(BAND[0])))
    peaks = []
    for lag in range(max(2, lag_lo), min(len(ac) - 1, lag_hi) + 1):
        if ac[lag] >= ac[lag - 1] and ac[lag] >= ac[lag + 1]:
            peaks.append((float(ac[lag]), lag))
    peaks.sort(key=lambda t: (-t[0], t[1]))
    return [{"bpm": lag_to_bpm(lag), "lag_frames": lag, "ac": v} for v, lag in peaks[:k]]


def tiebreak(sha16: str, bpm: float) -> str:
    return hashlib.sha256(f"{sha16}|{bpm:.4f}".encode()).hexdigest()


def octave_relation(bpm_v5: float, bpm_librosa: float) -> str:
    r = bpm_v5 / bpm_librosa
    for target, name in ((1.0, "same"), (2.0, "double"), (0.5, "half")):
        if abs(r - target) / target <= 0.03:
            return name
    return "other"


def estimate(audio_path: Path, sha16: str) -> dict:
    y, sr = librosa.load(str(audio_path), sr=SR, mono=True)
    onset_env = librosa.onset.onset_strength(y=y, sr=sr, hop_length=HOP)
    tempo, _beats = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr, hop_length=HOP,
                                            start_bpm=120.0, units="frames")
    bpm_librosa = float(np.asarray(tempo).flatten()[0])

    ac = librosa.autocorrelate(onset_env)
    ac = ac / (ac[0] + 1e-12)

    cands: dict[str, dict] = {}
    for mult, rel in MULTIPLIERS:
        b = bpm_librosa * mult
        cands[f"librosa_x_{rel}"] = {"bpm": b, "origin": f"bpm_librosa*{mult:.4f}", "relation_to_librosa": rel}
    for i, p in enumerate(top_ac_peaks(ac)):
        cands[f"ac_peak_{i + 1}"] = {"bpm": p["bpm"], "origin": f"autocorr_peak_rank_{i + 1}", "lag_frames": p["lag_frames"]}

    scored = []
    for name, c in cands.items():
        b = c["bpm"]
        w = plausibility(b)
        ac_v, lag_i = ac_at_bpm(ac, b) if b > 0 else (0.0, 0)
        c.update({"plausibility_weight": w, "autocorr_norm": round(ac_v, 6),
                  "autocorr_lag_frames": lag_i, "score": round(ac_v * w, 6),
                  "tiebreak_sha256": tiebreak(sha16, b), "bpm": round(b, 6)})
        scored.append((c["score"], c["tiebreak_sha256"], name))
    # argmax score; ties -> LOWEST sha (deterministic, pre-registered)
    scored.sort(key=lambda t: (-t[0], t[1]))
    win = scored[0][2]
    bpm_v5 = cands[win]["bpm"]

    _t2, beats2 = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr, hop_length=HOP,
                                          start_bpm=bpm_v5, tightness=200, units="time")
    beats2 = np.asarray(beats2, dtype=float)
    ivs = np.diff(beats2) if len(beats2) > 2 else np.array([])
    grid_cv = float(np.std(ivs) / np.mean(ivs)) if len(ivs) > 1 and np.mean(ivs) > 0 else None
    grid_median_bpm = float(60.0 / np.median(ivs)) if len(ivs) > 1 else None

    # scores at the pure octave lags of the librosa estimate (for the RULES-IN clause)
    s_T = cands["librosa_x_same"]["autocorr_norm"]
    s_2T = cands["librosa_x_double"]["autocorr_norm"]

    anchor = ANCHORS.get(sha16)
    delta = None
    within = None
    if anchor and anchor.get("anchor_bpm") is not None:
        delta = round(bpm_v5 - anchor["anchor_bpm"], 6)
        if anchor.get("tolerance_bpm") is not None:
            within = abs(delta) <= anchor["tolerance_bpm"]
    flag_half_double = octave_relation(bpm_v5, bpm_librosa) in ("double", "half")
    wig_rules_in = None
    if sha16 == "252eb21ce7df7328":
        wig_rules_in = bool(95.0 <= bpm_v5 <= 106.0 and s_2T >= 1.10 * s_T)

    out = {
        "schema_version": 1, "cycle": 79, "sha16": sha16, "audio_path": str(audio_path),
        "env_pin_sha256": ENV_PIN_SHA256,
        "params": {"sr": SR, "hop": HOP, "band": list(BAND), "half_band_lo": list(HALF_BAND_LO),
                   "half_band_hi": list(HALF_BAND_HI), "lag_window_frac": LAG_WINDOW_FRAC,
                   "grid_cv_unstable": GRID_CV_UNSTABLE, "librosa_version": librosa.__version__,
                   "duration_s": round(len(y) / sr, 3), "n_onset_frames": int(len(onset_env))},
        "bpm_librosa": round(bpm_librosa, 6),
        "bpm_v5": round(bpm_v5, 6),
        "winner_candidate": win,
        "candidates": cands,
        "autocorr_scores": {n: cands[n]["score"] for n in cands},
        "autocorr_at_T": round(s_T, 6), "autocorr_at_2T": round(s_2T, 6),
        "ratio_2T_over_T": round(s_2T / s_T, 6) if s_T > 0 else None,
        "octave_relation_to_librosa": octave_relation(bpm_v5, bpm_librosa),
        "flag_half_double_time": flag_half_double,
        "grid_cv": round(grid_cv, 6) if grid_cv is not None else None,
        "grid_unstable": (grid_cv is not None and grid_cv > GRID_CV_UNSTABLE),
        "grid_median_bpm": round(grid_median_bpm, 6) if grid_median_bpm is not None else None,
        "n_beats_at_bpm_v5": int(len(beats2)),
        "anchors": anchor,
        "delta_vs_anchor_bpm": delta,
        "within_anchor_tolerance": within,
        "wig_rules_in_clause": wig_rules_in,
        # lag table for falsifiable plotting: lags 1..128 frames == 2584..20.2 BPM
        "autocorr_lag_table": {"lag_frames_start": 1,
                               "bpm_per_lag": [round(lag_to_bpm(l), 3) for l in range(1, 129)],
                               "autocorr_norm": [round(float(v), 6) for v in ac[1:129]]},
        "lag_quantization_note": ("librosa tempo estimates are integer-lag quantized at hop=512/22050 Hz "
                                  "(e.g. lag 21 = 123.047 BPM, lag 22 = 117.454, lag 32 = 80.750); "
                                  "resolution near 120 BPM is ~5 BPM, so anchors derived the same way carry that quantization."),
    }
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="v5 tempo estimator (autocorr-validated)")
    ap.add_argument("--manifest", default="data/v5/corpus/corpus_manifest.json")
    ap.add_argument("--out-dir", default="data/v5/corpus")
    ap.add_argument("--songs", nargs="*", default=None, help="subset of sha16 (default: all in_v5_corpus)")
    ap.add_argument("--summary-name", default="tempo_v5_summary.tsv")
    args = ap.parse_args()
    os.chdir(_WS)

    man = json.loads(Path(args.manifest).read_text())
    songs = [s for s in man["songs"] if s.get("in_v5_corpus")]
    if args.songs:
        songs = [s for s in songs if s["sha16"] in set(args.songs)]
    out_dir = Path(args.out_dir)
    rows = []
    for s in songs:
        sha16 = s["sha16"]
        res = estimate(Path(s["audio_path"]), sha16)
        res["title"] = s.get("title")
        d = out_dir / sha16
        d.mkdir(parents=True, exist_ok=True)
        txt = json.dumps(res, sort_keys=True, indent=2) + "\n"
        (d / "tempo_v5.json").write_text(txt)
        rows.append(res)
        print(f"{sha16} {str(s.get('title'))[:28]:28s} librosa={res['bpm_librosa']:8.3f} v5={res['bpm_v5']:8.3f} "
              f"rel={res['octave_relation_to_librosa']:6s} win={res['winner_candidate']:18s} cv={res['grid_cv']} "
              f"dAnchor={res['delta_vs_anchor_bpm']} ok={res['within_anchor_tolerance']}")

    hdr = ["sha16", "title", "bpm_librosa", "bpm_v5", "winner_candidate", "octave_relation_to_librosa",
           "autocorr_at_T", "autocorr_at_2T", "grid_cv", "grid_unstable", "anchor_bpm", "delta_vs_anchor_bpm",
           "within_anchor_tolerance", "flag_half_double_time"]
    lines = ["\t".join(hdr)]
    for r in rows:
        a = (r.get("anchors") or {}).get("anchor_bpm")
        vals = [r["sha16"], str(r.get("title")), r["bpm_librosa"], r["bpm_v5"], r["winner_candidate"],
                r["octave_relation_to_librosa"], r["autocorr_at_T"], r["autocorr_at_2T"], r["grid_cv"],
                r["grid_unstable"], a, r["delta_vs_anchor_bpm"], r["within_anchor_tolerance"],
                r["flag_half_double_time"]]
        lines.append("\t".join(str(v) for v in vals))
    (out_dir / args.summary_name).write_text("\n".join(lines) + "\n")
    print(f"wrote {out_dir / args.summary_name} ({len(rows)} rows)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
