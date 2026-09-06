#!/usr/bin/python3
"""c81 P2 — tempo estimator v5c: harmonic sum read DIRECTLY from the autocorrelation (pre-registered).

created: 2026-09-06T16:52:00Z
cycle: 81
run_id: run-2026-09-06T000000Z
agent: worker
milestone: M-V5-CORPUS-1/tempo_v5c-preregistered-c81

Pre-registered in data/v5/corpus/tempo_v5c_preregistration.json BEFORE any per-song
output (mtime gate enforced by tempo_v5c_verdict.py + tests). Third and FINAL
unaided attempt (FD-1 meta-gate: if this rules out, c82 runs a mechanism probe
before any further criterion is proposed).

Held constant from v5b (READ-ONLY imports): onset envelope, normalized ac,
candidate set = local maxima in the [40,240] BPM lag range, pick band [70,180],
weights (1, 1/2, 1/2), SHA-256 tiebreak, corpus, env pin.

Axis varied: the two harmonic terms are read at the EXACT fractional lags
lag_T/2 and 2*lag_T by linear interpolation between neighbouring integer lags of
the autocorrelation, contributing 0 only when the lag is < 1 frame or beyond the
autocorrelation length. No candidate-band restriction on harmonic terms.

Discipline: /usr/bin/python3 guard; no PRNG; no sidecar_nonfactor; no VST3 state
APIs; tempo_v5.py / tempo_v5b.py + their frozen verdicts NOT modified; no retune.
"""
from __future__ import annotations

import argparse
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

_WS = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_WS))

import numpy as np  # noqa: E402
import librosa  # noqa: E402
from scripts.v5.tempo_v5 import (SR, HOP, BAND, ENV_PIN_SHA256, ANCHORS,  # noqa: E402  READ-ONLY
                                 bpm_to_lag, lag_to_bpm, tiebreak)
from scripts.v5.tempo_v5b import CAND_BAND, HALF_WEIGHT, LAG_TABLE_MAX, local_maxima, candidate_lag_range  # noqa: E402  READ-ONLY

CRITERION = "autocorr_direct_harmonic_sum_v5c"


def interp_ac(ac: np.ndarray, lag: float) -> tuple[float, bool]:
    """Linear interpolation of the normalized autocorrelation at a fractional lag.
    Returns (value, in_range). in_range is False (value 0) when lag < 1 or lag > len(ac)-1."""
    if lag < 1.0 or lag > len(ac) - 1:
        return 0.0, False
    lo = int(np.floor(lag))
    hi = min(lo + 1, len(ac) - 1)
    frac = lag - lo
    v = float(ac[lo]) * (1.0 - frac) + float(ac[hi]) * frac
    return float(v), True


def harmonic_sum_direct(ac: np.ndarray, lag: int) -> dict:
    bpm = lag_to_bpm(lag)
    ac_T = float(ac[lag])
    lag_half = lag / 2.0
    lag_double = 2.0 * lag
    ac_half, half_in = interp_ac(ac, lag_half)
    ac_double, dbl_in = interp_ac(ac, lag_double)
    s = ac_T + HALF_WEIGHT * ac_half + HALF_WEIGHT * ac_double
    return {"bpm": round(bpm, 6), "lag_frames": int(lag), "ac_T": round(ac_T, 6),
            "lag_half_period": round(lag_half, 3), "ac_half_period": round(ac_half, 6), "half_in_autocorr": bool(half_in),
            "lag_double_period": round(lag_double, 3), "ac_double_period": round(ac_double, 6), "double_in_autocorr": bool(dbl_in),
            "s": round(s, 6), "in_pick_band": bool(BAND[0] <= bpm <= BAND[1])}


