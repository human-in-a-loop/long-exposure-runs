---
title: "Music-Gen — Cycles 20-22"
date: "2026-08-28"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# Music-Gen — Cycles 20-22

## Abstract

Cycles 20-22 covered the fork `392503ab7d47` fanout with three parallel clones and its post-merge integration. **Clone 0** closed the four-cycle SSoT ledger-schema hardening arc (writer c10 → concat c12 → field-type + enum c14 → transitions c15) by adding a canonical `_STATE_TRANSITIONS` frozenset and a `validate_history` per-milestone check wired into both `_lint_clone_shadow` and `promise_check`, catching the state-transition drift class that cycle 14 had honestly misdiagnosed as an enum drift; the ledger's 301 existing per-milestone histories validated with no grandfathering, and the writer / concat suites extended to 21/21 and 15/15 respectively. **Clone 1** empirically confirmed cycle-14 clone-1's I4 stratified rejection sampling construction proof — a straight algorithmic drop-in into the cycle-13 batch-v2 pipeline drove the M-GEN-1 collision floor at N = 8 from 11 pairs to **0 pairs** (PASS, Δ = −11), with per-rule-type counts all zero exactly matching the I4 `predicted_per_type` block, salt=0 legacy byte-identity to batch-v2 song_0 preserved on all four file kinds so the reduction is like-for-like, and all 8 songs byte-distinct so no hidden collision hid inside a render-SHA collapse. **Clone 2** empirically confirmed cycle-14 clone-1's I3 harmonic-corpus-expansion mechanism on a D_minor label-swap augmented ledger (K harmonic 10 → 20) — 11 → **6 pairs (PASS at the low edge of the [6, 9] band)**, with the entire −5 pair reduction inside the harmonic bucket and the four other rule_types byte-unchanged, plus an honest synthetic-relabel caveat for the observed-6 count. Cycle 22's post-merge integration diagnosed a concat-skip on `LedgerConcatError` — the harness auto-writes a per-clone `_run/report_cycles_1-1` row that collided across the three clones because file-order ts monotonicity was violated by clone-2 finishing its report before clone-1 did — and reconciled by serial `append_ledger_event` replay with per-clone id normalization (`_run/report_cycles_1-1_clone-{0,1,2}`). The ledger grew 301 → 321 rows (14 shadow + 6 rollup capstones); `promise_check` returned 0 ERRORs and 17 pre-existing WARNs; all four test suites are green (integration §1–§30 0 failures; writer 21/21; concat 15/15; i4 6/6). 56 orphan artefacts adopted under a single fork-scoped `_infra/adopt-fanout-artifacts-fork-392503ab7d47` rollup.

## Introduction

