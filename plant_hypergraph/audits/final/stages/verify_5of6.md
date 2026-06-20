# Final Audit Stage 6 - Verify 5/6

Assigned slice: M6, baseline and hypergraph experiments with ablations.

## Milestone Under Review

| Milestone | Ledger terminal status | Ledger confidence | Stage verdict-pending flag | Verify result |
|---|---:|---:|---:|---|
| M6 | validated | high | no | validated/high supported |

M6 claims a falsification-oriented baseline and hypergraph experiment suite over the validated synthetic benchmark, with tree/DAG, ordinary graph, flat/frequency/depth, clique expansion, native hypergraph variants, hierarchy-aware metrics, ablations, a strict negative control, and public-sample plumbing checks.

## Evidence Checked

Ledger events for M6 show the expected chain:

- Cycle 3 opened narrow M6 preparatory scaffolding for public-source evidence transformation checks.
- Cycle 4 opened the full M6 baseline and hypergraph experiment suite.
- Worker marked M6 `validated/high` with runner, outputs, determinism, and unittest evidence.
- Auditor marked M6 `validated/high` after verifying baseline families, metrics, case-type outputs, strict negative control, public-sample plumbing, figures, determinism, unittest validation, and the corrected collapsed-to-clique ablation.

Required code, test, report, and result artifacts exist:

- `tools/baselines.py`
- `scripts/run_synthetic_experiments.py`
- `tests/test_baselines.py`
- `docs/m6_experiment_report.md`
- `data/experiments/synthetic_v0.1/results.csv`
- `data/experiments/synthetic_v0.1/predictions.csv`
- `data/experiments/synthetic_v0.1/ablation_results.csv`
- `data/experiments/synthetic_v0.1/case_type_breakdown.csv`
- `data/experiments/synthetic_v0.1/clique_false_similarity.csv`
- `data/experiments/synthetic_v0.1/strict_negative_control.csv`
- `data/experiments/synthetic_v0.1/summary.json`
- `data/experiments/synthetic_v0.1/metric_comparison.png`
- `data/experiments/synthetic_v0.1/ablation_heatmap.png`
- `data/experiments/synthetic_v0.1/case_type_breakdown.png`
- `data/experiments/synthetic_v0.1/clique_false_similarity.png`

The result set supports the reported scope:

- `results.csv`: 63 rows across seven model families and ablation states.
- Model families present: `label_frequency`, `taxonomy_depth`, `flat_lookup_or_centroid`, `tree_dag`, `ordinary_graph`, `clique_expansion`, `native_hypergraph`.
- Test split size for aggregate results: 22.
- Aggregate no-ablation result: tree/DAG, ordinary graph, clique expansion, and native hypergraph tie at `0.409091` flat and synonym-normalized exact match.
- Native hypergraph has the best no-ablation mean hierarchy distance in the aggregate table: `1.772727`, compared with tree/DAG `2.181818`, ordinary graph `2.181818`, and clique expansion `2.090909`.
- `case_type_breakdown.csv`: 42 rows with strict hierarchy, synonym/rename, missing-rank, reticulate, trait-convergence, and noisy-occurrence case categories. The report correctly notes zero held-out test cases for noisy-occurrence and trait-convergence in this split.
- `ablation_results.csv`: 63 rows. Ablations include `remove_synonym`, `remove_trait`, `randomize_trait`, `remove_occurrence_geography_context`, `remove_reticulate`, `remove_missing_rank_bridge`, `collapse_to_clique_expansion`, and `randomize_accepted_names`.
- `strict_negative_control.csv`: 7 rows. Tree/DAG and native hypergraph both have mean hierarchy distance `0.571429`, supporting the stated strict-control result.
- `clique_false_similarity.csv`: 33 rows, including regional checklist context, reticulate/hybrid signal, and trait syndrome hyperedges that become pairwise similarities under clique expansion.
- `summary.json`: records seed `20260517`, benchmark path, file hashes, result row counts, public sample check, strict negative control counts, and key findings.

The public-data-backed sample is used only as source-evidence plumbing, not as a biological prediction benchmark. `summary.json` records a public-sample check with 327 nonsynthetic hyperedge rows and edge families `regional_checklist_context`, `synonym_cluster`, and `taxonomic_parentage`.

An initial audit rerun used stale CLI flags (`--dataset` and `--output-dir`) and failed argument parsing. The documented command uses `--benchmark-dir`, `--public-sample-dir`, and `--out-dir`; rerunning with those flags succeeded. This was an audit-command error, not a M6 finding.

## Tests Run

Compilation:

```text
python3 -m py_compile tools/baselines.py scripts/run_synthetic_experiments.py tests/test_baselines.py
```

Observed result: passed.

Focused unittest:

```text
python3 -m unittest tests.test_baselines -v
```

Observed result:

```text
Ran 8 tests in 34.011s
OK
```

Covered test cases:

- model information budgets are constrained;
- synonym mappings are hidden from tree prediction;
- clique expansion introduces extra pairwise relationships;
- native hypergraph preserves reticulate roles;
- public sample parses as nonsynthetic plumbing;
- strict negative control does not disadvantage tree;
- runner outputs are hash stable;
- collapse ablation scores native hypergraph as clique expansion.

Experiment rerun:

```text
python3 scripts/run_synthetic_experiments.py --benchmark-dir data/synthetic_benchmark/v0.1 --public-sample-dir data/public_taxonomy_sample/v0.1 --out-dir /tmp/m6_experiment_check.* --seed 20260517 --ablation all
```

Observed result: exited successfully and produced the expected CSV, JSON, and PNG output files. The rerun summary matched the checked row counts and key findings, including 63 result rows, 63 ablation rows, 42 case-type rows, 33 clique false-similarity rows, and 7 strict-negative-control rows.

## Findings

No CRITICAL findings.

No MODERATE findings.

No MINOR findings.

## Stage Conclusion

M6 `validated/high` is supported. The milestone has runnable code, focused tests, reproducible experiment outputs, fair baseline families, hierarchy-aware metrics, ablations, a strict negative control, public-sample plumbing checks, figures, and a report that states negative and limited results without overstating biological claims.

Findings appended to `findings.jsonl`: 0.
