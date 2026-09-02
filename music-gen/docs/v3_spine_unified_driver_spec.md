---
created: 2026-09-02T23:45:00Z
run_id: run-2026-09-02T234500Z
cycle: 22
agent: worker
milestone: M-V3-SPINE-2/unified-driver-spec-committed
---

# v3 Unified Driver Specification — `recreate_v3.py`

## Purpose

Single parameterized driver that runs the entire v3 per-stem chain for
ANY focus-set song, with NO per-song code paths. Per-song facts live in
data (`data/v3/focus_set_v2.json`); the driver is instrumentation.

Per operator directive 2026-09-02 (verbatim scope items 1, 5, 6):

> Write ONE parameterized driver `scripts/v3_spine/recreate_v3.py
> --song <sha16> [--section operator|auto]` that runs the entire
> per-stem chain with NO per-song code paths … Unit of proof: running
> it twice on the same song → byte-identical deliveries; running it on
> Chicken Grease + Rome → reproduces already-approved deliveries …
> Peach Dream's pending delivery = FIRST delivery produced by the
> unified driver. From c22 on: agent cycles build/improve programs
> and handle creative stages; no agent ever hand-orchestrates a song
> recreation again.

## Rubric — three-verdict

- `V3_UNIFIED_DRIVER_LANDS_pending_operator` — spec chain green,
  driver end-to-end runs green on ≥1 song (Peach Dream mandatory),
  byte-det ×2, env-pin manifest stamped, reproduce-proof panel-equal
  on Chicken Grease + Rome (byte-equal where env pins unchanged).
- `V3_UNIFIED_DRIVER_PARTIAL` — spec + driver land; ≥1 sub-clause
  honestly deferred with named reason (e.g. wall-time in this cycle).
- `V3_UNIFIED_DRIVER_FAILS` — spec + driver present but reproduce
  contract fails or Peach Dream cannot deliver.

Operator ear on Peach Dream remains the only LANDS authority per FD-6;
this verdict class covers ONLY the driver-mechanism gate.

## Three-way `rubric_hash_v3` byte-equality chain

Contract enforced across three artifacts:

1. This document's SHA-256 (mtime hard gate: doc mtime < every mtime
   under `scripts/v3_spine/recreate_v3*` or `long_exposure/v3_pipeline/*`).
2. `data/v3/recreate_v3/rubric_hash.txt` (single-line hex).
3. `verdict.rubric_hash_v3` field in every delivery verdict.json
   produced by the driver.

If any two differ, the delivery is invalidated at emit.

Distinguished from the c50 M-RECREATE-2 `rubric_hash_v2`
(`0e11f704e12c62f8…`) which governs the recreate_v2 arc. The v3-spine
rubric for unified-driver deliveries is `rubric_hash_v3` under this
document. For continuity, existing c4-landed `rubric_hash_v2`
(`c49db5a12e955f26c001165ad6e8f9d191bc26bfd96e24c1b163adc37016451a`)
remains the anchor for per-cycle spine deliveries; c22+ deliveries
carry BOTH keys — `rubric_hash_v3` = this doc SHA (mechanism gate),
`rubric_hash_v2` = c4 chain (v3-spine content gate).

## CLI

```
recreate_v3.py --song <sha16>
               [--section {operator,auto}]     (default: operator)
               [--out <dir>]                   (default: data/v3/deliveries/<sha16>/cycle22/)
               [--verify-det]                  (internal byte-det ×2 gate on outputs)
               [--reproduce-check <dir>]       (compare against existing delivery)
               [--dry-run]                     (parse+validate; no rendering)
```

- `--song <sha16>`: MUST resolve in `data/recreate_v2/focus_set_v2.json.songs[*].audio_sha16`.
  (Note: the brief nominally locates focus_set at `data/v3/focus_set_v2.json`
  but the c50-landed authoritative artifact is under `data/recreate_v2/`;
  the driver honors the on-disk location and this spec follows suit.)
- `--section operator`: uses `focus_set_v2.json.songs[*].chosen_section`
  (t_start_s .. t_end_s per D1 auto-picker). Chicken Grease
  t=233.6392..263.6392s; Rome t=62.7403..92.7403s; Peach Dream
  t=172.8726..202.8726s; WIG t=72.7713..102.7713s; Disco A
  t=21.9196..51.9196s.
- `--section auto`: re-computes chosen section deterministically per
  c50 D1 (combined RMS + onset density, hop=512, argmax, ties broken
  earliest start).
- `--reproduce-check <dir>`: driver renders as usual AND diffs
  per-stage anchors against `<dir>`, emitting
  `reproduce_report.json`. Panel-equal required always; byte-equal
  required where env-pin manifest is byte-identical.
- `--dry-run`: parses focus_set, validates `<sha16>`, prints
  planned stage order and output paths; no side effects.

## Stages (pure functions, composed from `long_exposure/v3_pipeline/`)

Each stage reads its inputs, produces its outputs, and is byte-deterministic
under the c5-established env pins. Located under
`scripts/v3_spine/v3_pipeline/` (the brief nominally names
`long_exposure/v3_pipeline/*` but `long_exposure/` is an external
read-only orchestrator package outside this workspace; consumers
import from `scripts.v3_spine.v3_pipeline.env_pin`).

