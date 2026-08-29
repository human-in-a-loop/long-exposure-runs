---
created: 2026-08-29T02:45:00Z
cycle: 31
run_id: run-2026-08-28T040704Z
agent: worker
milestone: M-DAW-SPIKE-1/palette-instrument-determinism
---

# Palette instrument determinism report (cycle 31, branch A)

**Verdict roll-up:** 1 GREEN, 0 REDEFINED_GAP, 2 STILL_GAP.

| Instrument | Loader pathway    | Verdict       |
|-----------:|-------------------|---------------|
| Surge XT   | dawdreamer_vst3   | STILL_GAP     |
| Dexed      | dawdreamer_vst3   | STILL_GAP     |
| sfizz      | sfizz_render_cli  | GREEN         |

The falsifiability escape hatch (rubric §2, STILL_GAP verdict) fires
for two of the three instruments. This is a legitimate first-class
negative finding per cycle-11 M-TEX-1/panel/embedding discipline: it
informs cycle-32 palette-driven bare render design that Surge XT and
Dexed cannot presently underwrite byte-deterministic × 2 without
plugin-side or DawDreamer-side pinning work. sfizz remains eligible
for the palette as-is.

## §1 Cycle context + operator-steering priority

Cycle 31 branch A. Egress remains blocked at cycle start (single
non-blocking retry logged to `notes/cycle_31_egress_probe.txt`,
`harvest_exit=0`, `bands 6/5/4: 0/0/0 files`). Operator directive (2):
`*.googlevideo.com` unblocking is the standing armed harness's trigger,
not this branch's; branch work proceeded independently.

No pause memo; no Hold Pattern narrative. Branch shipped its 3-verdict
rubric before any probe script landed under `scripts/palette_probe/`
(rubric doc mtime precedes the first probe script mtime; git-log
ordering additionally verified where a project commit followed).

## §2 Rubric recap

Rubric SHA-256 (frozen, pre-registered): `75daa068aa804351db744cdb3a41df151ba682bbe3278c7c8cb8870a54ac7c96`
(first 16 hex: `75daa068aa804351`). Full document at
`docs/palette_instrument_determinism_rubric.md`. Recorded in
`data/palette_probe/rubric_hash.txt` and in the verdict roll-up ledger
event's narrative.

Verdict labels (verbatim from rubric §2):
- **GREEN** — byte-deterministic × 2 achieved.
- **REDEFINED_GAP** — deterministic only after ONE documented pinning
  refinement.
- **STILL_GAP** — non-deterministic under any reasonable pinning; or
  the instrument is not fetchable / not loadable. Falsifiability
  escape hatch invoked.

## §3 Fetchability ladder

Recorded per-instrument in `data/palette_probe/fetchability_ladder.jsonl`.

| Instrument | Binary path                      | Present | Loader pathway     | Loadable |
|-----------:|----------------------------------|:-------:|--------------------|:--------:|
| Surge XT   | `/usr/lib/vst3/Surge XT.vst3`    | yes     | dawdreamer_vst3    | yes      |
| Dexed      | `/usr/lib/vst3/Dexed.vst3`       | yes     | dawdreamer_vst3    | yes      |
| sfizz      | `/usr/bin/sfizz_render` + `data/texture/test.sfz` | yes | sfizz_render_cli | yes      |

**Loader-pathway note (sfizz):** neither VST3 nor LV2 sfizz plugin is
present in this workspace (checked `/usr/lib/vst3/`, `/usr/local/lib/vst3/`,
`/usr/lib/lv2/`, `/usr/local/lib/lv2/`, all sfizz absent). The
`sfizz_render` CLI is present; the pre-existing SFZ reference file
`data/texture/test.sfz` (single-region sawtooth sampler pointing at
`test_saw.wav`) drives it. Loading through the CLI is the honest
reflection of what sfizz can be driven with today — the pinned-state
JSON records this as `loader_pathway: "sfizz_render_cli"` (rubric §3).

**DawDreamer version:** 0.9.0 (invoked under `/usr/bin/python3` 3.11.15).
Every probe script asserts `sys.executable == '/usr/bin/python3'`.

