---
title: "PhytoGraph M1.3 Reticulation Source Ingestion — cycles 1-3"
date: "2026-05-17"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# PhytoGraph M1.3 Reticulation Source Ingestion — cycles 1-3

## Abstract

Clone 1 of fanout fork `e34b5b2c1c6c` was assigned **M1.3**, the Wave 1 ingestion task for PhytoGraph's reticulation specialty sources. The objective was to stage chromosome-count evidence, ploidy-context assertions, hybridization events, and polyploidization events from CCDB, Plant DNA C-values, and curated systematic-botany literature for Track 1, the Reticulation Atlas.

The clone produced the required artifact, `substrate/staging/reticulation_sources/INGEST_AUDIT.md`, plus normalized staging tables, raw source-probe checksums, diagnostic figures, a local-file bulk-intake harness, tests, and a conductor-facing Barrier 1 handoff. The final audited state is **`validated/access-limited`**: the schema, provenance, evidence boundaries, and late-arrival import path are validated, but production-scale row-count floors were not reached because approved bulk source exports were not available.

The staged seed data contain 12 chromosome-count assertions, 6 ploidy-context rows, 1 hybridization event, 4 polyploidization events, and 5 reticulate-inheritance evidence rows. These are far below the M1.3 floors of at least 30,000 chromosome-count assertions and at least 2,000 event/support rows. The audit explicitly validated this as an access/source-acquisition limitation, not as a transformation or schema failure.

## Introduction

PhytoGraph is a typed hypergraph for plant biology. A hypergraph is a graph-like structure where one edge can connect more than two nodes. That matters for reticulation because hybridization and polyploidization can involve multiple parent lineages, while a conventional taxonomic tree usually permits only one parent.

M1.3 supports Track 1, the Reticulation Atlas. Track 1's later goal is to compute a `tree_compatibility_index`, identify clades where a single-parent tree loses biological information, and recover canonical hybrid or polyploid lineages without being told their labels in advance. This clone did not build that predictive instrument. Its narrower Wave 1 task was to stage the raw reticulation evidence that later Track 1 components can read after Barrier 1.

The clone was instructed to use raw scientific names as canonical node identifiers, such as `raw_name:Triticum_aestivum`. It was not allowed to invent WFO, GBIF, or other taxonomy-backbone identifiers locally. Cross-referencing to the taxonomy backbone is reserved for Barrier 1.

The source sessions provided for this report are:

| Cycle | Role | Session ID |
|---|---|---|
| 1 | researcher | `2cdb62b9-3020-4feb-8e02-7d36015600c9` |
| 1 | worker | `7c4cc3ad-46ad-4722-800b-d140daedb59d` |
| 1 | auditor | `5b359182-a617-432e-a1ac-487ddfe9aa13` |
| 2 | researcher | `e6947641-eea3-4b0e-8d0e-519afc7da6b5` |
| 2 | worker | `1bcda3e9-72d7-434f-9e8d-c365719986ec` |
| 2 | auditor | `14d7b278-7fda-460d-b1a1-19629c007ab9` |
| 3 | researcher | `649f6033-4871-4642-b4ed-468c2c598767` |
| 3 | worker | `c135124f-0a11-4708-b9c0-eb9c05975a15` |
| 3 | auditor | `b6fb4b91-6e8d-4bdf-9e2f-e03808620c62` |

Full session bodies were not available through session-search tools in this reporting environment. The chronology below is assembled from the provided session IDs, the supplied audit report, clone-local logs, promise-ledger events, `merge_report.md`, and the workspace artifacts.

## Approach

The worker staged evidence under `substrate/staging/reticulation_sources/`, keeping it separate from the shared substrate until Barrier 1. Three source classes were probed or represented:

| Source | Role in M1.3 | Access result |
|---|---|---|
| CCDB, the Chromosome Counts Database | Primary chromosome-count source for plant cytogenetic assertions | Landing page reachable; no unauthenticated bulk endpoint found in the low-impact probes. |
| Plant DNA C-values Database | Genome-size and ploidy-context support | Search application reachable; no all-row export endpoint found from probed public pages. |
| Wood et al. 2009 polyploid speciation synthesis | Curated canonical reticulation examples and positive seeds | DOI machine-retrieval path returned HTTP 403; only conservative public seed rows were staged. |

