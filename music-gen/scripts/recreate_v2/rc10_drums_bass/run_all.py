#!/usr/bin/env /usr/bin/python3
# RC10 Branch A main runner: transcribe, D4, score, winners, verdict, A/B.
# created: 2026-09-02, cycle 54, run-2026-08-28T040704Z, worker, fork bdd7bb47f1b5 clone-0
import json
import sys
import time
import hashlib
from pathlib import Path

import numpy as np
import soundfile as sf

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from scripts.recreate_v2.rc10_drums_bass._common import (
    load_focus_songs, BASELINE_DIR, IMPL_DIR, AB_DIR, RUBRIC_HASH, RUBRIC_DOC,
    tempo_for, sha256_of, slice_and_load, write_json_canonical,
)
from scripts.recreate_v2.rc10_drums_bass import drums as drums_mod
from scripts.recreate_v2.rc10_drums_bass import bass as bass_mod
from scripts.recreate_v2.rc10_drums_bass import postproc as pp_mod
from scripts.recreate_v2.rc10_drums_bass import metrics as met_mod
from scripts.recreate_v2.rc10_drums_bass import render as ren_mod


def _hash_notes(notes):
    """Canonical hash of a notes list (candidate-name comparison anchor)."""
    payload = json.dumps(notes, sort_keys=True).encode()
    return hashlib.sha256(payload).hexdigest()


def process_song(song, drums_only=False, bass_only=False):
    sha16 = song["audio_sha16"]
    t0 = float(song["chosen_section"]["t_start_s"])
    t1 = float(song["chosen_section"]["t_end_s"])
    bpm = tempo_for(sha16) if (BASELINE_DIR.parent.parent / "data/rc5_impl" / sha16).exists() else 120.0
    bpm = tempo_for(sha16)

    drums_wav = BASELINE_DIR / sha16 / "rc9_6stem" / "drums.wav"
    bass_wav = BASELINE_DIR / sha16 / "rc9_6stem" / "bass.wav"

    out_song = IMPL_DIR / sha16
    out_song.mkdir(parents=True, exist_ok=True)

    rows = []

    # ----- DRUMS -----
    y_d, sr_d = slice_and_load(drums_wav, t0, t1)
    ref_onsets = drums_mod.reference_onsets(y_d, sr_d)
    ref_count = len(ref_onsets)

    if not bass_only:
        d_notes_raw = drums_mod.transcribe(y_d, sr_d)
        for pp_on in (False, True):
            notes = pp_mod.apply_d4(d_notes_raw, y_d, sr_d, bpm, "drums") if pp_on else d_notes_raw
            onsets = [n["onset_s"] for n in notes]
            f1, tp, fp, fn = met_mod.onset_f1(onsets, ref_onsets)
            count_ratio = (len(notes) / ref_count) if ref_count else 0.0
            passed = met_mod.drums_gate(f1, count_ratio)
            row = {
                "song_id": sha16, "stem": "drums", "candidate": "onset_band_energy",
                "d4": bool(pp_on), "bpm_used": float(bpm),
                "n_notes": len(notes), "ref_count": ref_count,
                "onset_f1": float(f1), "tp": tp, "fp": fp, "fn": fn,
                "count_ratio": float(count_ratio),
                "median_midi_pitch": met_mod.median_midi_pitch(notes),
                "framewise_f0_agreement": None, "low_band_corr": None,
                "passed": passed,
                "notes_sha256": _hash_notes(notes),
            }
            rows.append(row)
            _write_notes(out_song, "drums", "onset_band_energy", pp_on, notes, row)

    # ----- BASS -----
    if not drums_only:
        y_b, sr_b = slice_and_load(bass_wav, t0, t1)
        # baseline reference: pyin voiced-segment count on baseline stem
        ref_bass_notes = bass_mod.transcribe_pyin(y_b, sr_b)
        ref_bass_count = len(ref_bass_notes)

        for cand_name, cand_fn in [
            ("bp_defaults", bass_mod.transcribe_bp_defaults),
            ("bp_tuned", bass_mod.transcribe_bp_tuned),
            ("pyin_mono", bass_mod.transcribe_pyin),
        ]:
            try:
                raw = cand_fn(y_b, sr_b)
            except Exception as e:
                print(f"[bass {cand_name} {sha16}] ERROR: {e}", flush=True)
                raw = []
            for pp_on in (False, True):
                notes = pp_mod.apply_d4(raw, y_b, sr_b, bpm, "bass") if pp_on else raw
                y_rendered = _quick_render_bass(notes, sr_b) if notes else np.zeros(len(y_b), dtype=np.float32)
                # framewise-f0 agreement between baseline stem and rendered
                agree = met_mod.framewise_f0_agreement(y_b, y_rendered, sr_b) if len(y_rendered) > 0 else 0.0
                low_corr = met_mod.low_band_correlation(y_b, y_rendered, sr_b) if len(y_rendered) > 0 else 0.0
                med_midi = met_mod.median_midi_pitch(notes)
                count_ratio = (len(notes) / ref_bass_count) if ref_bass_count else 0.0
                passed = met_mod.bass_gate(agree, low_corr, med_midi, count_ratio)
                row = {
                    "song_id": sha16, "stem": "bass", "candidate": cand_name,
                    "d4": bool(pp_on), "bpm_used": float(bpm),
                    "n_notes": len(notes), "ref_count": ref_bass_count,
                    "onset_f1": None, "tp": None, "fp": None, "fn": None,
                    "count_ratio": float(count_ratio),
                    "median_midi_pitch": int(med_midi),
                    "framewise_f0_agreement": float(agree),
                    "low_band_corr": float(low_corr),
                    "passed": passed,
                    "notes_sha256": _hash_notes(notes),
                }
                rows.append(row)
                _write_notes(out_song, "bass", cand_name, pp_on, notes, row)

    return rows


