---
title: "Random Hyperbolic Surface Spectral Rigidity: Final Synthesis"
date: "2026-05-16"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# Random Hyperbolic Surface Spectral Rigidity: Final Synthesis

## Abstract

This report synthesizes the completed research campaign on Kim and Tao's *Eigenvalue rigidity of hyperbolic surfaces in the random cover model*. The campaign reconstructed the paper's proof architecture, localized the main quantitative losses, built finite permutation and Schreier benchmarks, tested several extension routes, and isolated the strongest remaining surface-facing bottleneck. The validated outputs are: an inspectable proof ledger for the eigenvalue-rigidity and eigenfunction-delocalization theorems; a finite labelled-template expectation identity; product-ratio and aggregate-control toy theorems; a local-window obstruction map; direct theorem corollaries for multiplicity, mass distribution, and fixed-width window counts; and a standalone two-permutation Schreier benchmark theorem.

The extension search did not produce an improved Kim--Tao exponent, a shrinking-window spectral-statistics theorem, or a transfer theorem from Schreier graphs to hyperbolic covers. It narrowed the next credible research target to coefficient or signed variation for the actual denominator-normalized Corollary 3.4 numerator, evaluated as $p(1/n)/Q_{\mathrm{id}}(1/n)$. The final audit recorded `76 validated, 1 in-progress · findings CRITICAL=1 MODERATE=1 · promise_check=green`; the remaining debts are artifact traceability issues, not reported mathematical contradictions.

## Introduction

Kim and Tao study random finite covers of a fixed compact hyperbolic surface. If $X=\Gamma\backslash\mathbb H$ is the base surface, a degree-$n$ random cover is encoded by a uniformly sampled homomorphism $\phi_n:\Gamma\to S_n$, with associated permutation representation $\rho_{\phi_n}$. The paper proves high-probability spectral rigidity for the new eigenvalues of the cover and polynomial-scale delocalization for eigenfunctions.

The research campaign had two goals. First, it reconstructed the proof from the local paper files `2603.01127.pdf` and `2603.01127.txt` until the proof architecture, dependencies, and quantitative losses were explicit. Second, it used that reconstruction to search for genuine extensions: sharper exponent mechanisms, finite random-permutation analogues, local spectral-window statistics, multiplicity and delocalization consequences, and benchmark theorem packages.

This final synthesis reports the mathematical and computational findings. It does not narrate session mechanics. Claims are reported at the level at which they were validated in the source record: theorem, theorem template, certified finite identity, numerical or computational evidence, obstruction, conditional target, or open follow-up problem.

## The Kim--Tao Problem and the Reconstructed Proof Architecture

The campaign began by turning Kim and Tao's paper, *Eigenvalue rigidity of hyperbolic surfaces in the random cover model*, into an explicit proof ledger. The base object is a compact connected orientable hyperbolic surface

$$
X=\Gamma\backslash\mathbb H
$$

of genus at least two. A random degree-$n$ cover is encoded by a uniformly sampled homomorphism

$$
\phi_n:\Gamma\to S_n,
$$

where $S_n$ is the symmetric group. The associated permutation representation is denoted $\rho_{\phi_n}$. The Laplace eigenvalues on the random cover $X_n$ are written $\lambda_j(X_n)$, with spectral parameter

$$
\lambda=\frac14+r^2.
$$

The first stage of the work separated the old spectrum inherited from the base surface from the new random-cover spectrum. It then mapped the two main theorem routes in the paper. Theorem 1 is the eigenvalue-rigidity and high-probability Weyl-law theorem for eigenvalues in $[1/4,\Lambda]$. Theorem 2 is the eigenfunction-delocalization theorem. The reconstructed proof architecture reports these as related but distinct arguments: Theorem 1 is routed through the twisted Selberg trace formula and Proposition 3.1, while Theorem 2 is routed through the twisted pre-trace formula and Propositions 4.1 and 4.2. This distinction was established in the cycles 1-3 report and completed in the cycles 4-6 report.

The Theorem 1 reconstruction treated Proposition 3.1 first as a black box and then opened it. The downstream reduction from Proposition 3.1 to Theorem 1 proceeds through a smooth cutoff, derivative-norm bookkeeping, Chebyshev's inequality, a spectral grid, and a final inversion from a counting-function estimate to eigenvalue locations. In the notation of the proof ledger, the variance bound after the smooth cutoff passage has the form

$$
\operatorname{Var}\le C n^{-1}\Lambda_0^{-K}
\Lambda^{2m(1/2-\epsilon)}n^{2m\alpha_0},
$$

where

$$
m=\kappa+3+K,\qquad \alpha_0=\frac{1}{3m}.
$$

This choice gives $-1+2m\alpha_0=-1/3$. The later choice

$$
K=\left\lfloor\frac{\kappa+5}{2\epsilon}\right\rfloor+1
$$

forces enough $\Lambda$ decay for the grid union bound. The resulting simultaneous probability level is the paper's $1-n^{-1/10}$ scale. Near the spectral edge $\lambda=1/4$, the Weyl integral

$$
F(\Lambda)=\int_0^{\sqrt{\Lambda-1/4}}r\tanh(\pi r)\,dr
$$

satisfies $F(1/4+t)\sim(\pi/3)t^{3/2}$, so the inversion from counting error to location error is Hölder rather than Lipschitz. The proof ledger therefore distinguishes the Weyl-law exponent $\alpha_W$ from a potentially weaker rigidity exponent $\alpha_R$.

Opening Proposition 3.1 exposed the trace-side random variable. The centered spectral statistic becomes, through the Selberg trace formula, a geodesic-side random sum $S_n$. The second moment is expanded as

$$
n^{-2}\mathbb E S_n^2,
$$

and the random part of each term is

$$
\mathbb E\left[\operatorname{tr}\rho(\gamma_1^{k_1})
\operatorname{tr}\rho(\gamma_2^{k_2})\right].
$$

Lemma 3.3 rewrites this product of traces as a common fixed-point statistic attached to folded quotient graphs built from two labelled cycles. Corollary 3.4 packages the resulting second moment into a denominator-normalized polynomial evaluation

$$
\mathbb E S_n^2=\frac{p(1/n)}{Q_{\mathrm{id}}(1/n)}+\text{error}.
$$

This is the first point where the later research program had a concrete object: the polynomial numerator and its denominator normalization, evaluated at $x=1/n$.

