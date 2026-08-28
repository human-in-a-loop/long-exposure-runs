---
created: 2026-08-29T00:20:00Z
cycle: 29
run_id: run-2026-08-28T040704Z
agent: worker
milestone: M-GEN-1/collision-model-hash-space-geometry/adjudication
---

# Adjudication of the cycle-28 M3_WEAK verdict on hash-space geometry

**Verdict: `M3_COLLAPSES_TO_REFUTES`.**

The cycle-28 raw p = 0.0487 signal is a multiple-testing artifact.
Under Benjamini-Hochberg correction at q = 0.05 across all m = 35
cells, zero cells survive. Bonferroni and Šidák corrections also
yield zero survivors. Drop-batch_v2 and leave-one-cell-out sensitivity
analyses corroborate. Hash-space geometry does not explain the
residual collision structure of the M-GEN-1 batch outcomes.

## §1. Prior state and auditor charge

Cycle 28 measured hash-space uniformity per (rule_type × batch) across
the seven validated M-GEN-1 batches (v1, v2, v3_i3, v3_i4, v4, v5_n16,
v6) — 35 cells total. It computed an analytic χ²-vs-uniform p-value
per cell, defined an effective K under the M3 mechanism as
`K_eff_hash = max(K·(1 − min(1, χ²/(N·(K−1)))), 1)`, refit the
birthday-paradox model with α pinned at cycle-26's α̂ = 0.7469, and
computed a per-batch shape R² across the three shape-informative
batches (v2, v3_i3, v6). The mean shape R² came out to −0.240 and
exactly one cell reached raw p < 0.05:

    batch_v2 × harmonic: χ² = 17.0, dof = 9, K = 10, N_salts = 8,
                        raw p = 0.0487, unique_winners = 5

The cycle-28 rubric fired M3_WEAK on "hash-non-uniformity present but
shape correction modest." The auditor flagged the outcome as fragile
under multiple-testing correction: 35 tests at α = 0.05 have a
family-wise error rate ≈ 1 − 0.95^35 ≈ 0.834, so a single p = 0.049
survivor is well within the null noise floor. Cycle 29's charge:
adjudicate the verdict under Bonferroni / Šidák / Benjamini-Hochberg,
plus two sensitivity analyses (drop-batch_v2, leave-one-cell-out).

## §2. Frozen rubric (SHA + verdict definitions)

The rubric was published at
`docs/collision_model_hash_space_geometry_adjudication_rubric.md`
BEFORE any adjudication script ran. Its SHA-256:

    1571bdd074c6cc999d00506ab5a785a338234b1a81a68c14f81a3f86b884eed6

The verdict JSON's `rubric_hash` field is asserted equal to this
value at test time (`tests/test_hash_geometry_adjudication.py::
test_verdict_rubric_frozen_hash_matches_committed_doc`).

Three verdict outcomes:

- **M3_STANDS**: BH q < 0.05 leaves ≥ 1 survivor AND drop-batch_v2
  leaves ≥ 1 survivor AND leave-one-cell-out shows no single-cell
  dependence.
- **M3_COLLAPSES_TO_REFUTES**: zero BH survivors on the full m = 35
  p-vector.
- **MIXED**: exactly one survivor whose absence under drop-batch_v2
  removes it, OR total single-cell dependence under LOCO.

α is pinned at 0.7469387071101908 throughout.

## §3. Multiple-testing correction results

Input: 35-cell p-vector from
`data/collision_model/hash_uniformity_summary.json`. Output:
`data/collision_model/multiple_testing_correction.json`.

| method | threshold | survivors |
|---|---|---|
| Bonferroni (α=0.05) | 0.05 / 35 ≈ 1.4286 × 10⁻³ | **0** |
| Šidák (α=0.05) | 1 − 0.95^(1/35) ≈ 1.4644 × 10⁻³ | **0** |
| Benjamini-Hochberg (q=0.05) | rank i × 0.05 / 35 | **0** |

Five smallest p-values (BH rank annotation):

| BH rank i | cell | raw p | BH threshold i·q/m |
|---:|---|---:|---:|
| 1 | batch_v2 × harmonic | 0.048716 | 0.001429 |
| 2 | batch_v1 × rhythmic | 0.052456 | 0.002857 |
| 3 | batch_v1 × melodic | 0.264128 | 0.004286 |
| 4 | batch_v1 × arrangement | 0.313374 | 0.005714 |
| 5 | batch_v2 × melodic | 0.328532 | 0.007143 |

