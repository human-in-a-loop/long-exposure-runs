---
title: "Random Hyperbolic Surface Spectral Rigidity — cycles 37-39"
date: "2026-05-16"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# Random Hyperbolic Surface Spectral Rigidity — cycles 37-39

## Abstract

Cycles 37-39 moved the campaign out of the fixed-energy local-window branch and into direct theorem-consequence work. The previous branch had been preserved as a follow-up problem in M25 because further progress required either a new localized Corollary 3.4 coefficient-variation theorem or a new noncompact trace-tail architecture. Cycle 37 therefore re-ranked the remaining extension directions and selected a conservative next target: multiplicity and spectral-cluster corollaries from Kim--Tao Theorem 1.

Cycle 38 carried out that target. It proved a deterministic transport statement: if random eigenvalues stay within a rigidity radius of deterministic reference locations, then any random spectral cluster is bounded by the number of reference locations in the corresponding expanded interval. This gives theorem-level multiplicity and cluster bounds, but the audit validated the branch as useful bookkeeping rather than a new local-statistics improvement. The bounds remain at the already understood rigidity and endpoint scales.

Cycle 39 then tested the next theorem-level input, Kim--Tao Theorem 2 on eigenfunction delocalization. It derived three deterministic corollaries: $L^p$ interpolation, small-set mass upper bounds, and effective-support lower bounds. After an audit repair to row-level mass classification, the branch was validated as a useful theorem-level corollary package. At fixed energy, Theorem 2 excludes concentration of a normalized eigenfunction on sets below volume scale $n^{2\alpha}$ up to constants. This is distinct from M27's eigenvalue-count bookkeeping, but it is still a corollary package rather than a new proof mechanism.

No `REFERENCES.md` file exists in the workspace. The references section therefore lists the local paper files, session IDs, reports, proof ledgers, generated data, and figures used in this report.

## Introduction

The research campaign studies Kim and Tao's paper *Eigenvalue rigidity of hyperbolic surfaces in the random cover model*, using the local files `2603.01127.pdf` and `2603.01127.txt` as the primary source. Earlier cycles reconstructed the paper's proof architecture, built toy and formal probes, and explored extension routes.

The immediate background for cycles 37-39 is the closure of the fixed-energy shrinking local-window route. By M25, the campaign had identified the remaining compact-support local-window problem as a precise but difficult follow-up theorem: one would need actual coefficient-variation or small-$x$ control for the localized Corollary 3.4 numerator in the surface-group quotient family. M25 also identified a separate noncompact route, but that route would require a new trace-tail theorem. The audited decision was not to continue with another same-axis local-window empirical cycle.

The work reported here therefore asks a different question: what theorem-level consequences remain available from the already reconstructed Kim--Tao results, without solving the M25 open theorem?

The answer across these cycles is:

- M26 selected the next branch by scoring six post-local candidates.
- M27 extracted rigidity-scale multiplicity and cluster bounds from Theorem 1.
- M28 extracted $L^p$, small-set mass, and effective-support corollaries from Theorem 2.

## Approach

The report follows the chronological sequence of the three cycles.

Cycle 37, M26, was a branch-selection cycle. It scored candidate branches by mathematical value, tractability, artifact readiness, dependence on the unresolved M25 theorem, novelty, and risk. Its role was not to prove a new theorem, but to choose the next theorem-level target with an explicit rationale.

Cycle 38, M27, used Kim--Tao Theorem 1 as the only random-cover input. Theorem 1 is the eigenvalue rigidity statement: on a high-probability event, random-cover eigenvalues remain close to deterministic reference locations. M27 converted that displacement control into interval and multiplicity bounds by deterministic counting.

Cycle 39, M28, used Kim--Tao Theorem 2 as the only random-cover input. Theorem 2 is the eigenfunction delocalization statement: for $L^2$-normalized eigenfunctions below energy $\Lambda$, the sup norm is bounded by a polynomially decaying factor in the cover degree $n$, with explicit $\Lambda$ losses. M28 converted that amplitude bound into standard norm and mass-distribution consequences.

