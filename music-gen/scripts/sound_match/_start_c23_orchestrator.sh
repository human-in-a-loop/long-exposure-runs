#!/bin/bash
chmod +x scripts/sound_match/_launch_non_cg_bass_stage1_c23.sh
mkdir -p data/v4/logs
nohup setsid bash scripts/sound_match/_launch_non_cg_bass_stage1_c23.sh > data/v4/logs/non_cg_bass_stage1_c23_orchestrator.log 2>&1 &
PID_VAL=$!
disown
echo "LAUNCHED_ORCHESTRATOR_PID=$PID_VAL"
echo "PID_VAL=$PID_VAL"
sleep 3
ps -p $PID_VAL -o pid,stat,cmd 2>&1 || echo "not running"
