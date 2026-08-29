#!/bin/bash
# session-2 orchestrator: runs pipeline for a bounded wall-clock, then sweeps stubs
# and drives all terminal artifacts + validators.
#
# Design: single foreground shell task. On completion, all artifacts are on disk.
# The Claude session receives a task-completion notification.

set -uo pipefail

cd /home/user/long-exposure-runs/music-gen

STATE_FILE="data/recreate_v0_full_corpus/session2_state.json"
STAGE_LOG="data/recreate_v0_full_corpus/session2_orchestrator.log"

# Pipeline wall-clock budget. Auditor: 35 songs × ~165s ≈ 96 min = 5760s.
# Reserve ~15 min for terminal artifacts + validators.
PIPELINE_BUDGET_S="${MUSICGEN_PIPELINE_BUDGET_S:-5400}"

log() {
  local msg="$1"
  local ts
  ts="$(date -u +%FT%TZ)"
  echo "[$ts] $msg" >> "$STAGE_LOG"
  # Also to stdout so the harness's background-task log captures it.
  echo "[$ts] $msg"
}

update_state() {
  local stage="$1"
  local status="$2"
  local rc="${3:-0}"
  local ts
  ts="$(date -u +%FT%TZ)"
  python3 - "$STATE_FILE" "$stage" "$status" "$rc" "$ts" << 'EOF'
import json, sys, os
path, stage, status, rc, ts = sys.argv[1:6]
try:
    d = json.load(open(path))
except Exception:
    d = {"stages": []}
d["stages"].append({"stage": stage, "status": status, "rc": int(rc), "ts": ts})
d["last_stage"] = stage
d["last_status"] = status
d["last_rc"] = int(rc)
d["last_ts"] = ts
os.makedirs(os.path.dirname(path), exist_ok=True)
tmp = path + ".tmp"
open(tmp, "w").write(json.dumps(d, indent=2, sort_keys=True))
os.replace(tmp, path)
EOF
}

mkdir -p "$(dirname "$STAGE_LOG")"

log "session2_orchestrator START (pipeline_budget=${PIPELINE_BUDGET_S}s)"
update_state "orchestrator" "start"

# ---- Stage 1: Pipeline ---------------------------------------------------
log "STAGE 1: pipeline start"
update_state "pipeline" "running"

# Run pipeline with hard timeout. Idempotent per-song: reuses cached results
# from session 1 (song 1 full, song 2 partial per handoff).
timeout --preserve-status --kill-after=60 "${PIPELINE_BUDGET_S}" \
  /usr/bin/python3 scripts/recreate_v0_full_corpus/run_full_corpus.py \
  >> data/recreate_v0_full_corpus/run_full_corpus.log 2>&1
PIPE_RC=$?
log "STAGE 1: pipeline exit rc=$PIPE_RC"
update_state "pipeline" "done" "$PIPE_RC"

# ---- Stage 2: Sweep early-exit stubs (unconditional) --------------------
log "STAGE 2: sweep_early_exit_stubs"
/usr/bin/python3 scripts/recreate_v0_full_corpus/sweep_early_exit_stubs.py \
  > data/recreate_v0_full_corpus/sweep.log 2>&1
SWEEP_RC=$?
log "STAGE 2: sweep rc=$SWEEP_RC"
update_state "sweep" "done" "$SWEEP_RC"

# ---- Stage 3: Cross-band analysis ---------------------------------------
log "STAGE 3: cross_band_analysis"
/usr/bin/python3 scripts/recreate_v0_full_corpus/cross_band_analysis.py \
  > data/recreate_v0_full_corpus/cross_band.log 2>&1
CB_RC=$?
log "STAGE 3: cross_band rc=$CB_RC"
update_state "cross_band" "done" "$CB_RC"

# ---- Stage 4: Verdict ---------------------------------------------------
log "STAGE 4: verdict"
/usr/bin/python3 scripts/recreate_v0_full_corpus/verdict.py \
  > data/recreate_v0_full_corpus/verdict.log 2>&1
V_RC=$?
log "STAGE 4: verdict rc=$V_RC"
update_state "verdict" "done" "$V_RC"

# ---- Stage 5: Write report ----------------------------------------------
log "STAGE 5: write_report"
/usr/bin/python3 scripts/recreate_v0_full_corpus/write_report.py \
  > data/recreate_v0_full_corpus/write_report.log 2>&1
WR_RC=$?
log "STAGE 5: write_report rc=$WR_RC"
update_state "write_report" "done" "$WR_RC"

# ---- Stage 6: Anchor preservation ---------------------------------------
log "STAGE 6: anchor_preservation"
if [ -f scripts/recreate_v0_full_corpus/anchor_preservation.py ]; then
  /usr/bin/python3 scripts/recreate_v0_full_corpus/anchor_preservation.py \
    > data/recreate_v0_full_corpus/anchor_preservation.log 2>&1
  AP_RC=$?
  log "STAGE 6: anchor_preservation rc=$AP_RC"
  update_state "anchor_preservation" "done" "$AP_RC"
else
  log "STAGE 6: anchor_preservation script missing — will be written by orchestrator continuation"
  update_state "anchor_preservation" "skipped" "0"
fi

# ---- Stage 7: Tests -----------------------------------------------------
log "STAGE 7: tests"
PYTHONPATH=. /usr/bin/python3 tests/test_recreate_v0_full_corpus.py \
  > data/recreate_v0_full_corpus/tests.log 2>&1
T_RC=$?
log "STAGE 7: tests rc=$T_RC"
update_state "tests" "done" "$T_RC"

# ---- Stage 8: Validators (promise_check + org_check) --------------------
log "STAGE 8: promise_check"
/usr/bin/python3 -m long_exposure.tools.promise_check . \
  > data/recreate_v0_full_corpus/promise_check.log 2>&1
PC_RC=$?
log "STAGE 8: promise_check rc=$PC_RC"
update_state "promise_check" "done" "$PC_RC"

log "STAGE 9: org_check"
/usr/bin/python3 -m long_exposure.tools.org_check . \
  > data/recreate_v0_full_corpus/org_check.log 2>&1
OC_RC=$?
log "STAGE 9: org_check rc=$OC_RC"
update_state "org_check" "done" "$OC_RC"

# ---- Stage 10: Ledger events (only if verdict exists) -------------------
if [ -f data/recreate_v0_full_corpus/verdict.json ] && [ -f tools/_c39_clone0_emit_events.py ]; then
  log "STAGE 10: ledger emitter"
  /usr/bin/python3 tools/_c39_clone0_emit_events.py \
    > data/recreate_v0_full_corpus/ledger_emit.log 2>&1
  LE_RC=$?
  log "STAGE 10: ledger_emit rc=$LE_RC"
  update_state "ledger_emit" "done" "$LE_RC"
else
  log "STAGE 10: ledger emitter skipped (missing prerequisites)"
  update_state "ledger_emit" "skipped" "0"
fi

log "session2_orchestrator COMPLETE"
update_state "orchestrator" "complete"

echo ""
echo "======== SESSION 2 ORCHESTRATOR SUMMARY ========"
echo "Pipeline RC: $PIPE_RC"
echo "Sweep RC:    $SWEEP_RC"
echo "Cross-band RC: $CB_RC"
echo "Verdict RC:  $V_RC"
echo "Write-report RC: $WR_RC"
echo "Tests RC:    $T_RC"
echo "Promise-check RC: $PC_RC"
echo "Org-check RC: $OC_RC"
echo "================================================"
