# Verify Stage 6 of 23 — Ear v2.1 + c48 Infra Closure Slice

**Stage:** 7 of 48 (verify 6/23)
**Slice theme:** Close out the ear-arc capstone (M-EAR-1/real-label-training-v2.1, c47) and the two c48 infra hardening milestones that clear the c47-audit backlog. Peer sub-milestones under M-EAR-1 (per c29 state-machine lemma) and under the root `_infra/` chain.

**Verified milestones (3):**
1. `M-EAR-1/real-label-training-v2.1` (c47 clone-0 Branch A) — CONFIRMED
2. `_infra/harness-and-writer-hardening-v3` (c48 clone-0 Branch A) — CONFIRMED
3. `_infra/pre-existing-test-drift-triage-clone-2` (c48 clone-2 Branch C) — CONFIRMED

---

## 1. M-EAR-1/real-label-training-v2.1 → `EAR_v2p1_STABLE_FPR_PASS` (mapping `EAR_v2p1_PARTIAL_WITH_SB3_PASS`)

Peer sub-milestone under M-EAR-1 per c29 state-machine lemma; explicitly NOT a child of validated v2. Reproduces c46 SB3 50-control widening's exact-boundary FPR = 0.100 across two byte-deterministic runs.

### Rubric-hash chain (three-way byte-equality)
- `sha256(docs/ear_real_label_training_v2p1_rubric.md)` = `2920875671ea98b127a585bf42ed401110a724b0b6b61fc5aa1bca0cff2abafa`
- `cat data/ear_v2p1/rubric_hash.txt` = `2920875671ea98b127a585bf42ed401110a724b0b6b61fc5aa1bca0cff2abafa`
- `data/ear_v2p1/verdict.json.rubric_hash` = `2920875671ea98b127a585bf42ed401110a724b0b6b61fc5aa1bca0cff2abafa`
- Three-way chain byte-equal ✓

### SB3 50-control re-verdict (the material change vs c45)
- Run 1 FPR = 0.1000; run 2 FPR = 0.1000 (both at boundary)
- `sha256(sb3_50ctl_verdict_v2p1.json)` run1 = `c5add489eace0a6d3772307ef9ec2d8797a8b75ee49b16f80c73d4f99aacb140`
- `sha256(sb3_50ctl_verdict_v2p1.json)` run2 = `c5add489eace0a6d3772307ef9ec2d8797a8b75ee49b16f80c73d4f99aacb140`
- Byte-determinism × 2 = **True** (verdict `EAR_v2p1_STABLE_FPR_PASS`, not `BOUNDARY_TIP`) ✓
- Run temp dirs from fresh `tempfile.mkdtemp()` (`/tmp/ear_v2p1_sb3_run_1__wud16dt`, `/tmp/ear_v2p1_sb3_run_2_bliz5vth`) — fresh-dir isolation contract satisfied
- Detection = 1.000 (unchanged from c46, PASS)
- SB3 detection_status = PASS, sb3_fpr_status = PASS

### Training determinism (chassis stability)
- `sha256(corn_head_v2p1.pt)` = `43cd7045ac6835baa34a0b714ae91270d65dc62765329c0e5150ce0a3cd62b17` (run 1 == run 2, byte-det × 2 True) ✓
- `sha256(training_result_v2p1.json)` = `a030ef1611a1754ebab6106a48374d8e6666965fd9e56ab1b26f9d1fefcd9d2f` (byte-det × 2 True) ✓
- Both from fresh `tempfile.mkdtemp()` dirs under BLAS + PYTHONHASHSEED=0 + SOURCE_DATE_EPOCH=1756463424 + TZ=UTC + LC_ALL=C.UTF-8 + torch.manual_seed(0)

### SB1/SB2 pre-registered `FAIL_unchanged_from_c45` policy
- `sb1_status` = `FAIL_unchanged_from_c45` — v2.1 correctly does not re-verdict SB1 (per rubric §"Do NOT re-verdict SB1 or SB2")
- `sb2_status` = `FAIL_unchanged_from_c45` — same discipline

### Cross-ref anchor to c45 v2
- Verdict pins `c45_v2_verdict_json_sha256` = `fed3a4605c70a9e02546d9e6deffab28ecb04f0459cdeb9c483c68a43d292d7e`
- On-disk `sha256(data/ear_v2/verdict.json)` = `fed3a4605c70a9e02546d9e6deffab28ecb04f0459cdeb9c483c68a43d292d7e` ✓ (c45 verdict.json is READ-ONLY anchor)
- c46 methodology chain pinned (`c37_f1_pooled_variance` → `c38_leak_lift` → `c46_widening_25_to_50`)

### Anchor preservation
- `n_anchors` = 34 (target ≥32) ✓
- `unchanged` = True; `drift` = [] ✓
- All entries recorded as SHA strings pre==post

### Corpus caveat surfaced
- `corpus_caveat` = `preview_partial_corpus_v2p1`, `corpus_n` = `43_of_80` — 43/80 caveat prominent

**Verdict: CONFIRMED / severity=none.** All rubric gates hold; c26 Path B SB3 boundary-tip resolution byte-deterministic × 2 across two fresh temp dirs. The v2.1 arc closes the SB3 leak-test question honestly (PASS at boundary) without re-verdicting the SB1/SB2 FAIL results.

---

## 2. _infra/harness-and-writer-hardening-v3 → `HARNESS_AND_WRITER_HARDENING_LANDS`

Two-sub-fix c48 upstream infra hardening: (1) substantive/infra namespace split under new env-var toggle; (2) `supersedes` field opt-in inclusion in UUID5 content-hash path.

