# Long-Exposure Research Prompt: PhytoGraph

## Campaign Title

**PhytoGraph: A Six-Track Discovery Program for Plant Reticulation, Coevolution, Convergence, Domestication, Chemodiversity, and the Limits of AI Botanical Knowledge**

## Mission

Run a full-scale long-exposure research campaign that builds **PhytoGraph** — a large, typed, auditable hypergraph of plant biology — and uses it as a **discovery instrument** across six parallel research tracks. PhytoGraph is not a catalog, not a wiki, and not a representation-quality benchmark. It is a substrate for producing falsifiable predictions that the existing literature does not yet contain.

The angiosperms are not a tree. They reticulate (polyploidy, hybridization, introgression, grafted chimeras). They converge (fruit syndromes, C4 photosynthesis, succulence, myrmecochory). They coevolve (with dispersers, pollinators, mycorrhizal partners, herbivores, and humans). Their secondary chemistry leaks across families in patterns that respect both phylogeny and ecology. They have been miscatalogued for centuries, and modern AI inherits those miscatalogues. A hypergraph is the natural substrate for all of this. PhytoGraph treats that substrate as a means, not an end.

The six tracks:

1. **Reticulation Atlas** — quantify, planet-wide, where and how much the tree-of-life metaphor lies for angiosperms.
2. **Ghost Hyperedges** — recover extinct coevolutionary partnerships (anachronistic fruits, ghost pollinators, missing dispersers) from holes in the modern hypergraph.
3. **Convergence Pressure** — formalize and measure the evolutionary inevitability of fruit syndromes, defense chemistry, and other repeatedly-evolved traits.
4. **Domestication Hypergraph** — represent every major crop as a multi-parent edge spanning wild ancestors, Vavilov centers, human selection, and companion species; use it to recommend wild-relative substitutes under climate stress.
5. **Chemodiversity Predictor** — predict undocumented phytochemistry from family-level + ecological + herbivore-pressure hyperedge signatures, as a drug-discovery and ethnobotany prior.
6. **Botanical Foundation Model Probe** — use PhytoGraph as adversarial ground truth to measure where modern AI hallucinates plant biology, with particular attention to high-stakes failure modes (toxicity look-alikes, hybrid pedigrees, synonym-induced confusion, region-conditional questions).

Each track produces its own predictive instrument, validation protocol, formal contribution, falsification protocol, and prediction ledger. The hypergraph substrate is shared. The audit is rigorous and per-prediction, not generic. The success criterion is not "we built a thing" — it is **"we predicted something the existing literature does not yet contain, and either validated it or falsified it cleanly."**

## The Central Reframing

This campaign explicitly deprecates three habits from earlier framings of the work:

- **A wiki as flagship deliverable.** The Botanical Atlas (the interactive site) still exists, but it is a window into the research, not the headline output. Researchers should not walk away saying "they built a wiki of fruit plants" — they should walk away saying "they predicted X, Y, Z, three of which checked out and one of which was falsified."
- **Edibility demoted to a stray metadata field.** Human-coupled botany — domestication, ethnobotany, toxicity, drug discovery, foraging safety — is now central via Tracks 4, 5, and 6. Edibility is not the inclusion rule, but the human-plant interaction surface is one of the campaign's primary engines.
- **"Hypergraph vs DAG" as the headline benchmark.** That comparison still happens, but as instrumentation, not as the scientific question. The hypergraph either predicts things the DAG cannot, or it does not. Audit is per-track and per-prediction.

The campaign succeeds if a competent reader of computational biology, crop science, ML evaluation, or phytochemistry can point to at least one falsifiable prediction PhytoGraph made that they did not previously have access to.

## Required Novelty

At least four of the following are required across the six tracks:

- **New predictive instrument** that produces falsifiable claims, not just describes data (one per track is the target).
- **New metric or diagnostic statistic** with stated invariance properties (e.g. reticulation index, convergence pressure score, chemodiversity neighborhood-completion score).
- **New dataset transform** integrating phylogenetic, geographic, paleobotanical, germplasm, phytochemical, or adversarial-probe layers under a single typed schema.
- **New formal contribution** — theorem template, counterexample, sufficient condition, or algorithm with proof of properties.
- **New benchmark** — an adversarial test set for foundation-model botanical reasoning, or a held-out crop-substitution / phytochemistry-discovery / anachronism-recovery test.
- **New insight ledger** that distinguishes validated structural discoveries from speculative or source-biased patterns.
- **New falsification result** — evidence that an apparent insight disappears after controlling for synonymy, source bias, crop popularity, family size, image availability, or publication density.

The final report must explicitly state, per track, what is new, what is merely integrated, and what remains speculative.

---

## Track 1 — Reticulation Atlas

**Central question.** Quantify, on a planetary scale, where and by how much angiosperm evolution departs from a single-parent tree. Produce the first computable, queryable map of reticulation across angiosperms.

**Why this is a breakthrough lane.** Polyploid speciation accounts for a substantial fraction of angiosperm speciation events (Wood et al. and successors). Hybrid swarms are well-documented in *Helianthus*, *Quercus*, *Rosa*, *Citrus*, *Malus*, *Iris*. Grafted chimeras and cultivar pedigrees are reticulation under human selection. There is no comprehensive, machine-readable, cross-clade reticulation atlas. Producing one is a contribution to evolutionary biology, not just to knowledge representation.

**Predictive targets.**
- Given a taxon, return a `tree_compatibility_index ∈ [0,1]` with sources and confidence.
- Given a clade, identify reticulation hotspots — lineages whose single-parent encoding loses the most information.
- Recover known polyploid/hybrid lineages (e.g. *Triticum aestivum*, *Brassica napus*, *Musa* cultivars, *Spartina anglica*, *Tragopogon* allopolyploids) without being told they are polyploid.
- Predict reticulation candidates in under-studied clades (e.g. tropical genera with high chromosome-count variance and high name turnover).

**Formal target.** An information-theoretic measure of reticulation derived from the hypergraph's incidence structure and node typing, with proof that it distinguishes single-parent from multi-parent inheritance under a stated generative prior.

**Data sources.** CCDB (Chromosome Counts Database), Plant DNA C-values, GBIF, Open Tree of Life, curated extraction of published hybridization records, cultivar pedigree databases for major crops.

**Falsification.** If the reticulation index correlates trivially with publication density, family size, or genome-size variance once those are controlled, the contribution is informational rather than biological — flag explicitly.

**Parallelism.** Per-clade fan-out across major angiosperm orders/families. Each clone computes the local reticulation index on its assigned clade against the frozen substrate; results merge at Barrier 4 with no cross-clone writes.

---

## Track 2 — Ghost Hyperedges

