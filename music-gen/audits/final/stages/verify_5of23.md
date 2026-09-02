# Verify Stage 5 of 23 — M-EAR-1 real-label training arc (v0 → v1 → v2)

Slice: three tightly-coupled peer sub-milestones under M-EAR-1
representing the c26 Path B real-label calibration arc. Each is a peer
under M-EAR-1 per the c29 state-machine lemma (NOT a child of the
terminal-validated Path B commitment / stability-audit chain). All three
audited from on-disk artifacts under `data/ear_v{0,1,2}/`.

## Milestone 1 — M-EAR-1/real-label-training-v0 (cycle 36, clone-0)

**Reported verdict:** `EAR_v0_INSUFFICIENT` (43-song corpus, `preview_partial_corpus_v0`).

Verification:
- **rubric_hash chain** — three-way byte-equality holds:
  - `sha256(docs/ear_v0_real_label_training_rubric.md)` = `636c2cd0…1bb2e9`
  - `cat data/ear_v0/rubric_hash.txt` = `636c2cd0…1bb2e9`
  - `data/ear_v0/verdict.json.rubric_hash` = `636c2cd0…1bb2e9`
  All three identical.
- **SB gate outcomes** (from `verdict.json`):
  - SB1: margin −0.2093 vs required +0.5909 → FAIL. Baseline min MAE
    0.9302 (majority = mean-integer = 6); model MAE 1.1395.
  - SB2: mean pairwise Kendall τ −0.0987 vs required +0.4 → FAIL. Ten
    per-resample values all present, negative-mode as reported.
  - SB3: artist detection 0.0 (denominator=43, single-rep) → FAIL;
    genre `deferred_aliased_with_band`; era `deferred_no_metadata`.
- **Verdict rule per rubric**: `INSUFFICIENT` fires when no SB
  improves over any prior baseline AND no SB passes. v0 is the first
  real-label pass, so improvement is not evaluable — INSUFFICIENT is
  the correct terminal for a 0/3 first-pass finding. Consistent with
  the c26 Path B commitment's honest-negative-finding contract.
- Ledger event `M-EAR-1/real-label-training-v0/verdict-emitted` and
  the six named sub-leaves under `-clone-0` land per plan-of-record.
- `preview_partial_corpus_v0` caveat present in verdict + report.

**Verdict:** CONFIRMED. Severity: none.

## Milestone 2 — M-EAR-1/real-label-training-v1-clone-0 (cycle 38)

**Reported verdict:** `EAR_v1_PARTIAL`.

Verification:
- **rubric_hash chain** — three-way byte-equality holds:
  - `sha256(docs/ear_real_label_training_v1_rubric.md)` = `10131bf3…baa37f`
  - `cat data/ear_v1/rubric_hash.txt` = `10131bf3…baa37f`
  - `data/ear_v1/verdict.json.rubric_hash` = `10131bf3…baa37f`
- **SB gate outcomes**:
  - SB1: margin −0.2093 unchanged from v0 (same features + chassis, no
    calibration change to feature space). FAIL.
  - SB2: mean τ −0.0987 unchanged from v0. FAIL.
  - SB3: `statistic_version` upgraded from raw permutation drop (v0)
    to `F1_pooled_variance_v1` — the c37 statistic. Per-leak-type
    artist detection = 1.0 (was 0.0 in v0); FPR = 1.0 with
    single-rep-per-clip denominator. `pass_detection=True`,
    `pass_fpr=False`. FAIL overall.
- **PARTIAL clause per c46 mapping-clarified paragraph** (rubric doc
  §PARTIAL): fires when ≥1 SB improves over v0 AND ≥1 SB falls short
  under PASS thresholds. SB3 statistic upgrade (v0→v1) lifts detection
  0.0 → 1.0 — a genuine methodology improvement counted under the
  IMPROVEMENT clause. 0/3 SB pass + ≥1 SB improve ⇒ PARTIAL is the
  correct rubric-mapped verdict. Consistent with c46 mapping doc.
- `leak_test_diff_manifest.json` present (v0→v1 leak-test diff),
  `determinism_check.json` present (byte-determinism × 2 recorded).

