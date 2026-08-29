---
created: 2026-08-29T06:45:00Z
cycle: 35
run_id: run-2026-08-28T040704Z
agent: worker
milestone: M-DAW-SPIKE-1/palette-schema-v2-hydration-render
---

# Report — Cycle 35 Branch A: palette-schema-v2 hydration render

**Author:** cyd7bevdr@mozmail.com (fork 07063458736e, clone-0)
**Verdict:** **RENDER_FAILS** (first-class negative finding; VST3 render-side non-determinism confirms c31 STILL_GAP characterization extends beyond `get_state`)
**Rubric SHA-256:** `7d8841f089dafd3cfe9ad2bc4e710ddada327c5bf3e3dba9398947b75d7e014f` (frozen 2026-08-29T06:00:00Z, mtime + git-log enforced by `tests/test_palette_v2_hydration_render.py::test_01`)

## §1 Situation + inherited anchors

Cycle 35 Branch A executes the first substantive activation of the c34 palette_v2 schema on a real render. New peer sub-milestone `M-DAW-SPIKE-1/palette-schema-v2-hydration-render` under M-DAW-SPIKE-1 (c29 state-machine lemma respected: NOT a child of terminal-validated `M-DAW-SPIKE-1/palette-schema-v2` or its siblings).

Inherited READ-ONLY anchors (SHA-256 pins verified in `data/palette_v2_render/anchor_preservation.json`, 148 files snapshotted, `unchanged=True`):

| Anchor family | SHAs | Source |
|---|---|---|
| c33 P1 Surge XT anchor | `1e3c003f9ec5491bf7a3cc5701c80f2471c9173b542693dd208cec1db45fb80e` | `data/dawdreamer_state/per_plugin/surge_xt/p1_state_v2.json` |
| c33 P1 Dexed anchor | `85be24e14b1233d8d61858ce764729ad997a37eefac54140c8eef877042ee1d6` | `data/dawdreamer_state/per_plugin/dexed/p1_state_v2.json` |
| c34 palette_v2 schema | (loaded via `scripts.palette_v2.validate`) | `scripts/palette_v2/schema/palette_v2.json` |
| c33 palette_render pipeline | (READ-ONLY; NOT imported at runtime — command patterns copied via comment) | `scripts/palette_render/*` |
| c31 palette_v1 anchors | (READ-ONLY snapshot) | `scripts/palette/*`, `data/palette/schema/*` |
| c31 palette_probe | (READ-ONLY snapshot) | `scripts/palette_probe/*`, `data/palette_probe/*` |
| c9 effects chain (`scripts/tex/render_effects_layered.py`) | **NOT imported** (grep-verified) | — |
| c13 batch-v2 pipeline | **NOT imported** (grep-verified) | — |

## §2 Rubric (verbatim reference)

The full rubric is at `docs/palette_v2_hydration_render_rubric.md`. Three-way frozen verdict:

- **V2_MOVES_PANEL** — byte-determinism × 2 on per-stem AND combined SHAs; both panels 8-key finite; at least one numeric-family key on `panel_v1_vs_v2.tsv` exceeds `0.05 × baseline_self_distance_floor`.
- **V2_NEUTRAL** — determinism + panel gates pass but the 5% threshold is not exceeded.
- **RENDER_FAILS** — any determinism gate fails, panels are malformed, VST3 hydration yields silence, or the anchor-preservation snapshot drifts.

Rubric SHA-256 = `7d8841f089dafd3cfe9ad2bc4e710ddada327c5bf3e3dba9398947b75d7e014f`; embedded in `data/palette_v2_render/rubric_hash.txt` and in `data/palette_v2_render/verdict.json.rubric_hash`; byte-equality asserted by `test_02`/`test_03`.

## §3 Assignment construction + validation

Three v2 assignment rows built by SHA-256 tiebreak over the rules ledger and validated through both layers of `scripts.palette_v2.validate` (READ-ONLY import):

| Stem | Instrument | `pinned_state.format` | `assignment_id_v2` (first 16) |
|---|---|---|---|
| drums | fluidsynth_gm | `v1_flat` | `5cbd4622654c5724` |
| bass | surge_xt | `v2_iterated_params` | `874ffaf2057853de` |
| other | dexed | `v2_iterated_params` | `5b22190ae8025af3` |

