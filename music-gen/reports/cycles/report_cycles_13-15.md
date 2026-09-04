---
title: "Chicken Grease sound-matching arcs — cycles 13–15"
date: "2026-09-04"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# Chicken Grease sound-matching arcs — cycles 13–15

## Abstract

Cycles 13–15 close the last three per-instrument sound-matching arcs for the Chicken Grease song of the Music-Gen v4 closure campaign. The goal was to drive the `M-V4-SHOWCASE-1` deliverable — a Chicken Grease A/B render whose per-stem tracks are either synthesized from pinned SoundFont / stem-sampled profiles or explicitly refused with a documented substitute — to a state where a smoke test reports no missing cells. At cycle 15 close, that state is reached: all five per-instrument cells (bass, drums, guitar, piano, other-residual) have terminal verdicts, and the vocals stem is covered by a pre-existing hybrid-overlay policy. Two of the five terminal verdicts (drums, guitar) are refusals — the sound-matching sweep exhausted both explored render families under a retained absolute floor on the VGGish embedding-cosine similarity metric, and the operator-heard reference stem is substituted verbatim in the showcase mix. Two more (piano, other-residual) are grounded null findings: the underlying stems are inaudible, and the derived per-instrument MIDI transcription is empty. One (bass) had already been accepted at cycle 9. Alongside the arc closures the three cycles produced two campaign-scoped process documents — a codification of the invariants an agent applies when resolving a pre-registered options fork without waiting on the operator, and an interpreter-guard policy for new scripts. A latent correctness concern about the sign convention of the embedding metric was surfaced at cycle 15 and deferred for operator adjudication in cycle 16; the concern does not affect the safety of the refuse-and-substitute deliveries but may affect the interpretation of every arc's verdict.

## 1. Introduction

The v4 closure campaign is organized as a sequence of per-song, per-instrument sound-matching arcs. Each arc searches two frozen render families — a General-MIDI SoundFont sweep (family "sf2") and a stem-sampled concatenative builder (family "family2") — for a configuration whose 6-second render best matches the reference stem, scored under a fixed composite objective and evaluated against a fixed decision protocol. The protocol has three outcomes: a candidate above the 0.60 VGGish embedding-cosine threshold is `CONFIRMED`; a family whose best candidate falls below the 0.40 floor is `RULED_OUT`; anything between the two is `STILL_INDETERMINATE`. When both families are ruled out, the arc is closed as `EXHAUSTED_NO_CONFIRMED` and the acceptance question is escalated to a pre-registered options fork, one of which is always to refuse the sub-milestone and substitute the operator-heard reference stem into the deliverable.

At the start of cycle 13 the campaign held: bass accepted at cycle 9 under a hybrid `OPT1+OPT3` operator directive; drums arc-exhausted at cycle 12 with a three-option acceptance fork awaiting adjudication; three CG instrument cells untouched (guitar, piano, other-residual); vocals covered by a pre-existing hybrid-overlay policy. Cycles 13–15 were tasked with closing those three untouched cells, resolving the drums acceptance fork, and driving the CG A/B render scaffold from `n_missing = 4` to `n_missing = 0`. Because the last three cycles all executed sequentially against a single song with the same objective and decision protocol, this report treats them as one continuous piece of work and organizes by outcome rather than by cycle boundary.

## 2. Grounded null findings: piano and other-residual (cycle 14)

Two of the six per-instrument tracks in the Chicken Grease `merged.mid` — piano (track 5, GM program 0, MIDI channel 2) and other-residual (track 4) — carry zero `note_on` events. Both were produced by the v3 spine's MuScriptor stem transcription during the earlier `cert_run1` unified-driver run; the four sibling stems carry non-empty transcriptions (drums 186, bass 65, guitar 391, vocals 0-by-policy).

