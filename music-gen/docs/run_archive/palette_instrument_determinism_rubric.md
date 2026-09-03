---
created: 2026-08-29T02:00:00Z
cycle: 31
run_id: run-2026-08-28T040704Z
agent: worker
milestone: M-DAW-SPIKE-1/palette-instrument-determinism
---

# Palette instrument determinism — frozen 3-verdict rubric

**Milestone:** M-DAW-SPIKE-1/palette-instrument-determinism (new peer
sub-milestone under M-DAW-SPIKE-1).

**Committed:** 2026-08-29T02:00:00Z, cycle 31 branch A (clone 0 of fork
cfc5009aca96). This rubric is committed **before** any probe script
lands under `scripts/palette_probe/` (git-commit-order enforced by
`tests/test_palette_instrument_determinism.py::test_rubric_committed_before_probe_scripts`).
The SHA-256 of this file is recorded in `data/palette_probe/rubric_hash.txt`
and referenced in the verdict roll-up ledger event's narrative.

## §1 Purpose and scope

Probe each of the three palette instruments — Surge XT (VST3), Dexed
(VST3), sfizz (SFZ sampler) — for byte-deterministic audio rendering
under two independent invocations, with the pinned plugin state
serialized as a JSON sidecar. The verdict per instrument determines
palette eligibility for the cycle-32 palette-driven bare render.

This branch does not modify the cycle-3 DAW spike coverage matrix,
the cycle-9 DawDreamer effects chain
(`scripts/tex/render_effects_layered.py` — read-only anchor,
grep-verified zero import under `scripts/palette_probe/`), or the
cycle-13 batch-v2 pipeline.

## §2 Verdict definitions (frozen, verbatim)

- **GREEN** — byte-deterministic × 2 achieved. SHA-256 of both
  `render.wav` and `pinned_state.json` is equal across two independent
  runs into two fresh `tempfile.mkdtemp()` directories.

- **REDEFINED_GAP** — deterministic only after ONE documented pinning
  refinement. The initial probe was non-deterministic; a single
  refinement identified the specific drift source, pinned it, and the
  re-probe achieved byte-identity × 2. The refinement is documented
  with the concrete parameter or state that drifted, and the file
  `data/palette_probe/per_instrument/<inst>/refinement.json` records
  it.

- **STILL_GAP** — non-deterministic under any reasonable pinning
  (initial probe drifts, one refinement attempted, still drifts) OR
  the instrument is not fetchable or not loadable in the current
  workspace. Falsifiability escape hatch invoked — the instrument is
  declared ineligible for the palette. This is a legitimate first-class
  negative finding, not a defeat. Per cycle-11 M-TEX-1/panel/embedding
  discipline, honest STILL_GAP verdicts advance the palette design by
  informing cycle 32 which instruments are eligible.

## §3 Pinned-state JSON format (canonical, name-sorted keys)

```
{
  "plugin_name": <str>,                 // e.g. "Surge XT", "Dexed", "sfizz"
  "plugin_version": <str | null>,       // from VST3 metadata or SFZ header; null if unavailable
  "plugin_binary_sha256": <str>,        // SHA-256 of the loaded .vst3 bundle path or .sfz file
  "sample_rate": 44100,
  "block_size": <int>,                  // documented per instrument
  "stereo": true,
  "sample_count": 352800,               // 44100 * 8
  "midi_input_sha256": <str>,           // SHA-256 of the fixed 8s test-input MIDI file
  "parameter_dict": {                    // name-sorted for canonical JSON
    "<param_name>": <float | int | str>,
    ...
  },
  "preset_name": <str | null>,
  "external_state_sha256": <str | null>, // SHA of external preset bank / SFZ sample file
  "loader_pathway": <str>               // "dawdreamer_vst3" | "sfizz_render_cli" | "dawdreamer_sampler"
}
```

Serialize with `json.dumps(obj, sort_keys=True, indent=2,
separators=(",", ": "))` — this is the canonical form that
byte-determinism × 2 asserts against. The `loader_pathway` key is
required so future readers can reconstruct exactly which invocation
path produced the render.

If a plugin does not expose a version or preset name via its API,
use `null` (never fabricate). This honors the cycle-11 discipline of
documenting plugin-API limitations candidly.

## §4 Test-input MIDI spec

- Duration: 8.000 seconds (exact); render sample count = 44100 × 8 = 352,800.
- Sample rate: 44,100 Hz.
- Channels: 2 (stereo output; MIDI is monophonic input).
- MIDI channel: 1 (0-indexed 0).
- Velocity: 96 (constant).
- Content (melodic instruments — Surge XT, Dexed, sfizz on non-drum
  SFZ): ascending diatonic C4-major scale, one note per beat at 120 BPM
  (i.e., 0.5 s per note). Sixteen notes total: C4 D4 E4 F4 G4 A4 B4 C5
  D5 E5 F5 G5 A5 B5 C6 D6. Each note-on at t=0.5*i s, note-off at
  t=0.5*i + 0.45 s (short gap prevents legato tie). All note-offs
  strictly before t=8.0 s.
