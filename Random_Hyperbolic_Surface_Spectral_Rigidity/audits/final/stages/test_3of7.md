# Final Audit Stage 11 - Test 3/7: Referenced and Orphan Artifact Check

## Scope

This adversarial pass extracted artifact-like paths from every ledger event, resolved them relative to `<workspace>`, checked existence, and looked for likely final/report artifacts under `docs/`, `reports/`, `data/`, `figures/`, and `audits/` that are not directly named by ledger artifact fields. Missing artifacts in latest terminal events are treated as evidence-traceability findings; orphan artifacts are reported as residual hygiene unless they contradict a terminal claim.

## Required Validators

- `python3 -m long_exposure.tools.promise_check <workspace>` -> return code `0`
  - stdout: `events: 150, plan milestones: 39 | ! WARNING: ledger:line 4: artifact path 'docs/paper_map/' not canonicalized | ! WARNING: orphan artifact in managed path: reports/cycles/report_cycles_1-3.md (no ledger event references it) | ! WARNING: orphan artifact in managed path: reports/cycles/report_cycles_1-3.pdf (no ledger event references it) | ! WARNING: orphan artifact in managed path: reports/cycles/report_cycles_10-12.md (no ledger event references it) | ! WARNING: orphan artifact in managed path: reports/...`
- `python3 -m long_exposure.tools.org_check <workspace>` -> return code `0`
  - stdout: `root files: 12, root dirs: 10; standard folders present: ['audits', 'data', 'docs', 'reports', 'scripts', 'stale', 'tests', 'tools'] | ! WARNING: file at workspace root not in allowed-set: 2603.01127.pdf | ! WARNING: file at workspace root not in allowed-set: 2603.01127.txt | ! WARNING: file at workspace root not in allowed-set: CURATION.yaml | ! WARNING: file at workspace root not in allowed-set: long_exposure_random_surface_live.README | ! WARNING: file at workspace root not in allowed-set: long_exposur...`

Validator status: green.

## Referenced Artifact Summary

- Ledger events parsed: 150.
- Artifact-like references extracted: 868.
- Missing artifact-like references across all events: 2.
- Missing artifact-like references in latest event for their milestone: 1.
- Findings appended this stage: 0.

## Missing Latest-Event References

| Milestone | Latest status | Raw reference | Resolved path |
|---|---:|---|---|
| `M6-final-synthesis` | validated | `reports/final/final_report.md` | `reports/final/final_report.md` |

## Likely Orphan Final/Report Artifacts

These are not appended as findings in this pass because the audit found no contradiction with a terminal claim. They remain useful for final figure/file-map coverage accounting.

- Likely orphan final/report artifacts sampled: 46 of 46.
- `reports/final/run_mode.json`
- `reports/cycles/report_cycles_40-42.md`
- `reports/cycles/report_cycles_28-30.pdf`
- `reports/cycles/report_cycles_31-33.md`
- `reports/cycles/report_cycles_13-15.md`
- `reports/cycles/report_cycles_4-6.pdf`
- `reports/cycles/report_cycles_16-18.pdf`
- `reports/cycles/report_cycles_37-39.pdf`
- `reports/cycles/report_cycles_19-21.md`
- `reports/cycles/report_cycles_19-21.pdf`
- `reports/cycles/report_cycles_1-3.pdf`
- `reports/cycles/report_cycles_13-15.pdf`
- `reports/cycles/report_cycles_22-24.pdf`
- `reports/cycles/report_cycles_46-48.md`
- `reports/cycles/report_cycles_49-50.pdf`
- `reports/cycles/report_cycles_25-27.pdf`
- `reports/cycles/report_cycles_1-3.md`
- `reports/cycles/report_cycles_43-45.md`
- `reports/cycles/report_cycles_10-12.md`
- `reports/cycles/report_cycles_10-12.pdf`
- `reports/cycles/report_cycles_7-9.pdf`
- `reports/cycles/report_cycles_31-33.pdf`
- `reports/cycles/report_cycles_49-50.md`
- `reports/cycles/report_cycles_16-18.md`
- `reports/cycles/report_cycles_40-42.pdf`
- `reports/cycles/report_cycles_37-39.md`
- `reports/cycles/report_cycles_28-30.md`
- `reports/cycles/report_cycles_25-27.md`
- `reports/cycles/report_cycles_4-6.md`
- `reports/cycles/report_cycles_34-36.pdf`
- `reports/cycles/report_cycles_34-36.md`
- `reports/cycles/report_cycles_43-45.pdf`
- `reports/cycles/report_cycles_7-9.md`
- `reports/cycles/report_cycles_46-48.pdf`
- `reports/cycles/report_cycles_22-24.md`
- `audits/final/run_mode.json`
- `audits/final/explore.md`
- `audits/final/final_audit_summary.json`
- `audits/final/audit_reports_index.md`
- `audits/final/stages/verify_6of7.md`
- `audits/final/stages/verify_4of7.md`
- `audits/final/stages/verify_1of7.md`
- `audits/final/stages/verify_5of7.md`
- `audits/final/stages/verify_3of7.md`
- `audits/final/stages/verify_7of7.md`
- `audits/final/stages/verify_2of7.md`


## Findings Appended

- None. Missing latest-event artifact references were either absent or already represented by the existing findings ledger.

## Gate Check

- Expected file written: `<workspace>/audits/final/stages/test_3of7.md`.
- Findings appended this stage: `0`.
- Validator execution observed: both required validators were run from `<workspace>`.
