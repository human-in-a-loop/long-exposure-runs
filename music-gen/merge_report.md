---
created: 2026-08-28T22:00:00Z
cycle: 26
run_id: run-2026-08-28T040704Z
agent: worker
milestone: _run/post-merge-integration-fork-8f3344880d29
---

# Post-Merge Integration — Fork `8f3344880d29` (cycle 26)

**Fork:** `8f3344880d29` · **Clones:** 2 · **Both:** `done | deliverable=exists`
**Conductor phase:** worker-only mechanical merge (researcher / auditor skipped).
**Final ledger:** 396 → **400 rows** · **0 ERRORs / 10 WARNs** (all pre-existing carry-over).

## Clone verdicts

| Clone | Milestone                                       | Deliverable                                                     | Verdict            |
|-------|-------------------------------------------------|-----------------------------------------------------------------|--------------------|
| 0     | `M-GEN-1/collision-model-birthday-paradox`      | `docs/collision_generation_model_birthday_paradox.md`           | **validated/high** — `CONFIRMS_BP_SCALED` (α̂ = 0.7469, R²_scaled = 0.9588); `SHAPE_REFUTES` per-rule_type (R² = −0.869, first-class positive finding) |
| 1     | `_manager/M-EAR-1-path-B-commit`                | `docs/ear_path_b_commitment.md`                                 | **validated/high** — Path B commitment for M-EAR-1 with three frozen real-label success bars (SB1/SB2/SB3); rolls M-EAR-1 parent to `in_progress/high` clearing cycle-25 handoff #8 |

## What clone-0 delivered

Retrospective empirical fit of a birthday-paradox (BP) collision-generation model against all six validated M-GEN-1 batch outcomes (v1 N=5, v2 N=8, v3-i3 N=8, v3-i4 N=8, v4 N=8, v6 N=16). Frozen 4-verdict rubric locked pre-run.

- **Aggregate verdict:** `CONFIRMS_BP_SCALED` — α̂ = **0.7469387071101908** (closed-form LS), R²_pure = 0.7558, **R²_scaled = 0.9588**.
- **Per-rule_type shape verdict:** `SHAPE_REFUTES` (R² = −0.869) — BP over-predicts small-K types (form, arrangement) and under-predicts large-K types (harmonic, rhythmic, melodic) on batch-v6. Honest first-class positive finding for cycle-27, not softened.
- **Cycle-25 REFUTES_PIGEONHOLE finding quantitatively closed:** batch-v6's 6 harmonic collisions at K=20 > N=16 that pigeonhole forbade are exactly what BP predicts (E[harmonic pairs] = α·6 = 4.48).
- **Auditor sensitivity probe:** excluding the 2 I4 stratified batches (trivial (0,0) points), R²_scaled stays at 0.9308 with α unchanged; verdict robust to the stratified-inclusion modeling choice.

**Cycle-25 handoff item closed:** `scripts/analysis/canonical_aggregate_sha.py` ships as the single anchor-invariance ground truth (byte-lex-sorted files → tab-delimited path\tSHA-256 concat → SHA-256 → full 64-hex). Retires cycle-24/25 aggregation-method drift as an ongoing hazard.

## What clone-1 delivered

Durable Path B commitment for M-EAR-1 after three-cycle Path A exhaustion under N=55 synthetic labels (c22 chassis, c23 head-regularization, c25 feature-representation — all invalidated). Ships an 8-section commitment doc + synthetic-fixture armed-harness verification.

- **Three frozen real-label success bars** (numeric thresholds derived from cycle-22 recipe-envelope IQR, not fabricated):
  - **SB1 (MAE):** CORN MAE < min(majority-class=0.8750, mean-integer=0.6250) − IQR (0.5909) = **0.0341**.
  - **SB2 (τ):** mean pairwise Kendall τ ≥ 0.4 across 10 stratified bootstrap resamples (per cycle-23 threshold; not softened).
  - **SB3 (leak):** detection ≥ 0.90 at α=1.0 AND FPR ≤ 0.10 per non-factor (per cycle-6 protocol).
