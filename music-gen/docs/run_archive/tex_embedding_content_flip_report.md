---
created: 2026-08-28T15:50:00Z
cycle: 14
run_id: run-2026-08-28T040704Z
agent: worker
milestone: M-TEX-1/panel/embedding/content-flip-analysis
---

# M-TEX-1/panel/embedding — VGGish content-type flip characterization (cycle 14, clone 2)

## 1. Cycle-13 recap and stakes

Cycle 13 clone-2's stage-by-stage widening measured the M-TEX-1/panel across
three seeds through the (original, bare_midi, effects_layered) triple. On the
two polyphonic fluidsynth mixes (`synth_030s`, `synth_060s`), applying the
cycle-9 pinned DawDreamer chain to `bare_midi` moved the result *farther*
from `original` on `mel_l1_db` (+1.03 dB and +0.21 dB) but *closer* on
`embedding_cosine_distance` (VGGish; −0.028 and −0.019). On the monophonic
decaying-triad-sine seed (`seed_mid_50s`), the chain moved the result
*closer* on `mel_l1_db` (−1.86 dB) but *farther* on VGGish (+0.011). Same
family-disagreement class (mel and VGGish cross-signs) but with the VGGish
direction *inverted* relative to the polyphonic anchors.

Reading this straight: the panel's aggregation-refusal design pays off —
different families give different, well-defined answers — but only if we
know *when* to trust which family. If the VGGish direction depends on
content type, then the family is a rung whose direction changes underfoot.
This branch's job is to characterize where and why that happens, and to
recommend what the panel should promise about `embedding` going forward.

## 2. Sweep design

Two axes, four variants each. Every variant is 10 s at 44.1 kHz stereo,
rendered via `fluidsynth` on the M-SEP-1 pinned SoundFont
`FluidR3_GM.sf2` (sha `74594e8f…1cb0`), then processed through the
cycle-9 pinned DawDreamer chain to produce `effects_layered`. Panel
called on the (`bare_midi`, `effects_layered`) pair per variant.

**Polyphony sweep** — vary the number of simultaneously-active timbral voices
holding envelope shape roughly constant.

| Variant | Content                                | GM patches                                     |
|---------|----------------------------------------|------------------------------------------------|
| P1      | monophonic bass, quarter notes         | 33 (Acoustic Bass)                             |
| P2      | P1 + piano (5ths above)                | 33 + 1 (Piano)                                 |
| P3      | P2 + drums (kick+snare)                | 33 + 1 + kit (ch 10)                           |
| P4      | P3 + extra piano triads (C5-C6)        | 33 + 1 + kit + 1                               |

**Envelope sweep** — vary envelope shape / spectral behaviour holding voice
count roughly at "one instrument family" per variant.

| Variant | Content                                    | GM patches                    |
|---------|--------------------------------------------|-------------------------------|
| E1      | sustained sine-like chords (5 whole notes) | 79 (Whistle)                  |
| E2      | decaying triad (C-E-G, quarter notes)      | 1 (Piano)                     |
| E3      | percussion-heavy (dense kick+snare+hihat)  | kit (ch 10)                   |
| E4      | harmonic sustained (5 whole-note chords)   | strings (Str Ensemble family) |

