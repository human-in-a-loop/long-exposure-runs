---
created: 2026-08-29T05:40:00Z
cycle: 33
run_id: run-2026-08-28T040704Z
agent: worker
milestone: M-DAW-SPIKE-1/dawdreamer-state-extraction-workaround
---

# DawDreamer state-extraction workaround — cycle 33 clone-1 report

**Milestone:** M-DAW-SPIKE-1/dawdreamer-state-extraction-workaround
(new peer sub-milestone under M-DAW-SPIKE-1; respects c29 state-machine
lemma).
**Fork:** 4595e91f7574 (clone-1).
**Rubric:** [`docs/dawdreamer_state_extraction_rubric.md`](./dawdreamer_state_extraction_rubric.md).
**Rubric SHA-256:** `611e0b768036d44862ca4ba495b2e1a08742cf890d8f5a6298b441634a69f27c`
(equal in `data/dawdreamer_state/rubric_hash.txt` and
`data/dawdreamer_state/verdict.json.rubric_hash` — chain integrity
green).

## §1 Setup and anchors

| Anchor                        | Value                                                                 |
|-------------------------------|-----------------------------------------------------------------------|
| Interpreter                   | `/usr/bin/python3` (guard-asserted in every probe script)             |
| DawDreamer version            | `0.9.0` (probed via `dawdreamer.__version__`)                         |
| Sample rate                   | 44,100 Hz                                                             |
| Duration                      | 8.000 s (352,800 samples)                                             |
| Channels                      | 2 (stereo)                                                            |
| Block size                    | 512 (DawDreamer default)                                              |
| Input MIDI                    | c31 Branch A ascending-diatonic 16-note (C4→D6), 0.5 s per beat @ 120 BPM, velocity 96 |
| Input MIDI SHA-256            | `a416bf8019eb5f4451f6676e07dc8401e45b2e30cab5740727fd2f6321067a93`    |
| Plugins probed                | Surge XT VST3 (`/usr/lib/vst3/Surge XT.vst3`), Dexed VST3 (`/usr/lib/vst3/Dexed.vst3`) |
| BLAS pins                     | `OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1`          |
| Cycle-9 effects chain import  | zero (AST-grep clean; enforced by `tests/test_dawdreamer_state_extraction.py::test 3` and `tests/test_integration_cross_branch.py §49e`) |
| PRNG                          | zero (AST-grep clean; test 2)                                         |
| Writes under c31 anchor dirs  | zero (write-verb + anchor-prefix scan; test 5)                        |

**Empirical API-surface substitutions (documented in rubric §3):**

- Rubric-brief's `plugin.get_num_parameters()` is not in the
  DawDreamer 0.9.0 API surface. Actual binding used:
  `plugin.get_plugin_parameter_size() → int`, verified against
  `plugin.get_plugin_parameters_description()` length (identical
  counts: 2855 for Surge XT, 2238 for Dexed).
