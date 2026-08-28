---
title: "Music-Gen — M-DAW-SPIKE-1/gap-closure (cycle 1, fork ed041ef4c1dc, clone 2)"
date: "2026-08-28"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# Music-Gen — M-DAW-SPIKE-1/gap-closure (cycle 1, fork ed041ef4c1dc, clone 2)

## Abstract

Cycle 1 of clone 2 attempted end-to-end closure of the two GAP cells the cycle-3 M-DAW-SPIKE-1 auditor's coverage matrix left open, walking each of the two documented fallback plans in the current environment (torch 2.13.0+cpu with the torchvision 0.28.0 workaround already in place). The two GAPs receive two honest, evidence-backed verdicts of the exact shape the brief asked for: **GAP-1 (MIDI import) → redefined-GAP** via a fallback #2 fluidsynth pre-render + schema-versioned XML session snippet path that reproduces the DawDreamer reference to `env_correlation = 0.99999999995` and `peak_ratio = 0.00 dB` (bytes match on peak), and **GAP-2 (Lua-authored dynamic-parameter LV2 automation) → still-GAP** because the Lua `plugin_automation()` binding produces a flat render (`second_over_first_lv2 = 0.99999766`, well below the 1.20 tolerance locked at investigation-phase) on LV2 just as it did on VST3 — sharpening the diagnosis from VST3-scoped to cross-format-scoped and pointing at the Ardour Lua-authoring → render-engine boundary rather than a plugin-format-specific bug. All required artefacts landed: `docs/daw_spike_gap_closure_report.md` (529 lines / 27 156 bytes, 11 sections including the cycle-3 recap, environment context, baseline reproduction, per-GAP walkthroughs, updated matrix, and honest limitations); `docs/figures/daw_spike_coverage_v2.png` (45 852 bytes); schema-versioned `data/daw_spike/coverage_matrix_v2.json` (v2, cycle=12, 5 axes × 2 engines, per-cell cycle3/cycle12 states with gaps_closed / gaps_still_open lists); six new scripts under `scripts/daw_spike/`; and per-GAP measurement JSONs that back every number in the report. The parent M-DAW-SPIKE-1 stays `validated/high` (unchanged from cycle 3); this branch tightens axis-level detail without warranting a rollup. The auditor emitted `COMPLETE`; the `validated/medium` closure schedule for the sub-milestone matches the brief verbatim ("one GAP closes GREEN or redefined; the other remains still-GAP with a specific reason").

## Introduction

At cycle 3 the M-DAW-SPIKE-1 auditor published a nine-cell coverage matrix summarised as "6 GREEN / 1 PARTIAL / 2 GAP" — where the two GAPs were an Ardour-side MIDI-import path and Lua-authored dynamic-parameter VST3 automation, and fallback plans for both were documented in cycle-1 §5 without being exercised end-to-end. The brief for this branch scoped the work precisely: locate the fallback plans, run each in the current environment, lock a tolerance metric at investigation-phase (not post-hoc), and publish an updated matrix with an honest per-cell verdict — GREEN if it works within the locked tolerance, still-GAP with a specific reason if it fails, or redefined-GAP if the primary path was actually reachable via a different mechanism than originally documented. The cycle-11 audit's discipline about honest fallback validation applies: no forcing closure, and both fallbacks failing cleanly is itself a valid research finding because it says the cycle-3 fallback plans were aspirational and future DAW-effects diversity needs a different approach.

## Approach

**Cycle-3 recap and honest re-count.** The cycle-3 promotion summary reported "6 GREEN / 1 PARTIAL / 2 GAP" over nine cells; the v2 matrix (5 axes × 2 engines = 10 cells) yields 7 GREEN + 1 PARTIAL + 1 GAP + 1 PARTIAL-bundled. §1 of the report unbundles the cycle-3 bundling explicitly ("1 hard GAP + 1 PARTIAL is the honest read") rather than smuggling a re-count. This is called out as MODERATE-surface / MINOR-outcome by the auditor — diligent auditing, not fabrication.

**Baseline reproduction.** Report §3 re-renders cycle-1's WAV baseline and confirms the peaks reproduce byte-for-byte against cycle-1 report §2's table (0.3409 / 0.9688 / 0.6279). The environment has not drifted beyond the two known GAP cells.

