# Operator deep-dive: why recreations sound wrong (2026-08-29)

User listening verdict on the delivered samples: "way off — mostly keyboard
only, hardly any drums or bass, sounds completely different." Operator audit
of the pipeline artifacts confirms this and identifies six root causes. These
are architectural, not tuning issues.

Evidence song: Chicken Grease (band 6, sha16 31a164f845f8e27e) — a
drum-and-bass-driven funk groove. 30 s excerpt.

## Root causes (ranked by audible impact)

**RC1 — Vocals are deliberately skipped.**
`scripts/recreate_v0/run_pipeline.py` line 288: "Stage 5: basic-pitch on
{drums, bass, other} (skip vocals)". The vocals stem is separated by htdemucs
and then thrown away. The lead melody of every song is simply absent from
every recreation. The campaign prompt requires vocal transcription (melody,
rhythm, lyrics-to-text); the pipeline dropped the entire stem.

**RC2 — Drums are transcribed with a pitched-note model.**
basic-pitch is a *pitched* transcriber; it is structurally incapable of drum
transcription. Result on Chicken Grease: **5 notes in 30 seconds** for a funk
drum groove that has hundreds of hits. Those 5 pitched notes (pitch range
29–48) are then flagged `is_drum=True`, so GM channel 10 plays 5 arbitrary
percussion sounds. That is why there are "hardly any drums."

**RC3 — Bass is massively under-transcribed and rendered as a piano.**
17 notes in 30 s for a funk bassline (should be ~60–150). basic-pitch's
default onset/frame thresholds miss low-register content. Worse, the bass
part inherits basic-pitch's default **program 4 (Electric Piano 1)** — so
what little bass survives is played as keyboard, not bass.

**RC4 — Every part is rendered as Electric Piano.**
merged.midi: bass=program 4, drums=program 4 (is_drum), other=program 4.
No per-stem GM program assignment exists anywhere in the pipeline. This is
the single direct cause of "mostly keyboard only."

**RC5 — No tempo/beat estimation.**
`initial_tempo=120.0` is hardcoded (line 348). Note timing survives via
absolute seconds, but the score/MusicXML quantization is built against a
fictional 120 BPM grid (the already-flagged c37 quantization defect is a
symptom), and nothing aligns transcription to the song's real beat grid.

**RC6 — The gate metric rewards the wrong thing.**
FULL_CORPUS_LANDS was gated on mel-L1 delta alone. On the delivered samples,
mel-L1 improved while **VGGish embedding distance got worse** (0.29→0.33 on
05/02) and **spectral centroid error got worse** (1678→1929 Hz). The effects
chain is smearing spectra toward a broadband average — gaming mel-L1 — not
adding fidelity. A pipeline that deletes the drums, bass, and vocals can
still "LANDS" under this gate. The gate must become a panel: no single
metric may confer success, and perceptual embedding must not regress.

## Second-pass audit (same day): three more root causes

