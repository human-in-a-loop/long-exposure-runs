---
created: 2026-05-18T23:59:45+00:00
cycle: 31
run_id: run-phytograph-cycle31-fork-2f05eabe3800-postmerge-integration
agent: worker
milestone: _plan/fork-2f05eabe3800-postmerge-integration
---

# Fork 2f05eabe3800 Post-Merge Integration

## Scope

This worker-only integration reconciles fork `2f05eabe3800` clone outputs for
Track 2 free-tier ghost-hyperedge controls and Track 3 free-tier
trait/confound controls. It does not start new research, refit instruments,
fetch external sources, perform audit-level validation, or promote rows into
`prediction_ledger.tsv` or `speculation_ledger.tsv`.

## Divergence Check

The divergence table has no state-level disagreement:

| Clone | Track | Outcome | Deliverable |
|---|---|---|---|
| clone-0 | Track 2 | done | `tracks/track2/reports/track2_free_tier_ghost_evidence_controls.md` |
| clone-1 | Track 3 | done | `tracks/track3/reports/track3_free_tier_trait_confound_matrix.md` |

Both branches strengthen closure/null evidence. Neither branch authorizes a
master prediction-ledger row or an established biological claim.

## Integrated Status Records

| Track | Hypothesis | Integrated status | Evidence carried forward | Master-ledger action |
|---|---|---|---|---|
| Track 2 | H2 | `H2_remains_not_supported_or_data_limited` | The control matrix contains 8 canonical held-outs and 31 local candidates. Canonical gate counts are 2/8 accepted-key present, 0/8 independent modern-failure evidence, 0/8 non-singleton/source-class support, 7/8 living-megafauna exclusion, and 0/8 validation-contract pass. | No prediction or speculation row promoted. |
| Track 3 | H3 | `confound_limited` | The accepted-key trait matrix contains 3,069 `(trait, accepted_taxon_key)` rows across 15 canonical traits. No trait is `controlled_convergence_ready`; `drupe` and `capsule` remain pending priors because projection loss and single-source dominance still block controlled-readiness. | No prediction or speculation row promoted. |

## Reconciliation Decision

Track 2 and Track 3 agree on the shared Barrier 4 boundary: track-local
evidence can sharpen the blocker diagnosis, but current controls do not support
promotion to validated biological predictions. Track 2 is blocked by missing
accepted-key recovery, missing independent modern-failure evidence, singleton
or source-class fragility, and one living-megafauna ambiguity. Track 3 is
blocked by projection loss, source dominance, and trait-specific family or
sampling confounds.

## Ledger Boundary

The master `prediction_ledger.tsv` and `speculation_ledger.tsv` remain
header-only. This report is an integration record and handoff artifact for
future researcher/auditor cycles, not an audit decision and not a master-level
claim promotion.

## Integration Checks

The focused integration test
`tests/test_fork_2f05eabe3800_postmerge_integration.py` verifies Track 2 gate
counts, Track 3 controlled-readiness counts, branch non-promotion flags, figure
presence, and header-only master ledgers.
