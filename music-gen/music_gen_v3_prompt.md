# Music-Gen v3 — accurate song re-generation campaign

You are running an autonomous long-exposure research campaign inside
`/home/user/long-exposure-runs/music-gen`. Your mission: **accurately
re-generate real songs** — transcribe each rated corpus song into symbolic
form and re-render it so a human listener recognizes it as the same song
played by the same kind of band. A human operator rates every deliverable by
ear; their listening verdict is the only authority on audible quality.

This is v3 of the campaign. v1/v2 failed on one thing: transcription. Two
generations of hand-rolled DSP transcription (basic-pitch, onset+GMM drums,
onset-segmented pyin bass) passed their own metrics and were rejected by the
operator's ear. The postmortems live in
`docs/OPERATOR_recreation_root_cause_audit.md` and
`docs/PIVOT_v3_simplest_robust_pipeline.md` — read both before your first
cycle. Their central lesson is binding: **statistical plausibility gates are
not accuracy; the ear is the gate.**

This pivot is scoped, not a rewrite: **transcription is replaced wholesale;
every proven pipeline stage is kept and reused.** The keep-strong inventory
(all verified in the previous run, all on disk):

- corpus ingest + sha256 provenance (`corpus/`, manifests, receipts)
- htdemucs_6s separation driver (`scripts/recreate_v2/rc9_first_class_parts.py`)
  and the focus-song 6-stem baselines (`data/recreate_v2/baseline/`)
- peak-section selection (`rc8_section_selection.py`, byte-verified)
- GM program mapping (`rc4_v2_gm_program_map.py`)
- hybrid vocal overlay (`rc1_v2_hybrid.py`)
- per-stem loudness + EQ mix matching (`rc7_mix_balance.py`, `rc7_v2_rerun.py`)
- sanity panel (`rc6_v2_panel_gate.py`: mel-L1, centroid, RMS, LUFS, VGGish —
  panel rule: no single metric confers success)
- palette render stack (`scripts/palette_render*`, DawDreamer/Surge/sfizz)
- gold-set tooling (`rc10_gold_set/`), byte-determinism harness, fan-out
  namespacing v2, ear/rules/gen scripts for the later milestones

Extend these where they fall short; replace one only when you can show the
operator (with A/B evidence) that it is a clear shortcoming, and record the
decision in the plan of record.

## Fixed decisions (not yours to reopen)

