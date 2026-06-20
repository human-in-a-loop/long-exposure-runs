# Final Audit Stage 10 - Verify Pass 9 of 9

Stage input: `10 of 20 (verify (9/9))`

Assigned slice:

- `M-COMP-1`
- `M-DC12-1`
- `M-ATTEST-1`
- `M-EVIDART-1`
- `_manager/validator-warnings`
- `_plan/final-architecture-package-milestone`
- `_plan/production-evidence-gatechain-replay`
- `_plan/production-timebase-observer-integrity`
- `_run/report_cycles_13-15`
- `_run/report_cycles_4-6`

## Ledger And Artifact State

Parsed the full `promise_ledger.jsonl` rather than relying on the bounded prompt summary.

| Record | Latest ledger line | Status | Confidence | Artifact check | Low/provisional history | Verdict-pending |
|---|---:|---|---|---|---|---|
| `M-COMP-1` | 42 | validated | high | 15/15 artifacts present | none | no |
| `M-DC12-1` | 104 | validated | high | 14/14 artifacts present | none | no |
| `M-ATTEST-1` | 146 | validated | high | 17/17 artifacts present | none | no |
| `M-EVIDART-1` | 190 | validated | high | 15/15 artifacts present | none | no |
| `_manager/validator-warnings` | 220 | superseded | high | 2/2 artifacts present | none | yes - structural ledger defect |
| `_plan/final-architecture-package-milestone` | 110 | validated | medium | 2/2 artifacts present | none | no |
| `_plan/production-evidence-gatechain-replay` | 152 | validated | medium | 2/2 artifacts present | none | no |
| `_plan/production-timebase-observer-integrity` | 162 | validated | medium | 2/2 artifacts present | none | no |
| `_run/report_cycles_13-15` | 80 | validated | high | 2/2 artifacts present | none | yes - stale narrative finding |
| `_run/report_cycles_4-6` | 77 | validated | high | 2/2 latest artifacts present | none | no |

## Targeted Execution

Commands executed and observed:

- `wolfram-batch -script scripts/compression_model.wls && python3 scripts/evaluate_compression_strategies.py && python3 scripts/plot_compression_strategies.py`
  - Exit code 0.
  - Regenerated compression special cases, inequalities, scoring tables, queue interaction tables, and three figures.
- `python3 scripts/local_dc12_proxy_bench.py --quick && python3 scripts/apply_dc12_proxy_calibration.py && python3 scripts/plot_dc12_proxy_calibration.py && python3 tests/verify_dc12_proxy_calibration.py`
  - Exit code 0.
  - `verify_dc12_proxy_calibration: ok`.
- `python3 scripts/build_production_attestation_fixtures.py && python3 scripts/evaluate_production_attestation.py && python3 scripts/plot_production_attestation.py && python3 tests/verify_production_attestation.py`
  - Exit code 0.
  - `OK: production attestation envelope verified.`
- `python3 scripts/build_gate_evidence_artifact_contract.py && python3 scripts/validate_gate_evidence_artifacts.py && python3 scripts/plot_gate_evidence_artifacts.py && python3 tests/verify_gate_evidence_artifacts.py`
  - Exit code 0.
  - `OK: gate evidence artifact kit verified.`
- `python3 scripts/build_final_architecture_package.py && python3 scripts/plot_final_architecture_package.py && python3 tests/verify_final_architecture_package.py`
  - Exit code 0.
  - `OK: final architecture package verified.`
- `python3 scripts/build_evidence_gatechain_fixtures.py && python3 scripts/replay_evidence_gatechain.py && python3 scripts/plot_evidence_gatechain.py && python3 tests/verify_evidence_gatechain.py`
  - Exit code 0.
  - `OK: evidence gatechain verified.`
- `python3 scripts/build_timebase_integrity_fixtures.py && python3 scripts/evaluate_timebase_integrity.py && python3 scripts/plot_timebase_integrity.py && python3 tests/verify_timebase_integrity.py`
  - Exit code 0.
  - `OK: timebase integrity verified.`
