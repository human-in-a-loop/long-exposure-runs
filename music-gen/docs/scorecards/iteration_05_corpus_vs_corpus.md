# v6 scorecard — iteration_05_corpus_vs_corpus

Overall verdict: **FLAG** — clap:kid_song (primary); clap:c2st_balanced_accuracy (secondary); clap:coverage (diagnostic); mert:kid_song (primary); mert:c2st_balanced_accuracy (secondary); mert:coverage (diagnostic)

Candidates: 29 mix files (29 with windows); reference `corpus`: 29 files. Gates: `/home/user/long-exposure-runs/music-gen/data/v6/scorecard/gates_v6.json` (sha16 de7eeb897ee08f0a, key `backbones`). Seed 0, k=5, bootstrap 200.

## clap (d=512; candidates 29 songs / 842 windows; reference 29 songs / 1459 windows) — **FLAG**

| metric | value | CI95 | noise floor (split-half 95%) | rule | verdict |
|---|---|---|---|---|---|
| kid_song | 0.002178 | [0.001729, 0.002635] | [-8.77e-05, 0.0001986] | FLAG if > 0.0001986 and CI95 excludes 0 | FLAG |
| c2st_balanced_accuracy | 0.9528 | - | [0.3304, 0.666] | FLAG if > 0.67 | FLAG |
| coverage | 0.1378 | - | [0.4671, 0.9042] | FLAG if < 0.4671 | FLAG |
| density | 3.384 | - | [1.368, 3.801] | info | INFO |
| fad | 0.5547 | - | [0.1227, 0.207] | info (rank only) | INFO |
| knn_real_fraction | 0.0019 | - | [0.3704, 0.7168] | info (null expectation 0.6424) | INFO |
| kid_mean | 0.002099 | - | [9.012e-05, 0.0004242] | info | INFO |
| novelty_max_cos | 0.9411 | - | [0.9595, 0.9686] | FLAG song if max cos > 0.985 or >= 3 consecutive windows > 0.9686 on one ref song | PASS |

Novelty: no candidate song flagged.

Least real-like candidates (lowest kNN-real fraction; nearest reference song by cosine):
- `ab_mix.wav`: kNN-real 0, max cos 0.9074 to `Anderson .Paak: Vans Sidestripe Sessions | VANS`
- `ab_mix.wav`: kNN-real 0, max cos 0.9347 to `Corn on my Dinner Plate - Swing Dreams (OFFICIAL MUSIC VIDEO)`
- `ab_mix.wav`: kNN-real 0, max cos 0.8833 to `Anderson .Paak: Vans Sidestripe Sessions | VANS`

## mert (d=1536; candidates 29 songs / 842 windows; reference 29 songs / 1459 windows) — **FLAG**

| metric | value | CI95 | noise floor (split-half 95%) | rule | verdict |
|---|---|---|---|---|---|
| kid_song | 0.005055 | [0.003841, 0.006309] | [-0.00049, 0.000851] | FLAG if > 0.000851 and CI95 excludes 0 | FLAG |
| c2st_balanced_accuracy | 0.9769 | - | [0.3578, 0.5485] | FLAG if > 0.55 | FLAG |
| coverage | 0.1193 | - | [0.5551, 0.8626] | FLAG if < 0.5551 | FLAG |
| density | 0.2081 | - | [1.26, 3.627] | info | INFO |
| fad | 7.459 | - | [5.426, 6.236] | info (rank only) | INFO |
| knn_real_fraction | 0.02043 | - | [0.3131, 0.7029] | info (null expectation 0.6424) | INFO |
| kid_mean | 0.005705 | - | [0.001047, 0.002239] | info | INFO |
| novelty_max_cos | 0.9816 | - | [0.984, 0.9874] | FLAG song if max cos > 0.995 or >= 3 consecutive windows > 0.9874 on one ref song | PASS |

Novelty: no candidate song flagged.

Least real-like candidates (lowest kNN-real fraction; nearest reference song by cosine):
- `ab_mix.wav`: kNN-real 0, max cos 0.9765 to `Disco A`
- `ab_mix.wav`: kNN-real 0, max cos 0.9794 to `Disco A`
- `ab_mix.wav`: kNN-real 0, max cos 0.9752 to `Disco A`

## Audio descriptors (mix level)

Candidates n=29, reference n=29. Loudness/width/crest mismatches often explain embedding distance before timbre does.

| descriptor | candidates mean ± sd | reference mean ± sd | Δ (cand − ref) |
|---|---|---|---|
| lufs_integrated | -13.26 ± 1.5 | -11.82 ± 3.35 | -1.43 |
| crest_factor_db | 14.38 ± 1.71 | 14.06 ± 1.96 | 0.323 |
| spectral_centroid_hz | 2368 ± 241 | 2421 ± 617 | -52.6 |
| stereo_width_db | -9.706 ± 3.21 | -12.94 ± 12 | 3.23 |
| lr_correlation | 0.7712 ± 0.133 | 0.8023 ± 0.168 | -0.0311 |
| peak_dbfs | -1.099 ± 0.445 | -0.03152 ± 2.89 | -1.07 |
| rms_dbfs | -15.48 ± 1.49 | -14.09 ± 3.56 | -1.39 |

Wall 2393.3 s. Full numbers: `scorecard.json`, per-backbone `distribution_<backbone>.json`.
