---
created: 2026-08-29T06:30:00Z
cycle: 35
run_id: run-2026-08-28T040704Z
agent: worker
milestone: M-GEN-1/palette-driven-batch-v2-sampler-diversified
---

# M-GEN-1/palette-driven-batch-v2-sampler-diversified — Report

**Cycle 35, Branch B (clone-1, fork 07063458736e).**
Sampler-side diversification response to c34 clone-2's
`BATCH_SPREAD_COLLAPSED` finding.

**Verdict: `SPREAD_STILL_COLLAPSED` (first-class negative finding).**

**Rubric SHA-256:** `749973025e5fa4c18c745eb0aedfda3773be003b72eab390754ba21e18aaeb6c`
(`docs/palette_driven_batch_v2_sampler_diversified_rubric.md` →
`data/gen_palette_batch_v2/rubric_hash.txt` → embedded in
`data/gen_palette_batch_v2/verdict.json.rubric_hash`).

## 1. Situation carried in

c34 clone-2 rendered a 3-song palette-driven batch (salts 0, 1, 2)
through the c33 palette-render pipeline and observed
**`BATCH_SPREAD_COLLAPSED`** — all three salts produced byte-identical
`bare_combined.wav` at SHA
`a8c1557c09470340aea0cb0556468117d67907292af35e2a351dbe9c212ba794`.
Root cause: the c33 dispatcher `scripts.palette_render.build_assignments.build_assignment_row`
is `rule_id`-invariant. Different rule triples produce identical
assignment rows apart from the (metadata) `provenance_pointers` and
`assignment_id` — the renderer `render_stem(stem, instrument, out_dir)`
sees only `(stem, instrument)`.

## 2. What this cycle changed

Two orthogonal per-salt differences were threaded:

1. **Per-salt DIFFERENT rule triples with cross-salt distinctness.** For
   each rule_type ∈ {harmonic, rhythmic, arrangement}, salts pick rank-0
   by SHA-256 tiebreak on `sha256(f"{salt}|{rule_id}|{rule_type}")` over
   the full candidate pool on `data/rules/ledger.jsonl` (base 76-row
   ledger, actual counts H=10, R=18, M=18, F=15, A=15 — **the brief's
   "K=20 harmonic" was a carry-over typo from c15's D-minor augmented
   ledger; deviation noted here rather than in code**). Cross-salt
   distinctness is enforced: on rule_id collision within a rule_type, the
   higher-salt clone falls to next rank. Implementation:
   `scripts.gen_palette_batch_v2.sample_rule_triple_v2.sample_triples`.

2. **Pinned-state perturbation for Surge XT + Dexed.** Per
   `(rule_id, param_name)`, a deterministic typed delta (SHA-256 rank-0
   bytes 0..3 as uint32; float→uniform `[-δ,+δ]` with δ=0.05; int→mod-N
   stride; bool→XOR bit-0) is applied to the c33 dawdreamer_state P1
   iterated_params anchor. The output is wrapped as a `v2_iterated_params`
   payload and validated through `scripts.palette_v2.validate.validate_row`
   at authoring time. Drums stay fluidsynth-static. Implementation:
   `scripts.gen_palette_batch_v2.perturb_pinned_state`. NO PRNG anywhere.

Actual audio render invokes the c33 `scripts.palette_render.*` machinery
verbatim through read-only import.

## 3. Per-salt rule triples (cross-salt distinct ✓)

| salt | harmonic                | rhythmic                | arrangement             |
|------|-------------------------|-------------------------|-------------------------|
| 0    | `rule_900193a92a8810e5` | `rule_2afe9862efd1e8ea` | `rule_1aa3fa507bba0573` |
| 1    | `rule_2549a4193dead599` | `rule_4f801fa8961967c3` | `rule_a8ffe2f88dc29eed` |
| 2    | `rule_ff1fa8c4bf0f228f` | `rule_6ae8cec716982090` | `rule_f14c45df9121ab03` |

All 9 rule_ids distinct. The sampler diversification landed exactly as
designed. Per-salt canonical-JSON of the triple:

- salt 0: SHA-256 = `3fbeca33f065506fd1ed6cf8a511a2bfe8167a850ca2b99f238992a13c88b653`
- salt 1: SHA-256 = `2d9e79dc78b68e968384c2eeec3e68dccd1327afafece96fe1946197a8e4cd0e`
- salt 2: SHA-256 = `7560cfaf9ba23e2b26dc2af506d0e62fb92a68194bd50a368e6f7216089c8d80`

## 4. Perturbed v2 pinned-state payloads (per-salt distinct ✓)

For each salt, `perturb_pinned_state.build_v2_assignment_row(stem="mono",
plugin_name, rule_id=triple["harmonic"], provenance_pointers)` was
invoked for `plugin_name ∈ {surge_xt, dexed}`. Every row validated
through the c34 palette_v2 validator; per-salt `iteration_sha_256`s and
`assignment_id_v2`s differ:

| salt | plugin   | iteration_sha_256[0..16] | assignment_id_v2[0..12] |
|------|----------|---------------------------|--------------------------|
| 0    | dexed    | `da699df6ad24bb0b`        | `56c24c966ed7`           |
| 0    | surge_xt | `9e07e01c962a7d5d`        | `ef4e4ed82cec`           |
| 1    | dexed    | `554252fb08e7cb3a`        | `da6af0eede99`           |
| 1    | surge_xt | `7fa3c6e8785e183b`        | `a07740a1c136`           |
| 2    | dexed    | `2411749da6151176`        | `add43a8bbe6c`           |
| 2    | surge_xt | `8ca313ca2ecee331`        | `ab1c481c525d`           |

Surge XT iteration size = 2855 params; Dexed = 2238. Payloads written to
`data/gen_palette_batch_v2/per_song/<salt>/v2_perturbed/{surge_xt,dexed}.json`
and are ready for a c36 renderer that consumes them.

## 5. Panel measurements — SPREAD_STILL_COLLAPSED

Every salt produced identical numeric values on both panels (the
`bare_combined.wav` file is byte-identical across the 3 salts):

`panel_original` (original synth_030s vs palette-bare):
`mel_l1_db = 16.5520, spectral_centroid_rmse_hz = 1982.91,
rms_env_rmse = 0.05911, lufs_m_rmse_lu = 4.8783` (identical for salts
0, 1, 2).

`panel_fluidsynth` (c9 fluidsynth-only vs palette-bare):
`mel_l1_db = 23.6785, spectral_centroid_rmse_hz = 3094.51,
rms_env_rmse = 0.06499, lufs_m_rmse_lu = 6.6885` (identical for salts
0, 1, 2).

Per-key IQR = 0.000000 and `max − min = 0.000000` on every one of the 4
numeric-family keys on both panels. The 3 salts produce a single
distinct `bare_combined.wav` SHA:
`a8c1557c09470340aea0cb0556468117d67907292af35e2a351dbe9c212ba794` —
byte-equal to c34 clone-2's anchor. Per-salt byte-determinism × 2 holds
on every stem and combined WAV.

`sfizz_vs_delta_correlation` returns `None` because both variables are
constant across salts (sfizz count = 2, mel_l1_db_fluid_vs_palette
= 23.6785 for every salt) — Pearson is undefined on a zero-variance
axis. This is expected and correct.

## 6. Mechanism exposition — the load-bearing negative finding

The sampler-side diversification landed cleanly at the provenance and
metadata layers:

- Rule triples per salt DIFFER — verified by three distinct
  `assignments.jsonl` SHAs.
- Perturbed v2 pinned-state payloads per salt + plugin DIFFER —
  verified by six distinct `iteration_sha_256`s and six distinct
  `assignment_id_v2`s.

But the audio path is IDENTICAL across salts because the c33
`render_stem` API is `(stem, instrument, out_dir)`-parameterized only.
Drums render via fluidsynth+SF2 on a fixed per-stem MIDI; bass/other
render via sfizz+SFZ (chosen by SFZ fetchability, not by rule) on a
fixed per-stem MIDI. Neither dispatcher consumes `pinned_state`,
`provenance_pointers`, `assignment_id`, or `iterated_params`. The
palette-v2 payloads authored here are CORRECT and VALIDATED but do
not flow into audio bytes on this cycle.

