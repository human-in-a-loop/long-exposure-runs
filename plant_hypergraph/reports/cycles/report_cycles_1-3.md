---
title: "PhytoGraph — Wave 0 + Wave 1 Substrate Ingestion (cycles 1–3)"
date: "2026-05-17"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
[OUTPUT: report]

# PhytoGraph — Wave 0 + Wave 1 Substrate Ingestion (cycles 1–3)

## Abstract

The first three cycles of the PhytoGraph campaign opened with the directive's full six-track program and closed with a merged, audited Wave 1 substrate ready for Barrier 1 normalization. Cycle 1 froze the schema, the data-source audit, and the inclusion contract (Wave 0), then spawned an 8-clone fan-out (FAN-OUT A) covering milestones M1.1, M1.3–M1.9 of substrate ingestion. Cycle 2 produced the post-fan-out researcher brief synthesizing what merged. Cycle 3 ran the post-merge integration audit, consolidating the 8 clone outputs into two workspace-level deliverables (`substrate/staging/BARRIER1_INTEGRATION.md`, `coverage_report.md`) and committing a ledger event recording the integrated state.

Five of eight Wave 1 milestones cleared their numeric floors; three (M1.3 reticulation, M1.6 domestication CWR pair-count, M1.9 Wikidata/Commons) closed as `data-limited` with named blockers and recovery paths. The substrate-isolation contract held across the fan-out — no clone wrote outside its namespace, no schema drift, zero violations of the three discipline gates (zero inferred anachronism edges, zero pre-instrument `convergence_signature` edges, zero ethnobotanical sovereignty violations). The Tier-0 substrate floor (≥50,000 taxa) cleared at 60,000 accepted-taxon keys; Tier 3 (phytochemistry) cleared at 2,315 taxa / 24,751 compounds; Tier 4 (per-axis deep enrichment) cleared in all four contributing axes. Two pre-existing ledger validator errors carry forward as inherited audit backlog.

No predictions were filed in cycles 1–3. Predictions are a Wave 3–4 deliverable. Cycles 1–3 produced only the substrate that Wave 2 enrichment will consume.

## 1. Introduction

PhytoGraph is a typed hypergraph `H = (V, E, τ_V, τ_E, W, P, C, T)` used as a discovery instrument across six tracks: Reticulation Atlas, Ghost Hyperedges, Convergence Pressure, Domestication Hypergraph, Chemodiversity Predictor, and Botanical Foundation Model Probe. The campaign's success criterion is per-track falsifiable prediction, not catalog construction. Cycles 1–3 establish the substrate layer on which those predictions will later be computed.

The directive organizes work into waves separated by barriers. Wave 0 is a single-coordinator scoping pass. Wave 1 fans out one clone per source group and writes only to per-source staging tables. Barrier 1 normalizes synonyms, unions taxonomic crosswalks, and deduplicates against a canonical key before Wave 2 (track enrichment) starts. Cycles 1–3 cover Wave 0, Wave 1, and the post-merge integration that hands the staged substrate to the Barrier 1 coordinator.

The source sessions for this report:

| Cycle | Role | Session ID |
|---|---|---|
| 1 | Researcher | `16a0090c-1df4-4290-8f9c-9bf26fef716a` |
| 1 | Worker (fan-out parent) | `635c1857-af92-4552-945b-01929ee831f3` |
| 1 | Auditor | `fc963b3e-dda6-459c-a0df-06d2e2fa7f00` |
| 2 | Researcher | `6f1abe89-ef08-4438-833f-e321132affa5` |
| 3 | Worker (post-merge integrator) | `d74b0a20-923b-4f5d-8280-f6cb54f604e3` |

Per-clone narratives for M1.3, M1.4, M1.5, and M1.8 are preserved as sibling clone reports (`report_cycles_1-3_clone_{1,2,3,6}.md`). This report consolidates the campaign-level view across all eight clones.

## 2. Cycle 1 — Wave 0 Scoping and Wave 1 Fan-Out

