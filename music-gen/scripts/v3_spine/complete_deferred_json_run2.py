#!/usr/bin/env /usr/bin/python3
"""Complete cycle-3 deferred MuScriptor JSON Run-2 for OPTION A cycle 4.

Runs MuScriptor `--format json` twice into fresh tempfile.mkdtemp() dirs for
the 4 stems whose Run-2 was deferred in cycle 3: guitar, other, piano, full_mix.
Cycle-3 Run-1 SHA anchors are pinned in muscriptor_determinism_per_stem.json.
"""
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

SONG_SHA16 = '31a164f845f8e27e'
MUSCRIPTOR = 'workspace/learned_transcribers_venv/bin/muscriptor'

# Stems to complete (cycle-3 partial); each carries per-stem input WAV + instrument whitelist
# from the c3 instrument whitelist mapping.
STEMS = {
    'guitar': {
        'wav': f'data/recreate_v2/baseline/{SONG_SHA16}/rc9_6stem/guitar.wav',
        'instruments': 'clean_electric_guitar,distorted_electric_guitar,acoustic_guitar',
    },
    'other': {
        'wav': f'data/recreate_v2/baseline/{SONG_SHA16}/rc9_6stem/other.wav',
        'instruments': 'clean_electric_guitar,distorted_electric_guitar,acoustic_guitar,synth_lead,synth_pad',
    },
    'piano': {
        'wav': f'data/recreate_v2/baseline/{SONG_SHA16}/rc9_6stem/piano.wav',
        'instruments': 'acoustic_piano,electric_piano,organ',
    },
    'full_mix': {
        'wav': 'corpus/ratings/6/017__It2s36sL4aM__Chicken_Grease.mp3',
        'instruments': None,  # no whitelist for full mix cross-check
    },
}

CYCLE3_RUN1_JSON_SHAS = {
    'guitar': '97b5a598db8424bbca725c1fbbc4854e4cb39297aae390dc84f760056f4ddabc',
    'other': '4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945',
    'piano': '4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945',
    'full_mix': '7d011b6178b89407524283da830bf9cea9def41b3ffe075dec47b9a0214420fb',
}


def sha256_file(p: str) -> str:
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def run_muscriptor_json(input_wav: str, out_dir: str, instruments: str | None) -> str:
    """Run muscriptor --format json into out_dir, return path to emitted JSON."""
    env = os.environ.copy()
    env.update({
        'PYTHONHASHSEED': '0',
        'SOURCE_DATE_EPOCH': '1756463424',
        'TZ': 'UTC',
        'LC_ALL': 'C.UTF-8',
        'OMP_NUM_THREADS': '1',
        'MKL_NUM_THREADS': '1',
        'OPENBLAS_NUM_THREADS': '1',
    })
    out_path = os.path.join(out_dir, 'events.json')
    cmd = [
        MUSCRIPTOR, 'transcribe',
        input_wav,
        '--format', 'json',
        '--output', out_path,
        '--model', 'workspace/models/muscriptor-medium/model.safetensors',
        '--device', 'cpu',
        '--detect-tempo', 'best-effort',
    ]
    if instruments:
        cmd += ['--instruments', instruments]
    r = subprocess.run(cmd, env=env, capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(
            f'muscriptor failed rc={r.returncode}: {r.stderr.decode("utf-8", "replace")[-2000:]}'
        )
    return out_path


def main() -> None:
    only_stem = sys.argv[1] if len(sys.argv) > 1 else None
    results = {}
    for stem, cfg in STEMS.items():
        if only_stem and stem != only_stem:
            continue
        run1_sha_c3 = CYCLE3_RUN1_JSON_SHAS[stem]
        # Run-2 fresh
        t0 = time.monotonic()
        with tempfile.TemporaryDirectory(prefix=f'v3spine_c4_{stem}_run2_') as d:
            out = run_muscriptor_json(cfg['wav'], d, cfg['instruments'])
            run2_sha = sha256_file(out)
            # Canonicalize per spec (sort_keys=True, separators=(",",":"))
            try:
                events = json.loads(open(out).read())
                canon = json.dumps(
                    events, sort_keys=True, separators=(',', ':'), ensure_ascii=False
                )
                canon_sha = hashlib.sha256(canon.encode('utf-8')).hexdigest()
            except Exception:
                canon_sha = None
        wall_s = time.monotonic() - t0
        equal = (run2_sha == run1_sha_c3)
        results[stem] = {
            'run1_sha_cycle3': run1_sha_c3,
            'run2_sha_cycle4': run2_sha,
            'run2_canonical_sha': canon_sha,
            'equal_run1_run2_raw': equal,
            'run2_wall_s': round(wall_s, 1),
        }
        print(f'{stem:10s}  run2={run2_sha[:16]}  equal={equal}  wall={wall_s:.1f}s')
    out_path = Path(f'data/v3_spine/{SONG_SHA16}/muscriptor_determinism_json_completed.json')
    payload = {
        'schema_version': 1,
        'cycle': 4,
        'song_sha16': SONG_SHA16,
        'results': results,
        'notes': [
            'other and piano stems yielded empty JSON [] on cycle 3 (SHA of []); trivially deterministic.',
            'Empty-transcription is a content finding (M-V3-FOCUS-era whitelist widening), not a c4 blocker.',
        ],
    }
    if only_stem:
        # partial write - merge with existing if present
        if out_path.exists():
            existing = json.loads(out_path.read_text())
            existing.setdefault('results', {})[only_stem] = results[only_stem]
            payload = existing
    out_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + '\n')
    print(f'wrote {out_path}')


if __name__ == '__main__':
    main()
