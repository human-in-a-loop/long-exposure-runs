---
title: "PhytoGraph — cycles 38-40"
date: "2026-05-19"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# PhytoGraph — cycles 38-40

## Abstract

Cycles 38-40 preserved the already-validated PhytoGraph closure state and converted it into a maintainer-facing handoff. The reporting window did not reopen any scientific track, add evidence, promote predictions, or change the master `prediction_ledger.tsv` or `speculation_ledger.tsv`. The supplied audit report records one moderate communication defect: `reports/final_campaign_handoff_manifest.md` linked to nonexistent `../atlas_runbook.md`. The auditor repaired that link by pointing the manifest to existing Atlas documentation: `botanical_atlas_site/page_contract.md` and `reports/barrier3_atlas_instrument_readiness.md`.

After repair, the audit decision was `VALIDATED`. The manifest link check reported 15 links checked and 0 missing. The taxonomy results site public-text tests reported 5 passed, Python compilation passed, both master ledgers remained header-only, and promise/org checks exited 0 with inherited warnings only.

The scientific outcome remains the conservative six-track closure state: Track 1 `sidecar_readiness_uncontrolled`, Track 2 `H2_remains_not_supported_or_data_limited`, Track 3 `confound_limited`, Track 4 `still_data_limited`, Track 5 `H5_remains_source_biased`, and Track 6 `environment_limited_untested`.

## Introduction

PhytoGraph is a six-track plant-biology hypergraph campaign whose controlling success criterion was prediction promotion, not artifact production. A track-local candidate, benchmark, prior, or website display becomes a campaign-level result only if it satisfies the validation and promotion predicate recorded for the master ledgers.

Earlier cycle reports established the substantive scientific closure. In particular, cycles 33-35 consolidated the final free-tier closure synthesis and preserved both master ledgers as header-only files. Cycles 38-40 did not change that scientific position. Their role was communication maintenance: making sure future maintainers can find the canonical closure artifacts, understand the six final status classes, and avoid accidental reopening through website or manifest edits.

## Approach

This report consolidates completed work rather than re-auditing it. The main sources were the supplied audit report, local workspace artifacts, `promise_ledger.jsonl`, the handoff manifest, the taxonomy results site records, and prior closure reports.

The supplied cycle-session IDs were:

| Cycle | Researcher | Worker | Auditor |
|---|---|---|---|
| 38 | `67145c97-2985-4640-ac61-aedc72ec1c9b` | `278aa73c-6838-4a00-9d5d-2c8fc0a6cd64` | `ff845c86-8cf5-4299-a1b8-5672115c6521` |
| 39 | `d38d842a-0702-435c-bfb0-31d3d06a851d` | `df9be374-5a74-4f40-968d-90e0ae8dbcfa` | `90b55592-2272-4fc0-a098-8e797e72cb3b` |
| 40 | `aa6d3add-ebbb-445f-95ab-8a4cad0fc239` | `f567cadb-13fb-4bc1-8593-905213d88b25` | `217cd6e7-da66-4495-aad3-e28862ffe630` |

Full native transcripts for these sessions could not be fetched in this environment because session-search/session-fetch tools were not available. That is a record gap. The report therefore relies on the supplied audit and local artifacts.

## Findings

### Handoff Manifest

`reports/final_campaign_handoff_manifest.md` is the central artifact for this window. It states that PhytoGraph is scientifically closed in a conservative non-promotion state. It links maintainers to the canonical artifacts: `artifact_index.md`, `research_contribution_ledger.md`, `final_report.md`, `audit_report.md`, `falsification_and_ablation_report.md`, `reports/reopen/final_free_tier_closure_synthesis.md`, and `reports/taxonomy_results_site_closure_note.md`.

The manifest also records the substrate and interface boundary. `phytograph_schema.md` remains frozen at schema v1.0. `phytograph_dataset/` remains a Barrier 1 substrate for query and provenance review, not a source of new biological claims by itself. `botanical_atlas_site/` and the taxonomy results site remain communication and expert-review surfaces over the closed campaign.

The manifest’s final track table preserves the six limitation classes without changing their scientific meaning:

| Track | Final limitation class | Handoff meaning |
|---|---|---|
| Track 1 Reticulation Atlas | `sidecar_readiness_uncontrolled` | Sidecar evidence exists, but accepted-key reconciliation and source-density controls block promotion. |
| Track 2 Ghost Hyperedges | `H2_remains_not_supported_or_data_limited` | Canonical held-out recovery is 0/8 under the validation contract. |
| Track 3 Convergence Pressure | `confound_limited` | Trait evidence does not clear family-size and sampling-density controls. |
| Track 4 Domestication Hypergraph | `still_data_limited` | Numeric BIOCLIM vectors and validation-allowed comparators are absent. |
| Track 5 Chemodiversity Predictor | `H5_remains_source_biased` | Non-Duke temporal evidence is insufficient for a validation-ready stratum. |
| Track 6 Foundation Model Probe | `environment_limited_untested` | No qualifying local/open model responses were executed or scored. |

