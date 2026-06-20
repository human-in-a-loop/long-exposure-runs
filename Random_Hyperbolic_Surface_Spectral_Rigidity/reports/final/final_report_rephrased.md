---
title: "Random Hyperbolic Surface Spectral Rigidity: Rephrased Final Synthesis"
date: "2026-05-17"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
header-includes:
  - \usepackage{xurl}
---

# Random Hyperbolic Surface Spectral Rigidity: Rephrased Final Synthesis

## Abstract

This report summarizes a research run on Kim and Tao's paper *Eigenvalue rigidity of hyperbolic surfaces in the random cover model*. The run reconstructed the proof structure of the paper, identified where the main quantitative losses occur, built finite permutation and Schreier-graph test cases, and then used those reconstructions to look for possible extensions.

The main verified outputs are:

- a proof ledger for the eigenvalue-rigidity theorem and the eigenfunction-delocalization theorem;
- a finite expectation identity for labelled graph embeddings in random permutations;
- product-ratio and aggregate-control toy theorems;
- an obstruction map for local spectral windows;
- direct corollaries for multiplicity, mass distribution, and fixed-width spectral window counts;
- a standalone theorem for trace moments of a two-permutation Schreier graph model.

The run did **not** prove a better Kim--Tao exponent, a shrinking-window spectral-statistics theorem, or a theorem transferring the Schreier model back to random hyperbolic covers. Its clearest mathematical conclusion is more modest and more precise: the most credible next target is a coefficient-variation or signed-cancellation theorem for the actual numerator appearing in Kim--Tao's Corollary 3.4, after division by its denominator, evaluated at $x=1/n$:

$$
\frac{p(1/n)}{Q_{\mathrm{id}}(1/n)}.
$$

The final audit reported `76 validated, 1 in-progress; findings CRITICAL=1 MODERATE=1; promise_check=green`. The two remaining audit issues are about traceability of generated files, not about mathematical contradictions in the reported results.

## How to Read the Report

Several phrases in the original machine-generated report mixed mathematical ideas with internal project language. This rephrased version keeps the formulas, claims, and scope boundaries unchanged, but rewrites that language in a form intended for a PhD mathematician familiar with spectral geometry, probability, or representation-theoretic trace methods.

The following choices are used throughout:

- "research run" means the long-exposure investigation whose results are being summarized.
- "extension route" means a possible mathematical strategy for going beyond the Kim--Tao theorem.
- "validated" means checked against the run's reports, scripts, audits, or proof notes; it does not mean peer-reviewed.
- Terms that remain somewhat specialized are collected in the terminology appendix.

## 1. The Kim--Tao Problem and the Reconstructed Proof Structure

Kim and Tao study random finite covers of a fixed compact hyperbolic surface. Let

$$
X=\Gamma\backslash\mathbb H
$$

be the base surface, with genus at least two. A random degree-$n$ cover is encoded by a uniformly chosen homomorphism

$$
\phi_n:\Gamma\to S_n.
$$

The associated permutation representation is denoted $\rho_{\phi_n}$. The Laplace eigenvalues on the random cover $X_n$ are written $\lambda_j(X_n)$, and the usual spectral parameter is

$$
\lambda=\frac14+r^2.
$$

The first part of the run separated the old spectrum inherited from $X$ from the new spectrum of the random cover. It then reconstructed the two main theorem paths in the paper.

Theorem 1 is the high-probability eigenvalue-rigidity and Weyl-law theorem for eigenvalues in $[1/4,\Lambda]$. Its proof goes through the twisted Selberg trace formula and Proposition 3.1.

Theorem 2 is the eigenfunction-delocalization theorem. Its proof goes through the twisted pre-trace formula and Propositions 4.1 and 4.2.

This distinction matters. Theorem 2 is not simply Theorem 1 with the trace formula replaced by the pre-trace formula. It uses a local fourth-moment statistic, subtracts a primitive-power diagonal term, invokes an eight-word folded-graph estimate, and then pays separate probability and elliptic-regularity costs.

### 1.1 Theorem 1: From Proposition 3.1 to Rigidity

The run first treated Proposition 3.1 as a black box and then opened the box. Downstream from Proposition 3.1, the proof of Theorem 1 uses:

- a smooth cutoff;
- derivative-norm bookkeeping;
- Chebyshev's inequality;
- a spectral grid;
- an inversion step from a counting-function estimate to individual eigenvalue locations.

In the notation used in the proof ledger, the variance bound after the smooth cutoff has the form

$$
\operatorname{Var}\le C n^{-1}\Lambda_0^{-K}
\Lambda^{2m(1/2-\epsilon)}n^{2m\alpha_0},
$$

where

$$
m=\kappa+3+K,\qquad \alpha_0=\frac{1}{3m}.
$$

This choice gives

$$
-1+2m\alpha_0=-1/3.
$$

The later choice

$$
K=\left\lfloor\frac{\kappa+5}{2\epsilon}\right\rfloor+1
$$

gives enough decay in $\Lambda$ for the union bound over the spectral grid. This leads to the paper's simultaneous high-probability scale $1-n^{-1/10}$.

Near the bottom of the continuous spectral parameter range, $\lambda=1/4$, the Weyl integral

$$
F(\Lambda)=\int_0^{\sqrt{\Lambda-1/4}}r\tanh(\pi r)\,dr
$$

satisfies

$$
F(1/4+t)\sim(\pi/3)t^{3/2}.
$$

Thus the passage from counting estimates to eigenvalue-location estimates is Hölder near the edge, not Lipschitz. The proof ledger therefore distinguishes the Weyl-law exponent $\alpha_W$ from the possibly weaker eigenvalue-rigidity exponent $\alpha_R$.

### 1.2 The Corollary 3.4 Polynomial

Opening Proposition 3.1 reveals a trace-side random variable. The centered spectral statistic becomes, through the Selberg trace formula, a geodesic-side random sum $S_n$. Its second moment is expanded as

$$
n^{-2}\mathbb E S_n^2.
$$

The random part of each term is

$$
\mathbb E\left[\operatorname{tr}\rho(\gamma_1^{k_1})
\operatorname{tr}\rho(\gamma_2^{k_2})\right].
$$

Lemma 3.3 rewrites this product of traces as a common fixed-point statistic attached to folded quotient graphs built from two labelled cycles. Corollary 3.4 packages the resulting second moment into the form

$$
\mathbb E S_n^2=\frac{p(1/n)}{Q_{\mathrm{id}}(1/n)}+\text{error}.
$$

