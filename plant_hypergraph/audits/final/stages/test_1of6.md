# Final Audit Stage 8 - Test 1/6

## Scope

Adversarial test pass focused on validator baseline, plan/ledger terminal status consistency, contradiction/supersession signals, closure-document drift, periodic report inventory, and planned-milestone artifact existence.

## Commands Run

From `<run-root>`:

```bash
python3 -m long_exposure.tools.promise_check <run-root>
python3 -m long_exposure.tools.org_check <run-root>
```

Additional structured scan:

- Parsed `promise_ledger.jsonl` as JSONL.
- Checked latest status/confidence for M1-M8.
- Searched for `supersedes`, `supersedes_event_id`, and `superseded_by` ledger fields.
- Searched narrative/status text for contradiction, invalidation, reopened, supersession-pending, and superseded signals.
- Searched workspace filenames containing `CLOSURE` or `SUPERSEDES`.
- Counted report files matching the configured report glob.
- Checked artifact existence for latest planned milestone events M1-M8.

## Validator Results

`promise_check` exited `0`.

Observed warnings were the same nonblocking process warnings already identified in prior stages:

- Three noncanonical directory artifact paths for `data/public_taxonomy_sample/v0.1/raw/{wfo,gbif,opentree}/`.
- Missing ledger-tracked manager assessment artifacts under `long-exposure/manager_assessments/...`.

These warnings do not invalidate planned milestone closure in this pass because the latest M5 auditor event explicitly names all individual raw JSON source artifacts, and the missing manager artifacts are process-scope records rather than M1-M8 deliverables.

`org_check` exited `0`.

Observed warnings were workspace-organization warnings:

- Root-level final deliverables such as `artifact_index.md`, `audit_report.md`, and `research_contribution_ledger.md`.
- Root-level run prompt/score/log files.

These warnings are not plan-adherence defects because M8 required those canonical deliverables by name at the workspace root.

## Plan/Ledger Consistency

Latest planned milestone states from the full ledger:

| Milestone | Status | Confidence | Latest evidence |
|---|---|---|---|
| M1 | validated | high | Ledger line 7, 6 artifacts |
| M2 | validated | high | Ledger line 8, 1 artifact |
| M3 | validated | high | Ledger line 13, 9 artifacts |
| M4 | validated | high | Ledger line 14, 3 artifacts |
| M5 | validated | high | Ledger line 18, 60 artifacts |
| M6 | validated | high | Ledger line 23, 15 artifacts |
| M7 | validated | high | Ledger line 26, 7 artifacts |
| M8 | validated | high | Ledger line 31, 4 artifacts |

All latest planned milestone artifact paths existed on disk.

Note: an intermediate scan initially compared the `confidence` object directly to the string `high`, which made it print the full M1-M8 events under an "unexpected" heading. Manual inspection of the same output confirms each object has `confidence.level == high`; this was an audit-script representation issue, not a run finding.

## Supersession and Contradiction Checks

- Ledger events parsed: 68.
- Supersedes edges/fields found: 0.
- Contradiction clusters from input summary: none.
- Status/narrative scan found no planned milestone with `invalidated`, `reopened`, `superseded`, or `supersession-pending` semantics.
- Closure or supersession documents found on disk: 0.
- Report files found: 26, from `reports/cycles/report_cycles_1-3.md` through `reports/cycles/report_cycles_76-77.md`.

Open non-plan entries observed:

- `_run/start`: `in-progress/high`.
- `_manager/validator-warnings`: `in-progress/medium`.

These remain process-scope entries and are not counted as residual debt against planned milestones in this test pass.

## Findings Appended

None.

No CRITICAL, MODERATE, or MINOR planned-milestone finding was identified in this slice, so `<run-root>/audits/final/findings.jsonl` was left unchanged.
