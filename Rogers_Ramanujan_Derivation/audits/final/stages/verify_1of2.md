# Verify Pass 1 of 2

Scope from `audits/final/explore.md`: `M0`, `M1`, `M2`, `_orphan/worker-combined-finite-foundation`, `_orphan/worker-repro-test-k12`, `_run/start`.

## Method

- Checked latest ledger event status and confidence for each scoped id.
- Verified cited artifacts exist on disk.
- Read support documents/scripts/data for terms and structure matching the ledger claims; CSV coefficient tables were treated as data artifacts and checked for existence/nonempty content rather than prose terms.
- Checked whether earlier low/provisional-confidence events in this slice were later reverified; none in this slice required that special handling.

## Results

### `M0`

- Ledger state: `validated` / `high`.
- Claim checked: M0 validated: the formal-power-series setup is usable for later Rogers-Ramanujan proof cycles, and computational observations are not promoted to proof.
- Artifact existence: pass.
- Support file `docs/lemmas/lemma_catalogue.md`: supports claim; matched/checked Formal power series|Z\[\[q\]\], coefficientwise, truncation|stabilization, staircase.
- Support file `docs/validation.md`: supports claim; matched/checked computational|experiment, not proof|not treated as proof|discovery.
- Low/provisional follow-up: not applicable.
- Verify verdict: `supported`.

### `M1`

- Ledger state: `validated` / `high`.
- Claim checked: M1 validated: the finite approximant harness is reproducible and adequate for discovery, with recurrence/product observations kept separate from proved identities.
- Artifact existence: pass.
- Support file `scripts/rr/finite_rr_experiments.wls`: supports claim; matched/checked KMax|KMAX, RR1|Rogers, negative|NC|control.
- Support file `data/finite_experiments/rr_recurrence_candidates.csv`: supports claim; matched/checked none_through_KMax|residual, first_nonzero.
- Support file `data/finite_experiments/rr_coefficients.csv`: supports claim; matched/checked exists.
- Support file `data/finite_experiments/rr_difference_heatmap.png`: supports claim; matched/checked exists.
- Low/provisional follow-up: not applicable.
- Verify verdict: `supported`.

### `M2`

- Ledger state: `validated` / `high`.
- Claim checked: Cycle 8 audited and M2 validated: the derived Bailey-style triangular matrix inversion, explicit a=1 and a=q alpha pairs, coefficientwise limiting transform, and match to the previously derived Jacobi product identities provide a proof-bearing transfer mechanism from the Rogers-Ramanujan series to the residue-class pro
- Artifact existence: pass.
- Support file `docs/proof/bailey_matrix_transform.md`: supports claim; matched/checked triangular|matrix, Bailey, coefficientwise|formal, a=1|a=q.
- Support file `docs/lemmas/lemma_catalogue.md`: supports claim; matched/checked Bailey|triangular, Jacobi|triple|product.
- Support file `docs/validation.md`: supports claim; matched/checked Bailey, residual|zero|sanity.
- Support file `scripts/rr/bailey_matrix_probe.wls`: supports claim; matched/checked alpha|Alpha, residual|Residual.
- Support file `data/finite_experiments/bailey_alpha_solve.csv`: supports claim; matched/checked exists.
- Support file `data/finite_experiments/bailey_transform_residuals.csv`: supports claim; matched/checked residual.
- Support file `data/finite_experiments/bailey_limit_residuals.csv`: supports claim; matched/checked residual.
- Low/provisional follow-up: not applicable.
- Verify verdict: `supported`.

### `_orphan/worker-combined-finite-foundation`

- Ledger state: `validated` / `high`.
- Claim checked: Built the formal-power-series lemma catalogue, gap-two staircase interpretation, finite Rogers-Ramanujan coefficient harness, validation note, and heatmap. Coefficient checks are explicitly labeled experimental.
- Artifact existence: pass.
- Support file `docs/lemmas/lemma_catalogue.md`: supports claim; matched/checked Formal power series|Z\[\[q\]\], coefficientwise, truncation|stabilization, staircase.
- Support file `docs/validation.md`: supports claim; matched/checked computational|experiment, not proof|not treated as proof|discovery.
- Support file `scripts/rr/finite_rr_experiments.wls`: supports claim; matched/checked KMax|KMAX, RR1|Rogers, negative|NC|control.
- Support file `data/finite_experiments/rr_recurrence_candidates.csv`: supports claim; matched/checked none_through_KMax|residual, first_nonzero.
- Support file `data/finite_experiments/rr_coefficients.csv`: supports claim; matched/checked exists.
- Support file `data/finite_experiments/rr_difference_heatmap.png`: supports claim; matched/checked exists.
- Low/provisional follow-up: not applicable.
- Verify verdict: `supported`.

### `_orphan/worker-repro-test-k12`

- Ledger state: `validated` / `high`.
- Claim checked: Reproducibility test for the finite Rogers-Ramanujan harness using KMax=12.
- Artifact existence: pass.
- Support file `data/finite_experiments/test_k12/rr_recurrence_candidates.csv`: supports claim; matched/checked none_through_KMax|first_nonzero.
- Support file `data/finite_experiments/test_k12/rr_coefficients.csv`: supports claim; matched/checked exists.
- Support file `data/finite_experiments/test_k12/rr_differences.csv`: supports claim; matched/checked exists.
- Low/provisional follow-up: not applicable.
- Verify verdict: `supported`.

### `_run/start`

- Ledger state: `in-progress` / `high`.
- Claim checked: # Long-Exposure Prompt: Derive the Rogers-Ramanujan Identities from First Principles
- Artifact existence: pass.
- Low/provisional follow-up: not applicable.
- Verify verdict: `supported`.

## Findings Appended

- Count: 0.
- CRITICAL: 0.
- MODERATE: 0.
- MINOR: 0.

## Residual Notes

- `_run/start` remains `in-progress` and is not treated as a failed proof milestone in this pass; it should be represented as residual run-state debt in the document stage if still present.
- No file-gate or evidence-support defect was found for M0, M1, M2, or the scoped supporting ledger-only records.

## Gate Evidence

- Evidence files exist and support claims: yes for all validated/scope records in this pass.
- Low/provisional-confidence events rechecked: yes; no current low/provisional terminal state exists in this slice.
- Findings appended to findings file: 0.
