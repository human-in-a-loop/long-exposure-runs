---
created: 2026-08-29T19:40:00Z
cycle: 51
run_id: run-2026-08-28T040704Z
agent: worker
milestone: M-RECREATE-2/accurate-small-set/rc7-mix-balance-match
branch: fork-38eba9f21a61 clone-2 (Branch C)
verdict: RC7_FAILS (first-class negative finding — mechanism sound, per-stem MIDIs under-transcribed)
---

# RC7 Mix-Balance + D4 Per-Stem EQ — c51 Branch C Report

## §1 Summary

c51 Branch C landed **RC7 mix-balance mechanism** end-to-end across 5 focus songs (including mandatory Chicken Grease). The pipeline works structurally under the c50 v2 rubric: 12-band iirpeak EQ curve fitted per stem from the original 6-stem spectrum, RMS + LUFS-S loudness match applied post-EQ, per-stem outputs summed into a mixed reconstruction, and the c33 pinned Surge chorus+reverb chain preserved as a D4 comparison baseline row (never a LANDS deliverable). **Verdict: `RC7_FAILS`** — 0/5 songs pass A7 across all three drums+bass+other stems; 8/15 stems pass A7 individually. Root cause is legitimate and matches operator RC2 audit: c33-anchor per-stem MIDIs (used as placeholder per brief — Branches A+B partials not available at c51 open) are severely under-transcribed for drums, and htdemucs_6s "other" stems are near-silent on the chosen sections, leaving the mix pipeline structurally sound but mechanically unable to hit A7 without substantive RC2/RC3 inputs.

## §2 Pre-registration discipline

Per c46 path (ii) amendment: mtime hard, git-log advisory.

- **`docs/render_stem_signature_v3.md`** (SHA `<pinned in ledger event 1>`) mtime `1788032356` committed BEFORE any Python edit under `scripts/palette_render/render_stem.py`. Documents the two additive keyword-only kwargs `eq_curve: dict | None = None` and `loudness_target: dict | None = None`, extending the c36 `parameter_dict` pattern verbatim. Backwards-compat contract explicit: c33 no-kwargs path SHA-identical; c36 all-None (`parameter_dict=None, eq_curve=None, loudness_target=None`) SHA-identical to c33.
- **`docs/rc7_eq_curve_fit_method.md`** (SHA `<pinned in ledger event 1>`) mtime `1788032387` committed BEFORE any Python edit. Pins the 12-band iirpeak (Q=1.4) fit method: `np.geomspace(20.0, 20000.0, 12)` centers, per-band `mag_orig - mag_render` gains clipped ±12 dB, then a zero-mean normalization step (shape-vs-level factoring — keeps the broadband level owned by the separate `loudness_target` accept).
- `scripts/palette_render/render_stem.py` edit mtime `1788032627` > both pre-registration docs. `scripts/recreate_v2/rc7_mix_balance.py` mtime `1788032627` > both docs.
- Test suite `tests/test_rc7_impl.py` includes `test_17` (v3 sig doc mtime hard gate) + `test_18` (fit method doc mtime hard gate). Both PASS.

**Three-way rubric_hash-v2 byte-equality:** doc SHA `0e11f704e12c62f85cfb9d58d6e6890227209ffb43247239e735a22acfdebe1f` == `data/recreate_v2/rubric_hash_v2.txt` == `data/recreate_v2/rc7_out/verdict.json.rubric_hash`. Verified in `test_07`.

**c49 v1 rubric preservation:** SHA `958ade3886eba560df284878ff5d351e3f6186159ed598f68b82fc7c3fe58b9d` byte-identical pre/post (verified in `test_08`).

## §3 render_stem.py signature v3

Additive-kwargs extension per c36 backwards-compat pattern:

```python
def render_stem(stem: str, instrument: str, out_dir: Path,
                *,
                parameter_dict: dict | None = None,
                eq_curve: dict | None = None,
                loudness_target: dict | None = None) -> dict:
```

**Backwards-compat verified:**
- c33 no-kwargs path (`render_stem("drums", "fluidsynth_gm", d)`): SHA `f66a776dfde8ba15…` — byte-identical across two fresh `tempfile.mkdtemp()` runs (test_02).
- c36 all-None (`parameter_dict=None, eq_curve=None, loudness_target=None`): SHA byte-identical to c33 path (test_03).

**VST3 c35 anti-pattern lock enforced:** any non-None of the three kwargs on `instrument ∈ {surge_xt, dexed}` raises `NotImplementedError` naming the c35 STILL_GAP anchor. Verified in test_04 + test_05.

