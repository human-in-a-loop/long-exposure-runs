---
created: 2026-08-29T12:50:00Z
run_id: run-2026-08-29T125000Z
cycle: 41
agent: worker
milestone: M-RULES-1/extraction/rated-corpus/harmonic-window-refinement
---

# Rubric — M-RULES-1/extraction/rated-corpus/harmonic-window-refinement (c41 Branch A)

Frozen 3-verdict rubric for the c40 harmonic shortfall refinement pass. c40 delivered `RATED_CORPUS_PARTIAL` on 43/43 rated-corpus songs: 4 rule_types met the ≥5-rows-per-song LANDS floor; harmonic fell to ~2/song under the c12 `insufficient-progression` coercion (`unique(chord_progression) < 2` → skip) firing on 3–4 of the 6 KS+chordify windows on real-audio 30 s trims. This cycle tests a 2-axis 6-cell grid (window-hop × uniqueness-relaxation) that leaves the c9 extractor + c12 coercion policy anchored and emits a new PEER shard only on LANDS verdict.

This document's SHA-256 is committed to `data/rules_harmonic_window_v2/rubric_hash.txt` (65 B) and embedded byte-equal in `data/rules_harmonic_window_v2/verdict.json.rubric_hash`. This doc's mtime must be strictly earlier than every `scripts/rules_harmonic_window_v2/*.py` mtime. Git-log commit ordering (rubric before scripts) applies with `MERGE_DEFERRED` acceptable per c37/c38/c39/c40 precedent.

## Verdict domain

Exactly one of:

- **`HARMONIC_v2_LANDS`** — ≥5 harmonic rows per song on ≥36/43 songs under the winning cell of the 2-axis grid AND the `(5.0, 2)` identity cell reproduces c9 synth_030s harmonic anchor rule_ids byte-identically AND per-cell byte-determinism × 2 clean.

- **`HARMONIC_v2_PARTIAL`** — 20–35 songs cleanly extract ≥5 harmonic rows under the best cell, OR the best cell only lifts one of the two axes; per-cell / per-song numbers reported honestly.

- **`HARMONIC_v2_INSUFFICIENT`** — no grid cell lifts ≥36/43 above the 5-row floor; c40 `RATED_CORPUS_PARTIAL` stands; hand off to c42 with a "corpus-side intervention won't close this" finding + concrete alternative direction.

## Refinement grid (frozen)

**Axis A — chord-window hop size (`window_hop_s`):** `{5.0, 2.5, 2.0}` seconds. c9's default (~5–6 s per 3-measure window at tempo 120) → 5.0. Finer hops give more chord windows on 30 s trims.

**Axis B — progression uniqueness policy (`progression_min_unique`):** `{2, 1_with_repeat_allowed}`. c9's default (matching c12 coercion) is `unique >= 2`. The relaxation permits a progression with only 1 unique Roman numeral IF the same numeral repeats ≥2 times in the window (excludes silence/single-note artifacts).

Grid: 3 × 2 = 6 cells enumerated verbatim as
`[(5.0, 2), (5.0, "1_with_repeat_allowed"), (2.5, 2), (2.5, "1_with_repeat_allowed"), (2.0, 2), (2.0, "1_with_repeat_allowed")]`.

Pre-registered evaluation metric: **mean harmonic-rows-per-song across 43 songs**; tie-break by **byte-determinism × 2 pass rate**.

## Contracts

### Anti-cheat identity-cell contract

`(5.0, 2)` identity cell MUST reproduce c9's synth_030s harmonic anchor rule_ids byte-identically. Wrapper delegates to c9 `scripts/rules/extract/harmonic.py::extract()` unchanged and applies `progression_min_unique=2` filter (a no-op on synth_030s where every window has ≥2 unique Roman numerals). Test-enforced. If it fails, the refinement wrapper has drifted from c9 semantics and the cycle FAILS regardless of grid outcome.

### Rubric-hash discipline

- `docs/rules_harmonic_window_refinement_rubric.md` → SHA-256 → `data/rules_harmonic_window_v2/rubric_hash.txt` (65 B: 64-hex + trailing newline).
- `verdict.json.rubric_hash` byte-equal to `rubric_hash.txt`.
- Rubric doc mtime strictly earlier than every `scripts/rules_harmonic_window_v2/*.py` mtime.

### Determinism × 2 contract

