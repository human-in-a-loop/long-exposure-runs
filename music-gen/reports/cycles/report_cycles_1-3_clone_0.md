---
title: "Cycles 1-3 Clone 0 Report — M-EAR-1/real-label-training-v0 (Fork 87da4f517029)"
date: "2026-08-29"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
[OUTPUT: report_cycles_1-3_clone_0]

# Cycles 1-3 Clone 0 Report — M-EAR-1/real-label-training-v0 (Fork 87da4f517029)

## Abstract

Cycles 1-3 of clone-0 (fork `87da4f517029`) open `M-EAR-1/real-label-training-v0` — the first real-label ear-model training pass on the 43-song rated corpus the operator delivered (10 band-4 + 10 band-5 + 13 band-6 + 10 band-7 across `corpus/ratings/{4,5,6,7}/*.mp3` per `RECEIPTS.md` sha manifests). This fires the pre-registered Path B plan from c26. The milestone is **in-progress at CONTINUE**: rubric frozen, report skeleton landed at the required path, PANNs feature extraction restarted under `nohup setsid` supervision after a silent-halt incident, and running at ~213 s/song (ETA ~2 h from cycle-3 restart at 06:00 UTC; 11/43 songs cached). SB1/SB2/SB3 numbers are placeholders pending extraction completion. Auditor decision at cycle 3: **CONTINUE** with a light-touch nudge to close the deferred cache-regeneration-determinism half.

## Verdict

**IN-PROGRESS** (three cycles: pre-registration + null Hold Pattern + substantive-with-restart; auditor **CONTINUE** at cycle 3). Verdict `EAR_v0_LANDS / EAR_v0_PARTIAL / EAR_v0_INSUFFICIENT` unresolved pending SB1/SB2/SB3 computation on completed features.

## Rubric SHA Anchor

| Location | SHA-256 |
| --- | --- |
| `docs/ear_v0_real_label_training_rubric.md` | `636c2cd0…1bb2e9` |
| `data/ear_v0/rubric_hash.txt` | `636c2cd0…1bb2e9` |
| Rubric-mtime-before-scripts (git-log fallback) | verified at cycle 1 |

Three SB thresholds cited in report §2:
- **SB1**: MAE beats `min(majority-class, mean-integer)` by margin > cycle-22 recipe-envelope-IQR **0.5909**.
- **SB2**: mean pairwise Kendall τ ≥ **0.4** across 10 stratified bootstrap resamples (c23 threshold).
- **SB3**: leak-test detection ≥ **0.90** at α=1.0 (c6 protocol).

## Cycle Disposition

| Cycle | Researcher Directive | Worker Action | Auditor Decision |
| --- | --- | --- | --- |
| 1 | Pre-register rubric + scaffolding | Rubric frozen; scripts scaffolded under `scripts/ear_v0/`; test scaffolding + `data/ear_v0/rubric_hash.txt` landed; ledger events 1-3 emitted (`_run/…-launched`, `_plan/…-rubric-frozen`, `_infra/…-egress-probe`) | VALIDATED-in-progress |
| 2 | Substantive advance | **NULL Hold Pattern** ("check if it finished yet"); auditor flagged coupling and orthogonal-deliverable rule | CONTINUE with strong nudge |
| 3 | Break Hold Pattern; land ≥1 orthogonal deliverable | Report skeleton at required path with operator-critical §1 caveat verbatim; extraction restarted detached (`nohup setsid` PID 20291, heartbeat TSV, `data/ear_v0/extract3.log`); feature-cache manifest emitter smoke-tested; anchor-preservation snapshot script landed as spec; extraction advancing 8 → 11 songs at 213 s/song | **CONTINUE** (light-touch) |

## Report Skeleton (Landed at Required Path)

`docs/ear_v0_real_label_training_report.md` present with the exact structure the brief specified:

- **§1 Operator-critical `preview_partial_corpus_v0` caveat** (verbatim): scale_bounds `{4, 7}` absent `[1, 2, 3]`; 43/80 = 54% of c26 Path B target; class imbalance 10/10/13/10; genre = `deferred_aliased_with_band` (playlist_id aliased with rating band in this corpus); era = `deferred_no_metadata` (post-yt-dlp-metadata cycle).
- **§2 Rubric SHA + three SB thresholds** cited above.
- **§4 `[TBD-post-training: …]` placeholders** for SB1/SB2/SB3 numeric results.
- **§5 Two-path c37 handoff** (see below).
- **§6 Infra handoff** for silent-background-job supervision pattern.

## Ledger Events (6 Shadow Rows Under `-clone-0` Suffix; Closing 5 Owed by Completion Cycle)

1. `_run/cycle_36_launched-clone-0` (`status: validated` per c35 Branch C codified convention)
2. `_plan/ear_v0_real_label_training_rubric_frozen-clone-0`
3. `_infra/egress-probe-cycle-36-clone-0` (`media_ok=false, http_code=403` — rated audio is on-disk; egress probe non-blocking per usual)
4. `M-EAR-1/real-label-training-v0` (in-progress; M-* unsuffixed per c32; NOT validated — SB evaluation has not run)
5. `_infra/feature-cache-manifest-emitter-clone-0` (landed + smoke-tested)
6. `_manager/background-job-supervision-clone-0` (in-progress; durable handoff for silent-background-job failure mode)

