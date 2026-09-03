---
created: 2026-08-29T12:26:21Z
run_id: run-2026-08-29T122621Z
cycle: 40
agent: worker
milestone: M-RULES-1/extraction/rated-corpus
verdict: RATED_CORPUS_PARTIAL
rubric_hash: ed572704f205a723a9bb6e2f8b7a5d122e9aa186af6a00a05a60a6e59013f1c3
---

# Report — M-RULES-1/extraction/rated-corpus (c40 Branch A)

**Verdict:** `RATED_CORPUS_PARTIAL`
**Rubric hash:** `ed572704f205a723a9bb6e2f8b7a5d122e9aa186af6a00a05a60a6e59013f1c3` (embedded byte-equal in `verdict.json.rubric_hash`).

**Headline:** 43/43 rated-corpus songs cleanly extracted, **1030 valid rule rows** appended to the new peer shard `data/rules/ledger_rated_corpus.jsonl`, byte-determinism × 2 PASS, 31/31 read-only anchors byte-unchanged, 100 % provenance-pointer resolvability. The verdict is `PARTIAL` (not `LANDS`) for one specific reason: the frozen c9 harmonic extractor's `insufficient-progression` coercion — a bug-free but conservative Krumhansl-Schmuckler-plus-`chordify()` filter that drops windows with fewer than 2 distinct Roman-numeral figures — reduces harmonic rows to a per-song mean of 2.0 on real audio, falling below the rubric's strict `≥5-per-rule_type-per-song` LANDS floor on all 43 songs. The other four rule types (arrangement, form, melodic, rhythmic) clear ≥5 rows/song on 43/43 songs. Report §9 discloses the shortfall honestly per rubric.

## §1 Frozen rubric verbatim

Rubric source: `docs/rules_extraction_rated_corpus_rubric.md` (SHA-256 `ed572704…f1c3`, mtime `1788006425.30`).

Verdict domain:

- **`RATED_CORPUS_LANDS`** — ≥5 rule rows per rule_type × ≥36 of 43 songs = ≥900 new validated rows appended to `data/rules/ledger_rated_corpus.jsonl`; every row Layer-1 (JSON-Schema draft 2020-12) + Layer-2 (cross-row) clean; content-derived `rule_id` reproduces byte-identically across two independent runs; every `provenance_pointers` entry resolves to a real per-song merged.musicxml element or transcription event id.
- **`RATED_CORPUS_PARTIAL`** — 20–35 of 43 songs cleanly extracted, OR one or more rule_types fall below the ≥5-rows-per-song floor on >5 songs. Report §4 (per-song table) and §5 (per-band cross-tab) MUST honestly disclose which songs/rule_types shortfall.
- **`RATED_CORPUS_FAILS`** — <20 songs cleanly extracted, OR determinism × 2 fails, OR any read-only anchor drifts.

Contracts: rubric-hash discipline, determinism × 2, provenance-pointer resolvability, anchor preservation on 30+ SHAs, ≥15 tests. Full text at the source doc.

## §2 Corpus enumeration (43 songs, SHA-256 tiebreak order)

- **1 song** from c37 clone-0 (`data/recreate_v0/per_stage/06_score/merged.musicxml`)
- **5 songs** from c38 clone-2 (`data/recreate_v0_batch/per_song/<band>/<sha16>/per_stage/06_score/merged.musicxml`)
- **37 songs** from c39 clone-0 (`data/recreate_v0_full_corpus/per_song/<band>/<sha16>/per_stage/06_score/merged.musicxml`)

