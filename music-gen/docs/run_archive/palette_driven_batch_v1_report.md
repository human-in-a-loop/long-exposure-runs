---
created: 2026-08-29T05:20:00Z
cycle: 34
run_id: run-2026-08-28T040704Z
agent: worker
milestone: M-GEN-1/palette-driven-batch-v1
---

# M-GEN-1/palette-driven-batch-v1 — Report

**Cycle 34, Branch C (fork 43802db1a81c, clone-2).**
**Verdict: `BATCH_SPREAD_COLLAPSED` — first-class negative finding.**

## §1. Frozen rubric verbatim + SHA

- Rubric doc: `docs/palette_driven_batch_v1_rubric.md`
- SHA-256: `42f0bcea9ea13e4543380d5b17034c623deeb69fb5ef1a98b54e1ed670101017`
- Committed to disk **before** any Python module under
  `scripts/gen_palette_batch_v1/` landed (test §12 asserts this via
  mtime + git-log fallback; test §53b in the cross-branch suite
  re-asserts).

Three verdicts, exhaustive:

- **BATCH_SPREAD_EXPECTED** — ≥ 2 distinct `bare_combined.wav` SHAs
  AND per-key IQR ≥ half c33 single-seed delta on ≥ 1 numeric-family
  key.
- **BATCH_SPREAD_COLLAPSED** — all 3 salts yield the same
  `bare_combined.wav` SHA (or SHA-distinct but no IQR meets bar).
  First-class negative finding.
- **BATCH_FAILS** — any byte-determinism, 8-key-finite panel, or
  c31 palette-v1 validator check fails.

## §2. Execution timeline

| Step | Milestone-id | Substantive artifact |
|------|--------------|----------------------|
| 1 | `_infra/egress-probe-cycle-34-clone-2` | `data/ingestion/egress_status.jsonl` (unchanged since c26; `media_ok=false`, `http_code=403`) |
| 2 | `_run/cycle_34_launched-clone-2` | — |
| 3 | Author `docs/palette_driven_batch_v1_rubric.md` (SHA `42f0bcea…`) + `data/gen_palette_batch_v1/rubric_hash.txt` | 2 files |
| 4 | `_plan/palette_driven_batch_v1_rubric_frozen-clone-2` (plan-row registration folded in narrative) | `plan_of_record.md` row added |
| 5 | `M-GEN-1/palette-driven-batch-v1` in-progress/medium | — |
| 6 | Author 5 scripts under `scripts/gen_palette_batch_v1/` in required order | 5 files |
| 7 | Author `tests/test_palette_driven_batch_v1.py` (16 cases) | 1 file |
| 8 | Extend `tests/test_integration_cross_branch.py §53` (9 checks) | +105 LOC |
| 9 | Run `scripts.gen_palette_batch_v1.run_batch` → 6 renders + 6 panels | `data/gen_palette_batch_v1/**` |
| 10 | Run test suites (16/16, 0 failures) + `promise_check` (0-ERROR) | — |
| 11 | `M-GEN-1/palette-driven-batch-v1` verdict roll-up (validated/high, `BATCH_SPREAD_COLLAPSED`) | verdict.json |
| 12 | `_run/cycle_34_closed-clone-2` | — |
| 13 | `_archive/cycle-34-scratch-clone-2` (emitters → `tools/stale/`) | 2 files |
| 14 | `_infra/adopt-cycle34-tests-clone-2` (new tests adopted) | 2 files |

## §3. Per-salt rule-triple selection

Selection rule (per salt, per rule_type ∈ {harmonic, rhythmic, arrangement}):
sort matching `rule_id`s from `data/rules/ledger.jsonl` by
`sha256(f"{salt}|{rule_id}".encode())`, take rank 0. NO PRNG. NO
rejection loop. NO exclusion set.

Corpus counts (`data/rules/ledger.jsonl` frozen): harmonic=10,
rhythmic=18, arrangement=15 (also melodic=18, form=15 — not consumed
by this branch).

| Salt | Harmonic rank-0 | Rhythmic rank-0 | Arrangement rank-0 |
|------|------------------|------------------|--------------------|
| 0    | `rule_d8ab0bcf0694e01d` | `rule_7be767b167d250f6` | `rule_1aa3fa507bba0573` |
| 1    | `rule_900193a92a8810e5` | `rule_d15d2951e86e16bf` | `rule_4e0d2fded1aef6ac` |
| 2    | `rule_a5f50a9707200179` | `rule_7894d12215472070` | `rule_dc9073323dc15d36` |

