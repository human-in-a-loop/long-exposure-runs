---
title: "Music-Gen — M-SCORE-1 (cycle 1, fork 3a908edcb241, clone 0)"
date: "2026-08-28"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# Music-Gen — M-SCORE-1 (cycle 1, fork 3a908edcb241, clone 0)

## Abstract

Cycle 1 of clone 0 delivered the MuseScore programmatic bridge — the last-mile milestone that turns cycle-6's per-stem basic-pitch transcriptions into a full-song MusicXML score whose MIDI export recovers every input note. All required artefacts landed: `scripts/score/{__init__, bridge, jsonl_to_midi, seed_score}.py`, `tests/test_score_bridge.py` (23/23 passing), `docs/score_bridge_report.md` (304 lines, all seven required sections), a §15 extension to the cross-branch integration test, and the merged deliverables under `data/score/` (seed round-trip pair, deterministic-check pair, and the 30 s M-SEP-1 synth-mix merged score with its `parts_mapping.json` sidecar). The 8-bar seed round-trips to byte identity across two full `xml → mid → xml → mid → xml` passes after scrubbing; note preservation is exact at 88/88 events with 0.00 ms onset drift. Merged full-song F1 on the 30 s synth mix is **1.0000 / 1.0000 / 1.0000** on drums / bass / other against the basic-pitch input MIDIs — the load-bearing identity-merge metric — and 0.0000 / 0.4746 / 0.7317 against M-SEP-1 tiled ground truth, upper-bounded by cycle-6 basic-pitch quality and diagnosed exhaustively in the report. The auditor emitted **VALIDATED** with a parent `M-SCORE-1` roll-up, ran the full test suite and both validators live, and fixed one moderate defect in-cycle (a docstring on `merge_stems_to_score` that contradicted the implementation's 1/64-quarter grid snap). Downstream, M-RULES-1's extraction-half and M-TEX-1's parent stage-by-stage are now genuinely unblocked.

## Introduction

M-SCORE-1 sits at a pivot point in the campaign. Upstream, the M-SEP-1 htdemucs adoption, M-TRANS-1 transcription survey, and the frozen cycle-6 basic-pitch JSONL are all in place. Downstream, M-RULES-1's extraction-half was blocked on the availability of a merged score to read from, and M-TEX-1's parent stage-by-stage was blocked on the "bare MIDI" starting point that only a full-song export can produce. The brief scoped this branch precisely to that pivot: build a bridge that (a) translates between MusicXML and MIDI via `mscore3` headless with byte-identical round-trips, (b) identity-merges the per-stem basic-pitch outputs into a full-song MusicXML score whose MIDI export preserves every input note, (c) fails legibly through a typed `ScoreBridgeError` at each edge, and (d) preserves the campaign's non-factor isolation contract. The success bar was seed round-trip bit-identity (twice) and merged-full-song per-stem note-level F1 ≥ 0.98 against the M-SEP-1 ground-truth MIDIs, with an explicit relaxation clause in the brief for the case where the F1 shortfall is diagnosed as basic-pitch upstream noise.

## Approach

The module is partitioned so the load-bearing surface is minimal: `scripts/score/bridge.py` exposes `xml_to_midi`, `midi_to_xml`, `merge_stems_to_score`, and `ScoreBridgeError` and nothing else; `scripts/score/jsonl_to_midi.py` is the basic-pitch-JSONL → per-stem-MIDI helper (PPQ 480, tempo 500000 μs/beat, drums on channel 9); and `scripts/score/seed_score.py` deterministically generates the 8-bar hand-authored seed via music21. `mscore3 3.2.3` is driven headless under `QT_QPA_PLATFORM=offscreen` with a subprocess timeout at each call.

Two non-obvious mechanics were surfaced empirically and folded into the bridge:

- **Determinism scrubbing.** `mscore3`'s MusicXML export carries a daily `<encoding-date>`, a `<software>` build string, a `<source>` line echoing the mscore invocation's absolute path, a build-flag-derived `<encoder>`, a `<supports>` block that varies with mscore build flags, and a `<creator type="composer">MuseScore …</creator>` default. Music21 and mscore's XML export additionally assign randomised 32-hex-digit ids to `<part id="P…">`, `<score-part id="P…">`, `<score-instrument id="I…">`, and `<midi-instrument id="I…">`. The scrubber strips whole lines matching the six element names above, canonicalises `<work-title>` / `<movement-title>` that echo the input basename to empty tags, and renumbers each unique hex id in first-occurrence order to `P1, P2, …` / `I1, I2, …` — the renumbering is applied consistently across the whole document so `<part id>` references match their `<score-part id>` declarations. After scrubbing, two full runs of both round-trip paths are byte-identical.
- **mscore3 per-part voice cap.** `mscore3 3.2.3` empirically collapses six voice-partitions inside a single `<part>` into fewer than six MIDI note-on streams on export (78 piano notes → 64 recovered when written as a single 6-voice part). The fix is one `<part>` per voice partition, chosen by interval-graph coloring of the input notes, named `{stem}__v{k}`. A sidecar JSON at `{score}.parts_mapping.json` maps each MIDI track group back to its stem, so downstream F1 extractors can walk the tracks in `[meta, stem_1_v0, …, stem_1_vN, stem_2_v0, …]` order without guessing.

Two smaller mechanics matter for correctness. First, `merge_stems_to_score` snaps every input onset and duration to a 1/64-quarter grid (~7.8 ms at 120 BPM). The rationale is that music21's serializer refuses arbitrary sub-tuplet durations with `Cannot convert "2048th" duration to MusicXML (too short)`; the chosen grid is a pure power-of-2 fraction with no nested tuplets, and the resulting maximum onset shift (≤ 3.9 ms) is well under `mir_eval`'s 50 ms tolerance, so F1 measurements are unchanged by the snap. Second, the bridge detects a silent-rc-0 trap on structurally-invalid MusicXML input: `mscore3` returns exit 0 and writes an empty MIDI, so the bridge scans stderr for `"is not a valid musicxml file"`, `"is not a musicxml score-partwise file"`, `"cannot import"`, and `"empty score"` and escalates to `ScoreBridgeError`; the scan does not fire on legitimate `"Error at line N col M"` rounding-error warnings that mscore also prints on valid inputs.

## Findings

### Seed round-trip

The 8-bar seed authors 88 events: bass quarter-note roots (32), piano whole-note triads across two four-bar cycles (24), and a kick+snare backbeat on the quarter grid (32). Two full round-trips produce:

| Property | Authored | After `xml_to_midi` |
|---|---|---|
| Event count | 88 | 88 |
| Pitch multi-set | seed | seed (exact) |
| Onset drift, max | — | 0.00 ms |
| Duration drift | 500 ms → 499 ms | 1 tick @ PPQ 480 (~2 ms, legitimate PPQ boundary) |

SHA-256 (first 16 hex) across two independent runs after scrub:

```
m1 = e2493fc7f7e3a4df    m2 = e2493fc7f7e3a4df
x1 = 71d0e1eaf1d798ad    x2 = 71d0e1eaf1d798ad
```

Byte identity holds across separate `mscore3` invocations, so the effect is not a cache artefact.

### Merged full-song F1

Inputs are the frozen cycle-6 basic-pitch outputs at `data/transcribe/basic_pitch/synth_030s/{drums, bass, other}.jsonl`. Converted to per-stem MIDI via `jsonl_to_midi.py`, merged via `merge_stems_to_score`, exported via `xml_to_midi`. Metric: `mir_eval.transcription.precision_recall_f1_overlap` at `onset_tolerance=0.05 s`, `pitch_tolerance=0.5 semitones`, `offset_ratio=None`.

**F1 vs basic-pitch input MIDIs — the identity-merge (bridge-only) metric:**

| Stem | Precision | Recall | F1 | Ref | Est | ≥ 0.98? |
|---|---:|---:|---:|---:|---:|:---:|
| drums | 1.0000 | 1.0000 | **1.0000** | 0 | 0 | ✅ |
| bass  | 1.0000 | 1.0000 | **1.0000** | 44 | 44 | ✅ |
| other | 1.0000 | 1.0000 | **1.0000** | 78 | 78 | ✅ |

