---
created: 2026-09-03T00:00:00Z
run_id: run-2026-09-03T000000Z
cycle: 25
agent: worker
milestone: M-V3-SPINE-1/wig-palette-render-c25
---

# What If I Go Surge XT / sfizz Palette Render — Cycle 25 Rubric (frozen)

Song: What If I Go, `audio_sha16 = 252eb21ce7df7328`, operator-section
`t = 72.77133786848073 .. 102.77133786848073 s` (per
`data/recreate_v2/focus_set_v2.json.chosen_section`).

This rubric is committed BEFORE any Python edit under
`scripts/v3_spine/palette_render_wig/`. The rubric SHA is pinned to
`data/v3_spine/252eb21ce7df7328/palette_render/rubric_hash_v2.txt`.
Three-way `rubric_hash_v2` byte-equality is asserted at verdict time
(doc SHA-256 == `rubric_hash_v2.txt` content ==
`verdict_palette.json.rubric_hash_v2`).

This rubric mirrors the c21 Chicken Grease palette-render rubric
(`docs/v3_spine_chicken_grease_palette_render_c21_rubric.md`, SHA
`9eb5523cbd090c388e30b0b271cb1dffd4f321ed907c78be122f56cbad5e1879`).
Extending the palette proof from Chicken Grease (band 6, mandatory) to
What If I Go (band 5, operator-ear-approved 2026-09-02) gives the
operator a second focus-song A/B on the palette pipeline. Per operator
decision D-D (2026-09-02): if the operator confirms audible improvement
on this A/B in a future cycle, palette becomes primary campaign-wide.

## Frozen 3-verdict rubric

### PALETTE_MOVES_PANEL

All of:

1. Every per-stem render succeeds OR is honestly logged as a
   REDEFINED_GAP or SMALL_PERTURBATION_TOLERABLE arm with fallback data
   present.
2. Per-stem byte-determinism × 2 holds on each rendered WAV OR the
   VST3-stem's 3-fresh-tempdir pairwise RMS envelope satisfies
   `max_pairwise_rms ≤ 1e-4` per the c36 small-perturbation
   characterization (SMALL_PERTURBATION_TOLERABLE arm).
3. Comparison B panel — `(c21 WIG operator-blessed
   full_reconstruction_operator_section.wav, palette-render)` on the
   operator section — shows delta magnitudes exceeding the 5% relative
   threshold on ≥ 3 of the 5 numeric panel keys (matches the c21 CG
   rubric verbatim).
4. c21 WIG operator-blessed delivery byte-identical pre==post (hard).
   Manifest SHA `9a8a09d0f553a79f9304da0348fa7f1234a91f76f26f1037079bf40b6c414454`
   preserved. Chicken Grease c21 palette-render anchors preserved.
   Preserved v3-spine scripts (`recreate_v3.py`, `env_pin.py`,
   `midi_from_json_events.py`, `render_stem.py`, `rc7_v2_rerun_v3_paths.py`,
   `mix_match_operator_section.py`) all SHA byte-identical pre==post.

### PALETTE_NEUTRAL

Renders succeed and byte-determinism gate holds, but Comparison B panel
delta magnitudes fall below the 5% threshold on 3 or more of the 5
numeric keys (i.e. `< 3/5` exceed threshold).

### RENDER_FAILS

Any of:

- Per-stem byte-determinism × 2 fails on a non-VST3 stem without a
  documented REDEFINED_GAP arm, OR
- Bass VST3 render fails all 3 fresh-tempdir attempts AND
  `max_pairwise_rms > 1e-4` (structural drift) AND the
  `fluidsynth_gm(33)` REDEFINED_GAP arm ALSO fails byte-det × 2.
- Fetchability failure that leaves any required stem without a
  renderable pipeline (fluidsynth_gm fallback failure counts).
- Either comparison panel returns non-finite on any of the 8 keys.
- c21 WIG operator-blessed delivery drifts (any anchor SHA changes),
  OR Chicken Grease c21 palette-render anchors drift, OR any preserved
  v3-spine script SHA drifts.

## REDEFINED_GAP arm (bass VST3)

