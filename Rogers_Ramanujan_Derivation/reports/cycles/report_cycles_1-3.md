---
title: "Rogers-Ramanujan Derivation — cycles 1-3"
date: "2026-05-15"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# Rogers-Ramanujan Derivation — cycles 1-3

## Introduction

Cycles 1-3 established a validated foundation for a first-principles proof of the two Rogers-Ramanujan identities, but did not complete the proof. The completed work produced formal-power-series definitions, reproducible finite experiments, proved series-side q-difference structure, proved finite gap recurrences, and proved the product-side Euler/Jacobi transformation infrastructure.

The current proof bottleneck is precise: the run has not yet proved that the Euler-multiplied Rogers-Ramanujan series collapse to the derived bilateral Jacobi sums. The auditor validated this as partial M2 progress and kept milestone M2 `in-progress` (auditor session `532d9472-a3f9-4ebd-ab75-90e005dc2cdf`).

## Definitions and Notation

The work is carried out in the formal power series ring \(\mathbb{Z}[[q]]\). Equality means coefficientwise equality. The finite q-Pochhammer symbol is

\[
(q;q)_n=\prod_{k=1}^{n}(1-q^k),\qquad (q;q)_0=1.
\]

Cycle 1 introduced coefficient extraction \([q^k]A(q)\), congruence modulo \(q^{K+1}\), and coefficientwise stabilization: a sequence \(A_N(q)\) has a formal limit if each fixed coefficient eventually becomes constant. These definitions support all later finite-to-infinite passages (`docs/lemmas/lemma_catalogue.md`, worker session `8f4715a2-55b0-41e8-97b8-7a8ffd2c2709`).

The two target series were also given a partition interpretation. The summand \(q^{n^2}/(q;q)_n\) generates partitions into exactly \(n\) positive parts with adjacent gaps at least two, by subtracting the staircase \((2n-1,2n-3,\ldots,1)\). The summand \(q^{n^2+n}/(q;q)_n\) generates the analogous partitions with smallest part at least two, by subtracting \((2n,2n-2,\ldots,2)\).

## Cycle 1: Formal Foundation and Finite Experiments

Cycle 1 built milestones M0 and M1. The researcher asked for a formal setup, finite coefficient harness, negative controls, and a validation document (`84bce78a-c820-4739-950c-3445d9d2c1f0`). The worker produced:

- `docs/lemmas/lemma_catalogue.md`
- `scripts/rr/finite_rr_experiments.wls`
- `scripts/rr/plot_rr_difference_heatmap.py`
- `docs/validation.md`
- coefficient, difference, recurrence, and figure outputs in `data/finite_experiments/`

The main finite experiment checked the two target series/products through degree 40. Both true pairs had no nonzero coefficient difference through that range. Negative controls failed early: residue classes \(\{1,3\}\) and \(\{2,4\}\) failed at degree 3, and the shifted exponent \(n^2+2n\) failed at degree 1.

![Heatmap of coefficient differences for the true residue products and negative controls. The true comparisons remain zero through the checked degree, while negative controls fail early.](data/finite_experiments/rr_difference_heatmap.png)

The auditor validated M0 and M1 after inspecting the artifacts and rerunning a smaller Wolfram check. A ledger-format defect was repaired, but no mathematical defect was found (`1759cc99-303e-4617-8ce0-56165df7f4f7`).

## Cycle 2: Q-Difference Ladder and Finite Gap Recurrence

Cycle 2 moved to M2: finding a proof-bearing transfer mechanism (`bb2de806-9212-4328-8d2f-33a4f8f88a3c`). The worker proved the auxiliary q-difference identity for

\[
F(z,q)=\sum_{n\ge0}\frac{z^nq^{n^2}}{(q;q)_n}.
\]

The proved identity is

\[
F(z,q)-F(zq,q)=zqF(zq^2,q).
\]

Specializing \(z=q^r\) gives the infinite ladder

\[
A_r=A_{r+1}+q^{r+1}A_{r+2},\qquad
A_r=F(q^r,q).
\]

Here \(A_0\) and \(A_1\) are the two Rogers-Ramanujan series sides. The worker also proved tail-normalized uniqueness: there is at most one ladder solution satisfying \(A_r\to1\) coefficientwise as \(r\to\infty\) (`docs/proof/q_difference_mechanism.md`, worker session `3503791b-e87a-459d-995e-a915715e61e2`).

The same cycle proved a finite largest-part recurrence. If \(G_N^{(a)}\) generates gap-two partitions with all parts at least \(a\) and largest part at most \(N\), then

\[
G_N^{(a)}=G_{N-1}^{(a)}+q^NG_{N-2}^{(a)}.
\]

This comes from splitting partitions by whether the largest allowed part \(N\) appears (`docs/proof/finite_gap_recurrence.md`).

![Residual plot for the q-difference ladder and backsolved product comparisons. The series ladder residuals are zero through the checked range.](data/finite_experiments/q_difference_residuals.png)

The auditor validated the cycle as partial M2 progress. The series-side ladder and uniqueness were accepted, but product-side closure was not proved. M2 remained `in-progress` (`036adf0a-962e-4299-8aae-8ac788349d06`).

## Cycle 3: Euler/Jacobi Product Transform

Cycle 3 varied the M2 strategy toward an Euler-product and finite q-binomial route (`221798d5-223f-4de3-8ca8-929e697ca61e`). The worker proved that multiplying by

\[
E(q)=(q;q)_\infty
\]

reduces the target product identities to complementary modulo-5 products:

\[
E(q)S_1=(q^2;q^5)_\infty(q^3;q^5)_\infty(q^5;q^5)_\infty,
\]