**BLAS pins:** `OMP_NUM_THREADS=OPENBLAS_NUM_THREADS=MKL_NUM_THREADS=1`,
set by `scripts/palette_probe/_shared.py` at import time and by
`run_all.py` in the subprocess env.

## §4 Per-instrument sections

### §4.1 Surge XT — STILL_GAP

- Loader: `dawdreamer_vst3` at `/usr/lib/vst3/Surge XT.vst3`.
- Loadable: yes. `RenderEngine(44100, 512).make_plugin_processor("surge_xt", ...)` succeeds. Parameter dictionary populates (77 KB pinned_state.json — hundreds of Surge parameters exposed).
- Initial probe × 2: `pinned_state.json` SHA-256 **equal** across two runs (`61662ba908809410…`), but `render.wav` SHA-256 **differs**:
  - run1 wav sha16: `fe80fc17ad59b3ab…`
  - run2 wav sha16: `443ca252dd568853…`
  - max-abs sample delta (int16-normalized): **0.318**. Non-trivial audio-domain drift, not a rounding-noise floor.
- Interpretation: the drift lives inside Surge XT's internal state (modulation-source phase, unison detune startup, oscillator sub-sample phase) that DawDreamer's parameter API does not expose. All exposed parameters serialize identically.
- Refinement attempted (per rubric §6): capture `PluginProcessor.get_state()` bytes from a warm-up render, then invoke `load_state(...)` in both refinement runs to force identical internal state.
  - Outcome: **`get_state()` returned empty** (0 bytes) on Surge XT under DawDreamer 0.9.0. The pinning path is unavailable — the plugin's DawDreamer-visible state buffer is not usable as a determinism-pinning mechanism at this API version.
  - Refinement JSON: `data/palette_probe/per_instrument/surge_xt/refinement.json` — `pinning_change: "plugin state API empty"`, `wav_max_abs_drift_before: 0.318…`.
- Verdict: **STILL_GAP** (falsifiability escape hatch invoked). Surge XT is ineligible for the cycle-32 palette-driven bare-render pipeline in its present state.
- Path forward (informational, not committed here): (a) load a Surge XT `.fxp` patch that resets modulation state before render; (b) upgrade DawDreamer past 0.9.0 if a newer release exposes internal-state pinning; (c) hand-author a `.wt` wavetable with no internal-mod nondeterminism. All three belong to a follow-up cycle.

### §4.2 Dexed — STILL_GAP

- Loader: `dawdreamer_vst3` at `/usr/lib/vst3/Dexed.vst3`.
- Loadable: yes. `make_plugin_processor("dexed", ...)` succeeds.
- Initial probe × 2: `pinned_state.json` SHA-256 **equal** (`e6f332af7e2ef753…`), `render.wav` SHA-256 **differs**:
  - run1 wav sha16: `05c48e004fa3cc1c…`
  - run2 wav sha16: `3ac46320ddd6ffe8…`
- Interpretation: same shape as Surge XT — parameters serialize identically, internal FM-operator startup state drifts.
- Refinement: same `get_state()`-based pinning attempted. Result: `get_state()` returned empty on Dexed as well. Pinning path unavailable at DawDreamer 0.9.0.
- Verdict: **STILL_GAP**.
- Path forward: preset load (`.syx` bank) is the standard Dexed determinism pin — belongs to a follow-up cycle.

### §4.3 sfizz — GREEN

- Loader: `sfizz_render_cli` at `/usr/bin/sfizz_render`. SFZ reference: `data/texture/test.sfz` (single-region sawtooth sampler → `test_saw.wav`). Pinned bundle SHA-256 (SFZ + sample): `5f330e7bf42dc4ba…`.
- CLI invocation flags (all pinned): `-b 512 -s 44100 -q 1 -p 64`.
- Initial probe × 2: both `render.wav` (`4f9735d9459d06df…`) and `pinned_state.json` (`1bda0de79181c057…`) SHA-256 **equal**.
- Interpretation: the CLI is deterministic given fixed inputs. The stdlib `wave` module is used to canonicalize the WAV header bytes so any nondeterminism in sfizz's writer would be neutralized (in fact none was observed even before canonicalization).
- Verdict: **GREEN** — no refinement necessary.
- Palette eligibility: sfizz is the sole cycle-32 palette-eligible instrument from this branch.

