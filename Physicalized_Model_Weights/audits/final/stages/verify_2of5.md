# Final Audit Stage 3 - Verify 2/5

Run id: `run-2026-05-13T015136Z`
Stage: `3 of 12 (verify 2/5)`
Slice: `M-CAL-1`, `M-WORKLOAD-1`, `M-SWBASE-2`, `M-SYNTH-2`, `M-MEASURE-1`, `M-TRACE-1`, `M-REOPEN-1`
Wall cap hit: `false`

## Method

Read the latest ledger events for each milestone in the slice, checked every latest-event artifact path for existence, reviewed low/medium/provisional prior events for later revalidation, inspected generated summary artifacts, and ran the focused milestone tests.

The focused tests regenerate normal data/doc outputs as part of their validation path; no source or artifact repair was made by this final-auditor stage.

## Artifact Existence

All latest terminal ledger artifacts for the seven assigned milestones exist on disk.

| Milestone | Latest event | Status | Confidence | Artifact count | Missing artifacts |
|---|---:|---|---|---:|---|
| `M-CAL-1` | `01e105fd-994d-42bc-a9f6-ccc018fb1873` | `validated` | `high` | 19 | none |
| `M-WORKLOAD-1` | `8fddef1b-3c55-443f-ab49-e9b12be6f592` | `validated` | `high` | 8 | none |
| `M-SWBASE-2` | `a2b30051-93e9-4b9e-9cf7-b09f65d92fb5` | `validated` | `high` | 7 | none |
| `M-SYNTH-2` | `133c3d9e-62b8-4479-9f02-0c123cb9aa10` | `validated` | `high` | 12 | none |
| `M-MEASURE-1` | `5cb0d945-36eb-4cc4-9c4a-5fe1d9e957d6` | `validated` | `high` | 8 | none |
| `M-TRACE-1` | `f458a74a-5f24-4c6e-9f2f-6201aa1847ea` | `validated` | `high` | 10 | none |
| `M-REOPEN-1` | `6f7a8c4d-1d2e-4f7a-a5cf-9b0c8d7e6f31` | `validated` | `high` | 9 | none |

## Verification Results

### `M-CAL-1`

Verdict: supported.

Evidence supports the claim that the calibrated companion model emits explicit-unit CSV/JSON/PNG artifacts, validates source/unit metadata, ranks uncertainty drivers, and states the weakened safety/filter result. `calibrated_breakeven_summary.json` reports 6,300 calibrated scenarios, winner counts of 452 hybrid, 4,948 programmable accelerator, and 900 optimized software scenarios, and top uncertainty drivers led by fallback frequency, utilization, request volume, audit/control scale, and update interval.

Focused test:

`python3 physicalized-weights/tests/test_calibrated_breakeven.py` exited 0.

### `M-WORKLOAD-1`

Verdict: supported.

Evidence supports the workload/update-cadence trace claim. `workload_summary.json` covers 10 scenarios and reports classifications of 4 falsified, 1 preserved, 2 speculative, and 3 weakened. Scenario fields include invocation volume, fallback rate, near-threshold frequency, update cadence, audit logging cost, feature extraction cost, utilization, and falsification/control cases.

Focused test:

`python3 physicalized-weights/tests/test_workload_trace_generator.py` exited 0.

### `M-SWBASE-2`

Verdict: supported.

Evidence supports the stronger software/runtime and programmable-accelerator baseline replay. `stronger_baseline_summary.json` reports 10 workload scenarios, winner counts of 9 programmable accelerator and 1 optimized software, and confirms the formerly preserved case winner is `programmable_accelerator`.

Focused test:

`python3 physicalized-weights/tests/test_stronger_baseline_model.py` exited 0.

### `M-SYNTH-2`

Verdict: supported, with shared-manifest caveat already recorded under `M-FINAL-1`.

Evidence supports the Phase 2 downgrade claim. `phase2_synthesis_summary.json` reports `hybrid_workload_wins: 0`, stronger-baseline winner counts of 9 programmable accelerator and 1 optimized software, and a reopening standard requiring measured production traces with durable positive hybrid margin under identical accounting. `test_phase2_synthesis.py` regenerated the Phase 2 claim matrix, summary, evidence map, and downgrade document, then passed.

