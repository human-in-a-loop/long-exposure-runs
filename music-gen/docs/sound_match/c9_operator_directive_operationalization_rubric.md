---
created: 2026-09-03T23:30:00Z
cycle: 9
run_id: run-2026-09-03T233000Z
agent: worker
milestone: M-V4-PROFILES-1
---

# c9 Operator-Directive Operationalization Rubric

**Author:** worker · **Cycle:** 9 · **Date:** 2026-09-03

## 1. Scope

Operationalize the OPERATOR DIRECTIVE 2026-09-03 (three parts: acceptance /
anti-stall rule / immediate unblock) in a single multi-track cycle.

Frozen success criteria for c9:

  R1. `data/v4/deliveries/31a164f845f8e27e/cg_bass_pinned_profile.json`
      lands with `bass_v2` (profile_id `d62cd3b6-4521-5d4f-b840-87ef7800c48d`,
      profile sha `2a1cb340bffd11016c566467b0d313fb002c5949ce881968702846867e090462`)
      pinned as CG-bass WINNER, honest embedding_cos_vggish=0.4946 disclosure,
      family verdicts pinned (sf2 STILL_INDETERMINATE + family-2 RULED_OUT),
      acceptance_fork block naming CHOSEN=OPT1+OPT3 hybrid + REJECTED options,
      env_pin_sha256=`2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca`.

  R2. Ledger event supersedes `_manager/M-V4-SHOWCASE-1-cg-bass-acceptance-policy`
      with `supersedes_path` as `str` per c14 lemma (not list).

  R3. Wait-on-operator heartbeat cadence retired: `_plan/retire-v4-heartbeat-cadence-per-operator-2026-09-03`
      ledger event lands + POR line appended.

  R4. `scripts/sound_match/coarse_sweep_sf2_drums.py` authored as sibling to c1
      `coarse_sweep_sf2.py` (READ-ONLY anchor `c74c35bc61264c8846ed716dfd80011550ed081194d8be557c26f81d6d5ce51f`
      unmodified). Sweep launched detached under 7-key env pins verbatim
      (env_pin_sha256 identical to c1/c8) with score-and-delete hygiene wired
      in (≤500 MB working audio budget).

  R5. `scripts/sound_match/deliver_cg_ab_v4.py` scaffold lands + smoke test
      confirms missing-profile clean-fail; NO A/B render this cycle.

  R6. `data/v4/profiles/31a164f845f8e27e/anchor_preservation_pre_c9.json` +
      `anchor_preservation_post_c9.json` both hold with `all_match=true`,
      `n_mismatch=0` across the c9 anchor set.

  R7. POR tail appended with acceptance-fork block + heartbeat-retirement line
      (both this cycle, both honest).

## 2. Three-way rubric_hash chain

This doc's SHA-256 is pinned in `data/v4/profiles/31a164f845f8e27e/c9_rubric_hash.txt`
and re-referenced in every verdict-like JSON emitted this cycle
(`cg_bass_pinned_profile.json.rubric_hash_c9`, anchor_preservation_{pre,post}_c9.json).

## 3. Anchor set (11 items, per research_brief §read_only_anchors_do_not_modify + c8 liveness list)

Honest note: the research_brief abbreviated SHAs for `bass.replay_proof.json`
(`c69775040c...4ff019c`) and `bass_v2.replay_proof.json` (`832868d0ea...3aeac5`)
correspond to the render WAV SHAs recorded INSIDE the JSON payloads, not to
the JSON file SHAs themselves. The on-disk JSON-file SHAs are captured
authoritatively in the pre_c9/post_c9 snapshots (see §Anchor SHAs below).
Both are legitimate anchors; the discrepancy is naming, not drift.

Anchor SHAs (on disk at c9 top):

| Path                                                                                     | SHA-256 (on disk)                                                  |
|------------------------------------------------------------------------------------------|--------------------------------------------------------------------|
| `data/v3/deliveries/31a164f845f8e27e/cert_double_run_sha_table.json`                     | (materialized by pre-snapshot; canonical M-V4-CERT-1 certificate)  |
| `data/v4/profiles/31a164f845f8e27e/bass.json`                                            | `11747a42cb1a8f7f693f27c36f0c5e0fc60d0d44da13c877f984443487a8f1c9` |
| `data/v4/profiles/31a164f845f8e27e/bass_v2.json`                                         | `2a1cb340bffd11016c566467b0d313fb002c5949ce881968702846867e090462` |
| `data/v4/profiles/31a164f845f8e27e/bass.replay_proof.json`                               | `89746b07a327952e44d7d35d9f3e819d247ae579cdd214eb8f314629eb03fd81` |
| `data/v4/profiles/31a164f845f8e27e/bass_v2.replay_proof.json`                            | `4b9eea98052d6b2f54dcc7b87af334614c5ad56fb8c159eb6563c21533d5817f` |
| `data/v4/profiles/31a164f845f8e27e/bass_family_verdict.json`                             | `cbbdbebf00c30e2c2b0b7c6a575fa59c723a7d1294905eec12bbb2166c546228` |
| `data/v4/profiles/31a164f845f8e27e/bass_family2_verdict.json`                            | `1c6967aa3dc2d092f9f5ea8bd1942ff2b142f9c6534ad61897c9bf49f1171a80` |
| `data/v4/profiles/31a164f845f8e27e/bass_arc_closeout.json`                               | `2e6d9c978e410dad21af817b2d4b759bfe7eda189bd333ef5e30f039308ead1a` |
| `data/v4/profiles/31a164f845f8e27e/anchor_liveness_c8.json`                              | `9e15fd795ca9fa6a36e49bbd26774fbc348e8b6f79d347dd47879c32c8f95547` |
| `scripts/sound_match/coarse_sweep_sf2.py` (c1 anchor)                                    | `c74c35bc61264c8846ed716dfd80011550ed081194d8be557c26f81d6d5ce51f` |
| `scripts/sound_match/replay.py` (post-c6-fix)                                            | `419d9558747eec61e58b3450b9f57b9bd057a7f8d7a31dfd1ab02f4d63c9f545` |

## 4. FD compliance

- FD-1 (no tuning/retry/fallback): drums sweep uses fixed program set; no
  in-run parameter search shortcuts.
- FD-6 (operator ear = LANDS authority): CG-bass acceptance rests on operator
  directive, not on numeric threshold pass.
- FD-16b (no `--verify-det`): none anywhere in this cycle's code.
- FD-16c (per-family replay proofs as READ-ONLY anchors): sf2 + family-2
  replay proofs preserved byte-identical.

## 5. Halt rule

Any anchor drift detected in pre/post → CRITICAL halt via
`_manager/v4-anchor-drift-critical-c9` with falsifying `(name, expected, on_disk)`
tuple. Sweep-storage hygiene: abort if disk ≥ 90 % at any check.
