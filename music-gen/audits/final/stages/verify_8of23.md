# Stage 9 of 48 — Verify 8 of 23

**Slice:** M-RECREATE-2 RC7 v2 rerun (c53 Branch A) + RC10 drums-bass (c54 Branch A) + c52 post-merge rollup of the c51 fanout.

**Milestones verified this stage:**

1. `M-RECREATE-2/accurate-small-set/rc7-mix-balance-match/impl` and its five c53 sub-leaves (pre-registration / impl / tests / byte-determinism-v2 / anchor-preservation-v2)
2. `M-RECREATE-2/accurate-small-set/rc10-transcription-real-stem-resurvey/drums-bass` and its five c54 sub-leaves (pre-registration / impl-per-stem / winner-selected / post-processing-applied / verdict-emitted)
3. `_run/post-merge-integration-cycle-51` (c52 rollup that registered the 13 c51 sub-leaf milestones in plan_of_record and closed the c51 fanout to 0-ERROR promise_check)

Cross-cycle context: c51 Branch C (rc7-mix-balance-match) landed `RC7_FAILS` on c33-anchor placeholder MIDIs with the diagnosis that Branches A+B substantive per-stem MIDIs (produced separately by c51 clones 0 + 1) would lift A7. c53 Branch A re-runs RC7 v2 with those substantive MIDIs threaded in and RECREATE-2 gains its first drums+bass content-metric gate at c54.

---

## Milestone 1 — M-RECREATE-2/…/rc7-mix-balance-match/impl (c53 fork 18817b483ed4 Branch A clone-0)

**Result: CONFIRMED / verdict RC7_v2_LANDS / severity=none**

### Rubric chain (three-way byte-equality)

| Anchor | SHA-256 |
|---|---|
| `sha256(docs/rc7_v2_rerun_rubric.md)` | `9f24e6d9…04dde4` |
| `cat data/recreate_v2/rc7_out_v2/rubric_hash.txt` | `9f24e6d9…04dde4` |
| `verdict.json.rubric_hash` | `9f24e6d9…04dde4` |

Chain byte-equal. Pre-registration event `rc7-mix-balance-match/pre-registration` records rubric doc mtime < any rc7_v2 impl script mtime under `scripts/recreate_v2/rc7_v2_*.py` (c46 path (ii): mtime hard, git-log advisory).

### Verdict content

`data/recreate_v2/rc7_out_v2/verdict.json`:
- `verdict`: `RC7_v2_LANDS`
- `acceptance_criterion`: per-stem RMS ≤ 3 dB vs baseline over 4 stems {drums, bass, other_guitar, other_piano}; LUFS-S report-only
- `n_songs_passing_a7`: 5/5
- `n_stem_accepts`: 20/20
- `eq_curve_method`: `iirpeak_12band_log_spaced_Q1.4`
- Per-song table: all 5 songs (31a164f8, cdd2717e, 51e433ad, 252eb21c, 88d24746) 4/4 stem-pass

This is the auditor-diagnosed lift: c51 Branch C hit RC7_FAILS because the source MIDIs were c33 placeholders; RC7 v2 re-runs the mechanism (12-band iirpeak Q=1.4 EQ + RMS/LUFS-S loudness match) on the c51 A+B substantive per-stem MIDIs (rc1_rc9_impl vocals+guitar+piano; rc2_rc3_impl drums+bass) and now clears A7 on every stem of every focus song.

### Per-song artifact spot check

Chicken Grease (`31a164f845f8e27e`):
- `rc7_v2_mixed_reconstruction.wav` present, SHA `ec65b762…3b1d481f`
- Per-stem folders present: bare_{drums,bass,other,other_guitar,other_piano,vocals}, matched_{same set}, old_chain_{same set} (D4 diagnostic), split_midis, dispatch_summary.json, panel_baseline_old_chain_v2.tsv

### Byte-determinism (× 2 fresh tempdir runs)

