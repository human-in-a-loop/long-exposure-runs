# Verify stage 7 of 23 — M-RECREATE-2 operator-override arc (c50 rubric-v2 supersede, c51 RC1+RC9, c53 RC10 guitar-piano)

**Stage:** 8 of 48 (verify 7/23)
**Slice theme:** M-RECREATE-2 operator priority override arc landings (rubric-v2 supersede + first substantive branch verdicts).
**Method:** per c29 state-machine lemma — treat these as peer sub-milestones under M-RECREATE-2, verify three-way `rubric_hash` byte-equality end-to-end, spot-check on-disk artifact SHAs against verdict claims, confirm ledger `supersedes_path` typing, and check byte-determinism sidecars.

---

## Milestone 1: `M-RECREATE-2/accurate-small-set-v2` (cycle 50 rubric-v2 supersede)

**Result:** CONFIRMED / severity=none.

- **Rubric-v2 chain 2-way byte-equal:** `sha256(docs/m_recreate_2_accurate_small_set_rubric_v2.md)` = `0e11f704e12c62f85cfb9d58d6e6890227209ffb43247239e735a22acfdebe1f` = `cat data/recreate_v2/rubric_hash_v2.txt`. (Third leg — verdict rubric_hash — verified under Milestone 2 below.)
- **Rubric-v1 preserved read-only anchor:** `sha256(docs/m_recreate_2_accurate_small_set_rubric.md)` = `958ade3886eba560df284878ff5d351e3f6186159ed598f68b82fc7c3fe58b9d` = `cat data/recreate_v2/rubric_hash.txt`. Byte-identical to plan-of-record's c49 anchor.
- **Supersede ledger event landed correctly:** `_plan/m-recreate-2-rubric-v2-supersede` cycle=50 status=validated with `supersedes_path` as **`str`** (value = `docs/m_recreate_2_accurate_small_set_rubric.md`), not list — c14 `_infra/ledger-schema-hardening-v2` lemma respected.
- **focus_set_v2 structure:** 5 songs; keys `cycle=50`, `d1_formula`, `milestone`, `rubric_v2_sha256`, `run_id`, `songs`, `supersedes_v1`. Chicken Grease (band 6) present at `corpus/ratings/6/017__It2s36sL4aM__Chicken_Grease.mp3` — operator UPDATE #1 mandate honored.
- **focus_set v1 anchor preserved:** 8 top-level keys including `rubric_sha256` + `selection_method` unchanged.

---

## Milestone 2: `M-RECREATE-2/accurate-small-set/rc-v2-branch-a-verdict-emitted-clone-0` (c51 fork 38eba9f21a61 Branch A)

**Result:** CONFIRMED / severity=none.

- **Verdict:** `RC1_RC9_LANDS` (rc1_pass_count=4/5, rc9_pass_count=5/5, both_pass_count=4/5).
- **Three-way rubric_hash chain (byte-equal):** doc SHA `0e11f704…debe1f` == `rubric_hash_v2.txt` == verdict.json `rubric_hash` field == verdict.json `rubric_doc_sha256` == verdict.json `rubric_hash_source` reference. All four legs identical.
- **focus_set_v2 pinned in verdict:** `focus_set_v2_sha256` = `8908dae03202ae529282c08e74d490b336fadcf7ded4f93483a2b32756a1a5ca`.
- **Per-song merged_partial.midi SHAs spot-verified against on-disk:**
  - song 31a164f8 (Chicken Grease): verdict SHA `7ee77e8c10bedb4c80108e5bbfd1401a00249e552177dabe07913cea4cd1ebdc` == `sha256(data/rc1_rc9_impl/per_song/31a164f845f8e27e/merged_partial.midi)` byte-equal.
  - song cdd2717e: verdict SHA `96284bf34343e80aa7fbd8424990d52ca93293271ffef0e354d8c15660f73034` == on-disk byte-equal.
- **Honest negative finding surfaced:** Chicken Grease `coverage_ratio=0.2781` → `rc1_accept=false` (RC9 still passes). Per plan-of-record c52 auditor policy call — root cause: c49 baseline captured t=0–30s but focus_set_v2's D1 auto-picker chose t=233.6–263.6s; documented, not silently swept.
- **Anchor preservation:** 49 entries, 0 mismatches. `note` field documents `modified_stubs_c50_to_c51=[]` (the two c50 pre-registration stubs `rc1_v2_hybrid.py` + `rc9_first_class_parts.py` were designed to be replaced by c51 landed impls — plan-consistent). Two `missing_paths` documented honestly.
- **Byte-determinism sidecar** present at `data/rc1_rc9_impl/byte_determinism.json` (verdict pins per-song `merged_midi_sha256` values that reproduce on-disk).
- **Ledger event landed correctly:** cycle=51 status=validated under `-clone-0` suffix per c33 harness-clone-namespace-guard.

