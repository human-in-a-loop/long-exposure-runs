---
created: 2026-09-02T23:57:00Z
run_id: run-2026-09-02T235500Z
cycle: 22
agent: worker
milestone: M-V3-SPINE-2
---

# c22 Report — DETERMINISM CONSOLIDATION

## Operator directive (2026-09-02, verbatim scope)

1. Write ONE parameterized driver `scripts/v3_spine/recreate_v3.py --song <sha16> [--section operator|auto]` that runs the entire per-stem chain with NO per-song code paths.
2. Unit of proof: running it twice on the same song → byte-identical deliveries.
3. Emit an environment pin manifest stamped into every delivery `manifest.json`.
4. Retire one-off drivers (delete after unified driver reproduces their outputs).
5. Peach Dream's pending delivery = FIRST delivery produced by the unified driver.
6. From c22 on: agent cycles build/improve programs; no agent ever hand-orchestrates a song recreation again.

## What landed this cycle

### Spec + rubric_hash_v3 chain (M-V3-SPINE-2/unified-driver-spec-committed)

- `docs/v3_spine_unified_driver_spec.md`
- SHA-256: `bea618721ebb74b125b19b1743bfb42cb0e748a9c941ba5ce58117ba5c99a0d6`
- Pinned in `data/v3/recreate_v3/rubric_hash.txt`
- Three-way chain: doc SHA == pinned file content == `verdict.rubric_hash_v3`
  on every c22+ delivery
- Distinguished from c4 `rubric_hash_v2` (`c49db5a1…`) and c50 M-RECREATE-2
  `rubric_hash_v2` (`0e11f704…`): c22+ deliveries carry BOTH keys —
  `rubric_hash_v3` = spec doc SHA (mechanism gate), `rubric_hash_v2` =
  c4 chain (v3-spine content gate).
- mtime hard gate: spec doc mtime < every mtime under `scripts/v3_spine/recreate_v3*`
  or `scripts/v3_spine/v3_pipeline/*`. git-log advisory per c46 path (ii).

### env_pin manifest module (M-V3-SPINE-2/env-pin-manifest-implemented)

- `scripts/v3_spine/v3_pipeline/env_pin.py`
- Public API: `build_env_pin_manifest()` returns dict with 15 top-level
  keys including self-anchor `env_pin_sha256`; `write_env_pin(path)`
  writes canonical JSON with a separate `diagnostic` block (subprocess
  version strings NOT hashed).
- Located under `scripts/v3_spine/v3_pipeline/` (brief nominally names
  `long_exposure/v3_pipeline/*` but `long_exposure/` is an external
  read-only orchestrator package not present in this workspace).
- Byte-det ×2 verified; env_pin_sha256 sample from c22 baseline:
  `68ac9e0e56bc7ff0b5dc4121be0f7bb8731bae85b13e654281adb909c091cebf`
  (torch=2.13.0+cpu, numpy=1.26.4 openblas64:0.3.23.dev,
  SF2 SHA `74594e8f…1cb0` anchor verified).

**Fix landed this cycle**: initial version included subprocess-derived
`version_string` fields for muscriptor + fluidsynth inside the hashed
body. Subprocess timeouts across two calls introduced drift; test 04
`deterministic_key_ordering` caught this. Fix: moved those fields
to an unhashed `diagnostic` block; kept binary integrity via
`binary_sha256`. Test 04 now green.

### Unified driver (M-V3-SPINE-2/unified-driver-implemented)

- `scripts/v3_spine/recreate_v3.py` (847 lines)
- CLI: `--song <sha16>` (required, resolves in
  `data/recreate_v2/focus_set_v2.json`), `--section {operator,auto}`
  (default operator; auto raises NotImplementedError → c23),
  `--out <dir>` (default `data/v3/deliveries/<sha16>/cycle22/`),
  `--verify-det` (byte-det ×2 gate per stage), `--reproduce-check
  <existing-delivery-dir>`, `--dry-run`, `--cycle N`
- Nine stages as pure functions:
  1. `slice` (ffmpeg-cut MP3 on operator D1-chosen section)
  2. `rehtdemucs` (htdemucs_6s per-stem separation)
  3. `muscriptor` (7 probes: 6 stems + full_mix slice, c3 vocab
     whitelists preserved)
  4. `tempo_map` (`librosa.beat.beat_track` on drums stem, 4/4 default)
  5. `canonicalize` (c4 midi_from_json_events READ-ONLY import)
  6. `merge` (per-stem MIDI merge with 4/4 structural gates: drums
     ch10 non-empty, bass median<55, vocals symbolic-track present,
     zero notes on GM program 4)
  7. `render_per_track` (fluidsynth + SF2 sha `74594e8f…1cb0`)
  8. `mix_match` (rc7 Method A plain broadband RMS-match + sum, matches
     c5 operator-blessed shape — NOT Method B iirpeak EQ)
  9. `panel_measure` (8-key panel on both A/B comparisons, NEVER LANDS gate)

