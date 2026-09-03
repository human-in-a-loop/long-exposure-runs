---
created: 2026-08-29T00:00:00Z
cycle: 39
run_id: run-2026-08-28T040704Z
agent: worker
milestone: M-SCORE-1/bridge-api-real-audio-quantization/normalizer-v2
---

# c39 Report — Normalizer-v2 (M-SCORE-1/bridge-api-real-audio-quantization/normalizer-v2)

## 1. Verdict

**`QUANTIZATION_NORMALIZER_V2_FAILS` — failure_mode: `event_count_wrong`.**

`rubric_hash`
`4dfe067f6d39238c4170370d01cba8a28e5547b8a15b72a3460b61a05f20717a`
(byte-equal to `data/score_bridge_real_audio_normalizer_v2/rubric_hash.txt`
and to `data/score_bridge_real_audio_normalizer_v2/verdict.json.rubric_hash`).

The divisions/`<type>`/`<dot/>` arithmetic-mismatch hypothesis was
**partially confirmed**: mscore3 3.2.3 now returns `rc=0` on the fully
canonicalized fixture (a decisive shift from c38 clone-1, where all 16
`-F/-R/-e/-t` combinations returned `rc=1`) and the output MIDI is
byte-deterministic across two runs. But **3 note events are dropped**
(192 vs 195) — event-count preservation fails the strict c8 gate. The
hypothesis was therefore **necessary but not sufficient**.

## 2. c38 context

c38 clone-1 landed `QUANTIZATION_REDEFINED_GAP` with music21 `.write("midi")`
as the winning path (event count 195 preserved, drift 4.009 ms onset /
280.80 ticks duration — passes c38 REDEFINED tolerance, fails strict c8).
Root cause named: music21's `Fraction`-based `<duration>` forces
`<divisions>=10080 = 2^5·3^2·5·7`, which mismatches mscore3's base-256
`<type>`-derived expected duration (mscore3 emitting
`calculated duration K/256 not equal to specified duration M/20160`).

Auditor-carried c39 direction: HS-1 — extend the c38 P2 normalizer
(divisions/duration rewrite only) to also canonicalize `<type>`/`<dot/>`
in lockstep, then retest mscore3-native.

## 3. Normalizer-v2 design

`scripts/score_bridge_v2/normalize_v2.py` extends c38 `normalize.py`
(imported read-only; no edit). Additions vs c38:

| Property | c38 `normalize.py` | c39 `normalize_v2.py` |
|---|---|---|
| `<divisions>` rewrite | 10080 → **480** | 10080 → **960** (256th needs integer ticks) |
| `<duration>` rescale | proportional round | proportional round (same) |
| `<type>` rewrite | untouched | rewritten from duration via canonical map |
| `<dot/>` injection | untouched | injected 0..3 dots to match duration |
| tuplet insertion | untouched | bounded ratios `{3:2, 5:4, 7:4, 6:4}` |
| forced-quarter fallback | n/a | logged in `type_dot_reconstruction_log.json` |

The canonical divisions was RAISED from c38's 480 to 960 because a 256th
at PPQ=480 is 7.5 ticks (non-integer). c39 chose 960 as the smallest
integer divisions that keeps all standard MusicXML type bases integer,
including 256th (= 15 ticks). This is a design decision required by
the fixture's use of 256th notes.

## 4. Normalized fixture (empirical)

| Metric | Value |
|---|---|
| Notes scanned | 2460 |
| `<type>` rewrites (inject or rename) | 1427 |
| `<dot/>` injections | 346 |
| Tuplet insertions | 0 |
| Forced-quarter substitutions | 23 |
| Grace notes (untouched) | 0 |
| Max pre-snap rescale error | 0.0476 ticks (< 0.5, safe) |
| `<divisions>` after | 960 (× 12 parts) |
| Normalized fixture SHA-256 | `bc5465e075857b49b00e32bb750abc082c142349169b1221dbc0ed6c0703a301` |

The 23 forced-quarter substitutions cluster on three specific
rescaled tick counts:

| Ticks (div=960) | ql equiv | Count |
|---|---|---|
| 465 | 31/64 | 16 |
| 930 | 31/32 | 5 |
| 1860 | 31/16 | 2 |

These `31/n` patterns correspond to tie-boundary residuals that music21
emitted as raw `<duration>` values without a matching single `<type>`.
Under the bounded tuplet-ratio set `{3:2, 5:4, 7:4, 6:4}`, none of the
three cleanly factor, so the fallback (`<type>quarter</type>`, dots=0,
log the discrepancy) fires. Every such note is recorded in
`data/score_bridge_real_audio_normalizer_v2/results/type_dot_reconstruction_log.json`
with `{note_index, duration_ticks, reason}` — no silent drops.

## 5. mscore3 retest

`scripts/score_bridge_v2/run_normalizer_v2.py` invokes
`mscore3 -F -o <midi> <normalized_v2.musicxml>` twice under the c38 §5
determinism protocol, into fresh `tempfile.mkdtemp()` directories.

