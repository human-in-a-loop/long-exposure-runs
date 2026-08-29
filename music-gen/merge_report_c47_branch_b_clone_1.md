<!--
created: 2026-08-29T17:52:00Z
cycle: 47
run_id: run-2026-08-28T040704Z
agent: worker
milestone: _infra/pre-registration-gate-policy-scope-verification-clone-1
target_conductor_path: /home/user/music-gen-instance/fork-420a6b028dfb/clone-1/merge_report.md
-->

# c47 Branch B merge report (fork 420a6b028dfb, clone-1)

> **Conductor note:** the assigned harness path
> `/home/user/music-gen-instance/fork-420a6b028dfb/clone-1/merge_report.md`
> is outside this session's workspace sandbox and could not be
> written directly. Prior clone merge reports live at workspace root
> (e.g. `merge_report_c36_branch_a_clone_0.md`); this file follows
> the same convention as `merge_report_c47_branch_b_clone_1.md`.

## Verdict

**MIXED** — the c46 harness-constraint amendment claim holds for the
currently-observed harness session (all cycles-45+ commits land at
periodic-sweep or merge boundaries), but the git-log history also
contains 9 `worker-turn` commits (all under
`M-SCORE-1/bridge-api-real-audio-quantization/*` cycles 38–39) that
prove a prior session context DID permit `git commit` inside a
single worker turn.

Rubric SHA-256: `1be2bac55ce595b47b6f369f472c3dadff31024d0447c133fd75bdf0132511cb`.
Three-way byte-equality asserted (doc SHA == `rubric_hash.txt` ==
`verdict.json.rubric_hash`).

## Reconciliation path fired

**Path C (MIXED)** → appended a new §3 to
`docs/pre_registration_gate_policy.md` documenting the
session-context partition. §1 and §2 preserved verbatim (SHA-256 of
first 3488 bytes of post-edit doc equals the pre-edit SHA
`d432523ec2bdc9a628e02eba2542545e7dc2de4781ac628284fc1157b67f230f`,
asserted in test 08 via anchor manifest).

No sunset ticket emitted — MIXED does not trigger path (i)
reinstatement globally. A follow-up amendment can restore the git-log
gate scope-locally for the in-turn-capable bucket if a future harness
permits in-turn commits.

## Branch B scope-isolation verification

- **c22 stability harness** (`scripts/ear/{synthetic_labels,stability_metrics,stability_audit,features,model,corn,leak_test}.py`
  + `data/ear/stability_audit/*`): SHA-manifest byte-identical
  pre==post (7 script SHAs + 8 data SHAs pinned in
  `data/pre_reg_policy_verify/anchor_preservation.json`; tests 12 +
  §62h assert equality against the current on-disk SHAs). Untouched.
- **c46 canonical `scripts/ear_v2/adjudication/determinism_check_c46.py`**:
  SHA byte-identical pre==post (test 13 + §62h). Untouched.
- **Branch A paths** (`scripts/ear_v2p1/*`, `data/ear_v2p1/*`,
  `docs/ear_real_label_training_v2p1_*`): NOT read by any Branch B
  script; NOT written by this clone. Present on disk from peer
  clone-0's concurrent work (visible via `git status --porcelain`
  but not attributable to this clone).
- **Branch C paths** (`scripts/deprecation_and_anchor_pin/*`,
  `data/deprecation_and_anchor_pin/*`, `data/anchor_manifest_v1.json`):
  NOT read by any Branch B script; NOT written by this clone.
  Present on disk from peer clone-2's concurrent work.

## Writes summary (Branch B allow-list only)

- `docs/pre_registration_gate_policy_scope_verification_rubric.md`
- `docs/pre_registration_gate_policy_scope_verification_report.md`
- `docs/pre_registration_gate_policy.md` — append-only §3 (prefix
  SHA-preserved)
- `scripts/pre_reg_policy_verify/{__init__,grep_git_log,classify_commits,session_context_matrix,verdict}.py`
  (5 files)
- `data/pre_reg_policy_verify/{rubric_hash.txt,git_log_raw.tsv,commit_classification.tsv,session_context_matrix.tsv,verdict.json,determinism_check.json,anchor_preservation.json}`
  (7 files)
- `tests/test_pre_reg_policy_verify.py` (15 plain-assert cases,
  15/15 PASS)
- `tests/test_integration_cross_branch.py` §62 extension (12 checks,
  12/12 PASS)
- `plan_of_record.md` — one row appended to main Milestones table
- `promise_ledger.jsonl` — 12 events appended
- `tools/stale/_c47_branch_b_anchor_preservation.py`
- `tools/stale/_c47_branch_b_emit_events.py`
- `merge_report_c47_branch_b_clone_1.md` (this file)

## Byte-determinism × 2 SHA

