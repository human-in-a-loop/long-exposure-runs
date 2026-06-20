---
title: "Random Hyperbolic Surface Spectral Rigidity — cycles 46-48"
date: "2026-05-16"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# Random Hyperbolic Surface Spectral Rigidity — cycles 46-48

## Abstract

Cycles 46-48 returned to the hardest unresolved surface-facing bottleneck in the Kim--Tao rigidity architecture: the numerator in Corollary 3.4, which packages the second moment of the compactly supported trace statistic as a denominator-normalized polynomial value. The work did not prove a new exponent improvement. It converted the remaining obstruction into a precise sequence of theorem targets and route classifications.

Cycle 46 / M35 reconstructed the actual Corollary 3.4 ratio and located the existing `q^(2 kappa)` loss at the Markov-interpolation step applied to `x^2 p(x)`, rather than in the definition of the numerator itself. Cycle 47 / M36 isolated the direct small-`x` replacement target for the evaluated ratio `p(1/n)/Q_id(1/n)` and showed how denominator loss affects any proposed saving. Cycle 48 / M37 classified the only remaining direct route: signed pointwise cancellation at the actual evaluation point `x=1/n`. It remains an independent target only if the grouping is surface-attached; absolute fixed-stratum control collapses back into coefficient variation.

All three milestones were validated. M35 required one auditor repair to restore the correct paper energy factor `Lambda0^20`; M36 and M37 required no substantive repair. The final state is a narrowed research fork: either prove a genuinely surface-level signed value cancellation theorem for `p(1/n)/Q_id(1/n)`, or treat the compact-support route as a coefficient/signed-variation problem.

## Introduction

The research campaign studies Kim and Tao's paper *Eigenvalue rigidity of hyperbolic surfaces in the random cover model*, using the local files `2603.01127.pdf` and `2603.01127.txt`. Earlier cycles reconstructed the paper, explored product-ratio and quotient-family mechanisms, built local-window obstruction ledgers, mined theorem-level corollaries, and closed a separate Schreier benchmark branch as a standalone finite-model theorem package.

The immediate context for cycles 46-48 is the compact-support trace route. In this route, Kim--Tao use the Selberg trace formula and random-cover trace statistics to control a second moment. The unresolved question is whether the proof's `q^(2 kappa)` loss is structural or whether it can be reduced by controlling the actual surface-group aggregate more directly.

The object under study is the Corollary 3.4 expression

```text
E S_n(h)^2
  = p(1/n) / Q_id(1/n)
    + O(Lambda0 (Cq)^(kappa q) n^(-q) ||htilde||^2).
```

Here `p(x)` is a Selberg-weighted sum of quotient polynomials attached to pairs of surface-group elements, and `Q_id(x)` is the normalizing denominator from the Kim--Tao rational expansion. The paper proves that `Q_id(1/n)` is bounded above and below in the working range. The question is whether one can improve the proof by controlling the normalized value `p(1/n)/Q_id(1/n)` directly.

## Approach

Cycles 46-48 were analytical classification cycles. They did not simulate a replacement surface-group quotient family. Instead, each cycle built proof ledgers, executable exponent ledgers, CSV classifications, and figures that make the compact-support bottleneck explicit.

The sequence was:

1. M35 identified where the paper's `q^(2 kappa)` loss enters and separated paper-proved inputs from open theorem targets.
2. M36 turned one open branch into an exact direct small-`x` theorem target for `p(1/n)/Q_id(1/n)`.
3. M37 tested whether that direct branch remains meaningfully distinct from coefficient variation, concluding that it does only under signed pointwise cancellation at `x=1/n`.

The cycle outputs were validated by scripts, tests, figure checks, `promise_check`, `org_check`, and auditor review. The reporter did not re-audit those results; it consolidates the validated record.

## Source Inventory and Timeline

Cycle 46 began with researcher session `7ae38a1a-b742-4253-99bb-ed3b1ff7755f`. The researcher directed the worker to reconstruct the exact Kim--Tao Lemma 3.3 / Corollary 3.4 numerator, denominator, degree/support scale, reciprocal-integer range, and error term. The goal was to determine whether the `q^(2 kappa)` loss came from the numerator itself or from a later interpolation step.

