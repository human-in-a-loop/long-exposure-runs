#!/usr/bin/python3
"""c82 P2 — tempo MECHANISM PROBE (pre-registered measurement; NOT a criterion).

created: 2026-09-06T17:55:00Z
cycle: 82
run_id: run-2026-09-06T000000Z
agent: worker
milestone: M-V5-CORPUS-1/tempo-mechanism-preregistered-c82 / tempo-mechanism-verdict-c82

Pre-registered in data/v5/corpus/tempo_mechanism_probe_c82_preregistration.json BEFORE any output
(mtime gate enforced here + in tests). The meta-gate fired after three falsified criteria
(v5 / v5b / v5c): this script MEASURES the integer-lag quantization mechanism the c81 auditor
diagnosed and does not pick a tempo. No song's bpm_v5 changes; recanonicalization_blocked.json is
untouched; there is no tempo_v5d.

Per song:
  1. onset envelope + normalized autocorrelation exactly as tempo_v5 / tempo_v5b (READ-ONLY imports);
     the autocorrelation is DUMPED for lags 1..N (N = 2*lag_hi + 2, capped at len(ac)-1).
  2. every local maximum in the [40,240] BPM lag range is refined by parabolic interpolation over
     (lag-1, lag, lag+1): d = 0.5*(y[-1]-y[+1]) / (y[-1] - 2*y[0] + y[+1]), clamped to [-0.5, 0.5].
  3. per candidate: integer s (tempo_v5c harmonic_sum_direct, READ-ONLY) and refined s_ref =
     ac(T_ref) + 0.5*ac(T_ref/2) + 0.5*ac(2*T_ref), all read by linear interpolation (tempo_v5c.interp_ac).
  4. dominant refined candidate = argmax s_ref over refined BPM in the [70,180] pick band
     (SHA-256 tiebreak via tempo_v5.tiebreak); nearest-to-anchor and nearest-to-v5c-winner reported.
  5. librosa.beat.beat_track(start_bpm=120) on the full mix and, where an htdemucs drums stem exists on
     disk (30 s operator-section stem for the 5 focus songs; full-length stems are transient), on the drums stem.
Confirmation statistic (pre-declared): MECHANISM_CONFIRMED iff (A) all five anchor songs' nearest refined
candidate is within +/-1 BPM of the anchor AND (B) Disco A's s_ref at its refined ~120.2 candidate exceeds
s_ref at its refined ~80.75 candidate; PARTIAL if exactly one holds; REFUTED if neither.
Secondary: number of the 21 non-anchor songs whose dominant BPM moves by > 2 between integer v5c and refined.

Discipline: /usr/bin/python3 guard; no PRNG; no sidecar_nonfactor; no VST3 state APIs; tempo_v5*.py and their
frozen verdicts NOT modified.
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

_WS = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_WS))

import numpy as np  # noqa: E402
import librosa  # noqa: E402
from scripts.v5.tempo_v5 import (SR, HOP, BAND, ENV_PIN_SHA256, ANCHORS,  # noqa: E402  READ-ONLY
                                 lag_to_bpm, tiebreak)
from scripts.v5.tempo_v5b import CAND_BAND, HALF_WEIGHT, local_maxima, candidate_lag_range  # noqa: E402  READ-ONLY
from scripts.v5.tempo_v5c import interp_ac, harmonic_sum_direct  # noqa: E402  READ-ONLY

PREREG = "data/v5/corpus/tempo_mechanism_probe_c82_preregistration.json"
ANCHOR_TSV = "data/v5/corpus/tempo_v5b_summary_c81.tsv"  # c81 anchor_source column (WIG = librosa full-mix 99.384; tempo_v5.ANCHORS pins the c20 50.17 drums-stem section value)


def anchor_bpm_table() -> dict[str, float]:
    """Anchor BPM per focus song: tempo_v5.ANCHORS[...]['anchor_bpm'] (READ-ONLY) with the c81 TSV anchor_bpm column
    taking precedence where present (it carries the WIG full-mix anchor per tempo_v5b_summary_c81.tsv, pre-registered)."""
    table = {k: float(v["anchor_bpm"]) for k, v in ANCHORS.items()}
    p = _WS / ANCHOR_TSV
    if p.exists():
        lines = p.read_text().splitlines()
        hdr = lines[0].split("\t")
        for line in lines[1:]:
            row = dict(zip(hdr, line.split("\t")))
            if row.get("sha16") in table and row.get("anchor_bpm"):
                table[row["sha16"]] = float(row["anchor_bpm"])
    return table


ANCHOR_BPM = anchor_bpm_table()
ENUM = ("MECHANISM_CONFIRMED", "MECHANISM_PARTIAL", "MECHANISM_REFUTED")
ANCHOR_TOL_BPM = 1.0
SECONDARY_FLIP_BPM = 2.0
DISCO = "cdd2717e52820ff6"
FOCUS_STEM_DIRS = ("operator_section/rc9_6stem", "operator_section_c25_checkpointed/rc9_6stem")


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def parabolic_refine(ac: np.ndarray, lag: int) -> tuple[float, float]:
    """Return (refined_lag, offset d) from the parabola through (lag-1, lag, lag+1); d clamped to [-0.5, 0.5]."""
    if lag < 1 or lag + 1 >= len(ac):
        return float(lag), 0.0
    ym, y0, yp = float(ac[lag - 1]), float(ac[lag]), float(ac[lag + 1])
    den = ym - 2.0 * y0 + yp
    if den == 0.0:
        return float(lag), 0.0
    d = 0.5 * (ym - yp) / den
    d = max(-0.5, min(0.5, d))
    return lag + d, d


def s_refined(ac: np.ndarray, lag_ref: float) -> dict:
    ac_T, _ = interp_ac(ac, lag_ref)
    ac_h, h_in = interp_ac(ac, lag_ref / 2.0)
    ac_d, d_in = interp_ac(ac, 2.0 * lag_ref)
    return {"ac_T": round(ac_T, 6), "ac_half": round(ac_h, 6), "half_in": bool(h_in), "ac_double": round(ac_d, 6),
            "double_in": bool(d_in), "s_ref": round(ac_T + HALF_WEIGHT * ac_h + HALF_WEIGHT * ac_d, 6)}


def beat_track_bpm(y: np.ndarray) -> float:
    env = librosa.onset.onset_strength(y=y, sr=SR, hop_length=HOP)
    t, _ = librosa.beat.beat_track(onset_envelope=env, sr=SR, hop_length=HOP, start_bpm=120.0)
    return float(np.asarray(t).flatten()[0])


def octave_rel(a: float, b: float) -> str:
    r = a / b if b else 0.0
    for name, v in (("same", 1.0), ("double", 2.0), ("half", 0.5), ("three_halves", 1.5), ("two_thirds", 2 / 3)):
        if abs(r - v) / v <= 0.04:
            return name
    return "other"


def probe_song(song: dict, corpus_out: Path, v5c_dir: Path) -> dict:
    sha16 = song["sha16"]
    audio = Path(song["audio_path"])
    y, sr = librosa.load(str(audio), sr=SR, mono=True)
    env = librosa.onset.onset_strength(y=y, sr=sr, hop_length=HOP)
    ac = librosa.autocorrelate(env)
    ac = ac / ac[0] if ac[0] > 0 else ac
    lag_lo, lag_hi = candidate_lag_range(len(ac))
    n_dump = min(2 * lag_hi + 2, len(ac) - 1)
    cand_lags = [L for L in local_maxima(ac) if lag_lo <= L <= lag_hi]
    v5c_p = v5c_dir / sha16 / "tempo_v5c.json"
    v5c = json.loads(v5c_p.read_text()) if v5c_p.exists() else {}
    bpm_v5c = v5c.get("bpm_v5c")
    anchor = ANCHOR_BPM.get(sha16)
    cands = []
    for L in cand_lags:
        lag_ref, d = parabolic_refine(ac, L)
        bpm_ref = lag_to_bpm(lag_ref)
        integer = harmonic_sum_direct(ac, L)
        ref = s_refined(ac, lag_ref)
        cands.append({"lag_int": int(L), "bpm_int": round(lag_to_bpm(L), 6), "s_int": integer["s"],
                      "lag_ref": round(lag_ref, 4), "parabolic_offset": round(d, 4), "bpm_ref": round(bpm_ref, 6),
                      "ac_int": round(float(ac[L]), 6), **ref,
                      "in_pick_band": bool(BAND[0] <= bpm_ref <= BAND[1]),
                      "tiebreak": tiebreak(sha16, round(bpm_ref, 6))})
    band = [c for c in cands if c["in_pick_band"]]
    dom_ref = min(band, key=lambda c: (-c["s_ref"], c["tiebreak"])) if band else None
    dom_int = min([c for c in cands if BAND[0] <= c["bpm_int"] <= BAND[1]], key=lambda c: (-c["s_int"], c["tiebreak"])) if cands else None
    nearest_anchor = min(cands, key=lambda c: abs(c["bpm_ref"] - anchor)) if (anchor and cands) else None
    nearest_v5c = min(cands, key=lambda c: abs(c["bpm_ref"] - bpm_v5c)) if (bpm_v5c and cands) else None
    # beat trackers
    bt_full = beat_track_bpm(y)
    drums = None
    for sub in FOCUS_STEM_DIRS:
        p = _WS / "data/v3_spine" / sha16 / sub / "drums.wav"
        if p.exists():
            yd, _ = librosa.load(str(p), sr=SR, mono=True)
            b = beat_track_bpm(yd)
            drums = {"path": str(p.relative_to(_WS)), "sha256": sha(p), "duration_s": round(len(yd) / SR, 3), "bpm": round(b, 6),
                     "relation_to_full_mix": octave_rel(b, bt_full),
                     "relation_to_anchor": octave_rel(b, anchor) if anchor else None,
                     "abs_delta_vs_full_mix_bpm": round(abs(b - bt_full), 6)}
            break
    rec = {"schema_version": 1, "cycle": 82, "sha16": sha16, "title": song.get("title"), "audio_path": str(audio),
           "audio_sha256": song.get("audio_sha256"), "env_pin_sha256": ENV_PIN_SHA256, "kind": "mechanism_probe_measurement_not_criterion",
           "params": {"sr": SR, "hop": HOP, "candidate_band_bpm": list(CAND_BAND), "candidate_lag_range": [lag_lo, lag_hi],
                      "pick_band_bpm": list(BAND), "half_weight": HALF_WEIGHT, "parabolic_offset_clamp": [-0.5, 0.5],
                      "n_ac": int(len(ac)), "duration_s": round(len(y) / SR, 3), "librosa_version": librosa.__version__},
           "anchor_bpm": anchor, "bpm_v5": v5c.get("bpm_v5"), "bpm_v5c_integer_winner": bpm_v5c,
           "autocorr_dump": {"lags": f"1..{n_dump}", "ac": [round(float(v), 6) for v in ac[1:n_dump + 1]]},
           "n_candidates": len(cands), "candidates": cands,
           "dominant_integer": dom_int, "dominant_refined": dom_ref,
           "nearest_refined_to_anchor": nearest_anchor, "nearest_refined_to_v5c_winner": nearest_v5c,
           "refined_dominant_bpm_delta_vs_integer": (round(dom_ref["bpm_ref"] - dom_int["bpm_int"], 6) if (dom_ref and dom_int) else None),
           "beat_track": {"full_mix_bpm": round(bt_full, 6), "full_mix_relation_to_anchor": octave_rel(bt_full, anchor) if anchor else None,
                          "drums_stem": drums, "drums_stem_note": None if drums else "no drums stem on disk (full-length stems are transient; only the 5 focus songs have a 30 s section stem)"}}
    if anchor:
        rec["anchor_check"] = {"nearest_refined_bpm": nearest_anchor["bpm_ref"], "abs_delta_bpm": round(abs(nearest_anchor["bpm_ref"] - anchor), 6),
                               "within_tol": bool(abs(nearest_anchor["bpm_ref"] - anchor) <= ANCHOR_TOL_BPM), "tol_bpm": ANCHOR_TOL_BPM}
    out = corpus_out / sha16
    out.mkdir(parents=True, exist_ok=True)
    (out / "tempo_mechanism_c82.json").write_text(json.dumps(rec, sort_keys=True, indent=2) + "\n")
    return rec


def verdict(recs: list[dict], corpus_out: Path) -> dict:
    anchor_ok = {r["sha16"]: r["anchor_check"] for r in recs if r.get("anchor_check")}
    cond_a = len(anchor_ok) == 5 and all(v["within_tol"] for v in anchor_ok.values())
    d = next((r for r in recs if r["sha16"] == DISCO), None)
    cond_b, disco = False, None
    if d and d["candidates"]:
        c120 = min(d["candidates"], key=lambda c: abs(c["bpm_ref"] - 120.185))
        c80 = min(d["candidates"], key=lambda c: abs(c["bpm_ref"] - 80.75))
        cond_b = c120["s_ref"] > c80["s_ref"]
        disco = {"refined_near_120": c120, "refined_near_80_75": c80, "s_ref_120_gt_s_ref_80": cond_b,
                 "integer_s_120": c120["s_int"], "integer_s_80": c80["s_int"], "margin_ref": round(c120["s_ref"] - c80["s_ref"], 6)}
    if cond_a and cond_b:
        v = "MECHANISM_CONFIRMED"
    elif cond_a or cond_b:
        v = "MECHANISM_PARTIAL"
    else:
        v = "MECHANISM_REFUTED"
    flips = [{"sha16": r["sha16"], "title": r["title"], "bpm_int": r["dominant_integer"]["bpm_int"], "bpm_ref": r["dominant_refined"]["bpm_ref"],
              "delta": r["refined_dominant_bpm_delta_vs_integer"]}
             for r in recs if r["sha16"] not in ANCHORS and r["dominant_integer"] and r["dominant_refined"]
             and abs(r["refined_dominant_bpm_delta_vs_integer"]) > SECONDARY_FLIP_BPM]
    prereg_mtime = os.path.getmtime(_WS / PREREG)
    outs = sorted(corpus_out.glob("*/tempo_mechanism_c82.json"))
    min_out = min(os.path.getmtime(p) for p in outs)
    drums = {r["sha16"]: r["beat_track"]["drums_stem"] for r in recs if r["beat_track"]["drums_stem"]}
    rec = {"schema_version": 1, "cycle": 82, "agent": "worker", "kind": "mechanism_probe_measurement_not_criterion", "env_pin_sha256": ENV_PIN_SHA256,
           "enum": list(ENUM), "verdict": v, "condition_A_all_five_anchors_within_1bpm": cond_a, "condition_B_disco_a_refined_120_beats_80_75": cond_b,
           "anchor_checks": anchor_ok, "disco_a": disco,
           "secondary_non_anchor_refinement_flips_gt_2bpm": {"n": len(flips), "of": sum(1 for r in recs if r["sha16"] not in ANCHORS), "songs": flips},
           "drums_vs_full_mix_beat_track": {k: {"drums_bpm": v_["bpm"], "full_mix_bpm": next(r["beat_track"]["full_mix_bpm"] for r in recs if r["sha16"] == k),
                                                "relation": v_["relation_to_full_mix"], "relation_to_anchor": v_["relation_to_anchor"]} for k, v_ in drums.items()},
           "preregistration_gate": {"prereg_path": PREREG, "prereg_mtime": prereg_mtime, "min_output_mtime": min_out, "prereg_precedes_outputs": prereg_mtime < min_out},
           "anchor_bpm_table": ANCHOR_BPM, "anchor_tol_bpm": ANCHOR_TOL_BPM,
           "n_songs": len(recs), "no_criterion_note": "measurement only; no bpm_v5 changed; blocked file untouched; no tempo_v5d; a criterion is c83+ with its own pre-registration"}
    (corpus_out / "tempo_mechanism_c82_verdict.json").write_text(json.dumps(rec, sort_keys=True, indent=2) + "\n")
    return rec


def main() -> int:
    ap = argparse.ArgumentParser(description="c82 tempo mechanism probe (measurement, not criterion)")
    ap.add_argument("--manifest", default="data/v5/corpus/corpus_manifest.json")
    ap.add_argument("--corpus-out", default="data/v5/corpus", help="root for per-song outputs (use a temp dir for byte-det runs)")
    ap.add_argument("--v5c-dir", default="data/v5/corpus", help="where <sha16>/tempo_v5c.json (READ-ONLY integer winners) live")
    args = ap.parse_args()
    os.chdir(_WS)
    if not Path(PREREG).exists():
        raise SystemExit("PREREG_MISSING: write the pre-registration before any output (FD-1)")
    man = json.loads(Path(args.manifest).read_text())
    songs = sorted([s for s in man["songs"] if s.get("in_v5_corpus")], key=lambda s: s["v5_priority_rank"])
    corpus_out = Path(args.corpus_out)
    recs = []
    rows = []
    for s in songs:
        r = probe_song(s, corpus_out, Path(args.v5c_dir))
        recs.append(r)
        di, dr = r["dominant_integer"], r["dominant_refined"]
        na = r.get("anchor_check") or {}
        rows.append([r["sha16"], str(r["title"]), r["anchor_bpm"], r["bpm_v5c_integer_winner"], di and di["bpm_int"], di and di["s_int"],
                     dr and dr["bpm_ref"], dr and dr["s_ref"], dr and dr["lag_ref"], r["refined_dominant_bpm_delta_vs_integer"],
                     na.get("nearest_refined_bpm"), na.get("abs_delta_bpm"), na.get("within_tol"),
                     r["beat_track"]["full_mix_bpm"], (r["beat_track"]["drums_stem"] or {}).get("bpm"),
                     (r["beat_track"]["drums_stem"] or {}).get("relation_to_full_mix")])
        print(f"{r['sha16']} {str(r['title'])[:26]:26s} anchor={r['anchor_bpm']} v5c={r['bpm_v5c_integer_winner']} "
              f"int_dom={di and di['bpm_int']:.3f} ref_dom={dr and dr['bpm_ref']:.3f} "
              f"near_anchor={na.get('nearest_refined_bpm')} ok={na.get('within_tol')} bt_full={r['beat_track']['full_mix_bpm']:.2f} "
              f"bt_drums={(r['beat_track']['drums_stem'] or {}).get('bpm')}")
    hdr = ["sha16", "title", "anchor_bpm", "bpm_v5c_integer_winner", "dominant_integer_bpm", "dominant_integer_s", "dominant_refined_bpm",
           "dominant_refined_s", "dominant_refined_lag", "refined_minus_integer_bpm", "nearest_refined_to_anchor_bpm", "anchor_abs_delta_bpm",
           "anchor_within_1bpm", "beat_track_full_mix_bpm", "beat_track_drums_stem_bpm", "drums_vs_full_relation"]
    tsv = ["\t".join(hdr)] + ["\t".join("" if v is None else str(v) for v in row) for row in rows]
    (corpus_out / "tempo_mechanism_summary_c82.tsv").write_text("\n".join(tsv) + "\n")
    v = verdict(recs, corpus_out)
    print(f"VERDICT {v['verdict']} A={v['condition_A_all_five_anchors_within_1bpm']} B={v['condition_B_disco_a_refined_120_beats_80_75']} "
          f"secondary flips {v['secondary_non_anchor_refinement_flips_gt_2bpm']['n']}/{v['secondary_non_anchor_refinement_flips_gt_2bpm']['of']} "
          f"prereg_gate={v['preregistration_gate']['prereg_precedes_outputs']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
