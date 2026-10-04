#!/usr/bin/env bash
# v6 Phase 0 — stage-by-stage runbook for re-running the v5 rule extractors + generator on the 29-song corpus.
#
# created: 2026-10-04   milestone: M-V6-DATA-0/run-pipeline-v6
#
# Usage:  scripts/v6/run_pipeline_v6.sh [--from <stage>] [--to <stage>] [--force] [--list] [--dry-run]
# Stages (in order):
#   manifest tempo bootstrap transcribe content_gate recanonicalize harmony groove form_plan bass_pitch melody_vomm
#   velocity comping generate
# Each stage has an idempotent "done" check (skipped unless --force / FORCE=1) and logs to data/v6/logs/<stage>.log.
# Where a v5 script's hard-coded assumption breaks on this corpus, the stage calls a thin scripts/v6 wrapper that imports
# the v5 module and patches the constant in-process (velocity_v6.py, form_plan_v6.py, generate_v6.py); scripts/v5 is
# never edited. The transcribe stage only PRINTS the pinned command and launches it detached (multi-hour); it is SKIPPED
# with a clear message while workspace/learned_transcribers_venv/bin/muscriptor (or the model weights) is absent.
set -euo pipefail

WS="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$WS"
PY=/usr/bin/python3
export PYTHONHASHSEED=0 SOURCE_DATE_EPOCH=1756463424 TZ=UTC LC_ALL=C.UTF-8 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1

STAGES=(manifest tempo bootstrap transcribe content_gate recanonicalize harmony groove form_plan bass_pitch melody_vomm velocity comping generate)
FROM=manifest
TO=generate
FORCE="${FORCE:-0}"
DRY=0
LOGDIR=data/v6/logs
CORPUS=data/v5/corpus
MANIFEST=$CORPUS/corpus_manifest.json
OVERRIDES_C86=$CORPUS/tempo_overrides_c86.json
MUSCRIPTOR_BIN=workspace/learned_transcribers_venv/bin/muscriptor
MUSCRIPTOR_MODEL=workspace/models/muscriptor-medium/model.safetensors
TRANSCRIBE_CMD="$PY scripts/v5/transcribe_full_length.py --manifest $MANIFEST --tempo-dir $CORPUS"
TRANSCRIBE_LOG=data/v5/logs/transcribe_v6.log

while [[ $# -gt 0 ]]; do
  case "$1" in
    --from) FROM="$2"; shift 2 ;;
    --to) TO="$2"; shift 2 ;;
    --force) FORCE=1; shift ;;
    --dry-run) DRY=1; shift ;;
    --list) printf '%s\n' "${STAGES[@]}"; exit 0 ;;
    -h|--help) sed -n '2,16p' "$0"; exit 0 ;;
    *) echo "unknown arg: $1" >&2; exit 2 ;;
  esac
done

idx() { local i; for i in "${!STAGES[@]}"; do [[ "${STAGES[$i]}" == "$1" ]] && { echo "$i"; return; }; done; echo "unknown stage: $1" >&2; exit 2; }
FROM_I=$(idx "$FROM"); TO_I=$(idx "$TO")
mkdir -p "$LOGDIR" data/v5/logs

