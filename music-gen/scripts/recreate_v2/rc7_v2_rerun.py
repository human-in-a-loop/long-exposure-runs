#!/usr/bin/python3
# c53 Branch A: RC7-v2 re-run using c51 A+B substantive MIDIs.
# Pre-registration: docs/rc7_v2_rerun_rubric.md (mtime hard).
# Milestone: M-RECREATE-2/accurate-small-set/rc7-mix-balance-match
# NO PRNG. /usr/bin/python3 guard.
"""RC7-v2 re-run.

Replaces c51 Branch C's c33-anchor placeholder MIDIs with the c51
Branch A+B substantive per-stem MIDIs:

  * vocals, guitar, piano, other  <- data/rc1_rc9_impl/per_song/<sha16>/merged_partial.midi
  * drums, bass                   <- data/rc2_rc3_impl/<sha16>/merged.midi

Per focus song, split the merged MIDIs into per-instrument single-track
MIDIs, bare-render each via fluidsynth (imported READ-ONLY from
render_stem.py), fit a 12-band iirpeak EQ curve vs the original 6-stem
baseline spectrum, apply EQ + RMS loudness match, sum, and emit a
4-stem A7 verdict over {drums, bass, other_guitar, other_piano}.

Byte-determinism x 2 via two fresh tempfile.mkdtemp() runs (env pins).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
from pathlib import Path

# c48 env-var flag flips remain default OFF.
os.environ.setdefault("MUSICGEN_LEDGER_SUBSTANTIVE_EXEMPTION", "0")
os.environ.setdefault("MUSICGEN_LEDGER_SUPERSEDES_IN_HASH", "0")
# Single-thread BLAS for byte-determinism.
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")
# Reproducibility pins (rubric).
os.environ.setdefault("PYTHONHASHSEED", "0")
os.environ.setdefault("SOURCE_DATE_EPOCH", "1756463424")
os.environ.setdefault("TZ", "UTC")
os.environ.setdefault("LC_ALL", "C.UTF-8")

if sys.executable != "/usr/bin/python3":
    raise RuntimeError(f"RC7-v2 requires /usr/bin/python3 (got {sys.executable})")

import numpy as np  # noqa: E402
import scipy.io.wavfile as scipy_wav  # noqa: E402
import pretty_midi  # noqa: E402

# Ensure workspace root on sys.path for scripts.* imports.
_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

# READ-ONLY imports from render_stem.py (SHA
# 214372d920a319a97d6e3fc7b9ee4134c08c0cb4aecb776f4a50c75f965b5b2b).
from scripts.palette_render.render_stem import (  # noqa: E402
    render_fluidsynth,
    _apply_eq_curve_iirpeak,
    _apply_loudness_target,
    _canonicalize_wav_deterministic,
    SAMPLE_RATE,
    SAMPLE_COUNT,
)

# READ-ONLY imports from rc7_mix_balance.py (c51 Branch C, no edits).
from scripts.recreate_v2.rc7_mix_balance import (  # noqa: E402
    _sha256_file,
    _read_wav_float,
    _rms_db,
    _fit_eq_curve_from_original,
    _apply_old_chain_baseline,
)

RC_ID = "M-RECREATE-2/accurate-small-set/rc7-mix-balance-match"
ACCEPTANCE_CRITERIA = (
    "per-stem RMS <= 3 dB vs baseline over 4 stems "
    "{drums,bass,other_guitar,other_piano}; LUFS-S report-only"
)
FOCUS_SET_V2 = _REPO / "data" / "recreate_v2" / "focus_set_v2.json"
BASELINE_DIR = _REPO / "data" / "recreate_v2" / "baseline"
RC7_OUT_V2_DIR = _REPO / "data" / "recreate_v2" / "rc7_out_v2"
RC7_OUT_ANCHOR_DIR = _REPO / "data" / "recreate_v2" / "rc7_out"
BRANCH_A_MIDI_ROOT = _REPO / "data" / "rc1_rc9_impl" / "per_song"
BRANCH_B_MIDI_ROOT = _REPO / "data" / "rc2_rc3_impl"

RUBRIC_DOC = _REPO / "docs" / "rc7_v2_rerun_rubric.md"

# All six stems are rendered for reproduction completeness; only the
# 4-stem set is gated in the A7 verdict (D5).
A7_GATE_STEMS = ["drums", "bass", "other_guitar", "other_piano"]
ALL_STEMS = ["drums", "bass", "other_guitar", "other_piano", "vocals", "other"]

# Every stem is rendered via fluidsynth_gm for c53 (VST3 lock respected;
# c11 CLAP anti-pattern respected -- no external fetch).
STEM_INSTRUMENT = {s: "fluidsynth_gm" for s in ALL_STEMS}


def _rubric_doc_sha() -> str:
    return hashlib.sha256(RUBRIC_DOC.read_bytes()).hexdigest()


def _split_merged_midis(sha16: str, out_dir: Path) -> dict:
    """Split Branch A + Branch B merged MIDIs into per-instrument
    single-track MIDIs. Returns a dict mapping stem-name -> Path.

    Branch A (merged_partial.midi): instruments named 'vocals','guitar',
    'piano','other'. The 'guitar' and 'piano' tracks become 'other_guitar'
    and 'other_piano' in our A7 4-stem gate. The residual 'other' and
    'vocals' tracks are rendered too but not gated.

    Branch B (merged.midi): 'Drums' (is_drum=True) and 'Electric Bass'
    (program 33). These become 'drums' and 'bass'.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    stems: dict = {}

    branch_a = BRANCH_A_MIDI_ROOT / sha16 / "merged_partial.midi"
    branch_b = BRANCH_B_MIDI_ROOT / sha16 / "merged.midi"
    if not branch_a.is_file():
        raise RuntimeError(f"Branch A MIDI missing: {branch_a}")
    if not branch_b.is_file():
        raise RuntimeError(f"Branch B MIDI missing: {branch_b}")

    pm_a = pretty_midi.PrettyMIDI(str(branch_a))
    pm_b = pretty_midi.PrettyMIDI(str(branch_b))

    # Branch A -> vocals, guitar (=other_guitar), piano (=other_piano), other
    name_to_stem_a = {
        "vocals": "vocals",
        "guitar": "other_guitar",
        "piano": "other_piano",
        "other": "other",
    }
    for inst in pm_a.instruments:
        target = name_to_stem_a.get(inst.name)
        if target is None:
            continue
        pm_single = pretty_midi.PrettyMIDI()
        # Force a clean, single-instrument MIDI.
        new_inst = pretty_midi.Instrument(
            program=int(inst.program),
            is_drum=bool(inst.is_drum),
            name=target,
        )
        # Deep-copy notes without mutation.
        for n in inst.notes:
            new_inst.notes.append(pretty_midi.Note(
                velocity=int(n.velocity), pitch=int(n.pitch),
                start=float(n.start), end=float(n.end),
            ))
        pm_single.instruments.append(new_inst)
        p = out_dir / f"{target}.mid"
        pm_single.write(str(p))
        stems[target] = p

    # Branch B -> drums, bass.
    for inst in pm_b.instruments:
        if inst.is_drum:
            target = "drums"
        elif int(inst.program) == 33:
            target = "bass"
        else:
            continue
        pm_single = pretty_midi.PrettyMIDI()
        new_inst = pretty_midi.Instrument(
            program=int(inst.program),
            is_drum=bool(inst.is_drum),
            name=target,
        )
        for n in inst.notes:
            new_inst.notes.append(pretty_midi.Note(
                velocity=int(n.velocity), pitch=int(n.pitch),
                start=float(n.start), end=float(n.end),
            ))
        pm_single.instruments.append(new_inst)
        p = out_dir / f"{target}.mid"
        pm_single.write(str(p))
        stems[target] = p

    for req in ["drums", "bass", "other_guitar", "other_piano"]:
        if req not in stems:
            raise RuntimeError(f"required stem {req!r} not present in split MIDIs for {sha16}")
    return stems


