---
title: "Music-Gen v3 FOCUS Milestone — Fanout Clone 2: Peach Dream (Cycle 4, escalation escape)"
date: "2026-09-02"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# Music-Gen v3 FOCUS Milestone — Fanout Clone 2: Peach Dream (Cycle 4, escalation escape)

## Abstract

This report covers Cycle 4 of the fanout-clone branch on *Peach Dream* (source SHA-16 `88d247468cb6d49f`) from fork `88d75f9754c3`. Cycles 1–3 of the same branch, covered by an earlier report, ended with the Cycle 3 auditor issuing PIVOT and a CRITICAL escalation to the root conductor after three consecutive turns of the Hold Pattern anti-pattern: Cycle 1 executed substantive setup and launched a background htdemucs task; Cycles 2 and 3 both produced only pause memos and did not authore any substantive artifact, despite explicit anti-Hold-Pattern gating language in the Cycle 2 research brief. The auditor's escalation named three recovery options for the root conductor with a recommendation of Option 3 (accept the three-turn deferral as terminal, merge the substantive on-disk state as a first-class `V3_FOCUS_SONG_PARTIAL`). Cycle 4 is the operationalization of that recommendation. The Cycle 4 research brief scoped the turn to a single-purpose sequential-file-writes-only escape with an explicit anti-Hold-Pattern trip-wire, and the worker landed exactly three primary deliverables: an honest `V3_FOCUS_SONG_PARTIAL` verdict with the required rubric integrity chain, a merge report carrying the three recovery options verbatim with the Option 3 recommendation preserved, and a four-row housekeeping envelope with the emitter script correctly archived. The Cycle 4 audit issued `COMPLETE` with `[[BRANCH_COMPLETE]]`: the three-turn Hold Pattern is broken; the required verdict artifact exists on disk with an honest verb; every rubric integrity assertion holds byte-equal; the branch hands back to the root conductor for Option 1/2/3 selection with the substantive on-disk state preserved as first-class inheritable inheritance for whichever recovery path is chosen. Two moderate findings are logged for the root conductor's post-merge integration: a ledger-visibility gap (the housekeeping rows target the fanout shadow ledger, which is not visible from within the workspace sandbox) and a merge-report path relocation (the intended fanout target `/home/user/music-gen-instance-v3/fork-88d75f9754c3/clone-2/merge_report.md` was blocked by the sandbox, so the merge report landed at the workspace-legal fallback `data/v3/deliveries/88d247468cb6d49f/cycle20/merge_report.md` with the relocation disclosed in the verdict).

## 1. Continuity from Cycles 1–3

The Cycle 3 auditor's PIVOT + CRITICAL escalation packet had named three options: reassign the branch to a fresh clone under a new fork (Option 1); scope-compress into a MuScriptor-only sub-branch and a downstream-sweep sub-branch (Option 2); or accept the three-turn deferral as terminal, merging the substantive on-disk state as a first-class `V3_FOCUS_SONG_PARTIAL` outcome per Fixed Decision 1 with the auditor drafting the PARTIAL verdict at root-conductor level (Option 3, recommended). Cycle 4 is the operationalization of Option 3 by the branch itself under an auditor-carried brief, closing the branch cleanly rather than requiring root-conductor manual composition.

The Cycle 4 research brief scoped the turn to a single-purpose, sequential-file-writes-only escape with an explicit anti-Hold-Pattern trip-wire: *"if at any point you find yourself typing 'I'll wait for' — STOP."* The brief explicitly forbade running MuScriptor, canonicalize, merge, render, vocals-overlay, mix-match, deliver, panel, or the test suite; it forbade any background job; it forbade polling; it capped the wall-time budget at roughly five minutes. Its sufficiency contract required exactly three primary deliverables — a verdict, a merge report, and a four-row housekeeping envelope — followed by immediate termination.

## 2. Cycle 4: honest PARTIAL escape landed in a single turn

### 2.1 Verdict

`data/v3/deliveries/88d247468cb6d49f/cycle20/verdict.json` (3 955 bytes, mtime 18:44) emitted with:

- `verdict = V3_FOCUS_SONG_PARTIAL` (honest verb; deliberately no `LANDS_pending_operator` language)
- `cycle = 20`, `song_sha16 = 88d247468cb6d49f`, `song_name = "Peach Dream"`, `clone = clone-2`, `fork = 88d75f9754c3`
- `blocked_on_operator = true`, `cadence_mode = escalation_partial`, `cycles_since_last_operator_input = 16`
- Three-way `rubric_hash_v2` chain byte-equal at `c49db5a12e955f26c001165ad6e8f9d191bc26bfd96e24c1b163adc37016451a` (document SHA, `rubric_hash_v2.txt` content, verdict field, and dedicated `rubric_hash_v2_chain` object with `chain_byte_equal: true` all identical).
- `c19_backref_sha = 1485f281acb42e3f13d50ee1001b8f1b0be14e733f1b122ea366e2390ada6bfd`, with `c19_backref_verification = live_computed_matches_expected` — the backref was live-computed at emit time and matched the brief-pinned expected value byte-exactly.

The verdict's `honest_partial_reasons` array enumerates five explicit reasons, four brief-mandated plus one honest disclosure:

1. `clone_hold_pattern_terminal_3_turns`
2. `muscriptor_3_of_6_stems_landed_other_piano_vocals_absent`
3. `downstream_chain_not_executed_canonicalize_merge_render_vocals_mix_deliver_panel_rc7`
4. `12_case_test_suite_present_not_executed`
5. `merge_report_target_outside_workspace_sandbox_written_to_workspace_fallback_path_instead`

The `landed_substantive_state` object pins every preserved artifact with a verifiable disk path or SHA: pre-registration scripts (`scripts/v3_spine/peach_dream_c20_*.py`, thirteen files), test file (`tests/test_v3_focus_peach_dream_c20.py`), tempo choice (123.046875 BPM), chosen-section stems (`data/v3/deliveries/88d247468cb6d49f/stems_6s/`), htdemucs full-song 24 SHAs byte-deterministic ×2 (`data/v3_spine/88d247468cb6d49f/htdemucs_determinism.json`), chosen-section window (t = 172.87256235827664 s to t = 202.87256235827664 s from the D1 auto-picker over `focus_set_v2.json`), MuScriptor partial (drums, bass, guitar) and absent (other, piano, vocals) enumerated by name, full-mix probe pending, and the chosen-section vocals SHA `c49d5736e014508e1980f15776e11937c6c997da006fcf28544394c3f5ed891a` with a `vocals_sha_matches_audit_anchor: true` cross-check.

The verdict also carries an `anti_hold_pattern_binding` block explicitly recording the compliance action — `emitted_honest_PARTIAL_this_turn_terminated_loop`, `did_not_emit_pause_memo: true`, `did_not_run_background_job: true`, `did_not_run_muscriptor: true`, `did_not_run_downstream_chain: true` — and a `no_fabrication_declaration` block asserting `fd_1_compliance: true`, `no_lands_language: true`, `verdict_verb_reflects_disk_state: true`, `landed_state_pinned_verifiable: true`, `absent_state_enumerated: true`.

### 2.2 Escalation block

The verdict's `escalation` block carries the Cycle 3 auditor's escalation packet verbatim into the merge handoff:

| Field | Value |
|---|---|
| `status` | `handoff_to_root_conductor` |
| `auditor_severity` | `CRITICAL` |
| `auditor_finding` | `clone_hold_pattern_terminal_after_3_turns_no_substantive_advancement` |
| `auditor_recommendation` | `Option 3 (auditor-drafted PARTIAL merge, unblock root)` |
| `options_named` | three-element array carrying Options 1, 2, and 3 verbatim |
| `recommended_option` | `Option 3` |
| `root_conductor_action_required` | `true` |
| `merge_report_path_intended` | `/home/user/music-gen-instance-v3/fork-88d75f9754c3/clone-2/merge_report.md` |
| `merge_report_path_actual` | `data/v3/deliveries/88d247468cb6d49f/cycle20/merge_report.md` |
| `merge_report_relocation_reason` | `harness_sandbox_blocks_writes_outside_workspace_root` |
| `merge_report_relocation_action` | `root_conductor_should_cp_from_actual_to_intended` |

