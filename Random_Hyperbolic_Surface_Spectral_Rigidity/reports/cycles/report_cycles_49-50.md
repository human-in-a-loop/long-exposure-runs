---
title: "Random Hyperbolic Surface Spectral Rigidity — cycles 49-50"
date: "2026-05-16"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# Random Hyperbolic Surface Spectral Rigidity — cycles 49-50

## Abstract

Cycles 49-50 continued the compact-support trace-side branch of the Kim--Tao random-cover spectral-rigidity campaign. The branch is focused on the denominator-normalized Corollary 3.4 ratio

```text
p(1/n) / Q_id(1/n),
```

where earlier cycles had localized the current `q^(2 kappa)` loss to Markov interpolation of `x^2 p(x)` and had isolated direct small-`x` control as the only route distinct from coefficient variation.

Cycle 49, milestone M38, turned the generic signed pointwise cancellation idea into a concrete surface-native grouping problem. It classified possible groupings of actual Corollary 3.4 summands by quotient-complex profile, surface-relation kernel, diagonal/off-diagonal structure, primitive-power profile, length-shell transform phase, and several blocked or toy-only controls. Two direct theorem templates survived as conditional targets: surface-relation kernel grouping and length-shell transform-phase grouping. No cancellation theorem or exponent improvement was proved.

Cycle 50, milestone M39, tested the strongest surviving M38 target: surface-relation kernel grouping. The result was negative for theorem readiness. Lemma 3.3's kernel-closure condition is paper-native, but the validated record says it currently functions as an admissibility condition for folded quotient targets rather than as an evaluated sign-pairing mechanism for `Q_i(1/n)`. The direct kernel signed pointwise cancellation branch is therefore not currently theorem-ready. The next recommended target is coefficient/signed variation for the actual surface numerator.

## Introduction

The long-exposure campaign studies Kim and Tao's paper *Eigenvalue rigidity of hyperbolic surfaces in the random cover model* using local copies `2603.01127.pdf` and `2603.01127.txt`. The broader aim is to reconstruct the proof architecture, expose bottlenecks, and develop credible extensions.

The immediate context for cycles 49-50 comes from milestones M35-M37:

- M35 localized the existing `q^(2 kappa)` loss to Markov interpolation applied to `P(x)=x^2 p(x)`, after reciprocal-integer control of the Corollary 3.4 numerator.
- M36 isolated the direct small-`x` theorem target for the evaluated ratio `p(1/n)/Q_id(1/n)`.
- M37 showed that direct small-`x` control is independent of coefficient variation only if it proves signed pointwise cancellation at the actual evaluation point `x=1/n`.

Cycles 49-50 asked whether that signed pointwise route can be made precise using paper-native structure. Here, "paper-native" means structure visible in Kim--Tao Lemma 3.3 and Corollary 3.4, not imported from Schreier or independent-permutation toy models.

## Approach

The two cycles followed a narrowing sequence.

Cycle 49/M38 first enumerated candidate groupings of the normalized summand

```text
w(gamma1,k1) w(gamma2,k2)
Q_{gamma1^k1,gamma2^k2}(1/n) / Q_id(1/n).
```

The Selberg length denominator in `w(gamma,k)` is positive, so signs can only come from transform values and evaluated quotient-polynomial values. Denominator normalization is safe only in the paper range. If the denominator contributes a modeled loss

```text
|Q_id(1/n)|^(-1) <= n^D,
```

then every projected saving loses `D`.

M38 used the common exponent bookkeeping

```text
beta = (2 kappa - A) eta + sigma - D.
```

A direct signed pointwise theorem template was written as

```text
SPC_G(A,sigma):
|sum_{i in G} w_i Q_i(1/n) / Q_id(1/n)|
  <= C n Lambda0^20 ||htilde||^2 q^A n^(-sigma+o(1)).
```

Cycle 50/M39 then selected the strongest M38 survivor, surface-relation kernel grouping, and checked whether Lemma 3.3's kernel-closure condition actually supplies signed cancellation at `x=1/n`.

## Source Inventory and Timeline

The report uses the following source sessions and artifacts.

