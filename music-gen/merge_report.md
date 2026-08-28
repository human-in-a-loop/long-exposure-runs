---
created: 2026-08-28T19:25:00Z
cycle: 24
run_id: run-2026-08-28T040704Z
agent: worker
milestone: _run/post-merge-integration-fork-3fbd8c1ab57c
---
# Cycle-24 Post-Merge Integration — Fork 3fbd8c1ab57c

**Fork:** `3fbd8c1ab57c`
**Clones:** 2 (both `done | deliverable=exists`)
**Cross-branch conflicts:** 0
**Shadow-ledger events auto-concat'd:** 14/14 (7 per clone)
**Orphans adopted:** 28
**`promise_check`:** 0 ERRORs / 33 WARNs (all pre-existing carry-over)

## Divergence table

| Clone | Milestone | Verdict | Note |
|-------|-----------|---------|------|
| 0 | `M-GEN-1/batch-v5-n16` | **validated/high** | `NOT_TESTABLE_SAMPLER_EXHAUSTS_AT_N_GT_K` — I4 sampler raises `I4SamplerError` at salt=15 (K_form=15 < N=16). First-class positive empirical finding on the cycle-14 construction proof. |
| 1 | `M-EAR-1/head-regularization-audit` | **invalidated/high** | All 3 regularized variants (ridge / bottleneck / frozen-projector) FAIL C1' AND C2' by ~5×. Head-side-fix hypothesis exhaustively falsified across three orthogonal axes. |

Zero overlap between the two clones' file trees:
- clone-0: `scripts/gen/batch_v5_*`, `data/gen/batch_v5_n16/`, `tests/test_batch_v5_n16.py`, `docs/gen_batch_v5_n16_report.md`, `docs/figures/batch_v5_n16_*.png`, `tools/tmp_batch_v5_run2/`.
- clone-1: `scripts/ear/{_variant_core,model_v2_*,stability_audit_v2_variants,tau_mae_frontier}.py`, `data/ear/head_regularization_audit/`, `tests/test_ear_head_regularization.py`, `docs/ear_head_regularization_audit_report.md`, `docs/figures/ear_head_regularization_*.png`.
- Shared appends only: `plan_of_record.md` (both clones added their milestone row); `tests/test_integration_cross_branch.py` (clone-0 added §33, clone-1 added §34).

## The concat happened automatically (again)

All 14 shadow-ledger `event_id`s were already in the main ledger when this session opened, exactly as with fork `cc548ca0c2e5` in cycle 22. The cycle-22 harness-auto-write namespacing fix (`_infra/harness-auto-write-namespacing`) is now working in production for both 3-clone and 2-clone fanouts. The bespoke per-clone id-normalization workaround from cycle 21 remains retired.

## Ledger events emitted this session (4)

1. `_infra/adopt-fanout-artifacts-fork-3fbd8c1ab57c` — validated/high (28 orphan artifacts adopted: 27 head-reg `_run1_<variant>/_run2_<variant>/` byte-determinism side-by-side outputs + `scripts/gen/plot_batch_v5.py`).
2. `_infra/cross-branch-integration-test-cycle24` — validated/high (all 8 test suites green + batch-anchor invariance recorded).
3. `_run/post-merge-integration-fork-3fbd8c1ab57c` — validated/high (this integration cycle roll-up).
4. `_archive/integration-scratch-fork-3fbd8c1ab57c` — validated/high (one-shot emitter archived to `tools/stale/`).

Total main-ledger rows: 363 → **367** (+4).

## Test suites (all green via `/usr/bin/python3` with `PYTHONPATH=.:/home/user/human-in-a-loop/long-exposure`)

| Suite | Result | Δ vs cycle 22 |
|-------|--------|---------------|
| `test_ledger_writer_validation.py` | 21/21 | 0 |
| `test_fanout_concat_validation.py` | 17/17 | 0 |
| `test_harness_report_namespacing.py` | 7/7 | 0 |
| `test_batch_v4_compound.py` | 6/6 | 0 |
| `test_batch_v5_n16.py` | 7/7 | +7 NEW (clone-0) |
| `test_ear_stability_audit.py` | 12/12 | 0 |
| `test_ear_head_regularization.py` | 6/6 | +6 NEW (clone-1) |
| `test_integration_cross_branch.py` | 0 failures §1–§34 | +§33, +§34 |

## Batch-anchor invariance (aggregate SHA-256 over sorted (relpath, file-SHA) list)

