---
created: 2026-08-29T14:32:51Z
cycle: 43
run_id: fork-c320de981fda-clone-0
agent: worker
milestone: M-GEN-1/palette-driven-batch-rated-corpus
---

# c43 Rubric — M-GEN-1/palette-driven-batch-rated-corpus

## 0. Purpose

Direct successor to c42 clone-0's VALIDATED `HARMONIC_v2_INSUFFICIENT`
finding. c40 `RATED_CORPUS_PARTIAL` is accepted as terminal for the
harmonic dimension. This cycle activates the 1030-row rated-corpus
shard in the M-GEN-1 palette-driven batch chain by applying c36 v3's
PARAM_MOVES_AUDIO pattern (4×4 SHA-256-derived `parameter_dict` × 3
salts) verbatim, with the sole substitution of the rules source
(`data/rules/ledger_rated_corpus.jsonl` in place of
`data/rules/ledger.jsonl`).

## 1. Frozen verdict domain (3-way)

The batch resolves to exactly one of:

- **`RATED_CORPUS_BATCH_LANDS`** — all of:
  1. `3/3` cross-salt `bare_combined.wav` SHAs distinct;
  2. per-salt byte-determinism × 2 PASS on every stem and on
     `bare_combined.wav`;
  3. 8-key finite panel per salt on both `panel_original` and
     `panel_fluidsynth`;
  4. `data/rules/ledger_rated_corpus.jsonl` SHA byte-equal pre/post;
  5. c40/c9/c15 rules ledgers, c33 palette_render, c31 palette anchors
     all unchanged.

- **`RATED_CORPUS_BATCH_PARTIAL`** — one of:
  1. `2/3` cross-salt distinct (one identical pair, attributed
     honestly to sfizz opcode-file rewrite absence per c36 §7 fallback
     ladder); or
  2. panel finite on only one of the two comparisons per salt.
  All other conditions from LANDS still hold.

- **`RATED_CORPUS_BATCH_FAILS`** — any of:
  1. `0/3` or `1/3` cross-salt distinct (SPREAD_STILL_COLLAPSED-family
     regression);
  2. per-salt determinism × 2 fails on any stem or combined;
  3. c40 rated-corpus shard modified pre/post;
  4. anchor SHA drift on any read-only anchor beyond the fixed set.

## 2. Rubric-hash discipline (c37/c38/c39/c40/c41/c42 precedent)

