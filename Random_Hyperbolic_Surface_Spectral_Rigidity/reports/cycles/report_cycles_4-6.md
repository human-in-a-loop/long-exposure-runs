---
title: "Random Hyperbolic Surface Spectral Rigidity — cycles 4-6"
date: "2026-05-15"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# Random Hyperbolic Surface Spectral Rigidity — cycles 4-6

## Abstract

Cycles 4-6 completed the proof-ledger phase for Kim--Tao's random-cover spectral rigidity paper and began the first computational probe phase. Cycle 4 reconstructed the Theorem 2 eigenfunction delocalization argument from the twisted pre-trace formula through the fourth-moment statistic, diagonal subtraction, probability conversion, and final $L^\infty$ bound. Cycle 5 consolidated the full `M2-proof-ledger` milestone by producing a unified Theorem 1 rigidity reconstruction, a cross-proof loss map, and a closure note accepted by audit. Cycle 6 opened `M3-computational-probes` with a reproducible random-permutation common-fixed-point benchmark.

The main decision made during these cycles was that `M2-proof-ledger` is now validated, narrowly for local proof reconstruction and quantitative dependency/loss accounting. The main new empirical result is a toy-level confirmation of the diagonal-subtraction mechanism: cyclic primitive-power word families have order-one common fixed-point counts, while rank-two pair families scale near $1/n$. The same experiment also found that naive multiword pointwise intersections are not a good model for the paper's eight-word folded-graph mechanism, because several composite word families collapse to the same fixed-point constraint as the pair $(a,b)$.

## Introduction

The campaign studies Elena Kim and Zhongkai Tao's paper *Eigenvalue rigidity of hyperbolic surfaces in the random cover model*, using the local files `2603.01127.pdf` and `2603.01127.txt`. Earlier cycles established the paper map and reconstructed the trace-side proof of Theorem 1 through Proposition 3.1. Cycles 4-6 continued from that state.

The report uses the following terms.

- `M2-proof-ledger` is the milestone for reconstructing the paper's main proof architecture, quantitative dependencies, and exponent losses.
- `M3-computational-probes` is the milestone for reproducible finite or toy computations that test mechanisms exposed by the proof ledger.
- $V_n$ is the fourth power of the centered local spectral mass appearing in the Theorem 2 pre-trace argument.
- $S$ is the primitive-power diagonal term subtracted from $V_n$ before applying the rank-two common-fixed-point estimate.
- $\alpha_W$ is the exponent in the uniform Weyl law; $\alpha_R$ is the possibly weaker eigenvalue-rigidity exponent after Weyl-law inversion near the spectral edge $\lambda=1/4$.

## Approach

The reporting pass gathered the specified cycle sessions, local artifacts, ledger events, figures, generated datasets, validation outputs, and the current workspace manifest. The source set included all nine requested cycle sessions:

- Cycle 4: researcher `9b69e544-cee2-427e-88a7-a2b32be2d4df`, worker `9a8d5232-7da5-416e-be1a-8515bcece60c`, auditor `dddcaf65-1172-4fa3-a859-9374ae0213b4`.
- Cycle 5: researcher `0bf32ed4-2866-4671-af3c-2f1b6f30f8ba`, worker `b5a3c22f-3083-4803-b8c6-1f8e8dee3dc2`, auditor `7dc50143-c79a-4b3c-8371-63f8e61aa904`.
- Cycle 6: researcher `40632ca0-1b63-4d2b-9bc8-c8baab1f4ae4`, worker `fe7f867c-00e3-47b8-a4cd-172c205ba885`, auditor `3229364f-0203-4038-8c82-32992a28250f`.

No `REFERENCES.md` file was present in the workspace, so this report cannot continue a global numbered bibliography. Sources are therefore cited by local paper file, artifact path, and session ID.

## Source Inventory and Timeline

### Cycle 4: Theorem 2 Delocalization Reconstruction

