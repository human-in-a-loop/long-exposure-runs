---
title: "Random Hyperbolic Surface Spectral Rigidity — cycles 1-3"
date: "2026-05-15"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# Random Hyperbolic Surface Spectral Rigidity — cycles 1-3

## Introduction

Cycles 1-3 began the long-horizon research campaign on Elena Kim and Zhongkai Tao's paper, *Eigenvalue rigidity of hyperbolic surfaces in the random cover model*, using the local files `2603.01127.pdf` and `2603.01127.txt`. The goal for these first cycles was not to extend the paper yet. It was to make the paper's proof architecture inspectable: define the model and notation, locate the main theorem-level dependencies, reconstruct the first quantitative proof chain, and identify where the dominant losses enter.

The work proceeded in three stages:

- Cycle 1 established the foundational map of the paper and validated milestone `M1-paper-map`.
- Cycle 2 reconstructed the theorem-level reduction from Proposition 3.1 to Theorem 1, including the high-probability Weyl law and eigenvalue-location inversion.
- Cycle 3 reconstructed the internal proof mechanism of Proposition 3.1, including the two-trace expansion, polynomialization in `1/n`, and the Markov brothers derivative-control step.

The Cycle 3 audit validated the mathematical reconstruction completed so far and corrected a bookkeeping issue: workers had marked broad milestone `M2-proof-ledger` as validated, but only slices of that milestone are complete. The current ledger state is that `M2-proof-ledger` remains active, with the Theorem 2 pre-trace/fourth-moment reconstruction still pending. Source sessions: Cycle 1 researcher `f25feffa-92d5-4c84-8de0-30919b1b7b35`, worker `4c2dd885-8bb7-4410-b522-5996f1a60220`, auditor `b66fbf4b-9931-4dbc-8158-35f1cd1105a3`; Cycle 2 researcher `b9cb131c-85c5-40b1-b1c5-83c2272eaa6d`, worker `590777b8-647a-4313-a13e-03022a34549b`, auditor `9a341547-56b9-4763-a609-946173aa778c`; Cycle 3 researcher `c35ab776-8779-466c-8bbf-52c7baf91305`, worker `22f10712-a68a-4240-8aec-ec70338e35b0`, auditor `0ab24e92-33d4-4e37-986a-306ee1e9ae47`.

## Definitions and Notation

The base object is a compact connected orientable hyperbolic surface

$$X = \Gamma \backslash \mathbb{H}$$

of genus $g \ge 2$. A random degree-$n$ cover $X_n$ is encoded by a uniformly sampled homomorphism

$$\phi_n : \Gamma \to S_n,$$

where $S_n$ is the symmetric group. The associated permutation representation is denoted by $\rho = \rho_{\phi_n}$. The eigenvalues of the Laplacian on $X_n$ are written $\lambda_j(X_n)$, and the spectral parameter is

$$\lambda = \frac14 + r^2.$$

The eigenvalue counting function is

$$N_{X_n}(\Lambda) = \#\{j : \lambda_j(X_n) \le \Lambda\}.$$

The paper's Theorem 1 is an eigenvalue rigidity and Weyl-law result for eigenvalues in $[1/4,\Lambda]$. Theorem 2 is an eigenfunction delocalization result. Cycle 1 recorded both theorem statements in run notation and separated the two proof routes: Theorem 1 uses the twisted Selberg trace formula, while Theorem 2 uses the twisted pre-trace formula.

## Source Inventory and Timeline

### Cycle 1: Foundational Paper Map

The Cycle 1 research brief (`f25feffa-92d5-4c84-8de0-30919b1b7b35`) directed the worker to stay inside the local paper and produce a notation table, theorem map, dependency graph, and open-question ledger. The worker produced:

- `docs/paper_map/cycle1_foundational_map.md`
- `docs/paper_map/cycle1_dependency_graph.dot`
- `docs/paper_map/cycle1_dependency_graph.png`
- `docs/paper_map/cycle1_open_questions.md`

The map identified the major theorem and proposition dependencies: Lemmas 2.1-2.4, Proposition 3.1, Lemma 3.3, Corollary 3.4, Lemma 3.5, Propositions 4.1 and 4.2, and the downstream Chebyshev, grid, Weyl inversion, Sobolev, and elliptic steps.

![Dependency graph for the Cycle 1 paper map.](docs/paper_map/cycle1_dependency_graph.png)

