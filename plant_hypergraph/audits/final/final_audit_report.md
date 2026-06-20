# Final Audit Report - PhytoGraph Delta Closure

Scope: delta audit over post-baseline deliverables newer than the committed final-audit boundary, with the prior `audits/final/final_audit_report.md` baseline treated as canonical for earlier work. This report covers the new closure, handoff, taxonomy-results-site, and periodic report artifacts inspected in this final-audit pass.

## Status distribution

Delta milestone status distribution:

| Status | Count |
|---|---:|
| validated | 10 |
| in-progress | 1 |
| not-started | 0 |
| action_required | 0 |
| deferred | 0 |
| reopened | 0 |
| superseded | 0 |
| invalidated | 0 |

The single in-progress item is `_manager/validator-warnings`, a watch-only manager status. It did not change the scientific closure state; both required validators exited 0 during the test pass.

## Plan adherence

| Milestone | Terminal status | Confidence | Evidence count | Latest evidence pointer |
|---|---|---|---:|---|
| `_plan/final-free-tier-closure-synthesis` | validated | high | 5 | `reports/reopen/final_free_tier_closure_synthesis.md`; `data/reopen/final_free_tier_track_status.tsv`; `reports/reopen/figures/final_free_tier_track_status.png`; ledger events 225-226 |
| `_plan/taxonomy-results-site` | validated | high | 4 | `taxonomy_results_site/`; `taxonomy_results_site/data/site_summary.json`; `reports/taxonomy_results_site_qa.md`; ledger event 231 |
| `_plan/taxonomy-results-site-closure` | validated | high | 2 | `reports/taxonomy_results_site_closure_note.md`; ledger event 232 |
| `_plan/final-campaign-handoff-manifest` | validated | high | 3 | `reports/final_campaign_handoff_manifest.md`; ledger events 233-234; manifest link check |
| `_run/report_cycles_33-35` | validated | high | 2 | `reports/cycles/report_cycles_33-35.md`; ledger event 227 |
| `_run/report_cycles_38-40` | validated | high | 2 | `reports/cycles/report_cycles_38-40.md`; ledger event 235 |
| `_run/report_cycles_41-43` | validated | high | 2 | `reports/cycles/report_cycles_41-43.md`; ledger event 237 |
| `_run/report_cycles_44-46` | validated | high | 2 | `reports/cycles/report_cycles_44-46.md`; ledger event 239 |
| `_run/report_cycles_47-49` | validated | high | 2 | `reports/cycles/report_cycles_47-49.md`; ledger event 240 |
| `_run/report_cycles_50-52` | validated | high | 2 | `reports/cycles/report_cycles_50-52.md`; ledger event 242 |
| `_manager/validator-warnings` | in-progress | medium | 4 | ledger events 228-230, 236, 238, 241; Stage 3 validator run |

Plan adherence conclusion: the post-baseline delta milestones that make terminal claims are supported by on-disk artifacts and ledger events. No delta artifact promotes prediction or speculation rows beyond the header-only master ledgers.

## Confidence calibration

Validated delta events with high confidence: 10 milestones.

Validated delta events with medium, low, or provisional confidence: 0 milestones.

Low-confidence terminal states: none in the delta slice. The manager warning row is intentionally non-terminal and medium-confidence; it remains a validator-watch signal rather than a scientific-status change.

## Residual debt

| Item | Status | Confidence | Residual debt |
|---|---|---|---|
| `_manager/validator-warnings` | in-progress | medium | Watch-only inherited validator warnings remain, but required validators exited 0 in Stage 3. No new blocking issue was confirmed. |
| Inherited baseline plan-ledger consistency issue | action_required in baseline context | medium | The prior baseline issue for exact active plan IDs was not reopened by the delta artifacts and is not re-reported as a new finding. |
| Report mtime drift for reports 24-32 | validated support context | high | These reports have post-baseline mtimes and were adversarially inspected. They preserve no-promotion and header-only ledger claims and do not reopen the baseline. |
| `reports/taxonomy_results_site_closure_note.md` timestamp drift | validated | high | File mtime is later than its ledger event timestamp, but the note is referenced by the ledger, content is maintenance-boundary only, adjacent site tests passed, and master ledgers stayed header-only. |
| Session transcript coverage | deferred record gap | medium | The audit index used local `sessions.db`, reports, ledger events, and on-disk artifacts. Full native transcripts for some session IDs were not fetched; this did not block verification of current delta claims. |

## Findings by severity

CRITICAL: 0

MODERATE: 0

MINOR: 0

No structured findings were appended in this final-audit run. `audits/final/findings.jsonl` was absent at document time, which is treated as zero findings rather than a missing-result defect.

## Future work

Anchored to `_manager/validator-warnings`: keep inherited validator warnings on the maintenance checklist, but do not treat them as reopening scientific closure unless a validator begins exiting nonzero or a warning points to a current delta artifact.

Anchored to inherited baseline plan-ledger consistency debt: resolve exact active plan-ID coverage in a future maintenance pass if the campaign is reopened. The delta closure did not need a reconciliation event because no new artifact contradicted the baseline state.

Anchored to session transcript coverage: if a future public audit requires provenance beyond local artifacts and ledger records, export the relevant session transcripts and add them as canonical audit artifacts.

## Reconciliation log

Reconciliation events emitted by this final auditor: 0.

No `_plan/`, `_archive/`, or correction ledger event is proposed. The delta artifacts support their ledger claims; the master `prediction_ledger.tsv` and `speculation_ledger.tsv` remain header-only; and no supersession-pending status was found in the delta closure path.

## Test record

The test pass ran:

- `python3 -m long_exposure.tools.promise_check <run-root>`
- `python3 -m long_exposure.tools.org_check <run-root>`
- `pytest -q tests/test_taxonomy_results_site_public_text.py`
- `python3 -m py_compile scripts/build_taxonomy_results_site_assets.py tests/test_taxonomy_results_site_public_text.py`

Observed results: both required validators exited 0 with inherited warnings only; taxonomy public-text tests passed (`5 passed`); Python compilation passed; `prediction_ledger.tsv` and `speculation_ledger.tsv` each had zero non-header rows.

## Figure coverage

Delta-relevant figure assets present: 10.

Ledger-referenced delta figure artifacts: 10.

Missing ledger-referenced delta figures: 0.

Milestones with figure-backed artifacts: 2 (`_plan/final-free-tier-closure-synthesis`, `_plan/taxonomy-results-site`).

Milestones warranting figures but lacking them: 0 in the delta slice. Periodic report and closure-note milestones did not require new figures.
