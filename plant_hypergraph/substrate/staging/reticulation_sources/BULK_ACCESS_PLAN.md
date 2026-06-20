---
created: 2026-05-17T18:12:00Z
cycle: 2
run_id: run-phytograph-cycle2-fanout-e34b5b2c1c6c-clone1
agent: worker
milestone: M1.3
---

# M1.3 Bulk Access Plan

## Purpose

The seed M1.3 ingest is validated but far below production scale: 12 chromosome-count assertions and 10 event/support rows versus floors of 30,000 count assertions and 2,000 hybridization/polyploidization/reticulate event-support rows. This plan separates the remaining source-acquisition blocker from transformation logic. The bulk intake script now accepts approved local files and writes schema-compatible staging tables without changing frozen schema v1.0.

## Source Acquisition Matrix

| Source route | Exact file needed | Acquisition route | Redistribution constraints | Expected floor contribution | Current blocker | Priority |
|---|---|---|---|---:|---|---|
| CCDB maintainer/export | CSV/TSV/XLSX with raw scientific name, verbatim chromosome count, and source record/citation ID per assertion | Request maintainer dump or documented export from CCDB operators; alternatively conductor-provided manual export with permission | License not confirmed from probed pages; conductor must record permitted internal use and attribution | Up to the full 30,000 count floor if assertion-level export is available | Access/license; parsing path is ready | P0 |
| Plant DNA C-values export | CSV/TSV/XLSX with raw scientific name, ploidy or genome-size context, and source record/citation ID | Documented Kew export/manual download supplied by conductor | Kew attribution and license terms must be preserved; genome size cannot be promoted to event fact | Supporting ploidy context only; may improve Track 1 confidence but does not close event floor alone | Access/license/evidence scope | P1 |
| Wood-style supplements | Structured supplement table from Wood et al.-style or successor polyploid speciation literature with child, event type, parents where available, and citation ID | Conductor-provided supplement files with redistribution or transformation permission | Article/supplement copyright may restrict redistribution; stage derived factual assertions only when allowed | Could contribute hundreds of event/support rows, unlikely to close 2,000 alone | Access/license/structure | P1 |
| Independent curated event table | CSV/TSV/XLSX/JSON with child, event type, two or more parent roles where asserted, and source record/citation ID | Build or obtain a redistributable allopolyploid/hybrid event table from systematic-botany literature | Must carry citation-level provenance and license for each row; no inferred parent roles may be invented | Most likely route to close the 2,000 event/support floor | Source availability and curation effort | P0 |

## Conductor Request List

1. Approved CCDB export or maintainer dump with assertion-level record IDs and citation metadata.
2. Documented Plant DNA C-values export or manual file with license approval and citation metadata.
3. Redistributable curated allopolyploid/hybrid event table with child, event type, parent roles, and source record IDs.
4. Any manual-export workflow notes that establish license, attribution, version/release, and acquisition route.

## Bulk Intake Commands

Preview mode, which preserves seed staging tables:

```bash
python3 scripts/reticulation_bulk_intake.py \
  --source ccdb \
  --input approved_ccdb_export.csv \
  --source-version "maintainer dump YYYY-MM-DD" \
  --access-date 2026-05-17 \
  --license "..." \
  --attribution "..." \
  --acquisition-route "..." 
```

Promotion mode, to be used only after validation:

```bash
python3 scripts/reticulation_bulk_intake.py \
  --source curated_events \
  --input approved_events.tsv \
  --promote \
  --demote-one-parent \
  --source-version "curation release ..." \
  --access-date 2026-05-17 \
  --license "..." \
  --attribution "..." \
  --acquisition-route "..."
```

## Barrier 1 Recommendation

Barrier 1 should consume the validated seed rows as access-limited evidence and carry M1.3 forward with a late-arrival side-wave slot for production reticulation evidence. It should not treat the seed rows as production coverage. The remaining blocker is approved bulk source acquisition, not schema representation or normalization code.

## Figure

![Which source-acquisition routes can close the M1.3 chromosome-count and reticulation-event floors, separated by access, license, and parse risk.](plots/m1_3_scale_gap_closure_matrix.png)