By the end of cycle 19 three concrete open questions remained on the ledger-write and M-GEN-1 fronts: the state-transition drift class cycle 14 had honestly misdiagnosed as enum drift (surfacing on cycle-13's line-250 `validated → in-progress` without an intervening `reopened`); the two candidate M-GEN-1 collision-floor interventions cycle 14 clone-1 had proposed (I3 corpus-expansion at analytic ≈ 7.75 pairs, and I4 stratified rejection sampling at analytic 0 pairs) which were mechanically specified but not empirically tested; and the recurring pattern that every SSoT hardening cycle finds a new drift class the current validator does not cover. Cycle 20 was the worker pass that ran the fork `392503ab7d47` fanout addressing all three (one clone per open question). Cycle 21 was the researcher pass framing the post-merge integration. Cycle 22 was the integration itself — a pure worker-only cycle with no new research directions, whose job was to reconcile the three shadow ledgers into the main workspace, run the validators and test suites, and produce a capstone.

## Approach

**Fork `392503ab7d47` (cycle 20, three clones, disjoint file trees).**

- **Clone 0 (`_infra/ledger-schema-hardening-v3`).** Extended `long_exposure/tools/_ledger_schema.py` with a canonical `_STATE_TRANSITIONS` frozenset at module top level (15 pairs — the 13 the brief drafted plus two self-loops observed in real ledger rows: `(validated, validated)` for parent-milestone rollups and `(in-progress, in-progress)` for mid-cycle progress notes; both self-loops documented under the same falsifiability escape hatch cycle 14 used for the enum). Added `validate_history(rows_for_milestone)` that groups by `milestone_id`, sorts by `ts`, and rejects illegal consecutive transitions with milestone + `event_ids` + transition-name-annotated messages. Wired into both `_lint_clone_shadow` (pre-concat lint gate) and `promise_check._check_lifecycle` (audit-time gate). Zero caller-side change; `append_ledger_event(workspace, event)` and `concat_clone_ledgers(workspace, fork_dir) → int` public signatures are byte-identical to cycle-14.
- **Clone 1 (`M-GEN-1/batch-v3-i4`).** Implemented `scripts/rules/sampling/i4_stratified.py` per the cycle-14 §I4 spec: per-rule_type SHA-256-ranked draw without replacement, with a cross-salt `already_picked` set forbidding repeat selection at N ≤ K. No PRNG imports anywhere (grep + `test_no_prng` unit test). `scripts/gen/batch_v3_i4.py` imports `run_batch` from `scripts.gen.batch_v2` verbatim — only the sampler swaps; the cycle-9 pinned DawDreamer chain, the SF2 pin `74594e8f…1cb0`, and the M-SCORE-1 bridge all inherit unchanged. Writes to a distinct batch root `data/gen/batch_v3_i4/` so batch-v2 anchor tree is physically untouched.
- **Clone 2 (`M-GEN-1/batch-v3-i3`).** Built `scripts/rules/sampling/i3_dminor.py` producing `data/rules/ledger_i3_dminor.jsonl` (86 rows = 76 source + 10 D_minor variants; every D_minor variant is a `parameters.key` label-swap of one of the 10 F_major harmonic rules with identical `chord_progression`, `scope`, `provenance_pointers` — but since rule_id is content-hashed the key byte-swap produces a distinct row for the sampler). Wrote the augmented ledger to a distinct file so the source 76-row ledger and its append-only invariant are untouched. `scripts/gen/batch_v3_i3.py` imports `run_batch` from `scripts.gen.batch_v2` verbatim at line 51.

Both clone 1 and clone 2 use `scripts.gen.collision_analysis.analyze` from cycle 13 unchanged — like-for-like comparison against the batch-v2 baseline of 11.

**Cycle 21 (researcher).** Framed the post-merge integration: worker-only, no new research direction, no audit-level re-validation of the three clones' internal claims.

**Cycle 22 (post-merge integration).**

- `tools/_integrate_fork_392503ab7d47.py` was authored, executed, and archived to `tools/stale/` on completion. The driver serially replays each clone's shadow-ledger events via `append_ledger_event` (which invokes the writer's `validate_history`, permitting the `validated → validated` self-loop per clone-0's `_STATE_TRANSITIONS`).
- The one concat-skip encountered — `LedgerConcatError` on a per-clone `_run/report_cycles_1-1` row that the harness auto-writes at reporting time — was diagnosed as **harness behaviour, not clone behaviour**: file-order across clones (0 → 1 → 2) had `ts` `16:53:17 → 16:59:57 → 16:54:07`, and clone-2 finished its report before clone-1 did, so per-clone-milestone file-order `ts` monotonicity failed. Fix: per-clone id normalization (`_run/report_cycles_1-1_clone-{0,1,2}`) at replay time. The concat-skip root cause is hoisted to cycle-22 handoff #1 as a small durable upstream fix (namespace `_run/report_cycles_1-1` per clone at write time so future fork merges do not require this reconciliation).
- Six rollup capstones emitted (adopt-orphans, plan-register, cross-branch-test, shadow-concat-skip-reconciliation, post-merge-run, archive-driver).

## Findings

### Clone 0 — `_infra/ledger-schema-hardening-v3` (`validated/high`, `COMPLETE`)

The full-ledger dynamic sweep passed 301/301 rows (grew to 301 during clone runtime as two sibling events landed mid-run: `_plan/register-content-flip-milestone`, `M-TEX-1/panel/embedding/content-flip-analysis`). Observed distinct consecutive transitions in the current ledger: 7 pairs, all a proper subset of `_STATE_TRANSITIONS`. The cycle-13 line-250 pattern (`validated → in-progress` without a preceding `reopened`) is rejected at both the writer gate (`LedgerAppendError`) and the pre-concat lint gate (`LedgerConcatError`), each with milestone + `event_ids` + `_STATE_TRANSITIONS` token in the message and the ledger file line count unchanged on rejection (atomicity preserved). The bridging sequence `validated → reopened → in-progress` is accepted. `_lint_clone_shadow` on a shadow carrying the same illegal pair raises `LedgerConcatError` naming shadow path, milestone, and transition — the `<shadow_path>:<line>` annotation established in cycle 14 flows through. Public API of both `append_ledger_event` and `concat_clone_ledgers` byte-identical to cycle 14. `_STATUS_ENUM is STATUS_VALUES` identity preserved. Writer suite extended 18 → 21; concat suite extended 13 → 15; cross-branch integration test §1–§30 PASS 0 failures.

### Clone 1 — `M-GEN-1/batch-v3-i4` (`validated/high`, `COMPLETE`)

**Prediction test:** predicted 0 pairs at N = 8 (analytic construction proof); observed **0 raw / 0 coerced (PASS)**; Δ = −11 vs batch-v2 baseline. Per-rule-type breakdown matches the I4 `predicted_per_type` block exactly:

| rule_type | batch-v2 pairs | batch-v3-i4 pairs | Δ |
|---|---:|---:|---:|
| harmonic | 6 | 0 | −6 |
| rhythmic | 2 | 0 | −2 |
| melodic | 2 | 0 | −2 |
| form | 0 | 0 | 0 |
| arrangement | 1 | 0 | −1 |
| **total** | **11** | **0** | **−11** |

**Anti-artefact checks (each one could have made the zero misleading, all came back clean):**

- Salt=0 legacy anchor: `data/gen/batch_v3_i4/song_0/*` SHA-identical to `data/gen/batch_v2/song_0/*` on all four file kinds (`musicxml d3d75dfb…`, `midi 80dd3420…`, `bare 669fabde…`, `effects 918c8aaa…`) — the reduction is a like-for-like comparison, not a wholesale sampler replacement.
- All 8 songs byte-distinct across every file kind (8/8 distinct SHAs per artefact class) — no render-SHA collapse masking a hidden collision.
- Zero coherence-gate coercions on every one of the 8 salts — the cycle-14 §7.2 pre-registered blind spot ("gate rewrites might introduce cross-type interactions") did not fire on this configuration; the report honestly does *not* generalise this to a "free consistency dividend" claim.
- Batch-v2 anchor tree physically unmodified: `find data/gen/batch_v2 -newer scripts/rules/sampling/i4_stratified.py` returns empty.
- Source ledger `data/rules/ledger.jsonl` SHA `a6fd53e9…` unchanged.

Determinism × 2: 56/56 SHA-256 matches across 8 songs × 7 artefacts. Unit tests 6/6 (`test_salt0_matches_batch_v2_anchor`, `test_determinism_same_input_same_output`, `test_distinct_salts_distinct_outputs`, `test_stratification_predicate_on_synthetic_corpus`, `test_no_prng`, `test_no_sidecar_import`).

### Clone 2 — `M-GEN-1/batch-v3-i3` (`validated/high`)

**Prediction test:** predicted 7.75 pairs (report headline) or 8.24 pairs (`intervention_proposal.json` H = 10 sweep) at N = 8; PASS band [6, 9]; observed **6 raw / 6 coerced (PASS at the low edge)**. Per-rule-type v2 → v3-i3:

| rule_type | v2 (K, pairs) | v3-i3 (K, pairs) | Δ |
|---|---|---|---:|
| harmonic | (10, 6) | (20, 1) | **−5** |
| rhythmic | (18, 2) | (18, 2) | 0 |
| melodic | (18, 2) | (18, 2) | 0 |
| form | (15, 0) | (15, 0) | 0 |
| arrangement | (15, 1) | (15, 1) | 0 |
| **total** | 11 | **6** | **−5** |

The entire five-pair reduction is inside the rule_type whose K doubled; the four non-harmonic buckets are byte-unchanged. BP-expected harmonic under H = 20 = 1.40; observed 1 within single-sample variance. Determinism × 2: 62/62 SHA-256 matches. Cycle-9 chain imported unchanged (grep-confirmed at `scripts/gen/batch_v3_i3.py:51`); cycle-13 batch-v2 anchors preserved by construction (distinct batch root); source ledger untouched; augmented ledger in distinct file.

**Honest synthetic-relabel caveat:** the 10 D_minor rows keep the F_major `chord_progression` verbatim and only relabel `parameters.key`. The mechanism claim (harmonic K doubles → BP-expected harmonic halves → observed harmonic ~halves) is empirically confirmed because rule_id is content-hashed and the key swap changes the content bytes so the sampler sees 20 distinct harmonic rules. The *observed 6* comes with the caveat that when rated audio unblocks and real minor-mode scores are extracted, the observed count could move within BP variance while the mechanism verdict stays invariant.

### Cycle-22 post-merge integration

The concat-skip diagnosis and reconciliation was the substantive integration work. Baseline 301 rows → final **321 rows** (+20 = 14 shadow + 6 rollup):

| Bucket | Rows | Detail |
|---|---:|---|
| Clone 0 shadow | +3 | schema-hardening-v3, archive-scratch, report_cycles_1-1_clone-0 |
| Clone 1 shadow | +7 | register, 3× in-progress, validated, archive, report_cycles_1-1_clone-1 |
| Clone 2 shadow | +4 | register, validated, archive, report_cycles_1-1_clone-2 |
| Rollup capstones | +6 | adopt-orphans / plan-register / cross-branch-test / shadow-concat-skip-reconciliation / post-merge-run / archive-driver |

`promise_check` on the 321-row ledger: 0 ERRORs, 17 WARNs, all pre-existing categories (6 trailing-slash canonicalisation on old rows that cannot be rewritten without breaking their content hash / event_id; 1 `M-EAR-1` parent roll-up pending; 7 `data/ear/features/gen_first_gen_*.npz` orphans from cycle-10; 3 upstream `long_exposure/*` out-of-workspace exemption — up from 2 because clone 0 additively references `long_exposure/tools/promise_check.py` in addition to the existing `_ledger_schema.py` and `workspace_bootstrap.py`). 56 orphan artefacts adopted under a single fork-scoped `_infra/adopt-fanout-artifacts-fork-392503ab7d47` rollup (64 batch_v3_i3 artefacts + 64 batch_v3_i4 artefacts + reports + figures + samplers + drivers + augmented ledger + i4 unit test, deduped to 56 unique paths not already tracked).

### Tests at cycle-22 exit

- `tests/test_integration_cross_branch.py` — PASS (0 failures across §1–§30).
- `tests/test_ledger_writer_validation.py` — 21/21 pass (was 18; clone-0 added 19–21).
- `tests/test_fanout_concat_validation.py` — 15/15 pass (was 13; clone-0 added 14–15).
- `tests/test_i4_stratified.py` — 6/6 pass (clone-1 new).

## Discussion

Three things about this range are worth naming.

First, the four-cycle SSoT hardening arc closes as a coherent unit. Cycle 10 established the writer gate; cycle 12 established the concat gate with per-milestone `ts` monotonicity and content-hash tiebreak; cycle 14 added `supersedes_path` type-check and the `status` enum; cycle 15 (this range's clone 0) added state-transition validation via `_STATE_TRANSITIONS` + `validate_history`, wired into both the pre-concat lint gate and the audit-time `promise_check` gate. Every cycle strengthened the SSoT without weakening any prior invariant and without changing any caller-side signature. The specific historical drift the brief pointed at (cycle-13 line-250 `validated → in-progress` without `reopened`) is now categorically impossible to land through any of the write / merge / audit surfaces without an intervening `reopened`, and the falsifiability escape hatch — expand the transition graph rather than reject legitimate historical rows — was used sparingly and honestly for the two observed self-loops with defended documentation. The pattern of using post-merge integration surface as the retrospective driver of the next hardening cycle is the mechanism by which this arc converged; if a fifth drift class ever appears at post-merge integration, the diagnostic ladder should start at Rung 3 ("does the tightened validator catch it, and if not, why?") rather than at Rung 1.

Second, the two M-GEN-1 interventions confirmed exactly the cycle-14 clone-1 predictions and did so in complementary ways. I4 (algorithmic, `validated/high`) drove the within-rule_type contribution to zero via a construction that cannot produce a within-rule_type collision at N ≤ K by definition; the three anti-artefact checks (salt=0 identity preserved, 8/8 distinct SHAs, zero coherence-gate coercions) each independently ruled out a way the zero could have been spurious. I3 (corpus-side, `validated/high`) drove the harmonic-bucket contribution from 6 to 1 by doubling K, leaving the four non-harmonic buckets byte-unchanged — the cleanest possible one-batch confirmation of the "expand-the-dominant-rule-type-pool" mechanism. The two interventions are complementary rather than competing: I4 alone hits zero at N = 8 but has a hard ceiling at the smallest K (harmonic K = 10 on the source ledger, so N > 10 raises `I4SamplerError`); I3 alone reduces the harmonic contribution but does not touch other rule_types. The natural cycle-23+ composition — I4 sampler against I3's augmented ledger at N = 8 and N = 12 — should hit zero with headroom and is the concrete downstream step this range enables.

Third, the concat-skip diagnosis is the branch's most useful non-obvious contribution to future forks. The failure was not a clone defect but a *harness* behaviour: the per-clone `_run/report_cycles_1-1` row the harness auto-writes at reporting time collided across the three clones because clone-2 finished its report before clone-1 did, and per-clone-milestone file-order `ts` monotonicity failed. The reconciliation this range applied (serial replay with per-clone id normalization) is idempotent and works, but the durable fix hoisted to cycle-22 handoff #1 is to namespace `_run/report_cycles_1-1` per clone at write time in the harness, so the next fork with two or more clones does not require this same reconciliation. This is the third such small durable fix the campaign has queued in the harness layer (cycles 10/11 shim; cycle-14 optional-field enumeration; this one), and each of them moves post-merge integration debt closer to zero.

The uncalibrated CORN head and the rated-audio unblock remain the campaign's biggest open credibility gaps; neither moves in this range. The M-EAR-1 parent roll-up is still one of the standing WARNs — a researcher judgment, not an integration action.

## Open Questions

- **I3 + I4 composition test** (cycle-23+). Run this range's I4 sampler against clone-2's I3 augmented ledger at N = 8 and N = 12. I4 alone at N = 12 on the source ledger fails loudly at the harmonic K = 10 ceiling; the augmented ledger's K = 20 opens the headroom. Cheap and empirically informative.
- **Harness auto-write namespacing** (cycle-22 handoff #1). Durable upstream fix: namespace `_run/report_cycles_*` per clone at write time so future fork merges do not require the concat-skip reconciliation. Until this lands, every future fork merge with ≥ 2 clones will hit the same skip; the reconciliation is idempotent so it is safe, but the fix eliminates a class of integration debt.
- **Land I4 as the default sampler** behind a config knob (auditor guidance). Keep `sample_ruleset` for the batch-v2 regression path so the salt=0 legacy anchor and the cycle-13 collision baseline remain intact.
- **Promote `test_salt0_matches_batch_v2_anchor`** to `tests/test_integration_cross_branch.py` as a locked cross-branch regression on the salt=0 identity path.
- **Expose `--n-salts` on the batch driver CLI** so `N > K` attempts fail loudly via the existing `I4SamplerError` rather than silently sampling a stale N = 8 default.
- **Real minor-mode extraction** when rated audio unblocks. Rerun clone-2's I3 test with real D_minor harmonic rules; mechanism verdict is invariant but observed count could move within BP variance.
- **Do not generalise the "free consistency dividend" claim** (I4 report §8 item 2) beyond the exact configuration tested — under an expanded ledger the coherence gate could re-activate.
- **CORN-head calibration** and **rated-audio unblock** — still blocked on egress. `M-INGEST-1/egress-ready-automation` is armed and awaits its two-consecutive-`media_ok=true` trigger.
- **M-EAR-1 parent roll-up** — a researcher judgment on one of the standing WARNs, not an integration action.
- **Fifth-drift-class diagnostic ladder start at Rung 3** — if a future post-merge integration surfaces a drift class the tightened SSoT does not catch, the diagnosis should start with "does the tightened validator catch it, and if not, why?" rather than at the corruption-detection level.

## Appendix: Provenance

**Cycle range:** cycles 20-22.
**Working directory:** `/home/user/long-exposure-runs/music-gen`.
**Session references:** cycle 20 worker `91774a48-cc3c-4b20-a5ba-0a3537bd2a69`; cycle 21 researcher `27fc72bd-e4e9-4767-ad5c-0a15cbcf041b`; cycle 22 worker `3d2e7cb3-30b0-4599-9df0-af79f8db43c0`.

**Sub-agent transcripts (fork `392503ab7d47` clones).**

- Clone 0 (`_infra/ledger-schema-hardening-v3`): researcher `45a3e916-51ce-4b5d-9a31-f0810945ab64`, worker `3778ec06-6112-4b2f-9978-50338e97532e`, auditor `a222f718-34db-4ad5-a49a-af16e5084a02`. Verdict COMPLETE; sub-milestone closes at `validated/high`.
- Clone 1 (`M-GEN-1/batch-v3-i4`): researcher `5b392017-f49d-4053-9c9c-37f3d128ac96`, worker `4447207c-fb43-437b-9ade-b327e7ab7ca2`, auditor `6ffff05c-35b5-4f57-8582-8ba609057c82`. Verdict VALIDATED / COMPLETE; sub-milestone closes at `validated/high`.
- Clone 2 (`M-GEN-1/batch-v3-i3`): researcher `ed834519-770e-4d8e-a193-d979be895294`, worker `bb205777-0d10-401a-a6d4-6cab65d50d48`, auditor `c456daba-7446-4ea0-8c0d-a27f32e8b4be`. Verdict VALIDATED; sub-milestone closes at `validated/high`.

**Deliverables on disk at cycle-22 exit.**

- Clone 0: extensions to `long_exposure/tools/_ledger_schema.py` (`_STATE_TRANSITIONS` frozenset, `validate_history`, `_STATUS_ENUM` alias); wiring into `_lint_clone_shadow` and `promise_check`; `tests/test_ledger_writer_validation.py` +3 cases (18 → 21); `tests/test_fanout_concat_validation.py` +2 cases (13 → 15); `docs/ledger_schema_hardening_v3.md` (285 lines).
- Clone 1: `scripts/rules/sampling/i4_stratified.py`; `scripts/gen/batch_v3_i4.py`; `scripts/gen/collision_count_batch_v3_i4.py`; `data/gen/batch_v3_i4/` (8 song sub-dirs + rollups); `docs/gen_batch_v3_i4_report.md` (15 081 bytes); `docs/figures/batch_v3_i4_collision_heatmap.png`; `tests/test_i4_stratified.py` (6/6 pass).
- Clone 2: `scripts/rules/sampling/i3_dminor.py`; `scripts/gen/batch_v3_i3.py`; `data/rules/{ledger_i3_dminor.jsonl (86 rows), i3_dminor_manifest.json}`; `data/gen/batch_v3_i3/` (8 song sub-dirs + `i3_summary.json`, `collision_analysis.json`); `docs/gen_batch_v3_i3_report.md`.
- Cycle-22 integration: `tools/stale/_integrate_fork_392503ab7d47.py`; `tools/stale/_discover_orphans.py`; workspace-root `merge_report.md` rewritten as cycle-21 fork capstone with 10-point cycle-22 handoff.

**Load-bearing runtime evidence.**

- `_STATE_TRANSITIONS` = frozenset of 15 `(str, str)` tuples; every endpoint drawn from `STATUS_VALUES`; two documented self-loops added under the falsifiability escape hatch.
- `_STATUS_ENUM is STATUS_VALUES` → True (cycle-14 alias preserved).
- Historical sweep at cycle-15 (clone 0): 301/301 rows pass `validate_history`; distinct consecutive transitions observed = 7; proper subset of `_STATE_TRANSITIONS`.
- I4 collision count: raw 0, coerced 0, verdict PASS; Δ = −11; per-rule-type all 0; 56/56 determinism SHAs match; salt=0 legacy identity 4/4 match batch-v2 song_0; all 8 songs byte-distinct.
- I3 collision count: raw 6, coerced 6, verdict PASS; Δ = −5 (entirely in harmonic); BP-expected harmonic under H = 20 = 1.40, observed 1 within variance; 62/62 determinism SHAs match; source ledger and batch-v2 unchanged.
- Cycle-22 ledger: 301 → 321 rows; `promise_check` 0 ERRORs, 17 pre-existing WARNs; 4 test suites green.

**Ledger routing.** Shadow-ledger events emitted per clone into `/home/user/music-gen-instance/fork-392503ab7d47/clone-{0,1,2}/promise_ledger.jsonl` and reconciled at cycle 22 via serial `append_ledger_event` replay with per-clone id normalization on the auto-write `_run/report_cycles_1-1` collision. Six rollup capstones (adopt-orphans / plan-register / cross-branch-test / shadow-concat-skip-reconciliation / post-merge-run / archive-driver). 56 orphan artefacts adopted under a single fork-scoped `_infra/adopt-fanout-artifacts-fork-392503ab7d47`. Upstream `long_exposure/*` out-of-workspace exemption count moved 2 → 3 as expected (clone-0 additively references `promise_check.py`).

**Environment stack unchanged since cycle 10.** `mscore3` 3.2.3 headless; Python 3.11.15; `numpy 1.26.4`; `music21 9.1.0`; `mir_eval 0.8.2`; fluidsynth (Debian) with pinned SF2 `74594e8f…1cb0`; DawDreamer + Surge XT Effects.vst3 at `/usr/lib/vst3/`; basic-pitch 0.4.0 in `workspace/basic_pitch_venv/`; VGGish rung on the texture panel; CORN head under the `synthetic_labels_only` sentinel. Single-thread BLAS pins throughout.

**Rated audio.** Still egress-blocked per `corpus/CORPUS_STATUS.md`. `M-INGEST-1/egress-ready-automation` state machine remains `IDLE`; runtime state files correctly absent until the first live trigger. Not this range's problem; the machine is pre-wired.

**Handoff to next cycle.** The concrete downstream steps queued by this range are (a) the I3 + I4 composition test (cheap, empirically informative, natural cycle-23+ next), (b) the harness auto-write namespacing durable fix (removes a class of post-merge integration debt), (c) landing I4 as the default M-GEN-1 sampler behind a config knob, (d) promoting `test_salt0_matches_batch_v2_anchor` to the cross-branch integration test as a locked regression, and (e) exposing `--n-salts` on the batch driver CLI. Anything requiring rated audio remains a straight-line consequence of the egress-ready state machine firing.
