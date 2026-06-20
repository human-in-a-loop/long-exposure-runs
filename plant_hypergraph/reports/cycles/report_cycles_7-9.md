---
title: "PhytoGraph — cycles 7-9"
date: "2026-05-17"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# PhytoGraph — cycles 7-9

## Abstract

Cycles 7-9 moved PhytoGraph from a repaired shared substrate into Barrier 2-ready Wave 2 enrichment.

Cycle 7 repaired and validated the Barrier 1 canonical-member projection defect that had blocked downstream work. The repaired substrate now propagates synonym-resolved accepted keys into retained hyperedges and deduplicates on full typed member sets rather than raw taxon names. The substrate validator passed with 363,237 nodes and 641,183 retained hyperedges.

Cycle 8 launched Wave 2 track enrichment across all six tracks. Each branch wrote only to its own `tracks/trackN/` namespace, preserved the frozen substrate as read-only, and kept enrichment distinct from prediction. The branches produced per-track `ENRICHMENT_AUDIT.md` files and machine-readable enrichment outputs.

Cycle 9 integrated the six Wave 2 branches as Barrier 2 candidate inputs. The conformance validator passed for all six tracks, the combined track regression suite passed with 41 tests, `prediction_ledger.tsv` remained empty, and the integration report preserved each branch’s evidence boundaries and data-limited caveats.

The result is not a predictive-instrument milestone. No Track 1 reticulation index, Track 2 ranker, Track 3 convergence-pressure statistic, Track 4 crop-substitution engine, Track 5 chemodiversity predictor, or Track 6 live model probe was built. The campaign is now positioned for Barrier 2 review and later Wave 3 instrument construction.

## Introduction

The PhytoGraph campaign depends on a shared typed hypergraph substrate before any track-specific predictive instruments can be trusted. Earlier cycles created Wave 1 source staging and attempted a Barrier 1 substrate freeze, but that freeze failed audit because canonical keys were not propagated back into retained hyperedges and deduplication collapsed distinct biological assertions.

Cycles 7-9 address the transition from substrate repair to track enrichment:

- **Cycle 7** repaired Barrier 1 canonical-member projection and deduplication.
- **Cycle 8** launched six independent Wave 2 enrichment branches.
- **Cycle 9** integrated those branches into a Barrier 2 conformance package.

Key terms:

- **Barrier 1**: the point where staged source rows become the shared read-only substrate.
- **Barrier 2**: the point where all track-specific enrichment outputs are checked for schema conformance, provenance discipline, duplicate-edge issues, and prediction-boundary discipline.
- **Enrichment**: observed or cited evidence attached to the frozen substrate. Enrichment is not prediction.
- **Prediction ledger**: the master ledger where falsifiable model-generated predictions will later be filed. It stayed empty in these cycles.

## Approach

The cycles followed the campaign’s dependency discipline. Cycle 7 kept Wave 1 source rows fixed and repaired only the Barrier 1 substrate pipeline. Cycle 8 then treated the repaired substrate as read-only and launched six track-local enrichment branches. Cycle 9 did not build instruments; it validated that branch outputs were suitable candidate inputs for Barrier 2.

The integration checks used:

```bash
python3 tools/validate_barrier2_track_enrichment.py
python3 -m pytest -q tests/test_track1_reticulation_enrichment.py tracks/track2/tests/test_ghost_enrichment.py tracks/track3/tests/test_track3_enrichment.py tracks/track4/tests/test_domestication_enrichment.py tracks/track5/tests/test_track5_enrichment.py tests/test_track6_offline_probe.py
python3 tools/validate_barrier1_substrate.py
python3 -m long_exposure.tools.promise_check <run-root>
python3 -m long_exposure.tools.org_check <run-root>
```

The reported results were:

```text
PASS: Barrier 2 track enrichment conformance (6 tracks checked)
41 passed in 20.87s
PASS: Barrier 1 substrate validation (363237 nodes, 641183 retained hyperedges)
```

## Cycle 7: Barrier 1 Repair

Cycle 7 began with researcher session `00ecd932-4314-43ed-8a94-b64661660769`, which scoped the remaining Barrier 1 blocker as canonical-member projection loss. The prior broken pipeline had deduplicated large source frames using raw-name-only member sets, so same-taxon rows with different traits or compounds could collapse.

Worker session `e63dca56-ad6d-4877-9e8c-6cf590e38f5e` repaired:

