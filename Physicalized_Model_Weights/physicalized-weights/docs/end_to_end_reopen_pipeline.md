---
created: 2026-05-13T10:24:00Z
cycle: 3
run_id: run-2026-05-13T015136Z
agent: worker
milestone: M-PIPELINE-1
---

# End-to-end reopen pipeline

M-PIPELINE-1 composes the three existing evidence gates before a trace-like artifact can affect the Phase 2 downgrade. The pipeline validates trace schema and privacy guardrails with M-TRACE-1, checks ingestion-path admissibility with M-INGEST-1, maps per-trace hybrid and programmable-baseline energy terms onto the M-REOPEN-1 threshold row, and emits a final status.

The final statuses are `invalid_trace`, `valid_but_insufficient`, `threshold_evaluable_not_crossed`, `synthetic_counterfactual_crossed`, and `actual_reopen_candidate`. Actual reopen requires the conjunction: M-TRACE-1 `valid_reopen_candidate`, M-INGEST-1 `reopen_candidate_path`, measured hybrid and programmable baseline terms, production/shadow/canary source type, provenance attestation, and threshold crossing.

![end-to-end reopen gate outcomes for invalid, insufficient, threshold-evaluable, and synthetic counterfactual traces, showing that no current artifact becomes actual production reopen evidence](../data/reopen_pipeline_decision_flow.png)

## Fixture results

- `physicalized-weights/data/pipeline_trace_invalid_privacy.csv`: `invalid_trace`; blockers `trace_status=invalid_privacy_risk|ingestion_class=inadmissible|threshold_crossed=false`.
- `physicalized-weights/data/pipeline_trace_valid_insufficient.csv`: `valid_but_insufficient`; blockers `trace_status=valid_but_insufficient|ingestion_class=valid_but_insufficient|measured_terms=false|source_type=synthetic|threshold_crossed=false`.
- `physicalized-weights/data/pipeline_trace_threshold_evaluable_not_crossed.csv`: `threshold_evaluable_not_crossed`; blockers `threshold_crossed=false`.
- `physicalized-weights/data/pipeline_trace_synthetic_counterfactual_crossed.csv`: `synthetic_counterfactual_crossed`; blockers `ingestion_class=threshold_evaluable_if_measured|source_type=synthetic`.

## Interpretation

No current artifact is actual production, shadow, or canary measured evidence that crosses the threshold with full provenance. The synthetic counterfactual crosses the numeric threshold only to exercise the arithmetic branch; it remains `synthetic_counterfactual_crossed`, not `actual_reopen_candidate`. The summary reports `actual_reopen_candidate_count = 0`, preserving the Phase 2 downgrade.