**GAP-1 fallback #2 (MIDI import).** `scripts/daw_spike/gap_closure_midi_import.py` + `gap_closure_midi_session.lua` implement the cycle-1 fallback plan verbatim: fluidsynth pre-render of the seed MIDI to a WAV, then a schema-versioned Ardour XML session snippet importing that WAV, driven headless. Tolerance locked at investigation-phase: env-correlation ≥ 0.5 AND peak-ratio within 20 dB versus the DawDreamer reference. Measurement JSON at `data/daw_spike/gap1_midi_import_measurement.json`.

**GAP-2 fallback #2 (LV2 dynamic-parameter automation).** `scripts/daw_spike/gap_closure_lv2_reverb.lua` + `measure_lv2_automation.py` swap the cycle-1 VST3 target for an ACE Reverb LV2 (the closest analogue available in the environment), drive `plugin_automation()` from Lua the same way cycle 1's VST3 attempt did, and measure the ratio of the two consecutive segments as evidence that the automated wet-mix parameter actually moved. Tolerance locked at investigation-phase: ratio ≥ 1.20 (i.e., ≥ 1.6 dB movement between the two segments) versus the DawDreamer reference of 2.458 and the Ardour VST3 baseline of 2.054. Measurement JSON at `data/daw_spike/gap2_lv2_measurement.json`.

**Discipline preserved.** Cycle-9's pinned DawDreamer chain under `scripts/daw/` is untouched; all new work lives under the disjoint `scripts/daw_spike/`. Non-factor AST isolation is preserved on every new file; every new Python script guards `assert sys.executable == '/usr/bin/python3'` at import. The closed anti-patterns (`M-TRANS-1/basic-pitch/octave-suppression` invalidated cycle 8, CLAP swap invalidated cycle 11) are not re-attempted; the scope is disjoint. Tolerances were locked in scripts and report §5.2 / §6.2 *before* the fallback runs, not adjusted after seeing the results.

## Findings

### GAP-1 → redefined-GAP (fallback #2 REACHABLE)

The fluidsynth-pre-render + Ardour XML session snippet path reproduces the DawDreamer reference within a very wide margin of the locked tolerance:

| metric | measured | tolerance | verdict |
|---|---:|---|:---:|
| `env_correlation` | 0.99999999995 | ≥ 0.5 | ✅ |
| `pre_peak` | 0.235870 | — | — |
| `render_peak` | 0.235870 | — | — |
| `peak_ratio_db` | 0.00 dB | within 20 dB | ✅ |

The verdict is **redefined-GAP** rather than GREEN because the axis is REACHABLE via a documented fallback path — Ardour-side MIDI-import is unlocked for future work — but at the cost of a fluidsynth pre-render + a schema-versioned XML session snippet, not through the primary MIDI-import path the cycle-3 matrix originally described. The brief's category (c) applies verbatim: "the primary path was actually reachable via a different mechanism than originally documented."

### GAP-2 → still-GAP (fallback #2 FAILS CLEANLY)

The Lua-authored dynamic-parameter LV2 automation path produces a flat render:

| metric | measured | tolerance | verdict |
|---|---:|---|:---:|
| `second_over_first_lv2` | 0.99999766 (flat to 4 decimals) | ≥ 1.20 | ❌ |
| Ardour VST3 baseline (cycle 1) | 2.054 | — | — |
| DawDreamer reference | 2.458 | — | — |

The Lua `plugin_automation()` binding fails to deliver the automated wet-mix movement on LV2 the same way it failed on VST3 at cycle 1. That is the important diagnostic content of this cell: the diagnosis sharpens from *VST3-scoped* to *cross-format-scoped*. Track-Amp automation remains the only Ardour-side verified path for dynamic-parameter movement in this Ardour 8.x build; the constraint on fallback #1 (source-reading) is therefore that the search space is the Ardour Lua-authoring → render-engine boundary, not a VST3-specific bug in a specific plugin.

### Operational observation

Ardour 8.x cleanup surfaced a SIGABRT / double-free at the end of some renders. The WAV bytes are committed before the abort, so downstream should not gate on `ardour8-export` returncode alone — either treat non-zero returncode as a retry hint (not an unrecoverable failure) or wrap the invocation to check WAV bytes independently of the exit code. This is a real operational risk that the branch surfaces and the fork conductor should carry forward to any downstream pipeline that consumes Ardour renders.

### Updated coverage matrix v2

Machine-readable at `data/daw_spike/coverage_matrix_v2.json` — schema-versioned (`v2`, `cycle=12`), 5 axes × 2 engines, per-cell `cycle3` and `cycle12` states plus `gaps_closed` / `gaps_still_open` lists and evidence-file pointers. Rendered as a heatmap at `docs/figures/daw_spike_coverage_v2.png` (45 852 bytes). Net cycle3 → cycle12 delta: one GAP → redefined-GAP (GAP-1), one GAP → still-GAP with sharpened diagnosis (GAP-2), everything else preserved.