- `scripts/barrier1_common.py`
- `scripts/barrier1_merge_substrate.py`
- `scripts/barrier1_apply_synonyms.py`
- `scripts/barrier1_deduplicate_edges.py`
- `scripts/barrier1_write_reports.py`
- `tools/validate_barrier1_substrate.py`
- `tests/test_barrier1_canonical_members.py`
- `tests/test_barrier1_merge.py`

The worker produced:

- `substrate/BARRIER1_REPAIR_REPORT.md`
- `phytograph_dataset/canonical_member_audit.tsv`
- `phytograph_dataset/resolved_key_propagation_audit.tsv`
- `phytograph_dataset/dedup_collision_audit.tsv`
- `phytograph_dataset/dedup_before_after_by_edge_type.tsv`
- `substrate/barrier1_dedup_before_after.png`
- `substrate/barrier1_canonical_member_widths.png`
- `reports/barrier1_canonical_member_repair_validation.md`

The repaired validator passed:

```text
PASS: Barrier 1 substrate validation (363237 nodes, 641183 retained hyperedges)
10 passed in 31.86s
```

Auditor session `67171417-7a93-4bef-bcf8-16b65a264c6d` validated the repair. The decisive probes were:

| Probe | Result |
|---|---:|
| Track 3 resolved retained rows with blank accepted key | 0 |
| Track 3 resolved retained rows still pending crosswalk | 0 |
| Track 3 rows missing accepted key in canonical members | 0 |
| Track 3 width-one canonical member sets | 0 |
| Track 5 resolved retained rows with blank accepted key | 0 |
| Track 5 resolved retained rows still pending crosswalk | 0 |
| Track 5 rows missing accepted key in canonical members | 0 |
| Track 5 width-one canonical member sets | 0 |
| `Acaena x ovina` retained Track 3 rows | 14 |
| `Acaena x ovina` unique canonical member sets | 14 |

The repair also corrected the Tier 0 reporting distinction: accepted taxonomy rows are 60,000, while 113,582 synonym rows are separate synonym coverage, not accepted taxa.

## Cycle 8: Wave 2 Track Enrichment

Cycle 8 researcher session `3edad7dc-2222-4bec-8bc0-2739c0c80d5b` launched the first post-Barrier-1 fan-out. The shared rules were: read `phytograph_dataset/` as frozen, write only under each track namespace, do not change schema v1.0, do not independently normalize synonyms, do not emit predictive instruments, and preserve provenance, license, caveats, and evidence scope.

### Track 1 Reticulation

Track 1 projected the 28-row M1.3 reticulation seed set onto the repaired Barrier 1 accepted-key namespace. It remained data-limited.

| Edge type | Staged rows | Resolved | Pending |
|---|---:|---:|---:|
| `chromosome_count_assertion` | 12 | 2 | 10 |
| `ploidy_state_assertion` | 6 | 1 | 5 |
| `hybridization_event` | 1 | 0 | 1 |
| `polyploidization_event` | 4 | 0 | 4 |
| `reticulate_inheritance_evidence` | 5 | 0 | 5 |
| **Total** | **28** | **3** | **25** |

The audit explicitly forbids using these rows to compute a `tree_compatibility_index` or a planet-scale reticulation index. The canonical validation seeds for Track 1 remain mostly `pending_crosswalk`.

![Track 1 reticulation enrichment coverage by edge type.](tracks/track1/plots/reticulation_coverage_by_edge_type.png)

![Track 1 reticulation source and license mix.](tracks/track1/plots/reticulation_source_license_mix.png)

### Track 2 Ghost Partners

Track 2 converted cited paleobotany and Janzen-Martin candidate rows into Track 2-local seed evidence. It did not infer anachronism predictions.

| Metric | Value |
|---|---:|
| Candidate seed edges | 31 |
| Candidate classes | 6 |
| Unique plant names | 24 |
| Unique extinct-fauna nodes in seed edges | 11 |
| Pending-crosswalk seed rows | 25 |
| Resolved seed rows | 6 |
| Range-context support edges | 52 |
| Extinct-fauna support nodes | 237 |
| Paleo-context support nodes | 80 |
| Modern-disperser context nodes | 49 |
| Inferred candidate rows emitted | 0 |
| Prediction-ledger rows written | 0 |

