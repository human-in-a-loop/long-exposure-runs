---
created: 2026-08-29T06:00:00Z
cycle: 35
run_id: run-2026-08-28T040704Z
agent: worker
milestone: M-GEN-1/palette-driven-batch-v2-sampler-diversified
---

# M-GEN-1/palette-driven-batch-v2-sampler-diversified — Frozen 3-verdict rubric

**Cycle 35, Branch B (clone-1, fork 07063458736e).**
**Locked BEFORE any script under `scripts/gen_palette_batch_v2/` lands.**
**Rubric SHA-256 is recorded in `data/gen_palette_batch_v2/rubric_hash.txt`
and embedded verbatim in `data/gen_palette_batch_v2/verdict.json` under
key `rubric_hash`.**

## Scope

A 3-song batch (salts 0, 1, 2). Response to the c34 clone-2 finding
that the c33 dispatcher `build_assignment_row` is `rule_id`-invariant
(3 salts × 2 runs produced byte-identical `bare_combined.wav` at SHA
`a8c1557c09470340aea0cb0556468117d67907292af35e2a351dbe9c212ba794`).

Two orthogonal per-salt differences are threaded:

1. **Per-salt DIFFERENT rule triples.** Per rule_type ∈ {harmonic,
   rhythmic, arrangement}, salts pick rank-0 by SHA-256 tiebreak on
   `sha256(f"{salt}|{rule_id}|{rule_type}".encode())` over the full
   candidate pool on `data/rules/ledger.jsonl`. Cross-salt distinctness
   enforced: on rule_id collision within a rule_type, the higher-salt
   clone falls to next rank. The base 76-row ledger has actual counts
   (H=10, R=18, M=18, F=15, A=15 — brief's "K=20 harmonic" was a
   carry-over typo from batch-v6's ledger_i3_dminor.jsonl; deviation
   noted here rather than in code).

2. **Pinned-state perturbation for Surge XT + Dexed only.** Each
   `(rule_id, param_name)` pair → SHA-256 rank-0 digest bytes 0..3 as
   uint32, mapped through a fixed typed lookup: float params → uniform
   over `[-δ, +δ]` via fixed-point arithmetic (δ per param-type); int
   params → modulo-N stride; bool → XOR bit-0. Wrap the c33
   dawdreamer_state P1 iterated-params output as `v2_iterated_params`
   payload; validate through c34 `scripts.palette_v2.validate` READ-ONLY.
   Drums stay fluidsynth-static (no perturbation).

**Every salt is rendered via c33 `scripts.palette_render.*` READ-ONLY
import** (drums→fluidsynth_gm, bass/other→sfizz|fluidsynth_gm per SFZ
fetchability). Each salt twice into fresh `tempfile.mkdtemp()` dirs;
SHA-256 equality asserted per-salt across runs; SHA-256 inequality
recorded (as OBSERVATION, not assertion) between salts.

## Numeric-family panel keys (4)

`mel_l1_db`, `spectral_centroid_rmse_hz`, `rms_env_rmse`, `lufs_m_rmse_lu`.

## Spread analysis

Per numeric-family key on each panel (`panel_original`,
`panel_fluidsynth`): IQR (linear-interp percentile) + `max − min`
across the 3 salts. Reported in `data/gen_palette_batch_v2/spread_analysis.json`.

Numeric tolerance for "spread present" = **1e-6** on IQR and max-min
(matches the numeric panel self-distance floor).

## Three verdicts (disjoint, exhaustive)

### SPREAD_ACHIEVED

ALL of:

1. For every one of the 4 numeric-family keys on `panel_original`,
   `IQR > 1e-6 AND max_minus_min > 1e-6`; AND
2. `bare_combined.wav` SHA-256 pairwise distinct across all 3 salts
   (3 distinct SHAs); AND
3. Per-salt byte-determinism holds × 2 runs (per-stem AND combined).

Interpretation: sampler-side diversification actually moved the panel
in a measurable way on every numeric axis, and the 3 salts produced
3 distinct WAV files.

### SPREAD_PARTIAL

Either:

- ≥1 but NOT all 4 numeric-family keys satisfy the spread thresholds
  on `panel_original`; OR
- ≥2 (but not all 3) salts yield pairwise-distinct
  `bare_combined.wav` SHA-256 values;