0. `slice(mp3, t_start, t_dur, dst_wav)` — ffmpeg-cut the operator
   section from the raw MP3.
1. `rehtdemucs(section_wav, out_dir, verify_det)`
   → 6 stem WAVs (htdemucs_6s, byte-det ×2 gate).
2. `tempo_map(drums_stem_wav)` → `tempo_choice.json`
   (`librosa.beat.beat_track`, 4/4).
3. `muscriptor_per_stem(stems_dir, whitelists, out_dir)` → 7 probes
   (drums/bass/guitar/piano/other/vocals + full_mix slice), c3 vocab
   whitelists preserved.
4. `canonicalize_midi(json_probes_dir, out_dir)` → 7 canonical MIDIs
   via READ-ONLY import of `scripts/v3_spine/midi_from_json_events.py`
   (anchor SHA `214372d9…` for anchor `render_stem.py`; canonical
   serializer's own SHA is a separate anchor).
5. `merge_per_stem_midi(per_stem_midis, tempo, out_path)` → `merged.mid`
   with 4/4 structural gates:
   - drums channel 10 non-empty
   - bass median MIDI pitch < 55
   - vocals symbolic-track present
   - zero notes on GM program 4
6. `render_per_track(merged_mid, sf2_path, out_dir)` → per-track WAVs
   via fluidsynth (SF2 SHA `74594e8f…1cb0`).
7. `vocals_overlay(htdemucs_vocals_wav, out_wav)` → D2 SHA-verified copy.
8. `mix_match(per_track_wavs, vocals_overlay_wav, out_wav)` → rc7
   Method A plain broadband RMS-match + sum (matches c5 operator-blessed
   shape). NOT rc7 Method B (EQ+LUFS) — that's a separate palette path.
9. `panel_measure(original_wav, reconstruction_wav)` → 8-key panel
   on BOTH (original, mix) and (fluidsynth-only, mix) comparisons.
10. `emit_delivery(out_dir, verdict, manifest_with_env_pins,
    rubric_hash_v3_chain)` → verdict.json + manifest.json + WAVs.

## Discipline (enforced at import/CLI time)

- `/usr/bin/python3` interpreter guard on `recreate_v3.py` entrypoint.
- Env pins set BEFORE any observed import that could branch on them:
  `PYTHONHASHSEED=0`, `SOURCE_DATE_EPOCH=1756463424`, `TZ=UTC`,
  `LC_ALL=C.UTF-8`, `OMP_NUM_THREADS=1`, `MKL_NUM_THREADS=1`,
  `OPENBLAS_NUM_THREADS=1`. `torch.manual_seed(0)` in stages
  that touch torch (htdemucs).
- Zero PRNG in pipeline modules (AST-enforced by
  `test_recreate_v3_unified_driver.py`).
- Zero `sidecar_nonfactor` import (AST-enforced).
- Zero VST3 `get_state`/`save_state`/`save_preset`/`load_state`/
  `set_state(bytes)` in pipeline modules (c31/c35 anti-pattern locked,
  AST-enforced).
- FD-1 on any byte-det ×2 gate failure: halt, surface falsifying
  tuple, emit `V3_UNIFIED_DRIVER_FAILS` verdict, blocked_on_operator.
  No retry, no fallback, no tuning.

## env_pins block (stamped into every delivery `manifest.json`)

Emitted by `long_exposure.v3_pipeline.env_pin.emit_env_pin_json()`.
Schema:

```
{
  "python": {"version": "3.11.x", "executable": "/usr/bin/python3"},
  "torch":  {"version": "2.13.0+cpu"|"2.14.0+cpu"|...,
             "file": "/usr/local/.../torch/__init__.py",
             "commit_or_none": null},
  "numpy":  {"version": "1.26.4"|..., "blas": "openblas"|"mkl"|...},
  "librosa":     {"version": "0.10.x"},
  "muscriptor":  {"version": "...", "binary_sha256": "<hex>"},
  "htdemucs_weights": {"<weight_file_relpath>": "<hex>"},
  "soundfont":   {"path": "workspace/.../FluidR3_GM.sf2",
                  "sha256": "74594e8f…1cb0"},
  "fluidsynth":  {"version": "..."},
  "model_safetensors": {"path": "...", "sha256": "<hex>"},
  "env_vars":    {"PYTHONHASHSEED": "0",
                  "SOURCE_DATE_EPOCH": "1756463424",
                  "TZ": "UTC", "LC_ALL": "C.UTF-8",
                  "OMP_NUM_THREADS": "1",
                  "MKL_NUM_THREADS": "1",
                  "OPENBLAS_NUM_THREADS": "1"}
}
```

Canonical form: `json.dumps(sort_keys=True, indent=2)`. Self-anchor
`env_pin.sha256` computed on canonical bytes, embedded as
`env_pins._sha256` field. Byte-det ×2 gate: two calls in same process
return byte-identical JSON. Cross-cycle drift becomes detectable-by-diff:
if `torch.version` or `numpy.blas` changes between c5 and c22, the diff
lands in the delivery manifest.

## Reproduce-check contract

`--reproduce-check <existing_delivery_dir>`:

1. Run the driver as usual into `--out <dir>`.
2. Compare `<out>/manifest.json.env_pins` vs
   `<existing_delivery_dir>/manifest.json.env_pins`. Field-level diff.
3. For each deterministic-anchor file (WAVs, MIDIs, panel TSVs),
   compare SHA-256s.
4. Emit `<out>/reproduce_report.json`:
   ```
   {
     "per_stage_diff": {stage: {status: EQUAL|DRIFT, ...}},
     "per_key_panel_diff": {key: {existing, current, delta}},
     "env_pin_diff": {field: {existing, current}},
     "panel_equal": bool,   # ALWAYS required
     "byte_equal":  bool,   # required IFF env_pin_diff == {}
     "verdict":     REPRODUCE_LANDS|REPRODUCE_PANEL_ONLY|REPRODUCE_FAILS
   }
   ```
5. FD-1: `panel_equal == False` → halt, verdict REPRODUCE_FAILS.

## Retirement list

`_infra/retire-oneoff-drivers-c22` catalogues the following classes
of scripts under `scripts/v3_spine/` for deletion AFTER driver
reproduce-proof green on Chicken Grease + Rome AND Peach Dream
unified delivery lands:

**Delete after green** (all `*_song_<sha16>.py` variants):
- `rehtdemucs_song_*.py`
- `tempo_map_song_*.py`
- `muscriptor_song_*.py`
- `canonicalize_song_*.py`
- `merge_per_stem_midi_song_*.py`
- `render_per_track_song_*.py`
- `vocals_overlay_song_*.py`
- `mix_match_song_*.py`
- `deliver_song_*.py`
- `rc7_per_stem_loudness_song_*.py`
- `sanity_panel_song_*.py`
- `verdict_song_*.py`
- `peach_dream_c20_merge.py`

Expected retirement per song: ~12 per-song scripts × Rome, WIG,
Peach Dream, Chicken Grease, Disco A = ~60 candidate scripts.

**Preserve as first-class**:
- `scripts/v3_spine/recreate_v3.py` (NEW — this driver)
- `long_exposure/v3_pipeline/*` (NEW — stage modules)
- `scripts/palette_render/render_stem.py` (READ-ONLY anchor
  SHA `214372d920a319a9…5b2b`, DO-NOT-TOUCH per c21)
- `scripts/v3_spine/midi_from_json_events.py` (c4 canonical
  serializer)
- Ledger emitters (`*_ledger.py`) — policy artifacts, not pipeline
- Per-cycle verdict/anchor emitters (`torch213_reproduce_probe_c*.py`,
  `anchor_preservation_c*.py`, `verdict_c*.py`) — cycle-scoped
  bookkeeping, retained.

Partial-retirement contract: if any `*_song_*.py` remain after this
cycle, the plan-of-record retirement row enumerates them honestly
with cited reason (typically: still consumed by an in-flight partial
delivery not yet superseded by driver output).

## Anti-patterns (must not re-attempt)

- Hand-orchestrating song recreation (operator NEW ANTI-PATTERN
  2026-09-02): c22+ agents build/improve programs; songs run
  through the unified driver.
- VST3 `get_state`/`save_state`/`save_preset`/`load_state`/
  `set_state(bytes)` (c31 STILL_GAP + c35 A locked, AST-forbidden).
- Emitting `_infra/`/`_run/`/`_plan/`/`_archive/`/`_manager/` from
  clone contexts without `-clone-<k>` suffix (c32 convention —
  linear cycle so unsuffixed OK).
- Disabling TLS verification or unsetting HTTPS_PROXY.

## Success criteria (auditor-checkable)

Enumerated verbatim from operator brief:

1. `scripts/v3_spine/recreate_v3.py --song 88d247468cb6d49f
   --section operator` produces byte-identical delivery on 2 fresh runs.
2. `--reproduce-check` green on Chicken Grease (panel-equal always)
   and Rome (panel-equal always).
3. Every c22+ delivery `manifest.json` carries `env_pins` block with
   self-anchor `env_pin.sha256`.
4. Zero per-song `*_song_<sha16>.py` scripts remain under
   `scripts/v3_spine/` after retirement row lands, OR honest partial
   retirement row enumerates remainder with reason.
5. Peach Dream `data/v3/deliveries/88d247468cb6d49f/cycle22/verdict.json`
   ∈ {V3_FOCUS_SONG_LANDS_pending_operator, PARTIAL, FAILS} with
   three-way `rubric_hash_v2` chain
   (`c49db5a12e955f26c001165ad6e8f9d191bc26bfd96e24c1b163adc37016451a`)
   AND `rubric_hash_v3` chain (this doc SHA).
6. Zero AST-forbidden imports; zero VST3 state APIs; zero PRNG in
   pipeline modules.
7. c5 operator-blessed anchors byte-identical pre==post (61-anchor
   snapshot preserved).
8. `promise_check` 0-ERROR after `_plan/register-c22-*` row lands.
