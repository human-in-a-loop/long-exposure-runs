#!/usr/bin/python3
"""v6 rules — melody_v6: melody VOMM (melody_vomm_v5 schema) + rhythm / register / phrase statistics from the vocals stem.

created: 2026-10-04
milestone: M-V6-RULES-1/audio-derived-groove-bass-melody

  /usr/bin/python3 scripts/v6/rules/melody_v6.py [--songs sha16,...] [--workers 2] [--out-v5 data/v5/rules/melody_vomm_v5.json]
      [--out-v6 data/v6/rules/melody_v6.json]

Source: the vocals stem; when it is near-silent (frame RMS < -45 dBFS) for > 70 % of the song the 'other' stem's predominant
pitch is used instead (recorded per song). Pitch: librosa.pyin fmin 80 / fmax 1000 Hz, frame 2048, hop 256. Notes: voiced
runs (voiced probability > 0.5), split where consecutive frames jump > 1.5 semitones, runs < 80 ms dropped, pitch = median f0
of the run rounded to MIDI. Onsets -> v5 ticks on the shared microtiming grid (stems_common_v6.grid_tick: beat index * 480 +
16th * 120; onsets outside the fitted beats are dropped). Key: the sibling's (via bass_pitch_v6.chord_stream_for) else the
Krumhansl fallback of the _bassroots cache. Tokens / training / sampling are scripts/v5/melody_vomm_v5's own pure helpers
(tokenize, train_counts, order_stats, run_sampling_check, phrase_structure; READ-ONLY) with max_order 2.
Extras (v6 keys): rhythm (16th-slot onset histogram, IOI histogram in 16ths + v5 buckets, duration histogram), register
(median, IQR), phrases (rest >= 1 beat = boundary: length distribution in bars, interval histogram, leap fraction, contour
peak position). No PRNG.
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

_WS = Path(__file__).resolve().parent.parent.parent.parent
if str(_WS) not in sys.path:
    sys.path.insert(0, str(_WS))
from scripts.v6.rules import stems_common_v6 as SC  # noqa: E402  (pins + guard at import)
from scripts.v6.rules.bass_pitch_v6 import PITCH_DIR, chord_stream_for, pyin_track  # noqa: E402
from scripts.v6.v6_data_common import ENV_PIN_SHA256, WS, read_json, sha256_file, write_json_atomic  # noqa: E402
import numpy as np  # noqa: E402
from scripts.v5 import melody_vomm_v5 as V5  # noqa: E402  READ-ONLY pure exports

PYIN = {"fmin": 80.0, "fmax": 1000.0, "frame_length": 2048, "hop_length": 256}
VOICED_MIN, MIN_NOTE_S, JUMP_SEMITONES = 0.5, 0.080, 1.5
SILENCE_DB, SILENT_FRAC_MAX = -45.0, 0.70
PHRASE_REST_BEATS = 1.0
MAX_ORDER = 2
LEVEL_WIN_S = 0.030
OUT_V5 = WS / "data/v5/rules/melody_vomm_v5.json"
OUT_V6 = WS / "data/v6/rules/melody_v6.json"


# ------------------------------------------------------------------------------------------------- segmentation ----
def segment_notes(f0: np.ndarray, prob: np.ndarray, t: np.ndarray, min_dur_s: float = MIN_NOTE_S, jump: float = JUMP_SEMITONES, prob_min: float = VOICED_MIN) -> list[dict]:
    """[{onset_s, offset_s, midi, n_frames}] from voiced runs split at > `jump` semitone frame-to-frame changes; runs < min_dur_s dropped."""
    voiced = (prob > prob_min) & np.isfinite(f0) & (f0 > 0)
    midi = np.where(voiced, 69.0 + 12.0 * np.log2(np.where(voiced, f0, 440.0) / 440.0), np.nan)
    hop = float(t[1] - t[0]) if t.size > 1 else 0.0
    notes, run = [], []
    def flush():
        if run and (t[run[-1]] + hop - t[run[0]]) >= min_dur_s:
            m = midi[run]
            notes.append({"onset_s": round(float(t[run[0]]), 6), "offset_s": round(float(t[run[-1]] + hop), 6), "midi": int(round(float(np.median(m)))), "n_frames": len(run)})
    for i in range(f0.size):
        if not voiced[i]:
            flush(); run = []
            continue
        if run and abs(midi[i] - midi[run[-1]]) > jump:
            flush(); run = []
        run.append(i)
    flush()
    return notes


def silent_fraction(y: np.ndarray, frame_length: int = 2048, hop_length: int = 256, floor_db: float = SILENCE_DB) -> float:
    import librosa
    rms = librosa.feature.rms(y=y, frame_length=frame_length, hop_length=hop_length)[0]
    return float(np.mean(20.0 * np.log10(rms + 1e-9) < floor_db)) if rms.size else 1.0


def melody_notes(sha16: str) -> dict:
    """Cached note list for a song (source stem chosen by the vocals silence rule), with 30 ms post-onset levels (velocity_v6)."""
    p = PITCH_DIR / f"{sha16}_melody.json"
    if p.exists():
        return read_json(p)
    voc = SC.stem(sha16, "vocals")
    sil = silent_fraction(voc)
    source = "vocals" if sil <= SILENT_FRAC_MAX else "other"
    y = voc if source == "vocals" else SC.stem(sha16, "other")
    f0, prob, t = pyin_track(y, **PYIN)
    notes = segment_notes(f0, prob, t)
    lev = SC.MT.levels_db(y, np.asarray([n["onset_s"] for n in notes])) if notes else np.zeros(0)
    for n, l in zip(notes, lev):
        n["level_db"] = round(float(l), 3)
    out = {"schema_version": 1, "sha16": sha16, "source_stem": source, "vocals_silent_fraction": round(sil, 6), "silent_rule": f"frame RMS < {SILENCE_DB} dBFS on > {SILENT_FRAC_MAX:.0%} of frames -> 'other'",
           "pyin": dict(PYIN, voiced_prob_min=VOICED_MIN, min_note_s=MIN_NOTE_S, jump_semitones=JUMP_SEMITONES), "voiced_frame_fraction": round(float(np.mean(prob > VOICED_MIN)), 6) if prob.size else 0.0,
           "n_notes": len(notes), "notes": notes, "env_pin_sha256": ENV_PIN_SHA256}
    write_json_atomic(p, out)
    return out


# ------------------------------------------------------------------------------------------------- statistics ----
def _hist(vals, keys) -> dict:
    return {str(k): int(sum(1 for v in vals if v == k)) for k in keys}


def _pct(xs: list, q: float):
    s = sorted(xs)
    if not s:
        return None
    pos = (len(s) - 1) * q
    lo, hi = int(pos), min(int(pos) + 1, len(s) - 1)
    return round(s[lo] + (s[hi] - s[lo]) * (pos - lo), 6)


def register_of(midis: list) -> dict:
    return {"n": len(midis), "median": _pct(midis, 0.5), "iqr_lo": _pct(midis, 0.25), "iqr_hi": _pct(midis, 0.75), "min": min(midis) if midis else None, "max": max(midis) if midis else None}


def phrases_of(notes: list, beat_s: float, rest_beats: float = PHRASE_REST_BEATS) -> list[list[dict]]:
    out, cur = [], []
    for n in notes:
        if cur and n["onset_s"] - cur[-1]["offset_s"] >= rest_beats * beat_s:
            out.append(cur); cur = []
        cur.append(n)
    if cur:
        out.append(cur)
    return out


def phrase_stats(phrases: list[list[dict]], beat_s: float) -> dict:
    lengths = [round((ph[-1]["offset_s"] - ph[0]["onset_s"]) / (4 * beat_s) * 2) / 2 for ph in phrases]
    ivs = [b["midi"] - a["midi"] for ph in phrases for a, b in zip(ph, ph[1:])]
    clipped = [max(-12, min(12, iv)) for iv in ivs]
    peaks = []
    for ph in phrases:
        if len(ph) >= 3:
            i = max(range(len(ph)), key=lambda k: (ph[k]["midi"], -k))
            peaks.append(i / (len(ph) - 1))
    return {"n_phrases": len(phrases), "notes_per_phrase_mean": round(sum(len(p) for p in phrases) / len(phrases), 4) if phrases else None,
            "length_bars_histogram": {str(k): lengths.count(k) for k in sorted(set(lengths))}, "length_bars_quantiles": {"p25": _pct(lengths, 0.25), "median": _pct(lengths, 0.5), "p75": _pct(lengths, 0.75)},
            "interval_histogram": _hist(clipped, range(-12, 13)), "n_intervals": len(ivs),
            "step_fraction": round(sum(1 for iv in ivs if 1 <= abs(iv) <= 2) / len(ivs), 6) if ivs else None, "repeat_fraction": round(sum(1 for iv in ivs if iv == 0) / len(ivs), 6) if ivs else None,
            "leap_fraction": round(sum(1 for iv in ivs if abs(iv) > 2) / len(ivs), 6) if ivs else None,
            "peak_position": {"n": len(peaks), "mean": round(sum(peaks) / len(peaks), 6) if peaks else None,
                              "quartile_histogram": {q: sum(1 for p in peaks if (q == "q4" and p > 0.75) or (q != "q4" and lo <= p <= hi)) for q, lo, hi in (("q1", 0.0, 0.25), ("q2", 0.25001, 0.5), ("q3", 0.50001, 0.75), ("q4", 0.75001, 1.0))}}}


def analyze(sha16: str) -> dict:
    t0 = time.time()
    onsets = SC.load_onsets(sha16)
    grid = onsets["grid"]
    mel = melody_notes(sha16)
    _stream, key, key_src = chord_stream_for(sha16, onsets)
    key = key or {"tonic": 0, "mode": "major"}
    beats, beat_s = grid["beat_times"], 60.0 / grid["bpm"]
    ticks, slots, kept = [], [], []
    for n in mel["notes"]:
        g = SC.time_to_grid(n["onset_s"], beats)
        if g is None:
            continue
        ticks.append((g[0] * SC.PPQ + g[1] * SC.TICKS_16TH, n["midi"]))
        slots.append(SC.bar_slot(g[0], g[1], grid)[1])
        kept.append(n)
    ticks_sorted = sorted(ticks)
    toks = V5.tokenize(ticks_sorted, int(key["tonic"]), str(key["mode"]))
    ioi16 = [max(1, int(round((b[0] - a[0]) / SC.TICKS_16TH))) for a, b in zip(ticks_sorted, ticks_sorted[1:])]
    dur16 = [max(1, int(round((n["offset_s"] - n["onset_s"]) / (beat_s / 4)))) for n in kept]
    phr = phrases_of(kept, beat_s)
    return {"title": onsets.get("title"), "band": onsets.get("band"), "bpm": grid["bpm"], "source_stem": mel["source_stem"], "vocals_silent_fraction": mel["vocals_silent_fraction"],
            "voiced_frame_fraction": mel["voiced_frame_fraction"], "n_notes": mel["n_notes"], "n_notes_on_grid": len(kept), "tokens": toks, "ticks": ticks_sorted,
            "key": {"tonic": int(key["tonic"]), "mode": str(key["mode"]), "source": key_src["source"]}, "n_chromatic": sum(1 for t in toks if t.startswith("c|")),
            "rhythm": {"slot16_histogram": _hist(slots, range(16)), "ioi16_histogram": _hist([min(32, x) for x in ioi16], range(1, 33)), "ioi_bucket_histogram": _hist([V5.ioi_bucket(x * SC.TICKS_16TH) for x in ioi16], V5.IOI_BUCKETS),
                       "dur16_histogram": _hist([min(32, d) for d in dur16], range(1, 33)), "n_onsets": len(kept)},
            "register": register_of([n["midi"] for n in kept]), "phrases": phrase_stats(phr, beat_s), "wall_s": round(time.time() - t0, 1)}


def _sum_hist(per: list[dict]) -> dict:
    out: dict = {}
    for h in per:
        for k, v in h.items():
            out[k] = out.get(k, 0) + v
    return out


def build_outputs(per_song: dict[str, dict]) -> tuple[dict, dict]:
    songs = sorted(per_song)
    sequences = [per_song[s]["tokens"] for s in songs if per_song[s]["tokens"]]
    counts = V5.train_counts(sequences, MAX_ORDER)
    stats = V5.order_stats(counts)
    top = stats[str(MAX_ORDER)]["singleton_context_fraction"]
    verdict = "GENERALIZES" if top is not None and top < V5.SINGLETON_MAX else "MEMORIZES"
    model = {"max_order": MAX_ORDER, "counts": counts}
    check = V5.run_sampling_check(model)
    uni = counts["0"].get("", {})
    tot = sum(uni.values())
    all_midi = [p for s in songs for _t, p in per_song[s]["ticks"]]
    v5 = {"schema_version": 1, "cycle": "v6", "agent": "worker", "run_id": "v6-rules-2026-10-04", "milestone": "M-V6-RULES-1/audio-derived-groove-bass-melody", "kind": "melody_vomm_v5",
          "env_pin_sha256": ENV_PIN_SHA256, "prereg_path": None, "prereg_sha256": None, "script_sha256": sha256_file(Path(__file__).resolve()),
          "eligible_from": "data/v6/stems/manifest.json", "eligible_sha256": sha256_file(SC.STEMS_DIR / "manifest.json"), "n_songs": len(songs), "songs": songs,
          "n_songs_with_events": len(sequences),
          "inputs": {s: {"stem_sha256": SC.song_meta(s)["stems_sha256"][per_song[s]["source_stem"]], "source_stem": per_song[s]["source_stem"], "key_source": per_song[s]["key"]["source"]} for s in songs},
          "vomm_generator_reused": False, "vomm_generator_reuse_reason": "scripts.v5.melody_vomm_v5 pure helpers (tokenize/train_counts/sample_next) reused; c72 vomm_generator.py not applicable",
          "token": {"format": "<deg>|<ioi>", "deg": "scale degree 0..6 of (pc - tonic) % 12 in the mode scale, 'c' if chromatic", "scales": {k: list(v) for k, v in V5.SCALES.items()},
                    "ioi": "round(gap_ticks / 120) snapped to nearest bucket", "ioi_buckets": list(V5.IOI_BUCKETS), "fold": "simultaneous onsets (same tick) -> highest pitch"},
          "model": {"max_order": MAX_ORDER, "context_key": "previous tokens joined by ' ' ('' for order 0)",
                    "escape_rule": f"longest matching context of length <= {MAX_ORDER} with >= 1 count; unseen -> next shorter context; empty order 0 -> '0|4'", "smoothing": "none", "counts": counts},
          "max_order": MAX_ORDER, "counts": counts, "order_stats": stats, "singleton_threshold_order3": V5.SINGLETON_MAX, "singleton_threshold_top_order": V5.SINGLETON_MAX,
          "verdict_enum": list(V5.ENUM), "verdict": verdict, "unigram": {"n": tot, "probs": {t: round(c / tot, 9) for t, c in sorted(uni.items())} if tot else {}}, "vocab": sorted(uni),
          "phrase_structure": V5.phrase_structure({s: per_song[s]["ticks"] for s in songs}),
          "per_song": {s: {"n_vocal_onsets": per_song[s]["n_notes"] if per_song[s]["source_stem"] == "vocals" else 0, "n_lead_onsets": per_song[s]["n_notes"] if per_song[s]["source_stem"] == "other" else 0,
                           "n_events_folded": len(per_song[s]["tokens"]), "n_chromatic": per_song[s]["n_chromatic"], "key": {"tonic": per_song[s]["key"]["tonic"], "mode": per_song[s]["key"]["mode"]},
                           "bpm_v5": per_song[s]["bpm"], "lead_pairing": {"present": per_song[s]["source_stem"] == "other", "source_stem": per_song[s]["source_stem"]}} for s in songs},
          "sampling_check": check, "fd1": "recorded, not tuned",
          "disclosures": ["notes from pyin on separated vocals stems (or 'other' when vocals are > 70 % silent): pitch-tracking noise inflates the chromatic share vs symbolic transcriptions",
                          f"VOMM max_order {MAX_ORDER} (v5 used 3): fewer, better-supported contexts for audio-derived notes; sample_next honours model['max_order']",
                          "the last onset of each song has no next onset; its ioi bucket is 12 (phrase end)", "sequences are trained per song; contexts never cross song boundaries",
                          "no smoothing in the VOMM: the escape rule (longest context with >= 1 count) is the only backoff"],
          "generator": "scripts/v6/rules/melody_v6.py", "source": "audio stems (no symbolic transcription)",
          "register": {"corpus": register_of(all_midi), "median_of_song_medians": _pct([per_song[s]["register"]["median"] for s in songs if per_song[s]["register"]["n"]], 0.5)},
          "rhythm": {k: _sum_hist([per_song[s]["rhythm"][k] for s in songs]) for k in ("slot16_histogram", "ioi16_histogram", "ioi_bucket_histogram", "dur16_histogram")},
          "phrases_v6": {"definition": f"phrase boundary = rest >= {PHRASE_REST_BEATS} beat between note offset and next onset; length in bars rounded to 0.5",
                         "interval_histogram": _sum_hist([per_song[s]["phrases"]["interval_histogram"] for s in songs]), "length_bars_histogram": _sum_hist([per_song[s]["phrases"]["length_bars_histogram"] for s in songs]),
                         "n_phrases": sum(per_song[s]["phrases"]["n_phrases"] for s in songs)}}
    ivh = v5["phrases_v6"]["interval_histogram"]
    n_iv = sum(ivh.values())
    v5["phrases_v6"].update({"step_fraction": round(sum(v for k, v in ivh.items() if 1 <= abs(int(k)) <= 2) / n_iv, 6) if n_iv else None,
                             "repeat_fraction": round(ivh.get("0", 0) / n_iv, 6) if n_iv else None, "leap_fraction": round(sum(v for k, v in ivh.items() if abs(int(k)) > 2) / n_iv, 6) if n_iv else None,
                             "peak_position_mean": round(sum(per_song[s]["phrases"]["peak_position"]["mean"] * per_song[s]["phrases"]["peak_position"]["n"] for s in songs if per_song[s]["phrases"]["peak_position"]["n"])
                                                         / max(1, sum(per_song[s]["phrases"]["peak_position"]["n"] for s in songs)), 6)})
    v6 = {"schema_version": 1, "generator": "scripts/v6/rules/melody_v6.py", "milestone": v5["milestone"], "env_pin_sha256": ENV_PIN_SHA256, "n_songs": len(songs), "songs": songs,
          "max_order": MAX_ORDER, "order_stats": stats, "verdict": verdict, "sampling_check": check, "unigram_top": sorted(uni.items(), key=lambda kv: (-kv[1], kv[0]))[:20],
          "register": v5["register"], "rhythm": v5["rhythm"], "phrases": v5["phrases_v6"], "pyin": dict(PYIN, voiced_prob_min=VOICED_MIN, min_note_s=MIN_NOTE_S, jump_semitones=JUMP_SEMITONES),
          "per_song": {s: {k: v for k, v in per_song[s].items() if k not in ("tokens", "ticks")} for s in songs},
          "source_stems": {src: sorted(s for s in songs if per_song[s]["source_stem"] == src) for src in {per_song[s]["source_stem"] for s in songs}}, "v5_file": str(OUT_V5.relative_to(WS))}
    return v5, v6


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--songs", default=None)
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--out-v5", default=str(OUT_V5))
    ap.add_argument("--out-v6", default=str(OUT_V6))
    args = ap.parse_args(argv)
    shas = [s.strip() for s in args.songs.split(",")] if args.songs else SC.corpus_songs()
    per_song = SC.run_parallel(analyze, shas, args.workers)
    for s in shas:
        a = per_song[s]
        print(f"{s} {str(a['title'])[:24]:24s} src={a['source_stem']} silent={a['vocals_silent_fraction']} voiced={a['voiced_frame_fraction']} notes={a['n_notes']} on_grid={a['n_notes_on_grid']} "
              f"key={a['key']['tonic']}:{a['key']['mode']} median={a['register']['median']} phrases={a['phrases']['n_phrases']} step={a['phrases']['step_fraction']} wall={a['wall_s']}s", flush=True)
    v5, v6 = build_outputs(per_song)
    write_json_atomic(args.out_v5, v5)
    write_json_atomic(args.out_v6, v6)
    print(f"verdict {v5['verdict']} order_stats {v5['order_stats']}; register {v5['register']['corpus']}; intervals step={v6['phrases']['step_fraction']} "
          f"repeat={v6['phrases']['repeat_fraction']} leap={v6['phrases']['leap_fraction']}; phrase bars {v6['phrases']['length_bars_histogram']}; wrote {args.out_v5}, {args.out_v6}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