### 2.1 Wave 0: schema freeze and source audit

Cycle 1's researcher session produced the track-by-track scoping documents, the unified hypergraph schema (`phytograph_schema.md`, 251 lines, with the node and edge vocabulary listed in the directive), and the cross-track data-source audit (`data_source_audit.md`, 77 lines). The schema was frozen at version 1.0 as the gate condition for Barrier 0. No downstream phase modified it.

The risk register was opened covering image licensing, source bias, false biological inference, foundation-model API cost, paleobotany interpretation risk, and ethnobotanical data sovereignty.

### 2.2 Wave 1: source-level fan-out (FAN-OUT A)

The cycle-1 worker session orchestrated an 8-clone fan-out, one clone per source group, each writing to a per-source staging namespace under `substrate/staging/`. Inter-clone writes were prohibited until Barrier 1.

| Clone | Milestone | Source group | Track served | Result |
|---|---|---|---|---|
| 0 | M1.1 | WFO + GBIF + Open Tree + POWO taxonomy backbone | substrate-wide | validated, 60,000 accepted-taxon keys |
| 1 | M1.3 | CCDB + Plant DNA C-values + Wood 2009 curated | T1 Reticulation | data-limited (access blocker) |
| 2 | M1.4 | PBDB + LQE + Faurby & Svenning + IUCN + Janzen-Martin canon | T2 Ghost Hyperedges | validated, 237 extinct-fauna nodes |
| 3 | M1.5 | AusTraits 6.0.0 + trait lists | T3 Convergence | validated, 420,545 staged edges |
| 4 | M1.6 | Genesys + USDA GRIN + FAO CWR + WorldClim/CHELSA | T4 Domestication | data-limited (pair-count short) |
| 5 | M1.7 | KNApSAcK + NPASS + Duke + ChEBI + ethnobotanical DBs | T5 Chemodiversity | validated, 2,315 taxa / 24,751 compounds |
| 6 | M1.8 | Foundation-model API harness (Anthropic/OpenAI/Gemini) | T6 Probe | validated (stub fallback, no live keys) |
| 7 | M1.9 | Wikidata SPARQL + Wikimedia Commons | substrate-wide | data-limited (API throttle) |

Each clone produced an `INGEST_AUDIT.md` documenting source access, staged row counts, evidence-scope limits, bias profile, blockers, and validation tests. Clones held three discipline gates strictly:

- **Inferred-anachronism gate (M1.4).** Only 31 literature-cited `anachronism_candidate_edge` rows were emitted; 0 inferred. Track 2 receives a clean seed.
- **Pre-instrument convergence gate (M1.5).** Zero `convergence_signature` edges emitted; 23 candidate uses quarantined into `rejected_records.tsv` with documented refusal reasons. The convergence-pressure statistic is reserved for Wave 3.
- **Ethnobotanical sovereignty gate (M1.7).** Hard-fail probe present on Moerman / PROTA / PROSEA records; zero stripped-provenance violations.

The cycle-1 auditor session ran per-clone validation and a campaign-level closure event for Wave 1, identifying two ledger format defects (line 85 invalid UUID on an auditor closure event; line 99 missing `reopened` interstitial for an M1.3 status transition) that the append-only ledger could not retroactively fix.

## 3. Cycle 2 — Post-Fan-Out Research Synthesis

The cycle-2 researcher session produced the merge synthesis brief that fed the post-merge worker. The brief enumerated five documented divergences across the eight clones, classified them by severity (low, very low, medium, high), and recommended Barrier 1 resolution paths for each:

- **Format heterogeneity** (low) — JSONL / TSV / parquet / code+telemetry mixed across clones; canonical parquet emit at Barrier 1.
- **Test framework heterogeneity** (very low) — `unittest` vs `pytest`; functionally equivalent.
- **Live vs proxy ingestion posture** (medium) — paleobotany rows are literature-curated rather than live-fetched; tagged `access_mode: literature-curated` and barred from serving as primary evidence for paleo-validation predictions.
- **Scale dispersion** (high for Track 1) — M1.3 staged 12 chromosome rows against a 30,000-row floor; M1.5 staged 420,545 trait-assertion edges.

