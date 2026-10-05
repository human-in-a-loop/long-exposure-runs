# v6 scorecard — iteration_03_corpus_vs_corpus

Overall verdict: **FLAG** — clap:kid_song (primary); clap:c2st_balanced_accuracy (secondary); clap:coverage (diagnostic); mert:kid_song (primary); mert:c2st_balanced_accuracy (secondary); mert:coverage (diagnostic)

Candidates: 29 mix files (29 with windows); reference `corpus`: 29 files. Gates: `/home/user/long-exposure-runs/music-gen/data/v6/scorecard/gates_v6.json` (sha16 4579182689de8ace). Seed 0, k=5, bootstrap 200.

## clap (d=512; candidates 29 songs / 826 windows; reference 29 songs / 1459 windows) — **FLAG**

| metric | value | CI95 | noise floor (split-half 95%) | rule | verdict |
|---|---|---|---|---|---|
| kid_song | 0.001856 | [0.001381, 0.002293] | [-8.77e-05, 0.0001986] | FLAG if > 0.0001986 and CI95 excludes 0 | FLAG |
| c2st_balanced_accuracy | 0.9377 | - | [0.3304, 0.666] | FLAG if > 0.67 | FLAG |
| coverage | 0.1624 | - | [0.4671, 0.9042] | FLAG if < 0.4671 | FLAG |
| density | 3.399 | - | [1.368, 3.801] | info | INFO |
| fad | 0.5061 | - | [0.1227, 0.207] | info (rank only) | INFO |
| knn_real_fraction | 0.001937 | - | [0.3704, 0.7168] | info (null expectation 0.6469) | INFO |
| kid_mean | 0.001827 | - | [9.012e-05, 0.0004242] | info | INFO |
| novelty_max_cos | 0.9418 | - | [0.9595, 0.9686] | FLAG song if max cos > 0.985 or >= 3 consecutive windows > 0.9686 on one ref song | PASS |

Novelty: no candidate song flagged.

Least real-like candidates (lowest kNN-real fraction; nearest reference song by cosine):
- `ab_mix.wav`: kNN-real 0, max cos 0.9123 to `FKJ & Pomo - Lucky Star (Live)`
- `ab_mix.wav`: kNN-real 0, max cos 0.8907 to `FKJ & Pomo - Lucky Star (Live)`
- `ab_mix.wav`: kNN-real 0, max cos 0.9269 to `Corn on my Dinner Plate - Swing Dreams (OFFICIAL MUSIC VIDEO)`

## mert (d=1536; candidates 29 songs / 826 windows; reference 29 songs / 1459 windows) — **FLAG**

| metric | value | CI95 | noise floor (split-half 95%) | rule | verdict |
|---|---|---|---|---|---|
| kid_song | 0.004465 | [0.00322, 0.005624] | [-0.00049, 0.000851] | FLAG if > 0.000851 and CI95 excludes 0 | FLAG |
| c2st_balanced_accuracy | 0.9705 | - | [0.3578, 0.5485] | FLAG if > 0.55 | FLAG |
| coverage | 0.1576 | - | [0.5551, 0.8626] | FLAG if < 0.5551 | FLAG |
| density | 0.3334 | - | [1.26, 3.627] | info | INFO |
| fad | 7.012 | - | [5.426, 6.236] | info (rank only) | INFO |
| knn_real_fraction | 0.0109 | - | [0.3131, 0.7029] | info (null expectation 0.6469) | INFO |
| kid_mean | 0.004857 | - | [0.001047, 0.002239] | info | INFO |
| novelty_max_cos | 0.9833 | - | [0.984, 0.9874] | FLAG song if max cos > 0.995 or >= 3 consecutive windows > 0.9874 on one ref song | PASS |

Novelty: no candidate song flagged.

Least real-like candidates (lowest kNN-real fraction; nearest reference song by cosine):
- `ab_mix.wav`: kNN-real 0, max cos 0.9811 to `Disco A`
- `ab_mix.wav`: kNN-real 0, max cos 0.9797 to `Disco A`
- `ab_mix.wav`: kNN-real 0, max cos 0.9778 to `Disco A`

## Audio descriptors (mix level)

Candidates n=29, reference n=29. Loudness/width/crest mismatches often explain embedding distance before timbre does.

| descriptor | candidates mean ± sd | reference mean ± sd | Δ (cand − ref) |
|---|---|---|---|
| lufs_integrated | -12.21 ± 0.196 | -11.82 ± 3.35 | -0.385 |
| crest_factor_db | 12.57 ± 0.69 | 14.06 ± 1.96 | -1.49 |
| spectral_centroid_hz | 2563 ± 377 | 2421 ± 617 | 142 |
| stereo_width_db | -18.67 ± 1.2 | -12.94 ± 12 | -5.73 |
| lr_correlation | 0.9729 ± 0.00673 | 0.8023 ± 0.168 | 0.171 |
| peak_dbfs | -1.991 ± 0.519 | -0.03152 ± 2.89 | -1.96 |
| rms_dbfs | -14.56 ± 0.411 | -14.09 ± 3.56 | -0.472 |

Wall 1481.1 s. Full numbers: `scorecard.json`, per-backbone `distribution_<backbone>.json`.
