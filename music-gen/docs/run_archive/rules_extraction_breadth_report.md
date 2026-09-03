---
created: 2026-08-28T11:50:00Z
cycle: 12
run_id: run-2026-08-28T040704Z
agent: worker (clone-0, fork ed041ef4c1dc)
milestone: M-RULES-1/extraction/breadth-seeds
---

# M-RULES-1 breadth expansion (cycle 12, fork ed041ef4c1dc / clone-0)

**Scope:** run the frozen cycle-9 rule extractors (harmonic, rhythmic,
melodic, form, arrangement) against the two M-INGEST-1/breadth-second-seeds
merged scores (`data/breadth/{seed_mid_50s,synth_060s}/merged.musicxml`),
append typed rule rows to `data/rules/ledger.jsonl` via the frozen
M-RULES-1/schema/ledger-writer, and quantify the impact on the M-GEN-1
salt=0..4 sampler's collision behaviour that cycle-11's batch-v1 audit
flagged as the mechanical unlock for larger batches.

**Regression contract (non-negotiable):** cycle-9 anchor rule_ids on
`data/score/merged_synth030s.musicxml` reproduce byte-identically after
the expansion. This holds trivially via the append-only writer contract
— the pre-existing 28 rows are the file's prefix and their bytes are
untouched.

**Result headline:** 76-row ledger after expansion (48 new rows across
the two breadth seeds); byte-deterministic across two independent runs;
salt-collision count drops from 5 to 4 out of 50 pairwise cells; the
specific arrangement-collision cycle-11 flagged (salts 1 & 4) resolves,
though new collisions surface (salt=4 becomes over-represented).

---

## 1. Seed selection walkthrough

The two breadth seeds are the ones already on disk under `data/breadth/`
after M-INGEST-1/breadth-second-seeds (cycle 10, clone-1) landed. No
other seeds are candidates — this is a corpus-limited cycle, not a seed-
selection cycle.

| Seed          | Source content family                                                                         | Score structure (from `merged.parts_mapping.json`) | Expected extraction viability |
|---------------|-----------------------------------------------------------------------------------------------|-----------------------------------------------------|--------------------------------|
| `seed_mid_50s` | 50 s / 22.05 kHz / mono decaying-triad sine → htdemucs → basic-pitch (bass:4v, drums:3v, other:2v) | 9 Parts; polyphonic at score level even though source is monophonic sine (htdemucs+basic-pitch produce multiple voice partitions from the transient triads) | harmonic (single sustained triad → weak progression), rhythmic (onset-driven, fallback path), melodic (bass + other pitched), form (50 s ≥ 8 bars), arrangement (3-group + density curve) |
| `synth_060s`   | 60 s / 44.1 kHz / stereo fluidsynth 3-instrument (drums+bass+piano) → htdemucs → basic-pitch (bass:2v, drums:3v, other:7v) | 12 Parts across all 3 instrument groups | all 5 rule_types viable; structurally analogous to synth_030s but 2× duration |

The cycle-9 extractor code is content-preserving on synth_030s (the
regression contract) and re-used verbatim for the breadth seeds; the
orchestrator swaps the `_common.py` extraction context so the frozen
extractors read the breadth-seed `merged.musicxml` and per-stem
`transcriptions/*.jsonl` rather than the synth_030s defaults. When the
context is reset, `transcription_event_id()` returns to its cycle-9
values — an exit-side guard against anchor drift.

## 2. Extraction results per seed per rule_type

Per-rule_type row counts (frozen dispatch order:
`harmonic → rhythmic → melodic → form → arrangement`; per-seed dispatch
order: `seed_mid_50s → synth_060s`):

| rule_type      | synth_030s (cycle-9 baseline) | seed_mid_50s (cycle-12) | synth_060s (cycle-12) | total post-expansion |
|----------------|-------------------------------|-------------------------|------------------------|-----------------------|
| harmonic       | 6                             | 2                       | 2                      | 10                    |
| rhythmic       | 6                             | 6                       | 6                      | 18                    |
| melodic        | 6                             | 6                       | 6                      | 18                    |
| form           | 5                             | 5                       | 5                      | 15                    |
| arrangement    | 5                             | 5                       | 5                      | 15                    |
| **all types**  | **28**                        | **24**                  | **24**                 | **76**                |

**Null-with-reason coverage** — the only rule_type × seed cells that
did not produce every candidate row are the measure-window harmonic
rules on both seeds:

| seed          | rule_type | reason                     | detail                             | rows suppressed |
|---------------|-----------|----------------------------|------------------------------------|-----------------|
| seed_mid_50s  | harmonic  | insufficient-progression   | `scope=measure unique_chords=1`    | 4 of 6 (2 kept: song-level + one 3-measure window that contained a chord change) |
| synth_060s    | harmonic  | insufficient-progression   | `scope=measure unique_chords=1`    | 4 of 6 (2 kept: song-level + one 3-measure window) |

