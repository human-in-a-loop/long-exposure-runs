---
created: 2026-05-18T21:10:00+00:00
run_id: fork-5fe97ebd91d9-clone-2
agent: codex
milestone: M4.V5 / Track 5 free-tier non-Duke temporal chemistry recovery
---

# Track 5 Free-Tier Non-Duke Temporal Chemistry Recovery

## Decision

determination: `insufficient_non_duke_temporal_evidence_h5_remains_source_biased`.

This clone varied the evidence-acquisition axis: instead of inspecting only the frozen local chemistry staging tables, it performed a bounded free/open literature-source pass for canonical medicinal taxa and adjacent taxa. The pass found historical non-Duke literature statements for several canonical discoveries, but only two candidate species-level rows also have a frozen WFO accepted key visible in the current substrate lookup: `Artemisia annua` -> artemisinin and `Atropa bella-donna` / canonical `Atropa belladonna` -> atropine. That does not meet the Track 5 validation predicate because the current instrument needs a structured non-Duke family/class stratum sufficient to estimate `S_f[k]`, not isolated retrospective literature facts.

The conclusion from the validated reopen package is therefore unchanged at the campaign level: H5 is not validated, the M3.T5 predictor should not be rerun, and no master `prediction_ledger.tsv` or `speculation_ledger.tsv` row is licensed by this branch.

## Acceptance Predicate

A row is qualifying validation evidence only if all conditions hold:

| Predicate | Required value |
|---|---|
| Source class | non-Duke, free/open/local-accessible source |
| Evidence scope | true taxon-compound detection or isolation, not ethnobotanical-use-only and not bioactivity-only |
| Taxon key | accepted key in the frozen PhytoGraph/WFO substrate namespace |
| Temporal field | usable discovery/isolation/publication year |
| Holdout visibility | pre-target rows may train; target-label rows must remain hidden for temporal holdout scoring |
| Instrument usefulness | enough rows to populate a family/class signature, not only one-off narrative confirmations |

Mechanism: the Track 5 score is `score(t,k|f)=S_f[k]*w_specificity(k)*w_screening(t)`. If non-Duke rows do not populate `S_f[k]` at family/class scale, then source-independent neighborhood-completion cannot be distinguished from screening/source density.

## Free/Open Source Search Results

| Taxon or adjacent taxon | Compound/class | Year basis | Open source inspected | Accepted-key status in frozen substrate | Predicate result | Reason |
|---|---|---:|---|---|---|---|
| `Taxus brevifolia` | paclitaxel/taxol, diterpene | 1971 | JACS isolation/structure record [68] | no frozen accepted key for `Taxus brevifolia` or `Taxus` found in local accepted-taxa lookup | rejected | true historical detection, but no accepted-key join in this workspace |
| `Catharanthus roseus` / `Vinca rosea` | reserpine and vinca alkaloid context | 1958 | Nature `Vinca rosea` isolation record [71] plus modern source context from prior searches | genus `Catharanthus` has a frozen accepted key; species `Catharanthus roseus` does not | rejected for H5 holdout | species-level target lacks accepted-key join; source is not the vincristine target-label row |
| `Cinchona officinalis` / `Cinchona` spp. | quinine, alkaloid | 1820 | JAMA historical account [72] and Science Museum collection record [73] | genus `Cinchona` has a frozen accepted key; `Cinchona officinalis` does not | rejected for H5 holdout | historical source is genus/bark-level and probably not the held-out species |
| `Artemisia annua` | artemisinin/qinghaosu, sesquiterpene lactone | 1972/1977/1984 | PubMed-indexed review and JNP isolation record [69], [70] | species key present: `wfo:wfo-0000083255-2025-12` | candidate accepted-key detection | true detection candidate, but one species/class row cannot supply a non-Duke family/class training stratum |
| `Digitalis purpurea` / `Digitalis lanata` | digoxin/digitalis, cardenolide | contested for target | BMJ correction that digoxin source is `Digitalis lanata`, not `D. purpurea` [76] | genus `Digitalis` has a frozen accepted key; `Digitalis purpurea` does not | rejected | canonical heldout appears taxonomically/source mismatched for digoxin; should be treated as target-design risk |
| `Papaver somniferum` | morphine, alkaloid | 1804/1806 | ACS review of morphine history [74] | genus `Papaver` has a frozen accepted key; species `Papaver somniferum` does not | rejected | true historical detection, but no species accepted-key join |
| `Atropa belladonna` / `Atropa bella-donna` | atropine, tropane alkaloid | 1831 | BMJ `Atropa belladonna` historical note [75] | orthographic accepted species key present as `Atropa bella-donna`: `wfo:wfo-0001019409-2025-12` | candidate accepted-key detection | true detection candidate, but orthographic normalization is not represented in the existing holdout matrix and one species/class row is insufficient |
| `Salix alba` | salicin, glycoside | 1828 | willow/salicin source trail, including Royal Society willow-bark antecedent [77] | `Salix` genus and other species/forms present; `Salix alba` not found in frozen accepted-taxa lookup | rejected | source trail supports willow chemistry history, but current species target lacks accepted-key join |

