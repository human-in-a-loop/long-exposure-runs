---
title: "PhytoGraph M1.5 Convergence Source Ingestion — cycles 1-3"
date: "2026-05-17"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# PhytoGraph M1.5 Convergence Source Ingestion — cycles 1-3

## Abstract

Cycles 1-3 of clone 3 completed and revalidated **M1.5**, the Wave 1 source-ingestion branch for Track 3, **Convergence Pressure**. The branch did not build the convergence-pressure statistic and did not infer independent evolutionary origins. Its purpose was narrower: stage source-stated plant trait, fruit morphology, and life-form assertions so later phases can compute convergence only after taxonomic normalization and phylogenetic context are available.

The validated output is `substrate/staging/convergence_sources/INGEST_AUDIT.md`, supported by staged node and edge tables under `substrate/staging/convergence_sources/data/`. The worker staged 420,545 structural edge assertions and 32,793 nodes from AusTraits 6.0.0 [31]. Thirteen trait lists were staged; twelve exceeded the target threshold of 500 rows. The branch emitted only `fruit_morphology`, `life_form`, and `trait_syndrome` edges. It emitted zero `convergence_signature` edges because no source in this branch met the explicit requirement to enumerate a convergent set across clades.

The audit decision across cycles was `VALIDATED`. Cycle 1 built and audited the staging layer. Cycles 2 and 3 did not add new biological ingestion; they preserved the Barrier 1 handoff contract. The central invariant is:

`S(source_id, raw_taxon_name, asserted_trait_or_morphology)` is a source assertion. It is not yet `I(trait | accepted_taxon, clade_context, phylogeny)`, the later independent-recurrence inference required for Track 3.

## Introduction

PhytoGraph is a typed hypergraph substrate for plant biology. In this campaign, a **hypergraph** means a data structure where one edge can connect more than two typed entities: for example, a taxon, a trait, a source, evidence metadata, and caveats can all participate in one assertion. Track 3, Convergence Pressure, asks whether repeated plant traits such as C4 photosynthesis, fleshy fruits, succulence, myrmecochory, elaiosomes, and samaras can be distinguished as convergent rather than inherited from one common ancestor.

Clone 3 was assigned M1.5, the Wave 1 ingestion task for Track 3. Wave 1 precedes Barrier 1, where source-local staging tables are joined against the shared taxonomic backbone. For that reason, this clone was required to preserve source names and provenance, not resolve accepted taxonomy. The researcher brief in cycle 1 stated the boundary directly: stage source-stated fruit morphology, life form, generic trait membership, and explicit source-enumerated convergent sets only; do not compute convergence pressure or infer independent origins. Source: cycle 1 researcher session `5d8ac272-6e36-48c2-a63c-1e9c8f1d5ea5`.

The required artifact was:

`substrate/staging/convergence_sources/INGEST_AUDIT.md`

That artifact was produced in cycle 1 and remained the authoritative M1.5 audit artifact through cycles 2 and 3.

## Approach

The ingestion design separated three operations that occur at different campaign phases.

First, M1.5 records source assertions. A source assertion is a row-level claim such as “this source states this raw taxon name has this trait value.” The staged assertion keeps the raw source taxon name, source identifiers, license, access date, evidence scope, caveats, confidence, and the clone ID.

Second, Barrier 1 may join those raw taxon names to accepted taxon IDs using the M1.1 taxonomic crosswalk. This join is a normalization step. It must preserve the raw names and diagnostics rather than replacing them silently.

Third, M2.T3 may later estimate convergence after accepted taxonomy and phylogenetic context exist. A trait membership row alone does not show independent recurrence. The branch therefore treated `convergence_signature` as allowed only where a source explicitly enumerated a convergent set. No such rows were staged.

The worker selected AusTraits 6.0.0 as the only staged source because it supplied redistributable row-level trait data at the required scale under CC-BY-4.0. Candidate C4, succulence, myrmecochory, elaiosome, and samara publication sources were recorded but not staged when they lacked row-level redistributable data, required registration or special retrieval, represented secondary summaries, or required inference beyond the source claim. Source: cycle 1 worker session `e817d78e-2216-4a6e-8be3-0e57a01b3044`; `INGEST_AUDIT.md`; `data/rejected_records.tsv`.

