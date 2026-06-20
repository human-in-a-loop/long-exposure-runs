---
title: "Rogers-Ramanujan Derivation — cycles 7-9"
date: "2026-05-15"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# Rogers-Ramanujan Derivation — cycles 7-9

## Introduction

Cycles 7-9 continued milestone M2: finding a proof-bearing transfer from the Rogers-Ramanujan series

\[
S_\alpha(q)=\sum_{n\ge0}\frac{q^{n^2+\alpha n}}{(q;q)_n},\qquad \alpha\in\{0,1\},
\]

to the modulo-five product sides. The cycle labels in this report follow the supplied `cycle_sessions` input. Some artifact front matter and ledger entries use adjacent internal cycle numbers, but the source sessions for this report are exactly the nine session IDs listed in the handoff.

The work proceeded in three steps. First, the Euler-tail telescoping route proved a useful double-sum expansion but rejected the tested low-order telescoping certificates. Second, the direct partition-bijection route generated exact finite gap/residue partition data but rejected simple static beta-set and abacus maps. Third, the Bailey-style triangular matrix route supplied the missing mechanism: it derived a finite matrix inverse, explicit alpha sequences, a coefficientwise limiting transform, and the connection to the already-proved Jacobi product identities. The auditor validated this as closing M2.

The outcome is that M2 is now validated. The remaining work is no longer mechanism discovery; it is M3 product-side formalization and M4 final proof synthesis.

## Definitions and Notation

All identities are treated in the formal power series ring unless otherwise stated. The finite product notation is

\[
(q;q)_n=\prod_{k=1}^n(1-q^k),
\qquad
(a;q)_n=\prod_{k=0}^{n-1}(1-aq^k).
\]

The two Rogers-Ramanujan series are

\[
S_0(q)=\sum_{n\ge0}\frac{q^{n^2}}{(q;q)_n},
\qquad
S_1(q)=\sum_{n\ge0}\frac{q^{n^2+n}}{(q;q)_n}.
\]

Earlier cycles had already proved the formal setup, the staircase interpretation of the series, the residue-class interpretation of the products, and the Jacobi-type complementary product identities. Cycles 7-9 used those earlier results rather than re-proving them.

## Results

### Cycle 7: Euler-Tail Telescoping

Cycle 7 tested whether multiplying the Rogers-Ramanujan series by the Euler product could be collapsed directly to the bilateral pentagonal sums. The researcher session `bbad39f9-bd37-4653-8c6e-3202a176434e` proposed expanding the Euler tail and searching for telescoping certificates on the \((n,k)\)-lattice. The worker session `72b889fb-afd5-44aa-8ca3-70ef78b56b45` built `docs/proof/euler_tail_telescoping.md` and `scripts/rr/euler_tail_telescoping_probe.wls`. The auditor session `4a3065c4-20bc-4202-9cca-d9aa42d8cf5a` validated the partial result after fixing a selector scoping defect in the mod-5 diagnostic.

The proved result is Lemma L27. For \(\alpha\in\{0,1\}\),

\[
(q;q)_\infty S_\alpha(q)
=
\sum_{n,k\ge0}
\frac{(-1)^kq^{n^2+\alpha n+kn+k(k+1)/2}}{(q;q)_k}.
\]

This follows from the finite q-binomial theorem applied coefficientwise to

\[
(q^{n+1};q)_\infty
=
\sum_{k\ge0}\frac{(-1)^kq^{k(k+1)/2+kn}}{(q;q)_k},
\]

and the cancellation

\[
(q;q)_\infty\frac{q^{n^2+\alpha n}}{(q;q)_n}
=
q^{n^2+\alpha n}(q^{n+1};q)_\infty.
\]

The rejected result is Lemma L28. The probe tested certificates of the form

\[
F_\alpha(n,k)
=
U_\alpha(n,k)-U_\alpha(n+1,k)
+V_\alpha(n,k)-V_\alpha(n,k+1)+R_\alpha(n,k),
\]

