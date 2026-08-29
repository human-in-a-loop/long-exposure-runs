---
title: "Cycles 4-6 Clone 0 Report — M-EAR-1/real-label-training-v0 (Fork 87da4f517029)"
date: "2026-08-29"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
[OUTPUT: report_cycles_4-6_clone_0]

# Cycles 4-6 Clone 0 Report — M-EAR-1/real-label-training-v0 (Fork 87da4f517029)

## Abstract

Cycles 4-6 of clone-0 (fork `87da4f517029`) close `M-EAR-1/real-label-training-v0` at **EAR_v0_INSUFFICIENT** — a first-class negative finding per operator directive. Cycle 4 was a NULL Hold-Pattern recurrence (extraction 11 → advancing; "background task will notify" — but the harness cannot notify a `setsid`-detached PID); cycle 5 was the completion pass (43/43 extraction → SB evaluation → verdict → 5+2 closing ledger events → tests green); cycle 6 is a merge-report-confirmation-only standby (zero ledger events; validated-milestone re-invocation exemption). Fork 87da4f517029 closes 3/3 with no silent failures: clone-0 EAR_v0_INSUFFICIENT, clone-1 PARAM_MOVES_AUDIO, clone-2 MIXED — all first-class deliverables. This is the fifth piece of coherent evidence that the c6 CORN chassis at N≤43-55 cannot beat trivial ordinal baselines under either synthetic or real labels.

## Verdict

**EAR_v0_INSUFFICIENT** (VALIDATED at cycle 5 close; standby-confirmed at cycle 6). SB1 failed at the c22 recipe-envelope-IQR margin of 0.5909 on the partial-corpus (43-song, 54% of c26 Path B target).

## Rubric SHA Anchor Chain

| Location | SHA-256 |
| --- | --- |
| `docs/ear_v0_real_label_training_rubric.md` | `636c2cd0…1bb2e9` |
| `data/ear_v0/rubric_hash.txt` | `636c2cd0…1bb2e9` |
| `verdict.json.rubric_hash` | `636c2cd0…1bb2e9` |

Byte-equal across all three locations; verdict published under frozen rubric without post-hoc bar adjustment.

## Complete 6-Cycle Arc (Clone-0 Chronology)

| Cycle | State | Outcome |
| --- | --- | --- |
| c36-1 | Pre-registration | Rubric + scripts + tests + skeleton (substantive) |
| c36-2 | Extraction 6→8 | NULL — "continuing to wait" (Hold Pattern) |
| c36-3 | Post-audit corrective | Substantive: report skeleton + liveness TSV + `nohup setsid` restart + 6 events |
| c36-4 | Extraction 11→? | NULL — "background task will notify" (harness cannot notify a setsid-detached PID; Hold Pattern recurrence) |
| c36-5 | Completion | Substantive: 43/43 → SB eval → verdict `EAR_v0_INSUFFICIENT` → 5+2 events → tests green |
| c36-6 | (this range close) Standby | Merge-report confirmation only; zero events |

The 2-null pattern is documented in `_manager/hold-pattern-recurrence-clone-0` as a durable finding.

## Cycle Disposition (Merge Range)

| Cycle | Researcher Directive | Worker Action | Auditor Decision |
| --- | --- | --- | --- |
| 4 | Continue extraction supervision | NULL: "background task will notify" | CONTINUE with corrective note |
| 5 | Completion pass | 43/43 extraction → folds → CORN training (`torch.manual_seed(0)` + BLAS pins) → SB1/SB2/SB3 → leak-ablation → verdict.json byte-determinism × 2 → anchor snapshot execution → fill report placeholders → 5+2 closing events | VALIDATED (EAR_v0_INSUFFICIENT) |
| 6 | Standby: merge-report confirmation only | §1 merge-report confirmation; §2 standby exit note; zero ledger events | **VALIDATED (standby)** |

## Merge-Report Confirmation (Cycle 6)

- **Intended path**: `/home/user/music-gen-instance/fork-87da4f517029/clone-0/merge_report.md` — refused by sandbox (consistent with c31/c34/c35 precedent; fourth observation).
- **Fallback path**: `/home/user/long-exposure-runs/music-gen/merge_report.md` overwritten with current c36 clone-0 content (found holding stale c35 clone-2 content prior to overwrite).
- **Content coverage**: milestone status VALIDATED; verdict `EAR_v0_INSUFFICIENT`; SB1/SB2/SB3 numeric values verbatim; per-fold MAE table; rubric SHA; byte-determinism × 2 status; `preview_partial_corpus_v0` caveat with binding c37 prohibitions; pointer to `docs/ear_v0_real_label_training_report.md`; full c37 handoff list including new highest-priority `_manager/ear-sb3-statistic-degeneracy-on-singleton-artists-clone-0`; campaign-level M-EAR-1 status table; fork-closure summary.

## Deliverables (All On Disk at Cycle 5 Close)