## Findings

### Staged Outputs

The branch staged 420,545 structural edge assertions and 32,793 nodes. The edge types were:

| Edge type | Meaning in this branch |
|---|---|
| `fruit_morphology` | Source-stated fruit or diaspore morphology, such as fruit type, dehiscence, or fleshiness. |
| `life_form` | Source-stated growth form, woodiness, or succulence-related life-form fields. |
| `trait_syndrome` | Source-stated generic trait membership, such as life history, dispersal syndrome, dispersers, seed shape, appendage, or photosynthetic pathway. |

No `convergence_signature` rows were emitted. This was intentional and validated. The source material staged in this branch did not explicitly enumerate convergent sets across clades in a way that met the campaign’s evidence rule.

The staged trait lists were:

| Trait list | Staged assertion rows | Scale status |
|---|---:|---|
| `plant_growth_form` | 123,510 | meets >=500 |
| `life_history` | 89,164 | meets >=500 |
| `fruit_type` | 57,356 | meets >=500 |
| `fruit_dehiscence` | 42,367 | meets >=500 |
| `fruit_fleshiness` | 32,578 | meets >=500 |
| `dispersal_syndrome` | 19,206 | meets >=500 |
| `dispersers` | 16,283 | meets >=500 |
| `photosynthetic_pathway` | 15,003 | meets >=500 |
| `seed_shape` | 13,341 | meets >=500 |
| `diaspore_fleshiness` | 4,126 | meets >=500 |
| `woodiness` | 4,102 | meets >=500 |
| `dispersal_appendage` | 3,425 | meets >=500 |
| `plant_succulence` | 84 | data-limited |

The target was at least five trait lists with at least 500 taxa or rows each. The staged output exceeded that threshold with twelve lists above 500 rows. Source: `data/ingest_summary.json`; `INGEST_AUDIT.md`; cycle 1 auditor session `db9e36a0-5e87-44ec-b1d8-16cf0cbd6d65`.

### Source Registry

The source registry contains two entries. AusTraits 6.0.0 was staged and is redistributable with attribution. The second entry covers specialty publication candidates for C4, succulence, myrmecochory, elaiosome, and samara sources; those candidates were not staged in this branch because their scale, license, retrieval, or row-provenance status remained unresolved.

This means the branch met the structural ingestion target, but its coverage is dominated by Australian flora through AusTraits. The audit reports that limitation as a bias, not as a staging defect.

### Rejected and Quarantined Candidates

The worker recorded 23 rejected or quarantined records. These included:

- Secondary web summaries, such as Wikipedia or Britannica examples.
- Publication review candidates without redistributable row-level species tables staged in this branch.
- Family-level or genus-level expansions, such as treating all Cactaceae as succulent or all maples as samara-bearing.
- Forbidden scope expansions, such as inferring animal dispersal from fleshy fruit or convergence from C4 membership.
- Registration or license blockers, such as TRY full database access.
- Missing provenance cases, such as manual extraction from unnamed PDF tables.
- Image-derived trait calls, rejected because media evidence cannot establish biology for M1.5.

These rejected records are important because they show how the branch enforced the root directive’s caveat: stage what the source says, not what the source implies.

## Validation

Cycle 1 worker validation ran:

```bash
python3 substrate/staging/convergence_sources/scripts/ingest_convergence_sources.py
python3 -m pytest substrate/staging/convergence_sources/tests/test_convergence_sources_schema.py
python3 -m long_exposure.tools.promise_check <run-root>
```

The scoped schema tests passed. Cycle 1 reported `7 passed in 84.71s`; the cycle 1 auditor independently reported `7 passed in 61.83s`. Cycle 2 repeated the handoff checks and reported `7 passed in 70.45s`; the cycle 2 auditor reported `7 passed in 58.90s`. Cycle 3 carried forward the prior verified state, and the final supplied audit reported scoped tests passing again, `7 passed in 45.52s`.

The tests checked that required files exist, edge types remain within the frozen schema, provenance fields are complete, at least five lists clear the scale threshold, evidence scope is not overclaimed, taxonomy remains unresolved with `pending_crosswalk=true`, and rejected records cover the expected negative cases.

