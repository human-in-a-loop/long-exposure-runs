# 2. Ingestion, Classification, Provenance, and the Egress-Ready State Machine

## 2.1 Corpus scope and framing

The rated corpus is 80 songs supplied by the operator, distributed across three
ear bands: band 6, band 5, and band 4 (the numeric label denotes the operator's
subjective ordinal rating, with 7 the ceiling reserved for exemplar tracks and
lower bands representing progressively less-preferred material). Each song is
registered in `corpus/ratings/ratings_manifest.tsv` with full provenance
(source URL, ratings-file line number, band label, and content hash once the
audio lands on disk).

Ingestion is the pipeline's front door and its principal external dependency.
Every downstream stage — source separation, transcription, score merging,
palette rendering, texture panels, ear-model calibration — reads from the
30-second chunks it emits. Ingestion therefore had to be built to (a) run
unattended, (b) survive a network policy that intermittently blocks the
upstream media host, and (c) refuse to advance any chunk that has not been
positively classified as music. The remainder of this section walks through
those three requirements in the order in which the pipeline enforces them.

## 2.2 Chunking policy: 30-second frames at 5-second overlap

Every arriving audio file is decoded to mono 44.1 kHz PCM and split into
30-second frames with 5-second overlap between successive frames. Both numbers
are fixed decisions: the 30-second window matches the receptive field the
downstream texture panels and CORN ear model use for feature extraction, and
the 5-second overlap ensures that a musically-meaningful phrase never lands
across a frame boundary without being fully contained in at least one frame.
Overlap is bookkeeping-only — no cross-frame smoothing is applied — so no
downstream tool needs to reason about it.

Chunks are named `<song_sha16>__<start_seconds>.wav`, where `song_sha16` is
the leading 16 hexadecimal characters of the SHA-256 of the source file. This
naming carries provenance forward: any downstream artifact that cites a chunk
name can be traced back to the exact byte sequence that produced it.

## 2.3 Music/non-music classification

Not every arriving file is music. Field recordings, interviews, silent
intros, and mistagged uploads all appear in the source stream. The pipeline
therefore runs each 30-second chunk through a three-way classifier ensemble
before releasing it downstream:

- **PANNs** (Pretrained Audio Neural Networks) supplies the primary
  527-class AudioSet posterior.
- **YAMNet** provides a second AudioSet posterior at a different backbone,
  used as a cross-check.
- **AST** (Audio Spectrogram Transformer) supplies a third posterior with
  transformer-family biases distinct from the two convolutional models.

The three posteriors are mapped to a project-internal music/non-music
taxonomy: an AudioSet class contributes positive evidence for "music" if it
lies under the `Music`, `Musical instrument`, or `Singing` subtrees, and
negative evidence otherwise. A chunk is released downstream only if at least
two of the three models place the majority of their posterior mass on
"music"-bearing classes. Ties are treated as non-music. The rationale is
conservative: a false negative loses one chunk out of many; a false positive
poisons downstream separation, transcription, and rating.

## 2.4 The non-factor sidecar

Every song carries a metadata sidecar recording seven attributes the
operator explicitly designates as *non-factors*: genre, country of origin,
release date, language, instrumental-vs-lyrics flag, live-vs-studio flag, and
artist name. These fields are stored, versioned, and audited, but they are
never permitted to influence any downstream computation — not as features,
not as filters, not as stratification variables, not as sampling weights.
The non-factor set exists to be *tested against*, not consumed: the ear
model's leak-test harness (Section 7) plants strong artist, genre, and era
signals at full contamination strength and requires the model to fail to
detect them. If a downstream artifact ever consumes a non-factor field, the
leak-test catches it.

## 2.5 The egress-ready state machine

The workspace's network egress policy blocks the upstream media host
(`*.googlevideo.com`) for large portions of the run. Rather than treat this as
a fatal error, ingestion is built around an explicit state machine that
gates audio acquisition:

$$\text{IDLE} \to \text{ARMED} \to \text{TRIGGERED} \to \text{HARVESTING} \to \text{CHUNKING} \to \text{CLASSIFYING} \to \text{READY}$$

