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
| M-INGEST-1/chunker | G1   | Sub-milestone of M-INGEST-1: 30 s / 5 s-overlap chunker with tail-anchored final clip and short-song fallback. | Chunker tests green on all seed clips; sample-accurate boundaries; standard-overlap frames == 5.0 s exactly. | M-INGEST-1 |
| M-INGEST-1/provenance | G1 | Sub-milestone of M-INGEST-1: append-only JSONL provenance schema v1 with source/clip rows, Python + JSON-schema validators, replay round-trip. | Round-trip clip reconstruction is byte-identical; validator rejects duplicate/append-only violations. | M-INGEST-1 |
| M-INGEST-1/harvester-parity | G1 | Sub-milestone of M-INGEST-1: two front doors (local folder, YouTube playlist) converge on identical downstream manifests up to source_type/source_ref. | Parity test green; container-invariance test green (fingerprints computed on decoded PCM). | M-INGEST-1 |
| M-INGEST-1/egress-probe | G1 | Sub-milestone of M-INGEST-1: non-blocking two-stage YouTube-CDN reachability probe (yt-dlp metadata + 1 KiB media range). | ≥1 live probe row logged; probe never blocks other cycle work; two consecutive media_ok=true rows are the ingestion-unblock signal. | M-INGEST-1 |
| M-TEX-1/panel | G4 | Texture-distance panel implementation as a callable library (multi-scale spectral + dynamics envelope + one perceptual embedding) with per-metric documented scale, refusing to expose a weighted-sum overall — pre-M-SCORE-1 partial closure of M-TEX-1. | Panel returns exactly 8 keys, refuses aggregate; matched-pair reproduces clone-1's mel_l1_db=3.13, rms_env_rmse=0.041, spectral_centroid_rmse_hz=159.02 within ±5%; known-different pair ≥2× larger on mel_l1_db and spectral_centroid_rmse_hz; self-distance ≤1e-6 on numeric metrics, ≤1e-4 on embedding cosine. | M-TEX-1 |
| M-TEX-1/panel/spectral | G4 | Sub-milestone of M-TEX-1/panel: spectral family — multi-scale (64/128/256-mel) log-mel L1 in dB + spectral centroid RMSE in Hz, mono mixdown, hop=512 n_fft=2048. | Matched-pair (Ardour↔DawDreamer) mel_l1_db and spectral_centroid_rmse_hz reproduce clone-1 reference within ±5%. | M-TEX-1/panel |
| M-TEX-1/panel/envelope | G4 | Sub-milestone of M-TEX-1/panel: dynamics envelope family — RMS-envelope RMSE (mono, linear) + LUFS-M RMSE (stereo, EBU R128 400ms/100ms, LU). | Matched-pair rms_env_rmse reproduces reference within ±5%; LUFS-M finite and non-negative on non-silent pair. | M-TEX-1/panel |
| M-TEX-1/panel/embedding | G4 | Sub-milestone of M-TEX-1/panel: perceptual embedding cosine distance ladder — CLAP → VGGish → none_available (visible None, never fabricated). | Rung logged with source URL; cosine distance in [0,2] on validation pairs; self-distance ≤ 1e-4 (documented FP-nondeterminism tolerance). | M-TEX-1/panel |
| M-HEUR-1/melody | G3 | Sub-milestone of M-HEUR-1: melody_quality heuristic (pyin-based contour smoothness + interval variety + pitch-class entropy) on the mess-scale with documented blind spots. | Function computes 3 features, blends to [0,1] via mess_scale; ≥2 blind spots documented in module-level BLIND_SPOTS; returns null-with-reason on unvoiced-dominant clips. | M-HEUR-1 |
| M-HEUR-1/timbre | G3 | Sub-milestone of M-HEUR-1: timbre_quality heuristic (MFCC delta RMS + spectral centroid range + spectral flatness variance) on the mess-scale with documented blind spots. | Function computes 3 features, blends to [0,1] via mess_scale; ≥2 blind spots documented. | M-HEUR-1 |
| M-HEUR-1/form | G3 | Sub-milestone of M-HEUR-1: form_quality heuristic (chroma-CQT self-similarity diagonal-band ratio) on the mess-scale, null-with-reason below 30s. | Function computes SSM ratio, blends to [0,1] via mess_scale; ≥2 blind spots documented; returns null on <30s clips. | M-HEUR-1 |
| M-HEUR-1/dynamics | G3 | Sub-milestone of M-HEUR-1: dynamics_quality heuristic (crest factor + envelope-range ratio + envelope variance dB) on the mess-scale with documented blind spots. | Function computes 3 features, blends to [0,1] via mess_scale; ≥2 blind spots documented; returns null-with-reason on <5s clips. | M-HEUR-1 |
| M-HEUR-1/meta-tracker | G3 | Sub-milestone of M-HEUR-1: intra-song meta-heuristic tracker emitting dynamics_trajectory, form_coherence, peak_location_fraction, heuristic_variance_across_clips; honors anchored_tail debias weight (30−overlap)/30. | Meta-tracker JSON produced on all 3 seed songs; anchored-tail weight matches the formula numerically on seed_long_87s (0.2333…) and seed_mid_50s (0.6667…). |
| M-SEP-1/ground-truth | G1 | Sub-milestone of M-SEP-1: deterministic 3-stem ground-truth mixes (drums+bass+piano) synthesized via fluidsynth from committed MIDIs + committed FluidR3_GM.sf2 at 44.1 kHz stereo, at three durations {30, 60, 90}s. | Per-stem WAVs + summed mix WAV per duration; SF2 SHA-256 recorded; MIDI SHA-256s recorded; regeneration reproduces bit-identical WAVs. | M-SEP-1 |
| M-SEP-1/htdemucs-baseline | G1 | Sub-milestone of M-SEP-1: htdemucs 4-stem separation baseline on the three synthesized mixes with SI-SDR/SIR/SAR per (mix, stem) + vocals false-positive energy. | htdemucs runs on all 3 mixes unattended; 4 non-silent stems per mix; SI-SDR finite on drums/bass/other; est_energy_dBFS reported on vocals (GT-zero case). | M-SEP-1/ground-truth |
| M-SEP-1/alternative | G1 | Sub-milestone of M-SEP-1: alternative separator (open-unmix UMXHQ chosen after fetchability probe cleared both wheel and Zenodo weights) evaluated on the same three synth mixes with the same metric. | UMXHQ runs on all 3 mixes; same TSV schema as baseline; naive-copy baseline row present; adopt-or-build verdict cites the numbers. | M-SEP-1/ground-truth | M-HEUR-1 |

