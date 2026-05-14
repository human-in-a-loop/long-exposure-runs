# Manifest

## Key Files

The following workspace files produced results cited in
final_report.md. Downstream packaging should include
these; other files are supporting or exploratory.

- `docs/landscape_gap_map.md` — Landscape gap findings in "Milestone Findings" and "Comparison to Existing Tools".
- `data/landscape_gap_matrix.csv` — Machine-readable M-1 coverage matrix cited in "Artifact Map".
- `data/landscape_gap_matrix.png` — M-1 landscape figure covered by final audit figure coverage.
- `docs/failure_taxonomy.md` — Operational failure labels cited in "Milestone Findings" and "How to Add a Safe Task Family".
- `docs/benchmark_quality_rubric.md` — Benchmark-quality gates cited in "Milestone Findings" and "Validated Architecture".
- `data/failure_taxonomy_operational_matrix.csv` — Machine-readable M-2 taxonomy matrix cited in "Artifact Map".
- `alignment-test-factory/src/alignment_test_factory/schemas.py` — `TaskSpec` schema implementation cited in "Validated Architecture".
- `alignment-test-factory/schemas/task_spec.schema.json` — Exported JSON Schema cited in "Validated Architecture".
- `alignment-test-factory/examples/valid/permission_tool_overreach.json` — Valid permission family spec used by schema validation and runtime reproduction.
- `alignment-test-factory/examples/valid/provenance_trace_mismatch.json` — Valid provenance family spec used by schema validation.
- `alignment-test-factory/examples/valid/uncertainty_escalation.json` — Valid uncertainty family spec used by schema validation.
- `alignment-test-factory/examples/valid/delegation_drift.json` — Valid delegation family spec used by schema validation.
- `alignment-test-factory/examples/invalid/composite_without_primitive.json` — Invalid schema fixture supporting the rejected-spec validation result.
- `alignment-test-factory/examples/invalid/missing_required_trace_event.json` — Invalid schema fixture supporting trace-requirement validation.
- `alignment-test-factory/examples/invalid/rejected_rubric_or_unsafe_flag.json` — Invalid schema fixture supporting safety and rubric-gate validation.
- `alignment-test-factory/src/alignment_test_factory/runtime.py` — `ToyEnvironment` implementation cited in "Validated Architecture" and reproduction commands.
- `alignment-test-factory/src/alignment_test_factory/trace.py` — Trace integrity and task requirement validation cited in "Executive Summary" and "Validated Architecture".
- `alignment-test-factory/src/alignment_test_factory/scorers.py` — Deterministic predicates cited in "Validated Architecture".
- `alignment-test-factory/src/alignment_test_factory/families.py` — Four-family scripted trajectories cited in "Core Question Answer" and reproduction commands.
- `alignment-test-factory/src/alignment_test_factory/stress.py` — Stress probe implementation cited in "Validated Architecture" and "Milestone Findings".
- `alignment-test-factory/tools/validate_specs.py` — Spec validation command cited in "Reproduction Commands".
- `alignment-test-factory/tools/run_toy_environment.py` — Toy runtime command cited in "Reproduction Commands".
- `alignment-test-factory/tools/run_task_families.py` — Multi-family deterministic runner cited in "Reproduction Commands".
- `alignment-test-factory/tools/run_inspect_smoke.py` — Two-sample Inspect runner cited in "Validated Architecture".
- `alignment-test-factory/tools/run_multi_family_inspect.py` — Eight-sample Inspect runner cited in "Validated Architecture" and reproduction commands.
- `alignment-test-factory/tools/run_benchmark_stress.py` — Stress runner cited in "Reproduction Commands".
- `alignment-test-factory/evals/permission_tool_overreach_smoke.py` — Inspect adapter cited in "Validated Architecture".
- `alignment-test-factory/evals/multi_family_smoke.py` — Multi-family Inspect adapter cited in "Validated Architecture".
- `alignment-test-factory/examples/runtime/permission_tool_overreach_pass_trace.json` — Compliant runtime trace supporting reproduction results.
- `alignment-test-factory/examples/runtime/permission_tool_overreach_fail_trace.json` — Violating runtime trace supporting reproduction results.
- `alignment-test-factory/examples/runtime/permission_tool_overreach_score_summary.json` — Runtime score summary supporting deterministic permission results.
- `alignment-test-factory/examples/families/multi_family_score_summary.json` — Four-family score summary supporting multi-family results.
- `alignment-test-factory/examples/families/multi_family_verdict_matrix.csv` — Predicate verdict matrix supporting multi-family results.
- `alignment-test-factory/examples/families/multi_family_verdict_matrix.svg` — Multi-family figure covered by final audit figure coverage.
- `alignment-test-factory/examples/inspect/permission_tool_overreach_inspect_score_summary.json` — Two-sample Inspect summary supporting the Inspect smoke result.
- `alignment-test-factory/examples/inspect/permission_tool_overreach_inspect_log_manifest.json` — Inspect smoke log manifest supporting reproducibility.
- `alignment-test-factory/examples/inspect/multi_family_inspect_score_summary.json` — Eight-sample Inspect summary supporting the `accuracy 1.000` result.
- `alignment-test-factory/examples/inspect/multi_family_inspect_log_manifest.json` — Multi-family Inspect log manifest supporting reproducibility.
- `alignment-test-factory/examples/stress/benchmark_stress_results.json` — Stress probe results supporting `matched_expectations: 11/11`.
- `alignment-test-factory/examples/stress/benchmark_stress_matrix.csv` — Stress matrix supporting M-7 probe outcomes.
- `alignment-test-factory/examples/stress/benchmark_stress_matrix.svg` — Stress figure covered by final audit figure coverage.
- `tests/test_task_spec_schema.py` — Schema test coverage included in the 31-test validation baseline.
- `tests/test_toy_environment.py` — Runtime and scorer test coverage included in the 31-test validation baseline.
- `tests/test_inspect_smoke.py` — Inspect smoke test coverage included in the 31-test validation baseline.
- `tests/test_task_families.py` — Multi-family and nested trace-field test coverage included in the 31-test validation baseline.
- `tests/test_multi_family_inspect.py` — Eight-sample Inspect summary test coverage included in the 31-test validation baseline.
- `tests/test_benchmark_stress.py` — Stress test coverage included in the 31-test validation baseline.
- `reports/benchmark_stress_test.md` — Developer-facing stress report cited in "Artifact Map".
- `reports/final/artifact_index.md` — Developer artifact map cited in "Artifact Map".
- `reports/final/roadmap.md` — Future implementation roadmap cited in "Prioritized Roadmap".

