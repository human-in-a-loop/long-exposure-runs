---
created: 2026-05-16T18:25:00Z
cycle: 34
run_id: run-2026-05-15T153635Z
agent: worker
milestone: M23-localized-trace-numerator-quotient-family-model
---

# Localized Trace Numerator Quotient-Family Model

## Paper Object

Lemma 2.1 gives the trace-side non-identity statistic as a primitive-geodesic and primitive-power sum:

```text
G_n(phi) =
  sum_{gamma in P(X)} sum_{k >= 1}
    ell_gamma(X)/(2 sinh(k ell_gamma(X)/2))
    phi(k ell_gamma(X))
    tr rho(gamma^k).
```

In Proposition 3.1 the paper takes `phi = (h o f_Lambda0)^vee`. Squaring the centered trace statistic gives the two-trace summation in (3.13):

```text
sum_{gamma1,gamma2 in P(X)} sum_{k1,k2 >= 1}
  ell_gamma1 ell_gamma2
  / (4 sinh(k1 ell_gamma1/2) sinh(k2 ell_gamma2/2))
  (h o f_Lambda0)^vee(k1 ell_gamma1)
  (h o f_Lambda0)^vee(k2 ell_gamma2)
  E[tr rho(gamma1^k1) tr rho(gamma2^k2)].
```

Lemma 3.3 expands the two-trace expectation for cyclically reduced nontrivial words with `|gamma1| + |gamma2| <= q`:

```text
E[tr rho(gamma1) tr rho(gamma2)]
  = Q_{gamma1,gamma2}(1/n) / Q_id(1/n) + O((Cq)^(Cq) n^(-q)).
```

The proof factors morphisms from the graph `C_{gamma1,gamma2}` of two disjoint labelled cycles through folded labelled quotient graphs `W_r`. The folding condition includes the surface-group-law constraint: every path in `W_r` spelling an element in the kernel of `F_{2g} -> Gamma` is closed. This is the point where the M23 proxy must not be confused with independent permutations.

Corollary 3.4 packages the weighted expansion into the polynomial numerator

```text
p(x) =
  sum_{gamma1,gamma2 in P(X)} sum_{k1,k2 >= 1}
    ell_gamma1 ell_gamma2
    / (4 sinh(k1 ell_gamma1/2) sinh(k2 ell_gamma2/2))
    (h o f_Lambda0)^vee(k1 ell_gamma1)
    (h o f_Lambda0)^vee(k2 ell_gamma2)
    Q_{gamma1^k1,gamma2^k2}(x).
```

The nonzero terms satisfy a support-derived word-length bound using `|gamma| <= K1 ell_gamma + K2`.

## Localized Numerator

For the M21 fixed-energy bulk window, M22 replaces the endpoint test by a localized test `h_{Delta,q}` centered at `r0 = sqrt(Lambda0 - 1/4)`, with `Delta = n^(-d)` and support scale `q = n^eta`. The localized numerator is therefore the Corollary 3.4 numerator with the transform value replaced by the localized transform:

```text
p_{Delta,q}(x) =
  sum_{gamma1,gamma2 in P(X)} sum_{k1,k2 >= 1}
    a(gamma1,k1) a(gamma2,k2)
    h_{Delta,q}^vee(k1 ell_gamma1)
    h_{Delta,q}^vee(k2 ell_gamma2)
    Q_{gamma1^k1,gamma2^k2}(x),

a(gamma,k) = ell_gamma(X)/(2 sinh(k ell_gamma(X)/2)).
```

The exact summation indices are `gamma1,gamma2 in P(X)` and `k1,k2 >= 1`, restricted by transform support `k_i ell_gamma_i <= O(q)` and the Lemma 3.3 word-length condition after converting geodesic length to word length.

## Weight Taxonomy

Each quotient/template contribution carries these factors:

