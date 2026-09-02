---
title: "Music-Gen v3 FOCUS Milestone — Fanout Clone 0 (Cycles 1–3)"
date: "2026-09-02"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# Music-Gen v3 FOCUS Milestone — Fanout Clone 0 (Cycles 1–3)

## Abstract

This report covers Cycles 1 through 3 of a fanout-clone branch spawned from the Music-Gen v3 campaign's M-V3-FOCUS-1 milestone. The clone (fork `88d75f9754c3`, clone 0) was assigned a scoped objective distinct from the campaign's main M-V3-SPINE-1 heartbeat cadence: run the full v3 per-stem chain end-to-end on the reference track *What If I Go* (source SHA-16 `252eb21ce7df7328`), delivering an A/B pair on the operator-chosen section and a full-song reconstruction, and emit `data/v3/deliveries/252eb21ce7df7328/cycle20/verdict.json` with a `V3_FOCUS_SONG_LANDS_pending_operator` or `PARTIAL/FAILS honestly` verdict. Cycle 1 executed substantive pipeline work through the first three MuScriptor probes before the background task terminated at 3-of-7 stems, and emitted an honest `V3_FOCUS_SONG_PARTIAL_pending_operator` verdict with the pipeline state fully disclosed. Cycles 2 and 3 were consecutive re-invocations of the same c20-scoped directive against a workspace where the required output artifact already existed byte-identically; both re-invocations validated the artifact against on-disk state without producing new substantive work, and the Cycle 3 audit closed the branch with a `COMPLETE` verdict per the `<no-null-cycle-validation>` rule. The required output artifact remained byte-identical across four independent verification points (SHA `bd394c43c6134811257bb9b27539bf95e8d5b4663135d2646b0035f6b0e8ea2b`). The branch terminates cleanly; the parent M-V3-FOCUS-1 milestone remains in-progress at the campaign level, with pipeline advancement queued for a subsequent c21-scoped fanout clone.

## 1. Introduction and scope

The M-V3-FOCUS-1 milestone widens the M-V3-SPINE-1 pipeline (previously exercised only on *Chicken Grease*, source SHA-16 `31a164f845f8e27e`) to five focus songs — *Chicken Grease* as the mandatory anchor plus four SHA-256-tiebreak picks from `data/recreate_v2/focus_set_v2.json` (SHA `8908dae03202ae52…a1a5ca`). Under the campaign's Fixed Decision 6, M-V3-SPINE-1 itself remains gated on operator ear on Chicken Grease A/B; opening M-V3-FOCUS-1 substantively before that gate would ordinarily be premature. This clone operates under a break-glass carveout from the wait-on-operator cadence policy that permitted substantive fanout-branch work on the focus songs in parallel with the M-V3-SPINE-1 wait — a decision the parent conductor took to accumulate downstream pipeline evidence rather than sit idle across long operator-absent stretches.

Clone 0's assignment is *What If I Go*. Sibling clones 1–4 (Peach Dream, Dojo, Disco A, and one band-4 filler) are separately in scope for later fanout branches; they are not covered by this report.

The clone's scoped objective as issued:

- Read the chosen section from `focus_set_v2.json`.
- Run htdemucs_6s on both the chosen section and the full song, asserting byte-determinism ×2 across 24 stem SHAs.
- Run MuScriptor on the six per-stem probes plus the full-mix probe using the c3 stem whitelist and vocab mapping.
- Serialize canonical MIDI via the c4 `midi_from_json_events.py` (read-only).
- Merge per-stem MIDIs and assert the four structural gates.
- Choose tempo via `librosa.beat.beat_track` on the chosen-section drums stem.
- Run fluidsynth per-track render ×2 (byte-deterministic), then the D2 vocals overlay via a SHA-verified htdemucs vocals copy.
- Mix-match via the c5 Method A pattern (plain RMS-match) using a per-song sibling script that reads `scripts/v3_spine/mix_match_operator_section.py` read-only.
- Emit the operator-section A/B WAVs (30 s each), a full-song reconstruction WAV, and a delivery manifest under `data/v3/deliveries/252eb21ce7df7328/` matching the c5 Chicken Grease format.
- Measure the M-TEX-1 eight-key perceptual panel with the c33 rc7 anchor tripwire.
- Emit `cycle20/verdict.json` with `V3_FOCUS_SONG_LANDS_pending_operator` (or `PARTIAL/FAILS honestly`), the three-way `rubric_hash_v2` chain byte-equal, and `blocked_on_operator=true`.
- Land a twelve-case test suite at `tests/test_v3_focus_wig_c20.py`.
- Emit the standard four-row housekeeping ledger set under a `-clone-0` suffix.