The supplied audit report for cycles 1-3 found no critical or moderate M1.5 defects. It confirmed:

- 420,545 edge rows.
- 32,793 node rows.
- 13 trait lists.
- 12 trait lists with at least 500 rows.
- Edge types limited to `fruit_morphology`, `life_form`, and `trait_syndrome`.
- 0 `convergence_signature` rows.
- 23 rejected rows.
- 0 rows missing required provenance.
- 0 rows with `pending_crosswalk != true`.
- 0 rows with `direct_source_claim != true`.

The nonblocking issues were workspace-level process warnings: legacy pre-PhytoGraph milestone IDs in `promise_check`, missing historical report artifacts, orphan artifacts from sibling or prior work, and known root-layout warnings from `org_check`. These were classified as coordinator-level cleanup, not M1.5 defects. Cycle 1 also noted duplicate reference numbering in `REFERENCES.md`; that remains a synthesis-cleanup item, not a blocker for the staged data.

## Discussion

The main result of cycles 1-3 is a validated Track 3 structural staging layer. It is not a convergence model and it does not make biological predictions. Its durable contribution is that later phases can consume broad trait and morphology assertions with provenance, source limitations, and evidence-scope boundaries intact.

The branch made three key decisions.

First, AusTraits was used as the staged scale source. This met the row-count requirement and provided redistributable trait data, but it introduced a clear Australian-flora bias. The branch documented that bias instead of presenting the staged layer as global convergence coverage.

Second, candidate specialty sources were quarantined rather than forced into the staging layer. This prevented the branch from expanding genus-level or family-level statements into species-level claims and prevented secondary summaries from becoming substrate evidence.

Third, `convergence_signature` was left empty. This is not a missing deliverable. It is the correct state under the evidence rule, because trait membership, morphology, C4/CAM status, myrmecochory, elaiosome presence, and life-form rows are not independent-origin evidence by themselves.

The handoff contract for Barrier 1 is explicit. Barrier 1 may add accepted taxon IDs through the M1.1 crosswalk, but it must preserve raw `taxon_name`, `taxon_rank`, source identifiers, provenance, caveats, `pending_crosswalk`, and direct-source-claim diagnostics. Deduplication should happen only after accepted IDs exist, and even then supporting source sets and raw-name diagnostics must remain available.

## Open Questions

The branch leaves several gaps for later phases.

Non-AusTraits specialty lists remain candidates, not staged data. C4 lineage lists, global succulence lists, myrmecochory lists, elaiosome lists, and samara lists may still be valuable, but they require row-level supplements, license review, or careful source-specific ingestion.

Taxonomic normalization is still pending for M1.5 rows. All staged taxon names remain unresolved with `pending_crosswalk=true`, as required for a Wave 1 source clone. Barrier 1 owns accepted-name resolution and ambiguity handling.

Convergence inference remains entirely future work. M2.T3 must combine the staged source assertions with accepted taxonomy and phylogenetic or clade context before estimating independent recurrence.

Coordinator-level cleanup remains outside the branch. The legacy validator warnings and duplicate reference numbering should be addressed before synthesis, but they do not reopen M1.5.

## References

[31] Daniel Falster, Rachael Gallagher, Elizabeth Wenk, Herve Sauquet, et al., "AusTraits: a curated plant trait database for the Australian flora," Zenodo, version 6.0.0, 2024. https://doi.org/10.5281/zenodo.11188867 (accessed 2026-05-17).

## Appendix: Implementation Details

### Code Organization

The M1.5 staging directory is:

```text
substrate/staging/convergence_sources/
  INGEST_AUDIT.md
  data/
    ingest_summary.json
    rejected_records.tsv
    source_registry.tsv
    staged_edges.tsv
    staged_nodes.tsv
  raw/
    austraits-6.0.0.zip
    manifests/
      austraits_zenodo_11188867.json
  scripts/
    ingest_convergence_sources.py
  tests/
    test_convergence_sources_schema.py
```

The merge handoff is:

```text
.long-exposure/fork-e34b5b2c1c6c/clone-3/merge_report.md
```

### File Counts

