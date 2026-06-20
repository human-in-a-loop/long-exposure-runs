---
created: 2026-05-18T00:00:00Z
milestone: M3.A
fork: eec13528227c
clone: 2
artifact_type: barrier3_atlas_scaffold_report
---

# Botanical Atlas Barrier 3 Scaffold

## Scope

This branch builds the Botanical Atlas as the Barrier 3 integration surface.
It does not create new biological predictions and does not promote any row
into the master `prediction_ledger.tsv` or `speculation_ledger.tsv`.

The scaffold reads the frozen substrate and track-local outputs, then emits a
local static site under `botanical_atlas_site/`. Its core invariant is that a
researcher can distinguish substrate evidence, enriched evidence, model
predictions, and missing data on every taxon page.

## Built Artifacts

| Artifact | Purpose |
|---|---|
| `botanical_atlas_site/index.html` | Local static Atlas shell. |
| `botanical_atlas_site/app.js` | Search, page rendering, evidence-band display, counter-claim payload builder. |
| `botanical_atlas_site/style.css` | Evidence-band visual styling. |
| `botanical_atlas_site/search_index.json` | 60,000-row local taxon search index. |
| `botanical_atlas_site/pages/*.json` | 60,000 per-taxon page payloads. |
| `botanical_atlas_site/coverage_summary.json` | Machine-readable coverage and adapter status. |
| `botanical_atlas_site/provenance_registry.json` | Source-group license/access-date summary. |
| `botanical_atlas_site/counter_claim_template.json` | Counter-claim schema for researcher correction workflow. |
| `botanical_atlas_site/build_log.json` | Reproducible build metadata. |
| `tools/file_counter_claim.py` | Append-only counter-claim validator and ledger emitter. |
| `tests/test_atlas_build.py` | Atlas contract tests. |

## Integration Contract

Track outputs are integrated as follows:

| Track | Atlas mode | Input paths | Adapter result |
|---|---|---|---|
| Track 1 Reticulation Atlas | prediction adapter | `tracks/track1/outputs/tci_per_taxon.tsv`; `tracks/track1/outputs/tci_hotspots_genus.tsv` | 60,000 TCI instrument rows across 60,000 accepted-key taxa. These are data-limited instrument results, not validated reticulation claims. |
| Track 2 Ghost Hyperedges | prediction adapter | `tracks/track2/data/ghost_partner_candidate_scores.tsv`; `tracks/track2/data/ghost_partner_predictions.tsv` | 6 prediction rows across 6 accepted-key taxa. |
| Track 3 Convergence Pressure | prediction adapter | `tracks/track3/data/convergence_pressure_scores.tsv`; `tracks/track3/data/convergence_predictions.tsv` | 50 page-level rows projected from pending convergence-prior hypotheses onto accepted-key pages named by listed supporting hyperedges. This is a queryability sample, not exhaustive carrier enumeration. |
| Track 4 Domestication Hypergraph | prediction adapter | `tracks/track4/data/crop_substitution_candidates.tsv` | 6 endpoint rows, rendered across 5 accepted-key taxa after crop/wild-relative projection. |
| Track 5 Chemodiversity Predictor | prediction adapter | `tracks/track5/data/phytochemistry_predictions.tsv` | 1,405 pending screening-prior rows across 65 accepted-key taxa. |
| Track 6 Foundation-Model Probe | prediction adapter | `tracks/track6/data/probe_results.tsv`; `tracks/track6/data/offline_probe_question_bank.tsv` | 244 deterministic offline result rows across 48 accepted-key taxa. |

## Build Results

Command:

```bash
python3 botanical_atlas_site/build_atlas.py
```

Observed output:

| Metric | Value |
|---|---:|
| Substrate nodes read | 363,237 |
| Substrate hyperedges read | 641,183 |
| Taxon crosswalk rows read | 75,269 |
| Per-taxon pages written | 60,000 |
| Search-index rows written | 60,000 |

Per-track page state after the final build:

| Track | Observed pages | Enriched pages | Predicted pages | Data-limited pages |
|---|---:|---:|---:|---:|
| Track 1 | 0 | 0 | 60,000 | 0 |
| Track 2 | 0 | 0 | 6 | 59,994 |
| Track 3 | 4 | 3,198 | 50 | 56,748 |
| Track 4 | 0 | 0 | 5 | 59,995 |
| Track 5 | 0 | 1,255 | 65 | 58,680 |
| Track 6 | 0 | 0 | 48 | 59,952 |

