---
title: "Final Audit Report"
date: "2026-05-14"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# Final Audit Report

Run id: `run-2026-05-13T204826Z`

## Status Distribution

Plan milestone distribution:

| Status | Count |
|---|---:|
| validated | 8 |
| in-progress | 0 |
| action_required | 0 |
| deferred | 0 |
| reopened | 0 |
| superseded | 0 |
| invalidated | 0 |
| not-started | 0 |

Non-plan bookkeeping states observed:

| Milestone | Status | Confidence | Note |
|---|---|---|---|
| `_run/start` | in-progress | high | Run-start bookkeeping event remains open after all plan milestones reached terminal validated status. |
| `_plan/initial-campaign-milestones` | validated | medium | Initial plan adoption is supported by `plan_of_record.md`. |
| `_plan/domain-folder-convention` | validated | medium | Domain folder convention is supported by `STRUCTURE.md`. |
| `_manager/validator-warnings` | in-progress | medium | Validator warning bookkeeping remains open and is residual debt. |

## Plan Adherence

| Milestone | Terminal Status | Confidence | Evidence Count | Latest Evidence Pointer |
|---|---|---|---:|---|
| M-1 | validated | high | 6 | `docs/landscape_gap_map.md`, `data/landscape_gap_matrix.csv`, `data/landscape_gap_matrix.png`, `docs/failure_taxonomy_seed.md` |
| M-2 | validated | high | 6 | `docs/failure_taxonomy.md`, `docs/benchmark_quality_rubric.md`, `data/failure_taxonomy_operational_matrix.csv`, `data/failure_taxonomy_priority.png` |
| M-3 | validated | high | 14 | `alignment-test-factory/schemas/task_spec.schema.json`, safe examples, invalid fixtures, `tests/test_task_spec_schema.py` |
| M-4 | validated | high | 9 | deterministic runtime, trace/scorer modules, generated toy traces, `tests/test_toy_environment.py` |
| M-5 | validated | high | 7 | Inspect smoke eval, score summary, log manifest, Inspect JSON log, `tests/test_inspect_smoke.py` |
| M-6 | validated | high | 16 | four task families, deterministic scorers, family matrix, Inspect summary/logs, task-family tests |
| M-7 | validated | high | 12 | benchmark stress probes, stress results JSON, stress matrix, stress report, stress tests |
| M-8 | validated | high | 13 | `reports/final/final_report.md`, artifact index, roadmap, final Inspect/family/stress summaries |

The final audit verified that every plan milestone M-1 through M-8 has a terminal `validated` ledger event with high confidence and existing evidence files. The validated artifacts cover the requested landscape review, failure taxonomy, provider-agnostic schema, deterministic toy runtime, Inspect smoke path, multiple task families, stress testing, and final developer-facing package.

## Confidence Calibration

Validated event confidence distribution for terminal plan milestones:

| Confidence | Count |
|---|---:|
| high | 8 |
| medium | 0 |
| low | 0 |
| provisional | 0 |

No plan milestone ended in `validated` with low or provisional confidence. The two `_plan/*` bookkeeping milestones are validated with medium confidence; they are plan-history records rather than deliverable claims. The remaining in-progress items are bookkeeping states, not failed plan milestones.

## Residual Debt

| Milestone | Kind | Narrative |
|---|---|---|
| `_manager/validator-warnings` | validator_bookkeeping_warning | `promise_check` exits 0, but it emits warnings that manager assessment artifacts are missing under `<RUN_INSTANCE_DIR>/...` while the exact ledger artifacts exist on disk under `<RUN_INSTANCE_DIR>/...`. It also reports cycle report artifacts as orphan managed-path files. This does not invalidate M-1 through M-8, but the warning output is misleading bookkeeping debt. |
| `_run/start` | run_bookkeeping_in_progress | The run-start event remains `in-progress` with high confidence after all plan milestones were validated. This is not a deliverable failure, but it leaves final state reporting less clean than a terminal run-closure ledger event would. |

No deferred, supersession-pending, reopened, invalidated, or low-confidence validated plan milestones remain.

## Findings By Severity

### CRITICAL

None.

### MODERATE

1. `_manager/validator-warnings`: `validator_warning_bookkeeping_mismatch`

   `promise_check` exits 0 but emits warnings that ledger-tracked manager assessment artifacts are missing under `<RUN_INSTANCE_DIR>/...`, while the ledger artifacts exist on disk under the dotted path `<RUN_INSTANCE_DIR>/...`. This does not invalidate M-1 through M-8, but the validator output is misleading and should remain residual bookkeeping debt.

### MINOR

None.

## Future Work

| Anchored To | Proposal |
|---|---|
| `_manager/validator-warnings` | Normalize `promise_check` artifact paths before reporting missing managed-path artifacts, preserve the exact ledger spelling in warning output, and decide whether periodic cycle reports should receive ledger events or be excluded from orphan-artifact checks. |
| `_run/start` | Add a terminal run-closure ledger event or archive marker so final audits can distinguish an active run from a completed run whose deliverable milestones are all validated. |

## Reconciliation Log

No `_plan/`, `_archive/`, or correction events are emitted by this final audit. The residual debt is documented for human follow-up rather than reconciled in the ledger by the final auditor.
