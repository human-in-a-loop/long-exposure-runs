---
created: 2026-05-16T18:55:00Z
cycle: 35
run_id: run-2026-05-15T153635Z
agent: worker
milestone: M24-localized-transform-geodesic-weight-decay-obstruction
---

# M24 Localized Transform/Geodesic Weight Decay Obstruction

## Summary

M24 tests whether the localized transform and Selberg/geodesic weights in the M22 numerator can justify the optimistic M23 transform model. The answer is negative inside the compact-support Paley-Wiener architecture. The localized transform scales as `delta_r e^{-ir0 t} phi^vee(delta_r t)`, so decay is in `u=t delta_r`, not in `t` itself.

## Built Artifacts

- `docs/proof_ledger/localized_transform_geodesic_weight_decay.md`
- `scripts/analyze_localized_transform_weight_decay.py`
- `tests/test_localized_transform_weight_decay.py`
- `data/extension_candidates/localized_transform_weight_decay.csv`
- `data/extension_candidates/localized_transform_decay_summary.csv`
- `reports/figures/m24_transform_envelope_scaling.png`
- `reports/figures/m24_geodesic_growth_vs_transform_decay.png`

## Quantitative Output

The analyzer generated 960 rows over bulk window exponent `d`, support exponent `eta`, transform model, and growth proxy. Among the 396 rows satisfying both M22 support and endpoint conditions, all 198 compact-support-compatible rows are classified as `compact_route_obstructed`; 99 zero-mean/vanishing-moment rows do not preserve a positive count statistic; and the 99 noncompact Gaussian-tail contrast rows are classified as `contrast_insufficient` for the M23 rate `exp(-0.18 t)` against the positive growth proxies used here.

| transform model | compatibility | dominant verdict on M22 rows |
|---|---|---|
| compact support only | compatible | compact route obstructed |
| smooth Schwartz scaled | compatible | compact route obstructed |
| vanishing moment scaled | conditional zero mean | not count-positive |
| noncompact Gaussian `t` tail | incompatible with compact support | contrast insufficient at rate 0.18 |

![scaled localized transform envelopes versus t delta_r, showing what changes and what does not inside the required support](reports/figures/m24_transform_envelope_scaling.png)

![net transform damping versus geodesic/family growth proxies across support exponents](reports/figures/m24_geodesic_growth_vs_transform_decay.png)

## Comparison To M23

M23 compared three transform-weight models:

- `compact_support`: no internal damping inside support.
- `paley_wiener_scaled`: damping only through a scaled support variable.
- `optimistic_decay`: an extra `exp(-0.18 t)` factor.

M24 explains the gap. The first two are compatible with the compact-support trace architecture but do not remove the rank-two/unknown aggregate obstruction asymptotically. The third is the only model with support-length exponential damping, but it is not a consequence of Paley-Wiener scaling; at the M23 contrast rate `0.18`, it is also weaker than the positive geodesic/family growth proxies used in this diagnostic. A successful noncompact route would need both a new geometric-tail trace architecture and a tail rate exceeding the relevant growth/variation rate.

## Answers To Key Questions

1. The strongest paper-compatible transform decay inside support is scaled decay in `u=t delta_r`, plus ordinary smoothness-dependent tail improvement after `u` is large.
2. The identity `h_delta^vee(t)=delta_r e^{-ir0t} phi^vee(delta_r t)` gives no decay in `t` alone.
3. After Selberg/geodesic and family-growth proxies are included, compatible compact-support weights do not produce the M22 beta-saving mechanism.
4. M23's optimistic decay is not compatible with the existing compact-support Paley-Wiener proof architecture.
5. The sharper obstruction is transform-weight nondecay in `t`: geodesic/family growth then overwhelms the available scaled damping.

## Decision

`close compact-support local-window route`

This closes only the route where transform/geodesic weights themselves are expected to supply the M23 optimistic damping. A compact-support coefficient-variation theorem could still exist, but it would need new control of the actual Lemma 3.3/Corollary 3.4 quotient-polynomial family rather than relying on localized transform decay. The noncompact route should be a separate future branch only if one first formulates a trace-formula tail theorem controlling the omitted geometric side.

## Validation

Commands run:

```text
python3 -m py_compile scripts/analyze_localized_transform_weight_decay.py tests/test_localized_transform_weight_decay.py
python3 scripts/analyze_localized_transform_weight_decay.py
python3 tests/test_localized_transform_weight_decay.py
figure check reports/figures/m24_transform_envelope_scaling.png
figure check reports/figures/m24_geodesic_growth_vs_transform_decay.png
```

All passed before final ledger validation.