**Central question.** Can lost coevolutionary partnerships — anachronistic fruits, ghost pollinators, extinct dispersers, lost mycorrhizal partners — be recovered from holes in the modern hypergraph?

**Why this is a breakthrough lane.** The Janzen-Martin "neotropical anachronism" hypothesis (avocado, osage orange, honey locust evolved for Pleistocene megafauna now extinct) is a 40-year-old conjecture without systematic computational test. Similar logic applies to ghost pollinator specialists, lost fungal partners, and "orphan" fruit syndromes with no extant disperser. PhytoGraph can run this test at scale.

**Predictive targets.**
- A ranked ledger of candidate anachronistic fruits, each tied to: fruit morphology (large mass, hard endocarp, long retention), modern dispersal failure (parent-shadow seedling recruitment, ungulate-mediated dispersal in non-native settings), biogeographic plausibility (overlap with megafauna ranges), extinction timing.
- Ghost-pollinator candidates: flowers whose morphology demands a pollinator absent from the current fauna.
- Ghost-mycorrhizal candidates: plants whose current fungal partnerships look unstable, geographically narrow, or post-glacial.

**Validation protocol.** Hold out canonical Janzen-Martin examples (avocado, *Maclura pomifera*, *Gleditsia triacanthos*, *Annona cherimola* and other Annonaceae, *Mauritia flexuosa*, *Spondias*, *Sideroxylon*, *Asimina triloba*). Train the model without seeing those labels. Check whether the held-out set is recovered in the top-ranked predictions, and how many novel candidates the method proposes.

**Formal target.** A hyperedge-completion inference rule under known extinction, with a proof that — given a stated coevolutionary prior — it correctly identifies a class of anachronistic syndromes.

**Data sources.** Paleobotany literature, megafauna range reconstructions (Faurby & Svenning and successors), Late Quaternary Extinctions database, PBDB, modern dispersal-failure literature, IUCN fauna data for current dispersers.

**Falsification.** If predictions are dominated by neotropical large-fruited Fabaceae and the model cannot distinguish living-megafauna dispersal (elephants and tapirs still working) from ghost-megafauna anachronism, that is a fail.

**Parallelism.** Per-candidate-class fan-out: spawn clones across candidate anachronism classes (large-seeded neotropical Fabaceae, palm-fruit anachronisms, Annonaceae large-fruited candidates, ghost-pollinator Orchidaceae, post-glacial mycorrhizal candidates). Held-out validation cases are independently scored in parallel.

---

## Track 3 — Convergence Pressure

**Central question.** Formalize and measure the evolutionary inevitability of repeatedly-evolved phenotypes — and use the resulting statistic to predict which under-sampled lineages are likely to harbor convergent forms not yet documented.

**Why this is a breakthrough lane.** Convergent evolution is everywhere in plants. Fleshy fruits have evolved independently more than 100 times. C4 photosynthesis has evolved at least 60 times across grasses, sedges, eudicots. Succulence in cacti and euphorbs is the textbook parallelism. Myrmecochory recurs across distant families. A formal hypergraph-derived statistic for convergence pressure would contribute to phylogenetic comparative methods, an active area of research. The fruit/dispersal axis is the cleanest test bed: a small number of fruit syndromes (berry, drupe, samara, capsule, achene, follicle, aril) recur across the angiosperm phylogeny.

**Predictive targets.**
- For each major fruit syndrome and major convergent trait, a *convergence pressure score* derived from hypergraph topology.
- A ranked list of under-sampled lineages predicted to harbor convergent forms not yet documented (e.g. unrecognized myrmecochores in tropical understory genera; suspected C4 lineages flagged for chromatography).
- A formal distinction between *convergence* (independent recurrence) and *homology* (shared inheritance) operationalized from hypergraph topology alone.

**Formal target.** A hypergraph statistic whose value reliably distinguishes convergently-evolved from homologously-inherited traits, validated against canonical cases (C4, succulence, myrmecochory, fleshy-fruit syndromes, elaiosomes, samaras).

**Falsification.** If the statistic is collinear with simple family-size or sampling-density baselines, the contribution is artifactual.

**Parallelism.** Per-trait fan-out across (C4, CAM, succulence, fleshy fruit, drupe, samara, capsule, elaiosome, myrmecochory, carnivory, parasitism, ant-domatia). Each clone runs the convergence-pressure statistic on its assigned trait; canonical-case validation is scored in parallel.

---

## Track 4 — Domestication Hypergraph

**Central question.** Can the full history of plant domestication — wild ancestors, hybridization events, Vavilov centers of origin, selection traits, companion species, geographic spread, breeder pedigrees — be represented as a coherent hypergraph, and does that representation usefully predict crop-substitution choices under climate stress?

**Why this is a breakthrough lane.** Every major crop is a chimera that no taxonomic DAG can express coherently. Bread wheat is a hexaploid hybrid (*Triticum urartu* × *Aegilops speltoides* × *Aegilops tauschii*). Cultivated apple is a mosaic of *Malus sieversii* × *M. sylvestris* × *M. baccata* with introgression history. Cultivated bananas are sterile triploid hybrids of *Musa acuminata* × *M. balbisiana*. Cassava, cotton, peanut, coffee, citrus, brassica — all multi-parent. Vavilov's centers of origin are natural hyperedges. Under climate stress, the practical question is: which crop-wild-relative substitutes the failing variety best? That is a hypergraph query.

**Predictive targets.**
- A queryable **Crop Substitution Engine**: given a failing crop and a target climate envelope, return ranked wild-relative substitutes with mechanistic justification (shared trait, hybridization compatibility, climate match, ethnobotanical precedent).
- A formal **Vavilov-center hypergraph** with confidence levels, accepting that some centers are now contested.
- Predictions of *under-recognized* crop-wild-relative pairs (orphan crops with potential wild substitutes that current breeding programs have not flagged).

**Validation protocol.** Compare the engine's recommendations against expert recommendations from CGIAR/IRRI/CIMMYT, the FAO crop-wild-relative literature, and published climate-resilience breeding programs for a held-out set of crops. Measure agreement at genus and species level. Run an ablation removing the multi-parent edges and check whether a single-parent baseline (sister-species recommender) matches the hypergraph's recommendations.

**Data sources.** Genesys germplasm database, CGIAR genebank data, USDA GRIN, FAO WIEWS and crop-wild-relative inventories, breeder pedigree literature, WorldClim and CHELSA climate envelopes.

**Falsification.** If recommendations are dominated by "use the same genus" — i.e. taxonomic proximity alone explains the gains — the hypergraph adds no value over a simple sister-species recommender. State this and pivot.

**Parallelism.** Per-(crop × climate envelope) fan-out across the crop matrix. Each clone runs the Crop Substitution Engine for one (crop, target-climate) pair; held-out expert recommendations are scored in parallel. The crop matrix is large enough to keep many clones saturated.