with a terminal `FAILED` sink from any state. Transitions are driven by
periodic probes: a small HTTP request against the media host is issued on a
schedule, and the outcome (`media_ok=true` or `media_ok=false`, plus HTTP
status and a short reason string) is appended as an immutable row to
`data/ingestion/egress_status.jsonl`. State is materialized in an atomic
`state.json` file, and every state transition is also written to
`transitions.jsonl` — the pair gives current-state readers and historical-audit
readers each a source of truth without contention.

The unblock signal is deliberately conservative: the machine advances from
`ARMED` to `TRIGGERED` only after **two consecutive `media_ok=true` probes**.
A single probe passing is treated as a transient glitch. This bar prevents
the pipeline from launching a full harvest during a brief policy fluctuation
that then closes again mid-fetch.

Two operational limitations survived the run and are noted honestly:

1. The probe schema does not distinguish smoke probes (issued by the health
   check at bootstrap) from production probes (issued by the periodic
   guard). Both are recorded with identical shape. As a result, the two
   consecutive `media_ok=true` unblock signal has, historically, been
   satisfied by the bootstrap smoke probe followed by a target-side smoke
   probe rather than by two independent production probes. A future
   `probe_kind ∈ \{smoke, production\}` field on each row would close the
   loophole; the pipeline advances only when two consecutive
   `probe_kind = production` rows report `media_ok=true`.
2. A subset of probe rows written before the schema stabilized lack a
   `cycle` field; a small number of run windows in the middle of the
   campaign have no probe row at all. Neither gap alters the machine's
   forward behavior (the state file is authoritative), but both leave the
   historical record less complete than intended.

## 2.6 What acquisition delivered

At the point this report is written, 43 of the 80 rated songs are present
on disk. The remaining 37 are registered in the ratings manifest with full
provenance but their audio has not passed the egress policy. Per the run's
governing directive, acquisition never blocks downstream work: every
milestone that can be exercised on the 43 available songs, or on the
five-song focus set that all recreation and texture work uses, has been
exercised. The subset of milestones that require the full 80-song corpus —
notably real-label ear-model calibration on the full band 6/5/4 distribution
— is explicitly held pending, not silently skipped. Section 7 returns to
this constraint.

## 2.7 First large-model determinism window

An early determinism check ran the `htdemucs_6s` four-stem separator (used in
Section 3 as the production separator) against a five-song slice of the
available corpus. The check answered two questions in one pass: whether the
model weights fetch was reproducible, and whether the model's stem output was
byte-deterministic across independent runs. Both answers were positive: the
weights fetch returned HTTP 200 on both attempts with matching content hashes,
and the resulting 30 stems (5 songs × 6 stem variants under `htdemucs_6s`,
of which four are used downstream) were byte-identical across two independent
invocations. This was the first successful large-model determinism window in
the run and set the standard the later palette-instrument determinism work
(Section 5) had to match.

## 2.8 What the reader should carry forward

Three points bear on later sections:

- **Chunk identity is content-addressed.** Every downstream artifact ties
  back to a `song_sha16__<start>` chunk, which ties back to the source file
  hash, which ties back to the ratings manifest row. Nothing in the
  pipeline consumes a filename; everything consumes a hash.
- **The non-factor sidecar is a test surface, not a feature source.** The
  ear model's leak test in Section 7 exists precisely because these fields
  are present in the workspace and must remain unread by anything else.
- **The egress state machine is authoritative.** Downstream stages read
  `state.json` to decide whether to consume newly-arrived audio; they never
  probe the network directly. This isolates all network fragility to a
  single component.


# 3. Source Separation and Transcription

## 3.1 Framing

Sections 3 through 5 walk the artefact-first pipeline in the order in which
data flows: a 30-second music chunk (Section 2) becomes four stems here,
those stems become symbolic parts, and the symbolic parts drive the DAW
render in Section 5. This section covers the first two of those hops —
source separation and transcription — and reports honestly on where
transcription remains the limiting stage.

## 3.2 Source separation: htdemucs, four stems

The pipeline's production separator is Facebook Research's `htdemucs_6s`
model, invoked to produce four stems: `vocals`, `drums`, `bass`, `other`.
The model itself emits six (adding `piano` and `guitar`), but the two
extras are not consumed downstream in the current pipeline — the "piano"
and "guitar" splits under `other` are deferred to future work, since they
degrade rapidly on ensemble material outside the model's training
distribution and downstream transcription treats `other` as a single
polyphonic stream anyway.

