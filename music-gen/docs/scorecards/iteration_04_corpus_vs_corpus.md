# v6 scorecard — iteration_04_corpus_vs_corpus

Overall verdict: **FLAG** — clap:kid_song (primary); clap:c2st_balanced_accuracy (secondary); clap:coverage (diagnostic); mert:kid_song (primary); mert:c2st_balanced_accuracy (secondary); mert:coverage (diagnostic)

Candidates: 29 mix files (29 with windows); reference `corpus`: 29 files. Gates: `/home/user/long-exposure-runs/music-gen/data/v6/scorecard/gates_v6.json` (sha16 de7eeb897ee08f0a, key `backbones`). Seed 0, k=5, bootstrap 200.

## clap (d=512; candidates 29 songs / 824 windows; reference 29 songs / 1459 windows) — **FLAG**

| metric | value | CI95 | noise floor (split-half 95%) | rule | verdict |
|---|---|---|---|---|---|
| kid_song | 0.001662 | [0.001257, 0.002067] | [-8.77e-05, 0.0001986] | FLAG if > 0.0001986 and CI95 excludes 0 | FLAG |
| c2st_balanced_accuracy | 0.9306 | - | [0.3304, 0.666] | FLAG if > 0.67 | FLAG |
| coverage | 0.1741 | - | [0.4671, 0.9042] | FLAG if < 0.4671 | FLAG |
| density | 4.168 | - | [1.368, 3.801] | info | INFO |
| fad | 0.4767 | - | [0.1227, 0.207] | info (rank only) | INFO |
| knn_real_fraction | 0.002913 | - | [0.3704, 0.7168] | info (null expectation 0.6474) | INFO |
| kid_mean | 0.001649 | - | [9.012e-05, 0.0004242] | info | INFO |
| novelty_max_cos | 0.9373 | - | [0.9595, 0.9686] | FLAG song if max cos > 0.985 or >= 3 consecutive windows > 0.9686 on one ref song | PASS |

Novelty: no candidate song flagged.

Least real-like candidates (lowest kNN-real fraction; nearest reference song by cosine):
- `ab_mix.wav`: kNN-real 0, max cos 0.897 to `FKJ & Pomo - Lucky Star (Live)`
- `ab_mix.wav`: kNN-real 0, max cos 0.9179 to `Don't Know What's Normal`
- `ab_mix.wav`: kNN-real 0, max cos 0.9248 to `Don't Know What's Normal`

## mert (d=1536; candidates 29 songs / 824 windows; reference 29 songs / 1459 windows) — **FLAG**

| metric | value | CI95 | noise floor (split-half 95%) | rule | verdict |
|---|---|---|---|---|---|
| kid_song | 0.005126 | [0.003918, 0.006352] | [-0.00049, 0.000851] | FLAG if > 0.000851 and CI95 excludes 0 | FLAG |
| c2st_balanced_accuracy | 0.9746 | - | [0.3578, 0.5485] | FLAG if > 0.55 | FLAG |
| coverage | 0.1371 | - | [0.5551, 0.8626] | FLAG if < 0.5551 | FLAG |
| density | 0.382 | - | [1.26, 3.627] | info | INFO |
| fad | 7.666 | - | [5.426, 6.236] | info (rank only) | INFO |
| knn_real_fraction | 0.01019 | - | [0.3131, 0.7029] | info (null expectation 0.6474) | INFO |
| kid_mean | 0.005745 | - | [0.001047, 0.002239] | info | INFO |
| novelty_max_cos | 0.9821 | - | [0.984, 0.9874] | FLAG song if max cos > 0.995 or >= 3 consecutive windows > 0.9874 on one ref song | PASS |

Novelty: no candidate song flagged.

Least real-like candidates (lowest kNN-real fraction; nearest reference song by cosine):
- `ab_mix.wav`: kNN-real 0, max cos 0.9789 to `Don't Know What's Normal`
- `ab_mix.wav`: kNN-real 0, max cos 0.9796 to `Disco A`
- `ab_mix.wav`: kNN-real 0, max cos 0.9805 to `Don't Know What's Normal`

## Audio descriptors (mix level)

Candidates n=29, reference n=29. Loudness/width/crest mismatches often explain embedding distance before timbre does.

| descriptor | candidates mean ± sd | reference mean ± sd | Δ (cand − ref) |
|---|---|---|---|
| lufs_integrated | -12.34 ± 0.349 | -11.82 ± 3.35 | -0.516 |
| crest_factor_db | 13.15 ± 0.811 | 14.06 ± 1.96 | -0.91 |
| spectral_centroid_hz | 2656 ± 257 | 2421 ± 617 | 235 |
| stereo_width_db | -8.357 ± 2.83 | -12.94 ± 12 | 4.58 |
| lr_correlation | 0.7132 ± 0.148 | 0.8023 ± 0.168 | -0.0891 |
| peak_dbfs | -1.603 ± 0.885 | -0.03152 ± 2.89 | -1.57 |
| rms_dbfs | -14.75 ± 0.448 | -14.09 ± 3.56 | -0.661 |

Wall 106.5 s. Full numbers: `scorecard.json`, per-backbone `distribution_<backbone>.json`.