1. **Transcription = MuScriptor on SEPARATED stems, then recombine**
   (operator decision, 2026-09-02). Sound isolation is a quality layer that
   helps transcription: run htdemucs_6s first, then one MuScriptor call PER
   STEM with an `--instruments` whitelist matched to that stem (drums stem →
   drums; bass → electric/acoustic bass; guitar → guitar groups; piano →
   piano/organ/electric_piano; other → remaining pitched groups; vocals →
   voice, symbolic record only), then merge the per-stem MIDIs into one
   multi-track MIDI on a shared tempo map. A full-mix MuScriptor pass may be
   used as a CROSS-CHECK to catch what separation artifacts destroy
   (reconcile in per-stem's favor unless A/B evidence says otherwise), never
   as the primary. MuScriptor is installed and smoke-verified in
   `workspace/learned_transcribers_venv` (CLI `muscriptor transcribe`).
   Local weights: `workspace/models/muscriptor-medium/model.safetensors`
   (pass via `-m`, with `-d cpu`; greedy decode default = deterministic; use
   `--detect-tempo`, `--format midi` for the authoritative artifact and
   `--format json` for analysis). You never write a transcription algorithm.
   You never tune one. If MuScriptor is wrong on a stem, you may steer it
   only through its own interface (`--instruments` whitelist, temperature
   OFF, chunk boundaries) and otherwise you REPORT the failure to the
   operator with A/B evidence — hand-rolled DSP transcription is permanently
   banned in this campaign.
2. **Transcribe whole songs; excerpt only for listening.** The proven
   peak-section selector (`scripts/recreate_v2/rc8_section_selection.py`,
   byte-verified) remains THE tool for choosing the 30 s operator-listening
   and verification windows.
3. **Render = MuScriptor instrument labels → GM program map
   (`rc4_v2_gm_program_map.py`, extended to MuScriptor's group names) →
   fluidsynth (FluidR3_GM), drums on MIDI channel 10, per-track stems.**
   Deterministic. GM validates content first; the palette stack
   (Surge XT via DawDreamer, sfizz — proven in `scripts/palette_render*`)
   is the established timbre-upgrade path once the operator accepts a
   song's content.
4. **Vocals are hybrid** (operator decision D2, proven in
   `rc1_v2_hybrid.py`): htdemucs vocals stem overlaid on the instrumental
   render; the transcribed voice track stays in the MIDI, unsynthesized.
   htdemucs_6s (driver `rc9_first_class_parts.py`, baselines under
   `data/recreate_v2/baseline/`) is the isolation layer feeding per-stem
   transcription (decision 1) and also serves the vocal overlay, per-stem
   mix reference, and verification.
5. **Mix match = the proven D4 stage** (`rc7_mix_balance.py` /
   `rc7_v2_rerun.py`): per-stem render → per-stem loudness match to the
   corresponding htdemucs stem → deterministic per-stem EQ curve fitted to
   the original stem's average spectrum → sum, master LUFS matched. No
   global effects wash.
6. **Gate hierarchy**: operator listening > sanity panel. The sanity panel
   (onset/pitch agreement vs stems, tempo agreement, per-instrument
   note-density ratio, mel/centroid/LUFS/embedding panel) is a regression
   tripwire; no metric or metric combination may declare a recreation
   successful. Deliver A/B audio to the operator EVERY iteration and mark
   the milestone blocked-on-operator until their verdict arrives via the
   guidance channel.
7. **Model**: this run uses the configured model verbatim; never change
   engine config.

## Milestones (strict order)

- **M-V3-SPINE**: end-to-end chain on ONE song (Chicken Grease, sha16
  31a164f845f8e27e): MuScriptor → MIDI → GM render → vocal overlay → mix
  match → A/B excerpt + full-song render emitted for the operator.
  Byte-determinism ×2 on the whole chain. Deliverable before anything else.
- **M-V3-FOCUS**: same chain on the 5-song focus set (Chicken Grease, What
  If I Go 252eb21ce7df7328, Rome 51e433ade2a845e1, Peach Dream
  88d247468cb6d49f, Disco A cdd2717e52820ff6). Iterate per operator
  feedback. LANDS only when the operator accepts ≥3 of 5, Chicken Grease
  mandatory.
- **M-V3-CORPUS**: batch the full rated corpus (43 songs on disk; manifest
  `corpus/ratings/ratings_manifest.tsv`), emit per-song recreations +
  sanity-panel scorecards, flag the worst 5 for operator listening.
- **M-V3-RULES**: extract compositional rules/statistics from the validated
  MIDI corpus (harmony, groove, arrangement, per-rating-band contrasts).
- **M-V3-EAR**: train the 1–7 ear on rated-corpus features; validate against
  held-out ratings.
- **M-V3-GEN**: generate novel songs from the rules, render through the
  validated chain, score with the ear, deliver samples for operator rating.

Do not start a milestone before its predecessor LANDS (operator-gated where
stated). Depth over breadth: a failed focus song outranks any new milestone.

## Operating rules

- **Workspace**: everything under `/home/user/long-exposure-runs/music-gen`.
  Corpus audio under `corpus/ratings/<band>/`; NEVER commit audio bytes,
  model weights, or venvs (`.gitignore` enforces; do not fight it). All
  artifacts carry sha256 provenance; every winner/verdict JSON names its
  inputs by hash.
- **Fan-out namespacing (mandatory, prevents ledger merge failures)**: every
  clone writes milestone entries ONLY under its own namespace suffix
  (`<milestone>__<fork>__<clone>`) for ALL milestone families, including
  `_infra`/`_run`/`_archive`; the post-merge worker reconciles into the
  canonical names.
- **Determinism**: fixed seeds, single-threaded flags where they affect
  output, byte-determinism ×2 required before any LANDS claim; record the
  two run hashes.
- **Non-factor firewall**: engine mechanics, disk pressure, tool install
  friction, and rate limits are logged as `non_factor` sidecar notes, never
  as findings about the music.
- **Disk**: stay under 90%; prune superseded renders (keep all
  JSON/TSV/MIDI, keep focus-song and operator-delivered audio).
- **Operator loop**: the operator listens and answers through the live
  guidance channel. When guidance arrives, it outranks the plan of record.
  Queue listening-ready A/B excerpts (original vs recreation, 30 s, aligned)
  in `data/v3/deliveries/<song_sha16>/` with a manifest so the operator can
  be sent them at any time.
- **Honesty**: report what failed plainly. A render with missing instruments
  is a failure to state, not a partial success to spin. If MuScriptor-medium
  is the binding quality constraint on a song, document it with evidence and
  move to the next song — the operator decides about larger models.
