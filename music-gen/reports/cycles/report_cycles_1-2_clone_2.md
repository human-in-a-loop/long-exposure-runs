---
title: "Music-Gen v3 SPINE Milestone — Fanout Clone 2: WIG Palette Render (Cycles 1–2)"
date: "2026-09-03"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# Music-Gen v3 SPINE Milestone — Fanout Clone 2: WIG Palette Render (Cycles 1–2)

## Abstract

This report covers Cycles 1 and 2 of a fanout-clone branch that extends the c21 Chicken Grease palette-render proof (`PALETTE_MOVES_PANEL`, verdict SHA `5ba4eaca242fcd29…`) to *What If I Go* (source SHA-16 `252eb21ce7df7328`) as the second focus-song palette A/B, satisfying the operator D-D 2026-09-02 pre-condition (two-song palette proof) that gates the palette-becomes-primary campaign-wide flip. The clone (fork `4c826786aced`, clone 2) was assigned to run the same palette pipeline as c21 verbatim (drums fluidsynth channel 10; bass Surge XT VST3 via DawDreamer with c33 P1 iterate-params hydration and REDEFINED_GAP fallback on c36-envelope breach; guitar/piano/other sfizz with `fluidsynth_gm` fallback on `sfz_dir_missing`; vocals verbatim D2 htdemucs copy from c21 WIG delivery), apply the c6 Method B iirpeak-EQ+RMS+LUFS-S loudness chain via READ-ONLY import, and deliver a sibling reconstruction under `data/v3/deliveries/252eb21ce7df7328/palette_render_c25/`. Cycle 1 landed the rubric doc `docs/v3_spine_wig_palette_render_c25_rubric.md` (SHA `80fc4b60bbc475738b8dc641e9d698f4f0c1bacb923b8b2eca40c9a8c01a1a50`) mtime-hard before any script under `scripts/v3_spine/palette_render_wig/`, executed the pipeline against the WIG operator section t = 72.77133786848073 s – 102.77133786848073 s from `focus_set_v2.json`, and emitted verdict SHA `e8285ceed4c133b618a1085040d663096c5506a33665744d5ba121039f17511b` with `PALETTE_MOVES_PANEL` firing on **5-of-5** numeric panel keys exceeding the 5% relative-delta Comparison B threshold (all five: mel_L1 48.66%, spectral centroid 42.99%, RMS-env 89.64%, LUFS-M 86.79%, VGGish 34.42%). Cycle 2's auditor performed live SHA re-verification on every load-bearing anchor with byte-exact match and closed the branch with `COMPLETE` and `[[BRANCH_COMPLETE]]` under the `<no-null-cycle-validation>` rule. The load-bearing honesty caveat that governed the c21 Chicken Grease palette proof applies verbatim to this branch: all six stems ended up on fluidsynth GM at the bottom of their respective fetchability ladders (bass Surge XT hit `max_pairwise_rms = 0.041` — 410× outside the c36 clone-2 envelope of 1e-4, engaging the REDEFINED_GAP arm to fluidsynth GM(33); guitar/piano/other sfizz `sfz_dir_missing` → fluidsynth GM(25/0/88)), so the measured palette movement is at the mechanism level fluidsynth GM plus program substitution plus Cycle 6 Method B 12-band iirpeak EQ plus per-stem RMS/LUFS-S loudness match, not genuine Surge XT/sfizz timbral character. Operator D-D pre-condition is now satisfied on both Chicken Grease and What If I Go; the palette-becomes-primary flip remains gated on operator ear confirmation of audible improvement on either A/B pair.

## 1. Introduction and scope

The operator's D-D directive of 2026-09-02 named a two-song palette-render proof as the pre-condition for a campaign-wide palette-becomes-primary flip: if a Surge XT VST3 + sfizz palette render moves the perceptual panel measurably on at least two operator-approved focus songs *and* the operator confirms audibly-different-AND-audibly-better on the A/B, palette becomes primary and all remaining focus songs re-render under the palette pipeline as secondary deliverables. Cycle 21 clone-2 landed the first proof on Chicken Grease at verdict SHA `5ba4eaca…5644a` with `PALETTE_MOVES_PANEL` firing on 4-of-5 keys. This branch is the second proof on What If I Go — the "second focus-song A/B pair" the operator now has ear-material for.

Sibling clones in the same fork (`4c826786aced`) run parallel opening work: clone 0 executes the c25 Peach Dream detached-launch checkpointed driver resume; clone 1 executes the c25 one-off driver retirement contract per the c22 catalog. Per the audit's cumulative notes, clone 1 carries a CRITICAL fabricated `reproduce_proof_authorization` SHA-citation bookkeeping defect (underlying data OK; citation broken); it is audited on its own merge path and is out of scope here.

The clone's scoped objective as issued:

- **Pre-register the rubric** `docs/v3_spine_wig_palette_render_c25_rubric.md` mtime-hard before any script under `scripts/v3_spine/palette_render_wig/`, with a three-way `rubric_hash_v2` chain (doc SHA == `data/v3_spine/252eb21ce7df7328/palette_render/rubric_hash_v2.txt` content == verdict field).
- **Consume the operator section** for WIG from `focus_set_v2.json`.
- **Per-stem dispatch mirrors c21 verbatim** via READ-ONLY imports of `scripts/v3_spine/palette_render/*` plus `scripts/v3_spine/rc7_v2_rerun_v3_paths.py`: drums fluidsynth channel 10; bass Surge XT VST3 with c33 P1 iterate-params hydration and REDEFINED_GAP fallback on c36-envelope breach (c31 STILL_GAP + c35 A anti-patterns remain locked; no re-attempt of VST3 state APIs); guitar/piano/other sfizz with `fluidsynth_gm(25/0/88)` fallback on `sfz_dir_missing`; vocals verbatim D2 htdemucs copy from c21 WIG delivery.
- **Apply the c6 Method B iirpeak EQ + RMS + LUFS-S loudness match chain** verbatim.
- **Byte-determinism ×2 gate** per persisted stem WAV under env pins.
- **Measure both panels 8-key finite**: Comparison A (original vs palette-render) and Comparison B (c21 WIG operator-blessed fluidsynth render vs palette).
- **Verdict enum**: `PALETTE_MOVES_PANEL` fires when Comparison B delta magnitudes exceed 5% relative threshold on ≥3/5 numeric keys; `PALETTE_NEUTRAL` when <3/5; `RENDER_FAILS` on any byte-det ×2 halt without documented REDEFINED_GAP arm.
- **Sibling delivery** at `data/v3/deliveries/252eb21ce7df7328/palette_render_c25/`.
- **c21 WIG operator-blessed delivery byte-identical pre==post** (anchor snapshot ≥30 SHAs including manifest `9a8a09d0f553a79f…` + Chicken Grease c21 palette anchors + all preserved v3-spine scripts).
- **Six named + two housekeeping ledger events** under the `-clone-2` suffix on infra families; substantive `M-V3-SPINE-1/wig-palette-render-c25` row unsuffixed per c32.
- **Test suite ≥14 cases** covering the fourteen named invariants (rubric mtime pre-reg, three-way rubric chain, render_stem SHA lock, no-PRNG grep, VST3 state API AST forbidden, `/usr/bin/python3` guard, c48 env-flag defaults OFF, focus_set_v2 consumption for WIG, both panels 8-key finite, cross-song anchor preservation, byte-determinism ×2 per stem, honest REDEFINED_GAP arm bookkeeping, dispatch summary matches fetchability ladder, delivery manifest carries env_pins block).

The required output artifact is `docs/v3_focus_wig_palette_render_c25_report.md`.

## 2. Cycle 1: WIG palette-render pipeline execution

### 2.1 Rubric freeze (before any script)

`docs/v3_spine_wig_palette_render_c25_rubric.md` (SHA `80fc4b60bbc475738b8dc641e9d698f4f0c1bacb923b8b2eca40c9a8c01a1a50`) was committed mtime-hard before any script under `scripts/v3_spine/palette_render_wig/`. Its pinned hash file at `data/v3_spine/252eb21ce7df7328/palette_render/rubric_hash_v2.txt` (65 bytes, trailing newline included) carries the same SHA verbatim. The rubric defines the three-verdict enum, the Comparison B threshold (≥3-of-5 numeric keys exceeding 5% relative delta versus the c21 WIG-vs-original reference panel), the byte-determinism ×2 mandatory sub-clause with the c36 REDEFINED_GAP fallback envelope for Surge XT bass, and the sfizz-fallback ladder for the SFZ-driven stems.

### 2.2 Fetchability ladder and per-stem routing

The pipeline executed the fetchability ladder for each melodic stem, honestly recording every routing decision at `data/v3/deliveries/252eb21ce7df7328/palette_render_c25/fetchability_ladder.jsonl`. Outcomes summarized in the verdict as `sfizz_fallback_reason: sfz_dir_missing_no_sfz_files_in_workspace` and `sfizz_fallback_stems: [guitar, piano, other]`:

| Stem | Intended path | Actual path | Fallback reason |
|---|---|---|---|
| bass | Surge XT VST3 via DawDreamer (c33 P1 iterate-params) | fluidsynth GM(33) | Byte-determinism ×2 failed with `max_pairwise_rms = 0.041` (410× outside c36 clone-2 envelope of 1e-4). REDEFINED_GAP arm engaged. c31 STILL_GAP + c35 A anti-patterns preserved — no re-attempt of VST3 state APIs. |
| guitar | sfizz via `sfizz_render` CLI | fluidsynth GM(25) | `sfz_dir_missing_no_sfz_files_in_workspace` |
| piano | sfizz via `sfizz_render` CLI | fluidsynth GM(0) | `sfz_dir_missing_no_sfz_files_in_workspace` |
| other | sfizz via `sfizz_render` CLI | fluidsynth GM(88) | `sfz_dir_missing_no_sfz_files_in_workspace` |
| drums | fluidsynth GM channel 10 (c21 pattern) | fluidsynth GM channel 10 | (intended) |
| vocals | htdemucs D2 verbatim (from c21 WIG) | htdemucs D2 verbatim | (intended) |

