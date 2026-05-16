---
title: "Random Hyperbolic Surface Spectral Rigidity — cycles 43-45"
date: "2026-05-16"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# Random Hyperbolic Surface Spectral Rigidity — cycles 43-45

## Abstract

Cycles 43-45 completed two pieces of the long-exposure campaign and opened no new unvalidated claim. Cycle 43 closed the proof gap left by the Schreier variance mechanism: for the independent two-permutation Schreier benchmark, fixed nontrivial reduced word pairs have bounded fixed-point covariance. Cycle 44 consolidated the Schreier work from M30-M32 into a standalone theorem package. Cycle 45 returned to Kim--Tao surface-facing consequences and extracted a fixed positive-width spectral-window count corollary from endpoint subtraction in Theorem 1.

The main theorem-grade benchmark result is:

$$
\mathbb{E}\left[n^{-1}\operatorname{Tr}(A_n^k)\right] = m_k + O_k(n^{-1}),
\qquad
\operatorname{Var}\left(n^{-1}\operatorname{Tr}(A_n^k)\right)=O_k(n^{-2}),
$$

for fixed $k$, where

$$
A_n=P_a+P_a^{-1}+P_b+P_b^{-1}
$$

and $P_a,P_b$ are independent uniform permutations. This is a finite free-Schreier theorem only. It is not a Kim--Tao random hyperbolic cover theorem.

The main surface-facing corollary from cycle 45 is: for fixed $1/4\le a<b$,

$$
N_{X_n}([a,b])
=(2g-2)n(F(b)-F(a))
+O_\epsilon(n^{1-\alpha_W}b^{1/2+\epsilon}).
$$

Because $F(b)-F(a)>0$ for fixed positive-width intervals, the relative error is $O(n^{-\alpha_W})$ up to fixed interval and energy constants. This is a fixed-window count asymptotic, not a variance result, limiting law, level-repulsion theorem, or shrinking-window statistic.

## Introduction

The campaign studies Kim and Tao's paper `2603.01127`, "Eigenvalue rigidity of hyperbolic surfaces in the random cover model." Earlier cycles reconstructed the paper, built proof ledgers, explored shrinking-window obstructions, and developed a finite Schreier benchmark based on random permutations.

Cycles 40-42 had left two active directions:

- the Schreier benchmark had a validated variance mechanism but still needed a proof for arbitrary fixed reduced word pairs;
- the surface-facing branch still needed fixed non-shrinking spectral statistics separated from the harder shrinking-window problem.

Cycles 43-45 addressed these directions in sequence:

- Cycle 43 / M32 proved the fixed-pair covariance lemma for the Schreier benchmark.
- Cycle 44 / M33 packaged M30-M32 into a standalone theorem-grade Schreier benchmark.
- Cycle 45 / M34 derived and classified fixed positive-width spectral-window count asymptotics from Kim--Tao Theorem 1.

The report follows that order.

## Approach

The reporting method was consolidation, not re-audit. The source record consisted of nine cycle sessions:

| Cycle | Role | Session ID | Content |
|---|---|---|---|
| 43 | researcher | `1607a34a-d480-47ae-81f6-93f573b0fbd5` | M32 fixed-pair covariance task definition |
| 43 | worker | `16b90bb7-190d-4699-bfae-e3fd0bf1b157` | M32 proof package and checker outputs |
| 43 | auditor | `c0124064-f822-45ed-8e31-8051c3fcb2c3` | M32 validation after wording repair |
| 44 | researcher | `f8317168-5633-4be7-b43a-741d97059109` | M33 package synthesis task definition |
| 44 | worker | `c1f7d747-3769-4a30-b906-e389a2121d71` | M33 theorem package outputs |
| 44 | auditor | `9dcce388-1881-4fed-ad7f-94033d18451c` | M33 validation |
| 45 | researcher | `67814750-4305-4b96-b654-c741d30d11f8` | M34 fixed-window spectral-statistics task definition |
| 45 | worker | `b5075c1c-6f86-4d77-a7bd-d0c770300642` | M34 fixed-window package outputs |
| 45 | auditor | `415665c3-84c8-4073-8ed9-79f8690d12ea` | M34 validation after figure-link repair |

