# Music-Gen

*Status: planning stage. This prompt is framed and waiting; no run has been
launched against it, and this document does not authorize one.*

---

## Intent

You are building a system that learns how songs work by taking them apart,
and then writes new ones by putting the learned parts back together —
deterministically.

The bet behind this project is specific, so understand it before writing any
code. Most machine music generation goes straight from data to audio and
hopes quality emerges. This project refuses that shortcut. It insists on the
long way around: real songs get separated into stems, transcribed into
symbolic form, rebuilt as MIDI, and re-clothed in sound — and only once that
round trip works do we ask the system to compose. Every stage produces an
artifact a human can inspect: a clip with a timestamp, a score, a MIDI file,
a named rule, an effect chain. If the system makes something good, we can say
exactly why. If it makes something bad, we can find the stage that failed.

The full loop you are building:

> Harvest audio → keep only music → split into stems → transcribe each stem →
> merge into a full score → render the score as MIDI → import MIDI into a
> professional DAW → extract and save the rules and patterns that governed
> the transcription → layer on effects to give the MIDI life and color →
> build deterministic effects and heuristics that recreate the *texture* of
> the original song → repeat over many songs, accumulating rules and
> texture heuristics → generate new songs deterministically by selecting
> similar rules and patterns and pushing a fresh score through the same
> MIDI-to-full-audio path.

One warning, placed here so it is never forgotten: the step where bare MIDI
becomes something that sounds like a record — deterministic audio effects and
heuristics that recreate the texture of the original — is the hardest and
most important piece of this entire project. Everything else is either
feeding it or measuring it. Budget your effort accordingly.

## Decisions already made

Do not reopen these. They are constraints, not suggestions.

**Clips are 30 seconds.** When harvested audio is chunked, the chunk length
is 30 s. The reasoning is settled: 30 s is long enough that melodies are not
taken out of context; 10 s is too short. How chunks overlap and how you
handle the tail of a song are yours to decide — the length itself is not.

**Provenance is non-negotiable.** Every clip knows what song it came from
and its start and end timestamps within that song. This chain never breaks:
a stem knows its clip, a transcription knows its stem, a rule knows its
transcriptions, a generated song knows its rules. An artifact whose lineage
cannot be traced back to source audio is a bug.

**Only music flows downstream.** Harvested audio must be classified before
anything else touches it. The classifier distinguishes at minimum: speech
(no music), applause (no music), background/ambient (no music), and music —
with a subtree under music separating live from recorded. Everything that is
not music is filtered out of the working corpus.

**Non-factors are recorded but powerless.** Certain attributes must be
tracked in a sidecar file and must influence nothing: genre, country of
origin, date released, the language the lyrics are written in, instrumental
vs. with lyrics, live vs. recorded, artist name, and the non-music classes
themselves (speech, applause, ambient sounds, and so on). The sidecar exists
for audit and curiosity. No model trains on it, no heuristic reads it, no
curation or generation step branches on it. Treat any leak of a non-factor
into a decision as a defect and prove absence of leaks with tests, not
assertions.

**Survey before you build.** For separation, transcription, and score
tooling: open-source software with high transcription accuracy exists, and
your first job is to find it, benchmark it on this project's own clips, and
adopt what wins. You may develop your own method only where no adequate
open-source solution exists, and "inadequate" is a measurement you publish,
not an opinion.

**The ear's scale is 1–7.** 1 terrible, 2 bad, 3 average, 4 good, 5 great,
6 exceptional, 7 one-of-a-kind. These anchors are fixed.

**The DAW is chosen by its interface, not its reputation.** Ableton Live or
Pro Tools — whichever offers the more robust programmatic interface to the
backend. Decide by evidence, early.

## The system, piece by piece

### 1. Getting audio in

Build the harvester around a user-provided YouTube playlist: given the
playlist, download the audio, chunk it into 30 s clips, and register every
clip in the provenance ledger. Design the harvester as a replaceable front
door — the rest of the system should accept audio from a local folder just
as happily, because acquisition policy must never be the thing that blocks
work on the interesting stages.

Then curate. Run the classifier over every clip, write the non-music
verdicts and all non-factor attributes to the sidecar, and pass only the
music clips onward. When this stage is done you have the project's raw
material: a music-only library of 30 s clips, each with provenance, each
with its sidecar row quarantined off to the side.

### 2. Taking songs apart

Source separation, two capabilities: isolate vocals from instruments, and
isolate individual instruments from each other. This is prime survey
territory — measure the leading open-source separators on your own corpus
before considering anything custom.

### 3. Writing down what you hear

Transcription operates on the separated stems, not the mix.

For instrumental stems, transcription means all six of: rhythm, melody,
timbre, dynamics, harmony, and form. Be honest about coverage — pitch and
rhythm tools are plentiful; timbre, dynamics, and form are where
transcription usually goes silent, and a rule you never wrote down is a rule
the generator can never use.

For vocal stems: transcribe the vocals to text (lyrics extraction), capture
the vocal melody, capture the vocal rhythm, and detect harmony.

Per-stem transcriptions then merge into one full score for the song. From
the score, two bridges:

- **Score generation.** A backend bridge to MuseScore or another composing
  tool, so scores are created and edited programmatically. Support the
  bridge with corpus mining of the tool's documentation and a
  telemetry/live-debugging loop: every bridge failure is captured with
  enough context to diagnose, and fixes flow back into the bridge's
  knowledge base rather than dying in a log file.
- **Score to MIDI.** Convert scores to MIDI, and import that MIDI into the
  DAW (via the interface in piece 5).

