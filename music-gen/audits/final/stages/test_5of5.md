# Stage 11 — Test 5/5 (Adversarial Closure-Infra Slice, c19–c25+)

**Stage:** 11 of 12 (test 5/5)
**Slice scope:** Closure infrastructure — M-V4-RULES-1/scaffold-c20 stub contract, POR retirement / supersession decisions, `_infra/adopt-cycle*-tests` + `_archive/cycle-N-scratch` + `_run/cycle_N_closed` + `_plan/register-cN-*` housekeeping event structure, and adjacent c21+ ledger drift.
**Wall cap hit:** false
**Findings appended this stage:** 1 (MODERATE, silent-supersession class)

---

## 1. Adversarial verification results

### 1.1 M-V4-RULES-1/scaffold-c20 stub contract — BROKEN ON DISK (test_5of5 primary CRITICAL check)

**POR contract (c20 plan-of-record row):**
- Both `scripts/v4_rules/__init__.py` and `scripts/v4_rules/extract_v4.py` are STUBS.
- Every entry point (`extract_rules_v4` in both pkg init and module; `list_corpus_songs`; `compute_rule_id`) MUST raise `NotImplementedError('c21+ substantive implementation')`.
- `data/v4/rules/scaffold_smoke_test.json` (SHA `8250774547d0c55d…`) must record `all_stubs_raise_c21_plus_notimplemented=true`.
- READ-ONLY anchors: c23 v3-rules `scripts/v3_rules/extract_rules.py` (SHA `9af3e37c…`) + `data/v3/rules/rules_artifact.jsonl` (SHA `e19fb205…`) byte-identical pre==post.
- Substantive extraction (Model A statistical + Model B CA/VOMM sequence) **DEFERRED to c21+**.

**On-disk reality (verified this stage by Read of `scripts/v4_rules/extract_v4.py`):**

| Contract clause | POR narrative | On-disk state | Divergence class |
|---|---|---|---|
| `extract_v4.py` SHA | `1e0ad1131f090003…` (scaffold) | `2b1764e3fa9b4c75f8aa5d48b46478421c12e136caa686460d349332d5af2939` (substantive) | full SHA divergence |
| `__init__.py` SHA | `c8603851d54c56c4…` (scaffold) | `3189da3df7cfb49f84797fa96da1b7eea8a5c069259f3ed2094899879c35f9f4` (substantive) | full SHA divergence |
| Module docstring | scaffold, entry points raise NotImplementedError | "M-V4-RULES-1 substantive extractor. Deterministic given the 7-key env-pin. Reads the five focus songs' merged.mid + section.wav READ-ONLY." | substantive impl (~1060 lines) |
| Header block | cycle: 20, milestone: M-V4-RULES-1/scaffold-c20 | `cycle: 21`, `milestone: M-V4-RULES-1/substantive` | c21+ supersession |
| `extract_rules_v4()` | raises `NotImplementedError('c21+ substantive implementation')` | Runs `extract(Path("."), Path(out_dir))` on the 5-song focus corpus | substantive execution |
| Emitted artifacts | scaffold_smoke_test.json only | `statistical_model.json` + `sequence_model.json` + `audio_descriptors.jsonl` + `rules_artifact.jsonl` + `rules_artifact.sha256` + `manifest.json` + `replay_proof.json` + `env_pin.json` + `ca_retention_summary.json` + `run1/` + `run2/` sibling determinism directories | substantive output tree |
| `data/v4/rules/scaffold_smoke_test.json` | SHA `8250774547d0c55d…` | SHA `8250774547d0c55d08be313787bfb87eb31ff589747b4741cf107e28494c591c` | **BYTE-EXACT MATCH** |

**Ledger cross-check (grep on `promise_ledger.jsonl`):**
- `M-V4-RULES-1/substantive` milestone_id events: **0**
- `_plan/register-c21-v4-rules-substantive-sub-leaves` events: **0**
- All `M-V4-RULES-1/*` milestone_ids in the ledger: only `M-V4-RULES-1/scaffold-c20` and `M-V4-RULES-1/pinned-profile-schema-v1`

**Verdict class:** silent implementation supersession — the c20 scaffold has been overwritten on disk by a substantive c21+ implementation with no ledger event registering the change and no plan-of-record row for `M-V4-RULES-1/substantive`. The substantive extractor itself is genuine, deterministic, env-pinned, `/usr/bin/python3`-guarded, PRNG-free, and `sidecar_nonfactor`-free code (all discipline guards verified by Read of the module).

