<!--
created: 2026-05-17T15:50:00Z
cycle: 1
run_id: run-phytograph-cycle1
agent: worker
milestone: M0.1
schema_version: v1.0
schema_status: FROZEN
-->

# PhytoGraph Schema — v1.0 (FROZEN)

**Version:** v1.0
**Frozen:** 2026-05-17
**Modification policy:** any change requires a new BARRIER 0 coordinator pass plus a `_plan/schema-revision-vN.M` ledger event. No source clone, track clone, or instrument clone may extend the schema unilaterally.

This schema defines the typed hypergraph substrate `H = (V, E, τ_V, τ_E, W, P, C, T)` consumed by all six PhytoGraph tracks. It carries forward the seven hyperedge families from the prior plant-taxonomy campaign (`taxonomic_parentage`, `synonym_cluster`, `trait_syndrome`, `regional_checklist_context`, `occurrence_provenance`, `reticulate_or_hybrid_signal`, `missing_rank_bridge`) and extends to ~32 typed hyperedge families covering reticulation, ghost coevolution, convergence, domestication, chemodiversity, and adversarial-probe evidence.

## 1. Formal Object

`H = (V, E, τ_V, τ_E, W, P, C, T)` where:

| Symbol | Meaning |
|---|---|
| `V` | finite set of typed nodes |
| `E` | finite set of typed hyperedges; each `e ∈ E` is a non-empty subset of `V` annotated with a role-map |
| `τ_V : V → 𝒯_V` | node-type assignment, `𝒯_V` finite (see §2) |
| `τ_E : E → 𝒯_E` | hyperedge-type assignment, `𝒯_E` finite (see §3) |
| `W : E → [0,1] × ℝ⁺` | (confidence, source-reliability) per edge |
| `P : E → Provenance` | structured provenance record (see §4) |
| `C : E → Caveat-set` | machine-readable caveats — uncertainty class, source conflict, missing data flags |
| `T : E → Temporal-annotation ∪ {⊥}` | optional temporal interval (e.g. extinction date, isolation date, hybridization date, cultivation start) |

The incidence matrix `B ∈ {0, role-weight}^{|V|×|E|}` has `B[v,e] > 0` iff `v ∈ e`. Role weights distinguish (e.g. for a `crop_pedigree`) wild-ancestor vs. cultivar vs. selection-trait vs. region nodes. Default role-weight is `1`.

## 2. Node Type Inventory (`𝒯_V`)

