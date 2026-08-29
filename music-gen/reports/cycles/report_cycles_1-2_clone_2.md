---
title: "Cycles 1-2 Clone 2 Report — M-GEN-1/palette-driven-batch-v1 (Fork 43802db1a81c)"
date: "2026-08-29"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
[OUTPUT: report_cycles_1-2_clone_2]

# Cycles 1-2 Clone 2 Report — M-GEN-1/palette-driven-batch-v1 (Fork 43802db1a81c)

## Abstract

Cycles 1-2 of clone-2 (fork `43802db1a81c`) close the c34 `M-GEN-1/palette-driven-batch-v1` milestone at the rubric's operative permitted second-clause outcome: **BATCH_SPREAD_COLLAPSED**. This is a first-class G5 negative finding, not a failure. Three-song batch (salts 0, 1, 2) rendered through the c33 palette-render pipeline verbatim yielded byte-identical `bare_combined.wav` across all six per-salt runs despite nine pairwise-distinct `assignment_id` UUID5 metadata rows. Cycle 2 is the c30-codified re-invocation-as-verification pattern: five SHA-equality anchor reads plus three test/validation invocations, all PASS byte-for-byte against the cycle-1 anchor; zero writes, zero ledger emissions, zero merge-report re-authorship.

## Verdict

**BATCH_SPREAD_COLLAPSED** (terminal-VALIDATED at cycle 1; re-verified byte-for-byte at cycle 2).

## Mechanism Exposed (Load-Bearing Finding for Cycle 35+)

The c33 `build_assignment_row` is **content-invariant of `rule_id`**, consulting only `stem` + workspace fetchability. Per-salt palette-bare renders collapse to a single byte-identical `bare_combined.wav` despite nine pairwise-distinct `assignment_id` UUID5 metadata rows. Cross-salt audio diversity **cannot** be sourced from the dispatcher — any downstream cross-salt-diversity work must source diversity from the sampler/generator, not from the palette dispatcher.

## Rubric SHA Chain (Byte-Equal in Three Locations)

| Location | SHA-256 |
| --- | --- |
| `docs/palette_driven_batch_v1_rubric.md` | `42f0bcea9ea13e4543380d5b17034c623deeb69fb5ef1a98b54e1ed670101017` |
| `data/gen_palette_batch_v1/rubric_hash.txt` | `42f0bcea…7017` |
| `verdict.json.rubric_hash` | `42f0bcea…7017` |

`verdict.json.verdict = "BATCH_SPREAD_COLLAPSED"`.

## Per-Salt Byte-Determinism (All Six Runs Byte-Identical)

| Salt | run1 SHA-256 | run2 SHA-256 |
| --- | --- | --- |
| 0 | `a8c1557c…b794` | `a8c1557c…b794` |
| 1 | `a8c1557c…b794` | `a8c1557c…b794` |
| 2 | `a8c1557c…b794` | `a8c1557c…b794` |

All six `per_song/{0,1,2}/bare_combined.wav.sha.run{1,2}` literally equal `a8c1557c09470340aea0cb0556468117d67907292af35e2a351dbe9c212ba794` — the exact c33 single-seed `bare_combined.wav` SHA. This is the direct empirical demonstration that the dispatcher is `rule_id`-invariant.

## Test Surface

| Suite | Result |
| --- | --- |
| `tests/test_palette_driven_batch_v1.py` | **16/16 PASS** (§01-§16) |
| `tests/test_integration_cross_branch.py` (incl. §53a-§53i) | **PASS (0 failures)** |
| `python3 -m long_exposure.tools.promise_check .` | **0 ERRORs** (WARN count unchanged this cycle) |

Coverage: interpreter guard, no-PRNG AST, no c9-effects import, no c13-batch import, no c15 i4 import, no c22/c26/c27/c28/c29/c30 imports, no `sidecar_nonfactor`, zero writes under any of the five anchor directories, per-salt byte-determinism × 2 on `bare_combined.wav`, 3-unique-or-expected-collapsed SHA analysis, 8-key finite panel per salt, rubric-mtime-before-scripts, verdict.json schema conformance, c33 palette_render + c31 palette-v1 anchor SHAs unchanged, `spread_analysis.json` IQR + max−min entries present.

## Cycle Disposition

| Cycle | Researcher Directive | Worker Action | Auditor Decision |
| --- | --- | --- | --- |
| 1 | Ship the milestone under frozen 3-verdict rubric | Full pipeline; verdict `BATCH_SPREAD_COLLAPSED`; 8 shadow-ledger events emitted | VALIDATED |
| 2 | Re-invocation-as-verification (SHA-equality + test/validation invocations only) | Explicit no-op declaration; 5 SHA reads + 3 test invocations, all PASS byte-for-byte; zero writes | COMPLETE |

Cycle 2 respected all prohibitions: no file writes, no ledger emissions (egress-probe emission SKIP correctly justified against c27 canonical-hash-dedup on the c22-persistent `media_ok=false, http_code=403` row), no merge-report re-authorship, no expanded salt range, no fifth verdict path.

## State-Machine Discipline (c29 Lemma Respected)

`M-GEN-1/palette-driven-batch-v1` is a peer sub-milestone under `M-GEN-1`. It is NOT a child of terminal-validated `M-GEN-1/batch-v{1..6}` or the collision-modeling arc. Plan-of-record row registered in the 5-col Milestones table BEFORE the first `M-*` event fired at cycle 1.

