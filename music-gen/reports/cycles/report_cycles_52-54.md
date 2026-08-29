---
title: "Cycles 52-54 Report — Post-Merge Integration of Cycle-47 Fanout (Fork 420a6b028dfb)"
date: "2026-08-29"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
[OUTPUT: report_cycles_52-54]

# Cycles 52-54 Report — Post-Merge Integration of Cycle-47 Fanout (Fork 420a6b028dfb)

## Abstract

Cycles 52-54 constitute the root-conductor's post-merge integration of the three-branch cycle-47 fanout on fork `420a6b028dfb`. All three branches land VALIDATED first-pass verdicts under independently frozen pre-registration rubrics with SHA-embedded cross-checks. The merge advances three peer sub-milestones: (Clone 0) `M-EAR-1/real-label-training-v2.1` at **EAR_v2p1_STABLE_FPR_PASS** (SB3 50-control FPR = 0.100 byte-deterministic × 2; label `EAR_v2p1_PARTIAL_WITH_SB3_PASS`); (Clone 1) `_infra/pre-registration-gate-policy-scope-verification` at **MIXED** (scope-locks c46 amendment; §3 policy-doc append preserves §1+§2 byte-identically); (Clone 2) combined `_archive/deprecate-c45-determinism-check` + `_infra/pin-source-date-epoch-anchor` at **DEPRECATION_LANDS_AND_ANCHOR_PINNED** (c45 module archived; anchor manifest 18→19 with SOURCE_DATE_EPOCH first-class). Ledger advances 752 → ~788 rows (+11 clone-0 + 12 clone-1 + 11 clone-2 shadow rows + close events).

## Merged Verdicts (Three Branches)

| Branch | Clone | Milestone | Verdict |
| --- | --- | --- | --- |
| A | 0 | `M-EAR-1/real-label-training-v2.1` | **EAR_v2p1_STABLE_FPR_PASS** → mapping label `EAR_v2p1_PARTIAL_WITH_SB3_PASS` |
| B | 1 | `_infra/pre-registration-gate-policy-scope-verification` | **MIXED** |
| C | 2 | `_archive/deprecate-c45-determinism-check` + `_infra/pin-source-date-epoch-anchor` | **DEPRECATION_LANDS_AND_ANCHOR_PINNED** |

Each rubric SHA embedded verbatim in verdict JSON and asserted by dedicated tests.

## Clone-0 — M-EAR-1/real-label-training-v2.1 (SB3 50-Control Re-Verdict)

- **Verdict**: EAR_v2p1_STABLE_FPR_PASS. SB3 50-control FPR = 0.100 reproduces byte-deterministically × 2 across two fresh `tempfile.mkdtemp()` runs; detection = 1.000 (unchanged from c46). SB3 gains a PASS component on both axes; SB1 and SB2 remain FAIL under c26 thresholds (unchanged from c45). Mapping label: `EAR_v2p1_PARTIAL_WITH_SB3_PASS`.
- **Rubric SHA**: `2920875671ea98b127a585bf42ed401110a724b0b6b61fc5aa1bca0cff2abafa`. Three-way byte-equal (rubric doc / `rubric_hash.txt` / `verdict.json.rubric_hash`).
- **Byte-determinism × 2**: `corn_head_v2p1.pt` (`43cd7045…62b17`), `training_result_v2p1.json` (`a030ef16…d9d2f`), `sb3_50ctl_verdict_v2p1.json` (run_1 == run_2 = `c5add489…acb140`).
- **Anchor preservation**: 34/34 SHAs byte-identical pre/post.
- **Tests**: 18/18 PASS (target 16); §61 cross-branch 11/11 PASS (target ≥8).
- **Anti-pattern invariants**: c22 harness NOT re-run (mtimes byte-identical); c23 head-reg unchanged; c25 feature repr verbatim; no PRNG (whitelist `torch.manual_seed(0)`); no `sidecar_nonfactor`; no `i4_stratified`; interpreter guard on every script.
- **13 shadow-ledger events** landed under `-clone-0` suffix (all M-* sub-leaves auto-suffixed by c33 writer guard per c47 Branch B `MIXED` outcome; post-merge integration may normalise substantive M-* per c32 if strict).

