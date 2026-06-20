---
created: 2026-05-17T18:30:00Z
cycle: 2
run_id: run-phytograph-cycle2-fanout-e34b5b2c1c6c-clone0
agent: worker
milestone: M1.1
---

# M1.1 Barrier 1 Handoff

## Consumption Contract

M1.1 exposes an operational accepted-key set for Barrier 1. The stable internal key is `accepted_taxon_key`, formatted as `wfo:<wfo_id>`, and it is anchored to accepted WFO angiosperm taxa. This key is a join contract, not a biological claim that WFO is correct over GBIF, Open Tree, or POWO.

Barrier 1 consumers should join sibling source tables to `accepted_taxa.parquet` through `accepted_taxon_key` when already resolved, or through `wfo_id` / normalized accepted-name evidence when resolving source-local records. Do not use `gbif_taxon_key`, `ott_id`, or `powo_id` as required primary keys, because this clone sampled those sources for crosswalk evidence rather than building full-source coverage.

## Required Tables

| table | required use | stable join fields | notes |
|---|---|---|---|
| `accepted_taxa.parquet` | Tier 0 accepted-key universe | `accepted_taxon_key`, `wfo_id` | 60,000 WFO-anchored angiosperm accepted taxa; includes rank, family, genus, species, and provenance. |
| `source_crosswalk.parquet` | Source-local ID evidence map | `accepted_taxon_key`, `wfo_id`, `gbif_taxon_key`, `ott_id`, `powo_id` | One row per accepted key; external IDs may be empty strings and must remain null-preserving coverage gaps. |
| `synonym_clusters.parquet` | Name normalization / leakage control | `accepted_taxon_key`, synonym source fields | Synonyms are `name_normalization_only`; they do not support trait, range, phylogeny, reticulation, edibility, or novelty claims. |
| `taxonomic_conflicts.parquet` | Auditable disagreement candidates | `accepted_taxon_key`, source-local IDs, `disagreement_category` | These rows are evidence for review, not resolved consensus taxonomy. |
| `common_names.parquet` | Common-name staging placeholder | `accepted_taxon_key` | Intentionally empty in M1.1; no no-auth bulk common-name source was accepted for this branch. |

## Null And Coverage Semantics

Missing `gbif_taxon_key`, `ott_id`, or `powo_id` values mean "not matched in this sampled no-auth crosswalk run." They do not mean the taxon is absent from GBIF, Open Tree, or POWO, and they must not be used as negative biological evidence. The `disagreement_category` field distinguishes `wfo_only_not_attempted`, `matched_name_rank_agreement`, and `accepted_name_disagreement`; downstream filters must keep these categories visible when estimating source-density bias.

## Conflict Handling

Barrier 1 should preserve WFO accepted keys and carry source-local disagreements forward as caveated evidence. If a sibling source has a stronger source-local identifier, it should write that evidence into its own staging namespace and resolve against `accepted_taxon_key` at the barrier, not overwrite M1.1 accepted rows. Multiple accepted candidates, homonyms, synonym-only matches, and sampled API disagreements should be routed to conflict review rather than collapsed into accepted truth.

## Scope Limits

The accepted-key set is restricted to WFO descendants of the WFO `Angiosperms` node. GBIF, Open Tree, and POWO coverage in this branch is sampled API evidence for crosswalk sanity, not full four-source reconciliation. The correct downstream mental model is `join(WFO operational key, source-local evidence)`, with missing external IDs retained and source disagreements preserved.