All three triples are pairwise disjoint — the SHA-tiebreak is
genuinely salt-sensitive at the rule-selection layer. This is a
successful sampler test; the negative finding is *downstream* of it.

## §4. Per-salt assignment builder output

Assignments were built by re-using c33's `scripts.palette_render.build_assignments.build_assignment_row`
(READ-ONLY import) with `provenance_pointers=sorted(triple.values())`,
validated through `scripts.palette.validate.validate_row` (both layers
of c31 palette-v1 — no rejects on any of the 9 assignment rows).

| Salt | Assignment ids (drums / bass / other) | Per-stem instrument |
|------|---------------------------------------|---------------------|
| 0    | `b42f7b74…` / `a3b57902…` / `b64d13fb…` | drums→fluidsynth_gm; bass→sfizz; other→sfizz |
| 1    | `31f81213…` / `22511c18…` / `b87f1f85…` | drums→fluidsynth_gm; bass→sfizz; other→sfizz |
| 2    | `c5460b01…` / `855c6344…` / `2d489e39…` | drums→fluidsynth_gm; bass→sfizz; other→sfizz |

All 9 `assignment_id`s are pairwise distinct across salts — proving
the rule-triple divergence propagates into the `assignment_id`
content-hash (`UUID5(NAMESPACE, canonical_json(row_minus_notes))`).
No `SKIP_COMBOS` enforced this cycle: the per-stem dispatch policy
in c33 `build_assignment_row` is fixed (drums → `fluidsynth_gm`;
bass/other → `sfizz` when SFZ + `sfizz_render` fetchable, else
`fluidsynth_gm`). SFZ + `sfizz_render` were both fetchable, so bass
and other resolved to `sfizz` for every salt.

## §5. Per-salt render results (byte-determinism)

Every per-stem WAV rendered twice into fresh `tempfile.mkdtemp()`
directories via `scripts.palette_render.render_stem.render_stem`
(READ-ONLY import). SHA-256 equality asserted per stem and again on
the summed `bare_combined.wav`.

| Salt | Per-stem `sha_equal` | `bare_combined` `sha_equal` |
|------|----------------------|-----------------------------|
| 0    | drums=✓, bass=✓, other=✓ | ✓ |
| 1    | drums=✓, bass=✓, other=✓ | ✓ |
| 2    | drums=✓, bass=✓, other=✓ | ✓ |

Every `pinned_state.json` records the deterministic dispatch: same
per-stem `midi_input_sha256`, `sample_rate=44100`, `sample_count=
1_323_000`, `sha_equal=true`. See
`data/gen_palette_batch_v1/per_song/<salt>/per_stem/<stem>/pinned_state.json`.

## §6. 3-salt bare_combined SHA distinctness

| Salt | `bare_combined.wav.sha.run1` (prefix) | `bare_combined.wav.sha.run2` (prefix) |
|------|---------------------------------------|---------------------------------------|
| 0    | `a8c1557c09470340…` | `a8c1557c09470340…` |
| 1    | `a8c1557c09470340…` | `a8c1557c09470340…` |
| 2    | `a8c1557c09470340…` | `a8c1557c09470340…` |

**All 3 salts collapsed to the SAME `bare_combined.wav` SHA-256
(`a8c1557c09470340aea0cb0556468117d67907292af35e2a351dbe9c212ba794`)** —
identical to c33's single-seed `bare_combined.wav` SHA. `distinct_sha_count=1`.

## §7. Per-salt panel TSVs

`panel_original` = `texture_distance(original_synth_030s, palette_bare)`;
`panel_fluidsynth` = `texture_distance(c9_fluidsynth_only_bare, palette_bare)`.
Both call `scripts.texture.panel.texture_distance` (READ-ONLY, 8-key
contract, no aggregate).

| Salt | Panel | mel_l1_db | spectral_centroid_rmse_hz | rms_env_rmse | lufs_m_rmse_lu |
|------|-------|-----------|----------------------------|--------------|-----------------|
| 0 | vs original          | 16.5520 | 1982.9061 | 0.05911 | 4.8783 |
| 0 | vs fluidsynth-c9     | 23.6785 | 3094.5055 | 0.06499 | 6.6885 |
| 1 | vs original          | 16.5520 | 1982.9061 | 0.05911 | 4.8783 |
| 1 | vs fluidsynth-c9     | 23.6785 | 3094.5055 | 0.06499 | 6.6885 |
| 2 | vs original          | 16.5520 | 1982.9061 | 0.05911 | 4.8783 |
| 2 | vs fluidsynth-c9     | 23.6785 | 3094.5055 | 0.06499 | 6.6885 |

