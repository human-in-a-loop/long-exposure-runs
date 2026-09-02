#!/usr/bin/env /usr/bin/python3
# RC10 bass v2 orchestrator: per-song v2 transcription + D6 metrics + D7 verdict +
# A/B pair emission + regression vs c54 v1 + three-way rubric_hash + byte-det × 2.
# created: 2026-09-02, cycle 55, run-2026-08-28T040704Z, worker, fork 7cc01d726807 clone-1
import csv
import json
import hashlib
import sys
from pathlib import Path

import soundfile as sf

from ._common import (
    load_focus_songs, BASELINE_DIR, IMPL_DIR, AB_DIR, RUBRIC_HASH,
    RUBRIC_DOC, V1_SCORECARD, WS, sha256_of, slice_and_load, write_json_canonical,
)
from .bass_v2 import transcribe_bass_v2, onset_reference
from .metrics_v2 import (
    onset_f1, note_count_ratio, velocity_std, low_band_correlation, bass_v2_gate,
)
from .render_v2 import write_ab_pair_v2


MANDATORY_SONGS = {"31a164f845f8e27e", "252eb21ce7df7328"}  # Chicken Grease + What If I Go


def per_song_process(song, out_dir=None, ab_root=None):
    sha16 = song["audio_sha16"]
    bass_wav = BASELINE_DIR / sha16 / "rc9_6stem" / "bass.wav"
    if not bass_wav.exists():
        raise FileNotFoundError(f"missing baseline bass stem: {bass_wav}")
    cs = song.get("chosen_section") or {}
    y, sr = slice_and_load(bass_wav, cs.get("t_start_s", 0.0), cs.get("t_end_s", 30.0))
    ref_onsets = onset_reference(y, sr)
    notes = transcribe_bass_v2(y, sr)

    # D6 metrics — compare v2 predictions to baseline onset reference on the same stem.
    pred_onsets = [n["onset_s"] for n in notes]
    f1, tp, fp, fn = onset_f1(pred_onsets, ref_onsets, tol_s=0.050)
    cr = note_count_ratio(notes, ref_onsets)
    vstd = velocity_std(notes)
    # low-band correlation of predicted note "envelope" vs baseline: reuse c54's
    # low-band correlation on the original bass stem vs itself would be 1.0; the
    # meaningful comparison is envelope-of-notes-as-signal vs envelope-of-baseline.
    # We synthesize a mono note-envelope from note (onset, duration, velocity) via
    # a simple exponential-decay pulse train, then compare its low-band correlation
    # against baseline. This preserves the c54 metric definition semantics.
    y_pred_env = _synth_note_envelope(notes, sr, dur_s=len(y) / sr)
    low_corr = low_band_correlation(y, y_pred_env, sr, cutoff=250.0)

    gate = bass_v2_gate(f1, cr, vstd, low_corr)
    art_counts = _articulation_counts(notes)

    per_song = {
        "song_id": sha16,
        "n_ref_onsets": len(ref_onsets),
        "n_pred_notes": len(notes),
        "onset_f1": float(f1),
        "tp": int(tp), "fp": int(fp), "fn": int(fn),
        "count_ratio": float(cr),
        "velocity_std": float(vstd),
        "low_band_corr": float(low_corr),
        "articulation": art_counts,
        "gate": gate,
        "notes_sha256": hashlib.sha256(
            json.dumps(notes, sort_keys=True).encode("utf-8")
        ).hexdigest(),
    }

    if out_dir is not None:
        song_dir = Path(out_dir) / sha16
        song_dir.mkdir(parents=True, exist_ok=True)
        write_json_canonical(song_dir / "notes.json", notes)
        write_json_canonical(song_dir / "per_song.json", per_song)
    if ab_root is not None:
        ab_dir = Path(ab_root) / sha16 / "bass" / "iter_1"
        ab_meta = write_ab_pair_v2(y, sr, notes, ab_dir)
        per_song["ab_meta"] = ab_meta
    return per_song


def _synth_note_envelope(notes, sr, dur_s):
    """Build a note-driven envelope signal for low-band correlation.

    Per note: exponential decay pulse from onset over duration_s with amplitude
    proportional to velocity. Purely deterministic (numpy only, no PRNG)."""
    import numpy as np
    n_samples = int(round(dur_s * sr))
    if n_samples <= 0:
        return np.zeros(1, dtype=np.float32)
    y = np.zeros(n_samples, dtype=np.float32)
    for n in notes:
        s = int(round(float(n["onset_s"]) * sr))
        e = min(n_samples, s + int(round(float(n["duration_s"]) * sr)))
        if e <= s:
            continue
        amp = float(n["velocity"]) / 127.0
        t = np.arange(e - s, dtype=np.float32) / sr
        env = amp * np.exp(-3.0 * t)
        y[s:e] += env
    return y