The work was validated by cycle auditors. M27 and M28 each required one audit repair before validation: M27 repaired a decision-label issue for comparison-only rows, and M28 repaired row-level classifications for Remark 1.1 mass rows.

## Source Inventory and Timeline

**Cycle 37 / M26 researcher session `3d1f6457-01d1-4346-81e8-18d729d8761d`.**
This session defined `M26-post-local-extension-reprioritization`. It framed the pivot after M25 and required a deterministic scoring package for at least five branches: multiplicity and spectral clusters, eigenfunction $L^p$/mass consequences, finite non-shrinking spectral statistics, Schreier benchmark theoremization, adjacent-model transfer, and M25-dependent local-window continuation.

**Cycle 37 / M26 worker session `3aa7a047-79c7-4693-a4d5-b1b3487d5469`.**
The worker built the M26 package: `scripts/score_post_local_extension_candidates.py`, `tests/test_post_local_extension_candidates.py`, two CSV files, two figures, the extension report, the proof-ledger attachment-point note, and a ranked follow-up list. The scorer produced six candidate rows and thirteen dependency rows. The unique recommendation was `M27-multiplicity-and-cluster-corollaries-from-rigidity`.

**Cycle 37 / M26 auditor session `30ebba56-222e-45ef-bb37-2e1d89da85fe`.**
The auditor validated M26 with no repair. The only minor comment was that one matrix figure used a shared color scale for positive-preference and inverse-preference axes, but the labels made the interpretation clear. The decision was `VALIDATED`.

**Cycle 38 / M27 researcher session `f07fa799-c6cf-466f-877e-0a72240a039e`.**
This session defined `M27-multiplicity-and-cluster-corollaries-from-rigidity`. It asked for deterministic cluster and multiplicity consequences from Theorem 1, with separate bulk, edge, and high-energy regimes, and with an explicit test of whether the result was genuinely new or only M16 endpoint-scale bookkeeping.

**Cycle 38 / M27 worker session `7d6a903e-969f-47dd-bdea-ba7d1e05f07c`.**
The worker built `docs/proof_ledger/multiplicity_cluster_from_rigidity.md`, `reports/extension_candidates/m27_multiplicity_cluster_corollaries.md`, `reports/final/multiplicity_cluster_followup_statement.md`, the analyzer and test files, two CSV files, and two figures. The generated decision was `preserve_as_bookkeeping_corollary`.

**Cycle 38 / M27 auditor session `7bfa9744-a44e-48f1-a8a8-c9229aba0b4d`.**
The auditor found one moderate issue: `m27_cluster_regime_classification.csv` encoded `advance_multiplicity_cluster_branch` for bounded-loss hypothetical rows, even though the branch-level decision was `preserve_as_bookkeeping_corollary`. The repair forced all classification decisions to preserve the branch decision and added regression coverage rejecting any generated `advance_multiplicity_cluster_branch` row. M27 was then validated.

**Cycle 39 / M28 researcher session `ae184418-bd03-426c-a3ea-478d1819a0eb`.**
This session defined `M28-theorem2-lp-mass-distribution-corollaries`. It asked for deterministic consequences of Theorem 2: $L^p$ interpolation, small-set mass upper bounds, effective-support lower bounds, separation of the direct $\Lambda^{3/2}$ theorem from the Remark 1.1 $\Lambda^{1/4+\epsilon}$ variant, and explicit rejection of unsupported conclusions such as quantum ergodicity or nodal claims.

**Cycle 39 / M28 worker session `968d246e-6f64-46ef-8780-93d0b9104b9d`.**
The worker built `docs/proof_ledger/theorem2_lp_mass_corollaries.md`, `reports/extension_candidates/m28_theorem2_lp_mass_corollaries.md`, `reports/final/theorem2_followup_statement.md`, the analyzer and test files, three CSV files, and two figures. The generated decision was `advance_theorem2_consequence_branch`.

