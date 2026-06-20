---
title: "PhytoGraph Final Report"
date: "2026-05-19"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# PhytoGraph Final Report

## Abstract

PhytoGraph was scoped as a six-track discovery campaign: a typed, auditable plant-biology hypergraph intended to support falsifiable predictions about reticulation, ghost coevolutionary partners, convergence, domestication, chemodiversity, and botanical failure modes in foundation models. The campaign deliberately treated the Botanical Atlas as a research window rather than the headline result. Its intended success criterion was a master prediction ledger containing validated, falsified, or explicitly data-limited claims.

The work produced a large shared substrate, six track-local enrichment layers, instruments or scaffolds, a validated Atlas integration surface, validation and ablation records, controlled reopen gates, a final free-tier closure synthesis, a taxonomy-results communication site, and a final handoff manifest. It did not meet the original research-success criterion of at least one validated prediction per track. No track-local biological, crop-substitution, phytochemical, or model-performance claim was promoted into the master `prediction_ledger.tsv`, and the master `speculation_ledger.tsv` also remained header-only.

The controlling final-audit headline is: **10 validated, 1 in-progress · promise_check=green**. The only in-progress milestone is `_manager/validator-warnings`, a watch-only inherited-warning item with medium confidence. The final audit reports **0 CRITICAL**, **0 MODERATE**, and **0 MINOR** findings, emits **0 reconciliation events**, and records `promise_check_status=green`. The audit also records five residual-debt entries: inherited validator warnings, inherited baseline plan-ledger consistency debt, timestamp drift for reports 24-32, timestamp drift for the taxonomy-results-site closure note, and a session-transcript coverage gap.

The strongest completed contribution is architectural, diagnostic, and communicative. PhytoGraph now has a repaired typed substrate, explicit evidence boundaries, a six-track Atlas contract that separates observed evidence from predictions and missingness, conservative validation and falsification records, defined reopen predicates, and public communication and handoff artifacts that preserve the non-promotion boundary.

## Introduction And Mission

PhytoGraph is a typed hypergraph for plant biology. A hypergraph is a graph-like data structure in which one edge can connect more than two nodes. That property matters for plants because many important botanical relationships are not simple pairwise links. A crop pedigree can connect several wild ancestors, a cultivar, selected traits, geography, and time. A phytochemical assertion can connect a taxon, compound, plant part, concentration, source, and caveat. A reticulation event can involve multiple parental lineages.

The campaign's mission was predictive, not encyclopedic. It organized plant biology into six tracks:

| Track | Intended scientific question |
|---|---|
| Track 1, Reticulation Atlas | Where does a single-parent tree lose information about angiosperm evolution? |
| Track 2, Ghost Hyperedges | Can extinct or missing coevolutionary partners be recovered from holes in the modern hypergraph? |
| Track 3, Convergence Pressure | Can repeated plant phenotypes be measured as independent convergence rather than inherited homology? |
| Track 4, Domestication Hypergraph | Can crop pedigrees, wild relatives, Vavilov centers, and climate envelopes support crop-substitution analysis? |
| Track 5, Chemodiversity Predictor | Can family, ecology, and herbivore-pressure context prioritize under-screened taxa for phytochemistry? |
| Track 6, Botanical Foundation Model Probe | Can PhytoGraph provide adversarial botanical ground truth for model-failure evaluation? |

The report uses five terms consistently. A **master ledger** is the campaign-level file where a row becomes a cross-track prediction or speculation. A **track-local output** is a table, score, page, report, or validation artifact that belongs to one track but has not necessarily been promoted to the campaign ledger. **Validation** means checking a prediction against a named source or protocol. **Data-limited closure** means a track was closed because required evidence was absent, too sparse, or insufficiently joined to accepted taxon keys. A **communication-layer artifact** is a public or maintainer-facing presentation over already closed results; it can clarify, package, and expose results, but it cannot by itself reopen science or promote ledger rows.

The evidence discipline is central. A prediction is not a fact. A validated prediction is validated only against its stated source and protocol. A source assertion does not automatically become a biological truth. This report does not claim new taxonomy, new edibility, new native range, new ecological interaction, new hybrid origin, new anachronism, new bioactivity, or a measured foundation-model failure rate unless the artifacts explicitly support that claim. The campaign did not reach that level of per-track biological validation.

Later terminal work did not change the scientific result. It converted conservative closure into a clearer handoff state: a final free-tier closure synthesis, a taxonomy-results site for public review, QA and closure notes for that site, and a handoff manifest that tells future maintainers which artifacts are canonical and which changes would count as scientific reopening.

## Substrate, Schema, And Evidence Boundaries

The campaign began by freezing a shared schema and source-audit discipline. The common hypergraph was defined as:

```text
H = (V, E, tau_V, tau_E, W, P, C, T)
```

Here `V` are typed nodes, `E` are typed hyperedges, `tau_V` and `tau_E` assign node and edge types, `W` stores weights and source reliability, `P` stores provenance, `C` stores caveats and allowed evidence scope, and `T` stores temporal annotations. This structure allowed the campaign to keep taxonomy, phylogeny, reticulate inheritance, trait membership, convergence, domestication, phytochemical detection, bioactivity, ethnobotanical use, media evidence, and model-probe ground truth in separate evidence classes.

The first source-ingestion tranche produced `phytograph_schema.md`, `data_source_audit.md`, the risk register, per-source staging areas, and `coverage_report.md`. The Tier 0 substrate target cleared at **60,000 accepted-taxon keys**. The phytochemistry tier cleared at **2,315 taxa** and **24,751 compounds**. Five of eight early source milestones cleared their numeric floors; three closed as data-limited with named blockers.

The evidence-boundary rules were enforced at staging time:

- Paleobotany ingestion emitted **31 literature-cited anachronism candidate edges** and zero inferred anachronism edges.
- Convergence-source ingestion emitted source-stated trait, morphology, and life-form assertions, but zero pre-instrument `convergence_signature` edges.
- Reticulation-source ingestion staged chromosome counts, ploidy context, hybridization events, polyploidization events, and reticulate-inheritance evidence without treating chromosome counts as event proof.
- Ethnobotanical and phytochemical ingestion preserved provenance and did not turn use records into clinical or bioactivity claims.
- Track 6 harness work produced tooling and offline scaffolding, not model-response evidence.

