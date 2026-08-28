---
created: 2026-08-28T11:30:00Z
cycle: 26
run_id: run-2026-08-28T040704Z
agent: worker
milestone: _manager/M-EAR-1-path-B-commit
fork: 8f3344880d29
clone: 1
---

# M-EAR-1 Path B Commitment — cycle 26

**Status: cycle 26 commits Path B.** The M-EAR-1 milestone is deferred to
post-egress real-label calibration. Path A is closed as a campaign
anti-pattern. This document is durable: it must survive cycle 27+ readers
unchanged as the commit that shapes real-label training whenever egress
opens.

---

## §1. Three-audit exhaustion evidence

Three orthogonal design axes have been audited under the frozen cycle-22
`stability_audit.py` harness (SHA-anchored at run time) on the N=55
M-CLASS-1 synthetic-label valset. All three failed the credibility rubric.

| cycle | milestone / variant | C1 verdict | C2 verdict | C3 verdict | τ observed | MAE observed vs cycle-6 anchor (0.891) | pre-registered rule fired |
|---|---|---|---|---|---|---|---|
| 22 | `M-EAR-1/synthetic-label-stability-audit` (CORN cycle-6 chassis) | **FAIL** — 0.891 below observed min 0.909; well below envelope [1.032, 2.082] | **FAIL** — mean τ = 0.059 (« 0.7 threshold) | PASS — byte-deterministic ×2 | 0.059 | 0.891 vs env [1.032, 2.082] | rule fired: c23 opens head-regularization axis |
| 23 | `M-EAR-1/head-regularization-audit` — CORN-ridge (L2 + Dropout 0.5) | FAIL (C1') | FAIL (C2') — τ ≈ 0.05× cycle-6 | PASS | ≪ 0.4 | above cycle-6 anchor, ~5× | rule fired: c25 opens feature-representation axis |
| 23 | `M-EAR-1/head-regularization-audit` — CORN-bottleneck (32-D) | FAIL (C1') | FAIL (C2') | PASS | ≪ 0.4 | ~5× worse | (same rule as ridge) |
| 23 | `M-EAR-1/head-regularization-audit` — CORN-frozen-projector (PCA-64) | FAIL (C1') | FAIL (C2') | PASS | ≪ 0.4 | ~5× worse | (same rule as ridge) |
| 25 | `M-EAR-1/feature-representation-audit` — HEUR-only (D_in=4) | **PASS (C1')** — **but underdetermined-regressor signature, not a Path A rescue** | FAIL (C2') — mean τ = −0.076, bimodal [−0.958, +0.951] | PASS | −0.076 | inside envelope by artifact of 4-feature fit space | rule fired: c26 commits Path B |
| 25 | `M-EAR-1/feature-representation-audit` — PANNs-only (D_in=2048) | FAIL (C1') | FAIL (C2') — mean τ = +0.006 | PASS | +0.006 | above cycle-6 anchor | (same rule) |
| 25 | `M-EAR-1/feature-representation-audit` — VGGish-only (D_in=128) | **DEFERRED** — cache absent; not enough to keep Path A open | DEFERRED | DEFERRED | — | — | R3 legitimately deferred; does not gate the Path B commit |

**Sources (byte-anchored):**

- `docs/ear_stability_audit_report.md` — cycle-22 frozen thresholds C1/C2/C3, 10 recipe salts, observed MAE envelope [5th=1.032, 95th=2.082], min 0.909, cycle-6 anchor 0.891, mean τ 0.059.
- `docs/ear_head_regularization_audit_report.md` — cycle-23 C1'/C2'/C3'.
- `docs/ear_feature_representation_audit_report.md` — cycle-25 HEUR-only + PANNs-only.
- `data/ear/head_regularization_audit/frontier_summary.json` — cycle-23 numeric frontier.
- `data/ear/feature_representation_audit/frontier_summary.json` — cycle-25 numeric frontier.
- `data/ear/stability_audit/per_recipe_mae.tsv` — 10 per-recipe MAE values (basis for the IQR in §3).

The cycle-25 HEUR-only C1' PASS is the **underdetermined-regressor
signature** per cycle-25 clone-1 §7.1: with D_in=4 features and 55 clips,
the head can trivially fit any per-recipe ordering, picking a different
direction each time. It is not evidence that a 4-D feature family is a
viable ear chassis; it is evidence that C1' loses discriminating power
at very small D_in. Do not read it as a Path A rescue.

## §2. Path B rationale — vs. corpus expansion, vs. architecture change

