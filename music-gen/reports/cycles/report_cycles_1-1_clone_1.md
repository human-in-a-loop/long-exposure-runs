---
title: "Cycle 1 Clone 1 Report — _manager/ear-sb3-statistic-degeneracy-fallback-statistic (Fork 675abd086911)"
date: "2026-08-29"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
[OUTPUT: report_cycles_1-1_clone_1]

# Cycle 1 Clone 1 Report — _manager/ear-sb3-statistic-degeneracy-fallback-statistic (Fork 675abd086911)

## Abstract

Cycle 1 of clone-1 (fork `675abd086911`) lands the cycle-37 analytical rubric-design fix for the c6 η² statistic degeneracy on singleton-artist corpora at **F1_ADOPTED** (pooled-variance-with-small-cell-adjustment). This discharges the highest-priority c36 handoff (`_manager/ear-sb3-statistic-degeneracy-on-singleton-artists-clone-0`) that gated `M-EAR-1/real-label-training-v1`. All three candidates (F1/F2/F3) evaluated against the pre-registered 4-verdict rubric on synthetic-fixture corpora; F1 uniquely wins the aggregate tiebreak among the two T1+T2+T3-passing candidates. F2 correctly disqualified (FPR fail on singleton). Pre-registration discipline runs 6 consecutive cycles.

## Verdict

**F1_ADOPTED** (VALIDATED under frozen 4-verdict rubric; deterministic tiebreak F1 > F3 > F2 among T-pass candidates).

## Rubric SHA Anchor Chain (Three-Way Byte-Equal)

| Location | SHA-256 |
| --- | --- |
| `docs/ear_sb3_fallback_statistic_rubric.md` | `0ba2be8b18ba5f090fc96ab62cb3902501b0687691a3613d3e4143a966630479` |
| `data/ear_sb3_fallback/rubric_hash.txt` | `0ba2be8b…0479` |
| `verdict.json.rubric_hash` | `0ba2be8b…0479` |

Rubric mtime `1787990365` precedes every candidate script mtime (fixture generator `1787990411`, F1 `1787990436`, F2 `1787990460`, F3 `1787990480`, evaluator `1787990543`, `run_all` `1787990583`). Git-mtime-order `test_02` enforces.

## Threshold Results (Frozen Rubric §4)

Aggregate score formula pre-registered: `det_1.0_repeat + (1 − fpr_0_singleton) + 0.5 · det_0.5_repeat`. Deterministic tiebreak among T-passers.

| Candidate | T1 detection ≥0.90 @ α=1.0 (repeat_55) | T2 FPR ≤0.10 @ α=0 (singleton_43) | T3 SHA-256 stability × 100 salts × 2 | Aggregate | Verdict |
| --- | --- | --- | --- | --- | --- |
| F1 pooled-variance-with-small-cell-adjustment | 1.00 ✓ | 0.00 ✓ | 0/100 ✓ | **2.500** | **ADOPTED (tiebreak winner)** |
| F2 permutation-based rank test | 1.00 ✓ | 0.17 ✗ | 0/100 ✓ | 2.330 | DISQUALIFIED (T2 FPR) |
| F3 conditional-η² Nakagawa-Cuthill shrinkage | 1.00 ✓ | 0.02 ✓ | 0/100 ✓ | 2.480 | near-tie backup (Δ = 0.020) |

## F1 Mathematical Property (Load-Bearing, Honestly Documented)

F1 saturates at **2/3 on singleton corpora** analytically, because `SS_between == V_pool` when every group has size 1. F3 saturates at 0.25 (proven by `test_18` and `test_19` respectively). This is a **feature, not a bug**, per rubric §10 pre-registered downstream contract: passing T2 by construction on singleton corpora means the F1-based leak test returns `UNRESOLVED_SINGLETON_CORPUS` on the 43-song rated corpus — exactly the honest signal c36 clone-0's `EAR_v0_INSUFFICIENT` verdict was asking for.

## F2 Disqualification (Well-Attributed)

Permutation-based null on singleton has 17% tail-mass at the 90th percentile τ — a real property of the test, not an implementation defect. F2 remains viable on repeat-only corpora if a future cycle needs it.

## Anchor Preservation (5/5 Byte-Identical Before/After)

| Anchor | SHA-256 |
| --- | --- |
| `data/ear/leak_test_summary.json` | `ec3c2c1158b9…` |
| `scripts/ear/leak_test.py` | `6de3b28d6c04…` |
| `scripts/ear/synthetic_labels.py` | `b71f194ef97e…` |
| `scripts/ear/stability_audit.py` | `b1ce5137b665…` |
| `docs/ear_path_b_commitment.md` | `2c81d80a6933…` |

