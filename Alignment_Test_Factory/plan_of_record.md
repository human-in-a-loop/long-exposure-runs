---
created: 2026-05-13T20:48:26Z
run_id: run-2026-05-13T204826Z
agent: researcher
---

# Plan of Record — # Long-Exposure Prompt: Open Alignment Test Factory

**Created:** 2026-05-13T20:48:26Z
**Run id:** run-2026-05-13T204826Z

## Directive (verbatim)

# Long-Exposure Prompt: Open Alignment Test Factory

## Mission

Build a practical open-source alignment test factory for agentic AI systems.

The goal is not to produce another static jailbreak list. The goal is to determine what the open-source community is missing for repeatable, developer-useful alignment testing, then design and prototype a toolchain that can generate, run, score, and audit alignment tests for realistic agent workflows.

Long-exposure should decide the research path, decomposition, experiments, and trade-offs without waiting for user ratification. Prefer concrete artifacts over commentary: runnable examples, schemas, scoring rubrics, toy environments, adapters to existing tools, analysis notebooks, failure taxonomies, and a final report that explains what was learned. Structure the run as staged research with periodic executable checkpoints, so the final output is grounded in tests rather than only synthesis. The milestones and deliverables below are starting guidance, not a fixed spec; long-exposure should revise them as the research clarifies what is most valuable.

## Core Question

Can we create a reusable "alignment test factory" that turns high-level safety properties into safe, reproducible, nontrivial eval tasks for agents with tools, memory, delegation, and multi-step plans?

## Why This Matters

Open-source alignment testing has useful building blocks, but the ecosystem is still uneven for agentic systems:

- Inspect AI provides a strong open evaluation harness and log format.
- garak provides broad vulnerability probing for LLM applications.
- HarmBench and JailbreakBench provide standardized red-team and jailbreak benchmark references.
- Many current tools emphasize static prompt-response behavior, while practical agents fail through tool misuse, delegation drift, hidden objective substitution, weak oversight, bad uncertainty handling, brittle refusal boundaries, and poor recovery from ambiguous instructions.

This run should ask what a developer would actually need to test an autonomous coding, research, data-analysis, or operations agent before trusting it with broader authority.

## Landscape Anchors

Use existing tools where they are strong, and avoid rebuilding solved infrastructure:

- Inspect AI: primary candidate harness for eval definitions, model/provider abstraction, scoring, and logs. See https://inspect.aisi.org.uk/
- garak: reference for vulnerability-probing taxonomy and optional adapter ideas. See https://docs.garak.ai/ and https://github.com/NVIDIA/garak
- HarmBench: reference for standardized red-team evaluation structure and attack/defense comparison. See https://www.microsoft.com/en-us/research/publication/harmbench-a-standardized-evaluation-framework-for-automated-red-teaming-and-robust-refusal/
- JailbreakBench: reference for clearly specified threat models, templates, scoring, and leaderboard-style reproducibility. See https://arxiv.org/abs/2404.01318

Treat these as foundations and constraints, not as endpoints. The value-add should be in generating and validating agentic alignment tests that are harder to cover with one-turn prompt benchmarks.

## Safety Boundary

Keep the work defensive, benchmark-oriented, and non-operational.

Do not produce or collect real harmful instructions, credential-stealing payloads, malware code, evasion recipes, or actionable abuse workflows. If a risk category requires adversarial testing, use harmless toy domains, abstract placeholders, synthetic policies, controlled sandboxes, or metadata-only adapters. The benchmark should test whether agents respect boundaries and preserve oversight without distributing harmful content.

## Concrete Ask

Over a multi-day long-exposure run, produce a grounded plan and prototype for an open alignment test factory that can:

1. Convert high-level safety properties into executable eval tasks.
2. Generate safe synthetic agent scenarios with controlled ambiguity and measurable expected behavior.
3. Exercise tool use, memory, delegation, uncertainty, oversight, and recovery paths.
4. Score behavior with deterministic checks where possible and model-assisted judging only where it adds clear value.
5. Emit reproducible logs, failure labels, and summaries that help developers improve agents.
6. Compare the prototype against existing open-source eval tools and identify which gaps remain.
7. Demonstrate at least one end-to-end eval path from scenario specification to execution log to scored finding.

## Suggested Research Threads

Long-exposure may pursue any thread it judges valuable, but should strongly consider:

- A taxonomy of agentic alignment failure modes that are not well covered by static jailbreak benchmarks.
- A minimal task specification schema for alignment eval generation.
- A safe synthetic environment where agents can use tools, create files, delegate subtasks, request permissions, handle conflicting objectives, and recover from misleading context.
- A deterministic scoring layer for file outputs, tool-call traces, policy compliance, provenance, and escalation behavior.
- Trace-level assertions that can catch failures even when the final answer looks plausible.
- A small set of prototype Inspect AI evals demonstrating different failure classes.
- Optional compatibility surfaces for garak-style probes, HarmBench/JailbreakBench-style benchmark metadata, or leaderboard-style result packaging.
- A "quality of benchmark" rubric: realism, reproducibility, safety, false-positive risk, gaming resistance, scoring clarity, and developer actionability.
- A gap analysis of what open-source alignment testing needs next.

## Suggested Milestone Ladder

This ladder is initial only. Keep the work broad, but force periodic grounding through increasingly realistic prototypes. If the live run discovers a stronger path, update the plan of record and follow the better path rather than mechanically preserving this sequence.

1. Map the landscape and identify the agentic alignment gaps that are most worth testing.
2. Define a small task schema and failure-label schema.
3. Build a minimal deterministic toy environment with benign tools and inspectable state.
4. Run a smoke eval with `mockllm/model` or another nonproduction target to verify harness wiring.
5. Add multiple task families that test distinct failure modes rather than superficial prompt variation.
6. Add deterministic scorers for output files, tool-call traces, permission boundaries, provenance, and escalation.
7. Stress-test the benchmark itself for gaming, ambiguity, false positives, and false negatives.
8. Package the findings into a developer-facing report and a next-step implementation roadmap.

## Important Blindspots To Address

Do not let the work collapse into a generic safety essay. It should produce usable scaffolding.

Do not equate alignment testing with jailbreak success rate alone. For agents, important failures include bad escalation judgment, silent policy drift, tool overreach, brittle recovery, missing provenance, bad uncertainty calibration, unsafe delegation, reward hacking against the evaluator, and plausible but unverified final claims.

Do not rely only on agentic judges. Where possible, create deterministic fixtures and expected traces. Use model-assisted judging only for cases where semantic assessment is unavoidable, and record why it was needed.

Do not overfit to one model provider, one CLI, or one agent architecture. The factory should be provider-agnostic at the task/spec level.

Do not make the benchmark unsafe by publishing harmful payloads. Use benign analogues that preserve the alignment structure without operational risk.

Do not accept a benchmark design that only evaluates final text. Agentic failures often occur in intermediate actions, hidden assumptions, bad tool choices, or missing verification. Capture traces and score them directly where possible.

## Desired Artifacts

By the end of the run, aim to produce:

- A landscape review of existing open alignment and red-team tooling.
- A failure-mode taxonomy for agentic alignment testing.
- A benchmark/task schema with examples.
- A small prototype test factory, preferably using Inspect AI as the execution harness.
- Several safe generated eval tasks covering distinct agentic failure modes.
- Deterministic scorers for at least some tasks.
- Optional adapter sketches for garak, HarmBench, or JailbreakBench metadata if they add real value.
- A final report explaining what exists, what is missing, what was built, and what should come next.

## Workspace And Dependencies

Use `<RUN_WORKSPACE>` as the working directory.

The following minimal environment has been prepared for this run:

- Python 3.12
- `uv`
- Virtual environment: `<RUN_WORKSPACE>/.alignment-eval-venv`
- Installed packages: `inspect-ai`, `pandas`, `pydantic`, `pytest`

Use this environment for prototype evals and validation:

```bash
source <RUN_WORKSPACE>/.alignment-eval-venv/bin/activate
```

The Inspect AI smoke path has been verified with `mockllm/model`. In this installed version, run Inspect task files from their containing directory or with relative task paths; absolute task file paths can fail during task discovery.

Do not install large benchmark datasets or heavyweight red-team repositories unless long-exposure determines they are a real value-add. Prefer lightweight adapters, schema compatibility, and documentation over copying external corpora. If an optional dependency is needed, explain why it is worth the added complexity before using it.

`<OPTIONAL_LOCAL_WOLFRAM_TOOL>` exists as a local skill/tool for Wolfram Language access, but it is not expected to be a gate for this run unless a mathematical modeling thread needs it.

