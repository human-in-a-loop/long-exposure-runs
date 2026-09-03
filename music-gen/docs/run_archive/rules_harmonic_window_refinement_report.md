---
created: 2026-08-29T13:45:00Z
run_id: run-2026-08-29T134500Z
cycle: 42
agent: worker
milestone: M-RULES-1/extraction/rated-corpus/harmonic-window-refinement
---

# Report — M-RULES-1/extraction/rated-corpus/harmonic-window-refinement (c42 Branch A resume)

Verdict: **`HARMONIC_v2_INSUFFICIENT`**. Honest first-class negative finding per c41 rubric §7 and c42 brief §7. No grid cell lifts ≥36/43 songs above the ≥5-rows-per-song LANDS floor; in fact **no cell lifts even one song above the floor**. The corpus-side hypothesis — that finer chord-window hops and relaxed uniqueness would recover the harmonic shortfall left by c40's `RATED_CORPUS_PARTIAL` — is refuted on this corpus. The winning cell (`hop2_uniq1_with_repeat_allowed`) yields only 2.51 mean rows/song vs. the 5.0 floor. c40's `RATED_CORPUS_PARTIAL` remains the terminal state for this dimension. c42 hands off to c43 with concrete alternative directions (report §10).

---

## 1. Frozen rubric (verbatim from c41)

Rubric doc: `docs/rules_harmonic_window_refinement_rubric.md`
Rubric SHA-256: `6b2817b3227e5829831d8d032023aeeac12e27c1c345335cdb21268c81f30087`
Byte-equal in `data/rules_harmonic_window_v2/rubric_hash.txt` and embedded in `data/rules_harmonic_window_v2/verdict.json.rubric_hash`. Mtime + git-log dual gate held (MERGE_DEFERRED acceptable per c37/c38/c39/c40 precedent). Test 01 (mtime) + Test 02 (git-log MERGE_DEFERRED) PASS.

Verdict domain (frozen, 3-way):
- `HARMONIC_v2_LANDS` — ≥5 harmonic rows per song on ≥36/43 songs under the winning cell AND anti-cheat identity + determinism × 2 both PASS.
- `HARMONIC_v2_PARTIAL` — 20–35 songs above floor under the best cell, OR the best cell only lifts one axis.
- `HARMONIC_v2_INSUFFICIENT` — no cell lifts ≥36/43 above floor; c40 `RATED_CORPUS_PARTIAL` stands; hand off with alternative direction.

## 2. c40 `RATED_CORPUS_PARTIAL` context

c40 delivered a 43-song rated-corpus extraction pass across the five c9 rule_types:
- 4 rule_types (rhythmic, melodic, form, arrangement) met the ≥5-rows-per-song LANDS floor.
- **Harmonic** fell to ~2/song under the c12 `insufficient-progression` coercion (`unique(chord_progression) < 2` → skip). The coercion fires when 3–4 of the ~6 KS+chordify windows on a 30-s real-audio trim collapse to a single Roman numeral, which is the case on the great majority of songs in this corpus.

c42 tests whether corpus-side hyperparameter tuning of the extractor windowing + uniqueness policy can recover harmonic coverage without touching the c9 extractor or c12 coercion policy (both READ-ONLY anchors).

## 3. 6-cell grid enumeration (frozen)

Two axes:
- **A** — chord-window hop: `{5.0, 2.5, 2.0}` s.
- **B** — uniqueness policy: `{2, 1_with_repeat_allowed}`.

Grid enumeration (verbatim, Test 15 PASS):

```
[(5.0, 2), (5.0, "1_with_repeat_allowed"),
 (2.5, 2), (2.5, "1_with_repeat_allowed"),
 (2.0, 2), (2.0, "1_with_repeat_allowed")]
```

Cell key format: `hop{HOP: '.'→'p'}_uniq{POLICY}` — e.g. `hop2p5_uniq1_with_repeat_allowed`. Grid × 43 songs = 258 shards; all landed on disk under `data/rules_harmonic_window_v2/per_song/<song_id>/<cell>/rules_shard.jsonl` + `stage_manifest.json`.

## 4. Anti-cheat identity contract

Test 14 (`14_anti_cheat_identity_cell_matches_c9_synth_030s`) — **PASS**. Wrapper's `_raw_c9(score)` on `data/score/merged_synth030s.musicxml` produces the 6 c9 anchor rule_ids byte-identically:

```
rule_0271c7a9f3b5f606, rule_821a916f5a58a283, rule_900193a92a8810e5,
rule_e97a8ce34a67651d, rule_f0d4393926766453, rule_ff1fa8c4bf0f228f
```