| Batch | File count | Aggregate SHA (first 16 hex) |
|-------|-----------:|------------------------------|
| `data/gen/batch_v2/` | 62 | `2a2a30db5d3d9a76` |
| `data/gen/batch_v3_i3/` | 62 | `1f2c19a7bdb3f8f3` |
| `data/gen/batch_v3_i4/` | 62 | `f3fa079a474ab10b` |
| `data/gen/batch_v4/` | 74 | `5d9dabfabb17f265` |

Clone-0's `batch_v5_anchor_regression.py` reported 32/32 PASS against batch-v4 in-branch, matching the anchor SHA above.

## Key findings by clone

### Clone-0 (`M-GEN-1/batch-v5-n16`, validated/high)

**Verdict:** `NOT_TESTABLE_SAMPLER_EXHAUSTS_AT_N_GT_K` — a first-class positive empirical finding on the cycle-14 construction proof.

The I4 stratified rejection sampler (`scripts/rules/sampling/i4_stratified.py:127-133`) raises `I4SamplerError` at salt=15 on `rule_type=form`: `K_form = 15` and all 15 form rules are already-picked after salts 0..14. Same holds by symmetry for `rhythmic`, `melodic`, and `arrangement` (all K=15). Both run 1 and run 2 failed identically at salt=15 with byte-identical prior-salt SHAs. Salts 0..14 (N=15) rendered successfully with 60/60 byte-determinism ×2 and 32/32 anchor regression PASS vs batch-v4.

**Interpretation.** At N > K per rule_type, the I4 exclusion-set converts the pigeonhole floor from *must-collide* (statistical) into *cannot-sample* (structural). The sampler's structural inability to reach N=16 is the pigeonhole bound made unfalsifiable-within-the-mechanism. Formally: `N_max_producible_by_I4(ledger) = min_K_across_rule_types(ledger)`. For the current I3-augmented ledger, `N_max = 15`.

**Two orthogonal paths clone-0 recommends for cycle 25** to test the construction proof at N > K without modifying `i4_stratified.py`:
1. `scripts/rules/sampling/i4_replacement.py` — new sibling sampler accepting N > K by allowing repeats past K with an explicit collision-recording branch.
2. batch-v6 using cycle-13's `scripts/rules/sampling/sample_rules.py` (no rejection) at N=16 on `ledger_i3_dminor.jsonl`. Closer to batch-v2's baseline and easier to reason about.

Both paths keep the I4 sampler untouched. Ledger-side follow-up: add a `min_K < N` pre-flight guard to any future batch-vN driver at N > 8.

### Clone-1 (`M-EAR-1/head-regularization-audit`, invalidated/high — MAJOR NEGATIVE FINDING)

**Verdict:** All three regularized variants FAIL both C1' (MAE-in-envelope) and C2' (mean τ ≥ 0.4) under the relaxed rubric. C3' (byte-determinism ×2) PASSES uniformly per variant, empirically validating the harness-preservation monkey-patch mechanism.

| Variant | C1' | C2' | C3' | Overall | Byte-det SHA |
|---------|:---:|:---:|:---:|:---:|:---|
| CORN-ridge | FAIL | FAIL (τ ≈ 0.06–0.08) | PASS | **FAIL** | `be9a750e…` |
| CORN-bottleneck | FAIL | FAIL (τ ≈ 0.06–0.08) | PASS | **FAIL** | `f224157c…` |
| CORN-frozen-projector | FAIL | FAIL (τ ≈ 0.06–0.08) | PASS | **FAIL** | `5dd1c9da…` |

**Pre-registered rule-2 firing.** Three orthogonal head-side regularizations at N = 55 clips all land τ ≈ 0.06–0.08, ~5× below C2' = 0.4. The head chassis is not the load-bearing failure surface at 55 clips. Combined with cycle 22's τ ≥ 0.7 invalidation at the stricter bar, this **exhaustively falsifies the head-side-fix hypothesis** in both stricter and relaxed modes.

Anchor invariance held: 6 harness anchor SHAs matched cycle-22 values at run start AND end; PCA basis SHA pinned at `9381ad73…`; feature cache byte-identical pre/post.

**Auditor MODERATE observation (cosmetic, no verdict impact).** Report §7 line 241 conflates two interpretations of C1' — the sentence's "no variant lands inside its own envelope" is false for `frozen_projector` (salt-4 MAE 1.1273 IS inside its [1.0127, 1.9282] envelope), but the C1' verdicts in `variant_verdicts.json` are computed against the constant cycle-6 anchor 0.891 per cycle-22 clone-2's precedent, so all three variants still FAIL C1' under that methodology. Verdicts unchanged; sentence should be edited to reflect actual C1' definition.