---

## Track 5 — Chemodiversity Predictor

**Central question.** Plant secondary metabolites cluster by phylogenetic family and by ecology and by herbivore pressure. Can a typed hypergraph predict where undocumented phytochemistry — alkaloids, terpenes, glycosides, bioactive peptides — is likely to be found, as a drug-discovery and ethnobotany prior?

**Why this is a breakthrough lane.** Only a small fraction of described plants have been screened for bioactives. Phytochemistry shows strong family-level signals (Solanaceae tropane alkaloids, Apocynaceae cardenolides, Brassicaceae glucosinolates, Lamiaceae terpenoids, Asteraceae sesquiterpene lactones) and surprising cross-family convergence (caffeine in *Coffea*, *Camellia*, *Ilex*, *Theobroma*, *Paullinia*; nicotine-related alkaloids across Solanaceae and unrelated families). A hypergraph with phytochemistry, herbivore-defense, and ecological-context layers is a natural drug-discovery prior. This connects to ethnobotany: indigenous medicinal-use records are themselves hypergraph evidence about bioactivity.

**Predictive targets.**
- A ranked list of under-screened taxa with predicted bioactive classes, prioritized by neighborhood completion in the chemodiversity hypergraph.
- A formal "chemodiversity signature" per family / clade / ecological context.
- Recovery of canonical examples under held-out training: would the model have prioritized *Taxus brevifolia* before paclitaxel, *Catharanthus roseus* before vincristine, *Cinchona* before quinine, *Artemisia annua* before artemisinin?

**Validation protocol.** Hold out known phytochemical discoveries with documented isolation dates. Train without those labels. Check whether the model would have ranked those source taxa highly *before* the discovery. Also check ethnobotanical precedence: do indigenous-use records predict subsequent confirmed bioactivity?

**Data sources.** KNApSAcK, NPASS, Dr. Duke's Phytochemical & Ethnobotanical Database, ChEBI, ethnobotanical databases (Native American Ethnobotany DB, PROTA, PROSEA), herbivore-defense literature.

**Falsification.** If predictions cluster on taxa already over-screened (rich-get-richer), or if removing the ecological/herbivore-pressure layer does not degrade performance, the chemistry hyperedges are not doing real work — they are reflecting screening intensity.

**Parallelism.** Per-family fan-out across major chemically-distinct angiosperm families (Solanaceae, Apocynaceae, Brassicaceae, Lamiaceae, Asteraceae, Rubiaceae, Euphorbiaceae, Fabaceae, ...). Each clone scores chemodiversity neighborhood-completion within its family; temporally-frozen held-out discoveries are validated in parallel.

---

## Track 6 — Botanical Foundation Model Probe

**Central question.** Use PhytoGraph as adversarial ground truth to measure where modern AI (LLMs, multimodal models, plant-ID classifiers) hallucinates plant biology — with particular attention to high-stakes failure modes.

**Why this is a breakthrough lane.** Plant identification and edibility/toxicity reasoning are high-stakes: deaths from misidentified *Amanita*, *Conium maculatum*, *Cicuta*, *Datura*, *Aconitum* are real, recurrent, and preventable. Foundation-model botanical knowledge is not rigorously benchmarked. The hypergraph is exactly the substrate for an adversarial probe. This connects to the rapidly-growing scientific-LLM evaluation literature.

**Probe categories.**
- **Synonym confusion** — rephrase a question using a deprecated synonym; measure the model's stability across synonym variants.
- **Toxicity look-alikes** — present visual or textual descriptions of dangerous look-alike pairs (*Amanita* vs. *Agaricus*, *Conium maculatum* vs. wild carrot, *Phytolacca* vs. blueberry, *Veratrum* vs. *Allium*); measure error rate and confidence calibration.
- **Hybrid pedigree** — ask the model to identify the parents of a known polyploid or hybrid crop; measure correctness.
- **Region-conditional knowledge** — ask about a plant's status (native, naturalized, invasive, cultivated) in a specific region; measure factual accuracy.
- **Ghost-partner reasoning** — ask whether a fruit's modern dispersal pattern fits its morphology; check awareness of anachronism literature.
- **Convergence detection** — present two morphologically-similar fruits from distant families and ask whether they are related; check for shape-based hallucination of phylogenetic closeness.
- **Phytochemistry safety** — ask about safe vs. unsafe parts of edible-but-partly-toxic plants (rhubarb leaves, elderberry seeds, cassava preparation, ackee unripe arils).

**Validation protocol.** Score free/open-source or already-local models and classifiers against the probe. Paid, pay-as-you-go, or key-gated provider APIs are out of scope for this run. If no suitable local/open-weight model is available, build the static benchmark, deterministic scoring harness, and public-data evaluation protocol without executing model calls. For each error class, report rate, confidence calibration, and whether the model recovers under alternative prompt templates.

**Formal target.** A taxonomy of botanical hallucination failure modes, with measurable per-mode error rates and a public adversarial test set.

**Falsification.** If foundation models score near ceiling on the probe, the probe is too easy — harden by drawing from the hypergraph's hardest cases (rare polyploids, region-specific synonymy, deep ethnobotanical literature).

**Parallelism.** Maximally parallel: per-(local/open model or classifier × probe-category × question-batch) fan-out. The (model × category) matrix is the outer fan-out; per-question batching is the inner fan-out. The binding constraints are local compute, public data quality, and benchmark design, not paid API quota.

---

## Unified Hypergraph Substrate

All six tracks share one typed hypergraph:

```text
H = (V, E, τ_V, τ_E, W, P, C, T)
```

Where:

- `V` are typed nodes;
- `E` are typed hyperedges;
- `τ_V` maps nodes to node types;
- `τ_E` maps hyperedges to relation/evidence types;
- `W` gives weights, confidence, and source reliability;
- `P` stores provenance, license, access date, and source record identifiers;
- `C` stores caveats — uncertainty, source conflict, missing data, allowed evidence scope;
- `T` stores temporal annotation where relevant (cultivation start date, extinction date, isolation date for phytochemicals, hybridization event timing).

### Node types

Carrying forward from prior schema with track-driven additions in **bold**:

- taxon; accepted name; synonym; common name; rank; family/genus/species/infraspecific unit;
- fruit type; plant life form; trait;
- region; native-origin area; introduced/naturalized area; habitat;
- animal consumer/disperser; **animal pollinator**; **mycorrhizal partner**; **herbivore**; **extinct fauna node**;
- human-use category; edibility status; toxicity/preparation caveat; cultivation/domestication status;
- **wild ancestor**; **cultivar**; **landrace**; **breeder pedigree node**; **Vavilov center**;
- **phytochemical compound**; **chemical class**; **bioactivity class**; **ethnobotanical use record**;
- image/media; source; story/narrative note;
- conservation status; phylogenetic/clade context;
- **chromosome count / ploidy state**; **hybridization event**; **polyploidization event**;
- **paleoclimate / paleoecology context**;
- **adversarial probe question / probe ground truth / foundation-model response**.