| Artefact | Status |
| --- | --- |
| `docs/ear_v0_real_label_training_rubric.md` | frozen at cycle 1; unchanged |
| `docs/ear_v0_real_label_training_report.md` | placeholders filled at cycle 5; §1 caveat verbatim; SB tables populated |
| `scripts/ear_v0/{ingest_ratings,extract_features_v0,train_v0,evaluate_success_bars,leak_ablation_v0,run_all}.py` + `__init__.py` | landed |
| `data/ear_v0/{rubric_hash.txt, per_song_features/*.npy (43), held_out_folds.json, training_result.json, corn_head_v0_real.pt, held_out_predictions.tsv, leak_ablation_summary.json, verdict.json, anchor_preservation.json}` | landed; byte-determinism × 2 confirmed |
| `tests/test_ear_v0_real_label_training.py` (≥14 cases) | green |
| `tests/test_integration_cross_branch.py` §57 | green |

Ledger events (cycles 1-5 total: 6 named + 2 housekeeping under `-clone-0` suffix; cycle 6 zero per standby exemption):

1. `_run/cycle_36_launched-clone-0` (`status: validated` per c35 Branch C convention)
2. `_plan/ear_v0_real_label_training_rubric_frozen-clone-0`
3. `_infra/egress-probe-cycle-36-clone-0`
4. `M-EAR-1/real-label-training-v0` (in-progress → validated verdict roll-up at cycle 5, `EAR_v0_INSUFFICIENT`)
5. `_infra/feature-cache-manifest-emitter-clone-0`
6. `_manager/background-job-supervision-clone-0`
7. `_run/cycle_36_closed-clone-0` (housekeeping)
8. `_archive/cycle-36-scratch-clone-0` (housekeeping)

Plus durable handoff `_manager/hold-pattern-recurrence-clone-0`.

## MINOR Findings (Worker-Flagged, Out of Scope This Range)

1. **Merge-report path fallback recurs** (fourth cycle observing `/home/user/music-gen-instance/*` write refusal: c31, c34, c35, c36). Worker suggestion: codify via `_infra/merge-report-path-fallback-convention`. c37 conductor should either open that infra milestone OR fix the harness path-mapping.
2. **Shared-single-file merge-report slot has a race window** — fallback path is overwritten across clones/cycles; if the merge conductor consumes asynchronously, later-written wins. Worker correctly identified as outside worker scope. c37 handoff: either (a) per-clone fallback path (e.g. `merge_report_<fork>_<clone>.md`) or (b) conductor-side snapshot-on-notify.

## State-Machine Discipline (c29 Lemma Respected)

`M-EAR-1/real-label-training-v0` is a peer sub-milestone under M-EAR-1. NOT a child of terminal-validated `_manager/M-EAR-1-path-B-commit`, `M-EAR-1/{synthetic-label, head-regularization, feature-representation}-audit`, or `M-EAR-1/armed-harness-fixture-reinforcement`.

## Load-Bearing Interpretation (Clone-0 Terminal Note)

The clone-0 negative-verdict outcome joins the c22/c23/c25 chassis invalidations as the **fifth piece of coherent evidence** that the c6 CORN chassis at N≤43-55 cannot beat trivial ordinal baselines under either synthetic or real labels:

| Cycle | Milestone | Chassis Verdict |
| --- | --- | --- |
| c22 | `M-EAR-1/synthetic-label-audit` | insufficient at 55-clip valset |
| c23 | `M-EAR-1/head-regularization-audit` | insufficient (anti-pattern locked) |
| c25 | `M-EAR-1/feature-representation-audit` | insufficient (anti-pattern locked) |
| c31 | `M-EAR-1/armed-harness-fixture-reinforcement` | FIXTURE_READY (harness proven under synthetic dry-run) |
| c36 (this) | `M-EAR-1/real-label-training-v0` | **EAR_v0_INSUFFICIENT** on real 43-song labels |

The c26 Path B commit stands validated in its rule-2 firing logic (defer to real labels). Its rule-2-outcome side (real labels also insufficient at partial corpus) is now empirically settled. **Corpus scale is the leading candidate variable to change; chassis redesign remains locked out.**

## Standing Constraints (Unchanged)

- α pinned at `0.7469387071101908`.
- SHA-256 tiebreak; no PRNG (AST-verified); no `sidecar_nonfactor` imports; no live network.
- Interpreter guard `assert sys.executable == '/usr/bin/python3'` on every new script.
- Byte-determinism × 2 confirmed on all 6 named artefacts: `feature_cache_manifest.json`, `training_result.json`, `corn_head_v0_real.pt`, `held_out_predictions.tsv`, `leak_ablation_summary.json`, `verdict.json`.
- Read-only anchors preserved: c6 feature cache; c22 stability harness; c26 Path B commitment doc. Upstream c6 CORN chassis + feature pipeline NOT mutated.
- c15 `i4_stratified.py` NOT imported. Non-factor sidecar isolation contract preserved.
- Rated audio egress-blocked at `*.googlevideo.com` (unchanged 403; probe non-blocking per usual).
- Ledger hygiene: `narrative` field; `run_id="run-2026-08-28T040704Z"`; nested `confidence:{level,rationale,assessor}`; UUID5 content-hash `event_id`.
- Model artifact labeled `preview_partial_corpus_v0` in provenance per operator directive (NOT calibrated to full 80-song target; caveat prominent in report §1).

