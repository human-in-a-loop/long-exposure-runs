---
created: 2026-05-17T17:08:09+00:00
cycle: 2
run_id: run-phytograph-cycle2-fanout-e34b5b2c1c6c-clone3
agent: worker
milestone: M1.5
---

# M1.5 Convergence Specialty Source Ingest Audit

## Scope

This branch staged structural Track 3 source assertions only: fruit morphology, life form, and generic trait membership from source-stated AusTraits 6.0.0 rows. It did not compute convergence pressure, infer independent origins, expand genus-level claims to species, or write to the unified substrate.

## Source Registry

| Source | Access | License | Staged rows | Reuse status | Bias / limitation |
|---|---|---|---:|---|---|
| AusTraits 6.0.0, DOI `10.5281/zenodo.11188867` | Zenodo dump | CC-BY-4.0 | 420545 | Redistributable with attribution | Australian flora; harmonized from many primary sources; trait coverage uneven |
| C4 / succulence / myrmecochory / elaiosome / samara publication candidates | mixed supplements and reviews | per-publication | 0 | Not staged here | Candidate-specific access, scale, and row-provenance blockers recorded in `data/rejected_records.tsv` |

## Staged Schema Mapping

| Source trait | Staged edge type | Node type | Evidence scope |
|---|---|---|---|
| `plant_growth_form`, `woodiness`, `plant_succulence` | `life_form` | `life_form` | Source-stated growth form only |
| `fruit_type`, `fruit_dehiscence`, `fruit_fleshiness`, `diaspore_fleshiness` | `fruit_morphology` | `fruit_type` | Source-stated fruit/diaspore morphology only |
| `life_history`, `dispersal_syndrome`, `dispersers`, `dispersal_appendage`, `seed_shape`, `photosynthetic_pathway` | `trait_syndrome` | `trait` | Source-stated trait membership only |
| explicit source-enumerated convergent sets | `convergence_signature` | `trait` + taxa + clade context | None staged; no source in this branch met the explicit-enumeration requirement |

## Per-List Row Counts

| Trait list | Staged assertion rows | species-level source names | genus-level source names | infraspecific source names | unresolved source names | Scale status |
|---|---:|---:|---:|---:|---:|---|
| plant_growth_form | 123510 | 95671 | 1073 | 12369 | 232 | meets >=500 |
| life_history | 89164 | 75160 | 135 | 10005 | 176 | meets >=500 |
| fruit_type | 57356 | 53211 | 39 | 3698 | 96 | meets >=500 |
| fruit_dehiscence | 42367 | 39851 | 34 | 1756 | 60 | meets >=500 |
| fruit_fleshiness | 32578 | 31909 | 36 | 621 | 9 | meets >=500 |
| dispersal_syndrome | 19206 | 14711 | 1071 | 1509 | 49 | meets >=500 |
| dispersers | 16283 | 11564 | 920 | 1123 | 45 | meets >=500 |
| photosynthetic_pathway | 15003 | 12616 | 743 | 1574 | 54 | meets >=500 |
| seed_shape | 13341 | 9709 | 5 | 1150 | 14 | meets >=500 |
| diaspore_fleshiness | 4126 | 4109 | 1 | 16 | 0 | meets >=500 |
| woodiness | 4102 | 4040 | 18 | 43 | 1 | meets >=500 |
| dispersal_appendage | 3425 | 3295 | 22 | 98 | 2 | meets >=500 |
| plant_succulence | 84 | 66 | 8 | 8 | 2 | data-limited |

At least five lists clear the >=500-row threshold. The largest staged lists are plant growth form, life history, fruit type, fruit dehiscence, fruit fleshiness, dispersal syndrome, photosynthetic pathway, dispersers, seed shape, woodiness, and dispersal appendage.

## Direct Claims vs Normalization Artifacts

Direct source claims are the AusTraits row-level tuple `(taxon_name, trait_name, value, dataset_id, observation_id, source_id)`. Normalization artifacts added by this branch are stable PhytoGraph node IDs, edge IDs, role-map JSON, evidence-scope fields, and splitting whitespace-separated multi-state categorical values into separate trait-membership assertions; the original `value` token is preserved in every edge row.

## Rejected / Quarantined Records

`data/rejected_records.tsv` contains 23 rejected or quarantined candidates. The negative checks include forbidden source-implied expansions, secondary web summaries, genus-to-species expansion attempts, image-derived trait calls, C4/succulence convergence-signature attempts, TRY registration/license blockage, and publication candidates not staged because row-level redistributable supplements were not retrieved in this branch.

## License / Reuse Limits

AusTraits is CC-BY and requires citation of the resource paper and, where possible, original data sources. This branch preserves AusTraits attribution, DOI, version, access date, and source ID on every edge; downstream display should preserve the same attribution chain.

## Taxonomy Dependency

All taxon names are staged as `unresolved_taxon_name` nodes with `pending_crosswalk=true`. No spelling corrections, synonym resolution, accepted-name substitution, or species expansion was performed; Barrier 1 / M1.1 owns that crosswalk.

## Validation Commands

```bash
python3 substrate/staging/convergence_sources/scripts/ingest_convergence_sources.py
python3 -m pytest substrate/staging/convergence_sources/tests/test_convergence_sources_schema.py
python3 -m long_exposure.tools.promise_check
```

## Handoff Notes for Barrier 1

Barrier 1 should join `data/staged_edges.tsv` against the M1.1 taxonomic crosswalk using the unresolved source `taxon_name`, retain source-level taxon-rank fields for diagnostics, and deduplicate with the campaign canonical key after accepted taxon IDs exist. `trait_syndrome` rows must not be promoted to `convergence_signature` until Wave 2 estimates independent origins with phylogenetic context.
