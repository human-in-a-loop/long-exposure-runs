---
created: 2026-05-17T15:50:00Z
run_id: run-phytograph-cycle1
agent: worker
supersedes: plan_of_record.md (plant-taxonomy hypergraph, cycles 1–77)
---

# Plan of Record — PhytoGraph: A Six-Track Discovery Program

**Created:** 2026-05-17T15:50:00Z (PhytoGraph adoption)
**Run id:** run-phytograph-cycle1
**Prior campaign:** plant-taxonomy hypergraph (M1–M8, cycles 1–77) — complete and validated. Kernel inheritance documented in `docs/prior_campaign_kernel.md`.

## Directive (verbatim — PhytoGraph)

# Long-Exposure Research Prompt: PhytoGraph

## Campaign Title

**PhytoGraph: A Six-Track Discovery Program for Plant Reticulation, Coevolution, Convergence, Domestication, Chemodiversity, and the Limits of AI Botanical Knowledge**

## Mission

Run a full-scale long-exposure research campaign that builds **PhytoGraph** — a large, typed, auditable hypergraph of plant biology — and uses it as a **discovery instrument** across six parallel research tracks. PhytoGraph is not a catalog, not a wiki, and not a representation-quality benchmark. It is a substrate for producing falsifiable predictions that the existing literature does not yet contain.

The six tracks:

1. **Reticulation Atlas** — quantify, planet-wide, where and how much the tree-of-life metaphor lies for angiosperms.
2. **Ghost Hyperedges** — recover extinct coevolutionary partnerships (anachronistic fruits, ghost pollinators, missing dispersers) from holes in the modern hypergraph.
3. **Convergence Pressure** — formalize and measure the evolutionary inevitability of fruit syndromes, defense chemistry, and other repeatedly-evolved traits.
4. **Domestication Hypergraph** — represent every major crop as a multi-parent edge spanning wild ancestors, Vavilov centers, human selection, and companion species; use it to recommend wild-relative substitutes under climate stress.
5. **Chemodiversity Predictor** — predict undocumented phytochemistry from family-level + ecological + herbivore-pressure hyperedge signatures, as a drug-discovery and ethnobotany prior.
6. **Botanical Foundation Model Probe** — use PhytoGraph as adversarial ground truth to measure where modern AI hallucinates plant biology, with particular attention to high-stakes failure modes.

Each track produces its own predictive instrument, validation protocol, formal contribution, falsification protocol, and prediction ledger. The hypergraph substrate is shared. The audit is rigorous and per-prediction, not generic. The success criterion is not "we built a thing" — it is **"we predicted something the existing literature does not yet contain, and either validated it or falsified it cleanly."**

(Full directive body — central reframing, required novelty, per-track sections, unified hypergraph substrate, required conceptual distinctions, data sources, access and tooling, scale and coverage tiers, parallelism and fan-out strategy, phase plan, predictive validation protocol, required final deliverables, atlas success criteria, research success criteria, guardrails, initial hypotheses, suggested milestones — is preserved verbatim in the cycle-1 directive input and is canonical from there. This plan-of-record references it rather than duplicating ~9000 lines; the directive is immutable per long-exposure convention.)

## Directive Adoption Note

The prior directive (Plant Taxonomy as Hypergraph Structure) is superseded. Its M1–M8 deliverables are reusable as a kernel (see `docs/prior_campaign_kernel.md`); they are NOT re-executed.

## Goals (refactored G1–G7)