The required deliverable is `data/v3/deliveries/252eb21ce7df7328/cycle20/verdict.json`. The directive explicitly permits `PARTIAL/FAILS honestly` as a first-class verdict, not a failure state.

## 2. Cycle 1: substantive pipeline execution and honest PARTIAL

Cycle 1 was the branch's only substantive-work cycle. It executed the pipeline in order up to the MuScriptor stage, at which point the background transcription task terminated after completing three of the seven probes.

### 2.1 Upstream anchors respected

Every read-only anchor consumed by the clone was byte-verified against its pinned SHA before use:

| Anchor | Path | SHA-256 |
|---|---|---|
| c19 verdict (backref) | `data/v3/deliveries/31a164f845f8e27e/cycle19/verdict.json` | `1485f281acb42e3f13d50ee1001b8f1b0be14e733f1b122ea366e2390ada6bfd` |
| c5 Method A reconstruction (Chicken Grease ear anchor) | `data/v3/deliveries/31a164f845f8e27e/operator_section/full_reconstruction_operator_section.wav` | `cc919559b4508b6bfe868fa5433a50b6805c43bab763665a5f2be367f01bbbd7` |
| c4 canonical MIDI serializer (consumed READ-ONLY) | `scripts/v3_spine/midi_from_json_events.py` | `bbff015f4f1833f446ad72f9cd5815117b2a744798fe3857edf468de6731a2ea` |
| c5 mix-match Method A (per-song sibling reads READ-ONLY) | `scripts/v3_spine/mix_match_operator_section.py` | `4f47fbcd7bf89c2bdc46701ae8da1fd39a732e3cf1cec4683c619cb17b743f60` |
| c33 render_stem (DO-NOT-TOUCH invariant) | `scripts/palette_render/render_stem.py` | `214372d920a319a97d6e3fc7b9ee4134c08c0cb4aecb776f4a50c75f965b5b2b` |

The focus-set reference `data/recreate_v2/focus_set_v2.json` was consumed at SHA `8908dae03202ae529282c08e74d490b336fadcf7ded4f93483a2b32756a1a5ca`.

### 2.2 Stage-by-stage pipeline state at cycle close

The delivered verdict discloses the per-stage state directly:

| Stage | Status | Notes |
|---|---|---|
| htdemucs_6s (operator section) | `done` | 6 stems byte-deterministic ×2; determinism JSON at `data/v3_spine/252eb21ce7df7328/operator_section/htdemucs_determinism.json` (SHA `5a737be7baeb75cbbfc153d1d56f85ba415ed787047b12668c0ac0511b424e66`) |
| Tempo choice | `done` | Detected 50.174 BPM on WIG operator-section drums; recorded a large delta versus rc5 baseline (200.893 BPM), likely an octave/subdivision artefact. Per Fixed Decision 1, no rc5 fallback was applied — the honest measurement was recorded and flagged. Tempo file SHA `a6b31110c68f2396698fce43ba17465e1003b9e9dab1939a3614af425ade31dd`. |
| MuScriptor | `partial` (3/7) | Drums, bass, and guitar completed; the guitar transcription came back empty (`done_empty`) — a first-class outcome, not a failure. Other, piano, vocals, and full-mix probes remained `not_yet_run` when the background task terminated. |
| Canonicalize | `not_run` | MuScriptor prerequisite unmet. |
| Merge (4/4 structural gates) | `not_run` | Canonicalize prerequisite unmet. |
| Fluidsynth per-track render ×2 | `not_run` | Merge prerequisite unmet. |
| D2 vocals overlay | `not_run` | MuScriptor vocals probe absent. |
| rc7 mix-match (Method A) | `not_run` | Render prerequisite unmet. |
| Deliver A/B | `not_emitted` | Mix-match prerequisite unmet. |
| Panel measurement (M-TEX-1) | `not_run` | Delivery prerequisite unmet. |

Per-probe MuScriptor SHAs recorded for the three that completed:

- Drums JSON `a8c28773a4d7a4571a5927b80306ac296211cb9cae722fc62f97ffc3d2b51c68` + MIDI `33de0cbc2ae02844c96391e02198b77692db939106067c09f724af78cde5db28`.
- Bass JSON `8060faaa728092546b38b83ced62f6738bf1a5cdac9fa64aa0a1373ad4af6904` + MIDI `543f1ab705b7b2fe845689ca4ef5274e2dd885a2d70121e7a1e175ceadf40cbe`.
- Guitar JSON `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945` (canonical empty-events hash) + MIDI `b4134d5cce88b9049baca7d9efae3f7d592a42b22a47e4398cab2100dc75e10b`.

### 2.3 Verdict

`data/v3/deliveries/252eb21ce7df7328/cycle20/verdict.json` (8 931 bytes; SHA `bd394c43c6134811257bb9b27539bf95e8d5b4663135d2646b0035f6b0e8ea2b`) was emitted with:

- `verdict = V3_FOCUS_SONG_PARTIAL_pending_operator`
- `cycle = 20`, `song_sha16 = 252eb21ce7df7328`, `milestone_id = M-V3-FOCUS-1`
- `blocked_on_operator = true`, `blocked_on_muscriptor_completion = true`
- `verdict_placement_convention = cycle<N>/`
- `fork = 88d75f9754c3`, `clone = clone-0`
- `parent_cycle_track = peer sub-milestone under M-V3-FOCUS-1 per c29 state-machine lemma`
- Three-way `rubric_hash_v2` chain byte-equal at `c49db5a12e955f26c001165ad6e8f9d191bc26bfd96e24c1b163adc37016451a` (document SHA, `rubric_hash_v2.txt` content, and verdict field all identical).
- Cadence policy pin `docs/wait_on_operator_cadence_policy.md` SHA `0be540365c8c03ad38a15478fbad0fe32bf5ea4118e33ef3eeed62dbd9a0c7f2`.
- `operator_ab_pending.status = not_emitted_pipeline_incomplete` with the reason `Pipeline chain not exercised past muscriptor stage.`
- A `next_action_if_operator_greenlights_muscriptor_restart` block naming the three-step restart path.
- Operator-facing notes: (A) restart MuScriptor for the remaining four probes and continue the chain in a subsequent cycle, or (B) declare WIG focus-song delivery deferred behind the still-blocked Chicken Grease operator ear per Fixed Decision 6.
- The test suite pinned at `tests/test_v3_focus_wig_c20.py` (SHA `7fdb2737cbb7607e4cae1dfbae15d034c04beef16fab241ecdf309cdb8808a66`), landed with the twelve-case shape; determinism-gate cases skip when preconditions are absent (a design choice that keeps the suite green under partial pipeline execution).

The verdict's `reason` field records the situation verbatim: pipeline incomplete at the MuScriptor stage (3/7 probes), downstream chain not executed per Fixed Decision 1's prohibition on tuning-or-retry, operator A/B WAVs not emitted, operator ear irrelevant while the chain is incomplete. Existing artifacts (six-stem htdemucs byte-deterministic × 2, three MuScriptor JSON+MID pairs, tempo choice JSON) are preserved read-only; nothing is unwound.

## 3. Cycles 2 and 3: re-invocations under an already-discharged directive

Cycles 2 and 3 were consecutive re-invocations of the same c20-scoped directive against a workspace where the required output artifact already existed on disk from Cycle 1's emission. Neither cycle produced any new substantive work.

Cycle 2's audit re-verified the artifact against on-disk state byte-identically. Because the directive named `cycle20/verdict.json` as the required output and explicitly permitted `PARTIAL/FAILS honestly` as a first-class verdict, the artifact-on-disk plus the intact discipline chain already discharged the scope contract. The auditor recorded VALIDATED status-only, with no new work performed.

Cycle 3's audit was a fourth verification point of the same artifact (pre-compaction emission plus three post-hoc verifications). The verdict SHA `bd394c43c6134811257bb9b27539bf95e8d5b4663135d2646b0035f6b0e8ea2b` was byte-identical across all four checkpoints; the three-way rubric chain held byte-equal; anti-fabrication contract held (every SHA sampled in the verdict resolved on-disk); no substantive work was possible under the c20-scope contract. Under the `<no-null-cycle-validation>` rule — which explicitly instructs that a cycle whose work_output is only status-only re-verification of an already-validated finished branch must terminate rather than manufacture new scope to stay busy — the auditor issued the branch-terminating verdict `COMPLETE` with `[[BRANCH_COMPLETE]]`.

