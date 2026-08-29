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

## Operator directive queued alongside this audit

Stop breadth. Focus on **accurate reconstruction of 3–5 songs** with strong
rhythm sections (must include Chicken Grease), fixing RC1–RC6 as
pre-registered acceptance criteria before any other new work.