| Cycle | Session ID | Role | Main content |
|---|---|---|---|
| 49 | `4960a7ed-35a7-4504-bebc-0f807efc7b93` | researcher | Opened M38 and specified the surface-native grouping problem for the evaluated Corollary 3.4 aggregate. |
| 49 | `d0839d20-a538-4403-9f10-4efa6bb72137` | worker | Built M38 proof ledger, report, classifier script, tests, four CSVs, and three figures. |
| 49 | `bfc17ad1-8ea0-430d-b4a7-15bb06bdc1b7` | auditor | Validated M38 with no critical or moderate findings. |
| 50 | `3b09f8bd-0edb-4255-98df-38e5bebc7867` | researcher | Opened M39 to test surface-relation kernel closure as a signed pointwise cancellation mechanism. |
| 50 | `4dc8f1a3-89f1-479e-8f6c-506bde8aed53` | worker | Built M39 proof ledger, report, classifier script, tests, four CSVs, and three figures. |
| 50 | `01d4f196-4451-40c4-b2b3-d73405c6b57e` | auditor | Validated M39 with no critical or moderate findings. |

No `REFERENCES.md` file was present in the workspace. The references section therefore lists local paper files, session IDs, reports, proof ledgers, data artifacts, figures, and the supplied audit report rather than continuing a global numbered bibliography.

## Finding 1: M38 Formulated the Surface-Native Grouping Problem

M38 converted the remaining direct small-`x` route into a concrete grouping taxonomy for actual Corollary 3.4 summands. The work is recorded in session `4960a7ed-35a7-4504-bebc-0f807efc7b93`, worker session `d0839d20-a538-4403-9f10-4efa6bb72137`, and audit session `bfc17ad1-8ea0-430d-b4a7-15bb06bdc1b7`.

The M38 classifier generated:

- `data/extension_candidates/m38_grouping_invariant_classification.csv`: 12 classification rows.
- `data/extension_candidates/m38_grouping_beta_budget.csv`: 720 beta-budget rows.
- `data/extension_candidates/m38_grouping_dependency_matrix.csv`: 84 dependency rows.
- `data/extension_candidates/m38_candidate_spc_theorem_templates.csv`: five theorem-template rows.

The validated classifications were:

| Grouping route | M38 classification | Meaning |
|---|---|---|
| Markov baseline | `paper_proved_baseline` | Existing Kim--Tao route, included to anchor `Lambda0^20` and zero direct saving. |
| Surface-relation kernel grouping | `surface_theorem_target` | A paper-native, pointwise grouping target requiring a new structural cancellation theorem. |
| Length-shell transform phase | `surface_theorem_target` | A pointwise target using transform signs from the Selberg-weighted summand. |
| Quotient-complex profile | `underdetermined_surface_input` | Visible in the paper object, but no current theorem supplies profile-level cancellation. |
| Diagonal/off-diagonal relation balance | `underdetermined_surface_input` | Visible in the aggregate, but requires an actual surface input. |
| Primitive-power profile | `underdetermined_surface_input` | Native to the Selberg sum, but cancellation remains unproved. |
| Absolute fixed-stratum controls | `coefficient_variation_equivalent` | Any proof by absolute mass or total variation is no longer direct pointwise cancellation. |
| `x=0`, off-range, near-zero denominator, Schreier analogy | blocked or toy-only | These do not control the paper-safe evaluated ratio. |

![classification of candidate paper-native grouping invariants by theorem readiness and obstruction type](reports/figures/m38_surface_grouping_invariant_map.png)

![signed-saving beta budget under denominator-safe and denominator-loss scenarios](reports/figures/m38_grouping_beta_budget.png)

![boundary between genuine pointwise grouping and coefficient-variation-equivalent control](reports/figures/m38_grouping_vs_coefficient_variation_boundary.png)

The M38 decision was:

```text
decision=surface_relation_and_transform_phase_groupings_survive_only_as_new_SPC_G_targets
pivot_rule=pivot_to_coefficient_signed_variation_if_absolute_fixed_stratum_control_is_required
```

