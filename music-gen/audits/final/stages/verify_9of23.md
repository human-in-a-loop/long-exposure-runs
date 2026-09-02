# Verify slice 9 of 23 (audit stage 10 of 48)

Scope: three milestone slices verified this stage:
1. **M-RECREATE-2/accurate-small-set/rc10-transcription-real-stem-resurvey/guitar-piano** (c53 clone-1)
2. **M-RULES-1/extraction/rated-corpus** (c40 clone-0, retroactive fork c320de981fda reconciliation)
3. **M-RECREATE-1/full-corpus-recreation** (c39-41 clone-0, retroactive fork c320de981fda reconciliation)

## Verification method (per slice)

For each milestone: (a) three-way `rubric_hash` byte-equality (`sha256(rubric_doc) == rubric_hash.txt == verdict.json.rubric_hash`); (b) verdict content matches rubric acceptance; (c) byte-determinism × 2 anchor; (d) anchor preservation pre==post; (e) ledger events land under expected suffix convention.

---

## Slice 9.1 — M-RECREATE-2/.../rc10-transcription-real-stem-resurvey/guitar-piano (c53 clone-1)

- **Rubric-hash chain (three-way byte-equal)**: PASS.
  - `sha256(docs/rc10_guitar_piano_rubric.md)` = `c7fe33a742a98f9b8ad2d87cb3f26286950ad560ef5d69c47dd53686fe03d7a8`
  - `data/rc10_impl/guitar_piano/rubric_hash.txt` byte-equal to doc SHA.
  - `data/rc10_impl/guitar_piano/verdict.json.rubric_hash` byte-equal to same.
- **Verdict**: `RC10_GUITAR_PIANO_LANDS` — matches rubric acceptance (per-stem PASS ≥ 3/5). Observed: guitar 4/5 PASS, piano 5/5 PASS. `winner_per_stem_type` = `{guitar: C2_tuned, piano: C2_tuned}`. Scorecard has 60 rows (3 candidates × 2 stems × 5 songs × 2 D4-flavors), matching the sub-leaf `candidate-matrix-scored` contract.
- **Byte-determinism × 2**: `data/rc10_impl/guitar_piano/byte_determinism.json`: `byte_determinism_holds=true`, `n_mismatch=0` across 133 artifacts.
- **Anchor preservation**: `n_entries=28`, `diff_count=0`, diff=[] — pre==post byte-exact.
- **Ledger**: 6 sub-leaf events landed under the parent (`pre-registration`, `candidate-matrix-implemented`, `candidate-matrix-scored`, `winner-selected`, `ab-pairs-emitted`, `verdict-emitted`); parent umbrella `rc10-transcription-real-stem-resurvey` also present. Grep count = 6 for `guitar-piano` suffix — matches rubric contract.
- **Verdict**: CONFIRMED. Severity: none.

## Slice 9.2 — M-RULES-1/extraction/rated-corpus (c40 clone-0, retroactively reconciled)

- **Rubric-hash chain (three-way byte-equal)**: PASS.
  - `sha256(docs/rules_extraction_rated_corpus_rubric.md)` = `ed572704f205a723a9bb6e2f8b7a5d122e9aa186af6a00a05a60a6e59013f1c3`
  - `data/rules_rated_corpus/rubric_hash.txt` byte-equal to doc SHA.
  - `data/rules_rated_corpus/verdict.json.rubric_hash` byte-equal.
- **Verdict**: `RATED_CORPUS_PARTIAL` — an honest partial finding. Verdict shows `n_songs=43`, `n_rows_aggregate=1030`, `n_duplicates_dropped=0`, `merge_deferred_on_git_log=true` (git-log MERGE_DEFERRED path per c38/c39 precedent). Per-band counts populated across all four bands and five rule_types; short-song fallback applied to 43/43 harmonic rows (documented in extractor coercion behavior). This is a first-class negative finding, not a defect.
- **Byte-determinism × 2**: `data/rules_rated_corpus/determinism_check.json`: `n_per_song_pairs=43`, `n_per_song_mismatches=0`. Aggregate shard canonical-sort SHA equal across two fresh tempdir runs (`aggregate_shard_canonical_sha_equal=true` in verdict).
- **Anchor preservation**: `all_unchanged=true`, `n_anchors=31` — meets contract (≥30).
- **Ledger shard**: `data/rules/ledger_rated_corpus.jsonl` present (1.19 MB, 1030 rows) — peer to c9 `ledger.jsonl` + c15 `ledger_i3_dminor.jsonl`. The c9 and c15 ledgers are asserted byte-identical anchors in the ledger-shard-appended event.
- **Ledger**: 6 sub-leaf events under `-clone-0` suffix per c33 harness auto-suffix convention (rubric-committed, songs-enumerated, per-song-extracted, ledger-shard-appended, anchor-preservation-verified, verdict-emitted). Total 18 rated-corpus events (includes cross-branch references).
- **Verdict**: CONFIRMED. Severity: none.