| Type | Domain | Layer |
|---|---|---|
| `taxon` | Managed taxon concept (WFO ID, GBIF taxon key, OTT ID) | taxonomy |
| `accepted_name` | Accepted name record under a source backbone | nomenclature |
| `synonym` | Synonym name record | nomenclature |
| `common_name` | Vernacular name with language/region tag | nomenclature |
| `rank` | Rank label (family, genus, species, infraspecific) | taxonomy/schema |
| `family` / `genus` / `species` / `infraspecific_unit` | Convenience aliases for `taxon` with `rank` constraint | taxonomy |
| `fruit_type` | Fruit-morphology code (berry, drupe, samara, capsule, achene, follicle, aril, ...) | trait |
| `life_form` | Raunkiær / growth-form code | trait |
| `trait` | Generic trait state (C3/C4/CAM, succulence, myrmecochory, ...) | trait |
| `region` | Geographic unit (country, TDWG region, ecoregion, biome) | geography |
| `native_origin_area` | Region tagged as native origin for a taxon | geography |
| `introduced_area` | Region where taxon is non-native | geography |
| `habitat` | Habitat type/biome | geography |
| `animal_consumer` | Animal disperser/consumer node | coevolution |
| `animal_pollinator` | Pollinator species/guild node | coevolution |
| `mycorrhizal_partner` | Fungal symbiont taxon | coevolution |
| `herbivore` | Herbivore taxon/guild | coevolution |
| `extinct_fauna` | Extinct animal taxon with extinction date | paleoecology |
| `human_use_category` | Category code (food, fiber, medicinal, ornamental, fuel, fodder, timber, dye, ...) | human use |
| `edibility_status` | Edibility code (edible, conditionally edible, inedible, toxic, deadly) | human use |
| `toxicity_caveat` | Preparation/part-specific toxicity caveat | human use |
| `cultivation_status` | wild / managed-wild / landrace / cultivar / modern-variety | human use |
| `wild_ancestor` | Wild progenitor taxon for a crop | domestication |
| `cultivar` | Named cultivated variety | domestication |
| `landrace` | Locally-adapted traditional variety | domestication |
| `breeder_pedigree_node` | Named cross / breeding line | domestication |
| `vavilov_center` | Vavilov / contested center of crop origin | domestication |
| `phytochemical_compound` | Named compound (InChIKey / CAS / ChEBI ID) | chemistry |
| `chemical_class` | Compound class (alkaloid subclass, terpene class, glycoside class, ...) | chemistry |
| `bioactivity_class` | Bioactivity class (anti-malarial, anti-tumor, neurotoxic, antibacterial, ...) | chemistry |
| `ethnobotanical_use_record` | Indigenous / traditional use record with people-group attribution | ethnobotany |
| `image_media` | Image / media record with license | media |
| `source` | Evidence provider (DB, paper, dataset, API) | provenance |
| `story_note` | Cultural / narrative note tied to a taxon | narrative |
| `conservation_status` | IUCN-style code | conservation |
| `phylo_node` | Node in a phylogenetic synthesis (OTT, induced subtree) | phylogeny |
| `clade_context` | Named clade (eudicots, monocots, rosids, ...) | phylogeny |
| `chromosome_count` | Reported 2n / x ploidy count | cytogenetics |
| `ploidy_state` | Inferred ploidy (diploid, tetraploid, hexaploid, mixoploid) | cytogenetics |
| `hybridization_event` | Hybridization event node with parental taxa references | reticulation |
| `polyploidization_event` | WGD / allopolyploidization event node | reticulation |
| `paleo_context` | Paleoclimate / paleoecology context window | paleoecology |
| `probe_question` | Adversarial probe question | probe |
| `probe_ground_truth` | Hypergraph-derived ground-truth answer | probe |
| `foundation_model_response` | Model response to a probe question, with confidence | probe |
| `prompt_template` | Template used to instantiate probe questions (BRIDGING type; see §5) | probe |
| `confidence_calibration_record` | Aggregate calibration record (BRIDGING type; see §5) | probe |

## 3. Hyperedge Type Inventory (`𝒯_E`) with Allowed-Evidence-Scope

Each row declares **what the edge supports** and **what it does not support**. These scopes are normative: an instrument that uses an edge for a forbidden inference is in violation of the schema, not merely making a weak claim.

### 3.1 Taxonomy / nomenclature (carry-forward)

| Edge type | Member node types | Supports | Does NOT support |
|---|---|---|---|
| `taxonomic_parentage` | child `taxon`, parent `taxon`, `rank`, `source` | hierarchy consistency; ancestor/descendant paths; missing-rank bridging | phylogenetic branch length; trait similarity; synonymy |
| `synonym_cluster` | `accepted_name`, ≥1 `synonym`, `taxon`, `source` | name normalization; reduced penalty for accepted-equivalent labels; label-noise diagnosis | evolutionary closeness; shared traits; geographic identity |
| `common_name_assertion` | `taxon`, `common_name`, `region`, `source` | linguistic / vernacular linkage with regional scope | accepted-taxon identity; biological closeness |
| `missing_rank_bridge` | lower-rank `taxon`, higher-rank `taxon`, missing `rank`, `source` | hierarchy completion when intermediate rank is absent | claim that missing rank is biologically invalid; synonymy |
| `taxonomic_conflict` | ≥2 `source`, ≥2 `taxon`/`accepted_name`, `rank` | acknowledged disagreement across backbones | resolution of which source is correct |
| `phylogenetic_or_reticulate_context` | `taxon`, `phylo_node`, `clade_context`, `source` | placement in a phylogenetic synthesis with stated source | branch lengths or rates beyond what the source publishes |

