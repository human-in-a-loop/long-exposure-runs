---
created: 2026-08-29T17:20:00Z
cycle: 47
run_id: run-2026-08-28T040704Z
agent: worker
milestone: M-EAR-1/real-label-training-v2.1
---

# M-EAR-1/real-label-training-v2.1 — 50-control SB3 re-verdict (cycle 47, clone-0, Branch A)

**Verdict.** `EAR_v2p1_STABLE_FPR_PASS`, mapping to `EAR_v2p1_PARTIAL_WITH_SB3_PASS`.

## §1 SB3 pass/fail decomposition

Under c26 Path B (`docs/ear_path_b_commitment.md` §3), SB3 is defined by
two axes measured against separate thresholds. The v2.1 result:

| SB3 axis                | Threshold          | Result at 50 controls | Status |
|-------------------------|--------------------|-----------------------|--------|
| Detection (F1 pooled-var, α=1.0) | ≥ 0.90 | 1.000 (both runs)       | **PASS** (unchanged from c46) |
| FPR (90th-pct null tail) | ≤ 0.10             | 0.100 (both runs)       | **PASS** (byte-deterministic) |
| Combined SB3 verdict     | detection ∧ FPR    | 1.000 ∧ 0.100          | **PASS**                     |

**The FPR value 0.100 reproduces byte-deterministically across two fresh
`tempfile.mkdtemp()` runs.** SHA-256 of `sb3_50ctl_verdict_v2p1.json` is
byte-equal across the two runs: `c5add489eace0a6d3772307ef9ec2d8797a8b75ee49b16f80c73d4f99aacb140`.
Verdict `EAR_v2p1_STABLE_FPR_PASS` fires per the frozen rubric.

Under c45's PARTIAL clause, SB2 τ improvement over v1 continues to fire
(v1 mean τ = -0.099 → v2 mean τ = -0.031 = +0.067 improvement), so the
mapping label is `EAR_v2p1_PARTIAL_WITH_SB3_PASS`: SB3 has PASSed on both
axes, but SB1 (clip-level margin) and SB2 (mean pairwise Kendall τ) still
fall short of their c26 thresholds.

## §2 c46 methodology-improvement chain

The v2.1 result completes a three-step measurement-methodology chain that
began in c37:

1. **c37 F1 pooled-variance statistic** replaced the c6 `max(S_model, S_resid)`
   two-sided η² statistic; the new statistic pools across artist buckets
   rather than reporting the max, and this closed the c6 fallback
   statistic's known bias on singleton-artist populations. Ledger event:
   `M-EAR-1/real-label-training-v1/leak-statistic-lifted-clone-0`
   (c38 clone-0 retroactive naming).
2. **c38 leak-lift plumbing** wired `f1_pooled_variance_statistic` into
   `scripts/ear/leak_test.py` as `STATISTIC_VERSION = "F1_pooled_variance_v1"`
   and made it the SB3 statistic across v1/v2/v2.1 verbatim.
3. **c46 25 → 50 control widening** measured what happens to the SB3 null
   distribution when the number of SHA-derived null artist-permutations
   is doubled from 25 to 50. The observed effect: 25-ctl FPR 0.120
   → 50-ctl FPR 0.100. The observed 50-ctl value sat exactly at the
   FPR threshold, leaving open the question of whether it was a
   boundary-tip artifact of finite-controls noise.
4. **c47 v2.1 re-verdict** (this cycle) proves the 0.100 result is
   byte-deterministic across two fresh temp-dir runs and gives SB3
   its first PASS component alongside its unchanged detection PASS.

## §3 Corpus caveat

The rated corpus is **43 of 80 songs**, unchanged from c45. Bands
distribution: 10 band-4 + 10 band-5 + 13 band-6 + 10 band-7 = 43 songs
= 252 clips at c22 30 s / 5 s-overlap chunker settings. The v2.1 model
and verdict both carry the `preview_partial_corpus_v2p1` label
prominently. Corpus expansion to the full 80-song target remains the
highest-leverage c48+ handoff. The v2.1 verdict is credible for the
on-disk 43/80-song corpus but not calibrated to the full 80-song target.

