---
created: 2026-05-18T14:45:00+00:00
cycle: 21
run_id: run-phytograph-cycle21-wave5-final-synthesis
agent: worker
milestone: M5.1
---

# Falsification And Ablation Report: PhytoGraph

## Summary Matrix

| Track | Hypothesis | Result | Control, ablation, or blocker | Master-ledger action |
|---|---|---|---|---|
| Track 1 | H1 | `sidecar_readiness_uncontrolled` | Free-tier sidecar retained 22 event taxa across 11 source groups, but WFO projection is only 2 taxa and source-density controls remain unresolved. | No master promotion. |
| Track 2 | H2 | `H2_remains_not_supported_or_data_limited` | Free-tier closure matrix has 8 canonical held-outs and 31 local candidates, but 0/8 canonical held-outs pass the validation contract. | No promotion. |
| Track 3 | H3 | `confound_limited` | Free-tier trait matrix has 3,069 accepted-key carrier rows across 15 canonical traits, but 0 controlled-ready traits; `drupe` and `capsule` remain local pending priors only. | No promotion. |
| Track 4 | H4 | `still_data_limited` | 3,358 post-filter occurrence records, 0 numeric BIOCLIM vectors, and 0 validation-allowed comparator rows. | No promotion. |
| Track 5 | H5 | `H5_remains_source_biased` | Non-Duke temporal evidence is insufficient and no validation-ready structured family/class stratum exists. | No promotion. |
| Track 6 | H6 | `environment_limited_untested` | 0 runnable local runtime-weight pairings, 0 executed responses, and 0 scored responses. | No promotion. |

## Track 1: Reticulation Atlas

The Track 1 closure refined the accepted-key failure mode but did not validate
H1. Current canonical accepted-key recovery is 0/8. A full-WFO sidecar recovers
5/8 names, including exact rows for `Triticum aestivum`, `Brassica napus`,
`Musa acuminata`, and `Musa balbisiana`, plus synonym-to-accepted recovery for
`Spartina anglica`.

The stricter event-shaped evidence remains insufficient: 3/8 with synonym
rescue and 2/8 with exact accepted-taxon rows only. This blocks the claim that
the frozen instrument recovers canonical reticulation lineages without
supervision.

The final free-tier sidecar result is `sidecar_readiness_uncontrolled`: 22 GBIF
sidecar event taxa across 11 source groups are retained, but WFO projection is 2
taxa and source-density controls remain unresolved.

## Track 2: Ghost Hyperedges

H2 is not supported at the 30 percent canonical recovery threshold under
accepted-key, modern-failure, singleton-source, source-class, and
living-megafauna controls. The integrated outcome is 0 validated cases, 1
falsified under ablation, 6 data-limited cases, and 1 insufficient-support case.

This is a null validation result, not a weak positive. Track-local candidate
rows remain useful for diagnosing missing evidence, but they do not become
master predictions.

The free-tier closure pass refines the same boundary: 8 canonical held-outs and
31 local candidates are retained, but 0/8 canonical held-outs pass the
validation contract because independent modern-failure evidence and
non-singleton/source-class support remain absent.

## Track 3: Convergence Pressure

H3 remains confound-limited. The Track 3 branch records convergence/confound
diagnostics over 3,069 accepted-key trait carrier rows and 15 canonical traits,
but 0 traits are controlled-ready. `drupe` and `capsule` are local pending
convergence-prior rows, not validated convergence predictions. The current
evidence does not license a claim that the convergence statistic beats
family-size or sampling-density baselines.

## Track 4: Domestication Hypergraph

H4 remains data-limited. The closure package records 3/69 joined CWR pairs,
2/22 held-out accepted-key rows, 36/375 accepted-key climate rows, and 0
observed bioclim vectors. All three candidate rows remain
`pending_data_limited` and `validation_ready=False`.

The final free-tier status is `still_data_limited`: 3,358 post-filter
occurrence records exist, but numeric BIOCLIM vectors and validation-allowed
comparator rows are both 0. Climate substitution is not computable, and no
recommendation-like claim is promoted.

## Track 5: Chemodiversity Predictor

H5 is not validated under frozen temporal inputs. The eight temporal holdouts
all have `top_decile=False`, and all carry `cutoff_status` indicating no
assertion dates were available. The source ablation is decisive: the full
baseline has 1,405 prediction rows, the no-Duke ablation has 0 rows, and
Duke-downweighted remains non-independent because Duke still supplies family
signals.

The result is a source-bias null finding: current Track 5 measures a
Duke-backed screening prior, not source-independent chemodiversity
neighborhood completion.

The final free-tier status is `H5_remains_source_biased`: non-Duke temporal
evidence is insufficient and there is no validation-ready structured
family/class stratum.

## Track 6: Foundation Model Probe

H6 is environment-limited and untested. The static benchmark, deterministic
rubric, and scorer controls exist, but local model availability is false:
`transformers=false`, `torch=false`, `llama_cpp=false`, and local model files
are empty.

The deterministic scorer controls are infrastructure checks. They do not
support model error rates, leaderboard claims, toxicity-look-alike policy
claims, or vendor/model-family comparisons.

The final free-tier status is `environment_limited_untested`: 0 runnable local
runtime-weight pairings, 0 executed responses, and 0 scored responses.

## Cross-Track Ledger Decision

No cross-track result currently satisfies the master prediction-ledger contract:
a validation source, a claim statement, supporting hyperedges/node set, and an
ablation/control result that does not collapse the claim. The master
`prediction_ledger.tsv` and `speculation_ledger.tsv` therefore remain
header-only.

## Post-Reopen Closure Addendum

The post-reopen closure package in `reports/reopen/reopen_closure_addendum.md`
and the free-tier integration in `reports/reopen/free_tier_recovery_integration.md`
reconcile the validated reopen attempts and free-tier branch outputs, including
fork `2f05eabe3800` for Tracks 2 and 3. The branch outcome table is
`data/reopen/reopen_closure_status.tsv`, and the figure is
`reports/reopen/figures/reopen_branch_outcomes.png`.

The final free-tier closure synthesis is
`reports/reopen/final_free_tier_closure_synthesis.md`, with canonical rows in
`data/reopen/final_free_tier_track_status.tsv` and the figure
`reports/reopen/figures/final_free_tier_track_status.png`. Track 1 is
`sidecar_readiness_uncontrolled`: the sidecar retained 22 GBIF event taxa
across 11 source groups, but WFO projection is 2 taxa and source-density
controls remain unresolved. Track 2 is
`H2_remains_not_supported_or_data_limited` with 0/8 canonical held-outs passing
the validation contract. Track 3 is `confound_limited` with 0 controlled-ready
traits across 3,069 accepted-key trait carrier rows. Track 4 is
`still_data_limited`: coordinates exist, but numeric BIOCLIM vectors and
validation-allowed comparator rows are both 0. Track 5 is
`H5_remains_source_biased`: non-Duke temporal evidence is insufficient and no
validation-ready structured family/class stratum exists. Track 6 is
`environment_limited_untested` with 0 runnable runtime-weight pairings, 0
executed responses, and 0 scored responses.