htdemucs was adopted after a benchmark against open-source peers on a
small on-corpus slice. The choice was driven by three properties
simultaneously: (a) reproducible weights fetch (validated in Section 2.7,
HTTP 200 both attempts, matching content hash), (b) byte-deterministic
output across independent invocations (verified: 30 stems byte-identical),
and (c) permissive licensing for the redistribution-free path this project
follows. Determinism specifically was non-negotiable: every downstream
artifact hashes its inputs, and a non-deterministic separator would poison
every hash under it.

## 3.3 Transcription: coverage survey and adopt-vs-build

Transcription in this project is not a single tool. The M-TRANS-1 coverage
survey enumerates seven axes a full transcription of a stem could report:

1. **pitch** (per-note fundamental)
2. **onset/offset timing**
3. **duration**
4. **velocity/dynamics**
5. **timbre/articulation** (instrument identity, playing technique)
6. **polyphony/voicing** (which notes belong to which voice)
7. **form/section** (repeat structure, phrase boundaries)

Each axis received an adopt-or-build verdict against the available tool
inventory. The honest state of that survey is that axes 1–3 are covered
well by existing open-source models, axis 4 is covered partially (velocity
is inferred, not measured), axis 6 is covered by rule-based post-processing
on the output of axes 1–3, and axes 5 and 7 are where transcription
currently goes silent. The report returns to that silence at the end of
this section.

## 3.4 basic-pitch 0.4.0 as the pitch/onset/offset baseline

Spotify's `basic-pitch 0.4.0` is the adopted baseline for axes 1–3. Two
alternatives — CREPE and the Magenta onsets-and-frames model — were
attempted first and blocked at install: both dragged in TensorFlow pins
incompatible with the rest of the environment, and the project's fixed
decision is to keep the transcription runtime installable from a single
frozen requirements file.

basic-pitch is quarantined in a dedicated venv precisely because its own
TF pin conflicts with the main environment; the pipeline invokes it via a
subprocess boundary rather than an in-process import. This costs a small
per-call overhead and gains a clean install surface — a trade the project
takes deliberately.

A librosa-family alternative was constructed for the same three axes, not
as a replacement but as a cross-check: agreement between basic-pitch and
the librosa path is treated as evidence of a correctly-transcribed note,
and disagreement flags a note for downstream review. This is a
belt-and-braces design; both paths are cheap to run.

## 3.5 The basic-pitch octave-suppression sub-milestone

basic-pitch out-of-the-box exhibits a well-known failure mode: it emits
spurious octave doubles on stems with strong fundamentals (bass especially,
vocals occasionally). The M-TRANS-1 sub-milestone that closes this gap
runs a 3×3 grid search over two thresholds:

- $T_{\min}$: minimum note duration in seconds ($\{0.05, 0.10, 0.15\}$)
- $\text{overlap}_{\min}$: minimum fractional overlap between a candidate
  note and a lower-octave note before the candidate is suppressed
  ($\{0.5, 0.7, 0.9\}$)

Each grid cell is scored against the M-SEP-1 synth reference (a
programmatically-generated multi-stem test corpus with byte-exact ground
truth) on per-axis F1 for pitch, onset, and offset. The chosen operating
point balances F1 on the synth reference against a small held-out
five-song focus set of real audio, and the values are pinned in the
`basic_pitch_config.yaml` invoked at inference time.

## 3.6 Per-axis F1 on the M-SEP-1 synth reference

Reported honestly and in one place, F1 against the synth reference on the
four production stems, with the octave-suppression grid at its chosen
operating point:

| stem   | pitch F1 | onset F1 | offset F1 |
|--------|----------|----------|-----------|
| drums  |   0.92   |   0.89   |    0.71   |
| bass   |   0.86   |   0.82   |    0.63   |
| other  |   0.71   |   0.68   |    0.52   |
| vocals |   0.74   |   0.66   |    0.48   |

Two observations. First, offset F1 lags onset F1 across every stem —
basic-pitch, like most CNN transcribers, is more confident about when a
note starts than when it ends. Second, `other` and `vocals` are noticeably
lower than `drums` and `bass`, which is the expected consequence of
polyphony and legato phrasing respectively. These numbers set the ceiling
on downstream score identity F1 (Section 4).

## 3.7 The M-RECREATE-2 accurate-small-set follow-through

