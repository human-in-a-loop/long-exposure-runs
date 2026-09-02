#!/usr/bin/env python3
"""RC10 Branch C — Other-Residual + Vocals candidate-matrix runner (c53 clone-2).

Interpreter guard: this script uses the c33 quarantined-venv precedent —
librosa + basic_pitch + pretty_midi live in workspace/basic_pitch_venv, so
the entrypoint dispatches into that venv via subprocess when invoked from
/usr/bin/python3. It is also directly executable inside the venv itself.

Runs the D3 candidate matrix on all 5 focus songs, scores per D2, applies
D4 post-processing (with and without), picks per-stem-type winners per D5,
emits A/B pairs per D6, and writes verdict.json per D7 with three-way
rubric_hash byte-equality.

Env pins (byte-determinism × 2 gate):
    PYTHONHASHSEED=0 SOURCE_DATE_EPOCH=1756463424 TZ=UTC LC_ALL=C.UTF-8
    OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1

NO PRNG: all tie-breaks are SHA-256 based.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# Interpreter guard: either /usr/bin/python3 (thin dispatcher) or the
# quarantined venv (heavy worker). Any other python is rejected.
_ALLOWED = {
    "/usr/bin/python3",
    "/home/user/long-exposure-runs/music-gen/workspace/basic_pitch_venv/bin/python",
    "/home/user/long-exposure-runs/music-gen/workspace/basic_pitch_venv/bin/python3",
}

VENV_PY = "/home/user/long-exposure-runs/music-gen/workspace/basic_pitch_venv/bin/python"
WS = Path("/home/user/long-exposure-runs/music-gen")

# Env pins — applied to every subprocess and to the current process
ENV_PINS = {
    "PYTHONHASHSEED": "0",
    "SOURCE_DATE_EPOCH": "1756463424",
    "TZ": "UTC",
    "LC_ALL": "C.UTF-8",
    "OMP_NUM_THREADS": "1",
    "MKL_NUM_THREADS": "1",
    "OPENBLAS_NUM_THREADS": "1",
    "TF_CPP_MIN_LOG_LEVEL": "3",
}


def _pinned_env() -> dict:
    e = dict(os.environ)
    e.update(ENV_PINS)
    return e


def _sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _sha256_file(p: Path) -> str:
    return _sha256_bytes(p.read_bytes())


def _load_focus() -> list[dict]:
    return json.loads((WS / "data/recreate_v2/focus_set_v2.json").read_text())["songs"]


def _load_rc5_bpm(sha16: str) -> float:
    p = WS / f"data/rc5_impl/{sha16}/rc5_tempo_estimate.json"
    if p.exists():
        d = json.loads(p.read_text())
        return float(d.get("corrected_estimate") or d.get("baseline_bpm") or 120.0)
    return 120.0


def _extract_window(src_wav: Path, dst_wav: Path, t_start: float, t_end: float) -> None:
    """Extract [t_start, t_end] window with soundfile — deterministic PCM slice."""
    import soundfile as sf  # type: ignore
    import numpy as np

    y, sr = sf.read(str(src_wav), always_2d=False)
    i0 = int(round(t_start * sr))
    i1 = int(round(t_end * sr))
    if y.ndim == 2:
        y = np.mean(y, axis=1)  # mono mixdown for stem analysis
    y = y[i0:i1].astype(np.float32)
    sf.write(str(dst_wav), y, sr, subtype="PCM_16")


# ────────────────────────── candidates ──────────────────────────

_BP_MODEL = None


def _bp_predict(wav: Path, out_midi: Path, tuned: bool) -> None:
    """Run basic-pitch via its Python API (predict_and_save). Model loaded once."""
    global _BP_MODEL
    from basic_pitch.inference import predict_and_save  # type: ignore
    from basic_pitch import ICASSP_2022_MODEL_PATH  # type: ignore

    _WS_TMP = WS / "tmp" / "rc10_bp"
    _WS_TMP.mkdir(parents=True, exist_ok=True)
    tmpdir = tempfile.mkdtemp(prefix="rc10_bp_", dir=str(_WS_TMP))
    kwargs: dict = {
        "audio_path_list": [str(wav)],
        "output_directory": tmpdir,
        "save_midi": True,
        "sonify_midi": False,
        "save_model_outputs": False,
        "save_notes": False,
        "model_or_model_path": str(ICASSP_2022_MODEL_PATH),
    }
    if tuned:
        kwargs.update({
            "onset_threshold": 0.3,
            "frame_threshold": 0.3,
            "minimum_note_length": 100.0,
            "minimum_frequency": 80.0,
            "maximum_frequency": 1100.0,
        })
    predict_and_save(**kwargs)
    produced = list(Path(tmpdir).glob("*_basic_pitch.mid"))
    if not produced:
        raise RuntimeError(f"basic-pitch produced no MIDI for {wav}")
    shutil.copy(produced[0], out_midi)
    shutil.rmtree(tmpdir, ignore_errors=True)


def _pyin_notes(wav: Path, out_midi: Path) -> None:
    """v_c: pyin + voicing-confidence segmentation → note MIDI."""
    import librosa
    import numpy as np
    import pretty_midi

    y, sr = librosa.load(str(wav), sr=None, mono=True)
    f0, voiced_flag, _ = librosa.pyin(
        y,
        fmin=librosa.note_to_hz("C2"),
        fmax=librosa.note_to_hz("C7"),
        sr=sr,
        hop_length=512,
    )
    hop_s = 512 / sr
    min_run_frames = max(1, int(round(0.100 / hop_s)))  # 100 ms

    pm = pretty_midi.PrettyMIDI()
    inst = pretty_midi.Instrument(program=52)  # choir aahs GM 52 as lead-voice proxy
    voiced = np.nan_to_num(voiced_flag, nan=False).astype(bool)
    i = 0
    n = len(voiced)
    while i < n:
        if not voiced[i]:
            i += 1
            continue
        j = i
        while j < n and voiced[j]:
            j += 1
        if (j - i) >= min_run_frames:
            run_f0 = f0[i:j]
            run_f0 = run_f0[~np.isnan(run_f0)]
            if len(run_f0) > 0:
                med_hz = float(np.median(run_f0))
                if 80.0 <= med_hz <= 1100.0:
                    midi_num = int(round(librosa.hz_to_midi(med_hz)))
                    if 0 <= midi_num <= 127:
                        inst.notes.append(
                            pretty_midi.Note(
                                velocity=80,
                                pitch=midi_num,
                                start=i * hop_s,
                                end=j * hop_s,
                            )
                        )
        i = j
    pm.instruments.append(inst)
    pm.write(str(out_midi))


# 24 triad templates (12 major + 12 minor), key-order C..B
def _triad_templates():
    import numpy as np

    T = np.zeros((24, 12), dtype=np.float32)
    for root in range(12):
        # major
        T[root, root] = 1.0
        T[root, (root + 4) % 12] = 1.0
        T[root, (root + 7) % 12] = 1.0
        # minor
        T[12 + root, root] = 1.0
        T[12 + root, (root + 3) % 12] = 1.0
        T[12 + root, (root + 7) % 12] = 1.0
        T[root] /= np.linalg.norm(T[root]) + 1e-12
        T[12 + root] /= np.linalg.norm(T[12 + root]) + 1e-12
    return T


def _chroma_chord_track(wav: Path, out_midi: Path, bpm: float) -> None:
    """o_b: chroma_cqt argmax over 24 triads on beat grid, render as pretty_midi."""
    import librosa
    import numpy as np
    import pretty_midi

    y, sr = librosa.load(str(wav), sr=None, mono=True)
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr, hop_length=512)  # (12, T)
    # beat grid from bpm hint (deterministic)
    _, beats = librosa.beat.beat_track(y=y, sr=sr, hop_length=512, start_bpm=bpm, tightness=100)
    if len(beats) < 2:
        # Fall back to fixed beat grid at bpm hint
        n_frames = chroma.shape[1]
        frames_per_beat = max(1, int(round((60.0 / bpm) / (512 / sr))))
        beats = np.arange(0, n_frames, frames_per_beat)
    # Beat-synchronous chroma
    beat_chroma = librosa.util.sync(chroma, beats, aggregate=np.mean)  # (12, nb)
    T = _triad_templates()  # (24, 12)
    # normalize columns of beat_chroma
    bc_norm = beat_chroma / (np.linalg.norm(beat_chroma, axis=0, keepdims=True) + 1e-12)
    sims = T @ bc_norm  # (24, nb)
    winners = np.argmax(sims, axis=0)  # (nb,)
    beat_times = librosa.frames_to_time(beats, sr=sr, hop_length=512)

    pm = pretty_midi.PrettyMIDI()
    inst = pretty_midi.Instrument(program=0)  # GM 0 piano
    # Add one triad per beat, held for the beat duration
    total_dur = len(y) / sr
    for i, w in enumerate(winners):
        t0 = float(beat_times[i]) if i < len(beat_times) else i * (60.0 / bpm)
        t1 = float(beat_times[i + 1]) if i + 1 < len(beat_times) else min(t0 + 60.0 / bpm, total_dur)
        if t1 <= t0:
            continue
        is_minor = w >= 12
        root = int(w % 12)
        third = (root + (3 if is_minor else 4)) % 12
        fifth = (root + 7) % 12
        # Anchor to octave 4 (MIDI 60 = C4)
        base = 60
        for pc in (root, third, fifth):
            inst.notes.append(pretty_midi.Note(velocity=70, pitch=base + pc, start=t0, end=t1))
    pm.instruments.append(inst)
    pm.write(str(out_midi))


# ────────────────────────── post-processing (D4) ──────────────────────────

def _postprocess(in_midi: Path, out_midi: Path, wav_for_velocity: Path, bpm: float, stem_type: str) -> None:
    """Apply D4: beat-snap, min-duration drop, velocity from RMS, pitch range filter."""
    import librosa
    import numpy as np
    import pretty_midi
    import soundfile as sf

    pm = pretty_midi.PrettyMIDI(str(in_midi))
    y, sr = sf.read(str(wav_for_velocity), always_2d=False)
    if y.ndim == 2:
        y = np.mean(y, axis=1)
    # beat grid (frames → seconds)
    _, beats = librosa.beat.beat_track(y=y.astype(np.float32), sr=sr, hop_length=512,
                                        start_bpm=bpm, tightness=100)
    beat_times = librosa.frames_to_time(beats, sr=sr, hop_length=512)
    min_dur_s = 60.0 / (bpm * 8.0)  # 32nd note

    lo, hi = (80.0, 1100.0) if stem_type == "vocals" else (
        librosa.note_to_hz("C1"), librosa.note_to_hz("C7"))

    def snap(t: float) -> float:
        if len(beat_times) == 0:
            return t
        idx = int(np.argmin(np.abs(beat_times - t)))
        if abs(beat_times[idx] - t) <= 0.050:
            return float(beat_times[idx])
        return t

    def vel_at(t0: float, t1: float) -> int:
        i0 = int(round(t0 * sr))
        i1 = max(i0 + 1, int(round(t1 * sr)))
        seg = y[i0:i1]
        if len(seg) == 0:
            return 80
        rms = float(np.sqrt(np.mean(seg.astype(np.float64) ** 2))) if len(seg) else 0.0
        # map [-60..0] dBFS → [1..127]
        db = 20.0 * np.log10(max(1e-6, rms))
        v = int(round(np.clip((db + 60.0) / 60.0 * 126.0 + 1.0, 1, 127)))
        return v

    out = pretty_midi.PrettyMIDI()
    for inst in pm.instruments:
        new_inst = pretty_midi.Instrument(program=inst.program, is_drum=inst.is_drum)
        for note in inst.notes:
            hz = librosa.midi_to_hz(note.pitch)
            if hz < lo or hz > hi:
                continue
            t0 = snap(float(note.start))
            t1 = snap(float(note.end))
            if t1 - t0 < min_dur_s:
                continue
            v = vel_at(t0, t1)
            new_inst.notes.append(pretty_midi.Note(velocity=v, pitch=int(note.pitch),
                                                   start=t0, end=t1))
        out.instruments.append(new_inst)
    out.write(str(out_midi))


# ────────────────────────── scoring (D2) ──────────────────────────

def _pyin_track(wav: Path):
    import librosa
    import numpy as np

    y, sr = librosa.load(str(wav), sr=None, mono=True)
    f0, voiced_flag, _ = librosa.pyin(
        y, fmin=librosa.note_to_hz("C2"), fmax=librosa.note_to_hz("C7"),
        sr=sr, hop_length=512,
    )
    return f0, np.nan_to_num(voiced_flag, nan=False).astype(bool), sr


def _render_midi_wav(midi: Path, out_wav: Path, sr: int, duration_s: float) -> None:
    """Deterministic pretty_midi.synthesize (no external synth needed for f0 comparison)."""
    import numpy as np
    import pretty_midi
    import soundfile as sf

    pm = pretty_midi.PrettyMIDI(str(midi))
    # fs matches original sr for direct pyin comparison
    y = pm.synthesize(fs=sr).astype(np.float32)
    # pad/trim to expected duration
    n_target = int(round(duration_s * sr))
    if len(y) < n_target:
        y = np.pad(y, (0, n_target - len(y)))
    else:
        y = y[:n_target]
    sf.write(str(out_wav), y, sr, subtype="PCM_16")


def _score_vocals(baseline_wav: Path, cand_midi: Path, tmp: Path):
    import numpy as np

    f0_b, v_b, sr_b = _pyin_track(baseline_wav)
    rendered = tmp / "vocals_render.wav"
    dur = len(f0_b) * 512 / sr_b
    _render_midi_wav(cand_midi, rendered, sr_b, dur)
    f0_r, v_r, sr_r = _pyin_track(rendered)
    n = min(len(f0_b), len(f0_r))
    f0_b, v_b, f0_r, v_r = f0_b[:n], v_b[:n], f0_r[:n], v_r[:n]
    both = v_b & v_r
    denom = int(both.sum())
    if denom == 0:
        f0_agreement_pct = 0.0
    else:
        with np.errstate(invalid="ignore"):
            semis = 12.0 * np.log2(np.nan_to_num(f0_r[both], nan=1.0) /
                                    np.nan_to_num(f0_b[both], nan=1.0))
        within = int(np.sum(np.abs(semis) <= 1.0))
        f0_agreement_pct = 100.0 * within / denom
    voiced_b = int(v_b.sum())
    voiced_r = int(v_r.sum())
    coverage_ratio = (voiced_r / voiced_b) if voiced_b > 0 else 0.0
    passes = (f0_agreement_pct >= 60.0) and (0.5 <= coverage_ratio <= 2.0)
    return {
        "f0_agreement_pct": round(f0_agreement_pct, 4),
        "voiced_time_coverage_ratio": round(coverage_ratio, 4),
        "voiced_frames_baseline": voiced_b,
        "voiced_frames_rendered": voiced_r,
        "frames_voiced_both": denom,
        "pass": bool(passes),
    }


def _score_other(baseline_wav: Path, cand_midi: Path, bpm: float):
    """Score other-residual candidate by chroma cosine + density ratio.

    Per rubric §D4 deviation note: chroma is computed on the templated MIDI's
    implied pitch-class multiset rather than a fluidsynth re-render. Densities
    computed from note events / seconds.
    """
    import librosa
    import numpy as np
    import pretty_midi
    import soundfile as sf

    y, sr = sf.read(str(baseline_wav), always_2d=False)
    if y.ndim == 2:
        y = np.mean(y, axis=1)
    y = y.astype(np.float32)
    chroma_orig = librosa.feature.chroma_cqt(y=y, sr=sr, hop_length=512)
    _, beats = librosa.beat.beat_track(y=y, sr=sr, hop_length=512, start_bpm=bpm, tightness=100)
    if len(beats) < 2:
        n_frames = chroma_orig.shape[1]
        frames_per_beat = max(1, int(round((60.0 / bpm) / (512 / sr))))
        beats = np.arange(0, n_frames, frames_per_beat)
    beat_orig = librosa.util.sync(chroma_orig, beats, aggregate=np.mean)
    beat_times = librosa.frames_to_time(beats, sr=sr, hop_length=512)

    # Build beat-synchronous chroma from candidate MIDI's active pitch classes
    pm = pretty_midi.PrettyMIDI(str(cand_midi))
    nb = beat_orig.shape[1]
    beat_cand = np.zeros((12, nb), dtype=np.float32)
    for inst in pm.instruments:
        if inst.is_drum:
            continue
        for note in inst.notes:
            pc = int(note.pitch % 12)
            for i in range(nb):
                t0 = float(beat_times[i]) if i < len(beat_times) else 0.0
                t1 = float(beat_times[i + 1]) if i + 1 < len(beat_times) else t0 + 60.0 / bpm
                overlap = max(0.0, min(note.end, t1) - max(note.start, t0))
                if overlap > 0:
                    beat_cand[pc, i] += float(overlap)
    # normalize per beat column
    bo_n = beat_orig / (np.linalg.norm(beat_orig, axis=0, keepdims=True) + 1e-12)
    bc_n = beat_cand / (np.linalg.norm(beat_cand, axis=0, keepdims=True) + 1e-12)
    cos = float(np.mean(np.sum(bo_n * bc_n, axis=0)))

    # density ratio: rendered notes/s vs basic-pitch-on-original reference density
    dur_s = len(y) / sr
    n_notes = sum(len(inst.notes) for inst in pm.instruments)
    density_rendered = n_notes / max(1e-6, dur_s)

    # baseline density from basic-pitch on original stem (light sidecar, only if
    # a reference density file is present — otherwise use candidate against itself)
    passes_cos = cos >= 0.55
    passes_dens = 0.5 <= 1.0 <= 2.0  # will be recomputed at aggregation using per-song ref
    return {
        "mean_chroma_cosine": round(cos, 4),
        "density_rendered_per_s": round(density_rendered, 4),
        "n_notes_rendered": int(n_notes),
        "duration_s": round(float(dur_s), 4),
        "chroma_pass_gate": bool(passes_cos),
    }


# ────────────────────────── A/B pairs (D6) ──────────────────────────

def _rms_dbfs_normalize(y, target_dbfs=-23.0):
    import numpy as np

    rms = float(np.sqrt(np.mean(y.astype(np.float64) ** 2)) + 1e-12)
    cur_db = 20.0 * np.log10(rms + 1e-12)
    gain_db = target_dbfs - cur_db
    gain = 10 ** (gain_db / 20.0)
    y2 = np.clip(y * gain, -0.999, 0.999).astype(np.float32)
    return y2


def _write_ab_pair(baseline_wav: Path, cand_midi: Path, ab_dir: Path) -> None:
    import numpy as np
    import soundfile as sf

    ab_dir.mkdir(parents=True, exist_ok=True)
    # original
    y, sr = sf.read(str(baseline_wav), always_2d=False)
    if y.ndim == 2:
        y = np.mean(y, axis=1)
    y = _rms_dbfs_normalize(y.astype(np.float32))
    sf.write(str(ab_dir / "original.wav"), y, sr, subtype="PCM_16")
    # rendered
    _WS_AB_TMP = WS / "tmp" / "rc10_ab"
    _WS_AB_TMP.mkdir(parents=True, exist_ok=True)
    tmp = tempfile.mkdtemp(prefix="rc10_ab_", dir=str(_WS_AB_TMP))
    try:
        rendered = Path(tmp) / "r.wav"
        _render_midi_wav(cand_midi, rendered, sr, len(y) / sr)
        yr, _ = sf.read(str(rendered), always_2d=False)
        yr = _rms_dbfs_normalize(yr.astype(np.float32))
        sf.write(str(ab_dir / "rendered.wav"), yr, sr, subtype="PCM_16")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ────────────────────────── main pipeline ──────────────────────────

def _process_song(song: dict, out_root: Path, ab_root: Path) -> dict:
    sha16 = song["audio_sha16"]
    section = song["chosen_section"]
    t0, t1 = float(section["t_start_s"]), float(section["t_end_s"])
    bpm = _load_rc5_bpm(sha16)

    base_dir = WS / f"data/recreate_v2/baseline/{sha16}/rc9_6stem"
    vocals_full = base_dir / "vocals.wav"
    other_full = base_dir / "other.wav"

    work = out_root / sha16
    work.mkdir(parents=True, exist_ok=True)

    # Baseline stems on disk are 30s captures at t=0..30 (c49 baseline convention),
    # not the D1 chosen_section window. When chosen_section extends beyond stem
    # duration, we score against the full baseline stem — the same honest-negative
    # convention Branch A used for Chicken Grease (RC1 coverage 27.81%).
    import soundfile as _sf
    stem_dur = _sf.info(str(vocals_full)).duration
    section_dur = t1 - t0
    vocals_win = work / "vocals_window.wav"
    other_win = work / "other_window.wav"
    if t1 <= stem_dur + 0.01:
        _extract_window(vocals_full, vocals_win, t0, t1)
        _extract_window(other_full, other_win, t0, t1)
        section_source = "chosen_section"
    else:
        # Fall back to full baseline stem (mono mixdown copy)
        _extract_window(vocals_full, vocals_win, 0.0, stem_dur)
        _extract_window(other_full, other_win, 0.0, stem_dur)
        section_source = f"baseline_full_0..{stem_dur:.2f}s (chosen_section {t0:.1f}..{t1:.1f}s out of range)"

    # ── VOCALS candidates
    voc_results = {}
    for cid, fn in (
        ("v_a", lambda o: _bp_predict(vocals_win, o, tuned=False)),
        ("v_b", lambda o: _bp_predict(vocals_win, o, tuned=True)),
        ("v_c", lambda o: _pyin_notes(vocals_win, o)),
    ):
        raw = work / f"vocals_{cid}_raw.mid"
        try:
            fn(raw)
        except Exception as ex:  # noqa: BLE001
            voc_results[cid] = {"error": str(ex)[:200]}
            continue
        pp = work / f"vocals_{cid}_pp.mid"
        _postprocess(raw, pp, vocals_win, bpm, "vocals")
        score_raw = _score_vocals(vocals_win, raw, work)
        score_pp = _score_vocals(vocals_win, pp, work)
        voc_results[cid] = {"raw": score_raw, "pp": score_pp}
        # A/B pair — for both raw and pp (D6: "for every iteration + winner")
        for tag, midi in (("raw", raw), ("pp", pp)):
            _write_ab_pair(vocals_win, midi,
                           ab_root / sha16 / "vocals" / f"iter_{cid}_{tag}")

    # ── OTHER-RESIDUAL candidates
    other_results = {}
    for cid, fn in (
        ("o_a", lambda o: _bp_predict(other_win, o, tuned=False)),
        ("o_b", lambda o: _chroma_chord_track(other_win, o, bpm)),
    ):
        raw = work / f"other_{cid}_raw.mid"
        try:
            fn(raw)
        except Exception as ex:  # noqa: BLE001
            other_results[cid] = {"error": str(ex)[:200]}
            continue
        pp = work / f"other_{cid}_pp.mid"
        _postprocess(raw, pp, other_win, bpm, "other")
        score_raw = _score_other(other_win, raw, bpm)
        score_pp = _score_other(other_win, pp, bpm)
        other_results[cid] = {"raw": score_raw, "pp": score_pp}
        for tag, midi in (("raw", raw), ("pp", pp)):
            _write_ab_pair(other_win, midi,
                           ab_root / sha16 / "other_residual" / f"iter_{cid}_{tag}")

    # baseline density reference for density_ratio computation (D2)
    baseline_dens = other_results.get("o_a", {}).get("raw", {}).get("density_rendered_per_s")
    if baseline_dens is None:
        baseline_dens = other_results.get("o_b", {}).get("raw", {}).get("density_rendered_per_s")

    # augment other_results with density_ratio + pass gate
    for cid, res in other_results.items():
        if "error" in res:
            continue
        for tag in ("raw", "pp"):
            d = res[tag]
            dr = (d["density_rendered_per_s"] / baseline_dens) if baseline_dens else 0.0
            d["density_ratio_vs_baseline"] = round(dr, 4)
            d["pass"] = bool(d["chroma_pass_gate"] and 0.5 <= dr <= 2.0)

    return {
        "song_id": sha16,
        "bpm_hint": bpm,
        "window_s": [t0, t1],
        "section_source": section_source,
        "vocals": voc_results,
        "other_residual": other_results,
    }


def _select_winner(per_song: list[dict], stem_key: str, metric_key: str) -> dict:
    """§D5 winner: candidate that PASSes on ≥3/5 songs with highest mean metric.
    Prefer post-processed variant; SHA-256 tiebreak on candidate name."""
    # collect per-candidate scores
    cand_ids = sorted({cid for song in per_song for cid in song[stem_key].keys()})
    scored = []
    for cid in cand_ids:
        for tag in ("pp", "raw"):
            passes = 0
            metrics = []
            for song in per_song:
                r = song[stem_key].get(cid, {})
                if "error" in r or tag not in r:
                    continue
                if r[tag].get("pass"):
                    passes += 1
                metrics.append(r[tag].get(metric_key, 0.0))
            mean_metric = sum(metrics) / len(metrics) if metrics else 0.0
            scored.append({
                "candidate": cid,
                "postprocessed": tag == "pp",
                "songs_passed": passes,
                "mean_metric": round(mean_metric, 4),
                "tiebreak_sha": hashlib.sha256(f"{cid}|{tag}".encode()).hexdigest(),
            })
    # sort: songs_passed desc, mean_metric desc, tiebreak_sha asc
    scored.sort(key=lambda s: (-s["songs_passed"], -s["mean_metric"], s["tiebreak_sha"]))
    return scored[0] if scored else {}


def main() -> int:
    if sys.executable not in _ALLOWED:
        print(f"REJECTED interpreter: {sys.executable} (allowed: {_ALLOWED})", file=sys.stderr)
        return 2

    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", required=True, help="Root work dir for this run")
    ap.add_argument("--ab-dir", required=True, help="Root A/B pairs dir")
    ap.add_argument("--verdict-out", required=True, help="Output verdict.json path")
    args = ap.parse_args()

    out_root = Path(args.out_dir)
    ab_root = Path(args.ab_dir)
    out_root.mkdir(parents=True, exist_ok=True)
    ab_root.mkdir(parents=True, exist_ok=True)

    # dispatch to venv if not already there
    if sys.executable == "/usr/bin/python3":
        cmd = [VENV_PY, __file__, "--out-dir", str(out_root),
               "--ab-dir", str(ab_root), "--verdict-out", args.verdict_out]
        r = subprocess.run(cmd, env=_pinned_env())
        return r.returncode

    songs = _load_focus()
    per_song = [_process_song(s, out_root, ab_root) for s in songs]

    winner_v = _select_winner(per_song, "vocals", "f0_agreement_pct")
    winner_o = _select_winner(per_song, "other_residual", "mean_chroma_cosine")

    voc_pass_count = winner_v.get("songs_passed", 0) if winner_v else 0
    oth_pass_count = winner_o.get("songs_passed", 0) if winner_o else 0
    voc_ok = voc_pass_count >= 3
    oth_ok = oth_pass_count >= 3
    if voc_ok and oth_ok:
        verdict = "RC10_OTHER_VOCALS_LANDS"
    elif voc_ok or oth_ok:
        verdict = "RC10_OTHER_VOCALS_PARTIAL"
    else:
        verdict = "RC10_OTHER_VOCALS_FAILS"

    rubric_sha = (WS / "data/rc10_impl/other_vocals/rubric_hash.txt").read_text().strip()

    # winner_per_stem_type.json
    winners_path = WS / "data/rc10_impl/other_vocals/winner_per_stem_type.json"
    winners_path.write_text(json.dumps({
        "vocals": winner_v,
        "other_residual": winner_o,
    }, indent=2, sort_keys=True) + "\n")

    verdict_doc = {
        "verdict": verdict,
        "rubric_hash": rubric_sha,
        "milestone": "M-RECREATE-2/accurate-small-set/rc10-transcription-real-stem-resurvey",
        "vocals_winner": winner_v,
        "other_residual_winner": winner_o,
        "vocals_pass_count": voc_pass_count,
        "other_residual_pass_count": oth_pass_count,
        "per_song": per_song,
        "focus_set_v2_sha256": _sha256_file(WS / "data/recreate_v2/focus_set_v2.json"),
        "d2_gates": {
            "vocals": {"f0_agreement_pct_min": 60.0, "coverage_ratio_range": [0.5, 2.0]},
            "other_residual": {"mean_chroma_cosine_min": 0.55, "density_ratio_range": [0.5, 2.0]},
        },
        "notes": [
            "LUFS-I -23 approximated by RMS-dBFS -23 (pyloudnorm unavailable in venv).",
            "o_b chroma cosine computed on templated MIDI pitch-class implication (see rubric deviation).",
        ],
    }
    Path(args.verdict_out).write_text(json.dumps(verdict_doc, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"verdict": verdict, "voc_pass": voc_pass_count,
                      "oth_pass": oth_pass_count}, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
