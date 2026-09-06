---
title: "Music-Gen v4 — Cycle 87 (Optional Post-Close Augmentation)"
date: "2026-09-06"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# Music-Gen v4 — Cycle 87 (Optional Post-Close Augmentation)

## Abstract

Cycle 87 executed the pre-registered optional interpolation-hybrid demo per the c70 specification preserved at `M-V4-GEN-1/interpolation-demo-spec` through the intervening cycles, as substantive augmentation of the already-closed v4 campaign. The prior range terminated the campaign cleanly (M-V4-CLOSE-1 LANDS; all seven closure milestones at terminal state; run declared complete per campaign L151-152). This range treats the interpolation demo as the single remaining forward-guidance item that could land autonomously under FD-6 without operator input; it does not re-open the campaign, it augments the closed deliverable set additively. Priority 0 verified the c77 anchor preservation gate: 5 of 6 anchors byte-identical pre-vs-post (`docs/OPERATOR_DECISIONS.md` `b563caee…`; `scripts/ear/v4_ear.py` `e775621b…`; `data/v4/ear/exemplar_set.json` `31c10dfb…`; `data/v4/deliveries/31a164f845f8e27e/cg_ab_mix.wav` `6e13e007…`; `data/v3/rules/rules_artifact.jsonl` `e19fb205…` 76 rules); 1 documented drift on `docs/v4_completion_report_v3.md` `d920c93…` → `b900b0ee…` expected under §P2 additive amendment scope (supersede-by-appending, not re-close). Priority 1 landed the interpolation-hybrid demo end-to-end: `scripts/gen/interpolate_v4.py` (SHA `2359f35d2355647d…`) added as sibling to READ-ONLY c72 `iterate_v4.py` (SHA `8f1f0b8835bdda1d…`); interpolation-demo `ab_mix.wav` SHA `b129c6d1bac8be90fa32249a012a47e5c9e7b369b0707ca6b2f652de478e690a` under byte-determinism ×2 replay proof (`REPLAY_PROOF_HOLDS`, `run1_sha256 == run2_sha256`), distinct from all 15 prior generator iteration renders + 9 focus A/Bs + CG showcase. The worker's interpretation of §P1 step 1 skipped the per-parameter arithmetic-mean probe in favor of the §P1 step 2 SHA-tiebreak fallback on the grounds that VOMM rules are content-hashed corpus instances rather than parameter-tunable vectors — defensible per FD-1 no-fabrication and honestly disclosed in the worker's "Issues and Uncertainties" section. Priority 2 landed the completion-report v3.1 additive amendment at line 244 (`## Section: c78 Interpolation-hybrid demo (optional post-close deliverable)`) with new verdict `INTERPOLATION_DEMO_DELIVERED_pending_operator` and the interpolation WAV SHA `b129c6d1bac8be90…` pinned in-report; total report 363 lines grown from v3 baseline. Priority 3 landed the new `tests/test_gen_interpolate_v4.py` at 6/6 PASS plus regression on prior test files (`tests/test_ear_v4_scaffold.py` 5/5 + `tests/test_gen_iterate_v4.py` 7/7 + `tests/test_ear_batch_scoring_c75.py` 8/8) — auditor-verified subset 26/26; worker-reported cross-cycle total 35/35 monotone-additive without regression. Priority 4 emitted 6 ledger events advancing the ledger 1971 → 1977: `M-V4-GEN-1/interpolation-demo-delivered-c78`; `_plan/completion-report-v3-1-c78-amendment`; `_plan/register-c78-interpolation-demo-sub-leaves`; `_infra/adopt-cycle78-tests`; `_archive/cycle-78-scratch`; `_run/cycle_78_closed`. Delivered set at cycle close totals 25 A/B mixes pending operator ear per FD-6 (9 focus + 15 gen + 1 interpolation demo). Canonical 7-key `env_pin_sha256=2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca` held byte-identical from c22 to c78 across 57 consecutive cycles; FD-16(a) re-issue trigger did not fire. Independent audit returned **VALIDATED**. All §P0-§P4 sufficiency criteria cleared. Campaign M-V4-CLOSE-1 remains LANDS at c77. Cycle 87 is a substantive optional-close-out augmentation, not a re-opening. No autonomous forward work remains in scope; all remaining post-close queue items require operator authority under FD-6. Auditor closes the branch with `[[BRANCH_COMPLETE]]`.

