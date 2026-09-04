# Music-Gen v4 closure campaign — MANIFEST

Snapshot at cycle-15 close. Scope: files produced or extended during
cycles 1–15 of the v4 closure campaign. As of cycle 15 all five
Chicken Grease instrument cells reach a terminal state: bass accepted
under the cycle-9 hybrid rule; drums, guitar refused-showcase (OPT3)
under agent-picks selection invariants; piano and other-residual
grounded as `NULL_MIDI_EMPTY_REFERENCE_INAUDIBLE`; vocals covered by
the hybrid-overlay policy. `deliver_cg_ab_v4.py --smoke-test`
reports `n_missing = 0` — the CG A/B render is now realizable end to
end. Prior v3-arc anchors are read-only and are not re-inventoried
here; the cycles reports §A.1 and §A.4 list them explicitly.

## Scripts (cycles 1–3 delta)

### `scripts/sound_match/`

| file | purpose |
|---|---|
| `coarse_sweep_sf2.py` | cycle-1: 15-preset General-MIDI SoundFont coarse sweep |
| `fine_fit_sf2.py` | cycle-2: 180-cell fine-fit v1 (READ-ONLY after cycle 3) |
| `fine_fit_sf2_v2.py` | cycle-3: 216-cell fine-fit v2 (LUFS-normalised, program-33 unconditionally promoted) |
| `stage2_zscore_diagnostic.py` | cycle-2 diagnostic |
| `stage2b_zscore_diagnostic.py` | cycle-3 diagnostic (v2 leaderboard) |
| `profile_writer.py` | extended additively cycle 3: `loudness_method`, `measured_db`, `applied_gain_lin`, `pyloudnorm_available`, `lufs_target_db`; cycle-2 profile SHA `11747a42cb1a8f7f…` reproduces byte-identically under extended signature |
| `_launch_cg_bass_sweep_c1.sh` | detached launcher, cycle 1 |
| `_launch_cg_bass_stage2_c2.sh` | detached launcher, cycle 2 |
| `_launch_cg_bass_stage2b_c3.sh` | detached launcher, cycle 3 |

Cycles 4–6 delta in `scripts/sound_match/`:

| file | cycle | purpose |
|---|---|---|
| `emit_bass_v2_and_replay_proof.py` | 4 | emits `bass_v2.json` (program 33 pin) + replay proof |
| `family_verdict_cg_bass.py` | 4 | runs pre-registered decision protocol on stage-2b leaderboard → `bass_family_verdict.json` |
| `family2_stem_sampled_spike.py` | 5 | family-2 shape probe, SHA `000c3ef68042f2da…6329e80` (byte-identical pre==post cycle 6) |
| `family2_stem_sampled_builder.py` | 6 | shipped stem-sampled builder promoted from cycle-5 spike |
| `replay_family2.py` | 6 | family-2 replay dispatch (sibling to `replay.py`) |
| `replay.py` | 6 patched in place | L79–93 replay-program-invariance fix; SHA moves `e03dad60…` → `419d9558747eec61e58b3450b9f57b9bd057a7f8d7a31dfd1ab02f4d63c9f545` |

Cycles 7–9 delta in `scripts/sound_match/`:

| file | cycle | purpose |
|---|---|---|
| `coarse_sweep_sf2_drums.py` | 9, patched 10 | drums coarse-sweep sibling (446 lines); dry-run PASS at cycle 9, `_disk_ok()` patched to absolute-budget check at cycle 10, launched detached under canonical env-pin |
| `deliver_cg_ab_v4.py` | 9 | Chicken Grease A/B render scaffold (5402 B); smoke test only, no render (`n_missing = 4`) |

Cycles 10–12 delta in `scripts/sound_match/`:

| file | cycle | purpose |
|---|---|---|
| `_launch_cg_drums_sweep_c10.sh` | 10 | detached launcher for the cycle-10 drums coarse sweep |
| `fine_fit_sf2_drums.py` | 11 | 216-cell drums fine-fit (679 lines); channel-10 aware, LUFS-normalised, drums-family sibling to `fine_fit_sf2_v2.py` |
| `_launch_cg_drums_stage2_c11.sh` | 11 | detached launcher for the cycle-11 drums stage-2 fine-fit |
| `replay.py` | 11 patched in place | channel-aware `_replay_sf2` extension (L79–93); bass regression byte-identical (`832868d0…`) since bass MIDI is channel-0 only; drums-channel-10 render becomes replayable (`dadafcfc…64b8d7c`). Post-patch SHA `1f43027039c45f5e066c…` |
| `family2_stem_sampled_drums_spike.py` | 12 | family-2 drums shape probe (144 lines); band-energy onset classifier; spike verdict `VIABLE` |
| `family2_stem_sampled_drums_builder.py` | 12 | family-2 drums builder (271 lines); MIDI-pitch → sample-class dispatch (kick p36, snare p38, hihat p42/44/46) |
| `_family2_drums_score_and_emit_c12.py` | 12 | scoring + `drums_family2_v1.json` + replay-proof + verdict emitter |
| `_family2_drums_closeout_and_escalation_c12.py` | 12 | arc-closeout + manager-escalation emitter |
| `_replay_regression_c12.py` | 12 | independent Track-1 replay-regression harness (bass_v2 + drums), two runs into fresh tempdirs, from-fresh-subprocess |
| `_emit_c12_ledger_events.py` | 12 | ledger-event emitter for the cycle-12 milestone slate |

Cycle-1 anchor `coarse_sweep_sf2.py` (SHA `c74c35bc…`) verified byte-identical through cycle 12.

Other files in `scripts/sound_match/` (`objective.py`,
`replay_proof.py`, `deliver_ab.py`) are prior-arc anchors used
unchanged through cycle 9.

## Tests (cycles 1–3 delta)

| file | test count | verified |
|---|---|---|
| `tests/test_sound_match_fine_fit_sf2.py` | 8 | cycle-2 (subsumed by v2) |
| `tests/test_sound_match_fine_fit_sf2_v2.py` | 14 | cycle-3, 14/14 pass |
| `tests/test_sound_match_profile_writer_v2.py` | 5 | cycle-3 auditor re-run, 5/5 pass; asserts byte-identical replay of cycle-2 profile SHA `11747a42cb1a8f7f…` under extended writer signature |

Test totals for v2 suites at cycle-3 close: 19 of 19 passing.

Cycles 10–12 test delta:

| file | cycle | purpose |
|---|---|---|
| `tests/test_coarse_sweep_disk_check.py` | 10 | pins the absolute-budget `_disk_ok()` formula and asserts the c9 false-positive regression |
| `tests/test_rc10_drums_bass.py` | 10 | drums+bass regression cross-check under channel-aware replay |
| `tests/test_rc10_drums_v2.py` | 10 | drums-family stage-2 leaderboard structural test |
| `tests/test_verdict_sha_fields_resolve_on_disk.py` | 12 | asserts every SHA field embedded in a verdict/manifest resolves to a byte-identical on-disk artefact |

## Data artefacts (cycles 1–3)

- `data/v4/profiles/31a164f845f8e27e/bass_sweep_stage1/leaderboard.tsv` — coarse sweep, SHA `0623210a19de0c96…`
- `data/v4/profiles/31a164f845f8e27e/bass_stage2/leaderboard.tsv` — fine-fit v1, SHA `47aa8b0aca52ac85…`
- `data/v4/profiles/31a164f845f8e27e/bass_stage2b/leaderboard.tsv` — fine-fit v2, 216 rows, 215 distinct render SHAs, 36 program-33 rows
- `data/v4/profiles/31a164f845f8e27e/bass.json` — cycle-2 pinned profile, UUID `56cdc50a-dbbc-5a49-afc9-f3cf93a25c7d`, SHA `11747a42cb1a8f7f…`
- `data/v4/profiles/31a164f845f8e27e/bass.replay_proof.json` — cycle-2 SoundFont-family replay proof, verdict `REPLAY_PROOF_HOLDS`, SHA `832868d0…`, under env-pin `2ac444c36298d6ad…`
- `data/v4/logs/cg_bass_stage2b_c3.log` — cycle-3 detached-run log (PID 17998)

Cycles 4–6 data-artefact delta under `data/v4/profiles/31a164f845f8e27e/`:

| file | cycle | notes |
|---|---|---|
| `bass_family_verdict.json` | 4 | `STILL_INDETERMINATE`; top-1 by composite = prog 33, top-1 by embedding = prog 19 (0.4946); neither reaches 0.60 CONFIRMED threshold |
| `bass_v2.json` | 4 | `d62cd3b6-4521-5d4f-b840-87ef7800c48d`, prog 33 Electric Bass Finger, gain 0.5, reverb 0.3, `post=EQ_only`; profile SHA `2a1cb340bffd11016c566467b0d313fb002c5949ce881968702846867e090462` |
| `bass_v2.replay_proof.json` | 4, refreshed 6 | run1 = run2 = `832868d0ea8a81cab2569e60445f80d516d1b5bb958b1b8b0c2e996bdb3aeac5`; unchanged after fix (expected — `bass.mid` already embeds `program_change 33`) |
| `bass.replay_proof.json` | refreshed 6 | run1 = run2 = `c69775040c325b865be029316d5ccbaff6b3d2393b238c877bae3f1b74ff019c`; **changed** from pre-fix `832868d0…` — audio-bytes evidence the fix took effect |
| `replay_fix_verdict.json` | 6 | `REPLAY_FIX_LANDS`, A/B/C = pass/pass/pass, cross-proof-differ = true, rubric hash `a9497ed585f9a8807ec0addb2d695b8b411eb60418c7bc3946663ce71c4178ef` |
| `replay_fix_test_matrix.json` | 6 | three-test regression matrix (negative inversion, positive determinism, existing-MIDI neutrality) |
| `bass_family2_v1.json` | 6 | `1f3c104a-2cc4-5e25-a802-d1360f1336ee`, `render_family = stem_sampled_v1`, canonical replay SHA `9b4647cef61fe9d6…523276` |
| `bass_family2_v1.replay_proof.json` | 6 | run1 = run2 = `9b4647cef61fe9d6…523276` |
| `bass_family2_verdict.json` | 6 | **`FAMILY2_RULED_OUT`**, `embedding_cos_vggish = 0.0896`, delta vs sf2 top-1 = −0.405, rubric hash `2dddc32a…91dfe` |
| `anchor_preservation_pre_c6.json`, `anchor_preservation_post_c6.json` | 6 | `all_match = true, n_mismatch = 0` on 4 anchors + cycle-5 spike script |
| `pre_c6_fix/` | 6 | archived pre-fix replay proofs (932 B + 892 B) |
| `replay_c6_post_fix_sha.txt`, `replay_fix_c6_rubric_hash.txt`, `family2_builder_c6_rubric_hash.txt` | 6 | fingerprint + three-way rubric-hash chain anchors |

Cycles 7–9 data-artefact delta:

| file | cycle | notes |
|---|---|---|
| `data/v4/profiles/31a164f845f8e27e/bass_arc_closeout.json` | 7 | verdict `CG_BASS_ARC_EXHAUSTED_NO_CONFIRMED`; both frozen families exhausted; rubric hash `544a399569b8d2e9…` |
| `data/v4/profiles/31a164f845f8e27e/operator_directive_c7.json` | 7 | `operator_directive_present = false` |
| `data/v4/profiles/31a164f845f8e27e/closeout_c7_rubric_hash.txt` | 7 | three-way chain anchor |
| `data/v4/profiles/31a164f845f8e27e/anchor_preservation_pre_c7.json` + `_post_c7.json` | 7 | anchor coverage |
| `data/v4/profiles/31a164f845f8e27e/operator_directive_c8.json` | 8 | `heartbeat_streak = 1`; single-shot wait-on-operator cycle |
| `data/v4/profiles/31a164f845f8e27e/c7_readonly_reverify_c8.json` | 8 | 6/6 cycle-7 deliverables byte-identical |
| `data/v4/profiles/31a164f845f8e27e/anchor_liveness_c8.json` + `_rubric_hash.txt` | 8 | 9/9 anchors match |
| `data/v4/deliveries/31a164f845f8e27e/cg_bass_pinned_profile.json` | 9 | operator OPT1+OPT3 hybrid pin of `bass_v2.json` as Chicken Grease bass profile of record; SHA `aa9b36be3f2e6748…`; carries acceptance-fork + honest-embedding-cos disclosure |
| `data/v4/deliveries/31a164f845f8e27e/scaffold_smoke_test.json` | 9 | A/B driver smoke test; `renderable_now = false`, `n_missing = 4` (drums, piano, guitar, other) |
| `data/v4/profiles/31a164f845f8e27e/anchor_preservation_pre_c9.json` + `_post_c9.json` | 9 | 11/11 anchors match |
| `data/v4/profiles/31a164f845f8e27e/c9_rubric_hash.txt` | 9 | `96e09627056412ad5af4c9f892b2f918d52e8c22bbf090bb6623861ae56fd58d` |
| `data/v4/profiles/31a164f845f8e27e/drums_sweep_stage1/` | 9 | placeholder tree awaiting cycle-10 sweep |
| `docs/sound_match/c9_operator_directive_operationalization_rubric.md` | 9 | 5769 B, SHA `96e09627…` |
| `plan_of_record.md` tail-append blocks (3) | 9 | operator directive verbatim, cycle-7 escalation supersede, heartbeat retirement |