### Hyperedge types

Carrying forward with track-driven additions in **bold**:

- `taxonomic_parentage`
- `synonym_cluster`
- `common_name_assertion`
- `fruit_morphology`
- `life_form`
- `native_origin`
- `distribution`
- `introduced_or_invasive_status`
- `habitat_association`
- `animal_consumption_or_dispersal`
- **`pollination_partnership`**
- **`mycorrhizal_partnership`**
- **`herbivore_defense_relationship`**
- `human_use`
- `edibility_status`
- `toxicity_or_preparation_caveat`
- `cultivation_or_domestication`
- **`crop_pedigree`** (multi-parent: wild ancestor(s) + cultivar + selection trait(s) + region + time)
- **`vavilov_center_hyperedge`**
- **`hybridization_event`**
- **`polyploidization_event`**
- **`reticulate_inheritance_evidence`**
- **`phytochemical_assertion`** (taxon + compound + plant part + concentration + source)
- **`chemodiversity_signature`** (clade + compound class + ecological context + herbivore pressure)
- **`ethnobotanical_use_assertion`** (taxon + people/region + use + source)
- **`convergence_signature`** (trait + taxa-set spanning distant lineages)
- **`anachronism_candidate_edge`** (fruit + extinct fauna + paleo context + modern recruitment failure)
- **`adversarial_probe_edge`** (question + correct answer + foundation-model response set + error type)
- `image_evidence`
- `source_assertion`
- `story_or_cultural_note`
- `taxonomic_conflict`
- `phylogenetic_or_reticulate_context`
- `metadata_missingness`

Every hyperedge must declare what it is allowed to support. A `phytochemical_assertion` from a single 1960s paper supports "compound has been detected in this taxon" but not "compound is taxon-typical." A `crop_pedigree` from a breeder catalog supports the named cross but not the dating. A `convergence_signature` supports topological clustering but not adaptive interpretation without independent ecological evidence. An `image_edge` supports media display and possibly weak morphology inspection, but does not prove distribution, edibility, or taxonomy. An `ethnobotanical_use_assertion` supports a human-use claim but does not by itself support a clinical-bioactivity claim.

## Required Conceptual Distinctions

Do not collapse these layers (carrying forward from prior framings, expanded):

- **Taxonomy** vs **Phylogeny** vs **Reticulate inheritance** — the third is now a first-class object, not an edge case.
- **Trait similarity (homology)** vs **convergence (independent recurrence)** — Track 3 depends on this distinction being machine-computable.
- **Fruit morphology** (botanical structure) vs **fruit syndrome** (ecological/coevolutionary pattern).
- **Distribution layers** — native vs. introduced vs. naturalized vs. cultivated. Never conflate.
- **Human use** vs **edibility** vs **toxicity** vs **cultural narrative**. Track 6 depends on this being clean.
- **Wild ancestor** vs **landrace** vs **cultivar** vs **modern variety**. Track 4 depends on this being clean.
- **Phytochemical detection** vs **typical concentration** vs **bioactivity in vitro** vs **clinical efficacy**. Track 5 depends on this being clean.
- **Ethnobotanical use** as evidence about human-plant interaction, which may correlate with bioactivity but does not by itself prove biological mechanism.
- **Media** as evidence of appearance but not biology unless independently supported.

Claims about biological novelty must be avoided unless supported by authoritative sources, or explicitly flagged as model-generated predictions awaiting validation.

## Data Sources

The campaign should investigate and use:

**Taxonomic backbone:** World Flora Online / WFO Plant List; GBIF taxonomy; Open Tree of Life; Plants of the World Online (POWO/Kew); Tropicos.

**Occurrence and distribution:** GBIF; iNaturalist research-grade; BIEN/RBIEN where local R tooling is feasible.

**Phylogeny and reticulation (Track 1):** Open Tree of Life; CCDB (Chromosome Counts Database); Plant DNA C-values database; curated extraction of published polyploid and hybridization records from systematic botany literature.

**Paleobotany and extinctions (Track 2):** PBDB (Paleobiology Database); Late Quaternary Extinctions database; megafauna range reconstructions (Faurby & Svenning and successors); modern dispersal-failure literature; IUCN fauna data for current dispersers.

**Convergence baselines (Track 3):** published fruit-syndrome codings; C4 lineage lists (Sage and successors); succulence lists; myrmecochory lists; elaiosome lists; samara lists.

**Crops and germplasm (Track 4):** Genesys; CGIAR genebank data; USDA GRIN; FAO WIEWS and crop-wild-relative inventories; breeder pedigree literature.

**Climate (Track 4):** WorldClim; CHELSA.

**Phytochemistry and ethnobotany (Track 5):** KNApSAcK; NPASS; Dr. Duke's Phytochemical and Ethnobotanical Database; ChEBI; Native American Ethnobotany Database; PROTA; PROSEA.

**Foundation-model probe resources (Track 6):** free/open-source or already-local models, public benchmark artifacts, deterministic scoring scripts, public datasets, and license-respecting offline/local plant-ID resources where available. Do not use paid, pay-as-you-go, or key-gated provider APIs for this run.

**Media:** Wikimedia Commons; GBIF media; iNaturalist (license-respecting).

The run must produce `data_source_audit.md` documenting source, purpose, license, access mode, reliability, known bias, bulk-scale support, and **which track(s) the source serves**.

## Access And Tooling Constraints

The campaign should not be blocked by authentication.

Expected low-friction path:
- WFO public taxonomy/name data;
- GBIF read APIs (species/taxon lookup, occurrence/media samples);
- Open Tree public APIs;
- Wikidata SPARQL and Wikimedia Commons metadata;
- CCDB, KNApSAcK, NPASS, PBDB — often static downloads;
- foundation-model API access through standard SDK clients.

Likely access limits:
- GBIF bulk occurrence downloads may require an account;
- TRY may require registration; treat as optional;
- some image sources have license constraints;
- Kew/POWO content for reference, not aggressive scraping;
- foundation-model API calls have cost and rate limits — batch carefully.

Recommended local stack:

- Python 3.11+ or 3.12+;
- `pandas`, `polars`, `pyarrow`, `numpy`, `scipy`;
- `requests` or `httpx`;
- `networkx`; `hypernetx` or `xgi` for hypergraph utilities; or a custom typed incidence-matrix layer;
- `scikit-learn`;
- `pytest`;
- `sqlite`, `duckdb`, or parquet for local storage;
- `matplotlib`, `seaborn`, `plotly`;
- `anthropic` and `openai` SDK clients for Track 6;
- a lightweight LLM evaluation harness for Track 6 (custom or based on existing eval frameworks);
- website stack for the Atlas: Vite + React/Svelte, or static HTML with D3/Cytoscape.js/Sigma.js;
- optional R: `rgbif`, `RBIEN`, `WorldFlora`;
- optional Wolfram for exact finite examples, symbolic diagnostics, and theorem/counterexample work (Tracks 1, 3).

Wolfram is not required for data ingestion. Use it only when it materially helps with formal diagnostics.

## Scale And Coverage Tiers

The campaign must define inclusion operationally and auditably. Suggested tiers, with track-specific overlays:

- **Tier 0 (substrate, target 50,000–100,000+ taxa):** sparse taxonomy-backed angiosperm taxa. Required substrate for Tracks 1, 3, 5.
- **Tier 1 (target ≥10,000 taxa):** taxa with fruit evidence and at least one cross-cutting metadata field. Required for Tracks 2, 3.
- **Tier 2 (target ≥1,000 taxa):** crop and crop-wild-relative taxa with pedigree, Vavilov-center, and climate data. Required for Track 4.
- **Tier 3 (target ≥1,000 taxa):** taxa with phytochemical assertions. Required for Track 5.
- **Tier 4 (target ≥200 taxa):** deeply enriched taxa with reticulation evidence, ghost-partner candidacy, convergence-signature membership, or adversarial-probe ground truth. Required for Tracks 1, 2, 3, 6.

If the run cannot reach Tier 0 ≥ 50,000, document the blocker and continue with what scale allows. Per-track minimum viable scales must be stated at Phase 1.

## Parallelism and Fan-Out Strategy

This campaign is structured for aggressive parallel fan-out wherever the dependency graph permits. Long-exposure clones should run concurrently on independent sub-tasks; barrier synchronization points are explicitly marked. The default posture is **parallel-by-default**: if two sub-tasks share no read-after-write dependency on the same artifact, they should run as concurrent clones.

### Top-level dependency graph

```text
[BARRIER 0] Phase 1 — scope, schema, source audit (single coordinator)
   ↓
[FAN-OUT A] Phase 2 — substrate ingestion (one clone per source)
   ↓
[BARRIER 1] substrate join, synonym normalization, schema conformance
   ↓
[FAN-OUT B] Phase 3 — track enrichment (6 clones, one per track)
   ↓
[BARRIER 2] cross-track schema conformance + duplicate-edge resolution
   ↓
[FAN-OUT C] Phase 4 — predictive instruments (6 clones) ∥
[FAN-OUT C′] Phase 5 — Botanical Atlas (1+ clones, concurrent)
   ↓
[BARRIER 3] instrument ↔ atlas integration
   ↓
[FAN-OUT D] Phase 6 — validation (6 clones, each fanned further) ∥
[FAN-OUT D′] Phase 7 — formal contributions (≥3 clones) ∥
[FAN-OUT D″] Phase 8 — ablations (N clones, see below)
   ↓
[BARRIER 4] cross-track synthesis, prediction-ledger reconciliation
   ↓
Phase 9 — final synthesis (single coordinator)
```

### Source-level fan-out (Phase 2)

Substrate ingestion is independent per source. Spawn at least one clone per source group:

- WFO taxonomy / Open Tree / POWO / GBIF taxonomy backbone (taxonomic crosswalks may need a barrier among themselves before joining the rest)
- GBIF occurrence/media samples
- CCDB + Plant DNA C-values + curated polyploid records (Track 1)
- PBDB + Late Quaternary Extinctions + megafauna ranges + Faurby & Svenning (Track 2)
- Fruit-syndrome / C4 / succulence / myrmecochory codings (Track 3)
- Genesys + USDA GRIN + FAO CWR + WorldClim/CHELSA (Track 4)
- KNApSAcK + NPASS + Duke + ChEBI + ethnobotanical DBs (Track 5)
- Free/open-source offline foundation-model probe harness scaffolding (Track 6)
- Wikidata SPARQL + Wikimedia Commons media metadata

Clones must write to per-source staging tables, not the shared substrate, until Barrier 1.

### Track-level fan-out (Phase 3 onwards)

The six tracks are intentionally designed for concurrent execution. After Barrier 1 they share only the substrate (read-only) and the schema (frozen). Track clones write only to their own track namespace until Barrier 4.

### Within-track fan-out

Each track is itself fan-out-friendly. Track-specific fan-out axes:

- **Track 1 (Reticulation):** per-clade — fan out across major angiosperm orders or families; each clone computes the local reticulation index.
- **Track 2 (Ghost Hyperedges):** per-candidate-syndrome — fan out across candidate anachronism classes (large-seeded neotropical Fabaceae, palm-fruit anachronisms, large-fruited Annonaceae, ghost-pollinator Orchidaceae candidates, etc.).
- **Track 3 (Convergence):** per-trait — fan out across (C4, CAM, succulence, fleshy-fruit, samara, elaiosome, myrmecochory, carnivory, ...); each clone scores convergence pressure on its trait.
- **Track 4 (Domestication):** per-(crop × climate envelope) — fan out across the crop matrix; each clone runs the substitution engine for one crop under one climate scenario.
- **Track 5 (Chemodiversity):** per-family — fan out across major chemically-distinct angiosperm families; each clone predicts neighborhood-completion for its family.
- **Track 6 (Foundation Model Probe):** per-(model × probe category) — fan out across the (model × category) matrix; further fan-out per probe-question batch. This is the most embarrassingly parallel track.

### Validation fan-out (Phase 6)

Validation is per-prediction. Each track's validation work fans out across its held-out set:

- Track 1: per held-out polyploid lineage
- Track 2: per held-out anachronism candidate
- Track 3: per held-out convergence case
- Track 4: per held-out crop × expert-recommendation pair
- Track 5: per held-out phytochemical discovery × frozen-time-cutoff
- Track 6: per (model × probe category × question) — already maximally parallel

### Ablation fan-out (Phase 8)

Ablations are independent experiments. Each ablation is its own clone:

- per-track edge-removal ablations (e.g. remove `polyploidization_event` → re-run Track 1)
- per-source ablations (e.g. remove all Wikidata-derived edges → re-run all tracks)
- per-confounder controls (source density, image availability, crop popularity, family size, synonym-cluster size, screening intensity)
- cross-track contamination tests (remove Track 4 edges from Track 5 input, etc.)

A single ablation matrix coordinator schedules the experiments; results report back to a shared ablation table.

### Formal contributions fan-out (Phase 7)

