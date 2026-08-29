---
created: 2026-08-29T00:30:00Z
cycle: 31
run_id: run-2026-08-28T040704Z
agent: worker (clone-2 fork cfc5009aca96)
milestone: M-EAR-1/armed-harness-fixture-reinforcement
verdict: FIXTURE_READY
rubric_hash: ff853170f22aaa08e4dfa1d4656262fabd221fbbf405f72ba3f345236e12f689
---

# Ear armed-harness fixture reinforcement — cycle 31 branch C

**Verdict: FIXTURE_READY.** All 19 fixture cases PASS; AST-grep clean;
SB dry-run outputs byte-identical across two fresh temp-dir runs;
SB1/SB2/SB3 all computable from the c22 synthetic-label protocol on the
55-clip M-CLASS-1 valset. The pre-registered Path B ear plan (frozen in
`docs/ear_path_b_commitment.md`, cycle 26) will fire correctly and
produce all three real-label success bars end-to-end from the armed
harness when two consecutive `media_ok=true` rows arrive on
`data/ingestion/egress_status.jsonl`.

## §1. Cycle-31 branch-C context and operator directive (2) recap

Operator directive (2) [c31 dispatch]: *.googlevideo.com egress unblock
is imminent. When two consecutive `media_ok=true` rows land in
`data/ingestion/egress_status.jsonl`, the armed harness MUST fire the
pre-registered Path B ear plan without human intervention. This cycle
verifies the harness is READY, not that it fires immediately.

**Egress retry probe (top of cycle, non-blocking).**
`bash workspace/harvest_playlists.sh` invoked; result:

```
band 6: 0 files
band 5: 0 files
band 4: 0 files
```

*.googlevideo.com egress remains blocked. `data/ingestion/egress_status.jsonl`
carries no new `media_ok=true` rows added by this cycle beyond what was
already present. The trigger has NOT fired. Fixture-reinforcement work
proceeds as planned per the operator directive — this cycle is about
readiness.

**Trigger conditions (verbatim from `docs/ear_path_b_commitment.md` §7).**
When the two-consecutive-fresh-`media_ok=true` rule fires on
`data/ingestion/egress_status.jsonl`, the cycle-8 egress-ready machine
drives `IDLE → ARMED → TRIGGERED → HARVESTING → CHUNKING → CLASSIFYING
→ READY`. On `READY` (i.e. `data/ear/rated_ready.flag` present) AND
either `data/ear/trained_v1.flag` absent OR the ratings-manifest
content-hash differs from the hash stored inside `trained_v1.flag`,
the cycle-11 armed-harness extension fires `READY → TRAINING → TRAINED`
without human intervention.

## §2. Frozen 2-verdict rubric

Rubric committed to `docs/ear_armed_harness_fixture_rubric.md` BEFORE
any fixture extension landed and BEFORE any invocation of
`scripts/ear/sb_dry_run.py`. SHA-256:

```
ff853170f22aaa08e4dfa1d4656262fabd221fbbf405f72ba3f345236e12f689
```

Embedded verbatim as `rubric_hash` in
`data/ear/armed_harness_reinforcement/sb_dry_run_verdict.json`.
Cross-branch integration §47b + fixture case 10 both assert equality.

**FIXTURE_READY** iff: (1) all ≥12 fixture cases PASS; (2) AST-grep
clean (zero live-network imports across armed harness + egress-ready +
SB dry-run + fixture); (3) SB dry-run outputs byte-identical across two
fresh temp-dir runs; (4) all three SB metrics computable end-to-end;
(5) `promise_check` 0 ERRORs.

**FIXTURE_INSUFFICIENT** iff any of the above fail; a
`_manager/armed-harness-bug-deferred` ledger event names the specific
gap for cycle 32. This escape-hatch is intact but was not needed.

## §3. SB dry-run methodology and per-SB result summary

**Purpose:** verify each of the three c26-frozen Path B success bars is
*computable* end-to-end on the 55-clip M-CLASS-1 valset via the c22
synthetic-label protocol, WITHOUT touching rated audio. **This is a
computability check, not a real-label PASS.** The frozen thresholds
(SB1 margin > 0.5909; SB2 τ ≥ 0.4; SB3 detection ≥ 0.90) belong to
real-label calibration and are not re-derived here.

Script: `scripts/ear/sb_dry_run.py`. Interpreter guard
`/usr/bin/python3`; BLAS thread pins (OMP/MKL/OPENBLAS=1);
`torch.manual_seed(0)` per fold; SHA-256 tiebreak for the SB2 bootstrap
resamples; no top-level PRNG (SB3 delegates to the c6 leak-test which
uses `np.random.default_rng` with fixed seeds — accepted campaign
pattern for that read-only anchor).

