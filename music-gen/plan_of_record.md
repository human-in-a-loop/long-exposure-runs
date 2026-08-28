---
created: 2026-08-28T04:07:04Z
run_id: run-2026-08-28T040704Z
agent: researcher
last_edit: 2026-08-28T04:12:00Z
---

# Plan of Record — Music-Gen campaign

**Created:** 2026-08-28T04:07:04Z
**Run id:** run-2026-08-28T040704Z

## Directive (verbatim)

Execute the Music-Gen campaign defined in music_gen_long_exposure_prompt.md at the root of this working directory (/home/user/long-exposure-runs/music-gen). The prompt's Fixed Decisions are binding. The toolchain is pre-provisioned and verified (workspace/smoke_test.py, all 14 stages green 2026-08-28). The user's rated playlists (ear bands 6/5/4) are registered with full provenance in corpus/ratings/ratings_manifest.tsv, but audio downloads are currently blocked by the workspace egress policy - see corpus/CORPUS_STATUS.md. Per the prompt, acquisition must never block downstream work: proceed on stages that do not require the rated audio, and periodically retry workspace/harvest_playlists.sh in case the network policy changes.

## Goals

| Goal ID | Goal                                                                                       | Owner       |
|---------|--------------------------------------------------------------------------------------------|-------------|
| G1      | Deliver the first end-to-end recreation spine on 5–10 songs: harvest → chunk → classify → separate → transcribe → merged score → MIDI → DAW render, with unbroken provenance. | researcher |
| G2      | Build the DAW-as-instrument layer: unattended Ardour + DawDreamer control of session, MIDI import, plugin params, automation, render — backed by a floor-and-ceiling knowledge stack. | researcher |
| G3      | Build the two judges: a hand-built heuristic battery (with intra-song meta tracker) and the trained ear (1–7 from user playlists), with non-factor leak tests. | researcher |
| G4      | Build the rules ledger and the deterministic texture layer that closes the bare-MIDI-to-original gap measured on the fixed multi-metric texture panel. | researcher |
| G5      | Generate at least one batch of new songs deterministically from the rules ledger and score them with heuristics + ear. | researcher |

## Milestones

| Milestone ID       | Goal | Description                                                                                              | Success criteria (falsifiable)                                                                                                                                                                | Dependencies       |
|--------------------|------|----------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------|
| M-INGEST-1         | G1   | Ingestion chassis: harvester (local-folder + YouTube front doors), 30 s / 5 s-overlap chunker, provenance ledger schema, tail-handling rule, egress retry probe. | On ≥1 public-domain seed song: chunker emits 30 s clips with 5 s overlap; every clip carries (source_id, t_start, t_end); replay reproduces the same clips bit-for-bit; retry probe records status of harvest_playlists.sh. | —                  |
| M-CLASS-1          | G1   | Music/non-music classifier: pretrained tagger (PANNs/YAMNet/AST) mapped to project taxonomy (speech / applause / ambient / music-live / music-recorded), with a non-factor sidecar writer. | On a held-out labeled set (ESC-50 subset or hand-labeled seed clips): confusion matrix reported; music-vs-not-music decision accuracy ≥ 0.90 on that set; non-factor sidecar populated for every clip and readable by nothing downstream. | M-INGEST-1         |
| M-DAW-SPIKE-1      | G2   | DAW-stack validation spike: unattended coverage matrix for session build, MIDI import, instrument+effect parameterization, automation, render across Ardour and DawDreamer; agreement check between the two on one shared chain. | Coverage matrix filled in with green/red/gap per axis; a MIDI file rendered through the same effect chain in both Ardour (offline) and DawDreamer produces bit-comparable or measurably-close audio; gaps documented with fallback plan.       | —                  |
| M-SEP-1            | G1   | Source-separation survey and adopt-or-build verdict: demucs (already verified) vs at least one alternative on 4-stem split, benchmarked on this project's seed clips using an objective metric (SI-SDR / SDR). | Benchmark table with per-stem SI-SDR on seed clips; adopted separator named; per-instrument isolation of the "other" stem explicitly deferred to a later milestone.                                | M-INGEST-1         |
| M-TRANS-1          | G1   | Transcription survey across the six axes (rhythm, melody, timbre, dynamics, harmony, form) and vocals-to-text: at minimum basic-pitch baseline + one alternative on pitch/rhythm; honest coverage note for timbre/dynamics/form. | Per-axis coverage report published; note-level F1 measured for pitch on seed clips against a manually-corrected reference; timbre/dynamics/form axes flagged with what is measured vs. what is not. | M-SEP-1            |
| M-SCORE-1          | G1   | Score bridge to MuseScore: programmatic score creation/edit + score→MIDI + MIDI→score round trip driven by scripts. | Round trip preserves note events on a ≥8-bar test score; a script assembles a merged full-song score from per-stem transcriptions on 1 seed song.                                              | M-TRANS-1          |
| M-HEUR-1           | G3   | Hand-built heuristics battery on the mess-scale: melody, timbre, form, dynamics; plus intra-song meta-heuristic tracker for macro descriptors. | Each heuristic has a defined scale + documented blind spots; battery runs on ≥1 rendered clip and outputs a score vector; meta-tracker produces macro descriptors on a whole seed song.       | M-INGEST-1         |
| M-EAR-1            | G3   | Ear model baseline v0: 1–7 predictor trained from the 80 rated songs (once audio arrives) with non-factor leak tests (genre, era, artist). | Held-out ordinal accuracy beats majority-class and length baselines; leak tests show no per-non-factor performance drop when the sidecar is scrambled.                                          | M-INGEST-1, M-CLASS-1, rated audio available |
| M-RULES-1          | G4   | Rules ledger schema (typed JSON/YAML) + first extraction from 1 song's merged score covering harmonic / rhythmic / melodic / form / arrangement rule types. | Schema versioned + documented; ≥5 rules extracted from 1 song with provenance pointers into the transcription; ledger re-read reproduces the same rules.                                       | M-SCORE-1          |
| M-TEX-1            | G4   | Texture distance panel + first bare-MIDI-vs-original stage-by-stage measurement (bare MIDI → effects layered → texture heuristics). | Panel implemented with multi-scale spectral, dynamics-envelope, and one perceptual-embedding distance side-by-side; measurement table for at least one held-out song shows numbers per stage.  | M-DAW-SPIKE-1, M-SCORE-1 |
| M-GEN-1            | G5   | First deterministic generation: rules-ledger-driven fresh score pushed through the same score→MIDI→DAW→effects→texture path; ear + heuristics scored. | ≥1 generated song produced end to end with full provenance; ear + heuristics scores recorded; audible artifact stored (not committed).                                                       | M-RULES-1, M-TEX-1, M-EAR-1 |

## Out of scope (explicit)

- Ableton Live, Pro Tools, or any DAW requiring GUI/licensing (superseded 2026-08-28).
- Per-instrument isolation inside the "other" stem in the first milestone — deferred to a refinement round.
- Any decision, model input, or curation branch that reads a non-factor attribute.

## Pointer to ledger

Every milestone status, history, and judgment lives in `promise_ledger.jsonl`,
filtered by `milestone_id`. Run `promise_check` to materialize the current
state for the human; agents call it via Bash:

    python3 -m long_exposure.tools.promise_check .

The directive section above is **immutable** after creation. Goals and
milestones tables are mutable, but every edit must emit a ledger event with
`milestone_id: "_plan/<descriptive-change-name>"` so the audit trail is
complete.
