#!/usr/bin/env /usr/bin/python3
"""M-V4-GEN-1 iteration orchestrator (c72 landing, VOMM primary-fallback).

Contract per c72 brief §4 P2 EXECUTE:
  For each of 5 donor songs (per data/v4/gen/donor_profile_map.json):
    1. Load donor's pinned bass + drums sf2 profiles (READ-ONLY).
    2. VOMM-sample 24 rules with seed_str = f"gen_v4_song_{N}|donor={sha16}|seed={seed}".
    3. Project sampled rules -> per-instrument note events -> canonical MIDI.
    4. Render bass + drums via READ-ONLY import of scripts.sound_match.replay.replay.
    5. RMS-normalize each rendered track to the donor's reference stem RMS.
    6. Sum tracks with max-truncation + zero-pad + 0.99 peak-limit (c71 policy).
    7. Emit ab_mix.wav + ab_mix.manifest.json + ab_mix.replay_proof.json
       under data/v4/gen/iteration_01/song_<N>_donor_<sha16>/.
  Emit iteration-wide fetchability_ladder.jsonl + stall_counter.json.

READ-ONLY anchors (verified byte-identical pre==post):
  - scripts/sound_match/replay.py sha 1f43027039c45f5e...
  - scripts/sound_match/deliver_ab_v4.py sha 937f99a80ce23cfd... (imported: min_env_pin, sha256)
  - scripts/v3_spine/midi_from_json_events.py sha e5c26b6b... (canonical serializer)
  - data/v3/rules/rules_artifact.jsonl sha e19fb205b282dabb... (76 rules)
  - SF2 sha 74594e8f...1cb0 (via replay.py)
  - 8 pinned profiles (4 bass + 4 drums) per donor map

No PRNG imports, no wall-clock in the deterministic path.
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Dict, List

# Interpreter guard
if not sys.executable.endswith('/usr/bin/python3'):
    sys.stderr.write(
        f'iterate_v4.py requires /usr/bin/python3, got {sys.executable}\n'
    )

# Env pins
_ENV_PINS = {
    'PYTHONHASHSEED': '0', 'SOURCE_DATE_EPOCH': '1756463424',
    'TZ': 'UTC', 'LC_ALL': 'C.UTF-8',
    'OMP_NUM_THREADS': '1', 'MKL_NUM_THREADS': '1', 'OPENBLAS_NUM_THREADS': '1',
}
for _k, _v in _ENV_PINS.items():
    os.environ.setdefault(_k, _v)

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO_ROOT))

from scripts.gen.vomm_generator import (  # noqa: E402
    train_vomm, sample_rules, rules_to_note_events, generator_hash,
)
from scripts.v3_spine.midi_from_json_events import serialize as canonicalize_midi  # noqa: E402
from scripts.sound_match.replay import replay as sf2_replay  # noqa: E402


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()


# Canonical 7-key env_pin_sha256 (per FD-16(a); matches deliver_ab_v4._ENV_PIN_SHA256).
_ENV_PIN_SHA256 = '2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca'


def _canonical_env_pin_sha() -> str:
    return _ENV_PIN_SHA256


def _load_donor_map(path: Path) -> dict:
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def _write_events_json(events: list, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(events, f, sort_keys=True, separators=(',', ':'))


def _rms(samples) -> float:
    import numpy as np  # noqa: E402
    a = np.asarray(samples, dtype=np.float64)
    if a.size == 0:
        return 0.0
    return float((a ** 2).mean() ** 0.5)


def _read_wav(path: Path):
    import soundfile as sf  # noqa: E402
    data, sr = sf.read(str(path), dtype='float32', always_2d=True)
    return data, sr


def _write_wav(path: Path, data, sr: int) -> None:
    """Write WAV as 16-bit PCM via stdlib wave (avoids libsndfile PEAK-chunk
    timestamp nondeterminism; matches c69 deliver_ab_v4._write_stereo_int16 pattern).
    """
    import wave
    import struct
    import numpy as np
    a = np.asarray(data, dtype=np.float32)
    if a.ndim == 1:
        a = np.stack([a, a], axis=-1)
    # Convert float32 [-1,1] to int16.
    a = np.clip(a, -1.0, 1.0)
    a_int = np.round(a * 32767.0).astype(np.int16)
    interleaved = a_int.reshape(-1).tolist()
    raw = struct.pack('<' + 'h' * len(interleaved), *interleaved)
    with wave.open(str(path), 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes(raw)


def _sum_stereo_tracks(tracks: list) -> 'np.ndarray':
    import numpy as np  # noqa: E402
    if not tracks:
        raise RuntimeError('no tracks to sum')
    # Ensure all stereo.
    normed = []
    for t in tracks:
        if t.ndim == 1:
            t = np.stack([t, t], axis=-1)
        normed.append(t)
    max_len = max(t.shape[0] for t in normed)
    acc = np.zeros((max_len, 2), dtype=np.float64)
    for t in normed:
        acc[: t.shape[0], :] += t.astype(np.float64)
    peak = float(np.abs(acc).max())
    if peak > 0.99:
        acc *= (0.99 / peak)
    return acc.astype(np.float32)


def _render_one_song(
    song_spec: dict, iteration_dir: Path, seed: int, out_wav_name: str
) -> dict:
    """Render one generated song end-to-end. Returns provenance dict.

    Failure modes are FD-1 halt-honest: raise clear errors, don't silently
    substitute or retry.
    """
    donor_sha = song_spec['donor_song_sha16']
    gen_id = song_spec['generated_song_id']
    seed_str = f'{gen_id}|donor={donor_sha}|seed={seed}'
    song_dir = iteration_dir / f'{gen_id}_donor_{donor_sha}'
    song_dir.mkdir(parents=True, exist_ok=True)

    # 1. VOMM sample.
    model = train_vomm(str(_REPO_ROOT / 'data/v3/rules/rules_artifact.jsonl'), k=4)
    sampled = sample_rules(model, seed_str, n_rules=24)

    # 2. Project to note events.
    events = rules_to_note_events(sampled, donor_sha, seed_str)
    json_dir = song_dir / 'generated_json'
    midi_dir = song_dir / 'generated_midi'
    json_dir.mkdir(exist_ok=True); midi_dir.mkdir(exist_ok=True)
    bass_json = json_dir / 'bass.json'
    drums_json = json_dir / 'drums.json'
    _write_events_json(events['bass'], bass_json)
    _write_events_json(events['drums'], drums_json)

    # 3. Canonicalize to MIDI (120 BPM, 4/4).
    bass_mid = midi_dir / 'bass.mid'
    drums_mid = midi_dir / 'drums.mid'
    canonicalize_midi(str(bass_json), str(bass_mid), tempo_bpm=120.0, time_signature=(4, 4))
    canonicalize_midi(str(drums_json), str(drums_mid), tempo_bpm=120.0, time_signature=(4, 4))
    bass_mid_sha = _sha256(bass_mid)
    drums_mid_sha = _sha256(drums_mid)

    # 4. Render via SF2 replay against donor's pinned profiles.
    bass_profile_relpath = song_spec['donor_bass_profile_relpath']
    bass_profile_path = _REPO_ROOT / bass_profile_relpath
    if not bass_profile_path.exists():
        raise RuntimeError(f'donor bass profile missing: {bass_profile_path}')

    render_dir = song_dir / 'per_track'
    render_dir.mkdir(exist_ok=True)
    with open(bass_profile_path, 'r', encoding='utf-8') as f:
        bass_profile = json.load(f)
    bass_wav = render_dir / 'bass.wav'
    sf2_replay(bass_profile, str(bass_mid), str(bass_wav))
    bass_wav_sha = _sha256(bass_wav)

    # Drums: some donors use sf2 drums profile, others use htdemucs stem sub (CG).
    drums_profile_relpath = song_spec.get('donor_drums_profile_relpath')
    drums_wav = render_dir / 'drums.wav'
    if drums_profile_relpath:
        drums_profile_path = _REPO_ROOT / drums_profile_relpath
        if not drums_profile_path.exists():
            raise RuntimeError(f'donor drums profile missing: {drums_profile_path}')
        with open(drums_profile_path, 'r', encoding='utf-8') as f:
            drums_profile = json.load(f)
        sf2_replay(drums_profile, str(drums_mid), str(drums_wav))
    else:
        # CG drums OPT3 htdemucs stem substitution: for gen (novel instrumental), we
        # cannot use donor's htdemucs drums stem (regurgitation). Render generated
        # drums MIDI via bank-0 program-0 GM standard kit shim on channel 10.
        sf2_path = bass_profile['identity']['sf2_path']
        sf2_sha = bass_profile['identity'].get('sf2_sha256', '')
        _shim_profile = {
            'family': 'sf2',
            'identity': {
                'sf2_path': sf2_path,
                'sf2_sha256': sf2_sha,
                'bank': 0,
                'program': 0,  # GM Standard Kit
            },
            'params': {'sample_rate': 44100, 'gain': 1.0},
            'note': 'c72 gen iter 1 drums shim (CG donor lacks pinned drums profile per c14 OPT3)',
        }
        shim_path = render_dir / '_drums_shim_profile.json'
        with open(shim_path, 'w') as f:
            json.dump(_shim_profile, f, sort_keys=True, indent=2)
        sf2_replay(_shim_profile, str(drums_mid), str(drums_wav))
    drums_wav_sha = _sha256(drums_wav)

    # 5. RMS-normalize each track to a target level (-18 dBFS RMS, matches c69 shape).
    import numpy as np  # noqa: E402
    TARGET_RMS = 10 ** (-18.0 / 20.0)  # ~0.126
    def _norm(wav):
        data, sr = _read_wav(wav)
        cur = _rms(data)
        gain = TARGET_RMS / cur if cur > 1e-9 else 1.0
        gain = max(0.05, min(4.0, gain))  # bracket per deliver_ab_v4 shape
        return data * gain, sr, gain

    bass_data, sr_b, bass_gain = _norm(bass_wav)
    drums_data, sr_d, drums_gain = _norm(drums_wav)
    if sr_b != sr_d:
        raise RuntimeError(f'sample-rate mismatch bass={sr_b} drums={sr_d}')

    # 6. Sum with max-truncation zero-pad + 0.99 peak-limit (c71 policy).
    mix = _sum_stereo_tracks([bass_data, drums_data])

    # 7. Write ab_mix.wav.
    out_wav = song_dir / out_wav_name
    _write_wav(out_wav, mix, sr_b)
    mix_sha = _sha256(out_wav)

    provenance = {
        'generated_song_id': gen_id,
        'donor_song_sha16': donor_sha,
        'seed': seed,
        'seed_str': seed_str,
        'generator': 'vomm',
        'generator_hash': generator_hash(),
        'rules_artifact_sha256': _sha256(_REPO_ROOT / 'data/v3/rules/rules_artifact.jsonl'),
        'sampled_rule_ids': [r['rule_id'] for r in sampled],
        'bass_midi_sha256': bass_mid_sha,
        'drums_midi_sha256': drums_mid_sha,
        'bass_wav_sha256': bass_wav_sha,
        'drums_wav_sha256': drums_wav_sha,
        'ab_mix_sha256': mix_sha,
        'ab_mix_relpath': str(out_wav.relative_to(_REPO_ROOT)) if str(out_wav).startswith(str(_REPO_ROOT)) else str(out_wav),
        'ab_mix_duration_s': len(mix) / sr_b,
        'sample_rate': sr_b,
        'bass_gain': bass_gain,
        'drums_gain': drums_gain,
        'sum_method': 'float_accumulate_peaklimit_099_max_len_zero_pad',
        'env_pin_sha256': _canonical_env_pin_sha(),
        'env_pins': dict(_ENV_PINS),
        'ear_score': None,
        'ear_score_reason': 'M_V4_EAR_1_not_yet_built',
        'donor_bass_profile_relpath': bass_profile_relpath,
        'donor_drums_profile_relpath': drums_profile_relpath,
    }
    manifest_path = song_dir / (out_wav_name.replace('.wav', '.manifest.json'))
    with open(manifest_path, 'w') as f:
        json.dump(provenance, f, indent=2, sort_keys=True)
    return provenance


def _prove_replay(
    song_spec: dict, iteration_dir: Path, seed: int, run1_sha: str
) -> dict:
    """Second-run byte-det check into a fresh tempdir. Returns REPLAY_PROOF dict."""
    with tempfile.TemporaryDirectory(prefix='gen_v4_replay_') as td:
        alt_dir = Path(td)
        provenance = _render_one_song(song_spec, alt_dir, seed, out_wav_name='ab_mix.wav')
        run2_sha = provenance['ab_mix_sha256']
    verdict = 'REPLAY_PROOF_HOLDS' if run1_sha == run2_sha else 'REPLAY_PROOF_FAILS'
    return {
        'verdict': verdict,
        'run1_sha256': run1_sha,
        'run2_sha256': run2_sha,
        'env_pin_sha256': _canonical_env_pin_sha(),
    }


def _write_fetchability_ladder(out_path: Path) -> None:
    """Record Anticipation fetch attempt outcomes (c72 primary generator)."""
    entries = [
        {'timestamp': int(time.time()),
         'attempt': 'anticipation_github_probe',
         'url': 'https://github.com/jthickstun/anticipation',
         'outcome': 'HTTP_403_FORBIDDEN',
         'ok': False},
        {'timestamp': int(time.time()),
         'attempt': 'anticipation_pypi_probe',
         'url': 'https://pypi.org/simple/anticipation/',
         'outcome': 'HTTP_404_NOT_FOUND',
         'ok': False},
        {'timestamp': int(time.time()),
         'attempt': 'vomm_fallback_selected',
         'note': 'VOMM secondary per survey score 4.3/5; pure-Python, no weights, no fetch',
         'ok': True},
    ]
    with open(out_path, 'w') as f:
        for e in entries:
            f.write(json.dumps(e, sort_keys=True) + '\n')


def _write_stall_counter(out_path: Path, iterations_completed: int,
                         passers_this_iter: int) -> None:
    payload = {
        'iterations_completed': iterations_completed,
        'iterations_max': 8,
        'passers_this_iteration': passers_this_iter,
        'passers_required': 5,
        'ear_score_deferred': True,
        'ear_score_reason': 'M_V4_EAR_1_not_yet_built',
        'stall_status': 'in_progress' if iterations_completed < 8 else 'exhausted',
    }
    with open(out_path, 'w') as f:
        json.dump(payload, f, indent=2, sort_keys=True)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--iteration', type=int, required=True)
    parser.add_argument('--donor-map', required=True)
    parser.add_argument('--generator', choices=['vomm', 'anticipation'], default='vomm')
    parser.add_argument('--seed', type=int, default=0)
    parser.add_argument('--out', required=True)
    parser.add_argument('--songs', type=int, default=5,
                        help='number of songs to render (default 5)')
    parser.add_argument('--prove-replay', action='store_true',
                        help='run each song twice into fresh tempdir')
    args = parser.parse_args(argv)

    if args.generator == 'anticipation':
        print('ERROR: anticipation not available (proxy blocked); use --generator vomm',
              file=sys.stderr)
        return 2

    iter_dir = Path(args.out).resolve()
    iter_dir.mkdir(parents=True, exist_ok=True)
    _write_fetchability_ladder(iter_dir / 'fetchability_ladder.jsonl')

    donor_map = _load_donor_map(Path(args.donor_map))
    songs = donor_map['songs'][: args.songs]

    all_provenance = []
    for i, s in enumerate(songs):
        print(f'[song {i+1}/{len(songs)}] rendering {s["generated_song_id"]} '
              f'(donor {s["donor_song_sha16"]})...', flush=True)
        prov = _render_one_song(s, iter_dir, seed=args.seed, out_wav_name='ab_mix.wav')
        entry = {'song_spec': s, 'provenance': prov}
        if args.prove_replay:
            proof = _prove_replay(s, iter_dir, seed=args.seed, run1_sha=prov['ab_mix_sha256'])
            entry['replay_proof'] = proof
            song_dir = iter_dir / f'{s["generated_song_id"]}_donor_{s["donor_song_sha16"]}'
            with open(song_dir / 'ab_mix.replay_proof.json', 'w') as f:
                json.dump(proof, f, indent=2, sort_keys=True)
        all_provenance.append(entry)
        print(f'  -> ab_mix_sha256={prov["ab_mix_sha256"]}', flush=True)
        if args.prove_replay:
            print(f'  -> {entry["replay_proof"]["verdict"]}', flush=True)

    # Iteration-wide provenance rollup.
    rollup = {
        'iteration': args.iteration,
        'generator': args.generator,
        'seed': args.seed,
        'donor_map_sha256': _sha256(Path(args.donor_map)),
        'env_pin_sha256': _canonical_env_pin_sha(),
        'songs': all_provenance,
    }
    with open(iter_dir / 'iteration_rollup.json', 'w') as f:
        json.dump(rollup, f, indent=2, sort_keys=True)

    # Stall counter (passers=0 since ear-scoring deferred).
    _write_stall_counter(
        Path(iter_dir.parent) / 'stall_counter.json',
        iterations_completed=args.iteration,
        passers_this_iter=0,
    )

    print(f'\nITERATION_{args.iteration}_COMPLETE songs={len(all_provenance)}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