## Introduction

The Music-Gen v4 closure campaign terminated at the prior range with the completion report v3 landing (M-V4-CLOSE-1 LANDS; all seven closure milestones at terminal state; run declared complete per campaign L151-152). The prior range's forward guidance enumerated four optional post-close paths, of which three require operator authority (ear on 24 pending_operator A/Bs; CLAP unblock or alternative backbone; L119 rubric revision) and one could land autonomously under FD-6 without operator input: the interpolation-hybrid demo per the c70 specification preserved at `M-V4-GEN-1/interpolation-demo-spec` through the intervening cycles.

Cycle 87 executes that single autonomous-forward-guidance item as substantive augmentation of the closed deliverable set. It does not re-open the campaign — M-V4-CLOSE-1 remains LANDS at c77 — it appends a new deliverable to the pending-operator A/B set additively under the v3.1 completion-report amendment shape, treating the demo as an optional close-out augmentation rather than a re-opened milestone. This is the correct disposition under the campaign's terminal state: the demo was pre-registered as optional across five prior cycles, its spec was preserved without modification, and its landing per that spec is a discipline-clean single-cycle execution rather than a scope extension.

## Approach

**Five-priority substantive execution.**

- **P0 (c77 anchor preservation gate).** Verified 6 named anchors from the c77 close snapshot pre-vs-post. 5 byte-identical (OPERATOR_DECISIONS.md, v4_ear.py, exemplar_set.json, cg_ab_mix.wav, rules_artifact.jsonl); 1 documented drift on `docs/v4_completion_report_v3.md` `d920c93…` → `b900b0ee…` expected under §P2 additive amendment scope. The drift is supersede-by-appending, not re-close; per FD-1 the anchor is not being replaced but extended, and per c14 the extension carries the string `supersedes_path` semantics rather than the report-level supersede semantics.
- **P1 (interpolation demo landing).** Landed `scripts/gen/interpolate_v4.py` (SHA `2359f35d2355647d…`) as sibling to the READ-ONLY c72 `iterate_v4.py` (SHA `8f1f0b8835bdda1d…`), preserving the existing generator anchor and adding the interpolation-specific driver alongside it. Executed the interpolation per the c70 spec: skipped §P1 step 1 (per-parameter arithmetic-mean probe) on the honest ground that VOMM rules are content-hashed corpus instances rather than parameter-tunable vectors — no per-parameter arithmetic is defined over content-hashed rule instances; fell back to §P1 step 2 (SHA-tiebreak fallback) per the pre-registered protocol. Rendered `ab_mix.wav` SHA `b129c6d1bac8be90fa32249a012a47e5c9e7b369b0707ca6b2f652de478e690a` under byte-determinism ×2 replay proof (`REPLAY_PROOF_HOLDS`, `run1_sha256 == run2_sha256` via fresh `tempfile.mkdtemp()` under 7-key env pins). The resulting SHA is distinct from all 15 prior generator iteration renders + 9 focus A/Bs + CG showcase, confirming the interpolation is a genuine new deliverable rather than a duplicate of prior work.
- **P2 (completion-report v3.1 additive amendment).** Appended `## Section: c78 Interpolation-hybrid demo (optional post-close deliverable)` at line 244 of `docs/v4_completion_report_v3.md` with new verdict `INTERPOLATION_DEMO_DELIVERED_pending_operator` and the interpolation WAV SHA `b129c6d1bac8be90…` pinned in-report. Total report 363 lines (grown from v3 baseline). Post-append SHA `b900b0ee…` per P0 documented drift. This is additive-only amendment preserving the v3 verdict matrix intact; it does not modify or supersede any of the seven M-V4-* milestone verdicts recorded at c77.
- **P3 (test suite).** Landed `tests/test_gen_interpolate_v4.py` at 6/6 PASS covering the interpolation driver's behavior. Regression on prior test files: `tests/test_ear_v4_scaffold.py` 5/5; `tests/test_gen_iterate_v4.py` 7/7; `tests/test_ear_batch_scoring_c75.py` 8/8. Auditor-verified subset 26/26; worker-reported cross-cycle total 35/35 (monotone-additive from the c77 baseline of 29/29 with the +6 new c78 cases). No regressions on preserved anchors.
- **P4 (ledger delta +6).** Six events emitted with UUID5 content-hash `event_id`s, canonical-JSON, `env_pin_sha256=2ac444c3…922ca`, `run_id=run-2026-09-06T…`: `M-V4-GEN-1/interpolation-demo-delivered-c78` (with string `supersedes_path` per c14 lemma → `_gen/batch-score-still-blocked-c76`, the earlier related event); `_plan/completion-report-v3-1-c78-amendment`; `_plan/register-c78-interpolation-demo-sub-leaves`; `_infra/adopt-cycle78-tests`; `_archive/cycle-78-scratch`; `_run/cycle_78_closed`. Ledger 1971 → 1977 (+6).

