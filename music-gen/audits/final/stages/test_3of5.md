# Stage 9 (Test 3/5) — Adversarial c12–c17 Slice

**Cycle window:** c12–c17 (drums family-2 closeout, c13 drums OPT1 fork, c14 CG-drums OPT3 revise + guitar stage-2 + NULL grounding, c15 guitar family-2 + OPT3 auto-resolution, c16 embedding metric-semantics diagnostic, c17 CG A/B full render + WIG opened + pinned-profile schema)

**Mode:** DELTA-AUDIT. Prior findings in `findings.jsonl` cover c1–c11 arc + c20 v4-rules scaffold + Slice D bass_v2 anchor drift.

---

## Method

Adversarial byte/SHA verification against POR narrative for on-disk artifacts spanning the six-cycle slice; targeted focus on:

1. c11 channel-aware `replay.py` fix regression (already verified sound in stage 8; re-checked via c12 independent re-verify JSON)
2. c12 CG-drums family-2 stem-sampled render byte-determinism + FAMILY2_RULED_OUT verdict
3. c13 CG guitar sweep leaderboard + c13 CG-drums OPT1 acceptance fork (below-floor CRITICAL caught by c14 auditor)
4. c14 CG-drums OPT3 revise: c13 stale sibling preservation + c14 pinned-profile shape (invariant e)
5. c15 CG-guitar family-2 verdict + acceptance auto-resolution via invariants
6. c16 embedding_cos_vggish metric-semantics diagnostic + escalation
7. c17 CG A/B full render manifest coherence + per-cell provenance SHA-round-trip
8. c17 WIG stem_manifest.json opened; pinned-profile JSON schema v1

---

## Positive Verifications (defenses that held)

| Anchor | POR pin | On-disk SHA-256 | Status |
|---|---|---|---|
| `data/v4/deliveries/31a164f845f8e27e/cg_ab_mix.wav` | `6e13e0075c5d8116…f9484b` | `6e13e0075c5d8116784109067cf2c73acd65e47d67398b88aa08e0f752f9484b` | **BYTE-MATCH** |
| c17 `cg_ab_mix.replay_proof.json` internal run1==run2 | `6e13e007…f9484b` | Both runs = `6e13e007…f9484b`, verdict REPLAY_PROOF_HOLDS | **BYTE-MATCH** |
| c17 manifest bass_v2 profile | `2a1cb340…` | `2a1cb340bffd11016c566467b0d313fb002c5949ce881968702846867e090462` | **BYTE-MATCH** |
| c17 manifest bass ref stem | `1bad8719…` | `1bad871901294395c1b1ad1c97689e07d879f48aa8b9fc953ea6981d76e09ffd` | **BYTE-MATCH** |
| c17 manifest drums stem (OPT3 source) | `34492c03…` | `34492c03f301b6eac3a75343b61244193889d039ae4ccce4c35cc44d568ac835` | **BYTE-MATCH** |
| c17 manifest guitar stem (OPT3 source) | `e4ff08ea…` | `e4ff08ea10f9bbcb7083e889172fe5fcf4fac57865e957d1bbdcda9341868bd8` | **BYTE-MATCH** |
| c17 manifest vocals stem (hybrid overlay) | `bc5a9031…` | `bc5a9031aadb643efabb7cbed0aff6cd47328c129ac9567c0a59cd503eae7dd5` | **BYTE-MATCH** |
| c12 `drums_family2_render/render.wav` | `69a76c5b…` | `69a76c5b4498972d1cb878da94e645c8c341675b113cc4ca315435f6bb16ca00` | **BYTE-MATCH** |
| c15 `guitar_family2_render/render.wav` | `f4156071…` | `f41560714a68415cd2fe1fc8f2c1010f54aafe182f4592ec20ed893ce2559ddc` | **BYTE-MATCH** |
| c14 `guitar.json` (POR c17 test file cites) | `5e6220ad…` | `5e6220ad9971e8feee4cc5717bab95639f16c40436d69b5b41649ec67516ffbb` | **BYTE-MATCH** |
| c17 `pinned_profile_schema_v1.json` | `8f61d939…` | `8f61d9391a5a3bcf362444a17094ff9f9dd5b4e470d8c91882dbb1ecfe7105d2` | **BYTE-MATCH** |
| c17 `profile_validator.py` | `cd17106f…` | `cd17106f651e9de7a5e596e9ebf65d4171f65b697875d2c7ad442247fb5d0ee6` | **BYTE-MATCH** |
| c16 diagnostic JSON | `2884dd32…` | `2884dd3203f4e561342ab50b082e4c1d5cc977db1f8ae94541819536ff98454e` | **BYTE-MATCH** |
| c16 diagnostic replay proof | `b3d74f59…` | `b3d74f5913bc0b05f36b0d2dba7a9b47fbe498c0bf0e19995c187965339acd6f` | **BYTE-MATCH** |

