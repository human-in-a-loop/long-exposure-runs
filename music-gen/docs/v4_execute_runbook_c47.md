# v4 Execute Runbook — c47 (post-omnibus)

Authored: 2026-09-06 (c47 close)
Authority: OPERATOR OMNIBUS ADJUDICATION 2026-09-05 point (5) EXECUTE order
Supersedes: none (new artifact class; preservation-spin retired per point (4))

## Purpose

c47 closed the 6 blocked-on-operator escalations per PATH_A + OPT1
extension + metric-semantics closure. c48+ EXECUTES the pipeline work
per operator directive. This runbook is the concrete resume manual
for the deferred sweeps.

## Preconditions at c48 open

1. **Disk clearance first** — `df -h .` at c47 close: 85% used, at
   c27 prune threshold. c48 must run `prune_after_pin()` sweep on
   `tools/stale/` + any residual `bass_sweep_stage*/` outputs before
   launching. Target: ≤ 82% before first sweep launch.
2. **OP-1 SerialLock still binding** — only one fine-fit driver at
   a time via `data/v4/_run/fine_fit_serial_lock` sentinel.
3. **PATH_A regression bar** — legacy-mode: bit-identical audio +
   composite tolerance |delta| <= 1e-5. Rejects on render-SHA
   mismatch only; composite drift under invariant (f) tolerance is
   PASS.
4. **OPT1 acceptance rule** — composite-relative winner across
   families accepted; 0.40 distance-upper-bound rules out only
   degenerate candidates (distance > 0.40 with no better in any
   family); never blocks best-available.
5. **SF2_CONFIRMED lifted** — per operator directive #3 the
   FORBIDDEN status on non-CG bass sf2 is lifted; verdicts land on
   composite-relative rule.

## Sweep resume commands

All commands run from `/home/user/long-exposure-runs/music-gen` with
`/usr/bin/python3`, sweep-hygiene flags mandatory per PROC
2026-09-05, and detached launch (nohup + setsid + logfile) per c8
policy.

### (a) Rome bass stage-2 (MANDATORY first-launch)

```
nohup /usr/bin/python3 scripts/sound_match/fine_fit_sf2_v2.py \
  --song-sha16 51e433ade2a845e1 \
  --score-and-delete --keep-top 3 --max-audio-mb 500 --disk-abort-pct 90 \
  > data/v4/logs/rome_bass_stage2_c48.log 2>&1 &
```

Grid: c23 stage-1 top-5 programs ∪ program 33 (Electric Bass Finger)
control. Expected top-1 program: prog 33 or prog 35 per WIG c28
precedent (Electric Bass family under distance semantics).
Post-completion: emit `bass.json` + `bass.replay_proof.json` +
`bass_family_verdict.json` under `data/v4/profiles/51e433ade2a845e1/`
(pattern: c28 WIG landing scripts/sound_match/_emit_c28_bass_landing.py).
Verdict enum under OPT1: `SF2_CONFIRMED` (composite top-1) or
`SF2_RULED_OUT` (top-1 distance > 0.40 AND no family-2 alternative
below).

### (b) Peach Dream bass stage-2

Same command with `--song-sha16 88d247468cb6d49f`. c23 stage-1
emb_cos_dist = 0.4437.

### (c) Disco A bass stage-2 (resume interrupted c26 sweep)

Same command with `--song-sha16 cdd2717e52820ff6`. `bass_sweep_stage2/`
dir exists on disk from c26 interrupted run — check whether
`leaderboard.tsv` is complete (216 rows) or partial; resume vs restart
per that state. Do NOT trust a partial leaderboard as pinned data.

### (d) WIG drums stage-1

```
nohup /usr/bin/python3 scripts/sound_match/coarse_sweep_sf2_drums.py \
  --song-sha16 252eb21ce7df7328 \
  --score-and-delete --keep-top 3 --max-audio-mb 500 \
  > data/v4/logs/wig_drums_stage1_c48.log 2>&1 &
```

Additive `--song-sha16` kwarg thread REQUIRED per c28 precedent (as
of c47, coarse_sweep_sf2_drums.py is CG-hardcoded per pre-c28 shape).
c48 first-act: thread the kwarg, land regression test (test pattern
c30 legacy-mode), then launch.

### (e) Disco A drums stage-1

Same as (d) with `--song-sha16 cdd2717e52820ff6`.

## Downstream pipeline (per operator directive #5)

After (a)-(e) land:
- **(b)** WIG + Disco A drums stage-2 (fine_fit_sf2_drums.py with kwarg
  thread); Rome + PD drums stage-1 + stage-2.
- **(c)** Remaining audible stems per per-song `stem_manifest.json` +
  `audibility_*.json` findings (piano/other NULL groundings already
  landed for Rome/PD/WIG; vocals hybrid-overlay for Disco A per
  existing note).
- **(d)** Re-render each song's A/B via `deliver_cg_ab_v4.py`-analog
  scaffold (extend to accept per-song sha16; c17 scaffold ships CG
  path only).
- **(e)** Fresh generation batch: stall budget RESET 8 iterations,
  target 5 passers ≥ 6, plus 1 interpolation-hybrid demo. Donor
  profiles corrected per c22 distance-semantics fix (c22 audit
  already confirmed composite ranks valid; re-label only, no
  re-render for those winners).
- **(f)** Amended completion report `docs/v4_closure_completion_report.md`
  v3 superseding v2 (which superseded c21 v1); pin all 5 songs ×
  all instruments + generation batch results + honest gaps.
- **(g)** Clean re-close: M-V4-CLOSE-1 rollup event; END THE RUN
  declaration per music_gen_v4_prompt.md.

## Sweep hygiene reminders

- `--score-and-delete` per candidate (render → score → delete WAV)
- `--keep-top 3` running top-K only
- `--max-audio-mb 500` per instrument working budget
- `--disk-abort-pct 90` df guard
- Delete all remaining sweep audio after each pin (post-pin cleanup)
- Batch-render-full-grid BANNED

## Prohibitions (unchanged from c46)

- No PRNG in sweep code
- No `sidecar_nonfactor` imports
- No VST3 state APIs (get_state / save_state / save_preset / load_state /
  set_state(bytes) / get_state_chunk / getChunk) — AST-forbidden
- No `--verify-det` on routine runs
- READ-ONLY anchors: `scripts/sound_match/objective.py` `8087ce80…`,
  `scripts/sound_match/_sweep_hygiene_c27.py` `771ff42b…`,
  `scripts/sound_match/_serial_lock_op1.py` `121809db…`

## Success criteria at c48 close (subset — operator directive #5 is multi-cycle)

1. Disk cleared to ≤ 82% before first sweep launch
2. WIG drums stage-1 driver kwarg thread landed + regression test green
3. AT LEAST ONE sweep (either bass or drums) launched detached with
   PID + log pinned
4. NO preservation-spin events emitted (per operator directive #4)
5. Honest deferral rows for remaining sweeps with concrete resume
   commands (this runbook is the canonical reference)
