---
created: 2026-05-17T23:59:55+00:00
cycle: 9
run_id: fork-e08673192f98-clone-1
agent: worker
milestone: M3.T2
---

# Track 2 Ghost-Partner Candidate Ranker

## Status

This is the first M3.T2 Ghost-Partner Candidate Ranker over the validated Barrier 2 Track 2 enrichment layer. It ranks cited paleobotany, extinct-fauna, and Janzen-Martin seed rows for validation priority only. It does not claim that any row is an established anachronism or write the master `prediction_ledger.tsv`.

## Inputs

| Input | Role |
|---|---|
| `tracks/track2/data/ghost_partner_seed_edges.parquet` | 31 cited candidate seed edges from Wave 2 enrichment |
| `tracks/track2/data/anachronism_candidate_seed_summary.tsv` | Candidate-class seed coverage |
| `tracks/track2/data/ghost_partner_support_nodes.parquet` | Extinct-fauna, paleo-context, and modern-disperser support nodes |
| `tracks/track2/data/ghost_partner_range_context_edges.parquet` | PHYLACINE range-context support, not prediction evidence |
| `data/barrier2_track_enrichment_conformance.json` | Barrier 2 conformance status: Track 2 ready at seed scale |

## Ranking Mechanism

The script `scripts/track2_ghost_partner_ranker.py` computes:

```text
S(c) = 0.25 M + 0.25 E + 0.20 F + 0.20 G + 0.10 P - 0.15 L - 0.10 Q
```

where `M` is morphology support, `E` is extinct-fauna or paleo-context support, `F` is modern dispersal-failure support, `G` is geography/time compatibility, `P` is provenance completeness, `L` is living-megafauna ambiguity, and `Q` is singleton-source thinness. The score is a prioritization statistic, not a truth value.

## Outputs

| Output | Rows | Purpose |
|---|---:|---|
| `tracks/track2/data/ghost_partner_candidate_scores.tsv` | 31 | Ranked candidate table with component columns and candidate-only statuses |
| `tracks/track2/data/ghost_partner_score_components.tsv` | 217 | Long-form component diagnostics for auditing and plotting |
| `tracks/track2/data/ghost_partner_data_limited_cases.tsv` | 27 | Rows blocked by missing accepted key, weak support, ambiguity, or source thinness |
| `tracks/track2/figures/ghost_candidate_score_components.png` | 1 | Component coverage by candidate class |
| `tracks/track2/tests/test_ghost_partner_ranker.py` | 5 tests | Regression checks for evidence boundaries and ranker behavior |

![Component coverage by candidate class; y-axis is mean component value from 0 to 1, with separate bars for morphology, extinct-fauna/paleo context, modern dispersal-failure, and geography/time compatibility.](figures/ghost_candidate_score_components.png)

## Result Summary

| Status | Count |
|---|---:|
| `data_limited` | 25 |
| `candidate_pending_validation` | 4 |
| `insufficient_support` | 2 |

The top score was 0.700. High-ranking rows require morphology plus extinct-fauna/paleo support and at least partial geography/time compatibility; morphology alone is not enough to produce a validation-ready candidate. Modern dispersal-failure evidence is sparse in the seed layer, so that component remains zero or weak for most rows rather than being inferred from fruit size.

## Evidence Boundaries

All scored rows keep `inferred_anachronism_claim = false` and `enters_prediction_ledger = false`. Rows missing an accepted focal taxon key are retained as `data_limited` or `insufficient_support`, not promoted to canonical predictions. Living-megafauna-compatible cases receive `ambiguity_flag = living_megafauna_compatible_genus`, so the ranker does not collapse extant megafauna dispersal into ghost-megafauna inference.

## Validation Readiness

Wave 4 can use `ghost_partner_candidate_scores.tsv` as a held-out validation queue, with `ghost_partner_score_components.tsv` providing the reason each candidate ranked where it did. The most important validation targets are accepted-key rows in `candidate_pending_validation`, followed by data-limited canonical Janzen-Martin examples once crosswalk gaps are resolved. The ranker is hypothesis-generation only until held-out validation and ablation test whether the scores survive source-density, geography, and living-megafauna ambiguity controls.
