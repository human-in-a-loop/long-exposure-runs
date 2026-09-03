# CG Bass c8 Heartbeat Report

**Milestone:** `M-V4-PROFILES-1` (CG bass anchor liveness, v4 scope)
**Cycle:** 8
**Song:** Chicken Grease (`sha16 31a164f845f8e27e`)
**Run ID:** `run-2026-09-03T230000Z`
**Timestamp:** `2026-09-03T23:10:00Z`
**Verdict:** `V4_ANCHOR_LIVENESS_HOLDS`
**Rubric SHA-256:** `5f94e2b8ad161174e243c2e89569b6f816bd18663a1bdaa536a1d9b31fef812c`
**Heartbeat streak (v4):** 1
**Cycles since last operator input:** 1

## 1 · Opening

Cycle 8 is a **wait-on-operator heartbeat cycle** in v4 scope. c8
`live_guidance` carries only the standing `parallel_cycle_fanout_
guidance` and `campaign_anti_patterns` blocks — no operator directive
naming any of the three options in `_manager/M-V4-SHOWCASE-1-cg-bass-
acceptance-policy` (OPT1 accept sf2 INDETERMINATE / OPT2 refuse
SHOWCASE / OPT3 change threshold). Per c7 auditor handoff step 4, c8
runs a single-track anchor-liveness probe and advances no substantive
M-V4 milestone.

