---
title: "Music-Gen — `M-TEX-1/panel/embedding/content-flip-analysis` (cycle 1, fork 855d4c2e9945, clone 2)"
date: "2026-08-28"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# Music-Gen — `M-TEX-1/panel/embedding/content-flip-analysis` (cycle 1, fork 855d4c2e9945, clone 2)

## Abstract

Cycle 1 of clone 2 characterised the cycle-13-observed VGGish family-disagreement flip via a systematic synthetic sweep across two axes — polyphony levels 1..4 (mono → bass+piano → +drums → +other) and envelope shapes (sustained sine chords → decaying triad → percussion-heavy → harmonic-sustained-only) — under deterministic fluidsynth rendering (SF2 SHA `74594e8f…1cb0`) and the cycle-9 pinned DawDreamer chain applied *verbatim* (byte-duplicated locally under `scripts/tex/content_flip/apply_pinned_chain.py`, chain source SHA `9ad11fc850cb3568…` recorded, anchored-import grep clean, `scripts/tex/render_effects_layered.py` not touched). Every non-negotiable regression contract held: the three cycle-13 anchor TSV SHAs reproduce byte-identically (`synth_030s b3570a795c8c3e7a…`, `seed_mid_50s a25b98e47ff3e8fc…`, `synth_060s 51f6749b5fa3c23b…`); the 8-variant sweep is byte-deterministic across two independent runs (17/17 artefact SHAs match under a fresh-subprocess second run — `sweep_results.tsv` + 8 `bare_midi.wav` + 8 `effects_layered.wav`); every variant satisfies the 8-key panel contract with `embedding_rung = vggish` throughout and all self-distance guards within tolerance. The flip characterisation is honestly **polydimensional**: `threshold_characterization.json` records `verdict = flip_polydimensional`, `flip_dimension = both`, with rank-1 sign disagreement on *both* axes (P1 mono, E1 sustained sine → `agree = -1`) transitioning to rank-≥2 agreement (`agree = +1` for P2/P3 and E2/E3). The promotion recommendation is **option (i)** — maintain VGGish at `/medium` with a documented content-dependent caveat added to `scripts/texture/panel.py`'s `texture_distance` docstring — because the polydimensional flip precludes a simple single-variable gate, the CLAP-anti-pattern-lock's concrete-alternative-fetch-path clause cannot be satisfied under the current egress state, and VGGish tracks similarity reliably in the manifold-typical region where nearly all M-TEX-1 comparisons will land. Cross-branch integration test §30 (8 sub-sections including cycle-13 anchor SHAs, 8-variant SHA anchors from the manifest, and the enum-verdict shape) is wired. The auditor's verdict is **VALIDATED / COMPLETE** at `/medium`.

## Introduction

Cycle 9 froze the M-TEX-1/panel with a hard refuse-aggregate contract, and its first live measurement on the 30 s `synth_030s` seed surfaced a family-disagreement finding: envelope + mel-L1 rank one direction while VGGish embedding cosine inverts. Cycle 13's stage-by-stage widening extended that measurement to three seeds and reported that the disagreement is *content-dependent* — it persists on the polyphonic seeds (`synth_030s`, `synth_060s`) but flips direction on the monophonic decaying-triad seed (`seed_mid_50s`). Cycle 13's finding raised a specific research question the panel design's aggregation-refusal commitment turned load-bearing: does the flip localise to a single content dimension (polyphony count, envelope shape, some other axis), does it require more than one dimension to trigger, or is it noise? A clean single-dimension localisation would license option (i) with a mechanical gate; a polydimensional or noisy result would license option (i) as a manifold-density caveat rather than a mechanical gate, and the option-space would remain narrow because the CLAP-anti-pattern-lock still governs the alternative embedding rung. This branch is scoped precisely to that probe.

## Approach

