# v6 scorecard — iteration_05_ablation_B_vs_corpus_accomp_fmt

Overall verdict: **FLAG** — clap:kid_song (primary); clap:c2st_balanced_accuracy (secondary); clap:coverage (diagnostic)

Candidates: 29 mix files (29 with windows); reference `corpus_accomp`: 29 files. Gates: `/home/user/long-exposure-runs/music-gen/data/v6/scorecard/gates_v6.json` (sha16 de7eeb897ee08f0a, key `references.corpus_accomp`). Seed 0, k=5, bootstrap 200. Candidates FORMAT-MATCHED to the reference: 22050 Hz / 1 ch (0 transformed, 29 already matched).

## clap (d=512; candidates 29 songs / 842 windows; reference 29 songs / 1451 windows) — **FLAG**

| metric | value | CI95 | noise floor (split-half 95%) | rule | verdict |
|---|---|---|---|---|---|
| kid_song | 0.001199 | [0.000963, 0.001485] | [-7.642e-05, 9.746e-05] | FLAG if > 9.746e-05 and CI95 excludes 0 | FLAG |
| c2st_balanced_accuracy | 0.9509 | - | [0.3895, 0.6059] | FLAG if > 0.61 | FLAG |
| coverage | 0.164 | - | [0.4925, 0.8298] | FLAG if < 0.4925 | FLAG |
| density | 1.378 | - | [1.619, 3.981] | info | INFO |
| fad | 0.3355 | - | [0.1133, 0.1652] | info (rank only) | INFO |
| knn_real_fraction | 0.004276 | - | [0.4249, 0.6308] | info (null expectation 0.6411) | INFO |
| kid_mean | 0.001127 | - | [7.288e-05, 0.0002731] | info | INFO |
| novelty_max_cos | 0.9485 | - | [0.9611, 0.9638] | FLAG song if max cos > 0.985 or >= 3 consecutive windows > 0.9638 on one ref song | PASS |

Novelty: no candidate song flagged.

Least real-like candidates (lowest kNN-real fraction; nearest reference song by cosine):
- `4c151209c4daf98a_22050hz_1ch.wav`: kNN-real 0, max cos 0.928 to `Willow Weep For Me`
- `gen_v6_song_27_donor_89ec8ec7c0be97de.wav`: kNN-real 0, max cos 0.928 to `Corn on my Dinner Plate - Swing Dreams (OFFICIAL MUSIC VIDEO)`
- `gen_v6_song_7_donor_7e6b59b873ed8972.wav`: kNN-real 0, max cos 0.9458 to `Dojo Cuts - Rome`

## Audio descriptors (mix level)

Candidates n=29, reference n=29. Loudness/width/crest mismatches often explain embedding distance before timbre does.

| descriptor | candidates mean ± sd | reference mean ± sd | Δ (cand − ref) |
|---|---|---|---|
| lufs_integrated | -16.92 ± 1.48 | -17.2 ± 3.4 | 0.282 |
| crest_factor_db | 14.75 ± 1.43 | 14.97 ± 2.24 | -0.216 |
| spectral_centroid_hz | 1692 ± 220 | 1674 ± 444 | 18.4 |
| stereo_width_db | - | - | - |
| lr_correlation | - | - | - |
| peak_dbfs | -1.237 ± 0.522 | -1.074 ± 2.74 | -0.163 |
| rms_dbfs | -15.99 ± 1.49 | -16.04 ± 3.65 | 0.0534 |

Wall 93.0 s. Full numbers: `scorecard.json`, per-backbone `distribution_<backbone>.json`.
