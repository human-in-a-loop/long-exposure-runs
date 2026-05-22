# Final Audit Stage 9 - Test 2/6

## Scope

Adversarial test pass focused on artifact existence and claimed-artifact mismatch across:

- the full promise ledger,
- latest planned milestone events M1-M8,
- final root documents,
- figure files referenced by ledger artifacts.

This pass also reran the required validators.

## Commands Run

From `<run-root>`:

```bash
python3 -m long_exposure.tools.promise_check <run-root>
python3 -m long_exposure.tools.org_check <run-root>
```

Additional structured scan:

- Parsed all 68 ledger events from `promise_ledger.jsonl`.
- Checked all ledger artifact paths for on-disk existence.
- Checked latest M1-M8 artifact paths independently.
- Conservatively extracted path-like claims from:
  - `final_report.md`
  - `artifact_index.md`
  - `research_contribution_ledger.md`
  - `audit_report.md`
- Checked PNG files under `data/**` against ledger PNG references.

## Validator Results

`promise_check` exited `0`.

Observed warnings:

- Three noncanonical directory artifact paths for `data/public_taxonomy_sample/v0.1/raw/{wfo,gbif,opentree}/`.
- Missing ledger-tracked manager assessment artifacts under `long-exposure/manager_assessments/...`.

The independent ledger artifact scan found the three raw source directories present on disk. It also found no missing planned milestone artifact paths. The manager assessment warnings remain process-scope and do not affect M1-M8 evidence closure.

`org_check` exited `0`.

Observed warnings:

- Root-level final deliverables and run files outside the tool's preferred organization allow-list.

These are not treated as milestone defects because M8 explicitly required the root-level deliverables `final_report.md`, `artifact_index.md`, `research_contribution_ledger.md`, and `audit_report.md`.

## Ledger Artifact Results

Full ledger artifact scan:

| Category | Missing count |
|---|---:|
| All ledger artifact paths | 0 |
| Planned milestone artifact paths | 0 |
| Process/auxiliary artifact paths | 0 |

Directory artifact paths:

| Ledger line | Milestone | Path | Exists |
|---:|---|---|---|
| 17 | M5 | `data/public_taxonomy_sample/v0.1/raw/wfo/` | true |
| 17 | M5 | `data/public_taxonomy_sample/v0.1/raw/gbif/` | true |
| 17 | M5 | `data/public_taxonomy_sample/v0.1/raw/opentree/` | true |

Latest planned milestone artifact status:

| Milestone | Latest artifacts | Missing |
|---|---:|---:|
| M1 | 6 | 0 |
| M2 | 1 | 0 |
| M3 | 9 | 0 |
| M4 | 3 | 0 |
| M5 | 60 | 0 |
| M6 | 15 | 0 |
| M7 | 7 | 0 |
| M8 | 4 | 0 |

## Final Document Path Claims

Conservative path extraction found no missing candidate paths in the final root documents:

| Document | Candidate paths checked | Missing |
|---|---:|---:|
| `final_report.md` | 31 | 0 |
| `artifact_index.md` | 61 | 0 |
| `research_contribution_ledger.md` | 21 | 0 |
| `audit_report.md` | 9 | 0 |

The scanner skipped glob/meta tokens and did not treat prose warning fragments as artifact claims.

## Figure Reference Preview

Seven PNG files were present under `data/**`, and all seven were referenced by ledger artifact paths:

- `data/synthetic_benchmark/v0.1/composition.png`
- `data/public_taxonomy_sample/v0.1/source_coverage.png`
- `data/experiments/synthetic_v0.1/metric_comparison.png`
- `data/experiments/synthetic_v0.1/ablation_heatmap.png`
- `data/experiments/synthetic_v0.1/case_type_breakdown.png`
- `data/experiments/synthetic_v0.1/clique_false_similarity.png`
- `data/formal_diagnostic/clique_warning_diagnostic.png`

Detailed figure-coverage judgment is reserved for a later test pass.

## Findings Appended

None.

No CRITICAL, MODERATE, or MINOR planned-milestone finding was identified in this slice, so `<run-root>/audits/final/findings.jsonl` was left unchanged.