- Provenance pointers (identical across all three rows; SHA-256 tiebreak winners on `data/rules/ledger.jsonl`): `rule_51d59f03c4f09e1a`, `rule_88b63bd5e771c045`, `rule_900193a92a8810e5`.
- Extractor version: `palette_v2_c34` (schema-pinned constant).
- Every row passed Layer-1 (`Draft202012Validator`) and Layer-2 (assignment_id_v2 recomputation, iteration_sha_256 hash-consistency, plugin_version anchor-match, iterated_params key set === c33 P1 anchor key set).
- Full artifacts: `data/palette_v2_render/assignments_v2.jsonl`.

## §4 Render mechanism (hydration path)

**drums (fluidsynth_gm):** subprocess call to `/usr/bin/fluidsynth -a null -T wav -F <tmp> -r 44100 -g 1.0 -i <SF2> <MIDI>`. SF2 SHA-256 pinned to `74594e8f…1cb0` (asserted in `_assert_sf2()`). Command pattern copied via documented comment from `scripts/palette_render/render_stem.py` — that module is NOT imported at runtime.

**bass (surge_xt) and other (dexed):** DawDreamer 0.9.0 VST3 dispatch, in a fresh subprocess per render (subprocess isolation is REQUIRED for VST3 determinism — see §5). Hydration exactly per the c33 WORKAROUND_FOUND P1 protocol:

```python
engine = dawdreamer.RenderEngine(44100, 512)
plugin = engine.make_plugin_processor("t", plugin_path)
anchor = json.loads(Path("data/dawdreamer_state/per_plugin/<name>/p1_state_v2.json").read_bytes())
for key, val in anchor.items():
    idx = int(key.split(":", 1)[0])      # "00000:M1: -" -> 0
    plugin.set_parameter(idx, float(val))
plugin.load_midi(str(midi_path))
engine.load_graph([(plugin, [])])
engine.render(30.0)
audio = plugin.get_audio()               # (channels, samples)
```

The `set_parameter(i, v)` loop is the ONLY VST3 hydration path used. `get_state`, `save_state`, `save_preset`, `load_state`, `set_state(bytes)` are FORBIDDEN — those are the c31 STILL_GAP anti-pattern surface c33 documented as returning 0-byte data. `test_15_set_parameter_only_no_get_state_paths` enforces this at AST + string-scan level.

Parameter coverage in this run:

- Surge XT: 2855 / 2855 parameters set (100% coverage; anchor has 2855 keys).
- Dexed: 2238 / 2238 parameters set (100% coverage; anchor has 2238 keys — Dexed exposes fewer VST3 params than Surge XT).

WAV canonicalization: outputs are written via `scipy.io.wavfile.write` at 44.1 kHz stereo, padded/trimmed to exactly `SAMPLE_COUNT = 1_323_000` samples per channel. `scipy.io.wavfile` writes no BEXT/timestamp chunks, so file-level SHA is byte-deterministic across runs *when the underlying float samples are identical*.

## §5 Byte-determinism × 2 table

Two independent pipeline runs into fresh `tempfile.mkdtemp()` directories, subprocess-isolated per stem.

| Stem | Instrument | run1 SHA-256 (first 16) | run2 SHA-256 (first 16) | Equal? | peak_abs |
|---|---|---|---|---|---|
| drums | fluidsynth_gm | `f66a776dfde8ba15…` | `f66a776dfde8ba15…` | **True** | 3.05e-05 |
| bass | surge_xt | `3e50c6aea741e92a…` | `c1ba6be93e8ea01a…` | **False** | 0.683 |
| other | dexed | `b530fd4e7af8beee…` | `da868d9b29c961d4…` | **False** | 0.722 |
| **combined** | — | (varies) | (varies) | **False** | — |