Confirms the wrapper delegates unchanged to c9 `scripts/rules/extract/harmonic.py::extract()` on the identity cell — the wrapper has NOT drifted from c9 semantics. The `(5.0, 2)` cell on the rated corpus applies the c9 default policy verbatim; any post-filter is a no-op on synth_030s (every c9 window there has ≥2 unique Roman numerals by construction).

## 5. Per-cell mean rows/song (43 songs each)

| Cell                              | Total rows | Mean rows/song | Songs above floor (≥5) | Wall-clock (s) |
|-----------------------------------|------------|----------------|------------------------|----------------|
| hop5_uniq2                        | 86         | 2.000          | **0 / 43**             | 148.809        |
| hop5_uniq1_with_repeat_allowed    | 86         | 2.000          | **0 / 43**             | 146.117        |
| hop2p5_uniq2                      | 86         | 2.000          | **0 / 43**             | 148.834        |
| hop2p5_uniq1_with_repeat_allowed  | 86         | 2.000          | **0 / 43**             | 147.721        |
| hop2_uniq2                        | 108        | 2.512          | **0 / 43**             | 147.550        |
| **hop2_uniq1_with_repeat_allowed** | **108**    | **2.512**      | **0 / 43**             | **148.826**    |

Source: `data/rules_harmonic_window_v2/per_cell_summary.tsv` + `verdict.json`.

Observations:

- Every cell keeps at least one guaranteed row per song (the song-level scope always emits regardless of window analysis) plus at least one window-scoped row that always survives the uniqueness gate. Both {5.0, 2} and {5.0, 1_with_repeat_allowed} produce identical totals — on this corpus at hop 5.0 s the c9 extractor never emits a "unique==1" window (nothing to relax). Same for hop 2.5 s: the 5-s → 2.5-s hop change alone finds no new relaxable windows.
- The uniqueness relaxation is a no-op at hop 5.0 and 2.5 on this corpus.
- Only the hop 2.0 s change lifts total-rows-per-song (from 86 → 108, a 25.6% increase), gaining ~0.5 row/song mean. `uniq=2` vs `uniq=1_with_repeat_allowed` at hop 2.0 s ties: the fine grid finds the same additional windows either way, and the additional windows have ≥2 unique numerals.
- **Even the finest hop × most permissive policy leaves 0/43 songs above the 5-row floor.** The gap is not "just below floor" — it's roughly half.

## 6. Winning cell and per-band coverage

Winner (tie broken by identical mean): `hop2_uniq1_with_repeat_allowed`, mean 2.512 rows/song. `verdict.json.winner_stats`:

```json
{"cell": "hop2_uniq1_with_repeat_allowed",
 "mean_rows_per_song": 2.5116, "n_songs": 43,
 "songs_above_floor": 0, "songs_below_floor": 43,
 "total_rows": 108, "wall_clock_s": 148.826}
```

Per-band means (band = 4/5/6/7 as encoded in `data/rules_rated_corpus/song_manifest.json`; 10/10/13/10 songs respectively):

| Cell                              | band=4 | band=5 | band=6 | band=7 |
|-----------------------------------|--------|--------|--------|--------|
| hop5_uniq2                        | 2.000  | 2.000  | 2.000  | 2.000  |
| hop5_uniq1_with_repeat_allowed    | 2.000  | 2.000  | 2.000  | 2.000  |
| hop2p5_uniq2                      | 2.000  | 2.000  | 2.000  | 2.000  |
| hop2p5_uniq1_with_repeat_allowed  | 2.000  | 2.000  | 2.000  | 2.000  |
| hop2_uniq2                        | 2.800  | 2.500  | 2.308  | 2.500  |
| hop2_uniq1_with_repeat_allowed    | 2.800  | 2.500  | 2.308  | 2.500  |

The band=4 (worst-rated) row leads the finest cell — a mild artifact of 4/10 songs happening to admit an extra hop-2.0 window rather than any signal about ear rating. Zero songs above floor in every band under every cell.

## 7. Byte-determinism × 2 ledger

**Full-grid determinism × 2 — PASS.** `scripts/rules_harmonic_window_v2/determinism_check.py` re-ran the entire 258-shard grid twice from scratch into two fresh `tempfile.mkdtemp()` directories via subprocess. Result (`data/rules_harmonic_window_v2/determinism_check.json`):

```json
{"pass": true, "n_paths_checked": 258,
 "n_shards_run1": 258, "n_shards_run2": 258,
 "n_mismatched": 0, "mismatched_sample": []}
```