The staging policy was conservative. A chromosome count supports only a `chromosome_count_assertion`; it does not create a `hybridization_event` or `polyploidization_event`. Ploidy context is staged as caveated `reticulate_inheritance_evidence`, because schema v1.0 does not define a separate `ploidy_state_assertion` edge type. Curated event rows require at least two parent roles unless explicitly demoted to caveated evidence.

Three diagnostic figures were produced and preserved inline in the audit:

![Reticulation-source staged row counts by evidence class compared with M1.3 minimum viable floors.](substrate/staging/reticulation_sources/plots/source_row_counts_vs_targets.png)

![Top families or genera by chromosome-count assertion density, used to detect source-density bias before Track 1 modeling.](substrate/staging/reticulation_sources/plots/top_families_count_bias.png)

![Which source-acquisition routes can close the M1.3 chromosome-count and reticulation-event floors, separated by access, license, and parse risk.](substrate/staging/reticulation_sources/plots/m1_3_scale_gap_closure_matrix.png)

## Cycle Chronology

### Cycle 1: Seed Staging And Source Audit

Cycle 1 produced the initial M1.3 staging package. The worker created `scripts/ingest_reticulation_sources.py`, which probed the source pages, saved raw responses with checksums, wrote source metadata, and emitted conservative seed rows.

The required audit artifact, `INGEST_AUDIT.md`, documented the access posture, artifacts, row counts, evidence boundaries, bias profile, blockers, and validation checks. It recorded that CCDB and Plant DNA C-values were reachable as web applications, but no documented public bulk export or API endpoint was found. It also recorded that the Wood et al. DOI endpoint returned HTTP 403 for machine retrieval in this run.

The seed rows included canonical positives for Track 1 validation scaffolding: `Triticum aestivum`, `Brassica napus`, `Spartina anglica`, `Tragopogon mirus`, and `Tragopogon miscellus`. `Arabidopsis thaliana` was staged as a negative control: it has a count/ploidy-context row, but no hybridization or polyploidization event row.

### Cycle 2: Bulk-Intake Readiness

Cycle 2 did not inflate the biological tables. Instead, it separated the production-scale blocker from the transformation logic.

The worker added `scripts/reticulation_bulk_intake.py`, a local-file-only import harness for approved late-arrival files. It accepts `--source ccdb`, `--source plant_dna_cvalues`, or `--source curated_events`; requires source version, access date, license, attribution, and acquisition route; writes to a preview directory by default; and requires `--promote` before overwriting normalized staging tables.

The worker also added `BULK_ACCESS_PLAN.md`, which tells the conductor what files are needed to close the scale gap:

- an approved CCDB export or maintainer dump with assertion-level record IDs;
- a documented Plant DNA C-values export with row-level source IDs and license information;
- a redistributable curated allopolyploid/hybrid event table with child taxon, event type, parent roles, source record IDs, citation metadata, license, attribution, source version, and acquisition route.

The machine-readable contract for those files is `normalized/bulk_intake_contract.tsv`.

### Cycle 3: Barrier 1 Handoff Hardening

Cycle 3 made the handoff conductor-readable without relying on clone-private context. The worker added `BARRIER1_HANDOFF.md`, `normalized/format_readiness.tsv`, `tests/test_reticulation_format_readiness.py`, and `scripts/check_reticulation_handoff.py`.

The Barrier 1 recommendation is explicit: classify M1.3 as `validated/access-limited`, merge the seed rows only as access-limited evidence, and do not treat the branch as satisfying production-scale coverage. The handoff repeats the main evidence boundary: chromosome counts do not imply reticulation event edges.

`format_readiness.tsv` closes a dependency ambiguity. CSV, TSV, and JSON intake are available through standard Python parsing. XLSX is conditional because `openpyxl` is absent in the current handoff environment; Barrier 1 should require CSV/TSV conversion unless `openpyxl` is installed and verified.

## Findings

### Staged Evidence Counts

The final normalized row counts are:

| Table | Rows | Meaning |
|---|---:|---|
| `chromosome_count_assertions.tsv` | 12 | Seed chromosome-count assertions only. |
| `ploidy_state_assertions.tsv` | 6 | Caveated supporting ploidy context only. |
| `hybridization_events.tsv` | 1 | Seed hybridization event. |
| `polyploidization_events.tsv` | 4 | Seed polyploidization events. |
| `reticulate_inheritance_evidence.tsv` | 5 | Seed multi-parent reticulate-inheritance evidence rows. |

The event/support total is 10 rows against the 2,000-row M1.3 floor. The chromosome-count table has 12 rows against the 30,000-row M1.3 floor.

### Evidence Boundary

