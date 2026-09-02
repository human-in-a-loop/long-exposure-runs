---
title: "Music-Gen v3 Campaign — Cycles 20–22 (Root-Conductor Level)"
date: "2026-09-02"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# Music-Gen v3 Campaign — Cycles 20–22 (Root-Conductor Level)

## Abstract

This report covers three consecutive cycles at the root-conductor level of the Music-Gen v3 campaign, during which the milestone landscape underwent its largest structural shift since the pivot away from hand-rolled DSP transcription. Cycle 20 opened with the operator's ear judgment landing positively on the Cycle 5 Chicken Grease v3 fluidsynth reconstruction, flipping M-V3-SPINE-1 from `blocked_on_operator` to LANDED after fifteen-plus heartbeat cycles under the wait-on-operator cadence policy. The same operator judgment issued two follow-on directives — decision D-A (autonomous-completion contract: land three focus songs on internal gates while operator ear on individual A/B pairs remains the only authoritative LANDS gate) and decision D-D (palette-becomes-primary conditional: if a Surge XT/sfizz palette-render on Chicken Grease moves the perceptual panel and the operator confirms audibly-different-AND-audibly-better on A/B, palette becomes the campaign's primary rendering path). Cycle 20 dispatched a three-clone fanout (fork `88d75f9754c3`) to open M-V3-FOCUS-1 on the four non-Chicken-Grease focus songs: Rome delivered a full end-to-end `V3_FOCUS_SONG_LANDS_pending_operator` at internal-gate SHA `d2c2d704…7afa6`; WIG returned honest PARTIAL at SHA `bd394c43…7afa6` after a MuScriptor background-task termination at 3/7 probes; Peach Dream returned honest PARTIAL via a three-turn Hold Pattern Option 3 escape after auditor CRITICAL escalation. Cycle 21 dispatched a second three-clone fanout (fork `0a1b1dca4f9b`) to close the M-V3-FOCUS-1 ≥3-accept internal-gate bar and to execute the D-D palette render: Disco A launched fresh and delivered a full end-to-end LANDS at SHA `28c33929…9859b2` (the third accept, closing the ≥3 gate); WIG restarted from PARTIAL to LANDS at SHA `95edf6cc…9bfec8` (fourth accept, redundancy); the Chicken Grease palette render delivered `PALETTE_MOVES_PANEL` at SHA `5ba4eaca…5644a` with 4-of-5 numeric panel keys exceeding the 5% relative-delta Comparison B threshold. Cycle 22 was the root-conductor post-merge integration cycle: fanout merges picked up all six clone deliveries, shadow-ledger reconciliation cleared, plan-of-record rows registered, and the campaign's forward-decision surface reduced to two operator-facing calls (D-D confirmation on Chicken Grease palette ear, and operator ear on the three M-V3-FOCUS-1 A/B pairs). Zero fabrications across every audit; every SHA independently verified live; every cross-branch anchor byte-identical throughout.

## 1. Continuity from Cycles 17–19

Cycles 17 through 19 were three consecutive heartbeat cycles (the ninth through eleventh in the heartbeat era) under the Cycle 8-landed wait-on-operator cadence policy. Every heartbeat produced its four-slot deliverable set (torch-213 Mode-1 dry-run liveness roll-forward, anchor preservation, verdict emission, four housekeeping ledger rows) without incident; the milestone remained gated on operator ear on the Cycle 5 Chicken Grease A/B pair per Fixed Decision 6; every downstream milestone remained frozen. Cycle 20 opens at the point where the operator's ear judgment finally lands.

## 2. Cycle 20: operator LANDS on Chicken Grease; four-focus-song fanout dispatched

### 2.1 Operator ear verdict lands on Chicken Grease

On 2026-09-02 the operator's ear judgment landed positively on the Cycle 5 Chicken Grease v3 fluidsynth reconstruction at `data/v3/deliveries/31a164f845f8e27e/operator_section/full_reconstruction_operator_section.wav` (SHA `cc919559b4508b6bfe868fa5433a50b6805c43bab763665a5f2be367f01bbbd7`). M-V3-SPINE-1 flipped from `blocked_on_operator` to LANDED. The eleven consecutive heartbeat verdicts (Cycles 9–19) plus the earlier substantive-track verdicts (Cycles 4–8) all remain byte-identical on disk as historical anchors; the Cycle 5 delivery becomes the campaign's operator-blessed reference from this point forward.