Worker session `33ac8ff8-977c-4180-9ef3-2f77173a8197` produced the M35 obstruction package: proof ledger, extension report, classifier script, tests, four CSV datasets, and three figures. The worker decision was:

```text
preserve_surface_numerator_as_open_theorem_target_no_schreier_transfer
```

Auditor session `4baeea93-c036-4ec9-82cc-167d838db7c2` validated M35 after repairing one moderate defect: the proof ledger had stated the Markov-stage energy factor as `Lambda0^2`, while the paper's bound is `Lambda0^20`. The auditor repaired the proof ledger and added regression coverage.

Cycle 47 began with researcher session `f180b82d-c061-45a2-8b68-aa4d8da0d390`. The researcher narrowed the next step to direct evaluation of `p(1/n)/Q_id(1/n)` at the actual point `x=1/n`.

Worker session `7c3494e6-3608-409f-b944-df7bd4412d84` produced the M36 direct small-`x` target package: proof ledger, extension report, classifier script, tests, four CSV datasets, and three figures. The worker decision was:

```text
direct_small_x_is_distinct_conditional_target_but_requires_new_surface_ratio_estimate
```

Auditor session `83f0fe80-ebc4-43a0-a490-6a15f4255e59` validated M36 with no critical or moderate defects.

Cycle 48 began with researcher session `7538f575-5120-4470-9497-06322e16514f`. The researcher asked whether the direct small-`x` route could remain independent through signed pointwise cancellation in the actual surface aggregate.

Worker session `3cd70352-0f82-4ea2-bafd-33eb39616ff1` produced the M37 signed pointwise cancellation package: proof ledger, extension report, classifier script, tests, four CSV datasets, and three figures. The worker decision was:

```text
signed_pointwise_cancellation_remains_independent_only_as_new_surface_ratio_theorem
```

Auditor session `56cd9686-f4b4-40ec-a9ee-5eeaf1ffc9bd` validated M37 with no critical or moderate defects. The only minor issue was a timestamp neatness problem in the M37 researcher ledger entries; `promise_check` accepted the lifecycle.

No `REFERENCES.md` file was present in the workspace during reporting. The references section therefore lists local paper files, sessions, artifacts, figures, and audit inputs rather than global numbered bibliographic entries.

## Finding 1: M35 Localized the Markov Loss

M35 established that the `q^(2 kappa)` loss is paid when the proof uses reciprocal-integer control and Markov brothers' inequality on `x^2 p(x)`. It is not forced merely by defining the Corollary 3.4 numerator.

The weighted numerator reconstructed in the proof ledger is

```text
p(x)
 = sum_{gamma1,gamma2 in P(X)} sum_{k1,k2>=1}
     ell_gamma1(X) ell_gamma2(X)
     ------------------------------------------------
     4 sinh(k1 ell_gamma1(X)/2) sinh(k2 ell_gamma2(X)/2)

     * (h o f_Lambda0)^vee(k1 ell_gamma1(X))
     * (h o f_Lambda0)^vee(k2 ell_gamma2(X))
     * Q_{gamma1^k1,gamma2^k2}(x).
```

Corollary 3.4 gives

```text
E[G_n(h)^2]
  = p(1/n) / Q_id(1/n)
    + O(Lambda0 (Cq)^(kappa q) n^(-q) ||htilde||^2),
```

with

```text
deg p <= C Lambda0^(-1/2) q,
Q_id(1/n) in [C^(-1), C]
```

in the paper's range.

The paper first obtains reciprocal-integer control

```text
n^(-2) |p(1/n)| <= C Lambda0^20 ||htilde||^2.
```

It then applies Markov control to

```text
P(x) = x^2 p(x),
```

which yields the derivative envelope containing `q^(2 kappa)`. Taylor expansion from `0` transfers this derivative bound back to `x=1/n`.

![where the existing proof pays q^{2 kappa} and which hypothetical controls would change the exponent budget](reports/figures/m35_corollary34_interpolation_loss.png)

The M35 mechanism classification separated six routes:

| Mechanism | M35 status |
|---|---|
| Existing Markov interpolation | Paper-proved baseline |
| Coefficient variation | Conditional surface theorem target |
| Direct small-`x` evaluation | Conditional surface theorem target |
| Signed cancellation | Conditional surface theorem target |
| Stronger Lemma 3.3 | Conditional stronger input |
| Schreier or independent-permutation transfer | Toy-only insufficient |

