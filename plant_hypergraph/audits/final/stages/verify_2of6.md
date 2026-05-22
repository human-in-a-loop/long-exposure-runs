# Final Audit Stage 3 - Verify 2/6

Assigned slice from `audits/final/explore.md`: M3, synthetic reticulate taxonomy benchmark generator.

## Milestone Verdict

| Milestone | Ledger terminal status | Ledger confidence | Final-auditor verification |
|---|---:|---:|---|
| M3 | validated | high | Supported |

## Evidence Checked

Ledger events for M3 show:

- Researcher opened M3 in cycle 2 as an in-progress synthetic benchmark generator task.
- Worker validated M3 with artifacts:
  - `scripts/generate_synthetic_benchmark.py`
  - `data/synthetic_benchmark/v0.1/taxa.csv`
  - `data/synthetic_benchmark/v0.1/names.csv`
  - `data/synthetic_benchmark/v0.1/hyperedges.csv`
  - `data/synthetic_benchmark/v0.1/examples.csv`
  - `data/synthetic_benchmark/v0.1/splits.csv`
  - `data/synthetic_benchmark/v0.1/metadata.json`
  - `data/synthetic_benchmark/v0.1/composition.png`
  - `docs/synthetic_benchmark_design.md`
- Auditor validated M3 with the same artifact set and explicit rationale covering deterministic generation, required benchmark files, required hyperedge families, role-labeled incidence rows, orphan-incidence checks, split leakage grouping, negative-control toggles, composition figure presence, metadata hashes, and synthetic-status documentation.

All listed artifacts exist on disk.

## Artifact Support

The design document explicitly identifies the benchmark as deterministic and fully synthetic. It states that the benchmark does not assert real plant trait syndromes, ranges, missing ranks, hybrid origins, or taxonomic changes.

The frozen default dataset under `data/synthetic_benchmark/v0.1/` contains:

- `taxa.csv`: 76 rows, with family, genus, and species ranks.
- `names.csv`: 138 rows, with `accepted`, `synonym`, `renamed_label`, and `noisy_verbatim` name statuses.
- `hyperedges.csv`: 1081 incidence rows, with all required edge families:
  - `taxonomic_parentage`
  - `synonym_cluster`
  - `trait_syndrome`
  - `regional_checklist_context`
  - `occurrence_provenance`
  - `reticulate_or_hybrid_signal`
  - `missing_rank_bridge`
- `examples.csv`: 103 labeled examples, covering `strict_hierarchy`, `synonym_or_rename`, `missing_rank`, `trait_convergence`, `noisy_occurrence`, and `reticulate` case types.
- `splits.csv`: 60 leakage groups with train/validation/test assignments.
- `metadata.json`: seed `20260517`, file hashes, schema version, parameter values, counts, required edge-family list, and synthetic-status disclaimer.
- `composition.png`: present and referenced by the design document.

Observed case counts:

| Case type | Examples |
|---|---:|
| strict_hierarchy | 23 |
| synonym_or_rename | 54 |
| missing_rank | 10 |
| trait_convergence | 4 |
| noisy_occurrence | 4 |
| reticulate | 8 |

Observed edge-family incidence counts:

| Edge family | Incidence rows |
|---|---:|
| taxonomic_parentage | 288 |
| synonym_cluster | 290 |
| trait_syndrome | 88 |
| regional_checklist_context | 28 |
| occurrence_provenance | 300 |
| reticulate_or_hybrid_signal | 35 |
| missing_rank_bridge | 52 |

The seven reticulate hyperedges each have two `source_lineage` roles, supporting the claim that reticulate/hybrid-like cases preserve multi-source structure rather than forcing a single-parent tree encoding.

## Leakage And Control Checks

No leakage group was assigned to more than one split in the examples table. The split table contains 60 accepted-taxon leakage groups, and the examples table uses 56 of those groups.

Focused test execution:

```text
python3 -m unittest tests.test_synthetic_benchmark -v

Ran 6 tests in 2.260s
OK
```

The passing tests covered:

- hash-stable generation for the same seed;
- required columns and required edge families;
- no orphan incidence rows;
- split leakage groups are not cross-split;
- reticulate edges have at least two source lineages and convergence cases are taxonomically distant;
- negative-control toggles remove reticulate, missing-rank, trait-convergence, and synonym/rename mechanisms.

Additional deterministic regeneration check:

- Ran `scripts/generate_synthetic_benchmark.py --seed 20260517` twice into separate temporary directories.
- Both runs exited with code 0.
- Generated file digests matched across all generated files: `composition.png`, `examples.csv`, `hyperedges.csv`, `metadata.json`, `names.csv`, `splits.csv`, and `taxa.csv`.

`python3 -m pytest tests/test_synthetic_benchmark.py -q` could not run because `pytest` is not installed in the active Python environment. This is not recorded as a milestone finding because the test file is unittest-compatible and the equivalent direct unittest execution passed.

## Findings

No CRITICAL findings.

No MODERATE findings.

No MINOR findings.

No entries appended to `audits/final/findings.jsonl`.

## Support Judgment

M3's `validated/high` status is supported. The repository contains a deterministic generator, frozen synthetic benchmark artifacts, metadata and hashes, explicit synthetic-status caveats, required reticulate, synonym/rename, missing-rank, trait-convergence, noisy-occurrence, and strict-hierarchy cases, leakage-safe splits, negative-control behavior, and focused tests that exercise those claims.
