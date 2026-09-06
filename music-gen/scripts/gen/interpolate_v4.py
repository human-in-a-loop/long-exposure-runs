#!/usr/bin/env /usr/bin/python3
"""M-V4-GEN-1 interpolation-hybrid demo driver (c78 landing).

Per c78 brief §P1: additive sibling to c72 `scripts/gen/iterate_v4.py`
(READ-ONLY anchor per FD-1 + invariant (d) DO-NOT-TOUCH). Renders a novel
song whose rule sequence is an interpolation between two donor rule sets
sampled by VOMM at the same seed but different `seed_str` prefixes.

Interpolation semantics (pre-registered in c78 brief §P1 step 1-3):
  1. VOMM sample rules_A using donor_a's seed_str; rules_B using donor_b's.
  2. Rules are corpus-selected instances (content-hashed rule_id), not
     parameter-tunable per position. Arithmetic mean on rule-parameter
     vectors would fabricate new rules absent from the corpus (violates
     FD-1). Per pre-registered fallback (step 2), fall back to per-position
     SHA-256 tiebreak: at each of the 24 positions, pick rules_A[i] if
     sha256(f"{donor_a}|{donor_b}|pos{i}|seed{seed}") % 1000 / 1000.0 < (1-t)
     else rules_B[i].
  3. Interpolated rule set r_mix has ~50% from A + ~50% from B at t=0.5.
  4. Render via same VOMM->canonical MIDI->SF2 replay pipeline as iter-01..03.
     Uses donor A's bass profile (interpolation is on rule-vector, not
     stems). CG donor lacks pinned drums profile per c14 OPT3 -> GM
     Standard Kit shim (matches iter renders' pattern).

READ-ONLY anchors (verified byte-identical pre==post):
  - scripts/gen/iterate_v4.py (c72 sibling; DO-NOT-TOUCH)
  - scripts/gen/vomm_generator.py (c72; imported read-only)
  - scripts/sound_match/replay.py (c11 fix; imported read-only)
  - scripts/v3_spine/midi_from_json_events.py (c4 canonical serializer)
  - data/v3/rules/rules_artifact.jsonl (76 rules, sha e19fb205...)
  - SF2 sha 74594e8f...1cb0 (via replay.py)
  - 8 pinned profiles (imported by ref through donor map)

No PRNG, no wall-clock in the deterministic path.
"""
import argparse
import hashlib
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Dict, List

# Interpreter guard
if not sys.executable.endswith('/usr/bin/python3'):
    sys.stderr.write(
        f'interpolate_v4.py requires /usr/bin/python3, got {sys.executable}\n'
    )

# Env pins (7-key canonical subset; matches env_pin_sha256=2ac444c3...922ca)
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

_ENV_PIN_SHA256 = '2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca'


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()


def _rms(samples) -> float:
    import numpy as np
    a = np.asarray(samples, dtype=np.float64)
    if a.size == 0:
        return 0.0
    return float((a ** 2).mean() ** 0.5)


def _read_wav(path: Path):
    import soundfile as sf
    data, sr = sf.read(str(path), dtype='float32', always_2d=True)
    return data, sr


