# Freshness-cache short-circuit policy (orchestrator layer)

**Cycle:** c24
**Directive origin:** OPERATOR DECISION 2026-09-03 (live_guidance), point 4:
> Fold the clone's freshness-cache recommendation in as designed (short-circuit
> identical replay audits after N=3).

## Problem observed

Peach Dream c23 fork `d5530f8d1ccc` clone-1 produced ten consecutive cycles
on byte-identical `(directive, work_output, plan_of_record_head)` inputs after
its substantive delivery landed at cycle 3. Researcher REV 7 contracted to a
single sentence, worker output was literally "No action.", and the auditor
issued a tenth consecutive VALIDATED — no state advanced, budget was spent.

## Policy

Before invoking any agent for a given cycle, the orchestrator computes

    replay_key = sha256(canonical_json({
      "directive":         <verbatim directive input for this cycle>,
      "work_output":       <verbatim last worker OUTPUT block, or empty string>,
      "plan_of_record_head": <sha256(plan_of_record.md)>,
    }))

and appends `(replay_key, cycle_number)` to a rolling per-branch queue. If the
last **N=3** entries share the same `replay_key`, the cycle is **short-circuited**:

- No agent is invoked.
- A `_run/cycle_<N>_short_circuited_identical_replay` ledger event fires with
  the replay_key, the three prior cycle numbers, and a rationale sentence.
- The branch is marked `awaiting_operator_input`; the escalation options
  named in the earlier PARTIAL verdict (or a generic three-way — fresh cycle
  budget, `--reproduce-check` redirect, retirement — depending on branch
  posture) are surfaced.

## Semantics

- N is 3, not 2 — a single duplicate is normal after a checkpoint; two might be
  a legitimate wait for a background result. Three identical replays with no
  intervening state change is the failure mode.
- The queue is per-branch (per-clone in a fanout; per-root in single-clone
  cycles). One branch stalling does not stall siblings.
- Short-circuit is not termination. Once a new input arrives (operator
  message, sibling branch completes, external state changes plan_of_record),
  the queue window slides and the next cycle runs normally.
- `--force-fresh` reserved keyword allows the operator to override the
  short-circuit for one cycle (e.g. to bring in a new context that is not
  yet reflected in the tuple).

## Interaction with the checkpointed driver (c24)

The freshness cache lives ABOVE the worker. A worker running the checkpointed
`recreate_v3_checkpointed.py` may legitimately produce byte-identical outputs
on two consecutive cycles (all stages cache-hit) — that is a **success**, not
a stall, because the plan_of_record advanced between cycles (new sub-leaves
land, verdict.json is fresh even if bytes are equal). The freshness key
already includes `plan_of_record_head`, so successful cache-hit cycles do
not trip the short-circuit.

## Scope

This document specifies the policy. Implementation is the orchestrator's
responsibility (outside the worker sandbox). The worker's contribution ends
at authoring the policy and identifying the invariants — the honest
handoff to root-conductor territory.

## Falsifiability

The policy is falsifiable at implementation time by a single test:
manufacture three identical `(directive, work_output, plan_of_record_head)`
tuples, invoke the orchestrator's cycle-decision hook, and assert the
fourth invocation is short-circuited without dispatching an agent. The
test lives in the orchestrator's test suite, not the worker sandbox.
