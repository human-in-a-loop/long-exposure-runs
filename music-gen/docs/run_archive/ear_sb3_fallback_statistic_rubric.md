# EAR SB3 fallback-statistic rubric (frozen — c37 clone-1)

Rubric: analytical rubric-design fix for the cycle-6 η² statistic degeneracy on
singleton-artist corpora (S_model = S_resid = 1.0 → detection identically 0).

This rubric is committed BEFORE any candidate implementation script under
`scripts/ear_sb3_fallback/` is written. A git-mtime ordering test enforces
rubric-before-candidates.

---

## 1. Scope

Three candidate fallback statistics evaluated on synthetic-fixture corpora:

- **F1** — pooled-variance-with-small-cell-adjustment
- **F2** — permutation-based rank test with within-artist symmetry
- **F3** — conditional-η² with variance shrinkage per Nakagawa-Cuthill

Fixture corpora:

- **singleton_43** — 43-song singleton-artist corpus (every song from a
  distinct artist — the c6 degeneracy regime)
- **repeat_55** — 55-clip repeat-artist corpus (11 artists × 5 clips each —
  the c22 valset regime)

Planted-leak strengths: α ∈ {1.0, 0.5, 0.1}, plus α = 0 (no-leak control).

Fixtures are SHA-256-derived deterministic; no PRNG. Byte-determinism across
≥100 salted regenerations is required.

## 2. Frozen 4-verdict rubric

Exactly one verdict is emitted per run:

| Verdict            | Meaning                                                          |
|--------------------|------------------------------------------------------------------|
| **F1_ADOPTED**     | F1 passes all three thresholds AND ranks best on aggregate score |
| **F2_ADOPTED**     | F2 passes all three thresholds AND ranks best on aggregate score |
| **F3_ADOPTED**     | F3 passes all three thresholds AND ranks best on aggregate score |
| **NO_FALLBACK_QUALIFIES** | Zero candidates satisfy all three thresholds              |

If two or more candidates pass all three thresholds, the tiebreaker is the
aggregate score defined in §4. If the aggregate score also ties (to within
1e-9), the first candidate in alphabetical order (F1 < F2 < F3) is adopted.

## 3. Acceptance thresholds (pre-registered)

Each candidate must satisfy ALL THREE:

- **T1 (detection floor)** — detection rate ≥ **0.90** at α = 1.0 on the
  `repeat_55` corpus (c6 protocol reproducibility). Detection = candidate's
  statistic exceeds its no-leak calibrated τ.
- **T2 (FPR ceiling)** — false-positive rate ≤ **0.10** at α = 0 on the
  `singleton_43` corpus (avoiding the c6 degeneracy in the other direction —
  saturating on all-unique groups must not falsely fire).
- **T3 (numerical stability)** — SHA-256 equality of the candidate's output
  scalar (rounded to 12 decimal places) across TWO independent regenerations
  of the same fixture, over ≥100 salts.

Failure on any threshold disqualifies that candidate from ADOPTED status.

## 4. Aggregate score (tiebreaker)

For each candidate that passes T1+T2+T3, aggregate score is:

    score = detection_rate_alpha_1_0_repeat55
          + (1.0 - fpr_alpha_0_singleton43)
          + 0.5 * detection_rate_alpha_0_5_repeat55

Higher is better. Range roughly [0, 2.5]. The 0.5 weight on the α=0.5 case
reflects that partial-leak detection is a nice-to-have, not a requirement.

## 5. Calibration protocol

For each (candidate, corpus) pair:

- Generate 20 no-leak (α = 0) fixtures, salts 0..19.
- Compute the candidate's statistic on each.
- τ = 90th percentile of the 20 statistics (Nakagawa-Cuthill FPR-target of
  0.10).

Detection tests then use salts 100..199 (100 replicates per α) to keep
calibration and evaluation salt ranges disjoint.

## 6. Numerical stability protocol

For each candidate:

- For each salt in 0..99, generate the same fixture TWICE independently
  from that salt.
- Compute statistic on each generation.
- Assert SHA-256 equality of the rounded-to-12-decimal-places scalar
  (bytes of the decimal string).

Any single mismatch across the 100 salts fails T3.

## 7. Anchor preservation

The following are READ-ONLY anchors and MUST NOT be modified:

- `data/ear/leak_test_summary.json` (c6 η² diagnostic)
- `scripts/ear/leak_test.py` (c6 leak-test harness)
- `scripts/ear/synthetic_labels.py` (c22 stability harness)
- `scripts/ear/stability_audit.py` (c22)
- `docs/ear_path_b_commitment.md` (c26 Path B doc)
- All existing `scripts/ear/` files (feature cache pipeline)

The report emits `data/ear_sb3_fallback/anchor_preservation.json` recording
the SHA-256 of each anchor BEFORE and AFTER the evaluate run.

## 8. Sidecar_nonfactor isolation

No script under `scripts/ear_sb3_fallback/` may import
`scripts.classifier.sidecar_nonfactor` (AST-grep enforced by the test suite).

## 9. Interpreter guard

Every script under `scripts/ear_sb3_fallback/` opens with:

    #!/usr/bin/env python3
    if sys.executable != "/usr/bin/python3":
        raise RuntimeError(f"Interpreter guard: expected /usr/bin/python3, got {sys.executable}")

(This is the same guard cycle-6, c11, c22, c26 use.)

## 10. Downstream implication

- **Any of F1/F2/F3 ADOPTED** → cycle 38 M-EAR-1/real-label-training-v1 uses
  the adopted statistic in place of the c6 η² diagnostic; corpus expansion
  becomes optional.
- **NO_FALLBACK_QUALIFIES** → M-EAR-1/real-label-training-v1 REMAINS BLOCKED
  on within-artist corpus expansion (the negative-finding path). The report
  documents the specific failure modes and hands a corpus-expansion ticket
  to the next cycle.

Either outcome closes the c36 clone-0 `EAR_v0_INSUFFICIENT` blocker on
M-EAR-1/real-label-training-v1.

---

**End of frozen rubric.** SHA-256 of this document (excluding trailing
whitespace) is recorded to `data/ear_sb3_fallback/rubric_hash.txt` and
echoed verbatim into `data/ear_sb3_fallback/verdict.json.rubric_hash`.