### SB1 — MAE margin over the harder baseline

Recipe: `RECIPES[0]` (hash-noise family, salt `stab-audit-0`). 5-fold
stratified CV with fresh CORN heads (2052→128→ReLU→Dropout(0.3)→6),
Adam, LR=1e-3, WD=1e-3, 30 epochs.

| metric | value |
|---|---|
| `sb1_mae_corn` | 1.4727 |
| `majority_class_baseline_mae` | 1.3818 |
| `mean_integer_baseline_mae` | 1.4000 |
| `sb1_baseline_hard` (= min) | 1.3818 |
| **`sb1_margin`** | **−0.0909** |
| SB1 computable | **YES** (all fields finite) |

Interpretation: the synthetic hash-noise recipe produces a null-signal
label vector, so the CORN head cannot beat the majority-class baseline —
SB1 margin is negative. **This is expected on synthetic labels.** The
dry-run's assertion is that SB1 is *computable* (all three quantities
finite), NOT that it passes on synthetic labels. Real-label PASS/FAIL
belongs to the downstream cycle after egress unblock.

### SB2 — mean pairwise Kendall τ across 10 stratified bootstrap resamples

Recipe: `RECIPES[2]` (linear-projection family, salt `stab-audit-2`).
For each of 10 SHA-256-salted stratified bootstrap resamples (80% keep
per rating class), a fresh CORN head is trained on the resampled subset
and predictions computed on the full 55-clip set. Kendall τ-b (exact,
via `scripts/ear/stability_metrics.kendall_tau_exact`) is measured
pairwise across the 10 prediction vectors — 45 pairs.

| metric | value |
|---|---|
| `sb2_mean_tau` | 0.9159 |
| `sb2_per_resample_tau` (mean vs the other 9) | `[0.8670, 0.9115, 0.9146, 0.9206, 0.9274, 0.9192, 0.9279, 0.9247, 0.9274, 0.9193]` |
| `sb2_pairwise_tau_count` | 45 |
| SB2 computable | **YES** (all 10 finite; length 10) |

Interpretation: the linear-projection recipe has a strong internal
signal (a fixed coefficient vector on z-scored features), so the CORN
head learns a stable ranking across resamples. τ ≈ 0.92 across resamples
is high — again, this is a synthetic-label artifact and NOT evidence
that SB2 will PASS on real labels. The dry-run confirms the metric
plumbing is intact end-to-end.

### SB3 — leak-test detection rate at α=1.0 per leak type

Delegates to `scripts/ear/leak_test.run_experiments` (read-only c6
anchor) with the c22 planted-non-factor protocol; bounded parameters
for wall-time (`n_controls=4`, `n_splits=3`, `epochs=20`); base_seed
SHA-derived from a fixed salt `sb-dryrun-c31-sb3` for byte-determinism
across the two runs.

| leak_type | `sb3_detection_rate` @α=1.0 | `sb3_tau_per_leak_type` |
|---|---|---|
| artist | 1.0000 | 0.5419 |
| genre  | 0.9167 | 0.5969 |
| era    | 1.0000 | 0.2641 |

SB3 computable: **YES** (all three finite in [0, 1]).

Interpretation: at α=1.0, the leak detector fires reliably on all three
planted non-factors, matching the c6 protocol's design guarantee. Under
the reduced parameters used for wall-time, detection rates already meet
or exceed the 0.90 real-label threshold — this is a favorable indicator
that the leak-test pipeline will produce a well-formed real-label
answer, but is NOT itself a real-label PASS.

### Aggregate byte-determinism

Two independent runs of `scripts/ear/sb_dry_run.py --out-dir <tempdir>`
against the same feature cache produced byte-identical
`sb_dry_run_verdict.json`. SHA-256:

```
e7ed2c189aa5af2811dde7caaf59f35fcfbbf34a95ba1a24852d070393607e1a
```

Feature-cache aggregate SHA-256 (SHA of sorted `{clip_id: per-file-SHA}`
dict): `dd0df1fef41c16116ca48629ae16f740b4f1aba9bde0de8789707ef76ab70fe7`.

## §4. Fixture-case enumeration

`tests/test_ear_armed_harness_synthetic_trigger.py`: **19 cases (was 8;
+11 cycle-31 additions).**

