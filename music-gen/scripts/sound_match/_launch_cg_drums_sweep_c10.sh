#!/bin/bash
# c10 detached launch of CG drums coarse sweep (post disk-check fix).
# ---
# created: 2026-09-03T18:35:00Z
# cycle: 10
# milestone: M-V4-PROFILES-1/cg-drums-sweep-launched
# ---
set -e
cd /home/user/long-exposure-runs/music-gen
mkdir -p data/v4/logs data/v4/profiles/31a164f845f8e27e/drums_sweep_stage1
LOG=data/v4/logs/cg_drums_sweep_c10.log
nohup setsid env PYTHONHASHSEED=0 SOURCE_DATE_EPOCH=1756463424 TZ=UTC LC_ALL=C.UTF-8 \
  OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
  /usr/bin/python3 scripts/sound_match/coarse_sweep_sf2_drums.py \
    --song 31a164f845f8e27e --instrument drums \
    --reference-stem data/v3/deliveries/31a164f845f8e27e/cert_run1/stems_6s/drums.wav \
    --midi-source data/v3/deliveries/31a164f845f8e27e/cert_run1/merged.mid \
    --sf2 /usr/share/sounds/sf2/FluidR3_GM.sf2 \
    --out data/v4/profiles/31a164f845f8e27e/drums_sweep_stage1 \
    --programs 0,8,16,24,25,32,40,48 \
    --score-and-delete --keep-top 3 --max-audio-mb 500 \
  > "$LOG" 2>&1 &
PID=$!
disown "$PID" 2>/dev/null || true
echo "SWEEP_PID=$PID"
echo "LOGFILE=$LOG"