A cycle-13 draft null finding rested on the empty transcription alone. Cycle 14 grounded both nulls in a stem-level audibility measurement using a small helper (`measure_stem_audibility.py`) that reports LUFS-I via `pyloudnorm` and falls back to RMS-dBFS when LUFS-I is non-finite. Both reference stems yielded `pyloudnorm = -inf LUFS-I` (silence-only or near-silence-only content), and the RMS-dBFS fallback measured piano at −81.53 dBFS and other-residual at −81.73 dBFS. Both sit far below the −60 dBFS silence floor. With no audible reference and no MIDI target, the sf2 sweep has no synthesis target by construction, and no retry with looser transcription thresholds is warranted (this is a `FD-1` no-retry / no-fallback binding rule, cited explicitly in the null-finding manifests). The showcase consequence is trivial: the mix uses the original (silent) htdemucs stem verbatim, matching what the v3 spine already does for empty tracks. Both null-finding manifests carry an `audibility_measurement` block with the WAV SHA and the measured dBFS values as first-class evidence, and the cycle-14 `other` sibling closes an audit note from cycle 13 that had asked for symmetry with the piano null.

## 3. Chicken Grease guitar arc (cycles 13–15)

The guitar arc followed the shape established by the earlier bass and drums arcs: a 15-preset SoundFont coarse sweep, a fine-fit stage-2 sweep on the coarse top-5 programs, a family verdict, then a stem-sampled family-2 spike, builder, and family verdict, then an arc closeout if both families rule out.

### 3.1 Cycle 13 — stage 1 (coarse sweep)

`coarse_sweep_sf2_guitar.py` ran the guitar-analogue of the c1 bass / c10 drums coarse sweep across GM programs 24–31 (the standard guitar bank) plus a small set of adjacent programs, evaluating 6-second renders of `guitar.mid` (391 `note_on` events on MIDI channel 1) against the reference stem. The stage-1 leaderboard ranks the "Nylon" program ahead of the source-of-truth "Rock Guitar" (GM program 27), the third instance in the campaign of the frozen composite ranking a non-source-of-truth program ahead of the source-of-truth program on a CG instrument (following bass c1 organ > bass, and drums c11 Power Kit > Standard Kit).

### 3.2 Cycle 14 — stage 2 (fine fit) and SF2 verdict

`fine_fit_sf2_guitar.py` swept a 180-cell grid (programs × gain × reverb × post-processing) over the coarse top-5. The stage-2 leaderboard ranks GM program 28 (a muted-electric variant; the c14 profile carries a cosmetic label of "Jazz Guitar" that a later cycle notes should be corrected to the GM standard name) ahead of the source-of-truth program 27 (best rank 84). The top-1 configuration — program 28, gain 1.5, reverb 0.7, EQ-only post-processing — scores composite 129.65, mel-L1 14.72 dB, spectral-centroid RMSE 463 Hz, and **embedding-cosine 0.2584**. The maximum embedding-cosine across all 180 cells is 0.3345.

The cycle-14 worker pinned this as `guitar.json` (profile UUID `bb3e537b-…`, SHA `5e6220ad…`) and emitted a canonical replay proof (`guitar.replay_proof.json`, canonical replay SHA `e2fee72dfa6b408e…`, verdict `REPLAY_PROOF_HOLDS`). The family verdict `guitar_family_verdict.json` records **`SF2_RULED_OUT`** with the verdict reason `top-1 emb_cos 0.2584 < 0.40 retained absolute floor`.

The cycle-14 verdict manifest carries a `systematic_finding` note explicitly recognizing this as the fourth arc where the composite outranks the source-of-truth program, and characterizes the pattern as "content-specific, not a defect."

### 3.3 Cycle 15 — family-2 stem-sampled builder and verdict

Once the SoundFont family ruled out, cycle 15 authored the family-2 stem-sampled path end to end. Two scripts were added under the interpreter-guard policy's canonical `#!/usr/bin/python3` shebang:

- `family2_stem_sampled_guitar_spike.py` builds a slice bank from onsets on the reference stem. Bank diagnostics report 147 detected onsets, of which 37 are voiced (i.e. `pyin` returned a defined pitch within the E1–E7 range), yielding **5 unique MIDI pitches** in the bank. The scarcity of voiced content in the guitar reference stem is explicitly flagged in the manifest as a known limitation.
- `family2_stem_sampled_guitar_builder.py` renders `guitar.mid` by dispatching each of the 391 events to the nearest-pitch bank sample and pitch-shifting the sample with `pyin` down to (or up to) the target pitch. All 391 events route successfully; a librosa `UserWarning` about `pyin` `fmin = 41 Hz` is preserved (kept intentionally to cover the E1 42.2 Hz corner).