This expression became the main object for later extension attempts. The important point is not just the numerator $p$, but the evaluated ratio after division by $Q_{\mathrm{id}}(1/n)$.

### 1.3 Theorem 2: Pre-Trace and Fourth Moments

The proof of Theorem 2 follows the same broad philosophy but has different local structure. The pre-trace formula produces a centered local spectral mass. In the cycle reports, its fourth power is denoted $V_n$. A primitive-power diagonal term $S$ is subtracted before applying the rank-two estimate.

The reconstructed proof path is:

```text
twisted pre-trace formula
-> centered local spectral mass
-> fourth power V_n
-> subtract primitive-power diagonal S
-> Proposition 4.2 eight-word polynomial approximation
-> Markov second-derivative q^{4 kappa} loss
-> Proposition 4.1
-> Chebyshev, fiber union, and window union
-> local L2 mass bound
-> Sobolev/elliptic conversion to L-infinity
```

The subtraction of $S$ is structural. The fourth moment $V_n$ alone contains cyclic primitive-power contributions that are too large for the rank-two common-fixed-point input. After subtracting $S$, the remaining non-diagonal statistic is the one to which the eight-word folded-graph machinery applies.

The reconstructed dependency map separates three kinds of inputs.

Standard background:

- random covers as homomorphisms into $S_n$;
- the Selberg trace formula;
- the pre-trace formula;
- hyperbolic kernel estimates;
- Chebyshev's inequality;
- monotonicity;
- Sobolev embedding and elliptic regularity.

Imported inputs:

- prior test-function technology;
- MPvH-style polynomial expansions;
- Witten-zeta and homomorphism-count asymptotics;
- Nau boundedness;
- MP23 rank-two estimates;
- Chebyshev coefficient control;
- Markov brothers' inequality.

Kim--Tao-specific constructions:

- the two-trace graph $C_{\gamma_1,\gamma_2}$;
- the Corollary 3.4 second-moment polynomialization;
- the fourth-order pre-trace statistic with diagonal subtraction.

## 2. Where the Quantitative Losses Enter

The proof reconstruction did not produce a sharper exponent. Its main quantitative contribution was to locate where the known losses enter.

For Theorem 1, the most visible proposition-level loss occurs at the Markov brothers interpolation step. The polynomial used there is

$$
P(x)=x^2p(x).
$$

Before this step, the argument controls $P(1/n)$ at reciprocal integer points. Markov brothers' inequality converts this discrete control into derivative control near zero:

$$
\|P'\|\le Cq^{2\kappa}
\sup_{n\ge Cq^\kappa}|P(1/n)|.
$$

Taylor expansion from $0$ to $1/n$, together with $P(0)=0$, gives the desired $n^{-1}$ gain:

$$
|P(1/n)|\le \frac{1}{n}\|P'\|.
$$

Thus the factor $q^{2\kappa}$ comes from derivative amplification. It is not forced merely by the initial formation of the two-trace statistic. The run did not show that this loss is sharp.

After Proposition 3.1, additional losses enter from smooth cutoff derivatives, the order

$$
m=\kappa+3+K,
$$

the choice of $K$, Chebyshev conversion to high probability, the union bound over the spectral grid, and the edge behavior of the Weyl-law inverse.

For Theorem 2, the analogous loss is a $q^{4\kappa}$ Markov-type loss at the Proposition 4.1/4.2 level. This is a second-derivative analogue of the trace-side interpolation cost and belongs to the eight-word statistic. Theorem 2 also has losses absent from Theorem 1: the primitive-power diagonal subtraction, the fiber union bound, and the conversion from local mass to pointwise $L^\infty$ control.

The resulting loss map is:

| Loss source | Location | Meaning |
|---|---|---|
| $q^{2\kappa}$ | Proposition 3.1 | Markov interpolation loss on the trace side |
| $m=\kappa+3+K$ | Theorem 1 smoothing | Derivative order needed for the smooth cutoff |
| $\alpha_W\to\alpha_R$ | Weyl inversion | Edge loss near $\lambda=1/4$ |
| $q^{4\kappa}$ | Propositions 4.1 and 4.2 | Markov second-derivative loss in the pre-trace fourth moment |
| Fiber union | Theorem 2 probability conversion | Union bound over fibers |
| $\Lambda_0^{3/2}$ | Theorem 2 final bound | Local-mass-to-$L^\infty$ conversion |

This accounting became the basis for the extension search. It singled out the Markov/interpolation step as the most concrete bottleneck, while avoiding the false conclusion that Theorem 2 is merely a repetition of Theorem 1.

## 3. Finite Permutation and Schreier-Graph Test Cases

After reconstructing the proof ledger, the run built finite toy models for the random permutation mechanisms suggested by the proof. These are not hyperbolic surface theorems. They are finite independent-permutation and Schreier-operator benchmarks.

### 3.1 Common Fixed Points and Folded Templates

The first benchmark counted common fixed points of reduced words in random permutations. It supported the diagonal-subtraction intuition in a toy setting: cyclic primitive-power families had order-one common fixed-point counts, while the rank-two pair $(a,b)$ was much smaller, near scale $1/n$.

The same experiment exposed a limitation. Adding composite words such as $ab$ and $aB$ to a pointwise common fixed set can impose the same constraints as fixing $a$ and $b$. Thus naive multiword intersections do not faithfully model Kim--Tao's eight-word folded-graph mechanism.

The second benchmark added folded trajectory quotient profiles. This separated cyclic or rank-one word families from rank-two or noncyclic families before sampling. It explained the first benchmark's limitation: the quotient structure must be tracked explicitly before choosing a Monte Carlo observable.

The third benchmark counted injective labelled-graph embeddings directly. For a labelled directed graph $H$, the observable counts injective maps from the vertices of $H$ into $[n]$ such that every labelled edge is realized by the corresponding random permutation or inverse. This made rank-two eight-word templates measurable. At $n=400$, the cyclic eight-word toy template stayed normalized near one, while the rank-two eight-word toy template had raw scale near $n^{-1}$ and normalized count near one. In this toy model, much of the cyclic/rank-two separation is explained by constraint dimension.

### 3.2 Polynomial Fits and Interpolation Conditioning

The fourth benchmark fitted normalized embedding counts as functions of $x=1/n$. Degree-3 Chebyshev-window fits were accepted as the current low-noise benchmark for the cyclic and rank-two eight-word templates. Deliberately underdetermined degree-6 and degree-8 fits showed large derivative and coefficient growth. This illustrates Markov-type interpolation conditioning in a toy model. It is not the actual MPvH/MP23 polynomial and not a hyperbolic trace statistic.