The generated `m35_candidate_mechanism_classification.csv` also recorded special-point diagnostics. Cancellation or expansion at `x=0` alone is not enough, because the target is the evaluated ratio at `x=1/n`. Any numerator saving must preserve denominator normalization. The hard boundary remains `n >= q^kappa`.

![dependency graph from Lemma 3.3 and Corollary 3.4 to Proposition 3.1, separating paper-proved inputs from open theorem targets](reports/figures/m35_mechanism_dependency_graph.png)

The exponent ledger kept the M22 algebra:

```text
beta = (2 kappa - A) eta + sigma
```

for a hypothetical theorem of the shape

```text
E G_n(h)^2 <= n q^A n^(-sigma+o(1)).
```

M35 did not prove a positive `beta`. It recorded that any improvement requires new surface-group input.

![regime map comparing direct small-x, coefficient-variation, and Markov-interpolation mechanisms](reports/figures/m35_direct_vs_coefficient_variation_map.png)

The M35 audit decision was `VALIDATED` after the `Lambda0^20` repair. The audit rationale was that M35 correctly localized the current trace-side loss to interpolation and cleanly separated paper-proved baseline input from conditional theorem targets.

## Finding 2: M36 Isolated the Direct Small-`x` Target

M36 converted the M35 direct branch into a precise theorem target for the actual denominator-normalized Corollary 3.4 value.

The target was stated as:

```text
|p(1/n) / Q_id(1/n)|
  <= C n Lambda0^20 ||htilde||^2 q^A n^(-sigma+o(1)).
```

The Markov baseline is recovered by

```text
A = 2 kappa,
sigma = 0.
```

M36 introduced an explicit denominator-loss parameter `D`. If

```text
|Q_id(1/n)|^(-1) <= n^D,
```

then the effective saving becomes

```text
beta = (2 kappa - A) eta + sigma - D.
```

In the paper-safe range, `D=0`, because `Q_id(1/n)` is bounded above and below. Outside that range, denominator zeros or near-zeros can erase any numerator saving.

![exponent-saving regions for direct small-x bounds versus the Markov baseline](reports/figures/m36_direct_small_x_budget_map.png)

The M36 output classified direct evaluation as logically distinct from coefficient variation because it asks for one evaluated value, not every coefficient or stratum. However, M36 also recorded that this distinction is only useful if the proof uses signed pointwise cancellation at `x=1/n`. If the proof expands the numerator and bounds absolute coefficient variation, the route becomes a coefficient-variation theorem in substance.

![how denominator loss or near-zero scenarios erase direct-evaluation savings](reports/figures/m36_denominator_obstruction_map.png)

The generated implication table listed five route types:

| Route | M36 conclusion |
|---|---|
| Direct small-`x` ratio bound | Plausible conditional route if it uses signed cancellation at `x=1/n` |
| Coefficient variation bound | Stronger structured target; implies pointwise control |
| Direct bound from fixed-pair `Q` estimates only | Blocked without aggregate signed control |
| Direct numerator-only bound with uncontrolled denominator | Blocked outside the paper denominator range |
| Schreier or independent-permutation transfer | Not a surface proof |

![dependency graph separating direct evaluation, coefficient variation, denominator control, and stronger Lemma 3.3 inputs](reports/figures/m36_direct_vs_cv_dependency_graph.png)

The M36 audit decision was `VALIDATED`. The auditor found no critical or moderate defects and confirmed that the generated tables recover the M35 baseline with `A=2 kappa`, `sigma=0`, `D=0`, and `Lambda0_power=20`.

## Finding 3: M37 Classified Signed Pointwise Cancellation

M37 tested whether the M36 direct small-`x` route remains independent. The answer was yes, but only in a narrow theorem form: a new surface-attached signed cancellation estimate must act on the actual evaluated ratio at `x=1/n`.

The signed aggregate was summarized as

```text
p(x) = sum_{gamma1,gamma2,k1,k2}
       w(gamma1,k1) w(gamma2,k2)
       Q_{gamma1^k1,gamma2^k2}(x),
```

where

```text
w(gamma,k)
  = ell_gamma / (2 sinh(k ell_gamma/2))
    * (h o f_Lambda0)^vee(k ell_gamma).
```

