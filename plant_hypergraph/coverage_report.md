---
created: 2026-05-17T20:29:34.596349+00:00
cycle: 7
run_id: run-phytograph-cycle7-barrier1-canonical-member-repair
agent: worker
milestone: _plan/barrier1-canonical-member-repair
---

# Coverage Report — Post-Barrier-1 Merged Substrate

This report supersedes the previous staging-only `coverage_report.md`; counts below are from the deduplicated merged substrate.

## Tier Summary

| tier | count | status |
| --- | --- | --- |
| Tier 0 taxonomy-backed accepted taxa | 60000 | cleared |
| Taxonomy synonym rows (reported separately, excluded from Tier 0 accepted taxa) | 113582 | coverage_only |
| Tier 2 crop/domestication retained edges | 190 | data-limited |
| Tier 3 phytochemical retained assertions | 101484 | cleared |
| Tier 4 deep evidence retained edges | 84247 | cleared/data-limited by axis |

## Source Summary

| source_group | retained_edges | edge_types | resolved_taxon_edges | input_edges | collapsed_rows |
| --- | --- | --- | --- | --- | --- |
| chemodiversity_ethnobotany_sources | 257781 | 3 | 23524 | 259960 | 2179 |
| convergence_sources | 209297 | 3 | 27548 | 420545 | 211248 |
| domestication_sources | 190 | 3 | 6 | 190 | 0 |
| paleobotany_sources | 83 | 2 | 6 | 83 | 0 |
| reticulation_sources | 28 | 4 | 3 | 28 | 0 |
| taxonomy_backbone | 173644 | 3 | 173644 | 173644 | 0 |
| wikidata_commons | 160 | 1 | 10 | 160 | 0 |

## Edge-Type Counts

| source_group | edge_type | retained_edges |
| --- | --- | --- |
| chemodiversity_ethnobotany_sources | ethnobotanical_use_assertion | 127564 |
| chemodiversity_ethnobotany_sources | phytochemical_assertion | 101484 |
| chemodiversity_ethnobotany_sources | bioactivity_assertion | 28733 |
| convergence_sources | trait_syndrome | 84044 |
| convergence_sources | fruit_morphology | 78963 |
| convergence_sources | life_form | 46290 |
| domestication_sources | cultivation_or_domestication | 104 |
| domestication_sources | crop_pedigree | 43 |
| domestication_sources | vavilov_center_hyperedge | 43 |
| paleobotany_sources | distribution | 52 |
| paleobotany_sources | anachronism_candidate_edge | 31 |
| reticulation_sources | chromosome_count_assertion | 12 |
| reticulation_sources | reticulate_inheritance_evidence | 11 |
| reticulation_sources | polyploidization_event | 4 |
| reticulation_sources | hybridization_event | 1 |
| taxonomy_backbone | synonym_cluster | 113582 |
| taxonomy_backbone | taxonomic_parentage | 60000 |
| taxonomy_backbone | taxonomic_conflict | 62 |
| wikidata_commons | image_evidence | 160 |

## Caveats

Tracks 1 and 4 are ready only at data-limited seed scale. Track 2 can start with cited literature seed rows only. Tracks 3, 5, and 6 can start Wave 2 after Barrier 1 validation.