Every value is finite; every panel returns exactly the c33-required
8 keys. All three salts produce identical panels because they
produce identical audio.

## §8. Spread analysis

Per-key IQR + max − min across the 3 salts on `panel_fluidsynth`
(the rubric-relevant panel):

| Key                          | Values (salts 0,1,2)    | IQR    | max−min | Half-c33 bar | Meets bar? |
|------------------------------|--------------------------|--------|---------|---------------|------------|
| `mel_l1_db`                  | 23.6785, 23.6785, 23.6785 | 0.0000 | 0.0000 | 11.8393 | ✗ |
| `spectral_centroid_rmse_hz`  | 3094.5055 × 3            | 0.0000 | 0.0000 | 1547.2527 | ✗ |
| `rms_env_rmse`               | 0.06499 × 3              | 0.0000 | 0.0000 | 0.03249 | ✗ |
| `lufs_m_rmse_lu`             | 6.6885 × 3               | 0.0000 | 0.0000 | 3.3443 | ✗ |

`sfizz_vs_delta_correlation`: **null** — Pearson correlation is
undefined when either input has zero variance (all 3 salts have
`sfizz_count = 2` per song). Recorded as `null` in
`spread_analysis.json`; this is honest and diagnostic, not a bug.

## §9. Verdict against frozen rubric

Numeric justification:

- **BATCH_FAILS gate**: PASS. Every per-stem WAV byte-deterministic
  across two independent tempdir runs; every `bare_combined.wav`
  byte-deterministic; every panel returned 8 finite numeric-family
  keys; every one of the 9 assignment rows validated under
  `scripts.palette.validate.validate_row`.
- **BATCH_SPREAD_EXPECTED test**: FAIL. `distinct_sha_count = 1`
  (bar: ≥ 2). Vacuously the IQR test also fails (0.0 < half-c33 on
  every key).
- **BATCH_SPREAD_COLLAPSED test**: **PASS** on the "all-3-same-SHA"
  branch of the definition.

**Verdict**: `BATCH_SPREAD_COLLAPSED`.

**Mechanism** (exposed per rubric requirement — this is the point of
the finding):

The c33 `build_assignment_row` policy is *content-invariant of
rule_id*. Its dispatch decision reads only `stem` and the
fetchability of `sfz_ok` / `sfizz_ok` — it does not consult the
rules ledger at all. Consequently, the rule_id triple threads
straight through into the `provenance_pointers` list, changes the
`assignment_id` content-hash, and stops there. Downstream,
`render_stem` renders the *same per-stem MIDIs* (from the c9/c6
`data/transcribe/basic_pitch/synth_030s/{drums,bass,other}.mid`
anchor triple) under the *same instrument* per stem across all
three salts, producing byte-identical audio.

**This is a legitimate first-class negative finding**, not a bug.
The rubric predicts and names this failure mode: "rule-triple
selection degenerated relative to the palette-render dispatch —
either the SHA-tiebreak sort put the same three rule_ids at rank 0
for every salt, OR the palette-render output is content-invariant
across salts because the rule_ids drive only metadata …" The
second clause fits: the sort is genuinely salt-varying (§3), so the
mechanism sits in the palette dispatch layer.

## §10. Fetchability ladder summary

Latest per-cycle probe rows recorded in
`data/gen_palette_batch_v1/fetchability_ladder.jsonl` (appended by
`probe_fetchability`):

| Resource | Status | Note |
|----------|--------|------|
| `/usr/share/sounds/sf2/FluidR3_GM.sf2` | `ok`      | SHA `74594e8f…1cb0` matches c6 pin |
| `data/texture/test.sfz`                | `ok`      | SFZ bundle SHA `5f330e7b…` (unchanged) |
| `/usr/bin/fluidsynth`                  | `ok`      | binary present |
| `/usr/bin/sfizz_render`                | `ok`      | binary present |

Egress probe at cycle top (`_infra/egress-probe-cycle-34-clone-2`):
`workspace/harvest_playlists.sh` invoked; latest recorded row in
`data/ingestion/egress_status.jsonl` is `media_ok=false`,
`http_code=403`, `video_id=jNQXAC9IVRw` — unchanged since the c26
Path B commitment. Armed harness stays dormant.

## §11. Read-only anchor preservation

Snapshot at batch-close: `data/gen_palette_batch_v1/anchor_preservation.json`
records SHA-256 of every `.py` under the read-only anchor directories.
Cross-branch integration §53e/§53f re-verifies against the live
files.

