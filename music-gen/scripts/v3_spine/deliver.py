#!/usr/bin/env /usr/bin/python3
"""Emit operator delivery artifacts under data/v3/deliveries/<sha16>/.

- original_ab.wav: 30s excerpt from Chicken Grease original mp3, t=0..30s
- reconstruction_ab.wav: 30s excerpt from full_reconstruction.wav
- full_reconstruction.wav: copy of the full-length mix
- manifest.json: per-artifact SHAs + chosen-section metadata + rubric hash chain
"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import scipy.io.wavfile as sw

SONG_SHA16 = '31a164f845f8e27e'
ORIGINAL_MP3 = Path('corpus/ratings/6/017__It2s36sL4aM__Chicken_Grease.mp3')
RECON = Path(f'data/v3_spine/{SONG_SHA16}/render/full_reconstruction.wav')
DELIVERY_DIR = Path(f'data/v3/deliveries/{SONG_SHA16}')

AB_START = 0.0
AB_END = 30.0
AB_DUR = AB_END - AB_START
SR = 44100

OPERATOR_CHOSEN_START = 233.63918367346938
OPERATOR_CHOSEN_END = 263.63918367346935


def sha256(p: Path) -> str:
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def decode_mp3_to_wav(mp3: Path, out_wav: Path, t_start: float, t_end: float) -> None:
    """Decode a section of MP3 to 44.1kHz stereo 16-bit WAV via ffmpeg."""
    import os
    env = os.environ.copy()
    env.update({'PYTHONHASHSEED': '0', 'SOURCE_DATE_EPOCH': '1756463424',
                'TZ': 'UTC', 'LC_ALL': 'C.UTF-8'})
    out_wav.parent.mkdir(parents=True, exist_ok=True)
    tmp = out_wav.parent / (out_wav.name + '.tmp.wav')
    r = subprocess.run(
        ['ffmpeg', '-y', '-ss', str(t_start), '-t', str(t_end - t_start),
         '-i', str(mp3), '-ac', '2', '-ar', str(SR), '-acodec', 'pcm_s16le',
         str(tmp)],
        env=env, capture_output=True,
    )
    if r.returncode != 0:
        raise RuntimeError(f'ffmpeg failed rc={r.returncode}: {r.stderr.decode()[-400:]}')
    tmp.replace(out_wav)


def slice_wav(src: Path, dst: Path, t_start: float, t_end: float) -> None:
    sr, y = sw.read(str(src))
    a = int(round(t_start * sr))
    b = int(round(t_end * sr))
    seg = y[a:b]
    dst.parent.mkdir(parents=True, exist_ok=True)
    tmp = dst.with_suffix('.wav.tmp')
    sw.write(str(tmp), sr, seg)
    tmp.replace(dst)


def peak(p: Path) -> float:
    _, y = sw.read(str(p))
    if y.dtype == np.int16:
        return float(np.max(np.abs(y.astype(np.float32) / 32768.0)))
    return float(np.max(np.abs(y.astype(np.float32))))


def duration_s(p: Path) -> float:
    sr, y = sw.read(str(p))
    return y.shape[0] / sr


def main() -> None:
    DELIVERY_DIR.mkdir(parents=True, exist_ok=True)

    # original_ab.wav
    orig_ab = DELIVERY_DIR / 'original_ab.wav'
    decode_mp3_to_wav(ORIGINAL_MP3, orig_ab, AB_START, AB_END)

    # reconstruction_ab.wav
    recon_ab = DELIVERY_DIR / 'reconstruction_ab.wav'
    slice_wav(RECON, recon_ab, AB_START, AB_END)

    # full_reconstruction.wav (copy)
    full_dst = DELIVERY_DIR / 'full_reconstruction.wav'
    import shutil
    shutil.copy2(RECON, full_dst)

    # Read rubric chain
    rubric_v2_hash = Path(f'data/v3_spine/rubric_hash_v2.txt').read_text().strip()

    # Read canonical MIDI + JSON SHAs
    canon_det = json.loads(Path(f'data/v3_spine/{SONG_SHA16}/canonical_midi_determinism.json').read_text())
    per_stem_canon = {s: r['final_out_sha256'] for s, r in canon_det['results'].items()
                       if r.get('status') != 'missing_input'}

    # Debug SHAs of MuScriptor --format midi (non_factor_debug)
    debug_midi = {}
    ms_dir = Path(f'data/v3_spine/{SONG_SHA16}/muscriptor')
    for f in sorted(ms_dir.glob('*.mid')):
        debug_midi[f.stem] = sha256(f)

    # Tempo + RC5 anchor
    tempo = json.loads(Path(f'data/v3_spine/{SONG_SHA16}/tempo_choice.json').read_text())

    # Panel + verdict pinned separately once emitted; leave placeholder
    manifest = {
        'schema_version': 1,
        'cycle': 4,
        'song_sha16': SONG_SHA16,
        'song_title': 'Chicken Grease',
        'song_audio_path': str(ORIGINAL_MP3),
        'ab_window_this_cycle': {
            't_start_s': AB_START, 't_end_s': AB_END, 'duration_s': AB_DUR,
            'note': (
                'Baseline htdemucs stems in data/recreate_v2/baseline/<sha16>/rc9_6stem/ '
                'cover only t=0..30s of the original mix; MuScriptor transcribed those '
                't=0..30s stems; so the A/B window this cycle is 0..30s. Operator-chosen '
                'window t=233..263s is preserved for c5+ (requires new htdemucs_6s run '
                'on that section which is deferred).'
            ),
        },
        'operator_chosen_window_deferred_to_c5': {
            't_start_s': OPERATOR_CHOSEN_START, 't_end_s': OPERATOR_CHOSEN_END,
            'duration_s': OPERATOR_CHOSEN_END - OPERATOR_CHOSEN_START,
        },
        'artifacts': {
            'original_ab_wav': {
                'path': str(orig_ab), 'sha256': sha256(orig_ab),
                'duration_s': duration_s(orig_ab), 'peak': peak(orig_ab),
            },
            'reconstruction_ab_wav': {
                'path': str(recon_ab), 'sha256': sha256(recon_ab),
                'duration_s': duration_s(recon_ab), 'peak': peak(recon_ab),
            },
            'full_reconstruction_wav': {
                'path': str(full_dst), 'sha256': sha256(full_dst),
                'duration_s': duration_s(full_dst), 'peak': peak(full_dst),
            },
        },
        'per_stem_canonical_midi_sha': per_stem_canon,
        'tempo_choice': {
            'bpm': tempo['detected_bpm'], 'meter': tempo['meter'],
            'source': tempo['source'],
        },
        'rubric_hash_v2': rubric_v2_hash,
        'rubric_hash_v2_source_doc': 'docs/v3_spine_rubric_v2.md',
        'muscriptor_debug_midi_shas': {
            'note': 'non_factor_debug per operator OPTION A directive point 3 (cycle-3 c3 MIDIs; not authoritative)',
            'shas': debug_midi,
        },
        'panel_result': 'see data/v3/deliveries/<sha16>/panel.tsv',
        'verdict': 'see data/v3/deliveries/<sha16>/verdict.json',
    }
    (DELIVERY_DIR / 'manifest.json').write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + '\n'
    )
    print(f'wrote {DELIVERY_DIR}/{{original_ab.wav, reconstruction_ab.wav, full_reconstruction.wav, manifest.json}}')
    print(f'  original_ab: peak={peak(orig_ab):.4f} dur={duration_s(orig_ab):.4f}')
    print(f'  reconstruction_ab: peak={peak(recon_ab):.4f} dur={duration_s(recon_ab):.4f}')

    # Assertions
    for p in [orig_ab, recon_ab, full_dst]:
        assert peak(p) > 1e-4, f'{p} silent'
    assert abs(duration_s(orig_ab) - 30.0) < 0.005, 'original_ab dur off'
    assert abs(duration_s(recon_ab) - 30.0) < 0.005, 'reconstruction_ab dur off'


if __name__ == '__main__':
    main()