**Structural checks:**
- c14 CG-drums OPT3 pinned profile (`cg_drums_pinned_profile.json` SHA `720f1424…`): 5-key `acceptance_fork` shape per invariant (e); `chosen=OPT3` + 5 rationale bullets (a)–(e); `rejected=[{OPT1,…},{OPT2,…}]` with per-option reasons; `authority` names campaign prompt + operator directive + agent-picks invariants doc; `family_verdicts_pinned` correctly cites c11 sf2 + c12 family-2 verdict SHAs (`35bb380f…`, `c8a340da…`).
- c14 c13-below-floor stale sibling preserved at `stale/cg_drums_pinned_profile.c13_opt1_below_floor.json` per `<supersedes>` invariant.
- c17 replay proof BYTE-DET × 2 HOLDS end-to-end for the full render pipeline (`kind=cg_ab_v4_full_render_replay_proof`).
- c15 CG-guitar OPT3 pinned profile (`cg_guitar_pinned_profile.json` SHA `14d0707898b557df…`) present per c15 POR narrative.

---

## New Findings

### MODERATE #1 (open, escalated) — c16 embedding_cos_vggish metric semantics inversion class

`data/v4/diagnostics/embedding_metric_semantics.json` empirically settles the metric semantics via three probes:

| Pair | Description | On-disk value | Similarity interpretation | Distance interpretation |
|---|---|---:|---|---|
| A | bass stem vs itself (identity) | **0.0** | Would be ~1.0 (identical→similarity one) | **~0.0 (identical→distance zero) — CONSISTENT** |
| B | bass stem vs bass + 1e-6 constant | 0.0 | Would be ~1.0 | ~0.0 — consistent (imperceptibly small) |
| C | bass vs drums (distinct real content) | 0.20050 | Would be < 1.0 | > 0 (larger than identity) — consistent |

**Verdict declared on disk: `metric_is=distance` (Pair A identity=0.0 is decisive — a similarity would return ~1.0).**

**Implication:** Every v4 acceptance threshold to date is worded as if the field were a similarity (`>= 0.60 CONFIRMED`, `<= 0.40 RULED_OUT`). Under the on-disk distance semantics those thresholds are semantically inverted:
- `>= 0.60 CONFIRMED` fires when the candidate is FAR from the reference (bad match)
- `<= 0.40 RULED_OUT` fires when the candidate is CLOSE to the reference (**good** match — inverted)

Applied to prior verdicts:
- CG-drums c11 top-1 emb_cos 0.2374 → declared SF2_RULED_OUT; **under distance reading = near match**
- CG-drums family-2 c12 emb_cos 0.0372 → declared FAMILY2_RULED_OUT; **under distance reading = essentially identical**
- CG-bass family-2 c6 emb_cos 0.0896 → declared FAMILY2_RULED_OUT; **under distance reading = near-identical**
- CG-guitar family-2 c15 emb_cos 0.0354 → declared FAMILY2_RULED_OUT; **under distance reading = near-identical**
- The systematic five-arc CG pattern where the composite objective ranks non-source-of-truth ahead of source-of-truth is **consistent with threshold inversion**, not with a genuine acoustic anomaly

**Escalation state:** properly logged as `_manager/M-V4-METRIC-SEMANTICS-c16` (also mirrored under `_manager_M-V4-SHOWCASE-1-cg-drums-acceptance-policy.json`), `status=action_required`, `blocked_on_operator=true`, three-way `rubric_hash` chain, two named paths (A: distance-as-named + invert thresholds; B: similarity-numeric-fix via `1 - distance`), per-path invariant-compliance analysis, honest disclosure that neither path resolves via agent-picks invariants.

**Not a defect in the audit process** — the diagnostic was authored honestly, byte-det × 2 HOLDS, no prior verdict was rewritten per c15 auditor guidance. This is the campaign's **largest single open decision** and the primary residual-debt item for the final report.