**Closing 5 events owed by completion cycle**: milestone-validated verdict roll-up; cross-branch §57 extension; plan-register-if-owed; `_run/cycle_36_closed-clone-0`; housekeeping pair (`_archive/cycle-36-scratch-clone-0`, `_infra/adopt-cycle36-tests-clone-0`).

No `M-EAR-1/*` events beyond the milestone row itself; no `M-GEN-1/*` events. c31 STILL_GAP and c35 A anti-patterns not re-opened.

## Extraction Liveness

- **Current progress**: 11/43 songs cached (advancing 8 → 11 during cycle 3).
- **Rate**: 213 s/song measured; NOT below the pathological 5 min/song threshold.
- **ETA**: ~2 h from cycle-3 restart at 06:00 UTC.
- **Supervision**: `nohup setsid` wrapper with periodic heartbeat to `data/ear_v0/extraction_liveness.tsv`; stdout to `data/ear_v0/extract3.log`. This is the second silent-halt in the campaign (n=2: c31 fixture, c36 extraction) and the correct fix pattern per prior audit.

## MODERATE Findings (Owed by Next Cycle)

1. **Cache-regeneration-determinism deferred half**: cache-hit determinism verified this cycle (bytes SHA-equal to on-disk `.npy`); regeneration-determinism deferred. Brief called for: `cp` a `.npy` aside, delete original, re-invoke extractor on that song, assert fresh output SHA-256 == saved copy. Next cycle: pick one of the 11 cached songs, execute the regeneration half; if unequal, this is CRITICAL — the byte-determinism × 2 gate will fail at completion, and `_manager/feature-pipeline-regeneration-nondeterminism-clone-0` should open immediately with observed diff (SHA-A vs SHA-B, torch/BLAS pin state, numpy version).
2. **Anchor-preservation snapshot test coverage**: script ships un-executed as designed, but brief §4 called for "covered by ≥2 tests in the existing test file." Next cycle: add tests to `tests/test_ear_v0_real_label_training.py` (one invocation on current tree returns non-empty JSON with `unchanged` field; second test asserts boolean flips when a fixture anchor file is perturbed). Cheap; unblocks completion pass.

## MINOR Observations