Formal targets are independent across tracks. Spawn one clone per theorem/counterexample/diagnostic. Wolfram-using clones (exact finite examples) run independently from prose-proof clones.

### Barrier discipline

Barriers enforce: (a) schema conformance, (b) provenance/license uniformity, (c) prediction-ledger consistency, (d) deduplication of cross-track hyperedges that name the same underlying biological fact.

- **Barrier 0:** schema and source-audit must be agreed before any ingestion.
- **Barrier 1:** all source clones must agree on taxonomic crosswalk + synonym normalization before track enrichment.
- **Barrier 2:** all track enrichment clones must conform to the unified hyperedge schema before instrument construction.
- **Barrier 3:** instruments must be queryable from the Atlas before validation runs use the Atlas as a researcher-facing surface.
- **Barrier 4:** all prediction sub-ledgers consolidate into the single `prediction_ledger.tsv`.

A clone that violates schema at a barrier blocks the merge. A coordinator clone reconciles or returns it for revision. Use `barrier_preempt_timeout_seconds` to bound waits; preempt a stuck clone rather than blocking the wave.

### What must NOT run in parallel

- The unified schema must be agreed once and not forked. Schema changes require a coordinator and a new barrier.
- The prediction ledger is a single source of truth. Per-track sub-ledgers feed in; never let two clones write to the master ledger concurrently without a reconciliation step.
- License and provenance conventions must be uniform — never let a clone invent its own provenance format.
- Synonym normalization is a substrate-level concern; do not let each track re-normalize separately, or downstream cross-track joins will break.

### Failure modes specific to parallel execution

- **Schema drift across clones** — surface at Barrier 2 with a conformance check, do not allow it to leak to Phase 4.
- **Duplicate hyperedges from overlapping sources** — Barrier 1 must deduplicate against a canonical key (taxon-ID + edge-type + supporting-source-set).
- **Cross-track contamination** — a clone in Track 5 should not read from Track 4's in-progress predictions; only from the frozen substrate. Enforce read-only mounts where possible.
- **Stragglers** — one slow clone (e.g. a track with a hard-to-reach data source) should not block the whole wave. Allow late-arrival merge into a subsequent barrier with a documented gap.

## Phase Plan

### Phase 1 — Scope, schema, and source audit  `[BARRIER 0 — single coordinator]`

- Track-by-track scoping documents stating predictive targets, validation protocols, and per-track minimum viable scales.
- Unified hypergraph schema with all node and edge types.
- `data_source_audit.md` with track assignments.
- Risk register covering image licensing, source bias, false biological inference, foundation-model API cost, paleobotany interpretation risk, ethnobotanical sensitivity.
- **Output gate:** schema frozen; no downstream phase may modify it without a new barrier.

### Phase 2 — Substrate ingestion  `[FAN-OUT A — one clone per source]`

- Reproducible ingestion for WFO, GBIF, Open Tree, Wikidata/Commons, CCDB, Genesys, paleobotany sources, phytochemistry databases.
- Each clone writes to per-source staging tables, not the shared substrate.
- Synonym normalization with documented coverage.
- Taxon identifier crosswalks.
- Image/media metadata where used.
- Provenance, license, and access-date capture for every record.
- Incremental build scripts, validation tests per source.
- Target Tier 0 scale.
- **Barrier 1:** join staging tables, deduplicate against canonical keys, finalize taxonomic crosswalk + synonym normalization for downstream tracks.

### Phase 3 — Track-specific enrichment  `[FAN-OUT B — 6 track clones, each fanned further per its own axis]`

Six parallel tracks; each track may further fan out internally (see per-track "Parallelism" notes):

- 3.1 **Reticulation enrichment** — CCDB, polyploid records, hybridization records, cultivar pedigrees. *Inner fan-out: per-clade.*
- 3.2 **Ghost-partner enrichment** — paleobotany, megafauna ranges, modern dispersal-failure literature, IUCN fauna data, curated Janzen-Martin candidate lists. *Inner fan-out: per-candidate-class.*
- 3.3 **Convergence enrichment** — fruit-syndrome coding, C4 lineage lists, succulence lists, myrmecochory lists, elaiosome lists. *Inner fan-out: per-trait.*
- 3.4 **Domestication enrichment** — Genesys, FAO CWR, breeder pedigrees, climate envelopes. *Inner fan-out: per-(crop × climate).*
- 3.5 **Chemodiversity enrichment** — KNApSAcK, NPASS, Duke, ethnobotanical databases. *Inner fan-out: per-family.*
- 3.6 **Adversarial-probe construction** — question set, ground-truth from PhytoGraph, model-response harness. *Inner fan-out: per-(model × category).*

Each track writes only to its own track namespace; no cross-track writes.

- **Barrier 2:** cross-track schema conformance check; resolve duplicate hyperedges that name the same underlying biological fact across tracks.

### Phase 4 — Predictive instruments  `[FAN-OUT C — 6 clones, concurrent with Phase 5]`

For each track, build the predictive instrument as an independent clone:

- 4.1 Tree-compatibility index + reticulation hotspot detector.
- 4.2 Ghost-partner candidate ranker.
- 4.3 Convergence-pressure statistic.
- 4.4 Crop Substitution Engine.
- 4.5 Chemodiversity neighborhood-completion predictor.
- 4.6 Foundation-model probe runner.

Instruments read from the frozen substrate + their own track's enrichment; they do not depend on the Atlas.

### Phase 5 — The Botanical Atlas  `[FAN-OUT C′ — concurrent with Phase 4]`

Build the local interactive site as a **window into the predictions**, not as the headline. The Atlas must support:

- fast search over taxa, synonyms, and common names;
- plant detail pages exposing per-track predictions (reticulation index, ghost-partner status, convergence neighborhood, crop-substitute candidates, predicted phytochemistry, foundation-model failure record on this taxon);
- a sharp visual distinction between observed evidence and model predictions;
- provenance badges, source links, license attribution;
- missing-data indicators;
- taxonomic breadcrumb and hypergraph neighborhood comparison;
- image/media display with license and attribution where used;
- filters by family, region, life form, fruit type, ploidy, anachronism candidacy, chemodiversity neighborhood, crop status, probe failure mode;
- export of local hypergraph neighborhoods;
- a mechanism for a researcher to file a counter-claim or correction against a prediction;
- performance suitable for ≥ 10,000 taxa locally, with a design path to 100,000.

The Atlas is a research instrument. It is usable by a researcher without reading source code, and it exposes uncertainty rather than hiding it.

- **Barrier 3:** instruments queryable from Atlas; Atlas exposes per-track predictions with provenance and prediction-vs-evidence distinction.

### Phase 6 — Predictive validation  `[FAN-OUT D — 6 track clones, each further fanned per held-out case]`

