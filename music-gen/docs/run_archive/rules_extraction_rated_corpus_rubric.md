---
created: 2026-08-29T12:26:21Z
run_id: run-2026-08-29T122621Z
cycle: 40
agent: worker
milestone: M-RULES-1/extraction/rated-corpus
---

# Rubric — M-RULES-1/extraction/rated-corpus (c40 Branch A)

Frozen 3-verdict rubric for the first rule-extraction pass at real-audio-derived MusicXML scale (43 songs: 1 c37 clone-0 + 5 c38 clone-2 + 37 c39 clone-0).

This document's SHA-256 is committed to `data/rules_rated_corpus/rubric_hash.txt` and embedded byte-equal in `data/rules_rated_corpus/verdict.json.rubric_hash`. This doc's mtime must be strictly earlier than every `scripts/rules_rated_corpus/*.py` mtime (mtime gate). Git-log commit ordering (rubric before scripts) applies with `MERGE_DEFERRED` acceptable per c38/c39 precedent.

## Verdict domain

Exactly one of:

- **`RATED_CORPUS_LANDS`** — ≥5 rule rows per rule_type × ≥36 of 43 songs = ≥900 new validated rows appended to `data/rules/ledger_rated_corpus.jsonl`; every row Layer-1 (JSON-Schema draft 2020-12) + Layer-2 (cross-row) clean; content-derived `rule_id` reproduces byte-identically across two independent runs; every `provenance_pointers` entry resolves to a real per-song merged.musicxml element or transcription event id.

- **`RATED_CORPUS_PARTIAL`** — 20–35 of 43 songs cleanly extracted, OR one or more rule_types fall below the ≥5-rows-per-song floor on >5 songs. Report §4 (per-song table) and §5 (per-band cross-tab) MUST honestly disclose which songs/rule_types shortfall, with per-song null-with-reason coercions logged.

- **`RATED_CORPUS_FAILS`** — <20 songs cleanly extracted, OR determinism × 2 fails on the aggregate `data/rules/ledger_rated_corpus.jsonl` shard, OR any read-only anchor (c37/c38/c39/c9/c6) drifts.

## Contracts

### Rubric-hash discipline

- `docs/rules_extraction_rated_corpus_rubric.md` → SHA-256 → `data/rules_rated_corpus/rubric_hash.txt` (65 B: 64-hex + trailing newline).
- `verdict.json.rubric_hash` byte-equal to `rubric_hash.txt`.
- Rubric doc mtime strictly earlier than every `scripts/rules_rated_corpus/*.py` mtime.

### Determinism × 2 contract

- Two independent full-pipeline runs into fresh `tempfile.mkdtemp()` output paths.
- SHA-256 equality on the canonical-sort of `ledger_rated_corpus.jsonl` (rows sorted by `rule_id`).
- SHA-256 equality on every per-song `rules_shard.jsonl`.

### Provenance-pointer resolvability contract

- Every emitted row's `provenance_pointers[i].transcription_event_id` must equal `sha256("transcription::<tag>::<sha256_of_source_file>")[:32]` where `tag ∈ {score, drums, bass, other}` and the source file exists on disk for that song.
- Every emitted row's `provenance_pointers[i].measure_range` must satisfy `end ≥ start ≥ 0`.
- Every emitted row's `provenance_pointers[i].clip_id` present (informational).

### Anchor preservation contract (30+ SHAs)

Pre/post SHA-256 byte-equality (`unchanged: true`) on:

- c37 recreate_v0 anchor tree: `data/recreate_v0/{verdict.json, rubric_hash.txt, chosen_song.json, per_stage/06_score/merged.musicxml}` (4 anchors).
- c38 recreate_v0_batch anchor tree: `data/recreate_v0_batch/{verdict.json, rubric_hash.txt, chosen_songs.json, cross_band_table.tsv}` (4 anchors).
- c39 recreate_v0_full_corpus anchor tree: `data/recreate_v0_full_corpus/{verdict.json, rubric_hash.txt, chosen_songs_full.json, cross_band_correlation.json}` (4 anchors).
- c9 extractors (5 files): `scripts/rules/extract/{harmonic,rhythmic,melodic,form,arrangement}.py` (5 anchors).
- c6 schema+validator+writer: `scripts/rules/{validate.py, ledger.py, rule_id.py, schema/rules_v1.json}` (4 anchors).
- Two frozen rules ledgers: `data/rules/{ledger.jsonl, ledger_i3_dminor.jsonl}` (2 anchors).

Total: 4+4+4+5+4+2 = **23 anchor files**, plus 3 c39 per-song per_stage/06_score/merged.musicxml spot-checks + 3 c37/c38 per-song equivalents = **≥30 SHAs**.

### ≥15-test contract

`tests/test_rules_extraction_rated_corpus.py` must PASS 15 or more cases covering rubric-hash discipline, mtime gate, git-log gate (MERGE_DEFERRED OK), NO PRNG, interpreter guard, no `sidecar_nonfactor` imports, anchor preservation SHAs, aggregate determinism × 2, per-song determinism × 2, row-level validation, provenance-pointer resolvability, per-song wall-clock recorded, 43-song enumeration count, aggregate row count against floor, verdict domain membership.

## Executional guardrails

- **Foreground execution** for the extraction pass (music21 + pure-Python only; no torch, no VST, no DAW).
- **Per-song idempotence**: `data/rules_rated_corpus/per_song/<song_id>/stage_manifest.json` marks completion; resume-safe skip.
- **NO PRNG** anywhere under `scripts/rules_rated_corpus/`.
- **Interpreter guard**: `/usr/bin/python3` on every script (assert `sys.executable`).
- **No `sidecar_nonfactor` imports** (grep-verified).
- **Ledger events emitted AFTER artifacts land** on disk.
- **Emitter idempotence**: any `tools/_c40_*_emit_events.py` MUST read the shadow ledger first and skip already-emitted milestones (do not trust docstring claims — enforce with a scan).

## Preservation invariants

- `data/rules/ledger.jsonl` (c9 + c12) — SHA byte-equal pre/post.
- `data/rules/ledger_i3_dminor.jsonl` (c15) — SHA byte-equal pre/post.
- c9 anchor rule_ids under `data/rules/ledger.jsonl` — unchanged (append-only history).
- c37/c38/c39 read-only anchor trees — SHAs unchanged.
- α = `0.7469387071101908` — not touched by this branch.

## Peer-shard placement

New peer ledger: `data/rules/ledger_rated_corpus.jsonl`. Peer to `data/rules/ledger.jsonl` (c9 synth + c12 breadth) and `data/rules/ledger_i3_dminor.jsonl` (c15 I3). Do NOT append to `data/rules/ledger.jsonl` (would break c26–c30 canonical-aggregate-SHA anchor stability).
