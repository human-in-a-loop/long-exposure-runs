---
created: 2026-05-17T00:45:40Z
cycle: 1
run_id: run-2026-05-17T004540Z
agent: worker
milestone: M1
---

# Data Feasibility Map

Access date for all source checks: 2026-05-17. This cycle used official documentation and tiny API smoke tests only; no scraping, bulk downloads, authenticated downloads, or trait-data requests were performed.

## Summary Recommendation

Cycle 2 should use a small public-data-backed name/taxonomy layer from WFO plus GBIF and Open Tree cross-checks, then keep traits, reticulation, and missing-rank stressors explicitly synthetic until trait and hybrid evidence are sourced under reproducible terms. The no-auth path is viable for name matching, accepted-name lookup, synonym/status checks, GBIF occurrence samples, and Open Tree TNRS/phylogeny-context probes. It is not yet viable for reproducible trait matrices from TRY, and BIEN should be optional until an R environment and query-size policy are fixed.

## Source Feasibility Table

| Source | Evidence layer | Endpoint or route | Auth | License/citation note | Limits and risks | Supports now | Does not support | Prototype recommendation |
|---|---|---|---|---|---|---|---|---|
| WFO Plant List API | taxonomy, nomenclature | `https://list.worldfloraonline.org/matching_rest.php`; GraphQL at `https://list.worldfloraonline.org/gql.php` | No auth documented for ordinary REST/GraphQL reads | Plant List downloads are citable Zenodo datasets; latest checked static release was December 2025, version `2025-12`, DOI `10.5281/zenodo.18007552`, CC0 [4]. | API docs warn not to scrape because downloads are available [3]. Snapshot releases occur every six months [1]. | Accepted names, WFO IDs, synonym/name status, placement paths, current and historical classifications. | Occurrence records, traits, phylogenetic evidence, biological claims about hybrid origins. | Primary canonical taxonomy and synonym layer for cycle 2. |
| GBIF | taxonomy, nomenclature, occurrence evidence | `https://api.gbif.org/v1/species/match`; `https://api.gbif.org/v1/occurrence/search` | Most API use does not require auth; POST/PUT/DELETE and some GETs do [6]. Async occurrence downloads require GBIF account/basic auth [9]. | Occurrences carry standardized licenses: CC0, CC BY, or CC BY-NC [11]. Species pages cite GBIF Backbone Taxonomy DOI `10.15468/39omei` [10]. Search-API occurrence results do not create a DOI; downloads or derived datasets are preferred for citeable occurrence data [10]. | Rate limiting can occur; large occurrence retrieval should use download API [6]. Occurrence data accuracy is not guaranteed [11]. | Taxon matching, accepted taxon keys, small occurrence samples, dataset/license metadata in response fields. | A stable DOI-backed occurrence dataset unless a download or derived dataset is created. | Secondary taxonomy cross-check and tiny occurrence/noise examples only. |
| Open Tree of Life | phylogeny/taxonomy synthesis, name resolution | `https://api.opentreeoflife.org/v3/tnrs/match_names`; other v3 APIs linked by Open Tree [12,13] | Public reads via v3 API; no auth observed for TNRS smoke test. | Open Tree data are CC0 where not limited by source terms [14]. Cite the synthetic tree and taxonomy papers for phylogeny/taxonomy synthesis [15]. | Treat as synthesis evidence, not a plant nomenclatural authority. TNRS may return taxonomy-version metadata and source taxonomy links. | OTT IDs, name resolution, plant context inference, source-taxonomy pointers, induced subtree candidates. | WFO-style accepted/synonym authority or trait/occurrence evidence. | Use for phylogeny-context comparison and reticulation/tree-limit diagnostics, not as the canonical taxonomy. |
| BIEN / RBIEN | traits, ranges, occurrences, phylogenies, plant lists | R package `BIEN`, current BIEN site reports database version 4.2 [16]; package manual version 1.2.7 [17]. | No account blocker identified in docs; requires local R package setup and package-mediated queries. | Package has MIT software license [17]. Data citation should use BIEN metadata/citation functions for downloaded data [17]. | Not smoke-tested this cycle because Python-first no-auth API path was sufficient; query volume and R setup need separate validation. | Potential source for traits, ranges, occurrence records, phylogenies, plant lists. | Immediate Python-only reproducible data layer without R setup. | Optional for later trait layer; do not block cycle 2. |
| TRY Plant Trait Database | traits | Website request workflow; rtry supports processing released TRY data [18]. | Practical access requires free registration/request workflow; public-data-only requests may still take one or two working days [19,20]. | Public trait data are CC BY in IP guidelines; products must cite TRY and underlying dataset sources [19]. Free-access policy says registration is required and downloaded data cannot be redistributed [20]. | Redistribution and request/turnaround constraints make it unsuitable for a tiny fully reproducible benchmark artifact unless a permitted public release is already available. | Authoritative plant trait evidence if access and terms are satisfied. | No-auth, immediately redistributable trait matrix for this campaign. | Treat as data-limited; use synthetic trait syndromes in cycle 2. |
| Hypergraph spectral learning | method | Zhou et al. NeurIPS paper [21] | N/A | Cite paper. | Establishes a modeling method, not plant-specific evidence. | Incidence-matrix/hypergraph Laplacian baseline candidate. | Biological validity of any edge family. | Use as formal basis for simple hypergraph propagation if needed. |
| Higher-order learning critique | method/falsification | Agarwal et al. ICML paper [22] | N/A | Cite paper. | Argues some hypergraph formulations reduce to graph problems; important negative-control framing. | Fair graph-baseline warning and clique-expansion skepticism. | Plant evidence or taxonomy-specific metric. | Include as a falsification anchor. |
| Hierarchical classification survey | method/metric | Silla and Freitas survey [23] | N/A | Cite paper. | Broad ML survey, not biodiversity-specific. | Baseline taxonomy for flat/local/global hierarchical classifiers and evaluation framing. | Synonym-aware plant-name normalization. | Use to define baseline families and hierarchy-aware errors. |
| Biodiversity knowledge graph | data integration | Ozymandias [24] | N/A | Cite paper. | Ordinary graph/KG framing rather than native hypergraph. | Entity separation: taxa, names, publications, specimens, identifiers. | Proof that hypergraphs outperform graphs. | Use to avoid conflating taxon/name/source entities. |
| OpenBiodiv | data integration | OpenBiodiv paper [25] | N/A | Cite paper. | Literature-extracted biodiversity linked data, not direct plant backbone. | Biodiversity KG precedent and semantic publishing constraints. | No direct no-auth plant benchmark source. | Method context only. |
| TRY enhanced coverage paper | trait database | Kattge et al. 2020 [26] | N/A | Cite paper and TRY data sources when used. | Access terms remain decisive for reproducibility. | Trait-database motivation and citation anchor. | Does not remove request/redistribution constraints. | Use only for feasibility discussion this cycle. |

