---
created: 2026-08-29T05:00:00Z
cycle: 34
run_id: run-2026-08-28T040704Z
agent: worker
milestone: M-GEN-1/palette-driven-batch-v1
---

# M-GEN-1/palette-driven-batch-v1 — Frozen 3-verdict rubric

**Cycle 34, Branch C (clone-2, fork 43802db1a81c).**
**Locked BEFORE any script under `scripts/gen_palette_batch_v1/` lands.**
**Rubric SHA-256 is recorded in `data/gen_palette_batch_v1/rubric_hash.txt`
and embedded verbatim in `data/gen_palette_batch_v1/verdict.json` under
key `rubric_hash`.**

## Scope

A 3-song batch (salts 0, 1, 2), each song rendered through the c33
palette-render pipeline VERBATIM. Per-salt rule triple is chosen by
SHA-256 tiebreak on `sha256(f"{salt}|{rule_id}".encode())` over
`data/rules/ledger.jsonl` across `{harmonic, rhythmic, arrangement}`
rule_types (rank 0 wins). No PRNG. No rejection loop. No exclusion
set.

Per song: assignments built via `scripts.palette_render.build_assignments`
with the salted rule_ids as `provenance_pointers`; per-stem render via
`scripts.palette_render.render_stem`; two independent temp-dir runs;
SHA-256 equality on `bare_combined.wav` and every per-stem WAV; panel
measurement of `(original_synth_030s, palette_bare)` and
`(c9_fluidsynth_only_bare, palette_bare)`.

## Numeric-family panel keys (4)

`mel_l1_db`, `spectral_centroid_rmse_hz`, `rms_env_rmse`, `lufs_m_rmse_lu`.

## c33 single-seed reference deltas (for the "≥ half" test)

Sourced from `data/palette_render/panel_fluidsynth_vs_palette.tsv`
(the true "did the palette add anything?" comparison, c33 verdict
PALETTE_MOVES_PANEL):

| Key                          | c33 value | Half |
|------------------------------|-----------|------|
| `mel_l1_db`                  | 23.6785   | 11.8393 |
| `spectral_centroid_rmse_hz`  | 3094.5055 | 1547.2527 |
| `rms_env_rmse`               | 0.06499   | 0.03249 |
| `lufs_m_rmse_lu`             | 6.6885    | 3.3443 |

## Verdicts

### BATCH_SPREAD_EXPECTED

BOTH:

1. The 3 salts produce **≥ 2 distinct** `bare_combined.wav` SHA-256
   values, AND
2. The per-key **inter-quartile range** across the 3 salts is
   **≥ half** the c33 single-seed reference delta for **at least one**
   of the 4 numeric-family panel keys (on `panel_fluidsynth_vs_palette`).

Interpretation: SHA-tiebreak rule-triple selection produced enough
rule-space diversity to move the panel measurably per salt.

### BATCH_SPREAD_COLLAPSED

**All 3 salts yield the SAME `bare_combined.wav` SHA-256.**

Interpretation: rule-triple selection degenerated relative to the
palette-render dispatch — either the SHA-tiebreak sort put the same
three rule_ids at rank 0 for every salt, OR the palette-render output
is content-invariant across salts because the rule_ids drive only
metadata (`provenance_pointers`, `assignment_id`) and not audio
dispatch (which is fixed per stem: drums→fluidsynth_gm,
bass/other→sfizz|fluidsynth_gm depending on SFZ fetchability).

**First-class negative finding.** The report MUST expose the mechanism.
Do NOT retry with different salt ranges. Do NOT change the palette
schema. Escalate to the next research cycle for a follow-up milestone
that closes the observed rule→audio pathway gap (candidates: palette-
v2 uplift once Branch A lands; a `rule_type=arrangement`-driven
per-stem SFZ selection that reads the arrangement rule's density/entry
info).

### BATCH_FAILS

ANY of the following:

- Any per-salt byte-determinism check fails (`bare_combined.wav.sha.run1
  ≠ .run2` for any salt, OR any per-stem `render_run1.wav.sha ≠
  .run2.sha`).
- Any per-salt panel is not 8-key finite (missing key, NaN, or ±inf on
  any numeric-family key of either TSV).
- Any assignment row rejects `scripts.palette.validate.validate_row`.

## Exhaustiveness

The verdict function evaluates:

1. **BATCH_FAILS** gate first.
2. Then **BATCH_SPREAD_EXPECTED** vs **BATCH_SPREAD_COLLAPSED** by
   the SHA-distinctness / IQR-threshold test. If the 3 salts produce a
   mixture of SHAs (e.g. `{shaA, shaA, shaB}`) that is neither "all
   same" nor "all different" AND no numeric-family IQR meets the
   half-of-c33 bar, the verdict is BATCH_SPREAD_COLLAPSED (partial
   collapse — the mechanism has not been broken enough to move the
   panel). The test suite rejects a mixed SHA distribution that would
   suggest non-determinism drift (i.e. two runs of the SAME salt
   producing different SHAs) — that is a byte-determinism failure and
   is caught by BATCH_FAILS.

Every outcome maps to exactly one verdict.

## Post-cycle discipline

- The rubric is FROZEN: its SHA-256 is recorded in
  `data/gen_palette_batch_v1/rubric_hash.txt` and embedded verbatim
  in `data/gen_palette_batch_v1/verdict.json.rubric_hash`. A test
  asserts byte equality between the two.
- The rubric MUST NOT be edited retroactively. If a follow-up cycle
  proposes a different threshold or an additional verdict, that is a
  new peer sub-milestone with its own rubric.
- The M-GEN-1 verdict roll-up event carries `status = validated` on
  either SPREAD outcome (they are both legitimate findings under the
  frozen rubric) and `status = invalidated` on BATCH_FAILS.
