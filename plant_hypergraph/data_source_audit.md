<!--
created: 2026-05-17T15:50:00Z
cycle: 1
run_id: run-phytograph-cycle1
agent: worker
milestone: M0.1
-->

# Data Source Audit — PhytoGraph Wave 1

Access mode codes: **API** = public REST/GraphQL; **DUMP** = static download / snapshot; **REG** = registration / account required; **SCRAPE** = scraping needed (avoid where possible); **API+REG** = API requires registered key; **SDK** = vendor SDK with API key.

Cycle-2 ingestion priority: **must / should / optional / blocked**.

| # | Source | Access mode | License | Known bias | Bulk-scale support | Served tracks | Cycle 2 priority |
|---|---|---|---|---|---|---|---|
| 1 | World Flora Online (WFO) Plant List | API + DUMP (yearly backbone) | CC BY 4.0 | Vascular-plant focus; ferns/bryos sparser; recent splits lag | Snapshot ~ 1.5M names | substrate (all tracks) | must |
| 2 | GBIF taxonomy backbone | API + DUMP | CC0 (taxonomy) | Aggregator — inherits source bias from constituents | DwC-A nightly | substrate (all tracks) | must |
| 3 | GBIF occurrence | API (anon read) + REG for bulk | CC0 / CC BY (per record) | Strong N-America/Europe sampling skew; tropics under-represented | Async bulk download needs account | T1 (range), T2 (modern dispersal), T4 (climate), T6 (region-conditional) | should |
| 4 | GBIF media | API | per record (mixed) | Heavily image-of-charismatic-genera skewed | Per-occurrence | T6 (visual probe), Atlas | should |
| 5 | Open Tree of Life | API | CC0 (synthesis), per-source for source trees | Phylogenetic synthesis — uneven taxon coverage | OTT taxonomy + synth tree downloadable | T1 (reticulation context), T3 (homology baseline) | must |
| 6 | Plants of the World Online (POWO / Kew) | API (read), DUMP for some checklists | CC BY 3.0 (mostly) | Kew curation bias toward vascular plants of named geographic interest | Per-taxon | substrate, T4 (cultivation status) | should |
| 7 | Tropicos (MO) | API+REG (API key) | restrictive — citation required | Strong neotropical coverage; uneven elsewhere | Per-taxon | substrate (crosswalk only) | optional |
| 8 | iNaturalist research-grade | API | CC0/CC BY/CC BY-NC (mixed) | Citizen-science sampling skew; charismatic-taxon bias | DUMP of monthly export | T6 (visual probe), Atlas | optional |
| 9 | Wikidata + Wikimedia Commons | SPARQL + API | CC0 (Wikidata), per-file (Commons) | LLM-training proxy — coverage tracks notability | SPARQL endpoint | T6 (synonym confusion baseline), Atlas | should |
| 10 | CCDB (Chromosome Counts Database) | DUMP | CC BY (with citation) | Historical literature bias; uneven counts per species | Static TSV | T1 (reticulation primary) | must |
| 11 | Plant DNA C-values (Kew) | DUMP | CC BY (citation required) | Old measurements concentrate in agronomy-relevant taxa | Static download | T1 (reticulation) | must |
| 12 | Curated polyploid records (e.g. Wood et al. supplements) | DUMP (supplementary materials) | per-publication | Selection bias toward studied lineages | Per-paper supplements | T1 | must |
| 13 | PBDB (Paleobiology Database) | API + DUMP | CC BY (citation) | Vertebrate-heavy; plant fossils sparser | Bulk export available | T2 (paleo-context) | must |
| 14 | Late Quaternary Extinctions DB | DUMP | CC BY | Megafauna-focused; small-bodied dispersers under-represented | Static download | T2 | must |
| 15 | Faurby & Svenning megafauna ranges | DUMP | CC BY (citation) | Range reconstruction uncertainty; methodological prior | Raster files | T2 | must |
| 16 | IUCN Red List (fauna for extant dispersers) | API+REG (token), DUMP | CC BY-NC | Anthropocentric assessment bias | Per-taxon, account needed for bulk | T2 (extant dispersers), T6 (region-conditional) | should |
| 17 | Fruit syndrome / C4 / succulence / myrmecochory curated lists | DUMP (per-publication supplements) | per-publication | Strong publication bias by region | Mixed | T3 (primary), T2 (fruit-morphology join) | must |
| 18 | Genesys germplasm | API + DUMP | CC BY (DOI per accession) | Genebank-curation bias; landrace under-represented in some genebanks | DOI per record; full DUMP available | T4 (primary) | must |
| 19 | USDA GRIN | API + DUMP | public domain (US gov) | US-curated bias | Static download | T4 | must |
| 20 | FAO WIEWS / CWR inventories | DUMP | CC BY | FAO country-reporting bias | XLS/TSV downloads | T4 | must |
| 21 | WorldClim v2 | DUMP | CC BY-SA / CC BY (per release) | Interpolation uncertainty; high latitudes/tropics weaker | Raster downloads | T4 (climate envelope) | must |
| 22 | CHELSA | DUMP | CC BY 4.0 | Topographic downscaling assumptions | Raster downloads | T4 (climate envelope) | should |
| 23 | KNApSAcK | DUMP + page-scrape | restrictive (academic) — preserve attribution | Strongly Japanese-literature-skewed; gaps in African/SE-Asian taxa | Static page set | T5 (primary phytochemistry) | must |
| 24 | NPASS | DUMP | CC BY-NC-SA | Natural-product-screening bias toward bioactive-known taxa | Static download | T5 | must |
| 25 | Dr. Duke's Phytochemical & Ethnobotanical DB (USDA-ARS) | DUMP | public domain | Strong English-language ethnobotany skew | Static TSV | T5 (ethnobotany primary) | must |
| 26 | ChEBI | API + DUMP | CC BY 4.0 | Chemistry-ontology gaps for plant secondary metabolites | OWL/SDF | T5 (compound IDs) | must |
| 27 | Native American Ethnobotany DB (Moerman) | DUMP | restrictive — preserve indigenous attribution | English-language and US-focused | TSV | T5 (ethnobotany, sovereignty-flagged) | must (sovereignty review required) |
| 28 | PROTA (Plant Resources of Tropical Africa) | API + DUMP (partial) | CC BY-NC-SA | Africa-focused; uneven country coverage | Per-record | T5 | should |
| 29 | PROSEA (Plant Resources of South-East Asia) | DUMP (legacy) | CC BY-NC | SE-Asia focused; legacy maintenance status | Static legacy archive | T5 | should |
| 30 | Anthropic API (Claude) | SDK | API terms — usage-based billing | Model-version-specific knowledge cutoff | Rate-limited; cost per call | T6 | must |
| 31 | OpenAI API (GPT-4 class) | SDK | API terms — usage-based billing | Model-version-specific | Rate-limited; cost per call | T6 | must |
| 32 | Google Gemini API | SDK | API terms — usage-based billing | Model-version-specific | Rate-limited; cost per call | T6 | should |
| 33 | Open-source LLM (e.g. Llama-3, Qwen) | local or HF inference | Model-license-specific | Limited multimodal | Local compute or HF endpoint | T6 (comparison baseline) | optional |
| 34 | Pl@ntNet API | API+REG | restrictive (academic) | Image-based; biased to well-photographed taxa | Per-image rate-limited | T6 (image probe) | optional |
| 35 | iNaturalist plant-ID API | API | per-license | Citizen-science skew | Per-image | T6 (image probe) | optional |