**Verdict:** CONFIRMED. Severity: none.

## Milestone 3 — M-EAR-1/real-label-training-v2 (cycle 45) + c46 adjudication

**Reported verdict:** `EAR_v2_PARTIAL` (0/3 SB pass, 2/3 SB improve).

Verification:
- **rubric_hash chain** — three-way byte-equality holds:
  - `sha256(docs/ear_real_label_training_v2_rubric.md)` = `01948b6e…d71e0`
  - `cat data/ear_v2/rubric_hash.txt` = `01948b6e…d71e0`
  - `data/ear_v2/verdict.json.rubric_hash` = `01948b6e…d71e0`
- **SB gate outcomes**:
  - SB1: margin −0.2341 (baseline 0.9286, model 1.1627) vs required
    +0.5909 → FAIL. Slightly worse than v1 (−0.2093), NOT an
    improvement over v1 baseline.
  - SB2: mean τ −0.0314 vs required +0.4 → FAIL. Improvement over v1
    (−0.099 → −0.031) counted per c46 mapping (v1-baseline gate
    > −0.0987).
  - SB3: artist detection 1.0 (PASS component); FPR 0.12 (FAIL); n_clips
    252 (43 songs × 6 clips), `denominator_pairs`=618 > 43 (denominator
    improvement per c46 mapping). `statistic_version` =
    `F1_pooled_variance_v1` preserved.
- **PARTIAL per c46 mapping-clarified paragraph**: 0/3 SB pass under
  PASS thresholds; ≥1 SB improves under IMPROVEMENT gate (SB2 mean τ
  improved v1→v2; SB3 denominator widened 43→618). Rubric-correct.
  This is the c45-c46 audit chain's specific reconciliation point.
- **c46 SB3 50-control widening** (`sb3_control_widening_result.json`):
  n_controls=25 → FPR=0.12 (FAIL); n_controls=50 → FPR=0.10 (boundary,
  PASS depending on strict inequality — c47 v2.1 re-evaluates this
  under fresh-temp-dir byte-determinism).
- **Adjudication artifacts** (`docs/ear_v2_verdict_adjudication_*`,
  `data/ear_v2/{adjudication_rubric_hash,determinism_check_c46,
  anchor_preservation_c46}.json`) all present. Adjudication verdict
  `ADJUDICATION_MAPPING_CLARIFIED` per c46 plan.

**Verdict:** CONFIRMED. Severity: none.

## Cross-cutting observations

1. **Rubric-hash contract holding** across three independent cycles
   (c36, c38, c45) and three independent rubric doc paths. This is the
   load-bearing pre-registration proof — confirmed byte-equal in all
   three cases via `sha256sum` of the doc file + `cat` of the
   `rubric_hash.txt` sidecar + JSON `.rubric_hash` field.
2. **PARTIAL vs INSUFFICIENT distinction is well-defined** and honored:
   v0 has no prior baseline (hence INSUFFICIENT is the correct terminal
   for 0/3 first-pass); v1/v2 both correctly land PARTIAL under the
   c46 IMPROVEMENT-clause mapping despite 0/3 PASS. No verdict drift.
3. **PASS thresholds unchanged**: SB1 margin +0.5909, SB2 mean τ +0.4,
   SB3 detection ≥0.9 & FPR ≤0.10. Frozen since c26 Path B commitment.
4. **43/80 corpus caveat** surfaced in all three verdicts + reports as
   `preview_partial_corpus_v{0,1,2}`. Honest.
5. Reference to c47 v2.1 (already audited via prior stages / to be
   audited in later slice) as the SB3 stable-FPR-pass re-verdict; not
   in this slice.

## Findings

Three findings appended to `audits/final/findings.jsonl`:
- v0 verdict-emitted CONFIRMED (severity=none)
- v1 verdict-emitted CONFIRMED (severity=none)
- v2 verdict-emitted CONFIRMED (severity=none)

No new severity-CRITICAL, MODERATE, or MINOR issues surfaced this
slice. The c46 mapping paragraph is on-disk and honored.