\[
E(q)S_2=(q;q^5)_\infty(q^4;q^5)_\infty(q^5;q^5)_\infty.
\]

The worker then derived, rather than cited, a finite q-binomial theorem and a finite Jacobi-type identity. Passing coefficientwise to the limit gave

\[
(z;Q)_\infty(Q/z;Q)_\infty(Q;Q)_\infty
=
\sum_{j\in\mathbb Z}(-1)^jz^jQ^{j(j-1)/2}.
\]

With \((Q,z)=(q^5,q^2)\), this yields exponents \(j(5j-1)/2\). With \((Q,z)=(q^5,q)\), it yields \(j(5j-3)/2\). This proves the product/Jacobi half of the route (`docs/proof/product_transform_route.md`, worker session `f5efac66-0414-4e6e-a0c6-cd3f74a442df`).

The transformed finite series were

\[
H_{\alpha,N}=\sum_{n=0}^{N}q^{n^2+\alpha n}\frac{(q;q)_N}{(q;q)_n}.
\]

They satisfy the proved recurrence

\[
H_{\alpha,N}=(1-q^N)H_{\alpha,N-1}+q^{N^2+\alpha N}.
\]

Experiments showed that the natural bilateral comparisons stabilize through degree \(N\), but simple Schur-style Gaussian-window finite identities fail at degree 1. Therefore the transformed-series bilateral collapse remained conjectural as lemma L16.

![First-failure degree for transformed-series candidates and negative controls. Natural comparisons stabilize through degree \(N\), while tested exact Gaussian-window formulas fail early.](data/finite_experiments/product_transform_residuals.png)

The auditor validated the cycle as partial success. The plot script was fixed to support `--out`, ledger schema was repaired, and fresh Wolfram checks reproduced the stated residuals. The decision was `VALIDATED`, with M2 still open (`532d9472-a3f9-4ebd-ab75-90e005dc2cdf`).

## Current Proof Status

Proved foundations:

- Formal coefficientwise equality, truncation transfer, and stabilization in \(\mathbb{Z}[[q]]\).
- Staircase interpretations of both Rogers-Ramanujan series.
- Residue-product partition interpretation.
- Series-side q-difference ladder and tail-normalized uniqueness.
- Finite largest-part gap recurrence.
- Euler complement product reduction.
- Finite q-binomial theorem and derived Jacobi-type product identity.

Experimentally supported but not proved:

- The full Rogers-Ramanujan identities through finite coefficient checks.
- Product-side agreement with the q-difference backsolve.
- The transformed-series bilateral collapse \(E(q)S_\alpha\) to the Jacobi bilateral sums.

Rejected or not sufficient:

- Naive bounded finite residue products as exact finite identities.
- Simple Schur-style Gaussian-window identities for \(H_{\alpha,N}\).

## Open Questions

The next cycle should target the missing transformed-series collapse:

\[
E(q)\sum_{n\ge0}\frac{q^{n^2+\alpha n}}{(q;q)_n}
=
\sum_{j\in\mathbb Z}(-1)^jq^{j(5j-(2\alpha+1))/2},
\qquad \alpha=0,1.
\]

The audit guidance recommends either a sign-reversing involution for coefficients of \((q;q)_N\sum_n q^{n^2+\alpha n}/(q;q)_n\), or a richer finite state recurrence, likely involving modulo 5 or multiple coupled states.

## References

No `REFERENCES.md` file exists in the workspace, and the cycle records state that no web search or external proof lookup was used. No external references are cited in this report.

## Appendix: Implementation Details

Session references:

| cycle | researcher | worker | auditor |
|---|---|---|---|
| 1 | `84bce78a-c820-4739-950c-3445d9d2c1f0` | `8f4715a2-55b0-41e8-97b8-7a8ffd2c2709` | `1759cc99-303e-4617-8ce0-56165df7f4f7` |
| 2 | `bb2de806-9212-4328-8d2f-33a4f8f88a3c` | `3503791b-e87a-459d-995e-a915715e61e2` | `036adf0a-962e-4299-8aae-8ac788349d06` |
| 3 | `221798d5-223f-4de3-8ca8-929e697ca61e` | `f5efac66-0414-4e6e-a0c6-cd3f74a442df` | `532d9472-a3f9-4ebd-ab75-90e005dc2cdf` |

Code organization:

| path | files | role |
|---|---:|---|
| `scripts/rr/` | 7 | Wolfram experiment harnesses and Python plotting scripts |
| `docs/lemmas/` | 1 | Lemma catalogue with proof statuses |
| `docs/proof/` | 3 | q-difference, finite-gap, and product-transform proof notes |
| `data/finite_experiments/` | 21 | CSV outputs and three figures |
| `docs/validation.md` | 1 | Separation of experiments, proof-supporting checks, and proved lemmas |

Validation runs recorded across cycles include:

- `wolfram-batch -script scripts/rr/finite_rr_experiments.wls`
- `wolfram-batch -script scripts/rr/q_difference_probe.wls`
- `wolfram-batch -script scripts/rr/finite_gap_probe.wls`
- `wolfram-batch -script scripts/rr/product_transform_probe.wls`
- `python3 -m long_exposure.tools.promise_check <run-workspace>`
- `python3 -m long_exposure.tools.org_check <run-workspace>`

Current warnings are process/organization warnings only: M3 and M4 have no ledger events yet, `data/sessions.db*` are orphan artifacts, and `rogers_ramanujan_run_config.yaml` remains a root-file organization warning.

A workspace `MANIFEST.md` snapshot was updated for this report with script counts, line counts, and cross-references.