### 3.3 The Two-Generator Schreier Operator

The fifth benchmark introduced a two-generator Schreier operator. For two independent random permutations $a,b$, define

$$
A=P_a+P_a^T+P_b+P_b^T.
$$

Loops and multiple edges are retained, so every row sum is exactly four. Coarse normalized adjacency-window counts were stable across $n=100,200,400,800$. Centered trace moments decreased after subtracting the moments of the infinite 4-regular tree. This supports the trace-formula analogy that deterministic tree-like or backtracking terms should be separated before studying fluctuations.

The same experiment found that degree-3 polynomial fits did not automatically transfer from low-noise labelled-template data to spectral-window data on a four-size grid. Degree-1 fits were more stable for smooth spectral windows.

Together these five tests support the following finite-model conclusions:

- cyclic or rank-one contributions remain order one in raw fixed-point and quotient observables;
- rank-two or noncyclic constraints are suppressed before normalization;
- direct labelled-template embeddings explain much of that suppression by constraint dimension;
- low-degree polynomial fits can be stable for low-noise normalized embedding observables;
- high-degree fits reveal derivative and coefficient amplification;
- Schreier spectral windows provide an operator-level toy analogue, but interpolation is fragile when the data grid is too small.

### 3.4 Certified Finite Expectation Identity

The first formal-certification component proved the exact finite identity behind the labelled-template embedding benchmark. For a labelled directed template $H$,

$$
\mathbf E\,\mathrm{InjEmb}_n(H)
=
(n)_{|V|}
\prod_a\frac{1}{(n)_{|C_a(H)|}},
$$

provided each normalized label constraint set $C_a(H)$ is a partial injection and $n\ge |V|$. If a constraint set is not a partial injection, or if $n<|V|$, the expectation is zero. Inverse-labelled edges are normalized by reversing orientation before forming forward constraints.

Wolfram symbolic checks and Python exhaustive enumeration over small symmetric groups agreed with the formula, including a repaired inverse-label regression case.

This certifies a narrow finite combinatorial mechanism. It does not certify the Selberg trace formula, the Kim--Tao trace expansion, or the imported MPvH/Nau/MP23 inputs. Its value is that it gives the later extension search a reliable finite benchmark identity.

## 4. Product-Ratio Stability and Its Boundary

The extension search began at the Markov/interpolation bottleneck. The question was whether the derivative amplification is an artifact of reconstructing a polynomial from sparse reciprocal-$n$ data, or whether it reflects real analytic behavior of the families appearing in the trace expansion.

The finite labelled-template identity gives a controlled test case. For a conflict-free labelled template with $V$ vertices and per-label constraint counts $C_a$, the normalized expectation is

$$
N_H(n)=n^{C-V}\frac{(n)_V}{\prod_a (n)_{C_a}},
\qquad C=\sum_a C_a.
$$

After substituting $x=1/n$, this becomes a finite product ratio:

$$
N_H(x)=\frac{\prod_{j\in A_H}(1-jx)}{\prod_{j\in B_H}(1-jx)}.
$$

For fixed templates, this function is analytic at $x=0$, and its low-order Taylor expansion can be computed exactly. For example, the key rank-two benchmark has the exact normalized form

$$
N_H(n)=n\frac{(n)_7}{(n)_4^2}
=\frac{(n-6)(n-5)(n-4)}{(n-1)(n-2)(n-3)}.
$$

Its order-four expansion matched both symbolic and Python checks. High-degree sparse-grid fits were much less stable. Thus sparse-grid interpolation can be ill-conditioned even when the fixed-template expectation is itself well behaved.

The same product-ratio framework also explains why fixed-template stability does not remove the Kim--Tao bottleneck. If the template support or constraint profile grows with a size parameter $L$, the zeros and poles of the falling-factorial factors move toward $x=0$ at scale $1/L$. The logarithmic expansion

$$
\log N_L(x)
=\sum_{r\ge1}
\frac{\sum_{b\in B_L} b^r-\sum_{a\in A_L} a^r}{r}x^r
$$

shows why fixed-order coefficients and derivatives can grow rapidly when the factor indices are $O(L)$.

This led to the following toy lemma. If

$$
N_L(x)=\frac{\prod_{a\in A_L}(1-ax)}{\prod_{b\in B_L}(1-bx)},
\qquad
\max(A_L\cup B_L)\le C_0L,\quad |A_L|+|B_L|\le C_1L,
$$

then fixed-order coefficients satisfy a crude bound

$$
|[x^k]N_L(x)|\le D_kL^{2k},
\qquad
|N_L^{(k)}(0)|\le k!D_kL^{2k}.
$$

This is a deterministic statement for normalized independent-permutation product ratios. It does not improve the Kim--Tao rigidity exponent, replace MPvH/Witten-zeta/Nau/MP23 estimates, or control a surface-group quotient-family sum. It isolates a clean principle: fixed conflict-free labelled templates are stable after normalization, while growing support or profile size can reintroduce the derivative amplification that the Markov step pays for.

## 5. Aggregate Control: Why Termwise Bounds Are Not Enough

The next question was whether termwise product-ratio control could be promoted to a Kim--Tao trace or pre-trace estimate. The answer was no, at least not without an additional input.

The product-ratio framework exactly describes the independent-permutation labelled-template baseline. Kim--Tao random covers instead average over homomorphisms from the surface group $\Gamma$ into $S_n$. That law includes surface relations, denominator normalization, Witten-zeta and homomorphism-count asymptotics, Nau boundedness, MP23 rank-two inputs, geometry weights, centering, and sums over quotient families. The product-ratio structure is visible, but it is not the full probability law.

The obstruction is elementary. If templates satisfy termwise bounds such as

$$
|[x^k]N_T(x)|\le C_kL^{2k},
$$

then a weighted aggregate

$$
A_L(x)=\sum_T w_TN_T(x)
$$

only satisfies

$$
|[x^k]A_L(x)|
\le C_kL^{2k}\sum_T|w_T|.
$$

The new factor is total variation: the sum of the absolute weights. Without a separate bound on family count, weight mass, rank-sensitive decay, or cancellation, per-template control does not become an aggregate theorem.