## Environment pins in force across cycles 1–3

| pin | scope |
|---|---|
| `623df01f262ffd180c8497ce9bb06a2d4438b9239d60dd997304830b6571d38d` | v3 spine driver session; determinism certificate anchors here |
| `2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca` | cycle-2 fine-fit v1; cycle-2 cg-bass profile + replay proof anchor here |
| `d606c8bc0ebfd38bf64ce588e2b133f4a954556d3c5c92d257fd3b582bfb0aa9` | cycle-3 fine-fit v2 sweep-time 9-key pin (adds `pyloudnorm_available` + `lufs_target_db`); preserved as diagnostic manifest per `_plan/env-pin-schema-unified-c6`, not merged into replay hash |
| `2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca` | canonical replay-time 7-key env-pin, unified across every cycle-6 proof/verdict; closes cycle-4 replay-side pin drift on the replay surface |

## Fixed anchors (unchanged, read-only)

- `FluidR3_GM.sf2` — SHA `74594e8f4250680adf590507a306655a299935343583256f3b722c48a1bc1cb0`
- Reference bass stem — SHA `1bad871901294395c1b1ad1c97689e07d879f48aa8b9fc953ea6981d76e09ffd`
- Bass MIDI excerpt — SHA `4863ca285c7db513c8bfc22da5e35e65036b0ecad2538a6d9794c80eb15f8ac9`
- `scripts/palette_render/render_stem.py` — SHA `214372d920a319a9…5b2b`
- Chicken Grease Method A operator-blessed WAV — SHA `cc919559b4508b6bfe86…`

## Cross-references between artefacts

- cycle-1 coarse top-5 → cycle-2 fine-fit grid
- cycle-2 top-1 (program 17 Drawbar Organ, gain 0.5, reverb 0.3, no post-processing) → cycle-2 pinned profile `56cdc50a-…` → cycle-2 replay proof `832868d0…`
- cycle-2 MODERATE findings (EQ inertness, program-33 absence, profile-writer additive extension) → cycle-3 architectural fixes in `fine_fit_sf2_v2.py` + additive fields in `profile_writer.py` → cycle-3 regression byte-identity re-verification of cycle-2 profile SHA under extended writer signature
- cycle-3 v2 216-cell sweep → cycle-3 stage-2b leaderboard → cycle-4 family-verdict emission (open; verdict currently reads `STILL_INDETERMINATE` per pre-registered decision protocol)

## Cumulative stats (cycles 1–6)

- New scripts: 6 (cycles 1–3) + 5 (cycles 4–6) + 1 in-place patch (`replay.py` at cycle 6).
- New tests: 3 files, 27 test functions across cycles 1–3, plus the cycle-6 A/B/C regression matrix in `replay_fix_test_matrix.json`.
- New leaderboards: 3 (coarse, fine-fit v1, stage-2b v2).
- Pinned profiles: 3 (`bass.json` cycle 2, `bass_v2.json` cycle 4, `bass_family2_v1.json` cycle 6).
- Replay proofs: 3, refreshed at cycle 6 to the unified canonical env-pin (`bass`, `bass_v2`, `bass_family2_v1`).
- Family verdicts: 2 — sf2 `STILL_INDETERMINATE` (cycle 4, READ-ONLY thereafter), family-2 `FAMILY2_RULED_OUT` (cycle 6).
- Foundational unblock: the cycle-6 `replay.py` L79–93 fix converts the SoundFont render family from "cannot ship replay proofs" to "can ship replay proofs on every song and instrument" for the remaining 24 profile cells.

