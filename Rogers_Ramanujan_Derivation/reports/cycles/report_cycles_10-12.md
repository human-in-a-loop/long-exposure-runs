---
title: "Rogers-Ramanujan Derivation — cycles 10-12"
date: "2026-05-15"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# Rogers-Ramanujan Derivation — cycles 10-12

## Introduction

Cycles 10-12 closed the Rogers-Ramanujan proof campaign. The work entered this range with M0, M1, and M2 already validated: the formal power series setting was established, finite experiments and diagnostic routes had been catalogued, and the derived Bailey-style triangular transform had supplied the missing series-to-Jacobi transfer mechanism. The remaining work was to formalize the product-side cancellation, assemble a final self-contained proof, and record closure.

The cycle records show three stages of completion:

- Cycle 10, from the provided session list, formalized the product side and validated milestone M3. The durable artifacts are `docs/proof/product_side.md`, `scripts/rr/product_side_formal_check.wls`, `data/finite_experiments/product_side_residuals.csv`, updates to `docs/lemmas/lemma_catalogue.md`, updates to `docs/validation.md`, and M3 ledger events. Sources: researcher `25a1a823-822a-4e33-8873-d4711a7424a2`, worker `b8a2a43b-6421-4bd5-84ec-2d7b750c1b7c`, auditor `b0fdc201-d374-47d4-b27d-b8702f2be077`.

- Cycle 11 synthesized the final proof and validated milestone M4. The durable artifacts are `docs/proof/final_proof.md`, final validation updates, L41-L42 in the lemma catalogue, and M4 ledger events. Sources: researcher `102fed25-5298-4519-b012-aed49190d041`, worker `e3cc5e5f-cac1-4832-be01-99501edb2ec9`, auditor `66c6a89f-ea9c-4162-a135-35515350d8aa`.

- Cycle 12 recorded closure. No new build was needed; the auditor reported that the ledger records M0-M4 as validated and that the primary directive is complete. Sources: researcher `d6d2a09b-20a0-4a61-ab2e-6c6aae71735f`, worker `fc300977-5b2c-4813-ab63-e46ae0770c1e`, auditor `f800ec4e-f0a7-46d9-ad6d-2144957ca4d1`.

There is a minor bookkeeping mismatch between the provided cycle labels and some artifact front matter or ledger cycle numbers. The report follows the user-provided cycle range and session IDs. The mathematical status is unaffected: the final audit report supplied with the task marks M0-M4 as validated.

## Definitions and Notation

All final proof work is in the ring $\mathbb Z[[q]]$ of formal power series with integer coefficients. Equality means equality coefficient by coefficient. A sequence of formal series converges coefficientwise when each fixed coefficient eventually stabilizes.

For $n \ge 0$,

\[
(a;q)_n=\prod_{i=0}^{n-1}(1-aq^i),
\qquad
(a;q)_\infty=\prod_{i\ge0}(1-aq^i)
\]

when the infinite product is coefficientwise-defined. Products with constant term $1$ are units in $\mathbb Z[[q]]$, so all cancellations in the final proof are formal multiplication by inverses, not analytic division.

For residue-class products,

\[
(q^{r_1},\ldots,q^{r_t};q^d)_\infty
=\prod_{i=1}^t(q^{r_i};q^d)_\infty.
\]

The two Rogers-Ramanujan series are

\[
S_1(q)=\sum_{n\ge0}\frac{q^{n^2}}{(q;q)_n},
\qquad
S_2(q)=\sum_{n\ge0}\frac{q^{n^2+n}}{(q;q)_n}.
\]

## Results

### Theorem 1. Product-Side Closure for the First Identity

In $\mathbb Z[[q]]$,

\[
S_1(q)
=
\prod_{m\ge0}\frac{1}{(1-q^{5m+1})(1-q^{5m+4})}.
\]

Cycle 10 proved this in `docs/proof/product_side.md` by combining the validated Bailey transfer with the derived Jacobi product identity. The transfer gives

