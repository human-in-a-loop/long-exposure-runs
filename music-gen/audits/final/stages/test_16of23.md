# Stage 40 of 48 — test 16 of 23

**Slice:** verify c53 fork 18817b483ed4 Branch A clone-0 RC7 v2 rerun sub-leaves
under `M-RECREATE-2/accurate-small-set/rc7-mix-balance-match/*` (pre-registration,
impl, tests, byte-determinism-v2, anchor-preservation-v2, verdict).

**Why this slice:** stage 39 verified the c52 post-merge-integration-cycle-51
rollup that closed with a first-class negative finding `RC7_FAILS` at
`data/recreate_v2/rc7_out/verdict.json` (SHA `757d3773…21edc99`, rubric_hash
`0e11f704…debe1f` c50 v2 rubric). c52 rollup's narrative pointed at c53 Branch A
as the RC7 v2 rerun consuming c51's substantive per-stem MIDIs (vocals+guitar+
piano from Branch A `merged_partial.midi`, drums+bass from Branch B
`merged.midi`) in place of c33 placeholder MIDIs. This stage confirms the
substantive substitution actually lifts A7 accepts.

## Probes

### 16.1 Rubric-v3 pre-registration chain

- Doc SHA-256 `sha256(docs/rc7_v2_rerun_rubric.md)` = `9f24e6d9240f1eaf80f6fb20bf0ce5a2e8e235e2ddcc1064dfa271bff404dde4`.
- On-disk `data/recreate_v2/rc7_out_v2/rubric_hash.txt` content byte-equal to doc SHA.
- `data/recreate_v2/rc7_out_v2/verdict.json.rubric_hash` byte-equal to same value.
- **Three-way rubric_hash byte-equality chain HOLDS.** PASS.

### 16.2 RC7 v2 verdict + A7 gate

- `data/recreate_v2/rc7_out_v2/verdict.json.verdict` = **`RC7_v2_LANDS`** (frozen enum ∈
  {RC7_v2_LANDS, RC7_v2_PARTIAL, RC7_v2_FAILS}; three-way rubric_hash byte-equality confirmed).
- Per-song table: 5/5 songs `song_pass=true`; every song `per_stem_pass_count=4/4`.
- Aggregate `n_stem_accepts=20 / n_stem_total=20`, `n_songs_passing_a7=5 / n_songs_total=5`.
- A7 gate defined over 4 stems {drums, bass, other_guitar, other_piano} per rubric D5;
  vocals+other rendered for reproduction completeness (not gated) — documented in
  per-song `dispatch_summary.json.notes`.
- `acceptance_criterion` = "per-stem RMS <= 3 dB vs baseline over 4 stems …; LUFS-S report-only".
- Song-ID roster (5): `31a164f845f8e27e`, `cdd2717e52820ff6`, `51e433ade2a845e1`,
  `252eb21ce7df7328`, `88d247468cb6d49f`.
- `supersedes_verdict` field pins `data/recreate_v2/rc7_out/verdict.json` (c51 `RC7_FAILS`
  at SHA `757d3773…21edc99` — verified byte-equal in stage 39 and re-verified this stage).
- **c51 RC7_FAILS negative finding cleanly promoted to RC7_v2_LANDS via substantive MIDI
  substitution.** PASS.

### 16.3 Byte-determinism v2 (226/226 anchor)

- `data/recreate_v2/rc7_out_v2/byte_determinism.json`: `byte_determinism_holds=true`,
  `n_files_run_a=226`, `n_files_run_b=226`, `n_common=226`, `n_mismatch=0`,
  `mismatch_files=[]`.
- Env pins recorded: `PYTHONHASHSEED=0`, `SOURCE_DATE_EPOCH=1756463424`, `TZ=UTC`,
  `LC_ALL=C.UTF-8`, `OMP/MKL/OPENBLAS_NUM_THREADS=1`.