## Evidence And Prediction Labeling

The Atlas uses four evidence states:

- `observed`: source-ingested substrate rows such as taxonomy, image,
  distribution, or life-form evidence.
- `enriched`: Wave 2 track-local source projections onto accepted keys.
- `predicted`: Wave 3 instrument or result rows adapted from track-local
  outputs. These carry `inferred_flag=true` in the page payload.
- `data-limited`: no accepted-key substrate or instrument rows are available
  for that taxon/track section.

The Track 1 adapter preserves the key caveat that current TCI rows are
data-limited instrument outputs: chromosome-count and ploidy-state rows are
structural context only, and canonical polyploid recovery is not validated.
The Track 3 adapter preserves the key caveat that `drupe` and `capsule` rows
are pending convergence-prior hypotheses awaiting held-out validation and
source/family/sampling ablations. The Track 5 adapter preserves the key caveat that these rows are pending
screening priors, not observed detections, typical concentrations,
bioactivity claims, clinical claims, or safety claims. The Track 4 adapter
preserves `not_computable_no_observed_bioclim_vectors` climate status. The
Track 6 adapter exposes deterministic offline controls only; no paid,
key-gated, remote, Anthropic/OpenAI/Gemini/Pl@ntNet/iNaturalist execution is
represented.

## Counter-Claim Path

Every taxon page includes a counter-claim form that builds a JSON payload with
an explicit `target_edge_id`. The validator rejects free-form notes that do
not target a page row.

CLI examples:

```bash
python3 tools/file_counter_claim.py --inline '{"accepted_taxon_key":"wfo:wfo-0000552025-2025-12","target_edge_id":"atlas:track2:T2C0016","target_kind":"predicted_row","reviewer_id":"email:reviewer@example.org","comment":"Check whether the cited dispersal-failure source supports the candidate status."}' --no-ledger
```

Without `--no-ledger`, the CLI appends to
`botanical_atlas_site/counter_claims.jsonl` and attempts to emit an
append-only `_run/counter-claim-<uuid>` ledger event.

## Validation

Commands run:

```bash
python3 -m pytest -q tests/test_atlas_build.py
python3 botanical_atlas_site/build_atlas.py
python3 -m long_exposure.tools.promise_check <run-root>
```

Results:

- `tests/test_atlas_build.py`: 10 passed.
- Full Atlas build: succeeded, 60,000 pages and 60,000 search rows.
- `promise_check`: exit 0 with known legacy/backlog warnings only.

The tests assert:

- every generated page has six fixed track sections;
- observed rows never carry `inferred_flag=true`;
- predicted rows have confidence;
- Track 1 and Track 3 no longer remain stale placeholder contracts after
  sibling output integration;
- Track 1, Track 2, Track 3, Track 4, Track 5, and Track 6 existing outputs
  appear as predicted rows;
- every rendered evidence/prediction row has provenance;
- search-index rows address page files;
- counter-claim validation rejects missing targets and empty comments.

## Limitations

The Atlas is a scaffold, not audit-level Barrier 3 closure by itself.

- Track 1 TCI rows cover 60,000 accepted keys, but the Track 1 report remains
  explicit that canonical polyploid recovery is data-limited.
- Track 3 page projection uses the explicitly listed supporting hyperedges in
  `convergence_predictions.tsv`; long support lists are truncated in that TSV,
  so page-level Track 3 exposure is queryable but not exhaustive.
- Search is local and client-side over 60,000 rows. The documented design path
  to 100,000 taxa is sqlite FTS5/sql.js if flat-array latency becomes binding.
- Track 2, Track 4, Track 5, and Track 6 page exposure is limited by accepted
  keys in the track outputs. Sparse prediction-page counts are therefore a
  data-join finding, not an Atlas rendering failure.
- Static HTML cannot append counter-claims directly without a local write
  service; the page builds a valid payload and the CLI performs append-only
  capture.

## Barrier 3 Interpretation

This integration advances `M3.A` by making the Atlas query and render existing
Track 1, Track 2, Track 3, Track 4, Track 5, and Track 6 outputs with
provenance and evidence-vs-prediction labels. It does not perform
audit-level validation and does not promote any row to the master prediction
or speculation ledgers.

Barrier 3 can now be assessed by the auditor/coordinator against the updated
site artifacts; this worker cycle does not mark the barrier globally closed.
