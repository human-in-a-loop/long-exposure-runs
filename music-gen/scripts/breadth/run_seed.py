#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-28T11:22:00Z
# cycle: 10
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-INGEST-1/breadth-second-seeds
# ---
"""Per-seed pipeline orchestrator for M-INGEST-1/breadth-second-seeds.

Stages (each wrapped in try/except and logged to stage_manifest.jsonl):
    1. chunker             (M-INGEST-1/chunker, demo output only)
    2. resample+upmix      (soxr HQ deterministic; force 44.1 kHz stereo)
    3. classifier          (M-CLASS-1 PANNs Cnn14 tagger on first chunk)
    4. htdemucs            (M-SEP-1/htdemucs-baseline on full seed)
    5. basic-pitch venv    (M-TRANS-1/basic-pitch on non-vocals stems)
    6. merge_stems_to_score (M-SCORE-1/bridge-api)
    7. render_bare_midi    (M-TEX-1/stage-by-stage fluidsynth path)
    8. texture panel       (M-TEX-1/panel on original vs bare_midi)

Determinism: torch.manual_seed(0), single-thread BLAS pins passed to
basic-pitch subprocess, scipy.io.wavfile writer for byte-stable WAVs.

Usage:
    PYTHONPATH=. /usr/bin/python3 scripts/breadth/run_seed.py \\
        --seed-id <id> --audio <path> --out-dir data/breadth/<id>
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
import traceback
from pathlib import Path
from typing import Any, Dict, Optional

assert sys.executable == '/usr/bin/python3', sys.executable

import numpy as np
import soundfile as sf
import scipy.io.wavfile as scipy_wav

ROOT = Path('/home/user/long-exposure-runs/music-gen')
VENV_PY = ROOT / 'workspace/basic_pitch_venv/bin/python3'
BP_CALL = ROOT / 'scripts/transcribe/_bp_call.py'
SF2 = Path('/usr/share/sounds/sf2/FluidR3_GM.sf2')
TARGET_SR = 44100

SCRIPT_VERSION = 'breadth/0.1.0'


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _write_wav_deterministic(path: Path, y: np.ndarray, sr: int) -> None:
    """Timestamp-free stable WAV via scipy.io.wavfile (matches
    scripts/tex/render_bare_midi.py convention)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    scipy_wav.write(str(path), sr, y.astype(np.float32))


def _log(manifest_path: Path, entry: Dict[str, Any]) -> None:
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    with manifest_path.open('a') as fh:
        fh.write(json.dumps(entry, sort_keys=True) + '\n')


# ---------------------------------------------------------------------------
# Stage functions — each returns dict with keys (name, ok, artifacts, notes).
# ---------------------------------------------------------------------------

def stage_chunker(audio_path: Path, out_dir: Path) -> Dict[str, Any]:
    """Demo the M-INGEST-1/chunker on the raw seed. Not used by later
    stages; kept for the M-INGEST-1 provenance chain."""
    from scripts.ingest.chunker import plan_clips
    from scripts.ingest.wavio import read_pcm16_mono, write_pcm16_mono

    # chunker only reads pcm16 mono — resample seeds are already that.
    try:
        y, sr = read_pcm16_mono(audio_path)
    except Exception:
        # Fall back to soundfile for float WAVs.
        y_sf, sr = sf.read(str(audio_path), always_2d=True)
        y = np.mean(y_sf, axis=1)
        y = np.clip(y, -1.0, 1.0)
    n_samples = len(y)
    clips_dir = out_dir / 'clips'
    clips_dir.mkdir(parents=True, exist_ok=True)
    plan = plan_clips(n_samples, sr)
    manifest_lines = []
    for c in plan:
        clip_wav = clips_dir / f'clip_{c.index:02d}.wav'
        clip_y = y[c.start_sample:c.end_sample].astype(np.float32)
        # write pcm16
        pcm = np.clip(clip_y * 32767, -32768, 32767).astype(np.int16)
        import wave
        with wave.open(str(clip_wav), 'wb') as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(sr)
            w.writeframes(pcm.tobytes())
        manifest_lines.append(dict(
            index=c.index, t_start=c.t_start_s, t_end=c.t_end_s,
            anchored_tail=c.anchored_tail, short_song=c.short_song,
            sha256=_sha(clip_wav),
        ))
    (out_dir / 'clips_manifest.jsonl').write_text(
        ''.join(json.dumps(m, sort_keys=True) + '\n' for m in manifest_lines)
    )
    return dict(
        name='chunker', ok=True, notes=f'{len(plan)} clips',
        artifacts=[str((clips_dir / f'clip_{c.index:02d}.wav').relative_to(ROOT))
                   for c in plan],
        chunk_count=len(plan),
    )


