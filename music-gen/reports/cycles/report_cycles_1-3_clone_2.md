---
title: "Music-Gen v3 FOCUS Milestone — Fanout Clone 2: Peach Dream (Cycles 1–3)"
date: "2026-09-02"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# Music-Gen v3 FOCUS Milestone — Fanout Clone 2: Peach Dream (Cycles 1–3)

## Abstract

This report covers Cycles 1 through 3 of a fanout-clone branch spawned from the Music-Gen v3 campaign's M-V3-FOCUS-1 milestone. The clone (fork `88d75f9754c3`, clone 2) was assigned the reference track *Peach Dream* (source SHA-16 `88d247468cb6d49f`) with the same scoped objective as its sibling clones on WIG and Rome: run the full v3 per-stem chain end-to-end on the operator-D1-chosen thirty-second section, matching the c5 Chicken Grease Method A delivery format exactly, and emit `data/v3/deliveries/88d247468cb6d49f/cycle20/verdict.json` with `V3_FOCUS_SONG_LANDS_pending_operator` or `PARTIAL/FAILS honestly`. Cycle 1 executed substantive setup work — pre-registration, tempo choice, inherited chosen-section stems, thirteen per-song sibling scripts, a twelve-case test file, and a background launch of htdemucs on the full song — but did not complete the pipeline within its turn. Cycles 2 and 3 both emitted only "pause memos" waiting for the background completion notification, producing zero substantive authorship despite the Cycle 2 research brief carrying explicit anti-Hold-Pattern gating language. On-disk state advanced only through inherited background completion (the full-song htdemucs landed with 24 SHAs byte-deterministic ×2 during the Cycle 2 wait) and did not advance at all during Cycle 3. The required output artifact `cycle20/verdict.json` remained absent for the full arc. The Cycle 3 auditor issued PIVOT with a CRITICAL escalation to the root conductor: three consecutive turns of the Hold Pattern anti-pattern have confirmed the failure mode as structural on this clone, and the auditor recommends the root conductor pick one of three named options rather than continue this clone. The branch merges as INSUFFICIENT — the only blocking call in fork `88d75f9754c3`, with substantial on-disk positive state preserved for whichever recovery path the root conductor selects.

## 1. Introduction and scope

The M-V3-FOCUS-1 milestone widens the M-V3-SPINE-1 pipeline to five focus songs read from `data/recreate_v2/focus_set_v2.json`. Fork `88d75f9754c3` operates under a Cycle 20 operator BREAK-GLASS carveout that authorized parallel substantive work on four focus songs while Chicken Grease continues to wait on operator ear under Fixed Decision 6.

This report is the merge-disposition summary for clone 2 (Peach Dream). Sibling clones in the same fork:

- **Clone 0 (WIG, sha16 `252eb21ce7df7328`)** — BRANCH_COMPLETE, PARTIAL (MuScriptor 3/7).
- **Clone 1 (Rome, sha16 `51e433ade2a845e1`)** — BRANCH_COMPLETE, LANDS_pending_operator (full end-to-end chain).
- **Clone 2 (Peach Dream, sha16 `88d247468cb6d49f`)** — this branch. INSUFFICIENT.

The clone's scoped objective as issued was identical in shape to its siblings: read the chosen section from `focus_set_v2.json`; run htdemucs_6s on both the chosen section and the full song with 24 stem SHAs byte-deterministic ×2; run MuScriptor on the seven probes; canonicalize MIDI via the read-only c4 serializer; merge with four structural gates; choose tempo via `librosa.beat.beat_track` on the chosen-section drums; render per-track ×2 via fluidsynth; overlay D2 vocals via a SHA-verified htdemucs vocals copy; mix-match via the c5 Method A pattern; emit A/B WAVs, full-song WAV, and manifest under `data/v3/deliveries/88d247468cb6d49f/` matching the c5 Chicken Grease format; measure the M-TEX-1 eight-key perceptual panel; emit `cycle20/verdict.json` with the strongest permitted verdict and the three-way rubric chain byte-equal; land a twelve-case test suite at `tests/test_v3_focus_peach_dream_c20.py`; emit the standard four-row housekeeping under a `-clone-2` suffix. Required deliverable: `data/v3/deliveries/88d247468cb6d49f/cycle20/verdict.json`.