## Script Inventory

### Root Documentation

| File | Lines | Purpose |
|---|---:|---|
| `plan_of_record.md` | 194 | Campaign directive, goals, milestone ladder, and scope constraints. |
| `STRUCTURE.md` | 46 | Workspace organization and domain-folder convention. |
| `REFERENCES.md` | 6 | Global numbered references used by reports and artifacts. |
| `promise_ledger.jsonl` | 30 | Chronological milestone and validation event ledger through M-8 validation. |

### docs/

| File | Lines | Purpose |
|---|---:|---|
| `docs/landscape_gap_map.md` | 86 | M-1 comparison of Inspect, garak, HarmBench, and JailbreakBench against agentic test-factory needs. |
| `docs/failure_taxonomy_seed.md` | 55 | M-1 seed labels and benign fixture patterns for later taxonomy work. |
| `docs/failure_taxonomy.md` | 182 | M-2 operational failure labels, event requirements, predicates, and prototype priorities. |
| `docs/benchmark_quality_rubric.md` | 72 | M-2 task quality gates for safety, trace completeness, scoring clarity, and actionability. |

### data/

| File | Lines | Purpose |
|---|---:|---|
| `data/landscape_gap_matrix.csv` | 14 | Machine-readable M-1 capability coverage matrix. |
| `data/failure_taxonomy_operational_matrix.csv` | 10 | Machine-readable M-2 failure-label matrix. |
| `data/landscape_gap_matrix.png` | n/a | M-1 heatmap generated from the landscape gap matrix. |
| `data/failure_taxonomy_priority.png` | n/a | M-2 priority figure generated from the taxonomy matrix. |

### scripts/

| File | Lines | Purpose |
|---|---:|---|
| `scripts/plot_landscape_gap_matrix.py` | 74 | Generates the M-1 landscape coverage heatmap from CSV. |
| `scripts/plot_failure_taxonomy_priority.py` | 94 | Generates the M-2 failure-label priority figure from CSV. |

### alignment-test-factory/src/alignment_test_factory/

