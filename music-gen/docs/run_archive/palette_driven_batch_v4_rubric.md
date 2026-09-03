---
created: 2026-08-29T09:05:00Z
cycle: 37
run_id: run-2026-08-28T040704Z
agent: worker
milestone: M-GEN-1/palette-driven-batch-v4
---

# M-GEN-1/palette-driven-batch-v4 — frozen rubric (fork 675abd086911, clone-2)

This rubric is committed BEFORE any script under
`scripts/palette_render_v4/` lands. Its SHA-256 is recorded verbatim in
`data/palette_render_v4/rubric_hash.txt` and embedded in
`data/palette_render_v4/verdict.json.rubric_hash`. The test suite
enforces mtime-order (rubric doc precedes every script under
`scripts/palette_render_v4/` AND the render_stem edit) via file-mtime
check with git-log fallback.

## 1. Scope

Deeper-perturbation extension of c36 clone-1
`M-GEN-1/palette-driven-batch-v3 → PARAM_MOVES_AUDIO`. Three deltas
vs v3:

* **sfizz opcode-file-rewrite fallback** (deferred from c36). When
  `parameter_dict` contains `cutoff` and/or `resonance` and the target
  instrument is sfizz, the SFZ file is rewritten in memory to a fresh
  `tempfile.mkstemp` path (adds `fil_cutoff=<Hz>` and/or
  `fil_resonance=<dB>` opcodes into each `<region>` block), sfizz_render
  is invoked with the temp path, then the temp path is unlinked. The
  on-disk anchor `data/texture/test.sfz` is never modified in place —
  the "restore file" semantics of the directive collapse to
  "we never overwrite the anchor".
* **8×8 parameter table**. c36 v3 shipped 4 params × 4 values per
  instrument. v4 ships 8 params × 8 values total, partitioned by
  instrument:
    * fluidsynth: `gain`, `chorus_level`, `reverb_level`,
      `lp_cutoff`, `hp_cutoff` (5 params × 8 values).
    * sfizz: `master_volume`, `cutoff`, `resonance`
      (3 params × 8 values).
  Total surface = 5 + 3 = 8 params × 8 values = 64 index slots. Per-
  `(rule_id, param_name)` value pick via
  `int.from_bytes(sha256(f"{rule_id}|{param_name}").digest()[:4], "big") % 8`.
* **Salt range 3 → 8** (salts 0..7). v3 rendered salts 0..2 (three
  cross-salt pairs). v4 renders salts 0..7 (twenty-eight cross-salt
  pairs) — a stronger diversification signal.

## 2. Verdicts (frozen — no addenda without a new brief)

| Verdict | Preconditions |
|---|---|
| **`PARAM_MOVES_AUDIO`** | All hard gates PASS AND ≥ 22 of 28 cross-salt `bare_combined.wav` SHA pairs distinct (documented shallowness attribution for any equal pair) AND panels 8-key finite per salt. |
| **`PARAM_NEUTRAL`** | All hard gates PASS but < 22 of 28 cross-salt pairs distinct — the deeper 8×8 table + opcode-rewrite still failed to diversify beyond noise. |
| **`RENDER_FAILS`** | Any hard gate fails. |

**Hard gates** (all must PASS for a non-`RENDER_FAILS` verdict):

1. **Backwards-compat regression.** All 3 c33 anchor SHAs match under
   `parameter_dict=None`:
    * bass  = `6b9a5219e761854bdcf42a87f370a283e3fb096faf64648eb198c98520540280`
    * other = `a2e5d0585404b448a2120c3c4bd6432ec1962ed82c3a7a74dd7518ed3d10f621`
    * combined = `a8c1557c09470340aea0cb0556468117d67907292af35e2a351dbe9c212ba794`
2. **Per-salt determinism × 2.** For each salt `s ∈ {0..7}`, two fresh
   `tempfile.mkdtemp` renders produce byte-identical
   `bare_combined.wav`.
3. **VST3 branches locked.** `render_stem(_, "surge_xt", …,
   parameter_dict=<non-None>)` and `render_stem(_, "dexed", …,
   parameter_dict=<non-None>)` raise `NotImplementedError`. c35 A
   anti-pattern remains locked.
4. **Anchor preservation.** All anchor SHAs unchanged except the one
   documented `scripts/palette_render/render_stem.py` edit (sfizz
   dispatch branch grows to the opcode-rewrite fallback; VST3 branches
   still raise; fluidsynth branch unchanged). c33 palette_render + c34
   palette_v2 + c36 palette_render_v3 sibling files READ-ONLY.
5. **Collision floor sanity.** Canonical aggregate SHA over
   `data/palette_render_v4/per_song/` via
   `scripts.analysis.canonical_aggregate_sha` (c26) reproduces across
   two independent full-batch runs.
6. **Panel finiteness.** For every salt and every panel (original
   comparison + fluidsynth comparison), all 8 keys are present and all
   four numeric-family keys (`mel_l1_db`,
   `spectral_centroid_rmse_hz`, `rms_env_rmse`, `lufs_m_rmse_lu`)
   are finite.

## 3. Anti-patterns locked

* c31 STILL_GAP (VST3 state-extraction) — not re-opened.
* c35 A RENDER_FAILS (VST3 hydration render) — not re-opened.
* No PRNG. All non-determinism candidates SHA-256-tiebroken.
* No `sidecar_nonfactor` imports.
* c9 effects chain (`scripts/tex/render_effects_layered.py`) NOT
  imported.
* c13 batch-v2 pipeline NOT imported.
* c15 `i4_stratified.py` NOT imported.
* Cycle-22 stability harness NOT imported.
* Cycle-26/27/28/29/30 collision-modeling utilities NOT imported by
  batch code (spread analysis is v4-local; `canonical_aggregate_sha`
  imported READ-ONLY for the sanity check only).
* `/usr/bin/python3` interpreter guard on every script.

## 4. Deliverables

* `docs/palette_driven_batch_v4_{rubric,report}.md` (this file +
  companion).
* `scripts/palette_render_v4/{__init__, extend_sfizz_opcode_rewrite,
  derive_parameter_dict_8x8, run_batch_v4, spread_analysis_v4}.py`.
* Additive-only edit to `scripts/palette_render/render_stem.py` sfizz
  branch (opcode-rewrite path). c36 additive-kwargs signature
  `render_stem(stem, instrument, out_dir, *, parameter_dict=None)`
  UNCHANGED.
* `data/palette_render_v4/{rubric_hash.txt, backwards_compat_check.json,
  batch_manifest.json, per_song/<s>/*, summary.tsv, spread_analysis.json,
  verdict.json, anchor_preservation.json}` (s ∈ 0..7).
* `tests/test_palette_driven_batch_v4.py` (≥ 16 cases).
* Six named + two housekeeping ledger events under `-clone-2` suffix on
  infra families per c32 fanout-namespace-convention-v2.

## 5. Spread contract

Per-key IQR + max−min across the 8 salts on both
`panel_original` and `panel_fluidsynth`. Compared against the c36 v3
per-key spread (3-salt IQR + max−min from `data/palette_render_v3/
spread_analysis.json` if present). v4 IQR ≥ v3 IQR on a majority of
the 4 numeric keys is a corroborating signal for the
`PARAM_MOVES_AUDIO` interpretation (not itself a gate).