**Consequence for the campaign.** The synthetic-label instrument has now exhausted its diagnostic reach on this valset in both stricter (cycle-22 τ ≥ 0.7) and relaxed (cycle-23 τ ≥ 0.4) modes. Two consecutive VALIDATED audits under the same frozen-harness / SHA-anchored / byte-determinism ×2 methodology also validate the stability-audit instrument itself. Auditor lean for cycle 25: **Path B** (defer to post-egress real labels) as the honest default; Path A (feature-side redesign, one cycle only if a specific concrete probe exists — class-supervised projection on M-CLASS-1's 5-class label at N = 55, or a VGGish concat rung reproducibility retry) is worth attempting only under those conditions.

## Cycle-25 handoff (8 items)

1. **Researcher's Path A vs Path B decision** (M-EAR-1 direction after clone-1 exhaustion). Auditor lean is Path B; Path A worth one cycle only with a specific concrete probe named upfront.
2. **Cosmetic fix to `docs/ear_head_regularization_audit_report.md` §7 line 241** — rewrite the "no variant lands inside its own envelope" sentence to reflect the actual constant-0.891 C1' methodology. Verdicts already correct in `variant_verdicts.json`.
3. **Clone-0's two cycle-25 paths** for testing the cycle-14 construction proof at N > K: `i4_replacement.py` (new sibling sampler) OR batch-v6 via cycle-13's unconditioned `sample_rules.py` at N=16 on the I3-augmented ledger. Both keep `i4_stratified.py` untouched.
4. **Ledger-side follow-up.** Add `min_K < N` pre-flight guard to any future batch-vN driver at N > 8, so sampler-exhaustion is detected in pre-flight instead of post-hoc.
5. **Real-label re-run when rated audio unblocks.** Fire the M-EAR-1/armed-harness on real labels; also re-run cycle-23's three regularized variants under real labels alongside. Do not inherit either cycle-6's or cycle-23's synthetic success bar.
6. **Future briefs should not repeat the "salt=0 = cycle-6 anchor" mis-statement.** The cycle-6 anchor is distinct-out-of-namespace PC1+noise per cycle-22 clone-2's report §55; C1' methodology is the constant-0.891 check. Worker correctly ignored the brief's parenthetical.
7. **Trailing-slash artifact canonicalization** — 6 pre-existing WARNs from cycles 1/3/6/9/13 (`scripts/ingest/`, `data/ingestion/`, `data/classifier/_nonfactor/`, `scripts/rules/`, `scripts/gen/`, `scripts/daw_spike/gap2_v3/`). Non-blocking; one-shot canonicalization sweep at any cycle.
8. **Cycle-22 handoff items still open.** Missing namespaced report file `reports/cycles/report_cycles_13-15_clone_1.md` (handoff #1); M-EAR-1 parent roll-up (handoff #5, now more meaningful post-clone-1 exhaustion); cycle-21 handoff items 2, 3, 5, 6, 7, 9.

## Files created this session

- `merge_report.md` — this document (workspace root, overwrites cycle-22 fork capstone).
- `tools/stale/_emit_cycle24_integration_events.py` — one-shot emitter, archived after use.
- `promise_ledger.jsonl` — +4 rows (363 → 367).

## Environment (unchanged)

Python 3.11.15, torch 2.13.0+cpu, numpy 1.26.4, mscore3 3.2.3, DawDreamer 0.9.0, basic-pitch 0.4.0 in `workspace/basic_pitch_venv`, SF2 pin `74594e8f…1cb0`, VGGish rung with cycle-14 content-caveat, single-thread BLAS pins (OMP/MKL/OPENBLAS=1). Rated audio remains egress-blocked (`corpus/CORPUS_STATUS.md`); all non-rated-audio work continues.

## Anti-patterns (updated live_guidance for cycle 25)

New: cycle-23 `M-EAR-1/head-regularization-audit` invalidated/high (all 3 regularized variants FAIL C1'+C2'; head-side-fix hypothesis exhaustively falsified across three orthogonal axes at N=55).

Also confirmed: cycle-22 `M-EAR-1/synthetic-label-stability-audit` invalidated/high, cycle-11 `M-TEX-1/panel/embedding` fetchability failure, cycle-8 `M-TRANS-1/basic-pitch/octave-suppression` bass F1 uplift shortfall.

## Status

**COMPLETE.** Ready for cycle 25.
