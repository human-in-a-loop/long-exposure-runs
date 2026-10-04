#!/usr/bin/python3
"""v6 rules — comping_v6: comping-rhythm statistics from the audio 'other' stem on the shared beat grid.

created: 2026-10-04
milestone: M-V6-RULES-1/audio-harmony

  /usr/bin/python3 scripts/v6/rules/comping_v6.py [--songs sha16,...] [--v5-out data/v5/rules/comping_v5.json]
                                                  [--v6-out data/v6/rules/comping_v6.json]

Per song: the htdemucs 'other' stem (keys / guitars / synths — there is no guitar|piano split, so the single stem class is
"other"; the pooled set == other) -> librosa.effects.harmonic (HPSS, margin HPSS_MARGIN, removes percussive leakage) ->
librosa.onset.onset_strength / onset_detect (hop 512) -> each onset to the nearest 16th slot of the SHARED beat grid read
from data/v6/rules/chords/<sha16>/chords_v6.json (beat_times, phase, hypermeter_offset of scripts/v6/microtiming_v6.py);
an onset is rejected when |deviation| > REJECT_F16 x 16th (microtiming_model.REJECT_F16). Bars are stream bars (bar 0 =
first downbeat), slot = 16th position in the bar.
Statistics (comping_v5.pool key set, plus the per-bar 16-bit onset MASK distribution and the onsets-per-bar histogram):
per stem class ("other"), pooled, and per rating band. IOI = slot difference between consecutive onsets (16ths, clipped
1..16). chord_size_mean / sustain_ratio are None (no polyphony or note-off information in audio; disclosed).
Verdict: the comping_v5 pre-registered rule, thresholds asserted equal to data/v5/rules/comping_prereg_c87.json:
  COMPING_NON_DEGENERATE iff >= 8 songs contribute >= 16 bars with onsets AND the pooled 16-slot histogram max mass < 0.5.
Outputs: data/v5/rules/comping_v5.json (the comping_v5 top-level key set, read by scripts/v6/gen/fixtures.load_models and
scripts/v6/gen/voicing.comping_onsets via stats.pooled.ioi16_histogram) and data/v6/rules/comping_v6.json (same + per-song
bar masks). No PRNG; sorted-key atomic JSON with schema_version; 7-key env pin.
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

_WS = Path(__file__).resolve().parent.parent.parent.parent
if str(_WS) not in sys.path:
    sys.path.insert(0, str(_WS))
from scripts.v6.v6_data_common import ENV_PIN_SHA256, WS, interpreter_guard, pin_env, read_json, sha256_file, write_json_atomic  # noqa: E402

pin_env()
interpreter_guard()
import numpy as np  # noqa: E402
from scripts.v5.comping_v5 import ENUM, IOI_MAX, SLOTS, THRESHOLDS, r6  # noqa: E402  READ-ONLY (verdict constants)
from scripts.v6.gen.microtiming_model import REJECT_F16  # noqa: E402  READ-ONLY (same rejection rule as microtiming)

SR, HOP = 22050, 512
HPSS_MARGIN = 2.0
STEM = "other"
STEMS_DIR = WS / "data/v6/stems"
CHORDS_DIR = WS / "data/v6/rules/chords"
PREREG = WS / "data/v5/rules/comping_prereg_c87.json"
V5_OUT = WS / "data/v5/rules/comping_v5.json"
V6_OUT = WS / "data/v6/rules/comping_v6.json"
TOP_MASKS = 24


def onset_times(y: np.ndarray) -> np.ndarray:
    import librosa
    harm = librosa.effects.harmonic(y, margin=HPSS_MARGIN)
    env = librosa.onset.onset_strength(y=harm, sr=SR, hop_length=HOP)
    frames = librosa.onset.onset_detect(onset_envelope=env, sr=SR, hop_length=HOP, units="frames", backtrack=False)
    return frames.astype(float) * HOP / SR


def assign_slots(times: np.ndarray, beats: np.ndarray, phase: int) -> list:
    """(bar, slot16, dev_f16) per accepted onset; bar 0 = first downbeat (grid beat `phase`); rejects |dev| > REJECT_F16."""
    out = []
    for t in times:
        i = int(np.searchsorted(beats, t, side="right")) - 1
        if i < 0 or i >= beats.size - 1:
            continue
        s16 = (beats[i + 1] - beats[i]) / 4.0
        sub_f = (t - beats[i]) / s16
        sub = int(round(sub_f))
        dev = sub_f - sub
        if sub == 4:
            i, sub = i + 1, 0
        if abs(dev) > REJECT_F16 or i < phase:
            continue
        out.append(((i - phase) // 4, ((i - phase) % 4) * 4 + sub, float(dev)))
    return out


def analyse_stem(placed: list, n_bars: int) -> dict:
    """comping_v5.analyse_stem key set (+ bar masks) from (bar, slot, dev) tuples; one onset per (bar, slot)."""
    cells = sorted({(b, s) for b, s, _d in placed if 0 <= b < n_bars})
    slot_counts = [0] * SLOTS
    ioi_counts = [0] * IOI_MAX
    masks = [0] * n_bars
    bars: dict = {}
    prev = None
    for b, s in cells:
        slot_counts[s] += 1
        masks[b] |= 1 << s
        bars[b] = bars.get(b, 0) + 1
        if prev is not None:
            ioi = min(IOI_MAX, max(1, (b * SLOTS + s) - prev))
            ioi_counts[ioi - 1] += 1
        prev = b * SLOTS + s
    return {"n_starts": len(cells), "n_onset_groups": len(cells), "n_unpaired_starts": len(cells), "n_detected": len(placed), "n_duplicate_cells": len(placed) - len(cells),
            "n_bars_with_onsets": len(bars), "bars": sorted(bars), "n_bars_total": n_bars,
            "slot_counts": slot_counts, "ioi_counts": ioi_counts, "chord_size_sum": 0, "duration_beats_sum": 0.0, "n_paired_durations": 0,
            "onsets_per_bar": r6(len(cells) / len(bars)) if bars else None, "notes_per_bar": r6(len(cells) / len(bars)) if bars else None,
            "chord_size_mean": None, "sustain_ratio": None, "bar_masks": masks,
            "onsets_per_bar_histogram": {str(k): sum(1 for v in bars.values() if v == k) for k in range(1, SLOTS + 1) if any(v == k for v in bars.values())}}


def analyse_song(sha16: str, y: np.ndarray, chords: dict) -> dict:
    g = chords["grid"]
    beats = np.asarray(g["beat_times"], dtype=float)
    n_bars = int(g["n_bars_from_first_downbeat"])
    placed = assign_slots(onset_times(y), beats, int(g["phase"]))
    st = analyse_stem(placed, n_bars)
    return {"sha16": sha16, "title": chords.get("title"), "band": chords.get("band"), "bpm_used": r6(g["bpm"]), "midi_dir": None,
            "grid_source": "data/v6/rules/chords/<sha16>/chords_v6.json grid (microtiming_v6 beats)", "hypermeter_offset": g["hypermeter_offset"],
            "per_stem": {STEM: st}, "n_bars_with_onsets_pooled": st["n_bars_with_onsets"]}


def _hist(counts: list) -> tuple[list, int]:
    n = sum(counts)
    return ([r6(c / n) for c in counts] if n else [0.0] * len(counts)), n


def pool(per_song: dict, stems: tuple) -> dict:
    """comping_v5.pool key set + bar_mask_counts (top masks) + onsets_per_bar_histogram."""
    slot, ioi = [0] * SLOTS, [0] * IOI_MAX
    n_starts = n_groups = n_bars = n_songs = 0
    bars_by_song, mask_counts, opb = [], {}, {}
    for sha16 in sorted(per_song):
        song_bars: set = set()
        contributed = False
        for stem in stems:
            st = per_song[sha16]["per_stem"][stem]
            if st["n_onset_groups"] == 0:
                continue
            contributed = True
            song_bars |= set(st["bars"])
            slot = [a + b for a, b in zip(slot, st["slot_counts"])]
            ioi = [a + b for a, b in zip(ioi, st["ioi_counts"])]
            n_starts += st["n_starts"]
            n_groups += st["n_onset_groups"]
            for m in st["bar_masks"]:
                if m:
                    mask_counts[m] = mask_counts.get(m, 0) + 1
            for k, v in st["onsets_per_bar_histogram"].items():
                opb[k] = opb.get(k, 0) + v
        if contributed:
            n_songs += 1
            n_bars += len(song_bars)
            bars_by_song.append(len(song_bars))
    slot_p, _ = _hist(slot)
    ioi_p, n_ioi = _hist(ioi)
    top = sorted(mask_counts.items(), key=lambda kv: (-kv[1], kv[0]))[:TOP_MASKS]
    return {"stems": list(stems), "n_songs": n_songs, "n_bars": n_bars, "n_starts": n_starts, "n_onset_groups": n_groups,
            "onset_density_notes_per_bar": r6(n_starts / n_bars) if n_bars else None, "onset_density_onsets_per_bar": r6(n_groups / n_bars) if n_bars else None,
            "slot16_counts": slot, "slot16_histogram": slot_p, "slot16_max_mass": max(slot_p) if n_groups else None,
            "slot16_argmax": int(max(range(SLOTS), key=lambda i: (slot[i], -i))) if n_groups else None,
            "ioi16_counts": ioi, "ioi16_histogram": ioi_p, "n_ioi": n_ioi, "chord_size_mean": None, "sustain_ratio": None, "n_paired_durations": 0,
            "bars_with_onsets_by_contributing_song": bars_by_song, "n_distinct_bar_masks": len(mask_counts),
            "bar_mask_counts_top": [{"mask": m, "bits": f"{m:016b}"[::-1], "count": c, "prob": r6(c / sum(mask_counts.values()))} for m, c in top],
            "onsets_per_bar_histogram": {k: opb[k] for k in sorted(opb, key=int)}}


def verdict_of(per_song: dict, pooled: dict) -> dict:
    songs_ge = sorted(s for s in per_song if per_song[s]["n_bars_with_onsets_pooled"] >= THRESHOLDS["min_bars_with_onsets_per_song"])
    max_mass = pooled["slot16_max_mass"]
    non_deg = len(songs_ge) >= THRESHOLDS["min_songs"] and max_mass is not None and max_mass < THRESHOLDS["pooled_max_slot_mass_lt"]
    return {"enum": ENUM[0] if non_deg else ENUM[1], "enum_values": list(ENUM), "thresholds": dict(THRESHOLDS),
            "n_songs_with_ge_16_pooled_bars": len(songs_ge), "songs_with_ge_16_pooled_bars": songs_ge, "songs_ok": len(songs_ge) >= THRESHOLDS["min_songs"],
            "pooled_max_slot_mass": max_mass, "pooled_argmax_slot": pooled["slot16_argmax"],
            "slot_mass_ok": bool(max_mass is not None and max_mass < THRESHOLDS["pooled_max_slot_mass_lt"]),
            "rule": "COMPING_NON_DEGENERATE iff n_songs_with_ge_16_pooled_bars >= 8 AND pooled_max_slot_mass < 0.5"}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="v6 comping-rhythm statistics from the 'other' stem")
    ap.add_argument("--songs", default=None)
    ap.add_argument("--chords-dir", default=str(CHORDS_DIR))
    ap.add_argument("--v5-out", default=str(V5_OUT))
    ap.add_argument("--v6-out", default=str(V6_OUT))
    args = ap.parse_args(argv)
    cd = Path(args.chords_dir) if Path(args.chords_dir).is_absolute() else WS / args.chords_dir
    prereg = read_json(PREREG)
    if prereg.get("thresholds") != THRESHOLDS or sorted(prereg.get("enum", [])) != sorted(ENUM):
        raise SystemExit(f"PREREG_MISMATCH: {PREREG} thresholds/enum differ from scripts/v5/comping_v5.py constants")
    man = read_json(STEMS_DIR / "manifest.json")
    shas = [s.strip() for s in args.songs.split(",")] if args.songs else sorted(s for s in man["songs"] if (cd / s / "chords_v6.json").exists())
    from scripts.v6.microtiming_v6 import load_mono  # READ-ONLY
    per_song = {}
    for sha in shas:
        t0 = time.time()
        r = analyse_song(sha, load_mono(STEMS_DIR / sha / f"{STEM}.wav"), read_json(cd / sha / "chords_v6.json"))
        r["wall_s"] = round(time.time() - t0, 1)
        per_song[sha] = r
        st = r["per_stem"][STEM]
        print(f"{sha} {str(r['title'])[:26]:26s} band={r['band']} onsets={st['n_onset_groups']} (detected {st['n_detected']}) bars={st['n_bars_with_onsets']}/{st['n_bars_total']} "
              f"onsets/bar={st['onsets_per_bar']} wall={r['wall_s']}s", flush=True)
    stats = {STEM: pool(per_song, (STEM,)), "pooled": pool(per_song, (STEM,))}
    stats["by_band"] = {str(b): pool({s: r for s, r in per_song.items() if str(r["band"]) == str(b)}, (STEM,)) for b in sorted({str(r["band"]) for r in per_song.values()})}
    verdict = verdict_of(per_song, stats["pooled"])
    strip = lambda r: {k: (v if k != "per_stem" else {st: {kk: vv for kk, vv in sv.items() if kk not in ("bars", "bar_masks")} for st, sv in v.items()}) for k, v in r.items()}  # noqa: E731
    base = {"schema_version": 1, "cycle": 600, "agent": "worker", "run_id": "v6-rules-2026-10-04", "env_pin_sha256": ENV_PIN_SHA256,
            "script_sha256": sha256_file(Path(__file__)), "prereg_path": str(PREREG.relative_to(WS)), "prereg_sha256": sha256_file(PREREG),
            "eligible": {"path": "data/v6/stems/manifest.json (songs with a chords_v6.json grid)", "sha256": sha256_file(STEMS_DIR / "manifest.json"), "n_used": len(shas), "used": list(shas),
                         "late_landed_deferred": []},
            "corpus_dir": "data/v6/stems", "stems": [STEM],
            "grid": {"ppq": None, "ticks_per_16th": None, "slots_per_bar": SLOTS, "phase_offset": "per song: microtiming_v6 downbeat phase (stream bar 0 = first downbeat)",
                     "seconds_to_ticks": None, "slot": "nearest 16th between consecutive shared-grid beats; |dev| > REJECT_F16 x 16th rejected (microtiming rule)",
                     "reject_f16": REJECT_F16, "chord_window_s": None, "ioi_clip": [1, IOI_MAX], "onset_group": "one onset per (bar, 16th slot) cell",
                     "sustain_ratio": None, "bars_with_onsets": "stream bars holding >= 1 accepted onset", "midi_dir_preference": None,
                     "onset_detector": f"librosa.effects.harmonic(margin={HPSS_MARGIN}) -> onset_strength -> onset_detect (hop {HOP})", "stem_source": "htdemucs 'other' (no guitar|piano split)"},
            "stats": stats, "verdict": verdict,
            "notes": ["v6: AUDIO onsets of the demucs 'other' stem on the shared microtiming beat grid; stem classes guitar/piano do not exist -> single class 'other' == pooled",
                      "chord_size_mean / sustain_ratio are None (no polyphony / note-off information in audio)",
                      "bar_mask_counts_top: per-bar 16-bit onset masks (bit j = 16th slot j), top 24 by count"]}
    v5p = Path(args.v5_out) if Path(args.v5_out).is_absolute() else WS / args.v5_out
    v6p = Path(args.v6_out) if Path(args.v6_out).is_absolute() else WS / args.v6_out
    write_json_atomic(v5p, dict(base, per_song={s: strip(r) for s, r in per_song.items()}))
    write_json_atomic(v6p, dict(base, per_song={s: {k: (v if k != "per_stem" else {st: {kk: vv for kk, vv in sv.items() if kk != "bars"} for st, sv in v.items()}) for k, v in r.items()}
                                                for s, r in per_song.items()}))
    p = stats["pooled"]
    print(f"VERDICT {verdict['enum']}: songs>=16 bars {verdict['n_songs_with_ge_16_pooled_bars']}/{len(shas)}; pooled max slot mass {p['slot16_max_mass']} at slot {p['slot16_argmax']}; "
          f"onsets/bar={p['onset_density_onsets_per_bar']} ioi16={p['ioi16_histogram'][:8]} top masks={[(m['bits'], m['count']) for m in p['bar_mask_counts_top'][:4]]}")
    print(f"wrote {v5p} and {v6p}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