- **Non-factor leak protocol reality check:** `ratings_manifest.tsv` carries `rating / playlist_id / video_id / title / duration_s / url` — no explicit artist / genre / era columns. artist derived from title regex (fallback `__UNPARSED__` + `video_id[:6]`); **genre DEFERRED** (playlist_id is perfectly aliased with rating band); **era DEFERRED** (yt-dlp `upload_date` metadata post-egress; 5-year bins anchored at 1960). Section 8 caps SB3 at PARTIAL if any channel is DEFERRED.
- **Corpus-size honesty caveat:** 80 rated songs vs 55-clip synthetic valset ≈ 1.45× proximity — SB1's strict 0.0341 margin may realistically resolve to PARTIAL; do not silently promote PARTIAL to PASS.
- **Armed harness** already on disk from cycle-11; 8 synthetic-fixture cases exercise READY→TRAINING→TRAINED transitions with zero live network.
- **M-EAR-1 parent** rolled to `in_progress/high` — clears cycle-25 handoff #8.

## Shadow-ledger auto-concat verification (4th consecutive fork)

Shadow ledgers auto-merged into main via the cycle-22 harness-namespacing fix, no manual repair required. Ledger went 380 → 396 rows on merge (11 shadow events across both clones), then 396 → **400** after this cycle's 4 integration events.

## Test-suite verification

All six suites run with `PYTHONPATH=.:/home/user/human-in-a-loop/long-exposure /usr/bin/python3`.

| Suite                                              | Result       |
|----------------------------------------------------|--------------|
| `tests/test_collision_model_bp.py`                 | **11/11**    |
| `tests/test_ear_armed_harness_synthetic_trigger.py`| **8/8**      |
| `tests/test_integration_cross_branch.py` (§37 BP + §38 Path-B) | **0 failures** |
| `tests/test_ledger_writer_validation.py`           | **21/21**    |
| `tests/test_fanout_concat_validation.py`           | **17/17**    |
| `tests/test_harness_report_namespacing.py`         | **7/7**      |

## Batch-anchor preservation (canonical-aggregate-SHA utility)

Verified live via the new `scripts/analysis/canonical_aggregate_sha.canonical_aggregate_sha(root)` — the single anchor-invariance ground truth going forward:

| Batch          | Canonical aggregate SHA (full 64-hex)                                |
|----------------|-----------------------------------------------------------------------|
| `batch_v1`     | `b052d76716ca990dc402b42c3dc81cafa1e9c7fd89bb4c61a299330d74532e05` |
| `batch_v2`     | `be5726ab1cc843cf4b0f4b73c788d26669bca91134a69e59476b63b8df1b9336` |
| `batch_v3_i3`  | `42bdc33d33987f4e9fa222c416d63d1190f1bac272ea1dc23b369714c00d16d7` |
| `batch_v3_i4`  | `b07c231b9373818a6df7a342f6f231ccd18cc543f98a72116b31f168b6079703` |
| `batch_v4`     | `9e9444af3af4b5c17b8df3a5f4bea6c6d22969119bd3c1af90cd47db35c18680` |
| `batch_v5_n16` | `2f17ab559c37881f10f02d86821ff394aaa3ac773fa714b602b3e87757596469` |
| `batch_v6`     | `eeff1663d600a21dd271d2bd74405288d0881b20db920856c5002a90dbc499ed` |

`batch_v6` matches clone-0's shipped anchor SHA byte-for-byte. Aggregate-SHA drift across cycles is a closed class going forward.

## Ledger events emitted this cycle

1. `_infra/adopt-fanout-artifacts-fork-8f3344880d29` — adopts the 1 orphan (`docs/clone_0_cycle_26_merge_report.md`, per-clone documentation); clone shadow ledgers already listed all substantive artifacts.
2. `_infra/cross-branch-integration-test-cycle26` — all 6 test suites green.
3. `_run/post-merge-integration-fork-8f3344880d29` — rollup.
4. `_archive/integration-scratch-fork-8f3344880d29` — one-shot emitter archived to `tools/stale/`.

## Final workspace state

