# Final Audit Stage 13 - Test 6/6

## Scope

Final adversarial consolidation pass before document stage. This pass checked:

- required validator status;
- latest planned milestone states and artifact presence;
- low-confidence terminal states;
- residual debt candidates for the final report;
- findings, reconciliation, and lesson-candidate queues;
- figure-coverage values for the final summary JSON;
- completeness of final-audit intermediate files.

## Validators

Command results:

- `python3 -m long_exposure.tools.promise_check <run-root>`: exit 0.
- `python3 -m long_exposure.tools.org_check <run-root>`: exit 0.

Observed validator warnings are unchanged from prior test passes:

- `promise_check` warns that three M5 raw directory artifact paths are not canonicalized:
  - `data/public_taxonomy_sample/v0.1/raw/wfo/`
  - `data/public_taxonomy_sample/v0.1/raw/gbif/`
  - `data/public_taxonomy_sample/v0.1/raw/opentree/`
- `promise_check` warns about missing process-scope manager assessment artifacts under `long-exposure/manager_assessments/...`.
- `org_check` warns about root-level final deliverables and run prompt/score/log files outside the preferred allow-list.

These warnings remain process-scope and do not change the M1-M8 planned-milestone assessment.

## Planned Milestone State

Status distribution across plan milestones only:

| Status | Count |
|---|---:|
| `validated` | 8 |

Confidence distribution across plan milestones only:

| Confidence | Count |
|---|---:|
| `high` | 8 |

Detailed latest planned states:

| Milestone | Latest status | Confidence | Artifact count | Missing artifacts |
|---|---:|---:|---:|---:|
| M1 | `validated` | `high` | 6 | 0 |
| M2 | `validated` | `high` | 1 | 0 |
| M3 | `validated` | `high` | 9 | 0 |
| M4 | `validated` | `high` | 3 | 0 |
| M5 | `validated` | `high` | 60 | 0 |
| M6 | `validated` | `high` | 15 | 0 |
| M7 | `validated` | `high` | 7 | 0 |
| M8 | `validated` | `high` | 4 | 0 |

Low-confidence terminal states: none.

Planned milestone residual debt: none.

## Findings And Reconciliation Queue

Findings file: `<run-root>/audits/final/findings.jsonl`.

- Findings lines: 0.
- CRITICAL findings: 0.
- MODERATE findings: 0.
- MINOR findings: 0.
- Reconciliation events queued via findings: 0.

Lesson-candidate file: `<run-root>/audits/final/lessons.jsonl`.

- Existing non-empty lesson candidates before document stage: 0.

## Figure Coverage For Final Summary

Scoped to current-run research PNGs under `data/**` and ledger-referenced figure artifacts:

| Field | Value |
|---|---:|
| `figures_present` | 7 |
| `figures_in_ledger` | 7 |
| `milestones_with_figures` | 4 |
| `milestones_without_figures` | 0 |

Missing figures: none.

Orphan current-run research figures: none.

The four planned milestones with figure artifacts are M3, M5, M6, and M7. M1, M2, M4, and M8 do not warrant separate figures beyond their documents, tests, and reuse of already-indexed figures.

## Final-Stage Inputs

Recommended values for `final_audit_summary.json`:

```json
{
  "run_id": "run-2026-05-17T004540Z",
  "milestone_status_distribution": {"validated": 8},
  "findings": {"CRITICAL": 0, "MODERATE": 0, "MINOR": 0},
  "reconciliation_events_emitted": 0,
  "lessons_emitted": [],
  "promise_check_status": "green",
  "wall_cap_exceeded": false,
  "figure_coverage": {
    "figures_present": 7,
    "figures_in_ledger": 7,
    "milestones_with_figures": 4,
    "milestones_without_figures": 0,
    "missing_figures": [],
    "orphan_figures": []
  }
}
```

The final report should count only M1-M8 in the primary milestone status distribution. Auxiliary process entries such as `_run/start` and `_manager/validator-warnings` should not inflate the plan-milestone distribution.

## Findings

No CRITICAL findings.

No MODERATE findings.

No MINOR findings added in this pass.

## Findings Appended

0 findings appended to `<run-root>/audits/final/findings.jsonl`.

The findings file remained at 0 lines after this stage.
