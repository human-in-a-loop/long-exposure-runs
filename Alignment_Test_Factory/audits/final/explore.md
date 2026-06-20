# Final Audit Explore Inventory

Run id: `run-2026-05-13T204826Z`

Stage: 1 of 4, explore.

Inputs read:

- `plan_of_record.md`
- `promise_ledger.jsonl` full file, 30 events
- `reports/cycles/report_cycles_1-3.md`
- `reports/cycles/report_cycles_4-6.md`
- `reports/cycles/report_cycles_7-9.md`
- `reports/cycles/report_cycles_10-12.md`
- `reports/cycles/report_cycles_13-13.md`
- `reports/benchmark_stress_test.md`
- `reports/final/final_report.md`
- `reports/final/artifact_index.md`
- `reports/final/roadmap.md`
- `REFERENCES.md`, `MANIFEST.md`, `STRUCTURE.md`, `audits/final/run_mode.json`

Closure documents: none found by filename scan for `*CLOSURE*` or `*SUPERSEDES*` under the run documentation/audit folders.

Report glob note: the glob also matches unrelated `optional-local-wolfram-tool/quantum_foundations/report_cycles_*.md` files. These are outside the Open Alignment Test Factory campaign and are excluded from this run-scope audit.

Verify/test slicing:

- Total stages: 4.
- Verify passes: 1. Stage 2 verifies all terminal milestone claims below.
- Test passes: 1. Stage 3 performs adversarial consistency checks and runs `promise_check` plus `org_check`.

## Milestone Inventory

| Milestone | Latest status | Confidence | Latest event | Latest evidence pointer | Stage-2 verdict pending | Notes |
|---|---|---|---|---|---|---|
| `_run/start` | in-progress | high | `bfb13fbb-679c-4b92-b789-8ad4ee68017c`, researcher, 2026-05-13T20:48:26Z | `plan_of_record.md`, `STRUCTURE.md` | no | Run-start bookkeeping remains in-progress; not a deliverable terminal claim. |
| `_plan/initial-campaign-milestones` | validated | medium | `890bae4a-a521-41a0-9a14-a31594a12efe`, researcher, 2026-05-13T20:48:58Z | `plan_of_record.md` | yes | Plan created goals G1-G5 and M-1 through M-8. |
| `_plan/domain-folder-convention` | validated | medium | `c4e8921f-2d01-48a3-8ff1-03c8ddbeb25c`, researcher, 2026-05-13T20:48:58Z | `STRUCTURE.md` | yes | Domain folder convention is visible in workspace organization and artifact paths. |
| `M-1` | validated | high | `976ad943-a9f5-474f-ba39-1f420aef02b6`, auditor, 2026-05-13T20:58:00Z | `docs/landscape_gap_map.md`; `data/landscape_gap_matrix.csv`; `data/landscape_gap_matrix.png`; `scripts/plot_landscape_gap_matrix.py`; `docs/failure_taxonomy_seed.md`; `promise_ledger.jsonl` | yes | Landscape/gap map milestone. Report coverage: `reports/cycles/report_cycles_1-3.md`. |
| `M-2` | validated | high | `4932e61a-06a4-4fa7-b9a3-aa77dfe283cd`, auditor, 2026-05-13T21:30:00Z | `docs/failure_taxonomy.md`; `docs/benchmark_quality_rubric.md`; `data/failure_taxonomy_operational_matrix.csv`; `data/failure_taxonomy_priority.png`; `scripts/plot_failure_taxonomy_priority.py`; `promise_ledger.jsonl` | yes | Failure taxonomy and quality rubric milestone. Report coverage: `reports/cycles/report_cycles_1-3.md`. |
| `M-3` | validated | high | `52b92e70-6e32-4f6a-8e86-915729a068fe`, auditor, 2026-05-13T22:08:00Z | `alignment-test-factory/src/alignment_test_factory/schemas.py`; `alignment-test-factory/tools/export_schema.py`; `alignment-test-factory/tools/validate_specs.py`; `alignment-test-factory/schemas/task_spec.schema.json`; valid/invalid example specs; `tests/test_task_spec_schema.py`; `promise_ledger.jsonl` | yes | Task/failure schema milestone. Report coverage: `reports/cycles/report_cycles_1-3.md`. |
| `M-4` | validated | high | `41795164-be66-4914-9945-d54081926bf8`, auditor, 2026-05-13T22:32:00Z | `alignment-test-factory/src/alignment_test_factory/trace.py`; `runtime.py`; `scorers.py`; `tools/run_toy_environment.py`; runtime pass/fail traces; score summary; `tests/test_toy_environment.py`; `promise_ledger.jsonl` | yes | Deterministic toy environment milestone. Report coverage: `reports/cycles/report_cycles_4-6.md`. |
| `M-5` | validated | high | `48a6db13-0eb1-4661-b136-1e902e6609bb`, auditor, 2026-05-13T22:55:00Z | `alignment-test-factory/evals/permission_tool_overreach_smoke.py`; `tools/run_inspect_smoke.py`; Inspect score summary; Inspect log manifest; exact Inspect JSON log; `tests/test_inspect_smoke.py`; `promise_ledger.jsonl` | yes | Inspect smoke eval milestone. Report coverage: `reports/cycles/report_cycles_4-6.md`. |
| `M-6` | validated | high | `d2530c8b-a5c7-4f3a-8484-f7f5b8913825`, auditor, 2026-05-13T23:40:00Z | `runtime.py`; `scorers.py`; `families.py`; `trace.py`; family and Inspect runners; family score summary; verdict matrix CSV/SVG; multi-family Inspect summary/manifest/log; `tests/test_task_families.py`; `tests/test_multi_family_inspect.py`; `promise_ledger.jsonl` | yes | Multi-family deterministic scoring milestone. Includes auditor repair of one MODERATE nested expected-trace validation defect. Report coverage: `reports/cycles/report_cycles_4-6.md`. |
| `M-7` | validated | high | `697cf781-8d40-4b95-bb53-6d45c39ef6bf`, auditor, 2026-05-14T00:05:00Z | `trace.py`; `scorers.py`; `stress.py`; `tools/run_benchmark_stress.py`; stress results JSON; stress matrix CSV/SVG; `tests/test_benchmark_stress.py`; `reports/benchmark_stress_test.md`; multi-family Inspect artifacts; `promise_ledger.jsonl` | yes | Benchmark stress-test milestone. Report coverage: `reports/cycles/report_cycles_7-9.md`. |
| `M-8` | validated | high | `ef24cca4-f071-414c-bb97-f275f3c730b8`, auditor, 2026-05-14T00:35:00Z | `reports/final/final_report.md`; `reports/final/artifact_index.md`; `reports/final/roadmap.md`; multi-family Inspect summary/manifest/log; family summary/matrix; stress results/matrix; `promise_ledger.jsonl` | yes | Final developer report and roadmap milestone. Report coverage: `reports/cycles/report_cycles_7-9.md`, with closure confirmations in cycles 10-13. |
| `_manager/validator-warnings` | in-progress | medium | `43f8bd26-4b5f-4d5d-bb23-5bd9747ee783`, manager, 2026-05-13T23:48:27.136031+00:00 | `<RUN_INSTANCE_DIR>/manager_assessments/manager_assessment_20260513T234827Z.md` | no | Latest manager bookkeeping warning event. Needs residual-debt consideration, but it is not a terminal deliverable claim. |

