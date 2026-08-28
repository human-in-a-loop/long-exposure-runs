# Merge report — fork 3fbd8c1ab57c, clone 1

**Milestone:** `M-EAR-1/head-regularization-audit`
**Cycle:** 23
**Verdict:** `invalidated/high` (three-variant negative finding; head-side-fix hypothesis closed)

## Scoped deliverable

`docs/ear_head_regularization_audit_report.md` (+ supporting artifacts).

## Summary

Cycle-23 response to cycle-22 clone-2's invalidation of the cycle-6 CORN 1–7 head under synthetic-label recipe perturbation. Three regularized head variants (CORN-ridge, CORN-bottleneck, CORN-frozen-projector) evaluated under cycle-22 clone-2's UNCHANGED 10-recipe stability-audit harness (SHA-anchored). Relaxed rubric (C1' MAE-in-envelope; C2' mean τ ≥ 0.4; C3' byte-determinism × 2) locked before the run.

**Result:** all three variants FAIL C1' and C2'; all three PASS C3'. Pre-registered interpretation rule 2 fires: "failure is not head-shape-fixable at 55 clips — cycle-24 must turn to features or accept the ear gate."

Frontier tuples (mean τ, median MAE):

| Point               | τ        | MAE      | C1' | C2' | C3' |
|---------------------|----------|----------|-----|-----|-----|
| cycle-6 baseline    | +0.059   | 0.891    |  —  |  —  |  —  |
| ridge               | +0.077   | 1.391    | FAIL | FAIL | PASS |
| bottleneck          | +0.061   | 1.455    | FAIL | FAIL | PASS |
| frozen_projector    | +0.061   | 1.573    | FAIL | FAIL | PASS |

Ridge's marginal τ lift (+30 % relative on a small floor) is real but ~5× below the τ = 0.4 threshold.

## Invariants preserved

- `scripts/ear/{stability_audit, synthetic_labels, stability_metrics, model, corn, features}.py`: SHA-anchored at cycle-22 clone-2 values; verified at every run boundary.
- `data/ear/features/*.npz` (55-clip cache): SHA-manifest byte-identical pre/post.
- `data/ear/stability_audit/*` (cycle-22 outputs): untouched.
- Cycle-6 M-EAR-1/preparation `validated/high` roll-up: intact.

## Byte-determinism × 2 (C3' proof)

Per-variant `stability_report.json` SHA-256:

| Variant           | run 1 SHA (prefix) | run 2 SHA (prefix) | equal |
|-------------------|--------------------|--------------------|-------|
| ridge             | `be9a750ed169adfa…` | `be9a750ed169adfa…` | ✓ |
| bottleneck        | `f224157c7b571ce3…` | `f224157c7b571ce3…` | ✓ |
| frozen_projector  | `5dd1c9dabfcee1cd…` | `5dd1c9dabfcee1cd…` | ✓ |

## Tests

- `tests/test_ear_head_regularization.py`: **6/6 PASS**.
- `tests/test_integration_cross_branch.py` §34 (M-EAR-1/head-regularization-audit): **0 failures** (23 new checks under §34, all PASS).
- `promise_check`: **0 ERRORs**.

## Files added / modified

**Code:**
- `scripts/ear/_variant_core.py`
- `scripts/ear/model_v2_ridge.py`
- `scripts/ear/model_v2_bottleneck.py`
- `scripts/ear/model_v2_frozen_projector.py`
- `scripts/ear/stability_audit_v2_variants.py`
- `scripts/ear/tau_mae_frontier.py`
- `tests/test_ear_head_regularization.py`
- `tests/test_integration_cross_branch.py` (§34 appended)

**Data:**
- `data/ear/head_regularization_audit/stability_report_v2_{ridge,bottleneck,frozen_projector}.json`
- `data/ear/head_regularization_audit/variant_verdicts.json`
- `data/ear/head_regularization_audit/frontier_summary.json`
- `data/ear/head_regularization_audit/harness_anchor_manifest.json`
- `data/ear/head_regularization_audit/feature_cache_pre_post_shas.json`
- `data/ear/head_regularization_audit/pca_basis.npz` + `.sha256`
- `data/ear/head_regularization_audit/_run{1,2}_<variant>/{stability_report.json, per_recipe_mae.tsv, rank_matrix.tsv, tau_pairs.tsv, per_clip_band_variance.tsv}`

**Docs:**
- `docs/ear_head_regularization_audit_report.md`  (§1 setup · §2 variants · §3 per-variant results · §4 frontier · §5 byte-determinism · §6 harness-invariance · §7 interpretation + cycle-24 recommendation)
- `docs/figures/ear_head_regularization_tau_mae_frontier.png`
- `docs/figures/ear_head_regularization_tau_per_variant.png`

**Plan of record:**
- Registered `M-EAR-1/head-regularization-audit` row in 5-col Milestones + 3-col Sub-milestones tables.

## Ledger events emitted (7)

1. `_plan/register-head-regularization-audit-milestone` — validated/high
2. `M-EAR-1/head-regularization-audit` — in-progress/medium (audit setup + anchor SHAs captured)
3. `M-EAR-1/head-regularization-audit` — in-progress/medium (variant heads + PCA basis pinned)
4. `M-EAR-1/head-regularization-audit` — in-progress/medium (all three first-run tuples captured)
5. `M-EAR-1/head-regularization-audit` — in-progress/medium (byte-determinism × 2 verified)
6. `M-EAR-1/head-regularization-audit` — **invalidated/high** (terminal; supersedes_path: docs/ear_stability_audit_report.md)
7. `_archive/head-regularization-scratch` — validated/high (one-shot emitters archived to tools/stale/)

## Cycle-24 handoff

Two paths recommended (researcher's call — pre-registered, brief-locked options):

- **Path A — feature-side redesign.** Investigate whether the 2052-D PANNs+HEUR feature vector carries a signal the 55-clip valset can resolve. Concrete probes: (i) VGGish concat (2180-D) or CLAP fetch retry; (ii) supervised probe on M-CLASS-1 label to test class-separability at N=55; (iii) fit-and-freeze a class-supervised projection and re-audit under this branch's harness.
- **Path B — defer all ear-model calibration to post-egress real labels.** Set `M-EAR-1/armed-harness` to fire on rated audio when egress opens; evaluate under real τ / MAE / band-variance without inheriting synthetic-label success bars.

**Do NOT** extend the audit at the same 55-clip N with a new head variant expecting a different answer — the pattern is now robust across three orthogonal head axes.

## Notes for integrator

- No cross-branch conflicts with fork 3fbd8c1ab57c clone 0 (M-GEN-1/batch-v5-n16): disjoint file scope. This branch touches `scripts/ear/*` and `data/ear/head_regularization_audit/*`; clone 0 touches `scripts/gen/*` and `data/gen/batch_v5_n16/*`.
- Harness auto-write namespacing (cycle-22 clone-0 fix) is in production — this clone's `_run/report_cycles_<lo>-<hi>_clone-1` ledger row lands automatically at concat time.
- One-shot emitters have been archived to `tools/stale/`; no post-merge action required from the integrator on that front.
