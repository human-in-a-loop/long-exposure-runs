---
created: 2026-05-15T15:36:35Z
cycle: 1
run_id: run-2026-05-15T153635Z
agent: worker
milestone: M1-paper-map
---

# Cycle 1 Foundational Map: Kim--Tao `2603.01127`

## Scope

This map records the proof architecture of Elena Kim and Zhongkai Tao, "Eigenvalue rigidity of hyperbolic surfaces in the random cover model", using only the local text `2603.01127.txt`. It is a Cycle 1 orientation artifact, not a proof reconstruction. Claims below are either paper statements, proof-pipeline summaries, or labeled bottleneck observations for later milestones.

## Run Notation

| Symbol | Meaning |
|---|---|
| `X = Gamma \ H` | Fixed compact connected orientable hyperbolic surface of genus `g >= 2`; see §2.1. |
| `X_n` | Degree `n` cover of `X` sampled uniformly from `X_{g,n} = Hom(Gamma, S_n)`; see §2.1. |
| `Gamma` | Surface group `<a_1,...,a_{2g} | [a_1,a_2]...[a_{2g-1},a_{2g}] = 1>`; see §2.1. |
| `phi_n` | Random homomorphism `Gamma -> S_n` encoding the cover; see §2.1. |
| `rho = rho_{phi_n}` | Permutation representation `std_n o phi_n : Gamma -> End(ell^2([n]))`; see (2.1). |
| `lambda_j(X_n)` | Laplacian eigenvalues of `X_n`; Theorem 1 uses those in `[1/4, Lambda]`. |
| `r` | Spectral parameter with `lambda = 1/4 + r^2`; trace integrals use `r tanh(pi r) dr`. |
| `Lambda` | Energy cutoff in Theorems 1-2. |
| `Lambda_0` | Auxiliary test-function scale: in §3 and §4, `Lambda_0 = Lambda` for large `Lambda`, otherwise fixed large `C`. |
| `q` | Polynomial degree. In the proof idea it is chosen on the scale `q = Lambda^{1/2-epsilon} n^c`; see §1.2 and §3.1. |
| `kappa` | Genus-dependent exponent from the polynomial expansion/Markov step; appears in Propositions 3.1, 4.1, 4.2 and Lemma 3.5 applications. |
| `h` | Polynomial/smooth cutoff on the range of `f_{Lambda_0}`, written `h(x)=x \tilde h(x)`; see §2.4 and §3.1. |
| `f_{Lambda_0}` | Rescaled positive test function `f(c_0 Lambda_0^{-1/2} x)` imported from [HMT25b, §2]; see §2.4. |
| `varphi` | Even compactly supported test function used in the trace/pre-trace formulas; its Fourier transform is specialized to `h o f_{Lambda_0}`. |
| `N_{X_n}(Lambda)` | Eigenvalue counting function `#{j : lambda_j(X_n) <= Lambda}`; see (1.4). |

## Main Results In Run Notation

### Theorem 1: Eigenvalue Rigidity and Weyl Law

Paper statement, §1, Theorem 1. For every `epsilon > 0`, there are `alpha = alpha(g, epsilon) > 0` and `C = C(X, epsilon) > 0` such that a uniformly random degree `n` cover `X_n` satisfies, with probability `1 - n^{-1/10}`, the following simultaneous estimates.

For every `Lambda in [1/4, infinity)` and every eigenvalue `lambda_j(X_n) in [1/4, Lambda]`,

```text
|lambda_j(X_n) - lambda_j| <= C Lambda^{1/2 + epsilon} n^{-alpha},
```

where the reference location `lambda_j >= 1/4` is defined by

```text
int_0^{sqrt(lambda_j - 1/4)} r tanh(pi r) dr = j / (n(2g-2)).
```

Moreover, uniformly for `Lambda in [1/4, infinity)`,

```text
N_{X_n}(Lambda)
= (2g-2)n int_0^{sqrt(Lambda - 1/4)} r tanh(pi r) dr
  + O_{X,epsilon}(n^{1-alpha} Lambda^{1/2+epsilon}).
```

Parameter roles to preserve: the probability is exactly `1 - n^{-1/10}` after the net/union bound in (3.12); `alpha` depends on `g, epsilon`; `C` depends on `X, epsilon`; `Lambda` is arbitrary in `[1/4, infinity)` after discretization and monotonicity.