The Cycle 4 researcher brief identified the remaining proof-ledger gap as the eigenfunction side of the paper. The worker was directed to reconstruct Theorem 2 from the twisted pre-trace formula, define $V_n$ and $S$, explain Proposition 4.1 and Proposition 4.2, and build a dependency graph.

The worker produced six artifacts:

- `docs/proof_ledger/delocalization_proof_reconstruction.md`
- `docs/proof_ledger/eigenfunction_fourth_moment_ledger.md`
- `docs/proof_ledger/pretrace_diagonal_term.md`
- `docs/proof_ledger/theorem2_dependency_graph.dot`
- `docs/proof_ledger/theorem2_dependency_graph.png`
- `docs/proof_ledger/theorem1_theorem2_loss_comparison.md`

The dependency graph was rendered successfully.

![Dependency graph for Theorem 2 delocalization, showing the route from pre-trace formula and fourth-moment control to the final sup-norm estimate.](docs/proof_ledger/theorem2_dependency_graph.png)

The Cycle 4 audit validated the mathematics of the Theorem 2 slice. It also found one structured-state defect: the worker had briefly marked broad `M2-proof-ledger` as validated even though the plan still required final proof-ledger consolidation. The auditor fixed this by reopening `M2-proof-ledger` and marking it `in-progress`, preserving the Theorem 2 slice validation without closing the broad milestone.

### Cycle 5: M2 Proof-Ledger Closure

The Cycle 5 researcher brief stated that the remaining work was consolidation, not another deep proof audit. The required deliverable was a unified Theorem 1 reconstruction plus a plan-level closure note and cross-proof loss map.

The worker produced five artifacts:

- `docs/proof_ledger/rigidity_proof_reconstruction.md`
- `docs/proof_ledger/m2_loss_map.md`
- `docs/proof_ledger/m2_proof_ledger_closure.md`
- `docs/proof_ledger/m2_closure_dependency_graph.dot`
- `docs/proof_ledger/m2_closure_dependency_graph.png`

The closure graph was rendered successfully.

![M2 proof-ledger closure map linking validated Theorem 1 and Theorem 2 reconstruction artifacts to the plan-level milestone.](docs/proof_ledger/m2_closure_dependency_graph.png)

The Cycle 5 audit validated broad `M2-proof-ledger`, narrowly for local proof reconstruction and quantitative dependency/loss accounting. The audit emphasized that this did not validate `M3`, `M4`, `M5`, or `M6`, and that imported MPvH, Nau, and MP23 inputs remain black boxes for later external audit.

### Cycle 6: First M3 Computational Probe

The Cycle 6 researcher brief moved the campaign to `M3-computational-probes`. The target was a finite random-permutation common-fixed-point experiment, because the proof ledger had localized the main unresolved mechanism to common-fixed-point statistics and polynomial interpolation rather than direct numerical simulation of hyperbolic spectra.

The worker produced:

- `scripts/probe_common_fixed_points.py`
- `tests/test_permutation_word_eval.py`
- `data/polynomial_method/common_fixed_point_probe.csv`
- `data/polynomial_method/common_fixed_point_summary.csv`
- `reports/figures/m3_common_fixed_point_scaling.png`
- `reports/figures/m3_common_fixed_point_tails.png`
- `reports/computational_probes/m3_common_fixed_point_probe.md`

The final dataset contains 136,000 rows over 17 word families, four cover degrees, and 2,000 samples per cover degree. The two final figures were verified as readable `1280 x 800` PNGs.

![Mean common-fixed-point counts versus cover degree `n` for cyclic/diagonal and rank-two/noncyclic word families.](reports/figures/m3_common_fixed_point_scaling.png)

![Empirical tail behavior of normalized common-fixed-point counts across toy word families.](reports/figures/m3_common_fixed_point_tails.png)

The Cycle 6 audit validated the first benchmark and kept `M3-computational-probes` marked `in-progress`, not fully validated.

## Findings

