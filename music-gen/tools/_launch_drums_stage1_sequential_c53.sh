#!/bin/bash
# c53 P2/P3 sequential drums stage-1: WIG then Disco A.
# Sequential per brief P2/P3 gate fallback (df>=80%; concurrent path rejected).
# Coarse sweeps do NOT require OP-1 SerialLock per operator directive.
set -e
cd "$(dirname "$0")/.."

WIG_SHA="252eb21ce7df7328"
DISCO_A_SHA="cdd2717e52820ff6"

echo "=== WIG drums stage-1 ==="
/usr/bin/python3 scripts/sound_match/coarse_sweep_sf2_drums.py \
  --song-sha16 "$WIG_SHA" \
  --instrument drums \
  --reference-stem "data/v3_spine/$WIG_SHA/operator_section/rc9_6stem/drums.wav" \
  --midi-source "data/v3_spine/$WIG_SHA/operator_section/merged.mid" \
  --sf2 /usr/share/sounds/sf2/FluidR3_GM.sf2 \
  --out "data/v4/profiles/$WIG_SHA/drums_sweep_stage1" \
  --score-and-delete --keep-top 3 --max-audio-mb 500 --disk-abort-pct 90 \
  > data/v4/logs/wig_drums_stage1_c53.log 2>&1

echo "=== Disco A drums stage-1 ==="
/usr/bin/python3 scripts/sound_match/coarse_sweep_sf2_drums.py \
  --song-sha16 "$DISCO_A_SHA" \
  --instrument drums \
  --reference-stem "data/v3_spine/$DISCO_A_SHA/operator_section/rc9_6stem/drums.wav" \
  --midi-source "data/v3_spine/$DISCO_A_SHA/operator_section/merged.mid" \
  --sf2 /usr/share/sounds/sf2/FluidR3_GM.sf2 \
  --out "data/v4/profiles/$DISCO_A_SHA/drums_sweep_stage1" \
  --score-and-delete --keep-top 3 --max-audio-mb 500 --disk-abort-pct 90 \
  > data/v4/logs/disco_a_drums_stage1_c53.log 2>&1

echo "=== Both drums stage-1 sweeps DONE ==="