The Cycle 1 audit (`b66fbf4b-9931-4dbc-8158-35f1cd1105a3`) validated `M1-paper-map`. It confirmed that the theorem statements preserved the probability level `1 - n^{-1/10}` and the roles of `alpha`, `C`, `Lambda`, and `epsilon`. It also confirmed that the trace/pre-trace distinction was correctly recorded.

### Cycle 2: Theorem 1 Exponent Flow

The Cycle 2 research brief (`b9cb131c-85c5-40b1-b1c5-83c2272eaa6d`) moved to `M2-proof-ledger`, focused only on the reduction from Proposition 3.1 to Theorem 1. The worker produced:

- `docs/proof_ledger/theorem1_exponent_flow.md`
- `docs/proof_ledger/weyl_inversion_detail.md`
- `docs/proof_ledger/theorem1_exponent_flow.dot`
- `docs/proof_ledger/theorem1_exponent_flow.png`

The main output was a quantitative ledger for equations (3.3)-(3.12) of the paper. It showed how the smooth cutoff passage, derivative norms, the choice of $K$, the choice of $\alpha_0$, Chebyshev's inequality, and the spectral grid combine to produce the high-probability Weyl law.

![Quantitative loss flow from Proposition 3.1 to Theorem 1.](docs/proof_ledger/theorem1_exponent_flow.png)

The Cycle 2 audit (`9a341547-56b9-4763-a609-946173aa778c`) validated the Theorem 1 slice. It also corrected the milestone state: the broad `M2-proof-ledger` milestone was reopened and set to in-progress because Theorem 2 and Proposition 3.1 internals were still pending.

### Cycle 3: Proposition 3.1 Internal Reconstruction

The Cycle 3 research brief (`c35ab776-8779-466c-8bbf-52c7baf91305`) directed work upstream into Proposition 3.1 itself. The worker produced:

- `docs/proof_ledger/proposition31_internal_reconstruction.md`
- `docs/proof_ledger/two_trace_expansion_ledger.md`
- `docs/proof_ledger/markov_loss_reconstruction.md`
- `docs/proof_ledger/proposition31_dependency_graph.dot`
- `docs/proof_ledger/proposition31_dependency_graph.png`
- `scripts/check_markov_scaling.py`
- `data/polynomial_method/markov_scaling_sanity.csv`
- `docs/proof_ledger/markov_scaling_sanity.png`

The Proposition 3.1 reconstruction followed the proof from the trace variance to a two-trace random permutation statistic, then to a polynomial expression in $1/n$, then through Markov brothers' inequality.

![Dependency graph for Proposition 3.1 internals.](docs/proof_ledger/proposition31_dependency_graph.png)

The Cycle 3 audit (`0ab24e92-33d4-4e37-986a-306ee1e9ae47`) validated this reconstruction. It again corrected the milestone state, leaving `M2-proof-ledger` active for the still-pending Theorem 2 delocalization proof.

## Results

### Result 1: The Paper Architecture Is Now Mapped

Cycle 1 established the paper-level proof architecture. Theorem 1 is routed through the twisted Selberg trace formula and Proposition 3.1. Theorem 2 is routed through the twisted pre-trace formula and Propositions 4.1 and 4.2. This separation matters because Theorem 1 is a global trace/counting statement, while Theorem 2 is a local pointwise mass statement.

The Cycle 1 map also separated three categories of inputs:

- Standard background: random covers via `Hom(Gamma,S_n)`, Selberg trace and pre-trace formulas, hyperbolic kernel estimates, Chebyshev's inequality, monotonicity, Sobolev embedding, and elliptic regularity.
- Imported prior work: test functions from prior HMT work, polynomial-method expansion technology from MPvH, Witten zeta and homomorphism-count asymptotics, Chebyshev coefficient control, smooth cutoff construction, common fixed-point estimates, and Markov brothers' inequality.
- Paper-specific adaptations: the two-trace graph `C_{gamma_1,gamma_2}`, the full geodesic second-moment polynomialization in Corollary 3.4, and the fourth-order pre-trace statistic with diagonal subtraction in the eigenfunction proof.

### Result 2: Theorem 1 Losses After Proposition 3.1 Are Explicit

Cycle 2 treated Proposition 3.1 as a black box and reconstructed how it implies the high-probability Weyl law. The key variance bound after the smooth cutoff passage is of the form

$$
\operatorname{Var} \le C n^{-1}\Lambda_0^{-K}
\Lambda^{2m(1/2-\epsilon)} n^{2m\alpha_0},
$$

