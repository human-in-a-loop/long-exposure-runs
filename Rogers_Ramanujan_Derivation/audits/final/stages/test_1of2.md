# Final Audit Stage 4 - Test Pass 1 of 2

Generated: 2026-05-15T13:20:33Z

## Scope
Adversarial consistency pass over plan/ledger terminal states, latest-event artifact pointers, orphan milestone handling, closure/SUPERSEDES drift, and required validators.

## Required Validators

- `python3 -m long_exposure.tools.promise_check <run-workspace>` exited `0`.
- `python3 -m long_exposure.tools.org_check <run-workspace>` exited `0`.

### promise_check output

```text
events: 33, plan milestones: 5
! WARNING: orphan artifact in managed path: data/sessions.db (no ledger event references it)
! WARNING: orphan artifact in managed path: data/sessions.db-shm (no ledger event references it)
! WARNING: orphan artifact in managed path: data/sessions.db-wal (no ledger event references it)
! WARNING: orphan artifact in managed path: reports/cycles/report_cycles_1-3.md (no ledger event references it)
! WARNING: orphan artifact in managed path: reports/cycles/report_cycles_1-3.pdf (no ledger event references it)
! WARNING: orphan artifact in managed path: reports/cycles/report_cycles_10-12.md (no ledger event references it)
! WARNING: orphan artifact in managed path: reports/cycles/report_cycles_10-12.pdf (no ledger event references it)
! WARNING: orphan artifact in managed path: reports/cycles/report_cycles_13-15.md (no ledger event references it)
! WARNING: orphan artifact in managed path: reports/cycles/report_cycles_13-15.pdf (no ledger event references it)
! WARNING: orphan artifact in managed path: reports/cycles/report_cycles_16-18.md (no ledger event references it)
! WARNING: orphan artifact in managed path: reports/cycles/report_cycles_16-18.pdf (no ledger event references it)
! WARNING: orphan artifact in managed path: reports/cycles/report_cycles_19-21.md (no ledger event references it)
! WARNING: orphan artifact in managed path: reports/cycles/report_cycles_19-21.pdf (no ledger event references it)
! WARNING: orphan artifact in managed path: reports/cycles/report_cycles_22-24.md (no ledger event references it)
! WARNING: orphan artifact in managed path: reports/cycles/report_cycles_22-24.pdf (no ledger event references it)
! WARNING: orphan artifact in managed path: reports/cycles/report_cycles_25-27.md (no ledger event references it)
! WARNING: orphan artifact in managed path: reports/cycles/report_cycles_25-27.pdf (no ledger event references it)
! WARNING: orphan artifact in managed path: reports/cycles/report_cycles_28-30.md (no ledger event references it)
! WARNING: orphan artifact in managed path: reports/cycles/report_cycles_28-30.pdf (no ledger event references it)
! WARNING: orphan artifact in managed path: reports/cycles/report_cycles_31-33.md (no ledger event references it)
! WARNING: orphan artifact in managed path: reports/cycles/report_cycles_31-33.pdf (no ledger event references it)
! WARNING: orphan artifact in managed path: reports/cycles/report_cycles_34-36.md (no ledger event references it)
! WARNING: orphan artifact in managed path: reports/cycles/report_cycles_34-36.pdf (no ledger event references it)
! WARNING: orphan artifact in managed path: reports/cycles/report_cycles_37-39.md (no ledger event references it)
! WARNING: orphan artifact in managed path: reports/cycles/report_cycles_37-39.pdf (no ledger event references it)
! WARNING: orphan artifact in managed path: reports/cycles/report_cycles_4-6.md (no ledger event references it)
! WARNING: orphan artifact in managed path: reports/cycles/report_cycles_4-6.pdf (no ledger event references it)
! WARNING: orphan artifact in managed path: reports/cycles/report_cycles_40-42.md (no ledger event references it)
! WARNING: orphan artifact in managed path: reports/cycles/report_cycles_40-42.pdf (no ledger event references it)
! WARNING: orphan artifact in managed path: reports/cycles/report_cycles_7-9.md (no ledger event references it)
! WARNING: orphan artifact in managed path: reports/cycles/report_cycles_7-9.pdf (no ledger event references it)
```

### org_check output

```text
root files: 7, root dirs: 9; standard folders present: ['audits', 'data', 'docs', 'reports', 'scripts', 'stale', 'tests', 'tools']
! WARNING: file at workspace root not in allowed-set: CURATION.yaml
! WARNING: file at workspace root not in allowed-set: derive_rogers_ramanujan_identities_from__package.zip
! WARNING: file at workspace root not in allowed-set: rogers_ramanujan_run_config.yaml
```

## Adversarial Checks

| Check | Result |
|---|---|
| Plan milestones M0-M4 terminal state | all latest states validated/high |
| Supersession-pending status | none found |
| Problem terminal states (`reopened`, `invalidated`, `action_required`) | none found |
| Closure/SUPERSEDES mtime drift | not applicable; no closure/SUPERSEDES files found |
| Latest artifact pointers for plan/archive/plan-change events | all checked paths exist |
| Report files discovered | 14 report files |

## Orphan Milestones

- `_orphan/worker-combined-finite-foundation` is ledger-only but validated/high with evidence present; no defect recorded.
- `_orphan/worker-repro-test-k12` is ledger-only but validated/high with evidence present; no defect recorded.

## Findings Appended

- None.

## Gate Check

- Expected file exists: yes, written at this path.
- Required validators were run and observed: yes.
- Regressions/new issues introduced by this audit pass: none; this pass only writes audit artifacts and findings JSONL.
