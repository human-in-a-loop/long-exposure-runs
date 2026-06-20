<!--
created: 2026-05-17T15:50:00Z
cycle: 1
run_id: run-phytograph-cycle1
agent: worker
milestone: M0.1
track: 5
-->

# Track 5 — Chemodiversity Predictor: Scoping

## (a) Central question

Can a typed hypergraph predict where undocumented phytochemistry — alkaloids, terpenes, glycosides, bioactive peptides — is likely to be found, by combining family-level + ecological + herbivore-pressure hyperedge signatures, as a drug-discovery and ethnobotany prior?

## (b) Predictive targets (concrete, falsifiable)

1. **Ranked list of under-screened taxa with predicted bioactive classes** per family, prioritized by neighborhood completion in the `chemodiversity_signature` hyperedge structure.
2. **Per-family/clade `chemodiversity_signature`** as a formal object (compound-class distribution conditioned on ecological context and herbivore pressure).
3. **Temporally-frozen historical recovery.** With training data frozen before the isolation date, would the model have prioritized the source taxon? Concrete test cases (per directive H5):
   - *Taxus brevifolia* before paclitaxel (1971 isolation; freeze pre-1971)
   - *Catharanthus roseus* before vincristine (1958; freeze pre-1958)
   - *Cinchona* spp. before quinine (1820 isolation; freeze pre-1820 — likely data-limited)
   - *Artemisia annua* before artemisinin (1972; freeze pre-1972)
   Target: each canonical source taxon ranked in **top decile of its family** at freeze time.
4. **Ethnobotanical-precedent test.** Do `ethnobotanical_use_assertion` edges predict subsequent confirmed `bioactivity_assertion`?

## (c) Formal target (mathematical object)

A neighborhood-completion score
`Chem(v, c) = Σ_{u ∈ N_hg(v)} I(c ∈ compound_classes(u)) × w(u,v)`
over the hypergraph neighborhood `N_hg(v)` defined by shared `phytochemical_assertion`, `herbivore_defense_relationship`, and `habitat_association` edges, with weights `w` derived from edge-type-specific source reliabilities.

Stated invariance: `Chem` is invariant to permutations of source identity (replacing one source with another of equal reliability does not change the score) and bounded above by the size of the relevant chemical-class universe.

## (d) Data sources required

- KNApSAcK (primary phytochemical assertions; Japanese-literature-skew flagged)
- NPASS (natural products)
- Dr. Duke's Phytochemical & Ethnobotanical DB (USDA-ARS; ethnobotany joined)
- ChEBI (compound IDs)
- Native American Ethnobotany DB (Moerman) — **sovereignty review required**
- PROTA (tropical Africa)
- PROSEA (SE Asia)
- Herbivore-defense literature

## (e) Minimum viable scale

- ≥ **1,000 taxa with at least one `phytochemical_assertion`** (Tier 3 floor).
- ≥ **8 chemically-distinct families** with ≥ 100 taxa each having phytochemistry (Solanaceae, Apocynaceae, Brassicaceae, Lamiaceae, Asteraceae, Rubiaceae, Euphorbiaceae, Fabaceae).
- ≥ **300 unique `phytochemical_compound` nodes**.
- ≥ **3 historical case studies** with sufficient pre-discovery training data for the temporally-frozen test (Taxus, Catharanthus, Artemisia are the most likely to have enough; Cinchona may be too early).
- If phytochemistry coverage falls below 500 taxa total, the neighborhood-completion machinery is **data-limited** and Track 5's headline becomes the chemodiversity-signature catalogue only.

## (f) Falsification protocol

- **Rich-get-richer test.** If predictions concentrate on already-over-screened taxa (top-decile of screening intensity), the model is reflecting screening rather than chemistry. Remove an ecological/herbivore-pressure layer and re-run; if performance is unchanged, the chemistry hyperedges are not doing real work — falsified.
- **Temporal-leakage audit.** Any taxon's pre-discovery rank must be computed on a substrate that demonstrably excludes its discovery-era and post-discovery literature. If the audit reveals leakage, recompute or flag as data-limited.
- **Indigenous-attribution audit.** Every `ethnobotanical_use_assertion` row must retain its source attribution and people-group identification. A track output that strips attribution is rejected at Barrier 4.
- **Bioactivity-claim guardrail.** Predictions are explicitly "compound-class candidacy worth screening," never "this taxon is medicinal." Cross-track contamination from Track 5 into Track 6 (safety-related probe questions) is checked at Barrier 2.

## (g) Parallelism axis

**Per-family fan-out:** Solanaceae · Apocynaceae · Brassicaceae · Lamiaceae · Asteraceae · Rubiaceae · Euphorbiaceae · Fabaceae · Rutaceae · Ranunculaceae · Papaveraceae. One clone per family; temporally-frozen held-out discoveries validated in parallel.

## (h) Prior-campaign kernel contribution

- **Retire:** the prior campaign had no phytochemistry layer.
- **Lift:** the prior provenance-preservation discipline maps directly onto the sovereignty-attribution requirement for ethnobotany.
- **Lift:** the synonym-normalization layer is critical here — many phytochemistry papers use synonyms that the substrate must resolve.
- **Lift:** the prior negative-result-preference posture (cycle-6 final synthesis) is the right posture for Track 5's rich-get-richer falsification.
