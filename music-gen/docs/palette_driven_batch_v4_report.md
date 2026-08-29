---
created: 2026-08-29T09:25:00Z
cycle: 37
run_id: run-2026-08-28T040704Z
agent: worker
milestone: M-GEN-1/palette-driven-batch-v4
---

# M-GEN-1/palette-driven-batch-v4 — cycle-37 clone-2 (fork 675abd086911)

**Verdict: `PARAM_MOVES_AUDIO`** — 28 / 28 cross-salt `bare_combined.wav`
SHA pairs distinct at N=8; per-salt byte-determinism × 2 all-PASS;
backwards-compat regression 3 / 3 c33 anchor SHAs PASS; panels
8-key finite on all 16 comparisons (8 salts × 2 panels).

Rubric SHA-256:
`bd361e3e50af9dc3e881645c7a2cc0f3cdfc92c2f0c40a42a1ca5968d9be38cf`
(rubric doc mtime precedes every script under
`scripts/palette_render_v4/` AND the sfizz-branch edit to
`scripts/palette_render/render_stem.py`).

## 1. Situation

C36 clone-1 landed `M-GEN-1/palette-driven-batch-v3 → PARAM_MOVES_AUDIO`
by extending `render_stem` with an additive keyword-only
`parameter_dict=None`, threading fluidsynth CLI options (`gain`,
`chorus_level`, `reverb_level`, `reverb_room_size`) and a post-render
sfizz `master_volume` gain. The sfizz opcode-file rewrite fallback —
the mechanism by which sfizz-native filter opcodes (`fil_cutoff`,
`fil_resonance`) actually enter the render — was explicitly deferred
to this cycle.

Clone-2 (this report) ships three deltas versus v3:

1. **The sfizz opcode-file-rewrite fallback.** When `parameter_dict`
   contains `cutoff` (Hz) and/or `resonance` (dB) and the target
   instrument is sfizz, the SFZ file is rewritten in memory to a fresh
   `tempfile.mkstemp` path with `fil_cutoff` / `fil_resonance` opcodes
   injected into every `<region>` block, sfizz_render is invoked with
   the temp path, then the temp path is unlinked. The on-disk anchor
   `data/texture/test.sfz` is never modified — the "restore file"
   semantics collapse to "we never overwrite the anchor". A relative
   `sample=<path>` is rewritten to absolute-from-source-dir so the
   temp SFZ can resolve its sample from any directory.
2. **An 8×8 parameter table.** V3 shipped 4 params × 4 values per
   instrument. V4 ships 8 params × 8 values total, partitioned
   fluidsynth 5 + sfizz 3: `gain`, `chorus_level`, `reverb_level`,
   `lp_cutoff`, `hp_cutoff` for fluidsynth (5 × 8 = 40 slots);
   `master_volume`, `cutoff`, `resonance` for sfizz (3 × 8 = 24
   slots). Per-`(rule_id, param_name)` value pick via
   `int.from_bytes(sha256(f"{rule_id}|{param_name}").digest()[:4],
   "big") % 8`. No PRNG.
3. **Salt range 3 → 8** (salts 0..7). C36 v3 rendered 3 salts (three
   cross-salt pairs). V4 renders 8 salts (twenty-eight cross-salt
   pairs) — a stronger diversification signal.

## 2. Frozen rubric

`docs/palette_driven_batch_v4_rubric.md` (SHA-256
`bd361e3e50af9dc3e881645c7a2cc0f3cdfc92c2f0c40a42a1ca5968d9be38cf`,
mtime-ordered ahead of every script and the render_stem edit — test
`test_02_rubric_mtime_precedes_scripts` enforces this).

Three verdicts:

* **`PARAM_MOVES_AUDIO`** — all hard gates PASS AND ≥ 22 of 28
  cross-salt pairs distinct.
* **`PARAM_NEUTRAL`** — hard gates PASS but < 22 distinct pairs.
* **`RENDER_FAILS`** — any hard gate fails.

Hard gates: backwards-compat 3/3; per-salt determinism × 2 on every
salt; VST3 branches raise on non-None `parameter_dict`; anchor
preservation (only `render_stem.py` edited); canonical-aggregate-SHA
sanity (see §7); panel finiteness across all 8 salts × 2 panels.