Wolfram support has been smoke-tested in the workspace with `wolfram-batch`; a simple symbolic integral returned the expected result. If useful, long-exposure may use Wolfram Language through `wolfram-batch -script <file.wls>` for heavier numerical or symbolic simulations, but it should only do so where this adds real value over Python or Inspect AI prototypes.

## Success Criteria

The run is successful if it produces a credible tool-building path that an open-source developer could inspect and extend. A strong outcome would include a runnable prototype, clear examples, deterministic scoring for multiple failure classes, trace-level evidence, and a report that distinguishes high-value future work from low-value benchmark expansion.

The final output should make a developer think: "This is a practical way to test agent behavior that existing jailbreak lists and one-turn evals miss."

## Goals

| Goal ID | Goal | Owner |
|---------|------|-------|
| G1 | Identify the agentic alignment testing gaps not adequately covered by static prompt-response or jailbreak benchmarks. | researcher |
| G2 | Define a provider-agnostic task/failure schema that converts high-level safety properties into executable, safe synthetic scenarios. | researcher |
| G3 | Prototype a minimal deterministic test factory using Inspect AI as the primary execution/logging harness. | worker |
| G4 | Demonstrate and audit multiple agentic failure families with trace-level deterministic scoring and reproducible logs. | worker/auditor |
| G5 | Package findings into developer-facing guidance, gap analysis, and an extension roadmap. | final reporter |

## Milestones

| Milestone ID | Goal | Description | Success criteria (falsifiable) | Dependencies |
|--------------|------|-------------|--------------------------------|--------------|
| M-1 | G1 | Landscape and gap map for open alignment/red-team tooling, focused on agentic workflows. | `docs/landscape_gap_map.md` identifies at least 6 agentic failure modes, maps each to Inspect/garak/HarmBench/JailbreakBench coverage, and names at least 3 gaps requiring new factory machinery. | — |
| M-2 | G1/G2 | Failure-mode taxonomy and benchmark quality rubric. | `docs/failure_taxonomy.md` defines labels for tool misuse, delegation drift, oversight failure, uncertainty, recovery, provenance, and evaluator gaming; `docs/benchmark_quality_rubric.md` gives measurable criteria for realism, safety, reproducibility, scoring clarity, false-positive risk, and developer actionability. | M-1 |
| M-3 | G2 | Minimal task specification and failure-label schemas with safe examples. | Pydantic or JSON Schema files in `alignment-test-factory/schemas/` validate at least 3 example task specs covering distinct failure modes and reject at least 2 malformed specs in tests. | M-2 |
| M-4 | G3 | Deterministic toy environment with benign tools, inspectable state, and trace capture. | Runnable code in `alignment-test-factory/` exposes safe file/memory/delegation/permission tools and records trace events sufficient for deterministic scoring. | M-3 |
| M-5 | G3/G4 | Inspect smoke eval path from scenario spec to scored log. | Running from the task directory with `mockllm/model` produces an Inspect log and a machine-readable score summary for at least 1 generated task. | M-4 |
| M-6 | G4 | Multiple task families and deterministic trace/file/provenance scorers. | At least 4 task families run, each has expected pass/fail behavior, deterministic scorer coverage, and one negative fixture showing the scorer catches a known failure. | M-5 |
| M-7 | G4/G5 | Benchmark stress test for gaming, ambiguity, false positives, and false negatives. | `reports/benchmark_stress_test.md` documents at least 4 benchmark failure probes and either validates or revises the schema/scorers accordingly. | M-6 |
| M-8 | G5 | Final developer report and roadmap. | `reports/final/final_report.md` explains what exists, what was built, reproducible commands, limitations, and prioritized next steps. | M-7 |

## Out of scope (explicit)

- Real harmful instructions, credential theft payloads, malware/evasion workflows, or operational abuse content.
- Bulk downloading external benchmark corpora or vendoring heavyweight red-team repositories unless a later plan revision justifies the added complexity.
- Provider-specific benchmark design that only works for one hosted model API or one agent CLI.
- Final-text-only scoring as the primary evaluation signal for agentic behavior.

## Pointer to ledger

Every milestone status, history, and judgment lives in `promise_ledger.jsonl`,
filtered by `milestone_id`. Run `promise_check` to materialize the current
state for the human; agents call it via Bash:

    python3 -m long_exposure.tools.promise_check .

The directive section above is **immutable** after creation. Goals and
milestones tables are mutable, but every edit must emit a ledger event with
`milestone_id: "_plan/<descriptive-change-name>"` so the audit trail is
complete.
