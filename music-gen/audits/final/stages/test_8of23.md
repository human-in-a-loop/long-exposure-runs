# Final audit — stage 32 of 48 (test 8/23)

Working dir: `/home/user/long-exposure-runs/music-gen`
Stage output: this file
Findings appended this stage: 4 (F31–F34, all INFO/MINOR)

## Scope

Executed the four probes queued at end of stage 31:

1. Anchor-manifest structural cross-check: `file_count` vs actual disk presence.
2. `docs/pre_registration_gate_policy.md` §3 partition arithmetic + coverage.
3. `_plan/*` event pattern audit — doc artifact per plan event.
4. `promise_check` + `org_check` full runs.

## Probe 1 — Anchor manifest structural integrity (INFO / PASS)

Structural claim: every anchor in `data/anchor_manifest_v1.json` declares
`file_count == len(sha_per_path)`, and every path in `sha_per_path`
resolves on disk. Verified across all 19 anchors:

```
c06_feature_cache                             listed=90       actual=90      OK
c08_basic_pitch_venv                          listed=21260    actual=21260   OK
c09_pinned_dawdreamer_chain                   listed=1        actual=1       OK
c13_batch_v2_pipeline                         listed=2        actual=2       OK
c15_i4_stratified                             listed=1        actual=1       OK
c22_stability_harness                         listed=3        actual=3       OK
c22_antipattern_flag                          listed=1        actual=1       OK
c23_antipattern_flag                          listed=1        actual=1       OK
c25_antipattern_flag                          listed=1        actual=1       OK
c26_c27_c28_c29_c30_analytical                listed=29       actual=29      OK
c31_palette_v1                                listed=47       actual=47      OK
c31_palette_probe                             listed=28       actual=28      OK
c33_palette_render                            listed=25       actual=25      OK
c33_dawdreamer_state                          listed=23       actual=23      OK
c33_harness_clone_namespace_guard             listed=3        actual=3       OK
c34_palette_v2                                listed=40       actual=40      OK
c34_palette_render_cross_seed                 listed=40       actual=40      OK
c34_gen_palette_batch_v1                      listed=62       actual=62      OK
env/SOURCE_DATE_EPOCH                         listed=0        actual=0       OK
```

Structural claim holds; the two content-drift findings from stage 31
(F29: `c33_palette_render` + `c33_harness_clone_namespace_guard` SHA
drift) remain the only anchor-manifest drifts. Presence claims are
sound.

## Probe 2 — Pre-registration gate policy §3 partition (INFO / PASS)

The policy doc §3 partitions the 244 observed commit-classification
buckets into two named buckets:

- Harness-boundary bucket: `periodic-sweep`, `merge-integration`,
  `harness-auto-write`, `unknown`.
- In-turn-capable bucket: `worker-turn`, `auditor-turn`,
  `researcher-turn`.

Verification:

- Sum of `periodic-sweep`(105) + `merge-integration`(36) +
  `harness-auto-write`(0) + `unknown`(94) = **235**.
- Sum of `worker-turn`(9) + `auditor-turn`(0) + `researcher-turn`(0)
  = **9**.