A restricted folded two-word model made this concrete. Folding and canonicalization reduced raw ordered-pair complexity, but conflict-free canonical profiles and their multiplicities still grew quickly even at small word length. Trace-like refinements helped: using cyclically reduced conjugacy representatives, tracking primitive and diagonal/cyclic classes, and adding length weights reduced total variation in the toy model. But this was still total-variation accounting, not a proof of cancellation.

The surviving theorem template had to be stratified by

$$
d=C-V.
$$

For a template $T$,

$$
E_T(n)=n^{d_T}R_T(1/n).
$$

Different values of $d_T$ carry different powers of $n$, so they cannot be merged into one coefficient sum without changing the meaning of the estimate. In a fixed stratum

$$
F_{L,d}=\{T:d_T=d\},
\qquad
TV_{L,d}=\sum_{T\in F_{L,d}}|w_T|,
$$

the accepted template was

$$
\left|[n^{d-k}]\sum_{T\in F_{L,d}}w_TE_T(n)\right|
\le C_kL^{2k}TV_{L,d}.
$$

This is a useful finite theorem template, but it emphasizes the missing input rather than removing it.

The cancellation diagnostics tested whether the missing input might be sign cancellation in the trace-like toy family. The dominant unweighted $d=1$ rank-two/noncyclic stratum at length cutoff $L=5$ showed no order-one cancellation: the signed sum and coefficient absolute variation were both $800$ in magnitude. Higher orders showed partial cancellation, but not in a stable way; finer structural groupings made the apparent cancellation disappear. Length weights improved the scale by lowering weighted total variation, but did not create sign cancellation.

The external-decay analysis then estimated how strong an outside input would need to be. In the dominant toy stratum, rank-only decay did not help because all surviving records had the same rank proxy. Polynomial length and folded-complexity decay required large exponents. Exponential length decay was the strongest tested axis, but even that required coefficient-variation decay far stronger than bare rank filtering.

For the actual Kim--Tao proof, this means that a theorem-level extension would need one of the following inputs for the true surface-group quotient families:

- polynomial total variation within fixed $d=C-V$ strata;
- rank-sensitive or probability-law decay beyond the toy product-ratio bound;
- coefficient-variation control for the numerator coefficients;
- signed cancellation that survives the true surface-group organization;
- a different surface-level estimate that bypasses total-variation bounds.

Larger independent-permutation enumerations are unlikely to change this conclusion unless they are tied directly to the actual surface-group numerator.

## 6. Local Spectral Windows and the Compact-Support Obstruction

The second extension strategy asked whether Kim--Tao's global rigidity and Weyl estimates imply local spectral statistics.

The first answer is endpoint subtraction. If

$$
F(\Lambda)=\int_0^{\sqrt{\Lambda-1/4}}r\tanh(\pi r)\,dr,
$$

then the reconstructed Weyl law gives

$$
N_{X_n}([1/4,\Lambda])
=(2g-2)nF(\Lambda)
+O\!\left(n^{1-\alpha_W}\Lambda^{1/2+\epsilon}\right).
$$

Subtracting this estimate at $\Lambda+\Delta$ and $\Lambda$ gives

$$
N_{X_n}([\Lambda,\Lambda+\Delta])
=(2g-2)n\bigl(F(\Lambda+\Delta)-F(\Lambda)\bigr)
+O\!\left(n^{1-\alpha_W}(\Lambda+\Delta)^{1/2+\epsilon}\right).
$$

This is valid but useful only when the local main term is larger than the inherited endpoint error. In the bulk, the window width must exceed a global-error scale. At the edge, where $F'(1/4)=0$ and

$$
F(1/4+\Delta)-F(1/4)
=\frac{\pi}{3}\Delta^{3/2}+O(\Delta^{5/2}),
$$

the threshold changes but still remains far above mean spacing for the relevant exponents. Rigidity gives a deterministic window-inclusion statement, but again only at scales larger than the rigidity displacement. It does not give microscopic multiplicity control.

The run then considered smoothed local statistics. For a smoothed window of width $\Delta=n^{-d}$, define

$$
Z_n(\phi;\Lambda,\Delta)
=
\sum_j\phi\left(\frac{\lambda_j(X_n)-\Lambda}{\Delta}\right)
-\operatorname{main}_n(\phi;\Lambda,\Delta).
$$

In the bulk, the expected main term has size $n\Delta$. If

$$
\operatorname{Var}Z_n\le n^v,
$$

then Chebyshev gives relative control when

$$
\frac v2<1-d.
$$

To improve on endpoint subtraction, the same window must also satisfy $d>\alpha_W$ in the bulk. This identifies the variance estimate that would be needed for a true local-window theorem.

The existing Kim--Tao compact-support architecture does not supply this variance estimate simply by retuning parameters. In the paper's setup, a polynomial degree parameter $q$ also controls geometric support:

$$
\operatorname{supp}((h\circ f_{\Lambda_0})^\vee)
\subset
[-c_0\Lambda_0^{-1/2}q,\;c_0\Lambda_0^{-1/2}q].
$$

Resolving a $\lambda$-window requires inverse-width localization in the spectral parameter $r$:

$$
\delta_r
=\sqrt{\Lambda+\Delta-1/4}-\sqrt{\Lambda-1/4}.
$$

At fixed bulk energy, $\delta_r\sim \Delta/(2\sqrt{\Lambda-1/4})$; at the edge it scales as $\sqrt{\Delta}$. Thus polynomially shrinking windows force polynomially growing geometric support. The trace side then pays the known $q^{2\kappa}$ Markov loss, and the pre-trace side pays the larger $q^{4\kappa}$ loss.

Fourier scaling closes another possible escape route inside compact support. If

$$
\widehat{h_\delta}(t)
=\delta e^{-ir_0t}\widehat{\phi}(\delta t),
$$

then truncating the geometric side to $|t|\le R$ loses the tail

$$
\int_{|u|>R\delta}|\widehat{\phi}(u)|\,du.
$$

Fixed-quality localization requires $R\delta$ bounded below, and small leakage requires $R\delta\to\infty$. Hence logarithmic support cannot resolve a polynomially shrinking bulk window. Polynomial support $R=n^\eta$ must satisfy $\eta\ge d$ in the bulk and $\eta\ge d/2$ at the edge.

This led to a long-support theorem template. At fixed energy, on the trace side, the missing variance estimate was stated as

$$
\operatorname{Var}Z_n(h_{\Lambda_0,\Delta,q})
\le C n^{1+2\kappa\eta-\beta+\epsilon},
\qquad q=n^\eta.
$$

