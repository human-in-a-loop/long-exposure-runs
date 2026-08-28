import sys, mido
sys.path.insert(0, '.')
from scripts.score.seed_score import seed_note_multiset

expected = seed_note_multiset()
print(f'expected: {len(expected)} notes')

m = mido.MidiFile('data/score/probe_seed_r1.mid')
tpb = m.ticks_per_beat
tempo_us = 500000
for tr in m.tracks:
    for msg in tr:
        if msg.type == 'set_tempo':
            tempo_us = msg.tempo
            break
sec_per_tick = (tempo_us/1e6)/tpb
print(f'PPQ={tpb}, tempo_us={tempo_us}')

got = []
for i, tr in enumerate(m.tracks):
    active = {}
    abs_t = 0
    tr_name = None
    for msg in tr:
        abs_t += msg.time
        if msg.type == 'track_name':
            tr_name = msg.name
        if msg.type == 'note_on' and msg.velocity > 0:
            active[(msg.channel, msg.note)] = abs_t
        elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
            k = (msg.channel, msg.note)
            if k in active:
                onset_ticks = active.pop(k)
                onset_s = onset_ticks * sec_per_tick
                dur_s = (abs_t - onset_ticks) * sec_per_tick
                got.append((tr_name or 'track_%d'%i, round(onset_s,3), round(dur_s,3), msg.note))

print(f'got: {len(got)} notes')
for g in sorted(got)[:6]: print('got', g)
for e in sorted(expected)[:6]: print('exp', e)
print('part names in got:', sorted(set(g[0] for g in got)))