**Discipline guards asserted.** All AST-scannable invariants pass: no PRNG (VOMM sampling hash-driven deterministic; SHA-tiebreak fallback per §P1 step 2 pre-registered); no `sidecar_nonfactor`; no VST3 state APIs; no `--verify-det` bypass; `/usr/bin/python3` interpreter guard. c14 string-`supersedes_path` lemma honored on the one supersede (`supersedes_path = _gen/batch-score-still-blocked-c76` as string, not list). c47 preservation-spin BAN honored — Cycle 87 is genuinely substantive (new driver + new render + new tests + new report section + new ledger events); deferrals not manufactured. c47 OPT_B emitter-exemption honored (`tools/_emit_c78_ledger_events.py` retained in-tree; `long_exposure/` absent from workspace). FD-1 halt-honest: §P1 step 1 skip is honestly disclosed with defensible rationale in the worker's "Issues and Uncertainties" section rather than fabricated as an executed step; the SHA-tiebreak fallback per §P1 step 2 is pre-registered so falling back to it is protocol-conformant. FD-6 operator authority respected: interpolation demo lands as `INTERPOLATION_DEMO_DELIVERED_pending_operator`; the +1 A/B advances the pending-operator set 24 → 25, all still awaiting operator ear as the only LANDS authority. FD-16(a) env-pin cert unchanged (57-cycle streak c22 → c78); re-issue trigger did not fire. FD-16(c) replay proof landed for the new code path (`interpolate_v4.py`). No wait-on-operator memo (banned per operator directive 2026-09-03 point 2). Six earlier operator-authority escalations remain formally closed on the substantive side; `data/v4/_manager/` state untouched. 18th consecutive cycle in §5 nine-header closing-summary contract compliance (c59 → c78 internal).

## Findings

### Interpolation-hybrid demo lands byte-deterministic per pre-registered spec

`scripts/gen/interpolate_v4.py` (SHA `2359f35d2355647d…`) added as sibling to the READ-ONLY c72 `iterate_v4.py` (SHA `8f1f0b8835bdda1d…`), preserving the existing generator anchor while adding the interpolation-specific driver. Interpolation `ab_mix.wav` SHA `b129c6d1bac8be90fa32249a012a47e5c9e7b369b0707ca6b2f652de478e690a` under `REPLAY_PROOF_HOLDS` byte-determinism ×2 via fresh `tempfile.mkdtemp()` under canonical 7-key env pins. SHA distinct from all 15 prior generator iteration renders + 9 focus A/Bs + CG showcase.

The worker's §P1 step 1 skip in favor of §P1 step 2 SHA-tiebreak fallback is defensible per FD-1 no-fabrication: VOMM rules are content-hashed corpus instances rather than parameter-tunable vectors, so no per-parameter arithmetic-mean probe is defined over them. The SHA-tiebreak fallback is pre-registered in the c70 spec, so falling back to it under this shape-mismatch is protocol-conformant. The rationale is honestly disclosed in the worker's "Issues and Uncertainties" section rather than the skip being reported as an executed step.

