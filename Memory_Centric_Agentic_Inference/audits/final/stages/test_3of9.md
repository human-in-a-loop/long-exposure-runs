# Final Audit Stage 13 - Test Pass 3/9

## Scope

Adversarial closure test focused on periodic report registration, stale
fanout-report claims, plan/ledger terminal state, closure/supersession
documents, and confidence-calibration surface. This pass intentionally avoids
repeating artifact, figure, and complete plan-milestone probes already covered
by test passes 1-2 except where needed for adjacent regression checks.

## Required Validators

Command:

```bash
python3 -m long_exposure.tools.promise_check .
```

Observed result:

```text
events: 220, plan milestones: 41
x ERROR:   ledger:line 220: event_id is not a valid UUID
x ERROR:   ledger:line 220: superseded event for '_manager/validator-warnings' missing 'supersedes' field
```

Verdict: known CRITICAL remains unresolved. This is the same
`_manager/validator-warnings` line-220 defect already recorded in
`audits/final/findings.jsonl`; this pass did not append a duplicate.

Command:

```bash
python3 -m long_exposure.tools.org_check .
```

Observed result:

```text
root files: 10, root dirs: 10; standard folders present: ['audits', 'data', 'docs', 'reports', 'scripts', 'stale', 'tests', 'tools']
! WARNING: file at workspace root not in allowed-set: CURATION.yaml
! WARNING: file at workspace root not in allowed-set: memory_centric_agentic_inference_package_2026-05-12T0019.zip
! WARNING: file at workspace root not in allowed-set: memory_centric_agentic_inference_package_latest.zip
```

Verdict: no new finding. These package-root warnings are unchanged from prior
test passes and are not the active validator failure.

## Closure And Supersession Document Probe

Command:

```bash
rg --files | rg '(CLOSURE|SUPERSEDES)' || true
```

Observed result: no matching closure or supersession documents.

Verdict: no silent closure-document mtime drift to assess in this pass.

## Report Registration Probe

Structured ledger/file comparison over `reports/cycles/report_cycles_*.md`
found:

- Report markdown files present: 19.
- Report markdown files with ledger registration: 19.
- Unregistered report markdown files: 0.

All periodic and fanout reports are therefore known to the ledger. The risk is
not orphaned report files; it is stale statements inside registered reports.

## Fanout Report Staleness Probe

This pass checked report-range statements containing record-gap, missing-work,
or parent-integration language against later ledger and data evidence.

New finding appended:

- `reports/cycles/report_cycles_1-3_clone_2.md` lines 236-248 state that the
  clone-2 plan is not yet complete as parent `M-EXP-1` CSV integration and
  that current parent measurement CSVs are not yet populated for clone-2
  `CDR-*` rows.
- Later `promise_ledger.jsonl` line 82 validates `M-EXP-1` after post-merge
  integration across trajectory reuse, provenance-validation overhead,
  semantic-cache correctness/invalidation, and durable replay-tail measurement
  designs.
- Current CSV evidence confirms the integration exists:
  `data/measurement_experiment_specs.csv` has 11 `CDR-*` rows,
  `data/measurement_thresholds.csv` has 10 `T-SEM-*`/`T-DUR-*` rows, and
  `data/measurement_claim_update_matrix.csv` has 11 related claim-update rows.

Severity: MODERATE. The clone report is a historical branch artifact, not a
technical failure in the measurement harness, but it is a public-record
statement that is false if read as current closure state.

## Plan And Confidence Regression Probe

Structured parse over the latest ledger state found:

- Latest status distribution across distinct ledger milestones:
  `validated=89`, `superseded=2`, `in-progress=1`.
- The sole latest `in-progress` record is `_run/start`, the run-root event.
- Plan milestones parsed: 41.
- Missing plan milestones: 0.
- Nonterminal plan milestones: 0.
- Latest `action_required` milestones: 0.
- Latest `reopened` milestones: 0.
- Latest terminal records with `low` or `provisional` confidence: 0.

Verdict: no new plan/ledger terminal-state finding. All plan milestones remain
latest `validated`, and there are no low-confidence terminal milestone states.

## Findings Appended

One MODERATE finding was appended to
`<workspace>/audits/final/findings.jsonl`:

- `_run/report_cycles_1-3`: stale fanout report statement in
  `report_cycles_1-3_clone_2.md` contradicted by later `M-EXP-1` integration
  validation and current parent CSV rows.

Findings file state after append:

- Prior findings: 10.
- New findings this pass: 1.
- Expected total after append: 11.

## Stage Conclusion

Test pass 3/9 reconfirmed the known red `promise_check` state, found no
unregistered report markdown files, no closure/supersession documents, no
nonterminal plan milestones, and no low/provisional terminal records. It found
one additional MODERATE public-record staleness issue in a registered fanout
report.