- Rubric-brief's `plugin.save_preset(path)` is not in the DawDreamer
  0.9.0 API surface. Actual binding used:
  `plugin.save_state(filepath: str) → None` (docstring: "Save the state
  to a file"). The absence of `save_preset` is logged in
  `data/dawdreamer_state/fetchability_ladder.jsonl` with the
  `AttributeError`-equivalent and `[a for a in dir(plugin) if
  a.startswith('save_') or a.startswith('preset')]` slice
  (`['save_midi', 'save_state']`).

## §2 Rubric + rubric SHA embedding

Rubric-frozen definitions (verbatim, from `§2` of the rubric):

- **WORKAROUND_FOUND** — ≥1 probe path yields non-empty byte-identical
  × 2 state on BOTH Surge XT AND Dexed.
- **PARTIAL_WORKAROUND** — ≥1 probe path yields non-empty
  byte-identical × 2 state on exactly one plugin.
- **NO_WORKAROUND** — all three paths fail on both plugins.

The doc SHA above is embedded verbatim in
`data/dawdreamer_state/verdict.json.rubric_hash` and copied to
`data/dawdreamer_state/rubric_hash.txt`. Committed BEFORE any script
under `scripts/dawdreamer_state/` landed (file-mtime ordering enforced
by `tests/test_dawdreamer_state_extraction.py::test 10`).

## §3 P1 — iterate parameters (canonical-JSON per-plugin dict)

Implementation: `scripts/dawdreamer_state/probe_p1_iterate_parameters.py`.
Contract: for each plugin, in a fresh `tempfile.mkdtemp()` directory,
build `state = {f"{i:05d}:{name}": value}` for `i in
range(get_plugin_parameter_size())`, canonical-JSON-serialize with
`sort_keys=True, separators=(",", ":")`, write `p1_state_v2.json`, and
compute SHA-256 of the raw bytes.

| Plugin   | n_params | run1 SHA-256 (first 16)       | run2 SHA-256 (first 16)       | equal | empty |
|----------|----------|-------------------------------|-------------------------------|-------|-------|
| Surge XT | 2855     | `1e3c003f9ec5491b`            | `1e3c003f9ec5491b`            | ✓     | ✗     |
| Dexed    | 2238     | `85be24e14b1233d8`            | `85be24e14b1233d8`            | ✓     | ✗     |

Full SHA-256:
- Surge XT: `1e3c003f9ec5491bf7a3cc5701c80f2471c9173b542693dd208cec1db45fb80e`
- Dexed:    `85be24e14b1233d8d61858ce764729ad997a37eefac54140c8eef877042ee1d6`

**P1 verdict cell:** byte-deterministic × 2 non-empty on BOTH plugins.
P1 falsifies the null for both plugins independently.

## §4 P2 — save_preset (fell through to save_state)

Implementation: `scripts/dawdreamer_state/probe_p2_save_preset.py`.
`save_preset` is absent from DawDreamer 0.9.0 (documented in
fetchability ladder); the probe falls through to
`plugin.save_state(filepath)` and hex-serializes the resulting raw
bytes.

| Plugin   | bytes (run1) | bytes (run2) | run1 SHA-256 (first 16) | run2 SHA-256 (first 16) | equal | empty |
|----------|--------------|--------------|-------------------------|-------------------------|-------|-------|
| Surge XT | 67,236       | 67,236       | `9b35b856cb94af69`      | `9b35b856cb94af69`      | ✓     | ✗     |
| Dexed    | 8,343        | 8,340        | `1fcb9f23e155e435`      | `d199a8497518a21f`      | ✗     | ✗     |

Full SHA-256 (Surge XT):
`9b35b856cb94af695a274034d6f06bd9454e52ca765627dffbf0200d67c19394`.

**P2 verdict cell:** byte-deterministic × 2 non-empty on Surge XT
only. Dexed's `save_state` output not only fails SHA equality — the
byte length itself differs (8,343 vs 8,340), which localizes the
non-determinism inside Dexed's own state serializer (likely a random
per-load session UUID or timestamp field). This is a plugin-internal
issue, not a DawDreamer bug; documented in the fetchability ladder.

## §5 P3 — metadata inspection + method-surface discovery

Implementation: `scripts/dawdreamer_state/probe_p3_metadata_inspection.py`.
Records `plugin.get_plugin_parameters_description()` (list-of-dicts,
one per parameter, keys sorted for canonical JSON) plus a
`discovered_methods` block for the seven candidate state-extraction
bindings named in the rubric brief: `get_state_information`,
`getStateInformation`, `save_state`, `get_state_chunk`, `getChunk`,
`writeStateInformation`, `get_patch`.

Discovered methods (both plugins):

| Method                    | Present |
|---------------------------|---------|
| `get_state_information`   | ✗       |
| `getStateInformation`     | ✗       |
| `save_state`              | ✓ (docstring: "Save the state to a file") |
| `get_state_chunk`         | ✗       |
| `getChunk`                | ✗       |
| `writeStateInformation`   | ✗       |
| `get_patch`               | ✓ (returns 2855-tuple on Surge XT, 2238-tuple on Dexed) |

Determinism (metadata + discovered_methods JSON, sha256):