- Two independent full-grid runs into fresh `tempfile.mkdtemp()` output paths.
- SHA-256 equality on the aggregated `per_cell_summary.tsv`.
- SHA-256 equality on every per-cell per-song `rules_shard.jsonl` (43 × 6 = 258 shards per run).

### Anchor preservation contract (32+ SHAs)

Pre/post SHA-256 byte-equality (`unchanged: true`) on:

- c9 extractors (5 files): `scripts/rules/extract/{harmonic,rhythmic,melodic,form,arrangement}.py` (5 anchors).
- c6 schema+validator+writer: `scripts/rules/{validate.py, ledger.py, rule_id.py, schema/rules_v1.json}` (4 anchors).
- Three frozen rules ledgers: `data/rules/{ledger.jsonl, ledger_i3_dminor.jsonl, ledger_rated_corpus.jsonl}` (3 anchors).
- c37 recreate_v0 anchor tree: `data/recreate_v0/{verdict.json, rubric_hash.txt}` (2 anchors).
- c38 recreate_v0_batch anchor tree: `data/recreate_v0_batch/{verdict.json, rubric_hash.txt}` (2 anchors).
- c39 recreate_v0_full_corpus anchor tree: `data/recreate_v0_full_corpus/{verdict.json, rubric_hash.txt}` (2 anchors).
- c40 rated_corpus anchor tree: `data/rules_rated_corpus/{verdict.json, rubric_hash.txt, aggregate_summary.json, aggregate_summary.tsv}` (4 anchors).
- 8+ per-song merged.musicxml spot-checks under the c40 song manifest.
- 2 additional c40 report + rubric docs: `docs/rules_extraction_rated_corpus_{rubric,report}.md`.

Total: 5+4+3+2+2+2+4+8+2 = **≥32 anchor files**.

### ≥15-test contract

`tests/test_rules_harmonic_window_refinement.py` PASS 15 or more cases covering: mtime gate, git-log gate (MERGE_DEFERRED OK), rubric_hash byte-chain, verdict-in-domain, NO PRNG, interpreter guard, no `sidecar_nonfactor`, c9 anchor SHAs unchanged, c6 anchor SHAs unchanged, c40 peer shard SHA byte-equal, c9 ledger SHA byte-equal, c15 ledger SHA byte-equal, anti-cheat identity-cell contract, grid enumeration deterministic, all rows Layer-1+Layer-2 clean, peer shard provenance resolvability (if LANDS).

## Peer-shard placement

On `HARMONIC_v2_LANDS` verdict only: emit `data/rules/ledger_rated_corpus_harmonic_v2.jsonl` as a NEW peer shard (winning cell rows). c40's `data/rules/ledger_rated_corpus.jsonl` SHA byte-equal pre/post regardless of verdict. c9's `data/rules/ledger.jsonl` + c15's `data/rules/ledger_i3_dminor.jsonl` SHA byte-equal regardless of verdict.

## Preservation invariants (reject any deviation)

- c40 `docs/rules_extraction_rated_corpus_{rubric,report}.md` — READ-ONLY.
- c40 `data/rules_rated_corpus/*` — READ-ONLY.
- c40 `data/rules/ledger_rated_corpus.jsonl` — SHA byte-equal pre/post.
- c9 `data/rules/ledger.jsonl` — SHA byte-equal pre/post.
- c15 `data/rules/ledger_i3_dminor.jsonl` — SHA byte-equal pre/post.
- c9 `scripts/rules/extract/*.py` — READ-ONLY imports; NO edits.
- c6 `scripts/rules/{validate,ledger,rule_id}.py`, `scripts/rules/schema/*` — READ-ONLY imports.
- c37/c38/c39 recreate trees — READ-ONLY.
- α = `0.7469387071101908` — this branch does not touch α.
- NO PRNG anywhere under `scripts/rules_harmonic_window_v2/`.
- Interpreter guard `/usr/bin/python3` on every script.
- No `sidecar_nonfactor` imports.

## Executional guardrails

- Foreground execution.
- Per-song × per-cell idempotence via `data/rules_harmonic_window_v2/per_song/<song_id>/<cell>/stage_manifest.json`.
- Ledger events emitted AFTER artifacts land.
- Emitter idempotence: writer-side `LedgerAppendError: duplicate event_id` catch (c40 precedent).
