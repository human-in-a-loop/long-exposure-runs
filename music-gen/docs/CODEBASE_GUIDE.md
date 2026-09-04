# Codebase guide — read this first (post-refactor, 2026-09-03)

You are a long-exposure agent joining the Music-Gen campaign after the
2026-09-03 cleanup/refactor. The working tree is deliberately small; the
messy history lives in git and `docs/run_archive/`. Do not recreate what
was removed.

## Orientation in five files
1. `music_gen_v3_prompt.md` — the campaign prompt (milestones, fixed
   decisions, operating rules). Binding.
2. `docs/ARCHITECTURE_v4_simplified.md` — how the pipeline is shaped, the
   determinism doctrine, and the sound-matching two-phase policy. Binding.
3. `docs/OPERATOR_recreation_root_cause_audit.md` — why v0–v2 failed;
   read to avoid repeating their mistakes.
4. `docs/REFACTOR_2026-09-03_inventory.md` — what was deleted/kept and why.
5. `docs/guidance/` — the operator decision log, chronological.

## The one rule about execution
ALL audio reconstruction and rendering goes through
`scripts/v3_spine/recreate_v3_checkpointed.py`, launched detached
(nohup/setsid + log), from the `music-gen/` root (module paths and the
RC4 anchor are CWD-relative). It is stage-cached (content-addressed): a
kill costs nothing; re-run to resume. Never hand-orchestrate a song in a
worker session; never write `deliver_song_<sha>.py`-style one-offs —
per-song facts belong in data files.

## Map
- `scripts/v3_spine/` — the spine: `recreate_v3.py` (stages),
  `recreate_v3_checkpointed.py` (entrypoint), `stage_cache.py`,
  `v3_pipeline/` (env pin), `gm_program_map_v3.py`, `palette_render/`.
- `scripts/recreate_v2/` — proven modules the spine imports (hybrid
  vocals rc1, GM map rc4, tempo grid rc5, panel rc6, mix match rc7,
  section selection rc8, htdemucs_6s driver rc9, gold set rc10).
- `scripts/separation/`, `scripts/ingest/`, `scripts/score*/` — spine
  support (demucs is the SYSTEM binary `/usr/local/bin/demucs`).
- Satellites: `scripts/v3_rules` + `scripts/rules_rated_corpus` (rules v3),
  `scripts/v4_rules` (rules v4 — Model A statistical + Model B CA/VOMM),
  `scripts/ear` + `scripts/ear_v2p1` (ear v3, audio-only),
  `scripts/v4_ear` (ear v4 — lightweight VGGish/CLAP exemplar ear),
  `scripts/gen` (generator v3), `scripts/v4_gen` (generator v4 — seeded
  hash-driven deterministic MIDI generator + interpolation-hybrid mode),
  `scripts/palette` + `scripts/palette_render_v4` + `scripts/daw` +
  `scripts/dawdreamer_state` (palette/DAW), `scripts/vst3_nondeterminism`
  (Surge nondeterminism evidence).
- `workspace/` — venv (`learned_transcribers_venv`: MuScriptor, torch,
  librosa), `models/muscriptor-medium/` (weights + SHA receipts),
  provisioning receipts, `smoke_test.py`.
- `corpus/` — rated audio (bands 4–7) + provenance. NEVER commit audio.
- `data/v3/deliveries/<sha16>/` — operator deliverables (append-only).
- `data/v3_spine/<sha16>/` — per-song working refs kept for the
  sound-matching layer: operator-section 6-stem WAVs, MuScriptor JSONs,
  canonical/merged MIDI, tempo/env manifests. `*.PRUNED.txt` files mark
  regenerable bulk that was removed — regenerate via the driver, don't
  mourn it.
- `data/v4/profiles/` — per-instrument sound profiles (see architecture
  doc; the search that produces them may be stochastic, the profile and
  its replay must be deterministic).
- `data/v4/rules/` — M-V4-RULES-1 artifacts (Model A `statistical_model.json`,
  Model B `sequence_model.json`, v3-shape `rules_artifact.jsonl`, audio
  descriptors, CA retention summary, replay proof).
- `data/v4/ear/` — M-V4-EAR-1 artifacts (`ear_scores.json`, exemplar
  and band-4 embedding NPZs, replay proof).
- `data/v4/generated/` — M-V4-GEN-1 outputs (per-song `merged.mid` +
  `song.wav` + manifest; `batch_full/batch_report.json` summarises the
  stall-rule iteration; `hybrid_cg_x_pd/` is the interpolation-hybrid demo).
- `docs/v4_closure_completion_report.md` — the c21 completion report,
  every deliverable indexed, gaps disclosed, certificate status recorded.

## Conventions that keep this tree clean
- Improve modules IN PLACE (git history is the version ladder); never
  create `*_v5/` sibling dirs.
- Every milestone ships a double-run byte-determinism proof before LANDS.
- Non-factor discipline: engine mechanics, disk, rate limits → sidecar
  notes, never findings.
- Disk: stay under 90%; prune regenerable WAVs first, tombstone what you
  prune; never touch corpus, deliveries, model weights, or torch-hub/
  huggingface caches.
- Fan-out clones namespace ALL milestone families as
  `<milestone>__<fork>__<clone>`.
