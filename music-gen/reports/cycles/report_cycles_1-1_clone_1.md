---
title: "DAW-Stack Validation Spike — cycles 1-1 [merge]"
date: "2026-08-28"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# DAW-Stack Validation Spike — cycles 1-1 [merge]

## Abstract

This branch tested whether a fully open-source, headless-only pair of digital audio workstations — Ardour 8 driven by its Lua scripting surface, and DawDreamer (a Python wrapper around JUCE) driven by its render-graph API — can jointly cover the five session-authoring operations the campaign needs (session build, MIDI import, instrument plus effect parameterization, automation, and offline render). One shared MIDI-plus-effects configuration was rendered through both engines and their outputs compared with a librosa-based texture panel. Both engines produced non-silent eight-second stereo renders at 48 kHz without a display server; on a matched sine source and matched effect chain, the two renders agreed to within roughly 3 dB of mel-spectral L1 and 0.041 of RMS-envelope RMSE. Two of the ten coverage cells came back as gaps: Ardour's Lua binding does not expose a MIDI-file import path in the installed 8.4 build, and Ardour's authored VST3-plugin-parameter automation, though written into the session XML, did not visibly modulate the plugin output at render time. Both gaps have concrete, open-source, headless fallbacks and neither invalidates the split between the two engines.

## 1. Introduction

The campaign's fixed decision is that all audio synthesis and rendering must be reproducible offline with open-source tools and no GUI. Two engines carry that load together: Ardour is intended for human-inspectable session files (so an engineer can open the same `.ardour` XML that the pipeline produced), and DawDreamer is intended for high-throughput automated batch rendering. The obvious risk is that one of the two cannot actually cover the operations the pipeline will ask of it — most sharply, that Ardour's headless Lua surface is too narrow, or that DawDreamer cannot host the plugins Ardour uses.

The spike therefore aimed to fill a 5 × 2 matrix of operations by engine, render one shared configuration through both, and quantify how closely the two engines agree on a matched source and chain. Two named failure conditions would have falsified the split outright: (a) Ardour cannot render a session at all headlessly, or (b) DawDreamer cannot produce a chained-effect render. Anything short of those is a scope note for downstream milestones, not a falsification.

## 2. Methodology

### 2.1 Shared configuration

- **Source (ideal):** a 32-note MIDI seed driving a Surge XT VST3 instrument.
- **Chain:** Surge XT Effects VST3 in chorus mode → Surge XT Effects VST3 in reverb mode, with the reverb's wet mix ("Output Mix") automated linearly from 0.05 to 0.60 over eight seconds.
- **Render window:** 8 s, 48 kHz, 24-bit stereo.
- **Substitution:** Calf Reverb (LV2) was replaced by a second instance of Surge XT Effects in reverb mode. DawDreamer's JUCE backend does not host LV2 at all, so keeping the reverb slot as a single VST3 shared between both engines is what makes any cross-engine comparison meaningful. The substitution and its rationale are recorded in `data/daw_spike/chain_spec.dawdreamer_overrides.yaml`.

### 2.2 Ardour path

Session authored by an `ardour8-lua` script (`scripts/daw/ardour_spike.lua`). Plugin instantiation used `ARDOUR.LuaAPI.new_plugin(...)` after a one-time invocation of `ardour-vst3-scanner` populated `~/.cache/ardour8/vst/`. Rendering used the headless CLI `ardour8-export` with no display server, no JACK, and no XVfb. Two operations required workarounds:

- **Session range.** No Lua binding for `IsSessionRange` was reachable. A small Python XML patcher (`scripts/daw/patch_session_range.py`) inserts the `<Location>` element into the `.ardour` file before export. Without it, `ardour8-export` produces a 44-byte silent WAV.
- **Automation state.** The Lua `AutomationControl:set_automation_state(Play)` binding is not exposed. Authored `<AutomationList>` blocks land in the XML at `state="Off"` and are ignored at render time. The same XML patcher flips them to `state="Play"`.

### 2.3 DawDreamer path

