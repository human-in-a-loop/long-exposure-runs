---
created: 2026-09-03T23:50:00Z
cycle: 9
run_id: run-2026-09-03T233000Z
agent: worker
milestone: M-V4-PROFILES-1
---

# c9 Cycle Report — Operator Directive Operationalization

**Author:** worker · **Cycle:** 9 · **Date:** 2026-09-03
**Rubric:** `docs/sound_match/c9_operator_directive_operationalization_rubric.md`
(SHA `96e09627056412ad5af4c9f892b2f918d52e8c22bbf090bb6623861ae56fd58d`)

## 1. Operator directive (verbatim)

Live-guidance from operator, 2026-09-03, three parts:

  (1) ACCEPTANCE: bass_v2 (profile_id `d62cd3b6-4521-5d4f-b840-87ef7800c48d`,
      `data/v4/profiles/31a164f845f8e27e/bass_v2.json`) is ACCEPTED as the
      Chicken Grease bass WINNER. The frozen absolute `embedding_cos_vggish
      >= 0.60` winner-acceptance bar is RETIRED as a kill gate; the binding
      spec defines the winner as the best composite candidate across families
      (relative). `embedding_cos` is one weighted component (0.25), not a
      gate. Absolute floors remain valid for RULING OUT degenerate candidates
      only — family-2 `FAMILY2_RULED_OUT` at 0.0896 stands. Record 0.4946
      honestly.

  (2) STANDING ANTI-STALL RULE: NO WAIT-ON-OPERATOR HEARTBEAT CYCLES IN V4.
      The v3 c9-c19 heartbeat chain is a BANNED PATTERN. On any policy fork
      mid-milestone: pick + record + proceed same cycle.

  (3) UNBLOCK NOW: M-V4-SHOWCASE-1 unblocked with bass_v2. Continue
      M-V4-PROFILES immediately — drums / piano / guitar / other.

## 2. Six tracks executed

| # | Track                                       | Status                    | Artifact                                                                                                                   |
|---|---------------------------------------------|---------------------------|----------------------------------------------------------------------------------------------------------------------------|
| 1 | acceptance_fork_por_and_manifest            | LANDS                     | `data/v4/deliveries/31a164f845f8e27e/cg_bass_pinned_profile.json` (sha `aa9b36be3f2e6748ba144845e7a7dbce15aee5f1bc354ed0c12392e4f3722dc7`) + POR block |
| 2 | supersede_c7_manager_escalation             | LANDS                     | ledger event with `supersedes_path` (str per c14 lemma) → `_manager/M-V4-SHOWCASE-1-cg-bass-acceptance-policy` |
| 3 | retire_heartbeat_cadence                    | LANDS                     | ledger event `_plan/retire-v4-heartbeat-cadence-per-operator-2026-09-03` + POR retirement line |
| 4 | cg_drums_stage1_sweep                       | PARTIAL — script authored + dry-run OK; **launch DEFERRED to c10** | `scripts/sound_match/coarse_sweep_sf2_drums.py` + `data/v4/profiles/31a164f845f8e27e/drums_sweep_stage1/run_manifest.json` (dry-run manifest) |
| 5 | cg_ab_delivery_scaffolding                  | LANDS (scaffold + smoke)  | `scripts/sound_match/deliver_cg_ab_v4.py` + `data/v4/deliveries/31a164f845f8e27e/scaffold_smoke_test.json` (4 profiles missing as expected) |
| 6 | anchor_preservation_snapshot                | LANDS                     | `data/v4/profiles/31a164f845f8e27e/anchor_preservation_{pre,post}_c9.json`; 11/11 match |

## 3. Track 4 partial — honest first-class finding

`statvfs` reports **97.4 %** root disk usage at c9 top (`df -h` showed 83 %
due to reserved blocks). The brief's own sweep-storage hygiene rule aborts
at ≥ 90 %. Consequences:

  - `coarse_sweep_sf2_drums.py` was authored end-to-end as sibling to the
    c1 anchor `coarse_sweep_sf2.py` (SHA `c74c35bc61264c8846ed716dfd80011550ed081194d8be557c26f81d6d5ce51f`
    unmodified — verified in `anchor_preservation_post_c9.json`).
  - Dry-run `--dry-run` smoke test passed end-to-end under the 7-key env
    pins verbatim: extracted 186 drums note-on events from `merged.mid`,
    computed ref stem LUFS-I proxy ≈ −14.4 dBFS, SF2 SHA verified.
  - Detached fluidsynth launch was **not** attempted — invoking it against
    the hygiene contract is a bigger risk than deferring it. Launch and
    stage-1 completion are queued for c10 the moment disk clears below the
    ceiling (either via workspace cleanup or reserved-block release).
  - Score-and-delete + top-K retention + per-cell disk sanity are all
    wired into the script (`--score-and-delete --keep-top 3
    --max-audio-mb 500 --disk-abort-pct 90.0`); the whole hygiene contract
    is in place, waiting only on disk headroom.

