#!/bin/bash
# poll feature extraction until 252/252
while true; do
  c=$(ls data/ear_v2/features_v2/ 2>/dev/null | wc -l)
  echo "count=$c/252"
  if [ "$c" -ge 252 ]; then
    echo DONE
    exit 0
  fi
  sleep 120
done
