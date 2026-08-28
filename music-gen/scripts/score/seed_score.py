#!/usr/bin/env python3
# M-SCORE-1/round-trip — 8-bar hand-authored seed score generator.
#
# Deterministic 8-bar drums + bass + piano seed in C major, 4/4, 120 BPM.
# Used by tests/test_score_bridge.py sections 1 and 2 (round-trip
# determinism + note preservation).
#
# Rationale for hand-authoring: a small, fully-specified seed lets us
# tell the difference between mscore3 non-determinism (which the
# scrubber must handle) and note-event mutation (which the bridge must
# NEVER do). Every note here has a documented pitch, onset, and
# duration; no unpitched percussion (mscore3's percussion round-trip
# needs channel-10 handling that is out of scope for the seed).

import sys
assert sys.executable == '/usr/bin/python3', sys.executable

from pathlib import Path

from music21 import stream, note, meter, tempo as m21tempo, instrument, \
    metadata, duration as m21duration, key


# Seed events: (part_name, bar_index_0based, beat_offset_in_bar, duration_ql, midi_pitch)
# 8 bars, 4/4, 120 BPM (so 1 quarter = 0.5 s).
# Piano: I-vi-IV-V progression (2 bars per chord voicing on top of a
#   quarter-note bassline).
# Bass: quarter-note root motion (C-A-F-G, C-A-F-G).
# Piano melody: whole-note chord tones on downbeats.
SEED_EVENTS = []

# Bass part: C2, A1, F1, G1 repeated across 8 bars, quarter notes on
# every beat.
_BASS_ROOTS = [36, 33, 29, 31, 36, 33, 29, 31]  # C2, A1, F1, G1
for bar in range(8):
    root = _BASS_ROOTS[bar]
    for beat in range(4):
        SEED_EVENTS.append(("bass", bar, float(beat), 1.0, root))

# Piano part: whole-note chord (root + 3rd + 5th) on beat 1 of each bar.
# Chord voicings for C, Am, F, G:
_PIANO_CHORDS = [
    [60, 64, 67],  # C: C-E-G
    [57, 60, 64],  # Am: A-C-E
    [53, 57, 60],  # F: F-A-C
    [55, 59, 62],  # G: G-B-D
]
for bar in range(8):
    voicing = _PIANO_CHORDS[bar % 4]
    for p in voicing:
        SEED_EVENTS.append(("piano", bar, 0.0, 4.0, p))

# Drums are a separate matter — mscore3 percussion round-trip requires
# a Percussion clef and specific pitch mapping. For seed determinism
# we author drums as pitched notes on a low register, labelled
# "drums", which lets mscore3 handle them uniformly. This is a seed
# convention, NOT the pattern for real drum tracks (which come from
# basic-pitch on the drums stem — currently F1=0 there).
# Kick on beats 1 & 3, snare-analog on beats 2 & 4.
for bar in range(8):
    SEED_EVENTS.append(("drums", bar, 0.0, 1.0, 36))  # kick
    SEED_EVENTS.append(("drums", bar, 1.0, 1.0, 38))  # snare
    SEED_EVENTS.append(("drums", bar, 2.0, 1.0, 36))  # kick
    SEED_EVENTS.append(("drums", bar, 3.0, 1.0, 38))  # snare


def build_seed_score(tempo_bpm: float = 120.0) -> stream.Score:
    """Build the 8-bar deterministic seed as a music21 Score."""
    sc = stream.Score()
    md = metadata.Metadata()
    md.title = ""
    md.composer = ""
    sc.insert(0, md)

    parts_by_name = {}
    for part_name in ("bass", "piano", "drums"):
        p = stream.Part(id=part_name)
        p.partName = part_name
        p.partAbbreviation = part_name[:3]
        if part_name == "drums":
            p.insert(0, instrument.Percussion())
        elif part_name == "bass":
            p.insert(0, instrument.ElectricBass())
        else:
            p.insert(0, instrument.Piano())
        p.insert(0, meter.TimeSignature("4/4"))
        p.insert(0, key.KeySignature(0))
        p.insert(0, m21tempo.MetronomeMark(number=float(tempo_bpm)))
        parts_by_name[part_name] = p

    for part_name, bar, beat, dur_ql, midi_pitch in SEED_EVENTS:
        onset_ql = bar * 4.0 + beat  # 4 quarter-notes per bar in 4/4
        n = note.Note(midi=int(midi_pitch))
        n.duration = m21duration.Duration(dur_ql)
        n.volume.velocity = 90
        parts_by_name[part_name].insert(onset_ql, n)

    for name in ("bass", "piano", "drums"):
        sc.append(parts_by_name[name])
    return sc


def write_seed_xml(out_xml_path) -> Path:
    """Write the 8-bar seed to a MusicXML file at the given path."""
    out_xml_path = Path(out_xml_path)
    out_xml_path.parent.mkdir(parents=True, exist_ok=True)
    sc = build_seed_score()
    sc.write("musicxml", fp=str(out_xml_path))
    return out_xml_path


def seed_note_multiset():
    """Return the seed's expected note multi-set as a sorted tuple of
    (part_name, absolute_seconds, duration_seconds, midi_pitch).

    Used by test §2 to assert note-preservation after round-trip.
    Uses 120 BPM => quarter=0.5s.
    """
    ql_to_s = 0.5  # at 120 BPM
    items = []
    for part_name, bar, beat, dur_ql, midi_pitch in SEED_EVENTS:
        onset_s = (bar * 4.0 + beat) * ql_to_s
        dur_s = dur_ql * ql_to_s
        items.append((part_name, round(onset_s, 6), round(dur_s, 6), int(midi_pitch)))
    return tuple(sorted(items))


if __name__ == "__main__":
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("data/score/seed_8bar.musicxml")
    print(write_seed_xml(out))
    print(f"{len(SEED_EVENTS)} note events authored")