The Track 1 reticulation source branch was validated as access-limited rather than production-scale complete. It staged **12 chromosome-count assertions**, **6 ploidy-context rows**, **1 hybridization event**, **4 polyploidization events**, and **5 reticulate-inheritance evidence rows**, far below the planned floor of 30,000 chromosome-count assertions and 2,000 event/support rows. Track 4 crop-wild-relative and climate evidence was also short of the evidence needed for climate substitution. These early constraints reappeared later as data-limited closures, not as instrument defects.

The first attempt to freeze the shared substrate failed for a substantive data-integrity reason. Synonym-resolved accepted taxon keys existed in a side table, but they had not been propagated back into retained hyperedges. Deduplication also collapsed distinct biological assertions because it grouped on incomplete member sets instead of full typed role maps. The reported example was `Acaena x ovina`, where distinct Track 3 trait rows collapsed even though they had different trait-role members.

After repair, accepted keys were propagated into retained hyperedges and deduplication used full typed member sets rather than raw taxon names alone. The shared substrate validator passed with **363,237 nodes** and **641,183 retained hyperedges**. All six enrichment branches passed conformance, and the combined track regression suite passed **41 tests**. At that point the campaign had a validated enrichment substrate, but no prediction had yet been promoted to the master ledger.

## Barrier Repairs, Instruments, And Atlas Integration

The Barrier 1 repair mattered scientifically because every downstream instrument depended on accepted-key joins and on preserving role-map distinctions. Without that repair, source rows could appear joined while retained hyperedges still lacked accepted keys, and distinct trait or evidence assertions could collapse into a single edge.

Wave 2 enrichment then projected each track onto the repaired substrate without changing the frozen schema. Track 1 remained sparse and data-limited. Track 2 carried literature-cited ghost-partner seeds and range context. Track 3 carried 209,297 trait-membership rows with a diagnostic `_other` bucket. Track 4 retained six observed domestication hyperedges. Track 5 carried 23,524 resolved taxon-keyed chemodiversity rows with heavy Dr. Duke source concentration. Track 6 carried 210 offline questions and 210 schema-shaped ground-truth rows marked `offline_unrun`.

The Atlas status changed after the early instrument cycle. An earlier report described the Atlas as a page contract and scaffold with missing generated outputs. Later reports revised that state: the missing Track 1 and Track 3 reports were completed, Track 1 and Track 3 outputs were integrated into Atlas adapters, and the static Atlas was rebuilt as a six-track integration surface. The Atlas exposed all six track-local outputs across **60,000 searchable taxon pages** with evidence-vs-prediction labels.

The Barrier 3 readiness package was auditor-validated. The Atlas exposed all six instruments or scaffolds with provenance, caveats, missing-data indicators, and evidence-vs-prediction labels. The rebuild produced 60,000 pages and 60,000 search-index rows. No page rows used unsupported `validated` status, and the master ledgers remained header-only.

This is an integration result, not terminal scientific validation. The Atlas makes track-local outputs inspectable and queryable; it does not by itself validate a biological, crop, chemistry, or model-performance claim. The later taxonomy-results site follows the same boundary: it communicates and packages closed statuses, but it does not reopen tracks.

## Track Status Synthesis

The final track status is conservative. Each track produced some combination of schema integration, instrument code, scoring outputs, validation tables, ablations, reports, or reopen evidence. None produced a master-ledger biological prediction accepted as validated across the campaign.

| Track | Final limitation class | Strongest completed artifact or result | Blocker | Claim boundary |
|---|---|---|---|---|
| Track 1, Reticulation Atlas | `sidecar_readiness_uncontrolled` | 22 GBIF event taxa, 11 source groups, 2 WFO-projected taxa, 0/17 matched-control event recovery. | GBIF sidecar signal was not WFO-projected and source-density controls remained unresolved. | No established reticulation hotspot, hybridization, or polyploid recovery claim. |
| Track 2, Ghost Hyperedges | `H2_remains_not_supported_or_data_limited` | 8 canonical held-outs, 31 local candidates, 0/8 canonical held-outs passed the validation contract. | Accepted-key modern-failure evidence, source-class support, and living-megafauna controls did not clear the contract. | No new anachronism, ghost-partner, or ecological-interaction claim. |
| Track 3, Convergence Pressure | `confound_limited` | 3,069 accepted-key trait carrier rows across 15 canonical traits; 0 controlled-ready traits. | No trait separated convergence signal from family-size, sampling-density, projection-loss, and source gates. | No convergence or adaptive-origin claim. |
| Track 4, Domestication Hypergraph | `still_data_limited` | 3,358 post-filter occurrence records, 0 numeric BIOCLIM vectors, 0 validation-allowed comparator rows. | Coordinate recovery did not yield numeric local/free BIOCLIM vectors or disjoint expert comparator rows. | No crop-substitution recommendation or climate-adaptation claim. |
| Track 5, Chemodiversity Predictor | `H5_remains_source_biased` | Non-Duke temporal evidence remained insufficient; no validation-ready structured family/class stratum. | Open non-Duke detections did not support a structured temporal predictor independent of Duke/source density. | No new phytochemical, bioactivity, or screening-priority claim. |
| Track 6, Botanical Foundation Model Probe | `environment_limited_untested` | 0 runnable local runtime-weight pairings, 0 executed responses, 0 scored responses. | No approved local model runtime and weight pairing was available under the free/open/local constraint. | No model error-rate, leaderboard, toxicity-look-alike, or vendor-comparison claim. |

