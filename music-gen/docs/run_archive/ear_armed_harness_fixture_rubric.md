---
created: 2026-08-29T00:00:00Z
cycle: 31
run_id: run-2026-08-28T040704Z
agent: worker (clone-2 fork cfc5009aca96)
milestone: _plan/verdict_rubric_frozen_armed_harness_fixture
---

# Ear armed-harness fixture reinforcement — frozen 2-verdict rubric

**Cycle 31 branch C, sub-milestone `M-EAR-1/armed-harness-fixture-reinforcement`.**

This rubric is FROZEN and COMMITTED BEFORE any fixture extension lands and
BEFORE any invocation of `scripts/ear/sb_dry_run.py`. Its SHA-256 is
recorded verbatim in `data/ear/armed_harness_reinforcement/sb_dry_run_verdict.json`
under `rubric_hash`. A test asserts on-disk SHA-256 of THIS file equals
the verdict JSON's `rubric_hash` field.

## Purpose

Verify the pre-registered Path B ear plan (frozen in
`docs/ear_path_b_commitment.md` cycle 26) will fire correctly and produce
all three real-label success bars (SB1/SB2/SB3) end-to-end from the
armed harness when two consecutive `media_ok=true` rows arrive on
`data/ingestion/egress_status.jsonl`. Verifies **computability**, not
real-label PASS: the SB thresholds committed in c26 remain the frozen
real-label thresholds.

## Verdict labels

### FIXTURE_READY

All of:

1. All ≥12 fixture cases PASS under
   `PYTHONPATH=. /usr/bin/python3 tests/test_ear_armed_harness_synthetic_trigger.py`.
2. AST grep clean: zero live-network imports (`urllib`, `urllib2`,
   `urllib3`, `requests`, `socket`, `httpx`, `aiohttp`, `http`,
   `http.client`) in every one of the following: `scripts/ear/train_armed_harness.py`,
   `scripts/egress_ready/*.py`, `scripts/ear/sb_dry_run.py`, and
   `tests/test_ear_armed_harness_synthetic_trigger.py`. `ast.parse`
   walk, not regex.
3. SB dry-run outputs (`data/ear/armed_harness_reinforcement/sb_dry_run_verdict.json`
   AND `data/ear/armed_harness_reinforcement/state_transitions_verification.jsonl`)
   byte-identical across two fresh temp-dir runs (SHA-256 equal).
4. All three SB threshold computations succeed end-to-end on the
   synthetic-label dry-run against the M-CLASS-1 55-clip valset without
   touching rated audio:
   - SB1 numeric margin: `sb1_margin` finite AND both baseline fields
     (`majority_class_baseline_mae`, `mean_integer_baseline_mae`) finite.
   - SB2 mean-τ over 10 stratified bootstrap resamples: `sb2_mean_tau`
     finite AND `sb2_per_resample_tau` list length 10 AND every element
     finite.
   - SB3 leak-detection rate at α=1.0 for artist/genre/era: entries for
     all three keys AND each rate finite in [0, 1].
5. `promise_check` reports 0 ERRORs (WARN drift not gated here — same
   contract as prior cycles).

### FIXTURE_INSUFFICIENT

Any of the above fail. The verdict JSON names the specific case-id AND
the specific real-label-firing gap surfaced (e.g. "SB2 bootstrap
resample seed drift", "state-machine TRAINING→TRAINED transition writes
state.json non-atomically", "content-hash gate re-fires on identical
hash"). No implementation fix in this branch; a
`_manager/armed-harness-bug-deferred` ledger event records the gap for
cycle 32.

## Escape-hatch integrity

`FIXTURE_INSUFFICIENT` is a legitimate research outcome. This branch's
purpose is to surface real-label-firing gaps BEFORE the egress unblock
lands, not to hand-wave them away.

## SB thresholds (verbatim from `docs/ear_path_b_commitment.md`, NOT changed)

- **SB1**: CORN MAE margin over `min(majority_class_baseline_mae,
  mean_integer_baseline_mae)` MUST exceed **0.5909** (frozen cycle-22
  recipe-envelope IQR). Threshold NOT re-derived here.
- **SB2**: Mean pairwise Kendall τ ≥ **0.4** across 10 stratified
  bootstrap resamples (cycle-23 threshold, cycle-22 methodology).
- **SB3**: Leak-test detection rate ≥ **0.90** at α=1.0, per leak type
  (artist, genre, era) — cycle-6 protocol via `scripts/ear/leak_test.py`.

The dry-run computes each SB metric on synthetic labels and asserts
finiteness ONLY. It DOES NOT assert PASS. Real-label PASS/FAIL is a
downstream cycle question after egress unblock.

## Rubric SHA embedding contract

The SHA-256 of this rubric file (computed with `hashlib.sha256` over the
raw UTF-8 bytes) is embedded in `sb_dry_run_verdict.json.rubric_hash`.
`tests/test_ear_armed_harness_synthetic_trigger.py` and
`tests/test_integration_cross_branch.py §47` both assert the embedded
hash equals the on-disk hash. Any drift fails the tests.

## Anti-patterns explicitly re-asserted

- Do NOT modify `scripts/ear/train_armed_harness.py`,
  `scripts/egress_ready/*`, `scripts/ear/{features,model,corn,leak_test,synthetic_labels,stability_metrics,stability_audit}.py`.
- Do NOT change any Path B commitment threshold.
- Do NOT run the VGGish R3 probe (operator directive 3).
- Do NOT re-audit Path A chassis (anti-patterns c22/c23/c25 locked).
- Do NOT touch rated audio.
- Do NOT emit live `subprocess.run` to `yt-dlp` or any network binary.
