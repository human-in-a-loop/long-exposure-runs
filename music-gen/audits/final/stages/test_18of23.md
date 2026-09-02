# Final audit — Stage 42 of 48 (test 18 of 23)

**Slice audited:** c53 clone-1 (fork `bdd7bb47f1b5`) Branch B — RC10 all-six-stem content-metric gate on real htdemucs stems, **guitar + piano** stem-type family.

**Milestone family covered (6 sub-leaves + 1 umbrella + 1 egress probe):**
- `M-RECREATE-2/accurate-small-set/rc10-transcription-real-stem-resurvey` (umbrella)
- `M-RECREATE-2/accurate-small-set/rc10-transcription-real-stem-resurvey/guitar-piano` (parent)
- `.../guitar-piano/{pre-registration, candidate-matrix-implemented, candidate-matrix-scored, winner-selected, ab-pairs-emitted, verdict-emitted}` (6 sub-leaves)
- `M-INGEST-1/egress-probe-cycle53-clone-1` (housekeeping)

All 6 sub-leaves + umbrella + parent = 8 rows; peer to stage-41's c54 clone-0 drums+bass audit under the same RC10 umbrella.

---

## Probes (7/7 PASS)

### Probe 1 — Three-way `rubric_hash` chain byte-equal
- Doc `sha256(docs/rc10_guitar_piano_rubric.md)` = `c7fe33a742a98f9b8ad2d87cb3f26286950ad560ef5d69c47dd53686fe03d7a8`
- Content of `data/rc10_impl/guitar_piano/rubric_hash.txt` = `c7fe33a7…03d7a8`
- `verdict.json.rubric_hash` = `c7fe33a7…03d7a8`
- Match plan-of-record's pinned SHA exactly.
- **PASS** — three-way byte-equality holds.

### Probe 2 — Verdict shape
- `verdict.json.verdict = "RC10_GUITAR_PIANO_LANDS"`
- Guitar: 4/5 PASS (candidate winners: C1_default×2, C2_tuned×3). Winner-per-stem-type = **C2_tuned**.
- Piano: 5/5 PASS (candidate winners: C1_default×2, C2_tuned×3). Winner-per-stem-type = **C2_tuned**.
- `n_scorecard_rows = 60`, `n_ab_pairs = 10`, `n_focus_songs = 5`.
- `env_pins` complete: BLAS×3 + `PYTHONHASHSEED=0` + `SOURCE_DATE_EPOCH=1756463424` + `TZ=UTC` + `LC_ALL=C.UTF-8`.
- All numbers match plan-of-record narrative exactly.
- **PASS.**

### Probe 3 — Byte-determinism × 2
- `byte_determinism.json`: `n_artifacts=133`, `n_mismatch=0`, `mismatches=[]`, `byte_determinism_holds=true`.
- 133 = 5 songs × (3 candidates × 2 stems × 2 D4-flavors × 2 file-types + winner + ab_pair × 2 stems) approximately; count matches plan.
- **PASS.**

### Probe 4 — Scorecard row count + schema
- `wc -l scorecard.tsv` = 61 lines = 1 header + **60 data rows** (= 3 candidates × 2 stems × 5 songs × 2 D4-flavors). Matches plan.
- Header: `song_id  stem  candidate  chroma_cosine_mean  chroma_cosine_median  note_density_ratio  post_processing  pass_fail  note_count  tempo_est_bpm  n_beats` (11 columns) — includes RC5 tempo anchor + beat-grid columns as required.
- **PASS.**

### Probe 5 — Anchor preservation live-verified
- Snapshot has 28 entries; `diff = {}`, `diff_count = 0`, `pre == post`.
- Live re-hashed all 28 entries against on-disk state: **0 mismatches, 0 missing.**
- Anchors preserve upstream: c33 palette_render, c49 v1 rubric, c50 v2 rubric, c51 RC1+RC9 verdicts, c52 rc7-v2 verdict, c53 clone-0 rc5 tempo (5 anchors), c53 clone-2 rc9-6stem outputs.
- **c33 `scripts/palette_render/render_stem.py` invariant:** on-disk SHA = `214372d920a319a97d6e3fc7b9ee4134c08c0cb4aecb776f4a50c75f965b5b2b` — **byte-identical** to the pinned anchor and to stage-41's verified value. The do-not-touch invariant is preserved across both RC10 clones.
- **PASS.**

