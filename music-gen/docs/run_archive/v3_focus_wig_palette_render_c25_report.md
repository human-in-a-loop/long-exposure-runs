---
created: 2026-09-03T00:20:00Z
run_id: fork-4c826786aced-clone-2
cycle: 25
agent: worker
milestone: M-V3-SPINE-1/wig-palette-render-c25
---

# What If I Go — Surge XT / sfizz Palette Render (Cycle 25, clone-2)

## Verdict

**`PALETTE_MOVES_PANEL`** — Comparison B (c21 WIG operator-blessed
fluidsynth reference vs c25 palette render) shows delta magnitudes
exceeding the 5% relative threshold on **5 / 5 numeric keys**. All
render + panel + anchor sub-clauses hold. Operator ear on the A/B is
the only LANDS authority per FD-6; verdict carries
`blocked_on_operator: true`. Per operator D-D 2026-09-02: if operator
confirms audible improvement on this A/B, palette becomes primary
campaign-wide.

- Rubric doc SHA: `80fc4b60bbc475738b8dc641e9d698f4f0c1bacb923b8b2eca40c9a8c01a1a50`
- Three-way `rubric_hash_v2` chain byte-equal: doc SHA == `rubric_hash_v2.txt` == `verdict.rubric_hash_v2`
- Verdict path: `data/v3/deliveries/252eb21ce7df7328/cycle25/verdict_palette.json` (SHA `e8285ceed4c133b6…`)
- Delivery: `data/v3/deliveries/252eb21ce7df7328/palette_render_c25/`

## Context

Second focus-song palette A/B after c21 Chicken Grease (verdict
`5ba4eaca242fcd29…`, `PALETTE_MOVES_PANEL`). What If I Go
(`sha16 252eb21ce7df7328`) was operator-ear-approved on the c21
fluidsynth chain 2026-09-02 and is the natural second candidate for
the palette proof required to unlock the campaign-wide flip.

Operator-section coordinates from `data/recreate_v2/focus_set_v2.json`:
`t = 72.77133786848073 .. 102.77133786848073 s` (30 s).

## What was built

- `docs/v3_spine_wig_palette_render_c25_rubric.md` — rubric doc,
  landed mtime-hard BEFORE any script under
  `scripts/v3_spine/palette_render_wig/` (verified in test 01).
- `data/v3_spine/252eb21ce7df7328/palette_render/rubric_hash_v2.txt`
  — pinned SHA `80fc4b60bbc475738b8dc641e9d698f4f0c1bacb923b8b2eca40c9a8c01a1a50`.
- `scripts/v3_spine/palette_render_wig/__init__.py`
- `scripts/v3_spine/palette_render_wig/render_palette.py` — per-stem
  dispatch mirroring c21 CG verbatim.
- `scripts/v3_spine/palette_render_wig/mix_and_deliver.py` — c6
  Method B iirpeak-EQ + RMS + LUFS-S loudness match chain via
  READ-ONLY import of `scripts/palette_render/render_stem.py`
  (SHA `214372d920a319a9…5b2b` byte-identical pre==post) and
  `scripts/recreate_v2/rc7_mix_balance.py`; delivery emission +
  env-pin self-anchor via READ-ONLY import of
  `scripts/v3_spine/v3_pipeline/env_pin.py`.
- `scripts/v3_spine/palette_render_wig/panels_and_verdict.py` — two
  `M-TEX-1/panel` measurements + verdict emission with three-way
  rubric-hash chain assertion.
- `scripts/v3_spine/palette_render_wig/anchor_preservation.py` — pre/post
  56-anchor snapshot (exceeds ≥30 target).
- `tests/test_v3_spine_wig_palette_render_c25.py` — 15/15 tests green.

## What was run

Under env pins (`PYTHONHASHSEED=0`, `SOURCE_DATE_EPOCH=1756463424`,
`TZ=UTC`, `LC_ALL=C.UTF-8`, `OMP_NUM_THREADS=1`, `MKL_NUM_THREADS=1`,
`OPENBLAS_NUM_THREADS=1`):

