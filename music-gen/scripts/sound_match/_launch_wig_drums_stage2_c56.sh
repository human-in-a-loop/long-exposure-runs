#!/usr/bin/env bash
# ---
# created: 2026-09-05T17:05:00Z
# cycle: 56
# run_id: run-2026-09-05T170000Z
# agent: worker
# milestone: _launches/wig-drums-stage2-c56
# ---
# c56 P2 launcher: WIG (sha16 252eb21ce7df7328) drums stage-2 fine fit,
# detached under OP-1 SerialLock. Inputs derived from c55 P3 stage-1
# outputs (drums_excerpt.mid + leaderboard.tsv). CG c11 fine-fit template
# adapted for non-CG song per c56 brief P2.1.
set -euo pipefail
SONG_SHA16="252eb21ce7df7328"
STAGE1_DIR="data/v4/profiles/${SONG_SHA16}/drums_sweep_stage1"
OUT_DIR="data/v4/profiles/${SONG_SHA16}/drums_sweep_stage2"
LOG="data/v4/logs/wig_drums_stage2_c56.log"
PID_FILE="data/v4/_run/wig_drums_stage2_c56.pid"
REFERENCE_STEM="data/v3_spine/${SONG_SHA16}/operator_section/rc9_6stem/drums.wav"
DRUMS_MIDI="${STAGE1_DIR}/drums_excerpt.mid"
STAGE1_LEADERBOARD="${STAGE1_DIR}/leaderboard.tsv"
SF2="/usr/share/sounds/sf2/FluidR3_GM.sf2"
mkdir -p "$(dirname "$LOG")" "$(dirname "$PID_FILE")" "$OUT_DIR"
setsid nohup /usr/bin/python3 scripts/sound_match/fine_fit_sf2_drums.py \
  --song-sha16 "$SONG_SHA16" \
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
echo "WIG drums stage-2 launched: PID=$CHILD_PID log=$LOG"
disown "$CHILD_PID" || true