## §4 Byte-determinism × 2 evidence table

All determinism gates use fresh `tempfile.mkdtemp()` CWDs plus the
brief-mandated env pins (BLAS pins + `PYTHONHASHSEED=0` +
`SOURCE_DATE_EPOCH=1756463424` + `TZ=UTC` + `LC_ALL=C.UTF-8` +
`torch.manual_seed(0)`).

| Artifact                              | Run 1 SHA-256                                                    | Run 2 SHA-256                                                    | Equal |
|---------------------------------------|-------------------------------------------------------------------|-------------------------------------------------------------------|-------|
| `corn_head_v2p1.pt`                   | `43cd7045ac6835baa34a0b714ae91270d65dc62765329c0e5150ce0a3cd62b17` | `43cd7045ac6835baa34a0b714ae91270d65dc62765329c0e5150ce0a3cd62b17` | ✅    |
| `training_result_v2p1.json`           | `a030ef1611a1754ebab6106a48374d8e6666965fd9e56ab1b26f9d1fefcd9d2f` | `a030ef1611a1754ebab6106a48374d8e6666965fd9e56ab1b26f9d1fefcd9d2f` | ✅    |
| `sb3_50ctl_verdict_v2p1.json`         | `c5add489eace0a6d3772307ef9ec2d8797a8b75ee49b16f80c73d4f99aacb140` | `c5add489eace0a6d3772307ef9ec2d8797a8b75ee49b16f80c73d4f99aacb140` | ✅    |

## §5 c26 threshold values unchanged; c45 v2 verdict unchanged

All three c26 Path B thresholds are unchanged in v2.1:

- SB1 margin > **0.5909** (c22 recipe-envelope IQR).
- SB2 mean pairwise Kendall τ ≥ **0.4** (c23 relaxed rubric).
- SB3 detection ≥ **0.90** at α=1.0 AND FPR ≤ **0.10**.

`data/ear_v2/verdict.json` was **not modified** by v2.1. The c45 v2 verdict
stands at `EAR_v2_PARTIAL` (per c46 mapping-clarified adjudication).
v2.1 publishes a NEW peer verdict at `data/ear_v2p1/verdict.json`; the two
verdicts coexist per the c29 state-machine lemma.

## §6 SB1 / SB2 status

| SB      | Threshold                | c45 v2 observed        | c47 v2.1 observed | Status vs c26           |
|---------|--------------------------|------------------------|-------------------|--------------------------|
| SB1     | margin > 0.5909          | -0.2341                | -0.2341 (unchanged) | `FAIL_unchanged_from_c45` |
| SB2     | mean τ ≥ 0.4             | -0.0314                | -0.0314 (unchanged) | `FAIL_unchanged_from_c45` |
| SB3 det | ≥ 0.90                   | 1.000                  | 1.000              | PASS                    |
| SB3 FPR | ≤ 0.10                   | 0.120 (25 ctl) → 0.100 (50 ctl) | 0.100 (both runs) | PASS (new PASS at 50 ctl) |

v2.1 does not re-verdict SB1 or SB2. Both remain FAIL under c26
thresholds unchanged from c45. The material change is exclusively on
the SB3 FPR axis.

## §7 Anchor preservation manifest

34 anchors snapshotted before and after v2.1 work; all 34 present, all 34
byte-identical pre/post. Anchor manifest at
`data/ear_v2p1/anchor_preservation_v2p1.json`.

Anchor set spans:

- **c6 chassis (7 files):** `scripts/ear/{features,model,corn,leak_test,synthetic_labels,stability_metrics,stability_audit}.py`.
- **c22 stability harness (1 file):** `data/ear/stability_audit/stability_report.json`.
- **c26 Path B (1 file):** `docs/ear_path_b_commitment.md`.
- **c36 v0 (4 files):** `docs/ear_v0_real_label_training_rubric.md`,
  `data/ear_v0/{rubric_hash.txt, verdict.json, corn_head_v0_real.pt}`.