def stage_prepare_audio(audio_path: Path, out_dir: Path) -> Dict[str, Any]:
    """Resample to 44.1 kHz + upmix to stereo, deterministically, via soxr HQ.
    This is the 'original' signal used for the texture panel and htdemucs."""
    import librosa

    y_raw, sr_in = sf.read(str(audio_path), always_2d=True)
    # y_raw shape: (n_samples, n_channels)
    if y_raw.shape[1] == 1:
        y_mono = y_raw[:, 0]
    else:
        y_mono = np.mean(y_raw, axis=1)

    # Resample deterministically. librosa.resample uses soxr under the hood
    # when available; force 'soxr_hq' for reproducibility.
    if sr_in != TARGET_SR:
        y_mono = librosa.resample(
            y_mono.astype(np.float32), orig_sr=sr_in, target_sr=TARGET_SR,
            res_type='soxr_hq',
        )
    # Upmix: duplicate mono channel deterministically.
    if y_raw.shape[1] == 1:
        y_stereo = np.stack([y_mono, y_mono], axis=1)
        upmix_note = 'mono_duplicated_L_eq_R'
    elif y_raw.shape[1] == 2:
        # If original was stereo, resample per channel deterministically.
        if sr_in != TARGET_SR:
            L = librosa.resample(y_raw[:, 0].astype(np.float32), orig_sr=sr_in,
                                 target_sr=TARGET_SR, res_type='soxr_hq')
            R = librosa.resample(y_raw[:, 1].astype(np.float32), orig_sr=sr_in,
                                 target_sr=TARGET_SR, res_type='soxr_hq')
            y_stereo = np.stack([L, R], axis=1)
        else:
            y_stereo = y_raw.astype(np.float32)
        upmix_note = 'stereo_preserved'
    else:
        raise RuntimeError(f'unsupported channel count: {y_raw.shape[1]}')

    out_wav = out_dir / 'original.wav'
    _write_wav_deterministic(out_wav, y_stereo, TARGET_SR)
    peak = float(np.max(np.abs(y_stereo))) if y_stereo.size else 0.0
    return dict(
        name='prepare_audio', ok=True,
        notes=f'sr_in={sr_in} nch_in={y_raw.shape[1]} peak={peak:.4f} {upmix_note}',
        artifacts=[str(out_wav.relative_to(ROOT))],
        sr_in=sr_in, nch_in=int(y_raw.shape[1]),
        upmix_note=upmix_note, peak=peak,
        output_sha=_sha(out_wav),
    )


def stage_classifier(audio_path: Path, out_dir: Path) -> Dict[str, Any]:
    """Run PANNs Cnn14 tagger on the FIRST 30 s chunk (or full clip if
    short). Records dominant AudioSet class. Non-factor sidecar is
    intentionally NOT written from breadth (M-CLASS-1 owns sidecars)."""
    from scripts.classifier.tagger import Tagger
    from scripts.classifier import taxonomy as _tax  # noqa: F401

    y, sr = sf.read(str(audio_path), always_2d=True)
    y_mono = np.mean(y, axis=1).astype(np.float32) if y.ndim == 2 else y.astype(np.float32)
    # Truncate to first 30 s for the tag call.
    n_max = 30 * sr
    y_mono = y_mono[:n_max]

    tagger = Tagger()
    probs = tagger.tag(y_mono, sr=sr)
    top_idx = int(np.argmax(probs))
    top_prob = float(probs[top_idx])
    weights_sha = tagger.weights_sha256

    # Load AudioSet class map from panns_inference default location.
    try:
        # panns_inference ships labels; discover via package.
        from panns_inference.config import labels as audioset_labels
        dominant_label = audioset_labels[top_idx]
    except Exception:
        dominant_label = f'class_{top_idx}'

    out_json = out_dir / 'classification.json'
    payload = dict(
        dominant_class_index=top_idx,
        dominant_class_label=dominant_label,
        dominant_class_prob=top_prob,
        weights_sha256=weights_sha,
        model_id=tagger.model_id,
    )
    out_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + '\n')
    return dict(
        name='classifier', ok=True,
        notes=f'{dominant_label} p={top_prob:.3f}',
        artifacts=[str(out_json.relative_to(ROOT))],
        dominant_class=dominant_label,
        dominant_class_prob=top_prob,
    )


