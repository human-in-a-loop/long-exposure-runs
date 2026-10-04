#!/usr/bin/python3
"""v6 rules — key_v6: global key (Krumhansl-Schmuckler / Krumhansl-Kessler profiles) + an 8-bar windowed key track per song.

created: 2026-10-04
milestone: M-V6-RULES-1/audio-harmony

Pure functions over the beat-synchronous chroma that scripts/v6/rules/chords_v6.py computes (no audio here):
  global_key(beat_chroma, mask)   KK major/minor profiles correlated with the mean beat chroma over 12 rotations; argmax
                                  with harmony_v5.estimate_key's tie rule (major < minor, lowest tonic). Confidence =
                                  best corr minus the best corr among keys with a DIFFERENT tonic (either mode);
                                  mode_margin = best corr minus the other mode on the same tonic.
  key_track(beat_chroma, ...)     8-bar windows (32 beats) hopped by 4 bars from the first downbeat; per-window KK key;
                                  modulation flag when a window with confidence >= TRACK_CONF_MIN disagrees with the
                                  global tonic; the fraction of windows agreeing with the global key is reported.
  annotate(record)                adds the "key" block to a chords_v6 per-song record (called by chords_v6 when writing).
  main                            re-reads data/v6/rules/chords/<sha16>/chords_v6.json, rebuilds the key table and the
                                  focus-song sanity (I/IV/V presence among the detected chords), writes
                                  data/v6/rules/key_v6_summary.json. No PRNG; sorted-key atomic JSON with schema_version.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

_WS = Path(__file__).resolve().parent.parent.parent.parent
if str(_WS) not in sys.path:
    sys.path.insert(0, str(_WS))
from scripts.v6.v6_data_common import ENV_PIN_SHA256, FOCUS, WS, interpreter_guard, pin_env, read_json, write_json_atomic  # noqa: E402

pin_env()
interpreter_guard()
import numpy as np  # noqa: E402
from scripts.v5.harmony_v5 import KK_MAJOR, KK_MINOR, PC_NAMES, estimate_key  # noqa: E402  READ-ONLY

CHORDS_DIR = WS / "data/v6/rules/chords"
SUMMARY_OUT = WS / "data/v6/rules/key_v6_summary.json"
WINDOW_BARS, HOP_BARS = 8, 4
TRACK_CONF_MIN = 0.05          # a window must separate its tonic from the runner-up tonic by this corr gap to flag a modulation
LOW_KEY_CONFIDENCE = 0.02      # harmony_rules_v6 excludes a song only below this (pre-declared, see its docstring)
PRIMARY_DEGREES = {0: "I", 5: "IV", 7: "V"}


def _corr_table(profile: np.ndarray) -> dict:
    """{(tonic, mode): corr} for the KK profiles against a 12-D profile (zero when the profile is flat)."""
    out = {}
    flat = float(profile.std()) <= 0.0
    for mode, prof in (("major", KK_MAJOR), ("minor", KK_MINOR)):
        for tonic in range(12):
            r = 0.0 if flat else float(np.corrcoef(profile, np.roll(np.asarray(prof, dtype=float), tonic))[0, 1])
            out[(tonic, mode)] = round(r, 9)
    return out


def global_key(beat_chroma: np.ndarray, mask: np.ndarray | None = None) -> dict:
    """KK key of the mean beat chroma (mask = beats to include; None = all). Same argmax/tie rule as harmony_v5.estimate_key."""
    C = np.asarray(beat_chroma, dtype=float)
    if mask is not None:
        C = C[np.asarray(mask, dtype=bool)]
    profile = C.mean(axis=0) if len(C) else np.zeros(12)
    best = estimate_key(profile)
    table = _corr_table(profile)
    t, m = best["tonic"], best["mode"]
    other_tonic = max(v for (tt, _mm), v in table.items() if tt != t)
    other_mode = table[(t, "minor" if m == "major" else "major")]
    ranked = sorted(table.items(), key=lambda kv: (-kv[1], 0 if kv[0][1] == "major" else 1, kv[0][0]))
    return {"tonic": int(t), "tonic_name": PC_NAMES[t], "mode": m, "corr": best["corr"],
            "confidence": round(float(best["corr"] - other_tonic), 6), "mode_margin": round(float(best["corr"] - other_mode), 6),
            "runner_up": {"tonic": int(ranked[1][0][0]), "tonic_name": PC_NAMES[ranked[1][0][0]], "mode": ranked[1][0][1], "corr": ranked[1][1]},
            "n_beats_used": int(len(C)), "profile": [round(float(x), 6) for x in profile],
            "method": "krumhansl_kessler_argmax on the mean beat-synchronous CQT chroma (harmony_v5.estimate_key tie rule)"}


def key_track(beat_chroma: np.ndarray, first_downbeat: int, global_tonic: int, mask: np.ndarray | None = None,
              window_bars: int = WINDOW_BARS, hop_bars: int = HOP_BARS) -> dict:
    """Windowed KK key from the first downbeat; windows shorter than half a window are dropped."""
    C = np.asarray(beat_chroma, dtype=float)
    n = len(C)
    w, h = window_bars * 4, hop_bars * 4
    windows = []
    start = int(first_downbeat)
    while start < n and n - start >= w // 2:
        idx = np.arange(start, min(n, start + w))
        if mask is not None:
            idx = idx[np.asarray(mask, dtype=bool)[idx]]
        if len(idx) >= w // 4:
            k = global_key(C[idx])
            windows.append({"start_beat": start, "start_bar": (start - int(first_downbeat)) // 4, "n_beats": int(len(idx)), "tonic": k["tonic"],
                            "tonic_name": k["tonic_name"], "mode": k["mode"], "corr": k["corr"], "confidence": k["confidence"]})
        start += h
    agree = [wd["tonic"] == global_tonic for wd in windows]
    confident_disagree = [wd for wd in windows if wd["tonic"] != global_tonic and wd["confidence"] >= TRACK_CONF_MIN]
    runs = []  # contiguous confident-disagreeing windows -> candidate modulation spans
    for wd in confident_disagree:
        if runs and runs[-1]["tonic"] == wd["tonic"] and wd["start_bar"] - runs[-1]["end_bar"] <= hop_bars:
            runs[-1]["end_bar"] = wd["start_bar"] + window_bars
            runs[-1]["n_windows"] += 1
        else:
            runs.append({"tonic": wd["tonic"], "tonic_name": wd["tonic_name"], "mode": wd["mode"], "start_bar": wd["start_bar"],
                         "end_bar": wd["start_bar"] + window_bars, "n_windows": 1})
    return {"window_bars": window_bars, "hop_bars": hop_bars, "n_windows": len(windows), "windows": windows,
            "fraction_agreeing_with_global": round(float(np.mean(agree)), 6) if windows else None,
            "n_confident_disagreeing": len(confident_disagree), "modulation_flag": bool(runs), "modulation_spans": runs,
            "rule": f"modulation_flag iff any window with confidence >= {TRACK_CONF_MIN} has a tonic != global tonic"}


def annotate(rec: dict) -> dict:
    """Add rec['key'] from rec['beat_chroma'] (beats with chord 'N' / silence excluded from the global profile when any remain)."""
    C = np.asarray(rec["beat_chroma"], dtype=float)
    stream = rec["chords"]["chord_stream"]
    sounding = np.ones(len(C), dtype=bool)
    for e in stream:
        if e["quality"] == "N":
            sounding[e["grid_beat"]] = False
    mask = sounding if sounding.sum() >= 8 else None
    g = global_key(C, mask)
    g["track"] = key_track(C, rec["grid"]["phase"], g["tonic"], mask)
    g["low_confidence"] = bool(g["confidence"] < LOW_KEY_CONFIDENCE)
    g["low_confidence_threshold"] = LOW_KEY_CONFIDENCE
    rec["key"] = g
    return rec


def primary_degree_report(rec: dict) -> dict:
    """Fraction of sounding beats on I / IV / V (relative to the detected tonic) + whether all three are present (>= 2 % each)."""
    tonic = rec["key"]["tonic"]
    counts = {d: 0 for d in PRIMARY_DEGREES}
    n = 0
    for e in rec["chords"]["chord_stream"]:
        if e["quality"] == "N":
            continue
        n += 1
        rel = (int(e["root"]) - tonic) % 12
        if rel in counts:
            counts[rel] += 1
    frac = {PRIMARY_DEGREES[d]: round(c / n, 6) if n else None for d, c in counts.items()}
    return {"fractions": frac, "n_sounding_beats": n, "all_present": bool(n and all(c / n >= 0.02 for c in counts.values())),
            "primary_mass": round(sum(counts.values()) / n, 6) if n else None}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="v6 key summary from the per-song chords_v6 files")
    ap.add_argument("--chords-dir", default=str(CHORDS_DIR))
    ap.add_argument("--out", default=str(SUMMARY_OUT))
    args = ap.parse_args(argv)
    cd = Path(args.chords_dir)
    rows, focus = {}, {}
    for p in sorted(cd.glob("*/chords_v6.json")):
        rec = read_json(p)
        k = rec["key"]
        rows[rec["sha16"]] = {"title": rec.get("title"), "band": rec.get("band"), "bpm": rec["bpm"], "tonic": k["tonic"], "tonic_name": k["tonic_name"], "mode": k["mode"],
                              "corr": k["corr"], "confidence": k["confidence"], "mode_margin": k["mode_margin"], "low_confidence": k["low_confidence"],
                              "runner_up": f"{k['runner_up']['tonic_name']} {k['runner_up']['mode']}", "modulation_flag": k["track"]["modulation_flag"],
                              "track_agreement": k["track"]["fraction_agreeing_with_global"], "n_fraction": rec["chords"]["n_fraction"],
                              "primary_degrees": primary_degree_report(rec)}
        if rec["sha16"] in FOCUS:
            focus[rec["sha16"]] = dict(rows[rec["sha16"]], short=FOCUS[rec["sha16"]]["short"])
        print(f"{rec['sha16']} {str(rec.get('title'))[:28]:28s} key={k['tonic_name']:2s} {k['mode']:5s} corr={k['corr']:.3f} conf={k['confidence']:.3f} "
              f"mod={k['track']['modulation_flag']} N={rec['chords']['n_fraction']:.3f} IVV={rows[rec['sha16']]['primary_degrees']['fractions']}")
    out = {"schema_version": 1, "generator": "scripts/v6/rules/key_v6.py", "milestone": "M-V6-RULES-1/audio-harmony", "env_pin_sha256": ENV_PIN_SHA256,
           "n_songs": len(rows), "per_song": rows, "focus_sanity": focus,
           "mode_counts": {m: sum(1 for r in rows.values() if r["mode"] == m) for m in ("major", "minor")},
           "n_modulation_flags": sum(1 for r in rows.values() if r["modulation_flag"]), "n_low_confidence": sum(1 for r in rows.values() if r["low_confidence"]),
           "params": {"window_bars": WINDOW_BARS, "hop_bars": HOP_BARS, "track_conf_min": TRACK_CONF_MIN, "low_key_confidence": LOW_KEY_CONFIDENCE}}
    write_json_atomic(Path(args.out), out)
    print(f"wrote {args.out} ({len(rows)} songs)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