No `REFERENCES.md` file was present in the workspace. The References section therefore lists local source artifacts and session IDs rather than global numbered citations.

## Source Inventory and Timeline

Cycle 43 began with the M31 gap: M31 had shown, through checked pair classes for $k=2,4,6$, that the Schreier variance should scale like $O_k(n^{-2})$, but it had not proved the fixed-pair covariance lemma for arbitrary fixed nontrivial reduced word pairs. The researcher session `1607a34a-d480-47ae-81f6-93f573b0fbd5` directed the worker to prove or obstruct:

$$
\operatorname{Cov}(\operatorname{Fix}(u),\operatorname{Fix}(v))=O_{u,v}(1).
$$

The worker session `16b90bb7-190d-4699-bfae-e3fd0bf1b157` produced the M32 proof ledger, report, final theorem statement, checker script, tests, CSV outputs, and two figures. The auditor session `c0124064-f822-45ed-8e31-8051c3fcb2c3` validated M32 after one moderate repair: the documents and checker were revised to distinguish the proof-level quotient-template lemma from bounded representative computational checks.

Cycle 44 used M32 to close the Schreier benchmark branch. The researcher session `f8317168-5633-4be7-b43a-741d97059109` asked for a standalone theorem package combining M30 expectation results, M31 variance expansion, and M32 covariance. The worker session `c1f7d747-3769-4a30-b906-e389a2121d71` produced the M33 proof ledger, extension report, final theorem statement, claim ledger, dependency edges, artifact index, scope firewall, and three figures. The auditor session `9dcce388-1881-4fed-ad7f-94033d18451c` validated M33. A ledger timestamp issue had already been repaired by the worker and did not affect theorem content.

Cycle 45 returned to surface-facing consequences. The researcher session `67814750-4305-4b96-b654-c741d30d11f8` asked what fixed positive-width spectral count statements follow from Kim--Tao Theorem 1. The worker session `b5075c1c-6f86-4d77-a7bd-d0c770300642` produced the M34 proof ledger, report, final statement, script, tests, CSV tables, and three figures. The auditor session `415665c3-84c8-4073-8ed9-79f8690d12ea` validated M34 after fixing three Markdown figure links in the extension report.

## Finding 1: M32 Proved the Schreier Fixed-Pair Covariance Lemma

M32 proved the missing fixed-pair covariance lemma for the two-permutation Schreier benchmark.

The model is:

$$
A_n=P_a+P_a^{-1}+P_b+P_b^{-1},
$$

where $P_a$ and $P_b$ are independent uniform permutations of $[n]$. For a word $u$ in the free group, $\operatorname{Fix}(u)$ denotes the number of fixed points of the permutation obtained by substituting $P_a,P_b$ and their inverses into $u$.

The M32 theorem is:

$$
\operatorname{Cov}(\operatorname{Fix}(u(P_a,P_b)),\operatorname{Fix}(v(P_a,P_b)))=O_{u,v}(1)
$$

for fixed nontrivial reduced words $u,v$.

The proof uses quotient templates. A word trajectory gives labelled constraints for the random permutations. After identifying trajectory vertices, a conflict-free quotient template $H$ has:

- $V(H)$ quotient vertices;
- $C_a(H)$ distinct directed $a$-constraints;
- $C_b(H)$ distinct directed $b$-constraints.

The M4 labelled-template expectation identity assigns the main exponent

$$
V(H)-C_a(H)-C_b(H).
$$

M32's key lemma is:

$$
V(H)-C_a(H)-C_b(H)\le 0.
$$

The reason is that after cyclic reduction, each conflict-free edge-containing quotient component contains a nonempty closed labelled trajectory. Every quotient vertex in that trajectory has at least one outgoing labelled constraint. Therefore the total number of distinct labelled constraints is at least the number of quotient vertices:

$$
C_a(H)+C_b(H)\ge V(H).
$$

Templates with partial-injection conflicts contribute zero. Equal, inverse, cyclic-conjugate, and shared-power word pairs can change constants, but not the exponent.

The companion computation was framed as an audit harness, not as the proof itself. It generated:

- `data/extension_candidates/m32_pair_quotient_classification.csv`: 90 length/class rows through reduced length 6;
- `data/extension_candidates/m32_covariance_exponent_proof_checks.csv`: 180 same-basepoint and distinct-basepoint representative audit rows;
- `data/extension_candidates/m32_variance_theorem_implication.csv`: theorem implication and scope-firewall rows.

![Maximum same-basepoint and distinct-basepoint exponent by pair class and word length.](reports/figures/m32_pair_quotient_exponent_map.png)

![Logical dependency from the labelled-template expectation identity and the M31 variance expansion to the fixed-k variance theorem.](reports/figures/m32_variance_theorem_dependency_map.png)

The auditor validated the result after the proof/checker distinction was repaired. The final decision was `VALIDATED`.

## Finding 2: M33 Consolidated the Schreier Benchmark into a Standalone Theorem Package

M33 turned M30-M32 into one auditable theorem package for fixed $k$.

The trace expansion is:

$$
\operatorname{Tr}(A_n^k)
=
\sum_{w\in\{a,a^{-1},b,b^{-1}\}^k}
\operatorname{Fix}(w(P_a,P_b)).
$$

Words that freely reduce to the identity have $\operatorname{Fix}(w)=n$ deterministically. They give the tree moment $m_k$, the number of length-$k$ closed walks at the root of the infinite 4-regular tree. M30 had regenerated:

| $k$ | $m_k$ |
|---:|---:|
| 0 | 1 |
| 1 | 0 |
| 2 | 4 |
| 3 | 0 |
| 4 | 28 |
| 5 | 0 |
| 6 | 232 |
| 8 | 2092 |
| 10 | 19864 |

The M33 package states:

$$
\mathbb{E}\left[n^{-1}\operatorname{Tr}(A_n^k)\right]=m_k+O_k(n^{-1}),
$$

and

$$
\operatorname{Var}\left(n^{-1}\operatorname{Tr}(A_n^k)\right)=O_k(n^{-2}).
$$

The variance proof combines:

- M31's paired expansion,

$$
\operatorname{Var}(n^{-1}\operatorname{Tr}(A_n^k))
=
n^{-2}\sum_{u,v}\operatorname{Cov}(\operatorname{Fix}(u),\operatorname{Fix}(v));
$$

- deterministic tree-word separation, which removes covariance terms involving freely reducing identity words;
- M32's fixed-pair bound $\operatorname{Cov}(\operatorname{Fix}(u),\operatorname{Fix}(v))=O_{u,v}(1)$ for nontrivial reduced pairs;
- the fact that there are only finitely many length-$k$ words for fixed $k$.

The generated claim ledger contained seven rows: fixed-$k$ expectation, deterministic tree-word separation, paired variance expansion, fixed-pair covariance, fixed-$k$ variance, M30 numerical slopes as illustrative evidence, and a no-transfer firewall.

![Theorem order `O_k(n^{-2})` shown beside M30 empirical centered-trace variance slopes for `k=2,4,6`.](reports/figures/m33_schreier_variance_package_summary.png)

![Dependency graph from M4 and M30-M32 to the final fixed-k Schreier expectation and variance theorem.](reports/figures/m33_schreier_theorem_dependency_graph.png)

![Boundary between proved two-permutation Schreier benchmark statements and non-claimed hyperbolic-cover transfer.](reports/figures/m33_schreier_scope_firewall.png)

The M33 decision was:

```text
preserve_as_standalone_benchmark_theorem_package
```

The auditor validated M33. The scope firewall remained explicit: the theorem is for independent uniform permutations in the free-Schreier benchmark only. It does not prove a Kim--Tao random hyperbolic cover result, a Selberg trace transfer, an adjacency-to-Laplacian theorem, a surface-group quotient-family estimate, or shrinking-window local spectral statistics.

## Finding 3: M34 Derived Fixed Non-Shrinking Spectral Count Corollaries

M34 returned to the Kim--Tao surface setting and asked what fixed positive-width spectral count statements already follow from Theorem 1.

For $\Lambda\ge 1/4$, define

$$
F(\Lambda)=\int_0^{\sqrt{\Lambda-1/4}} r\tanh(\pi r)\,dr.
$$