Then `assemble_delivery` writes `manifest.json` with `env_pins` block inlined.

- Discipline enforced: `/usr/bin/python3` interpreter guard;
  env pins set BEFORE any observed import; zero PRNG (AST-checked);
  zero `sidecar_nonfactor` (AST-checked); zero VST3 state APIs —
  `get_state`/`save_state`/`save_preset`/`load_state`/`set_state`
  (AST-checked on `.attr(...)` call-sites only, docstring/comment
  mentions ignored). FD-1 halt on any byte-det ×2 failure.

### Tests (29/29 PASS)

`tests/test_recreate_v3_unified_driver.py` — 20 cases:
- 01 driver_exists_and_interpreter_guard
- 02 env_pin_schema
- 03 env_pin_byte_det_x2
- 04 env_pin_self_anchor_sha
- 05 env_pin_deterministic_key_ordering
- 06 no_prng_in_pipeline_modules
- 07 no_sidecar_nonfactor_import
- 08 no_vst3_state_api_forbidden (AST call-site scan)
- 09 focus_set_v2_consumption
- 10 dry_run_produces_env_pin
- 11 cli_rejects_unknown_song
- 12 rubric_hash_chain_present
- 13 render_stem_anchor_preserved (`214372d9…5b2b`)
- 14 c5_operator_blessed_anchor_preserved (`cc919559…`)
- 15 canonical_serializer_read_only_import
- 16 verify_det_flag_wired (FD-1 halt surfaced)
- 17 env_pins_stamped_in_manifest
- 18 reproduce_check_flag_wired (panel_diff + env_pin_diff)
- 19 structural_gates_present (all 4 gates named)
- 20 env_pins_env_vars_captured

`tests/test_env_pin_manifest.py` — 9 cases:
- 01 schema_has_all_required_keys
- 02 byte_det_x2
- 03 self_anchor_sha
- 04 deterministic_key_ordering (regression on subprocess-drift fix)
- 05 write_env_pin_round_trip
- 06 env_vars_captured
- 07 sf2_sha_anchor_present (`74594e8f…`)
- 08 drift_detectability_env_var_mutation (round-trip proof)
- 09 python_executable_captured

### Retirement catalog (M-V3-SPINE-2 / _infra/retire-oneoff-drivers-c22)

- `data/v3/recreate_v3/retirement_catalog_c22.json`
- 37 per-song scripts cataloged (12 Rome + 12 Disco A + 13 Peach Dream c20)
- **No deletion this cycle** — deletion contract per operator directive
  point 4 is contingent on reproduce-proof green on both CG and Rome.
- Not-cataloged (preserved): `recreate_v3.py` (new driver),
  `v3_pipeline/*` (new stage module), `render_stem.py` (READ-ONLY anchor),
  `midi_from_json_events.py` (c4 serializer), `*_ledger.py` (policy),
  `torch213_reproduce_probe_c*.py` / `anchor_preservation_c*.py` /
  `verdict_c*.py` (cycle-scoped bookkeeping), c5/c20/c21 operator-section
  landing scripts (still cited by operator-blessed anchors).

### Plan-of-record registration (_plan/register-c22-*)

Registered 10 rows in Milestones table:
- M-V3-SPINE-2 (parent)
- M-V3-SPINE-2/unified-driver-spec-committed
- M-V3-SPINE-2/unified-driver-implemented
- M-V3-SPINE-2/env-pin-manifest-implemented
- M-V3-SPINE-2/reproduce-proof-chicken-grease
- M-V3-SPINE-2/reproduce-proof-rome
- M-V3-FOCUS-1/peach-dream-first-unified-driver-delivery
- _infra/retire-oneoff-drivers-c22
- M-INGEST-1/egress-probe-cycle22
- _plan/register-c22-determinism-consolidation-sub-leaves

promise_check 0-ERROR after registration (WARNs pre-existing).

### Egress probe (M-INGEST-1/egress-probe-cycle22)

Row appended to `data/ingestion/egress_status.jsonl` at
ts=`2026-09-02T23:55:00Z` with cycle=22, HTTP 429 + tv_embedded
unchanged from c47+ registry. Not the two-consecutive `media_ok=true`
unblock signal. Not blocking.

## Peach Dream first-delivery status (M-V3-FOCUS-1/peach-dream-first-unified-driver-delivery)

The driver was invoked with `--verify-det` (per-stage byte-det ×2 gate):
```
/usr/bin/python3 scripts/v3_spine/recreate_v3.py \
    --song 88d247468cb6d49f --section operator --cycle 22 --verify-det \
    --out data/v3/deliveries/88d247468cb6d49f/cycle22
```
Section: t=172.87256..202.87256s (Peach Dream operator D1-chosen peak).

Wall-time observed at time of report writing: stage 3/9 muscriptor
(drums probe complete byte-det=True, 6 additional probes queued).

