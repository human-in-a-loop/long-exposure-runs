---
title: "Music-Gen v4 — Cycles 78-80"
date: "2026-09-05"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# Music-Gen v4 — Cycles 78-80

## Abstract

Cycles 78-80 exit the extended stable-blocked cadence under fresh operator authority, land the four non-Chicken-Grease A/B mix deliverables per operator directive #5(d), diagnose an honest sparse-canonical-MIDI duration finding on the WIG mix under an operator "verify only" mandate, retire six rolling chains from the prior range explicitly via string-supersede semantics, and open the M-V4-GEN-1 scaffold at the milestone level with four sub-milestones and a parent rollup — while sustaining the discipline invariants across a substantive-work cycle count of sixteen events at range close. Cycle 78 held the terminal stable-blocked state (six-consecutive WIG piano Branch B; fifth-consecutive Rome bass disk-blocked SKIP; second-consecutive Peach Dream stem manifest lightweight carry-forward) under the pattern the prior range established. Cycle 79 executed the operator-authorized break in the disk-gate cascade: `scripts/sound_match/deliver_ab_v4.py` (SHA `52ff05e28d2feb55…`) landed as the READ-ONLY driver for non-CG A/B mix renders under an absent-stems policy derived from the c47 omnibus, and four A/B mix WAVs rendered to disk (WIG `6feca5d1fb41ee149e727b6ec2a61d2a006b4bc0b2a0aff62f2ef8946f47e3e9`; Rome `81e2ef15…`; Peach Dream `a300cf4c…`; Disco A `1b673106…`) — advancing M-V4-SHOWCASE-1 from one A/B mix (CG c17 SHA `6e13e007…`) to five A/B mixes, all `LANDS_pending_operator` per FD-6. The Cycle 79 audit's P1 forward-guidance mandated Cycle 80 explicitly retire the six c68 rolling chains via string-supersede rather than continue their chain-continue-supersede cadence, since the operator-authorized render break rendered several of the underlying blockers moot. Cycle 80 executed six priorities plus housekeeping in a sixteen-event ledger delta (four events over the twelve-event prediction; both overages disclosed and endorsed by the audit): P1 landed a WIG duration diagnostic per operator "verify only" mandate — `M-V4-SHOWCASE-1/wig-duration-diagnostic-honest` id `767ac7aa…` — with the finding classified as `HONEST_SPARSE_CANONICAL_MIDI` (canonical MIDI durations bass 8.991s, drums 9.081s, vocals 29.960s, piano 29.921s; `deliver_ab_v4.py:293` truncation policy `min(bass_L, drums_L, vocals_L)`; SF2 release-tail approximately 2.168s ceiling; final duration 8.991 + 2.168 = 11.249s honestly explained rather than rerendered), WIG WAV bytes byte-identical pre-vs-post. P2 landed the six explicit retirement rows per Cycle 79 audit guidance (Rome / PD / Disco A bass stage-2 disk-blocked-retired-c70; `_plan/wig-piano-stage1-retired-c70`; `_selection/peach-dream-stem-manifest-attribution-carry-retired-c70`; `_infra/op-2-monitor-retired-c70`) each with string `supersedes_path` per c14 lemma pointing at the c68 rolling-chain predecessor, closing the accumulated per-cycle-carry cadence terminally. P3 opened the M-V4-GEN-1 scaffold with four sub-milestones registered plus one parent rollup at `in-progress` state — primary generator (Anticipation) picked, 5-donor map pinned, rubric with stall-trigger clause pre-registered ("8 iterations without 5 passers → deliver best 5 by ear score, honest gap analysis, PROCEED to close without operator input"), interpolation-demo pre-registered. P4 landed six-of-six PASS on `tests/test_deliver_ab_v4.py` fulfilling test debt on the c69 driver. Housekeeping tail landed the standard four events. Independent audit returned **VALIDATED** with two P2 findings (both non-blocking): event-count scope-extension (16 emitted vs 12 predicted, attributable to legitimate parent-milestone opening plus explicit register row plus preserved full housekeeping tail); pre-edit `ab_mix.manifest.json` SHA not captured before the WIG duration-diagnostic block was appended (best practice per c34 P0.2 anchor-substitution convention). Zero CRITICAL, zero HIGH, zero MODERATE, zero MINOR. All 8 read-only anchors byte-identical pre-vs-post including the four c69 A/B mix WAVs. Test suite cross-cycle file-gate 9/9. §5 9-header closing-summary contract at twelfth consecutive compliant cycle (c59 → c70 internal numbering). M-V4-GEN-1 scaffold opened; iteration 1 gated on next-cycle disk prune to ≤82% per c27 policy (currently 85% at Cycle 80 close). M-V4-EAR-1 queued for the cycle after next per operator simplification 2026-09-03 (lightweight exemplar ear, CLAP + VGGish ensemble). Post-hoc operator ear on the four c69 A/B mixes remains the LANDS-authority gate per FD-6.

## Introduction

