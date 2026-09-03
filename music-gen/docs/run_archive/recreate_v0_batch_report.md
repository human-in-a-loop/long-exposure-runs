---
created: 2026-08-29T11:00:00Z
cycle: 38
run_id: run-2026-08-28T040704Z
agent: worker
milestone: M-RECREATE-1/second-real-audio-batch
fork: 33a2a8003c84
clone: 2
rubric_hash: be65f7cb37f71c4613afceb70dafa03a1bc68a384f4b51639127b4d5256b718d
---

# M-RECREATE-1/second-real-audio-batch — Clone-2 Report

**Fork:** 33a2a8003c84 · **Clone:** 2 · **Cycle:** 38
**Milestone:** `M-RECREATE-1/second-real-audio-batch` (peer sub-milestone
under G1, per the c29 state-machine lemma — NOT a child of the
terminal-validated c37 `M-RECREATE-1/first-real-audio`).

**Rubric SHA-256 (frozen 2026-08-29T10:30:00Z):**
`be65f7cb37f71c4613afceb70dafa03a1bc68a384f4b51639127b4d5256b718d`
committed BEFORE any file under `scripts/recreate_v0_batch/` (mtime-order
test + git-log order test enforce this — the git-log gate is
`MERGE_DEFERRED` in this clone's environment; the mtime gate is enforced
in-clone).

## 1. Verdict

**BATCH_LANDS** — 5/5 pipeline OK, 20/20 byte-det anchors, 5/5 positive mel delta

| Field | Value |
|---|---|
| n_songs | 5 |
| n_pipeline_ok | 5/5 |
| n_byte_det_x2 | 5/5 |
| n_positive_mel_delta | 5/5 |
| anchors_unchanged | True |
| rubric_hash | `be65f7cb37f71c4613afceb70dafa03a1bc68a384f4b51639127b4d5256b718d` |
| total_wall_seconds | 847.824 |

## 2. Selection (SHA-256 tiebreak per bucket + band-6 second-lowest)