Track 1's instrument is the **tree-compatibility index**, a score in `[0,1]` where `1` means tree-compatible under available evidence and lower values reflect direct reticulation evidence or structural proxies. Later repair tightened the evidence boundary: observed reticulation evidence counts only accepted-key, event-shaped evidence such as `hybridization_event`, `polyploidization_event`, event-shaped `reticulate_inheritance_evidence`, or accepted multi-parent `crop_pedigree` evidence. Chromosome-count and ploidy-state rows remain structural context. H1 did not validate or reopen because the event-shaped accepted-key evidence remained too narrow and source-density controls remained unresolved.

Track 2's Ghost Hyperedges work produced a scoring rule over morphology support, extinct-fauna or paleo-context support, modern dispersal-failure support, geography/time compatibility, provenance completeness, living-megafauna ambiguity, and singleton-source thinness. The final closure table records 0/8 canonical held-outs passing the validation contract. Track 2's result is a null/data-limited validation result for the current PhytoGraph ranker, not a claim that the broader biological anachronism literature is false.

Track 3 produced a convergence-pressure statistic and confound diagnostics. The later free-tier closure synthesis found 3,069 accepted-key trait carrier rows across 15 canonical traits, but zero controlled-ready traits. H3 remains unvalidated above family-size, sampling-density, projection-loss, and source controls.

Track 4's Crop Substitution Engine is recognized as present, but climate substitution is not computable under current evidence. Occurrence recovery improved, but no numeric BIOCLIM vectors and no validation-allowed comparator rows were available. The campaign therefore does not make recommendation-like crop-substitution or climate-adaptation claims.

Track 5 produced a family-level screening prior, but its validation result is source-limited. The durable result is a source-bias null: available evidence did not support a structured, dated, non-Duke family/class predictor independent of source density.

Track 6 produced a benchmark and deterministic controls, not model results. Because no approved local/open runtime-weight pairing produced audited responses, no model error rate, toxicity-look-alike policy claim, leaderboard, vendor comparison, or model-family comparison is supported.

## Validation, Ablations, And Master Ledgers

The master prediction boundary is the clearest campaign-level result. The campaign produced track-local instruments, candidate rows, validation tables, ablations, reopen diagnostics, and communication artifacts, but the master `prediction_ledger.tsv` and `speculation_ledger.tsv` remained header-only. No track-local row became a campaign-level validated biological prediction.

Wave 4 validation and later closure-strengthening produced the following hypothesis statuses:

| Hypothesis | Status | Validation or ablation result | Master-ledger result |
|---|---|---|---|
| H1, reticulation recovery and hotspots | Data-limited / sidecar-readiness uncontrolled | GBIF sidecar evidence remained uncontrolled, WFO projection was insufficient, and matched-control event recovery was 0/17 in the final free-tier table. | No promotion. |
| H2, ghost-partner recovery | Not supported or data-limited | 0/8 canonical held-outs passed the validation contract under accepted-key/source/living-megafauna controls. | No promotion. |
| H3, convergence above confounds | Confound-limited | 3,069 accepted-key trait carrier rows existed, but 0 traits were controlled-ready. | No promotion. |
| H4, climate-aware crop substitution | Data-limited | 3,358 post-filter occurrence records existed, but numeric BIOCLIM vectors and validation-allowed comparator rows were absent. | No promotion. |
| H5, temporal chemodiversity recovery | Not validated / source-biased | Non-Duke temporal evidence was insufficient for a validation-ready structured family/class stratum. | No promotion. |
| H6, foundation-model failure rates | Environment-limited / untested | No runnable local runtime-weight pairings, executed responses, or scored responses existed. | No promotion. |

The validation and ablation work should be read as evidence classification. Track 2 does not falsify the Janzen-Martin biological literature; it shows that the current PhytoGraph ranker did not recover held-out cases under accepted-key and source controls. Track 3 does not disprove convergence; it shows that current trait priors cannot yet validate H3 above confounds. Track 5 does not disprove chemodiversity structure; it shows that the present source layer is too dominated by available source strata for source-independent temporal discovery claims.

The final free-tier closure synthesis made the master-ledger decision explicit: the ledgers remain header-only because every track retains at least one failed validation predicate, unresolved control, source-bias collapse, or execution blocker. The later handoff and taxonomy-results site did not modify that decision.

No ledger causal summary was supplied for final synthesis. The report therefore does not invent a causal graph. It reports the track-local artifacts, header-only master ledgers, and final audit status as the controlling record.

## Post-Closure Reopen Gates And Evidence Tests

Post-closure work defined mechanical reopen gates for H1, H4, H5, and H6. A reopen is not triggered by wording changes, visualization changes, threshold tuning, communication-site changes, or scoring refinements alone. Reopening requires a named missing evidence class, accepted join keys, sufficient coverage, and a first validation or falsification test.

| Hypothesis | Evidence needed to reopen | Changes that do not reopen |
|---|---|---|
| H1, reticulation | Audited GBIF-to-WFO accepted-key projection or an admitted sidecar namespace plus source-density controls preserving event signal. | Rescoring sparse rows, adding chromosome-count context without event-shaped evidence, or changing TCI wording. |
| H4, climate substitution | Audited crop/CWR BIOCLIM summaries and disjoint candidate-level expert comparator rows. | Producing non-climate same-genus priors, recovered coordinates without numeric vectors, or climate placeholders. |
| H5, chemodiversity | Accepted-key, dated, non-Duke taxon-compound rows across enough families/classes to estimate signatures without source collapse. | More Duke-backed screening priors or undated compound rows alone. |
| H6, foundation-model probe | Approved local model weights and runtime producing audited deterministic response rows with scorer diagnostics. | Stub responses, deterministic controls, provider harness smoke tests, or unavailable local runtime checks. |

The H1 reopen tests improved the evidence inventory but did not reopen the hypothesis. Cycle 23 added accepted-key event-shaped rows, and later free/open recovery retained a GBIF sidecar signal. The final closure synthesis still records only 2 WFO-projected taxa and 0/17 matched-control event recovery. The blocker is not a missing table title; it is accepted-key projection and source-density control.

The H4 reopen tests recovered occurrence and coordinate context but did not produce the evidence needed for climate substitution. The final status records 3,358 post-filter occurrence records but zero numeric BIOCLIM vectors and zero validation-allowed comparator rows. Without numeric climate vectors and comparator pairs, climate substitution remains undefined.