- **c38 v1 (4 files):** `docs/ear_real_label_training_v1_rubric.md`,
  `data/ear_v1/{rubric_hash.txt, verdict.json, corn_head_v1.pt}`.
- **c45 v2 (3 files):** `docs/ear_real_label_training_v2_rubric.md`,
  `data/ear_v2/{rubric_hash.txt, verdict.json}`.
- **c46 SB3 widening result (2 files):** `data/ear_v2/{sb3_control_widening_result.json, determinism_check_c46.json}`.
- **c45/c46 adjudication (2 files):** `docs/ear_v2_verdict_adjudication_report.md`,
  `data/ear_v2/adjudication_rubric_hash.txt`.
- **Rules ledger invariants (3 files):** `data/rules/{ledger.jsonl, ledger_i3_dminor.jsonl, ledger_rated_corpus.jsonl}`.
- **c46 policy doc (1 file):** `docs/pre_registration_gate_policy.md`.
- **v2 auxiliary artifacts (3 files):** `data/ear_v2/{held_out_predictions.tsv, training_result.json, corn_head_v2.pt, leak_test_v2_summary.json, sb_v2_verdict.json, held_out_folds.json}`.

## §8 c22 / c23 / c25 Path A anti-pattern non-reopening evidence

- **c22 chassis exhaustion.** v2.1 did NOT re-run the 55-clip synthetic
  harness. The c22 rubric does not apply here; v2.1 is Path B on real
  labels. Test 08 asserts the c22 harness mtimes byte-identical
  pre/post via the anchor preservation manifest. AST-grep confirms zero
  imports of `scripts.ear.synthetic_labels` from `scripts/ear_v2p1/`.
- **c23 head regularization.** v2.1 uses c6 CORN head verbatim
  (`Linear(2052,128) → ReLU → Dropout(0.3) → Linear(128,6)`). Test 09
  asserts `scripts/ear/{features,model,corn,leak_test}.py` SHAs
  byte-identical pre/post.
- **c25 feature representation.** v2.1 uses c6 features verbatim
  (PANNs Cnn14 2048-D + M-HEUR-1 4-D). No feature swap.
- **c11 CLAP HF SSL / c35 palette VST3** forbidden state-extraction APIs
  (`get_state`/`save_state`/`save_preset`/`load_state`/`set_state(bytes)`)
  do not appear anywhere under `scripts/ear_v2p1/`. Grep-verified.

Additional invariance evidence:

- No PRNG in `scripts/ear_v2p1/` beyond the whitelisted `torch.manual_seed(0)`
  (test 11 AST-grep).
- No `sidecar_nonfactor` imports (test 12).
- No `i4_stratified.py` imports (test 14).

## §9 Egress state

Egress remains **blocked**. The c47 clone-0 probe row appended to
`data/ingestion/egress_status.jsonl` records the continuing failure mode
`429 + tv_embedded` first documented in c45 and reified as a lemma
(`_infra/egress-failure-mode-registry`) in c46. The
two-consecutive-`media_ok=true` unblock signal did NOT fire this cycle.
The corpus caveat 43/80 stands.

## §10 c48 handoff seeds

1. **Corpus expansion to 80 songs** remains the highest-leverage next
   step for downstream ear-model calibration. Egress unblock is the
   long-pole dependency; retry cadence per directive (each cycle,
   non-blocking).
2. **v2 vs v2.1 label reconciliation for downstream consumers.** Any
   consumer reading the ear-model verdict should now consult
   `data/ear_v2p1/verdict.json` (the peer v2.1 verdict) alongside
   `data/ear_v2/verdict.json`. The two coexist per c29 state machine.
   A short reconciliation note in `docs/ear_path_b_commitment.md`
   (or a new `docs/ear_v_v2p1_reconciliation.md`) would formalize the
   consumer contract.
