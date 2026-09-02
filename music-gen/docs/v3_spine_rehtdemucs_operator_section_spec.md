# v3 Spine Rehtdemucs Operator-Section Specification (cycle 5)

**Purpose.** Cycle 4 delivered an A/B on t=0..30 s of Chicken Grease
because the c49 baseline htdemucs stems cover only that window. The
operator's D1 auto-picker (frozen in `data/recreate_v2/focus_set_v2.json`)
selected **t=233.63918367346938..263.63918367346935 s** as the peak+exposed
section. This cycle produces an operator-section A/B by running htdemucs_6s
fresh on that 30 s slice.

## Input

- Source MP3: `corpus/ratings/6/017__It2s36sL4aM__Chicken_Grease.mp3`
- Slice bounds: `t_start=233.63918367346938`, `t_end=263.63918367346935`.
- Slice command: `ffmpeg -ss 233.63918367346938 -i <mp3> -t 30.0 -c:a pcm_s16le -ar 44100 -ac 2 <out.wav>`

## Model + weights

- `htdemucs_6s` via `demucs.pretrained.get_model("htdemucs_6s")` under
  `/usr/bin/python3` (verified c5-preflight: `sources=['drums','bass',
  'other','vocals','guitar','piano']`).
- Model weights fetched from HuggingFace Hub cache (cache warmed pre-c5;
  no fresh egress this cycle).

## Output

Per-run tempdir → 6 stem WAVs at 44.1 kHz stereo copied to a
per-run-fresh `tempfile.mkdtemp()` directory. Runs execute serially;
outputs compared by SHA-256 for byte-determinism ×2.

Canonical output paths (winners of ×2):
`data/v3_spine/31a164f845f8e27e/operator_section/rc9_6stem/<stem>.wav`
for `stem ∈ {bass,drums,guitar,other,piano,vocals}`.

## Determinism gate

Set:
- `PYTHONHASHSEED=0`
- `SOURCE_DATE_EPOCH=1756463424`
- `TZ=UTC`, `LC_ALL=C.UTF-8`
- `OMP_NUM_THREADS=1`, `MKL_NUM_THREADS=1`, `OPENBLAS_NUM_THREADS=1`
- `torch.manual_seed(0)`, `torch.use_deterministic_algorithms(True)` when
  supported by the model path (fall back silently if not).

**STOP condition.** If any of the 6 stems fails SHA-256 equality across
the two runs, halt Track B and emit an
`M-V3-SPINE-1/rehtdemucs-nondeterministic-falsified` ledger event with
the falsifying tuple.

## Pinned SHAs

12 SHAs (6 stems × 2 runs) recorded to
`data/v3_spine/31a164f845f8e27e/operator_section/htdemucs_determinism.json`.

## Pre-registration invariant

This document's mtime MUST precede every mtime under
`scripts/v3_spine/rehtdemucs_operator_section*`. Doc SHA-256 pinned to
`data/v3_spine/rehtdemucs_operator_section_spec_hash.txt` before code lands.