The most important decision is that count evidence remains count evidence. A single chromosome-count assertion is not treated as proof of a hybridization or polyploidization event.

This boundary appears in the normalized rows, tests, audit, and handoff. It protects later Track 1 models from learning artificial event labels created by the ingestion process itself.

### Bias Profile

The seed-scale staging already shows the expected source-density bias: Poaceae, Brassicaceae, crop lineages, and model systems dominate the positives. The audit states that this must not be interpreted as true biological reticulation density.

Known over-sampled strata are temperate Northern Hemisphere flora, crop lineages, textbook model systems, and recently studied allopolyploids. Known under-sampled strata are tropical understory angiosperms, non-crop woody lineages, regions with lower cytogenetic publication density, and taxa with unstable synonymy.

### Barrier 1 Status

The supplied audit report validates the handoff with no critical findings. Its decision is **VALIDATED**. The one moderate issue is campaign bookkeeping: `python3 -m long_exposure.tools.promise_check .` exits 1 because legacy pre-PhytoGraph milestone IDs remain in the main ledger and the new M1.3 artifacts are clone-local rather than represented in the main ledger. The audit states that this affects formal Barrier 1 bookkeeping, not the correctness of the M1.3 handoff files.

The audit's recommended next conductor action is ledger reconciliation: merge or mirror the clone-local validated M1.3 event into the main ledger, then carry M1.3 through Barrier 1 as `validated/access-limited`.

## Validation Summary

The final audited validation commands were:

```bash
python3 -m pytest -q tests/test_reticulation_staging.py tests/test_reticulation_bulk_intake.py tests/test_reticulation_format_readiness.py
```

Result: `13 passed in 0.11s`.

```bash
python3 -m py_compile scripts/reticulation_bulk_intake.py scripts/plot_m1_3_scale_gap_closure.py scripts/check_reticulation_handoff.py
```

Result: passed.

```bash
python3 scripts/check_reticulation_handoff.py
```

Result: `reticulation handoff readiness checks passed`.

The audit also confirmed that seed row counts were unchanged: 12 chromosome-count rows, 6 ploidy-context rows, 1 hybridization event, 4 polyploidization events, and 5 reticulate-inheritance evidence rows.

## Open Questions

The remaining work is source acquisition and ledger hygiene, not schema transformation.

Barrier 1 still needs an approved CCDB export or maintainer dump, a documented Plant DNA C-values export, and a redistributable curated hybrid/polyploid event table. Until those arrive, M1.3 should not be used as a production-scale reticulation substrate.

The main campaign ledger also needs to represent the clone-local validated M1.3 event so the conductor can make a formal Barrier 1 decision from the main workspace.

## References

[27] CCDB, "Chromosome Counts Database (CCDB)," Tel Aviv University, version 1.66.6, 2026. https://ccdb.tau.ac.il/ (accessed 2026-05-17).

[28] Anna Rice, Lior Glick, Shiran Abadi, et al., "The Chromosome Counts Database (CCDB) — a community resource of plant chromosome numbers," *New Phytologist*, 2015. https://doi.org/10.1111/nph.13191 (accessed 2026-05-17).

[29] Ilia J. Leitch, Emma Johnston, Jaume Pellicer, Oriane Hidalgo, and Michael D. Bennett, "Plant DNA C-values Database," Royal Botanic Gardens, Kew, 2026. https://cvalues.science.kew.org/ (accessed 2026-05-17).

[30] Troy E. Wood, Naoki Takebayashi, Michael S. Barker, et al., "The frequency of polyploid speciation in vascular plants," *Proceedings of the National Academy of Sciences*, 2009. https://doi.org/10.1073/pnas.0811575106 (accessed 2026-05-17).

## Appendix: Implementation Details

### Code Organization

| File | Lines | Purpose |
|---|---:|---|
| `scripts/ingest_reticulation_sources.py` | 415 | Source probing, raw checksum capture, conservative normalized staging, and plot generation. |
| `scripts/reticulation_bulk_intake.py` | 355 | Local-file-only intake harness for approved bulk files. |
| `scripts/plot_m1_3_scale_gap_closure.py` | 71 | Scale-gap closure matrix renderer. |
| `scripts/check_reticulation_handoff.py` | 66 | Stdlib Barrier 1 readiness checker. |
| `tests/test_reticulation_staging.py` | 77 | Seed staging schema and evidence-boundary tests. |
| `tests/test_reticulation_bulk_intake.py` | 182 | Bulk-intake fixture tests. |
| `tests/test_reticulation_format_readiness.py` | 45 | Format-readiness and handoff-language tests. |

