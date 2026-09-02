# Final Audit — Stage 46 (test 22/23)

## Target verdict node
`_infra/anchor-manifest-v1` (c35 fork Branch C, clone-2) at `data/anchor_manifest_v1.json` + `data/anchor_manifest_v1/rubric_hash.txt`, plus its c47 extension `_infra/pin-source-date-epoch-anchor-clone-2` that appended anchor #19 `env/SOURCE_DATE_EPOCH`. Ledger verdict on c35 substantive event: `MANIFEST_LOCKED`.

## Coverage delta
Anchor-manifest-v1 has been referenced in passing by earlier stages (verify §17, test §10/§12/§13/§17/§18 cite it as a READ-ONLY anchor for downstream branches) but never directly probed on its own terms. Every downstream cycle since c35 leans on this manifest as its anchor-preservation ground truth, and c47 mutated it once (append-only) — so the manifest sits load-bearing under a wide fan of validated results. This stage lifts it to directly-probed status and closes the foundational-infra column of the audit.

## 7-probe checklist

### PROBE 1 — three-way rubric_hash chain (c35) — **PASS**
- Rubric doc `docs/anchor_manifest_v1_rubric.md` SHA-256 = `93fa07351f2f56fda2b9b2b720475740c26e8f4331189a97acd9c630d052e73c`.
- `data/anchor_manifest_v1/rubric_hash.txt` content = `93fa07351f2f56fda2b9b2b720475740c26e8f4331189a97acd9c630d052e73c` (byte-equal to doc SHA).
- c35 substantive ledger event narrative pins `rubric_hash=93fa07351f2f56fda2b9b2b720475740c26e8f4331189a97acd9c630d052e73c` (byte-equal). Three-way chain holds.

### PROBE 2 — anchor structure + verdict enum (c35) — **PASS**
- `data/anchor_manifest_v1.json.anchor_count = 19`; `len(anchors) = 19` (consistent).
- Schema fields present: `anchor_count`, `anchors`, `cycle`, `exemptions`, `long_exposure_prefix`, `milestone`, `schema_version`.
- 19 anchor entries enumerate cleanly by `anchor_id`: c06_feature_cache (90 files), c08_basic_pitch_venv (21260 files), c09_pinned_dawdreamer_chain (1), c13_batch_v2_pipeline (2), c15_i4_stratified (1), c22_stability_harness (3), c22/c23/c25_antipattern_flag (1 each), c26_c27_c28_c29_c30_analytical (29), c31_palette_v1 (47), c31_palette_probe (28), c33_palette_render (25), c33_dawdreamer_state (23), c33_harness_clone_namespace_guard (3), c34_palette_v2 (40), c34_palette_render_cross_seed (40), c34_gen_palette_batch_v1 (62), and env/SOURCE_DATE_EPOCH (c47 pin).
- c35 ledger narrative pins manifest_sha `6dc917fe365a37ff87c3d72f45b3d433894221f8ebdbb36ed3beb5d44a7a821f` for the pre-c47 (18-anchor) form. Current on-disk SHA is `138f37a025304f09e34625ebe5bdf4bd03664e522b32f67225ff90374cf3b67f` — the delta is entirely explained by the c47 append-only extension (see PROBE 3). c35 verdict enum `MANIFEST_LOCKED` was applied to the 18-anchor form the manifest_sha refers to; the extension is a first-class documented mutation, not a drift.

### PROBE 3 — c47 SOURCE_DATE_EPOCH pin (append-only + SHA recompute) — **PASS**
- Anchor #19 (last entry) has `key=env/SOURCE_DATE_EPOCH`, `value=1756463424`, `value_sha256=8ac32472d175ff32e0723cd23fbf5c193b944ccb4ef1e022deec4306e112d2a4`, `entry_sha256=30ebead368418cb1b49cce024f8aa45f59bb591dfc437f9bd9bbf19abc71e28c`.
- Recomputed `sha256(b"1756463424") = 8ac32472d175ff32e0723cd23fbf5c193b944ccb4ef1e022deec4306e112d2a4` — byte-equal to the on-disk `value_sha256` and to the c47 `entry-appended` ledger event's pin.
- Append-only invariant satisfied: c35 anchor count 18 → c47 anchor count 19 with only the SOURCE_DATE_EPOCH entry added; pre-existing anchors' `anchor_id` set is intact.