```
/usr/bin/python3 scripts/v3_spine/palette_render_wig/anchor_preservation.py --phase pre
/usr/bin/python3 scripts/v3_spine/palette_render_wig/render_palette.py
/usr/bin/python3 scripts/v3_spine/palette_render_wig/mix_and_deliver.py
/usr/bin/python3 scripts/v3_spine/palette_render_wig/panels_and_verdict.py
/usr/bin/python3 scripts/v3_spine/palette_render_wig/anchor_preservation.py --phase post
/usr/bin/python3 tests/test_v3_spine_wig_palette_render_c25.py
```

## Per-stem dispatch outcomes

| stem | pipeline | outcome | byte-det ×2 | notes |
|------|----------|---------|-------------|-------|
| drums  | fluidsynth ch10 (c21 pattern)             | ok  | true | canonical MIDI drives ch10 |
| bass   | Surge XT VST3 → fluidsynth_gm(33) fallback | **REDEFINED_GAP arm** | true | VST3 `max_pairwise_rms=0.041 >> 1e-4` c36 envelope; fluidsynth_gm(33 electric bass finger) fallback engaged honestly and byte-det ×2 |
| guitar | sfizz probe → fluidsynth_gm(25)            | ok (fallback) | true | sfz_dir_missing (workspace/palette/sfz/ empty) |
| piano  | sfizz probe → fluidsynth_gm(0)             | ok (fallback) | true | same |
| other  | sfizz probe → fluidsynth_gm(88)            | ok (fallback) | true | same |
| vocals | verbatim D2 htdemucs copy from c21 WIG     | ok  | true | SHA-verified before copy |

VST3 characterization preserved verbatim in
`data/v3_spine/252eb21ce7df7328/palette_render/fetchability_ladder.jsonl`
with `outcome: structural_drift, max_pairwise_rms: 0.041`. c31
STILL_GAP + c35 A anti-patterns remain locked — VST3 state APIs not
re-attempted.

## Panels (Comparison A + B)

Both panels return 8 finite keys per `M-TEX-1/panel` contract (test 09).
Panel is NEVER a LANDS gate per FD-6.

### Comparison B (c21 WIG fluidsynth vs c25 palette) — the palette proof

| key | reference (c21 vs original) | test (palette vs c21) | rel-delta | exceeds 5% |
|-----|------:|------:|------:|:--:|
| mel_l1_db                | 9.5946   | 4.9257  | 0.4866 | ✓ |
| spectral_centroid_rmse_hz | 1363.33  | 777.24  | 0.4299 | ✓ |
| rms_env_rmse             | 0.1904   | 0.0197  | 0.8964 | ✓ |
| lufs_m_rmse_lu           | 9.9424   | 1.3137  | 0.8679 | ✓ |
| embedding_cosine_distance | 0.1247   | 0.0818  | 0.3442 | ✓ |

**5 / 5 numeric keys exceed the 5% threshold** → `PALETTE_MOVES_PANEL`
fires per rubric. All test-side values are **lower** than the
reference-side c21-vs-original values, indicating the palette
render is **closer to the c21 fluidsynth-vs-original baseline shape**
than the c21 fluidsynth is to the original — an interesting signal
that the loudness-matched palette mix sits between the c21 render and
the original stems on all four numeric families + the perceptual
embedding distance. This is the numerical shift required by the
rubric; whether that shift is *audibly better* than c21 WIG is
strictly the operator's call per FD-6.

## Sufficiency check (against rubric)

| criterion | required | observed | met? |
|-----------|----------|----------|:--:|
| rubric mtime pre-registered | doc mtime < scripts | 1788401627 < all scripts | ✓ |
| three-way rubric_hash_v2 chain | doc SHA == txt == verdict field | `80fc4b60bbc47573…` byte-equal | ✓ |
| per-stem render success | 6/6 non-error | 6/6 | ✓ |
| per-stem byte-det ×2 or envelope | all pass | 6/6 (bass via REDEFINED_GAP arm) | ✓ |
| both panels 8-key finite | 8 keys each, all finite | 8/8 both | ✓ |
| Comparison B ≥3/5 keys exceed 5% | ≥3 | 5/5 | ✓ |
| c21 WIG delivery byte-identical pre==post | all_match=true | 56/56 pre==post, n_mismatch=0 | ✓ |
| c21 CG palette anchors byte-identical pre==post | all_match=true | included in 56/56 | ✓ |
| render_stem.py SHA lock | `214372d9…5b2b` | byte-identical pre==post | ✓ |
| ≥30 anchors preserved | ≥30 | 56 | ✓ |
| ≥14 test cases green | ≥14 | 15/15 | ✓ |
| 6 named + 2 housekeeping ledger events under `-clone-2` suffix on infra families | 6+2 | 6 named (unsuffixed per c32) + 2 housekeeping (suffixed) + 1 egress-probe + 1 plan-register + 1 run-rollup | ✓ |
| delivery manifest carries env_pins block | present with self-anchor | env_pin_sha256 present | ✓ |

