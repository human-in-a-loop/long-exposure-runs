---
created: 2026-08-29T14:00:00Z
cycle: 39
run_id: run-2026-08-28T040704Z
agent: worker
milestone: M-RECREATE-1/full-corpus-recreation
fork: c320de981fda
clone: 0
---

# M-RECREATE-1/full-corpus-recreation — Report

First full-G1-spine measurement on real rated audio at scale: 37 songs across bands 4/5/6/7, extending cycle-37 clone-0's 1-song `RECREATION_LANDS` and cycle-38 clone-2's 5-song `BATCH_LANDS`.

## 1. Verdict

**FULL_CORPUS_LANDS** — 37/37 pipeline OK, 148/148 byte-det anchors, 36/37 positive mel delta (>=33 threshold)

- `rubric_hash`: `4cfca25d71f8bb67a2c3b2be30a3d2173f9ef893d31f3cf0fd88c093e1a954a2` (byte-equal to `data/recreate_v0_full_corpus/rubric_hash.txt`)
- Rubric verdicts: ['FULL_CORPUS_LANDS', 'FULL_CORPUS_PARTIAL', 'FULL_CORPUS_FAILS']
- LANDS threshold (positive mel delta): >= 33/37 (~89%)

## 2. Song selection

- Selection rule: `sha256_tiebreak_over_43_song_corpus_minus_6_song_exclusion`
- n_candidates_after_exclusion: 37
- n_chosen: 37
- Per-bucket counts: {'4': 9, '5': 9, '6': 11, '7': 8}

### Exclusion set (6 songs)

- `corpus/ratings/4/013__jZVdDl_asYY__Mariah_Carey_-_Shake_It_Off.mp3`
- `corpus/ratings/5/002__EvyTWRB4l4w__La_Rumba_Me_Llamo_Yo_-_Dayme_Arocena.mp3`
- `corpus/ratings/6/001__iLF0ZNdhNM0__Justin_Bieber_-_YUKON_Live_Grammys_2026.mp3`
- `corpus/ratings/6/027__riDSMdAH5hk__Tom_Misch_-_Red_Moon.mp3`
- `corpus/ratings/7/008__LOCAL__Oba_La_-_Vem_Ela.mp3`
- `corpus/ratings/7/016__LOCAL__05_02.mp3`

### 37-song canonical order (ascending SHA-256)

| # | band | file_sha256[:16] | mp3 bytes | relpath |
|---|------|------------------|-----------|---------|
| 0 | 4 | `2059d5e60e721e7f` | 6710902 | `corpus/ratings/4/019__-dyPeGDeS3o__J._Cole_-_Lights_Please.mp3` |
| 1 | 5 | `252eb21ce7df7328` | 4963344 | `corpus/ratings/5/021__pLuQ0MGLBXU__Mura_Masa_-_What_If_I_Go.mp3` |
| 2 | 7 | `2b0370d9d0162c98` | 7680296 | `corpus/ratings/7/001__LOCAL__Desire.mp3` |
| 3 | 6 | `31a164f845f8e27e` | 7394003 | `corpus/ratings/6/017__It2s36sL4aM__Chicken_Grease.mp3` |
| 4 | 6 | `34e97266d484aead` | 7244637 | `corpus/ratings/6/025__6EPwRdVg5Ug__Lake_Street_Dive_-_I_Want_You_Back_Sidewalk.mp3` |
| 5 | 5 | `3cc219598762c5a2` | 4605190 | `corpus/ratings/5/013__vYgTpLAIYgY__Aaron_Frazer_-_My_God_Has_A_Telephone.mp3` |
| 6 | 5 | `41bdba5c3dad40ac` | 5875008 | `corpus/ratings/5/023__QnO6Dxi2qtQ__Tedeschi_Trucks_Band_-_Part_of_Me_acoustic.mp3` |
| 7 | 4 | `42f585b439ef32ee` | 6475539 | `corpus/ratings/4/012__XKQNJzquduI__Frank_Ocean_-_Provider.mp3` |
| 8 | 7 | `467fbeb2e3b019a0` | 6348911 | `corpus/ratings/7/005__LOCAL__Wizkid_-_Essence_ft._Tems.mp3` |
| 9 | 5 | `46eb16d39cf8bb61` | 5272007 | `corpus/ratings/5/010__olwAPZ9L1io__Yesterday.mp3` |
| 10 | 4 | `49956e7d3d507769` | 5972008 | `corpus/ratings/4/014__QReOON-c6-4__Lucy_Pearl_-_Dance_Tonight.mp3` |
| 11 | 5 | `51e433ade2a845e1` | 5462329 | `corpus/ratings/5/012__gPp2KBV9zXk__Dojo_Cuts_-_Rome.mp3` |
| 12 | 6 | `5420adb139cae8db` | 6661750 | `corpus/ratings/6/004__KXdW0g6jAxE__Anderson_.Paak_-_The_Bird.mp3` |
| 13 | 6 | `6edf398477b3fb73` | 3446433 | `corpus/ratings/6/021__O_HoOpJ60C0__Charli_xcx_-_360.mp3` |
| 14 | 4 | `733ab58ee9bf7029` | 5680846 | `corpus/ratings/4/007__1gX1EP6mG-E__Old_Crow_Medicine_Show_-_Wagon_Wheel.mp3` |
| 15 | 6 | `78bdd2ce2fc5c1af` | 5673599 | `corpus/ratings/6/023__rqScfATfNnc__FKJ_-_10_Years_Ago.mp3` |
| 16 | 7 | `7e6b59b873ed8972` | 6137529 | `corpus/ratings/7/013__LOCAL__I_Found_My_Smile_Again_Radio_Edit.mp3` |
| 17 | 5 | `822e8e5c5bf12c05` | 5834573 | `corpus/ratings/5/030__fcNKG_isFgg__Windows.mp3` |
| 18 | 6 | `88d247468cb6d49f` | 5796054 | `corpus/ratings/6/015__wXvX1vOe0rQ__Peach_Dream.mp3` |
| 19 | 4 | `8b6dc92b73b3877a` | 9208177 | `corpus/ratings/4/001__pz650EkJFKc__Hector_Lavoe_-_Aguanile.mp3` |
| 20 | 4 | `a0979974ee89e398` | 3751337 | `corpus/ratings/4/006__gFGqiwA5gTc__Whitney_-_FTA.mp3` |
| 21 | 5 | `a4e6ab346837dbd4` | 3067735 | `corpus/ratings/5/016__c7BxiPq_6Ok__Cerca_De_Ti.mp3` |
| 22 | 7 | `a9587ccde1b333f5` | 7120771 | `corpus/ratings/7/019__LOCAL__Hiatus_Kaiyote_-_Molasses.mp3` |
| 23 | 4 | `a97f83cba25037b6` | 6828321 | `corpus/ratings/4/011__8Ee4QjCEHHc__Calvin_Harris_-_Slide_ft._Frank_Ocean_Migos.mp3` |
| 24 | 7 | `ae1b65eaf1560951` | 5253343 | `corpus/ratings/7/020__LOCAL__Shaolin_Monk_Motherfunk_Nai_Palm_Commentary.mp3` |
| 25 | 7 | `b8a030a4264a7aba` | 5010924 | `corpus/ratings/7/010__LOCAL__Samba_De_Raiz_-_Conselho.mp3` |
| 26 | 7 | `b8ae0217bb9660d8` | 3903050 | `corpus/ratings/7/015__LOCAL__Bruno_Berle_-_Som_Nyame.mp3` |
| 27 | 4 | `bed1a8f2315bc877` | 5346000 | `corpus/ratings/4/008__5gJmpjRm1RA__Cordae_-_Summer_Drop_ft._Anderson_.Paak.mp3` |
| 28 | 7 | `c7d491e98767eea5` | 5500131 | `corpus/ratings/7/002__LOCAL__Freedom_Interlude.mp3` |
| 29 | 4 | `cb771dae8fc3d962` | 7833695 | `corpus/ratings/4/002__Bc4AezWceUc__Stay_Live.mp3` |
| 30 | 6 | `cc0693b4a24f64b2` | 3856693 | `corpus/ratings/6/008__pxAWICqgjHM__Allah-Las_-_Houston.mp3` |
| 31 | 5 | `cdd2717e52820ff6` | 3881313 | `corpus/ratings/5/011__hcwKJOsUUIk__Disco_A.mp3` |
| 32 | 5 | `dcfdabd9a4331b82` | 6172757 | `corpus/ratings/5/019__kNwkXGeHE34__Gecko_Turner_-_Toda_Mojaita.mp3` |
| 33 | 6 | `e02d1eedf06ec62b` | 7683964 | `corpus/ratings/6/016__1GmuDka6pbk__Loyle_Carner_-_Angel_ft._Tom_Misch.mp3` |
| 34 | 6 | `e61bfa4144344843` | 5034338 | `corpus/ratings/6/007__89RgkWOsn18__Lost.mp3` |
| 35 | 6 | `e66cbeb1817e37f0` | 4576271 | `corpus/ratings/6/028__gLcTMUNmgwk__Jess_Best_-_Forgetfulness.mp3` |
| 36 | 6 | `f1cfe4855364ea9b` | 7931392 | `corpus/ratings/6/013__EO5dUydK2vU__Tom_Misch_Yussef_Dayes_-_Last_100.mp3` |

## 3. Per-band summary

| band | n_total | n_pipeline_ok | n_byte_det_ok | n_positive_mel_delta |
|------|---------|---------------|---------------|---------------------|
| 4 | 9 | 9 | 9 | 9 |
| 5 | 9 | 9 | 9 | 9 |
| 6 | 11 | 11 | 11 | 10 |
| 7 | 8 | 8 | 8 | 8 |

## 4. Per-song results

### Song 0: band 4, sha `2059d5e60e721e7f`

- relpath: `corpus/ratings/4/019__-dyPeGDeS3o__J._Cole_-_Lights_Please.mp3`
- file_sha256: `2059d5e60e721e7f241e3bb6e0ce27c4ab030ee3b6d27ebe3004c22057423585`
- run1 wall_clock_s: 84.15
- run2 wall_clock_s: 79.07
- run1_failed_stage: `None`
- byte-determinism x 2 (all 4 anchors): **yes**

| anchor | run1 sha[:16] | run2 sha[:16] | equal |
|--------|---------------|---------------|-------|
| `06_score/merged.midi` | `161a725277e8e191` | `161a725277e8e191` | yes |
| `06_score/merged.musicxml` | `63764fb946331ba0` | `63764fb946331ba0` | yes |
| `07_render/bare_midi.wav` | `29c26ad230d51f52` | `29c26ad230d51f52` | yes |
| `07_render/effects.wav` | `a83f8dd065cf68d3` | `a83f8dd065cf68d3` | yes |