Cycles 10–12 data-artefact delta under `data/v4/profiles/31a164f845f8e27e/`:

| file | cycle | notes |
|---|---|---|
| `drums_sweep_stage1/leaderboard.tsv` | 10 | 15-preset drums coarse-sweep leaderboard, SHA `dd5544d3bd3a549cab95…` |
| `drums_sweep_stage1/drums_excerpt.mid` | 10 | drums MIDI (channel 10, 186 note-on events), SHA `0fd71ce70a26365c2acf…` |
| `drums_sweep_stage2/leaderboard.tsv` | 11 | 216-cell drums stage-2 leaderboard, SHA `81a441732f7f7d1da615…`, spread 176.7% |
| `drums.json` | 11 | drums profile, UUID `83728154-6f48-5c5d-a558-b4d82523ac1b`, program 16 Power Kit, gain 1.0, reverb 0.7, `post=EQ_only`, `embedding_cos_vggish = 0.2374`, canonical replay SHA `dadafcfc…64b8d7c` |
| `drums.replay_proof.json` | 11 | run1 = run2 = `dadafcfc0153f002651c23975c3845dd3f8ca7896d263faf1c52eb54d64b8d7c`; embeds `bass_regression_check` PASS proving the c11 channel-aware `_replay_sf2` extension leaves bass byte-identity intact |
| `drums_family_verdict.json` | 11 | **`SF2_RULED_OUT`**, `top1_embedding_cos_vggish = 0.2374 ≤ 0.40`; `max_embedding_cos_across_216_cells = 0.4645` (program 48 Orchestra Kit, composite rank 76) |
| `drums_family2_spike_c12.json` | 12 | family-2 shape-probe verdict `VIABLE`; 147 onsets, class distribution kick 93 / snare 0 / hihat 53 |
| `drums_family2_v1.json` | 12 | family-2 profile, UUID `13aeeea0-934e-5b4c-9a7a-e69e1c0e5fc4`, canonical replay SHA `69a76c5b4498972d1cb878da94e645c8c341675b113cc4ca315435f6bb16ca00` |
| `drums_family2.replay_proof.json` | 12 | run1 = run2 = `69a76c5b…16ca00`; per FD-16(c) this covers the family-2 code path for all future CG drums profiles |
| `drums_family2_render/render.wav` | 12 | family-2 concatenative render, 2 678 664 B, SHA `69a76c5b…` |
| `drums_family2_verdict.json` | 12 | **`FAMILY2_RULED_OUT`**, `embedding_cos_vggish = 0.0372`; composite 618.16, mel_l1 13.41 dB, spectral-centroid RMSE 2442 Hz |
| `drums_arc_closeout.json` | 12 | verdict `CG_DRUMS_ARC_EXHAUSTED_NO_CONFIRMED`; parallels `bass_arc_closeout.json` shape; carries `cross_song_parallel_findings` + `systematic_finding` blocks |
| `_manager_M-V4-SHOWCASE-1-cg-drums-acceptance-policy.json` | 12 | `action_required = true`, `authority = OPERATOR`, three named options (OPT1 composite-relative WINNER extension of the bass_v2 precedent; OPT2 embedding-first tiebreak to program 48 Orchestra Kit; OPT3 refuse drums showcase and deliver A/B without drums recreation); `unilateral_action_taken_this_cycle = NONE` |
| `_replay_regression_c12.json` | 12 | independent from-fresh-subprocess Track-1 verdict `REPLAY_REGRESSION_HOLDS`; bass_v2 and drums anchors both byte-identical run1 = run2 = anchor; discloses a brief-vs-on-disk drums-anchor tail discrepancy caught in-cycle |
| `_c12_track3_summary.json`, `_c12_track4_summary.json` | 12 | per-track sub-milestone summaries |

## Downstream state at cycle-12 close