def _render_bare_from_midi(midi_path: Path, out_dir: Path) -> Path:
    """Bare-render a substantive per-instrument MIDI via fluidsynth
    (READ-ONLY helper import). Renders twice for determinism-cross-check
    and returns run1 path."""
    out_dir.mkdir(parents=True, exist_ok=True)
    out1 = out_dir / "render_run1.wav"
    out2 = out_dir / "render_run2.wav"
    render_fluidsynth(midi_path, out1, parameter_dict=None)
    render_fluidsynth(midi_path, out2, parameter_dict=None)
    sha1 = _sha256_file(out1)
    sha2 = _sha256_file(out2)
    (out_dir / "render_run1.wav.sha").write_text(sha1 + "\n")
    (out_dir / "render_run2.wav.sha").write_text(sha2 + "\n")
    if sha1 != sha2:
        raise RuntimeError(f"bare render non-deterministic: {out_dir}")
    return out1


def _apply_eq_and_loudness(bare_wav: Path, eq_curve: dict,
                            loudness_target: dict, out_wav: Path) -> float:
    """Apply the 12-band iirpeak EQ chain and the RMS loudness match
    to a rendered WAV; returns the final measured RMS in dB."""
    _, y = scipy_wav.read(str(bare_wav))
    if y.dtype == np.int16:
        y = y.astype(np.float32) / 32768.0
    elif y.dtype == np.int32:
        y = y.astype(np.float32) / 2147483648.0
    else:
        y = y.astype(np.float32)
    centers = eq_curve["band_center_freqs_hz"]
    gains = eq_curve["band_gains_db"]
    if len(centers) != 12 or len(gains) != 12:
        raise RuntimeError("eq_curve must carry exactly 12 bands")
    if y.ndim == 1:
        proc = _apply_eq_curve_iirpeak(y, centers, gains)
        y_eq = proc.astype(np.float32)
    else:
        ch_l = _apply_eq_curve_iirpeak(y[:, 0], centers, gains)
        ch_r = _apply_eq_curve_iirpeak(y[:, 1], centers, gains)
        y_eq = np.stack([ch_l, ch_r], axis=1).astype(np.float32)
    tgt = float(loudness_target["target_rms_db"])
    max_g = float(loudness_target.get("max_gain_db", 24.0))
    y_out, measured_after = _apply_loudness_target(y_eq, tgt, max_gain_db=max_g)
    _canonicalize_wav_deterministic(y_out, out_wav)
    return float(measured_after)


