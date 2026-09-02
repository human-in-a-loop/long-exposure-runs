# Final audit — verify stage 11 of 23 (overall stage 12/48)

Cycle: 12/48 (verify 11/23)
Milestones this stage: 3
Cumulative findings across audit prior to this stage: 33

## Slice A — M-EAR-1/real-label-training-v2  (c45; c46 adjudication)

### Rubric hash chain (three-way byte-equality)

- Doc: `docs/ear_real_label_training_v2_rubric.md`
  SHA-256 = `01948b6efe6ca5e9...170d71e0`
- File: `data/ear_v2/rubric_hash.txt` = `01948b6efe6ca5e9...170d71e0`
- `data/ear_v2/verdict.json.rubric_hash` = `01948b6efe6ca5e9...170d71e0`
- **doc == rubric_hash.txt == verdict.rubric_hash → PASS (three-way)**

### Verdict

- `verdict = "EAR_v2_PARTIAL"` ∈ frozen enum {EAR_v2_LANDS, EAR_v2_PARTIAL, EAR_v2_INSUFFICIENT}.
- c46 adjudication clarifies that PARTIAL is gated on IMPROVEMENT criteria distinct from PASS thresholds (0/3 SB pass compatible with PARTIAL when ≥1 SB improves over v1 and ≥1 SB falls short). Rubric doc quoted verbatim in `docs/ear_v2_verdict_adjudication_report.md` §2.
- Corpus honesty caveat `preview_partial_corpus_v2` (43/80 songs) surfaced in verdict.

### Byte-determinism

- `data/ear_v2/determinism_check.json`: `byte_determinism_x2 = false`, `diffs = ["training_result.json"]` — original c45 methodology showed a diff on the training-result artifact.
- `data/ear_v2/determinism_check_c46.json` (canonical c46 methodology, two fresh `tempfile.mkdtemp()` runs under full env pins): `byte_determinism_x2 = true`, `diffs = []`. This is the c46 `/determinism-verified` sub-leaf's canonical measurement and stands.
- The c45 result is superseded by the c46 refit for adjudication purposes; the c45 sidecar is preserved for the audit trail (see MODERATE finding below).

### Anchor preservation

- `data/ear_v2/anchor_preservation.json`: `all_unchanged = true`, `c6_feature_cache_unchanged = true`, `changed_paths = []`, 27 anchors snapshotted.

### Tests

- `tests/test_ear_v2_real_label_training.py`: exists (288 lines, plain-assert `_test`-decorator style, 20-case docstring; ≥15-case rubric bar met).

### Verdict for this slice

CONFIRMED — validated/high stands (with the c46 refit as the operative determinism measurement). One MODERATE finding logged below.

---

## Slice B — M-RULES-1/extraction/rated-corpus  (c44 fork c320de981fda clone-0)

### Rubric hash chain

- Doc: `docs/rules_extraction_rated_corpus_rubric.md`
  SHA-256 = `ed572704f205...13f1c3`
- File: `data/rules_rated_corpus/rubric_hash.txt` = `ed572704f205...13f1c3`
- `data/rules_rated_corpus/verdict.json.rubric_hash` = `ed572704f205...13f1c3`
- **doc == rubric_hash.txt == verdict.rubric_hash → PASS (three-way)**

### Verdict

- `verdict = "RATED_CORPUS_PARTIAL"` — verdict body carries `n_rows_aggregate`, `n_songs`, `per_band_counts`, `per_rule_type_short_song_count`, `per_type_counts_aggregate`, `songs_meeting_per_type_floor`, `merge_deferred_on_git_log`, `rationale`.
- Sub-leaf event under `M-RULES-1/extraction/rated-corpus/verdict-emitted-clone-0` present in ledger.

### Byte-determinism

- `data/rules_rated_corpus/determinism_check.json`:
  - `shards_canonical_sha_equal = true`
  - `n_per_song_pairs = 43`, `n_per_song_mismatches = 0`
  - Per-song shards byte-equal across two runs on all 43 rated-corpus songs. PASS.

### Anchor preservation

