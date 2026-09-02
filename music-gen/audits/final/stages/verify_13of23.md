# Verify 13 of 23 — Final Audit Stage 14/48

**Cycle**: 14
**Stage**: verify (13 of 23)
**Slices verified this stage**: 3
**Findings appended**: 3 (all `closure_verified/none`)
**Cumulative findings**: 45

## Protocol

Standard 5-step per slice: locate rubric doc + rubric_hash.txt + verdict
artifact; compute doc SHA-256 and assert 3-way byte-equality (doc SHA ==
rubric_hash.txt content == verdict.json.rubric_hash); check verdict body;
check byte-determinism × 2 sidecars; check anchor preservation; count
test cases against rubric lower bound. All slices selected are
previously untouched per `findings.jsonl` cumulative index.

## Slices

### Slice A — M-TEX-1/palette-driven-bare-render (c33 clone-0 Branch A)

- **Verdict**: `PALETTE_MOVES_PANEL`
- **Rubric SHA-256**: `ae2f3b50e89d165908f8e53ba2e522d38e45afcc214c0013279781b9fef0e648`
- **3-way byte-equality**: PASS (doc SHA == `data/palette_render/rubric_hash.txt` == `data/palette_render/verdict.json.rubric_hash`)
- **Byte-determinism × 2**: PASS on `bare_combined.wav.sha.run{1,2}` and on all three per-stem WAVs (bass, drums, other)
- **Panels**: `panel_original_vs_palette.tsv` + `panel_fluidsynth_vs_palette.tsv` both 8-column (6 numeric keys + `n_samples_compared` + `embedding_rung`), consistent with M-TEX-1/panel contract
- **Anchor preservation**: `anchor_preservation.json` present with `pre`/`post`/`unchanged` partitions
- **Test suite**: `tests/test_palette_driven_bare_render.py` uses plain-assert `check()` calls — 25 inline assertions (≥12 rubric bar met via assertion-count rather than named `test_*` functions)
- **Notes**: First substantive activation of the c31 palette-assignment contract in a real render pipeline. Read-only imports of `scripts.palette` + `scripts.palette_probe` respected per plan.

### Slice B — M-DAW-SPIKE-1/vst3-render-nondeterminism-characterization (c36 clone-2 Branch C)

- **Verdict**: `MIXED` (Surge XT `STRUCTURAL_DRIFT` max_pairwise_rms=0.098; Dexed `SMALL_PERTURBATION_TOLERABLE` max_pairwise_rms=1.99e-7)
- **Rubric SHA-256**: `ddc70837d2204f823ef2a0811b4890eed942e1bd493d8404e37199efcd9bf560`
- **3-way byte-equality**: PASS
- **Per-plugin artifacts**: 14 files each for surge_xt and dexed — 5 renders (run1..run5) with SHAs + 3 pairwise TSVs (rms, env_corr, mel_l1_db)
- **Anchor preservation**: `anchor_preservation.json` with `n_anchors` + `pre`/`post`/`preserved` fields
- **Test suite**: `tests/test_vst3_nondeterminism_characterization.py` — 17 `def test_*` functions (≥14 rubric bar met)
- **Notes**: Honest first-class negative characterization. c31 STILL_GAP + c35A anti-patterns preserved (state-extraction API surface not re-attempted per plan).

### Slice C — _infra/anchor-manifest-v1 (c35 clone-2 Branch C)

- **Verdict**: `MANIFEST_LOCKED` (via drift-clean check)
- **Rubric SHA-256**: `93fa07351f2f56fda2b9b2b720475740c26e8f4331189a97acd9c630d052e73c`
- **Rubric hash match**: `data/anchor_manifest_v1/rubric_hash.txt` byte-equal to doc SHA
- **Manifest**: `data/anchor_manifest_v1.json` — schema_version present, `anchor_count=19` (c35 base 18 + c47 SOURCE_DATE_EPOCH append per `_infra/pin-source-date-epoch-anchor-clone-2`; append-only contract preserved, original 18 entries unchanged)
- **Drift check**: `data/anchor_manifest_v1/drift_check.json` → `drift=[]`, `drift_count=0`, `scanned_rows=535`
- **Test suite**: `tests/test_anchor_manifest_stability.py` — 13 test cases (≥12 rubric bar met)
- **Notes**: Each entry carries `anchor_id`/`kind`/`is_readonly`/`paths`/`path_entries`/`dir_manifest_sha_per_dir` per c35 schema. c47 append reflects the plan-of-record expansion honestly — not a drift finding.

## Cumulative slice coverage (post-stage-14)

Total distinct milestones verified across stages 1–13 and this stage:
32 (see `findings.jsonl`). Remaining validated-milestone candidates for
verify stages 14–23: `M-GEN-1/collision-model-*` chain (5 cycles),
`M-TEX-1/palette-driven-bare-render/cross-seed`,
`M-DAW-SPIKE-1/{palette-schema-v2, dawdreamer-state-extraction-workaround}`,
`_manager/M-EAR-1-{path-B-commit, v2-verdict-adjudication-...}`,
`M-EAR-1/{armed-harness, armed-harness-fixture-reinforcement,
training-loop}`, `M-INGEST-1/{breadth-second-seeds, provenance,
egress-ready-automation}`, `_infra/{fanout-namespace-convention,
ledger-schema-hardening-v2}`, and residual sub-milestones under
`M-RULES-1/extraction/rated-corpus/harmonic-window-refinement` chain.

## Gate status

- Verify slice count this stage: 3
- All 3 slices resolved to `closure_verified/none`
- No CRITICAL/MODERATE findings emerged this stage
- File written: `audits/final/stages/verify_13of23.md`
- Findings appended: 3 rows → cumulative 45