## Sub-milestones

Registered sub-milestones (used by workers/auditors to attach granular
validation events; each rolls up into its parent milestone above).

| Milestone ID                  | Parent      | Description                                                    |
|-------------------------------|-------------|----------------------------------------------------------------|
| M-INGEST-1/chunker            | M-INGEST-1  | 30 s / 5 s-overlap chunker with tail-anchored final clip.       |
| M-INGEST-1/provenance         | M-INGEST-1  | Append-only JSONL provenance schema v1 + validator + replay.    |
| M-INGEST-1/harvester-parity   | M-INGEST-1  | Local ↔ YouTube front doors converge on identical manifests.    |
| M-INGEST-1/egress-probe       | M-INGEST-1  | Non-blocking two-stage YouTube-CDN reachability probe.          |
| M-TEX-1/panel                 | M-TEX-1     | Texture-distance panel implementation (multi-scale spectral, dynamics envelope, one perceptual embedding) as a callable library with per-metric documented scale — pre-M-SCORE-1 partial closure of M-TEX-1. |
| M-HEUR-1/melody               | M-HEUR-1    | melody_quality heuristic (pyin contour smoothness + interval variety + PCP entropy) on the mess-scale + blind spots. |
| M-HEUR-1/timbre               | M-HEUR-1    | timbre_quality heuristic (MFCC-delta RMS + centroid range + flatness variance) on the mess-scale + blind spots. |
| M-HEUR-1/form                 | M-HEUR-1    | form_quality heuristic (chroma-CQT SSM diagonal-band ratio) on the mess-scale + blind spots + null-below-30s policy. |
| M-HEUR-1/dynamics             | M-HEUR-1    | dynamics_quality heuristic (crest factor + envelope-range ratio + envelope variance dB) on the mess-scale + blind spots. |
| M-HEUR-1/meta-tracker         | M-HEUR-1    | intra-song meta-heuristic tracker (dynamics_trajectory, form_coherence, peak_location_fraction, heuristic_variance_across_clips) honoring anchored-tail debias weight. |
| M-SEP-1/ground-truth          | M-SEP-1     | Deterministic fluidsynth-rendered 3-stem ground-truth mixes at 44.1 kHz stereo, durations {30,60,90}s. |
| M-SEP-1/htdemucs-baseline     | M-SEP-1     | htdemucs 4-stem separation baseline on the three synth mixes with per-stem SI-SDR/SIR/SAR + vocals false-positive energy. |
| M-SEP-1/alternative           | M-SEP-1     | Open-unmix UMXHQ alternative separator evaluated on the same three synth mixes with the same metric. |
| M-TEX-1/panel/spectral        | M-TEX-1/panel | Multi-scale mel L1 + spectral centroid RMSE (mono, hop=512, n_fft=2048).                           |
| M-TEX-1/panel/envelope        | M-TEX-1/panel | RMS-envelope RMSE + LUFS-M RMSE (EBU R128, 400 ms window / 100 ms hop, stereo).                    |
| M-TEX-1/panel/embedding       | M-TEX-1/panel | Perceptual embedding cosine distance with CLAP → VGGish → none_available ladder + rung log.        |

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
