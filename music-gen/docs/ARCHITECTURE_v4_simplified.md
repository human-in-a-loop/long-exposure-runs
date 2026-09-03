# Music-Gen v4 — simplified architecture (2026-09-03)

The holistic simplification after M-V3-FOCUS landed 5/5. Every key feature
of the audio reconstruction pipeline is retained; what changes is HOW MUCH
MACHINERY carries it. Guiding rule (operator doctrine): **deterministic
wherever possible, agentic only where necessary** — agents design and
improve programs; deliverables are reproducible program outputs.

## The pipeline, as one spine and four satellites

```
corpus mp3 ──► recreate_v3_checkpointed.py ──► delivery dir
              (ONE entrypoint, 9 stages, per-stage
               content-addressed cache, env-pinned,
               byte-determinism ×2 evidence built in)

satellites:  rules extractor │ ear trainer │ generator │ sound-profile search
```

**The spine** (`scripts/v3_spine/recreate_v3_checkpointed.py`) is the only
way audio is reconstructed or rendered — recreations and generated songs
alike. Stages: section slice → htdemucs_6s → per-stem MuScriptor
(whitelists) → canonical JSON→MIDI → merge+tempo map → render → vocal
overlay → mix match → panel+manifest. All deterministic; certificate
discipline per `guidance_2026-09-03_full_determinism_certificate.txt`.

**Satellites** are deterministic programs built/improved by agent cycles:
- `v3_rules` + `rules_rated_corpus`: corpus → hashed rules artifact.
- `ear_v2p1`: audio embeddings + ratings → seeded, reproducible 1–7 model.
- `gen`: rules + seed + config → MIDI (the generator program; agent
  creativity lives in DESIGNING it, hand-written songs only as flagged
  fallback).
- sound-profile search (NEW, below).

## What was simplified away
- Three pipeline generations collapsed to one: recreate_v0 and the v2
  per-stem DSP transcribers are gone; recreate_v2 survives only as the
  proven modules the spine imports (hybrid vocals, GM map, panel, mix
  match, section selection, 6-stem driver, gold set).
- Version ladders trimmed to their newest rung: ear_v2p1, palette_render_v4,
  rules_rated_corpus (+v3_rules); older rungs deleted (git history).
- One-off cycle scripts (deliver_song_<sha>.py, reproduce dirs, probes)
  are banned going forward: per-song facts live in data (focus_set json,
  profiles), never in code. The checkpointed driver is the only executor.
- Agent orchestration of renders is retired. Long computations run
  detached with per-stage caching; a session boundary never kills work.

## The MIDI sound-matching layer (operator-agreed policy, 2026-09-03)

Goal: per instrument, match the SOUND of the original song's stem (using
the split MIDI tracks), then recombine into the full song.

Two phases with different determinism rules:

**Phase 1 — SEARCH (agentic/stochastic, NOT required deterministic).**
Finding the sound that matches an original stem — patch selection across
Surge XT / sfizz / soundfont libraries, effect-chain and EQ/compression
parameter search — is an optimization/creative problem, scored by the
panel and ultimately the operator's ear. Random/heuristic/agentic search
is allowed and encouraged; reproducibility of the search itself is NOT
required. (The old fully-deterministic closed-form EQ fit was deterministic
and weak; do not regress to requiring that.)

**Phase 2 — PROFILE + REPLAY (strictly deterministic).**
The search's winner is frozen as a per-instrument, per-song **sound
profile** artifact: `data/v4/profiles/<song_sha16>/<instrument>.json` with
patch identity, all parameters, EQ points, gains, effect settings, and
sha256 of every dependency (plugin binary, soundfont, sfz). Rendering
`MIDI + profile → audio` must be byte-reproducible ×2 per stem before
recombination; profiles are the cache key. Generated songs inherit their
mix-donor's profiles.

**VST escape hatch**: if the ear-preferred patch renders nondeterministically
(known Surge XT finding), render once and sha-pin the bounced stem as the
artifact, recording `render_replayable: false` plus full settings in the
profile. Deterministic renderers are preferred at equal quality; timbre is
never sacrificed to replayability without an operator question.

## Layout contract for future runs
- `scripts/v3_spine/` — the spine (only executor of audio).
- `scripts/{separation,recreate_v2,score*,ingest}` — spine modules.
- `scripts/{v3_rules,rules_rated_corpus,ear,ear_v2p1,gen,palette,`
  `palette_render_v4,daw,dawdreamer_state}` — satellites.
- `data/v3/deliveries/` — operator deliverables (append-only).
- `data/v4/profiles/` — sound profiles (new).
- `docs/` top level — operator + architecture docs only; run reports go to
  `docs/run_archive/`, guidance snapshots to `docs/guidance/`.
- Rules for agents: no new version-suffixed dirs (improve in place with
  git history); no per-song scripts; every long computation through the
  checkpointed driver pattern; every milestone ships its double-run proof.