The H5 reopen tests found insufficient non-Duke temporally structured evidence. Manual candidates and non-Duke hints did not become a structured family/class temporal layer capable of a source-independent validation rerun.

The H6 reopen test found no approved local runtime/weights and no executed or scored responses. The static benchmark and deterministic scorer remain useful future infrastructure, but they are not an evaluation result.

## Public Communication And Handoff

The latest delta adds a validated communication and handoff layer over the conservative scientific closure. This layer does not reopen tracks, alter scientific statuses, regenerate evidence tables, or promote prediction/speculation rows.

The taxonomy-results site is a public communication and expert-review surface over closed statuses. Its machine-readable summary reports **60,000 indexed taxa**, a typed plant-evidence hypergraph substrate, an accepted-name policy that keeps synonym/source conflicts visible, and a policy that separates observed evidence, inferred fields, predicted fields, and missing data. The public routes are organized around starting context, track choice, findings, non-promotion reasons, evidence exploration, methods for taxonomists, limitations, and evidence that would change conclusions.

The site summarizes the same six final track outcomes: Track 1 sidecar evidence only; Track 2 not supported or data-limited; Track 3 confound-limited; Track 4 data-limited; Track 5 source-biased; and Track 6 untested under local/open constraints. The site summary preserves track-specific claim boundaries, such as no reticulation hotspot claim, no anachronism or ecological-interaction claim, no convergence or adaptive-origin claim, no crop-substitution recommendation, no phytochemical or bioactivity claim, and no model error-rate or leaderboard claim.

The taxonomy-results QA report records the communication-layer checks. Required files were present: `index.html`, `assets/styles.css`, `assets/app.js`, `data/site_summary.json`, six evidence tables, README, and provenance notes. Required figure assets were present. Static local `src` and `href` targets passed. Public `.html`, `.css`, `.js`, `.json`, `.svg`, and `.md` text passed the language-boundary scan. Desktop and mobile screenshots were checked; an initial oversized headline and narrow-viewport clipping issue was corrected in CSS, and follow-up screenshots showed readable headings, usable route navigation, visible evidence controls, and no obvious text overlap in inspected views. The QA limitation is also explicit: this was screenshot and route rendering review, not a full assistive-technology audit.

The taxonomy-results closure note defines the website maintenance boundary. Future site maintenance may improve clarity, accessibility, broken links, provenance hygiene, and reproducibility, but it must not alter scientific statuses, regenerate evidence tables, or promote master ledger rows. The site is a one-way presentation layer over audited closure artifacts.

The final campaign handoff manifest gives future maintainers the canonical closure map. It names the final artifacts, states that `phytograph_schema.md` is frozen at schema v1.0, describes `phytograph_dataset/` as a query and provenance substrate rather than a source of new claims by itself, points to the Botanical Atlas and Barrier 3 readiness records, and identifies `taxonomy_results_site/` as validated public communication. It repeats the six limitation classes and gives the reopening rule: only a new scientific pass with qualifying evidence and audited controls may modify track conclusions or write data rows to the master ledgers.

## Formal And Diagnostic Contributions

PhytoGraph's durable contributions are formal, diagnostic, infrastructural, and communicative rather than validated biological discoveries.

First, the evidence-boundary schema is a reusable contribution. It defines what each edge type is allowed to support. A `phytochemical_assertion` can support compound detection only when the source says so; it does not prove taxon-typical concentration, clinical efficacy, dosage, or safety. A `crop_pedigree` edge supports a named pedigree relation within its provenance; it does not automatically validate a climate substitution. A trait-membership row does not become convergence evidence until an instrument evaluates independent recurrence and controls.

Second, the Barrier 1 repair is a concrete data-engineering contribution. It showed that synonym resolution is not enough if accepted keys remain outside retained hyperedges, and that deduplication must preserve full typed role maps. The repair prevented distinct biological assertions from collapsing into one retained edge.

Third, Track 1 contributes the TCI scoring framework and accepted-key diagnostic logic. The score separates direct reticulation evidence from structural context. Its present biological utility is limited by sparse accepted-key event evidence and unresolved source-density controls, but the framework and reopen tests define what better evidence would need to supply.

Fourth, Track 2 contributes a ghost-partner scoring rule and ablation discipline. The score explicitly separates morphology, paleo-context, modern dispersal failure, geography/time compatibility, provenance completeness, living-megafauna ambiguity, and singleton-source thinness. Its null result is interpretable because the closure table shows which support classes current candidates fail to satisfy.

Fifth, Track 3 contributes a convergence-pressure statistic with confound-diagnostic workflow. The important final state is cautious: accepted-key trait carrier rows exist, but no trait is controlled-ready under family-size, sampling-density, projection-loss, and source gates.

Sixth, Track 4 contributes a climate-substitution readiness diagnostic. It distinguishes occurrence recovery and crop/CWR staging from numeric climate vectors and validation-allowed expert comparators. That distinction prevents a same-genus or occurrence-only prior from becoming a recommendation.

Seventh, Track 5 contributes a neighborhood-completion prior and a source-bias null. The score can produce screening-prior rows, but the non-Duke temporal evidence gap prevents source-independent discovery claims under current evidence.

Eighth, Track 6 contributes a static adversarial benchmark, deterministic scoring harness, and local runtime availability check. Those artifacts can support future audited model runs, but they do not support model-performance findings until real free/open/local model responses are collected.

Ninth, the Atlas and taxonomy-results site contracts are user-facing contributions. They require rendered claims to distinguish observed evidence, enrichment rows, predicted or instrument rows, data-limited absence, and closed claim boundaries. That contract is essential because the interfaces expose hypotheses and diagnostics alongside source evidence without promoting them.

## Limitations, Residual Debt, And Future Work

The final audit's residual debt defines the remaining work. It records **10 validated** milestones and **1 in-progress** milestone. The in-progress milestone is `_manager/validator-warnings`, marked watch-only. The audit reports no critical, moderate, or minor findings and a green promise check.

