#!/usr/bin/python3
"""v6 rules — bass_pitch_v6: interval-class bass model (bass_pitch_v5 schema) from the bass stem's pyin pitch at each bass onset.

created: 2026-10-04
milestone: M-V6-RULES-1/audio-derived-groove-bass-melody

  /usr/bin/python3 scripts/v6/rules/bass_pitch_v6.py [--songs sha16,...] [--workers 2] [--out-v5 data/v5/rules/bass_pitch_v5.json]
      [--out-v6 data/v6/rules/bass_pitch_v6.json]

Pitch: librosa.pyin on the bass stem (fmin 30, fmax 500 Hz, frame 2048, hop 256) -> per bass onset of the shared onset cache
(scripts/v6/rules/stems_common_v6.py = the microtiming grid) the median f0 of the voiced frames (voiced probability > 0.5) in
the 60 ms after the onset, rounded to MIDI; onsets without a voiced frame are dropped (per-song voiced coverage reported).
Chords: beat-level chord roots on the SAME grid beat index — the sibling's data/v6/rules/chords/<sha16>/chords_v6.json when
present (adapter `adapt_sibling_chords`: list under chord_stream|beats|chords, root|root_pc per entry, beat index or a time
re-mapped onto the grid), else the chroma-template Viterbi fallback cached in data/v6/rules/_bassroots/<sha16>.json
(DEPENDENCY, swappable: the output records the source per song). Each onset becomes a v5 tick (beat_index * 480 + sub16 * 120)
and scripts/v5/bass_pitch_v5.analyze_song / build_model / run_sampling_check (READ-ONLY imports) classify root / fifth /
octave / third / approach (+/-1-2 semitones into the next change's root, only when the next beat's root differs) / other
conditioned on "<slot%4>|<change-flag>", exactly as v5. Register = per-song median / p25 / p75 of the pitched onsets. No PRNG.
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
from scripts.v6.v6_data_common import ENV_PIN_SHA256, WS, read_json, sha256_file, write_json_atomic  # noqa: E402
import numpy as np  # noqa: E402
from scripts.v5 import bass_pitch_v5 as V5  # noqa: E402  READ-ONLY pure exports

PYIN = {"fmin": 30.0, "fmax": 500.0, "frame_length": 2048, "hop_length": 256}
ONSET_WIN_S = 0.060
VOICED_MIN = 0.5
PITCH_DIR = SC.RULES_V6 / "_pitch"
OUT_V5 = WS / "data/v5/rules/bass_pitch_v5.json"
OUT_V6 = WS / "data/v6/rules/bass_pitch_v6.json"
GROOVE_V5 = WS / "data/v5/rules/groove_v5_v2_full.json"


# ---------------------------------------------------------------------------------------------------------- pitch ----
def pyin_track(y: np.ndarray, fmin: float, fmax: float, frame_length: int = 2048, hop_length: int = 256) -> tuple:
    """(f0_hz, voiced_prob, frame_times_s) — librosa.pyin, deterministic (Viterbi)."""
    import librosa
    f0, _flag, prob = librosa.pyin(y, fmin=fmin, fmax=fmax, sr=SC.MT.SR, frame_length=frame_length, hop_length=hop_length, fill_na=np.nan)
    t = librosa.frames_to_time(np.arange(f0.size), sr=SC.MT.SR, hop_length=hop_length)
    return f0, prob, t


def hz_to_midi(f: float) -> int:
    return int(round(69.0 + 12.0 * np.log2(float(f) / 440.0)))


def pitch_at_onsets(f0: np.ndarray, prob: np.ndarray, t: np.ndarray, onset_times: list, win_s: float = ONSET_WIN_S, prob_min: float = VOICED_MIN) -> list:
    """Per onset: MIDI of the median voiced f0 in [onset, onset + win_s), or None when no frame is voiced (> prob_min)."""
    out = []
    for on in onset_times:
        i0, i1 = int(np.searchsorted(t, on, side="left")), int(np.searchsorted(t, on + win_s, side="left"))
        seg_f, seg_p = f0[i0:i1], prob[i0:i1]
        ok = (seg_p > prob_min) & np.isfinite(seg_f)
        out.append(hz_to_midi(float(np.median(seg_f[ok]))) if ok.any() else None)
    return out


def bass_pitches(sha16: str, onsets: dict) -> dict:
    """Cached per-onset MIDI list for the bass stream of the onset cache (same order as onsets['streams']['bass'])."""
    p = PITCH_DIR / f"{sha16}_bass.json"
    if p.exists():
        return read_json(p)
    y = SC.stem(sha16, "bass")
    f0, prob, t = pyin_track(y, **PYIN)
    rows = onsets["streams"]["bass"]
    midi = pitch_at_onsets(f0, prob, t, [r[2] for r in rows])
    voiced_frames = float(np.mean(prob > VOICED_MIN)) if prob.size else 0.0
    out = {"schema_version": 1, "sha16": sha16, "stem": "bass", "pyin": dict(PYIN, onset_window_s=ONSET_WIN_S, voiced_prob_min=VOICED_MIN), "n_onsets": len(rows),
           "n_pitched": sum(1 for m in midi if m is not None), "midi": midi, "voiced_frame_fraction": round(voiced_frames, 6), "env_pin_sha256": ENV_PIN_SHA256}
    out["voiced_coverage"] = round(out["n_pitched"] / out["n_onsets"], 6) if rows else None
    write_json_atomic(p, out)
    return out


# --------------------------------------------------------------------------------------------------------- chords ----
def adapt_sibling_chords(d: dict, grid: dict) -> tuple[list, dict | None, dict]:
    """Best-effort adapter for the sibling's chords_v6.json -> v5 chord_stream [{beat, root, quality, state}] on the grid beat index."""
    seq = next((d[k] for k in ("chord_stream", "beats", "chords", "stream") if isinstance(d.get(k), list)), None)
    if seq is None:
        raise ValueError("chords_v6.json: no beat-level list under chord_stream|beats|chords|stream")
    key = d.get("key") if isinstance(d.get("key"), dict) else ({"tonic": d.get("tonic"), "mode": d.get("mode", "major")} if d.get("tonic") is not None else None)
    stream, notes, by_time = {}, {"entries": len(seq)}, 0
    for i, e in enumerate(seq):
        root = e.get("root", e.get("root_pc"))
        tm = next((e[k] for k in ("time", "beat_time", "t", "t_s") if k in e), None)
        if tm is not None:
            g = SC.time_to_grid(float(tm), grid["beat_times"])
            if g is None:
                continue
            beat, by_time = g[0], by_time + 1
        else:
            beat = int(e.get("beat", i))
        state = e.get("state") or ("N" if root is None else "ok")
        stream[beat] = {"beat": beat, "root": None if root is None or state == "N" else int(root) % 12, "quality": e.get("quality"), "state": "N" if root is None else state}
    notes["mapped_by_time"] = by_time
    return [stream[b] for b in sorted(stream)], key, notes


