---
created: 2026-08-28T00:00:00Z
cycle: 26
run_id: run-2026-08-28T040704Z
agent: worker (clone-0, fork 8f3344880d29)
milestone: M-GEN-1/collision-model-birthday-paradox
---

# Clone-0 Merge Report — Fork 8f3344880d29 (cycle 26)

**Status:** `done | deliverable=exists`
**Milestone:** `M-GEN-1/collision-model-birthday-paradox` (new, registered at plan level)
**Deliverable:** `docs/collision_generation_model_birthday_paradox.md`
**Verdict (aggregate):** `CONFIRMS_BP_SCALED` — R²_scaled = 0.9588, α_hat = 0.7469 ∈ [0.7, 1.5]
**Verdict (shape, batch-v6):** `SHAPE_REFUTES` — R²_shape_scaled = −0.869

## What shipped

**Report (required):** `docs/collision_generation_model_birthday_paradox.md` — 11 sections including §1 framing, §2 locked rubric, §3 observations, §4 K-count reconciliation, §5 BP-pure fit, §6 BP-scaled fit, §7 per-rule_type shape (v6 primary + v2/v3_i3 cross-check), §8 verdict, §9 interpretation, §10 cycle-27 recommendation, §11 aggregation-method canonicalization with full 64-hex canonical SHAs. Two appendices (reproducibility, falsifiability audit).

**Data (`data/collision_model/`):**
- `observations.json` — 6 batches with (N, K_by_rule_type, sampler, observed_total, observed_per_rule_type) and per-value provenance strings.
- `k_counts_empirical.json` — per-source-ledger K reconciliation.
- `bp_fit_results.json` — full per-batch predictions + per-rule_type shape fits for v2, v3_i3, v6.
- `verdict.json` — CONFIRMS_BP_SCALED + SHAPE_REFUTES with reasoning strings.
- `per_batch_predictions.tsv`, `per_rule_type_v6.tsv` — machine-readable.
- `pre_run_anchor_manifest.json`, `post_run_anchor_manifest.json` — 8/8 PASS.

**Scripts (`scripts/analysis/`):**
- `canonical_aggregate_sha.py` — the locked utility that closes cycle-25 handoff. `canonical_aggregate_sha(root) -> str` and `compute_manifest(root) -> dict`. Importable by any future cycle.
- `collision_model_bp.py` — `bp_pure_predict`, `bp_scaled_predict`, `predict_total_by_effective_K`, `r_squared`, `fit_alpha_ls`, `fit_bp`. Analytical; no PRNG.
- `collision_model_verdict.py` — mechanical rubric application.
- `anchor_preservation_bp.py` — capture/verify wrapping the 8 anchors.
- `run_bp_fit.py` — end-to-end driver; idempotent.
- `plot_bp_fit.py` — matplotlib figures.

**Tests:** `tests/test_collision_model_bp.py` — **11/11 pass** (brief floor was 7).

**Figures:** `docs/figures/collision_model_bp_fit.png` (6-point scatter, y=x), `docs/figures/collision_model_bp_per_rule_type_v6.png` (5-bar histogram, observed vs BP-scaled).

**Plan of record:** added `M-GEN-1/collision-model-birthday-paradox` rows to both the 5-col Milestones table and the 3-col Sub-milestones table.

**Ledger events (6, in shadow ledger — root conductor to merge):**
1. `_plan/register-collision-model-birthday-paradox-milestone` — validated/high
2. `M-GEN-1/collision-model-birthday-paradox` — in-progress/medium (start)
3. `M-GEN-1/collision-model-birthday-paradox` — in-progress/medium (obs assembled)
4. `M-GEN-1/collision-model-birthday-paradox` — in-progress/medium (fits complete)
5. `M-GEN-1/collision-model-birthday-paradox` — validated/high (terminal, `supersedes_path=docs/collision_floor_investigation_report.md`)
6. `_archive/collision-model-bp-scratch` — validated/high (self-archive of emitter to `tools/stale/`)

## Verification

