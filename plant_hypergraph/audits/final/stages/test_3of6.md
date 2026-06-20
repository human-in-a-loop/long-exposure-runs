# Final Auditor Stage 10 - Test 3/6

## Scope

Adversarial consistency pass on final-document claims against the M6 experiment outputs and M7 formal diagnostic outputs. This pass focused on whether the public-facing synthesis overstated native hypergraph advantage, contradicted the numeric artifacts, or weakened the limitation language around synthetic evidence and unsupported biological claims.

## Validators

- `python3 -m long_exposure.tools.promise_check <run-root>`: exit 0.
- `python3 -m long_exposure.tools.org_check <run-root>`: exit 0.

`promise_check` still reports the known noncanonical raw-directory artifact warnings for the M5 raw WFO/GBIF/Open Tree directories and missing process-scope manager assessment artifacts under `long-exposure/manager_assessments/...`. These do not contradict the planned M1-M8 milestone evidence checked in prior passes.

`org_check` still reports root-level final deliverables and run prompt/log/score files outside its preferred allow-list. The root final deliverables are required M8 artifacts by the plan of record and were already verified as present.

## Source Numeric Anchors Checked

From `data/experiments/synthetic_v0.1/results.csv`, no-ablation test split, `case_type=all`:

| Model | Flat exact | Synonym-normalized exact | Mean hierarchy distance | Reticulate near miss |
|---|---:|---:|---:|---:|
| `label_frequency` | 0.000000 | 0.000000 | 4.409091 | 0.000000 |
| `taxonomy_depth` | 0.000000 | 0.000000 | 3.500000 | 0.022727 |
| `flat_lookup_or_centroid` | 0.000000 | 0.000000 | 3.500000 | 0.022727 |
| `tree_dag` | 0.409091 | 0.409091 | 2.181818 | 0.409091 |
| `ordinary_graph` | 0.409091 | 0.409091 | 2.181818 | 0.409091 |
| `clique_expansion` | 0.409091 | 0.409091 | 2.090909 | 0.409091 |
| `native_hypergraph` | 0.409091 | 0.409091 | 1.772727 | 0.409091 |

From `data/experiments/synthetic_v0.1/ablation_results.csv`:

- `collapse_to_clique_expansion` for `native_hypergraph` keeps flat and synonym-normalized exact match at `0.409091`.
- The collapsed native mean hierarchy distance is `2.090909`.
- The hierarchy-distance delta versus native no-ablation is `+0.318182`.

From `data/experiments/synthetic_v0.1/strict_negative_control.csv`:

- `tree_dag`, `ordinary_graph`, `clique_expansion`, and `native_hypergraph` all have mean hierarchy distance `0.571429` and flat exact match `0.857143`.

From `data/experiments/synthetic_v0.1/case_type_breakdown.csv` for native no-ablation:

- Held-out test counts: `missing_rank=1`, `noisy_occurrence=0`, `reticulate=4`, `strict_hierarchy=5`, `synonym_or_rename=12`, `trait_convergence=0`.
- The zero held-out `noisy_occurrence` and `trait_convergence` counts are therefore necessary caveats.

From `data/formal_diagnostic/formal_diagnostic_summary.json`:

- `native_hypergraph_mean_hierarchy_distance`: `1.772727`.
- `clique_expansion_mean_hierarchy_distance`: `2.090909`.
- `collapsed_native_mean_hierarchy_distance`: `2.090909`.
- `collapse_to_clique_distance_delta`: `0.318182`.
- `finite_example_rows`: 8.
- `m6_family_rows`: 3.

## Final-Document Claim Checks

Documents checked:

- `final_report.md`
- `research_contribution_ledger.md`
- `audit_report.md`
- `docs/m6_experiment_report.md`
- `docs/formal_diagnostic.md`

Results:

- `final_report.md` contains the key numeric anchors `1.772727`, `2.090909`, `2.181818`, `0.409091`, `0.318182`, and `0.571429`.
- `docs/m6_experiment_report.md` contains the same M6 numeric anchors and explicitly reports the zero held-out noisy-occurrence and trait-convergence cases.
- `docs/formal_diagnostic.md` contains the M7 anchors tying the native hypergraph hierarchy-distance value to clique expansion and collapsed native hypergraph behavior.
- `research_contribution_ledger.md` does not repeat every numeric value, but its claims are qualitative and consistent with the source outputs: it states that broad hypergraph predictive superiority is not proved and that exact accuracy tied across structure-aware methods.
- `audit_report.md` repeats the scoped conclusion and key numeric caveats without introducing conflicting stronger claims.

Automated phrase probes found lines containing "superiority" and "outperform" only in negated or scoped statements, for example:

- `final_report.md`: "not broad predictive superiority."
- `final_report.md`: "Broad native-hypergraph predictive superiority is not supported."
- `research_contribution_ledger.md`: "Does not prove: that a native hypergraph will outperform graph or tree baselines on real data."

These are limitation statements, not overclaims.

The final report also includes the required guardrails: synthetic-only reticulate evidence, public-data-limited source use, unsupported biological claims avoided, no new plant taxonomy, no new species relationships, no documented hybrid origins, no trait-syndrome discovery, no range or occurrence-quality conclusions, and no phylogenetic novelty claims.

## Adversarial Verdict

No contradiction found between final-document claims and the M6/M7 artifacts.

The final synthesis accurately preserves the narrow result:

- Native hypergraph did not improve flat or synonym-normalized exact accuracy over tree/DAG, ordinary graph, or clique expansion.
- Native hypergraph did improve mean hierarchy distance on the synthetic no-ablation split.
- The strict tree-generated negative control does not show native hypergraph advantage.
- The clique-expansion diagnostic supports a semantic warning about pairwise expansion of multi-way/role-labeled evidence.
- Biological claims remain explicitly unsupported unless source-backed.

## Findings Appended

0