where

$$
m = \kappa + 3 + K,
\qquad
\alpha_0 = \frac{1}{3m}.
$$

With this choice,

$$
-1 + 2m\alpha_0 = -\frac13.
$$

The choice

$$
K = \left\lfloor\frac{\kappa+5}{2\epsilon}\right\rfloor + 1
$$

forces the remaining large-$\Lambda$ power to be at most $\Lambda^{-2}$. Chebyshev's inequality with threshold $n^{-1/9}$ then gives a failure probability of order $\Lambda^{-2}n^{-1/9}$. The grid union bound uses the inequality

$$
0.01 - \frac19 = -\frac{91}{900} < -\frac{1}{10},
$$

which yields the stated simultaneous probability $1-n^{-1/10}$.

The Weyl inversion note made explicit an exponent degradation near the spectral edge $\lambda=1/4$. If

$$
F(\Lambda)=\int_0^{\sqrt{\Lambda-1/4}} r\tanh(\pi r)\,dr,
$$

then near the edge

$$
F(1/4+t) \sim \frac{\pi}{3}t^{3/2}.
$$

Thus the inverse map is Hölder rather than Lipschitz at the edge, and the rigidity exponent may shrink from a Weyl-law exponent $\alpha_W$ to a location exponent $\alpha_R \le 2\alpha_W/3$. The audit accepted this as compatible with the paper's existential statement of a positive exponent.

### Result 3: Proposition 3.1 Reduces Randomness to Two-Trace Fixed-Point Statistics

Cycle 3 reconstructed the internal mechanism of Proposition 3.1. The centered spectral statistic is converted by the Selberg trace formula into a geodesic-side random sum $S_n$. The variance target is

$$
n^{-2}\mathbb{E}S_n^2.
$$

Expanding the square produces a double sum over primitive geodesics and powers. The random part is

$$
\mathbb{E}\left[\operatorname{tr}\rho(\gamma_1^{k_1})
\operatorname{tr}\rho(\gamma_2^{k_2})\right].
$$

Lemma 3.3 represents this product of traces as a common fixed-point statistic. The relevant graph is a disjoint union of two labeled cycles, denoted in the artifacts as `C_{gamma_1,gamma_2}`. Folded quotient graphs encode the possible overlap patterns, and the imported polynomial-method machinery turns the expectation into a rational-polynomial expression in $1/n$ with controlled error.

Corollary 3.4 then packages the full second moment into

$$
\mathbb{E}S_n^2 = \frac{p(1/n)}{Q_{\mathrm{id}}(1/n)} + \text{error}.
$$

The degree of $p$ is controlled by Fourier support and word-length comparison. This is where the geometric support of the Selberg transform enters the polynomial method.

### Result 4: The Visible `q^{2\kappa}` Loss Enters at Markov Brothers' Inequality

The Cycle 3 artifacts identify the Markov step as the visible source of the proposition-level $q^{2\kappa}$ loss. The polynomial used in that step is

$$
P(x)=x^2p(x).
$$

Before Markov is applied, the proof has control of $P(1/n)$ at reciprocal integer points. Markov brothers' inequality converts that discrete control into derivative control on an interval near zero:

$$
\left\|P'\right\| \le Cq^{2\kappa}\sup_{n \ge Cq^\kappa}|P(1/n)|.
$$

Taylor expansion from $0$ to $1/n$, using $P(0)=0$, gives the desired $n^{-1}$ gain:

$$
|P(1/n)| \le \frac{1}{n}\|P'\|.
$$

The audit accepted the diagnosis that the two-trace expansion is structural, while the final $q^{2\kappa}$ derivative amplification is plausibly technical or non-optimized, conditional on whether the imported Markov/interpolation machinery can be sharpened.

The Markov sanity script illustrates the classical endpoint derivative scale for Chebyshev polynomials, where $T_D'(1)=D^2$.

![Degree versus derivative-amplification scale illustrating the Markov brothers loss mechanism.](docs/proof_ledger/markov_scaling_sanity.png)

## Discussion

The campaign has moved from orientation to proof reconstruction, but it has not yet reached new extension work. That is deliberate. The first three cycles establish enough structure to make later extension attempts traceable to specific parts of the proof.

The main validated conclusion is that the Theorem 1 route has two layers of loss:

1. The theorem-level layer after Proposition 3.1: smooth cutoff derivatives, Chebyshev coefficient conversion, the choice of $K$, probability conversion, grid union bounds, and Weyl inversion near $1/4$.
2. The proposition-level layer inside Proposition 3.1: two-trace polynomialization followed by Markov derivative amplification of $P(x)=x^2p(x)$.

The most concrete technical bottleneck identified so far is the Markov brothers step. The artifacts do not claim that the $q^{2\kappa}$ power is sharp. They state the more conservative result: in the local paper proof, this is the step where the visible power enters. Any later attempt to improve the rigidity exponent should either sharpen this interpolation step or exploit additional structure in the polynomial $p$ and its degree/support constraints.

The second important point is that Theorem 2 should not be treated as a trivial parallel copy of Theorem 1. Cycle 1 identified a parallel macro-structure, but Theorem 2 uses the pre-trace formula, a fourth-moment statistic, and a diagonal/local term $S$. The Cycle 3 audit explicitly named Proposition 4.1, the pre-trace fourth-moment expansion, and the diagonal term $S$ as the next proof-ledger target.

## Open Questions

The following questions remain open after cycles 1-3:

1. Theorem 2 reconstruction: Proposition 4.1, Proposition 4.2, the fourth-moment expansion, and the diagonal term $S$ have been mapped but not reconstructed in proof-ledger detail.

2. Imported polynomial-method machinery: Lemma 3.3 and the Markov brothers lemma were reported as imported inputs where appropriate. The campaign has not yet audited MPvH, Nau, or related external machinery.

3. Sharpness of the $q^{2\kappa}$ loss: the current evidence localizes the loss to Markov derivative amplification but does not establish whether the loss is necessary.

4. Computational probes: apart from the Markov scaling sanity check, no finite random-cover, permutation, Schreier graph, or random regular graph toy model has been built yet.

5. Formal certification: no Lean, GAP, or Wolfram formal artifact has been created in cycles 1-3.

6. Extension search: no new conjecture or extension has been advanced yet. The validated preparation points toward possible later work on sharper interpolation, finer spectral windows, or the Theorem 2 fourth-moment structure.

## References

No `REFERENCES.md` file was found in the workspace during report gathering, so there was no accumulated global bibliography numbering to continue. This report cites only the local paper file `2603.01127.txt` by section/equation as recorded in the internal artifacts and the session IDs listed in the appendix.

## Appendix: Implementation Details

### Code Organization

Campaign-authored artifacts are organized as follows:

| Path | Role |
|---|---|
| `docs/paper_map/cycle1_foundational_map.md` | Cycle 1 theorem, notation, section, dependency, and loss map |
| `docs/paper_map/cycle1_open_questions.md` | Cycle 1 bottleneck ledger for later milestones |
| `docs/paper_map/cycle1_dependency_graph.dot` | Cycle 1 dependency graph source |
| `docs/paper_map/cycle1_dependency_graph.png` | Cycle 1 rendered dependency graph, 2245 x 1032 |
| `docs/proof_ledger/theorem1_exponent_flow.md` | Cycle 2 Proposition 3.1-to-Theorem 1 exponent ledger |
| `docs/proof_ledger/weyl_inversion_detail.md` | Cycle 2 Weyl-law-to-eigenvalue-rigidity inversion note |
| `docs/proof_ledger/theorem1_exponent_flow.dot` | Cycle 2 loss-flow graph source |
| `docs/proof_ledger/theorem1_exponent_flow.png` | Cycle 2 rendered loss-flow graph, 804 x 1423 |
| `docs/proof_ledger/proposition31_internal_reconstruction.md` | Cycle 3 reconstruction of Proposition 3.1 internals |
| `docs/proof_ledger/two_trace_expansion_ledger.md` | Cycle 3 two-trace fixed-point expansion ledger |
| `docs/proof_ledger/markov_loss_reconstruction.md` | Cycle 3 Markov brothers loss note |
| `docs/proof_ledger/proposition31_dependency_graph.dot` | Cycle 3 Proposition 3.1 graph source |
| `docs/proof_ledger/proposition31_dependency_graph.png` | Cycle 3 Proposition 3.1 rendered graph, 1242 x 1143 |
| `scripts/check_markov_scaling.py` | Cycle 3 Markov scaling sanity script |
| `data/polynomial_method/markov_scaling_sanity.csv` | Canonical Markov scaling CSV |
| `docs/proof_ledger/markov_scaling_sanity.png` | Markov scaling figure, 1170 x 756 |
| `scripts/data/polynomial_method/stale/markov_scaling_sanity.csv` | Archived duplicate CSV from an early figure-harness run |