The brief also surfaced cross-cutting findings to be lifted to the risk register: source-density confound concentrated in Dr. Duke for Track 5; Northern-Hemisphere temperate over-sampling in clones 0, 1, and 5; FM-cap mechanism not exercised against real billing; SPARQL pagination fragility in clone 7.

The brief explicitly prohibited the cycle-3 worker from starting new research directions or performing audit-level re-validation of the sub-cycles. Cycle 3's scope was post-merge integration only.

## 4. Cycle 3 — Post-Merge Integration

### 4.1 Scope

The cycle-3 worker session ran as a single-coordinator post-merge integration pass. Read-only assessment. No staging table rewritten. Two new workspace-level artifacts produced; one ledger event committed.

### 4.2 Cross-clone consistency check

A 9-row consistency check was run against the eight clone outputs. All nine rows passed:

| Check | Result |
|---|:-:|
| INGEST_AUDIT.md present in every staging dir | 8/8 |
| Substrate-isolation: writes confined to per-source namespace | ✅ |
| Provenance/license fields present on every row | ✅ |
| Schema v1.0 conformance (no new types invented) | ✅ |
| `pending_crosswalk=true` on raw scientific-name keys | ✅ |
| Discipline gate: zero `convergence_signature` rows pre-instrument | ✅ (0 emitted; 23 quarantined) |
| Discipline gate: zero inferred `anachronism_candidate_edge` | ✅ (31 cited / 0 inferred) |
| Sovereignty guard on ethnobotany | ✅ (0 violations) |
| Floor-cleared OR explicit data-limited declaration | ✅ (5 cleared / 3 declared) |

### 4.3 Tier-ladder coverage

The directive's inclusion contract specifies five tiers. Cycle 3 emitted `coverage_report.md` aggregating the per-source staging totals against tier floors:

| Tier | Target | Staged Wave 1 | Status |
|---|---|---:|---|
| Tier 0 — substrate | ≥50,000 taxa | 60,000 | cleared |
| Tier 1 — fruit + ≥1 metadata field | ≥10,000 | provisional ≥10k | pending Wave 2 merge |
| Tier 2 — crops + CWR | ≥1,000 pairs / taxa | 1,867 taxa / 397 pairs | partial — pair-floor short by 603 |
| Tier 3 — phytochemistry | ≥1,000 | 2,315 taxa / 112 family-cells / 24,751 compounds | cleared |
| Tier 4 — deeply enriched per-axis | ≥200 | cleared in 4 of 4 contributing axes | cleared |

The coverage report is **per-source pre-merge**. A merged-substrate report will supersede it after Barrier 1's canonical-key dedup.

### 4.4 Gap-item triage

Three data-limited milestones received explicit recovery paths in §5 of `BARRIER1_INTEGRATION.md`:

- **M1.3 reticulation.** Authorize CCDB bulk download + Wood 2009 supplement parse, or accept a data-limited Wave 2 Track 1 start. Binding constraint on M2.T1.
- **M1.6 domestication.** Authorize Vincent et al. 2013 Table S1 expansion (estimated +603 CWR pairs) + Genesys per-accession bioclim raster extraction. Binding constraint on M2.T4 only.
- **M1.9 Wikidata/Commons.** Abandon SPARQL pagination as primary; switch to dump-based ingestion. Cross-cutting (image evidence + QID crosswalk).

The integration report also enumerated four mechanical Barrier 1 tasks (storage canonicalization, taxonomic crosswalk union, synonym normalization pass, canonical-key dedup) that the next-cycle Barrier 1 coordinator must execute. These require destructive writes the post-merge brief explicitly deferred.

### 4.5 Ledger and validator state

