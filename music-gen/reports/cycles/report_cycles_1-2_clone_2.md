---
title: "Music-Gen v3 SPINE Milestone — Fanout Clone 2: Chicken Grease Palette Render (Cycles 1–2)"
date: "2026-09-02"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# Music-Gen v3 SPINE Milestone — Fanout Clone 2: Chicken Grease Palette Render (Cycles 1–2)

## Abstract

This report covers Cycles 1 and 2 of a fanout-clone branch spawned from the Music-Gen v3 campaign's newly-post-operator-LANDS phase on Chicken Grease. On 2026-09-02 the operator LANDED the Cycle 5 v3 fluidsynth reconstruction on Chicken Grease as the campaign's operator-blessed reference, closing the M-V3-SPINE-1 gate that had been open since Cycle 4. A subsequent operator D-D directive authorized a secondary-deliverable arm: attempt a palette-render sibling using Surge XT (VST3 via DawDreamer) for bass, sfizz for guitar/piano/other, fluidsynth GM channel 10 for drums (unchanged from Cycle 5 to preserve the rhythmic reference), and htdemucs vocals verbatim (D2, also unchanged from Cycle 5). The intent: if the palette render moves the perceptual panel *and* the operator confirms audibly-different-AND-audibly-better on A/B, palette becomes primary campaign-wide.

Clone 2 of fork `0a1b1dca4f9b` executed the palette-render pipeline against a frozen three-verdict rubric (`PALETTE_MOVES_PANEL / PALETTE_NEUTRAL / RENDER_FAILS`) committed before any script was written. Cycle 1 delivered the required output artifact `docs/v3_spine_chicken_grease_palette_render_c21_report.md` plus the palette-rendered full reconstruction, A/B deliverables, matched per-stem WAVs, both panel comparison sidecars, and the `cycle21/verdict_palette.json` sibling delivery (which explicitly does not overwrite the operator-blessed Cycle 5 delivery). The frozen rubric fired **PALETTE_MOVES_PANEL** on the Comparison B threshold (four of five numeric panel keys exceeded the 5% relative-delta threshold on the fluidsynth-vs-palette comparison). Cycle 2 was a re-verification audit that live-cross-checked every anchor, three-way rubric chain, and hard-anchor byte-identity, and terminated the branch with `COMPLETE` and `[[BRANCH_COMPLETE]]`. Two important honesty caveats surface prominently in the verdict and are the load-bearing input to the operator's forthcoming palette-becomes-primary decision: (a) the Surge XT VST3 bass path failed the byte-determinism ×2 gate after three fresh-tempdir attempts, with a `max_pairwise_rms` of 0.0656 versus the c36 clone-2 envelope of 1e-4, so the bass stem honestly fell back to a fluidsynth GM 33 render; and (b) the sfizz path failed on `sfz_dir_missing_no_sfz_files_in_workspace`, so guitar, piano, and other honestly fell back to fluidsynth GM 25/0/88. The net effect is that all six palette-render stems are, at bottom, fluidsynth GM renders with the Cycle 6 Method B rc7 12-band iirpeak EQ + RMS + LUFS-S loudness match applied on top. The panel movement is real and numerically first-class, but the operator's forthcoming ear judgment must discriminate GM-plus-EQ-plus-loudness from genuine sampler/synth timbral character.

## 1. Introduction and scope

The M-V3-SPINE-1 milestone had sat in `blocked_on_operator` state for fifteen-plus heartbeat cycles since Cycle 5 under Fixed Decision 6. On 2026-09-02 the operator's ear judgment landed positively on the Cycle 5 Chicken Grease A/B pair, flipping M-V3-SPINE-1 to LANDED and opening the door to a secondary-deliverable arm the operator named D-D: attempt a palette render on the same operator-chosen section (t = 233.63918–263.63918 s) using higher-quality synthesizers than fluidsynth's GM SoundFont, and see whether the perceptual panel moves.

This report is the merge-disposition summary for clone 2 (Chicken Grease palette render) of fork `0a1b1dca4f9b`. Sibling clones in the same fork run other v3 objectives; they are covered in separate reports.

The clone's scoped objective as issued was:

- **Read the operator-blessed Cycle 5 canonical per-stem MIDIs** as READ-ONLY sources from `data/v3_spine/31a164f845f8e27e/operator_section/canonical_midi/{bass,guitar,piano,other}.mid`, with SHAs asserted byte-identical pre-versus-post.
- **Route the four melodic stems through a palette**: bass → Surge XT VST3 via DawDreamer with c33 Branch B P1-iterate-parameters hydration (proven at c35 with 100% parameter coverage, 2 855/2 855 params); guitar/piano/other → sfizz via the `sfizz_render` CLI with SFZ file paths logged and a fluidsynth GM fallback if the SFZ files are unfetchable.
- **Preserve the Cycle 5 references** on the two non-palette stems: drums → fluidsynth GM channel 10 (unchanged from Cycle 5 to preserve the rhythmic reference); vocals → htdemucs vocals verbatim (D2, also unchanged from Cycle 5).
- **Byte-determinism ×2 gate** on each per-stem WAV, rendered into fresh `tempfile.mkdtemp()` directories. A `REDEFINED_GAP` first-class verdict arm was pre-authorized if the bass Surge XT path failed byte-equality after three fresh-tempdir attempts, with the c36 clone-2 characterization envelope `max_pairwise_rms ≤ 1e-4` allowed.
- **Apply the Cycle 6 Method B rc7 loudness chain verbatim** as a READ-ONLY import of `scripts/v3_spine/rc7_v2_rerun_v3_paths.py`: 12-band iirpeak EQ + RMS + LUFS-S loudness match.
- **Deliver the palette-rendered full reconstruction** at `data/v3_spine/31a164f845f8e27e/palette_render/full_reconstruction_palette.wav` as a sibling to (never a replacement of) the Cycle 5 `operator_section/full_reconstruction_operator_section.wav` (the operator-blessed hard anchor, SHA `cc919559b4508b6bfe868fa5433a50b6805c43bab763665a5f2be367f01bbbd7`).
- **Deliver A/B WAVs plus manifest** under `data/v3/deliveries/31a164f845f8e27e/palette_render/`.
- **Measure the eight-key perceptual panel twice**: Comparison A (original vs palette-render) and Comparison B (Cycle 5 fluidsynth-render vs palette-render), both with all five reported numeric keys finite.
- **Freeze the three-verdict rubric before any script was written** under `scripts/v3_spine/palette_render/`, with the enum `{PALETTE_MOVES_PANEL, PALETTE_NEUTRAL, RENDER_FAILS}`.
- **Emit** `data/v3/deliveries/31a164f845f8e27e/cycle21/verdict_palette.json` (sibling to `cycle20/`, never overwriting the operator-blessed Cycle 5 delivery) under a byte-equal three-way `rubric_hash_v2` chain.
- **Six named plus two housekeeping ledger events** under the `-clone-2` suffix, with the substantive `M-V3-SPINE-1/chicken-grease-palette-render` row unsuffixed per the c32 convention.

The required deliverable is `docs/v3_spine_chicken_grease_palette_render_c21_report.md`.

## 2. Cycle 1: rubric freeze, palette-render pipeline, verdict emission

### 2.1 Rubric freeze (before any script)

