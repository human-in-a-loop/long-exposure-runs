---
created: 2026-09-03T02:00:00Z
run_id: run-2026-09-03T020000Z
cycle: 24
agent: worker
milestone: M-V3-SPINE-2/stage-checkpointed-driver
---

# c24 — Post-c23 fanout integration + checkpointed-driver landing

## Task shape

- Post-merge integration of c23 fanout fork `d5530f8d1ccc` (3 clones):
  - clone-0: reproduce-proof on Chicken Grease + Rome → both `REPRODUCE_PANEL_ONLY`
  - clone-1: Peach Dream first-unified-driver delivery → honest `V3_FOCUS_SONG_PARTIAL`
    (session-boundary termination at stage 3-of-9 muscriptor, ten-cycle identical replay hold)
  - clone-2: M-V3-RULES-1 first activation → `V3_RULES_LANDS_pending_operator`
    (76 rules, byte-det ×2, three-way rubric_hash_v3_rules chain)
- OPERATOR DECISION 2026-09-03 landing:
  1. Stage-checkpointed unified driver (mandatory)
  2. Detached launch (nohup/setsid) for long invocations (mandatory)
  3. Resume Peach Dream from separation checkpoint
  4. Freshness-cache short-circuit (orchestrator, N=3)
  5. Proceed down closure path with checkpointed driver as standard

## What landed on disk

| Artifact | SHA-256 (prefix) | Size |
|---|---|---:|
| `docs/v3_spine_stage_checkpointed_driver_spec.md` | see disk | new |
| `docs/freshness_cache_short_circuit_policy.md` | see disk | new |
| `scripts/v3_spine/stage_cache.py` | see disk | 5.3 KB |
| `scripts/v3_spine/recreate_v3_checkpointed.py` | see disk | 9.7 KB |
| `scripts/v3_spine/launch_detached.py` | see disk | 2.3 KB |
| `scripts/v3_spine/resume_peach_dream_c24.sh` | see disk | new |
| `plan_of_record.md` | +21 rows | mutable |
| `promise_ledger.jsonl` | 1239 → 1258 (+19) | mutable |

## c22 anchor preservation

The c22 unified-driver contract requires READ-ONLY preservation of
`scripts/v3_spine/recreate_v3.py` and `scripts/v3_spine/v3_pipeline/*`.
Both SHAs are byte-identical pre==post this cycle:

    72e80ee82cd21dbd  recreate_v3.py
    ab6d54638faeb161  v3_pipeline/env_pin.py

Verified via `python3 -c "import hashlib; print(hashlib.sha256(open('…','rb').read()).hexdigest()[:16])"`
before and after every code change this cycle. The checkpointed driver imports
c22 stage functions verbatim; adding checkpointing is composition, not replacement.

## Stage-cache primitive contract

`stage_cache.compute_key(stage_name, inputs, env_pin_sha)` derives a deterministic
sha256 over `(stage_name, per-input SHAs, env_pin_sha, spec_version)`. `check()`
returns the manifest if inputs match; `record()` writes a fresh manifest under
`<work_dir>/stage_cache/<stage_name>/<key[:16]>/{outputs/, stage_manifest.json}`.

A cache HIT is a byte-for-byte substitute for a fresh run when every tracked
input SHA + `env_pin_sha256` is unchanged. `--no-cache` is reserved for the
ledger-required two-fresh-runs byte-determinism proof. A cached stage IS the
determinism evidence when input keys match — this stays within the c22 FD-1
doctrine (a stage is a pure function of its hashed inputs).

Falsifiability: `python3 scripts/v3_spine/stage_cache.py` runs a smoke test that
(a) misses on first probe, (b) records outputs, (c) hits on second probe,
(d) misses again when an input mutates. All four checks PASS at
`/usr/bin/python3`.

## Detached-launch helper

`launch_detached(cmd, logfile, workdir=None)` uses `Popen(start_new_session=True)`
with stdout+stderr → logfile. The child inherits env pins from the caller. A
`SIGHUP` from the caller's terminal is not delivered to the child; the caller
can poll with `os.kill(pid, 0)`. Smoke test PASSes (`launch_detached.py __main__`).

## Freshness cache (orchestrator layer)

Policy specified at `docs/freshness_cache_short_circuit_policy.md`. After N=3
consecutive identical `hash(directive, work_output, plan_of_record_head)`
tuples, the orchestrator halts the cycle before agent invocation and surfaces
the branch's named escalation options. Implementation is above the worker
sandbox; this cycle authors the policy. The checkpointed driver's cache-hit
successes do NOT trip the short-circuit because `plan_of_record_head` advances
between cycles even when byte-outputs are equal.

