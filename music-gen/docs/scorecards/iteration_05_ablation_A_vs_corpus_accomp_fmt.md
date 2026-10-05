# v6 scorecard — iteration_05_ablation_A_vs_corpus_accomp_fmt

Overall verdict: **FLAG** — clap:kid_song (primary); clap:c2st_balanced_accuracy (secondary); clap:coverage (diagnostic)

Candidates: 29 mix files (29 with windows); reference `corpus_accomp`: 29 files. Gates: `/home/user/long-exposure-runs/music-gen/data/v6/scorecard/gates_v6.json` (sha16 de7eeb897ee08f0a, key `references.corpus_accomp`). Seed 0, k=5, bootstrap 200. Candidates FORMAT-MATCHED to the reference: 22050 Hz / 1 ch (0 transformed, 29 already matched).

## clap (d=512; candidates 29 songs / 842 windows; reference 29 songs / 1451 windows) — **FLAG**

| metric | value | CI95 | noise floor (split-half 95%) | rule | verdict |
|---|---|---|---|---|---|
| kid_song | 0.001194 | [0.0009521, 0.001511] | [-7.642e-05, 9.746e-05] | FLAG if > 9.746e-05 and CI95 excludes 0 | FLAG |
| c2st_balanced_accuracy | 0.9495 | - | [0.3895, 0.6059] | FLAG if > 0.61 | FLAG |
| coverage | 0.1578 | - | [0.4925, 0.8298] | FLAG if < 0.4925 | FLAG |
| density | 1.421 | - | [1.619, 3.981] | info | INFO |
| fad | 0.3348 | - | [0.1133, 0.1652] | info (rank only) | INFO |
| knn_real_fraction | 0.004276 | - | [0.4249, 0.6308] | info (null expectation 0.6411) | INFO |
| kid_mean | 0.001124 | - | [7.288e-05, 0.0002731] | info | INFO |
| novelty_max_cos | 0.9494 | - | [0.9611, 0.9638] | FLAG song if max cos > 0.985 or >= 3 consecutive windows > 0.9638 on one ref song | PASS |

Novelty: no candidate song flagged.

Least real-like candidates (lowest kNN-real fraction; nearest reference song by cosine):
- `gen_v6_song_2_donor_51e433ade2a845e1.wav`: kNN-real 0, max cos 0.9053 to `Anderson .Paak: Vans Sidestripe Sessions | VANS`
- `gen_v6_song_4_donor_c7d491e98767eea5.wav`: kNN-real 0, max cos 0.9422 to `Corn on my Dinner Plate - Swing Dreams (OFFICIAL MUSIC VIDEO)`
- `gen_v6_song_22_donor_733ab58ee9bf7029.wav`: kNN-real 0, max cos 0.9213 to `FKJ & Pomo - Lucky Star (Live)`

## Audio descriptors (mix level)

Candidates n=29, reference n=29. Loudness/width/crest mismatches often explain embedding distance before timbre does.

| descriptor | candidates mean ± sd | reference mean ± sd | Δ (cand − ref) |
|---|---|---|---|
| lufs_integrated | -17.01 ± 1.44 | -17.2 ± 3.4 | 0.193 |
| crest_factor_db | 14.75 ± 1.47 | 14.97 ± 2.24 | -0.215 |
| spectral_centroid_hz | 1804 ± 232 | 1674 ± 444 | 130 |
| stereo_width_db | - | - | - |
| lr_correlation | - | - | - |
| peak_dbfs | -1.384 ± 0.474 | -1.074 ± 2.74 | -0.31 |
| rms_dbfs | -16.14 ± 1.44 | -16.04 ± 3.65 | -0.0949 |

Wall 3750.2 s. Full numbers: `scorecard.json`, per-backbone `distribution_<backbone>.json`.
