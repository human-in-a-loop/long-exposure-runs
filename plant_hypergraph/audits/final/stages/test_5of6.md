# Final Audit Stage 12 - Test 5/6

## Scope

Adversarial pass for silent supersession and closure drift. This pass checked for:

- closure or SUPERSEDES documents that would change the public record without matching ledger state;
- final-document mtime drift after the latest M8 `validated/high` ledger event;
- planned milestone status drift, orphan M-like milestones, and supersession-pending states;
- periodic report markdown/PDF pairing and ledger registration;
- validator regressions since prior test passes.

## Validators

Command results:

- `python3 -m long_exposure.tools.promise_check <run-root>`: exit 0.
- `python3 -m long_exposure.tools.org_check <run-root>`: exit 0.

Observed validator warnings matched prior passes:

- `promise_check` still warns that three M5 raw directory artifact paths are not canonicalized:
  - `data/public_taxonomy_sample/v0.1/raw/wfo/`
  - `data/public_taxonomy_sample/v0.1/raw/gbif/`
  - `data/public_taxonomy_sample/v0.1/raw/opentree/`
- `promise_check` still warns about missing ledger-tracked manager assessment artifacts under `long-exposure/manager_assessments/...`.
- `org_check` still warns about root-level final deliverables and run prompt/score/log files outside the preferred allow-list.

These remain nonblocking process-scope warnings. They do not invalidate M1-M8 because prior passes verified the latest planned-milestone artifacts directly, including the individual M5 raw JSON files and the required root M8 deliverables.

## Supersession And Closure Search

Closure/SUPERSEDES documents found outside `audits/final/` and `.git/`: 0.

Ledger supersedes edges from the causal summary: 0.

No planned milestone has latest status `superseded`, `reopened`, `invalidated`, `action_required`, or `deferred`.

The only latest non-plan open entries remain:

| Milestone | Status | Confidence | Scope |
|---|---:|---:|---|
| `_run/start` | `in-progress` | `high` | process/run marker |
| `_manager/validator-warnings` | `in-progress` | `medium` | process validator-warning marker |

These are not M1-M8 plan-adherence defects.

## Planned Milestone Status Drift

Latest planned milestone states from the full ledger:

| Milestone | Latest status | Confidence | Ledger line | Timestamp |
|---|---:|---:|---:|---|
| M1 | `validated` | `high` | 7 | 2026-05-17T01:00:59Z |
| M2 | `validated` | `high` | 8 | 2026-05-17T01:00:59Z |
| M3 | `validated` | `high` | 13 | 2026-05-17T01:23:30Z |
| M4 | `validated` | `high` | 14 | 2026-05-17T01:23:30Z |
| M5 | `validated` | `high` | 18 | 2026-05-17T02:03:30Z |
| M6 | `validated` | `high` | 23 | 2026-05-17T02:45:30Z |
| M7 | `validated` | `high` | 26 | 2026-05-17T03:12:30Z |
| M8 | `validated` | `high` | 31 | 2026-05-17T03:36:30Z |

Missing planned milestones: none.

Orphan `M\d+` ledger milestones outside M1-M8: none.

## Final Document Drift

Latest M8 validation timestamp: 2026-05-17T03:36:30Z.

Final root document mtimes:

| Document | Exists | Size | SHA-256 prefix | mtime UTC | mtime after M8 validation |
|---|---:|---:|---:|---:|---:|
| `final_report.md` | yes | 10966 | `493d9299e6a198b6` | 2026-05-17T03:00:39.157860+00:00 | no |
| `artifact_index.md` | yes | 7838 | `6d330ddd84f022c1` | 2026-05-17T03:00:39.160861+00:00 | no |
| `research_contribution_ledger.md` | yes | 3617 | `488842babc7caffc` | 2026-05-17T03:00:39.161861+00:00 | no |
| `audit_report.md` | yes | 5026 | `b5bddc5236dcf4f0` | 2026-05-17T03:00:39.161861+00:00 | no |

No silent final-document drift was detected after the latest M8 validation event.

## Periodic Report Registration

Report pairing and registration check:

- Markdown reports under `reports/cycles/report_cycles_*.md`: 26.
- PDF reports under `reports/cycles/report_cycles_*.pdf`: 26.
- Missing PDF for markdown report: none.
- Missing markdown for PDF report: none.
- Ledger `_run/report_cycles_*` registrations: 26.
- Markdown reports without ledger registration: none.
- Ledger registrations without markdown report: none.

## Findings

No CRITICAL findings.

No MODERATE findings.

No MINOR findings added in this pass. Prior process-scope validator warnings remain documented and unchanged.

## Findings Appended

0 findings appended to `<run-root>/audits/final/findings.jsonl`.

The findings file remained at 0 lines after this stage.
