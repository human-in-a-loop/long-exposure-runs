---
created: 2026-05-15T17:07:00Z
cycle: 5
run_id: run-2026-05-15T153635Z
agent: worker
milestone: M2-proof-ledger
---

# M2 Proof-Ledger Closure Note

## Closure Judgment

The existing validated slices, plus the consolidation artifact `rigidity_proof_reconstruction.md`, satisfy the plan-level `M2-proof-ledger` success criteria. I recommend marking broad `M2-proof-ledger` as `validated`, narrowly for proof reconstruction and loss/dependency accounting only. This recommendation does not claim progress on `M3-computational-probes`, `M4-formal-certification`, `M5-extension-candidates`, or `M6-final-synthesis`.

## Success-Criterion Map

| criterion | artifact(s) | validation status | remaining caveat |
|---|---|---|---|
| Reconstruct Theorem 1 proof pipeline with quantitative dependencies | `rigidity_proof_reconstruction.md`, `theorem1_exponent_flow.md`, `weyl_inversion_detail.md` | validated by consolidation and prior Cycle 2 audit | Imported polynomial-method inputs remain black boxes; this is local-paper reconstruction. |
| Reconstruct Proposition 3.1 internals | `proposition31_internal_reconstruction.md`, `two_trace_expansion_ledger.md`, `markov_loss_reconstruction.md`, `proposition31_dependency_graph.*` | validated by Cycle 3 audit | MPvH embedding expansion and Nau boundedness are identified but not externally audited. |
| Reconstruct Theorem 2 delocalization proof pipeline | `delocalization_proof_reconstruction.md`, `eigenfunction_fourth_moment_ledger.md`, `pretrace_diagonal_term.md`, `theorem2_dependency_graph.*` | validated by Cycle 4 audit and explicitly accepted here as the paired plan artifact | MP23 rank-two fixed-point input remains imported. |
| Record all nontrivial estimates with source locations | Cycle 2-4 proof-ledger files plus `m2_loss_map.md` | validated at plan level | Exact external theorem statements should be audited in a later literature cycle if needed. |
| Identify exponent-loss locations | `m2_loss_map.md`, `theorem1_theorem2_loss_comparison.md` | validated at consolidation level | Loss sharpness is not claimed. |
| Preserve distinction between Weyl law and rigidity exponents | `weyl_inversion_detail.md`, `rigidity_proof_reconstruction.md`, `m2_loss_map.md` | validated at consolidation level | Final theorem uses existence of a positive exponent; exact optimization is out of scope. |
| Tie proof-ledger work back to later research surface | `m2_loss_map.md`, this closure note | validated as handoff guidance | M3 still has no scripts/data/figures and remains pending. |

## Evidence Summary

Theorem 1 is now represented by one inspectable proof artifact that links Proposition 3.1, the two-trace polynomial expansion, Markov brothers loss, smooth cutoff derivative loss, Chebyshev/grid probability, Weyl-law exponent `alpha_W`, and rigidity inversion exponent `alpha_R`. Theorem 2 already had a coherent paired reconstruction in `delocalization_proof_reconstruction.md`, supported by separate ledgers for the fourth-moment mechanism and diagonal term `S`.

The cross-proof loss map preserves the major distinctions required by the research brief: Proposition 3.1 losses are not conflated with theorem-level smoothing, Proposition 4.1/4.2 losses are not conflated with the final Sobolev step, and `alpha_W` is kept separate from `alpha_R`.

## Remaining Caveats

The proof ledger is complete at the local-paper level, but three imported inputs remain external black boxes: MPvH-style embedding expansion, Nau boundedness for two-trace statistics, and MP23 rank-two common-fixed-point estimates. These caveats do not block M2 closure because the milestone asks for proof reconstruction and dependency/loss accounting, not full external literature rederivation.

## Recommended Next Target

Begin `M3-computational-probes` with random-permutation common-fixed-point experiments. The first script should compare cyclic/diagonal and rank-two/noncyclic word families, because that directly probes the mechanism behind Proposition 3.1 and the Theorem 2 diagonal subtraction `S`.