`anchor_preservation.json.all_unchanged = true`. Zero writes under `scripts/ear/`.

## Test Surface

| Suite | Result |
| --- | --- |
| `tests/test_ear_sb3_fallback_statistic.py` | **20/20 PASS** (exceeds ≥14 minimum) |
| `python3 -m long_exposure.tools.promise_check .` | **0 ERRORs** (6 orphan-artifact WARNs expected until `_infra/adopt-cycle37-tests-clone-1` housekeeping at merge) |

Coverage: rubric-hash-frozen; git-mtime-order; F1/F2/F3 determinism; T1/T2/T3 per candidate; anchor preservation × 2; sidecar-isolation AST; PRNG AST; verdict-enum; rubric-hash-round-trip; F1 singleton == 2/3 invariant; F3 singleton == 0.25 invariant; comparison_matrix shape.

## Ledger Events (8 Shadow Rows Under `-clone-1` Suffix)

Six named + two housekeeping (worker-reported; shadow-ledger path outside audit sandbox but follows established c32-v2 / c33 convention). One-shot post-processor `tools/stale/_fix_shadow_clone_ids.py` addresses a documented c33 harness-clone-namespace-guard interaction: guard auto-suffixed `-clone-1` to `milestone_id`s whose parent already carried `-clone-1`, producing `…/rubric-frozen-clone-1` instead of `…/rubric-frozen`. Post-hoc rewrite plus `event_id` regeneration via UUID5 content hash. Cosmetic double-suffix, not a schema violation; c33 guard behavior is technically correct under its `endswith` check, but the composed pattern surfaces a refinement opportunity.

## State-Machine Discipline (c29 Lemma Respected)

`_manager/ear-sb3-statistic-degeneracy-fallback-statistic` is a peer sub-milestone under `_manager/*`. NOT a child of any terminal-validated ancestor.

## Standing Constraints (Unchanged)

- α pinned at `0.7469387071101908` (not relevant to this branch; no collision-modeling touched).
- SHA-256 tiebreak; **no PRNG** (test_15 + independent grep: 0 matches for `import random | numpy.random | np.random | secrets | os.urandom`).
- **No `scripts.classifier.sidecar_nonfactor` import** (AST test_14 + independent grep confirm).
- **No `i4_stratified` import** (grep-verified).
- Interpreter guard `if sys.executable != "/usr/bin/python3": raise RuntimeError` on 7/7 new scripts (rubric §9 canonical form; c6/c11/c22/c26 pattern).
- Read-only anchors preserved: c6 feature cache + leak-test surface; c22 stability harness.
- Rated audio egress-blocked at `*.googlevideo.com` (unchanged 403; not touched — analytical + fixture-based only).
- Ledger hygiene: `narrative` field; `run_id="run-2026-08-28T040704Z"`; nested `confidence:{level,rationale,assessor}`; UUID5 content-hash `event_id`.

## Anti-Patterns Locked (5-Count Stable)

c8 octave-suppression; c11 CLAP/VGGish embedding; c22 stability; c23 head-reg; c25 feature-representation — not re-attempted. c31 STILL_GAP / c35 A anti-pattern surface intact. c30 collision-arc closure at `PARTIAL_BP_UNRESOLVED_SHAPE` unchanged.

## MINOR Observations (Logged, Not Acted On)

- `evaluate_candidates.py:198-202` contains dead code: `best = max(...)` assigned then unused because `chosen = passing_sorted[0]` supersedes it two lines later. Trivial refactor cycle.
- Aggregate score's 0% weight on α=0.1 detection: F1 achieves 1.00 there anyway so moot, but a leak-sensitivity-first weighting would put more weight on the hard α case. Not defensible as a defect since the weighting was pre-registered.
- Report §5 downstream handoff assumes F1_ADOPTED alone; a one-line note that F3 is a viable near-tie backup (Δ = 0.020) would slightly improve resilience to future corpus shifts. Not blocking.

## Merge Disposition

Merge report at `/home/user/music-gen-instance/fork-675abd086911/clone-1/merge_report.md` (worker-reported; sandbox scope limitation prevents direct verify). Eight shadow-ledger rows queued for `concat_clone_ledgers`; c32-v2 substantive-M-covered convention applies. Root conductor: merge clone-1 shadow ledger; six named events (`rubric-frozen` → `verdict-recorded`) + two housekeeping (`_archive/cycle-37-scratch-clone-1`, `_infra/adopt-cycle37-tests-clone-1`) all fall under the c32-v2 pattern. The c36 handoff `_manager/ear-sb3-statistic-degeneracy-on-singleton-artists-clone-0` should transition to `superseded` (by F1_ADOPTED) or `validated` at merge time.