### Auditor Link Repair

The supplied audit report records one moderate defect and its repair. The manifest originally referenced nonexistent `../atlas_runbook.md`. The auditor replaced that target with two existing Atlas artifacts:

- `botanical_atlas_site/page_contract.md`
- `reports/barrier3_atlas_instrument_readiness.md`

This was a documentation repair, not a scientific edit. The audit states that no track conclusions, evidence tables, schema, master ledgers, predictions, recommendations, crop/climate claims, bioactivity claims, or model-performance claims were changed.

After repair, the manifest link check reported 15 checked links and 0 missing links.

### Taxonomy Results Site

The taxonomy results site remains a public communication and expert-review layer over the closed campaign. `reports/taxonomy_results_site_closure_note.md` states that future maintenance is limited to clarity, accessibility, broken-link repair, provenance hygiene, and reproducibility. It explicitly says the site is not a path back into prediction ledgers or track claims.

`reports/taxonomy_results_site_qa.md` records the site checks: required files existed, required figure assets existed, local references passed, public-facing language was scanned, and desktop/mobile screenshots were inspected. The QA note also records a limitation: the browser check used screenshots and route rendering checks, not a full assistive-technology audit.

`taxonomy_results_site/data/site_summary.json` reports 60,000 indexed taxa and the same six final track statuses. Its public summaries keep the non-promotion boundary visible: Track 1 has sidecar evidence only, Track 2 has no held-out case passing validation, Track 3 remains confound-limited, Track 4 lacks numeric climate summaries and comparators, Track 5 is source-biased, and Track 6 lacks audited local/open response rows.

### Validation Outcome

The supplied audit decision for cycles 38-40 is `VALIDATED`.

The recorded validation results were:

| Check | Result |
|---|---|
| Manifest link check | 15 links checked, 0 missing |
| `pytest -q tests/test_taxonomy_results_site_public_text.py` | 5 passed |
| `python3 -m py_compile scripts/build_taxonomy_results_site_assets.py tests/test_taxonomy_results_site_public_text.py` | passed |
| `prediction_ledger.tsv` | 1 line, header-only |
| `speculation_ledger.tsv` | 1 line, header-only |
| `promise_ledger.jsonl` | 234 events after auditor repair event |
| `promise_check` | exit 0, inherited warnings only |
| `org_check` | exit 0, inherited root-layout warnings only |

The audit rationale is that the handoff manifest correctly preserves the conservative campaign outcome: no per-track master prediction promotion, six limitation-class closures, validated website communication status, inherited warnings, and explicit reopening conditions.

## Discussion

Cycles 38-40 are best understood as closure preservation. They did not produce a new discovery, a new benchmark result, a new validation table, or a new biological claim. Their contribution was to make the existing closure state easier to maintain without changing it.

That distinction matters because PhytoGraph’s artifacts include a large substrate, an Atlas, a public-facing taxonomy results site, and many track-local outputs. Without a final handoff manifest, a future maintainer could mistake communication artifacts for a reopened scientific pass. The repaired manifest now points to the correct Atlas records and states the maintenance boundary directly.

The master-ledger state remains the controlling signal. `prediction_ledger.tsv` and `speculation_ledger.tsv` each contain only a header row. This means no campaign-level prediction or speculation was promoted during this reporting window.

## Open Questions

The open questions are maintenance and reopening conditions, not new research tasks:

- Can future maintainers preserve the handoff manifest as a pointer to canonical artifacts without editing scientific conclusions?
- Can website maintenance remain limited to clarity, accessibility, link repair, provenance hygiene, and reproducibility?
- If a future scientific pass occurs, will it satisfy the recorded reopening predicates before changing track conclusions or master ledgers?
- Can inherited validator/root-layout warnings remain documented as nonblocking unless a new validation run reports a new error?

## References

No external bibliographic references are cited for cycles 38-40. This report cites only local project artifacts and the supplied audit record.

## Appendix: Implementation Details

### Source Inventory

