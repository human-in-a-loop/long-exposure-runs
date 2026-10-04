#!/usr/bin/python3
"""v6 rules — bass_pitch_v6: interval-class bass model (bass_pitch_v5 schema) from the bass stem's pyin pitch at each bass onset.

created: 2026-10-04
milestone: M-V6-RULES-1/audio-derived-groove-bass-melody

  /usr/bin/python3 scripts/v6/rules/bass_pitch_v6.py [--songs sha16,...] [--workers 2] [--out-v5 data/v5/rules/bass_pitch_v5.json]
      [--out-v6 data/v6/rules/bass_pitch_v6.json]

Pitch: librosa.pyin on the bass stem (fmin 30, fmax 500 Hz, frame 4096, hop 256; 2048 frames leave 30-60 Hz notes mostly
unvoiced) -> per bass onset of the shared onset cache (scripts/v6/rules/stems_common_v6.py = the microtiming grid) the median
f0 of the frames pyin's Viterbi path marks voiced in [onset + 20 ms, onset + 120 ms) (the attack transient is skipped),
rounded to MIDI; onsets without a voiced frame are dropped (per-song voiced coverage reported; the dropped onsets are the
quiet ones, typically < -35 dB spill). Chords: beat-level chord roots on the SAME grid beat index — the sibling's
data/v6/rules/chords/<sha16>/chords_v6.json when present (adapter `adapt_sibling_chords`: chords.chord_stream entries with
`grid_beat`; generic fallbacks: a list under chord_stream|beats|chords|stream with grid_beat | time | beat and root|root_pc),
else — or when > 50 % of its beats are 'N' — the chroma-template Viterbi fallback cached in data/v6/rules/_bassroots/<sha16>.json
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

PYIN = {"fmin": 30.0, "fmax": 500.0, "frame_length": 4096, "hop_length": 256}
ONSET_WIN_S = (0.020, 0.120)  # [onset + 20 ms, onset + 120 ms)
VOICED = "pyin voiced_flag (Viterbi voiced state) and finite f0"
PITCH_PARAMS = dict(PYIN, onset_window_s=list(ONSET_WIN_S), voiced=VOICED)
SIBLING_N_MAX = 0.5  # a sibling chord stream with more 'N' beats than this falls back to the bass+other chroma roots
PITCH_DIR = SC.RULES_V6 / "_pitch"
OUT_V5 = WS / "data/v5/rules/bass_pitch_v5.json"
OUT_V6 = WS / "data/v6/rules/bass_pitch_v6.json"
GROOVE_V5 = WS / "data/v5/rules/groove_v5_v2_full.json"


# ---------------------------------------------------------------------------------------------------------- pitch ----
def pyin_track(y: np.ndarray, fmin: float, fmax: float, frame_length: int = 2048, hop_length: int = 256) -> tuple:
    """(f0_hz, voiced_flag, voiced_prob, frame_times_s) — librosa.pyin, deterministic (Viterbi)."""
    import librosa
    f0, flag, prob = librosa.pyin(y, fmin=fmin, fmax=fmax, sr=SC.MT.SR, frame_length=frame_length, hop_length=hop_length, fill_na=np.nan)
    t = librosa.frames_to_time(np.arange(f0.size), sr=SC.MT.SR, hop_length=hop_length)
    return f0, np.asarray(flag, dtype=bool), prob, t


def hz_to_midi(f: float) -> int:
    return int(round(69.0 + 12.0 * np.log2(float(f) / 440.0)))


def pitch_at_onsets(f0: np.ndarray, voiced: np.ndarray, t: np.ndarray, onset_times: list, win_s: tuple = ONSET_WIN_S) -> list:
    """Per onset: MIDI of the median f0 over the voiced frames in [onset + win_s[0], onset + win_s[1]), or None when none is voiced."""
    out = []
    for on in onset_times:
        i0, i1 = int(np.searchsorted(t, on + win_s[0], side="left")), int(np.searchsorted(t, on + win_s[1], side="left"))
        seg_f = f0[i0:i1]
        ok = np.asarray(voiced[i0:i1], dtype=bool) & np.isfinite(seg_f)
        out.append(hz_to_midi(float(np.median(seg_f[ok]))) if ok.any() else None)
    return out


def cache_valid(path: Path, params: dict, n_onsets: int | None = None) -> dict | None:
    """The cached record when it exists and was produced with `params` (and, if given, over the same onset count), else None."""
    if not path.exists():
        return None
    d = read_json(path)
    return d if d.get("pyin") == params and (n_onsets is None or d.get("n_onsets") == n_onsets) else None


def bass_pitches(sha16: str, onsets: dict) -> dict:
    """Cached per-onset MIDI list for the bass stream of the onset cache (same order as onsets['streams']['bass'])."""
    rows = onsets["streams"]["bass"]
    p = PITCH_DIR / f"{sha16}_bass.json"
    cached = cache_valid(p, PITCH_PARAMS, len(rows))
    if cached is not None:
        return cached
    y = SC.stem(sha16, "bass")
    f0, flag, _prob, t = pyin_track(y, **PYIN)
    midi = pitch_at_onsets(f0, flag & np.isfinite(f0), t, [r[2] for r in rows])
    voiced_frames = float(np.mean(flag)) if flag.size else 0.0
    out = {"schema_version": 1, "sha16": sha16, "stem": "bass", "pyin": dict(PITCH_PARAMS), "n_onsets": len(rows),
           "n_pitched": sum(1 for m in midi if m is not None), "midi": midi, "voiced_frame_fraction": round(voiced_frames, 6), "env_pin_sha256": ENV_PIN_SHA256}
    out["voiced_coverage"] = round(out["n_pitched"] / out["n_onsets"], 6) if rows else None
    write_json_atomic(p, out)
    return out


# --------------------------------------------------------------------------------------------------------- chords ----
def adapt_sibling_chords(d: dict, grid: dict) -> tuple[list, dict | None, dict]:
    """Adapter for the sibling's chords_v6.json -> v5 chord_stream [{beat, root, quality, state}] on the GRID beat index.

    scripts/v6/rules/chords_v6.py writes d['chords']['chord_stream'] whose entries carry `grid_beat` (microtiming grid beat index,
    the index bass_pitch_v6.onset_ticks uses), `beat` (stream beat = grid beat - phase), `root` (None on 'N') and `quality`.
    Generic fallbacks: a list under chord_stream|beats|chords|stream; per entry grid_beat, else a time re-mapped onto the grid,
    else `beat` (+ the file's grid phase when its bar_convention declares the 'grid beat - phase' stream convention)."""
    seq = None
    for k in ("chord_stream", "beats", "chords", "stream"):
        v = d.get(k)
        if isinstance(v, dict) and isinstance(v.get("chord_stream"), list):
            seq = v["chord_stream"]
            break
        if isinstance(v, list):
            seq = v
            break
    if seq is None:
        raise ValueError("chords_v6.json: no beat-level list under chords.chord_stream|chord_stream|beats|chords|stream")
    key = d.get("key") if isinstance(d.get("key"), dict) else ({"tonic": d.get("tonic"), "mode": d.get("mode", "major")} if d.get("tonic") is not None else None)
    if key is not None:  # the sibling's key block carries a windowed track + profile; keep the summary the rule files need
        key = {k: key[k] for k in ("tonic", "mode", "tonic_name", "corr", "confidence", "low_confidence") if k in key}
    conv = str((d.get("grid") or {}).get("bar_convention", ""))
    phase = int((d.get("grid") or {}).get("phase", 0)) if "grid beat - phase" in conv else 0
    stream, notes = {}, {"entries": len(seq), "by_grid_beat": 0, "by_time": 0, "by_stream_beat": 0, "stream_beat_phase_added": phase}
    for i, e in enumerate(seq):
        root = e.get("root", e.get("root_pc"))
        tm = next((e[k] for k in ("time", "beat_time", "t", "t_s") if k in e), None)
        if "grid_beat" in e:
            beat, notes["by_grid_beat"] = int(e["grid_beat"]), notes["by_grid_beat"] + 1
        elif tm is not None:
            g = SC.time_to_grid(float(tm), grid["beat_times"])
            if g is None:
                continue
            beat, notes["by_time"] = g[0], notes["by_time"] + 1
        else:
            beat, notes["by_stream_beat"] = int(e.get("beat", i)) + phase, notes["by_stream_beat"] + 1
        state = e.get("state") or ("N" if root is None else "ok")
        n_state = root is None or state == "N" or e.get("quality") == "N" or e.get("chord") == "N"
        stream[beat] = {"beat": beat, "root": None if n_state else int(root) % 12, "quality": None if n_state else e.get("quality"), "state": "N" if n_state else state}
    return [stream[b] for b in sorted(stream)], key, notes


def _rel(p: Path) -> str:
    return str(p.relative_to(WS)) if str(p).startswith(str(WS)) else str(p)


def chord_stream_for(sha16: str, onsets: dict) -> tuple[list, dict | None, dict]:
    """(chord_stream, key, source) — sibling chords_v6.json first, else the fallback roots (see stems_common_v6.build_bassroots)."""
    sib = SC.CHORDS_DIR / sha16 / "chords_v6.json"
    if sib.exists():
        try:
            stream, key, notes = adapt_sibling_chords(read_json(sib), onsets["grid"])
            n_frac = round(sum(1 for c in stream if c["state"] == "N") / len(stream), 6) if stream else 1.0
            if n_frac <= SIBLING_N_MAX:
                return stream, key, {"source": "chords_v6", "path": _rel(sib), "sha256": sha256_file(sib), "adapter": notes, "n_fraction": n_frac}
            why = {"sibling_n_fraction": n_frac, "rule": f"sibling stream > {SIBLING_N_MAX:.0%} 'N' beats (its harmonic mix is below its silence floor while the bass plays) -> fallback"}
        except Exception as exc:  # noqa: BLE001  the sibling's schema is not final; fall back and disclose
            why = {"sibling_present_but_unreadable": f"{type(exc).__name__}: {exc}"}
        fb = SC.load_bassroots(sha16, onsets)
        return fb["chord_stream"], fb["key"], {"source": "fallback_chroma_viterbi", "path": _rel(SC.BASSROOTS_DIR / f"{sha16}.json"), **why}
    fb = SC.load_bassroots(sha16, onsets)
    return fb["chord_stream"], fb["key"], {"source": "fallback_chroma_viterbi", "path": _rel(SC.BASSROOTS_DIR / f"{sha16}.json"),
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
                          "gm_bass_range": [V5.GM_BASS_LO, V5.GM_BASS_HI],
                          "pitch": f"librosa.pyin {PYIN}; median f0 of the Viterbi-voiced frames in [onset + {int(ONSET_WIN_S[0] * 1000)} ms, onset + {int(ONSET_WIN_S[1] * 1000)} ms)"},
          **model, "sampling_check": check, "fd1": "recorded, not tuned",
          "disclosures": ["pitch from separated bass stems (htdemucs) via pyin; onsets without a Viterbi-voiced frame in [20 ms, 120 ms) after the onset are dropped "
                          "(voiced_coverage per song; the dropped onsets are the quiet ones, typically < -35 dB spill detected as bass onsets)",
                          "chord roots: sibling chords_v6.json (chords.chord_stream[].grid_beat) when present else chroma-template Viterbi fallback (per-song chord_source)",
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
          "pyin": dict(PITCH_PARAMS), "v5_file": str(OUT_V5.relative_to(WS))}
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