\[
(q;q)_\infty S_1(q)
=
\sum_{j\in\mathbb Z}(-1)^jq^{j(5j-1)/2}.
\]

The internally derived Jacobi specialization L14 gives

\[
\sum_{j\in\mathbb Z}(-1)^jq^{j(5j-1)/2}
=
(q^2,q^3,q^5;q^5)_\infty.
\]

The Euler product factors by residue class:

\[
(q;q)_\infty=(q,q^2,q^3,q^4,q^5;q^5)_\infty.
\]

Since these products are units, cancellation leaves

\[
S_1(q)
=
\frac{(q^2,q^3,q^5;q^5)_\infty}
{(q,q^2,q^3,q^4,q^5;q^5)_\infty}
=
\frac{1}{(q,q^4;q^5)_\infty}.
\]

This is exactly the target product over parts congruent to $1$ or $4$ modulo $5$. The worker recorded the result as L39, and the auditor validated it as part of M3.

### Theorem 2. Product-Side Closure for the Second Identity

In $\mathbb Z[[q]]$,

\[
S_2(q)
=
\prod_{m\ge0}\frac{1}{(1-q^{5m+2})(1-q^{5m+3})}.
\]

The same cycle proved the second identity by the parallel transformed equation

\[
(q;q)_\infty S_2(q)
=
\sum_{j\in\mathbb Z}(-1)^jq^{j(5j-3)/2}.
\]

The Jacobi specialization gives

\[
\sum_{j\in\mathbb Z}(-1)^jq^{j(5j-3)/2}
=
(q,q^4,q^5;q^5)_\infty.
\]

After using the same Euler residue factorization, formal cancellation gives

\[
S_2(q)
=
\frac{(q,q^4,q^5;q^5)_\infty}
{(q,q^2,q^3,q^4,q^5;q^5)_\infty}
=
\frac{1}{(q^2,q^3;q^5)_\infty}.
\]

This is exactly the target product over parts congruent to $2$ or $3$ modulo $5$. The worker recorded the result as L40, and the auditor validated it as part of M3.

### Theorem 3. Final Rogers-Ramanujan Proof Synthesis

Cycle 11 created `docs/proof/final_proof.md`, which is the final proof-bearing document. It restates the proof chain linearly:

1. Work in $\mathbb Z[[q]]$ with coefficientwise limits and formal product units.
2. Derive the finite $q$-binomial theorem by Gaussian Pascal recurrence.
3. Use that finite identity to derive the Jacobi-type product identity

   \[
   (z;Q)_\infty(Q/z;Q)_\infty(Q;Q)_\infty
   =
   \sum_{j\in\mathbb Z}(-1)^jz^jQ^{j(j-1)/2}.
   \]

4. Specialize it to obtain

   \[
   B_0(q)=(q^2,q^3,q^5;q^5)_\infty
   \]

   and

   \[
   B_1(q)=(q,q^4,q^5;q^5)_\infty.
   \]

5. Use the internally derived triangular transform

   \[
   \beta_n=\sum_{r=0}^{n}
   \frac{\alpha_r}{(q;q)_{n-r}(aq;q)_{n+r}}
   \]

   together with its explicitly derived inverse.

6. Apply the transform to $\beta_n=1/(q;q)_n$ for $a=1$ and $a=q$, producing the two alpha sequences used in the final proof.

7. Pass through the coefficientwise limiting transform

   \[
   \sum_{n\ge0}a^nq^{n^2}\beta_n
   =
   \frac{1}{(aq;q)_\infty}
   \sum_{r\ge0}a^rq^{r^2}\alpha_r.
   \]

8. Identify the transformed alpha sums with $B_0$ and $B_1$.

9. Cancel the residue-class factors formally to obtain the two target products.

The worker added final theorem entries L41 and L42 to `docs/lemmas/lemma_catalogue.md`. The M4 auditor validated the synthesis, noting that no equality in the final proof is justified solely by coefficient checks.

## Examples and Regression Checks

The cycles 10-12 computations were classified as regression checks, not as proof.