### Theorem 2: Eigenfunction Delocalization

Paper statement, §1, Theorem 2. There are `alpha = alpha(g) > 0` and `C = C(X) > 0` such that a uniformly random degree `n` cover `X_n` satisfies, with probability `1 - n^{-1/10}`, the following simultaneous estimate.

For every `Lambda >= 1/4` and every normalized eigenfunction `u_j` with `Delta_{X_n} u_j = lambda_j(X_n) u_j`, `||u_j||_{L^2(X_n)} = 1`, and `lambda_j(X_n) <= Lambda`,

```text
||u_j||_{L^infty(X_n)} <= C Lambda^{3/2} n^{-alpha} ||u_j||_{L^2(X_n)}.
```

Remark 1.1 records a non-optimized exponent and an interpolation consequence: for every `epsilon > 0`, one can replace the `Lambda^{3/2}` growth by `Lambda^{1/4+epsilon}` at the cost of changing `alpha = alpha(g,epsilon)` and `C = C(X,epsilon)`.

## Section And Estimate Map

| Location | Item | Role |
|---|---|---|
| §1.2, (1.9)-(1.10) | Proof idea | Explains the reduction from twisted Selberg trace formula to a variance bound for a geodesic sum involving `tr rho(gamma^k)`. |
| §2.1, (2.1) | Random cover setup | Defines `X_{g,n}`, `X_n`, and `rho`; standard random-cover encoding. |
| §2.2, Lemma 2.1, (2.2) | Twisted Selberg trace formula | Standard analytic input, proved for completeness; converts spectral traces into identity term plus primitive geodesic/permutation-trace sum. |
| §2.3, Lemma 2.2, (2.4)-(2.5) | Twisted pre-trace formula | Standard analytic input for pointwise eigenfunction sums; Theorem 2 uses this instead of the trace formula. |
| §2.4, (2.6)-(2.8) | Test function `f_{Lambda_0}` and polynomial `h` | Imported test-function design from [HMT25b, §2], adapted to polynomial-method compatibility. |
| §2.4, Lemma 2.3, (2.9)-(2.12) | Trace-side uniform bound | Bounds normalized traces of `h o f_{Lambda_0}` by `Lambda_0 ||tilde h||`; used in §3.2.1. |
| §2.4, Lemma 2.4, (2.13)-(2.15) | Pre-trace-side uniform bound | Pointwise analogue of Lemma 2.3; used in §4.2.1. |
| §3.1, Proposition 3.1, (3.1) | Eigenvalue variance estimate | Main paper-specific proposition for Theorem 1: variance is `<= C Lambda_0^2 q^{2kappa} n^{-1} ||tilde h||^2`. |
| §3.1, (3.3)-(3.5) | Smooth cutoff conversion | Extends polynomial estimate to smooth cutoffs using Chebyshev expansion and derivative norms. |
| §3.1, (3.6)-(3.7) | Spectral cutoff construction | Builds `h_{Lambda,epsilon}` approximating an eigenvalue interval with derivative loss `Lambda^{j(1/2-epsilon)} n^{j alpha_0}`. |
| §3.1, (3.8)-(3.12) | Chebyshev + net argument | Converts second-moment bound to probability `1 - n^{-1/10}` and uniform-in-`Lambda` Weyl law. |
| §3.1, final paragraph | Weyl inversion | Converts (1.4) into eigenvalue rigidity (1.2). |
| §3.2.1, (3.13)-(3.14) | Uniform bound | Uses spectral side plus Lemma 2.3 to show the second moment is `O(Lambda_0^2 ||tilde h||^2)`. |
| §3.2.2, Lemma 3.3, (3.15)-(3.17) | Polynomial expansion | Adapts [MPvH25, §4] to two traces; expectation of trace products is rational-polynomial in `1/n` with controlled error. |
| §3.2.2, Corollary 3.4, (3.18)-(3.19) | Geodesic sum polynomialization | Uses support of `(h o f_{Lambda_0})^vee`, word-length/length comparison, and Lemma 3.3 to polynomialize the full geodesic sum. |
| §3.2.3, Lemma 3.5, (3.20) | Markov brothers' inequality | Imported polynomial derivative control; first major exponent-amplifying step. |
| §3.2.3, (3.21)-(3.22) | Proposition 3.1 completion | Applies Markov to `x^2 p(x)` and splits cases `n >= 2C q^kappa` and `n <= 2C q^kappa`. |
| §4.1, (4.1)-(4.2) | `S` and `V_n` definitions | Isolates the diagonal/local oscillation term for the eigenfunction proof. |
| §4.1, Proposition 4.1, (4.3)-(4.5) | Eigenfunction fourth-moment estimate | Pre-trace analogue of Proposition 3.1, with fourth powers and error `Lambda_0^8 q^{4kappa}/n^2`. |
| §4.1, (4.6)-(4.9) | Chebyshev + spectral windows | Converts Proposition 4.1 to high-probability local mass bounds on small windows. |
| §4.1, final estimates | Sobolev/elliptic conversion | Converts localized `L^2` mass into `L^infty` delocalization, producing `Lambda_0^3 n^{-alpha_0}` before taking square roots. |
| §4.2.1, (4.10)-(4.11) | Uniform fourth-moment bound | Pointwise/pre-trace analogue of §3.2.1, using Lemma 2.4 and kernel decay. |
| §4.2.2, Proposition 4.2, (4.12)-(4.15) | Fourth-order polynomial expansion | Adapts Lemma 3.3 to common fixed points of eight group elements; imports [MP23, Theorem 1.3] for the `n^{-2}` scale. |
| §4.2.3 | Proposition 4.1 completion | Applies Markov brothers' inequality to the fourth-order polynomial approximation. |