The rank-1 cell (batch_v2 × harmonic) misses its BH threshold by a
factor of ~34. No smaller p-value exists to pull the reject frontier
forward, so BH stops at rank 0. Bonferroni and Šidák thresholds are
essentially identical at this m.

The p = 0.0487 signal is not distinguishable from the null under any
of the three corrections. The cycle-28 M3_WEAK verdict was driven by
that single below-threshold raw p-value plus the modest-R² clause of
the rubric — the multiple-testing view removes the below-threshold
half of that predicate.

## §4. Drop-batch_v2 sensitivity

Input: 35-cell p-vector minus batch_v2 (5 cells removed). 30 cells
retained. Output:
`data/collision_model/drop_batch_v2_sensitivity.json`.

| statistic | full (m = 35) | retained (m = 30) |
|---|---:|---:|
| Bonferroni survivors | 0 | 0 |
| Šidák survivors | 0 | 0 |
| BH q=0.05 survivors | 0 | 0 |
| Mean per-batch shape R² | −0.240 | **−0.524** |

Per-batch R² breakdown, retained set (α = 0.7469 pinned throughout):

- batch_v3_i3: R² = −0.207
- batch_v6: R² = −0.840

Removing batch_v2 makes the shape fit worse, not better. batch_v2 was
the only shape-informative batch with a positive R² (+0.327);
without it the two remaining shape batches have a mean of −0.524.
This is not a defense of M3 — it's the opposite: batch_v2's
positive R² was pulled toward zero by the same 4-salt harmonic clique
that generated its raw-significant p-value. The clique is a legacy
content cluster (see §5), not a hash-space geometry signal.

Even setting R² aside, the multiple-testing verdict is unchanged:
zero BH survivors on the retained 30-cell p-vector.

## §5. Leave-one-cell-out contribution

Input: for each of the 35 cells, hold that cell out and recompute
BH survival on the remaining 34. Output:
`data/collision_model/leave_one_cell_out.json`.

- baseline BH survivors (full m = 35): **0**
- LOCO changers (any cell whose removal changes the survivor count): **0**
- single-cell-dependent flag: **False**

With zero survivors at baseline, LOCO cannot demonstrate dependency
on any single cell — there is no signal to concentrate. The LOCO
analysis is included for completeness and rubric compliance; it is
formally consistent with M3_COLLAPSES_TO_REFUTES.

## §6. The batch_v2 × harmonic cell — content-level analysis

Even though the cell fails BH, its populating content matters for
the cycle-30 direction. The rank-0 rule for this cell across salts
{0, 1, 5, 6} is:

    rule_0271c7a9f3b5f606
      rule_type: harmonic
      extractor_version: harmonic-v1
      scope: song, start=0.0s, end=262.0s (level=song)
      parameters: cadence + chord_progression + key
      provenance: clip_id 1d723bf1d16087b6,
                  transcription_event_id 5d9f8c9e...

This is the "cycle-13 4-salt clique" flagged in the cycle-28 handoff.
It's a single song-level harmonic rule on the pre-I3 76-row ledger
(`data/rules/ledger.jsonl`) whose SHA-256 rank-0 digest-prefix
happens to lead the sort for four of eight batch_v2 salts. When
`data/rules/ledger_i3_dminor.jsonl` adds 10 D-minor harmonic variants
(K = 20 in batch_v3_i3 and later), the clique dissolves — every
subsequent hash-uniformity cell has p ≥ 0.11.

This is a legacy content property, not a hash-space geometry
property. A larger, differently-distributed rules ledger removes it.
The mechanism that would need to explain M-GEN-1's residual
collision shape is elsewhere.

## §7. Byte-determinism & anchor preservation

- Cycle-28 utilities: byte-identical (test-asserted via
  `tests/fixtures/cycle28_util_shas.json.cycle_28_utilities`;
  new §41 in `tests/test_integration_cross_branch.py`).
- Cycle-26 + cycle-27 utility SHAs: unchanged (existing §40b
  anchor guard still green).
- Cycle-27 data JSONs (`shape_mechanism_fit.json`,
  `shape_mechanism_verdict.json`): unchanged.
- `data/collision_model/hash_uniformity.tsv` +
  `hash_uniformity_summary.json` (cycle-28 primary outputs): consumed
  read-only.
