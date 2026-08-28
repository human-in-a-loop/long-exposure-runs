---
created: 2026-08-28T19:15:00Z
cycle: 22
run_id: run-2026-08-28T040704Z
agent: worker (post-merge integrator)
milestone: _run/post-merge-integration-fork-cc548ca0c2e5
---

# Cycle-22 Post-Merge Integration — Fork cc548ca0c2e5

## TL;DR

Three clones, all `done`, all deliverables present. **Automatic concat
succeeded** — no bespoke integration driver required. This is the first
2+-clone fork merge in which the cycle-21 workaround was NOT needed:
clone-0's harness auto-write namespacing fix landed at the very fanout
it was designed to fix, so shadow-ledger `_run/report_cycles_*` rows
were already namespaced per-clone at write time and
`concat_clone_ledgers` handled the merge on its own. Ledger 321→348
(+27: 20 shadow + 1 harness auto-write + 6 rollup capstones). All five
test suites green; `promise_check` 0-ERROR / 20-WARN.

## Divergence table

| Clone | Milestone | Verdict | Deliverable | Reconciliation needed? |
|-------|-----------|---------|-------------|------------------------|
| 0 | `_infra/harness-auto-write-namespacing` | validated/high | `docs/harness_report_namespacing_report.md` | None |
| 1 | `M-GEN-1/batch-v4-compound` | validated/high (CONFIRMS_H0_STRICT, 0 pairs) | `docs/gen_batch_v4_compound_report.md` | None |
| 2 | `M-EAR-1/synthetic-label-stability-audit` | **invalidated/high** (C1 FAIL, C2 FAIL, C3 PASS) | `docs/ear_stability_audit_report.md` | None |

No cross-branch conflicts. No overlapping edits to shared files. No
sampler/pipeline/schema changes to reconcile.

## Ledger delta

| Stage | Rows |
|-------|-----:|
| End of cycle 21 | 321 |
| Post automatic concat (20 shadow + 1 harness auto-write) | 342 |
| Post-integration rollup capstones (6) | 348 |
| Delta | +27 |

The +1 harness auto-write is the newly-namespaced
`_run/report_cycles_13-15_clone-1` — the first row in the campaign
written by the fixed writer. It landed as expected in `_run/`-prefixed
form and passed concat validation on the first attempt.

### Rollup capstones emitted (6)

1. `_infra/adopt-fanout-artifacts-fork-cc548ca0c2e5` — adopts
   clone-2's byte-determinism intermediate
   `stability_report.run1.json` (clears 1 orphan WARN).
2. `_plan/register-post-merge-integration-fork-cc548ca0c2e5` —
   plan-of-record touch (rows already added by clones during fanout).
3. `_infra/cross-branch-integration-test-cycle22` — five suites green.
4. `_infra/harness-namespacing-fix-in-production` — retires the
   cycle-21 bespoke-driver reconciliation pattern.
5. `_run/post-merge-integration-fork-cc548ca0c2e5` — fork rollup.
6. `_archive/integration-scratch-fork-cc548ca0c2e5` — closes
   `tools/stale/_emit_cycle22_capstones.py`.

## Test-suite state (all green)

| Suite | Result | Δ vs cycle 21 |
|-------|--------|---------------|
| `tests/test_ledger_writer_validation.py` | 21/21 | 0 |
| `tests/test_fanout_concat_validation.py` | 17/17 | **+2** (clone-0 §16: cure + regression guard) |
| `tests/test_harness_report_namespacing.py` | 7/7 | **+7 (NEW, clone-0)** |
| `tests/test_batch_v4_compound.py` | 6/6 | **+6 (NEW, clone-1)** |
| `tests/test_ear_stability_audit.py` | present (chassis-side of clone-2 audit) | **NEW, clone-2** |
| `tests/test_integration_cross_branch.py` | 0 failures across §1–§32 | **+§31 (batch-v4)** and **+§32 (stability-audit)** |