## Proof Pipeline

### Theorem 1 Pipeline

1. Construct `h o f_{Lambda_0}` so that it approximates an interval cutoff while retaining compact Fourier support and polynomial-method compatibility (§2.4, §3.1).
2. Apply the twisted Selberg trace formula (Lemma 2.1) to express the centered normalized spectral statistic as a geodesic sum weighted by `tr rho(gamma^k)`; see (3.13).
3. Prove Proposition 3.1 by three steps: uniform spectral-side bound (3.14), polynomial expansion of trace-product expectations via Lemma 3.3 and Corollary 3.4, then Markov brothers' derivative control via Lemma 3.5.
4. Convert Proposition 3.1 from polynomials to smooth cutoffs using Chebyshev polynomial expansion and derivative bounds; see (3.5).
5. Choose `alpha_0 = 1/(3(kappa+3+K))`, with `K = floor((kappa+5)/(2epsilon)) + 1`, so the cutoff-derivative losses are dominated; see §3.1.
6. Use Chebyshev's inequality, a geometric `Lambda` grid, and a union bound to obtain probability `1 - n^{-1/10}`; see (3.8)-(3.12).
7. Use monotonicity of `N_{X_n}` and Weyl-law inversion to obtain (1.4) and then eigenvalue rigidity (1.2).

### Theorem 2 Pipeline

1. Use the same `f_{Lambda_0}` and `h`, but replace the trace formula by the twisted pre-trace formula (Lemma 2.2).
2. Define the fourth-power fluctuation `V_n(h o f_{Lambda_0})(z,i)` and the diagonal/local term `S(h o f_{Lambda_0})(z,i)` in (4.1)-(4.2).
3. Prove Proposition 4.1 by the same three macro-steps as Proposition 3.1: uniform bound (4.11), polynomial expansion (Proposition 4.2), and Markov brothers' control (§4.2.3).
4. Use Chebyshev's inequality and a covering by spectral windows of size `(1+Lambda)n^{-alpha_0}` to bound local `L^2` mass; see (4.8)-(4.9).
5. Bound the diagonal term `S` by kernel localization and volume growth, giving `O(Lambda_0^4 n^{-4alpha_0})` before taking roots.
6. Apply Sobolev embedding and elliptic estimates on a fixed lift of a fundamental domain to convert local mass into the `L^infty` estimate (1.7).

The structural difference is therefore precise: Theorem 1 is a global trace/counting argument routed through (2.2), while Theorem 2 is a local pointwise mass argument routed through (2.5) and the `V_n - S` fourth-moment estimate.

## Input Taxonomy

### Standard Background