| Anchor family | Directory | Verified unchanged |
|---------------|-----------|---------------------|
| c33 palette-render | `scripts/palette_render/` | ✓ (4 files: `__init__.py`, `build_assignments.py`, `render_stem.py`, `run_all.py`) |
| c31 palette-v1     | `scripts/palette/`        | ✓ (`__init__.py`, `provenance.py`, `validate.py`) |
| c31 palette-probe  | `scripts/palette_probe/`  | ✓ (snapshot only; not consumed this cycle) |
| M-TEX-1/panel      | `scripts/texture/panel.py` | ✓ |
| c9 effects chain   | `scripts/tex/render_effects_layered.py` | not imported (AST test §03) |
| c13 batch-v2       | `scripts/gen/batch_v2*`   | not imported (AST test §04) |
| c15 i4_stratified  | `scripts/rules/sampling/i4_stratified.py` | not imported (AST test §05) |
| c22/c26-30 analytical | `scripts/analysis/*`, `scripts/ear/stability_*` | not imported (AST test §06) |
| Rules ledger       | `data/rules/ledger.jsonl` | ✓ (streaming read-only) |

Test suite guards §14 (c33) and §15 (c31 palette-v1) re-assert
anchor SHA equality; cross-branch §53e / §53f re-assert.

## §12. Forward-look for cycle 35

Candidates surfaced by this finding (researcher decision — not
committed here):

1. **`M-GEN-1/palette-driven-batch-v1/rule-driven-dispatch`** —
   a peer sub-milestone that closes the observed rule → audio
   pathway gap. Concrete: extend `build_assignment_row` to read
   the arrangement rule's `instrumentation` / `density_over_time`
   / `layer_events` and pick a stem-specific SFZ file (or a
   fluidsynth GM patch id) from a small palette keyed on those
   parameters. Prediction: 3 salts → 3 distinct `bare_combined.wav`
   SHAs → BATCH_SPREAD_EXPECTED under the same rubric or an updated
   one.
2. **`M-GEN-1/palette-driven-batch-v1/n=5-8`** — replay the same
   test with more salts to characterize the collision rate of
   assignment_ids under SHA-256 tiebreak (analytical continuation
   of the c26-c30 collision-modeling arc, but at the metadata
   layer instead of the audio layer). Read-only wrt c33/c31.
3. **`M-GEN-1/palette-driven-batch-v1/palette-v2-uplift`** —
   consume Branch A's `palette_v2` if it lands, re-run the 3-salt
   batch under the v2 schema. Would require an updated rubric with
   `palette_v2`-specific determinism / provenance keys.
4. **`M-GEN-1/palette-driven-batch-v1/cross-seed`** — replay on the
   `seed_mid_50s` and `synth_060s` breadth-second-seeds instead of
   `synth_030s`, so per-stem MIDIs differ across seeds. This decouples
   the rule → audio question from the seed → audio question.
5. **Opportunistic egress retry** — `workspace/harvest_playlists.sh`
   scheduled non-blocking probe at every cycle top; two consecutive
   `media_ok=true` rows would fire the c11 armed harness and unblock
   the entire M-EAR-1 real-label branch.
6. **`_infra/build_assignment_row-signature-audit`** (upstream): the
   observation from §9 suggests a lightweight upstream fix (a
   documented contract on `build_assignment_row`'s salt-invariance
   under fixed fetchability) would make the batch-v1 mechanism
   legible in the c33 module itself, not only downstream in this
   report.

## Appendix — key artifacts

- `docs/palette_driven_batch_v1_rubric.md` (SHA `42f0bcea…`)
- `data/gen_palette_batch_v1/rubric_hash.txt`
- `data/gen_palette_batch_v1/batch_manifest.json`
- `data/gen_palette_batch_v1/summary.tsv`
- `data/gen_palette_batch_v1/spread_analysis.json`
- `data/gen_palette_batch_v1/verdict.json` (embeds rubric SHA verbatim)
- `data/gen_palette_batch_v1/anchor_preservation.json`
- `data/gen_palette_batch_v1/per_song/<0,1,2>/{assignments.jsonl, bare_combined.wav, bare_combined.wav.sha.run{1,2}, dispatch_summary.json, panel_original.tsv, panel_fluidsynth.tsv, per_stem/<stem>/{pinned_state.json, render_run{1,2}.wav.sha}}`
- `scripts/gen_palette_batch_v1/{__init__.py, sample_rule_triple.py, render_song.py, run_batch.py, spread_analysis.py}`
- `tests/test_palette_driven_batch_v1.py` (16 cases — 16/16 PASS)
- `tests/test_integration_cross_branch.py §53` (9 checks — PASS)
- `plan_of_record.md` — new row `M-GEN-1/palette-driven-batch-v1`
