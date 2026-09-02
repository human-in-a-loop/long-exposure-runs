---
created: 2026-09-02T00:00:00Z
cycle: 58
run_id: run-2026-08-28T040704Z
agent: worker
milestone: M-V3-SPINE
---

# M-V3-SPINE frozen 3-verdict rubric

**Scope**: end-to-end v3 pipeline on Chicken Grease (sha16 `31a164f845f8e27e`,
chosen_section t=233.64..263.64s per `data/recreate_v2/focus_set_v2.json`).
Deliverable is the A/B excerpt + full-section reconstruction handed to the
operator, plus per-stage byte-deterministic artifacts.

## Pipeline chain (in strict order, per PIVOT_v3 §"The v3 pipeline")

1. Ingest source `.mp3`.
2. Slice audio to chosen_section (t_start..t_end from focus_set_v2.json).
3. htdemucs_6s separation on the chosen_section slice → 6 stems
   (drums, bass, guitar, piano, other, vocals).
4. MuScriptor transcribe PER STEM with instrument whitelist matched to that
   stem (per Fixed Decision 1, updated 2026-09-02). Greedy decoding on CPU.
   Vocal stem transcribed but not synthesized (Fixed Decision 4).
5. Merge per-stem MIDIs into one multi-track MIDI (shared tempo map).
6. Fluidsynth render per non-vocal track through GM program map
   (`scripts/v3_spine/gm_program_map_v3.py`), drums on MIDI channel 10.
7. Overlay htdemucs vocals stem (raw) on the summed instrumental render.
8. Per-stem loudness match to htdemucs stems (RMS + LUFS-S); sum.
9. Excerpt to 30 s A/B pair (original vs reconstruction),
   loudness-normalize both to −23 LUFS-I.
10. Sanity panel measurement (regression tripwire only, per Fixed Decision 6).
11. Emit verdict.

## Verdicts (frozen; pick exactly one)

### `V3_SPINE_CHAIN_LANDS`

ALL of:
- (a) Chain runs end-to-end with no unhandled exceptions.
- (b) Byte-determinism ×2 PASS on all deterministic anchors
  (see §"Deterministic anchors" below).
- (c) `data/v3/deliveries/31a164f845f8e27e/{original_ab.wav,
  reconstruction_ab.wav, full_reconstruction.wav, manifest.json}` present;
  all WAVs non-silent (peak > 1e-4); A/B WAVs duration 30 s ±5 ms.
- (d) Sanity panel returns 8 finite keys.
- (e) Zero MIDI parts on GM program 4 (Electric Piano 1); at least one drums
  track on MIDI channel 10; vocals part present in merged MIDI but not
  synthesized in the instrumental render.
- (f) ≥12/12 tests green in `tests/test_v3_spine.py`.
- (g) Anchor-preservation snapshot ≥20 SHAs pre==post byte-exact.
- (h) 0-ERROR `promise_check`.
- (i) **Operator listening deferred** — this verdict is at most
  `V3_SPINE_CHAIN_LANDS`; the operator's A/B listening verdict is a
  separate future event that outranks this. Verdict JSON MUST carry
  `operator_listening_status: "pending"`.

### `V3_SPINE_CHAIN_PARTIAL`

Chain runs end-to-end and A/B deliverable is emitted, but exactly one of
success bars (b)–(g) fails HONESTLY (documented, not papered over).
Verdict JSON MUST enumerate which bar failed and why.

### `V3_SPINE_CHAIN_FAILS`

Any of:
- Chain errors before A/B artifact emission.
- MuScriptor non-deterministic under greedy+CPU+seed=0 across two fresh
  runs (this is a first-class negative finding — report it, do not paper
  over per Fixed Decision 7).
- Any pipeline stage silently drops content (no per-stem stems produced,
  or zero notes across every per-stem MIDI, etc.).

## Deterministic anchors (byte-determinism ×2 must PASS on all)