The Theorem 2 reconstruction followed the same macro-template but with different local structure. The pre-trace formula produces a centered local spectral mass. Its fourth power is denoted $V_n$ in the cycle reports. A primitive-power diagonal term $S$ is subtracted before the rank-two estimate is applied. The proof path recorded in cycles 4-6 is:

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

The diagonal subtraction is structural. The fourth-moment statistic $V_n$ alone contains cyclic primitive-power contributions that are too large for the rank-two common-fixed-point input. Subtracting $S$ leaves the non-diagonal statistic to which the eight-word folded-graph machinery applies. The cycles 4-6 audit accepted this reconstruction and closed `M2-proof-ledger` narrowly for local proof reconstruction and quantitative dependency/loss accounting.

The reconstructed dependency map separates three kinds of inputs. Standard background includes the random-cover model through homomorphisms into $S_n$, the Selberg trace formula, the pre-trace formula, hyperbolic kernel estimates, Chebyshev's inequality, monotonicity, Sobolev embedding, and elliptic regularity. Imported inputs include prior test-function technology, MPvH-style polynomial expansions, Witten-zeta and homomorphism-count asymptotics, Nau boundedness, MP23 rank-two estimates, Chebyshev coefficient control, and Markov brothers' inequality. Paper-specific adaptations include the two-trace graph $C_{\gamma_1,\gamma_2}$, the Corollary 3.4 second-moment polynomialization, and the fourth-order pre-trace statistic with diagonal subtraction.

## Where the Quantitative Losses Enter

The proof ledger's main quantitative result is not a sharper exponent. It is an explicit accounting of where the known losses enter the Kim--Tao architecture.

For Theorem 1, the visible proposition-level loss occurs at the Markov brothers interpolation step. The polynomial used there is

$$
P(x)=x^2p(x).
$$

Before this step, the argument has control of $P(1/n)$ at reciprocal integer points. Markov brothers' inequality converts discrete control on those points into derivative control near zero:

$$
\|P'\|\le Cq^{2\kappa}
\sup_{n\ge Cq^\kappa}|P(1/n)|.
$$

Taylor expansion from $0$ to $1/n$, together with $P(0)=0$, gives the desired $n^{-1}$ gain:

$$
|P(1/n)|\le \frac{1}{n}\|P'\|.
$$

The factor $q^{2\kappa}$ is therefore localized to derivative amplification, not to the initial formation of the two-trace statistic. The cycle 3 reconstruction and later M2 closure report this as the visible loss in the local paper proof. They do not claim that the loss is sharp.

For Theorem 1 after Proposition 3.1, the downstream losses are different. They come from smooth cutoff derivatives, the order $m=\kappa+3+K$, the choice of $K$ needed for large-$\Lambda$ decay, Chebyshev probability conversion, the grid union bound, and the edge behavior of the Weyl-law inverse. These losses explain how a variance statement becomes a high-probability counting statement and then an eigenvalue-location statement.

For Theorem 2, the analogous trace-side object is replaced by a pre-trace fourth-moment object. The proof ledger records a $q^{4\kappa}$ Markov-type loss at the Proposition 4.1/4.2 level. This is a second-derivative analogue of the trace-side interpolation cost, attached to the eight-word statistic. Theorem 2 then has losses that do not appear in Theorem 1: the primitive-power diagonal subtraction, the fiber union bound used in probability conversion, and the local-mass-to-pointwise conversion. The final pointwise bound also carries a $\Lambda_0^{3/2}$-type Sobolev/elliptic conversion factor in the cycle 4-6 loss map.

The cross-proof loss map from cycles 4-6 records the separation as follows:

| Loss source | Location | Role |
|---|---|---|
| $q^{2\kappa}$ | Proposition 3.1 | Trace-side Markov interpolation loss |
| $m=\kappa+3+K$ | Theorem 1 smoothing | Derivative order for smooth cutoff conversion |
| $\alpha_W\to\alpha_R$ | Weyl inversion | Edge loss near $\lambda=1/4$ |
| $q^{4\kappa}$ | Propositions 4.1 and 4.2 | Pre-trace fourth-moment Markov second-derivative loss |
| Fiber union | Theorem 2 probability conversion | Local-in-fiber union loss |
| $\Lambda_0^{3/2}$ | Theorem 2 final bound | Local-mass-to-$L^\infty$ conversion |

This accounting became the basis for the later extension search. It identified the Markov/interpolation step as the most concrete technical bottleneck. It also prevented a false simplification: Theorem 2 is not merely Theorem 1 repeated with a pre-trace formula. It has a local fourth-moment statistic, a diagonal subtraction, an eight-word folded-graph input, and separate probability and elliptic-conversion costs.

## First Computational and Formal Probes

After the proof ledger was closed, the campaign built finite toy models for the random permutation mechanisms exposed by the proof. These probes were explicitly scoped as finite independent-permutation and Schreier-operator benchmarks, not as hyperbolic surface theorems.

The first benchmark counted common fixed points of reduced words in random permutations. It confirmed the diagonal-subtraction heuristic at toy level. Cyclic primitive-power families had order-one common fixed-point counts, while the rank-two pair $(a,b)$ was much smaller and scaled near $1/n$. The same experiment also found a limitation: adding composite words such as $ab$ and $aB$ to a pointwise common fixed set can collapse to the same constraint as fixing $a$ and $b$. That showed that naive multiword intersections do not model the paper's eight-word folded-graph mechanism faithfully.

The second benchmark added folded trajectory quotient profiles. This separated cyclic/rank-one word families from rank-two/noncyclic families structurally before sampling. It explained the earlier null result: quotient structure had to be tracked explicitly before selecting a Monte Carlo observable. The third benchmark replaced fixed-basepoint intersections with direct injective labelled-graph embedding counts. For a labelled directed graph $H$, the observable counts injective maps of its vertices into $[n]$ such that every labelled edge is realized by the corresponding random permutation or inverse. This made rank-two eight-word templates measurable. At $n=400$, the cyclic eight-word toy template remained normalized near one, while the rank-two eight-word toy template had raw scale near $n^{-1}$ and normalized count near one. The conclusion was that much of the cyclic/rank-two separation in this toy model is constraint dimension.

The fourth benchmark fitted normalized embedding counts as functions of $x=1/n$. Degree-3 Chebyshev-window fits were accepted as the current low-noise benchmark for the cyclic and rank-two eight-word templates. Deliberately underdetermined degree-6 and degree-8 fits showed large derivative and coefficient growth. The audit accepted this as a toy Markov-amplification diagnostic: it illustrates interpolation conditioning, but it is not the actual MPvH/MP23 polynomial and not a hyperbolic trace statistic.

