# Anchor manifest v1 (Cycle 35 Branch C, clone-2)

**Schema version:** 1
**Anchor count:** 19 *(18 c35 baseline + 1 c47 Branch C SOURCE_DATE_EPOCH pin)*
**Long-exposure prefix (exemption):** `/home/user/human-in-a-loop/long-exposure`

## Anchors

| # | anchor_id | cycle | kind | # paths | # files | is_readonly |
|---|-----------|-------|------|---------|---------|-------------|
| 1 | `c06_feature_cache` | 6 | feature_cache | 1 | 90 | True |
| 2 | `c08_basic_pitch_venv` | 8 | venv | 1 | 21260 | True |
| 3 | `c09_pinned_dawdreamer_chain` | 9 | dawdreamer_chain | 1 | 1 | True |
| 4 | `c13_batch_v2_pipeline` | 13 | batch_pipeline | 2 | 2 | True |
| 5 | `c15_i4_stratified` | 15 | sampling_utility | 1 | 1 | True |
| 6 | `c22_stability_harness` | 22 | stability_harness | 3 | 3 | True |
| 7 | `c22_antipattern_flag` | 22 | anti_pattern_flag | 1 | 1 | True |
| 8 | `c23_antipattern_flag` | 23 | anti_pattern_flag | 1 | 1 | True |
| 9 | `c25_antipattern_flag` | 25 | anti_pattern_flag | 1 | 1 | True |
| 10 | `c26_c27_c28_c29_c30_analytical` | 30 | analytical_utility | 1 | 29 | True |
| 11 | `c31_palette_v1` | 31 | schema | 4 | 47 | True |
| 12 | `c31_palette_probe` | 31 | probe | 4 | 28 | True |
| 13 | `c33_palette_render` | 33 | palette_render | 4 | 25 | True |
| 14 | `c33_dawdreamer_state` | 33 | workaround | 4 | 23 | True |
| 15 | `c33_harness_clone_namespace_guard` | 33 | guard | 3 | 3 | True |
| 16 | `c34_palette_v2` | 34 | schema | 4 | 40 | True |
| 17 | `c34_palette_render_cross_seed` | 34 | cross_seed | 4 | 40 | True |
| 18 | `c34_gen_palette_batch_v1` | 34 | batch | 4 | 62 | True |
| 19 | `env/SOURCE_DATE_EPOCH` | 47 | env_pin | 1 | 0 | True |

### Anchor #19 — `env/SOURCE_DATE_EPOCH` (c47 Branch C, clone-2)

Pinned by cycle 47 Branch C combined milestone
`_infra/pin-source-date-epoch-anchor-clone-2`. Registers the campaign-wide
`SOURCE_DATE_EPOCH=1756463424` environment pin (used across every
byte-determinism × 2 assertion since cycle 6) as a first-class anchor
entry with per-value SHA-256 and canonical-JSON entry SHA-256.

- `value`: `1756463424`
- `value_sha256`: `sha256(str(1756463424).encode("utf-8"))` =
  `8ac32472d175ff32e0723cd23fbf5c193b944ccb4ef1e022deec4306e112d2a4`
- `entry_sha256`:
  `sha256(canonical_json({"key": ..., "value": ..., "value_sha256": ...}))`
  = `30ebead368418cb1b49cce024f8aa45f59bb591dfc437f9bd9bbf19abc71e28c`
- Closes c46 audit MINOR #3 ("SOURCE_DATE_EPOCH unregistered as anchor").
- Append-only per the c35 anchor-manifest contract — 18 pre-existing
  entries byte-identical before/after.

## Per-anchor path SHA summary

### `c06_feature_cache` (cycle 6, kind: feature_cache)

- **`data/ear/features`** — kind=dir, files=90, dir_manifest_sha=`d03d477e9b9ec712426366e2377d7ca88ef2d246a3da6b492072b3417f01057b`

### `c08_basic_pitch_venv` (cycle 8, kind: venv)

- **`workspace/basic_pitch_venv`** — kind=dir, files=21260, dir_manifest_sha=`66bc3225f23176de8fb06fd5fc84ce398b067866455b71580eda716bfd1a3ba0`

### `c09_pinned_dawdreamer_chain` (cycle 9, kind: dawdreamer_chain)

- **`scripts/tex/render_effects_layered.py`** — kind=file, files=1
  - sha256=`b1ab2f4c375455c781cadb6630c3bd89d6165417d83e35440ff53e11b6b4b8e0`

### `c13_batch_v2_pipeline` (cycle 13, kind: batch_pipeline)

- **`scripts/gen/batch_v2.py`** — kind=file, files=1
  - sha256=`78b200c0c5c95ea2e766ae6df1e1664dbfefbbd35b259ed46e793d3adc108f9e`