### 2.3 Merge report

`data/v3/deliveries/88d247468cb6d49f/cycle20/merge_report.md` (9 758 bytes, mtime 18:45) carries the Cycle 3 auditor's three named recovery options verbatim, the Option 3 recommendation, the enumeration of preserved substantive on-disk state, and the intended-vs-actual path disclosure for the root conductor's `cp` at merge time.

### 2.4 Four-row housekeeping

The four housekeeping ledger rows under the `-clone-2` suffix were written by an emitter script that was correctly archived to `tools/stale/_c20_clone2_emit_events.py` after execution (mtime 18:47). The rows target the fork's shadow ledger; from within the workspace sandbox the primary `promise_ledger.jsonl` does not surface them (its mtime of 16:58 pre-dates the 18:45 emission), which is expected behavior for the c33 harness auto-suffix + fanout shadow-ledger pattern. The Cycle 4 auditor flagged this as MODERATE-1 (see §4) and recommended the root conductor confirm shadow-ledger concat picks them up at fanout merge or re-emit under `_run/post-merge-integration-cycle-20-peach-dream` if they fail to appear post-concat.

### 2.5 Scope compliance

Every do-not-do item in the Cycle 4 brief was honored:

- No pause memo emitted.
- No background job launched.
- No MuScriptor invocation attempted.
- No canonicalize, merge, render, vocals overlay, mix-match, deliver, or panel step executed.
- No test suite execution attempted.
- Wall time from first file write (18:44) to emitter archive (18:47) was three minutes, comfortably within the five-minute cap.

The three-turn Hold Pattern is broken. The clone's terminal contract with the fanout is discharged.

## 3. Audit findings and decision

The Cycle 4 audit performed live disk-state verification on eleven distinct checks including the presence of both primary deliverables at their exact expected paths, three independent computations of the three-way rubric hash chain, live re-computation of the c19 backref SHA against the brief-pinned expected value, the verdict verb, the operator-block flag, the cycles-since-last-operator counter, the `honest_partial_reasons` array shape, the escalation options and recommendation, the emitter script archive location, and the promise-check baseline. All ten primary checks passed; one check (ledger-row visibility in the primary workspace ledger) failed as expected and was flagged MODERATE-1 with the shadow-ledger explanation.

The audit issued `COMPLETE` on the grounds that:

- The prior turn's audit had escalated to CRITICAL with recommendation to accept Option 3 as terminal.
- The brief operationalized that recommendation into a single-turn scope with an explicit anti-Hold-Pattern trip-wire.
- The worker delivered exactly the scope the brief mandated (verdict honest, three-way chain byte-equal, escalation block verbatim, three-turn Hold Pattern broken, terminal scope exhausted).
- Continuing further cycles on this clone would violate the brief and re-open the Hold Pattern the auditor had already escalated as CRITICAL-terminal.
- Further Peach Dream work belongs to the root conductor's chosen resume path.

The M-V3-FOCUS-1 substantive milestone on Peach Dream (the full end-to-end chain) is not complete, but that fact is honestly and prominently declared in the verdict. The root conductor holds decision authority on how to finish it.

## 4. Moderate findings for post-merge handling

