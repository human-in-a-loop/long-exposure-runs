---
created: 2026-05-17T00:45:40Z
cycle: 1
run_id: run-2026-05-17T004540Z
agent: worker
milestone: M2
---

# Hypergraph Schema

This schema separates taxonomy, nomenclature, phylogeny, trait similarity, occurrence evidence, and dataset labels. The goal is not to assert new plant biology; it is to define information budgets for fair benchmark construction.

## Objects

Let `H = (V, E, X, W)` be a typed weighted hypergraph. `V` is the set of typed nodes, `E` is the set of typed hyperedges, `X` is an optional node/edge feature table, and `W` stores edge weights and provenance confidence.

The incidence matrix `B` has one row per node and one column per hyperedge. `B[v,e] = role_weight(v,e)` if node `v` participates in hyperedge `e`; otherwise `0`. Role weights may distinguish accepted taxon, synonym name, evidence source, parent lineage, child lineage, region, or dataset label, but the default unweighted incidence is `1`.

## Node Types

| Node type | Meaning | Examples | Layer |
|---|---|---|---|
| `taxon` | Managed taxon concept in a source classification | WFO taxon concept, GBIF accepted taxon key | taxonomy |
| `name_string` | Botanical name string or name record, not necessarily accepted | WFO name ID, verbatim specimen label | nomenclature |
| `rank` | Rank label or rank interval | family, genus, species, unresolved | taxonomy/schema |
| `trait` | Synthetic or sourced trait state | leaf type, growth form, habitat syndrome | trait similarity |
| `region` | Geographic unit or checklist scope | country code, ecoregion, regional checklist | geography/checklist |
| `occurrence_record` | Individual occurrence API record or frozen observation row | GBIF occurrence key | occurrence evidence |
| `source` | Evidence provider, dataset, checklist, API, publication | WFO snapshot, GBIF dataset key, Open Tree release | provenance |
| `specimen_or_observation` | Physical specimen or observation entity if distinct from occurrence row | herbarium specimen, iNaturalist observation | occurrence evidence |
| `phylogeny_node` | Node in a phylogenetic or synthetic tree/network source | OTT node, induced subtree internal node | phylogeny |
| `dataset_label` | Label available in a benchmark dataset | training label, held-out target, noisy label | dataset label hierarchy |

## Hyperedge Families

| Hyperedge family | Nodes included | Weight convention | Allowed inference | Forbidden inference |
|---|---|---|---|---|
| `taxonomic_parentage` | child `taxon`, parent `taxon`, `rank`, `source` | high for accepted backbone; lower for disputed/imported source | Hierarchy consistency, ancestor/descendant path, missing-rank bridge candidate. | Phylogenetic branch length, trait similarity, synonymy. |
| `synonym_cluster` | accepted `taxon`, accepted `name_string`, synonym `name_string` nodes, `source` | high when from WFO/GBIF accepted mapping; source-specific | Name normalization, reduced penalty for accepted taxon equivalence, label-noise diagnosis. | Evolutionary closeness, shared traits, geographic plausibility. |
| `trait_syndrome` | one or more `taxon` or `dataset_label` nodes, `trait` nodes, optional `source` | confidence or synthetic generation probability | Trait-based candidate evidence and convergence stress tests. | Taxonomic identity, accepted-name status, phylogenetic descent. |
| `regional_checklist_context` | `source`, `region`, accepted `taxon`, synonym or local `name_string`, optional `rank` | source reliability and date recency | Checklist conflict detection and region-scoped accepted-name context. | Global taxonomic truth or occurrence proof. |
| `occurrence_provenance` | `occurrence_record`, `taxon` or `name_string`, `specimen_or_observation`, `region`, date/source nodes | occurrence quality, coordinate validity, basis-of-record weight | Label provenance, geography plausibility, source-specific noise analysis. | Species distribution claim without adequate sampling/citation; phylogeny. |
| `reticulate_or_hybrid_signal` | child/target `taxon` or synthetic case, multiple parent/source lineage `taxon` or `phylogeny_node` nodes, `source` | authoritative-source confidence or synthetic flag | Multi-parent near-miss scoring, tree-obstruction tests, explicit reticulate benchmark labels. | New hybrid origin claim unless sourced; synonym normalization. |
| `missing_rank_bridge` | lower-rank `taxon`, higher-rank ancestor `taxon`, missing `rank`, `source` | derived from backbone path completeness | Hierarchy-aware completion when intermediate rank is absent. | Evidence that missing rank is biologically invalid; synonymy. |

Special limits remain defined: zero synonym clusters reduce `synonym_cluster` columns to none; missing genus rank is represented by `missing_rank_bridge`; no traits or no geography means those hyperedge families are absent rather than imputed; tree-only taxonomy is the subgraph containing only `taxonomic_parentage`.