def _articulation_counts(notes):
    c = {"slap": 0, "ghost": 0, "sustained": 0}
    for n in notes:
        a = n.get("articulation", "sustained")
        c[a] = c.get(a, 0) + 1
    return c


def load_v1_pyin_mono_scores():
    """Read c54 v1 scorecard for pyin_mono bass rows (d4=0) — regression baseline.

    Returns {sha16: {'n_notes': int, 'f0_agree': float, 'low_corr': float}}.
    NOTE: c54 scorecard did NOT record onset_f1 for pyin_mono (that column is
    empty), so v1 onset F1 is recomputed post-hoc on the same baseline using
    the SAME reference (librosa.onset.onset_detect) so v1/v2 F1 are comparable.
    """
    if not V1_SCORECARD.exists():
        return {}
    v1 = {}
    with V1_SCORECARD.open() as f:
        rdr = csv.DictReader(f, delimiter="\t")
        for r in rdr:
            if r.get("stem") != "bass" or r.get("candidate") != "pyin_mono":
                continue
            if r.get("d4") != "0":
                continue
            v1[r["song_id"]] = {
                "n_notes": int(r["n_notes"]),
                "count_ratio_v1": float(r["count_ratio"]),
                "framewise_f0_agreement": float(r["framewise_f0_agreement"]),
                "low_band_corr_v1": float(r["low_band_corr"]),
                "passed_v1": bool(int(r["passed"])),
            }
    return v1


def compute_v1_recomputed_onset_f1(songs):
    """For regression comparison, recompute v1 onset F1 by running the c54
    pyin_mono transcribe on the same baseline and F1-ing against the SAME
    onset reference used for v2 (librosa.onset_detect on the baseline stem)."""
    from scripts.recreate_v2.rc10_drums_bass.bass import transcribe_pyin
    v1r = {}
    for song in songs:
        sha16 = song["audio_sha16"]
        bass_wav = BASELINE_DIR / sha16 / "rc9_6stem" / "bass.wav"
        cs = song.get("chosen_section") or {}
        y, sr = slice_and_load(bass_wav, cs.get("t_start_s", 0.0), cs.get("t_end_s", 30.0))
        ref = onset_reference(y, sr)
        v1_notes = transcribe_pyin(y, sr)
        v1_onsets = [n["onset_s"] for n in v1_notes]
        f1, _, _, _ = onset_f1(v1_onsets, ref, tol_s=0.050)
        v1r[sha16] = float(f1)
    return v1r


def decide_verdict(per_song_rows, regression_ok, mandatory_pass):
    passed = [r for r in per_song_rows if r["gate"]["all_pass"]]
    three_of_four_with_m1 = [
        r for r in per_song_rows
        if r["gate"]["num_pass"] >= 3 and r["gate"]["m1_onset_f1_ge_060"]
    ]
    if not mandatory_pass:
        return "RC10_BASS_V2_FAILS", "mandatory (Chicken Grease + What If I Go) failed"
    if not regression_ok:
        # caps at PARTIAL per §D7 regression contract
        if len(passed) >= 2:
            return "RC10_BASS_V2_PARTIAL", "onset F1 regressed >0.05 on ≥1 song; capped at PARTIAL"
        return "RC10_BASS_V2_FAILS", "onset F1 regression + insufficient pass count"
    if len(passed) >= 3:
        return "RC10_BASS_V2_LANDS", f"{len(passed)}/5 songs pass all 4 metrics"
    if len(passed) == 2 or len(three_of_four_with_m1) >= 3:
        return "RC10_BASS_V2_PARTIAL", f"{len(passed)}/5 all-4; {len(three_of_four_with_m1)}/5 3-of-4 with m1"
    return "RC10_BASS_V2_FAILS", f"{len(passed)}/5 all-4; {len(three_of_four_with_m1)}/5 3-of-4 with m1"


