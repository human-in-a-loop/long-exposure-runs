---
created: 2026-05-18T03:20:00+00:00
cycle: 9
run_id: fork-aaf42b4ab956-clone-3-track5-chemodiversity
agent: worker-clone-3
milestone: M3.T5
---

# Track 5 — Chemodiversity Neighborhood-Completion Predictor

## Scope

This branch builds the first Track 5 predictive instrument over the frozen
Barrier 2 chemodiversity enrichment layer. It emits track-local pending
predictions only. It does not write to `prediction_ledger.tsv`, does not change
`phytograph_dataset/`, does not re-normalize synonyms, and does not assert any
new detection, bioactivity, safety, or clinical-efficacy claim as established
fact.

The required output for this clone is this report:
`tracks/track5/reports/track5_chemodiversity.md`.

## Inputs

| Artifact | Role |
|---|---|
| `tracks/track5/data/track5_enrichment_edges.parquet` | 23,524 retained taxon-keyed phytochemical + ethnobotanical enrichment rows. |
| `tracks/track5/data/track5_compound_class_membership.parquet` | 9,500 Duke compound-to-class rows used as class membership view. |
| `tracks/track5/data/track5_bioactivity_assertions.parquet` | 28,733 compound-keyed bioactivity rows; intentionally no `accepted_taxon_key`. |
| `tracks/track5/data/track5_taxon_to_family.parquet` | Accepted-key to family lookup derived before this instrument cycle. |
| `tracks/track5/data/per_taxon_screening_intensity.tsv` | Per-taxon screening load used to prioritize under-screened taxa. |
| `tracks/track5/data/source_density_diagnostics.tsv` | Source dominance audit, foregrounding Dr. Duke coverage. |
| `tracks/track5/data/canonical_phyto_held_out.tsv` | Future validation seed list; not used for supervised training in this cycle. |

## Mechanism

For taxon `t`, family `f`, and compound class `k`, the score is:

```text
score(t, k | f) = S_f[k] * w_specificity(k) * w_screening(t)
S_f[k] = taxa in family f with >=1 retained compound in class k / screened taxa in f
w_specificity(k) = -log p(k | global Track 5 compound-class rows)
w_screening(t) = 1 / (1 + n_compounds_detected_in_t)
```

The instrument therefore ranks under-screened taxa inside families whose
resolved Track 5 evidence already shows a compound-class neighborhood. This is
a neighborhood-completion prior, not evidence that the predicted taxon has been
screened or that a compound is clinically useful.

Special-point checks:

| Point | Result |
|---|---|
| Zero retained phytochemical rows after a source ablation | Emits an empty prediction table with stable columns instead of crashing. |
| Blank accepted taxon key | Excluded upstream by Barrier 2 Track 5 conformance. |
| Family with fewer than 3 screened taxa | Marked `data-limited:few_taxa`; no predictions emitted. |
| Family with fewer than 2 compound classes | Marked `data-limited:few_classes`; no predictions emitted. |
| Compound bioactivity without compound indirection | No taxon-level bioactivity claim emitted. |
| Clinical efficacy | Explicitly out of scope in every prediction row. |

## Outputs

| Artifact | Rows | Meaning |
|---|---:|---|
| `tracks/track5/data/phytochemistry_predictions.tsv` | 1,405 | Pending candidate taxon × compound-class predictions. |
| `tracks/track5/data/phytochemistry_signatures.parquet` | 580 | Family × compound-class signatures plus data-limited status rows. |
| `tracks/track5/data/phytochemistry_speculation.tsv` | 37 | Data-limited family rows with no validation source; not predictions. |
| `tracks/track5/data/phytochemistry_no_duke_predictions.tsv` | 0 | Duke-drop LOSO output; confirms no current non-Duke predictive coverage. |
| `tracks/track5/data/phytochemistry_no_duke_signatures.parquet` | 0 | Empty signature table after Duke removal. |
| `tracks/track5/data/phytochemistry_no_duke_speculation.tsv` | 0 | Empty speculation table after Duke removal. |

Prediction summary:

| Measure | Value |
|---|---:|
| Prediction rows | 1,405 |
| Families with predictions | 13 |
| Predicted compound classes | 54 |
| Rows with compound-indirected bioactivity-class annotation | 735 |
| Data-limited families withheld from prediction | 37 |
| Rows sensitive to Dr. Duke ablation | 1,405 / 1,405 |
| Predictions after dropping Dr. Duke | 0 |

