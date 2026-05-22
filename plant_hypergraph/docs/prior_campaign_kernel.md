<!--
created: 2026-05-17T15:50:00Z
cycle: 1
run_id: run-phytograph-cycle1
agent: worker
milestone: M0.1
-->

# Prior Campaign Kernel Inheritance

The prior campaign — **Plant Taxonomy as Hypergraph Structure** (M1–M8, cycles 1–77, completed and validated) — produced reusable artifacts. This document classifies each as **lift** (use unchanged), **partial lift** (use with reframing), or **retire** (do not carry forward).

| Prior artifact | Cycle / Milestone | Classification | Rationale |
|---|---|---|---|
| `docs/data_feasibility_map.md` | cycle 1 / M1 | **partial lift** | The WFO/GBIF/Open Tree access analysis is reused as the substrate-source rows of the new `data_source_audit.md`. The PhytoGraph audit adds ~25 new sources for tracks 2–6. |
| `docs/hypergraph_schema.md` | cycle 1 / M2 | **partial lift** | The 7 hyperedge families (`taxonomic_parentage`, `synonym_cluster`, `trait_syndrome`, `regional_checklist_context`, `occurrence_provenance`, `reticulate_or_hybrid_signal`, `missing_rank_bridge`) are subsumed in `phytograph_schema.md` §3.1–3.2 and §3.9 unchanged in spirit. PhytoGraph extends to ~32 edge types. **Critically: the prior schema's DAG-vs-hypergraph framing is NOT lifted into the new per-track scoping.** |
| WFO/GBIF/Open Tree no-auth probe (cycle 1 / M5) | cycle 3 / M5 | **lift** | The probe scripts and source-feasibility CSV are directly reusable in Wave 1 M1.1 ingestion. Access conventions documented there are still valid. |
| `data/source_probe_results.json`, `data/source_feasibility_matrix.csv` | cycle 1 | **lift** | Reusable as M1.1 starter data. |
| Synthetic reticulate taxonomy benchmark generator | cycle 2 / M3 | **lift** | Reused as the unit-test substrate for Track 1's TCI and Track 3's CPS before they run on real data. Provides ground-truth reticulation and convergence cases. |
| Hierarchy-aware metrics + tests | cycle 2 / M4 | **partial lift** | Lifted: the synonym-normalized error, hierarchy-coherence violation rate, reticulate near-miss score. Reframed: these become metrics for ablations and Atlas-display quality, not the campaign headline. |
| Public taxonomy sample | cycle 3 / M5 | **lift** | Frozen WFO/GBIF/Open Tree sample is direct input to M1.1. Access dates already recorded. |
| Baseline + hypergraph experiment harness | cycle 4 / M6 | **partial lift** | The harness (flat / tree-DAG / ordinary-graph / native-hypergraph / clique-expansion baselines) becomes the **ablation harness** in Phase 8, NOT the headline experiment. Per directive: "Hypergraph vs DAG" is instrumentation, not the scientific question. |
| Clique-expansion warning theorem | cycle 5 / M7 | **lift** | Direct lift. Constrains Track 1 TCI implementation (must operate on native hyperedges) and Track 3 CPS implementation (clique expansion would spuriously inflate convergence). It is also one of the ≥3 formal contributions countable in PhytoGraph (re-cited, not re-derived). |
| Final report / audit / contribution ledger (cycle 6 / M8) | cycle 6 | **partial lift** | The discipline (separate validated / falsified / speculative / data-limited) carries forward as the per-track ledger format. The specific scoped-modeling conclusion does not carry forward. |

## Reframings explicitly required

- The prior campaign's headline question was "does a hypergraph beat tree/DAG/graph baselines for plant taxonomy classification?" PhytoGraph's headline question is "what predictions about plant biology does PhytoGraph make, and which can we validate or falsify?" The shift from representation-quality to predictive instrument is not a footnote — it changes the success criteria.
- The prior campaign's Atlas was implicitly a wiki-style browser. The new Atlas is a **window into predictions**. This kills any reflex to surface prior catalog content as cycle-2 Atlas filler.

## What is NOT inherited

- The prior plan-of-record's M1–M8 milestone structure (replaced by Waves 0–5).
- The "Hypergraph vs DAG" headline benchmark (relegated to ablation).
- The fruit-plants-as-wiki framing (deprecated per directive).
- The edibility-as-inclusion-rule framing (replaced by Tracks 4/5/6 covering human-plant interaction).
