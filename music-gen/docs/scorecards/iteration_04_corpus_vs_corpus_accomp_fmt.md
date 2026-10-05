# v6 scorecard — iteration_04_corpus_vs_corpus_accomp_fmt

Overall verdict: **FLAG** — clap:kid_song (primary); clap:c2st_balanced_accuracy (secondary); clap:coverage (diagnostic); mert:kid_song (primary); mert:c2st_balanced_accuracy (secondary); mert:coverage (diagnostic)

Candidates: 29 mix files (29 with windows); reference `corpus_accomp`: 29 files. Gates: `/home/user/long-exposure-runs/music-gen/data/v6/scorecard/gates_v6.json` (sha16 de7eeb897ee08f0a, key `references.corpus_accomp`). Seed 0, k=5, bootstrap 200. Candidates FORMAT-MATCHED to the reference: 22050 Hz / 1 ch (29 transformed, 0 already matched).

## clap (d=512; candidates 29 songs / 824 windows; reference 29 songs / 1451 windows) — **FLAG**

| metric | value | CI95 | noise floor (split-half 95%) | rule | verdict |
|---|---|---|---|---|---|
| kid_song | 0.0007987 | [0.000555, 0.001131] | [-7.642e-05, 9.746e-05] | FLAG if > 9.746e-05 and CI95 excludes 0 | FLAG |
| c2st_balanced_accuracy | 0.9256 | - | [0.3895, 0.6059] | FLAG if > 0.61 | FLAG |
| coverage | 0.2212 | - | [0.4925, 0.8298] | FLAG if < 0.4925 | FLAG |
| density | 2.455 | - | [1.619, 3.981] | info | INFO |
| fad | 0.2715 | - | [0.1133, 0.1652] | info (rank only) | INFO |
| knn_real_fraction | 0.006553 | - | [0.4249, 0.6308] | info (null expectation 0.6462) | INFO |
| kid_mean | 0.0008006 | - | [7.288e-05, 0.0002731] | info | INFO |
| novelty_max_cos | 0.951 | - | [0.9611, 0.9638] | FLAG song if max cos > 0.985 or >= 3 consecutive windows > 0.9638 on one ref song | PASS |

Novelty: no candidate song flagged.

Least real-like candidates (lowest kNN-real fraction; nearest reference song by cosine):
- `gen_v6_song_3_donor_cdd2717e52820ff6.wav`: kNN-real 0, max cos 0.9335 to `FKJ & Pomo - Lucky Star (Live)`
- `gen_v6_song_6_donor_b5133ee83b0e599f.wav`: kNN-real 0, max cos 0.9324 to `Corn on my Dinner Plate - Swing Dreams (OFFICIAL MUSIC VIDEO)`
- `gen_v6_song_10_donor_3fc418b996445d3a.wav`: kNN-real 0, max cos 0.9382 to `Dojo Cuts - Rome`

## mert (d=1536; candidates 29 songs / 824 windows; reference 29 songs / 1451 windows) — **FLAG**

| metric | value | CI95 | noise floor (split-half 95%) | rule | verdict |
|---|---|---|---|---|---|
| kid_song | 0.005829 | [0.004135, 0.00794] | [-0.0008597, 0.0007167] | FLAG if > 0.0007167 and CI95 excludes 0 | FLAG |
| c2st_balanced_accuracy | 0.9259 | - | [0.3724, 0.5626] | FLAG if > 0.57 | FLAG |
| coverage | 0.3136 | - | [0.6029, 0.8887] | FLAG if < 0.6029 | FLAG |
| density | 1.457 | - | [1.277, 4.427] | info | INFO |
| fad | 9.404 | - | [7.283, 8.45] | info (rank only) | INFO |
| knn_real_fraction | 0.007767 | - | [0.3658, 0.7553] | info (null expectation 0.6462) | INFO |
| kid_mean | 0.00645 | - | [0.001155, 0.00319] | info | INFO |
| novelty_max_cos | 0.9819 | - | [0.9803, 0.9809] | FLAG song if max cos > 0.995 or >= 3 consecutive windows > 0.9809 on one ref song | PASS |

Novelty: no candidate song flagged.

Least real-like candidates (lowest kNN-real fraction; nearest reference song by cosine):
- `ccfdf2028840a13f_22050hz_1ch.wav`: kNN-real 0, max cos 0.9784 to `Disco A`
- `37091fa60ff13cec_22050hz_1ch.wav`: kNN-real 0, max cos 0.9752 to `Don't Know What's Normal`
- `dcb6d6b40c9d67bc_22050hz_1ch.wav`: kNN-real 0, max cos 0.9763 to `Don't Know What's Normal`

## Audio descriptors (mix level)

Candidates n=29, reference n=29. Loudness/width/crest mismatches often explain embedding distance before timbre does.

| descriptor | candidates mean ± sd | reference mean ± sd | Δ (cand − ref) |
|---|---|---|---|
| lufs_integrated | -16.19 ± 0.553 | -17.2 ± 3.4 | 1.01 |
| crest_factor_db | 13.97 ± 0.922 | 14.97 ± 2.24 | -1 |
| spectral_centroid_hz | 2097 ± 363 | 1674 ± 444 | 424 |
| stereo_width_db | - | - | - |
| lr_correlation | - | - | - |
| peak_dbfs | -1.5 ± 0.917 | -1.074 ± 2.74 | -0.426 |
| rms_dbfs | -15.47 ± 0.66 | -16.04 ± 3.65 | 0.574 |

Wall 3239.7 s. Full numbers: `scorecard.json`, per-backbone `distribution_<backbone>.json`.
