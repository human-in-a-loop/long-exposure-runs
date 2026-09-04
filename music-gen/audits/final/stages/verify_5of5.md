# Verify Slice E (Stage 6 of 12) — c16–c20 metric-semantics, showcase, skeletons, rules scaffold

Scope: c16 embedding-metric-semantics diagnostic + operator escalation, c17
M-V4-SHOWCASE-1 CG A/B full render + WIG skeleton + pinned-profile Schema v1,
c18 Rome skeleton + bass-gain narrative clarification + LUFS-I diagnostic
sidecar + full-render test debt fillin, c19 Disco A + Peach Dream skeletons +
LUFS FETCH_FAIL fixture, c20 M-V4-RULES-1 scaffold + LUFS FETCH_FAIL branch
test. Delta-audit mode: baseline `audits/final/final_audit_report.md` treated
as canonical for earlier work; Slice E carries new artifacts.

## SHA verification — Slice E anchors (24-hex byte-exact vs POR narrative)

| POR anchor | Expected prefix | On-disk prefix | Cycle | Status |
|---|---|---|---|---|
| `cg_ab_mix.wav` (M-V4-SHOWCASE-1/cg-ab-full-render) | `6e13e0075c5d8116…f9484b` | `6e13e0075c5d8116…f9484b` | c17 | ✅ |
| `cg_ab_mix.manifest.json` | `f9f1c9edce944c27…` | `f9f1c9edce944c27` | c17 | ✅ |
| `cg_ab_mix.replay_proof.json` | `fcd8e6878b13818f…` | `fcd8e6878b13818f` | c17 | ✅ |
| WIG `stem_manifest.json` | `13e21d69a8711b35…` | `13e21d69a8711b35` | c17 | ✅ |
| Disco A `stem_manifest.json` | `acadbf258cd95814…` | `acadbf258cd95814` | c19 | ✅ |
| Peach Dream `stem_manifest.json` | `c4944ee80dfe446b…` | `c4944ee80dfe446b` | c19 | ✅ |
| `pinned_profile_schema_v1.json` | `8f61d9391a5a3bcf…` | `8f61d9391a5a3bcf` | c17 | ✅ |
| `profile_validator.py` | `cd17106f651e9de7…` | `cd17106f651e9de7` | c17 | ✅ |
| `tests/test_pinned_profile_shape.py` | `0c1f5667117c4755…` | `0c1f5667117c4755` | c16 | ✅ |
| `embedding_metric_semantics.json` | `2884dd3203f4e561…` | `2884dd3203f4e561` | c16 | ✅ |
| `embedding_metric_semantics.replay_proof.json` | `b3d74f5913bc0b05…` | `b3d74f5913bc0b05` | c16 | ✅ |
| `probe_embedding_metric_semantics.py` | `d6464d02f2d201d8…` | `d6464d02f2d201d8` | c16 | ✅ |
| `cg_ab_mix.lufs_diagnostic.json` | `6810d505…647b6b` | `6810d5056edf5889…647b6b` | c18 | ✅ |
| `scaffold_smoke_test.json` (v4_rules) | `8250774547d0c55d…` | `8250774547d0c55d` | c20 | ✅ |

Rome `stem_manifest.json` on-disk SHA = `e00bd15d400b663777d2263614ac579a…`;
c18 POR row narrative does not state a specific SHA, so no drift class. The
manifest exists and is invariant-(d) parallel to WIG/Disco A/Peach Dream
sibling shape per POR row wording ("byte-parallel to c17 WIG shape").

## c16 — CRITICAL diagnostic + operator escalation (still open)

- Track 1 `_infra/embedding-metric-semantics-diagnosed-c16` diagnostic verdict
  `metric_is=distance` empirically settled by Pair A identity=0.0 (three-pair
  probe, replay-proof HOLDS). Anchors byte-verified.
- Track 2 `_manager/M-V4-METRIC-SEMANTICS-c16` operator escalation preserved
  through Slice E: `blocked_on_operator=true`; two named paths (A distance,
  B similarity). No cycle in c17–c20 unilaterally adjudicated it. Carryover
  handling honest (each opened stem_manifest.json carries `blocked_on:
  _manager/M-V4-METRIC-SEMANTICS-c16` per POR narrative).
- Track 3 invariant (e) codified in `docs/agent_picks_selection_invariants.md`
  and enforced by `tests/test_pinned_profile_shape.py` (6/6 per POR).

No drift finding on Slice E for c16.

## c17 — CG A/B full render + WIG skeleton + Schema v1