- M-TEX-1 panel deltas (bare − effects; positive = effects narrows the gap):
  - `mel_l1_db`: bare 27.8219, effects 19.2917, delta **8.5302**
  - `spectral_centroid_rmse_hz`: bare 1814.0668, effects 1621.2505, delta 192.8163
  - `rms_env_rmse`: bare 0.2168, effects 0.2089, delta 0.0079
  - `lufs_m_rmse_lu`: bare 24.0617, effects 19.5765, delta 4.4853

- pretty_midi_fallback_used_run1: `False`

- preview_untrained_ear: M-EAR-1/real-label-training-v1 verdict EAR_v1_PARTIAL (SB1 -0.209 / SB2 -0.099 / SB3 corpus-shape-degenerate; 43/80 corpus coverage) — see docs/ear_real_label_training_v1_report.md — this pipeline does NOT compute per-song ear predictions

### Song 1: band 5, sha `252eb21ce7df7328`

- relpath: `corpus/ratings/5/021__pLuQ0MGLBXU__Mura_Masa_-_What_If_I_Go.mp3`
- file_sha256: `252eb21ce7df7328e498b14f94afc8f38fec5c5fa85a9f815c7ee6ca94c4e59a`
- run1 wall_clock_s: 82.72
- run2 wall_clock_s: 80.54
- run1_failed_stage: `None`
- byte-determinism x 2 (all 4 anchors): **yes**

| anchor | run1 sha[:16] | run2 sha[:16] | equal |
|--------|---------------|---------------|-------|
| `06_score/merged.midi` | `97a2066575778e19` | `97a2066575778e19` | yes |
| `06_score/merged.musicxml` | `deb4e56d5ea8fb18` | `deb4e56d5ea8fb18` | yes |
| `07_render/bare_midi.wav` | `ff06b601ecf1d017` | `ff06b601ecf1d017` | yes |
| `07_render/effects.wav` | `9ad4e8b7e554125b` | `9ad4e8b7e554125b` | yes |

- M-TEX-1 panel deltas (bare − effects; positive = effects narrows the gap):
  - `mel_l1_db`: bare 24.9812, effects 13.9635, delta **11.0178**
  - `spectral_centroid_rmse_hz`: bare 1929.7833, effects 1791.4219, delta 138.3615
  - `rms_env_rmse`: bare 0.1806, effects 0.1660, delta 0.0146
  - `lufs_m_rmse_lu`: bare 20.5761, effects 17.4847, delta 3.0914

- pretty_midi_fallback_used_run1: `False`

- preview_untrained_ear: M-EAR-1/real-label-training-v1 verdict EAR_v1_PARTIAL (SB1 -0.209 / SB2 -0.099 / SB3 corpus-shape-degenerate; 43/80 corpus coverage) — see docs/ear_real_label_training_v1_report.md — this pipeline does NOT compute per-song ear predictions

### Song 2: band 7, sha `2b0370d9d0162c98`

- relpath: `corpus/ratings/7/001__LOCAL__Desire.mp3`
- file_sha256: `2b0370d9d0162c98dd59c5705c5e7b206fb2ac9e3c36e534b162b662db95daf6`
- run1 wall_clock_s: 89.85
- run2 wall_clock_s: 88.43
- run1_failed_stage: `None`
- byte-determinism x 2 (all 4 anchors): **yes**

| anchor | run1 sha[:16] | run2 sha[:16] | equal |
|--------|---------------|---------------|-------|
| `06_score/merged.midi` | `7be06325f70c8565` | `7be06325f70c8565` | yes |
| `06_score/merged.musicxml` | `2a1356c1d585fe90` | `2a1356c1d585fe90` | yes |
| `07_render/bare_midi.wav` | `858c73ad83217e6b` | `858c73ad83217e6b` | yes |
| `07_render/effects.wav` | `46e7e47cad02c412` | `46e7e47cad02c412` | yes |

- M-TEX-1 panel deltas (bare − effects; positive = effects narrows the gap):
  - `mel_l1_db`: bare 12.8168, effects 7.9279, delta **4.8888**
  - `spectral_centroid_rmse_hz`: bare 1229.9326, effects 1060.8802, delta 169.0523
  - `rms_env_rmse`: bare 0.0631, effects 0.0861, delta -0.0230
  - `lufs_m_rmse_lu`: bare 6.6728, effects 7.0862, delta -0.4133

- pretty_midi_fallback_used_run1: `False`

- preview_untrained_ear: M-EAR-1/real-label-training-v1 verdict EAR_v1_PARTIAL (SB1 -0.209 / SB2 -0.099 / SB3 corpus-shape-degenerate; 43/80 corpus coverage) — see docs/ear_real_label_training_v1_report.md — this pipeline does NOT compute per-song ear predictions

### Song 3: band 6, sha `31a164f845f8e27e`

- relpath: `corpus/ratings/6/017__It2s36sL4aM__Chicken_Grease.mp3`
- file_sha256: `31a164f845f8e27e7ee49d7871bb0d3643262b6df69826ed74855507e84b3049`
- run1 wall_clock_s: 78.77
- run2 wall_clock_s: 78.58
- run1_failed_stage: `None`
- byte-determinism x 2 (all 4 anchors): **yes**

| anchor | run1 sha[:16] | run2 sha[:16] | equal |
|--------|---------------|---------------|-------|
| `06_score/merged.midi` | `c4d1a333c78e13fd` | `c4d1a333c78e13fd` | yes |
| `06_score/merged.musicxml` | `b89ad0120210497b` | `b89ad0120210497b` | yes |
| `07_render/bare_midi.wav` | `09b41d33bc2de88a` | `09b41d33bc2de88a` | yes |
| `07_render/effects.wav` | `aec6e869d3bbd0e4` | `aec6e869d3bbd0e4` | yes |

- M-TEX-1 panel deltas (bare − effects; positive = effects narrows the gap):
  - `mel_l1_db`: bare 21.2505, effects 12.6028, delta **8.6477**
  - `spectral_centroid_rmse_hz`: bare 2878.8759, effects 2796.4231, delta 82.4528
  - `rms_env_rmse`: bare 0.1238, effects 0.1237, delta 0.0001
  - `lufs_m_rmse_lu`: bare 17.0880, effects 11.6013, delta 5.4868

- pretty_midi_fallback_used_run1: `False`

- preview_untrained_ear: M-EAR-1/real-label-training-v1 verdict EAR_v1_PARTIAL (SB1 -0.209 / SB2 -0.099 / SB3 corpus-shape-degenerate; 43/80 corpus coverage) — see docs/ear_real_label_training_v1_report.md — this pipeline does NOT compute per-song ear predictions

### Song 4: band 6, sha `34e97266d484aead`

- relpath: `corpus/ratings/6/025__6EPwRdVg5Ug__Lake_Street_Dive_-_I_Want_You_Back_Sidewalk.mp3`
- file_sha256: `34e97266d484aead534982c7b3484928d1cac2b57af26f85c66444ee703ea062`
- run1 wall_clock_s: 76.60
- run2 wall_clock_s: 77.32
- run1_failed_stage: `None`
- byte-determinism x 2 (all 4 anchors): **yes**

| anchor | run1 sha[:16] | run2 sha[:16] | equal |
|--------|---------------|---------------|-------|
| `06_score/merged.midi` | `69136b4e4bf4df7f` | `69136b4e4bf4df7f` | yes |
| `06_score/merged.musicxml` | `fc118eb9ec69ba3d` | `fc118eb9ec69ba3d` | yes |
| `07_render/bare_midi.wav` | `d6cd541650e910fd` | `d6cd541650e910fd` | yes |
| `07_render/effects.wav` | `bfb0d60b1f558583` | `bfb0d60b1f558583` | yes |

- M-TEX-1 panel deltas (bare − effects; positive = effects narrows the gap):
  - `mel_l1_db`: bare 15.8353, effects 11.8786, delta **3.9567**
  - `spectral_centroid_rmse_hz`: bare 1370.0336, effects 1279.6114, delta 90.4222
  - `rms_env_rmse`: bare 0.0370, effects 0.0490, delta -0.0120
  - `lufs_m_rmse_lu`: bare 8.4661, effects 10.1220, delta -1.6560

- pretty_midi_fallback_used_run1: `False`

- preview_untrained_ear: M-EAR-1/real-label-training-v1 verdict EAR_v1_PARTIAL (SB1 -0.209 / SB2 -0.099 / SB3 corpus-shape-degenerate; 43/80 corpus coverage) — see docs/ear_real_label_training_v1_report.md — this pipeline does NOT compute per-song ear predictions

### Song 5: band 5, sha `3cc219598762c5a2`

- relpath: `corpus/ratings/5/013__vYgTpLAIYgY__Aaron_Frazer_-_My_God_Has_A_Telephone.mp3`
- file_sha256: `3cc219598762c5a224a5e7f0c889a5d507a115894c555d7e85444e5fe0d7c722`
- run1 wall_clock_s: 81.19
- run2 wall_clock_s: 79.63
- run1_failed_stage: `None`
- byte-determinism x 2 (all 4 anchors): **yes**

| anchor | run1 sha[:16] | run2 sha[:16] | equal |
|--------|---------------|---------------|-------|
| `06_score/merged.midi` | `7295dbf9794a79c1` | `7295dbf9794a79c1` | yes |
| `06_score/merged.musicxml` | `1c7ad179e66faa7e` | `1c7ad179e66faa7e` | yes |
| `07_render/bare_midi.wav` | `3dbf63dcaf048f51` | `3dbf63dcaf048f51` | yes |
| `07_render/effects.wav` | `ac60d79339a3fcfe` | `ac60d79339a3fcfe` | yes |

- M-TEX-1 panel deltas (bare − effects; positive = effects narrows the gap):
  - `mel_l1_db`: bare 12.5204, effects 10.0081, delta **2.5122**
  - `spectral_centroid_rmse_hz`: bare 1730.7356, effects 802.1681, delta 928.5676
  - `rms_env_rmse`: bare 0.0999, effects 0.0952, delta 0.0046
  - `lufs_m_rmse_lu`: bare 5.6925, effects 7.6249, delta -1.9324

- pretty_midi_fallback_used_run1: `False`

- preview_untrained_ear: M-EAR-1/real-label-training-v1 verdict EAR_v1_PARTIAL (SB1 -0.209 / SB2 -0.099 / SB3 corpus-shape-degenerate; 43/80 corpus coverage) — see docs/ear_real_label_training_v1_report.md — this pipeline does NOT compute per-song ear predictions

### Song 6: band 5, sha `41bdba5c3dad40ac`

- relpath: `corpus/ratings/5/023__QnO6Dxi2qtQ__Tedeschi_Trucks_Band_-_Part_of_Me_acoustic.mp3`
- file_sha256: `41bdba5c3dad40ac4bf3014480355116e380c0b2a3e5e86cb87d5321f13c3cd6`
- run1 wall_clock_s: 80.03
- run2 wall_clock_s: 80.80
- run1_failed_stage: `None`
- byte-determinism x 2 (all 4 anchors): **yes**