- **`scripts/gen/sample_rules.py`** — kind=file, files=1
  - sha256=`7dcdcc03d1b3565f1f160a1de48150642218820f2e24fd482c223e12359e2a74`

### `c15_i4_stratified` (cycle 15, kind: sampling_utility)

- **`scripts/rules/sampling/i4_stratified.py`** — kind=file, files=1
  - sha256=`ad69aecf680fac2066bc4a885d6e73eae631c977e12ae54f3661c06a3c6a065b`

### `c22_stability_harness` (cycle 22, kind: stability_harness)

- **`scripts/ear/synthetic_labels.py`** — kind=file, files=1
  - sha256=`b71f194ef97e8936bb8942d5fccba899e6efe47e292cca185728d1cd9f41fb4d`
- **`scripts/ear/stability_metrics.py`** — kind=file, files=1
  - sha256=`6a5cb5183fdc77e80677ef01bb47f777a2662404f737f8aa74287f30cf97dc27`
- **`scripts/ear/stability_audit.py`** — kind=file, files=1
  - sha256=`b1ce5137b665a962657f1ee128db4d36abcb6d2174f57101b354a3194ea02e4c`

### `c22_antipattern_flag` (cycle 22, kind: anti_pattern_flag)

- **`docs/ear_stability_audit_report.md`** — kind=file, files=1
  - sha256=`fd31b654e7ab6f4ef7cd7a0e244b96613ef3e532f278af965709440b96e06931`

### `c23_antipattern_flag` (cycle 23, kind: anti_pattern_flag)

- **`docs/ear_head_regularization_audit_report.md`** — kind=file, files=1
  - sha256=`74d6845a8fae14625f9c31f3061154bfacfd19df9562c3a4de8c4fa57f4aeb21`

### `c25_antipattern_flag` (cycle 25, kind: anti_pattern_flag)

- **`docs/ear_feature_representation_audit_report.md`** — kind=file, files=1
  - sha256=`e600e65886add6e71bf879f639fa544cd8ec985764020c1d91344872e363fc9b`

### `c26_c27_c28_c29_c30_analytical` (cycle 30, kind: analytical_utility)

- **`scripts/analysis`** — kind=dir, files=29, dir_manifest_sha=`f2cf3591d13889a322547f1cce4a96935211047bafd606537d85f691ef7300e0`

### `c31_palette_v1` (cycle 31, kind: schema)

- **`scripts/palette`** — kind=dir, files=41, dir_manifest_sha=`51f39c12e7d033ef3629b87b0ca736cc06bd2a43841b6deb63eddc4bc31108ac`
- **`docs/palette_assignment_schema_rubric.md`** — kind=file, files=1
  - sha256=`1493818cb276344e817a965c6d8b9d3cbfe02607e7cd741fdc46a1b3560ebce9`
- **`docs/palette_assignment_schema_report.md`** — kind=file, files=1
  - sha256=`071b684b912336bc992ddaa9ab56274cd11cb057a2d0452ffaa22eb9b7584d00`
- **`data/palette/schema`** — kind=dir, files=4, dir_manifest_sha=`4075eae97ae9a119e416231cb8722b5398ceb60c27e0b6424460fec36a9ffbee`

### `c31_palette_probe` (cycle 31, kind: probe)

- **`scripts/palette_probe`** — kind=dir, files=6, dir_manifest_sha=`2e25642cbc06aa47083ee2a0cfd32a4e49b0b5185bc8377a95bb46435a009f96`
- **`docs/palette_instrument_determinism_rubric.md`** — kind=file, files=1
  - sha256=`75daa068aa804351db744cdb3a41df151ba682bbe3278c7c8cb8870a54ac7c96`
- **`docs/palette_instrument_determinism_report.md`** — kind=file, files=1
  - sha256=`526ae3762b7738f3e9a4a5dd43414eef5cda8e7209730b00d342dc5992542a85`
- **`data/palette_probe`** — kind=dir, files=20, dir_manifest_sha=`acf5f6fcdc0cc06f1487074e1c4782abf0c73a428c1e418f72920701dab08a68`

### `c33_palette_render` (cycle 33, kind: palette_render)

- **`scripts/palette_render`** — kind=dir, files=4, dir_manifest_sha=`14cb76894367a7d0b17d0622593606b8d9c195a4c410db5311e648c722ee7ab9`
- **`docs/palette_driven_bare_render_rubric.md`** — kind=file, files=1
  - sha256=`ae2f3b50e89d165908f8e53ba2e522d38e45afcc214c0013279781b9fef0e648`
- **`docs/palette_driven_bare_render_report.md`** — kind=file, files=1
  - sha256=`048c93827120ed967599a4a9ead87c08bce3ad711b3464b242f1fc3b2e3c0f8a`
