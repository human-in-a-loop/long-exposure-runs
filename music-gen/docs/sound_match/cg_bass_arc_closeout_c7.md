<!-- created: 2026-09-03T22:00:00Z cycle: 7 run_id: run-2026-09-03T220000Z agent: worker milestone: M-V4-PROFILES-1 -->

# Chicken Grease Bass Profiling Arc — c7 Close-Out Report

## 1. Opening

c7 is an honest close-out cycle for the CG bass profiling arc plus a
manager escalation to the operator on M-V4-SHOWCASE-1 acceptance policy.
No sweep, no re-render, no re-open of c4 sf2 or c6 family-2 verdicts.
Two mandatory tracks land; one conditional track does not fire (no
operator directive in c7 live_guidance).

## 2. Family verdict summary

| Family                 | Cycle | Top-1 embedding_cos_vggish | Verdict                     |
|------------------------|-------|----------------------------|-----------------------------|
| sf2 (FluidR3_GM)       | c4    | 0.4946 (max, prog 19)      | STILL_INDETERMINATE         |
| stem_sampled_v1        | c6    | 0.0896                     | FAMILY2_RULED_OUT           |
| **Frozen CONFIRMED bar** | —   | **≥ 0.60**                 | —                           |
| **Frozen RULED_OUT bar** | —   | **< 0.40**                 | —                           |

Neither family CONFIRMED. Both verdicted honestly under c5-spec lever
sets. First-class negative finding on the CG bass arc per FD-1.

## 3. Best-available profile

`bass_v2.json` (SHA `2a1cb340bffd1101…`, profile_id
`d62cd3b6-4521-5d4f-b840-87ef7800c48d`) — sf2, FluidR3_GM bank 0
program 33 (Electric Bass Finger), gain 0.5, reverb_send 0.3, post
`EQ_only`, sample_rate 44100. Top-1 by the frozen composite objective on
the c3 stage-2b 216-cell leaderboard. Its own embedding_cos_vggish =
0.20353, below the CONFIRMED bar; recorded as STILL_INDETERMINATE at
family level because the max embedding_cos on the sf2 leaderboard (0.4946
at prog 19) is between the frozen 0.40 and 0.60 gates.

`bass.json` (c2 sf2 prog 17 Drawbar Organ) remains on disk as legacy;
`bass_family2_v1.json` (c6 stem_sampled_v1) remains on disk as
RULED_OUT provenance.

## 4. Three operator options (M-V4-SHOWCASE-1 acceptance policy)

Presented neutrally per FD-6. Operator ear is the sole LANDS authority.

**OPTION 1 — ACCEPT_SF2_INDETERMINATE_TOP1**
Pin `bass_v2.json` (sf2 prog 33 Electric Bass Finger, embedding_cos
0.4946 family-max / 0.20353 for the selected preset) as the CG bass
profile for M-V4-SHOWCASE-1.
- Pros: sf2 replay chain now trustworthy (c6 program-invariance fix);
  prog 33 is the source-of-truth GM bass; single closest match by the
  frozen composite objective; SHOWCASE unblocks immediately; audibility
  validation is the operator ear.
- Cons: below the frozen 0.60 CONFIRMED bar (~0.11 embedding_cos units
  short of CONFIRMED at family max; ~0.40 units short at the selected
  preset).
- Cost: zero — SHOWCASE proceeds with existing profile.

**OPTION 2 — REFUSE_SHOWCASE_ON_CG_BASS**
Block M-V4-SHOWCASE-1 until a CONFIRMED profile lands.
- Pros: honors FD-1 no-tuning; preserves rubric integrity.
- Cons: requires reopening family-2 with a different lever set
  (per_note_pick or windowed_f0 per c5 spec §Builder sketch), OR
  opening a new render family (e.g., commercial sample-based VST via
  DawDreamer with sfizz fallback). Both are multi-cycle work.
- Cost: ~2–8 hours per new lever-set attempt (per c3-brief cost basis),
  plus SHOWCASE remains blocked until CONFIRMED.

**OPTION 3 — CHANGE_THE_CONFIRMED_THRESHOLD**
Lower 0.60 to a value at which one of the existing top-1s lands (e.g.
0.45 would let sf2 CONFIRMED at 0.4946; 0.40 would still leave family-2
at 0.0896 RULED_OUT).
- Pros: allows honest acceptance under a newly-frozen rubric.
- Cons: DESTRUCTIVE to FD-1 pre-registration doctrine — the 0.60/0.40
  thresholds are frozen. Operator must explicitly override the frozen
  rubric and stamp a v4.rubric.2 pre-reg document naming the change.
- Cost: rubric-freeze precedent broken; downstream cycles will need to
  justify why other frozen thresholds are still binding.

