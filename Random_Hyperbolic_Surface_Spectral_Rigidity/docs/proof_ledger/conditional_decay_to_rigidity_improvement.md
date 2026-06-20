---
created: 2026-05-16T13:06:00Z
cycle: 26
run_id: run-2026-05-15T153635Z
agent: worker
milestone: M15-kim-tao-bridge-requirement
---

# Conditional Decay To Rigidity Improvement

## Question

If M14's missing coefficient-variation decay were proved for actual Kim--Tao quotient families, would it improve theorem-level exponents or only repackage existing inputs?

## Trace-Side Algebra

Proposition 3.1 currently gives

\[
\mathrm{variance}\le C\Lambda_0^2 q^{2\kappa} n^{-1}\|\tilde h\|^2.
\]

The proof then converts polynomial control into smooth cutoffs.  With a generic replacement \(q^b\) for the Proposition 3.1 Markov/interpolation loss, the same reconstructed algebra gives

\[
m=b/2+3+K,\qquad \alpha_0=\frac{1}{3m},
\]

with \(K\) still chosen large enough to dominate the \(\Lambda\)-power.  The fixed-\(\Lambda\) Weyl exponent is

\[
\alpha_W=\min(\alpha_0,1/9),
\]

and the edge Weyl inversion gives

\[
\alpha_R\le \frac{2}{3}\alpha_W.
\]

Thus a genuine replacement \(b<2\kappa\) improves the theorem-level rigidity exponent as long as the smooth cutoff derivative budget remains the limiting term.  Once \(\alpha_0\ge1/9\), further improvement would only affect constants or non-dominant losses unless the Chebyshev/grid step is also changed.

## Pre-Trace Algebra

Proposition 4.1/4.2 currently gives the fourth-moment estimate

\[
E\int a(z)(V_n-S)^2\,d\mathrm{Vol}
\le C\Lambda_0^8 q^{4\kappa}n^{-2}\|\tilde h\|^8.
\]

The reconstructed theorem proof uses derivative order \(2\kappa+11\).  With \(q^b\) replacing \(q^{4\kappa}\), the corresponding representative algebra is

\[
\alpha_0=\frac{1}{16(b/2+11)},\qquad
\alpha_{\infty}=\alpha_0/2.
\]

So a real eight-word coefficient-variation estimate with \(b<4\kappa\) would improve the \(n\)-exponent in Theorem 2's delocalization path.  The improvement is capped by the eighth-power cutoff derivative budget and the local-mass-to-\(L^\infty\) conversion.

## Scenario Table

Representative numeric scenarios from `data/extension_candidates/conditional_exponent_scenarios.csv`, taking \(\kappa=5\) and \(\epsilon=0.1\):

| theorem path | current loss | hypothetical loss | current alpha | hypothetical alpha | improvement | remaining limiter |
|---|---:|---:|---:|---:|---:|---|
| Theorem 1 rigidity | \(q^{10}\) | bounded \(q^0\) | 0.003766 | 0.007663 | 2.03x | smooth cutoff derivatives and Weyl-edge \(2/3\) conversion |
| Theorem 2 delocalization | \(q^{20}\) | bounded \(q^0\) | 0.001488 | 0.002841 | 1.91x | eighth-power cutoff derivatives and local mass conversion |

This table supports H3 in the conditional sense: replacing the Markov/interpolation envelope by a genuinely smaller coefficient-variation bound would change theorem-level \(\alpha\), not only constants.  It also shows that the improvement is moderate unless other proof axes are improved.

![representative theorem alpha under current and bounded Markov-loss scenarios](reports/figures/m15_conditional_exponent_scenarios.png)

## Where The Estimate Must Enter

| route | current bottleneck | replacement needed | theorem consequence |
|---|---|---|---|
| Proposition 3.1 to Theorem 1 | Markov derivative control of \(x^2p(x)\), yielding \(q^{2\kappa}\) | direct fixed-\(d\) weighted coefficient-variation bound for the Corollary 3.4 numerator | improves \(\alpha_R\) until cutoff/grid/Weyl-edge losses dominate |
| Proposition 4.2 to Theorem 2 | Markov second derivative control of \(x^2p(x)\), yielding \(q^{4\kappa}\) | direct fixed-\(d\) weighted coefficient-variation bound for the eight-word numerator after \(S\) subtraction | improves \(\alpha_\infty\) until eighth-power cutoff and local Sobolev conversion dominate |

## Decision

The route is not logically exhausted: the right conditional estimate would improve the exponent algebra.  It is practically blocked at the exact place M8 identified: one needs a Kim--Tao-level weighted coefficient-variation theorem for the actual quotient-family polynomial, not more independent-permutation toy enumeration.  Without that theorem, continuing to enlarge the toy model is unlikely to change the research conclusion.