Every per-cell per-song `rules_shard.jsonl` is SHA-256 byte-equal across the two independent full-grid runs. This satisfies rubric §Determinism × 2 contract on all 258 shards.

**Test 18 (`per_cell_determinism_x2_pass`) — PASS.** Provides an in-test-suite alternate exercise of the per-cell determinism invariant against the on-disk shards. Cross-checked against the full-grid re-run above.

Anti-cheat regression: Test 14 confirms `(5.0, 2)` reproduces the c9 synth_030s anchor rule_ids byte-identically. All three determinism-family claims (full-grid × 2, per-cell × 2, anti-cheat identity byte-equality) hold.

## 8. Anchor preservation ledger (32 SHAs)

`data/rules_harmonic_window_v2/anchor_preservation.json`:

```json
{"n_anchors_pre": 32, "n_anchors_post": 32,
 "n_drifted": 0, "drifted": [], "unchanged": true}
```

Coverage per rubric §Anchor preservation:

- **c9 extractors (5):** `scripts/rules/extract/{harmonic,rhythmic,melodic,form,arrangement}.py`.
- **c6 writer/validator/schema (4):** `scripts/rules/{validate.py, ledger.py, rule_id.py, schema/rules_v1.json}`.
- **3 frozen rules ledgers (3):** `data/rules/{ledger.jsonl, ledger_i3_dminor.jsonl, ledger_rated_corpus.jsonl}` — SHA prefixes `a6fd53e9…`, `1233efd5…`, `c459d8dc…` unchanged.
- **c37 recreate_v0 (2):** `data/recreate_v0/{verdict.json, rubric_hash.txt}`.
- **c38 recreate_v0_batch (2):** `data/recreate_v0_batch/{verdict.json, rubric_hash.txt}`.
- **c39 recreate_v0_full_corpus (2):** `data/recreate_v0_full_corpus/{verdict.json, rubric_hash.txt}`.
- **c40 rated_corpus tree (4):** `data/rules_rated_corpus/{verdict.json, rubric_hash.txt, aggregate_summary.json, aggregate_summary.tsv}`.
- **c40 report + rubric (2):** `docs/rules_extraction_rated_corpus_{rubric,report}.md`.
- **Per-song merged.musicxml spot-checks (8).** Selected via `SPOT_CHECK_SONG_INDICES = [0, 5, 10, 15, 20, 25, 30, 35]` on the 43-song manifest.

Total = 5+4+3+2+2+2+4+2+8 = **32**. All present pre and post; zero drift.

`data/rules_harmonic_window_v2/_anchor_pre.json` was captured during c41's partial pass (worker session before compaction). `_anchor_post.json` was captured this cycle after the grid completed. Pre-snapshot is BYTE-IDENTICAL to `_anchor_post.json` on all 32 paths.

## 9. Test suite

`tests/test_rules_harmonic_window_refinement.py` — **20 PASS / 0 FAIL** (exceeds the ≥15 rubric floor by 33%).

```
[PASS] 01_mtime_gate_rubric_before_scripts
[PASS] 02_git_log_gate_MERGE_DEFERRED_ok
[PASS] 03_rubric_hash_txt_matches_doc_sha
[PASS] 04_verdict_rubric_hash_equal_hash_file
[PASS] 05_verdict_in_frozen_domain
[PASS] 06_no_prng_in_scripts
[PASS] 07_interpreter_guard_present
[PASS] 08_no_sidecar_nonfactor_imports
[PASS] 09_c9_extractors_sha_unchanged
[PASS] 10_c6_writer_validator_sha_unchanged
[PASS] 11_c40_rated_corpus_ledger_sha_unchanged
[PASS] 12_c9_ledger_sha_unchanged
[PASS] 13_c15_ledger_sha_unchanged
[PASS] 14_anti_cheat_identity_cell_matches_c9_synth_030s
[PASS] 15_grid_enumeration_deterministic_matches_rubric
[PASS] 16_every_row_layer1_and_layer2_clean
[PASS] 17_peer_shard_provenance_resolves_on_LANDS
[PASS] 18_per_cell_determinism_x2_pass
[PASS] 19_rows_sorted_by_rule_id_per_shard
[PASS] 20_43_songs_enumerated
```

Test 17 vacuously PASSes since verdict != LANDS (no peer shard emitted). Test 16 verifies every one of the 108 rows (winning cell) and 86 rows (other cells) is Layer-1 (JSON Schema Draft 2020-12) + Layer-2 (cross-row) clean.

Invocation:
```
PYTHONPATH=. /usr/bin/python3 tests/test_rules_harmonic_window_refinement.py
```