## 5. Anchor preservation

Nine anchors snapshotted pre and post; all_match=true, n_diff=0.

| Anchor                                              | SHA-256                                                            |
|-----------------------------------------------------|--------------------------------------------------------------------|
| `bass.json`                                         | `11747a42cb1a8f7f…87a8f1c9`                                        |
| `bass_v2.json`                                      | `2a1cb340bffd1101…7e090462`                                        |
| `bass_family_verdict.json`                          | `cbbdbebf00c30e2c…66c546228`                                       |
| `bass_family2_verdict.json`                         | `1c6967aa3dc2d092…f1171a80`                                        |
| `bass_family2_v1.json`                              | `503284c5e3adb3fb…ecc85561`                                        |
| `stems_6s/bass.wav`                                 | `1bad871901294395…6e09ffd`                                         |
| `scripts/sound_match/replay.py` (c6 post-fix)       | `419d9558747eec61…c9f545`                                          |
| `scripts/sound_match/family2_stem_sampled_spike.py` | `000c3ef68042f2da…6329e80`                                         |
| `scripts/sound_match/family2_stem_sampled_builder.py` | `eaa8fb6cb513f342…f8234`                                          |

## 6. Storage accounting

- df before c7: 83% used (192 GB free out of 252 GB).
- df after c7: 83% (net add ~10 KB: two docs + two JSONs + one hash
  file + this report).
- No new audio artifacts this cycle.
- Well below the 90% hard limit and ≤500 MB per-instrument working audio
  bound.

## 7. Track-3 status

**NOT-FIRED.** c7 live_guidance contains only `parallel_cycle_fanout_guidance`
and `campaign_anti_patterns` blocks; no operator directive names an
`OPTn` acceptance choice. Recorded in
`data/v4/profiles/31a164f845f8e27e/operator_directive_c7.json`
(`operator_directive_present: false`). Single bookkeeping ledger event
emitted under `_plan/c7-track-3-not-fired-no-operator-directive`.

## 8. Downstream branches for c8 auditor

- **Operator picks OPT1** → c8 opens cg-drums profiling arc under the
  v4 spec instrument order (drums next after bass). Adopt `bass_v2.json`
  as CG bass profile.
- **Operator picks OPT2** → c8 opens family-2 per_note_pick lever-set
  attempt on CG bass; c7's rubric pre-registers only, no sweep runs
  until c8.
- **Operator picks OPT3** → c8 opens rubric v4.2 threshold-override doc
  + retroactive-CONFIRMED audit of existing STILL_INDETERMINATE
  profiles.
- **Operator silent** → c8 defaults to wait-on-operator heartbeat cycle
  (single track = c6-anchor-liveness probe verifying `scripts/sound_match/
  replay.py` post-fix SHA + both family verdict SHAs byte-identical; no
  substantive M-V4 advance). Precedent: c5→c19 heartbeat chain under v3
  wait-on-operator cadence policy adapted for v4 scope.

## 9. Cumulative arc note

The c1→c7 arc took **seven cycles** to honestly exhaust two render
families on the mandatory Chicken Grease bass cell of M-V4-PROFILES-1:

- c1: coarse sf2 sweep (15 presets); prog 33 rank 8, top-1 organ 19.
- c2: sf2 stage-2 fine fit (top-5 × 3×3×4 = 180 cells); top-1
  Drawbar Organ (prog 17); `bass.json` profile v1 emitted; sf2 replay
  proof HOLDS.
- c3: sf2 stage-2b (top-5 ∪ prog 33, 216 cells) with EQ v2; prog 33 top-1
  by composite; sf2 verdict STILL_INDETERMINATE (top-1 embedding_cos <
  0.60 but not < 0.40).
- c4: family verdict pinned STILL_INDETERMINATE; `bass_v2.json` v2 sibling
  emitted; per-family replay proof HOLDS.
- c5: family-2 (stem-sampled) spec + spike; replay-program-invariance
  CRITICAL identified in `scripts/sound_match/replay.py`.
- c6: CRITICAL fix landed (mido MIDI rewrite; 3/3 regression tests
  PASS); refreshed replay proofs HOLD; family-2 builder emits
  `bass_family2_v1.json`; family-2 verdict FAMILY2_RULED_OUT at
  embedding_cos_vggish = 0.0896.
- c7: this close-out. Neither family CONFIRMED. Escalated to operator.

Remaining 24 profile cells (4 non-CG focus songs × 6 instruments each,
plus the 5 non-bass CG cells) queue behind the SHOWCASE acceptance
decision. Under OPT1, cg-drums opens c8; under OPT2, the CG bass cell
reopens; under OPT3, all cells re-audit against the new threshold.
