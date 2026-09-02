#!/usr/bin/python3
# c53 clone-1 RC10 Branch B — orchestrator.
# NO PRNG. /usr/bin/python3 guard. c48 env flags default OFF.
"""End-to-end orchestrator for RC10 guitar+piano candidate matrix.

Reads `data/recreate_v2/focus_set_v2.json`; for each focus song, for each stem
in {guitar, piano}, for each candidate in {C1_default, C2_tuned, C3_chord_track},
for each D4-flavor in {without_d4, with_d4}:
  - transcribe/emit the MIDI (basic-pitch or chord-track)
  - score chroma_cosine + note_density_ratio against the ORIGINAL stem
  - append a scorecard row

Then select the winner per (song, stem) and emit A/B pairs. Finally,
emit the verdict.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Iterable

# Path so `from scripts.recreate_v2.rc10_guitar_piano._utils import *` works
# when invoked as a module OR as a script.
ROOT = Path("/home/user/long-exposure-runs/music-gen")
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.recreate_v2.rc10_guitar_piano import _utils as U  # noqa: E402
from scripts.recreate_v2.rc10_guitar_piano import basic_pitch_runner as BPR  # noqa: E402

import numpy as np  # noqa: E402
import pretty_midi  # noqa: E402

if sys.executable != "/usr/bin/python3":
    raise RuntimeError(f"run_all requires /usr/bin/python3 (got {sys.executable})")

FOCUS_SET_PATH = ROOT / "data/recreate_v2/focus_set_v2.json"
BASELINE_ROOT = ROOT / "data/recreate_v2/baseline"
RC5_ROOT = ROOT / "data/rc5_impl"
OUT_ROOT = ROOT / "data/rc10_impl/guitar_piano"
AB_ROOT = ROOT / "data/recreate_v2/ab_pairs"
RUBRIC_HASH_PATH = OUT_ROOT / "rubric_hash.txt"

STEMS = ("guitar", "piano")

# GM programs: guitar → 25 (Acoustic Guitar (steel)), piano → 0 (Acoustic Grand).
GM_PROGRAM = {"guitar": 25, "piano": 0}
FREQ_RANGE = {"guitar": (80.0, 1300.0), "piano": (27.5, 4186.0)}

CANDIDATES = ("C1_default", "C2_tuned", "C3_chord_track")

PASS_CHROMA = 0.60
PASS_DENSITY = (0.5, 2.0)


def load_focus_set() -> list[dict]:
    fs = json.loads(FOCUS_SET_PATH.read_text())
    return fs["songs"]


def baseline_stem(sha16: str, stem: str) -> Path:
    p = BASELINE_ROOT / sha16 / "rc9_6stem" / f"other_{stem}.wav"
    if not p.exists():
        # Fallback naming.
        alt = BASELINE_ROOT / sha16 / "rc9_6stem" / f"{stem}.wav"
        if alt.exists():
            return alt
    return p


def rc5_bpm(sha16: str) -> float:
    p = RC5_ROOT / sha16 / "rc5_tempo_estimate.json"
    j = json.loads(p.read_text())
    return float(j.get("corrected_estimate") or j.get("baseline_bpm") or 120.0)


def mixdown_section(sha16: str) -> tuple[np.ndarray, int]:
    """Load the summed 6-stem baseline mixdown of the (already-sliced) chosen section.

    Baseline stems under `data/recreate_v2/baseline/<sha16>/rc9_6stem/*.wav`
    are already 30s clips of the chosen section (per c50 D1); NO further
    slicing is required. This returns the summed mixdown at U.SR.
    """
    sr = U.SR
    stems = ("drums", "bass", "vocals", "other", "guitar", "piano")
    total = None
    for s in stems:
        p = BASELINE_ROOT / sha16 / "rc9_6stem" / f"{s}.wav"
        if not p.exists():
            p = BASELINE_ROOT / sha16 / "rc9_6stem" / f"other_{s}.wav"
        if not p.exists():
            continue
        sig = U.load_stem(p, sr=sr)
        if total is None:
            total = sig
        else:
            n = min(len(total), len(sig))
            total = total[:n] + sig[:n]
    if total is None:
        raise FileNotFoundError(f"no baseline stems for {sha16}")
    return total, sr


def resave_wav_to_tmp(wav_path: Path, tmp_dir: Path) -> Path:
    """Re-write a stem as mono @ U.SR under a temp path for basic-pitch input."""
    sig = U.load_stem(wav_path, sr=U.SR)
    out = tmp_dir / f"section_{wav_path.stem}.wav"
    U.write_wav(out, sig, U.SR)
    return out


def score_candidate(
    rendered_notes: list[dict],
    orig_stem_section: np.ndarray,
    sr: int,
    beat_times: np.ndarray,
    section_end_s: float,
    program: int,
) -> tuple[float, float, float]:
    """Return (chroma_cosine_mean, chroma_cosine_median, note_density_ratio)."""
    # Synthesize rendered notes to audio for chroma comparison.
    if rendered_notes:
        pm = U.pmidi_from_notes(rendered_notes, program=program)
    else:
        pm = pretty_midi.PrettyMIDI(initial_tempo=120.0)
        pm.instruments.append(pretty_midi.Instrument(program=program))
    rend_sig = U.render_notes_to_wav(pm, sr, section_end_s)
    n_want = min(len(orig_stem_section), len(rend_sig))
    orig_sec = orig_stem_section[:n_want]
    rend_sec = rend_sig[:n_want]

    orig_beat_ch = U.chroma_cqt_beat_sync(orig_sec, sr, beat_times)
    rend_beat_ch = U.chroma_cqt_beat_sync(rend_sec, sr, beat_times)
    cos_mean, cos_med = U.chroma_cosine_per_beat(orig_beat_ch, rend_beat_ch)
    density = U.note_density_ratio(
        rendered_notes, orig_sec, sr, n_beats=orig_beat_ch.shape[1]
    )
    return cos_mean, cos_med, density


def transcribe_candidate(
    candidate: str,
    stem_type: str,
    stem_section_wav: Path,
    beat_times: np.ndarray,
    orig_sec: np.ndarray,
    sr: int,
    section_end_s: float,
) -> list[dict]:
    """Return raw note events for the given candidate (before D4)."""
    if candidate == "C1_default":
        m, jpath = BPR.run("default", stem_section_wav)
        return json.loads(jpath.read_text())
    if candidate == "C2_tuned":
        preset = "tuned_guitar" if stem_type == "guitar" else "tuned_piano"
        m, jpath = BPR.run(preset, stem_section_wav)
        rows = json.loads(jpath.read_text())
        lo, hi = FREQ_RANGE[stem_type]
        # Post-transcription freq-window clip (from D3 defn).
        rows = [r for r in rows
                if lo <= (440.0 * (2.0 ** ((int(r["pitch"]) - 69) / 12.0))) <= hi]
        return rows
    if candidate == "C3_chord_track":
        # Beat-sync chroma of orig, template-match to triads, sustained on beat grid.
        chroma_beat = U.chroma_cqt_beat_sync(orig_sec, sr, beat_times)
        pm = U.chord_track_from_chroma(
            chroma_beat, beat_times, program=GM_PROGRAM[stem_type],
            section_end_s=section_end_s, octave=4 if stem_type == "guitar" else 4,
        )
        return U.midi_notes(pm)
    raise ValueError(candidate)


def process_song_stem(song: dict, stem_type: str, tmp_dir: Path) -> list[dict]:
    """Return the scorecard rows for one (song, stem)."""
    sha16 = song["audio_sha16"]
    bpm = rc5_bpm(sha16)
    stem_wav_path = baseline_stem(sha16, stem_type)
    if not stem_wav_path.exists():
        rows = []
        for cand in CANDIDATES:
            for d4 in ("without_d4", "with_d4"):
                rows.append({
                    "song_id": sha16, "stem": stem_type, "candidate": cand,
                    "chroma_cosine_mean": 0.0, "chroma_cosine_median": 0.0,
                    "note_density_ratio": 0.0, "post_processing": d4,
                    "pass_fail": "FAIL", "note_count": 0,
                    "notes": f"missing stem: {stem_wav_path}",
                })
        return rows

    # Baseline stems are already chosen-section clips (see c50 D1 note).
    orig_stem_sec = U.load_stem(stem_wav_path, sr=U.SR)
    section_end_s = len(orig_stem_sec) / float(U.SR)

    # Prepare a mono @ U.SR WAV for basic-pitch subprocess input.
    stem_section_wav = resave_wav_to_tmp(stem_wav_path, tmp_dir)

    # Reference mixdown + beat grid for the same 30s clip.
    mix_sec, sr = mixdown_section(sha16)
    tempo_est, beat_times = U.beat_grid(mix_sec, sr, start_bpm=bpm)
    # Beat times are relative to mix_sec start (t=0).

    rows: list[dict] = []
    per_stem_type_out_dir = OUT_ROOT / "per_song" / sha16 / stem_type
    per_stem_type_out_dir.mkdir(parents=True, exist_ok=True)

    for cand in CANDIDATES:
        raw_notes = transcribe_candidate(
            cand, stem_type, stem_section_wav, beat_times, orig_stem_sec,
            sr, section_end_s,
        )
        for d4 in ("without_d4", "with_d4"):
            if d4 == "with_d4":
                notes, diag = U.d4_postprocess(
                    raw_notes, sr, tempo_est, beat_times, orig_stem_sec,
                    freq_lo_hz=FREQ_RANGE[stem_type][0],
                    freq_hi_hz=FREQ_RANGE[stem_type][1],
                )
            else:
                notes = list(raw_notes)
                diag = {"n_in": len(raw_notes), "n_out": len(raw_notes)}

            cos_mean, cos_med, density = score_candidate(
                notes, orig_stem_sec, sr, beat_times, section_end_s,
                program=GM_PROGRAM[stem_type],
            )
            pf = (
                "PASS" if (cos_mean >= PASS_CHROMA
                           and PASS_DENSITY[0] <= density <= PASS_DENSITY[1])
                else "FAIL"
            )
            rows.append({
                "song_id": sha16, "stem": stem_type, "candidate": cand,
                "chroma_cosine_mean": round(cos_mean, 6),
                "chroma_cosine_median": round(cos_med, 6),
                "note_density_ratio": round(density, 6),
                "post_processing": d4, "pass_fail": pf,
                "note_count": len(notes),
                "tempo_est_bpm": round(float(tempo_est), 4),
                "n_beats": int(beat_times.size),
                "diag_d4": diag,
            })
            # Emit MIDI for this cell (deterministic filename).
            midi_out = (per_stem_type_out_dir /
                        f"{cand}__{d4}.midi")
            pm = U.pmidi_from_notes(notes, program=GM_PROGRAM[stem_type])
            pm.write(str(midi_out))
    return rows


def select_winner(rows: list[dict]) -> dict:
    """Per (song, stem) — winner selection honoring D5 + operator UPDATE #4.

    Precedence:
      1. Prefer PASS over FAIL (operator: 'correct chord track > wrong note soup').
      2. Within class, highest chroma_cosine_mean.
      3. Tiebreak: SHA-256(candidate|post_processing)[0], then with_d4 preferred,
         then candidate name lex.
    """
    by_key: dict[tuple[str, str], list[dict]] = {}
    for r in rows:
        by_key.setdefault((r["song_id"], r["stem"]), []).append(r)

    winners: dict[str, dict] = {}
    for (song_id, stem), rs in by_key.items():

        def sort_key(r):
            tag = f"{r['candidate']}|{r['post_processing']}"
            sha_first = hashlib.sha256(tag.encode("utf-8")).digest()[0]
            return (
                0 if r["pass_fail"] == "PASS" else 1,   # PASS first
                -float(r["chroma_cosine_mean"]),         # then max chroma
                sha_first,
                0 if r["post_processing"] == "with_d4" else 1,
                r["candidate"],
            )

        best = sorted(rs, key=sort_key)[0]
        winners[f"{song_id}|{stem}"] = best
    return winners


def emit_ab_pairs(winners: dict[str, dict], songs: list[dict]) -> list[dict]:
    """Emit LUFS-normalized original + rendered WAVs per (song, stem, iter_0)."""
    manifest = []
    songs_by_id = {s["audio_sha16"]: s for s in songs}
    for key, w in winners.items():
        song_id, stem = key.split("|", 1)
        song = songs_by_id[song_id]
        stem_wav_path = baseline_stem(song_id, stem)
        if not stem_wav_path.exists():
            continue
        orig_sec = U.load_stem(stem_wav_path, sr=U.SR)
        section_end_s = len(orig_sec) / float(U.SR)

        # Re-render the winner cell exactly as scored.
        per_stem_dir = OUT_ROOT / "per_song" / song_id / stem
        midi_p = per_stem_dir / f"{w['candidate']}__{w['post_processing']}.midi"
        pm = pretty_midi.PrettyMIDI(str(midi_p))
        rend_sig = U.render_notes_to_wav(pm, U.SR, section_end_s)

        # Loudness normalize both to -23 LUFS-I.
        orig_norm = U.loudness_normalize(orig_sec, U.SR, target_lufs=-23.0)
        rend_norm = U.loudness_normalize(rend_sig, U.SR, target_lufs=-23.0)

        ab_dir = AB_ROOT / song_id / stem / "iter_0"
        ab_dir.mkdir(parents=True, exist_ok=True)
        orig_out = ab_dir / "original.wav"
        rend_out = ab_dir / "rendered.wav"
        U.write_wav(orig_out, orig_norm, U.SR)
        U.write_wav(rend_out, rend_norm, U.SR)

        # Verify LUFS post-hoc.
        import pyloudnorm as pyln
        meter = pyln.Meter(U.SR)
        try:
            l_orig = float(meter.integrated_loudness(orig_norm))
        except Exception:
            l_orig = float("nan")
        try:
            l_rend = float(meter.integrated_loudness(rend_norm))
        except Exception:
            l_rend = float("nan")

        manifest.append({
            "song_id": song_id, "stem": stem,
            "iter": 0,
            "original_wav": str(orig_out.relative_to(ROOT)),
            "rendered_wav": str(rend_out.relative_to(ROOT)),
            "lufs_original": round(l_orig, 3),
            "lufs_rendered": round(l_rend, 3),
            "winner_candidate": w["candidate"],
            "winner_post_processing": w["post_processing"],
            "winner_chroma_cosine_mean": w["chroma_cosine_mean"],
        })
    return manifest


def write_scorecard_tsv(rows: list[dict], out_tsv: Path) -> None:
    cols = ["song_id", "stem", "candidate", "chroma_cosine_mean",
            "chroma_cosine_median", "note_density_ratio",
            "post_processing", "pass_fail", "note_count",
            "tempo_est_bpm", "n_beats"]
    lines = ["\t".join(cols)]
    # Deterministic order:
    for r in sorted(rows, key=lambda x: (x["song_id"], x["stem"],
                                          x["candidate"], x["post_processing"])):
        lines.append("\t".join(str(r.get(c, "")) for c in cols))
    out_tsv.write_text("\n".join(lines) + "\n")


def write_scorecard_md(rows: list[dict], out_md: Path) -> None:
    header = (
        "# RC10 Guitar+Piano Scorecard (c53 clone-1)\n\n"
        "| song | stem | candidate | post | chroma_μ | density | pass |\n"
        "|---|---|---|---|---|---|---|\n"
    )
    body_lines = []
    for r in sorted(rows, key=lambda x: (x["song_id"], x["stem"],
                                          x["candidate"], x["post_processing"])):
        body_lines.append(
            f"| {r['song_id']} | {r['stem']} | {r['candidate']} | "
            f"{r['post_processing']} | {r['chroma_cosine_mean']:.4f} | "
            f"{r['note_density_ratio']:.4f} | {r['pass_fail']} |"
        )
    out_md.write_text(header + "\n".join(body_lines) + "\n")


def compute_verdict(winners: dict[str, dict]) -> dict:
    """Winner-per-stem-type: candidate that wins on ≥3/5 focus songs; then
    verdict is per-stem PASS ⇔ ≥3/5 winner-cells pass D7 gate.
    """
    per_stem_wins: dict[str, dict[str, int]] = {"guitar": {}, "piano": {}}
    per_stem_pass: dict[str, int] = {"guitar": 0, "piano": 0}
    per_stem_total: dict[str, int] = {"guitar": 0, "piano": 0}
    for key, w in winners.items():
        _, stem = key.split("|", 1)
        per_stem_wins[stem][w["candidate"]] = per_stem_wins[stem].get(w["candidate"], 0) + 1
        per_stem_total[stem] += 1
        if w["pass_fail"] == "PASS":
            per_stem_pass[stem] += 1

    def pick_winner_type(counts: dict[str, int]) -> str:
        if not counts:
            return ""
        # ≥3/5 preferred; else tiebreak by SHA-256(candidate) first byte.
        for cand in CANDIDATES:
            if counts.get(cand, 0) >= 3:
                return cand
        return sorted(
            counts.keys(),
            key=lambda c: (-counts[c], hashlib.sha256(c.encode("utf-8")).digest()[0]),
        )[0]

    winner_guitar = pick_winner_type(per_stem_wins["guitar"])
    winner_piano = pick_winner_type(per_stem_wins["piano"])

    guitar_passes = per_stem_pass["guitar"] >= 3
    piano_passes = per_stem_pass["piano"] >= 3

    if guitar_passes and piano_passes:
        verdict = "RC10_GUITAR_PIANO_LANDS"
    elif guitar_passes or piano_passes:
        verdict = "RC10_GUITAR_PIANO_PARTIAL"
    else:
        verdict = "RC10_GUITAR_PIANO_FAILS"

    return {
        "verdict": verdict,
        "winner_per_stem_type": {"guitar": winner_guitar, "piano": winner_piano},
        "per_stem_pass_count": per_stem_pass,
        "per_stem_total": per_stem_total,
        "candidate_win_counts": per_stem_wins,
    }


def write_winner_per_stem_json(winners: dict[str, dict], verdict_summary: dict, out_path: Path) -> None:
    entries = []
    for key, w in sorted(winners.items()):
        song_id, stem = key.split("|", 1)
        entries.append({
            "song_id": song_id, "stem": stem,
            "candidate": w["candidate"],
            "post_processing": w["post_processing"],
            "chroma_cosine_mean": w["chroma_cosine_mean"],
            "note_density_ratio": w["note_density_ratio"],
            "pass_fail": w["pass_fail"],
        })
    payload = {
        "milestone": "M-RECREATE-2/accurate-small-set/rc10-transcription-real-stem-resurvey/guitar-piano",
        "clone": "clone-1",
        "cycle": 53,
        "per_song_winners": entries,
        "winner_per_stem_type": verdict_summary["winner_per_stem_type"],
        "tiebreak_method": "SHA-256(candidate_name.encode('utf-8'))[0]",
    }
    out_path.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n")


def snapshot_anchors() -> dict:
    """Snapshot ≥25 anchor SHAs."""
    anchors: dict[str, str] = {}
    # c49 v1 rubric + c50 v2 rubric + c51 A/B/C verdicts + c52 render_stem + others.
    for p in (
        ROOT / "docs/m_recreate_2_accurate_small_set_rubric.md",
        ROOT / "docs/m_recreate_2_accurate_small_set_rubric_v2.md",
        ROOT / "data/recreate_v2/rubric_hash.txt",
        ROOT / "data/recreate_v2/rubric_hash_v2.txt",
        ROOT / "data/rc1_rc9_impl/verdict.json",
        ROOT / "data/rc2_rc3_impl/verdict.json",
        ROOT / "data/recreate_v2/rc7_out/verdict.json",
        ROOT / "scripts/palette_render/render_stem.py",
        ROOT / "data/recreate_v2/focus_set_v2.json",
        ROOT / "data/recreate_v2/focus_set.json",
        ROOT / "data/recreate_v2/anchor_preservation.json",
        ROOT / "data/recreate_v2/anchor_preservation_v2.json",
        ROOT / "data/recreate_v2/baseline_byte_determinism.json",
    ):
        if p.exists():
            anchors[str(p.relative_to(ROOT))] = U.sha256_file(p)
    # 5 rc5 estimates.
    for sha_dir in sorted((ROOT / "data/rc5_impl").glob("*")):
        p = sha_dir / "rc5_tempo_estimate.json"
        if p.exists():
            anchors[str(p.relative_to(ROOT))] = U.sha256_file(p)
    # 10 baseline guitar+piano WAVs (5 songs × 2 stems).
    for sha_dir in sorted((ROOT / "data/recreate_v2/baseline").glob("*")):
        for stem in ("guitar", "piano"):
            for name in (f"other_{stem}.wav", f"{stem}.wav"):
                p = sha_dir / "rc9_6stem" / name
                if p.exists():
                    anchors[str(p.relative_to(ROOT))] = U.sha256_file(p)
                    break
    return anchors


def main(argv: list[str] | None = None) -> int:
    argp = argparse.ArgumentParser()
    argp.add_argument("--out-suffix", default="", help="suffix for scorecard/artifact dir (for byte-det runs)")
    argp.add_argument("--songs", type=int, default=None, help="limit songs (dev only)")
    argp.add_argument("--dry-run", action="store_true")
    args = argp.parse_args(argv)

    OUT_ROOT.mkdir(parents=True, exist_ok=True)

    songs = load_focus_set()
    if args.songs is not None:
        songs = songs[: args.songs]

    # Anchor snapshot pre-run.
    anchors_pre = snapshot_anchors()

    all_rows: list[dict] = []
    with tempfile.TemporaryDirectory(prefix="rc10_gp_") as tdir:
        tmp_dir = Path(tdir)
        for song in songs:
            for stem in STEMS:
                rows = process_song_stem(song, stem, tmp_dir)
                all_rows.extend(rows)

    winners = select_winner(all_rows)
    verdict_summary = compute_verdict(winners)
    ab_manifest = emit_ab_pairs(winners, songs)

    # Anchor snapshot post-run.
    anchors_post = snapshot_anchors()
    anchor_diff = {
        k: (anchors_pre.get(k), anchors_post.get(k))
        for k in set(anchors_pre) | set(anchors_post)
        if anchors_pre.get(k) != anchors_post.get(k)
    }

    scorecard_tsv = OUT_ROOT / f"scorecard{args.out_suffix}.tsv"
    write_scorecard_tsv(all_rows, scorecard_tsv)
    write_scorecard_md(all_rows, ROOT / "docs/rc10_guitar_piano_scorecard.md")

    winner_json = OUT_ROOT / f"winner_per_stem{args.out_suffix}.json"
    write_winner_per_stem_json(winners, verdict_summary, winner_json)

    ab_manifest_path = OUT_ROOT / f"ab_pairs_manifest{args.out_suffix}.json"
    ab_manifest_path.write_text(json.dumps(ab_manifest, sort_keys=True, indent=2) + "\n")

    anchor_snap_path = OUT_ROOT / f"anchor_preservation{args.out_suffix}.json"
    anchor_snap_path.write_text(json.dumps({
        "n_entries": len(anchors_pre),
        "diff_count": len(anchor_diff),
        "diff": anchor_diff,
        "pre": anchors_pre,
        "post": anchors_post,
    }, sort_keys=True, indent=2) + "\n")

    rubric_hash = RUBRIC_HASH_PATH.read_text().strip()
    verdict_payload = {
        "milestone": "M-RECREATE-2/accurate-small-set/rc10-transcription-real-stem-resurvey/guitar-piano",
        "clone": "clone-1",
        "cycle": 53,
        "rubric_hash": rubric_hash,
        "verdict": verdict_summary["verdict"],
        "per_stem_pass_count": verdict_summary["per_stem_pass_count"],
        "per_stem_total": verdict_summary["per_stem_total"],
        "winner_per_stem_type": verdict_summary["winner_per_stem_type"],
        "candidate_win_counts": verdict_summary["candidate_win_counts"],
        "n_focus_songs": len(songs),
        "n_scorecard_rows": len(all_rows),
        "n_ab_pairs": len(ab_manifest),
        "anchor_preservation": {
            "n_entries": len(anchors_pre),
            "n_mismatch": len(anchor_diff),
        },
        "env_pins": U.env_pins(),
    }
    verdict_path = OUT_ROOT / f"verdict{args.out_suffix}.json"
    verdict_path.write_text(json.dumps(verdict_payload, sort_keys=True, indent=2) + "\n")

    print(f"RC10 Branch B complete: verdict={verdict_summary['verdict']}")
    print(f"  scorecard: {scorecard_tsv}")
    print(f"  winner:    {winner_json}")
    print(f"  verdict:   {verdict_path}")
    print(f"  n_ab_pairs: {len(ab_manifest)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
