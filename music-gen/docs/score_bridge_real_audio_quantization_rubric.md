---
created: 2026-08-29T11:00:00Z
run_id: run-2026-08-28T040704Z
cycle: 38
agent: worker
milestone: M-SCORE-1/bridge-api-real-audio-quantization
scope: fork 33a2a8003c84 clone-1
---

# M-SCORE-1/bridge-api-real-audio-quantization — Frozen Rubric

**Commit-order gate:** this rubric doc **MUST** land on disk and be
`git commit`ted BEFORE any file appears under `scripts/score_bridge_v2/`.
`tests/test_score_bridge_real_audio_quantization.py` enforces this via
(a) file-mtime ordering (rubric-file mtime ≤ every script mtime) AND
(b) git-log-order (rubric commit predates every commit touching
`scripts/score_bridge_v2/`).

## 1. Fixture (c37 clone-0 anchor, byte-identical copy)

- **Anchor path:** `data/recreate_v0/per_stage/06_score/merged.musicxml`
- **Working-copy path:** `data/score_bridge_real_audio/inputs/merged_real_audio.musicxml` (read-only after copy).
- **SHA-256:** `95de5356fc127e8ff2b3c5153a950b35ddd4836b1ec1f40d658f41ebb73e1592`
- **Bytes:** 635231
- **Structural properties:**
  - `<divisions>10080</divisions>` (music21 chose LCM including tuplet-safety
    denominators although the merged score contains ZERO
    `<time-modification>` elements — this LCM inflation is a
    candidate pathology cause for P2).
  - 2460 `</note>` closing tags (mixed pitched notes, rests, and
    tie-split fragments from music21's identity-merge partitioner).
  - 512 `<tie ...>` elements (basic-pitch's real-audio onsets frequently
    cross music21's synthesized bar-line grid).
  - 0 `<time-modification>` elements (no tuplets).
  - c8 bridge (`scripts/score/bridge.py::merge_stems_to_score`) authored
    this file with `_MERGE_GRID_QL = 1.0/64.0` snapping applied to the
    per-stem basic-pitch note events for the band-7 rated song
    `corpus/ratings/7/016__LOCAL__05_02.mp3` (30 s trim).

## 2. Failure signature (reproduced under this cycle's environment)

`scripts.score.bridge.xml_to_midi(fixture)` raises `ScoreBridgeError`:

    xml_to_midi: mscore3 exited 1: ...
    Error at line 256 col 13: calculated duration (15/256) not equal to
      specified duration (1181/20160) -> assuming rounding error
    Error at line 268 col 13: calculated duration (7/256) not equal to
      specified duration (551/20160) -> assuming rounding error
    ...(dozens more with denominators 20160 and 5040)...

mscore3 3.2.3 escalates rounding-error warnings to rc=1 on this input
(where the c8 seed_8bar synthetic score usually returns rc=0 with the
same warning class ignored). This is the c37 clone-0 handoff #1
pathology this cycle must root-cause.

## 3. Reference oracle (current-known-good)

The c37 clone-0 fallback path (in `scripts/recreate_v0/run_pipeline.py`,
NOT `stage_06_merged_score.py`) skips mscore3 entirely and concatenates
per-stem basic-pitch MIDIs directly via `pretty_midi`:

- **Path:** `data/score_bridge_real_audio/inputs/fallback_reference.midi`
- **SHA-256:** `5cccca6c48820e26be95aae125679b4002ccab1a28b9aea13500066d213ac599`
- **Bytes:** 4154
- **Note count:** 195 (across bass + drums + other stems).

Any candidate winning path's MIDI event count is compared against 195.

## 4. c8-frozen tolerance envelope

Adopted verbatim from `M-SCORE-1/bridge-api` §M-SCORE-1/round-trip:

- Event count preserved: `|note_count_produced - 195| == 0`.
- Onset drift: max per-event `|t_produced - t_reference|` ≤ 2 ms.
- Duration drift: max per-event ≤ 1 tick at PPQ=480 (i.e. ≤ 2.083 ms
  at 120 BPM).

A path that passes ALL THREE thresholds satisfies
`fidelity_pass_c8_tolerance = True`. Any threshold failure is
`fidelity_pass_c8_tolerance = False`.

## 5. Byte-determinism × 2 protocol

Every candidate run pair MUST:

- Run in a fresh `tempfile.mkdtemp()` directory (independent for run 1
  and run 2).
- Set `PYTHONHASHSEED=0`, `SOURCE_DATE_EPOCH=1577836800` (2020-01-01T00:00:00Z),
  `TZ=UTC`, `LC_ALL=C.UTF-8`.
- Pin single-thread BLAS: `OMP_NUM_THREADS=1`, `MKL_NUM_THREADS=1`,
  `OPENBLAS_NUM_THREADS=1`.
- For any mscore3 invocation: `QT_QPA_PLATFORM=offscreen`.

A path is `byte_deterministic = True` iff `sha256(run1_midi) == sha256(run2_midi)`.

## 6. Probes (all three MUST run regardless of intermediate results)

### P1 — mscore3 flag matrix

Bounded enumeration on the fixture. Axes actually supported by
mscore3 3.2.3 (verified against `mscore3 --help`):

- **A** `-F` factory settings on/off.
- **B** `-R` revert-settings on/off.
- **C** `-e` experimental on/off.
- **D** `-t` test-mode on/off.
- **E** `-c <empty tempdir>` custom config folder vs default.

(The brief mentions `-f`, `--pretty`, and quantize-related flags that
DO NOT EXIST in mscore3 3.2.3. This rubric supersedes those with the
axes above and documents the discrepancy in the report §3.)

For each combination, run twice under §5; emit `data/score_bridge_real_audio/probes/p1_mscore3_flags.tsv`
with columns:

    flag_combination  run1_midi_sha  run2_midi_sha  byte_deterministic
    event_count  onset_drift_ms_max  duration_drift_ticks_max
    fidelity_pass_c8_tolerance  rc_run1  rc_run2

Winning row = first row in canonical (alphabetical) flag-combination
order with `byte_deterministic == True AND fidelity_pass_c8_tolerance == True`.

### P2 — Pre-mscore3 MusicXML normalizer

1. Property-attribution diff against `seed_synthetic.musicxml`.
2. `scripts/score_bridge_v2/normalize.py` applies:
   - Rewrite `<divisions>10080</divisions>` to `<divisions>480</divisions>`
     and rescale every `<duration>` accordingly (`new_duration = round(old * 480/10080)`,
     minimum 1). PPQ=480 is mscore3's own internal default and matches
     the c8 tolerance PPQ; sub-tick truncation is bounded by the c8
     tolerance envelope.
   - Snap sub-tick residual `<duration>` values to the nearest
     resulting-tick integer at PPQ=480.
   - Round `<tempo>` and `<sound tempo="...">` attributes to 6 decimals
     for canonical form (does not alter event count).
   - Rewrite ties: on the current fixture there are already
     appropriate `<tie/>` and `<tied/>` elements. The normalizer only
     canonicalizes attribute ordering (does not split further).
3. Run normalized fixture through mscore3 with the P1 baseline row
   (i.e. default flags, no `-F/-R/-e/-t`), twice under §5.
4. Emit `data/score_bridge_real_audio/probes/p2_normalizer.tsv`
   (same columns as P1) and
   `data/score_bridge_real_audio/probes/p2_property_attribution.json`.

Winning outcome: normalized fixture through mscore3 is
`byte_deterministic == True AND fidelity_pass_c8_tolerance == True`.

### P3 — Alternative MusicXML → MIDI backends

- **P3-A** `music21.stream.Score.write("midi", out_path)` on the fixture,
  loading via `music21.converter.parse(xml)`.
- **P3-B** `lilypond --midi in.ly` where `in.ly` is generated from the
  fixture via music21's LilyPond export. **lilypond is not installed in
  this workspace** — this probe records `fetch_status=FETCH_FAIL` in the
  `fetchability_ladder.jsonl` and `byte_deterministic=null,
  fidelity_pass_c8_tolerance=null` in the TSV, honestly not attempted.
  This is a first-class negative rung, not a fabricated result.

Emit `data/score_bridge_real_audio/probes/p3_alternative_backends.tsv`
(same columns as P1 plus a `backend` and `fetch_status` column).

Winning backend = first row where `byte_deterministic == True AND
fidelity_pass_c8_tolerance == True`.

## 7. Three-verdict rubric (frozen; canonical selection order)

Verdict selection is **strict priority order** — the first satisfied
label wins:

1. **`QUANTIZATION_FIXED`** — mscore3 native produces a
   byte-deterministic × 2 MIDI on the fixture using either
   (a) a P1 flag combination or (b) the P2 normalizer, AND the produced
   MIDI passes ALL THREE §4 tolerance thresholds against the §3
   reference. Stage-06 would no longer NEED the pretty_midi fallback
   (Stage-06 is NOT migrated this cycle regardless).
2. **`QUANTIZATION_REDEFINED_GAP`** — mscore3 native cannot be made
   byte-deterministic × 2 on the fixture under any tested flag
   combination, BUT one of:
     (a) the P2 normalizer collapses the observed duration drift below
         the §4 tolerance envelope (event count still preserved), OR
     (b) any P3 backend is byte-deterministic × 2 AND preserves event
         count within §4 tolerance.
   A new anchor (P2 normalizer script and/or P3 backend adapter) is
   documented under `scripts/score_bridge_v2/` as a peer to the c8
   `scripts/score/bridge.py`; underlying mscore3 real-audio-input
   nondeterminism is codified as a new locked anti-pattern.
3. **`QUANTIZATION_STILL_GAP`** — none of P1/P2/P3 produces a byte-
   deterministic × 2 path preserving event-count fidelity on the
   fixture. The pretty_midi fallback in Stage-06 is elevated from
   workaround to primary path with a documented tolerance envelope;
   mscore3 on real-audio-derived MusicXML is codified as a new locked
   anti-pattern; a fetchability-ladder-style ledger records the failure
   modes per probe for future cycles.

## 8. Emitted artifacts (deterministic paths)

- `data/score_bridge_real_audio/rubric_hash.txt` — SHA-256 of this
  rubric doc (this file); committed alongside this doc.
- `data/score_bridge_real_audio/verdict.json` — MUST embed
  `rubric_hash` byte-equal to the above.
- `data/score_bridge_real_audio/anchor_preservation.json` — 12+ read-
  only anchor SHAs pre/post byte-equal.
- `data/score_bridge_real_audio/probes/{p1_mscore3_flags,p2_normalizer,p3_alternative_backends}.tsv`
- `data/score_bridge_real_audio/probes/p2_property_attribution.json`
- `data/score_bridge_real_audio/fetchability_ladder.jsonl`
- `docs/score_bridge_real_audio_quantization_report.md`

## 9. Non-negotiables

- `scripts/score/bridge.py` (c8 anchor) is **byte-identical** pre/post.
- `scripts/recreate_v0/run_pipeline.py` (c37 clone-0 anchor — contains
  the pretty_midi fallback) is **byte-identical** pre/post.
- The pretty_midi fallback is **NOT deleted** regardless of verdict.
- No PRNG anywhere; only SHA-256 tiebreak (this cycle uses no tiebreak
  — enumeration is total on P1 flag axes).
- Interpreter guard `#!/usr/bin/python3` on every new script under
  `scripts/score_bridge_v2/`.
- No `import scripts.tex.render_effects_layered`, no
  `import scripts.classifier.sidecar_nonfactor`, no
  `import scripts.rules.sampling.i4_stratified`, no c31 palette imports.
- No forbidden state-extraction methods (`get_state`, `save_state`,
  `save_preset`, `load_state`, `set_state`) — not relevant to this
  scope; AST test still runs.

## 10. Fixture equality with c37 anchor

A test enforces `sha256(data/score_bridge_real_audio/inputs/merged_real_audio.musicxml)
== 95de5356fc127e8ff2b3c5153a950b35ddd4836b1ec1f40d658f41ebb73e1592`.
If the equality fails, the fixture was mutated or a wrong file was
copied — the test refuses to run further probes.