def estimate(audio_path: Path, sha16: str, bpm_v5: float | None) -> dict:
    y, sr = librosa.load(str(audio_path), sr=SR, mono=True)
    onset_env = librosa.onset.onset_strength(y=y, sr=sr, hop_length=HOP)
    ac = librosa.autocorrelate(onset_env)
    ac = ac / (ac[0] + 1e-12)

    cands = []
    for lag in local_maxima(ac):
        c = harmonic_sum_direct(ac, lag)
        c["tiebreak_sha256"] = tiebreak(sha16, c["bpm"])
        cands.append(c)
    eligible = sorted([c for c in cands if c["in_pick_band"]], key=lambda c: (-c["s"], c["tiebreak_sha256"]))
    winner = eligible[0] if eligible else None
    bpm_v5c = winner["bpm"] if winner else None

    anchor = ANCHORS.get(sha16)
    anchor_bpm = (anchor or {}).get("anchor_bpm")
    flipped = (bpm_v5 is not None and bpm_v5c is not None and abs(bpm_v5c - bpm_v5) > 1e-6)
    # secondary check (Rome): explicit rows at the two contested lags, whether or not they are local maxima
    contested = {str(l): harmonic_sum_direct(ac, l) for l in (17, 25) if l < len(ac) - 1}
    return {
        "schema_version": 1, "cycle": 81, "sha16": sha16, "audio_path": str(audio_path),
        "env_pin_sha256": ENV_PIN_SHA256, "criterion": CRITERION,
        "params": {"sr": SR, "hop": HOP, "candidate_band_bpm": list(CAND_BAND), "pick_band_bpm": list(BAND),
                   "half_weight": HALF_WEIGHT, "candidate_lag_range": list(candidate_lag_range(len(ac))),
                   "harmonic_domain": "autocorrelation-direct, linear interpolation at fractional lag; 0 only if lag < 1 or > len(ac)-1",
                   "librosa_version": librosa.__version__, "duration_s": round(len(y) / sr, 3),
                   "n_onset_frames": int(len(onset_env)), "n_ac": int(len(ac))},
        "bpm_v5": bpm_v5, "bpm_v5c": bpm_v5c, "winner": winner, "flipped_vs_v5": bool(flipped),
        "n_candidates": len(cands), "n_eligible": len(eligible), "candidates": cands,
        "s_scores_top3": [{"bpm": c["bpm"], "s": c["s"]} for c in eligible[:3]],
        "contested_lags_17_25": contested,
        "anchor_bpm": anchor_bpm,
        "delta_vs_anchor_bpm": (round(bpm_v5c - anchor_bpm, 6) if (anchor_bpm is not None and bpm_v5c is not None) else None),
        "autocorr_lag_table": {"lag_frames_start": 1,
                               "bpm_per_lag": [round(lag_to_bpm(l), 3) for l in range(1, LAG_TABLE_MAX + 1)],
                               "autocorr_norm": [round(float(v), 6) for v in ac[1:LAG_TABLE_MAX + 1]]},
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="v5c tempo estimator (autocorrelation-direct harmonic sum)")
    ap.add_argument("--manifest", default="data/v5/corpus/corpus_manifest.json")
    ap.add_argument("--tempo-v5-dir", default="data/v5/corpus")
    ap.add_argument("--out-dir", default="data/v5/corpus")
    ap.add_argument("--songs", nargs="*", default=None)
    ap.add_argument("--summary-name", default="tempo_v5c_summary.tsv")
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
        v5p = Path(args.tempo_v5_dir) / sha16 / "tempo_v5.json"
        bpm_v5 = json.loads(v5p.read_text())["bpm_v5"] if v5p.exists() else None
        res = estimate(Path(s["audio_path"]), sha16, bpm_v5)
        res["title"] = s.get("title")
        d = out_dir / sha16
        d.mkdir(parents=True, exist_ok=True)
        (d / "tempo_v5c.json").write_text(json.dumps(res, sort_keys=True, indent=2) + "\n")
        rows.append(res)
        print(f"{sha16} {str(s.get('title'))[:28]:28s} v5={bpm_v5} v5c={res['bpm_v5c']} flipped={res['flipped_vs_v5']} "
              f"anchor={res['anchor_bpm']} d={res['delta_vs_anchor_bpm']} top3={res['s_scores_top3']}")
    hdr = ["sha16", "title", "bpm_v5", "bpm_v5c", "anchor_bpm", "flipped", "s_scores_top3"]
    lines = ["\t".join(hdr)]
    for r in rows:
        lines.append("\t".join(str(v) for v in [r["sha16"], r.get("title"), r["bpm_v5"], r["bpm_v5c"], r["anchor_bpm"],
                                                r["flipped_vs_v5"], json.dumps(r["s_scores_top3"], separators=(",", ":"))]))
    (out_dir / args.summary_name).write_text("\n".join(lines) + "\n")
    print(f"wrote {out_dir / args.summary_name} ({len(rows)} rows)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
