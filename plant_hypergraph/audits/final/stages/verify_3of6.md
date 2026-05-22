# Final Audit Stage 4 - Verify 3/6

Assigned slice from `audits/final/explore.md`: M4, hierarchy-aware metric implementation and tests.

## Milestone Verdict

| Milestone | Ledger terminal status | Ledger confidence | Final-auditor verification |
|---|---:|---:|---|
| M4 | validated | high | Supported |

## Evidence Checked

Ledger events for M4 show:

- Researcher opened M4 in cycle 2 as metric-facing scaffolding tied to the synthetic benchmark.
- Worker validated M4 with artifacts:
  - `tools/hierarchy_metrics.py`
  - `tests/test_hierarchy_metrics.py`
  - `tests/test_synthetic_benchmark.py`
- Auditor validated M4 with the same artifact set and rationale covering flat match, synonym normalization, hierarchy distance, hierarchy coherence, missing-rank behavior, reticulate near-miss partial credit, `py_compile`, and unittest execution.

All listed artifacts exist on disk.

## Implementation Support

`tools/hierarchy_metrics.py` defines the following metric-facing functions:

- `normalize_label`
- `flat_exact_match`
- `synonym_normalized_exact_match`
- `hierarchy_distance`
- `mean_hierarchical_distance_error`
- `hierarchy_coherence_violation_rate`
- `reticulate_parent_map`
- `reticulate_near_miss_score`
- `mean_reticulate_near_miss_score`

The implementation covers the M4 success criteria:

- Metric beyond flat accuracy: `hierarchy_distance`, `mean_hierarchical_distance_error`, `hierarchy_coherence_violation_rate`, and reticulate near-miss scoring.
- Synonym normalization: `normalize_label` and `synonym_normalized_exact_match` collapse accepted names, synonyms, renamed labels, and verbatim labels where the names table maps them to an accepted taxon.
- Hierarchy-aware behavior: `hierarchy_distance` uses ancestor chains over the observed taxonomy parent map, distinguishing exact matches, wrong species in the same genus, wrong genus in the same family, missing-rank bridges, and distant errors.
- Hierarchy coherence: `hierarchy_coherence_violation_rate` checks whether predicted family/genus/species labels can coexist in the accepted hierarchy and exposes an `allow_missing_rank_bridge` control.
- Reticulate near-miss behavior: `reticulate_near_miss_score` gives full credit for exact targets and partial credit for documented `source_lineage` nodes from `reticulate_or_hybrid_signal` hyperedges.

## Test Results

Focused M4 tests:

```text
python3 -m unittest tests.test_hierarchy_metrics -v

Ran 5 tests in 0.002s
OK
```

The passing tests covered:

- synonym-normalized matching differs from flat exact matching;
- hierarchy distance distinguishes exact matches, same-genus near misses, and same-family near misses;
- missing-rank bridge behavior;
- hierarchy-coherence violation rate;
- reticulate near-miss scoring credits only documented source lineages.

Adjacent synthetic benchmark tests:

```text
python3 -m unittest tests.test_synthetic_benchmark -v

Ran 6 tests in 2.474s
OK
```

Those adjacent tests confirm the benchmark structures consumed by the metrics: required edge families, leakage groups, reticulate source-lineage structure, distant trait-convergence cases, negative-control toggles, and deterministic generation.

Compilation and direct smoke checks:

```text
py_compile: tools/hierarchy_metrics.py OK
py_compile: tests/test_hierarchy_metrics.py OK
Loaded frozen benchmark rows: taxa=76, names=138, edges=1081, examples=103
Synonym example: synonym-normalized exact match = 1.0
Strict-hierarchy exact example: hierarchy_distance = 0
Reticulate exact example: reticulate_near_miss_score = 1.0
Reticulate example source-lineage count = 2
```

An optional smoke script initially attempted to import helper names that are not part of `tools/hierarchy_metrics.py`. That was an audit-script mistake, corrected by using the actual public functions listed above. It is not a finding against the artifact.

## Findings

No CRITICAL findings.

No MODERATE findings.

No MINOR findings.

No entries appended to `audits/final/findings.jsonl`.

## Support Judgment

M4's `validated/high` status is supported. The repository implements hierarchy-aware metrics beyond flat accuracy, including synonym normalization, hierarchy distance, coherence checking, missing-rank behavior, and reticulate near-miss scoring. The focused tests and direct checks support the claimed metric behavior, and the adjacent benchmark tests verify the relevant frozen structures used by those metrics.
