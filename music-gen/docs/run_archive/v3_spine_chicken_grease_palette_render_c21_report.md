---
created: 2026-09-02T23:35:00Z
run_id: run-2026-09-02T231500Z
cycle: 21
agent: worker
milestone: M-V3-SPINE-1/chicken-grease-palette-render
---

# Chicken Grease Surge XT / sfizz Palette Render — Cycle 21 Report

Song: **Chicken Grease**, `audio_sha16 = 31a164f845f8e27e`, operator-section
`t = 233.63918 .. 263.63918 s`.

Fork: `0a1b1dca4f9b` · clone 2 · milestone
`M-V3-SPINE-1/chicken-grease-palette-render` (unsuffixed substantive per
c32 fanout-namespace convention).

**Verdict: `PALETTE_MOVES_PANEL`** — three-way `rubric_hash_v2` chain holds;
4 / 5 numeric panel keys exceed the 5 % relative threshold on Comparison B
`(c5 fluidsynth reference, palette render)`. `blocked_on_operator = true`
per FD-6: the operator ear is the only LANDS authority. Per operator D-D
(2026-09-02, palette-becomes-primary): if the operator confirms this
palette rendering lands, it becomes the c22 input for the campaign-wide
palette-primary decision.

---

## 1. What was built

Pre-registered before any Python edit:

- `docs/v3_spine_chicken_grease_palette_render_c21_rubric.md` — frozen
  3-verdict rubric (`PALETTE_MOVES_PANEL` / `PALETTE_NEUTRAL` /
  `RENDER_FAILS`) with the panel-B ≥ 3-of-5 delta-magnitude firing rule
  and the c36 clone-2 `max_pairwise_rms ≤ 1e-4`
  `SMALL_PERTURBATION_TOLERABLE` envelope for VST3 stems.
- `data/v3_spine/31a164f845f8e27e/palette_render/rubric_hash_v2.txt`
  pinning doc SHA `9eb5523cbd090c388e30b0b271cb1dffd4f321ed907c78be122f56cbad5e1879`.
  Three-way byte-equality asserted at verdict time.

Implementation modules under `scripts/v3_spine/palette_render/`:

| Module                     | Role                                                                     |
|----------------------------|--------------------------------------------------------------------------|
| `anchor_preservation.py`   | 61-anchor read-only snapshot (pre-run) + post-run diff, hard gate.       |
| `render_palette.py`        | Per-stem dispatch (drums / bass / guitar / piano / other / vocals) with byte-det × 2 into fresh `tempfile.mkdtemp()` dirs and Surge XT VST3 3-retry envelope check. |
| `mix_and_deliver.py`       | Applies c6 Method B chain via READ-ONLY import of `scripts/v3_spine/rc7_v2_rerun_v3_paths.py` — 12-band iirpeak EQ (Q = 1.4, geomspace 20 – 20 000 Hz) + RMS loudness match per stem + sum → `full_reconstruction_palette.wav`. Emits delivery tree. |
| `panels_and_verdict.py`    | Comparison A + B panel measurement; verdict emission w/ three-way `rubric_hash_v2` chain. |

Tests: `tests/test_v3_spine_chicken_grease_palette_render_c21.py` —
12 invariants, 12 / 12 green.

## 2. What was run — reproducible commands

    export PYTHONHASHSEED=0 SOURCE_DATE_EPOCH=1756463424 TZ=UTC LC_ALL=C.UTF-8
    export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1

    /usr/bin/python3 scripts/v3_spine/palette_render/anchor_preservation.py --phase pre
    /usr/bin/python3 scripts/v3_spine/palette_render/render_palette.py
    /usr/bin/python3 scripts/v3_spine/palette_render/mix_and_deliver.py
    /usr/bin/python3 scripts/v3_spine/palette_render/panels_and_verdict.py
    /usr/bin/python3 scripts/v3_spine/palette_render/anchor_preservation.py --phase post
    /usr/bin/python3 tests/test_v3_spine_chicken_grease_palette_render_c21.py

## 3. Per-stem outcome