## Candidate Rows That Could Be Staged Later

These rows are not promoted to the master ledgers. They are a minimal future-data recipe for a structured non-Duke temporal intake.

| accepted_key | accepted_name | canonical_label | compound | class | year | date_basis | evidence_scope | source |
|---|---|---|---|---|---:|---|---|---|
| `wfo:wfo-0000083255-2025-12` | `Artemisia annua` | `Artemisia annua` | artemisinin/qinghaosu | Sesquiterpene | 1972/1977/1984 | isolation/structure publication trail | taxon-compound detection/isolation only | [69], [70] |
| `wfo:wfo-0001019409-2025-12` | `Atropa bella-donna` | `Atropa belladonna` | atropine | Alkaloid | 1831 | isolation-history note | taxon-compound detection/isolation only | [75] |

These rows would still be `candidate_manual_recovery`, not validation rows, until a reproducible intake script captures source identifiers, license/access metadata, plant part where available, and temporal-label hiding rules.

## Why H5 Still Does Not Reopen

1. The direct search weakens the literal statement "no open non-Duke historical detections exist," but does not satisfy the actual validation mechanism. Two manual candidates do not define a source-independent family/class signature.
2. The no-Duke ablation remains the decisive instrument test: prior Track 5 outputs report 1,405 baseline prediction rows and 0 rows under `no_duke`, `source_density_matched`, and `screening_count_matched`.
3. Most canonical taxa still fail the frozen accepted-key species join. Genus-level hits are not enough for a held-out source-taxon recovery claim.
4. Several open sources are retrospective summaries rather than structured detection databases. They can guide future curation, but they do not create a bulk validation stratum.
5. The `Digitalis purpurea` heldout is likely mis-specified for digoxin because an open BMJ correction identifies `Digitalis lanata` as the source. That is a benchmark-design issue, not positive H5 evidence.

## Evidence Firewall

This report asserts only historical detection/isolation-source availability and workspace join status. It does not assert clinical efficacy, dose, preparation, safety, medicinal recommendation, taxonomic novelty, or new phytochemical novelty. Ethnobotanical-use-only rows and bioactivity-only rows remain excluded.

## Reproducibility Notes

Local accepted-key inspection used `substrate/staging/taxonomy_backbone/accepted_taxa.csv` and exact/string-contains checks for the canonical genera/species. Prior local Track 5 evidence state was cross-checked against:

- `tracks/track5/data/non_duke_temporal_taxon_compound_evidence.tsv`
- `tracks/track5/data/track5_reopen_temporal_holdout_matrix.tsv`
- `tracks/track5/data/track5_reopen_source_diagnostics.tsv`
- `tracks/track5/reports/track5_reopen_temporal_chemistry_evidence.md`
- `tracks/track5/reports/track5_wave4_temporal_source_closure.md`

## Next Data Predicate

Only reopen Track 5 if a structured non-Duke intake adds accepted-key, dated taxon-compound detection rows across enough families/classes to estimate `S_f[k]` and to run temporal label hiding without target leakage. A minimal credible threshold would be at least the two candidate rows above plus additional accepted-key rows in Apocynaceae, Rubiaceae, Taxaceae, Papaveraceae, Salicaceae, and Plantaginaceae/`Digitalis lanata`, each with source identifiers and date bases.
