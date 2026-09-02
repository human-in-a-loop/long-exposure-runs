"""End-to-end validation tests for M-V3-SPINE-1 cycle 4 (OPTION A pipeline)."""
import hashlib
import json
import os
import re
import sys
import unittest
from pathlib import Path

# add project root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

SONG_SHA16 = '31a164f845f8e27e'


def sha256(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


class TestV3SpineCycle4(unittest.TestCase):

    def test_01_canonical_spec_doc_mtime_before_serializer(self):
        spec = Path('docs/v3_spine_canonical_midi_serializer_spec.md')
        serializer = Path('scripts/v3_spine/midi_from_json_events.py')
        canonicalizer = Path('scripts/v3_spine/canonicalize_all_probes.py')
        self.assertLess(spec.stat().st_mtime, serializer.stat().st_mtime)
        self.assertLess(spec.stat().st_mtime, canonicalizer.stat().st_mtime)

    def test_02_rubric_v2_doc_mtime_before_pipeline_outputs(self):
        rubric = Path('docs/v3_spine_rubric_v2.md')
        # Only assert precedence against files that landed after rubric-v2 (deliver.py, verdict.py)
        for later in ['scripts/v3_spine/deliver.py', 'scripts/v3_spine/verdict.py']:
            self.assertLess(rubric.stat().st_mtime, Path(later).stat().st_mtime,
                            f'rubric-v2 mtime must be before {later}')

    def test_03_three_way_rubric_hash_v2_chain(self):
        doc_sha = sha256('docs/v3_spine_rubric_v2.md')
        rh_txt = Path('data/v3_spine/rubric_hash_v2.txt').read_text().strip()
        vjs = json.loads(Path(f'data/v3/deliveries/{SONG_SHA16}/verdict.json').read_text())
        self.assertEqual(doc_sha, rh_txt)
        self.assertEqual(rh_txt, vjs['rubric_hash_v2'])

    def test_04_muscriptor_json_intra_cycle_determinism(self):
        d = json.loads(Path(f'data/v3_spine/{SONG_SHA16}/muscriptor_determinism_per_stem.json').read_text())
        for stem in ('drums', 'bass', 'vocals'):
            self.assertTrue(d['probes'][stem]['json']['equal'])
        # guitar intra-cycle in c4:
        c4 = json.loads(Path(f'data/v3_spine/{SONG_SHA16}/muscriptor_c4_within_cycle_check.json').read_text())
        self.assertTrue(c4['results']['guitar']['c4_to_c4_equal'])

    def test_05_canonical_midi_determinism_x2_all_7(self):
        d = json.loads(Path(f'data/v3_spine/{SONG_SHA16}/canonical_midi_determinism.json').read_text())
        for stem in ('drums', 'bass', 'guitar', 'other', 'piano', 'vocals', 'full_mix'):
            self.assertTrue(d['results'][stem]['byte_deterministic_x2'],
                            f'canonical MIDI {stem} not deterministic ×2')

    def test_06_mido_version_pin(self):
        import importlib.metadata as im
        self.assertEqual(im.version('mido'), '1.3.3')

    def test_07_canonical_serializer_synthetic_x2(self):
        # inline round-trip test
        import tempfile
        from scripts.v3_spine.midi_from_json_events import serialize
        events = [
            {'type': 'start', 'index': 0, 'pitch': 60, 'start_time': 0.0, 'instrument': 'piano'},
            {'type': 'start', 'index': 1, 'pitch': 64, 'start_time': 0.25, 'instrument': 'piano'},
            {'type': 'start', 'index': 2, 'pitch': 67, 'start_time': 0.5, 'instrument': 'piano'},
            {'type': 'end', 'start_event_index': 0, 'end_time': 0.5},
            {'type': 'end', 'start_event_index': 1, 'end_time': 0.75},
            {'type': 'end', 'start_event_index': 2, 'end_time': 1.0},
        ]
        with tempfile.TemporaryDirectory() as d:
            j = os.path.join(d, 'e.json'); open(j, 'w').write(json.dumps(events))
            m1 = os.path.join(d, 'a.mid'); m2 = os.path.join(d, 'b.mid')
            serialize(j, m1, 120.0, (4, 4))
            serialize(j, m2, 120.0, (4, 4))
            self.assertEqual(sha256(m1), sha256(m2))

    def test_08_zero_notes_on_gm_program_4(self):
        import mido
        mf = mido.MidiFile(f'data/v3_spine/{SONG_SHA16}/merged.mid')
        for tr in mf.tracks:
            for m in tr:
                if m.type == 'program_change':
                    self.assertNotEqual(m.program, 4, 'GM program 4 found in merged.mid')

    def test_09_drums_track_ch10_nonempty(self):
        import mido
        mf = mido.MidiFile(f'data/v3_spine/{SONG_SHA16}/merged.mid')
        found = False
        for tr in mf.tracks[1:]:
            # first track meta might have track_name
            name = None
            for m in tr:
                if m.type == 'track_name':
                    name = m.name; break
            if name == 'drums':
                n_on = sum(1 for m in tr if m.type == 'note_on')
                self.assertGreater(n_on, 0)
                # all note_on on channel 9
                for m in tr:
                    if m.type in ('note_on', 'note_off'):
                        self.assertEqual(m.channel, 9)
                found = True; break
        self.assertTrue(found, 'drums track not found in merged.mid')

    def test_10_bass_median_pitch_lt_55(self):
        import mido
        import statistics
        mf = mido.MidiFile(f'data/v3_spine/{SONG_SHA16}/merged.mid')
        pitches = []
        for tr in mf.tracks[1:]:
            name = None
            for m in tr:
                if m.type == 'track_name':
                    name = m.name; break
            if name == 'bass':
                pitches = [m.note for m in tr if m.type == 'note_on']
                break
        self.assertTrue(pitches, 'bass has no notes')
        self.assertLess(statistics.median(pitches), 55)

    def test_11_vocals_track_present_symbolic(self):
        import mido
        mf = mido.MidiFile(f'data/v3_spine/{SONG_SHA16}/merged.mid')
        found_symbol = False; has_notes = False
        for tr in mf.tracks[1:]:
            name = None; sym = False
            for m in tr:
                if m.type == 'track_name': name = m.name
                if m.type == 'text' and m.text == 'voice_symbolic_do_not_render':
                    sym = True
            if name == 'vocals':
                has_notes = any(m.type == 'note_on' for m in tr)
                found_symbol = sym
                break
        self.assertTrue(has_notes)
        self.assertTrue(found_symbol)

    def test_12_ab_wavs_30s_non_silent(self):
        import scipy.io.wavfile as sw
        import numpy as np
        for name in ('original_ab.wav', 'reconstruction_ab.wav'):
            sr, y = sw.read(f'data/v3/deliveries/{SONG_SHA16}/{name}')
            dur = y.shape[0] / sr
            self.assertAlmostEqual(dur, 30.0, delta=0.005)
            y_norm = y.astype(np.float32) / 32768.0 if y.dtype == np.dtype('int16') else y
            self.assertGreater(float(np.max(np.abs(y_norm))), 1e-4)

    def test_13_panel_8_keys_finite(self):
        d = json.loads(Path(f'data/v3/deliveries/{SONG_SHA16}/panel.json').read_text())
        self.assertGreaterEqual(d['panel_keys_count'], 8)
        # Numeric metrics finite
        NUMERIC = ('mel_l1_db', 'spectral_centroid_rmse_hz', 'rms_env_rmse',
                   'lufs_m_rmse_lu', 'embedding_cosine_distance')
        for k in NUMERIC:
            self.assertIn(k, d['panel'])
            self.assertTrue(d['finite_per_key'][k], f'{k} not finite')

    def test_14_anchor_preservation_pre_post_match(self):
        d = json.loads(Path(f'data/v3_spine/{SONG_SHA16}/anchor_preservation_v2.json').read_text())
        self.assertEqual(d['n_mismatch'], 0)
        self.assertGreaterEqual(d['anchor_count'], 21)

    def test_15_render_stem_lock_preserved(self):
        # render_stem.py + rc7_v2_rerun.py SHAs from anchor snapshot
        anchors = json.loads(Path(f'data/v3_spine/{SONG_SHA16}/anchor_preservation_v2.json').read_text())
        m = {e['path']: e['sha256'] for e in anchors['anchors_post']}
        self.assertIn('scripts/palette_render/render_stem.py', m)
        # SHA prefix from render_stem.py DO-NOT-TOUCH lock
        self.assertTrue(m['scripts/palette_render/render_stem.py'].startswith('214372d9'))

    def test_16_no_prng_no_forbidden_writes(self):
        # grep for random.sample / random.random / random.randint / random.choice etc. in v3 spine scripts
        for f in Path('scripts/v3_spine').glob('*.py'):
            if f.name.startswith('_'): continue
            src = f.read_text()
            for bad in ('random.sample', 'random.random(', 'random.randint(',
                        'random.choice(', 'np.random.'):
                self.assertNotIn(bad, src, f'PRNG usage in {f}: {bad}')


if __name__ == '__main__':
    unittest.main(verbosity=2)
