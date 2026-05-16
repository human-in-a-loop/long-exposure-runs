---
created: 2026-05-16T18:28:00Z
cycle: 34
run_id: run-2026-05-15T153635Z
agent: worker
milestone: M23-localized-trace-numerator-quotient-family-model
---

# M23 Localized Trace Numerator Quotient-Family Model

## Summary

M23 converts the M22 localized Corollary 3.4 numerator target into an inspectable quotient-family budget. The exact paper numerator is indexed by `gamma1,gamma2 in P(X)` and `k1,k2 >= 1`, with Selberg weights, localized transform weights, and the polynomial numerator `Q_{gamma1^k1,gamma2^k2}(x)`. The quotient family behind each `Q` is the folded surface-group-law quotient family in Lemma 3.3, not an independent-permutation enumeration.

The generated model is intentionally a proxy. It uses bounded length bins, primitive-power bins, three transform-weight models, quotient-control tags, and `d=C-V` strata to test whether localization plausibly changes the aggregate obstruction.

## Built Artifacts

- `docs/proof_ledger/localized_trace_numerator_quotient_family_model.md`
- `scripts/model_localized_trace_numerator_quotients.py`
- `tests/test_localized_trace_numerator_quotients.py`
- `data/extension_candidates/localized_trace_numerator_quotient_terms.csv`
- `data/extension_candidates/localized_trace_numerator_strata_summary.csv`
- `data/extension_candidates/localized_trace_numerator_weight_taxonomy.csv`
- `reports/figures/m23_localized_quotient_strata_tv.png`
- `reports/figures/m23_transform_weight_vs_family_growth.png`

## Quantitative Budget

The generator produced 4,800 term rows and 27 support-valid stratum summary rows. Total weighted-variation proxy by transform model:

| transform model | total weighted TV proxy |
|---|---:|
| compact support | 619646.329313 |
| Paley-Wiener scaled | 244563.796952 |
| optimistic decay | 16199.197116 |

The compact-support-only model leaves the quotient-family growth obstruction essentially intact. The Paley-Wiener envelope reduces mass but still leaves a large rank-two/unknown aggregate. The optimistic extra decay changes the scale substantially, which suggests the next useful proof question is whether any real localized transform or geodesic estimate can justify comparable damping.

![total-variation proxy by localized numerator stratum and transform-weight model](reports/figures/m23_localized_quotient_strata_tv.png)

![comparison of localized transform damping against quotient-family growth proxies across support bins](reports/figures/m23_transform_weight_vs_family_growth.png)

## Dominant Unknowns

The main unknown remains the actual variation of `Q_{gamma1^k1,gamma2^k2}` after summing over the folded surface-group quotient family. The rows tagged `unknown_surface_group` are not counted as M4-certified, and the tests enforce that rule. Diagonal/cyclic rows are separated from rank-two/noncyclic rows because their deterministic or lower-rank behavior should not be averaged into the expected bottleneck.

The model preserves `d=C-V` strata in the summary, so a future coefficient-variation theorem can attach a fixed-power bound before summing. This is the main practical output of M23: the next proof target is now a weighted, localized, stratum-preserving numerator estimate rather than a global variance slogan.

## Decision

`attempt analytic weight-decay lemma next`

Reason: the finite proxy table already shows that compact support and the basic Paley-Wiener envelope do not obviously defeat family growth. A finite enumeration would be useful later, but without an analytic reason for extra damping it risks reproducing the M9-M15 aggregate obstruction in a more detailed toy model.

## Validation

Commands run:

```text
python3 -m py_compile scripts/model_localized_trace_numerator_quotients.py tests/test_localized_trace_numerator_quotients.py
python3 scripts/model_localized_trace_numerator_quotients.py
python3 tests/test_localized_trace_numerator_quotients.py
figure check reports/figures/m23_localized_quotient_strata_tv.png
figure check reports/figures/m23_transform_weight_vs_family_growth.png
```

All passed.