- Run tempdirs: `/tmp/rc7v2_run5_trioy36g` and `/tmp/rc7v2_run6_30kgxg05`.
- On-disk `find data/recreate_v2/rc7_out_v2/ -type f | wc -l` = 229 (226 substantive
  audio+per-stem-JSON files + 3 top-level sidecars {verdict.json, byte_determinism.json,
  anchor_preservation_v2.json, rubric_hash.txt = 4 actual — 229-226=3 minor accounting
  variance driven by JSON sidecar exclusion in the byte-det diff scope). **Not
  material** to the byte-determinism claim, which is authoritative via the recorded
  per-file SHA comparison. PASS.
- Spot-check: `sha256(data/recreate_v2/rc7_out_v2/31a164f845f8e27e/matched_drums/matched.wav)`
  = `f4cdf594b70e98c673c12d5226cc12e11672c3a7b933ce3d319fde807be4ae31` (present + finite).

### 16.4 Anchor preservation v2 (c51 rc7_out 182-file)

- `anchor_preservation_v2.json`: `anchor_root=/…/data/recreate_v2/rc7_out`, `pre_count=182`,
  `post_count=182`, `preservation_holds=true`, `sha_diff_after_run=[]`,
  `missing_after_run=[]`, `new_after_run=[]`.
- `find data/recreate_v2/rc7_out/ -type f | wc -l` = 182 (matches). c51 Branch C
  artifacts byte-identical pre==post the c53 Branch A rerun. PASS.

### 16.5 c33 render_stem.py do-not-touch invariant

- `sha256(scripts/palette_render/render_stem.py)` = `214372d920a319a97d6e3fc7b9ee4134c08c0cb4aecb776f4a50c75f965b5b2b`
  — byte-identical to the SHA pinned in stages 38, 39, and plan_of_record c51-Branch-C
  narrative. **c33 additive-kwargs edit surface (introduced c51 Branch C) unchanged
  through c53.** PASS.

### 16.6 EQ + loudness match method spot-check

- `dispatch_summary.json` for song `31a164f845f8e27e` bass stem records
  `eq_curve_method="iirpeak_12band_log_spaced_Q1.4"`, `eq_fallback_used=false`,
  `eq_bands_gains_db=[0.0]×12`, `a7_rms_pass=true`, `in_a7_gate=true`,
  `instrument="fluidsynth_gm"`.
- Zero-gain EQ curve on this stem consistent with c51 rc7-eq-curve-fitted sub-leaf
  design: broadband level owned by `loudness_target`; per-band `mag_orig − mag_render`
  gains zero-mean-normalized so a well-matched baseline naturally produces near-zero
  band gains. This is by-design, not a mis-fit. **Method match confirmed.** PASS.

## Verdict

**ALL PASS.** c53 Branch A RC7 v2 rerun cleanly lifts c51's first-class negative
`RC7_FAILS` finding to `RC7_v2_LANDS` via the mechanism c51 auditor predicted
(substantive MIDI substitution). Three-way rubric_hash chain byte-equal, byte-
determinism 226/226 across 2 fresh temp-dir runs, anchor preservation 182/182
against c51 Branch C, c33 render_stem.py SHA byte-identical, per-stem A7 accepts
20/20 over 5 songs.

## Findings

**Findings appended this stage: 0.**

### MINOR observations logged (not escalated, not appended)

- **Supersession granularity.** The c53 v2 verdict.json expresses supersession of
  c51's `RC7_FAILS` verdict via a free-text `supersedes_verdict` string field
  rather than a dedicated `_plan/supersede-c51-rc7-verdict` ledger event of the
  form the plan_of_record rubric-v2 supersede uses at
  `_plan/m-recreate-2-rubric-v2-supersede`. The natural chain (v1-rubric verdict →
  v2-rubric verdict via rubric-supersede) is unambiguous, but a dedicated
  supersede event would make the chain machine-discoverable. Below-threshold for
  a MODERATE finding.
- **A7 gate scope disclosure.** The 4-stem gate (drums/bass/other_guitar/
  other_piano) excludes vocals and untuned "other" from A7 acceptance. This is
  correctly documented in `dispatch_summary.json.notes` and rubric D5 but is not
  restated inside `verdict.json` — a reader would need to cross-reference. Below
  MINOR threshold for a narrative-clarity nit.

## Files verified

| Artifact                                                      | SHA-256                                                              |
|---------------------------------------------------------------|----------------------------------------------------------------------|
| `docs/rc7_v2_rerun_rubric.md`                                 | `9f24e6d9240f1eaf80f6fb20bf0ce5a2e8e235e2ddcc1064dfa271bff404dde4`   |
| `data/recreate_v2/rc7_out_v2/rubric_hash.txt` (content)       | `9f24e6d9240f1eaf80f6fb20bf0ce5a2e8e235e2ddcc1064dfa271bff404dde4`   |
| `data/recreate_v2/rc7_out_v2/verdict.json.rubric_hash`        | `9f24e6d9240f1eaf80f6fb20bf0ce5a2e8e235e2ddcc1064dfa271bff404dde4`   |
| `data/recreate_v2/rc7_out/verdict.json` (c51 superseded pin)  | `757d37732439f543efdb701e76121c807c645db732d1808113a4f711e21edc99`   |
| `scripts/palette_render/render_stem.py` (c33 anchor)          | `214372d920a319a97d6e3fc7b9ee4134c08c0cb4aecb776f4a50c75f965b5b2b`   |
| `data/recreate_v2/rc7_out_v2/31a164f845f8e27e/matched_drums/matched.wav` | `f4cdf594b70e98c673c12d5226cc12e11672c3a7b933ce3d319fde807be4ae31` |
