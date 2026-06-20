---
created: 2026-05-18T13:29:20+00:00
milestone: M3.T6
agent: fork-e08673192f98-clone-5
schema_version: phytograph v1.0
runner_mode: benchmark_only_data_limited
---

# Track 6 Foundation Model Probe — Offline Runner

## Status

**benchmark-only / data-limited for model execution.** The Track 6 Wave 3 runner executed the offline scoring path against deterministic local controls. No hosted, paid, key-gated, remote, or live model provider was called. No local free/open model runtime plus model weights were discoverable in the workspace, so this artifact does not claim foundation-model error rates.

## Inputs

- `tracks/track6/data/offline_probe_question_bank.parquet`
- `tracks/track6/data/probe_ground_truth_edges.parquet`
- `tracks/track6/scripts/score_offline_probe.py`

## Outputs

- `tracks/track6/data/probe_results.tsv`
- `tracks/track6/data/probe_model_summary.tsv`
- `tracks/track6/data/probe_category_summary.tsv`
- `tracks/track6/data/local_model_availability.json`
- `tracks/track6/data/offline_probe_error_by_category.png`
- `tracks/track6/track6_foundation_model_probe.md`

## Probe Coverage

Questions scored: **210** across **7** categories.

| category | questions |
|---|---|
| convergence_detection | 30 |
| ghost_partner_reasoning | 30 |
| hybrid_pedigree | 30 |
| phytochemistry_safety | 30 |
| region_conditional | 30 |
| synonym_confusion | 30 |
| toxicity_lookalike_media_scope | 30 |

## Local Model Availability

Runner mode: `benchmark_only_data_limited`.
Runnable local open model config found: `False`.
Runtime modules available: `{"llama_cpp": false, "torch": false, "transformers": false}`.
Local model files found: `0`.

Because no runnable local model configuration was available, `probe_results.tsv` contains deterministic controls only. These rows validate the offline scoring mechanism; they are not model performance measurements.

## Control Results

| model_id | result_role | questions | passed | missing_responses | pass_rate |
|---|---|---|---|---|---|
| empty_response_control | negative_control | 210 | 0 | 210 | 0.000 |
| forbidden_overclaim_control | negative_control | 210 | 0 | 0 | 0.000 |
| rubric_minimal_scoped_control | positive_control | 210 | 210 | 0 | 1.000 |
| verbatim_expected_answer_diagnostic | scorer_limitation_probe | 210 | 90 | 0 | 0.429 |

## Mechanism Interpretation

- `rubric_minimal_scoped_control` is the positive control: it includes every required rubric term and no forbidden terms.
- `empty_response_control` is a missing-output negative control.
- `forbidden_overclaim_control` is a high-stakes overclaim negative control.
- `verbatim_expected_answer_diagnostic` passed at rate `0.429` because the scorer is lexical: several narrative expected answers contain forbidden phrases in explicitly negated form. This is a scorer limitation to fix before treating results as semantic model evaluation.

The current instrument therefore validates the offline benchmark and deterministic scoring path, not any live/local foundation-model capability. Wave 4 validation should either add a local semantic scorer or require manually audited response subsets before making publishable model-error claims.

## Evidence Boundaries

- Synonym rows test name-normalization stability only; they do not support trait, range, edibility, or phylogeny claims.
- Hybrid/pedigree rows test source-scoped parentage reasoning only; they do not establish new taxonomy, dates, or performance.
- Region rows test region/status scoping only; native/current/global distribution remain distinct.
- Ghost-partner rows test recognition of cited hypotheses; they are not validation of extinct ecological interactions.
- Convergence rows test whether trait similarity is overread; they do not establish convergence without Track 3 analysis.
- Phytochemistry rows test safety/bioactivity overclaim resistance; they do not support clinical efficacy, dose, or edibility advice.
- Media-scope rows test image-evidence boundaries; image availability is not biological importance or safety evidence.

## Barrier 3 Readiness

Track 6 can be exposed in the Atlas as an offline benchmark with deterministic control results and clear `data-limited` status for actual model scoring. It is not ready to contribute model leaderboard claims until a free/open/local model adapter or audited response file is added.