- `python3 -m long_exposure.tools.promise_check . ; python3 -m long_exposure.tools.org_check .`
  - `promise_check` failed on line 220: non-UUID `event_id` and missing `supersedes` on a superseded `_manager/validator-warnings` event.
  - `org_check` exited 0 with known root-file warnings for `CURATION.yaml` and package zip files.

## Evidence Probes

### M-COMP-1

The rerun supports the latest narrowed compression claim:

- `data/compression_special_cases.csv`: 11 rows.
- `data/compression_boundary_inequalities.csv`: 5 rows.
- `data/compression_strategy_scores.csv`: 210 rows.
- `data/compression_best_strategy_by_object.csv`: 35 rows.
- `data/compression_workload_summary.csv`: 6 rows.
- `data/compression_safety_failures.csv`: 29 rows.
- `data/compression_object_queue_interactions.csv`: 146 rows.
- `data/compression_queue_interactions.csv`: 19 rows.
- Figures exist and are nonempty:
  - `data/compression_strategy_matrix.png`: 139492 bytes, 2196x1044.
  - `data/compression_safety_vs_savings.png`: 126087 bytes, 1710x1116.
  - `data/compression_queue_relief.png`: 127023 bytes, 2610x1278.

Conclusion: supported. The evidence matches the ledger's narrowed high-confidence claim: compression/offload has capacity, locality, provenance, and safety-boundary value under the synthetic setup, but does not currently support a queue-threshold-preserving benefit.

### M-DC12-1

The latest ledger record is validated/high at line 104. All 14 cited artifacts exist.

Probe results:

- `data/dc12_local_bench_metadata.csv`: 11 rows.
- `data/dc12_byte_movement_measurements.csv`: 12 rows.
- `data/dc12_contention_measurements.csv`: 3 rows.
- `data/dc12_proxy_threshold_overlay.csv`: 60 rows.
- `data/dc12_claim_update_matrix.csv`: 4 rows.
- `data/dc12_missing_production_telemetry.csv`: 5 rows.
- `data/dc12_claim_update_matrix.csv` has 0 rows with `production_calibrated=true`.
- Figures exist and are nonempty:
  - `data/dc12_byte_movement_proxy.png`: 130656 bytes, 1700x1020.
  - `data/dc12_contention_latency_proxy.png`: 60334 bytes, 1530x1020.
  - `data/dc12_threshold_overlay.png`: 135300 bytes, 2040x1020.

Conclusion: supported. The proxy-only boundary is preserved; the local proxy outputs do not promote any production-calibrated claim.

### M-ATTEST-1

The latest ledger record is validated/high at line 146. All 17 cited artifacts exist.

Probe results:

- `data/production_attestation_results.csv`: 12 rows.
- `data/production_attestation_failure_modes.csv`: 7 rows.
- `data/production_attestation_intake_boundary.csv`: 12 rows.
- `data/production_attestation_intake_boundary.csv` has 0 rows with `production_calibrated=true`, 0 with `production_ready=true`, and 0 with `claim_credit_allowed=true`.
- Figures exist and are nonempty:
  - `data/production_attestation_envelope_coverage.png`: 42589 bytes, 1360x768.
  - `data/production_attestation_failure_modes.png`: 39302 bytes, 1440x768.
  - `data/production_attestation_boundary.png`: 37829 bytes, 1360x768.

Conclusion: supported. The attestation verifier confirms fixture-only trust semantics and fail-closed boundary behavior.

### M-EVIDART-1

The latest ledger record is validated/high at line 190. All 15 cited artifacts exist.

Probe results after verifier regeneration:

- `data/gate_evidence_artifact_validation_results.csv`: 44 rows.
- `data/gate_evidence_failure_modes.csv`: 10 rows.
- `data/gate_evidence_replay_readiness_boundary.csv`: 12 rows.
- `data/gate_evidence_replay_readiness_boundary.csv` has 0 rows with `production_calibrated=true`, 0 with `production_ready=true`, 0 with `threshold_success=true`, 0 with `causal_validity_granted=true`, and 0 with `claim_credit_allowed=true`.
- Figures exist and are nonempty:
  - `data/gate_evidence_dependency_graph.png`: 90233 bytes, 1760x1040.
  - `data/gate_evidence_failure_modes.png`: 77030 bytes, 1600x864.
  - `data/gate_evidence_replay_readiness_boundary.png`: 72431 bytes, 1360x768.