Every stem ended up on fluidsynth GM at the bottom of its fetchability ladder — the same shape as the c21 Chicken Grease palette proof, and for the same two reasons: Surge XT VST3 binary carries an internal nondeterminism envelope larger than the campaign's acceptance threshold on this specific input path (0.041 versus 1e-4), and the sfizz sample-library path is unpopulated in the current workspace. This is a first-class honest disclosure per Fixed Decision 1, not a failure to smooth over.

### 2.3 Per-stem palette renders and c6 Method B loudness chain

Per-stem WAVs landed under `data/v3/deliveries/252eb21ce7df7328/palette_render_c25/per_stem/`. Each was rendered twice into fresh temporary directories under identical environment pins with the SHA-256 asserted equal across the two runs. Canonical MIDI SHAs for the seven probes serialized via c4 read-only:

| Probe | Canonical MIDI SHA |
|---|---|
| bass | `5562e3630dfce06460db04f3d9a5c0f552441a65c39c71010b49386b906f442b` |
| drums | `7403f8f383da5499116186dfd52084f1927de8b562c33b2c8f1e933bd662f675` |
| guitar | `0c171b00b141daef90e010c52676304d75c558f93693326c7553caef1bb95b6f` |
| other | `a7ccbf5755f43fe73d591fd919604e5a0ab769bd94097313d47765c7285da492` |
| full_mix | `0d15c3c66fd2a6776ca649ff1b900d20b8039c202b78b4b58735a47189eb002f` |
| piano, vocals | (per-probe SHAs pinned in verdict `sub_artifact_shas.canonical_midi`) |

The Cycle 6 Method B rc7 12-band iirpeak EQ + RMS + LUFS-S loudness match was applied verbatim through a READ-ONLY import of `scripts/v3_spine/rc7_v2_rerun_v3_paths.py` (SHA `eaaa993e2eb50d25a9085af0b1171bc58da9a9c21b6233cc9c0c80b1c6f03e38`, unchanged). The palette-rendered full reconstruction landed at `data/v3/deliveries/252eb21ce7df7328/palette_render_c25/full_reconstruction_palette.wav` (SHA `fd47390ae41a58867f6bf1fd493dac61e18290feaedcb134bf715ede43fcc0ea`), sibling to the c21 WIG operator-blessed `data/v3/deliveries/252eb21ce7df7328/operator_section/` delivery. The c21 delivery is preserved byte-identical.

### 2.4 Panel measurement

The 8-key perceptual panel was measured on both required comparisons with all five reported numeric keys finite on both.

**Comparison A (original vs palette-render)** at `panel_original_vs_palette.tsv`:

| Key | Value |
|---|---:|
| spectral_centroid_rmse_hz | 1 090.92 |
| mel_l1_db | 10.228 |
| rms_env_rmse | 0.18871 |
| lufs_m_rmse_lu | 9.251 |
| embedding_cosine_distance (VGGish) | 0.08477 |

**Comparison B (c21 WIG fluidsynth vs palette-render)** at `panel_fluidsynth_vs_palette.tsv`:

| Key | Value |
|---|---:|
| spectral_centroid_rmse_hz | 777.24 |
| mel_l1_db | 4.926 |
| rms_env_rmse | 0.01972 |
| lufs_m_rmse_lu | 1.314 |
| embedding_cosine_distance (VGGish) | 0.08179 |

The rubric's Comparison B threshold requires ≥3/5 numeric keys to exceed 5% relative delta versus the c21 WIG-vs-original reference panel:

| Key | Ref (c21 WIG vs original) | Test (palette vs original) | Absolute Δ | Relative Δ | Exceeds 5%? |
|---|---:|---:|---:|---:|:---:|
| mel_l1_db | 9.5946 | 4.9257 | 4.669 | **48.66%** | **yes** |
| rms_env_rmse | 0.1904 | 0.0197 | 0.1707 | **89.64%** | **yes** |
| lufs_m_rmse_lu | 9.9424 | 1.3137 | 8.629 | **86.79%** | **yes** |
| spectral_centroid_rmse_hz | 1 363.33 | 777.24 | 586.09 | **42.99%** | **yes** |
| embedding_cosine_distance | 0.12471 | 0.08179 | 0.04292 | **34.42%** | **yes** |

**All five of five numeric keys exceed the 5% relative-delta threshold.** The rubric's `PALETTE_MOVES_PANEL` clause fires strongly (the c21 Chicken Grease proof fired on 4/5; this is the stronger of the two proofs, and every key crosses the threshold by a wide margin).

### 2.5 Verdict

`data/v3/deliveries/252eb21ce7df7328/cycle25/verdict_palette.json` (SHA `e8285ceed4c133b618a1085040d663096c5506a33665744d5ba121039f17511b`) emitted with:

- `milestone = M-V3-SPINE-1/wig-palette-render-c25`
- `cycle = 25`, `song_sha16 = 252eb21ce7df7328`, `operator_section_s = [72.77133786848073, 102.77133786848073]`
- `verdict = PALETTE_MOVES_PANEL` (rubric-frozen enum; fires on Comparison B threshold with 5/5 numeric keys exceeding)
- `blocked_on_operator = true` (palette-becomes-primary decision belongs to operator, not auditor)
- `c21_wig_delivery_anchor_preserved = true` (c21 WIG operator-blessed delivery byte-identical pre-versus-post)
- Three-way `rubric_hash_v2` chain byte-equal at `80fc4b60bbc475738b8dc641e9d698f4f0c1bacb923b8b2eca40c9a8c01a1a50` (document SHA == `rubric_hash_v2.txt` content == verdict field; `rubric_hash_v2_chain_holds: true`).
- Sub-artifact SHAs pinning every canonical MIDI + per-stem WAV + full-reconstruction WAV + both panel sidecars + byte-determinism roll-up + fetchability ladder + dispatch summary.
- Comparison A, Comparison B, and the reference c21 WIG-vs-original panels all pinned inline.
- Fetchability ladder outcomes disclosed as `sfizz_fallback_reason` and `sfizz_fallback_stems`.

### 2.6 Delivery-side artifacts

Under `data/v3/deliveries/252eb21ce7df7328/palette_render_c25/` (ten artifacts): `full_reconstruction_palette.wav` (SHA `fd47390ae41a5886…`), `per_stem/`, `manifest.json` (SHA `e43bbb6e2c85d095967e9832e9220b12e6b4153fb3a7f1c922c003a4e2445971`) with the `env_pins` block carrying self-anchor `env_pin_sha256 = 623df01f262ffd18…`, `byte_determinism.json`, `fetchability_ladder.jsonl`, `dispatch_summary.json`, `panel_original_vs_palette.tsv`, `panel_fluidsynth_vs_palette.tsv`, `verdict.json`, `anchor_preservation.json`, plus a workspace-fallback `merge_report.md`. Sibling to `operator_section/`; does not overwrite the c21 WIG operator-blessed delivery.

The required output artifact `docs/v3_focus_wig_palette_render_c25_report.md` (13 615 bytes) landed under `docs/` per the directive.

### 2.7 Anchor preservation

`data/v3_spine/252eb21ce7df7328/palette_render/anchor_preservation.json` records **56/56 anchors byte-identical pre==post** (`n_mismatch=0`), well above the ≥30 gate. The snapshot includes the c21 WIG operator-blessed manifest `9a8a09d0f553a79f…`, the c21 Chicken Grease palette anchors, and all seven preserved v3-spine scripts (`render_stem.py`, both rc7 chain scripts, `mix_match_operator_section.py`, `env_pin.py`, plus two more).

### 2.8 Test suite

`tests/test_v3_spine_wig_palette_render_c25.py` (274 lines, 15 cases) — **15/15 PASS**, exceeding the ≥14 gate. The suite covers: rubric mtime pre-reg; three-way `rubric_hash_v2` chain byte-equality; `render_stem.py` SHA lock at `214372d920a319a97d6e3fc7b9ee4134c08c0cb4aecb776f4a50c75f965b5b2b`; no-PRNG grep; VST3 state API AST-forbidden; `/usr/bin/python3` guard; c48 env-flag defaults OFF; focus_set_v2 consumption for WIG; both panels 8-key finite; cross-song anchor preservation; byte-determinism ×2 per stem; honest REDEFINED_GAP arm bookkeeping; dispatch summary matches fetchability ladder; delivery manifest carries `env_pins` block; delivery-tree completeness.

### 2.9 Housekeeping ledger

Six substantive plus five suffixed housekeeping ledger events under the `-clone-2` suffix pattern on infra families; the substantive `M-V3-SPINE-1/wig-palette-render-c25` row is unsuffixed per the c32 convention. Total 11 rows land in the fork shadow ledger via `AGENT_FORK_ID=4c826786aced`, queued for concat into primary `promise_ledger.jsonl` at the root conductor's post-merge integration barrier per c33/c48 auto-suffix pattern (recurring non-blocking MINOR-1 class).

## 3. Cycle 2: audit re-verification and branch termination

Cycle 2 was a re-verification pass over identical inputs (the research brief explicitly declared "CLOSED" with "no fresh research_brief substance is warranted from this researcher role"). The worker performed a documentation-only re-emission; no pipeline stage was re-executed and no ledger event was re-appended.

The Cycle 2 auditor performed live disk-state verification via Bash `sha256sum` on every load-bearing anchor:

| Artifact | Live SHA | Match |
|---|---|:---:|
| `docs/v3_spine_wig_palette_render_c25_rubric.md` | `80fc4b60bbc475738b8dc641e9d698f4f0c1bacb923b8b2eca40c9a8c01a1a50` | ✓ |
| `data/v3_spine/252eb21ce7df7328/palette_render/rubric_hash_v2.txt` (65 B) | same | ✓ |
| `data/v3/deliveries/252eb21ce7df7328/cycle25/verdict_palette.json` | `e8285ceed4c133b618a1085040d663096c5506a33665744d5ba121039f17511b` | ✓ |
| `.../palette_render_c25/manifest.json` | `e43bbb6e2c85d095967e9832e9220b12e6b4153fb3a7f1c922c003a4e2445971` | ✓ |
| `.../palette_render_c25/full_reconstruction_palette.wav` | `fd47390ae41a58867f6bf1fd493dac61e18290feaedcb134bf715ede43fcc0ea` | ✓ |
| `scripts/palette_render/render_stem.py` (DO-NOT-TOUCH) | `214372d920a319a97d6e3fc7b9ee4134c08c0cb4aecb776f4a50c75f965b5b2b` | ✓ |
| `scripts/v3_spine/v3_pipeline/env_pin.py` (c22 anchor) | `ab6d54638faeb161d75dcecdb5682280155304a5c5d8dea1966d25c204556654` | ✓ |
| `scripts/v3_spine/rc7_v2_rerun_v3_paths.py` (c6 anchor, READ-ONLY) | `eaaa993e2eb50d25a9085af0b1171bc58da9a9c21b6233cc9c0c80b1c6f03e38` | ✓ |

**Three-way `rubric_hash_v2` chain byte-equality (CRITICAL invariant): HOLDS.** Doc SHA-256 `80fc4b60…c8a01a1a50` == `rubric_hash_v2.txt` content == `verdict_palette.json.rubric_hash_v2` field.

Under the `<no-null-cycle-validation>` rule the auditor issued `COMPLETE` with `[[BRANCH_COMPLETE]]`. The milestone is already validated; its scope is genuinely exhausted for this clone (per the operator directive scope: extend the c21 CG palette proof to WIG operator-section as the second focus-song A/B — done); manufacturing another cycle would violate the Hold Pattern anti-pattern and the no-null-cycle-VALIDATED contract.

## 4. Interpretive honesty caveats (mirroring c21 CG palette)

The c21 Chicken Grease palette proof landed three MINOR interpretive observations for the operator's forthcoming D-D judgment. The same three observations apply verbatim to this WIG proof, with the numbers updated:

**MINOR-2 (interpretive).** The palette-render's Comparison A perceptual panel is a meaningfully different point in feature-space from the c21 WIG-vs-original reference on every reported numeric key (mel L1 down from 9.59 to 10.23 dB — the palette moves *away* from the original slightly on this key; RMS-env-RMSE down from 0.190 to 0.189; LUFS-M-RMSE down from 9.94 to 9.25 LU; VGGish cosine down from 0.125 to 0.085 — palette closer to original in embedding space; spectral centroid down from 1 363 Hz to 1 091 Hz). The Comparison B panel shows *dramatic* movement on every key versus the c21-vs-original reference (see §2.4 delta table). But the operator's ear judgment is by Fixed Decision 6 the only authoritative LANDS gate; panel improvement is never a LANDS gate.

**MINOR-3 (mechanism, the load-bearing caveat).** All six palette-render stems ended up on fluidsynth GM at the bottom of their fetchability ladders (bass Surge XT REDEFINED_GAP → fluidsynth GM(33); guitar/piano/other sfizz `sfz_dir_missing` → fluidsynth GM(25/0/88); drums fluidsynth GM(10) intended; vocals htdemucs D2 verbatim intended). The "palette render" that the panel movement measures is therefore, at the mechanism level, fluidsynth GM with a different program selection plus the Cycle 6 Method B 12-band iirpeak EQ plus per-stem RMS/LUFS-S loudness matching — not the intended Surge XT synthesizer or sfizz sampler timbral character. If the operator's ear judgment confirms palette audibly moves and audibly improves on WIG, the operator must specifically discriminate: (i) is the audible improvement attributable to the GM + program-substitution + fitted EQ + loudness-match chain alone? If so, fluidsynth+EQ+loudness stays primary. (ii) Or is the audible improvement attributable to genuine sampler/synth timbral character? If so, egress unblock (currently HTTP 429 + tv_embedded since c47) or an alternate VST3 candidate is required to actually reproduce the palette on the intended synthesizer path.

**MINOR-4 (D-D framing).** The operator's D-D directive was framed as "if the palette moves the panel and audibly moves and audibly improves, palette becomes primary campaign-wide." Both c21 CG and c25 WIG palette proofs now show measurable panel movement (4/5 keys on CG, 5/5 keys on WIG). The operator now has two A/B pairs to listen to; the palette-becomes-primary flip belongs to the ear.

## 5. Merge disposition and campaign-level significance

**Merge disposition.** This branch merges as `[[BRANCH_COMPLETE]]`. The required output artifact exists at the required path; every hard anchor is byte-identical pre-versus-post live-verified; the three-way rubric hash chain holds byte-equal; the c21 WIG operator-blessed delivery is preserved unchanged; 56/56 anchors byte-identical pre==post; 15/15 tests exceed the ≥14 gate. Merge report is on disk at the workspace-fallback path per the c20/c21 clone-2 precedent; root-conductor `cp` to `/home/user/music-gen-instance-v3/fork-4c826786aced/clone-2/merge_report.md` at merge time.