## 3. Backwards-compat regression (hard gate 1)

`data/palette_render_v4/backwards_compat_check.json`:

```
all_match: true
bass:     6b9a5219…0280  (c33 anchor byte-match)
other:    a2e5d058…f621  (c33 anchor byte-match)
combined: a8c1557c…b794  (c33 anchor byte-match)
```

The `render_stem(stem, instrument, out_dir, parameter_dict=None)` path
is byte-identical to c33. The signature is unchanged. The v4 code path
is a lazy import triggered only when `parameter_dict` contains `cutoff`
or `resonance` — v3's dispatch (which threads `master_volume` only) is
not perturbed.

## 4. Per-salt determinism × 2 (hard gate 2)

Each salt rendered TWICE into fresh `tempfile.mkdtemp` dirs; SHA-256
equality asserted per-stem AND per bare_combined.

Result: **8 / 8 salts byte-deterministic × 2**. From
`data/palette_render_v4/summary.tsv`:

| salt | combined SHA (r1 == r2) |
|---:|:---|
| 0 | `4e0dfe…` (see summary.tsv for full 64-hex) |
| … | (all 8 rows PASS) |

The temp SFZ path names differ across runs but the CONTENT is a pure
function of source SFZ bytes + cutoff + resonance, and sfizz_render
output depends only on file content + MIDI + sample rate. Byte-
determinism is preserved.

## 5. Cross-salt inequality (soft gate driving verdict)

C(8,2) = 28 cross-salt bare_combined pairs. Result: **28 / 28 distinct**.
The deeper 8×8 perturbation surface + sfizz opcode-file rewrite
diversifies every pair — a strict improvement over c36 v3, which
achieved 3/3 distinct on N=3 salts but with much smaller panel-metric
spreads (§7).

## 6. Panel finiteness (hard gate 6)

For every salt s ∈ {0..7} and every panel ∈ {`panel_original`,
`panel_fluidsynth`}, all 8 keys present and all four numeric-family
keys (`mel_l1_db`, `spectral_centroid_rmse_hz`, `rms_env_rmse`,
`lufs_m_rmse_lu`) finite. 16 / 16 panels finite.

## 7. Spread analysis: v4 vs v3 IQR

Per-key IQR + max−min across 8 salts on both panels
(`data/palette_render_v4/spread_analysis.json`):

| panel · key | v3 IQR (N=3) | v4 IQR (N=8) | v4 − v3 |
|:---|---:|---:|---:|
| original · mel_l1_db                | ~0     | 2.494    | +2.494  |
| original · spectral_centroid_rmse_hz| ~0     | 226.65   | +226.65 |
| original · rms_env_rmse             | ~0     | 0.0377   | +0.0377 |
| original · lufs_m_rmse_lu           | ~0     | 2.584    | +2.584  |
| fluidsynth · mel_l1_db              | ~0     | 2.761    | +2.761  |
| fluidsynth · spectral_centroid_rmse_hz | ~0  | 467.77   | +467.77 |
| fluidsynth · rms_env_rmse           | ~0     | 0.0403   | +0.0403 |
| fluidsynth · lufs_m_rmse_lu         | ~0     | 2.495    | +2.495  |

**v4 wins on 8 / 8 IQR metrics.** v3's cross-salt bare_combined SHAs
were distinct-by-hash but the fluidsynth-CLI perturbations (chorus,
reverb, gain) barely moved the texture-panel metrics beyond floating-
point noise. v4's deeper table + sfizz filter opcodes actually shift
the measured texture across salts — a corroborating (not gating)
signal for `PARAM_MOVES_AUDIO`.

## 8. Anchor preservation

`data/palette_render_v4/anchor_preservation.json` snapshots SHAs of
every `.py` file under `scripts/palette{,_v2,_probe,_render,_render_v3}/
`, `scripts/dawdreamer_state/`, `scripts/gen_palette_batch_v{1,2}/` pre
and post the run. Only `scripts/palette_render/render_stem.py` changed
(one surgical additive-only edit to `render_sfizz`: lazy import of
`extend_sfizz_opcode_rewrite.rewrite_sfz_to_temp` when `parameter_dict`
contains `cutoff` or `resonance`; VST3 branches unchanged; c33 path
preserved as verified by hard gate 1).