---

## Milestone 3: `M-RECREATE-2/accurate-small-set/rc10-transcription-real-stem-resurvey/guitar-piano/verdict-emitted` (c53 fork bdd7bb47f1b5 clone-1)

**Result:** CONFIRMED / severity=none.

- **Verdict:** `RC10_GUITAR_PIANO_LANDS` (guitar 4/5 PASS, piano 5/5 PASS; winner-per-stem-type = `C2_tuned` for both, 3/5 majority).
- **Three-way rubric_hash chain (byte-equal):** doc SHA `sha256(docs/rc10_guitar_piano_rubric.md)` = `c7fe33a742a98f9b8ad2d87cb3f26286950ad560ef5d69c47dd53686fe03d7a8` == `cat data/rc10_impl/guitar_piano/rubric_hash.txt` == verdict.json `rubric_hash` field. All three legs identical.
- **Byte-determinism × 2:** `data/rc10_impl/guitar_piano/byte_determinism.json.byte_determinism_holds=true`, `n_artifacts=133`, `n_mismatch=0`. Env pins recorded: OMP/MKL/OPENBLAS=1, PYTHONHASHSEED=0, SOURCE_DATE_EPOCH=1756463424, TZ=UTC, LC_ALL=C.UTF-8.
- **Anchor preservation:** 28 entries, 0 mismatches.
- **Scorecard structure:** 60 rows on disk (3 candidates × 2 stems × 5 songs × 2 D4-flavors) — matches plan-of-record success criterion (c).
- **Candidate win counts:** guitar {C1_default:2, C2_tuned:3}, piano {C1_default:2, C2_tuned:3} — consistent with D5 amended selection (prefer PASS, then chroma_cosine_mean, SHA-256 tiebreak per operator UPDATE #4).
- **A/B pairs:** `n_ab_pairs=10` (5 songs × 2 stems), matches plan.
- **Ledger event landed correctly:** cycle=53 status=validated. Clone-1 suffix applied at the parent umbrella level; sub-leaf `verdict-emitted` under `guitar-piano` unsuffixed per c32 substantive-M-* convention.

---

## Cross-cutting observations

- **c29 state-machine lemma respected** on all three milestones — verified as peer sub-milestones under M-RECREATE-2, not children of any c49-in-progress terminal.
- **c14 supersedes-path typing:** the c50 `_plan/m-recreate-2-rubric-v2-supersede` event carries `supersedes_path` as `str`. No `list` regression.
- **c32/c33 namespace convention:** `-clone-<k>` suffix applied to infra families (`_infra/`, `_plan/`, etc. — none in this slice), substantive `M-*` unsuffixed.
- **Operator UPDATE #4 amendment:** D5 winner-selection now prefers PASS first (not just max chroma_cosine_mean); rc10 guitar-piano verdict reflects that ordering (winner_per_stem.json contains `tiebreak_method` per song).
- **Chicken Grease policy carry-over:** RC1 miss (0.2781 coverage) traced to baseline-window / auto-picker mismatch and documented; no attempt to backfill in this slice.

---

## Findings this stage

None (severity=none for all three milestones). All rubric chains three-way byte-equal (v1 verified 2-way — third leg was structural, no c50 verdict.json exists to check; v2 verified 3-way via c51 verdict.json). All on-disk artifact SHAs reproduce verdict claims byte-exactly. All ledger events landed with correct status, cycle, and typing.

## Anchors verified read-only pre-slice

- docs/m_recreate_2_accurate_small_set_rubric.md (c49 v1)
- docs/m_recreate_2_accurate_small_set_rubric_v2.md (c50 v2)
- data/recreate_v2/rubric_hash.txt + rubric_hash_v2.txt
- data/recreate_v2/focus_set.json + focus_set_v2.json
- data/rc1_rc9_impl/{verdict,byte_determinism,anchor_preservation}.json
- data/rc10_impl/guitar_piano/{verdict,byte_determinism,rubric_hash.txt,winner_per_stem,scorecard.tsv}
- docs/rc10_guitar_piano_rubric.md
- promise_ledger.jsonl (read-only scan)
