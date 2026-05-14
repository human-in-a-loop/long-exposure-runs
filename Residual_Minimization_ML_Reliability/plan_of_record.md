---
created: 2026-05-14T03:08:13Z
run_id: run-2026-05-14T030813Z
agent: researcher
---

# Plan of Record — # Residual Minimization And Scientific ML Reliability

**Created:** 2026-05-14T03:08:13Z
**Run id:** run-2026-05-14T030813Z

## Directive (verbatim)

# Residual Minimization And Scientific ML Reliability

Research problem:

> Residual minimization is not enough: construct explicit scientific machine-learning failures for ODE/PDE learning, and develop verifiable certificates that prevent them.

## Goal

Develop a grounded research package showing when physics-informed neural networks, neural operators, collocation methods, or residual-minimization methods can produce physically wrong solutions despite small training loss, and identify corrected norms, constraints, or certificates that restore reliability.

The target is not a sweeping critique of scientific machine learning. The target is one or more clean, rigorous, limited-scope results that can be stated simply, proved carefully, illustrated with lightweight computations, and connected honestly to current practice.

The research engine should choose its own framing, decomposition, execution structure, search strategy, and intermediate milestones. The sections below are suggestions and constraints of taste, not a mandatory workflow. They are intended to point toward promising territory while leaving room for better formulations, sharper examples, or more natural proof strategies discovered as research develops.

The final output goal is the statement at the end of this prompt: a simple residual objective whose loss vanishes while the learned solution remains wrong, together with an explicit failure mechanism and a minimal certificate or correction that restores convergence.

## Useful Big-Picture Questions

1. Can we construct simple ODE/PDE examples where residual loss tends to zero but the learned or approximating sequence does not converge to the true physical solution?
2. Are the failures caused by weak norms, boundary or initial condition leakage, collocation blind spots, discretization mismatch, non-uniqueness, stiffness, shocks, oscillations, localized defects, or optimization artifacts?
3. Can we separate approximation failure from optimization failure by constructing explicit function sequences with vanishing residual but wrong limits?
4. What minimal additional assumptions restore correctness?
5. Can we formulate checkable certificates using energy estimates, weak formulations, Sobolev norms, conservation laws, entropy conditions, Lyapunov functions, maximum principles, or sum-of-squares methods?
6. Which examples are simple enough to explain visually but rigorous enough for a scientific journal or serious preprint?

## Suggested Scope

The following scope is recommended, but not exhaustive. Prioritize applied mathematics, numerical analysis, PDE theory, scientific machine learning, formal verification, and computational physics. Prefer pen-and-paper reasoning, symbolic calculations, and lightweight numerical demonstrations. Avoid depending on large neural-network training runs except as optional illustrations, unless a compelling reason emerges.

Wolfram Language and Wolfram bridge tools are available for symbolic mathematics, exact calculations, algebraic manipulation, differential equations, visualization, and other math-intensive subproblems. Use them when they materially improve rigor, speed, or clarity.

Use `<run-workspace>` as the working directory. A lightweight
scientific Python environment is available at
`<run-workspace>/.sciml-venv` with NumPy, SciPy, SymPy,
Matplotlib, and Pytest for small numerical experiments, symbolic sanity
checks, figures, and reproducibility tests. Wolfram Language is available
through `wolfram-batch -script <file.wls>`, and the local
`<run-workspace>/wolfram-bridge` skill/tool is available for
Wolfram-assisted mathematical work when it adds value.

It may be useful to focus first on problems where:

- the exact solution is known,
- the residual operator is simple,
- the loss functional can be written explicitly,
- bad approximating sequences can be constructed by hand,
- convergence or non-convergence can be proved in standard norms,
- and the corrected certificate has a classical mathematical interpretation.

Possible initial candidates:

- 1D linear advection or transport,
- Poisson equation on an interval,
- heat equation with simple boundary and initial data,
- inviscid Burgers' equation before and after shock formation,
- scalar conservation laws with entropy conditions,
- stiff scalar or two-dimensional ODEs,
- Hamiltonian or dissipative ODEs,
- boundary-layer problems,
- simple eigenvalue problems with spurious modes.

## Definitions Worth Making Explicit

Define the relevant objects before making broad claims. Useful definitions may include:

- residual loss,
- collocation loss,
- continuous loss,
- boundary and initial condition penalty,
- physical correctness,
- convergence norm,
- weak solution,
- entropy solution where relevant,
- certificate,
- and the distinction between optimization failure and objective-function failure.

When relevant, track whether a result applies to PINNs specifically, neural operators, collocation methods, Galerkin-style methods, or residual-based learning more generally.

## Possible Research Pattern

A useful pattern may be to search for explicit sequences \(u_n\) such that:

- residual loss \(R(u_n) \to 0\),
- boundary or initial penalties also vanish when included,
- but \(u_n\) does not converge to the intended solution in the relevant norm, observable, or solution concept.

For each candidate, consider whether the following steps help:

1. State the ODE/PDE and domain.
2. State the true solution and assumptions.
3. Define the residual objective exactly.
4. Construct a candidate bad sequence.
5. Prove the residual objective vanishes.
6. Prove the solution error does not vanish, or that the limit is physically wrong.
7. Identify the failure mechanism.
8. Propose the smallest plausible correction.
9. Prove whether the correction restores convergence.
10. Decide whether the example is mathematically new, communicable, and publishable.

## High-Value Result Types

At least one strong result in one of these forms would be valuable. These are examples, not requirements:

### A. Continuous Residual Counterexample

An ODE or PDE where the residual goes to zero in the training norm while the solution error remains bounded away from zero.

### B. Collocation Blind-Spot Counterexample

A collocation objective that is exactly or nearly zero at all sampled points while the global solution is wrong.

### C. Weak-Norm Failure

A sequence where residual convergence in a weak norm misses high-frequency oscillations, boundary layers, or localized defects.

### D. Conservation-Law Failure

A scalar conservation-law example where residual minimization admits a weak but non-entropy solution, or otherwise fails to select the physically relevant solution.

### E. Certificate Theorem

A positive theorem showing that adding an energy estimate, entropy inequality, boundary trace condition, Sobolev control, maximum principle, or Lyapunov certificate restores convergence.

### F. Verification Framework

A limited framework for verifying learned ODE/PDE surrogates using Lyapunov, conservation-law, or sum-of-squares certificates.

## Grounding Principles

Keep the project grounded:

- Do not claim that all PINNs fail.
- Do not claim practical failure from a purely artificial example unless the connection is justified.
- Do not conflate continuous residual minimization with finite collocation training.
- Do not conflate failure of the objective with optimizer failure.
- Do not assume neural networks are essential; first prove the phenomenon for explicit approximating functions.
- Do not pursue examples requiring deep unresolved PDE theory.
- Prefer one-dimensional or low-dimensional examples until a complete proof exists.
- Prefer classical estimates over exotic machinery.
- Make every norm, topology, and boundary condition explicit.

## Literature Anchors To Consider

Search for related results in areas such as:

- least-squares finite element methods,
- residual minimization,
- Galerkin and Petrov-Galerkin methods,
- spectral collocation,
- compactness and weak convergence,
- Sobolev trace theory,
- conservation laws and entropy solutions,
- PINN failure analyses,
- neural operator approximation theory,
- posteriori error estimation,
- and formal verification of dynamical systems.

For promising theorems, ask whether the result is already known in numerical analysis under another name. If so, clarify what is new: the scientific-ML framing, a simpler counterexample, a sharper certificate, or a connection to modern training objectives.

## Optional Operating Procedure

The research engine may use, adapt, or ignore this procedure:

1. Review the current candidate examples.
2. Try to prove or disprove the strongest current theorem statement.
3. If blocked, simplify the equation, norm, boundary condition, or domain.
4. Search for analogous classical results.
5. Record useful lemmas and failed attempts.
6. Update the ranking of candidate results.
7. Write the cleanest theorem statement available.
8. Identify the next symbolic computation or numerical sanity check.
9. Keep a short "publishability note" for each result.

## Parallel Exploration

The run may explore multiple independent paths simultaneously when doing so is
actually useful. Use parallel branches for tasks with cleanly separable
assumptions, candidate equations, proof strategies, literature checks,
symbolic computations, or numerical demonstrations. Do not parallelize tightly
coupled work that depends on a shared proof state; in those cases, keep the
reasoning sequential and use parallelism only for independent verification or
side calculations.

## Suggested Supporting Artifacts

The following artifacts would be useful if they support the final output goal:

- definitions,
- candidate examples,
- failed attempts,
- theorem statements,
- proof sketches,
- complete proofs where available,
- minimal computational demonstrations,
- figures or figure concepts,
- related-work notes,
- novelty assessment,
- a ranked list of the most promising results,
- a journal-style abstract,
- a paper outline,
- and a short public-facing explanation of the cleanest example.

## Suggested Evaluation Criteria

Prefer results that are:

- mathematically rigorous,
- simple to state,
- surprising but not overclaimed,
- connected to current scientific ML practice,
- visualizable in one figure,
- tractable with symbolic reasoning and small computations,
- and strong enough to support a serious preprint.

## Required Final Output Goal

The final output should, if at all possible, have the form:

> Here is a simple residual objective for a scientific ML problem. The residual tends to zero while the learned solution remains wrong. The failure mechanism is explicit. Adding this minimal certificate restores convergence.