| Anchor | Residual debt | Future work |
|---|---|---|
| `_manager/validator-warnings` | Inherited validator warnings remain watch-only; required validators exited 0 during the delta test pass. | Continue monitoring inherited validator warnings and reopen only if a validator exits nonzero or a warning points to a current delta artifact. |
| `baseline-plan-ledger-consistency` | The prior baseline plan-ledger consistency issue was not reopened by delta artifacts and is not counted as a new finding. | If the campaign is reopened, resolve exact active plan-ID coverage as maintenance before adding new scientific work. |
| `report-mtime-drift-24-32` | Reports 24-32 have post-baseline mtimes but were inspected and preserve no-promotion, header-only ledger boundaries. | No scientific reopen follows from timestamp drift alone. |
| `_plan/taxonomy-results-site-closure` | The closure-note mtime is later than its ledger event timestamp; content and tests support maintenance-boundary closure only. | Preserve the site as communication-only unless a future scientific pass supplies qualifying evidence and audited controls. |
| `session-transcript-coverage` | Full native transcripts for some session IDs were not fetched; local artifacts, reports, and ledger events were sufficient for delta verification. | Export relevant session transcripts if future public audit requirements demand provenance beyond local artifacts and ledger records. |

The scientific future-data requirements remain those in the final free-tier closure synthesis:

- Track 1 needs audited GBIF-to-WFO accepted-key projection or an admitted sidecar namespace plus source-density controls preserving event signal.
- Track 2 needs accepted-key modern-failure evidence, multi-source/source-class support, living-megafauna controls, and source-class-independent held-out recovery.
- Track 3 needs broader trait coverage, phylogenetically separated carrier sets, and family-size/sampling-density controls.
- Track 4 needs audited crop/CWR BIOCLIM summaries and disjoint candidate-level expert comparator rows.
- Track 5 needs accepted-key, dated, non-Duke taxon-compound rows across enough families/classes to estimate signatures without source collapse.
- Track 6 needs approved local model weights and runtime producing audited deterministic response rows with scorer diagnostics.

These are evidence requirements, not active promises. They are intentionally specific enough to prevent another same-axis retry that only regenerates the same null result.

The remaining gaps are explicit. The ledger causal summary input was empty. Some native session transcripts were unavailable. Reports 24-32 and the taxonomy-results closure note have timestamp drift, but the final audit classifies that drift as non-reopening debt. The master prediction and speculation ledgers are header-only. No per-track validated biological discovery was promoted. Later taxonomy-results and handoff artifacts are communication and maintenance deliverables, not new scientific evidence. The wall cap was not hit.

## Reproducibility And Artifact Map

The workspace contains a broad set of reproducibility artifacts. The key distinction is between files that define or test infrastructure, files that record track-local diagnostics, files that communicate closed results, and files that would support a promoted biological claim. At final synthesis, the infrastructure and diagnostic artifacts are substantial; the master prediction artifacts remain empty of data rows.

| Function | Representative artifacts | Reported state |
|---|---|---|
| Schema and source audit | `phytograph_schema.md`, `data_source_audit.md`, `coverage_report.md` | Produced and used to freeze the shared schema and evidence-boundary discipline. |
| Barrier 1 repair | `scripts/barrier1_common.py`, `scripts/barrier1_merge_substrate.py`, `scripts/barrier1_apply_synonyms.py`, `scripts/barrier1_deduplicate_edges.py`, `tools/validate_barrier1_substrate.py`, `phytograph_dataset/` | Initial freeze rejected; repaired substrate validated with 363,237 nodes and 641,183 retained hyperedges. |
| Barrier 2 integration | `tools/validate_barrier2_track_enrichment.py`, `reports/barrier2_wave2_integration_report.md`, `data/barrier2_track_enrichment_conformance.json` | Six enrichment branches passed conformance; no master prediction rows written. |
| Atlas integration | `botanical_atlas_site/build_atlas.py`, `botanical_atlas_site/page_contract.md`, `reports/barrier3_atlas_instrument_readiness.md`, `data/barrier3_atlas_instrument_contract.tsv` | Six track-local outputs exposed across 60,000 searchable taxon pages; Atlas remains an integration surface. |
| Track 1 | `tracks/track1/instruments/tci_spec.md`, `tracks/track1/instruments/build_tci.py`, `tracks/track1/outputs/tci_per_taxon.tsv`, `tracks/track1/data/reticulation_reopen_candidate_events.tsv`, `tracks/track1/data/reticulation_reopen_join_diagnostics.tsv` | TCI and reopen diagnostics exist; H1 remains data-limited and non-reopened. |
| Track 2 | `tracks/track2/data/track2_wave4_validation_outcomes.tsv`, `tracks/track2/reports/track2_wave4_validation_closure.md` | H2 not supported or data-limited under current accepted-key and ablation controls. |
| Track 3 | `tracks/track3/data/track3_wave4_validation_outcomes.tsv`, `tracks/track3/data/track3_wave4_validation_summary.json`, `tracks/track3/data/convergence_pressure_scores.tsv` | Trait rows exist, but no controlled-ready convergence claim was promoted. |
| Track 4 | `tracks/track4/data/crop_cwr_bioclim_vectors.tsv`, `tracks/track4/data/crop_cwr_validation_pairs.tsv`, `tracks/track4/reports/track4_barrier4_closure.md` | Climate substitution not computable under current evidence. |
| Track 5 | `tracks/track5/data/track5_wave4_validation_outcomes.tsv`, `tracks/track5/data/source_ablation_results.tsv`, `tracks/track5/reports/track5_wave4_temporal_source_closure.md` | H5 not validated; source limitations block screening-priority claims. |
| Track 6 | `tracks/track6/data/probe_results.tsv`, `tracks/track6/data/local_model_availability.json`, `tracks/track6/reports/track6_barrier4_closure.md` | Static benchmark and deterministic controls exist; no audited free/open/local model-response rates. |
| Reopen and final closure | `reports/reopen/reopen_evidence_gate.md`, `data/reopen/reopen_branch_matrix.tsv`, `reports/reopen/final_free_tier_closure_synthesis.md`, `data/reopen/final_free_tier_track_status.tsv` | Defines reopen predicates and the canonical six-track final free-tier closure table. |
| Public communication and handoff | `taxonomy_results_site/`, `taxonomy_results_site/data/site_summary.json`, `reports/taxonomy_results_site_qa.md`, `reports/taxonomy_results_site_closure_note.md`, `reports/final_campaign_handoff_manifest.md` | Validated as communication, expert-review, and handoff surfaces over closed statuses. |
| Master ledgers | `prediction_ledger.tsv`, `speculation_ledger.tsv` | Header-only; no campaign-level biological prediction or speculation rows promoted. |