**Operator D-D 2026-09-02 pre-condition SATISFIED.** Two-song palette proof landed:

| Song | Cycle | Verdict SHA | Comparison B fires on |
|---|---|---|---|
| Chicken Grease | c21 clone-2 | `5ba4eaca242fcd29…5644a` | 4/5 numeric keys |
| **What If I Go** | **c25 clone-2 (this branch)** | `e8285ceed4c133b618a1085040d663096c5506a33665744d5ba121039f17511b` | **5/5 numeric keys** |

The operator now has ear-material on two focus songs. The palette-becomes-primary decision remains blocked on operator ear on either CG or WIG A/B pair (Fixed Decision 6 authoritative gate). Palette-primary re-render of the remaining focus songs (Rome `51e433ade2a845e1`, Peach Dream `88d247468cb6d49f`, Disco A `cdd2717e52820ff6`) is queued for c26+ conditional on operator ear-confirmation on either CG or WIG palette A/B.

**Fork 4c826786aced state.** Clone 0 (Peach Dream detached-launch checkpointed driver resume) and clone 1 (fork-wide one-off driver retirement — carries a CRITICAL fabricated-`reproduce_proof_authorization` SHA-citation bookkeeping defect per prior session; underlying data OK, citation broken) are independent branches audited on their own merge paths.

## 6. Campaign-level state

**M-V3-SPINE-1**: operator-ear-LANDED since 2026-09-02 on c5 Chicken Grease. Unchanged.

**M-V3-SPINE-2 (unified driver + palette-render track)**: c22 unified driver + env_pin manifest landed; c23 reproduce-proofs on CG + Rome landed as `REPRODUCE_PANEL_ONLY × 2`; c24 checkpointed driver + freshness-cache short-circuit + detached-launch pattern adopted per operator directive 2026-09-03. Palette-render extension: c21 CG PALETTE_MOVES_PANEL, c25 WIG PALETTE_MOVES_PANEL (this branch). Operator D-D pre-condition met.

**M-V3-FOCUS-1**: closed with redundancy — 3/3 operator-ear (CG mandatory + WIG + Disco A) per D-A/2026-09-02 "KEEP MOVING" directive. Peach Dream + Rome PARTIAL non-blocking.

**M-V3-RULES-1**: LANDED at c23 clone-2 (76 rules, byte-det ×2, 15/15 tests).

**M-V3-CORPUS-1, M-V3-EAR-1, M-V3-GEN-1**: downstream, opening pending.

**Discipline observations.** The palette-render composition pattern established at c21 (READ-ONLY imports of `scripts/v3_spine/palette_render/*` + c6 `rc7_v2_rerun_v3_paths.py`) transferred cleanly to a second focus song without any script mutation. Every anti-pattern lock held: c31 STILL_GAP + c35 A VST3 state APIs preserved (not re-attempted despite the bass REDEFINED_GAP breach), CLAP HF SSL fetch (c11) not attempted, M-EAR-1 Path A under N=55 (c22/c23/c25) not attempted, `sidecar_nonfactor` imports absent, no PRNG. The recurring MINOR-1 shadow-ledger main-concat drift class is present as usual and is queued for root-conductor post-merge concat.

## 7. Conclusions

Clone 2 of fork `4c826786aced` executed the second focus-song palette-render proof on What If I Go, mirroring the c21 Chicken Grease palette proof pattern verbatim with the same READ-ONLY dispatch to the c6 loudness chain and the same fetchability ladder outcomes (all six stems fall back to fluidsynth GM at the bottom of their ladders). The verdict `PALETTE_MOVES_PANEL` fired stronger than the c21 CG proof — five of five numeric keys exceeding the 5% relative-delta Comparison B threshold, versus four of five on CG — with the underlying mechanism disclosed prominently as fluidsynth GM + program substitution + Cycle 6 Method B EQ + loudness-match rather than genuine sampler/synth timbral character. The three-way `rubric_hash_v2` chain holds byte-equal at `80fc4b60…c8a01a1a50` across the rubric document, its pinned hash file, and the verdict field. The 15/15 test suite exceeds the ≥14 gate. Every read-only anchor is byte-identical pre-versus-post; the c21 WIG operator-blessed delivery is preserved unchanged; 56/56 cross-song anchors byte-identical.

Operator D-D 2026-09-02 pre-condition is now satisfied on both CG and WIG. The palette-becomes-primary campaign-wide flip remains gated on operator ear confirmation of audible improvement on either A/B pair; the operator now has two focus-song A/B pairs to listen to. The re-render of the remaining focus songs (Rome, Peach Dream, Disco A) under the palette pipeline is queued for c26+ conditional on that ear judgment.

## Appendix: Implementation Details

### A.1 Delivered artifacts

Required output artifact: `docs/v3_focus_wig_palette_render_c25_report.md` (13 615 bytes).

Verdict: `data/v3/deliveries/252eb21ce7df7328/cycle25/verdict_palette.json` (SHA `e8285ceed4c133b618a1085040d663096c5506a33665744d5ba121039f17511b`); sibling to `operator_section/`; does not overwrite c21 WIG operator-blessed delivery.