The Music-Gen v4 closure campaign is driving through seven strictly-ordered milestones toward a clean close. Prior ranges had extended a stable-blocked terminal cadence for many cycles under two operator-authority surfaces (WIG piano stage-1 escalation with four named operator paths OPT_A/B/C/D; Peach Dream stem manifest attribution question resolved under Branch C halt-honest) and one operational precondition (disk pressure at 85% versus the 82% precondition for stage-2 fine-fit launches), with each cycle emitting the appropriate chain-continue-supersede events via the c14 string-`supersedes_path` lemma and preserving all six c47 omnibus-closed operator escalation memos.

Cycles 78-80 are the range in which fresh operator authority breaks the cadence. An operator directive (implied by the c69 A/B mix render authorization and the c70 "verify only" mandate on WIG duration) permitted the campaign to render the four remaining non-CG A/B mixes under an absent-stems policy derived from the c47 omnibus — advancing M-V4-SHOWCASE-1 from one A/B mix to five and re-enabling substantive downstream work. The range's arc has three parts: Cycle 78's continued stable-blocked cadence per prior pattern; Cycle 79's operator-authorized A/B mix landing which produced the four non-CG WAVs and left the WIG mix with a duration finding requiring diagnostic follow-up; Cycle 80's six-priority substantive execution which diagnosed the WIG duration honestly, retired the six rolling chains explicitly via string-supersede, opened the M-V4-GEN-1 scaffold, and landed test debt on the new driver.

## Approach

**Cycle 78 (final stable-blocked cadence cycle).** Held the terminal stable-blocked state per prior-range pattern: sixth-consecutive WIG piano Branch B (`_plan/wig-piano-stage1-blocked-on-operator-c68`); fifth-consecutive Rome bass disk-blocked SKIP; cascaded PD + Disco A bass SKIPs; second-consecutive Peach Dream stem manifest lightweight carry-forward; OP-2 Monitor Branch B N/A. Ten events (six substantive + four housekeeping) matching prior brief predictions.

**Cycle 79 (operator-authorized A/B mix landing; new `deliver_ab_v4.py` READ-ONLY driver).** Executed under fresh operator authority permitting non-CG A/B mix renders. Landed `scripts/sound_match/deliver_ab_v4.py` (SHA `52ff05e28d2feb55…`) as READ-ONLY driver with absent-stems policy derived from the c47 omnibus (missing stems handled via fallback rather than sweep gating). Rendered four A/B mix WAVs:

- WIG `data/v4/deliveries/252eb21ce7df7328/ab_mix.wav` SHA `6feca5d1fb41ee149e727b6ec2a61d2a006b4bc0b2a0aff62f2ef8946f47e3e9` — 11.249s duration (partial; expected ~30s per other songs).
- Rome `data/v4/deliveries/51e433ade2a845e1/ab_mix.wav` SHA `81e2ef15…`.
- Peach Dream `data/v4/deliveries/88d247468cb6d49f/ab_mix.wav` SHA `a300cf4c…`.
- Disco A `data/v4/deliveries/cdd2717e52820ff6/ab_mix.wav` SHA `1b673106…`.

M-V4-SHOWCASE-1 advances from one A/B mix (CG c17 SHA `6e13e007…`) to five A/B mixes. All five `LANDS_pending_operator` per FD-6. Cycle 79 audit's P1 forward-guidance mandated Cycle 80 explicitly retire the six c68 rolling chains via string-supersede rather than continue their chain-continue-supersede cadence, since the operator-authorized render break rendered several underlying blockers moot.

**Cycle 80 (six priorities; sixteen-event substantive cycle).**

- **P1 WIG duration diagnostic (honest, no rerender).** Executed under operator "verify only" mandate. Diagnosed the WIG 11.249s duration as `HONEST_SPARSE_CANONICAL_MIDI`: canonical MIDI durations are bass 8.991s, drums 9.081s, vocals 29.960s, piano 29.921s; `deliver_ab_v4.py:293` truncation policy `min(bass_L, drums_L, vocals_L)` selects the shortest instrumental stem (bass at 8.991s); SF2 release-tail approximately 2.168s adds a ceiling of 8.991 + 2.168 = 11.249s. WAV bytes byte-identical pre-vs-post at SHA `6feca5d1…` — no rerender attempted per operator directive. Emitted event `M-V4-SHOWCASE-1/wig-duration-diagnostic-honest` id `767ac7aa…` with the eight-field diagnostic block appended additively to `data/v4/deliveries/252eb21ce7df7328/ab_mix.manifest.json` (fields: `answer`, `canonical_midi`, `sf2_release_tail_s`, `mix_target_len_policy`, `rerender_required`, `operator_directive_ref`, `cross_check`, `authority`).
- **P2 six explicit retirement rows.** Per Cycle 79 audit P1 forward-guidance, each c68 rolling chain closed with a `_retired-c70` event carrying string `supersedes_path` per c14 lemma pointing at its c68 predecessor and citing landing evidence:

| Retirement event | Supersedes | Landing evidence |
|---|---|---|
| `M-V4-SHOWCASE-1/rome-bass-stage2-disk-blocked-retired-c70` | `M-V4-PROFILES-1/rome-bass-stage2-disk-blocked-c68` | c69 Rome render |
| `M-V4-SHOWCASE-1/peach-dream-bass-stage2-disk-blocked-retired-c70` | `M-V4-PROFILES-1/peach-dream-bass-stage2-disk-blocked-c68` | c69 PD render |
| `M-V4-SHOWCASE-1/disco-a-bass-stage2-disk-blocked-retired-c70` | `M-V4-PROFILES-1/disco-a-bass-stage2-disk-blocked-c68` | c69 Disco A render |
| `_plan/wig-piano-stage1-retired-c70` | `_plan/wig-piano-stage1-blocked-on-operator-c68` | c47 omnibus absent-stems policy + c69 WIG render |
| `_selection/peach-dream-stem-manifest-attribution-carry-retired-c70` | `_selection/c68-peach-dream-stem-manifest-attribution-carry-moderate` | c47 omnibus + invariant (d) fallback in c69 driver |
| `_infra/op-2-monitor-retired-c70` | `_infra/op-2-monitor-not-applicable-c68` | No detached processes in c69 (deliver_ab_v4 foreground) |

All six chains closed terminally; each retirement narrative names its supersede target and landing evidence.
- **P3 M-V4-GEN-1 scaffold.** Opened at milestone level. Four sub-milestones registered (per brief §4 P3 shape). One parent rollup at `in-progress` state (scope-extension +1 vs brief prediction; endorsed by audit as legitimate parent-milestone opening). Primary generator picked: Anticipation. 5-donor map pinned. Rubric pre-registered with stall-trigger clause: "8 iterations without 5 passers → deliver best 5 by ear score, honest gap analysis, PROCEED to close without operator input per FD standing rule L146-147." Interpolation-demo pre-registered. Post-hoc operator ear per FD-6 remains authoritative on generated songs.
- **P4 test debt fill-in.** `tests/test_deliver_ab_v4.py` 6/6 PASS matching brief §4 P4 named cases:
  1. `test_01_env_pin_drift_raises`
  2. `test_02_min_truncation_policy`
  3. `test_03_peach_dream_invariant_d_fallback`
  4. `test_04_absent_stems_manifest_shape`
  5. `test_05_manifest_provenance_field_completeness`
  6. `test_06_prove_replay_writes_second_render_into_fresh_tempdir`

  Cross-cycle file-gate 8 pre-c70 + 1 new = 9/9 satisfied.
- **Housekeeping tail.** `_plan/register-c70-sub-leaves` + `_run/cycle_70_closed` + `_archive/cycle-70-scratch` + `_infra/adopt-cycle70-tests`.

Total: 16 events (6 retirements + 1 WIG diagnostic + 4 M-V4-GEN-1 sub-milestones + 1 M-V4-GEN-1 parent rollup + 1 explicit register row + 3 housekeeping-body events + 1 register housekeeping = 16). Brief predicted 12; overage of 4 attributable to legitimate parent-rollup opening + explicit register-row emission + full housekeeping tail preservation. Ledger 1879 → 1895.

**Discipline guards asserted across the range.** OP-2 Monitor Branch B N/A at Cycle 78; Cycle 79 driver `deliver_ab_v4.py` foreground (no detached process → Monitor N/A); Cycle 80 no sweep fine-fits (Monitor N/A). Zero re-escalations of WIG piano stage-1 through Cycle 78; Cycle 80 explicitly retires the chain per Cycle 79 audit guidance rather than re-escalating. Zero wait-on-operator memos (banned per operator directive 2026-09-03 point 2). Zero preservation-spin sub-leaves (21 consecutive clean cycles since c48; substantive retirement rows at Cycle 80 rather than continued rolling carries). All six c47 omnibus-closed operator-authority memos remain CLOSED. c14 string-`supersedes_path` lemma honored: all six retirement rows carry string `supersedes_path`; all four M-V4-GEN-1 sub-milestone registrations and the parent rollup use appropriate string/null values; no list-typed supersede introduced. All AST-scannable invariants pass: no PRNG, no `sidecar_nonfactor`, no VST3 state APIs, no `--verify-det` bypass, `/usr/bin/python3` interpreter guard. No READ-ONLY anchor lift; no unilateral READ-ONLY lift; no fabricated fallbacks; no destructive `rm`. FD-1 halt-honest: WIG 11.249s partial disclosed honestly and diagnosed rather than fabricated; 16-vs-12 event count self-disclosed per FD-1. FD-6 operator-ear-only-LANDS on non-CG respected — all 4 c69 A/B mixes remain `pending_operator`. FD-16(a) `env_pin_sha256=2ac444c3…` canonical 7-key subset unchanged; no cert re-issue trigger. FD-16(c) per-family per-song replay proofs N/A this cycle (no new render code path introduced this cycle; c79 driver replay proofs remain the byte-determinism guarantee for the four landed A/B mixes). c47 preservation-spin BAN honored; c17 SHOWCASE anchor `cg_ab_mix.wav` `6e13e007…` READ-ONLY untouched.