| anchor | run1 sha[:16] | run2 sha[:16] | equal |
|--------|---------------|---------------|-------|
| `06_score/merged.midi` | `67823ba98cedef64` | `67823ba98cedef64` | yes |
| `06_score/merged.musicxml` | `e1f1d2b534cb88fb` | `e1f1d2b534cb88fb` | yes |
| `07_render/bare_midi.wav` | `2d62e2253e4a46d8` | `2d62e2253e4a46d8` | yes |
| `07_render/effects.wav` | `06237c93a7c4c333` | `06237c93a7c4c333` | yes |

- M-TEX-1 panel deltas (bare − effects; positive = effects narrows the gap):
  - `mel_l1_db`: bare 18.3588, effects 12.7219, delta **5.6369**
  - `spectral_centroid_rmse_hz`: bare 2548.4416, effects 2728.4306, delta -179.9889
  - `rms_env_rmse`: bare 0.0809, effects 0.0902, delta -0.0093
  - `lufs_m_rmse_lu`: bare 6.9104, effects 5.6231, delta 1.2873

- pretty_midi_fallback_used_run1: `False`

- preview_untrained_ear: M-EAR-1/real-label-training-v1 verdict EAR_v1_PARTIAL (SB1 -0.209 / SB2 -0.099 / SB3 corpus-shape-degenerate; 43/80 corpus coverage) — see docs/ear_real_label_training_v1_report.md — this pipeline does NOT compute per-song ear predictions

### Song 7: band 4, sha `42f585b439ef32ee`

- relpath: `corpus/ratings/4/012__XKQNJzquduI__Frank_Ocean_-_Provider.mp3`
- file_sha256: `42f585b439ef32eeb7daab49e7cbc80bfadd340d4bfc56700834f97da07bd9d6`
- run1 wall_clock_s: 82.31
- run2 wall_clock_s: 81.79
- run1_failed_stage: `None`
- byte-determinism x 2 (all 4 anchors): **yes**

| anchor | run1 sha[:16] | run2 sha[:16] | equal |
|--------|---------------|---------------|-------|
| `06_score/merged.midi` | `dd6d4cd9338d6b60` | `dd6d4cd9338d6b60` | yes |
| `06_score/merged.musicxml` | `10b87d9796c85ba9` | `10b87d9796c85ba9` | yes |
| `07_render/bare_midi.wav` | `8fa77c4d44488c0f` | `8fa77c4d44488c0f` | yes |
| `07_render/effects.wav` | `7754200dc0455e0a` | `7754200dc0455e0a` | yes |

- M-TEX-1 panel deltas (bare − effects; positive = effects narrows the gap):
  - `mel_l1_db`: bare 20.7675, effects 16.2271, delta **4.5403**
  - `spectral_centroid_rmse_hz`: bare 2230.7095, effects 2242.0917, delta -11.3822
  - `rms_env_rmse`: bare 0.0666, effects 0.0685, delta -0.0018
  - `lufs_m_rmse_lu`: bare 5.3827, effects 8.3670, delta -2.9843

- pretty_midi_fallback_used_run1: `False`

- preview_untrained_ear: M-EAR-1/real-label-training-v1 verdict EAR_v1_PARTIAL (SB1 -0.209 / SB2 -0.099 / SB3 corpus-shape-degenerate; 43/80 corpus coverage) — see docs/ear_real_label_training_v1_report.md — this pipeline does NOT compute per-song ear predictions

### Song 8: band 7, sha `467fbeb2e3b019a0`

- relpath: `corpus/ratings/7/005__LOCAL__Wizkid_-_Essence_ft._Tems.mp3`
- file_sha256: `467fbeb2e3b019a04035dabe262d95f4fa65ef44a0afc6b7e2f6f6d30771427d`
- run1 wall_clock_s: 85.95
- run2 wall_clock_s: 83.43
- run1_failed_stage: `None`
- byte-determinism x 2 (all 4 anchors): **yes**

| anchor | run1 sha[:16] | run2 sha[:16] | equal |
|--------|---------------|---------------|-------|
| `06_score/merged.midi` | `018684910cab1ccb` | `018684910cab1ccb` | yes |
| `06_score/merged.musicxml` | `7d1c581394322c2a` | `7d1c581394322c2a` | yes |
| `07_render/bare_midi.wav` | `e28d71beb74c8e07` | `e28d71beb74c8e07` | yes |
| `07_render/effects.wav` | `3af631776eb374c5` | `3af631776eb374c5` | yes |

- M-TEX-1 panel deltas (bare − effects; positive = effects narrows the gap):
  - `mel_l1_db`: bare 18.2614, effects 13.1080, delta **5.1534**
  - `spectral_centroid_rmse_hz`: bare 2077.4636, effects 2015.7422, delta 61.7213
  - `rms_env_rmse`: bare 0.1936, effects 0.1693, delta 0.0243
  - `lufs_m_rmse_lu`: bare 6.6924, effects 7.6729, delta -0.9805

- pretty_midi_fallback_used_run1: `False`

- preview_untrained_ear: M-EAR-1/real-label-training-v1 verdict EAR_v1_PARTIAL (SB1 -0.209 / SB2 -0.099 / SB3 corpus-shape-degenerate; 43/80 corpus coverage) — see docs/ear_real_label_training_v1_report.md — this pipeline does NOT compute per-song ear predictions

### Song 9: band 5, sha `46eb16d39cf8bb61`

- relpath: `corpus/ratings/5/010__olwAPZ9L1io__Yesterday.mp3`
- file_sha256: `46eb16d39cf8bb6113681a6fc0957205bfad7f7311661cf6e749bce1674e80d1`
- run1 wall_clock_s: 90.39
- run2 wall_clock_s: 89.59
- run1_failed_stage: `None`
- byte-determinism x 2 (all 4 anchors): **yes**

| anchor | run1 sha[:16] | run2 sha[:16] | equal |
|--------|---------------|---------------|-------|
| `06_score/merged.midi` | `3f6648ae40fb8de4` | `3f6648ae40fb8de4` | yes |
| `06_score/merged.musicxml` | `e3c8f7f0aeab3c92` | `e3c8f7f0aeab3c92` | yes |
| `07_render/bare_midi.wav` | `be8e85d85ed83fc8` | `be8e85d85ed83fc8` | yes |
| `07_render/effects.wav` | `d9aada9cbf7886e0` | `d9aada9cbf7886e0` | yes |

- M-TEX-1 panel deltas (bare − effects; positive = effects narrows the gap):
  - `mel_l1_db`: bare 14.3334, effects 9.1375, delta **5.1959**
  - `spectral_centroid_rmse_hz`: bare 1453.9579, effects 1269.4823, delta 184.4756
  - `rms_env_rmse`: bare 0.1093, effects 0.1071, delta 0.0021
  - `lufs_m_rmse_lu`: bare 10.7723, effects 7.9175, delta 2.8548

- pretty_midi_fallback_used_run1: `False`

- preview_untrained_ear: M-EAR-1/real-label-training-v1 verdict EAR_v1_PARTIAL (SB1 -0.209 / SB2 -0.099 / SB3 corpus-shape-degenerate; 43/80 corpus coverage) — see docs/ear_real_label_training_v1_report.md — this pipeline does NOT compute per-song ear predictions

### Song 10: band 4, sha `49956e7d3d507769`

- relpath: `corpus/ratings/4/014__QReOON-c6-4__Lucy_Pearl_-_Dance_Tonight.mp3`
- file_sha256: `49956e7d3d5077696997ad3ee1891a320fce798abf9177d99466e02a3f9a7bbc`
- run1 wall_clock_s: 86.27
- run2 wall_clock_s: 85.12
- run1_failed_stage: `None`
- byte-determinism x 2 (all 4 anchors): **yes**

| anchor | run1 sha[:16] | run2 sha[:16] | equal |
|--------|---------------|---------------|-------|
| `06_score/merged.midi` | `f3dae35a9ed5d28b` | `f3dae35a9ed5d28b` | yes |
| `06_score/merged.musicxml` | `25df3129e5a4e209` | `25df3129e5a4e209` | yes |
| `07_render/bare_midi.wav` | `3a42c9592fa4e625` | `3a42c9592fa4e625` | yes |
| `07_render/effects.wav` | `dbd45cf3e8c2de30` | `dbd45cf3e8c2de30` | yes |

- M-TEX-1 panel deltas (bare − effects; positive = effects narrows the gap):
  - `mel_l1_db`: bare 16.1113, effects 12.8345, delta **3.2768**
  - `spectral_centroid_rmse_hz`: bare 2578.5925, effects 2506.9473, delta 71.6452
  - `rms_env_rmse`: bare 0.0619, effects 0.0486, delta 0.0133
  - `lufs_m_rmse_lu`: bare 10.0720, effects 7.3019, delta 2.7701

- pretty_midi_fallback_used_run1: `False`

- preview_untrained_ear: M-EAR-1/real-label-training-v1 verdict EAR_v1_PARTIAL (SB1 -0.209 / SB2 -0.099 / SB3 corpus-shape-degenerate; 43/80 corpus coverage) — see docs/ear_real_label_training_v1_report.md — this pipeline does NOT compute per-song ear predictions

### Song 11: band 5, sha `51e433ade2a845e1`

- relpath: `corpus/ratings/5/012__gPp2KBV9zXk__Dojo_Cuts_-_Rome.mp3`
- file_sha256: `51e433ade2a845e10a56e0bc61be034bae0d19f9a98f930ef3669612f2cce4e6`
- run1 wall_clock_s: 84.37
- run2 wall_clock_s: 82.51
- run1_failed_stage: `None`
- byte-determinism x 2 (all 4 anchors): **yes**

| anchor | run1 sha[:16] | run2 sha[:16] | equal |
|--------|---------------|---------------|-------|
| `06_score/merged.midi` | `c1654067d9303bac` | `c1654067d9303bac` | yes |
| `06_score/merged.musicxml` | `51ea2241a9fdb0a7` | `51ea2241a9fdb0a7` | yes |
| `07_render/bare_midi.wav` | `32e70486a2aca424` | `32e70486a2aca424` | yes |
| `07_render/effects.wav` | `37952c157ffdb09c` | `37952c157ffdb09c` | yes |

- M-TEX-1 panel deltas (bare − effects; positive = effects narrows the gap):
  - `mel_l1_db`: bare 20.2763, effects 13.0732, delta **7.2030**
  - `spectral_centroid_rmse_hz`: bare 1818.6346, effects 1697.2752, delta 121.3594
  - `rms_env_rmse`: bare 0.1120, effects 0.1247, delta -0.0127
  - `lufs_m_rmse_lu`: bare 9.3660, effects 10.1310, delta -0.7650

- pretty_midi_fallback_used_run1: `False`

- preview_untrained_ear: M-EAR-1/real-label-training-v1 verdict EAR_v1_PARTIAL (SB1 -0.209 / SB2 -0.099 / SB3 corpus-shape-degenerate; 43/80 corpus coverage) — see docs/ear_real_label_training_v1_report.md — this pipeline does NOT compute per-song ear predictions

