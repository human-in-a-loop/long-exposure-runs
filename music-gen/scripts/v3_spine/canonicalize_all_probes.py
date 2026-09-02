#!/usr/bin/env /usr/bin/python3
"""Canonicalize all 7 stems + full_mix from MuScriptor JSON events into
byte-deterministic MIDIs via the canonical serializer. Runs ×2 into
fresh tempfile.mkdtemp() dirs and asserts SHA-256 equality per probe.
"""
import hashlib
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from scripts.v3_spine.midi_from_json_events import serialize  # noqa: E402

SONG_SHA16 = '31a164f845f8e27e'
JSON_DIR = Path(f'data/v3_spine/{SONG_SHA16}/muscriptor')
OUT_DIR = Path(f'data/v3_spine/{SONG_SHA16}/canonical_midi')
STEMS = ['drums', 'bass', 'guitar', 'other', 'piano', 'vocals', 'full_mix']


def sha256_file(p: str) -> str:
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def main() -> None:
    tempo = json.loads(Path(f'data/v3_spine/{SONG_SHA16}/tempo_choice.json').read_text())
    bpm = float(tempo['detected_bpm'])
    meter = tuple(tempo['meter'])

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    results = {}
    for stem in STEMS:
        jp = JSON_DIR / f'{stem}.json'
        if not jp.exists():
            print(f'SKIP {stem}: {jp} missing')
            results[stem] = {'status': 'missing_input'}
            continue

        # Run 1 into temp1
        with tempfile.TemporaryDirectory(prefix=f'canon_{stem}_r1_') as d1:
            out1 = os.path.join(d1, f'{stem}.mid')
            serialize(str(jp), out1, bpm, meter)
            sha1 = sha256_file(out1)
            # Copy final artifact to authoritative location from run-1
            final_path = OUT_DIR / f'{stem}.mid'
            shutil.copy2(out1, final_path)

        # Run 2 into temp2
        with tempfile.TemporaryDirectory(prefix=f'canon_{stem}_r2_') as d2:
            out2 = os.path.join(d2, f'{stem}.mid')
            serialize(str(jp), out2, bpm, meter)
            sha2 = sha256_file(out2)

        final_sha = sha256_file(str(final_path))
        equal = (sha1 == sha2 == final_sha)
        results[stem] = {
            'input_json': str(jp),
            'input_json_sha256': sha256_file(str(jp)),
            'run1_sha256': sha1,
            'run2_sha256': sha2,
            'final_out_sha256': final_sha,
            'final_out_path': str(final_path),
            'byte_deterministic_x2': equal,
        }
        print(f'{stem:10s} run1={sha1[:16]} run2={sha2[:16]} equal={equal}')

    payload = {
        'schema_version': 1, 'cycle': 4, 'song_sha16': SONG_SHA16,
        'tempo_bpm': bpm, 'meter': list(meter),
        'serializer_path': 'scripts/v3_spine/midi_from_json_events.py',
        'serializer_spec_hash_path': 'data/v3_spine/canonical_serializer_spec_hash.txt',
        'results': results,
        'note': (
            'Canonical MIDI byte-determinism x2 gate (rung 1a per rubric-v2 sub-clause b). '
            'Serializer is a pure function of (json_events_path, tempo_bpm, time_signature); '
            'byte-determinism x2 within cycle 4 is verified by re-serializing into fresh temp dirs.'
        ),
    }
    out_json = Path(f'data/v3_spine/{SONG_SHA16}/canonical_midi_determinism.json')
    out_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + '\n')
    print(f'wrote {out_json}')

    # STOP condition
    fails = [s for s, r in results.items() if not r.get('byte_deterministic_x2')]
    if fails:
        print(f'STOP: canonical serializer NON-DETERMINISTIC on: {fails}')
        sys.exit(1)


if __name__ == '__main__':
    main()