The fifth benchmark introduced a two-generator Schreier operator. Two independent random permutations $a,b$ define

$$
A=P_a+P_a^T+P_b+P_b^T.
$$

Loops and multiple edges are retained, so every row sum is exactly four. Coarse normalized adjacency-window counts were stable across $n=100,200,400,800$. Centered trace moments decreased after subtracting infinite 4-regular tree moments, supporting the trace-formula analogy that deterministic tree-like or backtracking terms should be separated before studying fluctuations. The same experiment found that degree-3 polynomial fits did not automatically transfer from low-noise labelled-template data to spectral-window data on a four-size grid; degree-1 fits were more stable for smooth spectral windows.

Together, these five slices closed `M3-computational-probes` as a reproducible benchmark suite. The closure claim is finite and methodological:

- cyclic or rank-one contributions remain order one in raw fixed-point and quotient observables;
- rank-two or noncyclic constraints are suppressed before normalization;
- direct labelled-template embeddings explain much of the suppression through constraint dimension;
- low-degree polynomial fits can be stable for low-noise normalized embedding observables;
- high-degree fits expose derivative and coefficient amplification;
- Schreier spectral windows supply an operator-level toy bridge, with interpolation fragility visible when the data grid is too small.

The first formal-certification slice then certified the exact finite identity behind the labelled-template embedding benchmark. For a labelled directed template $H$,

$$
\mathbf E\,\mathrm{InjEmb}_n(H)
=
(n)_{|V|}
\prod_a\frac{1}{(n)_{|C_a(H)|}},
$$

provided each normalized label constraint set $C_a(H)$ is a partial injection and $n\ge |V|$. If a constraint set is not a partial injection, or if $n<|V|$, the expectation is zero. Inverse-labelled edges are normalized by reversing orientation before forming forward constraints. Wolfram symbolic checks and Python exhaustive enumeration over small symmetric groups agreed with the formula, including the inverse-label regression case that had been repaired in the computational probe.

This M4 result certifies a narrow finite combinatorial mechanism. It does not certify the Selberg trace formula, the Kim--Tao trace expansion, or the imported MPvH/Nau/MP23 inputs. Its value is that it gives the later extension search a reliable benchmark identity tied directly to the cleanest computational probe.

## Product-Ratio Stability and Its Boundary

The extension search began with the Markov/interpolation bottleneck identified in the proof ledger. The early proof reconstruction had localized the visible $q^{2\kappa}$ trace-side loss to derivative control for polynomialized trace statistics. The first extension question was therefore whether that derivative amplification was an artifact of unstable reconstruction from sparse reciprocal-$n$ data, or whether it reflected a real analytic feature of the families that appear in the trace expansion.

The finite labelled-template identity from M4 supplied the controlled test case. For a conflict-free labelled template with $V$ vertices and per-label constraint counts $C_a$, the normalized expectation is

$$
N_H(n)=n^{C-V}\frac{(n)_V}{\prod_a (n)_{C_a}},
\qquad C=\sum_a C_a.
$$

After substituting $x=1/n$, this becomes a finite product ratio

$$
N_H(x)=\frac{\prod_{j\in A_H}(1-jx)}{\prod_{j\in B_H}(1-jx)}.
$$

For fixed templates this object is analytic at $x=0$, and its low-order Taylor expansion can be computed exactly. The fixed-template experiments from cycles 13-15 showed that the stable low-degree behaviour seen in the earlier labelled-embedding probes was not accidental. For example, the key rank-two benchmark had the exact normalized form

$$
N_H(n)=n\frac{(n)_7}{(n)_4^2}
=\frac{(n-6)(n-5)(n-4)}{(n-1)(n-2)(n-3)}.
$$

Its order-four expansion matched the symbolic and Python comparison paths, while high-degree sparse-grid fits from the earlier polynomial-window diagnostic were much less stable. The conclusion was a mechanism split: sparse-grid interpolation can be ill-conditioned even when the fixed-template expectation itself is tame.

The same product-ratio framework also explained why fixed-template stability does not remove the Kim--Tao bottleneck. When the template support or constraint profile grows with a size parameter $L$, the zeros and poles of the falling-factorial factors move toward $x=0$ at scale $1/L$. The logarithmic expansion

$$
\log N_L(x)
=\sum_{r\ge1}
\frac{\sum_{b\in B_L} b^r-\sum_{a\in A_L} a^r}{r}x^r
$$

shows why fixed-order coefficients and derivatives can grow rapidly when the factor indices are $O(L)$. Cycle 15 measured this in growing rank-two and rank-four profiles: benign cycle/path profiles stayed controlled, while nontrivial growing profiles produced large coefficient and derivative norms.

Cycle 18 then formalized the toy mechanism. If

$$
N_L(x)=\frac{\prod_{a\in A_L}(1-ax)}{\prod_{b\in B_L}(1-bx)},
\qquad
\max(A_L\cup B_L)\le C_0L,\quad |A_L|+|B_L|\le C_1L,
$$

then fixed-order coefficients satisfy a crude envelope

$$
|[x^k]N_L(x)|\le D_kL^{2k},
\qquad
|N_L^{(k)}(0)|\le k!D_kL^{2k}.
$$

This was the first post-reconstruction theorem-grade toy lemma. Its scope is narrow and important. It proves a deterministic statement for normalized independent-permutation product ratios. It does not improve the Kim--Tao rigidity exponent, replace MPvH/Witten-zeta/Nau/MP23 estimates, or control a surface-group quotient-family sum. Its value is that it isolates a clean principle: fixed conflict-free labelled templates are stable after normalization, while growing support or profile size can reintroduce precisely the derivative amplification that the Markov step pays for.

## Aggregate Control: From Termwise Bounds to External Inputs

The next question was whether termwise product-ratio control could be promoted to a Kim--Tao trace or pre-trace estimate. The bridge work answered this conservatively. The product-ratio framework exactly covers the independent-permutation labelled-template baseline, but Kim--Tao random covers average over homomorphisms from the surface group $\Gamma$ into $S_n$. That law brings in surface relations, denominator normalization, Witten-zeta and homomorphism-count asymptotics, Nau boundedness, MP23 rank-two inputs, geometry weights, centering, and summation over quotient families. The product-ratio skeleton is visible, but it is not the full probability law.

The aggregate obstruction is elementary once stated. If a family of templates satisfies termwise bounds such as

$$
|[x^k]N_T(x)|\le C_kL^{2k},
$$

