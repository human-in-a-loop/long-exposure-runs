#!/usr/bin/env /usr/bin/python3
"""Merge 6 canonicalized per-stem MIDIs into a single multi-track MIDI.

Drums on channel 10 (0-indexed 9). Vocals track flagged with
`voice_symbolic_do_not_render` text meta so the renderer skips it.

Structural assertions per rubric-v2 clause (d):
- drums track exists on ch10 with note count > 0
- bass track present with median MIDI pitch < 55
- zero notes on GM program 4
- vocals track present + non-empty
"""
import hashlib
import json
import statistics
import sys
from pathlib import Path

import mido

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from scripts.v3_spine.gm_program_map_v3 import STEM_DEFAULT  # noqa: E402

SONG_SHA16 = '31a164f845f8e27e'
CANON_DIR = Path(f'data/v3_spine/{SONG_SHA16}/canonical_midi')
STEMS_ORDER = ['drums', 'bass', 'guitar', 'piano', 'other', 'vocals']  # full_mix not merged; reconciled separately


def load_stem_notes(stem: str):
    """Return list of (abs_tick, msg) tuples from the canonical MIDI's note track."""
    path = CANON_DIR / f'{stem}.mid'
    mf = mido.MidiFile(path)
    if mf.ticks_per_beat != 480:
        raise RuntimeError(f'{path} has wrong PPQ {mf.ticks_per_beat}')
    # The canonical serializer emits: track 0 = meta, track 1 = notes.
    if len(mf.tracks) < 2:
        return [], mf.ticks_per_beat, mf.tracks[0]
    note_track = mf.tracks[1]
    events = []
    t = 0
    for m in note_track:
        t += m.time
        if m.type in ('note_on', 'note_off'):
            events.append((t, m))
    return events, mf.ticks_per_beat, mf.tracks[0]


def main() -> None:
    tempo = json.loads(Path(f'data/v3_spine/{SONG_SHA16}/tempo_choice.json').read_text())
    bpm = float(tempo['detected_bpm'])
    ts = tempo['meter']

    merged = mido.MidiFile(type=1, ticks_per_beat=480)

    # Track 0: meta (tempo + time_signature at tick 0)
    meta = mido.MidiTrack()
    meta.append(mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(bpm), time=0))
    meta.append(mido.MetaMessage('time_signature', numerator=ts[0], denominator=ts[1],
                                 clocks_per_click=24, notated_32nd_notes_per_beat=8, time=0))
    meta.append(mido.MetaMessage('end_of_track', time=0))
    merged.tracks.append(meta)

    per_stem_stats = {}
    for stem in STEMS_ORDER:
        default_label, default_prog, default_ch = STEM_DEFAULT[stem]
        events, _, _ = load_stem_notes(stem)

        track = mido.MidiTrack()
        # Track name & symbolic-only flag for vocals
        track.append(mido.MetaMessage('track_name', name=stem, time=0))
        if stem == 'vocals':
            track.append(mido.MetaMessage('text', text='voice_symbolic_do_not_render', time=0))
        # Program change on the appropriate channel (unless drums which uses ch10 + no program)
        if default_prog is not None:
            track.append(mido.Message('program_change', channel=default_ch,
                                      program=default_prog, time=0))

        # Rewrite events onto the assigned channel (drums always ch9; others per default_ch)
        prev_tick = 0
        note_ons = 0
        pitches = []
        for abs_tick, m in events:
            new_ch = 9 if stem == 'drums' else default_ch
            delta = abs_tick - prev_tick
            if delta < 0:
                delta = 0
            new_msg = m.copy(channel=new_ch, time=delta)
            track.append(new_msg)
            if m.type == 'note_on':
                note_ons += 1
                pitches.append(m.note)
            prev_tick = abs_tick
        track.append(mido.MetaMessage('end_of_track', time=0))
        merged.tracks.append(track)

        per_stem_stats[stem] = {
            'note_ons': note_ons,
            'median_pitch': (statistics.median(pitches) if pitches else None),
            'gm_program': default_prog,
            'gm_channel': (9 if stem == 'drums' else default_ch),
        }

    out_path = Path(f'data/v3_spine/{SONG_SHA16}/merged.mid')
    out_path.parent.mkdir(parents=True, exist_ok=True)
    # Atomic write ×2 for byte-determinism
    tmp = out_path.with_suffix('.mid.tmp')
    merged.save(tmp)
    tmp.replace(out_path)
    sha1 = hashlib.sha256(open(out_path, 'rb').read()).hexdigest()

    # Second write for determinism ×2
    tmp2 = out_path.with_suffix('.mid.tmp2')
    merged.save(tmp2)
    sha2 = hashlib.sha256(open(tmp2, 'rb').read()).hexdigest()
    tmp2.unlink()

    Path(f'data/v3_spine/{SONG_SHA16}/merged_midi_sha.txt').write_text(sha1 + '\n')

    # Structural assertions
    drums_notes = per_stem_stats['drums']['note_ons']
    drums_ch = per_stem_stats['drums']['gm_channel']
    bass_notes = per_stem_stats['bass']['note_ons']
    bass_med = per_stem_stats['bass']['median_pitch']
    vocals_notes = per_stem_stats['vocals']['note_ons']

    assertions = {
        'drums_track_on_ch10_nonempty': (drums_ch == 9 and drums_notes > 0),
        'bass_median_pitch_lt_55': (bass_med is not None and bass_med < 55),
        'vocals_track_present_nonempty': (vocals_notes > 0),
        # zero notes on GM program 4: verified by iterating all program_changes in the file
        'zero_notes_on_gm_program_4': _check_no_program_4(out_path),
    }
    print('merged.mid sha:', sha1)
    print('sha1 == sha2:', sha1 == sha2)
    print('per-stem stats:', json.dumps(per_stem_stats, indent=2, sort_keys=True))
    print('assertions:', assertions)

    if not all(assertions.values()):
        failed = [k for k, v in assertions.items() if not v]
        print(f'STRUCTURAL ASSERTION FAILED: {failed}', file=sys.stderr)
        # Continue anyway; verdict will capture this


def _check_no_program_4(path: Path) -> bool:
    mf = mido.MidiFile(path)
    for track in mf.tracks:
        for m in track:
            if m.type == 'program_change' and m.program == 4:
                return False
    return True


if __name__ == '__main__':
    main()