log()  { printf '[%s] %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$*"; }
die()  { log "STOP: $*"; exit 1; }
n_songs()  { $PY -c "import json;print(sum(1 for s in json.load(open('$MANIFEST'))['songs'] if s.get('in_v5_corpus')))" 2>/dev/null || echo 0; }
shas()     { $PY -c "import json;print(' '.join(s['sha16'] for s in sorted(json.load(open('$MANIFEST'))['songs'],key=lambda s:s['v5_priority_rank']) if s.get('in_v5_corpus')))"; }
landed()   { local s out=""; for s in $(shas); do [[ -f $CORPUS/$s/transcription_manifest.json ]] && out="$out $s"; done; echo $out; }
n_landed() { echo "$(landed)" | wc -w; }
newer()    { [[ -f "$1" && -f "$2" && "$1" -nt "$2" ]]; }  # $1 newer than $2
json_get() { $PY -c "import json,sys;d=json.load(open('$1'))
for k in '$2'.split('.'):
    d=d[int(k)] if isinstance(d,list) else d[k]
print(d)" 2>/dev/null; }

# ----------------------------------------------------------------------------------------------------- done checks
done_manifest()      { [[ -f $MANIFEST ]] && [[ "$(json_get $MANIFEST summary.n_songs)" == "29" ]] && [[ -f data/v6/corpus/corpus_manifest_v6.json ]]; }
done_tempo()         { local s; [[ -f data/v6/corpus/tempo_v6_summary.json ]] || return 1; [[ "$(json_get data/v6/corpus/tempo_v6_summary.json validation.all_pass)" == "True" ]] || return 1
                       for s in $(shas); do [[ -f $CORPUS/$s/tempo_v5.json ]] || return 1; done; }
done_bootstrap()     { return 1; }   # always re-run: idempotent, cheap, refreshes derived files
done_transcribe()    { [[ "$(n_landed)" -eq "$(n_songs)" ]]; }
done_content_gate()  { [[ -f $CORPUS/content_blocked.json ]] && [[ "$(json_get $CORPUS/content_blocked.json n_landed)" == "$(n_landed)" ]]; }
overridden_landed()  { local s out=""; for s in $($PY -c "import json;print(' '.join(json.load(open('$OVERRIDES_C86'))))"); do [[ -f $CORPUS/$s/transcription_manifest.json ]] && out="$out $s"; done; echo $out; }
done_recanonicalize(){ local s; for s in $(overridden_landed); do [[ -f $CORPUS/$s/canonical_v5c_reindexed/reindex_manifest.json ]] || return 1; done; }
done_harmony()       { [[ -f data/v5/rules/harmony_markov_v5_full.json ]] && [[ "$(json_get data/v5/rules/harmony_markov_v5_full.json gate.n_landed)" == "$(n_landed)" ]]; }
done_groove()        { [[ -f data/v5/rules/groove_v5_v2_full.json ]] && [[ "$(json_get data/v5/rules/groove_v5_v2_full.json gate.n_landed)" == "$(n_landed)" ]]; }
done_form_plan()     { newer data/v5/rules/form_plan_v5.json data/v5/rules/harmony_markov_v5_full.json; }
done_bass_pitch()    { newer data/v5/rules/bass_pitch_v5.json data/v5/rules/eligible_c84.json; }
done_melody_vomm()   { newer data/v5/rules/melody_vomm_v5.json data/v5/rules/eligible_c84.json; }
done_velocity()      { newer data/v5/rules/velocity_profiles_v5.json data/v5/rules/groove_v5_v2_full.json; }
done_comping()       { newer data/v5/rules/comping_v5.json data/v5/rules/eligible_c86.json; }
done_generate()      { [[ -f data/v5/gen/iteration_01/iteration_rollup.json ]] && [[ -n "$(json_get data/v5/gen/iteration_01/iteration_rollup.json v6_enums.n_regular_songs)" ]]; }

# ----------------------------------------------------------------------------------------------------- stages
stage_manifest()  { $PY scripts/v6/corpus_manifest_v6.py; }
stage_tempo()     { $PY scripts/v6/tempo_v6.py --jobs "${JOBS:-4}"; }
stage_bootstrap() { $PY scripts/v6/bootstrap_v5_inputs.py; }

stage_transcribe() {
  log "pinned transcription command (detached):"
  log "  nohup $TRANSCRIBE_CMD > $TRANSCRIBE_LOG 2>&1 &"
  if [[ ! -x $MUSCRIPTOR_BIN ]]; then
    log "SKIP transcribe: $MUSCRIPTOR_BIN is missing (MuScriptor venv not provisioned; a separate approval covers installing it + the model weights)."
    log "     When present, re-run: scripts/v6/run_pipeline_v6.sh --from transcribe   (or paste the command above)."
    return 3
  fi
  if [[ ! -f $MUSCRIPTOR_MODEL ]]; then
    log "SKIP transcribe: model weights $MUSCRIPTOR_MODEL are missing (scripts/v3_spine/recreate_v3.py:78 hashes them at launch)."
    return 3
  fi
  if [[ -f $CORPUS/transcription_progress.json ]]; then
    local pid; pid=$(json_get $CORPUS/transcription_progress.json pid)
    if [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null; then
      log "transcription already running (pid $pid); landed $(n_landed)/$(n_songs). Not relaunching."; return 3
    fi
  fi
  $PY scripts/v5/transcribe_full_length.py --manifest $MANIFEST --tempo-dir $CORPUS --dry-run --max-songs 1 >/dev/null || die "transcribe dry-run failed (tempo_v5.json / manifest keys?)"
  nohup $TRANSCRIBE_CMD > $TRANSCRIBE_LOG 2>&1 &
  log "launched pid $! -> $TRANSCRIBE_LOG; landed so far $(n_landed)/$(n_songs). Re-run with --from content_gate once it completes."
  return 3
}

stage_content_gate() {
  [[ "$(n_landed)" -ge 1 ]] || die "content_gate: no song has landed (transcription_manifest.json absent for all)"
  $PY scripts/v5/content_gate_v5.py --manifest $MANIFEST --corpus-dir $CORPUS
}

stage_recanonicalize() {
  local songs; songs=$(overridden_landed)
  if [[ -z "$songs" ]]; then log "recanonicalize: no landed song carries a tempo override — nothing to do"; return 0; fi
  $PY scripts/v5/recanonicalize_tempo_v5.py --corpus-dir $CORPUS --resolution $CORPUS/tempo_f4_operator_resolution_c86.json --songs $songs
}

stage_harmony() {
  $PY scripts/v5/harmony_v5.py --manifest $MANIFEST --corpus-dir $CORPUS --out-dir data/v5/rules \
      --out-name harmony_markov_v5_full.json --per-song-subdir per_song_c84 --tempo-overrides $OVERRIDES_C86
  [[ -f data/v5/rules/harmony_markov_v5_full.json ]] || die "harmony gated (harmony_v5_gated.json): fewer than 3 unblocked landed songs"
  # eligible_c84/eligible_c86 := the harmony gate (same construction as the c84 files bass_pitch/melody/comping read)
  $PY scripts/v6/bootstrap_v5_inputs.py --only eligible
}

stage_groove()     { $PY scripts/v5/groove_v5_full_c84.py --corpus-dir $CORPUS --manifest $MANIFEST; }
stage_form_plan()  { $PY scripts/v6/form_plan_v6.py --corpus-dir $CORPUS; }
stage_bass_pitch() { $PY scripts/v5/bass_pitch_v5.py; }
stage_melody_vomm(){ $PY scripts/v5/melody_vomm_v5.py; }

stage_velocity() {
  $PY -c "import torch, demucs" 2>/dev/null || die "velocity: torch/demucs not importable under $PY (htdemucs separation needed; Route 1)"
  log "velocity: Route-1 extraction = one htdemucs_6s separation per landed song (minutes each); wrapper patches FOCUS -> all landed songs, R1 -> >= 80 %"
  $PY scripts/v6/velocity_v6.py --corpus-dir $CORPUS --skip-done
}

stage_comping() { $PY scripts/v5/comping_v5.py --corpus-dir $CORPUS --tempo-overrides $OVERRIDES_C86; }

stage_generate() {
  command -v fluidsynth >/dev/null || die "generate: fluidsynth not on PATH (sf2 replay)"
  local n flags="" ; n=$(n_songs)
  flags="--iteration 1 --songs $n --prove-replay --tempo-overrides $OVERRIDES_C86 --cycle 100 --feature 'v6 phase-0 iteration 1 ($n donors)'"
  if [[ -f data/v5/rules/form_plan_v5.json ]]; then flags="$flags --form-plan data/v5/rules/form_plan_v5.json"; else log "generate: form_plan_v5.json absent -> iteration-1 fixed form (A A B A)"; fi
  if [[ -f data/v5/rules/velocity_profiles_v5.json && -f data/v5/rules/bass_pitch_v5.json && -f data/v5/rules/melody_vomm_v5.json ]]; then
    flags="$flags --f2 --velocity-mode f2"
  else log "generate: F2 models incomplete (velocity_profiles / bass_pitch / melody_vomm) -> --f2 omitted"; fi
  if [[ -f data/v5/rules/comping_v5.json ]] && [[ "$(json_get data/v5/rules/comping_v5.json verdict.enum)" == "COMPING_NON_DEGENERATE" ]]; then
    flags="$flags --f3"
  else log "generate: comping_v5.json absent or COMPING_DEGENERATE (generate_v5.py:900 asserts NON_DEGENERATE) -> --f3 omitted"; fi
  log "generate: $PY scripts/v6/generate_v6.py $flags"
  eval $PY scripts/v6/generate_v6.py $flags
}

# ----------------------------------------------------------------------------------------------------- driver
rc_total=0
for i in "${!STAGES[@]}"; do
  st="${STAGES[$i]}"
  (( i < FROM_I || i > TO_I )) && continue
  if [[ "$FORCE" != "1" ]] && "done_$st"; then log "skip $st (done)"; continue; fi
  if [[ "$DRY" == "1" ]]; then log "would run $st"; continue; fi
  log "=== stage $st -> $LOGDIR/$st.log"
  set +e
  ( "stage_$st" ) 2>&1 | tee -a "$LOGDIR/$st.log"
  rc=${PIPESTATUS[0]}
  set -e
  if [[ $rc -eq 3 ]]; then log "stage $st deferred/skipped (see message above); stopping here"; exit 3; fi
  if [[ $rc -ne 0 ]]; then log "stage $st FAILED rc=$rc (log: $LOGDIR/$st.log)"; exit $rc; fi
  log "stage $st OK"
done
log "pipeline done (stages $FROM..$TO)"
exit $rc_total
