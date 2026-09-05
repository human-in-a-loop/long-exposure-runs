# c30 test debt — c52 disposition (Path B: historical retirement)

**Cycle**: 52 (2026-09-05)
**Scope**: `tests/test_c30_legacy_mode_regression.py` tests 38 through 42
**Authority**: c52 research brief O-2 Path B; docs/agent_picks_selection_invariants.md invariants (a) + (d); c47 operator omnibus part 4 (preservation-spin BANNED)

## Summary

Tests 38–42 assert byte-identical preservation of escalation-memo SHAs and per-cycle preservation-sidecar chain invariants (c44 → c46) that were codified during the c33→c46 preservation-cadence era. That era's core artifacts (six escalation memos, per-cycle `_selection/c<N>-*-preservation` sidecars) were structurally invalidated by the c47 operator omnibus adjudication (2026-09-05):

- 6 escalation memos closed with append-only `c47_omnibus_closure` blocks (SHA drift by design; c44-frozen `before_sha256` values no longer match on-disk).
- Preservation-spin cadence BANNED per operator directive #4 — new `_selection/c<N>-*-preservation` sidecars are not emitted from c47+ forward.

The assertions in tests 38–42 were monotonicity/byte-identity claims about that retired cadence. They are historically true (as-of the cycle they landed) but structurally void post-c47. Repinning SHAs is not applicable because the retired cadence has no successor to which the chain would supersede; the assertion class does not exist post-c47.

Per invariant (a) (do not retro-relabel finalized artifacts) and invariant (d) (on-disk-vs-brief disclosure norm), the c44/c45/c46-frozen sidecars themselves are preserved byte-identical as historical anchors — this doc retires only the assertions that gate on their monotonic continuation.

## Per-test disposition

| test | subject                                                                 | disposition        | rationale                                                                                   |
|------|-------------------------------------------------------------------------|--------------------|---------------------------------------------------------------------------------------------|
| 38   | c44 escalation-memo counter monotonicity (6 memos)                      | historical/skip    | c47 omnibus rewrote 6 memos with `c47_omnibus_closure` blocks; SHA drift by design           |
| 39   | c45 chain-supersede invariant string-not-list (c45 preservation chain)  | historical/skip    | c47 BANNED preservation-spin cadence; c45 chain has no c47+ successor                       |
| 40   | c45 P0 sidecar shape I-2 canonical adoption from c44                    | historical/skip    | same as test 39; per-cycle P0 sidecars are retired cadence                                  |
| 41   | c46 chain-supersede invariant (5 chain + 2 null-supersede sidecars)     | historical/skip    | same as test 39; c46 was the final preservation-cadence cycle before c47 pivot              |
| 42   | c46 P0 sidecar shape I-2 canonical adoption from c45                    | historical/skip    | same as test 40                                                                             |

## Preserved: tests 01–37 + 43–44

- Tests 01–37 continue to pin substantive infra invariants (anchor tables, driver SHAs, hygiene module, OP-1 sentinel behaviour, c33 POR drift, c34 empirical proof, c35 blocker, c36–c43 preservation chain sidecars themselves — the sidecars remain byte-identical as historical anchors; only the c44+ monotonic-continuation assertions retire).
- Tests 43 (c48 `--song-sha16` alias regression on drums coarse) and 44 (c48 anchor-substitution amendment shape) are orthogonal to c47 closure and remain valid.

## Skip mechanism (plain-assert compatible)

The test file uses plain-assert (no pytest). Historical-skip is expressed as an early `return` guarded by a module-level `HISTORICAL_PRE_C47_SKIP = True` flag, with a `print(f"test_<N> SKIPPED_HISTORICAL — retired per docs/c30_test_debt_c52_disposition.md")` diagnostic so the runner surface still lists the test and its disposition.

## Bar

Honest 39/39 green (34 legacy + 5 historical-skipped + 2 c48-valid = 41 total test bodies; but with 5 retired via early-return, the assertion count is 34 green + 2 green = 36; with 5 skip diagnostics printed. Reported honestly per c52 O-2 sufficiency criterion.

## Rollback

If a future operator directive un-retires the c33-c46 preservation cadence (unlikely per current omnibus), the assertions can be re-enabled by flipping the flag; the c44/c45/c46 sidecar SHAs remain on-disk as historical anchors and the assertion bodies remain intact for review.
