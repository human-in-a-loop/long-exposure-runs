# Final Auditor Stage 2 Verify (1/1)

Run: PhytoGraph delta final audit
Stage: 2 of 4, verify pass 1 of 1
Baseline: `<run-root>/audits/final/final_audit_report.md` is the committed prior final audit and remains canonical for earlier covered work.

## Scope

This verify pass covered all post-baseline verdict-pending delta milestones listed in `audits/final/explore.md`:

- `_plan/final-free-tier-closure-synthesis`
- `_plan/taxonomy-results-site`
- `_plan/taxonomy-results-site-closure`
- `_plan/final-campaign-handoff-manifest`
- `_run/report_cycles_33-35`
- `_run/report_cycles_38-40`
- `_run/report_cycles_41-43`
- `_run/report_cycles_44-46`
- `_run/report_cycles_47-49`
- `_run/report_cycles_50-52`

The manager validator-warning rows were treated as context only because they are warning/watch events and do not assert scientific status changes.

## Verification Method

I checked existence and support for the evidence files named by the stage-1 inventory and latest ledger events. The checks included:

- `promise_ledger.jsonl` latest event range after the baseline boundary.
- `reports/reopen/final_free_tier_closure_synthesis.md`.
- `data/reopen/final_free_tier_track_status.tsv`.
- `reports/reopen/figures/final_free_tier_track_status.png`.
- `reports/taxonomy_results_site_qa.md`.
- `reports/taxonomy_results_site_closure_note.md`.
- `reports/final_campaign_handoff_manifest.md`.
- `taxonomy_results_site/` required static site files.
- `taxonomy_results_site/data/site_summary.json`.
- `prediction_ledger.tsv` and `speculation_ledger.tsv`.
- Delta periodic reports from cycles 33-35 through 50-52.

I also checked manifest Markdown links and master ledger line counts.

## Results By Milestone

### `_plan/final-free-tier-closure-synthesis`

Status verified: `validated`, confidence high.

Evidence exists and supports the claim:

- Ledger events 225 and 226 are present, validated, high confidence, and all listed artifacts exist.
- `reports/reopen/final_free_tier_closure_synthesis.md` exists.
- `data/reopen/final_free_tier_track_status.tsv` exists and contains six track rows.
- `reports/reopen/figures/final_free_tier_track_status.png` exists.
- `prediction_ledger.tsv` has exactly one line, the header.
- `speculation_ledger.tsv` has exactly one line, the header.

The six final statuses in the TSV match the closure claim:

- Track 1: `sidecar_readiness_uncontrolled`
- Track 2: `H2_remains_not_supported_or_data_limited`
- Track 3: `confound_limited`
- Track 4: `still_data_limited`
- Track 5: `H5_remains_source_biased`
- Track 6: `environment_limited_untested`

Verdict: supported. No master prediction or speculation row was promoted.

### `_plan/taxonomy-results-site`

Status verified: `validated`, confidence high.

Evidence exists and supports the claim:

- Ledger event 231 is present, validated, high confidence, and all listed artifacts exist.
- `taxonomy_results_site/index.html`, `assets/styles.css`, `assets/app.js`, `data/site_summary.json`, six evidence tables, `README.md`, and `PROVENANCE.md` exist.
- `reports/taxonomy_results_site_qa.md` reports required-file checks, local reference checks, evidence-table checks, public-language scan, screenshots, and header-only master ledgers.
- `taxonomy_results_site/data/site_summary.json` reports `substrate.taxa_indexed = 60000`.
- The site summary states that no cross-track prediction or speculation entries were promoted beyond table headers because validation predicates were not met.

I initially checked for `taxonomy_results_site/data/search_index.json`; that file is not part of the QA-defined required file set. The site's actual required data layout is `data/site_summary.json` plus `data/evidence_tables/track1.json` through `track6.json`. This was a verifier-path assumption, not a defect.

Verdict: supported. The site is a communication/expert-review layer over closure artifacts, not reopened scientific analysis.

### `_plan/taxonomy-results-site-closure`

Status verified: `validated`, confidence high.

Evidence exists and supports the claim:

- Ledger event 232 is present, validated, high confidence.
- `reports/taxonomy_results_site_closure_note.md` exists.
- The closure note states that the site does not reopen any track, alter statuses, regenerate evidence tables, or introduce biological, climate, chemistry, or model-performance claims.
- Master ledgers remain header-only.

Verdict: supported.

### `_plan/final-campaign-handoff-manifest`

Status verified: `validated`, confidence high.

Evidence exists and supports the claim:

- Ledger events 233 and 234 are present, validated, high confidence.
- `reports/final_campaign_handoff_manifest.md` exists.
- The manifest states that PhytoGraph is scientifically closed in a conservative non-promotion state and that future reopening requires a new scientific pass with qualifying evidence and audited controls.
- The manifest points to existing Atlas documentation: `botanical_atlas_site/page_contract.md` and `reports/barrier3_atlas_instrument_readiness.md`.
- Markdown link check found 15 manifest links and 0 missing local targets.
- Master ledgers remain header-only.

Verdict: supported. The documented broken-link repair is verified without changing scientific status.

### Periodic Report Milestones

Status verified: `validated`, confidence high, for:

- `_run/report_cycles_33-35`
- `_run/report_cycles_38-40`
- `_run/report_cycles_41-43`
- `_run/report_cycles_44-46`
- `_run/report_cycles_47-49`
- `_run/report_cycles_50-52`

Evidence exists and supports the claim:

- Each Markdown report exists under `reports/cycles/`.
- Each report's corresponding ledger registration event exists in the latest event range.
- The reports consistently preserve the closure/non-promotion boundary.
- Reports 38-40 through 50-52 state or support header-only master ledgers and no reopening predicate.
- The documented promise-ledger line-count drift in cycle 50-52 is explained by a later manager warning/watch event, not by scientific status change or prediction promotion.

Verdict: supported.

## Findings Appended

No findings were appended to `audits/final/findings.jsonl` in this verify stage.

Severity counts for this stage:

- CRITICAL: 0
- MODERATE: 0
- MINOR: 0

## Residual Verification Notes

- The inherited validator-warning rows remain contextual watch items for the Stage 3 adversarial test pass.
- No `ledger_causal_summary` contradictions were supplied for this stage.
- The baseline final audit's prior plan-ledger consistency issue was not reopened by the delta artifacts checked here.

## Stage Verdict

The post-baseline delta milestones in this verify slice are supported by on-disk evidence. I found no confirmed defect requiring a finding, reconciliation event, or repair during Stage 2.