with \(U=A(x,y)F_\alpha(n,k)\), \(V=B(x,y)F_\alpha(n,k)\), \(x=q^n\), and \(y=q^k\). The normalized identity was

\[
A(x,y)-q^{\alpha+1}x^2yA(qx,y)
+B(x,y)+\frac{qxy}{1-qy}B(x,qy)=1.
\]

For polynomial \(A,B\) of total degree at most 3, including monomial-support diagnostics by \(2n+k+\alpha \bmod 5\), the exact cleared polynomial systems had no solution. This rejected only the tested ansatz class; it did not rule out richer telescoping certificates.

The finite truncation check, Lemma L29, agreed with the corrected bilateral targets through degree 40, but it remained explicitly labeled as diagnostic evidence rather than proof.

![Residual support on the \((n,k)\)-lattice after the Euler-tail expansion; the top panels show checked lattice terms with pentagonal exponents highlighted, and the bottom panels show zero finite residuals against the corrected bilateral targets through `KMAX=40`.](data/finite_experiments/euler_tail_lattice_residuals.png)

### Cycle 8: Direct Partition-Bijection Diagnostics

Cycle 8 pivoted to the direct combinatorial route. The researcher session `59a349f1-618a-4f54-9696-b6b37afc520e` asked whether the already-proved gap-two partition interpretation could be mapped directly to the modulo-five residue partitions. The worker session `0fec6a27-bb37-44fb-b1f3-44c040cd40ed` created `docs/proof/direct_partition_bijection.md` and `scripts/rr/direct_bijection_probe.py`. The auditor session `7ac2b819-e0ee-40a5-807f-bb85cb14ac3d` validated the cycle as partial M2 progress.

The finite sets were

\[
G_\alpha(K)=\{\lambda\vdash K:\lambda_i-\lambda_{i+1}\ge2,\
\lambda_{\ell(\lambda)}\ge1+\alpha\},
\]

and

\[
R_0(K)=\{\rho\vdash K:\rho_i\equiv1,4\pmod5\},
\qquad
R_1(K)=\{\rho\vdash K:\rho_i\equiv2,3\pmod5\}.
\]

Lemma L30 records that the exact enumerations matched in cardinality through `KMax=28` for both \(\alpha=0\) and \(\alpha=1\). This was a consistency check for the direct bijection route, not a proof.

The rejected mechanisms were L31 and L32. L31 rejected static signatures using length, beta-set runner counts, shifted beta-set runner counts, and quotient sums. Minimal failures occurred at low weights, including \(\alpha=0\), \(\lambda=(1)\), for shifted-runner signatures, and \(\alpha=1\), \(\lambda=(4)\), for length-plus-runner signatures. L32 rejected the independent nearest-runner bead slide because it changed total weight in minimal examples; for \(\alpha=0\), \(\lambda=(2)\) mapped from beta position 2 to image weight 1.

The conclusion was not that direct bijections are impossible. It was narrower: static low-information beta/abacus signatures and independent nearest-runner normalization are insufficient. Any successful direct bijection would need ordered moves, charge data, recursive insertion/deletion, or another richer structure.

![5-abacus views of same-weight small gap-two and residue-class partitions; blue beads lie on the target allowed runners for the corresponding alpha, and orange beads mark forbidden runners in the tested beta/residue display.](data/finite_experiments/direct_bijection_abacus_examples.png)

### Cycle 9: Bailey-Style Matrix Transform

Cycle 9 changed mechanism axis again. The researcher session `d70f02b6-7e45-43f0-a6c6-3f6dba479bfa` proposed deriving a Bailey-style triangular transform from finite q-binomial algebra rather than citing a known theorem. The worker session `a033b4c5-6641-47a7-9ebd-7c4db37a9c3b` built `docs/proof/bailey_matrix_transform.md`, `scripts/rr/bailey_matrix_probe.wls`, and `scripts/rr/plot_bailey_transform_residuals.py`. The auditor session `d9c612a8-38e0-44dd-ab4c-d940fc08773b` validated the result and recorded M2 as validated.