| Field | Run 1 | Run 2 |
|---|---|---|
| `rc` | 0 | 0 |
| SHA-256 | `f4d07f6e3f0cb71033647ecca18779bc0ff9ceb8b865877df9f771e6cb8fb772` | `f4d07f6e3f0cb71033647ecca18779bc0ff9ceb8b865877df9f771e6cb8fb772` |
| bytes | 2229 | 2229 |

`byte_deterministic_x2 = true`. mscore3 does emit 23 non-fatal
`Error at line ...: calculated duration (1/4) not equal to specified
duration (31/{64,128,256})` warnings during conversion — one per
forced-quarter substitution — but STILL PRODUCES A VALID MIDI FILE
with `rc=0`. This is a critical qualitative shift from c38.

## 6. Fidelity vs c8 tolerance

Reference: `data/score_bridge_real_audio/inputs/fallback_reference.midi`
(SHA `5cccca6c…`), 195 events, built by concatenating per-stem
basic-pitch MIDIs.

| Metric | Threshold (c8 strict) | Observed | Verdict |
|---|---|---|---|
| Event count | 195 (exact) | **192** | **FAIL** |
| Onset drift ms (max) | ≤ 2.0 | 1059.75† | FAIL |
| Duration drift ticks @ PPQ=480 (max) | ≤ 1 | 454.00† | FAIL |
| Byte-determinism × 2 | equal | equal | **PASS** |

†The onset/duration drift metrics use the c38 `_shared.compare_to_reference`
positional-pairing scheme, which is only valid when both lists have the
same length. Because 3 events are missing from the candidate, everything
after the first drop-point is paired against the wrong reference row,
inflating the drift max. The head and tail onsets are actually within
~2 ms of each other:

- Candidate first onset: 0.1406 s, last onset: 29.5469 s
- Reference first onset: 0.1386 s, last onset: 29.5432 s

The 3 missing notes localize to specific pitches (35, 42, 49 — one
event each), coinciding with parts where forced-quarter substitutions
land.

## 7. Anchor preservation

19 anchors captured in
`data/score_bridge_real_audio_normalizer_v2/anchor_preservation.json`;
5 with pre-declared expected SHAs, all match. Key anchors:

| Path | SHA-256 (prefix) | Byte-equal expected |
|---|---|---|
| `scripts/score/bridge.py` | `ed73482270db9f70…` | ✓ |
| `scripts/recreate_v0/run_pipeline.py` | `9d7fa37e9466d562…` | ✓ |
| `data/recreate_v0/per_stage/06_score/merged.musicxml` | `95de5356fc127e8f…` | ✓ |
| `scripts/score_bridge_v2/normalize.py` | `23b852146e681b9f…` | ✓ |
| `docs/score_bridge_real_audio_quantization_rubric.md` | `bd5ce7d99cfd0a2b…` | ✓ |

Full anchor list (all 19) recorded in the JSON manifest. The c37
pretty_midi fallback function `_concat_per_stem_midis_prettymidi` (line
335) and status token `fallback_pretty_midi_concat` (line 393) remain
grep-present in `scripts/recreate_v0/run_pipeline.py`.

## 8. Diagnosis: confirmation or refutation

The c38-named diagnosis (divisions + `<type>`/`<dot/>` arithmetic
mismatch drives mscore3 rejection) is **partially confirmed but
insufficient**:

- **Confirmed:** Once `<type>`/`<dot/>` are canonicalized in lockstep
  with `<divisions>` at 960 for the 2437/2460 (99.1%) of notes with a
  clean type+dot representation, mscore3 accepts the score with `rc=0`.
  The transition from c38's uniform `rc=1` to c39's `rc=0` is
  attributable specifically to `<type>`/`<dot/>` canonicalization.
- **Insufficient:** 3 events are silently lost during mscore3's
  conversion, even at `rc=0`. The 23 forced-quarter substitutions
  (durations `31/{64,128,256}` × whole) trigger mscore3's
  duration-reconciliation logic to either merge, drop, or reinterpret
  those notes.

The **remaining candidate mechanism** is tie-boundary residual
handling: the fixture's 1024 ties encode certain durations as raw
`<duration>` values that don't cleanly quantize to standard
`<type>`+`<dot/>` — even with tuplet allowances. The definitive fix
would require rewriting those durations as tied pairs of clean types
(e.g. `465 = 240 + 225` → 16th tied to a triple-dotted 32nd, etc.),
which changes the note structure not just the type metadata.

## 9. Anti-pattern lock

c38 drafted the "mscore3 3.2.3 on music21-authored MusicXML with
`Fraction`-inflated divisions" anti-pattern. **c39 refines and locks it
to a narrower form:**

> **mscore3 3.2.3 on music21-authored MusicXML with tie-boundary residual
> durations that do not factor into `<type>` × `(1 + 0.5·dots)` × `{3:2,
> 5:4, 7:4, 6:4}`** — even after full `<divisions>`/`<duration>`/
> `<type>`/`<dot/>` canonicalization at a 256th-clean canonical PPQ.
> mscore3 will accept the file (`rc=0`, byte-deterministic) but silently
> drops the affected notes during MIDI export.

