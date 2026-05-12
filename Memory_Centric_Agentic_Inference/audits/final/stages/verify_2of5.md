# Final Audit Verify 2/5

Stage: 3 of 12, verify pass 2/5
Slice: M-SCHED-1, M-ARCH-1, M-TRACE-1, M-QUEUE-1
Run id: run-2026-05-11T121649Z
Wall cap hit: false

## Method

This pass verified the second milestone slice assigned in
`audits/final/explore.md`. For each milestone, I checked the full ledger
history, latest validated event, evidence-file existence, artifact content
against the plan success criteria, and executable or generated-output evidence
where applicable.

Commands and checks run from `<workspace>`:

- Searched `plan_of_record.md`, `promise_ledger.jsonl`, and cycle reports for
  `M-SCHED-1`, `M-ARCH-1`, `M-TRACE-1`, and `M-QUEUE-1`.
- Read primary narrative artifacts:
  - `memory-centric-agentic/scheduling_abstractions.md`
  - `memory-centric-agentic/architecture_proposal.md`
  - `memory-centric-agentic/trace_schema.md`
  - `memory-centric-agentic/queueing_model.md`
- Re-ran executable artifacts:
  - `python3 scripts/evaluate_scheduling_abstractions.py`
  - `python3 scripts/plot_scheduling_abstractions.py`
  - `python3 scripts/synthesize_architecture_package.py`
  - `python3 scripts/plot_architecture_synthesis.py`
  - `python3 scripts/generate_agentic_trace_v2.py`
  - `python3 scripts/validate_agentic_trace_v2.py`
  - `python3 scripts/plot_agentic_trace_v2.py`
  - `wolfram-batch -script scripts/queueing_model.wls`
  - `python3 scripts/simulate_queueing_overheads.py`
  - `python3 scripts/plot_queueing_overheads.py`
- Ran a targeted CSV/PNG validation script for artifact existence, row counts,
  winner semantics, trace validation failures, queue reversal behavior, and
  nonblank figure outputs.
- Ran `py_compile` over the Python scripts used by this slice.

## Milestone Results

### M-SCHED-1

Latest ledger state: `validated/high`, cycle 5, event
`90fad94d-a41f-4fef-b926-5364d6bba053`.

Evidence checked:

- `memory-centric-agentic/scheduling_abstractions.md`
- `scripts/evaluate_scheduling_abstractions.py`
- `scripts/plot_scheduling_abstractions.py`
- `data/scheduling_unit_comparison.csv`
- `data/scheduling_regime_winners.csv`
- `data/scheduling_failure_modes.csv`
- `data/scheduling_special_cases.csv`
- `data/scheduling_abstraction_plot.png`
- `data/scheduling_failure_modes.png`

Verification:

- The evaluator regenerated 48 comparison rows across 8 scheduling units and 6
  workloads, satisfying the required request/job/kernel/model/cache-page/
  context-segment/memory-object/trajectory comparison surface.
- The winner table shows regime-dependent abstraction changes:
  - `single-turn chat control`: `model`
  - `batch summarization/offline inference control`: `model`
  - `RAG with retrieved-context reuse`: `memory_object`
  - `code-agent loop with tool outputs and durable workspace`:
    `agent_trajectory_dag`
  - `verification-heavy agent`: `agent_trajectory_dag`
  - `multi-agent branch/merge run`: `agent_trajectory_dag`
- The package includes failure-mode and special-case tables, preserving the
  claim that scheduling units are information boundaries rather than universal
  improvements.
- Both scheduling figures are present and nonblank:
  - `data/scheduling_abstraction_plot.png`: `2080 x 1040`
  - `data/scheduling_failure_modes.png`: `1920 x 928`

Verdict-pending flag from explore: resolved for this pass.
Finding: none.

### M-ARCH-1

Latest ledger state: `validated/high`, cycle 6, event
`c0de6de8-f1b8-4b46-b2e5-6ce2e5ce3afa`.

Evidence checked:

- `memory-centric-agentic/architecture_proposal.md`
- `scripts/synthesize_architecture_package.py`
- `scripts/plot_architecture_synthesis.py`
- `data/architecture_options.csv`
- `data/runtime_compiler_hook_matrix.csv`
- `data/architecture_policy_matrix.csv`
- `data/architecture_failure_modes.csv`
- `data/research_agenda_ranked.csv`
- `data/architecture_option_matrix.png`
- `data/runtime_hook_coverage.png`

Verification:

- The synthesis script regenerated 3 architecture options:
  `A_conventional_request_model_kv_serving`,
  `B_memory_object_aware_runtime`, and
  `C_trajectory_dag_memory_fabric`.
- The regenerated tables include 12 runtime/compiler hook rows, 11 policy rows,
  7 failure-mode rows, and 10 ranked research agenda rows.
- `architecture_options.csv` explicitly lists supported object sets for the
  options, including weights, KV cache, retrieved context, tool output, branch
  state, verifier state, durable workspace, and semantic cache terms. This
  supports the auditor repair described by the latest ledger event.
- The narrative artifact labels claims as `derived`, `simulated`,
  `speculative`, or `deferred`, and keeps measured hardware constants deferred.