def _rel_to_song(song_out: Path, p: Path) -> str:
    """Path relative to the per-song output dir; keeps dispatch_summary.json
    byte-stable across fresh tempdirs (byte-determinism x 2)."""
    try:
        return str(Path(p).resolve().relative_to(Path(song_out).resolve()))
    except ValueError:
        return str(p)


def _process_song(sha16: str, orig_stems_dir: Path, out_dir: Path) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    per_stem_summary: dict = {}
    matched_wavs = []

    split_dir = out_dir / "split_midis"
    stem_midis = _split_merged_midis(sha16, split_dir)

    # Baseline 6-stem original mapping: our 'other_guitar' and 'other_piano'
    # match originals named 'guitar' and 'piano'; other 4 match by name.
    stem_to_orig_name = {
        "drums": "drums", "bass": "bass",
        "other_guitar": "guitar", "other_piano": "piano",
        "vocals": "vocals", "other": "other",
    }

    for stem in ALL_STEMS:
        orig_name = stem_to_orig_name[stem]
        orig_wav = orig_stems_dir / f"{orig_name}.wav"
        if not orig_wav.is_file():
            per_stem_summary[stem] = {"error": f"original stem missing: {orig_wav}"}
            continue
        _, y_orig = _read_wav_float(orig_wav)
        target_rms_db = _rms_db(y_orig)

        bare_dir = out_dir / f"bare_{stem}"
        bare_wav = _render_bare_from_midi(stem_midis[stem], bare_dir)

        eq_curve = _fit_eq_curve_from_original(orig_wav, bare_wav)

        matched_dir = out_dir / f"matched_{stem}"
        matched_dir.mkdir(parents=True, exist_ok=True)
        matched_wav = matched_dir / "matched.wav"
        loudness_target = {
            "target_rms_db": float(target_rms_db),
            "reference_sha256": _sha256_file(orig_wav),
            "max_gain_db": 48.0,
        }
        measured_after = _apply_eq_and_loudness(
            bare_wav, eq_curve, loudness_target, matched_wav)

        old_chain_dir = out_dir / f"old_chain_{stem}"
        old_chain_dir.mkdir(parents=True, exist_ok=True)
        old_chain_wav = old_chain_dir / "old_chain.wav"
        _apply_old_chain_baseline(bare_wav, old_chain_wav)

        _, y_matched = _read_wav_float(matched_wav)
        measured_rms_db_final = _rms_db(y_matched)
        error_db = float(abs(measured_rms_db_final - target_rms_db))

        per_stem_summary[stem] = {
            "instrument": STEM_INSTRUMENT[stem],
            "orig_wav": str(orig_wav.relative_to(_REPO)),
            "orig_sha256": _sha256_file(orig_wav),
            "target_rms_db": float(target_rms_db),
            "measured_rms_db_post_match": float(measured_rms_db_final),
            "loudness_error_rms_db": error_db,
            "a7_rms_pass": bool(error_db <= 3.0),
            "in_a7_gate": stem in A7_GATE_STEMS,
            "bare_wav": _rel_to_song(out_dir, bare_wav),
            "bare_sha256": _sha256_file(bare_wav),
            "matched_wav": _rel_to_song(out_dir, matched_wav),
            "matched_sha256": _sha256_file(matched_wav),
            "old_chain_wav": _rel_to_song(out_dir, old_chain_wav),
            "old_chain_sha256": _sha256_file(old_chain_wav),
            "eq_bands_gains_db": eq_curve["band_gains_db"],
            "midi_src": _rel_to_song(out_dir, stem_midis[stem]),
            "midi_src_sha256": _sha256_file(stem_midis[stem]),
        }
        matched_wavs.append(matched_wav)

    # Sum all matched stems (6 stems) into the reconstruction.
    mix_out = out_dir / "rc7_v2_mixed_reconstruction.wav"
    if matched_wavs:
        sr, y0 = _read_wav_float(matched_wavs[0])
        mix = np.zeros_like(y0)
        for w in matched_wavs:
            _, y = _read_wav_float(w)
            L = min(len(mix), len(y))
            mix[:L] += y[:L]
        peak = float(np.max(np.abs(mix)))
        if peak > 0.999:
            mix = mix * (0.999 / peak)
        mix = mix.astype(np.float32)
        scipy_wav.write(str(mix_out), sr, mix)
    mix_sha = _sha256_file(mix_out) if mix_out.exists() else None

    dispatch = {
        "song_id": sha16,
        "cycle": 53,
        "branch": "A",
        "clone": "clone-0",
        "milestone_id": RC_ID,
        "rubric_sha256": _rubric_doc_sha(),
        "eq_curve_method": "iirpeak_12band_log_spaced_Q1.4",
        "eq_fallback_used": False,
        "d4_old_chain_preserved_as_baseline_only": True,
        "per_stem": per_stem_summary,
        "rc7_v2_mixed_reconstruction_sha256": mix_sha,
        "notes": (
            "c51 A+B substantive MIDIs consumed as bare MIDI-per-stem source. "
            "vocals+other rendered for reproduction completeness; A7 gate over "
            "{drums,bass,other_guitar,other_piano} per rubric D5."
        ),
    }
    (out_dir / "dispatch_summary.json").write_text(
        json.dumps(dispatch, sort_keys=True, indent=2) + "\n")

    # panel_baseline_old_chain_v2.tsv (D4 diagnostic).
    tsv_lines = [
        "stem\ttarget_rms_db\tmatched_rms_db\told_chain_rms_db\tmatched_error_db\told_chain_error_db\tin_a7_gate"
    ]
    for stem in ALL_STEMS:
        s = per_stem_summary.get(stem, {})
        if not s or "error" in s:
            continue
        _, y_old = _read_wav_float(out_dir / s["old_chain_wav"])
        old_rms = _rms_db(y_old)
        old_err = float(abs(old_rms - s["target_rms_db"]))
        tsv_lines.append(
            f"{stem}\t{s['target_rms_db']:.6f}\t{s['measured_rms_db_post_match']:.6f}\t"
            f"{old_rms:.6f}\t{s['loudness_error_rms_db']:.6f}\t{old_err:.6f}\t"
            f"{'1' if s['in_a7_gate'] else '0'}"
        )
    (out_dir / "panel_baseline_old_chain_v2.tsv").write_text("\n".join(tsv_lines) + "\n")

    return dispatch