- `data/v3_spine/31a164f845f8e27e/section.wav` (chosen_section audio slice)
- `data/v3_spine/31a164f845f8e27e/stems_6s/*.wav` (6 htdemucs stems)
- `data/v3_spine/31a164f845f8e27e/muscriptor/<stem>.mid` (per-stem MIDIs)
- `data/v3_spine/31a164f845f8e27e/muscriptor/<stem>.json` (canonical-JSON
  MuScriptor events)
- `data/v3_spine/31a164f845f8e27e/merged.mid` (multi-track merged MIDI)
- `data/v3_spine/31a164f845f8e27e/render/<track>.wav` (per-track fluidsynth
  stems)
- `data/v3_spine/31a164f845f8e27e/mixed_reconstruction.wav`
- `data/v3/deliveries/31a164f845f8e27e/reconstruction_ab.wav`
- `data/v3/deliveries/31a164f845f8e27e/full_reconstruction.wav`
- `data/v3_spine/31a164f845f8e27e/panel.tsv`
- `data/v3_spine/31a164f845f8e27e/verdict.json` (excluding wall-time fields)

## Three-way rubric_hash byte-equality chain

- SHA-256 of this document
- `data/v3_spine/rubric_hash.txt` content
- `data/v3_spine/31a164f845f8e27e/verdict.json.rubric_hash` field

All three must be byte-equal for a valid verdict emission (c46
mtime-hard/git-log-advisory pattern path (ii)).

## READ-ONLY anchors (pre==post byte-identical, ≥20 SHAs)

- `scripts/recreate_v2/rc4_v2_gm_program_map.py`
- `scripts/recreate_v2/rc1_v2_hybrid.py`
- `scripts/recreate_v2/rc7_mix_balance.py`
- `scripts/recreate_v2/rc7_v2_rerun.py`
- `scripts/recreate_v2/rc6_v2_panel_gate.py`
- `scripts/recreate_v2/rc8_section_selection.py`
- `scripts/recreate_v2/rc9_first_class_parts.py`
- `data/recreate_v2/focus_set_v2.json`
- `data/recreate_v2/baseline/31a164f845f8e27e/rc9_6stem/{drums,bass,guitar,piano,other,vocals}.wav` (6)
- `data/recreate_v2/baseline/31a164f845f8e27e/rc5_tempo_bpm.json`
- `workspace/models/muscriptor-medium/model.safetensors`
- `/usr/share/sounds/sf2/FluidR3_GM.sf2` (SHA `74594e8f4250680adf590507a306655a299935343583256f3b722c48a1bc1cb0`)
- `scripts/palette_render/render_stem.py` (c53 anchor `214372d9…5b2b`)
- `corpus/ratings/6/017__It2s36sL4aM__Chicken_Grease.mp3`

Total: ≥20 SHAs, all byte-identical pre/post cycle.

## Discipline invariants

- Interpreter guard `/usr/bin/python3` on every top-level script.
- Env pins: `PYTHONHASHSEED=0`, `SOURCE_DATE_EPOCH=1756463424`, `TZ=UTC`,
  `LC_ALL=C.UTF-8`, `OMP_NUM_THREADS=1`, `MKL_NUM_THREADS=1`,
  `OPENBLAS_NUM_THREADS=1`, `torch.manual_seed(0)`.
- NO PRNG (AST-grep clean in `scripts/v3_spine/`).
- Zero import of banned lineage under `scripts/v3_spine/`:
  `scripts/recreate_v0/*`, `scripts/transcribe/*`,
  `scripts/recreate_v2/rc2_*`, `rc3_*`, `rc10_drums_*`, `rc10_bass_*`,
  `rc10_guitar_piano/*`, `rc10_other_vocals/*`.
- `data/v3_spine/rubric_hash.txt` mtime < any script mtime under
  `scripts/v3_spine/` (mtime hard; git-log advisory per c46 path (ii)).

## Non-factor firewall

Tool-install friction, disk pressure, MuScriptor CLI quirks, and rate
limits are `non_factor` sidecar notes at
`data/v3_spine/31a164f845f8e27e/non_factor_notes.jsonl`, NOT findings
about the music.