The promise ledger advanced from 102 to 103 events; the new event (`_plan/wave1-postmerge-integration`) was linked to both new artifacts. Validator hard-error count was unchanged at 2 (both inherited). Two cycle-2 orphan artifacts (`scripts/build_reticulation_enrichment_preflight.py`, `tests/test_reticulation_enrichment_preflight.py`) remain unlinked and were flagged for a follow-up `_plan/orphan-cleanup-reticulation-preflight` event.

A per-cycle temp helper for ledger appending (`.ledger_event_tmp.py`) was preserved as `stale/ledger_event_tmp_cycle3_postmerge.py` rather than deleted; the harness declined `rm` and archival preserves the audit trail.

## 5. Findings Across Cycles 1–3

### 5.1 What is established

- A frozen schema v1.0 covering all directive node and edge types, with per-edge `allowed_evidence_scope` declarations.
- A Tier-0 substrate of 60,000 angiosperm accepted-taxon keys with synonym clusters (113,582 rows) and a typed taxonomic-conflict table (62 rows) staged for Barrier 1 resolution.
- A Track-2 paleobotany seed of 237 extinct-fauna nodes and 31 literature-cited anachronism candidates, all with verbatim source confidence codes.
- A Track-3 trait substrate of 420,545 source-asserted structural edges across 12 trait lists clearing the ≥500-row floor, with all `convergence_signature` inference deferred.
- A Track-5 chemodiversity layer of 2,315 taxa and 24,751 compounds spanning 112 family-cells, with one mandatory ablation (remove Dr. Duke) lifted to the Wave 4 plan.
- A Track-6 FM probe harness with four provider adapters (three real plus stub fallback) and a $500/cycle USD cap mechanism (stub-validated only).
- Two consolidating reports (`BARRIER1_INTEGRATION.md`, `coverage_report.md`) and a 103-event promise ledger.

### 5.2 What is constrained

- Track 1 (Reticulation) cannot start enrichment at production scale without M1.3 source acquisition (12 chromosome rows / 5 polyploidization events against floors of 30,000 / 2,000).
- Track 4 (Domestication) cannot start enrichment at full scale without the M1.6 CWR-pair expansion (397 / 1,000).
- Tier 1 cannot be finalized until Wave 2 M2.T3 joins fruit-syndrome codings to the accepted-key set.
- Live FM-cap behavior in M3.T6 requires a first-call $5 sentinel observation before normal Wave-3 operation.

### 5.3 What is open

- Two pre-existing ledger validator hard errors require either a manager-authorized validator allowlist extension or explicit tolerance as historical-evidence rows. Append-only semantics block retro-fixing.
- Two cycle-2 orphan reticulation-preflight artifacts need ledger linkage.
- The post-merge `coverage_report.md` will be superseded by a merged-substrate version after Barrier 1.
- Three documented bias confounds (Northern-Hemisphere temperate over-sampling; Dr. Duke source-density dominance; literature-curated paleobotany access mode) must be reflected in Phase-6 validation stratification, not Wave-1 ingestion.

## 6. What Is New, What Is Integrated, What Is Speculative

The directive requires this classification per track. At end of cycle 3, no predictions have been filed; the question reduces to substrate categorization.

**New.** The unified typed hypergraph schema v1.0 covering reticulation, ghost-partner, convergence, crop-pedigree, chemodiversity, ethnobotany, and adversarial-probe edges under one source-permission rule set is novel as an integration. The discipline-gate enforcement (zero pre-instrument inference) at the staging layer is a methodological contribution carried forward from the directive into per-clone audit infrastructure.

**Integrated.** All Wave 1 staged data are integrations of published or publicly accessible sources (WFO, GBIF, Open Tree, POWO, PBDB, LQE, Faurby & Svenning, AusTraits, Genesys, USDA GRIN, FAO CWR, KNApSAcK, NPASS, Dr. Duke, Moerman, ChEBI, PROTA, PROSEA, Wikidata, Wikimedia Commons). No new biological claims are made in cycles 1–3.

