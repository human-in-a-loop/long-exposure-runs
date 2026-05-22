---
created: 2026-05-19T00:00:00Z
cycle: final-handoff
run_id: run-phytograph-cycle1
agent: worker
milestone: _plan/final-campaign-handoff-manifest
---

# Final Campaign Handoff Manifest

PhytoGraph is scientifically closed in a conservative non-promotion state. The
campaign produced a frozen typed substrate, six instrument or benchmark paths,
validation and ablation records, a local Atlas, and a validated taxonomy-results
communication site, but no per-track result satisfies the master promotion
predicate for a validated prediction row. The master
[`prediction_ledger.tsv`](../prediction_ledger.tsv) and
[`speculation_ledger.tsv`](../speculation_ledger.tsv) remain header-only.

Canonical final artifacts:

- [`artifact_index.md`](../artifact_index.md): canonical artifact map and known
  nonblocking warning summary.
- [`research_contribution_ledger.md`](../research_contribution_ledger.md):
  contribution classification and claim boundaries.
- [`final_report.md`](../final_report.md): final campaign synthesis.
- [`audit_report.md`](../audit_report.md): audit judgment, residual warnings,
  and unsupported-claim boundary.
- [`falsification_and_ablation_report.md`](../falsification_and_ablation_report.md):
  cross-track falsification and ablation accounting.
- [`reports/reopen/final_free_tier_closure_synthesis.md`](reopen/final_free_tier_closure_synthesis.md):
  final six-track closure synthesis.
- [`reports/taxonomy_results_site_closure_note.md`](taxonomy_results_site_closure_note.md):
  validated communication-layer closure for the taxonomy results website.

Substrate and interface status:

- [`phytograph_schema.md`](../phytograph_schema.md) is frozen at schema v1.0;
  schema changes require a new scientific pass.
- [`phytograph_dataset/`](../phytograph_dataset/) is the Barrier 1 substrate;
  it supports query, provenance review, and track-local analysis, not new
  biological claims by itself.
- [`botanical_atlas_site/`](../botanical_atlas_site/) and
  [`botanical_atlas_site/page_contract.md`](../botanical_atlas_site/page_contract.md)
  expose the instrument outputs with evidence-vs-prediction boundaries; the
  validated Barrier 3 readiness record is
  [`reports/barrier3_atlas_instrument_readiness.md`](barrier3_atlas_instrument_readiness.md).
- [`taxonomy_results_site/`](../taxonomy_results_site/) is validated as a
  public communication and expert-review layer over the closed campaign.

Final track outcomes:

| Track | Final limitation class | Handoff meaning |
|---|---|---|
| Track 1 Reticulation Atlas | `sidecar_readiness_uncontrolled` | Branch-local sidecar evidence exists, but accepted-key reconciliation and source-density controls block master promotion. |
| Track 2 Ghost Hyperedges | `H2_remains_not_supported_or_data_limited` | Canonical held-out recovery is 0/8 under the validation contract. |
| Track 3 Convergence Pressure | `confound_limited` | Trait carrier rows exist, but no controlled-ready trait clears family-size and sampling-density confounds. |
| Track 4 Domestication Hypergraph | `still_data_limited` | Crop/CWR and occurrence scaffolds exist, but numeric BIOCLIM vectors and validation-allowed comparators are absent. |
| Track 5 Chemodiversity Predictor | `H5_remains_source_biased` | Non-Duke temporal evidence is insufficient for a validation-ready structured family/class stratum. |
| Track 6 Foundation Model Probe | `environment_limited_untested` | Static benchmark and deterministic scorer exist, but no qualifying local model responses were executed or scored. |

The website status is communication-only: future website maintenance may improve
clarity, accessibility, broken links, provenance hygiene, and reproducibility,
but it must not alter scientific statuses, regenerate evidence tables, or
promote prediction/speculation rows.

Inherited validator/root-layout/orphan warnings are historical and nonblocking
unless a new validation run reports a new error. In particular, the immutable
historical malformed ledger row is already covered by the validator exception
policy, legacy path warnings come from prior archived records, and required root
deliverables are expected to trigger layout warnings.

Future reopening condition: only a new scientific pass with qualifying
evidence and audited controls may modify track conclusions or write data rows to
the master prediction or speculation ledgers. Any such reopening must preserve
the distinction between observed evidence, local priors, predictions,
validated predictions, null results, and data-limited or source-biased closure.