### Staging Tables

| File | Rows excluding header |
|---|---:|
| `normalized/source_manifest.tsv` | 3 |
| `normalized/chromosome_count_assertions.tsv` | 12 |
| `normalized/ploidy_state_assertions.tsv` | 6 |
| `normalized/hybridization_events.tsv` | 1 |
| `normalized/polyploidization_events.tsv` | 4 |
| `normalized/reticulate_inheritance_evidence.tsv` | 5 |
| `normalized/bulk_intake_contract.tsv` | 3 |
| `normalized/format_readiness.tsv` | 4 |
| `normalized/row_counts.tsv` | 5 |

### Source Inventory

| Source ID | Date / cycle | What it contains | Timeline role |
|---|---|---|---|
| `INGEST_AUDIT.md` | 2026-05-17, cycle 2 metadata | Required M1.3 audit with source access, artifacts, staged counts, evidence rules, bias profile, blockers, and verification. | Primary narrative record of seed staging and access-limited status. |
| `BULK_ACCESS_PLAN.md` | 2026-05-17, cycle 2 | Acquisition matrix and import commands for approved bulk files. | Separates remaining blocker from transformation logic. |
| `BARRIER1_HANDOFF.md` | 2026-05-17, cycle 2 | Conductor-facing Barrier 1 classification and checklist. | Final merge decision artifact. |
| `.long-exposure/fork-e34b5b2c1c6c/clone-1/merge_report.md` | 2026-05-17, cycle 2 | Clone merge report with artifacts, validation, row counts, and merge notes. | Handoff summary for root conductor. |
| clone promise ledger event `c548839c-cb73-484d-8d01-d8ac557ad378` | 2026-05-17 | Initial seed staging event, status `in-progress`. | Records first staging pass and scale blocker. |
| clone promise ledger event `8e463c62-021f-49e4-a1cc-899cf05d39ad` | 2026-05-17 | Bulk-intake and acquisition-plan event, status `in-progress`. | Records late-arrival production path. |
| clone promise ledger event `01bc281e-7749-43ed-b698-5c7a5d3a37cc` | 2026-05-17 | Handoff hardening event, status `validated`. | Records final validated/access-limited state. |
| Supplied audit report | 2026-05-17 | Independent validation summary and decision. | Confirms `VALIDATED` with no critical findings. |

### Cross-Reference Map

| Origin | Consuming artifact | Flow |
|---|---|---|
| `scripts/ingest_reticulation_sources.py` | `normalized/*.tsv`, `INGEST_AUDIT.md` | Source probes and seed staging produce the required M1.3 package. |
| `normalized/source_manifest.tsv` | `INGEST_AUDIT.md`, `BARRIER1_HANDOFF.md` | Source access, checksum, license, reliability, version, and bias metadata support the access-limited classification. |
| `normalized/chromosome_count_assertions.tsv` | `tests/test_reticulation_staging.py`, `BARRIER1_HANDOFF.md` | Count-only evidence is preserved without creating event edges. |
| `scripts/reticulation_bulk_intake.py` | `tests/test_reticulation_bulk_intake.py`, `bulk_intake_contract.tsv`, `BULK_ACCESS_PLAN.md` | Approved late-arrival files can be previewed and promoted under schema v1.0. |
| `format_readiness.tsv` | `tests/test_reticulation_format_readiness.py`, `scripts/check_reticulation_handoff.py` | Runtime dependency policy is validated, including the XLSX conversion requirement. |
| `BARRIER1_HANDOFF.md` | clone merge report, conductor Barrier 1 decision | M1.3 can be carried forward as `validated/access-limited`. |

### File Counts And Figures

The M1.3 code and test inventory contains 4 scripts, 3 test files, and 1,211 Python/test lines. The handoff/audit markdown set contains 3 files and 250 lines. The report-specific figure set contains 3 PNG files:

- `substrate/staging/reticulation_sources/plots/source_row_counts_vs_targets.png`
- `substrate/staging/reticulation_sources/plots/top_families_count_bias.png`
- `substrate/staging/reticulation_sources/plots/m1_3_scale_gap_closure_matrix.png`

### Manifest Update

`MANIFEST.md` was updated with a clone-1 M1.3 snapshot covering script inventory, data/documentation inventory, cumulative stats, and cross-references. The existing `## Key Files` section was preserved verbatim.