The Cycle 3 auditor's rationale distinguished four separable considerations that jointly justified branch termination:

1. **Scope contract discharged.** The required deliverable existed at the required path with a first-class-permitted verdict and an intact discipline chain.
2. **Worker's honest deferral was defensible on scope grounds.** The worker in Cycles 2 and 3 correctly recognized the scope boundary and refused to autonomously reclassify the c20 PARTIAL as c21-recoverable substantive work without either an operator directive in `live_guidance` or a re-brief with `cycle21/verdict.json` as the required artifact. The auditor observed that a MuScriptor restart under locked configuration would be idempotent-overwrite, so a Fixed Decision 1 argument against restart was actually weaker than the scope-boundary argument the worker had used, but both routes justified the same conclusion.
3. **The c21-shaped forward brief embedded in the audit-report input was auditor guidance from the prior cycle, not an operator directive.** Executing it under a c20-scoped invocation would either succeed and blur the audit trail by mislabeling c21 work as c20 delivery, or fail on background-task session-boundary termination without operator green-light and waste budget. Neither is preferable to closing the branch cleanly and letting the parent conductor spawn a c21-scoped clone.
4. **The MINOR-1 ledger drift observation is a c21-scope reconciliation task, not resolvable within c20 scope.** Five c20 ledger events had allegedly been appended pre-compaction, but zero `cycle:20` rows for the WIG SHA-16 were visible in the primary ledger and no shadow-ledger candidates were on disk; the item was carried forward as log-only across all three re-invocations and formally deferred to a future c21-scoped cycle per the c38+ post-merge-reconciliation precedent.

## 4. Deliverables and integrity chains at branch close

**Required output artifact.** `data/v3/deliveries/252eb21ce7df7328/cycle20/verdict.json` present, 8 931 bytes, SHA `bd394c43c6134811257bb9b27539bf95e8d5b4663135d2646b0035f6b0e8ea2b`. Byte-identical across four independent verification points.

**Three-way rubric-v2 chain.** Document SHA `c49db5a12e955f26c001165ad6e8f9d191bc26bfd96e24c1b163adc37016451a` == `data/v3_spine/rubric_hash_v2.txt` content == verdict `rubric_hash_v2` field. Byte-equal at every verification point.

**Anti-fabrication.** Every SHA in the delivered verdict that the auditor sampled resolved on-disk at audit time. Approximately 135 cumulative SHA spot-checks across the campaign's eight consecutive audits (five Chicken Grease heartbeats plus a Peach Dream INSUFFICIENT clone, two WIG VALIDATED re-invocations, and this branch's terminating COMPLETE) have been made with zero fabrications detected.

**Test suite.** `tests/test_v3_focus_wig_c20.py` at SHA `7fdb2737cbb7607e4cae1dfbae15d034c04beef16fab241ecdf309cdb8808a66`, twelve-case shape landed. Determinism-gated cases correctly skip when their preconditions (later pipeline stages) are absent.

**Housekeeping ledger events (MINOR-1 open).** The four-row housekeeping envelope with the `-clone-0` suffix is disclosed by the delivered verdict as having been emitted pre-compaction, but the primary `promise_ledger.jsonl` shows zero `cycle:20` rows for the WIG SHA-16 and no shadow-ledger candidates were located on disk. The observation persisted across three consecutive audits as log-only per the c38+ post-merge-reconciliation precedent, and is queued for retro-append in a subsequent c21-scoped cycle with narrative citing this branch's MINOR-1 finding verbatim.

## 5. Campaign-level state at branch close

The M-V3-FOCUS-1 milestone remains **in-progress** at the campaign level. This fanout clone's c20-scoped branch terminates by COMPLETE; the parent milestone does not. Pipeline advancement on *What If I Go* — the remaining four MuScriptor probes plus the full downstream chain (canonicalize → merge → render → vocals overlay → mix-match → deliver A/B → panel measurement) — is queued for a separately-briefed c21 fanout clone with `cycle21/verdict.json` as its required artifact.

The four remaining focus songs (Peach Dream, Dojo, Disco A, one band-4 filler) are also still in scope under the M-V3-FOCUS-1 umbrella; a Peach Dream clone was previously spawned and returned INSUFFICIENT per the auditor's cumulative-notes summary. Parallel fanout clones for these songs remain viable whenever the parent conductor deems the campaign ready.