The Weyl-law ledger gives, on the Kim--Tao high-probability event,

$$
N_{X_n}([1/4,\Lambda])
=
(2g-2)nF(\Lambda)
+
O_\epsilon\left(n^{1-\alpha_W}\Lambda^{1/2+\epsilon}\right).
$$

For a fixed interval $I=[a,b]$ with $1/4\le a<b$, simultaneous endpoint subtraction gives:

$$
N_{X_n}([a,b])
=
(2g-2)n(F(b)-F(a))
+
O_\epsilon\left(n^{1-\alpha_W}b^{1/2+\epsilon}\right).
$$

Since $F(b)-F(a)>0$ for fixed positive-width intervals, the main term is order $n$. The relative error is therefore:

$$
O_\epsilon\left(
n^{-\alpha_W}
\frac{b^{1/2+\epsilon}}{(2g-2)(F(b)-F(a))}
\right),
$$

which is $O(n^{-\alpha_W})$ after fixing $a,b$, $g$, and $\epsilon$.

At the spectral edge,

$$
F(1/4+\Delta)-F(1/4)
=
\frac{\pi}{3}\Delta^{3/2}
+
O(\Delta^{5/2}).
$$

Thus fixed $\Delta>0$ still gives an order-$n$ main term. If $\Delta=n^{-d}$, however, the window is shrinking with $n$ and returns to the M16-M25 obstruction branch. M34 explicitly excludes those rows from its theorem-level scope.

The centered version,

$$
N_{X_n}([a,b])-(2g-2)n(F(b)-F(a))
=
O_\epsilon(n^{1-\alpha_W}b^{1/2+\epsilon}),
$$

is also theorem-level, but only as a deterministic high-probability error bound. It is not a variance asymptotic or a limiting distribution.

The generated threshold table included fixed edge-adjacent, near-edge, bulk, wide-bulk, and high-energy windows, plus excluded shrinking-window comparison rows. For the representative theorem-shape model in the generated data, all fixed positive-width rows had relative exponent `-0.006`, while shrinking rows were marked `outside_m34_scope`.

![Relative error exponent for fixed-width spectral windows across edge, bulk, and high-energy regimes.](reports/figures/m34_fixed_window_relative_error.png)

M34 also compared endpoint subtraction with rigidity-location control. Rigidity gives interval inclusion after an $n^{-\alpha_R}$ expansion, but for fixed windows it does not sharpen the count asymptotic beyond endpoint subtraction unless a sharper deterministic reference-count estimate is added.

![Comparison of endpoint-subtraction and rigidity-location control for fixed non-shrinking intervals.](reports/figures/m34_endpoint_vs_rigidity_map.png)

The classification table preserved fixed-window endpoint counts and centered deterministic bounds, classified rigidity comparison as bookkeeping, excluded shrinking windows, and listed variance asymptotics, limiting laws, level repulsion, and local universality as no-claim rows.

![Classification of fixed-window statements into theorem-level corollaries, bookkeeping, and new-input-required claims.](reports/figures/m34_window_regime_classification.png)

The M34 decision was:

```text
advance_fixed_window_corollary_preserve_no_local_statistics_claim
```

The auditor validated M34 after fixing Markdown figure links in the extension report.

## Discussion

Cycles 43-45 separate two kinds of progress.

First, the Schreier benchmark branch is now closed as a theorem-grade finite-model result. M30 supplied fixed-$k$ expectation and tree moments. M31 supplied the paired variance expansion and small-$k$ mechanism. M32 proved the missing fixed-pair covariance lemma. M33 consolidated the package. The result is useful because it shows a complete trace-method pattern in a tractable random-permutation model: deterministic tree-word subtraction, quotient-template expectation bounds, and normalized variance decay.

Second, the surface-facing M34 result is legitimate but deliberately modest. It extracts fixed positive-width spectral-window count asymptotics from Kim--Tao Theorem 1 by endpoint subtraction. This gives a macroscopic spectral count corollary with polynomial relative error. It does not address the harder local-statistics problem, because no variance, correlation, or limiting distribution input is present.

The campaign posture after cycle 45 is therefore:

- The Schreier benchmark is a closed finite-model theorem package.
- Kim--Tao theorem-consequence mining now includes multiplicity/cluster bookkeeping, Theorem 2 mass consequences, fixed-cutoff local mass, and fixed positive-width spectral counts.
- The open surface-facing bottleneck remains the actual surface-group quotient-family coefficient/variation theorem or obstruction for the Kim--Tao Corollary 3.4 / Lemma 3.3 numerator.

## Open Questions

1. Can the surface-group quotient-family coefficient/variation problem be stated and attacked directly for the actual Kim--Tao numerator rather than through free-Schreier analogies?

2. Is there a new trace or pre-trace variance input strong enough to reopen shrinking spectral windows beyond the M16-M25 obstruction chain?

3. Can the fixed-window M34 corollary be used as a clean baseline for future variance investigations without being mistaken for a local-statistics theorem?

4. Is there a publication-facing way to present the Schreier benchmark as a standalone random-permutation theorem package that usefully informs random-cover trace bookkeeping while preserving the no-transfer boundary?

## References

No `REFERENCES.md` file was present in the workspace during this report. The sources used here are local artifacts and session records:

- Kim--Tao paper files: `2603.01127.pdf`, `2603.01127.txt`.
- Cycle 43 sessions: `1607a34a-d480-47ae-81f6-93f573b0fbd5`, `16b90bb7-190d-4699-bfae-e3fd0bf1b157`, `c0124064-f822-45ed-8e31-8051c3fcb2c3`.
- Cycle 44 sessions: `f8317168-5633-4be7-b43a-741d97059109`, `c1f7d747-3769-4a30-b906-e389a2121d71`, `9dcce388-1881-4fed-ad7f-94033d18451c`.
- Cycle 45 sessions: `67814750-4305-4b96-b654-c741d30d11f8`, `b5075c1c-6f86-4d77-a7bd-d0c770300642`, `415665c3-84c8-4073-8ed9-79f8690d12ea`.
- M32 artifacts: `docs/proof_ledger/schreier_fixed_pair_covariance_lemma.md`, `reports/extension_candidates/m32_schreier_fixed_pair_covariance_lemma.md`, `reports/final/schreier_variance_theorem_statement.md`.
- M33 artifacts: `docs/proof_ledger/schreier_benchmark_theorem_package.md`, `reports/extension_candidates/m33_schreier_benchmark_package_synthesis.md`, `reports/final/schreier_benchmark_theorem_package.md`.
- M34 artifacts: `docs/proof_ledger/finite_nonshrinking_spectral_statistics.md`, `reports/extension_candidates/m34_finite_nonshrinking_spectral_statistics.md`, `reports/final/nonshrinking_statistics_followup_statement.md`.
- Audit input supplied for Cycle 45 / M34.

## Appendix: Implementation Details

### Code Organization

Cycle 43 added or used:

- `scripts/prove_schreier_fixed_pair_covariance.py` (491 lines)
- `tests/test_schreier_fixed_pair_covariance.py` (99 lines)

Cycle 44 added or used:

- `scripts/build_schreier_benchmark_package.py` (311 lines)
- `tests/test_schreier_benchmark_package.py` (81 lines)

Cycle 45 added or used:

- `scripts/analyze_finite_nonshrinking_spectral_statistics.py` (359 lines)
- `tests/test_finite_nonshrinking_spectral_statistics.py` (100 lines)

### Generated Data

M32 generated:

- `data/extension_candidates/m32_pair_quotient_classification.csv` — 91 lines including header.
- `data/extension_candidates/m32_covariance_exponent_proof_checks.csv` — 181 lines including header.
- `data/extension_candidates/m32_variance_theorem_implication.csv` — 5 lines including header.

M33 generated:

- `data/final/m33_schreier_package_artifact_index.csv` — 26 lines including header.
- `data/final/m33_schreier_theorem_claim_ledger.csv` — 8 lines including header.
- `data/final/m33_schreier_dependency_edges.csv` — 11 lines including header.
- `data/final/m33_schreier_scope_firewall.csv` — 8 lines including header.

M34 generated:

- `data/extension_candidates/m34_fixed_window_thresholds.csv` — 64 lines including header.
- `data/extension_candidates/m34_fixed_window_classification.csv` — 8 lines including header.
- `data/extension_candidates/m34_endpoint_vs_rigidity_comparison.csv` — 16 lines including header.