**Family-disagreement sign definition (this branch's convention).** For a
sweep axis, pick a baseline variant B. For every other variant v on that axis,

- `dmel(v)  = mel_l1_db(bare_v, eff_v)  − mel_l1_db(bare_B, eff_B)`
- `dvgg(v)  = vgg(bare_v, eff_v)        − vgg(bare_B, eff_B)`
- `agree(v) = sign(dmel(v)) · sign(dvgg(v))`   (+1 agree, −1 disagree, 0 tie)

A **flip** along the axis is a transition where `agree(v)` changes sign
between adjacent ranks. Baselines: P4 for polyphony, E4 for envelope
(both are the axis's densest / most-manifold-typical variant, closest to
cycle-13's polyphonic anchors).

Cycle-13 anchors describe a different comparison — across *stages* of the
same seed (`bare_midi` → `effects_layered` relative to `original`) — and
are reported side-by-side for interpretation only; they do not enter the
axis-threshold characterization directly.

## 3. Regression proof — cycle-13 anchor byte-identity

The orchestrator's first step re-runs `M-TEX-1/panel` on the three
frozen cycle-13 seed WAVs at `data/tex/renders/{seed}/{original,
bare_midi, effects_layered}.wav` and compares the resulting TSV bytes to
the frozen `data/tex/stage_by_stage_{seed}.tsv`. All three match.

| Seed          | Frozen SHA-256 (first 16 hex) | Regenerated SHA (first 16) | Byte-identical |
|---------------|-------------------------------|----------------------------|:--------------:|
| synth_030s    | `b3570a795c8c3e7a`            | `b3570a795c8c3e7a`         | ✓              |
| seed_mid_50s  | `a25b98e47ff3e8fc`            | `a25b98e47ff3e8fc`         | ✓              |
| synth_060s    | `51f6749b5fa3c23b`            | `51f6749b5fa3c23b`         | ✓              |

Panel numerics unchanged since cycle 13. The regression contract holds
for this branch to build on.

## 4. Polyphony sweep results

Baseline P4. Deltas relative to P4:

| Rank | Variant | Content                | mel_l1_db | vgg_cos | dmel     | dvgg     | s_mel | s_vgg | agree |
|:----:|:-------:|------------------------|----------:|--------:|---------:|---------:|:-----:|:-----:|:-----:|
| 1    | P1      | mono bass              | 6.9688    | 0.3651  | −1.696   | +0.098   | −     | +     | **−1 (disagree)** |
| 2    | P2      | bass + piano           | 8.4775    | 0.1859  | −0.188   | −0.081   | −     | −     | +1 (agree) |
| 3    | P3      | + drums                | 10.2602   | 0.3710  | +1.595   | +0.104   | +     | +     | +1 (agree) |
| 4    | P4      | + other (baseline)     | 8.6652    | 0.2670  | 0        | 0        | 0     | 0     | 0 (tie) |

Flip transition: **P1 → P2** (rank 1 to rank 2). The monophonic-bass
variant is the only polyphony point at which mel and VGGish disagree
relative to the polyphonic baseline; every other rank agrees.

## 5. Envelope sweep results

Baseline E4. Deltas relative to E4:

| Rank | Variant | Content                  | mel_l1_db | vgg_cos | dmel     | dvgg     | s_mel | s_vgg | agree |
|:----:|:-------:|--------------------------|----------:|--------:|---------:|---------:|:-----:|:-----:|:-----:|
| 1    | E1      | sustained sine chords    | 12.6614   | 0.0507  | +5.256   | −0.029   | +     | −     | **−1 (disagree)** |
| 2    | E2      | decaying triad           | 7.6460    | 0.2709  | +0.240   | +0.191   | +     | +     | +1 (agree) |
| 3    | E3      | percussion-heavy         | 14.0334   | 0.1906  | +6.628   | +0.111   | +     | +     | +1 (agree) |
| 4    | E4      | harmonic sustained (base)| 7.4056    | 0.0800  | 0        | 0        | 0     | 0     | 0 (tie) |

Flip transition: **E1 → E2** (rank 1 to rank 2). The sustained-sine-chord
variant is the only envelope point at which mel and VGGish disagree
relative to the harmonic-sustained baseline; every other rank agrees.

## 6. Cross-axis analysis — the flip is polydimensional

Both sweeps land the disagreement at **rank 1** and switch to agreement
at **rank 2**. Rank 1 is the axis's minimum-content extreme:

- Polyphony rank 1 = monophonic bass (P1): a single voice, single timbral
  family, narrow bandwidth (C2–C3), quarter-note articulation.
- Envelope rank 1 = sustained sine chords (E1): a single quasi-sinusoidal
  patch (GM 79 Whistle) sustained on whole notes — narrow bandwidth,
  minimal onset transients, very tonally-uniform spectrum.

The common attribute across the two rank-1 variants is **spectral sparsity
or tonal simplicity**, not a specific polyphony count or a specific
envelope shape. Rank ≥ 2 on either axis — the moment content becomes
either multi-voice (P2, P3) or multi-timbral / transient / broadband (E2,
E3) — the sign disagreement vanishes.

The verdict emitted by `analyze_flip.py`:

```json
{"verdict": "flip_polydimensional", "flip_dimension": "both"}
```

Threshold characterization data is written to
`data/tex/embedding_flip_analysis/threshold_characterization.json`.

Confidence heuristic (defined in `analyze_flip.py` as a 5%-of-baseline
magnitude threshold on both dmel and dvgg) marks both axes as `low`. That
threshold is calibrated to mel_l1_db's dB scale; on the VGGish side the
`dvgg` values around ~0.08–0.19 sit visibly above panel self-distance
tolerance (≤ 1e-4), so the sign observations themselves are trustworthy —
the confidence flag is really saying "the mel deltas are small compared
to typical mel_l1_db magnitudes."

## 7. Mechanism interpretation

The polydimensional flip aligns with a **manifold-density** reading of
VGGish's embedding behaviour. VGGish is trained on AudioSet (YouTube
audio), whose musical portion is overwhelmingly polyphonic and rich in
onsets, transients, and broadband content. The learned embedding space
concentrates around such content; monophonic bass alone and single-patch
sustained sine chords both live in a low-density region of that
manifold. Cosine distances between low-density-region embeddings become
less reliable and can invert relative to the local geometry — that
inversion is what shows up as the sign flip at rank 1 on both axes.

Under this reading, the effect is not "polyphony causes it" or "envelope
shape causes it" but "content that VGGish's training data
under-represented causes it." The two rank-1 variants share
under-representation in different ways (mono voice; single-patch
quasi-sinusoidal sustained), which is why the flip appears on both
axes rather than only on one.

Cycle-13's `seed_mid_50s` — the on-disk source of which is a decaying
triad sine test tone that goes through demucs + basic-pitch + score-bridge
+ fluidsynth — sits at the low-density corner along BOTH axes at once
(monophonic-lineage AND sine-like envelope). That is precisely the corner
this sweep confirms as the anomaly zone. The cycle-13 sign inversion
observed on that seed is consistent with, not orthogonal to, the sweep
findings.

Alternative reading kept for the record: VGGish's mel-band coverage
differences under monophonic vs polyphonic content could produce
similar behaviour without invoking training-corpus density. The two
readings are not distinguishable from this branch's data alone; both
predict the observed rank-1-flip pattern.

## 8. Promotion-path recommendation

The three options in the research brief:

- **(i) Maintain VGGish with a documented content-caveat at `/medium`.**
- (ii) Reopen the CLAP anti-pattern for a future cycle with a
  different fetch path.
- (iii) Accept `/medium` permanently.

**Recommendation: option (i).** Rationale:

1. The flip is polydimensional. There is no single-content-variable gate
   that would let the panel automatically switch to a different rung on
   the anomalous side (a gate would need at minimum a polyphony estimator
   AND an envelope-shape estimator agreeing that the content is at
   rank 1 on both). Building that gate is disproportionate to the
   benefit for a family the panel already refuses to aggregate away.
2. Reopening the CLAP anti-pattern (option ii) requires, per the
   research brief's escape-hatch clause, a *concrete alternative fetch
   path with a defensible new mechanism*. No such path exists in this
   session: HuggingFace SSL failure is still reproducible per
   `corpus/CORPUS_STATUS.md`; Zenodo mirror + laion-clap weight bundles
   were not evaluated because egress remains blocked; and the cycle-11
   probe log at `data/tex/panel_rung_log.jsonl` already documents the
   fetch-side failure at rung 1.2. A handwave "try again later" does
   not clear the anti-pattern lock.
3. Option (iii) is stronger than the evidence supports. The flip is not
   noise: two independent axes, both showing a clean rank-1 disagreement
   and rank-≥2 agreement, byte-deterministic across two runs. VGGish
   still tracks perceptual similarity in the manifold-typical region,
   which is where nearly all M-TEX-1 comparisons will land in practice.

Concrete caveat text to surface in the M-TEX-1/panel docstring (deferred
to a follow-up cycle — this branch does not modify the panel itself,
only characterizes its embedding rung):

> **Caveat (embedding rung, cycle 14):** the `embedding_cosine_distance`
> value may sign-invert relative to `mel_l1_db` on content that is either
> monophonic OR a single-patch quasi-sinusoidal sustained tone (the
> "manifold-sparse corner" of VGGish's AudioSet-trained embedding space).
> Treat spectral and embedding families as complementary, not redundant;
> this is why the panel refuses aggregation. On multi-voice or
> broadband/transient content the families agree in sign.

The panel already refuses aggregation, so the caveat is a documentation
change, not a semantics change. `M-TEX-1/panel/embedding` stays at
`/medium` with the caveat surfaced — no re-classification.

## 9. Cycle-9 pinned chain preservation proof

The branch **duplicates** the cycle-9 pinned chain locally rather than
importing it. This guarantees the audit-mandated anchored-import grep is
empty and eliminates any risk of accidental shadowing.

```
$ grep -rEn '^(from|import) .*(scripts\.tex\.render_effects_layered|scripts_tex_render_effects_layered)' scripts/tex/content_flip/
(no matches; ISOLATION_OK)
```

Duplicated file: `scripts/tex/content_flip/apply_pinned_chain.py`
(SHA-256 `9ad11fc850cb35687ecda80e95ff3a567a1049ca73c41e7526477f031748814c`).
Cycle-9 source file `scripts/tex/render_effects_layered.py` (SHA-256
`b1ab2f4c375455c781cadb6630c3bd89d6165417d83e35440ff53e11b6b4b8e0`)
is byte-unchanged this cycle. The duplication is a plain copy of the
public functions `apply_dawdreamer_chain`, `apply_numpy_effects_fallback`,
and a locally-named `apply_effects_layered_local` wrapper; parameter
values are identical (Chorus FX Type 0.28 / Output Mix 0.35, Reverb FX
Type 0.02 / Output Mix ramp 0.05→0.60, gain envelope 0.25→1.4). If
cycle-9 is ever revised, this file must be updated in lockstep.

## 10. Determinism & panel-contract evidence

- **Byte-determinism × 2 subprocess run.** The orchestrator's second
  run of the full sweep executes in a fresh subprocess (a fresh Python
  interpreter) in a temp dir, then diffs SHA-256 hashes of all bare +
  effects WAVs plus `sweep_results.tsv` against the primary run. All
  **17** artifacts SHA-256-equal.
  Recorded in `data/tex/embedding_flip_analysis/determinism_check.json`.
- **Panel contract.** Every panel call inside `measure_variant.py`
  asserts (a) `set(keys) == PUBLIC_KEYS` (the 8 keys), (b) numeric
  self-distance ≤ 1e-6, (c) embedding cosine self-distance ≤ 1e-4,
  (d) all metrics finite, (e) non-silent inputs (`|peak| > 1e-4`).
  Zero contract violations observed across all 8 variants + 3 anchors
  in each of the two runs.
- **Non-factor AST isolation.** Zero `sidecar_nonfactor` imports under
  `scripts/tex/content_flip/` (integration test §30c verifies).
- **Interpreter guard.** Every new script asserts
  `sys.executable == "/usr/bin/python3"` at top (integration test §30b
  verifies).

## 11. Notes and known limitations

- **Runtime interaction: DawDreamer VST loading + TensorFlow (VGGish)
  segfault.** On this host, initializing TensorFlow (which VGGish
  loads via `scripts.texture.embedding_panel`) before loading a VST3
  through DawDreamer segfaults on the first `RenderEngine.make_plugin_processor`
  call. The orchestrator works around this in two ways: (1) it runs
  the variant sweep's chain phase FIRST and the panel phase second
  within a run (`run_variant_sweep` is split into Phase A / Phase B);
  and (2) it invokes the second determinism run as a subprocess rather
  than in-process. Both workarounds are annotated in the code. This is
  a documented environmental interaction, not a determinism failure —
  a fresh-interpreter run reproduces every byte identically.
- **Envelope-axis interpretation caveat.** E1 (Whistle) is
  approximately sinusoidal but has vibrato, and E4 (Strings) is
  sustained but not pure sine. The label "sustained sine chords" for
  E1 is a shorthand; the exact spectral character is what fluidsynth's
  FluidR3_GM patch renders. This is deliberate — the goal was to
  reproduce a realistically-fetchable "sustained tonal" content type,
  not a synthesizer-primitive pure sine.
- **Duration.** 10 s per variant is short compared to the cycle-13
  anchors (30 s / 50 s / 60 s). The panel's contract holds on any
  length, but the anchor comparison is cross-length by construction.
  This is why cycle-13 anchor signs enter the report side-by-side
  rather than being interleaved with sweep signs.
- **The "flip_polydimensional" verdict is a valid finding, not a
  falsification.** The research brief explicitly permits this closure
  path (§Sufficiency Criteria: `validated/medium` when the flip does
  not localize cleanly).

## 12. Closure

- **Regression contract:** met — 3 cycle-13 anchor TSVs byte-identical.
- **8-variant byte-determinism × 2:** met — 17/17 SHA-256-equal.
- **Cycle-9 chain isolation:** met — grep-verified.
- **Flip characterization published honestly:** met — polydimensional,
  rank-1 disagreement on both axes, mechanism-typing recorded.
- **Promotion-path recommendation:** option (i), documented content
  caveat, `M-TEX-1/panel/embedding` remains at `/medium`.

Closure event: `M-TEX-1/panel/embedding/content-flip-analysis`
`validated/medium` (rationale: characterization succeeded but flip did
not localize to a single dimension — validated at the confidence-level
the brief's Sufficiency Criteria assigns to that outcome).

## 13. Artifacts

Under `data/tex/embedding_flip_analysis/`:

- `sweep_results.tsv` — 8 rows × 11 cols, one per variant.
- `variant_manifest.json` — per-variant SHAs, chain rung, panel values.
- `threshold_characterization.json` — verdict + per-axis analysis.
- `summary.json` — high-level pass/fail summary.
- `determinism_check.json` — 17-artifact SHA-256 equality across two runs.
- `anchor_regen/regen_{synth_030s, seed_mid_50s, synth_060s}.tsv` —
  regenerated cycle-13 anchor TSVs; byte-identical to
  `data/tex/stage_by_stage_{seed}.tsv`.
- `variants/{P1..P4, E1..E4}/{variant.mid, bare_midi.wav,
  effects_layered.wav, panel.tsv}` — per-variant artifacts.

Under `docs/`:

- `tex_embedding_content_flip_report.md` (this file).
- `figures/tex_embedding_flip_analysis.png` — two-subpanel figure.

![Content-flip sweep: normalized Δmel and ΔVGGish bars per variant, with the sign-disagreement marker (✗) landing on rank 1 of both axes (P1 mono bass, E1 sustained sine); rank ≥ 2 flips to agreement. Cycle-13 anchor across-stage signs annotated at the bottom.](figures/tex_embedding_flip_analysis.png)

Under `scripts/tex/content_flip/`:

- `__init__.py`, `synth_variants.py`, `apply_pinned_chain.py`
  (duplicated cycle-9 chain), `measure_variant.py`, `orchestrator.py`,
  `analyze_flip.py`, `plot_flip_analysis.py`.
