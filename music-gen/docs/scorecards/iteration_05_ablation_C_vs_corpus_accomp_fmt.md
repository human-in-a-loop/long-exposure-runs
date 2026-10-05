# v6 scorecard — iteration_05_ablation_C_vs_corpus_accomp_fmt

Overall verdict: **FLAG** — clap:kid_song (primary); clap:c2st_balanced_accuracy (secondary); clap:coverage (diagnostic)

Candidates: 29 mix files (29 with windows); reference `corpus_accomp`: 29 files. Gates: `/home/user/long-exposure-runs/music-gen/data/v6/scorecard/gates_v6.json` (sha16 de7eeb897ee08f0a, key `references.corpus_accomp`). Seed 0, k=5, bootstrap 200. Candidates FORMAT-MATCHED to the reference: 22050 Hz / 1 ch (0 transformed, 29 already matched).

## clap (d=512; candidates 29 songs / 841 windows; reference 29 songs / 1451 windows) — **FLAG**

| metric | value | CI95 | noise floor (split-half 95%) | rule | verdict |
|---|---|---|---|---|---|
| kid_song | 0.0009668 | [0.0007257, 0.001298] | [-7.642e-05, 9.746e-05] | FLAG if > 9.746e-05 and CI95 excludes 0 | FLAG |
| c2st_balanced_accuracy | 0.9355 | - | [0.3895, 0.6059] | FLAG if > 0.61 | FLAG |
| coverage | 0.1909 | - | [0.4925, 0.8298] | FLAG if < 0.4925 | FLAG |
| density | 1.638 | - | [1.619, 3.981] | info | INFO |
| fad | 0.2994 | - | [0.1133, 0.1652] | info (rank only) | INFO |
| knn_real_fraction | 0.008561 | - | [0.4249, 0.6308] | info (null expectation 0.6414) | INFO |
| kid_mean | 0.000934 | - | [7.288e-05, 0.0002731] | info | INFO |
| novelty_max_cos | 0.9521 | - | [0.9611, 0.9638] | FLAG song if max cos > 0.985 or >= 3 consecutive windows > 0.9638 on one ref song | PASS |

Novelty: no candidate song flagged.

Least real-like candidates (lowest kNN-real fraction; nearest reference song by cosine):
- `gen_v6_song_26_donor_98af4505ea239661.wav`: kNN-real 0, max cos 0.9285 to `Dojo Cuts - Rome`
- `gen_v6_song_2_donor_51e433ade2a845e1.wav`: kNN-real 0, max cos 0.9355 to `Don't Know What's Normal`
- `gen_v6_song_15_donor_87cabfc2e3a48d0c.wav`: kNN-real 0, max cos 0.9443 to `Corn on my Dinner Plate - Swing Dreams (OFFICIAL MUSIC VIDEO)`

## Audio descriptors (mix level)

Candidates n=29, reference n=29. Loudness/width/crest mismatches often explain embedding distance before timbre does.

| descriptor | candidates mean ± sd | reference mean ± sd | Δ (cand − ref) |
|---|---|---|---|
| lufs_integrated | -15.94 ± 0.497 | -17.2 ± 3.4 | 1.26 |
| crest_factor_db | 13.95 ± 0.633 | 14.97 ± 2.24 | -1.02 |
| spectral_centroid_hz | 1865 ± 283 | 1674 ± 444 | 191 |
| stereo_width_db | - | - | - |
| lr_correlation | - | - | - |
| peak_dbfs | -1.213 ± 0.55 | -1.074 ± 2.74 | -0.139 |
| rms_dbfs | -15.16 ± 0.556 | -16.04 ± 3.65 | 0.884 |

Wall 155.8 s. Full numbers: `scorecard.json`, per-backbone `distribution_<backbone>.json`.