Relative bulk control would require

$$
\beta>2\kappa\eta+2d-1.
$$

The pre-trace analogue is less plausible because the corresponding loss scale is $4\kappa\eta$.

The trace-side strategy was narrowed to the localized Corollary 3.4 numerator

$$
p_{\Delta,q}(x)
=
\sum_{\gamma_1,\gamma_2}\sum_{k_1,k_2\ge1}
a(\gamma_1,k_1)a(\gamma_2,k_2)
h_{\Delta,q}^{\vee}(k_1\ell_{\gamma_1})
h_{\Delta,q}^{\vee}(k_2\ell_{\gamma_2})
Q_{\gamma_1^{k_1},\gamma_2^{k_2}}(x),
$$

where

$$
a(\gamma,k)=\frac{\ell_\gamma}{2\sinh(k\ell_\gamma/2)}.
$$

The localized numerator proxy model made this target inspectable but did not prove the needed estimate. It generated 4,800 proxy rows while separating exact paper indices and weights from modelling annotations such as quotient type, rank proxy, cyclic status, and $d=C-V$ stratum.

The conclusion is negative but useful. No local spectral-statistics theorem was proved. What was proved is the shape of the obstruction and the form of the theorem target needed to go beyond it:

$$
\frac{p_{\Delta,q}(1/n)}{Q_{\mathrm{id}}(1/n)}
\le n q^A n^{-\sigma+o(1)}
$$

with parameters strong enough to meet the trace-side saving condition. Alternatively, one would need a genuinely new noncompact trace-tail architecture with controlled spectral localization, geometric convergence, truncation, and tail bounds strong enough to beat geodesic and quotient-family growth.

## 7. Direct Consequences of the Reconstructed Theorems

After the local-window strategy was set aside as a follow-up problem, the run extracted consequences that follow directly from Kim--Tao's reconstructed theorems.

### 7.1 Multiplicity and Spectral Clusters

Let $\mu_j$ denote random-cover eigenvalues and $\lambda_j$ the deterministic reference locations. If, on the high-probability rigidity event,

$$
|\mu_j-\lambda_j|\le R_j,
$$

then every random cluster in an interval $I$ must come from deterministic reference locations in the expanded interval. With a uniform radius $R$,

$$
\#\{j:\mu_j\in I\}
\le
\#\{j:\lambda_j\in I^{+R}\}.
$$

For a single point this gives the multiplicity envelope

$$
\operatorname{mult}_{X_n}(\lambda)
\le
\#\{j:|\lambda_j-\lambda|\le R\}.
$$

In the Kim--Tao theorem-level regime,

$$
R=C_\epsilon \Lambda_{\max}^{1/2+\epsilon}n^{-\alpha_R}.
$$

The deterministic reference locations are described by

$$
F(\lambda_j)=\frac{j}{(2g-2)n},
\qquad
F(\Lambda)=\int_0^{\sqrt{\Lambda-1/4}}r\tanh(\pi r)\,dr.
$$

In the fixed bulk, this gives the multiplicity scale

$$
O(n^{1-\alpha_R}\lambda^{1/2+\epsilon})
$$

up to fixed-energy constants. At the spectral edge, the correct density comes from

$$
F(1/4+\Delta)=\frac{\pi}{3}\Delta^{3/2}+O(\Delta^{5/2}),
$$

and the edge cluster envelope is

$$
O\bigl(n(\Delta+R)^{3/2}\bigr).
$$

This is a transport corollary from rigidity. It does not prove simplicity, level repulsion, microscopic spacing laws, or endpoint-beating counts.

### 7.2 Mass Distribution from Theorem 2

Theorem 2 also gives deterministic mass-distribution consequences. If $u$ is $L^2$-normalized, $\lambda\le\Lambda$, and

$$
\|u\|_\infty\le M_{\Lambda,n},
$$

then for $2\le p\le\infty$,

$$
\|u\|_p
\le
\|u\|_\infty^{1-2/p}\|u\|_2^{2/p}
\le
M_{\Lambda,n}^{1-2/p}.
$$

The same bound gives, for every measurable set $A$,

$$
\int_A |u|^2
\le
\|u\|_\infty^2\operatorname{vol}(A)
\le
M_{\Lambda,n}^2\operatorname{vol}(A).
$$

If a set $E$ carries mass $\theta$, then

$$
\operatorname{vol}(E)\ge \theta M_{\Lambda,n}^{-2}.
$$

With the direct Theorem 2 envelope

$$
M_{\Lambda,n}=C\Lambda^{3/2}n^{-\alpha},
$$

fixed-energy eigenfunctions cannot concentrate positive mass on sets of volume $o(n^{2\alpha})$, up to constants. This is polynomial-scale delocalization in the cover degree. It is not quantum ergodicity or equidistribution.

One can also read a stronger fixed-cutoff statement from an earlier point in the Theorem 2 proof. Before the final Sobolev and elliptic conversion to $L^\infty$, the pre-trace argument controls a fixed-cutoff local $L^2$ mass statistic. With probability at least $1-n^{-1/10}$, for the smooth nonnegative base cutoff $a$ used in the proof, every fiber $i$, and all normalized eigenfunctions below the relevant energy,

$$
\int_{\mathbb H} a(z)\,|u_j^\rho(z,i)|^2\,d\operatorname{Vol}(z)
\le
C\Lambda_0 n^{-\alpha_0},
\qquad
\alpha_0=\frac{1}{16(2\kappa+11)}.
$$

This has better $\Lambda_0$ bookkeeping than the final sup-norm-derived mass envelope, because the final conversion introduces an additional $\Lambda_0^2$ factor at the squared-mass level. The statement is only for the fixed cutoff. It does not imply lower mass bounds, arbitrary ball estimates, or spatial equidistribution.

### 7.3 Fixed Positive-Width Spectral Windows

The reconstructed Weyl law gives, on the high-probability event,

$$
N_{X_n}([1/4,\Lambda])
=
(2g-2)nF(\Lambda)
+O_\epsilon(n^{1-\alpha_W}\Lambda^{1/2+\epsilon}).
$$

For a fixed interval $I=[a,b]$ with $1/4\le a<b$, subtracting endpoint estimates gives

$$
N_{X_n}([a,b])
=
(2g-2)n(F(b)-F(a))
+O_\epsilon(n^{1-\alpha_W}b^{1/2+\epsilon}).
$$

