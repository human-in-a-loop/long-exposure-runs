# MANIFEST

## Key Files

The following workspace files produced results cited in
final_report.md. Downstream packaging should include
these; other files are supporting or exploratory.

- `scripts/rr/finite_rr_experiments.wls` — finite coefficient agreement and negative-control diagnostics cited in "Foundational Results and Diagnostics" and "Validation and Artifact Trail."
- `scripts/rr/q_difference_probe.wls` — q-difference ladder residual and backsolve diagnostics cited in "Foundational Results and Diagnostics" and "Validation and Artifact Trail."
- `scripts/rr/product_transform_probe.wls` — finite transformed recurrence, finite Jacobi residual, and Gaussian-window failure diagnostics cited in "Foundational Results and Diagnostics" and "Validation and Artifact Trail."
- `scripts/rr/transformed_cancellation_probe.wls` — signed-object expansion and rejected local cancellation diagnostics cited in "Routes Explored Before the Transfer Mechanism" and "Validation and Artifact Trail."
- `scripts/rr/nonlocal_involution_probe.wls` — nonlocal transfer obstruction diagnostics cited in "Routes Explored Before the Transfer Mechanism" and "Validation and Artifact Trail."
- `scripts/rr/mod5_state_recurrence_probe.py` — shifted-state and modulo-5 non-closure diagnostics cited in "Routes Explored Before the Transfer Mechanism" and "Validation and Artifact Trail."
- `scripts/rr/euler_tail_telescoping_probe.wls` — Euler-tail expansion and low-order certificate diagnostics cited in "Routes Explored Before the Transfer Mechanism" and "Validation and Artifact Trail."
- `scripts/rr/direct_bijection_probe.py` — finite gap/residue enumeration and beta/abacus diagnostics cited in "Routes Explored Before the Transfer Mechanism" and "Validation and Artifact Trail."
- `scripts/rr/bailey_matrix_probe.wls` — triangular transform, explicit-pair, and limiting inner-sum checks cited in "The Bailey-Style Triangular Transfer" and "Validation and Artifact Trail."
- `scripts/rr/product_side_formal_check.wls` — transformed, Jacobi, and final reciprocal-product residual checks cited in "Product-Side Closure" and "Validation and Artifact Trail."

## Script Inventory

### scripts/rr

| file | lines | purpose |
|---|---:|---|
| `bailey_matrix_probe.wls` | 142 | Checks the derived triangular matrix transform, alpha solves, pair residuals, and limiting inner-sum residuals. |
| `euler_tail_telescoping_probe.wls` | 155 | Searches exact low-order Euler-tail divergence certificates and records finite truncation consistency. |
| `finite_gap_probe.wls` | 71 | Tests largest-part gap-two recurrences and naive bounded residue-product comparisons. |
| `finite_rr_experiments.wls` | 106 | Generates truncated Rogers-Ramanujan series/product coefficients, differences, recurrence probes, and negative controls. |
| `mod5_state_recurrence_probe.wls` | 167 | Wolfram probe for shifted diagonal and modulo-5 state recurrence diagnostics. |
| `nonlocal_involution_probe.wls` | 172 | Enumerates nonlocal subset-transfer candidates and classifies involution failures. |
| `product_side_formal_check.wls` | 99 | Checks transformed, Jacobi, and final reciprocal residue-product residuals for the formal product-side closure. |
| `product_transform_probe.wls` | 190 | Tests Euler-multiplied finite series, finite Jacobi identities, candidate transformed finite formulas, and negative controls. |
| `q_difference_probe.wls` | 123 | Checks the series-side q-difference ladder residuals and product/backsolve diagnostics. |
| `transformed_cancellation_probe.wls` | 180 | Enumerates signed transformed-series objects and tests local absorb/release cancellation. |
| `direct_bijection_probe.py` | 409 | Enumerates finite gap-two and residue partitions, tests beta/abacus signatures, and renders abacus diagnostics. |
| `mod5_state_recurrence_probe.py` | 234 | Python mirror for recurrence-only modulo-5 diagnostics and stable coefficient tables. |
| `plot_bailey_transform_residuals.py` | 49 | Renders residual checks for the Bailey-style triangular transform. |
| `plot_euler_tail_lattice_residuals.py` | 80 | Renders Euler-tail lattice support and finite residual diagnostics. |
| `plot_mod5_state_support.py` | 71 | Renders stable coefficient support by residue class with pentagonal overlays. |
| `plot_nonlocal_involution_fixed_points.py` | 65 | Renders nonlocal fixed/unpaired object patterns against predicted pentagonal exponents. |
| `plot_product_transform_residuals.py` | 82 | Renders first-failure-degree residual plot for product-transform candidates. |
| `plot_q_difference_residuals.py` | 72 | Renders residual magnitude plot for q-difference ladder and backsolve comparisons. |
| `plot_rr_difference_heatmap.py` | 50 | Renders heatmap of coefficient differences for target and negative-control finite products. |
| `plot_transformed_cancellation_survivors.py` | 54 | Renders transformed signed-survivor pattern and boundary corrections. |

## Cumulative Stats