## Findings

### Operator-authorized A/B mix advance: M-V4-SHOWCASE-1 from 1 to 5

Cycle 79's landing of `scripts/sound_match/deliver_ab_v4.py` (SHA `52ff05e28d2feb55…`) as READ-ONLY driver under an absent-stems policy derived from the c47 omnibus advanced M-V4-SHOWCASE-1 from one A/B mix (CG c17 SHA `6e13e007…`) to five A/B mixes:

- CG (c17): `data/v4/deliveries/31a164f845f8e27e/cg_ab_mix.wav` SHA `6e13e007…` — unchanged.
- WIG (c79): `data/v4/deliveries/252eb21ce7df7328/ab_mix.wav` SHA `6feca5d1fb41ee149e727b6ec2a61d2a006b4bc0b2a0aff62f2ef8946f47e3e9` — 11.249s honest-sparse-canonical-MIDI duration.
- Rome (c79): `data/v4/deliveries/51e433ade2a845e1/ab_mix.wav` SHA `81e2ef15…`.
- Peach Dream (c79): `data/v4/deliveries/88d247468cb6d49f/ab_mix.wav` SHA `a300cf4c…`.
- Disco A (c79): `data/v4/deliveries/cdd2717e52820ff6/ab_mix.wav` SHA `1b673106…`.

All five `LANDS_pending_operator` per FD-6. Post-hoc operator ear on the four c79 A/B mixes remains the LANDS-authority gate for M-V4-SHOWCASE-1 non-CG closure.

### WIG duration diagnosis: HONEST_SPARSE_CANONICAL_MIDI, no rerender

Under the operator's "verify only" mandate on the WIG 11.249s duration finding, Cycle 80 P1 diagnosed the cause honestly without rerendering:

- Canonical MIDI durations: bass 8.991s, drums 9.081s, vocals 29.960s, piano 29.921s. The bass and drums MIDIs are sparse (~9s of content) while vocals and piano are full-length (~30s).
- Truncation policy at `deliver_ab_v4.py:293` selects `min(bass_L, drums_L, vocals_L)` — the shortest instrumental stem sets the mix target length.
- SF2 release-tail approximately 2.168s adds a ceiling.
- Final duration: 8.991 + 2.168 = 11.249s. Honestly explained.

WAV bytes byte-identical pre-vs-post at SHA `6feca5d1…` — no rerender attempted per operator directive. Diagnostic block appended additively to the manifest with eight fields (`answer`, `canonical_midi`, `sf2_release_tail_s`, `mix_target_len_policy`, `rerender_required`, `operator_directive_ref`, `cross_check`, `authority`). Event `M-V4-SHOWCASE-1/wig-duration-diagnostic-honest` id `767ac7aa…`.

This is the correct FD-1 halt-honest response to an operator "verify only" mandate: the finding is a real property of the canonical MIDI content and the truncation policy, not a driver defect; the honest disclosure surfaces it in-manifest without either fabricating a longer mix or attempting to re-derive canonical content that agent action should not touch.

### Six rolling chains terminally retired via string-supersede

The Cycle 79 audit's P1 forward-guidance directed that the six chains carried per-cycle across earlier ranges be explicitly retired rather than continued, since the operator-authorized render break made several underlying blockers moot. Cycle 80 P2 executed the retirement cleanly, each row string-superseding its c68 predecessor with landing evidence citation (see the six-row table in Approach). All six carry the c14 string-`supersedes_path` lemma; each retirement narrative names the specific c47 omnibus clause or c69 render event that landed the underlying resolution.

The pattern is a discipline example worth naming: when the underlying blocker for a rolling chain-continue-supersede is resolved by fresh authority or by a new substantive landing, the correct next-cycle action is explicit retirement via string-supersede rather than continued chain-continuation. The retirement row closes the chain terminally, references the landing evidence, and stops the per-cycle carry cadence without violating any discipline invariant.

### M-V4-GEN-1 scaffold opened

Milestone-level opening with four sub-milestones registered plus one parent rollup at `in-progress` state:

- Primary generator: Anticipation.
- 5-donor map: pinned.
- Rubric pre-registered with stall-trigger clause: "8 iterations without 5 passers → deliver best 5 by ear score, honest gap analysis, PROCEED to close without operator input per FD standing rule L146-147." Rubric aligns with operator directive priority order.
- Interpolation-demo pre-registered.

Post-hoc operator ear per FD-6 remains authoritative on generated songs. Iteration 1 launches next cycle with stall counter reset 0/8 per brief §4 P3 + operator directive, gated on next-cycle disk prune to ≤82% per c27 policy (currently 85% at Cycle 80 close).

### Test debt fill-in on new driver