The render lands at `guitar_family2_render/render.wav` (SHA `f41560714a68415c…`). The replay proof runs the builder twice into fresh temp directories under the canonical 7-key replay-time environment pin (`2ac444c36298d6ad…`); both runs reproduce byte-identically. The verdict manifest `guitar_family2_verdict.json` records:

| field | value |
|---|---|
| composite | 164.03 |
| mel_L1_dB | 13.17 |
| spectral_centroid_RMSE_Hz | 626.2 |
| embedding_cos_vggish | **0.03543** |
| verdict | **`FAMILY2_RULED_OUT`** |

with the verdict reason `emb_cos_vggish 0.0354 < 0.40 retained absolute floor`. The predicted-value outcome from the systematic four-arc pattern (bass family-2 at 0.0896; drums family-2 at 0.0372) is recorded in the manifest's `systematic_pattern_note`; the actual measured value is stated honestly rather than fitted to the prediction.

### 3.4 Arc closeout and acceptance fork

`guitar_arc_closeout.json` records **`CG_GUITAR_ARC_EXHAUSTED_NO_CONFIRMED`** with both family verdicts and their best embedding-cosine values enumerated; the manifest's `systematic_finding` notes that this is the third CG-instrument arc to exhaust with no `CONFIRMED` family, mirroring the shape of the c7 bass and c12 drums closeouts.

The pre-registered options fork `_manager/M-V4-SHOWCASE-1-cg-guitar-acceptance-policy.json` enumerates three options:

1. **OPT1** — accept the SF2 top-1 (program 28, embedding-cosine 0.2584) as the guitar WINNER via composite-relative extension of the cycle-9 bass acceptance precedent.
2. **OPT2** — accept the family-2 render (embedding-cosine 0.0354) as WINNER via embedding-first tiebreak.
3. **OPT3** — refuse the guitar showcase and deliver the CG A/B with the htdemucs reference stem substituted verbatim.

The fork was resolved by the agent under the codified selection invariants (see §4). OPT1 fails invariant (a) — it requires extending the scope of an operator directive that is currently CG-bass-only — and fails invariant (b) — the candidate is below the 0.40 retained floor. OPT2 fails invariant (b). OPT3 satisfies all four invariants and is selected. The fork manifest's status is set to `resolved_via_agent_picks_invariants` and a delivery-scope pinned profile `cg_guitar_pinned_profile.json` is written under `data/v4/deliveries/31a164f845f8e27e/` recording the OPT3 choice, the rejected options with per-option rationales, the SHA of the substituted htdemucs stem (`e4ff08ea10f9bbcb…`), and a cosmetic-label correction note for the c14 profile.

## 4. Process codification

Two campaign-scoped documents were emitted during these cycles.

### 4.1 Agent-picks selection invariants (cycle 14, extended cycle 15)

