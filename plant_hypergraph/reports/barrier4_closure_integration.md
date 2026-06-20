---
created: 2026-05-18T14:05:00+00:00
cycle: 20
run_id: run-phytograph-cycle20-barrier4-closure-integration
agent: worker
milestone: _plan/barrier4-closure-integration
---

# Barrier 4 Closure Integration

## Scope

This post-merge integration reconciles fork `0b556d9370a2` Track 1, Track 4,
and Track 6 closure/refinement outputs into the main workspace. It reads the
branch reports and existing local artifacts only. It does not alter the frozen
schema, substrate, Atlas, `prediction_ledger.tsv`, or `speculation_ledger.tsv`.

## Divergence Check

The fork divergence table has no state-level disagreement:

| Clone | Track | Outcome | Deliverable |
|---|---|---|---|
| clone-0 | Track 1 | done | `tracks/track1/reports/track1_barrier4_closure.md` |
| clone-1 | Track 4 | done | `tracks/track4/reports/track4_barrier4_closure.md` |
| clone-2 | Track 6 | done | `tracks/track6/reports/track6_barrier4_closure.md` |

The only reconciliation point is interpretive: all three branches produce
closure evidence, not validated master predictions.

## Integrated Status Records

| Track | Hypothesis | Barrier 4 status | Evidence | Master-ledger action |
|---|---|---|---|---|
| Track 1 | H1 | data-limited | Current canonical accepted-key recovery is 0/8; full-WFO sidecar recovery is 5/8, but event-shaped recovery reaches only 3/8 with synonym rescue or 2/8 with exact accepted-taxon rows. | No prediction or speculation row promoted. |
| Track 4 | H4 | data-limited | Current evidence has 3/69 joined CWR pairs, 2/22 held-out accepted-key rows, 36/375 accepted-key climate rows, and 0 observed bioclim vectors; all 3 candidate rows remain `pending_data_limited`. | No recommendation, climate-match, prediction, or speculation row promoted. |
| Track 6 | H6 | environment-limited / untested | The benchmark and deterministic controls exist, but no free/open/local runtime is runnable: `transformers=false`, `torch=false`, `llama_cpp=false`, local model files = 0. | No model error-rate, leaderboard, policy, prediction, or speculation row promoted. |

## Reconciliation Decision

Track 1's full-WFO sidecar improves the diagnosis from a simple accepted-key
failure to a mixed blocker: frozen-subset truncation, name-status mismatch,
exact-name absence, raw-name absence, and insufficient event-shaped accepted-key
coverage. This refines H1's future-data recipe, but it does not validate the
reticulation instrument.

Track 4's closure is consistent with the earlier M1.6 terminal data-limited
disposition: climate matching is undefined when observed bioclim vectors are
absent. The three candidate rows may stay as local pedigree/CWR candidate-prior
rows only.

Track 6's refreshed outputs are scorer and benchmark infrastructure. The
deterministic controls verify the harness path, while the verbatim expected
answer diagnostic documents the lexical scorer limitation. No model-response
claim is supported until local open model weights and audited response rows
exist.

## Ledger Boundary

The master `prediction_ledger.tsv` and `speculation_ledger.tsv` remain
header-only. The integrated result is a Barrier 4 status reconciliation record,
not a promotion of biological, climate-substitution, or foundation-model
performance claims.
