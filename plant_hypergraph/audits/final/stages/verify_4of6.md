# Final Audit Stage 5 - Verify 4/6

Assigned slice: M5, minimal public-data-backed name/synonym/taxonomy sample.

## Milestone Under Review

| Milestone | Ledger terminal status | Ledger confidence | Stage verdict-pending flag | Verify result |
|---|---:|---:|---:|---|
| M5 | validated | high | no | validated/high supported |

M5 claims a small no-auth WFO/GBIF/Open Tree sample with frozen raw responses, normalized source-specific tables, metadata hashes, source disagreement preservation, leakage-safe splits, and tests.

## Evidence Checked

Ledger events for M5 show the expected causal chain:

- Researcher opened M5 in cycle 3 as a public-data-backed WFO/GBIF/Open Tree name, synonym, and taxonomy sample.
- Worker marked M5 `validated/high` with builder, raw cache, normalized tables, metadata hashes, coverage figure, docs, and unittest validation.
- Auditor marked M5 `validated/high` and explicitly listed the individual raw JSON artifacts under WFO, GBIF, and Open Tree.

Required implementation and documentation artifacts exist:

- `scripts/build_public_taxonomy_sample.py`
- `tools/source_sample_checks.py`
- `tests/test_public_taxonomy_sample.py`
- `docs/public_taxonomy_sample_design.md`
- `data/public_taxonomy_sample/v0.1/metadata.json`
- `data/public_taxonomy_sample/v0.1/source_coverage.png`
- `data/public_taxonomy_sample/v0.1/seed_names.csv`
- `data/public_taxonomy_sample/v0.1/taxa.csv`
- `data/public_taxonomy_sample/v0.1/names.csv`
- `data/public_taxonomy_sample/v0.1/source_crosswalk.csv`
- `data/public_taxonomy_sample/v0.1/hyperedges.csv`
- `data/public_taxonomy_sample/v0.1/splits.csv`
- 48 raw source-response JSON files: 16 WFO, 16 GBIF, and 16 Open Tree files.

Observed frozen sample structure:

- `seed_names.csv`: 16 seed names.
- `taxa.csv`: 62 rows with source-specific IDs, ranks, parent IDs, statuses, query names, match types, and confidence fields.
- `names.csv`: 63 rows with source-local accepted-taxon mappings and `task_visibility` controls.
- `source_crosswalk.csv`: 16 rows, each with WFO, GBIF, and Open Tree fields, source match counts, match summary, and disagreement category.
- `hyperedges.csv`: 327 incidence rows using the established incidence columns.
- `splits.csv`: 47 leakage groups.
- `metadata.json`: records access date `2026-05-17`, WFO/GBIF/Open Tree endpoints, query parameters, software versions, hashes, citation/license notes, and known limitations.

The source-crosswalk and metadata support the claim that source disagreements are preserved rather than reconciled into a single taxonomic truth. All 16 seeds had two or more sources, and the recorded disagreement category was `different_status` for 16 seeds. The design document states that WFO, GBIF, and Open Tree are treated as distinct evidence systems and that the sample does not support trait, occurrence, reticulation, hybrid-origin, range, phylogenetic novelty, or broad representativeness claims.

The known `promise_check` warning about raw directory artifact paths is not a M5 defect in this verification slice. The final M5 auditor ledger event enumerates the individual raw JSON files, and all WFO/GBIF/Open Tree raw files were present on disk.

## Tests Run

Command:

```text
python3 -m unittest tests.test_public_taxonomy_sample -v
```

Observed result:

```text
Ran 6 tests in 2.314s
OK
```

Covered test cases:

- required files and schemas exist;
- metadata hashes match artifacts;
- cached builder rerun is stable for normalized outputs;
- source coverage and disagreement are preserved;
- incidence rows are unique and required edge families are present;
- split groups do not cross splits and synonym visibility is limited.

Additional check:

```text
python3 tools/source_sample_checks.py data/public_taxonomy_sample/v0.1
```

Observed result: exited successfully.

## Findings

No CRITICAL findings.

No MODERATE findings.

No MINOR findings.

## Stage Conclusion

M5 `validated/high` is supported. The artifacts exist, the metadata records access dates, endpoints, hashes, limitations, source roles, and citation/license notes, the raw source responses are frozen, normalized tables preserve source-specific identifiers and disagreements, and focused integrity tests passed.

Findings appended to `findings.jsonl`: 0.