For each track, run the held-out validation protocol described above. Score the predictions. Maintain a per-track prediction ledger with status: `validated`, `falsified`, `pending`, `data-limited`, `superseded`.

Within each track, validation is per-prediction: spawn a clone per held-out case (per polyploid lineage, per anachronism candidate, per convergence case, per crop, per phytochemical discovery, per (model × question)). These are independent — saturate.

### Phase 7 — Formal contributions  `[FAN-OUT D′ — ≥3 clones, concurrent with Phase 6]`

At least one formal contribution per track is targeted. Minimum total: three formal contributions (theorem template, counterexample, diagnostic statistic with proof of properties, or algorithm with proof of correctness/safety).

Formal targets are independent: spawn one clone per theorem/counterexample/diagnostic. Wolfram-using clones (exact finite examples) run independently from prose-proof clones. Each clone owns its own proof artifact.

Wolfram may be used for exact finite examples, but every formal result must also be described in ordinary mathematical prose.

### Phase 8 — Stress tests, ablations, falsification  `[FAN-OUT D″ — N ablation clones, concurrent with Phases 6 and 7]`

Ablations are independent experiments. Spawn one clone per ablation; results report to a shared ablation table. The ablation matrix coordinator schedules; clones execute.

Per-track ablations (as described in each track) plus cross-track ablations:

- remove reticulation edges → does Track 4 (crop substitution) degrade?
- remove phytochemistry edges → does Track 5 collapse?
- remove paleobotany edges → does Track 2 still work?
- shuffle source provenance → does any apparent biological signal collapse into a source-density signal?
- downsample popular crop taxa, image-rich taxa, well-screened taxa → which tracks are robust?
- stratify by family size and region → where are the gains real vs. confound-driven?

Explicit cross-cutting failure modes to test:

- whether per-track predictions are dominated by source density;
- whether image availability drives any reported centrality or salience;
- whether crop popularity dominates substitution recommendations;
- whether synonym normalization explains apparent diversity;
- whether pairwise-graph baselines capture all useful signal in any track;
- whether taxonomy-only DAGs are sufficient for core navigation;
- whether foundation-model probe results are dominated by prompt-template effects rather than knowledge gaps.

- **Barrier 4:** consolidate all per-track and ablation results into the single `prediction_ledger.tsv`; reconcile statuses (`validated` / `falsified` / `data-limited` / `superseded`).

### Phase 9 — Final synthesis  `[BARRIER 5 — single coordinator]`

A final report stating, per track:

- the predictions made;
- the predictions validated;
- the predictions falsified;
- the data-limited cases;
- the formal contribution;
- the open questions;
- what would be required for a publishable paper in the track's home venue (evolutionary biology, crop science, phytochemistry, ML evaluation).

## Predictive Validation Protocol

Every prediction is filed as a row in `prediction_ledger.tsv` with columns:

- track;
- prediction statement;
- supporting hyperedges and node-set;
- expected validation source;
- status (`pending`, `validated`, `falsified`, `data-limited`, `superseded`);
- ablation sensitivity (which hyperedge classes, if removed, change the prediction);
- date filed, date resolved.

A prediction that cannot be assigned a validation source is not a prediction; it is speculation, and must be filed in `speculation_ledger.tsv` instead.

Every insight from any track must be classified:

- validated;
- plausible;
- speculative;
- source-biased;
- data-limited;
- falsified by ablation;
- atlas/narrative-only.

## Required Final Deliverables

1. `phytograph_schema.md`
2. `data_source_audit.md`
3. `coverage_report.md`
4. `phytograph_dataset/` — the typed hypergraph itself, with provenance
5. `botanical_atlas_site/` and `atlas_runbook.md`
6. Per-track instruments and ledgers:
   - `track1_reticulation_atlas.md` + `reticulation_predictions.tsv`
   - `track2_ghost_hyperedges.md` + `ghost_partner_predictions.tsv`
   - `track3_convergence_pressure.md` + `convergence_predictions.tsv`
   - `track4_domestication_hypergraph.md` + `crop_substitution_predictions.tsv`
   - `track5_chemodiversity.md` + `phytochemistry_predictions.tsv`
   - `track6_foundation_model_probe.md` + `probe_results.tsv`
7. `formal_contributions.md` — theorem templates, counterexamples, diagnostic statistics, algorithm proofs
8. `falsification_and_ablation_report.md`
9. `prediction_ledger.tsv` (cross-track) and `speculation_ledger.tsv` (cross-track)
10. `research_contribution_ledger.md` — every artifact, classified
11. `final_report.md`
12. `audit_report.md`
13. Reproducible code, tests, build scripts.

## Atlas Success Criteria

The Atlas succeeds only if a local researcher can:

- search by accepted name, synonym, or common name;
- browse ≥ 10,000 indexed taxa;
- inspect plant pages exposing per-track predictions, observed evidence, and provenance;
- see images where available with attribution;
- compare taxonomic relatives, hypergraph neighbors, and per-track predicted neighbors;
- navigate by family, genus, region, life form, fruit type, ploidy, anachronism candidacy, chemodiversity neighborhood, crop status, probe failure mode;
- understand whether a field is observed, inferred, predicted, or missing;
- export a taxon's local neighborhood;
- file a counter-claim or correction against a prediction;
- use the interface without reading source code.

## Research Success Criteria

The campaign succeeds if it produces, at minimum:

- A scale-50,000+ angiosperm hypergraph with provenance.
- **At least one validated prediction per track**, with validation source and protocol documented.
- At least three formal contributions across the six tracks (theorem template, counterexample, diagnostic statistic, or algorithm with proof).
- A usable Botanical Atlas exposing predictions to researchers.
- A foundation-model probe with publishable results (Track 6).
- An honest accounting of which predictions were falsified by ablation or held-out validation.

The campaign fails if it produces only:

- A polished but predictively empty catalog;
- A wiki integrating known facts without generating new claims;
- A "hypergraph vs DAG" benchmark with no biological consequence;
- Speculative claims unsupported by validation sources;
- A track that produces predictions but never tries to validate them;
- An attractive visualization without per-track predictions and ablations.

## Guardrails