**Threshold-orthogonal defenses that protect the c17 CG A/B delivery:**
- Bass acceptance rides c9 OPT1+OPT3 hybrid (composite-relative WINNER rule per operator directive 2026-09-03 part 1), **not** the disputed `>= 0.60` threshold.
- Drums (OPT3) + guitar (OPT3) accept via htdemucs stem substitution, **not** any threshold at all.
- Piano + other are NULL findings on audibility grounds (c14 audibility-grounded, unrelated to embedding thresholds).
- Vocals ride htdemucs hybrid overlay per campaign policy.

⇒ The c17 CG A/B render is **defensible regardless of Path A vs Path B resolution**. Escalation carries forward for the WIG/Rome/Peach Dream/Disco A profile arcs and any future accept/reject decision that relies on numeric emb_cos thresholds.

*Recorded as `finding_kind=open_escalation_confirmation` (not a new defect; audit-trail confirmation that the escalation is real, well-formed, and material to residual debt).*

---

## Adversarial checks that resolved cleanly (no new finding)

- **c11 → c14 CG-drums OPT1 → OPT3 acceptance sequence:** c13 OPT1 acceptance (emb_cos 0.2374 below 0.40 floor) was correctly caught by c14 auditor as CRITICAL and revised to OPT3 in-cycle at c14, with the c13 artifact preserved as `stale/cg_drums_pinned_profile.c13_opt1_below_floor.json`. Invariants a/b/c/d retroactively applied. Audit trail complete.
- **c15 CG-guitar acceptance auto-resolution:** OPT3 uniquely satisfies all four invariants (a)-(d) under FAMILY2_RULED_OUT outcome; auto-resolution correctly declined to violate (a) via composite-relative extension. Not a defect.
- **c12 independent re-verify of channel-aware `replay.py` fix:** bass_v2 anchor `832868d0…` reproduced byte-identically; drums anchor reproduced byte-identically to on-disk canonical `dadafcfc0153f002651c23975c3845dd…` (c12 auditor honestly disclosed transcription-error tail-drift on brief anchor). Fix is sound; regression contract holds.
- **c17 WIG opening:** `stem_manifest.json` present with `blocked_on: _manager/M-V4-METRIC-SEMANTICS-c16` — correctly gates downstream WIG profiling on Track 2 resolution.
- **c17 pinned-profile JSON Schema v1:** additive-only (does not mutate c9/c14/c15 anchors); 6/6 tests PASS per POR narrative; grandfathers c9 shape variance per invariant (d); tests validate `supersedes_path` as `str` per c14 lemma.

---

## Findings appended this stage

1 new MODERATE finding appended to `audits/final/findings.jsonl`:
- `_manager/M-V4-METRIC-SEMANTICS-c16` — open-escalation confirmation

Running total: 6 findings (5 MINOR POR-anchor-drift class from prior stages + 1 MODERATE open escalation this stage).

---

## Handoff to stage 10 (test 4/5)

Suggested next slice: **c18–c25** — the M-V3-SPINE / M-V4-CERT / M-V4-PROFILES-1 focus-song openings (WIG stem_manifest c17; Rome c18; Disco A + Peach Dream c19; v4_rules scaffold c20 already spot-checked; M-V4-CERT-1 double-run byte-det; showcase re-render iterations if any). Adversarial focus: verify WIG/Rome/Disco A/Peach Dream stem_manifest.json SHAs against `data/v3_spine/*/operator_section/rc9_6stem/*.wav` file-level SHAs; verify M-V4-CERT-1 `cert_run1/cert_run2` byte-det claim (both `full_reconstruction.wav` = `cc919559b4508b6bfe86…`) and env_pin_sha256 = `623df01f…`.

[OUTPUT: final_audit_stage]
Stage 9 (test 3/5): Adversarial c12–c17 slice — verified 14 anchor SHAs byte-match POR (c17 CG A/B mix + manifest + 5 per-cell provenance stems + c12+c15 family-2 renders + c14 guitar.json + c17 schema/validator + c16 diagnostic); confirmed c16 metric-semantics escalation is well-formed and material (Pair A identity=0.0 decisively → distance semantics; RULED_OUT thresholds ≤0.40 fire on CLOSE-match candidates under on-disk reading; systematic 5-arc CG pattern consistent with threshold inversion; blocked_on_operator; two named paths; largest open residual-debt item for final report; c17 CG A/B delivery is threshold-orthogonal via composite-relative bass acceptance + OPT3 htdemucs stem substitution + audibility-grounded piano/other NULL, so defensible regardless of Path A/B resolution).
File: audits/final/stages/test_3of5.md
Findings appended: 1 MODERATE (_manager/M-V4-METRIC-SEMANTICS-c16 open escalation confirmation)
[END OUTPUT: final_audit_stage]