Every seed row was marked `literature_curated_seed`, `prediction_status=not_prediction`, `enters_prediction_ledger=false`, and `inferred_anachronism_claim=false`.

### Track 3 Convergence

Track 3 projected the repaired substrate’s AusTraits-derived trait, fruit morphology, and life-form edges onto a canonical Track 3 trait axis. It emitted `track3_trait_membership` rows only and no `convergence_signature` rows.

The output contained 209,297 memberships. Coverage by canonical trait included 12 nonzero traits and three zero-data traits (`ant_domatia`, `carnivory`, `parasitism`). Only `fleshy_fruit` and `capsule` cleared the 500 accepted-taxon floor.

| Trait | Retained edges | Accepted taxa | Pending-crosswalk taxa | Floor met |
|---|---:|---:|---:|---|
| `fleshy_fruit` | 4,748 | 716 | 3,371 | yes |
| `capsule` | 9,074 | 543 | 8,531 | yes |
| `c4_photosynthesis` | 1,378 | 157 | 1,219 | no |
| `myrmecochory` | 2,195 | 288 | 849 | no |
| `_other` | 184,218 | 3,252 | 29,285 | diagnostic bucket |

The `_other` bucket was the main integration divergence. It is large because AusTraits includes many labels outside the Track 3 canonical axis. The cycle 9 integration fixed the validator interpretation: `_other` is recorded as a Barrier 2 review item, not treated as a canonical trait floor.

![Track 3 trait coverage by family.](tracks/track3/data/track3_trait_coverage_by_family.png)

### Track 4 Domestication

Track 4 attached M1.6 domestication staging rows to accepted substrate keys at data-limited scale. It retained six observed hyperedges: two `crop_pedigree`, two `vavilov_center_hyperedge`, and two `cultivation_or_domestication`.

| Category | Staged rows | Joined rows | Unjoined rows | Main shortfall |
|---|---:|---:|---:|---|
| `crop_pedigree` | 43 | 2 | 41 | focal accepted-key gaps |
| `vavilov_center_hyperedge` | 43 | 2 | 41 | focal accepted-key gaps |
| `cultivation_or_domestication` | 104 | 2 | 102 | focal accepted-key gaps |
| `crop_wild_relative_pairs` | 69 | 3 | 66 | crop and/or wild ancestor accepted-key gaps |
| `heldout_validation_seed` | 22 | 2 | 20 | held-out focal accepted-key gaps |
| `climate_envelope` | 375 | 36 | 339 | all rows data-limited until bioclim extraction |

The held-out validation seed retained zero species-level overlap with retained crop-pedigree training evidence. Climate rows remained placeholders; no row supported climate suitability prediction.

![Track 4 joined and unjoined enrichment counts by evidence category.](tracks/track4/data/track4_enrichment_coverage.png)

### Track 5 Chemodiversity

Track 5 projected resolved phytochemical and ethnobotanical evidence into its namespace, preserved a compound-level bioactivity firewall, and foregrounded source-density diagnostics.

Key outputs:

| Artifact | Rows | Purpose |
|---|---:|---|
| `track5_enrichment_edges.parquet` | 23,524 | Resolved taxon-keyed phyto and ethnobotany projection |
| `track5_bioactivity_assertions.parquet` | 28,733 | Compound-level bioactivity, no taxon column |
| `track5_compound_class_membership.parquet` | 9,500 | Duke CHEMCLASS mapping |
| `family_chemistry_coverage_summary.tsv` | 91 families | Per-family coverage |
| `per_taxon_screening_intensity.tsv` | 1,258 taxa | Source/compound/paper intensity |

The dominant finding is source concentration. Dr. Duke accounted for 99.96% of the combined enrichment plus bioactivity signal. Removing Dr. Duke eliminated all family-cells above the 100-assertion floor, all bioactivity-class signal, and 99.2% of taxa with assertions.

![Top-30 Track 5 families by phytochemical assertion count, colored by Dr. Duke share.](tracks/track5/data/family_chemistry_coverage_top30.png)

![Distribution of Dr. Duke source share across retained Track 5 families.](tracks/track5/data/dr_duke_dominance_histogram.png)

![Track 5 leave-one-source-out coverage; Duke removal collapses all floor-clearing family-cells.](tracks/track5/data/leave_one_source_out_coverage.png)

![Track 5 family by compound-class matrix.](tracks/track5/data/family_compound_class_heatmap.png)