| Plugin   | run1 SHA-256 (first 16) | run2 SHA-256 (first 16) | equal | empty |
|----------|-------------------------|-------------------------|-------|-------|
| Surge XT | `2a8d08913deda121`      | `2a8d08913deda121`      | ✓     | ✗     |
| Dexed    | `f30035ea58a3793e`      | `f30035ea58a3793e`      | ✓     | ✗     |

Full SHA-256:
- Surge XT: `2a8d08913deda121e34ebd453ba3e8e1fae652ede475989bbcedab59ad672c97`
- Dexed:    `f30035ea58a3793e1823dc765031ef48189a71485d971d895d17b6b9e52b602d`

**P3 verdict cell:** byte-deterministic × 2 non-empty on BOTH plugins
after one documented deviation from the brief's contract: the probe
does NOT record `repr(bound_method)` under `discovered_methods` because
CPython embeds the object's memory address in the repr, which drifts
per plugin-instance. The deviation is documented inline in the probe
source (`probe_p3_metadata_inspection.py::_describe_discovered`) and
records only `doc_head` + `patch_len` under each discovered method —
both content-derived and byte-stable across fresh instances.

## §6 Verdict per rubric + rationale

**Verdict: `WORKAROUND_FOUND`** (winning_path `P1`).

Rubric §2's decision procedure (implemented in
`scripts/dawdreamer_state/run_all.py::decide`): a probe path
"succeeds" for a plugin iff its `state_sha` is byte-equal across the
two independent runs AND the payload is non-empty; a WORKAROUND_FOUND
verdict fires as soon as any one probe path succeeds on BOTH Surge XT
AND Dexed. Two paths satisfy this condition independently: P1 (2/2)
and P3 (2/2). P1 wins by canonical P1→P2→P3 order.

Per-path summary:

| Path | surge_xt | dexed  | verdict cell            |
|------|----------|--------|-------------------------|
| P1   | ✓✓       | ✓✓     | both determ. non-empty  |
| P2   | ✓✓       | ✗ (bytes differ + size differs) | one plugin only |
| P3   | ✓✓       | ✓✓     | both determ. non-empty  |

## §7 Interpretation

**Falsification target** (rubric §Investigation contract): "no
DawDreamer 0.9.0 API path yields a byte-deterministic non-empty state
extract for Surge XT + Dexed VST3 in this workspace." **REFUTED** —
two orthogonal paths (P1 iterate_parameters and P3 metadata
inspection) each independently produce byte-deterministic non-empty
state extracts on BOTH plugins in fresh `tempfile.mkdtemp()`
directories.