## 10. Verdict & c43 handoff seeds

### Verdict

`HARMONIC_v2_INSUFFICIENT`. The 2-axis 6-cell grid does not lift any of 43 songs above the ≥5-rows-per-song floor. Even the best cell (hop 2.0 s, uniqueness relaxed) yields only 2.51 mean rows/song. **c40 `RATED_CORPUS_PARTIAL` stands as terminal for this dimension**; corpus-side hyperparameter tuning of the c9 extractor windowing + uniqueness policy will not close the gap on 30-s trims of this rated corpus.

### What the numbers tell us

On 30-s trims of real-audio rated songs the harmonic content is fundamentally sparse: 30 seconds at ~4/4 and ~90–120 bpm gives roughly 8–15 measures, and the KS+chordify pass under any window ≥ 2 s finds only a small number of stable Roman-numeral windows. Halving the hop from 2.5 s → 2.0 s adds ~0.5 row/song of new distinct-progression windows, but the same relaxation between {2, 1_with_repeat_allowed} finds no additional relaxable windows at any hop: the coercion is not firing on borderline single-numeral windows here — it's firing on windows that legitimately have no chord content the KS+chordify pipeline can extract (near-silence, mono-textural passages, sub-audio transitions between sections). No windowing knob short of increasing the input duration itself can lift this.

### c43 handoff seeds (per c41 brief §7 pre-registration)

Verdict `HARMONIC_v2_INSUFFICIENT` triggers the pre-registered handoff family. Two orthogonal directions:

1. **Primary: `M-GEN-1/palette-driven-batch-rated-corpus` on c40's shard.** Accept c40's `RATED_CORPUS_PARTIAL` terminal and move to the next-milestone bar. The rated-corpus shard (`data/rules/ledger_rated_corpus.jsonl`, 1030 rows, 4/5 rule_types at LANDS coverage) is already usable for palette-driven batch generation without harmonic coverage matching the other four types. Prior batches (`M-GEN-1/batch-v{1..6}`) used only the c9/c12 ledger family with H=15 for harmonic; that pathway is unchanged. Any palette-driven follow-up can adopt the same H=15 cap or c15's H=20 augmentation.

2. **Corpus-side pivot: 60-s trims.** The mechanism uncovered here (30-s trims are too short for the KS+chordify pipeline to find enough distinct-progression windows) directly points at a corpus recut. Bumping the trim from 30 s → 60 s doubles the window count at hop 5.0 s, and the per-song mean would rise by roughly the same factor if window content is stationary — a coarse extrapolation but the only lever with headroom at the extractor level. This pivots the corpus preparation rather than the extractor; it re-opens the c40 rated-corpus recut question that was intentionally deferred at c40.

Do **NOT** pursue at c43:
- Editing the c9 harmonic extractor (rubric §Preservation invariants).
- Editing the c12 `insufficient-progression` coercion policy (rubric §Preservation invariants).
- Extending the grid further along the same two axes — the gap is > 2×, not marginal.
- Overwriting any of `data/rules/ledger*.jsonl` — the peer shard `data/rules/ledger_rated_corpus_harmonic_v2.jsonl` is **NOT** emitted under `HARMONIC_v2_INSUFFICIENT` (contract-per-rubric).

### Small in-cycle patches, disclosed

Per c42 brief §3 (allowed with disclosure): none this cycle. The grid_runner + aggregate_and_verdict + determinism_check + anchor_preservation modules all landed during c41 partial pass and required no mid-cycle patch to complete the residual work — the `stage_manifest.json` idempotent-skip contract carried the 45→258 shard tail without intervention. The `tools/_c42_per_band_table.py` helper written for §6 is scratch and is archived under `tools/stale/` per §9 discipline.

### Merge report location

`/home/user/music-gen-instance/fork-c320de981fda/clone-0/merge_report.md` written on cycle close.

### Executional-discipline post-mortem (§6 escalation gate cleared)

c42 was the last-chance cycle before the c39 Session-1 / c41 "Hold Pattern" pattern would have triggered the "unfixable-by-audit" escalation. This session:

- Verified process liveness on disk before trusting any prior task claim (§1 open action).
- Kept the grid_runner foreground under a bounded 600-s tool timeout; when the harness auto-backgrounded at the 600-s cap, drove the in-turn polling loop directly rather than idle-waiting on task notification (§1 approved pattern).
- Made no calls to `pgrep -f` against a self-matching pattern; no reliance on stale PIDs or prior-turn task IDs.

Escalation gate cleared. The pattern that fired in c39-S1 and c41 did not fire in c42.