### Song 12: band 6, sha `5420adb139cae8db`

- relpath: `corpus/ratings/6/004__KXdW0g6jAxE__Anderson_.Paak_-_The_Bird.mp3`
- file_sha256: `5420adb139cae8dba783790068c3ad59e57cd3e36727bdd014586e8521421e76`
- run1 wall_clock_s: 76.84
- run2 wall_clock_s: 75.63
- run1_failed_stage: `None`
- byte-determinism x 2 (all 4 anchors): **yes**

| anchor | run1 sha[:16] | run2 sha[:16] | equal |
|--------|---------------|---------------|-------|
| `06_score/merged.midi` | `a20f3005cadae172` | `a20f3005cadae172` | yes |
| `06_score/merged.musicxml` | `7d8e6469f415acd5` | `7d8e6469f415acd5` | yes |
| `07_render/bare_midi.wav` | `948fb99038a1e19f` | `948fb99038a1e19f` | yes |
| `07_render/effects.wav` | `344451faa5040041` | `344451faa5040041` | yes |

- M-TEX-1 panel deltas (bare − effects; positive = effects narrows the gap):
  - `mel_l1_db`: bare 23.6491, effects 19.7473, delta **3.9018**
  - `spectral_centroid_rmse_hz`: bare 3032.2312, effects 3104.0271, delta -71.7959
  - `rms_env_rmse`: bare 0.2312, effects 0.2193, delta 0.0119
  - `lufs_m_rmse_lu`: bare 18.6091, effects 15.2985, delta 3.3105

- pretty_midi_fallback_used_run1: `False`

- preview_untrained_ear: M-EAR-1/real-label-training-v1 verdict EAR_v1_PARTIAL (SB1 -0.209 / SB2 -0.099 / SB3 corpus-shape-degenerate; 43/80 corpus coverage) — see docs/ear_real_label_training_v1_report.md — this pipeline does NOT compute per-song ear predictions

### Song 13: band 6, sha `6edf398477b3fb73`

- relpath: `corpus/ratings/6/021__O_HoOpJ60C0__Charli_xcx_-_360.mp3`
- file_sha256: `6edf398477b3fb73c336c7be7c417e19e4ea86780726e4f9635adc690b174fab`
- run1 wall_clock_s: 76.38
- run2 wall_clock_s: 77.08
- run1_failed_stage: `None`
- byte-determinism x 2 (all 4 anchors): **yes**

| anchor | run1 sha[:16] | run2 sha[:16] | equal |
|--------|---------------|---------------|-------|
| `06_score/merged.midi` | `ae1878913099bddc` | `ae1878913099bddc` | yes |
| `06_score/merged.musicxml` | `781ac7bcc29e65f6` | `781ac7bcc29e65f6` | yes |
| `07_render/bare_midi.wav` | `4c38555a0beb8530` | `4c38555a0beb8530` | yes |
| `07_render/effects.wav` | `a5b395525dcee33b` | `a5b395525dcee33b` | yes |

- M-TEX-1 panel deltas (bare − effects; positive = effects narrows the gap):
  - `mel_l1_db`: bare 18.9904, effects 13.8450, delta **5.1453**
  - `spectral_centroid_rmse_hz`: bare 1562.9336, effects 1469.1466, delta 93.7870
  - `rms_env_rmse`: bare 0.2455, effects 0.2085, delta 0.0370
  - `lufs_m_rmse_lu`: bare 12.1670, effects 9.0124, delta 3.1546

- pretty_midi_fallback_used_run1: `False`

- preview_untrained_ear: M-EAR-1/real-label-training-v1 verdict EAR_v1_PARTIAL (SB1 -0.209 / SB2 -0.099 / SB3 corpus-shape-degenerate; 43/80 corpus coverage) — see docs/ear_real_label_training_v1_report.md — this pipeline does NOT compute per-song ear predictions

### Song 14: band 4, sha `733ab58ee9bf7029`

- relpath: `corpus/ratings/4/007__1gX1EP6mG-E__Old_Crow_Medicine_Show_-_Wagon_Wheel.mp3`
- file_sha256: `733ab58ee9bf7029439902265abf0a0fd06d99063a164f23ead7201ca8e49b01`
- run1 wall_clock_s: 82.33
- run2 wall_clock_s: 84.78
- run1_failed_stage: `None`
- byte-determinism x 2 (all 4 anchors): **yes**

| anchor | run1 sha[:16] | run2 sha[:16] | equal |
|--------|---------------|---------------|-------|
| `06_score/merged.midi` | `33cf4b3708be369d` | `33cf4b3708be369d` | yes |
| `06_score/merged.musicxml` | `fb923d0853f9e5d0` | `fb923d0853f9e5d0` | yes |
| `07_render/bare_midi.wav` | `05b0d8869d338664` | `05b0d8869d338664` | yes |
| `07_render/effects.wav` | `2b1c02002eb07477` | `2b1c02002eb07477` | yes |

- M-TEX-1 panel deltas (bare − effects; positive = effects narrows the gap):
  - `mel_l1_db`: bare 11.6256, effects 10.2958, delta **1.3298**
  - `spectral_centroid_rmse_hz`: bare 1263.5111, effects 1201.7000, delta 61.8112
  - `rms_env_rmse`: bare 0.0480, effects 0.0940, delta -0.0460
  - `lufs_m_rmse_lu`: bare 8.5062, effects 9.0434, delta -0.5372

- pretty_midi_fallback_used_run1: `False`

- preview_untrained_ear: M-EAR-1/real-label-training-v1 verdict EAR_v1_PARTIAL (SB1 -0.209 / SB2 -0.099 / SB3 corpus-shape-degenerate; 43/80 corpus coverage) — see docs/ear_real_label_training_v1_report.md — this pipeline does NOT compute per-song ear predictions

### Song 15: band 6, sha `78bdd2ce2fc5c1af`

- relpath: `corpus/ratings/6/023__rqScfATfNnc__FKJ_-_10_Years_Ago.mp3`
- file_sha256: `78bdd2ce2fc5c1affdc9806e532ae5e9cbd0dc6a7b0e275ff1980ec8160c6e38`
- run1 wall_clock_s: 81.26
- run2 wall_clock_s: 82.32
- run1_failed_stage: `None`
- byte-determinism x 2 (all 4 anchors): **yes**

| anchor | run1 sha[:16] | run2 sha[:16] | equal |
|--------|---------------|---------------|-------|
| `06_score/merged.midi` | `2013de7c111e713e` | `2013de7c111e713e` | yes |
| `06_score/merged.musicxml` | `90507b16428fb54e` | `90507b16428fb54e` | yes |
| `07_render/bare_midi.wav` | `f36b015144edd5c0` | `f36b015144edd5c0` | yes |
| `07_render/effects.wav` | `b8993e0639b50e40` | `b8993e0639b50e40` | yes |

- M-TEX-1 panel deltas (bare − effects; positive = effects narrows the gap):
  - `mel_l1_db`: bare 10.7819, effects 12.1232, delta **-1.3412**
  - `spectral_centroid_rmse_hz`: bare 1321.0808, effects 539.5493, delta 781.5315
  - `rms_env_rmse`: bare 0.0293, effects 0.1072, delta -0.0779
  - `lufs_m_rmse_lu`: bare 7.0059, effects 8.9839, delta -1.9780

- pretty_midi_fallback_used_run1: `False`

- preview_untrained_ear: M-EAR-1/real-label-training-v1 verdict EAR_v1_PARTIAL (SB1 -0.209 / SB2 -0.099 / SB3 corpus-shape-degenerate; 43/80 corpus coverage) — see docs/ear_real_label_training_v1_report.md — this pipeline does NOT compute per-song ear predictions

### Song 16: band 7, sha `7e6b59b873ed8972`

- relpath: `corpus/ratings/7/013__LOCAL__I_Found_My_Smile_Again_Radio_Edit.mp3`
- file_sha256: `7e6b59b873ed8972c9770b8ff73e0072decfcab70f23346f17de42cc2e606a8b`
- run1 wall_clock_s: 77.89
- run2 wall_clock_s: 79.29
- run1_failed_stage: `None`
- byte-determinism x 2 (all 4 anchors): **yes**

| anchor | run1 sha[:16] | run2 sha[:16] | equal |
|--------|---------------|---------------|-------|
| `06_score/merged.midi` | `128a37d92dcd2d90` | `128a37d92dcd2d90` | yes |
| `06_score/merged.musicxml` | `e99c04bbcc7544e4` | `e99c04bbcc7544e4` | yes |
| `07_render/bare_midi.wav` | `e9380255654d934e` | `e9380255654d934e` | yes |
| `07_render/effects.wav` | `eaf4f4af5e7fcf92` | `eaf4f4af5e7fcf92` | yes |

- M-TEX-1 panel deltas (bare − effects; positive = effects narrows the gap):
  - `mel_l1_db`: bare 30.6094, effects 21.4274, delta **9.1820**
  - `spectral_centroid_rmse_hz`: bare 2548.8178, effects 2791.2293, delta -242.4116
  - `rms_env_rmse`: bare 0.1841, effects 0.1734, delta 0.0106
  - `lufs_m_rmse_lu`: bare 18.2530, effects 16.3570, delta 1.8960

- pretty_midi_fallback_used_run1: `False`

- preview_untrained_ear: M-EAR-1/real-label-training-v1 verdict EAR_v1_PARTIAL (SB1 -0.209 / SB2 -0.099 / SB3 corpus-shape-degenerate; 43/80 corpus coverage) — see docs/ear_real_label_training_v1_report.md — this pipeline does NOT compute per-song ear predictions

### Song 17: band 5, sha `822e8e5c5bf12c05`

- relpath: `corpus/ratings/5/030__fcNKG_isFgg__Windows.mp3`
- file_sha256: `822e8e5c5bf12c05da7cfbdedab45b94fad5a4368662f3d8b6ccb2d67ab25336`
- run1 wall_clock_s: 82.86
- run2 wall_clock_s: 81.94
- run1_failed_stage: `None`
- byte-determinism x 2 (all 4 anchors): **yes**

| anchor | run1 sha[:16] | run2 sha[:16] | equal |
|--------|---------------|---------------|-------|
| `06_score/merged.midi` | `877764d5bfd28362` | `877764d5bfd28362` | yes |
| `06_score/merged.musicxml` | `520777e082e52526` | `520777e082e52526` | yes |
| `07_render/bare_midi.wav` | `fd0c165d273f7588` | `fd0c165d273f7588` | yes |
| `07_render/effects.wav` | `2f3ba90acef10da6` | `2f3ba90acef10da6` | yes |