| factor | exact/proxy | role |
|---|---|---|
| `gamma_i`, `k_i` | exact paper indices | primitive geodesic and primitive-power summation variables |
| `ell_gamma/(2 sinh(k ell_gamma/2))` | exact paper weight | Selberg/geodesic decay for each trace |
| `h_{Delta,q}^vee(k ell_gamma)` | exact target, modeled by proxy envelopes | localized transform weight and support cutoff |
| diagonal/cyclic subtraction | proof annotation | separated because deterministic or cyclic contributions need different treatment |
| `Q_{gamma1^k1,gamma2^k2}` | exact paper numerator object | random-cover polynomial numerator from Lemma 3.3 |
| folded quotient identifier | exact in Kim--Tao, proxy in M23 data | actual object is a folded surface-group-law quotient `W_r`; M23 only records tags |
| `d=C-V` | proxy annotation | carries the M11-M15 template power analogue and is never globally aggregated before stratification |

The generated taxonomy file records these distinctions in `data/extension_candidates/localized_trace_numerator_weight_taxonomy.csv`.

## Row Schema

The M23 term table uses this schema:

| column | source status |
|---|---|
| `gamma1_proxy`, `gamma2_proxy` | proxy length-bin representatives for exact `gamma1,gamma2 in P(X)` |
| `primitive_exponent_k1`, `primitive_exponent_k2` | exact paper index type, bounded in the proxy |
| `length_bin_1`, `length_bin_2`, `support_argument_i` | proxy bins for exact `ell_gamma_i` and `k_i ell_gamma_i` |
| `transform_model`, `transform_weight_i`, `support_valid` | proxy models for exact localized transform values |
| `geodesic_weight_proxy`, `primitive_power_multiplicity_proxy` | proxy numerical weights matching the paper's Selberg factor and primitive-power bookkeeping |
| `quotient_identifier_proxy`, `rank_proxy`, `cyclic_flag`, `quotient_control_tag` | proxy annotations, not exact Kim--Tao quotients |
| `C_constraints_proxy`, `V_vertices_proxy`, `d_C_minus_V` | proxy template-power annotation kept as a stratum |
| `Q_numerator_type` | exact paper object type, without computed coefficients |
| `weighted_total_variation_proxy` | modeled contribution to coefficient-variation budget |
| `coverage_by_M4_M12` | internal coverage label; `unknown_surface_group` rows are not M4-certified |

## Strata To Track

The coefficient-variation problem should keep at least these strata:

1. Word/geodesic support bins through `k_i ell_gamma_i <= O(q)`.
2. Primitive exponent pair `(k1,k2)`.
3. Diagonal/cyclic versus noncyclic rank-two status.
4. Surface-group-law unknown rows separately from independent-permutation skeleton rows.
5. `d=C-V` before any total-variation aggregation.
6. Transform-scale bins, since support and envelope damping are the only plausible localized numerator gain in this route.

## Proxy Model Result

The script `scripts/model_localized_trace_numerator_quotients.py` builds 4,800 bounded proxy rows and 27 support-valid, `d=C-V`-stratified summaries. It compares:

1. compact support cutoff only,
2. Paley-Wiener scaled window envelope,
3. optimistic additional decay.

Total weighted-variation proxy by transform model:

| model | total weighted TV proxy |
|---|---:|
| compact support | 619646.329313 |
| Paley-Wiener scaled | 244563.796952 |
| optimistic decay | 16199.197116 |

Localization damps the aggregate substantially in the optimistic model, but the compact-support and Paley-Wiener envelope rows remain dominated by rank-two/noncyclic and unknown surface-group strata. Thus M23 does not prove coefficient variation; it isolates the next target.

## Finite Proxy Boundary

The finite proxy extracted here is a quotient-family budget schema, not an enumeration of Kim--Tao's `R` or the `W_r`. It preserves paper summation variables and weights while replacing actual surface-group quotient data by tags:

```text
identity/diagonal, cyclic, rank_two_noncyclic, unknown_surface_group.
```

This avoids the false step of replacing the surface group by independent permutations. A future finite enumeration can be attempted only if it implements the surface-group-law condition from Lemma 3.3 or clearly remains a labelled free-group skeleton.
