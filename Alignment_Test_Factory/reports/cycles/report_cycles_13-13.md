---
title: "Open Alignment Test Factory - cycles 13-13"
date: "2026-05-14"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# Open Alignment Test Factory - cycles 13-13

## Abstract

Cycle 13 closed the Open Alignment Test Factory campaign. The researcher, worker, and auditor sessions all recorded the same state: the campaign had already completed its planned build and validation work, no new research or implementation was needed, and closure was validated.

No commands were run in cycle 13. No new task families, tools, tests, figures, or benchmark artifacts were created. The cycle’s purpose was final confirmation that the completed prototype and reports were sufficient. The validated end state remained:

- `pytest`: 31 passed.
- Stress runner: `matched_expectations: 11/11`.
- Multi-family Inspect suite: 8 samples, accuracy `1.000`.
- `promise_check`: exit 0, with known non-blocking bookkeeping warnings.
- `org_check`: green.

The final campaign artifacts remain `reports/final/final_report.md`, `reports/final/artifact_index.md`, and `reports/final/roadmap.md`.

## Introduction

The Open Alignment Test Factory campaign asked whether a practical open-source toolchain could turn high-level safety properties into safe, reproducible, nontrivial alignment tests for agentic AI systems. In this campaign, “agentic” means systems that may use tools, maintain state or memory, delegate subtasks, make multi-step plans, and act under partial or ambiguous instructions.

The completed prototype answered that question within a scoped synthetic setting. Its validated mechanism is:

high-level safety property -> provider-agnostic `TaskSpec` -> benign scripted trajectory or runtime trace -> trace integrity validation -> task trace requirement validation -> deterministic evidence-linked scorers -> Inspect-compatible logs and summaries -> stress-tested benchmark report -> developer-facing final documentation.

A `TaskSpec` is the provider-independent task description used by the prototype. A trace is the structured record of intermediate actions, tool calls, approvals, delegations, observations, and final answers. Deterministic scorers are rule-based checks that produce reproducible pass, fail, or inconclusive verdicts from trace evidence rather than relying only on final text. Inspect-compatible logs and summaries connect the prototype to Inspect AI, the open evaluation harness used as the campaign’s primary execution and reporting surface [1].

Cycle 13 did not extend this mechanism. It confirmed that the mechanism had already been built, validated, documented, and closed.

## Approach

The reporting pass used the cycle 13 source record as the primary evidence:

- Researcher session `226b8489-8d60-469e-88dc-34dcf967c4aa`, created on 2026-05-14.
- Worker session `3c56d343-0536-43e3-8564-aaf596957025`, created on 2026-05-14.
- Auditor session `b7d62235-bee1-4b02-87d3-3bc8658ea7b0`, created on 2026-05-14.
- Supplied cycle 13 audit report.
- Workspace artifacts, including `REFERENCES.md`, `MANIFEST.md`, the final reports, and existing figures.

The cycle 13 source record is consistent across all roles. The researcher said no new questions were active, no build or run was recommended, and future work should begin from `reports/final/roadmap.md` if opened as a new campaign. The worker performed no build and ran no commands because the campaign was already complete. The auditor issued a `VALIDATED` decision with no CRITICAL or MODERATE findings.

The reporting pass also scanned the workspace for existing figures. No cycle 13-specific figures were created. The relevant existing evidence figures remain the multi-family verdict matrix and the benchmark stress matrix, both produced before cycle 13 and carried forward as validated artifacts.

## Findings

### Cycle 13 Confirmed Closure

Cycle 13’s central finding is that closure sufficiency was met. The campaign had already completed milestones M-1 through M-8, and the final package was present.

The researcher session recorded the closure criteria directly: no new research, build, test, or audit work remained. It also restated the conditions that would have falsified closure: a missing final artifact, failed core validation, unsafe benchmark content, unresolved CRITICAL or MODERATE audit findings, or claims beyond the validated synthetic deterministic scope. None of those conditions appeared in the cycle 13 record.

The worker session recorded no implementation activity. This was not a missing work item. It was the intended outcome for a closure-only cycle after validation.

The auditor session issued the final decision:

- CRITICAL findings: none.
- MODERATE findings: none.
- MINOR findings: known `promise_check` bookkeeping warnings, already classified as non-blocking.
- Decision: `VALIDATED`.

### The Final Validated Artifacts Were Unchanged

Cycle 13 confirmed the same final artifact set reported in the supplied audit record:

- `reports/final/final_report.md`
- `reports/final/artifact_index.md`
- `reports/final/roadmap.md`

The final report explains what the campaign learned and what was built. The artifact index maps developers to the files needed to inspect or run the prototype. The roadmap identifies next implementation priorities, including packaging, stable command-line interfaces, real-agent trace ingestion, and first-class scorer evidence bundles.

### The Validated Prototype Scope Remained Synthetic and Defensive

The auditor confirmed that the benchmark content stayed within the stated safety boundary. The validated prototype uses benign synthetic scenarios rather than harmful payloads, credential-stealing material, malware, evasion recipes, or operational abuse workflows.

The closure decision also kept the claims scoped. The prototype validates a synthetic deterministic alignment evaluation path. It does not claim to validate arbitrary real-world agents. The future-work path for real agents is documented in `reports/final/roadmap.md`.

