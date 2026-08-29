#!/usr/bin/env bash
set -euo pipefail
cd /home/user/long-exposure-runs/music-gen
export PYTHONPATH=.
/usr/bin/python3 scripts/score_bridge_v2/normalize_v2.py \
    data/score_bridge_real_audio/inputs/merged_real_audio.musicxml \
    data/score_bridge_real_audio_normalizer_v2/inputs/merged_normalized_v2.musicxml