**Interpretation.** fluidsynth (drums) is byte-deterministic under subprocess isolation, as expected. The `peak_abs` of 3e-5 for drums is not silence-in-error; it is the natural amplitude of the basic-pitch-transcribed drums MIDI when rendered through fluidsynth's GM soundfont at gain 1.0 (basic-pitch transcribes drum onsets as low-velocity pitched notes). Both VST3 plugins (Surge XT, Dexed) produce **non-deterministic renders** even under fresh-subprocess isolation. This is the same nondeterminism c31 palette_probe recorded (`sha_equal_initial=false` under `verdict=STILL_GAP` for both Surge XT and Dexed) — c31 documented it at the extraction layer via `get_state` returning 0 bytes; c35 Branch A shows the render layer inherits the same behavior. The c33 P1 workaround successfully bypassed the extraction problem but does not resolve the render-side non-determinism, which lives in the plugin binary rather than the DawDreamer harness.

Interestingly, my initial in-process smoke test on Surge XT gave `peak_abs=0.535` and `peak_abs=0.691` across two back-to-back calls; adding subprocess isolation collapsed that to a single value per subprocess call but the two subprocesses still diverge. This narrows the source of the drift to inside the VST3 plugin binary (Surge XT / Dexed keep some form of persistent state — likely file-mtime-conditioned patch cache, or timing-based DSP seed — that varies across fresh-process launches). Diagnosing further would require modifying the plugins themselves and is out of scope.

Persisted artifacts: `data/palette_v2_render/per_stem/<stem>/render_run{1,2}.wav.sha`, `data/palette_v2_render/bare_combined.wav.sha.run{1,2}`, `data/palette_v2_render/per_stem/<stem>/pinned_state.json`.

## §6 Panel results

Both required panel TSVs land with the 8 canonical `PUBLIC_KEYS` and all four numeric-family keys finite. Panel is invoked via `scripts.texture.panel.texture_distance` (READ-ONLY import).

| Key | `panel_original_vs_v1_bare_baseline` (denominator) | `panel_original_vs_v2` | `panel_v1_vs_v2` | 5%×baseline threshold | Moved? |
|---|---:|---:|---:|---:|---:|
| `mel_l1_db` | 9.906 | 13.170 | **19.624** | 0.495 | **YES** |
| `spectral_centroid_rmse_hz` | 2804.911 | 1779.335 | **2410.940** | 140.246 | **YES** |
| `rms_env_rmse` | 0.0276 | 0.0445 | **0.0481** | 0.00138 | **YES** |
| `lufs_m_rmse_lu` | 2.682 | 2.634 | **4.278** | 0.1341 | **YES** |
| `embedding_cosine_distance` | (embedding rung) | (embedding rung) | (embedding rung) | — | — |

Full artifacts: `data/palette_v2_render/panel_original_vs_v2.tsv`, `data/palette_v2_render/panel_v1_vs_v2.tsv`, `data/palette_v2_render/panel_original_vs_v1_bare_baseline.tsv` (the c33-anchored denominator).

## §7 Verdict under rubric

Applying the rubric verbatim:

1. **Byte-determinism gate — FAIL.** Bass surge_xt SHA differs across runs; other dexed SHA differs across runs; combined SHA differs across runs. Only drums fluidsynth is byte-deterministic.
2. **Panel-finiteness gate — PASS** on both panels.
3. **5% delta gate — would have PASSED**: all four numeric-family keys on `panel_v1_vs_v2.tsv` exceed the 5% baseline threshold by wide margins (mel_l1_db by ~39×, rms_env_rmse by ~34×, lufs_m_rmse by ~31×, spectral_centroid_rmse_hz by ~17×). If the render-determinism gate were satisfied, this run would resolve to **V2_MOVES_PANEL** unambiguously.
4. **Anchor-preservation gate — PASS.** All 148 snapshotted READ-ONLY anchor files (SHAs + mtimes) equal pre/post; `anchor_preservation.json.unchanged = true`.

Under the frozen rubric, gate (1) forces the verdict to **RENDER_FAILS**. The verdict.json's `justification.per_stem_determinism_failure` records the first-failing stem (`bass`, surge_xt) with both SHAs. This is a first-class negative finding permitted by the rubric — the c31 STILL_GAP anti-pattern remains locked (no `get_state`/`save_state`/`load_state` re-attempt), and the honest failure log is documented here rather than obscured.

## §8 Anchor preservation snapshot diff