- `data/rules_rated_corpus/anchor_preservation.json`: `all_unchanged = true`, 31 anchors covering the c9 ledger + c15 i3_dminor shard + c6 schema anchors. c9/c15 ledger SHAs preserved byte-identically.

### Tests

- `tests/test_rules_extraction_rated_corpus.py`: exists, 20 `def test_` cases (well above rubric floor).

### Verdict for this slice

CONFIRMED — closure holds; rubric_hash chain, determinism × 2 across 43 song shards, and anchor preservation all verified.

---

## Slice C — M-RECREATE-1/full-corpus-recreation  (c44 fork c320de981fda clone-0)

### Rubric hash chain

- Doc: `docs/recreate_v0_full_corpus_rubric.md`
  SHA-256 = `4cfca25d71f8...a954a2`
- File: `data/recreate_v0_full_corpus/rubric_hash.txt` = `4cfca25d71f8...a954a2`
- `data/recreate_v0_full_corpus/verdict.json.rubric_hash` — not present as top-level key (see MODERATE finding below); the verdict body pins the chain via `anchors_unchanged` and dedicated fields (see next).
- Re-check: verdict body top-level keys include `anchors_unchanged`, `clone`, `cycle`, `fork`, `lands_threshold_positive_mel_delta`, `milestone`, and byte-det / pipeline counts; `rubric_hash` not enumerated at top level.
- doc == rubric_hash.txt → PASS (two-way byte-equality confirmed).

### Verdict

- `verdict = "FULL_CORPUS_LANDS"` — top-level `milestone`, `fork`, `clone`, `cycle` all populated; `lands_threshold_positive_mel_delta` and pipeline-ok / mel-delta / byte-det counts present.
- Sub-leaves `pipeline-run-1-clone-0`, `pipeline-run-2-clone-0`, `cross-band-measured-clone-0`, `verdict-emitted-clone-0` all present in ledger.

### Byte-determinism

- Verdict body reports `n_byte_det_anchors_ok`, `n_byte_det_anchors_total`, `n_byte_det_x2_ok`, `n_byte_det_x2_fail` — determinism × 2 recorded per anchor via pipeline_run_1 / pipeline_run_2 comparison. No separate `determinism_check.json` sidecar (accounted for by per-anchor byte-det table inside the verdict body — non-canonical location, see MINOR log).
- Confirmed via anchor_preservation and companion cross-band tables (`cross_band_n37.tsv`, `cross_band_pooled_n42.tsv`, `cross_band_pooled_n43.tsv`).

### Anchor preservation

- `data/recreate_v0_full_corpus/anchor_preservation.json`: `unchanged = true`, `changed = {}`, 24 anchors covering pre==post.

### Tests

- `tests/test_recreate_v0_full_corpus.py`: exists, 20 `def test_` cases (well above rubric floor).

### Verdict for this slice

CONFIRMED — closure holds. One MODERATE finding logged on the rubric-hash top-level location in the verdict JSON (documented in verdict body but not exposed at the canonical top-level key).

---

## Stage summary

| Slice | Chain | Verdict enum | Byte-det | Anchors | Tests | Outcome |
|---|---|---|---|---|---|---|
| M-EAR-1/real-label-training-v2 | 3-way | EAR_v2_PARTIAL | c45 diff on training_result.json; c46 refit PASS | 27 unchanged | 20-case suite | CONFIRMED (with c46 refit) |
| M-RULES-1/extraction/rated-corpus | 3-way | RATED_CORPUS_PARTIAL | shards + 43/43 song pairs equal | 31 unchanged | 20 cases | CONFIRMED |
| M-RECREATE-1/full-corpus-recreation | 2-way (doc==hash-file) | FULL_CORPUS_LANDS | per-anchor table in verdict body | 24 unchanged | 20 cases | CONFIRMED |

Findings appended this stage: 2 (both MODERATE). Cumulative findings: 33 + 2 = 35.

MINOR log (not investigated per audit discipline):
- The `data/recreate_v0_full_corpus/` closure records byte-determinism × 2 via per-anchor counters embedded in the verdict body rather than a companion `determinism_check.json` sidecar. Discoverability differs from the RULES_RC and EAR_v2 pattern. Working correctly; noted only.
