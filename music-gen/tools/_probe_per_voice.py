import xml.etree.ElementTree as ET
tree = ET.parse('data/score/merged_synth030s.musicxml')
root = tree.getroot()
other_part = root.findall('part')[2]
per_voice = {}
per_voice_distinct = {}
for measure in other_part.findall('measure'):
    for n in measure.findall('note'):
        pitch = n.find('pitch')
        if pitch is None:
            continue
        v = n.find('voice')
        vid = v.text if v is not None else '?'
        per_voice[vid] = per_voice.get(vid, 0) + 1
        ties = n.findall('tie')
        types = [t.get('type') for t in ties]
        is_new = ('start' in types and 'stop' not in types) or not ties
        if is_new:
            per_voice_distinct[vid] = per_voice_distinct.get(vid, 0) + 1
print('pitches per voice:', per_voice)
print('distinct notes per voice:', per_voice_distinct)
print('sum distinct:', sum(per_voice_distinct.values()))
