---
created: 2026-08-29T15:10:00Z
cycle: 44
run_id: fork-c320de981fda-clone-0
agent: worker
milestone: M-GEN-1/palette-driven-batch-rated-corpus
---

# M-GEN-1/palette-driven-batch-rated-corpus — c44 report

## §1. Purpose and rubric

Direct successor to c40 `RATED_CORPUS_PARTIAL` (harmonic dimension
terminal at 30-s trims; other four rule_types LANDS) and c42
`HARMONIC_v2_INSUFFICIENT` (harmonic-window refinement grid refuted
across 6 cells). This cycle activates the c33 palette-render machinery
in the M-GEN-1 batch chain for the first time, sourcing rule triples
from the c40 rated-corpus shard (`data/rules/ledger_rated_corpus.jsonl`,
1030 rows) instead of the c9+c12 primary shard.

c44 is a retry of c43, which failed at CLI startup with empty stdout
(`Failed to parse CLI JSON output`). The heartbeat probes in §10
preempted a recurrence.

Frozen 3-verdict rubric (committed BEFORE any script per §5):

- `RATED_CORPUS_BATCH_LANDS` — 3/3 cross-salt distinct AND per-salt
  determinism × 2 PASS AND 8-key finite panel per salt on both
  comparisons AND c40 shard byte-equal pre/post.
- `RATED_CORPUS_BATCH_PARTIAL` — 2/3 distinct OR panel finite on only
  one of two comparisons per salt.
- `RATED_CORPUS_BATCH_FAILS` — ≤1/3 distinct OR determinism fails OR
  c40 shard modified pre/post.

Rubric doc SHA-256:
`6823cdf280435088a555c2df81430dcf17a9fd74c8da92440f4db7b64fd98875`.
`data/gen_palette_batch_rated_corpus/rubric_hash.txt` and
`verdict.json.rubric_hash` are three-way byte-equal (test_02, test_03).

## §2. Verdict

**`RATED_CORPUS_BATCH_LANDS`.**

All four rubric gates cleared:

- Cross-salt bare_combined distinct: **3/3** (§6).
- Per-salt byte-determinism × 2: **3/3 PASS** (§6).
- 8-key finite panel per salt on both `panel_original` and
  `panel_fluidsynth`: **6/6 PASS** (§7).
- c40 rated-corpus shard SHA byte-equal pre/post:
  `c459d8dc1d76991f…` unchanged (§8).

## §3. Scope inheritance and pattern match

Follows c34 clone-2 `M-GEN-1/palette-driven-batch-v1` scaffolding
verbatim. Only substantive substitutions:

1. Rules source: `data/rules/ledger_rated_corpus.jsonl` (c40, 1030
   rows) in place of `data/rules/ledger.jsonl` (76 rows).
2. Per-salt `parameter_dict` threaded per c36 clone-1 `PARAM_MOVES_AUDIO`
   pattern (4×4 SHA-derived table via
   `scripts/gen_palette_batch_rated_corpus/derive_parameter_dict.py`).
3. Dispatch: fluidsynth_gm for drums, sfizz for bass and other. No
   VST3. `render_stem` non-None `parameter_dict` is threaded per c36
   additive-kwargs edit.

The dispatch pins ensure the c35-A / c36-refuted VST3 nondeterminism
surface is not entered — c33 `render_stem` raises `NotImplementedError`
if a VST3 branch receives non-None `parameter_dict` (see test_09).

## §4. Rules-source characterization

- Path: `data/rules/ledger_rated_corpus.jsonl`
- SHA-256 (pre): `c459d8dc1d76991f…` (byte-identical post-run)
- 1030 rows; rule_type distribution accepted from c40 as terminal for
  harmonic (86 rows, PARTIAL) and LANDS for the other four
  (rhythmic/melodic/form/arrangement).

Per-salt rule triples (arrangement / harmonic / rhythmic, SHA-256
tiebreak over `(salt, rule_id)` pairs, no PRNG):

| salt | arrangement          | harmonic             | rhythmic             |
|------|----------------------|----------------------|----------------------|
| 0    | rule_4ad6d647a1f8755f | rule_2ab97a4baf2dcb9d | rule_16bbb68e8f438756 |
| 1    | rule_dbeba19caeb15f15 | rule_bd98d7e32dcfc4b3 | rule_659d2a931f88ad6b |
| 2    | rule_b03487b4e3df13ad | rule_c05bc9ac7d0e8e0f | rule_4b2bc4fd5d5bb06c |

Per-salt assignments.jsonl SHA-256 (first 16 hex):

| salt | assignments SHA |
|------|-----------------|
| 0    | `6851b9cf61fb6daa…` |
| 1    | `f84f8ca4f934b4b3…` |
| 2    | `de96312e8810b4cc…` |

Three distinct per-salt assignments — the sampler diversifies across
the 1030-row shard, ruling out the c34-clone-2 `BATCH_SPREAD_COLLAPSED`
sampler collapse.

## §5. Rubric-first discipline

Rubric doc mtime and SHA-256 landed **before** any file under
`scripts/gen_palette_batch_rated_corpus/`. Verified by test_02
(SHA identity) and test_06 (mtime ordering). git-log ordering
`MERGE_DEFERRED` acceptable per c38–c42 precedent (workspace sandbox
does not permit direct writes under a git-tracked branch of
`/home/user/music-gen-instance/…`).

## §6. Byte-determinism and cross-salt inequality

Two independent fresh-`tempfile.mkdtemp()` runs per salt; SHA-256
on final `bare_combined.wav`:

| salt | run1 SHA (first 16 hex) | run2 SHA (first 16 hex) | equal |
|------|-------------------------|-------------------------|-------|
| 0    | `b960d84e48cecbe3…`     | `b960d84e48cecbe3…`     | ✓     |
| 1    | `abc7a214ff394817…`     | `abc7a214ff394817…`     | ✓     |
| 2    | `4fcc4119277ec77b…`     | `4fcc4119277ec77b…`     | ✓     |

Cross-salt pairwise inequality (all 3 pairs distinct):

| pair (a,b) | distinct |
|------------|----------|
| (0,1)      | ✓        |
| (0,2)      | ✓        |
| (1,2)      | ✓        |

## §7. Panel measurement (M-TEX-1/panel per salt × 2 comparisons)

Per-salt 4 numeric keys (mel_l1_db / spectral_centroid_rmse_hz /
rms_env_rmse / lufs_m_rmse_lu) × 2 comparisons (original,
c9-fluidsynth-bare). All 6 cells return finite 8-key panels.

Panel spread across 3 salts (from
`data/gen_palette_batch_rated_corpus/spread_analysis.json`):

**panel_original (rated corpus original synth_030s vs palette-bare):**

| key                       | max − min | IQR (p75−p25) |
|---------------------------|-----------|---------------|
| mel_l1_db                 |    1.969  |    0.985      |
| spectral_centroid_rmse_hz |   67.091  |   33.546      |
| rms_env_rmse              |    0.0245 |    0.0122     |
| lufs_m_rmse_lu            |    1.781  |    0.891      |

**panel_fluidsynth (c9 fluidsynth-only bare vs palette-bare):**

| key                       | max − min | IQR (p75−p25) |
|---------------------------|-----------|---------------|
| mel_l1_db                 |    2.136  |    1.068      |
| spectral_centroid_rmse_hz |  148.730  |   74.365      |
| rms_env_rmse              |    0.0263 |    0.0131     |
| lufs_m_rmse_lu            |    1.718  |    0.859      |

The panel produces detectable per-salt spread on both comparisons,
consistent with c36 `PARAM_MOVES_AUDIO` on the smaller shard. The
palette moves audio bytes across salts on the rated-corpus rule triples.

## §8. Anchor preservation

Pre and post snapshots of 34 anchor files (33 present-files +
1 absent-check for c42 `ledger_rated_corpus_harmonic_v2.jsonl`
which remains absent). Categories:

- **c33 palette_render** (4 files including c36 additive-kwargs edit).
- **c31 palette_v1** (5 files: schema, validate, provenance, __init__,
  YAML mirror).
- **c31 palette_probe** (6 files).
- **c33 dawdreamer_state P1** (6 files).
- **Rules ledgers**: c9+c12 primary, c15 i3_dminor, c40 rated_corpus
  (3 files).
- **c37 recreate_v0 rubric_hash** + c38 recreate_v0_batch rubric_hash +
  c39 recreate_v0_full_corpus rubric_hash + c40
  rules_rated_corpus rubric_hash + c42 rules_harmonic_window_v2
  rubric_hash (5 files).
- **Report docs** (c39 full-corpus, c40 rules_rated_corpus, c42
  harmonic_window) (3 files).
- **c9 effects chain** (`scripts/tex/render_effects_layered.py`,
  SHA-tracked, NOT imported — grep-verified).
- **c42-absent shard** (`data/rules/ledger_rated_corpus_harmonic_v2.jsonl`,
  invariant `absent`).

`anchor_preservation.json.unchanged=true`; `drift_rows=[]`.

## §9. Test suite

`tests/test_palette_driven_batch_rated_corpus.py` — 20 cases across
five families (A rubric+hash 3, B scaffold+guards 4, C anti-patterns 4,
D artifacts+determinism 5, E verdict+anchor 4). **20/20 PASS.**

## §10. Retry-of-c43 discipline + operational notes

**Heartbeat probes fired before any real work** per Correction 2 of the
c44 brief (preempting the c43 CLI-startup-silence pattern):

- `echo "worker c44 alive"` → stdout OK.
- `/usr/bin/python3 -c "print('py alive')"` → stdout OK.
- `PYTHONPATH=. /usr/bin/python3 -c "import scripts.palette_render;
  print('palette_render importable')"` → stdout OK.

**Foreground-only execution.** No Monitor polling, no background jobs,
no waits. Run wall-clock: ~90 s for 6 fresh-tempdir renders + panel
measurement + verdict assembly.

**No PRNG anywhere.** SHA-256 tiebreak throughout (test_08 AST-grep
clean).

**No `sidecar_nonfactor` imports** (test_07).

**No VST3 branch entered** — dispatch map contains only
`{fluidsynth, sfizz, fluidsynth_gm}` (test_09). c33 `render_stem`
would `raise NotImplementedError` on any VST3 dispatch with non-None
`parameter_dict` — this branch remains locked out per c35-A / c36
anti-patterns.

**Merge report** is written to
`tools/stale/c44_clone0_merge_report_draft.md` (workspace sandbox
required the fallback per c40/c41/c42/c43 precedent).

**c45 handoff (verdict-branched, per c43 §7):** since verdict is
`RATED_CORPUS_BATCH_LANDS`, primary c45 candidate is 8-salt expansion
(c37 clone-2 pattern) OR 8×8 param_dict OR cross-batch heuristic
+ M-TEX-1/panel comparison vs c34–c37 palette-batches.