| Goal ID | Goal | Track(s) | Owner |
|---|---|---|---|
| G1 | Build a frozen, typed, auditable angiosperm hypergraph substrate (≥50,000 taxa Tier 0) with uniform provenance. | substrate | researcher/worker |
| G2 | Quantify reticulation across angiosperms via a computable `tree_compatibility_index` with stated invariance properties. | Track 1 | worker |
| G3 | Recover candidate anachronistic / ghost-coevolutionary partnerships from hypergraph holes; recover ≥30% of held-out Janzen-Martin canon. | Track 2 | worker |
| G4 | Formalize convergence pressure via a hypergraph statistic that ranks canonical convergent traits above family-size / sampling-density confounds. | Track 3 | worker |
| G5 | Deliver a Crop Substitution Engine that agrees with CGIAR-class expert recommendations at genus level on ≥60% of held-out cases AND outperforms a sister-species baseline by a measurable margin. | Track 4 | worker |
| G6 | Deliver a chemodiversity neighborhood-completion predictor that ranks known phytochemical source taxa in the top decile of their family before their discovery date (temporally-frozen training). | Track 5 | worker |
| G7 | Deliver a foundation-model botanical-reasoning probe with publishable per-(model × category) error rates and a taxonomy of failure modes. | Track 6 | worker |
| G+ | Falsification & ablation contract: every track must have at least one ablation that would invalidate its headline; insights are filed in the prediction or speculation ledger. | cross-cutting | auditor |

## Milestones

(Wave-structured. Within a wave, milestones run as concurrent clones; between waves, a barrier enforces consistency.)

### Wave 0 — BARRIER 0 (single coordinator) — **active this cycle**

| Milestone | Description | Success criteria (falsifiable) | Dependencies |
|---|---|---|---|
| M0.1 | Scoping documents, unified schema, data-source audit, risk register; schema frozen v1.0 | ≥6 scoping docs with numerical minimum-viable-scale; ≥15 sources audited; ≥8 risks; schema v1.0 frozen; ≥25 edge types with allowed-evidence-scope declared; plan-of-record updated; prior-campaign kernel classified | — |

### Wave 1 — FAN-OUT A (one clone per source group)

| Milestone | Description | Success criteria | Dependencies |
|---|---|---|---|
| M1.1 | WFO + Open Tree + POWO + GBIF taxonomy backbone (internal crosswalk sub-barrier) | Tier 0 candidate ≥50k taxa staged; synonym crosswalk lossless on test set | M0.1 |
| M1.2 | GBIF occurrence/media samples | ≥10k taxa with ≥1 occurrence record; license/attribution preserved | M0.1 |
| M1.3 | CCDB + Plant DNA C-values + curated polyploid records | ≥30k chromosome-count assertions ingested | M0.1 |
| M1.4 | PBDB + Late Quaternary Extinctions + megafauna ranges (Faurby & Svenning) | ≥200 extinct-fauna nodes with date and range | M0.1 |
| M1.5 | Fruit-syndrome / C4 / succulence / myrmecochory codings | ≥5 trait lists with ≥500 taxa each | M0.1 |
| M1.6 | Genesys + USDA GRIN + FAO CWR + WorldClim/CHELSA | ≥1000 crop-wild-relative pairs with climate envelopes | M0.1 |
| M1.7 | KNApSAcK + NPASS + Duke + ChEBI + ethnobotanical DBs | ≥1000 taxa with ≥1 phytochemical assertion; ≥5 chemically-distinct families | M0.1 |
| M1.8 | Free/open-source offline foundation-model probe harness scaffolding | Static benchmark + deterministic scoring harness produced; no paid API calls or key-gated providers | M0.1 |
| M1.9 | Wikidata / Wikimedia Commons metadata | Crosswalk to ≥30k taxa; media license fields preserved | M0.1 |
| (Barrier 1) | Substrate join + synonym normalization + deduplication | Tier 0 ≥50k taxa or documented blocker; canonical-key conformance | M1.1–M1.9 |

### Wave 2 — FAN-OUT B (6 track clones, each with inner fan-out)

| Milestone | Description | Success criteria | Dependencies |
|---|---|---|---|
| M2.T1 | Reticulation enrichment (inner: per-clade) | ≥30 angiosperm orders enriched | Barrier 1 |
| M2.T2 | Ghost-partner enrichment (inner: per-candidate-class) | ≥5 candidate classes enriched | Barrier 1 |
| M2.T3 | Convergence enrichment (inner: per-trait) | ≥8 convergent traits enriched | Barrier 1 |
| M2.T4 | Domestication enrichment (inner: per-(crop × climate)) | ≥30 crops × ≥3 climate envelopes | Barrier 1 |
| M2.T5 | Chemodiversity enrichment (inner: per-family) | ≥8 families enriched | Barrier 1 |
| M2.T6 | Adversarial-probe construction (inner: per-(free/open/local model × category)) | ≥7 probe categories × ≥3 free/open/local model configs × ≥30 questions each, or benchmark-only `data-limited` if local models unavailable | Barrier 1 |
| (Barrier 2) | Cross-track schema conformance + duplicate-edge resolution | Conformance check passes; duplicate canonical-key edges merged | M2.T1–M2.T6 |