This is exactly the mechanism c34 clone-2 identified. Sampler-side
diversification alone is insufficient to move the `bare_combined.wav`
SHA because the actual render path is renderer-side.

## 7. Handoff to c36 — `M-GEN-1/palette-driven-batch-v3`

Two concrete follow-up candidates fall out of this finding:

- **Deeper perturbation surface** — extend `scripts.palette_render.render_stem`
  to consume a `pinned_state` payload for `fluidsynth_gm` (SF2 alt banks,
  gain per stem, MIDI velocity/pitch nudges) and for `sfizz`
  (opcode overrides, sample overrides, per-stem MIDI perturbation).
  The palette-v1 schema already carries `parameter_dict`; the c33
  render dispatch would need to consume it. This is the cheapest path
  to move audio bytes with the existing renderer chain.
- **Generator swap** — introduce a c33-style peer renderer that
  dispatches on `surge_xt` / `dexed` and consumes the palette-v2
  `v2_iterated_params` payloads this cycle already authored. This is
  the palette-v2 payoff: the payloads are ready, the schema is
  frozen, the P1 anchor is stable; the missing piece is a renderer
  that instantiates DawDreamer with those iterated params applied to
  the plugin state. Non-trivial (per c31/c33 STILL_GAP on Surge XT +
  Dexed byte-determinism), but the palette-v2 uplift makes it
  tractable.

Recommend c36 pursue **both** in parallel: cheap perturbation-surface
extension on the fluidsynth/sfizz path (Option A) AND generator-swap
scaffolding on the VST3 path (Option B). Option A moves audio in the
short term; Option B unlocks the strategic direction.

## 8. Anchors preserved (test-verified ✓)

`anchor_preservation.unchanged == True` — every file under
`scripts/palette_v2/`, `data/palette_v2/`, `scripts/palette_render/`,
`data/palette_render/`, `scripts/dawdreamer_state/`,
`data/dawdreamer_state/`, `scripts/palette/`, `scripts/palette_probe/`,
`data/palette/`, `data/palette_probe/`, `scripts/texture/panel.py`,
`data/rules/ledger.jsonl` retained its byte-identical SHA and mtime
across the run.

`data/rules/ledger_i3_dminor.jsonl` was not read this cycle (AST-string
literal grep in the test suite confirms).

## 9. Contract checks (test-verified ✓)

- 20/20 tests in `tests/test_palette_driven_batch_v2.py` PASS.
- Cross-branch integration §55 in `tests/test_integration_cross_branch.py` PASS.
- Rubric SHA doc == `rubric_hash.txt` == `verdict.json.rubric_hash`.
- Rubric mtime PRECEDES every script under `scripts/gen_palette_batch_v2/`.
- Per-salt byte-determinism × 2 on every stem and combined WAV.
- Panel returns 8 finite keys on every salt on both panels.
- AST-grep clean: no `random`, `numpy.random`, `torch.*seed`,
  `secrets`, `os.urandom`, `sidecar_nonfactor`.
- AST-grep clean: no import of the 16 forbidden anchor modules
  (c9 chain, c13 pipeline, c15 i4_stratified, c22 stability harness,
  c26/27/28/29/30 collision-model utilities).
- Interpreter guard `assert sys.executable == '/usr/bin/python3'`
  on every new script.
- Egress probe row written to `data/ingestion/egress_status.jsonl`
  (non-blocking; `media_ok=false`).
- Six named + two housekeeping ledger events emitted with `-clone-1`
  suffix on infra families; substantive `M-*` milestone unsuffixed
  per c32 fanout-namespace convention.

## 10. `SPREAD_STILL_COLLAPSED` as first-class

Per the rubric's post-cycle discipline: `SPREAD_STILL_COLLAPSED` is
NOT a bug — it is the mechanistic exposure that the c34-c35 branch of
the investigation was designed to close on. The value of this cycle
is the honest, load-bearing finding that sampler-side diversification
alone cannot move audio bytes through the c33 renderer, AND the
concrete evidence that the c34 palette-v2 schema's `v2_iterated_params`
payloads validate deterministically under per-rule perturbation. That
evidence hands c36 a clean starting point for either of the two
follow-up options above without needing to re-explore the sampler
layer.