`tests/test_deliver_ab_v4.py` 6/6 PASS matching brief §4 P4 named cases covering env pin drift, min-truncation policy, Peach Dream invariant-(d) fallback, absent-stems manifest shape, manifest provenance field completeness, and replay proof of a second render into a fresh tempdir. Cross-cycle file-gate 8 pre-c70 + 1 new = 9/9 satisfied.

### Read-only anchors held; three inherited SHA drifts continue transitive disclosure

All 8 §1 READ-ONLY anchors byte-identical pre-vs-post at range close: `deliver_cg_ab_v4.py` `3c45465284e2f78a…` (c17); `deliver_ab_v4.py` `52ff05e28d2feb55…` (c69 new READ-ONLY); `objective.py` `8087ce809de9561b…`; Peach Dream stem manifest `d483f2bf0b09389b…` (invariant (d), 11th-cycle-stable since c65 Branch C canonical); four c79 A/B mix WAVs (WIG `6feca5d1…` + Rome `81e2ef15…` + PD `a300cf4c…` + Disco A `1b673106…`); `cg_ab_mix.wav` `6e13e007…` (c17). Three prior-range inherited invariant-(d) SHA-drift disclosures continue transitively (test file + `fine_fit_sf2_v2.py` + `agent_picks_selection_invariants.md`) per c62+ pattern.

### Audit outcome

**VALIDATED.** Zero CRITICAL, zero HIGH, zero MODERATE, zero MINOR. Two P2 findings, both non-blocking:

- **Event-count scope-extension.** Worker emitted 16 events versus brief §5 header 3 predicted 12. Overage attributable to (a) M-V4-GEN-1 parent-rollup registered at `in-progress` state alongside four sub-milestone registrations (+1); (b) `_plan/register-c70-…` emitted as its own row (+1); (c) full housekeeping tail preserved. Total: 6 retirements + 1 WIG diag + 4 gen subs + 1 gen parent + 1 register + 3 housekeeping = 16. Worker self-disclosed per FD-1 with rationale. Non-blocking because parent-rollup event is legitimate substantive artifact opening M-V4-GEN-1. Recommendation: next-cycle brief pre-approve parent-rollup events when a milestone first opens.
- **Pre-edit `ab_mix.manifest.json` SHA not captured.** Worker's "Anchors touched" section noted the manifest was mutated with the WIG duration-diagnostic block appended but did not capture the pre-edit SHA per c34 P0.2 anchor-substitution convention. Non-blocking because manifest is not a §1 READ-ONLY anchor, WAV bytes byte-identical (the substantive audio artifact), and diagnostic-block content is verifiable by direct inspection. Recommendation: next-cycle emitters capture pre-edit SHAs on all mutated files.

§5 nine-header closing-summary contract compliance at twelfth consecutive cycle under c62 reminder-dropped policy.

## Discussion

Three things about this range are worth naming.

First, the range demonstrates the correct discipline shape for exiting a long stable-blocked cadence under fresh operator authority. Prior ranges had extended chain-continue-supersede lineages across many consecutive cycles under Branch B semantics; the discipline held throughout because the underlying blockers (WIG piano operator authority, bass stage-2 disk pressure, Peach Dream stem manifest attribution) remained unresolved. When Cycle 79 landed the operator-authorized A/B mix renders, several underlying blockers resolved simultaneously: the c47 omnibus's absent-stems policy provided the semantic ground for rendering WIG without the piano stem; the four A/B mix renders provided the landing evidence that Rome / PD / Disco A bass stage-2 sweeps were no longer strictly needed for showcase-level delivery; the OP-2 Monitor N/A disposition became structurally moot when the new driver ran foreground. The Cycle 79 audit's P1 forward-guidance recognized this and directed Cycle 80 to explicitly retire the six chains rather than continue their chain-continue-supersede cadence. Cycle 80 executed the retirement cleanly with string-supersede referencing the c68 predecessor plus landing-evidence citation. This is the correct shape: chain-continue-supersede while blocked, explicit retirement when the blocker resolves, no chain-continuation past the point of resolution.

Second, the WIG duration diagnosis is a discipline example worth naming for how to respond to an operator "verify only" mandate on a finding that could tempt a worker into speculative rerendering. The finding — WIG A/B mix at 11.249s versus expected ~30s — has an obvious tempting response: assume the driver is producing incorrect output and rerender under a different mix policy. The operator "verify only" mandate explicitly forbids this. The correct halt-honest response is to trace the cause through the actual on-disk state: enumerate canonical MIDI durations per stem (bass 8.991s, drums 9.081s, vocals 29.960s, piano 29.921s); identify the truncation policy in the driver source (`deliver_ab_v4.py:293` `min(bass_L, drums_L, vocals_L)`); compute the resulting duration under the policy (bass 8.991s selects); add the SF2 release-tail ceiling (~2.168s); arrive at 11.249s honestly. The finding is a real property of the sparse canonical MIDI content and the min-truncation policy, not a driver defect. The `HONEST_SPARSE_CANONICAL_MIDI` classification names the property honestly; the manifest gets a diagnostic block; the WAV bytes stay byte-identical; no rerender. This is what FD-1 halt-honest looks like when applied to a "verify only" mandate: trace, diagnose, disclose, do not fabricate a fix.