| artifact | SHA-256 (run_1 == run_2) |
|---|---|
| commit_classification.tsv | `119d41d4afc850700bd586ad0c87107b8f0fd36c6d2aee6d4531f48afad45a68` |
| session_context_matrix.tsv | `81bbf452f4d376a6f9a6e5f04079947f2d1e2de09cbf91044feec11d77b59aa9` |
| verdict.json | `53febe83b0d638d51064bb958a86074bddfcbd0e403d3a2cb5d0edf648d07de1` |

## Ledger events emitted (12 total, all under `-clone-1` on infra families)

Six named:
1. `_infra/pre-registration-gate-policy-scope-verification-clone-1/rubric-committed`
2. `_infra/pre-registration-gate-policy-scope-verification-clone-1/classification-stable`
3. `_infra/pre-registration-gate-policy-scope-verification-clone-1/verdict-emitted`
4. `_infra/pre-registration-gate-policy-scope-verification-clone-1/amendment-empirically-mixed`
5. `_infra/pre-registration-gate-policy-scope-verification-clone-1/anchor-preservation-verified`
6. `_infra/pre-registration-gate-policy-scope-verification-clone-1/report-published`

Housekeeping pair + open/close + egress-probe + plan-register:
- `_run/cycle_47_launched-clone-1`
- `_plan/register-pre-reg-policy-verify-milestone-clone-1`
- `M-INGEST-1/egress-probe-cycle47-clone-1`
- `_run/cycle_47_closed-clone-1`
- `_archive/cycle-47-scratch-clone-1`
- `_infra/adopt-cycle47-tests-clone-1`

## Test results

- `tests/test_pre_reg_policy_verify.py`: **15/15 PASS**.
- `tests/test_integration_cross_branch.py §62`: **12/12 PASS** for
  Branch B additions. (87 pre-existing failures in other sections
  unchanged; documented environmental drift from prior cycles per
  the c46 restored-context notes.)

## `promise_check` state

- Errors: **1**. Root cause: `_manager/M-EAR-1-real-label-training-v2-unfixable-by-audit-clone-1`
  ledger row at line 745 uses `supersedes_path` but promise_check
  requires `supersedes`. **This is a c46 pre-existing row (cycle 46,
  ts 2026-08-29T17:20:01Z), NOT authored by Branch B.** Out of
  Branch B's scope; flagged here for the conductor / c48 auditor.
- Warns: 2519 (baseline was 2452 at c46; +67 attributable to peer
  clones' concurrent writes + the 12 new Branch B ledger events
  referencing artifacts under fresh directories not yet fully
  adopted). No new warns are attributable to Branch B artifacts
  themselves — the tests + report + rubric are all under adopted
  paths in this clone's ledger events.

## Success gate summary

| gate | status |
|---|:-:|
| Rubric doc landed BEFORE any script (mtime hard) | ✓ |
| verdict.json ∈ {CONFIRMED, LIFTED, MIXED} with three-way rubric_hash byte-equality | ✓ (MIXED) |
| Byte-determinism × 2 SHA-equal on classification + matrix + verdict | ✓ |
| c22 stability harness anchors byte-identical pre==post | ✓ |
| c46 canonical determinism module byte-identical pre==post | ✓ |
| ≥12 test cases green in `tests/test_pre_reg_policy_verify.py` | ✓ (15/15) |
| Cross-branch §62 extended with ≥8 checks | ✓ (12) |
| 0-ERROR promise_check after all events land | ✗ (1 pre-existing c46 error, not Branch B) |
| Ledger events emitted in canonical order under `-clone-1` suffix | ✓ (12) |
| Report at `docs/pre_registration_gate_policy_scope_verification_report.md` with 10-section template | ✓ |
| Merge report | ✓ (this file; conductor may re-home to `/home/user/music-gen-instance/…`) |

## c48 handoff seeds (from report §10)

1. Auditor-reads-rubric-docs lemma from c46 handoff — auditor should
   verify PARTIAL/CONFIRMED/LIFTED/MIXED clauses against the actual
   decision-rule inputs, not paraphrase.
2. Periodic-sweep failure surface: any misclassified `worker-turn`
   commit envelope-wrapped by `(periodic sweep)` would change MIXED
   counts materially — re-run classifier deterministically to catch
   drift.
3. MIXED path (i) restoration ticket: scope-local restoration for
   `worker-turn`/`auditor-turn`/`researcher-turn` if c48+ harness
   permits in-turn commits.
4. c46 `_plan/git-log-gate-policy-amendment` status: LEAVE IN PLACE
   (MIXED does not retire it — claim holds for current harness).
5. Egress retry cadence: HTTP 429 + tv_embedded unchanged; two
   consecutive `media_ok=true` rows remain the unblock signal.
6. **Pre-existing promise_check ERROR at ledger line 745**
   (`_manager/M-EAR-1-real-label-training-v2-unfixable-by-audit-clone-1`
   uses `supersedes_path` not `supersedes`) — c48 auditor should
   either amend the row to include `supersedes` or update
   promise_check to accept both spellings.
