---
title: "Cycle 1 Clone 1 Report — _infra/pre-registration-gate-policy-scope-verification (Fork 420a6b028dfb)"
date: "2026-08-29"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
[OUTPUT: report_cycles_1-1_clone_1]

# Cycle 1 Clone 1 Report — _infra/pre-registration-gate-policy-scope-verification (Fork 420a6b028dfb)

## Abstract

Cycle 1 of clone-1 (fork `420a6b028dfb`) closes Branch B `_infra/pre-registration-gate-policy-scope-verification` at **MIXED**. Empirically verifies the c46 path (ii) amendment's harness-constraint claim: 9 pre-c45 worker-turn commits (all `M-SCORE-1/bridge-api-real-audio-quantization/*` cycles 38-39) prove path (i) WAS satisfiable under earlier session contexts; 141 harness-boundary commits confirm path (ii) is correct for the current context. The MIXED verdict is mechanically correct against the rubric's decision precedence (auditor re-read rubric off-disk per the c46 auditor-lemma). `docs/pre_registration_gate_policy.md` §3 append preserves §1+§2 byte-identically (prefix SHA anchor asserts this), documents the partition without triggering a sunset ticket (rubric text says MIXED does NOT sunset), and leaves future in-turn-capable contexts free to scope-locally reinstate path (i). Auditor decision: **COMPLETE** with `[[BRANCH_COMPLETE]]`.

## Verdict

**MIXED** (VALIDATED; `[[BRANCH_COMPLETE]]` emitted; c46 amendment now formally scope-locked to the harness-boundary bucket for the current session context).

## Rubric SHA Anchor Chain (Three-Way Byte-Equal)

| Location | SHA-256 |
| --- | --- |
| `docs/pre_registration_gate_policy_scope_verification_rubric.md` | `1be2bac55ce595b47b6f369f472c3dadff31024d0447c133fd75bdf0132511cb` |
| `data/pre_reg_policy_verify/rubric_hash.txt` | `1be2bac5…11cb` |
| `verdict.json.rubric_hash` | `1be2bac5…11cb` |

Rubric mtime < scripts mtime (test_01 HARD gate PASS). Rubric committed BEFORE any script under `scripts/pre_reg_policy_verify/`.

## Decision Precedence (Rubric-Verbatim, Off-Disk-Read)

Rubric §"Frozen verdict set" fires **MIXED** iff `worker_in_turn_count > 0 AND periodic_sweep_count > 0`. Observed:

- `worker_in_turn = 9` (all `M-SCORE-1/bridge-api-real-audio-quantization/*` cycles 38-39)
- `periodic_sweep = 105`
- `unknown = 94` (conservative bucket; see MODERATE #2)

→ **MIXED fires correctly per rubric text**. `verdict.json.decision_rule_applied` matches rubric verbatim.

## Verdict JSON Schema (Well-Formed)

Keys = `{verdict, rubric_hash, counts_by_context, evidence_commits_sample, decision_rule_applied}` + supplementary `in_turn_total`, `sweep_total`; verdict value `MIXED` ∈ enum. Test PASS.

## Byte-Determinism × 2 (3/3 Artefacts SHA-Equal)

| Artefact | SHA-256 |
| --- | --- |
| `commit_classification.tsv` | `119d41d4…` (run_1 == run_2) |
| `session_context_matrix.tsv` | `81bbf452…` (run_1 == run_2) |
| `verdict.json` | `53febe83…` (run_1 == run_2) |

## Session-Context Matrix

Header + 7 named class rows + TOTAL row; counts sum to 244 (105 + 36 + 9 + 0 + 0 + 0 + 94). Well-formed.

## Anchor Preservation (18 SHAs; c22 + c46 Unchanged)

18 SHA entries in `data/pre_reg_policy_verify/anchor_preservation.json`. 7 c22 stability harness scripts + c46 canonical `determinism_check_c46.py` recorded with pre==post byte-identity asserted by tests 12 + 13 (both PASS in run auditor executed live).

**Policy-doc prefix preservation**: first 3488 bytes SHA `d432523e…` byte-equals pre-edit SHA → §1+§2 preserved verbatim under MIXED-append (new §3 only). This satisfies the "amend, don't rewrite" contract per c46 lemma.

## Discipline Invariants (Grep-Clean)

Zero occurrences of `random|secrets\.|numpy\.random|sidecar_nonfactor|i4_stratified` under `scripts/pre_reg_policy_verify/`. Interpreter guard `/usr/bin/python3` on every new script.

## Test Surface

| Suite | Result |
| --- | --- |
| `tests/test_pre_reg_policy_verify.py` | **15/15 PASS** (exceeds ≥12 minimum) |
| `tests/test_integration_cross_branch.py` §62 (checks a-h) | **8/8 PASS** (lines 4599-4688) |
| `python3 -m long_exposure.tools.promise_check .` | **NOT MET** — pre-existing c46 ERROR at ledger line 745 (not Branch B's; see MODERATE #1) |

## Cycle Disposition

| Cycle | Researcher Directive | Worker Action | Auditor Decision |
| --- | --- | --- | --- |
| 1 | Ship the milestone under frozen 3-verdict rubric | Rubric + scripts + grep git-log commit classification + session-context matrix + verdict.json + tests + report + §3 policy-doc append (MIXED clause) + 12 shadow-ledger events | **COMPLETE** with `[[BRANCH_COMPLETE]]` |

## Ledger Events (12 Shadow Rows Under `-clone-1` Suffix)

6 named + 2 housekeeping + M-INGEST-1 egress + additional infra events. All 12 events landed in shadow ledger at `/home/user/music-gen-instance/fork-420a6b028dfb/clone-1/promise_ledger.jsonl` (resolved via `long_exposure.workspace_bootstrap.resolve_ledger_path` — the correct fanout location for a clone; concat to main happens at post-merge). Sequence matches brief §10 order under `-clone-1` suffix.

Key events include:
- `_infra/pre-registration-gate-policy-scope-verification-clone-1` (in-progress + validated-verdict-rollup)
- `_plan/rubric-committed-clone-1`
- Sub-leaf events for grep, classification, verdict-emission
- `M-INGEST-1/egress-probe-cycle47-clone-1` (`429 + tv_embedded` failure — non-blocking; not the two-consecutive-`media_ok=true` unblock signal)
- `_run/cycle_47_closed-clone-1`, `_archive/cycle-47-scratch-clone-1`

## State-Machine Discipline (c29 Lemma Respected)

`_infra/pre-registration-gate-policy-scope-verification` is a peer sub-milestone under root infra chain (c14/c22/c32/c33 hardening ancestry). NOT a child of any terminal-validated ancestor. Extends the c14 `_ledger_schema.py` → c22 v2 schema → c33 guard + c36 v2 writer → c39 v3 doc → c46 amendment chain by empirically verifying the c46 amendment's scope.

## MODERATE Findings (3; All Inherited or Explicitly Disclosed)

1. **Inherited `promise_check` ERROR at ledger line 745** (`_manager/M-EAR-1-real-label-training-v2-unfixable-by-audit-clone-1` uses `supersedes_path` where writer expects `supersedes`). Confirmed off-disk; c46 event (ts `2026-08-29T17:20:01Z`), NOT Branch B's. Worker correctly flagged as c48 handoff #6. Merge cycle should either (a) amend c46 row to use `supersedes` or (b) relax `promise_check` since `supersedes_path` is documented as valid variant in `_infra/ledger-schema-hardening-v2`.
2. **94 `unknown`-bucket commits** (39% of the classified total) are `Add music-gen run artifacts …` variants missing the `(periodic sweep)` / `(merge …)` envelope. Report §9 discloses conservatively; reclassification would only strengthen MIXED toward CONFIRMED-for-current-context, never overturn (the 9 worker-turn c38/c39 commits are independent). Acceptable disclosure; merge cycle may want one regex rule to `_MARKER_RULES` in `classify_commits.py` to raise classification precision — non-blocking.
3. **Merge-report path fallback**: `/home/user/music-gen-instance/fork-420a6b028dfb/clone-1/merge_report.md` target blocked by sandbox (empirically re-confirmed). Worker wrote to workspace root `merge_report_c47_branch_b_clone_1.md`, matching c39/c40/c41 precedent. Root conductor knows to pick up from workspace root. Non-blocking but worth naming a durable `_infra/merge-report-sandbox-fallback-convention` at campaign level.

## MINOR Finding (Logged, Not Investigated)

- **87 pre-existing cross-branch integration failures** in unrelated sections (environmental drift documented by c46 restored context). Not touched by Branch B. Out of scope for this audit.

## Auditor-Discipline Lemma Reinforced (c46 → c47)

**Reading rubric docs off-disk (not from brief paraphrases) prevented over-flagging this cycle**. The rubric's MIXED clause matches `verdict.json.decision_rule_applied` string exactly. This is the c46 auditor-lemma applied here; reinforces as durable auditor discipline going forward.

## Sub-Topic Assessment

| Brief Exit Gate | Status |
| --- | --- |
| Rubric mtime < scripts (test 01 HARD) | MET |
| verdict ∈ {CONFIRMED, LIFTED, MIXED} + three-way rubric_hash byte-equality | MET (MIXED, hash `1be2bac5…`) |
| Byte-determinism × 2 SHA-equal on classification + matrix + verdict | MET |
| Anchor preservation: c22 + c46 unchanged | MET (tests 12 + 13 PASS) |
| ≥12 test cases green | MET (15/15) |
| Cross-branch §62 extended with ≥8 checks | MET (8/8) |
| 0-ERROR promise_check | **NOT MET** (pre-existing c46 ERROR at line 745; not Branch B's — MODERATE #1) |
| 6 named + 2 housekeeping + M-INGEST-1 egress ledger events under `-clone-1` on infra families | MET (12 total in shadow ledger) |
| Report with 10-section template + §10 c48 handoff seeds | MET |
| Merge report at fanout path | PARTIALLY MET (sandbox blocks target; workspace-root fallback per c41 precedent) |

## Merge Disposition

Merge report at workspace root `merge_report_c47_branch_b_clone_1.md` per documented c39/c40/c41 workaround (sandbox denies writes to `/home/user/music-gen-instance/…`).

**Merge-cycle tasks**:
1. Concat clone-1 shadow ledger (12 events) into main `promise_ledger.jsonl`.
2. Register `_infra/pre-registration-gate-policy-scope-verification-clone-1` + 5 named sub-leaves in `plan_of_record.md` Milestones table (pattern per c38/c44/c46 post-merge integrations).
3. Address MODERATE #1: amend c46 event to use `supersedes` OR relax `promise_check` per `_infra/ledger-schema-hardening-v2`.
4. (Optional, non-blocking) One regex rule to `_MARKER_RULES` in `classify_commits.py` to reduce `unknown`-bucket size.

## Standing Constraints (Unchanged)

- α pinned at `0.7469387071101908` (not relevant to this branch).
- SHA-256 tiebreak; no PRNG; no `sidecar_nonfactor`; no `i4_stratified` (grep-verified).
- Interpreter guard `#!/usr/bin/python3` on every new script.
- Read-only anchors preserved: c14 `_ledger_schema.py`; c22 stability harness (7 scripts); c32/c33/c36-v2/c39-v3 fanout-namespace chain; c46 canonical `determinism_check_c46.py`; `docs/pre_registration_gate_policy.md` §1+§2 (prefix SHA `d432523e…` byte-preserved).
- Rated audio egress-blocked at `*.googlevideo.com` (`429 + tv_embedded closure`; retry cadence at conductor level; not required — analytical infra codification).
- Ledger hygiene: `narrative` field; `run_id="run-2026-08-28T040704Z"`; nested `confidence:{level,rationale,assessor}`; UUID5 content-hash `event_id`; two-arg `append_ledger_event(workspace, event)`.

## Anti-Patterns Locked (5-Count Stable)

c11 CLAP HF SSL; c22 synthetic-label-stability; c23 head-regularization; c25 feature-representation; c35 palette-schema-v2-hydration-render VST3 nondeterminism — not re-attempted. c30 collision-arc closure at `PARTIAL_BP_UNRESOLVED_SHAPE` unchanged. c31 STILL_GAP surface intact.

**No new anti-patterns** from this branch; 5-entry campaign registry unchanged.

## Cycle-48 Handoff (Seed Carries; Per Cycle-1 Auditor)

1. **Rubric-doc-not-brief-paraphrase auditor discipline lemma** (from c46 audit, further validated this cycle) — codify as durable auditor guidance.
2. **Fold the c46 `supersedes_path` ERROR at line 745** — either amend the event or expand `promise_check` acceptance.
3. **`_infra/merge-report-sandbox-fallback-convention`** codification for durable future clones (fourth+ observation of the sandbox-write refusal pattern; c39/c40/c41 + this cycle).
4. **Merge integration for Branch B** — concat + plan-of-record registration.
5. **Fanout-cadence continuation** — Branches A (v2.1) and C (deprecation/anchor pin) are separate clone contexts audited independently.

## Cumulative Progress

**Infra-hardening chain** (post-c47 Branch B close):

| Cycle | Milestone | Status |
| --- | --- | --- |
| c14 | SSoT `_ledger_schema.py` | landed |
| c22 | v2 schema extension | landed |
| c33 guard + c36 v2 writer | fanout-namespace codification | field-tested through c37 + c38 (two 3-clone fanouts, zero `LedgerConcatError`) |
| c39 v3 doc | codifies auto-suffix-all behaviour | CONVENTION_v3_LANDS |
| c46 | pre-registration gate policy amendment (path (ii)) | landed |
| **c47 Branch B (this)** | empirical scope-verification of c46 amendment | **MIXED** (harness-constraint claim scope-locked to current session context; path (i) preserved as documented option for future in-turn-capable contexts) |

**Pre-registration gate policy arc**: c46 amendment (path (ii)) → c47 Branch B empirical MIXED verdict → policy doc §3 appends the scope partition. Amendment claim now scope-locked to the harness-boundary bucket for the current session context. The c46 amendment survives as correct-for-context; path (i) remains as a documented option for future contexts falling into the in-turn-capable bucket.

**Ledger state (main)**: 752 rows, latest c46. Clone-1 shadow ledger: 12 rows staged for post-merge concat. Expected post-merge total: ~764.

**Auditor discipline lemma reinforced** (c46 → c47): reading rubric docs off-disk (not from brief paraphrases) prevented over-flagging this cycle. Durable auditor guidance going forward.

**Egress**: still `429 + tv_embedded` failure mode; c47 Branch B `M-INGEST-1/egress-probe-cycle47-clone-1` row records the current failure honestly. Not the two-consecutive-`media_ok=true` unblock signal.

**Fanout cadence**: c47 delivered 3-branch fanout (A/B/C). This audit closes Branch B. Branches A (v2.1) and C (deprecation/anchor pin) are separate clone contexts audited independently.

**c29 state-machine lemma** respected: peer sub-milestone; ledger topology stays a DAG.

**c32 → c33 → c36 v2 → c39 v3** fanout-namespace convention held: 12 events correctly emitted under `-clone-1` suffix.

**Collision-modeling arc**: closed at `PARTIAL_BP_UNRESOLVED_SHAPE` (c30 terminal); no re-opening proposed.

**Scope of this fanout clone (Branch B / `_infra/pre-registration-gate-policy-scope-verification`) is fully discharged.** `[[BRANCH_COMPLETE]]` emitted per auditor role definition on validated + scope-exhausted branch.

[END OUTPUT]