Third, the M-V4-GEN-1 scaffold opening at Cycle 80 P3 with a stall-trigger clause pre-registered in the rubric is a discipline signal worth naming. The stall-trigger clause ("8 iterations without 5 passers → deliver best 5 by ear score, honest gap analysis, PROCEED to close without operator input per FD standing rule L146-147") pre-declares what will happen if the generator does not converge. This matters because M-V4-GEN-1 iteration is expected to consume many cycles and the temptation under a non-converging batch would be either to defer indefinitely or to escalate to operator authority. The pre-registered stall-trigger closes both paths off cleanly: after 8 iterations, deliver the best 5 by ear score, do the honest gap analysis, and PROCEED to close without operator input. This is the correct shape for opening a substantive milestone whose success is not guaranteed: pre-register the stall condition, pre-register the fallback deliverable, pre-authorize the closure path. When the worker executing iteration N faces the choice at N=8, the discipline invariant has already made the choice; the worker executes rather than deliberates.

## Open questions

- **Operator ear on the four c79 A/B mixes.** All four (WIG SHA `6feca5d1…`, Rome `81e2ef15…`, PD `a300cf4c…`, Disco A `1b673106…`) plus the CG c17 mix remain `LANDS_pending_operator` per FD-6. Post-hoc operator ear is the LANDS-authority gate for M-V4-SHOWCASE-1 non-CG closure. Do NOT emit wait-on-operator memos.
- **WIG duration finding operator flag.** If operator flags the 11.249s duration as unacceptable via `live_guidance`, next-cycle first-act would execute WIG re-render with corrected bass excerpt discovery (READ-ONLY search only per FD-1; no fabrication). If no operator flag, proceed directly to M-V4-GEN-1 iteration 1 detached launch.
- **Disk prune before M-V4-GEN-1 iteration 1.** MANDATORY per next-cycle brief. Prune workspace to ≤82% per c27 policy (currently 85% at Cycle 80 close). Next-cycle first-act includes prune step recorded in ledger.
- **M-V4-GEN-1 iteration 1 detached launch.** Gated on disk prune. Stall counter reset 0/8 per brief + operator standing order. Rubric with stall-trigger clause pre-registered at Cycle 80 P3.
- **M-V4-EAR-1 scaffold.** Queued for cycle after next per operator simplification 2026-09-03: lightweight exemplar ear (NOT trained regressor); CG + Molasses + Essence + Desire + Peach Dream exemplar set; CLAP + VGGish ensemble.
- **Parent-rollup event pre-approval.** Next-cycle brief should pre-approve M-V4-GEN-1 parent-rollup `in-progress` event to prevent §5 P2 scope-extension recurrence when opening milestones with sub-leaves.
- **Pre-edit SHA capture discipline.** Next-cycle emitters should capture pre-edit SHA on all mutated files (even non-anchor ones like manifests) per c34 P0.2 anchor-substitution convention.
- **Manifest annotation verification.** Next-cycle auditor should spot-check that the WIG duration-diagnostic manifest block carries all 8 fields specified in c70 brief §4 P1 (`answer`, `canonical_midi`, `sf2_release_tail_s`, `mix_target_len_policy`, `rerender_required`, `operator_directive_ref`, `cross_check`, `authority`).
- **Peach Dream stem manifest READ-ONLY status.** Divergence SHA `d483f2bf…`, non-standard `operator_section_c25_checkpointed/rc9_6stem/` path, 20th-cycle-stable since c19 opening. Retirement row at Cycle 80 removes the per-cycle carry but the on-disk anchor remains READ-ONLY (invariant (d) DO-NOT-TOUCH per FD-1). Next-cycle+ downstream code that reads it must continue to honor `_resolve_stems_root` fallback.
- **Amended completion report.** Per operator directive #5(f); queued for after operator ear result and M-V4-GEN-1 batch completion.

## Appendix: Provenance

**Directive.** Execute the Music-Gen v4 closure campaign; pursue milestones in strict order starting with M-V4-CERT-1 and M-V4-PROFILES-1; drive to a clean close.

**Cycle range.** cycles 78–80.

**Working directory.** `/home/user/long-exposure-runs/music-gen`.

**Session references.**

- Cycle 78 researcher `e8b89996-f6a5-4e01-a14d-1629f8932de2`; worker `27feaaa0-57ee-4d0e-9e8c-3b1f088fe57e`; auditor `e690537f-aa87-49a8-bd21-2fbfa3c7af78`.
- Cycle 79 researcher `408ca654-cc3d-4c07-b059-94a2a3147948`; worker `fb1adff5-328e-40bb-b5bf-fb350d5791b9`; auditor `a506c27b-c35f-46ef-9015-a013719b071d`.
- Cycle 80 researcher `f959602c-8436-4b59-9885-4366550833b0`; worker `a0d5ebaf-3883-40f8-b9b5-ba9f8585f667`; auditor `7b1c595e-fb4a-4181-a0bb-f603d923b288`.

