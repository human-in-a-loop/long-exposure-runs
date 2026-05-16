---
created: 2026-05-16T20:37:00Z
cycle: 40
run_id: run-2026-05-15T153635Z
agent: worker
milestone: M29-pretrace-local-mass-intermediate-from-theorem2-proof
---

# Pre-Trace Local-Mass Intermediate

## Controlled Statistic

Kim--Tao Theorem 2 does not first control pointwise eigenfunction values. The proof controls a centered pre-trace local spectral mass. In §4.1, equations (4.1) and (4.2) define

```text
V_n(h o f_Lambda0)(z,i)
  = (sum_l h o f_Lambda0(t_l^rho)|u_l^rho(z,i)|^2
     - (1/(2 pi)) int_0^infty h o f_Lambda0(r) r tanh(pi r) dr)^4
```

and a primitive-power diagonal term `S(h o f_Lambda0)(z,i)`. Proposition 4.1 bounds, for fixed fiber `i` and normalized nonnegative cutoff `a in C_c^\infty(H)`,

```text
E int_H a(z) (V_n - S)^2 dVol(z)
  <= C Lambda0^8 q^(4 kappa) n^(-2) ||htilde||_infty^8.
```

The smooth rewrite (4.5) gives the same bound with derivative norm `||htilde||_{C^(2 kappa + 11)}^8` and factor `Lambda0^(-2)n^(-2)`.

## Proof Chain

The extraction chain is:

```text
twisted pre-trace formula (2.5)
-> centered local spectral mass
-> fourth power V_n
-> primitive-power diagonal subtraction S
-> Proposition 4.2 eight-word polynomialization
-> Proposition 4.1 moment bound
-> Chebyshev plus fiber/window union
-> fixed-cutoff local L2 mass
-> Sobolev/elliptic Linf conversion
```

Equation (4.8) gives fixed-fiber high-probability control of `int a(V_n-S)^2`; union over fibers and the spectral-window grid gives the event of probability at least `1 - n^(-1/10)`. On that event, equation (4.9) yields for each selected spectral window:

```text
sum_{lambda_j in window} int_H a(z)|u_j^rho(z,i)|^2 dVol(z)
  <= identity/local-Weyl term + sup_z |S|^(1/4) + n^(-1/32).
```

The proof then bounds the first two terms by `C Lambda0 n^(-alpha0)`, with

```text
alpha0 = 1/(16(2 kappa + 11)).
```

## Standalone Proposition

**Proposition (fixed-cutoff fiber local mass, extracted from Theorem 2 proof).** Fix the base surface `X`, choose a nonnegative `a in C_c^\infty(H)` with `int_H a dVol = 1`, and keep the Theorem 2 spectral cutoff/window construction. There are constants `C=C(X,a)` and `alpha0=alpha0(g)>0` such that, with probability at least `1 - n^(-1/10)`, for every fiber `i in [n]` and every normalized eigenfunction with `lambda_j(X_n) <= Lambda0`,

```text
int_H a(z)|u_j^rho(z,i)|^2 dVol(z) <= C Lambda0 n^(-alpha0).
```

For low energies the proof uses the paper's convention `Lambda0=C(X)`, and for high energies `Lambda0` tracks the ambient upper energy. This is a fixed-cutoff or smoothed local-mass statement on each sheet of the cover.

## Comparison With Final Linf Step

The final step applies Sobolev embedding and elliptic estimates on a fixed base ball:

```text
||u_j^rho(.,i)||_Linf(B(z0,R))^2
  <= C_R Lambda0^2 int_H a(z)|u_j^rho(z,i)|^2 dVol(z)
  <= C Lambda0^3 n^(-alpha0).
```

Thus the pre-Sobolev local-mass statement has the same `n` exponent as the squared final Theorem 2 bound, but improves the visible energy power from `Lambda0^3` to `Lambda0`. The exponent gap is therefore a real high-energy gap, not an improved fixed-energy `n` exponent.

## Nonclaims and Obstructions

The valid statement is not quantum ergodicity, random-wave behavior, lower mass on balls, nodal information, or shrinking-scale statistics. It is also not an arbitrary moving-ball theorem as stated. The proof fixes a smooth cutoff `a` and uses positivity on a chosen covering patch for the later Sobolev step; turning this into uniform control for all balls or a large family of indicators would require a separate cutoff/net majorization and another union-bound check.

The obstruction to a stronger geometric statement is not the diagonal term alone. `S` is controlled at the correct scale after subtraction. The limiting issue is that Proposition 4.1 is formulated for the proof's smooth cutoff/test-function pipeline and then unioned over fibers and spectral windows, not over arbitrary spatial centers or nonsmooth indicators.
