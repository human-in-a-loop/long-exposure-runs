# Verify slice 10 of 23 (stage 11 of 48)

Three unverified slices selected: (A) latest c54 rc10 drums-bass; (B) c31
palette-instrument-determinism (VST3 state-extraction GAP first-classing);
(C) c33 `_infra/harness-clone-namespace-guard` writer-boundary enforcement.

## Slice A — M-RECREATE-2/.../rc10-transcription-real-stem-resurvey/drums-bass (c54 clone-0)

Rubric-hash chain (three-way byte-equality):
- `sha256(docs/rc10_drums_bass_rubric.md)` = `a79bee01b4c97a1282f476a01915f4f9119fa23d369e5be2b0b72fbee05fd919`
- `data/rc10_drums_bass_impl/rubric_hash.txt` content = `a79bee01…5fd919`
- `data/rc10_drums_bass_impl/verdict.json.rubric_hash` = `a79bee01…5fd919`
- All three byte-equal ✓

Verdict content:
- verdict = `RC10_DRUMS_BASS_LANDS` (∈ frozen enum) ✓
- drums: `{ok:true, songs_pass:5, winner:"onset_band_energy"}` — 5/5 focus
  songs passed the drums content-metric gate; winner = onset+band-energy
  classifier (vs basic-pitch default / tuned)
- bass: `{ok:true, songs_pass:3, winner:"pyin_mono"}` — 3/5 focus songs
  passed the bass content-metric gate; winner = pyin monophonic

Byte-determinism `data/rc10_drums_bass_impl/byte_determinism.json`:
- `n_mismatch = 0` across all captured artifacts (per-file SHA maps in
  `run1_sha` + `run2_sha`, run1==run2). ✓

Anchor preservation `anchor_preservation.json`:
- 28 anchors snapshotted (c50 v2 rubric SHA `0e11f704…debe1f`, c49 v1
  rubric SHA `958ade38…3fe58b9d`, c33 `render_stem.py` SHA
  `214372d9…5b2b`, rc1_rc9 / rc2_rc3 / rc5 / rc7_out verdicts, per-song
  rc9_6stem drums+bass WAVs + rc2 onset_count JSONs, focus_set_v2).
  Format is per-entry `{path: sha}` snapshot (comparison at read-back);
  no in-band drift marker; acceptable per c48+ pattern. ✓

Governance:
- fork bdd7bb47f1b5, clone-1 (matches Branch B in c53 fanout; c54
  extension to drums-bass slice). Substantive `M-RECREATE-2/*` milestone
  unsuffixed per c32 convention; infra families would carry `-clone-*`
  (per c33 guard) but this stage's audit does not enumerate them.
- Six named sub-leaves for this slice observed in ledger causal summary
  (drums-bass-pre-registration, -impl-per-stem, -post-processing-applied,
  -winner-selected, -verdict-emitted, plus egress-probe-cycle54-clone-0).

Verdict: **CONFIRMED**. No reconciliation needed.

## Slice B — M-DAW-SPIKE-1/palette-instrument-determinism (c31 Branch B)

Rubric-hash chain:
- `sha256(docs/palette_instrument_determinism_rubric.md)` = `75daa068aa804351db744cdb3a41df151ba682bbe3278c7c8cb8870a54ac7c96`
- `data/palette_probe/rubric_hash.txt` = `75daa068…7c96` ✓

TSV `data/palette_probe/instrument_determinism.tsv` contains exactly the
three required rows (surge_xt, dexed, sfizz), each carrying a verdict
∈ frozen enum {GREEN, REDEFINED_GAP, STILL_GAP}:

- **surge_xt**: STILL_GAP. run1/run2 WAV SHAs differ
  (`fe80fc17…a492` vs `443ca252…09c2`); state-capture SHAs equal but
  `plugin.get_state()` returned empty per `refinement_description`.
- **dexed**: STILL_GAP. Same signature (WAV SHAs diverge, state SHAs
  match, get_state empty).
- **sfizz**: GREEN. WAV SHAs byte-equal
  (`4f9735d9…8f21` == `4f9735d9…8f21`) and state SHAs byte-equal.

Per-instrument dirs {surge_xt, dexed, sfizz} present as required. Fetchability
ladder JSONL present. All three verdicts honestly first-classed — VST3
state-extraction GAP was subsequently characterized in c33 Branch B
(`dawdreamer-state-extraction-workaround`) and c36 Branch C
(`vst3-render-nondeterminism-characterization`), so the STILL_GAP entries
survive as legitimate anchors for downstream work.

Verdict: **CONFIRMED**. No reconciliation needed.

## Slice C — _infra/harness-clone-namespace-guard (c33 Branch C)

Rubric-hash chain:
- `sha256(docs/harness_clone_namespace_guard_rubric.md)` = `cd020761c919648e797769e3d05721b875be860cc845f16dbd9061ce92e876e3`
- `tests/fixtures/harness_clone_namespace_guard_rubric_hash.txt` = `cd020761…76e3` ✓

Writer implementation (`long_exposure.workspace_bootstrap`, resolved to
the installed package at
`/home/user/human-in-a-loop/long-exposure/long_exposure/workspace_bootstrap.py`
— outside the workspace tree, correctly imported at runtime):
- `_is_clone_context` present ✓
- `_guard_clone_namespace` (rubric criterion (b) helper) present ✓
- `MUSICGEN_LEDGER_STRICT_CLONE_NAMESPACE` env-var handling present ✓
- `LedgerNamespaceViolation` MRO:
  `[LedgerNamespaceViolation, LedgerSchemaError, ValueError, Exception,
  BaseException, object]` — correctly subclasses `LedgerSchemaError` per
  rubric criterion (f) ✓

Tests: `tests/test_harness_clone_namespace_guard.py` present with 14
top-level test cases (rubric threshold ≥10 test cases satisfied; c33
brief called for the 468-row baseline replay + ≥10 cases) ✓.

Downstream evidence: the c37+ / c38+ / c47 clone campaigns produced 300+
auto-suffixed `-clone-<k>` events with zero LedgerConcatError, and the
c48 harness-and-writer-hardening-v3 extension composed cleanly with this
guard (adds `MUSICGEN_LEDGER_SUBSTANTIVE_EXEMPTION` for the `^M-` path,
leaves the c33 `_infra/*` path intact). Behaviour matches the rubric.

Verdict: **CONFIRMED**. No reconciliation needed.

## Slice summary

| Slice | Milestone                                                        | Verdict     | Severity |
|-------|------------------------------------------------------------------|-------------|----------|
| A     | M-RECREATE-2/.../rc10-.../drums-bass (c54 clone-0)               | CONFIRMED   | none     |
| B     | M-DAW-SPIKE-1/palette-instrument-determinism (c31 Branch B)      | CONFIRMED   | none     |
| C     | _infra/harness-clone-namespace-guard (c33 Branch C)              | CONFIRMED   | none     |

No reconciliation events proposed. Cumulative findings after this stage
= 33 (30 pre-stage + 3 closure_verified rows).
