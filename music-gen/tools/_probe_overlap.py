import json
from collections import defaultdict
rows = [json.loads(l) for l in open('data/transcribe/basic_pitch/synth_030s/other.jsonl')]
# Check pitch-repeat overlaps: two notes on the same pitch that overlap
per_pitch = defaultdict(list)
for r in rows:
    per_pitch[r['pitch']].append((r['onset_s'], r['offset_s']))
overlaps = 0
for pitch, iv in per_pitch.items():
    iv.sort()
    for i in range(len(iv)-1):
        if iv[i+1][0] < iv[i][1]:
            overlaps += 1
            print(f'  pitch {pitch}: [{iv[i][0]:.3f},{iv[i][1]:.3f}] overlaps [{iv[i+1][0]:.3f},{iv[i+1][1]:.3f}]')
print(f'total overlap events: {overlaps}')

# Now count distinct-pitch simultaneous notes (chords)
from collections import Counter
onsets = Counter(r['onset_s'] for r in rows)
print(f'onsets with 2+ different pitches (chords): {sum(1 for v in onsets.values() if v > 1)}')