## Evidence Pointers Observed

Initial file existence checks confirmed these key milestone pointers are present:

- `docs/landscape_gap_map.md`
- `docs/failure_taxonomy.md`
- `docs/benchmark_quality_rubric.md`
- `alignment-test-factory/examples/families/multi_family_score_summary.json`
- `alignment-test-factory/examples/stress/benchmark_stress_results.json`
- `alignment-test-factory/examples/inspect/multi_family_inspect_score_summary.json`
- `alignment-test-factory/examples/inspect/multi_family_inspect_log_manifest.json`
- `reports/final/final_report.md`
- `reports/final/roadmap.md`

Observed machine-readable summary keys:

- Family summary: `families`, `family_count`, `sample_count`, `samples`.
- Stress results: `families`, `matched_expectations`, `probe_count`, `results`, `stress_classes`.
- Multi-family Inspect summary: `inspect_log_path`, `model`, `sample_count`, `samples`, `task_name`.
- Multi-family Inspect manifest: `command`, `inspect_version`, `log_file_path`, `score_summary_path`, `working_directory`.

## Preliminary Finding Classification

No CRITICAL or MODERATE findings are entered at explore stage. Items to check in later stages:

- Verify that each validated milestone's evidence files exist and support the ledger claim.
- Verify the known M-6 MODERATE repair is reflected in code/tests and did not leave a residual terminal defect.
- Check whether manager warning artifacts or managed-report bookkeeping create residual debt for final documentation.
- Check for silent supersession or closure-document drift. Initial filename scan found no closure/supersession documents.
- Run `promise_check` and `org_check` during the adversarial test stage.

MINOR log candidates observed from source records only, not yet final findings:

- Known `promise_check` bookkeeping warnings are repeatedly described as non-blocking.
- Generated `__pycache__` files are present.
- Some reports note no raw transcript search tool was available in reporting contexts; this stage used direct SQLite queries instead.

## Stage 2 Assignment

Stage 2 verify slice: `_plan/initial-campaign-milestones`, `_plan/domain-folder-convention`, and M-1 through M-8. For each, verify evidence support against the filesystem and append structured findings only for unsupported, inconsistent, or materially under-evidenced claims.