## Labels and Tasks

The initial label space is accepted taxon at species or genus level, with optional multi-rank labels `(family, genus, species)`. Dataset labels are separate nodes so the benchmark can represent noisy labels, synonym labels, and incomplete labels without changing the source taxonomy.

Candidate Cycle 2 tasks:

1. Name normalization: map `name_string` or noisy `dataset_label` to accepted `taxon`.
2. Hierarchy-consistent label completion: infer missing genus/species under known family.
3. Reticulate near-miss detection: distinguish synthetic multi-parent cases from strict hierarchy cases.
4. Conflict scoring: identify when trait/geography/source evidence disagrees with taxonomy.

## Baseline Information Budgets

| Baseline | Allowed inputs | Explicitly hidden inputs | Expected role |
|---|---|---|---|
| Flat classifier | Example features only; no taxonomy edges; labels as atomic classes | Parent/child edges, synonym clusters, reticulation labels | Tests whether hierarchy matters at all. |
| Label-frequency baseline | Training-label counts and global class priors | Features, names, taxonomy depth, graph/hypergraph edges | Detects class imbalance memorization. |
| Taxonomy-depth baseline | Rank/depth priors and allowed rank path lengths | Names, traits, occurrences, synonym mappings, reticulation labels | Detects depth/rank shortcut behavior. |
| Tree/DAG baseline | `taxonomic_parentage` and `missing_rank_bridge` only; one accepted parent path per taxon unless source backbone is DAG-like | Synonym clusters, traits, occurrence geography, checklist conflicts, reticulation edges | Tests strict hierarchy information. |
| Ordinary graph baseline | Pairwise edges generated from the same permitted evidence families, with edge type labels retained | Native hyperedge cardinality and role constraints | Fair graph competitor; must not receive extra information. |
| Clique-expansion graph | Pairwise clique from each hyperedge with provenance that it was expanded | Native multi-way semantics; hyperedge-level cardinality penalties | Negative control for false pairwise similarity. |
| Native hypergraph | Incidence matrix with typed hyperedges, role weights, and provenance | Held-out target labels and leakage-prone accepted mapping depending on task | Tests whether multi-way evidence helps beyond fair graph baselines. |

## Leakage Controls

Train/test splits must be by accepted taxon or synonym cluster for name-normalization tasks. A synonym of a held-out accepted taxon cannot appear in training if the task is to infer that accepted taxon from names.

Accepted-name mappings are features only for a name-normalization task. For classification from traits or occurrences, direct `name_string -> accepted taxon` edges for test labels must be removed or masked.

Occurrence geography must be coarsened or split by taxon/source so a model cannot solve the task by memorizing a one-record country/taxon pair. GBIF occurrence samples must retain dataset key and license metadata because source-specific bias is part of the evidence.

Synthetic reticulation labels must be hidden from tree/DAG, flat, label-frequency, and taxonomy-depth baselines. Those baselines may see only the permitted taxonomy/trait/occurrence evidence for the corresponding task.

Trait convergence cases must include taxonomically distant taxa sharing the same trait hyperedge. A model receives credit only if it avoids converting trait similarity into false taxonomic closeness.

When WFO, GBIF, and Open Tree disagree, the disagreement is represented as source-specific evidence rather than reconciled away. WFO remains the default plant taxonomy/nomenclature layer for the first prototype; Open Tree remains phylogeny/synthesis context.

## Edge Weights

Default weights:

| Evidence source | Initial weight | Reason |
|---|---:|---|
| WFO accepted taxonomy/synonym edge | 1.0 | Canonical plant taxonomy/nomenclature source for prototype. |
| GBIF accepted taxon match | 0.8 | Useful aggregator/backbone, but not the chosen canonical source. |
| Open Tree TNRS/phylogeny-context edge | 0.7 | Synthesis evidence, separate from WFO nomenclature. |
| Synthetic trait syndrome | configurable, default 0.5 | Stress-test signal, not biological authority. |
| Synthetic reticulation edge | configurable, default 1.0 inside synthetic benchmark | Ground truth for synthetic diagnostic only. |
| Occurrence provenance | quality-dependent, default 0.5 | Sensitive to sampling and source bias. |

Weights are not biological confidence by themselves. They are modeling priors for benchmark ablations and must be reported with source/provenance.

## Initial Falsification Criteria

The hypergraph formulation is unhelpful for the first prototype if all measured gains are reproduced by the fair ordinary graph baseline, synonym normalization alone explains the improvement, or random trait hyperedges improve performance as much as real/synthetic trait syndromes.

The formulation remains worth pursuing if occurrence provenance, regional checklist context, missing-rank bridges, or reticulate synthetic labels create measurable behavior that cannot be represented by a single-parent taxonomy tree without either losing information or adding false pairwise similarities.
