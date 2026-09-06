#!/usr/bin/env /usr/bin/python3
"""Tests for c78 M-V4-GEN-1/interpolation-demo landing (scripts/gen/interpolate_v4.py).

Cases (per c78 brief §P3):
  test_01: interpolation deterministic under identical (donor, t, seed)
  test_02: at t=0.5 sampled set contains rules from both donor pools
           (rule_id provenance grep)
  test_03: AST scan on interpolate_v4.py — no PRNG, no sidecar_nonfactor,
           no VST3 state APIs
  test_04: env_pin_sha256 matches campaign anchor 2ac444c3...922ca
  test_05: c72/c73/c74 iteration anchors byte-identical (15-SHA regression)
  test_06: on-disk replay_proof.json is HOLDS + shape valid
"""
import ast
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT))

_DEMO_DIR = _REPO_ROOT / (
    'data/v4/gen/interpolation_demo/'
    'interpolation_demo_donor_a_31a164f845f8e27e_donor_b_88d247468cb6d49f_t_0.5'
)
_DRIVER = _REPO_ROOT / 'scripts/gen/interpolate_v4.py'
_MANIFEST = _DEMO_DIR / 'ab_mix.manifest.json'
_REPLAY_PROOF = _DEMO_DIR / 'ab_mix.replay_proof.json'
_AB_MIX = _DEMO_DIR / 'ab_mix.wav'

_EXPECTED_AB_MIX_SHA = 'b129c6d1bac8be90fa32249a012a47e5c9e7b369b0707ca6b2f652de478e690a'
_ENV_PIN_SHA256_ANCHOR = '2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca'


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()


def test_01_interpolation_deterministic_seed() -> None:
    """Same (donor_a, donor_b, t, seed) -> byte-identical ab_mix.wav via
    fresh subprocess into a fresh tempdir."""
    with tempfile.TemporaryDirectory(prefix='interp_test01_') as td:
        env = os.environ.copy()
        env.update({
            'PYTHONHASHSEED': '0', 'SOURCE_DATE_EPOCH': '1756463424',
            'TZ': 'UTC', 'LC_ALL': 'C.UTF-8',
            'OMP_NUM_THREADS': '1', 'MKL_NUM_THREADS': '1',
            'OPENBLAS_NUM_THREADS': '1',
        })
        r = subprocess.run(
            ['/usr/bin/python3', str(_DRIVER),
             '--donor-a', '31a164f845f8e27e',
             '--donor-b', '88d247468cb6d49f',
             '--interpolation-t', '0.5',
             '--seed', '0',
             '--out', td],
            env=env, capture_output=True, text=True, cwd=str(_REPO_ROOT),
        )
        assert r.returncode == 0, f'driver failed: {r.stderr}'
        out_wav = Path(td) / (
            'interpolation_demo_donor_a_31a164f845f8e27e_donor_b_88d247468cb6d49f_t_0.5/ab_mix.wav'
        )
        assert out_wav.exists(), f'missing {out_wav}'
        assert _sha256(out_wav) == _EXPECTED_AB_MIX_SHA, (
            f'byte-det failed: got {_sha256(out_wav)} expected {_EXPECTED_AB_MIX_SHA}'
        )
    print('test_01 PASS: interpolation deterministic')


def test_02_interpolation_t_0_5_uses_both_donors() -> None:
    """At t=0.5, the mix rule_ids should contain rules only-in-A AND
    only-in-B (per pre-registered SHA-tiebreak protocol)."""
    with open(_MANIFEST, 'r') as f:
        m = json.load(f)
    assert m['n_positions_from_donor_a_only'] > 0, (
        'zero positions from donor A only'
    )
    assert m['n_positions_from_donor_b_only'] > 0, (
        'zero positions from donor B only'
    )
    total = (m['n_positions_from_donor_a_only']
             + m['n_positions_from_donor_b_only']
             + m['n_positions_ambiguous'])
    assert total == m['n_positions'] == 24, (
        f'sum {total} != n_positions {m["n_positions"]}'
    )
    # Also verify rule_ids in mix are a subset of union(A, B) — no fabrication.
    ids_a = set(m['sampled_rule_ids_donor_a'])
    ids_b = set(m['sampled_rule_ids_donor_b'])
    for rid in m['sampled_rule_ids_mix']:
        assert rid in ids_a or rid in ids_b, (
            f'mix rule_id {rid} not in either donor pool (fabrication)'
        )
    print('test_02 PASS: interpolation uses both donors, no fabrication')