**Root-cause interpretation of the c31 Branch A STILL_GAP verdict:**
the "0-byte return from `PluginProcessor.get_state()`" reported at
c31 was not a DawDreamer or plugin defect. `get_state()` is not a
member of the DawDreamer 0.9.0 `PluginProcessor` binding surface (see
`dir(plugin)` slice at
`scripts/palette_probe/surge_xt.py:54-58` — the call was wrapped in a
bare `try/except Exception` that captured the resulting
`AttributeError` and produced `None`, which was reported downstream as
"0 bytes". The actual state-write binding is
`save_state(filepath: str) → None` (P2 above), and per-parameter
enumeration is available through `get_parameter(i)` /
`get_parameter_name(i)` for `i in range(get_plugin_parameter_size())`
(P1 above). This is exactly the API surface c31 needed; the
STILL_GAP verdict is therefore best redefined as a probe-code defect,
not an API-surface gap.

**`pinned_state_v2` candidate:** the P1 canonical-JSON dict
serialization (name-keyed under `f"{i:05d}:{name}"`, values numeric)
is the winning-path artifact. Per-plugin snapshots live at
`data/dawdreamer_state/per_plugin/<plugin>/p1_state_v2.json`. This
serialization is the **candidate schema-v2** for a future cycle to
formalize under a new peer sub-milestone
`M-DAW-SPIKE-1/palette-schema-v2` (name TBD). Per the rubric's
non-scope contract and explicit prohibitions §, the frozen c31
`palette_v1.json` is **not edited** this cycle; `pinned_state_v2` is
documented as a candidate only.

**Why P1 wins over P3 (which also passes):** P1 carries the actual
runtime parameter values, which is what an eventual palette-v2
render-time dispatcher needs to seed a plugin instance
deterministically. P3 carries parameter metadata (ranges, defaults,
labels) — necessary for validation but not sufficient for state
reconstruction. P1 is therefore the semantically correct schema-v2
seed.

**Why the P2 verdict cell is asymmetric:** Surge XT's `save_state`
serializer is content-deterministic; Dexed's is not — the fresh-run
byte-length differs (8,343 vs 8,340 bytes at first-instance), which
points to a per-session UUID / timestamp in Dexed's own state format.
This is a plugin-internal issue that ONLY becomes relevant if a
future cycle chooses P2's raw-preset serialization for palette-v2. P1
sidesteps the issue by extracting only the parameter values.

**Anti-pattern discipline:** c11 CLAP fetchability, c22/c23/c25
M-EAR-1 chassis audits, and c8 octave-suppression were not
re-attempted (they are unrelated to state extraction). VGGish R3 was
not attempted per operator directive.

## §8 Handoff to cycle 34

**Proposed next-cycle sub-milestones (peer under M-DAW-SPIKE-1,
respecting c29 state-machine lemma):**

1. `M-DAW-SPIKE-1/palette-schema-v2` — formalize `pinned_state_v2`
   as a schema-v2 update to the c31 palette, including validator +
   round-trip round + test suite. Consumes P1's per-plugin
   `p1_state_v2.json` verbatim as the canonical seed format.
2. `M-DAW-SPIKE-1/dexed-save-state-drift` (optional) — characterize
   the 3-byte length drift in Dexed's `save_state` output and localize
   the drift field. Not blocking palette-schema-v2 (which uses P1),
   but useful if a future cycle wants to preserve DX7 patch bank
   fidelity beyond parameter values (envelope release curves, LFO
   phases, etc.).
3. `M-DAW-SPIKE-1/sfizz-state-extraction` — extend the same three-
   probe framework to sfizz once the sfizz DawDreamer sampler pathway
   is available; sfizz is in the c31 palette but outside this cycle's
   scope (Surge XT + Dexed only were named in the assignment).

**Linkage back to c31 Branch A STILL_GAP verdicts:** the c31
`M-DAW-SPIKE-1/palette-instrument-determinism` ledger event's
per-instrument `STILL_GAP` labels for Surge XT + Dexed remain
terminal-validated per c29 state-machine lemma (a validated
milestone's verdict cannot be edited); the redefined-STILL_GAP
interpretation lives in this cycle's peer sub-milestone
verdict rather than mutating c31.

**Cross-branch integration:** `tests/test_integration_cross_branch.py
§49` covers eight state-extraction invariants (package presence,
rubric SHA chain integrity, verdict enum + schema conformance,
per-plugin data-file presence, cycle-9 chain non-import [AST],
sidecar_nonfactor non-import, pinned_state_v2 candidacy note
presence, c31 anchor preservation). All eight pass at cycle close.

---

**Artifacts** (also enumerated in the verdict roll-up ledger event's
`artifacts` field):

- `docs/dawdreamer_state_extraction_rubric.md` (this cycle's frozen rubric)
- `docs/dawdreamer_state_extraction_workaround_report.md` (this report)
- `scripts/dawdreamer_state/{__init__.py, _shared.py,
  probe_p1_iterate_parameters.py, probe_p2_save_preset.py,
  probe_p3_metadata_inspection.py, run_all.py}`
- `data/dawdreamer_state/{rubric_hash.txt, verdict.json,
  fetchability_ladder.jsonl}`
- `data/dawdreamer_state/per_plugin/{surge_xt,dexed}/{p1_state_v2.json,
  p1_state_sha, p2_preset_hex, p2_state_sha, p3_metadata.json,
  p3_state_sha}` (6 files × 2 plugins = 12)
- `tests/test_dawdreamer_state_extraction.py` (≥12 cases, all green)
- `tests/test_integration_cross_branch.py §49` (8 checks, all green)

END OF REPORT.
