#!/usr/bin/env bash
set -euo pipefail
cd /home/user/long-exposure-runs/music-gen
export PYTHONPATH=.
/usr/bin/python3 scripts/score_bridge_v2/run_normalizer_v2.py