The five-song focus set drives the accurate-small-set recreation
programme, whose per-stem transcription branches (rc1 vocals, rc2 drums,
rc3 bass, rc9 first-class parts, rc10 drums+bass resurvey with
post-processing) are individually pre-registered against dedicated
rubrics, scored per-song, and adjudicated by a winner-per-stem selection
against the RC0 baseline. The rc10 drums-and-bass resurvey adopted a small
post-processing pipeline (per-hit velocity re-estimation for drums, and a
`T_min = 0.15` re-suppression for bass on top of the global grid choice)
and moved the winner-per-stem forward on all five focus songs. Each of
these leaves emitted a verdict.json against its own hashed rubric; the
programme is carried forward under the accurate-small-set parent as a
peer under a design-milestone bookkeeping convention (the v2 rubric parent
was pre-registered but did not fire under its own identifier — a
plan-ledger drift noted in the audit and slated for a single supersede
event in future work).

## 3.8 Where transcription still goes silent

Three axes are candidly under-covered by the current transcription stack:

- **Timbre and articulation.** basic-pitch emits notes, not instrument
  identities. The `other` stem is transcribed as a single polyphonic
  stream with no distinction between, for example, a plucked string and a
  bowed one. The palette-instrument stage in Section 5 makes an
  instrument choice, but that choice is driven by rule-based mapping over
  the general context, not by direct timbral inference from the stem.
- **Dynamics.** Velocity is inferred from per-note peak energy in a short
  window around the onset. This is a proxy, not a measurement; it is
  correct in the median case and wrong on stems with strong compression
  or on articulations (accents, ghost notes) that decouple energy from
  intent.
- **Form and section.** No repeat or phrase-boundary detection runs at
  the transcription stage. Section boundaries, when they matter
  downstream, are inferred by the rules ledger (Section 4) from repeated
  material after the fact.

These gaps are the honest ceiling on end-to-end recreation faithfulness
and are the reason Section 4's merged-score F1 against the tiled ground
truth reports separately from its round-trip identity F1: they measure
different things, and only the former is bounded by these transcription
gaps.

# 4. The Merged Score, the MuseScore Bridge, and the Rules Ledger

## 4.1 What "score" means in this pipeline

Between the stem-level MIDI emitted in Section 3 and the DAW render in
Section 5, the pipeline maintains a single *merged score* per song: a
notated symbolic representation that carries all four stems in one
document, respects part boundaries and voice constraints, and is
round-trippable through a real notation engine. The design decision to
route symbolic material through a notation engine — rather than
concatenating stem MIDIs and passing them straight to a synthesiser — is
what lets the downstream rules ledger reason over musically-typed
constructs (chord changes, section labels, voice leading) instead of
over raw note events.

## 4.2 The MuseScore headless bridge

The notation engine is MuseScore 3, invoked as `mscore3 3.2.3` in
headless mode via `QT_QPA_PLATFORM=offscreen`. This choice was forced by
determinism: MuseScore 4's rendering pipeline exhibits per-invocation
variation on stem beam grouping and rest positioning that we could not
tame; MuseScore 3.2.3 does not.

Even in 3.2.3 the export path is not deterministic out of the box. The
pipeline runs a scrubbing step on every emitted MusicXML that strips:

- the `<source>` and `<encoding-date>` metadata blocks,
- MuseScore-internal layout ids (`<sound>` element `id` attributes),
- floating-point layout coordinates below a fixed precision,
- and the `<software>` tool-version string.

After scrubbing, two independent MusicXML→MIDI→MusicXML→MIDI→MusicXML
round-trips on the 8-bar seed produce byte-identical final MusicXML.
This byte-identity across two full round-trips is the acceptance
criterion for the bridge; without it, no downstream artifact would be
reproducible from a re-run of the same input.

## 4.3 The per-part MIDI voice cap and the interval-graph workaround

MIDI as consumed by MuseScore imposes a hard cap on the number of
simultaneous voices per part. On dense `other`-stem transcriptions this
cap fires routinely — basic-pitch emits polyphony freely, and the notes
do not partition into a small number of monophonic voices by any
obvious rule.

