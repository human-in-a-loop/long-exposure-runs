# v6 Phase 1A — real-vs-real baseline (noise floor)

Corpus: 29 songs, bands {'4': 9, '5': 16, '7': 4}; splits=20, seed=0, window/hop from embed sidecars; k=5.

## clap (d=512, 1459 windows)

| metric | split-half mean | sd | 95% range [p2.5, p97.5] | band-vs-band (min..max) | leave-one-band-out (min..max) |
|---|---|---|---|---|---|
| kid_song | 8.04e-06 | 8.38e-05 | [-8.77e-05, 0.0001986] | -5.449e-05..0.0001209 | -7.839e-05..9.787e-05 |
| kid_mean | 0.0002068 | 0.0001004 | [9.012e-05, 0.0004242] | 0.0003087..0.0003731 | 0.0002506..0.0003217 |
| fad | 0.1548 | 0.02459 | [0.1227, 0.207] | 0.2004..0.2553 | 0.1608..0.2004 |
| c2st_balanced_accuracy | 0.4941 | 0.09516 | [0.3304, 0.666] | 0.3213..0.4935 | 0.4178..0.4548 |
| knn_real_fraction | 0.5234 | 0.1064 | [0.3704, 0.7168] | 0.265..0.6742 | 0.5103..0.9838 |
| density | 2.423 | 0.7407 | [1.368, 3.801] | 1.763..4.493 | 1.975..3.652 |
| coverage | 0.7067 | 0.1247 | [0.4671, 0.9042] | 0.5872..1 | 0.3407..0.7711 |
| novelty_max_cos | 0.9667 | 0.00331 | [0.9595, 0.9686] | 0.9546..0.9686 | 0.9633..0.9686 |

Song-level KID bootstrap CI covered 0 in 100% of split-halves (target ~95%). Window-level KID has a positive floor of 0.0002068 (within-song clustering) and is reported for reference only. FAD across splits: mean 0.1548, CV 0.16; FAD is never near 0 at this n (covariance estimation in d=512 from ~729 windows per half), so it can rank candidate sets but has no absolute meaning here. C2ST noise floor [0.33, 0.666]; band-vs-band C2ST 0.321..0.493 — bands above the floor: none; bands with KID CI excluding 0: none.

MUSDB18: absent 

## mert (d=1536, 1459 windows)

| metric | split-half mean | sd | 95% range [p2.5, p97.5] | band-vs-band (min..max) | leave-one-band-out (min..max) |
|---|---|---|---|---|---|
| kid_song | -6.67e-05 | 0.000391 | [-0.00049, 0.000851] | 0.0001666..0.002112 | 0.0001608..0.001829 |
| kid_mean | 0.001458 | 0.0003622 | [0.001047, 0.002239] | 0.001903..0.006276 | 0.001594..0.005115 |
| fad | 5.818 | 0.229 | [5.426, 6.236] | 6.737..9.802 | 5.973..8.312 |
| c2st_balanced_accuracy | 0.4777 | 0.05916 | [0.3578, 0.5485] | 0.43..0.628 | 0.4261..0.5169 |
| knn_real_fraction | 0.538 | 0.1043 | [0.3131, 0.7029] | 0.2076..0.7053 | 0.4437..0.9124 |
| density | 2.384 | 0.7118 | [1.26, 3.627] | 1.392..2 | 1.368..2.798 |
| coverage | 0.7384 | 0.09294 | [0.5551, 0.8626] | 0.5658..0.9946 | 0.2457..0.9107 |
| novelty_max_cos | 0.9861 | 0.001457 | [0.984, 0.9874] | 0.9811..0.9847 | 0.9834..0.9847 |

Song-level KID bootstrap CI covered 0 in 100% of split-halves (target ~95%). Window-level KID has a positive floor of 0.001458 (within-song clustering) and is reported for reference only. FAD across splits: mean 5.818, CV 0.04; FAD is never near 0 at this n (covariance estimation in d=1536 from ~729 windows per half), so it can rank candidate sets but has no absolute meaning here. C2ST noise floor [0.358, 0.548]; band-vs-band C2ST 0.43..0.628 — bands above the floor: ['band4_vs_band7']; bands with KID CI excluding 0: none.

MUSDB18: absent 

## Which metrics are usable at n=29

- **Song-level KID with the two-level bootstrap** is the primary gate: its null expectation is 0 by construction, the CI coverage above says whether the bootstrap is calibrated, and a candidate set whose CI excludes 0 *and* whose point estimate exceeds the split-half p97.5 is distinguishable from real.
- **C2ST-kNN (song-aware)** is the secondary gate: compare a candidate's value with the split-half 95% range; it is scale-free and the same across backbones, which makes it the easiest number to read.
- **Coverage / density** are diagnostics (diversity vs realism); gate only on coverage falling below the split-half p2.5.
- **FAD** is reported but not recommended as a gate at this sample size: the Ledoit-Wolf covariance is shrunk heavily (n << 10 d), the estimate is biased upward and its split-to-split spread is shown above.
- **Window-level KID (subsets)** carries a within-song-clustering bias; prefer the song-level estimate.
- **Novelty guard** (max cosine to any reference window) is a hard flag, not a distribution statistic; the split-half column shows the real-vs-real ceiling, so a threshold must sit clearly above it.
