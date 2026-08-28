"""Extract every actual pitched note (with tie=start info) from the third part
of merged_synth030s.musicxml and count distinct note-starts."""
import xml.etree.ElementTree as ET

tree = ET.parse('data/score/merged_synth030s.musicxml')
root = tree.getroot()
parts = root.findall('part')
print(f'parts in tree: {len(parts)}')
other_part = parts[2]  # bass, drums, other

# Iterate through measures and count notes with pitch, tracking tie starts
n_pitch_notes = 0
n_tie_start = 0
n_tie_stop = 0
n_tie_continue = 0
n_no_tie = 0
n_grace = 0
n_chord_children = 0
voice_ids = set()

for measure in other_part.findall('measure'):
    for n in measure.findall('note'):
        pitch = n.find('pitch')
        if pitch is None:
            continue
        n_pitch_notes += 1
        if n.find('grace') is not None:
            n_grace += 1
        if n.find('chord') is not None:
            n_chord_children += 1
        v = n.find('voice')
        if v is not None:
            voice_ids.add(v.text)
        ties = n.findall('tie')
        types = [t.get('type') for t in ties]
        if 'start' in types and 'stop' not in types:
            n_tie_start += 1
        elif 'stop' in types and 'start' not in types:
            n_tie_stop += 1
        elif 'stop' in types and 'start' in types:
            n_tie_continue += 1
        elif not ties:
            n_no_tie += 1

print(f'total pitched <note>: {n_pitch_notes}')
print(f'  chord-children: {n_chord_children}')
print(f'  grace: {n_grace}')
print(f'  tie start-only: {n_tie_start}')
print(f'  tie stop-only: {n_tie_stop}')
print(f'  tie both (continue): {n_tie_continue}')
print(f'  no tie: {n_no_tie}')
print(f'voice ids: {sorted(voice_ids)}')
# A distinct note event corresponds to (tie start-only OR no-tie).
distinct = n_tie_start + n_no_tie
print(f'estimated distinct note events (tie-collapsed): {distinct}')
