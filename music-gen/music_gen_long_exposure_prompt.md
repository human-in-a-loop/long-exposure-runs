# Long-Exposure Research Prompt: Music-Gen

> **STATUS: PLANNING / PROMPT-FRAMING STAGE ONLY.** This prompt documents the
> intended campaign. No run has been launched against it, and nothing in this
> document authorizes launching one. Launch requires an explicit human go-ahead
> plus a `long-exposure.config.yaml` scoped to this directory.

## Campaign Title

**Music-Gen: A Transcription-First, Rules-Extracting Pipeline from Harvested Audio to Deterministic New-Song Generation, with a Trainable Ear and Full DAW Control**

## Mission

Build a full audio-manipulation stack that can take real songs from a
user-provided YouTube playlist and carry them end-to-end through:

```text
harvest → classify → separate → transcribe → score → MIDI → DAW import
        → extract rules/patterns → layer effects → deterministic texture
        heuristics → repeat over many songs → generate NEW songs
        deterministically from the extracted rules
```

The campaign is **transcription-first and rules-first**: the generative step is
not a neural sampler producing audio directly, but a deterministic composer
that selects and recombines rules and patterns extracted from real songs,
renders them as scores/MIDI, and then re-textures the MIDI into full audio
using deterministic effect and heuristic layers learned from the originals.

The single hardest and most important piece of the entire campaign — stated up
front so no track loses sight of it — is the **MIDI-to-texture problem**:
building deterministic audio effects and audio heuristics that recreate the
texture, life, and color of an original song starting from a bare MIDI
recreation of its transcription. Every other capability exists to feed,
measure, or exploit that piece.

Alongside the pipeline, the campaign builds a **trainable "ear"** — a music
quality judge trained from user-rated playlists on a 1–7 scale — and a
**professional-DAW control layer** (Ableton Live or Pro Tools, chosen by
interface robustness) so that every DAW feature is drivable from the backend.

## Fixed Design Decisions (do not relitigate)

These are inputs to the campaign, not open questions:

1. **Clip length is 30 seconds.** Harvested audio is split into 30 s chunks.
   30 s is long enough that melodies are not taken out of musical context;
   10 s is too short. Do not shorten it. (Overlap/hop strategy between
   consecutive 30 s chunks is an open engineering choice; the chunk length is
   not.)
2. **Every clip carries provenance.** Each clip records what song it came
   from and its start/end timestamps within that song. No clip enters any
   downstream stage without a resolvable provenance record.
3. **Input curation filters to music only.** The classifier must distinguish
   at least: speech (no music), applause (no music), background/ambient
   (no music), and music — with a subtree under music that differentiates
   live vs. recorded. Only clips classified as music proceed downstream.
4. **Non-factors are tracked as a sidecar and must not influence anything.**
   Non-factors include: genre, country of origin, date released, language the
   lyrics are written in, instrumental vs. with-lyrics, live vs. recorded,
   artist name, and the non-music classes themselves (speech, applause,
   ambient sounds, etc.). They are recorded per clip in a sidecar file for
   audit and analysis, but no model, heuristic, ranking, curation step, or
   generative decision may condition on them. This is the **non-factor
   firewall**, and it is testable (see Track 5 ablations).
5. **Survey open source before building.** For separation, transcription,
   score generation, and MIDI tooling: first survey existing open-source
   software with high accuracy. Only if no adequate open-source solution
   exists may the campaign develop its own method — and the inadequacy must
   be documented with measurements, not vibes.
6. **The ear's scale is 1–7**, anchored as: 1 terrible, 2 bad, 3 average,
   4 good, 5 great, 6 exceptional, 7 one-of-a-kind.
7. **DAW choice is decided by interface robustness**, not preference:
   Ableton Live vs. Pro Tools, whichever supports deeper, more reliable
   programmatic control from the backend. The evaluation is Track 4's first
   deliverable.

## Required Novelty

Across the tracks, at least four of the following are required:

- A **rules/pattern ledger format** for extracted compositional rules that is
  expressive enough to regenerate a score "in the style of" its sources
  deterministically, with per-rule provenance back to source clips.
- A **deterministic MIDI-to-texture layer** — effect chains and heuristics
  that measurably close the gap between a bare MIDI render and the original
  song's texture, with an objective texture-distance metric to prove it.
- A **mess-scale heuristic battery** (melody quality, timbre quality, form
  quality, dynamics quality, …) with stated failure modes, plus an
  **intra-song meta-heuristic tracker** that aggregates clip-level heuristics
  into macro-scale (whole-song) descriptors.
- A **trainable ear** whose 1–7 predictions on held-out user-rated playlists
  beat non-trivial baselines, and which is demonstrably invariant to the
  non-factor sidecar.
- A **layered DAW/score corpus-mining system** — deterministic floor, agentic
  ceiling (the comsol-support pattern): a deterministic lookup layer over
  mined official docs/APIs that answers what it can exactly, with an agentic
  layer above it for everything the deterministic floor cannot answer, plus a
  telemetry/live-debugging loop that feeds failures back into the floor.
- An **honest transcription-accuracy survey** of open-source separation and
  transcription tools on this campaign's own clip corpus, with a documented
  build-vs-adopt decision per stage.

The final report must state explicitly, per track, what is new, what is merely
integrated, and what remains speculative.

---

## Track 1 — Corpus Engine (harvest, chunk, classify, provenance)

**Goal.** A reproducible corpus builder from user-provided YouTube playlists
to a curated, music-only, provenance-complete library of 30 s clips.

**Capabilities.**
- **Audio harvesting:** download audio from a user-provided YouTube playlist
  (see Guardrails — lawful, ToS-respecting acquisition for personal research
  use only; the harvester is an interchangeable input stage, and the rest of
  the pipeline must also accept locally supplied audio files so no downstream
  track is blocked on acquisition policy).