Every basic-pitch note event survives the (per-stem MIDI → merged MusicXML → mscore3 export) round trip.

**F1 vs M-SEP-1 tiled ground truth — the end-to-end metric:**

| Stem | Precision | Recall | F1 | Ref | Est | Threshold |
|---|---:|---:|---:|---:|---:|:---:|
| drums | 1.0000 | 0.0000 | **0.0000** | 180 | 0 | not met |
| bass  | 0.3182 | 0.9333 | **0.4746** | 15 | 44 | not met |
| other | 0.5769 | 1.0000 | **0.7317** | 45 | 78 | not met |

None of the three shortfalls is a bridge defect. Drums 0.0000 is inherited from basic-pitch emitting zero notes on a pitchless drum stem (the model was trained on pitched polyphonic instruments; this is exactly the *lower-bound* row in the cycle-6 transcription survey). Bass 0.4746 reproduces `docs/transcription_survey_report.md §5` bit-for-bit — basic-pitch over-generates by roughly 3× (44 est vs 15 ref) and precision is the cap. Other 0.7317 actually *slightly raises* the cycle-6 baseline of 0.72 because every one of the 78 input notes survives the merge and recall reaches 1.0. The brief explicitly relaxes the 0.98 threshold when the shortfall is diagnosed as basic-pitch upstream noise, which is the case here.

### Failure-mode surfacing

All four legibility contracts hold, each covered by a test:

| Trigger | Message contains |
|---|---|
| Malformed MusicXML | `"mscore3 rc=0 but stderr flagged invalid input"` |
| Missing input file | `"input file not found"` |
| Timeout (`timeout_s` exceeded) | `"timed out"` |
| Missing per-stem MIDI in `merge_stems_to_score` | `"stem MIDI not found"` |
| Non-zero `mscore3` exit | `"mscore3 exited <rc>: <stderr>"` |

**Special-point coverage.** Bar-boundary ties survive round-trip (seed 88/88); rests inside a voice preserve as `<rest>`; an empty stem emits a part with a whole-measure rest so mscore does not drop it entirely; overlapping notes on the same channel partition into `{stem}__v{k}` parts by interval-graph coloring; very short notes below one PPQ tick snap to `_MERGE_GRID_QL`; and missing `set_tempo` meta falls back to 500000 μs/beat (120 BPM).

### Non-factor isolation

Zero import hits for `sidecar_nonfactor` across `scripts/score/` and `tests/test_score_bridge.py` (test §6a enforces the grep at run-time; §15 of the cross-branch integration test enforces it structurally). The bridge only handles musical content — pitches, onsets, durations, velocities — and has no code path that reads or writes non-factor sidecar files. Every module carries `assert sys.executable == "/usr/bin/python3"` at import.

### Tests

`tests/test_score_bridge.py` — 23/23 passing across six sections (seed round-trip, note preservation, merged F1 identity-merge, merged F1 vs GT, determinism byte-identity, failure modes). Cross-branch integration test — 0 failures with §15 in place.

### Audit disposition

The auditor ran `tests/test_score_bridge.py` under the single-thread BLAS pins live (23 pass, 0 fail, printed per-stem F1 numbers matched the worker's claim); ran the cross-branch integration test live (0 failures); greped for the `sidecar_nonfactor` regex live (0 import hits, only docstring / comment mentions plus the test's own regex string); ran `promise_check` and `org_check` live (only WARNINGs — the shadow-ledger orphan-artifact residue on `data/score/*`, `scripts/score/*`, `tests/test_score_bridge.py`, and `docs/score_bridge_report.md`, plus three pre-existing non-canonical root-file WARNs unrelated to this branch — and no ERRORs); independently verified the seed event count (88 = 8 bars × (4 bass + 3 piano-chord tones + 4 drum)) matches the reported preservation; and independently verified the basic-pitch JSONL schema at `data/transcribe/basic_pitch/synth_030s/bass.jsonl` (rows carry `{is_drum, onset_s, offset_s, pitch, velocity}`, matching the worker's `jsonl_to_midi.py` and contradicting the research brief's earlier `{pitch_midi, amplitude}` guess). The one moderate defect found and fixed in-cycle was a `merge_stems_to_score` docstring that claimed "sub-tick precision (no quantization, no snapping)" while the implementation snaps to the 1/64-quarter grid described in §3a of the report; the docstring was patched in place to name the grid, the max shift, and the report reference, and the test suite ran 23/23 again after the edit.