The audit validated the result. It specifically checked that the theorem-ready rows were exactly `surface_relation_kernel_grouping` and `length_shell_transform_phase`, both with `D=0`, and that tests preserved the M35-M37 safeguards: `Lambda0_power=20`, denominator loss subtraction, wrong-point blocking at `x=0`, no Schreier transfer, and coefficient-variation equivalence for absolute-control rows.

## Finding 2: M39 Found Kernel SPC Not Currently Theorem-Ready

M39 tested the strongest M38 survivor: surface-relation kernel grouping. The work is recorded in session `3b09f8bd-0edb-4255-98df-38e5bebc7867`, worker session `4dc8f1a3-89f1-479e-8f6c-506bde8aed53`, and audit session `01d4f196-4451-40c4-b2b3-d73405c6b57e`.

The relevant paper structure is Kim--Tao Lemma 3.3's folded quotient setup. In the M39 reconstruction, the condition is:

```text
every path in W_r spelling an element of ker(F_{2g} -> Gamma) is closed.
```

That condition attaches to folded quotient targets `W_r`. The validated account places it before the embedding expectations `E_emb_n(W_r)`, polynomial contributions, and the evaluated quotient ratio

```text
Q_{gamma1,gamma2}(1/n) / Q_id(1/n).
```

The M39 classifier generated:

- `data/extension_candidates/m39_kernel_constraint_schema.csv`: five kernel-closure flow rows.
- `data/extension_candidates/m39_kernel_spc_classification.csv`: ten mechanism classification rows.
- `data/extension_candidates/m39_kernel_beta_budget.csv`: 600 beta-budget rows.
- `data/extension_candidates/m39_kernel_pivot_decision.csv`: three pivot decision rows.

The validated decision was:

```text
decision=kernel_spc_not_currently_theorem_ready
pivot_rule=pivot_to_coefficient_signed_variation_if_absolute_kernel_stratum_control_is_required
```

The classification counts accepted by the audit were:

| Classification | Count |
|---|---:|
| `paper_proved_baseline` | 1 |
| `surface_theorem_target` | 2 |
| `underdetermined_surface_input` | 3 |
| `coefficient_variation_equivalent` | 1 |
| `range_blocked` | 1 |
| `denominator_blocked` | 1 |
| `toy_only` | 1 |

The two `surface_theorem_target` rows remain conditional templates only:

- `kernel_class_signed_pairing`
- `quotient_polynomial_sign_grouping`

They would be genuine direct signed pointwise results if a new theorem proved cancellation of evaluated `Q_i(1/n)` values across relation-kernel classes. M39 did not find such a theorem in the current Lemma 3.3 input.

![how Lemma 3.3 kernel closure feeds from folded quotients to `Q_{gamma1,gamma2}(1/n)`](reports/figures/m39_kernel_constraint_flow.png)

![classification of relation-kernel grouping mechanisms by theorem readiness and obstruction](reports/figures/m39_kernel_spc_decision_map.png)

![beta budget for candidate `SPC_kernel(A,sigma)` rows under safe and lossy denominator regimes](reports/figures/m39_kernel_beta_budget.png)

The audit rationale was that kernel closure is genuinely paper-native, but currently acts as admissibility and structure. It does not expose a sign-pairing or orthogonality mechanism for evaluated values at `x=1/n`.

## Discussion

Cycles 49-50 narrowed the direct signed pointwise cancellation branch to a fork and then resolved the stronger side of that fork.

M38 showed that direct signed pointwise cancellation is still logically possible only through a theorem of the form `SPC_G(A,sigma)` for a paper-native grouping evaluated at `x=1/n`. The two strongest groupings were surface-relation kernel classes and length-shell transform-phase classes.

M39 then tested surface-relation kernel classes and found that the current paper input is not enough. Lemma 3.3's kernel closure controls which folded quotient targets are admissible. It does not by itself produce opposite signs, orthogonality, or evaluated cancellation among the `Q_i(1/n)` terms.

This changes the research posture. The direct pointwise branch should not continue by repeatedly relabeling admissibility or smaller quotient-family size as cancellation. If the next proof requires bounds of the form

```text
sum_i |w_i Q_i(1/n)|
```

or total variation inside fixed quotient, length, primitive-power, or relation-kernel strata, then the target is coefficient/signed variation, not direct signed pointwise cancellation.

