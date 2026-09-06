# Stage 5 — verify 4 of 7: M-V4-GEN-1 iterations 1-3 byte-determinism

## Scope

Verify per operator directive: 3 iterations × 5 songs = 15 renders under
c72/c73/c74 M-V4-GEN-1 pipeline. Each per-song `ab_mix.replay_proof.json`
must carry `REPLAY_PROOF_HOLDS` with `run1_sha256 == run2_sha256 ==
sha256(ab_mix.wav)`; `env_pin_sha256` must equal the canonical 7-key
subset `2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca`;
all 15 mix SHAs must be pairwise distinct across the 3 iterations.

## Method

Deterministic Python probe walked `data/v4/gen/iteration_{01,02,03}/gen_v4_song_{1..5}_donor_*/`
for all 15 cells. For each cell:

1. Read `ab_mix.wav`, compute SHA-256.
2. Read `ab_mix.replay_proof.json`, extract `verdict`, `run1_sha256`,
   `run2_sha256`, `env_pin_sha256`.
3. Cross-check against POR-pinned expected SHAs.
4. Aggregate distinctness across the 15-cell set.

Also verified presence of `iteration_rollup.json` under each iteration
directory and inspected `ear_score` field across all 15 manifests.

## Results

- **15/15 cells verified**: every cell has both `ab_mix.wav` and
  `ab_mix.replay_proof.json` on disk.
- **15/15 verdicts = `REPLAY_PROOF_HOLDS`**.
- **15/15 `run1_sha256 == run2_sha256 == sha256(ab_mix.wav)`** — byte-determinism
  × 2 holds end-to-end.
- **15/15 SHAs match POR pinning** (iter-01/02/03 anchors).
- **15/15 `env_pin_sha256 == 2ac444c3…922ca`** — canonical replay-time
  7-key subset unchanged across all three iterations.
- **15/15 distinct SHAs across iterations** (seed 0/1/2 shift produces
  distinct novel MIDI as expected).
- **3/3 `iteration_rollup.json` present**.
- **15/15 `ear_score == null`** — consistent with M-V4-EAR-1 HALT-HONEST
  under L119 monotone-infeasibility (c76 anchor); operator ear delegated
  as authoritative gate per FD-6.

## Verdict

**PASS**. All discipline invariants hold: FD-1 halt-honest applies (null
ear_score honestly disclosed, not fabricated); FD-16(a) env_pin cert
unchanged; FD-16(c) 15 replay proofs cover the M-V4-GEN-1 per-family
per-song scope; c47 preservation-spin BAN respected; no PRNG /
sidecar_nonfactor / VST3 state APIs surfaced in gen pipeline outputs.

## Findings

**No new findings this stage.** The 15-cell REPLAY_PROOF_HOLDS chain is
byte-consistent with POR row narratives at c72 P2, c73 P2.b, c74 P1 and
with the c73 P2.c iter-01 manifest backfill (byte-identical WAV verified
during that backfill, unchanged here).

## Status Receipt

Stage 5 (verify 4/7): PASS 15/15; no new findings appended.