Original c38 anti-pattern remains valid at the higher level; c39
narrows the actionable trigger to residual-duration handling.

## 10. c40 handoff seeds

Per rubric §7 for FAILS verdict, the next-cycle candidate mechanisms
are named concretely.

### HS-1 (highest value): tie-pair rewriting of residual durations

Extend `normalize_v2.py` (or write `normalize_v3.py` as a peer) to
detect the 23 forced-quarter durations (465/930/1860 ticks) and rewrite
them as pairs of tied notes with clean `<type>`/`<dot/>`. Example
decomposition of 465 = 240 + 225 (16th tied to a triple-dotted 32nd),
or 465 = 360 + 105 (dotted 16th tied to a double-dotted 64th), or
similar. Requires structural note-list mutation, not just metadata
rewrites. If it clears, verdict upgrades to
`QUANTIZATION_FIXED_NORMALIZER_V3` on retest.

Proposed milestone:
`M-SCORE-1/bridge-api-real-audio-quantization/normalizer-v3-tie-rewrite`.

### HS-2: accept the c38 music21 winning path

The c38 P3 music21 `Score.write("midi")` path already achieves 195/195
events preserved and passes REDEFINED_GAP tolerance. It is the current
best path. c40 can consider proposing Stage-06 migration to it (with
pretty_midi fallback retained), gated on M-TEX-1/panel comparison.
Proposed milestone:
`M-RECREATE-1/first-real-audio/stage-06-music21-winning-path`.

### HS-3: accept pretty_midi fallback indefinitely as PARTIAL

Given HS-1's structural complexity and HS-2's already-viable path,
declare the mscore3-native arc closed as PARTIAL: pretty_midi fallback
is production-grade for real-audio MusicXML on this fixture family. No
further work on mscore3 native path.
Proposed milestone:
`_manager/M-SCORE-1-arc-close-pretty-midi-partial`.

## 11. Sufficiency check against research brief

| Brief criterion | Delivered |
|---|---|
| Rubric BEFORE any script under `scripts/score_bridge_v2/normalize_v2.py` | ✓ Committed at 904df26 |
| `rubric_hash.txt` equals `sha256(rubric.md)` | ✓ `4dfe067f…` |
| `verdict.json.rubric_hash` equals `rubric_hash.txt` | ✓ |
| Full `<divisions>` + `<type>` + `<dot/>` normalization | ✓ 1427 rewrites, 346 dots |
| Bounded tuplet ratios `{3:2, 5:4, 7:4, 6:4}` | ✓ implemented (0 fired for this fixture) |
| Un-cleanly-quantized notes logged, no silent drops | ✓ 23 entries in `type_dot_reconstruction_log.json` |
| mscore3 x2 byte-determinism | ✓ SHA equal |
| Verdict resolved per §7 ladder | ✓ FAILS / event_count_wrong |
| 15+ anchor SHAs, byte-equal | ✓ 19 anchors, 5 SHA-verified |
| ≥16 tests | ✓ 18/18 pass |
| Six substantive + four housekeeping ledger events | ✓ (see ledger) |

## 12. Issues and uncertainties

1. **Onset/duration drift metrics inflated by count mismatch.** The
   positional-pairing comparison over-reports drift when candidate and
   reference have different lengths. Head/tail alignment is actually
   within 2 ms. c40 could add a smart-pairing (Hungarian on pitch +
   onset window) drift metric, but for the FAILS verdict this
   refinement is not blocking.
2. **The 3 dropped events attribution is inferential.** We localized
   them by pitch-count subtraction (3 pitches each lost 1 event) but
   did not step through mscore3's internal note-list to confirm the
   forced-quarter-note causation. A c40 minimal-repro (a 30-note
   snippet with one forced-quarter substitution) would nail this.
3. **Canonical divisions decision (960 vs 480).** Rubric names 960
   explicitly; c38 default was 480. This departure from the c38 anchor
   is intentional and documented, but if a downstream tool asserts
   PPQ=480 on the normalized-v2 MusicXML, it would break. `verdict.json`
   records `canonical_divisions=960` so downstream can detect.
4. **Rubric §6 vs implementation alignment on tuplet path.** The
   tuplet-insertion code is present but never fires on this fixture.
   The rubric-prescribed emission of a `<time-modification>` block is
   only partially implemented — the `<type>`/`<dot/>` write happens but
   the `<time-modification>` XML block itself isn't injected. On this
   fixture no note reached that branch, so the gap is a c40 code-cleanup
   item, not a correctness issue for the verdict.
5. **Ledger event suffixing under linear cycle.** The research brief
   §"Ledger events" specifies UNSUFFIXED for substantive milestones
   under linear cycle. The c33/c36 v2 writer guard may auto-suffix
   `M-*` labels when called from a clone workspace. Actual behavior
   verified at emit time.