`docs/agent_picks_selection_invariants.md` codifies the rules an agent applies when it must resolve a pre-registered options fork without waiting on the operator (the campaign's binding anti-stall rule forbids null-cycle "waiting" behaviour). The document was written at cycle 14 in response to a cycle-13 mis-resolution of the drums acceptance fork: at cycle 13 the agent had elected OPT1 (composite-relative WINNER extension) with a rejection of OPT3 that rested on a paraphrase of OPT3's text as "extending the vocals-only hybrid overlay to drums", where the pre-registered verbatim text was "refuse the drums showcase, use htdemucs drums track as-is in the mix" (a refuse-and-substitute, not an overlay). The cycle-14 auditor flagged this as an incorrect resolution; the cycle-14 worker retracted the cycle-13 pick and re-resolved to OPT3 by codifying three invariants:

- **(a) Prefer no operator-scope extension** — when one option requires enlarging an operator directive's scope and another stays within it, prefer the one that stays within.
- **(b) Prefer above-floor over below-floor** — when one option selects a candidate below a retained absolute floor and another selects an above-floor candidate or takes a non-candidate policy path (such as refuse-and-substitute), prefer the latter.
- **(c) Do not reject an option based on a misreading of its own definition** — quote the option's pre-registered text verbatim before rejecting it; if the rejection depends on a paraphrase that contradicts the verbatim text, the rejection is invalid.

Cycle 15 extended the document with a fourth invariant, prompted by a cycle-14 discrepancy in which a brief-hardcoded value diverged from the on-disk canonical value and the worker silently followed the on-disk value without disclosing the divergence:

- **(d) On-disk-versus-brief divergence disclosure norm** — if on-disk truth (anchor SHAs, leaderboard ranks, script contents, grid contents) diverges from the brief text, the divergence must be explicitly disclosed in the work-output issues block, with the on-disk value pinned by SHA and the rationale for choosing on-disk over brief stated. `FD-1` makes on-disk truth authoritative; invariant (d) makes silent-honoring of on-disk truth an anti-pattern.

The invariants sit under (never above) the campaign's binding specs — the `FD-1` retry/tuning/fallback ban, the `FD-6` operator-ear authority, the `FD-16` environment-pin and replay-proof scoping rules, and the operator directive of 2026-09-03 — and constrain only the agent's judgment call, not the operator's.

The cycle-15 guitar acceptance fork (§3.4) was resolved conformantly to all four invariants on the first attempt, which the cycle-15 auditor recorded as empirical validation of the cycle-14 auditor's stated purpose for the codification.

### 4.2 Interpreter guard policy (cycle 15)

`docs/interpreter_guard_policy.md` formalizes an earlier informal convention: new Python scripts added to `scripts/sound_match/` and its siblings from cycle 13 onward must use `#!/usr/bin/python3` (absolute path) rather than `#!/usr/bin/env python3`. The convention was in place informally since cycle 1 to make interpreter choice explicit and avoid PATH-derived Python drift across cycles. Two pre-cycle-13 anchor scripts (`family2_stem_sampled_drums_spike.py` and `family2_stem_sampled_drums_builder.py`, both cycle 12) use the `env` form and are grandfathered as read-only; on this system both forms resolve to `/usr/bin/python3`, so the grandfathering is safe. The policy is enforced through the corresponding tests in `tests/test_sound_match_family2_drums.py`.

## 5. Latent correctness concern — the embedding metric sign convention

The cycle-15 auditor surfaced a semantic question about the embedding metric that threads through every family verdict since cycle 1. The panel `scripts/texture/embedding_panel.py` computes `_cosine_distance(u, v) = 1.0 - cos_sim` and emits the value as `embedding_cosine_distance` (in `[0, 2]`, lower = more similar). The composite objective consumes it correctly as a distance (`+ 0.25 * (embedding_cos_dist * 100.0)`, minimize composite = better match). However, downstream profile and verdict manifests carry the value as `embedding_cos_vggish` (the `cos` suffix reads as a similarity), and the campaign's frozen decision-protocol thresholds — `≥ 0.60 CONFIRMED`, `< 0.40 RULED_OUT` — are worded as if the value were a similarity (higher = better).

If the field is truly a distance, the c15 guitar family-2 value 0.0354 means cos-similarity ≈ 0.965 — extremely similar to the reference stem — rather than "very dissimilar." Under the intended-threshold semantics, the correct application would reject only when the distance exceeds 0.60. Under the current application, low-distance candidates get `RULED_OUT` precisely because they are close matches. The concern is not a defect that a worker could fix unilaterally under `FD-1` (which forbids threshold retuning without cause); it is a semantic ambiguity in the frozen decision protocol that requires operator adjudication, and it potentially inverts the interpretation of every CG family verdict in the record (bass c3, c6; drums c11, c12; guitar c14, c15).

The cycle-15 auditor's guidance for cycle 16 is (i) run a controlled two-clip probe — feed the panel two copies of the same clip and two orthogonal noises; a `~0.0` for the first pair and `~1.0` for the second confirms it is a distance — and (ii) present the operator with a binary choice between correcting the thresholds (accepting that most or all prior candidates would `CONFIRM` under the corrected reading) and correcting the panel or its consumer to emit similarity (with a corresponding trigger under `FD-16(a)` to re-issue every downstream replay proof because the numeric contract of every future profile changes). The refuse-and-substitute pins for drums and guitar remain safe regardless: the htdemucs reference stems they substitute are the operator-heard truth by construction, and no interpretation of the embedding metric makes them worse.

## 6. State of the deliverable

At cycle-15 close all five CG instrument cells in `M-V4-SHOWCASE-1` are terminal:

| cell | terminal state | source of showcase audio |
|---|---|---|
| bass | accepted (cycle 9) | `bass_v2.json` render (GM program 33) |
| drums | refused (cycle 14 OPT3) | htdemucs `drums.wav` verbatim |
| guitar | refused (cycle 15 OPT3) | htdemucs `guitar.wav` verbatim |
| piano | grounded null (cycle 14) | htdemucs `piano.wav` verbatim (silent) |
| other-residual | grounded null (cycle 14) | htdemucs `other.wav` verbatim (silent) |
| vocals | policy hybrid-overlay (pre-existing) | htdemucs `vocals.wav` overlaid on the instrumental mix |

The smoke test `python scripts/sound_match/deliver_cg_ab_v4.py --smoke-test` reports `n_missing = 0`. The end-to-end CG A/B render is a substantive-advance path unblocked in cycle 16, alongside the embedding-metric adjudication.

The systematic pattern noted across the arcs — three consecutive CG-instrument arcs (bass c7, drums c12, guitar c15) exhausted both explored render families under the retained 0.40 floor, and five instances of the composite ranking a non-source-of-truth GM program ahead of the source-of-truth program — is recorded in each arc-closeout manifest as a content-specific characterization, not a defect claim. Under the latent embedding-metric concern of §5 this pattern may reduce to a threshold-application artifact rather than an empirical finding about the objective's behaviour on Chicken Grease content; the auditor's guidance explicitly asks that the pattern not be extended further until the metric question is settled.

## 7. Discipline gates and validators

Across the three cycles the following discipline gates held:

- **Anchor immutability.** The cycle-9 bass anchor (`832868d0…`), the cycle-11 drums anchor (`dadafcfc…`), and the cycle-14 guitar anchor (`e2fee72d…`) are byte-identical pre- and post-cycle at every subsequent cycle's boundary. The cycle-11 `replay.py` channel-aware fix's post-patch SHA is unchanged through cycle 15.
- **Absence of forbidden constructs.** No PRNG use in any new script (grep-verified by each cycle's auditor). No imports from the `sidecar_nonfactor` module (which the campaign forbids). The `/usr/bin/python3` interpreter guard is present on every new script authored from cycle 13 onward.
- **Replay-proof scoping.** Every emitted family verdict has a per-family per-song replay proof under the canonical 7-key environment pin `2ac444c36298d6ad…`, satisfying `FD-16(c)`.
- **Validators.** `promise_check` runs 0 ERROR through cycle 15 (pre-existing WARN count drifts within a ~3-WARN band across cycles 12–15; the drift is scheduled for a cycle-16 audit fill-in). `org_check` runs 0 ERROR through cycle 15.

## 8. Open items

Handed forward to cycle 16 in order of priority:

1. **Adjudicate the embedding-metric sign convention** (§5). Run the two-clip diagnostic; present the operator with the correct-the-thresholds vs. correct-the-panel choice; re-interpret prior arc verdicts as needed. Do not extend the systematic-pattern narrative or re-open the refuse-and-substitute pins until this is settled.
2. **Execute the CG A/B render end to end** — the scaffold is unblocked and every cell is terminal.
3. **Formalize the pinned-profile shape.** The c14 drums pinned profile carries a nested `acceptance_fork.invariants_doc` key; the c15 guitar pinned profile folds the same content into an `authority` string. Neither is a defect, but the drift is exactly the class of thing invariant (d) was written to prevent, applied to profile schemas rather than sweep grids. Options are an invariant (e) on pinned-profile cross-cycle shape stability, or a JSON Schema alongside `profile_writer.py`.
4. **Back-fill test debt.** Author tests for `family2_stem_sampled_guitar_spike.py` and `family2_stem_sampled_guitar_builder.py`; add an adoption row to close the ~3-WARN drift on `promise_check`; add an audibility measurement smoke test.
5. **Correct the cosmetic GM label** on `guitar.json` in a follow-up if operator authority for anchor-touch is granted (the profile parameters are correct; only the human-readable program name is wrong).

## 9. Discussion

The three-cycle span shows two closely related dynamics worth noting for the reader.

The first is that the acceptance-fork resolution mechanism went through one full observe-then-codify iteration and one full codify-then-apply iteration inside these three cycles. Cycle 13 resolved the drums fork incorrectly under an implicit rule; cycle 14 codified the rule explicitly in response to that failure and re-resolved the drums fork correctly; cycle 15 encountered the same fork shape on guitar and resolved it correctly on the first attempt using the codified rules. The cycle-14 codification with cycle-15 validation is the healthiest audit-driven feedback loop in the v4 record — every named audit item from the prior cycle closed on the subsequent cycle, with the codified process artefact serving as both the closure evidence and the mechanism preventing recurrence.

The second is that the systematic four-arc pattern surfaced consistently across the arcs — the composite ranking non-source-of-truth programs ahead of source-of-truth programs, and both frozen render families ruling out on every CG instrument by wide margins under the 0.40 floor — was building toward a claim of an empirical finding about the objective's behaviour on Chicken Grease content when the cycle-15 auditor surfaced the sign-convention question in §5. Under the current reading the pattern is a real observation; under the alternative reading the pattern reduces to a threshold-application artifact and the pinned candidates are actually close matches. The correct next move is to settle the ambiguity before extending the narrative — the cycle-15 auditor's explicit guidance — and this report follows that guidance by naming the pattern once (§6) and stopping there. The named anti-pattern from the cycle-15 auditor's discussion, "internal consistency masks external correctness," is a fitting label for the class of concern.

## Appendix: Implementation Details

### A.1 Scripts added or modified during cycles 13–15

Under `scripts/sound_match/`:

- Cycle 13: `coarse_sweep_sf2_guitar.py`; `_emit_c13_ledger_events.py`.
- Cycle 14: `fine_fit_sf2_guitar.py`; `_launch_cg_guitar_stage2_c14.sh`; `_emit_c14_guitar_profile.py`; `measure_stem_audibility.py`; `_emit_c14_ledger_events.py`.
- Cycle 15: `family2_stem_sampled_guitar_spike.py`; `family2_stem_sampled_guitar_builder.py`; `_c15_family2_guitar_emit.py`; `_emit_c15_ledger_events.py`.

Under `docs/`:

- Cycle 14: `agent_picks_selection_invariants.md` (invariants (a), (b), (c)).
- Cycle 15: `agent_picks_selection_invariants.md` extended with invariant (d); `interpreter_guard_policy.md`.

Under `tests/`:

- Cycle 14: `tests/test_sound_match_family2_drums.py`.

### A.2 Data artefacts added during cycles 13–15

Under `data/v4/profiles/31a164f845f8e27e/`:

| file | cycle | SHA prefix |
|---|---|---|
| `guitar_sweep_stage1/leaderboard.tsv` | 13 | – |
| `piano_null_finding.json` | 14 (supersedes c13) | – |
| `other_null_finding.json` | 14 | – |
| `audibility/piano_stem_audibility.json` | 14 | – |
| `audibility/other_stem_audibility.json` | 14 | – |
| `guitar_sweep_stage2/leaderboard.tsv` | 14 | – |
| `guitar.json` | 14 | `5e6220ad9971e8fe…` |
| `guitar.replay_proof.json` | 14 | `cc22105f2ff41509…` |
| `guitar_family_verdict.json` | 14 | – |
| `guitar_family2_v1.json` | 15 | `8a11f6532af572a6…` |
| `guitar_family2_v1.replay_proof.json` | 15 | `e87e09bd91f88ef1…` |
| `guitar_family2_render/render.wav` | 15 | `f41560714a68415c…` |
| `guitar_family2_verdict.json` | 15 | `969c4d2f197f4bcd…` |
| `guitar_arc_closeout.json` | 15 | `a36576d1d3b67576…` |
| `_manager/M-V4-SHOWCASE-1-cg-guitar-acceptance-policy.json` | 15 | `3a0367155cbd543e…` |
| `_c15_guitar_family2_summary.json` | 15 | – |

Under `data/v4/deliveries/31a164f845f8e27e/`:

- `cg_drums_pinned_profile.json` (cycle 14; OPT3 pin for drums)
- `cg_guitar_pinned_profile.json` (cycle 15; OPT3 pin for guitar; SHA `14d0707898b557df…`)

### A.3 Environment pin

The canonical 7-key replay-time environment pin `2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca` (in force since cycle 6) anchors every family verdict, replay proof, and pinned profile emitted in cycles 13–15.

### A.4 Read-only anchors preserved (verified byte-identical pre-cycle and post-cycle across cycles 13–15)

- `coarse_sweep_sf2.py` (cycle 1, SHA `c74c35bc…`); `fine_fit_sf2_v2.py` (cycle 3, SHA `dc03007365aa29be…`); `family2_stem_sampled_{spike,builder}.py` (cycles 5/6); `replay.py` post-cycle-11 patch (SHA `1f43027039c45f5e066c…`); `FluidR3_GM.sf2` soundfont (SHA `74594e8f4250680a…`).
- Bass artefacts: `bass_v2.json`, `bass_v2.replay_proof.json` (anchor `832868d0…`), `bass_arc_closeout.json`, `cg_bass_pinned_profile.json`.
- Drums artefacts: `drums.json`, `drums.replay_proof.json` (anchor `dadafcfc…`), `drums_family2_v1.json`, `drums_family2.replay_proof.json` (anchor `69a76c5b…`), `drums_arc_closeout.json`.
- Cycle-14 anchors extended into cycle 15: `guitar.json`, `guitar_family_verdict.json`, invariants document (a)/(b)/(c) text.

### A.5 Session references

For traceability to the underlying working records:

| cycle | researcher | worker | auditor |
|---|---|---|---|
| 13 | `c06b1659-f97d-4657-a709-04cee245fbb9` | `00b0e8f8-6a58-42c9-b524-f43d635fad44` | `525c2020-2dae-467a-96b2-2372e3f203a7` |
| 14 | `4c0059b5-0c40-4da3-ab74-f976144db2a8` | `40f77ad0-f5ff-4963-8aa6-a4953e74889b` | `5f6569a0-15f3-4190-aca3-bf3633367f9b` |
| 15 | `3e9c817c-d258-4230-aa98-e463d9f377fb` | `1e053bc5-ee9c-4e8a-92ba-2d5249b47f0e` | `ea8ed426-df62-45d6-aac5-d6462803af60` |

### A.6 Cross-references between artefacts

- Cycle-14 guitar stage-2 top-1 → `guitar.json` (SHA `5e6220ad…`) → `guitar.replay_proof.json` (canonical replay SHA `e2fee72dfa6b408e…`) → `guitar_family_verdict.json` (`SF2_RULED_OUT`).
- Cycle-15 family-2 render → `guitar_family2_render/render.wav` (SHA `f41560714a68415c…`) → `guitar_family2_v1.json` → `guitar_family2_v1.replay_proof.json` → `guitar_family2_verdict.json` (`FAMILY2_RULED_OUT`).
- Cycle-15 guitar arc closeout → `_manager/M-V4-SHOWCASE-1-cg-guitar-acceptance-policy.json` (three options, `status = resolved_via_agent_picks_invariants`) → `cg_guitar_pinned_profile.json` (OPT3 delivery pin, `supersedes_path` = the acceptance-policy JSON).
- Cycle-14 drums fork revise → `cg_drums_pinned_profile.json` (OPT3) → `deliver_cg_ab_v4.py --smoke-test` transitions `n_missing` from 4 (cycle 9) through intermediate values to 0 at cycle-15 close.