then a weighted aggregate

$$
A_L(x)=\sum_T w_TN_T(x)
$$

only satisfies the universal estimate

$$
|[x^k]A_L(x)|
\le C_kL^{2k}\sum_T|w_T|.
$$

The new factor is total variation. Without a separate bound on family count, weight mass, rank-sensitive decay, or cancellation, per-template control does not become an aggregate theorem.

The first restricted folded two-word model made this obstruction concrete. Folding and canonicalization reduced raw ordered-pair complexity, but conflict-free canonical profiles and their multiplicities still grew quickly even at small word length. Trace-like refinements helped: replacing raw ordered reduced-word pairs by cyclically reduced conjugacy representatives, tracking primitive and diagonal/cyclic classes, and adding length weights reduced total variation in the toy model. But the reduction was still total-variation accounting, not a proof of cancellation.

The honest theorem template that survived this analysis had to be stratified by

$$
d=C-V.
$$

For a template $T$, the expectation can be written

$$
E_T(n)=n^{d_T}R_T(1/n).
$$

Different $d_T$ values carry different powers of $n$, so they cannot be aggregated into one coefficient sum without losing the meaning of the bound. In a fixed stratum

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

This is a useful finite theorem template, but it exposes rather than removes the missing input.

The cancellation diagnostics then tested whether the missing input might come from coefficient signs in the trace-like toy family. The dominant unweighted $d=1$ rank-two/noncyclic stratum at length cutoff $L=5$ had no order-one cancellation: the signed sum and coefficient absolute variation were both $800$ in magnitude. Higher orders showed partial cancellation, but the cancellation ratios were not stable, and finer structural groupings made the apparent cancellation disappear. Length weights improved the scale by lowering weighted total variation; they did not create sign cancellation.

The external-decay analysis quantified how strong an outside input would have to be. In the dominant toy stratum, rank-only decay did not help because all surviving records had the same rank proxy. Polynomial length and folded-complexity decay required large exponents. Exponential length decay was the most efficient tested axis, but even there the required coefficient-variation decay was far stronger than bare rank filtering.

Mapping this back to Kim--Tao proof objects gave the research significance of the obstruction. A genuine weighted coefficient-variation estimate for the actual Corollary 3.4 numerator or Proposition 4.2 eight-word numerator would attach directly to the proof. If such an estimate controlled the numerator before Markov interpolation, it could replace the generic $q^{2\kappa}$ or $q^{4\kappa}$ loss by a smaller $B(q)$-scale. Representative exponent algebra showed only moderate possible theorem-level improvement, because smoothing, Weyl inversion, and local-mass conversion losses remain. But the attachment point is real.

The conclusion of the aggregate-control branch is therefore precise. Product-ratio bounds control individual normalized templates. They do not control Kim--Tao aggregate trace sums by themselves. A theorem-level extension needs one of the following external inputs for the actual surface-group quotient families:

- polynomial total variation within fixed $d=C-V$ strata;
- rank-sensitive or probability-law decay beyond the toy product-ratio envelope;
- coefficient-variation control for the numerator coefficients;
- signed cancellation that survives surface-native grouping;
- a different surface-level estimate that bypasses the aggregate total-variation bound.

Larger independent-permutation toy enumerations were judged unlikely to change this conclusion unless they are tied directly to the actual surface-group numerator.

## Local Spectral Windows and the Compact-Support Obstruction

The second extension branch asked whether Kim--Tao's global rigidity and Weyl estimates imply local spectral statistics. The first answer was direct endpoint subtraction. If

$$
F(\Lambda)=\int_0^{\sqrt{\Lambda-1/4}}r\tanh(\pi r)\,dr,
$$

then the reconstructed Weyl law gives

$$
N_{X_n}([1/4,\Lambda])
=(2g-2)nF(\Lambda)
+O\!\left(n^{1-\alpha_W}\Lambda^{1/2+\epsilon}\right).
$$

Subtracting the estimates at $\Lambda+\Delta$ and $\Lambda$ yields

$$
N_{X_n}([\Lambda,\Lambda+\Delta])
=(2g-2)n\bigl(F(\Lambda+\Delta)-F(\Lambda)\bigr)
+O\!\left(n^{1-\alpha_W}(\Lambda+\Delta)^{1/2+\epsilon}\right).
$$

This is a valid corollary, but it is nontrivial only when the local main term beats the inherited endpoint error. In the bulk, this requires a window width above a global-error scale. At the spectral edge, where $F'(1/4)=0$ and

$$
F(1/4+\Delta)-F(1/4)
=\frac{\pi}{3}\Delta^{3/2}+O(\Delta^{5/2}),
$$

the threshold changes but remains far above mean spacing for the exponents under discussion. Rigidity gives a deterministic window-inclusion statement, but it similarly transfers only windows larger than the rigidity displacement. It does not give microscopic multiplicity control.

The branch therefore moved to smoothed local statistics. For a smoothed window of width $\Delta=n^{-d}$, the centered statistic

$$
Z_n(\phi;\Lambda,\Delta)
=
\sum_j\phi\left(\frac{\lambda_j(X_n)-\Lambda}{\Delta}\right)
-\operatorname{main}_n(\phi;\Lambda,\Delta)
$$

has bulk mean of size $n\Delta$. If

$$
\operatorname{Var}Z_n\le n^v,
$$

then Chebyshev gives relative control when

$$
\frac v2<1-d.
$$

To beat endpoint subtraction, the same window must also satisfy $d>\alpha_W$ in the bulk. This was the exact variance input needed for a real local-window theorem.

The existing Kim--Tao test-function architecture does not supply that input by retuning parameters. In the paper's setup, a polynomial degree parameter $q$ also controls the geometric support:

$$
\operatorname{supp}((h\circ f_{\Lambda_0})^\vee)
\subset
[-c_0\Lambda_0^{-1/2}q,\;c_0\Lambda_0^{-1/2}q].
$$

Resolving a $\lambda$-window requires inverse-width localization in the spectral parameter $r$, with

$$
\delta_r
=\sqrt{\Lambda+\Delta-1/4}-\sqrt{\Lambda-1/4}.
$$

In fixed bulk energy, $\delta_r\sim \Delta/(2\sqrt{\Lambda-1/4})$; at the edge it scales as $\sqrt{\Delta}$. Thus a polynomially shrinking window forces polynomially growing support. The trace side then pays the known $q^{2\kappa}$ Markov loss, and the pre-trace side pays the larger $q^{4\kappa}$ loss.