def _emit_verdict(all_song_results: list, out_dir: Path) -> dict:
    per_song_passes = []
    n_stem_accepts = 0
    n_stem_total = 0
    for r in all_song_results:
        stems_in_gate = [
            r["per_stem"][s] for s in A7_GATE_STEMS
            if s in r["per_stem"] and "error" not in r["per_stem"][s]
        ]
        n_stem_total += len(stems_in_gate)
        stem_ok_flags = [bool(s.get("a7_rms_pass")) for s in stems_in_gate]
        n_stem_accepts += sum(stem_ok_flags)
        song_pass = len(stems_in_gate) == len(A7_GATE_STEMS) and all(stem_ok_flags)
        per_song_passes.append({
            "song_id": r["song_id"],
            "song_pass": song_pass,
            "per_stem_pass_count": sum(stem_ok_flags),
            "per_stem_total": len(A7_GATE_STEMS),
        })
    n_pass = sum(1 for p in per_song_passes if p["song_pass"])
    if n_pass >= 3:
        verdict = "RC7_v2_LANDS"
    elif n_pass >= 1 or n_stem_accepts >= 15:
        verdict = "RC7_v2_PARTIAL"
    else:
        verdict = "RC7_v2_FAILS"
    verdict_obj = {
        "milestone_id": RC_ID,
        "cycle": 53,
        "branch": "A",
        "clone": "clone-0",
        "supersedes_verdict": "data/recreate_v2/rc7_out/verdict.json",
        "verdict": verdict,
        "n_songs_passing_a7": n_pass,
        "n_songs_total": len(per_song_passes),
        "n_stem_accepts": n_stem_accepts,
        "n_stem_total": n_stem_total,
        "per_song_passes": per_song_passes,
        "rubric_hash": _rubric_doc_sha(),
        "acceptance_criterion": ACCEPTANCE_CRITERIA,
        "eq_curve_method": "iirpeak_12band_log_spaced_Q1.4",
        "d4_old_chain_baseline_present": True,
    }
    (out_dir / "verdict.json").write_text(
        json.dumps(verdict_obj, sort_keys=True, indent=2) + "\n")
    return verdict_obj