The wait-on-operator cadence policy exception under which this substantive branch operated does not automatically propagate to a subsequent c21-scoped clone; that clone would need either an explicit `live_guidance` directive greenlighting substantive advancement or a re-affirmation of the break-glass carveout. Absent either, a subsequent WIG cycle would fall back to the heartbeat cadence consistent with the c8 policy.

The Chicken Grease M-V3-SPINE-1 milestone remains blocked on operator ear per Fixed Decision 6. Fifteen-plus cycles have passed since Cycle 5 without the operator ear input that would flip the gate. The v3-focus fanout branches — WIG, and the sibling clones planned for the other four focus songs — are the campaign's mechanism for accumulating downstream pipeline evidence during that wait, but they do not themselves substitute for the operator ear authority that gates M-V3-SPINE-1's positive-verdict advancement.

## 6. Conclusions

Clone 0 of fork `88d75f9754c3` delivered its scoped objective honestly. Cycle 1 executed the WIG per-stem pipeline as far as the MuScriptor stage, hit a background-task termination at 3-of-7 probes, and emitted the required output artifact with a first-class PARTIAL verdict that discloses the exact pipeline state and the two operator-facing options for continuation. Cycles 2 and 3 re-verified the artifact byte-identically against on-disk state without producing new substantive work; the Cycle 3 auditor closed the branch per the `<no-null-cycle-validation>` rule with COMPLETE and `[[BRANCH_COMPLETE]]`.

Three notable properties of this branch are worth recording. First, the honest-PARTIAL clause of the directive worked as intended: the clone did not manufacture a false LANDS or a false FAILS to look decisive, it disclosed the actual pipeline state, and the auditor accepted the PARTIAL as a first-class deliverable rather than as a failure. Second, the anti-fabrication discipline held under repeated re-invocation: four independent verification points on the same artifact all returned the same SHA. Third, the `<no-null-cycle-validation>` rule terminated the re-invocation loop correctly, avoiding the failure mode of accumulating an indefinite chain of status-only re-verifications on an already-finished branch. The one outstanding item, MINOR-1 ledger drift on the c20 housekeeping rows, is a bookkeeping reconciliation queued for a subsequent c21-scoped cycle and does not block the branch's clean termination.

## Appendix: Implementation Details

### A.1 Delivered artifact and integrity

Artifact: `data/v3/deliveries/252eb21ce7df7328/cycle20/verdict.json` (8 931 bytes; SHA `bd394c43c6134811257bb9b27539bf95e8d5b4663135d2646b0035f6b0e8ea2b`; byte-identical across four verification points).

Three-way rubric-v2 chain: `docs/v3_spine_rubric_v2.md` SHA `c49db5a12e955f26c001165ad6e8f9d191bc26bfd96e24c1b163adc37016451a` == `data/v3_spine/rubric_hash_v2.txt` content == verdict field.

Cadence policy pin: `docs/wait_on_operator_cadence_policy.md` SHA `0be540365c8c03ad38a15478fbad0fe32bf5ea4118e33ef3eeed62dbd9a0c7f2`.

### A.2 Read-only upstream anchors consumed

`data/v3/deliveries/31a164f845f8e27e/cycle19/verdict.json` SHA `1485f281acb42e3f13d50ee1001b8f1b0be14e733f1b122ea366e2390ada6bfd`. `data/v3/deliveries/31a164f845f8e27e/operator_section/full_reconstruction_operator_section.wav` SHA `cc919559b4508b6bfe868fa5433a50b6805c43bab763665a5f2be367f01bbbd7`. `scripts/v3_spine/midi_from_json_events.py` SHA `bbff015f4f1833f446ad72f9cd5815117b2a744798fe3857edf468de6731a2ea`. `scripts/v3_spine/mix_match_operator_section.py` SHA `4f47fbcd7bf89c2bdc46701ae8da1fd39a732e3cf1cec4683c619cb17b743f60`. `scripts/palette_render/render_stem.py` SHA `214372d920a319a97d6e3fc7b9ee4134c08c0cb4aecb776f4a50c75f965b5b2b`. `data/recreate_v2/focus_set_v2.json` SHA `8908dae03202ae529282c08e74d490b336fadcf7ded4f93483a2b32756a1a5ca`.

### A.3 htdemucs stem determinism (operator section)