| File | Lines | Purpose |
|---|---:|---|
| `alignment-test-factory/src/alignment_test_factory/__init__.py` | 30 | Package exports for schemas, runtime, trace helpers, scorers, family runners, and stress helpers. |
| `alignment-test-factory/src/alignment_test_factory/schemas.py` | 275 | Provider-agnostic Pydantic task, policy, trace, label, predicate, and rubric schema models. |
| `alignment-test-factory/src/alignment_test_factory/trace.py` | 159 | Trace event model, task trace requirement validation, and global trace integrity validation. |
| `alignment-test-factory/src/alignment_test_factory/runtime.py` | 212 | Deterministic benign `ToyEnvironment` with resources, approval decisions, state mutation, delegation, final answers, and trace capture. |
| `alignment-test-factory/src/alignment_test_factory/scorers.py` | 452 | Deterministic predicates for permission, provenance, uncertainty, and delegation families, each emitting evidence-linked results. |
| `alignment-test-factory/src/alignment_test_factory/families.py` | 257 | Scripted compliant and violating trajectories for all four task families plus summary builders. |
| `alignment-test-factory/src/alignment_test_factory/stress.py` | 298 | M-7 stress probe builders and evaluator for gaming, ambiguity, false-positive, false-negative, and trace-integrity probes. |

### alignment-test-factory/tools/

| File | Lines | Purpose |
|---|---:|---|
| `alignment-test-factory/tools/export_schema.py` | 31 | Regenerates `task_spec.schema.json` from the Pydantic model. |
| `alignment-test-factory/tools/validate_specs.py` | 54 | Validates bundled valid and invalid task-spec examples. |
| `alignment-test-factory/tools/run_toy_environment.py` | 123 | Generates the permission/tool-overreach compliant and violating runtime traces and score summary. |
| `alignment-test-factory/tools/run_inspect_smoke.py` | 122 | Runs the two-sample Inspect smoke eval and exports log manifest plus deterministic score summary. |
| `alignment-test-factory/tools/run_task_families.py` | 107 | Generates the four-family score summary, verdict CSV, and SVG verdict matrix. |
| `alignment-test-factory/tools/run_multi_family_inspect.py` | 111 | Runs the eight-sample Inspect suite and exports log manifest plus deterministic score summary. |
| `alignment-test-factory/tools/run_benchmark_stress.py` | 105 | Runs the M-7 stress suite and writes JSON, CSV, and SVG stress artifacts. |

### alignment-test-factory/evals/

| File | Lines | Purpose |
|---|---:|---|
| `alignment-test-factory/evals/permission_tool_overreach_smoke.py` | 153 | Inspect adapter for the two-sample permission/tool-overreach smoke eval under `mockllm/model`. |
| `alignment-test-factory/evals/multi_family_smoke.py` | 81 | Inspect adapter for the eight-sample multi-family smoke eval under `mockllm/model`. |

### alignment-test-factory/examples/

| File | Lines | Purpose |
|---|---:|---|
| `alignment-test-factory/examples/valid/permission_tool_overreach.json` | 160 | Valid safe task spec for least-authority resource use and approval-gated state changes. |
| `alignment-test-factory/examples/valid/provenance_trace_mismatch.json` | 152 | Valid safe task spec for observed-source citations and trace/final-answer consistency. |
| `alignment-test-factory/examples/valid/uncertainty_escalation.json` | 117 | Valid safe task spec for conflict handling, uncertainty, and escalation. |
| `alignment-test-factory/examples/valid/delegation_drift.json` | 109 | Valid safe task spec for delegated context minimization and policy inheritance. |
| `alignment-test-factory/examples/invalid/composite_without_primitive.json` | 100 | Invalid fixture proving composite labels cannot stand alone without a primitive cause. |
| `alignment-test-factory/examples/invalid/missing_required_trace_event.json` | 94 | Invalid fixture proving trace-dependent labels must declare required event types. |
| `alignment-test-factory/examples/invalid/rejected_rubric_or_unsafe_flag.json` | 88 | Invalid fixture proving unsafe or rubric-rejected specs fail before execution. |
| `alignment-test-factory/examples/runtime/permission_tool_overreach_pass_trace.json` | 98 | Generated compliant runtime trace for permission/tool-overreach. |
| `alignment-test-factory/examples/runtime/permission_tool_overreach_fail_trace.json` | 56 | Generated violating runtime trace for permission/tool-overreach. |
| `alignment-test-factory/examples/runtime/permission_tool_overreach_score_summary.json` | 117 | Generated deterministic score summary for permission/tool-overreach. |
| `alignment-test-factory/examples/families/multi_family_score_summary.json` | 1,375 | Generated score summary for four families and eight scripted samples. |
| `alignment-test-factory/examples/families/multi_family_verdict_matrix.csv` | 13 | Generated predicate verdict matrix in CSV form. |
| `alignment-test-factory/examples/families/multi_family_verdict_matrix.svg` | 42 | Generated SVG verdict matrix figure. |
| `alignment-test-factory/examples/inspect/permission_tool_overreach_inspect_score_summary.json` | 357 | Generated Inspect score summary for the two-sample smoke eval. |
| `alignment-test-factory/examples/inspect/permission_tool_overreach_inspect_log_manifest.json` | 19 | Generated Inspect command, version, log path, and summary manifest. |
| `alignment-test-factory/examples/inspect/multi_family_inspect_score_summary.json` | 1,395 | Generated Inspect score summary for the eight-sample multi-family suite. |
| `alignment-test-factory/examples/inspect/multi_family_inspect_log_manifest.json` | 19 | Generated Inspect command, version, log path, and summary manifest. |
| `alignment-test-factory/examples/stress/benchmark_stress_results.json` | 901 | M-7 full stress probe results with expected and observed outcomes. |
| `alignment-test-factory/examples/stress/benchmark_stress_matrix.csv` | 12 | M-7 stress matrix in CSV form. |
| `alignment-test-factory/examples/stress/benchmark_stress_matrix.svg` | 39 | M-7 SVG stress matrix figure. |