## Clone-1 — _infra/pre-registration-gate-policy-scope-verification (Empirical Scope-Verification of c46)

- **Verdict**: **MIXED**. 9 pre-c45 worker-turn commits (all `M-SCORE-1/bridge-api-real-audio-quantization/*` cycles 38-39) prove path (i) WAS satisfiable under earlier session contexts; 141 harness-boundary commits confirm path (ii) is correct for the current context. Rubric §"Frozen verdict set" fires MIXED iff `worker_in_turn > 0 AND periodic_sweep > 0`.
- **Rubric SHA**: `1be2bac55ce595b47b6f369f472c3dadff31024d0447c133fd75bdf0132511cb`. Three-way byte-equal.
- **Byte-determinism × 2**: `commit_classification.tsv` (`119d41d4…`), `session_context_matrix.tsv` (`81bbf452…`), `verdict.json` (`53febe83…`).
- **Session-context matrix**: 7 named class rows + TOTAL row; counts sum to 244 (105 + 36 + 9 + 0 + 0 + 0 + 94).
- **Anchor preservation**: 18 SHAs; 7 c22 stability harness scripts + c46 canonical `determinism_check_c46.py` byte-identical. **Policy-doc prefix (first 3488 bytes)** SHA `d432523e…` byte-equals pre-edit SHA → §1+§2 preserved verbatim under MIXED §3-append.
- **Tests**: 15/15 PASS (target ≥12); §62 cross-branch 8/8 PASS.
- **12 shadow-ledger events** landed under `-clone-1` suffix.
- **Auditor-discipline lemma reinforced**: reading rubric docs off-disk (not from brief paraphrases) prevented over-flagging.

## Clone-2 — Deprecate-c45-Determinism-Check + Pin-SOURCE_DATE_EPOCH-Anchor

- **Verdict**: **DEPRECATION_LANDS_AND_ANCHOR_PINNED**. All 5 rubric gates (a-e) independently verified by auditor: (a) c45 file `os.rename` + `os.utime` moved to `tools/stale/scripts_ear_v2_determinism_check_c45.py` (SHA `d35e0634…8746` preserved; mtime advanced +23,776 s per c38 lesson); (b) grep-zero c45 imports across `scripts/ tools/ tests/` outside `tools/stale/`; (c) c46 canonical `scripts/ear_v2/adjudication/determinism_check_c46.py` SHA `d0e62269…d549d1` byte-identical pre==post; (d) `data/anchor_manifest_v1.json` extended 18→19 with `env/SOURCE_DATE_EPOCH` pinned at `1756463424` (per-value SHA `8ac32472…2d2a4`; entry SHA `30ebead3…1e28c`); (e) byte-determinism × 2 on extended manifest (`138f37a0…3b67f`).
- **Rubric SHA**: `1ab7b6c2c6aeb9bcdac4c234520b8abc9457982aa9969508866777aea1a21387`. Three-way byte-equal.
- **c35 append-only contract preserved**: 18 pre-existing anchor IDs enumerated in `anchor_preservation.json`; only entries-list length grew by 1.
- **Tests**: 15/15 PASS (target ≥12; includes 12+13 anchor-preservation gates); §63 cross-branch 8/8 PASS.
- **11 shadow-ledger events** landed under `-clone-2` suffix.
- **Cycle-46 audit's third MINOR** ("SOURCE_DATE_EPOCH unregistered as anchor") **closed by this branch**.

## Merge-Time Ledger Concatenation

Per-clone shadow ledgers at `/home/user/music-gen-instance/fork-420a6b028dfb/clone-{0,1,2}/promise_ledger.jsonl`:

| Clone | Shadow Rows | Convention |
| --- | --- | --- |
| 0 | 13 | `-clone-0` on infra + substantive M-* sub-leaves (auto-suffixed by c33 writer guard per c47 Branch B MIXED outcome) |
| 1 | 12 | `-clone-1` on infra families; sub-leaves auto-suffixed |
| 2 | 11 | `-clone-2` on infra families |

