# Manifest

Generated for `report_cycles_50-52` on 2026-05-19.

This snapshot covers the terminal-maintenance window represented by cycles 50-52. The supplied audit records a validated no-op: no new defect, reproducibility failure, public-facing issue, or qualifying scientific evidence was supplied, so no build/run action, artifact rebuild, file edit, or ledger promotion was warranted during worker/auditor cycle work. PhytoGraph remains conservatively closed with six limitation-class track outcomes, header-only master prediction/speculation ledgers, inherited-warning posture, and the same explicit reopening conditions.

## Key Files

The following workspace files produced results cited in
final_report.md. Downstream packaging should include
these; other files are supporting or exploratory.

- `phytograph_schema.md` — Shared typed-hypergraph schema and evidence-boundary rules cited in Substrate, Schema, And Evidence Boundaries.
- `data_source_audit.md` — Source-role and provenance audit cited in the schema/source-audit summary.
- `coverage_report.md` — Coverage artifact cited in the schema/source-audit and reproducibility sections.
- `phytograph_dataset/hyperedges.parquet` — Repaired retained hyperedge substrate underlying the 641,183-hyperedge state cited in Barrier Repairs and the artifact map.
- `phytograph_dataset/nodes.parquet` — Repaired node substrate underlying the 363,237-node state cited in Barrier Repairs and the artifact map.
- `phytograph_dataset/resolved_key_propagation_audit.tsv` — Accepted-key propagation audit supporting the Barrier 1 repair cited in the final report.
- `phytograph_dataset/dedup_report.tsv` — Deduplication repair report supporting the typed-member deduplication discussion.
- `scripts/barrier1_common.py` — Barrier 1 repair helper cited in the reproducibility artifact map.
- `scripts/barrier1_merge_substrate.py` — Barrier 1 merge script cited for the repaired shared substrate.
- `scripts/barrier1_apply_synonyms.py` — Accepted-key propagation script cited in the Barrier Repairs section.
- `scripts/barrier1_deduplicate_edges.py` — Typed-member deduplication script cited in the Barrier Repairs section.
- `tools/validate_barrier1_substrate.py` — Validator cited for the 363,237-node and 641,183-hyperedge repaired substrate state.
- `tools/validate_barrier2_track_enrichment.py` — Barrier 2 conformance validator cited in enrichment readiness.
- `reports/barrier2_wave2_integration_report.md` — Wave 2 integration report cited for six-track conformance and enrichment status.
- `data/barrier2_track_enrichment_conformance.json` — Machine-readable Barrier 2 conformance result cited in the artifact map.
- `botanical_atlas_site/build_atlas.py` — Atlas builder cited for the 60,000-page integration surface.
- `botanical_atlas_site/page_contract.md` — Atlas evidence-class contract cited in Atlas integration and formal contributions.
- `reports/barrier3_atlas_instrument_readiness.md` — Barrier 3 readiness report cited for six-track Atlas integration.
- `data/barrier3_atlas_instrument_contract.tsv` — Machine-readable Atlas instrument contract cited in the artifact map.
- `tracks/track1/instruments/tci_spec.md` — Track 1 TCI definition cited in track status and formal contributions.
- `tracks/track1/instruments/build_tci.py` — Track 1 builder that produced the per-taxon TCI output cited in instrument status.
- `tracks/track1/outputs/tci_per_taxon.tsv` — Track 1 TCI table cited in the artifact map.
- `tracks/track1/data/reticulation_reopen_candidate_events.tsv` — Track 1 reopen candidate table cited for the H1 non-reopen result.
- `tracks/track1/data/reticulation_reopen_join_diagnostics.tsv` — Track 1 reopen diagnostics cited for accepted-key/event-shaped recovery limits.
- `tracks/track2/data/track2_wave4_validation_outcomes.tsv` — Track 2 validation table cited for the H2 null/data-limited result.
- `tracks/track2/reports/track2_wave4_validation_closure.md` — Track 2 closure report cited for held-out and ablation status.
- `tracks/track3/data/track3_wave4_validation_outcomes.tsv` — Track 3 validation table cited for H3 data-limited status.
- `tracks/track3/data/track3_wave4_validation_summary.json` — Track 3 validation summary cited for convergence-prior status.
- `tracks/track3/data/convergence_pressure_scores.tsv` — Track 3 score table cited for convergence-pressure priors.
- `tracks/track4/data/crop_cwr_bioclim_vectors.tsv` — Track 4 climate-vector attempt table cited for the H4 non-reopen result.
- `tracks/track4/data/crop_cwr_validation_pairs.tsv` — Track 4 held-out comparator table cited for validation-readiness limits.
- `tracks/track4/reports/track4_barrier4_closure.md` — Track 4 closure report cited for data-limited climate substitution.
- `tracks/track5/data/track5_wave4_validation_outcomes.tsv` — Track 5 validation table cited for temporal holdout limits.
- `tracks/track5/data/source_ablation_results.tsv` — Track 5 ablation table cited for no-Duke and matched-source collapse.
- `tracks/track5/reports/track5_wave4_temporal_source_closure.md` — Track 5 closure report cited for source-limited temporal validation.
- `tracks/track6/data/probe_results.tsv` — Track 6 deterministic control-result table cited for benchmark-only status.
- `tracks/track6/data/local_model_availability.json` — Track 6 local runtime check cited for environment-limited closure.
- `tracks/track6/reports/track6_barrier4_closure.md` — Track 6 closure report cited for no audited model-response rates.
- `reports/reopen/reopen_evidence_gate.md` — Post-closure reopen gate cited for H1/H4/H5/H6 reopen requirements.
- `data/reopen/reopen_branch_matrix.tsv` — Machine-readable reopen matrix cited for evidence requirements and promotion risk.
- `reports/reopen/final_free_tier_closure_synthesis.md` — Canonical six-track final free-tier closure synthesis cited in Track Status Synthesis and Conclusions.
- `data/reopen/final_free_tier_track_status.tsv` — Machine-readable final six-track status table cited in the reproducibility artifact map and public-site projection.
- `taxonomy_results_site/data/site_summary.json` — Public communication summary cited for 60,000 indexed taxa and six final track statuses.
- `reports/taxonomy_results_site_qa.md` — QA record cited for required files, link checks, language-boundary scan, screenshots, and responsive CSS correction.
- `reports/taxonomy_results_site_closure_note.md` — Communication-layer closure note cited for the site maintenance boundary.
- `reports/final_campaign_handoff_manifest.md` — Canonical handoff manifest cited for final artifact scope, closure status, and reopening conditions.
- `prediction_ledger.tsv` — Header-only master prediction ledger cited in Validation, Ablations, And Master Ledgers.
- `speculation_ledger.tsv` — Header-only master speculation ledger cited in Validation, Ablations, And Master Ledgers.