## Slice 9.3 — M-RECREATE-1/full-corpus-recreation (c39-41 clone-0, retroactively reconciled)

- **Rubric-hash chain (three-way byte-equal)**: PASS.
  - `sha256(docs/recreate_v0_full_corpus_rubric.md)` = `4cfca25d71f8bb67a2c3b2be30a3d2173f9ef893d31f3cf0fd88c093e1a954a2`
  - `data/recreate_v0_full_corpus/rubric_hash.txt` byte-equal.
  - `data/recreate_v0_full_corpus/verdict.json.rubric_hash` byte-equal.
- **Verdict**: `FULL_CORPUS_LANDS` — matches rubric acceptance (`lands_threshold_positive_mel_delta=33`; observed `n_positive_mel_delta=36` of 37). All 37 songs completed the 8-stage pipeline (`n_pipeline_ok=37`, `n_pipeline_fail=0`). Per-band positive-mel-delta counts: band 4 = 9/9, band 5 = 9/9, band 6 = 10/11 (one song not positive), band 7 = 8/8. Overall 36/37 positive — well above the 33-song LANDS floor.
- **Byte-determinism × 2**: `n_byte_det_x2_ok=37`, `n_byte_det_x2_fail=0`. Anchor-level: `n_byte_det_anchors_ok=148`, `n_byte_det_anchors_total=148`, `per_anchor_byte_det_failures=[]`.
- **Anchor preservation**: `unchanged=true`, `changed={}`, `n_anchors=24`. Includes c37/c38 recreate trees + c9/c15 ledgers.
- **Cross-band tables**: `cross_band_n37.tsv`, `cross_band_pooled_n42.tsv`, `cross_band_pooled_n43.tsv` all present per rubric §e (three pooled-N presentations honestly labeled by pooling).
- **Ledger**: 10 events tied to milestone; 6 named + housekeeping under `-clone-0` per c33 auto-suffix on infra families; `M-*` unsuffixed per c32 convention.
- **Verdict**: CONFIRMED. Severity: none.

## MINOR observations (log-only, per audit charter)

- **Slice 9.2**: `merge_deferred_on_git_log=true` field in the rated-corpus verdict.json is honest documentation of the c38/c39-established path where git-commit approval prompts cannot land inside a worker turn (see c46 `_plan/git-log-gate-policy-amendment`). This is a governance record, not a defect — logged for completeness.
- **Slice 9.3**: One band-6 song did not clear positive mel_l1_db delta (36/37 positive overall). Verdict correctly reports this as `n_mel_delta_fail=1` and still lands per rubric's 33-song floor. Not a defect; the rubric explicitly permits per-song exceptions under the aggregate threshold.
- **Slice 9.1**: `ab_pairs_manifest.json` documents LUFS relaxation for peak-limited signals (rubric §h ±0.5 LU target relaxed honestly). Documented in report §Issues per the plan-of-record narrative — behavior matches contract.

## Cumulative counts

Findings this stage appended: 3 (all CONFIRMED, severity=none).
Cumulative findings.jsonl rows: 30.
Verified slices so far (stages 1–10): 27 milestone slices covering ingestion → classifier → separation → transcription → score → texture → heuristics → ear-model chassis + real-label v0/v1/v2/v2.1 → rules schema + extraction + rated-corpus + harmonic-window-refinement → generation batches v1..v6 + collision-model arc + palette-driven batches v1..v4 + rated-corpus batch → recreate-v0 first-song + second-batch + full-corpus → recreate-v2 rc0 baseline + rc-stubs + rc1+rc9 + rc7 v2 + rc10 drums-bass + rc10 guitar-piano → DAW-spike + palette-schema + palette-schema-v2 + hydration + VST3-nondeterminism → infra ledger-hardening v1/v2 + fanout-concat + harness clone-namespace-guard + anchor-manifest-v1 + harness-and-writer-hardening-v3 + pre-existing-test-drift-triage + pre-registration-gate-policy-scope-verification.

Nothing flagged for reconciliation. All verified milestones remain terminally validated at high confidence.
