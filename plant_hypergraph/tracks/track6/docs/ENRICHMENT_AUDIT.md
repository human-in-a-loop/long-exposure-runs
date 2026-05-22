---
created: 2026-05-17T20:54:35+00:00
milestone: M2.T6
agent: clone-5
schema_version: phytograph v1.0
---

# Track 6 Enrichment Audit — Offline Foundation-Model Probe Construction

## Status

**ready_offline_static / data-limited for live model execution.** This branch builds a static, free/open-source/offline botanical probe question bank and a schema-shaped ground-truth edge layer from the frozen Barrier 1 substrate. It does not execute, import, extend, or configure the superseded paid-provider M1.8 harness.

## Outputs

- `tracks/track6/data/offline_probe_question_bank.parquet`
- `tracks/track6/data/offline_probe_question_bank.tsv`
- `tracks/track6/data/probe_ground_truth_edges.parquet`
- `tracks/track6/data/probe_ground_truth_edges.tsv`
- `tracks/track6/data/offline_scoring_rubric.json`
- `tracks/track6/scripts/score_offline_probe.py`
- `tests/test_track6_offline_probe.py`

## Coverage

Question rows: **210**. Ground-truth adversarial-probe rows: **210**.

| category | questions | status |
|---|---:|---|
| `convergence_detection` | 30 | cleared |
| `ghost_partner_reasoning` | 30 | cleared |
| `hybrid_pedigree` | 30 | cleared |
| `phytochemistry_safety` | 30 | cleared |
| `region_conditional` | 30 | cleared |
| `synonym_confusion` | 30 | cleared |
| `toxicity_lookalike_media_scope` | 30 | cleared |

| supporting edge type | questions |
|---|---:|
| `anachronism_candidate_edge` | 30 |
| `bioactivity_assertion` | 30 |
| `crop_pedigree` | 30 |
| `cultivation_or_domestication` | 30 |
| `fruit_morphology` | 30 |
| `image_evidence` | 30 |
| `synonym_cluster` | 30 |

## Offline Constraint

- No Anthropic, OpenAI, Gemini, Pl@ntNet, iNaturalist, paid, remote, or key-gated provider was called.
- The old `substrate/staging/fm_probe_harness/` provider harness is preserved as historical superseded context only and is not imported by this branch.
- `foundation_model_response:offline_unrun` appears only as a schema-shaped placeholder in the ground-truth edge layer; it is not a model output.

## Evidence-Scope Discipline

Questions are generated only from existing Barrier 1 hyperedges. Each row carries the source edge id, source group, source id, source record id, license, access date, provenance pointer, caveats, and the source edge's allowed evidence scope. The expected answers are deliberately scoped: they ask what the edge supports and what it does not support.

No row claims new taxonomy, native range, edibility, toxicity, clinical efficacy, hybridization, anachronism, or bioactivity as established truth. The toxicity-lookalike lane is represented at this enrichment stage by media/evidence-scope guardrail questions because the frozen substrate has image evidence but no authoritative look-alike toxicity-pair ground truth.

## Data-Limited Notes

- All generated categories reached the target of 30 questions.
- Live model scoring remains out of scope until a future M3.T6 offline/local-open runner is explicitly authorized and available without paid or key-gated calls.
- True visual toxicity look-alike benchmarking needs authoritative paired image/ground-truth sources in a later enrichment or validation cycle.

## Deterministic Scoring Scaffold

The scorer in `tracks/track6/scripts/score_offline_probe.py` accepts a TSV/CSV of model-like answers with `question_id` and `response_text`. It performs deterministic required-term / forbidden-term checks against `offline_probe_question_bank.parquet` and emits per-row pass/fail diagnostics. This is a scaffold only; it does not call any model.

## Barrier 2 Readiness

The output is namespace-local under `tracks/track6/`, uses only schema v1.0 types, preserves provenance from source substrate edges, and does not modify the shared substrate. It is ready for Barrier 2 conformance checks as Track 6 enrichment.
