<!--
created: 2026-05-17T15:50:00Z
cycle: 1
run_id: run-phytograph-cycle1
agent: worker
milestone: M0.1
track: 6
-->

# Track 6 — Botanical Foundation Model Probe: Scoping

## (a) Central question

Use PhytoGraph as adversarial ground truth to measure where modern AI (LLMs, multimodal models, plant-ID classifiers) hallucinates plant biology, with particular attention to high-stakes failure modes.

## (b) Predictive targets (concrete, falsifiable)

1. **Per-(model × probe-category) error rates** with confidence-calibration profiles, across 7 probe categories: synonym confusion · toxicity look-alikes · hybrid pedigree · region-conditional knowledge · ghost-partner reasoning · convergence detection · phytochemistry safety.
2. **A public adversarial test set** drawn from PhytoGraph ground truth, large enough to be statistically meaningful (≥ 30 questions per category per model).
3. **A taxonomy of botanical-hallucination failure modes** with measurable per-mode error rates and chain-of-thought recovery rates.
4. **Policy-relevant toxicity-look-alike finding (per H6).** Error rate on toxicity look-alikes is high enough to be policy-relevant — meaning > 5% of look-alike questions answered with high confidence and dangerous direction.

## (c) Formal target (mathematical object)

A categorical error-type taxonomy `E = {synonym_drift, toxicity_misclassification, hybrid_pedigree_error, region_conditional_error, anachronism_blind, convergence_confused, preparation_unsafe}` and a per-(model, category) measure
`error_rate(m, c) = (1/|Q_c|) Σ_{q ∈ Q_c} I(classify(response(m,q)) ∈ E_c)`
with companion calibration measure
`ECE(m, c) = Σ_b w_b × |confidence_b − accuracy_b|`
(expected calibration error binned by stated confidence).

Stated invariance: under prompt-template-shuffling (paraphrasing of the same question), high-information probe questions should give near-identical error rates per model. Cross-template error-rate variance above a threshold is itself a finding (prompt-sensitivity is part of the failure profile).

## (d) Data sources required

- Free/open-source or already-local LLMs/classifiers only.
- Public benchmark artifacts and deterministic scoring scripts.
- Public datasets and license-respecting offline/local plant-ID resources where available.
- PhytoGraph substrate (ground truth source).

## (e) Minimum viable scale

- ≥ **3 free/open-source or already-local model/classifier configurations**, if available without paid API calls. If fewer are locally available, publish the static benchmark plus deterministic scoring harness and mark model execution `data-limited`.
- ≥ **7 probe categories**.
- ≥ **30 questions per (model × category)** = 3 × 7 × 30 = **630 scored cases per pass**, target.
- ≥ **3 prompt-template variants per question** for the invariance check → **1,890 scored cases per full pass**, target.
- Question generation: questions are programmatically generated from PhytoGraph ground-truth edges (e.g. a `synonym_cluster` produces N synonym-confusion questions; a `crop_pedigree` produces hybrid-pedigree questions). Need ≥ 5 ground-truth edges per category × question-template count to meet the 30-question floor.
- If we cannot reach 3 free/open-source/local models × 7 categories × 30 questions, Track 6 may still publish the benchmark and scoring harness, but must label model execution `data-limited`.

## (f) Falsification protocol

- **Ceiling-effect falsification.** If all foundation models score > 90% on a category, the probe is too easy. Harden by drawing harder PhytoGraph cases (rare polyploids, region-specific synonymy, deep ethnobotanical literature) and re-run.
- **Prompt-template confound.** If error rate varies > 30% across prompt-template variants for the same question, the finding is partly about prompts and not knowledge — report as such per directive H6 / H7.
- **Vendor-claim avoidance.** Findings are about failure modes, not vendor inadequacy. Phrase results accordingly.
- **Ground-truth fragility.** If a probe question's "correct" answer is itself contested in PhytoGraph (taxonomic conflict), exclude it from the error-rate denominator and file it under `data-limited`.

## (g) Parallelism axis

**Per-(free/open/local model × category × question-batch) fan-out** — the most parallel track in the campaign. The (model × category) matrix is the outer fan-out; per-question batching is the inner fan-out. Binding constraints are local compute, public-data quality, and benchmark design, not paid API rate limit or cost.

## (h) Prior-campaign kernel contribution

- **Retire:** the prior campaign had no LLM-probe layer.
- **Lift:** the prior synonym-cluster machinery is the substrate for the synonym-confusion probe category.
- **Lift:** the prior leakage-control discipline applies — probe ground truth must not leak into the question template (e.g. the question must not contain the answer).

## (i) Budget guidance (must be honored)

Track 6 must be free/open-source/public-materials only for this run. Paid, pay-as-you-go, or key-gated model APIs are out of scope. Do not export provider keys, do not run live paid-provider smoke tests, and do not build future milestones around a USD cap. If local/open model execution is unavailable, produce the benchmark, scoring scripts, and `data-limited` execution note instead.