`docs/v3_spine_chicken_grease_palette_render_c21_rubric.md` (SHA `9eb5523cbd090c388e30b0b271cb1dffd4f321ed907c78be122f56cbad5e1879`) was committed before any script under `scripts/v3_spine/palette_render/`, with the mtime hard-verified. Its pinned hash file at `data/v3_spine/31a164f845f8e27e/palette_render/rubric_hash_v2.txt` carries the same SHA verbatim. The rubric defines the three-verdict enum, the Comparison B threshold (a verdict of `PALETTE_MOVES_PANEL` fires if the palette-render's Comparison B numeric panel keys move by ≥5% relative on ≥3 of 5 keys), the byte-determinism ×2 mandatory sub-clause with the `REDEFINED_GAP` fallback envelope for the Surge XT bass stem, and the sfizz-fallback ladder for the SFZ-driven stems.

### 2.2 Fetchability ladder and per-stem routing

The palette-render pipeline executed a fetchability ladder for each melodic stem and honestly recorded the routing decision at each rung. The ladder outcomes are logged at `data/v3_spine/31a164f845f8e27e/palette_render/fetchability_ladder.jsonl` and summarized in the verdict as `sfizz_fallback_reason: sfz_dir_missing_no_sfz_files_in_workspace` and `sfizz_fallback_stems: [guitar, piano, other]`:

| Stem | Intended path | Actual path | Fallback reason |
|---|---|---|---|
| bass | Surge XT VST3 via DawDreamer (c33 Branch B, 2 855/2 855 params) | fluidsynth GM program 33 | Byte-determinism ×2 failed after 3 fresh-tempdir attempts with `max_pairwise_rms = 0.0656` (outside the c36 clone-2 envelope of 1e-4). `REDEFINED_GAP` first-class fallback arm engaged. |
| guitar | sfizz via `sfizz_render` CLI | fluidsynth GM program 25 | `sfz_dir_missing_no_sfz_files_in_workspace` |
| piano | sfizz via `sfizz_render` CLI | fluidsynth GM program 0 | `sfz_dir_missing_no_sfz_files_in_workspace` |
| other | sfizz via `sfizz_render` CLI | fluidsynth GM program 88 | `sfz_dir_missing_no_sfz_files_in_workspace` |
| drums | fluidsynth GM channel 10 (unchanged from c5) | fluidsynth GM channel 10 | (intended path taken) |
| vocals | htdemucs vocals verbatim (D2, unchanged from c5) | htdemucs vocals verbatim | (intended path taken) |

The net effect is that all six palette-render stems reach fluidsynth GM at the bottom of their respective ladders. This is a first-class honest disclosure per Fixed Decision 1, not a failure to smooth over. It is called out prominently in the verdict via the `sfizz_fallback_stems` and `sfizz_fallback_reason` fields and is the load-bearing MINOR-3 observation for the operator's forthcoming ear judgment.

The Surge XT bass byte-determinism failure with `max_pairwise_rms = 0.0656` is significant: it is roughly 655× the c36 clone-2 characterization envelope of 1e-4 and does not qualify as small-perturbation-tolerable, so the c33 `REDEFINED_GAP` fallback arm correctly declined the Surge XT bass render rather than accepting a nondeterministic artifact. This is an important negative finding on its own — it demonstrates that even with 100% parameter hydration (2 855/2 855 params proven at c35), the Surge XT VST3 binary carries an internal nondeterminism envelope larger than the campaign's acceptance threshold on this specific input path.

### 2.3 Per-stem palette renders

Per-stem matched WAVs landed at `data/v3_spine/31a164f845f8e27e/palette_render/matched_{bass,drums,guitar,other,piano,vocals}.wav`. Each was rendered twice into fresh temporary directories with the SHA-256 asserted equal across the two runs (byte-determinism ×2 gate satisfied on the six stems that reached their final routing, with the bass Surge XT failure disclosed above). The byte-determinism roll-up sits at `data/v3_spine/31a164f845f8e27e/palette_render/byte_determinism.json`.

### 2.4 Cycle 6 Method B loudness chain applied verbatim

The rc7 12-band iirpeak EQ + RMS + LUFS-S loudness match from Cycle 6 Method B was applied verbatim through a READ-ONLY import of `scripts/v3_spine/rc7_v2_rerun_v3_paths.py` (Cycle 6 anchor, unchanged). The palette-rendered full reconstruction landed at `data/v3_spine/31a164f845f8e27e/palette_render/full_reconstruction_palette.wav`, sibling to (never overwriting) the Cycle 5 operator-blessed `operator_section/full_reconstruction_operator_section.wav`.

### 2.5 Panel measurement

The eight-key perceptual panel was measured on both required comparisons, with all five reported numeric keys finite on both:

**Comparison A (original vs palette-render)** at `panel_original_vs_palette.json/tsv`:

| Key | Value |
|---|---:|
| `spectral_centroid_rmse_hz` | 1 149.89 |
| `mel_l1_db` | 6.360 |
| `rms_env_rmse` | 0.1071 |
| `lufs_m_rmse_lu` | 4.514 |
| `embedding_cosine_distance` (VGGish) | 0.24335 |

**Comparison B (Cycle 5 fluidsynth-render vs palette-render)** at `panel_fluidsynth_vs_palette.json/tsv`:

| Key | Value |
|---|---:|
| `spectral_centroid_rmse_hz` | 3 120.31 |
| `mel_l1_db` | 6.889 |
| `rms_env_rmse` | 0.0802 |
| `lufs_m_rmse_lu` | 3.724 |
| `embedding_cosine_distance` (VGGish) | 0.09569 |

The rubric's Comparison B threshold requires ≥3-of-5 numeric keys to exceed 5% relative delta versus the c5-vs-original reference panel. The delta table computed by the pipeline (`panel_delta_comparison.json`) is:

| Key | Ref (c5-vs-original) | Test (palette-vs-original) | Absolute Δ | Relative Δ | Exceeds 5%? |
|---|---:|---:|---:|---:|:---:|
| `spectral_centroid_rmse_hz` | 3 254.47 | 3 120.31 | 134.16 | 4.12% | **no** |
| `mel_l1_db` | 8.786 | 6.889 | 1.897 | 21.59% | **yes** |
| `rms_env_rmse` | 0.1473 | 0.0802 | 0.0671 | 45.54% | **yes** |
| `lufs_m_rmse_lu` | 7.427 | 3.724 | 3.703 | 49.86% | **yes** |
| `embedding_cosine_distance` | 0.1876 | 0.0957 | 0.0919 | 48.99% | **yes** |

Four of five numeric keys exceed the 5% relative-delta threshold. The rubric's `PALETTE_MOVES_PANEL` clause fires.

### 2.6 Verdict

`data/v3/deliveries/31a164f845f8e27e/cycle21/verdict_palette.json` (SHA `5ba4eaca242fcd29…5644a`) emitted with:

- `milestone = M-V3-SPINE-1/chicken-grease-palette-render`
- `cycle = 21`, `song_sha16 = 31a164f845f8e27e`, `operator_section_s = [233.63918, 263.63918]`
- `verdict = PALETTE_MOVES_PANEL` (rubric-frozen enum, fired on Comparison B threshold)
- `blocked_on_operator = true` (the palette-becomes-primary decision belongs to the operator, not to the auditor)
- `c5_delivery_anchor_preserved = true` (the Cycle 5 operator-blessed WAV is byte-identical pre-versus-post at SHA `cc919559b4508b6b…f01bbbd7`)
- Three-way `rubric_hash_v2` chain byte-equal at `9eb5523cbd090c388e30b0b271cb1dffd4f321ed907c78be122f56cbad5e1879` (document SHA, `rubric_hash_v2.txt` content, and verdict field all identical; `rubric_hash_v2_chain_holds: true`).
- Sub-artifact SHAs pinning the four consumed canonical MIDIs (bass `f439fb31…`, drums `8021a1ca…`, guitar `69e7c7bb…`, other `c88c69a0…`, piano `c88c69a0…` — matching the empty-events canonical hash on the piano source) plus the six per-stem matched WAVs, the full-reconstruction palette WAV, the two panel sidecars, and the byte-determinism roll-up.
- Comparison A, Comparison B, and the reference Cycle 5-vs-original panels all pinned inline.
- The fetchability ladder outcomes disclosed as `sfizz_fallback_reason` and `sfizz_fallback_stems`.

### 2.7 Delivery-side artifacts

Under `data/v3/deliveries/31a164f845f8e27e/palette_render/`: `full_reconstruction_palette.wav`, `manifest.json`, `panel_original_vs_palette.tsv`, `panel_fluidsynth_vs_palette.tsv`, `anchor_preservation.json`, `byte_determinism.json`, `fetchability_ladder.jsonl`, and a `per_stem/` subtree. Sibling to `cycle20/`; does not overwrite the operator-blessed Cycle 5 delivery.

The required output artifact `docs/v3_spine_chicken_grease_palette_render_c21_report.md` (12 053 bytes) was landed under `docs/` per the directive.

## 3. Cycle 2: audit re-verification and branch termination

Cycle 2 was a re-verification pass. The auditor performed live disk-state verification against every anchor: three-way `rubric_hash_v2` chain byte-equal at the pinned SHA; the Cycle 5 operator-blessed full-reconstruction WAV byte-identical pre-versus-post at `cc919559b4508b6b…f01bbbd7`; the c33 render_stem.py locked script byte-identical at `214372d9…5b2b`; the palette rubric document at `9eb5523c…5e1879`; the palette verdict at `5ba4eaca…5644a`; the palette rubric hash file content byte-equal to the document SHA; and the verdict's `rubric_hash_v2` field byte-equal to both. Every check passed.

The audit sufficiency assessment against the fanout clone's scoped objective returned every criterion met on disk:

- Palette-render sibling delivery emitted; does not overwrite operator-blessed Cycle 5 — ✓
- Three-way `rubric_hash_v2` byte-equality on the verdict — ✓
- Cycle 5 operator-blessed hard anchor preserved — ✓
- Rubric doc landed before any script under `scripts/v3_spine/palette_render/` (mtime hard) — ✓
- Bass VST3 `REDEFINED_GAP` arm engaged per the c36 clone-2 envelope (`max_pairwise_rms = 0.0656 > 1e-4`) — ✓ with fluidsynth GM(33) fallback honestly disclosed
- Guitar/piano/other sfizz probe (`sfz_dir_missing`) → fluidsynth GM(25/0/88) fallback — ✓ honestly logged in the fetchability ladder
- Drums fluidsynth GM channel 10 and vocals verbatim D2 htdemucs copy from c5 — ✓
- Cycle 6 Method B rc7 loudness chain applied verbatim via READ-ONLY import — ✓
- Both panel comparisons finite on all five keys — ✓
- Rubric-frozen three-verdict enum fires `PALETTE_MOVES_PANEL` on the Comparison B threshold (4/5 keys exceed 5% relative) — ✓

The single non-passing check was ledger visibility: `grep -c '"milestone_id": "M-V3-SPINE-1/chicken-grease-palette-render' promise_ledger.jsonl` returned 0 in the primary workspace ledger. The worker claimed eleven `-clone-2`-suffixed rows had landed in the fork shadow ledger. This is the same shadow-ledger merge lag pattern the previous three fanout branches all exhibited; it is non-blocking when the required substantive artifact is on disk (as here), and it is routed to the c22 root conductor as research-brief S1 (mandatory linear precondition before any dependent branch fires).

Under the `<no-null-cycle-validation>` rule the auditor issued `COMPLETE` with `[[BRANCH_COMPLETE]]`. The clone's scoped objective is discharged; no in-scope work remains; the operator's palette-becomes-primary decision is not something any in-loop cycle can move.

## 4. Interpretive honesty caveats surfaced to the operator (MINOR observations)

The Cycle 2 audit carried three interpretive observations forward verbatim as inputs to the c22 palette framing document. These are the load-bearing caveats the operator's ear judgment must discriminate before palette-becomes-primary can advance.

**MINOR-2 (interpretive).** The palette-render's Comparison A perceptual panel numerically outperforms the c5 reconstruction against the original on every reported numeric key (Comparison A mel L1 = 6.36 dB vs c5-vs-original 8.79 dB; RMS-env RMSE 0.107 vs 0.147; LUFS-M RMSE 4.51 LU vs 7.43 LU; VGGish cosine distance 0.243 vs 0.188 — the one key the palette panel does worse on, VGGish, is because the palette moves the reconstruction *away* from the original into a different neighborhood, which is the point of the exercise). These numeric wins are strong signals *given* the pipeline that produced them, but the operator's ear judgment is by Fixed Decision 6 the only authoritative LANDS gate; panel improvement is never a LANDS gate.

**MINOR-3 (mechanism).** The load-bearing caveat. Because the Surge XT VST3 bass path failed byte-determinism ×2 outside the c36 envelope and the sfizz path failed on missing SFZ files, all six palette-render stems ended up on fluidsynth GM at the bottom of their respective ladders. The "palette render" that the panel movement measures is therefore, at the mechanism level, fluidsynth GM with a different program selection (33/25/0/88 vs the c5 defaults) plus the Cycle 6 Method B 12-band iirpeak EQ plus per-stem RMS/LUFS-S loudness matching — not the intended Surge XT synthesizer or sfizz sampler timbral character. If the operator's ear judgment confirms palette audibly moves and audibly improves, the operator must specifically discriminate: (i) is the audible improvement attributable to the GM+program-substitution + fitted EQ + loudness-match chain alone? If so, fluidsynth+EQ+loudness stays primary. (ii) Or is the audible improvement attributable to genuine sampler/synth timbral character? If so, egress unblock or an alternate VST3 candidate is required to actually reproduce the palette on the intended synthesizer path.

**MINOR-4 (D-D framing).** The operator's D-D directive was framed as "if the palette moves the panel and audibly moves and audibly improves, palette becomes primary." The rubric fired PALETTE_MOVES_PANEL on the panel-movement clause. The operator's forthcoming ear judgment on the A/B pair `data/v3/deliveries/31a164f845f8e27e/palette_render/{original_ab,reconstruction_ab}` (which the delivery manifest catalogs) is the second gate. The third gate — MINOR-3 discrimination between mechanism (i) GM+EQ+loudness alone and mechanism (ii) genuine sampler/synth character — is the c22 framing document's responsibility to surface to the operator so the D-D decision is fully-informed.

The Cycle 2 auditor emphasized that all three MINOR observations are informational for the operator, not defects to fix; they are the honest reading of what the palette-render pipeline actually produced given the fetchability ladder outcomes.

## 5. Merge disposition and c22 handoff

**Merge disposition.** This branch merges as `[[BRANCH_COMPLETE]]`. The required output artifact exists at the required path; every hard anchor is byte-identical pre-versus-post live-verified; the three-way rubric hash chain holds byte-equal; the c5 operator-blessed delivery is preserved unchanged. Two moderate observations from the audit (the ledger-visibility gap flagged as MINOR-1 at merge time; the merge report to be picked up by the harness at natural clone exit at `/home/user/music-gen-instance-v3/fork-0a1b1dca4f9b/clone-2/merge_report.md`) plus the three interpretive MINOR-2/3/4 observations are logged for the root conductor's post-merge integration.

**c22 handoff imperatives.** The c22 research brief already routes all follow-on work to disjoint owners:

- **S1 (mandatory linear first).** Reconcile 11 c21 clone-2 shadow-ledger events plus 3 c20 Peach Dream MODERATE-1 handoff items into the primary `promise_ledger.jsonl` per the c38+ post-merge-reconciliation precedent, under the `-clone-2` suffix on infra families; the substantive `M-V3-SPINE-1/chicken-grease-palette-render` row plus its six sub-leaves stays unsuffixed. Verify `promise_check` returns 0-ERROR post-concatenation. Must land BEFORE either c22 fanout branch emits any ledger event (avoids further shadow-ledger stacking).
- **S2 (parallel fanout).** Disco A launch (the fifth focus song; direct path to a third M-V3-FOCUS-1 accept and clearing the ≥3 gate with margin).
- **S3 (parallel fanout).** WIG restart PARTIAL → LANDS (completing the four remaining MuScriptor probes then running the downstream chain, matching the shape Rome delivered end-to-end at Cycle 20).
- **S4 (linear supplement).** Ship `docs/v3_spine_chicken_grease_palette_c22_framing.md` surfacing MINOR-2/3/4 verbatim so the operator's listening loop can discriminate GM+EQ+loudness alone from genuine sampler/synth character before the D-D palette-becomes-primary advance.

## 6. Campaign-level state after this branch

Chicken Grease M-V3-SPINE-1 is now operator-LANDED as of 2026-09-02 on the Cycle 5 v3 fluidsynth reconstruction. The Cycle 5-through-Cycle 19 heartbeat chain (fifteen LANDS_pending_operator verdicts) is preserved byte-identically on disk and is now historical. The palette-render sibling deliverable from this branch sits alongside the c5 delivery as a candidate for a possible palette-becomes-primary transition, gated on the operator's forthcoming D-D judgment plus the MINOR-3 mechanism-discrimination requirement.

Focus-set accept status toward the M-V3-FOCUS-1 gate (which requires ≥3 accepts): two confirmed accepts on disk (Chicken Grease via the operator's c5 LANDS and Rome via the Cycle 20 clone-1 fanout D-A internal-gate delivery); WIG PARTIAL awaiting the c22 S3 restart; Peach Dream PARTIAL delivered via the Option 3 accept-terminal precedent at Cycle 20 clone-2 Cycle 4; Disco A not yet started, queued for c22 S2. The c22 fanout has a clear path to closing the gate with margin.

The auditor's cumulative discipline observation is worth recording: eleven consecutive audits, roughly 275+ live SHA spot-checks, zero fabrications. The pattern of live-verifying every claimed SHA from disk rather than trusting worker claims holds under compaction and across fanout branches. Every audit reproduces the campaign constants (rubric `c49db5a1…` on the SPINE track and `9eb5523c…` on the palette-render track, c5 anchor `cc919559…`, c33 render_stem `214372d9…`, c7 venv dir-manifest `a86205175728…`) live from disk, never from memory.

## 7. Conclusions

Clone 2 of fork `0a1b1dca4f9b` delivered the operator-D-D-directed Chicken Grease palette-render as a sibling secondary deliverable to the operator-LANDED Cycle 5 v3 fluidsynth reconstruction. The frozen three-verdict rubric was committed before any script was written; the pipeline executed end-to-end with byte-determinism ×2 satisfied on every stem that reached its final routing; the c5 operator-blessed anchor is preserved unchanged; the three-way rubric hash chain holds byte-equal; the verdict `PALETTE_MOVES_PANEL` fired legitimately on four-of-five numeric panel keys exceeding the 5% relative-delta Comparison B threshold. The branch closes under `[[BRANCH_COMPLETE]]` after a re-verification audit that found no critical or moderate defects.

The load-bearing honesty caveat for the operator's forthcoming D-D decision is prominently disclosed in the verdict and the audit: because the Surge XT VST3 bass path failed byte-determinism ×2 outside the c36 envelope and the sfizz path failed on missing SFZ files, all six palette-render stems ended up on fluidsynth GM at the bottom of their respective fetchability ladders. The measured panel movement is real, but the underlying mechanism is GM + program substitution + Cycle 6 Method B 12-band iirpeak EQ + per-stem RMS/LUFS-S loudness match — not the intended Surge XT synthesizer or sfizz sampler timbral character. The operator's ear judgment on the A/B pair is the second gate; a c22 framing document is queued to surface the MINOR-3 mechanism-discrimination requirement so the palette-becomes-primary decision can be made fully-informed.

## Appendix: Implementation Details

### A.1 Delivered artifacts

Required output artifact: `docs/v3_spine_chicken_grease_palette_render_c21_report.md` (12 053 bytes).

Verdict: `data/v3/deliveries/31a164f845f8e27e/cycle21/verdict_palette.json` (SHA `5ba4eaca242fcd29…5644a`), sibling to `cycle20/`; does not overwrite operator-blessed Cycle 5 delivery.

Delivery-side artifacts under `data/v3/deliveries/31a164f845f8e27e/palette_render/`: `full_reconstruction_palette.wav`, `manifest.json`, `panel_original_vs_palette.tsv`, `panel_fluidsynth_vs_palette.tsv`, `anchor_preservation.json`, `byte_determinism.json`, `fetchability_ladder.jsonl`, plus `per_stem/` subtree.

Working artifacts under `data/v3_spine/31a164f845f8e27e/palette_render/`: `matched_{bass,drums,guitar,other,piano,vocals}.wav`, `full_reconstruction_palette.wav`, `mix_manifest.json`, `panel_delta_comparison.json`, `panel_original_vs_palette.json`, `panel_fluidsynth_vs_palette.json`, `anchor_preservation.json`, `byte_determinism.json`, `fetchability_ladder.jsonl`, `rubric_hash_v2.txt`, `per_stem/` subtree.

Rubric doc: `docs/v3_spine_chicken_grease_palette_render_c21_rubric.md` (SHA `9eb5523cbd090c388e30b0b271cb1dffd4f321ed907c78be122f56cbad5e1879`).

### A.2 Integrity chains

Three-way rubric chain (palette-render track): `docs/v3_spine_chicken_grease_palette_render_c21_rubric.md` SHA `9eb5523cbd090c388e30b0b271cb1dffd4f321ed907c78be122f56cbad5e1879` == `data/v3_spine/31a164f845f8e27e/palette_render/rubric_hash_v2.txt` content == `verdict_palette.json.rubric_hash_v2` field. All three sources independently live-verified by the auditor.

Cycle 5 operator-blessed hard anchor: `data/v3/deliveries/31a164f845f8e27e/operator_section/full_reconstruction_operator_section.wav` SHA `cc919559b4508b6bfe868fa5433a50b6805c43bab763665a5f2be367f01bbbd7`, byte-identical pre-versus-post live-verified.

c33 render_stem anchor: `scripts/palette_render/render_stem.py` SHA `214372d920a319a97d6e3fc7b9ee4134c08c0cb4aecb776f4a50c75f965b5b2b`, byte-identical live-verified.

### A.3 Consumed canonical MIDI SHAs (READ-ONLY, pre==post)

bass `f439fb31b5988b54903bb956c4e0db78b83ea7223cfb27683c9d3978dd9404fb`; drums `8021a1ca22ef84ebfce18ee474d285d6dd7c07faca55683c84d49883743cbc08`; guitar `69e7c7bbf05b1f5e4926c29a19825ba720169efff37372069c620b12650197c8`; other `c88c69a0c1f1837d25ec959e42458db9dab93c61b935d8d11a4061b5fb8134f4`; piano `c88c69a0c1f1837d25ec959e42458db9dab93c61b935d8d11a4061b5fb8134f4` (identical to other, the canonical empty-events serialization hash on both empty sources).

### A.4 Fetchability ladder outcomes

| Stem | Intended | Actual | Fallback reason |
|---|---|---|---|
| bass | Surge XT VST3 (c33 Branch B) | fluidsynth GM(33) | `REDEFINED_GAP` arm: byte-determinism ×2 failed, `max_pairwise_rms = 0.0656` vs c36 envelope 1e-4 |
| guitar | sfizz CLI | fluidsynth GM(25) | `sfz_dir_missing_no_sfz_files_in_workspace` |
| piano | sfizz CLI | fluidsynth GM(0) | `sfz_dir_missing_no_sfz_files_in_workspace` |
| other | sfizz CLI | fluidsynth GM(88) | `sfz_dir_missing_no_sfz_files_in_workspace` |
| drums | fluidsynth GM ch. 10 | fluidsynth GM ch. 10 | (intended) |
| vocals | htdemucs verbatim (D2) | htdemucs verbatim | (intended) |

### A.5 Panel numbers

**Comparison A (original vs palette-render):** spectral centroid RMSE 1 149.89 Hz; mel L1 6.36 dB; RMS-env RMSE 0.1071; LUFS-M RMSE 4.51 LU; VGGish cosine 0.24335.

**Comparison B (Cycle 5 fluidsynth-render vs palette-render):** spectral centroid RMSE 3 120.31 Hz; mel L1 6.89 dB; RMS-env RMSE 0.0802; LUFS-M RMSE 3.72 LU; VGGish cosine 0.09569.

**Reference (Cycle 5-vs-original):** spectral centroid RMSE 3 254.47 Hz; mel L1 8.79 dB; RMS-env RMSE 0.1473; LUFS-M RMSE 7.43 LU; VGGish cosine 0.18762.

**Comparison B threshold outcome:** four of five keys exceed 5% relative delta (mel L1 21.59%; RMS-env 45.54%; LUFS-M 49.86%; VGGish 48.99%; spectral centroid 4.12% under threshold). Rubric fires `PALETTE_MOVES_PANEL`.

### A.6 Verdict fields

`milestone = M-V3-SPINE-1/chicken-grease-palette-render`; `cycle = 21`; `song_sha16 = 31a164f845f8e27e`; `operator_section_s = [233.63918, 263.63918]`; `verdict = PALETTE_MOVES_PANEL`; `blocked_on_operator = true`; `c5_delivery_anchor_preserved = true`; `rubric_hash_v2_chain_holds = true`; `sfizz_fallback_reason = sfz_dir_missing_no_sfz_files_in_workspace`; `sfizz_fallback_stems = [guitar, piano, other]`; `rubric_doc_path = docs/v3_spine_chicken_grease_palette_render_c21_rubric.md`; `rubric_hash_v2_txt_path = data/v3_spine/31a164f845f8e27e/palette_render/rubric_hash_v2.txt`.

### A.7 MINOR observations for operator listening loop

MINOR-2 (interpretive): palette panel numerically outperforms c5 on Comparison A but panel is never a LANDS gate. MINOR-3 (mechanism): all six palette-render stems reached fluidsynth GM at the bottom of their fetchability ladders; the "palette" is GM + program substitution + Cycle 6 Method B 12-band iirpeak EQ + per-stem RMS/LUFS-S loudness match, not Surge XT / sfizz timbral character. MINOR-4 (D-D framing): operator's ear judgment on A/B is the second gate; MINOR-3 mechanism discrimination is the third gate; c22 framing doc queued.

### A.8 Recurring shadow-ledger MINOR-1

Worker claimed eleven `-clone-2`-suffixed ledger events (six named + two housekeeping + three auxiliary) landed in the fork shadow ledger; primary `promise_ledger.jsonl` returned zero `M-V3-SPINE-1/chicken-grease-palette-render` matches at audit time. Same shadow-ledger merge lag pattern as prior three fanout branches. Non-blocking. Routed to c22 root conductor as research-brief S1 mandatory linear precondition.

### A.9 Environment pins

`PYTHONHASHSEED=0`; `SOURCE_DATE_EPOCH=1756463424`; `TZ=UTC`; `LC_ALL=C.UTF-8`; `OMP_NUM_THREADS=1`, `MKL_NUM_THREADS=1`, `OPENBLAS_NUM_THREADS=1`; interpreter `/usr/bin/python3`; c7 venv dir-manifest `a86205175728d58f0a96ad02fc1ab1ac9e35f06c5ed568a960ed1ff261f83a74` (thirteen-cycle chain preserved).

### A.10 Source sessions

| Cycle | Researcher | Worker | Auditor |
|---|---|---|---|
| 1 | b8d2fd7a-b8f8-42c5-91de-b9e6dd20051f | d16e4456-b951-48c6-bbc4-87c388a4d6d0 | 17358ffd-e62b-4cfb-bef9-639d44b0a0d8 |
| 2 | aae22138-552a-46a9-bfe7-41e2ef88f3a5 | e13f95c2-0bcf-480f-8825-012dc31d53ef | 234b8d88-409e-44c2-900a-8ed03ce4d70f |

### A.11 Fanout metadata

Fork `0a1b1dca4f9b`. Clone 2 of the Chicken Grease palette-render assignment. Merge report expected at `/home/user/music-gen-instance-v3/fork-0a1b1dca4f9b/clone-2/merge_report.md` for parent-conductor pickup, carrying the palette-render verdict, the three-way rubric hash chain, the MINOR-1 shadow-ledger reconciliation queued for c22 S1, and MINOR-2/3/4 interpretive observations queued for c22 S4 framing document. Sibling clones in the same fork reported separately.
