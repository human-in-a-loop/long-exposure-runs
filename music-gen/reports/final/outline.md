# Music-Gen Final Report — Outline

## Intended audience

An expert in deterministic music-generation systems and music
information retrieval (source separation, transcription, symbolic
rules, effect-chain rendering, ordinal listener modelling) who has no
knowledge of this project's internal harness, ledger, or agent
process. Register: technical, quantitative, honest about negative
results. Domain jargon (mel L1, F1, τ, PANNs/CLAP/VGGish, LV2/VST3,
DawDreamer, Ardour, htdemucs, basic-pitch, CORN, SB1/SB2/SB3, mir_eval)
is kept intact. Process artefacts (milestone IDs, ledger events,
cycle/fork numbers, promise-check statuses, auditor decisions) are
translated to plain-language equivalents at the point of use.

## Narrative arc

Problem-then-progression, not chronology. The report opens with the
project bet (long-way-round, artefact-first, deterministic
recreation-before-generation), states the operating constraint (rated
audio was egress-blocked for most of the run), and then walks the
pipeline in the order in which artefacts flow: ingestion →
classification → separation → transcription → score → rules → DAW →
texture → ear → recreation → generation → what remains. Each section
first states what was established, then how it was measured, then
what still isn't known.

## Sections and source assignments

Body stages are stages 2 through 8 (seven body writing stages);
stage 9 assembles the abstract, introduction, conclusions, and
references.

### §1 Abstract and Introduction — Stage 9 (finalize)

Sets the bet, the pipeline shape, the fixed decisions, and the
end-state at a glance (validated stages, open stages, headline
findings). Sources: project prompt; final audit headline; §9
conclusions.

### §2 Ingestion, provenance, classification, and the egress constraint — Stage 2

The private-corpus contract, 30 s / 5 s-overlap chunking, the
music/non-music classifier built on a PANNs/YAMNet-family tagger,
the non-factor sidecar, the eight-song rated corpus registration
under playlist-inherited 1–7 labels, and the workspace-egress denial
on `*.googlevideo.com` that shaped almost every downstream design
choice. Ends with the crash-resumable IDLE→ARMED→…→READY state
machine that ultimately fired one 6-stem model window (htdemucs_6s
fetch, HTTP 200).
Sources: `report_cycles_1-1_clone_0/1/2` (ingestion chassis),
`report_cycles_1-2_clone_0/1/2` (classifier + rated-corpus
provenance), `report_cycles_7-9` §M-INGEST-1/egress-ready-automation,
`report_cycles_56-58` (htdemucs_6s window), `report_cycles_49-51`
(long-hold on egress).

### §3 Source separation and transcription — Stage 3

Separation: htdemucs adoption after on-corpus benchmarking against
open-source peers; four-stem vocals/drums/bass/other; the deferred
per-instrument split under "other". Transcription: the M-TRANS-1
seven-axis coverage survey with adopt-or-build verdicts, the
basic-pitch 0.4.0 baseline (quarantined venv under TF-pin conflict),
librosa-family alternative construction after Crepe/onsets-frames
were blocked at install, and the basic-pitch octave-suppression
sub-milestone (3×3 grid over T_min × overlap_min). Honest per-axis
F1 on the M-SEP-1 synth reference and the frank statement that
timbre / dynamics / form are where transcription still goes silent.
Sources: `report_cycles_4-6` and its clones,
`report_cycles_7-9` §M-TRANS-1/basic-pitch/octave-suppression.

### §4 The merged score, the MuseScore bridge, and the rules ledger — Stage 4

The `mscore3 3.2.3` headless bridge (`QT_QPA_PLATFORM=offscreen`),
its determinism scrubbing list, and the interval-graph-colouring
workaround for the per-part MIDI voice cap. Round-trip byte-identity
across two full xml→mid→xml→mid→xml passes on the 8-bar seed. The
merged-score identity F1 (1.0 across drums/bass/other vs the input
MIDIs) and the honest F1 vs the tiled ground truth (upper-bounded by
basic-pitch). Then the M-RULES-1 schema (typed rule rows over
harmonic/rhythmic/melodic/form/arrangement, SHA-derived rule_id,
provenance pointers, planted-invalid rejection matrix) and the
extraction-half growing the ledger 28 → 76 rows on second seeds.
Sources: `report_cycles_7-9` §M-SCORE-1 and §M-RULES-1,
`report_cycles_10-12` (first generation, schema hardening),
`report_cycles_13-15` (76-row ledger, concat hardening).

### §5 The DAW stack and the palette-instrument determinism arc — Stage 5

The 2026-08-28 reversal from Ableton/Pro-Tools to Ardour +
DawDreamer + open plugins. Validation spike (M-DAW-SPIKE-1): what
the spike proved and the two documented gaps — GAP-1 (Ardour Lua
MIDI-file import) redefined-GAP via fluidsynth pre-render plus
hand-authored Ardour audio-region XML; GAP-2 (Ardour VST3 automation
delivery) still-GAP with the sharper diagnosis that the mechanism is
LV2 as well as VST3. Then the DawDreamer `set_automation` gap-closure
work (env_corr 0.487 — misses the 0.9 primary bar, satisfies the
0.15/0.3 secondary bar), the palette-instrument determinism arc
(Surge XT + Dexed rendered with parameter payloads deterministic
across salts), and the c31 STILL_GAP → activation on real render.
Sources: `report_cycles_13-15` §M-DAW-SPIKE-1/gap-closure,
`report_cycles_16-18` §Clone-1 DawDreamer set_automation,
`report_cycles_35-37` (c31 palette activation, STILL_GAP closure).

