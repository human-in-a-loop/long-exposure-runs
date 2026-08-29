#!/usr/bin/python3
"""One-shot inspection of the c37 fixture for c39 normalizer-v2 design."""
import re
import pathlib
from collections import Counter

text = pathlib.Path(
    'data/score_bridge_real_audio/inputs/merged_real_audio.musicxml'
).read_text()

notes = re.findall(r'<note[^>]*>.*?</note>', text, re.DOTALL)
print('total notes:', len(notes))
print('first 3 notes:')
for n in notes[:3]:
    print(n[:500])
    print('===')
print('type tags:', len(re.findall(r'<type>[^<]+</type>', text)))
print('dot tags:', text.count('<dot/>'))
print('time-modification blocks:', text.count('<time-modification>'))
print('tie tags:', text.count('<tie'))
print('duration tags:', len(re.findall(r'<duration>\d+</duration>', text)))
divs = re.findall(r'<divisions>(\d+)</divisions>', text)
print('divisions samples:', divs[:3])
print('unique divisions:', sorted(set(divs)))
c = Counter(re.findall(r'<type>([^<]+)</type>', text))
print('type distribution:', c)