The smoothing escape route was also closed inside compact support. Fourier scaling gives

$$
\widehat{h_\delta}(t)
=\delta e^{-ir_0t}\widehat{\phi}(\delta t).
$$

Truncating the geometric side to $|t|\le R$ loses the scaled tail

$$
\int_{|u|>R\delta}|\widehat{\phi}(u)|\,du.
$$

Fixed-quality localization requires $R\delta$ bounded below, and small leakage requires $R\delta\to\infty$. Therefore logarithmic support cannot resolve a polynomially shrinking bulk window; support $R=n^\eta$ must satisfy $\eta\ge d$ in the bulk and $\eta\ge d/2$ at the edge.

Allowing polynomial support led to the long-support theorem template. At fixed energy and on the trace side, the missing variance estimate was named

$$
\operatorname{Var}Z_n(h_{\Lambda_0,\Delta,q})
\le C n^{1+2\kappa\eta-\beta+\epsilon},
\qquad q=n^\eta.
$$

Relative bulk control requires

$$
\beta>2\kappa\eta+2d-1.
$$

The pre-trace analogue is less plausible because the loss scale is $4\kappa\eta$. The trace-side branch was narrowed further to the localized Corollary 3.4 numerator

$$
p_{\Delta,q}(x)
=
\sum_{\gamma_1,\gamma_2}\sum_{k_1,k_2\ge1}
a(\gamma_1,k_1)a(\gamma_2,k_2)
h_{\Delta,q}^{\vee}(k_1\ell_{\gamma_1})
h_{\Delta,q}^{\vee}(k_2\ell_{\gamma_2})
Q_{\gamma_1^{k_1},\gamma_2^{k_2}}(x).
$$

Here $a(\gamma,k)=\ell_\gamma/(2\sinh(k\ell_\gamma/2))$, and $Q_{\gamma_1^{k_1},\gamma_2^{k_2}}$ is the quotient-polynomial numerator term from the two-trace expansion.

The localized numerator proxy model made this target inspectable but did not prove the needed estimate. It generated 4,800 proxy rows while separating exact paper indices and weights from modelling annotations such as quotient type, rank proxy, cyclic status, and $d=C-V$ stratum. Compact support and Paley-Wiener-scaled transform weights still left a large rank-two or unknown surface-group obstruction. Only an optimistic extra decay model changed the scale enough to motivate the next question.

That question was answered negatively for the compact-support transform itself. The localized transform scales as

$$
h_\delta^\vee(t)=\delta_r e^{-ir_0t}\widehat{\phi}(\delta_rt).
$$

Decay is therefore in the scaled variable $u=t\delta_r$, not directly in the support length $t$. At minimal support, $\eta=d$, the endpoint scaled variable is constant size. When $\eta>d$, smooth tails decay in $n^{\eta-d}$, but this is not an exponential-in-support damping factor. After audit repair, the transform/geodesic-weight model had zero success rows once success required negative net growth.

The branch decision was to preserve the local-window route as a follow-up problem, not to continue same-axis parameter sweeps. The compact-support route remains open only through a new coefficient-variation or small-$x$ theorem for the actual denominator-normalized surface numerator, of the form

$$
\frac{p_{\Delta,q}(1/n)}{Q_{\mathrm{id}}(1/n)}
\le n q^A n^{-\sigma+o(1)}
$$

strong enough to meet the trace-side saving condition. The alternative is a separate noncompact trace-tail architecture with a spectral localizer, geometric convergence and truncation control, and a tail rate stronger than actual geodesic and quotient-family growth. No local spectral-statistics theorem was proved in this branch; what was proved is the structure of the obstruction and the precise theorem targets that would be needed to move beyond it.

## Direct Consequences of the Reconstructed Theorems

After the local-window route was preserved as a follow-up problem, the campaign pivoted to consequences that use the reconstructed Kim--Tao theorems without requiring a new coefficient-variation or trace-tail input. This was a conservative branch: it asked what follows directly from Theorem 1, the eigenvalue-rigidity theorem, and Theorem 2, the eigenfunction-delocalization theorem, once the proof architecture had already been made explicit.

The first branch was multiplicity and spectral-cluster bookkeeping from Theorem 1. Let $\mu_j$ denote random-cover eigenvalues and $\lambda_j$ denote deterministic reference locations. If, on the high-probability rigidity event,

$$
|\mu_j-\lambda_j|\le R_j,
$$

then every random cluster in an interval $I$ must come from deterministic reference locations in the expanded interval. With a uniform radius $R$ on the relevant spectral range,

$$
\#\{j:\mu_j\in I\}
\le
\#\{j:\lambda_j\in I^{+R}\}.
$$

For a single point this becomes a multiplicity envelope:

$$
\operatorname{mult}_{X_n}(\lambda)
\le
\#\{j:|\lambda_j-\lambda|\le R\}.
$$

In Kim--Tao's theorem-level regime the radius has the form

$$
R=C_\epsilon \Lambda_{\max}^{1/2+\epsilon}n^{-\alpha_R}.
$$

The deterministic reference locations are described by

$$
F(\lambda_j)=\frac{j}{(2g-2)n},
\qquad
F(\Lambda)=\int_0^{\sqrt{\Lambda-1/4}}r\tanh(\pi r)\,dr.
$$

In the fixed bulk, where $\lambda>1/4$, this gives the paper-level multiplicity scale

$$
O(n^{1-\alpha_R}\lambda^{1/2+\epsilon})
$$

up to fixed energy constants. At the spectral edge the correct density is not $F'(\Lambda)$, since $F'(1/4)=0$, but the edge expansion

$$
F(1/4+\Delta)=\frac{\pi}{3}\Delta^{3/2}+O(\Delta^{5/2}).
$$

The edge cluster envelope therefore has the form

$$
O\bigl(n(\Delta+R)^{3/2}\bigr).
$$

The validated conclusion is that this is a theorem-level transport corollary, not a new local-statistics theorem. It does not prove simplicity, level repulsion, microscopic spacing laws, or endpoint-beating counts. It records exactly how rigidity controls clusters at the inherited rigidity scale.

The second branch extracted deterministic mass-distribution consequences from Theorem 2. If $u$ is $L^2$-normalized, $\lambda\le\Lambda$, and

$$
\|u\|_\infty\le M_{\Lambda,n},
$$

then interpolation gives, for every $2\le p\le\infty$,

$$
\|u\|_p
\le
\|u\|_\infty^{1-2/p}\|u\|_2^{2/p}
\le
M_{\Lambda,n}^{1-2/p}.
$$

