# QUARANTINE — schema-noncompliant records

This directory holds any record that could not be staged under
phytograph_schema.md v1.0 without inventing a new type.

## Current state: EMPTY (zero quarantined records)

Every staged row in `pbdb/`, `lqe/`, `faurby_svenning/`, `iucn/`, and
`anachronism_canon/` validates against schema v1.0 node and edge
inventories. No `_plan/schema-revision-v1.1` flag is raised by this
clone.

If future re-ingestion (e.g. PBDB API direct fetch at Barrier 1)
surfaces records that fail schema, this clone's downstream successor
should:

1. Stage the record's raw data here, named
   `<source>_<reason>_<rowidx>.jsonl`.
2. Append the source citation and the specific schema gap.
3. Emit a coordinator-review note in the next cycle's merge report.

A non-empty QUARANTINE means the coordinator should consider whether
a schema-revision-v1.1 BARRIER 0 pass is required.