**RC7 — No mix/balance matching.** The entire "texture" stage is a fixed
Surge XT chorus (Output Mix 0.35) + faint reverb (Output Mix 0.05) applied
identically to every song's full mix (`scripts/tex/content_flip/
apply_pinned_chain.py`). Rendered stem balance is whatever fluidsynth's
default patch loudness produces — never compared to the original stems.
A per-stem render module exists (`scripts/palette_render/render_stem.py`)
but the recreation pipeline does not use it.

**RC8 — Always the first 30 s from t=0.** Intros are systematically the
sparsest, least representative section; the pipeline never reconstructs a
chorus/full-groove section.

**RC9 — Arrangement collapse.** All non-bass/drums/vocals instruments
("other" = keys+guitar+horns+synths) are transcribed as ONE polyphonic part
on ONE patch.

## Operator design decisions (user-selected, 2026-08-29)

1. **Section selection:** auto-pick the peak 30 s window per song
   (max RMS + onset density) instead of t=0.
2. **Vocals:** HYBRID render — layer the original separated vocal stem over
   the reconstructed band. (Vocal melody is still transcribed into the score
   for the campaign's symbolic artifacts; it is just not synthesized in the
   render.)
3. **Arrangement:** switch separation to htdemucs_6s (piano + guitar stems
   first-class; thinner residual "other"), each with its own transcription
   and GM patch.
4. **Mix stage:** per-stem render → per-stem loudness match (RMS/LUFS) to
   the corresponding original stem → deterministic per-stem EQ curve fitted
   to the original stem's average spectrum → sum. Replaces the global
   chorus+reverb wash entirely.

## Third-pass finding (user listening audit of per-stem A/B pairs)

**RC10 — Transcription was validated on the easy case and is the core
failure.** The M-TRANS-1 survey measured transcription accuracy on
*synthetic* seed clips (clean fluidsynth renders of known MIDI — the easiest
possible input) and the adopted tool/settings were never re-benchmarked on
real separated stems. On real stems the transcription content is, in the
user's words, "very far off and completely wrong" — sparse, missing, or
wrong notes on every part. Every downstream stage (score, MIDI, render,
mix) faithfully reproduces a wrong transcription. Transcription accuracy is
the campaign's central unsolved problem, and it must be measured per stem
against the real separated stems, per song, forever after.

## Operator decisions (updated)

- The per-stem content gate applies to **ALL SIX parts** — drums, bass,
  guitar, piano, other-residual, and vocals — not just the rhythm section.
  Drums/bass keep fix *priority* only; the gate is all six.
- A transcription re-survey on REAL stems is mandatory (see directive).

## Operator directive queued alongside this audit

Stop breadth. Focus on **accurate reconstruction of 3–5 songs** with strong
rhythm sections (must include Chicken Grease), fixing RC1–RC10 under the
design decisions above, with pre-registered per-stem acceptance criteria on
all six parts, before any other new work.

## Fourth-pass audit (2026-09-02): conceptual blind spots

User verdict on the v2 gated winners (Chicken Grease + Peach Dream drums via
per-song GMM classification, Rome bass via onset-segmented pyin): **"ALL OF
THESE SAMPLES are still far off from the correct transcription."** v2 passed
its own gates and failed the ear — the gates themselves are the problem.
Operator audit identified seven structural blind spots:

**BS1 — Gates measure plausibility, not correctness; the F1 reference is
circular.** Onset F1 is computed against onsets from the same detector
family that feeds the transcriber. Nothing compares output to ground truth.

**BS2 — No musical time.** Absolute seconds only; no tempo map, beat grid,
or bars. Syncopation is unrepresentable and the ~15x-repeated groove loop is
never exploited — ~150 independent noisy decisions instead of repeats voting.

**BS3 — Model-class ceiling.** pyin / onset+GMM / basic-pitch are classical
or lightweight tools near their ceilings on real stems; threshold iteration
cannot recover what the representations never capture.

**BS4 — Verification lens conflates transcription with timbre.** GM
fluidsynth renders make even a correct transcription unverifiable by ear.

**BS5 — Independent per-stem transcription despite bleed coupling.** The
kick over-count was bass bleed; no cross-stem event reconciliation exists.

**BS6 — Drum vocabulary too coarse.** {kick,snare,hat} forces open/closed
hat, ghost snares, toms, cymbals into 3 clusters. Bass ghost detector found
0 ghosts across all five songs.

**BS7 — Peak-density section is the hardest possible input**; no easy-first
curriculum (a D1 side-effect).

**Directive queued (supersedes threshold tuning):** W1 gold-set reference
transcription (2–4 bars, Chicken Grease + What If I Go) as the accuracy
standard for all gates; W2 beat-grid + micro-timing + loop-repetition
evidence aggregation; W3 learned-transcriber re-survey (E-GMD/ADT drums,
CREPE f0, ByteDance piano, MT3-class) evaluated against gold; W4
concatenative resynthesis from the song's own hits as the primary A/B
listening artifact. Integrated: cross-stem reconciliation, BIC-chosen drum
vocabulary ≥7 classes, one sparse section per song alongside the peak
section. No transcription LANDS without gold-bar accuracy + resynthesis A/B
+ operator ear confirmation.