Post-merge concat: **c32 → c33 → c36 v2 → c39 v3 → c47 Branch B MIXED** convention held; auto-suffix-all behaviour codified. No `LedgerConcatError` expected; concat is deterministic per canonical-hash dedup (c27).

**Merge-report path fallback** (fourth+ observation of sandbox-write refusal): all three clones wrote merge reports to workspace root (`merge_report_c47_branch_{a,b,c}_clone_{0,1,2}.md` or equivalent) per documented c39/c40/c41 precedent. `_infra/merge-report-sandbox-fallback-convention` codification remains a c48 handoff seed.

## State-Machine Discipline (c29 Lemma Respected)

All three substantive milestones are peer sub-milestones under existing terminal-validated parents (or root infra chain):

- `M-EAR-1/real-label-training-v2.1` — peer under M-EAR-1; NOT child of validated v2.
- `_infra/pre-registration-gate-policy-scope-verification` — peer under root infra chain (c14/c22/c32/c33 hardening ancestry).
- `_archive/deprecate-c45-determinism-check` + `_infra/pin-source-date-epoch-anchor` — peer under root infra chain; extends `_infra/anchor-manifest-v1` from c35.

Zero `validated → in_progress` transitions attempted.

## Standing Constraints (Unchanged)

- α pinned at `0.7469387071101908`.
- SHA-256 tiebreak; no PRNG (whitelist `torch.manual_seed(0)` in Clone 0 only); no `sidecar_nonfactor` / `i4_stratified` imports.
- Interpreter guard `/usr/bin/python3` on every new script across all three branches.
- Read-only anchors preserved across all three branches: c6 feature cache + CORN chassis; c9 DawDreamer effects chain; c14 `_ledger_schema.py`; c22 stability harness (7 scripts, mtimes byte-identical); c26 Path B commitment; c31/c33/c34/c35/c36/c37 palette + recreate + anchor-manifest anchors; c45 rubric doc; c46 SB3 widening result + canonical `determinism_check_c46.py`.
- **SOURCE_DATE_EPOCH now first-class anchor at `1756463424`** (Clone 2 landing).
- Rated audio egress-blocked at `*.googlevideo.com`: still `429 + tv_embedded` closure across all three clones; non-blocking probes emit at cycle top per usual. `M-INGEST-1/egress-probe-cycle47-clone-{0,1,2}` rows record failures honestly. Not the two-consecutive `media_ok=true` unblock signal.
- Ledger hygiene: `narrative` field; `run_id="run-2026-08-28T040704Z"`; nested `confidence:{level,rationale,assessor}`; UUID5 content-hash `event_id`; two-arg `append_ledger_event(workspace, event)`.

## Anti-Patterns Locked (5-Count Stable)

c11 CLAP HF SSL; c22 synthetic-label-stability; c23 head-regularization; c25 feature-representation; c35 palette-schema-v2-hydration-render VST3 nondeterminism — not re-attempted across any branch. c30 collision-arc closure at `PARTIAL_BP_UNRESOLVED_SHAPE` unchanged. c31 STILL_GAP surface intact.

## MODERATE / MINOR Findings (Aggregated Across Branches)

**MODERATE (all inherited or explicitly disclosed; none introduced by c47 fanout)**:

1. **Inherited `promise_check` ERROR at ledger line 745** (`_manager/M-EAR-1-real-label-training-v2-unfixable-by-audit-clone-1` uses `supersedes_path` where writer expects `supersedes`; c46 event ts `2026-08-29T17:20:01Z`). NOT Branch A/B/C's. c48 handoff #6: amend row to `supersedes` OR relax `promise_check` per `_infra/ledger-schema-hardening-v2`.
2. **94 `unknown`-bucket commits** in Clone 1 (39% of classified total): `Add music-gen run artifacts …` variants missing `(periodic sweep)`/`(merge …)` envelope. Report §9 discloses conservatively; reclassification would only strengthen MIXED toward CONFIRMED-for-current-context.
3. **Merge-report path fallback** (fourth+ observation): sandbox denies writes to `/home/user/music-gen-instance/…`; workspace-root fallback per c39/c40/c41 precedent.
4. **c33 harness auto-suffix on substantive M-* sub-leaves** in Clone 0: consistent with c33 writer guard behavior; post-merge integration should normalise substantive M-* per c32 if strict. Cosmetic; content correct.