Three options were on the table for cycle 26. The commit chooses **Path
B**; the other two are honestly deferred with named reasons.

### Path B (CHOSEN) — defer all ear calibration to post-egress real labels
- **Rationale**: three orthogonal axes exhausted under identical harness,
  all producing negative findings. The cycle-25 pre-registered rule
  ("no-representation-passes → cycle 26 commits Path B") has fired.
  Incremental cost is smallest. Falsifiability is highest — real labels
  become available on egress unblock, and the frozen success bars in §3
  will produce a clean verdict.
- **Anti-pattern discipline**: reopening the chassis, head, or feature
  slice without a **fundamentally distinct probe** (not a fourth variant
  of any of the three axes already closed) is now forbidden under the
  cycle-26 anti-pattern set.

### Corpus expansion (DEFERRED) — expand N=55 synthetic → N=200+ synthetic
- Rationale for deferral: still synthetic labels. Does not answer the
  question the three audits were trying to answer (does real signal exist
  under a credible chassis?). A larger synthetic N might expose more
  chassis brittleness, but it cannot escape the "no real signal → noise
  ceiling" problem. Blocked on rated audio anyway to be meaningful.

### Architecture change (DEFERRED) — replace CORN with a non-ordinal head
- Rationale for deferral: open-ended and premature. Nothing in the three
  audits points at the head *shape* as the bottleneck — the frontier plot
  puts the bottleneck at the label-vs-feature information channel, which
  a different head shape does not repair. Waiting for real labels first
  is the cheaper falsifiability path; if real labels also fail SB1/SB2,
  that is the moment to consider architecture change with concrete
  motivation.

**Commit statement.** Cycle 26 commits Path B. The M-EAR-1 milestone
remains blocked on rated-audio availability. Path A is closed as an
anti-pattern; do not reopen it without a fundamentally distinct probe.

## §3. Three frozen real-label success bars

Each bar has (a) a computable definition, (b) a numeric threshold, (c) a
PASS/PARTIAL/FAIL protocol. **No softening.** No backfill of thresholds
after data arrives.

### Numeric constants (derived, not fabricated)

Computed from `data/ear/stability_audit/per_recipe_mae.tsv` (N=10 recipes;
cycle-22 harness output — read-only anchor) and `corpus/ratings/ratings_manifest.tsv`
(80 songs; band distribution H=30, M=30, L=20 with rating values 6, 5, 4).

```
per_recipe_mae (sorted): [0.9091, 1.1818, 1.2000, 1.3091, 1.4545, 1.5273,
                          1.6545, 1.8727, 1.9818, 2.1636]
Q1  = np.percentile(mae, 25) = 1.2272727273
Q3  = np.percentile(mae, 75) = 1.8181818182
IQR = Q3 - Q1                = 0.5909090909   ← frozen SB1 IQR threshold

label distribution: {4: 20, 5: 30, 6: 30}   (mean = 5.125)
majority-class predictor: pred = argmax_count(labels)
    Both 5 and 6 have count 30; `collections.Counter.most_common(1)`
    picks the last-encountered tied key, which for insertion order
    [4,5,6] is `6`. MAE(pred=6) = (20·2 + 30·1 + 30·0) / 80 = 70/80 = 0.8750
mean-integer predictor:   pred = round(mean(labels)) = round(5.125) = 5
    MAE(pred=5) = (20·1 + 30·0 + 30·1) / 80 = 50/80 = 0.6250

min(majority-class MAE, mean-integer MAE) = 0.6250   ← the harder baseline
SB1 margin threshold: CORN MAE must be < 0.6250 - 0.5909 = 0.0341
```

### SB1 — MAE beats both baselines by margin > IQR

- **Definition.** `margin_SB1 = min(majority_class_MAE, mean_integer_MAE) − CORN_MAE_5foldCV_real`
- **Threshold.** `IQR_MAE = 0.5909090909` (frozen).
- **Protocol.**
  - **PASS** iff `margin_SB1 > IQR_MAE` (i.e. `CORN MAE < 0.0341`).
  - **PARTIAL** iff `0 < margin_SB1 ≤ IQR_MAE`.
  - **FAIL** iff `margin_SB1 ≤ 0`.
