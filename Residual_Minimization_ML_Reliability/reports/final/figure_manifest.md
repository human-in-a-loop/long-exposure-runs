---
created: 2026-05-14T04:20:00Z
cycle: 3
run_id: run-2026-05-14T030813Z
agent: worker
milestone: M-5
---

# Figure Manifest

## `data/triage_residual_scaling.png`

Caption: Candidate residual mechanisms compared by sampled loss, physical error, and certificate scaling.

Generating script: `scripts/triage_residual_sequences.py`

Claim supported: M-1 triage identifies fixed finite collocation as the strongest validated mechanism because sampled residuals can miss global error while continuous derivative control detects oscillation.

## `data/triage_bad_sequence_profiles.png`

Caption: Representative bad-sequence profiles showing nonzero oscillatory functions that satisfy sampled constraints.

Generating script: `scripts/triage_residual_sequences.py`

Claim supported: the failure is visible as between-node behavior, not as boundary-condition leakage.

## `data/collocation_certificate_scaling.png`

Caption: Fixed collocation loss remains zero while the fill-distance regularity certificate detects hidden oscillations.

Generating script: `scripts/collocation_certificate_scaling.py`

Claim supported: for \(u_n(x)=\sin^2(\pi mnx)\), the sampled loss is zero and \(\|u_n\|_{L^2}^2=3/8\), but the sampled regularity certificate grows like \(m^2n^4\).

## `data/collocation_certificate_profiles.png`

Caption: The bad sequence satisfies sampled residual constraints but violates the sampled stability certificate through large between-node curvature.

Generating script: `scripts/collocation_certificate_scaling.py`

Claim supported: the derivative residual vanishes at fixed collocation nodes while curvature reveals the unresolved between-node oscillation.