def chord_stream_for(sha16: str, onsets: dict) -> tuple[list, dict | None, dict]:
    """(chord_stream, key, source) — sibling chords_v6.json first, else the fallback roots (see stems_common_v6.build_bassroots)."""
    sib = SC.CHORDS_DIR / sha16 / "chords_v6.json"
    if sib.exists():
        try:
            stream, key, notes = adapt_sibling_chords(read_json(sib), onsets["grid"])
            return stream, key, {"source": "chords_v6", "path": str(sib.relative_to(WS)), "sha256": sha256_file(sib), "adapter": notes}
        except Exception as exc:  # noqa: BLE001  the sibling's schema is not final; fall back and disclose
            fb = SC.load_bassroots(sha16, onsets)
            return fb["chord_stream"], fb["key"], {"source": "fallback_chroma_viterbi", "path": str((SC.BASSROOTS_DIR / f"{sha16}.json").relative_to(WS)),
                                                   "sibling_present_but_unreadable": f"{type(exc).__name__}: {exc}"}
    fb = SC.load_bassroots(sha16, onsets)
    return fb["chord_stream"], fb["key"], {"source": "fallback_chroma_viterbi", "path": str((SC.BASSROOTS_DIR / f"{sha16}.json").relative_to(WS)),
                                           "dependency": "swap in data/v6/rules/chords/<sha16>/chords_v6.json when the sibling lands"}