**Caveat on sfizz plugin_version:** `sfizz_render --version` is not a recognized flag on the installed sfizz build. The pinned-state JSON records the honest CLI response string in `plugin_version` (per rubric §3 discipline of not fabricating). This does not affect determinism.

## §5 Pinned-state JSON format spec

Every `pinned_state.json` conforms to the rubric §3 schema. Enforced by
`scripts/palette_probe/_shared.py::validate_pinned_state` and by the
per-instrument schema-conformance test in
`tests/test_palette_instrument_determinism.py`.

Required keys (name-sorted): `block_size`, `external_state_sha256`,
`loader_pathway`, `midi_input_sha256`, `parameter_dict`,
`plugin_binary_sha256`, `plugin_name`, `plugin_version`, `preset_name`,
`sample_count`, `sample_rate`, `stereo`.

Serialization: `json.dumps(obj, sort_keys=True, indent=2,
separators=(",", ": "))`. Any two runs that produce byte-identical
JSON have canonically-identical semantic content; any drift here is a
schema violation and fails the test.

`plugin_version`, `preset_name`, and `external_state_sha256` are
nullable (`None`) when the loader pathway does not expose them (rubric
§3, cycle-11 discipline).

## §6 Palette-eligibility roll-up

**Cycle-32 palette-driven bare render implications** (informational —
this branch does not gate cycle-32 authoring):

- **sfizz:** eligible now. A palette assignment for a stem that targets
  sfizz with the pinned CLI protocol above will render byte-deterministically.
- **Surge XT:** ineligible in current DawDreamer 0.9.0 wiring. A cycle-32
  palette that assigns Surge XT to any stem must either (i) commit to a
  documented preset-load refinement path (an unmodified follow-up to
  this branch, since the one-refinement budget is exhausted here); or
  (ii) route via `sfizz` or a fluidsynth pathway for that stem; or (iii)
  render Surge XT once, cache the WAV as a stem asset, and treat the
  cached WAV as the deterministic artifact.
- **Dexed:** same shape as Surge XT.

The cycle-13 batch-v2 pipeline (untouched by this branch) already
demonstrates byte-deterministic × 2 rendering via `fluidsynth + cycle-9
DawDreamer effects chain`, so a fluidsynth-anchored palette is a
working fallback for stems that would otherwise target Surge XT/Dexed.

## §7 Cycle-9 effects chain isolation confirmation

**Grep-verified**: no script under `scripts/palette_probe/` imports
`scripts.tex.render_effects_layered` or any module under `scripts/tex/`.
Enforced by `tests/test_palette_instrument_determinism.py::test_cycle9_chain_not_imported`.

Command that reproduces the check locally:

```
grep -rE "from scripts.tex|import scripts.tex|render_effects_layered" \
  scripts/palette_probe/
```

Expected output: empty (exit code 1 from grep).

## §8 Honest failure ledger

Per cycle-3 discipline (fetchability failures are data, not defeats):

1. **sfizz plugin form.** sfizz VST3 / LV2 not present in the workspace.
   Loader pathway pivoted to `sfizz_render` CLI, documented in
   fetchability ladder as `loader_pathway: sfizz_render_cli`. Verdict
   still GREEN — the pivot did not paper over anything; it named the
   available loader and delivered byte-determinism honestly.
2. **DawDreamer 0.9.0 `PluginProcessor.get_state()` returned 0 bytes**
   for both Surge XT and Dexed. This is the root cause of the STILL_GAP
   verdicts. A DawDreamer upgrade or a preset-based pinning refinement
   would need to run in a follow-up cycle.
3. **`sfizz_render --version` unrecognized flag.** Recorded honestly
   in `pinned_state.json[plugin_version]` as the CLI's actual response
   string. No fabrication.
4. **Merge report target directory** (`/home/user/music-gen-instance/fork-cfc5009aca96/clone-0/`)
   is outside this session's writable sandbox. This branch writes a
   copy to `workspace/merge_report_cycle_31_branch_A.md` for the root
   conductor to pick up (documented in the merge report itself and in
   the housekeeping ledger event).

END OF REPORT.
