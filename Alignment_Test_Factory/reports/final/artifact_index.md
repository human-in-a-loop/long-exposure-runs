---
created: 2026-05-14T00:20:00Z
cycle: 8
run_id: run-2026-05-13T204826Z
agent: worker
milestone: M-8
---

# Artifact Index

This index maps the validated Open Alignment Test Factory artifacts to developer tasks: understand the design, inspect the schema, run the prototype, review stress coverage, and extend the factory.

## Start Here

| File | Use |
|---|---|
| `reports/final/final_report.md` | End-to-end explanation of what was validated, how to reproduce it, and what remains out of scope. |
| `reports/final/roadmap.md` | Prioritized implementation roadmap with acceptance criteria. |
| `reports/benchmark_stress_test.md` | M-7 stress-test report explaining repairs and remaining benchmark limitations. |
| `REFERENCES.md` | External reference list for Inspect, garak, HarmBench, and JailbreakBench. |
| `plan_of_record.md` | Original campaign goals, milestone ladder, and success criteria. |

## Landscape, Taxonomy, and Rubric

| File | Use |
|---|---|
| `docs/landscape_gap_map.md` | Comparison of existing alignment/red-team tools against agentic testing gaps. |
| `docs/failure_taxonomy_seed.md` | Early M-1 taxonomy seed used to shape M-2. |
| `docs/failure_taxonomy.md` | Operational failure labels and trace evidence expectations. |
| `docs/benchmark_quality_rubric.md` | Benchmark quality rubric for realism, safety, reproducibility, scoring clarity, false-positive risk, gaming resistance, trace completeness, and developer actionability. |
| `data/landscape_gap_matrix.csv` | Machine-readable landscape/gap matrix. |
| `data/landscape_gap_matrix.png` | Rendered landscape/gap figure. |
| `data/failure_taxonomy_operational_matrix.csv` | Machine-readable taxonomy-to-evidence matrix. |
| `data/failure_taxonomy_priority.png` | Rendered priority figure for initial prototype family selection. |

## Schema and Spec Validation

| File or directory | Use |
|---|---|
| `alignment-test-factory/src/alignment_test_factory/schemas.py` | Pydantic source of truth for `TaskSpec`, metadata, fixtures, policy, trace requirements, labels, predicates, and rubric. |
| `alignment-test-factory/schemas/task_spec.schema.json` | Exported JSON Schema for downstream tools. |
| `alignment-test-factory/tools/export_schema.py` | Regenerates the JSON Schema from Pydantic models. |
| `alignment-test-factory/tools/validate_specs.py` | Validates all example specs and expected rejections. |
| `alignment-test-factory/examples/valid/permission_tool_overreach.json` | Valid permission/tool-overreach task spec. |
| `alignment-test-factory/examples/valid/provenance_trace_mismatch.json` | Valid provenance and trace/final mismatch task spec. |
| `alignment-test-factory/examples/valid/uncertainty_escalation.json` | Valid uncertainty escalation task spec. |
| `alignment-test-factory/examples/valid/delegation_drift.json` | Valid delegation drift task spec. |
| `alignment-test-factory/examples/invalid/missing_required_trace_event.json` | Invalid spec missing required permission trace evidence. |
| `alignment-test-factory/examples/invalid/rejected_rubric_or_unsafe_flag.json` | Invalid spec rejected by safety/rubric constraints. |
| `alignment-test-factory/examples/invalid/composite_without_primitive.json` | Invalid composite label without supporting primitive label. |
| `tests/test_task_spec_schema.py` | Schema and example validation tests. |

## Runtime, Trace, and Scorers

| File | Use |
|---|---|
| `alignment-test-factory/src/alignment_test_factory/runtime.py` | Deterministic toy environment for benign resources, approvals, state, delegation, and final answers. |
| `alignment-test-factory/src/alignment_test_factory/trace.py` | Trace event model, task trace requirement validation, and global trace integrity validation. |
| `alignment-test-factory/src/alignment_test_factory/scorers.py` | Deterministic predicates and family scorer dispatch. |
| `alignment-test-factory/src/alignment_test_factory/families.py` | Scripted compliant and violating trajectories for four task families. |
| `alignment-test-factory/src/alignment_test_factory/stress.py` | Stress probe construction and evaluation. |
| `alignment-test-factory/src/alignment_test_factory/__init__.py` | Package exports for the prototype modules. |

## Runners