- M-TEX-1 panel deltas (bare − effects; positive = effects narrows the gap):
  - `mel_l1_db`: bare 16.1980, effects 12.0791, delta **4.1189**
  - `spectral_centroid_rmse_hz`: bare 2468.7392, effects 2619.6001, delta -150.8609
  - `rms_env_rmse`: bare 0.0504, effects 0.0853, delta -0.0349
  - `lufs_m_rmse_lu`: bare 16.0701, effects 12.3816, delta 3.6885

- pretty_midi_fallback_used_run1: `False`

- preview_untrained_ear: M-EAR-1/real-label-training-v1 verdict EAR_v1_PARTIAL (SB1 -0.209 / SB2 -0.099 / SB3 corpus-shape-degenerate; 43/80 corpus coverage) — see docs/ear_real_label_training_v1_report.md — this pipeline does NOT compute per-song ear predictions

### Song 18: band 6, sha `88d247468cb6d49f`

- relpath: `corpus/ratings/6/015__wXvX1vOe0rQ__Peach_Dream.mp3`
- file_sha256: `88d247468cb6d49f3c209ff91a968c9a19e05b9a0d5db4fdcdb12a8dcc697862`
- run1 wall_clock_s: 80.40
- run2 wall_clock_s: 80.34
- run1_failed_stage: `None`
- byte-determinism x 2 (all 4 anchors): **yes**

| anchor | run1 sha[:16] | run2 sha[:16] | equal |
|--------|---------------|---------------|-------|
| `06_score/merged.midi` | `10a7d89fe3d96543` | `10a7d89fe3d96543` | yes |
| `06_score/merged.musicxml` | `f292b435b871734a` | `f292b435b871734a` | yes |
| `07_render/bare_midi.wav` | `788cfb94d46e95f2` | `788cfb94d46e95f2` | yes |
| `07_render/effects.wav` | `755dfa20128a41fb` | `755dfa20128a41fb` | yes |

- M-TEX-1 panel deltas (bare − effects; positive = effects narrows the gap):
  - `mel_l1_db`: bare 24.8351, effects 17.8505, delta **6.9846**
  - `spectral_centroid_rmse_hz`: bare 1605.3222, effects 1532.4300, delta 72.8923
  - `rms_env_rmse`: bare 0.1728, effects 0.1625, delta 0.0103
  - `lufs_m_rmse_lu`: bare 15.4240, effects 12.9902, delta 2.4338

- pretty_midi_fallback_used_run1: `False`

- preview_untrained_ear: M-EAR-1/real-label-training-v1 verdict EAR_v1_PARTIAL (SB1 -0.209 / SB2 -0.099 / SB3 corpus-shape-degenerate; 43/80 corpus coverage) — see docs/ear_real_label_training_v1_report.md — this pipeline does NOT compute per-song ear predictions

### Song 19: band 4, sha `8b6dc92b73b3877a`

- relpath: `corpus/ratings/4/001__pz650EkJFKc__Hector_Lavoe_-_Aguanile.mp3`
- file_sha256: `8b6dc92b73b3877a837448ed5b68ee838a2f16e99992842bed00f245aa3d000d`
- run1 wall_clock_s: 77.72
- run2 wall_clock_s: 76.49
- run1_failed_stage: `None`
- byte-determinism x 2 (all 4 anchors): **yes**

| anchor | run1 sha[:16] | run2 sha[:16] | equal |
|--------|---------------|---------------|-------|
| `06_score/merged.midi` | `7c8a02a73564c9a9` | `7c8a02a73564c9a9` | yes |
| `06_score/merged.musicxml` | `6ea9c12047cebbb5` | `6ea9c12047cebbb5` | yes |
| `07_render/bare_midi.wav` | `b13f9365ed34511a` | `b13f9365ed34511a` | yes |
| `07_render/effects.wav` | `d63e1f1e89428130` | `d63e1f1e89428130` | yes |

- M-TEX-1 panel deltas (bare − effects; positive = effects narrows the gap):
  - `mel_l1_db`: bare 28.6397, effects 21.6301, delta **7.0096**
  - `spectral_centroid_rmse_hz`: bare 2392.2952, effects 1577.4687, delta 814.8265
  - `rms_env_rmse`: bare 0.0497, effects 0.0457, delta 0.0040
  - `lufs_m_rmse_lu`: bare 19.8360, effects 17.3202, delta 2.5158

- pretty_midi_fallback_used_run1: `False`

- preview_untrained_ear: M-EAR-1/real-label-training-v1 verdict EAR_v1_PARTIAL (SB1 -0.209 / SB2 -0.099 / SB3 corpus-shape-degenerate; 43/80 corpus coverage) — see docs/ear_real_label_training_v1_report.md — this pipeline does NOT compute per-song ear predictions

### Song 20: band 4, sha `a0979974ee89e398`

- relpath: `corpus/ratings/4/006__gFGqiwA5gTc__Whitney_-_FTA.mp3`
- file_sha256: `a0979974ee89e398cf4d6da58882e0721da6fb6e8a0bc706074c456cf6bfba5b`
- run1 wall_clock_s: 79.93
- run2 wall_clock_s: 79.64
- run1_failed_stage: `None`
- byte-determinism x 2 (all 4 anchors): **yes**

| anchor | run1 sha[:16] | run2 sha[:16] | equal |
|--------|---------------|---------------|-------|
| `06_score/merged.midi` | `206ae184c0b06d89` | `206ae184c0b06d89` | yes |
| `06_score/merged.musicxml` | `a51a93d676e15566` | `a51a93d676e15566` | yes |
| `07_render/bare_midi.wav` | `04ec8501dc587630` | `04ec8501dc587630` | yes |
| `07_render/effects.wav` | `fe1741e75db54dd6` | `fe1741e75db54dd6` | yes |

- M-TEX-1 panel deltas (bare − effects; positive = effects narrows the gap):
  - `mel_l1_db`: bare 12.9119, effects 9.0613, delta **3.8505**
  - `spectral_centroid_rmse_hz`: bare 946.5869, effects 480.5609, delta 466.0260
  - `rms_env_rmse`: bare 0.0350, effects 0.0326, delta 0.0024
  - `lufs_m_rmse_lu`: bare 9.9881, effects 10.9644, delta -0.9763

- pretty_midi_fallback_used_run1: `False`

- preview_untrained_ear: M-EAR-1/real-label-training-v1 verdict EAR_v1_PARTIAL (SB1 -0.209 / SB2 -0.099 / SB3 corpus-shape-degenerate; 43/80 corpus coverage) — see docs/ear_real_label_training_v1_report.md — this pipeline does NOT compute per-song ear predictions

### Song 21: band 5, sha `a4e6ab346837dbd4`

- relpath: `corpus/ratings/5/016__c7BxiPq_6Ok__Cerca_De_Ti.mp3`
- file_sha256: `a4e6ab346837dbd4ef6fcd5f84165dc7e89fa6832e802d03c4e907ea002e65ab`
- run1 wall_clock_s: 85.95
- run2 wall_clock_s: 83.05
- run1_failed_stage: `None`
- byte-determinism x 2 (all 4 anchors): **yes**

| anchor | run1 sha[:16] | run2 sha[:16] | equal |
|--------|---------------|---------------|-------|
| `06_score/merged.midi` | `b14523866248a0a4` | `b14523866248a0a4` | yes |
| `06_score/merged.musicxml` | `096f19b13eb92472` | `096f19b13eb92472` | yes |
| `07_render/bare_midi.wav` | `c99bfc3447d5ab21` | `c99bfc3447d5ab21` | yes |
| `07_render/effects.wav` | `21fc25e8b88c3f3a` | `21fc25e8b88c3f3a` | yes |

- M-TEX-1 panel deltas (bare − effects; positive = effects narrows the gap):
  - `mel_l1_db`: bare 12.5345, effects 9.2957, delta **3.2388**
  - `spectral_centroid_rmse_hz`: bare 1723.6775, effects 651.2803, delta 1072.3972
  - `rms_env_rmse`: bare 0.1085, effects 0.0886, delta 0.0199
  - `lufs_m_rmse_lu`: bare 7.9606, effects 6.4437, delta 1.5169

- pretty_midi_fallback_used_run1: `False`

- preview_untrained_ear: M-EAR-1/real-label-training-v1 verdict EAR_v1_PARTIAL (SB1 -0.209 / SB2 -0.099 / SB3 corpus-shape-degenerate; 43/80 corpus coverage) — see docs/ear_real_label_training_v1_report.md — this pipeline does NOT compute per-song ear predictions

### Song 22: band 7, sha `a9587ccde1b333f5`

- relpath: `corpus/ratings/7/019__LOCAL__Hiatus_Kaiyote_-_Molasses.mp3`
- file_sha256: `a9587ccde1b333f561c727dce5175136a55a8dd724390e9cf83d95287c1389ac`
- run1 wall_clock_s: 90.95
- run2 wall_clock_s: 92.61
- run1_failed_stage: `None`
- byte-determinism x 2 (all 4 anchors): **yes**

| anchor | run1 sha[:16] | run2 sha[:16] | equal |
|--------|---------------|---------------|-------|
| `06_score/merged.midi` | `296fc9199aae2878` | `296fc9199aae2878` | yes |
| `06_score/merged.musicxml` | `84f47a1cfdd60bf9` | `84f47a1cfdd60bf9` | yes |
| `07_render/bare_midi.wav` | `b4045b36a00fcb35` | `b4045b36a00fcb35` | yes |
| `07_render/effects.wav` | `b491fddbe185400b` | `b491fddbe185400b` | yes |

- M-TEX-1 panel deltas (bare − effects; positive = effects narrows the gap):
  - `mel_l1_db`: bare 12.3433, effects 9.5045, delta **2.8388**
  - `spectral_centroid_rmse_hz`: bare 1466.9166, effects 1155.7757, delta 311.1409
  - `rms_env_rmse`: bare 0.0785, effects 0.1271, delta -0.0486
  - `lufs_m_rmse_lu`: bare 11.4783, effects 9.7600, delta 1.7183

- pretty_midi_fallback_used_run1: `False`

- preview_untrained_ear: M-EAR-1/real-label-training-v1 verdict EAR_v1_PARTIAL (SB1 -0.209 / SB2 -0.099 / SB3 corpus-shape-degenerate; 43/80 corpus coverage) — see docs/ear_real_label_training_v1_report.md — this pipeline does NOT compute per-song ear predictions

### Song 23: band 4, sha `a97f83cba25037b6`

- relpath: `corpus/ratings/4/011__8Ee4QjCEHHc__Calvin_Harris_-_Slide_ft._Frank_Ocean_Migos.mp3`
- file_sha256: `a97f83cba25037b6e53de150dd2cac32ca383dc2d97680253d00679f4aa01c9f`
- run1 wall_clock_s: 86.36
- run2 wall_clock_s: 88.68
- run1_failed_stage: `None`
- byte-determinism x 2 (all 4 anchors): **yes**

