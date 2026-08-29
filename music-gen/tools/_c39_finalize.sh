#!/usr/bin/env bash
set -euo pipefail
cd /home/user/long-exposure-runs/music-gen
git add -u tools/
git status --short
git commit -m "M-SCORE-1/bridge-api-real-audio-quantization/normalizer-v2: archive c39 scratch (c39 clone-1)" 2>&1
git log --oneline -1
