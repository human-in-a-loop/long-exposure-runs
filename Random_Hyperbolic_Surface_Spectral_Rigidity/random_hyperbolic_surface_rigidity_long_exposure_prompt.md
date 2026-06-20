# Long-Exposure Research Prompt: Random Hyperbolic Surface Spectral Rigidity

## Core Directive

Run a long-horizon autonomous research program centered on the paper:

- `2603.01127.pdf`
- `2603.01127.txt`

The paper is "Eigenvalue rigidity of hyperbolic surfaces in the random cover model" by Elena Kim and Zhongkai Tao. The first objective is to understand and rederive the paper's key results from first principles, with enough detail that the proof architecture, dependencies, and technical bottlenecks are explicit and inspectable. The second objective is to build from that understanding toward genuinely new research directions in random hyperbolic surfaces, spectral rigidity, eigenfunction delocalization, random covers, trace/pre-trace formula methods, and polynomial-method analogies with random regular graphs.

The intended outcome is not a summary. The intended outcome is a serious research campaign that may take weeks, producing derivations, validation artifacts, computational experiments, proof sketches, counterexample searches, and eventually one or more novel findings or conjectural pathways that could add real value to active research in this domain.

## Autonomy

Long-exposure decides what to do. No user ratification or guidance will be provided to unblock choices during the live run. When there are multiple plausible paths, choose the path with the best balance of mathematical significance, tractability, and evidence production. Use parallel branches for genuinely independent workstreams, such as analytic rederivation, computational experiments, formalized sublemmas, and literature-context mapping.

Milestones and deliverables below are initial scaffolding only. Revise them as the run learns more.

## Initial Research Ladder

1. Establish a precise map of the paper.
   - State the main theorems in the run's own notation.
   - Identify all critical inputs: Selberg trace formula, pre-trace formula, random cover model, permutation representation trace statistics, polynomial approximation, Markov brothers' inequality, Weyl law conversion, and eigenfunction estimates.
   - Separate standard background from paper-specific innovations.

2. Reconstruct the proof.
   - Rebuild the main eigenvalue rigidity argument step by step.
   - Rebuild the eigenfunction delocalization argument and show where it diverges from the eigenvalue proof.
   - Track every nontrivial dependency in a proof ledger.
   - Make explicit which estimates are quantitative, which constants/exponents are non-optimized, and where losses enter.

3. Build computational probes.
   - Implement finite and toy models that mimic random cover behavior through permutation representations and Schreier-style constructions.
   - Test trace-statistic concentration and polynomial-window approximations in simplified settings.
   - Compare toy random-cover behavior with random regular graph analogies where appropriate.
   - Produce reproducible scripts, datasets, and figures.

4. Formalize or certify isolated pieces where useful.
   - Use Lean for small self-contained lemmas: polynomial inequalities, finite combinatorial identities, elementary expectation manipulations, or proof-skeleton checks.
   - Do not attempt to formalize the full Selberg trace formula unless a focused subproblem makes that worthwhile.

5. Search for real extensions.
   - Identify which assumptions are structural and which may be relaxable.
   - Explore whether sharper exponents, improved eigenfunction norms, finer window statistics, multiplicity bounds, or transfer to related random surface models are plausible.
   - Look for a tractable new proposition, conjecture-with-evidence, or technical lemma that meaningfully extends the paper.
   - Prefer one solid new contribution with evidence over many shallow speculations.

6. Produce research-grade artifacts.
   - Maintain `plan_of_record.md`, `promise_ledger.jsonl`, and structured notes.
   - Produce periodic reports that distinguish proven facts, numerically supported hypotheses, failed routes, and open gaps.
   - Keep code and generated data reproducible.
   - End-state outputs should include a final report, audit, curated file map, and a ranked list of credible follow-up research problems.

## Available Workspace Tools

The run is launched from `<workspace>`, which contains the paper and tool support.

Use these tools when they add value:

- Wolfram Language through `wolfram-batch`; use this for symbolic algebra, asymptotics, special-function manipulations, exact checks, and heavier analytic experiments.
- `workspace/wolfram-bridge` is available as a local skill/tool reference for Wolfram-backed workflows. It is not a replacement for direct Wolfram smoke tests.
- Lean 4 and Lake are available; use them selectively for small formal checks.
- GAP is installed minimally with FGA and IO; use it for free groups, finitely presented groups, permutation groups, and group-action toy models.
- Python scientific stack is available: NumPy, SciPy, SymPy, Matplotlib, Pandas, and NetworkX.
- LaTeX/Pandoc/Tectonic are available for report rendering and formula-heavy artifacts.
- Web access is available, but do not use web search as a shortcut for understanding the paper. Use external sources to contextualize, verify, and extend after reconstructing the core argument from the local paper.

## Working Standards

- Be mathematically conservative: label claims as theorem, lemma, heuristic, numerical evidence, conjecture, or failed route.
- Reproduce before extending. Any proposed extension should cite the internal derivation step it builds on.
- Prefer simple robust computations and exact finite checks before expensive experiments.
- Use Wolfram, GAP, Python, and Lean as complementary tools rather than forcing all work through one system.
- Keep artifacts topic-specific and publication-facing; avoid local-machine assumptions in final outputs.
- If a path becomes unproductive, document why and pivot.

## High-Value Targets

Potential high-impact directions include, but are not limited to:

- Sharpening the polynomial rigidity exponent or isolating the dominant exponent loss.
- A toy theorem or experimentally supported conjecture linking the random-cover trace expansion to graph rigidity mechanisms.
- A framework for testing local spectral statistics at windows that shrink with cover degree.
- New multiplicity or delocalization consequences from the paper's estimates.
- A transferable proof template for Weil-Petersson random surfaces or variable-curvature covers.
- A computational benchmark suite for random-cover spectral rigidity heuristics.

The run should remain open to better directions discovered during the work.