The length denominator is positive. Signs can enter through the transform values and through the evaluated quotient polynomial. Therefore the cancellation target must control the weighted signed sum after evaluation at `x=1/n` and after division by `Q_id(1/n)`.

M37 named the falsifiable target:

```text
SPC(A,sigma):
|p(1/n) / Q_id(1/n)|
  <= C n Lambda0^20 ||htilde||^2 q^A n^(-sigma+o(1)).
```

The generated mechanism table classified the following rows as `surface_theorem_target`:

| Mechanism | Reason it remains a target |
|---|---|
| Surface signed pointwise grouping | Could save at the evaluated value without bounding every coefficient |
| Diagonal/off-diagonal signed balance | Could be independent if actual surface strata cancel at `x=1/n` |
| Transform phase oscillation | Could use signs from the transform together with quotient evaluations |

It classified fixed-stratum absolute control and coefficient sign-variation control as `coefficient_variation_equivalent`. Such approaches may still be useful, but they are no longer the narrower direct route.

It classified cancellation at `x=0`, off-range reciprocal cancellation, and near-zero denominator scenarios as blocked. Schreier and independent-permutation pairings remained `toy_only`.

![classification counts for signed cancellation mechanisms](reports/figures/m37_signed_mechanism_map.png)

The stratum and denominator grids preserve the same saving formula:

```text
beta = (2 kappa - A) eta + sigma - D.
```

They show that denominator loss subtracts directly from signed numerator savings and that the paper-safe denominator range is essential.

![candidate beta by stratum at kappa=5 and eta=0.08](reports/figures/m37_stratum_cancellation_budget.png)

![boundary between direct pointwise and coefficient-variation-equivalent targets](reports/figures/m37_direct_vs_cv_cancellation_boundary.png)

The M37 audit decision was `VALIDATED`. The auditor confirmed that the Markov baseline rows have `A_offset=0`, `sigma=0`, `D=0`, and `Lambda0_power=20`, and that the classifications include all required categories.

## Discussion

Cycles 46-48 did not advance the Kim--Tao exponent. They made the remaining compact-support problem sharper.

Before these cycles, the open route could be described broadly as "improve the Corollary 3.4 numerator control." After M35-M37, the alternatives are clearer:

1. Prove a surface-attached signed pointwise theorem for the actual normalized value `p(1/n)/Q_id(1/n)`.
2. Prove a coefficient or signed-variation theorem for the surface quotient-polynomial family.
3. Abandon the direct compact-support numerator route if every attempted direct proof requires absolute fixed-stratum control or leaves the paper-safe range.

The most important boundary is the distinction between a direct pointwise theorem and coefficient variation. A direct theorem only controls the evaluated value at `x=1/n`. It remains independent if cancellation is visible only after summing the actual weighted surface aggregate. A coefficient-variation theorem controls a structured expansion and is stronger in form, but it may be the route that the mathematics actually demands.

The cycles also preserved the no-transfer firewall. The M30-M33 Schreier theorem package remains a useful finite-model benchmark, but it does not prove anything about the Kim--Tao Corollary 3.4 numerator. The surface problem includes the surface relation, MPvH/Witten-zeta normalization, Nau boundedness, Selberg weights, the denominator `Q_id`, and a growing folded quotient-family sum.

## Open Questions

The next research step should formulate the actual surface-attached grouping problem for `p(1/n)/Q_id(1/n)` more concretely. The M37 audit suggested grouping by paper-native invariants such as quotient complex, primitive-power structure, length shell, or surface-relation kernel constraint.

The main open theorem target is:

```text
|p(1/n) / Q_id(1/n)|
  <= C n Lambda0^20 ||htilde||^2 q^A n^(-sigma+o(1))
```

with enough saving that

```text
beta = (2 kappa - A) eta + sigma - D
```

is positive in the relevant budget.

Open questions left by these cycles are:

- Is there a natural signed grouping of the actual Corollary 3.4 summands at `x=1/n`?
- Do diagonal/off-diagonal surface strata cancel after Selberg weights and denominator normalization?
- Can transform-phase oscillation interact with quotient evaluations in a surface-specific way?
- Does every plausible proof require absolute fixed-stratum control, making coefficient variation the real target?
- Can denominator control remain paper-safe for any strengthened numerator theorem?
- Is there an obstruction showing that the direct signed pointwise route is equivalent to coefficient variation?

