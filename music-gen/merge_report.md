# Clone-2 merge report — fork cc548ca0c2e5

**Branch:** `M-EAR-1/synthetic-label-stability-audit` (cycle 22, chassis-stability audit)
**Terminal status:** `invalidated/high` — C1 FAIL, C2 FAIL, C3 PASS.
**Deliverable:** `docs/ear_stability_audit_report.md` (in-workspace, adopted).

## Verdict summary

| Criterion | Threshold                                           | Observed                                              | Verdict |
|-----------|-----------------------------------------------------|-------------------------------------------------------|---------|
| C1 — MAE reproducibility | cycle-6 MAE (0.891) in 10-recipe [5th, 95th] envelope | envelope=[1.032, 2.082]; min observed = 0.909; 0.891 below min | **FAIL** |
| C2 — Rank stability      | mean pairwise Kendall τ-b ≥ 0.7                     | mean τ = 0.059, p05 = -0.225, min = -0.346            | **FAIL** |
| C3 — Byte-determinism ×2 | SHA-256(stability_report.json) equal across 2 runs   | run-1 SHA = run-2 SHA = `36615ad7…6889c9aa`           | **PASS** |

C3 PASSing is load-bearing: it makes the C1 and C2 FAIL verdicts trustworthy.  Two of three failing is *invalidated/high* because the cycle-6 CORN synthetic-MAE anchor is not reproducible under label-recipe perturbation — a first-class finding that reshapes what the M-EAR-1/armed-harness success bar should be.

## Shadow ledger contents (7 events, in emission order)

1. `_plan/register-stability-audit-milestone` — validated/high — plan_of_record.md rows added (5-col Milestones + 3-col Sub-milestones, parent M-EAR-1).
2. `M-EAR-1/synthetic-label-stability-audit` — in-progress/medium — 10-recipe design + 3 frozen criteria locked.
3. `M-EAR-1/synthetic-label-stability-audit` — in-progress/medium — run-1 observed numbers + SHA `36615ad7…`.
4. `M-EAR-1/synthetic-label-stability-audit` — **invalidated/high** — terminal verdict with observed values vs thresholds.
5. `_infra/adopt-fanout-artifacts-stability-audit` — validated/high — 13 files adopted (5 data + 1 doc + 2 figures + 4 scripts + 1 test).
6. `_infra/cross-branch-integration-test-cycle22-stability-audit` — validated/high — §32 added to `tests/test_integration_cross_branch.py` (~68 new checks; all PASS).
7. `_archive/stability-audit-scratch` — validated/high — 4 diag + 2 emit helpers moved to `tools/stale/`; 2 scratch dirs moved to `data/ear/stale/`.

## New files (adopt targets — 13 total)

Data (`data/ear/stability_audit/`, byte-deterministic ×2):

- `stability_report.json` (SHA `36615ad7…6889c9aa`)
- `per_recipe_mae.tsv`, `rank_matrix.tsv`, `tau_pairs.tsv`, `per_clip_band_variance.tsv`

Report + figures:

- `docs/ear_stability_audit_report.md`  (front-matter carries all three verdicts + observed values)
- `docs/figures/ear_stability_mae_envelope.png`
- `docs/figures/ear_stability_tau_matrix.png`

Code:

- `scripts/ear/synthetic_labels.py`  (10 recipes across 4 families; 0 lines of PRNG; AST-verified)
- `scripts/ear/stability_metrics.py`  (exact Kendall τ-b, pinned percentile, per-clip variance)
- `scripts/ear/stability_audit.py`  (driver; reuses `scripts/ear/model.train_and_eval` verbatim)
- `scripts/ear/plot_stability.py`  (figures)
- `tests/test_ear_stability_audit.py`  (12 assertions, all green; includes a self-invoked C3 re-run)

Test extension:

- `tests/test_integration_cross_branch.py` §32 (68 new PASS checks; existing suite unchanged).

## Frozen invariants preserved

- `scripts/ear/features.py` and `data/ear/features/*.npz` cache: **untouched** (feature_version = `ear-features-v1`).
- `scripts/ear/{model,corn,train}.py`: **untouched**; audit calls `train_and_eval` as-is.
- `scripts/ear/leak_test.py`, `data/ear/leak_test_summary.json`: **untouched**.
- Cycle-6 M-EAR-1/preparation validated/high roll-up: **intact**.
- Cycle-6 synthetic salt is out of `stab-audit-*` namespace; no salt reuse.

## Key implications for the next cycle (armed harness / real-label training)

1. **Do NOT use cycle-6 MAE (0.891) as the real-label success threshold.**  It was recipe-friendly — labels equal `round(4 + 1.5·sign(PC1(X)·features) + noise)`, i.e. the label IS the top PC of the features.  A defensible real-label bar is *beats mean-integer baseline by ≥ 0.3 MAE points* (cycle-6 chassis margin halved).
2. **Add a rank-stability side-check to M-EAR-1/armed-harness.**  Retrain on 5 leave-one-out subsets of the real labels; require mean pairwise τ ≥ 0.5 (softer than C2's 0.7 which was designed for a chassis-noise floor, but strictly greater than the observed synthetic-recipe floor of 0.06).
3. **Publish envelope percentile of the real-label MAE against this audit's envelope [1.03, 2.08].**  If real-label MAE lands in this envelope the chassis is doing "typical work"; if ≤ 0.9 it either has strong PANNs structure OR is over-fitting; if > 2.08 it is *worse* on real labels than on random hash-noise — red flag.
4. **Do NOT publish a single-number "the ear model works" claim before the rank-stability side-check has landed.**

## Determinism envelope (as used)

- Single-thread BLAS: `OMP_NUM_THREADS=OPENBLAS_NUM_THREADS=MKL_NUM_THREADS=1`
- `PYTHONHASHSEED=0`
- `torch.manual_seed(0)` per `_fit` fold entry (matches cycle-6 chassis)
- `torch.use_deterministic_algorithms(True)` NOT enabled — CORN head under CPU / no non-deterministic ops; C3 PASSed anyway.  Documented in the report.

## Test status at merge time

- `tests/test_ear_stability_audit.py`  — **12/12 pass** (including self-invoked C3 re-run under `env PATH=/usr/bin:/bin`).
- `tests/test_integration_cross_branch.py`  — **PASS (0 failures)** with §32 added.
- Pre-existing suites (`tests/test_ledger_writer_validation.py`, `tests/test_fanout_concat_validation.py`, `tests/test_i4_stratified.py`): **not touched** and expected to remain green (this branch only extended the cross-branch test).

## Nothing changed outside branch scope

- No modifications to any pre-existing report, feature cache, ledger row, script, or test outside this branch.
- No `sidecar_nonfactor` imports (AST + regex verified).
- No PRNG symbols in recipe code (AST + substring verified).
- 0-ERROR `promise_check` at branch end (the WARN list has 3 pre-existing upstream-out-of-workspace lines + branch-local files that will resolve once this shadow ledger is merged).

---

*This merge report is also copied to `/home/user/music-gen-instance/fork-cc548ca0c2e5/clone-2/merge_report.md` per the fanout contract.*