### Finding 1: Theorem 2 Uses the Same Macro-Template as Theorem 1, but With New Local Fourth-Moment Structure

Cycle 4 reconstructed the Theorem 2 pipeline as:

```text
twisted pre-trace formula
-> centered local spectral mass
-> fourth power V_n
-> subtract primitive-power diagonal S
-> Proposition 4.2 eight-word polynomial approximation
-> Markov second-derivative q^{4 kappa} loss
-> Proposition 4.1
-> Chebyshev, fiber union, and window union
-> local L2 mass bound
-> Sobolev/elliptic conversion to L-infinity
```

This parallels Theorem 1 at the highest level: both proofs use compactly supported transforms, trace or pre-trace expansion, polynomial approximation in $1/n$, Markov brothers interpolation, and Chebyshev plus grid union. The difference is that Theorem 2 is local and fourth-moment based. It introduces $S$, an eight-word common-fixed-point statistic, a fiber union bound, and a final local-mass-to-pointwise conversion.

### Finding 2: The Diagonal Term `S` Is a Structural Subtraction

The Cycle 4 artifacts define $S$ as the primitive-power diagonal part of the fourth power of the centered pre-trace sum. In local notation, it sums over four nonzero powers of one primitive element. Its purpose is to remove cyclic four-tuples before applying the rank-two common-fixed-point input.

The audit accepted the mechanism: $V_n$ alone contains cyclic primitive-power contributions too large for the rank-two estimate, while $V_n-S$ leaves a non-diagonal statistic to which the eight-word folded-graph and common-fixed-point machinery applies.

### Finding 3: The Visible Losses Are Now Separated Across the Two Main Theorems

Cycle 5 produced the cross-proof loss map. The main distinctions are:

| Loss source | Location | Role |
|---|---|---|
| $q^{2\kappa}$ | Proposition 3.1 | trace-side Markov interpolation loss |
| $m=\kappa+3+K$ | Theorem 1 smoothing | derivative order for smooth cutoff conversion |
| $\alpha_W \to \alpha_R$ | Weyl inversion | edge loss near $\lambda=1/4$ |
| $q^{4\kappa}$ | Proposition 4.1/4.2 | pre-trace fourth-moment Markov second-derivative loss |
| fiber union | Theorem 2 probability conversion | new local-in-fiber union loss |
| $\Lambda_0^{3/2}$ | Theorem 2 final bound | Sobolev/elliptic local-mass-to-$L^\infty$ conversion |

The closure audit accepted this accounting and validated `M2-proof-ledger`.

### Finding 4: The First M3 Benchmark Supports the Diagonal-Subtraction Heuristic at Toy Level

Cycle 6 implemented a free-group random-permutation model. For each cover degree $n$, the script samples random permutations for free generators, evaluates reduced words, and counts

$$
\#\{x \in \{1,\ldots,n\}: w_1x=\cdots=w_kx=x\}.
$$

The main numerical means were:

| family | n=50 | n=100 | n=200 | n=400 |
|---|---:|---:|---:|---:|
| `cyclic_pair_a_a2` | 0.9555 | 1.0240 | 1.0075 | 1.0175 |
| `cyclic_four` | 0.9555 | 1.0240 | 1.0075 | 1.0175 |
| `cyclic_eight` | 0.9555 | 1.0240 | 1.0075 | 1.0175 |
| `rank_two_pair_a_b` | 0.0195 | 0.0115 | 0.0080 | 0.0040 |
| `independent_four` | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| `independent_eight` | 0.0000 | 0.0000 | 0.0000 | 0.0000 |

The result supports the proof-ledger heuristic: cyclic primitive-power families retain order-one common fixed-point counts, while the rank-two pair $(a,b)$ is much smaller and scales near $1/n$.

### Finding 5: Naive Eight-Word Pointwise Intersections Are Not the Right Next Model

Cycle 6 also produced a useful null result. The rank-two composite families, such as `a,b,ab,aB`, had the same counts as the pair `a,b`, because any point fixed by both `a` and `b` is automatically fixed by those composites. The audit accepted this as a limitation rather than a failure.