**Finding logged:** appended to `audits/final/findings.jsonl` as `silent_supersession` MODERATE.

**Reconciliation not proposed here (`reconcile: false`).** Rationale: the substantive c21+ implementation's own status/verdict against the M-V4-RULES-1 success criteria (Two rules models over the operator-approved v3-rendered corpus; artifact hashed; same-input→same-output proof) was never emitted as a ledger event. The appropriate authority to close that gap is the c21+ author, not the final auditor.

**Cross-reference:** the on-disk-scaffold-SHA divergence itself was already logged as MINOR finding #3 (`por_sha_drift`) during stage 4 (verify_4of5). This test_5of5 finding reclassifies the same on-disk divergence as MODERATE `silent_supersession` because the stage-4 finding treated it as narrative transcription drift, but Read of the module docstring proves substantive supersession.

### 1.2 POR retirement / supersession decisions — CLEAN

Verified selected `_plan/*-supersede*` / `_archive/*-superseded*` events use `supersedes_path` as `str` (per c14 lemma), never as list. Sampled:
- `_plan/m-recreate-2-rubric-v2-supersede` (c50): `supersedes_path: docs/m_recreate_2_accurate_small_set_rubric.md` (str) — OK
- `_plan/adopt-operator-per-stem-directive-2026-09-02` (c3): `supersedes_path: docs/PIVOT_v3_simplest_robust_pipeline.md` (str) — OK
- `_plan/adopt-operator-checkpointed-driver-directive-2026-09-03` (c24): `supersedes_path: docs/v3_spine_unified_driver_spec.md` (str) — OK

`_infra/ledger-schema-hardening-v2` (c14) SSoT enforces `supersedes_path` as str; validator has been in place since c14. No supersede-chain drift in the delta-audit slice.

### 1.3 Housekeeping event pattern — STRUCTURALLY SOUND

Ledger-wide grep counts (whole ledger, not delta-scoped, since the pattern is cross-cycle by construction):

| Event family | Count | Comment |
|---|---|---|
| `_archive/cycle-N-scratch` (and variants) | 124 | Codified in plan-of-record §"Housekeeping event pattern" |
| `_infra/adopt-cycleN-tests` (and variants) | 122 | Codified same section |
| `_run/cycle_N_closed` (and variants) | 54 | Rollup event |
| `_plan/register-cN-*` (and variants) | 55 | Plan-of-record registration event |

Pattern is stable, discoverable via grep, and preserves the promise-check contract (no milestone-id drift). One structural observation, not logged as a finding: the raw count of `_archive/cycle-N-scratch` (124) exceeds `_run/cycle_N_closed` (54) — the ratio reflects fanout, per-clone, and named-scratch variants that accreted across cycles 3–28 before the c29 hardening pinned the canonical two-event form. All variants respect the append-only + content-hash-derived-event_id invariants.

### 1.4 `_infra/adopt-cycle21-tests-clone-0` structure — CLEAN

Random-adversarial spot check on the c21 clone-0 housekeeping event (chosen because the c21 fanout was one of the most complex three-clone forks in the run):
- Structure per `promise_ledger.jsonl`: `status: validated`, `confidence.level: high`, nested `confidence`, `narrative` field (not `summary`), pinned `run_id`, UUID5 content-hash `event_id`.
- Fired AFTER `_run/post-integration-cycle-21-wig-restart-clone-1` per the c29 hardening ordering.
- Cross-references live under `_plan/register-c21-fanout-and-integration-milestones` for POR-side reconciliation.
- No milestone-id namespace violation (c33 harness auto-suffix path applied correctly to the `-clone-0` infra label).

### 1.5 c22 unified-driver + c24 checkpointed-driver retirement contingency — CLEAN

`_infra/retire-oneoff-drivers-c22` (c22): 37 per-song `*_song_<sha16>.py` scripts cataloged for deletion contingent on reproduce-proof green. C23 clone-0 delivered `REPRODUCE_PANEL_ONLY` on both Chicken Grease and Rome. Per `M-V3-SPINE-2/reproduce-proof-authorizes-c24-retirement`, deletion is UNBLOCKED. Retirement itself queued for a future cycle after operator directive #3 (Peach Dream A/B delivery via checkpointed driver) lands. Honest deferral, correctly recorded.

