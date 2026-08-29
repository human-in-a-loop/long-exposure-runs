---
created: 2026-08-29T17:00:00Z
cycle: 47
run_id: run-2026-08-28T040704Z
agent: worker
milestone: M-EAR-1/real-label-training-v2.1
---

# M-EAR-1/real-label-training-v2.1 — 50-control SB3 re-verdict rubric

## Scope

`M-EAR-1/real-label-training-v2.1` is a **peer sub-milestone under M-EAR-1**
per the c29 state-machine lemma — it is NOT a child of the validated
`M-EAR-1/real-label-training-v2` milestone. v2.1 measures whether the c46
`SB3 50-control widening`'s observed 50-ctl FPR = 0.100 result reproduces
**byte-deterministically across two fresh `tempfile.mkdtemp()` runs**.

- v2.1 does NOT re-verdict SB1 or SB2. Both remain FAIL under c26 thresholds,
  unchanged from c45's `EAR_v2_PARTIAL` verdict.
- v2.1 does NOT modify `data/ear_v2/verdict.json`.
- v2.1 does NOT re-run the c22 55-clip synthetic-label stability harness.
- v2.1 does NOT change any element of the c6 CORN chassis, the c6
  feature pipeline, or the c26 Path B thresholds.
- v2.1 does NOT reopen c22 / c23 / c25 Path A audits.

The material change v2.1 measures: **does SB3's FPR component flip stably
to PASS at 50 controls, or was c46's exact 0.100 result a boundary-tip
artifact of finite-controls null-distribution noise?** SB3's detection
component was already PASS at 1.000 in c46; that stands unchanged.

## SB3 pass/fail decomposition

Under the c26 Path B commitment (`docs/ear_path_b_commitment.md` §3),
SB3 is defined by two axes measured against separate thresholds:

- **SB3 detection axis (PASS iff detection_rate ≥ 0.90):** in c46,
  detection_rate = 1.000 with the c37 F1 pooled-variance leak statistic
  on the artist non-factor at α=1.0 across 20 subsample repeats. The
  detection axis was already PASS in c46 and is UNCHANGED under v2.1.
- **SB3 FPR axis (PASS iff FPR ≤ 0.10):** in c46 with n_controls=50,
  the observed FPR was exactly 0.100 (5 of 50 null permutations above
  the 90th-percentile null threshold τ). At this exact-boundary
  value, it is not knowable a priori whether the underlying leak-null
  distribution is stably at ≤ 0.10 or whether c46's exact tie was a
  boundary-tip artifact. v2.1's job is to decide.

The SB3 verdict axis for v2.1 combines the two: SB3 gains a PASS
component alongside its unchanged detection PASS if the FPR reproduces
stably at ≤ 0.10 in both fresh runs.

## Frozen 3-verdict SB3 FPR rubric (v2.1 material axis)

```
EAR_v2p1_STABLE_FPR_PASS
    IFF   fpr_run_1 ≤ 0.10  AND  fpr_run_2 ≤ 0.10
    AND   sha256(sb3_50ctl_run_1/sb3_50ctl_verdict_v2p1.json)
          == sha256(sb3_50ctl_run_2/sb3_50ctl_verdict_v2p1.json)
    AND   no boundary-tip: max(fpr_run_1, fpr_run_2) < 0.10 + 1e-9  is not required;
          byte-equality of the two verdict JSONs is the primary determinism gate.
          (The c37/c38 F1 pooled-variance statistic is deterministic given
           fixed rows + fixed null seeds, so byte-equality is the honest test.)

EAR_v2p1_BOUNDARY_TIP
    IFF   the two runs produce different sb3_50ctl_verdict_v2p1.json SHAs
          (indicating a source of non-determinism outside the pinned seeds
           and BLAS pins — this should not happen and would be surfaced as
           a genuine c47 finding)
    OR    exactly one of {fpr_run_1, fpr_run_2} is > 0.10 while the other is ≤ 0.10.

EAR_v2p1_FPR_STILL_OVERSHOOT
    IFF   fpr_run_1 > 0.10  AND  fpr_run_2 > 0.10.
```

Under c45's rubric PARTIAL clause (SB2 τ improvement over v1), the peer
v2.1 verdict maps:

| SB3 FPR axis outcome           | v2.1 mapping label                         |
|-------------------------------|--------------------------------------------|
| `EAR_v2p1_STABLE_FPR_PASS`    | `EAR_v2p1_PARTIAL_WITH_SB3_PASS`           |
| `EAR_v2p1_BOUNDARY_TIP`       | `EAR_v2p1_PARTIAL_WITH_SB3_BOUNDARY_TIP`   |
| `EAR_v2p1_FPR_STILL_OVERSHOOT`| `EAR_v2p1_PARTIAL` (unchanged from c45 v2) |

Both PASS and BOUNDARY_TIP cases cite the c46 methodology-improvement
chain: **c37 F1 pooled-variance statistic → c38 leak-lift plumbing →
c46 25→50 control widening.** SB1 and SB2 remain FAIL under c26
thresholds in all cases.

## Determinism envelope

Every v2.1 script runs under the following pins:

- BLAS: `OMP_NUM_THREADS=1`, `MKL_NUM_THREADS=1`, `OPENBLAS_NUM_THREADS=1`.
- Env: `PYTHONHASHSEED=0`, `SOURCE_DATE_EPOCH=1756463424`, `TZ=UTC`,
  `LC_ALL=C.UTF-8`.
- Torch: `torch.manual_seed(0)`, `torch.set_num_threads(1)`,
  `torch.use_deterministic_algorithms(True, warn_only=True)`.

The `SOURCE_DATE_EPOCH` value is inherited from the c46 canonical anchor;
formalization to `data/anchor_manifest_v1.json` is Branch C's responsibility
this cycle. v2.1 uses the value as-is.

The SB3 50-control re-verdict runs in a **fresh `tempfile.mkdtemp()`
directory** with the current working directory swapped in, twice. Both
runs read READ-ONLY from `data/ear_v2/held_out_predictions.tsv` (c45 v2
per-clip OOF predictions) and write per-run verdict JSON files under
`data/ear_v2p1/sb3_50ctl_run_{1,2}/`.

## Chassis anchor invariance (READ-ONLY)

v2.1 does NOT touch:

- `scripts/ear/{features,model,corn,leak_test,synthetic_labels,stability_metrics,stability_audit}.py`
- `data/ear/stability_audit/stability_report.json`
- `docs/ear_path_b_commitment.md`
- `docs/ear_real_label_training_v0_rubric.md`,
  `data/ear_v0/{rubric_hash.txt,verdict.json,corn_head_v0.pt}`
- `docs/ear_real_label_training_v1_rubric.md`,
  `data/ear_v1/{rubric_hash.txt,verdict.json,corn_head_v1.pt}`
- `docs/ear_real_label_training_v2_rubric.md`,
  `data/ear_v2/{rubric_hash.txt,verdict.json,sb3_control_widening_result.json,determinism_check_c46.json,adjudication_rubric_hash.txt,adjudication_verdict.json}`
- `data/rules/{ledger.jsonl,ledger_i3_dminor.jsonl,ledger_rated_corpus.jsonl}`
- `docs/pre_registration_gate_policy.md`

The `data/ear_v2p1/anchor_preservation.json` manifest lists ≥32 SHA-256
values snapshotted before and after v2.1 work — every entry must be
byte-identical pre/post.

## Anti-pattern lockouts (binding)

- **c22 Path A chassis exhaustion:** v2.1 does NOT re-run the 55-clip
  synthetic harness; the c22 rubric does not apply here. c22 harness
  files are READ-ONLY anchors.
- **c23 head regularization:** v2.1 does NOT introduce
  ridge/bottleneck/frozen-projector variants. c6 CORN head is
  `Linear(2052,128) → ReLU → Dropout(0.3) → Linear(128,6)`, unchanged.
- **c25 feature representation:** v2.1 does NOT swap features. c6
  pipeline verbatim: PANNs Cnn14 2048-D + M-HEUR-1 4-D.
- **c11 CLAP HF SSL / c35 palette VST3 forbidden state-extraction API
  set** (`get_state`/`save_state`/`save_preset`/`load_state`/
  `set_state(bytes)`): AST-grep zero occurrences under `scripts/ear_v2p1/`.
- **No PRNG:** SHA-256 tiebreak only. Whitelist: `torch.manual_seed(0)`.
- **No `sidecar_nonfactor` imports** under `scripts/ear_v2p1/`.
- **No `i4_stratified.py` imports** under `scripts/ear_v2p1/`.
- **`/usr/bin/python3` interpreter guard** on every script under
  `scripts/ear_v2p1/`.
