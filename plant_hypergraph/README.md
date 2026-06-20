# Plant Hypergraph Research Run

This folder contains a long-exposure research run exploring whether botanical
knowledge can be organized as a typed hypergraph across taxonomy, reticulation,
convergence, domestication, chemodiversity, and model-probing tracks.

The run is intentionally conservative: it records many useful infrastructure,
validation, and public-communication artifacts, while keeping master prediction
and speculation ledgers header-only when evidence did not satisfy the campaign's
promotion criteria.

## Key Outputs

- `reports/final/final_report.md` - final narrative report for the campaign.
- `audits/final/final_audit_report.md` - final audit of the run artifacts.
- `reports/cycles/` - in-cycle reports showing campaign progress.
- `taxonomy_results_site/` - local interactive public-facing review site.
- `phytograph_dataset/` - derived graph substrate artifacts retained under the
  repository file-size limits.
- `tracks/` - track-specific data, scripts, reports, and tests.

## Local Website

Serve the review site from this folder with:

```bash
python3 -m http.server 8765 --directory taxonomy_results_site
```

Then open `http://127.0.0.1:8765/`.

## Publication Notes

Transient orchestration state, raw source caches, stale folders, local account
configuration, and oversized files were excluded from this public copy. Remaining
paths were sanitized to avoid local machine identifiers while preserving the
scientific structure of the run.