### c77 anchor preservation held with one documented additive-amendment drift

Five of six named c77 anchors byte-identical pre-vs-post at Cycle 87 close: `docs/OPERATOR_DECISIONS.md` `b563caee…`; `scripts/ear/v4_ear.py` `e775621b…`; `data/v4/ear/exemplar_set.json` `31c10dfb…`; `data/v4/deliveries/31a164f845f8e27e/cg_ab_mix.wav` `6e13e007…`; `data/v3/rules/rules_artifact.jsonl` `e19fb205…` (76 rules).

The sixth anchor `docs/v4_completion_report_v3.md` drifted `d920c93…` → `b900b0ee…` per the §P2 additive amendment (v3.1 append at line 244). This drift is EXPECTED under §P2 scope: supersede-by-appending, not re-close. Per FD-1 the anchor is being extended additively, not replaced; per c14 the extension carries string-`supersedes_path` semantics on the ledger event rather than report-level supersede semantics. The v3 verdict matrix (M-V4-CERT-1 LANDS + M-V4-PROFILES-1 LANDS_WITH_HONEST_GAPS + M-V4-SHOWCASE-1 LANDS_pending_operator + M-V4-RULES-1 LANDS + M-V4-EAR-1 HALT-HONEST + M-V4-GEN-1 HALT-HONEST_DELIVER_15 + M-V4-CLOSE-1 LANDS) is preserved intact.

### Ledger delta +6 and test suite 35/35 monotone-additive

Ledger 1971 → 1977 (+6) verified with all six events cycle=78 carrying UUID5 content-hash `event_id`s, canonical-JSON, `env_pin_sha256=2ac444c3…922ca`, `run_id=run-2026-09-06T…`. Test suite 35/35 cross-cycle: auditor-verified subset 26/26 (`tests/test_gen_interpolate_v4.py` 6/6 + `tests/test_ear_v4_scaffold.py` 5/5 + `tests/test_gen_iterate_v4.py` 7/7 + `tests/test_ear_batch_scoring_c75.py` 8/8); worker-reported total 35/35 monotone-additive from the c77 baseline of 29/29 with the +6 new c78 cases. No regressions on preserved anchors.

### Delivered set advances 24 → 25 A/B mixes pending operator ear

- 15 generator renders (5 songs × 3 iterations under VOMM primary, seeds 0/1/2, all byte-det ×2 `REPLAY_PROOF_HOLDS`).
- 9 focus A/Bs (CG c17 + 4 c69 v1 non-CG + 4 c71 v2 non-CG).
- 1 interpolation-hybrid demo (SHA `b129c6d1bac8be90…`, byte-det ×2 `REPLAY_PROOF_HOLDS`).

All 25 remain `pending_operator` per FD-6 — expected under operator-ear-only-LANDS authority; not a gap. Operator ear is the only LANDS authority for the delivered set.

### env_pin held 57 consecutive cycles c22 → c78

Canonical 7-key `env_pin_sha256=2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca` held byte-identical from c22 to c78 across 57 consecutive cycles. FD-16(a) re-issue trigger did not fire at Cycle 87 (no environment-touching mutation introduced). FD-16(c) replay proof landed for the new code path (`interpolate_v4.py`) satisfying the per-family per-song replay proof requirement.

### Audit outcome

**VALIDATED.** Zero CRITICAL. Zero MODERATE. All §P0-§P4 sufficiency criteria cleared. The interpolation-hybrid demo — the only remaining forward-guidance item that could land autonomously under FD-6 without operator input — has landed byte-deterministically with a preserved replay-proof, honest per-position SHA-tiebreak semantics (pre-registered fallback per §P1 step 2), and additive-only amendment to the c77 completion report. The 20/20 → 35/35 cross-cycle test progression is monotone-additive; no regressions on preserved anchors.

