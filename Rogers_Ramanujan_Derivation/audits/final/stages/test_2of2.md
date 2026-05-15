# Final Audit Stage 5 - Test Pass 2 of 2

Generated: 2026-05-15T13:21:48Z

## Scope
Second adversarial pass over validators, final proof/validation cross-document consistency, full-ledger artifact references, figure coverage, residual statuses, supersession state, and closure/SUPERSEDES drift.

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
| Residual nonterminal statuses | 1 found; `_run/start` is expected residual debt, unexpected problem states recorded as findings if present |
| Final proof promotes computation to proof | no |
| Validation separates experiments from proof | yes |
| Failed/rejected routes preserved | yes |
| Full-ledger artifact paths | all path-like artifacts exist |
| Closure/SUPERSEDES drift | not applicable; no files found |
| Supersession-pending state | none found |

## Residual Statuses

- `_run/start` remains `in-progress/high`.

## Figure Coverage Snapshot

- Figure files under `data/`: 9
- Figure paths referenced by ledger artifacts: 9
- Missing ledger-referenced figures: 0
- Orphan figure files not referenced by ledger artifacts: 0

## Findings Appended

- None.

## Gate Check

- Expected file exists: yes, written at this path.
- Required validators were run and observed: yes.
- Adjacent behavior/regression checked: yes, via final proof/validation separation, artifact references, residual statuses, figures, supersessions, and closure drift.
- Regressions/new issues introduced by this audit pass: none; this pass only writes audit artifacts and findings JSONL.