These files let a reviewer reproduce the reported boundary: PhytoGraph built a repaired substrate, track-local instruments, Atlas integration, validation outputs, ablation outputs, closure reports, reopen gates, a public results site, and a final handoff manifest. They do not support a claim that the campaign validated one prediction per track.

## Conclusions

PhytoGraph produced a disciplined discovery substrate and a conservative evidence architecture, but it did not produce the validated per-track discovery ledger promised by the original directive. The final state is not a polished catalog pretending to be a prediction engine. It is a typed hypergraph substrate, a six-track Atlas integration surface, track-local instruments and diagnostics, validation and falsification records, controlled reopen gates, a public communication site, and a final handoff manifest.

The strongest durable result is the combination of schema discipline, accepted-key repair, Atlas evidence labeling, source-sensitive validation, explicit reopen gates, and communication artifacts that preserve scientific boundaries. The campaign preserved distinctions that matter for botanical inference: taxonomy versus phylogeny versus reticulate inheritance, trait membership versus convergence, crop pedigree versus climate substitution, phytochemical detection versus bioactivity, ethnobotanical use versus clinical efficacy, media evidence versus biology, and benchmark controls versus model responses.

The final track outcomes are bounded. H1 remains sidecar-readiness uncontrolled. H2 is not supported or data-limited under current controls. H3 is confound-limited. H4 remains data-limited because climate substitution lacks numeric bioclim vectors and validation comparator rows. H5 remains source-biased. H6 remains environment-limited because no audited free/open/local model responses exist.

The final audit status is cleaner than the baseline report: **10 validated, 1 in-progress · promise_check=green**, with no critical, moderate, or minor findings and no reconciliation events emitted. The only in-progress item is inherited validator warnings under watch-only treatment. The campaign can be reopened productively, but only with evidence that meets the gates already defined. Until then, the master prediction and speculation ledgers correctly remain header-only.

## References

[1] World Flora Online, "WFO Plant List API," World Flora Online, 2026. https://list.worldfloraonline.org/index.php (accessed 2026-05-17).

[2] World Flora Online, "Name Matching REST API," World Flora Online, 2026. https://list.worldfloraonline.org/matching_rest.php (accessed 2026-05-17).

[3] World Flora Online, "GraphQL API," World Flora Online, 2026. https://list.worldfloraonline.org/gql_index.php (accessed 2026-05-17).

[4] The World Flora Online Consortium et al., "World Flora Online Plant List December 2025," Zenodo, 2025. https://doi.org/10.5281/zenodo.18007552 (accessed 2026-05-17).

[5] World Flora Online, "The WFO Plant List," World Flora Online, 2026. https://about.worldfloraonline.org/plant-list/ (accessed 2026-05-17).

[6] GBIF Secretariat, "GBIF API Reference," GBIF Technical Documentation, 2026. https://techdocs.gbif.org/en/openapi/ (accessed 2026-05-17).

[7] GBIF Secretariat, "Species API," GBIF Technical Documentation, 2026. https://techdocs.gbif.org/en/openapi/v1/species (accessed 2026-05-17).

[8] GBIF Secretariat, "Occurrence API," GBIF Technical Documentation, 2026. https://techdocs.gbif.org/en/openapi/v1/occurrence (accessed 2026-05-17).

[9] GBIF Secretariat, "API Downloads," GBIF Technical Documentation, 2026. https://techdocs.gbif.org/en/data-use/api-downloads (accessed 2026-05-17).

[10] GBIF Secretariat, "Citation Guidelines," GBIF, 2026. https://www.gbif.org/citation-guidelines (accessed 2026-05-17).

[11] GBIF Secretariat, "Terms of Use," GBIF, 2026. https://www.gbif.org/terms (accessed 2026-05-17).

[12] Open Tree of Life, "Link to current Open Tree API," Open Tree of Life, 2026. https://opentreeoflife.github.io/develop/api (accessed 2026-05-17).

[13] OpenTreeOfLife, "TNRS API v3," Open Tree of Life germinator wiki, 2022. https://github.com/OpenTreeOfLife/germinator/wiki/TNRS-API-v3 (accessed 2026-05-17).

[14] Open Tree of Life, "Licenses," Open Tree of Life, 2026. https://tree.opentreeoflife.org/about/licenses (accessed 2026-05-17).

[15] Cody E. Hinchliff, Stephen A. Smith, James F. Allman, et al., "Synthesis of Phylogeny and Taxonomy into a Comprehensive Tree of Life," Proceedings of the National Academy of Sciences, 2015. https://doi.org/10.1073/pnas.1423041112 (accessed 2026-05-17).

[16] BIEN, "RBIEN," Botanical Information and Ecology Network, 2026. https://bien.nceas.ucsb.edu/bien/tools/rbien/ (accessed 2026-05-17).

[17] Brian Maitner, "BIEN: Tools for Accessing the Botanical Information and Ecology Network Database," R-universe package manual, version 1.2.7, 2026. https://cran.r-universe.dev/BIEN/doc/manual.html (accessed 2026-05-17).

[18] TRY, "TRY Plant Trait Database," TRY, 2026. https://www.try-db.org/TryWeb/Home.php (accessed 2026-05-17).