def stage_htdemucs(original_wav: Path, out_dir: Path) -> Dict[str, Any]:
    """Run htdemucs on the 44.1 kHz stereo prepared audio. Matches
    scripts/separation/run_htdemucs.py invocation verbatim."""
    import torch
    from demucs.apply import apply_model
    from demucs.pretrained import get_model

    torch.manual_seed(0)
    y, sr = sf.read(str(original_wav), always_2d=True)
    assert sr == TARGET_SR, sr
    # apply_model expects (batch, channels, samples).
    wav_t = torch.from_numpy(y.T.astype(np.float32)).unsqueeze(0)
    model = get_model('htdemucs')
    model.eval()
    with torch.no_grad():
        estimates = apply_model(
            model, wav_t, device='cpu',
            shifts=0, split=True, overlap=0.25, num_workers=0, progress=False,
        )
    stems_dir = out_dir / 'stems'
    stems_dir.mkdir(parents=True, exist_ok=True)
    estimates = estimates[0].numpy()  # (sources, channels, samples)
    stem_paths = {}
    shas = {}
    peaks = {}
    for i, name in enumerate(model.sources):
        stem_y = estimates[i].T  # (samples, channels)
        stem_path = stems_dir / f'{name}.wav'
        _write_wav_deterministic(stem_path, stem_y, sr)
        stem_paths[name] = stem_path
        shas[name] = _sha(stem_path)
        peaks[name] = float(np.max(np.abs(stem_y))) if stem_y.size else 0.0
    return dict(
        name='htdemucs', ok=True,
        notes=f'sources={list(model.sources)} peaks={ {k: round(v, 4) for k, v in peaks.items()} }',
        artifacts=[str(p.relative_to(ROOT)) for p in stem_paths.values()],
        stem_shas=shas, stem_peaks=peaks,
    )


def stage_basic_pitch(out_dir: Path, stems_to_transcribe=('drums', 'bass', 'other')) -> Dict[str, Any]:
    """Drive basic-pitch subprocess in quarantined venv for each named stem.
    Env pins passed via subprocess env (NOT os.environ mutation)."""
    stems_dir = out_dir / 'stems'
    trans_dir = out_dir / 'transcriptions'
    trans_dir.mkdir(parents=True, exist_ok=True)
    env = {**os.environ,
           'OMP_NUM_THREADS': '1',
           'MKL_NUM_THREADS': '1',
           'OPENBLAS_NUM_THREADS': '1',
           'TF_DETERMINISTIC_OPS': '1',
           'PYTHONHASHSEED': '0',
           'TF_CPP_MIN_LOG_LEVEL': '3'}
    results = {}
    for stem in stems_to_transcribe:
        wav = stems_dir / f'{stem}.wav'
        if not wav.exists():
            results[stem] = dict(ok=False, reason='stem_missing')
            continue
        # Check non-silence.
        y, sr = sf.read(str(wav), always_2d=True)
        peak = float(np.max(np.abs(y))) if y.size else 0.0
        if peak < 1e-4:
            results[stem] = dict(ok=False, reason=f'silent_stem_peak={peak:.6g}')
            continue
        out_midi = trans_dir / f'{stem}.mid'
        out_jsonl = trans_dir / f'{stem}.jsonl'
        try:
            subprocess.run(
                [str(VENV_PY), str(BP_CALL), str(wav), str(out_midi), str(out_jsonl)],
                check=True, env=env, capture_output=True, timeout=600,
            )
            n_notes = sum(1 for _ in out_jsonl.open())
            results[stem] = dict(
                ok=True, n_notes=n_notes,
                midi_sha=_sha(out_midi), jsonl_sha=_sha(out_jsonl),
            )
        except subprocess.CalledProcessError as e:
            results[stem] = dict(ok=False, reason='subprocess_error',
                                 stderr_tail=e.stderr.decode()[-500:] if e.stderr else '')
        except subprocess.TimeoutExpired:
            results[stem] = dict(ok=False, reason='timeout')
    n_ok = sum(1 for r in results.values() if r.get('ok'))
    return dict(
        name='basic_pitch', ok=n_ok > 0,
        notes=f'{n_ok}/{len(stems_to_transcribe)} stems transcribed',
        artifacts=[str((trans_dir / f'{s}.mid').relative_to(ROOT))
                   for s in stems_to_transcribe
                   if results.get(s, {}).get('ok')],
        per_stem=results,
    )