- 235 + 9 = **244** (matches the doc's total-commit claim).
- Every observed session-context class appears in exactly one bucket
  (0 missing, 0 extras).
- `data/pre_reg_policy_verify/verdict.json.verdict == "MIXED"` matches
  §3's narrative.

Partition names the observed buckets and the arithmetic closes. No
finding.

## Probe 3 — `_plan/*` event pattern audit (INFO / PASS)

Enumerated 88 distinct `_plan/*` milestone identifiers with events in
the ledger. 87 of 88 carry a `.md` artifact (either a canonical
`docs/*.md` policy doc or `plan_of_record.md`). Sole exception:

- `_plan/c46-line-745-supersedes-field-added` — its listed artifact is
  `promise_ledger.jsonl` because this is a ledger-mechanical fix event
  (appended a missing `supersedes` field to c46 line 745 to clear a
  promise_check ERROR). Doc absence is appropriate; no policy artifact
  is warranted for a ledger schema fix.

**Verdict: PASS.** The doc-per-plan pattern is followed.

## Probe 4 — `promise_check` + `org_check` full runs

### promise_check (INFO)

- Exit-code: 0. **Zero `ERROR` lines** on `grep -c '^ERROR'` and
  `grep -c ERROR audits/final/_stage32_promise_check.out`.
- Warning total: **3437** on `grep -c '^!'`.

Warning composition:

| category | count | severity |
|---|---:|---|
| `orphan artifact in managed path` | 2713 | MINOR (long-standing hygiene debt) |
| `ledger-tracked artifact missing` | 684 | INFO (mostly `long_exposure/*` sitting under `~/human-in-a-loop/` — pre-registered as external anchor in c14 hardening) |
| `ledger:line N: artifact path ... not canonicalized` | 21 | MINOR (trailing-slash directory refs) |
| `plan milestone ... has no ledger events yet` | 20 | INFO (see below) |

The plan-milestone-no-events warnings decompose as follows (verified
in `audits/final/_stage32_ghost_check.py`):

- **13 rows with events under `-clone-<k>` suffix** — the c33 harness
  auto-suffix guard fires on `_infra|_run|_plan|_archive|_manager/` ids
  in clone context; the parent plan row never receives an unsuffixed
  event but every substantive claim landed under the suffixed id.
  Examples: `_infra/anchor-manifest-v1` (2 events under
  `-clone-2`), `_infra/harness-and-writer-hardening-v3` (1 event +
  6 children under `-clone-0`), `M-EAR-1/real-label-training-v2.1/*`
  (7 sub-leaves all under `-clone-0`). Benign per fanout-namespace
  convention.
- **6 rows with only child events, no parent rollup** — e.g.
  `M-RECREATE-2/accurate-small-set/rc10-transcription-real-stem-resurvey`
  (18 children), `_archive/deprecate-c45-determinism-check-clone-2`
  (3 children), `_infra/pre-registration-gate-policy-scope-verification-clone-1`
  (6 children). Cosmetic. Rollup convention not applied consistently.
- **1 legitimately deferred**: `M-RECREATE-2/accurate-small-set/rc8-peak-section-selection`
  (0 events, 0 children, 0 clone-suffix) is a c51+ RC-v2 branch stub
  that was registered in the plan but genuinely never landed. Deferred
  per operator halt.

The 0-ERROR invariant from the plan of record holds. Warnings are pre-existing.

### org_check (MINOR)

- Exit-code: 0. Zero `ERROR` lines.
- Warning total: **47** — all "figure in docs/" (figures should be
  co-located with their source script + data, not under `docs/`).

Cosmetic org-hygiene noise. Long-standing. Deferred.

## New findings this stage

- **F31 INFO/PASS** — Anchor manifest file_count claims are
  structurally sound. All 19 anchors resolve; the only drifts remain
  the two content SHA drifts logged in F29 (stage 31).
- **F32 INFO/PASS** — Policy §3 partition covers all 244 observed
  commits with correct arithmetic (235 harness-boundary + 9
  in-turn-capable = 244).
- **F33 INFO/PASS** — 87/88 `_plan/*` events land a `.md` policy or
  plan-of-record artifact; sole exception is a ledger-mechanical fix
  and appropriately artifactless.
- **F34 MINOR** — `promise_check` 0-ERROR contract holds but produces
  3437 pre-existing warnings (2713 orphan / 684 missing / 21
  non-canonical path / 20 plan-milestone-no-events). `org_check`
  produces 47 figure-in-docs warnings. Neither surfaces new
  correctness defects.

## Prior findings disposition summary

- F18 rubric-mtime → PASS (prior stages).
- F19 cycle-report coverage → MODERATE narrowed (prior stages).
- F20 → F24 install location → INFO resolved (prior stages).
- F21 → F28 (band-7 manifest) MINOR (stage 31).
- F23 → MODERATE cosmetic naming drift (prior stages).
- F25, F26, F27, F30 → PASS/INFO (prior stages).
- F29 anchor drift → MODERATE (stage 31 — recommend v2 manifest ratchet).

## Planned probes for stage 33 (test 9/23)

1. **Rated-corpus TSV vs on-disk audio** — walk
   `corpus/ratings/ratings_manifest.tsv` and check that each song's
   audio file resolves and its SHA-256 matches the recorded manifest
   value (partial validation was done in stage 31 for the band-7 gap;
   this widens to all 80/80 or 80/43 rows depending on registered
   rows).
2. **Egress-probe cadence** — enumerate all `M-INGEST-1/egress-probe*`
   ledger events (should exist for c46-c54); verify every cycle in
   that range has at least one probe row per c49 policy.
3. **Test suite health** — `find tests/ -name 'test_*.py' | wc -l`
   and spot-check that at least the most-recently-added suites (c51+)
   still resolve their pre-registered SHA anchors.
4. **Ledger schema-check** — validate every row of
   `promise_ledger.jsonl` through `long_exposure.tools._ledger_schema
   .validate_event`.

<checkpoint>
  <stage>test (8/23)</stage>
  <status>working</status>
  <confidence>high</confidence>
  <tokens>~185k / 1000k</tokens>
  <budget-pressure>none</budget-pressure>
  <what-i-did>Ran the four probes queued at end of stage 31.
    Probes 1–3 pass cleanly. Probe 4 confirms promise_check +
    org_check hold their 0-ERROR contracts but produce large pre-
    existing warning tails; classified.</what-i-did>
  <next-action>Move to stage 33 (test 9/23): rated-corpus SHA
    coverage + egress-probe cadence + test suite health + ledger
    schema-check.</next-action>
  <gate-check>Continuing in test.</gate-check>
</checkpoint>