Track 5 did not emit `chemodiversity_signature` rows and did not convert ethnobotanical use into clinical bioactivity.

### Track 6 Offline Probe

Track 6 built a static, free/open-source/offline probe question bank and ground-truth edge layer. It did not call or configure paid/key-gated providers and did not use the superseded M1.8 live-provider harness.

| Category | Questions |
|---|---:|
| `convergence_detection` | 30 |
| `ghost_partner_reasoning` | 30 |
| `hybrid_pedigree` | 30 |
| `phytochemistry_safety` | 30 |
| `region_conditional` | 30 |
| `synonym_confusion` | 30 |
| `toxicity_lookalike_media_scope` | 30 |
| **Total** | **210** |

The branch also produced 210 schema-shaped `adversarial_probe_edge` rows. Every row uses `foundation_model_response:offline_unrun`, which is a placeholder, not a model output. Live or local-open model scoring remains future M3.T6 work.

## Cycle 9: Barrier 2 Integration

Cycle 9 worker session `7e8a8f0a-786b-484b-8c69-d41b89087cc2` integrated the six Wave 2 branches and produced:

- `tools/validate_barrier2_track_enrichment.py`
- `data/barrier2_track_enrichment_conformance.json`
- `reports/barrier2_wave2_integration_report.md`

A ledger event was appended: `b0c3ef94-5b71-4b59-9e66-6b50514386e4`.

The integration report states that all six branches are candidate Barrier 2 inputs, not predictive instruments. `prediction_ledger.tsv` remains empty.

| Track | Barrier 2 integration status | Integrated finding |
|---|---|---|
| Track 1 | `ready_data_limited` | 28 reticulation seed rows retained; 25 remain pending crosswalk |
| Track 2 | `ready_seed_scale` | 31 cited seeds and 52 range-context supports remain not-prediction |
| Track 3 | `ready_with_conformance_review_item` | 209,297 trait memberships retained; `_other` bucket requires explicit interpretation |
| Track 4 | `ready_data_limited` | 6 observed domestication edges retained; CWR and bioclim evidence remain data-limited |
| Track 5 | `ready_with_source_bias_warning` | 23,524 resolved taxon-keyed rows retained; Duke share is 0.999598 |
| Track 6 | `ready_offline_static` | 210 offline questions and 210 ground-truth rows retained; no live responses |

## Findings

The core substrate risk from earlier cycles is resolved. Barrier 1 now passes validation with full canonical-member projection and retained accepted-key propagation.

Wave 2 enrichment is successful as enrichment, not as prediction. Each track produced evidence-bearing artifacts in its own namespace, and the integration validator confirmed six-track conformance.

The strongest cross-track constraint is data limitation. Track 1 is seed-scale; Track 4 has no observed bioclim vectors; Track 5 is dominated by Dr. Duke; Track 6 is offline-static only; Track 3 has a large `_other` diagnostic bucket; Track 2 remains literature-seed scale.

The master prediction boundary held. No branch wrote predictive instrument outputs, and `prediction_ledger.tsv` remained empty.

## Discussion

Cycles 7-9 are best understood as infrastructure-to-enrichment transition cycles. They did not produce falsifiable biological predictions yet. Their contribution is that the campaign now has a validated substrate and six track-local enrichment layers with explicit caveats.

The most important design discipline preserved across the work is separation of evidence from prediction. Track 2 seed hypotheses are not inferred ghost-partner predictions. Track 3 trait memberships are not convergence signatures. Track 4 pedigree and Vavilov edges are not crop-substitution recommendations. Track 5 compound bioactivity is not taxon-level clinical efficacy. Track 6 offline-unrun edges are not model responses.

The next campaign step should either move into Barrier 2 schema/provenance review or start carefully bounded Wave 3 instrument design with the recorded data-limited constraints carried forward.

## Open Questions

1. Should Track 1 run a side-wave accepted-key recovery for canonical polyploid validation seeds before any reticulation index is attempted?
2. Should Track 3 treat `_other` as a diagnostic-only bucket permanently, or should a side-wave refine noncanonical AusTraits labels into additional instrument axes?
3. Can Track 4 recover enough CWR and bioclim evidence to support a Crop Substitution Engine, or must M3.T4 remain a design-only artifact?
4. Can Track 5 obtain non-Duke counterfactual coverage from NAEB synonym recovery, NPASS, KNApSAcK, or ChEBI before prediction?
5. When Track 6 moves beyond static construction, which free/open/local model path satisfies the no paid/key-gated constraint?