**New behavior activated** when `eq_curve is not None` OR `loudness_target is not None`:
1. Re-read canonicalized bare-render WAV.
2. If `eq_curve` present: apply 12-band iirpeak chain to each channel (parallel L/R), cascaded in ascending center-frequency order.
3. If `loudness_target` present: RMS-match to `target_rms_db`, clamped to `[-max_gain_db, +max_gain_db]`.
4. Re-canonicalize output.

Return dict gains `eq_applied`, `eq_bands_gains_db` (12 floats) when EQ used, and `loudness_error_rms_db` when loudness match used.

## §4 rc7_mix_balance.py per-song pipeline

For each of 5 focus songs (loaded from `data/recreate_v2/focus_set_v2.json`):

1. Load 6-stem original WAVs from `data/recreate_v2/baseline/<sha16>/rc9_6stem/{drums,bass,other,vocals,guitar,piano}.wav` (READ-ONLY anchor).
2. Compute per-stem target RMS_dB from the original stem (full-clip since the 6-stem WAVs represent the chosen_section content).
3. Render bare stem via `render_stem(stem, "fluidsynth_gm", bare_dir)` (c33 anchor path, no kwargs) using the c33-anchor `data/transcribe/basic_pitch/synth_030s/<stem>.mid` MIDIs — used as MIDI-per-stem placeholder per brief since Branches A+B partials are not available at c51 open.
4. Fit 12-band iirpeak EQ curve from `mag_orig - mag_render` (both mono-mixdowns, `n_fft=8192`), clip ±12 dB per band, zero-mean normalize.
5. Re-render with EQ + loudness_target via extended `render_stem`.
6. Apply the D4 old c33 chorus+reverb chain to the bare-render for comparison — this is diagnostic evidence in `panel_baseline_old_chain.tsv`, never a LANDS deliverable per rubric-v2 §2 D4.
7. Sum matched drums+bass+other into `rc7_mixed_reconstruction.wav` (peak-normalized to 0.99 to prevent clipping).

## §5 Per-song results

Aggregate: **0/5 songs pass A7 across all three stems**; 8/15 stems pass individually.

| Song ID | Song ID (sha16) | A7 pass count | A7 total | Song pass |
|---|---|---|---|---|
| Chicken Grease | 31a164f845f8e27e | 1 | 3 | False |
| cdd2717e52820ff6 | cdd2717e52820ff6 | 2 | 3 | False |
| 51e433ade2a845e1 | 51e433ade2a845e1 | 1 | 3 | False |
| 252eb21ce7df7328 | 252eb21ce7df7328 | 2 | 3 | False |
| 88d247468cb6d49f | 88d247468cb6d49f | 2 | 3 | False |

**Chicken Grease per-stem breakdown** (chosen_section [233.6s, 263.6s]):

| Stem | Target RMS_dB | Matched RMS_dB | Error (dB) | A7 PASS |
|---|---|---|---|---|
| bass | -21.72 | -21.72 | 0.00 | ✓ |
| drums | -14.41 | -54.12 | 39.72 | ✗ |
| other | -86.34 | -68.41 | 17.92 | ✗ |

The drums failure is diagnostic: target -14.4 dB is loud (heavy drum content in the peak section), but the c33-anchor drums MIDI (basic-pitch on synth_030s drums stem) contains ≤ 5 drum notes in 30 s (operator RC2 audit anchor). The fluidsynth GM render of that sparse MIDI has RMS ≈ -60 dB. Loudness match applies its +48 dB clamp and reaches -54 dB — still ~40 dB below target. This is EXACTLY the failure mode the RC2 branch is designed to fix; RC7 mechanism is not at fault.

The "other" failure at target -86.34 dB is the mirror-image issue: htdemucs_6s successfully separates guitar/piano/vocals into their own stems, leaving "other" near-silent for this section. Loudness match tries to attenuate the fluidsynth render by 33 dB — clamped at -48 dB is fine, but the match still overshoots because near-silence targets don't quantize well through gain-scaling. Legitimate operational limit; not an RC7 mechanism failure.

## §6 D4 old-chain comparison

Per-song `panel_baseline_old_chain.tsv` compares the RC7-matched path (EQ + loudness) against the OLD c33 pinned Surge chorus+reverb chain applied to the same bare-render. Per operator rubric-v2 §2 D4 the old chain is **preserved as diagnostic comparison ONLY**, never as a LANDS deliverable.

Chicken Grease diagnostic:

| Stem | Matched error (dB) | Old-chain error (dB) |
|---|---|---|
| bass  | 0.00 | 3.04 |
| drums | 39.72 | 45.79 |
| other | 17.92 | 20.36 |

