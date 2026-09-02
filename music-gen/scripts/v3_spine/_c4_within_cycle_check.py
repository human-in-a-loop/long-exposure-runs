"""Check c4-to-c4 determinism for the previously-diverged guitar JSON.

If c4 Run-1 == c4 Run-2 (byte-identical), the c3 vs c4 divergence is an
environment-drift/version-drift artifact between cycles, not a live-run
nondeterminism. In that case, adopt c4 anchor as authoritative and
proceed under OPTION A.
"""
import hashlib
import json
import os
import subprocess
import tempfile
import time

ENV = {**os.environ, **{
    'PYTHONHASHSEED': '0', 'SOURCE_DATE_EPOCH': '1756463424',
    'TZ': 'UTC', 'LC_ALL': 'C.UTF-8',
    'OMP_NUM_THREADS': '1', 'MKL_NUM_THREADS': '1', 'OPENBLAS_NUM_THREADS': '1',
}}


def run_once(stem_wav: str, instruments: str) -> tuple[str, float]:
    with tempfile.TemporaryDirectory() as d:
        out = os.path.join(d, 'ev.json')
        t0 = time.monotonic()
        subprocess.run([
            'workspace/learned_transcribers_venv/bin/muscriptor', 'transcribe',
            stem_wav, '--format', 'json', '--output', out,
            '--model', 'workspace/models/muscriptor-medium/model.safetensors',
            '--device', 'cpu', '--detect-tempo', 'best-effort',
            '--instruments', instruments,
        ], env=ENV, check=True, capture_output=True)
        wall = time.monotonic() - t0
        sha = hashlib.sha256(open(out, 'rb').read()).hexdigest()
    return sha, wall


def main():
    stems = {
        'guitar': ('data/recreate_v2/baseline/31a164f845f8e27e/rc9_6stem/guitar.wav',
                   'clean_electric_guitar,distorted_electric_guitar,acoustic_guitar'),
    }
    out_path = 'data/v3_spine/31a164f845f8e27e/muscriptor_c4_within_cycle_check.json'
    results = {}
    for stem, (wav, insts) in stems.items():
        sha_a, wall_a = run_once(wav, insts)
        sha_b, wall_b = run_once(wav, insts)
        results[stem] = {
            'c4_run_a_sha': sha_a, 'c4_run_a_wall_s': round(wall_a, 1),
            'c4_run_b_sha': sha_b, 'c4_run_b_wall_s': round(wall_b, 1),
            'c4_to_c4_equal': (sha_a == sha_b),
        }
        print(f'{stem}: c4_a={sha_a[:16]} c4_b={sha_b[:16]} equal={sha_a==sha_b}')
    payload = {
        'schema_version': 1, 'cycle': 4, 'song_sha16': '31a164f845f8e27e',
        'results': results,
        'note': 'c4-to-c4 determinism probe; if equal here, cycle-3 vs cycle-4 divergence attributed to environment drift (torch/BLAS versions between cycles).',
    }
    open(out_path, 'w').write(json.dumps(payload, indent=2, sort_keys=True) + '\n')
    print(f'wrote {out_path}')


if __name__ == '__main__':
    main()