### 3.2 Morphology / ecology (carry-forward + bold)

| Edge type | Member node types | Supports | Does NOT support |
|---|---|---|---|
| `fruit_morphology` | `taxon`, `fruit_type`, `source` | morphological coding of fruit type per source | ecological dispersal syndrome; edibility |
| `life_form` | `taxon`, `life_form`, `source` | growth-form coding | distribution; ecology beyond growth form |
| `habitat_association` | `taxon`, `habitat`, `region`, `source` | habitat occupancy as recorded by source | climate niche or invasive risk |
| `native_origin` | `taxon`, `native_origin_area`, `source`, optional `T` | claim of native origin per source | current distribution; absence elsewhere |
| `distribution` | `taxon`, ≥1 `region`, `source` | recorded distribution under source's coverage | native vs introduced status; absence claims |
| `introduced_or_invasive_status` | `taxon`, `introduced_area`, status-code, `source` | introduced/naturalized/invasive flag per source/region | native-range claim; impact magnitude |

### 3.3 Coevolution (track 2 / track 3 substrate)

| Edge type | Member node types | Supports | Does NOT support |
|---|---|---|---|
| `animal_consumption_or_dispersal` | `taxon`, `animal_consumer`, `region`, `source` | observed consumption/dispersal events | obligate-disperser claim; effectiveness |
| `pollination_partnership` | `taxon` (plant), `animal_pollinator`, `region`, `source` | observed pollinator visitation/effective pollination per source | obligate-specialist claim without independent evidence |
| `mycorrhizal_partnership` | `taxon` (plant), `mycorrhizal_partner`, `source` | observed plant-fungus association | functional dependence beyond what the source measures |
| `herbivore_defense_relationship` | `taxon`, `herbivore`, `chemical_class` or `trait`, `source` | observed herbivore-defense pairing | proven causal defense without bioassay evidence |
| `anachronism_candidate_edge` | `taxon`, `fruit_type`, ≥1 `extinct_fauna`, `paleo_context`, modern-recruitment-failure `source` | hypothesis that fruit syndrome fits an extinct disperser | established anachronism status without independent paleobotany |

### 3.4 Reticulation (track 1)

| Edge type | Member node types | Supports | Does NOT support |
|---|---|---|---|
| `hybridization_event` | child `taxon`, ≥2 parent `taxon`, `source`, optional `T` | named hybridization event per source | timing beyond source's stated date; viability claims |
| `polyploidization_event` | `taxon`, `ploidy_state`, ≥1 progenitor `taxon`, `source`, optional `T` | WGD / allopolyploidization event per source | autopolyploid vs allopolyploid distinction unless source states it |
| `reticulate_inheritance_evidence` | `taxon`, ≥2 parent/source-lineage nodes, `source` | multi-parent inheritance evidence | single resolved phylogenetic placement |
| `chromosome_count_assertion` | `taxon`, `chromosome_count`, `source` | reported 2n count per source | uniform species-level ploidy; ancestral state |

### 3.5 Human use / domestication (track 4)

| Edge type | Member node types | Supports | Does NOT support |
|---|---|---|---|
| `human_use` | `taxon`, `human_use_category`, `region`, `source` | recorded human-use category | universality or current practice |
| `edibility_status` | `taxon`, `edibility_status`, `source` | edibility coding per source | safety in any preparation; quantitative dose |
| `toxicity_or_preparation_caveat` | `taxon`, plant-part, `toxicity_caveat`, `source` | part-specific or preparation-specific caveat | absolute safety after any caveat is satisfied |
| `cultivation_or_domestication` | `taxon`, `cultivation_status`, `region`, `source`, optional `T` | cultivation/domestication status per source | domestication date unless source states it |
| `crop_pedigree` | `cultivar` or modern-variety `taxon`, ≥1 `wild_ancestor` / `landrace` / `breeder_pedigree_node`, selection `trait`s, `region`, `source`, optional `T` | named multi-parent cross/pedigree per source | dating of cross unless source provides date; performance claims |
| `vavilov_center_hyperedge` | ≥1 crop `taxon`, `vavilov_center`, `region`, `source` | Vavilov-class center association per source | uncontested center status — many are contested |

