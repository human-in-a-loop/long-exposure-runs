# CG Bass Anchor-Liveness Rubric — Cycle 8 (v4 heartbeat)

**Milestone:** `M-V4-PROFILES-1` (arc: CG bass anchor liveness, v4 scope)
**Cycle:** 8
**Song:** Chicken Grease (`sha16 31a164f845f8e27e`)
**Instrument:** bass
**Run ID:** `run-2026-09-03T230000Z`
**Timestamp:** `2026-09-03T23:10:00Z` (SOURCE_DATE_EPOCH-anchored)
**Rubric SHA-256 pinned in:** `data/v4/profiles/31a164f845f8e27e/anchor_liveness_c8_rubric_hash.txt`

## 1 · Statement

Cycle 8 is a v4-scoped **wait-on-operator heartbeat cycle** per c7 auditor
handoff step 4 (executed because c8 `live_guidance` carries no operator
directive naming any of the three options in
`_manager/M-V4-SHOWCASE-1-cg-bass-acceptance-policy`). Its single
substantive track is an anchor-liveness probe that verifies the
`M-V4-PROFILES-1/cg-bass` arc's read-only anchors have not drifted
under wait-on-operator cadence. It advances no substantive M-V4
milestone. The manager escalation from c7 is left standing untouched.

Adapts the v3 c9-c19 heartbeat pattern (11 consecutive heartbeats
resolved by operator LANDS 2026-09-02 on Chicken Grease v3
reconstruction) to v4 scope with a smaller anchor set (fewer active
arcs pending) and a distinct escalation threshold.

## 2 · Frozen 2-verdict enum

| Verdict | Firing condition |
|---|---|
| `V4_ANCHOR_LIVENESS_HOLDS` | All 6 v4 anchors byte-identical pre==post **AND** all 3 script anchors byte-identical pre==post. |
| `V4_ANCHOR_LIVENESS_FAILS` | Any of the 9 anchor SHAs drifts from the expected pin. Halt cycle per FD-1 and escalate as `_manager/v4-anchor-drift-critical-c8` (severity `CRITICAL`, `action_required`) with the falsifying tuple `(name, expected_sha256, on_disk_sha256)`. |

## 3 · Three-way `rubric_hash` chain

Byte-equality holds across:

1. This document's SHA-256 (`sha256(docs/sound_match/cg_bass_anchor_liveness_c8_rubric.md)`)
2. Content of `data/v4/profiles/31a164f845f8e27e/anchor_liveness_c8_rubric_hash.txt`
3. `data/v4/profiles/31a164f845f8e27e/anchor_liveness_c8.json.rubric_hash`

## 4 · Anchor list (9 anchors)

Expected SHA-256 values from c7 auditor snapshot (`anchor_preservation_post_c7.json`):

| # | Anchor | Expected SHA-256 |
|---|---|---|
| 1 | `data/v4/profiles/31a164f845f8e27e/bass.json` | `11747a42cb1a8f7f693f27c36f0c5e0fc60d0d44da13c877f984443487a8f1c9` |
| 2 | `data/v4/profiles/31a164f845f8e27e/bass_v2.json` | `2a1cb340bffd11016c566467b0d313fb002c5949ce881968702846867e090462` |
| 3 | `data/v4/profiles/31a164f845f8e27e/bass_family_verdict.json` | `cbbdbebf00c30e2c2b0b7c6a575fa59c723a7d1294905eec12bbb2166c546228` |
| 4 | `data/v4/profiles/31a164f845f8e27e/bass_family2_verdict.json` | `1c6967aa3dc2d092f9f5ea8bd1942ff2b142f9c6534ad61897c9bf49f1171a80` |
| 5 | `data/v4/profiles/31a164f845f8e27e/bass_family2_v1.json` | `503284c5e3adb3fb1f1eaefde293f55dc465376d04a1203112ccf760ecc85561` |
| 6 | `data/v3/deliveries/31a164f845f8e27e/cert_run1/stems_6s/bass.wav` | `1bad871901294395c1b1ad1c97689e07d879f48aa8b9fc953ea6981d76e09ffd` |
| 7 | `scripts/sound_match/replay.py` (c6 post-fix) | `419d9558747eec61e58b3450b9f57b9bd057a7f8d7a31dfd1ab02f4d63c9f545` |
| 8 | `scripts/sound_match/family2_stem_sampled_spike.py` (c5) | `000c3ef68042f2da6971257bf97f950271850005e5889d9c72dfd5b106329e80` |
| 9 | `scripts/sound_match/family2_stem_sampled_builder.py` (c6) | `eaa8fb6cb513f342ff716611ab091ad0f498cfd97e47c8b0443118aee58f8234` |

Rows 1-6 are v4 substantive anchors (profile + verdict + reference stem);
rows 7-9 are READ-ONLY script anchors under `scripts/sound_match/`
(per c7 constraint "no edits to anything under scripts/sound_match/").

## 5 · Downstream (this heartbeat does NOT)

- advance `M-V4-SHOWCASE-1` (blocked on operator per c7 escalation)
- reopen any family (sf2 `STILL_INDETERMINATE` per c4 verdict; family-2
  `FAMILY2_RULED_OUT` per c6 verdict — both READ-ONLY anchors)
- alter the frozen 0.60/0.40 `embedding_cos_vggish` CONFIRMED/RULED_OUT
  thresholds
- pin `bass_v2.json` as the accepted CG bass profile (requires operator
  OPT1 directive)
- open next-instrument (drums) profiling (requires OPT1 or explicit
  operator directive)
- re-sweep any family
- emit any new manager event other than the CRITICAL drift escalation if
  §c8.2 detects anchor drift

Downstream branches for the c9 auditor recommendation:

- **Operator directive in c9 live_guidance** naming `OPT1`/`OPT2`/`OPT3`
  → fire the chosen sub-option per c7 Track 3 conditional (drums sweep,
  family-2 per_note_pick attempt, or rubric v4.2 override).
- **No operator directive in c9 live_guidance** → `heartbeat_streak=2`,
  identical structure to c8 with the streak counter +1. Freshness-cache
  short-circuit warning fires at `heartbeat_streak >= 3` (c24
  `_plan/freshness-cache-short-circuit-policy` N=3 threshold).
- **Anchor drift detected in c9** (any of the 15 anchors changes) → halt
  and escalate per `_manager/v4-anchor-drift-critical-cN` with the
  falsifying tuple.
- **Wait-on-operator cadence policy**: after `heartbeat_streak >= 10`
  with no operator input, auditor should escalate to the operator via a
  distinct manager event
  `_manager/M-V4-SHOWCASE-1-operator-reminder-cN` (precedent: v3 c8
  fired reminder at streak=4; v4 adopts streak=10 threshold given fewer
  active tracks pending).

---

**FD compliance:** FD-1 (no tuning, no retry, no fallback); FD-6
(operator ear = LANDS authority); FD-16b (no `--verify-det`); FD-16c
(per-family replay proofs preserved as READ-ONLY anchors).
