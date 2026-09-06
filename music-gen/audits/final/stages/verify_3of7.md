# Verify Pass 3/7 — c47 Escalation Closures

Slice: Explore.md §3 verdict-pending item 3 — the six c47-adjudicated
manager escalation memos + invariant (f) codification + post-c47
reopen scan.

## Method

1. Enumerate the 6 memos under `data/v4/_manager/`.
2. Load each JSON; assert `c47_omnibus_closure` block presence, block
   schema, `status=closed_by_operator`, `blocked_on_operator=false`,
   `adjudication_outcome` semantics.
3. Grep `promise_ledger.jsonl` for any post-c47 (cycle ≥ 48) event
   under these milestone_ids that would reopen the block.
4. Verify invariant (f) codified in
   `docs/agent_picks_selection_invariants.md` (the c47 codification
   requirement).

## Results

### 6/6 memos closed with well-formed c47_omnibus_closure block

| Memo | status | blocked_on_op | adjudication_outcome |
|---|---|---|---|
| M-V4-CERT-composite-fp-drift-adjudication-c32 | closed_by_operator | False | PATH_A |
| M-V4-CERT-fine-fit-sf2-drums-legacy-halt | closed_by_operator | False | PATH_A |
| M-V4-CERT-fine-fit-sf2-v2-legacy-halt | closed_by_operator | False | PATH_A |
| M-V4-CERT-fine-fit-sf2-guitar-legacy-halt | closed_by_operator | False | PATH_A |
| M-V4-METRIC-SEMANTICS-c16 | closed_by_operator | False | CLOSED |
| M-V4-SHOWCASE-1-non-cg-bass-acceptance-policy | closed_by_operator | False | OPT1_EXTENDED_CAMPAIGN_WIDE |

### c47_omnibus_closure block schema (verified on every memo)

All 6 memos carry the append-only closure block with these keys:
`adjudicated_at`, `adjudicated_by`, `adjudicated_via`,
`adjudication_outcome`, `chosen_path`, `pre_closure_sha256`, `rationale`.

The composite-FP-drift umbrella memo additionally carries `cascade_closes`
(listing the 3 fine-fit halts) and `invariant_added` (naming invariant
(f)) — expected fields for the umbrella-scope memo per c47 brief.

Each memo preserves its `pre_closure_sha256` — the SHA of the memo body
prior to the c47 closure-block append — as required by the append-only
discipline (c14 str-supersede lemma applies here: closure is an
additive block, not a rewrite).

### Post-c47 reopen scan

Ledger scan of `promise_ledger.jsonl` for cycle ≥ 48 events under any
of these 6 milestone_ids: **0 events found for any of the 6 memos.**

That is: the closures held across c48 → c78 (56 cycles). No later
cycle emitted a `status=action_required` or `blocked_on_operator=true`
event that would re-open the adjudication. Consistent with the
c47-c77 chain-closure narrative in POR.

### Invariant (f) codification

`docs/agent_picks_selection_invariants.md` contains an `## Invariant (f)`
section at line 115 titled "legacy-mode regression bar (composite
FP-drift adjudication)". String `invariant (f)` occurs twice in the
doc (section header + version-block reference), matching the c47
codification requirement.

## Findings

**0 new findings this pass.**

Baseline findings F1 + F2 (from stages 1-2) are unaffected by this
slice; the c47 escalation closures do not reopen or invalidate them.

## Adjacent-behavior spot-checks

- Ledger POR narrative at c47 refers to the same 6 memos with matching
  adjudication outcomes (PATH_A × 4 + CLOSED + OPT1_EXTENDED).
- No ledger event under any `_manager/M-V4-*` id lands with
  `status=action_required` after c47. The escalation surface is empty
  through c78 (delta-window terminus).

## Verdict on this slice

c47 escalation closures are on-disk substantive and durable: 6/6 memos
closed with schema-compliant closure blocks, pre-closure SHAs
preserved, no post-c47 reopens, invariant (f) codified. This slice
consumes no CRITICAL/MODERATE audit budget.

## Next stage

Stage 5 = verify 4/7. Recommended pick: item 4 (c72-c74 M-V4-GEN-1
iterations 1-3 byte-determinism × 2 across 15 renders across 5 songs).
Concrete steps: for each iteration in {01, 02, 03}, list the 5
per-song delivery dirs; parse each `ab_mix.replay_proof.json`; assert
`REPLAY_PROOF_HOLDS` + `run1_sha256 == run2_sha256 == ab_mix.wav
SHA-256`; verify env_pin_sha256 canonical `2ac444c3…`; check that
across the 3 iterations the 15 mix SHAs are pairwise distinct
(evidence that seed shifts 0→1→2 produced genuine novelty and not a
cache short-circuit).