| # | scenario | case name | verdict | notes |
|---|---|---|---|---|
| 1 | base | `test_cold_start_ready_holds_without_flag` | PASS | pre-c31 |
| 2 | base | `test_synthetic_flag_triggers_ready_to_trained` | PASS | pre-c31 |
| 3 | f | `test_content_hash_gate_prevents_redundant_training` | PASS | pre-c31 |
| 4 | base | `test_audio_missing_transitions_to_failed` | PASS | pre-c31; FAILED[training/audio_missing] |
| 5 | base | `test_atomic_state_write_survives_simulated_crash` | PASS | pre-c31 |
| 6 | g | `test_byte_deterministic_transitions_jsonl` | PASS | pre-c31 |
| 7 | d | `test_zero_live_network_ast_grep` | PASS | pre-c31 |
| 8 | d | `test_no_sidecar_nonfactor_imports` | PASS | pre-c31; c31 extended to include `sb_dry_run.py` |
| 9 | a | `test_ratings_manifest_content_hash_change_refires_training` | PASS | c31 new; TRAINED → forced_reset READY → TRAINING → TRAINED |
| 10 | b/SB1 | `test_sb1_computable_from_synthetic_dry_run` | PASS | c31 new |
| 11 | b/SB2 | `test_sb2_computable_from_synthetic_dry_run` | PASS | c31 new |
| 12 | b/SB3 | `test_sb3_computable_from_synthetic_dry_run` | PASS | c31 new |
| 13 | c | `test_mock_egress_unblock_probe_fires_full_state_chain` | PASS | c31 new; egress_ready machine transitions IDLE→TRIGGERED→HARVESTING→CHUNKING→CLASSIFYING→READY |
| 14 | d | `test_zero_live_network_ast_grep_covers_sb_dry_run` | PASS | c31 new; AST-grep extended to `sb_dry_run.py` + the fixture itself |
| 15 | e | `test_resumable_from_failed_training_loop` | PASS | c31 new; FAILED[training/loop] → TRAINING → TRAINED on retry |
| 16 | e | `test_resumable_from_failed_training_audio_missing_when_audio_returns` | PASS | c31 new |
| 17 | e | `test_resumable_from_failed_training_audio_missing_stays_failed_when_still_missing` | PASS | c31 new |
| 18 | f | `test_idempotent_repeat_scan_writes_bookkeeping_row_only` | PASS | c31 new; stricter than case 3 |
| 19 | g | `test_sb_dry_run_byte_determinism_x2` | PASS | c31 new; two independent temp-dir runs SHA-equal |

Full row-per-case machine table:
`data/ear/armed_harness_reinforcement/fixture_scenarios.tsv`.

## §5. Mock-egress-unblock probe: state-transition sequence with atomic-write verification

Case 13 authors a synthetic `mock_egress_status.jsonl` fixture with two
consecutive fresh `media_ok=true` rows (target `*.googlevideo.com`,
http_code 206, timestamps 12:00 and 12:15 UTC on 2026-08-29 with the
clock frozen at 12:20 UTC), then runs the cycle-8 `EgressReadyMachine`
against this fixture with mocked hooks (subclass of `SubprocessHooks`
that skips `super().__init__` and returns `HookResult(ok=True, …)` for
each of `run_harvest`, `run_chunker`, `run_classifier`,
`write_ready_flag` — **zero real subprocess.run**).

Recorded state transitions (also written to
`data/ear/armed_harness_reinforcement/state_transitions_verification.jsonl`):

| from_state | to_state | reason |
|---|---|---|
| IDLE | TRIGGERED | two consecutive fresh media_ok=true rows |
| TRIGGERED | HARVESTING | chain: start harvest |
| HARVESTING | CHUNKING | chain: harvest ok -> chunk |
| CHUNKING | CLASSIFYING | chain: chunk ok -> classify |
| CLASSIFYING | READY | chain: classify ok, ready flag written |

Atomic-write invariant: no `.tmp` turds visible in the state dir after
each transition. `state.json` fully-formed JSON, re-loadable by a fresh
machine instance. The state.json write uses
`tempfile.NamedTemporaryFile(dir=path.parent) + os.replace`, which is
POSIX-atomic on the same filesystem.

Note: `IDLE → ARMED → TRIGGERED` is the two-scan chain when one true
row arrives per scan; a single scan seeing both trues in the fixture
takes `IDLE → TRIGGERED` directly, which is the legal transition in the
c8 map (`TRANSITIONS[IDLE] = {ARMED, TRIGGERED}`). Case 13 exercises
this single-scan variant; a follow-up cycle can add a two-scan variant
if desired — it is not gated by the c31 rubric.

## §6. Zero-live-network isolation proof

AST-walk methodology (case 14, integration §47d, plus the pre-c31 case
7). `ast.parse` on each target file; walk collects `Import.names` +
`ImportFrom.module` (both full name and dotted-first-part). Assert
disjoint from:

```
{urllib, urllib2, urllib3, requests, socket,
 httpx, aiohttp, http, http.client}
```

Coverage table:

| target file | AST-grep clean |
|---|---|
| `scripts/ear/train_armed_harness.py` | ✓ |
| `scripts/ear/sb_dry_run.py` | ✓ (c31 new) |
| `tests/test_ear_armed_harness_synthetic_trigger.py` | ✓ (c31 new) |
| `scripts/egress_ready/state.py` | ✓ |
| `scripts/egress_ready/cli.py` | ✓ |
| `scripts/egress_ready/subprocess_hooks.py` | ✓ (only stdlib `subprocess` — not a network lib) |
| `scripts/egress_ready/trigger.py` | ✓ |

Also `sidecar_nonfactor` import negation is asserted across the same
target set (case 8, extended in c31 to include `sb_dry_run.py`; also
§47e).

## §7. Verdict

**FIXTURE_READY.**

- 19/19 fixture cases PASS (≥12 required).
- SB1/SB2/SB3 all computable end-to-end on the 55-clip valset.
- Byte-determinism × 2 verified (verdict JSON SHA-equal across two
  independent temp-dir runs).
- Zero live-network imports across armed harness + egress_ready +
  SB dry-run + fixture.
- Rubric SHA-256 (`ff853170…12f689`) committed BEFORE fixture
  extensions landed; embedded in `sb_dry_run_verdict.json.rubric_hash`
  and cross-checked by case 10 + integration §47b.
- All c22 stability harness + c6 feature cache + c26/c27/c28/c29/c30
  analytical utilities untouched (§47g anchor asserts).
- Cycle-8 armed-harness state machine (`scripts/ear/train_armed_harness.py`,
  `scripts/egress_ready/*`) NOT modified.
- No implementation bugs discovered in the read-only anchors during
  fixture extension — no `_manager/armed-harness-bug-deferred` event
  needed.

**No real-label-firing gap surfaced.** The armed harness is ready to
fire the pre-registered Path B ear plan whenever the two-consecutive-
`media_ok=true`-row trigger arrives.

## §8. Post-egress-unblock validation checklist

When the two-`media_ok=true` trigger actually fires against live rated
audio in a downstream cycle, the auditor MUST confirm:

1. **State-machine sequence.** `data/egress_ready/state/transitions.jsonl`
   shows IDLE → (ARMED →) TRIGGERED → HARVESTING → CHUNKING →
   CLASSIFYING → READY with all four subprocess hooks returning
   `ok=True`, followed by READY → TRAINING → TRAINED (or FAILED[…]
   with a diagnostic).
2. **Content-hash gate.** `data/ear/trained_v1.flag` records the
   SHA-256 of `corpus/ratings/ratings_manifest.tsv` at training time.
   A no-op scan after training is IDLE for the harness (single "noop"
   row in transitions.jsonl).
3. **SB1 real-label PASS/FAIL.** Load `training_result.json.mean_mae`
   from the training-loop output; compare to
   `min(majority_class_baseline_mae, mean_integer_baseline_mae)`
   derived from `corpus/ratings/ratings_manifest.tsv` per the c26
   §3 computation. PASS iff `baseline_hard − mean_mae > 0.5909`.
4. **SB2 real-label PASS/FAIL.** Run 10 stratified bootstrap resamples
   over the 80-song rated set (80% keep per rating class);
   fit-and-predict CORN heads; compute mean pairwise Kendall τ.
   PASS iff mean τ ≥ 0.4.
5. **SB3 real-label PASS/FAIL.** Run the c6 leak-test harness against
   real ratings with actual artist metadata (parsed from title;
   see c26 §4 for the exact protocol) + deferred genre/era per c26
   §4's honest-deferral note. PASS iff detection rate ≥ 0.90 at α=1.0
   per leak type.
6. **Anchor SHA re-verification.** `data/ear/features/*.npy` aggregate
   SHA unchanged from c31 baseline
   (`dd0df1fef41c16116ca48629ae16f740b4f1aba9bde0de8789707ef76ab70fe7`);
   c22 stability harness + c26 α (0.7469387071101908) unchanged.
7. **Fixture-suite regression.** All 19 fixture cases still PASS after
   the live firing; no new implementation drift.
8. **Ledger events.** A `_manager/egress-unblock-observed` (if not
   already emitted this cycle) + `M-EAR-1/first-real-label-training`
   verdict roll-up + housekeeping pair per c30 codified pattern.

If any of (3)/(4)/(5) fail on real labels, cycle 32+ opens a
`M-EAR-1/real-label-failure-analysis` sub-milestone under M-EAR-1 —
this is a legitimate research outcome per c26's escape-hatch integrity
clause. It does NOT retroactively invalidate the c31 FIXTURE_READY
verdict, which only asserts computability.