The next M3 probe should therefore move closer to folded-graph/common-quotient statistics or polynomial-window diagnostics, instead of adding more words to a pointwise common fixed set.

## Discussion

Cycles 4-6 moved the campaign from proof reconstruction into empirical mechanism testing. The validated proof ledger now covers both main theorems at the local-paper level:

- Theorem 1 is represented by a unified rigidity reconstruction linking Proposition 3.1, smoothing, Chebyshev/grid probability, Weyl law, and rigidity inversion.
- Theorem 2 is represented by a delocalization reconstruction linking the pre-trace formula, $V_n$, $S$, Proposition 4.1/4.2, probability conversion, local mass, and the final $L^\infty$ estimate.

The main remaining proof-theoretic caveat is external: MPvH-style embedding expansion, Nau boundedness, and MP23 rank-two common-fixed-point estimates are treated as imported inputs. This was accepted for `M2-proof-ledger` because that milestone required local proof reconstruction and dependency accounting, not full literature rederivation.

The computational direction is now better defined. M3 should keep the Cycle 6 script as a baseline control suite, but the next substantive observable should encode folded quotient structure rather than only pointwise fixed-set intersections.

## Open Questions

1. Can the Markov interpolation losses $q^{2\kappa}$ and $q^{4\kappa}$ be separated into structural and technical components by a sharper polynomial-method analysis?
2. Can a finite folded-graph/common-quotient statistic reproduce the eight-word mechanism behind Proposition 4.2 more faithfully than naive common fixed-point intersections?
3. Can polynomial-window diagnostics be added to the M3 benchmark suite without requiring a full hyperbolic spectral simulation?
4. Are the imported MPvH, Nau, and MP23 inputs sharp enough for the exponents used in Kim--Tao, or are they only convenient black boxes?
5. Can the final Theorem 2 $\Lambda^{3/2}$ behavior be improved by refining the local-mass-to-$L^\infty$ conversion, beyond the interpolation route already noted by the paper?

## References

No `REFERENCES.md` file was present in the workspace during this reporting pass. The report therefore cites only local sources by path and session ID:

- Local paper files: `2603.01127.pdf`, `2603.01127.txt`.
- Cycle 4 sessions: `9b69e544-cee2-427e-88a7-a2b32be2d4df`, `9a8d5232-7da5-416e-be1a-8515bcece60c`, `dddcaf65-1172-4fa3-a859-9374ae0213b4`.
- Cycle 5 sessions: `0bf32ed4-2866-4671-af3c-2f1b6f30f8ba`, `b5a3c22f-3083-4803-b8c6-1f8e8dee3dc2`, `7dc50143-c79a-4b3c-8371-63f8e61aa904`.
- Cycle 6 sessions: `40632ca0-1b63-4d2b-9bc8-c8baab1f4ae4`, `fe7f867c-00e3-47b8-a4cd-172c205ba885`, `3229364f-0203-4038-8c82-32992a28250f`.

## Appendix: Implementation Details

### Code and Artifact Organization

| Area | Files | Purpose |
|---|---|---|
| Theorem 2 proof ledger | `docs/proof_ledger/delocalization_proof_reconstruction.md`, `eigenfunction_fourth_moment_ledger.md`, `pretrace_diagonal_term.md` | Reconstruct the pre-trace/fourth-moment delocalization proof. |
| Theorem 2 graph | `docs/proof_ledger/theorem2_dependency_graph.dot`, `.png` | Visual dependency map for Theorem 2. |
| M2 closure | `docs/proof_ledger/rigidity_proof_reconstruction.md`, `m2_loss_map.md`, `m2_proof_ledger_closure.md` | Consolidate and close the proof-ledger milestone. |
| M2 closure graph | `docs/proof_ledger/m2_closure_dependency_graph.dot`, `.png` | Visual map from validated slices to broad `M2-proof-ledger`. |
| M3 probe script | `scripts/probe_common_fixed_points.py` | Random-permutation common-fixed-point Monte Carlo CLI. |
| M3 tests | `tests/test_permutation_word_eval.py` | Direct-run tests for word evaluation and reproducibility. |
| M3 data | `data/polynomial_method/common_fixed_point_probe.csv`, `common_fixed_point_summary.csv` | Final raw and summarized datasets. |
| M3 report and figures | `reports/computational_probes/m3_common_fixed_point_probe.md`, `reports/figures/m3_common_fixed_point_scaling.png`, `reports/figures/m3_common_fixed_point_tails.png` | Empirical report and plots. |