- α pinned at 0.7469387071101908 in all cycle-29 scripts and JSON
  outputs.
- No PRNG imports in any of the four new scripts (test-asserted).
- No `sidecar_nonfactor` or `i4_stratified` imports (test-asserted).
- Interpreter guard `assert sys.executable == "/usr/bin/python3"`
  present in all four new scripts (test-asserted).

## §8. Backfill: archived-emitter workspace-root resolution

The cycle-28 handoff documented a shadow-ledger writer bug in the
archived emitter at `tools/stale/_emit_cycle28_events.py`. The
emitter used `Path(__file__).resolve().parent.parent`, which resolves
to `tools/` (not the workspace root) when the archived file is
invoked from `tools/stale/`. This caused a stray
`tools/promise_ledger.jsonl` to be written when the shadow-ledger
cleanup event was emitted from stale.

Fix (this cycle): the emitter now walks up from `Path(__file__)` until
it finds a directory containing `promise_ledger.jsonl`, and asserts
the resulting workspace root exists. The same walk-up pattern is used
in the new `tools/_emit_cycle29_events.py` so that future archives
are safe by construction.

Regression test: `tests/test_ledger_writer_validation.py::
test_22_archived_emitter_resolves_workspace_root_from_stale` imports
the archived emitter in isolation and asserts that `_HERE` resolves
to the workspace root and that `promise_ledger.jsonl` is present
there.

## §9. Implications for cycle 30

- **Do**: pursue the cycle-28 auditor's ranked #2 candidate —
  semantic-cluster overlap. Per-rule_type structural fingerprints
  (arrangement.instrumentation multisets, chord_progression tokens,
  PCH peaks, form section partitions, rhythmic pattern tokens);
  pairwise structural distance; equivalence-classes that collide
  semantically even when rule_ids differ. Apply a frozen 3-verdict
  rubric analogous to M3 (STANDS / COLLAPSES / MIXED).
- **Do**: if the semantic-cluster overlap probe also refutes, close
  the collision-modeling arc as `PARTIAL_BP_UNRESOLVED_SHAPE`. A
  first-class negative finding, consistent with the falsifiability
  contract.
- **Do not**: refit α — cycle-26's α̂ = 0.7469 remains the anchor
  for every future mechanism test.
- **Do not**: re-attempt M1-family mechanisms — cycle-27's structural
  invariant (coherence gate mutates rule parameters but never remaps
  rule_ids across ledger rows) is a permanent codebase constraint.
- **Do not**: reopen this hash-geometry branch. The 3-verdict rubric
  is frozen and the verdict is COLLAPSES.

## §10. Frozen sufficiency criteria — this cycle

- [x] All new scripts run under `/usr/bin/python3` with interpreter
      guard, no PRNG, SHA-256-only tiebreaking.
- [x] Frozen rubric doc committed BEFORE verdict scripts run
      (verified by ledger `verdict_rubric_frozen` timestamp precedes
      `hash_geometry_adjudication_verdict.json` mtime).
- [x] `data/collision_model/hash_geometry_adjudication_verdict.json`
      exists with one of {M3_STANDS, M3_COLLAPSES_TO_REFUTES, MIXED}
      (= M3_COLLAPSES_TO_REFUTES).
- [x] Deliverable at
      `docs/collision_model_hash_space_geometry_adjudication.md`.
- [x] Six ledger events appended in strict order (see §11).
- [x] Cycle-28 utilities untouched (SHA-verified in fixture).
- [x] Archived emitter backfill landed with regression test.

## §11. Ledger events

Six events appended, in order:

1. `_run/cycle_29_launched` — in-progress/high
2. `_plan/verdict_rubric_frozen` — validated/high
3. `_infra/hash-geometry-adjudication-scripts` — validated/high
4. `_infra/archived-emitter-backfill` — validated/high
5. `M-GEN-1/collision-model-hash-space-geometry/adjudication` —
   validated/high (**terminal**, verdict = M3_COLLAPSES_TO_REFUTES)
6. `_run/cycle_29_closed` — validated/high

Every event uses the `narrative` field (not `summary`), nested
`confidence: {level, rationale, assessor}`, and the plan-of-record
`run_id = run-2026-08-28T040704Z`. Event IDs are UUID5 content-hashes
derived from canonical-JSON of each event minus `event_id` and `ts`.
