<!--
created: 2026-05-17T15:50:00Z
cycle: 1
run_id: run-phytograph-cycle1
agent: worker
milestone: M0.1
track: 4
-->

# Track 4 — Domestication Hypergraph: Scoping

## (a) Central question

Can the full history of plant domestication — wild ancestors, hybridization events, Vavilov centers of origin, selection traits, companion species, geographic spread, breeder pedigrees — be represented as a coherent hypergraph, and does that representation usefully predict crop-substitution choices under climate stress?

## (b) Predictive targets (concrete, falsifiable)

1. **Crop Substitution Engine.** Given `(failing_crop, target_climate_envelope)`, return ranked wild-relative substitutes with mechanistic justification (shared trait, hybridization compatibility from `crop_pedigree` evidence, climate match, ethnobotanical precedent). Falsifiable per directive H4: ≥ 60% genus-level agreement with CGIAR/IRRI/CIMMYT recommendations on held-out crops.
2. **Vavilov-center hypergraph.** Confidence-tagged centers, accepting that several are contested. Filed as `vavilov_center_hyperedge` evidence, not as fact.
3. **Outperformance over sister-species baseline.** The multi-parent hypergraph engine must beat a "use the same genus" recommender by a measurable margin (≥ 5% on a stated agreement metric). If not, the hypergraph adds no value over taxonomic proximity — falsified.
4. **Under-recognized crop-wild-relative pairs.** Orphan crops (fonio, teff, sorghum landraces, minor millets, bambara groundnut, *Dioscorea* species) with predicted wild-relative substitutes that current breeding programs have not flagged.

## (c) Formal target (mathematical object)

A ranking function `S(c, T) → Σ_v score(v | c, T)` where `c` is the failing-crop node, `T` is the target climate envelope, and `v` ranges over candidate `wild_ancestor` / sister `taxon` nodes. The score combines:

- climate-envelope-match (Mahalanobis-style distance in WorldClim/CHELSA feature space),
- hybridization-compatibility (does a `crop_pedigree` edge link the crop's wild ancestor and `v`?),
- trait-overlap (shared `trait_syndrome` edges),
- ethnobotanical precedent (`ethnobotanical_use_assertion` edges with people-group preserved).

Theorem template (M4.F): if the multi-parent-edge contribution to `S` is set to zero, `S` collapses to a sister-species recommender. Therefore the *delta* between full and ablated `S` measures the unique contribution of the multi-parent edge — making the directive's H4-falsification operational.

## (d) Data sources required

- Genesys (germplasm DOIs, accession-level data)
- USDA GRIN
- FAO WIEWS / CWR inventories
- Breeder pedigree literature (for `crop_pedigree`)
- WorldClim v2 + CHELSA (climate envelopes)
- WFO/POWO (cultivation status crosswalk)
- CGIAR / IRRI / CIMMYT recommendation lists (for held-out validation)

## (e) Minimum viable scale

- ≥ **1,000 crop and crop-wild-relative taxa** in the substrate.
- ≥ **30 major crops** with multi-parent `crop_pedigree` edges (wheat, rice, maize, barley, oats, sorghum, finger/pearl millet, banana, plantain, cassava, sweet potato, potato, tomato, pepper, cotton, peanut, soybean, common bean, chickpea, lentil, pea, sunflower, apple, citrus complex, grape, olive, coffee, cacao, brassica complex, sugarcane).
- ≥ **3 climate envelopes per crop** (current, +2°C, +4°C) yielding ≥ 90 (crop × climate) substitution queries for the matrix.
- ≥ **20 held-out crops** with documented CGIAR-class expert recommendations.
- If `crop_pedigree` coverage falls below 15 multi-parent crops, Track 4's headline (multi-parent engine beats sister-species) is **data-limited** and the track defaults to filing the matrix.

## (f) Falsification protocol

- If genus-level agreement < 30%, **fail**.
- If the engine matches sister-species baseline within noise (delta < 2%), **falsified** per directive — the hypergraph adds no value; pivot to reporting as negative result.
- If recommendations are dominated by a single climate-feature (e.g. mean annual temperature) and other features have no effect, the climate component is degenerate; report and fix.
- If the engine over-recommends well-studied/popular crops (rich-get-richer), per-source ablation will catch it; flag as confound.

## (g) Parallelism axis

**Per-(crop × climate envelope) fan-out:** for ~30 crops × 3 climate envelopes = ~90 clones. Each clone runs the Substitution Engine for one (crop, climate) pair; held-out expert recommendations are scored in parallel.

## (h) Prior-campaign kernel contribution

- **Lift:** the prior schema's `regional_checklist_context` and `taxonomic_parentage` are unchanged in PhytoGraph; the sister-species ablation is the prior tree/DAG baseline.
- **Retire:** the prior campaign had no germplasm, climate, or pedigree layer. Track 4 introduces these from scratch.
- **Lift:** the prior leakage-control practice (no `name_string → accepted_taxon` for held-out test labels) is reused: held-out crops' CGIAR recommendations must not leak into the engine's input.