def onset_ticks(rows: list, midi: list, grid: dict) -> list[tuple[int, int]]:
    """[(tick, pitch)] for pitched onsets: tick = grid beat index * 480 + sub16 * 120 (bar/slot -> beat index via phase + hypermeter offset)."""
    out = []
    for r, m in zip(rows, midi):
        if m is None:
            continue
        bar, slot = int(r[0]), int(r[1])
        beat = (bar + grid["hypermeter_offset"]) * 4 + slot // 4 + grid["phase"]
        out.append((beat * SC.PPQ + (slot % 4) * SC.TICKS_16TH, int(m)))
    return sorted(out)


def analyze(sha16: str) -> dict:
    t0 = time.time()
    onsets = SC.load_onsets(sha16)
    pitches = bass_pitches(sha16, onsets)
    stream, key, src = chord_stream_for(sha16, onsets)
    ticks = onset_ticks(onsets["streams"]["bass"], pitches["midi"], onsets["grid"])
    a = V5.analyze_song(ticks, stream, int(onsets["grid"]["downbeat_phase_offset_16th"]))
    a.update({"title": onsets.get("title"), "band": onsets.get("band"), "bpm": onsets["grid"]["bpm"], "n_bass_onsets": pitches["n_onsets"], "n_pitched": pitches["n_pitched"],
              "voiced_coverage": pitches["voiced_coverage"], "voiced_frame_fraction": pitches["voiced_frame_fraction"], "chord_source": src, "key": key,
              "n_chord_beats": len(stream), "n_chord_N": sum(1 for c in stream if c.get("state") == "N"), "wall_s": round(time.time() - t0, 1)})
    return a


