---
created: 2026-05-18T01:35:00+00:00
cycle: 8
run_id: run-phytograph-cycle8-postmerge-integration
agent: worker
milestone: _plan/wave2-postmerge-integration
---

# Barrier 2 Wave 2 Integration Report

## Scope

This report integrates fork `56e44dff3ca4` Wave 2 enrichment outputs into the
main workspace as Barrier 2 candidate inputs. It is a conformance and
evidence-boundary integration pass only: no predictive instrument was built,
no master prediction-ledger rows were filed, and no track-local enrichment row
was promoted to a biological claim.

## Integrated Outputs

| Track | Integration status | Integrated finding |
|---|---|---|
| Track 1 Reticulation | `ready_data_limited` | 28 seed rows retained across chromosome, ploidy, hybridization, polyploidization, and reticulate-inheritance evidence; 25 remain `pending_crosswalk`. |
| Track 2 Ghost partners | `ready_seed_scale` | 31 cited anachronism seed edges and 52 range-context support edges remain `not_prediction`; zero rows enter the master prediction ledger. |
| Track 3 Convergence | `ready_with_conformance_review_item` | 209,297 trait-membership rows retained as `track3_trait_membership`; no `convergence_signature` rows emitted. |
| Track 4 Domestication | `ready_data_limited` | 6 observed domestication edges retained; CWR joins and all bioclim vectors remain data-limited. |
| Track 5 Chemodiversity | `ready_with_source_bias_warning` | 23,524 resolved taxon-keyed rows, 28,733 compound-level bioactivity rows, and 9,500 Duke compound-class rows retained with a bioactivity firewall. |
| Track 6 Offline probe | `ready_offline_static` | 210 offline questions and 210 schema-shaped `adversarial_probe_edge` rows retained; no live provider responses exist. |

## Reconciled Divergences

The broad Track 3 volume and seed-scale Track 1/4 outputs are compatible
because they occupy separate track namespaces and are evidence projections, not
instrument outputs. Track 5's numeric richness is explicitly source-dominated:
Dr. Duke accounts for 0.999598 of combined enrichment plus bioactivity signal,
so Wave 3/4 work must carry source-density diagnostics and Duke ablations as
first-class inputs.

Track 3's `_other` bucket is the main conformance-review item. A first
integration-check assumption that only `capsule` and `fleshy_fruit` exceeded
the 500-row floor was invalidated because `_other` has 184,218 rows. The
correct interpretation is that only canonical traits are floor-gated for
instrument readiness; `_other` is a diagnostic bucket whose size must remain
visible at Barrier 2.

Track 4's 22 held-out validation seeds still have zero species-level overlap
with retained crop-pedigree training evidence. This is a positive integration
condition for later validation, not a coverage success claim.

## Evidence Boundaries

- Track 1 chromosome and ploidy rows support reported counts or context only;
  they do not establish reticulation events or a tree-compatibility index.
- Track 2 literature-curated seeds support cited hypotheses only; they are not
  inferred anachronism predictions.
- Track 3 trait memberships are observed/source-coded memberships only; the
  convergence-pressure instrument owns any future multi-lineage signature.
- Track 4 climate-envelope rows are placeholders until observed bioclim vectors
  exist.
- Track 5 compound bioactivity rows remain compound-keyed and do not imply
  taxon-level clinical efficacy.
- Track 6 `foundation_model_response:offline_unrun` is a schema placeholder,
  not a model response.

## Integration Check

The integration validator `tools/validate_barrier2_track_enrichment.py`
passed and wrote `data/barrier2_track_enrichment_conformance.json`.

Raw validator output:

```text
PASS: Barrier 2 track enrichment conformance (6 tracks checked)
WROTE: data/barrier2_track_enrichment_conformance.json
```

## Carry-Forward

Barrier 2 can proceed as a schema/provenance review over these local track
namespaces. Wave 3 should either run targeted source-recovery side waves for
accepted-key and non-Duke coverage gaps, or build bounded instruments that
carry the data-limited and source-bias findings as explicit caveats.