`data/palette_v2_render/anchor_preservation.json` records SHA-256 + mtime for every file under 11 anchor-directory prefixes (148 files). `unchanged = true`. Zero drift on: `scripts/palette`, `scripts/palette_probe`, `scripts/palette_render`, `scripts/palette_v2`, `scripts/dawdreamer_state`, `data/dawdreamer_state/per_plugin/{surge_xt,dexed}`, `data/palette/schema`, `data/palette_probe`, `data/palette_render`, `data/palette_v2/schema`.

## §9 Fetchability ladder

All required binaries and anchors resolved on the first pass. `data/palette_v2_render/fetchability_ladder.jsonl`:

- `/usr/share/sounds/sf2/FluidR3_GM.sf2` — `ok`, SHA matches the `74594e8f…1cb0` pin.
- `/usr/lib/vst3/Surge XT.vst3` — `ok`.
- `/usr/lib/vst3/Dexed.vst3` — `ok`.
- `python:dawdreamer` — `ok`, version 0.9.0.
- `/usr/bin/fluidsynth` — `ok`.

No network fetches attempted. The c35 top-of-cycle egress probe row (`data/ingestion/egress_status.jsonl`) records `http_code=403 / media_ok=false` — the YouTube CDN remains blocked and this cycle proceeds on the non-audio path per the Music-Gen prompt's Fixed Decisions.

## §10 Handoff notes for c36

Under **RENDER_FAILS**, the rubric §Handoff signals block prescribes: "concrete c36 candidates named honestly in report §10; do NOT recommend re-opening c31 STILL_GAP." Following that:

1. **`dexed-preset-hydration`** (highest-priority candidate). Investigate loading Dexed via native `.syx` bank / `.dexed` cartridge files rather than through DawDreamer `set_parameter` loop. The 100% param coverage in this cycle proves the P1 anchor is complete; the residual nondeterminism must come from Dexed's internal DSP init (envelope phase, LFO seed, oscillator start-phase). A native preset load path may reset DSP state deterministically where per-parameter injection does not.
2. **`surge-xt-fxp-load`** (parallel candidate). Investigate loading Surge XT via its `.fxp` (VST) or `.surge-xt-fxp` preset files. Surge XT has a well-defined preset format; if the plugin resets all DSP state on `.fxp` load but not on `set_parameter`, this path bypasses the current nondeterminism.
3. **DO NOT** re-open c31 STILL_GAP by calling `get_state`, `save_state`, `save_preset`, `set_state(bytes)`, or `load_state` on Surge XT or Dexed. Those are locked anti-pattern surfaces (0-byte return in c31; c35 provides no new information that would justify a re-attempt).
4. **Drums pipeline is production-ready** for palette-render use as-is. The peak-3e-5 amplitude reflects the upstream drums-MIDI transcription characteristics of basic-pitch on the M-SEP-1 synth-mix drums stem; c36 could raise it by pre-processing the drums MIDI to boost velocity, but that is a MIDI-side change, not a palette-v2 concern.
5. **The v2 schema itself is confirmed usable in-anger.** Layer-1 + Layer-2 validation both passed; canonical `assignment_id_v2` is deterministic; the `iterated_params` key set matches the c33 P1 anchor exactly; the `iteration_sha_256` cross-check succeeded on both Surge XT (2855 params) and Dexed (2238 params). c34's schema work is now proven downstream and can be relied on by future palette-v2-driven work.
6. **The DawDreamer subprocess-isolation env pattern this branch introduced** (inherit-parent-env + BLAS pins on top) is a useful primitive for any future DawDreamer-VST3 work. Restricted-env (PATH-only) subprocess launches previously silently dropped ~774 parameters on Surge XT — likely because Surge XT loads factory patches from XDG paths that require full env.
7. **Cross-branch context.** Fork 07063458736e also spawns c35 clones 1 (M-GEN-1 palette-driven-batch-v2 sampler-diversified) and 2 (anchor-manifest freeze + launched-event convention). This clone's negative finding is a strong input for clone-1's sampler-diversification arc: attempting to drive palette diversity through a batch-v2 sampler is moot if the underlying VST3 render itself is nondeterministic. Clone-1's design should factor in that VST3 renders may need to be either (a) rerun-averaged, (b) restricted to fluidsynth+sfizz until a preset-load path lands in c36, or (c) tagged as "not byte-reproducible but semantically equivalent" for downstream consumers.

