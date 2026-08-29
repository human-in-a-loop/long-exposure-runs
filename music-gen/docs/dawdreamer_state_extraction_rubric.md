---
created: 2026-08-29T05:00:00Z
cycle: 33
run_id: run-2026-08-28T040704Z
agent: worker
milestone: M-DAW-SPIKE-1/dawdreamer-state-extraction-workaround
---

# DawDreamer state-extraction workaround — frozen 3-verdict rubric

**Milestone:** M-DAW-SPIKE-1/dawdreamer-state-extraction-workaround
(new peer sub-milestone under M-DAW-SPIKE-1 — respects c29 state-machine
lemma; NOT a child of terminal-validated
`M-DAW-SPIKE-1/palette-instrument-determinism`).

**Committed:** 2026-08-29T05:00:00Z, cycle 33 branch B (clone 1 of fork
4595e91f7574). This rubric is committed **before** any probe script
lands under `scripts/dawdreamer_state/`
(git/mtime-order enforced by
`tests/test_dawdreamer_state_extraction.py::test_rubric_committed_before_probe_scripts`).
The SHA-256 of this file is recorded in
`data/dawdreamer_state/rubric_hash.txt` and embedded verbatim in the
`M-DAW-SPIKE-1/dawdreamer-state-extraction-workaround` verdict roll-up
ledger event's `narrative`, and inside
`data/dawdreamer_state/verdict.json` under key `rubric_hash`.

## §1 Purpose and scope

Characterize the c31 Branch A STILL_GAP finding that Surge XT + Dexed
VST3 plugins produce "0-byte return" from a DawDreamer 0.9.0 state
extraction call. Probe three orthogonal state-extraction API paths on
both plugins in isolated `tempfile.mkdtemp()` directories and decide
whether a byte-deterministic non-empty state extract is achievable
through any of them.

**Read-only anchors** (grep-verified by test suite):
`scripts/palette/*` (c31 Branch B palette assignment schema),
`scripts/palette_probe/*` (c31 Branch A palette instrument determinism),
`scripts/tex/render_effects_layered.py` (cycle-9 effects chain),
`data/palette/*`, `data/palette_probe/*`,
`scripts/gen/*`, `scripts/ear/*`,
`data/rules/ledger.jsonl`, `data/rules/ledger_i3_dminor.jsonl`.
Zero writes under those paths. This branch is analytical + probe-only;
no rendering pipeline changes; the frozen c31 `palette_v1` schema is
NOT edited.

## §2 Verdict definitions (frozen, verbatim)

- **WORKAROUND_FOUND** — ≥1 probe path (P1, P2, or P3) yields a
  non-empty state extract that is byte-identical × 2 (SHA-256 equal on
  canonical-JSON or raw-bytes serialization) on BOTH Surge XT AND
  Dexed. The winning path (or, if multiple paths pass, the earliest
  one in the P1→P2→P3 order) is documented as the `pinned_state_v2`
  candidate; a future cycle will open a peer sub-milestone under
  M-DAW-SPIKE-1 to author `palette_v2` incorporating it. Cycle 31's
  frozen `palette_v1.json` is NOT edited this cycle.

- **PARTIAL_WORKAROUND** — ≥1 probe path yields a non-empty
  byte-deterministic-×2 state on exactly one plugin (Surge XT XOR
  Dexed). Documents which plugin still lacks a workaround; the
  asymmetric verdict names both.

- **NO_WORKAROUND** — All three paths fail on both plugins (either
  yield empty/zero-byte state OR are not byte-deterministic × 2).
  Codifies the STILL_GAP as a redefined-GAP with a durable formal
  claim: **Surge XT + Dexed remain palette-schema-eligible in
  `palette_v1` because the schema's `pinned_state_optional` field
  accepts `{}` as a valid v1 record; the render dispatcher at cycle 33
  Branch A (sibling) handles empty `pinned_state` via the same
  `null-state skip reason` path as any other non-fatal integrity
  note.** No PARTIAL variants inside NO_WORKAROUND — either something
  byte-deterministic non-empty is extracted, or it isn't.

## §3 Probe contracts

Each probe runs twice into fresh `tempfile.mkdtemp()` directories on
both plugins with the SAME input MIDI (c31 Branch A ascending-diatonic
8 s @ 44.1 kHz stereo — the exact
`scripts/palette_probe/_shared.write_test_midi` MIDI, referenced by
its SHA-256 in `scripts/dawdreamer_state/_shared.py`). Each probe
writes a `<probe>_state_sha` sidecar (`p1_state_sha`, `p2_state_sha`,
`p3_state_sha`) alongside its main output.

- **P1 — iterate_parameters**
  (`scripts/dawdreamer_state/probe_p1_iterate_parameters.py`):
  `n = plugin.get_plugin_parameter_size()` — the DawDreamer 0.9.0
  binding for parameter count; the rubric-brief's
  `plugin.get_num_parameters()` name is not in the DawDreamer 0.9.0
  API surface (verified by `dir(plugin)` scan on
  `Surge XT.vst3` / `Dexed.vst3`), so the probe uses the
  actual-API alias — a documented, expected-behavior name substitution
  that does not weaken the probe contract. Then
  `state = {plugin.get_parameter_name(i): plugin.get_parameter(i) for
  i in range(n)}` → canonical JSON with sorted keys + fixed float
  formatting (`json.dumps(..., sort_keys=True, separators=(",", ":"))`).
  Assert SHA-256 equality on `p1_state_v2.json` bytes across two runs.