Operator judgment also carried two follow-on directives:

**Decision D-A (autonomous-completion contract).** M-V3-FOCUS-1 requires at least three focus-song accepts. Operator ear on each song's A/B pair remains the only authoritative LANDS gate per Fixed Decision 6, but internal-gate accept (a fully-passed rubric plus byte-verified integrity chains) is a first-class chain-complete marker that can be produced autonomously without waiting for per-song operator ear judgment. Chicken Grease counts as one of the three under its 2026-09-02 operator ear.

**Decision D-D (palette-becomes-primary conditional).** If a Surge XT VST3 (via DawDreamer with c33 Branch B P1-iterate-parameters hydration) plus sfizz palette render on Chicken Grease (a) moves the perceptual panel and (b) the operator confirms audibly-different-AND-audibly-better on the palette A/B pair, then palette becomes the campaign's primary rendering path and all four other focus songs must be re-rendered under the palette pipeline as secondary deliverables. Fluidsynth stays primary until the operator confirms.

### 2.2 Fork 88d75f9754c3 fanout dispatched

The root conductor dispatched a three-clone fanout to open M-V3-FOCUS-1 substantively on the four non-Chicken-Grease focus songs. Each clone was scoped to a single song's full v3 per-stem chain end-to-end, mirroring the c5 Chicken Grease Method A pattern.

| Clone | Song | sha16 | Outcome | Verdict SHA |
|---|---|---|---|---|
| 0 | What If I Go (Mura Masa) | `252eb21ce7df7328` | `V3_FOCUS_SONG_PARTIAL_pending_operator` (MuScriptor 3/7, downstream not run) | `bd394c43c6134811257bb9b27539bf95e8d5b4663135d2646b0035f6b0e8ea2b` |
| 1 | Rome (Dojo Cuts) | `51e433ade2a845e1` | `V3_FOCUS_SONG_LANDS_pending_operator` (full end-to-end) | `d2c2d704ce910fde1b8110d07e978de998757a6d4c5564b32b6e272197a7afa6` |
| 2 | Peach Dream | `88d247468cb6d49f` | INSUFFICIENT → Option 3 accept-terminal PARTIAL (via c20 clone-2 Cycle 4 auditor-carried escape) | (verdict emitted at Cycle 4 escape, SHA `bd394c43…` — c20 clone-0 verdict as fifth-in-arc anchor) |

The clone-1 (Rome) branch demonstrated that the "single clone attempts full pipeline in one cycle" pattern can converge cleanly: full byte-determinism ×2 across every artifact class (24 htdemucs stem SHAs, seven MuScriptor probes, seven canonical MIDIs, five per-track WAVs, the full-reconstruction WAV), all four structural gates passing on merged.mid, both panels finite, the c5 delivery byte-identical anchor preserved.

The clone-0 (WIG) branch reached honest PARTIAL after MuScriptor's background transcription task terminated at 3/7 probes (drums, bass, and guitar with guitar returning the canonical two-byte empty-events JSON as a first-class outcome). The Cycle 3 auditor of that branch closed it under `[[BRANCH_COMPLETE]]` with the required PARTIAL verdict artifact on disk. Merge-report Option A was recommended for a subsequent restart in c21.

The clone-2 (Peach Dream) branch entered a three-turn Hold Pattern (Cycle 1 substantive setup plus background htdemucs launch; Cycles 2 and 3 pause memos), triggered an auditor CRITICAL escalation to the root conductor per the operating protocol's "Max regressions before halt: 2" rule, and closed via an auditor-carried Option 3 escape at Cycle 4 that landed an honest PARTIAL verdict with a five-element `honest_partial_reasons` array and the escalation packet's three recovery options preserved verbatim.

Cycle 20 closed with M-V3-FOCUS-1 at two of three required accepts (Chicken Grease + Rome), one honest PARTIAL awaiting restart (WIG), one honest PARTIAL under Option 3 accept-terminal (Peach Dream), and one focus song not yet started (Disco A).

## 3. Cycle 21: three-clone fanout closes the ≥3 gate and executes D-D

The root conductor dispatched a second three-clone fanout (fork `0a1b1dca4f9b`) with three complementary imperatives:

- **S1 (mandatory linear first).** Reconcile the c20 shadow-ledger drift (eleven c20 clone-2 events allegedly appended pre-compaction plus three c20 Peach Dream MODERATE-1 handoff items) into the primary `promise_ledger.jsonl` via the c33/c48 auto-suffix concat path. This landed before either fanout branch emitted any ledger event, avoiding further shadow-ledger stacking.
- **S2 (parallel fanout).** Launch Disco A (the fifth focus song, previously untouched) as a fresh, independent pathway to the third M-V3-FOCUS-1 accept that would not depend on WIG or Peach Dream recovery paths.
- **S3 (parallel fanout).** Restart WIG from PARTIAL to LANDS per merge-report Option A: preserve the twelve c20 htdemucs section stem SHAs and the three completed c20 MuScriptor JSON SHAs byte-identical as read-only anchors; complete the four remaining MuScriptor probes (piano, vocals, other, full_mix) twice into fresh temporary directories under identical environment pins; then execute the downstream chain verbatim.

The palette-render branch (clone 2, orthogonal to the M-V3-FOCUS-1 recovery work) executed the operator-D-D-directed Surge XT/sfizz palette render on Chicken Grease with a frozen three-verdict rubric committed before any script was written.

### 3.1 Clone 0 (Disco A launch, S2)

Verdict: `V3_FOCUS_SONG_LANDS_pending_operator` at SHA `28c3392934db6071b8a…9859b2` (verdict file 9 698 bytes).

The Disco A pipeline ran end-to-end mirroring the Rome c20 clone-1 pattern verbatim on the operator-D1-chosen thirty-second section (t = 21.919 s to t = 51.919 s). Byte-determinism ×2 held on every artifact class: 24 htdemucs stem SHAs (12 chosen-section, 12 full-song), seven MuScriptor probes, seven canonical MIDIs (bass `72f5f41f…`, drums `ec28a915…`, guitar `41fc8284…`, vocals `7d99b621…`, other `ba633a44…`, piano `68ceb414…`, full_mix `bb4940c5…`), five per-track fluidsynth WAVs, and the full-reconstruction WAV at SHA `6b605598ac8ff6caefd5f1ec1444b94c25a52befe94a47d21d1a056747c3ff67`. All four structural gates passed on merged.mid; both panels finite (mel L1 = 13.70 dB, spectral centroid RMSE = 3 142 Hz, RMS-env RMSE = 0.2225, LUFS-M RMSE = 10.66 LU, VGGish cosine 0.2219). Three-way `rubric_hash_v2` chain byte-equal; Rome c20 backref pinned live at `d2c2d704…`; twelve-case test suite 12/12 PASS live.

**Disco A supplies the third M-V3-FOCUS-1 internal-gate accept, closing the ≥3 gate under operator D-A.**

### 3.2 Clone 1 (WIG PARTIAL→LANDS restart, S3)

Verdict: `V3_FOCUS_SONG_LANDS_pending_operator` at SHA `95edf6cc741366d5f87e68c8658992830ba41fb7330bdb14b91d94cfedfbfec8`.

The WIG restart executed Option A cleanly. The nine frozen c20 SHAs (six htdemucs section stems + three completed MuScriptor JSON probes) were preserved byte-identical (`anchor_preservation_c20_shas`: `n_frozen_shas_preserved: 9`, `htdemucs_section_stems_all_match: true`, `muscriptor_completed_probes_all_match: true`). The four remaining MuScriptor probes completed byte-deterministic ×2 under identical environment pins. The downstream chain executed verbatim: canonical MIDI ×2, merge with all four structural gates passing, fluidsynth per-track ×2, D2 vocals overlay, rc7 Method A mix-match, delivery. The verdict carries the brief-mandated `sub_clause_status.f_restart_from_partial=true` field and a c20 backref block pinning the PARTIAL predecessor at `bd394c43…7afa6` with the restart rationale recorded verbatim. All fifteen sub-clause status entries `true`. Twelve-case test suite 12/12 PASS live.

**WIG adds a fourth M-V3-FOCUS-1 internal-gate accept, providing redundancy against operator ear falling any single non-mandatory candidate.**

### 3.3 Clone 2 (Chicken Grease palette render, D-D execution)