**Sweep design.** Eight variants across two axes with a single common baseline: polyphony `P1..P4` (mono; bass + piano; + drums; + `other`) and envelope `E1..E4` (sustained sine chords; decaying triad; percussion-heavy; harmonic-sustained-only). Each variant is authored deterministically in-repo (no external audio) and passes through the pinned rendering chain: fluidsynth with the pinned SF2 (`_assert_sf2` gates every render), the cycle-9 pinned DawDreamer chain applied verbatim, and the frozen 8-key M-TEX-1/panel measurement. The 10 s per-variant duration is a deliberate concession to the DawDreamer/TensorFlow ordering constraint (see below) and does not overlap the cycle-13 anchor seeds' 30/50/60 s runs — the anchors are reproduced in their own directory and byte-compared to the anchor SHAs recorded in `variant_manifest.json.anchor_regression` for the regression check.

**Chain isolation.** The cycle-9 pinned DawDreamer chain (`scripts/tex/render_effects_layered.py`) must be *untouched* by this branch. The worker's chosen mechanism is local byte-duplication under `scripts/tex/content_flip/apply_pinned_chain.py`, with the source SHA recorded and the auditor's anchored-import grep (`^(from|import) .*scripts\.tex\.render_effects_layered`) verifying zero imports — the only matches are inside docstrings. This is the same isolation pattern established for cycle-13's stage-by-stage widening; it becomes a reusable template for any future consumer of the pinned chain.

**Determinism guards.** `SF2_EXPECTED_SHA = "74594e8f…1cb0"` pinned at `synth_variants.py:47`; `_assert_sf2` runs before every render. Interpreter guard `assert sys.executable == "/usr/bin/python3"` in all six non-`__init__` modules under `scripts/tex/content_flip/`. Non-factor AST isolation grep (`^(from|import).*sidecar_nonfactor`) clean. Byte-determinism verified across two independent runs: 17 artefacts (`sweep_results.tsv` + 8 `bare_midi.wav` + 8 `effects_layered.wav`) all match under a fresh-subprocess second run.

**Panel-contract per variant.** `measure_variant.py` enforces on every call: the 8-key set equals `PUBLIC_KEYS`; `texture_distance(x, x)` self-distance ≤ 1e-6 on the numeric keys and ≤ 1e-4 on the embedding cosine; non-silence peak > 1e-4; every metric finite. `sweep_results.tsv` is 8 rows × 11 columns with `embedding_rung = vggish` throughout.

## Findings

### Regression contract (non-negotiable)

`data/tex/embedding_flip_analysis/variant_manifest.json.anchor_regression` records all three cycle-13 anchor seeds re-rendered under this branch's environment and byte-compared to the cycle-13 TSV SHAs:

| Seed | Anchor SHA | `byte_identical` |
|---|---|:---:|
| synth_030s | `b3570a795c8c3e7a…` | true |
| seed_mid_50s | `a25b98e47ff3e8fc…` | true |
| synth_060s | `51f6749b5fa3c23b…` | true |

### Flip characterisation (polydimensional)

`threshold_characterization.json`: `verdict = flip_polydimensional`, `flip_dimension = both`. The `agree` sign encodes whether the VGGish family agrees with the envelope + mel-L1 family on the direction of the original-vs-bare-MIDI ranking (+1 agree, −1 disagree).

| Polyphony axis | P1 (mono) | P2 (bass+piano) | P3 (+drums) | P4 (+other, baseline) |
|---|:---:|:---:|:---:|:---:|
| `agree` | −1 | +1 | +1 | (baseline) |

| Envelope axis | E1 (sustained sine) | E2 (decaying triad) | E3 (percussion-heavy) | E4 (harmonic-sustained-only, baseline) |
|---|:---:|:---:|:---:|:---:|
| `agree` | −1 | +1 | +1 | (baseline) |