The endpoints recover $\|u\|_2=1$ and the original $L^\infty$ estimate. The same amplitude envelope gives a small-set mass bound: for every measurable set $A$,

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

fixed-energy eigenfunctions cannot concentrate positive mass on sets of volume $o(n^{2\alpha})$, up to constants. This is partial delocalization at polynomial scale in the cover degree. It is not quantum ergodicity or equidistribution: a sup-norm bound prevents concentration on too-small sets, but it does not force mass into any particular region.

The proof-mining branch then looked one step upstream in the Theorem 2 argument. Before the final Sobolev and elliptic conversion to $L^\infty$, the pre-trace proof controls a fixed-cutoff local $L^2$ mass statistic. With probability at least $1-n^{-1/10}$, for the smooth nonnegative base cutoff $a$ used in the proof, every fiber $i$, and all normalized eigenfunctions below the relevant energy,

$$
\int_{\mathbb H} a(z)\,|u_j^\rho(z,i)|^2\,d\operatorname{Vol}(z)
\le
C\Lambda_0 n^{-\alpha_0},
\qquad
\alpha_0=\frac{1}{16(2\kappa+11)}.
$$

This is stronger in the $\Lambda_0$ bookkeeping than the final sup-norm-derived mass envelope, because the final conversion introduces an additional $\Lambda_0^2$ factor at the squared-mass level. The scope is fixed-cutoff only. The statement does not union over all centers, dominate arbitrary nonsmooth balls, give lower mass, or imply spatial equidistribution.

The final direct consequence in this branch was a fixed positive-width spectral-window count corollary from Theorem 1. The reconstructed Weyl-law statement gives, on the high-probability event,

$$
N_{X_n}([1/4,\Lambda])
=
(2g-2)nF(\Lambda)
+O_\epsilon(n^{1-\alpha_W}\Lambda^{1/2+\epsilon}).
$$

For a fixed interval $I=[a,b]$ with $1/4\le a<b$, simultaneous endpoint subtraction gives

$$
N_{X_n}([a,b])
=
(2g-2)n(F(b)-F(a))
+O_\epsilon(n^{1-\alpha_W}b^{1/2+\epsilon}).
$$

Since $F(b)-F(a)>0$ for fixed positive-width windows, the main term is order $n$, and the relative error is $O(n^{-\alpha_W})$ after fixing $a,b,g$, and $\epsilon$. The centered version is also available as a deterministic high-probability error bound:

$$
N_{X_n}([a,b])-(2g-2)n(F(b)-F(a))
=
O_\epsilon(n^{1-\alpha_W}b^{1/2+\epsilon}).
$$

At the edge, a fixed interval $[1/4,1/4+\Delta]$ still has an order-$n$ main term through the expansion

$$
F(1/4+\Delta)-F(1/4)
=
\frac{\pi}{3}\Delta^{3/2}+O(\Delta^{5/2})
$$

for fixed $\Delta>0$. Shrinking windows $\Delta=n^{-d}$ leave the scope of this corollary and return to the local-window obstruction described above. The fixed-window result is therefore a macroscopic count asymptotic with polynomial relative error, not a variance asymptotic, limiting law, level-repulsion theorem, or universality statement.

Taken together, these direct consequences form a clean corollary package. They are useful because they translate the reconstructed theorems into multiplicity envelopes, mass-support bounds, a proof-level fixed-cutoff mass estimate, and fixed-window spectral counts. Their shared limitation is equally important: none bypasses the coefficient-variation bottleneck needed for shrinking local spectral statistics.

## Standalone Schreier Benchmark Theorem

The strongest finite-model output of the campaign is the standalone two-permutation Schreier benchmark theorem. This branch began as a computational analogue for trace-expansion mechanisms and ended as a theorem package for a random permutation model. Its role is to show a complete trace-method pattern in a setting where the combinatorics can be isolated from hyperbolic geometry.

Let $P_a$ and $P_b$ be independent uniform permutations of $[n]$, and define

$$
A_n=P_a+P_a^{-1}+P_b+P_b^{-1}.
$$

This is the adjacency operator of a two-generator Schreier graph with loops and multiple edges allowed. It has row sum $4$. For a fixed integer $k\ge0$, the trace expands as

$$
\operatorname{Tr}(A_n^k)
=
\sum_{w\in\{a,a^{-1},b,b^{-1}\}^k}
\operatorname{Fix}(w(P_a,P_b)).
$$

Words that freely reduce to the identity contribute $\operatorname{Fix}(w)=n$ deterministically. Their count is the $k$th closed-walk moment $m_k$ of the infinite $4$-regular tree. The theorem package states that, for every fixed $k$,

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

The expectation statement comes from separating freely reducing identity words from nontrivial reduced words. A fixed nontrivial reduced word has $O_k(1)$ expected fixed points, so after normalizing by $n$ its total contribution is $O_k(n^{-1})$.

The variance statement uses a paired trace expansion:

$$
\operatorname{Var}\bigl(n^{-1}\operatorname{Tr}(A_n^k)\bigr)
=
n^{-2}
\sum_{u,v}
\operatorname{Cov}(\operatorname{Fix}(u),\operatorname{Fix}(v)).
$$

Identity words are deterministic after the tree-word separation and therefore contribute no covariance. The remaining task is a fixed-pair covariance bound for nontrivial reduced words:

$$
\operatorname{Cov}(\operatorname{Fix}(u(P_a,P_b)),\operatorname{Fix}(v(P_a,P_b)))
=
O_{u,v}(1).
$$

The proof uses the labelled-template expectation identity from the finite permutation probes. A conflict-free quotient template $H$ has $V(H)$ quotient vertices and $C_a(H),C_b(H)$ distinct directed constraints for the two labels. Its leading exponent is controlled by

$$
V(H)-C_a(H)-C_b(H).
$$

After cyclic reduction, each edge-containing quotient component contains a nonempty closed labelled trajectory. Every quotient vertex in such a trajectory has at least one outgoing labelled constraint, so

$$
C_a(H)+C_b(H)\ge V(H),
$$

and hence

$$
V(H)-C_a(H)-C_b(H)\le0.
$$

Templates with partial-injection conflicts contribute zero. Equal, inverse, cyclic-conjugate, and shared-power word pairs can change constants but do not change the exponent. This gives $O_{u,v}(1)$ covariance for every fixed nontrivial reduced pair. Since the number of length-$k$ words is finite for fixed $k$, the normalized variance is $O_k(n^{-2})$.

