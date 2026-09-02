# Final Audit — Stage 4 (verify 3 of 23)

Slice: three M-GEN-1 palette-render batch milestones. First two are
first-class negative findings (invalidated/high); third is the c36
recovery that carried the palette-arc into `PARAM_MOVES_AUDIO`.

## Slice

1. **M-GEN-1/palette-driven-batch-v1** (c34 clone-2) — invalidated/high.
2. **M-GEN-1/palette-driven-batch-v2-sampler-diversified** (c35 clone-1) — invalidated/high.
3. **M-GEN-1/palette-driven-batch-v3** (c36 clone-1) — validated/high.

All three consume the c33 palette-render machinery READ-ONLY and rest
on the c31 palette-v1 + c33 dawdreamer_state anchors. All three run on
the c33 additive-kwargs render_stem contract.

---

## 1. M-GEN-1/palette-driven-batch-v1 — CONFIRMED invalidated/high

Evidence: `data/gen_palette_batch_v1/verdict.json`.

- `verdict` = `BATCH_SPREAD_COLLAPSED`.
- `rubric_hash` = `42f0bcea…101017`, byte-equal to `rubric_hash.txt`
  (three-way chain holds).
- `distinct_bare_combined_shas` = 1 (`a8c1557c…b794`) — all 3 salts
  produced the same `bare_combined.wav`.
- `evidence.reason` = "all 3 salts yield the SAME bare_combined.wav SHA".
- Per-key IQR = 0.0 on all 4 numeric-family keys against half_c33
  thresholds (mel_l1_db half_c33=11.84, lufs_m half=3.34, rms_env
  half=0.032, centroid half=1547.3) — every `meets`=false.
- Per-salt panel triples are literally identical dicts (not just close):
  same mel_l1_db=23.678, same centroid=3094.505, same rms_env=0.0650,
  same lufs_m=6.688 across salts 0/1/2.

The finding is honest and load-bearing: it exposed that per-salt rule
selection in v1 was not diversifying rule triples enough to move audio
under the (stem, instrument)-only c33 dispatch surface. It gated
c35 clone-1's diversified-sampler attempt.

## 2. M-GEN-1/palette-driven-batch-v2-sampler-diversified — CONFIRMED invalidated/high

Evidence: `data/gen_palette_batch_v2/verdict.json`.

- `verdict` = `SPREAD_STILL_COLLAPSED`.
- `rubric_hash` = `74997302…eb6c`, byte-equal to `rubric_hash.txt`.
- Mechanism-exposing content preserved: `assignments_all_distinct` = true;
  `per_salt_rule_triples` shows 3 DISTINCT triples per salt (harmonic +
  rhythmic + arrangement rule_ids all differ between salts 0/1/2);
  `assignments_sha_per_salt` are 3 distinct SHAs.
- Despite distinct assignments, `distinct_bare_combined_shas` = 1
  (`a8c1557c…b794` — same anchor as v1). All 4 numeric keys on both
  `panel_original` and `panel_fluidsynth` have IQR = 0.0 and
  max_minus_min = 0.0 under `spread_tolerance` = 1e-06.
- `evidence.reason` = "all 3 salts yield identical bare_combined SHA".
- `anchor_preservation_unchanged` = true — no c33 or c31 anchor mutation.

The finding cleanly exposes the c33 API-surface limitation: `render_stem`
was (stem, instrument)-parameterized only and never consumed
`pinned_state`, `provenance_pointers`, or `iterated_params`. Sampler-side
diversification alone could not move audio bytes. This directly
motivated c36's additive-kwargs render_stem extension.

## 3. M-GEN-1/palette-driven-batch-v3 — CONFIRMED validated/high (PARAM_MOVES_AUDIO)

Evidence: `data/palette_render_v3/verdict.json`.

- `verdict` = `PARAM_MOVES_AUDIO`.
- `rubric_hash` = `0c4b97a2…5211`, byte-equal to `rubric_hash.txt`.
- Cross-salt distinctness: `distinct_pair_count_of_3` = 3, all three
  cross-salt `bare_combined.wav` SHAs distinct
  (`785e47c3…32bd`, `ad4d4263…c665`, `aac37ed4…e055`).
- Per-salt determinism × 2: run1 SHA == run2 SHA on every salt
  (`per_salt_determinism` = {0: true, 1: true, 2: true}).
- `backwards_compat_pass` = true (c33 anchor SHAs match under
  `parameter_dict=None`).
- `anchor_unchanged_except_render_stem_edit` = true — the one
  documented render_stem.py additive-kwargs edit is honestly declared.

This is the correct downstream lift from v1/v2's negative findings:
v3 extended the API surface via additive kwargs, restored
backwards-compat, and produced measurable per-salt audio diversity
under fluidsynth + sfizz dispatch. VST3 branches raising
`NotImplementedError` on non-None `parameter_dict` correctly keeps the
c35 anti-pattern locked.

---

## Cross-check

The v1 and v2 anchor SHA `a8c1557c…b794` is the same string in both
verdicts. Both invalidated milestones consistently name the same
byte-identical output as evidence — the two cycles independently
converged on the same collapsed anchor. No contradiction between the
two negative findings; they document one underlying constraint from
two angles (v1 = same rule triple, v2 = distinct rule triples but same
API surface).

The v3 recovery does not retroactively invalidate v1 or v2 — the two
negative findings remain load-bearing because they document the
API-surface constraint that v3 explicitly widened.

## Housekeeping

Both v1 and v2 verdicts embed `per_salt_panel_key_summaries` that are
byte-identical dicts (same mel_l1_db=23.678, centroid=3094.505,
rms_env=0.0650, lufs_m=6.688 across all three salts). This is
consistent with the "collapsed anchor" story and is the honest
per-key evidence. Not a finding.

## Verdict

3/3 CONFIRMED. No new CRITICAL or MODERATE findings this stage.
Findings appended: 3 (each is `invalidation_verified` or
`validation_verified` at severity=none).