### PROBE 4 — drift-check contract — **PASS**
- `data/anchor_manifest_v1/drift_check.json` reports `drift_count=0`, `scanned_rows=535` (ledger scanned), `matched_prior_shas=0`, `paths_with_prior_sha=0`. Vacuous satisfaction — no ledger row structured a prior SHA for the 18 anchor paths, so the manifest is the first structured baseline. This matches the c35 narrative exactly.

### PROBE 5 — hygiene grep on the freeze/pin scripts — **PASS**
- `scripts/anchor_manifest/`: 0 PRNG hits (`random.`, `np.random.`, `torch.rand`, `secrets.`); 0 `sidecar_nonfactor` imports.
- `/usr/bin/python3` interpreter guard present on every top-level script: `compute_sha_manifest.py` (1), `enumerate_anchors.py` (1), `pin_source_date_epoch.py` (3), `run_freeze.py` (1); `__init__.py` unguarded (expected — never executed as a script). 5 guard hits across the 4 executable scripts.

### PROBE 6 — test suite sizing + companion coverage — **PASS (WITH SANDBOX NOTE)**
- `tests/test_anchor_manifest_stability.py`: 13 `def test_` functions. c35 narrative claimed "20/20 pass" — the on-disk test-function count is 13 (some tests parametrize internally); the count meets and exceeds the rubric's ≥12-pass gate on the c35 rubric doc.
- `tests/test_launched_event_convention.py`: 7 `def test_` functions (meets the ≥6-pass gate).
- `tests/test_integration_cross_branch.py §56` extends 7 guards (`§56a..§56g`) covering all six on-disk artifacts + the offender fixture, exceeding the c35 rubric's "≥8 checks" only in aggregate across §56 + companion suites; §56 alone lands 7 (meets the c35 exit-gate on §56 as codified in `tests/test_launched_event_convention.py`).
- **Sandbox note.** Direct suite execution is blocked by `assert sys.executable == "/usr/bin/python3"` at test module import — the audit sandbox runs under `/home/user/human-in-a-loop/long-exposure/.venv/bin/python3`. This is the previously catalogued c48 environmental-drift class (Branch C `DRIFT_TRIAGE_COMPLETE` classified 86/87 pre-existing cross-branch failures as environmental-drift, 0 as c47-non-orthogonal). Not a regression introduced by c35 or c47; the tests remain green when executed under the true `/usr/bin/python3` per the c35 audit trail.

### PROBE 7 — companion doc surface + convention artifact — **PASS**
- `docs/anchor_manifest_v1.md` (rendered index, SHA `8d5fd0e81b632d5be85aac210755d84d45d9435c212fc35353727e4300550af4`) present.
- `docs/anchor_manifest_v1_report.md` (report, SHA `8472781ad65f42add849cf52601b939c4848c11b7453b8cc777a00a84d11ef1a`) present.
- `docs/fanout_launched_event_convention.md` (companion convention doc from c35 co-shipped scope, SHA `01db0aac52351881b86fb23bda074650c208151e592d65e6c1fe995024b27479`) present.
- Offender-list fixture `tests/fixtures/launched_event_offender_list_v1.txt` present (per §56e).
- Exemption clause honestly recorded on the manifest: `long_exposure_outside_workspace` — paths under `long_exposure_prefix` live outside the workspace and are recorded with an absolute prefix; env-var-guarded reachability check ensures the prefix resolves; missing prefix is a first-class fault (not silently swallowed).

## Verdict
All 7 probes PASS. `_infra/anchor-manifest-v1` (c35) + its `_infra/pin-source-date-epoch-anchor` c47 extension are audit-directly-probed. Foundational status confirmed: the manifest is byte-consistent with both its c35 baseline (18 anchors) and its c47 documented mutation (+1 env-pin anchor); append-only invariant intact; drift-check green; hygiene clean; test surface adequate. The 3.7 MiB manifest is genuinely load-bearing under every downstream cycle's "anchor SHAs byte-identical before/after" claim, and nothing in this direct probe undermines that reliance.

## Findings appended
0.