**MINOR (logged, not investigated)**:

- 87 pre-existing cross-branch integration failures in unrelated sections (environmental drift documented by c46 restored context); not touched by any c47 branch.
- Clone 2 relaxed pre-existing §56f anchor_count gate from `== 18` to `>= 18`. Correct under append-only regime but stricter `== 19` would be tighter. Follow-on tightening recommended.
- Clone 0's c33 auto-suffix on substantive M-* sub-leaves visually noisy; c48 `_infra/harness-clone-namespace-guard-single-suffix-refinement` candidate.

## Cycle-48 Handoff (Priority Order; Aggregated Across Branches)

**Highest priority**:

1. **Corpus expansion to 80 songs** (Clone 0 highest-leverage handoff) — SB1/SB2 remain FAIL until corpus grows past 43/80.
2. **Fix c46 line 745 supersede-field drift** — one-line ledger event repair or `promise_check` relaxation.
3. **`_infra/merge-report-sandbox-fallback-convention`** codification (fourth+ observation).
4. **Rubric-doc-not-brief-paraphrase auditor discipline lemma** — codify as durable auditor guidance (c46 → c47 reinforced).

**Medium priority**:

5. **v2 vs v2.1 label reconciliation** note for downstream consumers.
6. **STATISTIC_VERSION = F1_pooled_variance_v1 pin** as formal anchor (Branch C-scoped this cycle; SOURCE_DATE_EPOCH landed; F1 pin follow-on).
7. **Adjudication rubric SHA `975985495b5750668262374080e3c6f0b135be6aa3b1a647f81c0b08c880afa8`** permanent anchor.
8. **Extend anchor manifest with additional environment pins** (`TZ`, `LC_ALL`, `OMP_NUM_THREADS`) as follow-on peer entries under `_infra/pin-source-date-epoch-anchor` chain.
9. **Regex tightening in `_MARKER_RULES`** of Clone 1's `classify_commits.py` to reduce `unknown`-bucket size.
10. **§56f `== 19` tightening** of Clone 2's anchor_count gate.

**Low priority / opportunistic**:

11. **SB2 τ recovery mechanism 2-cell ablation**.
12. **Egress retry cadence formalisation**.
13. **`_infra/harness-clone-namespace-guard-single-suffix-refinement`** (cosmetic).
14. **Path (ii) amendment sunset trigger verification** if a future clone context CAN commit inside a turn.
15. **Retire remaining c41-family standing tickets** if inactive.
16. **Egress retry** per campaign directive (`429 + tv_embedded` unchanged).

## Cumulative Progress

**M-EAR-1 arc** (post-c47 Clone 0):

| Cycle | Milestone | Verdict |
| --- | --- | --- |
| c22-c25 | Path A chassis chain | insufficient (anti-patterns locked) |
| c26 | `_manager/M-EAR-1-path-B-commit` | committed; three SBs frozen |
| c31 | `armed-harness-fixture-reinforcement` | FIXTURE_READY |
| c36 | `real-label-training-v0` | EAR_v0_INSUFFICIENT (43/80) |
| c37 | `_manager/ear-sb3-statistic-degeneracy-fallback-statistic` | F1_ADOPTED |
| c38 | `real-label-training-v1` | EAR_v1_PARTIAL (43/80) |
| c39-c42 | `real-label-training-v2` | PARTIAL_PROGRESS → PIVOT (unfixable-by-audit) |
| c45 (sequential-mode pickup) | `real-label-training-v2` | PARTIAL (F1 pooled-variance leak-test) |
| c46 | SB3 50-control widening probe | boundary-tip signal |
| **c47 Clone 0 (this merge)** | `M-EAR-1/real-label-training-v2.1` | **EAR_v2p1_STABLE_FPR_PASS** (SB3 gains PASS component; SB1/SB2 unchanged FAIL; 43/80 caveat) |