- **Honesty caveat (mirrored in §5).** The PASS bar is deliberately strict.
  Because the label distribution is narrow (3 bands, 80 songs), the
  mean-integer baseline is already at 0.625 MAE, and requiring CORN to beat
  it by 0.5909 places the PASS bar at ~0.03 MAE — essentially near-perfect
  ordinal recovery. **The PARTIAL band is the realistic "beats baselines
  meaningfully but does not clear the synthetic-chassis instability
  envelope" outcome and should be treated as the ordinary success signal
  for a first real-label evaluation.** Do not silently promote PARTIAL to
  PASS; the whole point of freezing the bar is that it is a stable
  reference across cycles.

### SB2 — Rank stability under real-label bootstrap

- **Definition.** 10 stratified bootstrap resamples of the 80 rated songs
  (stratified by rating band so each resample preserves the 20/30/30 split).
  For each resample, run 5-fold stratified CV of the cycle-6 CORN chassis;
  record the 80-song predicted-rank vector. Compute mean pairwise Kendall
  τ across all 45 pairs of the 10 predicted-rank vectors.
- **Threshold.** `mean_pairwise_tau ≥ 0.4` (frozen at cycle-23 relaxed
  threshold; do NOT soften to 0.2 or 0.3 after data arrives — that would
  be the same backfill anti-pattern cycle-23 already refused).
- **Protocol.**
  - **PASS** iff `mean_tau ≥ 0.4`.
  - **PARTIAL** iff `0.2 ≤ mean_tau < 0.4`.
  - **FAIL** iff `mean_tau < 0.2`.
- **Reference point.** Cycle-22 chassis-as-is on synthetic labels gave
  τ = 0.059; real labels are expected to score much higher if any real
  signal exists in the features. If real-label τ lands near 0.059, that
  confirms the noise ceiling and closes M-EAR-1 as invalidated.

### SB3 — Non-factor leak protocol on real non-factors

- **Definition.** Per cycle-6 leak-test protocol at α=1.0 (see
  `scripts/ear/leak_test.py` — validated cycle-6, feature cache read-only).
  Plant each non-factor at strength α ∈ {1.0, 0.5, 0.1}; two-sided η²
  statistic `S = max(S_model, S_resid)`; τ_detect calibrated from ≥20
  no-leak controls per leak type.
- **Threshold.**
  - `detection_rate(leak_type) ≥ 0.90` at α = 1.0
  - AND `false_positive_rate(leak_type) ≤ 0.10`.
- **Protocol.**
  - **PASS** iff both thresholds hold for **every** non-factor.
  - **PARTIAL** iff some non-factor has `detection < 0.90` but **no**
    non-factor has `FPR > 0.10`. Interpretation: the leak detector is
    under-powered but not producing false alarms — safe to proceed with
    a caveat.
  - **FAIL** iff **any** non-factor has `FPR > 0.10`, **or** any non-factor
    has `detection < 0.90` **while** the chassis is showing SB1 PASS.
    Interpretation: the head is fitting non-factors (the whole point of
    the leak test).

## §4. Non-factor leak protocol on real artist / genre / era

**Verified at run time** — the ratings manifest was inspected on
2026-08-28 and has columns:

```
rating   playlist_id   video_id   title   duration_s   url
```

There is **no explicit `artist`, `genre`, or `era` column.** All three
non-factors must be derived — some via straightforward parsing, some with
honest deferrals to post-egress metadata harvest. The three columns and
their derivation rules follow.

### 4.1 Artist — derived from `title` by regex parse

- **Derivation rule.** For each row, parse `title` with the regex
  `^(?P<artist>[^-—]+?)\s*[-—]\s*(?P<song>.+)$` and strip whitespace.
  The first two rows of the manifest confirm this format:
  - `Justin Bieber - YUKON (Live From The 68th Grammy Awards / 2026)` → artist=`Justin Bieber`
  - `Jungle - Candle Flame (feat. Erick The Architect) (Official Video)` → artist=`Jungle`
- **Fallback.** If the regex does not match (e.g. no `-`/`—` separator),
  set `artist = "__UNPARSED__" + video_id[:6]` so each unparseable row
  becomes its own singleton bucket (which the leak test cannot exploit).
  Report the fraction of unparseable rows in the SB3 output; if it
  exceeds 0.10, the leak-test on artist is under-powered and the artist
  channel must be marked PARTIAL by construction.
- **Bucket definition.** Case-insensitive stripped-string equality after
  removing "The " prefix and trailing "feat." clauses (regex
  `\s*[\(\[]feat\..*$`, i.e. anything after `(feat.` or `[feat.`). This
  gives a deterministic canonical artist label per row.
- **Post-egress refinement (optional).** If yt-dlp metadata harvest is
  eventually run, replace the title-parse with the YouTube channel-id
  field. This is a strict refinement; the regex-parse is the durable fallback.

