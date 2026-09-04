# Verify 3 of 5 — Slice C (V3-SPINE-2 unified driver + M-V4-CERT-1 + checkpointed driver + M-V3-RULES-1 first activation)

Delta-audit mode. Cycles 22–24 post-baseline slice.

## Scope
- c22 M-V3-SPINE-2 unified-driver + env-pin manifest module
- c22 Peach Dream first-unified-driver delivery (per operator directive point 5)
- c23 clone-0 reproduce-proofs (Chicken Grease + Rome) → REPRODUCE_PANEL_ONLY (authorizes c22 retirement contract)
- c23 clone-1 Peach Dream honest PARTIAL (session-boundary halt at stage 3/9 muscriptor probe 4/7)
- c23 clone-2 M-V3-RULES-1 first activation (76 rules over 4 operator-approved v3 deliveries)
- c24 stage-checkpointed driver + detached-launch helper (operator directive 2026-09-03)
- M-V4-CERT-1 end-to-end determinism certificate (double `--no-cache` run byte-identity)

## Byte-exact anchor verifications (POR narrative pins vs on-disk SHA-256 prefix-24)

| Anchor | Expected (24hex) | On-disk (24hex) | Match |
|---|---|---|---|
| `data/v3/deliveries/88d247468cb6d49f/cycle23/verdict.json` | `5cd0afdd674aa583` | `5cd0afdd674aa583cac3d00b` | ✅ |
| `data/v3/reproduce/c23/31a164f845f8e27e/reproduce_report.json` | `8b23c448afbc8596` | `8b23c448afbc8596b0194549` | ✅ |
| `data/v3/reproduce/c23/51e433ade2a845e1/reproduce_report.json` | `5cb0b78837d37cac` | `5cb0b78837d37cac1c3142ac` | ✅ |
| `data/v3/rules/rules_artifact.jsonl` (76 rules, 47,662 B) | `e19fb205b282dabb` | `e19fb205b282dabbf9f6ba38` | ✅ |
| `docs/specs/v3_rules_deterministic_extractor_spec_c23.md` | `e81ff589200f6d6b` | `e81ff589200f6d6b52d7a68f` | ✅ (path drift — see MINOR-1) |
| `data/v3/deliveries/31a164f845f8e27e/cert_run1/full_reconstruction.wav` | `cc919559b4508b6b` | `cc919559b4508b6bfe868fa5` | ✅ |
| `data/v3/deliveries/31a164f845f8e27e/cert_run2/full_reconstruction.wav` | `cc919559b4508b6b` | `cc919559b4508b6bfe868fa5` | ✅ (byte-equal to run1) |

## Env-pin certificate coherence (M-V4-CERT-1)
- `cert_run1/env_pin.json` → `env_pin_sha256 = 623df01f262ffd180c8497ce9bb06a2d4438b9239d60dd997304830b6571d38d`
- `cert_run2/env_pin.json` → `env_pin_sha256 = 623df01f262ffd180c8497ce9bb06a2d4438b9239d60dd997304830b6571d38d`
- Both env-pin SHAs byte-equal to the POR-narrated cert env pin.
- `docs/v3_determinism_certificate.md` contains `E2E_DETERMINISM_HOLDS` verdict token, `cc919559b4508b6b` reconstruction sha token, and `623df01f262ffd18` env-pin sha token in-line.
- Verdict internally consistent: two `--no-cache` runs produce byte-identical `full_reconstruction.wav` under identical `env_pin_sha256`. Passes FD-16(a) certificate re-issue trigger contract (env_pin change would flag).

## c22 unified driver + pipeline module presence
- `scripts/v3_spine/recreate_v3.py` — present.
- `scripts/v3_spine/v3_pipeline/env_pin.py` — present.

## c24 checkpointed driver + detached-launch helper presence
- `scripts/v3_spine/stage_cache.py` — present.
- `scripts/v3_spine/recreate_v3_checkpointed.py` — present.
- `scripts/v3_spine/launch_detached.py` — present.

## Peach Dream first-unified-driver delivery status (M-V3-FOCUS-1/peach-dream-first-unified-driver-delivery)
- POR row says c22 delivery + `verdict.json` at `data/v3/deliveries/88d247468cb6d49f/cycle22/`; superseded by c23 clone-1 honest PARTIAL.
- On-disk `cycle22/` contains only `env_pin.json` + `run.log` + `run_report.json` (no `verdict.json`). Consistent with the sub-leaf event `M-V3-FOCUS-1/peach-dream-first-unified-driver-delivery/c23-partial-honest` which pins the authoritative verdict at `cycle23/verdict.json` sha `5cd0afdd674aa583…` — verified.
- `cycle23/verdict.json` shape: `verdict = V3_FOCUS_SONG_PARTIAL`, `failure_mode = session_boundary_termination`, `failure_mode_named_block = stage_3_of_9_muscriptor`, `blocked_on_root_conductor = true`, `rubric_hash_v2 = c49db5a12e955f26…016451a`, `rubric_hash_v3 = bea618721ebb74b1…c99a0d6`. All fields match POR narrative pins.
- Session-boundary termination is disclosed honestly and retired by the c24 checkpointed-driver + `M-V3-FOCUS-1/peach-dream-resume-checkpointed` operator directive.

## c23 reproduce-proofs
- Both `data/v3/reproduce/c23/{31a164f845f8e27e,51e433ade2a845e1}/reproduce_report.json` carry `verdict = REPRODUCE_PANEL_ONLY` on disk — matches POR narrative.
- REPRODUCE_PANEL_ONLY is the expected outcome when the pre-c22 anchor's env-pin diverges from the c22 unified driver's env-pin manifest (documented in c23 report §8), and is the trigger clause for `M-V3-SPINE-2/reproduce-proof-authorizes-c24-retirement` in POR.

## M-V3-RULES-1 first activation (c23 clone-2)
- Rules artifact `data/v3/rules/rules_artifact.jsonl`: sha `e19fb205b282dabb…`, 47,662 bytes, 76 lines (rules), all byte-exact vs POR narrative pins.
- Spec doc `docs/specs/v3_rules_deterministic_extractor_spec_c23.md`: sha `e81ff589200f6d6b…` — byte-exact vs POR narrative pin. Path differs from POR text (see MINOR-1 below).

## Findings summary
- CRITICAL: 0 appended this slice.
- MODERATE: 0 appended this slice.
- MINOR: 1 appended (path-drift disclosure on v3_rules spec doc).

## MINOR (logged, not investigated further per audit philosophy)
- MINOR-1: POR narrates the v3_rules spec doc at `docs/v3_rules_deterministic_extractor_spec_c23.md`; on-disk canonical location is `docs/specs/v3_rules_deterministic_extractor_spec_c23.md`. SHA byte-exact under the on-disk path. Cosmetic path-drift only; the three-way `rubric_hash_v3_rules` chain (doc SHA == `data/v3/rules/rubric_hash.txt` == verdict field) remains anchor-preserving.

## Chain integrity
Slice C chain (c22 → c23 → c24 + M-V4-CERT-1) intact. All 7 verdict/artifact SHAs byte-exact against plan-of-record narrative pins. Unified-driver, env-pin manifest, and stage-checkpointed driver modules all present. Certificate double-run byte-identity holds under identical env_pin_sha256. First activation of M-V3-RULES-1 emits 76 typed rules deterministically over the four operator-approved v3-rendered corpus deliveries; artifact reproduces byte-identically per POR-recorded byte-determinism ×2 proof.
