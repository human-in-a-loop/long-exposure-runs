<!--
created: 2026-05-17T15:50:00Z
cycle: 1
run_id: run-phytograph-cycle1
agent: worker
milestone: M0.1
track: 1
-->

# Track 1 — Reticulation Atlas: Scoping

## (a) Central question

Quantify, on a planetary scale, where and by how much angiosperm evolution departs from a single-parent tree. Produce the first computable, queryable map of reticulation across angiosperms.

## (b) Predictive targets (concrete, falsifiable)

1. **`tree_compatibility_index ∈ [0,1]` per taxon**, with source set and confidence. A taxon at 0 is "this lineage cannot be encoded as single-parent without loss"; at 1 is "single-parent encoding is lossless given current evidence." Falsifiable: when applied to canonical polyploids/hybrids without supervision, TCI must be low on those taxa.
2. **Reticulation hotspot ranking per clade.** Top-N reticulation-density orders/families. Falsifiable: canonical reticulating clades (Triticeae, Brassiceae, Musa, Citrus, Rosaceae, Salicaceae, Asteraceae) must appear in the top 25 ranked orders/families.
3. **Held-out polyploid/hybrid recovery.** Without labels, the index identifies *Triticum aestivum* (allohexaploid), *Brassica napus* (allotetraploid), *Musa* cultivars (sterile triploid hybrids), *Spartina anglica* (recent allopolyploid), *Tragopogon mirus / T. miscellus* (1920s allopolyploids), *Helianthus anomalus / paradoxus / deserticola* (hybrid origin). Falsifiable: recall ≥ 0.8 at top-1% of TCI ranking.
4. **Under-studied-clade reticulation candidates.** Ranked list of tropical genera with high chromosome-count variance, high synonym turnover, and high TCI uncertainty. Filed as predictions, not facts.

## (c) Formal target (mathematical object)

An information-theoretic measure
`TCI(v) = 1 − H_reticulate(v) / H_max(v)`
derived from the hypergraph's incidence structure restricted to `taxonomic_parentage`, `hybridization_event`, `polyploidization_event`, and `reticulate_inheritance_evidence` edges. The numerator is the entropy of the multi-parent posterior over `v`'s ancestry given those edges; the denominator is the entropy under a uniform multi-parent prior over taxa in `v`'s clade.

Theorem template (to be proven in M4.F): under a stated generative prior in which each taxon is generated with probability `1−p` from a single parent and probability `p` from two parents, `E[TCI] = 1 − f(p)` where `f` is strictly decreasing in `p` and `f(0) = 0`. Equivalently, TCI distinguishes single-parent from multi-parent inheritance regimes asymptotically.

## (d) Data sources required

- CCDB (chromosome counts) — primary
- Plant DNA C-values — supplement
- Open Tree of Life (phylogenetic context for clade definitions)
- WFO + GBIF (synonym normalization, since hybrid taxa often have unstable nomenclature)
- Curated polyploid records (Wood et al. supplements and successors)
- Cultivar pedigree literature (for crops where pedigrees exist)

## (e) Minimum viable scale

- ≥ **30,000 taxa with at least one `chromosome_count_assertion`** (CCDB covers ~20–30k species; we should clear this floor).
- ≥ **2,000 documented `polyploidization_event` or `hybridization_event` edges**.
- ≥ **30 angiosperm orders** with non-trivial reticulation evidence (for the hotspot ranking to be meaningful).
- If chromosome-count coverage falls below 10,000 taxa, the TCI's unsupervised polyploid-recovery validation becomes underpowered and Track 1's headline prediction is **data-limited**.

## (f) Falsification protocol

- If `TCI` correlates trivially (Spearman ρ > 0.7) with publication density per taxon, family size, or genome-size variance once those are controlled out, the contribution is informational (about literature) rather than biological. **Flag explicitly and pivot to a residual-TCI metric.**
- If canonical-polyploid recovery falls below 0.5 at top-1%, the TCI is broken; redesign before any prediction is filed.
- If the index is collinear with chromosome-count-availability (i.e. TCI is "studied vs unstudied" rather than "reticulating vs not"), report as falsified and add an availability-controlled variant.

## (g) Parallelism axis

**Per-clade fan-out** across ~50 major angiosperm orders/families. Each clone computes the local TCI on its assigned clade against the frozen substrate; clones write only to their clade-namespaced output and merge at Barrier 4.

## (h) Prior-campaign kernel contribution

- **Lift:** the seven hyperedge families from the prior `hypergraph_schema.md` are subsumed in PhytoGraph schema §3.1–3.2. Specifically `taxonomic_parentage`, `synonym_cluster`, `missing_rank_bridge` are used unchanged.
- **Lift:** the clique-expansion warning theorem (cycle-5 M7) directly motivates Track 1's choice to compute TCI on native hyperedges, not clique expansions.
- **Partial lift:** the synthetic reticulate-taxonomy benchmark generator (cycle-2 M3) is the unit-test substrate for TCI before it is run on real data.
- **Retire:** the "hypergraph vs DAG" framing as headline. Track 1's headline is the planetary reticulation map; the DAG comparison is an ablation only.