def stage_merge(out_dir: Path, stems=('drums', 'bass', 'other')) -> Dict[str, Any]:
    """Merge per-stem MIDIs into MusicXML via M-SCORE-1/bridge-api, then
    export back to MIDI."""
    from scripts.score.bridge import merge_stems_to_score, xml_to_midi, ScoreBridgeError

    trans_dir = out_dir / 'transcriptions'
    per_stem_midis = {}
    for s in stems:
        m = trans_dir / f'{s}.mid'
        if m.exists() and m.stat().st_size > 0:
            per_stem_midis[s] = m
    if not per_stem_midis:
        return dict(name='merge_stems_to_score', ok=False,
                    notes='no non-empty MIDIs to merge', artifacts=[])

    xml_out = out_dir / 'merged.musicxml'
    mid_out = out_dir / 'merged.mid'
    try:
        merge_stems_to_score(per_stem_midis, xml_out)
        xml_to_midi(xml_out, mid_out)
        return dict(
            name='merge_stems_to_score', ok=True,
            notes=f'merged {len(per_stem_midis)} stems',
            artifacts=[str(xml_out.relative_to(ROOT)), str(mid_out.relative_to(ROOT))],
            xml_sha=_sha(xml_out), midi_sha=_sha(mid_out),
        )
    except ScoreBridgeError as e:
        return dict(name='merge_stems_to_score', ok=False,
                    notes=f'ScoreBridgeError: {str(e)[:400]}', artifacts=[])
    except Exception as e:
        return dict(name='merge_stems_to_score', ok=False,
                    notes=f'{type(e).__name__}: {str(e)[:400]}', artifacts=[])


def stage_render_bare_midi(out_dir: Path, duration_s: float) -> Dict[str, Any]:
    """Fluidsynth render of merged.mid using pinned FluidR3_GM.sf2."""
    from scripts.tex.render_bare_midi import render_bare_midi

    midi_in = out_dir / 'merged.mid'
    if not midi_in.exists():
        return dict(name='render_bare_midi', ok=False,
                    notes='merged.mid missing', artifacts=[])
    wav_out = out_dir / 'bare_midi.wav'
    try:
        render_bare_midi(midi_in, wav_out, SF2, sr=TARGET_SR,
                         duration_s=duration_s)
        y, sr = sf.read(str(wav_out), always_2d=True)
        peak = float(np.max(np.abs(y))) if y.size else 0.0
        return dict(
            name='render_bare_midi', ok=True,
            notes=f'sr={sr} peak={peak:.4f} nframes={y.shape[0]}',
            artifacts=[str(wav_out.relative_to(ROOT))],
            wav_sha=_sha(wav_out), peak=peak,
        )
    except Exception as e:
        return dict(name='render_bare_midi', ok=False,
                    notes=f'{type(e).__name__}: {str(e)[:400]}', artifacts=[])


def stage_panel(out_dir: Path) -> Dict[str, Any]:
    """Texture panel on (original, bare_midi). Single ordered pair per
    the pipeline-breadth brief (24-number cross is M-TEX-1/stage-by-stage
    scope)."""
    from scripts.texture.panel import texture_distance

    a_path = out_dir / 'original.wav'
    b_path = out_dir / 'bare_midi.wav'
    if not (a_path.exists() and b_path.exists()):
        return dict(name='texture_panel', ok=False,
                    notes='missing input wav(s)', artifacts=[])
    a, sr_a = sf.read(str(a_path), always_2d=True)
    b, sr_b = sf.read(str(b_path), always_2d=True)
    assert sr_a == sr_b == TARGET_SR
    try:
        result = texture_distance(a, b, sr_a)
    except Exception as e:
        return dict(name='texture_panel', ok=False,
                    notes=f'{type(e).__name__}: {str(e)[:400]}', artifacts=[])

    panel_tsv = out_dir / 'panel.tsv'
    keys = ['mel_l1_db', 'spectral_centroid_rmse_hz', 'rms_env_rmse',
            'lufs_m_rmse_lu', 'embedding_cosine_distance', 'embedding_rung',
            'sr_hz', 'n_samples_compared']
    with panel_tsv.open('w') as fh:
        fh.write('a_stage\tb_stage\t' + '\t'.join(keys) + '\n')
        row_vals = []
        for k in keys:
            v = result.get(k)
            if v is None:
                row_vals.append('None')
            elif isinstance(v, float):
                row_vals.append(f'{v:.6g}')
            else:
                row_vals.append(str(v))
        fh.write('original\tbare_midi\t' + '\t'.join(row_vals) + '\n')

    return dict(
        name='texture_panel', ok=True,
        notes=f"rung={result.get('embedding_rung')}",
        artifacts=[str(panel_tsv.relative_to(ROOT))],
        panel=result, panel_tsv_sha=_sha(panel_tsv),
    )


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------

