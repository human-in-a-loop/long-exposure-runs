# Verify Pass 2 of 23 (Stage 3 of 48)

**Slice:** VP-A #4 (M-EAR-1/head-regularization-audit c23), VP-A #5
(M-EAR-1/feature-representation-audit c25), VP-A #6
(M-DAW-SPIKE-1/palette-schema-v2-hydration-render c35).

All three are first-class invalidated milestones. All three are
load-bearing: they close Path A on the ear-model chassis (c22 → c23 →
c25 → c26 Path B commit) and the palette-schema-v2 render path (c35
RENDER_FAILS → c36 characterization → c33 anti-pattern preserved).

## VP-A #4 — M-EAR-1/head-regularization-audit (c23)

**Verdict:** CONFIRMED. Honest negative finding.

**Ledger status:** invalidated / high (cycle 23, 2026-08-28T18:45:28Z).

**Evidence:** `data/ear/head_regularization_audit/variant_verdicts.json`.

Three regularized CORN head variants, each measured under the frozen
c22 stability harness against the relaxed c23 rubric (C1' MAE-in-
envelope, C2' mean pairwise Kendall τ ≥ 0.4, C3' byte-determinism ×
2).

| Variant           | C1' (envelope [p05, p95]) | c6 MAE in envelope? | C2' (mean τ) | C3' | Overall |
|-------------------|---------------------------|---------------------|--------------|-----|---------|
| ridge             | [0.989, 1.898]            | 0.891 → FAIL (below) | 0.0766 → FAIL | PASS | FAIL |
| bottleneck        | [1.037, 1.936]            | 0.891 → FAIL (below) | 0.0605 → FAIL | PASS | FAIL |
| frozen_projector  | [1.013, 1.928]            | 0.891 → FAIL (below) | 0.0612 → FAIL | PASS | FAIL |

Every variant's envelope is strictly above the c6 baseline MAE 0.891 —
the c6 head sits below every variant's 5th percentile, meaning
regularization uniformly worsened MAE reproducibility relative to the
baseline. All three C2' means sit ~0.06 (near-zero rank agreement),
identical failure mode to c22 (τ = 0.0588). C3' PASSes uniformly
(three SHA-256 pairs each byte-equal across two independent runs).

