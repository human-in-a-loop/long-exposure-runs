#!/usr/bin/env /usr/bin/python3
"""Render each non-vocal track from merged.mid via fluidsynth to per-track WAVs.

Vocals track (channel 3 with text meta `voice_symbolic_do_not_render`) is
excluded from render. Byte-determinism ×2 per WAV via re-render into fresh
temp dir.
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import mido

SONG_SHA16 = '31a164f845f8e27e'
SF2 = '/usr/share/sounds/sf2/FluidR3_GM.sf2'
MERGED = Path(f'data/v3_spine/{SONG_SHA16}/merged.mid')
OUT_DIR = Path(f'data/v3_spine/{SONG_SHA16}/render/per_track')

# Tracks to render (channels + names). Vocals excluded per symbolic-only flag.
# From merged.mid: drums ch9, bass ch0, guitar ch1, piano ch2, other ch4, vocals ch3.
TRACKS_TO_RENDER = [
    ('drums', 9),
    ('bass', 0),
    ('guitar', 1),
    ('piano', 2),
    ('other', 4),
]


def split_track_to_single_track_mid(source_mid: Path, track_name: str, out_mid: Path) -> None:
    """Extract a single named track from source_mid into a new single-track type-1 MIDI.

    Preserves the tempo/TS meta from track 0 plus the target track.
    """
    mf = mido.MidiFile(source_mid)
    new_mf = mido.MidiFile(type=1, ticks_per_beat=mf.ticks_per_beat)

    # Copy meta track 0
    new_mf.tracks.append(mf.tracks[0])
    # Find target track by name
    for tr in mf.tracks[1:]:
        # Track name is the first meta message
        name = None
        for m in tr:
            if m.type == 'track_name':
                name = m.name
                break
        if name == track_name:
            new_mf.tracks.append(tr)
            break
    out_mid.parent.mkdir(parents=True, exist_ok=True)
    tmp = out_mid.with_suffix('.mid.tmp')
    new_mf.save(tmp)
    tmp.replace(out_mid)


def fluidsynth_render(midi_path: Path, wav_path: Path) -> None:
    """Render midi to wav via fluidsynth CLI."""
    env = os.environ.copy()
    env.update({
        'PYTHONHASHSEED': '0', 'SOURCE_DATE_EPOCH': '1756463424',
        'TZ': 'UTC', 'LC_ALL': 'C.UTF-8',
    })
    wav_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        'fluidsynth', '-ni', '-F', str(wav_path),
        '-r', '44100', '-o', 'synth.cpu-cores=1',
        '-o', 'synth.reverb.active=false', '-o', 'synth.chorus.active=false',
        SF2, str(midi_path),
    ]
    r = subprocess.run(cmd, env=env, capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f'fluidsynth failed rc={r.returncode}: {r.stderr.decode()[-500:]}')


def sha256_file(p: Path) -> str:
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    results = {}
    for name, _ch in TRACKS_TO_RENDER:
        # Split the merged.mid to just this track
        single_mid = OUT_DIR / f'{name}.mid'
        split_track_to_single_track_mid(MERGED, name, single_mid)

        # Render twice for byte-determinism
        with tempfile.TemporaryDirectory(prefix=f'render_{name}_r1_') as d1:
            wav1 = Path(d1) / f'{name}.wav'
            fluidsynth_render(single_mid, wav1)
            sha1 = sha256_file(wav1)
            final_wav = OUT_DIR / f'{name}.wav'
            shutil.copy2(wav1, final_wav)
        with tempfile.TemporaryDirectory(prefix=f'render_{name}_r2_') as d2:
            wav2 = Path(d2) / f'{name}.wav'
            fluidsynth_render(single_mid, wav2)
            sha2 = sha256_file(wav2)
        results[name] = {
            'wav_path': str(final_wav),
            'wav_sha256_run1': sha1,
            'wav_sha256_run2': sha2,
            'byte_deterministic_x2': (sha1 == sha2),
        }
        print(f'{name:10s} sha1={sha1[:16]} sha2={sha2[:16]} equal={sha1==sha2}')

    out_json = Path(f'data/v3_spine/{SONG_SHA16}/render/per_track_determinism.json')
    out_json.write_text(json.dumps({
        'schema_version': 1, 'cycle': 4, 'song_sha16': SONG_SHA16,
        'sf2_path': SF2, 'sf2_sha256': sha256_file(Path(SF2)),
        'results': results,
    }, indent=2, sort_keys=True) + '\n')
    print(f'wrote {out_json}')

    fails = [n for n, r in results.items() if not r['byte_deterministic_x2']]
    if fails:
        print(f'WARN: per-track WAV nondeterministic: {fails}', file=sys.stderr)


if __name__ == '__main__':
    main()