AND per-salt byte-determinism × 2 still holds. That is, the run
completed cleanly and there is SOME per-salt divergence, but not on
every axis of every panel.

### SPREAD_STILL_COLLAPSED

Either:

- All 3 salts still produce byte-identical `bare_combined.wav`
  (single distinct SHA); OR
- Numeric spread flat on every one of the 4 numeric-family keys of
  both panels (IQR ≤ 1e-6 AND max-min ≤ 1e-6 on every key of every
  panel).

**First-class negative finding.** Hands
`M-GEN-1/palette-driven-batch-v3` to c36 with concrete evidence:
deeper perturbation surface (bass/other pinned-state accepted by
`render_stem` CLI) OR generator-swap (replace c33 fluidsynth/sfizz
dispatch with a per-rule-parameterized synth) OR both.

The report MUST expose the mechanism (what the sampler DID diverge
on and where the divergence failed to reach the audio path).

## Silent fourth bucket: BATCH_FAILS

Reserved for render-fail. Reported only if triggered:

- Any per-stem `render_run{1,2}.wav.sha` mismatch (byte-determinism ×2 fails).
- Any per-salt `bare_combined.wav.sha.run1 ≠ .run2`.
- Any panel returns fewer than 8 finite numeric-family keys, or a
  finite-family key is NaN / ±inf.
- Any assignment row rejects `scripts.palette.validate.validate_row`
  (Layer 1 or Layer 2).

If BATCH_FAILS did not fire, the field is absent from `verdict.json`.

## Exhaustiveness

The verdict function evaluates:

1. **BATCH_FAILS** gate first (any render-fail).
2. Then: SHA-distinct-count in {1, 2, 3} + per-key numeric-spread flags:
   - 3 distinct SHAs AND every numeric key on `panel_original` exceeds
     spread tolerance → **SPREAD_ACHIEVED**.
   - 1 distinct SHA (fully collapsed) → **SPREAD_STILL_COLLAPSED**.
   - Every numeric key on both panels below spread tolerance →
     **SPREAD_STILL_COLLAPSED** (numeric-collapse form).
   - Otherwise → **SPREAD_PARTIAL**.

Every outcome maps to exactly one verdict.

## Post-cycle discipline

- The rubric is FROZEN. Its SHA-256 is recorded in
  `data/gen_palette_batch_v2/rubric_hash.txt` and embedded verbatim
  in `data/gen_palette_batch_v2/verdict.json.rubric_hash`. A test
  asserts byte equality between the two.
- The rubric MUST NOT be edited retroactively. If a follow-up cycle
  proposes a different threshold, that is a new peer sub-milestone
  with its own rubric.
- The M-GEN-1 verdict roll-up event carries `status = validated` on
  any of SPREAD_ACHIEVED / SPREAD_PARTIAL / SPREAD_STILL_COLLAPSED
  (all are legitimate findings under the frozen rubric) and
  `status = invalidated` on BATCH_FAILS.

## Anchors, honesty, exclusions

- c34 palette_v2 (`scripts/palette_v2/*`, `data/palette_v2/*`) —
  READ-ONLY; validator invoked at authoring time via
  `scripts.palette_v2.validate.validate_row_v2`.
- c33 palette_render (`scripts/palette_render/*`) — READ-ONLY.
- c33 dawdreamer_state (`scripts/dawdreamer_state/*`,
  `data/dawdreamer_state/*`) — READ-ONLY; per-plugin P1 anchor
  consumed at authoring time.
- c31 palette_v1 (`scripts/palette/*`, `data/palette/*`) — READ-ONLY.
- c26/27/28/29/30 analytical utilities, c22 stability harness — MUST
  NOT import (AST-grep enforced).
- c15 `scripts/rules/sampling/i4_stratified.py` — MUST NOT import.
- c13 batch-v2 pipeline, c9 effects chain — MUST NOT import.
- `data/rules/ledger.jsonl` — READ-ONLY streaming only (base 76-row
  ledger). `data/rules/ledger_i3_dminor.jsonl` MUST NOT be read.
- No PRNG (`random`, `numpy.random`, `torch.*seed`, `secrets`,
  `os.urandom`) — AST-grep clean.
- No `sidecar_nonfactor` imports.
- Interpreter guard `/usr/bin/python3` on every new script.
- Do NOT emit any `M-EAR-1/*` events.

## Frozen. Do not edit after commit.