| File | Lines or rows | Purpose |
|---|---:|---|
| `scripts/ingest_convergence_sources.py` | 510 lines | Builds the M1.5 staged outputs and audit from source-stated rows. |
| `tests/test_convergence_sources_schema.py` | 93 lines | Validates schema, provenance, evidence scope, unresolved taxonomy, and negative checks. |
| `INGEST_AUDIT.md` | 77 lines | Required narrative ingest audit. |
| `data/staged_edges.tsv` | 420,545 rows | Staged source assertions. |
| `data/staged_nodes.tsv` | 32,793 rows | Staged nodes. |
| `data/source_registry.tsv` | 2 rows | Source registry. |
| `data/rejected_records.tsv` | 23 rows | Rejected and quarantined candidates. |
| `data/ingest_summary.json` | 1 file | Machine-readable counts and summaries. |

### Test Results

Scoped test results reported across the cycles:

| Cycle | Source session | Result |
|---|---|---|
| Cycle 1 worker | `e817d78e-2216-4a6e-8be3-0e57a01b3044` | `7 passed in 84.71s` |
| Cycle 1 auditor | `db9e36a0-5e87-44ec-b1d8-16cf0cbd6d65` | `7 passed in 61.83s` |
| Cycle 2 worker | `c0a0bf7d-ab05-469c-a505-ccc59e8fca7a` | `7 passed in 70.45s` |
| Cycle 2 auditor | `1265f799-9ac9-4c64-9391-389ea45bec21` | `7 passed in 58.90s` |
| Cycle 3 auditor / supplied audit | `47857dd8-176e-4cf8-bbac-b9c8147e3f52` and input audit | `7 passed in 45.52s` |

### Session References

| Cycle | Role | Session ID | Contribution |
|---|---|---|---|
| 1 | Researcher | `5d8ac272-6e36-48c2-a63c-1e9c8f1d5ea5` | Scoped M1.5 and set the source-stated-claims-only boundary. |
| 1 | Worker | `e817d78e-2216-4a6e-8be3-0e57a01b3044` | Built the staging layer, audit, tests, raw manifest, and merge report. |
| 1 | Auditor | `db9e36a0-5e87-44ec-b1d8-16cf0cbd6d65` | Validated the staging layer and identified nonblocking workspace/reference cleanup. |
| 2 | Researcher | `3111990a-ae63-4163-860a-60b5d8061fd5` | Reframed the next work as Barrier 1 handoff, not new ingestion. |
| 2 | Worker | `c0a0bf7d-ab05-469c-a505-ccc59e8fca7a` | Verified handoff package and updated merge report status. |
| 2 | Auditor | `1265f799-9ac9-4c64-9391-389ea45bec21` | Revalidated handoff state and confirmed no M1.5-specific blocker. |
| 3 | Researcher | `9b247223-4a65-4bad-9dbc-e6e8c8d333fd` | Defined the M1.5-to-Barrier 1 integration contract after M1.1 validation. |
| 3 | Worker | `76d06caa-78ec-4d7a-a337-c8ed0056399a` | Confirmed no new ingestion was required and preserved validated handoff state. |
| 3 | Auditor | `47857dd8-176e-4cf8-bbac-b9c8147e3f52` | Final validation that M1.5 remains Barrier 1-ready. |

### Cross-Reference Map

| Origin | Consuming stage | Required preservation |
|---|---|---|
| `data/staged_edges.tsv` | Barrier 1 taxonomy join | Preserve raw source names, source IDs, provenance, caveats, `pending_crosswalk`, and direct-source-claim diagnostics. |
| M1.1 taxonomic crosswalk | Barrier 1 join | Add accepted IDs without deleting raw M1.5 fields. |
| Barrier 1 joined rows | M2.T3 convergence enrichment | Use accepted taxonomy and clade context before estimating independent recurrence. |
| `data/rejected_records.tsv` | Later source-ingestion planning | Revisit only with proper row-level supplements, license clearance, or explicit source evidence. |
| `INGEST_AUDIT.md` | Merge report and cycle synthesis | Authoritative statement of M1.5 scope, results, limitations, validation, and handoff contract. |

### Manifest Update

`MANIFEST.md` was updated for this report cycle with the M1.5 script inventory, data inventory, cumulative stats, and cross-reference map. The existing `## Key Files` section was preserved verbatim.