### §6 The texture panel (M-TEX-1) — Stage 6

The refuse-to-aggregate contract: multi-scale mel, spectral,
loudness-envelope, and CLAP/VGGish perceptual embedding distances
reported side by side. The stage-by-stage measurement (original ↔
bare-MIDI ↔ effects-layered, 24 numbers) and its widening across
three seeds (72 finite numbers, VGGish family-disagreement
content-dependent — persists on polyphonic, flips on monophonic
decaying-triad). The content-flip embedding analysis. What the panel
tells the reader: no single number is the texture score.
Sources: `report_cycles_7-9` §M-TEX-1/stage-by-stage,
`report_cycles_16-18` §Clone-2 widening,
`report_cycles_35-37` (content-flip analysis).

### §7 The ear model (M-EAR-1) — Stage 7

Preparation chassis on the 55-clip classifier validation set;
CORN ordinal 1-7 head; the non-factor leak-test harness clearing the
0.90 detection / 0.10 false-positive bar on artist, genre, era
plants. The head-side invalidation (τ ≈ 0.06 across three
regularization variants — ridge, bottleneck, frozen-projector — under
the c22 stability audit) and the feature-side invalidation (HEUR-only
4-D, PANNs-only 2048-D both FAIL C2'). Path A closure at N = 55
synthetic labels; Path B commit for real-label calibration. The v2
partial (SB3 axis passes, SB1 and SB2 fail under c26 thresholds) and
v2.1 SB3 50-control stability (FPR = 0.100 byte-deterministic × 2).
Ends honestly on the corpus gap (43 / 80 rated songs on disk).
Sources: `report_cycles_4-6` §M-EAR-1/preparation,
`report_cycles_23-25` §Clone-1 head regularization,
`report_cycles_26-28` §Clone-1 HEUR-only + PANNs-only,
`report_cycles_43-45` §Clone-1 SB3 F1_ADOPTED,
`report_cycles_49-51` (extraction advance under partial corpus),
`report_cycles_52-54` §Clone-0 EAR_v2p1_STABLE_FPR_PASS.

### §8 Recreation of real audio and the accurate-small-set programme — Stage 8

First end-to-end recreation of a rated song (M-RECREATE-1
RECREATION_LANDS, +5.906 dB mel_l1_db improvement effects-vs-bare on
band-7 song `016__LOCAL__05_02.mp3`). Then the accurate-small-set
programme (M-RECREATE-2) at the RC0 baseline plus RC1 (vocals
transcription, 4/5 lands), RC2/RC3 (drums / bass with post-processing),
RC7 (mix balance, EQ + loudness-match, 5/5 focus songs, 20/20 stem
accepts on substantive per-stem MIDIs), RC9 (first-class parts, 5/5),
RC10 (transcription real-stem resurvey, drums + bass impl-per-stem +
winner selection + post-processing). Frame each with what it
measures. Also covers the M-GEN-1 generation-batch arc (batch-v1
through batch-v6 palette-driven-v4), and the collision-modelling arc
that reached `PARTIAL_BP_UNRESOLVED_SHAPE` after exhausting the four
mechanism candidates (M1 coherence-gate coercion — structurally
disqualified; M2 effective-K — refuted; M3 hash-space geometry per
(rule_type × salt) — collapsed under multiple-testing correction;
M4 semantic-cluster overlap — refuted).
Sources: `report_cycles_43-45` §Clone-0 first-real-audio and
§Clone-2 palette-driven-batch-v4, `report_cycles_46-48`,
`report_cycles_49-51`, `report_cycles_52-54`,
`report_cycles_56-58` (RC7-RC9 stubs, htdemucs_6s),
`report_cycles_1-1_clone_0` (RC7 v2 rerun 5/5),
`report_cycles_20-22`, `report_cycles_23-25`,
`report_cycles_26-28`, `report_cycles_29-31`, `report_cycles_32-34`
(collision arc M1–M4).

### §9 Conclusions, honest limits, and future work — Stage 9

State what is done against the seven "what counts as done" criteria
in the project prompt, name the two live constraints (the ear's
real-label calibration depends on completing the audio downloads;
generation quality still depends on the recreation loop closing on
held-out songs), and list actionable next steps drawn only from the
final audit's `future_work` block. No new hypotheses.
Sources: project prompt "What counts as done", final audit summary
milestone distribution and future_work list.

### §10 References — Stage 9

Assembled from `REFERENCES.md` if present, otherwise from inline
citations across the cycle reports. Uses `[N]` bracket style
throughout the body.

## Notes to composer

- Never mention cycle numbers, session IDs, ledger event names, or
  fork suffixes in reader-facing prose. Reference prior sections
  by content ("as established in §4") or by what was measured.
- Do not repeat findings across sections. Cross-reference.
- Show numbers before interpretation. Show the negative result
  before naming it a negative result.
- The single most-important-and-hardest piece per the prompt is
  the texture layer; give §6 and §8 the space they deserve, and
  do not let the collision-modelling arc crowd out the recreation
  arc in §8.
- Draft path is `reports/final/draft.md`; append per stage.
- Final path is `reports/final/final_report.md`; assembled once at
  stage 9.