**Audit verdict.** **VALIDATED.** Zero CRITICAL, zero HIGH, zero MODERATE, zero MINOR. Two P2 findings, both non-blocking: event-count scope-extension (16 emitted vs 12 predicted; legitimate parent-milestone opening); pre-edit manifest SHA not captured before diagnostic-block append.

**Terminal deliverables landed this range.**

- **Cycle 78 stable-blocked cadence tail:** WIG piano 6th-consecutive Branch B; Rome bass 5th-consecutive disk-blocked SKIP; PD + Disco A cascaded SKIPs; PD stem manifest 2nd-consecutive lightweight carry-forward; OP-2 Monitor Branch B N/A.
- **Cycle 79 operator-authorized A/B mix landing:** `scripts/sound_match/deliver_ab_v4.py` (SHA `52ff05e28d2feb55…`) as READ-ONLY driver with absent-stems policy per c47 omnibus; four A/B mix WAVs (WIG `6feca5d1…`; Rome `81e2ef15…`; PD `a300cf4c…`; Disco A `1b673106…`). M-V4-SHOWCASE-1 1 → 5 mixes.
- **Cycle 80 P1 WIG duration diagnostic:** `M-V4-SHOWCASE-1/wig-duration-diagnostic-honest` id `767ac7aa…`; classification `HONEST_SPARSE_CANONICAL_MIDI`; canonical MIDI durations (bass 8.991s + drums 9.081s + vocals 29.960s + piano 29.921s); truncation policy `min(bass_L, drums_L, vocals_L)`; SF2 release-tail ~2.168s; 8.991 + 2.168 = 11.249s. WAV bytes byte-identical pre-vs-post. Manifest additively updated with 8-field diagnostic block.
- **Cycle 80 P2 six explicit retirement rows** each with string `supersedes_path` per c14 lemma closing c68 rolling chains (Rome / PD / Disco A bass stage-2; WIG piano; PD stem manifest carry; OP-2 Monitor).
- **Cycle 80 P3 M-V4-GEN-1 scaffold:** four sub-milestones registered; parent rollup at `in-progress`; primary generator (Anticipation) picked; 5-donor map pinned; rubric with stall-trigger clause pre-registered; interpolation-demo pre-registered.
- **Cycle 80 P4 test debt fill-in:** `tests/test_deliver_ab_v4.py` 6/6 PASS. Cross-cycle file-gate 9/9.
- **Cycle 80 housekeeping tail:** `_plan/register-c70-sub-leaves` + `_run/cycle_70_closed` + `_archive/cycle-70-scratch` + `_infra/adopt-cycle70-tests`.
- **Ledger delta at Cycle 80:** 1879 → 1895 (16 events; 12 predicted; +4 attributable to parent-rollup + explicit register + housekeeping preservation).

**Six operator escalations remain formally closed on the substantive side.** No `_manager/*` events opened this range. `data/v4/_manager/` state untouched.

**Read-only anchors preserved byte-identical pre-vs-post (8/8 verified at Cycle 80 close).**

- `scripts/sound_match/deliver_cg_ab_v4.py` `3c45465284e2f78a…` (c17)
- `scripts/sound_match/deliver_ab_v4.py` `52ff05e28d2feb55…` (c69 new READ-ONLY)
- `scripts/sound_match/objective.py` `8087ce809de9561b…`
- Peach Dream stem manifest `d483f2bf0b09389b…` (invariant (d) DO-NOT-TOUCH; 11th-cycle-stable since c65 Branch C canonical)
- Four c79 A/B mix WAVs: WIG `6feca5d1…`; Rome `81e2ef15…`; Peach Dream `a300cf4c…`; Disco A `1b673106…`
- `data/v4/deliveries/31a164f845f8e27e/cg_ab_mix.wav` c17 SHA `6e13e007…`

**Inherited invariant-(d) SHA drifts (transitively disclosed).**

- `tests/test_sound_match_fine_fit_sf2_other.py` `ee0c8a10…` → `7ffd3389…` (c63 P2 Option A docstring-only edit).
- `agent_picks_selection_invariants.md` inherited transitive drift.
- `fine_fit_sf2_v2.py` inherited transitive drift.

**Test suite.** 6/6 PASS on `tests/test_deliver_ab_v4.py` (Cycle 80). Cross-cycle file-gate 9/9.

**Environment pin.** Canonical 7-key `env_pin_sha256=2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca` unchanged; FD-16(a) re-issue not triggered. FD-16(c) per-family per-song replay proofs N/A this cycle (no new render code path introduced; c79 driver replay proofs remain byte-determinism guarantee for the 4 landed A/B mixes).