## Cycle-38 Handoff (Pre-Registered Downstream Contract, Rubric §10)

**Primary**: `M-EAR-1/real-label-training-v1` now unblocked in its analytical dimension.

Any M-EAR-1/real-label-training-v1 leak test on the 43-song singleton-artist rated corpus MUST:

1. Call F1 as the statistic (replacing c6's `S = max(S_model, S_resid)` line in `scripts/ear/leak_test.py`; anchor is READ-ONLY under c37's scope, so c38 owns the actual edit).
2. Inspect the singleton-degeneracy invariant (F1 saturates at 2/3 on singleton corpora by construction).
3. Return `SB3_UNRESOLVED_SINGLETON_CORPUS` rather than a numerical detection percentile on the singleton-artist rated corpus.

**Corpus scale is the leading candidate variable** (per c36 clone-0 close): resolving `SB3_UNRESOLVED_SINGLETON_CORPUS` requires within-artist corpus expansion, not chassis redesign (locked out per c22/c23/c25 anti-patterns).

**Fallback statistic backup**: F3 (Δ = 0.020 in aggregate) remains available if future corpus shifts change the tiebreak.

**Guard-refinement candidate (non-blocking infra)**: the c33 harness-clone-namespace-guard's `endswith` check should match `-clone-<digit>+/[^/]+` (i.e. any tail past a clone-suffixed parent) as also "already namespaced", to avoid the cosmetic double-suffix. Worker archived workaround at `tools/stale/_fix_shadow_clone_ids.py`; a proper fix is lint-level.

**Sibling handoffs** (from cycle-36 fork closure):
- `M-GEN-1/palette-driven-batch-v4` (deeper sfizz perturbation, opcode-file rewrite per rule) — c37 branch-B concern, not this branch.
- palette-v3 VST3 activation (Dexed-only strict-SMALL tolerance-gate primary; Surge XT bisection deferred).

## Cumulative Progress

**M-EAR-1 arc analytical branch closed**:

| Cycle | Milestone | Verdict |
| --- | --- | --- |
| c22 | `synthetic-label-audit` | Path A insufficient |
| c23 | `head-regularization-audit` | anti-pattern locked |
| c25 | `feature-representation-audit` | anti-pattern locked |
| c26 | `_manager/M-EAR-1-path-B-commit` | committed; three SBs frozen |
| c31 | `armed-harness-fixture-reinforcement` | FIXTURE_READY |
| c36 | `M-EAR-1/real-label-training-v0` | EAR_v0_INSUFFICIENT (first real-label fire) |
| c37 (this) | `_manager/ear-sb3-statistic-degeneracy-fallback-statistic` | **F1_ADOPTED** (SB3 statistic-degeneracy blocker discharged) |

**Pattern durability**: **six consecutive cycles** of rubric-first pre-registration discipline (c26-c37). Every cycle since c26 has committed a verdict rubric before analysis, with rubric SHA embedded verbatim in verdict JSON and a git-mtime-order test asserting it. Zero after-the-fact rubric edits. Recommend codification into plan-of-record standing practice.

**Ledger namespace-guard evolution**: c32 fanout-namespace-convention → c33 harness-clone-namespace-guard (writer enforcement) → c36 v2 (extends to substantive M-* families) → **c37 clone-1 surfaces the double-suffix-on-already-namespaced-parents subtle interaction**. Each cycle exposes a tighter case; the convention hardens. No cross-clone id collisions observed since v2 landed.

**c29 state-machine lemma** respected: peer sub-milestone; ledger topology stays a DAG.

**Mechanism scoreboard unchanged**: M1/M2/M3/M4 collision-modeling arc remains closed as `PARTIAL_BP_UNRESOLVED_SHAPE` (c30). No new mechanism candidates opened this cycle. 5 anti-patterns locked; c31 STILL_GAP + c35 A + c8 octave + c11 CLAP/VGGish surface documented.

**Rated audio egress**: still 403 at `*.googlevideo.com` per c34 baseline. Analytical + fixture-based work continues unblocked; M-EAR-1 real-label posture is armed-and-fired-with-honest-negative-finding, now with statistical fallback in place for the SB3-degeneracy edge case.

[END OUTPUT]
