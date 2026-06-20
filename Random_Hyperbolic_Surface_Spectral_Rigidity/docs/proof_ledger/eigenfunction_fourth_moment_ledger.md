---
created: 2026-05-15T16:36:00Z
cycle: 4
run_id: run-2026-05-15T153635Z
agent: worker
milestone: M2-proof-ledger
---

# Eigenfunction Fourth-Moment Ledger

## Scope

This note reconstructs Proposition 4.1 and Proposition 4.2 from Kim--Tao §4.2. It focuses on how the eigenfunction delocalization proof reuses the polynomial-method architecture from Proposition 3.1 and where the pre-trace/fourth-moment setting forces new combinatorics.

## Object Controlled

After the pre-trace formula, the centered local spectral mass is

```text
sum_l h o f_Lambda0(t_l^rho)|u_l^rho(z,i)|^2
  - (1/(2 pi)) int_0^infty h o f_Lambda0(r) r tanh(pi r) dr.
```

The paper defines `V_n` as the fourth power of this centered quantity and subtracts the diagonal term `S`. Proposition 4.1 controls the square of the local average of `V_n-S`:

```text
E[ int_H a(z) (V_n(h o f_Lambda0)(z,i) - S(h o f_Lambda0)(z,i))^2 dVol(z) ]
  <= C Lambda0^8 q^{4 kappa} n^{-2} ||htilde||^8.
```

This is an eighth-order expression after expansion: four factors from `V_n` and two copies from squaring `V_n-S`.

## Expansion (4.10)

Using (2.5), the left side becomes a sum over two four-tuples of non-identity group elements, with the diagonal primitive-power four-tuples removed:

```text
sum_{(gamma_1,...,gamma_4) in Gamma_tilde^4}
sum_{(gamma_5,...,gamma_8) in Gamma_tilde^4}
  E[ prod_{ell=1}^8 rho_ii(gamma_ell) ]
  int_H a(z) prod_{ell=1}^8 K_{(h o f_Lambda0)^vee}(z,gamma_ell z) dVol(z).
```

Here `Gamma_tilde^4` is the set of non-identity four-tuples excluding the diagonal family

```text
(gamma^{k_1}, gamma^{k_2}, gamma^{k_3}, gamma^{k_4}),
gamma != id, k_m != 0.
```

That exclusion is exactly where `S` enters the proof. The remaining statistic must have enough independence to be `O(n^{-2})` after averaging.

## Uniform Bound

Section 4.2.1 proves the crude estimate

```text
(4.10) <= C Lambda0^8 ||htilde||^8.
```

The first part follows from Lemma 2.4 and the identity contribution bound (2.10):

```text
sup_z |V_n(h o f_Lambda0)(z,i)| <= C Lambda0^4 ||htilde||^4.
```

The second part controls `S` using kernel decay:

```text
|S(h o f_Lambda0)(z,i)| <= C Lambda0^4 ||htilde||^4.
```

This uniform bound is too weak for large `n`, but handles the small range `n <= 2C q^kappa` after constants are enlarged.

## Proposition 4.2: Polynomial Approximation

For polynomial `h(x)=x htilde(x)` of degree `q`, Proposition 4.2 states that for `n >= q^kappa`, `Lambda0 >= C`, and fixed `i`,

```text
(4.10) = p(1/n) / (n^2 Q_id(1/n))
         + O( Lambda0^8 (Cq)^{kappa q} n^{-q-2} ||htilde||^8 ),
```

where

```text
deg p <= C Lambda0^{-1/2} q + C,
Q_id(1/n) in [C^{-1}, C].
```

The support statement is the pre-trace analogue of the trace-side support reduction:

```text
supp k_{(h o f_Lambda0)^vee} subset [0, c0 Lambda0^{-1/2} q].
```

Together with `d_H(z,gamma z) >= ell_gamma(X)` and the word-length comparison (3.19), each nonzero term has

```text
|gamma_ell| <= C Lambda0^{-1/2} q.
```

For large `Lambda0`, this is at most `q/8`, leaving room for all eight words to have total length at most `q`.

## Eight-Word Common-Fixed-Point Input

The needed analogue of Lemma 3.3 is equation (4.15). For `sum_{ell=1}^8 |gamma_ell| <= q`, with the first four-tuple not diagonal in the primitive-power sense,

