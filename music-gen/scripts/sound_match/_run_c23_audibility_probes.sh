#!/bin/bash
set -eu
# Empty-stem audibility measurements for c23 NULL findings
# WIG guitar
/usr/bin/python3 scripts/sound_match/measure_stem_audibility.py \
  --wav data/v3_spine/252eb21ce7df7328/operator_section/rc9_6stem/guitar.wav \
  --out data/v4/profiles/252eb21ce7df7328/audibility_guitar.json

# Rome piano
/usr/bin/python3 scripts/sound_match/measure_stem_audibility.py \
  --wav data/v3_spine/51e433ade2a845e1/operator_section/rc9_6stem/piano.wav \
  --out data/v4/profiles/51e433ade2a845e1/audibility_piano.json

# Rome other
/usr/bin/python3 scripts/sound_match/measure_stem_audibility.py \
  --wav data/v3_spine/51e433ade2a845e1/operator_section/rc9_6stem/other.wav \
  --out data/v4/profiles/51e433ade2a845e1/audibility_other.json

# Peach Dream guitar
/usr/bin/python3 scripts/sound_match/measure_stem_audibility.py \
  --wav data/v3_spine/88d247468cb6d49f/operator_section_c25_checkpointed/rc9_6stem/guitar.wav \
  --out data/v4/profiles/88d247468cb6d49f/audibility_guitar.json

# Disco A vocals (vocals is hybrid-overlay policy — audibility for provenance only)
/usr/bin/python3 scripts/sound_match/measure_stem_audibility.py \
  --wav data/v3_spine/cdd2717e52820ff6/operator_section/rc9_6stem/vocals.wav \
  --out data/v4/profiles/cdd2717e52820ff6/audibility_vocals.json
