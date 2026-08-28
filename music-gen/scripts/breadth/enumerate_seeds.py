#!/usr/bin/env -S /usr/bin/python3
# ---
# created: 2026-08-28T11:20:00Z
# cycle: 10
# run_id: run-2026-08-28T040704Z
# agent: worker
# milestone: M-INGEST-1/breadth-second-seeds
# ---
"""Enumerate on-disk audio candidates for pipeline-breadth cycle 10.

Emits data/breadth/seed_enumeration.tsv with columns:
    path, duration_s, sr, channels, sha256, provenance_class

provenance_class is one of:
    synth_ground_truth  -- M-SEP-1 fluidsynth-rendered mixes / GT stems.
    synth_seed_gen      -- scripts/ingest/seed_gen.py CC-0 sines.
    unknown             -- any other on-disk audio (should be empty when
                           egress is blocked; still listed for candor).

Interpreter: /usr/bin/python3.
"""
from __future__ import annotations

import hashlib
import sys
import wave
from pathlib import Path

assert sys.executable == '/usr/bin/python3', sys.executable

ROOT = Path('/home/user/long-exposure-runs/music-gen')
ROOTS = [
    ROOT / 'corpus' / 'seed',
    ROOT / 'corpus' / 'ratings',
    ROOT / 'data' / 'ingestion' / 'seed',
    ROOT / 'data' / 'separation' / 'synth_mix',
]
AUDIO_EXTS = {'.wav', '.flac', '.mp3', '.m4a', '.ogg', '.opus'}
OUT_TSV = ROOT / 'data' / 'breadth' / 'seed_enumeration.tsv'


def classify_provenance(p: Path) -> str:
    s = str(p)
    if '/data/ingestion/seed/' in s:
        return 'synth_seed_gen'
    if '/data/separation/synth_mix/' in s:
        return 'synth_ground_truth'
    if '/corpus/ratings/' in s or '/corpus/seed/' in s:
        return 'unknown'
    return 'unknown'


def probe(p: Path) -> dict:
    # soundfile handles float32 WAVs (M-SEP-1 ground truth) and PCM16 uniformly.
    import soundfile as sf
    info = sf.info(str(p))
    sr = info.samplerate
    nch = info.channels
    dur = info.frames / sr
    sha = hashlib.sha256(p.read_bytes()).hexdigest()
    return dict(sr=sr, channels=nch, duration_s=dur, sha256=sha)


def main() -> None:
    rows: list[dict] = []
    for r in ROOTS:
        if not r.exists():
            continue
        for f in sorted(r.rglob('*')):
            if not (f.is_file() and f.suffix.lower() in AUDIO_EXTS):
                continue
            try:
                info = probe(f)
            except Exception as e:
                info = dict(sr=-1, channels=-1, duration_s=-1.0, sha256=f'error:{type(e).__name__}')
            row = dict(
                path=str(f.relative_to(ROOT)),
                duration_s=f'{info["duration_s"]:.3f}',
                sr=info['sr'],
                channels=info['channels'],
                sha256=info['sha256'],
                provenance_class=classify_provenance(f),
            )
            rows.append(row)

    OUT_TSV.parent.mkdir(parents=True, exist_ok=True)
    cols = ['path', 'duration_s', 'sr', 'channels', 'sha256', 'provenance_class']
    with OUT_TSV.open('w') as fh:
        fh.write('\t'.join(cols) + '\n')
        for r in rows:
            fh.write('\t'.join(str(r[c]) for c in cols) + '\n')
    print(f'wrote {OUT_TSV} with {len(rows)} rows')
    for r in rows:
        print(f'  {r["provenance_class"]:20s} {r["duration_s"]:>8s}s sr={r["sr"]}ch={r["channels"]} {r["path"]}')


if __name__ == '__main__':
    main()
