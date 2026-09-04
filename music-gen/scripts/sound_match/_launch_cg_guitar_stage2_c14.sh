#!/usr/bin/env bash
# c14 CG guitar stage-2 fine fit — detached launch.
set -euo pipefail
cd "$(dirname "$0")/../.."
mkdir -p data/v4/logs data/v4/profiles/31a164f845f8e27e/guitar_sweep_stage2
LOG=data/v4/logs/cg_guitar_stage2_c14.log
: > "$LOG"
nohup setsid /usr/bin/python3 -u scripts/sound_match/fine_fit_sf2_guitar.py \
  --song-sha16 31a164f845f8e27e \
  --stage1-leaderboard data/v4/profiles/31a164f845f8e27e/guitar_sweep_stage1/leaderboard.tsv \
  --guitar-midi       data/v4/profiles/31a164f845f8e27e/guitar_sweep_stage1/guitar_excerpt.mid \
  --reference-stem    data/v3/deliveries/31a164f845f8e27e/cert_run1/stems_6s/guitar.wav \
  --out-dir           data/v4/profiles/31a164f845f8e27e/guitar_sweep_stage2 \
  --top-k 5 \
  --score-and-delete --keep-top 3 --max-audio-mb 500 --disk-abort-pct 90.0 \
  >> "$LOG" 2>&1 < /dev/null &
PID=$!
disown $PID || true
echo "$PID" > data/v4/logs/cg_guitar_stage2_c14.pid
echo "LAUNCHED pid=$PID log=$LOG"