For M3, `scripts/rr/product_side_formal_check.wls` expanded truncated versions of the transformed identities, Jacobi products, and final reciprocal products. The main run reported:

```text
KMax=40
Transformed identity max residual: 0
Jacobi product max residual: 0
Final product identity max residual: 0
```

The same script was also run at `KMAX=0` to check the constant-term boundary used by formal unit cancellation.

For M4, the worker reran the critical Bailey and product-side checks:

```text
KMax=18
NMax=6
Alpha solve max residual: 0
Triangular transform max residual: 0
Limit inner residual max coefficient: 0
```

and

```text
KMax=18
Transformed identity max residual: 0
Jacobi product max residual: 0
Final product identity max residual: 0
```

The final audit accepts these only as discovery and regression evidence. The proof itself is the formal algebra recorded in `docs/proof/final_proof.md`.

No new figures were produced in cycles 10-12. Earlier figures remain part of the validation trail, but the closure cycles were proof-document and regression-check cycles.

## Remarks

The main decision in cycle 10 was to stop searching for new proof mechanisms. M2 had already validated the Bailey-style transfer, so the cycle focused on formal product-side cancellation. The researcher brief explicitly framed the risk as transcription discipline: keep the bilateral exponents correct, keep $B_0$ and $B_1$ separate, and match the target residue classes exactly.

The main decision in cycle 11 was to keep failed routes out of the final theorem proof. The final proof uses only the validated route: finite $q$-binomial algebra, Jacobi products, the derived triangular transform, coefficientwise limiting, and formal residue-class cancellation. Rejected routes remain in `docs/validation.md` as diagnostics.

The main decision in cycle 12 was closure. The researcher and worker both recorded that no further build was needed for the primary directive. The final auditor marked the directive validated and complete.

## Open Questions

No open question remains for the primary Rogers-Ramanujan directive. The ledger records M0-M4 as validated.

One optional extension remains: an independent direct partition bijection could still be pursued as a separate objective. It is not required for the validated proof chain.

## References

No external references were used in cycles 10-12, and no `REFERENCES.md` file exists in the workspace. The proof is documented through internal artifacts and session records.

## Appendix: Implementation Details

### Code Organization

The report-time `MANIFEST.md` snapshot records:

| category | count | lines |
|---|---:|---:|
| Wolfram scripts | 10 | 1405 |
| Python scripts | 10 | 1166 |
| Total scripts | 20 | 2571 |
| Proof/lemma/validation docs | 13 | 3036 |
| Experiment data and figures under `data/finite_experiments` | 82 | n/a |

The M3/M4-specific additions in this report range are:

| file | purpose |
|---|---|
| `docs/proof/product_side.md` | Formal product-side cancellation in $\mathbb Z[[q]]$. |
| `scripts/rr/product_side_formal_check.wls` | Regression check for transformed, Jacobi, and final product identities. |
| `data/finite_experiments/product_side_residuals.csv` | M3 residual output; all six residual families have zero max coefficient through the tested range. |
| `docs/proof/final_proof.md` | Final self-contained formal proof of both identities. |
| `docs/lemmas/lemma_catalogue.md` | Updated through L42, including the final theorem entries. |
| `docs/validation.md` | Updated to separate proof-bearing artifacts, regression scripts, diagnostics, and rejected routes. |
| `promise_ledger.jsonl` | Updated with M3 and M4 worker/regression/auditor events. |
| `MANIFEST.md` | Refreshed during this reporting pass to include the final script and proof inventory. |

### Test and Audit Results

Cycle 10 worker checks:

```bash
KMAX=40 OUTDIR=data/finite_experiments wolfram-batch -script scripts/rr/product_side_formal_check.wls
KMAX=0 OUTDIR=data/finite_experiments/test_product_side_k0 wolfram-batch -script scripts/rr/product_side_formal_check.wls
python3 -m long_exposure.tools.promise_check <run-workspace>
```