### alignment-test-factory/schemas/

| File | Lines | Purpose |
|---|---:|---|
| `alignment-test-factory/schemas/task_spec.schema.json` | 615 | Generated JSON Schema for `TaskSpec`. |

### tests/

| File | Lines | Purpose |
|---|---:|---|
| `tests/test_task_spec_schema.py` | 105 | Pytest coverage for valid examples, invalid examples, unknown labels, provider-specific core fields, final-answer-only tasks, and JSON Schema export. |
| `tests/test_toy_environment.py` | 106 | Runtime trace vocabulary, permission/tool-overreach scorers, denied/mismatched approvals, and final-answer-only inconclusive handling. |
| `tests/test_inspect_smoke.py` | 101 | Inspect log generation, two-sample verdicts, evidence IDs, trace IDs, and final-answer-only non-substitution. |
| `tests/test_task_families.py` | 106 | Four-family compliant/violating trajectories, deterministic predicate evidence, and nested trace-field validation. |
| `tests/test_multi_family_inspect.py` | 98 | Eight-sample Inspect summary and per-sample trace/scorer evidence preservation. |
| `tests/test_benchmark_stress.py` | 79 | Stress coverage, invalid trace handling, ambiguity handling, malformed payload ordering, and artifact generation. |

### reports/

| File | Lines | Purpose |
|---|---:|---|
| `reports/cycles/report_cycles_1-3.md` | 308 | Periodic report covering M-1 landscape, M-2 taxonomy/rubric, and M-3 schema work. |
| `reports/cycles/report_cycles_4-6.md` | 211 | Periodic report covering M-4 runtime, M-5 Inspect smoke path, and M-6 multi-family scoring. |
| `reports/cycles/report_cycles_7-9.md` | 268 | Periodic report covering M-7 benchmark stress testing, M-8 final packaging, and M-9 closure. |
| `reports/cycles/report_cycles_10-12.md` | 181 | Periodic closure report covering repeated campaign validation across cycles 10 through 12. |
| `reports/benchmark_stress_test.md` | 73 | M-7 developer-facing stress report and repair summary. |
| `reports/final/final_report.md` | 317 | Final developer-facing synthesis of the validated factory path, updated with final audit closure status. |
| `reports/final/artifact_index.md` | 145 | M-8 developer map of important files and how to inspect or run them. |
| `reports/final/roadmap.md` | 161 | M-8 prioritized implementation roadmap and acceptance criteria. |

## Cumulative Stats

| Scope | Count |
|---|---:|
| Scripts and code files | 18 |
| Test files | 6 |
| Markdown documentation/report files | 15 |
| CSV data files | 4 |
| JSON schema/spec/summary files | 17 |
| Figure files | 4 |
| Total tracked text files in this manifest | 61 |
| Total tracked text lines in this manifest | 11,481 |
| Active sub-topics | 8: landscape gaps, operational taxonomy/rubric, task-spec schema, deterministic runtime, Inspect smoke path, multi-family deterministic scoring, benchmark stress testing, final packaging/roadmap |

## Cross-References

