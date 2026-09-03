---
created: 2026-08-29T06:00:00Z
cycle: 35
run_id: run-2026-08-28T040704Z
agent: worker
milestone: M-DAW-SPIKE-1/palette-schema-v2-hydration-render
---

# Rubric — M-DAW-SPIKE-1/palette-schema-v2-hydration-render (Cycle 35 Branch A)

**Author:** cyd7bevdr@mozmail.com — fork 07063458736e / clone-0
**Frozen at:** 2026-08-29T06:00:00Z (BEFORE any script under `scripts/palette_v2_render/` lands; mtime + git-log enforced by tests/test_palette_v2_hydration_render.py).
**Peer sub-milestone under M-DAW-SPIKE-1 per c29 state-machine lemma.** NOT a child of the terminal-validated `M-DAW-SPIKE-1/palette-schema-v2` or its siblings.
**Inheritance:** c34 `scripts.palette_v2.validate` (READ-ONLY import), c33 P1 iterated-params anchors for Surge XT / Dexed (READ-ONLY: SHAs `1e3c003f…b80e` / `85be24e1…e1d6`), c31 `fluidsynth_gm` drums fallback, c31 palette_probe + palette anchors (READ-ONLY snapshot).

## Scope

First substantive activation of the c34 palette_v2 schema in a real render. Builds three per-stem palette assignment rows with `pinned_state.format=v2_iterated_params` for Surge XT (bass) and Dexed (other) and `format=v1_flat` for fluidsynth_gm (drums); validates every row through both layers of `scripts.palette_v2.validate` (READ-ONLY import); renders per-stem via subprocess-to-CLI or DawDreamer-VST3 dispatch; assembles `bare_combined.wav`; measures `M-TEX-1/panel` on TWO comparisons; resolves the verdict below.

## Verdict enum (frozen, 3-way)

- **V2_MOVES_PANEL** iff ALL of:
  1. Per-stem AND `bare_combined.wav` SHA-256 equal across two fresh `tempfile.mkdtemp()` runs (byte-determinism × 2).
  2. Both panels (`panel_original_vs_v2.tsv` and `panel_v1_vs_v2.tsv`) return the 8 canonical `PUBLIC_KEYS` and every numeric-family key is finite.
  3. At least ONE of the four numeric-family keys on `panel_v1_vs_v2.tsv` (`mel_l1_db` / `rms_env_rmse` / `spectral_centroid_rmse_hz` / `lufs_m_rmse_lu`) exceeds `0.05 × baseline_self_distance_floor` where the floor is the corresponding value of `panel_original_vs_fluidsynth_c9_baseline.tsv` (the c33-anchored (original, fluidsynth) self-distance) — i.e., v2 is measurably different from v1's fluidsynth fallback.