def run_seed(seed_id: str, audio_path: Path, out_dir: Path) -> Dict[str, Any]:
    audio_path = audio_path.resolve()
    out_dir = out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = out_dir / 'stage_manifest.jsonl'
    if manifest_path.exists():
        manifest_path.unlink()

    def _run_stage(name, fn, *args, **kwargs):
        t0 = time.monotonic()
        try:
            result = fn(*args, **kwargs)
        except Exception as e:
            result = dict(name=name, ok=False,
                          notes=f'{type(e).__name__}: {str(e)[:400]}',
                          traceback_tail=traceback.format_exc()[-800:],
                          artifacts=[])
        elapsed = time.monotonic() - t0
        result['elapsed_s'] = round(elapsed, 3)
        result['script_version'] = SCRIPT_VERSION
        _log(manifest_path, result)
        return result

    summary: Dict[str, Any] = dict(
        seed_id=seed_id, audio_path=str(audio_path.relative_to(ROOT)),
        audio_sha=_sha(audio_path),
    )
    chunker = _run_stage('chunker', stage_chunker, audio_path, out_dir)
    prep = _run_stage('prepare_audio', stage_prepare_audio, audio_path, out_dir)
    if not prep['ok']:
        return {**summary, 'stages': ['prepare_audio_failed']}
    original_wav = out_dir / 'original.wav'
    duration_s = sf.info(str(original_wav)).duration

    classifier = _run_stage('classifier', stage_classifier, original_wav, out_dir)
    htdemucs = _run_stage('htdemucs', stage_htdemucs, original_wav, out_dir)
    if htdemucs['ok']:
        bp = _run_stage('basic_pitch', stage_basic_pitch, out_dir)
    else:
        bp = dict(ok=False, notes='skipped due to htdemucs failure')
    if bp.get('ok'):
        merge = _run_stage('merge_stems_to_score', stage_merge, out_dir)
    else:
        merge = dict(ok=False, notes='skipped due to basic-pitch failure')
        _log(manifest_path, dict(name='merge_stems_to_score', **merge))
    if merge.get('ok'):
        render = _run_stage('render_bare_midi', stage_render_bare_midi, out_dir, duration_s)
    else:
        render = dict(ok=False, notes='skipped due to merge failure')
        _log(manifest_path, dict(name='render_bare_midi', **render))
    if render.get('ok'):
        panel = _run_stage('texture_panel', stage_panel, out_dir)
    else:
        panel = dict(ok=False, notes='skipped due to render failure')
        _log(manifest_path, dict(name='texture_panel', **panel))

    summary['stages'] = dict(
        chunker=chunker.get('ok', False),
        prepare_audio=prep.get('ok', False),
        classifier=classifier.get('ok', False),
        htdemucs=htdemucs.get('ok', False),
        basic_pitch=bp.get('ok', False),
        merge_stems_to_score=merge.get('ok', False),
        render_bare_midi=render.get('ok', False),
        texture_panel=panel.get('ok', False),
    )
    summary['all_ok'] = all(summary['stages'].values())
    (out_dir / 'summary.json').write_text(
        json.dumps(summary, indent=2, sort_keys=True) + '\n')
    return summary


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--seed-id', required=True)
    ap.add_argument('--audio', required=True, type=Path)
    ap.add_argument('--out-dir', required=True, type=Path)
    args = ap.parse_args()
    result = run_seed(args.seed_id, args.audio, args.out_dir)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