### Existing Evidence Figures Remain the Relevant Visual Summary

The cycle did not create new figures. The two existing benchmark evidence figures remain the compact visual record of the validated executable path.

![Four-family deterministic verdict matrix for the validated task families.](alignment-test-factory/examples/families/multi_family_verdict_matrix.svg)

The multi-family matrix summarizes the deterministic verdicts for four safe task families: permission/tool overreach, provenance trace mismatch, uncertainty escalation, and delegation drift.

![Stress probe outcomes showing 11 matched expectations across gaming, ambiguity, false-positive, false-negative, and trace-integrity probes.](alignment-test-factory/examples/stress/benchmark_stress_matrix.svg)

The stress matrix summarizes the benchmark’s validation against expected outcomes for gaming, ambiguity, false-positive, false-negative, and trace-integrity probes.

## Discussion

Cycle 13 did not change the project’s technical state. Its value was confirmatory: it established that the campaign should stop rather than expand into another build loop.

That matters because the original mission emphasized concrete artifacts over commentary. By cycle 13, the campaign had already produced the expected concrete path: a provider-agnostic task schema, safe task examples, a deterministic toy environment, trace validation, deterministic scorers, Inspect-compatible smoke evals, multi-family task coverage, stress testing, and developer-facing documentation.

The repeated closure decision prevents benchmark expansion from becoming a substitute for packaging and adoption work. The next useful work is not to add more synthetic families inside this completed campaign. It is to begin a new implementation track from the roadmap, especially around stable interfaces, real-agent trace ingestion, and better evidence packaging for scorer outputs.

## Open Questions

No open questions remain inside this campaign.

Future work exists, but it belongs to a new campaign or development phase. The cycle 13 record identifies the next starting point as `reports/final/roadmap.md`, with priority on:

- Packaging and stable command-line interfaces.
- Real-agent trace ingestion.
- First-class scorer evidence bundles.
- Broader benchmark coverage only after the above foundations are stronger.

## References

[1] UK AI Security Institute, "Inspect AI: Framework for Large Language Model Evaluations," 2024. https://inspect.aisi.org.uk/

## Appendix: Implementation Details

### Source Sessions

| Role | Session ID | Date | Cycle 13 content |
|---|---|---:|---|
| Researcher | `226b8489-8d60-469e-88dc-34dcf967c4aa` | 2026-05-14 | Closure-only assessment; no new research questions; no build or run recommended. |
| Worker | `3c56d343-0536-43e3-8564-aaf596957025` | 2026-05-14 | No build performed and no commands run; final artifacts and validation state restated. |
| Auditor | `b7d62235-bee1-4b02-87d3-3bc8658ea7b0` | 2026-05-14 | Final `VALIDATED` decision; no CRITICAL or MODERATE findings. |

### Files and Artifacts

Cycle 13 created no new prototype artifacts and no new figures. The reporting pass updated `MANIFEST.md` as a current workspace snapshot after the prior cycles 10-12 report had been written by the orchestrator.

The manifest now records:

- Scripts and code files: 18.
- Test files: 6.
- Markdown documentation/report files: 15.
- CSV data files: 4.
- JSON schema/spec/summary files: 17.
- Figure files: 4.
- Total tracked text files: 61.
- Total tracked text lines: 11,481.

The manifest update added:

- `reports/cycles/report_cycles_10-12.md` | 181 lines | Periodic closure report covering repeated campaign validation across cycles 10 through 12.

### Validation State Reported Upstream

Cycle 13 did not rerun tests or commands. It reported the already validated state from the closure record:

| Validation item | Reported result |
|---|---|
| `pytest` | 31 passed |
| Stress runner | `matched_expectations: 11/11` |
| Multi-family Inspect suite | 8 samples, accuracy `1.000` |
| `promise_check` | exit 0 with known non-blocking bookkeeping warnings |
| `org_check` | green |

### Cross-Reference Map

| Validated element | Primary artifact |
|---|---|
| Final synthesis | `reports/final/final_report.md` |
| Developer artifact map | `reports/final/artifact_index.md` |
| Future implementation plan | `reports/final/roadmap.md` |
| Task schema | `alignment-test-factory/src/alignment_test_factory/schemas.py` and `alignment-test-factory/schemas/task_spec.schema.json` |
| Trace validation | `alignment-test-factory/src/alignment_test_factory/trace.py` |
| Deterministic runtime | `alignment-test-factory/src/alignment_test_factory/runtime.py` |
| Deterministic scorers | `alignment-test-factory/src/alignment_test_factory/scorers.py` |
| Multi-family scripted tasks | `alignment-test-factory/src/alignment_test_factory/families.py` |
| Benchmark stress probes | `alignment-test-factory/src/alignment_test_factory/stress.py` |
| Inspect smoke adapters | `alignment-test-factory/evals/permission_tool_overreach_smoke.py` and `alignment-test-factory/evals/multi_family_smoke.py` |

### Record Gaps

There are no cycle 13 command transcripts because the cycle was intentionally closure-only and no commands were run by the researcher, worker, or auditor sessions. There are no cycle 13-specific figures or benchmark outputs for the same reason.