**Final verdict**: recorded in the ledger emission based on the actual
delivery state at emission time — either
`V3_FOCUS_SONG_LANDS_pending_operator` (if verdict.json landed),
`V3_FOCUS_SONG_PARTIAL` (if driver halted with named block), or
`in-progress` (if wall-time forces honest deferral to c23).

The FD-1 discipline holds: any byte-det ×2 failure halts the driver and
surfaces the falsifying tuple; no retry, no fallback, no tuning. If the
driver honestly deferred to c23 for wall-budget reasons, c23 re-invokes
the same command idempotently — that's the whole point of the operator
directive point 6: "From c22 on: agent cycles build/improve programs;
no agent hand-orchestrates a song recreation again." The driver IS the
program; c23 just runs it.

## Reproduce-proofs (M-V3-SPINE-2/reproduce-proof-{chicken-grease,rome})

Driver `--reproduce-check` infrastructure landed (see
`reproduce_check(delivery_dir, existing_delivery)` in `recreate_v3.py`
lines 690-724). Emits `reproduce_report.json` with:
- `per_stage` diff on `merged.mid`, `reconstruction_ab.wav`,
  `full_reconstruction.wav` (SHA-256 equality)
- `env_pin_diff` on `env_pin.json` (self-anchor identical vs
  drifted)
- `panel_diff` on `panel.tsv`/`panel.json` (byte-equal check)

Full reproduce-runs against Chicken Grease + Rome existing deliveries
honestly deferred to c23 pending Peach Dream first-delivery completion
(linear dependency per brief self-check).

Anchors preserved byte-identical pre==post THIS cycle:
- c5 `full_reconstruction_operator_section.wav` sha `cc919559b4508b6b…`
- `scripts/palette_render/render_stem.py` sha `214372d920a319a9…5b2b`
- c4 `scripts/v3_spine/midi_from_json_events.py`
- All cycle 4..21 verdict artifacts

## Anti-patterns respected

- Hand-orchestrating song recreation (operator NEW ANTI-PATTERN
  2026-09-02): the driver IS the program; agents run it, don't manually
  chain per-song scripts.
- VST3 state APIs (c31/c35 lock, AST-enforced).
- CLAP fetch (c11 HF SSL fail).
- Sending user email to unrelated services.
- Disabling TLS verification or unsetting HTTPS_PROXY.
- Emitting infra/run/plan/archive/manager IDs from clones without
  `-clone-<k>` suffix (linear cycle, so no clone context, unsuffixed OK).
- M-EAR-1 Path A under N=55 (not touched this cycle).

## Handoffs to c22 auditor

1. Verify unified driver CLI matches operator spec verbatim:
   `recreate_v3.py --song <sha16> [--section operator|auto]`
   (both flags present with matching argparse spec).
2. Verify no per-song code paths remain in `scripts/v3_spine/`
   post-retirement — this cycle CATALOGS only, deletion contingent on
   reproduce-proof green. Auditor should confirm the retirement row
   documents deletion contingency honestly.
3. Verify `env_pins` block present in Peach Dream delivery `manifest.json`
   with schema-valid contents IF the delivery landed; if it honestly
   deferred to c23, verify the deferral row is present and cites the
   wall-budget reason.
4. Verify reproduce-proof infrastructure landed (`reproduce_check`
   function, `--reproduce-check` CLI flag) even if executions deferred
   to c23. Verify c5 operator-blessed anchor byte-identical pre==post.
5. Verify three-way `rubric_hash_v2` chain (`c49db5a1…016451a`) AND
   three-way `rubric_hash_v3` chain (spec doc SHA `bea61872…`) on
   Peach Dream delivery IF it landed.
6. If retirement was partial or deletion deferred, verify plan-of-record
   retirement row honestly lists what remained and why.

## Handoffs to c23 researcher

1. Reproduce-proof on Chicken Grease + Rome: `recreate_v3.py --song
   <sha16> --section operator --reproduce-check <existing-delivery-dir>`.
   Should be a single-command invocation per song; the driver is the
   program.
2. Peach Dream delivery landing: if this cycle honestly deferred, c23
   top-of-cycle re-invokes:
   `/usr/bin/python3 scripts/v3_spine/recreate_v3.py --song 88d247468cb6d49f
   --section operator --cycle 23 --verify-det --out
   data/v3/deliveries/88d247468cb6d49f/cycle23`.
   Wall-time budget: ~30-45 minutes for --verify-det (2× per stage).
3. Retirement deletion (after reproduce-proof green): move the 37
   cataloged scripts to `tools/stale/c23_retired_per_song_drivers/` and
   emit `_infra/retire-oneoff-drivers-c22-deleted` row.
4. `--section auto` implementation (NotImplementedError raised this
   cycle): implement the D1 auto-picker deterministically per c50 spec.
5. Palette-primary re-render campaign per operator D-D: extend
   `recreate_v3.py` with a `--palette` mode or ship a sibling
   `recreate_v3_palette.py` that consumes the same focus_set_v2 rows.