- `cg_ab_mix.wav` sha `6e13e007…f9484b` matches POR narrative exactly (both the
  24-hex head and the …f9484b tail). Manifest and replay-proof siblings match.
  Replay-proof verdict `REPLAY_PROOF_HOLDS` is asserted by POR narrative +
  c18 Track 1 test `test_deliver_cg_ab_v4_full_render.py` 12/12 PASS (per POR).
- WIG `stem_manifest.json` sha `13e21d69…` matches. Opened as skeleton with
  `blocked_on: _manager/M-V4-METRIC-SEMANTICS-c16` (per POR narrative). No
  candidate acceptance until Track 2 operator resolution — coherent.
- pinned-profile Schema v1 + validator SHAs match; c18 companion rationale doc
  clarifies invariant (d) disclosure norm around the "loosened" schema (c9
  bass_v2 `operator_authority` + c14 canonical + c15 3-key drift all validate).

No drift finding on Slice E for c17.

## c18 — Rome skeleton + bass-gain clarification + LUFS + tests

- Rome `stem_manifest.json` exists (on-disk sha `e00bd15d…`) byte-parallel to
  WIG. `blocked_on` carry-over honest. No POR-vs-disk drift because POR row
  narrative pins no explicit SHA.
- Bass-gain clarification: `docs/sound_match/cg_ab_bass_gain_clarification_c18.md`
  supplements the c17 "attenuation" narrative → amplification `gain=2.688385`
  test-anchored (test_04 in the full-render suite per POR). Correct invariant
  (d) application (c17 report READ-ONLY, note supplements).
- LUFS-I diagnostic `cg_ab_mix.lufs_diagnostic.json` sha `6810d505…647b6b`
  matches. `does_not_mutate_audio=true` asserted (c17 `cg_ab_mix.wav` SHA
  byte-identical pre==post — still on-disk verified).
- c14 grid-deviation retroactive disclosure for guitar stage-2 (`_infra/guitar-stage2-grid-deviation-disclosed-c15`) chained appropriately.

No new drift finding on Slice E for c18.

## c19 — Disco A + Peach Dream skeletons + LUFS FETCH_FAIL test

- Disco A + Peach Dream `stem_manifest.json` SHAs match POR narrative.
  Peach Dream honestly discloses non-standard stem path
  `operator_section_c25_checkpointed/rc9_6stem/` per invariant (d) — no drift.
- All 5 focus songs now opened; M-V4-PROFILES-1 skeleton coverage complete
  (CG terminal + 4 skeletons blocked on c16 Track 2). Coherent with campaign
  scope order.

No drift finding on Slice E for c19.

## c20 — M-V4-RULES-1 scaffold

- `scripts/v4_rules/__init__.py` + `extract_v4.py` present on disk. Not
  cited by SHA in POR narrative for c20 (POR narrative pins module SHAs
  `c8603851…` init + `1e0ad113…` extract, but on-disk are
  `3189da3df7cfb49f…` and `2b1764e3fa9b4c75…`). This is a SHA drift class:
  POR-cited init/extract SHAs do NOT match on-disk. Filed as MINOR — this is
  a POR narrative transcription-error-or-scratch-emitter class analogous to
  Slice D `bass_v2.replay_proof.json` (POR narrative pinned a different SHA
  than on-disk; the on-disk artifacts are authoritative per FD-1).
- Smoke-test JSON sha `8250774547d0c55d…` matches POR exactly. Contract:
  `all_stubs_raise_c21_plus_notimplemented=true` per POR narrative.
- c23 v3-rules anchors (`extract_rules.py` `9af3e37c…`, `rules_artifact.jsonl`
  `e19fb205…`) READ-ONLY status carried into c20 — no drift.

## Findings

New MINOR (Slice E scope):

1. c20 POR narrative pins `scripts/v4_rules/__init__.py` sha `c8603851d54c56c4…`
   and `extract_v4.py` sha `1e0ad1131f090003…`, but on-disk 24-hex prefixes
   are `3189da3df7cfb49f…` and `2b1764e3fa9b4c75…` respectively. Neither the
   POR narrative nor any subsequent event pins the on-disk SHAs. Consistent
   with the Slice D pattern (bass_v2.replay_proof.json POR-anchor drift):
   POR narrative SHAs are not authoritative; on-disk artifacts are per FD-1.
   Not a defect — scaffold contract (stubs raise `NotImplementedError`)
   verifiable orthogonally via `scaffold_smoke_test.json` which matches
   its POR SHA. Filed as MINOR narrative-transcription drift.

Filed as one finding_kind `por_sha_drift` MINOR appended to
`audits/final/findings.jsonl`.