- Both architecture figures are present and nonblank:
  - `data/architecture_option_matrix.png`: `1980 x 990`
  - `data/runtime_hook_coverage.png`: `1980 x 1350`

Verdict-pending flag from explore: resolved for this pass.
Finding: none.

### M-TRACE-1

Latest ledger state: `validated/high`, cycle 7, event
`547c907f-82e2-4f49-8c1c-441373e12280`.

Evidence checked:

- `memory-centric-agentic/trace_schema.md`
- `memory-centric-agentic/trace_calibration_plan.md`
- `scripts/generate_agentic_trace_v2.py`
- `scripts/validate_agentic_trace_v2.py`
- `scripts/plot_agentic_trace_v2.py`
- `data/agentic_trace_events_v2.csv`
- `data/trace_object_lifetimes.csv`
- `data/trace_reuse_intervals.csv`
- `data/trace_branch_dag_metrics.csv`
- `data/trace_workload_summary.csv`
- `data/trace_schema_validation.csv`
- `data/trace_invalid_cases.csv`
- `data/trace_lifetime_distributions.png`
- `data/trace_live_bytes_by_object.png`
- `data/trace_branch_dag_metrics.png`

Verification:

- The generator regenerated 503 deterministic synthetic events across 6
  workloads, with 66 object lifetimes, 184 reuse intervals, 6 DAG metric rows,
  and 6 workload summary rows.
- Positive trace validation remains clean: `positive_errors=0`.
- Invalid fixtures intentionally fail. The validation output includes the
  repaired ordering check
  `row_5:object_event_after_evict:object_access:late-birth`, supporting the
  latest auditor claim that use-after-evict is rejected.
- Control traces collapse branch/DAG fields, while RAG and agentic traces expose
  non-KV/provenance and branch/DAG signals respectively.
- The trace schema documents required event columns, object lifecycle events,
  branch/verifier/tool/workspace/cache events, derived metrics, privacy
  boundaries, and calibration intent.
- All three trace figures are present and nonblank:
  - `data/trace_lifetime_distributions.png`: `1920 x 960`
  - `data/trace_live_bytes_by_object.png`: `2080 x 1440`
  - `data/trace_branch_dag_metrics.png`: `1920 x 960`

Verdict-pending flag from explore: resolved for this pass.
Finding: none.

### M-QUEUE-1

Latest ledger state: `validated/high`, cycle 8, event
`47f5f418-3131-4932-b5fb-97df6136db77`.

Evidence checked:

- `memory-centric-agentic/queueing_model.md`
- `scripts/queueing_model.wls`
- `scripts/simulate_queueing_overheads.py`
- `scripts/plot_queueing_overheads.py`
- `data/queueing_special_cases.csv`
- `data/queueing_reversal_thresholds.csv`
- `data/queueing_trace_rates.csv`
- `data/queueing_overhead_sweep.csv`
- `data/queueing_architecture_winners.csv`
- `data/queueing_failure_modes.csv`
- `data/queueing_reversal_thresholds.png`
- `data/queueing_utilization_by_workload.png`
- `data/queueing_architecture_winner_map.png`

Verification:

- The Wolfram script regenerated 11 symbolic special cases and 4 reversal
  threshold rows.
- The Python sweep regenerated 6 trace-rate rows, 92,160 overhead-sweep rows,
  6 architecture-winner rows, and 7 queueing failure-mode rows.
- Winner behavior supports the narrowed architecture claim:
  - Controls remain `A_conventional_request_model_kv_serving` under low, high
    object, and high DAG overhead.
  - RAG is `B_memory_object_aware_runtime` at low overhead and reverses to
    `A_conventional_request_model_kv_serving` under high object overhead.
  - Code-agent, verification-heavy, and multi-agent branch/merge workloads are
    `C_trajectory_dag_memory_fabric` at low overhead, reverse to
    `A_conventional_request_model_kv_serving` under high object overhead, and
    reverse to `B_memory_object_aware_runtime` under high DAG overhead.
- The architecture-winner table includes controlled reversal fields:
  `first_object_reversal_metadata_service_time` and
  `first_non_C_dag_service_time`, supporting the auditor repair for threshold
  attribution.
- All three queueing figures are present and nonblank:
  - `data/queueing_reversal_thresholds.png`: `1980 x 1044`
  - `data/queueing_utilization_by_workload.png`: `1980 x 1044`
  - `data/queueing_architecture_winner_map.png`: `1890 x 1440`

Verdict-pending flag from explore: resolved for this pass.
Finding: none.

## Low Or Provisional Confidence Review

No low-confidence or provisional terminal events were found for this slice.
The non-terminal events are ordinary start/defer states followed by later
`validated/high` ledger events. M-TRACE-1 and M-QUEUE-1 both had auditor repair
claims; this pass re-ran the repaired executables and confirmed the repaired
behaviors are present in the regenerated outputs.

## Findings Appended

None. No CRITICAL, MODERATE, or MINOR findings were identified in this verify
slice, so `audits/final/findings.jsonl` was left unchanged.

## Residual Items For Later Stages

- The global process markers noted in explore (`_run/start` and
  `_manager/validator-warnings`) are outside this milestone slice and remain for
  later test/document stages.
- This pass did not run the global `promise_check` or `org_check` validators;
  those are required by the test stages.