### 4.2 Genre — DEFERRED with an honest reason

- **Why not `playlist_id`.** The three playlist IDs in the manifest are
  **perfectly aliased with the three rating bands**:
  ```
  PLoxlz_x73gZNv_Ae3HP2b-uhjQNnb5YnN  → all 20 rows with rating=4
  PLoxlz_x73gZO1UKfmdIRRvnJBiJkQd53l  → all 30 rows with rating=6
  PLoxlz_x73gZPwSJkctwHkzMT6RpFnZqXQ  → all 30 rows with rating=5
  ```
  Using `playlist_id` as a genre proxy would trivially "leak" 100% at
  α=1.0 — but that would be measuring the direct rating-to-playlist alias,
  not a genuine genre channel. Reporting this as a leak would be an
  interpretive failure. **Do not use `playlist_id` for the genre leak
  test.**
- **Deferred derivation.** Real genre must come from either
  (a) yt-dlp metadata `categories` / `tags` fields on each video, or
  (b) an audio-classifier tagger (e.g. PANNs on the harvested clips).
  Both require rated audio to have been harvested. The SB3 genre channel
  therefore evaluates **only after harvest + tagger inference**, and the
  post-trigger checklist in §8 gates SB3 genre on presence of a
  `corpus/ratings/genre_tags.tsv` (rows: `video_id`, `genre`).
- **Interim safe posture.** If SB3 is computed before genre tags are
  populated, the genre channel is reported as `DEFERRED (no source)` and
  the overall SB3 verdict is capped at PARTIAL until it is completed.

### 4.3 Era — DEFERRED to post-egress metadata

- **Why not `duration_s`.** Duration is orthogonal to era in general
  (a 2-minute 1965 song and a 2-minute 2025 song both exist). Using it as
  an era proxy would be measuring song-length variance, not release-year
  variance. **Do not use `duration_s` for the era leak test.**
- **Deferred derivation.** Real era comes from yt-dlp metadata `upload_date`
  (best-available proxy for release year within the constraints of what
  YouTube publishes) or, if the harvest fetches the actual media, from
  `format.year` or `release_date` fields on the raw video.
- **Bucket rule (frozen for when data arrives).** 5-year bins anchored at
  1960: `[1960..1964, 1965..1969, ..., 2025..2029]`. Rows whose year is
  unresolved land in bucket `__unresolved__`; if that bucket contains
  > 10% of rows, era leak-test is under-powered and marked PARTIAL by
  construction.
- **Interim safe posture.** Same as genre — SB3 era is reported as
  `DEFERRED (no source)` and caps the overall verdict at PARTIAL until
  populated.

### 4.4 Consequence for SB3 at cycle-of-egress-unblock

The **earliest** SB3 verdict that will be available on egress unblock is:

- **artist channel**: computable immediately from titles.
- **genre channel**: computable after yt-dlp metadata harvest OR
  PANNs-tagger inference on the harvested clips.
- **era channel**: computable after yt-dlp metadata harvest.

The post-trigger checklist in §8 makes this explicit: if only artist is
available at first, publish SB3 verdict as `artist=PASS/PARTIAL/FAIL,
genre=DEFERRED, era=DEFERRED`, do not claim overall PASS.

## §5. Corpus-size honesty caveat + corpus-expansion-ticket template

### 5.1 Honesty caveat

**80 rated songs is close to the 55-clip synthetic valset — proximity
ratio 80/55 ≈ 1.45**. The same corpus-size signal that cycle-25 auditor
named ("small-N chassis brittleness produces C2 failure") could still
bite real-label evaluation, especially for SB2 (bootstrap-τ stability).

**Frozen honest consequence.** If SB2 FAILS at 80 songs, the honest
response is to **request corpus expansion**, not to redesign the chassis.
Path A is closed. The cycle-26 anti-pattern set forbids reopening chassis
/ head / feature-slice exploration in response to a bootstrap-τ FAIL.

Additionally, SB1's threshold (`CORN MAE < 0.034`) is dominated by
IQR-shape from the synthetic-label chassis instability; a PARTIAL result
on SB1 that comfortably beats both baselines but does not clear the IQR
is a strong signal — do not read PARTIAL as failure.

### 5.2 Corpus-expansion-ticket template

To be instantiated by any cycle that receives a bootstrap-τ FAIL on 80
rated songs. Values in `<>` are placeholders.