def test_03_no_prng_no_sidecar_no_vst3_state() -> None:
    """AST scan: no random module import, no sidecar_nonfactor import,
    no VST3 state APIs."""
    with open(_DRIVER, 'r') as f:
        src = f.read()
    tree = ast.parse(src)
    banned_modules = {'random', 'numpy.random', 'sidecar_nonfactor'}
    banned_attrs = {
        'get_state', 'save_state', 'save_preset', 'load_state', 'set_state',
    }
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                assert n.name not in banned_modules, (
                    f'banned import: {n.name}'
                )
        elif isinstance(node, ast.ImportFrom):
            assert node.module not in banned_modules, (
                f'banned import: {node.module}'
            )
        elif isinstance(node, ast.Call):
            fn = node.func
            if isinstance(fn, ast.Attribute):
                assert fn.attr not in banned_attrs, (
                    f'banned VST3 state API call: .{fn.attr}(...)'
                )
    # Grep also for text-level occurrences (belt+suspenders):
    for bad in ('import random', 'from random import',
                'sidecar_nonfactor', 'set_state(bytes'):
        assert bad not in src, f'source contains banned pattern: {bad!r}'
    print('test_03 PASS: no PRNG, no sidecar_nonfactor, no VST3 state')


def test_04_env_pin_canonical_7_key() -> None:
    """env_pin_sha256 in manifest matches campaign canonical 7-key anchor."""
    with open(_MANIFEST, 'r') as f:
        m = json.load(f)
    assert m['env_pin_sha256'] == _ENV_PIN_SHA256_ANCHOR, (
        f'env_pin drift: manifest {m["env_pin_sha256"]} != anchor {_ENV_PIN_SHA256_ANCHOR}'
    )
    # Also verify the 7 required keys are present.
    required = {'PYTHONHASHSEED', 'SOURCE_DATE_EPOCH', 'TZ', 'LC_ALL',
                'OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS'}
    got = set(m['env_pins'].keys())
    assert required <= got, f'missing env pins: {required - got}'
    print('test_04 PASS: env_pin canonical 7-key subset')


def test_05_c72_c73_c74_iteration_anchors_byte_identical() -> None:
    """Regression pin: 15 iter-01/02/03 A/B mix SHAs byte-identical.

    Reads iteration_rollup.json for each iteration and verifies each song's
    ab_mix.wav on disk still matches its recorded ab_mix_sha256.
    """
    for iter_n in (1, 2, 3):
        rollup_path = _REPO_ROOT / f'data/v4/gen/iteration_{iter_n:02d}/iteration_rollup.json'
        assert rollup_path.exists(), f'missing rollup: {rollup_path}'
        with open(rollup_path, 'r') as f:
            rollup = json.load(f)
        for entry in rollup['songs']:
            prov = entry['provenance']
            wav_relpath = prov['ab_mix_relpath']
            wav_path = _REPO_ROOT / wav_relpath
            assert wav_path.exists(), f'missing {wav_path}'
            on_disk = _sha256(wav_path)
            assert on_disk == prov['ab_mix_sha256'], (
                f'iter{iter_n} {prov["generated_song_id"]} drift: '
                f'on-disk {on_disk} vs recorded {prov["ab_mix_sha256"]}'
            )
    print('test_05 PASS: 15 iter anchors byte-identical')


def test_06_replay_proof_holds() -> None:
    """Validate on-disk replay_proof.json shape + verdict."""
    with open(_REPLAY_PROOF, 'r') as f:
        p = json.load(f)
    assert p['verdict'] == 'REPLAY_PROOF_HOLDS', (
        f'replay proof not HOLDS: {p["verdict"]}'
    )
    assert p['run1_sha256'] == p['run2_sha256'] == _EXPECTED_AB_MIX_SHA, (
        f'proof SHAs do not match anchor {_EXPECTED_AB_MIX_SHA}'
    )
    assert p['env_pin_sha256'] == _ENV_PIN_SHA256_ANCHOR
    # Also verify the on-disk ab_mix.wav sha matches.
    assert _sha256(_AB_MIX) == _EXPECTED_AB_MIX_SHA
    print('test_06 PASS: replay proof holds byte-det ×2')


if __name__ == '__main__':
    test_01_interpolation_deterministic_seed()
    test_02_interpolation_t_0_5_uses_both_donors()
    test_03_no_prng_no_sidecar_no_vst3_state()
    test_04_env_pin_canonical_7_key()
    test_05_c72_c73_c74_iteration_anchors_byte_identical()
    test_06_replay_proof_holds()
    print('\nALL 6 TESTS PASS')