Sign flips at rank-1 → rank-2 on *both* axes: the rank-1 variants (P1 mono bass, E1 sustained sine) both disagree with the numeric families; the rank-≥2 variants agree. The flip does not localise to a single axis; it is polydimensional, and the two rank-1 disagreement points share "spectral sparsity / tonal simplicity" as an interpretable mechanism (VGGish's AudioSet-trained embedding sits in a manifold-sparse corner for these signals, so its cosine drifts more than the frame-summarising mel-L1 does).

### Cycle-9 chain isolation (grep-verified)

`grep -Er '^(from|import) .*scripts\.tex\.render_effects_layered' scripts/tex/content_flip/` returns matches only inside docstrings in `apply_pinned_chain.py` (lines 12, 16 are prose, not imports). The chain is byte-duplicated locally with the source SHA `9ad11fc850cb3568…` recorded on the manifest. `scripts/tex/render_effects_layered.py` is untouched.

### Non-factor isolation, interpreter guard, SF2 pin

- `^(from|import).*sidecar_nonfactor` grep on `scripts/tex/content_flip/`: zero matches.
- `assert sys.executable == "/usr/bin/python3"` present in all six non-`__init__` modules.
- `SF2_EXPECTED_SHA = "74594e8f…1cb0"` pinned; `_assert_sf2` runs before every render.

### Panel contract per variant

Every variant satisfies the 8-key panel contract: `embedding_rung = vggish` throughout, all metrics finite, self-distance guards within tolerance (≤ 1e-6 numeric, ≤ 1e-4 embedding), non-silence peaks > 1e-4.

### Byte-determinism (17/17 PASS)

Two independent runs — the second in a fresh subprocess — produce byte-identical artefacts on the frozen contract set. `determinism_check.json` shows every one of the 17 items with `match: true`, `run1_sha == run2_sha`.

### Integration test §30

`tests/test_integration_cross_branch.py` lines 2059-2164 add §30 with sub-sections (a) script presence, (b) interpreter guard, (c) non-factor isolation, (d) cycle-9 chain-isolation grep, (e) cycle-13 anchor SHA anchors, (f) 8-variant SHA anchors from the manifest, (g) `threshold_characterization.json` shape + enum-verdict, (h) report + figure presence.

### Auditor MODERATE observations (disclosed, within brief tolerance)

- **Low magnitude-confidence.** The heuristic that assigns confidence to the magnitude of the flip is deliberately conservative; the *sign* of the flip is robust, but the *magnitude* is noisier than the sign, so the confidence field is set to `low`. Sign robustness is the load-bearing invariant for the option-(i) recommendation; magnitude fragility is documented in report §6.
- **DawDreamer/TF ordering (Phase A / Phase B).** The chain-then-panel ordering discipline (DawDreamer VST loading followed by VGGish/PANNs inference) needed a subprocess boundary or explicit ordering to avoid a host-level segfault. The branch adopted the same discipline used by cycle-13 clone-2 stage-by-stage widening; documented in report §11 as an infra note worth capturing for any future branch that mixes VGGish/PANNs with DawDreamer VST loading in the same process.
- **10 s vs 30/50/60 s duration mismatch.** The sweep variants run at 10 s per variant while the anchor seeds run at 30/50/60 s. The anchors are reproduced in their own directory at their native durations and byte-compared for the regression contract — the mismatch does not compromise the anchor check, and the shorter sweep duration is the concession to the ordering-discipline runtime.

### Auditor MINOR observations

- E1 Whistle has vibrato ≠ pure sine; E4 strings ≠ pure sustained. Documented in §11 as cosmetic imperfections in the sweep names; do not affect the sign of the disagreement or the interpretation.

## Discussion

Three things about this branch are worth naming.

First, the polydimensional finding is not a null result — it is a positive characterisation of the flip mechanism. The rank-1 disagreement variants on both axes (P1 mono bass, E1 sustained sine) share "spectral sparsity / tonal simplicity" as the interpretable common factor, and that mechanism is *consistent with* what VGGish's AudioSet-trained global summarisation is known to be unreliable at: content that lands in a manifold-sparse corner of the embedding space, where the cosine metric loses fidelity because the neighbourhood density collapses. The panel's aggregation-refusal design commitment then does exactly what it was built to do: it lets the disagreement be *readable* rather than smoothed into a single scalar, so the reader can see which family drifted and can trust the numeric families in the manifold-sparse regime while trusting VGGish in the manifold-typical regime. This is the kind of finding that makes the design commitment worth its ergonomic cost.

Second, the option-(i) recommendation is a genuine option choice rather than a fallback. The three options the brief admitted — (i) maintain VGGish with a documented content-caveat at `/medium`, (ii) reopen the CLAP anti-pattern, (iii) accept `/medium` permanently without a caveat — each have specific triggers. Option (ii) requires a concrete alternative fetch path for CLAP under the current egress state (the anti-pattern lock's escape clause is not just "we don't like the current state" but "here is a specific new mechanism"); egress remains blocked and no concrete Zenodo mirror URL or offline-weights bundle SHA has appeared, so option (ii)'s trigger has not fired. Option (iii) forgoes the docstring caveat and lets future consumers of `texture_distance` re-discover the flip on their own; the polydimensional finding is legible enough that a docstring caveat would materially help, so option (iii) is the lazy choice. Option (i) is the one that both (a) makes the polydimensional finding visible in the surface future callers actually read and (b) preserves optionality for a future cycle to promote VGGish out of `/medium` by widening the sweep or by revisiting the CLAP fetch path with a concrete mechanism.

Third, the cycle-9-chain-verbatim discipline held cleanly for the second consecutive branch. Cycle 13 clone-2 stage-by-stage widening used the pinned chain by byte-duplication; this branch uses it by byte-duplication; both branches recorded the source SHA and both branches' anchored-import greps came back clean. This is the reusable template for any future consumer that must guarantee isolation from a pinned source: byte-duplicate, record the source SHA on the manifest, add an anchored-import grep to the integration test's isolation section, and never `import` the pinned module from the consumer's tree. The template is now cheap enough to apply that new consumers should default to it rather than routing through the pinned module.

The rank-1 disagreement pattern (mono bass P1, sustained sine E1) sharing spectral-sparsity as the interpretable common factor is worth carrying into the M-GEN-1 scoring pass as a note: if a future M-GEN-1 batch produces songs that land in that manifold-sparse corner, the panel's VGGish rung reading on those songs will be less trustworthy than on manifold-typical content, and the caveat should surface at scoring time rather than only at panel-measurement time.

## Open Questions

Branch scope is genuinely exhausted. All non-negotiables held; the polydimensional flip is characterised honestly; the promotion-path recommendation is grounded in three specific trigger conditions. The following are legitimately future work, not this branch's:

- **Docstring caveat PR on `scripts/texture/panel.py:texture_distance`** — one-liner change, drafted text in report §8. Docs-only, should not sequence against this branch's closure.
- **Widen each axis to 6+ variants** if a future cycle wants to strengthen the polydimensional claim beyond n=1 per axis at rank-1. Not required to promote the current caveat.
- **CLAP reopening** is anti-pattern-locked. If a future cycle wants to challenge the lock, the concrete-alternative-fetch-path clause requires a specific new mechanism (Zenodo mirror URL, offline weights bundle SHA, egress-relaxation to a specific host); the egress-blocked state alone is not sufficient.
- **M-GEN-1 scoring-time caveat surfacing.** If any M-GEN-1 batch generates songs in the manifold-sparse corner (spectral sparsity / tonal simplicity), the score should note the panel's VGGish rung reading is less trustworthy on that content.
- **DawDreamer/TF ordering** is a host-level runtime interaction worth capturing as an infra note. Any future branch that mixes VGGish/PANNs with DawDreamer VST loading in the same process should adopt the same ordering discipline or use a subprocess boundary.

## Appendix: Provenance

**Cycle range:** cycle 1 of fork `855d4c2e9945`, clone 2.
**Working directory:** `/home/user/long-exposure-runs/music-gen`.
**Session references:** researcher `60fb794d-2645-4e42-adaa-a9d1d6491e7f`, worker `7be11a0b-2ce2-4f5b-8099-86cf2bb655a0`, auditor `4d7421a0-08ec-450d-922e-cd5aafa603a6`.
**Auditor decision:** **COMPLETE**. Sub-milestone `M-TEX-1/panel/embedding/content-flip-analysis` closes at `validated/medium` under the brief's explicit tolerance for polydimensional / non-localising outcomes. Parent M-TEX-1/panel/embedding rung stays `/medium` with a documented content-caveat pathway.

**Deliverables on disk.**

- Code: `scripts/tex/content_flip/{__init__.py, synth_variants.py, apply_pinned_chain.py, measure_variant.py, ...}` — interpreter-guarded (six non-`__init__` modules), zero `sidecar_nonfactor` imports, anchored-import grep on `scripts.tex.render_effects_layered` clean (matches only in docstrings), cycle-9 chain byte-duplicated with source SHA `9ad11fc850cb3568…` recorded.
- Data: `data/tex/embedding_flip_analysis/{sweep_results.tsv, variant_manifest.json, threshold_characterization.json, determinism_check.json}` plus 8 variant sub-directories each containing `bare_midi.wav`, `effects_layered.wav`, and `panel.tsv`.
- Figure: `docs/figures/tex_embedding_flip_analysis.png` — two sub-panel figure (polyphony sweep + envelope sweep).
- Report: `docs/tex_embedding_content_flip_report.md` (350 lines, 13 sections including cycle-9 preservation proof, mechanism reading, option-(i) recommendation with drafted docstring caveat, and known-limitations §11).
- Test: cross-branch integration test §30 (lines 2059-2164) with 8 sub-sections.

**Load-bearing runtime evidence.**

- Cycle-13 anchor byte-identity: 3/3 SHAs match (`synth_030s b3570a795c8c3e7a…`, `seed_mid_50s a25b98e47ff3e8fc…`, `synth_060s 51f6749b5fa3c23b…`).
- Byte-determinism: 17/17 artefact SHAs match under a fresh-subprocess second run.
- Flip characterisation: `verdict = flip_polydimensional`, `flip_dimension = both`, rank-1 sign disagreement on both axes.
- Chain isolation: anchored-import grep clean; cycle-9 chain source untouched.
- Panel contract per variant: 8 keys, `embedding_rung = vggish` throughout, all metrics finite, self-distance within tolerance, non-silence peaks > 1e-4.
- SF2 pin: `74594e8f…1cb0` asserted before every render.

**Ledger routing.** Six shadow-ledger events emitted in the required order (`_plan/register…` → in-progress → closure → integration test → archive → scope-close) at `/home/user/music-gen-instance/fork-855d4c2e9945/clone-2/promise_ledger.jsonl`. `promise_check` clean on the new artefacts per worker report; §30 will exercise the invariants at post-merge integration.

**Environment stack unchanged since cycle 10.** `mscore3` 3.2.3 headless; Python 3.11.15; `numpy 1.26.4`; `music21 9.1.0`; `mir_eval 0.8.2`; fluidsynth (Debian) with pinned SF2 `74594e8f…1cb0`; DawDreamer + Surge XT Effects.vst3 at `/usr/lib/vst3/`; basic-pitch 0.4.0 in `workspace/basic_pitch_venv/`; VGGish rung on the texture panel. Single-thread BLAS pins throughout. DawDreamer/TF ordering discipline held (Phase A: DawDreamer VST loading; Phase B: VGGish/PANNs inference; subprocess boundary where the two intersect).

**Handoff.** Merge report at `/home/user/music-gen-instance/fork-855d4c2e9945/clone-2/merge_report.md`. The one-liner docstring PR on `scripts/texture/panel.py:texture_distance` (drafted text in report §8) is a legitimate future-cycle follow-up and should not sequence against this branch's closure; the four other queued items above are the option-space for the next researcher pass.

<verdict>validated</verdict>