| Origin | Consuming Artifact | Value Flow |
|---|---|---|
| `plan_of_record.md` | `promise_ledger.jsonl` | Milestones M-1 through M-8 define the ledger event lifecycle. |
| `docs/landscape_gap_map.md` | `docs/failure_taxonomy_seed.md` | Agentic gaps become seed failure labels and benign analogues. |
| `data/landscape_gap_matrix.csv` | `scripts/plot_landscape_gap_matrix.py` -> `data/landscape_gap_matrix.png` | Capability coverage values render into the M-1 heatmap. |
| `docs/failure_taxonomy_seed.md` | `docs/failure_taxonomy.md` | Seed labels are expanded into primitive/composite operational labels. |
| `docs/failure_taxonomy.md` | `data/failure_taxonomy_operational_matrix.csv` | Label definitions, trace events, scorer sketches, traps, and priorities become machine-readable rows. |
| `data/failure_taxonomy_operational_matrix.csv` | `scripts/plot_failure_taxonomy_priority.py` -> `data/failure_taxonomy_priority.png` | Prototype priorities and scoreability render into the M-2 priority figure. |
| `docs/failure_taxonomy.md` + `docs/benchmark_quality_rubric.md` | `alignment-test-factory/src/alignment_test_factory/schemas.py` | Event vocabulary, failure labels, structured final fields, predicate inputs, and rubric gates become schema validators. |
| `alignment-test-factory/src/alignment_test_factory/schemas.py` | `alignment-test-factory/schemas/task_spec.schema.json` | Pydantic `TaskSpec` exports to JSON Schema. |
| `alignment-test-factory/examples/valid/*.json` and `alignment-test-factory/examples/invalid/*.json` | `alignment-test-factory/tools/validate_specs.py` and `tests/test_task_spec_schema.py` | Example specs provide validation and regression-test fixtures. |
| `alignment-test-factory/examples/valid/permission_tool_overreach.json` | `alignment-test-factory/src/alignment_test_factory/runtime.py` | The first validated task spec drives the provider-agnostic toy runtime. |
| `alignment-test-factory/src/alignment_test_factory/runtime.py` | `alignment-test-factory/examples/runtime/*.json` | Scripted runtime paths emit compliant and violating permission traces. |
| `alignment-test-factory/src/alignment_test_factory/trace.py` | `alignment-test-factory/src/alignment_test_factory/scorers.py` | Trace events, nested required-field validation, and integrity checks provide the evidence substrate for deterministic predicates. |
| `alignment-test-factory/src/alignment_test_factory/scorers.py` | `alignment-test-factory/examples/runtime/permission_tool_overreach_score_summary.json` | Permission predicates produce evidence-linked pass/fail verdicts for the runtime path. |
| `alignment-test-factory/examples/runtime/permission_tool_overreach_score_summary.json` | `alignment-test-factory/evals/permission_tool_overreach_smoke.py` | Inspect wraps the deterministic permission path without changing core runtime semantics. |
| `alignment-test-factory/evals/permission_tool_overreach_smoke.py` | `alignment-test-factory/examples/inspect/permission_tool_overreach_inspect_score_summary.json` | Inspect preserves trace event IDs, predicate IDs, verdicts, rationales, scorer events, and evidence IDs for two samples. |
| `alignment-test-factory/src/alignment_test_factory/families.py` | `alignment-test-factory/tools/run_task_families.py` | Four scripted task families produce the machine-readable family summary and verdict matrix. |
| `alignment-test-factory/examples/families/multi_family_verdict_matrix.csv` | `alignment-test-factory/examples/families/multi_family_verdict_matrix.svg` | Predicate verdict rows render into the multi-family SVG matrix. |
| `alignment-test-factory/src/alignment_test_factory/families.py` | `alignment-test-factory/evals/multi_family_smoke.py` | The four-family scripted summaries feed the eight-sample Inspect smoke suite. |
| `alignment-test-factory/evals/multi_family_smoke.py` | `alignment-test-factory/examples/inspect/multi_family_inspect_score_summary.json` | Inspect preserves per-family trace and scorer evidence for all eight samples. |
| `alignment-test-factory/src/alignment_test_factory/stress.py` | `alignment-test-factory/tools/run_benchmark_stress.py` | Benign stress probes exercise trace integrity, gaming, ambiguity, false-positive, and false-negative surfaces. |
| `alignment-test-factory/tools/run_benchmark_stress.py` | `alignment-test-factory/examples/stress/benchmark_stress_results.json` | Stress evaluation records 11/11 matched expected outcomes. |
| `alignment-test-factory/examples/stress/benchmark_stress_matrix.csv` | `alignment-test-factory/examples/stress/benchmark_stress_matrix.svg` | Stress probe outcomes render into the M-7 SVG matrix. |
| `reports/benchmark_stress_test.md` | `reports/final/final_report.md` | M-7 stress findings supply the three-layer validation/scoring split used in final packaging. |
| `reports/final/final_report.md` | `reports/final/artifact_index.md` and `reports/final/roadmap.md` | Final synthesis points developers to concrete artifacts and prioritized extension tracks. |
| `alignment-test-factory/examples/inspect/*_log_manifest.json` | `alignment-test-factory/examples/inspect/logs/*.json` | Manifests record the exact generated Inspect log files used by smoke eval summaries. |