The single anchor drift (`v4_completion_report_v3.md` SHA delta) is EXPECTED per §P2 append-only amendment and does not constitute an FD-1 halt condition. The worker's interpretation of §P1 step 1 (skipping the per-parameter arithmetic-mean probe in favor of the §P1 step 2 SHA-tiebreak fallback) is defensible per FD-1 no-fabrication and honestly disclosed.

Campaign M-V4-CLOSE-1 remains LANDS at c77. Cycle 87 is a substantive optional-close-out augmentation, not a re-opening. Total pending_operator A/Bs advances 24 → 25, all awaiting FD-6 operator adjudication.

Auditor closes the branch with `[[BRANCH_COMPLETE]]`.

## Discussion

Two things about this cycle — the final autonomous cycle of the Music-Gen v4 campaign — are worth naming.

First, the cycle is a clean example of the correct discipline shape for executing an optional post-close augmentation. The c70 spec was pre-registered as an optional deliverable; the spec was preserved across five intervening cycles without modification; the terminal completion-report v3 at c77 explicitly named it as one of four optional post-close paths of which it was the single one that could land autonomously under FD-6. Cycle 87 executed against that pre-registered spec without scope extension, without re-opening the closed milestone verdicts, and without violating any preservation invariant. The v3.1 additive amendment appended a new section at line 244 with a new verdict class (`INTERPOLATION_DEMO_DELIVERED_pending_operator`) rather than modifying any prior verdict; the anchor drift is documented as expected under append-only semantics. This is what a substantive optional close-out augmentation looks like when the discipline invariants continue to hold: the augmentation is auditable, it does not re-open the closure, and it advances the pending-operator set by one deliverable without violating the FD-6 operator-ear-only-LANDS authority.

Second, the §P1 step-1 skip is a discipline example worth naming for how to handle a spec step that turns out to be structurally undefined against the underlying data model. The c70 spec was authored before VOMM was promoted to primary generator; step 1 assumed a per-parameter arithmetic-mean probe would be defined over the generator's parameter space. Under VOMM, rules are content-hashed corpus instances rather than parameter-tunable vectors — no per-parameter arithmetic-mean is defined. Three shortcut paths were available: (a) fabricate an arithmetic-mean-like operation over the content hashes to satisfy step 1's letter; (b) refuse to execute the demo on the ground that step 1 is unsatisfiable; (c) fall back to the pre-registered step 2 (SHA-tiebreak fallback) and honestly disclose the shape-mismatch. The worker chose (c), which is the correct FD-1 halt-honest response: the fallback is pre-registered so falling back is protocol-conformant; the shape-mismatch is honestly disclosed in the "Issues and Uncertainties" section; the demo lands byte-deterministically under the fallback. The audit endorses the interpretation as "defensible per FD-1 no-fabrication and honestly disclosed." This is what a discipline invariant looks like when it survives a spec-vs-implementation mismatch: the pre-registered fallback carries the demo through, the shape-mismatch is surfaced honestly rather than papered over, and the resulting deliverable is auditable end-to-end.

## Open questions (post-close operator adjudication queue — unchanged from c77)

Per campaign L151-152 the run remains declared complete; the operator verifies post-close. No autonomous forward work remains in scope. The following surfaces await operator adjudication but do not mandate a subsequent cycle:

- **Operator ear on 25 pending_operator A/Bs.** 9 focus + 15 generator + 1 interpolation demo. Operator ear equals LANDS authority per FD-6.
- **Optional CLAP unblock** (via `torchvision::nms` install) or **alternative backbone** (MERT / MULE / HTS-AT) or **L119 rubric revision** if operator wishes to reopen ear-scoring.
- **Optional `CODEBASE_GUIDE.md` refresh** — deferrable indefinitely per c77 forward guidance.

Cycle 87 is the terminal cycle of autonomous scope. If operator supplies a listening verdict on any pending A/B, append acceptance/rejection ledger event via standard cycle framing. No new sub-topic is in scope.

## Appendix: Provenance

**Directive.** Execute the Music-Gen v4 closure campaign; pursue milestones in strict order starting with M-V4-CERT-1 and M-V4-PROFILES-1; drive to a clean close.