## `promise_check` state

- **0 ERRORs**.
- 20 WARNs (was 17 end of cycle 21; ±3 = -1 stability run1 adopted;
  +2 gen_first_gen_*.npz feature-cache orphans (unrelated to this
  fork; pre-existing from M-GEN-1/first-generation era); +1 the
  fixed writer's namespaced report file
  `reports/cycles/report_cycles_13-15_clone_1.md` — the harness
  emitted the event but the report file at that exact namespaced
  path is not on disk (only the un-suffixed
  `reports/cycles/report_cycles_13-15.md` exists). This is a
  file-naming side effect of the namespacing fix and is left to
  cycle-23 as handoff item #1).
- All pre-existing categories preserved: 6 trailing-slash artifact
  canonicalization; 1 M-EAR-1 parent roll-up pending; 3 upstream
  `long_exposure/*` out-of-workspace exemption.

## Cycle-21 handoff retirement scorecard

| # | Cycle-21 handoff item | Status |
|---|-----------------------|--------|
| **1** | Harness auto-write per-clone namespacing | ✅ **RETIRED IN PRODUCTION** (clone-0) |
| 2 | `concat_clone_ledgers` transition sweep | still open |
| 3 | `_INFRA_DRIFT_CLASSES` enumeration index | still open |
| **4** | I3 + I4 composition (batch-v4-compound) | ✅ **CLOSED** (clone-1, CONFIRMS_H0_STRICT) |
| 5 | `--n-salts` CLI on batch drivers | still open |
| 6 | Promote `test_salt0_matches_batch_v2_anchor` to cross-branch | still open |
| 7 | VGGish content-caveat surfacing at M-GEN-1 scoring | still open |
| 8 | `M-EAR-1` parent roll-up | still open |
| 9 | Real minor-mode extraction (egress-blocked) | egress-blocked |
| 10 | CORN-head calibration | **INVALIDATED at chassis level** by clone-2 (see below) |

## Clone-2 finding: the negative one

Clone-2's `M-EAR-1/synthetic-label-stability-audit` reports **C1 FAIL,
C2 FAIL, C3 PASS** on the cycle-6 CORN 1–7 head under 10 SHA-256-salted
synthetic-label recipes:

- **C1 (cycle-6 MAE ∈ [5th, 95th])**: cycle-6 reported MAE 0.891, but
  the recipe envelope is [5th=1.032, 95th=2.082] with observed min
  0.909. Cycle-6's number is **outside AND below** the envelope. The
  cycle-6 synthetic-MAE anchor is therefore not reproducible under
  recipe perturbation — it was optimistic for that specific label
  recipe rather than intrinsically low.
- **C2 (mean pairwise Kendall τ ≥ 0.7)**: observed **0.059**, an order
  of magnitude below threshold. Rank predictions across recipes are
  essentially uncorrelated with each other. The chassis' ranking
  signal is dominated by the label recipe.
- **C3 (byte-determinism × 2)**: PASS. Run-1 SHA = Run-2 SHA
  = `36615ad789074bce…`. The audit itself is trustworthy, which makes
  the C1+C2 verdicts trustworthy.

C3 PASS with C1 FAIL and C2 FAIL is the strongest possible
chassis-invalidating signal: the audit reproduces byte-identically,
so the failure is not measurement noise — it is a real property of the
CORN head under synthetic-label choice. **Handoff item #10
(CORN-head calibration) is downgraded from "biggest open credibility
gap" to "chassis invalidated at synthetic-label layer; real-label
retraining is a distinct experiment whose results must be interpreted
under the recipe-sensitivity envelope this audit establishes."**

Clone-2 recorded this as `invalidated/high` in the ledger. That
verdict is preserved verbatim through integration.

## Clone-1 finding: I3 + I4 compose without interference

Clone-1's `M-GEN-1/batch-v4-compound` returns **CONFIRMS_H0_STRICT at
0 collision pairs at N=8**. Anchor cross-reference (32 cells) shows
12/32 batch-v4 renders are byte-identical to prior anchors:

- 8 cells `matches_both` (byte-identical to batch-v3-i3 AND batch-v3-i4)
- 4 cells `matches_i4_only` (salt=4, all 4 file kinds — the H0_STRICT
  witness)
- 12 cells `matches_i3_only` (salts 2/5/6)
- 8 cells `novel` (salts 1/7)

Mechanism: I3 augmentation is additive on the harmonic bucket only
(K_harmonic=10→20) and never removes or renumbers other rule_types, so
non-harmonic renders are byte-identical to i4-only. Harmonic renders
either pick a new D_minor variant or coincidentally re-select an
F_major rule. K_harmonic=20 ≥ N=8 keeps I4's construction proof
intact.

## Clone-0 finding: cycle-21 workaround retired

Clone-0's `_infra/harness-auto-write-namespacing` closes cycle-21
handoff #1 upstream. Replay proof: cycle-21's three shadow ledgers
re-driven through the new writer produce the three main-ledger rows
`_run/report_cycles_1-1_clone-{0,1,2}` byte-identical at full canonical
JSON — stronger than the brief's `(mid, event_id, canonical-excl-ts)`
requirement. `tests/test_fanout_concat_validation.py` §16 adds cases
16 (cure) and 17 (regression guard: an un-namespaced 2+-clone concat
still fails loud, so the standing signal survives).

## Cycle-23 handoff (short list)

1. **Missing namespaced report file**
   `reports/cycles/report_cycles_13-15_clone_1.md` — the fixed writer
   emitted a namespaced event but the on-disk report at that exact
   path is absent (only `reports/cycles/report_cycles_13-15.md`
   exists). Two options: (a) reconcile the harness's report-file
   naming with the ledger event's namespaced mid; (b) archive the
   event as informational-only. Pick (a) unless the harness
   docs clearly state otherwise.
2. **Cycle-17 followup from clone-1**: `M-GEN-1/batch-v4-N16` — extend
   compound to salts 0..15. At N=16, K_form=15 and K_arrangement=15
   fall below N; expected outcome under I4's construction proof is
   collisions land entirely inside form + arrangement. Harmonic
   collisions at N=16 would be a genuine CONFIRMS_H2 signal.
3. **Post-invalidation ear-model direction (arising from clone-2)**:
   the CORN head's synthetic-label sensitivity is now the primary
   open credibility question, not the missing rated audio. Two
   possible responses: (a) redesign the head to be robust to label
   choice (regularization, ordinal loss substitute); (b) accept that
   the synthetic-label chassis cannot demonstrate credibility and
   defer all ear-model calibration to the real-label training that
   will follow egress unblock. Researcher's call.
4. **Trailing-slash artifact canonicalization** — 6 pre-existing WARNs
   in the ledger reference paths ending in `/`. Trivial one-shot
   cleanup; deferred to a future integration cycle unless the
   researcher wants them earlier.
5. **M-EAR-1 parent roll-up** — with clone-2's INVALIDATED/high
   verdict, the parent M-EAR-1 milestone now has a clear terminal
   assessment for the synthetic-label chassis half; combined with the
   validated M-EAR-1/preparation, the parent is close to a
   terminal-state event. Recommend emitting on cycle-23.
6. Handoff items 2, 3, 5, 6, 7, 9 from cycle 21 remain open unchanged.

## Environment (unchanged)

Python 3.11.15, torch 2.13.0+cpu, numpy 1.26.4, mscore3 3.2.3,
DawDreamer 0.9.0, basic-pitch 0.4.0 quarantined venv, SF2 pin
`74594e8f…1cb0`, VGGish rung with cycle-14 content-caveat, single-thread
BLAS pins.

## Sign-off

Fork cc548ca0c2e5 integrated. Ledger 348 rows. 5/5 test suites green.
0 ERRORs / 20 WARNs. Researcher resumes next cycle.
