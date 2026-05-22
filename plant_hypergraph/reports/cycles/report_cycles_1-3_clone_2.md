---
title: "PhytoGraph Track 2 / M1.4 — Paleobotany & Megafauna Substrate Ingestion (clone 2, cycles 1–3)"
date: "2026-05-17"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
[OUTPUT: report]

# PhytoGraph Track 2 / M1.4 — Paleobotany & Megafauna Substrate Ingestion (clone 2, cycles 1–3)

## Abstract

Clone 2 of fanout `e34b5b2c1c6c` was scoped to milestone **M1.4** of the PhytoGraph campaign: stage paleobotany and megafauna specialty sources for Track 2 (Ghost Hyperedges). The required artifact — `substrate/staging/paleobotany_sources/INGEST_AUDIT.md` — was produced in cycle 1, alongside per-source staging tables for PBDB, the Late Quaternary Extinctions database (LQE), Faurby & Svenning megafauna ranges, and IUCN extant-disperser scaffolding. Targets were met: 237 extinct-fauna nodes (target ≥200), 31 literature-cited anachronism candidate edges (zero inferred), 52 distribution edges with verbatim source confidence codes, schema-conformance tests 10/10 passing. Cycles 2 and 3 were structural null cycles: the brief, worker, and auditor all converged on a PIVOT-to-exit posture, holding the boundary against scope creep into adjacent clones' namespaces (Barrier 1, sibling staging, root deliverables) and awaiting harness-level termination. The merge report at the conductor handoff path is intact and unchanged since cycle 1.

## 1. Introduction

PhytoGraph is a typed hypergraph of plant biology used as a discovery instrument across six tracks. Track 2 (Ghost Hyperedges) tests the Janzen–Martin "neotropical anachronism" hypothesis at scale by looking for fruit syndromes whose modern disperser is missing. That test requires a substrate layer of extinct megafauna with date and range, modern dispersers with overlapping range, and paleoclimate context. Wave 1 of the campaign assigns this ingestion to milestone **M1.4** and fans it out to a dedicated clone — this clone.

The clone's directive was narrow and disciplined:

