---
created: 2026-05-17T23:59:00Z
run_id: fork-56e44dff3ca4-clone-1
agent: worker
milestone: M2.T2
schema_version: v1.0
---

# ENRICHMENT_AUDIT.md — Track 2 Ghost-Partner Enrichment

## Status

Track 2 enrichment is **seed-scale and schema-conformant**. It converts the
Barrier 1 paleobotany/anachronism rows into Track 2-local enrichment artifacts
without promoting any seed into a prediction.

## Inputs

| Input | Role | Rows used |
|---|---|---:|
| `phytograph_dataset/hyperedges.parquet` / `anachronism_candidate_edge` | cited Janzen-Martin and related candidate seeds | 31 |
| `phytograph_dataset/hyperedges.parquet` / `distribution` | PHYLACINE range-context support | 52 |
| `substrate/staging/paleobotany_sources/*/*.jsonl` | extinct fauna, paleo-context, and extant disperser support nodes | 366 |

The frozen Barrier 1 substrate was read-only. This branch wrote only under
`tracks/track2/`.

## Outputs

| Artifact | Description |
|---|---|
| `tracks/track2/data/ghost_partner_seed_edges.parquet` | Track 2 seed edge table derived from cited `anachronism_candidate_edge` rows. |
| `tracks/track2/data/ghost_partner_seed_edges.tsv` | Diffable copy of the seed edge table. |
| `tracks/track2/data/anachronism_candidate_seed_summary.tsv` | Candidate-class coverage summary for Barrier 2. |
| `tracks/track2/data/ghost_partner_support_nodes.parquet` | Extinct-fauna, paleo-context, and extant-disperser support nodes. |
| `tracks/track2/data/ghost_partner_range_context_edges.parquet` | PHYLACINE distribution support edges, not predictions. |
| `tracks/track2/data/ghost_partner_enrichment_metrics.json` | Machine-readable counts and safety-check results. |
| `tracks/track2/tests/test_ghost_enrichment.py` | Regression tests for evidence-boundary and schema conformance. |

## Coverage

| Metric | Value |
|---|---:|
| Candidate seed edges | 31 |
| Candidate classes | 6 |
| Unique plant names | 24 |
| Unique extinct-fauna nodes in seed edges | 11 |
| Pending-crosswalk seed rows retained as caveated seeds | 25 |
| Resolved seed rows | 6 |
| Range-context support edges | 52 |
| Extinct-fauna support nodes | 237 |
| Paleo-context support nodes | 80 |
| Modern-disperser context nodes | 49 |
| Inferred candidate rows emitted | 0 |
| Prediction-ledger rows written | 0 |

## Candidate Classes

| Candidate class | Seed edges | Plant names | Extinct fauna | Pending crosswalk rows | Sources |
|---|---:|---:|---:|---:|---|
| `amazonian_palm_or_ground_sloth_fruit` | 3 | 2 | 2 | 2 | Guimaraes2008|Hansen&Galetti2009 |
| `european_browsing_regime` | 1 | 1 | 1 | 1 | Barlow2000 |
| `madagascar_elephant_bird_baobab` | 2 | 2 | 1 | 0 | Bond&Silander2007 |
| `neotropical_gomphothere_large_fruit` | 16 | 13 | 3 | 14 | Barlow2000|Guimaraes2008|Janzen&Martin1982 |
| `new_zealand_moa_divarication` | 2 | 1 | 2 | 2 | Greenwood&Atkinson1977 |
| `north_american_temperate_megafauna_fruit` | 7 | 5 | 3 | 6 | Barlow2000|Janzen&Martin1982 |

## Citation Source Mix

| Source | Seed rows |
|---|---:|
| Barlow2000 | 9 |
| Bond&Silander2007 | 2 |
| Greenwood&Atkinson1977 | 2 |
| Guimaraes2008 | 8 |
| Hansen&Galetti2009 | 1 |
| Janzen&Martin1982 | 9 |

## Evidence Boundary

- Every row in `ghost_partner_seed_edges.parquet` has
  `enrichment_role = literature_curated_seed`.
- Every row has `prediction_status = not_prediction` and
  `enters_prediction_ledger = false`.
- Every row has `inferred_anachronism_claim = false`; no spatial-overlap or
  morphology-only candidate was generated in this branch.
- `allowed_evidence_scope` remains `cited hypothesis only; not inferred by
  Barrier 1`, and the copied caveats retain the source warning that the row is
  not established anachronism status.
- `pending_crosswalk` rows are retained with their raw names and caveats; this
  branch does not perform independent synonym normalization.

## Mechanism Check

Mechanism hypothesis: premature prediction leakage would occur if a cited
candidate seed were recoded as a ranked candidate or model output. This build
rules that mechanism out for M2.T2 by setting all seed rows to
`not_prediction`, writing zero prediction-ledger rows, and testing that no row
has `inferred_anachronism_claim = true`.

Special points:

- `pending_crosswalk = true`: retained as caveated seed, not discarded and not
  resolved locally.
- Missing citation: build fails; all emitted seed rows require citation short
  name and page/section.
- Inference flag true: build fails; all emitted seed rows must be cited source
  rows.
- Prediction ledger boundary: no `ghost_partner_predictions.tsv` or master
  `prediction_ledger.tsv` writes are performed.

## Known Limitations

- This is not the M3.T2 Ghost-Partner Candidate Ranker. It is a Wave 2
  enrichment seed table.
- The seed canon is source-biased toward Janzen-Martin/Guimarães neotropical
  megafaunal fruit cases plus a small set of Madagascar, New Zealand, temperate
  North American, and European examples.
- Twenty-five seed rows are still `pending_crosswalk` after Barrier 1. They are
  usable as literature-curated seeds but are not ready for taxon-key-only
  joins without Barrier 2 handling.
- PHYLACINE/IUCN range context is support evidence only; no range-overlap
  inference was run.

## Reproduction

```bash
python3 tracks/track2/scripts/build_ghost_enrichment.py
python3 -m pytest -q tracks/track2/tests/test_ghost_enrichment.py
```