| Stem   | Dispatch                                           | Outcome                                          | byte_det × 2 |
|--------|----------------------------------------------------|--------------------------------------------------|:------------:|
| drums  | fluidsynth GM channel 10 (canonical MIDI unmodified) | Native GM 128 mapping (c5 unchanged)             | ✅ |
| bass   | Surge XT VST3 via DawDreamer (c33 P1 hydration, 2855/2855 params) → fluidsynth_gm(33) fallback | REDEFINED_GAP arm — VST3 structural drift `max_pairwise_rms = 0.068` >> `1e-4` c36 envelope; fluidsynth_gm(33 electric bass finger) fallback delivers byte-det bass | ✅ (fallback) |
| guitar | sfizz probe → fluidsynth_gm(25 clean electric)     | sfizz `sfz_dir_missing` — no SFZ files in `workspace/palette/sfz/`; fallback engaged | ✅ |
| piano  | sfizz probe → fluidsynth_gm(0 acoustic grand)      | sfizz `sfz_dir_missing`; fallback engaged        | ✅ |
| other  | sfizz probe → fluidsynth_gm(88 new age pad)        | sfizz `sfz_dir_missing`; fallback engaged        | ✅ |
| vocals | Verbatim D2 copy of `render/vocals_htdemucs.wav`   | c5 htdemucs stem preserved SHA-identical         | ✅ |

`byte_det_gate_holds = true` across all 6 stems. Bass VST3
characterization preserved verbatim (`vst3_shas`, `vst3_outcome`,
`vst3_max_pairwise_rms`) in `byte_determinism.json` even though the
fluidsynth_gm fallback provides the persisted `render.wav`.

## 4. Panels (both 8 keys finite)

### Comparison A — `(original_ab, palette)`

| Key                          | Value       |
|------------------------------|-------------|
| mel_l1_db                    | 6.360       |
| spectral_centroid_rmse_hz    | 1149.9      |
| rms_env_rmse                 | 0.107       |
| lufs_m_rmse_lu               | 4.514       |
| embedding_cosine_distance    | 0.2434      |
| embedding_rung               | vggish      |
| n_samples_compared           | 1_323_000   |
| sr_hz                        | 44100       |

### Comparison B — `(c5 fluidsynth, palette)`

| Key                          | Value       |
|------------------------------|-------------|
| mel_l1_db                    | 6.889       |
| spectral_centroid_rmse_hz    | 3120.3      |
| rms_env_rmse                 | 0.0802      |
| lufs_m_rmse_lu               | 3.724       |
| embedding_cosine_distance    | 0.0957      |
| embedding_rung               | vggish      |
| n_samples_compared           | 1_323_000   |
| sr_hz                        | 44100       |

### Comparison B delta magnitudes vs baseline `(c5 fluidsynth, original)`

| Key                          | ref (c5 vs orig) | test (palette vs c5) | rel delta | exceeds 5 % |
|------------------------------|-----------------:|----------------------:|----------:|:-----------:|
| mel_l1_db                    | 8.786            | 6.889                 | 0.216     | ✅ |
| spectral_centroid_rmse_hz    | 3254.5           | 3120.3                | 0.041     | ❌ |
| rms_env_rmse                 | 0.1473           | 0.0802                | 0.455     | ✅ |
| lufs_m_rmse_lu               | 7.427            | 3.724                 | 0.499     | ✅ |
| embedding_cosine_distance    | 0.1876           | 0.0957                | 0.490     | ✅ |

**4 / 5 keys exceed the 5 % relative threshold** → PALETTE_MOVES_PANEL
criterion met. Interpretation: on all four exceeding keys the palette
render is *closer* to c5 (deltas are smaller) — the RC7 EQ + RMS chain
compresses the palette spectrum toward c5's fluidsynth reference. This is
consistent with sfizz-unavailability collapsing guitar / piano / other
back to fluidsynth GM under different programs; the audible palette shift
comes from GM program substitution + fitted per-stem EQ + independent
loudness match, not from external samplers or VST3.

## 5. Fetchability ladder summary

    sfizz  · guitar → sfz_dir_missing → fluidsynth_gm(25)
    sfizz  · piano  → sfz_dir_missing → fluidsynth_gm(0)
    sfizz  · other  → sfz_dir_missing → fluidsynth_gm(88)
    surge_xt_vst3 · bass → 2855/2855 params loaded via DawDreamer,
                            structural_drift (max_pairwise_rms=0.068),
                            REDEFINED_GAP arm active,
                            → fluidsynth_gm(33) fallback

Workspace SFZ inventory: `workspace/palette/sfz/` does not exist — every
sfizz-eligible stem falls through honestly. No fetch was attempted (egress
remains HTTP 429 / tv_embedded per c47 + registry).

## 6. Read-only anchor preservation

`data/v3_spine/31a164f845f8e27e/palette_render/anchor_preservation.json`:
**61 / 61 anchors byte-identical pre == post**, `n_mismatch = 0`,
`all_match = true`. Every gate holds:

- c5 operator-blessed delivery `full_reconstruction_operator_section.wav`
  SHA `cc919559b4508b6b…f01bbbd7` byte-identical (hard gate).
- c5 canonical per-stem MIDIs (bass / drums / guitar / piano / other /
  vocals / full_mix) untouched.
- c33 `scripts/palette_render/render_stem.py` SHA
  `214372d920a319a9…5b2b` byte-identical (do-not-touch invariant).
- c6 v3-paths `scripts/v3_spine/rc7_v2_rerun_v3_paths.py` SHA
  `eaaa993e2eb50d25…3ce38` byte-identical.
- Rubric v2 chain SHA `c49db5a12e955f26…016451a` and c5 htdemucs
  vocals stem SHA both preserved.

## 7. Verdict details

Written to
`data/v3/deliveries/31a164f845f8e27e/cycle21/verdict_palette.json`
(SHA `5ba4eaca242fcd29…`) sibling to `cycle20/` — does NOT overwrite the
operator-blessed c5 delivery.

    verdict                            = PALETTE_MOVES_PANEL
    rubric_hash_v2_chain_holds         = true
    blocked_on_operator                = true
    per_stem_render_success            = true
    per_stem_byte_det_or_envelope      = true
    panel_a_8_keys_finite              = true
    panel_b_8_keys_finite              = true
    comparison_b_keys_exceeding        = 4 / 5
    c5_delivery_anchor_preserved       = true

`sub_artifact_shas` pins every WAV + MIDI + manifest SHA. `vst3_bass`
records the REDEFINED_GAP outcome verbatim.

## 8. Ledger events (11 total)

Emitted via `tools/stale/_c21_palette_emit_events.py`
(auto-archived post-run per c29 housekeeping convention):

  1. `_plan/register-c21-palette-render-milestones`
  2. `M-V3-SPINE-1/chicken-grease-palette-render/rubric-committed`
  3. `M-V3-SPINE-1/chicken-grease-palette-render/fetchability-probed`
  4. `M-V3-SPINE-1/chicken-grease-palette-render/per-stem-rendered`
  5. `M-V3-SPINE-1/chicken-grease-palette-render/panel-emitted`
  6. `M-V3-SPINE-1/chicken-grease-palette-render/delivery-emitted`
  7. `M-V3-SPINE-1/chicken-grease-palette-render/verdict-emitted`
  8. `_archive/cycle-21-palette-scratch-clone-2`
  9. `_infra/adopt-cycle21-palette-scripts-clone-2`
 10. `M-INGEST-1/egress-probe-cycle21-clone-2`
 11. `_run/palette-render-cycle-21-clone-2`

`promise_check` reports **0 ERRORs** post-emission (WARN set unchanged
from cycle start — all pre-existing).

## 9. Issues and honest handoffs

- **VST3 bass rendered structural drift under c36 envelope** — Surge XT
  loads and hydrates cleanly (2855 / 2855 params) but three fresh-tempdir
  renders on Chicken Grease bass MIDI content diverge with
  `max_pairwise_rms = 0.068`, three orders of magnitude beyond the c36
  clone-2 `≤ 1e-4` tolerance. This is a REDEFINED_GAP arm outcome, not
  a bug: the fluidsynth_gm(33) fallback delivers byte-det bass and the
  VST3 characterization is preserved verbatim in `byte_determinism.json`
  and `fetchability_ladder.jsonl`. Root-cause exploration deferred to a
  future substantive cycle if operator directs — the c31 STILL_GAP
  anti-pattern (`get_state` / `save_state` / `set_state(bytes)`) remains
  AST-forbidden and was NOT re-attempted.

- **sfizz coverage 0 / 3** — `workspace/palette/sfz/` is empty. Every
  sfizz-eligible stem falls through to fluidsynth_gm honestly. Fetching
  SFZ presets would require egress which remains blocked (HTTP 429 /
  tv_embedded per the c47 + registry). A future cycle with egress open
  can populate the SFZ palette and re-render for a *true* sampler-based
  palette test.

- **PALETTE_MOVES_PANEL is not a LANDS gate** — per FD-6 the operator
  ear is the only LANDS authority. The verdict carries
  `blocked_on_operator = true`. This branch's numeric evidence is that
  the palette render shifts panel measurements substantially vs the c5
  fluidsynth reference; whether that shift is audibly *better* is the
  operator's call.

- **Per operator D-D**: if the operator confirms audibly, this
  palette-render becomes the c22 input to the "palette becomes primary
  campaign-wide" decision. The c5 fluidsynth reference remains the
  operator-blessed anchor until then.