def run(focus_set_v2_path: Path | None = None, out_dir: Path | None = None,
        limit: int | None = None) -> dict:
    if focus_set_v2_path is None:
        focus_set_v2_path = FOCUS_SET_V2
    if out_dir is None:
        out_dir = RC7_OUT_V2_DIR
    out_dir.mkdir(parents=True, exist_ok=True)

    focus = json.loads(focus_set_v2_path.read_text())
    songs = focus.get("songs", [])
    if limit is not None:
        songs = songs[:limit]

    all_results = []
    for song in songs:
        sha16 = song.get("audio_sha16") or song.get("song_id")
        orig_stems_dir = BASELINE_DIR / sha16 / "rc9_6stem"
        if not orig_stems_dir.is_dir():
            print(f"  [skip] {sha16}: rc9_6stem/ missing", file=sys.stderr)
            continue
        song_out = out_dir / sha16
        song_out.mkdir(parents=True, exist_ok=True)
        print(f"  [process] {sha16}", file=sys.stderr)
        res = _process_song(sha16, orig_stems_dir, song_out)
        all_results.append(res)

    return _emit_verdict(all_results, out_dir)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--focus-set", type=Path, default=FOCUS_SET_V2)
    ap.add_argument("--out-dir", type=Path, default=RC7_OUT_V2_DIR)
    ap.add_argument("--limit", type=int, default=None)
    a = ap.parse_args()
    verdict = run(focus_set_v2_path=a.focus_set, out_dir=a.out_dir, limit=a.limit)
    print(json.dumps(verdict, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