No cycle 46-48 artifact claims a variance law, limiting distribution, level repulsion, local universality, shrinking-window theorem, or improved Kim--Tao rigidity exponent.

## References

No `REFERENCES.md` file was present in the workspace during this report pass. The following local sources were used for traceability.

- Kim--Tao paper files: `2603.01127.pdf`, `2603.01127.txt`.
- Cycle 46 sessions: researcher `7ae38a1a-b742-4253-99bb-ed3b1ff7755f`, worker `33ac8ff8-977c-4180-9ef3-2f77173a8197`, auditor `4baeea93-c036-4ec9-82cc-167d838db7c2`.
- Cycle 47 sessions: researcher `f180b82d-c061-45a2-8b68-aa4d8da0d390`, worker `7c3494e6-3608-409f-b944-df7bd4412d84`, auditor `83f0fe80-ebc4-43a0-a490-6a15f4255e59`.
- Cycle 48 sessions: researcher `7538f575-5120-4470-9497-06322e16514f`, worker `3cd70352-0f82-4ea2-bafd-33eb39616ff1`, auditor `56cd9686-f4b4-40ec-a9ee-5eeaf1ffc9bd`.
- Proof ledgers: `docs/proof_ledger/surface_corollary34_numerator_obstruction.md`, `docs/proof_ledger/direct_small_x_surface_numerator_target.md`, `docs/proof_ledger/signed_pointwise_cancellation_surface_aggregate.md`.
- Extension reports: `reports/extension_candidates/m35_surface_corollary34_numerator_obstruction.md`, `reports/extension_candidates/m36_direct_small_x_surface_numerator_target.md`, `reports/extension_candidates/m37_signed_pointwise_cancellation_surface_aggregate.md`.
- Generated data: all `m35_*`, `m36_*`, and `m37_*` CSV files under `data/extension_candidates/`.
- Figures: all `m35_*`, `m36_*`, and `m37_*` PNG files under `reports/figures/`.
- Audit input supplied for Cycle 48 / M37 validation.

## Appendix: Implementation Details

### Code Organization

Cycle 46 / M35 added:

- `scripts/analyze_surface_corollary34_numerator_obstruction.py` (400 lines)
- `tests/test_surface_corollary34_numerator_obstruction.py` (109 lines)
- `docs/proof_ledger/surface_corollary34_numerator_obstruction.md` (183 lines)
- `reports/extension_candidates/m35_surface_corollary34_numerator_obstruction.md` (133 lines)

Cycle 47 / M36 added:

- `scripts/analyze_direct_small_x_surface_numerator_target.py` (445 lines)
- `tests/test_direct_small_x_surface_numerator_target.py` (129 lines)
- `docs/proof_ledger/direct_small_x_surface_numerator_target.md` (123 lines)
- `reports/extension_candidates/m36_direct_small_x_surface_numerator_target.md` (81 lines)

Cycle 48 / M37 added:

- `scripts/analyze_signed_pointwise_cancellation_surface_aggregate.py` (503 lines)
- `tests/test_signed_pointwise_cancellation_surface_aggregate.py` (151 lines)
- `docs/proof_ledger/signed_pointwise_cancellation_surface_aggregate.md` (96 lines)
- `reports/extension_candidates/m37_signed_pointwise_cancellation_surface_aggregate.md` (65 lines)

### Generated Data

M35 generated:

| File | Rows excluding header |
|---|---:|
| `data/extension_candidates/m35_interpolation_loss_budget.csv` | 90 |
| `data/extension_candidates/m35_candidate_mechanism_classification.csv` | 13 |
| `data/extension_candidates/m35_surface_input_gap_matrix.csv` | 6 |
| `data/extension_candidates/m35_direct_vs_markov_regime_grid.csv` | 100 |

M36 generated:

| File | Rows excluding header |
|---|---:|
| `data/extension_candidates/m36_direct_small_x_budget.csv` | 120 |
| `data/extension_candidates/m36_denominator_obstruction_grid.csv` | 400 |
| `data/extension_candidates/m36_mechanism_classification.csv` | 16 |
| `data/extension_candidates/m36_direct_vs_cv_implication_table.csv` | 5 |

M37 generated:

| File | Rows excluding header |
|---|---:|
| `data/extension_candidates/m37_signed_mechanism_classification.csv` | 18 |
| `data/extension_candidates/m37_stratum_cancellation_grid.csv` | 435 |
| `data/extension_candidates/m37_denominator_signed_saving_grid.csv` | 125 |
| `data/extension_candidates/m37_theorem_target_table.csv` | 5 |

### Figure Inventory

| Figure | Dimensions |
|---|---|
| `reports/figures/m35_corollary34_interpolation_loss.png` | 1360 x 736 |
| `reports/figures/m35_mechanism_dependency_graph.png` | 1472 x 800 |
| `reports/figures/m35_direct_vs_coefficient_variation_map.png` | 1680 x 608 |
| `reports/figures/m36_direct_small_x_budget_map.png` | 1620 x 990 |
| `reports/figures/m36_denominator_obstruction_map.png` | 1350 x 936 |
| `reports/figures/m36_direct_vs_cv_dependency_graph.png` | 1800 x 1044 |
| `reports/figures/m37_signed_mechanism_map.png` | 1530 x 864 |
| `reports/figures/m37_stratum_cancellation_budget.png` | 1620 x 864 |
| `reports/figures/m37_direct_vs_cv_cancellation_boundary.png` | 1530 x 864 |

### Validation Results

M35 validation:

- `py_compile`: passed.
- `python3 scripts/analyze_surface_corollary34_numerator_obstruction.py`: passed.
- `python3 tests/test_surface_corollary34_numerator_obstruction.py`: passed.
- Figure checks: passed.
- `promise_check`: passed with historical warnings only; post-audit count `events: 138, plan milestones: 35`.
- `org_check`: passed with historical warnings only.
- Auditor repair: corrected `Lambda0^2` to `Lambda0^20` in the proof ledger and added regression coverage.

M36 validation:

- `py_compile`: passed.
- `python3 scripts/analyze_direct_small_x_surface_numerator_target.py`: passed.
- `python3 tests/test_direct_small_x_surface_numerator_target.py`: passed.
- Figure and report-link checks: passed.
- `promise_check`: passed with historical warnings only; `events: 141, plan milestones: 36`.
- `org_check`: passed with historical warnings only.
- Auditor repair: none.

M37 validation:

- `py_compile`: passed.
- `python3 scripts/analyze_signed_pointwise_cancellation_surface_aggregate.py`: passed.
- `python3 tests/test_signed_pointwise_cancellation_surface_aggregate.py`: passed.
- Figure and report-link checks: passed.
- Targeted CSV checks: passed.
- `promise_check`: passed with historical warnings only; `events: 144, plan milestones: 37`.
- `org_check`: passed with historical warnings only.
- Auditor repair: none.

During reporting, `MANIFEST.md` was updated to the cycles 46-48 snapshot. The post-update checks passed:

```text
python3 -m long_exposure.tools.promise_check .
python3 -m long_exposure.tools.org_check .
```

Both emitted only historical warnings: old noncanonical `docs/paper_map/` ledger path, old orphan cycle reports, root paper/live-run files, and old figures under `docs/`.

### Workspace Snapshot

After the manifest update:

- Python scripts: 46 files, 14,049 lines.
- Python tests: 38 files, 3,303 lines.
- Canonical CSV datasets: 106 files under `data/`.
- PNG figures: 92 files under `reports/figures/`.
- Documentation/report artifacts: 211 Markdown/DOT/PNG files under `docs/`, `reports/`, and `audits/`.
- Promise ledger events: 144.
- Plan milestones: 37.
- `MANIFEST.md`: 241 lines.

### Cross-Reference Map

| Earlier source | Cycle 46-48 use |
|---|---|
| M15/M22/M25 compact-support obstruction | M35 returned to the actual Corollary 3.4 numerator instead of toy aggregate proxies. |
| M35 numerator obstruction | M36 isolated direct control of `p(1/n)/Q_id(1/n)` as a conditional theorem target. |
| M36 direct small-`x` target | M37 tested whether the direct route remains independent through signed cancellation. |
| M30-M33 Schreier benchmark package | Used only as a no-transfer firewall; it provides no Kim--Tao surface numerator theorem. |
| M34 fixed non-shrinking spectral statistics | Remains a separate macroscopic count corollary and does not support local-statistics claims. |
