---
created: 2026-05-14T00:20:00Z
cycle: 8
run_id: run-2026-05-13T204826Z
agent: worker
milestone: M-8
---

# Implementation Roadmap

This roadmap prioritizes engineering work that makes the validated factory easier to install, extend, audit, and connect to real agents. Benchmark expansion comes after those surfaces are stable.

## Track 1: Package the Prototype

Priority: near-term engineering.

Goal: turn `alignment-test-factory/` into an installable Python package with stable CLI entry points.

Recommended work:

- Add packaging metadata such as `pyproject.toml`.
- Expose CLIs for schema export, spec validation, family runs, stress runs, and Inspect smoke runs.
- Replace ad hoc `sys.path` insertion with normal package imports.
- Add a top-level developer README for setup and command usage.
- Keep generated artifacts under the existing examples directories.

Acceptance criteria:

- `python -m pytest` passes from a fresh checkout after installing the package in editable mode.
- Existing commands have equivalent package CLI entry points.
- The exported JSON Schema is reproducible.
- No provider-specific or Inspect-specific fields leak into the core `TaskSpec` contract.

## Track 2: Real-Agent Trace Ingestion

Priority: near-term engineering.

Goal: map real agent logs into the validated trace vocabulary without weakening deterministic scoring.

Recommended work:

- Define an adapter interface that emits `observation`, `tool_call`, `state_update`, `permission_decision`, `delegation_message`, `final_answer`, and optional `scorer_event` records.
- Build one file-based adapter for a simple JSONL trace format before adding provider or CLI-specific adapters.
- Add adapter validation that runs `validate_trace_integrity()` before any task scorer.
- Add fixtures for missing tool-call results, missing permissions, malformed event IDs, and final-answer-only logs.

Acceptance criteria:

- A real or simulated agent trace can be converted into the factory trace model without changing scorer code.
- Invalid converted traces are rejected as `invalid_trace`, not scored as pass/fail.
- Under-evidenced converted traces become requirement failures or `inconclusive`, not pass.
- Adapter metadata remains outside the semantic task fields.

## Track 3: First-Class Scorer Evidence Bundles

Priority: near-term engineering.

Goal: make scorer events part of canonical audit bundles rather than summary-side metadata only.

Recommended work:

- Append scorer events to an explicit audit trace or bundle after deterministic scoring.
- Require every fail and inconclusive result to cite evidence event IDs or a documented absence of evidence.
- Add integrity checks that scorer event evidence links point to non-scorer trace events.
- Export a compact developer finding format with verdict, rationale, evidence IDs, and remediation hint.

Acceptance criteria:

- Stress integrity checks cover scorer evidence links in normal family outputs.
- Developers can trace every finding back to specific runtime events.
- Missing evidence links fail integrity validation.
- Existing M-6 and M-7 summaries remain reproducible.

## Track 4: Inspect-Native Packaging

Priority: medium-term engineering.

Goal: make Inspect the easiest harness path while keeping factory semantics independent.

Recommended work:

- Package each family as an Inspect task with shared deterministic scorer wrappers.
- Keep task specs as external JSON artifacts loaded by the eval, not hard-coded provider prompts.
- Preserve the current behavior of running task files from their containing directory for this Inspect version.
- Add log-manifest utilities that identify the exact JSON log created by each run.

Acceptance criteria:

- A developer can run one family or all families through Inspect with one documented command.
- Inspect score summaries agree with deterministic runner summaries.
- Inspect logs preserve enough metadata to link back to task specs and factory predicate results.

## Track 5: Metadata-Only Compatibility Surfaces

Priority: medium-term engineering.

Goal: interoperate with existing benchmark discipline without importing unsafe or heavyweight corpora.

Recommended lightweight sketches:

- garak-style probe metadata: category, goal, benign fixture, expected failure label, deterministic predicates, and safety boundary notes.
- HarmBench/JailbreakBench-style benchmark card: threat model, allowed content, disallowed content, scorer definition, split/version, and reproducibility command.
- Leaderboard-style result package: task ID, family, version, model/agent adapter metadata, pass/fail/inconclusive counts, invalid-trace counts, and artifact hashes.

Acceptance criteria:

- Compatibility exports are metadata-only.
- No external harmful prompts, attacks, payloads, or benchmark corpora are vendored.
- Exports can be regenerated from existing task specs and score summaries.
- The final benchmark card distinguishes synthetic validation from real-agent validation.

## Track 6: New Task Families

Priority: benchmark expansion after Tracks 1-3.

Candidate families:

- Recovery after misleading context.
- Hidden objective substitution in benign task planning.
- File-output validation and stale artifact handling.
- Memory mutation and unauthorized state persistence.
- Multi-agent delegation chains with scoped context propagation.
- Tool-result verification before final claims.

Acceptance criteria for each family:

- Valid and invalid specs exist.
- Compliant and violating traces are scripted.
- Deterministic predicates have evidence-linked verdicts.
- Final-answer-only traces are invalid or inconclusive, not pass.
- At least one stress probe covers gaming, ambiguity, false-positive risk, false-negative risk, or trace integrity.
- Inspect exposure is added only after deterministic runner behavior is validated.

## Track 7: Model-Assisted Judging With Guardrails

Priority: later, only where deterministic scoring leaves semantic residue.

Goal: use model-assisted judging sparingly for cases that cannot be reduced to structured trace predicates.

Recommended work:

- Require a deterministic prefilter before any model-assisted judgment.
- Store judge prompt metadata and rationale fields in task specs.
- Make model-assisted judgment optional and clearly labeled in summaries.
- Add agreement checks against deterministic fixtures.

Acceptance criteria:

- Model-assisted judging never overrides trace integrity failure.
- It cannot convert missing required trace evidence into pass.
- It is used only when a task spec explains why deterministic scoring is insufficient.

## Work Not Recommended Yet

Do not bulk-import external red-team datasets. The current value-add is safe agentic trajectory testing, not corpus scale.

Do not add live model/provider integrations before trace ingestion is stable. Without reliable trace conversion, deterministic scorers will produce misleading confidence.

Do not expand task families faster than stress coverage. Every new predicate should ship with stress probes.

Do not move toward final-answer-only scoring. That would lose the central advantage of this factory.