### Wave 3 — FAN-OUT C ∥ C′ (instruments + Atlas concurrent)

| Milestone | Description | Success criteria | Dependencies |
|---|---|---|---|
| M3.T1 | Tree-compatibility index + reticulation hotspot detector | Reproducible per-taxon TCI ∈ [0,1] with confidence; recovers ≥80% of canonical polyploid lineages unsupervised | Barrier 2 |
| M3.T2 | Ghost-Partner Candidate Ranker | Ranked list with ≥50 candidates; held-out canon-recovery measured | Barrier 2 |
| M3.T3 | Convergence-Pressure statistic | Per-trait score; canonical-case recovery measured | Barrier 2 |
| M3.T4 | Crop Substitution Engine | Queryable (crop, climate) → ranked substitutes | Barrier 2 |
| M3.T5 | Chemodiversity neighborhood-completion predictor | Ranked under-screened taxa per family | Barrier 2 |
| M3.T6 | Free/open-source offline foundation-model probe runner | Per-(free/open/local model × category) error rates and calibration, or benchmark-only `data-limited`; no paid API calls | Barrier 2 |
| M3.A | Botanical Atlas (local interactive site) | ≥10k taxa browsable; per-track predictions exposed with evidence-vs-prediction distinction; counter-claim filing supported | Barrier 2 |
| (Barrier 3) | Instruments queryable from Atlas | Atlas links to instrument outputs; provenance/license badges present | M3.T1–M3.T6, M3.A |

### Wave 4 — FAN-OUT D ∥ D′ ∥ D″ (validation + formal + ablations)

| Milestone | Description | Success criteria | Dependencies |
|---|---|---|---|
| M4.V1–V6 | Per-track validation (inner fan-out per held-out case) | ≥1 validated prediction per track; falsified cases reported | Barrier 3 |
| M4.V2 | Track 2 held-out ghost-partner validation/falsification child branch | Track-local validation scaffold and ablation sensitivity recorded; no master-ledger promotion before Barrier 3 | Barrier 3 |
| M4.V4 | Track 4 climate-substitution validation closure | Determine whether CWR and climate-envelope evidence supports bounded H4 validation; close as data-limited if observed bioclim vectors or accepted-key CWR/held-out coverage are insufficient; no recommendation-like claims without climate-aware validation and ablations | Barrier 3 |
| M4.V5 | Track 5 temporal held-out chemodiversity validation child branch | Track-local temporal holdout diagnostics recorded; no master-ledger promotion before Barrier 3 | Barrier 3 |
| M4.V6 | Track 6 free/open/local model execution closure | Local model runtime availability inspected; deterministic scorer controls documented; H6 closed as environment-limited if no runnable local model exists; no model error-rate claims without audited model responses | Barrier 3 |
| M4.F1–F≥3 | Formal contributions (≥3 across tracks) | ≥3 theorem templates / counterexamples / diagnostics with proof of properties | Barrier 2 |
| M4.A1–An | Ablation matrix | All cross-cutting ablations executed; results in shared table | Barrier 2 |
| M4.A-track3-convergence-confounds | Track 3 convergence-pressure validation/confound child branch | Track-local convergence/confound outcomes recorded; no master-ledger promotion before Barrier 4 reconciliation | Barrier 2 |
| M4.A-track5-duke-source-ablation | Track 5 Dr. Duke/source-dominance ablation child branch | Track-local source-ablation result recorded as sensitivity/null finding; no master-ledger promotion before Barrier 4 reconciliation | Barrier 2 |
| (Barrier 4) | Prediction ledger consolidation | All sub-ledgers merged into `prediction_ledger.tsv`; statuses reconciled | M4.V1–V6, M4.A1–An |