Allowed on the bass stem only, following the c21 CG precedent and c36
characterization: Surge XT VST3 on Chicken Grease-family content
exhibited structural drift `max_pairwise_rms ≈ 0.068 >> 1e-4`. If WIG
bass content exhibits the same class of drift, engage the
`fluidsynth_gm(33 electric bass finger)` fallback honestly. The VST3
attempt shape (shas, outcome, max_pairwise_rms) MUST be recorded
verbatim in `data/v3_spine/252eb21ce7df7328/palette_render/fetchability_ladder.jsonl`
and in the per-stem `dispatch_summary.json` with
`arm_engaged: redefined_gap`. c31 STILL_GAP + c35 A anti-patterns
remain locked: DO NOT re-attempt VST3 `get_state`/`save_state`/`save_preset`/
`load_state`/`set_state(bytes)` APIs.

## Panel-is-never-a-LANDS-gate reminder (FD-6)

The panel is a diagnostic measurement, not a LANDS gate. The rubric
above fires `PALETTE_MOVES_PANEL` on the *comparison B delta magnitude
criterion*; it never fires LANDS on any panel-numeric-passes-threshold.
Operator ear remains the only LANDS authority per FD-6. This cycle's
verdict carries `blocked_on_operator: true`; the c21 WIG
operator-blessed delivery is a sibling reference. If a future-cycle
operator ear confirms this palette A/B improves audibly on the c21 WIG
fluidsynth reference, palette becomes primary campaign-wide per
operator D-D (2026-09-02).

## Per-stem dispatch (mirrors c21 CG verbatim)

- **drums** — fluidsynth channel 10 (c21 pattern unchanged).
- **bass** — Surge XT VST3 via DawDreamer with c33 P1 iterate-params
  hydration; on structural drift, `fluidsynth_gm(33)` REDEFINED_GAP arm.
- **guitar** — sfizz probe → `fluidsynth_gm(25 clean electric)` fallback.
- **piano** — sfizz probe → `fluidsynth_gm(0 acoustic grand)` fallback.
- **other** — sfizz probe → `fluidsynth_gm(88 new age pad)` fallback.
- **vocals** — verbatim D2 copy from c21 WIG delivery's
  `data/v3_spine/252eb21ce7df7328/operator_section/render/vocals_htdemucs.wav`
  (SHA-verified before copy).

Apply c6 Method B iirpeak EQ (12-band, `Q=1.4`,
`np.geomspace(20, 20000, 12)`) + RMS + LUFS-S loudness match per stem
via READ-ONLY import of `scripts/v3_spine/rc7_v2_rerun_v3_paths.py`
and `scripts/palette_render/render_stem.py` (SHA
`214372d920a319a97d6e3fc7b9ee4134c08c0cb4aecb776f4a50c75f965b5b2b`
byte-identical pre==post — MUST NOT MUTATE).

## Env pins

Every renderer + panel + delivery script sets, before any observed
import:

    PYTHONHASHSEED=0
    SOURCE_DATE_EPOCH=1756463424
    TZ=UTC
    LC_ALL=C.UTF-8
    OMP_NUM_THREADS=1
    MKL_NUM_THREADS=1
    OPENBLAS_NUM_THREADS=1
    torch.manual_seed(0)  (where torch is imported)

`c48` env-var flags default OFF via `os.environ.setdefault`:
`MUSICGEN_LEDGER_SUBSTANTIVE_EXEMPTION`, `MUSICGEN_LEDGER_SUPERSEDES_IN_HASH`.

## Delivery contract

Sibling to c21 WIG operator-blessed delivery under
`data/v3/deliveries/252eb21ce7df7328/palette_render_c25/`:

- `full_reconstruction_palette.wav`
- `per_stem/<stem>/render.wav` (6 files: drums, bass, guitar, piano,
  other, vocals)
- `manifest.json` with `env_pins` block + self-anchor
  `env_pin_sha256` (c22 env_pin module SHA
  `ab6d54638faeb161d75dcecdb5682280155304a5c5d8dea1966d25c204556654`
  READ-ONLY import)
- `byte_determinism.json`
- `fetchability_ladder.jsonl`
- `panel_original_vs_palette.tsv`
- `panel_fluidsynth_vs_palette.tsv`
- `verdict.json` with three-way `rubric_hash_v2` byte-equality,
  `blocked_on_operator: true`, `sub_clause_status` + `sub_artifact_shas`.

