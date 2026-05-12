# Final Audit Stage 16 - Test Pass 6 of 9

Timestamp: 2026-05-12T20:21:52Z

Scope: adversarial pass focused on artifact-index completeness and public handoff/final-report traceability. This pass intentionally did not re-run the earlier final-package readiness-boundary audit except where needed to compare public index claims against current ledger state.

## Required Validators

Command:

```bash
python3 -m long_exposure.tools.promise_check .
```

Observed result: exit code 1.

Output:

```text
events: 220, plan milestones: 41
x ERROR:   ledger:line 220: event_id is not a valid UUID
x ERROR:   ledger:line 220: superseded event for '_manager/validator-warnings' missing 'supersedes' field
```

Verdict: still red for the already-recorded CRITICAL `_manager/validator-warnings` ledger defect at line 220. No new validator error class appeared in this pass.

Command:

```bash
python3 -m long_exposure.tools.org_check .
```

Observed result: exit code 0.

Output:

```text
root files: 10, root dirs: 10; standard folders present: ['audits', 'data', 'docs', 'reports', 'scripts', 'stale', 'tests', 'tools']
! WARNING: file at workspace root not in allowed-set: CURATION.yaml
! WARNING: file at workspace root not in allowed-set: memory_centric_agentic_inference_package_2026-05-12T0019.zip
! WARNING: file at workspace root not in allowed-set: memory_centric_agentic_inference_package_latest.zip
```

Verdict: green with the known package-root warnings only.

## Closure / Supersession Document Probe

Command:

```bash
rg --files | rg '(CLOSURE|SUPERSEDES)' || true
```

Observed result: no matching files. No silent closure/supersession document drift was found.

## Plan / Ledger Consistency Probe

Latest ledger state by milestone:

```text
latest_status_distribution {'in-progress': 1, 'validated': 89, 'superseded': 2}
plan_milestones 41
latest_plan_status {'validated': 41}
missing_plan_milestones []
nonterminal_plan_milestones []
latest_action_required []
latest_reopened []
latest_low_or_provisional_terminal []
```

Verdict: all 41 plan milestones have latest status `validated`; no latest `action_required`, `reopened`, missing, or low/provisional terminal plan states were found.

## Artifact Index Integrity Probe

File checked: `data/handoff_artifact_index.csv`.

Internal consistency:

```text
rows: 278
missing_paths: 0
false_exists_rows: 0
production_true_markers: 0
bad_boundary_rows: 0
milestones represented: 24
artifact types: narrative=33, data=121, script_or_test=59, figure=59, artifact=6
evidence classes: validated_artifact=74, derived=29, simulated=59, sourced=12, derived_synthesis=32, synthetic_internal_control_plane=43, host_local_proxy=14, synthetic_fixture_or_contract_ready=15
```

Verdict: the rows present in the artifact index are internally valid. The index does not contain missing paths or production-readiness overclaims.

Completeness against current plan and ledger:

```text
plan milestones: 41
index milestones: 24
validated plan milestones missing from handoff index: 17
ledger concrete artifact paths: 566
index paths: 271
ledger concrete non-report paths missing from index: 261
```

Validated plan milestones absent from `data/handoff_artifact_index.csv`:

```text
M-PRODDEPLOY-1 latest line 124, 11/11 latest artifacts exist
M-TRENDS-1 latest line 128, 11/11 latest artifacts exist
M-ADAPTER-1 latest line 132, 15/15 latest artifacts exist
M-PORT-1 latest line 136, 15/15 latest artifacts exist
M-INTAKE-1 latest line 141, 16/16 latest artifacts exist
M-ATTEST-1 latest line 146, 17/17 latest artifacts exist
M-TRUSTPOL-1 latest line 151, 17/17 latest artifacts exist
M-GATECHAIN-1 latest line 155, 16/16 latest artifacts exist
M-ROOTINT-1 latest line 161, 16/16 latest artifacts exist
M-TIMEBASE-1 latest line 165, 16/16 latest artifacts exist
M-REDACT-1 latest line 170, 17/17 latest artifacts exist
M-UNCERT-1 latest line 175, 16/16 latest artifacts exist
M-CAUSAL-1 latest line 180, 17/17 latest artifacts exist
M-PRODREPLAY-1 latest line 185, 10/10 latest artifacts exist
M-EVIDART-1 latest line 190, 15/15 latest artifacts exist
M-LIVECOLLECT-1 latest line 195, 16/16 latest artifacts exist
M-CLAIMEXP-1 latest line 200, 17/17 latest artifacts exist
```

Examples of ledger-referenced artifacts missing from the handoff index include current production-deployment, trend, adapter-conformance, intake, attestation, gatechain, root-enrollment, timebase, redaction, uncertainty, causal, replay, evidence-artifact, live-collector, and claim-expiry artifacts. The latest ledger events for these milestones validate concrete artifacts that exist on disk, but the canonical handoff artifact index does not enumerate them.

Public-report claim checked: `final_report.md` says the hand-off index maps "every tracked campaign artifact" to type, producer, verifier, milestone, evidence class, dependencies, production-readiness impact, and limitation. That statement is stale against the current run state because 17 later validated plan milestones and 261 concrete non-report ledger artifact paths are absent from the index.

Severity: MODERATE. This is not a scientific-artifact failure and does not undermine the production-readiness boundary, but it is a public-record traceability defect. A reader using `data/handoff_artifact_index.csv` as the complete campaign artifact map would miss substantial validated post-handoff work.

## Handoff Verifier Probe

Command:

```bash
python3 tests/verify_campaign_handoff.py
```

Observed result:

```text
OK: campaign handoff package verified.
```

Verdict: the existing verifier passes but does not check artifact-index completeness against the current plan/ledger. This explains why the stale index can remain undetected by the campaign-handoff test.

## Claim Boundary Spot Check

Files checked:

- `data/handoff_claim_traceability.csv`: 17 rows
- `data/final_claim_readiness_matrix.csv`: 17 rows
- `data/production_target_replay_claim_boundary.csv`: 17 rows
- `data/handoff_reproduction_manifest.csv`: 49 rows

Observed result: no rows contained `production_ready=true`, `production_calibrated=true`, `claim_credit_allowed=true`, or `production_endorsed=true`.

Verdict: no new production-readiness overclaim was found in this pass.

## Findings Appended

One finding appended to `audits/final/findings.jsonl`:

- MODERATE: `M-HANDOFF-1`, `stale_artifact_index`, because `data/handoff_artifact_index.csv` and the public final-report description of it no longer cover the current run's validated plan milestones and concrete ledger artifacts.

Findings count before append:

```text
lines 12
counts {'MODERATE': 11, 'CRITICAL': 1}
```

Expected findings count after append: 13 total, with 1 CRITICAL and 12 MODERATE.

## New Issues Introduced

None. This pass wrote only this stage report and appended one structured audit finding.

## Remaining Issues

- CRITICAL: unresolved `promise_ledger.jsonl` line 220 validator failure for `_manager/validator-warnings`.
- MODERATE: stale periodic reports already recorded in earlier verify/test passes.
- MODERATE: newly recorded stale handoff artifact index / final-report artifact-map claim.