- Surface group model for covers via `Hom(Gamma,S_n)` (§2.1).
- Selberg trace formula and primitive geodesic expansion (Lemma 2.1).
- Selberg pre-trace formula and kernel representation (Lemma 2.2).
- Hyperbolic kernel estimates and compact support localization in §2.4 and §4.2.
- Chebyshev's inequality, union bounds, monotonicity of counting functions, Sobolev embedding, and elliptic regularity.

### Imported Prior Work

- Test function `f` and its properties from [HMT25b, §2], used in §2.4.
- Polynomial-method expansion technology from [MPvH25, §4], adapted in Lemma 3.3 and Proposition 4.2.
- Witten zeta and homomorphism-count asymptotics from [MP23] and [MPvH25], used in Lemma 3.3.
- Chebyshev polynomial coefficient control from [CGVTvH26, Corollary 4.5], used in (3.5).
- Smooth cutoff construction from [DZ16, Lemma 3.3], used around (3.6).
- Common fixed-point estimate from [MP23, Theorem 1.3], used in Proposition 4.2.
- Markov brothers' inequality in the form [MPvH25, Lemma 2.1], restated as Lemma 3.5.

### Paper-Specific Choices Or Adaptations

- The two-trace graph `C_{gamma_1,gamma_2}` in Lemma 3.3, replacing the single-loop graph in [MPvH25].
- The conversion of the full geodesic second moment into a low-degree polynomial `p(1/n)` in Corollary 3.4.
- The fourth-order pre-trace statistic `V_n - S` and diagonal subtraction `S` in (4.1)-(4.2).
- The eight-loop/common-fixed-point expansion in Proposition 4.2.
- The uniform-in-`Lambda` high-probability Weyl law and its eigenvalue rigidity consequence.

## Quantitative Loss Ledger

| Loss point | Location | Mechanism | Later-cycle priority |
|---|---|---|---|
| Test-function transition width | (3.6)-(3.7), (4.6)-(4.7) | Derivatives of smooth cutoffs grow with `n^{j alpha_0}` and powers of `Lambda`; this forces small `alpha_0`. | High: `M2-proof-ledger` should reproduce exact exponent flow. |
| Chebyshev coefficient/derivative conversion | (3.5), (4.5) | Polynomial estimates are converted to smooth functions with `C^{kappa+3+K}` or `C^{2kappa+11}` norms. | High: likely non-optimized exponent source. |
| Polynomial degree and support | Corollary 3.4, Proposition 4.2 | Fourier support gives word-length cutoff `|gamma^k| <= C Lambda_0^{-1/2} q`; degree is `O(Lambda_0^{-1/2} q)` plus constants. | Medium: determines admissible `q` scale. |
| Markov brothers' inequality | Lemma 3.5, §3.2.3, §4.2.3 | Derivative control costs powers like `q^{2kappa}` and `q^{4kappa}`. | High: prime candidate for exponent sharpening. |
| Chebyshev probability conversion | (3.8)-(3.12), (4.8)-(4.9) | Second/fourth moment bounds are degraded to high-probability estimates and then union-bounded over spectral grids. | Medium: affects final `1 - n^{-1/10}` and `alpha`. |
| Weyl inversion | End of §3.1 | Counting-function error becomes eigenvalue-position error; paper does not expose detailed spacing calculation. | Medium: reconstruct in `M2-proof-ledger`. |
| Pre-trace diagonal term `S` | (4.1), (4.9) | Local fourth moment leaves a diagonal oscillation term controlled separately by kernel decay. | High for eigenfunction proof; absent from Theorem 1. |

## Cycle 1 Diagnostic Outcomes

1. Hypothesis ruled in: the proof architecture is controlled by proposition-level estimates. Theorem 1 bottlenecks at Proposition 3.1; Theorem 2 bottlenecks at Proposition 4.1 plus Proposition 4.2.
2. Hypothesis partially ruled in: polynomial degree and Markov brothers' control are major losses, but the smooth-cutoff derivative conversion in (3.5)-(3.7) and (4.5)-(4.7) is also an explicit exponent bottleneck.
3. Hypothesis ruled in with qualification: Theorem 2 is structurally parallel to Theorem 1, but it introduces a genuinely local fourth-order statistic and the diagonal term `S`; it is not merely the same random-cover statistic with the trace formula replaced.

