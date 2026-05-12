# Final Audit Stage 11 - Test Pass 1/9

## Scope

Adversarial closure test focused on structural consistency after the completed verify passes. This pass checked validator state, plan/ledger alignment, ledger structural defects, stale report narratives, supersession records, closure-document presence, and findings-file parseability.

## Required Validators

| Command | Result | Observed output |
|---|---:|---|
| `python3 -m long_exposure.tools.promise_check .` | FAIL | `events: 220, plan milestones: 41`; line 220 has invalid `event_id`; line 220 is a superseded `_manager/validator-warnings` event missing `supersedes`. |
| `python3 -m long_exposure.tools.org_check .` | WARN | Exit code 0 with root organization warnings for `CURATION.yaml`, `memory_centric_agentic_inference_package_2026-05-12T0019.zip`, and `memory_centric_agentic_inference_package_latest.zip`. |

The `promise_check` failure is the same CRITICAL ledger validator defect already appended during verify pass 9. This test pass does not append a duplicate finding. The `org_check` warnings remain known root-package warnings, not a new defect in this pass.

## Adversarial Checks

### Ledger Structure

- Parsed full `promise_ledger.jsonl`: 220 events and 92 distinct milestone IDs.
- UUID/supersession probe found exactly two structural errors, both on ledger line 220:
  - bad event id: `final-auditor-reconcile-validator-warnings-20260512T160500Z`
  - `status: superseded` without a `supersedes` field
- Superseded-event scan found four superseded events total. Lines 86, 98, and 123 include `supersedes`; line 220 does not.
- Line 220 narrative also claims final-audit test pass 1 observed green `promise_check` and that latest `_manager/validator-warnings` was line 204. Current evidence contradicts that: line 220 is now latest and makes `promise_check` red.

### Plan and Ledger Alignment

- Parsed current `plan_of_record.md`: 41 plan milestone IDs.
- Every plan milestone ID has a latest ledger record.
- Latest plan milestone status distribution: `validated: 41`.
- No plan milestone is missing, nonterminal, or extra outside the plan.

### Findings File

- Parsed `audits/final/findings.jsonl` successfully before this pass's append.
- Pre-append count: 9 findings: `CRITICAL: 1`, `MODERATE: 8`.
- Last pre-existing finding is `_run/report_cycles_13-15`, `MODERATE`, `stale_periodic_report_statement`.

### Closure Documents

Searched workspace filenames for `CLOSURE` or `SUPERSEDES`; no matches were present. No closure-document mtime drift finding applies in this pass.

### Artifact Pointer Probe

A literal artifact-existence probe reported one missing string pointer, `data/runtime_*`, from ledger line 43. This is a glob-style artifact family pointer, and the matching runtime files exist on disk:

- `data/runtime_ablation_effects.png`
- `data/runtime_ablation_results.csv`
- `data/runtime_architecture_boundary.png`
- `data/runtime_compiler_hook_matrix.csv`
- `data/runtime_failure_cases.csv`
- `data/runtime_hook_coverage.png`
- `data/runtime_object_residency.png`
- `data/runtime_policy_decisions.csv`
- `data/runtime_registry_snapshots.csv`
- `data/runtime_workload_summary.csv`

No finding is recorded for this probe.

### Stale Periodic Reports

Previously recorded stale-report findings remain supported for:

- `_run/report_cycles_13-15`
- `_run/report_cycles_19-21`
- `_run/report_cycles_23-25`
- `_run/report_cycles_26-28`
- `_run/report_cycles_29-31`
- `_run/report_cycles_32-34`
- `_run/report_cycles_35-37`
- `_run/report_cycles_38-40`

New stale-report finding in this pass:

- `_run/report_cycles_16-18`: ledger line 93 registers `reports/cycles/report_cycles_16-18.md` and `.pdf` at `2026-05-11T22:27:51.974430+00:00`. The report states that cycle 18 had no separate named artifact, milestone, or ledger entry and treats it as a reporting/consolidation boundary. Later ledger lines 94-99 add and validate `_plan/compiler-runtime-planning-milestone` and `M-PLAN-1` within cycle 18, ending with `M-PLAN-1 validated/high` at `2026-05-11T23:27:00Z`.

Not treated as new findings in this pass:

- `_run/report_cycles_4-6`: contains recommended next work, but no later same-range ledger event contradicts the latest clone-0 report registration.
- `_run/report_cycles_7-9`: latest ledger registration points to clone-2 report artifacts, already handled during verify pass 1.
- `_run/report_cycles_1-3`: later same-range manager warning is process oversight only and does not contradict the report's technical closure claims.

## Findings Appended

| Milestone | Severity | Kind | Summary |
|---|---|---|---|
| `_run/report_cycles_16-18` | MODERATE | `stale_periodic_report_statement` | Registered report treats cycle 18 as no separate milestone/artifact/ledger event, but later cycle-18 ledger events add and validate `M-PLAN-1`. |

## New Issues Introduced

None observed. This pass wrote only the stage report and appended one findings JSONL record.

## Remaining Issues

- One CRITICAL ledger validator failure remains: malformed line 220 in `promise_ledger.jsonl` keeps `promise_check` red.
- Nine MODERATE stale periodic-report findings are now recorded across the final audit. These affect public-record authority and report freshness, not the validated technical artifacts.
- The root `org_check` package warnings remain warnings only.

## Gate Check

- Is every fix/claim under test checked against original evidence? yes, this pass re-ran both required validators and inspected ledger/report evidence for the newly recorded stale-report finding.
- Have adjacent behaviors been checked for regressions? yes, plan/ledger alignment, closure-doc presence, superseded-event structure, artifact pointer behavior, and findings JSONL parseability were checked.
- Are any new issues introduced and classified? yes, no issue was introduced by this audit pass; the single new discovered defect is classified MODERATE.