def build_outputs(per_song: dict[str, dict]) -> tuple[dict, dict]:
    model = V5.build_model(per_song)
    check = V5.run_sampling_check(model)
    songs = sorted(per_song)
    marg = model["marginal"]
    v5 = {"schema_version": 1, "cycle": "v6", "agent": "worker", "run_id": "v6-rules-2026-10-04", "milestone": "M-V6-RULES-1/audio-derived-groove-bass-melody",
          "kind": "bass_pitch_model_v5", "env_pin_sha256": ENV_PIN_SHA256, "prereg_path": None, "prereg_sha256": None,
          "script_sha256": sha256_file(Path(__file__).resolve()), "eligible_from": "data/v6/stems/manifest.json", "eligible_sha256": sha256_file(SC.STEMS_DIR / "manifest.json"),
          "n_songs": len(songs), "songs": songs,
          "inputs": {s: {"bass_stem_sha256": SC.song_meta(s)["stems_sha256"]["bass"], "chord_source": per_song[s]["chord_source"], "bpm": per_song[s]["bpm"]} for s in songs},
          "groove_path": str(GROOVE_V5.relative_to(WS)), "groove_sha256": sha256_file(GROOVE_V5) if GROOVE_V5.exists() else None,
          "definitions": {"beat": "grid beat index (microtiming_v6 smoothed grid); tick = beat * 480 + sub16 * 120", "slot": "sub16 in 0..3", "chord": "chord_stream[beat]; null root / state 'N' skipped",
                          "chord_change_flag": "next beat exists with non-null root != current root", "approach": "pc within +/-1 or +/-2 semitones of the NEXT chord root, only when chord_change_flag",
                          "root": "pc == root and not octave", "fifth": "(pc - root) % 12 == 7", "third": "(pc - root) % 12 in {3, 4}",
                          "octave": "pc == root and pitch >= lowest root-pc bass note of the chord segment + 12", "other": "remaining onsets", "conditional_key": "<slot>|<chg>",
                          "smoothing": "probs = (count + 0.5) / (n + 0.5 * 6) over class_order", "register": "per song median / p25 (iqr_lo) / p75 (iqr_hi) of pitched bass onsets",
                          "gm_bass_range": [V5.GM_BASS_LO, V5.GM_BASS_HI], "pitch": f"librosa.pyin {PYIN}; median voiced f0 (prob > {VOICED_MIN}) over {int(ONSET_WIN_S * 1000)} ms after the onset"},
          **model, "sampling_check": check, "fd1": "recorded, not tuned",
          "disclosures": ["pitch from separated bass stems (htdemucs) via pyin; onsets without a voiced frame in the 60 ms window are dropped (voiced_coverage per song)",
                          "chord roots: sibling chords_v6.json when present else chroma-template Viterbi fallback (per-song chord_source)",
                          "octave = pc == chord root AND pitch >= lowest root-pc bass note of the chord segment + 12 (v5 definition, measurable here too)",
                          "chord_change_flag is 0 when the next beat is null/'N' or past the end of chord_stream"],
          "generator": "scripts/v6/rules/bass_pitch_v6.py", "source": "audio stems (no symbolic transcription)"}
    v6 = {"schema_version": 1, "generator": "scripts/v6/rules/bass_pitch_v6.py", "milestone": v5["milestone"], "env_pin_sha256": ENV_PIN_SHA256, "n_songs": len(songs), "songs": songs,
          "class_order": model["class_order"], "marginal": marg, "marginal_fractions": {c: round(marg["counts"][c] / marg["n"], 6) if marg["n"] else None for c in model["class_order"]},
          "conditional": model["conditional"], "register": model["register"], "downbeat": model["downbeat"], "chord_change_rate": model["chord_change_rate"], "sampling_check": check,
          "n_events": model["n_events"], "n_onsets_total": model["n_onsets_total"],
          "per_song": {s: {"title": a["title"], "band": a["band"], "bpm": a["bpm"], "n_bass_onsets": a["n_bass_onsets"], "n_pitched": a["n_pitched"], "voiced_coverage": a["voiced_coverage"],
                           "voiced_frame_fraction": a["voiced_frame_fraction"], "n_used": a["n_used"], "n_skipped_null_chord": a["n_skipped_null_chord"], "register": a["register"],
                           "counts": model["per_song"][s]["counts"], "class_fractions": {c: round(v / a["n_used"], 6) if a["n_used"] else None for c, v in model["per_song"][s]["counts"].items()},
                           "chord_source": a["chord_source"]["source"], "key": a["key"], "n_chord_beats": a["n_chord_beats"], "n_chord_N": a["n_chord_N"]} for s, a in per_song.items()},
          "chord_sources": {src: sorted(s for s, a in per_song.items() if a["chord_source"]["source"] == src) for src in {a["chord_source"]["source"] for a in per_song.values()}},
          "pyin": dict(PYIN, onset_window_s=ONSET_WIN_S, voiced_prob_min=VOICED_MIN), "v5_file": str(OUT_V5.relative_to(WS))}
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
        print(f"{s} {str(a['title'])[:24]:24s} onsets={a['n_bass_onsets']} pitched={a['n_pitched']} cov={a['voiced_coverage']} used={a['n_used']} "
              f"median={a['register']['median']} chords={a['chord_source']['source']} key={a['key']} wall={a['wall_s']}s", flush=True)
    v5, v6 = build_outputs(per_song)
    write_json_atomic(args.out_v5, v5)
    write_json_atomic(args.out_v6, v6)
    print(f"marginal {v6['marginal_fractions']}; register {v6['register']['corpus']}; sampling_check pass={v5['sampling_check']['pass']} "
          f"(sampled root-pc {v5['sampling_check']['sampled_root_pc_fraction']} vs corpus downbeat {v5['sampling_check']['corpus_downbeat_root_pc_fraction']})")
    print(f"chord sources {v6['chord_sources']}; wrote {args.out_v5}, {args.out_v6}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