**Coercion policy** (extractor-side, schema untouched): the orchestrator
suppresses harmonic-progression rows whose `chord_progression` collapses
to ≤ 1 unique Roman-numeral figure. This is the correct honest coercion
for decaying-triad / 4-bar-loop material where `music21.chordify()` +
`romanNumeralFromChord` cannot recover a progression. The pipeline
retains full song-level harmonic context (key + best-effort figure list)
on every seed, so the ledger has ≥1 harmonic row per seed even when
narrower windows produce nothing.

The `melodic` and `form` extractors emit exactly the same
5-sectionizations-per-seed pattern the cycle-9 extractor emits on
synth_030s. The `rhythmic` extractor's drums-fallback-to-bass path
fires on `seed_mid_50s` (basic-pitch produces no drum note events on
that mono seed) — same pattern as cycle-9 synth_030s; the fallback is
recorded in `provenance_pointers.transcription_event_id` (bass stem
digest for both seed_mid_50s and synth_030s, drum stem digest for
synth_060s where basic-pitch produced 8 drum onsets).

The full per-seed count matrix and null list is at
`data/rules/breadth_expansion_summary.json`.

## 3. Regression proof — cycle-9 anchors byte-identical

`data/rules/ledger.jsonl` grew from **28 rows** (SHA
`4fe722adde034c09…`) to **76 rows** (SHA `a6fd53e9bf9a10f6…`). The first
28 lines of the post-expansion ledger are byte-identical to the
pre-expansion ledger — verified by `tools/stale/_validate_breadth_expansion.py`
which snapshots the baseline, runs the extraction into two independent
temp copies of the baseline, and diffs prefix bytes:

    baseline SHA:      4fe722adde034c09...
    baseline rows:     28
    run 0 final SHA:   a6fd53e9bf9a10f6...
    run 1 final SHA:   a6fd53e9bf9a10f6...
    byte-determinism:  OK
    cycle-9 anchors:   28 / 28 preserved byte-identically

All 28 cycle-9 anchor rule_ids reproduce (spot-check of the 5 anchors
that cycle-11 batch-v1 salt=0 pinned into
`tests/test_integration_cross_branch.py` §23):

| rule_type    | cycle-9 anchor rule_id     | present in post-expansion ledger prefix? |
|--------------|-----------------------------|-------------------------------------------|
| harmonic     | `rule_0271c7a9f3b5f606`    | yes (line 1)                              |
| rhythmic     | `rule_88b63bd5e771c045`    | yes                                       |
| melodic      | `rule_09f340921fa2d258`    | yes                                       |
| form         | `rule_84816f91e31e50c4`    | yes                                       |
| arrangement  | `rule_67d34b1c927ef33d`    | yes                                       |