| category | count | lines |
|---|---:|---:|
| Wolfram scripts | 10 | 1405 |
| Python scripts | 10 | 1166 |
| Total scripts | 20 | 2571 |
| Proof/lemma/validation docs | 13 | 3036 |
| Experiment data and figures under `data/finite_experiments` | 82 | n/a |

Sub-topics represented: formal finite approximants, q-difference ladder, finite gap recurrence, Euler/Jacobi product transform, transformed signed-object cancellation, nonlocal transfer obstruction, modulo-5 shifted-state recurrence obstruction, Euler-tail telescoping obstruction, direct partition-bijection diagnostics, Bailey-style triangular matrix transfer, product-side formal cancellation, final proof synthesis, validation/plotting.

## Cross-References

| origin | consuming artifact | value or role |
|---|---|---|
| `scripts/rr/finite_rr_experiments.wls` | `docs/validation.md`, `data/finite_experiments/rr_difference_heatmap.png` | Target coefficient agreement through `KMax=40`; negative controls fail at degrees `3`, `3`, and `1`. |
| `docs/lemmas/lemma_catalogue.md` L0-L7 | `docs/proof/q_difference_mechanism.md`, `docs/proof/product_transform_route.md`, `docs/proof/direct_partition_bijection.md`, `docs/proof/final_proof.md` | Formal-power-series definitions, truncation transfer, staircase interpretations, and residue-product generation rules. |
| `scripts/rr/q_difference_probe.wls` | `docs/proof/q_difference_mechanism.md`, `docs/validation.md` | Series ladder residual max `0`; backsolve comparisons `C0-P14` and `C1-P23` agree through the checked degree. |
| `docs/proof/q_difference_mechanism.md` L8-L10 | `docs/proof/finite_gap_recurrence.md`, later M2 work | Proved ladder `A_r=A_{r+1}+q^(r+1)A_{r+2}` and tail-normalized uniqueness; product-side closure was left open. |
| `scripts/rr/product_transform_probe.wls` | `docs/proof/product_transform_route.md`, `docs/validation.md`, `data/finite_experiments/product_transform_residuals.png` | `H` recurrence residual max `0`; finite Jacobi residual max `0`; simple Gaussian-window finite identities fail at degree `1`. |
| `docs/proof/product_transform_route.md` L12-L16 | `docs/proof/bailey_matrix_transform.md`, `docs/proof/product_side.md`, `docs/proof/final_proof.md` | Euler complement reduction and Jacobi-type product identities feed the Bailey transfer and final modulo-5 product cancellation. |
| `scripts/rr/transformed_cancellation_probe.wls` | `docs/proof/transformed_series_collapse.md`, `data/finite_experiments/transformed_cancellation_survivors.png` | Proves signed-object expansion L17 and rejects local absorb/release rule L18 as non-total. |
| `scripts/rr/nonlocal_involution_probe.wls` | `docs/proof/nonlocal_transformed_involution.md`, `data/finite_experiments/nonlocal_involution_fixed_points.png` | Tests pure nonlocal subset transfer; singleton-tail and smallest-`r` obstructions reject L21-L23. |
| `scripts/rr/mod5_state_recurrence_probe.py` | `docs/proof/mod5_state_recurrence.md`, `data/finite_experiments/mod5_state_support.png` | Generates stable coefficients from L24/L25 and records fixed diagonal-window non-closure L26. |
| `scripts/rr/euler_tail_telescoping_probe.wls` | `docs/proof/euler_tail_telescoping.md`, `data/finite_experiments/euler_tail_lattice_residuals.png` | Proves Euler-tail expansion L27 and rejects the tested low-order divergence certificates L28; finite agreement L29 is diagnostic only. |
| `scripts/rr/direct_bijection_probe.py` | `docs/proof/direct_partition_bijection.md`, `data/finite_experiments/direct_bijection_abacus_examples.png` | Enumerates gap/residue sets L30 and rejects static beta/abacus signatures L31 and nearest-runner slides L32. |
| `scripts/rr/bailey_matrix_probe.wls` | `docs/proof/bailey_matrix_transform.md`, `data/finite_experiments/bailey_transform_residuals.png`, `docs/proof/final_proof.md` | Supports the proved triangular inversion L33, explicit pairs L34, limiting transform L35, and Bailey-matrix transfer L36 that validates M2. |
| `scripts/rr/product_side_formal_check.wls` | `docs/proof/product_side.md`, `docs/validation.md`, `docs/proof/final_proof.md` | Confirms transformed, Jacobi, and final product residuals at `KMax=40`, M4 `KMax=18`, and edge `KMax=0`; these are regression checks, not proof. |
| `docs/proof/product_side.md` L37-L40 | `docs/proof/final_proof.md`, `docs/lemmas/lemma_catalogue.md` | Formal product units, Euler modulo-5 factorization, and residue-class cancellations close M3. |
| `docs/proof/final_proof.md` L41-L42 | `promise_ledger.jsonl`, `docs/validation.md` | Final self-contained formal proof of both Rogers-Ramanujan identities; M4 auditor validation event `031480b5-4644-4668-b467-9dfcb1f3d0fd`. |