**Speculative.** None. The cycle-3 brief explicitly forbade new research directions; the speculation ledger is empty for this period.

## 7. Open Questions

- Will Barrier 1's synonym normalization (113,582 cluster rows) materially change apparent taxon diversity, as H8 predicts? This is the first quantitative observable in cycle 4.
- Will the M1.3 source-acquisition decision unblock Track 1 production scale, or will Track 1 proceed at data-limited scale with caveats?
- Does the M1.7 ablation "remove Dr. Duke" collapse the Track 5 floor, exposing it as a source-density artifact?
- Does the literature-curated access mode for M1.4 prevent Track 2 from producing publishable Phase-6 validation, or does the canon seed plus modern-disperser substrate suffice?

## 8. Appendix: Implementation Details

### 8.1 Staging inventory (per-source)

```
substrate/staging/
├── taxonomy_backbone/         (M1.1) accepted_taxa, synonym_clusters, conflicts
├── taxonomy_backbone_smoke/   (M1.1) smoke validation outputs
├── reticulation_sources/      (M1.3) seed chrom counts, ploidy, hybrid/polyploid events
├── paleobotany_sources/       (M1.4) extinct fauna, anachronism candidates, ranges
├── convergence_sources/       (M1.5) AusTraits-derived staged edges and nodes
├── domestication_sources/     (M1.6) CWR pairs, multi-parent pedigrees, Vavilov centers
├── chemodiversity_ethnobotany_sources/  (M1.7) phytochem assertions, ethno-use, sovereignty guard
├── fm_probe_harness/          (M1.8) provider adapters, telemetry JSONL, $500 cap
├── wikidata_commons/          (M1.9) QID crosswalk, Commons media metadata
└── BARRIER1_INTEGRATION.md    (cycle 3) consolidated audit
```

### 8.2 Test status

All clones report local test passes (per-clone INGEST_AUDIT.md):
- M1.1: parquet schema and crosswalk smoke tests pass.
- M1.3: 13 pytest cases pass (staging, bulk-intake, format-readiness).
- M1.4: 10/10 schema-conformance tests pass.
- M1.5: 1 schema test passes covering required files, frozen edge types, provenance completeness, scale threshold, evidence-scope limits, unresolved taxonomy preservation, and rejected-record coverage.
- M1.7: sovereignty hard-fail probe passes; chemodiversity floor tests pass.
- M1.8: 12 smoke tests pass, 3 skip on no-keys condition.

### 8.3 Validator state

`python3 -m long_exposure.tools.promise_check <run-root>` returns:
- Total events: 103.
- Hard errors: 2 (inherited; line 85 invalid UUID, line 99 missing `reopened` interstitial).
- Orphan warnings: ~50 pre-existing legacy artifacts plus 2 cycle-2 reticulation-preflight files; no new orphans introduced by cycle 3.

### 8.4 Session-to-artifact map

| Session | Cycle | Primary outputs |
|---|---|---|
| `16a0090c-…` (researcher) | 1 | `phytograph_schema.md`, `data_source_audit.md`, `risk_register.md`, track scoping notes |
| `635c1857-…` (worker, fan-out parent) | 1 | 8 clone staging dirs + INGEST_AUDIT.md each; promise-ledger events for M1.1, M1.3–M1.9 |
| `fc963b3e-…` (auditor) | 1 | per-clone validation outcomes; ledger format-defect surfacing |
| `6f1abe89-…` (researcher) | 2 | post-fan-out merge synthesis brief; divergence triage; gap-item handoff plan |
| `d74b0a20-…` (worker, integrator) | 3 | `substrate/staging/BARRIER1_INTEGRATION.md`, `coverage_report.md`, ledger event 103, `stale/ledger_event_tmp_cycle3_postmerge.py` |

### 8.5 Cross-reference map

