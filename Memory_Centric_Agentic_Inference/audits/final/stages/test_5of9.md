# Final Auditor Stage 15 - Test Pass 5 of 9

Stage input: `15 of 20 (test (5/9))`  
Expected file: `<workspace>/audits/final/stages/test_5of9.md`  
Working directory: `<workspace>`  
Wall cap hit: `false`

## Scope

This adversarial pass checked whether the closing verdict can be broken through reproduction-manifest dishonesty, stale fanout-report claims, silent supersession artifacts, or plan/ledger status drift. It did not re-audit already-cleared final-readiness boundary claims from test pass 4.

## Required Validators

### `python3 -m long_exposure.tools.promise_check .`

Result: **red**.

Observed output:

```text
events: 220, plan milestones: 41
x ERROR:   ledger:line 220: event_id is not a valid UUID
x ERROR:   ledger:line 220: superseded event for '_manager/validator-warnings' missing 'supersedes' field
```

Assessment: this is the same unresolved CRITICAL issue already recorded for `_manager/validator-warnings`; no duplicate finding was appended in this pass.

### `python3 -m long_exposure.tools.org_check .`

Result: **green exit**, with the known package-root warnings:

```text
root files: 10, root dirs: 10; standard folders present: ['audits', 'data', 'docs', 'reports', 'scripts', 'stale', 'tests', 'tools']
! WARNING: file at workspace root not in allowed-set: CURATION.yaml
! WARNING: file at workspace root not in allowed-set: memory_centric_agentic_inference_package_2026-05-12T0019.zip
! WARNING: file at workspace root not in allowed-set: memory_centric_agentic_inference_package_latest.zip
```

Assessment: no new finding. These are package-root warnings, not evidence that the run's scientific artifacts or milestone claims are invalid.

## Silent Supersession And Status Drift Probe

Command: `rg --files | rg '(CLOSURE|SUPERSEDES)'`

Result: no matching closure or supersession documents were present, so no mtime drift or unregistered closure-document supersession was detected.

Latest ledger status probe:

- Latest status distribution: `validated: 89`, `superseded: 2`, `in-progress: 1`.
- Latest superseded records:
  - `_manager/ledger-integrity`, line 86, includes `supersedes`.
  - `_manager/validator-warnings`, line 220, lacks `supersedes`; this is the known CRITICAL issue.
- Latest `action_required`: none.
- Latest `reopened`: none.

Assessment: no new plan/ledger drift beyond the known line 220 ledger defect.

## Reproduction Manifest Probe

Manifest inspected: `data/handoff_reproduction_manifest.csv`

Structural checks:

- Rows: 49.
- Missing primary artifact paths: 0.
- Bad command targets: 0.
- Rows with `exists != true`: 0.
- Rows missing the production-boundary disclaimer: 0.

Sampled executable checks from the manifest:

| Step | Command | Result |
|---:|---|---|
| 43 | `python3 tests/verify_final_architecture_package.py` | exit 0; final architecture package verified |
| 44 | `python3 tests/verify_campaign_handoff.py` | exit 0; campaign handoff package verified |
| 45 | `python3 tests/verify_memory_object_abi.py` | exit 0; ABI validation artifacts regenerated and verified |
| 46 | `python3 tests/verify_memory_object_abi_integration.py` | exit 0; ABI integration artifacts regenerated and verified |
| 47 | `python3 tests/verify_architecture_control_plane_progression.py` | exit 0; control-plane progression verified |

Assessment: the manifest's executable validation commands support the handoff claim for the sampled validation tier. No reproduction-manifest finding was appended.

## Stale Fanout Report Probe

Files scanned for unresolved/stale language in this pass:

- `reports/cycles/report_cycles_4-6_clone_0.md`
- `reports/cycles/report_cycles_4-6_clone_2.md`
- `reports/cycles/report_cycles_7-9_clone_0.md`
- `reports/cycles/report_cycles_7-9_clone_2.md`

New distinct issue found:

- `reports/cycles/report_cycles_4-6_clone_2.md` says clone 2 was not yet integrated into the parent `M-EXP-1` measurement harness and that parent `M-EXP-1` CSV ingestion/ledger cleanup remained the only open gap.
- Later `promise_ledger.jsonl` line 82 validates post-merge `M-EXP-1` integration across trajectory reuse, provenance-validation overhead, semantic-cache correctness/invalidation, and durable replay-tail measurement designs.
- Current parent CSV evidence contradicts the stale report statement:
  - `data/measurement_experiment_specs.csv`: 25 total rows, 11 CDR-related rows.
  - `data/measurement_thresholds.csv`: 18 total rows, 10 CDR-related rows.
  - `data/measurement_claim_update_matrix.csv`: 29 total rows, 11 CDR-related rows.

Finding appended:

- Severity: MODERATE
- Milestone: `_run/report_cycles_4-6`
- Kind: `stale_periodic_report_statement`
- Destination: `<workspace>/audits/final/findings.jsonl`

## Findings File State After Append

Parsed findings file:

- Lines: 12.
- Counts: `CRITICAL: 1`, `MODERATE: 11`, `MINOR: 0`.
- Latest appended finding: `_run/report_cycles_4-6`, MODERATE, `stale_periodic_report_statement`.

## New Issues Introduced

No CRITICAL or MODERATE issues were introduced by this test pass. The sampled validation commands regenerated their expected data/figure outputs and exited 0.

## Stage Verdict

Test pass 5 found one new MODERATE public-record honesty issue: a stale clone-2 cycle 4-6 report statement about parent `M-EXP-1` integration. The run's core handoff reproduction commands sampled in this pass remain executable. The unresolved CRITICAL ledger defect at line 220 remains the blocking validator issue for the final public record.