- **V2_NEUTRAL** iff conditions (1) and (2) hold but (3) fails (v2 hydration produces byte-different WAVs whose delta on `panel_v1_vs_v2.tsv` is within the 5% floor of v1's fluidsynth fallback).

- **RENDER_FAILS** iff ANY of:
  * (1) fails on any per-stem OR combined SHA;
  * (2) fails on either panel;
  * Surge XT or Dexed state-hydration produces a silent WAV (`peak_abs < 1e-4`);
  * assignment validation fails through `scripts.palette_v2.validate`;
  * anchor_preservation snapshot diff is non-empty (any READ-ONLY anchor drifted).

First-class negative finding permitted. If RENDER_FAILS is triggered by the hydration path, document the full failure log in the report and fetchability ladder; do NOT re-open the c31 STILL_GAP anti-pattern by re-attempting `get_state()`, `save_state()`, `save_preset()`, or `set_state(bytes)`.

## Byte-determinism × 2 protocol

Each pipeline run instantiates a fresh `tempfile.mkdtemp()` directory. Per-stem WAVs are canonicalized through `scipy.io.wavfile.write` at 44.1 kHz stereo, exactly `SAMPLE_COUNT = 44100 × 30 = 1_323_000` samples per file (pad or trim). SHA-256 is computed on the final canonicalized bytes. Both runs must produce byte-identical per-stem SHAs AND byte-identical `bare_combined.wav.sha`. `bare_combined.wav.sha.run{1,2}` files persist the two SHAs; equality is a hard verdict gate.

## Panel-measurement protocol

`M-TEX-1/panel` is invoked via `scripts.texture.panel.texture_distance(a_wav, b_wav, sr=44100)` (READ-ONLY import). Two comparison pairs are required:

1. `panel_original_vs_v2.tsv` — `texture_distance(original.wav, bare_combined_v2.wav, sr=44100)`.
2. `panel_v1_vs_v2.tsv` — `texture_distance(bare_midi_c9.wav, bare_combined_v2.wav, sr=44100)`, where `bare_midi_c9.wav = data/tex/renders/synth_030s/bare_midi.wav` (c9 fluidsynth-only anchor).

A third comparison — `panel_original_vs_fluidsynth_c9_baseline.tsv` = `texture_distance(original.wav, bare_midi_c9.wav)` — provides the denominator for the 5% floor in verdict step (3). This is the SAME anchor c33 used and is READ-ONLY.

Both required TSVs must have exactly the 8 canonical `PUBLIC_KEYS` and all four numeric-family keys must be finite.

## Render mechanism (v2 hydration path)

- **drums** — `fluidsynth_gm` via `fluidsynth` CLI. `parameter_dict = {"gain": 1.0, "sample_rate": 44100.0}`. SF2 pin `74594e8f…1cb0`. This path is the c31/c33 known-green fallback.
- **bass** — `surge_xt` via DawDreamer 0.9.0 VST3 dispatch. Hydration path (P1, c33 WORKAROUND_FOUND):
  ```python
  engine = dawdreamer.RenderEngine(44100, 512)
  plugin = engine.make_plugin_processor("t", "/usr/lib/vst3/Surge XT.vst3")
  anchor = json.loads(Path("data/dawdreamer_state/per_plugin/surge_xt/p1_state_v2.json").read_bytes())
  for key, value in anchor.items():
      idx = int(key.split(":", 1)[0])  # "00000:M1: -" -> 0
      plugin.set_parameter(idx, float(value))
  plugin.load_midi(str(midi_path))
  engine.load_graph([(plugin, [])])
  engine.render(30.0)
  audio = plugin.get_audio()  # (channels, samples) float32
  ```
  This is a `set_parameter(i, v)` loop over the P1 iterated-params dict — the canonical c33-verified hydration path. `get_state()`, `save_state()`, `save_preset()`, `set_state(bytes)` are FORBIDDEN.
- **other** — `dexed` via DawDreamer 0.9.0 VST3 dispatch. Same P1 hydration pattern with the Dexed anchor.

If DawDreamer raises OR the returned buffer is silent (peak_abs < 1e-4), the fallback is NOT to re-attempt with `get_state`/`set_state(bytes)` — it is to emit RENDER_FAILS honestly and document the failure log.

## Rubric hash

The SHA-256 of THIS rubric document (bytes-as-committed) is recorded in `data/palette_v2_render/rubric_hash.txt` and embedded in `data/palette_v2_render/verdict.json` under `rubric_hash`. `tests/test_palette_v2_hydration_render.py::test_rubric_hash_equality` asserts byte-equality between the on-disk rubric file, `rubric_hash.txt`, and the `rubric_hash` field in `verdict.json`.

## Anti-patterns locked (5, unchanged from c34)

1. No CLAP fetch retry (c11 invalidated).
2. No c8 octave-suppression retry.
3. No c22/c23/c25 ear-chassis re-audit.
4. No fifth collision-mechanism candidate.
5. No re-authoring of validated artifacts under re-invocation.

Additionally: **no `get_state`/`save_state`/`save_preset`/`set_state(bytes)` on Surge XT or Dexed** — that is the c31 STILL_GAP surface c33 already characterized as 0-byte-return; re-attempting it is a re-open of an invalidated approach. Only the P1 `set_parameter(i, v)` loop is permitted for VST3 hydration.

## Handoff signals (for the c36 researcher)

- V2_MOVES_PANEL → v2 hydration is production-ready; c36 candidate is `palette-driven-batch-v2` combining v2 hydration + sampler-side diversification (per c34 batch-v1 finding).
- V2_NEUTRAL → v2 schema lands but the render is indistinguishable from v1's fluidsynth fallback on this seed; c36 candidate is per-plugin patch-diversity probe (are all-default-params too uniform to matter?).
- RENDER_FAILS with a specific plugin failure log → concrete c36 candidates named honestly in report §10: `dexed-preset-hydration` (FXP/BANK load path) or `surge-xt-fxp-load` (workspace-native preset ingestion). Do NOT recommend re-opening c31 STILL_GAP.