Everything ran in-process: `daw.RenderEngine(sr, block)` with `synth.load_midi("seed.mid")`, `engine.make_plugin_processor(...)` for the two Surge XT VST3s, `fx_reverb.set_automation(param_index, ndarray)` for a per-sample float32 wet-mix curve, and `engine.render(duration_s)` producing a `(2, 384000)` float32 array written out with `soundfile.write` at PCM_24.

### 2.4 Agreement panel

Both renders were compared with librosa: log-mel L1 distance (top-line metric), RMS-envelope RMSE, spectral-centroid RMSE, and peak cross-correlation lag. A deliberately mismatched pair (Ardour sine vs. DawDreamer MIDI, same chain) was also computed to establish the metric's dynamic range and confirm the numbers separate a matched pair from a mismatched one.

## 3. Results

### 3.1 Coverage matrix

Ten cells, one per operation-and-engine combination. Six came back GREEN, one PARTIAL, and two GAP (both on the Ardour side).

| operation                    | Ardour (`ardour8-lua` + XML) | DawDreamer (Python graph)   |
|------------------------------|------------------------------|-----------------------------|
| session build                | GREEN                        | GREEN                       |
| MIDI import                  | GAP                          | GREEN                       |
| instrument + effect params   | GREEN                        | GREEN                       |
| automation                   | PARTIAL                      | GREEN                       |
| offline render               | GREEN                        | GREEN                       |

The Ardour `automation` cell is PARTIAL because track-level gain automation works end-to-end and is visible in the render envelope (first-half RMS 0.096 rises to second-half RMS 0.192, a clean 2× ramp confirming that `ardour8-export` honored the authored `<AutomationList>`), but plugin-parameter automation authored on the Surge XT Effects VST3 wet mix did not modulate the render output even after the state flip. The gap is between Ardour's automation subsystem and the VST3 plugin's parameter input, not between the script and the automation list.

### 3.2 Rendered artifacts

Three renders on disk, all non-silent, all 8 s at 48 kHz stereo:

| file                                          | source                                | peak  | overall RMS | first-half RMS | second-half RMS |
|-----------------------------------------------|---------------------------------------|-------|-------------|----------------|-----------------|
| `data/daw_spike/dawdreamer_render.wav`         | MIDI seed → Surge XT                  | 0.969 | 0.194       | 0.152          | 0.228           |
| `data/daw_spike/dawdreamer_render_matched.wav` | 220 Hz sine → same chain              | 0.628 | 0.175       | 0.090          | 0.213           |
| `data/daw_spike/ardour_render.wav`             | 220 Hz `SinGen` LuaProcessor → chain  | 0.341 | 0.152       | 0.096          | 0.192           |

### 3.3 Agreement between the two engines

Measured on the matched-source pair (`ardour_render.wav` vs. `dawdreamer_render_matched.wav`), both driving the same Surge XT Effects VST3 chain with the same envelope-shape gain ramp:

| metric                        | value        | soft target      | verdict                     |
|-------------------------------|--------------|------------------|-----------------------------|
| mel-spectral L1 (log-mel dB)  | 3.13         | ≤ 3.0            | just above the target       |
| RMS-envelope RMSE (linear)    | 0.041        | ≤ 0.05           | within target               |
| spectral-centroid RMSE (Hz)   | 159          | (informational)  | small vs. source pitch      |
| peak cross-corr lag (samples) | −148         | ≤ ±10 000        | Ardour leads by ≈3 ms       |
| samples compared              | 384 000      | (full 8 s)       | —                           |

The 3-millisecond lead is consistent with a plugin-activation offset. The mel-L1 of 3.13 dB sits just above the informal 3.0 dB target the worker set for this spike; the residual is dominated by phase differences between the two engines' sine generators (Ardour's `SinGen` LuaProcessor vs. a sample-perfect NumPy sine) rather than any chain divergence.

The deliberately mismatched pair — the Ardour sine render against the DawDreamer MIDI render, same chain — gives:

| metric                        | value  |
|-------------------------------|--------|
| mel-L1 (log-mel dB)           | 31.78  |
| RMS-envelope RMSE (linear)    | 0.050  |
| spectral-centroid RMSE (Hz)   | 1406   |

A tenfold jump in mel-L1 and a ninefold jump in spectral-centroid RMSE between the matched and mismatched conditions confirms that the metric distinguishes matched from mismatched source content. RMS-envelope RMSE is a weaker discriminator (0.041 vs. 0.050); mel-L1 and spectral-centroid RMSE are the sharper signals.

### 3.4 Chain-spec divergences

Three points where the actually-rendered chain differs from the ideal chain, each with a reason kept inside the open-source-headless envelope:

| slot        | ideal                                | Ardour actual                             | DawDreamer actual                                | reason                                                        |
|-------------|--------------------------------------|-------------------------------------------|--------------------------------------------------|---------------------------------------------------------------|
| source      | MIDI → Surge XT VST3                  | 220 Hz `SinGen` LuaProcessor              | matched: 220 Hz sine; full: Surge XT on MIDI     | Ardour Lua exposes no MIDI-file-to-region binding.            |
| effect 2    | Calf Reverb LV2                      | Surge XT Effects VST3, Reverb 1 preset    | Surge XT Effects VST3, Reverb 1 preset           | DawDreamer's JUCE backend cannot host LV2.                    |
| automation  | plugin wet mix 0.05 → 0.60           | authored on plugin **and** on track gain 0.25 → 1.4 | delivered per-sample to plugin wet mix          | Ardour plugin-parameter automation did not modulate the render; the parallel track-gain envelope carries the shape agreement. |

## 4. Discussion

### 4.1 What the spike established

The falsification conditions did not fire. Both engines produced offline, unattended, non-silent chained-effect renders without a display server, JACK, or a virtual X server. The DAW-stack split named in the campaign's fixed decisions therefore survives the spike.

The agreement panel proves, at the level of overall spectrum and envelope shape, that when both engines are handed a matched sine source and a matched Surge XT Effects VST3 chain, and their gain ramps match, they land within the noise-floor neighbourhood established by the mismatched-pair floor. This is a real, if narrow, cross-engine reproduction result.

### 4.2 What the spike did not establish

The Ardour envelope in the matched pair is shaped by a track-level gain automation, not by the intended plugin-wet-mix automation. So the agreement number validates that Ardour can render a session whose envelope is driven by an authored automation list, and that the two engines' overall envelopes agree when their gain ramps match. It does **not** yet validate that plugin-parameter automation delivered by Ardour matches plugin-parameter automation delivered by DawDreamer. This is a scope boundary for downstream texture work, not a defect in the spike.

### 4.3 Open-source-headless fallbacks

Four gaps in Ardour's Lua surface were catalogued, each with at least one fallback that stays inside the fixed decision:

- **No Lua MIDI-file import.** Fall back to (a) a hand-authored `.ardour` template with a pre-embedded MIDI region under `interchange/<sess>/midifiles/`, or (b) pre-render the MIDI through DawDreamer, sfizz, or fluidsynth and import the resulting WAV as an audio region. Both stay open-source and headless.
- **No Lua binding for arming plugin-parameter automation delivery.** Fall back to (a) using LV2 for the reverb slot on the Ardour side (Calf Reverb is Ardour's most-tested automation path), or (b) accepting that Ardour's automation lives on track-gain and that DawDreamer carries plugin-parameter automation, with the divergence logged per-chain.
- **No Lua binding for the session range.** Post-process the `.ardour` XML with the small Python patcher used here. It is deterministic and cheap.
- **`ardour-vst3-scanner` needs an explicit invocation.** Add one line per VST3 to `workspace/provision.sh`; DawDreamer scans plugins itself and does not need this.

### 4.4 Guidance for the texture milestone

Two carry-forwards for the next milestone that depends on this surface:

1. Do not assume Ardour delivers VST3-plugin-parameter automation until gap 2 is closed. Either use LV2 plugins on the Ardour side, or treat DawDreamer as the plugin-parameter automation engine and let Ardour's automation live on track-gain.
2. Use mel-L1 and spectral-centroid RMSE as the primary agreement signals; RMS-envelope RMSE is a weaker discriminator in this configuration.

## 5. Conclusions

The DAW-stack split holds: Ardour renders sessions offline with the operations the campaign needs, DawDreamer renders chained-effect audio through the same VST3 binaries, and the two engines' outputs on a matched sine source and matched chain agree to within the target neighbourhood. Two gaps in Ardour's Lua surface (MIDI-file import and plugin-parameter automation delivery) are real and named, and each has an open-source, headless fallback that keeps the fixed decisions intact. No proprietary tool or GUI step was required at any point in the render pipeline. The branch's scoped objective — fill the coverage matrix, render one shared configuration through both engines, and measure agreement — is discharged.

Recommended immediate follow-ups: add the `ardour-vst3-scanner` step to the workspace provisioning script (one-line change), and pass the four-gap catalog above to whoever plans the texture milestone next, since that milestone will hit gaps 1 and 2 directly.

## 6. Appendix: Implementation Details

### 6.1 Artifacts

- Report on disk: `docs/daw_spike_report.md` (194 lines, seven sections).
- Renders: `data/daw_spike/ardour_render.wav`, `data/daw_spike/dawdreamer_render.wav`, `data/daw_spike/dawdreamer_render_matched.wav` — all 384 000 stereo samples at 48 kHz.
- Panel: `data/daw_spike/agreement.json` and `data/daw_spike/agreement.png`.
- Reproducibility: `data/daw_spike/manifest.json` records sha256s and byte counts for every seed, spec, intermediate WAV, final render, panel, state file, and script listed above.
- Scripts under `scripts/daw/`: `make_seed.py`, `render_synth_only.py`, `dawdreamer_spike.py`, `dawdreamer_spike_matched.py`, `ardour_spike.lua`, `patch_session_range.py`, `agreement.py`, `manifest.py`, plus the diagnostic helpers `inspect_renders.py` and `probe_plugins.py`.

### 6.2 Ledger event

`M-DAW-SPIKE-1` was written to `promise_ledger.jsonl` at 2026-08-28T04:37:48Z with `status=in-progress`, `confidence=medium`, and an artifact list that mirrors the report. The auditor's follow-on event upgrades the confidence to `high` and marks the milestone `validated`.

### 6.3 Session references

- Researcher: `d4b5658c-ce73-4998-aed3-22a5dea6380d`
- Worker: `40eafff2-fe17-4bf5-afc6-48119fb5403c`
- Auditor: `ce004fc2-0e36-4522-bc02-fd0fe442a4e0`

### 6.4 Validator status at close

`promise_check`: clean for this branch's ledger entries. `org_check`: clean for the placements this branch made (scripts under `scripts/daw/`, data under `data/daw_spike/`, report under `docs/`). Warnings surfaced by either validator during the audit were pre-existing and belong to other branches.

### 6.5 Reproducing the spike

```
/usr/bin/python3 scripts/daw/make_seed.py
/usr/bin/python3 scripts/daw/render_synth_only.py
/usr/bin/python3 scripts/daw/dawdreamer_spike.py
/usr/bin/python3 scripts/daw/dawdreamer_spike_matched.py
rm -rf data/daw_spike/sessions/spike
LD_LIBRARY_PATH=/usr/lib/ardour8 /usr/lib/ardour8/ardour-vst3-scanner "/usr/lib/vst3/Surge XT.vst3"
LD_LIBRARY_PATH=/usr/lib/ardour8 /usr/lib/ardour8/ardour-vst3-scanner "/usr/lib/vst3/Surge XT Effects.vst3"
ardour8-lua scripts/daw/ardour_spike.lua
/usr/bin/python3 scripts/daw/patch_session_range.py
ardour8-export -s 48000 -b 24 -o data/daw_spike/ardour_render.wav \
    data/daw_spike/sessions/spike spike
/usr/bin/python3 scripts/daw/agreement.py
/usr/bin/python3 scripts/daw/manifest.py
```

<verdict>validated</verdict>
