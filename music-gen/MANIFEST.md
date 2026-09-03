# Music-Gen v4 closure campaign — MANIFEST

Snapshot at cycle-9 close. Scope: files produced or extended during
cycles 1–9 of the v4 closure campaign (Chicken Grease bass
sound-matching sub-milestone closed under operator OPT1+OPT3
acceptance; Chicken Grease drums arc scaffolded to launch-ready;
`M-V4-SHOWCASE-1` A/B render scaffold in place with `n_missing = 4`;
plus the determinism-certificate check). Prior v3-arc anchors are
read-only and are not re-inventoried here; the cycles reports §A.1
and §A.4 list them explicitly.

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
| `coarse_sweep_sf2_drums.py` | 9 | drums coarse-sweep sibling (15 471 B); dry-run PASS, detached launch halted by disk-check false positive — cycle-10 fix scope |
| `deliver_cg_ab_v4.py` | 9 | Chicken Grease A/B render scaffold (5402 B); smoke test only, no render (`n_missing = 4`) |

Cycle-1 anchor `coarse_sweep_sf2.py` (SHA `c74c35bc…`) verified byte-identical through cycle 9.

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

## Downstream state at cycle-9 close

- cg-bass arc closed under operator OPT1+OPT3 hybrid acceptance; `bass_v2.json` (program 33, embedding-cosine 0.4946) is the pinned Chicken Grease bass profile. The 0.60 CONFIRMED threshold is retired for this one acceptance; the 0.40 RULED_OUT floor is retained for future family verdicts.
- cg-drums arc scaffolded to launch-ready; detached sweep deferred one cycle by a `_disk_ok()` false positive (statvfs vs df: 97.39% vs 82.24% used on a volume with 6.6 GB free against a 500 MB budget) — cycle-10 patch scope.
- `M-V4-SHOWCASE-1` unblocked in principle; A/B render scaffold (`deliver_cg_ab_v4.py`) reports `n_missing = 4` (drums, piano, guitar, other). Full render fires when the four remaining Chicken Grease instrument profiles land.
- v4 wait-on-operator heartbeat cadence formally retired at cycle 9 after a single cycle of operational use (cycle 8).
- Cycle-10 scope: fix `_disk_ok()`, launch drums sweep detached under canonical 7-key env-pin, then rotate through cg-piano/keys, cg-guitar, cg-other at one instrument per cycle.
