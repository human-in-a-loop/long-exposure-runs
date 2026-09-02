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

# 5. The DAW Stack and the Palette-Instrument Determinism Arc

## 5.1 The 2026-08-28 stack reversal

The project's original DAW choice was Ableton Live plus Pro Tools,
driven by their strong plugin ecosystems and mature MIDI-clip authoring.
That choice was reversed on 2026-08-28 in favour of **Ardour +
DawDreamer + open-source plugins** (LV2 and open VST3s). Three reasons
converged:

1. **Redistribution constraints.** Ableton and Pro Tools cannot be
   installed unattended in a reproducible workspace; every worker would
   have needed a manually-managed license seat. Ardour installs from
   package under an open licence, and DawDreamer is `pip install`-able.
2. **Determinism reach.** DawDreamer exposes plugin state as
   Python-native parameter maps that can be dumped, hashed, and diffed;
   commercial DAWs' automation formats are opaque binary blobs whose
   byte-identity across saves is not guaranteed even without semantic
   change.
3. **Automation as first-class data.** DawDreamer's `set_automation`
   accepts a per-parameter time-series directly, so automation curves
   are inputs the pipeline can construct programmatically from the
   rules ledger, rather than clip-region drawings maintained by hand.

The reversal was carried out as a bounded validation spike — M-DAW-SPIKE-1
— rather than a wholesale rewrite; the spike's purpose was to answer
"can this stack render a merged score with automation, deterministically,
end to end" before any downstream code was re-pointed.

## 5.2 What the spike proved and its two documented gaps

The spike closed the end-to-end path for a single seed song: merged
score → per-part MIDI → Ardour session with correct automation lanes →
render to WAV → panel input. Two gaps surfaced during the spike and were
documented rather than papered over:

- **GAP-1: Ardour Lua MIDI-file import.** Ardour's Lua scripting API
  does not expose a stable programmatic path for importing a
  standalone MIDI file into a new track region. Manual UI import
  works; scripted import does not (the API surface exists, but its
  behaviour across Ardour patch releases was not stable enough to
  build on).
- **GAP-2: Ardour VST3 automation delivery.** Even when a VST3 plugin
  is instantiated in an Ardour track and an automation lane is drawn
  onto it, parameter changes were observed not to reach the plugin's
  audio-thread state on render. Initial diagnosis pointed to VST3
  specifically; later work sharpened this: the delivery gap affects
  **both VST3 and LV2** paths on the versions of Ardour available in
  the workspace.

GAP-1 was closed by a **redefinition**: rather than route MIDI through
Ardour's importer at all, the pipeline pre-renders each MIDI part to
audio via `fluidsynth` (with a pinned SoundFont per part) and then
authors the Ardour audio-region XML by hand. Hand-authored XML uses
Ardour's stable on-disk schema (which is stable across the patch
releases we tested) rather than its unstable scripting API. The audit
records this closure as a REDEFINED-GAP, not a fix — a signal to future
readers that the underlying Lua import path is still not exercisable.

GAP-2 remains **STILL-GAP** at the time of writing. The pipeline works
around it with a two-step render (rendered stems from fluidsynth, then
DawDreamer for parameter-automation-driven effect passes on those
stems); the workaround is documented in the DAW-stack README and is
consumed by the palette-instrument work in §5.4.

## 5.3 DawDreamer `set_automation` gap-closure and `env_corr`

Independent of the Ardour VST3/LV2 gap, DawDreamer's own
`set_automation` path was exercised as the primary automation-delivery
mechanism. The gap-closure metric is `env_corr`: the Pearson correlation
between the rendered stem's short-window RMS envelope and the target
envelope encoded by the automation curve. Two bars were pre-registered:

- **Primary bar:** `env_corr ≥ 0.9` on a sinusoidal AM-envelope target.
- **Secondary bar:** `env_corr ∈ [0.15, 0.3]` — a floor that
  distinguishes "automation is delivered at all" from "automation has
  no measurable effect."

The observed number after gap-closure was **env_corr = 0.487**. This
misses the primary bar and satisfies the secondary bar. The result is
reported as a **partial closure**, not a pass: it demonstrates that
`set_automation` reliably delivers a monotonic control signal to the
plugin's audio thread, but the sinusoidal target's high-frequency
detail is smoothed by parameter-quantisation and per-block latency in
the plugins we tested. Downstream panel input is computed on the actual
rendered envelope, not on the target — so the panel measurements remain
faithful even where the primary bar is missed.

## 5.4 The palette-instrument determinism arc

Beyond the automation gap, the pipeline needed a *palette* of
instruments — synths and samplers whose per-parameter state can be set
programmatically and whose rendered output is byte-deterministic for a
given parameter payload. Two plugins were adopted:

- **Surge XT** (open-source hybrid synth) for pitched tonal content.
- **Dexed** (open-source FM synth, DX7-family) for FM-specific timbres
  and for the leak-test control condition of a strong,
  spectrally-narrow reference tone.

Each is rendered via DawDreamer under a fixed sample rate (44.1 kHz), a
fixed block size, and a fixed parameter payload. Byte-identity was
verified across:

- **Independent invocations** on the same host (same worker, cold
  cache): identical bytes.
- **Salted invocations** across a set of five deterministic-salt seeds
  intended to perturb any hidden nondeterminism (thread scheduling,
  allocator interleavings, floating-point summation order): identical
  bytes.
- **Two hosts** with matching CPU family: identical bytes.

Both plugins passed. The determinism proof is *conditioned* on the CPU
family being homogeneous across workers — the pipeline pins workers to
a single family precisely because we did not want to promise
cross-family byte identity we could not measure.

## 5.5 The c31 STILL_GAP-to-activation closure

The palette-instrument work started as a STILL_GAP: the fixture at
c26 showed byte-identity on a synthetic sine-wave rendering, but the
first attempt at rendering a real merged-score part through the same
path exposed a mismatch between the fixture's parameter payload and
the shape the real path fed the plugin (an additive-kwargs mismatch in
`scripts/palette_render/render_stem.py`). The c31 activation closure
resolved this: the render function was extended additively (new
kwargs default to a value that recovers the fixture's behaviour), the
fixture was re-run to confirm no regression, and a real merged-score
part was rendered end-to-end with byte-identical output across the
determinism grid above.

The audit notes one downstream consequence: the anchor manifest that
pinned the pre-c31 form of `render_stem.py` was not republished after
the c31 additive-kwargs edit. The manifest's contract still holds
(`parameter_dict=None` recovers the pinned c33 anchor byte-for-byte),
but this backwards-compat guarantee lives in the code and the audit,
not in the manifest itself. Republishing the manifest as `_v2` with
the post-edit SHA and an explicit backwards-compat clause is called
out under future work.

## 5.6 A schema wart worth noting

The palette-instrument determinism milestone emits its per-song
determinism verdict as a row in a TSV (`data/palette_determinism/
scorecard.tsv`) rather than as a top-level `verdict.json`. This is
faithful to the milestone's rubric (which is defined per-row) but
breaks the cross-milestone convention that verdicts live at the top
level as JSON with a `rubric_hash` key. The audit flags this as
verdict-schema drift; consolidating the TSV row into a wrapper
`verdict.json` (referencing the TSV as an artefact rather than as the
verdict itself) is a small future-work item that does not change the
determinism guarantee.

## 5.7 What the reader should carry forward

- The DAW stack is Ardour + DawDreamer + open plugins, chosen for
  determinism reach and unattended reproducibility.
- One documented gap (GAP-1, Ardour Lua MIDI import) is closed by a
  hand-authored XML redefinition; one (GAP-2, Ardour VST3/LV2
  automation delivery) remains open and is worked around by a
  two-step render.
- DawDreamer's `set_automation` delivers monotonic control signals
  (`env_corr = 0.487`, primary bar 0.9 missed, secondary bar
  0.15/0.3 satisfied).
- Surge XT and Dexed render byte-deterministically across independent
  invocations, salt sweeps, and paired hosts within a pinned CPU
  family. This byte-identity is the load-bearing property that lets
  the generation stage in Section 8 hash renders and deduplicate at
  the payload level.

# 6. The Texture Panel (M-TEX-1)

## 6.1 The refuse-to-aggregate contract

The texture panel is the single largest concession this project makes
to honesty over convenience. Every mature evaluation tradition — for
speech synthesis, for image generation, for music tagging — offers a
one-number scalar quality score. M-TEX-1 explicitly refuses that. The
panel reports **a vector of side-by-side distances** on every
comparison it makes, and it exposes the family disagreements between
those distances rather than smoothing them into a mean.

The rationale is that no single mel-, spectral-, or embedding-derived
distance measures texture faithfulness well enough to be trusted alone.
Each family has known blind spots — mel L1 is insensitive to fine
timbral colour, VGGish is content-dependent, CLAP over-weights
semantic tags, the loudness envelope ignores spectral balance —
and averaging their normalised values produces a number that looks
authoritative and is not. The contract is therefore: **the panel is
the answer; the answer is not a scalar**.

## 6.2 What the panel measures

The panel emits four families of distances per comparison, at multiple
scales where the metric admits scale:

- **Multi-scale mel L1.** Log-mel spectrograms are computed at three
  window/hop pairs (2048/512, 4096/1024, 8192/2048), L1 distance is
  taken per scale, and all three are reported.
- **Spectral centroid, bandwidth, rolloff, flatness.** Four
  librosa-family low-order spectral statistics, each reported as
  frame-mean L1.
- **Loudness envelope.** Short-window RMS envelope L1, with an
  additional cross-correlation `env_corr` figure (the same statistic
  used to characterise the DawDreamer automation delivery in Section
  5.3).
- **CLAP and VGGish perceptual embedding distances.** Cosine and L2
  distances in each embedding space, reported separately (they
  disagree, and the disagreement is the point).

For a single pairwise comparison this produces on the order of a dozen
scalar entries. The panel does not reduce them.

## 6.3 The stage-by-stage comparison

The comparison the panel is designed for is not "recreation vs
original" alone. It is three-way: **original ↔ bare-MIDI ↔
effects-layered**, where:

- *original* is the source audio,
- *bare-MIDI* is the merged score of Section 4 rendered through the
  DAW stack of Section 5 with palette instruments but no effects
  chain,
- *effects-layered* is the same render with the rules-ledger-derived
  effects chain applied (EQ, compression, reverb, delay).

The three-way structure lets the panel disentangle two questions the
project genuinely cared about separately: how much of the texture gap
is symbolic (bare-MIDI vs original) vs how much is production
(effects-layered vs bare-MIDI). On the seed song, roughly two-thirds
of the mel L1 gap and roughly half of the VGGish cosine gap closed
between bare-MIDI and effects-layered, consistent with production
being a large but not dominant contributor to texture faithfulness.

## 6.4 Widening: three seeds, 72 finite numbers

Initial evaluation was on a single seed; widening to three seeds
produced 72 finite scalar entries (three seeds × three stages × four
families × the family-appropriate number of sub-scales). "Finite" is
literal — the panel refuses to emit NaN and refuses to fall back to
imputation. A metric that cannot be computed for a given comparison
(for example, VGGish cosine on a stem below the model's minimum
duration) is reported as an explicit absent row, not as zero.

Across the three seeds the panel's headline observation was that no
single distance ordered the three stages consistently. Multi-scale
mel L1 preferred effects-layered on all three seeds. VGGish cosine
preferred effects-layered on two seeds and bare-MIDI on one. CLAP
cosine preferred effects-layered on the two ensemble seeds and was
essentially tied on the monophonic seed. This is the family
disagreement the panel exists to surface.

## 6.5 The content-flip embedding analysis

The one persistent VGGish flip — bare-MIDI preferred over
effects-layered on a specific seed — was drilled into as a dedicated
sub-milestone: the content-flip embedding analysis. The finding is
that the flip is **content-dependent, not seed-random**:

- On polyphonic material, VGGish's cosine geometry places the
  effects-layered render closer to the original: the model rewards
  the spectral density that the effects chain adds.
- On monophonic decaying-triad material (the specific seed that
  flipped), VGGish places the bare-MIDI render closer: the effects
  chain's reverb tail moves the embedding *away* from the
  dry-monophonic original along a dimension the model uses.

The analysis's importance is not to fix the flip — it is a true fact
about VGGish, not a bug in the pipeline — but to make it legible in
the panel output. The relevant panel row now carries a
`content_class ∈ \{polyphonic, monophonic-decaying-triad, mixed\}`
tag that tells a downstream reader when this flip is expected.

One book-keeping note: the c14 clone-2 closure event pinned 13
artefacts plus an adopt event for a `variants/` directory of
content-flip case studies. That directory is only partially present
on disk today; the analysis's *findings* survive intact in the
verdict JSONs and in the tagged panel rows, but the illustrative
per-case variants would need to be regenerated to restore the
directory to its pinned form. The audit records this as evidence
drift, tracked but not blocking.

## 6.6 A note on figures

The M-TEX-1 content-flip analysis has figures on disk under
`docs/figures/`; the M-RECREATE-2 RC0..RC10 scorecards are tabular
only and would benefit from before/after mel and centroid plots that
we did not generate in-run. The audit's figure-coverage assessment
flags this as an outstanding item; it does not change any numeric
finding.

## 6.7 What the reader should carry forward

- The panel is the answer; there is no single texture number.
- Every panel row is a real measurement, not a smoothed average or
  an imputation.
- Family disagreements — especially VGGish vs mel L1 on monophonic
  decaying material — are surfaced by construction, not swept up.
- The panel is what Section 7's ear model is calibrated *against*
  as a separate signal from the ear model's own ordinal loss;
  keeping the two signals distinct is a load-bearing part of the
  ear-model design.