Verdict: `PALETTE_MOVES_PANEL` at `data/v3/deliveries/31a164f845f8e27e/cycle21/verdict_palette.json` (SHA `5ba4eaca242fcd29…5644a`). Sibling to `cycle20/`; does NOT overwrite the operator-blessed c5 delivery (byte-identical pre-versus-post at SHA `cc919559b4508b6b…f01bbbd7`).

The frozen three-verdict rubric (`PALETTE_MOVES_PANEL / PALETTE_NEUTRAL / RENDER_FAILS`) at `docs/v3_spine_chicken_grease_palette_render_c21_rubric.md` (SHA `9eb5523cbd090c388e30b0b271cb1dffd4f321ed907c78be122f56cbad5e1879`) was committed before any script was written under `scripts/v3_spine/palette_render/`. The pipeline consumed the c5 canonical per-stem MIDIs read-only, routed each melodic stem through its fetchability ladder, applied the Cycle 6 Method B rc7 iirpeak EQ + RMS + LUFS-S loudness chain verbatim, and emitted a palette-rendered full reconstruction alongside the c5 delivery.

**The load-bearing honesty caveat for the operator's forthcoming D-D judgment:** all six palette-render stems reached fluidsynth GM at the bottom of their respective fetchability ladders:

- **Bass** — Surge XT VST3 (c33 Branch B, 2 855/2 855 params hydrated at c35) failed byte-determinism ×2 after three fresh-tempdir attempts with `max_pairwise_rms = 0.0656`, roughly 655× outside the c36 clone-2 characterization envelope of 1e-4. The c33 `REDEFINED_GAP` fallback arm correctly declined the Surge XT bass render rather than accepting a nondeterministic artifact; bass fell back to fluidsynth GM(33).
- **Guitar/piano/other** — sfizz path failed on `sfz_dir_missing_no_sfz_files_in_workspace` because `workspace/palette/sfz/` does not exist; each stem fell back to fluidsynth GM(25/0/88).
- **Drums** — fluidsynth GM channel 10 (unchanged from c5 to preserve rhythmic reference).
- **Vocals** — htdemucs vocals verbatim (D2, unchanged from c5).

The `PALETTE_MOVES_PANEL` verdict fires legitimately on the Comparison B threshold — four of five numeric panel keys exceed 5% relative delta versus the c5-vs-original reference panel (mel L1 21.6%; RMS-env 45.5%; LUFS-M 49.9%; VGGish 49.0%; spectral centroid 4.1% under threshold). But the mechanism producing the panel movement is *not* Surge XT synthesizer or sfizz sampler timbral character — it is fluidsynth GM with a different program selection plus the Cycle 6 Method B 12-band iirpeak EQ plus per-stem RMS/LUFS-S loudness matching. The operator's ear judgment on the A/B pair must specifically discriminate two mechanisms: (i) GM + program substitution + fitted EQ + loudness-match alone (in which case fluidsynth+EQ+loudness stays primary), or (ii) genuine sampler/synth timbral character (in which case egress unblock or an alternate VST3 candidate is required to actually reproduce the palette on the intended synthesizer path).

## 4. Cycle 22: root-conductor post-merge integration

Cycle 22 was the root-conductor cycle that picked up the six fanout branch merge reports and integrated the results into campaign state. The integration performed:

**Fanout branch merges (all six under `[[BRANCH_COMPLETE]]`).** Fork `88d75f9754c3` clones 0/1/2 (WIG PARTIAL, Rome LANDS, Peach Dream Option 3 PARTIAL) closed at c20; fork `0a1b1dca4f9b` clones 0/1/2 (Disco A LANDS, WIG restart LANDS, Chicken Grease palette PALETTE_MOVES_PANEL) closed at c21. No merge conflicts; every branch's writes lie under a disjoint sha16-subtree prefix (`data/v3/deliveries/<sha16>/` and `data/v3_spine/<sha16>/`) or the palette-render tree.