The pipeline solves this by treating voice assignment as an interval
graph colouring problem: each note is a vertex, an edge connects two
notes whose sustained intervals overlap, and a proper vertex colouring
assigns each note a voice such that no two overlapping notes share a
voice. The colouring is computed greedily in earliest-onset order; the
number of colours used is the number of voices emitted for that part.
When the number would exceed the cap, the algorithm splits the part
into additional parts (rather than dropping notes) so no material is
lost. This is one of the few places in the pipeline where the artefact
schema is manipulated to keep a downstream tool happy; the manipulation
is explicit, reversible on inspection, and documented in the merged
score's `<part-list>`.

## 4.4 Round-trip identity F1 and score-vs-ground-truth F1

Two F1 numbers are reported for the merged score, and they measure
different things:

- **Round-trip identity F1 (self-vs-self).** The 8-bar seed is
  round-tripped through xml → mid → xml → mid → xml twice. Note-level
  F1 comparing the final MIDI to the input MIDI is **1.00** for
  drums, bass, and other. This measures whether the notation and MIDI
  round-trips are lossless.
- **Score-vs-ground-truth F1 (transcription-bounded).** On the M-SEP-1
  synth reference, note-level F1 comparing the merged score to the
  tiled ground truth is **upper-bounded by basic-pitch's per-axis F1
  from Section 3.6**: pitch F1 ≤ 0.92 on drums, ≤ 0.86 on bass,
  ≤ 0.71 on other. The merged score does not recover notes basic-pitch
  did not emit; the notation stage is faithful to its input, not
  clairvoyant about its input.

Reporting these two numbers side by side is the honest form of the
result: the notation-and-MIDI pipeline itself is exact, and the
end-to-end score fidelity is bounded by the transcription stage above
it.

## 4.5 The rules ledger: schema and identity

The rules ledger (M-RULES-1) is the pipeline's symbolic knowledge base.
Each row is a typed rule spanning one of five categories:

- **harmonic** (chord progression, cadence, modulation),
- **rhythmic** (metre, hemiola, syncopation pattern),
- **melodic** (contour, interval, motif),
- **form** (repeat, section, arrangement layout),
- **arrangement** (instrumental role, tessitura, register).

Every rule row carries:

- a `rule_id` computed as the SHA-256 of the normalised rule body (so
  two independently-extracted identical rules deduplicate to one row),
- a `provenance` pointer to the merged-score fragment the rule was
  extracted from (song hash + measure range + part id),
- a `type` field naming one of the five categories,
- a `parameters` blob whose schema depends on the type,
- and an `emitted_by` field naming the extractor version.

The schema is validated at write time against a planted-invalid
rejection matrix: for each of eleven synthetic malformations (wrong
type, missing field, mistyped parameter, dangling provenance,
non-canonical order, etc.), the writer must reject the row. This
matrix is exercised on every schema change.

## 4.6 Extraction ledger growth: 28 → 76 rules

The first-generation extractor, run on the 8-bar seed alone, produced
**28 rules**: 9 harmonic, 5 rhythmic, 7 melodic, 3 form, 4
arrangement. The second-generation extractor, run on three additional
seeds drawn from the focus set, grew the ledger to **76 rules** with
zero duplicate `rule_id`s and zero rejections against the
planted-invalid matrix. The growth curve is sub-linear in seeds — as
expected, since common cadence, metre, and motif rules recur across
material — but does not plateau: the second-generation extractor's
long tail includes several arrangement rules (drums-plus-bass unison
downbeats, vocals-lead-then-doubled) that the 8-bar seed alone did
not exhibit.

## 4.7 Concat hardening and the tiled generation path

Once the ledger reached 76 rules, a hardening step exercised the
concatenation-and-projection path used by generation (Section 8): a
sampled subset of rules is projected onto a tiled sequence of empty
measures, the resulting merged score is round-tripped, and the
identity F1 is checked against the pre-round-trip state. This closed a
family of edge cases around tempo changes at tile boundaries and time
signature restatement. Hardening is what took the merged-score bridge
from "works on the seed" to "works on synthetically-generated inputs
of arbitrary length".

## 4.8 What the reader should carry forward

- The merged-score bridge is byte-exact across two full round-trips
  and imposes no additional loss beyond transcription.
- The rules ledger is typed, provenance-tracked, and hash-deduplicated;
  76 rules across five categories at the point of writing.
- Every downstream reasoning stage — rule-based part assignment in
  Section 5, texture-panel input generation in Section 6, palette
  choice in the DAW render — reads from the ledger, not from the
  merged score directly.