## Anchor preservation (56 SHAs, `n_mismatch = 0`)

`data/v3_spine/252eb21ce7df7328/palette_render/anchor_preservation.json`
snapshotted 56 anchors pre-run and re-hashed post-run; all 56
byte-identical:

- c21 WIG operator-blessed delivery (6 files including manifest SHA
  `9a8a09d0f553a79f…`, full_reconstruction sha `f2deaf6aecb5afa5…`,
  original_ab sha `4c51a79a37017f1a…`, reconstruction_ab sha
  `f2deaf6aecb5afa5…`, panel.json/tsv).
- c21 WIG spine dir (11 files: section.wav, merged.mid,
  merged_report.json, tempo_choice.json, determinism JSONs, vocals
  overlay, per-track determinism).
- 6 baseline rc9_6stem WAVs + 7 canonical_midi MIDs.
- c21 Chicken Grease palette-render delivery + palette_render spine
  anchors (verdict `5ba4eaca242fcd29…`, palette full mix).
- 7 locked scripts (`render_stem.py` sha `214372d9…5b2b`,
  `recreate_v3.py` sha `72e80ee82cd21dbd…`, `env_pin.py` sha
  `ab6d54638faeb161…`, `midi_from_json_events.py` sha `bbff015f…`,
  `rc7_v2_rerun_v3_paths.py`, `mix_match_operator_section.py`,
  `rc7_mix_balance.py`).
- Rubric chains: c3 rubric, c4 rubric_v2, c21 CG palette rubric, c25
  WIG palette rubric (this cycle), all rubric_hash_v2 pin files.
- Focus set v2, cadence policy, plan_of_record.md.
- SF2 sha `74594e8f4250680adf590507a306655a299935343583256f3b722c48a1bc1cb0`.

## Test suite (`tests/test_v3_spine_wig_palette_render_c25.py`)

15/15 tests PASS covering all rubric-mandated invariants:

1. rubric mtime pre-registration
2. three-way rubric_hash_v2 chain byte-equality
3. `render_stem.py` SHA lock (`214372d9…5b2b`)
4. no-PRNG AST grep across palette_render_wig scripts
5. VST3 state API AST-forbidden (get_state, save_state, save_preset,
   load_state, set_state, get_state_chunk, getChunk)
6. `/usr/bin/python3` interpreter guard on every top-level script
7. c48 env-flag defaults OFF via `os.environ.setdefault`
8. focus_set_v2 consumption for WIG (sha16 chosen_section resolved)
9. both panels 8-key finite per M-TEX-1/panel contract
10. cross-song anchor preservation (c21 CG palette + c21 WIG
    operator_section byte-identical pre==post)
11. byte-determinism ×2 per persisted stem
12. honest REDEFINED_GAP arm bookkeeping (bass VST3 → fluidsynth_gm(33)
    fallback recorded in fetchability ladder + dispatch summary)
13. dispatch summary matches fetchability ladder
14. delivery manifest.json carries env_pins block with self-anchor
15. `sidecar_nonfactor` AST-forbidden

## Ledger events emitted (11 rows under fork-4c826786aced-clone-2)

Six named `M-V3-SPINE-1/wig-palette-render-c25/*` sub-leaves (unsuffixed
per c32 fanout-namespace convention on substantive milestones):

- `rubric-committed` → `d3cf95ef-b783-5481-9d17-618aae407b84`
- `fetchability-probed` → `3270e002-c007-5b63-a9ee-2a298d52316a`
- `per-stem-rendered` → `a4a8f28d-3b11-53c8-a55b-024732933f81`
- `panel-emitted` → `85638bbe-9b14-5caf-9d15-54ebeb83eeb0`
- `delivery-emitted` → `050e3f1f-584d-59c6-a56d-d0648a7d66e2`
- `verdict-emitted` → `1c7d6131-4b8d-501b-8099-36d8af9f6db9`

