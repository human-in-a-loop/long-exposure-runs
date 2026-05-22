# Final Audit Stage 3: Test Pass

Stage: 3 of 4, test (1/1)
Run mode: delta audit against committed baseline final audit.
Trace file: `audits/final/stages/test_1of1_trace.json`

## Scope

This adversarial pass tested whether the post-baseline delta verdict from the explore and verify stages could be broken by:

- validator failures;
- silent master-ledger promotion;
- report files newer than the baseline boundary but not covered by the verified delta slice;
- closure-document mtime drift without ledger support;
- orphan, supersession-pending, or active status inconsistencies that would reopen the final closure claim;
- taxonomy-results site regressions adjacent to the verified communication-layer closure.

No campaign source, scientific ledger, report, site, or evidence artifact was modified during this stage.

## Required Validators

| Check | Command | Exit | Result |
|---|---|---:|---|
| Promise ledger validator | `python3 -m long_exposure.tools.promise_check <run-root>` | 0 | Passed with inherited missing-artifact warnings only. |
| Organization validator | `python3 -m long_exposure.tools.org_check <run-root>` | 0 | Passed with inherited workspace-root allowed-set warnings only. |

The validator warnings match the known inherited warning pattern from prior stages. They did not escalate to a failing validator exit, and the latest delta artifacts did not introduce a new validator failure.

## Adjacent Regression Checks

| Check | Command | Exit | Result |
|---|---|---:|---|
| Taxonomy-results public text tests | `pytest -q tests/test_taxonomy_results_site_public_text.py` | 0 | 5 tests passed. |
| Taxonomy asset/test compilation | `python3 -m py_compile scripts/build_taxonomy_results_site_assets.py tests/test_taxonomy_results_site_public_text.py` | 0 | Compilation passed. |

These checks directly exercise the communication-layer artifact that was added after the baseline final audit. No public-text or syntax regression was observed.

## Master Ledger Boundary

| Ledger | Line count | Non-header rows | Test result |
|---|---:|---:|---|
| `prediction_ledger.tsv` | 1 | 0 | Header-only; no prediction promotion. |
| `speculation_ledger.tsv` | 1 | 0 | Header-only; no speculation promotion. |

This supports the post-baseline closure claim that the later free-tier recovery, taxonomy-results site, and handoff artifacts did not promote a cross-track prediction or speculation row.

## Report Drift Test

The baseline boundary from `audits/final/run_mode.json` and the commit marker was used to identify report files newer than the committed baseline. Nine Markdown cycle reports had mtimes newer than the boundary:

- `reports/cycles/report_cycles_24-26.md`
- `reports/cycles/report_cycles_27-29.md`
- `reports/cycles/report_cycles_30-32.md`
- `reports/cycles/report_cycles_33-35.md`
- `reports/cycles/report_cycles_38-40.md`
- `reports/cycles/report_cycles_41-43.md`
- `reports/cycles/report_cycles_44-46.md`
- `reports/cycles/report_cycles_47-49.md`
- `reports/cycles/report_cycles_50-52.md`

The verify stage had already tested the cycle 33-35 and 38-52 reports. This test stage inspected the earlier drift candidates, reports 24-32, because they also fall after the baseline boundary by mtime.

Verdict on reports 24-32: no new defect. They are conservative no-promotion reports. They repeatedly state that the master `prediction_ledger.tsv` and `speculation_ledger.tsv` remained header-only and that Track 1, Track 2, Track 3, Track 4, Track 5, and Track 6 recovery work did not satisfy promotion/reopening predicates. They do not reopen a baseline finding or contradict the later final free-tier closure synthesis.

## Closure And Supersession Drift Test

Closure/supersession-like files were scanned for mtime drift and ledger references. Relevant post-baseline closure files had ledger support:

| Artifact | Drift observation | Ledger support | Test result |
|---|---|---:|---|
| `reports/reopen/final_free_tier_closure_synthesis.md` | Newer than baseline; created as final free-tier synthesis. | 2+ refs, latest event under `_plan/final-free-tier-closure-synthesis`. | Supported. |
| `data/reopen/final_free_tier_track_status.tsv` | Newer than baseline and verified in Stage 2. | Included in final free-tier closure synthesis artifact set. | Supported. |
| `reports/final_campaign_handoff_manifest.md` | Newer than baseline; mtime before auditor repair event. | Worker and auditor events under `_plan/final-campaign-handoff-manifest`. | Supported. |
| `reports/taxonomy_results_site_closure_note.md` | Mtime is later than the worker event timestamp. | Event `_plan/taxonomy-results-site-closure` references the note; content remains a non-reopen closure note. | Not a confirmed defect. |

The taxonomy-results site closure note was the only relevant closure document with mtime later than its ledger event. Direct content inspection showed a 15-line closure note that does not alter scientific statuses, regenerate evidence tables, promote master-ledger rows, or add biological claims. The adjacent site tests and master-ledger counts passed. I classify this as a harmless timestamp drift/residual audit note, not a CRITICAL or MODERATE finding.

Generated `__pycache__` files matched the closure-name scan because their filenames contain closure-related test/module names. They are build/test byproducts, not closure documents, and no finding is recorded for them.

## Active Status And Supersession-Pending Test

The latest promise ledger contains 242 events. The post-baseline validated delta events are lines 225-242:

- `_plan/final-free-tier-closure-synthesis`
- `_run/report_cycles_33-35`
- `_plan/taxonomy-results-site`
- `_plan/taxonomy-results-site-closure`
- `_plan/final-campaign-handoff-manifest`
- `_run/report_cycles_38-40`
- `_run/report_cycles_41-43`
- `_run/report_cycles_44-46`
- `_run/report_cycles_47-49`
- `_run/report_cycles_50-52`

Manager `_manager/validator-warnings` rows remain in-progress/watch-only and correspond to validator warnings that exit 0. Older action-required and in-progress milestone rows are inherited process or pre-closure status debt already accounted for by the baseline audit and later closure synthesis; no new post-baseline artifact reopened them.

No supersession-pending status was found in the delta closure path.

## Figure And Site Artifact Spot Check

The taxonomy-results site contains figure assets under `taxonomy_results_site/assets/figures/`, and Stage 2 verified required figure assets and site data layout. This stage rechecked the broader site artifact surface through public-text tests and compilation. No missing referenced figure or site-regression finding was confirmed.

## Findings Appended

No structured findings were appended to `audits/final/findings.jsonl` during this stage.

Severity counts for this stage:

- CRITICAL: 0
- MODERATE: 0
- MINOR: 0

## Residual Notes For Document Stage

- The final report should mention that reports 24-32 also have post-baseline mtimes but were adversarially inspected here and found to preserve the same no-promotion boundary.
- The taxonomy-results closure note has harmless timestamp drift after its ledger event; because its content and tests preserve the closure boundary, it should be recorded as residual timestamp noise only if the document stage includes residual notes.
- The promise and organization validators remain green with inherited warnings; this supports `promise_check_status: green` in the summary JSON unless later evidence changes.
- No reconciliation event is warranted by this test pass.

## Stage Verdict

The Stage 3 adversarial pass did not break the Stage 2 verification verdict. Post-baseline delta artifacts remain supported by on-disk evidence, master ledgers remain header-only, validators are green with inherited warnings only, and no new CRITICAL, MODERATE, or MINOR findings were confirmed.