Top prediction-bearing families:

| Family | Rows |
|---|---:|
| Apiaceae | 215 |
| Amaryllidaceae | 210 |
| Poaceae | 150 |
| Malvaceae | 120 |
| Rutaceae | 120 |
| Ranunculaceae | 110 |
| Lamiaceae | 110 |
| Berberidaceae | 95 |

Top predicted compound classes:

| Compound class | Rows |
|---|---:|
| Carbohydrate | 65 |
| Inorganic | 65 |
| Lipid | 65 |
| Proteid | 65 |
| Carotenoid | 55 |
| Benzenoid | 55 |
| Flavonoid | 55 |
| Vitamin | 55 |

Score distribution:

| Statistic | Score |
|---|---:|
| min | 0.129590 |
| median | 1.240891 |
| mean | 1.390382 |
| max | 5.271049 |

## Evidence Firewall

The predictor preserves three separate layers:

1. **Phytochemical detection.** A source detected or reported a compound in a
   taxon. This does not imply typical concentration or bioactivity.
2. **Compound-level bioactivity.** A compound has a source-recorded activity
   label. The bioactivity table is compound-keyed and has no taxon key.
3. **Clinical efficacy and safety.** Not inferable from this track. No output
   row supports clinical efficacy, preparation safety, dosage, or medical use.

Rows in `phytochemistry_predictions.tsv` predict only a candidate compound
class for future screening. The optional
`predicted_bioactivity_via_compound_indirection` field is populated only when a
compound-class member maps through the compound-keyed bioactivity table. It is
therefore a weak prioritization annotation, not a taxon-level bioactivity claim.

## Dr. Duke Dominance Sensitivity

The instrument is source-dominated. Barrier 2 already measured Dr. Duke at
0.999598 of combined Track 5 enrichment plus bioactivity signal. This branch
propagates that fact into every prediction row:

- `duke_share_in_family` is at least 0.5 for all prediction-bearing families.
- `ablation_sensitivity` names Dr. Duke for every prediction row.
- Running the same predictor with `--loso-drop-source-class "Dr. Duke"` emits
  zero predictions.

Interpretation: the current M3.T5 output is a useful, auditable pending prior
for where to screen next, but it is not yet evidence of a robust multi-source
biological signal. Wave 4 must treat Duke removal, source-density matching, and
screening-intensity controls as decisive falsification probes.

## Validation Readiness

Each prediction row carries an expected validation path:

```text
Targeted phytochemical screen of taxon; KNApSAcK/NPASS/ChEBI side-wave ingest
for cross-source confirmation; ethnobotanical-use cross-check (NAEB expansion).
```

The canonical held-out discoveries file is present but not yet sufficient for
the Track 5 headline validation target because the current Barrier 2 resolved
coverage is Duke-dominated and lacks the temporal freezes needed to ask whether
Taxus, Catharanthus, Cinchona, Artemisia, and related cases would have ranked
high before discovery. This branch therefore files pending predictions and
data-limited speculation rows only.

## Reproducibility

Commands run:

```bash
python3 tracks/track5/scripts/track5_predictor.py
python3 tracks/track5/scripts/track5_predictor.py --loso-drop-source-class 'Dr. Duke' --out-prefix phytochemistry_no_duke
python3 tracks/track5/tools/validate_track5_enrichment.py
python3 -m pytest -q tracks/track5/tests/test_track5_enrichment.py tracks/track5/tests/test_track5_predictor.py
python3 tools/validate_barrier2_track_enrichment.py
python3 tools/validate_barrier1_substrate.py
python3 -m long_exposure.tools.promise_check <run-root>
python3 -m long_exposure.tools.org_check <run-root>
```

## Open Issues

- Non-Duke coverage is too sparse for robust chemodiversity inference.
- The compound-class view is Duke-derived; ChEBI/NPASS/KNApSAcK class
  harmonization remains a source-recovery task.
- The temporal validation target for canonical discoveries is not implemented
  in this branch.
- No prediction is validated; all candidate rows remain `pending`.

## Wave 4 Validation Update

`tracks/track5/reports/track5_temporal_validation.md` now records the first
M4.V5 / Track 5 source-ablation pass. The result changes the interpretation
from "pending but source-dominated" to "pending and currently not temporally
validated": all canonical holdout cases are data-limited under frozen source
coverage, no holdout reaches top-decile recovery, and no-Duke/source-matched
variants emit zero prediction rows.