[19] TRY, "Intellectual Property Guidelines for the TRY Plant Trait Database," TRY, updated 2023. https://www.try-db.org/TryWeb/TRY_Intellectual_Property_Guidelines.pdf (accessed 2026-05-17).

[20] TRY, "Free Access TRY Data," TRY, 2026. https://www.try-db.org/TryWeb/TRY_Policy_Free_Access_Data.pdf (accessed 2026-05-17).

[21] Dengyong Zhou, Jiayuan Huang, and Bernhard Scholkopf, "Learning with Hypergraphs: Clustering, Classification, and Embedding," Advances in Neural Information Processing Systems 19, 2006. https://papers.nips.cc/paper/3128-learning-with-hypergraphs-clustering-classification-and-embedding (accessed 2026-05-17).

[22] Sameer Agarwal, Kristin Branson, and Serge Belongie, "Higher Order Learning with Graphs," International Conference on Machine Learning, 2006. https://doi.org/10.1145/1143844.1143847 (accessed 2026-05-17).

[23] Carlos N. Silla Jr. and Alex A. Freitas, "A Survey of Hierarchical Classification across Different Application Domains," Data Mining and Knowledge Discovery, 2011. https://doi.org/10.1007/s10618-010-0175-9 (accessed 2026-05-17).

[24] Roderic D. M. Page, "Ozymandias: A Biodiversity Knowledge Graph," PeerJ, 2019. https://peerj.com/articles/6739/ (accessed 2026-05-17).

[25] Lyubomir Penev, Teodor Georgiev, Pavel Stoev, et al., "OpenBiodiv: A Knowledge Graph for Literature-Extracted Linked Open Data in Biodiversity Science," Publications, 2019. https://www.mdpi.com/2304-6775/7/2/38 (accessed 2026-05-17).

[26] Jens Kattge, Gerhard Boenisch, Sandra Diaz, et al., "TRY Plant Trait Database - Enhanced Coverage and Open Access," Global Change Biology, 2020. https://doi.org/10.1111/gcb.14904 (accessed 2026-05-17).

[27] Royal Botanic Gardens, Kew, "Plants of the World Online," Kew Science, 2026. https://powo.science.kew.org/ (accessed 2026-05-17).

[27] CCDB, "Chromosome Counts Database (CCDB)," Tel Aviv University, version 1.66.6, 2026. https://ccdb.tau.ac.il/ (accessed 2026-05-17).

[28] Anna Rice, Lior Glick, Shiran Abadi, et al., "The Chromosome Counts Database (CCDB) — a community resource of plant chromosome numbers," New Phytologist, 2015. https://doi.org/10.1111/nph.13191 (accessed 2026-05-17).

[29] Ilia J. Leitch, Emma Johnston, Jaume Pellicer, Oriane Hidalgo, and Michael D. Bennett, "Plant DNA C-values Database," Royal Botanic Gardens, Kew, 2026. https://cvalues.science.kew.org/ (accessed 2026-05-17).

[30] Troy E. Wood, Naoki Takebayashi, Michael S. Barker, et al., "The frequency of polyploid speciation in vascular plants," Proceedings of the National Academy of Sciences, 2009. https://doi.org/10.1073/pnas.0811575106 (accessed 2026-05-17).

[31] Wikidata, "Wikidata Query Service SPARQL endpoint," Wikimedia Foundation, 2026. https://query.wikidata.org/ (accessed 2026-05-17).

[32] Wikimedia Commons, "MediaWiki Action API," Wikimedia Foundation, 2026. https://commons.wikimedia.org/w/api.php (accessed 2026-05-17).

[31] Daniel Falster, Rachael Gallagher, Elizabeth Wenk, Herve Sauquet, et al., "AusTraits: a curated plant trait database for the Australian flora," Zenodo, version 6.0.0, 2024. https://doi.org/10.5281/zenodo.11188867 (accessed 2026-05-17).

[38] James A. Duke, "Dr. Duke's Phytochemical and Ethnobotanical Databases," Ag Data Commons, 2023. https://agdatacommons.nal.usda.gov/articles/dataset/Dr_Duke_s_Phytochemical_and_Ethnobotanical_Databases/24660351 (accessed 2026-05-17).

[39] Louis Potok, "Native American Ethnobotany Database mirror," Datasette mirror of Moerman NAEB data, 2026. https://naeb.louispotok.com/naeb (accessed 2026-05-17).

[40] KNApSAcK Family, "KNApSAcK Core System," KNApSAcK Family Databases, 2026. http://www.knapsackfamily.com/KNApSAcK/ (accessed 2026-05-17).

[41] Zeng et al., "NPASS: Natural Product Activity and Species Source Database," NPASS, 2026. https://bidd.group/NPASS/ (accessed 2026-05-17).

[42] EMBL-EBI, "ChEBI: Chemical Entities of Biological Interest," EMBL-EBI, 2026. https://www.ebi.ac.uk/chebi/ (accessed 2026-05-17).

[43] PROTA Foundation, "Plant Resources of Tropical Africa," PROTA4U, 2026. https://prota.prota4u.org/ (accessed 2026-05-17).

[44] PlantUse, "Plant Resources of South-East Asia (PROSEA)," PlantUse, 2026. https://uses.plantnet-project.org/en/PROSEA (accessed 2026-05-17).

[45] GBIF Secretariat, "Species match API," GBIF API, 2026. https://api.gbif.org/v1/species/match (accessed 2026-05-18).

[46] Crossref, "REST API," Crossref, 2026. https://api.crossref.org/ (accessed 2026-05-18).

[47] OpenAlex, "Works API," OpenAlex, 2026. https://docs.openalex.org/api-entities/works (accessed 2026-05-18).

[48] Jakob de Sousa Leite et al., "Ancient hybridizations among the ancestral genomes of bread wheat," Science, 2014. https://doi.org/10.1126/science.1250092

[49] Rachel Brenchley et al., "Analysis of the bread wheat genome using whole-genome shotgun sequencing," Nature, 2012. https://doi.org/10.1038/nature11650

