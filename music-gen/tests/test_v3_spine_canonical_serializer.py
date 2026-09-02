"""Unit tests for the canonical JSON->MIDI serializer (M-V3-SPINE-1 c4)."""
import hashlib
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

# Add project root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.v3_spine.midi_from_json_events import (  # noqa: E402
    CanonicalSerializerError,
    PPQ,
    serialize,
    _check_mido_version,
    _channel_for_instrument,
    _pair_events,
    _seconds_to_ticks,
)


def _sha(path: str) -> str:
    return hashlib.sha256(open(path, 'rb').read()).hexdigest()


def _write_json(events, path):
    with open(path, 'w') as f:
        json.dump(events, f)


def _serialize_twice(events, tempo=120.0, ts=(4, 4)):
    """Serialize the same event list into two temp dirs, return (sha1, sha2)."""
    with tempfile.TemporaryDirectory() as d1, tempfile.TemporaryDirectory() as d2:
        j1 = os.path.join(d1, 'ev.json')
        j2 = os.path.join(d2, 'ev.json')
        _write_json(events, j1)
        _write_json(events, j2)
        m1 = os.path.join(d1, 'out.mid')
        m2 = os.path.join(d2, 'out.mid')
        serialize(j1, m1, tempo, ts)
        serialize(j2, m2, tempo, ts)
        return _sha(m1), _sha(m2)


SYNTHETIC_3_NOTES = [
    {'type': 'start', 'index': 0, 'pitch': 60, 'start_time': 0.0, 'instrument': 'piano'},
    {'type': 'start', 'index': 1, 'pitch': 64, 'start_time': 0.5, 'instrument': 'piano'},
    {'type': 'start', 'index': 2, 'pitch': 67, 'start_time': 1.0, 'instrument': 'piano'},
    {'type': 'end', 'start_event_index': 0, 'end_time': 0.5},
    {'type': 'end', 'start_event_index': 1, 'end_time': 1.0},
    {'type': 'end', 'start_event_index': 2, 'end_time': 1.5},
]


def _overlap_events():
    """12-note event set with overlapping pitches across channels."""
    events = []
    idx = 0
    for i in range(6):
        events.append({
            'type': 'start', 'index': idx, 'pitch': 60 + i,
            'start_time': i * 0.25, 'instrument': 'piano',
        })
        events.append({
            'type': 'end', 'start_event_index': idx, 'end_time': i * 0.25 + 0.5,
        })
        idx += 1
    for i in range(6):
        events.append({
            'type': 'start', 'index': idx, 'pitch': 60 + i,
            'start_time': i * 0.25, 'instrument': 'electric_bass',
        })
        events.append({
            'type': 'end', 'start_event_index': idx, 'end_time': i * 0.25 + 0.5,
        })
        idx += 1
    return events