**Cycle range.** cycle 87 (single-cycle optional post-close augmentation; internal c78).

**Working directory.** `/home/user/long-exposure-runs/music-gen`.

**Session references.**

- Cycle 87 researcher `bb98e46b-6f14-4a1b-8043-1970dcd84690`; worker `09264878-4623-4067-8beb-6487036c16f0`; auditor `be0131cd-d94a-4a44-9413-08d8d720d261`.

**Audit verdict.** **VALIDATED.** All §P0-§P4 sufficiency criteria cleared. Zero CRITICAL. Zero MODERATE. The auditor closes the branch with `[[BRANCH_COMPLETE]]`.

**Terminal deliverables landed this cycle.**

- `scripts/gen/interpolate_v4.py` (SHA `2359f35d2355647d…`) — interpolation driver added as sibling to READ-ONLY c72 `iterate_v4.py` (SHA `8f1f0b8835bdda1d…`).
- Interpolation-hybrid demo `ab_mix.wav` SHA `b129c6d1bac8be90fa32249a012a47e5c9e7b369b0707ca6b2f652de478e690a` under byte-determinism ×2 replay proof (`REPLAY_PROOF_HOLDS`, `run1_sha256 == run2_sha256`).
- `docs/v4_completion_report_v3.md` v3.1 additive amendment at line 244 (`## Section: c78 Interpolation-hybrid demo (optional post-close deliverable)`); post-append SHA `b900b0ee…`; total report 363 lines; new verdict `INTERPOLATION_DEMO_DELIVERED_pending_operator` pinned with WAV SHA `b129c6d1bac8be90…`.
- `tests/test_gen_interpolate_v4.py` 6/6 PASS.
- Six ledger events: `M-V4-GEN-1/interpolation-demo-delivered-c78` (string `supersedes_path` → `_gen/batch-score-still-blocked-c76`); `_plan/completion-report-v3-1-c78-amendment`; `_plan/register-c78-interpolation-demo-sub-leaves`; `_infra/adopt-cycle78-tests`; `_archive/cycle-78-scratch`; `_run/cycle_78_closed`.

**Ledger delta.** 1971 → 1977 (+6) verified.

**Delivered set at cycle close.** 25 A/B mixes pending operator ear per FD-6: 9 focus (CG c17 + 4 c69 v1 non-CG + 4 c71 v2 non-CG) + 15 generator (5 songs × 3 iterations under VOMM primary, seeds 0/1/2) + 1 interpolation-hybrid demo.

**Read-only anchors preserved byte-identical pre-vs-post (5/6 verified; 1 expected drift under §P2 amendment).**

- `docs/OPERATOR_DECISIONS.md` `b563caee…`
- `scripts/ear/v4_ear.py` `e775621b…`
- `data/v4/ear/exemplar_set.json` `31c10dfb…`
- `data/v4/deliveries/31a164f845f8e27e/cg_ab_mix.wav` `6e13e007…`
- `data/v3/rules/rules_artifact.jsonl` `e19fb205…` (76 rules)
- `docs/v4_completion_report_v3.md` `d920c93…` → `b900b0ee…` (EXPECTED drift under §P2 additive v3.1 amendment)

Additional anchors preserved from prior ranges: `scripts/gen/vomm_generator.py` `e25b520372ff6abd…` byte-identical (READ-ONLY); `scripts/gen/iterate_v4.py` `8f1f0b8835bdda1d…` byte-identical (READ-ONLY); Peach Dream `stem_manifest.json` `d483f2bf0b09389b…` byte-identical (c65 Branch C canonical, 20th-cycle-stable).

**Test suite at cycle close.** 35/35 cross-cycle: auditor-verified subset 26/26 (`tests/test_gen_interpolate_v4.py` 6/6 + `tests/test_ear_v4_scaffold.py` 5/5 + `tests/test_gen_iterate_v4.py` 7/7 + `tests/test_ear_batch_scoring_c75.py` 8/8); worker-reported total 35/35 monotone-additive from c77 baseline. 14 files under `tests/` gate held.

