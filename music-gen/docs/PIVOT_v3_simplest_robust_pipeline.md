# Pivot v3 — conceptual audit: the simplest, most robust end-to-end pipeline (2026-09-02)

## Why the pivot

Two full fix iterations on the hand-rolled transcription stack (basic-pitch →
onset+GMM drums / onset-segmented pyin bass) passed their own gates and still
failed the operator's ear ("ALL OF THESE SAMPLES are still far off"). The
fourth-pass audit identified seven structural blind spots (circular gates, no
musical time, model-class ceiling, timbre-confounded verification, unreconciled
stem bleed, too-coarse drum vocabulary, hardest-input bias). The operator
decision: kill the run, delete the dead transcription code, and rebuild the
pipeline around a prebuilt state-of-the-art transcriber.

## Scope: replace the failing area only (operator correction, same day)

The pivot replaces **transcription** — the diagnosed failure — and keeps
every proven stage. Removed for good: the basic-pitch / pyin / onset+GMM
transcription lineage (`scripts/recreate_v0*`, `scripts/transcribe/`, the
rc2/rc3/rc10 transcriber families), `basic_pitch_venv` (2.1 GB), and the
superseded iteration outputs under `data/` (4.0 GB → 0.6 GB).

Restored from history after an over-broad first sweep, because they are
proven and functioning: `rc8_section_selection.py` (peak-section choice,
byte-verified), `rc7_mix_balance.py`/`rc7_v2_rerun.py` (per-stem loudness +
EQ mix matching, D4), `rc4*_gm_program_map.py`, `rc1_v2_hybrid.py` (vocal
overlay, D2), `rc9_first_class_parts.py` (htdemucs_6s driver),
`rc6*_panel_gate.py` (sanity panel), `rc5_tempo_beat_grid.py`,
`rc10_gold_set/`. Also kept throughout: corpus + provenance, separation
baselines, palette render stack, ear/rules/gen scripts, all docs.

## The new spine: MuScriptor

[MuScriptor](https://muscriptor.github.io/) (Mirelo + Kyutai, open-weighted
2026, CC-BY-NC-4.0 — fits this never-released experimental project) is a
transformer that transcribes a FULL MIX into multi-track MIDI: one track per
detected instrument, with instrument-group labels, tempo and time-signature
detection built in. Verified working in this workspace:

- installed into `workspace/learned_transcribers_venv` (pip `muscriptor`,
  torch 2.14 cpu);
- weights: `muscriptor-medium` (1.23 GB safetensors) fetched from the open
  community mirror `cocktailpeanut/muscriptor-medium` (canonical
  `MuScriptor/muscriptor-medium` is license-gated; the mirror is
  byte-identical in size; sha256 receipts in
  `workspace/models/muscriptor-medium/SHA256SUMS`);
- invocation: `muscriptor transcribe <audio> -m <local safetensors> -d cpu`
  with `--format json|midi`, `--detect-tempo`, `--instruments` whitelist,
  greedy decoding by default (deterministic).

Model-size policy: medium by default (CPU box; large is 5.5 GB and
disk/latency-prohibitive). If medium's quality is the binding constraint on a
song, that is a finding to report, not a reason to hand-roll DSP again.

## The v3 pipeline (simplest robust path, in order)

1. **Ingest** (exists, unchanged): rated corpus 4–7, sha256 provenance.
2. **Transcribe** (operator decision 2026-09-02): htdemucs_6s separation
   first — isolation is a quality layer that helps transcription — then one
   MuScriptor call PER STEM with a stem-matched `--instruments` whitelist,
   merged back into one multi-track MIDI on a shared tempo map. A full-mix
   pass is allowed only as a cross-check for separation-artifact losses.
   No hand-rolled DSP. Output: MIDI (authoritative) + JSON events + tempo
   map.
3. **Render**: fixed lookup from MuScriptor instrument groups → GM programs →
   fluidsynth (FluidR3_GM), drums on channel 10, per-track stems rendered
   separately. Deterministic. Palette upgrades (Surge/sfizz) only AFTER the
   GM render is validated by ear — timbre polish must never precede content
   correctness again.
4. **Vocals hybrid** (operator decision D2, unchanged): htdemucs vocals stem
   overlaid on the instrumental render; the transcribed voice track stays in
   the MIDI but is not synthesized.
5. **Mix match**: per-track gain set by comparing rendered-track loudness to
   the corresponding htdemucs stem loudness; master LUFS matched to the
   original. No EQ fitting unless listening demands it.
6. **Verify**: (a) operator A/B listening on a 30 s excerpt EVERY iteration —
   the only LANDS authority for audible quality; (b) objective sanity panel
   (onset/pitch agreement vs htdemucs stems, tempo agreement, per-instrument
   note-density ratios) as regression tripwires, never as success criteria;
   (c) byte-determinism ×2 over the full chain.
7. **Scale**: 5-song focus set first (Chicken Grease mandatory) → full rated
   corpus batch once ≥3 focus songs pass operator listening.
8. **Then, and only then**: rules extraction from validated MIDI → ear
   training on the rated corpus → novel generation through the same render
   stack.

## Design principles carried forward

- Prebuilt learned models over hand-rolled DSP, always. A weak model is
  replaced by a stronger model, never by threshold tuning.
- The gate hierarchy is explicit: operator ear > objective sanity panel.
  No metric may confer LANDS on audible quality.
- Separation is a quality layer FOR transcription: per-stem MuScriptor with
  stem-matched instrument whitelists, recombined; full-mix pass only as a
  cross-check. Bleed is handled by the whitelists plus reconciliation, not
  by hand-rolled classifiers.
- One tool per stage, one call per song, deterministic flags everywhere.
