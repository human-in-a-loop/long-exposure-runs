#!/bin/bash
# Detached launcher for the CG bass coarse sweep, cycle 1.
# Emits PID + logfile; cycle 2 picks up the leaderboard.

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

mkdir -p data/v4/logs data/v4/profiles/31a164f845f8e27e/bass_sweep_stage1

LOG="data/v4/logs/cg_bass_sweep_c1.log"

nohup setsid /usr/bin/python3 -m scripts.sound_match.coarse_sweep_sf2 \
  --song 31a164f845f8e27e \
  --instrument bass \
  --reference-stem data/v3/deliveries/31a164f845f8e27e/cert_run1/stems_6s/bass.wav \
  --midi-excerpt data/v3/deliveries/31a164f845f8e27e/cert_run1/per_track/bass.mid \
  --sf2 /usr/share/sounds/sf2/FluidR3_GM.sf2 \
  --presets "bank0:programs=32,33,34,35,36,37,38,39,4,5,6,7,17,18,19" \
  --out data/v4/profiles/31a164f845f8e27e/bass_sweep_stage1/ \
  > "$LOG" 2>&1 &

PID=$!
echo "LAUNCHED_PID=$PID"
echo "LOG=$LOG"