## Script Inventory

### Terminal Maintenance References

| File | Lines | Purpose |
|---|---:|---|
| `scripts/build_taxonomy_results_site_assets.py` | 428 | Builds the public taxonomy-results review site data, evidence tables, and figure assets from the final six-track status table. |
| `tests/test_taxonomy_results_site_public_text.py` | 130 | Verifies required site files, figure references, route labels, public-language boundary, six status codes, and header-only master ledgers. |

### Closure Synthesis Still Referenced

| File | Lines | Purpose |
|---|---:|---|
| `reports/reopen/scripts/build_final_free_tier_closure_synthesis.py` | 197 | Builds the final six-track free-tier status table, closure report, and summary figure consumed by the handoff and site artifacts. |
| `tests/test_final_free_tier_closure_synthesis.py` | 109 | Verifies the final six-track status table, root/reopen propagation, figure presence, and header-only master ledgers. |

## Data And Documentation Inventory

| Path | Rows / Lines | Purpose |
|---|---:|---|
| `reports/final_campaign_handoff_manifest.md` | 76 lines | Validated handoff manifest linking maintainers to canonical closure artifacts, six final statuses, Atlas records, ledgers, and reopening conditions. |
| `reports/taxonomy_results_site_closure_note.md` | 15 lines | Communication-layer closure note that limits future site work to clarity, accessibility, link repair, provenance hygiene, and reproducibility. |
| `reports/taxonomy_results_site_qa.md` | 40 lines | QA record for the public taxonomy-results site, including file/link checks, language-boundary checks, screenshots, and remaining limitations. |
| `taxonomy_results_site/data/site_summary.json` | 229 lines | Public site summary with 60,000 indexed taxa and six final track status summaries. |
| `taxonomy_results_site/data/evidence_tables/track1.json` | 15 lines | Public evidence table for Track 1 communication status. |
| `taxonomy_results_site/data/evidence_tables/track2.json` | 15 lines | Public evidence table for Track 2 communication status. |
| `taxonomy_results_site/data/evidence_tables/track3.json` | 15 lines | Public evidence table for Track 3 communication status. |
| `taxonomy_results_site/data/evidence_tables/track4.json` | 15 lines | Public evidence table for Track 4 communication status. |
| `taxonomy_results_site/data/evidence_tables/track5.json` | 15 lines | Public evidence table for Track 5 communication status. |
| `taxonomy_results_site/data/evidence_tables/track6.json` | 15 lines | Public evidence table for Track 6 communication status. |
| `taxonomy_results_site/index.html` | 253 lines | Static local public site shell. |
| `taxonomy_results_site/README.md` | 13 lines | Local serving instructions and communication boundary. |
| `taxonomy_results_site/PROVENANCE.md` | 33 lines | Public-site provenance notes. |
| `botanical_atlas_site/page_contract.md` | 89 lines | Atlas evidence-class and page-order contract used as the repaired manifest target. |
| `reports/barrier3_atlas_instrument_readiness.md` | 35 lines | Barrier 3 Atlas readiness record used as the repaired manifest target. |
| `prediction_ledger.tsv` | 0 data rows | Header-only master prediction ledger. |
| `speculation_ledger.tsv` | 0 data rows | Header-only master speculation ledger. |
| `promise_ledger.jsonl` | 241 events | Current append-only ledger count after a cycle-52 manager warning event; the supplied cycles 50-52 audit recorded 240 events before that post-audit append. |

