---
created: 2026-05-17T19:05:00Z
cycle: 2
run_id: run-phytograph-cycle2-fanout-e34b5b2c1c6c-clone1
agent: worker
milestone: M1.3
---

# M1.3 Barrier 1 Handoff

## Barrier 1 Classification

M1.3 should be classified at Barrier 1 as `validated/access-limited`. The seed staging artifacts are schema-conformant and validated, and the late-arrival bulk-intake path is fixture-tested for approved local files, but the production floors remain blocked by missing approved source exports.

M1.3 is not production-scale complete. Current normalized seed counts are:

| Table | Rows excluding header | Barrier 1 meaning |
|---|---:|---|
| `normalized/chromosome_count_assertions.tsv` | 12 | Validated seed count assertions only; far below the 30,000 floor. |
| `normalized/ploidy_state_assertions.tsv` | 6 | Caveated supporting context only. |
| `normalized/hybridization_events.tsv` | 1 | Validated seed event row only. |
| `normalized/polyploidization_events.tsv` | 4 | Validated seed event rows only. |
| `normalized/reticulate_inheritance_evidence.tsv` | 5 | Validated seed support rows only. |

The event/support total is 10 rows against the 2,000 hybridization/polyploidization/support floor. Barrier 1 can merge these rows as access-limited evidence and reserve a late-arrival side-wave for approved bulk files.

## Evidence Boundary

Chromosome-count rows support `chromosome_count_assertion` only. They must not create `hybridization_event` or `polyploidization_event` edges at Barrier 1.

Plant DNA C-values and ploidy context are supporting evidence only and are staged as caveated `reticulate_inheritance_evidence` under schema v1.0. Curated event rows require at least two parent roles unless the row is explicitly demoted to caveated supporting evidence during intake.

## Validation Status

The completed validation pack covers:

| Check | Status |
|---|---|
| Seed staging provenance, allowed edge types, parent-role rules, and count-only negative control | Passed by stdlib-equivalent validation; `pytest` was unavailable in the earlier audited environment. |
| Bulk-intake fixture tests for CCDB-like counts, Plant DNA C-values context, curated events, missing provenance rejection, and one-parent event rejection/demotion | Passed with `python3 -m unittest -q tests.test_reticulation_bulk_intake`. |
| Bulk-intake and plot script compilation | Passed. |
| Scale-gap matrix figure generation and nonblank check | Passed. |

In the current Barrier 1 handoff environment, `pytest` is available but `openpyxl` is not. `normalized/format_readiness.tsv` records the supported-format policy.

## Conductor Checklist

1. Merge the clone-local M1.3 ledger event `8e463c62-021f-49e4-a1cc-899cf05d39ad` or append an equivalent main-workspace ledger event that names this handoff pack.
2. Request an approved CCDB export or maintainer dump with assertion-level record IDs, raw scientific names, verbatim count text, citation metadata, license, attribution, source version, and acquisition route.
3. Request a documented Plant DNA C-values export or approved manual export with row-level source IDs, license, attribution, source version, and acquisition route.
4. Request a redistributable curated hybrid/polyploid event table with child taxon, event type, at least two parent roles where asserted, source record IDs, citation metadata, license, attribution, source version, and acquisition route.
5. Decide XLSX policy before bulk intake: either install and verify `openpyxl`, or require CSV/TSV conversion before ingestion. Current policy is CSV/TSV conversion required for XLSX because `openpyxl` is absent.
6. Preserve the existing seed tables until a preview import is validated; only then run `scripts/reticulation_bulk_intake.py --promote`.

## Main Artifacts For Barrier 1

| Artifact | Barrier 1 use |
|---|---|
| `INGEST_AUDIT.md` | Source-access audit, bias profile, seed row counts, evidence boundaries, and validation summary. |
| `BULK_ACCESS_PLAN.md` | Specific acquisition requests and late-arrival import workflow. |
| `normalized/bulk_intake_contract.tsv` | Machine-readable required columns, provenance fields, and reject/demotion rules. |
| `normalized/format_readiness.tsv` | Runtime-honest input-format policy, including the current XLSX dependency gap. |
| `BARRIER1_HANDOFF.md` | Merge decision summary for conductor use without clone-private context. |
