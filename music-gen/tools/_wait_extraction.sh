#!/bin/bash
# Poll the extraction cache and emit progress lines until we reach 43/43.
prev=0
while true; do
  n=$(ls data/ear_v0/per_song_features/ 2>/dev/null | wc -l)
  if [ "$n" != "$prev" ]; then
    echo "cached=$n/43 at $(date +%H:%M:%S)"
    prev="$n"
  fi
  if [ "$n" -ge 43 ]; then
    echo "DONE cached=$n"
    break
  fi
  sleep 45
done