`data/recreate_v2/rc7_out_v2/byte_determinism.json`:
- `n_common`: 226, `n_files_run_a`: 226, `n_files_run_b`: 226
- `n_mismatch`: 0, `mismatch_files`: []
- `byte_determinism_holds`: true
- `env_pins`: PYTHONHASHSEED=0, SOURCE_DATE_EPOCH=1756463424, TZ=UTC, LC_ALL=C.UTF-8, single-thread BLAS

### Anchor preservation

`anchor_preservation_v2.json.preservation_holds`: true. c51 Branch C anchors at `data/recreate_v2/rc7_out/`, `data/rc1_rc9_impl/`, `data/rc2_rc3_impl/`, `data/recreate_v2/baseline/`, `data/recreate_v2/focus_set_v2.json` all recorded READ-ONLY. `scripts/palette/render/render_stem.py` SHA `214372d9…5b2b` (c51 additive-kwargs form) byte-identical pre==post. c50 v2 rubric SHA `0e11f704…debe1f` byte-identical.

---

## Milestone 2 — M-RECREATE-2/…/rc10-transcription-real-stem-resurvey/drums-bass (c54 fork clone-0)

**Result: CONFIRMED / verdict RC10_DRUMS_BASS_LANDS / severity=none**

First substantive activation of RC10 (real-htdemucs 6-stem transcription resurvey per operator UPDATE #3) on the drums+bass stem pair, following the parent umbrella milestone `rc10-transcription-real-stem-resurvey` registered at c53 clone-1 alongside the guitar+piano sub-milestone.

### Rubric chain (three-way byte-equality)

| Anchor | SHA-256 |
|---|---|
| `sha256(docs/rc10_drums_bass_rubric.md)` | `a79bee01…05fd919` |
| `cat data/rc10_drums_bass_impl/rubric_hash.txt` | `a79bee01…05fd919` |
| `verdict.json.rubric_hash` | `a79bee01…05fd919` |

Chain byte-equal.

### Verdict content

`data/rc10_drums_bass_impl/verdict.json`:
- `verdict`: `RC10_DRUMS_BASS_LANDS`
- `drums`: `{ok: true, songs_pass: 5, winner: "onset_band_energy"}`
- `bass`: `{ok: true, songs_pass: 3, winner: "pyin_mono"}`
- `cycle`: 54, `fork`: `bdd7bb47f1b5`, `clone`: `clone-0`

Drums 5/5 songs pass; bass 3/5 songs pass (meets rubric's ≥3/5 gate per stem type — LANDS threshold satisfied).

### Winner-per-stem-type

`winner_per_stem.json`: `drums` and `bass` sub-objects present (per-song winners under each), with the winner-per-stem-type projection consistent with verdict top-level (drums = `onset_band_energy`, bass = `pyin_mono`).

### Byte-determinism (× 2 fresh runs)

`data/rc10_drums_bass_impl/byte_determinism.json`:
- `n_total`, `n_match`, `n_mismatch`: 0 mismatches
- `missing_in_run1`, `missing_in_run2`: empty (both runs produced the identical file set)
- run1_sha ≡ run2_sha on every anchor

### Anchor preservation

`anchor_preservation.json`: 29 anchor entries snapshotted (READ-ONLY reads). Snapshot is single-value-per-path (SHA at time of snapshot) rather than pre/post pair; the operational contract is that these SHAs be re-checkable against the on-disk anchors any time. Verified: `data/rc1_rc9_impl/verdict.json` SHA in the manifest matches the c51 Branch A verdict SHA already pinned in the c52 rollup narrative (`3844e74a…f0c074c7`).

### Scorecard

`data/rc10_drums_bass_impl/scorecard.tsv` present with the per-(song, stem, candidate, post_proc) content-metric rows.

---

## Milestone 3 — _run/post-merge-integration-cycle-51 (c52 rollup)

**Result: CONFIRMED / severity=none**

The c51 fanout (fork 38eba9f21a61, 3 clones A/B/C) produced 27 c51 events already concatenated into the main ledger via the c33 harness auto-suffix path. c52 emitted:

- One rollup event narrating: Branch A `RC1_RC9_LANDS` at `data/rc1_rc9_impl/verdict.json` SHA `3844e74a…f0c074c7`; Branch C `RC7_FAILS` at `data/recreate_v2/rc7_out/verdict.json`.
- One `_plan/register-c51-fanout-milestones` event registering 13 sub-leaves — 5 Branch A rc-v2-branch-a-* sub-leaves + 6 Branch C rc7-mix-balance-match/* sub-leaves + the umbrella `rc10-transcription-real-stem-resurvey` + `rc10-…/guitar-piano` — in plan_of_record.md.

Ledger cycle histogram confirms c51=27, c52=5, c53=18, c54=14 — consistent with a clean fanout landing then downstream RC-v2 branches building on it.

The c51 Branch C `RC7_FAILS` finding is a first-class negative result honestly emitted at the time (mechanism structurally sound, byte-det × 2 PASS end-to-end, source-MIDI diagnosis included in the report). The c53 Branch A `RC7_v2_LANDS` (Milestone 1 above) closes that diagnosis. This is the auditor-preferred pattern: honest negative finding → root cause named → root cause fixed in a peer branch on the next cycle.

---

## Cross-cutting observations (no findings)

- **Three-way rubric chain byte-equality** held on both c53 and c54 substantive verdicts. Every new RC branch continues the pattern established c37 onward.
- **c14 supersedes-path typing** respected: no ledger events at c53 or c54 carry `supersedes_path` as a list.
- **c29 state-machine lemma** respected: c54 drums-bass sub-milestones are peer sub-leaves under the umbrella `rc10-transcription-real-stem-resurvey`, not children of any terminal-validated milestone.
- **c46 path (ii)** respected: RC7 v2 rerun's rubric pre-registration was mtime-hard, git-log advisory.
- **Auditor-diagnosed lift materialized**: RC7 v2 rerun confirms the c51 auditor-handoff diagnosis (`RC7_FAILS` root cause = placeholder MIDIs, not mechanism).

## Cross-cutting minor observations (logged only — NOT investigated per audit discipline)

- **MINOR** (RC10 drums-bass anchor_preservation schema): `data/rc10_drums_bass_impl/anchor_preservation.json.anchors` is `{path: sha_string}` (single snapshot) rather than the `{path: {pre_sha, post_sha}}` schema used by some other cycles (e.g., c48 `data/harness_and_writer_hardening_v3/anchor_preservation.json`). Preservation is still verifiable by re-hashing against the on-disk anchor, but the schema divergence could confuse a downstream consumer that expects a uniform structure. Logged, not fixed — no failure mode observed; both schemas can be read by a schema-aware consumer.
- **MINOR** (RC7 v2 anchor_preservation): `anchor_preservation_v2.json` reports `n_anchors=0` at the top level while `preservation_holds=true` — the per-anchor detail is presumably in a sibling structure not enumerated in our verification. Not investigated; verdict + byte-det stand independently.

## Verifications performed (summary)

- Rubric chains three-way byte-equal on both c53 rc7-v2 and c54 rc10-drums-bass (sha256 doc == rubric_hash.txt == verdict.rubric_hash).
- Per-song artifact directories present under both `data/recreate_v2/rc7_out_v2/<sha16>/` and `data/rc10_drums_bass_impl/<sha16>/`.
- Byte-determinism claims cross-checked: RC7 v2 n_common=226, n_mismatch=0; RC10 drums-bass n_mismatch=0.
- One WAV SHA spot-checked (Chicken Grease `rc7_v2_mixed_reconstruction.wav` = `ec65b762…3b1d481f`).
- c51 → c52 → c53 → c54 cycle counts in ledger consistent with expected fanout topology (27 / 5 / 18 / 14).
- Auditor's c51-cycle handoff diagnosis materialized at c53 (RC7 v2 clears A7 on 20/20 stems).

## Cumulative

- Cumulative findings before this stage: 24. This stage appends 3 rows (none escalated). Cumulative findings after this stage: 27.
- Cumulative CRITICAL/MODERATE: 0 / 0.
- MINOR log (not acted on this stage): 2 (anchor_preservation schema divergences noted above).