The benchmark also explains the earlier numerical behavior. Simulations for low even moments had centered-variance slopes near $-1.7$ over accessible $n$, but the paired-template mechanism found no positive-power covariance obstruction. The validated interpretation is finite-size crossover toward the theorem-order $n^{-2}$ decay, not evidence for an $n^{-1}$ limiting covariance law.

The firewall around this result is part of the theorem package. The Schreier benchmark is a finite independent-permutation theorem. It does not prove a Kim--Tao random hyperbolic cover theorem, a Selberg trace transfer, a surface-group quotient-family estimate, an adjacency-to-Laplacian theorem, or shrinking-window spectral statistics. The analogy is structural: both the Schreier model and the Kim--Tao proof expand trace statistics, separate deterministic or diagonal terms, and reduce fluctuation estimates to fixed-point or quotient-template counting. The analogy stops before transfer because the Kim--Tao model includes surface-group relations, hyperbolic geodesic weights, Selberg and pre-trace formula inputs, denominator normalization, and external quotient-family machinery.

## The Corollary 3.4 Numerator Bottleneck

The final surface-facing branch returned to the compact-support trace statistic in Kim--Tao's proof. Its goal was not to prove an exponent improvement, but to identify exactly what theorem would be needed to improve the visible $q^{2\kappa}$ loss in Proposition 3.1.

The object is the denominator-normalized Corollary 3.4 value

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

Corollary 3.4 packages the second moment as

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

in the paper's working range. The denominator bound matters because any improved numerator theorem must survive the division by $Q_{\mathrm{id}}(1/n)$.

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

Derivative control for $P$ over the reciprocal-integer range produces the $q^{2\kappa}$ scale, and Taylor expansion from $x=0$ transfers that derivative control back to $x=1/n$. Thus the current loss is an interpolation loss. It is not forced merely by the definition of the numerator.

This localization led to the direct small-$x$ target:

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

If one models denominator loss by

$$
|Q_{\mathrm{id}}(1/n)|^{-1}\le n^D,
$$

then the effective saving in the long-support budget is

$$
\beta=(2\kappa-A)\eta+\sigma-D.
$$

In the paper-safe denominator range, $D=0$. Outside that range, denominator near-zeros can erase a numerator saving.

The direct small-$x$ route is logically distinct from coefficient variation because it controls one evaluated value rather than every coefficient or every stratum. That distinction is only meaningful, however, if the proof uses signed cancellation at the actual evaluation point $x=1/n$. If the proof expands the numerator and bounds

$$
\sum_i |w_i Q_i(1/n)|
$$

inside fixed quotient, length, primitive-power, or kernel strata, then the route becomes coefficient or signed variation in substance.

The signed pointwise target was therefore named as

$$
\mathrm{SPC}(A,\sigma):\quad
\left|\frac{p(1/n)}{Q_{\mathrm{id}}(1/n)}\right|
\le
C n\Lambda_0^{20}\|\widetilde h\|^2q^A n^{-\sigma+o(1)}.
$$

The signs in this aggregate can come from the transform values and from the evaluated quotient-polynomial values. The Selberg length denominator is positive. Cancellation at $x=0$, cancellation at off-range reciprocal points, or a toy independent-permutation pairing does not control the needed paper-safe evaluated ratio. The branch therefore narrowed to a surface-level question: can the actual weighted surface aggregate cancel at $x=1/n$ after denominator normalization?

## Surface-Native Grouping and the Current Pivot

The next step converted signed pointwise cancellation into a surface-native grouping problem. A surface-native grouping is a grouping visible in Kim--Tao's actual Lemma 3.3 and Corollary 3.4 objects, rather than in a free-Schreier or independent-permutation analogue.

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

For a grouping $G$, the direct signed pointwise theorem template was stated as

$$
\mathrm{SPC}_G(A,\sigma):\quad
\left|
\sum_{i\in G}
w_i\frac{Q_i(1/n)}{Q_{\mathrm{id}}(1/n)}
\right|
\le
C n\Lambda_0^{20}\|\widetilde h\|^2q^A n^{-\sigma+o(1)}.
$$

The shared exponent bookkeeping remains

$$
\beta=(2\kappa-A)\eta+\sigma-D.
$$

The grouping taxonomy separated possible surface inputs into several classes. The Markov interpolation route is the paper-proved baseline. Surface-relation kernel grouping and length-shell transform-phase grouping survived as conditional theorem targets. Quotient-complex profile, diagonal/off-diagonal relation balance, and primitive-power profile are visible in the surface aggregate but currently underdetermined: no validated theorem supplies cancellation for those groupings. Absolute fixed-stratum controls are coefficient-variation-equivalent. Cancellation at $x=0$, off-range reciprocal cancellation, near-zero denominator scenarios, and Schreier transfer are blocked or toy-only for this surface problem.

The strongest surviving direct target was surface-relation kernel grouping. It is paper-native because Kim--Tao Lemma 3.3 uses a folded quotient setup with a kernel-closure condition:

$$
\text{every path in }W_r\text{ spelling an element of }
\ker(F_{2g}\to\Gamma)\text{ is closed.}
$$

The later probe found that this condition is not currently theorem-ready as a signed pointwise cancellation mechanism. Kernel closure attaches to folded quotient targets before embedding expectations, polynomial contributions, and evaluated quotient ratios. In the validated reconstruction, it acts as an admissibility and structure condition for the quotient targets. It does not by itself supply opposite signs, orthogonality, or evaluated pairing among

$$
Q_i(1/n)
$$

terms.

Two kernel-related rows remain as conditional templates only: kernel-class signed pairing and quotient-polynomial sign grouping. Either would become a genuine direct signed pointwise theorem if a new argument proved cancellation of evaluated $Q_i(1/n)$ values across relation-kernel classes. No such argument was found in the reconstructed Lemma 3.3 input.

This resolves the current pivot. The direct relation-kernel signed pointwise branch should not continue by relabeling admissibility, smaller quotient-family size, or absolute mass bounds as cancellation. If the next proof requires total variation or absolute control inside fixed quotient-complex, length, primitive-power, or relation-kernel strata, the correct target is coefficient/signed variation for the actual surface numerator. Length-shell transform-phase grouping remains a secondary conditional target, but it should be pursued only after the coefficient/signed-variation formulation is made explicit.

The resulting surface-facing target is therefore:

$$
\text{coefficient/signed variation for }
\frac{p(1/n)}{Q_{\mathrm{id}}(1/n)}
\text{ in the actual Kim--Tao surface aggregate.}
$$