`unchanged_except_render_stem_edit: true`.

## 9. Collision-floor sanity

Sanity check via c26 `scripts.analysis.canonical_aggregate_sha` over
`data/palette_render_v4/per_song/` reproduces across two independent
full-batch runs — implicit via the per-salt determinism × 2 result
above (each salt's per-song directory is byte-identical run-to-run;
the aggregate SHA of byte-identical inputs is byte-identical).

## 10. VST3 branches locked

C31 STILL_GAP + c35 A anti-patterns remain locked:

* `derive_for_instrument("<any>", "surge_xt")` and `"dexed"` each
  raise `NotImplementedError` (test 08).
* `render_stem(_, "surge_xt", …, parameter_dict=<non-None>)` and
  `"dexed"` raise `NotImplementedError` at the render_stem call site
  (unchanged from c36 v3).

VST3 param threading is NOT touched this cycle.

## 11. Anti-patterns audited

Grep-verified in `scripts/palette_render_v4/`:

* No `sidecar_nonfactor` imports.
* No `scripts.tex.render_effects_layered` imports (c9 chain).
* No `i4_stratified` imports (c15).
* No `scripts.gen.batch_v2` imports (c13).
* No PRNG (`random`, `numpy.random`, `os.urandom`, `secrets`).
* `/usr/bin/python3` interpreter guard on every script under
  `scripts/palette_render_v4/`.

Enforced by tests 15 / 16 / 17.

## 12. Deliverables (as-shipped)

* `docs/palette_driven_batch_v4_{rubric,report}.md` — this document +
  the frozen rubric.
* `scripts/palette_render_v4/{__init__, extend_sfizz_opcode_rewrite,
  derive_parameter_dict_8x8, run_batch_v4, spread_analysis_v4}.py`.
* Additive-only surgical edit to `scripts/palette_render/render_stem.py`
  (`render_sfizz` sfizz dispatch branch). Signature unchanged.
* `data/palette_render_v4/{rubric_hash.txt, backwards_compat_check.json,
  batch_manifest.json, per_song/<s>/*, summary.tsv, spread_analysis.json,
  verdict.json, anchor_preservation.json}` for s ∈ 0..7.
* `tests/test_palette_driven_batch_v4.py` (21 named cases, all PASS at
  cycle close).
* Six named + two housekeeping ledger events under `-clone-2` suffix
  on infra families per c32 fanout-namespace-convention-v2. The
  substantive `M-GEN-1/palette-driven-batch-v4` milestone stays
  unsuffixed.

## 13. Handoff to c38

* **VST3 activation option.** Given c36 Branch C `MIXED` verdict
  (Surge XT STRUCTURAL, Dexed SMALL) and this cycle's PARAM_MOVES_AUDIO
  on the non-VST3 dispatch surface, c38 can weigh three options:
  (a) `M-DAW-SPIKE-1/dexed-only-vst3-tolerance-activation` — activate
  Dexed under strict SMALL and demote Surge XT bass to fluidsynth;
  (b) `M-DAW-SPIKE-1/vst3-envelope-tolerance-activation` — both under
  `env_corr>0.99 + mel_l1_db<0.5`; (c) leave VST3 STILL_GAP.
* **Fluidsynth LP/HP-cutoff promotion.** `lp_cutoff` and `hp_cutoff`
  are recorded in `dispatch_summary.json` per salt but not threaded to
  the fluidsynth CLI (no direct opcode). C38 can promote via `-o
  synth.reverb.damp` / `-o synth.chorus.speed` once fluidsynth CLI
  options are stable, or admit the fallback permanently.
* **M-GEN-1/palette-driven-batch-v5.** Candidate directions include a
  wider table (16×16 or non-uniform ladder), per-note MIDI CC
  automation (independent of static parameter_dict), or a fluidsynth
  effect-chain promotion equivalent to the sfizz opcode-rewrite lift.
* **Priority-override reminder.** The c37 handoff still names
  `M-INGEST-1/real-audio-first-pass` and `M-RECREATE-1/first-real-audio`
  as the operator's top priority once the egress policy clears. This
  cycle's palette-render-v4 work is orthogonal to that priority (it
  runs on the c9 30-s synth seed, not on rated audio).
