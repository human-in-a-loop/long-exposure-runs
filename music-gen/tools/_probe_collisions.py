import json
from collections import Counter
rows = [json.loads(l) for l in open('data/transcribe/basic_pitch/synth_030s/other.jsonl')]
grid_s = 0.5 / 64.0
print(f'grid_s={grid_s*1000:.2f}ms  ({len(rows)} rows)')
snapped = [(round(r['onset_s']/grid_s)*grid_s, r['pitch']) for r in rows]
c = Counter(snapped)
dupes = {k: v for k, v in c.items() if v > 1}
print(f'onset-pitch collisions after snap: {len(dupes)} keys, {sum(v-1 for v in dupes.values())} dropped notes')
same_onset = Counter([r['onset_s'] for r in rows])
print(f'raw onsets with 2+ notes: {sum(1 for v in same_onset.values() if v > 1)}')
# What happens in music21 with two notes at same offset+pitch? Second replaces first (by hash equality)?
# Let's dump the dupes we lose
for (o, p), v in sorted(dupes.items())[:10]:
    print(f'  snapped_onset={o:.4f}s pitch={p} x{v}')
