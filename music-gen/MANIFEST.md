# Music-Gen v4 closure campaign — MANIFEST

Snapshot at cycle-3 close. Scope: files produced or extended during
cycles 1–3 of the v4 closure campaign (Chicken Grease bass
sound-matching sub-milestone, plus the determinism-certificate check).
Prior v3-arc anchors are read-only and are not re-inventoried here;
the cycles 1–3 report §A.1 and §A.4 lists them explicitly.

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

Other files in `scripts/sound_match/` (`objective.py`, `replay.py`,
`replay_proof.py`, `deliver_ab.py`) are prior-arc anchors used
unchanged during cycles 1–3.

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

## Environment pins in force across cycles 1–3

| pin | scope |
|---|---|
| `623df01f262ffd180c8497ce9bb06a2d4438b9239d60dd997304830b6571d38d` | v3 spine driver session; determinism certificate anchors here |
| `2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca` | cycle-2 fine-fit v1; cycle-2 cg-bass profile + replay proof anchor here |
| v2 hash (absorbs `pyloudnorm_available` + `lufs_target_db`) | cycle-3 fine-fit v2; any new pinned profile from stage-2b needs a fresh replay proof under this pin |

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

## Cumulative stats (cycles 1–3 delta only)

- New scripts: 6 (2 launchers not counted separately as they are shell one-liners) or 9 including launchers.
- New tests: 3 files, 27 test functions (8 + 14 + 5).
- New leaderboards: 3 (coarse, fine-fit v1, stage-2b v2).
- New pinned profile: 1 (cg-bass, cycle 2).
- New replay proof: 1 (cg-bass SoundFont family, cycle 2).
