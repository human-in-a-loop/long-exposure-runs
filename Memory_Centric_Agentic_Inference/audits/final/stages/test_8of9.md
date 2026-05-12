# Final Audit Stage 18 - Test Pass 8 of 9

Stage input: `18 of 20 (test (8/9))`

Expected file: `<workspace>/audits/final/stages/test_8of9.md`

## Scope

This adversarial pass avoided rechecking areas already covered by test passes 1-7 except for the mandatory validators and global ledger/plan consistency probes. The fresh focus was public-record drift in the cycles 10-12 report, the current final narrative documents, and the registered package archive artifacts.

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

Verdict: red, same known CRITICAL issue already recorded in `audits/final/findings.jsonl` for `_manager/validator-warnings`. No duplicate finding appended in this pass.

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

Verdict: green with known root package warnings.

## Closure and Supersession Documents

Command:

```bash
rg --files | rg '(CLOSURE|SUPERSEDES)' || true
```

Observed result: no matching files.

Verdict: no closure or supersession documents were available for mtime drift checks.

## Plan and Ledger Consistency

Probe result:

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

Verdict: no new orphan plan milestone, missing plan milestone, action-required latest state, reopened latest state, or low/provisional terminal state was found. The sole latest in-progress record remains `_run/start`, which is not a plan milestone.

## Cycles 10-12 Report Probe

File inspected:

- `reports/cycles/report_cycles_10-12.md`

The report states the cycle-10 compression repair under the narrowed queue-attribution claim, the cycle-11 runtime prototype, and the cycle-12 sourced calibration map. The potentially risky statements were checked against later ledger and final artifacts:

- `M-COMP-1` is described as no longer supporting a positive queue-threshold preservation claim under current synthetic trace and coefficients.
- `M-PROTO-1` is described as a synthetic trace-replay prototype, not production scheduling or calibrated performance.
- `M-CALIB-1` is described as a sourced map that preserves deferred constants rather than retroactively measuring them.

Verdict: no new finding. The cycles 10-12 report does not preserve a contradicted terminal state comparable to the stale periodic-report issues found in earlier passes.

## Current Final Narrative Probe

Files inspected:

- `final_report.md`
- `memory-centric-agentic/final_architecture_package.md`
- `memory-centric-agentic/final_synthesis.md`
- `data/handoff_open_questions.csv`
- `data/final_production_experiment_backlog.csv`

Observed:

- `final_report.md` preserves the zero-production-ready boundary and says Option B/C are validated mechanisms and contract-ready pathways, not production endorsements.
- `memory-centric-agentic/final_architecture_package.md` requires direct `production_target` evidence plus production gates before `production_ready=true`.
- `memory-centric-agentic/final_synthesis.md` labels economic/energy and durable trajectory-reuse claims as unresolved or speculative where production calibration is absent.
- `data/handoff_open_questions.csv` has 11 rows, all with `current_status=open_production_calibration_required`.
- `data/final_production_experiment_backlog.csv` preserves the requirement that claim promotion needs production-target evidence and ingestion gates.

Verdict: no new production-readiness or claim-boundary finding. The already-recorded `M-HANDOFF-1` finding for stale artifact-index completeness remains distinct and is not duplicated here.

## Package Archive Probe

Files inspected:

- `memory_centric_agentic_inference_package_latest.zip`
- `memory_centric_agentic_inference_package_2026-05-12T0019.zip`
- `promise_ledger.jsonl:118`

Observed:

```text
memory_centric_agentic_inference_package_latest.zip -> memory_centric_agentic_inference_package_2026-05-12T0019.zip
archive entries: 4
has_final_report: False
has_handoff_index: False
has_abiint_note: False
```

Archive contents:

```text
memory_centric_agentic_inference/README.md
memory_centric_agentic_inference/report/CURATION.yaml
memory_centric_agentic_inference/report/MANIFEST.md
memory_centric_agentic_inference/report/REFERENCES.md
```

The archive README accurately warns that `curation_complete: false` and says the package is intentionally incomplete. However, the same README's verification instructions say to open `report/final_report.pdf` or `final_report.md`, and neither file exists in the archive. The archive manifest is also a cycles 19-21 snapshot, while the live ledger continued through later validated milestones and the package artifacts were registered in `_run/final-package-artifacts` at `promise_ledger.jsonl:118`.

Verdict: new MODERATE finding appended. The archive is not the live workspace and is caveated as incomplete, so this is not a core research correctness failure. It is still a misleading registered handoff artifact because its own verification instructions reference absent report files and the archive omits later final/handoff artifacts.

## Findings Appended

One finding appended to `<workspace>/audits/final/findings.jsonl`:

- MODERATE: `_run/final-package-artifacts`, `incomplete_registered_package_archive`

## Findings Count After Append

Expected count after append:

```text
CRITICAL: 1
MODERATE: 14
MINOR: 0
Total JSONL findings: 15
```

## New Issues Introduced

None observed. This stage wrote only the expected stage file and appended one structured finding.
