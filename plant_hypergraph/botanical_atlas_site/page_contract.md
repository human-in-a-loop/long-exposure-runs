---
created: 2026-05-18T03:05:00+00:00
cycle: 9
run_id: run-phytograph-cycle9-wave3-atlas
agent: worker
milestone: M3.A
---

# Botanical Atlas — Page Contract (Wave 3 / M3.A)

The Atlas's scientific value rests on a single invariant: **every rendered
claim is labelled with its evidence class and its provenance, such that a
researcher can never confuse a Wave-3 prediction for a substrate
observation.** This page contract is the mechanical encoding of that
invariant. The builder (`build_atlas.py`) refuses to emit a row without a
`provenance_ref`; the front-end (`app.js`) refuses to render a row
without an evidence-class band.

## Evidence classes (bands)

| Class | Band | Source | Meaning |
|---|---|---|---|
| **OBSERVED** | blue | substrate edges from `taxonomy_backbone`, `wikidata_commons`, or `image_evidence`/`life_form`/`distribution` rows | direct ingestion of a source row |
| **ENRICHED** | yellow | substrate edges from Wave-2 source groups (`reticulation_sources`, `paleobotany_sources`, `convergence_sources`, `domestication_sources`, `chemodiversity_ethnobotany_sources`) or the Track-6 offline probe ground-truth | source-row projection onto the accepted-key namespace, often with `pending_crosswalk=true` caveats |
| **PREDICTED** | orange | rows whose `inferred_flag=true` or rows ingested from `tracks/track*/instruments/*` outputs | Wave-3 instrument output — model-generated claim awaiting validation |
| **DATA-LIMITED** | gray | per-track section with zero substrate edges AND no instrument output | the substrate has nothing to say for this taxon under this track |

A per-track section is in exactly one state. The state is derived
mechanically by `build_atlas.classify_edge` from `source_group`,
`edge_type`, `inferred_flag`, and the result of probing
`tracks/track*/instruments/`. The state cannot be overridden.

## Required page order

1. **Header.** Accepted name (WFO-anchored), rank, genus inferred from
   the accepted name, list of synonyms, list of external IDs as
   provenance badges (WFO / GBIF / OTT / POWO each link to the
   `provenance_registry.json`).
2. **Provenance strip.** Always rendered; if an external ID is missing the
   badge for that source is omitted (never silently stubbed).
3. **Per-track sections (six, fixed order).** Each header is
   `Track N — <name>` followed by the band tag. Inside, rows are
   grouped by evidence class. Each row prints `edge_type`, `source_group`,
   first 60 chars of `license`, `confidence`, and `pending_crosswalk`
   flag when set. If the section is `DATA-LIMITED`, the reason string is
   printed; if the corresponding Wave-3 instrument is missing, an
   explicit `Instrument M3.T*: pending` placeholder is rendered with
   the sibling clone's name. Instrument absence is NEVER hidden.
4. **Hypergraph neighborhood.** Compact JSON view of the taxon's local
   incident edges (substrate-derived). Cytoscape.js rendering is optional;
   the raw JSON is always present for export.
5. **Counter-claim button.** Opens an inline form that constructs a JSON
   payload `{accepted_taxon_key, target_edge_id, target_kind, reviewer_id,
   comment, iso_timestamp}`. The user copies the payload into
   `botanical_atlas_site/counter_claims.jsonl` directly or pipes it
   through `tools/file_counter_claim.py`, which appends and emits a
   `_run/counter-claim-<uuid>` ledger event.

## Falsifiability tests (the Atlas falsifies its own claim of being a research instrument if any of the following hold)

- (a) any taxon page renders a `PREDICTED` band without a `confidence`
  value AND a validation-source pointer;
- (b) any `OBSERVED` band cites a synthesized hyperedge (an edge with
  `inferred_flag=true` rendered under OBSERVED);
- (c) the counter-claim CLI accepts a payload without a `target_edge_id`;
- (d) `reports/atlas_barrier3_scaffold.md` hides per-track coverage gaps;
- (e) `instrument_pending` slots are rendered as empty divs rather than
  visible placeholders.

The test suite (`tests/test_atlas_build.py`) asserts (a), (b), (c), and (e).

## Performance design path to 100 k taxa

The current `search_index.json` is a flat array of `{k, n, s, f, u}`
records — ~80 bytes/row × 59 908 ≈ 4.8 MB. This is the smallest viable
client-side index. At 100 k taxa the projected size is ~8 MB, which is
still tractable for an initial fetch; if that becomes a problem the
fallback is **sqlite FTS5 + sql.js (WASM)**. The trade is up-front
~600 kB JS library cost for O(log n) query latency over the full corpus,
versus the current O(n) JS-string scan that is acceptable below 100 k
records. We pick the flat-array index now (no library dependency, no
build complexity) and document the FTS5 fallback for a 10× scale jump.

## Read-only contract

The Atlas reads from `phytograph_dataset/` and `tracks/track*/` and
writes only to `botanical_atlas_site/` and `tools/`. Any write to the
substrate or track namespaces is a Barrier-2 violation; the test suite
checks for none.
