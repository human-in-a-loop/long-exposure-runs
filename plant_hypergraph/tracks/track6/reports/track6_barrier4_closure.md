---
created: 2026-05-18T13:29:31+00:00
milestone: M4.V6
agent: fork-0b556d9370a2-clone-2
schema_version: phytograph v1.0
status: environment_limited_closure
---

# Track 6 Barrier 4 Closure

## Closure Decision

Track 6 closes Barrier 4 as **benchmark-only / environment-limited for model execution**. The static adversarial benchmark, deterministic scorer, control outputs, and Atlas integration are usable research infrastructure. They do not support H6 model-error-rate claims because no runnable free/open/local model configuration is available in the current workspace and paid, key-gated, hosted, or remote providers are out of scope for this recovery branch.

H6 is therefore **not validated** in this run. It remains a testable hypothesis for a future environment that supplies audited local model responses or an approved free/open local model runtime with weights.

## Evidence Inspected

Track 6 artifacts already present and re-checked:

- `tracks/track6/data/offline_probe_question_bank.parquet`
- `tracks/track6/data/probe_ground_truth_edges.parquet`
- `tracks/track6/scripts/score_offline_probe.py`
- `tracks/track6/scripts/run_offline_probe.py`
- `tracks/track6/data/probe_results.tsv`
- `tracks/track6/data/probe_model_summary.tsv`
- `tracks/track6/data/probe_category_summary.tsv`
- `tracks/track6/data/local_model_availability.json`
- `tracks/track6/track6_foundation_model_probe.md`

The offline runner was refreshed on 2026-05-18 with `python3 tracks/track6/scripts/run_offline_probe.py --no-plot`.

## Local Runtime Availability

The refreshed availability probe is workspace-local only: it does not import model runtimes, call a network service, or perform inference.

| Probe | Observed value |
|---|---|
| `runner_mode` | `benchmark_only_data_limited` |
| `local_open_model_runnable` | `false` |
| `transformers` module | `false` |
| `torch` module | `false` |
| `llama_cpp` module | `false` |
| local model files | `0` |
| checked_at | `2026-05-18T13:29:20+00:00` |

Mechanism: Track 6 needs both a local inference runtime and local model weights before any foundation-model response can exist. With both absent, all response rows must be controls or fixtures. Treating controls as model outputs would confound scorer validation with model evaluation.

## Deterministic Control Results

`probe_results.tsv` contains 840 rows: 210 questions across 7 categories, scored under four deterministic controls.

| control | role | questions | passed | pass_rate | interpretation |
|---|---:|---:|---:|---:|---|
| `rubric_minimal_scoped_control` | positive | 210 | 210 | 1.000 | Scorer accepts responses containing all required terms and no forbidden terms. |
| `empty_response_control` | negative | 210 | 0 | 0.000 | Scorer rejects missing responses. |
| `forbidden_overclaim_control` | negative | 210 | 0 | 0.000 | Scorer rejects responses that include a forbidden overclaim term. |
| `verbatim_expected_answer_diagnostic` | scorer-limit probe | 210 | 90 | 0.429 | Narrative expected answers can contain forbidden phrases in negated contexts, exposing lexical scorer limits. |

The controls validate the deterministic scoring path, not any model's botanical reasoning.

## Scorer Limitation

The current scorer is lexical: it checks required substrings and forbidden substrings. This is useful for deterministic guardrail tests, but it is not a semantic evaluator. The `verbatim_expected_answer_diagnostic` result is the decisive evidence: a human-written expected answer can fail when it names a forbidden overclaim in order to reject it.

Consequence: future model runs need at least one of:

- manually audited response subsets for each probe category;
- a structured-answer format that separates answer fields from caveat fields before lexical scoring;
- a local semantic judge with its own calibration set, if a free/open/local judge is available.

## H6 Status

H6 stated: "Foundation models will exhibit systematic, measurable failure modes on synonym confusion, hybrid pedigree, and region-conditional questions. Failure rate on toxicity look-alikes will be high enough to be policy-relevant."

Barrier 4 status: **environment-limited / untested**.

What is supported:

- A 210-question static benchmark exists across 7 Track 6 categories.
- Ground-truth adversarial-probe edges exist with provenance and evidence-scope caveats.
- Deterministic controls verify that the scorer can accept scoped answers and reject empty or overclaiming answers.
- The Atlas can expose Track 6 as benchmark/control infrastructure with data-limited status.

What is not supported:

- No model error rate.
- No leaderboard.
- No vendor or model-family comparison.
- No claim that toxicity look-alike failure rates are policy-relevant.
- No claim that synonym, pedigree, or region-conditional failures have been observed in a foundation model.

## Barrier 4 Recommendation

Do not promote any Track 6 rows to `prediction_ledger.tsv` as validated or falsified model-performance predictions. Keep the master prediction and speculation ledgers header-only for Track 6 unless a future branch supplies audited local model responses.

Recommended ledger classification for this branch: `M4.V6` deferred with high confidence, rationale "environment-limited: benchmark and deterministic controls exist, but local free/open model runtime plus weights are absent."

## Minimal Future Data Recipe

To reopen H6 without paid or key-gated APIs:

1. Install or provide a free/open local model runtime and compatible local weights under a documented license.
2. Add an explicit adapter that writes response TSV rows with `question_id`, `model_id`, `response_text`, runtime metadata, model license, and prompt template hash.
3. Run the 210-question benchmark without changing the question bank.
4. Score with the deterministic scorer and manually audit a stratified subset covering all 7 categories.
5. Only then compute per-category error rates and calibration summaries.