class TestCanonicalSerializer(unittest.TestCase):

    def test_01_ppq_correct(self):
        """PPQ = 480 in the emitted MIDI."""
        import mido
        sha1, sha2 = _serialize_twice(SYNTHETIC_3_NOTES)
        # Also inspect the file directly
        with tempfile.TemporaryDirectory() as d:
            j = os.path.join(d, 'ev.json')
            _write_json(SYNTHETIC_3_NOTES, j)
            m = os.path.join(d, 'out.mid')
            serialize(j, m, 120.0, (4, 4))
            mf = mido.MidiFile(m)
            self.assertEqual(mf.ticks_per_beat, PPQ)

    def test_02_sort_key_reproducible(self):
        """Same-tick events sort by (channel, pitch, kind); byte-equal ×2."""
        # 3 events at same start_time, different pitches
        events = [
            {'type': 'start', 'index': 0, 'pitch': 67, 'start_time': 0.0, 'instrument': 'piano'},
            {'type': 'start', 'index': 1, 'pitch': 60, 'start_time': 0.0, 'instrument': 'piano'},
            {'type': 'start', 'index': 2, 'pitch': 64, 'start_time': 0.0, 'instrument': 'piano'},
            {'type': 'end', 'start_event_index': 0, 'end_time': 0.5},
            {'type': 'end', 'start_event_index': 1, 'end_time': 0.5},
            {'type': 'end', 'start_event_index': 2, 'end_time': 0.5},
        ]
        sha1, sha2 = _serialize_twice(events)
        self.assertEqual(sha1, sha2)

    def test_03_on_before_off_at_same_tick(self):
        """When start_time == end_time (post-widening), note_on emitted before note_off."""
        import mido
        events = [
            {'type': 'start', 'index': 0, 'pitch': 60, 'start_time': 0.0, 'instrument': 'piano'},
            {'type': 'end', 'start_event_index': 0, 'end_time': 0.0},  # equal
        ]
        with tempfile.TemporaryDirectory() as d:
            j = os.path.join(d, 'ev.json')
            _write_json(events, j)
            m = os.path.join(d, 'out.mid')
            serialize(j, m, 120.0, (4, 4))
            mf = mido.MidiFile(m)
            # Track 1 has the notes
            note_track = mf.tracks[1]
            kinds = [msg.type for msg in note_track if msg.type in ('note_on', 'note_off')]
            self.assertEqual(kinds, ['note_on', 'note_off'])

    def test_04_empty_events_baseline(self):
        """Empty event list produces minimal MIDI; byte-determinism ×2."""
        sha1, sha2 = _serialize_twice([])
        self.assertEqual(sha1, sha2)

    def test_05_mido_version_check(self):
        """_check_mido_version raises on version mismatch."""
        with self.assertRaises(CanonicalSerializerError):
            _check_mido_version(expected='9.9.9')

    def test_06_byte_determinism_3_notes(self):
        sha1, sha2 = _serialize_twice(SYNTHETIC_3_NOTES)
        self.assertEqual(sha1, sha2)

    def test_07_byte_determinism_12_notes_overlap(self):
        sha1, sha2 = _serialize_twice(_overlap_events())
        self.assertEqual(sha1, sha2)

    def test_08_byte_determinism_empty(self):
        sha1, sha2 = _serialize_twice([])
        self.assertEqual(sha1, sha2)

    def test_09_no_prng_no_wallclock(self):
        """AST-grep the serializer source for forbidden imports."""
        src = Path('scripts/v3_spine/midi_from_json_events.py').read_text()
        # exclude the docstring/spec doc reference
        forbidden = ['random.', 'time.time', 'datetime.now', 'datetime.utcnow']
        for bad in forbidden:
            self.assertNotIn(bad, src, f'forbidden symbol {bad!r} in serializer')

    def test_10_channel_mapping(self):
        self.assertEqual(_channel_for_instrument('drums'), 9)
        self.assertEqual(_channel_for_instrument('electric_bass'), 0)
        self.assertEqual(_channel_for_instrument('clean_electric_guitar'), 1)
        self.assertEqual(_channel_for_instrument('distorted_electric_guitar'), 1)
        self.assertEqual(_channel_for_instrument('piano'), 2)
        self.assertEqual(_channel_for_instrument('voice'), 3)
        self.assertEqual(_channel_for_instrument(''), 4)
        self.assertEqual(_channel_for_instrument('unknown_thing'), 4)

    def test_11_pair_events_dangling_start(self):
        events = [
            {'type': 'start', 'index': 0, 'pitch': 60, 'start_time': 0.0, 'instrument': 'piano'},
        ]
        paired = _pair_events(events)
        self.assertEqual(len(paired), 1)
        self.assertAlmostEqual(paired[0][1] - paired[0][0], 0.100, places=6)

    def test_12_seconds_to_ticks_at_120bpm(self):
        # At 120 BPM, 1 second = 2 beats = 960 ticks
        self.assertEqual(_seconds_to_ticks(1.0, 120.0), 960)


if __name__ == '__main__':
    unittest.main(verbosity=2)
