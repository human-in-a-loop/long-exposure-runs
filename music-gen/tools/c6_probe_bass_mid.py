#!/usr/bin/env -S /usr/bin/python3
"""Probe bass.mid for notes."""
import sys
sys.path.insert(0, ".")
import mido
m = mido.MidiFile("data/v4/profiles/31a164f845f8e27e/bass_sweep_stage1/inputs/bass.mid")
tempo = 500000
tick = 0
notes_on = {}
events = []
for msg in mido.merge_tracks(m.tracks):
    tick += msg.time
    if msg.type == "set_tempo":
        tempo = msg.tempo
    elif msg.type == "note_on" and msg.velocity > 0:
        notes_on[msg.note] = mido.tick2second(tick, m.ticks_per_beat, tempo)
    elif msg.type == "note_off" or (msg.type == "note_on" and msg.velocity == 0):
        if msg.note in notes_on:
            t_on = notes_on.pop(msg.note)
            t_off = mido.tick2second(tick, m.ticks_per_beat, tempo)
            events.append((t_on, msg.note, t_off - t_on))
events.sort()
for e in events:
    print(f"  onset={e[0]:.4f}s pitch={e[1]} dur={e[2]:.4f}s")
print(f"total notes: {len(events)}")
if events:
    print(f"total duration: {max(e[0] + e[2] for e in events):.3f}s")