**Cycle 39 / M28 auditor session `37a61811-f8e7-4403-802a-c7f26100773e`.**
The auditor found one moderate classification issue: the mass grid labeled every Remark 1.1 mass row as `direct_theorem2_corollary`, including vacuous high-energy rows. The repair made row classification depend on the computed small-set mass exponent, effective-support exponent, and set-volume exponent. Regression tests now ensure Remark mass rows receive consequence-level labels and are not labeled `direct_theorem2_corollary`. M28 was then validated.

## Findings

### Finding 1: M26 Chose a Conservative Post-Local Pivot

M26's main result was a branch decision, not a theorem. It scored six post-local candidates and selected M27 as the unique next milestone.

The ranked candidates were:

| Rank | Candidate | Classification | Reason for Placement |
|---:|---|---|---|
| 1 | Multiplicity and spectral-cluster consequences from rigidity | Kim--Tao corollary | Directly attached to Theorem 1, M2, and M16; no M25 theorem needed. |
| 2 | Eigenfunction $L^p$/mass-distribution consequences | Kim--Tao corollary | Directly attached to Theorem 2; likely deterministic but potentially useful. |
| 3 | Schreier benchmark theoremization | Toy/model evidence | Strong artifact readiness, but still toy-only without the M15 bridge. |
| 4 | Fixed-window non-shrinking spectral statistics | Kim--Tao corollary | Avoids shrinking-window obstruction but risks repackaging global rigidity. |
| 5 | Adjacent-model transfer | Requires new theorem | High value but too model-dependent for one cycle. |
| 6 | M25-dependent shrinking local-window continuation | Requires new theorem | Immediate next step remains the unresolved coefficient-variation or trace-tail theorem. |

The score table is stored in `data/extension_candidates/post_local_extension_candidate_scores.csv`, and the dependency table is stored in `data/extension_candidates/post_local_extension_candidate_dependencies.csv`.

![Ranked post-local extension candidates by value, tractability, dependency risk, and artifact readiness. The M25-dependent local-window branch is preserved but ranked last because its immediate next step is still an open theorem.](reports/figures/m26_post_local_candidate_matrix.png)

![Dependency map from validated Kim--Tao proof artifacts and Phase II results to post-local candidate branches. M27 attaches directly to Theorem 1 and prior rigidity/Weyl reconstruction.](reports/figures/m26_extension_dependency_map.png)

The audited decision was that this was a defensible pivot. The M25-dependent local-window branch remained preserved as a future problem, but it was explicitly deprioritized for immediate continuation.

### Finding 2: M27 Converted Rigidity Into Cluster Bounds, But Only at the Rigidity Scale

M27 derived a deterministic transport lemma from Theorem 1. Let $\mu_j$ denote random-cover eigenvalues and $\lambda_j$ denote deterministic reference locations. If, on a high-probability event,

\[
|\mu_j-\lambda_j|\le R_j,
\]

then any interval $I$ can contain only those random eigenvalues whose reference locations lie in an expanded interval. Using a uniform radius $R$ on the relevant spectral range,

\[
\#\{j:\mu_j\in I\}
\le
\#\{j:\lambda_j\in I^{+R}\}.
\]

For a single point, this becomes an exact multiplicity envelope:

\[
\operatorname{mult}_{X_n}(\lambda)
\le
\#\{j:|\lambda_j-\lambda|\le R\}.
\]

For Kim--Tao Theorem 1, the rigidity radius has the form

\[
R=C_\epsilon \Lambda_{\max}^{1/2+\epsilon}n^{-\alpha_R}.
\]

The deterministic reference locations are defined by

\[
F(\lambda_j)=\frac{j}{(2g-2)n},
\qquad
F(\Lambda)=\int_0^{\sqrt{\Lambda-1/4}} r\tanh(\pi r)\,dr.
\]

In the fixed bulk, where $\Lambda_0>1/4$,

\[
F'(\Lambda_0)
=
\frac12\tanh\left(\pi\sqrt{\Lambda_0-1/4}\right),
\]

so the zero-width multiplicity envelope becomes

\[
1+
2(2g-2)nF'(\lambda)
C_\epsilon\lambda^{1/2+\epsilon}n^{-\alpha_R}
+
O(nR^2).
\]