### File Counts

| File group | Count or lines |
|---|---:|
| Campaign scripts | 2 |
| Campaign script lines | 342 |
| Campaign test files | 1 |
| Campaign test lines | 57 |
| Cycle 6 final raw CSV rows | 136,000 |
| Cycle 6 word families | 17 |
| Cycle 6 final PNG figures | 2 |
| Cycle 4-5 new proof-ledger PNG figures | 2 |

### Validation Results

Cycle 4 validation:

- `docs/proof_ledger/theorem2_dependency_graph.png` readable, `1459 x 1343`, RGBA.
- `promise_check` passed with warnings only.
- `org_check` passed with warnings only.
- Audit decision: `VALIDATED`, with broad `M2-proof-ledger` reopened and kept active.

Cycle 5 validation:

- `docs/proof_ledger/m2_closure_dependency_graph.png` readable, `2125 x 745`, RGB.
- `promise_check` passed with warnings only, `events: 19`.
- `org_check` passed with warnings only.
- Audit decision: `VALIDATED`, closing broad `M2-proof-ledger` narrowly.

Cycle 6 validation:

- `python3 -m py_compile scripts/probe_common_fixed_points.py tests/test_permutation_word_eval.py`: passed.
- `python3 tests/test_permutation_word_eval.py`: passed.
- Smoke CLI run to `/tmp`: passed.
- Final CSV integrity check: `136000` rows with required columns.
- Final figures readable: both `1280 x 800`, RGBA.
- `promise_check` passed with warnings only, `events: 20`.
- `org_check` passed with warnings only.
- Audit decision: `VALIDATED`, with `M3-computational-probes` kept `in-progress`.

Known validator warnings remain non-blocking:

- Pre-existing noncanonical `docs/paper_map/` ledger artifact path.
- Future milestones `M4`, `M5`, and `M6` have no ledger events yet.
- Old cycle 1-3 report files are orphan artifacts in managed paths.
- Root paper/runtime files are outside the organization allow-set.
- Several requested graph figures are under `docs/`, which `org_check` warns about but auditors accepted because the briefs explicitly requested those paths.

### Session Cross-Reference Map

| Cycle | Researcher role | Worker output | Audit decision |
|---|---|---|---|
| 4 | Directed Theorem 2 pre-trace/fourth-moment reconstruction. | Built Theorem 2 proof ledgers and dependency graph. | Validated slice; fixed premature broad M2 closure. |
| 5 | Directed plan-level M2 consolidation. | Built unified rigidity reconstruction, loss map, closure note, and graph. | Validated broad M2 narrowly. |
| 6 | Directed first M3 random-permutation probe. | Built script, tests, data, figures, and computational report. | Validated first benchmark; kept M3 in progress. |

### Manifest Update

`MANIFEST.md` was replaced with a current snapshot after this reporting pass. It now lists both scripts, the test file, current file counts, cross-references from proof-ledger artifacts into M3, and the milestone state:

- `M1-paper-map`: validated.
- `M2-proof-ledger`: validated narrowly for local proof reconstruction and quantitative dependency/loss accounting.
- `M3-computational-probes`: in-progress, with a validated first benchmark.
- `M4-formal-certification`: pending.
- `M5-extension-candidates`: pending.
- `M6-final-synthesis`: pending.