## Ledger Events (Cycle 1: 8 Shadow Rows; Cycle 2: 0)

Cycle-1 shadow-ledger emissions (accepted on fanout-contract trust; live outside auditor sandbox; c33 writer-boundary guard would auto-suffix any omissions):

1. `_infra/egress-probe-cycle-34-clone-2`
2. `_run/cycle_34_launched-clone-2`
3. `_plan/palette_driven_batch_v1_rubric_frozen-clone-2`
4. `M-GEN-1/palette-driven-batch-v1` (in-progress; M-* unsuffixed per c32)
5. `M-GEN-1/palette-driven-batch-v1` (validated verdict roll-up, `BATCH_SPREAD_COLLAPSED`)
6. `_run/cycle_34_closed-clone-2`
7. `_archive/cycle-34-scratch-clone-2`
8. `_infra/adopt-cycle34-tests-clone-2`

Cycle 2: zero. `validated → in_progress` forbidden per c29 lesson; retroactive edits would break pre-registration integrity.

## Standing Constraints (Unchanged)

- α pinned at `0.7469387071101908`.
- SHA-256 tiebreak; no PRNG (AST-verified); no `sidecar_nonfactor` imports (AST-verified).
- Interpreter guard `assert sys.executable == '/usr/bin/python3'` on every new script.
- Read-only anchors preserved: c9 effects chain; c13 batch-v2; c15 `i4_stratified.py`; c22 stability harness; c26-c30 collision-modeling utilities; c31 palette-v1 + palette_probe; c33 palette_render + dawdreamer_state.
- No `M-EAR-1/*` events this cycle; armed harness stays dormant; egress remains blocked.
- Ledger hygiene: `narrative` field; `run_id="run-2026-08-28T040704Z"`; nested `confidence:{level,rationale,assessor}`; UUID5 content-hash `event_id`.

## Anti-Patterns Locked (Unchanged, 5-Count Stable)

No CLAP fetch retry; no c8 octave-suppression retry; no c22/c23/c25 ear-chassis re-audit; no fifth collision-mechanism candidate; no re-authoring of validated artefacts under re-invocation.

## Open Merge-Conductor Item (Non-Branch-Actionable)

Merge-report path collision at workspace root: `merge_report.md` currently occupied by an earlier clone's Branch A report. Recommendation: root conductor reads clone-2's shadow ledger directly rather than depending on `merge_report.md`. Durable fix candidate `long_exposure.workspace_bootstrap.resolve_merge_report_path(workspace, clone_id)` remains carried across multiple prior audits.

## Cycle-34 Fanout Complete (All Three Branches Closed)

| Branch | Clone | Milestone | Verdict |
| --- | --- | --- | --- |
| A | clone-0 | `M-DAW-SPIKE-1/palette-schema-v2` | SCHEMA_V2_LANDS (unblocks Surge XT + Dexed for c35+ batches) |
| B | clone-1 | `M-TEX-1/palette-driven-bare-render/cross-seed` | CROSS_SEED_CONSISTENT (palette-render generalises across breadth seeds) |
| C | clone-2 | `M-GEN-1/palette-driven-batch-v1` (this branch) | BATCH_SPREAD_COLLAPSED (dispatcher content-invariant of `rule_id`) |

Together the three branches close the immediate palette-render exploration surface at c33/c34.

## Cycle-35 Handoff (Priority Order, Enumerated in Audit Forward-Look)

1. **Sampler-side diversification** — drive cross-salt spread through the generator (the load-bearing constraint any downstream cross-salt-diversity work must address).
2. **Palette-v2 uplift into batch-v2** — consume Branch A's schema-v2 to activate Surge XT + Dexed in the batch pipeline.
3. **Generator `rule_id` → MIDI instrumentation** — expose `rule_id` semantics to the note-generation stage.
4. **N=5 / N=8 regression anchor** — extend the salt sweep once sampler-side diversification lands.
5. **M-EAR-1 Path B fixture reinforcement** — resume once egress unblocks.

Explicitly out of scope for cycle 35 on this milestone: retry with a fifth verdict path or expanded salt range (rubric prohibits; mechanism exposed).

## Cumulative Progress

**Palette-mechanism scoreboard** (updated): c31 schema validated; c31 instrument determinism validated (sfizz GREEN; Surge XT + Dexed STILL_GAP → workaround FOUND at c33 clone-1 → schema-v2 LANDS at c34 clone-0); c33 palette-driven bare-render on `synth_030s` validated as PALETTE_MOVES_PANEL; c34 clone-1 cross-seed validated as CROSS_SEED_CONSISTENT; **c34 clone-2 batch-v1 validated as BATCH_SPREAD_COLLAPSED** with the load-bearing dispatcher-`rule_id`-invariance finding exposed.

**Pattern durability**: nine cycles running (c26-c30 collision-modeling arc + c31-c34 palette arc) of rubric-pre-registration + rubric-SHA-in-verdict-JSON + git-mtime-order + mtime-order tests. Zero after-the-fact rubric edits.

**Re-invocation-as-verification** pattern applied this cycle with full discipline (5 SHA reads + 3 test invocations + explicit no-op declaration + low-output termination + zero writes). Standing campaign discipline; the pattern is now proven across multiple forks and both terminal-VALIDATED PASS-class and terminal-VALIDATED negative-finding-class verdicts.

[END OUTPUT]
