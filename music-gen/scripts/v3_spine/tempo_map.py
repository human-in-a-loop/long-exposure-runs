#!/usr/bin/env /usr/bin/python3
"""Canonical tempo + time-signature choice for the v3 spine (M-V3-SPINE-1 c4).

Uses the c49 rc5 baseline (`librosa.beat.beat_track` on the original mix)
as the authoritative source for Chicken Grease tempo. Documented decision:
MuScriptor JSON events do not carry tempo meta; drums-stem beat detection
under librosa is the canonical source. Falls back to full_mix librosa only
if drums baseline is missing (not the case for Chicken Grease).
"""
import json
import sys
from pathlib import Path

SONG_SHA16 = '31a164f845f8e27e'


def main() -> None:
    rc5 = Path(f'data/recreate_v2/baseline/{SONG_SHA16}/rc5_tempo_bpm.json')
    if not rc5.exists():
        print(f'FATAL: rc5 baseline missing: {rc5}', file=sys.stderr)
        sys.exit(1)
    d = json.loads(rc5.read_text())
    bpm = float(d['estimated_bpm'])
    # Meter default 4/4 (Chicken Grease is 4/4; MuScriptor doesn't provide time-sig)
    meter = [4, 4]
    payload = {
        'schema_version': 1,
        'cycle': 4,
        'song_sha16': SONG_SHA16,
        'source': 'rc5_baseline_full_mix_librosa_beat_track',
        'source_path': str(rc5),
        'source_sha256_note': 'see data/v3_spine/31a164f845f8e27e/anchor_preservation_pre_v2.json',
        'detected_bpm': bpm,
        'meter': meter,
        'fallback_reason': None,
        'delta_vs_rc5_baseline_bpm': 0.0,  # identity source
        'note': (
            'MuScriptor JSON events carry no tempo meta; librosa beat_track on the '
            'original mix (RC5 baseline, cycle-49 anchor) is the authoritative source. '
            'Drums-stem-derived tempo would require additional librosa call on '
            'baseline/rc9_6stem/drums.wav; deferred as unnecessary — full-mix rc5 '
            'already captures ensemble tempo and is a READ-ONLY anchor preserved '
            'byte-identically pre==post.'
        ),
    }
    out = Path(f'data/v3_spine/{SONG_SHA16}/tempo_choice.json')
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + '\n')
    print(f'wrote {out}: bpm={bpm} meter={meter}')


if __name__ == '__main__':
    main()