Downstream load-bearing: this cycle's failure hands the ear-model
chassis question to c25 feature-representation-audit (VP-A #5 below).

## VP-A #5 — M-EAR-1/feature-representation-audit (c25)

**Verdict:** CONFIRMED. Honest negative finding. Closes Path A.

**Ledger status:** invalidated / high (cycle 25, 2026-08-28T20:06:17Z).

**Evidence:** `data/ear/feature_representation_audit/representation_verdicts.json`
and `vggish_deferral_note.json`.

Two representations trained under the UNCHANGED c22 harness and c23
rubric; VGGish deferred honestly because the cache was never
populated (`has_vggish=False` on the 55 valset clips).

| Representation | d_in  | C1' (envelope)      | c6 MAE in envelope? | C2' (mean τ)  | C3' | Overall  |
|----------------|-------|---------------------|---------------------|----------------|-----|----------|
| heur_only      | 4     | [0.815, 1.693]      | 0.891 → PASS        | −0.0756 → FAIL | PASS | FAIL |
| panns_only     | 2048  | [0.955, 2.040]      | 0.891 → FAIL (below)| 0.0064 → FAIL  | PASS | FAIL |
| vggish_only    | 128   | —                   | —                   | —              | —    | DEFERRED (cache not present) |

heur_only clears C1' (the low-D feature envelope brackets the c6 MAE)
but τ = −0.076 shows anti-correlated ranks across recipes. panns_only
mirrors the c22 pattern with a tighter envelope. Neither
representation delivers rank stability — the interpretation rule
pre-registered in the plan-of-record ("no-representation-passes →
c26 commits to Path B") fires cleanly.

Downstream load-bearing: this closes the three-cycle Path A
exhaustion. c26 emits `_manager/M-EAR-1-path-B-commit` (validated /
high per the plan) with three frozen real-label success bars (SB1
margin > 0.5909 derived from the c22 recipe-envelope IQR; SB2 τ ≥
0.4; SB3 leak-detection ≥ 0.90). The full v0/v1/v2/v2.1 real-label
campaign that followed exists BECAUSE of this negative finding.

VGGish deferral is honest and self-contained — the deferral note
names the concrete probe clip that failed and the missing feature.
Follow-up would just need a VGGish extractor run over the 55 valset
clips.

## VP-A #6 — M-DAW-SPIKE-1/palette-schema-v2-hydration-render (c35)

**Verdict:** CONFIRMED. RENDER_FAILS is honest; positive structural
findings survive as claimed.

**Ledger status:** invalidated / high (cycle 35, 2026-08-29T07:00:00Z).

**Evidence:** `data/palette_v2_render/verdict.json`, panel TSVs,
`data/vst3_nondeterminism/characterization_verdict.json` (c36).

Byte-determinism × 2 asserts:

- Combined: `bare_combined_sha_run1` `712e1a97…4b15` ≠ `run2`
  `ceaf12b7…030d`. `bare_combined_sha_equal: false` in verdict.
- Per-stem:
  - drums (fluidsynth_gm): run1 == run2 == `f66a776d…82c9` (SHA
    equal) but silent (`run1_peak_abs = 3.05e-05`, well below the
    1e-4 non-silence contract). See MINOR finding below.
  - bass (surge_xt, VST3): run1 `3e50c6ae…4e59a` ≠ run2 `c1ba6be9…99aa`.
    `n_params_set = 2855` (100% c33 P1 hydration coverage claimed
    in plan-of-record, confirmed on disk).
  - other (dexed, VST3): run1 `b530fd4e…5846` ≠ run2 `da868d9b…5f23`.
    `n_params_set = 2238` (100% c33 P1 hydration coverage confirmed).

The verdict is forced by the two VST3 stems (Surge XT + Dexed both
nondeterministic across fresh temp-dir runs). Three-way rubric_hash
chain byte-equal: doc SHA == `rubric_hash.txt` content == verdict
`rubric_hash` == `7d8841f0…014f`. RENDER_FAILS is one of the three
enum members in the frozen rubric — first-class negative outcome.

Cross-check against c36 M-DAW-SPIKE-1/vst3-render-nondeterminism-
characterization (MIXED verdict, validated/high per the same evidence
directory):

- Surge XT: STRUCTURAL. max_pairwise_rms = 0.098; max_pairwise_mel_l1_db
  = 0.186 dB; all 5 SHAs distinct across 5 fresh temp-dir runs.
- Dexed: SMALL. max_pairwise_rms = 1.99e-07; max_pairwise_mel_l1_db =
  5.54e-05 dB; median env-correlation = 1.0; all 5 SHAs distinct.

Both plugins produce distinct SHAs, which fully explains c35's
per-stem SHA inequality on both bass and other. c31 STILL_GAP + c35A
anti-pattern (do NOT re-attempt `get_state/save_state/set_state(bytes)`)
correctly stays locked; the VST3 nondeterminism is binary-internal,
not an API-usage bug.

Positive findings that survive under RENDER_FAILS (all confirmed):

- Schema-v2 activation end-to-end: three v2 assignments validated
  through both layers of `scripts.palette_v2.validate`; format
  discriminator `v1_flat` (drums) and `v2_iterated_params` (bass,
  other) both accepted.
- Hydration parameter coverage 100% (2855/2855 Surge, 2238/2238 Dexed).
- Panel deltas are large:
  - panel_original_vs_v1_bare_baseline: mel_l1_db 9.906, spectral
    centroid RMSE 2804.9 Hz.
  - panel_original_vs_v2: mel_l1_db 13.170 (+33%), spectral centroid
    RMSE 1779.3 Hz (−37%).
  - panel_v1_vs_v2: mel_l1_db 19.624 (~2× original baseline).

The panels can't confer LANDS under nondeterministic renders, but
they do demonstrate that v2 iterated-params hydration audibly
diverges from the v1 fluidsynth-only baseline (per plan claim of
"panel deltas 17-39× the 5% threshold").

Anchor preservation (`anchor_preservation.json`): snapshots the c33
dawdreamer_state P1 anchors (Surge + Dexed p1_state_sha, p1_state_v2.json,
p2/p3 sidecar SHAs) — post-block present, all READ-ONLY reads. No
c34 palette_v2 schema files modified.

Downstream load-bearing: c35 hands the VST3 nondeterminism question
to c36 characterization, which produced the SMALL/STRUCTURAL split
above. That in turn justifies the c35/c36 anti-pattern lock: no
future cycle may attempt VST3 palette rendering under a byte-
determinism contract until (a) a determinism-tolerance floor is
negotiated for SMALL-labeled plugins, or (b) an upstream DawDreamer
fix lands.

## MINOR findings (logged, not acted on)

1. **c35 drums stem silent under fluidsynth_gm fallback.** `per_stem[0]`
   for drums shows `run1_silent: true`, `run1_peak_abs: 3.05e-05` —
   below the M-TEX-1/panel non-silence contract of 1e-4. Impact on
   the RENDER_FAILS verdict: none (VST3 drift on bass+other forces the
   verdict regardless). Impact on positive-findings claim: the
   panel_original_vs_v2 mel_l1_db of 13.17 is measured on a mix that
   includes silent drums, so the delta reflects mostly bass+other +
   silence-vs-drums, not a clean palette-v2-vs-original test on the
   drums stem. Follow-up (out of audit scope) would rework the drums
   assignment onto a non-fallback fluidsynth path.

2. **c25 VGGish representation deferred.** `has_vggish=False` across
   all 55 cached feature clips means the VGGish rung of M-TEX-1/panel/
   embedding was cached during c13 but never propagated to the
   M-EAR-1/preparation feature cache. Impact on Path A closure: none
   — c26 explicitly notes VGGish is "deferred to follow-up cycle if
   VGGish not cached" and the two representations that did run both
   FAIL. Follow-up (out of audit scope) would just extract VGGish over
   the 55-clip valset via the already-fetched model.

## Files this stage

- `audits/final/stages/verify_2of23.md` (this file).
- Findings appended to `audits/final/findings.jsonl`: 3 ×
  `invalidation_verified` (severity `none`) + 2 × new MINOR
  (`silent_drums_under_fallback`, `vggish_representation_deferred`).

## Next slice (S4, verify 3/23)

Remaining first-class invalidated milestones to cover in later verify
passes; the specific slice for S4 will be assigned when its brief
arrives. Candidates for near-term passes:

- M-GEN-1/palette-driven-batch-v2-sampler-diversified (c35) — verdict
  SPREAD_STILL_COLLAPSED. Not yet verified this run.
- M-GEN-1/palette-driven-batch-v1 (c34) — verdict BATCH_SPREAD_COLLAPSED.
- Continue into the validated-milestone verify passes once first-class
  invalidations are cleared.
