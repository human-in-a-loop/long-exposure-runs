# v6 scorecard — iteration_04_corpus_vs_corpus_accomp

Overall verdict: **FLAG** — clap:kid_song (primary); clap:c2st_balanced_accuracy (secondary); clap:coverage (diagnostic); mert:kid_song (primary); mert:c2st_balanced_accuracy (secondary); mert:coverage (diagnostic)

Candidates: 29 mix files (29 with windows); reference `corpus_accomp`: 29 files. Gates: `/home/user/long-exposure-runs/music-gen/data/v6/scorecard/gates_v6.json` (sha16 de7eeb897ee08f0a, key `references.corpus_accomp`). Seed 0, k=5, bootstrap 200.

## clap (d=512; candidates 29 songs / 824 windows; reference 29 songs / 1451 windows) — **FLAG**

| metric | value | CI95 | noise floor (split-half 95%) | rule | verdict |
|---|---|---|---|---|---|
| kid_song | 0.001361 | [0.001059, 0.001649] | [-7.642e-05, 9.746e-05] | FLAG if > 9.746e-05 and CI95 excludes 0 | FLAG |
| c2st_balanced_accuracy | 0.9835 | - | [0.3895, 0.6059] | FLAG if > 0.61 | FLAG |
| coverage | 0.08477 | - | [0.4925, 0.8298] | FLAG if < 0.4925 | FLAG |
| density | 0.1604 | - | [1.619, 3.981] | info | INFO |
| fad | 0.3759 | - | [0.1133, 0.1652] | info (rank only) | INFO |
| knn_real_fraction | 0.001699 | - | [0.4249, 0.6308] | info (null expectation 0.6462) | INFO |
| kid_mean | 0.001366 | - | [7.288e-05, 0.0002731] | info | INFO |
| novelty_max_cos | 0.9333 | - | [0.9611, 0.9638] | FLAG song if max cos > 0.985 or >= 3 consecutive windows > 0.9638 on one ref song | PASS |

Novelty: no candidate song flagged.

Least real-like candidates (lowest kNN-real fraction; nearest reference song by cosine):
- `ab_mix.wav`: kNN-real 0, max cos 0.9025 to `Anderson .Paak: Vans Sidestripe Sessions | VANS`
- `ab_mix.wav`: kNN-real 0, max cos 0.897 to `Anderson .Paak: Vans Sidestripe Sessions | VANS`
- `ab_mix.wav`: kNN-real 0, max cos 0.9 to `Don't Know What's Normal`

## mert (d=1536; candidates 29 songs / 824 windows; reference 29 songs / 1451 windows) — **FLAG**

| metric | value | CI95 | noise floor (split-half 95%) | rule | verdict |
|---|---|---|---|---|---|
| kid_song | 0.006435 | [0.004722, 0.008552] | [-0.0008597, 0.0007167] | FLAG if > 0.0007167 and CI95 excludes 0 | FLAG |
| c2st_balanced_accuracy | 0.9313 | - | [0.3724, 0.5626] | FLAG if > 0.57 | FLAG |
| coverage | 0.2853 | - | [0.6029, 0.8887] | FLAG if < 0.6029 | FLAG |
| density | 1.258 | - | [1.277, 4.427] | info | INFO |
| fad | 9.664 | - | [7.283, 8.45] | info (rank only) | INFO |
| knn_real_fraction | 0.006553 | - | [0.3658, 0.7553] | info (null expectation 0.6462) | INFO |
| kid_mean | 0.007034 | - | [0.001155, 0.00319] | info | INFO |
| novelty_max_cos | 0.9812 | - | [0.9803, 0.9809] | FLAG song if max cos > 0.995 or >= 3 consecutive windows > 0.9809 on one ref song | PASS |

Novelty: no candidate song flagged.

Least real-like candidates (lowest kNN-real fraction; nearest reference song by cosine):
- `ab_mix.wav`: kNN-real 0, max cos 0.9766 to `Don't Know What's Normal`
- `ab_mix.wav`: kNN-real 0, max cos 0.9786 to `Disco A`
- `ab_mix.wav`: kNN-real 0, max cos 0.979 to `Disco A`

## Audio descriptors (mix level)

Candidates n=29, reference n=29. Loudness/width/crest mismatches often explain embedding distance before timbre does.

| descriptor | candidates mean ± sd | reference mean ± sd | Δ (cand − ref) |
|---|---|---|---|
| lufs_integrated | -12.34 ± 0.349 | -17.2 ± 3.4 | 4.86 |
| crest_factor_db | 13.15 ± 0.811 | 14.97 ± 2.24 | -1.82 |
| spectral_centroid_hz | 2656 ± 257 | 1674 ± 444 | 983 |
| stereo_width_db | -8.357 | - | - |
| lr_correlation | 0.7132 | - | - |
| peak_dbfs | -1.603 ± 0.885 | -1.074 ± 2.74 | -0.528 |
| rms_dbfs | -14.75 ± 0.448 | -16.04 ± 3.65 | 1.29 |

Wall 73.5 s. Full numbers: `scorecard.json`, per-backbone `distribution_<backbone>.json`.