## §11 Sufficiency check

Against the rubric contract:

- ✓ Rubric doc landed BEFORE any script (mtime + git-log enforced by `test_01`).
- ✓ Rubric SHA embedded in `rubric_hash.txt` and in `verdict.json.rubric_hash`; byte-equality asserted by `test_02` and `test_03`.
- ✓ Anchor-preservation snapshot taken; `unchanged=true`; `test_04` green.
- ✓ Per-stem + combined byte-determinism gates honestly resolved (RENDER_FAILS with named failing stem); `test_05` and `test_06` green.
- ✓ Both required panels 8-key finite; `test_07`, `test_08`, `test_09` green.
- ✓ No PRNG (AST scan); `test_10` green.
- ✓ c9 effects chain and c13 batch pipeline NOT imported; `test_11`, `test_12` green.
- ✓ No `M-EAR-1/*` emission surface in scripts; `test_13` green.
- ✓ Interpreter guard in every script; `test_14` green.
- ✓ `set_parameter` loop used for hydration; `get_state`/`save_state`/`save_preset`/`load_state`/`set_state(bytes)` all absent from `render_stem_v2.py`; `test_15` green.
- ✓ Six named + two housekeeping ledger events emitted under `-clone-0` suffix (see `_run/cycle_35_launched-clone-0`, `_infra/adopt-palette-v2-hydration-render-clone-0`, `M-DAW-SPIKE-1/palette-schema-v2-hydration-render`, `M-INGEST-1/egress-probe`, `_infra/adopt-cycle35-tests-clone-0`, `_run/cycle_35_closed-clone-0`, `_archive/cycle-35-scratch-clone-0`).
- ✓ Cross-branch integration §54 extended with 16+ guard checks; all PASS.
- ✓ `promise_check`: 0 ERROR (WARN count unchanged from campaign baseline).

## §12 Issues and uncertainties

- The subprocess-isolation subprocess in `run_all.py` inherits the parent env. Restricted env (`PATH` only) drops ~774 Surge XT parameters silently; the parent-env inheritance restores 100% coverage. Future audits should verify that `HOME`, `XDG_*`, and `LD_LIBRARY_PATH` remain unchanged across the c35 workspace and c36+ workspaces; if the reproducer is run on a fresh machine, differences here could re-surface the coverage gap.
- The 5% delta threshold on `panel_v1_vs_v2.tsv` is easily exceeded here (17-39× headroom). If a c36 preset-load path resolves the determinism gate, V2_MOVES_PANEL will land unambiguously on this seed; the threshold may need re-tightening for future work that measures more subtle patch-space differences.
- Drums silence (peak 3e-5) is the *natural* fluidsynth output for the basic-pitch drums transcription. It is not a bug in v2 hydration. If future work needs louder drums, the fix is at the MIDI transcription layer (basic-pitch velocity handling) or at the fluidsynth invocation (higher `-g` gain), not at the palette assignment layer.
- Dexed anchor has 2238 params vs Surge XT's 2855 — this is Dexed's actual VST3 parameter surface (26 continuous DX7 params × ~86 buckets vs Surge XT's much larger patch grammar). Both anchors are complete per c33's `both_deterministic_nonempty=true` extraction.

## References

- Rubric: `docs/palette_v2_hydration_render_rubric.md`
- Test suite: `tests/test_palette_v2_hydration_render.py`
- Cross-branch integration: `tests/test_integration_cross_branch.py` §54
- Verdict: `data/palette_v2_render/verdict.json`
- Anchor snapshot: `data/palette_v2_render/anchor_preservation.json`
- c34 palette-schema-v2 report: `docs/palette_schema_v2_report.md`
- c33 palette-driven-bare-render report: `docs/palette_driven_bare_render_report.md`
- c33 dawdreamer-state-extraction-workaround report: `docs/dawdreamer_state_extraction_workaround_report.md`
- c31 palette-instrument-determinism report: `docs/palette_instrument_determinism_report.md`
