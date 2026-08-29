#!/bin/bash
# Restart feature extraction detached from parent shell + harness so it
# survives session teardowns (fix for c31/c36 silent-halt pattern).
# Writes a heartbeat file every song print so a supervisor can detect
# stall vs progress.
cd /home/user/long-exposure-runs/music-gen
export PYTHONPATH=.
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
mkdir -p data/ear_v0
: > data/ear_v0/extract3.log
nohup setsid /usr/bin/python3 -u -m scripts.ear_v0.extract_features_v0 \
  >> data/ear_v0/extract3.log 2>&1 < /dev/null &
echo "spawned pid=$!"
sleep 2
head -5 data/ear_v0/extract3.log 2>/dev/null
