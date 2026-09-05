#!/usr/bin/env /usr/bin/python3
"""Tests for M-V4-GEN-1 c72 iteration 1 driver (VOMM primary-fallback).

Contract per c72 brief §4 P4: ≥5 named cases covering donor map shape,
fetchability ladder shape, VOMM determinism, per-song manifest shape, and
structural-gate WARN-only posture on generated music.
"""
import hashlib
import json
import os
import sys
import tempfile
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT))
os.chdir(str(_REPO_ROOT))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_01_donor_map_5_songs() -> bool:
    """donor_profile_map.json has 5 entries + interpolation demo spec."""
    with open('data/v4/gen/donor_profile_map.json') as f:
        m = json.load(f)
    assert len(m['songs']) == 5, f'expected 5 songs, got {len(m["songs"])}'
    assert 'interpolation_demo' in m
    donors = {s['donor_song_sha16'] for s in m['songs']}
    expected = {'31a164f845f8e27e', '252eb21ce7df7328', '51e433ade2a845e1',
                '88d247468cb6d49f', 'cdd2717e52820ff6'}
    assert donors == expected, f'donor set mismatch: {donors ^ expected}'
    return True


def test_02_fetchability_ladder_shape() -> bool:
    """fetchability_ladder.jsonl carries HTTP status + timestamp per attempt."""
    path = Path('data/v4/gen/iteration_01/fetchability_ladder.jsonl')
    assert path.exists(), 'fetchability_ladder.jsonl missing'
    lines = path.read_text().strip().split('\n')
    assert len(lines) >= 3, f'expected >=3 attempts, got {len(lines)}'
    for line in lines:
        e = json.loads(line)
        assert 'timestamp' in e and isinstance(e['timestamp'], int)
        assert 'ok' in e
    # First attempt should be an anticipation probe.
    e0 = json.loads(lines[0])
    assert 'anticipation' in e0.get('attempt', '').lower()
    return True


def test_03_vomm_deterministic_seed() -> bool:
    """VOMM generator with seed=0 produces byte-identical MIDI across two runs."""
    from scripts.gen.vomm_generator import train_vomm, sample_rules, rules_to_note_events
    from scripts.v3_spine.midi_from_json_events import serialize
    seed_str = 'test_03|donor=31a164f845f8e27e|seed=0'
    model = train_vomm('data/v3/rules/rules_artifact.jsonl', k=4)
    r1 = sample_rules(model, seed_str, n_rules=24)
    e1 = rules_to_note_events(r1, '31a164f845f8e27e', seed_str)
    model2 = train_vomm('data/v3/rules/rules_artifact.jsonl', k=4)
    r2 = sample_rules(model2, seed_str, n_rules=24)
    e2 = rules_to_note_events(r2, '31a164f845f8e27e', seed_str)
    assert [r['rule_id'] for r in r1] == [r['rule_id'] for r in r2], \
        'sampled rule_ids diverge'
    # Serialize both to MIDI and compare bytes.
    with tempfile.TemporaryDirectory() as td:
        p1 = Path(td) / 'a.json'; p2 = Path(td) / 'b.json'
        m1 = Path(td) / 'a.mid'; m2 = Path(td) / 'b.mid'
        p1.write_text(json.dumps(e1['bass'], sort_keys=True, separators=(',', ':')))
        p2.write_text(json.dumps(e2['bass'], sort_keys=True, separators=(',', ':')))
        serialize(str(p1), str(m1), tempo_bpm=120.0, time_signature=(4, 4))
        serialize(str(p2), str(m2), tempo_bpm=120.0, time_signature=(4, 4))
        assert _sha256(m1) == _sha256(m2), 'MIDI SHA diverges across runs'
    return True


def test_04_iteration_01_manifest_shape() -> bool:
    """Per-song manifest carries seed, generator_hash, rules_hash, donor, env_pins, ear_score placeholder."""
    for song_dir in sorted(Path('data/v4/gen/iteration_01').glob('gen_v4_song_*')):
        m_path = song_dir / 'ab_mix.manifest.json'
        assert m_path.exists(), f'missing manifest {m_path}'
        m = json.loads(m_path.read_text())
        for k in ('seed', 'generator_hash', 'rules_artifact_sha256',
                  'donor_song_sha16', 'env_pins', 'env_pin_sha256',
                  'ear_score', 'ear_score_reason', 'ab_mix_sha256'):
            assert k in m, f'{song_dir.name}: manifest missing {k}'
        assert m['ear_score'] is None
        assert m['ear_score_reason'] == 'M_V4_EAR_1_not_yet_built'
        assert m['env_pin_sha256'] == '2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca'
    return True


def test_05_structural_gate_warn_not_halt() -> bool:
    """Recreation-tuned bass-register-bounds check WARNs on generated music per prompt L131-134, doesn't FD-1 halt.

    Verified by construction: iterate_v4.py does NOT call any recreation-tuned
    structural gate (bass median-pitch <55 gate; drums channel-10 non-empty
    gate) on the generated MIDI. Assert the driver source contains no such
    halt-raising call sites.
    """
    src = Path('scripts/gen/iterate_v4.py').read_text()
    # No structural-gate halt patterns from recreation-mode code paths.
    for banned in ('bass_median_pitch < 55', 'raise if any(', 'STRUCTURAL_GATE_HALT'):
        assert banned not in src, f'iterate_v4.py contains banned structural-gate pattern: {banned}'
    # Positive check: presence of the WARN-only posture note in the module docstring.
    assert 'FD-1 halt-honest' in src, 'iterate_v4.py should honor FD-1 halt-honest disclosure norm'
    return True


def test_06_replay_proofs_hold_5_of_5() -> bool:
    """All 5 c72 iteration 1 replay proofs verify REPLAY_PROOF_HOLDS."""
    holds = 0; total = 0
    for song_dir in sorted(Path('data/v4/gen/iteration_01').glob('gen_v4_song_*')):
        p = song_dir / 'ab_mix.replay_proof.json'
        if p.exists():
            total += 1
            proof = json.loads(p.read_text())
            assert proof['verdict'] == 'REPLAY_PROOF_HOLDS', \
                f'{song_dir.name}: {proof["verdict"]}'
            assert proof['run1_sha256'] == proof['run2_sha256']
            holds += 1
    assert total == 5, f'expected 5 replay proofs, got {total}'
    assert holds == 5, f'expected 5 HOLDS, got {holds}'
    return True


def _run_all() -> int:
    tests = [
        ('test_01_donor_map_5_songs', test_01_donor_map_5_songs),
        ('test_02_fetchability_ladder_shape', test_02_fetchability_ladder_shape),
        ('test_03_vomm_deterministic_seed', test_03_vomm_deterministic_seed),
        ('test_04_iteration_01_manifest_shape', test_04_iteration_01_manifest_shape),
        ('test_05_structural_gate_warn_not_halt', test_05_structural_gate_warn_not_halt),
        ('test_06_replay_proofs_hold_5_of_5', test_06_replay_proofs_hold_5_of_5),
    ]
    passed = 0
    for name, fn in tests:
        try:
            fn()
            print(f'PASS {name}')
            passed += 1
        except AssertionError as e:
            print(f'FAIL {name}: {e}')
        except Exception as e:
            print(f'ERROR {name}: {type(e).__name__}: {e}')
    print(f'\n{passed}/{len(tests)} passed')
    return 0 if passed == len(tests) else 1


if __name__ == '__main__':
    sys.exit(_run_all())