**Precedent:** v3 c9-c19 heartbeat chain (11 consecutive heartbeats
resolved by operator LANDS 2026-09-02 on Chicken Grease v3
reconstruction). v4 adapts the pattern with a smaller anchor set and a
distinct streak-10 auditor-reminder threshold (vs v3's streak-4).

## 2 · Anchor-liveness verdict

`V4_ANCHOR_LIVENESS_HOLDS`. All 9 anchors byte-identical pre==post
(`n_matched=9, n_mismatched=0`).

Artifact: `data/v4/profiles/31a164f845f8e27e/anchor_liveness_c8.json`
(SHA `9e15fd795ca9fa6a36e49bbd26774fbc348e8b6f79d347dd47879c32c8f95547`).

Three-way `rubric_hash` chain byte-equal:

- Doc SHA-256 (`docs/sound_match/cg_bass_anchor_liveness_c8_rubric.md`) = `5f94e2b8ad161174e243c2e89569b6f816bd18663a1bdaa536a1d9b31fef812c`
- `data/v4/profiles/31a164f845f8e27e/anchor_liveness_c8_rubric_hash.txt` content = `5f94e2b8ad161174e243c2e89569b6f816bd18663a1bdaa536a1d9b31fef812c`
- `anchor_liveness_c8.json.rubric_hash` = `5f94e2b8ad161174e243c2e89569b6f816bd18663a1bdaa536a1d9b31fef812c`

## 3 · c7 read-only re-verification

All 6 c7 deliverables byte-identical to their c7-recorded SHAs
(`c7_deliverables_all_match=true, n_matched=6, n_mismatched=0`).

Artifact: `data/v4/profiles/31a164f845f8e27e/c7_readonly_reverify_c8.json`
(SHA `601f6a2ebae8598a62f8b6d6fa639d2f99670b532d62813cbc446d099e4d4023`).

Highlighted anchors:

- `docs/sound_match/cg_bass_arc_closeout_c7_rubric.md` = `544a399569b8d2e9004c5ff85a60e65d3b553b826423d86755ed288050a1a81a` ✓
- `data/v4/profiles/31a164f845f8e27e/bass_arc_closeout.json` = `2e6d9c978e410dad21af817b2d4b759bfe7eda189bd333ef5e30f039308ead1a` ✓ (verdict `CG_BASS_ARC_EXHAUSTED_NO_CONFIRMED` still on disk)

## 4 · Operator directive check

`operator_directive_present = false`. c7 manager escalation
`_manager/M-V4-SHOWCASE-1-cg-bass-acceptance-policy` remains
`action_required` (severity `HIGH`, cycle 7). No re-emit, no supersede,
no amendment this cycle.

Artifact: `data/v4/profiles/31a164f845f8e27e/operator_directive_c8.json`.

## 5 · Anchor preservation (15 anchors pre==post byte-exact)

| # | Anchor | SHA-256 |
|---|---|---|
| 1 | `bass.json` | `11747a42cb1a8f7f…87a8f1c9` |
| 2 | `bass_v2.json` | `2a1cb340bffd1101…7e090462` |
| 3 | `bass_family_verdict.json` | `cbbdbebf00c30e2c…66c546228` |
| 4 | `bass_family2_verdict.json` | `1c6967aa3dc2d092…f1171a80` |
| 5 | `bass_family2_v1.json` | `503284c5e3adb3fb…ecc85561` |
| 6 | `data/v3/…/stems_6s/bass.wav` | `1bad871901294395…6e09ffd` |
| 7 | `scripts/sound_match/replay.py` (c6 post-fix) | `419d9558747eec61…c9f545` |
| 8 | `scripts/sound_match/family2_stem_sampled_spike.py` (c5) | `000c3ef68042f2da…6329e80` |
| 9 | `scripts/sound_match/family2_stem_sampled_builder.py` (c6) | `eaa8fb6cb513f342…e58f8234` |
| 10 | `cg_bass_arc_closeout_c7_rubric.md` | `544a399569b8d2e9…050a1a81a` |
| 11 | `closeout_c7_rubric_hash.txt` | `fc903c5125ecb826…dae0b19cee` |
| 12 | `bass_arc_closeout.json` | `2e6d9c978e410dad…9308ead1a` |
| 13 | `operator_directive_c7.json` | `ec06e0c4b9d3b118…7e4e87ef501e` |
| 14 | `anchor_preservation_post_c7.json` | `0847d68c79115d70…489b1a0292` |
| 15 | `cg_bass_arc_closeout_c7.md` | `8c9b2e891bb2677e…08cdc5219` |

`all_match=true, n_anchors=15, n_mismatch=0`.

Artifact: `data/v4/profiles/31a164f845f8e27e/anchor_preservation_post_c8.json`.

## 6 · Storage accounting

- `df -h /` before cycle: **83% used, 6.6 G free** (< 90% threshold ✓)
- Added disk this cycle: ~10 KB (2 docs + 4 JSONs + 1 hash file + POR
  append; no audio artifacts, no sweep outputs)
- `df -h /` after cycle: 83% (delta negligible)

## 7 · Cadence summary + c9 downstream branches

- `heartbeat_streak = 1` (v4 scope, first heartbeat after c7 close-out)
- `cycles_since_last_operator_input = 1`
- No substantive M-V4 milestone advanced

**Downstream branches for c9 auditor recommendation:**

- **Operator directive lands in c9 `live_guidance` naming OPT1/OPT2/OPT3**
  → c9 fires the chosen sub-option per c7 Track 3 conditional:
    - `OPT1`: adopt `bass_v2.json` as accepted CG bass profile,
      open `M-V4-PROFILES-1/cg-drums-sweep-launched` (next instrument
      per v4 spec order).
    - `OPT2`: emit `_plan/showcase-blocked-per-operator-opt2`,
      pre-register family-2 `per_note_pick` / `windowed_f0` lever set.
    - `OPT3`: author `docs/specs/v4_sound_matching_layer_rubric_v2.md`,
      run retroactive-CONFIRMED audit under lowered threshold.
- **No operator directive in c9 `live_guidance`** → `heartbeat_streak =
  2`. Continue heartbeat cadence with identical structure. Freshness-
  cache short-circuit warning fires at `heartbeat_streak >= 3` (c24
  `_plan/freshness-cache-short-circuit-policy` N=3 threshold adapted
  from orchestrator layer to auditor-visibility layer).
- **Anchor drift detected in c9** (any of the 15 anchors changes) → halt
  and escalate per `_manager/v4-anchor-drift-critical-cN` with the
  falsifying tuple `(name, expected_sha256, on_disk_sha256)`, severity
  `CRITICAL`, `action_required`.
- **Wait-on-operator cadence policy**: after `heartbeat_streak >= 10`
  with no operator input, auditor should escalate to the operator via a
  distinct manager event `_manager/M-V4-SHOWCASE-1-operator-reminder-
  cN`. (Precedent: v3 c8 policy fired reminder at streak=4 for
  wait-on-operator; v4 adopts streak=10 threshold given fewer active
  tracks pending.)

## 8 · FD compliance summary

| FD | Compliance |
|---|---|
| FD-1 (no tuning, no retry, no fallback) | ✓ heartbeat scope; no substantive advance |
| FD-6 (operator ear = LANDS authority) | ✓ c7 manager escalation left standing |
| FD-16b (no `--verify-det`) | ✓ not passed anywhere |
| FD-16c (per-family replay proofs preserved) | ✓ 9 anchors incl. sf2 + family-2 verdicts byte-identical |

**Additional discipline:**

- Env pin `env_pin_sha256 = 2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca` (canonical replay-time 7-key subset) recorded verbatim in `anchor_liveness_c8.json`
- No writes to `data/v3/deliveries/*`
- No edits to anything under `scripts/sound_match/`
- No `<parallel_cycle_fanout>` emitted (sequential single worker)
- No new test files this cycle (heartbeat precedent per v3 c9-c19 chain)
- No new manager events (c7 escalation untouched; drift escalation would fire only on anchor drift, which did not occur)

---

**Cycle 8 status:** CLOSED. Blocked on operator directive for
`M-V4-SHOWCASE-1` acceptance policy.