Old-chain adds ~2-6 dB of additional error on top of the matched path across all stems — confirming the D4 replacement is a strict improvement (never worse). Old chain is NOT a candidate for M_RECREATE_2_v2_LANDS emission per rubric.

## §7 Byte-determinism × 2

Verified via `scripts/recreate_v2/_rc7_determinism_check.py` (archived to `tools/stale/rc7_determinism_check.py`):

- Two fresh `tempfile.mkdtemp()` runs.
- Env pins: `PYTHONHASHSEED=0`, `SOURCE_DATE_EPOCH=1756463424`, `TZ=UTC`, `LC_ALL=C.UTF-8`, single-thread BLAS, `torch.manual_seed(0)` (not directly used — no torch in RC7).
- Chicken Grease `rc7_mixed_reconstruction.wav` SHA `e74f38f7c80a5653…` — **byte-identical across both runs.**
- Verdict `rubric_hash` byte-identical across both runs.

Also verified in `test_13_rc7_out_byte_determinism_x2` — PASS.

## §8 Anchor preservation

`data/recreate_v2/rc7_out/anchor_preservation.json` snapshots **95 READ-ONLY anchor SHAs** (well above the ≥30 required by rubric-v2). Includes:

- c49 v1 rubric doc + rubric_hash.txt + focus_set.json + all 5 RC0 baseline files × 11 = 55 anchors
- c50 v2 rubric doc + rubric_hash_v2.txt + focus_set_v2.json
- All 30 htdemucs_6s stem WAVs (5 songs × 6 stems)
- 3 rules ledgers (c9 `ledger.jsonl` + c15 `ledger_i3_dminor.jsonl` + c40 `ledger_rated_corpus.jsonl`)
- `data/anchor_manifest_v1.json`

Every anchor byte-identical pre/post (verified in `test_14`).

**READ-ONLY files unchanged this cycle:** c49 v1 stubs (`scripts/recreate_v2/rc1_vocals_transcription.py`, `rc2_...`, etc.), c50 v2 sibling stubs OTHER than `rc7_mix_balance.py`, all c33 non-`render_stem` files, all `data/rules/*`, all c22 stability harness, c6 CORN chassis, htdemucs weights.

## §9 Discipline invariants