**Environment pin.** Canonical 7-key `env_pin_sha256=2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca` held byte-identical from c22 to c78 across 57 consecutive cycles; FD-16(a) re-issue trigger did not fire this cycle. FD-16(c) replay proof landed for the new code path (`interpolate_v4.py`).

**Discipline guards asserted (AST-scannable).** No PRNG (VOMM sampling hash-driven deterministic; SHA-tiebreak fallback per §P1 step 2 pre-registered protocol). No `sidecar_nonfactor`. No VST3 state APIs. No `--verify-det` bypass. `/usr/bin/python3` interpreter guard. c14 string-`supersedes_path` lemma honored on the one supersede (`_gen/batch-score-still-blocked-c76` as string, not list). c47 preservation-spin BAN honored — Cycle 87 is genuinely substantive (new driver + new render + new tests + new report section + new ledger events); deferrals not manufactured. c47 OPT_B emitter-exemption honored (`tools/_emit_c78_ledger_events.py` retained in-tree; `long_exposure/` absent from workspace). FD-1 halt-honest: §P1 step 1 skip honestly disclosed with defensible rationale rather than fabricated. FD-6 operator authority respected (interpolation demo lands as `INTERPOLATION_DEMO_DELIVERED_pending_operator`; +1 A/B advances pending-operator set 24 → 25, all still awaiting operator ear). No wait-on-operator memo (banned per operator directive 2026-09-03 point 2). All six c47 omnibus-closed operator-authority escalation memos remain formally closed; `data/v4/_manager/` state untouched. §5 nine-header closing-summary contract at 18th consecutive compliant cycle (c59 → c78 internal).

**Terminal milestone status.**

- M-V4-CERT-1 — LANDS (unchanged; env_pin unchanged 57 cycles c22 → c78).
- M-V4-PROFILES-1 — LANDS_WITH_HONEST_GAPS (unchanged).
- **M-V4-SHOWCASE-1** — LANDS_pending_operator (25 A/B mixes at cycle close; +1 from prior range).
- M-V4-RULES-1 — LANDS (unchanged; 76 rules preserved).
- M-V4-EAR-1 — HALT-HONEST (unchanged; c76 L119 infeasibility formal lemma).
- **M-V4-GEN-1** — HALT-HONEST_DELIVER_15 (unchanged for iteration set); augmented by interpolation-hybrid demo landing this cycle as new `INTERPOLATION_DEMO_DELIVERED_pending_operator` verdict on the v3.1 amendment.
- M-V4-CLOSE-1 — LANDS at c77 (unchanged; v3.1 amendment additive).

**Campaign trajectory** (c1 → c78 internal, cycle 87 external).

- c1-c17: Determinism cert + profile sweeps + CG showcase.
- c22: env_pin canonical 7-key subset frozen (`2ac444c3…922ca`); held byte-identical 57 cycles.
- c47: OPERATOR omnibus adjudication (PATH_A composite-FP-drift + OPT1 non-CG bass acceptance + metric-semantics closed); preservation-spin BANNED.
- c69-c71: 8 A/Bs delivered across 4 focus songs (v1 + v2 audibility-gated substitution).
- c72-c74: M-V4-GEN-1 3 iterations × 5 songs = 15 gen renders (VGGish-only fallback after CLAP fetchability failure).
- c75-c76: L119 monotone-infeasibility lemma proved (empirical + analytical); FD-6 delegation activated for M-V4-GEN-1 completion.
- c77: M-V4-CLOSE-1 completion report v3 authored; all seven M-V4-* verdicts terminal.
- **c78 (this cycle)**: interpolation-hybrid demo LANDS byte-deterministic (SHA-tiebreak fallback per §P1 step 2 pre-registered protocol); +6 ledger events; 35/35 tests green; delivered set 25 A/B mixes pending operator ear.

**Auditor's final position.** The Music-Gen v4 closure campaign has been driven to a clean close (c77) and augmented with the optional interpolation-hybrid demo (c78). No further autonomous scope remains. All future work requires operator adjudication under FD-6. Ending this branch cleanly.

[[BRANCH_COMPLETE]]