The finite lower triangular matrix was

\[
M^{(a)}_{n,r}=
\frac{1}{(q;q)_{n-r}(aq;q)_{n+r}},
\qquad 0\le r\le n,
\]

with relation

\[
\beta_n=\sum_{r=0}^n M^{(a)}_{n,r}\alpha_r.
\]

Lemma L33 proved the inverse

\[
\alpha_n=\sum_{j=0}^n
\frac{1-aq^{2n}}{1-a}
\frac{(a;q)_{n+j}}{(q;q)_{n-j}}
(-1)^{n-j}q^{(n-j)(n-j-1)/2}\beta_j.
\]

The proof multiplied the triangular matrices directly. Diagonal terms became 1. Off-diagonal terms reduced to finite q-binomial cancellations of the form

\[
\sum_k(-1)^k q^{k(k-1)/2}{m\brack k}_q q^{-tk}=0,
\qquad 0\le t<m.
\]

Lemma L34 applied the inverse to \(\beta_n=1/(q;q)_n\). For \(a=1\),

\[
\alpha^{(0)}_0=1,\qquad
\alpha^{(0)}_r=(-1)^rq^{r(3r-1)/2}(1+q^r)\quad(r\ge1).
\]

For \(a=q\),

\[
\alpha^{(1)}_r=(-1)^rq^{r(3r+1)/2}\frac{1-q^{2r+1}}{1-q}.
\]

Lemma L35 proved the coefficientwise limiting transform

\[
\sum_{n\ge0}a^nq^{n^2}\beta_n
=
\frac{1}{(aq;q)_\infty}\sum_{r\ge0}a^rq^{r^2}\alpha_r.
\]

The inner sum was reduced to

\[
\sum_{s\ge0}\frac{z^s q^{s(s-1)}(zq^s;q)_\infty}{(q;q)_s}=1,
\]

and the coefficient of \(z^m\) vanished for \(m>0\) by the finite q-binomial factor \((1;q)_m=0\). Coefficientwise interchange was justified by the earlier formal truncation lemmas.

Lemma L36 then connected the transform to the already-proved Jacobi products. For \(a=1\),

\[
S_0(q)
=
\frac1{(q;q)_\infty}
\sum_{j\in\mathbb Z}(-1)^jq^{j(5j-1)/2}.
\]

Using the earlier Jacobi product identity,

\[
\sum_{j\in\mathbb Z}(-1)^jq^{j(5j-1)/2}
=
(q^2;q^5)_\infty(q^3;q^5)_\infty(q^5;q^5)_\infty,
\]

division by \((q;q)_\infty\) leaves the reciprocal product over parts congruent to \(1\) or \(4\pmod5\).

For \(a=q\),

\[
S_1(q)
=
\frac{1}{(q^2;q)_\infty(1-q)}
\sum_{j\in\mathbb Z}(-1)^jq^{j(5j-3)/2}.
\]

The earlier Jacobi identity gives

\[
\sum_{j\in\mathbb Z}(-1)^jq^{j(5j-3)/2}
=
(q;q^5)_\infty(q^4;q^5)_\infty(q^5;q^5)_\infty.
\]

Since \((q;q)_\infty=(1-q)(q^2;q)_\infty\), division gives the reciprocal product over parts congruent to \(2\) or \(3\pmod5\).

The Wolfram probe supported the algebra by checking exact cleared residuals. The main run used `KMAX=50` and `NMAX=12` and reported:

```text
Alpha solve max residual: 0
Triangular transform max residual: 0
Limit inner residual max coefficient: 0
```

The audit independently reran a smaller focused check with `KMAX=16` and `NMAX=7`, compiled the plotting script, regenerated a PNG in `/tmp`, and found no critical or moderate defects.