- cg-bass arc closed under operator OPT1+OPT3 hybrid acceptance; `bass_v2.json` (program 33, embedding-cosine 0.4946) is the pinned Chicken Grease bass profile. The 0.60 CONFIRMED threshold is retired for this one acceptance; the 0.40 RULED_OUT floor is retained for future family verdicts.
- cg-drums arc fully closed at cycle 12 as `CG_DRUMS_ARC_EXHAUSTED_NO_CONFIRMED`. Both frozen render families are ruled out: SoundFont top-1 (Power Kit, embedding-cosine 0.2374) and family-2 stem-sampled (embedding-cosine 0.0372) both sit below the 0.40 retained honesty floor. A three-option acceptance policy has been escalated to operator authority in `_manager_M-V4-SHOWCASE-1-cg-drums-acceptance-policy.json`; no unilateral OPT1 extension was taken because the c9 threshold retirement is scoped to Chicken Grease bass only.
- The cycle-11 `replay.py` channel-aware fix has been independently re-verified at cycle 12 from a fresh Python subprocess; both bass_v2 (`832868d0…aeac5`) and drums (`dadafcfc…64b8d7c`) anchors reproduce byte-identical over two runs.
- `M-V4-SHOWCASE-1` gate: 2 of 5 CG instruments have terminal verdicts (bass accepted; drums arc-exhausted, awaiting operator drums-acceptance decision). Piano, guitar, and other-residual remain pending.
- Cycle-13 scope: register the drums acceptance-policy outcome (either operator directive on arrival or agent-elected option under the c9 banned-heartbeat rule), open the cg-piano SoundFont coarse sweep, and back-fill accumulated test debt for the family-2 drums render path.

## Scripts (cycles 13–15 delta)

### `scripts/sound_match/`

| file | cycle | purpose |
|---|---|---|
| `coarse_sweep_sf2_guitar.py` | 13 | 15-preset guitar coarse-sweep sibling (channel 1, GM programs 24–31); consumes `guitar.mid` transcription |
| `fine_fit_sf2_guitar.py` | 14 | 180-cell guitar stage-2 fine-fit; LUFS-normalised, channel 1 |
| `_launch_cg_guitar_stage2_c14.sh` | 14 | detached launcher for the c14 guitar stage-2 fine-fit |
| `_emit_c14_guitar_profile.py` | 14 | emits `guitar.json` + replay proof + SF2 family verdict |
| `family2_stem_sampled_guitar_spike.py` | 15 | family-2 guitar shape probe; onset-slice bank builder |
| `family2_stem_sampled_guitar_builder.py` | 15 | family-2 guitar builder; nearest-pitch dispatch + pyin pitch-shift (E1–E7) |
| `_c15_family2_guitar_emit.py` | 15 | scoring + `guitar_family2_v1.json` + replay-proof + verdict emitter |
| `measure_stem_audibility.py` | 14 | LUFS-I / RMS-dBFS audibility measurement helper (with silence-floor fallback) |
| `_emit_c13_ledger_events.py`, `_emit_c14_ledger_events.py`, `_emit_c15_ledger_events.py` | 13/14/15 | per-cycle ledger-event emitters |

## Tests (cycles 13–15 delta)

| file | cycle | purpose |
|---|---|---|
| `tests/test_sound_match_family2_drums.py` | 14 | pins the c12 family-2 drums render SHA `69a76c5b…` and the c12 anchor script SHAs; encodes the interpreter-guard grandfathering contract |
| (guitar family-2 spike/builder tests) | 15 | deferred by design; scheduled for cycle-16 alongside the embedding-metric diagnostic (see report §5) |

## Data artefacts (cycles 13–15)

Under `data/v4/profiles/31a164f845f8e27e/`:

| file | cycle | notes |
|---|---|---|
| `guitar_sweep_stage1/leaderboard.tsv` | 13 | 15-preset guitar coarse-sweep leaderboard |
| `guitar_sweep_stage2/leaderboard.tsv` | 14 | 180-cell guitar stage-2 leaderboard; source-of-truth GM program 27 best rank 84 |
| `piano_null_finding.json` | 14 | grounded null (0 note_on + reference RMS −81.5 dBFS ≪ −60 silence floor); supersedes c13 ungrounded version archived under `stale/` |
| `other_null_finding.json` | 14 | symmetric grounded null for other-residual (0 note_on + reference RMS −81.7 dBFS); closes c13 auditor MINOR #1 |
| `audibility/piano_stem_audibility.json`, `audibility/other_stem_audibility.json` | 14 | audibility measurement sidecars |
| `guitar.json` | 14 | SF2 profile, top-1 GM program 28 gain 1.5 reverb 0.7, `embedding_cos_vggish = 0.2584` |
| `guitar.replay_proof.json` | 14 | canonical replay SHA `e2fee72dfa6b408e…`; `REPLAY_PROOF_HOLDS` |
| `guitar_family_verdict.json` | 14 | **`SF2_RULED_OUT`**, 0.2584 < 0.40 floor |
| `guitar_family2_v1.json` + `.replay_proof.json` | 15 | family-2 guitar profile UUID `a7c62e5e-…`; render SHA `f41560714a68415c…`; run1 = run2 |
| `guitar_family2_render/render.wav` | 15 | family-2 concatenative guitar render |
| `guitar_family2_verdict.json` | 15 | **`FAMILY2_RULED_OUT`**, `embedding_cos_vggish = 0.0354` |
| `guitar_arc_closeout.json` | 15 | **`CG_GUITAR_ARC_EXHAUSTED_NO_CONFIRMED`**; parallels bass c7 and drums c12 |
| `_manager/M-V4-SHOWCASE-1-cg-guitar-acceptance-policy.json` | 15 | three-option fork; `status = resolved_via_agent_picks_invariants` (OPT3) |
| `_c15_guitar_family2_summary.json` | 15 | cycle-summary sidecar |

Under `data/v4/deliveries/31a164f845f8e27e/`:

| file | cycle | notes |
|---|---|---|
| `cg_drums_pinned_profile.json` | 14 | OPT3 pin: htdemucs drums stem substituted verbatim in showcase mix |
| `cg_guitar_pinned_profile.json` | 15 | OPT3 pin: htdemucs guitar stem (`sha256 = e4ff08ea…`) substituted verbatim; `supersedes_path` string per invariant (d) |

Under `docs/`:

| file | cycle | notes |
|---|---|---|
| `agent_picks_selection_invariants.md` | 14 (a/b/c); 15 extends (d) | codifies the three (then four) invariants agents apply to anti-stall option-selection forks |
| `interpreter_guard_policy.md` | 15 | canonical shebang policy for new sound-match scripts, with c12-anchor grandfathering contract |

## Downstream state at cycle-15 close

- **All 5 CG instrument cells terminal.** bass_v2 accepted (c9); drums OPT3 refuse-showcase (c14); guitar OPT3 refuse-showcase (c15); piano and other-residual grounded null (c14); vocals covered by hybrid-overlay policy. `deliver_cg_ab_v4.py --smoke-test` reports `n_missing = 0`.
- **Systematic pattern surfaced.** Three consecutive CG arcs (bass c7, drums c12, guitar c15) exhausted both explored render families under the retained 0.40 emb-cos floor. On every SF2 stage-2 sweep the frozen composite ranks a non-source-of-truth program ahead of the ground-truth GM program (organ > bass; Power Kit > Standard; Nylon/Jazz > Rock).
- **Latent correctness concern outstanding.** The c15 auditor surfaced a sign-convention question on `embedding_cos_vggish`: the panel emits `1 − cos_sim` (a distance, in [0, 2]) while the campaign's verdict thresholds are worded as similarity (≥ 0.60 CONFIRMED, < 0.40 RULED_OUT). If the field is truly a distance, every CG family verdict since c1 is potentially inverted. Escalated as the mandatory first item for c16; downstream OPT3 pins remain safe regardless because htdemucs reference stems are operator-heard truth by construction.
- **Codified process norms.** `docs/agent_picks_selection_invariants.md` (a/b/c/d) and `docs/interpreter_guard_policy.md` are now the two operating-discipline anchors specific to this campaign. The c14 revise of the c13 drums fork is retroactively conformant to the codified invariants; the c15 guitar fork was resolved conformantly on the first attempt.
- **Cycle-16 scope**: (1) diagnose the embedding-metric sign convention with a controlled two-clip probe and escalate to operator; (2) either render the CG A/B end to end (unblocked by `n_missing = 0`) or hold pending item 1's resolution per operator guidance; (3) formalize the pinned-profile shape (add invariant (e) or a JSON Schema); (4) back-fill guitar family-2 spike/builder tests + the ~3-WARN adoption-row drift.
