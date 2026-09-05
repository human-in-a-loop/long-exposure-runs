#!/usr/bin/env bash
# ---
# created: 2026-09-05T17:15:00Z
# cycle: 56
# run_id: run-2026-09-05T170000Z
# agent: worker
# milestone: _launches/rome-drums-stage1-c56
# ---
# c56 P4 launcher: Rome (sha16 51e433ade2a845e1) drums stage-1 coarse SF2
# preset sweep, detached, per brief P4.1. Not OP-1 gated (different driver).
set -euo pipefail
SONG_SHA16="51e433ade2a845e1"
OUT_DIR="data/v4/profiles/${SONG_SHA16}/drums_sweep_stage1"
LOG="data/v4/logs/rome_drums_stage1_c56.log"
PID_FILE="data/v4/_run/rome_drums_stage1_c56.pid"
REFERENCE_STEM="data/v3_spine/${SONG_SHA16}/operator_section/rc9_6stem/drums.wav"
MIDI_SOURCE="data/v3_spine/${SONG_SHA16}/operator_section/merged.mid"
SF2="/usr/share/sounds/sf2/FluidR3_GM.sf2"
mkdir -p "$(dirname "$LOG")" "$(dirname "$PID_FILE")" "$OUT_DIR"
setsid nohup /usr/bin/python3 scripts/sound_match/coarse_sweep_sf2_drums.py \
  --song-sha16 "$SONG_SHA16" \
  --instrument drums \
  --reference-stem "$REFERENCE_STEM" \
  --midi-source "$MIDI_SOURCE" \
  --sf2 "$SF2" \
  --out "$OUT_DIR" \
  --score-and-delete \
  --keep-top 3 \
  --max-audio-mb 500 \
  --disk-abort-pct 90 \
  > "$LOG" 2>&1 &
CHILD_PID=$!
echo "$CHILD_PID" > "$PID_FILE"
echo "Rome drums stage-1 launched: PID=$CHILD_PID log=$LOG"
disown "$CHILD_PID" || true