At the spectral edge, the bulk density approximation fails because $F'(1/4)=0$. The correct expansion is

\[
F(1/4+\Delta)=\frac{\pi}{3}\Delta^{3/2}+O(\Delta^{5/2}),
\]

which gives an edge envelope of the form

\[
1+(2g-2)n\frac{\pi}{3}(\Delta+R)^{3/2}
+
O(n(\Delta+R)^{5/2}).
\]

At high energy, $F'(\Lambda)\to 1/2$, while the radius grows like $\Lambda^{1/2+\epsilon}n^{-\alpha_R}$. The high-energy count is therefore dominated by the rigidity radius, not improved by density decay.

The generated classification table had 12 rows after audit repair. At $n=10^8$, representative proved-shape rows included:

| Regime | Classification | Decision |
|---|---|---|
| Edge $\Delta$ at the rigidity scale | `edge_endpoint_equivalent` | `preserve_as_bookkeeping_corollary` |
| Near fixed edge | `rigidity_scale_cluster_bound` | `preserve_as_bookkeeping_corollary` |
| Fixed bulk | `tautological_or_endpoint_only` | `preserve_as_bookkeeping_corollary` |
| High energy | `high_energy_loss_dominated` | `preserve_as_bookkeeping_corollary` |

![Log-log cluster-envelope scaling versus cover degree for bulk, edge, and high-energy representative energies. The envelopes remain at the rigidity scale for proved-shape representative exponents.](reports/figures/m27_cluster_bound_vs_n.png)

![Regime classification map at fixed representative cover degree. The post-audit decision rows preserve the branch-level decision rather than advancing comparison-only hypothetical rows.](reports/figures/m27_regime_phase_diagram.png)

The audited conclusion was that M27 is mathematically correct and theorem-level, but not a new local-statistics result. It bounds clusters and exact multiplicities by deterministic reference locations in a rigidity-expanded interval. It does not imply simplicity, level repulsion, microscopic statistics, or endpoint-beating local counts.

### Finding 3: M28 Produced a Theorem 2 Mass-Support Corollary Package

M28 turned to Kim--Tao Theorem 2, which controls eigenfunction amplitudes. For an $L^2$-normalized eigenfunction $u_j$ with eigenvalue below $\Lambda$, the direct Theorem 2 input has the form

\[
\|u_j\|_\infty
\le
C\Lambda^{3/2}n^{-\alpha}.
\]

Remark 1.1 gives a different high-energy tradeoff:

