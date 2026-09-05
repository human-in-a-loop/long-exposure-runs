#!/usr/bin/env bash
# ---
# created: 2026-09-05T18:15:00Z
# cycle: 57
# run_id: run-2026-09-05T180000Z
# agent: worker
# milestone: _launches/rome-drums-stage2-c57
# ---
# c57 P6 launcher: Rome (sha16 51e433ade2a845e1) drums stage-2 fine fit,
# detached under OP-1 SerialLock. --cycle 57 explicit per c56 M-1
# launcher-level cycle-attribution fix (c57 P3).
set -euo pipefail
SONG_SHA16="51e433ade2a845e1"
STAGE1_DIR="data/v4/profiles/${SONG_SHA16}/drums_sweep_stage1"
OUT_DIR="data/v4/profiles/${SONG_SHA16}/drums_sweep_stage2"
LOG="data/v4/logs/rome_drums_stage2_c57.log"
PID_FILE="data/v4/_run/rome_drums_stage2_c57.pid"
REFERENCE_STEM="data/v3_spine/${SONG_SHA16}/operator_section/rc9_6stem/drums.wav"
DRUMS_MIDI="${STAGE1_DIR}/drums_excerpt.mid"
STAGE1_LEADERBOARD="${STAGE1_DIR}/leaderboard.tsv"
SF2="/usr/share/sounds/sf2/FluidR3_GM.sf2"
mkdir -p "$(dirname "$LOG")" "$(dirname "$PID_FILE")" "$OUT_DIR"
setsid nohup /usr/bin/python3 scripts/sound_match/fine_fit_sf2_drums.py \
  --song-sha16 "$SONG_SHA16" \
  --cycle 57 \
  --stage1-leaderboard "$STAGE1_LEADERBOARD" \
  --drums-midi "$DRUMS_MIDI" \
  --reference-stem "$REFERENCE_STEM" \
  --sf2 "$SF2" \
  --out-dir "$OUT_DIR" \
  --keep-top 3 \
  --max-audio-mb 500 \
  > "$LOG" 2>&1 &
CHILD_PID=$!
echo "$CHILD_PID" > "$PID_FILE"
echo "Rome drums stage-2 launched: PID=$CHILD_PID log=$LOG"
disown "$CHILD_PID" || true