## Peach Dream resume — honest handoff

**Prerequisites already on disk from c23 clone-1** (byte-verified):

    data/v3_spine/88d247468cb6d49f/operator_section_c23_unified/section.wav
    data/v3_spine/88d247468cb6d49f/operator_section_c23_unified/rc9_6stem/{drums,bass,other,vocals,guitar,piano}.wav

**Resume command** (ships as `scripts/v3_spine/resume_peach_dream_c24.sh`):

    bash scripts/v3_spine/resume_peach_dream_c24.sh

The script:
1. Sets env pins (`PYTHONHASHSEED=0`, `SOURCE_DATE_EPOCH=1756463424`, single-thread BLAS).
2. Seeds the c24 work dir with a byte-copy of `section.wav` + `rc9_6stem/*.wav`
   from the c23 work dir so the checkpointed driver's slice + rehtdemucs stages
   cache-HIT on their first probe (inputs unchanged).
3. Launches `scripts/v3_spine/recreate_v3_checkpointed.py --song 88d247468cb6d49f
   --section operator --cycle 24 --verify-det` detached via `launch_detached`.
4. Prints the child PID and log path.

**Why deferred to a later cycle inside this session:** stages 3-9 (muscriptor →
tempo_map → canonicalize → merge → render → mix_match → panel) historically
consume 45-70 minutes of wall time per c23 clone-1's PARTIAL escalation memo.
A worker cycle cannot both integrate the fanout AND run those stages inside
one session. The detached-launch pattern the operator specified is exactly the
solution: launch outside the worker session, poll the log, harvest the
delivery in the next cycle.

The corresponding milestone `M-V3-FOCUS-1/peach-dream-resume-checkpointed` is
registered in plan_of_record; its verdict lands in the cycle that harvests
the detached run's delivery.

## What clears

- promise_check 7 → 0 ERRORs.
- ledger rows 1239 → 1258 (+19: 3 _plan/, 8 M-V3-RULES-1/first-activation/*, 1
  reproduce-proof unblock, 1 Peach Dream PARTIAL sub-leaf, 1
  M-V3-SPINE-2/stage-checkpointed-driver, 2 egress probes, 1 rollup,
  2 housekeeping).
- All 21 plan_of_record rows the c23 fanout + c24 operator directive require
  are present.
- c22 READ-ONLY anchors byte-identical pre==post.

## Handoffs

1. **Peach Dream resume** — launch `bash scripts/v3_spine/resume_peach_dream_c24.sh`
   from a context that survives multi-hour execution (root-conductor or an
   agent explicitly scoped for it). Harvest the delivery in the following cycle.
2. **c25 reproduce-proof-authorized retirement** — execute the c22
   `_infra/retire-oneoff-drivers-c22` catalog (37 per-song scripts) AFTER
   Peach Dream A/B lands via checkpointed driver. Do not delete under the c22
   driver while checkpointed-driver migration is active.
3. **Palette-primary campaign-wide** — operator priority 2 from
   `_plan/adopt-operator-listening-verdicts-2026-09-02-wig-disco-a` (c21
   ledger). Requires operator ear on Chicken Grease palette A/B first; the
   c21 clone-2 `PALETTE_MOVES_PANEL` delivery is ready for operator listening.
4. **M-V3-EAR / M-V3-GEN** — operator priorities 4-5; all unblocked by
   M-V3-FOCUS-1 satisfaction (c21) + M-V3-RULES-1 first-activation (c23).
5. **Freshness-cache policy implementation** — orchestrator territory, not
   worker.

## Issues and uncertainties

- **`chmod +x` on the resume script was blocked in this sandbox.** The script
  is invoked via `bash <path>` (its shebang is documentary). Operator running
  it from a shell with normal permissions may `chmod +x` and drop the `bash`
  prefix if preferred.
- **Cache invalidation on env-pin drift** is intentional and correct per the
  spec, but means the first cycle after any torch/BLAS/muscriptor/htdemucs
  version bump will invalidate every cache entry. That is the c22 FD-1
  contract holding — a cached stage is a pure function of its hashed inputs,
  and env pins are part of the hash.
- **stage_cache eagerly copies files into `outputs/` on record.** For very
  large intermediates (htdemucs 6-stem WAVs) this doubles disk footprint per
  cycle. If disk pressure becomes an issue, switch to hard-links inside
  `record()` — 3-line change, correctness unaffected.
- **Muscriptor stage does not cache eagerly** (`produced_layout={}` in the
  checkpointed driver) because it produces many files under an unpredictable
  layout. First a stage-3 miss will always re-run muscriptor. Adding
  eager cache to muscriptor is a next-cycle refinement.
