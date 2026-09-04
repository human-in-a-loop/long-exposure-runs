---
created: 2026-09-04T04:00:00Z
cycle: 18
run_id: run-2026-08-28T040704Z
agent: worker
milestone: M-V4-SHOWCASE-1
---

# CG A/B bass-gain semantics clarification (c18)

## Purpose

Close c17 auditor MODERATE #1 (narrative-vs-artifact drift on bass gain).
This note **only clarifies** the meaning of the on-disk value; it does not
modify any on-disk anchor. The c17 report itself is READ-ONLY per Fixed
Decision 1 + invariant (d) (on-disk-vs-report divergence disclosure).

## The drift

The c17 report (informal summary passed forward in session compaction)
described the CG bass RMS-normalize step as *"attenuation"* with a "gain
0.093" figure. Both are inconsistent with the artifact that actually landed
on disk.

## The artifact of record

`data/v4/deliveries/31a164f845f8e27e/cg_ab_mix.manifest.json`

```json
"provenance": {
  "bass": {
    "rms_normalize_gain": 2.688385,
    ...
  }
}
```

`2.688385` is greater than `1.0`. Multiplying a sample by a factor greater
than `1.0` is **amplification**, not attenuation. The bass is scaled *up*
toward the reference level, not down.

## The formula

`scripts/sound_match/deliver_cg_ab_v4.py` (this cycle's SHA
`3c45465284e2f78a…`) lines 244–250:

```python
if ren_rms > 1e-9:
    gain = ref_rms / ren_rms
    # Cap gain to reasonable range to avoid runaway on empty renders.
    if gain > 4.0: gain = 4.0
    if gain < 0.05: gain = 0.05
else:
    gain = 1.0
```

The gain is the ratio `ref_rms / ren_rms` clipped to `[0.05, 4.0]`, where:

- `ref_rms` is the RMS of the reference bass stem
  `data/v3/deliveries/31a164f845f8e27e/cert_run1/stems_6s/bass.wav`
  (SHA `1bad8719…`) — the htdemucs-separated bass signal from the operator
  section.
- `ren_rms` is the RMS of the freshly rendered bass_v2 sf2 replay
  (mono → upmix to stereo, before scaling).

The direction of the ratio is `reference / render`. When the render is
quieter than the reference, the ratio exceeds `1.0` and the scale
amplifies the bass toward the reference. When the render is louder, the
ratio falls below `1.0` and the scale attenuates.

## Why this render came out quiet

The `bass_v2` profile that landed at c4 picks FluidR3_GM bank 0 program 33
(Electric Bass Finger) with `gain=0.5`, `reverb_send=0.3`, `post=EQ_only`,
`sample_rate=44100`. The profile's own `gain=0.5` intentionally holds the
sf2 output well below unity so the mix-time RMS-match owns the level, and
the reference bass stem is loud (a solo bass sits high in the operator
section). The ratio ~2.69 falls comfortably inside the `[0.05, 4.0]` cap.

## Test-anchored semantics

`tests/test_deliver_cg_ab_v4_full_render.py::test_04_bass_gain_amplification_semantics`
regresses the on-disk value at `2.688385` and asserts `gain > 1.0` with a
docstring that names amplification. Any future report that describes this
as attenuation will lose the argument against a green test. This is how the
c17 narrative-vs-artifact class stops recurring.

## What is not changed

- `cg_ab_mix.wav` sha `6e13e007…f9484b` — READ-ONLY anchor, unchanged.
- `cg_ab_mix.manifest.json` sha `f9f1c9ed…944c27` — READ-ONLY anchor,
  unchanged.
- `cg_ab_mix.replay_proof.json` sha `fcd8e687…13818f` — READ-ONLY anchor,
  unchanged.
- The c17 report is READ-ONLY per FD-1 + invariant (d); this note
  supplements it, does not rewrite it.

Operator ear on the mix remains the only LANDS authority per Fixed
Decision 6.
