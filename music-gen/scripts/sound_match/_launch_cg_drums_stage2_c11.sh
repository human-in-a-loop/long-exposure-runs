#!/usr/bin/env bash
# c11 detached launch helper for CG drums stage-2 fine fit.
# env pins verbatim per research brief Track 2.
set -euo pipefail

cd /home/user/long-exposure-runs/music-gen

LOG=data/v4/logs/cg_drums_stage2_c11.log
OUT=data/v4/profiles/31a164f845f8e27e/drums_sweep_stage2
mkdir -p "$(dirname "$LOG")" "$OUT"

# Detach and forget. Log carries all output.
nohup setsid env PYTHONHASHSEED=0 SOURCE_DATE_EPOCH=1756463424 TZ=UTC LC_ALL=C.UTF-8 \
    OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
  /usr/bin/python3 scripts/sound_match/fine_fit_sf2_drums.py \
    --song-sha16 31a164f845f8e27e \
    --stage1-leaderboard data/v4/profiles/31a164f845f8e27e/drums_sweep_stage1/leaderboard.tsv \
    --drums-midi data/v4/profiles/31a164f845f8e27e/drums_sweep_stage1/drums_excerpt.mid \
    --reference-stem data/v3/deliveries/31a164f845f8e27e/cert_run1/stems_6s/drums.wav \
    --out-dir "$OUT" \
    --sample-rate 44100 \
    --top-k 5 \
    --include-program 0 \
    --lufs-target -18.0 \
    --score-and-delete \
    --keep-top 3 \
    --max-audio-mb 500 \
  > "$LOG" 2>&1 &
PID=$!
disown "$PID" || true
echo "$PID" > data/v4/logs/cg_drums_stage2_c11.pid
echo "LAUNCHED pid=$PID log=$LOG out=$OUT"