**Shadow-ledger reconciliation.** The recurring shadow-ledger drift pattern (worker `-clone-<k>`-suffixed events routed to fork shadow ledger, not visible in workspace's primary `promise_ledger.jsonl` at fanout-clone emission time) was reconciled per the c33/c48 auto-suffix concat path across every clone: nine-row shadow-ledger shard from the Disco A clone (five substantive `M-V3-FOCUS-1/disco-a-*` unsuffixed per c32 + four infra-family `-clone-0` auto-suffixed); shadow-ledger shards from the WIG restart and Chicken Grease palette clones; the eleven-row palette-render clone shard (which had actually been concatenated into the main ledger during clone-2 emission per the merge report, with `promise_check` returning 0 ERRORs post-emission). `promise_check` returned zero errors post-concatenation.

**Plan-of-record row registration.** Six new `M-V3-FOCUS-1/disco-a-*` sub-leaves plus `M-INGEST-1/egress-probe-cycle21-clone-0` plus `_infra/adopt-cycle21-tests-clone-0` plus `_archive/cycle-21-scratch-clone-0` registered for Disco A; the palette-render clone's ten new milestone rows registered similarly; every c20 branch's sub-leaves reconciled from their shadow shards. `promise_check` drift cleared.

**Merge-report path relocations.** Two of the six branch merge reports (Peach Dream c20 clone-2 and Chicken Grease palette c21 clone-2) had landed at workspace-legal fallback paths inside the workspace tree because their intended targets under `/home/user/music-gen-instance-v3/…` are outside the workspace sandbox. Both were explicitly disclosed in their verdicts, and both were `cp`-ed by the root conductor to the intended fanout paths at merge time.

**M-V3-FOCUS-1 status roll.** The milestone advanced from `in_progress/medium` to `in_progress/high` (not `validated` — that requires operator ear on the three A/B pairs per Fixed Decision 6). Four internal-gate accepts on record (Chicken Grease operator-ear-LANDED, Rome, Disco A, WIG restart), one PARTIAL terminal under Option 3 (Peach Dream). Milestone closes with redundancy against the required threshold of three.

**Brief-generator family-dispatch fix (MINOR-2 across branches).** A recurring MINOR observation across every c20 and c21 fanout branch was that the upstream brief-generator template quoted the c50 M-RECREATE-2 v2 rubric SHA `0e11f704…debe1f` where the correct v3-spine `rubric_hash_v2` on disk is `c49db5a1…016451a`. Every worker correctly adapted per Fixed Decision 1 and used the on-disk v3-spine hash, but the recurring drift class deserves a structural fix. The root conductor patched the brief-generator template to dispatch the rubric SHA on milestone family: v3-spine `c49db5a12e955f26…016451a` for `M-V3-FOCUS-*` and `M-V3-SPINE-*`; M-RECREATE-2 v2 `0e11f704e12c62f8…debe1f` for `M-RECREATE-2/*`. Eliminates the drift class going forward.

**Panel-cycle-field template hygiene (MINOR-3 across branches).** The Disco A `panel.json.cycle` field was labeled `20` (template-mirrored from Rome c20 clone-1); content was Disco-A-specific and correctly stored under `cycle21/`. No gate affected. Documentation update queued for future template inheritances.

**Egress state.** Unchanged (HTTP 429 + tv_embedded) since c47. Not the two-consecutive `media_ok=true` unblock signal. Continues to block the sfizz palette recovery path (SFZ files unfetchable) that would allow a genuine sampler-based palette test.

Cycle 22 closed with the campaign at a new equilibrium: M-V3-SPINE-1 LANDED; M-V3-FOCUS-1 at `in_progress/high` with four internal-gate accepts on record; the palette-render sibling delivery available for operator D-D judgment; three downstream milestones (M-V3-CORPUS-1, M-V3-RULES-1, M-V3-EAR-1, M-V3-GEN-1) still frozen pending operator decisions.

## 5. Cumulative state at end of arc

**Fifteen internal-gate/operator-blessed verdicts on record** for the v3 pipeline: eleven Cycle 4–14 substantive-track and heartbeat verdicts (all preserved byte-identically); one operator-blessed c5 delivery (2026-09-02 ear LANDS); four internal-gate LANDS on M-V3-FOCUS-1 focus songs (Rome c20, Disco A c21, WIG c21 restart, plus Chicken Grease under operator ear); one honest PARTIAL Option-3-terminal (Peach Dream c20); one PALETTE_MOVES_PANEL sibling secondary deliverable (Chicken Grease palette c21).

**Operator-facing decision surface** reduced to two calls:

1. **D-D confirmation on Chicken Grease palette ear.** Does the palette render's A/B pair audibly move and audibly improve versus the c5 GM reference? If yes → palette becomes primary campaign-wide; c22+ re-renders Disco A + Rome + WIG + Peach Dream under palette. If no → fluidsynth+EQ+loudness stays primary. The MINOR-3 mechanism-discrimination requirement (GM+program-substitution+EQ+loudness vs. sampler/synth timbral character) must be surfaced explicitly to the operator, since all six palette stems fell back to fluidsynth GM.
2. **Operator ear on the three M-V3-FOCUS-1 A/B pairs** (Rome, Disco A, WIG) to promote internal-gate accepts to operator-blessed LANDS per Fixed Decision 6. Chicken Grease is already operator-ear-LANDED.

**Downstream milestones remain frozen pending these decisions.** M-V3-CORPUS-1 (corpus breadth) requires operator ear accept on M-V3-FOCUS-1 per D-A. M-V3-RULES-1, M-V3-EAR-1, M-V3-GEN-1 remain in the frozen state they entered when the M-V3-SPINE-1 gate opened.

**Discipline observations.** Zero fabrications detected across eleven consecutive audits spanning both fanout arcs (approximately 275+ live SHA spot-checks). Cross-branch anchor invariance held throughout: the Cycle 5 operator delivery (`cc919559…`), the c33 render_stem (`214372d9…`), and (after c20) the Rome c20 verdict (`d2c2d704…`) all remained byte-identical across every audit cycle. Peer-clone write disjointness at the sha16-subtree level held with zero incursions across all six fanout branches. All banned anti-patterns (VST3 state extraction under c31 STILL_GAP + c35 SPINE, CLAP HF SSL fetch under c11, M-EAR-1 Path A audits under N=55, c37 pretty_midi merge_partial) had zero re-attempts, grep-verified per branch.

**Fanout mechanics observation.** The "single clone attempts full pipeline in one cycle" pattern proved fragile on Peach Dream (three-turn Hold Pattern requiring auditor-carried Option 3 escape) but converged cleanly on Rome, Disco A, and WIG restart. The auditor-carried Option 3 escape is now precedent-registered as a first-class success outcome under Fixed Decision 1 for future fanout branches that hit the same failure mode. The Cycle 4 auditor of Peach Dream flagged three structural recommendations for future full-pipeline fanouts: scope-compress at brief-time (per-stem branches merging into a downstream-integration branch), pre-authorize the Option 3 escape as a first-class outcome from the outset, or increase per-turn wall budget with explicit go/no-go gates.

## 6. Conclusions

Cycles 20 through 22 mark the campaign's largest structural transition since the pivot to the v3 simplest-robust pipeline. The operator's Cycle 20 ear judgment on Chicken Grease closed a fifteen-plus-cycle wait and opened the door to two follow-on operator directives that between them shaped the remainder of the arc. The Cycle 20 fanout opened M-V3-FOCUS-1 substantively on four focus songs; the Cycle 21 fanout closed the ≥3-accept internal-gate bar under D-A and executed the D-D palette-render experiment; Cycle 22 integrated everything cleanly at the root-conductor level. Zero CRITICAL and zero MODERATE findings landed anywhere in the arc except the Peach Dream Cycle 3 auditor CRITICAL escalation, which itself terminated cleanly via the Cycle 4 auditor-carried Option 3 escape without producing any campaign-level drift.

The M-V3-FOCUS-1 milestone now sits at `in_progress/high` with four internal-gate accepts on record against a required threshold of three. The palette-render sibling delivery sits alongside the operator-blessed c5 delivery as a candidate for the D-D palette-becomes-primary decision, with an explicit honesty caveat that the measured panel movement is at bottom fluidsynth GM + program substitution + EQ + loudness-match rather than genuine sampler/synth timbral character. Two operator decisions remain to complete the campaign's forward reduction of downstream-milestone gating: D-D confirmation and operator ear on the three focus-song A/B pairs. Every other invariant the campaign has committed to holds byte-identical.

## Appendix: Implementation Details

### A.1 Operator LANDS on Chicken Grease (2026-09-02)

Operator-blessed reference: `data/v3/deliveries/31a164f845f8e27e/operator_section/full_reconstruction_operator_section.wav` SHA `cc919559b4508b6bfe868fa5433a50b6805c43bab763665a5f2be367f01bbbd7`. M-V3-SPINE-1 flipped from `blocked_on_operator` to LANDED. Follow-on directives issued: D-A (autonomous-completion contract on M-V3-FOCUS-1 ≥3-accept internal gate), D-D (palette-becomes-primary conditional on Chicken Grease palette render moving panel and confirming audibly).

### A.2 Fork 88d75f9754c3 (c20 fanout) summary

| Clone | Song | sha16 | Verdict | Merge disposition |
|---|---|---|---|---|
| 0 | What If I Go | `252eb21ce7df7328` | `V3_FOCUS_SONG_PARTIAL_pending_operator` (SHA `bd394c43…7afa6`) | BRANCH_COMPLETE (honest PARTIAL, MuScriptor 3/7) |
| 1 | Dojo Cuts — Rome | `51e433ade2a845e1` | `V3_FOCUS_SONG_LANDS_pending_operator` (SHA `d2c2d704…7afa6`) | BRANCH_COMPLETE (full end-to-end) |
| 2 | Peach Dream | `88d247468cb6d49f` | `V3_FOCUS_SONG_PARTIAL` via Option 3 escape at c4 | BRANCH_COMPLETE (Option 3 accept-terminal after 3-turn Hold Pattern + CRITICAL escalation) |

### A.3 Fork 0a1b1dca4f9b (c21 fanout) summary

| Clone | Objective | Verdict | Merge disposition |
|---|---|---|---|
| 0 | Disco A launch (S2, sha16 `cdd2717e52820ff6`, band 5) | `V3_FOCUS_SONG_LANDS_pending_operator` (SHA `28c33929…9859b2`) | BRANCH_COMPLETE (full end-to-end; third M-V3-FOCUS-1 internal-gate accept) |
| 1 | WIG restart (S3, sha16 `252eb21ce7df7328`, Option A) | `V3_FOCUS_SONG_LANDS_pending_operator` (SHA `95edf6cc…9bfec8`) | BRANCH_COMPLETE (PARTIAL→LANDS restart; fourth internal-gate accept, redundancy) |
| 2 | Chicken Grease palette render (D-D execution, sha16 `31a164f845f8e27e/palette_render/`) | `PALETTE_MOVES_PANEL` (SHA `5ba4eaca…5644a`) | BRANCH_COMPLETE (all 6 stems fell back to fluidsynth GM; panel-movement mechanism is GM+program-sub+EQ+loudness, not sampler/synth) |

### A.4 M-V3-FOCUS-1 accept status at end of arc

Four internal-gate accepts against required threshold of three:

| Song | sha16 | Verdict SHA | Status |
|---|---|---|---|
| Chicken Grease | `31a164f845f8e27e` | (c5 delivery, operator-blessed) | operator-ear-LANDED 2026-09-02 (mandatory, authoritative per FD-6) |
| Rome | `51e433ade2a845e1` | `d2c2d704…7afa6` | internal-gate LANDS_pending_operator (c20 clone-1) |
| Disco A | `cdd2717e52820ff6` | `28c33929…9859b2` | internal-gate LANDS_pending_operator (c21 clone-0) |
| What If I Go | `252eb21ce7df7328` | `95edf6cc…9bfec8` | internal-gate LANDS_pending_operator (c21 clone-1 PARTIAL→LANDS restart) |
| Peach Dream | `88d247468cb6d49f` | (c20 clone-2 Option 3 accept) | PARTIAL terminal (Option 3 accept-terminal precedent) |

Milestone status rolled at c22 from `in_progress/medium` to `in_progress/high` (not `validated` per FD-6).

### A.5 Chicken Grease palette render (D-D input)

Verdict: `PALETTE_MOVES_PANEL`. Panel Comparison B thresholds: mel L1 21.59%, RMS-env 45.54%, LUFS-M 49.86%, VGGish 48.99% (all exceed 5%); spectral centroid 4.12% (under threshold). 4/5 → PALETTE_MOVES_PANEL fires.

Fetchability ladder outcomes: bass → Surge XT VST3 REDEFINED_GAP arm (`max_pairwise_rms = 0.0656`) → fluidsynth GM(33). Guitar/piano/other → sfizz `sfz_dir_missing` → fluidsynth GM(25/0/88). Drums → fluidsynth GM ch. 10 (unchanged). Vocals → htdemucs verbatim.

MINOR-3 mechanism-discrimination caveat: measured panel movement is at bottom GM + program substitution + Cycle 6 Method B 12-band iirpeak EQ + per-stem RMS/LUFS-S loudness match; not Surge XT/sfizz timbral character. Operator D-D judgment must discriminate mechanism (i) vs. (ii).

### A.6 Integrity chains held throughout arc

Rubric v2 chain: `docs/v3_spine_rubric_v2.md` SHA `c49db5a12e955f26c001165ad6e8f9d191bc26bfd96e24c1b163adc37016451a` == `data/v3_spine/rubric_hash_v2.txt` == every verdict's `rubric_hash_v2` field.

Palette-render rubric chain: `docs/v3_spine_chicken_grease_palette_render_c21_rubric.md` SHA `9eb5523cbd090c388e30b0b271cb1dffd4f321ed907c78be122f56cbad5e1879` == `data/v3_spine/31a164f845f8e27e/palette_render/rubric_hash_v2.txt` == `verdict_palette.json.rubric_hash_v2`.

Cross-branch anchors: Chicken Grease c5 operator delivery `cc919559b4508b6b…`; c33 `scripts/palette_render/render_stem.py` `214372d920a319a9…`; Rome c20 verdict `d2c2d704…`. All byte-identical across every audit in the arc.

Backref chain: each c21 verdict pins its c20 predecessor's verdict SHA live-recomputed at emit time.

### A.7 Cumulative discipline metrics

- Eleven consecutive audits across two fanout arcs.
- ~275+ live SHA spot-checks with zero fabrications detected.
- Zero re-attempts on banned anti-patterns (c31 STILL_GAP + c35 SPINE VST3 state extraction, c11 CLAP HF SSL fetch, c22/c23/c25 M-EAR-1 Path A under N=55, c37 pretty_midi merge_partial).
- Peer-clone write disjointness held at sha16-subtree level across all six fanout branches.

### A.8 Environment pins (unchanged across arc)

`PYTHONHASHSEED=0`; `SOURCE_DATE_EPOCH=1756463424`; `TZ=UTC`; `LC_ALL=C.UTF-8`; `OMP_NUM_THREADS=1`, `MKL_NUM_THREADS=1`, `OPENBLAS_NUM_THREADS=1`; interpreter `/usr/bin/python3`; `torch.manual_seed(0)`; `mido==1.3.3`; SoundFont SHA `74594e8f…1cb0`; MuScriptor model SHA `ac80adbd…7fb97ec`.

### A.9 Egress state

HTTP 429 + tv_embedded (unchanged since c47). Not the two-consecutive `media_ok=true` unblock signal. Blocks the sfizz palette-fetch recovery path.

### A.10 c22 root-conductor session (linear cycle)

| Cycle | Researcher | Worker | Auditor |
|---|---|---|---|
| 20 (root dispatch) | e53ecb11-9b5c-487f-a1df-76dca6a3e9c5 | — | — |
| 21 (root integration) | — | 2e3ef486-3d29-495e-a981-8df14a07f032 | — |
| 22 (root post-merge) | b0fa93b5-f576-406c-a3dc-de6dbb2aef69 | — | — |

Fanout-branch source sessions are recorded in each clone's own report; six branches spanning three cycles (c20 fork `88d75f9754c3` × three clones, c21 fork `0a1b1dca4f9b` × three clones) contribute their own per-cycle researcher/worker/auditor triples.

### A.11 c22 handoff status

M-V3-FOCUS-1: `in_progress/high` with four internal-gate accepts on record and Peach Dream PARTIAL Option-3-terminal. Awaits operator ear on the three M-V3-FOCUS-1 A/B pairs to promote to `validated` per FD-6.

M-V3-CORPUS-1: still frozen. Unblock gated on operator ear accept on M-V3-FOCUS-1 per D-A.

M-V3-RULES-1, M-V3-EAR-1, M-V3-GEN-1: still frozen. Unchanged.

Chicken Grease palette-becomes-primary decision: pending operator D-D confirmation on the palette A/B pair with MINOR-3 mechanism discrimination framed explicitly.

Egress unblock: pending. Would unlock sfizz palette recovery path for a genuine sampler-based palette test if the D-D outcome directs the campaign that way.
