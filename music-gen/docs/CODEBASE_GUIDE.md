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


## v5 REOPENING layer (c79–c90) — appended additively at c90

The 2026-09-06 operator guidance reopened RULES / EAR / GEN only (entry #20 of `docs/OPERATOR_DECISIONS.md`); everything above this
heading is unchanged and still binding. The v5 layer lives in `scripts/v5/` + `data/v5/`; it closed at c90 (entry #21). Cycle numbers
on disk are harness − 44.

### Module map (SHA-256 at c90)

| Module | SHA-256 | Role |
|---|---|---|
| `scripts/v5/generate_v5.py` | `94c8ba99eac98eee1f88d871cfc520507ddf253d3962287f50a7a368fdaaa055` | the v5 groove-first generator (drums+bass → chords on the form plan → keys/melody; F1/F2/F3/F5 flags default OFF) — additive edits only |
| `scripts/v5/interpolate_v5.py` | `177ac5c6c3f2d7ceebb2110cdb336ea05e414cfd155a962a2e2a0237caab624b` | F5 model-parameter blend of two donor-conditioned models (imported only under `--f5`) |
| `scripts/v5/repo_root.py` | `d012e5105c838355893f9a5bf7cccf00a387b7689defc230dbf83060743a2804` | marker walk-up (`promise_ledger.jsonl` + `scripts/v5/`) for scripts under data/; no `parents[N]` |
| `scripts/v5/comping_gen_v5.py` | `571cc0a4376741c888e1f455a69b8cb4ffa12680586a1135abba5cd34ba59360` | F3 comping-part builder (IOI-walk on the corpus IOI histogram) — READ-ONLY since c87 |
| `scripts/v5/velocity_v5.py` | `dd94336de4e09fcec3e34d8ec1bbe9db18a0462398e709f0e3dc3a8281b7169a` | F2 Route-1 velocity extraction from separated stems — READ-ONLY (do not edit) |
| `scripts/v5/harmony_v5.py` | `cd1ceff73b63f9205bd130c9fb2d6d07ad0164a0c0712f998dc78bed1ab53bcc` | ROOT+QUALITY template matching → functional Markov chain (n=23 with `--eligible-from` / `--tempo-overrides`) |
| `scripts/v5/groove_v5_v2.py` | `30de598f8e68b808fe3818b424ec3451331cb6312f1a63ff24eded0eebd310ae` | joint groove conditionals (kick8 / snare16\|kick8 / hat16\|kick8,snare16 / bass16\|kick8), held-out verdict |
| `scripts/v5/comping_v5.py` | `f4ca05527d34ea15486eb5e64d7df2bcae9edca70b04387d83eab2ddc6d5d6df` | guitar/piano/other comping statistics |
| `scripts/v5/form_plan_v5.py` | `0653f9a56d02a4ce93618735708bc0bbcb396483a5811cba1d396d44aa995f10` | corpus form-plan model (R1 test; fixed-template fallback) |
| `scripts/v5/bass_pitch_v5.py` | `b6887ddd35c6696883bc2bb8782586667253eab846074ce65fe39f138aa6547d` | bass interval-class model conditioned on (slot, chord change) |
| `scripts/v5/melody_vomm_v5.py` | `329b3ecfd1ba81e2cd932b4817c4c463a8ff528a50eca47b768572ba42d6e050` | melody VOMM over scale-degree\|IOI tokens |
| `scripts/v5/score_gen_batch_v5.py` | `7acfdb34a15dd0043ad17b7c42b6e68b6e9595a9afe4299f45bde229d1c9f47d` | informational ear scoring through the isolated venv (`--cycle` required) |
| `scripts/v5/deliver_v5_listening.py` | `feb9574b3f3b1155bd8efb55a44fcc7fabd977c6c9163622cf2cb30df6190208` | SHA-verified listening copies → data/v4/generated/v5_iter_NN/ |
| `scripts/v3_spine/launch_detached.py` | `999045f373f9d476aa965d05c4e218d5c3bf841c0e4a2203b0e88829cdd8ec5b` | READ-ONLY c24 detached launcher (setsid-equivalent, log file, PID) |
| `scripts/v5/reindex_hook.py` | `a63434a60cc12b83a9c704a296dd2a8468941242676c01b76d5a12cb69941ad2` | lossless reindex at landing (hook-at-birth) + idempotent catch-up |
| `scripts/v5/reindex_canonical_v5.py` | `08e94008a79ce2c05e1c370d0ccc0aa09062270bd61b93bc63b087c297b18115` | c80 index-collision fix (start/end re-pairing → `canonical_v5_reindexed/`) |
| `scripts/v5/transcribe_full_length.py` | `c1c6b2df923db13c7444ace4d2c17b3a349bfb209b08202c1b32a9503c3191c7` | full-length corpus transcription through the checkpointed stages (stage-cache; delete-after-transcribe) |
| `scripts/v5/midi_from_json_events_v5.py` | `4ea85e0bc54e22aca48bb7a7a153cf3f560d0c945168c864df493cdc936efc9b` | sibling of the c4 serializer with a velocity field |
| `scripts/v5/content_gate_v5.py` | `b28cc3ba7588919b67b888ce45595743b0aa8df2bca6d43b9fc41e4fb1f47666` | pre-registered non-music content gate (R1/R2) |
| `scripts/v5/recanonicalize_tempo_v5.py` | `c631b49873fb293fcb36f25c3cff5472bb5b5d11aad27330838a47358f634ea1` | canonical MIDI at an adopted BPM → `canonical_v5c_reindexed/` |
| `scripts/v5/runners/run_from_launch_json.py` | `9c6f464ebfac72a847ba1dbd0463b9a4df3f904081fea910efb4857c102ec246` | generic re-executor of any pinned launch/byte-det command (dry-run default) |

The per-cycle one-shot emitters / registrars (`tools/_emit_cNN_ledger_events.py`, `tools/_register_cNN_por_rows.py`) are retained in-tree
per `docs/emitter_exemption_policy.md`; they fail closed on missing artifacts and are idempotent on (milestone_id, cycle).

### Generator flag matrix (`scripts/v5/generate_v5.py`)

| Flag | Since | Meaning |
|---|---|---|
| `--iteration N --seed S --cycle C --out DIR` | c84 | seed = iteration − 1 by the F6 schedule; `--no-stall-update` for tempdir replays |
| `--form-plan data/v5/rules/form_plan_v5.json` | c85 (F1) | section form plan + literal repetition + intro/outro/breakdown/fills |
| `--f2 --velocity-mode f2 [--rms-variance-test]` | c86/c87 (F2) | bass pitch model + melody VOMM + velocity ladders; sub-flags error without `--f2` |
| `--f3 [--comping-model J]` | c88 (F3) | guitar / piano / other parts through pinned profiles where present, else GM shims; sub-flag errors without `--f3` |
| `--tempo-overrides data/v5/corpus/tempo_overrides_c86.json` | c88 (F4) | PD / Disco A adopted BPM replacing the frozen anchors |
| `--harmony-prereg J --groove-prereg J` | c88 | prereg paths pinned into `rules_sha256` |
| `--f5 --interp-a A --interp-b B --interp-t t --f5-prereg J` | c89 (F5) | ONE extra demo spec with blended groove tables + harmony chain; `--f5` requires all four + `--f2 --f3 --form-plan` |
| `--prove-replay` | c84 | second render into a fresh mkdtemp; `REPLAY_PROOF_HOLDS` per song |

Flag-off invariant: every additive edit must reproduce the previous iteration's `ab_mix.wav` SHAs with the new flag absent
(`byte_determinism_cNN.json` → `entries.iteration_0N_flag_off_replay`).

### Data layout under `data/v5/`

- `corpus/` — `corpus_manifest.json`, per-song `<sha16>/` (transcription_manifest, muscriptor_full, `canonical_v5_reindexed/` +
  sidecar, `canonical_v5c_reindexed/` for adopted tempos, stage_cache), tempo criteria + falsification records, `content_blocked.json`,
  `recanonicalization_blocked.json` (+ `stale/`), `tempo_overrides_c86.json`, figures + plot scripts co-located.
- `rules/` — harmony / groove / comping / form / velocity / bass / melody models + their pre-registrations + byte-det records + figures.
- `gen/` — `iteration_0N/` (per-song `ab_mix.wav` + manifest + replay proof + per-stem MIDI + generated_json + rollup), per-feature
  preregs (`form_prereg_c85`, `f2_prereg_c86`, `f3_prereg_c88`, `f5_prereg_c89`), `byte_determinism_cNN.json`, ear-score tables,
  `stall_counter.json` (5/12 at close).
- `ear/` — isolated-venv receipts (`env_pin_ear_venv_c82_amended.json`, freezes, fetchability ladder), `ear_gate_v5_c82.json`.
- `logs/` — launch JSONs (`gen_iter0N_cNN.launch.json` pin the exact command), pipeline logs, prune records, `validators_cNN.json`,
  `test_results_cNN.json`, `runners_decision_c90.json`.
- Listening copies go to `data/v4/generated/v5_iter_NN/` (+ `f5_interp_CG_PD_t050_c89/`); `data/v4/**` is otherwise FROZEN.

### Disciplines specific to v5

- **Prereg before output**: every feature / criterion writes its `*_prereg_cNN.json` (frozen enum, clauses, held-constant SHAs)
  BEFORE any code edit or output; tests assert the mtime gate. Verdicts are recorded from the enum, never retuned (FD-1).
- **Byte-det ×2** in fresh tempdirs per new code path (+ an independent second process for the F5 demo); flag-off regression per edit.
- **Ear venv**: `workspace/ear_venv/bin/python` (numpy 1.26.4 / tensorflow 2.21.0 / tensorflow_hub 0.16.1 / librosa 0.11.0), invoked
  as a subprocess by `scripts/v5/score_gen_batch_v5.py --renders-glob 'data/v5/gen/iteration_0N/*/ab_mix.wav' --cycle N --milestone M --table-out T`;
  scores are informational only (FD-6, c76 L119).
- **`blend_record_sha256`** (F5 manifests / rollup / stall history) = SHA-256 of the compact canonical JSON of the blend record
  (`sort_keys`, separators `,`/`:`), NOT of the on-disk `f5_blend.json` bytes (indent=2); the delivery manifest carries the file-byte SHA.
- Cycle records: `df -P` driver semantics for disk (85 % WARN / 90 % abort); one-shot emitters with `agent=worker` on every event,
  `supersedes_path` str|null, `created:` never future-dated.
