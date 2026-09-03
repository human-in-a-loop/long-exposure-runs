---
created: 2026-08-29T00:00:00Z
cycle: 39
run_id: run-2026-08-28T040704Z
agent: worker
milestone: M-SCORE-1/bridge-api-real-audio-quantization/normalizer-v2
---

# Rubric — c39 Normalizer-v2 (M-SCORE-1/bridge-api-real-audio-quantization/normalizer-v2)

**Frozen BEFORE any script under `scripts/score_bridge_v2/normalize_v2.py` or
`scripts/score_bridge_v2/run_normalizer_v2.py` exists.** Enforced via mtime +
git-log dual gate. Rubric SHA-256 recorded in
`data/score_bridge_real_audio_normalizer_v2/rubric_hash.txt` and embedded
verbatim in `data/score_bridge_real_audio_normalizer_v2/verdict.json.rubric_hash`.

## 1. Fixture

- **Path:** `data/recreate_v0/per_stage/06_score/merged.musicxml` (c37 clone-0
  anchor, byte-equal to c38 `data/score_bridge_real_audio/inputs/merged_real_audio.musicxml`).
- **SHA-256:** `95de5356fc127e8ff2b3c5153a950b35ddd4836b1ec1f40d658f41ebb73e1592`.
- **Size:** 635231 bytes.
- **Structure (empirical, c39 pre-run):** 2460 `<duration>` events, 1054
  `<type>` tags, 0 `<dot/>`, 0 `<time-modification>`, 1024 ties, unique
  `<divisions>=10080` across 12 parts.

## 2. Reference

Pretty_midi fallback reference at `data/score_bridge_real_audio/inputs/fallback_reference.midi`,
SHA-256 `5cccca6c48820e26be95aae125679b4002ccab1a28b9aea13500066d213ac599`, 195
note events. Constructed in c38 by concatenating per-stem basic-pitch MIDIs
from `data/recreate_v0/per_stage/05_basic_pitch/{bass,drums,other}.mid`.

## 3. c8-frozen tolerance thresholds (STRICT gate)

- Event count == 195 (exact).
- Onset drift max ≤ 2 ms (relative to reference PPQ=480 grid).
- Duration drift max ≤ 1 tick at PPQ=480.

## 4. c38 REDEFINED_GAP tolerance envelope (RELAXED gate)

Preserved for reference; onset ≤ 5 ms and duration ≤ 512 ticks. Not used by
the c39 verdict resolver directly (see §7).

## 5. Byte-determinism protocol (identical to c38 §5)

Two independent invocations of mscore3 under identical pinned environment:

- `PYTHONHASHSEED=0`
- `SOURCE_DATE_EPOCH=1730000000`
- `TZ=UTC`
- `LC_ALL=C.UTF-8`
- `OMP_NUM_THREADS=1`, `MKL_NUM_THREADS=1`, `OPENBLAS_NUM_THREADS=1`
- `QT_QPA_PLATFORM=offscreen`

Each run writes into a fresh `tempfile.mkdtemp()` directory to prevent
cross-contamination. Byte-determinism means SHA-256 of the two produced
MIDI files must be identical.

## 6. Scope of normalize_v2 (what it adds beyond normalize.py)

Beyond c38 `normalize.py` (which rewrites `<divisions>` and rescales
`<duration>` values only), `normalize_v2.py` also canonicalizes per-note
type/dot metadata so mscore3's base-256 `<type>`-derived expected duration
matches the specified `<duration>` bit-for-bit at the new
`<divisions>=CANONICAL_DIVISIONS`. The canonical value MUST be chosen so
that every standard `<type>` in the fixture maps to an integer tick count.
Given the fixture contains `256th` (base 1/64 of a quarter), the canonical
value is `CANONICAL_DIVISIONS = 960` (chosen this cycle to accommodate
256th = 15 ticks). This differs from c38 `normalize.py`'s default of 480
because 256th at PPQ=480 is 7.5 (non-integer). The chosen value must be a
multiple of 64 and of `music21`'s smallest expected division. The rubric
explicitly names `CANONICAL_DIVISIONS = 960` as the frozen choice.

For each `<note>` element in the normalized-v2 output:

1. Compute the canonical duration ticks `d_new` (from the c38 normalize.py
   rescale of `<divisions>=10080` → `<divisions>=960`, with rounding).