### Rubric-hash chain
- `sha256(docs/harness_and_writer_hardening_v3_rubric.md)` = `17c5025504d1aca9413bbd3570db08c568fedcae7d32e725ae0933a7bfb27267`
- `cat data/harness_and_writer_hardening_v3/rubric_hash.txt` = `17c5025504d1aca9413bbd3570db08c568fedcae7d32e725ae0933a7bfb27267`
- `verdict.json.rubric_hash` = `17c5025504d1aca9413bbd3570db08c568fedcae7d32e725ae0933a7bfb27267`
- Three-way chain byte-equal ✓

### Baseline replay contract (load-bearing)
- 793 pre-edit rows byte-identical to post-edit
- `baseline_replay_rows` = 793; `baseline_replay_raw_line_matches` = 793 ✓
- `baseline_manifest_sha256` = `c175d65a87bae90be2b8212fbfc0a547ff49964e5fbc30582fef2be5933871f3` (pinned in both `baseline_manifest_sha.txt` and `verdict.provenance`)

### Sub-fix 1 — substantive/infra namespace split
- `sub_fix_1_landed` = True
- Env-var `MUSICGEN_LEDGER_SUBSTANTIVE_EXEMPTION` (default OFF this cycle; c49+ default flip planned)
- Toggle-round-trip fixture: `M-EAR-1/synthetic-test` unsuffixed under flag=1, suffixed under flag=unset (per verdict summary)
- `LedgerNamespaceViolation` MRO preserved: `[LedgerNamespaceViolation, LedgerSchemaError, ValueError, Exception, BaseException, object]` ✓
- `append_ledger_event.__signature__` = `(workspace, event)` — public API unchanged ✓

### Sub-fix 2 — supersedes-in-hash toggle
- `sub_fix_2_landed` = True
- Env-var `MUSICGEN_LEDGER_SUPERSEDES_IN_HASH` (default OFF)
- Flag OFF: c46 line-745 `event_id` = `658231db-5d86-56e5-8ca9-2a9bed7fdf9f` (baseline, matches on-disk) ✓
- Flag ON: alternate UUID5 `event_id` = `6366af60-acb7-5e3f-a2e5-89b47f42c82f` (material behavior-change evidence) ✓

**Verdict: CONFIRMED / severity=none.** Both sub-fixes land under a locked rubric chain; baseline replay contract preserved (793 rows byte-identical); public writer API + MRO invariants preserved. The behavioral toggles are pinned by concrete UUID5 diff evidence, not by prose. Default-OFF this cycle preserves c47 behavior for c48's own emissions; the c49+ default-flip is planned outside this branch.

---

## 3. _infra/pre-existing-test-drift-triage-clone-2 → `DRIFT_TRIAGE_COMPLETE`

Diagnostic-only branch classifying all 87 `tests/test_integration_cross_branch.py` failures against the frozen 4-label taxonomy (c47-non-orthogonal / infra-brittleness / environmental-drift / c47-orthogonal).

### Rubric-hash chain
- `sha256(docs/pre_existing_test_drift_triage_rubric.md)` = `c06059450effc1b190b7c2267d0ed8f9d5f3cd6247bdd01e4672ecea62cf8bf3`
- `cat data/pre_existing_test_drift/rubric_hash.txt` = `c06059450effc1b190b7c2267d0ed8f9d5f3cd6247bdd01e4672ecea62cf8bf3`
- `verdict.json.rubric_hash` = `c06059450effc1b190b7c2267d0ed8f9d5f3cd6247bdd01e4672ecea62cf8bf3`
- Three-way chain byte-equal ✓

### Coverage + classification (load-bearing)
- `captured_failures.jsonl` line count = 87 ✓
- `triage_taxonomy.tsv` line count = 88 (1 header + 87 rows) ✓
- Disposition manifest `total_entries` = 87 ✓
- `verdict.verdict` = `DRIFT_TRIAGE_COMPLETE` (all 87 classified, satisfies COMPLETE threshold)

### c47 CRITICAL surface (the closure-blocking question)
- `verdict.c47_critical_count` = 0 ✓
- `verdict.c47_critical_identifiers` = [] (implied by count=0; disposition_manifest.critical_count = 0)
- Independent re-scan agrees with classification: `c47_overlap_detection.classification_agreement` = True; `soundness_status` = PASS ✓

### Diagnostic-only contract preserved
- Verdict narrative confirms no test file was rewritten (`tests/test_integration_cross_branch.py §60..§62` untouched — matches plan)
- Read-only stance around c47 anchors preserved

**Verdict: CONFIRMED / severity=none.** 87/87 failures classified; zero c47-non-orthogonal criticals; independent overlap re-scan agrees (soundness PASS). Closes c47 audit Issue #1 without touching any test surface.

---

## Cross-milestone observations for this slice

- All three milestones follow the same three-way rubric-hash byte-equality discipline (doc SHA == `rubric_hash.txt` content == `verdict.rubric_hash`). This is now the single load-bearing pre-registration proof across the campaign; every verified cycle in this slice honors it.
- Two of the three (v2.1 SB3, hardening-v3) use fresh `tempfile.mkdtemp()` isolation with env pins for their byte-determinism × 2 assertion, matching the c46/c33 methodology chain.
- c48 successfully retires the last c47-audit backlog items without any anchor drift into the ear-arc or generation-arc surfaces.

## Findings appended this stage: 3

- `M-EAR-1/real-label-training-v2.1` — CONFIRMED / severity=none
- `_infra/harness-and-writer-hardening-v3` — CONFIRMED / severity=none
- `_infra/pre-existing-test-drift-triage-clone-2` — CONFIRMED / severity=none

All appended to `audits/final/findings.jsonl` with structured JSONL entries.