The salt=0-anchor assertion at `tests/test_integration_cross_branch.py`
line 1342–1356 reads a saved `sampling_manifest.json` from cycle-11's
batch-v1 output and is unaffected by ledger expansion. (See §5 below
for the separate observation that live salt=0 selection on the expanded
ledger differs from the pinned batch-v1 selection for 3 of 5 rule_types
— that becomes cycle-13's mechanical follow-up.)

## 4. rule_id uniqueness across seeds

The cross-seed collision matrix is empty: all 76 rule_ids in the
post-expansion ledger are distinct. This is guaranteed structurally by
the content-hash rule_id derivation
(`sha256(canonical_json({rule_type, scope, sorted_provenance_pointers, parameters}))`)
because `provenance_pointers.transcription_event_id` is computed from
the SHA of the seed-specific merged.musicxml / per-stem transcription
files, which differ between seeds — even for structurally-identical
rows (e.g. a form-monolithic row on seed_mid_50s vs. synth_060s share
`parameters` but differ in `provenance_pointers` and therefore in
`rule_id`).

Empirically:

    total rule_ids checked:  76
    distinct rule_ids:       76
    cross-seed collisions:   0

## 5. Salt-collision quantification (pre vs post)

Sampler: `scripts/gen/sample_rules.py` at salts 0..4. Salt=0 uses the
legacy bare canonical hash (cycle-10 identity path); salts 1..4 use the
envelope hash `{"salt": salt, "rule": row}`. Cell definition: a
pairwise "collision" is a (rule_type, salt_i, salt_j) triple with i<j
where the sampler picks the same rule_id at both salts. Total pairwise
cells = 5 rule_types × C(5,2) = **50**.

**Headline reduction:**

|                          | pre-expansion (28-row) | post-expansion (76-row) |
|--------------------------|------------------------|-------------------------|
| total pairwise collisions | 5 / 50                 | 4 / 50                  |
| per-type: harmonic       | 1 (salt 0 = salt 1)    | 1 (salt 0 = salt 1) still |
| per-type: rhythmic       | 2 (0=1, 2=3)           | 1 (1=4)                 |
| per-type: melodic        | 1 (1=2)                | 1 (2=4)                 |
| per-type: form           | 0                      | 0                       |
| per-type: arrangement    | 1 (1=4) — cycle-11 flag | 1 (3=4) — different pair |
| candidate pool sizes     | (6,6,6,5,5)            | (10,18,18,15,15)        |

**Interpretation** — the specific arrangement collision cycle-11's
batch-v1 audit named (salts 1 & 4 → same arrangement rule) **resolves**
under the expanded ledger (salt=1 arrangement now picks
`rule_b99a5066e653b247`, salt=4 arrangement picks
`rule_a8ffe2f88dc29eed`). Rhythmic collisions dropped from 2 to 1. But
new collisions surfaced at salt=4 in melodic (2=4) and arrangement
(3=4), and harmonic salt-0-vs-1 persists because both hash schemes
happen to rank the cycle-9 F_major song-level rule
(`rule_0271c7a9f3b5f606`) lowest across the wider candidate pool.

Salt=4 is over-represented in the post-expansion collision set (3 of
the 4 collisions involve salt=4), suggesting the envelope hash for
salt=4 partitions the rule space asymmetrically for these pools — a
subtle finding, not a bug in the sampler. A future cycle could probe
whether adding a few more high-diversity arrangement / melodic rows
(e.g. from a truly monophonic 60 s seed) breaks the salt=4 correlation.

**Verdict.** The expansion delivers a material but modest collision
reduction (5→4). Cycle-11's specific arrangement collision is gone; the
"corpus-size unlocks batch diversity" hypothesis is partially confirmed
— pool size 3× increase drove pairwise collision rate 10% → 8%, not
proportionally. The remaining collisions are concentrated at (harmonic
salt 0 vs 1) and (salt 4 vs the rest). Corpus size is one of several
gating factors — the arrangement rule's structural repetitiveness across
similar-family seeds (both breadth seeds retain the drums-bass-other
3-group instrumentation, so `layer_events` sequences look alike) is
another.

Full pre-vs-post pick table at `data/rules/salt_collision_before_after.tsv`
(25 rows: 5 salts × 5 rule_types with `pre_rule_id`, `post_rule_id`,
`pre_pool_size`, `post_pool_size`, `pre_collides_with_salts`,
`post_collides_with_salts`, `pre_selection_changed_post`).

**Live salt=0 divergence from batch-v1 anchors** — the post-expansion
live salt=0 sampler differs from the saved cycle-11 batch-v1
sampling_manifest for melodic, form, and arrangement (see the
"pre_selection_changed_post" column of the TSV). This does NOT break
the anchor test (which reads the saved JSON) but it means cycle-13's
mechanical batch-v2 rerun on the expanded ledger will produce different
salt=0 rule_ids for those three rule_types, and therefore different
generated songs at salt=0 than cycle-11's batch-v1. Flagged as expected
cycle-13 behaviour, not a regression.

## 6. Figure

![Panel A: per-rule_type × per-seed row-count stack. Panel B: pre→post
collision partner count heatmap (5 salts × 5 rule_types). Bold cells
indicate a collision that changed between pre and post. Non-zero cells
are the collision points; salt=4 lights up in the post grid on rhythmic,
melodic, and arrangement.](figures/rules_extraction_breadth_growth.png)

Regenerable via `tools/stale/_plot_breadth_growth.py`
(the script consumes `data/rules/breadth_expansion_summary.json` +
`data/rules/salt_collision_before_after.json` and writes to
`docs/figures/rules_extraction_breadth_growth.png`).

## 7. Blind spots

- **No batch-v2 regeneration.** The expanded ledger has NOT been fed
  through `scripts/gen/batch_v1.py`. Doing so would change the salt=0
  batch-v1 rule_ids for 3 of 5 rule_types (§5) and therefore change
  every rendered artifact (musicxml / midi / bare / effects) at salt=0
  under the batch pipeline. That is cycle-13's mechanical follow-up per
  the brief; this branch is rules-only.
- **Coherence-gate impact unmeasured.** The cycle-11 coherence gate
  (M-GEN-1/rule-composition-constraint) enumerates three coercion
  rules. With the expanded ledger, the population of coercions per salt
  might shift — cycle-11 recorded {2, 2, 1, 1, 2}. Not measured here to
  avoid re-running the batch pipeline.
- **No truly monophonic seed.** `seed_mid_50s` is monophonic at the
  source but the htdemucs → basic-pitch pipeline produced 9 Parts, so
  the extraction pool for that seed is polyphonic. A future
  breadth-third-seeds cycle could add a mono-single-Part score
  authored directly (bypassing htdemucs) to probe the arrangement rule
  under a true single-instrumentation vector.
- **No CLAP-family re-check.** Independent of this branch — cycle-11's
  CLAP-swap attempt failed at HF SSL cert (rung 1.2) and is untouched.
- **Pool size ≠ diversity.** Post-expansion pool sizes are 3× the
  baseline, but the added rows are structurally similar within each
  rule_type (e.g. 3 form-monolithic rows now exist — one per seed —
  which all produce structurally-identical `sections` lists differing
  only in `provenance_pointers`). Genuine parameter diversity would
  require seeds with different tempi, meters, or key contexts.

## 8. Recommendations for cycle 13

1. **Batch-v2 rerun.** `scripts/gen/batch_v1.py` on the expanded
   ledger at salts 0..4. Anchor the new salt=0 rule_ids into
   `tests/test_integration_cross_branch.py` §25 (a new section — do
   NOT touch the §23 cycle-11 batch-v1 anchors, which pin the saved
   sampling_manifest.json). Compare the 5-song grid figure against
   cycle-11's under a difference-metric summary.
2. **Salt N > 5.** Cycle-11 hard-coded 5 salts because that was the
   batch size. With the expanded pool, salts 5..9 would be a
   straightforward probe of whether the collision rate scales
   inverse-linearly with salt count. Free experiment; no extra
   ledger writes needed.
3. **Seed diversity, not just seed count.** Add one seed with a
   different key (currently every score-anchoring extractor produces
   `F_major` — the merged synth mixes all share that key). One D-minor
   or Bb-major seed would break the harmonic-salt-0-vs-1 persistent
   collision by adding a genuinely-differently-hashing song-level
   harmonic candidate.
4. **Arrangement structural diversity.** All three seeds have the
   drums-bass-other instrumentation shape. One two-instrument or
   five-instrument seed would break the arrangement rule's
   near-degenerate structure and drop the arrangement salt-3-vs-4
   post-expansion collision.

---

## Sufficiency check against the research brief

- Cycle-9 anchors byte-identical: **yes** (append-only guarantee + tmp-copy verification).
- ≥15 new rows: **yes** (48).
- Per-seed per-rule_type honest reporting including null-with-reason: **yes** (§2).
- Byte-determinism across two runs: **yes** (§3, SHA `a6fd53e9bf9a10f6…` reproduced).
- Salt-collision pre-vs-post table + interpretation: **yes** (§5 + `data/rules/salt_collision_before_after.tsv`).
- Report + figure shipped: **yes** (this file + `docs/figures/rules_extraction_breadth_growth.png`).
- Every new row validates: **yes** (orchestrator raises SystemExit on validator failure).
- rule_id uniqueness: **yes** (§4, 76 distinct rule_ids).

**Suggested closure verdict:** `validated/high` under the brief's
sufficiency ladder (regression contract intact, target met,
byte-deterministic, salt-collision analysis complete with material — if
modest — reduction and honest interpretation of the residual collisions).

## Deliverables index

| Path                                                      | Purpose                                            |
|-----------------------------------------------------------|----------------------------------------------------|
| `data/rules/ledger.jsonl`                                 | Expanded ledger (76 rows, post-expansion)          |
| `data/rules/breadth_expansion_summary.json`               | Per-seed per-rule_type counts + null-with-reason   |
| `data/rules/salt_collision_before_after.tsv`              | Salt-collision matrix (25 rows)                    |
| `data/rules/salt_collision_before_after.json`             | Salt-collision structured summary + picks table    |
| `docs/figures/rules_extraction_breadth_growth.png`        | Two-panel report figure                            |
| `docs/rules_extraction_breadth_report.md`                 | This report                                        |
| `scripts/rules/extract/breadth_seeds.py`                  | Orchestrator (kept live under scripts/)            |
| `scripts/rules/extract/_common.py`                        | Extended with `set_extraction_context()` (cycle-9 defaults preserved) |
| `tools/stale/_validate_breadth_expansion.py`              | Regression harness (archived post-run)             |
| `tools/stale/_salt_collision_analysis.py`                 | Salt-collision analysis (archived post-run)        |
| `tools/stale/_plot_breadth_growth.py`                     | Figure renderer (archived post-run)                |
| `tools/stale/_emit_breadth_events.py`                     | Ledger-event emitter (archived post-run)          |