## References

No external references are newly cited in this cycles 7-9 report. Source references accumulated by ingestion and enrichment agents remain in `REFERENCES.md`.

## Appendix: Implementation Details

### Session Inventory

| Cycle | Source ID | Role | Contents |
|---:|---|---|---|
| 7 | `00ecd932-4314-43ed-8a94-b64661660769` | Researcher | Barrier 1 canonical-member repair brief |
| 7 | `e63dca56-ad6d-4877-9e8c-6cf590e38f5e` | Worker | Repaired Barrier 1 scripts, regenerated substrate outputs, ran validators |
| 7 | `67171417-7a93-4bef-bcf8-16b65a264c6d` | Auditor | Validated Barrier 1 repair |
| 8 | `3edad7dc-2222-4bec-8bc0-2739c0c80d5b` | Researcher | Wave 2 six-track fan-out brief |
| 9 | `7e8a8f0a-786b-484b-8c69-d41b89087cc2` | Worker | Barrier 2 post-merge integration and conformance validation |

### Code and Artifact Inventory

| File | Lines | Purpose |
|---|---:|---|
| `tools/validate_barrier2_track_enrichment.py` | 247 | Cross-track Barrier 2 enrichment conformance validator |
| `reports/barrier2_wave2_integration_report.md` | 82 | Human integration report for six Wave 2 branches |
| `tracks/track1/docs/ENRICHMENT_AUDIT.md` | 251 | Track 1 reticulation enrichment audit |
| `tracks/track2/docs/ENRICHMENT_AUDIT.md` | 130 | Track 2 ghost-partner seed enrichment audit |
| `tracks/track3/docs/ENRICHMENT_AUDIT.md` | 269 | Track 3 convergence trait-membership audit |
| `tracks/track4/docs/ENRICHMENT_AUDIT.md` | 57 | Track 4 domestication enrichment audit |
| `tracks/track5/docs/ENRICHMENT_AUDIT.md` | 297 | Track 5 chemodiversity enrichment audit |
| `tracks/track6/docs/ENRICHMENT_AUDIT.md` | 72 | Track 6 offline probe construction audit |
| `data/barrier2_track_enrichment_conformance.json` | n/a | Machine-readable PASS summary |

### Test Results

Cycle 7 Barrier 1 repair:

```text
PASS: Barrier 1 substrate validation (363237 nodes, 641183 retained hyperedges)
10 passed in 32.16s
promise_check: exit 0
org_check: exit 0, warnings only
```

Cycle 9 Barrier 2 integration:

```text
PASS: Barrier 2 track enrichment conformance (6 tracks checked)
41 passed in 20.87s
PASS: Barrier 1 substrate validation (363237 nodes, 641183 retained hyperedges)
promise_check: exit 0
org_check: exit 0, warnings only
```

### Cross-Reference Map

| Origin | Consumer | Carried-forward value |
|---|---|---|
| Barrier 1 repaired substrate | All Wave 2 branches | Read-only accepted-key and canonical-member namespace |
| Track 1 reticulation enrichment | Barrier 2 integration | `ready_data_limited`; 25 pending-crosswalk rows |
| Track 2 ghost-partner enrichment | Barrier 2 integration | Seed evidence only; zero prediction rows |
| Track 3 convergence enrichment | Barrier 2 integration | 209,297 memberships; no `convergence_signature` |
| Track 4 domestication enrichment | Barrier 2 integration | 6 observed edges; climate and CWR shortfalls |
| Track 5 chemodiversity enrichment | Barrier 2 integration | Dr. Duke dominance and source-density diagnostics |
| Track 6 offline probe | Barrier 2 integration | 210 offline questions; no live provider responses |
| `prediction_ledger.tsv` | Barrier 2 validator | Confirmed empty during enrichment integration |

### Remaining Gaps

Track 1 requires accepted-key recovery or a raw-name-aware instrument strategy before canonical polyploid validation can be used. Track 4 requires CWR expansion and observed bioclim extraction before climate substitution predictions. Track 5 requires non-Duke counterfactual coverage before chemodiversity prediction can be separated from screening intensity. Track 6 requires a future free/open/local execution path before model scoring exists. Track 3 requires Barrier 2 agreement on how to treat the large `_other` bucket.