- `_manager/background-job-supervision-clone-0` narrative should spell out the worker-side orthogonal-deliverable rule (a cycle spawned alongside a supervised background job MUST land ≥1 named on-disk deliverable orthogonal to the job's output before it may sleep/exit) — verbatim recommendation from cycle-3 auditor.

## Deferrals Correctly Documented (Not Verdict-Impairing)

- **Genre column**: `deferred_aliased_with_band` — playlist_id is aliased with rating band in this corpus, so genre remains unseparable-from-signal for this run; c26 §4 authorizes.
- **Era column**: `deferred_no_metadata` — pending post-yt-dlp-metadata cycle.
- **80-song target**: this is `preview_partial_corpus_v0` (54% of c26 Path B target); operator explicitly accepted this as first-class deliverable, NOT calibrated to full 80-song target. Caveat prominent in report §1.

## Standing Constraints (Unchanged)

- α pinned at `0.7469387071101908`.
- SHA-256 tiebreak; no PRNG (AST-verified); no `sidecar_nonfactor` imports; no live network.
- Interpreter guard `assert sys.executable == '/usr/bin/python3'` on every new script.
- Read-only anchors preserved: c6 feature cache; c22 stability harness; c26 Path B commitment doc; c34 palette_v2; c33 palette_render; c35 palette_v2_render.
- c15 `i4_stratified.py` NOT imported.
- Non-factor sidecar isolation contract preserved (AST-grep).
- Rated audio egress-blocked at `*.googlevideo.com` (unchanged 403; probe non-blocking).
- Ledger hygiene: `narrative` field; `run_id="run-2026-08-28T040704Z"`; nested `confidence:{level,rationale,assessor}`; UUID5 content-hash `event_id`.

## Anti-Patterns Locked (6-Count Stable)

c8 octave-suppression; c11 CLAP/VGGish embedding; c22 stability; c23 head-reg; c25 feature-representation — not re-attempted. c35 Branch A VST3-nondeterminism finding survives as fair characterization. c22/c23/c25 anti-patterns NOT re-opened per audit standing note.

## State-Machine Discipline (c29 Lemma Respected)

`M-EAR-1/real-label-training-v0` is a peer sub-milestone under M-EAR-1. NOT a child of terminal-validated `_manager/M-EAR-1-path-B-commit`, `M-EAR-1/{synthetic-label, head-regularization, feature-representation}-audit`, or `M-EAR-1/armed-harness-fixture-reinforcement`.

## Merge Disposition

Merge report at workspace-root fallback per c34 convention (honest; c34-compliant). Six shadow-ledger rows queued for `concat_clone_ledgers`; zero cross-clone collisions under c32 `-clone-0` suffixes. Sibling branches (clone-1 palette-driven-batch-v3, clone-2 vst3-nondeterminism) converged at 2026-08-29T05:44-05:50; clone-0 is now the slow branch — compute-bound on 43 real-audio songs, and c26 explicitly authorized the wait. c37 should be prepared for a "still running" merge report if extraction extends beyond the fork's convergence window.

## Cycle-37 Handoff (Two-Path, Per Report §5)

**Path 1 (if EAR_v0_LANDS or EAR_v0_PARTIAL at 43-song completion)**:
1. **`M-EAR-1/real-label-training-v1`** — larger corpus (target 80-song per c26 Path B) + class-imbalance reweighting; upstream c6 chassis unchanged.

**Path 2 (if EAR_v0_INSUFFICIENT at 43-song completion — first-class deliverable per operator)**:
1. **`M-EAR-1/real-label-training-v1`** — larger corpus + reweighting to unblock SB1; do NOT rebrand as EAR_v0_LANDS via post-hoc bar adjustment.

**Infra handoff (report §6)**: silent-background-job death is a first-class campaign failure mode (n=2: c31 fixture, c36 extraction). Recommendation surviving to c37: (i) any background job spanning cycle boundaries MUST be launched via `nohup setsid` with a periodic heartbeat log the harness can inspect; (ii) any cycle inheriting a supervised background job in flight is DISQUALIFIED from producing "wait" as its sole cycle output and MUST produce ≥1 orthogonal on-disk deliverable.

## Next-Cycle Priority Order (Per Cycle-3 Auditor Guidance)

1. **Close the deferred cache-regeneration-determinism half** on one of the 11 already-cached songs.
2. **Verify anchor_preservation snapshot test coverage** in `tests/test_ear_v0_real_label_training.py` (two tests).
3. **Check extraction progress against ETA**: `ls data/ear_v0/per_song_features/*.npy | wc -l`. If ≥30, completion pass may become possible; if ≥43, execute §7 verbatim (folds → CORN training with `torch.manual_seed(0)` + BLAS pins → SB1/SB2/SB3 → leak-ablation → verdict.json with `rubric_hash` byte-equal → byte-determinism × 2 → anchor snapshot execution → fill report placeholders → emit closing 5 events).
4. **If extraction stalled again**: check `data/ear_v0/extract3.log` tail, `ps -ef | grep extract_features_v0`, `dmesg | tail`. Do NOT restart naïvely a third time. Land diagnostic findings in `data/ear_v0/extraction_liveness.tsv` under `restart_attempt_2_diagnosis` row. Escalate `_manager/background-job-supervision-clone-0`.
5. **If short of 43/43 AND items 1-4 done AND no parallel work**: pause memo becomes defensible; state file count, elapsed vs ETA, resumption trigger (`ls | wc -l == 43`). One sentence.

**Do NOT**: adjust SB thresholds; re-open c22/c23/c25 anti-patterns; re-verify rubric SHA / mtime / interpreter guard / PRNG grep / sidecar_nonfactor grep (cleared cycles ago); modify c6 CORN chassis or feature cache; import c15 `i4_stratified.py`.

## Cumulative Progress

**M-EAR-1 line** (post-c36 Branch A entry):

| Cycle | Milestone | Status |
| --- | --- | --- |
| c22-c25 | `M-EAR-1/{synthetic-label, head-regularization, feature-representation}-audit` chassis chain | Path A exhausted |
| c26 | `_manager/M-EAR-1-path-B-commit` | Committed; three SBs frozen |
| c31 | `M-EAR-1/armed-harness-fixture-reinforcement` | FIXTURE_READY (six-times-VALIDATED) |
| c36 (this) | `M-EAR-1/real-label-training-v0` (Path B first real fire) | **IN-PROGRESS** (CONTINUE at cycle 3; extraction 11/43 with ~2 h ETA) |

**Path B armed harness fires for real**: the c26 pre-registered plan is executing on the operator's 43-song delivered corpus; egress unblock is not required for this training pass because rated audio is on-disk. The M-EAR-1 armed-not-fired posture that has held across c26-c35 is now advancing to armed-and-firing at c36.

**Pattern durability**: rubric-first pre-registration discipline held for the substantive-cycle-3 pipeline (rubric SHA committed before scripts, embedded in `rubric_hash.txt`, ready to embed in `verdict.json` at completion).

**c29 state-machine lemma** respected: peer sub-milestone; ledger topology stays a DAG.

**c32 fanout-namespace convention** held: infra families `-clone-0`-suffixed, substantive `M-*` unsuffixed.

**Silent-background-job supervision pattern** now observed n=2 (c31 fixture, c36 extraction); infra handoff recommendation formalised at report §6 and durably ledgered under `_manager/background-job-supervision-clone-0`. This is the second n-of-2 observation this fork; the auto-termination-on-N-consecutive-standby heuristic carried across prior branches now has a complementary infra recommendation for the opposite failure mode (silent stall instead of standby).

**Collision-modeling arc**: closed at `PARTIAL_BP_UNRESOLVED_SHAPE` (c30 terminal); no re-opening proposed.

[END OUTPUT]