## 2. Cycle 1: substantive setup and background launch

Cycle 1 was the branch's only cycle with substantive authorship. The worker executed the pipeline prologue in the following order and completed each named step:

- Pre-registered the sub-leaves in the plan-of-record with the `-clone-2` suffix.
- Read the chosen section from `focus_set_v2.json`.
- Landed the inherited chosen-section six-stem WAVs at `data/v3/deliveries/88d247468cb6d49f/stems_6s/`.
- Ran `librosa.beat.beat_track` on the chosen-section drums stem and recorded the tempo choice.
- Landed thirteen per-song sibling scripts under `scripts/v3_spine/peach_dream_c20_*.py` — the individual drivers for htdemucs, MuScriptor, canonicalize, merge, render, vocals-overlay, mix-match, deliver, panel, and verdict, each of which reads its c5 sibling script (`mix_match_operator_section.py`, `midi_from_json_events.py`, etc.) read-only.
- Landed the twelve-case test suite at `tests/test_v3_focus_peach_dream_c20.py`.
- Ran MuScriptor synchronously on three probes (drums, bass, guitar) with the guitar transcription returning the canonical empty-events JSON (two bytes, `{}`).
- Launched htdemucs on the full song as a background task with the expectation that the completion notification would surface in a subsequent turn.

At Cycle 1 close the on-disk state was:

- `data/v3/deliveries/88d247468cb6d49f/stems_6s/` — six chosen-section stem WAVs present.
- `data/v3/deliveries/88d247468cb6d49f/stems_6s_full_song/` — created as the background htdemucs output directory.
- `data/v3/deliveries/88d247468cb6d49f/muscriptor_operator_section/` — three probes (drums, bass, guitar) with JSON + MIDI pairs; guitar.json at the canonical empty-events size of two bytes.
- `data/v3/deliveries/88d247468cb6d49f/operator_section/` and `.../per_track/` — empty (downstream stages had not run).
- `data/v3/deliveries/88d247468cb6d49f/cycle20/` — empty (required verdict artifact not yet emitted).

The Cycle 1 audit accepted the substantive setup work as valid partial progress toward the c20 objective and did not raise a Hold Pattern finding at that point; the background launch was consistent with the standard fanout-clone pattern of dispatching htdemucs full-song and returning to close the pipeline once it completes.

## 3. Cycle 2: first pause memo, background htdemucs lands

Cycle 2 produced no new substantive authorship. The worker output was a "pause memo" of the shape *"I'll wait for the muscriptor completion notification. The background task will notify when muscriptor_determinism.json lands"* — a wait-on-notification note without any script invocation, synchronous MuScriptor advance, downstream chain execution, verdict emission, or housekeeping row.

On-disk state did advance during the wait, but not through this turn's authorship: the background htdemucs full-song task launched in Cycle 1 completed, and `data/v3_spine/88d247468cb6d49f/htdemucs_determinism.json` landed with the full-song 24 SHAs byte-deterministic across two runs. This is genuine positive on-disk state on the branch, but under the harness's authorship discipline it is inherited background output rather than Cycle 2 work.

The Cycle 2 audit flagged the Hold Pattern anti-pattern as MODERATE, disclosed the escalation threshold explicitly — *"Two consecutive deferral cycles on this clone. If c21 also produces pause memo, escalate to CRITICAL and hand back to root conductor for scope compression or reassignment."* — and issued PIVOT back to the researcher. The research brief for Cycle 3 was drafted with explicit anti-Hold-Pattern gating language: *"Do NOT `run_in_background` and wait."*

## 4. Cycle 3: second pause memo, escalation

Cycle 3 produced no new substantive authorship and no new on-disk advancement. The worker output was again a pause memo of the same shape as Cycle 2, despite the Cycle 2 research brief's explicit anti-Hold-Pattern gate. No script was invoked, no synchronous MuScriptor completion attempted, no downstream chain executed, no verdict emitted, no housekeeping row landed. Every stage of the c20 pipeline downstream of htdemucs full-song remained in the same state it was in at Cycle 2 close:

- MuScriptor: still 3/6 probes, guitar.json still the canonical two-byte empty-events file, unchanged bytes and mtime.
- Canonical MIDI, merge, per-track render, vocals overlay, mix-match, delivery, panel, tests, housekeeping — all `not_run`.
- `data/v3/deliveries/88d247468cb6d49f/cycle20/` still empty; required verdict artifact still absent.

The Cycle 3 auditor issued **PIVOT with CRITICAL escalation to root conductor**. The rationale cites four converging constraints:

1. **Cannot VALIDATE** — the `<no-null-cycle-validation>` rule forbids VALIDATED on a cycle whose work_output is a bare pause memo with no authored substantive artifact.
2. **Cannot fabricate LANDS** — Fixed Decision 1 forbids fabricating positive verdicts on absent artifacts.
3. **Cannot COMPLETE** — the branch scope is genuinely incomplete: the required deliverable does not exist on disk, so `COMPLETE`/`[[BRANCH_COMPLETE]]` is not available.
4. **Cannot INVALIDATE** — there is no prior VALIDATED judgment on this milestone to reverse.

The auditor's assessment against the fourteen c20 rubric sufficiency criteria: 0/14 met. The verdict artifact is absent; the three-way `rubric_hash_v2` chain has no verdict to chain against; MuScriptor is 3/6 not 6/6, with no run-2 for the landed three; canonical MIDI, merge with four structural gates, per-track render, D2 vocals overlay, rc7 Method A mix-match, A/B WAVs, full-song WAV, manifest, eight-key panel, twelve-case test execution, four-row housekeeping, c19 backref verification, anchor preservation POST snapshot — none have run. Sub-topic completion has regressed into a repeated no-op state.

Under the operating protocol's "Max regressions before halt: 2" rule and the third-regression escalation clause, the auditor determined that three consecutive Hold Pattern turns confirm the pattern as structural on this specific clone rather than incidental, and that continuing to PIVOT back to the researcher would burn cycles without breaking the loop. Escalation to root conductor is the honest verdict.

## 5. Root-conductor escalation

The Cycle 3 auditor's escalation packet names three viable options for the root conductor:

**Option 1 — Reassign the Peach Dream fanout branch to a fresh clone under a new fork.** This clone's turn cadence has entered a stable no-op attractor; a context reset is likely necessary to break the Hold Pattern loop. Substantive on-disk state from Cycle 1 (pre-registration, tempo choice, inherited chosen-section stems, background-landed full-song htdemucs) and the thirteen sibling scripts and test file all carry forward to any successor clone.

**Option 2 — Scope-compress.** Split the c20 objective into two sub-branches: one branch completes MuScriptor 3/6 → 6/6 only (roughly five minutes of synchronous wall time), and a second branch runs the downstream sweep from a landed 6/6 MuScriptor state. Empirically the "full end-to-end chain in one turn" scope has not converged on this clone. A benefit of the MuScriptor-only sub-branch is that it would explicitly stress-test the c3 anti-pattern (`muscriptor-nondeterministic-falsified`, the MuScriptor bass MIDI container encoding drift), which Cycle 1's Run-1-only 3/6 landing did not touch.

