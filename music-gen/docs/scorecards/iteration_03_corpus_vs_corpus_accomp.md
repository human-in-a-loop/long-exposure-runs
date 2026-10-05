# v6 scorecard — iteration_03_corpus_vs_corpus_accomp

Overall verdict: **FLAG** — clap:kid_song (primary); clap:c2st_balanced_accuracy (secondary); clap:coverage (diagnostic); mert:kid_song (primary); mert:c2st_balanced_accuracy (secondary); mert:coverage (diagnostic)

Candidates: 29 mix files (29 with windows); reference `corpus_accomp`: 29 files. Gates: `/home/user/long-exposure-runs/music-gen/data/v6/scorecard/gates_v6.json` (sha16 de7eeb897ee08f0a, key `references.corpus_accomp`). Seed 0, k=5, bootstrap 200.

## clap (d=512; candidates 29 songs / 826 windows; reference 29 songs / 1451 windows) — **FLAG**

| metric | value | CI95 | noise floor (split-half 95%) | rule | verdict |
|---|---|---|---|---|---|
| kid_song | 0.001585 | [0.001336, 0.001869] | [-7.642e-05, 9.746e-05] | FLAG if > 9.746e-05 and CI95 excludes 0 | FLAG |
| c2st_balanced_accuracy | 0.9878 | - | [0.3895, 0.6059] | FLAG if > 0.61 | FLAG |
| coverage | 0.06203 | - | [0.4925, 0.8298] | FLAG if < 0.4925 | FLAG |
| density | 0.1433 | - | [1.619, 3.981] | info | INFO |
| fad | 0.4131 | - | [0.1133, 0.1652] | info (rank only) | INFO |
| knn_real_fraction | 0.002906 | - | [0.4249, 0.6308] | info (null expectation 0.6456) | INFO |
| kid_mean | 0.001567 | - | [7.288e-05, 0.0002731] | info | INFO |
| novelty_max_cos | 0.9271 | - | [0.9611, 0.9638] | FLAG song if max cos > 0.985 or >= 3 consecutive windows > 0.9638 on one ref song | PASS |

Novelty: no candidate song flagged.

Least real-like candidates (lowest kNN-real fraction; nearest reference song by cosine):
- `ab_mix.wav`: kNN-real 0, max cos 0.8964 to `FKJ & Pomo - Lucky Star (Live)`
- `ab_mix.wav`: kNN-real 0, max cos 0.9084 to `I Found My Smile Again (Radio Edit)`
- `ab_mix.wav`: kNN-real 0, max cos 0.9207 to `Anderson .Paak: Vans Sidestripe Sessions | VANS`

## mert (d=1536; candidates 29 songs / 826 windows; reference 29 songs / 1451 windows) — **FLAG**

| metric | value | CI95 | noise floor (split-half 95%) | rule | verdict |
|---|---|---|---|---|---|
| kid_song | 0.006308 | [0.004544, 0.008094] | [-0.0008597, 0.0007167] | FLAG if > 0.0007167 and CI95 excludes 0 | FLAG |
| c2st_balanced_accuracy | 0.9434 | - | [0.3724, 0.5626] | FLAG if > 0.57 | FLAG |
| coverage | 0.2633 | - | [0.6029, 0.8887] | FLAG if < 0.6029 | FLAG |
| density | 1.248 | - | [1.277, 4.427] | info | INFO |
| fad | 9.271 | - | [7.283, 8.45] | info (rank only) | INFO |
| knn_real_fraction | 0.006053 | - | [0.3658, 0.7553] | info (null expectation 0.6456) | INFO |
| kid_mean | 0.006652 | - | [0.001155, 0.00319] | info | INFO |
| novelty_max_cos | 0.982 | - | [0.9803, 0.9809] | FLAG song if max cos > 0.995 or >= 3 consecutive windows > 0.9809 on one ref song | PASS |

Novelty: no candidate song flagged.

Least real-like candidates (lowest kNN-real fraction; nearest reference song by cosine):
- `ab_mix.wav`: kNN-real 0, max cos 0.9769 to `Disco A`
- `ab_mix.wav`: kNN-real 0, max cos 0.9804 to `Disco A`
- `ab_mix.wav`: kNN-real 0, max cos 0.9787 to `Disco A`

## Audio descriptors (mix level)

Candidates n=29, reference n=29. Loudness/width/crest mismatches often explain embedding distance before timbre does.

| descriptor | candidates mean ± sd | reference mean ± sd | Δ (cand − ref) |
|---|---|---|---|
| lufs_integrated | -12.21 ± 0.196 | -17.2 ± 3.4 | 4.99 |
| crest_factor_db | 12.57 ± 0.69 | 14.97 ± 2.24 | -2.4 |
| spectral_centroid_hz | 2563 ± 377 | 1674 ± 444 | 890 |
| stereo_width_db | -18.67 | - | - |
| lr_correlation | 0.9729 | - | - |
| peak_dbfs | -1.991 ± 0.519 | -1.074 ± 2.74 | -0.916 |
| rms_dbfs | -14.56 ± 0.411 | -16.04 ± 3.65 | 1.48 |

Wall 100.4 s. Full numbers: `scorecard.json`, per-backbone `distribution_<backbone>.json`.