- **`data/palette_render`** — kind=dir, files=19, dir_manifest_sha=`1c75c0a2ac79572f4936c3f11bbfcdec20293c421d2ce2def37041d6ee614222`

### `c33_dawdreamer_state` (cycle 33, kind: workaround)

- **`scripts/dawdreamer_state`** — kind=dir, files=6, dir_manifest_sha=`f6db9c5e4836f5716a75ab1a640384234d924e59614d3a5810405ac2bf1df74b`
- **`docs/dawdreamer_state_extraction_rubric.md`** — kind=file, files=1
  - sha256=`611e0b768036d44862ca4ba495b2e1a08742cf890d8f5a6298b441634a69f27c`
- **`docs/dawdreamer_state_extraction_workaround_report.md`** — kind=file, files=1
  - sha256=`7611b900634bf34da8a00b26847acef4311f8291fcaf672df2677a883ca08fd1`
- **`data/dawdreamer_state`** — kind=dir, files=15, dir_manifest_sha=`7128a18cd7df8bbc1a2917fee0105ac87ca5fe6c4aa13bd9743f9ce1978a8357`

### `c33_harness_clone_namespace_guard` (cycle 33, kind: guard)

- **`/home/user/human-in-a-loop/long-exposure/long_exposure/workspace_bootstrap.py`** — kind=file, files=1
  - sha256=`f55f54319e7a5f4d1b5da4e489451cb8b37361a21dde6dbdc54429416d532a1e`
- **`tests/fixtures/harness_clone_namespace_guard_rubric_hash.txt`** — kind=file, files=1
  - sha256=`12e14f8a4d780881733597baa1cae940b2e0a89ec187e0e37e41da9547d5e789`
- **`docs/harness_clone_namespace_guard_rubric.md`** — kind=file, files=1
  - sha256=`cd020761c919648e797769e3d05721b875be860cc845f16dbd9061ce92e876e3`

### `c34_palette_v2` (cycle 34, kind: schema)

- **`scripts/palette_v2`** — kind=dir, files=32, dir_manifest_sha=`e6111a118fe0595917e10a3a807b339026e3f194bd81d224536a822c5dc71745`
- **`docs/palette_schema_v2_rubric.md`** — kind=file, files=1
  - sha256=`ed737733c79848c9f84e7dc0bbd3421b2fbb6f8442e485c3bb3e3c553c452ec2`
- **`docs/palette_schema_v2_report.md`** — kind=file, files=1
  - sha256=`2233a96ce699aa41da1967acabf8bd0ae3cd98ab6714c82df758eb174620133c`
- **`data/palette_v2`** — kind=dir, files=6, dir_manifest_sha=`8ec431af6301e81d0fed87948c3252c77a2d4b6ff383774e12b65c23c50654b2`

### `c34_palette_render_cross_seed` (cycle 34, kind: cross_seed)

- **`scripts/palette_render_cross_seed`** — kind=dir, files=4, dir_manifest_sha=`f4a32ca97a2637aa30b57e253c0834af3d6aacea6f8eab4377aca17d0dbbaaea`
- **`docs/palette_driven_bare_render_cross_seed_rubric.md`** — kind=file, files=1
  - sha256=`48c073dfadc0c11533bf2f56ab16b4eec72e08271058fa1101777b9b1175a59f`
- **`docs/palette_driven_bare_render_cross_seed_report.md`** — kind=file, files=1
  - sha256=`fb7a9aa71d5825dfbed25f0974f009bfca0975cbeafbb9fe52994bfdf71973c4`
- **`data/palette_render_cross_seed`** — kind=dir, files=34, dir_manifest_sha=`ec2f878b232baf88a9dc14fe6a43d0b2f30d55402bc730c10039dadc83927e4e`

### `c34_gen_palette_batch_v1` (cycle 34, kind: batch)

- **`scripts/gen_palette_batch_v1`** — kind=dir, files=5, dir_manifest_sha=`32f15dcd1995af7519e7e838f42d856e08bda9191acc6b8f00875fe94d0acaa9`
- **`docs/palette_driven_batch_v1_rubric.md`** — kind=file, files=1
  - sha256=`42f0bcea9ea13e4543380d5b17034c623deeb69fb5ef1a98b54e1ed670101017`
- **`docs/palette_driven_batch_v1_report.md`** — kind=file, files=1
  - sha256=`8ce69c5b445d489b068855a0653e4bb58b3afee41eb8961eb69521058eb30b6b`
- **`data/gen_palette_batch_v1`** — kind=dir, files=55, dir_manifest_sha=`fa1c983b905b25575d775396df00c8b2ba85223fa086fa675886ee236d93f805`