## Anchor preservation ≥30 SHAs

Snapshot at
`data/v3_spine/252eb21ce7df7328/palette_render/anchor_preservation.json`
covers ≥30 anchors:

- c21 WIG operator-blessed delivery under
  `data/v3/deliveries/252eb21ce7df7328/operator_section/`
  (manifest `9a8a09d0f553a79f…`; full_reconstruction, original_ab,
  reconstruction_ab, panel.json/tsv).
- c21 WIG operator_section under
  `data/v3_spine/252eb21ce7df7328/operator_section/` (section.wav,
  rc9_6stem/{6 stems}, canonical_midi/{7 mids}, render/*,
  merged.mid, merged_report.json, tempo_choice.json).
- c21 CG palette delivery: verdict `5ba4eaca242fcd29…`, rubric doc
  `9eb5523cbd090c388e30b0b271cb1dffd4f321ed907c78be122f56cbad5e1879`,
  CG palette full_reconstruction, per_stem WAVs.
- Preserved v3-spine scripts: `scripts/v3_spine/recreate_v3.py`
  (`72e80ee82cd21dbdc9422ca1ee9770c85e9f42d9085231a90d00d12bb5b2bfc8`),
  `scripts/v3_spine/v3_pipeline/env_pin.py`
  (`ab6d54638faeb161d75dcecdb5682280155304a5c5d8dea1966d25c204556654`),
  `scripts/v3_spine/midi_from_json_events.py`
  (`bbff015f4f1833f446ad72f9cd5815117b2a744798fe3857edf468de6731a2ea`),
  `scripts/palette_render/render_stem.py`
  (`214372d920a319a97d6e3fc7b9ee4134c08c0cb4aecb776f4a50c75f965b5b2b`),
  `scripts/v3_spine/rc7_v2_rerun_v3_paths.py`,
  `scripts/v3_spine/mix_match_operator_section.py`,
  `scripts/recreate_v2/rc7_mix_balance.py`.
- SF2 SHA `74594e8f4250680adf590507a306655a299935343583256f3b722c48a1bc1cb0`.
- `data/recreate_v2/focus_set_v2.json` + rubric-v2 chain
  `c49db5a12e955f26c001165ad6e8f9d191bc26bfd96e24c1b163adc37016451a`.
- `plan_of_record.md`.

Snapshot pre and post; `all_match=true`, `n_mismatch=0`.

## Anti-patterns preserved

- **VST3 state extraction** (c31 STILL_GAP + c35 A):
  `get_state`, `save_state`, `save_preset`, `load_state`,
  `set_state(bytes)`, `get_state_chunk`, `getChunk` all AST-forbidden.
- **CLAP fetch** (c11): VGGish rung authoritative; do not attempt
  CLAP re-fetch.
- **M-EAR-1 Path A audits under N=55** (c22/c23/c25): do NOT emit any
  `M-EAR-1/*` events from this clone.
- **PRNG in pipeline scripts**: no `random`, no unseeded
  `numpy.random`/`torch.randn`. SHA-256 tiebreaks only.
- **`sidecar_nonfactor` imports**: forbidden.
- **`render_stem.py` mutation**: SHA
  `214372d920a319a97d6e3fc7b9ee4134c08c0cb4aecb776f4a50c75f965b5b2b`
  MUST be byte-identical pre==post. Only READ-ONLY import.

## Verdict shape

```
verdict ∈ {PALETTE_MOVES_PANEL, PALETTE_NEUTRAL, RENDER_FAILS}
rubric_hash_v2 == doc SHA-256
rubric_hash_v2 == rubric_hash_v2.txt content
sub_clause_status: {per_stem_render_success, per_stem_byte_det_or_envelope,
                    panel_a_8_keys_finite, panel_b_8_keys_finite,
                    comparison_b_keys_exceeding_threshold,
                    comparison_b_threshold_met}
sub_artifact_shas: {full_reconstruction_palette_wav, per_stem_wav (6),
                    canonical_midi (7), delivery_manifest_json}
blocked_on_operator: true
```