\[
\|u_j\|_\infty
\le
C_\epsilon\Lambda^{1/4+\epsilon}n^{-\alpha'}.
\]

M28 kept these two models separate because the improved $\Lambda$ exponent comes with a different $n$ exponent and constant.

Let $M_{\Lambda,n}$ denote either admissible amplitude envelope. Three deterministic consequences follow.

First, interpolation between $L^2$ and $L^\infty$ gives, for $2\le p\le\infty$,

\[
\|u\|_p
\le
\|u\|_\infty^{1-2/p}\|u\|_2^{2/p}
\le
M_{\Lambda,n}^{1-2/p}.
\]

The endpoint checks are exact: at $p=2$ this recovers $\|u\|_2=1$, and at $p=\infty$ it recovers Theorem 2.

Second, for any measurable set $A\subset X_n$,

\[
\int_A |u|^2
\le
\|u\|_\infty^2\operatorname{vol}(A)
\le
M_{\Lambda,n}^2\operatorname{vol}(A).
\]

This is nontrivial relative to the identity $\int_A |u|^2\le1$ when

\[
\operatorname{vol}(A)<M_{\Lambda,n}^{-2}.
\]

Third, if a measurable set $E$ carries mass $\theta$, then

\[
\theta
\le
\int_E |u|^2
\le
M_{\Lambda,n}^2\operatorname{vol}(E),
\]

so

\[
\operatorname{vol}(E)\ge \theta M_{\Lambda,n}^{-2}.
\]

At fixed energy in the direct Theorem 2 model, this gives

\[
\operatorname{vol}(E)\gtrsim_\Lambda \theta n^{2\alpha}.
\]

This is the main preserved consequence of M28: fixed-energy eigenfunctions cannot concentrate mass on sets of volume $o(n^{2\alpha})$, up to constants. Since the cover volume is order $n$, this is partial delocalization rather than equidistribution.

The generated classification file contains six rows:

| Item | Classification | Meaning |
|---|---|---|
| Theorem 2 sup-norm input | `direct_theorem2_corollary` | The paper's input statement or Remark 1.1. |
| $L^p$ interpolation | `standard_interpolation` | Deterministic norm interpolation. |
| Small-set mass | `nontrivial_mass_delocalization` | Fixed-energy exclusion of concentration below polynomial volume. |
| High-energy limitations | `bookkeeping_only` | $\Lambda$ growth can erase the $n$ gain. |
| Quantum ergodicity/equidistribution claims | `unsupported_stronger_claim` | Sup-norm control alone does not force mass into specified regions. |
| Branch decision | `nontrivial_mass_delocalization` | Preserve the Theorem 2 consequence package. |

![Decay exponent for $L^p$ interpolation as a function of $p$. The exponent vanishes at $p=2$ and recovers the Theorem 2 exponent at $p=\infty$.](reports/figures/m28_lp_decay_by_p.png)

![Set-volume exponent phase diagram for the small-set mass envelope. The nontrivial region is where $M_{\Lambda,n}^2\operatorname{vol}(A)<1$.](reports/figures/m28_mass_scale_phase_diagram.png)

The audit repair mattered for downstream planning. Before repair, every Remark 1.1 mass row was classified as `direct_theorem2_corollary`, including vacuous high-energy rows. After repair, row labels depend on the computed mass exponent, effective-support exponent, and set-volume exponent. This prevents the report from presenting high-energy bookkeeping rows as direct theorem-level mass consequences.

The validated decision was `advance_theorem2_consequence_branch`, with a precise limitation: this is a corollary package, not a new proof mechanism.

## Discussion

The three cycles form a clean post-local sequence.

M26 prevented the campaign from drifting back into the local-window obstruction. It did this by scoring candidate branches and making the M25 dependency explicit. The best immediate target was not the most ambitious one; it was the one with the strongest attachment to validated proof artifacts and the least dependence on unresolved coefficient-variation input.

M27 then tested that target. The resulting multiplicity and cluster bounds are useful because they package Theorem 1 into a direct statement about observed random-cover spectral clusters. But the audit-confirmed branch decision is conservative: the bounds are transport bounds at the rigidity radius. They do not create new local spectral statistics.

M28 produced a stronger preserved consequence because Theorem 2 controls eigenfunction amplitude directly. The $L^p$ inequalities are standard interpolation, but the effective-support statement has a clear random-cover interpretation. At fixed energy, a normalized eigenfunction cannot place positive mass on a set much smaller than $n^{2\alpha}$ in volume. This is weaker than full-volume equidistribution but stronger in nature than M27's eigenvalue-count bookkeeping.

The cumulative lesson is that direct theorem-consequence branches are valuable for extracting clean corollaries and follow-up statements, but they should not be repeated indefinitely. After M27 and M28, the next high-value step should either exploit the internal pre-trace local-mass step behind Theorem 2 in a carefully scoped way, or pivot to a less bookkeeping-heavy direction such as finite non-shrinking spectral statistics or Schreier benchmark theoremization.

## Open Questions

1. **Can the Theorem 2 pre-trace local-mass intermediate be made into a standalone fixed-domain spatial theorem?**
   M28 records an internal proof-ledger statement for fundamental-domain cutoffs, but it did not elevate that to arbitrary moving sets or all balls. Doing so would require reopening the Proposition 4.1 cutoff architecture.

2. **Can finite non-shrinking spectral statistics produce more than global rigidity repackaging?**
   M26 ranked this below M27 and M28, but it remains a possible next branch if centered fixed-width statistics can avoid the shrinking-window support obstruction.

3. **Can the Schreier/random-regular benchmark branch be theoremized without overclaiming transfer to Kim--Tao?**
   M26 kept this branch viable as a toy/model theoremization path, but M15's bridge obstruction still blocks direct transfer to actual surface-group quotient families.

4. **Can the M25 local-window follow-up theorem be attacked directly?**
   The compact route requires localized Corollary 3.4 coefficient-variation or small-$x$ control for the actual folded surface-group quotient family. The noncompact route requires a trace-tail theorem with sufficient tail-rate dominance. Neither was pursued in cycles 37-39.

5. **What is the correct stopping point for direct corollary extraction?**
   M27 and M28 show that direct consequences are worth recording, but the campaign should avoid another cycle that only reclassifies deterministic interpolation or endpoint bookkeeping unless a genuinely new local-mass statement is extracted.

## References

No `REFERENCES.md` file was present in the workspace during this reporting pass. The following local sources were used.

- Kim--Tao paper files: `2603.01127.pdf`, `2603.01127.txt`.
- Cycle 37 sessions: researcher `3d1f6457-01d1-4346-81e8-18d729d8761d`, worker `3aa7a047-79c7-4693-a4d5-b1b3487d5469`, auditor `30ebba56-222e-45ef-bb37-2e1d89da85fe`.
- Cycle 38 sessions: researcher `f07fa799-c6cf-466f-877e-0a72240a039e`, worker `7d6a903e-969f-47dd-bdea-ba7d1e05f07c`, auditor `7bfa9744-a44e-48f1-a8a8-c9229aba0b4d`.
- Cycle 39 sessions: researcher `ae184418-bd03-426c-a3ea-478d1819a0eb`, worker `968d246e-6f64-46ef-8780-93d0b9104b9d`, auditor `37a61811-f8e7-4403-802a-c7f26100773e`.
- M26 artifacts: `reports/extension_candidates/m26_post_local_extension_reprioritization.md`, `docs/proof_ledger/post_local_branch_attachment_points.md`, `reports/final/post_local_followup_ranked_problem_list.md`, `data/extension_candidates/post_local_extension_candidate_scores.csv`, `data/extension_candidates/post_local_extension_candidate_dependencies.csv`.
- M27 artifacts: `reports/extension_candidates/m27_multiplicity_cluster_corollaries.md`, `docs/proof_ledger/multiplicity_cluster_from_rigidity.md`, `reports/final/multiplicity_cluster_followup_statement.md`, `data/extension_candidates/m27_cluster_bound_grid.csv`, `data/extension_candidates/m27_cluster_regime_classification.csv`.
- M28 artifacts: `reports/extension_candidates/m28_theorem2_lp_mass_corollaries.md`, `docs/proof_ledger/theorem2_lp_mass_corollaries.md`, `reports/final/theorem2_followup_statement.md`, `data/extension_candidates/m28_lp_bound_grid.csv`, `data/extension_candidates/m28_mass_distribution_grid.csv`, `data/extension_candidates/m28_corollary_classification.csv`.

## Appendix: Implementation Details

### Code Organization

New or cycle-relevant scripts:

| File | Lines | Purpose |
|---|---:|---|
| `scripts/score_post_local_extension_candidates.py` | 324 | Scores post-local extension candidates after M25. |
| `scripts/analyze_multiplicity_cluster_bounds.py` | 240 | Computes M27 rigidity-scale cluster and multiplicity envelopes. |
| `scripts/analyze_theorem2_lp_mass_corollaries.py` | 247 | Computes M28 $L^p$, small-set mass, and support-corollary grids. |

New or cycle-relevant tests:

| File | Lines | Purpose |
|---|---:|---|
| `tests/test_post_local_extension_candidates.py` | 72 | Validates M26 candidate coverage, ranking, and unique recommendation. |
| `tests/test_multiplicity_cluster_bounds.py` | 72 | Validates M27 formulas, edge scaling, monotonicity, and repaired branch decision. |
| `tests/test_theorem2_lp_mass_corollaries.py` | 83 | Validates M28 interpolation endpoints, mass thresholds, unsupported-claim exclusions, and repaired Remark-row classifications. |

### Generated Data

| File | Rows Excluding Header | Notes |
|---|---:|---|
| `data/extension_candidates/post_local_extension_candidate_scores.csv` | 6 | M26 ranked candidates. |
| `data/extension_candidates/post_local_extension_candidate_dependencies.csv` | 13 | M26 dependency map rows. |
| `data/extension_candidates/m27_cluster_bound_grid.csv` | 72 | M27 cluster-envelope grid. |
| `data/extension_candidates/m27_cluster_regime_classification.csv` | 12 | M27 regime classification after audit repair. |
| `data/extension_candidates/m28_lp_bound_grid.csv` | 648 | M28 $L^p$ interpolation grid. |
| `data/extension_candidates/m28_mass_distribution_grid.csv` | 96 | M28 mass-distribution grid after audit repair. |
| `data/extension_candidates/m28_corollary_classification.csv` | 6 | M28 corollary and branch classifications. |

### Figure Inventory

| Figure | Dimensions | Used For |
|---|---:|---|
| `reports/figures/m26_post_local_candidate_matrix.png` | 1872x1044 | M26 candidate scoring matrix. |
| `reports/figures/m26_extension_dependency_map.png` | 2015x1188 | M26 dependency map. |
| `reports/figures/m27_cluster_bound_vs_n.png` | 1440x900 | M27 cluster envelope versus $n$. |
| `reports/figures/m27_regime_phase_diagram.png` | 1350x864 | M27 regime classification. |
| `reports/figures/m28_lp_decay_by_p.png` | 1440x900 | M28 $L^p$ decay exponents. |
| `reports/figures/m28_mass_scale_phase_diagram.png` | 1350x900 | M28 mass-scale phase diagram. |

### Validation Results

The final validation commands run during this reporter pass were:

```text
python3 -m long_exposure.tools.promise_check .
python3 -m long_exposure.tools.org_check .
```

`promise_check` exited successfully and reported:

```text
events: 110, plan milestones: 28
```

Its warnings were historical: one old noncanonical `docs/paper_map/` path and orphan prior cycle reports under `reports/cycles/`.

`org_check` exited successfully. Its warnings were historical root files and older figures under `docs/`.

The reporter also updated `MANIFEST.md` after gathering. The updated manifest has 156 lines and records the workspace snapshot through M28.

### Manifest Snapshot

After cycles 37-39, the manifest records:

| Category | Count |
|---|---:|
| Python scripts | 37 files, 10,302 lines |
| Python tests | 29 files, 2,376 lines |
| Canonical CSV datasets | 74 |
| PNG figures under `reports/figures/` | 67 |
| Markdown/DOT/PNG documentation and report artifacts | 159 |
| Promise ledger events | 110 |
| Plan milestones | 28 |

There was no `## Key Files` section in the previous manifest, so no protected final-reporter section needed preservation.

### Cross-Reference Map

| Origin | Consuming Artifact | Role |
|---|---|---|
| M25 local-window branch decision | M26 candidate scorer | Forces pivot away from same-axis local-window work. |
| M26 score table | M27 researcher brief | Selects multiplicity and cluster corollaries as next branch. |
| Kim--Tao Theorem 1 / M2 / M16 | M27 proof ledger and analyzer | Supplies rigidity radius and reference-density formulas. |
| M27 audit repair | M27 classification table and tests | Prevents comparison-only rows from advancing the branch. |
| M27 branch decision | M28 researcher brief | Moves from eigenvalue bookkeeping to eigenfunction delocalization consequences. |
| Kim--Tao Theorem 2 / M2 delocalization ledger | M28 proof ledger and analyzer | Supplies sup-norm input for $L^p$, mass, and support corollaries. |
| M28 audit repair | M28 mass grid and tests | Prevents vacuous Remark rows from being labeled direct theorem corollaries. |
| M28 final statement | Future branch planning | Preserves Theorem 2 mass-support corollary and points to pre-trace local-mass refinement or a new pivot. |