| anchor | run1 sha[:16] | run2 sha[:16] | equal |
|--------|---------------|---------------|-------|
| `06_score/merged.midi` | `43bbad379c102cba` | `43bbad379c102cba` | yes |
| `06_score/merged.musicxml` | `d111bcc4a4a1fa05` | `d111bcc4a4a1fa05` | yes |
| `07_render/bare_midi.wav` | `dbf8c569e2b8997b` | `dbf8c569e2b8997b` | yes |
| `07_render/effects.wav` | `fa68d424c7ef26ce` | `fa68d424c7ef26ce` | yes |

- M-TEX-1 panel deltas (bare − effects; positive = effects narrows the gap):
  - `mel_l1_db`: bare 11.7184, effects 9.5708, delta **2.1477**
  - `spectral_centroid_rmse_hz`: bare 1286.9266, effects 948.6746, delta 338.2520
  - `rms_env_rmse`: bare 0.0391, effects 0.0702, delta -0.0310
  - `lufs_m_rmse_lu`: bare 2.8194, effects 4.6677, delta -1.8483

- pretty_midi_fallback_used_run1: `False`

- preview_untrained_ear: M-EAR-1/real-label-training-v1 verdict EAR_v1_PARTIAL (SB1 -0.209 / SB2 -0.099 / SB3 corpus-shape-degenerate; 43/80 corpus coverage) — see docs/ear_real_label_training_v1_report.md — this pipeline does NOT compute per-song ear predictions

### Song 24: band 7, sha `ae1b65eaf1560951`

- relpath: `corpus/ratings/7/020__LOCAL__Shaolin_Monk_Motherfunk_Nai_Palm_Commentary.mp3`
- file_sha256: `ae1b65eaf15609510665d7f3f059b166fc9a11fdc330b5d057b5ede98a8d175e`
- run1 wall_clock_s: 76.45
- run2 wall_clock_s: 75.64
- run1_failed_stage: `None`
- byte-determinism x 2 (all 4 anchors): **yes**

| anchor | run1 sha[:16] | run2 sha[:16] | equal |
|--------|---------------|---------------|-------|
| `06_score/merged.midi` | `c942f9ac3bbcc965` | `c942f9ac3bbcc965` | yes |
| `06_score/merged.musicxml` | `05f26cf8a5a55296` | `05f26cf8a5a55296` | yes |
| `07_render/bare_midi.wav` | `b944961d1cedc587` | `b944961d1cedc587` | yes |
| `07_render/effects.wav` | `ccce397cc92a2c01` | `ccce397cc92a2c01` | yes |

- M-TEX-1 panel deltas (bare − effects; positive = effects narrows the gap):
  - `mel_l1_db`: bare 14.7038, effects 13.5352, delta **1.1686**
  - `spectral_centroid_rmse_hz`: bare 3016.9923, effects 3665.5833, delta -648.5910
  - `rms_env_rmse`: bare 0.0127, effects 0.0223, delta -0.0096
  - `lufs_m_rmse_lu`: bare 12.4418, effects 12.6894, delta -0.2476

- pretty_midi_fallback_used_run1: `False`

- preview_untrained_ear: M-EAR-1/real-label-training-v1 verdict EAR_v1_PARTIAL (SB1 -0.209 / SB2 -0.099 / SB3 corpus-shape-degenerate; 43/80 corpus coverage) — see docs/ear_real_label_training_v1_report.md — this pipeline does NOT compute per-song ear predictions

### Song 25: band 7, sha `b8a030a4264a7aba`

- relpath: `corpus/ratings/7/010__LOCAL__Samba_De_Raiz_-_Conselho.mp3`
- file_sha256: `b8a030a4264a7abaacbad1216f1cfa9b15af5f8789f264137f898ed962ce74be`
- run1 wall_clock_s: 81.76
- run2 wall_clock_s: 78.49
- run1_failed_stage: `None`
- byte-determinism x 2 (all 4 anchors): **yes**

| anchor | run1 sha[:16] | run2 sha[:16] | equal |
|--------|---------------|---------------|-------|
| `06_score/merged.midi` | `1d951cb15d9fec01` | `1d951cb15d9fec01` | yes |
| `06_score/merged.musicxml` | `b4e7140b2f0fa4bb` | `b4e7140b2f0fa4bb` | yes |
| `07_render/bare_midi.wav` | `31d55b5f19cd6fa1` | `31d55b5f19cd6fa1` | yes |
| `07_render/effects.wav` | `f1f6e8024a43e830` | `f1f6e8024a43e830` | yes |

- M-TEX-1 panel deltas (bare − effects; positive = effects narrows the gap):
  - `mel_l1_db`: bare 28.0398, effects 19.5866, delta **8.4532**
  - `spectral_centroid_rmse_hz`: bare 3047.5208, effects 3041.4940, delta 6.0268
  - `rms_env_rmse`: bare 0.0693, effects 0.0772, delta -0.0079
  - `lufs_m_rmse_lu`: bare 9.0746, effects 8.1212, delta 0.9534

- pretty_midi_fallback_used_run1: `False`

- preview_untrained_ear: M-EAR-1/real-label-training-v1 verdict EAR_v1_PARTIAL (SB1 -0.209 / SB2 -0.099 / SB3 corpus-shape-degenerate; 43/80 corpus coverage) — see docs/ear_real_label_training_v1_report.md — this pipeline does NOT compute per-song ear predictions

### Song 26: band 7, sha `b8ae0217bb9660d8`

- relpath: `corpus/ratings/7/015__LOCAL__Bruno_Berle_-_Som_Nyame.mp3`
- file_sha256: `b8ae0217bb9660d8263ca67568c0173d66b37adfe9c8de60dc1c4e49607b9760`
- run1 wall_clock_s: 75.82
- run2 wall_clock_s: 75.95
- run1_failed_stage: `None`
- byte-determinism x 2 (all 4 anchors): **yes**

| anchor | run1 sha[:16] | run2 sha[:16] | equal |
|--------|---------------|---------------|-------|
| `06_score/merged.midi` | `3f515b0d74798525` | `3f515b0d74798525` | yes |
| `06_score/merged.musicxml` | `922eac95b65f3c13` | `922eac95b65f3c13` | yes |
| `07_render/bare_midi.wav` | `126ceb861357273f` | `126ceb861357273f` | yes |
| `07_render/effects.wav` | `abf8056ef6b451ca` | `abf8056ef6b451ca` | yes |

- M-TEX-1 panel deltas (bare − effects; positive = effects narrows the gap):
  - `mel_l1_db`: bare 24.2591, effects 17.9600, delta **6.2991**
  - `spectral_centroid_rmse_hz`: bare 1397.5795, effects 636.3689, delta 761.2106
  - `rms_env_rmse`: bare 0.1861, effects 0.1742, delta 0.0119
  - `lufs_m_rmse_lu`: bare 13.2210, effects 15.2171, delta -1.9961

- pretty_midi_fallback_used_run1: `False`

- preview_untrained_ear: M-EAR-1/real-label-training-v1 verdict EAR_v1_PARTIAL (SB1 -0.209 / SB2 -0.099 / SB3 corpus-shape-degenerate; 43/80 corpus coverage) — see docs/ear_real_label_training_v1_report.md — this pipeline does NOT compute per-song ear predictions

### Song 27: band 4, sha `bed1a8f2315bc877`

- relpath: `corpus/ratings/4/008__5gJmpjRm1RA__Cordae_-_Summer_Drop_ft._Anderson_.Paak.mp3`
- file_sha256: `bed1a8f2315bc877bb95a2401bb5c6fd2279365cce9d98ab95c2cbd080e08cf1`
- run1 wall_clock_s: 78.24
- run2 wall_clock_s: 76.28
- run1_failed_stage: `None`
- byte-determinism x 2 (all 4 anchors): **yes**

| anchor | run1 sha[:16] | run2 sha[:16] | equal |
|--------|---------------|---------------|-------|
| `06_score/merged.midi` | `bc32239ad7c08dbc` | `bc32239ad7c08dbc` | yes |
| `06_score/merged.musicxml` | `2e9d982eaf2ad05a` | `2e9d982eaf2ad05a` | yes |
| `07_render/bare_midi.wav` | `c792507bc09ef0c8` | `c792507bc09ef0c8` | yes |
| `07_render/effects.wav` | `7de3770dfbb8c816` | `7de3770dfbb8c816` | yes |

- M-TEX-1 panel deltas (bare − effects; positive = effects narrows the gap):
  - `mel_l1_db`: bare 25.1447, effects 18.2273, delta **6.9175**
  - `spectral_centroid_rmse_hz`: bare 1714.5898, effects 1734.7510, delta -20.1612
  - `rms_env_rmse`: bare 0.1827, effects 0.1646, delta 0.0181
  - `lufs_m_rmse_lu`: bare 14.1966, effects 12.7260, delta 1.4706

- pretty_midi_fallback_used_run1: `False`

- preview_untrained_ear: M-EAR-1/real-label-training-v1 verdict EAR_v1_PARTIAL (SB1 -0.209 / SB2 -0.099 / SB3 corpus-shape-degenerate; 43/80 corpus coverage) — see docs/ear_real_label_training_v1_report.md — this pipeline does NOT compute per-song ear predictions

### Song 28: band 7, sha `c7d491e98767eea5`

- relpath: `corpus/ratings/7/002__LOCAL__Freedom_Interlude.mp3`
- file_sha256: `c7d491e98767eea5f58cd6ff854ff03729dc180718aa35050df2dd24c940b41a`
- run1 wall_clock_s: 82.65
- run2 wall_clock_s: 82.82
- run1_failed_stage: `None`
- byte-determinism x 2 (all 4 anchors): **yes**

| anchor | run1 sha[:16] | run2 sha[:16] | equal |
|--------|---------------|---------------|-------|
| `06_score/merged.midi` | `917b33415ec5966e` | `917b33415ec5966e` | yes |
| `06_score/merged.musicxml` | `6bb4342e6dea4bfc` | `6bb4342e6dea4bfc` | yes |
| `07_render/bare_midi.wav` | `dae54f10ca1ad972` | `dae54f10ca1ad972` | yes |
| `07_render/effects.wav` | `53c01328d968bb25` | `53c01328d968bb25` | yes |

- M-TEX-1 panel deltas (bare − effects; positive = effects narrows the gap):
  - `mel_l1_db`: bare 20.5849, effects 14.4773, delta **6.1076**
  - `spectral_centroid_rmse_hz`: bare 2232.4405, effects 1951.5885, delta 280.8520
  - `rms_env_rmse`: bare 0.1734, effects 0.1531, delta 0.0203
  - `lufs_m_rmse_lu`: bare 9.6912, effects 8.4936, delta 1.1975

- pretty_midi_fallback_used_run1: `False`

- preview_untrained_ear: M-EAR-1/real-label-training-v1 verdict EAR_v1_PARTIAL (SB1 -0.209 / SB2 -0.099 / SB3 corpus-shape-degenerate; 43/80 corpus coverage) — see docs/ear_real_label_training_v1_report.md — this pipeline does NOT compute per-song ear predictions