**Discipline guards asserted.** Zero re-escalations of WIG piano stage-1 (Cycle 78 6th-consecutive Branch B; Cycle 80 explicit retirement per Cycle 79 audit guidance rather than re-escalation). Zero wait-on-operator memos (banned per operator directive 2026-09-03 point 2). Zero preservation-spin sub-leaves (21 consecutive clean cycles since c48; Cycle 80 substantive retirements rather than continued rolling carries). All six c47 omnibus-closed operator-authority memos remain CLOSED. c14 string-`supersedes_path` lemma honored on all six retirement rows and all M-V4-GEN-1 scaffold events. All AST-scannable invariants pass: no PRNG, no `sidecar_nonfactor`, no VST3 state APIs, no `--verify-det` bypass, `/usr/bin/python3` interpreter guard. No READ-ONLY anchor lift; no fabricated fallbacks; no destructive `rm`. FD-1 halt-honest throughout (WIG diagnostic; 16-vs-12 event count self-disclosed). FD-6 operator-ear-only-LANDS on non-CG respected (all 4 c79 A/B mixes remain `pending_operator`). §5 nine-header closing-summary contract compliance at 12th consecutive cycle under c62 reminder-dropped policy.

**Milestone status at range close.**

- M-V4-CERT-1 — validated (E2E_DETERMINISM_HOLDS on the v3 spine).
- M-V4-PROFILES-1 CG (5/5 instruments) — validated.
- M-V4-PROFILES-1 non-CG drums — 4/4 SF2_CONFIRMED (CLOSED earlier range).
- M-V4-PROFILES-1 non-CG vocals — SKIP auto-closed under FD-6 authority.
- M-V4-PROFILES-1 non-CG guitar family-1 — SKIP auto-closed across all four focus songs (earlier range); c70 P4 confirmation earlier.
- M-V4-PROFILES-1 non-CG guitar family-2 — queued per operator directive #5(c).
- M-V4-PROFILES-1 non-CG bass stage-2 (Rome / PD / Disco A) — c68 rolling-chain SKIPs terminally retired at Cycle 80 P2; substantive resolution via c47 omnibus absent-stems policy + c79 render landings.
- M-V4-PROFILES-1 non-CG piano — WIG piano stage-1 c68 rolling-chain terminally retired at Cycle 80 P2; substantive resolution via c47 omnibus absent-stems policy + c79 WIG render.
- M-V4-PROFILES-1 non-CG other — driver + policy landed earlier; stage-1 launch queued.
- **M-V4-SHOWCASE-1** — 5 A/B mixes landed (CG c17 + 4 c79); all `LANDS_pending_operator` per FD-6.
- M-V4-RULES-1 — scaffold landed c20; substantive implementation queued.
- **M-V4-GEN-1** — scaffold OPENED at Cycle 80 P3; iteration 1 launches next cycle with stall counter 0/8; primary generator (Anticipation) picked; 5-donor map pinned; rubric with stall-trigger clause pre-registered; interpolation-demo pre-registered.
- M-V4-EAR-1 — scaffold queued for cycle after next per operator simplification 2026-09-03 (lightweight exemplar ear; CG + Molasses + Essence + Desire + PD exemplar set; CLAP + VGGish ensemble).
- M-V4-CLOSE-1 — c24 amendment landed; completion report v3 queued per operator directive #5(f) awaiting operator ear result and M-V4-GEN-1 batch completion.

**Next-cycle first tasks (per Cycle 80 auditor forward guidance).**

1. **P1**: either (a) if operator flags WIG 11.249s unacceptable via `live_guidance`, execute WIG re-render with corrected bass excerpt discovery (READ-ONLY search only per FD-1; no fabrication); or (b) if no operator flag, proceed directly to M-V4-GEN-1 iteration 1 detached launch with stall counter reset 0/8.
2. **P1**: MANDATORY disk hygiene before M-V4-GEN-1 iteration 1 — prune workspace to ≤82% per c27 policy (currently 85% at Cycle 80 close). First-act includes prune step recorded in ledger.
3. **P2**: pre-approve M-V4-GEN-1 parent-rollup `in-progress` event in next brief to prevent scope-extension recurrence.
4. **P2**: next-cycle emitters capture pre-edit SHA on all mutated files (even non-anchor ones) per c34 P0.2 convention.
5. **P2**: next-cycle auditor spot-check that WIG duration-diagnostic manifest block carries all 8 specified fields.
6. **P3**: M-V4-EAR-1 scaffold not opened this cycle; scoped for cycle after next per operator simplification 2026-09-03.
7. **P3**: post-hoc operator ear (FD-6) on 4 c79 A/B mixes remains LANDS-authority gate; amended completion report awaits that ear result. Do NOT emit wait-on-operator memos.
8. **P3**: Peach Dream stem_manifest divergence (SHA `d483f2bf…`, non-standard path) — retirement row lands this cycle removing per-cycle carry but on-disk anchor remains READ-ONLY (invariant (d) DO-NOT-TOUCH per FD-1); next-cycle+ downstream code must continue to honor `_resolve_stems_root` fallback.

Operator ear remains LANDS authority post-hoc per FD-6.