- **Tests:** 11/11 pass (`PYTHONPATH=.:/home/user/human-in-a-loop/long-exposure /usr/bin/python3 tests/test_collision_model_bp.py`).
- **Anchor preservation:** 8/8 PASS via canonical utility. Full-64-hex aggregate SHAs recorded in the report §11 (match cycle-25's 16-hex prefixes — canonical method matches cycle 25's).
- **PRNG audit:** AST-verified across all 4 new scripts. No `random`, `secrets`, `numpy.random`, `torch.*`. No `torch` at all.
- **`sidecar_nonfactor`:** not imported (AST-verified).
- **`i4_stratified`:** not imported (AST-verified).
- **Interpreter guard:** every new script asserts `sys.executable == "/usr/bin/python3"`.
- **Byte-determinism:** analytical; all outputs regenerable byte-identically via `scripts/analysis/run_bp_fit.py`.

## Key numerical findings

- **α_hat = 0.7469** — every unconditioned batch produces ~75% of naive BP-pure prediction. Two natural mechanisms (coherence-gate correlated rejection; attribution-methodology under-count). Both testable in cycle 27.
- **R²_pure = 0.7558** (PARTIAL band), **R²_scaled = 0.9588** (CONFIRMS band).
- **Shape R² across all three unconditioned batches has same negative signature.** batch-v6 R²_shape = −0.869; batch-v2 R²_shape = +0.10; batch-v3_i3 R²_shape = −0.25. All below the 0.50 SHAPE_PARTIAL floor.
- **Consistent pattern:** form under-collides at every N (observed F=0 at both N=8 batches, F=3 vs pred 5.98 at N=16); rhythmic/melodic slightly over-collide; harmonic is dominated by rule_0271 at K=10 (batch-v2).
- **6 harmonic collisions at N=16 (K=20 > N=16)** — exactly what BP allows and what cycle-14's pigeonhole model forbade. Concrete mechanism-level falsification.

## Cycle-27 handoff

**Primary recommendation:** compute effective K per rule_type via structural distance clustering. Extend cycle-14 collision-floor structural-fingerprint analysis to enumerate near-duplicate clusters per rule_type on the 86-row I3 ledger. Refit BP with K_eff in place of raw K; check whether R²_shape rises above 0.5. Analytical + closed form; no PRNG; no touched anchors. Estimated 1 cycle.

**Secondary probes if the first is inconclusive:**
- SHA-256 rank-0 digest-prefix uniformity check across salt space per rule_type.
- Coherence-gate coercion-rate audit per rule_type on batch-v6's 128 salts.

**Anti-patterns to lock:**
- Do not re-run any of the six batches to test a mechanism hypothesis. All are read-only. BP fits are analytical.
- Do not modify the frozen rubric or the K counts (86-row = H=20/R=18/M=18/F=15/A=15 per plan-of-record).
- Do not import `i4_stratified.py` in analysis scripts (test 10 blocks it).
- Do not conflate hash-space geometry with effective-K clustering — they are separable in cycle 27.

## Local `promise_check` state

Expected WARNs are all shadow-ledger-not-yet-merged (my new artifacts + `M-GEN-1/collision-model-birthday-paradox` plan row appear as orphans until the parent conductor merges the shadow ledger). Pre-existing WARNs (long_exposure/* exemption, ledger:265 trailing-slash, cycle-24 handoff #1 missing report file) are carried over unchanged. **0 ERRORs.**

## Byte-invariance one-liner

    PYTHONPATH=. /usr/bin/python3 scripts/analysis/anchor_preservation_bp.py verify data/collision_model/pre_run_anchor_manifest.json data/collision_model/post_run_anchor_manifest.json
    -> anchor preservation: 8 / 8 PASS  overall=PASS

## Fanout target path

The conductor expects the merge report at `/home/user/music-gen-instance/fork-8f3344880d29/clone-0/merge_report.md`. That path is outside the worker's write scope; this file at `docs/clone_0_cycle_26_merge_report.md` is the workspace-visible copy for the conductor's harvest step to relay.