### 4. Judging

Two judges, one hand-built and one trained.

The hand-built judge is a battery of **audio heuristics on a mess-scale**:
melody quality, timbre quality, form quality, dynamics quality, and further
axes as they earn their place. Each heuristic is a function with a defined
scale and known blind spots. On top of the clip-level battery sits an
**intra-song meta-heuristic tracker**: because a song is not the average of
its clips, the tracker follows heuristics across a whole song to produce
macro-scale descriptors — how dynamics move, whether the form coheres, where
the song peaks.

The trained judge is the **ear**: a model of the user's taste, trained from
user-provided YouTube playlists rated on the 1–7 scale. The ear scores
audio; it is the fitness function for everything the system eventually
generates. And because the non-factor rule binds here hardest of all: an ear
that secretly learned to detect genre, era, or artist is not an ear, it is a
demographic profiler wearing headphones. Test for this directly.

### 5. The DAW as an instrument

The goal is blunt: control all features of a professional DAW from the
backend. Session and track creation, MIDI import, instrument and effect
selection and parameterization, automation, mixing, rendering — the backend
plays the DAW the way the rest of the system plays MuseScore.

First, run the selection study: Ableton Live vs. Pro Tools, scored on the
robustness of what the backend can actually reach — scripting and remote
protocols, headless operation, reliability under automation. Pick the winner
and commit.

Then build the knowledge layer that makes deep control sustainable: mine the
corpus of DAW-specific documentation into a **layered system — a
deterministic floor under an agentic ceiling**. The floor is an indexed,
exactly-answerable knowledge base built from the mined docs: questions it
can answer, it answers identically every time, with no model in the loop.
The ceiling is an agent that handles what the floor cannot — and every
problem the ceiling solves gets distilled downward, growing the floor.
Telemetry and live debugging run through both layers, so the interface gets
more deterministic the longer it operates.

### 6. Putting songs back together

This is where the project pays off or doesn't.

**Sampling.** Tools for remixing and remastering — including chopping an
original song up and recombining it into something new, the way hip-hop and
rap producers flip a sample. Provenance makes this safe to iterate on: every
slice in a remix is traceable to its source and timestamps.

**Rules extraction.** From each song's full transcription, extract and save
the rules and patterns that govern it — harmonic movement, rhythmic
signatures, melodic contours, structural templates, arrangement habits.
Rules accumulate across songs into a single ledger, each rule carrying
provenance to the transcriptions that support it.

**Texture.** Bare MIDI renders are skeletons. First, layer on audio effects
to give them life and color. Then the hard part: deterministic audio effects
and heuristics that recreate the texture of the *original* song from its
MIDI recreation. Define a measurable texture distance between a render and
the original, and let that number — not your impression on tired ears —
tell you whether the texture layer is working. The gap between the bare
MIDI render and the original is the project's central quantity; the texture
layer's job is to close it, and its progress report is the honest
measurement of how much remains.

**Generation.** Once the loop runs over multiple songs and the ledgers have
depth: generate new songs deterministically. Select compatible, similar
rules and patterns from the ledger, compose a fresh score with them, and
push it through the exact same score → MIDI → DAW → effects → texture path
used for recreations. Generation is not a new pipeline; it is the recreation
pipeline pointed at a score that never existed. The ear and the heuristics
judge the results.

## Order of work

Dependencies, not a schedule:

1. Harvesting, chunking, provenance, and classification come first — nothing
   else has inputs without them.
2. The open-source survey and the DAW selection study run early and in
   parallel; both produce decisions the rest of the build consumes.
3. Separation → transcription → score → MIDI is the spine; get one song
   through it end to end, however roughly, before polishing any stage.
4. Heuristics and the ear can develop in parallel with the spine — they need
   the corpus, not the pipeline.
5. Rules extraction, effect layering, and the texture work start as soon as
   the first recreation exists, and they never really stop.
6. Generation comes last and only earns attention once recreations of
   held-out songs demonstrably work.

## What counts as done

- A music-only clip corpus with unbroken provenance and a sidecar whose
  contents demonstrably influence nothing.
- A survey document with on-corpus benchmarks and an adopt-or-build verdict
  for every separation and transcription stage.
- Full-score transcriptions whose accuracy was measured on this corpus,
  with honest per-axis reporting — including the awkward axes.
- A backend that can take a MIDI file to rendered audio in the chosen DAW
  with zero human clicks, backed by the mined-docs floor-and-ceiling layer.
- A recreation of at least one held-out song where the measured texture
  distance from the original improves stage by stage — bare MIDI, effects
  layered, full texture heuristics — and the remaining gap is stated.
- An ear whose 1–7 predictions on held-out rated playlists beat honest
  baselines and survive non-factor leak tests.
- At least one batch of new songs generated deterministically from the rules
  ledger, each with full provenance and an ear score.

And the failure modes to refuse: a downloader with nothing downstream; a
pipeline whose accuracy was never measured on its own data; a DAW bridge
that needs a human hand; an ear that profiles instead of listens; a
"texture layer" that is a stock mastering preset; a generator bolted on
before recreation worked.

## Conduct

- Harvested audio is private research material for the user. Acquire it
  lawfully and in keeping with platform terms; never commit or redistribute
  audio, clips, or stems — code, schemas, measurements, and reports are the
  publishable surface.
- Remixes and generated songs are experiments, not releases. Generated work
  must derive from the rules ledger and texture heuristics, not from
  recognizable lifted audio.
- Report negative results as results. A stage that doesn't work, measured
  honestly, is worth more than a stage that pretends to.