**Source count: 35 entries** (well above the ≥15 floor).

## Sovereignty & attribution caveats

- Native American Ethnobotany DB (Moerman), PROTA, PROSEA: ethnobotanical records carry **indigenous data sovereignty considerations**. Every ingested record must preserve the people-group, language, and original source attribution. No anonymization. No bulk reuse without source-citation pass-through. Disagreement between an ethnobotanical record and a "scientific" record is preserved as `taxonomic_conflict` or as separate `ethnobotanical_use_assertion` and `bioactivity_assertion` edges, never reconciled.
- Tropicos: citation requirement is explicit per record; preserve `Tropicos:nameId` in `P(e)`.
- KNApSAcK: academic-only license clause — restrict re-export; document at Atlas display layer.

## Per-source reliability defaults (for `W(e)`)

| Tier | Sources | Default `source_reliability` |
|---|---|---|
| Backbone | WFO, GBIF taxonomy, Open Tree, ChEBI | 0.9 |
| Curated DB | CCDB, KNApSAcK, NPASS, Genesys, USDA GRIN, FAO WIEWS, PBDB | 0.8 |
| Publication supplements | Polyploid records, fruit-syndrome lists, megafauna range papers | 0.75 |
| Aggregator (with-bias) | iNaturalist, Wikidata, Wikimedia Commons | 0.6 |
| Citizen / scraped | Page-scrape fallbacks | 0.4 |

Reliability values are starting priors; downstream tracks may down-weight where their own validation reveals systematic bias, but must declare the change in their per-track scope doc.

## Blocked / not-this-cycle

- TRY trait database (registration + manual curation overhead) — explicitly deprioritized per directive's tooling guidance.
- Tropicos beyond crosswalk — registration / restrictive terms.
- Bulk GBIF occurrence beyond ~1M rows — requires account and storage budget; cycle 2 will sample.