3. **Egress retry cadence formalization.** The egress probe has been
   emitting a fresh row every cycle since c14; a formal
   `_infra/egress-retry-cadence-policy.md` would name the cadence
   (per-cycle, non-blocking) and the unblock signal
   (two consecutive `media_ok=true`) as durable campaign policy.
4. **Audit-reads-rubric-docs lemma.** If not yet landed in a prior
   cycle's `_infra/*` policy family, formalizing that audits and workers
   must consult the on-disk rubric doc verbatim (never a paraphrase)
   would prevent recurrence of the c45 audit's reconciliation-A
   mapping error.
5. **SB2 τ recovery mechanism probe.** The c45 lift −0.099 → −0.031
   improved SB2 τ but stayed below the 0.4 threshold. A 2-cell ablation
   (per-clip vs GroupKFold contribution) would attribute the observed
   improvement — useful before any Path C proposal targeting SB2.
6. **SB3 statistic version pin.** With SB3 now PASS on both axes at
   v2.1, pinning `STATISTIC_VERSION = "F1_pooled_variance_v1"` as a
   formal anchor in `data/anchor_manifest_v1.json` (Branch C's scope
   this cycle) closes the risk of a downstream statistic swap
   silently invalidating the v2.1 verdict.
7. **Adjudication rubric SHA is a permanent anchor.** Future
   verdict-mapping cycles must respect or supersede the c46
   adjudication rubric SHA
   `975985495b5750668262374080e3c6f0b135be6aa3b1a647f81c0b08c880afa8`.

## Provenance chain

- Rubric doc SHA-256: `2920875671ea98b127a585bf42ed401110a724b0b6b61fc5aa1bca0cff2abafa`
  → pinned in `data/ear_v2p1/rubric_hash.txt`
  → pinned in `data/ear_v2p1/verdict.json.rubric_hash` (three-way byte-equal).
- c45 v2 feature cache manifest SHA-256:
  `b00a001ef9a5dd3689369b65f8d984a368609d6736cda8cd10a4144923d5b819`
  (READ-ONLY re-use, no re-extraction).
- c46 SB3 widening result SHA-256: pinned in
  `data/ear_v2p1/verdict.json.c46_sb3_widening_result_sha256`.
- v2.1 SB3 per-run verdict SHA-256:
  `c5add489eace0a6d3772307ef9ec2d8797a8b75ee49b16f80c73d4f99aacb140`
  (both runs).
- c45 v2 verdict.json SHA-256: pinned in
  `data/ear_v2p1/verdict.json.c45_v2_verdict_json_sha256`
  (proof of non-modification).

## Ledger events fired (6 named + 2 housekeeping + 4 aux)

Named events under `M-EAR-1/real-label-training-v2.1/` (substantive
`M-*` unsuffixed per c32 convention):

1. `M-EAR-1/real-label-training-v2.1/rubric-committed`
2. `M-EAR-1/real-label-training-v2.1/features-loaded`
3. `M-EAR-1/real-label-training-v2.1/head-trained`
4. `M-EAR-1/real-label-training-v2.1/sb3-50ctl-run-1`
5. `M-EAR-1/real-label-training-v2.1/sb3-50ctl-run-2`
6. `M-EAR-1/real-label-training-v2.1/verdict-emitted`

Aux (c33 auto-suffix on infra families):

- `_plan/register-ear-v2p1-milestone-clone-0`
- `M-EAR-1/real-label-training-v2.1/anchor-preservation-verified` (sub-leaf, unsuffixed)
- `M-INGEST-1/egress-probe-cycle47-clone-0`
- `_run/cycle_47_launched-clone-0`

Housekeeping (after `_run/cycle_47_closed-clone-0`):

1. `_archive/cycle-47-scratch-clone-0`
2. `_infra/adopt-cycle47-tests-clone-0`

## Result: `EAR_v2p1_STABLE_FPR_PASS` → `EAR_v2p1_PARTIAL_WITH_SB3_PASS`.