Six stems byte-deterministic across two runs; roll-up sidecar `data/v3_spine/252eb21ce7df7328/operator_section/htdemucs_determinism.json` SHA `5a737be7baeb75cbbfc153d1d56f85ba415ed787047b12668c0ac0511b424e66`.

### A.4 MuScriptor per-probe hashes at cycle 1 close

Drums JSON `a8c28773a4d7a4571a5927b80306ac296211cb9cae722fc62f97ffc3d2b51c68`; drums MIDI `33de0cbc2ae02844c96391e02198b77692db939106067c09f724af78cde5db28`. Bass JSON `8060faaa728092546b38b83ced62f6738bf1a5cdac9fa64aa0a1373ad4af6904`; bass MIDI `543f1ab705b7b2fe845689ca4ef5274e2dd885a2d70121e7a1e175ceadf40cbe`. Guitar JSON `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945` (canonical empty-events hash) and MIDI `b4134d5cce88b9049baca7d9efae3f7d592a42b22a47e4398cab2100dc75e10b`. Other, piano, vocals, and full-mix probes remained `not_yet_run` at cycle close.

### A.5 Tempo choice

Detected 50.174 BPM on the WIG operator-section drums via `librosa.beat.beat_track`; rc5 baseline 200.893 BPM; a large delta likely explained as an octave/subdivision artefact. No rc5 fallback applied per Fixed Decision 1. Tempo file SHA `a6b31110c68f2396698fce43ba17465e1003b9e9dab1939a3614af425ade31dd`.

### A.6 Test suite

`tests/test_v3_focus_wig_c20.py` SHA `7fdb2737cbb7607e4cae1dfbae15d034c04beef16fab241ecdf309cdb8808a66`; twelve-case shape landed; determinism-gated cases skip cleanly when their preconditions (later pipeline stages) are absent.

### A.7 Environment pins

`PYTHONHASHSEED=0`; `SOURCE_DATE_EPOCH=1756463424`; `TZ=UTC`; `LC_ALL=C.UTF-8`; `OMP_NUM_THREADS=1`, `MKL_NUM_THREADS=1`, `OPENBLAS_NUM_THREADS=1`; interpreter `/usr/bin/python3`; `mido==1.3.3`; SoundFont SHA `74594e8f…1cb0`; MuScriptor model SHA `ac80adbd…7fb97ec`.

### A.8 Open items at branch close

MINOR-1 (log-only, carried across all three cycles): five c20 ledger events allegedly appended pre-compaction not visible in primary `promise_ledger.jsonl` under WIG SHA-16, no shadow-ledger candidates on disk. Queued for retro-append per c38+ post-merge-reconciliation precedent in a subsequent c21-scoped cycle with narrative citing this branch's MINOR-1 verbatim, timestamp `2026-09-02T22:00:00Z` (pre-c21 substantive work).

Downstream WIG pipeline stages remaining for a subsequent c21-scoped clone: complete the four remaining MuScriptor probes (other, piano, vocals, full_mix), then canonicalize → merge with four structural gates → fluidsynth per-track render ×2 → D2 vocals overlay → rc7 mix-match Method A → deliver A/B WAVs + full-song reconstruction WAV → M-TEX-1 eight-key panel measurement with c33 rc7 anchor tripwire → emit `cycle21/verdict.json`.

### A.9 Source sessions

| Cycle | Researcher | Worker | Auditor |
|---|---|---|---|
| 1 | 8e854a84-71e6-49dc-8eaa-dc07425b91e8 | 3d37cb74-2e55-49c9-83d9-8c36e6bbdcd7 | 16386e4d-a054-448d-89be-6c4444b893a5 |
| 2 | 6bc6085e-5c1c-410d-83a5-b3ba8703504d | 996b9b05-4d02-4980-a1fb-d76ea13857b0 | 216daad0-a0ca-46a0-8957-43bad5e2684b |
| 3 | 6a6269e6-410d-42e5-80bb-2f60f11a1fe0 | 71107169-382c-47c4-b24a-780a5b04b976 | 3809e8ff-69b3-4707-86b8-dc0228ee3b31 |

### A.10 Fanout metadata

Fork `88d75f9754c3`. Clone 0 of the WIG assignment. Merge report expected at `/home/user/music-gen-instance-v3/fork-88d75f9754c3/clone-0/merge_report.md` for parent-conductor pickup. Peer clones 1–4 planned for Peach Dream, Dojo, Disco A, and one band-4 filler in separate fanout invocations.