### Figure Inventory

M32 figures:

- `reports/figures/m32_pair_quotient_exponent_map.png` — 1669 x 863.
- `reports/figures/m32_variance_theorem_dependency_map.png` — 1570 x 756.

M33 figures:

- `reports/figures/m33_schreier_theorem_dependency_graph.png` — 2700 x 1170.
- `reports/figures/m33_schreier_scope_firewall.png` — 2160 x 900.
- `reports/figures/m33_schreier_variance_package_summary.png` — 1260 x 900.

M34 figures:

- `reports/figures/m34_fixed_window_relative_error.png` — 1475 x 900.
- `reports/figures/m34_endpoint_vs_rigidity_map.png` — 1260 x 864.
- `reports/figures/m34_window_regime_classification.png` — 1512 x 900.

### Validation Results

The M32 audit reported:

- `py_compile`: passed.
- `scripts/prove_schreier_fixed_pair_covariance.py`: passed.
- `tests/test_schreier_fixed_pair_covariance.py`: passed.
- Both M32 figures: nonblank.
- `promise_check`: passed with historical warnings.
- `org_check`: passed with historical warnings.

The M33 audit reported:

- `py_compile`: passed.
- `scripts/build_schreier_benchmark_package.py`: regenerated 25 artifact rows, 7 claim rows, 10 dependency rows, 7 firewall rows, and 3 figures.
- `tests/test_schreier_benchmark_package.py`: passed.
- All M33 figures: nonblank.
- `promise_check`: passed with `events: 130, plan milestones: 33`, historical warnings only.
- `org_check`: passed with historical warnings only.

The M34 audit reported:

- `py_compile`: passed.
- `scripts/analyze_finite_nonshrinking_spectral_statistics.py`: regenerated 63 threshold rows, 7 classification rows, 15 endpoint-vs-rigidity rows, and 3 figures.
- `tests/test_finite_nonshrinking_spectral_statistics.py`: passed.
- Targeted invariant checks: passed.
- Figure checks and repaired report links: passed.
- `promise_check`: passed with `events: 134, plan milestones: 34`, historical warnings only.
- `org_check`: passed with historical warnings only.

After updating `MANIFEST.md`, the reporter reran:

- `python3 -m long_exposure.tools.promise_check .`
  - Result: passed with `events: 134, plan milestones: 34`.
  - Warnings were historical orphan cycle reports and old `docs/paper_map/` canonicalization.
- `python3 -m long_exposure.tools.org_check .`
  - Result: passed with historical root-file and old docs-figure warnings.
- `wc -l MANIFEST.md`
  - Result: 191 lines.

### Manifest Snapshot

`MANIFEST.md` was replaced with a cycles 43-45 snapshot. There was no `## Key Files` section to preserve.

Current manifest totals:

- 43 Python scripts, 12,701 lines.
- 35 Python tests, 2,914 lines.
- 94 canonical CSV datasets under `data/`.
- 83 PNG figures under `reports/figures/`.
- 195 Markdown/DOT/PNG documentation/report artifacts under `docs/`, `reports/`, and `audits/`.
- 134 promise ledger events.
- 34 plan milestones.

### Cross-Reference Map

- M4 labelled-template expectation identity -> M32 fixed-pair covariance lemma.
- M31 paired variance expansion -> M32 fixed-$k$ variance consequence.
- M30 expectation/tree moments + M31 variance expansion + M32 covariance lemma -> M33 standalone Schreier theorem package.
- M16 endpoint subtraction -> M34 fixed-window count asymptotic.
- M34 shrinking-window exclusion -> M16-M25 shrinking-window obstruction branch.

### Remaining Scope Boundaries

- M32-M33 do not prove random hyperbolic cover, Selberg trace, surface-group quotient-family, adjacency-to-Laplacian, or shrinking-window results.
- M34 does not prove variance asymptotics, limiting laws, level repulsion, local universality, or shrinking-window statistics.
- The main open surface-facing problem remains the actual Kim--Tao surface-group quotient-family coefficient/variation theorem or obstruction.