Wave 4 child milestone namespace repair, 2026-05-18: cycle-10 fork rows for `M4.V2`, `M4.V5`, and `M4.A-track5-duke-source-ablation` are retained as historical track-local outputs because they already exist in `promise_ledger.jsonl`. Cycle-14 post-merge integration also makes `M4.A-track3-convergence-confounds` explicit after the Track 3 branch produced a track-local convergence/confound package under a surrogate `_plan/` ledger ID. Cycle-15 Track 6 closure makes `M4.V6` explicit so free/open/local model availability and scorer-limit closure can be audited independently. Cycle-15 Track 4 closure makes `M4.V4` explicit so H4 climate-substitution evidence sufficiency can be audited independently. These plan updates make exact child IDs explicit without promoting any row to the master prediction ledger and without authorizing Barrier 4 reconciliation before the validation/ablation packages are audited.

### Wave 5 — BARRIER 5 (single coordinator)

| Milestone | Description | Success criteria | Dependencies |
|---|---|---|---|
| M5.1 | Final report, contribution ledger, audit report | All 13 required deliverables produced; per-track predictions/validations/falsifications/data-limited cases listed | Barrier 4 |

### Legacy Milestone Disposition (archived prior campaign)

These IDs belong to the superseded Plant Taxonomy as Hypergraph Structure run (`run-2026-05-17T004540Z`) and remain in `promise_ledger.jsonl` as historical evidence. They are not active PhytoGraph milestones and must not be re-executed for this campaign; they are listed here only so ledger validation can distinguish archived history from schema drift after the PhytoGraph pivot.

| Milestone | Description | Success criteria | Dependencies |
|---|---|---|---|
| M1 | Archived prior-campaign data and literature feasibility map. | Historical evidence retained; no PhytoGraph execution implied. | superseded prior run |
| M2 | Archived prior-campaign hypergraph schema and baseline definition. | Historical evidence retained; no PhytoGraph execution implied. | superseded prior run |
| M3 | Archived prior-campaign synthetic benchmark generator. | Historical evidence retained; no PhytoGraph execution implied. | superseded prior run |
| M4 | Archived prior-campaign metric scaffolding. | Historical evidence retained; no PhytoGraph execution implied. | superseded prior run |
| M5 | Archived prior-campaign public taxonomy sample. | Historical evidence retained; no PhytoGraph execution implied. | superseded prior run |
| M6 | Archived prior-campaign baseline and hypergraph experiments. | Historical evidence retained; no PhytoGraph execution implied. | superseded prior run |
| M7 | Archived prior-campaign formal diagnostic. | Historical evidence retained; no PhytoGraph execution implied. | superseded prior run |
| M8 | Archived prior-campaign final synthesis and audit. | Historical evidence retained; no PhytoGraph execution implied. | superseded prior run |

## Out of scope (explicit, this campaign)

- Claims of new plant taxonomy, hybridization, anachronism, or bioactivity as established truth.
- Aggressive scraping when APIs/dumps exist.
- A "wiki of fruit plants" as headline deliverable. The Atlas is a window into predictions, not the deliverable itself.
- "Hypergraph vs DAG" as headline benchmark. Audit is per-track per-prediction.

## Pointer to ledger

Every milestone status, history, and judgment lives in `promise_ledger.jsonl`,
filtered by `milestone_id`. The schema document `phytograph_schema.md` is frozen at v1.0;
any modification requires a `_plan/schema-revision-vN.M` event and a new BARRIER 0 pass.

The PhytoGraph directive section above is **immutable** after this cycle. Goals and milestones tables are mutable; every edit must emit a ledger event with `milestone_id: "_plan/<descriptive-change-name>"`.

## Legacy Artifact Disposition

Legacy manager assessments and periodic cycle reports from `run-2026-05-17T004540Z` are historical harness outputs. Missing legacy report or manager-assessment files referenced by old ledger rows are not to be regenerated during PhytoGraph Barrier 1; any future cleanup should be append-only and recorded under `_archive/` or `_plan/`, not by rewriting historical events. Current PhytoGraph source branches should treat those warnings as audit backlog unless they become new blocking errors.