### 3.6 Phytochemistry / ethnobotany (track 5)

| Edge type | Member node types | Supports | Does NOT support |
|---|---|---|---|
| `phytochemical_assertion` | `taxon`, `phytochemical_compound`, plant-part, optional concentration, `source` | "compound has been detected in this taxon by this source" | "compound is taxon-typical"; "concentration is representative"; bioactivity |
| `chemodiversity_signature` | `clade_context`, `chemical_class`, optional `habitat` / herbivore-pressure `trait`, `source` | topological/statistical clustering of compound class within clade | adaptive interpretation without independent ecological evidence |
| `bioactivity_assertion` | `phytochemical_compound`, `bioactivity_class`, assay-context, `source` | in-vitro or in-vivo activity per source | clinical efficacy; therapeutic dose; safety |
| `ethnobotanical_use_assertion` | `taxon`, people-group / `region`, `human_use_category` or `bioactivity_class`, `source` | recorded traditional use, with attribution preserved | clinical bioactivity; mechanism; universality |

### 3.7 Convergence (track 3)

| Edge type | Member node types | Supports | Does NOT support |
|---|---|---|---|
| `convergence_signature` | `trait`, ≥3 `taxon` from ≥2 distinct `clade_context`, `source` | topological clustering of a trait across distant lineages | adaptive interpretation; phylogenetic homology |
| `trait_syndrome` (carry-forward) | ≥1 `taxon`, ≥1 `trait`, optional `source` | trait-based candidate evidence and convergence stress tests | taxonomic identity; phylogenetic descent |

### 3.8 Probe (track 6)

| Edge type | Member node types | Supports | Does NOT support |
|---|---|---|---|
| `adversarial_probe_edge` | `probe_question`, `probe_ground_truth`, ≥1 `foundation_model_response`, error-class label, `prompt_template` | per-question error rate, calibration, error-class assignment | vendor inadequacy claim; model-internal mechanism |
| `probe_calibration_edge` | ≥1 `confidence_calibration_record`, model identifier, category | aggregate calibration profile per (model × category) | causal attribution of miscalibration |

### 3.9 Occurrence / provenance / source / meta (carry-forward + bridges)

| Edge type | Member node types | Supports | Does NOT support |
|---|---|---|---|
| `occurrence_provenance` | occurrence-record, `taxon`/`accepted_name`, `region`, date, `source` | label provenance; coordinate-validity diagnostics | species distribution claim without sampling adequacy |
| `regional_checklist_context` | `source`, `region`, `taxon`, optional `rank` | regional-checklist scope; conflict detection | global taxonomic truth |
| `image_evidence` | `taxon`, `image_media`, `source`, license-field | media display; weak morphology inspection | distribution; edibility; taxonomy |
| `source_assertion` | claim-node, `source` | recording a claim under a named source | adjudication across sources |
| `story_or_cultural_note` | `taxon`, `story_note`, `source` | cultural / narrative context | biological fact |
| `metadata_missingness` | `taxon`, field-name | declared-missing marker | inferential filling |
| `paleoclimate_overlap_edge` (bridging) | `taxon`, `paleo_context`, `region`, `source` | paleobotanical overlap of taxon and a paleo window | extinction causality |

**Total enumerated edge types: 32.** This exceeds the sufficiency threshold of ≥25 with evidence-scope declarations.

## 4. Provenance Record (uniform across clones)

Every edge `e` carries `P(e) = {`
- `source_id` (canonical source identifier, e.g. `WFO:wfo-0001234567`, `GBIF:taxonKey=1234`, `KNApSAcK:C00012345`, DOI),
- `source_name` (human-readable),
- `source_version_or_release` (e.g. `WFO 2024-12 snapshot`),
- `access_date` (ISO-8601),
- `license` (SPDX identifier or string),
- `attribution` (free-text, must preserve indigenous attribution when applicable),
- `ingest_clone_id` (which Phase-2 ingestion clone produced this row),
- `confidence` ∈ [0,1],
- `source_reliability` ∈ [0,1] (per `data_source_audit.md`)
`}`. Provenance fields are immutable post-ingest; merging at Barrier 1 unions source_id sets, does not overwrite.

