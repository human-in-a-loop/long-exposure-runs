---
title: "Final Audit Report"
date: "2026-05-12"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# Final Audit Report

Run id: `run-2026-05-11T121649Z`

Scope: closing audit of structured commitments, ledger events, evidence files, and public closure artifacts for the memory-centric agentic inference run. This report does not re-audit the whole workspace; it records whether the run's public record honestly supports its terminal claims.

## Status Distribution

Latest distinct ledger milestones:

| Status | Count |
|---|---:|
| `validated` | 89 |
| `superseded` | 2 |
| `in-progress` | 1 |

Plan-of-record milestones only:

| Status | Count |
|---|---:|
| `validated` | 41 |

The only latest `in-progress` item is `_run/start`, a run-start sentinel rather than an unfinished plan milestone.

## Plan Adherence

All 41 plan-of-record milestones are terminal `validated` with `high` confidence. Evidence counts below are the artifact counts on each milestone's latest ledger event.

| Milestone | Terminal status | Confidence | Evidence count | Latest ledger line |
|---|---|---|---:|---:|
| `M-ABI-1` | `validated` | `high` | 17 | 206 |
| `M-ABIINT-1` | `validated` | `high` | 12 | 211 |
| `M-ADAPTER-1` | `validated` | `high` | 15 | 132 |
| `M-ARCH-1` | `validated` | `high` | 10 | 20 |
| `M-ARCHPKG-1` | `validated` | `high` | 14 | 215 |
| `M-ATTEST-1` | `validated` | `high` | 17 | 146 |
| `M-CALIB-1` | `validated` | `high` | 12 | 50 |
| `M-CAUSAL-1` | `validated` | `high` | 17 | 180 |
| `M-CLAIMEXP-1` | `validated` | `high` | 17 | 200 |
| `M-COMP-1` | `validated` | `high` | 15 | 42 |
| `M-COST-1` | `validated` | `high` | 9 | 8 |
| `M-DC12-1` | `validated` | `high` | 14 | 104 |
| `M-ENERGY-1` | `validated` | `high` | 11 | 87 |
| `M-EVIDART-1` | `validated` | `high` | 15 | 190 |
| `M-EXP-1` | `validated` | `high` | 9 | 82 |
| `M-FINALPKG-1` | `validated` | `high` | 11 | 112 |
| `M-GATECHAIN-1` | `validated` | `high` | 16 | 155 |
| `M-HANDOFF-1` | `validated` | `high` | 11 | 119 |
| `M-INTAKE-1` | `validated` | `high` | 16 | 141 |
| `M-LIFE-1` | `validated` | `high` | 7 | 6 |
| `M-LIVECOLLECT-1` | `validated` | `high` | 16 | 195 |
| `M-PLAN-1` | `validated` | `high` | 12 | 99 |
| `M-PORT-1` | `validated` | `high` | 15 | 136 |
| `M-PRODDEPLOY-1` | `validated` | `high` | 11 | 124 |
| `M-PRODREPLAY-1` | `validated` | `high` | 10 | 185 |
| `M-PRODTELEM-1` | `validated` | `high` | 15 | 108 |
| `M-PROTO-1` | `validated` | `high` | 12 | 46 |
| `M-QUEUE-1` | `validated` | `high` | 13 | 34 |
| `M-REDACT-1` | `validated` | `high` | 17 | 170 |
| `M-ROOTINT-1` | `validated` | `high` | 16 | 161 |
| `M-SCHED-1` | `validated` | `high` | 9 | 16 |
| `M-SEC-1` | `validated` | `high` | 12 | 54 |
| `M-SECOPS-1` | `validated` | `high` | 12 | 92 |
| `M-SIM-1` | `validated` | `high` | 9 | 13 |
| `M-SYNTH-1` | `validated` | `high` | 10 | 59 |
| `M-TAX-1` | `validated` | `high` | 7 | 5 |
| `M-TIMEBASE-1` | `validated` | `high` | 16 | 165 |
| `M-TRACE-1` | `validated` | `high` | 15 | 30 |
| `M-TRENDS-1` | `validated` | `high` | 11 | 128 |
| `M-TRUSTPOL-1` | `validated` | `high` | 17 | 151 |
| `M-UNCERT-1` | `validated` | `high` | 16 | 175 |

Auditor judgment: the research package satisfies the plan milestones at the artifact/evidence level. The closure is not clean because the canonical ledger validator is red.

## Confidence Calibration

Validated ledger events by confidence:

| Confidence | Count |
|---|---:|
| `high` | 128 |
| `medium` | 33 |

Latest ledger records by confidence:

| Confidence | Count |
|---|---:|
| `high` | 60 |
| `medium` | 32 |

No latest terminal milestone is `low` or `provisional`. All plan milestones are `validated/high`. Medium-confidence latest records are primarily plan-update, report-registration, and package-registration records rather than core research milestone validations.

Validator status:

- `python3 -m long_exposure.tools.promise_check .`: red. It reports `promise_ledger.jsonl` line 220 has a non-UUID `event_id` and a superseded `_manager/validator-warnings` event missing `supersedes`.
- `python3 -m long_exposure.tools.org_check .`: exits 0 with warnings for root-level `CURATION.yaml` and the two package zip files.

Figure and image coverage:

- 107 data figure files are present and referenced by ledger artifacts.
- One additional referenced figure lives under `memory-centric-agentic/data/`.
- 40 milestones reference figure artifacts.
- Missing referenced figures: 0.
- Orphan data figures: 0.
- Final narrative image links checked in `final_report.md`, `memory-centric-agentic/final_architecture_package.md`, and `memory-centric-agentic/final_synthesis.md`: 10 links, 0 missing.

## Residual Debt

| Milestone / record | Kind | Narrative |
|---|---|---|
| `_manager/validator-warnings` | `validator-red` | Latest ledger line 220 is structurally invalid: non-UUID `event_id`, superseded status without required `supersedes`, and a narrative contradicted by current validator evidence. This is CRITICAL because the canonical promise validator exits red. |
| `_run/report_cycles_*` | `stale-public-record` | Fourteen stale periodic-report statements were found across reports 1-3, 4-6, 7-9, 13-15, 16-18, 19-21, 23-25, 26-28, 29-31, 32-34, 35-37, and 38-40. They are historical snapshots but currently contain statements contradicted by later validated ledger events. |
| `M-HANDOFF-1` | `stale-artifact-index` | `data/handoff_artifact_index.csv` is internally valid but stale against the current plan/ledger. It covers 24 milestones while the current plan has 41 validated milestones and omits 261 concrete non-report ledger artifact paths. |
| `_run/final-package-artifacts` | `incomplete-registered-package` | The registered package zip archives contain only four files and direct readers to absent final report files. The live workspace has the final report, but the registered archive is misleading as a handoff package. |
| `_run/start` | `in-progress-at-end` | Latest status remains `in-progress/high`; treated as a run-start sentinel, not evidence of unfinished research work. |

No deferred, action-required, reopened, invalidated, or low-confidence terminal plan milestones remain.

## Findings By Severity

### CRITICAL

1. `_manager/validator-warnings` - `ledger_validator_failure`: `promise_ledger.jsonl` line 220 breaks `promise_check` because `event_id` is not a UUID and the superseded event lacks `supersedes`.

### MODERATE

1. `_run/report_cycles_19-21` - stale cycle-21 no-milestone/no-artifact statement contradicted by later `M-FINALPKG-1` events.
2. `_run/report_cycles_23-25` - stale cycle-25 no-milestone/no-artifact statement contradicted by later `M-ADAPTER-1` events.
3. `_run/report_cycles_26-28` - stale cycle-28 no-milestone/no-artifact statement contradicted by later `M-ATTEST-1` events.
4. `_run/report_cycles_29-31` - stale cycle-31 no-milestone/no-artifact statement contradicted by later `M-ROOTINT-1` events.
5. `_run/report_cycles_32-34` - stale cycle-34 no-artifact/no-plan/no-ledger statement contradicted by later `M-UNCERT-1` events.
6. `_run/report_cycles_35-37` - stale cycle-37 no-technical-artifact/no-ledger statement contradicted by later `M-EVIDART-1` events.
7. `_run/report_cycles_38-40` - stale cycle-40 no-artifact/no-ledger statement contradicted by later `M-ABI-1` events.
8. `_run/report_cycles_13-15` - stale DC-006 parent-integration gap statement contradicted by later `M-EXP-1` validation.
9. `_run/report_cycles_16-18` - stale cycle-18 no-named-artifact/no-ledger statement contradicted by later `M-PLAN-1` events.
10. `_run/report_cycles_1-3` - stale clone-2 parent-integration statement contradicted by later `M-EXP-1` validation and current parent CSV rows.
11. `_run/report_cycles_4-6` - stale clone-2 parent-integration/CSV-ingestion statement contradicted by later `M-EXP-1` validation and current parent CSV rows.
12. `M-HANDOFF-1` - stale artifact index incomplete against current plan/ledger while `final_report.md` describes it as mapping every tracked campaign artifact.
13. `_run/report_cycles_7-9` - stale `M-COMP-1` action-required conclusion contradicted by later narrowed validation.
14. `_run/final-package-artifacts` - registered package archive is incomplete and contains verification instructions pointing to absent files.

### MINOR

1. Final auditor could not use `search_sessions/list_session_catalog` because those helper tools were not exposed in this Codex surface; direct SQLite query was used instead.
2. Legacy scratch files `audits/final/stages/verify_1of5.md` and `audits/final/stages/verify_2of5.md` remain outside the current 20-stage final-audit protocol. No stale green-validator claims were found in them.

## Future Work

| Anchored to | Proposal |
|---|---|
| `_manager/validator-warnings` | Repair the final validator-warning reconciliation with a valid UUID, a correct `supersedes` pointer, and a narrative consistent with current evidence; rerun `python3 -m long_exposure.tools.promise_check .` before publishing closure. |
| `_run/report_cycles_*` | Add a consolidated errata or supersession index for periodic reports so historical cycle snapshots are not mistaken for terminal status after later repairs and validations. |
| `M-HANDOFF-1` | Regenerate `data/handoff_artifact_index.csv` against the current plan and ledger; extend `tests/verify_campaign_handoff.py` to compare indexed milestones and artifact paths against latest plan/ledger state. |
| `_run/final-package-artifacts` | Rebuild the registered package archives as closed-world handoff artifacts containing the final report, summary, current manifest, handoff index, references, and verification instructions that point only to files inside the archive. |
| `_run/start` | Close or explicitly classify the run-start sentinel so latest-status distributions do not imply active research work remains open. |

## Reconciliation Log

No reconciliation events are emitted by this final-audit document stage. The unresolved CRITICAL ledger defect is recorded as residual debt rather than silently patched in canonical `promise_ledger.jsonl`.