## Goals

| Goal ID | Goal | Owner |
|---------|------|-------|
| G1      | Identify explicit residual-minimization objectives whose loss can vanish while physical error does not vanish. | researcher |
| G2      | Prove at least one minimal corrective certificate/norm/constraint that restores convergence for a clean counterexample. | researcher |
| G3      | Package the strongest result with reproducible lightweight computations, figures, and related-work positioning. | researcher |
| G4      | Build a broad catalogue of at least twenty attempted residual-minimization failure mechanisms, separating distinct mathematical mechanisms from variants. | researcher |
| G5      | Map representative mechanisms to realistic scientific-ML application motifs without overclaiming production failures. | researcher |
| G6      | Produce at least five lightweight toy simulations, each with data, figure where useful, and a certificate/correction check. | researcher |

## Milestones

| Milestone ID | Goal | Description | Success criteria (falsifiable) | Dependencies |
|--------------|------|-------------|--------------------------------|--------------|
| M-1          | G1   | Candidate triage and definitions | A ranked table of at least four candidate mechanisms exists, with explicit PDE/ODE, residual objective, bad sequence template, target error norm, and likely certificate. | — |
| M-2          | G1/G2 | Continuous norm-mismatch counterexample | A complete theorem states an explicit continuous residual objective with residual loss tending to zero and solution error bounded below, including a proof and a minimal correction/certificate. | M-1 |
| M-3          | G1/G2 | Collocation blind-spot counterexample | A complete theorem or proposition gives an explicit collocation grid/objective with zero or vanishing sampled residual while global error remains large, plus a certificate such as fill distance, quadrature norm, or derivative/variation control. | M-1 |
| M-4          | G1/G2 | Conservation-law or weak-solution selection failure | A scalar conservation-law example is either validated with an entropy-certificate theorem or rejected with a documented reason. | M-1 |
| M-5          | G3   | Reproducible demonstrations | Scripts generate all committed data files and plots, and tests verify asymptotic scaling/negative controls for the selected examples. | M-2 or M-3 |
| M-6          | G3   | Research synthesis | A concise report contains definitions, theorem statements, proofs, figures, related-work notes, limitations, and the final "residual vanishes but solution wrong; certificate restores convergence" statement. | M-3, M-5 |
| M-7          | G4/G5 | Broad catalogue and application map bootstrap | `residual-certificates/residual_case_catalogue.md` contains at least twenty attempted mechanisms and at least ten explicit candidate families/objective settings; `residual-certificates/application_risk_map.md` links each mechanism to application motifs and states the strength of evidence. | M-1, M-3 |
| M-8          | G4/G2 | Weak-norm and topology-mismatch branch | At least three weak-norm or topology-mismatch candidates are analyzed with explicit scaling laws; each is classified as theorem-quality, stability baseline, or obstruction, with a proposed certificate/norm correction. | M-7 |
| M-9          | G4/G2/G5 | Conservation/admissibility branch | At least three conservation-law, entropy, positivity, maximum-principle, or invariant-constraint candidates are analyzed; at least one receives a toy simulation or a rigorous obstruction note. | M-7 |
| M-10         | G4/G2/G5 | ODE reliability branch | Stiffness, observability, Lyapunov, mass/positivity, and inverse-parameter non-identifiability examples are triaged; at least two candidate objectives receive explicit bad families or rigorous disproofs. | M-7 |
| M-11         | G6   | Five-toy-simulation suite | At least five toy simulations tied to application motifs produce small CSVs, figures where the shape matters, and tests or reproducibility scripts checking both low residual and physical/certificate behavior. | M-7, plus any of M-8/M-9/M-10 |
| M-12         | G3/G4/G5/G6 | Broad synthesis package | Final catalogue contains ranked mechanisms, proof/obstruction notes, application relevance, toy-simulation status, certificate/correction for each top candidate, and a clear closure argument against the directive's breadth criteria. | M-7, M-11 |

## Out of scope (explicit)

- Claims that residual minimization or PINNs fail in general.
- Large neural-network training studies unless used only as optional illustration after an explicit function-sequence result is proved.
- Examples depending on unresolved PDE regularity or high-dimensional numerics.

## Pointer to ledger

Every milestone status, history, and judgment lives in `promise_ledger.jsonl`,
filtered by `milestone_id`. Run `promise_check` to materialize the current
state for the human; agents call it via Bash:

    python3 -m long_exposure.tools.promise_check .

The directive section above is **immutable** after creation. Goals and
milestones tables are mutable, but every edit must emit a ledger event with
`milestone_id: "_plan/<descriptive-change-name>"` so the audit trail is
complete.
