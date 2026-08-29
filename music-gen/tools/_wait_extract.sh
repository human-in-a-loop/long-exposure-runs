#!/bin/bash
FEAT_DIR=/home/user/long-exposure-runs/music-gen/data/ear_v2/features_v2
PID=22488
while true; do
  count=$(ls "$FEAT_DIR" | wc -l)
  if [ "$count" -ge 252 ]; then
    echo "EXTRACTION_DONE count=$count"
    break
  fi
  if ! ps -p $PID >/dev/null 2>&1; then
    echo "EXTRACTION_PROCESS_DIED count=$count"
    break
  fi
  sleep 90
done
