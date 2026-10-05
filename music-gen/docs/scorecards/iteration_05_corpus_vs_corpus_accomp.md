# v6 scorecard — iteration_05_corpus_vs_corpus_accomp

Overall verdict: **FLAG** — clap:kid_song (primary); clap:c2st_balanced_accuracy (secondary); clap:coverage (diagnostic); mert:kid_song (primary); mert:c2st_balanced_accuracy (secondary); mert:coverage (diagnostic)

Candidates: 29 mix files (29 with windows); reference `corpus_accomp`: 29 files. Gates: `/home/user/long-exposure-runs/music-gen/data/v6/scorecard/gates_v6.json` (sha16 de7eeb897ee08f0a, key `references.corpus_accomp`). Seed 0, k=5, bootstrap 200.

## clap (d=512; candidates 29 songs / 842 windows; reference 29 songs / 1451 windows) — **FLAG**

| metric | value | CI95 | noise floor (split-half 95%) | rule | verdict |
|---|---|---|---|---|---|
| kid_song | 0.001872 | [0.001571, 0.002202] | [-7.642e-05, 9.746e-05] | FLAG if > 9.746e-05 and CI95 excludes 0 | FLAG |
| c2st_balanced_accuracy | 0.99 | - | [0.3895, 0.6059] | FLAG if > 0.61 | FLAG |
| coverage | 0.04273 | - | [0.4925, 0.8298] | FLAG if < 0.4925 | FLAG |
| density | 0.0715 | - | [1.619, 3.981] | info | INFO |
| fad | 0.4521 | - | [0.1133, 0.1652] | info (rank only) | INFO |
| knn_real_fraction | 0.003563 | - | [0.4249, 0.6308] | info (null expectation 0.6411) | INFO |
| kid_mean | 0.001799 | - | [7.288e-05, 0.0002731] | info | INFO |
| novelty_max_cos | 0.9304 | - | [0.9611, 0.9638] | FLAG song if max cos > 0.985 or >= 3 consecutive windows > 0.9638 on one ref song | PASS |

Novelty: no candidate song flagged.

Least real-like candidates (lowest kNN-real fraction; nearest reference song by cosine):
- `ab_mix.wav`: kNN-real 0, max cos 0.8949 to `Dojo Cuts - Rome`
- `ab_mix.wav`: kNN-real 0, max cos 0.9191 to `Corn on my Dinner Plate - Swing Dreams (OFFICIAL MUSIC VIDEO)`
- `ab_mix.wav`: kNN-real 0, max cos 0.9127 to `Anderson .Paak: Vans Sidestripe Sessions | VANS`

## mert (d=1536; candidates 29 songs / 842 windows; reference 29 songs / 1451 windows) — **FLAG**

| metric | value | CI95 | noise floor (split-half 95%) | rule | verdict |
|---|---|---|---|---|---|
| kid_song | 0.005736 | [0.004149, 0.007645] | [-0.0008597, 0.0007167] | FLAG if > 0.0007167 and CI95 excludes 0 | FLAG |
| c2st_balanced_accuracy | 0.9312 | - | [0.3724, 0.5626] | FLAG if > 0.57 | FLAG |
| coverage | 0.2901 | - | [0.6029, 0.8887] | FLAG if < 0.6029 | FLAG |
| density | 1.017 | - | [1.277, 4.427] | info | INFO |
| fad | 9.204 | - | [7.283, 8.45] | info (rank only) | INFO |
| knn_real_fraction | 0.01686 | - | [0.3658, 0.7553] | info (null expectation 0.6411) | INFO |
| kid_mean | 0.006282 | - | [0.001155, 0.00319] | info | INFO |
| novelty_max_cos | 0.981 | - | [0.9803, 0.9809] | FLAG song if max cos > 0.995 or >= 3 consecutive windows > 0.9809 on one ref song | PASS |

Novelty: no candidate song flagged.

Least real-like candidates (lowest kNN-real fraction; nearest reference song by cosine):
- `ab_mix.wav`: kNN-real 0, max cos 0.9757 to `Disco A`
- `ab_mix.wav`: kNN-real 0, max cos 0.9785 to `Disco A`
- `ab_mix.wav`: kNN-real 0, max cos 0.9747 to `Disco A`

## Audio descriptors (mix level)

Candidates n=29, reference n=29. Loudness/width/crest mismatches often explain embedding distance before timbre does.

| descriptor | candidates mean ± sd | reference mean ± sd | Δ (cand − ref) |
|---|---|---|---|
| lufs_integrated | -13.26 ± 1.5 | -17.2 ± 3.4 | 3.95 |
| crest_factor_db | 14.38 ± 1.71 | 14.97 ± 2.24 | -0.585 |
| spectral_centroid_hz | 2368 ± 241 | 1674 ± 444 | 695 |
| stereo_width_db | -9.706 | - | - |
| lr_correlation | 0.7712 | - | - |
| peak_dbfs | -1.099 ± 0.445 | -1.074 ± 2.74 | -0.0248 |
| rms_dbfs | -15.48 ± 1.49 | -16.04 ± 3.65 | 0.561 |

Wall 34.5 s. Full numbers: `scorecard.json`, per-backbone `distribution_<backbone>.json`.