## Anti-Patterns Locked (6-Count Stable)

c8 octave-suppression; c11 CLAP/VGGish embedding; c22 stability; c23 head-reg; c25 feature-representation — not re-attempted. c31 STILL_GAP / c35 A anti-pattern surface intact. **No SB threshold post-hoc adjustment** attempted; EAR_v0_INSUFFICIENT surfaced honestly per brief's explicit prohibition.

## Merge Disposition

Fork 87da4f517029 closes **3/3 with no silent failures**:

| Branch | Clone | Milestone | Verdict |
| --- | --- | --- | --- |
| A | clone-0 (this) | `M-EAR-1/real-label-training-v0` | **EAR_v0_INSUFFICIENT** |
| B | clone-1 | `M-GEN-1/palette-driven-batch-v3` | PARAM_MOVES_AUDIO |
| C | clone-2 | `M-DAW-SPIKE-1/vst3-render-nondeterminism-characterization` | MIXED |

All first-class deliverables; each carries the frozen rubric SHA and pre-registration integrity intact.

## Cycle-37 Handoff (Unchanged Verbatim from Cycle-5 Close)

**Primary**:
- **`M-EAR-1/real-label-training-v1`** — 80-song corpus + reweighting + yt-dlp era metadata; SB thresholds frozen; caveat retained.

**Highest priority (must resolve BEFORE v1 runs)**:
- **`_manager/ear-sb3-statistic-degeneracy-on-singleton-artists-clone-0`** — either corpus expansion with within-artist repeats or fallback statistic with small-cell adjustment. Discovered during SB3 leak-ablation on the 43-song corpus.

**New from cycle-6 standby**:
- **`_infra/merge-report-path-fallback-convention`** — fourth-observation of the sandbox-write refusal pattern; worth first-class codification. Per-clone fallback path OR harness path-mapping fix.

**Durable handoffs** (carried across multiple prior cycles):
- `_manager/background-job-supervision-clone-0` (silent-background-job death: n=2 across c31 fixture + c36 extraction).
- `_manager/hold-pattern-recurrence-clone-0` (n=2 NULL cycles this arc).
- Egress-probe-emission-convention.
- `promise_check`-clone-suffix-false-negative-fix.
- Rubric-committee-of-one checklist (post-c36 Branch C first rubric-authoring contradiction observation).
- Assessor-enum discipline note.

**Sibling handoffs (from siblings' merge reports)**:
- `M-GEN-1/palette-driven-batch-v4` (deeper sfizz perturbation, opcode-file rewrite per rule).
- palette-v3 VST3 activation (Dexed-only strict-SMALL tolerance-gate primary; Surge XT bisection deferred; envelope-only both-plugin higher-risk).

## Cumulative Progress

**M-EAR-1 line** (post-c36 Branch A):

| Cycle | Milestone | Verdict |
| --- | --- | --- |
| c22-c25 | Path A chassis chain | exhausted (three-audit chain) |
| c26 | `_manager/M-EAR-1-path-B-commit` | committed; three SBs frozen |
| c31 | `M-EAR-1/armed-harness-fixture-reinforcement` | FIXTURE_READY (six-times-VALIDATED) |
| c36 (this) | `M-EAR-1/real-label-training-v0` | **EAR_v0_INSUFFICIENT** (Path B first real fire) |

**Path B armed harness fired for real** at c36 on the operator's 43-song delivered corpus; egress unblock was not required (rated audio on-disk). The M-EAR-1 armed-not-fired posture that held across c26-c35 has transitioned to armed-and-fired-with-honest-negative-finding. The negative finding is the pre-registration methodology working as designed.

**Pattern durability**: rubric-first pre-registration discipline held for the substantive pipeline (rubric SHA committed before scripts, embedded in `rubric_hash.txt`, embedded verbatim in `verdict.json` at cycle-5 close). Zero post-hoc bar adjustment attempted despite the EAR_v0_INSUFFICIENT outcome; honest surfacing per operator directive.

**c29 state-machine lemma** respected: peer sub-milestone; ledger topology stays a DAG.

**c32 fanout-namespace convention** held under c33 harness-clone-namespace-guard: infra families `-clone-0`-suffixed, substantive `M-*` unsuffixed.

**Silent-background-job supervision + Hold-Pattern recurrence** both observed n=2 this fork; c37 owns crisp codification (`_infra/merge-report-path-fallback-convention` newly added).

**Collision-modeling arc**: closed at `PARTIAL_BP_UNRESOLVED_SHAPE` (c30 terminal); no re-opening proposed.

**Session terminal for clone-0's role in fork 87da4f517029.** No further work permitted on this milestone by clone-0.

[END OUTPUT]