```text
E[ prod_{ell=1}^8 rho_ii(gamma_ell) ]
  = E[ (1/n) sum_{i=1}^n prod_{ell=1}^8 rho_ii(gamma_ell) ]
  = Q_{gamma_1,...,gamma_8}(1/n) / (n^2 Q_id(1/n))
    + O((Cq)^{kappa q} n^{-q-2}).
```

The averaged product counts common fixed points of the eight permutations `rho(gamma_ell)`. The graph used in Lemma 3.3, `C_{gamma_1,gamma_2}`, is replaced by `C_{gamma_1,...,gamma_8}`: eight loops with their first vertices identified. The same folded-quotient/embedding expansion then applies.

The genuinely new input is the replacement for the two-trace boundedness step. Because the diagonal four-tuple has been removed, there are two elements among `gamma_1,...,gamma_4` that are not powers of the same primitive element. The paper uses that, without loss of generality, `gamma_1,gamma_2` generate a rank-two free group and invokes `[MP23, Theorem 1.3]`:

```text
E[ fix <gamma_1,gamma_2> ] / n <= C_q n^{-2}.
```

This is the source of the `n^{-2}` scale in the fourth-moment proof. It is absent from Proposition 3.1.

## Markov Step

Proposition 4.2 and the uniform bound imply, for `n >= C q^kappa`,

```text
|n^{-2} p(1/n)| <= C Lambda0^8 ||htilde||^8.
```

Applying the Markov brothers inequality (3.20) to `P(x)=x^2 p(x)` on `[0,1/(2Cq^kappa)]` gives

```text
p(1/n) / (n^2 Q_id(1/n))
  <= n^{-2} ||(x^2 p(x))''||_[0,1/(2Cq^kappa)]
  <= C q^{4 kappa} Lambda0^8 n^{-2} ||htilde||^8,
```

for `n >= 2Cq^kappa`. The second derivative is the reason the visible Markov loss is `q^{4 kappa}` rather than the `q^{2 kappa}` loss in Proposition 3.1.

For `n <= 2Cq^kappa`, the crude uniform bound (4.11) implies the same target after absorbing powers of `q` into the right-hand side. This completes Proposition 4.1.

## Proposition 3.1 vs Proposition 4.1/4.2

| Feature | Proposition 3.1 | Proposition 4.1/4.2 |
|---|---|---|
| Formula input | Selberg trace formula (2.2) | twisted pre-trace formula (2.5) |
| Statistic | centered global trace | centered local spectral mass |
| Moment expanded | second moment | square of a fourth-moment fluctuation |
| Random product | two traces / two words | eight matrix entries / eight words |
| Graph model | two disjoint labeled cycles folded to quotients | eight loops with common base vertex folded to quotients |
| Diagonal subtraction | volume identity already subtracted | primitive-power diagonal `S` subtracted |
| Key imported boundedness | Nau boundedness removes negative powers | MP23 common fixed-point estimate gives `n^{-2}` after diagonal removal |
| Polynomial approximation | `p(1/n)/Q_id(1/n)` | `p(1/n)/(n^2 Q_id(1/n))` |
| Degree after support | `<= C Lambda0^{-1/2}q` | `<= C Lambda0^{-1/2}q + C` |
| Uniform bound | `<= C Lambda0^2 ||htilde||^2` | `<= C Lambda0^8 ||htilde||^8` |
| Markov derivative | first derivative of `x^2 p(x)` | second derivative of `x^2 p(x)` |
| Visible Markov loss | `q^{2 kappa}` | `q^{4 kappa}` |
| Final theorem role | Weyl law and eigenvalue rigidity | local mass and eigenfunction sup-norm |

## Diagnostic Outcomes

Theorem 2 is not merely Proposition 3.1 with a different trace formula. The macro-architecture is shared: uniform bound, polynomial expansion, Markov interpolation, and small-`n` fallback. The new content is the diagonal-excluded four-tuple structure, the eight-word common-fixed-point polynomialization, and the `n^{-2}` input from common fixed points of a rank-two subgroup.

The dominant visible `n`-exponent loss in Proposition 4.1 is still technical Markov interpolation, now as `q^{4 kappa}` from a second derivative. The `n^{-2}` scale itself appears structural after subtracting `S`, because the fourth-moment proof needs two independent fixed-point constraints once the primitive-power diagonal has been removed.