The length-shell transform-phase branch remains secondary. M39 clarified that transform signs are not relation-kernel signs; they should be pursued only after the coefficient/signed-variation route is triaged.

## Open Questions

The main open target after cycles 49-50 is:

```text
surface_numerator_coefficient_signed_variation_first_attack
```

That target should formulate coefficient/signed variation for the actual Corollary 3.4 numerator at `x=1/n`, including both denominator-safe and denominator-loss regimes.

Open technical questions are:

- Can one state a useful coefficient/signed-variation theorem for the actual denominator-normalized surface numerator without claiming direct pointwise cancellation?
- Which strata should be used first: fixed `d=C-V`, quotient-complex profile, primitive-power type, length shell, or relation-kernel class?
- How does the denominator-loss term `D` enter the coefficient/signed-variation version of the beta budget?
- Does length-shell transform phase provide useful secondary structure after coefficient/signed variation is formulated?
- Is there any new Lemma 3.3-level input that could turn relation-kernel admissibility into evaluated `Q_i(1/n)` sign cancellation? No such input was found in M39.

## References

No global `REFERENCES.md` file was present. This report cites the local source record for cycles 49-50:

- Local paper files: `2603.01127.pdf`, `2603.01127.txt`.
- Cycle 49 sessions: researcher `4960a7ed-35a7-4504-bebc-0f807efc7b93`, worker `d0839d20-a538-4403-9f10-4efa6bb72137`, auditor `bfc17ad1-8ea0-430d-b4a7-15bb06bdc1b7`.
- Cycle 50 sessions: researcher `3b09f8bd-0edb-4255-98df-38e5bebc7867`, worker `4dc8f1a3-89f1-479e-8f6c-506bde8aed53`, auditor `01d4f196-4451-40c4-b2b3-d73405c6b57e`.
- M38 proof ledger and report: `docs/proof_ledger/surface_native_grouping_problem.md`, `reports/extension_candidates/m38_surface_native_grouping_problem.md`.
- M39 proof ledger and report: `docs/proof_ledger/surface_relation_kernel_spc_probe.md`, `reports/extension_candidates/m39_surface_relation_kernel_spc_probe.md`.
- M38 data and figures: `data/extension_candidates/m38_*.csv`, `reports/figures/m38_*.png`.
- M39 data and figures: `data/extension_candidates/m39_*.csv`, `reports/figures/m39_*.png`.
- Supplied cycle audit report for cycles 49-50.

## Appendix: Implementation Details

### Code Organization

Cycle 49/M38 added or updated:

| File | Lines | Purpose |
|---|---:|---|
| `scripts/analyze_surface_native_grouping_problem.py` | 562 | Generates M38 grouping classifications, beta budgets, dependencies, theorem templates, and figures. |
| `tests/test_surface_native_grouping_problem.py` | 152 | Validates M38 taxonomy, `Lambda0^20`, denominator beta loss, no-transfer guards, and pivot rules. |
| `docs/proof_ledger/surface_native_grouping_problem.md` | 103 | Proof-ledger formulation of candidate grouping invariants. |
| `reports/extension_candidates/m38_surface_native_grouping_problem.md` | 68 | M38 decision report and figure narrative. |

Cycle 50/M39 added or updated:

| File | Lines | Purpose |
|---|---:|---|
| `scripts/analyze_surface_relation_kernel_spc_probe.py` | 678 | Generates M39 kernel-closure schema, classifications, beta budgets, pivot decisions, and figures. |
| `tests/test_surface_relation_kernel_spc_probe.py` | 149 | Validates M39 kernel reconstruction, taxonomy, beta formula, and pivot guards. |
| `docs/proof_ledger/surface_relation_kernel_spc_probe.md` | 75 | Proof-ledger reconstruction of Lemma 3.3 kernel closure. |
| `reports/extension_candidates/m39_surface_relation_kernel_spc_probe.md` | 44 | M39 decision report and figure narrative. |

### Generated Data

M38 data products:

| File | Rows excluding header |
|---|---:|
| `data/extension_candidates/m38_grouping_invariant_classification.csv` | 12 |
| `data/extension_candidates/m38_grouping_beta_budget.csv` | 720 |
| `data/extension_candidates/m38_grouping_dependency_matrix.csv` | 84 |
| `data/extension_candidates/m38_candidate_spc_theorem_templates.csv` | 5 |

M39 data products:

| File | Rows excluding header |
|---|---:|
| `data/extension_candidates/m39_kernel_constraint_schema.csv` | 5 |
| `data/extension_candidates/m39_kernel_spc_classification.csv` | 10 |
| `data/extension_candidates/m39_kernel_beta_budget.csv` | 600 |
| `data/extension_candidates/m39_kernel_pivot_decision.csv` | 3 |

### Figure Inventory

M38 figures:

| Figure | Dimensions |
|---|---|
| `reports/figures/m38_surface_grouping_invariant_map.png` | 1620 x 864 |
| `reports/figures/m38_grouping_beta_budget.png` | 1710 x 936 |
| `reports/figures/m38_grouping_vs_coefficient_variation_boundary.png` | 1584 x 864 |

M39 figures:

| Figure | Dimensions |
|---|---|
| `reports/figures/m39_kernel_constraint_flow.png` | 1800 x 900 |
| `reports/figures/m39_kernel_spc_decision_map.png` | 1800 x 864 |
| `reports/figures/m39_kernel_beta_budget.png` | 1710 x 864 |

### Validation Results

M38 audit validation:

```text
python3 -m py_compile scripts/analyze_surface_native_grouping_problem.py tests/test_surface_native_grouping_problem.py
python3 scripts/analyze_surface_native_grouping_problem.py
python3 tests/test_surface_native_grouping_problem.py
```

All passed. The M38 audit also checked CSV invariants, figure existence and nonblank status, report links, `promise_check`, and `org_check`.

M39 audit validation:

```text
python3 -m py_compile scripts/analyze_surface_relation_kernel_spc_probe.py tests/test_surface_relation_kernel_spc_probe.py
python3 scripts/analyze_surface_relation_kernel_spc_probe.py
python3 tests/test_surface_relation_kernel_spc_probe.py
```

All passed. Targeted CSV checks verified ten classification rows, 600 beta rows, three pivot rows, and the beta formula on every row.

Post-manifest checks run during report preparation:

```text
python3 -m long_exposure.tools.promise_check .
```

Result:

```text
events: 150, plan milestones: 39
```

Only historical warnings remained: old noncanonical `docs/paper_map/` ledger path and orphan prior periodic reports under `reports/cycles/`.

```text
python3 -m long_exposure.tools.org_check .
```

Result: passed with historical warnings only, including root paper/live-run files and old figures under `docs/`.

### Workspace Snapshot

`MANIFEST.md` was updated for cycles 49-50. The current snapshot records:

| Category | Count |
|---|---:|
| Python scripts | 48 files, 15,289 lines |
| Python tests | 40 files, 3,604 lines |
| Canonical CSV datasets | 114 files under `data/` |
| PNG figures | 98 files under `reports/figures/` |
| Documentation/report artifacts | 222 Markdown/DOT/PNG files under `docs/`, `reports/`, and `audits/` |
| Promise ledger events | 150 |
| Plan milestones | 39 |

### Cross-Reference Map

| Origin | Consuming result |
|---|---|
| M35 numerator obstruction | M36 direct target for `p(1/n)/Q_id(1/n)`. |
| M36 direct target | M37 signed pointwise cancellation taxonomy. |
| M37 signed cancellation | M38 paper-native grouping taxonomy. |
| M38 surface-relation kernel grouping | M39 kernel SPC probe. |
| M39 kernel SPC decision | Next target: coefficient/signed variation for the actual surface numerator. |

### Residual Scope Boundaries

Cycles 49-50 do not prove an exponent improvement, local statistics theorem, variance law, shrinking-window result, random-wave statement, or Schreier-to-surface transfer. They refine the bottleneck map. The validated output is a decision: direct relation-kernel signed pointwise cancellation is not currently theorem-ready, and the next surface-facing attack should be coefficient/signed variation for the actual Corollary 3.4 numerator.