Excluded: `corpus/ratings/7/016__LOCAL__05_02.mp3` (c37 clone-0's song).
Candidates after exclusion: 42.

| Band | Slot | SHA-256 (prefix) | Relpath | Bytes |
|---|---|---|---|---|
| 4 | band_lowest_sha | `1d0f6dbbc9be325c` | `corpus/ratings/4/013__jZVdDl_asYY__Mariah_Carey_-_Shake_It_Off.mp3` | 6649386 |
| 5 | band_lowest_sha | `18fe981c78eae847` | `corpus/ratings/5/002__EvyTWRB4l4w__La_Rumba_Me_Llamo_Yo_-_Dayme_Arocena.mp3` | 7741833 |
| 6 | band_lowest_sha | `087687c3cd269def` | `corpus/ratings/6/027__riDSMdAH5hk__Tom_Misch_-_Red_Moon.mp3` | 6576174 |
| 7 | band_lowest_sha | `1d9ac896511ebcd4` | `corpus/ratings/7/008__LOCAL__Oba_La_-_Vem_Ela.mp3` | 6513860 |
| 6 | band_6_second_lowest_sha | `0e1e8f20592db366` | `corpus/ratings/6/001__iLF0ZNdhNM0__Justin_Bieber_-_YUKON_Live_Grammys_2026.mp3` | 7719812 |

## 3. Cross-band panel table

Two panels per song (5 songs × 2 panels = 10 TSVs) via `M-TEX-1/panel`;
aggregated at `data/recreate_v0_batch/cross_band_table.tsv`.

| band | song_sha16 | mel_l1_db_bare | mel_l1_db_effects | mel_l1_db_delta | spectral_centroid_rmse_hz_bare | spectral_centroid_rmse_hz_effects | spectral_centroid_rmse_hz_delta | rms_env_rmse_bare | rms_env_rmse_effects | rms_env_rmse_delta | lufs_m_rmse_bare | lufs_m_rmse_effects | lufs_m_rmse_delta |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 4.000 | 1d0f6dbbc9be325c | 28.838 | 20.855 | 7.983 | 3263.149 | 3376.530 | -113.381 | 0.180 | 0.156 | 0.023 | 13.835 | 11.692 | 2.143 |
| 5.000 | 18fe981c78eae847 | 17.672 | 14.793 | 2.879 | 1934.274 | 2123.598 | -189.324 | 0.052 | 0.054 | -0.002 | 13.864 | 12.297 | 1.567 |
| 6.000 | 087687c3cd269def | 21.536 | 16.318 | 5.217 | 1741.541 | 1491.039 | 250.502 | 0.187 | 0.177 | 0.010 | 13.360 | 16.470 | -3.110 |
| 7.000 | 1d9ac896511ebcd4 | 19.820 | 15.149 | 4.670 | 1536.079 | 1050.876 | 485.203 | 0.101 | 0.084 | 0.017 | 10.167 | 10.710 | -0.544 |
| 6.000 | 0e1e8f20592db366 | 21.669 | 17.244 | 4.425 | 2483.682 | 2171.109 | 312.573 | 0.034 | 0.048 | -0.015 | 14.398 | 16.610 | -2.212 |


**Deltas** are `bare − effects`; positive = effects narrows gap.

## 4. Cross-band correlation (n=5, exploratory only)

- **lufs_m_rmse_lu**: n=5, Pearson r=-0.695, Spearman ρ=-0.667. _n=5; correlation is exploratory only, not inferentially valid_
- **mel_l1_db**: n=5, Pearson r=-0.483, Spearman ρ=-0.205. _n=5; correlation is exploratory only, not inferentially valid_
- **rms_env_rmse**: n=5, Pearson r=-0.199, Spearman ρ=-0.205. _n=5; correlation is exploratory only, not inferentially valid_
- **spectral_centroid_rmse_hz**: n=5, Pearson r=0.911, Spearman ρ=0.872. _n=5; correlation is exploratory only, not inferentially valid_


## 5. Byte-determinism × 2

Every one of the 20 anchors (5 songs × 4 anchors: merged.musicxml,
merged.midi, bare_midi.wav, effects.wav) run twice into independent
fresh out-dirs under the same environment pins (`OMP/MKL/OPENBLAS=1`,
`torch.manual_seed(0)`). Results in per-song
`per_song_result.json.determinism`; aggregate:
`5/5` songs 4/4 byte-det.

Any drift on `effects.wav` is documented as substantive characterization
per c36 Branch C VST3-nondeterminism finding, NOT hidden.

## 6. Preview_untrained_ear caveat

Cite Branch A: [`docs/ear_real_label_training_v1_report.md`](../docs/ear_real_label_training_v1_report.md) — v1 real-label ear model report present on disk at write time; per Branch C contract, cite by document path only (never import artifact).

Per-song application:

- **Band 4 · sha `1d0f6dbbc9be325c`** — `corpus/ratings/4/013__jZVdDl_asYY__Mariah_Carey_-_Shake_It_Off.mp3`: pipeline=OK, byte-det×2=OK, mel_l1_db_delta=7.983 dB. Cite Branch A: [`docs/ear_real_label_training_v1_report.md`](../docs/ear_real_label_training_v1_report.md) — v1 real-label ear model report present on disk at write time; per Branch C contract, cite by document path only (never import artifact).
- **Band 5 · sha `18fe981c78eae847`** — `corpus/ratings/5/002__EvyTWRB4l4w__La_Rumba_Me_Llamo_Yo_-_Dayme_Arocena.mp3`: pipeline=OK, byte-det×2=OK, mel_l1_db_delta=2.879 dB. Cite Branch A: [`docs/ear_real_label_training_v1_report.md`](../docs/ear_real_label_training_v1_report.md) — v1 real-label ear model report present on disk at write time; per Branch C contract, cite by document path only (never import artifact).
- **Band 6 · sha `087687c3cd269def`** — `corpus/ratings/6/027__riDSMdAH5hk__Tom_Misch_-_Red_Moon.mp3`: pipeline=OK, byte-det×2=OK, mel_l1_db_delta=5.217 dB. Cite Branch A: [`docs/ear_real_label_training_v1_report.md`](../docs/ear_real_label_training_v1_report.md) — v1 real-label ear model report present on disk at write time; per Branch C contract, cite by document path only (never import artifact).
- **Band 7 · sha `1d9ac896511ebcd4`** — `corpus/ratings/7/008__LOCAL__Oba_La_-_Vem_Ela.mp3`: pipeline=OK, byte-det×2=OK, mel_l1_db_delta=4.670 dB. Cite Branch A: [`docs/ear_real_label_training_v1_report.md`](../docs/ear_real_label_training_v1_report.md) — v1 real-label ear model report present on disk at write time; per Branch C contract, cite by document path only (never import artifact).
- **Band 6 · sha `0e1e8f20592db366`** — `corpus/ratings/6/001__iLF0ZNdhNM0__Justin_Bieber_-_YUKON_Live_Grammys_2026.mp3`: pipeline=OK, byte-det×2=OK, mel_l1_db_delta=4.425 dB. Cite Branch A: [`docs/ear_real_label_training_v1_report.md`](../docs/ear_real_label_training_v1_report.md) — v1 real-label ear model report present on disk at write time; per Branch C contract, cite by document path only (never import artifact).

## 7. Anchor preservation

18 c37 clone-0 upstream anchors +
recreate_v0 stage scripts + c37 data anchors:
**unchanged = True**.
All byte-identical pre/post batch run.

## 8. Rubric commitment order

- Rubric doc on disk: `docs/recreate_v0_batch_rubric.md`
- Rubric hash file: `data/recreate_v0_batch/rubric_hash.txt`
- Rubric hash: `be65f7cb37f71c4613afceb70dafa03a1bc68a384f4b51639127b4d5256b718d`
- **mtime gate:** rubric mtime ≤ every script mtime under
  `scripts/recreate_v0_batch/` — enforced by
  `tests/test_recreate_v0_batch.py::test_04_rubric_mtime_precedes_scripts`.
- **git-log gate:** deferred to merge conductor (this clone's
  environment does not permit `git add`/`git commit`).
  `tests/test_recreate_v0_batch.py::test_05_rubric_git_log_order` records
  the deferral explicitly.

## 9. c39 handoff seeds (independent of verdict polarity)

Per the research brief §c39 handoff seeds — chosen conditionally on
this cycle's verdict `BATCH_LANDS`:

- **If `BATCH_LANDS`**: c39 opens (a) merging cross-band results with
  Branch A's v1 model; (b) `M-RECREATE-1/full-corpus-recreation`
  on remaining 37 songs.
- **If `BATCH_PARTIAL` with byte-det failure(s) on effects.wav**: c39
  lifts c36 Branch C VST3 characterization onto per-band data.
- **If `BATCH_PARTIAL` with mel_l1_db-delta failure(s)**: c39 opens
  `_manager/effects-chain-band-selectivity` investigation.
- **If `BATCH_FAILS`**: c39 opens stage-isolation branch reproducing
  the failure minimally, with named-band-bias analysis if failures
  concentrate on one band.
- **Regardless**: cross-band correlation coefficients (statistically
  weak at n=5) become the seed hypothesis for c40+ larger-N tests.

## 10. Test coverage

`tests/test_recreate_v0_batch.py` — 15 named test cases:

1. AST: no PRNG in `select_songs.py`.
2. `chosen_songs.json` excludes `016__LOCAL__05_02.mp3`.
3. Each chosen SHA-256 matches actual file bytes.
4. Rubric mtime ≤ every script mtime.
5. Rubric commit predates every script commit (`MERGE_DEFERRED`).
6. `verdict.json.rubric_hash` byte-equals `rubric_hash.txt`.
7. Per-song stage manifests: 5 songs × 8 stages = 40.
8. Byte-determinism × 2: 20 SHA-equal assertions.
9. `cross_band_table.tsv` has 5 rows × 14 columns.
10. `cross_band_correlation.json` carries literal `n_too_small_caveat`.
11. No writes under c37 `data/recreate_v0/` (via anchor preservation).
12. Literal preview_untrained_ear caveat present (v1 or v0 branch).
13. c37 upstream anchor preservation (≥18 anchors).
14. AST: no Branch A / Branch B imports.
15. AST: no forbidden state calls (`get_state`, `save_state`, etc.);
    no `sidecar_nonfactor` / `i4_stratified` imports; interpreter
    guard on every executable script.

Run: `PYTHONPATH=. /usr/bin/python3 tests/test_recreate_v0_batch.py`

END OF REPORT.