## 4. Track 1 — acceptance fork, honest disclosure

`data/v4/deliveries/31a164f845f8e27e/cg_bass_pinned_profile.json` pins:

  - **profile** `bass_v2.json` (sha `2a1cb340bffd11016c566467b0d313fb002c5949ce881968702846867e090462`,
    profile_id `d62cd3b6-4521-5d4f-b840-87ef7800c48d`).
  - **replay proof** `bass_v2.replay_proof.json` (sha `4b9eea98052d6b2f54dcc7b87af334614c5ad56fb8c159eb6563c21533d5817f`).
  - **family verdicts** sf2 `STILL_INDETERMINATE` + family-2 `FAMILY2_RULED_OUT`.
  - **honest disclosure** `embedding_cos_vggish = 0.4946` with the string
    "best available across 216-cell sweep; below aspirational 0.60"; the
    aspirational bar is recorded as `retired` and the 0.40 absolute floor
    is recorded as `retained for ruling out degenerate candidates only`.
  - **acceptance_fork** `{chosen: "OPT1+OPT3 per operator 2026-09-03",
    rejected: ["OPT2_REFUSE_SHOWCASE", "OPT3_THRESHOLD_ONLY"],
    operator_authority: "2026-09-03 live_guidance directive part (1)"}`.
  - **env_pin_sha256** `2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca`
    (replay-time 7-key subset, byte-equal to c8 baseline).

## 5. Track 6 — anchor preservation

11 anchors snapshotted pre and post; all 11 byte-identical, 0 missing,
0 mismatched. Honest note: the research_brief abbreviated SHAs for
`bass.replay_proof.json` and `bass_v2.replay_proof.json` correspond to
the render WAV SHAs recorded INSIDE the JSON payloads, not to the JSON
file SHAs themselves. The on-disk JSON-file SHAs (`89746b07…` and
`4b9eea98…`) are captured authoritatively and match c8's silent baseline
(neither JSON was rewritten this cycle).

## 6. Auditor-gate quick reference (against §research_brief `auditor_gate_checklist_for_c9`)

| # | Gate                                                                | Outcome |
|---|---------------------------------------------------------------------|---------|
| 1 | Operator directive parts (1)(2)(3) recorded verbatim in POR         | PASS (§1 of this doc + POR acceptance-fork block) |
| 2 | cg_bass_pinned_profile.json exists with acceptance-fork provenance  | PASS |
| 3 | embedding_cos=0.4946 honestly disclosed (not hidden, not inflated)  | PASS (`honest_embedding_cos_disclosure` block) |
| 4 | c7 manager escalation superseded with supersedes_path as STRING     | PASS (ledger event, str per c14 lemma) |
| 5 | Heartbeat cadence formally retired in POR + ledger                  | PASS |
| 6 | cg-drums sweep script authored as sibling (c1 anchor not edited)    | PASS (c1 SHA byte-identical in anchor_preservation_post_c9) |
| 7 | cg-drums sweep launched detached with 7-key env pins                | PARTIAL — dry-run OK; **detached launch deferred to c10** per disk hygiene |
| 8 | Sweep-storage hygiene wired into drums script                       | PASS (score-and-delete + top-K + ≤500 MB + disk-abort-pct) |
| 9 | df check emitted before launch (statvfs 97.4 %, above 90 %)         | PASS (honest report; abort behaviour verified) |
| 10 | CG A/B driver scaffolded but NOT rendered                          | PASS |
| 11 | Anchor preservation pre+post c9 byte-identical for all 11 anchors  | PASS (11/11 match) |
| 12 | No re-open of terminal-validated milestones (M-V4-CERT-1)          | PASS |
| 13 | No re-open of READ-ONLY family verdicts                            | PASS |
| 14 | Rubric hash three-way chain for any new verdict this cycle         | PASS (`c9_rubric_hash.txt` byte-equal to doc SHA; pinned in manifest/pre/post) |
| 15 | FD-1 respected: no tuning/retry/fallback in drums sweep            | PASS |
| 16 | FD-16b respected: no --verify-det anywhere                         | PASS (grep-clean under scripts/sound_match/) |
| 17 | FD-16c respected: replay proof plan per family per song for drums  | PASS (drums stage-1 dry-run manifest cites this scope) |
| 18 | Sequential single-worker (no fanout)                               | PASS |
| 19 | Anti-stall rule respected: cycle advances ≥1 milestone             | PASS (SHOWCASE unblocked + PROFILES drums-sweep-scaffolded) |
| 20 | c9 rubric doc authored                                             | PASS |

## 7. Handoff to c10

  1. Disk-hygiene resolution first — cannot launch drums sweep at 97.4 %.
  2. If disk clears: launch `coarse_sweep_sf2_drums.py` detached with the
     dry-run-verified command, complete stage-1, emit family verdict.
  3. Then piano stage-1 sweep (sibling script under sound_match/).
  4. Continue rotation through remaining instruments per anti-stall rule.
  5. Full CG A/B render only after all 5 CG instrument profiles land.