| Origin | Consumer | Flow |
|---|---|---|
| `phytograph_schema.md` (Wave 0) | All 8 Wave 1 clones | Frozen node/edge vocabulary; allowed-evidence-scope per edge type |
| Per-clone `INGEST_AUDIT.md` | Cycle 3 integrator | Source-level evidence for consistency check |
| Per-clone `coverage_row.json` | `coverage_report.md` | Machine-readable tier-ladder aggregation |
| Cycle 2 merge synthesis brief | Cycle 3 integrator | §6 work-list carried into `BARRIER1_INTEGRATION.md` §5 |
| `BARRIER1_INTEGRATION.md` | Next-cycle Barrier 1 coordinator | Task queue for destructive normalization writes |
| `coverage_report.md` | Directive deliverable #3 | Tier-ladder evidence for inclusion contract |
| Promise ledger event 103 | `promise_check` validator | Two-way linkage between integration artifacts and audit trail |

### 8.6 References cited this cycle range

References [1]–[32] from the prior cycle range carry over. Cycles 1–3 of the PhytoGraph campaign add references through [44] for the specialty sources ingested in Wave 1:

[27] Royal Botanic Gardens, Kew, "Plants of the World Online," Kew Science, 2026.
[28] CCDB, "Chromosome Counts Database," Tel Aviv University, version 1.66.6, 2026.
[29] Rice, Glick, Abadi et al., "The Chromosome Counts Database (CCDB) — a community resource of plant chromosome numbers," *New Phytologist*, 2015.
[30] Leitch, Johnston, Pellicer, Hidalgo, Bennett, "Plant DNA C-values Database," RBG Kew, 2026.
[31] Wood, Takebayashi, Barker et al., "The frequency of polyploid speciation in vascular plants," *PNAS*, 2009.
[32] Wikidata, "Wikidata Query Service SPARQL endpoint," Wikimedia Foundation, 2026.
[33] Wikimedia Commons, "MediaWiki Action API," Wikimedia Foundation, 2026.
[34] Falster, Gallagher, Wenk, Sauquet et al., "AusTraits: a curated plant trait database for the Australian flora," Zenodo v6.0.0, 2024.
[35] Duke, "Dr. Duke's Phytochemical and Ethnobotanical Databases," Ag Data Commons, 2023.
[36] Potok, "Native American Ethnobotany Database mirror," Datasette mirror of Moerman NAEB data, 2026.
[37] KNApSAcK Family, "KNApSAcK Core System," 2026.
[38] Zeng et al., "NPASS: Natural Product Activity and Species Source Database," 2026.
[39] EMBL-EBI, "ChEBI: Chemical Entities of Biological Interest," 2026.
[40] PROTA Foundation, "Plant Resources of Tropical Africa," PROTA4U, 2026.
[41] PlantUse, "Plant Resources of South-East Asia (PROSEA)," 2026.
[42] Faurby and Svenning, "Resurrection of the genus *Tomistoma* / Late-Quaternary megafauna range reconstructions" and successors, cited per `paleobotany_sources/INGEST_AUDIT.md`.
[43] Late Quaternary Extinctions database, cited per `paleobotany_sources/INGEST_AUDIT.md`.
[44] Vincent et al., "A prioritized crop wild relative inventory to help underpin global food security," Table S1, 2013 — cited as the recovery path for M1.6 CWR-pair expansion.

Full bibliographic entries are preserved in `REFERENCES.md`.

[END OUTPUT: report]

Cycles 1–3 of the PhytoGraph campaign covered Wave 0 schema freeze, Wave 1 eight-clone substrate-ingestion fan-out, and a cycle-3 post-merge integration audit. Five of eight Wave 1 milestones cleared their floors; three closed as `data-limited` with named recovery paths. The substrate-isolation contract and all three discipline gates held across the fan-out. Two consolidating reports (`BARRIER1_INTEGRATION.md`, `coverage_report.md`) and one ledger event were produced in cycle 3; no predictions were filed (predictions are a Wave 3–4 deliverable). The report is in the OUTPUT block above; the harness will write it to `reports/cycles/report_cycles_1-3.md` and render the PDF.

Type `/complete` to save the session and exit.
