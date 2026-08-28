from pathlib import Path
import re
x = Path('data/score/merged_synth030s.musicxml').read_text()
parts = re.split(r'<part id="P', x)
print(f'chunks: {len(parts)}')
for i, chunk in enumerate(parts[1:], start=1):
    n_pitch = chunk.count('<pitch>')
    n_rest = chunk.count('<rest')
    n_note = chunk.count('<note>') + chunk.count('<note ')
    n_chord = chunk.count('<chord')
    n_measure = chunk.count('<measure ')
    print(f'part {i}: measures={n_measure} pitches={n_pitch} rests={n_rest} <note>={n_note} chord_tags={n_chord}')
