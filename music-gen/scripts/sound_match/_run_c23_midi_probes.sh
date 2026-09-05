#!/bin/bash
set -eu
chmod +x scripts/sound_match/stem_midi_probe.py
/usr/bin/python3 scripts/sound_match/stem_midi_probe.py \
  --song-sha16 252eb21ce7df7328 \
  --merged-midi data/v3_spine/252eb21ce7df7328/operator_section/merged.mid \
  --out data/v4/profiles/252eb21ce7df7328/stem_midi_probe.json
/usr/bin/python3 scripts/sound_match/stem_midi_probe.py \
  --song-sha16 51e433ade2a845e1 \
  --merged-midi data/v3_spine/51e433ade2a845e1/operator_section/merged.mid \
  --out data/v4/profiles/51e433ade2a845e1/stem_midi_probe.json
/usr/bin/python3 scripts/sound_match/stem_midi_probe.py \
  --song-sha16 88d247468cb6d49f \
  --merged-midi data/v3_spine/88d247468cb6d49f/operator_section_c25_checkpointed/merged.mid \
  --out data/v4/profiles/88d247468cb6d49f/stem_midi_probe.json
/usr/bin/python3 scripts/sound_match/stem_midi_probe.py \
  --song-sha16 cdd2717e52820ff6 \
  --merged-midi data/v3_spine/cdd2717e52820ff6/operator_section/merged.mid \
  --out data/v4/profiles/cdd2717e52820ff6/stem_midi_probe.json
