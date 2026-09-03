# v4 sound-matching layer — implementation spec (operator-decided 2026-09-03)

Goal: per instrument, per song, make the rendered MIDI track SOUND like the
original song's stem, then recombine. Two-phase policy applies: the SEARCH
may be stochastic/agentic; the winning PROFILE and its replay are strictly
deterministic. Not a hardened spec — the run refines details in place, but
the decided shape below is binding.

## Candidate space (three families, searched together)
1. **Soundfont/SFZ presets (first line).** Sweep every plausible preset in
   FluidR3_GM plus additional free .sf2/.sfz instrument libraries
   (survey-open-source-first: e.g. GeneralUser GS, Salamander-class sfz
   sets, VSCO-community; install with receipts). Deterministic replay via
   fluidsynth/sfizz.
2. **Original-stem sampled instruments (accuracy ceiling).** Build a
   per-song SFZ instrument FROM the original separated stem: slice clean
   hits/notes at onsets (drums: per-class hits; bass/keys/guitar: stable
   sustained notes per detected pitch), map slices across the key range,
   loop sustained regions where needed. Closest timbre by construction.
   PRIVACY RULE: original-stem audio is used ONLY inside this workspace
   for comparison and sound reconstruction; sampled-instrument banks live
   under `data/` (never committed) like all audio.
3. **Surge XT patches (second line).** Only where families 1–2 can't get
   close (synth-heavy parts). Nondeterministic replay ⇒ pinned-bounce
   escape hatch (`render_replayable: false`, sha-pinned stem bounce).

All three families compete under the same objective; the winner is
whichever matches best — the run should A/B the top candidate of each
family per instrument in its milestone delivery so the operator hears the
choice.

## Objective (search scoring)
Panel composite on candidate-render vs original stem over the SAME MIDI
excerpt: weighted mel-spectrogram L1 + spectral-centroid error + VGGish
embedding cosine (reuse `rc6_v2_panel_gate` components). Weights fixed
once at milestone start and recorded in every profile.

## Procedure (per instrument, bounded)
- **Stage 1 — coarse sweep:** render one 8-bar representative excerpt
  (chosen from the operator section by note-density) with EVERY candidate
  preset/instrument; rank by objective; keep top-5 (ensure ≥1 candidate
  from each family survives to stage 2 when available).
- **Stage 2 — fine fit:** on each finalist, fit the FX chain — per-band
  EQ (match the stem's average spectrum in bands), gain, compressor
  (threshold/ratio fit to the stem's envelope statistics), one shared
  reverb send level — grid/coordinate search, objective-scored; pick the
  overall winner.
- Budget: minutes per instrument, hours per song max. Stochastic steps
  allowed; record seeds anyway for post-hoc study.

## Profile artifact (`data/v4/profiles/<song_sha16>/<instrument>.json`)
- family (sf2|sfz|stem_sampled|surge), instrument identity (file + preset
  or sfz path), all FX parameters, gain, reverb send;
- sha256 of every dependency (soundfont/sfz/sample bank/plugin binary);
- objective scores (final + per-component), search metadata (seed, n
  candidates, date);
- `render_replayable`: true|false (false ⇒ `bounce_sha256` + bounce path).

## Replay (deterministic)
`MIDI + profile → stem audio` via fluidsynth/sfizz + Pedalboard offline
chain; deterministic replay proven ×2 once per render family per song
(relaxation 2026-09-03 — each profile records its render sha); then
per-stem loudness match to the original stem (rc7) and sum. Generated
songs inherit their donor's profiles wholesale.
