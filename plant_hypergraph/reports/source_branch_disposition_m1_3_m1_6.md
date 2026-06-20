---
created: 2026-05-18T09:10:00+00:00
cycle: 13
run_id: run-phytograph-cycle13-source-branch-disposition
agent: worker
milestone: _plan/source-branch-disposition-m1-3-m1-6
---

# Source Branch Disposition: M1.3 and M1.6

## Scope

This package closes the lifecycle question for two stale Wave 1 source branches before any new Wave 4 validation or ablation work. It does not expand ingestion, modify the frozen Barrier 1 substrate, change Wave 2 enrichment, change Wave 3 instrument algorithms, rebuild the Atlas contract, or write master prediction/speculation ledger rows.

## M1.3 Reticulation Sources

M1.3 remains a source-coverage limitation, not a Track 1 instrument or Barrier 3 defect. The staged reticulation branch contains 28 seed rows: 12 chromosome-count assertions, 6 ploidy-state assertions, 1 hybridization event, 4 polyploidization events, and 5 reticulate-inheritance evidence rows. Track 1 Wave 2 projection resolved 3 rows to accepted keys and preserved 25 rows as `pending_crosswalk`; the canonical polyploid seed set remains pending-crosswalk or absent in the frozen accepted-key namespace.

Production-scale CCDB/C-value/polyploid recovery is not available in this run because the local branch has only seed-scale probed rows and the documented bulk recovery paths remain access- or acquisition-limited. The M3.T1 TCI mechanism correctly counts only event-shaped accepted-key reticulation evidence or accepted multi-parent crop-pedigree evidence. Chromosome-count and ploidy-state rows remain structural context, and unresolved `pending_crosswalk` rows cannot increase accepted-key TCI.

Disposition: M1.3 should be closed as `deferred_terminal_data_limited`, encoded in the ledger as `deferred` with a `terminal_data_limited:` rationale. It is superseded operationally for current Wave 3 use by the Track 1 data-limited enrichment and TCI artifacts, but the original source branch can reopen only if approved bulk/source data and accepted-key recovery become available.

Downstream caveats that remain attached to M3.T1 and the Atlas:

- TCI is a data-limited accepted-key instrument, not a planet-scale reticulation atlas.
- Absence of event evidence is missing data, not evidence of single-parent inheritance.
- Canonical polyploid recovery for the original M1.3 seed set is not validated.
- Pending-crosswalk rows must remain visible and cannot be silently dropped.

## M1.6 Domestication/CWR-Climate Sources

M1.6 remains a source-coverage limitation, not a Track 4 scoring or Atlas projection defect. The Track 4 enrichment retained 6 observed domestication edges, joined 3 of 69 crop-wild-relative pairs, and joined 36 of 375 climate-envelope rows. The decisive special point is that observed bioclim vector count is 0, so climate suitability is not computable.

The M3.T4 Crop Substitution Engine therefore excludes climate from the denominator and scores only retained pedigree, joined CWR, selection-trait, and Vavilov-center evidence. Its candidate rows are `pending_data_limited` rankings, not validated crop-substitution recommendations. Unjoined CWR rows cannot support substitute claims, and climate rows without observed vectors cannot support climate-match claims.

Disposition: M1.6 should be closed as `deferred_terminal_data_limited`, encoded in the ledger as `deferred` with a `terminal_data_limited:` rationale. It is superseded operationally for current Wave 3 use by the Track 4 data-limited enrichment and Crop Substitution Engine artifacts, but the source branch can reopen only after observed bioclim extraction and accepted-key CWR expansion are available.

Downstream caveats that remain attached to M3.T4 and the Atlas:

- Crop-substitution rows are candidate rankings only, not deployment recommendations.
- `climate_match_status=not_computable_no_observed_bioclim_vectors` remains binding.
- The score is pedigree/CWR/selection/Vavilov-only until observed bioclim vectors exist.
- Held-out expert validation and climate-envelope suitability must wait for Wave 4 after this disposition is auditor-ready.

## Mechanism Table

| milestone_id | failure_signature | mechanism | special_point | downstream_artifacts | terminal_status | reopen_condition |
|---|---|---|---|---|---|---|
| M1.3 | 28 reticulation seed rows staged; 3 accepted-key resolved rows; 25 pending_crosswalk rows; canonical polyploid seed set remains pending_crosswalk or absent; no production-scale CCDB/C-value/polyploid recovery available in this run. | Reticulation source evidence contributes to TCI only when raw_source_name resolves to an accepted_taxon_key and the row is event-shaped reticulation evidence or accepted multi-parent pedigree evidence; unresolved pending_crosswalk rows are preserved but cannot increase accepted-key TCI. | At near-zero accepted-key recovery, unresolved seed rows contribute no accepted-key TCI evidence; chromosome/ploidy rows remain structural context and are not event evidence. | `tracks/track1/docs/ENRICHMENT_AUDIT.md`; `tracks/track1/reports/track1_reticulation_atlas.md`; `tracks/track1/outputs/tci_per_taxon.tsv`; `tracks/track1/outputs/pending_crosswalk_reticulation_evidence.tsv`; `tracks/track1/outputs/canonical_recovery_report.tsv`; `data/barrier3_atlas_instrument_contract.tsv` | deferred_terminal_data_limited | Reopen only if approved local/public CCDB or Plant DNA C-values bulk data plus curated polyploid/hybrid event rows are available and can be resolved through the frozen substrate accepted-key crosswalk or an audited schema/crosswalk revision. |
| M1.6 | Track 4 domestication branch retained 6 observed edges; 3 of 69 CWR pairs joined; 36 of 375 climate envelope rows joined but 0 observed bioclim vectors exist; climate suitability remains not computable. | Crop substitution climate matching requires crop_or_cwr_key to map to an observed_bioclim_vector; with observed bioclim vector count equal to zero, the climate term is undefined and excluded rather than scored as negative evidence. | At observed_bioclim_vectors = 0, Track 4 score reduces to pedigree/CWR/selection/Vavilov evidence only; unjoined CWR rows cannot support substitute recommendation claims. | `tracks/track4/track4_domestication_hypergraph.md`; `tracks/track4/data/crop_cwr_coverage_summary.tsv`; `tracks/track4/data/crop_substitution_candidates.tsv`; `tracks/track4/data/crop_substitution_data_availability.tsv`; `tracks/track4/data/crop_substitution_engine_summary.json`; `data/barrier3_atlas_instrument_contract.tsv` | deferred_terminal_data_limited | Reopen only if observed crop/CWR occurrence coordinates and bioclim vectors are generated under the existing provenance contract, and CWR expansion resolves enough accepted keys to support climate-envelope scoring. |

## Ledger Encoding

The promise ledger status vocabulary is handled conservatively: both source milestones should receive append-only `deferred` events whose narratives begin with `terminal_data_limited:`. This records terminal disposition without rewriting historical in-progress rows and without pretending that the data gaps are biological negative results.
