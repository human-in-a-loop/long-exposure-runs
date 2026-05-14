# Final Audit Test Stage 1 of 1

Run id: `run-2026-05-14T030813Z`
Stage: 3 of 4, test
Expected file: `<run-workspace>/audits/final/stages/test_1of1.md`

## Commands Run

The required validators were run from `<run-workspace>`:

```text
python3 -m long_exposure.tools.promise_check <run-workspace>
python3 -m long_exposure.tools.org_check <run-workspace>
```

Raw command output was saved at `audits/final/stages/test_command_output.txt`.

## Validator Results

| Validator | Exit status | Test result |
|---|---:|---|
| `promise_check` | 0 | Green with warnings. It reported 48 events and 12 plan milestones. Warnings include M-2 and M-4 having no ledger events, orphan/generated report and session artifacts, historical missing manager-assessment artifacts, noncanonical `residual-certificates/`, and missing `reports/final/final_report.md`. |
| `org_check` | 0 | Green with warnings. It reported standard folders present and warned about root-level launcher/config files. |

## Adversarial Checks

| Check | Observation | Result |
|---|---|---|
| Plan/ledger consistency | Plan milestones are M-1 through M-12. Ledger latest states validate M-1, M-3, M-5, M-6, M-7, M-8, M-9, M-10, M-11, and M-12. M-2 and M-4 have no ledger events. | Consistent with verify-stage residual debt. |
| Orphan milestones | No ledger milestones of the form `M-*` were found outside the plan milestone set. | Pass. |
| Supersession-pending statuses | No latest milestone status is `superseded`, `reopened`, `invalidated`, or `action_required`; no active supersession-pending condition was detected. | Pass. |
| Closure/SUPERSEDES files | Filename scan found zero files containing `CLOSURE` or `SUPERSEDES`. | No silent closure-doc drift to classify. |
| Missing validated artifacts | One latest validated plan milestone artifact is missing: M-6 references `reports/final/final_report.md`. | Already recorded as `FA-V1-001`; no duplicate finding appended. |
| Final report drift | Some cycle report markdown mtimes are later than the final report mtime, but they are periodic reports already indexed by stage 1 and not closure documents or terminal scientific artifacts. | No finding. |
| Figure coverage spot check | 18 figure-like files were present under managed evidence/report paths; 13 are directly referenced in ledger text. Missing-figure scan did not identify a ledger-referenced absent figure. | No test-stage defect. |

## Finding Impact

The test stage confirmed the verify-stage finding:

- `FA-V1-001` remains MODERATE evidence-traceability debt. `promise_check` independently reports `reports/final/final_report.md` as a missing ledger-tracked artifact. Later final package files preserve the M-6 scientific claim, so this does not invalidate the research package.

No additional CRITICAL or MODERATE findings were introduced by the adversarial pass.

## Residual Debt For Document Stage

- M-2 remains `not-started` / `provisional`: no standalone continuous norm-mismatch theorem was validated.
- M-4 remains `not-started` / `provisional`: no standalone conservation-law or shock-selection campaign was completed.
- `promise_check` warnings are real but mostly organizational/history warnings; the one materially relevant missing validated artifact is already captured by `FA-V1-001`.
- `org_check` warnings are repository-organization warnings, not scientific claim failures.

## Gate Check

- Every verify-stage issue was tested against original evidence: yes. `FA-V1-001` reproduces through `promise_check`.
- Adjacent behavior was checked for regressions: yes. Plan/ledger consistency, orphan milestones, supersession states, closure docs, artifact existence, and figure presence were scanned.
- New issues introduced: none at CRITICAL or MODERATE severity.