Since $F(b)-F(a)>0$ for fixed positive-width windows, the main term is order $n$, and the relative error is $O(n^{-\alpha_W})$ after fixing $a,b,g$, and $\epsilon$. The centered version is

$$
N_{X_n}([a,b])-(2g-2)n(F(b)-F(a))
=
O_\epsilon(n^{1-\alpha_W}b^{1/2+\epsilon}).
$$

At the edge, a fixed interval $[1/4,1/4+\Delta]$ still has an order-$n$ main term through

$$
F(1/4+\Delta)-F(1/4)
=
\frac{\pi}{3}\Delta^{3/2}+O(\Delta^{5/2})
$$

for fixed $\Delta>0$. Shrinking windows $\Delta=n^{-d}$ fall outside this corollary and return to the local-window obstruction. The fixed-window result is a macroscopic count asymptotic with polynomial relative error, not a variance asymptotic, limiting law, level-repulsion theorem, or universality result.

## 8. Standalone Schreier Benchmark Theorem

The strongest finite-model output is a theorem for a two-permutation Schreier graph. This result is useful because it gives a complete trace-method pattern in a model where the combinatorics are much simpler than in the hyperbolic surface problem.

Let $P_a$ and $P_b$ be independent uniform permutations of $[n]$, and define

$$
A_n=P_a+P_a^{-1}+P_b+P_b^{-1}.
$$

This is the adjacency operator of a two-generator Schreier graph, allowing loops and multiple edges. Its row sum is $4$. For fixed $k\ge0$,

$$
\operatorname{Tr}(A_n^k)
=
\sum_{w\in\{a,a^{-1},b,b^{-1}\}^k}
\operatorname{Fix}(w(P_a,P_b)).
$$

Words that freely reduce to the identity contribute $\operatorname{Fix}(w)=n$ deterministically. Their count is the $k$th closed-walk moment $m_k$ of the infinite 4-regular tree. The theorem package states that, for every fixed $k$,

$$
\mathbb E\bigl[n^{-1}\operatorname{Tr}(A_n^k)\bigr]
=
m_k+O_k(n^{-1}),
$$

and

$$
\operatorname{Var}\bigl(n^{-1}\operatorname{Tr}(A_n^k)\bigr)
=
O_k(n^{-2}).
$$

The expectation statement separates identity words from nontrivial reduced words. A fixed nontrivial reduced word has $O_k(1)$ expected fixed points; after normalization by $n$, the total contribution is $O_k(n^{-1})$.

For the variance,

$$
\operatorname{Var}\bigl(n^{-1}\operatorname{Tr}(A_n^k)\bigr)
=
n^{-2}
\sum_{u,v}
\operatorname{Cov}(\operatorname{Fix}(u),\operatorname{Fix}(v)).
$$

Identity words are deterministic after subtracting the tree-word contribution, so they contribute no covariance. The remaining task is the fixed-pair covariance bound

$$
\operatorname{Cov}(\operatorname{Fix}(u(P_a,P_b)),\operatorname{Fix}(v(P_a,P_b)))
=
O_{u,v}(1)
$$

for nontrivial reduced words $u,v$.

The proof uses the labelled-template expectation identity from the finite permutation tests. A conflict-free quotient template $H$ has $V(H)$ quotient vertices and $C_a(H),C_b(H)$ distinct directed constraints for the two labels. Its leading exponent is controlled by

$$
V(H)-C_a(H)-C_b(H).
$$

After cyclic reduction, each edge-containing quotient component contains a nonempty closed labelled trajectory. Every quotient vertex in such a trajectory has at least one outgoing labelled constraint, so

$$
C_a(H)+C_b(H)\ge V(H),
$$

and therefore

$$
V(H)-C_a(H)-C_b(H)\le0.
$$

Templates with partial-injection conflicts contribute zero. Equal, inverse, cyclic-conjugate, and shared-power word pairs can change constants but not this exponent. Thus the covariance is $O_{u,v}(1)$ for every fixed nontrivial reduced pair. Since there are finitely many length-$k$ words, the normalized variance is $O_k(n^{-2})$.

This theorem also explains the numerical behavior observed earlier. Low even moments showed centered-variance slopes near $-1.7$ over accessible $n$, but the template argument found no positive-power covariance obstruction. The interpretation is finite-size crossover toward the theorem-order $n^{-2}$ decay, not evidence for an $n^{-1}$ limiting covariance law.

The scope boundary is important. This is a finite independent-permutation theorem. It does not prove a Kim--Tao hyperbolic-cover theorem, a Selberg trace transfer, a surface-group quotient-family estimate, an adjacency-to-Laplacian theorem, or shrinking-window spectral statistics. The analogy is structural: both settings expand trace statistics, separate deterministic or diagonal terms, and reduce fluctuation estimates to fixed-point or quotient-template counting. The analogy stops before transfer because the Kim--Tao model includes surface-group relations, hyperbolic geodesic weights, Selberg and pre-trace inputs, denominator normalization, and external quotient-family estimates.

## 9. The Corollary 3.4 Numerator Bottleneck

The final extension attempt returned to the compact-support trace statistic in Kim--Tao's proof. Its goal was to state exactly what theorem would be needed to improve the visible $q^{2\kappa}$ loss in Proposition 3.1.

The central object is

$$
\frac{p(1/n)}{Q_{\mathrm{id}}(1/n)}.
$$

In the reconstructed form, the numerator is the Selberg-weighted aggregate

$$
p(x)
=
\sum_{\gamma_1,\gamma_2}\sum_{k_1,k_2\ge1}
\frac{\ell_{\gamma_1}\ell_{\gamma_2}}
{4\sinh(k_1\ell_{\gamma_1}/2)\sinh(k_2\ell_{\gamma_2}/2)}
(h\circ f_{\Lambda_0})^\vee(k_1\ell_{\gamma_1})
(h\circ f_{\Lambda_0})^\vee(k_2\ell_{\gamma_2})
Q_{\gamma_1^{k_1},\gamma_2^{k_2}}(x).
$$

Corollary 3.4 expresses the second moment as

$$
\mathbb E[G_n(h)^2]
=
\frac{p(1/n)}{Q_{\mathrm{id}}(1/n)}
+O\!\left(\Lambda_0(Cq)^{\kappa q}n^{-q}\|\widetilde h\|^2\right),
$$

with

$$
\deg p\le C\Lambda_0^{-1/2}q,
\qquad
Q_{\mathrm{id}}(1/n)\in[C^{-1},C]
$$