**MODERATE-1 (ledger-row visibility).** The four housekeeping ledger rows the worker's emitter targeted are not present in the workspace's `promise_ledger.jsonl` at audit time (the file's mtime of 16:58 pre-dates the 18:45 emissions). The emitter script itself is well-formed and correctly archived to `tools/stale/`. The c33 harness's auto-suffix + fanout shadow-ledger pattern routes clone writes outside the workspace, which is not verifiable from within the sandbox. The root conductor should confirm that shadow-ledger concat picks up the rows at fanout merge, or re-emit them under `_run/post-merge-integration-cycle-20-peach-dream` at integration time if they fail to appear post-concat. Severity is MODERATE (not CRITICAL) because the substantive deliverables — `verdict.json` and `merge_report.md` — landed correctly on disk; the ledger rows are bookkeeping.

**MODERATE-2 (merge report path relocation).** The intended fanout path `/home/user/music-gen-instance-v3/fork-88d75f9754c3/clone-2/merge_report.md` is outside the workspace sandbox and was blocked. The merge report landed at the workspace-legal fallback `data/v3/deliveries/88d247468cb6d49f/cycle20/merge_report.md`. Content is unchanged; only the path drifts. The relocation is disclosed honestly in `verdict.escalation.merge_report_relocation_action`; the root conductor should `cp` from the actual path to the intended path at fanout merge time.

**MINOR (c3 anti-pattern coverage).** The c3 anti-pattern `muscriptor-nondeterministic-falsified` — the MuScriptor bass MIDI container-encoding nondeterminism observed in the campaign's third cycle — remains unmeasured on Peach Dream and unmeasured on the three absent stems (other, piano, vocals). Any Option 1 or Option 2 recovery branch that completes the pipeline must handle this per Fixed Decision 1.

## 5. Merge disposition and cross-fork summary

**Merge disposition.** This branch merges as `[[BRANCH_COMPLETE]]` on the strength of Cycle 4's honest escape. The required verdict artifact exists on disk at the required path with an honest `V3_FOCUS_SONG_PARTIAL` verb, a byte-equal three-way rubric chain, a fully-pinned `landed_substantive_state`, a five-element `honest_partial_reasons` array, and a verbatim carry-forward of the Cycle 3 auditor's three-option escalation with Option 3 recommended. The merge report is on disk at the workspace-legal fallback with the intended fanout path disclosed for the root conductor's `cp`. Two MODERATE findings and one MINOR observation are logged for the root conductor's post-merge integration.

**Fork 88d75f9754c3 final summary:**

| Clone | Song | sha16 | Verdict | Merge disposition |
|---|---|---|---|---|
| 0 | What If I Go | `252eb21ce7df7328` | `V3_FOCUS_SONG_PARTIAL_pending_operator` | BRANCH_COMPLETE |
| 1 | Dojo Cuts — Rome | `51e433ade2a845e1` | `V3_FOCUS_SONG_LANDS_pending_operator` | BRANCH_COMPLETE |
| 2 | Peach Dream | `88d247468cb6d49f` | `V3_FOCUS_SONG_PARTIAL` (escalation-escape, honest) | BRANCH_COMPLETE (via Cycle 4 Option 3 operationalization) |

Two of the three clones landed substantive partial or full deliveries in a single fanout cycle; the third landed an honest PARTIAL after an auditor-carried escape at Cycle 4. All three clones close under `[[BRANCH_COMPLETE]]`.

## 6. Campaign-level implications

The Cycle 4 auditor's cumulative notes flag one first-class negative finding for the campaign as a whole: the "single clone attempts full pipeline in one cycle" pattern proved fragile on Peach Dream, and future fanouts for full-pipeline songs should either scope-compress at brief-time (per-stem branches merging into a downstream-integration branch), pre-authorize the auditor-carried Option 3 escape as a first-class success outcome from the outset, or increase per-turn wall budget with explicit go/no-go gates. Rome's clean end-to-end delivery on the same fanout shape demonstrates the pattern can converge; Peach Dream's three-turn Hold Pattern demonstrates it does not always converge.

The M-V3-SPINE-1 Chicken Grease operator-ear gate remains open per Fixed Decision 6 and is unchanged by this cycle. The panel-is-never-a-LANDS-gate discipline under Fixed Decision 6 has held cleanly across every verdict in this campaign. The anti-fabrication contract has held: the Peach Dream branch produced no fabricated LANDS at any point, the pause-memo cycles were flagged and pivoted rather than hidden, and the escape cycle explicitly encoded no-fabrication compliance in the verdict.

## 7. Conclusions

Cycle 4 of the Peach Dream fanout clone-2 branch executed the Cycle 3 auditor's Option 3 recommendation cleanly and closed the branch under `[[BRANCH_COMPLETE]]`. The honest PARTIAL verdict is on disk at the required path with every integrity chain byte-equal; the merge report carries the Cycle 3 auditor's three recovery options verbatim with Option 3 recommended; the four-row housekeeping envelope was emitted (with an expected shadow-ledger visibility gap flagged MODERATE-1 for root-conductor confirmation) and the emitter script archived; the three-turn Hold Pattern is broken; and the operating protocol's "Max regressions before halt: 2" rule was honored via a compliant termination rather than a fourth PIVOT-back. The M-V3-FOCUS-1 substantive Peach Dream milestone remains open — a fact declared prominently in the verdict — and the root conductor holds decision authority on Option 1 (reassign to fresh clone), Option 2 (scope-compress into MuScriptor-only and downstream-sweep sub-branches), or Option 3 (accept the current state as terminal).

## Appendix: Implementation Details

### A.1 Delivered artifacts

Required output artifact: `data/v3/deliveries/88d247468cb6d49f/cycle20/verdict.json` (3 955 bytes, mtime 18:44). Merge report: `data/v3/deliveries/88d247468cb6d49f/cycle20/merge_report.md` (9 758 bytes, mtime 18:45) at workspace-legal fallback path. Emitter script archived at `tools/stale/_c20_clone2_emit_events.py` (mtime 18:47).

### A.2 Verdict fields

`verdict = V3_FOCUS_SONG_PARTIAL`; `cycle = 20`; `song_sha16 = 88d247468cb6d49f`; `song_name = "Peach Dream"`; `clone = clone-2`; `fork = 88d75f9754c3`; `blocked_on_operator = true`; `cadence_mode = escalation_partial`; `cycles_since_last_operator_input = 16`; `verdict_placement_convention = cycle<N>/`; `operator_ear_gate = unchanged_FD_6_operator_ear_only_LANDS_authority`; `cadence_policy_sha = 0be54036...c7f2`.

### A.3 Integrity chains

Three-way rubric-v2 chain: `docs/v3_spine_rubric_v2.md` SHA `c49db5a12e955f26c001165ad6e8f9d191bc26bfd96e24c1b163adc37016451a` == `data/v3_spine/rubric_hash_v2.txt` content == verdict `rubric_hash_v2` field == verdict `rubric_hash_v2_chain.chain_byte_equal: true`. All three sources independently verified live by the auditor.

c19 backref: `1485f281acb42e3f13d50ee1001b8f1b0be14e733f1b122ea366e2390ada6bfd`, live-computed at emit time, matches the brief-pinned expected value byte-exactly (`c19_backref_verification: live_computed_matches_expected`).

### A.4 Landed substantive state preserved

Thirteen pre-registration scripts under `scripts/v3_spine/peach_dream_c20_*.py`; test file `tests/test_v3_focus_peach_dream_c20.py`; tempo choice 123.046875 BPM; chosen-section six stems at `data/v3/deliveries/88d247468cb6d49f/stems_6s/`; htdemucs full-song 24 SHAs byte-deterministic ×2 at `data/v3_spine/88d247468cb6d49f/htdemucs_determinism.json`; chosen-section window t = 172.87256235827664 s to t = 202.87256235827664 s from the D1 auto-picker over `focus_set_v2.json`; MuScriptor 3/6 (drums, bass, guitar) with 3/6 absent (other, piano, vocals) and full-mix probe pending; chosen-section vocals SHA `c49d5736e014508e1980f15776e11937c6c997da006fcf28544394c3f5ed891a` with `vocals_sha_matches_audit_anchor: true`.

### A.5 Honest PARTIAL reasons (verbatim)

1. `clone_hold_pattern_terminal_3_turns`
2. `muscriptor_3_of_6_stems_landed_other_piano_vocals_absent`
3. `downstream_chain_not_executed_canonicalize_merge_render_vocals_mix_deliver_panel_rc7`
4. `12_case_test_suite_present_not_executed`
5. `merge_report_target_outside_workspace_sandbox_written_to_workspace_fallback_path_instead`

### A.6 Anti-fabrication declaration block

`fd_1_compliance: true`; `no_lands_language: true`; `verdict_verb_reflects_disk_state: true`; `landed_state_pinned_verifiable: true`; `absent_state_enumerated: true`.

### A.7 Anti-Hold-Pattern binding block

`adopted: true`; `brief_directive_verbatim: "no more deferrals"`; `compliance_action: emitted_honest_PARTIAL_this_turn_terminated_loop`; `did_not_emit_pause_memo: true`; `did_not_run_background_job: true`; `did_not_run_muscriptor: true`; `did_not_run_downstream_chain: true`.

### A.8 Escalation block for root conductor

`status: handoff_to_root_conductor`; `auditor_severity: CRITICAL`; `auditor_finding: clone_hold_pattern_terminal_after_3_turns_no_substantive_advancement`; `auditor_recommendation: Option 3 (auditor-drafted PARTIAL merge, unblock root)`; `options_named: [Option 1: Reassign Peach Dream to fresh clone under new fork; Option 2: Scope-compress into MuScriptor-3-stems-only branch + downstream-sweep branch; Option 3: Accept 3-turn deferral as terminal; preserve on-disk state as first-class positive]`; `recommended_option: Option 3`; `root_conductor_action_required: true`; `merge_report_path_intended: /home/user/music-gen-instance-v3/fork-88d75f9754c3/clone-2/merge_report.md`; `merge_report_path_actual: data/v3/deliveries/88d247468cb6d49f/cycle20/merge_report.md`; `merge_report_relocation_reason: harness_sandbox_blocks_writes_outside_workspace_root`; `merge_report_relocation_action: root_conductor_should_cp_from_actual_to_intended`.

### A.9 Moderate findings for post-merge handling

MODERATE-1 (ledger visibility): four c20-clone-2 rows targeting the fork's shadow ledger not visible in the workspace's `promise_ledger.jsonl` at audit time (workspace ledger mtime 16:58 pre-dates emission at 18:45); expected fanout-shadow-ledger behavior; root conductor to confirm concat picks up rows at fanout merge or re-emit under `_run/post-merge-integration-cycle-20-peach-dream` at integration time if they fail to appear post-concat.

MODERATE-2 (merge report path relocation): intended fanout path outside workspace sandbox and blocked; actual landing at workspace-legal fallback; content unchanged; root conductor to `cp` from actual to intended at fanout merge time.

MINOR (c3 anti-pattern coverage): MuScriptor bass MIDI container-encoding nondeterminism (`muscriptor-nondeterministic-falsified`) remains unmeasured on Peach Dream and on the three absent stems (other, piano, vocals); any Option 1/2 recovery branch that completes the pipeline must handle per Fixed Decision 1.

### A.10 Validator state

`promise_check`: 0 ERROR, ~3 001 WARN (pre-existing cross-fanout drift; unchanged from prior turn).

### A.11 Wall-time budget

18:44 first verdict file-write → 18:45 merge report file-write → 18:47 emitter script archive. Total wall time roughly three minutes, well within the brief's five-minute cap.

### A.12 Source session

| Cycle | Researcher | Worker | Auditor |
|---|---|---|---|
| 4 | 3f6f0161-e9bc-45d3-a534-b9ba0af23ede | 1dd8bf5e-29e1-447f-8b02-5ee80d4a150b | 87362474-a0a2-47a0-8ad9-9de161ad249d |

### A.13 Fanout metadata

Fork `88d75f9754c3`. Clone 2 of the Peach Dream assignment. Merge report at workspace-legal fallback `data/v3/deliveries/88d247468cb6d49f/cycle20/merge_report.md`; intended fanout path `/home/user/music-gen-instance-v3/fork-88d75f9754c3/clone-2/merge_report.md` requires root-conductor `cp` at merge time per the disclosed relocation action. Sibling clones 0 (WIG) and 1 (Rome) reported separately; all three clones now close under `[[BRANCH_COMPLETE]]`.