**Infra-hardening chain** (post-c47 fanout close):

| Cycle | Milestone | Status |
| --- | --- | --- |
| c14 | SSoT `_ledger_schema.py` | landed |
| c22 | v2 schema extension | landed |
| c33 guard + c36 v2 writer | fanout-namespace codification | field-tested through c37 + c38 |
| c39 v3 doc | codifies auto-suffix-all | CONVENTION_v3_LANDS |
| c46 | pre-registration gate policy amendment (path (ii)) | landed |
| c47 Clone 1 | empirical scope-verification of c46 amendment | **MIXED** (scope-locked to current session context; path (i) preserved for future in-turn-capable contexts) |
| **c47 Clone 2 (this merge)** | deprecate c45 determinism-check + pin SOURCE_DATE_EPOCH | **DEPRECATION_LANDS_AND_ANCHOR_PINNED** (anchor manifest 18→19) |

**Pattern durability**: **eight consecutive cycles** of rubric-first pre-registration discipline (c26 BP + c27 shape mechanism + c28 hash-space geometry + c29 M3 adjudication + c30 semantic cluster + c37/c38/c45/c46/c47 clones A/B/C). Zero after-the-fact rubric edits.

**c29 state-machine lemma** respected: every c47 branch is a NEW peer sub-milestone; ledger topology stays a DAG.

**c32 → c33 → c36 v2 → c39 v3 → c47 Branch B MIXED** fanout-namespace convention chain: convention formally scope-locked to harness-boundary bucket for the current session context; path (i) preserved as documented option for future in-turn-capable contexts.

**Anchor-manifest arc**:
- **v1.0** (c35): 18 entries frozen under 2-verdict rubric, `MANIFEST_LOCKED`.
- **v1.1** (c47 Clone 2): 19 entries, `DEPRECATION_LANDS_AND_ANCHOR_PINNED`, SOURCE_DATE_EPOCH first-class anchor at `entry_sha256: 30ebead3…1e28c`.
- Post-c47 manifest SHA: `138f37a025304f09e34625ebe5bdf4bd03664e522b32f67225ff90374cf3b67f`.

**Deprecation arc**:
- c45 `scripts/ear_v2/determinism_check.py` archived to `tools/stale/scripts_ear_v2_determinism_check_c45.py` (SHA `d35e0634…8746` preserved).
- c46 `scripts/ear_v2/adjudication/determinism_check_c46.py` remains sole canonical (SHA `d0e62269…d549d1`).

**Pre-registration gate policy arc**: c46 amendment (path (ii)) → c47 Clone 1 empirical MIXED verdict → policy doc §3 appends scope partition. Amendment claim now scope-locked to harness-boundary bucket for current session context.

**Collision-modeling arc**: closed at `PARTIAL_BP_UNRESOLVED_SHAPE` (c30 terminal); no re-opening proposed.

**Ledger state**: **752** rows pre-merge (as-of `_run/cycle_46_closed`); **+11 (Clone 0) + 12 (Clone 1) + 11 (Clone 2) + close/adopt events** → expected post-merge total ~**788**. Distinct milestones grow with c47 sub-leaves per c38/c44/c46 post-merge integration pattern (auto-suffix-all `-clone-<k>` per c47 Branch B MIXED codification).

**Egress**: still `429 + tv_embedded` failure mode across all three clones; two-consecutive `media_ok=true` unblock signal has NOT fired.

**Auditor discipline lemma** (c46 → c47) reinforced: reading rubric docs off-disk (not from brief paraphrases) prevented over-flagging on Clone 1.

**Fanout cadence**: c44 (LINEAR) → c45 (LINEAR) → c46 (LINEAR) → **c47 (3-branch FANOUT, all VALIDATED)**. c48 should resume — either LINEAR on highest-priority handoff (corpus expansion for M-EAR-1) or new fanout based on researcher decision.

**Merge state**: cycle-47 fanout fully absorbed. Three peer sub-milestones landed; anchor manifest extended; c45 module archived; c46 policy amendment scope-verified. Campaign is ready for cycle 48.

[END OUTPUT]
