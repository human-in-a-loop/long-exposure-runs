#!/usr/bin/python3
"""c80 P1 — tempo estimator v5b: harmonic-sum octave selection (pre-registered).

created: 2026-09-06T16:12:00Z
cycle: 80
run_id: run-2026-09-06T000000Z
agent: worker
milestone: M-V5-CORPUS-1/tempo_v5b-preregistered-c80

Pre-registered in data/v5/corpus/tempo_v5b_preregistration.json BEFORE any
per-song output (mtime gate enforced by tempo_v5b_verdict.py + tests).

Held constant from v5 (scripts/v5/tempo_v5.py, READ-ONLY import): mono 22050 Hz,
onset_strength hop 512, normalized autocorrelation (ac[0]=1), the +/-2 % lag
window helper `ac_at_bpm`, the SHA-256 tiebreak, the [70,180] plausibility band
for the FINAL pick, the corpus and the MuScriptor outputs.

Axis varied: candidate set = every local maximum of ac in the lag range for
[40, 240] BPM; score s(T) = ac(lag_T) + 0.5*ac(lag_{T/2}) + 0.5*ac(lag_{2T}),
harmonic terms contributing 0 when their lag falls outside the [40,240] range.
argmax over candidates with BPM in [70,180]; ties -> lowest tiebreak SHA.

Discipline: /usr/bin/python3 guard; no PRNG; no sidecar_nonfactor; no VST3 state
APIs; tempo_v5.py + its frozen verdict are NOT modified; no retune (FD-1).
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
                                 bpm_to_lag, lag_to_bpm, ac_at_bpm, tiebreak)

CAND_BAND = (40.0, 240.0)
HALF_WEIGHT = 0.5
LAG_TABLE_MAX = 128


def candidate_lag_range(n_ac: int) -> tuple[int, int]:
    lag_lo = max(2, int(np.floor(bpm_to_lag(CAND_BAND[1]))))
    lag_hi = min(n_ac - 2, int(np.ceil(bpm_to_lag(CAND_BAND[0]))))
    return lag_lo, lag_hi


def local_maxima(ac: np.ndarray) -> list[int]:
    lo, hi = candidate_lag_range(len(ac))
    return [lag for lag in range(lo, hi + 1) if ac[lag] >= ac[lag - 1] and ac[lag] >= ac[lag + 1]]


def harmonic_term(ac: np.ndarray, bpm: float) -> tuple[float, int | None]:
    """ac at the +/-2 % window around lag(bpm); 0 if the lag is outside the [40,240] BPM range."""
    if not (CAND_BAND[0] <= bpm <= CAND_BAND[1]):
        return 0.0, None
    v, lag = ac_at_bpm(ac, bpm)
    return float(v), int(lag)


def harmonic_sum(ac: np.ndarray, lag: int) -> dict:
    bpm = lag_to_bpm(lag)
    ac_T = float(ac[lag])
    ac_half, lag_half = harmonic_term(ac, 2.0 * bpm)   # period T/2 -> tempo 2*bpm
    ac_double, lag_double = harmonic_term(ac, bpm / 2.0)  # period 2T -> tempo bpm/2
    s = ac_T + HALF_WEIGHT * ac_half + HALF_WEIGHT * ac_double
    return {"bpm": round(bpm, 6), "lag_frames": int(lag), "ac_T": round(ac_T, 6),
            "ac_half_period": round(ac_half, 6), "lag_half_period": lag_half,
            "ac_double_period": round(ac_double, 6), "lag_double_period": lag_double,
            "s": round(s, 6), "in_pick_band": bool(BAND[0] <= bpm <= BAND[1])}


def estimate(audio_path: Path, sha16: str, bpm_v5: float | None) -> dict:
    y, sr = librosa.load(str(audio_path), sr=SR, mono=True)
    onset_env = librosa.onset.onset_strength(y=y, sr=sr, hop_length=HOP)
    ac = librosa.autocorrelate(onset_env)
    ac = ac / (ac[0] + 1e-12)

    cands = []
    for lag in local_maxima(ac):
        c = harmonic_sum(ac, lag)
        c["tiebreak_sha256"] = tiebreak(sha16, c["bpm"])
        cands.append(c)
    eligible = [c for c in cands if c["in_pick_band"]]
    if not eligible:  # honest degenerate case: no local maximum in [70,180]
        winner = None
        bpm_v5b = None
    else:
        eligible_sorted = sorted(eligible, key=lambda c: (-c["s"], c["tiebreak_sha256"]))
        winner = eligible_sorted[0]
        bpm_v5b = winner["bpm"]
    top3 = sorted(eligible, key=lambda c: (-c["s"], c["tiebreak_sha256"]))[:3]

    anchor = ANCHORS.get(sha16)
    anchor_bpm = (anchor or {}).get("anchor_bpm")
    flipped = (bpm_v5 is not None and bpm_v5b is not None and abs(bpm_v5b - bpm_v5) > 1e-6)
    return {
        "schema_version": 1, "cycle": 80, "sha16": sha16, "audio_path": str(audio_path),
        "env_pin_sha256": ENV_PIN_SHA256,
        "criterion": "harmonic_sum_v5b",
        "params": {"sr": SR, "hop": HOP, "candidate_band_bpm": list(CAND_BAND), "pick_band_bpm": list(BAND),
                   "half_weight": HALF_WEIGHT, "candidate_lag_range": list(candidate_lag_range(len(ac))),
                   "librosa_version": librosa.__version__, "duration_s": round(len(y) / sr, 3),
                   "n_onset_frames": int(len(onset_env))},
        "bpm_v5": bpm_v5,
        "bpm_v5b": bpm_v5b,
        "winner": winner,
        "flipped_vs_v5": bool(flipped),
        "n_candidates": len(cands), "n_eligible": len(eligible),
        "candidates": cands,
        "s_scores_top3": [{"bpm": c["bpm"], "s": c["s"]} for c in top3],
        "anchor_bpm": anchor_bpm,
        "delta_vs_anchor_bpm": (round(bpm_v5b - anchor_bpm, 6) if (anchor_bpm is not None and bpm_v5b is not None) else None),
        "autocorr_lag_table": {"lag_frames_start": 1,
                               "bpm_per_lag": [round(lag_to_bpm(l), 3) for l in range(1, LAG_TABLE_MAX + 1)],
                               "autocorr_norm": [round(float(v), 6) for v in ac[1:LAG_TABLE_MAX + 1]]},
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="v5b tempo estimator (harmonic-sum octave selection)")
    ap.add_argument("--manifest", default="data/v5/corpus/corpus_manifest.json")
    ap.add_argument("--tempo-v5-dir", default="data/v5/corpus", help="where <sha16>/tempo_v5.json live (READ-ONLY)")
    ap.add_argument("--out-dir", default="data/v5/corpus")
    ap.add_argument("--songs", nargs="*", default=None)
    ap.add_argument("--summary-name", default="tempo_v5b_summary.tsv")
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
        (d / "tempo_v5b.json").write_text(json.dumps(res, sort_keys=True, indent=2) + "\n")
        rows.append(res)
        print(f"{sha16} {str(s.get('title'))[:28]:28s} v5={bpm_v5} v5b={res['bpm_v5b']} flipped={res['flipped_vs_v5']} "
              f"anchor={res['anchor_bpm']} d={res['delta_vs_anchor_bpm']} top3={res['s_scores_top3']}")

    hdr = ["sha16", "title", "bpm_v5", "bpm_v5b", "anchor_bpm", "flipped", "s_scores_top3"]
    lines = ["\t".join(hdr)]
    for r in rows:
        lines.append("\t".join(str(v) for v in [r["sha16"], r.get("title"), r["bpm_v5"], r["bpm_v5b"], r["anchor_bpm"],
                                                r["flipped_vs_v5"], json.dumps(r["s_scores_top3"], separators=(",", ":"))]))
    (out_dir / args.summary_name).write_text("\n".join(lines) + "\n")
    print(f"wrote {out_dir / args.summary_name} ({len(rows)} rows)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