## Cumulative Stats

| Category | Count |
|---|---:|
| Cycle-window scientific artifact changes reported by audit | 0 |
| Cycle-window maintenance defects supplied | 0 |
| Cycle-window build/run actions warranted | 0 |
| Critical audit findings | 0 |
| Moderate audit findings | 0 |
| New minor audit findings | 0 |
| `promise_check` result reported by audit | exit 0, inherited warnings only |
| `org_check` result reported by audit | exit 0, inherited warnings only |
| Public site indexed taxa | 60,000 |
| Final tracked statuses preserved | 6 |
| Master prediction-ledger data rows | 0 |
| Master speculation-ledger data rows | 0 |
| Promise-ledger events reported in cycles 50-52 audit | 240 |
| Current local promise-ledger events after reporter gather | 241 |
| Plan milestones reported by `promise_check` | 46 |
| New claims/predictions/recommendations introduced | 0 |

## Cross-References

| Origin | Consuming Artifact | Flow |
|---|---|---|
| `data/reopen/final_free_tier_track_status.tsv` | `taxonomy_results_site/data/site_summary.json` and six evidence tables | The final six-track closure statuses are projected into public communication artifacts without promoting master-ledger rows. |
| `reports/final_campaign_handoff_manifest.md` | Future maintainer/researcher turns | The manifest points to canonical closure artifacts, substrate/interface status, final track outcomes, inherited-warning posture, and reopening condition. |
| Supplied cycles 50-52 audit report | This periodic report | The audit validates the no-op terminal-maintenance posture and confirms no new actionable defect, evidence predicate, artifact rebuild, file edit, or master-ledger promotion. |
| `prediction_ledger.tsv`, `speculation_ledger.tsv` | All cycle 50-52 closure records | Both master ledgers remain header-only because no track reopening predicate was met. |
| Inherited `promise_check` / `org_check` warnings | Future maintainer turns | Warnings remain historical/nonblocking unless a future validation run reports a new error. |