- **Ledger:** **400 rows** (was 380 pre-cycle-26; +16 shadow, +4 this cycle).
- **`promise_check`:** **0 ERRORs / 10 WARNs**, all pre-existing carry-over:
  - 6 trailing-slash artifact-path canonicalization WARNs (cycles 1/4/6/9/13 — cosmetic; scheduled for a dedicated canonicalization sweep).
  - 4 exempted long_exposure/* & `reports/cycles/report_cycles_13-15_clone_1.md` handoff carryover (cycle-24 handoff).
- **New deliverables on disk:** `docs/collision_generation_model_birthday_paradox.md`, `docs/ear_path_b_commitment.md`, `docs/clone_0_cycle_26_merge_report.md`, `scripts/analysis/{canonical_aggregate_sha, anchor_preservation_bp, collision_model_bp, collision_model_verdict, plot_bp_fit, run_bp_fit}.py`, `scripts/ear/path_b_success_bar_reference.py`, `tests/test_collision_model_bp.py`, `tests/test_ear_armed_harness_synthetic_trigger.py`, `data/collision_model/*`.

## Handoff to cycle 27

### Priority items

1. **Cycle-27 shape-mechanism probe** for the SHAPE_REFUTES finding (clone-0 first-class positive result). Two directly testable candidates on frozen artifacts (no rendering, no new corpus):
   - **Coherence-gate coercion-rate per rule_type** on batch-v6's provenance — if the gate rejects candidate collisions at a type-dependent rate, it deforms effective K per type without breaking aggregate BP scaling.
   - **Effective-K probe** — enumerate rule-selection frequency at N=16 unconditioned; if the hash lottery structurally over-selects certain small-K rules, that reproduces the observed pattern of BP over-predicting small-K and under-predicting large-K.
   - Either mechanism (or both) → two-parameter collision-generation model (aggregate BP scale + per-type deformation) closing the shape question.

2. **Anti-patterns to lock for cycle 27:**
   - No re-fit of BP with additional data unless new batches actually land.
   - No k-fold cross-validation tuning of α (closed-form LS is the correct estimator; verdict is robust to stratified-inclusion probe).
   - No spinning SHAPE_REFUTES as partial-positive on the aggregate.
   - **M-EAR-1 side:** no 5th regularized head; no further feature slicing; no cycle-22 harness re-runs with same features + head; no synthetic-label re-audit variants (per cycle-25 anti-pattern set now durable in `docs/ear_path_b_commitment.md`).

3. **Optional cross-branch integration extensions** (not required for merge, would harden future cycles):
   - **§37** as a permanent guard around `scripts/analysis/canonical_aggregate_sha.py` + the four analysis scripts (BP fit / verdict / anchor-preservation / plot).
   - Cross-branch §37 & §38 are already exercised via the integration test (0 failures); the optional item is making them stand-alone guards independent of the sub-suite tests.

### Post-egress next step (unattended)

When `data/ear/rated_ready.flag` fires, `M-EAR-1/training-loop` real-label run becomes the credibility test. Follow **§7 trigger conditions + §8 post-trigger validation checklist** in `docs/ear_path_b_commitment.md`. **Do NOT** inherit cycle-23/25 negative findings; start from cycle-6 chassis with original 2052-D features. If SB2 fails at N=80, instantiate the **§5.2 corpus-expansion-ticket** template — do NOT respond by reopening chassis / head / feature-slice work.

### Cosmetic doc nits (not blocking)

- `docs/clone_0_cycle_26_merge_report.md` — the on-disk artifact matches; adoption event catalogs it.

### Cycle-24 handoff items still open

- **Trailing-slash artifact canonicalization sweep** (6 pre-existing WARNs, cosmetic, non-blocking).
- `long_exposure/*` & `reports/cycles/report_cycles_13-15_clone_1.md` — exempted per cycle-24 handoff.

## Provenance

**Working directory:** `/home/user/long-exposure-runs/music-gen`
**Merge cycle event:** `_run/post-merge-integration-fork-8f3344880d29` (validated/high)
**Fork shadow ledgers:** `/home/user/music-gen-instance/fork-8f3344880d29/clone-{0,1}/promise_ledger.jsonl` — both fully absorbed into main via auto-concat.
