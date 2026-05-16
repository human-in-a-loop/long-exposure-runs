---
created: 2026-05-16T15:14:00Z
cycle: 29
run_id: run-2026-05-15T153635Z
agent: worker
milestone: M18-test-function-localization-feasibility
---

# Test-Function Localization Feasibility

## Paper Parameter Map

Kim--Tao's test-function setup in §2.4 starts with a fixed even smooth function `f` whose inverse Fourier transform is supported in `[-1,1]`. They rescale it as

```text
f_{Lambda0}(x) = f(c0 Lambda0^{-1/2} x),
```

and in the Selberg/pre-trace formula use

```text
hat phi(x) = h o f_{Lambda0}(x),
```

where `h(x)=x htilde(x)` is a polynomial of degree `q`. Thus the spectral cutoff is not a freely translated local bump in `lambda`; it is a polynomial cutoff in the scalar variable `f_{Lambda0}(sqrt(lambda-1/4))`.

The support/degree facts used later are:

```text
supp((h o f_{Lambda0})^vee) subset [-c0 Lambda0^{-1/2} q, c0 Lambda0^{-1/2} q]
```

in the trace proof, and the analogous one-sided kernel support

```text
supp K_{(h o f_{Lambda0})^vee} subset [0, c0 Lambda0^{-1/2} q]
```

in the pre-trace proof. Therefore `q` is both the polynomial degree and, up to the factor `Lambda0^{-1/2}`, the geometric-side support scale.

## Random-Cover Losses

For Theorem 1, Proposition 3.1 bounds the normalized trace variance by

```text
Lambda0^2 q^(2 kappa) n^(-1) ||htilde||^2.
```

The source of `q^(2 kappa)` is the polynomial expansion plus Markov brothers' inequality applied to `x^2 p(x)` on an interval of size about `q^{-kappa}`.

For Theorem 2, Proposition 4.1/4.2 gives the pre-trace fourth-moment analogue

```text
Lambda0^8 q^(4 kappa) n^(-2) ||htilde||^8.
```

The stronger `q^(4 kappa)` loss comes from the second-derivative Markov step after an eight-loop common-fixed-point expansion and the rank-two input imported from MP23.

## Lambda Width To r Width

Write

```text
lambda = r^2 + 1/4.
```

A `lambda`-window `[Lambda, Lambda+Delta]` corresponds exactly to

```text
delta_r
  = sqrt(Lambda + Delta - 1/4) - sqrt(Lambda - 1/4).
```

For fixed bulk `Lambda>1/4` and `Delta << Lambda-1/4`,

```text
delta_r = Delta / (2 sqrt(Lambda-1/4)) + O(Delta^2).
```

At the edge `Lambda=1/4`, the bulk approximation is singular and the exact formula gives

```text
delta_r = sqrt(Delta).
```

Thus inverse-width support at the exact edge scales as `R ~= Delta^(-1/2)`;
for `Delta=n^{-d}` this is `R ~= n^{d/2}`, not the bulk `n^d` scale.

At high energy, fixed `lambda`-width produces a smaller `r`-width by a factor comparable to `sqrt(Lambda)`, so resolving the same `Delta` asks for larger transform scale.

## Uncertainty Mechanism

A compactly supported or sharply localized Fourier-side trace test resolving an `r`-window of width `delta_r` needs geometric/Fourier scale at least

```text
R >= c / delta_r.
```

Since Kim--Tao's architecture has `R ~ Lambda0^{-1/2} q`, resolving a bulk window `Delta=n^{-d}` at fixed `Lambda0` heuristically forces

```text
q >= C(Lambda) n^d.
```

The paper's theorem-level choice is instead logarithmic/polynomially small enough to satisfy `n >= q^kappa` and to keep the Markov losses under control. Therefore a local-window statistic below the M16 endpoint scale is not obtained by simply retuning the existing cutoffs.

## Exponent Feasibility

M17 requires, in the bulk,

```text
sqrt(Var Z_n) << n Delta,
```

or at exponent level, for `Delta=n^{-d}` and `Var Z_n <= n^v`,

```text
v < 2 - 2d.
```

If one ties `q` to the support required by localization, `q ~ n^d`, then the existing loss proxies scale like

```text
trace:     q^(2 kappa) ~ n^(2 kappa d),
pre-trace: q^(4 kappa) ~ n^(4 kappa d).
```

These proxies are not complete variance laws; they isolate the known interpolation/support penalty inside the current proof architecture. With representative `kappa=5`, the pre-trace proxy reaches the M17 bulk variance budget already around `d=0.1`, while the trace proxy is less severe but still grows polynomially with the desired localization.

## Trace Versus Pre-Trace

The trace-side architecture is the more plausible of the two because it pays `q^(2 kappa)` and targets a second moment. It still needs a new localized test-function construction and a random-cover variance estimate for the resulting statistic, because the paper's cutoff is designed for global endpoint control rather than a translated window bump.

The pre-trace architecture inherits the same spectral-window resolution problem and adds fourth-moment, fiberwise, diagonal-subtraction, and local Sobolev losses. Its `q^(4 kappa)` proxy makes it a less plausible first route for M17-style local spectral-window variance.

## Conservative Conclusion

The M17 variance target is not accessible by directly inserting a compactly localized `Delta=n^{-d}` window into the existing Kim--Tao proof. If a logarithmic-support smoothed test could resolve enough of the window with controlled leakage, the obstruction would weaken, but that would be a new test-function lemma rather than a consequence of §2.4. The next productive step is to isolate such a smoothed Paley-Wiener/window lemma and quantify leakage against the M17 main term.
