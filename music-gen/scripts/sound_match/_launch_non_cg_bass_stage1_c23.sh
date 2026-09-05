#!/bin/bash
# Detached launcher for non-CG bass stage-1 sweeps, cycle 23.
# Runs 4 songs sequentially in background; each takes ~5-10 min.

set -eu

REPO="/home/user/long-exposure-runs/music-gen"
cd "$REPO"

export PYTHONHASHSEED=0
export SOURCE_DATE_EPOCH=1756463424
export TZ=UTC
export LC_ALL=C.UTF-8
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1

mkdir -p data/v4/logs
SF2=/usr/share/sounds/sf2/FluidR3_GM.sf2
PRESETS="bank0:programs=32,33,34,35,36,37,38,39,4,5,6,7,17,18,19"

launch_one() {
  local SHA=$1
  local NAME=$2
  local MID=$3
  local STEM=$4
  local OUT="data/v4/profiles/$SHA/bass_sweep_stage1"
  local LOG="data/v4/logs/${NAME}_bass_sweep_c23.log"
  mkdir -p "$OUT"
  echo "[$NAME/$SHA] launching bass sweep..."
  /usr/bin/python3 -m scripts.sound_match.coarse_sweep_sf2 \
    --song "$SHA" \
    --instrument bass \
    --reference-stem "$STEM" \
    --midi-source "$MID" \
    --sf2 "$SF2" \
    --presets "$PRESETS" \
    --out "$OUT/" \
    > "$LOG" 2>&1
  echo "[$NAME/$SHA] done, log=$LOG"
}

# Order per brief: Peach Dream first (operator-flagged), then WIG, Rome, Disco A
launch_one 88d247468cb6d49f peach_dream \
  data/v3_spine/88d247468cb6d49f/operator_section_c25_checkpointed/merged.mid \
  data/v3_spine/88d247468cb6d49f/operator_section_c25_checkpointed/rc9_6stem/bass.wav

launch_one 252eb21ce7df7328 wig \
  data/v3_spine/252eb21ce7df7328/operator_section/merged.mid \
  data/v3_spine/252eb21ce7df7328/operator_section/rc9_6stem/bass.wav

launch_one 51e433ade2a845e1 rome \
  data/v3_spine/51e433ade2a845e1/operator_section/merged.mid \
  data/v3_spine/51e433ade2a845e1/operator_section/rc9_6stem/bass.wav

launch_one cdd2717e52820ff6 disco_a \
  data/v3_spine/cdd2717e52820ff6/operator_section/merged.mid \
  data/v3_spine/cdd2717e52820ff6/operator_section/rc9_6stem/bass.wav

echo "ALL_DONE_$(date -u +%s)"