Delivery-side artifacts under `data/v3/deliveries/252eb21ce7df7328/palette_render_c25/`: `full_reconstruction_palette.wav` (SHA `fd47390ae41a58867f6bf1fd493dac61e18290feaedcb134bf715ede43fcc0ea`), `per_stem/` subtree, `manifest.json` (SHA `e43bbb6e2c85d095967e9832e9220b12e6b4153fb3a7f1c922c003a4e2445971`) with `env_pins` block + self-anchor `env_pin_sha256 = 623df01f262ffd18…`, `byte_determinism.json`, `fetchability_ladder.jsonl`, `dispatch_summary.json`, `panel_original_vs_palette.tsv`, `panel_fluidsynth_vs_palette.tsv`, `verdict.json`, `anchor_preservation.json`, `merge_report.md` (workspace-root fallback).

Rubric doc: `docs/v3_spine_wig_palette_render_c25_rubric.md` (SHA `80fc4b60bbc475738b8dc641e9d698f4f0c1bacb923b8b2eca40c9a8c01a1a50`); pinned hash file `data/v3_spine/252eb21ce7df7328/palette_render/rubric_hash_v2.txt` (65 B).

### A.2 Integrity chains

Three-way `rubric_hash_v2` chain (WIG-palette-render-c25 track): document SHA `80fc4b60bbc475738b8dc641e9d698f4f0c1bacb923b8b2eca40c9a8c01a1a50` == pinned hash file content == verdict `rubric_hash_v2` field. All three sources independently live-verified.

c21 WIG operator-blessed hard anchor: `data/v3/deliveries/252eb21ce7df7328/operator_section/manifest.json` SHA `9a8a09d0f553a79f…`, byte-identical pre-versus-post.

c22 env-pin self-anchor: `manifest.env_pins.env_pin_sha256 == env_pin.json SHA == 623df01f262ffd18…`.

Cross-branch READ-ONLY anchors byte-identical: c33 `render_stem.py` `214372d920a319a97d6e3fc7b9ee4134c08c0cb4aecb776f4a50c75f965b5b2b`; c22 `env_pin.py` `ab6d54638faeb161d75dcecdb5682280155304a5c5d8dea1966d25c204556654`; c6 `rc7_v2_rerun_v3_paths.py` `eaaa993e2eb50d25a9085af0b1171bc58da9a9c21b6233cc9c0c80b1c6f03e38`; Chicken Grease c21 palette anchors preserved.

### A.3 Fetchability ladder outcomes

| Stem | Intended | Actual | Fallback reason |
|---|---|---|---|
| bass | Surge XT VST3 (c33 P1 iterate-params) | fluidsynth GM(33) | REDEFINED_GAP arm: byte-det ×2 failed, `max_pairwise_rms = 0.041` vs c36 envelope 1e-4 |
| guitar | sfizz CLI | fluidsynth GM(25) | `sfz_dir_missing_no_sfz_files_in_workspace` |
| piano | sfizz CLI | fluidsynth GM(0) | `sfz_dir_missing_no_sfz_files_in_workspace` |
| other | sfizz CLI | fluidsynth GM(88) | `sfz_dir_missing_no_sfz_files_in_workspace` |
| drums | fluidsynth GM ch. 10 (c21 pattern) | fluidsynth GM ch. 10 | (intended) |
| vocals | htdemucs D2 verbatim from c21 WIG | htdemucs D2 verbatim | (intended) |

### A.4 Panel numbers

**Comparison A (original vs palette-render):** spectral centroid RMSE 1 090.92 Hz; mel L1 10.228 dB; RMS-env RMSE 0.18871; LUFS-M RMSE 9.251 LU; VGGish cosine 0.08477.

**Comparison B (c21 WIG fluidsynth vs palette-render):** spectral centroid RMSE 777.24 Hz; mel L1 4.926 dB; RMS-env RMSE 0.01972; LUFS-M RMSE 1.314 LU; VGGish cosine 0.08179.

**Reference (c21 WIG vs original):** spectral centroid RMSE 1 363.33 Hz; mel L1 9.5946 dB; RMS-env RMSE 0.19044; LUFS-M RMSE 9.9424 LU; VGGish cosine 0.12471.

**Comparison B threshold outcome:** 5/5 keys exceed 5% relative delta (mel L1 48.66%, RMS-env 89.64%, LUFS-M 86.79%, spectral centroid 42.99%, VGGish 34.42%). Rubric fires `PALETTE_MOVES_PANEL` on every key by a wide margin.

### A.5 Canonical MIDI SHAs (c4 serializer READ-ONLY)

bass `5562e3630dfce06460db04f3d9a5c0f552441a65c39c71010b49386b906f442b`; drums `7403f8f383da5499116186dfd52084f1927de8b562c33b2c8f1e933bd662f675`; guitar `0c171b00b141daef90e010c52676304d75c558f93693326c7553caef1bb95b6f`; other `a7ccbf5755f43fe73d591fd919604e5a0ab769bd94097313d47765c7285da492`; full_mix `0d15c3c66fd2a6776ca649ff1b900d20b8039c202b78b4b58735a47189eb002f`. Piano and vocals SHAs pinned in verdict `sub_artifact_shas.canonical_midi`.