- For sfizz driven by a drum-mapped SFZ (case not expected in this
  cycle since `data/texture/test.sfz` is a sawtooth sampler): the same
  16-note sequence maps to GM drums (kick=36, snare=38, hi-hat=42,
  etc.) — documented in the instrument's pinned-state
  `preset_name` field.

The MIDI file is deterministically written to `<out_dir>/input.mid` by
`_shared.write_test_midi` (mido, no PRNG). Its SHA-256 is recorded in
every pinned-state JSON.

## §5 Determinism protocol

For each instrument:

1. Create two fresh directories via `tempfile.mkdtemp()`.
2. Invoke the probe with `--out-dir <dir>` twice, once per dir. Each
   invocation is a full `/usr/bin/python3` subprocess with the BLAS
   pins in the environment (`OMP_NUM_THREADS=1`, `MKL_NUM_THREADS=1`,
   `OPENBLAS_NUM_THREADS=1`).
3. Compute SHA-256 of each dir's `render.wav` and `pinned_state.json`.
4. Assert equality on both files across the two runs.

Verdict candidate:
- Equal on both → GREEN.
- Unequal on either → proceed to §6.

## §6 Pinning-refinement procedure (single-shot)

If run1 ≠ run2 on the initial probe:

1. Diff the two `pinned_state.json` files to see if any parameter
   drifted. If so, that parameter is the drift source — pin it to a
   documented value in the probe script.
2. If parameters match, diff the WAVs. Compute max-absolute-sample
   drift and drift location. Common suspects: uninitialized RNG
   (plugin internal), block-boundary state, sample-rate coercion,
   plugin-load ordering.
3. Apply ONE refinement (preset load, explicit `set_parameter`,
   `block_size` alignment, `torch.use_deterministic_algorithms(True)`,
   etc.). Document in
   `data/palette_probe/per_instrument/<inst>/refinement.json` with:
   `{"drift_source": <str>, "pinning_change": <str>,
   "wav_max_abs_drift_before": <float>, "state_drift_keys": [<str>]}`.
4. Re-probe × 2 with fresh temp dirs.
   - Equal → REDEFINED_GAP (record refined SHAs).
   - Still unequal → STILL_GAP (falsifiability escape hatch fires).

Only ONE refinement attempt is allowed by protocol. Second attempts
would erode the falsifiability guarantee.

## §7 Non-determinism sources checklist (drift-diagnosis)

Named up-front so the refinement is fast and the STILL_GAP verdict is
honest when hit:

1. Unseeded plugin-internal RNG (Surge XT mod-source phase, Dexed
   operator startup state) — pin via preset or parameter freeze.
2. Uninitialized parameter defaults that vary by plugin-load order —
   pin every parameter to a documented value up-front.
3. Sample-rate conversion nondeterminism — assert plugin sample rate
   matches DawDreamer's 44,100 Hz.
4. Block-size boundary effects — pin `block_size` and assert
   `render_length` is an exact multiple.
5. VST3 sidechain / aux-input state — leave disconnected explicitly.
6. Global thread-pool nondeterminism — BLAS pinned to 1 thread; if
   torch is transitively imported, `torch.manual_seed(0)` +
   `torch.use_deterministic_algorithms(True, warn_only=True)`.

## §8 Test-suite mapping

`tests/test_palette_instrument_determinism.py` enforces this rubric:

| Test                                              | Rubric section |
|---------------------------------------------------|----------------|
| `test_interpreter_guard_present_in_all_probe_scripts` | §5 (interpreter contract) |
| `test_no_prng_in_probe_code`                      | §7 (RNG suspect enumeration) |
| `test_pinned_state_json_schema_conformance`       | §3 |
| `test_run1_run2_sha_equal_per_instrument`         | §5 |
| `test_verdict_frozen_label`                       | §2 |
| `test_cycle9_chain_not_imported`                  | §1 (read-only anchor discipline) |
| `test_pinned_state_roundtrip`                     | §3 (canonical JSON) |
| `test_rubric_hash_matches_committed_doc`          | this doc's SHA |
| `test_rubric_committed_before_probe_scripts`      | pre-registration integrity |

`tests/test_integration_cross_branch.py §45` extends this with the
per-instrument determinism-verdict presence check across the
`data/palette_probe/instrument_determinism.tsv` rows.

END OF RUBRIC (frozen).
