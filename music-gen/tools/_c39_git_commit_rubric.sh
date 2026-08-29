#!/usr/bin/env bash
set -euo pipefail
cd /home/user/long-exposure-runs/music-gen
git add docs/score_bridge_real_audio_quantization_normalizer_v2_rubric.md
git commit -m "M-SCORE-1/bridge-api-real-audio-quantization/normalizer-v2: rubric first (c39)"
git log --oneline -1
