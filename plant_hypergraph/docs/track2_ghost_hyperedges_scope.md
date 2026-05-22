<!--
created: 2026-05-17T15:50:00Z
cycle: 1
run_id: run-phytograph-cycle1
agent: worker
milestone: M0.1
track: 2
-->

# Track 2 — Ghost Hyperedges: Scoping

## (a) Central question

Can lost coevolutionary partnerships — anachronistic fruits, ghost pollinators, extinct dispersers, lost mycorrhizal partners — be recovered from holes in the modern hypergraph?

## (b) Predictive targets (concrete, falsifiable)

1. **Ranked ledger of candidate anachronistic fruits.** Per candidate: fruit morphology (mass, hard endocarp, retention time), modern dispersal-failure signature, biogeographic overlap with Late-Pleistocene megafauna, extinction-timing window.
2. **Held-out canon recovery.** Holding out canonical Janzen-Martin cases — *Persea americana* (avocado), *Maclura pomifera* (osage orange), *Gleditsia triacanthos* (honey locust), large-fruited Annonaceae (*Annona cherimola*, *Annona muricata*), *Mauritia flexuosa*, *Spondias* spp., *Sideroxylon* spp., *Asimina triloba* — at least **30%** appear in top 100 of the ranker (per directive H2).
3. **Ghost-pollinator candidates.** Flowers whose morphology demands a pollinator absent from the current fauna. Filed as predictions.
4. **Ghost-mycorrhizal candidates.** Plants whose current fungal partnerships look geographically narrow and post-glacial-relict-shaped. Filed as predictions.

## (c) Formal target (mathematical object)

A hyperedge-completion inference rule:

Given a fruit-morphology hyperedge `e_fruit` whose `fruit_type` ∈ {large-drupe, hard-endocarp, mass>200g, ...}, no extant `animal_consumption_or_dispersal` edge incident on the same `taxon` adequate to disperse `e_fruit`, and at least one `extinct_fauna` node with paleo-range overlapping the `taxon`'s native range,

infer `anachronism_candidate_edge(taxon, fruit_type, {extinct_fauna_set}, paleo_context, recruitment_failure_source)`.

Proposition (to be proven in M4.F): under a stated coevolutionary prior (fruit syndrome is conditionally independent of modern fauna given its evolutionary partner; partner is from the union of extant + Pleistocene fauna), the rule correctly identifies anachronistic syndromes with bounded false-positive rate `δ` controlled by the strength of the recruitment-failure evidence.

## (d) Data sources required

- PBDB (paleobotany)
- Late Quaternary Extinctions database
- Faurby & Svenning megafauna range reconstructions
- IUCN fauna for extant dispersers (to distinguish "ghost megafauna" from "still-extant elephants/tapirs")
- Modern dispersal-failure literature (parent-shadow seedling recruitment; ungulate-mediated dispersal in non-native settings)
- Curated Janzen-Martin candidate lists (for held-out validation)

## (e) Minimum viable scale

- ≥ **200 large-fruited Neotropical taxa** with fruit-morphology coding and native-range data.
- ≥ **30 candidate extant megafauna species** with paleo-range reconstruction.
- ≥ **15 documented dispersal-failure cases** in literature.
- ≥ **10 canonical Janzen-Martin held-out exemplars** for recall measurement.
- If fewer than 5 of the 10 held-out exemplars have sufficient PhytoGraph evidence to be scored, the recall metric is **data-limited** and Track 2's headline becomes the candidate ledger itself rather than the recall.

## (f) Falsification protocol

- If the ranked-ledger is dominated by Neotropical large-fruited Fabaceae (single confounder), and the model cannot distinguish ghost-disperser cases from cases where elephants/tapirs/cassowaries are still dispersing the fruit — **fail**.
- If the model proposes anachronism for *Cocos nucifera* (well-dispersed by ocean and humans) or *Carica papaya* (broadly dispersed by modern fauna), recall the model — its negative-evidence channel is broken.
- If holding out reveals that recovery is driven entirely by `fruit_type=large_drupe` and not by paleo-overlap, the paleo layer is doing no work and the contribution collapses to fruit-morphology re-ranking.

## (g) Parallelism axis

**Per-candidate-class fan-out:** large-seeded Neotropical Fabaceae · palm-fruit anachronisms · Annonaceae large-fruited · Sapotaceae · ghost-pollinator Orchidaceae · post-glacial mycorrhizal candidates · Madagascar lemur-fruit candidates (still-extant + recently-extinct) · African elephant-fruit (still-active vs ghost). One clone per class; held-out cases scored in parallel.

## (h) Prior-campaign kernel contribution

- **Retire:** the prior campaign had no paleobotany layer; nothing direct to lift.
- **Lift:** the prior schema's `regional_checklist_context` and `occurrence_provenance` are reused as the native-range substrate for the paleo-overlap join.
- **Lift:** the prior synthetic-benchmark framework (cycle 2) provides the methodology for building a held-out test set; analogous structure used for the canon-recovery validation.