def write_scorecard_tsv(rows, path):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    header = [
        "song_id", "n_ref_onsets", "n_pred_notes", "onset_f1",
        "count_ratio", "velocity_std", "low_band_corr",
        "art_slap", "art_ghost", "art_sustained",
        "m1", "m2", "m3", "m4", "num_pass", "all_pass", "notes_sha256",
    ]
    with Path(path).open("w") as f:
        f.write("\t".join(header) + "\n")
        for r in rows:
            g = r["gate"]; ac = r["articulation"]
            f.write("\t".join([
                r["song_id"], str(r["n_ref_onsets"]), str(r["n_pred_notes"]),
                f"{r['onset_f1']:.6f}", f"{r['count_ratio']:.6f}",
                f"{r['velocity_std']:.6f}", f"{r['low_band_corr']:.6f}",
                str(ac.get("slap", 0)), str(ac.get("ghost", 0)), str(ac.get("sustained", 0)),
                str(int(g["m1_onset_f1_ge_060"])), str(int(g["m2_count_ratio_070_150"])),
                str(int(g["m3_vel_std_ge_10"])), str(int(g["m4_low_corr_ge_05"])),
                str(g["num_pass"]), str(int(g["all_pass"])), r["notes_sha256"],
            ]) + "\n")


def run(out_dir=None, ab_root=None, emit_ab=True):
    songs = load_focus_songs()
    out_dir = Path(out_dir) if out_dir else IMPL_DIR
    ab_root = Path(ab_root) if ab_root else AB_DIR
    out_dir.mkdir(parents=True, exist_ok=True)

    rows = []
    for song in songs:
        rows.append(per_song_process(song, out_dir=out_dir, ab_root=ab_root if emit_ab else None))

    # Regression vs c54 v1
    v1_meta = load_v1_pyin_mono_scores()
    v1_onset_f1_recomputed = compute_v1_recomputed_onset_f1(songs)
    reg_rows = []
    reg_ok = True
    for r in rows:
        sha = r["song_id"]
        v1_f1 = v1_onset_f1_recomputed.get(sha, None)
        v2_f1 = r["onset_f1"]
        delta = None if v1_f1 is None else (v2_f1 - v1_f1)
        regressed = bool(delta is not None and delta < -0.05)
        if regressed:
            reg_ok = False
        reg_rows.append({
            "song_id": sha,
            "v1_onset_f1_recomputed": v1_f1,
            "v2_onset_f1": v2_f1,
            "delta": delta,
            "regressed_gt_005": regressed,
            "v1_scorecard": v1_meta.get(sha, {}),
        })

    mandatory_pass = all(
        (r["gate"]["all_pass"] or r["gate"]["m1_onset_f1_ge_060"])
        for r in rows if r["song_id"] in MANDATORY_SONGS
    )
    verdict, reason = decide_verdict(rows, reg_ok, mandatory_pass)

    rubric_sha_from_file = Path(RUBRIC_HASH).read_text().strip()
    rubric_sha_from_doc = sha256_of(RUBRIC_DOC)
    if rubric_sha_from_file != rubric_sha_from_doc:
        raise RuntimeError(f"rubric_hash drift: file={rubric_sha_from_file} doc={rubric_sha_from_doc}")

    write_scorecard_tsv(rows, out_dir / "scorecard.tsv")
    write_json_canonical(out_dir / "regression_vs_v1.json", {
        "reference": "librosa.onset.onset_detect(delta=0.02, backtrack=True) on baseline bass stem",
        "note": "v1 onset F1 recomputed post-hoc so v1/v2 use the same reference; c54 scorecard did not emit onset F1 for pyin_mono bass rows.",
        "rows": reg_rows,
        "regression_ok_no_song_below_minus_005": bool(reg_ok),
    })
    verdict_payload = {
        "verdict": verdict,
        "reason": reason,
        "n_pass_all4": sum(1 for r in rows if r["gate"]["all_pass"]),
        "n_pass_3of4_with_m1": sum(
            1 for r in rows
            if r["gate"]["num_pass"] >= 3 and r["gate"]["m1_onset_f1_ge_060"]
        ),
        "mandatory_pass": bool(mandatory_pass),
        "regression_ok": bool(reg_ok),
        "rubric_hash": rubric_sha_from_file,
        "songs": [
            {
                "song_id": r["song_id"],
                "gate": r["gate"],
                "articulation": r["articulation"],
                "onset_f1": r["onset_f1"],
                "count_ratio": r["count_ratio"],
                "velocity_std": r["velocity_std"],
                "low_band_corr": r["low_band_corr"],
            }
            for r in rows
        ],
    }
    write_json_canonical(out_dir / "verdict.json", verdict_payload)
    return verdict_payload


if __name__ == "__main__":
    v = run()
    print(json.dumps({"verdict": v["verdict"], "reason": v["reason"]}))