song_id = full SHA-256 of the source audio file (from each cycle's chosen_songs manifest). Tiebreak order = ascending song_id. Full manifest at `data/rules_rated_corpus/song_manifest.json` — 43 entries, 0 missing on disk.

Per-band population (source-of-truth: `data/rules_rated_corpus/per_band_summary.json`):

| band | songs |
|-----:|------:|
| 4    | 10    |
| 5    | 10    |
| 6    | 13    |
| 7    | 10    |
| **total** | **43** |

## §3 Extractor invocation methodology

Read-only import of the frozen c9 extractors (`scripts/rules/extract/{harmonic,rhythmic,melodic,form,arrangement}.py`) via the c12 `set_extraction_context(seed_name, score_path, bp_dir)` pattern already used by `scripts/rules/extract/breadth_seeds.py`. Per song:

1. `set_extraction_context("rated_corpus::<song_id>", merged.musicxml, 05_basic_pitch/)`.
2. `music21.converter.parse(merged.musicxml)` → `music21.stream.Score`.
3. For each rule_type in `(harmonic, rhythmic, melodic, form, arrangement)`, call `mod.extract(score, tempo_bpm=120.0)`.
4. Apply c12 `_coerce_row_or_skip` policy inline (insufficient-progression, all-rest-pattern, no_pitched_notes, no_rows_after_coercion), record each `null-with-reason` in `per_type_nulls`.
5. Decorate each surviving candidate with the c9 `_finish` metadata (`event_type=rule`, `schema_v=1`, `ts=FIXED_TS`, `extractor`, `extractor_version`, content-derived `rule_id`, `event_id`).
6. Layer-1 (JSON-Schema) + Layer-2 (cross-row) validate each row via c6 `validate_row`; drop invalid rows into `null-with-reason: validation_failed` for full-batch revalidation.
7. Write `per_song/<song_id>/rules_shard.jsonl` (rows sorted by `rule_id`) and `per_song/<song_id>/stage_manifest.json` (records `n_rows`, `per_type_counts`, `per_type_nulls`, `wall_clock_s`, source paths).

Aggregation: `scripts/rules_rated_corpus/aggregate_and_append.py` collects all 43 shards, revalidates the full batch with c6 `validate_batch`, deduplicates any inter-song rule_id collisions by keeping the lowest-canonical-index song, and appends to the DEDICATED peer shard `data/rules/ledger_rated_corpus.jsonl` via c6 `write_rule` (append-only, fsynced, Layer-1+Layer-2 at write time). **The c9 synth ledger `data/rules/ledger.jsonl` is never modified** — c26/c27/c28/c29/c30 canonical-aggregate-SHA anchors preserved.

Foreground execution end-to-end (music21 + pure-Python; no torch, no VST, no DAW). Full pipeline wall time on one machine: ~110 s for the canonical extraction run, ~360 s for the determinism-check × 2 (two additional independent temp-dir runs). Per-song median wall_clock_s: 3.0 s (range 0.36–10.0 s).

## §4 Per-song extraction summary

Full details at `data/rules_rated_corpus/verdict.json.per_song` (43 rows). Summary:

| statistic | value |
|-----------|------:|
| songs cleanly extracted (n_rows > 0) | 43/43 |
| songs meeting strict ≥5-per-type floor on all 5 rule_types | 0/43 |
| median rows/song | 24 |
| range rows/song | 23–24 |
| songs with 24 rows | 41/43 |
| songs with 23 rows | 2/43 (band-7 `b8a030a4264a…`, band-6 `f1cfe4855364ea9b`) |
| n_duplicates_dropped (inter-song rule_id collisions) | 0 |

Per-rule_type row counts, aggregated across all 43 songs (source-of-truth: `verdict.json.per_type_counts_aggregate`):

| rule_type   | rows | per-song mean | meets ≥5-per-song on |
|-------------|-----:|--------------:|----------------------|
| arrangement | 215  | 5.0           | 43/43                |
| form        | 215  | 5.0           | 43/43                |
| harmonic    |  86  | 2.0           | **0/43** ← shortfall |
| melodic     | 256  | 5.95          | 43/43                |
| rhythmic    | 258  | 6.0           | 43/43                |
| **total**   |**1030**|              |                      |

**Harmonic shortfall root cause.** The c9 harmonic extractor emits at most 6 candidate rows per song (1 song-level + 5 window-scoped). On real-audio-derived scores, the c12 `insufficient-progression` coercion (`unique(chord_progression) < 2` → skip) fires on 4 of the 6 window scopes for the median song, leaving 2 harmonic rows/song. This is faithful behavior of the frozen extractor: KS analysis on 30 s trims often yields a single key and only 1–2 distinct Roman numerals in a 6 s window. The rubric's `PARTIAL` OR-clause (`one or more rule_types fall below the ≥5-rows-per-song floor on >5 songs`) fires accordingly.

The four non-harmonic rule_types all meet or exceed the ≥5 floor on 43/43 songs — the shortfall is one-dimensional, not a systemic pipeline defect.

## §5 Per-band cross-tabulation (rule_type × band)

Source-of-truth: `data/rules_rated_corpus/per_band_summary.json`.

| band | songs | arrangement | form | harmonic | melodic | rhythmic | total |
|-----:|------:|------------:|-----:|---------:|--------:|---------:|------:|
| 4    | 10    | 50          | 50   | 20       | 60      | 60       | 240   |
| 5    | 10    | 50          | 50   | 20       | 60      | 60       | 240   |
| 6    | 13    | 65          | 65   | 26       | 77      | 78       | 311   |
| 7    | 10    | 50          | 50   | 20       | 59      | 60       | 239   |

Per-song mean is band-flat: 24.0 rows/song in bands 4/5/7, 23.92 in band 6. No cross-band pattern in extraction yield.

## §6 Byte-determinism × 2 ledger

Source-of-truth: `data/rules_rated_corpus/determinism_check.json`.

Two independent full-pipeline runs into `tempfile.mkdtemp()`-prefixed directories (`/tmp/c40_det1_*` and `/tmp/c40_det2_*`), fresh per song. Each run: per-song extraction across all 43 songs + aggregate to a temp shard.

| SHA-256 target | run 1 | run 2 | equal |
|----------------|-------|-------|-------|
| aggregate `ledger_rated_corpus.jsonl` canonical-sort SHA | `<see JSON>` | `<see JSON>` | **YES** |
| all 43 per-song `rules_shard.jsonl` files | 43/43 | 43/43 | **43/43 YES** |
| n mismatches | — | — | 0 |

`shards_canonical_sha_equal = true`; `per_song_shards_equal = true`; `n_per_song_pairs = 43`; `n_per_song_mismatches = 0`.

## §7 Anchor preservation ledger (31 anchors, all unchanged)

Source-of-truth: `data/rules_rated_corpus/anchor_preservation.json`. Pre-snapshot taken before `extract_per_song.py` invocation; post-snapshot taken after the aggregate and determinism-check runs.

| anchor group                                         | files | pre==post |
|------------------------------------------------------|------:|----------:|
| c37 recreate_v0 (verdict/rubric_hash/chosen_song/merged.musicxml) | 4 | 4/4 |
| c38 recreate_v0_batch (verdict/rubric_hash/chosen_songs/cross_band_table) | 4 | 4/4 |
| c39 recreate_v0_full_corpus (verdict/rubric_hash/chosen_songs_full/cross_band_correlation) | 4 | 4/4 |
| c9 extractors (harmonic, rhythmic, melodic, form, arrangement) | 5 | 5/5 |
| c6 schema/validate/ledger/rule_id                    | 4 | 4/4 |
| Two frozen rules ledgers (c9 + c15 i3)               | 2 | 2/2 |
| c39 per-song merged.musicxml spot-checks (5 sampled) | 5 | 5/5 |
| c38 per-song merged.musicxml spot-checks (3 sampled) | 3 | 3/3 |
| **total**                                            | **31**| **31/31** |

`all_unchanged = true`. Rubric contract ("30+ SHAs") satisfied at 31.

## §8 Test suite output

Command: `PYTHONPATH=. /usr/bin/python3 tests/test_rules_extraction_rated_corpus.py`

Result: **20/20 PASS** (rubric ≥15 required).

Cases (all PASS):

1. `test_01_mtime_gate` — rubric mtime < every `scripts/rules_rated_corpus/*.py` mtime.
2. `test_02_gitlog_gate` — MERGE_DEFERRED acceptable per c38/c39 precedent.
3. `test_03_rubric_hash_matches_doc` — rubric_hash.txt byte-equals sha256(rubric doc); size = 65 B.
4. `test_04_verdict_rubric_hash_matches` — verdict.json.rubric_hash byte-equal to rubric_hash.txt.
5. `test_05_verdict_in_domain` — verdict ∈ {LANDS, PARTIAL, FAILS}.
6. `test_06_no_prng` — no `random.` / `numpy.random` / `secrets.` references.
7. `test_07_interpreter_guard` — `/usr/bin/python3` guard on every script.
8. `test_08_no_sidecar_nonfactor` — no `sidecar_nonfactor` imports (comments/docstrings mentioning it excluded).
9. `test_09_c9_extractor_anchor_preservation` — 5 c9 extractor SHAs unchanged.
10. `test_10_c6_writer_validator_anchor_preservation` — 4 c6 anchor SHAs unchanged.
11. `test_11_c9_ledger_unchanged` — `data/rules/ledger.jsonl` byte-identical pre/post.
12. `test_12_c15_i3_ledger_unchanged` — `data/rules/ledger_i3_dminor.jsonl` byte-identical pre/post.
13. `test_13_aggregate_determinism_x2` — aggregate SHA equal; 43/43 per-song shards equal.
14. `test_14_every_row_validates` — 1030/1030 rows Layer-1+Layer-2 clean via c6 `validate_batch`.
15. `test_15_provenance_pointers_resolve` — 0 unresolvable transcription_event_ids across the shard.
16. `test_16_wall_clock_finite` — every `stage_manifest.json.wall_clock_s` finite and ≥ 0.
17. `test_17_43_songs_enumerated` — song_manifest.json.n_songs == 43, sorted by song_id ascending.
18. `test_18_aggregate_row_floor` — row count reflects verdict honestly.
19. `test_19_peer_shard_unmodified_synth_ledger` — c9 synth ledger contains no rated_corpus provenance.
20. `test_20_peer_shard_row_count_matches_verdict` — shard line count == verdict n_rows_aggregate.

## §9 Verdict under frozen rubric + honest shortfall disclosure

**Verdict: `RATED_CORPUS_PARTIAL`.**

Rationale (verbatim from verdict.json):

> `43/43 songs cleanly extracted with 1030 valid rows; 0/43 songs meet the strict ≥5-per-type-per-song floor; rule_types falling short on >5 songs: {'harmonic': 43}`.

Rubric OR-clause matched: **"one or more rule_types fall below the ≥5-rows-per-song floor on >5 songs"** — harmonic falls short on 43 of 43 songs, satisfying the `>5` threshold by a wide margin. This is not a determinism defect, not an anchor drift, and not a validation failure: it is a faithful measurement of the frozen c9 harmonic extractor's yield on real-audio-derived MusicXML.

**Positive findings preserved:**
- **1030 valid rule rows** appended to the peer shard (rubric's aggregate volume floor of ≥900 met).
- **43/43 songs** produced valid rows without crash.
- **4 of 5 rule_types** (arrangement, form, melodic, rhythmic) hit the ≥5-per-song floor on 43/43 songs.
- **Byte-determinism × 2 PASS** on the aggregate shard and all 43 per-song shards.
- **Anchor preservation 31/31 unchanged** (contract required 30+).
- **Provenance-pointer resolvability 100%** — every one of the 1030 rows' provenance_pointers resolves to a per-song merged.musicxml or basic_pitch/*.jsonl on disk.
- **Peer-shard placement respected**: `data/rules/ledger_rated_corpus.jsonl` created as new peer; `data/rules/ledger.jsonl` and `data/rules/ledger_i3_dminor.jsonl` byte-unchanged.

**Honest per-song / per-rule_type gap disclosure:**
- Harmonic short-of-floor songs: **43 / 43** (band-4 10/10, band-5 10/10, band-6 13/13, band-7 10/10).
- Non-harmonic short-of-floor songs: **0 / 43** on all four other rule_types.
- Root cause: `insufficient-progression` coercion (`unique(chord_progression) < 2`), documented at `scripts/rules/extract/breadth_seeds.py:_coerce_row_or_skip`, fires on 3–4 of the 6 candidate harmonic rows per song.

## §10 c41 handoff seeds

Pre-registered by this report per rubric §7 pattern; c41 auditor to select:

- **Primary (per rubric)**: single-song focused-rerun on the harmonic shortfall — extract with a different 30 s window (offset trim by 15 s) OR a different chord-window granularity (2 s hop instead of 5 s) to test whether the shortfall is coercion-conservatism or an unavoidable feature of KS-plus-`chordify()` on ≤30 s real-audio-derived scores. Falsifiable prediction: if the coercion is window-conservatism, a 2 s hop should lift median harmonic rows/song from 2.0 to ≥4.0 on ≥30 songs; if the coercion is unavoidable, the median stays ≤2.5.

- **Alternate (per rubric)**: shift the M-GEN-1 palette-driven-batch pipeline to draw from the new rated-corpus ledger shard (`data/rules/ledger_rated_corpus.jsonl`) on the four rule_types (arrangement, form, melodic, rhythmic) that DID clear the floor. `M-GEN-1/palette-driven-batch-rated-corpus` — first M-GEN-1 batch sampling from the new rated-corpus ledger shard, letting the c33 palette-render machinery draw from real-audio-derived rules on 4 of the 5 rule_types.

**Standing tickets (opportunistic, not gated on this branch):**
- Band-6 `f1cfe4855364ea9b` (Tom Misch / Yussef Dayes — *Last 100*) focused-rerun ticket from c39 auditor: single-song different-30 s-window rerun to test whether the c39 negative mel_l1_db delta is stochastic-in-window or genuinely chain-hostile.
- `_infra/emitter-idempotence-guard-clone-*` peer sub-milestone: shadow-ledger-scan skip-if-already-emitted check as a general safeguard.
- `_manager/effects-chain-band-selectivity` — remains opportunistic per c39 pre-registered logic (correlations did not clear the "gradient" interpretation on n=43).
- c38 clone-1 REDEFINED_GAP + normalizer-v2 REFUTED — mscore3 quantization root-cause narrowing remains opportunistic.
- c37 VST3 activation still gated by c36 MIXED verdict.
- Egress retry per campaign directive.

## Provenance

- 43 songs at `data/rules_rated_corpus/per_song/<song_id>/` (each: `rules_shard.jsonl` + `stage_manifest.json`).
- Peer shard: `data/rules/ledger_rated_corpus.jsonl` (1030 rows).
- Verdict: `data/rules_rated_corpus/verdict.json`.
- Determinism check: `data/rules_rated_corpus/determinism_check.json`.
- Anchor preservation: `data/rules_rated_corpus/anchor_preservation.json`.
- Aggregate summary: `data/rules_rated_corpus/aggregate_summary.{json,tsv}`.
- Per-band summary: `data/rules_rated_corpus/per_band_summary.json`.
- Song manifest: `data/rules_rated_corpus/song_manifest.json`.
- Rubric: `docs/rules_extraction_rated_corpus_rubric.md` (SHA `ed572704…f1c3`).
- Scripts: `scripts/rules_rated_corpus/` (`song_manifest.py`, `extract_per_song.py`, `aggregate_and_append.py`, `determinism_check.py`, `anchor_preservation.py`, `verdict.py`, `run_all.py`).
- Tests: `tests/test_rules_extraction_rated_corpus.py` (20/20 PASS).