[50] Boulos Chalhoub et al., "Early allopolyploid evolution in the post-Neolithic Brassica napus oilseed genome," Science, 2014. https://doi.org/10.1126/science.1253435

[51] David J. Bertioli et al., "The genome sequence of segmental allotetraploid peanut Arachis hypogaea," Nature Genetics, 2019. https://doi.org/10.1038/s41588-019-0405-z

[52] Andrew H. Paterson et al., "Repeated polyploidization of Gossypium genomes and the evolution of spinnable cotton fibres," Nature, 2012. https://doi.org/10.1038/nature11798

[53] Philippe Lashermes et al., "Molecular characterisation and origin of the Coffea arabica L. genome," Theoretical and Applied Genetics, 1999. https://doi.org/10.1007/s001220051041

[54] Nicolas Sierro et al., "The tobacco genome sequence and its comparison with those of tomato and potato," Nature Communications, 2014. https://doi.org/10.1038/ncomms4833

[55] Patrick P. Edger et al., "Origin and evolution of the octoploid strawberry genome," Nature Genetics, 2019. https://doi.org/10.1038/s41588-019-0356-4

[56] Malika L. Ainouche et al., "Polyploid evolution in Spartina: dealing with highly redundant hybrid genomes," Biological Journal of the Linnean Society, 2004. https://doi.org/10.1111/j.1095-8312.2004.00333.x

[57] Pamela S. Soltis et al., "The recent and recurrent origin of allopolyploid species in Tragopogon," Proceedings of the National Academy of Sciences, 2004. https://doi.org/10.1073/pnas.0405153101

[58] Marcus A. Koch et al., "Sequencing of the genus Arabidopsis identifies a complex history of nonbifurcating speciation and abundant trans-specific polymorphism," Nature Genetics, 2016. https://doi.org/10.1038/ng.3617

[59] Loren H. Rieseberg et al., "Major ecological transitions in wild sunflowers facilitated by hybridization," Science, 2003. https://doi.org/10.1126/science.1086949

[60] Michael L. Arnold, "Natural hybridization in Louisiana irises: genetic variation and ecological determinants," Evolution, 1990. https://doi.org/10.2307/2445221

[61] Amandine Cornille et al., "New insight into the history of domesticated apple: secondary contribution of the European wild apple to the genome of cultivated varieties," PLOS Genetics, 2012. https://doi.org/10.1371/journal.pgen.1002703

[62] Guohong Albert Wu et al., "Sequencing of diverse mandarin, pummelo and orange genomes reveals complex history of admixture during citrus domestication," Nature Biotechnology, 2014. https://doi.org/10.1038/nbt.2906

[63] Guohong Albert Wu et al., "Genomics of the origin and evolution of Citrus," Nature, 2018. https://doi.org/10.1038/nature25447

[64] Christian Ritz et al., "Evolution by reticulation: European dogroses originated by multiple hybridization across the genus Rosa," Molecular Ecology, 2005. https://doi.org/10.1111/j.1365-294X.2005.02730.x

[65] Thibault Leroy et al., "Extensive recent secondary contacts between four European white oak species," New Phytologist, 2019. https://doi.org/10.1111/nph.16069

[66] Xavier Perrier et al., "Multidisciplinary perspectives on banana domestication," Proceedings of the National Academy of Sciences, 2011. https://doi.org/10.1073/pnas.1102001108

[67] Martin A. Lysak et al., "The emerging biofuel crop Camelina sativa retains a highly undifferentiated hexaploid genome structure," Nature Communications, 2014. https://doi.org/10.1038/ncomms4706

[68] Mansukh C. Wani, Harold L. Taylor, Monroe E. Wall, Philip Coggon, and Andrew T. McPhail, "Plant antitumor agents. VI. Isolation and structure of taxol, a novel antileukemic and antitumor agent from Taxus brevifolia," Journal of the American Chemical Society, 1971. https://doi.org/10.1021/ja00738a045 (accessed 2026-05-18).

[69] Richard K. Haynes, "The biosynthesis of artemisinin (Qinghaosu) and the phytochemistry of Artemisia annua L. (Qinghao)," Molecules, 2010. https://pubmed.ncbi.nlm.nih.gov/21030913/ (accessed 2026-05-18).

[70] D. L. Klayman et al., "Isolation of Artemisinin (Qinghaosu) from Artemisia annua Growing in the United States," Journal of Natural Products, 1984. https://doi.org/10.1021/np50034a027 (accessed 2026-05-18).

[71] M. H. M. Sharaf and F. A. K. Al-Yahya, "Isolation of Reserpine from Vinca rosea Linn.," Nature, 1958. https://www.nature.com/articles/181552a0 (accessed 2026-05-18).

[72] JAMA, "Quinin: 1820-1920," Journal of the American Medical Association, 1920. https://jamanetwork.com/journals/jama/fullarticle/223878 (accessed 2026-05-18).

[73] Science Museum Group, "Original preparation of quinine by Pelletier and Caventou," Science Museum Group Collection, 2026. https://collection.sciencemuseumgroup.org.uk/objects/co184085/original-preparation-of-quinine-by-pelletier-and-caveton (accessed 2026-05-18).

[74] Andrea L. Devereaux, Susan L. Mercer, and Christopher W. Cunningham, "DARK Classics in Chemical Neuroscience: Morphine," ACS Chemical Neuroscience, 2018. https://doi.org/10.1021/acschemneuro.8b00150 (accessed 2026-05-18).

[75] M. J. Davies, "Atropa belladonna," Heart, 2002. https://heart.bmj.com/content/88/3/215.2 (accessed 2026-05-18).

[76] D. G. Grahame-Smith, "Digoxin comes from Digitalis lanata," BMJ, 1996. https://www.bmj.com/content/312/7035/912.1 (accessed 2026-05-18).

[77] Royal Society, "An Account of the Success of the Bark of the Willow in the Cure of Agues," Philosophical Transactions of the Royal Society of London, 1763. https://royalsocietypublishing.org/doi/10.1098/rstl.1763.0033 (accessed 2026-05-18).