in the paper's working range. The denominator bound matters: any improved theorem for $p(1/n)$ must survive division by $Q_{\mathrm{id}}(1/n)$.

The loss localization is precise. The paper first obtains reciprocal-integer control

$$
n^{-2}|p(1/n)|
\le
C\Lambda_0^{20}\|\widetilde h\|^2.
$$

The corrected energy factor is $\Lambda_0^{20}$. The visible $q^{2\kappa}$ loss enters later, when the proof applies Markov brothers' inequality to

$$
P(x)=x^2p(x).
$$

Derivative control for $P$ over the reciprocal-integer range produces the $q^{2\kappa}$ scale. Taylor expansion from $x=0$ transfers that derivative control back to $x=1/n$. Thus the current loss is an interpolation loss, not a loss forced by the definition of the numerator.

This motivates the direct small-$x$ target

$$
\left|\frac{p(1/n)}{Q_{\mathrm{id}}(1/n)}\right|
\le
C n\Lambda_0^{20}\|\widetilde h\|^2 q^A n^{-\sigma+o(1)}.
$$

The Markov baseline corresponds to

$$
A=2\kappa,
\qquad
\sigma=0.
$$

If denominator loss is modelled by

$$
|Q_{\mathrm{id}}(1/n)|^{-1}\le n^D,
$$

then the effective saving in the long-support budget is

$$
\beta=(2\kappa-A)\eta+\sigma-D.
$$

In the paper-safe denominator range, $D=0$. Outside that range, denominator near-zeros can erase any numerator saving.

The direct small-$x$ route is distinct from coefficient variation because it controls a single evaluated value rather than every coefficient. That distinction matters only if the proof uses signed cancellation at the actual point $x=1/n$. If the proof expands the numerator and bounds

$$
\sum_i |w_i Q_i(1/n)|
$$

inside fixed quotient, length, primitive-power, or kernel strata, then it is effectively a coefficient-variation or absolute-variation proof.

The signed pointwise target was therefore named

$$
\mathrm{SPC}(A,\sigma):\quad
\left|\frac{p(1/n)}{Q_{\mathrm{id}}(1/n)}\right|
\le
C n\Lambda_0^{20}\|\widetilde h\|^2q^A n^{-\sigma+o(1)}.
$$

The possible signs in this aggregate come from transform values and from the evaluated quotient-polynomial values. The Selberg length denominator is positive. Cancellation at $x=0$, cancellation at reciprocal points outside the needed range, or cancellation in an independent-permutation toy model does not control the required ratio. The true question is whether the weighted surface aggregate cancels at $x=1/n$ after denominator normalization.

## 10. Surface-Group Organization and the Current Pivot

The last part of the run translated the signed pointwise question into a question about the actual surface-group objects in Kim--Tao's Lemma 3.3 and Corollary 3.4.

The normalized summand has the form

$$
w(\gamma_1,k_1)w(\gamma_2,k_2)
\frac{Q_{\gamma_1^{k_1},\gamma_2^{k_2}}(1/n)}
{Q_{\mathrm{id}}(1/n)},
$$

where

$$
w(\gamma,k)
=
\frac{\ell_\gamma}{2\sinh(k\ell_\gamma/2)}
(h\circ f_{\Lambda_0})^\vee(k\ell_\gamma).
$$

For a grouping $G$, the signed pointwise theorem template is

$$
\mathrm{SPC}_G(A,\sigma):\quad
\left|
\sum_{i\in G}
w_i\frac{Q_i(1/n)}{Q_{\mathrm{id}}(1/n)}
\right|
\le
C n\Lambda_0^{20}\|\widetilde h\|^2q^A n^{-\sigma+o(1)}.
$$

The same exponent bookkeeping applies:

$$
\beta=(2\kappa-A)\eta+\sigma-D.
$$

Several possible groupings were considered. The Markov interpolation route is the baseline proved in the paper. Two conditional targets survived as plausible directions: grouping by surface-relation kernel structure and grouping by length-shell transform phase. Quotient-complex profile, diagonal/off-diagonal relation balance, and primitive-power profile are visible in the surface aggregate, but no validated theorem currently supplies cancellation for them. Absolute fixed-stratum controls are coefficient-variation estimates in substance.

The strongest surviving direct target was grouping by the surface-relation kernel. This is native to the paper because Kim--Tao's Lemma 3.3 uses folded quotient objects with the condition

$$
\text{every path in }W_r\text{ spelling an element of }
\ker(F_{2g}\to\Gamma)\text{ is closed.}
$$

The run found that this condition is not yet a theorem-ready cancellation mechanism. Kernel closure is an admissibility and structure condition for quotient targets before embedding expectations, polynomial contributions, and evaluated quotient ratios are formed. By itself, it does not provide opposite signs, orthogonality, or a pairing among the evaluated values

$$
Q_i(1/n).
$$

Two kernel-related possibilities remain conditional: signed pairing within kernel classes and sign grouping of quotient polynomials. Either would become a genuine signed pointwise theorem if a new argument proved cancellation of evaluated $Q_i(1/n)$ values across relation-kernel classes. No such argument was found in the reconstructed Lemma 3.3 input.

Thus the current mathematical pivot is:

$$
\text{prove coefficient variation or signed variation for }
\frac{p(1/n)}{Q_{\mathrm{id}}(1/n)}
\text{ in the actual Kim--Tao surface aggregate.}
$$

The run did not prove an improved rigidity exponent, a variance law, a shrinking-window theorem, level repulsion, local universality, or a Schreier-to-surface transfer. It refined the bottleneck map until the next useful theorem target could be stated without conflating surface geometry with toy permutation models.

## 11. Evidence Status and Remaining Record-Keeping Issues

The final audit headline was:

```text
76 validated, 1 in-progress; findings CRITICAL=1 MODERATE=1; promise_check=green
```

This supports treating the proof reconstruction, finite probes, theorem corollaries, Schreier benchmark, local-window obstruction, and surface-numerator bottleneck as the main validated outputs of the run, subject to the confidence levels recorded in the audit summary.

The remaining issues are about evidence hygiene, not mathematical disproof.

The moderate issue concerned the final synthesis milestone. A ledger event referred to a missing path:

```text
reports/final/final_report.md
```

The final reporter later regenerated that file.

The critical issue concerned the M36 direct small-$x$ surface numerator target. The plan success criteria referenced the text

```text
p(1/n)/Q_id(1/n)
```