### 1.6 Freshness-cache short-circuit policy (c24, N=3) — CLEAN

`_plan/freshness-cache-short-circuit-policy` (c24) documents the orchestrator-layer policy at `docs/freshness_cache_short_circuit_policy.md`. Ledger event is honest bookkeeping ("this policy lives above the worker layer; this cycle documents the recommendation for orchestrator implementation") — no over-claim of implementation.

### 1.7 M-V3-RULES-1/first-activation (c23) — CLEAN

Verified deterministic extractor + 76 typed rules on disk + 33-anchor preservation manifest holds. Path-drift on spec doc location (`docs/v3_rules_deterministic_extractor_spec_c23.md` narrated vs `docs/specs/v3_rules_deterministic_extractor_spec_c23.md` on disk) already logged as finding #1 MINOR in verify stages; no reopen. Three-way `rubric_hash_v3_rules` chain is preserved under the on-disk path.

---

## 2. Regression / adjacent-behavior probes

- The M-V4-RULES-1/substantive extractor's structure (Model A statistical + Model B CA/VOMM + audio descriptors + v3-shape rules artifact) is consistent with the M-V4-RULES-1 success criterion ("Two rules models over v3-rendered corpus... artifact hashed; same-input→same-output proof"). Under the "run1/ + run2/ + replay_proof.json" sibling determinism directories present on disk, the substantive impl appears to have satisfied the same-input→same-output proof internally. Not verified deeper this stage (out of test_5of5 scope — the finding is the audit-trail gap, not the code correctness).
- No new issues in the housekeeping-event family. No regression class introduced by the c22 unified-driver / c24 checkpointed-driver contingencies.
- `_manager/M-V4-METRIC-SEMANTICS-c16` remains `action_required` / `blocked_on_operator=true` — carried forward from stage 3 (test_3of5) finding #6 without change.

---

## 3. New findings introduced this stage

**One (1) MODERATE finding, appended to `audits/final/findings.jsonl`:**

- **`M-V4-RULES-1/scaffold-c20` — `silent_supersession` — MODERATE.** The c20 scaffold stub contract is broken on disk by an unregistered c21+ substantive implementation. See finding row for full detail (POR SHAs, on-disk SHAs, orphaned artifact list, ledger-grep evidence, recommended reconciliation event contour).

---

## 4. Findings NOT logged (deliberately)

- **c20 scaffold POR SHA drift on `__init__.py` + `extract_v4.py`:** already logged as MINOR finding #3 in prior verify stage. This stage's MODERATE finding supersedes it in classification; the MINOR finding stays in the ledger as an earlier-cycle observation.
- **General POR-narrative-transcription-drift pattern across findings #2, #4, #5:** class-level pattern already acknowledged; no synthesis finding needed.
- **`_archive/cycle-N-scratch` count divergence (124 vs 54 rollups):** structural observation only; not a defect.

---

## 5. Cumulative delta-audit findings summary

| # | Severity | Class | Milestone |
|---|---|---|---|
| 1 | MINOR | path_drift | M-V3-RULES-1/first-activation/rubric-committed |
| 2 | MINOR | por_anchor_drift | M-V4-PROFILES-1/cg-bass-sf2-replay-proof-v2 |
| 3 | MINOR | por_sha_drift | M-V4-RULES-1/scaffold-c20 |
| 4 | MINOR | por_anchor_drift | M-V4-PROFILES-1/cg-bass-sf2-replay-proof |
| 5 | MINOR | por_anchor_drift | M-V4-PROFILES-1/cg-drums-profile-v1-emitted |
| 6 | MODERATE | open_escalation_confirmation | _manager/M-V4-METRIC-SEMANTICS-c16 |
| 7 | MODERATE | silent_supersession | M-V4-RULES-1/scaffold-c20 (this stage) |

**Total:** 5 MINOR + 2 MODERATE + 0 CRITICAL. No reconciliation events proposed (all `reconcile: false`). All findings are audit-trail / classification issues; none invalidate any operator-blessed or internal-gate-blessed substantive deliverable. Post-baseline delta-audit findings ready for consolidation in stage 12 document report.

---

**Ready for stage 12 (document).**
