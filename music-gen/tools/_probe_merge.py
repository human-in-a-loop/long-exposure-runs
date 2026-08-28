"""Probe merged-full-song bridge F1 measurement."""
import sys, os, hashlib, json
sys.path.insert(0, '.')
os.environ['OMP_NUM_THREADS'] = '1'
os.environ['MKL_NUM_THREADS'] = '1'
os.environ['OPENBLAS_NUM_THREADS'] = '1'

from pathlib import Path
import mido
import numpy as np
import mir_eval

from scripts.score.bridge import merge_stems_to_score, xml_to_midi

STEM_MIDIS = {
    'drums': Path('data/score/stems_from_bp/drums.mid'),
    'bass':  Path('data/score/stems_from_bp/bass.mid'),
    'other': Path('data/score/stems_from_bp/other.mid'),
}
OUT_XML = Path('data/score/merged_synth030s.musicxml')
OUT_MID = Path('data/score/merged_synth030s.mid')

merge_stems_to_score(STEM_MIDIS, OUT_XML, tempo_bpm=120.0, time_signature=(4,4))
print('merged xml sha:', hashlib.sha256(OUT_XML.read_bytes()).hexdigest()[:16])
xml_to_midi(OUT_XML, OUT_MID)
print('merged mid sha:', hashlib.sha256(OUT_MID.read_bytes()).hexdigest()[:16])

sidecar = json.loads(OUT_XML.with_name(OUT_XML.stem + '.parts_mapping.json').read_text())
parts_by_stem = sidecar['parts_by_stem']
print('sidecar parts_by_stem:', {k: len(v) for k, v in parts_by_stem.items()})


def extract_notes_per_track(mid_path):
    m = mido.MidiFile(str(mid_path))
    tpb = m.ticks_per_beat
    tempo = 500000
    for tr in m.tracks:
        for msg in tr:
            if msg.type == 'set_tempo':
                tempo = msg.tempo
                break
    sec_per_tick = (tempo / 1e6) / tpb
    result = []
    for i, tr in enumerate(m.tracks):
        active = {}; abs_t = 0; notes = []
        for msg in tr:
            abs_t += msg.time
            if msg.type == 'note_on' and msg.velocity > 0:
                active[(msg.channel, msg.note)] = abs_t
            elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                k = (msg.channel, msg.note)
                if k in active:
                    onset_ticks = active.pop(k)
                    onset_s = onset_ticks * sec_per_tick
                    off_s = abs_t * sec_per_tick
                    notes.append((onset_s, off_s, msg.note))
        result.append((i, notes))
    return result


def load_ref_jsonl(path):
    notes = []
    with open(path) as f:
        for ln in f:
            r = json.loads(ln)
            notes.append((float(r['onset_s']), float(r['offset_s']), int(r['pitch'])))
    return notes


def as_arrays(notes):
    if not notes:
        return np.empty((0, 2)), np.empty((0,))
    arr = np.array(notes, dtype=float)
    return arr[:, :2], arr[:, 2]


def f1(ref_notes, est_notes):
    ref_iv, ref_pitch = as_arrays(ref_notes)
    est_iv, est_pitch = as_arrays(est_notes)
    if len(ref_iv) == 0 and len(est_iv) == 0:
        return 1.0, 1.0, 1.0
    if len(ref_iv) == 0:
        return 0.0, 1.0, 0.0
    if len(est_iv) == 0:
        return 1.0, 0.0, 0.0
    p, r, fv, _ = mir_eval.transcription.precision_recall_f1_overlap(
        ref_iv, ref_pitch, est_iv, est_pitch,
        onset_tolerance=0.05, pitch_tolerance=0.5, offset_ratio=None)
    return p, r, fv


merged_tracks = extract_notes_per_track(OUT_MID)
print('merged tracks:', [(i, len(ns)) for i, ns in merged_tracks])

# Group tracks by stem using sidecar. Tracks are ordered:
# track 0 = meta; then non-meta tracks in the same order as parts in the score.
non_meta_tracks = merged_tracks[1:]

# Walk stems in sorted order (that's the order they were added to the score).
merged_by_stem = {}
cursor = 0
for stem in sorted(parts_by_stem.keys()):
    n_parts = len(parts_by_stem[stem])
    merged_by_stem[stem] = []
    for _ in range(n_parts):
        if cursor < len(non_meta_tracks):
            merged_by_stem[stem].extend(non_meta_tracks[cursor][1])
        cursor += 1
print('merged notes by stem:', {k: len(v) for k, v in merged_by_stem.items()})

REF_JSONL = {
    'drums': 'data/transcribe/reference/synth_030s/drums.reference.jsonl',
    'bass':  'data/transcribe/reference/synth_030s/bass.reference.jsonl',
    'other': 'data/transcribe/reference/synth_030s/other.reference.jsonl',
}
ref_by_stem = {stem: load_ref_jsonl(p) for stem, p in REF_JSONL.items()}
print('reference (tiled) counts:', {k: len(v) for k, v in ref_by_stem.items()})

bp_by_stem = {}
for stem, p in STEM_MIDIS.items():
    all_notes = []
    for _, ns in extract_notes_per_track(p):
        all_notes.extend(ns)
    bp_by_stem[stem] = all_notes
print('basic-pitch input counts:', {k: len(v) for k, v in bp_by_stem.items()})

print()
print('=== F1 merged vs M-SEP-1 tiled reference (upper-bounded by BP quality) ===')
for stem in sorted(REF_JSONL):
    p, r, fv = f1(ref_by_stem[stem], merged_by_stem[stem])
    print(f'  {stem:6s}: P={p:.4f} R={r:.4f} F1={fv:.4f} ref={len(ref_by_stem[stem])} est={len(merged_by_stem[stem])}')

print()
print('=== F1 merged vs basic-pitch input MIDIs (identity-merge metric) ===')
for stem in sorted(REF_JSONL):
    p, r, fv = f1(bp_by_stem[stem], merged_by_stem[stem])
    print(f'  {stem:6s}: P={p:.4f} R={r:.4f} F1={fv:.4f} ref={len(bp_by_stem[stem])} est={len(merged_by_stem[stem])}')

# Determinism: two full runs must produce byte-identical merged XML and MIDI.
merge_stems_to_score(STEM_MIDIS, Path('data/score/merged_r2.musicxml'), tempo_bpm=120.0, time_signature=(4,4))
xml_to_midi(Path('data/score/merged_r2.musicxml'), Path('data/score/merged_r2.mid'))
r1_xml = Path('data/score/merged_synth030s.musicxml').read_bytes()
r2_xml = Path('data/score/merged_r2.musicxml').read_bytes()
r1_mid = Path('data/score/merged_synth030s.mid').read_bytes()
r2_mid = Path('data/score/merged_r2.mid').read_bytes()
print()
print('determinism xml-identical:', r1_xml == r2_xml)
print('determinism mid-identical:', r1_mid == r2_mid)