def _write_notes(out_song, stem, cand, pp_on, notes, row):
    sub = out_song / stem / cand / ("d4on" if pp_on else "d4off")
    sub.mkdir(parents=True, exist_ok=True)
    write_json_canonical(sub / "notes.json", notes)
    write_json_canonical(sub / "metrics.json", row)


def _quick_render_bass(notes, sr):
    """Cheap synthetic rendering: sine tones at note frequencies over their durations.

    Used only for framewise-f0 / low-band-correlation metrics; NOT the A/B artifact.
    """
    import numpy as np
    total_s = 0.0
    for n in notes:
        total_s = max(total_s, n["onset_s"] + n["duration_s"])
    if total_s <= 0:
        return np.zeros(1, dtype=np.float32)
    n_samp = int(round(total_s * sr)) + sr  # small tail
    y = np.zeros(n_samp, dtype=np.float32)
    for n in notes:
        f = 440.0 * 2 ** ((n["pitch"] - 69) / 12.0)
        a = int(n["onset_s"] * sr)
        b = a + int(n["duration_s"] * sr)
        if b <= a or a >= n_samp:
            continue
        b = min(b, n_samp)
        t = np.arange(b - a, dtype=np.float32) / sr
        env = np.exp(-3.0 * t / max(0.01, n["duration_s"]))
        y[a:b] += 0.2 * env * np.sin(2 * np.pi * f * t)
    peak = float(np.max(np.abs(y)) or 1.0)
    if peak > 0.98:
        y = y * (0.98 / peak)
    return y


def score_all():
    songs = load_focus_songs()
    IMPL_DIR.mkdir(parents=True, exist_ok=True)
    all_rows = []
    for s in songs:
        print(f"[song {s['audio_sha16']}] processing…", flush=True)
        rows = process_song(s)
        all_rows.extend(rows)
    _write_scorecard(all_rows)
    winners = _winners(all_rows)
    write_json_canonical(IMPL_DIR / "winner_per_stem.json", winners)
    verdict = _verdict(all_rows, winners)
    write_json_canonical(IMPL_DIR / "verdict.json", verdict)
    # A/B pairs for the winner per stem per song
    _write_ab_pairs(all_rows, winners, songs)
    return verdict


def _write_scorecard(rows):
    cols = [
        "song_id", "stem", "candidate", "d4", "bpm_used", "n_notes", "ref_count",
        "onset_f1", "tp", "fp", "fn", "count_ratio", "median_midi_pitch",
        "framewise_f0_agreement", "low_band_corr", "passed", "notes_sha256",
    ]
    lines = ["\t".join(cols)]
    def _fmt(v):
        if v is None: return ""
        if isinstance(v, bool): return "1" if v else "0"
        if isinstance(v, float): return f"{v:.6f}"
        return str(v)
    for r in sorted(rows, key=lambda r: (r["song_id"], r["stem"], r["candidate"], r["d4"])):
        lines.append("\t".join(_fmt(r[c]) for c in cols))
    (IMPL_DIR / "scorecard.tsv").write_text("\n".join(lines) + "\n")


