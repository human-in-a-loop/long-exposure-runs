---
created: 2026-05-16T20:38:00Z
cycle: 40
run_id: run-2026-05-15T153635Z
agent: worker
milestone: M29-pretrace-local-mass-intermediate-from-theorem2-proof
---

# M29 Pre-Trace Local-Mass Intermediate

## Decision

`advance_pretrace_local_mass_branch`

Classification: `standalone_smoothed_kernel_mass_corollary`.

The extracted statement is stronger than M28's deterministic small-set estimate in the high-energy energy-power budget, but only for the fixed smooth cutoffs used by the Theorem 2 proof. It should not be relabeled as an arbitrary fixed-ball, shrinking-ball, or quantum-ergodicity statement.

## Extracted Statement

On the Theorem 2 high-probability event, for the fixed nonnegative cutoff `a in C_c^\infty(H)` used in §4.1, every fiber `i` and every `L^2`-normalized eigenfunction below energy `Lambda0` satisfies

```text
int_H a(z)|u_j^rho(z,i)|^2 dVol(z) <= C Lambda0 n^(-alpha0),
alpha0 = 1/(16(2 kappa + 11)).
```

Source locations are Kim--Tao §4.1, equations (4.1)-(4.9), plus the M2 ledgers `delocalization_proof_reconstruction.md`, `eigenfunction_fourth_moment_ledger.md`, and `pretrace_diagonal_term.md`.

## Comparison With M28

M28's deterministic local mass upper bound from the final Theorem 2 sup norm has the schematic form

```text
int_A |u|^2 <= C Lambda0^3 n^(-alpha0) vol(A)
```

for a fixed-volume set or patch, because the final bound is `||u||_infty^2 <= C Lambda0^3 n^(-alpha0)`. The pre-Sobolev statement gives `Lambda0 n^(-alpha0)` for the proof's fixed smooth patch. At fixed energy this is a constant-factor theorem-strength distinction rather than a better `n` exponent; when `Lambda0 = n^b`, the improvement is `n^(2b)`.

## Reversal Evidence

| Candidate | Classification | Evidence | Decision impact |
|---|---|---|---|
| fixed smooth cutoff on one base patch, all fibers | `standalone_smoothed_kernel_mass_corollary` | §4.1 fixes `a`, Proposition 4.1 controls `int a(V_n-S)^2`, and (4.9) implies the local mass bound after fiber/window union | advances M29 branch |
| arbitrary fixed-radius ball family | `not_established` | no proof step unions over spatial centers or dominates all indicators by the same controlled cutoff family | do not claim |
| shrinking balls or local QE | `unsupported_stronger_claim` | the estimate is an upper mass bound at fixed base scale only | do not claim |
| diagonal-free fourth-moment cancellation | `proof_internal` | `S` must be subtracted and then bounded deterministically | not an external corollary |

## Interpretation

The theorem-level content is a pre-Sobolev delocalization statement: no normalized low-energy eigenfunction can place more than `C Lambda0 n^(-alpha0)` mass in the fixed sheet-local cutoff region. This is more local than M28's global support lower bound and explains why the final `Lambda^(3/2)` theorem loses visible energy power. The proof still stops short of fixed-ball uniformity because the spatial observable is a chosen smooth cutoff, not a family of all balls.