def _write_wav(path: Path, data, sr: int) -> None:
    """Write WAV as 16-bit PCM via stdlib wave (byte-deterministic)."""
    import wave
    import struct
    import numpy as np
    a = np.asarray(data, dtype=np.float32)
    if a.ndim == 1:
        a = np.stack([a, a], axis=-1)
    a = np.clip(a, -1.0, 1.0)
    a_int = np.round(a * 32767.0).astype(np.int16)
    interleaved = a_int.reshape(-1).tolist()
    raw = struct.pack('<' + 'h' * len(interleaved), *interleaved)
    with wave.open(str(path), 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes(raw)


def _sum_stereo_tracks(tracks: list):
    import numpy as np
    if not tracks:
        raise RuntimeError('no tracks to sum')
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


def _write_events_json(events: list, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(events, f, sort_keys=True, separators=(',', ':'))


def _interpolate_rule_sequences(
    rules_a: List[dict],
    rules_b: List[dict],
    donor_a_sha: str,
    donor_b_sha: str,
    t: float,
    seed: int,
) -> List[dict]:
    """Per-position SHA-256 tiebreak interpolation at threshold t.

    Rules are corpus-selected instances (content-hashed rule_id). Per
    c78 brief §P1 step 2 pre-registered fallback: at each position,
    pick rules_a[i] if sha256_tiebreak < (1-t) else rules_b[i]. At
    t=0.5, expected ~50% from A + ~50% from B.

    Halt-honest per FD-1: NO fabricated intermediate rules; picks are
    corpus-canonical.
    """
    n = min(len(rules_a), len(rules_b))
    picked: List[dict] = []
    for i in range(n):
        digest = hashlib.sha256(
            f'{donor_a_sha}|{donor_b_sha}|pos{i:03d}|seed{seed}'.encode('utf-8')
        ).digest()
        # Deterministic uniform in [0, 1) from first 8 bytes of digest.
        r = int.from_bytes(digest[:8], 'big') / (1 << 64)
        if r < (1.0 - t):
            picked.append(rules_a[i])
        else:
            picked.append(rules_b[i])
    return picked


def _load_profile(relpath: str) -> dict:
    with open(_REPO_ROOT / relpath, 'r', encoding='utf-8') as f:
        return json.load(f)


def _render_interpolated_song(
    donor_a_sha: str,
    donor_b_sha: str,
    donor_a_bass_profile_relpath: str,
    interpolation_t: float,
    seed: int,
    out_dir: Path,
    out_wav_name: str,
) -> dict:
    """Render the interpolation-demo song. Returns provenance dict."""
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. Sample rules_A + rules_B from same VOMM with different seed strings.
    model = train_vomm(str(_REPO_ROOT / 'data/v3/rules/rules_artifact.jsonl'), k=4)
    seed_str_a = f'interp_demo|donor={donor_a_sha}|seed={seed}'
    seed_str_b = f'interp_demo|donor={donor_b_sha}|seed={seed}'
    rules_a = sample_rules(model, seed_str_a, n_rules=24)
    rules_b = sample_rules(model, seed_str_b, n_rules=24)

    # 2. Interpolate at t via per-position SHA-256 tiebreak.
    rules_mix = _interpolate_rule_sequences(
        rules_a, rules_b, donor_a_sha, donor_b_sha, interpolation_t, seed
    )

    # Count how many positions came from A vs B (for provenance).
    ids_a = {r['rule_id'] for r in rules_a}
    ids_b = {r['rule_id'] for r in rules_b}
    n_from_a = sum(1 for r in rules_mix if r['rule_id'] in ids_a and r['rule_id'] not in ids_b)
    n_from_b = sum(1 for r in rules_mix if r['rule_id'] in ids_b and r['rule_id'] not in ids_a)
    n_ambiguous = len(rules_mix) - n_from_a - n_from_b  # in both A and B

    # 3. Project mixed rules to per-instrument note events.
    seed_str_mix = f'interp_mix|donor_a={donor_a_sha}|donor_b={donor_b_sha}|t={interpolation_t}|seed={seed}'
    events = rules_to_note_events(rules_mix, donor_a_sha, seed_str_mix)

    json_dir = out_dir / 'generated_json'
    midi_dir = out_dir / 'generated_midi'
    json_dir.mkdir(exist_ok=True); midi_dir.mkdir(exist_ok=True)
    bass_json = json_dir / 'bass.json'
    drums_json = json_dir / 'drums.json'
    _write_events_json(events['bass'], bass_json)
    _write_events_json(events['drums'], drums_json)

    # 4. Canonicalize to MIDI.
    bass_mid = midi_dir / 'bass.mid'
    drums_mid = midi_dir / 'drums.mid'
    canonicalize_midi(str(bass_json), str(bass_mid), tempo_bpm=120.0, time_signature=(4, 4))
    canonicalize_midi(str(drums_json), str(drums_mid), tempo_bpm=120.0, time_signature=(4, 4))
    bass_mid_sha = _sha256(bass_mid)
    drums_mid_sha = _sha256(drums_mid)

    # 5. Render bass via donor A's pinned bass profile.
    bass_profile = _load_profile(donor_a_bass_profile_relpath)
    render_dir = out_dir / 'per_track'
    render_dir.mkdir(exist_ok=True)
    bass_wav = render_dir / 'bass.wav'
    sf2_replay(bass_profile, str(bass_mid), str(bass_wav))
    bass_wav_sha = _sha256(bass_wav)

    # 6. Render drums via GM Standard Kit shim (CG donor lacks pinned drums
    # profile per c14 OPT3; matches iter renders' pattern).
    sf2_path = bass_profile['identity']['sf2_path']
    sf2_sha = bass_profile['identity'].get('sf2_sha256', '')
    drums_shim = {
        'family': 'sf2',
        'identity': {
            'sf2_path': sf2_path,
            'sf2_sha256': sf2_sha,
            'bank': 0,
            'program': 0,  # GM Standard Kit
        },
        'params': {'sample_rate': 44100, 'gain': 1.0},
        'note': 'c78 interpolation demo drums shim (donor A CG lacks pinned drums profile per c14 OPT3)',
    }
    with open(render_dir / '_drums_shim_profile.json', 'w') as f:
        json.dump(drums_shim, f, sort_keys=True, indent=2)
    drums_wav = render_dir / 'drums.wav'
    sf2_replay(drums_shim, str(drums_mid), str(drums_wav))
    drums_wav_sha = _sha256(drums_wav)

    # 7. RMS-normalize to -18 dBFS.
    import numpy as np
    TARGET_RMS = 10 ** (-18.0 / 20.0)
    def _norm(wav):
        data, sr = _read_wav(wav)
        cur = _rms(data)
        gain = TARGET_RMS / cur if cur > 1e-9 else 1.0
        gain = max(0.05, min(4.0, gain))
        return data * gain, sr, gain

    bass_data, sr_b, bass_gain = _norm(bass_wav)
    drums_data, sr_d, drums_gain = _norm(drums_wav)
    if sr_b != sr_d:
        raise RuntimeError(f'sample-rate mismatch bass={sr_b} drums={sr_d}')

    # 8. Sum + peak-limit.
    mix = _sum_stereo_tracks([bass_data, drums_data])

    # 9. Write ab_mix.wav.
    out_wav = out_dir / out_wav_name
    _write_wav(out_wav, mix, sr_b)
    mix_sha = _sha256(out_wav)

    provenance = {
        'demo_kind': 'interpolation_hybrid',
        'donor_a_sha16': donor_a_sha,
        'donor_b_sha16': donor_b_sha,
        'interpolation_t': interpolation_t,
        'interpolation_semantics': 'per_position_sha256_tiebreak_at_threshold_t',
        'interpolation_semantics_rationale': (
            'Rules are corpus-selected instances (content-hashed rule_id), '
            'not parameter-tunable per position. Arithmetic mean on rule-'
            'parameter vectors would fabricate new rules absent from the '
            'corpus (violates FD-1). Pre-registered fallback (c78 brief §P1 '
            'step 2): per-position SHA-256 tiebreak at threshold t.'
        ),
        'n_positions': len(rules_mix),
        'n_positions_from_donor_a_only': n_from_a,
        'n_positions_from_donor_b_only': n_from_b,
        'n_positions_ambiguous': n_ambiguous,
        'seed': seed,
        'seed_str_donor_a': seed_str_a,
        'seed_str_donor_b': seed_str_b,
        'seed_str_mix': seed_str_mix,
        'generator': 'vomm',
        'generator_hash': generator_hash(),
        'rules_artifact_sha256': _sha256(_REPO_ROOT / 'data/v3/rules/rules_artifact.jsonl'),
        'sampled_rule_ids_donor_a': [r['rule_id'] for r in rules_a],
        'sampled_rule_ids_donor_b': [r['rule_id'] for r in rules_b],
        'sampled_rule_ids_mix': [r['rule_id'] for r in rules_mix],
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
        'env_pin_sha256': _ENV_PIN_SHA256,
        'env_pins': dict(_ENV_PINS),
        'donor_a_bass_profile_relpath': donor_a_bass_profile_relpath,
        'donor_a_bass_profile_sha256': _sha256(_REPO_ROOT / donor_a_bass_profile_relpath),
        'drums_source': 'gm_standard_kit_shim_c14_OPT3',
        'ear_score': None,
        'ear_score_reason': 'M_V4_EAR_1_L119_infeasible_under_vggish_only_backbone_operator_ear_authoritative_per_FD_6',
    }
    manifest_path = out_dir / out_wav_name.replace('.wav', '.manifest.json')
    with open(manifest_path, 'w') as f:
        json.dump(provenance, f, indent=2, sort_keys=True)
    return provenance


def _prove_replay(
    donor_a_sha: str,
    donor_b_sha: str,
    donor_a_bass_profile_relpath: str,
    interpolation_t: float,
    seed: int,
    run1_sha: str,
) -> dict:
    """Second-run byte-det check into fresh tempdir."""
    with tempfile.TemporaryDirectory(prefix='interp_v4_replay_') as td:
        alt_dir = Path(td)
        prov = _render_interpolated_song(
            donor_a_sha, donor_b_sha, donor_a_bass_profile_relpath,
            interpolation_t, seed, alt_dir, out_wav_name='ab_mix.wav',
        )
        run2_sha = prov['ab_mix_sha256']
    verdict = 'REPLAY_PROOF_HOLDS' if run1_sha == run2_sha else 'REPLAY_PROOF_FAILS'
    return {
        'verdict': verdict,
        'run1_sha256': run1_sha,
        'run2_sha256': run2_sha,
        'env_pin_sha256': _ENV_PIN_SHA256,
    }


# Donor bass profile resolution table for the demo. Only pair used at c78
# is CG (donor A) x PD (donor B) per c74 P6 spec + c70 donor_profile_map.
_DONOR_A_BASS_PROFILE_RELPATH = {
    '31a164f845f8e27e': 'data/v4/profiles/31a164f845f8e27e/bass_v2.json',
    '252eb21ce7df7328': 'data/v4/profiles/252eb21ce7df7328/bass.json',
    '51e433ade2a845e1': 'data/v4/profiles/51e433ade2a845e1/bass.json',
    '88d247468cb6d49f': 'data/v4/profiles/88d247468cb6d49f/bass.json',
    'cdd2717e52820ff6': 'data/v4/profiles/cdd2717e52820ff6/bass.json',
}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--donor-a', required=True,
                        help='donor A sha16 (default demo: 31a164f845f8e27e = CG)')
    parser.add_argument('--donor-b', required=True,
                        help='donor B sha16 (default demo: 88d247468cb6d49f = PD)')
    parser.add_argument('--interpolation-t', type=float, default=0.5)
    parser.add_argument('--seed', type=int, default=0)
    parser.add_argument('--out', required=True,
                        help='output dir (created if absent)')
    parser.add_argument('--prove-replay', action='store_true',
                        help='run twice into fresh tempdir; emit replay proof')
    args = parser.parse_args(argv)

    donor_a_bass_profile_relpath = _DONOR_A_BASS_PROFILE_RELPATH.get(args.donor_a)
    if donor_a_bass_profile_relpath is None:
        print(f'ERROR: unknown donor A sha16 {args.donor_a}', file=sys.stderr)
        return 2

    out_dir = Path(args.out).resolve() / (
        f'interpolation_demo_donor_a_{args.donor_a}_donor_b_{args.donor_b}_t_{args.interpolation_t}'
    )

    print(f'[interp_demo] rendering donor_a={args.donor_a} donor_b={args.donor_b} '
          f't={args.interpolation_t} seed={args.seed}...', flush=True)
    prov = _render_interpolated_song(
        args.donor_a, args.donor_b, donor_a_bass_profile_relpath,
        args.interpolation_t, args.seed, out_dir, out_wav_name='ab_mix.wav',
    )
    print(f'  -> ab_mix_sha256={prov["ab_mix_sha256"]}', flush=True)
    print(f'  -> from_A={prov["n_positions_from_donor_a_only"]} '
          f'from_B={prov["n_positions_from_donor_b_only"]} '
          f'ambiguous={prov["n_positions_ambiguous"]} / {prov["n_positions"]}',
          flush=True)

    if args.prove_replay:
        proof = _prove_replay(
            args.donor_a, args.donor_b, donor_a_bass_profile_relpath,
            args.interpolation_t, args.seed, prov['ab_mix_sha256'],
        )
        with open(out_dir / 'ab_mix.replay_proof.json', 'w') as f:
            json.dump(proof, f, indent=2, sort_keys=True)
        print(f'  -> {proof["verdict"]}', flush=True)
        if proof['verdict'] != 'REPLAY_PROOF_HOLDS':
            # FD-1 halt-honest: report non-deterministic render.
            print('FD-1 halt-honest: interpolation demo render is non-deterministic; '
                  'FAILING to disclose per c78 brief §P1 falsification criteria.',
                  file=sys.stderr)
            return 3

    print(f'\nINTERPOLATION_DEMO_LANDED ab_mix_sha256={prov["ab_mix_sha256"]}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
