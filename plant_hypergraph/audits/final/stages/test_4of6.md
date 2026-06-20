# Final Auditor Stage 11 - Test 4/6

## Scope

Detailed figure-coverage pass for the plant-taxonomy hypergraph run. This pass checked:

- Required validators.
- Figure-like files present on disk.
- Figure paths referenced by `promise_ledger.jsonl`.
- Missing ledger-referenced figures.
- Figures under the current run's research artifact tree that are not ledger-referenced.
- Figure references in final root documents.
- Planned milestones that warrant figures and whether those figures exist.

## Validators

- `python3 -m long_exposure.tools.promise_check <run-root>`: exit 0.
- `python3 -m long_exposure.tools.org_check <run-root>`: exit 0.

`promise_check` warnings remained unchanged from prior passes:

- Noncanonical raw-directory artifact paths for the M5 raw WFO/GBIF/Open Tree directories.
- Missing process-scope manager assessment artifacts under `long-exposure/manager_assessments/...`.

`org_check` warnings remained unchanged from prior passes:

- Root-level M8 deliverables and run prompt/log/score files outside its preferred allow-list.

These warnings do not indicate missing planned milestone figures.

## Research Figures Present

Seven current-run research figures are present under `data/**`:

| Path | Size bytes | Ledger referenced |
|---|---:|---|
| `data/synthetic_benchmark/v0.1/composition.png` | 50317 | yes |
| `data/public_taxonomy_sample/v0.1/source_coverage.png` | 112873 | yes |
| `data/experiments/synthetic_v0.1/metric_comparison.png` | 115241 | yes |
| `data/experiments/synthetic_v0.1/ablation_heatmap.png` | 65949 | yes |
| `data/experiments/synthetic_v0.1/case_type_breakdown.png` | 83553 | yes |
| `data/experiments/synthetic_v0.1/clique_false_similarity.png` | 60429 | yes |
| `data/formal_diagnostic/clique_warning_diagnostic.png` | 38914 | yes |

All seven are non-empty.

## Ledger Figure References

The ledger contains 40 figure-like artifact references:

- 14 references to the seven current-run research PNG files, including repeated validated entries for M3, M5, M6, and M7.
- 26 references to report PDFs under `reports/cycles/report_cycles_*.pdf`.

Missing ledger-referenced figure-like artifacts: none.

The repeated PNG references are expected because some milestones have multiple validation events. They do not create duplicate artifact obligations.

## Planned Milestone Figure Coverage

Latest planned milestone events:

| Milestone | Latest status | Latest-event figure artifacts |
|---|---|---|
| M1 | `validated` | none |
| M2 | `validated` | none |
| M3 | `validated` | `data/synthetic_benchmark/v0.1/composition.png` |
| M4 | `validated` | none |
| M5 | `validated` | `data/public_taxonomy_sample/v0.1/source_coverage.png` |
| M6 | `validated` | `data/experiments/synthetic_v0.1/metric_comparison.png`; `data/experiments/synthetic_v0.1/ablation_heatmap.png`; `data/experiments/synthetic_v0.1/case_type_breakdown.png`; `data/experiments/synthetic_v0.1/clique_false_similarity.png` |
| M7 | `validated` | `data/formal_diagnostic/clique_warning_diagnostic.png` |
| M8 | `validated` | none |

Milestones with figure artifacts in their latest ledger event: M3, M5, M6, M7.

Milestones without figure artifacts but not warranting independent figures:

- M1: data/literature feasibility map and source probe.
- M2: formal schema.
- M4: metric implementation and tests.
- M8: synthesis/index/audit/ledger root documents that reference existing figures rather than generating a new figure.

Milestones that warrant figures but lack them: none.

## Final-Document Figure References

Detected figure references in final root documents:

- `final_report.md`: 5 figure paths.
  - `data/experiments/synthetic_v0.1/metric_comparison.png`
  - `data/experiments/synthetic_v0.1/ablation_heatmap.png`
  - `data/experiments/synthetic_v0.1/case_type_breakdown.png`
  - `data/experiments/synthetic_v0.1/clique_false_similarity.png`
  - `data/formal_diagnostic/clique_warning_diagnostic.png`
- `artifact_index.md`: 7 figure paths.
  - all seven research figures listed above.
- `research_contribution_ledger.md`: 0 figure paths.
- `audit_report.md`: 0 figure paths.

All figure paths referenced by final root documents exist.

## Out-of-Scope Figure-Like Files

The workspace also contains five PDFs under `wolfram-bridge/quantum_foundations/`:

- `wolfram-bridge/quantum_foundations/report_cycles_1-1.pdf`
- `wolfram-bridge/quantum_foundations/report_cycles_1-4.pdf`
- `wolfram-bridge/quantum_foundations/report_cycles_5-6.pdf`
- `wolfram-bridge/quantum_foundations/report_cycles_7-7.pdf`
- `wolfram-bridge/quantum_foundations/report_cycles_8-11.pdf`

These are not referenced by the plant-taxonomy plan, ledger, final documents, or report index. They are treated as unrelated workspace material, not orphan figures for this run.

## Figure Coverage Values for Final Summary

For the current plant-taxonomy run:

- `figures_present`: 7
- `figures_in_ledger`: 7
- `milestones_with_figures`: 4
- `milestones_without_figures`: 0
- `missing_figures`: []
- `orphan_figures`: []

## Findings Appended

0