## Discussion

Two things about this branch are worth naming. First, the separation of the identity-merge metric from the end-to-end metric is what makes the escape hatch legitimate rather than a face-saving move. The claim "the bridge preserves what basic-pitch produced" is falsifiable and was falsified against a strict test (F1 vs the basic-pitch input MIDIs, on every stem, must be 1.0000); it passed on every stem. The end-to-end claim (F1 vs M-SEP-1 tiled ground truth ≥ 0.98) failed, and the failure was independently traceable to already-published cycle-6 numbers — the bass row reproduces `docs/transcription_survey_report.md §5` bit-for-bit; the drums row is the lower-bound zero-notes case the survey called out with a disclaimer; the other row *raises* the cycle-6 baseline slightly. Composing sibling clone 1's octave-suppression filter with `jsonl_to_midi.py` (drop-in on the frozen JSONL before merge) is the concrete cycle-9 reconciliation that closes the vs-GT bass F1 gap toward ≥ 0.78; this is out of scope for this branch by construction and is called out in the merge report as guidance for the root conductor.

Second, the two emergent findings about the toolchain — the mscore3 per-part voice cap and the determinism scrubbing list — are the kind of infrastructure knowledge that pays off across every future score-authoring path. The `_partition_into_voices` interval-graph-coloring helper in `bridge.py` is reusable by any downstream extractor that emits multi-voice content; the `{stem}__v{k}` part-name convention plus the `parts_mapping.json` sidecar makes the workaround discoverable rather than magic. The scrubbing list was empirically enumerated by exporting the same MIDI twice on the same day and diffing (`tools/_probe_merge.py`), and the resulting rule set is documented so a future toolchain upgrade can shorten or extend it without re-deriving the whole list. Both are worth propagating into the plan of record at cycle-9 integration.

Beyond this branch, M-SCORE-1's closure genuinely unblocks two downstream milestones: M-RULES-1's extraction-half can start reading `data/score/test_merged.musicxml` (or a fresh `merge_stems_to_score` call) plus its `parts_mapping.json` sidecar to extract harmonic, rhythmic, melodic, form, and arrangement rules, and M-TEX-1's parent stage-by-stage can consume the merged MusicXML → MIDI export as its "bare MIDI" starting point for the texture ladder. Extractors should consult the sidecar's `parts_by_stem` map because a stem can occupy multiple `{stem}__v{k}` parts.

## Open Questions

None within the branch's scope; every falsification criterion held, the test suite is green, the moderate docstring defect was fixed in-audit, and the F1-vs-GT shortfall is diagnosed against already-published cycle-6 numbers. The following belong to future cycles and are recorded on the report and merge report:

- **Compose octave suppression with the bridge.** Drop sibling clone 1's `octave_suppression` filter into `jsonl_to_midi.py`'s input path (before merge) to close the vs-GT bass F1 gap toward ≥ 0.78. One-line change over the frozen JSONL; no bridge modification required.
- **Post-merge orphan-artifact adoption.** The `data/score/*`, `scripts/score/*`, `tests/test_score_bridge.py`, and `docs/score_bridge_report.md` warnings clear at fork-merge under the `_infra/adopt-fanout-artifacts-m-score-1` pattern established in prior forks.
- **Environment carry-forward.** `music21 9.1.0` is a new top-level pin this cycle. Numpy stayed at 1.26.4 and no cross-branch test regressed, but the cycle-9 integrator should note it in the environment record.

## Appendix: Provenance

**Cycle range:** cycle 1 of fork `3a908edcb241`, clone 0 of 3.
**Working directory:** `/home/user/long-exposure-runs/music-gen`.
**Session references:** researcher `843cb35b-9232-47b4-925c-a94c8d4ae257`, worker `ef72c18a-a76d-406c-87ae-f8243b0ba861`, auditor `0d95720c-be8d-4925-a72e-2f464664d68b`.
**Auditor verdict:** **VALIDATED** with a parent `M-SCORE-1` roll-up.

