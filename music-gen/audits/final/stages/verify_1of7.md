# Verify 1/7 — HALT-HONEST verdicts on M-V4-EAR-1 and M-V4-GEN-1

Slice covers explore.md §3 item **1** (HALT-HONEST verdicts on EAR-1 and
GEN-1).

## 1. L119 monotone-infeasibility proof (M-V4-EAR-1)

- File: `data/v4/ear/l119_infeasibility_proof_c76.json`
- Size: 9369 B, mtime 2026-09-05 23:58
- SHA-256: `ada44349277b17e0b2043c419403b2eed5f99046972aa31f94708f411b15a68a`
  (matches the sha pinned in explore.md and in the ledger event
  `M-V4-EAR-1/l119-infeasibility-proof-c76`).

Top-level keys: `['backbone', 'cycle', 'env_pin_sha256',
'infeasibility_verdict', 'milestone_id', 'n_band4_songs', 'n_exemplars',
'statistic_x_calibration_matrix']`.

- `backbone = vggish_only` — matches campaign-approved fallback after
  CLAP fetch-fail (c74).
- `cycle = 76` — matches ledger event cycle.
- `env_pin_sha256 = 2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca`
  — canonical 7-key subset. Matches the c22→c77 chain.
- `n_band4_songs = 3`, `n_exemplars = 5` — matches spec (3 band-4 spot
  check songs, 5 exemplars).

Sweep matrix depth verified: `statistic_x_calibration_matrix` contains
all 3 named statistics (`max_over_windows_c74`,
`mean_of_per_ex_max`, `mean_over_all_windows`); each expands into 3
calibrations (`linear_c74`, `sigmoid_dampen`, `wider_linear_c76`). Total
3×3 = 9 cells as the c76 report and ledger claim.

`infeasibility_verdict.all_three_statistics_raw_inverted = true`.
The `monotone_calibration_lemma` and `conclusion` strings are present
and read as formal claims, not slogans. The proof sidecar's shape is
consistent with a genuine infeasibility argument, not a placeholder.

Verdict for this leaf: on-disk evidence matches the HALT-HONEST claim
on M-V4-EAR-1. No finding.

## 2. 15 iteration A/B renders + REPLAY_PROOF_HOLDS (M-V4-GEN-1)

Enumerated 15 `data/v4/gen/iteration_{01,02,03}/gen_v4_song_*/ab_mix.wav`
files, each paired with an `ab_mix.replay_proof.json`.

| iteration | songs found | proofs found | verdict         | run1==run2 | env_pin_sha256 prefix |
|-----------|-------------|--------------|------------------|-----------:|-----------------------|
| iter_01   | 5/5         | 5/5          | REPLAY_PROOF_HOLDS | 5/5        | `2ac444c36298d6ad…`   |
| iter_02   | 5/5         | 5/5          | REPLAY_PROOF_HOLDS | 5/5        | `2ac444c36298d6ad…`   |
| iter_03   | 5/5         | 5/5          | REPLAY_PROOF_HOLDS | 5/5        | `2ac444c36298d6ad…`   |

All 15 A/B mix SHA-256 are **distinct** (15/15). Full SHA table (first
16 hex):

- iter_01: a1975327…, 8bfc7b6c…, 225a12dd…, 450dfbd3…, 4412394b…
- iter_02: f43a5701…, f7a5085a…, e40c7bcf…, 00e58872…, 156ad155…
- iter_03: d403e21c…, 11640117…, 833edbd6…, a9882815…, 882b5db4…

These SHAs byte-match the values pinned in the ledger's per-song
`M-V4-GEN-1/iteration-{01,02,03}/gen_v4_song_<N>` events.

Verdict for this leaf: HALT-HONEST_DELIVER_15 is substantively backed —
15 deterministic-replay-holding renders on disk, distinct across
iterations, matching the ledger's pinned SHAs and the canonical env_pin
prefix.

## 3. Stage 2 verdict for this slice

Both HALT-HONEST claims (EAR-1 infeasibility; GEN-1 deliver-15) are
consistent with on-disk state. No CRITICAL/MODERATE finding to append.

Findings appended: **0**.