Conclusion: supported. Artifact completeness remains replay readiness only and does not grant production calibration, threshold success, causal validity, or claim credit.

### Plan Records

The three plan-extension records are supported:

- `_plan/final-architecture-package-milestone` at ledger line 110 points to `plan_of_record.md` and `promise_ledger.jsonl`, both present. `plan_of_record.md` contains `M-FINALPKG-1`, and the final architecture package verifier passed.
- `_plan/production-evidence-gatechain-replay` at ledger line 152 points to `plan_of_record.md` and `promise_ledger.jsonl`, both present. `plan_of_record.md` contains `M-GATECHAIN-1`, and the evidence gatechain verifier passed.
- `_plan/production-timebase-observer-integrity` at ledger line 162 points to `plan_of_record.md` and `promise_ledger.jsonl`, both present. `plan_of_record.md` contains `M-TIMEBASE-1`, and the timebase integrity verifier passed.

Conclusion: supported.

### _manager/validator-warnings

Latest ledger line 220 is `superseded/high` and cites `promise_ledger.jsonl` plus `audits/final/stages/test_1of9.md`, both present. The evidence does not support a valid terminal state because the ledger event itself is malformed:

- `event_id` is `final-auditor-reconcile-validator-warnings-20260512T160500Z`, not a UUID.
- The event has `status: superseded` but no `supersedes` field.
- `python3 -m long_exposure.tools.promise_check .` exits red with both errors.

Finding: CRITICAL ledger-validator defect. This breaks the canonical promise validator and leaves the public ledger structurally invalid.

### _run/report_cycles_13-15

The registered artifacts exist:

- `reports/cycles/report_cycles_13-15.md`: 27106 bytes.
- `reports/cycles/report_cycles_13-15.pdf`: 518952 bytes.

The report content is stale relative to later ledger state:

- The report states that clone 1 / DC-006 provenance-overhead parent integration remained an open gap and that the current parent measurement CSVs contained no DC-006 rows.
- The report markdown mtime is `2026-05-11 21:06:53 +0000`; ledger line 80 registers it at `2026-05-11T21:07:05.467981+00:00`.
- Later ledger line 82, `2026-05-11T21:22:00Z`, validates `M-EXP-1` at high confidence after post-merge integration across trajectory reuse, provenance-validation overhead, semantic-cache correctness/invalidation, and durable replay-tail measurement designs.

Finding: MODERATE stale periodic report. The report artifacts exist, but the final public record should not rely on the report's DC-006 gap statement without reconciliation.

### _run/report_cycles_4-6

Latest ledger line 77 cites clone-0 artifacts:

- `reports/cycles/report_cycles_4-6_clone_0.md`: present.
- `reports/cycles/report_cycles_4-6_clone_0.pdf`: 64977 bytes.

Earlier ledger lines cite the main cycles 4-6 report and clone-2 report. The latest clone-0 registration is internally consistent: the cited files exist and the report content describes a clone-0 DC-005 merge-readiness branch, not the main M-SIM/M-SCHED/M-ARCH report. Like the earlier clone-2 registration pattern, this is artifact registration for a specific clone report under a reused report milestone id.

Conclusion: supported as an artifact-registration claim. No finding in this verify pass.

## Findings Appended

Two structured findings were appended to `audits/final/findings.jsonl`:

- CRITICAL: `_manager/validator-warnings` invalid ledger event at line 220 breaks `promise_check`.
- MODERATE: `_run/report_cycles_13-15` stale periodic report statement about DC-006 / provenance-overhead parent integration.

## Stage Gate

- Evidence files exist for every validated/superseded assigned record: yes.
- Assigned validated/superseded claims are supported by artifact content and targeted execution: yes, except for the CRITICAL structural ledger defect on `_manager/validator-warnings` and the MODERATE stale narrative caveat on `_run/report_cycles_13-15`.
- Low/provisional confidence terminal events needing re-verification: none found in this slice.
- Findings appended: 1 CRITICAL and 1 MODERATE.