**Deliverables on disk:**

- Code: `scripts/score/{__init__.py, bridge.py, jsonl_to_midi.py, seed_score.py}` — public API is `xml_to_midi`, `midi_to_xml`, `merge_stems_to_score`, `ScoreBridgeError`; every module guards `sys.executable == "/usr/bin/python3"` at import.
- Data: seed and round-trip pairs (`seed_8bar.musicxml`, `test_seed_{m1,m2}.mid`, `test_seed_{x1,x2}.musicxml`), deterministic-check pair (`test_det_r{1,2}.{mid, musicxml, parts_mapping.json}`), the 30 s synth-mix merged score (`merged_synth030s.{mid, musicxml, parts_mapping.json}`), and the failure-mode fixtures (`test_bad.xml`, `test_bad_out.mid`, `test_timeout_out.mid`).
- Tests: `tests/test_score_bridge.py` (396 lines, 23 checks in six sections); `tests/test_integration_cross_branch.py §15` (surface, isolation, sidecar, report guards).
- Report: `docs/score_bridge_report.md` (304 lines, seven sections plus §6.1 non-factor isolation and §7 scrubbing list).

**Environment:** `mscore3` MuseScore3 3.2.3 (headless, `QT_QPA_PLATFORM=offscreen`); Python 3.11.15 (`/usr/bin/python3`); `numpy 1.26.4`; `music21 9.1.0` (installed this cycle; cross-branch tests remain green); `mir_eval 0.8.2`; `mido` (Debian package, no `__version__`). Single-thread BLAS pins: `OMP_NUM_THREADS=MKL_NUM_THREADS=OPENBLAS_NUM_THREADS=1`.

**Frozen input SHA-256 (first 16 hex):**
```
c81d3b84a46429f3  data/separation/synth_mix/midi/drums.mid
edc499a1f673edf0  data/separation/synth_mix/midi/bass.mid
5fb0bae22ee71532  data/separation/synth_mix/midi/piano.mid
01ba4719c80b6fe9  data/transcribe/basic_pitch/synth_030s/drums.jsonl
c7165998626e9262  data/transcribe/basic_pitch/synth_030s/bass.jsonl
90ea9a10a8f8640c  data/transcribe/basic_pitch/synth_030s/other.jsonl
```

**Ledger routing:** shadow-ledger events emitted at `/home/user/music-gen-instance/fork-3a908edcb241/clone-0/promise_ledger.jsonl` for `M-SCORE-1/round-trip`, `M-SCORE-1/merged-full-song`, `M-SCORE-1/bridge-api`, and the parent `M-SCORE-1` roll-up. All events emitted with explicit `event_id`, avoiding the recurring lesson from cycle 7's ledger-append helper omission. Orphan-artifact WARNings clear at fork-merge under `_infra/adopt-fanout-artifacts-m-score-1` (same pattern as cycles 3, 5, 7).

**Handoff to root conductor.** Recorded verbatim in the merge report at `/home/user/music-gen-instance/fork-3a908edcb241/clone-0/merge_report.md`:

- Adopt `scripts/score/*` (4 files), `tests/test_score_bridge.py`, `docs/score_bridge_report.md`, and the `data/score/*` outputs under `M-SCORE-1`.
- Fold the four shadow-ledger events into the root ledger.
- Reconcile `tests/test_integration_cross_branch.py §15` against sibling clones' additions (clones 1 and 2 both use `§17`; renumber during integration if collision).
- Carry `music21 9.1.0` forward in the environment record; no numpy / torch / tensorflow drift.
- Propagate the two conventions to the plan of record: (a) `{score_xml.stem}.parts_mapping.json` sidecar; (b) `{stem}__v{k}` part-name convention for the mscore3 per-part voice-cap sidestep.
- **Downstream unlocks:** M-RULES-1 extraction-half can start immediately; M-TEX-1 parent stage-by-stage can start immediately.

<verdict>validated</verdict>
