#!/usr/bin/env bash
# ---
# created: 2026-09-05T16:20:00Z
# cycle: 55
# run_id: run-2026-09-05T160000Z
# agent: worker
# milestone: _launches/wig-drums-stage1-c55
# ---
# c55 P3 launcher: WIG (What If I Go, sha16 252eb21ce7df7328) drums stage-1
# coarse SF2 preset sweep, detached, per brief P3.1. Additional required
# driver args (--instrument, --reference-stem, --sf2, --out, --midi-source)
# supplied from the CG c10 template (data/v4/profiles/31a164f845f8e27e/
# drums_sweep_stage1/run_manifest.json), adapted for WIG per its stem
# manifest (data/v4/profiles/252eb21ce7df7328/stem_manifest.json). Brief
# under-specified these args; invariant (d) disclosure filed in the launch
# ledger event.
set -euo pipefail
SONG_SHA16="252eb21ce7df7328"
OUT_DIR="data/v4/profiles/${SONG_SHA16}/drums_sweep_stage1"
LOG="data/v4/logs/wig_drums_stage1_c55.log"
PID_FILE="data/v4/_run/wig_drums_stage1_c55.pid"
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
echo "WIG drums stage-1 launched: PID=$CHILD_PID log=$LOG"
disown "$CHILD_PID" || true