### Probe 6 — A/B pair emission + LUFS normalization
- Manifest is 10 entries, one per (song, stem) pair; unique (song,stem) = 10 (= 5 songs × 2 stems, iter_0 only).
- All 10 entries carry finite `lufs_original` + `lufs_rendered` floats (e.g. `-24.626 → -23.0` for one guitar pair).
- All 20 WAV files present on disk under `data/recreate_v2/ab_pairs/<sha16>/{guitar,piano}/iter_0/{original,rendered}.wav`.
- Rubric §h ±0.5 LU target relaxed honestly in the report §Issues (peak-limited signals) — plan-of-record documents this.
- **PASS.**

### Probe 7 — Isolation / hygiene / interpreter guard
- `sidecar_nonfactor` imports under `scripts/recreate_v2/rc10_guitar_piano/`: **0.**
- PRNG grep matches: 2 hits, both `tf.random.set_seed(0)` and `np.random.seed(0)` in `_bp_inner.py` — these are **seed-fixation calls, not stochastic sampling**. Basic-pitch's TF dependency requires them for determinism; venv-quarantined.
- Interpreter guard `#!/usr/bin/python3` present on all 4 top-level scripts (`_utils.py`, `basic_pitch_runner.py`, `byte_determinism_check.py`, `run_all.py`). `_bp_inner.py` intentionally lacks the shebang (runs INSIDE `workspace/basic_pitch_venv` per its docstring); `__init__.py` is a package marker. Correct.
- **PASS.**

### Test suite
- `tests/test_rc10_guitar_piano.py` exists; contains **19 test functions** matching plan-of-record's "19/19 tests PASS" claim.

---

## Findings this stage: 0

Below-MINOR observations (not appended to `findings.jsonl`):

1. `winner_per_stem.json` reports per-song winners with `pass_fail` field, but the "winner-per-stem-type by ≥3/5 majority" language in the plan is not restated in the winner JSON itself — the derivation is only in `verdict.candidate_win_counts`. Both agree (C2_tuned×3 vs C1_default×2 for both stems), so no defect; a nit for report readability.
2. `_bp_inner.py` has no `#!/usr/bin/python3` shebang; correct-by-design (venv-quarantined) but a first-time reader would want the docstring's "runs INSIDE workspace/basic_pitch_venv" line to be more prominent.
3. Anchor preservation's schema (`pre` + `post` + `diff` + `diff_count`) is different from stage-41's peer schema (which uses `anchor_shas` list-of-dicts). Both are self-consistent; a light cross-clone convention drift worth flagging for consolidation in a future infra pass — but not defect-worthy.

---

## Cross-clone consistency with stage-41 (drums+bass)

The two RC10 branches (drums+bass at c54 clone-0, guitar+piano at c53 clone-1) share:
- Same c33 render_stem.py invariant SHA `214372d9…5b2b` — preserved in both.
- Same env pins (BLAS×3 + PYTHONHASHSEED=0 + SOURCE_DATE_EPOCH=1756463424 + TZ=UTC + LC_ALL=C.UTF-8).
- Same three-way rubric_hash byte-equality discipline (different SHA per branch, both self-consistent).
- Both LAND: `RC10_DRUMS_BASS_LANDS` (drums 5/5, bass 3/5) at c54; `RC10_GUITAR_PIANO_LANDS` (guitar 4/5, piano 5/5) at c53.

The RC10 four-stem gate (drums, bass, guitar, piano) is now VALIDATED across both branches; only "other" + "vocals" remain to complete the RC10 all-six-stem gate per operator UPDATE #4.

---

## Next stage — Stage 43 of 48 (test 19 of 23)

Remaining unaudited high-value slices per priority:

- **c51 Branch B RC2+RC3 (fork 38eba9f21a61 clone-1)** — `data/rc2_rc3_impl/verdict.json` — drums onset transcription + bass transcription MIDIs consumed downstream by c53/c54 RC10 branches (already verified as `RC2_RC3_LANDS` through the c54 rubric hash chain, but no direct probes yet).
- **c50 rubric-v2 supersede chain** — `_plan/m-recreate-2-rubric-v2-supersede` supersedes_path `str` per c14 lemma; light sub-probe.
- **`_infra/anchor-manifest-v1` 18→19 entry evolution** (c35 → c47 SOURCE_DATE_EPOCH pin at anchor #19).
- **c34 palette_v2 schema activation** (c34 Branch A) — check schema validator hygiene.

Recommend Stage 43 = c51 Branch B RC2+RC3 (upstream feed for all RC10 branches; last major un-directly-probed non-EAR-1 verdict node).

## Stage receipt

Byte-determinism, anchor preservation, rubric_hash chain, and hygiene contracts all hold for the c53 clone-1 RC10 guitar+piano milestone family. Verdict `RC10_GUITAR_PIANO_LANDS` is honest and reproducible; the four-stem RC10 gate is now cross-verified across both parallel branches.