### Song 29: band 4, sha `cb771dae8fc3d962`

- relpath: `corpus/ratings/4/002__Bc4AezWceUc__Stay_Live.mp3`
- file_sha256: `cb771dae8fc3d962cc001af9a2763ae45c404ed67e78a09b6fae8a57d10cb460`
- run1 wall_clock_s: 87.11
- run2 wall_clock_s: 85.39
- run1_failed_stage: `None`
- byte-determinism x 2 (all 4 anchors): **yes**

| anchor | run1 sha[:16] | run2 sha[:16] | equal |
|--------|---------------|---------------|-------|
| `06_score/merged.midi` | `8d409df34abd91f6` | `8d409df34abd91f6` | yes |
| `06_score/merged.musicxml` | `3d0c637e054c7fb5` | `3d0c637e054c7fb5` | yes |
| `07_render/bare_midi.wav` | `eb16a481aa1cddd9` | `eb16a481aa1cddd9` | yes |
| `07_render/effects.wav` | `c5b750746cb0d7be` | `c5b750746cb0d7be` | yes |

- M-TEX-1 panel deltas (bare − effects; positive = effects narrows the gap):
  - `mel_l1_db`: bare 28.5211, effects 20.2498, delta **8.2713**
  - `spectral_centroid_rmse_hz`: bare 2907.6528, effects 2803.0034, delta 104.6494
  - `rms_env_rmse`: bare 0.1287, effects 0.1103, delta 0.0184
  - `lufs_m_rmse_lu`: bare 9.9566, effects 8.4000, delta 1.5566

- pretty_midi_fallback_used_run1: `False`

- preview_untrained_ear: M-EAR-1/real-label-training-v1 verdict EAR_v1_PARTIAL (SB1 -0.209 / SB2 -0.099 / SB3 corpus-shape-degenerate; 43/80 corpus coverage) — see docs/ear_real_label_training_v1_report.md — this pipeline does NOT compute per-song ear predictions

### Song 30: band 6, sha `cc0693b4a24f64b2`

- relpath: `corpus/ratings/6/008__pxAWICqgjHM__Allah-Las_-_Houston.mp3`
- file_sha256: `cc0693b4a24f64b2cfd6c818325b2c3f36296a15e3dc292ee7d569e216d9724f`
- run1 wall_clock_s: 83.35
- run2 wall_clock_s: 83.27
- run1_failed_stage: `None`
- byte-determinism x 2 (all 4 anchors): **yes**

| anchor | run1 sha[:16] | run2 sha[:16] | equal |
|--------|---------------|---------------|-------|
| `06_score/merged.midi` | `6edb9af00c8cfa5a` | `6edb9af00c8cfa5a` | yes |
| `06_score/merged.musicxml` | `6943d066b09efd22` | `6943d066b09efd22` | yes |
| `07_render/bare_midi.wav` | `8f9b6824362c325f` | `8f9b6824362c325f` | yes |
| `07_render/effects.wav` | `d412634aa24e797d` | `d412634aa24e797d` | yes |

- M-TEX-1 panel deltas (bare − effects; positive = effects narrows the gap):
  - `mel_l1_db`: bare 11.0648, effects 8.9057, delta **2.1591**
  - `spectral_centroid_rmse_hz`: bare 970.8071, effects 433.9879, delta 536.8192
  - `rms_env_rmse`: bare 0.1093, effects 0.1217, delta -0.0125
  - `lufs_m_rmse_lu`: bare 6.8621, effects 9.7829, delta -2.9207

- pretty_midi_fallback_used_run1: `False`

- preview_untrained_ear: M-EAR-1/real-label-training-v1 verdict EAR_v1_PARTIAL (SB1 -0.209 / SB2 -0.099 / SB3 corpus-shape-degenerate; 43/80 corpus coverage) — see docs/ear_real_label_training_v1_report.md — this pipeline does NOT compute per-song ear predictions

### Song 31: band 5, sha `cdd2717e52820ff6`

- relpath: `corpus/ratings/5/011__hcwKJOsUUIk__Disco_A.mp3`
- file_sha256: `cdd2717e52820ff69895e5f8e5901b59e581dcced81e031b9e0ca1db5709f157`
- run1 wall_clock_s: 79.08
- run2 wall_clock_s: 76.61
- run1_failed_stage: `None`
- byte-determinism x 2 (all 4 anchors): **yes**

| anchor | run1 sha[:16] | run2 sha[:16] | equal |
|--------|---------------|---------------|-------|
| `06_score/merged.midi` | `9994d3d54f34bc08` | `9994d3d54f34bc08` | yes |
| `06_score/merged.musicxml` | `72fc393448e52caa` | `72fc393448e52caa` | yes |
| `07_render/bare_midi.wav` | `d9d02122e4b8ea64` | `d9d02122e4b8ea64` | yes |
| `07_render/effects.wav` | `eafbb826b18dea77` | `eafbb826b18dea77` | yes |

- M-TEX-1 panel deltas (bare − effects; positive = effects narrows the gap):
  - `mel_l1_db`: bare 27.4468, effects 17.5391, delta **9.9077**
  - `spectral_centroid_rmse_hz`: bare 2027.9443, effects 1964.3585, delta 63.5858
  - `rms_env_rmse`: bare 0.2341, effects 0.2090, delta 0.0252
  - `lufs_m_rmse_lu`: bare 15.5772, effects 12.2987, delta 3.2784

- pretty_midi_fallback_used_run1: `False`

- preview_untrained_ear: M-EAR-1/real-label-training-v1 verdict EAR_v1_PARTIAL (SB1 -0.209 / SB2 -0.099 / SB3 corpus-shape-degenerate; 43/80 corpus coverage) — see docs/ear_real_label_training_v1_report.md — this pipeline does NOT compute per-song ear predictions

### Song 32: band 5, sha `dcfdabd9a4331b82`

- relpath: `corpus/ratings/5/019__kNwkXGeHE34__Gecko_Turner_-_Toda_Mojaita.mp3`
- file_sha256: `dcfdabd9a4331b82a742708cf6d42b5a584dbd55c20e7e73095c13798abf23c3`
- run1 wall_clock_s: 79.27
- run2 wall_clock_s: 79.35
- run1_failed_stage: `None`
- byte-determinism x 2 (all 4 anchors): **yes**

| anchor | run1 sha[:16] | run2 sha[:16] | equal |
|--------|---------------|---------------|-------|
| `06_score/merged.midi` | `d5cb459b02e66b96` | `d5cb459b02e66b96` | yes |
| `06_score/merged.musicxml` | `a47ad8d29cfe3f25` | `a47ad8d29cfe3f25` | yes |
| `07_render/bare_midi.wav` | `4fce3a3228a8eaa6` | `4fce3a3228a8eaa6` | yes |
| `07_render/effects.wav` | `2b1679e0c0497004` | `2b1679e0c0497004` | yes |

- M-TEX-1 panel deltas (bare − effects; positive = effects narrows the gap):
  - `mel_l1_db`: bare 17.1232, effects 12.0268, delta **5.0963**
  - `spectral_centroid_rmse_hz`: bare 2211.8097, effects 1527.4754, delta 684.3343
  - `rms_env_rmse`: bare 0.0302, effects 0.0684, delta -0.0382
  - `lufs_m_rmse_lu`: bare 14.4812, effects 14.0111, delta 0.4701

- pretty_midi_fallback_used_run1: `False`

- preview_untrained_ear: M-EAR-1/real-label-training-v1 verdict EAR_v1_PARTIAL (SB1 -0.209 / SB2 -0.099 / SB3 corpus-shape-degenerate; 43/80 corpus coverage) — see docs/ear_real_label_training_v1_report.md — this pipeline does NOT compute per-song ear predictions

### Song 33: band 6, sha `e02d1eedf06ec62b`

- relpath: `corpus/ratings/6/016__1GmuDka6pbk__Loyle_Carner_-_Angel_ft._Tom_Misch.mp3`
- file_sha256: `e02d1eedf06ec62b927a6a31c416b669e5c6a6ac1b641025439d305b37b87240`
- run1 wall_clock_s: 79.50
- run2 wall_clock_s: 77.88
- run1_failed_stage: `None`
- byte-determinism x 2 (all 4 anchors): **yes**

| anchor | run1 sha[:16] | run2 sha[:16] | equal |
|--------|---------------|---------------|-------|
| `06_score/merged.midi` | `04f020207d5a52ea` | `04f020207d5a52ea` | yes |
| `06_score/merged.musicxml` | `211b1ba855cfe8a7` | `211b1ba855cfe8a7` | yes |
| `07_render/bare_midi.wav` | `769600a96fe2d5ab` | `769600a96fe2d5ab` | yes |
| `07_render/effects.wav` | `260a0860961d64b6` | `260a0860961d64b6` | yes |

- M-TEX-1 panel deltas (bare − effects; positive = effects narrows the gap):
  - `mel_l1_db`: bare 25.0407, effects 19.6986, delta **5.3421**
  - `spectral_centroid_rmse_hz`: bare 2255.7530, effects 2261.8923, delta -6.1392
  - `rms_env_rmse`: bare 0.2677, effects 0.2477, delta 0.0199
  - `lufs_m_rmse_lu`: bare 14.5300, effects 14.5741, delta -0.0441

- pretty_midi_fallback_used_run1: `False`

- preview_untrained_ear: M-EAR-1/real-label-training-v1 verdict EAR_v1_PARTIAL (SB1 -0.209 / SB2 -0.099 / SB3 corpus-shape-degenerate; 43/80 corpus coverage) — see docs/ear_real_label_training_v1_report.md — this pipeline does NOT compute per-song ear predictions

### Song 34: band 6, sha `e61bfa4144344843`

- relpath: `corpus/ratings/6/007__89RgkWOsn18__Lost.mp3`
- file_sha256: `e61bfa4144344843587bad7f2f8f023a3c367626611fbefa2f8040e184ffa5bf`
- run1 wall_clock_s: 83.78
- run2 wall_clock_s: 82.11
- run1_failed_stage: `None`
- byte-determinism x 2 (all 4 anchors): **yes**

| anchor | run1 sha[:16] | run2 sha[:16] | equal |
|--------|---------------|---------------|-------|
| `06_score/merged.midi` | `d46c53473801d8ef` | `d46c53473801d8ef` | yes |
| `06_score/merged.musicxml` | `8be085087c2607c6` | `8be085087c2607c6` | yes |
| `07_render/bare_midi.wav` | `92c4b38425f700a7` | `92c4b38425f700a7` | yes |
| `07_render/effects.wav` | `b446c74a2eab9150` | `b446c74a2eab9150` | yes |