### File Counts

The current campaign line-count snapshot is:

| Artifact group | Count / lines |
|---|---:|
| Paper-map markdown files | 2 files, 240 lines |
| Proof-ledger markdown files | 5 files, 750 lines |
| Campaign Python scripts | 1 file, 60 lines |
| Canonical CSV rows | 65 lines including header |
| Ledger events | 14 events |
| Total counted campaign text/code/data lines | 1,319 |

### Test and Validation Results

Cycle 1 validation:

- `promise_check` passed with warnings only.
- Required paper-map artifacts existed.
- The dependency graph PNG was valid at 2245 x 1032.
- The audit validated `M1-paper-map`.

Cycle 2 validation:

- The exponent-flow chain was checked against local §3.1.
- The inequality forcing $\Lambda^{-2}$ decay was accepted.
- The Chebyshev and grid probability arithmetic was accepted.
- `theorem1_exponent_flow.png` was valid at 804 x 1423.
- The audit validated the Theorem 1 slice and reopened broad `M2-proof-ledger`.

Cycle 3 validation:

- `python3 -m long_exposure.tools.promise_check .`: passed with warnings only.
- `python3 -m long_exposure.tools.org_check .`: passed with warnings only.
- `python3 scripts/check_markov_scaling.py`: wrote the canonical CSV and reported degree 8 derivative 64 with ratio 1.0.
- `python3 -m py_compile scripts/check_markov_scaling.py`: passed.
- `proposition31_dependency_graph.png`: valid PNG, 1242 x 1143.
- `markov_scaling_sanity.png`: valid PNG, 1170 x 756.
- The audit validated the Proposition 3.1 internal reconstruction and kept broad `M2-proof-ledger` active.

Warnings that remain are non-blocking and already recorded by auditors: pre-existing `docs/paper_map/` canonicalization, future milestones `M3`-`M6` without events, root paper/runtime files outside the standard organization allow-set, and requested figures under `docs/`.

### Session References

| Cycle | Role | Session ID | Contribution |
|---|---|---|---|
| 1 | Researcher | `f25feffa-92d5-4c84-8de0-30919b1b7b35` | Set the foundational paper-map brief |
| 1 | Worker | `4c2dd885-8bb7-4410-b522-5996f1a60220` | Built Cycle 1 map, dependency graph, and open questions |
| 1 | Auditor | `b66fbf4b-9931-4dbc-8158-35f1cd1105a3` | Validated `M1-paper-map` |
| 2 | Researcher | `b9cb131c-85c5-40b1-b1c5-83c2272eaa6d` | Set the Theorem 1 exponent-flow brief |
| 2 | Worker | `590777b8-647a-4313-a13e-03022a34549b` | Built exponent-flow and Weyl inversion artifacts |
| 2 | Auditor | `9a341547-56b9-4763-a609-946173aa778c` | Validated the Theorem 1 slice and reopened broad `M2` |
| 3 | Researcher | `c35ab776-8779-466c-8bbf-52c7baf91305` | Set the Proposition 3.1 internal reconstruction brief |
| 3 | Worker | `22f10712-a68a-4240-8aec-ec70338e35b0` | Built Proposition 3.1, two-trace, Markov, script, data, and figure artifacts |
| 3 | Auditor | `0ab24e92-33d4-4e37-986a-306ee1e9ae47` | Validated Proposition 3.1 internals and kept broad `M2` active |

### Cross-Reference Map

| Source | Feeds Into | Purpose |
|---|---|---|
| Cycle 1 map | Cycle 2 theorem-level proof ledger | Defines notation and identifies Proposition 3.1 as Theorem 1 bottleneck |
| Cycle 1 open questions | Cycle 2 and Cycle 3 briefs | Promotes exponent flow, Weyl inversion, two-trace expansion, and Markov loss |
| Cycle 2 exponent flow | Cycle 3 Proposition 3.1 reconstruction | Separates downstream theorem-level losses from upstream proposition-level losses |
| Cycle 2 Weyl inversion note | Theorem 1 interpretation | Distinguishes Weyl exponent `alpha_W` from rigidity exponent `alpha_R` |
| Cycle 3 Proposition 3.1 reconstruction | Future extension search | Localizes the visible $q^{2\kappa}$ loss to Markov derivative amplification |
| Cycle 3 Markov sanity script | Computational-probe milestone seed | Provides the first small reproducible polynomial-method diagnostic |
