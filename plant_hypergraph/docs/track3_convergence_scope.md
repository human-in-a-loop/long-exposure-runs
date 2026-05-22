<!--
created: 2026-05-17T15:50:00Z
cycle: 1
run_id: run-phytograph-cycle1
agent: worker
milestone: M0.1
track: 3
-->

# Track 3 — Convergence Pressure: Scoping

## (a) Central question

Formalize and measure the evolutionary inevitability of repeatedly-evolved phenotypes — and use the resulting statistic to predict which under-sampled lineages are likely to harbor convergent forms not yet documented.

## (b) Predictive targets (concrete, falsifiable)

1. **Convergence Pressure Score (CPS) per trait.** A scalar derived from `convergence_signature` hyperedge topology that measures the independent recurrence rate of a trait across distant clades.
2. **Ranked list of under-sampled lineages predicted to harbor convergent forms.** Concrete predictions: unrecognized myrmecochores in tropical understory genera; suspected C4 lineages in poorly-screened sedges/grasses; succulent or CAM forms in under-sampled Pachypodium / Cissus relatives.
3. **Canonical-case validation.** CPS ranks textbook convergent traits (C4, succulence, myrmecochory, fleshy-fruit, samara, elaiosome) above family-size and sampling-density confounds. Falsifiable: rank correlation between CPS and confound baselines < 0.5 for these traits.
4. **Convergence-vs-homology operationalization.** From hypergraph topology alone, classify each trait state into convergent vs homologous. Falsifiable on the 6 canonical traits.

## (c) Formal target (mathematical object)

A hypergraph statistic
`CPS(t) = (#independent_clade_appearances_of_t / family_size_normalizer(t)) × topological_dispersion(t)`
where `topological_dispersion` is the mean pairwise hypergraph-distance between taxa carrying trait `t` measured over `taxonomic_parentage` and `phylogenetic_or_reticulate_context` edges.

Theorem template (M4.F): under a null model where trait `t` is inherited only along `taxonomic_parentage` edges from a single common ancestor, `E[CPS(t) | homology]` is bounded above by a closed-form function of clade size; observed CPS exceeding this bound is evidence for convergence. **Stated invariance: CPS is invariant under uniform addition of synonyms (a synonym cluster does not increase apparent convergence) and uniform pruning of taxonomically-isolated leaves.**

## (d) Data sources required

- Published fruit-syndrome codings (Phase 2 source group M1.5)
- C4 lineage lists (Sage and successors)
- Succulence lists
- Myrmecochory + elaiosome lists
- Samara / capsule lists for fruit-syndrome convergence
- OTT phylogenetic context for clade distance
- WFO taxonomy for family normalization

## (e) Minimum viable scale

- ≥ **8 convergent traits** with literature-curated taxa lists.
- ≥ **500 taxa per trait** (on average) with positive trait state.
- ≥ **40 angiosperm orders** represented across the 8 traits.
- ≥ **6 canonical-case held-out traits** (C4, CAM, succulence, fleshy-fruit, samara, myrmecochory) for validation.
- If any trait's positive-taxa list has < 50 entries, that trait's CPS is **data-limited** and is filed but not used in the family-size-confound test.

## (f) Falsification protocol

- If CPS is collinear (R² > 0.7) with simple `family-size × sampling-density` baseline, **the statistic is artifactual**. The prior campaign's clique-expansion warning suggests an analogous trap here: synonym proliferation can inflate apparent convergence.
- If under-sampled-lineage predictions concentrate in over-screened families (Asteraceae, Fabaceae, Orchidaceae) because those families have the most data — confound is dominant; report as falsified by source-density ablation.
- If the convergence-vs-homology classifier disagrees with phylogenetic comparative methods (e.g. character-state reconstruction on the OTT synthesis tree) on ≥ 50% of canonical cases, the topological signal is insufficient and the contribution becomes "negative result: hypergraph topology alone cannot distinguish convergence from homology."

## (g) Parallelism axis

**Per-trait fan-out:** C4 · CAM · succulence · fleshy-fruit · drupe · samara · capsule · elaiosome · myrmecochory · carnivory · parasitism · ant-domatia · resin-canal · latex. One clone per trait; canonical-case validation in parallel.

## (h) Prior-campaign kernel contribution

- **Lift:** the prior `trait_syndrome` hyperedge family in PhytoGraph schema §3.7 is unchanged in shape; CPS computes over it.
- **Lift:** the synthetic benchmark generator (cycle-2 M3) is reused for CPS unit tests — it can generate synthetic convergent vs homologous cases with known ground truth.
- **Lift:** the hierarchy-aware metric machinery (cycle-2 M4) provides the `family-size-normalizer` machinery for free; reuse rather than reimplement.
- **Partial lift:** the clique-expansion warning theorem (cycle-5 M7) constrains the CPS implementation: it must operate on native hyperedges, not pairwise clique expansions, because the warning shows the latter creates spurious convergence signals.
- **Retire:** the prior framing of "improvement over tree baseline" — Track 3's headline is per-trait CPS validation, not the comparison.