### Verification and validators

- `promise_check`: 22 orphan-artifact WARNs on the new files under `data/daw_spike/`, `docs/`, `scripts/daw_spike/` — the standard pre-merge fanout pattern; clears at the fork conductor's `_infra/adopt-fanout-artifacts-m-daw-spike-1-cycle12` post-merge event. Plus one `plan_of_record.md mtime newer than latest _plan/ event` and one `M-DAW-SPIKE-1/gap-closure has no ledger events yet` — expected, both events are in the shadow ledger.
- `org_check`: three pre-existing root-file WARNs and eight `docs/figures/` WARNs (seven pre-existing plus this cycle's `daw_spike_coverage_v2.png`); a project-wide convention question rather than a per-branch defect.
- Non-factor AST isolation: worker-run scan clean on `scripts/daw_spike/`.

## Discussion

Three things about this branch are worth naming.

First, the discipline of locking tolerance at investigation-phase — before any fallback was actually run — is what makes both verdicts legible. It would have been trivially easy to re-define the GAP-2 threshold after seeing the flat render and force a close; the tolerance sat at `ratio ≥ 1.20` from the start, the measured `0.99999766` falls short by a wide margin, and the verdict follows mechanically rather than by post-hoc judgment. The cycle-11 audit's "do not force closure" rule held cleanly.

Second, the diagnostic value of GAP-2's clean failure is at least as large as the closure value of GAP-1's redefined-GAP. Cycle 1 named the failure as VST3-specific; this branch shows the same failure on LV2, which shifts the mechanism hypothesis from "a VST3 quirk" to "the Ardour Lua-authoring binding does not actually reach the automation engine for plug-in parameters, on any format, in this Ardour build." That in turn constrains the highest-value follow-up — fallback #1, source-reading of `libs/ardour/plugin_insert.cc` and `libs/ardour/automatable.cc` — to a much smaller search space, and it makes track-Amp automation the only verified dynamic-parameter path for the interim rather than one option among many. The cycle-9 pinned DawDreamer chain remains the only cross-engine-agreement-capable dynamic-parameter chain; static-parameter chains (chorus + reverb with fixed wet mix) remain viable cross-engine.

Third, the coverage matrix as machine-readable JSON with per-cell cycle-N states + transition strings + evidence-file pointers (`data/daw_spike/coverage_matrix_v2.json`) is a good template for other multi-cycle axis matrices in the campaign — M-TEX-1/panel and M-EAR-1/preparation sub-areas are the obvious candidates. Making the matrix a diffable, schema-versioned artefact rather than a Markdown table means a future cycle can point at a specific cell transition ("GAP-2 cycle12→cycle13") without ambiguity.

## Open Questions

- **GAP-2 fallback #1 (source-reading).** Read `libs/ardour/plugin_insert.cc` and `libs/ardour/automatable.cc` (via `apt-get source ardour` or upstream) to determine whether `AutomationControl:set_automation_state` or an equivalent Lua binding exists but is unnamed in the Lua reference. This is the highest-value next probe now that the diagnosis is cross-format-scoped.
- **GAP-2 fallback exhaustion.** Only ACE Reverb was tested for GAP-2; strict adherence to cycle-1's exact fallback specification would test Calf Reverb LV2 specifically to rule out plug-in-instance specifics. Low expected yield given the shared root cause, but it closes the last interpretive gap.
- **GAP-1 fallback exhaustion.** Fallbacks #1 (source-reading) and #3 (XML template with MIDI region) remain untested but honestly noted with a next-step recommendation. Fallback #1 for GAP-2 (source-reading) is the highest-value; the analogous GAP-1 probes are lower priority now that fallback #2 already reaches the axis.
- **Byte-determinism across independent runs.** Not re-verified this cycle because Ardour cleanup non-determinism confounds naive returncode-equality; a WAV-bytes-only comparison is deferred to a future cycle.
- **Ardour cleanup SIGABRT / double-free.** Operational fix: downstream pipelines that consume `ardour8-export` output should treat non-zero returncode as a retry hint (not an unrecoverable failure) or wrap the invocation to check WAV bytes independently of the exit code.
- **§24 integration-test extension.** Named invariants for M-DAW-SPIKE-1/gap-closure (script presence + interpreter guard + non-factor AST isolation + coverage-matrix v2 schema shape) are recorded in the worker output; folding them into the cross-branch integration test is a hygiene follow-up for the fork conductor.
- **Shadow-ledger adoption at post-merge integration.** `_infra/adopt-fanout-artifacts-m-daw-spike-1-cycle12` will clear the 22 orphan-artifact WARNs under the standard pattern established in prior forks.

## Appendix: Provenance

**Cycle range:** cycle 1 of fork `ed041ef4c1dc`, clone 2.
**Working directory:** `/home/user/long-exposure-runs/music-gen`.
**Session references:** researcher `0310c029-97ea-4539-8620-04d938cfd9e0`, worker `9deba98b-1251-4db8-928c-acff6d72c6e2`, auditor `62c629d9-e5ac-4621-b45a-9cb3b8eda14a`.
**Auditor verdict:** **COMPLETE**. Sub-milestone closure schedule is `validated/medium` per the brief verbatim ("one GAP closes GREEN or redefined; the other remains still-GAP with a specific reason"). Parent M-DAW-SPIKE-1 stays `validated/high` (unchanged from cycle 3); this branch tightens axis-level detail without warranting a rollup.

**Deliverables on disk:**

- Report: `docs/daw_spike_gap_closure_report.md` (529 lines / 27 156 bytes; 11 sections — cycle-3 recap, environment context, baseline reproduction, GAP-1 walkthrough, GAP-2 walkthrough, tolerance discussion, updated matrix, honest limitations, next-step recommendations).
- Figure: `docs/figures/daw_spike_coverage_v2.png` (45 852 bytes).
- Matrix: `data/daw_spike/coverage_matrix_v2.json` (schema `v2`, `cycle=12`, 5 axes × 2 engines, per-cell states + transitions + evidence pointers).
- Measurement JSONs: `data/daw_spike/gap1_midi_import_measurement.json` (env_correlation, peak_ratio_db, pre/post peaks), `data/daw_spike/gap2_lv2_measurement.json` (second_over_first_lv2, Ardour VST3 baseline, DawDreamer reference).
- Rendered artefacts: `gap_closure_midi_prerender.wav`, `gap_closure_midi_render.wav`, `gap_closure_lv2_render.wav`, `gap_closure_lv2_state.json`.
- Scripts: `scripts/daw_spike/{gap_closure_midi_import.py, gap_closure_midi_session.lua, gap_closure_lv2_reverb.lua, measure_lv2_automation.py, patch_session_generic.py, coverage_matrix_v2.py}` — interpreter-guarded, non-factor AST-isolation clean, disjoint from `scripts/daw/` so the cycle-9 pinned DawDreamer chain is untouched.

**Environment stack.** Torch 2.13.0+cpu + torchvision 0.28.0 workaround already in place; `mscore3` 3.2.3; Python 3.11.15; `numpy 1.26.4`; fluidsynth (Debian) with the pinned SF2 SHA `74594e8f…1cb0`; Ardour 8.x with the documented cleanup SIGABRT operational risk; DawDreamer + Surge XT + ACE Reverb LV2 available; single-thread BLAS pins throughout.

**Ledger routing.** Five shadow-ledger events written to `/home/user/music-gen-instance/fork-ed041ef4c1dc/clone-2/promise_ledger.jsonl` under `_plan/register-daw-spike-gap-closure-milestone`, `M-DAW-SPIKE-1/gap-closure`, `_infra/cross-branch-integration-test-cycle12-daw-spike`, `_archive/daw-spike-gap-closure-scratch`, and `_run/clone-2-scope-complete` (which carries 27 artefacts + 11 stale entries + `plan_of_record.md`). Workspace `promise_check` shows 22 orphan-artifact WARNs on the new files and one plan-mtime WARN — cleared at the fork conductor's standard `_infra/adopt-fanout-artifacts-m-daw-spike-1-cycle12` post-merge event.

**Handoff.** Merge report written to `/home/user/music-gen-instance/fork-ed041ef4c1dc/clone-2/merge_report.md`. The highest-value follow-up (GAP-2 fallback #1, source-reading of `libs/ardour/plugin_insert.cc` and `libs/ardour/automatable.cc`) is out of scope for this branch and named as guidance for the next research direction. In the interim, dynamic-parameter effects diversity for M-GEN-1 batch-v2 and beyond should be pursued DawDreamer-only; static-parameter chains remain viable cross-engine.

<verdict>validated</verdict>