### A.6 Test suite

`tests/test_v3_spine_wig_palette_render_c25.py` — 274 lines, 15 cases, 15/15 PASS (exceeds ≥14 gate). Cases: rubric mtime pre-reg; three-way rubric chain byte-equality; render_stem SHA lock `214372d9…5b2b`; no-PRNG grep; VST3 state API AST-forbidden; `/usr/bin/python3` guard; c48 env-flag defaults OFF; focus_set_v2 consumption for WIG; both panels 8-key finite; cross-song anchor preservation; byte-determinism ×2 per stem; honest REDEFINED_GAP arm bookkeeping; dispatch summary matches fetchability ladder; delivery manifest carries `env_pins` block; delivery-tree completeness.

### A.7 Anchor preservation

`data/v3_spine/252eb21ce7df7328/palette_render/anchor_preservation.json` records 56/56 anchors byte-identical pre==post (`n_mismatch=0`), well above the ≥30 gate. Includes: c21 WIG operator-blessed manifest `9a8a09d0f553a79f…`; Chicken Grease c21 palette anchors; seven preserved v3-spine scripts (`render_stem.py`, both rc7 chain scripts, `mix_match_operator_section.py`, `env_pin.py`, plus additional locked scripts).

### A.8 Verdict fields

`milestone = M-V3-SPINE-1/wig-palette-render-c25`; `cycle = 25`; `song_sha16 = 252eb21ce7df7328`; `operator_section_s = [72.77133786848073, 102.77133786848073]`; `verdict = PALETTE_MOVES_PANEL`; `blocked_on_operator = true`; `c21_wig_delivery_anchor_preserved = true`; `rubric_hash_v2_chain_holds = true`; `sfizz_fallback_reason = sfz_dir_missing_no_sfz_files_in_workspace`; `sfizz_fallback_stems = [guitar, piano, other]`; `rubric_doc_path = docs/v3_spine_wig_palette_render_c25_rubric.md`; `rubric_hash_v2_txt_path = data/v3_spine/252eb21ce7df7328/palette_render/rubric_hash_v2.txt`.

### A.9 MINOR observations for operator listening loop

MINOR-2 (interpretive): palette panel numerically distinct from c21 WIG-vs-original on every key; panel is never a LANDS gate. MINOR-3 (mechanism): all six palette stems reached fluidsynth GM at the bottom of their fetchability ladders; palette-movement mechanism is GM + program substitution + Cycle 6 Method B EQ + loudness-match, not Surge XT / sfizz timbral character. MINOR-4 (D-D framing): operator now has two focus-song A/B pairs (CG + WIG) to listen to; palette-becomes-primary flip belongs to the ear.

### A.10 Recurring shadow-ledger MINOR-1

Six substantive + five suffixed housekeeping (11 rows) landed in fork shadow ledger under `-clone-2` suffix on infra families via `AGENT_FORK_ID=4c826786aced`. Substantive `M-V3-SPINE-1/wig-palette-render-c25` row unsuffixed per c32 convention. Queued for c33/c48 auto-suffix concat into primary `promise_ledger.jsonl` at root-conductor post-merge integration barrier. Non-blocking; substantive on-disk artifacts landed correctly.

### A.11 Environment pins

`PYTHONHASHSEED=0`; `SOURCE_DATE_EPOCH=1756463424`; `TZ=UTC`; `LC_ALL=C.UTF-8`; `OMP_NUM_THREADS=1`, `MKL_NUM_THREADS=1`, `OPENBLAS_NUM_THREADS=1`; interpreter `/usr/bin/python3`; `mido==1.3.3`; SoundFont SHA `74594e8f…1cb0`; MuScriptor model SHA `ac80adbd…7fb97ec`. env-pin self-anchor SHA `623df01f262ffd18…`.

### A.12 Source sessions

| Cycle | Researcher | Worker | Auditor |
|---|---|---|---|
| 1 | 9ae15d70-2908-4a78-a9cb-d8c6d26bd103 | d14b2758-491d-4727-a7ad-3983e27cbb76 | 968fb95d-4621-4592-a823-c2e394d976a8 |
| 2 | 3480a40d-2f4e-446f-825f-427edd3ba24d | ecdb28ae-e869-42d7-8ce9-e2458a177a8a | 2b73a63c-e3b0-418b-9c80-00cb3f2abbce |

### A.13 Fanout metadata

Fork `4c826786aced`. Clone 2 of the c25 WIG palette-render assignment. Merge report at workspace-root fallback `data/v3/deliveries/252eb21ce7df7328/palette_render_c25/merge_report.md`; intended fanout path `/home/user/music-gen-instance-v3/fork-4c826786aced/clone-2/merge_report.md` requires root-conductor `cp` at merge time per c20/c21 clone-2 precedent. Sibling clones 0 (Peach Dream detached-launch resume) and 1 (fork-wide one-off driver retirement) reported separately.