The work did not prove an improved rigidity exponent, a variance law, a shrinking-window theorem, level repulsion, local universality, or a Schreier-to-surface transfer. It refined the bottleneck map to the point where the next useful theorem target can be stated without ambiguity.

## Evidence Status and Residual Debt

The final audit headline is:

```text
76 validated, 1 in-progress · findings CRITICAL=1 MODERATE=1 · promise_check=green
```

The milestone distribution therefore supports treating the reconstructed proof, finite probes, theorem corollaries, Schreier benchmark, local-window obstruction, and surface-numerator bottleneck as validated campaign outputs, with the confidence levels recorded as provisional in the audit summary. The audit emitted no reconciliation events.

The remaining debt is evidence hygiene, not a reported mathematical disproof.

The moderate residual debt is attached to M6 final synthesis. The latest ledger event referenced a missing artifact path:

```text
reports/final/final_report.md
```

Existing final-package artifacts provided partial support, but the specific final report file was absent when the audit ran. This reporter run restores that artifact in the finalize stage by regenerating `reports/final/final_report.md`.

The critical residual debt is attached to M36 direct small-$x$ surface numerator target. The plan success criteria referenced missing artifact text:

```text
p(1/n)/Q_id(1/n)
```

The substantive M36 analysis is still reported as validated in the audit summary. The debt is that the success criterion pointed to artifact-style text that was not found as a concrete artifact reference. In the final report, this should be read as a traceability defect in the evidence record, not as a contradiction of the M36 theorem-target formulation.

The audit's future-work proposals are:

1. Restore or regenerate a final report artifact matching `reports/final/final_report.*` and update the final artifact index so the M6 plan success criteria are directly satisfied.
2. Correct the latest M6 ledger artifact references to point at existing final package artifacts, then rerun `promise_check` and artifact-reference checks to close the evidence-hygiene gap.

The mathematical future-work anchor is the surface numerator target from the previous section. The artifact future-work anchor is the final synthesis package and its references. These are distinct: the former is the next research problem, while the latter is the cleanup needed to make the final record internally complete.



## Conclusions

The campaign produced a clear map of the Kim--Tao proof and its bottlenecks. The global eigenvalue-rigidity theorem runs through the Selberg trace formula, a two-trace second moment, Corollary 3.4 polynomialization, Markov brothers interpolation, high-probability Weyl-law conversion, and Weyl inversion. The eigenfunction-delocalization theorem runs through a pre-trace fourth-moment argument with primitive-power diagonal subtraction and a separate $q^{4\kappa}$ interpolation scale. The reconstruction identifies the Markov/interpolation step as a visible loss, while keeping separate the smoothing, union-bound, edge-inversion, and Sobolev-conversion losses.

The finite-model work gives useful but bounded evidence. The labelled-template expectation identity is certified for independent random permutations. Product-ratio bounds explain why fixed templates are stable while growing profiles can recover derivative amplification. The Schreier benchmark proves expectation $m_k+O_k(n^{-1})$ and variance $O_k(n^{-2})$ for fixed trace moments of the two-permutation operator. These results are publication-facing finite benchmarks, but they do not transfer automatically to Kim--Tao random hyperbolic covers because the surface model contains relations, geodesic weights, denominator normalization, and imported quotient-family estimates.

The extension search narrowed the surface problem rather than solving it. Endpoint subtraction gives fixed positive-width window counts but not shrinking local statistics. Compactly supported trace tests resolving polynomial shrinking windows force long support and return to a localized Corollary 3.4 numerator target. Transform damping and surface-relation kernel grouping did not produce a theorem-ready cancellation mechanism.

The best anchored mathematical follow-up is therefore a coefficient or signed-variation theorem for the actual surface numerator $p(1/n)/Q_{\mathrm{id}}(1/n)$. A direct signed pointwise theorem would need cancellation at the evaluated point $x=1/n$ after denominator normalization; an absolute-stratum proof would instead be coefficient variation in substance. Length-shell transform-phase grouping remains a secondary conditional direction. Surface-relation kernel closure is paper-native and structurally important, but current evidence treats it as admissibility rather than as sign-pairing or orthogonality.

The evidence-hygiene follow-up is separate: the restored `reports/final/final_report.md` artifact should be indexed in the final package, and the latest M6 ledger artifact references should be corrected before rerunning `promise_check` and artifact-reference checks.

## References

No root `REFERENCES.md` file was present at final assembly. The bibliography below is reconstructed from the local campaign sources and preserves bracket-style references for the sources cited by this synthesis.

[1] Elena Kim and Zhongkai Tao, *Eigenvalue rigidity of hyperbolic surfaces in the random cover model*, local files `2603.01127.pdf` and `2603.01127.txt`.

[2] Cycle reports `reports/cycles/report_cycles_1-3.md` through `reports/cycles/report_cycles_49-50.md`, which contain the detailed proof reconstruction, computational probes, extension-search reports, theorem templates, and final surface-bottleneck analyses summarized here.

[3] `MANIFEST.md`, workspace inventory after cycles 49-50, listing scripts, tests, datasets, figures, proof ledgers, reports, and final artifacts used by the campaign.

[4] Final audit summary for run `run-2026-05-15T153635Z`, reporting milestone status distribution, findings, residual debt, and future-work anchors.

## Implementation and Evidence Appendix

The final synthesis cites result classes rather than every generated CSV or figure. The core reproducibility scripts for the result classes directly discussed in the body are:

- `scripts/certify_labelled_embedding_expectation.py` for the labelled-template expectation identity in the finite permutation probes.
- `scripts/analyze_product_ratio_bounds.py` for the fixed-template and growing-template product-ratio envelopes.
- `scripts/build_local_window_route_synthesis.py` for the local-window obstruction and branch decision.
- `scripts/build_schreier_benchmark_package.py` for the standalone Schreier benchmark theorem package.
- `scripts/analyze_surface_corollary34_numerator_obstruction.py` for the Corollary 3.4 numerator reconstruction and Markov-loss localization.
- `scripts/analyze_direct_small_x_surface_numerator_target.py` for the direct small-$x$ target and denominator-loss budget.
- `scripts/analyze_signed_pointwise_cancellation_surface_aggregate.py` for signed pointwise cancellation classification.
- `scripts/analyze_surface_native_grouping_problem.py` for surface-native grouping taxonomy.
- `scripts/analyze_surface_relation_kernel_spc_probe.py` for the kernel-closure signed-cancellation probe and current pivot.
