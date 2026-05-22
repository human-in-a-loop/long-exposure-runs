---
created: 2026-05-18T14:45:00+00:00
cycle: 21
run_id: run-phytograph-cycle21-wave5-final-synthesis
agent: worker
milestone: M5.1
---

# Audit Report: PhytoGraph Wave 5

## Audit Judgment

PhytoGraph does not currently satisfy the original research success criterion
of one validated prediction per track. The campaign is nevertheless internally
consistent as a conservative infrastructure, validation, and falsification run:
unsupported biological, climate-substitution, phytochemical, and model
performance claims were not promoted.

## Primary Failures And Limitations

- Track 1 H1 is `sidecar_readiness_uncontrolled`: the free-tier GBIF-keyed
  sidecar retained 22 event taxa across 11 source groups, but WFO projection
  retained only 2 taxa and source-density controls remain unresolved.
- Track 2 H2 is `H2_remains_not_supported_or_data_limited`: the free-tier
  branch retained 8 canonical held-outs and 31 local candidates, but 0/8
  canonical held-outs pass the validation contract.
- Track 3 H3 is `confound_limited`: the free-tier branch retained 3,069
  accepted-key trait carrier rows across 15 canonical traits, but
  0 controlled-ready traits are present and candidate convergence-prior rows
  are local only.
- Track 4 H4 is `still_data_limited`: 3,358 post-filter occurrence records
  exist, but numeric BIOCLIM vectors and validation-allowed comparator rows
  are both 0.
- Track 5 H5 is `H5_remains_source_biased`: non-Duke temporal evidence remains
  insufficient and no validation-ready structured family/class stratum exists.
- Track 6 H6 is `environment_limited_untested`: there are 0 runnable local
  runtime-weight pairings, 0 executed responses, and 0 scored responses.

## Unsupported Claims Avoided

The final synthesis does not claim new taxonomy, new accepted names, new
hybrid origins, new anachronisms, new crop recommendations, new native ranges,
new phytochemical detections, new clinical bioactivity, or foundation-model
error rates. Track outputs are described as observed evidence, local priors,
data-limited closures, source-bias nulls, or environment-limited scaffolds.

## Validator Coverage

The requested Wave 5 checks cover the critical path:

- `tests/test_reopen_closure_addendum.py` verifies post-reopen branch status
  coverage, header-only master ledgers, forbidden-claim language, future-data
  predicate framing, and the reopen branch outcome figure.
- `tests/test_free_tier_recovery_integration.py` verifies cycle 28 Track 1/4/5
  free-tier branch reconciliation and continued header-only master ledgers.
- `tests/test_free_tier_track2_track3_closure_integration.py` verifies Track
  2/3 free-tier closure representation, future-data blockers, figures, and
  continued header-only master ledgers.
- `tests/test_final_free_tier_closure_synthesis.py` verifies the final
  six-track free-tier status table, root/reopen consistency, nonblank final
  status figure, and continued header-only master ledgers.
- `tests/test_wave4_postmerge_integration.py` verifies Track 2/3/5
  integration outcomes and header-only master ledgers.
- `tests/test_barrier4_closure_integration.py` verifies Track 1/4/6 closure
  counts and master-ledger non-promotion.
- `tools/validate_barrier3_atlas_integration.py` verifies instrument-to-Atlas
  readiness.
- `tools/validate_barrier2_track_enrichment.py` verifies track enrichment
  conformance.
- `tools/validate_barrier1_substrate.py` verifies frozen substrate integrity.
- `promise_check` and `org_check` verify ledger and organization consistency
  with inherited warnings.

## Residual Warnings

Known warnings are inherited and nonblocking:

- Immutable historical malformed ledger line 85 is consumed by the validator
  exception policy and must not be rewritten.
- Older ledger rows contain noncanonical raw paths and legacy artifact
  references from the superseded plant-taxonomy campaign.
- Some plan milestones remain without exact current events because they are
  aggregate or archived historical milestones.
- Required root deliverables produce root-layout warnings under `org_check`.

No new warning changes the Wave 5 claim boundary.

## Post-Reopen Audit Note

The validated reopen branches and free-tier integrations do not alter the
master-ledger judgment. Track 1 is now `sidecar_readiness_uncontrolled`: the
GBIF-keyed free-tier sidecar retained 22 event taxa across 11 source groups, but
WFO projection is 2 taxa and source-density controls are unresolved. Track 2
remains `H2_remains_not_supported_or_data_limited` with 0/8 canonical held-outs
passing the validation contract. Track 3 remains `confound_limited` with
0 controlled-ready traits across 3,069 accepted-key carrier rows. Track 4 is
`still_data_limited` with 3,358 post-filter occurrence records, 0 numeric
BIOCLIM vectors, and 0 validation-allowed comparator rows. Track 5 is
`H5_remains_source_biased`, and Track 6 is `environment_limited_untested`. The
master ledgers staying header-only is therefore a non-promotion decision, not an
omission.

## Audit Conclusion

The correct final claim is negative and bounded: PhytoGraph produced a useful
typed substrate, Atlas integration surface, six instrument paths, and explicit
falsification/data-limit accounting, but did not yet produce validated
predictions across all tracks.