| File | Use |
|---|---|
| `alignment-test-factory/tools/run_toy_environment.py` | Generates pass/fail traces and score summary for the permission runtime. |
| `alignment-test-factory/tools/run_task_families.py` | Runs all four families and writes multi-family JSON/CSV/SVG summaries. |
| `alignment-test-factory/tools/run_inspect_smoke.py` | Runs the one-family Inspect smoke eval from the correct task directory. |
| `alignment-test-factory/tools/run_multi_family_inspect.py` | Runs the four-family Inspect smoke eval and writes score/log manifests. |
| `alignment-test-factory/tools/run_benchmark_stress.py` | Runs the 11-probe stress suite and writes JSON/CSV/SVG artifacts. |

## Generated Runtime and Family Artifacts

| File | Use |
|---|---|
| `alignment-test-factory/examples/runtime/permission_tool_overreach_pass_trace.json` | Compliant permission trace. |
| `alignment-test-factory/examples/runtime/permission_tool_overreach_fail_trace.json` | Violating permission trace. |
| `alignment-test-factory/examples/runtime/permission_tool_overreach_score_summary.json` | Permission scorer summary. |
| `alignment-test-factory/examples/families/multi_family_score_summary.json` | Four-family deterministic score summary. |
| `alignment-test-factory/examples/families/multi_family_verdict_matrix.csv` | Four-family verdict matrix. |
| `alignment-test-factory/examples/families/multi_family_verdict_matrix.svg` | Rendered four-family verdict matrix. |

## Inspect Artifacts

| File or directory | Use |
|---|---|
| `alignment-test-factory/evals/permission_tool_overreach_smoke.py` | Inspect task for permission/tool-overreach smoke validation. |
| `alignment-test-factory/evals/multi_family_smoke.py` | Inspect task for all four families. |
| `alignment-test-factory/examples/inspect/permission_tool_overreach_inspect_score_summary.json` | Machine-readable Inspect smoke score summary. |
| `alignment-test-factory/examples/inspect/permission_tool_overreach_inspect_log_manifest.json` | Log manifest for permission Inspect runs. |
| `alignment-test-factory/examples/inspect/multi_family_inspect_score_summary.json` | Machine-readable multi-family Inspect score summary. |
| `alignment-test-factory/examples/inspect/multi_family_inspect_log_manifest.json` | Log manifest for multi-family Inspect runs. |
| `alignment-test-factory/examples/inspect/logs/` | Inspect JSON logs from smoke runs. |

## Stress Artifacts

| File | Use |
|---|---|
| `alignment-test-factory/examples/stress/benchmark_stress_results.json` | Full 11-probe stress result summary. |
| `alignment-test-factory/examples/stress/benchmark_stress_matrix.csv` | Stress matrix with expected/observed outcomes and validation status. |
| `alignment-test-factory/examples/stress/benchmark_stress_matrix.svg` | Rendered stress matrix. |
| `tests/test_benchmark_stress.py` | Stress regression tests for coverage, invalid trace handling, ambiguity, malformed payload ordering, and artifact generation. |

## Tests

| File | Use |
|---|---|
| `tests/test_task_spec_schema.py` | Schema acceptance/rejection and provider-agnosticism checks. |
| `tests/test_toy_environment.py` | Runtime, trace, and permission scorer tests. |
| `tests/test_inspect_smoke.py` | One-family Inspect smoke tests. |
| `tests/test_task_families.py` | Four-family deterministic scorer tests. |
| `tests/test_multi_family_inspect.py` | Multi-family Inspect smoke tests. |
| `tests/test_benchmark_stress.py` | Benchmark stress tests. |

## Reproduction Command Stack

Run from `<RUN_WORKSPACE>`:

```bash
source <RUN_WORKSPACE>/.alignment-eval-venv/bin/activate
pytest tests/test_task_spec_schema.py tests/test_toy_environment.py tests/test_inspect_smoke.py tests/test_task_families.py tests/test_multi_family_inspect.py tests/test_benchmark_stress.py
python alignment-test-factory/tools/validate_specs.py
python alignment-test-factory/tools/run_toy_environment.py
python alignment-test-factory/tools/run_task_families.py
python alignment-test-factory/tools/run_benchmark_stress.py
python alignment-test-factory/tools/run_multi_family_inspect.py
python3 -m long_exposure.tools.promise_check <RUN_WORKSPACE>
python3 -m long_exposure.tools.org_check <RUN_WORKSPACE>
```

## Extension Checklist

Use this checklist when adding a new task family:

- Add or reuse a failure label in `schemas.py`.
- Add a safe valid example spec and any invalid counterexamples.
- Add compliant and violating scripted traces in `families.py`.
- Add deterministic predicates in `scorers.py`.
- Add trace requirements for required event types and final-answer fields.
- Add tests for valid, violating, malformed, and under-evidenced traces.
- Add at least one stress probe in `stress.py`.
- Add Inspect exposure only after deterministic runner behavior is stable.
- Append a ledger event with all new artifacts.
