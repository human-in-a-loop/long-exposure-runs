#!/usr/bin/env bash
# Detached launcher for cycle-2 stage-2 fine fit (CG bass, family sf2).
# c24 detached-launch pattern: nohup + setsid + logfile + echo PID.
set -euo pipefail

cd /home/user/long-exposure-runs/music-gen

LOG=data/v4/logs/cg_bass_stage2_c2.log
mkdir -p data/v4/logs data/v4/profiles/31a164f845f8e27e/bass_stage2

nohup setsid env \
  PYTHONHASHSEED=0 \
  SOURCE_DATE_EPOCH=1756463424 \
  TZ=UTC \
  LC_ALL=C.UTF-8 \
  OMP_NUM_THREADS=1 \
  MKL_NUM_THREADS=1 \
  OPENBLAS_NUM_THREADS=1 \
  PYTHONPATH=. \
  /usr/bin/python3 -m scripts.sound_match.fine_fit_sf2 \
    --song-sha16 31a164f845f8e27e \
    --stage1-leaderboard data/v4/profiles/31a164f845f8e27e/bass_sweep_stage1/leaderboard.tsv \
    --reference-stem data/v3/deliveries/31a164f845f8e27e/cert_run1/stems_6s/bass.wav \
    --bass-midi data/v4/profiles/31a164f845f8e27e/bass_sweep_stage1/inputs/bass.mid \
    --sf2 /usr/share/sounds/sf2/FluidR3_GM.sf2 \
    --out-dir data/v4/profiles/31a164f845f8e27e/bass_stage2 \
    > "$LOG" 2>&1 &
PID=$!
disown
echo $PID
