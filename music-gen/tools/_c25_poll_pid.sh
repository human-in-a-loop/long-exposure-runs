#!/bin/bash
# Poll c25 detached PID until exit or 25-min wall cap. Emit terminal status.
set -uo pipefail
PID=13838
LOG=data/v3_spine/88d247468cb6d49f/resume_peach_dream_c25.log

if ! kill -0 "$PID" 2>/dev/null; then
  echo "IMMEDIATE_EXIT pid=$PID"
else
  timeout 1500 bash -c 'while kill -0 '"$PID"' 2>/dev/null; do sleep 30; done' || true
fi

echo "---FINAL---"
if kill -0 "$PID" 2>/dev/null; then
  echo "STILL_RUNNING pid=$PID"
else
  echo "EXITED pid=$PID"
fi

echo "---LOG TAIL (60)---"
tail -60 "$LOG" 2>&1 || true

echo "---CYCLE25 DIR---"
ls -la data/v3/deliveries/88d247468cb6d49f/cycle25/ 2>&1

echo "---WORK DIR---"
ls -la data/v3_spine/88d247468cb6d49f/operator_section_c25_checkpointed/ 2>&1