Focused test:

`python3 physicalized-weights/tests/test_phase2_synthesis.py` exited 0.

Caveat: `python3 physicalized-weights/tests/test_final_synthesis.py` still exits 1 because the shared `evidence_manifest.csv` has stale hashes for rows labeled `M-FINAL-1` (`REFERENCES.md`, two `final_synthesis.md` rows, and `reproducibility.md`). This is the same defect already appended during Stage 2 as `M-FINAL-1/stale_evidence_manifest_hashes`; no new Stage 3 finding is appended because the stale rows are not assigned to this slice's milestones.

### `M-MEASURE-1`

Verdict: supported.

Evidence supports the production-measurement requirements and local proxy harness claim. `local_overhead_summary.json` reports 10 scenarios and 6 measured/proxy components, while `measurement_gap_matrix.csv` and the tests preserve the distinction between local proxy timing and production-required accelerator energy/latency/utilization. The all-fallback and zero-invocation controls retain no false fast-path credit.

Focused test:

`python3 physicalized-weights/tests/test_local_overhead_benchmark.py` exited 0.

### `M-TRACE-1`

Verdict: supported.

Evidence supports the production trace schema and validator claim. `production_trace_validation_summary.json` reports no reopen candidates, keeps the valid fixture at `valid_but_insufficient`, and rejects the invalid fixture as `invalid_privacy_risk`; issue counts include missing baseline, invalid units, inconsistent policy, privacy risk, and proxy insufficiency classes.

Focused test:

`python3 physicalized-weights/tests/test_production_trace_validator.py` exited 0.

### `M-REOPEN-1`

Verdict: supported.

Evidence supports the quantitative reopen-threshold model. `reopen_thresholds_summary.json` reports `current_hybrid_wins: 0`, 8 finite threshold cases, and the zero-volume/all-fallback controls as unreopenable. `symbolic_reopen_thresholds.json` exists and the Wolfram-backed proof path was exercised by the test.

Focused test:

`python3 physicalized-weights/tests/test_reopen_thresholds.py` exited 0, including the `wolfram-batch` symbolic special-point check.

## Prior Low/Provisional/Medium Confidence Review

No low or provisional terminal events were found in this slice.

Prior medium-confidence in-progress events were followed by high-confidence validated events:

| Milestone | Prior event | Prior status/confidence | Subsequent validation |
|---|---|---|---|
| `M-WORKLOAD-1` | `641896e7-2a9d-4f80-94e1-1ce827904fa0` | `in-progress` / `medium` | `8fddef1b-3c55-443f-ab49-e9b12be6f592` |
| `M-SWBASE-2` | `cefb3b37-e403-449f-b016-618148d5af68` | `in-progress` / `medium` | `a2b30051-93e9-4b9e-9cf7-b09f65d92fb5` |

## Findings Appended

None.

The only observed failing command in this stage was the already-known shared final synthesis manifest hash failure:

`python3 physicalized-weights/tests/test_final_synthesis.py` exited 1 at `test_artifact_hashes_are_current`.

Stale rows currently observed:

| Row | Manifest milestone | Path |
|---:|---|---|
| 2 | `M-FINAL-1` | `REFERENCES.md` |
| 3 | `M-FINAL-1` | `physicalized-weights/docs/final_synthesis.md` |
| 20 | `M-FINAL-1` | `physicalized-weights/docs/final_synthesis.md` |
| 23 | `M-FINAL-1` | `physicalized-weights/docs/reproducibility.md` |

Because those rows are labeled `M-FINAL-1`, this stage carries the Stage 2 `MODERATE` residual-debt finding forward rather than duplicating it against a Stage 3 milestone.

## Stage Gate

Gate result: pass.

Every assigned milestone's latest evidence exists and supports the claimed terminal status. Focused tests for each assigned milestone passed. No new structured finding was appended for this slice.
