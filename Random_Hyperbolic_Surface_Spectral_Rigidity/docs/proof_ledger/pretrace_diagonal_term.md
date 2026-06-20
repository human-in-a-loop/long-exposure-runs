---
created: 2026-05-15T16:37:00Z
cycle: 4
run_id: run-2026-05-15T153635Z
agent: worker
milestone: M2-proof-ledger
---

# Pre-Trace Diagonal Term S

## Scope

This note isolates the diagonal term `S` from Kim--Tao (4.1). It explains why the eigenfunction proof centers `V_n` and then subtracts `S`, rather than trying to estimate `V_n` alone.

## Definition

Let `Gamma_0` be the set of primitive elements in `Gamma \ {id}`. For `(z,i) in H x [n]`, §4.1 defines

```text
S(h o f_Lambda0)(z,i)
  := (1/2) sum_{k_1,k_2,k_3,k_4 in Z\{0}}
          sum_{gamma in Gamma_0}
          prod_{ell=1}^4 rho_ii(gamma^{k_ell})
          K_{(h o f_Lambda0)^vee}(z, gamma^{k_ell} z).
```

The factor `1/2` compensates for double counting of primitive orientations/powers. The multilinear version replaces the four identical factors by `h_1,...,h_4`.

## Where S Comes From

The centered pre-trace formula gives

```text
centered local mass
  = sum_{gamma != id} rho_ii(gamma) K(z,gamma z).
```

The fourth power of this expression sums over all non-identity four-tuples

```text
(gamma_1,gamma_2,gamma_3,gamma_4).
```

Among these four-tuples, the paper singles out the diagonal family

```text
(gamma^{k_1}, gamma^{k_2}, gamma^{k_3}, gamma^{k_4}),
gamma primitive, k_m != 0.
```

This is exactly the family encoded by `S`. In §4.2, the expansion (4.10) uses

```text
Gamma_tilde^4 = (Gamma\{id})^4 \ diagonal primitive-power four-tuples.
```

Thus `V_n-S` is the fourth-moment statistic with the primitive-power diagonal removed.

## Mechanistic Role

`S` is not a cosmetic normalization. Without removing the primitive-power diagonal, the eight-word common-fixed-point estimate used in Proposition 4.2 would not have the necessary rank-two/noncyclic input. After the diagonal is removed, the first four-tuple contains two elements that are not powers of the same primitive element. The paper then uses that these two elements generate a free group of rank two and applies the common-fixed-point estimate `[MP23, Theorem 1.3]` to obtain an `n^{-2}` scale.

In short:

```text
V_n alone      = fourth power including cyclic primitive diagonals,
S              = cyclic primitive diagonal contribution,
V_n - S        = non-diagonal fourth statistic with rank-two fixed-point decay.
```

This rules in the diagnostic hypothesis that `S` is a necessary diagonal/main-term subtraction.

## Special Cases

### x = y / z = w

The pre-trace proof evaluates the kernel on the diagonal in the base point:

```text
K(z, gamma z).
```

The identity element `gamma=id` is already separated in (2.5) as

```text
(1/(2 pi)) int_0^infty h o f_Lambda0(r) r tanh(pi r) dr.
```

Therefore `S` does not include the identity deck element. It starts after the local Weyl term has been subtracted from the spectral side.

### Identity Group Element

If `gamma=id`, the contribution belongs to the identity/local Weyl term in (2.5), not to `S`. The definition of `S` sums over primitive `gamma in Gamma_0 subset Gamma\{id}` and nonzero powers `k_ell`. This prevents identity powers from re-entering the diagonal term.

### Non-Identity Off-Diagonal Terms

All non-identity four-tuples not expressible as powers of one primitive element remain in `V_n-S`. These are the terms entering Proposition 4.2. Their common fixed-point statistics are polynomialized through the eight-loop graph `C_{gamma_1,...,gamma_8}` and controlled using the rank-two fixed-point estimate.

### Spectral Edge lambda = 1/4

The Theorem 2 proof uses windows in the spectral parameter `lambda` and the same transform `f_Lambda0`. At the edge `lambda=1/4`, the window construction still works by taking `Lambda0=C` below the fixed large threshold. No new edge inversion is needed, unlike Theorem 1's Weyl-law-to-eigenvalue step.

### Support Boundary

The pre-trace kernel support gives

```text
supp k_{(h o f_Lambda0)^vee} subset [0, c0 Lambda0^{-1/2} q].
```

Therefore a term in `S` or `V_n-S` is nonzero only when each displacement `d_H(z,gamma^{k_ell}z)` is within this radius. Since `d_H(z,gamma z) >= ell_gamma(X)`, the same support bound controls primitive powers and allows conversion to word length via (3.19).

## Deterministic Bound Used in Theorem 2

After the high-probability control of `V_n-S`, equation (4.9) still contains

```text
sup_z |S(h_Lambda o f_Lambda0)(z,i)|^{1/4}.
```

The paper bounds it deterministically using kernel decay:

```text
|S(h_Lambda o f_Lambda0)(z,i)|
  <= C Lambda0^4 n^{-4 alpha0},
```

so

```text
|S|^{1/4} <= C Lambda0 n^{-alpha0}.
```

This is the same size as the identity/local Weyl term for the short spectral window. Thus `S` is sharp enough for the proof's local mass target, but it is not optimized or shown to be the true expectation of `V_n`; it is the cyclic diagonal contribution that must be separated before the rank-two polynomial method applies.

## Diagnostic Outcome

`S` encodes a real diagonal obstruction in the fourth-moment expansion. It removes the cyclic primitive-power family, allowing the remaining terms to satisfy the noncyclic/rank-two condition needed for the `n^{-2}` common-fixed-point decay. Its contribution is later controlled deterministically and is not the source of the final `Lambda^{3/2}` exponent.