**Option 3 (auditor's recommendation) — Accept the current 3-turn deferral as terminal for this clone and merge the substantive Cycle 1 and background-landed deliverables as a first-class `V3_FOCUS_SONG_PARTIAL` outcome per Fixed Decision 1**, with `honest_partial_reasons = ["clone_hold_pattern_terminal_3_turns", "muscriptor_incomplete_3_of_6", "downstream_chain_not_executed"]`. The auditor would draft the PARTIAL `verdict.json` under `data/v3/deliveries/88d247468cb6d49f/cycle20/` at the root-conductor level.

The auditor's rationale for recommending Option 3: it preserves the substantive on-disk advancement (particularly the full-song htdemucs 24 SHAs byte-deterministic ×2), honors the campaign's anti-fabrication contract cleanly, delivers a first-class negative finding rather than continuing to burn cycles, and unblocks the fanout root to move on. Option 1 (reassign to fresh clone) is second choice on the grounds that the current clone's cadence has not proven capable of executing the downstream sweep within a turn.

The auditor explicitly warned against a fourth PIVOT back to the researcher on this clone: three consecutive turns confirm the pattern is structural, not incidental; per the operating protocol's third-regression rule this session has hit a fundamental blocker (worker cannot escape Hold Pattern on this specific downstream chain despite explicit brief-level gates) and requires user or root-conductor input to break.

## 6. On-disk state at branch close

Positive state that carries forward to any successor clone:

- `data/v3/deliveries/88d247468cb6d49f/stems_6s/` — six chosen-section stem WAVs.
- `data/v3/deliveries/88d247468cb6d49f/stems_6s_full_song/` — six full-song stem WAVs (via background htdemucs completion during Cycle 2).
- `data/v3_spine/88d247468cb6d49f/htdemucs_determinism.json` — full-song 24 SHAs byte-deterministic ×2.
- `data/v3/deliveries/88d247468cb6d49f/muscriptor_operator_section/` — three probes (drums, bass, guitar) with JSON + MIDI pairs; guitar.json is the canonical two-byte empty-events file (a first-class outcome, not a failure).
- `scripts/v3_spine/peach_dream_c20_*.py` — thirteen per-song sibling drivers landed under the read-only-consumer-of-c5-scripts pattern.
- `tests/test_v3_focus_peach_dream_c20.py` — twelve-case test suite landed.
- Cycle 1 tempo choice recorded.

Absent state that blocks LANDS:

- `data/v3/deliveries/88d247468cb6d49f/cycle20/` — empty; required verdict artifact absent.
- `data/v3/deliveries/88d247468cb6d49f/operator_section/` and `.../per_track/` — empty.
- MuScriptor 3/6 not 6/6; no run-2 for the landed three; canonical MIDI, merge, render, vocals overlay, mix-match, delivery, panel, tests-executed, and four-row housekeeping all `not_run`.
- Three-way `rubric_hash_v2` chain not asserted (no verdict to chain).
- c19 backref not verified live at emit (no emit).
- Anchor preservation POST snapshot not taken.

`promise_check` reports zero errors and roughly 3 001 warnings (pre-existing cross-fanout drift; not attributable to this cycle). `org_check` reports pre-existing figure-location warnings.

## 7. Merge disposition

**Merge disposition: INSUFFICIENT.** The branch does not merge under `[[BRANCH_COMPLETE]]`; it hands back to the root conductor with a CRITICAL escalation packet and the three named options. The auditor recommends Option 3 (auditor-drafted PARTIAL merge). The merge report at `/home/user/music-gen-instance-v3/fork-88d75f9754c3/clone-2/merge_report.md` carries the CRITICAL Hold-Pattern-terminal finding, the three named options, the auditor's recommendation, and the enumeration of substantive on-disk state that is preserved as first-class positive on-disk state for whichever recovery path the root conductor selects.

Peach Dream stands as the only blocking call in fork `88d75f9754c3`. The auditor notes it as the exception to the fork's otherwise-clean fanout track record: clone 0 (WIG) landed an honest PARTIAL and terminated by BRANCH_COMPLETE; clone 1 (Rome) landed a full LANDS_pending_operator and terminated by BRANCH_COMPLETE.

## 8. Campaign-level implications

Two of the fork's three attempted clones advanced substantively (WIG PARTIAL and Rome LANDS_pending_operator). Peach Dream is the failure mode. The Cycle 3 auditor's cumulative notes flag two forward-looking observations:

- The Hold Pattern anti-pattern is enumerated in the campaign's operating protocol under `<anti-pattern name="The Hold Pattern">`, and this branch's three-turn structural failure to escape it despite explicit brief-level gates is evidence that the anti-pattern's suppression mechanism (research-brief-level gating) is not sufficient on its own to prevent a worker from re-entering the pattern under the conditions of this specific clone. The auditor's Option 2 (scope-compress into a MuScriptor-only sub-branch plus a downstream sub-branch) is one plausible structural response.
- The c3 anti-pattern `muscriptor-nondeterministic-falsified` — the MuScriptor bass MIDI container encoding drift observed in the campaign's third cycle — has not been stress-tested by this branch, because MuScriptor Run-2 never ran on the three landed stems. Any successor Peach Dream cycle that completes MuScriptor 6/6 byte-deterministic ×2 would be the first cycle to touch this concern on this song.

The M-V3-SPINE-1 Chicken Grease operator-ear gate remains open per Fixed Decision 6 and is not disturbed by this clone's failure. The panel-is-never-a-LANDS-gate discipline under Fixed Decision 6 has held cleanly across all fifteen-plus verdicts to date including the two BRANCH_COMPLETE sibling clones.

## 9. Conclusions

Clone 2 of fork `88d75f9754c3` did not deliver its scoped objective. Cycle 1 executed substantive setup and launched the background htdemucs correctly; Cycles 2 and 3 produced only pause memos and did not authore any substantive artifact, despite the Cycle 2 research brief carrying explicit anti-Hold-Pattern gating language. Positive on-disk state exists — full-song htdemucs 24 SHAs byte-deterministic ×2 landed via background completion during Cycle 2, and thirteen per-song sibling drivers plus a twelve-case test file are on disk — but the required verdict artifact never emitted and the pipeline never reached MuScriptor 6/6, let alone the downstream chain. The Cycle 3 auditor's PIVOT with CRITICAL escalation is the honest verdict; three consecutive Hold Pattern turns confirm the failure mode as structural on this clone rather than incidental, and the branch hands back to the root conductor with three named recovery options and a recommendation of auditor-drafted PARTIAL merge that preserves the substantive on-disk state as a first-class negative finding.

## Appendix: Implementation Details

### A.1 Required output artifact status

`data/v3/deliveries/88d247468cb6d49f/cycle20/` — empty at branch close. Required output artifact `data/v3/deliveries/88d247468cb6d49f/cycle20/verdict.json` — **ABSENT for the full three-turn arc**. No three-way `rubric_hash_v2` chain assertion possible without a verdict to chain.

### A.2 Positive on-disk state preserved

`data/v3/deliveries/88d247468cb6d49f/stems_6s/` (six chosen-section WAVs); `data/v3/deliveries/88d247468cb6d49f/stems_6s_full_song/` (six full-song WAVs); `data/v3_spine/88d247468cb6d49f/htdemucs_determinism.json` (full-song 24 SHAs, byte-deterministic ×2, landed via background completion during Cycle 2); `data/v3/deliveries/88d247468cb6d49f/muscriptor_operator_section/` (drums, bass, guitar JSON + MID pairs; guitar.json is the canonical two-byte empty-events file); Cycle 1 tempo choice recorded; thirteen `scripts/v3_spine/peach_dream_c20_*.py` sibling drivers; `tests/test_v3_focus_peach_dream_c20.py`.

### A.3 Absent state blocking LANDS

MuScriptor 3/6 not 6/6 (missing other, piano, vocals, full_mix); no MuScriptor Run-2 for the three landed stems; canonical MIDI (7 probes), merge, four-structural-gates check, fluidsynth per-track render ×2, D2 vocals overlay, rc7 Method A mix-match, A/B WAVs, full-song WAV, delivery manifest, eight-key panel, twelve-case test execution, four-row housekeeping ledger, c19 backref verification, anchor preservation POST snapshot — all `not_run`.

### A.4 Anti-pattern classification

`<anti-pattern name="The Hold Pattern">` — three consecutive turns of pause-memo authorship on this clone. Cycle 1 mixed substantive authorship with background launch (not itself a Hold Pattern instance). Cycle 2 pure pause memo, flagged MODERATE. Cycle 3 pure pause memo despite explicit anti-Hold-Pattern gating language in the Cycle 2 research brief, flagged CRITICAL and escalated.

### A.5 Root-conductor escalation options

Option 1 — Reassign to a fresh clone under a new fork (context reset). Option 2 — Scope-compress into two sub-branches (MuScriptor 6/6 only, then downstream sweep). Option 3 (auditor recommendation) — Accept the 3-turn deferral as terminal, merge substantive c20 deliverables as a first-class `V3_FOCUS_SONG_PARTIAL` with `honest_partial_reasons = ["clone_hold_pattern_terminal_3_turns", "muscriptor_incomplete_3_of_6", "downstream_chain_not_executed"]`, and have the auditor draft the PARTIAL `verdict.json` at root-conductor level.

### A.6 Cross-fork context

| Clone | Song | sha16 | Verdict | Merge disposition |
|---|---|---|---|---|
| 0 | What If I Go | `252eb21ce7df7328` | `V3_FOCUS_SONG_PARTIAL_pending_operator` | BRANCH_COMPLETE |
| 1 | Dojo Cuts — Rome | `51e433ade2a845e1` | `V3_FOCUS_SONG_LANDS_pending_operator` | BRANCH_COMPLETE |
| 2 | Peach Dream | `88d247468cb6d49f` | (not emitted) | **INSUFFICIENT — CRITICAL escalation to root conductor** |

### A.7 Validator state at branch close

`promise_check`: 0 ERROR, ~3 001 WARN (pre-existing cross-fanout drift; not attributable to this cycle). `org_check`: 0 ERROR, pre-existing figure-location WARNs from cycles 6/15/25/28.

### A.8 Read-only anchors respected across the branch

Chicken Grease c19 verdict (`data/v3/deliveries/31a164f845f8e27e/cycle19/verdict.json` SHA `1485f281acb42e3f13d50ee1001b8f1b0be14e733f1b122ea366e2390ada6bfd`); c4 canonical MIDI serializer (`scripts/v3_spine/midi_from_json_events.py`); c5 mix-match Method A (`scripts/v3_spine/mix_match_operator_section.py` SHA `4f47fbcd…`); c33 render_stem (`scripts/palette_render/render_stem.py` SHA `214372d9…5b2b`); focus set (`data/recreate_v2/focus_set_v2.json`). All sibling drivers under `scripts/v3_spine/peach_dream_c20_*.py` are structured to consume their c5 anchors read-only.

### A.9 Environment pins

`PYTHONHASHSEED=0`; `SOURCE_DATE_EPOCH=1756463424`; `TZ=UTC`; `LC_ALL=C.UTF-8`; `OMP_NUM_THREADS=1`, `MKL_NUM_THREADS=1`, `OPENBLAS_NUM_THREADS=1`; interpreter `/usr/bin/python3`; `mido==1.3.3`; SoundFont SHA `74594e8f…1cb0`; MuScriptor model SHA `ac80adbd…7fb97ec`.

### A.10 Source sessions

| Cycle | Researcher | Worker | Auditor |
|---|---|---|---|
| 1 | 0b861aa2-80f0-4b27-8e07-1bc8290b0995 | 925e389e-65d0-48f4-acd5-dc6c41a6b059 | c55b3ca1-62a6-41fe-9894-c7bd9598c561 |
| 2 | b94a30d0-2ee7-4385-bc87-44687b328114 | 090e73c2-20c0-4ae8-b6e0-e8d81c951cbb | 9a02dbd7-9144-4418-ac1d-ec43593eb7ca |
| 3 | b5d7d6af-34bc-45e3-854b-3de77ccb18a9 | 529050c2-322d-493b-8fcc-90dbec8f84f7 | 4319dd99-7f37-4857-84ab-ae3cf0ca1429 |

### A.11 Fanout metadata

Fork `88d75f9754c3`. Clone 2 of the Peach Dream assignment. Merge report expected at `/home/user/music-gen-instance-v3/fork-88d75f9754c3/clone-2/merge_report.md` for parent-conductor pickup, carrying the CRITICAL Hold-Pattern-terminal finding, the three named recovery options, the auditor's Option 3 recommendation, and the enumeration of preserved substantive on-disk state.