## Access Notes

WFO is the cleanest first taxonomy/nomenclature source because it distinguishes names from taxon concepts and provides stable WFO IDs. This distinction is directly relevant to the schema: a `name_string` or WFO name node is not the same object as an accepted taxon concept.

GBIF is useful but should be treated as an aggregator and occurrence infrastructure. Small API samples can diagnose label noise, geography, and accepted taxon keys; they should not be used for broad distribution claims without a DOI-backed download or derived dataset.

Open Tree should be kept in a separate phylogeny/synthesis layer. Matching a plant name to an OTT ID can support comparison to a phylogenetic/taxonomic synthesis, but it must not overwrite WFO nomenclatural status.

BIEN and TRY are trait candidates, but neither should be on the critical path for Cycle 2. The first benchmark should use synthetic trait syndromes with source labels that make the synthetic status explicit.

## Null and Data-Limited Findings

TRY is not a no-auth, immediately redistributable trait source for this campaign. Its public policy still involves registration/request workflow and citation/redistribution requirements, so it is unsuitable for the first reproducible benchmark artifact unless a separately licensed sample is provided.

BIEN was not locally smoke-tested in this cycle because the required deliverable is Python-first and the no-auth public-source probe only targets WFO, GBIF, and Open Tree. This is a deliberate null result: BIEN remains promising, but not necessary for establishing the Cycle 1 schema.

No official public source checked this cycle provides authoritative reticulation/hybrid labels for a small plant benchmark without additional taxonomic/phylogenetic curation. Reticulation should therefore remain synthetic in Cycle 2.

## Minimal Data Path for Cycle 2

1. Pull 10-30 named plant examples through WFO matching REST and GraphQL, recording WFO IDs, accepted/current placement, synonym status, and snapshot/version metadata.
2. Cross-check the same names through GBIF species matching and a very small occurrence-search sample, recording accepted taxon keys, country, dataset key, and license.
3. Resolve the same names through Open Tree TNRS in the `Land plants` or `Flowering plants` context, recording OTT IDs and whether matches are synonyms.
4. Generate synthetic trait, missing-rank, noisy-label, and reticulate cases with explicit provenance flags so no unsupported biological claim is made.
5. Freeze all fetched JSON and generated synthetic data, then compute hashes before benchmark experiments.