- Predictions are predictions, not facts. Validated predictions are validated, not facts beyond the validation source.
- Do not claim new taxonomy, new edibility, new native range, new ecological interaction, new hybridization, new anachronism, or new bioactivity as established truth without authoritative evidence. Mark all model-generated claims as predictions.
- Do not conflate native origin with current distribution.
- Do not treat image availability as biological importance.
- Do not treat Wikidata or LLM-knowledge coverage as real-world salience without bias checks.
- Do not scrape aggressively when APIs, dumps, or documented downloads are available. Respect licenses.
- Respect foundation-model API terms; rate-limit and batch.
- Preserve source identifiers and access dates for every record.
- Mark all inferred fields as inferred; mark all predicted fields as predicted.
- Prefer explicit negative results over weak claims.
- Foundation-model probe results identify failure modes, not vendor inadequacy; phrase findings accordingly.
- Ethnobotanical data must be handled with attention to indigenous data sovereignty and source attribution; do not strip provenance from traditional knowledge records.
- Anachronism and reticulation claims must be flagged as model-derived hypotheses, not established biological history, unless the underlying paleobotany or hybridization record is itself authoritative.

## Initial Hypotheses

H1 (Track 1). A computable reticulation index will recover canonical polyploid and hybrid lineages without supervision, and will surface non-trivial reticulation density in under-studied tropical clades.

H2 (Track 2). A non-trivial fraction (≥ 30%) of canonical Janzen-Martin anachronism candidates will be recovered by hypergraph-hole-finding. The model will also propose plausible new anachronism candidates in under-studied paleotropical lineages.

H3 (Track 3). A hypergraph convergence statistic will rank fruit-syndrome convergence above family-size and sampling-density confounds, validating the Phase 4.3 instrument.

H4 (Track 4). Crop-substitution recommendations will agree with CGIAR-class expert recommendations at genus level on ≥ 60% of held-out cases, and the hypergraph will outperform a simple sister-species baseline by a measurable margin.

H5 (Track 5). Chemodiversity neighborhood-completion will rank known phytochemical-source taxa (e.g. *Taxus*, *Catharanthus*, *Cinchona*, *Artemisia annua*) in the top decile of their family *before* their discovery date, when run on temporally-frozen training data.

H6 (Track 6). Foundation models will exhibit systematic, measurable failure modes on synonym confusion, hybrid pedigree, and region-conditional questions. Failure rate on toxicity look-alikes will be high enough to be policy-relevant.

H7 (cross-cutting). Some apparent contributions will collapse under control for source density, image availability, crop popularity, family size, and Wikidata coverage. Those collapses are themselves contributions and must be reported as such.

H8 (cross-cutting). Synonym normalization will substantially change apparent taxon diversity, centrality, and probe error rates.

H9 (cross-cutting). The strongest durable contribution may be the combination of unified hypergraph substrate plus six predictive instruments plus rigorous cross-track ablations, even if any individual track's headline predictions are partly falsified.

## Suggested Milestones (wave structure)

Milestones are organized into **waves**. Within a wave, items are independent and should run as concurrent clones. Between waves, a barrier enforces consistency.

### Wave 0 — coordinator only `[BARRIER 0]`

- **M0.1** Track-by-track scoping documents, unified schema, data-source audit; schema frozen.

### Wave 1 — substrate ingestion `[FAN-OUT A, one clone per source group]`

Run concurrently:

- **M1.1** WFO + Open Tree + POWO + GBIF taxonomy backbone (with internal sub-barrier for crosswalk)
- **M1.2** GBIF occurrence/media samples
- **M1.3** CCDB + Plant DNA C-values + curated polyploid records
- **M1.4** PBDB + Late Quaternary Extinctions + megafauna ranges
- **M1.5** Fruit-syndrome / C4 / succulence / myrmecochory codings
- **M1.6** Genesys + USDA GRIN + FAO CWR + WorldClim/CHELSA
- **M1.7** KNApSAcK + NPASS + Duke + ChEBI + ethnobotanical DBs
- **M1.8** Free/open-source offline foundation-model probe harness scaffolding
- **M1.9** Wikidata / Wikimedia Commons metadata

`[BARRIER 1]` Substrate join, synonym normalization, deduplication, Tier 0 ≥ 50,000 taxa confirmed.

### Wave 2 — track enrichment `[FAN-OUT B, 6 track clones, each with inner fan-out]`

Run concurrently across the six tracks:

- **M2.T1** Reticulation enrichment (inner fan-out per clade)
- **M2.T2** Ghost-partner enrichment (inner fan-out per candidate class)
- **M2.T3** Convergence enrichment (inner fan-out per trait)
- **M2.T4** Domestication enrichment (inner fan-out per crop × climate)
- **M2.T5** Chemodiversity enrichment (inner fan-out per family)
- **M2.T6** Adversarial-probe construction (inner fan-out per model × category)

`[BARRIER 2]` Cross-track schema conformance; duplicate-edge resolution.

### Wave 3 — predictive instruments + Atlas `[FAN-OUT C and C′, concurrent]`

Run concurrently:

- **M3.T1** Tree-compatibility index + reticulation hotspot detector
- **M3.T2** Ghost-Partner Candidate Ranker
- **M3.T3** Convergence-Pressure statistic
- **M3.T4** Crop Substitution Engine
- **M3.T5** Chemodiversity neighborhood-completion predictor
- **M3.T6** Free/open-source offline foundation-model probe runner
- **M3.A** Botanical Atlas (local interactive site)

`[BARRIER 3]` Instruments queryable from Atlas; prediction-vs-evidence distinction enforced.

### Wave 4 — validation + formal contributions + ablations `[FAN-OUT D, D′, D″, all concurrent]`

Run concurrently:

- **M4.V1–V6** Per-track validation runs (each track further fans out per held-out case)
- **M4.F1–F≥3** Formal contributions (one clone per theorem/counterexample/diagnostic)
- **M4.A1–An** Ablation matrix (one clone per ablation experiment, both per-track and cross-track)

This wave is the largest fan-out in the campaign. Saturate clones across all three families of experiments simultaneously. Stragglers (e.g. ablations requiring re-ingestion) may merge into a documented late-arrival slot rather than blocking the whole wave.

`[BARRIER 4]` Consolidate all results into `prediction_ledger.tsv`; reconcile statuses; close out speculation ledger.

### Wave 5 — final synthesis `[BARRIER 5, single coordinator]`

- **M5.1** Final report, prediction ledger, contribution ledger, audit report.

### Critical-path note

Wave 0 → Wave 1 first-source-completion → Wave 2 track-start is the critical path for time-to-first-prediction. Tracks 1, 3, 5 depend on the substrate join only; they can start enrichment as soon as Barrier 1 clears. Tracks 2, 4 also depend on their specialty sources (PBDB / Genesys); ingest these in parallel from Wave 1 so they are not the bottleneck. Track 6 can start probe-question drafting in Wave 1 against the still-being-ingested substrate, since its harness is independent of which taxa are present.

### Failure-recovery posture

A stuck clone at any barrier should be preempted (`barrier_preempt_timeout_seconds`) rather than allowed to block the wave. The wave proceeds with a documented gap; the missing clone's contribution merges into the next barrier with status `data-limited` or is retried in a side wave.