- Stage from four specialty sources (PBDB, LQE, Faurby & Svenning, IUCN).
- Produce `extinct_fauna` nodes, `paleoclimate_paleoecology_context` nodes, megafauna range polygons, and extant-disperser nodes.
- ≥200 extinct-fauna nodes with date + range.
- Carry **source-stated confidence** on every record; do not inflate interpretive paleobotany claims.
- Stage `anachronism_candidate_edges` **only** where the source explicitly asserts one; **do not infer** them this cycle.
- Write to per-source staging tables; do not modify the shared substrate (that is Barrier 1's job).

This report covers cycles 1 through 3 of the clone's life: one substantive cycle followed by two null cycles whose audits independently confirmed scope exhaustion.

## 2. Approach

### 2.1 Per-source staging layout

Each source got its own directory under `substrate/staging/paleobotany_sources/`, isolated to prevent cross-source contamination before Barrier 1:

```
paleobotany_sources/
  pbdb/                 PBDB extinct fauna + paleo context
  lqe/                  Late Quaternary Extinctions + source citations
  faurby_svenning/      Megafauna range nodes + distribution edges + range polygons
  iucn/                 Extant-disperser scaffold
  anachronism_canon/    31 literature-cited Janzen-Martin canon edges
  _lib/                 shared schema helpers
  tests/                schema-conformance test suite
  QUARANTINE/           reserved for non-conformant records (0 used)
  INGEST_AUDIT.md       required output artifact (321 lines)
  coverage_row.json     machine-readable coverage summary
```

Each per-source directory carries the build script that produced its `.jsonl` tables, so the ingest is reproducible row-for-row when live network access is restored.

### 2.2 Schema discipline

All staged records conform to PhytoGraph schema v1.0 (frozen at Barrier 0). Confidence is recorded verbatim from each source rather than re-coded into a unified scale, preserving interpretive provenance:

- **PBDB:** record-level taxonomic confidence + stratigraphic interval.
- **LQE:** extinction-date interval and certainty flag as published.
- **Faurby & Svenning:** `range_type_code` preserved verbatim (e.g. `present-natural` vs. `current`), which is the field downstream consumers need to distinguish reconstructed Late Pleistocene range from anthropogenically-shrunken modern range.
- **Anachronism canon:** every edge cites a published source asserting the anachronism claim (Janzen & Martin 1982 and successor literature); zero inferred edges.

### 2.3 Hold-out reservation

The 31 literature-cited anachronism edges in `anachronism_canon/` are explicitly reserved as the Track 2 held-out validation set for milestones M2.T2 and M3.T2. The merge report flags this so the downstream ghost-partner ranker declares no-leakage upfront — the canon must not be fed into the model and then "recovered."

## 3. Results

### 3.1 Cycle 1 — substantive ingestion

Cycle 1 produced the full M1.4 deliverable. The audit verified the following against the directive:

| Target | Required | Delivered |
|---|---|---|
| `extinct_fauna` nodes with date + range | ≥200 | **237** |
| Literature-cited anachronism edges | ≥0 (no inference) | **31** (zero inferred) |
| Megafauna distribution edges | — | **52** (verbatim `range_type_code`) |
| Schema-conformance tests | passing | **10/10** |
| Quarantined records | — | **0** |
| Raw IUCN polygons committed | — | **0** (scaffold only; live download deferred) |
| `INGEST_AUDIT.md` | required | present, 321 lines |
| `merge_report.md` at conductor path | required | present |

Live network access for the IUCN polygon download and a live PBDB re-query was unavailable during the cycle; the build scripts capture the canonical query keys so a row-for-row re-ingest is possible at Barrier 1. This limitation is documented in `INGEST_AUDIT.md` and surfaced in the merge report.

The cycle-1 audit issued a VALIDATED verdict on M1.4. No CRITICAL or MODERATE findings were filed against the staging output.

### 3.2 Cycle 2 — first null cycle

The cycle-2 brief, recognizing that M1.4 was already validated and the clone's scope was exhausted, instructed zero further work. The worker complied: zero filesystem mutations. The auditor invoked the `<no-null-cycle-validation>` framework rule — a cycle producing only restatement-of-prior-state cannot itself be VALIDATED — and issued a **PIVOT-to-exit** verdict. One MINOR finding was logged: the harness's low-output detector had not yet terminated the clone loop. This finding is harness-level, not agent-level; no agent action resolves it.

### 3.3 Cycle 3 — second null cycle

Cycle 3 was identical in posture to cycle 2: zero mutations, the same `<no-null-cycle-validation>` invocation, the same PIVOT-to-exit verdict. The auditor explicitly noted that the verdict had now converged across two consecutive null cycles, confirming the structural posture. The recurrence stabilizes the exit pattern: any subsequent firing should produce the same verdict, and any "new scope" pivot would force scope creep into namespaces this clone is forbidden to touch (sibling Wave 1 staging, Barrier 1 reconciliation, root deliverables, Wave 2 enrichment).

### 3.4 Boundary discipline

Across all three cycles, the clone refrained from:

- modifying the frozen schema (Barrier 0 invariant);
- writing into sibling clones' staging namespaces;
- performing the Barrier 1 reconciliation work (LQE × PBDB taxon dedup, plant-binomial crosswalk against the M1.1 backbone) — this is reserved for the Barrier 1 coordinator;
- inferring anachronism edges beyond what the cited literature asserts.

## 4. Discussion

### 4.1 What is new

The new artifacts contributed by this clone:

1. **A reproducible paleobotany-and-megafauna staging layer** for PhytoGraph Track 2, structured for clean merge into the shared substrate at Barrier 1.
2. **A Janzen–Martin canon of 31 literature-cited anachronism edges** explicitly reserved as a held-out validation set — a precondition for an honest Track 2 evaluation.
3. **A verbatim-confidence convention** that preserves source-stated uncertainty (PBDB intervals, LQE flags, Faurby & Svenning `range_type_code`) rather than collapsing it to a single internal scale. This is necessary because Track 2's central question depends on the difference between reconstructed Late Pleistocene range and anthropogenically-shrunken modern range, and that distinction lives entirely in source-provided fields.

### 4.2 What is integrated

PBDB, LQE, Faurby & Svenning, and IUCN are all pre-existing datasets. The staging tables integrate them under one schema; they do not produce new biological claims.

### 4.3 What is deferred to Barrier 1

- LQE × PBDB taxon-name deduplication.
- Plant-binomial stub crosswalk against the M1.1 taxonomy backbone (clone 1's product).
- Live re-ingest of IUCN polygons (network was unavailable; canonical keys preserved).
- Any modification to the shared substrate.

### 4.4 What is deferred to Wave 2 / Track 2 enrichment (M2.T2)

- Inferred `anachronism_candidate_edges` (this clone staged only literature-asserted edges; M2.T2 is where the inference instrument runs).
- Held-out validation against the 31-edge canon.

### 4.5 The null-cycle posture

Two consecutive null cycles, each producing the same PIVOT-to-exit verdict, demonstrate convergence on the framework-prescribed terminal posture. The clone is not idle by accident; it is idle because its scope is exhausted and the directive forbids scope creep. The remaining termination mechanism is the harness low-output detector. This is a documented, expected, framework-conformant state.

## 5. Open Questions and Handoff Notes

For the Barrier 1 coordinator:

- The clone's staging tables are dedup-ready against canonical keys (taxon-ID + edge-type + supporting-source-set per the directive's deduplication discipline). Verify before merging into the shared substrate.
- Re-run the IUCN polygon download under the preserved query keys when live network is available.
- Cross-reference LQE and PBDB extinct-fauna nodes; expect overlap on canonical Pleistocene megafauna.

For the M2.T2 (Ghost-Partner Ranker) clone:

- The 31 canon edges in `anachronism_canon/anachronism_candidate_edges.jsonl` are held-out. Declare no-leakage upfront. The model must not see these labels during training; its job is to rediscover them.

For the campaign auditor:

- The cycle-1 manager intervention's `_manager/ledger-integrity` action_required, legacy plant-taxonomy ledger errors, and root-file `org_check` warnings on cycle-1 deliverables are carry-over items not owned by this clone. They are documented here to prevent re-attribution.

## Appendix: Implementation Details

### A.1 File inventory (workspace-relative)

```
substrate/staging/paleobotany_sources/
  INGEST_AUDIT.md                                       (required artifact, 321 lines)
  coverage_row.json
  _lib/                                                 shared schema helpers
  tests/                                                10 schema-conformance tests, all passing
  QUARANTINE/                                           empty (0 non-conformant records)
  pbdb/
    build_pbdb.py
    extinct_fauna.jsonl
    paleo_context.jsonl
    raw/
  lqe/
    build_lqe.py
    extinct_fauna.jsonl
    paleo_context.jsonl
    source_citations.jsonl
  faurby_svenning/
    build_faurby_svenning.py
    taxon_nodes.jsonl
    region_nodes.jsonl
    distribution_edges.jsonl
    ranges/
  iucn/                                                 scaffold (live polygon download deferred)
  anachronism_canon/
    build_anachronism_canon.py
    anachronism_candidate_edges.jsonl                   31 literature-cited edges, 0 inferred
    taxon_stubs.jsonl
    fruit_type_stubs.jsonl
    SOURCE_PAIRS.md
```

### A.2 Test results

10/10 schema-conformance tests passing as of cycle 1. State unchanged through cycles 2 and 3 (zero mutations).

### A.3 Cycle session references

| Cycle | Role | Session ID |
|---|---|---|
| 1 | researcher | 09c22174-7c20-4dc7-80bf-b6f6e6ef233e |
| 1 | worker | f4a5f3f0-092a-4b7e-9e67-92f5350ab9ca |
| 1 | auditor | 821fb9c2-2c54-412b-ad56-01a752ab8fda |
| 2 | researcher | 1044311e-61cb-4602-85e7-bdf832c53982 |
| 2 | worker | ecda6cac-44b0-4cfc-88d1-8da4bf8ddf7b |
| 2 | auditor | a2400a23-fdab-4b44-8436-3ec5dce402e0 |
| 3 | researcher | 4b268fd6-1b80-466e-88aa-e27eff9d6e84 |
| 3 | worker | ff414638-f1cf-4e16-a9a8-4cb65b6917a8 |
| 3 | auditor | 52cd95b0-bdd6-41df-b7ec-48e63100da1e |

### A.4 Cross-reference map

- Required output artifact: `substrate/staging/paleobotany_sources/INGEST_AUDIT.md` — present.
- Conductor handoff: `<run-root>/.long-exposure/fork-e34b5b2c1c6c/clone-2/merge_report.md` — present, unchanged since cycle 1.
- Held-out validation set for downstream M2.T2 / M3.T2: `anachronism_canon/anachronism_candidate_edges.jsonl` (31 rows).
- Wave 1 M1.4 milestone: VALIDATED at cycle 1; status unchanged through cycles 2 and 3.

### A.5 Verdict rationale

M1.4's required deliverables were produced and validated in cycle 1. Cycles 2 and 3 correctly held the boundary against scope creep and converged on the framework-prescribed PIVOT-to-exit posture. The clone's scoped objective is complete. The merge verdict reflects completion of the assigned milestone, not the null-cycle posture of the trailing cycles — those are evidence of disciplined exit, not of incomplete work.

<verdict>validated</verdict>
[END OUTPUT: report]