2. Enumerate valid `(type_name, dot_count)` pairs where
   `type_ticks(type_name, dot_count) == d_new`. `type_ticks` is defined
   as `base(type_name) * (2 - 2^-dot_count)` scaled by
   `CANONICAL_DIVISIONS`. Standard MusicXML type bases: `whole=4`, `half=2`,
   `quarter=1`, `eighth=1/2`, `16th=1/4`, `32nd=1/8`, `64th=1/16`,
   `128th=1/32`, `256th=1/64` (in quarter-length units).
3. If exactly one clean pair exists, rewrite the `<type>` text to the
   canonical name and inject the corresponding number of `<dot/>` siblings
   immediately after `<type>`. Existing `<dot/>` elements are removed
   first, then the new set is inserted.
4. If no clean `(type, dot)` pair exists, attempt tuplet insertion via
   `<time-modification>` blocks with `actual/normal` ratios drawn from
   the frozen bounded set `{(3,2), (5,4), (7,4), (6,4)}`. Emit the tuplet
   block adjusted to the note.
5. If neither approach succeeds, force `<type>quarter</type>`, remove any
   `<dot/>`, and record the discrepancy in
   `data/score_bridge_real_audio_normalizer_v2/results/type_dot_reconstruction_log.json`
   as `{note_index, original_duration, new_duration, reason}`. The note is
   NOT silently dropped.

## 7. Verdict resolution

The runner (`scripts/score_bridge_v2/run_normalizer_v2.py`) invokes
mscore3 twice on the normalized-v2 fixture under the c38 P1 baseline flag
row (`mscore3 -F -o <midi> <xml>`). It records: `rc1`, `rc2`, `sha1`, `sha2`,
`event_count`, `onset_drift_ms_max`, `duration_drift_ticks_max`.

Resolution ladder (evaluated top-down):

1. **`QUANTIZATION_FIXED_NORMALIZER_V2`** — `rc1==0` AND `rc2==0` AND
   `sha1==sha2` AND `event_count==195` AND `onset_drift_ms_max<=2.0` AND
   `duration_drift_ticks_max<=1`.
2. **`QUANTIZATION_STILL_REDEFINED_GAP`** — `rc1==0` AND `rc2==0` AND
   `sha1==sha2` AND `event_count==195` AND (`onset_drift_ms_max>2.0` OR
   `duration_drift_ticks_max>1`). The diagnosis (divisions + `<type>` /
   `<dot/>` arithmetic mismatch is the pathology) is confirmed; drift is
   real but bounded.
3. **`QUANTIZATION_NORMALIZER_V2_FAILS`** — otherwise. Named failure
   sub-mode recorded in `verdict.json.failure_mode` ∈
   `{rc_nonzero, sha_mismatch, event_count_wrong}`. Divisions/`<type>`
   hypothesis refuted; the report names the specific c40 candidate
   mechanism.

## 8. Explicit non-goals

- No fifth probe on the fixture.
- No music21 `Fraction`→`float` coercion tweaks.
- No lilypond backend re-attempt.
- No edit to c38 `scripts/score_bridge_v2/normalize.py` or any other c38
  script.
- No edit to c37 `scripts/recreate_v0/*` or c8 `scripts/score/bridge.py`.
- No removal or edit of the pretty_midi fallback path in
  `scripts/recreate_v0/run_pipeline.py`.
- No expansion of the fixture set.

## 9. Anchor preservation

The verdict's `anchor_preservation.json` must list 15+ anchor SHAs, all
byte-equal pre/post c39 execution:

- c8 `scripts/score/bridge.py`.
- c37 `scripts/recreate_v0/{run_pipeline, run_all, select_song, __init__}.py`.
- c37 `data/recreate_v0/per_stage/06_score/merged.musicxml`.
- c38 `scripts/score_bridge_v2/{__init__, _shared, normalize, probe_p1_mscore3_flags, probe_p2_normalizer, probe_p3_alternative_backends, verdict, run_all}.py` (all 8 files).
- c38 `data/score_bridge_real_audio/{rubric_hash.txt, verdict.json, anchor_preservation.json}` (3 files).
- c38 `docs/score_bridge_real_audio_quantization_{rubric, report}.md` (2 files).

## 10. Test coverage (≥16 cases)

Per the research brief §Test coverage. Enumerated in
`tests/test_score_bridge_normalizer_v2.py`.