| Source | Date / cycle | Contents | Timeline role |
|---|---|---|---|
| Supplied audit report | Cycles 38-40 | Auditor validation summary, repaired link, validation commands, ledger counts, and guidance | Primary validation source |
| Cycle 38 sessions | Cycle 38 | Session IDs supplied; full transcripts unavailable locally | Source gap |
| Cycle 39 sessions | Cycle 39 | Session IDs supplied; full transcripts unavailable locally | Source gap |
| Cycle 40 sessions | Cycle 40 | Session IDs supplied; full transcripts unavailable locally | Source gap |
| `reports/final_campaign_handoff_manifest.md` | Final handoff | Canonical handoff manifest with artifacts, track statuses, interface status, warning posture, and reopening condition | Main cycle-window artifact |
| `reports/taxonomy_results_site_closure_note.md` | Closure communication | Site maintenance boundary and non-promotion statement | Communication boundary source |
| `reports/taxonomy_results_site_qa.md` | Site QA | File/link checks, language-boundary check, screenshot review, limitations | Site validation context |
| `taxonomy_results_site/data/site_summary.json` | Site data | 60,000 indexed taxa and six public track summaries | Public status source |
| `botanical_atlas_site/page_contract.md` | Atlas contract | Evidence-class and page-order contract | Repaired manifest target |
| `reports/barrier3_atlas_instrument_readiness.md` | Barrier 3 | Atlas instrument readiness and track queryability | Repaired manifest target |
| `promise_ledger.jsonl` | Append-only ledger | 234 events after auditor repair event | Ledger-state source |
| `prediction_ledger.tsv` and `speculation_ledger.tsv` | Master ledgers | Header-only ledgers | Non-promotion boundary |

### Code Organization

| File | Lines | Purpose |
|---|---:|---|
| `scripts/build_taxonomy_results_site_assets.py` | 428 | Builds public taxonomy-results site data, evidence tables, and figure assets. |
| `tests/test_taxonomy_results_site_public_text.py` | 130 | Verifies required site files, public routes, figure references, public-language boundary, final status codes, and header-only master ledgers. |
| `reports/reopen/scripts/build_final_free_tier_closure_synthesis.py` | 197 | Builds the final six-track status table and closure synthesis consumed by the handoff/site layer. |

### File Counts

| File or directory | Count |
|---|---:|
| `reports/final_campaign_handoff_manifest.md` | 76 lines |
| `reports/taxonomy_results_site_closure_note.md` | 15 lines |
| `reports/taxonomy_results_site_qa.md` | 40 lines |
| `taxonomy_results_site/index.html` | 253 lines |
| `taxonomy_results_site/data/site_summary.json` | 229 lines |
| Six `taxonomy_results_site/data/evidence_tables/track*.json` files | 15 lines each |
| `botanical_atlas_site/page_contract.md` | 89 lines |
| `reports/barrier3_atlas_instrument_readiness.md` | 35 lines |
| `prediction_ledger.tsv` | 1 line |
| `speculation_ledger.tsv` | 1 line |
| `promise_ledger.jsonl` | 234 events |

### Test Results

The reporter did not rerun tests. The supplied audit reports these validation results:

- Manifest link check: 15 links checked, 0 missing.
- `pytest -q tests/test_taxonomy_results_site_public_text.py`: 5 passed.
- `python3 -m py_compile scripts/build_taxonomy_results_site_assets.py tests/test_taxonomy_results_site_public_text.py`: passed.
- `prediction_ledger.tsv`: 1 line.
- `speculation_ledger.tsv`: 1 line.
- `promise_check`: exit 0, inherited warnings only.
- `org_check`: exit 0, inherited root-layout warnings only.

### Cross-Reference Map

| Origin | Consumer | Flow |
|---|---|---|
| `data/reopen/final_free_tier_track_status.tsv` | Taxonomy results site data and handoff manifest | Supplies the six final track statuses and claim boundaries. |
| `reports/final_campaign_handoff_manifest.md` | Future maintainer turns | Provides canonical artifact map, status table, warning posture, and reopening condition. |
| Broken `../atlas_runbook.md` link | `botanical_atlas_site/page_contract.md` and `reports/barrier3_atlas_instrument_readiness.md` | Auditor replaced a nonexistent link with existing Atlas documentation. |
| `reports/taxonomy_results_site_closure_note.md` | Future website maintenance | Defines allowed communication-only maintenance scope. |
| Master ledgers | All closure records | Header-only state confirms no prediction/speculation promotion. |
| `MANIFEST.md` | Future researcher/worker turns | Updated as a concise snapshot for cycles 38-40 while preserving the existing `## Key Files` section verbatim. |

### Record Gaps

Full native transcripts for the supplied researcher, worker, and auditor session IDs were not available because session-search/session-fetch tools were not available in this environment. This report therefore uses local artifacts, ledger records, and the supplied audit report.

No new cycle-window scientific artifact was found or reported. The supplied audit explicitly states that no new claims, predictions, recommendations, crop/climate claims, bioactivity claims, or model-performance claims were introduced.

### Coherence Review

One coherence pass was completed. The report defines the master-ledger boundary before using it, distinguishes communication maintenance from scientific reopening, identifies the repaired link and its replacement targets, and marks unavailable session transcripts as a record gap.
