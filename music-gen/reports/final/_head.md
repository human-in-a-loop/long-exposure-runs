# Music-Gen: A Deterministic, Recreation-First Pipeline for Ordinally-Rated Music Generation

*Run:* `run-2026-08-28T040704Z` · *Report date:* 2026-09-02

## Abstract

We report the design, construction, and current end-state of a
deterministic music-generation pipeline built around three commitments:
artefact-first evaluation (no scalar quality scores; a side-by-side
panel is the answer), recreation-before-generation (the pipeline must
close on a real rated song before its generation output is trusted),
and honest reporting of open ends (no in-progress milestone is
retroactively re-labelled to close a metric). The pipeline ingests
private 30-second music chunks through a three-model classifier
ensemble (PANNs / YAMNet / AST), separates them with `htdemucs_6s`,
transcribes pitch/onset/offset with `basic-pitch 0.4.0` under a tuned
octave-suppression grid, merges the four-stem transcriptions through
a determinism-scrubbed MuseScore 3 bridge (byte-identical across two
full MusicXML round-trips), reasons over a hash-deduplicated 76-row
typed rules ledger, and renders through an Ardour + DawDreamer +
open-plugin DAW stack whose Surge XT and Dexed palette instruments
render byte-deterministically across independent invocations,
deterministic-salt sweeps, and paired hosts within a pinned CPU
family. The M-TEX-1 texture panel reports mel, spectral, envelope,
and CLAP/VGGish embedding distances side by side and refuses to
aggregate. The M-EAR-1 ordinal listener (CORN head on three operator
bands) passes a seven-non-factor leak test, monotonically improves
over v1 on all three pre-registered PASS thresholds (SB1/SB2/SB3),
and is held in-progress by design pending real-label calibration on
the full 80-song corpus. End-to-end recreation of a band-7 exemplar
delivered +5.906 dB mel-L1 improvement of the effects-layered render
over the bare-MIDI render (M-RECREATE-1 RECREATION_LANDS); the
five-song accurate-small-set (M-RECREATE-2 RC0..RC10) is hardened
with per-stem pre-registration, with RC7 and RC9 landing 5/5 focus
songs and RC10 landing all five sub-milestones under a validated
drums-and-bass resurvey. Generation (M-GEN-1) delivered six batch
revisions; verdicts and provenance are intact and the rendered audio
is deterministically regenerable from the seeded ledger. Final audit:
**731 validated milestones, 22 in-progress, 6 invalidated, 2
reopened, 1 superseded; 0 CRITICAL findings, 1 MAJOR, 21 MODERATE, 10
MINOR; promise-check green.** The remaining constraint on the last
two open threads (real-label M-EAR-1 calibration; RC$n$ closure at
higher confidence) is corpus coverage: 43 of 80 rated songs are on
disk; the pipeline's egress-ready state machine will resume
acquisition automatically when the workspace network policy opens.

## 1. Introduction

### 1.1 The project bet

Long-way-round is a design bet, not a slogan. Music generation
systems that skip *recreation* — that produce plausible-sounding
audio without first proving they can faithfully reconstruct a piece
whose ground truth is known — accumulate opaque failures in the
places where evaluation is hardest: timbre, dynamics, form. This
project's bet is that a pipeline that closes the recreation loop
first, on a small number of rated songs, and instruments every hop
with per-stage evaluation, will produce a generation surface whose
failure modes are named rather than absorbed.

### 1.2 Three fixed decisions

Three decisions were binding from the start of the run and remain so
at report time:

- **Artefact-first evaluation.** Every stage emits a *panel* of
  measurements. No stage emits a scalar quality score. Downstream
  decisions read the panel, not a summary of the panel.
- **Recreation before generation.** M-RECREATE-1 must close on a
  real rated song, and M-RECREATE-2 must harden that closure on a
  small focus set, before any M-GEN-1 batch is trusted for
  operator review.
- **Honest ends.** An in-progress milestone stays in-progress until
  its rubric is met at the confidence its rubric names, even when
  the delay is caused by an external constraint (here, an egress
  policy). "Passing under IMPROVEMENT" is reported as PARTIAL, not
  as PASS.

### 1.3 Pipeline shape

The pipeline flows in one direction: **ingest → classify → separate
→ transcribe → score → rules → DAW → texture panel → ear model**,
with **recreation** exercising the whole flow end-to-end on a rated
song and **generation** exercising it forward from the rules ledger.
Each of the following sections walks one hop, states what was
established, how it was measured, and what still isn't known. The
narrative order is the flow of data, not the chronology of the run.

### 1.4 End-state at a glance

- **Milestone distribution.** 731 validated, 22 in-progress, 6
  invalidated, 2 reopened, 1 superseded.
- **Findings.** 0 CRITICAL, 1 MAJOR, 21 MODERATE, 10 MINOR, 30 INFO,
  4 PASS, 45 NONE.
- **Promise-check.** green.
- **Wall-cap.** not exceeded.
- **Open threads.** M-EAR-1 (real-label calibration on full corpus,
  gated on egress unblock); M-RECREATE-2 accurate-small-set (RC1
  4/5, RC7 and RC9 both 5/5, RC10 validated; parent held in-progress
  by design under the peer-under-G1 convention).