- M-TEX-1 panel deltas (bare − effects; positive = effects narrows the gap):
  - `mel_l1_db`: bare 18.3443, effects 14.1342, delta **4.2101**
  - `spectral_centroid_rmse_hz`: bare 2460.4575, effects 2248.3839, delta 212.0737
  - `rms_env_rmse`: bare 0.1776, effects 0.1721, delta 0.0056
  - `lufs_m_rmse_lu`: bare 8.0853, effects 6.9734, delta 1.1118

- pretty_midi_fallback_used_run1: `False`

- preview_untrained_ear: M-EAR-1/real-label-training-v1 verdict EAR_v1_PARTIAL (SB1 -0.209 / SB2 -0.099 / SB3 corpus-shape-degenerate; 43/80 corpus coverage) — see docs/ear_real_label_training_v1_report.md — this pipeline does NOT compute per-song ear predictions

### Song 35: band 6, sha `e66cbeb1817e37f0`

- relpath: `corpus/ratings/6/028__gLcTMUNmgwk__Jess_Best_-_Forgetfulness.mp3`
- file_sha256: `e66cbeb1817e37f0035e781d075c54f28f37da35a8a46da61e50598e4e1f8cd6`
- run1 wall_clock_s: 78.88
- run2 wall_clock_s: 78.12
- run1_failed_stage: `None`
- byte-determinism x 2 (all 4 anchors): **yes**

| anchor | run1 sha[:16] | run2 sha[:16] | equal |
|--------|---------------|---------------|-------|
| `06_score/merged.midi` | `f586f45bbc2879f4` | `f586f45bbc2879f4` | yes |
| `06_score/merged.musicxml` | `4e26a75e9b31b7c6` | `4e26a75e9b31b7c6` | yes |
| `07_render/bare_midi.wav` | `34940f201978e255` | `34940f201978e255` | yes |
| `07_render/effects.wav` | `baed242465942f60` | `baed242465942f60` | yes |

- M-TEX-1 panel deltas (bare − effects; positive = effects narrows the gap):
  - `mel_l1_db`: bare 24.2522, effects 18.0487, delta **6.2036**
  - `spectral_centroid_rmse_hz`: bare 2171.6694, effects 1720.3420, delta 451.3274
  - `rms_env_rmse`: bare 0.2542, effects 0.2374, delta 0.0168
  - `lufs_m_rmse_lu`: bare 16.6831, effects 17.3674, delta -0.6843

- pretty_midi_fallback_used_run1: `False`

- preview_untrained_ear: M-EAR-1/real-label-training-v1 verdict EAR_v1_PARTIAL (SB1 -0.209 / SB2 -0.099 / SB3 corpus-shape-degenerate; 43/80 corpus coverage) — see docs/ear_real_label_training_v1_report.md — this pipeline does NOT compute per-song ear predictions

### Song 36: band 6, sha `f1cfe4855364ea9b`

- relpath: `corpus/ratings/6/013__EO5dUydK2vU__Tom_Misch_Yussef_Dayes_-_Last_100.mp3`
- file_sha256: `f1cfe4855364ea9bef127a8a3e4ce2c02d0047b0c346213fcf05756aca40d913`
- run1 wall_clock_s: 80.25
- run2 wall_clock_s: 80.85
- run1_failed_stage: `None`
- byte-determinism x 2 (all 4 anchors): **yes**

| anchor | run1 sha[:16] | run2 sha[:16] | equal |
|--------|---------------|---------------|-------|
| `06_score/merged.midi` | `f6b975df40355f0e` | `f6b975df40355f0e` | yes |
| `06_score/merged.musicxml` | `ce86e5ecb865205e` | `ce86e5ecb865205e` | yes |
| `07_render/bare_midi.wav` | `1946994f15444995` | `1946994f15444995` | yes |
| `07_render/effects.wav` | `eee3713eb4c1b0b3` | `eee3713eb4c1b0b3` | yes |

- M-TEX-1 panel deltas (bare − effects; positive = effects narrows the gap):
  - `mel_l1_db`: bare 16.1881, effects 10.1804, delta **6.0078**
  - `spectral_centroid_rmse_hz`: bare 981.6992, effects 644.2086, delta 337.4906
  - `rms_env_rmse`: bare 0.0860, effects 0.0710, delta 0.0149
  - `lufs_m_rmse_lu`: bare 8.3849, effects 7.8151, delta 0.5698

- pretty_midi_fallback_used_run1: `False`

- preview_untrained_ear: M-EAR-1/real-label-training-v1 verdict EAR_v1_PARTIAL (SB1 -0.209 / SB2 -0.099 / SB3 corpus-shape-degenerate; 43/80 corpus coverage) — see docs/ear_real_label_training_v1_report.md — this pipeline does NOT compute per-song ear predictions

## 5. Cross-band tables (n=37, n=42 pooled, n=43 pooled)

Full tables in `data/recreate_v0_full_corpus/cross_band_{n37,pooled_n42,pooled_n43}.tsv`.

### n=37 (this branch only)
- rows (excluding header): 37
- path: `data/recreate_v0_full_corpus/cross_band_n37.tsv`

### n=42 (this branch + c38 clone-2's 5)
- rows (excluding header): 42
- path: `data/recreate_v0_full_corpus/cross_band_pooled_n42.tsv`

### n=43 (this branch + c38 clone-2's 5 + c37 clone-0's 1)
- rows (excluding header): 43
- path: `data/recreate_v0_full_corpus/cross_band_pooled_n43.tsv`

## 6. Cross-band correlations

Per-metric Pearson r + Spearman ρ of the four family metric deltas vs band index, at n=37, n=42, n=43. Every row carries the literal `n_too_small` caveat.

### n=37

| delta_key | n | n_finite | pearson_r | spearman_rho |
|-----------|---|----------|-----------|--------------|
| `mel_l1_db_delta` | 37 | 37 | -0.0133 | 0.0234 |
| `spectral_centroid_rmse_hz_delta` | 37 | 37 | -0.1453 | -0.0925 |
| `rms_env_rmse_delta` | 37 | 37 | 0.0103 | 0.0480 |
| `lufs_m_rmse_delta` | 37 | 37 | -0.0996 | -0.1205 |

  - `mel_l1_db_delta` caveat: `n_too_small; correlation is exploratory only, not inferentially valid`
  - `spectral_centroid_rmse_hz_delta` caveat: `n_too_small; correlation is exploratory only, not inferentially valid`
  - `rms_env_rmse_delta` caveat: `n_too_small; correlation is exploratory only, not inferentially valid`
  - `lufs_m_rmse_delta` caveat: `n_too_small; correlation is exploratory only, not inferentially valid`

### n=42_pooled

| delta_key | n | n_finite | pearson_r | spearman_rho |
|-----------|---|----------|-----------|--------------|
| `mel_l1_db_delta` | 42 | 42 | -0.0494 | -0.0087 |
| `spectral_centroid_rmse_hz_delta` | 42 | 42 | -0.0556 | 0.0240 |
| `rms_env_rmse_delta` | 42 | 42 | 0.0001 | 0.0239 |
| `lufs_m_rmse_delta` | 42 | 42 | -0.1685 | -0.1923 |

  - `mel_l1_db_delta` caveat: `n_too_small; correlation is exploratory only, not inferentially valid`
  - `spectral_centroid_rmse_hz_delta` caveat: `n_too_small; correlation is exploratory only, not inferentially valid`
  - `rms_env_rmse_delta` caveat: `n_too_small; correlation is exploratory only, not inferentially valid`
  - `lufs_m_rmse_delta` caveat: `n_too_small; correlation is exploratory only, not inferentially valid`

### n=43_pooled

| delta_key | n | n_finite | pearson_r | spearman_rho |
|-----------|---|----------|-----------|--------------|
| `mel_l1_db_delta` | 43 | 43 | -0.0399 | 0.0043 |
| `spectral_centroid_rmse_hz_delta` | 43 | 43 | -0.0958 | -0.0342 |
| `rms_env_rmse_delta` | 43 | 43 | 0.0145 | 0.0342 |
| `lufs_m_rmse_delta` | 43 | 43 | -0.1727 | -0.1963 |

  - `mel_l1_db_delta` caveat: `n_too_small; correlation is exploratory only, not inferentially valid`
  - `spectral_centroid_rmse_hz_delta` caveat: `n_too_small; correlation is exploratory only, not inferentially valid`
  - `rms_env_rmse_delta` caveat: `n_too_small; correlation is exploratory only, not inferentially valid`
  - `lufs_m_rmse_delta` caveat: `n_too_small; correlation is exploratory only, not inferentially valid`

## 7. Byte-determinism summary

- Total anchors: 148 (37 songs x 4 anchors)
- Anchors equal: 148

## 8. Anchor preservation

- 24 anchors tracked
- unchanged: True

Tracked anchor categories:
- c37 `scripts/recreate_v0/*.py` + data + report
- c38 clone-2 `scripts/recreate_v0_batch/*.py` + data + reports
- c38 clone-0 v1 report (doc-path reference)
- c38 clone-1 score-bridge + normalizer-v2 reports (doc-path references)
- c8 `scripts/score/bridge.py`
- c9 `scripts/tex/render_effects_layered.py`

## 9. Compute budget

- Per-song run-1 median wall-clock: 81.26 s
- Per-song run-1 max wall-clock: 90.95 s
- Early-exit threshold (6x c38 clone-2 median 82.2 s): 493.2 s
- Early-exit count: 0

## 10. Interpretation

The c37 8-stage recreation spine generalizes across all four rating bands at n=43 (37 songs new + 6 pooled). The effects-layer benefit is consistent: 36/37 songs show positive `mel_l1_db` delta.

### Cross-cycle comparison

- c37 clone-0 (n=1): band 7 `RECREATION_LANDS`, mel_l1_db_delta = +5.906 dB
- c38 clone-2 (n=5): bands 4/5/6/7, `BATCH_LANDS`, mel_l1_db deltas +2.879 to +7.983 dB (mean +5.04)
- c39 clone-0 (n=37): full-corpus extension, verdict `FULL_CORPUS_LANDS`, 36/37 positive mel deltas

## 11. c40 handoff seeds

- Depending on n=43 correlation gradient shape:
  - If mel_l1_db_delta shows a band-gradient → seed `_manager/effects-chain-band-selectivity` as urgent for c40.
  - If flat → G1 recreation spine is band-agnostic; seed `M-RULES-1/extraction/rated-corpus` (rule extraction on real-audio-derived MusicXML at scale).

### Standing c40 references (regardless of verdict)

- `_manager/fanout-namespace-convention-discrepancy` still open (c39 Branch C addresses in parallel).
- c38 clone-1 `QUANTIZATION_REDEFINED_GAP` + normalizer-v2 REFUTED — mscore3 quantization root-cause narrows to `<time-modification>` tuplets / ties-across-measures / `<beat-unit-dot>`; c40 opportunistic only.
- c37 VST3 activation still gated by c36 MIXED verdict.
- Egress retry per campaign directive: `workspace/harvest_playlists.sh` should be retried; two consecutive `media_ok=true` unblocks corpus expansion to the full 80 rated songs.

