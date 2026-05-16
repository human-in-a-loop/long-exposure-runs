---
created: 2026-05-16T13:50:00Z
cycle: 27
run_id: run-2026-05-15T153635Z
agent: worker
milestone: M16-local-spectral-window-corollaries
---

# M16 Local Spectral Window Corollaries

## Purpose

M15 ended the aggregate-control toy route unless a genuine Kim--Tao coefficient-variation theorem is targeted.  M16 pivots to a direct question: what local or mesoscopic spectral-window consequences already follow from Kim--Tao's validated Weyl-law and rigidity estimates?

The answer is conservative.  The theorem gives a clean local-window corollary by subtracting endpoint Weyl estimates, and rigidity gives window inclusions after expanding deterministic reference windows by the eigenvalue displacement scale.  But the inherited global errors are much larger than mean spacing for the representative M2 exponent sizes, so this does not yet produce local spectral statistics.

## Corollary Ledger

| Claim type | Statement | Status |
|---|---|---|
| Corollary | \(N_{X_n}([\Lambda,\Lambda+\Delta])=(2g-2)n(F(\Lambda+\Delta)-F(\Lambda))+O(n^{1-\alpha_W}(\Lambda+\Delta)^{1/2+\epsilon})\). | Follows by subtracting simultaneous Weyl endpoint bounds. |
| Threshold | Nontriviality requires \((2g-2)(F(\Lambda+\Delta)-F(\Lambda))\gg n^{-\alpha_W}(\Lambda+\Delta)^{1/2+\epsilon}\). | Sufficient, constants normalized. |
| Bulk approximation | For \(\Delta\ll \Lambda-1/4\), \(F'(\Lambda)=\tfrac12\tanh(\pi\sqrt{\Lambda-1/4})\), so \(\Delta\gg n^{-\alpha_W}\Lambda^{1/2+\epsilon}/((2g-2)F'(\Lambda))\). | Valid away from the edge. |
| Edge approximation | At \(\Lambda=1/4\), \(F(1/4+\Delta)-F(1/4)\sim(\pi/3)\Delta^{3/2}\), so the edge exponent is \(n^{-2\alpha_W/3}\) rather than \(n^{-\alpha_W}\). | Separate edge regime required. |
| Rigidity inclusion | Random-window counts are bounded by deterministic reference counts in windows expanded by \(\delta_R=\Lambda^{1/2+\epsilon}n^{-\alpha_R}\). | Follows from eigenvalue displacement. |
| Multiplicity | A \(\delta_R\)-scale cluster is bounded only by a deterministic Weyl mass of size roughly \(n^{1-\alpha_R}F'(\Lambda)\Lambda^{1/2+\epsilon}\) in the bulk. | Too coarse for exact multiplicity or mean-spacing statistics. |

## Numerical Threshold Probe

The script `scripts/analyze_local_window_thresholds.py` uses normalized constants with representative parameters
\[
\alpha_W=0.006,\qquad \alpha_R=0.004,\qquad \epsilon=0.1,\qquad g=2.
\]
These values are not asserted as paper constants; they are a stable scale model matching the M2/M15 exponent ledger.  The generated CSVs compare three quantities:

- Weyl-subtraction threshold \(\Delta_W\), solving the integral criterion exactly.
- Rigidity displacement \(\delta_R\).
- Mean-spacing proxy \(1/(n(2g-2)F'(\Lambda))\), only where \(F'(\Lambda)>0\).

Representative rows from `data/extension_candidates/local_window_thresholds.csv` show the obstruction:

| regime | \(\Lambda\) | \(n\) | \(F'(\Lambda)\) | \(\Delta_W\) | \(\delta_R\) | mean spacing |
|---|---:|---:|---:|---:|---:|---:|
| edge | 0.25 | \(10^6\) | 0 | 5.143 | 0.412 | undefined |
| moderate bulk | 1 | \(10^6\) | 0.496 | 5.836 | 0.946 | \(1.01\cdot10^{-6}\) |
| bulk | 4 | \(10^6\) | 0.500 | 8.297 | 2.174 | \(1.00\cdot10^{-6}\) |
| high energy | 25 | \(10^6\) | 0.500 | 17.448 | 6.528 | \(1.00\cdot10^{-6}\) |

The key finding is negative but useful: at realistic representative exponents, the inherited endpoint-error windows are macroscopic in these normalized units and astronomically larger than the mean-spacing proxy.  The exact integral threshold decreases with \(n\), but slowly enough that the local corollary is mesoscopic/global rather than local-statistical.

![normalized Weyl-subtraction and rigidity thresholds compared with mean spacing](reports/figures/m16_window_threshold_phase_diagram.png)

The density plot confirms the edge/bulk split:

![density F prime near the spectral edge compared with the square-root edge asymptotic and high-energy limit](reports/figures/m16_edge_vs_bulk_density.png)

## Interpretation Against Key Questions

**Q1. Lower bound on \(\Delta\).**  The sufficient scale is the exact integral threshold
\[
(2g-2)(F(\Lambda+\Delta)-F(\Lambda))\gg n^{-\alpha_W}(\Lambda+\Delta)^{1/2+\epsilon}.
\]
In the bulk this linearizes to \(\Delta\gg n^{-\alpha_W}\Lambda^{1/2+\epsilon}/((2g-2)F'(\Lambda))\).

**Q2. Edge versus bulk.**  The edge is different because \(F'(1/4)=0\).  The edge main term starts as \(\Delta^{3/2}\), giving the weaker exponent scale \(n^{-2\alpha_W/3}\) before constants and endpoint-energy factors.

**Q3. Rigidity-window consequence.**  Rigidity gives deterministic window inclusion after expansion by \(\delta_R\).  It is useful for transferring mesoscopic count control between random and reference spectra only when the window length is larger than the displacement scale.

**Q4. Multiplicity or cluster-size bound.**  The result gives no sharp multiplicity bound.  A cluster at the rigidity scale can still contain a deterministic Weyl mass of order \(n^{1-\alpha_R}\) in the bulk, far above \(O(1)\).

## Next Research Question

The first genuinely new local-statistics question is not another endpoint-subtraction corollary.  It is whether a trace or pre-trace variance estimate can be localized to spectral windows below the global Weyl-error scale, ideally approaching a power of the mean spacing.  That would require new input about windowed trace statistics or eigenvalue correlations; it is not a consequence of the current global Weyl and rigidity theorem alone.

## Non-Claims

- M16 does not prove microscopic local statistics.
- It does not optimize Kim--Tao constants or infer unspecified theorem constants numerically.
- It does not produce exact multiplicity bounds.
- It does not reopen the M10-M15 aggregate quotient-family machinery.