## 5. Bridging Types — Why They Exist

Two node types (`prompt_template`, `confidence_calibration_record`) and one edge type (`paleoclimate_overlap_edge`) are introduced beyond the directive's literal inventory:

- `prompt_template` — required so that Track 6 can attribute probe failures to template effects (see directive falsification protocol for Track 6).
- `confidence_calibration_record` — required so that Track 6 can publish per-(model × category) calibration without re-deriving from per-question rows.
- `paleoclimate_overlap_edge` — required so that Track 2's `anachronism_candidate_edge` has a typed substrate for its paleo-overlap field rather than free-text annotation.

These were judged necessary during this Phase-1 design pass and are flagged as bridging types so a future schema review can collapse them if downstream waves prove them redundant.

## 6. Canonical Deduplication Key

At Barrier 1, two edges `e₁, e₂` are duplicates iff:
```
canonical_key(e) = (
    τ_E(e),
    sorted(canonical_node_id(v) for v in e),
    role_map_signature(e)
)
```
matches, where `canonical_node_id` resolves a node to its accepted-taxon or compound-InChIKey or compound-ChEBI-ID where applicable, falling back to source-stable IDs otherwise. Provenance is unioned, never deduplicated. Confidence is recomputed as the max over duplicates' confidences; source_reliability as a length-weighted mean.

## 7. Allowed-Evidence-Scope Invariants

Three invariants the schema imposes on every downstream instrument:

- **Empty-data limit:** an edge backed by exactly one source supports exactly what that source records — never broader scope.
- **Over-replicated limit:** an edge backed by N sources supports the same statement-class as a single-source edge — replication raises confidence, never widens scope. (A taxon with 1000 `phytochemical_assertion` edges for compound X has high confidence of detection, but still does not support "X is taxon-typical concentration" without an explicit `chemodiversity_signature` edge.)
- **Cross-track join limit:** when a track reads another track's edges (read-only across Barrier 1), the evidence-scope label is preserved. Track 6 reading Track 5's `phytochemical_assertion` for probe-ground-truth construction must treat the detection scope, not infer concentration.

These invariants are enforceable at Barrier 2 by a conformance test that walks every track-clone's outputs and rejects any edge whose generated downstream claim exceeds the source-edge's declared scope.

## 8. Temporal Annotation `T`

`T(e)` is `⊥` unless the edge has a meaningful interval. When present:
- `cultivation_or_domestication`: cultivation start (often a range)
- `extinct_fauna` (when referenced from `anachronism_candidate_edge`): extinction date / Last Glacial Maximum proximity
- `phytochemical_assertion`: isolation date (critical for Track 5's temporal-freeze validation — H5 requires "would we have prioritized *Taxus* before paclitaxel?")
- `hybridization_event`, `polyploidization_event`: dated event when source provides
- `vavilov_center_hyperedge`: estimated domestication window
- `crop_pedigree`: cross date when breeder catalog supplies it

## 9. Hierarchy / Reticulation Constraints

- Strict ancestor/descendant paths are computed only over `taxonomic_parentage` edges; `phylogenetic_or_reticulate_context` is read-only for phylogeny synthesis, never converted to parentage.
- Hyperedge cardinality is preserved through the pipeline. Clique expansion is permitted as an **explicitly flagged baseline** only (carrying the prior campaign's clique-expansion warning theorem) and never as default rendering.

## 10. Schema-Freeze Declaration

This document is **schema v1.0, frozen 2026-05-17**.

Any modification — adding a node type, adding an edge type, modifying allowed-evidence-scope, modifying the canonical key, modifying provenance fields — requires:
1. a new BARRIER 0 coordinator pass,
2. a `_plan/schema-revision-vN.M` ledger event with `validated`/`high` status,
3. a re-run of all downstream barriers that depend on the affected types.

All Phase-2 source clones, Phase-3 track clones, and downstream instruments consume this schema **read-only**.