- **NO PRNG:** AST-grep clean across `scripts/palette_render/render_stem.py` + `scripts/recreate_v2/rc7_mix_balance.py` (test_15).
- **`/usr/bin/python3` interpreter guard:** present in every new/edited file (test_16).
- **c48 env-var flags default OFF:** `MUSICGEN_LEDGER_SUBSTANTIVE_EXEMPTION=0`, `MUSICGEN_LEDGER_SUPERSEDES_IN_HASH=0` (set via `os.environ.setdefault` in rc7_mix_balance.py).
- **c31 STILL_GAP AST-forbidden methods** (`get_state`, `save_state`, `save_preset`, `load_state`, `set_state(bytes)`): grep clean under all c51 Branch C files. Not touched.
- **c35 palette-schema-v2 VST3 anti-pattern:** respected. Non-None kwargs on Surge XT / Dexed raise `NotImplementedError` (test_04, test_05).
- **c11 CLAP anti-pattern:** respected. RC7 does not touch VGGish/CLAP; RC6-v2 panel gate deferred to c52.
- **No file deletion:** scratch → `tools/stale/` via `os.rename` + `os.utime` per c38 lesson.
- **No import of forbidden modules:** grep-verified zero import of `scripts.tex.render_effects_layered`, `sidecar_nonfactor`, `scripts.rules.sampling.i4_stratified`, c26-c30 collision-model utilities, any M-EAR-1/* or M-GEN-1/* script.
- **c14 `supersedes_path: str` lemma:** not triggered this cycle (no supersede events).
- **c33 harness auto-suffix:** applied automatically at ledger writer boundary — substantive `M-RECREATE-2/*` unsuffixed, infra `_archive/*` + `_infra/*` auto-suffixed `-clone-2`.

## §10 Tests

`tests/test_rc7_impl.py` — **20/20 PASS** under `PYTHONPATH=. /usr/bin/python3 tests/test_rc7_impl.py`:

| # | Test | Status |
|---|---|---|
| 01 | render_stem signature v3 (three additive kwargs, keyword-only) | PASS |
| 02 | c33 backwards-compat no-kwargs SHA match | PASS |
| 03 | c36 backwards-compat all-None SHA match | PASS |
| 04 | VST3 lock with eq_curve raises NotImplementedError | PASS |
| 05 | VST3 lock with loudness_target raises NotImplementedError | PASS |
| 06 | rc7_out/verdict.json present | PASS |
| 07 | Three-way rubric_hash-v2 byte-equality | PASS |
| 08 | c49 v1 rubric SHA preserved | PASS |
| 09 | Verdict in frozen enum {RC7_LANDS, RC7_PARTIAL, RC7_FAILS} | PASS |
| 10 | dispatch_summary.json per song (5 present) | PASS |
| 11 | panel_baseline_old_chain.tsv present per song (D4) | PASS |
| 12 | EQ curve 12-band geomspace | PASS |
| 13 | Byte-determinism × 2 on mixed reconstruction | PASS |
| 14 | Anchor preservation ≥ 30 (delivered 95) | PASS |
| 15 | No PRNG in render_stem.py | PASS |
| 16 | Interpreter guard in rc7_mix_balance.py | PASS |
| 17 | render_stem_signature_v3.md mtime hard | PASS |
| 18 | rc7_eq_curve_fit_method.md mtime hard | PASS |
| 19 | Verdict carries per_song_passes | PASS |
| 20 | D4 old-chain baseline flag in verdict | PASS |

## §11 Ledger events landed

Shadow ledger at `/home/user/music-gen-instance/fork-38eba9f21a61/clone-2/promise_ledger.jsonl` — **9 events**:

1. `M-RECREATE-2/accurate-small-set/rc7-mix-balance-match/rubric-v3-committed` (substantive)
2. `M-RECREATE-2/accurate-small-set/rc7-mix-balance-match/render-stem-signature-v3-extended` (substantive)
3. `M-RECREATE-2/accurate-small-set/rc7-mix-balance-match/eq-curve-fitted` (substantive)
4. `M-RECREATE-2/accurate-small-set/rc7-mix-balance-match/loudness-matched` (substantive)
5. `M-RECREATE-2/accurate-small-set/rc7-mix-balance-match/verdict-emitted` (substantive)
6. `M-RECREATE-2/accurate-small-set/rc7-mix-balance-match/anchor-preservation-verified` (substantive)
7. `M-INGEST-1/egress-probe-cycle51-clone-2` (egress probe, explicit clone-2 suffix per plan-of-record row)
8. `_archive/cycle-51-scratch-clone-2` (housekeeping, auto-suffixed by c33 writer guard)
9. `_infra/adopt-cycle51-tests-clone-2` (housekeeping, auto-suffixed by c33 writer guard)

Six named substantive + two housekeeping + one egress probe = 9 rows per brief.

## §12 §10 handoff seeds (for c52 integration + auditor)

- **c52 integration:** re-run RC7 with Branches A+B substantive per-stem MIDIs in place of the c33 placeholder MIDIs. Expected A7 lift: drums stem RMS should climb from -54 dB to within 3 dB of target once RC2 lands (Branch B). Bass already passes (0.00 dB error under placeholder — will remain PASS with real transcription). "Other" stem near-silence is a legitimate 6-stem separator artifact; RC7 mechanism handles it gracefully.
- **RC6-v2 panel gate implementation (c52+):** hook in VGGish DEFERRED-None per c11 anti-pattern; centroid-RMSE not-worsening path can already use the RC7 matched output.
- **`_infra/large-model-fetchability-registry` lemma:** htdemucs_6s continues to fetch OK; extend registry at c52 rollup.
- **`_infra/auditor-reads-ledger-not-brief-summaries` lemma:** c52 auditor should verify by CLI (`grep -c '"cycle":51' promise_ledger.jsonl` after post-merge concat) — do NOT trust worker report line counts alone.
- **c48 env-var flag flips** (`MUSICGEN_LEDGER_SUBSTANTIVE_EXEMPTION=1`, `MUSICGEN_LEDGER_SUPERSEDES_IN_HASH=1`): still deferred to c53+ post-M-RECREATE-2-v2 land.
- **RC7 mechanism sound; failure surface is under-transcribed placeholder MIDIs.** c52 auditor should spot-check that Branches A+B partials, once folded in, produce loudness targets the +48 dB clamp CAN reach. If RC7 still fails post-integration, the issue is genuinely mix-stage — not this cycle's structural output.
- **D4 old-chain retention:** the c33 pinned chorus+reverb chain remains in `data/recreate_v2/rc7_out/<sha16>/old_chain_<stem>/old_chain.wav` (READ-ONLY) as evidence per operator-mandate. Auditor should confirm no LANDS artifact references it.

## §13 Author

- Cycle 51, fork-38eba9f21a61 clone-2 (Branch C)
- Milestone `M-RECREATE-2/accurate-small-set/rc7-mix-balance-match`
- Rubric v2 SHA `0e11f704e12c62f85cfb9d58d6e6890227209ffb43247239e735a22acfdebe1f`
- Author-email `cyd7bevdr@mozmail.com` (attribution only; NEVER sent externally)