![Finite triangular-transform residuals for the derived \(a=1\) and \(a=q\) pairs; all tested cleared residual numerators are exactly zero.](data/finite_experiments/bailey_transform_residuals.png)

## Remarks

The failed routes remain useful because they define what was not silently assumed. The Euler-tail cycle established the double-sum reduction but showed that a simple low-degree divergence certificate was not available. The direct partition cycle showed that basic beta-set and abacus statistics do not supply a canonical bijection. These negative results justified the pivot to the finite triangular matrix transform.

The Bailey-style matrix route is the first mechanism in these cycles that supplies a complete proof-bearing bridge. It does not rely on an external Bailey lemma citation. The reportable derivation is internal: define the triangular matrix, derive its inverse, solve the two alpha sequences, prove the limiting transform coefficientwise, and then use the already-derived Jacobi product identities.

## Open Questions

M2 is validated, but M3 and M4 remain. M3 should formalize the product-side closure in a dedicated document, likely `docs/proof/product_side.md`, using L33-L36, the Jacobi product identity L14, Euler complement cancellation, and invertibility of products with constant term 1. M4 should synthesize the final proof in `docs/proof/final_proof.md`.

A direct partition bijection remains open as an optional independent route. It is no longer needed for the main proof chain, but the finite diagnostics suggest that any direct bijection must use structure richer than static runner counts or independent nearest-runner bead moves.

## References

No external references were used for these cycles, and no `REFERENCES.md` file is present in the workspace.

## Appendix: Implementation Details

### Source Inventory

| input cycle | source ID | date | role | contents |
|---:|---|---|---|---|
| 7 | `bbad39f9-bd37-4653-8c6e-3202a176434e` | 2026-05-15 | researcher | Brief for Euler-tail telescoping after prior transformed-collapse obstructions. |
| 7 | `72b889fb-afd5-44aa-8ca3-70ef78b56b45` | 2026-05-15 | worker | Built Euler-tail proof note, Wolfram probe, plot script, CSVs, and figure. |
| 7 | `4a3065c4-20bc-4202-9cca-d9aa42d8cf5a` | 2026-05-15 | auditor | Validated Euler-tail partial result; fixed mod-5 selector scoping in the diagnostic. |
| 8 | `59a349f1-618a-4f54-9696-b6b37afc520e` | 2026-05-15 | researcher | Brief for direct partition-bijection pivot using gap/residue finite sets. |
| 8 | `0fec6a27-bb37-44fb-b1f3-44c040cd40ed` | 2026-05-15 | worker | Built direct partition enumeration, beta/abacus diagnostics, CSVs, and figure. |
| 8 | `7ac2b819-e0ee-40a5-807f-bb85cb14ac3d` | 2026-05-15 | auditor | Validated direct-bijection diagnostics as partial M2 progress. |
| 9 | `d70f02b6-7e45-43f0-a6c6-3f6dba479bfa` | 2026-05-15 | researcher | Brief for derived Bailey-style finite matrix transformation. |
| 9 | `a033b4c5-6641-47a7-9ebd-7c4db37a9c3b` | 2026-05-15 | worker | Built Bailey matrix proof note, Wolfram probe, residual CSVs, plot script, and figure. |
| 9 | `d9c612a8-38e0-44dd-ab4c-d940fc08773b` | 2026-05-15 | auditor | Validated Bailey matrix route and recorded M2 as validated. |

### Artifact Inventory

New or central proof documents for these cycles:

| file | role |
|---|---|
| `docs/proof/euler_tail_telescoping.md` | Proves L27 and records L28/L29. |
| `docs/proof/direct_partition_bijection.md` | Records direct gap/residue enumeration and rejected simple abacus maps. |
| `docs/proof/bailey_matrix_transform.md` | Proves L33-L36 and closes M2. |
| `docs/lemmas/lemma_catalogue.md` | Updated with L27-L36. |
| `docs/validation.md` | Records cycle outputs, commands, figures, and proof-vs-diagnostic status. |
| `promise_ledger.jsonl` | Records worker and auditor events, including M2 validation. |
| `MANIFEST.md` | Updated snapshot of scripts, line counts, and cross-references. |