Cycle 10 auditor independently reran the product-side check at `KMAX=18`; it reported zero residuals. The auditor appended M3 validation event `1de672f2-0324-4979-b79b-e83eb371ec39`.

Cycle 11 worker checks:

```bash
KMAX=18 NMAX=6 OUTDIR=data/finite_experiments/test_m4_bailey wolfram-batch -script scripts/rr/bailey_matrix_probe.wls
KMAX=18 OUTDIR=data/finite_experiments/test_m4_product_side wolfram-batch -script scripts/rr/product_side_formal_check.wls
KMAX=0 OUTDIR=data/finite_experiments/test_m4_product_side_k0 wolfram-batch -script scripts/rr/product_side_formal_check.wls
python3 -m long_exposure.tools.org_check <run-workspace>
python3 -m long_exposure.tools.promise_check <run-workspace>
```

Cycle 11 auditor validated M4 and appended event `031480b5-4644-4668-b467-9dfcb1f3d0fd`.

Cycle 12 auditor reported no new build, no critical or moderate issues, and the final state:

| milestone | status |
|---|---|
| M0 formal setup | validated |
| M1 finite approximant exploration | validated |
| M2 derived Bailey-style transfer mechanism | validated |
| M3 product-side formalization | validated |
| M4 final proof synthesis and validation separation | validated |

Standing warnings remain unchanged: `promise_check` exits 0 with known orphan warnings for session database and generated report artifacts, and `org_check` exits 0 with the known root-file warning for `rogers_ramanujan_run_config.yaml`.

The workspace is not a git repository, so `git status --short` cannot be used for change reporting.

### Session References

| cycle | role | session ID | contribution |
|---|---|---|---|
| 10 | researcher | `25a1a823-822a-4e33-8873-d4711a7424a2` | Directed M3 product-side formalization after M2 validation. |
| 10 | worker | `b8a2a43b-6421-4bd5-84ec-2d7b750c1b7c` | Built `product_side.md`, product-side check script, residual CSV, L37-L40, and validation updates. |
| 10 | auditor | `b0fdc201-d374-47d4-b27d-b8702f2be077` | Validated M3 and recorded formal cancellation as correct. |
| 11 | researcher | `102fed25-5298-4519-b012-aed49190d041` | Directed final proof synthesis and validation separation. |
| 11 | worker | `e3cc5e5f-cac1-4832-be01-99501edb2ec9` | Built `final_proof.md`, updated validation, added L41-L42, and ran regressions. |
| 11 | auditor | `66c6a89f-ea9c-4162-a135-35515350d8aa` | Validated M4 and confirmed final theorem statements match the directive. |
| 12 | researcher | `d6d2a09b-20a0-4a61-ab2e-6c6aae71735f` | Recorded that the primary directive was complete. |
| 12 | worker | `fc300977-5b2c-4813-ab63-e46ae0770c1e` | Confirmed no new build was needed. |
| 12 | auditor | `f800ec4e-f0a7-46d9-ad6d-2144957ca4d1` | Validated final closure state with M0-M4 complete. |

### Cross-Reference Map

| proof component | source artifact | final use |
|---|---|---|
| Formal coefficientwise setting | `docs/lemmas/lemma_catalogue.md` L0-L4 | Defines equality, limits, truncation, and product legality. |
| Jacobi product identity | `docs/lemmas/lemma_catalogue.md` L13-L14, `docs/proof/product_transform_route.md` | Supplies $B_0$ and $B_1$ product forms. |
| Bailey-style triangular transform | `docs/proof/bailey_matrix_transform.md`, L33-L36 | Transfers $S_1$ and $S_2$ to bilateral Jacobi sums. |
| Product-side cancellation | `docs/proof/product_side.md`, L37-L40 | Converts transformed products into residue reciprocal products. |
| Final theorem proof | `docs/proof/final_proof.md`, L41-L42 | Assembles the complete derivation of both Rogers-Ramanujan identities. |
| Validation separation | `docs/validation.md` | Records which computations are discovery/regression only and which documents are proof-bearing. |