- **P2 — save_preset / save_state**
  (`scripts/dawdreamer_state/probe_p2_save_preset.py`):
  The rubric-brief's `plugin.save_preset(path)` name is not in the
  DawDreamer 0.9.0 API surface either; the actual binding is
  `save_state(filepath: str) -> None` (documented via `save_state.__doc__`,
  "Save the state to a file"). The probe first checks for either
  `save_preset` or `save_state`; if `save_preset` is absent (expected),
  it logs the AttributeError-equivalent to `fetchability_ladder.jsonl`
  and falls through to `save_state`. Read the resulting file bytes →
  hex-serialize into `p2_preset_hex`. Assert SHA-256 equality on
  `p2_preset_hex` across two runs.

- **P3 — metadata_inspection**
  (`scripts/dawdreamer_state/probe_p3_metadata_inspection.py`):
  Call `plugin.get_plugin_parameters_description()` if it exists →
  `p3_metadata.json`. Also probe the exposed API for
  `get_state_information`, `getStateInformation`, `save_state`,
  `get_state_chunk`, `getChunk`, `writeStateInformation` — any binding
  found gets recorded under `discovered_methods` inside
  `p3_metadata.json`. `save_state` will fire since it exists in
  DawDreamer 0.9.0 (see P2). Assert SHA-256 equality on
  `p3_metadata.json` across two runs.

Each probe module MUST expose `if __name__ == "__main__": main()`
and MUST be callable in isolation
(`python3 -c "from scripts.dawdreamer_state.probe_p1_iterate_parameters import main; main()"`).

## §4 Rendering pipeline invariants

- Sample rate: 44,100 Hz.
- Duration: 8.000 s (352,800 samples).
- Stereo output.
- Block size: 512 (DawDreamer default).
- MIDI input: exact c31 Branch A ascending-diatonic sequence
  (16 notes: C4 D4 E4 F4 G4 A4 B4 C5 D5 E5 F5 G5 A5 B5 C6 D6, 0.5 s
  per beat @ 120 BPM, 0.45 s note-on / 0.05 s gap, velocity 96).
- No PRNG.
- SHA-256 only (no MD5, no PRNG-derived salting).
- BLAS pins: `OMP_NUM_THREADS=1`, `MKL_NUM_THREADS=1`,
  `OPENBLAS_NUM_THREADS=1` set at `_shared` import time before any
  numeric library import.
- Interpreter guard `assert sys.executable == '/usr/bin/python3'`
  at the top of every script under `scripts/dawdreamer_state/`.
- Zero import of `scripts.tex.render_effects_layered`
  (grep-verified — test enforces).
- Zero import of `scripts.classifier.sidecar_nonfactor`
  (grep-verified — test enforces).
- Zero write under `scripts/palette/`, `scripts/palette_probe/`,
  `scripts/tex/`, `scripts/ear/`, `scripts/gen/`
  (grep-verified — test enforces).

## §5 Verdict JSON schema

`data/dawdreamer_state/verdict.json` MUST contain:

```
{
  "rubric_hash": "<sha256 of this file>",
  "verdict": "WORKAROUND_FOUND" | "PARTIAL_WORKAROUND" | "NO_WORKAROUND",
  "winning_path": "P1" | "P2" | "P3" | null,
  "per_plugin": {
    "surge_xt": {
      "P1": {"sha_run1": "...", "sha_run2": "...", "equal": true|false, "empty": bool},
      "P2": {...},
      "P3": {...}
    },
    "dexed": { ... }
  },
  "per_path": {
    "P1": {"both_deterministic_nonempty": bool},
    "P2": {"both_deterministic_nonempty": bool},
    "P3": {"both_deterministic_nonempty": bool}
  },
  "midi_input_sha256": "<sha256 of the fixed input MIDI>",
  "committed_at": "2026-08-29T05:00:00Z"
}
```

## §6 Test-suite mapping

`tests/test_dawdreamer_state_extraction.py` enforces this rubric with
at least 12 cases:

| Test                                                     | Rubric section |
|----------------------------------------------------------|----------------|
| `test_interpreter_guard_present_in_all_probe_scripts`    | §4 |
| `test_no_prng_in_probe_code`                             | §4 |
| `test_no_import_of_cycle9_effects_chain`                 | §4 |
| `test_no_import_of_sidecar_nonfactor`                    | §4 |
| `test_no_writes_under_c31_palette_anchor_dirs`           | §4 |
| `test_p1_byte_determinism_surge_xt`                      | §3 (P1) |
| `test_p1_byte_determinism_dexed`                         | §3 (P1) |
| `test_p2_byte_determinism_or_fetchability_documented`    | §3 (P2) |
| `test_p3_byte_determinism_surge_xt_and_dexed`            | §3 (P3) |
| `test_rubric_committed_before_probe_scripts`             | pre-registration integrity |
| `test_verdict_json_schema_conformance`                   | §5 |
| `test_three_probes_callable_in_isolation`                | §3 |

`tests/test_integration_cross_branch.py §49` extends this with
state-extraction invariants: rubric SHA chain integrity
(doc ↔ `rubric_hash.txt` ↔ `verdict.json.rubric_hash`),
no-import-of-c31-palette-anchors under `scripts/dawdreamer_state/`,
verdict JSON present and schema-conformant, `pinned_state_v2`
candidacy note present in
`docs/dawdreamer_state_extraction_workaround_report.md`
when the verdict is `WORKAROUND_FOUND`.

END OF RUBRIC (frozen).