- **Chunking:** split each track into 30 s clips (fixed decision #1); decide
  and document hop/overlap and edge-clip handling.
- **Provenance ledger:** `clip_provenance.tsv` — clip id, source song id,
  source title/artist (as sidecar-only fields), start timestamp, end
  timestamp, checksum, acquisition date.
- **Classification:** clip-level classifier over {speech, applause,
  background/ambient, music{live, recorded}}; music-only filter gates the
  curated corpus.
- **Sidecar:** `clip_sidecar.tsv` holding all non-factors (fixed decision #4).
  Downstream stages read the curated clip list, never the sidecar.

**Validation.** Held-out labeled clips for the classifier (confusion matrix,
per-class precision/recall); spot-audit of provenance timestamps against the
source audio; an automated check that no downstream artifact imports or joins
the sidecar.

**Falsification.** If the music/non-music filter's errors correlate with a
non-factor (e.g. it drops live recordings or a particular language at a higher
rate), the curation step is leaking non-factors — flag and fix before any
downstream training.

**Parallelism.** Per-song fan-out for download + chunking; per-clip-batch
fan-out for classification.

---

## Track 2 — Separation and Transcription

**Goal.** From a curated music clip to a complete, merged symbolic
transcription.

**Capabilities.**
- **Audio splitting (source separation):** isolate vocals from instruments;
  isolate individual instruments (stems).
- **Instrumental transcription** of each split stem, covering all six axes:
  rhythm, melody, timbre, dynamics, harmony, form.
- **Vocal transcription:** lyrics extraction (vocals-to-text), vocal melody,
  vocal rhythm, and harmony detection.
- **Merged transcription:** recombine per-stem transcriptions into a full
  score for the clip/song.
- **Open-source survey first (fixed decision #5):** benchmark candidate tools
  (e.g. current open-source separation and AMT systems) on this campaign's own
  clips; adopt the winners; build custom methods only where the survey proves
  inadequacy, and document why.

**Validation.** A small hand-verified reference set: clips where a competent
listener has checked the transcription (notes, rhythm, chords, lyrics) so that
tool accuracy is measured on in-domain data, not just published benchmarks.
Round-trip checks: render the transcription to audio and measure similarity to
the separated stems.

**Falsification.** If merged transcriptions systematically lose one of the six
instrumental axes (timbre and form are the likely casualties), say so
explicitly — the rules ledger (Track 6) cannot extract what transcription
never captured.

**Parallelism.** Per-clip and per-stem fan-out; per-tool fan-out for the
survey benchmark.

---

## Track 3 — Score, MIDI, and the Composing-Tool Bridge

**Goal.** Symbolic transcriptions become editable scores and DAW-ready MIDI.

**Capabilities.**
- **Score generation:** a backend bridge to MuseScore (or another open
  composing tool if the survey favors it) that turns merged transcriptions
  into engraved, editable scores programmatically.
- **Corpus mining + telemetry loop for the bridge:** mine the composing
  tool's docs/API corpus; instrument the bridge with telemetry and a live
  debugging loop so bridge failures are captured, diagnosed, and folded back
  into the deterministic layer (same layered pattern as Track 4).
- **Score → MIDI conversion**, preserving as much of dynamics/tempo/voicing
  as the format allows.
- **MIDI import into the DAW** (consumes Track 4's control layer), landing
  stems on the right tracks/instruments.

**Validation.** Round-trip fidelity: transcription → score → MIDI → re-parsed
symbolic form, diffed against the original transcription; a batch of scores
opened and audited in MuseScore without manual repair.

**Parallelism.** Per-score fan-out; bridge development is largely serial until
its API surface stabilizes, then per-document fan-out for corpus mining.

---

## Track 4 — DAW Control Layer (deterministic floor, agentic ceiling)

**Goal.** Control all features of a professional DAW from the backend.

**Capabilities.**
- **DAW selection study (first deliverable):** evaluate Ableton Live vs.
  Pro Tools strictly on robustness of programmatic control (API/scripting
  surface, remote-control protocols, headless/automation support, latency,
  reliability, licensing/automation friction). Choose one; document the
  decision matrix. (Fixed decision #7: robustness decides.)
- **Layered corpus-mining system over DAW-specific docs**, modeled on
  comsol-support: a **deterministic floor** — mined, indexed, exactly-quotable
  official documentation and API references answering known questions with
  zero model involvement — under an **agentic ceiling** — an agent that
  handles everything the floor cannot, and whose successful resolutions are
  distilled back down into the floor.
- **Backend control of the full DAW feature surface:** track/device creation,
  MIDI import and routing, instrument/effect selection and parameterization,
  automation lanes, mixing, rendering/bounce — everything Track 6's pipeline
  needs, driven headlessly where possible.
- **Telemetry/live-debugging loop:** every backend→DAW command logged with
  outcome; failures reproduce into test cases.

**Validation.** A scripted end-to-end demo: backend builds a session from a
MIDI file, applies a specified effect chain, and renders audio, with zero
manual DAW interaction. Coverage report: which DAW features are controllable
from the backend, which are not, and why.

**Falsification.** If neither DAW offers robust enough control for the
pipeline's needs, report the gap honestly and scope what is controllable
rather than faking coverage.

**Parallelism.** Per-doc-section fan-out for corpus mining; per-feature
fan-out for control-surface coverage tests.

---

## Track 5 — Heuristics and the Trainable Ear

**Goal.** Measure music quality — at clip scale, at song scale, and with a
trained judge.

**Capabilities.**
- **Mess-scale heuristics:** per-clip quality heuristics along named axes —
  melody quality, timbre quality, form quality, dynamics quality, and
  additional axes as justified. Each heuristic states what it measures, its
  scale, and its known failure modes.
- **Intra-song meta-heuristic tracker:** aggregates clip-level heuristics
  across a song into macro-scale descriptors (arc of dynamics, form-level
  coherence, section contrast), so song-scale quality is not just a mean of
  clip scores.
- **Trainable ear:** a judge trained on user-provided YouTube playlists rated
  1–7 (fixed decision #6). Input: audio clips (and optionally symbolic
  features from Track 2); output: predicted 1–7 rating with calibration.
- **Non-factor firewall enforcement:** the ear and all heuristics must be
  invariant to the sidecar. Test it: predictions must not shift when
  non-factors are permuted, and a probe trained to recover non-factors from
  the ear's internal features should perform near chance — or the leak must
  be reported.

**Validation.** Held-out playlist ratings (rank correlation and per-band
accuracy against the user's 1–7 labels); heuristic sanity suites (known-good
vs. deliberately corrupted audio: detuned melody, flattened dynamics,
shuffled form); meta-tracker checked against whole-song human judgments.

**Falsification.** If the ear's accuracy comes from a non-factor proxy
(e.g. it learned a genre or era detector), that is a firewall breach, not a
result — report it and retrain. If mess-scale heuristics do not separate
known-good from corrupted audio, they are decoration; drop or fix them.

**Parallelism.** Per-heuristic fan-out; per-playlist fan-out for ear training
and evaluation; ablation matrix fan-out for firewall tests.

---

## Track 6 — Sampling, Rules Extraction, and Deterministic Generation

**Goal.** The end-to-end payoff: remix engines, extracted rules, texture
recreation, and deterministically generated new songs.

**Capabilities.**
- **Audio sampling engine:** remixing and remastering tooling; "chop and
  flip" workflows that put a new spin on an original song by chopping it up
  and recombining it, in the tradition of popular hip-hop and rap production —
  driven by clip provenance so every sample in a remix is traceable.
- **Rules/pattern extraction:** from each song's full transcription, extract
  and save the rules and patterns that govern it (harmonic movement, rhythmic
  signatures, form templates, melodic contours, arrangement patterns) into a
  cross-song **rules ledger** with per-rule provenance.
- **Effect layering:** apply audio effects to bare MIDI renders to give them
  life and color.
- **MIDI-to-texture heuristics (the hardest and most important piece):**
  deterministic effect chains + heuristics that recreate the texture of the
  original song from its MIDI recreation. Define a texture-distance metric
  (spectral/timbral/dynamics-based) between the re-rendered audio and the
  original; drive the deterministic layer to minimize it; report the residual
  gap honestly.
- **Multi-song accumulation:** repeat the full pipeline over many songs,
  growing the rules ledger and the MIDI-to-texture heuristic library.
- **Deterministic new-song generation:** select compatible rules/patterns
  from the ledger, compose a new score deterministically, render to MIDI, and
  push it through the same MIDI → DAW → effects → texture pipeline used for
  recreations — so generation is the recreation path pointed at a new score,
  not a separate system. Judge outputs with Track 5's ear and heuristics.

**Validation.**
- **Recreation benchmark (gate for generation):** for held-out songs, measure
  texture distance between (a) bare MIDI render, (b) effect-layered render,
  (c) full deterministic-texture render, and the original. The claim "the
  texture layer works" is the measured (a)→(c) improvement.
- **Rules-ledger regeneration test:** regenerate a score from a single song's
  extracted rules and check it is recognizably derived from that song's
  patterns (symbolic similarity + ear score).
- **Generation test:** new songs scored by the ear; target distribution
  stated in advance (see Hypotheses).

**Falsification.** If the deterministic texture layer cannot beat a trivial
baseline (e.g. a stock general-purpose mastering chain applied blindly), the
"deterministic texture heuristics" claim fails — report it as the campaign's
central open problem rather than papering over it.

**Parallelism.** Per-song fan-out for rules extraction and recreation
benchmarks; per-(rule-set × generation-seed) fan-out for generation trials.

---

## End-to-End Pipeline (the campaign's spine)

Every stage below must exist as a callable, tested step, and the whole chain
must run unattended on at least a small corpus:

1. Audio harvesting (YouTube playlist or local files) — Track 1
2. Audio identification/classification, music-only curation — Track 1
3. Source separation (vocals, per-instrument stems) — Track 2
4. Transcription of split tracks — Track 2
5. Merged transcription (full score) — Tracks 2–3
6. Recreation of transcription as MIDI track — Track 3
7. MIDI import into DAW — Tracks 3–4
8. Extraction and saving of rules/patterns governing the transcription — Track 6
9. Effect layering to give life/color to MIDI tracks — Tracks 4, 6
10. Deterministic audio effects + heuristics recreating the original song's
    texture (**hardest, most important**) — Track 6
11. Repeat over multiple songs, accumulating rules and MIDI-to-texture
    heuristics — Track 6
12. Deterministic generation of new songs: select similar rules/patterns,
    start from a direct transcription-style score, run the full
    MIDI-to-full-audio path — Track 6, judged by Track 5

## Phase Plan and Fan-Out

```text
[BARRIER 0] Phase 1 — scope, schemas, tool survey plan, DAW selection study,
            legal/licensing review (single coordinator)
   ↓
[FAN-OUT A] Phase 2 — Corpus Engine (Track 1) ∥ open-source tool survey
            (Track 2 benchmark harness) ∥ DAW corpus mining floor (Track 4)
   ↓
[BARRIER 1] curated corpus frozen (provenance + sidecar complete);
            build-vs-adopt decisions recorded per stage
   ↓
[FAN-OUT B] Phase 3 — separation + transcription (Track 2) ∥ score/MIDI
            bridge (Track 3) ∥ DAW control surface (Track 4) ∥ heuristics +
            ear training (Track 5)
   ↓
[BARRIER 2] first end-to-end recreation of one song, however rough
   ↓
[FAN-OUT C] Phase 4 — rules extraction ∥ sampling/remix engine ∥
            MIDI-to-texture heuristics ∥ ear refinement + firewall ablations
   ↓
[BARRIER 3] recreation benchmark passes its stated gate on held-out songs
   ↓
[FAN-OUT D] Phase 5 — multi-song accumulation ∥ deterministic generation
            trials ∥ ablations
   ↓
[BARRIER 4] ledger reconciliation: rules ledger, heuristic library,
            prediction/claims ledger
   ↓
Phase 6 — final synthesis (single coordinator)
```

Barrier discipline: schemas (provenance, sidecar, rules ledger, texture
metric) freeze at their barrier and change only through a coordinator. The
rules ledger and heuristic library are single sources of truth — per-clone
sub-ledgers merge at barriers, never concurrent writes to the master.

## Required Final Deliverables

1. `corpus_engine/` — harvester, chunker, classifier; `clip_provenance.tsv`;
   `clip_sidecar.tsv`; classifier evaluation report.
2. `tool_survey.md` — the open-source separation/transcription/score survey
   with on-corpus benchmarks and per-stage build-vs-adopt decisions.
3. `separation_transcription/` — pipelines + the hand-verified reference set
   and accuracy report across all transcription axes.
4. `score_midi_bridge/` — MuseScore (or chosen tool) bridge, telemetry logs,
   round-trip fidelity report.
5. `daw_control/` — DAW selection study, deterministic-floor corpus index,
   agentic-ceiling agent, feature-coverage report, scripted end-to-end demo.
6. `heuristics_ear/` — mess-scale battery, intra-song meta-tracker, trained
   ear + calibration report, non-factor firewall ablation report.
7. `rules_ledger/` — cross-song rules/pattern ledger with provenance.
8. `texture_layer/` — deterministic MIDI-to-texture effects + heuristics,
   texture-distance metric definition, recreation benchmark results.
9. `sampling_engine/` — remix/remaster/chop-and-flip tooling with
   provenance-traced outputs.
10. `generated/` — deterministic new-song trials with ear scores and the
    exact rules/patterns each was generated from.
11. `claims_ledger.tsv` — every quantitative claim, its status
    (`validated` / `falsified` / `pending` / `data-limited`), and its
    evidence artifact.
12. `final_report.md` and `audit_report.md`.
13. Reproducible code, tests, and build scripts throughout.

## Success Criteria

The campaign succeeds if, at minimum:

- The curated corpus exists with complete provenance, music-only filtering,
  and a verified non-factor firewall.
- Transcription accuracy is measured (not assumed) on in-domain clips, with
  honest per-axis coverage including timbre, dynamics, and form.
- The backend can build a DAW session, import MIDI, apply effects, and render
  audio with zero manual DAW interaction.
- The recreation benchmark shows a measured, non-trivial texture-distance
  improvement from bare MIDI to the deterministic texture layer on held-out
  songs.
- The ear beats stated baselines on held-out user ratings and passes the
  firewall ablations.
- At least one batch of deterministically generated new songs exists,
  end-to-end, with ear scores and full rule provenance.

The campaign fails if it produces only: a downloader plus a pile of stems; a
transcription pipeline whose accuracy was never measured on its own corpus; a
DAW "integration" that requires a human clicking; an ear that is secretly a
genre detector; or generated audio whose texture step is an off-the-shelf
mastering preset with no measured contribution.

## Guardrails

- **Copyright and terms of service.** Harvested audio is for the user's
  private research/analysis only. Comply with applicable law and platform
  terms when acquiring audio; prefer the user's own library, licensed, or
  freely licensed sources where the pipeline permits. Never redistribute
  harvested audio, stems, or clips; keep them out of the public repo (corpus
  artifacts stay local; only code, schemas, metrics, and reports are
  publishable). Generated songs must come from the rules ledger and texture
  heuristics, not from recognizable copied audio; remix/sampling outputs are
  private experiments, not releases.
- **Non-factor firewall.** No stage conditions on sidecar fields. Violations
  found in ablation are reported, not quietly patched.
- **Provenance is mandatory.** A clip, stem, transcription, rule, or
  generated song without a resolvable provenance chain is an invalid
  artifact.
- **Survey before building.** No custom model where an adequate open-source
  tool exists; inadequacy claims require on-corpus measurements.
- **Honest metrics.** Texture distance, transcription accuracy, and ear
  calibration are defined before results are collected; negative results are
  reported as results.
- **No silent scope shrink.** If a stage (e.g. timbre transcription, full DAW
  coverage) proves infeasible, the gap is documented in the final report, not
  dropped from the success criteria.

## Initial Hypotheses

- **H1.** Open-source source separation is adequate (adoptable) for
  vocals-vs-instruments and for the common stem classes; open-source
  transcription is adequate for melody/rhythm/harmony but inadequate for
  timbre and form, which will need campaign-built methods.
- **H2.** The 30 s clip length preserves enough melodic context that
  clip-level transcriptions can be merged into song-level scores without
  major boundary artifacts, given a sensible overlap policy.
- **H3.** Ableton Live will win the DAW selection study on interface
  robustness (remote-control surface depth), but the study may falsify this.
- **H4.** The deterministic floor will resolve the majority of routine DAW
  and score-bridge operations without agentic involvement once the mined
  corpus and telemetry loop mature.
- **H5.** The ear will reach useful rank correlation with user ratings from
  audio features alone, and firewall ablations will initially catch at least
  one non-factor leak (most likely era/production-quality proxies).
- **H6.** The MIDI-to-texture layer will close a substantial fraction of the
  measured texture gap on sparse arrangements and a smaller fraction on dense
  ones — and this residual will be the campaign's headline open problem.
- **H7.** Deterministically generated songs built from rules of highly rated
  (5–7) source songs will score measurably higher on the ear than songs built
  from rules of low-rated (1–3) sources — the key end-to-end signal that the
  rules ledger captures something real about quality.