- **Startup banner to stdout** on every worker script before heavy imports
  (c43 CLI-Startup-Silence interdiction).
- **Foreground execution** (c41 Assumption Pattern interdiction). No
  `run_in_background=true` notification wait for the SB3 runs or the
  training. In-turn Monitor polling permitted; background notification
  reliance is not.

## Corpus caveat

The rated corpus at v2.1 time is **43 songs of the 80-song target** (10
band-4 + 10 band-5 + 13 band-6 + 10 band-7, 252 clips), unchanged from
c45. The v2.1 model artifact and verdict carry the label
**`preview_partial_corpus_v2p1`** prominently. The verdict is credible
for the on-disk 43-song corpus; it is NOT calibrated to the full 80-song
target. Corpus expansion to 80 songs remains the highest-leverage c48+
handoff.

## Test-suite ≥ 12 cases (target 16/16, minimum 12/15)

The v2.1 test suite at `tests/test_ear_v2p1_real_label_training.py`
covers:

1. Rubric mtime gate (HARD).
2. Git-log gate (SOFT per c46 path (ii) amendment).
3. Three-way rubric_hash byte-equality.
4. SB3 detection finite + equals 1.000.
5. SB3 FPR finite (both runs).
6. Byte-determinism × 2 on SB3 verdict.
7. Byte-determinism × 2 on training artifacts.
8. c22 stability harness mtimes unchanged.
9. c6 chassis anchor SHAs unchanged.
10. c26 threshold values unchanged (verbatim SB1/SB2/SB3 literals).
11. No PRNG in `scripts/ear_v2p1/` (AST-grep).
12. No `sidecar_nonfactor` imports.
13. Interpreter guard first-3-lines check.
14. No `i4_stratified.py` imports.
15. Corpus-N caveat present in report.
16. SB1/SB2 not re-verdicted (literal `FAIL_unchanged_from_c45`).

## Cross-branch integration §61 (target ≥8 checks)

`tests/test_integration_cross_branch.py §61` extends with:

- Verdict JSON schema well-formed.
- Three-way rubric_hash byte-equality.
- Byte-determinism × 2 on SB3 verdict.
- c22 stability harness anchor SHAs unchanged.
- c45 v2 verdict.json SHA unchanged.
- c46 SB3 widening result SHA unchanged.
- Corpus-N caveat presence.
- No re-verdict of SB1/SB2.

## 6 named + 2 housekeeping ledger events

Named events (substantive `M-*` unsuffixed per c32; sub-leaves per c32):
1. `M-EAR-1/real-label-training-v2.1/rubric-committed`
2. `M-EAR-1/real-label-training-v2.1/features-loaded`
3. `M-EAR-1/real-label-training-v2.1/head-trained`
4. `M-EAR-1/real-label-training-v2.1/sb3-50ctl-run-1`
5. `M-EAR-1/real-label-training-v2.1/sb3-50ctl-run-2`
6. `M-EAR-1/real-label-training-v2.1/verdict-emitted`

Also fires (aux):
- `_plan/register-ear-v2p1-milestone-clone-0` (pre-rubric)
- `M-EAR-1/real-label-training-v2.1/anchor-preservation-verified`
- `M-INGEST-1/egress-probe-cycle47-clone-0`
- `_run/cycle_47_launched-clone-0`

Housekeeping (fires after `_run/cycle_47_closed-clone-0`):
1. `_archive/cycle-47-scratch-clone-0`
2. `_infra/adopt-cycle47-tests-clone-0`

## Success gate for this clone's cycle close

- Rubric doc committed BEFORE any script under `scripts/ear_v2p1/`,
  mtime gate hard; git-log advisory per c46 path (ii).
- Verdict JSON three-way `rubric_hash` byte-equality verified.
- SB3 byte-determinism × 2 verified (SHA-256 equal on
  `sb3_50ctl_verdict_v2p1.json` across two fresh temp-dir runs).
- Training artifacts byte-determinism × 2 (`corn_head_v2p1.pt` +
  `training_result_v2p1.json` SHA-equal × 2).
- Anchor preservation 32+ SHAs pre==post byte-exact.
- ≥12/15 tests green in `tests/test_ear_v2p1_real_label_training.py`
  (target 16/16).
- Cross-branch §61 extended with ≥8 checks.
- 0-ERROR promise_check after all events land.
- Report at `docs/ear_real_label_training_v2p1_report.md` with 10
  sections.