Scripts added or central in these cycles:

| file | lines | purpose |
|---|---:|---|
| `scripts/rr/euler_tail_telescoping_probe.wls` | 155 | Exact Euler-tail certificate search. |
| `scripts/rr/plot_euler_tail_lattice_residuals.py` | 80 | Euler-tail lattice/residual figure. |
| `scripts/rr/direct_bijection_probe.py` | 409 | Gap/residue partition enumeration and abacus diagnostics. |
| `scripts/rr/bailey_matrix_probe.wls` | 142 | Bailey matrix alpha solves and residual checks. |
| `scripts/rr/plot_bailey_transform_residuals.py` | 49 | Bailey residual figure. |

Figures used in this report:

| figure | size | source |
|---|---:|---|
| `data/finite_experiments/euler_tail_lattice_residuals.png` | 1760 x 1120 | Euler-tail plot script. |
| `data/finite_experiments/direct_bijection_abacus_examples.png` | 1600 x 1120 | Direct-bijection probe figure mode. |
| `data/finite_experiments/bailey_transform_residuals.png` | 1280 x 720 | Bailey residual plot script. |

### Validation Results

Euler-tail main run:

```text
KMax=40
NMax=16
DegMax=3
Certificate candidates tested: 48
Solved candidates: 0
alpha=0 partial double sum minus bilateral first nonzero: none_through_KMax
alpha=1 partial double sum minus bilateral first nonzero: none_through_KMax
```

Direct partition-bijection main run:

```text
KMax=28
alpha=0 gap/residue counts match through KMax
alpha=1 gap/residue counts match through KMax
Candidate diagnostics tested: 40
Candidate failures recorded: 12
```

Bailey matrix main run:

```text
KMax=50
NMax=12
Alpha solve max residual: 0
Triangular transform max residual: 0
Limit inner residual max coefficient: 0
```

Bailey audit rerun:

```text
KMAX=16
NMAX=7
Alpha solve max residual: 0
Triangular transform max residual: 0
Limit inner residual max coefficient: 0
```

Standing validator warnings remained minor: M3/M4 had no ledger events yet at audit time, session/report artifacts were orphan warnings, and `rogers_ramanujan_run_config.yaml` remained at the workspace root. These were not blockers.

### File Counts

The updated manifest records:

| category | count | lines |
|---|---:|---:|
| Wolfram scripts | 9 | 1306 |
| Python scripts | 10 | 1166 |
| Total scripts | 19 | 2472 |
| Proof/lemma/validation docs | 11 | 2478 |
| Experiment data and figures under `data/finite_experiments` | 75 | n/a |

### Cross-Reference Map

| result | origin | consuming artifact |
|---|---|---|
| L27 Euler-tail expansion | `docs/proof/euler_tail_telescoping.md` | `docs/lemmas/lemma_catalogue.md`, `docs/validation.md` |
| L28 rejected low-order certificate | `scripts/rr/euler_tail_telescoping_probe.wls` | `docs/proof/euler_tail_telescoping.md` |
| L30 finite gap/residue enumeration | `scripts/rr/direct_bijection_probe.py` | `docs/proof/direct_partition_bijection.md` |
| L31/L32 rejected abacus maps | `scripts/rr/direct_bijection_probe.py` | `docs/lemmas/lemma_catalogue.md`, `docs/validation.md` |
| L33 triangular inverse | `docs/proof/bailey_matrix_transform.md` | L34-L36 |
| L34 explicit alpha pairs | `docs/proof/bailey_matrix_transform.md`, `scripts/rr/bailey_matrix_probe.wls` | L35/L36 |
| L35 limiting transform | `docs/proof/bailey_matrix_transform.md` | L36 |
| L36 transfer to Jacobi products | `docs/proof/bailey_matrix_transform.md`, earlier L14 | M2 validation and future M3/M4 |