```yaml
milestone_id: _manager/M-EAR-1-corpus-expansion-request
cycle: <N>
run_id: <RUN_ID>
agent: worker
status: action-required
confidence:
  level: high
  rationale: |
    Real-label SB2 evaluation on N=80 produced mean_tau = <VALUE>
    (< 0.4 threshold, and < 0.2 → FAIL band). Cycle-26 §5 anti-pattern:
    do not respond by redesigning the chassis. Corpus expansion is the
    only Path B-compatible response.
  assessor: worker
narrative: |
  Path B SB2 evaluation invalidated on N=80.
  Current: N=80 songs, band distribution H=30 (rating 6), M=30 (rating 5),
    L=20 (rating 4). Observed mean pairwise τ = <VALUE>.
  Target: N such that a bootstrap-power calculation projects
    mean_tau ≥ 0.4 at the observed per-clip band-variance level with
    probability ≥ 0.80. Compute this power calculation via
    `scripts/ear/path_b_success_bar_reference.py --power-calc`
    (armed-not-fired; see §6 below).
  Rated-song acquisition cost estimate: <yt-dlp minutes> +
    <human-rating minutes / song>.
  Timeline: <estimated cycles to acquire + re-rate the delta>.
  Reference-request: extend `corpus/ratings/ratings_manifest.tsv` and
    invoke egress-ready harness with the same content-hash gating; SB1/SB2/SB3
    re-run automatically on retrain trigger.
```

Any cycle instantiating this ticket must also emit an ordinary
`_manager/M-EAR-1-corpus-expansion-request` in-progress event with the
concrete values populated. The template lives here so cycle-27+ authors
can instantiate deterministically without re-inventing.

## §6. Armed-harness synthetic-fixture verification

**Deliverable.** `tests/test_ear_armed_harness_synthetic_trigger.py` —
plain-assert suite (no pytest), zero live network, all fixtures on-disk
synthetic files. Test count: **8 cases** (satisfies brief's ≥6 with two
extras for AST safety).

The armed-harness module `scripts/ear/train_armed_harness.py` exists on
disk (verified 2026-08-28; cycle-11 delivery, milestone `M-EAR-1/armed-harness`).
Its state entry point is `READY` (not `IDLE` — the egress_ready state
machine terminates in READY and this harness picks up from there).
State set: `{READY, TRAINING, TRAINED, FAILED}` with FAILED carrying a
`failed_stage` field (`training/loop` or `training/audio_missing`).

**Test cases (all runnable, none skipped):**

1. `test_cold_start_ready_holds_without_flag` — fresh state, no `rated_ready.flag` present; harness stays READY with a `noop` row in `transitions.jsonl`.
2. `test_synthetic_flag_triggers_ready_to_trained` — write `data/ear/rated_ready.flag` + synthetic manifest fixture + mocked audio; step harness through READY → TRAINING → TRAINED with `TrainingHooks` overridden by a stub that returns `TrainingHookResult(ok=True, mean_mae=0.5)`.
3. `test_content_hash_gate_prevents_redundant_training` — with `trained_v1.flag` already present recording the same manifest content-hash, a second scan stays TRAINED (writes a `noop` row).
4. `test_audio_missing_transitions_to_failed` — manifest present but the fixture `.wav` files under `clips_dir` are absent; transitions to `FAILED[training/audio_missing]`, resumable.
5. `test_atomic_state_write_survives_simulated_crash` — after a successful transition, ensure the `state.json` was written via tempfile + `os.replace` (no partial writes visible on filesystem; state re-loads cleanly on re-init).
6. `test_byte_deterministic_transitions_jsonl` — run the full flag → TRAINED sequence twice under fresh temp dirs (with the clock frozen and `evidence.manifest_sha256` as the only identity), hash both `transitions.jsonl` files, assert equal.
7. `test_zero_live_network_ast_grep` — AST-parse `scripts/ear/train_armed_harness.py` and every module under `scripts/egress_ready/`; assert **zero** imports of `urllib`, `requests`, `socket`, `httpx`.
8. `test_no_sidecar_nonfactor_imports` — AST-parse the same modules; assert **zero** imports of `scripts.classifier.sidecar_nonfactor`.

Test invocation:

```
PYTHONPATH=.:/home/user/human-in-a-loop/long-exposure /usr/bin/python3 \
    tests/test_ear_armed_harness_synthetic_trigger.py
```

**Verification result: 8/8 GREEN** (see cross-branch integration §38 for
the invariant table).

## §7. Trigger conditions

The full chain reactivates on the exact `data/ingestion/egress_status.jsonl`
pattern:

1. **Two consecutive rows with `media_ok=true`.** This is the cycle-1
   `M-INGEST-1/egress-probe` spec — a single true row is insufficient
   (guard against transient reachability).
2. **Both rows must be fresh** per the cycle-8 egress-ready-automation
   semantics — meaning the newer of the two rows has a timestamp
   monotonically greater than any prior `arming_started_at` state.
   Stale-row-does-not-count is exercised in the egress-ready test suite
   (`test_stale_row_does_not_count`).
3. **On trigger, the chain fires in order**:
   ```
   egress-ready ARMED → TRIGGERED → HARVESTING → CHUNKING → CLASSIFYING → READY
     (writes data/ear/rated_ready.flag with ratings_manifest content-hash)
   armed-harness READY → TRAINING → TRAINED
     (writes data/ear/trained_v1.flag with the same content-hash)
   ```
4. **Content-hash gating** on `data/ear/trained_v1.flag` prevents redundant
   retraining if the same manifest content-hash is presented again
   (idempotent noop). A manifest edit (any byte change) forces retrain
   via the `retrain: manifest hash changed` transition (documented in
   `scripts/ear/train_armed_harness.py` line 384).

## §8. Post-trigger validation checklist

Executable checklist for the cycle in which egress unblocks. Every step
is a **gated commit** — do not proceed to step N+1 until step N returns
green.

1. **Egress consistency.** Verify at least two consecutive `media_ok=true`
   rows in `data/ingestion/egress_status.jsonl` before proceeding. Reject
   if the newer row is not strictly after the older row's timestamp.
2. **Harvest completion.** Confirm `data/ear/rated_ready.flag` is present
   AND its recorded `ratings_manifest_content_hash` equals
   `sha256(corpus/ratings/ratings_manifest.tsv)`.
3. **Training completion + determinism.** Fire
   `scripts/ear/train.py` via harness; verify `training_result.json`
   and `corn_head_v1.pt` are byte-identical under a fresh temp-dir
   second run (with single-threaded BLAS pins + torch.manual_seed(0)).
4. **SB1 evaluation.** Run
   `scripts/ear/path_b_success_bar_reference.py --sb 1`
   → real-label MAE vs both baselines vs 0.5909 IQR threshold. Emit
   PASS/PARTIAL/FAIL verdict.
5. **SB2 evaluation.** Run
   `scripts/ear/path_b_success_bar_reference.py --sb 2`
   → 10-bootstrap × 5-fold τ, mean_tau vs 0.4 threshold. Emit verdict.
6. **SB3 evaluation.** Run
   `scripts/ear/path_b_success_bar_reference.py --sb 3`
   → artist / genre / era leak-test at α=1.0. **If genre or era source
   is DEFERRED (no yt-dlp metadata harvest yet)**, mark those channels
   DEFERRED and cap the overall SB3 verdict at PARTIAL — do NOT claim
   overall PASS.
7. **Combined verdict.** Publish `data/ear/path_b_evaluation.json`
   combining SB1/SB2/SB3. Decision rules:
   - **All three PASS** → roll `M-EAR-1` parent to `validated/high`.
   - **Any FAIL** → roll `M-EAR-1` to `invalidated/high` OR (per §5)
     instantiate the corpus-expansion-ticket if SB2 was the failure and
     the FAIL was under-powered (τ ∈ [0.2, 0.4) with high per-clip band
     variance).
   - **All PARTIAL** → roll `M-EAR-1` to `in-progress/medium` with an
     explicit rationale document, propose a specific next probe.
8. **Anti-pattern audit.** Confirm no chassis / head / feature-slice
   changes were made in response to the FAIL; only the corpus-expansion
   ticket path is legal per §5.

---

## Appendix — reproducibility

- **Recompute IQR + baselines:** `/usr/bin/python3 tools/_compute_iqr_and_baselines.py`.
- **Ratings-manifest inspection:** `head -1 corpus/ratings/ratings_manifest.tsv` — expected 6 columns `rating\tplaylist_id\tvideo_id\ttitle\tduration_s\turl`.
- **Armed harness test:** `PYTHONPATH=.:/home/user/human-in-a-loop/long-exposure /usr/bin/python3 tests/test_ear_armed_harness_synthetic_trigger.py`.
- **Cross-branch §38:** `PYTHONPATH=.:/home/user/human-in-a-loop/long-exposure /usr/bin/python3 tests/test_integration_cross_branch.py`.

Cycle 26, fork 8f3344880d29, clone 1. `run_id = run-2026-08-28T040704Z`.