as if it were an artifact reference. The substantive M36 analysis was still reported as validated. The issue is that the success criterion pointed to text rather than to a concrete artifact path. This should be read as a traceability defect, not as a contradiction of the M36 theorem target.

The record-keeping follow-ups are:

1. Ensure `reports/final/final_report.md` is listed in the final artifact index.
2. Correct the latest M6 ledger artifact references to point to existing final package artifacts.
3. Rerun `promise_check` and artifact-reference checks.

These are separate from the mathematical follow-up. The mathematical follow-up is the surface numerator problem described above.

## 12. Conclusions

The run produced a clear map of the Kim--Tao proof and its bottlenecks.

The global eigenvalue-rigidity theorem goes through:

1. the Selberg trace formula;
2. a two-trace second moment;
3. Corollary 3.4 polynomialization;
4. Markov brothers interpolation;
5. high-probability Weyl-law conversion;
6. Weyl inversion.

The eigenfunction-delocalization theorem goes through:

1. a pre-trace fourth-moment argument;
2. primitive-power diagonal subtraction;
3. an eight-word folded-graph estimate;
4. a separate $q^{4\kappa}$ interpolation scale;
5. probability conversion;
6. Sobolev and elliptic conversion to pointwise bounds.

The reconstruction identifies the Markov/interpolation step as a visible loss, while keeping it separate from smoothing, union-bound, edge-inversion, and Sobolev-conversion losses.

The finite-model work is useful but bounded. The labelled-template expectation identity is certified for independent random permutations. Product-ratio bounds explain why fixed templates are stable while growing profiles can recover derivative amplification. The Schreier benchmark proves

$$
\mathbb E[n^{-1}\operatorname{Tr}(A_n^k)]=m_k+O_k(n^{-1})
$$

and

$$
\operatorname{Var}(n^{-1}\operatorname{Tr}(A_n^k))=O_k(n^{-2})
$$

for fixed trace moments of the two-permutation operator. These are publication-facing finite benchmarks, but they do not automatically transfer to random hyperbolic covers because the surface model has relations, geodesic weights, denominator normalization, and imported quotient-family estimates.

The extension search narrowed the surface problem rather than solving it. Endpoint subtraction gives fixed positive-width window counts but not shrinking local statistics. Compactly supported trace tests for polynomially shrinking windows force long support and return to a localized Corollary 3.4 numerator estimate. Transform damping and surface-relation kernel grouping did not produce a theorem-ready cancellation mechanism.

The best anchored mathematical follow-up is therefore a coefficient-variation or signed-variation theorem for the actual surface numerator

$$
\frac{p(1/n)}{Q_{\mathrm{id}}(1/n)}.
$$

A direct signed pointwise theorem would need cancellation at $x=1/n$ after denominator normalization. An absolute-stratum proof would instead be coefficient variation in substance. Length-shell transform-phase grouping remains a secondary conditional direction. Surface-relation kernel closure is structurally important in the paper, but current evidence treats it as admissibility rather than as sign pairing or orthogonality.

The evidence-hygiene follow-up is separate: make sure the final report is indexed, correct stale artifact references, and rerun the artifact checks.

## References

[1] Elena Kim and Zhongkai Tao, *Eigenvalue rigidity of hyperbolic surfaces in the random cover model*, local files `2603.01127.pdf` and `2603.01127.txt`.

[2] Cycle reports \path{reports/cycles/report_cycles_1-3.md} through \path{reports/cycles/report_cycles_49-50.md}, which contain the proof reconstruction, computational probes, extension-search reports, theorem templates, and surface-bottleneck analyses summarized here.

[3] `MANIFEST.md`, workspace inventory after cycles 49-50, listing scripts, tests, datasets, figures, proof ledgers, reports, and final artifacts used by the run.

[4] Final audit summary for run \path{run-2026-05-15T153635Z}, reporting milestone status distribution, findings, residual debt, and future-work anchors.

## Implementation and Evidence Appendix

The synthesis cites result classes rather than every generated CSV or figure. The main reproducibility scripts are in the `scripts/` directory:

| Result class | Script basename |
|---|---|
| Labelled-template expectation identity | \path{certify_labelled_embedding_expectation.py} |
| Fixed-template and growing-template product-ratio bounds | \path{analyze_product_ratio_bounds.py} |
| Local-window obstruction and strategy choice | \path{build_local_window_route_synthesis.py} |
| Standalone Schreier benchmark theorem package | \path{build_schreier_benchmark_package.py} |
| Corollary 3.4 numerator reconstruction and Markov-loss localization | \path{analyze_surface_corollary34_numerator_obstruction.py} |
| Direct small-$x$ target and denominator-loss budget | \path{analyze_direct_small_x_surface_numerator_target.py} |
| Signed pointwise cancellation classification | \path{analyze_signed_pointwise_cancellation_surface_aggregate.py} |
| Surface-group organization taxonomy | \path{analyze_surface_native_grouping_problem.py} |
| Kernel-closure signed-cancellation probe and current pivot | \path{analyze_surface_relation_kernel_spc_probe.py} |

## Terminology Appendix

This appendix explains recurring terms that are useful in the report but may not be standard outside this run.

**Coefficient variation.** A bound on the sum of absolute coefficient contributions after expanding a numerator or polynomial family. It is stronger than controlling each individual template, because the number and weights of templates also matter.

**Denominator-normalized numerator.** The evaluated ratio

$$
\frac{p(1/n)}{Q_{\mathrm{id}}(1/n)}
$$

from Kim--Tao's Corollary 3.4. The denominator matters because a numerator improvement is useful only if it survives division by $Q_{\mathrm{id}}(1/n)$.

**Direct small-$x$ target.** A proposed estimate at the single point $x=1/n$, rather than a coefficient-by-coefficient estimate for the whole polynomial.

**Folded quotient template.** A finite labelled graph or quotient object that records identifications among paths or cycles in the fixed-point expansion.

**Markov interpolation loss.** The loss caused by applying Markov brothers' inequality to pass from control at reciprocal integer points to derivative control near zero.

**Product-ratio model.** A finite independent-permutation model in which normalized expectations become ratios of products of terms $(1-jx)$ after setting $x=1/n$.

**Signed pointwise cancellation.** Cancellation in the actual evaluated sum at $x=1/n$, not merely cancellation of formal coefficients or cancellation in a toy model.

**Surface-group organization.** A grouping or structure visible in the actual Kim--Tao surface-group quotient objects, as opposed to a grouping that exists only in a free-group or independent-permutation analogue.
