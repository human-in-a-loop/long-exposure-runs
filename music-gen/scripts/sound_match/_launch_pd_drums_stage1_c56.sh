#!/usr/bin/env bash
# ---
# created: 2026-09-05T17:15:00Z
# cycle: 56
# run_id: run-2026-09-05T170000Z
# agent: worker
# milestone: _launches/pd-drums-stage1-c56
# ---
# c56 P4 launcher: Peach Dream (sha16 88d247468cb6d49f) drums stage-1
# coarse SF2 preset sweep, detached, per brief P4.2. Uses non-standard
# operator_section_c25_checkpointed/rc9_6stem/ path per PD stem manifest
# (data/v4/profiles/88d247468cb6d49f/stem_manifest.json); invariant (d)
# disclosure filed in the launch ledger event.
set -euo pipefail
SONG_SHA16="88d247468cb6d49f"
OUT_DIR="data/v4/profiles/${SONG_SHA16}/drums_sweep_stage1"
LOG="data/v4/logs/pd_drums_stage1_c56.log"
PID_FILE="data/v4/_run/pd_drums_stage1_c56.pid"
REFERENCE_STEM="data/v3_spine/${SONG_SHA16}/operator_section_c25_checkpointed/rc9_6stem/drums.wav"
MIDI_SOURCE="data/v3_spine/${SONG_SHA16}/operator_section_c25_checkpointed/merged.mid"
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
echo "PD drums stage-1 launched: PID=$CHILD_PID log=$LOG"
disown "$CHILD_PID" || true
