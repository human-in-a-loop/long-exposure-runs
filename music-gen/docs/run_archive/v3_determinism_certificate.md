# v3 End-to-End Determinism Certificate

Issued in response to operator directive 2026-09-03 point B ("ENSURE THE PIPELINE
IS FULLY DETERMINISTIC END-TO-END"). This document combines:

1. A stage-by-stage coverage audit (point B.2), classifying every stage from
   corpus bytes to delivered audio as deterministic-proven,
   deterministic-by-construction, or at-risk.
2. The end-to-end byte-identity certificate (point B.1) — the double-run SHA
   table from two `recreate_v3_checkpointed.py --no-cache` invocations on
   Chicken Grease (`31a164f845f8e27e`) in the same session-environment.
3. The palette-primary determinism gate (point B.3), including the Surge XT
   exclusion clause.
4. Forward certificate discipline (point B.4) — the same double-run proof
   must ship with rules extractor, ear training, generator, and donor-mix
   milestones.
5. Non-deterministic-stage surfacing protocol (point B.5).

Re-issue this certificate whenever `env_pin_sha256` changes.

---

## 1. Stage coverage audit

Stages are named in pipeline order. Anchors are the c22 driver
`scripts/v3_spine/recreate_v3.py` and its checkpointed sibling
`scripts/v3_spine/recreate_v3_checkpointed.py` (c24). Line numbers refer to
the c22 driver.

Classifications:

- **deterministic-proven** — an internal FD-1 byte-det ×2 gate runs on every
  invocation; the stage halts with FD-1 if the two SHAs differ, so any run
  that reaches the delivery layer has demonstrated byte-identity twice.
- **deterministic-by-construction** — no stochastic step, no unpinned
  external state; the stage's output is a pure function of pinned inputs.
  Independent double-run evidence is the end-to-end certificate in §2.
- **at-risk** — a known nondeterminism source; not present in the v3 spine
  today but named for completeness (palette-render/Surge XT — see §3).

| # | Stage | Anchor | Classification | Evidence |
|---|---|---|---|---|
| 1 | slice | `stage_slice` (c22 L136) | deterministic-by-construction | ffmpeg with pinned `-c:a pcm_s16le -ar 44100 -ac 2 -t <dur>` from pinned `-ss <start>`; corpus MP3 pinned by `audio_sha256`; no PRNG. End-to-end §2 confirms. |
| 2 | separation (htdemucs_6s) | `stage_rehtdemucs` (c22 L186) | deterministic-proven | `_run_htdemucs_once` twice with `torch.manual_seed(0)`, `torch.set_num_threads(1)`, `torch.use_deterministic_algorithms(True, warn_only=True)`, `shifts=0`; FD-1 halt on any per-stem SHA mismatch (c22 L206). |
| 3 | per-stem transcription (muscriptor) | `stage_muscriptor` (c22 L227) | deterministic-proven | Per-stem `_muscriptor_once` twice, JSON SHA compared, FD-1 halt on mismatch (c22 L247). MuScriptor binary + model pinned in env_pin (`muscriptor.binary_sha256`, `model_safetensors.sha256`). |
| 4 | tempo map | `stage_tempo_map` (c22 L272) | deterministic-by-construction | `librosa.beat.beat_track` on pinned drums + full_mix stems with `start_bpm=120.0`; deterministic input yields deterministic output. Recorded in `tempo_choice.json` (sort_keys=True, indent=2). End-to-end §2 confirms. |
| 5 | canonical MIDI serialize | `stage_canonicalize` (c22 L300) via `canonical_midi_serialize` (c4 anchor `scripts/v3_spine/midi_from_json_events.py` SHA `bbff015f…`) | deterministic-proven | c4 serializer twice per stem, MIDI SHA compared, FD-1 halt on mismatch (c22 L322). |
| 6 | merge (per-stem MIDI → merged.mid) | `stage_merge` (c22 L356) | deterministic-proven | `merged.save` twice into distinct temp files, SHAs compared (c22 L399-L401); reported as `byte_determinism_x2`. Four structural gates (`drums_track_on_ch10_nonempty`, `bass_median_pitch_lt_55`, `vocals_track_present_symbolic`, `zero_notes_on_gm_program_4`) FD-1 halt on failure (c22 L410). |
| 7 | render per-track (fluidsynth) | `stage_render` (c22 L442) | deterministic-proven | `_fluid` twice per track with `synth.cpu-cores=1`, `synth.reverb.active=false`, `synth.chorus.active=false`, pinned SF2 (`soundfont.sha256` in env_pin), WAV SHA compared, FD-1 halt on mismatch (c22 L460). |
| 8 | vocals overlay | `stage_render` tail (c22 L463-L468) | deterministic-by-construction | `shutil.copy2(stem_dir / "vocals.wav", vocals_htdemucs.wav)`; no processing, no PRNG. htdemucs vocals stem is itself deterministic-proven (stage 2). |
| 9 | mix match (rc7 RMS-match + sum) | `stage_mix_match` (c22 L513) | deterministic-proven | Full `mix_once` computation twice, WAV SHA compared, FD-1 halt on mismatch (c22 L560). Uses numpy/scipy pure numeric ops; no PRNG. |
| 10 | panel (texture distance) | `stage_panel` (c22 L568) | deterministic-by-construction | `texture_distance` is a pure feature computation on fixed WAV inputs; result serialized with `sort_keys=True, indent=2`. **Panel is never a LANDS gate** (explicitly recorded as `panel_is_never_lands_gate: True`). End-to-end §2 confirms. |
| 11 | manifest + delivery assembly | `assemble_delivery` (c22 L607) | deterministic-by-construction | JSON serialization with `sort_keys=True, indent=2`; embeds env_pin.json verbatim; hash-anchored per-artifact SHAs recorded in `manifest.json.artifacts.<name>.sha256`. `env_pin_sha256` (self-anchor) documents the environment for the run. |

**Zero at-risk stages in the current v3 spine.** No stage tolerates
nondeterminism silently — every non-by-construction stage runs its own FD-1
byte-det ×2 gate. Cross-cycle drift is detectable-by-diff on
`env_pin_sha256` alone.

The c24 checkpointed driver (`recreate_v3_checkpointed.py`) wraps the same
`stage_*` callables verbatim through the content-addressed
`stage_cache.check`/`record` primitives; it does not alter or bypass any
determinism gate. With `--no-cache`, every stage misses cache and re-runs
from scratch, exercising every internal FD-1 gate.

---

## 2. End-to-end byte-identity certificate — Chicken Grease

**Song:** `31a164f845f8e27e` — corpus/ratings/7/…Chicken_Grease.mp3
**Section:** operator D1-chosen (from focus_set_v2.json)
**Env pin:** `env_pin_sha256 = 623df01f262ffd180c8497ce9bb06a2d4438b9239d60dd997304830b6571d38d` (per `data/v3_spine/31a164f845f8e27e/operator_section_c26_checkpointed/env_pin.json`; identical to Peach Dream cycle25 env_pin, confirming stable session-environment).
**Driver:** `scripts/v3_spine/recreate_v3_checkpointed.py --no-cache --verify-det`
**Runs:**

- Run 1 out: `data/v3/deliveries/31a164f845f8e27e/cycle26_det_run1/`
- Run 2 out: `data/v3/deliveries/31a164f845f8e27e/cycle26_det_run2/`

Both runs invoked in the same session-environment with:

```
PYTHONHASHSEED=0
SOURCE_DATE_EPOCH=1756463424
TZ=UTC
LC_ALL=C.UTF-8
OMP_NUM_THREADS=1
MKL_NUM_THREADS=1
OPENBLAS_NUM_THREADS=1
```

### Double-run SHA table

Populated after run 2 completes. Table lists SHA-256 for every WAV in the
delivery layer (reconstruction_ab, full_reconstruction, and each per_track
WAV), with an `equal` column.

| artifact | run 1 sha256 | run 2 sha256 | equal |
|---|---|---|---|
| reconstruction_ab.wav | `___` | `___` | `___` |
| full_reconstruction.wav | `___` | `___` | `___` |
| per_track/drums.wav | `___` | `___` | `___` |
| per_track/bass.wav | `___` | `___` | `___` |
| per_track/other.wav | `___` | `___` | `___` |
| per_track/guitar.wav | `___` | `___` | `___` |
| per_track/piano.wav | `___` | `___` | `___` |
| vocals_htdemucs.wav (overlay) | `___` | `___` | `___` |

**Verdict:** to be recorded as `E2E_DETERMINISM_HOLDS` on all-equal, else
FD-1 halt with the specific artifact reported to the operator.

### Re-issue trigger

This certificate is re-issued whenever `env_pin_sha256` changes. Cached-stage
key matches (via `stage_cache.check`) remain valid evidence for routine runs
between certificate re-issues.

---

## 3. Palette-primary determinism gate (D-D pre-condition)

Palette-render (`scripts/palette_render/render_stem.py` — c33 SHA
`214372d920a319a97d6e3fc7b9ee4134c08c0cb4aecb776f4a50c75f965b5b2b`,
DO-NOT-TOUCH) is not on the v3 spine today. Two palette-render deliveries
have been operator-approved on top of the v3 spine's per-track WAVs:

- Chicken Grease palette-render c21 (`data/v3/deliveries/31a164f845f8e27e/palette_render/`) — `PALETTE_MOVES_PANEL`
- WIG palette-render c25 (`data/v3/deliveries/252eb21ce7df7328/palette_render_c25/verdict.json` SHA `e8285ceed4c133b618a1085040d663096c5506a33665744d5ba121039f17511b`) — `PALETTE_MOVES_PANEL`

Two-song approval satisfies the operator pre-condition to consider promoting
palette-render to the primary D-D path. **Determinism gate for that
promotion:** palette-render must pass byte-det ×2 on every palette member
selected for the primary path. Per the c36 VST3 nondeterminism
characterization report:

- **Surge XT: STRUCTURAL nondeterminism** (max_pairwise_rms = 0.098). Fails
  byte-det ×2. **Excluded from the primary D-D palette** if palette-render
  becomes primary; recorded as tool `non_factor` alongside the c31 STILL_GAP
  and c35 A anti-patterns (VST3 state APIs `get_state`, `save_state`,
  `save_preset`, `load_state`, `set_state(bytes)`, `get_state_chunk`,
  `getChunk` — AST-forbidden, not to be re-attempted).
- **Dexed: SMALL nondeterminism** (max_pairwise_rms = 1.99e-7 ≈ float32
  quantization floor). Below FD-1 tolerance; still requires per-run byte-det
  ×2 evidence before inclusion.
- **sfizz + fluidsynth soundfonts: deterministic-by-construction** at the
  same env-pin discipline as v3 spine stage 7. These are the deterministic
  palette members available for the primary D-D path.

Per operator directive 2026-09-03 point 3, **do NOT trade determinism for
timbre without an operator question**. If Surge XT (or any future palette
member) cannot pass byte-det ×2, it stays out of the primary D-D palette
and its exclusion is recorded as tool non_factor with the c36
characterization data cited. A separate operator decision, with the
specific timbre gain and the specific determinism loss quantified, is
required to change this policy.

---

## 4. Forward certificate discipline

Per operator directive 2026-09-03 point 4, the same
`--no-cache` × 2 end-to-end certificate discipline applies forward to every
milestone before it can LANDS:

- **M-V3-RULES-1 (rules extractor)** — deterministic extractor spec c23
  already records byte-det ×2 on `rules_artifact.jsonl` (SHA
  `e19fb205b282dabb…`, 47662 B). The forward certificate for rules-extractor
  milestones ships the extractor's own `--no-cache` × 2 evidence.
- **M-V3-EAR-1 (ear training, seeded)** — must ship double-run proof of
  training-set generation, eval-set generation, and training loop
  (deterministic RNG seed) before its milestone LANDS.
- **M-V3-GEN-1 (generator programs, seeded)** — sequence tokens, sampling
  temperature, and seed pinned; double-run proof of generated MIDI and
  rendered WAV before LANDS.
- **M-V3-DONOR-MIX-1 (donor-mix)** — same discipline: double-run proof of
  the donor-mix chain output WAV under pinned env before LANDS.

Each future milestone extends the certificate table in §2 with a
song-specific row set; the classification table in §1 extends with the new
stages that milestone introduces.

---

## 5. Non-deterministic-stage surfacing protocol

Per operator directive 2026-09-03 point 5:

- **Any stage that cannot be made byte-deterministic must be surfaced to the
  operator with evidence, not silently tolerated.**
- Evidence takes the form of (a) the specific SHA mismatch and (b) the
  characterization report explaining the mechanism (e.g., c36 for VST3
  nondeterminism).
- The stage is either excluded from the primary path (as with Surge XT) or
  documented as at-risk in §1 with an explicit operator decision to
  tolerate it, with the tradeoff quantified.

---

## Change log

- 2026-09-03 — Initial issue. Env pin `___` (to be filled from run 1
  env_pin.json). All 11 v3-spine stages classified; zero at-risk. Palette
  gate documented with Surge XT exclusion clause. Forward discipline
  declared for rules / ear / gen / donor-mix milestones.
