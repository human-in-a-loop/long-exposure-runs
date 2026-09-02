# Final Audit — Stage 26 of 48 (Test 2 of 23)

**Stage:** test (2/23) — adversarial probes on validated verdicts
**Working dir:** `/home/user/long-exposure-runs/music-gen`
**Preceding stage:** test_1of23 (structural validators + ledger→disk artifact cross-map)

## Probes run this stage

1. `sidecar_nonfactor` non-factor-isolation grep across full tree (production code only).
2. PRNG-import grep across `scripts/` (looking for `random` / `numpy.random` in modules that
   claim SHA-256-only determinism).
3. Egress-probe honesty audit: statistical inspection of `data/ingestion/egress_status.jsonl`
   (34 rows), plus deep-dive on any `media_ok=true` rows and the surrounding trigger
   state-machine contract.
4. Trigger-state-machine liveness audit: search for `data/egress_ready/` state file and
   transitions log.

## Findings

| # | Severity | Verdict | Summary |
|---|----------|---------|---------|
| F6 | INFO | CONFIRMED | Non-factor sidecar isolation holds in production code |
| F7 | INFO | CONFIRMED | PRNG imports in `scripts/ear/{train.py, model.py}` are seed-controlled |
| F8 | MODERATE | CONFIRMED | Two consecutive `media_ok=true` bootstrap rows (cycle 1, video_id `jNQXAC9IVRw` = YouTube's canonical smoke-test "Me at the zoo") satisfy the documented unblock signal, but the trigger state machine was NEVER wired into a live loop — no `data/egress_ready/` state file or transitions log exists on disk |
| F9 | MODERATE | CONFIRMED | `egress_status.jsonl` schema lacks a `probe_kind` field to distinguish bootstrap/smoke-test probes from production retries; the two cycle-1 bootstrap rows are semantically indistinguishable from production `media_ok=true` and would have spuriously fired the harvest pipeline had the machine been running |

### F6 — Non-factor sidecar isolation: CLEAN

Grep for `from|import scripts.classifier.sidecar_nonfactor` across the tree returns 25 hits.
Manual triage:
- 12 hits in `tests/` files (assertion patterns, planted PLANT lines, forbidden-pattern regex sources).
- 8 hits in `docs/` (documentation citing the isolation contract).
- 3 hits in `scripts/*/validate.py` and `scripts/ear/leak_test.py` (comments declaring the contract).
- 1 hit in `audits/_plant_and_catch.py` (audit tool that plants + catches).
- 0 hits of actual production imports in `scripts/` outside the documented planted-and-caught paths.

The non-factor isolation contract holds.

### F7 — PRNG imports in ear-model chassis: SEED-CONTROLLED

`scripts/ear/train.py` and `scripts/ear/model.py` import `random` and use `np.random.seed(seed)`,
`random.seed(seed)`, `np.random.default_rng(seed)`, and `StratifiedKFold(random_state=seed)`.
Every call site threads a fixed `seed` argument. Combined with the pinned BLAS + `torch.manual_seed(0)`
env pins documented in the c22/c26/c45/c46/c47 stability harnesses, these produce byte-deterministic
outputs (verified by the c45 `determinism_check_c46.py` two-fresh-runs contract). Not a defect —
the "no PRNG" clause in specific milestone rubrics scopes to the SHA-256-only sampling paths
(`scripts/gen/sample_rules.py`, `scripts/rules/sampling/*`), not to the CV training loop.

### F8 — Egress trigger state machine was never wired live

Findings from `data/ingestion/egress_status.jsonl` (34 rows):
- 32 rows: `media_ok=false` (production probes across cycles 36-54, all with the documented
  HTTP 429 + `tv_embedded` failure mode).
- 2 rows: `media_ok=true` (index 0 and 1, both at `2026-08-28T04:18:04Z` and `04:18:07Z`).

The two `media_ok=true` rows are 3 seconds apart and both target `video_id: "jNQXAC9IVRw"`
(YouTube's very first video "Me at the zoo"), which is the canonical smoke-test target used
by `workspace/smoke_test.py`. They landed 71 seconds after `_run/start` (`2026-08-28T04:07:04Z`),
placing them in the workspace bootstrap window before any milestone events.

Per `M-INGEST-1/egress-probe` success criteria and the `M-INGEST-1/egress-ready-automation`
contract, **two consecutive `media_ok=true` rows are the ingestion-unblock signal**. This should
have fired the state machine's `IDLE→ARMED→TRIGGERED→HARVESTING→CHUNKING→CLASSIFYING→READY`
transition chain. It did not:

- No `data/egress_ready/` directory exists on disk.
- No `state.json`, `transitions.jsonl`, `rated_ready.flag`, or any other live-monitor artifact
  is present anywhere under `data/`.
- The `M-INGEST-1/egress-ready-automation` milestone was validated (cycle 8) using six SYNTHETIC
  fixture scenarios — the state machine was never wired to a supervisor process or cron that would
  execute it against the live `egress_status.jsonl` file.

Retroactive-safety analysis: the `staleness_hours=24` window in `scripts/egress_ready/trigger.py`
means that from cycle 9 onward (>24h after `04:18:04Z`), the bootstrap rows are correctly ignored
as stale. So the campaign's later narrative ("egress remains blocked") is honest and correct
in effect. But there was a ~24-hour window during cycles 1-8 in which the trigger, if wired live,
would have fired on the bootstrap smoke-test rows.

### F9 — Egress schema lacks probe_kind field

`data/ingestion/egress_status.jsonl` rows carry `{http_code, media_ok, metadata_ok, note,
stream_url_present, ts, video_id}` (plus `bytes_downloaded` on failure rows). No field
distinguishes:
- production probes (`workspace/harvest_playlists.sh` retries against operator playlists)
- bootstrap smoke-test probes (`workspace/smoke_test.py` against the canonical `jNQXAC9IVRw`)

The two smoke-test rows are semantically indistinguishable from production `media_ok=true` at
row-schema level. Combined with F8, this is a latent capability gap: had the state machine
been wired live during cycle 1, it would have spuriously triggered the rated-corpus harvest
pipeline based on smoke-test rows.

Neither F8 nor F9 falsifies any validated milestone verdict — the campaign's narrative that
"egress is blocked" is empirically correct throughout cycles 2-54. Severity is MODERATE because
these are capability/design gaps, not incorrect claims.

## Gate check (test stage)

- Every fix from prior stages verified against its finding? — N/A: audit-only probes; no fixes applied.
- Adjacent behavior checked for regressions? — Yes: sidecar isolation, PRNG seeding, and egress
  probes are the three most sensitive surfaces for silent supersession; all three probed.
- New issues classified? — Yes: F6 INFO, F7 INFO, F8 MODERATE, F9 MODERATE.

## What's next (stage 27 = test 3/23)

Planned probes:
- Orphan-milestones scan: `promise_ledger.jsonl` milestone_ids not on any plan-of-record row.
- Plan/ledger consistency: milestones in POR with no ledger events (or with only status-drifting events).
- Test-suite invocation audit: for each `tests/test_*.py`, is there a validated milestone
  claiming it runs green?
- Spot-sample verdict-SHA re-check: pick 3-5 terminal-validated milestones and re-hash their
  claimed anchor files against ledger narrative.

<checkpoint>
  <stage>test (2/23) — stage 26/48</stage>
  <status>working</status>
  <confidence>high</confidence>
  <tokens>~185k / 1000k</tokens>
  <budget-pressure>none</budget-pressure>
  <what-i-did>Ran 4 adversarial probes: sidecar isolation (CLEAN), PRNG determinism (SEED-CONTROLLED), egress-probe honesty (found two consecutive media_ok=true bootstrap rows at cycle 1), and trigger-state-machine liveness (found NO live-monitor artifacts).</what-i-did>
  <next-action>Advance to stage 27 (test 3/23): orphan milestones, plan/ledger consistency, test-suite audit, spot-sample verdict SHA re-check.</next-action>
  <gate-check>Every finding classified with severity + verdict; adjacent behaviors checked; report + findings.jsonl appended.</gate-check>
</checkpoint>