def _winners(rows):
    """Winner per stem = candidate with highest composite (drums: F1; bass: f0-agreement)
    with D4 on, ranked by majority (≥3/5) passing then by mean composite score."""
    from collections import defaultdict
    d4_rows = [r for r in rows if r["d4"]]
    per_stem_cand = defaultdict(list)
    for r in d4_rows:
        per_stem_cand[(r["stem"], r["candidate"])].append(r)
    result = {}
    for stem in ("drums", "bass"):
        cands = [(k[1], vs) for k, vs in per_stem_cand.items() if k[0] == stem]
        if not cands:
            continue
        scored = []
        for name, vs in cands:
            passes = sum(1 for r in vs if r["passed"])
            comps = [r["onset_f1"] if stem == "drums" else r["framewise_f0_agreement"] for r in vs]
            comps = [c for c in comps if c is not None]
            mean_comp = float(sum(comps) / len(comps)) if comps else 0.0
            scored.append((name, passes, mean_comp))
        # rank: passes desc, mean_comp desc, sha256(name) tiebreak
        scored.sort(key=lambda x: (-x[1], -x[2], hashlib.sha256(x[0].encode()).hexdigest()))
        winner_name, passes, mean_comp = scored[0]
        result[stem] = {
            "candidate": winner_name,
            "passes_gate_songs": passes,
            "mean_composite": mean_comp,
            "ranked": [{"candidate": n, "passes": p, "mean_composite": c} for n, p, c in scored],
        }
    return result


def _verdict(rows, winners):
    """Verdict per D8."""
    from collections import defaultdict
    # Count songs where the WINNER candidate (D4 on) passes.
    d4_rows = [r for r in rows if r["d4"]]
    def stem_pass_count(stem):
        w = winners.get(stem, {}).get("candidate")
        if not w:
            return 0
        return sum(1 for r in d4_rows if r["stem"] == stem and r["candidate"] == w and r["passed"])
    dp = stem_pass_count("drums")
    bp = stem_pass_count("bass")
    drums_ok = dp >= 3
    bass_ok = bp >= 3
    n_ok = int(drums_ok) + int(bass_ok)
    if n_ok == 2:
        v = "RC10_DRUMS_BASS_LANDS"
    elif n_ok == 1:
        v = "RC10_DRUMS_BASS_PARTIAL"
    else:
        v = "RC10_DRUMS_BASS_FAILS"
    return {
        "verdict": v,
        "drums": {"winner": winners.get("drums", {}).get("candidate"), "songs_pass": dp, "ok": drums_ok},
        "bass": {"winner": winners.get("bass", {}).get("candidate"), "songs_pass": bp, "ok": bass_ok},
        "rubric_hash": RUBRIC_HASH.read_text().strip(),
        "rubric_doc": str(RUBRIC_DOC.relative_to(RUBRIC_DOC.parents[1])),
        "cycle": 54, "clone": "clone-0", "fork": "bdd7bb47f1b5",
        "run_id": "run-2026-08-28T040704Z",
    }


def _write_ab_pairs(rows, winners, songs):
    from scripts.recreate_v2.rc10_drums_bass._common import BASELINE_DIR
    d4_rows = {(r["song_id"], r["stem"], r["candidate"], r["d4"]): r for r in rows}
    for s in songs:
        sha16 = s["audio_sha16"]
        t0 = float(s["chosen_section"]["t_start_s"])
        t1 = float(s["chosen_section"]["t_end_s"])
        for stem in ("drums", "bass"):
            w = winners.get(stem, {}).get("candidate")
            if not w:
                continue
            wav = BASELINE_DIR / sha16 / "rc9_6stem" / f"{stem}.wav"
            if not wav.exists():
                continue
            y, sr = slice_and_load(wav, t0, t1)
            notes_path = IMPL_DIR / sha16 / stem / w / "d4on" / "notes.json"
            if not notes_path.exists():
                continue
            notes = json.loads(notes_path.read_text())
            out = AB_DIR / sha16 / stem / "iter_1"
            info = ren_mod.write_ab_pair(y, sr, notes, stem, out)
            write_json_canonical(out / "info.json", {"winner": w, "n_notes": len(notes), **info})


if __name__ == "__main__":
    t0 = time.time()
    v = score_all()
    print(json.dumps(v, indent=2))
    print(f"[done] {time.time() - t0:.1f}s", flush=True)
