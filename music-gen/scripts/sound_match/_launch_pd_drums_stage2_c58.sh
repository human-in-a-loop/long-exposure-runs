#!/usr/bin/env bash
# ---
# created: 2026-09-05T20:15:00Z
# cycle: 58
# run_id: run-2026-09-05T200000Z
# agent: worker
# milestone: _launches/pd-drums-stage2-c58
# ---
# c58 P1 launcher: Peach Dream (sha16 88d247468cb6d49f) drums stage-2 fine
# fit, detached under OP-1 SerialLock (queued after Rome via kernel-atomic
# refuse). --cycle 58 explicit per c56 M-1 launcher-level fix. Stem source
# is non-standard operator_section_c25_checkpointed/rc9_6stem/ per PD
# stem_manifest.json (invariant (d) disclosure carried forward). SHA drift
# vs c57 launcher intentional (c58 relabel + cycle number bump).
set -euo pipefail
SONG_SHA16="88d247468cb6d49f"
STAGE1_DIR="data/v4/profiles/${SONG_SHA16}/drums_sweep_stage1"
OUT_DIR="data/v4/profiles/${SONG_SHA16}/drums_sweep_stage2"
LOG="data/v4/logs/pd_drums_stage2_c58.log"
PID_FILE="data/v4/_run/pd_drums_stage2_c58.pid"
REFERENCE_STEM="data/v3_spine/${SONG_SHA16}/operator_section_c25_checkpointed/rc9_6stem/drums.wav"
DRUMS_MIDI="${STAGE1_DIR}/drums_excerpt.mid"
STAGE1_LEADERBOARD="${STAGE1_DIR}/leaderboard.tsv"
SF2="/usr/share/sounds/sf2/FluidR3_GM.sf2"
mkdir -p "$(dirname "$LOG")" "$(dirname "$PID_FILE")" "$OUT_DIR"
setsid nohup /usr/bin/python3 scripts/sound_match/fine_fit_sf2_drums.py \
  --song-sha16 "$SONG_SHA16" \
  --cycle 58 \
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
echo "PD drums stage-2 launched: PID=$CHILD_PID log=$LOG"
disown "$CHILD_PID" || true