- SHA-256 of this document → `data/gen_palette_batch_rated_corpus/rubric_hash.txt` (65 B, content = hex + newline).
- `verdict.json.rubric_hash` byte-equal to the *content* of
  `rubric_hash.txt` (i.e. sha256 of this doc) — NOT to
  `sha256sum data/.../rubric_hash.txt` (per c42 gotcha #5).
- This document's mtime STRICTLY earlier than every
  `scripts/gen_palette_batch_rated_corpus/*.py` mtime (test enforced).
- git-log ordering: rubric commit before script commits.
  MERGE_DEFERRED acceptable on git-log per c38/c39/c40/c42 precedent.

## 3. Method (pinned)

- **Rules source**: `data/rules/ledger_rated_corpus.jsonl` (c40, 1030
  rows; SHA `c459d8dc1d76991f7c711509a3c686577dadb399f0763364941ac383d9674b0b`).
  Rule types considered: harmonic (86 rows), rhythmic (258 rows),
  arrangement (215 rows). melodic and form are extracted but not
  consumed by the palette (c33 assignment surface is 3-stem).
- **Sampling**: c34 clone-2 unconditioned SHA-256 tiebreak. Per
  salt s and rule_type rt, rank-0 rule_id by
  `sha256(f"{s}|{rule_id}".encode("ascii")).hexdigest()`. NO PRNG.
  NO rejection loop. NO exclusion set.
- **Stem ↔ rule_type mapping** (c36 verbatim): harmonic→other,
  rhythmic→drums, arrangement→bass.
- **Per-stem instrument dispatch** (c36 verbatim): drums=fluidsynth_gm,
  bass=sfizz, other=sfizz. VST3 branches (surge_xt, dexed) are
  test-enforced to raise `NotImplementedError` on non-None
  `parameter_dict` (c35 anti-pattern locked; not exercised this cycle).
- **`parameter_dict` derivation**: for each (rule_id, instrument) and
  each param_name in the frozen 4-entry table below, pick index
  `int.from_bytes(sha256(f"{rule_id}|{param_name}".encode("utf-8")).digest()[:4], "big") % 4`.
- **Frozen 4×4 tables (verbatim c36 v3)**:

  ```
  FLUIDSYNTH_TABLE:
    chorus_level:     [0.3, 0.5, 0.7, 0.9]
    reverb_level:     [0.2, 0.4, 0.6, 0.8]
    reverb_room_size: [0.4, 0.5, 0.6, 0.7]
    gain:             [0.6, 0.75, 0.9, 1.05]

  SFIZZ_TABLE:
    master_volume:         [-3.0, -1.5, 0.0, 1.5]
    master_pitch_offset:   [-2.0, 0.0, 2.0, 4.0]
    envelope_attack_mult:  [0.5, 0.75, 1.0, 1.25]
    envelope_release_mult: [0.75, 1.0, 1.25, 1.5]
  ```

  sfizz threads only `master_volume` in-band (post-render scalar);
  other keys are recorded for provenance per c36 v3 fallback ladder.
- **Salts**: {0, 1, 2}. Do NOT extend to 0..7 or 8×8 param — deferred
  to c44 per §7.
- **Determinism**: each salt rendered twice into fresh
  `tempfile.mkdtemp()` dirs; SHA-256 equality asserted per-stem and on
  `bare_combined.wav`.
- **Panels**: `M-TEX-1/panel` measured per salt against (a) c9
  `data/tex/renders/synth_030s/original.wav` and (b) c9
  `data/tex/renders/synth_030s/bare_midi.wav`.

## 4. Preservation invariants (any drift → FAILS)

- `data/rules/ledger_rated_corpus.jsonl` — SHA byte-equal pre/post.
- `data/rules/ledger.jsonl` — SHA byte-equal pre/post.
- `data/rules/ledger_i3_dminor.jsonl` — SHA byte-equal pre/post.
- `data/rules/ledger_rated_corpus_harmonic_v2.jsonl` — remains ABSENT
  per c42 INSUFFICIENT verdict.
- c33 `scripts/palette_render/{__init__.py, build_assignments.py,
  render_stem.py, run_all.py}` — READ-ONLY. `render_stem.py` carries
  the c36 additive-kwargs edit already; no further edit this cycle.
- c31 `scripts/palette/*` + schema — READ-ONLY.
- c31 `scripts/palette_probe/*` — READ-ONLY.
- c33 `scripts/dawdreamer_state/*` — READ-ONLY.
- c37/c38/c39 recreate trees — READ-ONLY.
- c40/c42 rubric docs + reports — READ-ONLY.
- c9 effects chain `scripts/tex/render_effects_layered.py` — NOT
  imported (test enforced).
- α = `0.7469387071101908` — not touched.
- NO PRNG anywhere (AST + regex grep test enforced).
- `/usr/bin/python3` interpreter guard on every script.
- No `sidecar_nonfactor` imports (test enforced).
- Never delete files; scratch → `tools/stale/`.

## 5. Anti-patterns explicitly locked (c42 audit-carried interdictions)

- Editing c9 harmonic extractor / c12 coercion policy — forbidden.
- Extending the c42 grid (hop or uniqueness axes) — forbidden.
- Modifying any `data/rules/ledger*.jsonl` — forbidden.
- The Hold Pattern (c39 Session-1, c41): no background-job-plus-await.
  Foreground OR foreground-Monitor-poll only.
- The Assumption Pattern: verify liveness on disk before trusting any
  prior task claim.
- Importing `scripts.tex.render_effects_layered`, `scripts/gen/*`
  (c15 i4_stratified), `scripts/ear/*`,
  `scripts/classifier/sidecar_nonfactor`, c22/c23/c25 harnesses.
- Emitting any `M-EAR-1/*` or `M-RULES-1/*` events this cycle.
  Substantive milestone strictly
  `M-GEN-1/palette-driven-batch-rated-corpus/*`.
- VST3 `parameter_dict` non-None — locked; VST3 branches raise
  `NotImplementedError` when a non-None `parameter_dict` reaches them.
- 8×8 param_dict expansion (c37 clone-2 pattern) — deferred to c44 IFF
  c43 verdict is PARTIAL.
- Additional salts (>3) — deferred.

## 6. Success bar (auditor will verify)

12 gates:

1. Rubric committed BEFORE any script (mtime + git-log
   MERGE_DEFERRED acceptable).
2. `verdict.json.rubric_hash` byte-equal to `rubric_hash.txt`
   content byte-equal to sha256(this doc).
3. 3 salts × 2 determinism runs = 6 SHA pairs; per-salt equality
   PASS on both combined and every per-stem.
4. Cross-salt `bare_combined.wav` SHAs: 3/3 distinct → LANDS;
   2/3 → PARTIAL; ≤1/3 → FAILS.
5. 8-key finite panel per salt on both `panel_original` and
   `panel_fluidsynth`.
6. Anchor preservation ≥30 SHAs pre==post (target 32 for c42
   parity).
7. c40 rated-corpus shard SHA byte-equal pre/post.
8. c9 + c15 shards byte-equal; c42-absent shard remains absent.
9. ≥15 tests green (target 20).
10. Report with all 10 sections + honest verdict + §10 handoff.
11. 10 ledger events emitted AFTER artifacts land under
    `M-GEN-1/palette-driven-batch-rated-corpus/*` (unsuffixed per c32)
    and `_run|_archive|_infra/…-clone-0`.
12. `promise_check` 0-ERROR; no new WARN.

## 7. c44 handoff seeds (pre-registered by verdict)

- **If LANDS**: primary c44 = expand salt range 0..7 (c37 clone-2
  pattern) OR 8×8 param_dict table AND/OR M-TEX-1/panel comparison vs
  c34/c35/c36/c37 palette-batches on 76-row baseline.
- **If PARTIAL**: primary c44 = 8×8 param_dict expansion (c37
  verbatim). Alternate = attribute per-rule_type contribution to
  sampler collapse.
- **If FAILS**: primary c44 = corpus-side 60-s trim recut per c42 §7
  alternate. Alternate = accept as terminal and re-scope G5 to
  c9+c12+c15 synthetic ledger stack.
- Standing tickets carried forward: `_infra/emitter-idempotence-guard-clone-*`,
  `_manager/effects-chain-band-selectivity`, band-6 Tom Misch focused
  rerun, c38 clone-1 REDEFINED_GAP + normalizer-v2 REFUTED, c37 VST3
  activation gated by c36 MIXED, `_infra/foreground-execution-enforcement-clone-*`,
  egress retry.

## 8. Test-list (frozen, ≥20 target)

1. mtime gate: rubric mtime < every scripts/gen_palette_batch_rated_corpus/*.py mtime.
2. git-log gate: rubric committed before scripts (MERGE_DEFERRED
   acceptable, verified via `git log --diff-filter=A --format=%H %ct` shape).
3. `rubric_hash.txt` content byte-equals sha256(this doc).
4. `verdict.json.rubric_hash` byte-equal to `rubric_hash.txt` content.
5. verdict ∈ frozen domain.
6. NO PRNG grep (regex `\brandom\b|\bnumpy\.random\b|\btorch\.manual_seed\b`).
7. `/usr/bin/python3` interpreter guard on every script.
8. NO `sidecar_nonfactor` import (grep + AST).
9. c33 palette-render anchors (mtime + SHA) unchanged.
10. c31 palette-v1 anchors unchanged.
11. c40 `data/rules/ledger_rated_corpus.jsonl` SHA byte-equal pre/post.
12. c9 `data/rules/ledger.jsonl` SHA byte-equal pre/post.
13. c15 `data/rules/ledger_i3_dminor.jsonl` SHA byte-equal pre/post.
14. c42 `data/rules/ledger_rated_corpus_harmonic_v2.jsonl` remains ABSENT.
15. Per-salt determinism × 2 SHA equality PASS on `bare_combined.wav`.
16. Cross-salt `bare_combined.wav` SHAs distinct (3/3 for LANDS).
17. 8-key finite panel per salt on both `panel_original` and
    `panel_fluidsynth`.
18. Anchor preservation ≥30 SHAs pre==post.
19. Rules-source pin in `batch_manifest.json` matches c40 anchor SHA.
20. c9 effects chain `scripts.tex.render_effects_layered` NOT imported
    (grep + AST).

## 9. Ledger event contract

Six substantive under `M-GEN-1/palette-driven-batch-rated-corpus/*`
(unsuffixed per c32):

- `rubric-committed`
- `songs-sampled`
- `parameter-dicts-derived`
- `batch-rendered`
- `spread-analyzed`
- `verdict-emitted`

Four housekeeping under auto-applied `-clone-0` suffix:

- `_run/cycle_43_launched-clone-0`
- `_run/cycle_43_closed-clone-0`
- `_archive/cycle-43-scratch-clone-0`
- `_infra/adopt-cycle43-tests-clone-0`

Every event: `status=validated`, nested
`confidence={level, rationale, assessor}`, `narrative` (NOT `summary`),
pinned `run_id=fork-c320de981fda-clone-0`, auto-derived UUID5
`event_id`. Emitter idempotence rides on writer-side
`LedgerAppendError: duplicate event_id`.

## 10. Rubric SHA-256

The 65-byte `data/gen_palette_batch_rated_corpus/rubric_hash.txt` is
sha256(this document) + newline, computed after this document is
frozen. `verdict.json.rubric_hash` echoes that SHA content.