Plus five housekeeping / infra rows under `-clone-2` suffix per c32
convention on infra families:

- `_archive/cycle-25-scratch-clone-2` → `ee279700-52c7-578f-a2c3-36a392f846b3`
- `_infra/adopt-cycle25-tests-clone-2` → `240ff4c5-8520-5a4c-a725-0ad636940efa`
- `M-INGEST-1/egress-probe-cycle25-clone-2` → `0a7a616e-c5ea-5f91-855c-8490495b2b3b`
- `_plan/register-c25-wig-palette-render-clone-2` → `ac1819c3-0bba-5122-963a-b7ae80279329`
- `_run/post-merge-integration-cycle-25-wig-palette-clone-2` → `e3e16a77-4f2d-526c-8854-ffc669717a6c`

`promise_check`: 0 ERRORs after emission.

## Interpretation (research-brief Key Questions)

- **Does the palette move the panel on WIG?** Yes — all 5 numeric
  Comparison B keys exceed 5% relative threshold, comparable in
  magnitude to the c21 CG palette proof (4/5 there vs 5/5 here).
- **Is the VST3 bass path stable on WIG content?** No —
  `max_pairwise_rms = 0.041 >> 1e-4` c36 envelope; same structural-drift
  characterization as c21 CG. Rubric-allowed REDEFINED_GAP arm engaged
  cleanly via `fluidsynth_gm(33)` fallback, byte-det ×2, dispatch
  summary + fetchability ladder record the arm honestly.
- **Are all cross-song anchors preserved?** Yes — 56/56 anchor SHAs
  byte-identical pre==post, including c21 WIG operator-blessed delivery
  manifest `9a8a09d0f553a79f…` and full c21 CG palette anchors.
- **Is this ear-material for the operator?** Yes — sibling A/B ready at
  `data/v3/deliveries/252eb21ce7df7328/palette_render_c25/full_reconstruction_palette.wav`
  next to c21 WIG operator-blessed
  `data/v3/deliveries/252eb21ce7df7328/operator_section/full_reconstruction_operator_section.wav`.

## Issues and Uncertainties

- Bass VST3 structural drift on WIG content reproduces c21 CG pattern;
  Surge XT VST3 remains not-fit for byte-deterministic per-stem
  rendering. c31 STILL_GAP anti-pattern preserved — do NOT re-attempt
  VST3 state-extraction APIs.
- sfizz remains fetch-blocked: `workspace/palette/sfz/` is empty and
  no SFZ files are in the workspace. `fluidsynth_gm` fallbacks for
  guitar/piano/other consume the same c21 CG GM program map (25/0/88).
  If the operator commissions in-workspace SFZ files, guitar/piano/other
  can be re-rendered without touching this cycle's delivery.
- Panel numerical *shift* toward the original baseline is not
  automatically *audible* improvement — that judgement is operator ear
  per FD-6.

## Handoffs

1. **Operator ear on the c25 WIG palette A/B.** If the operator confirms
   audible improvement over the c21 WIG fluidsynth reference, palette
   becomes primary campaign-wide per D-D 2026-09-02. Delivery WAVs
   ready to compare:
   - c21 (fluidsynth): `data/v3/deliveries/252eb21ce7df7328/operator_section/full_reconstruction_operator_section.wav`
   - c25 (palette): `data/v3/deliveries/252eb21ce7df7328/palette_render_c25/full_reconstruction_palette.wav`
   - Original A/B: `data/v3/deliveries/252eb21ce7df7328/operator_section/original_ab_operator_section.wav`
2. **Palette-primary campaign-wide re-render** (post-D-D confirmation):
   third and later focus songs (Disco A `cdd2717e52820ff6`, Rome
   `51e433ade2a845e1`, Peach Dream `88d247468cb6d49f`) queue for the
   palette pipeline once the operator greenlights.
3. **SFZ workspace population** (unblocks native palette-timbre
   guitar/piano/other) — orchestrator territory, not worker.
