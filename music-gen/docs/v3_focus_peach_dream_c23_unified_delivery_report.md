---
created: 2026-09-03T00:23:30Z
run_id: run-2026-09-02T210000Z
cycle: 23
clone: clone-1
fork: d5530f8d1ccc
agent: worker
milestone: M-V3-FOCUS-1/peach-dream-first-unified-driver-delivery
verdict: V3_FOCUS_SONG_PARTIAL
failure_mode: session_boundary_termination
---

# Peach Dream c23 clone-1 — first-unified-driver delivery report (PARTIAL)

**Song**: Peach Dream (`audio_sha16 = 88d247468cb6d49f`)
**Section**: operator, `t_start_s = 172.87256`, `t_end_s = 202.87256` from `focus_set_v2.json`
**Cycle**: 23 (post-c22 DETERMINISM CONSOLIDATION; first substantive activation of the c22 unified driver)
**Verdict**: `V3_FOCUS_SONG_PARTIAL` — `failure_mode: session_boundary_termination`
**verdict.json SHA**: `5cd0afdd674aa583cac3d00b157888bb7c0d83d5e5cc8b01c301992fb82e100a`
**c20 backref**: `d9bc2f590e1af21455cc3e71932af60b8bcff3f8ddca409df9e8210eac6dc222` (PARTIAL predecessor; NOT retired this cycle)

## Executive summary

This cycle is honest-PARTIAL, not LANDS. The c22 unified driver
(`scripts/v3_spine/recreate_v3.py`, SHA `72e80ee82cd21dbd…`) was launched
under all brief-mandated env pins on the operator section of Peach Dream. It
completed stages 1/9 (slice) and 2/9 (rehtdemucs, byte-det ×2 holds) and
reached stage 3/9 muscriptor, where it completed 3 of 7 probes fully
(drums, bass, guitar — json+mid each) plus half of the `other` probe (json
only, mid pending) before the session-boundary event terminated the
background process. Per research brief REV 3 §5 auditor watch item, a
third in-session restart was declined; honest PARTIAL emitted instead
under label `failure_mode: session_boundary_termination`.

**Every discipline gate that could be evaluated at this stage held**:
178-anchor preservation `n_byte_diff=0, n_missing=0`; both three-way rubric
chains byte-equal; c22 driver + c22 env_pin module SHAs byte-identical
pre==post; c33 palette renderer SHA byte-identical pre==post; c5 CG operator-
blessed WAV byte-identical pre==post; c20 predecessor byte-identical pre==post.

**Every artifact whose gate required stages 4-9 is honestly missing**:
`manifest.json`, `env_pin.json`, `merged.mid`, `full_reconstruction.wav`,
`original_ab.wav`, `reconstruction_ab.wav`, `tempo_choice.json`, `panel.json`,
`panel.tsv`, per-track WAVs, remaining muscriptor probes.

## §a Delivery SHAs

Actually-produced artifacts (only 3 of the 12 required for LANDS):

| artifact | path | SHA-16 | present |
|---|---|---|---|
| verdict.json (this cycle, PARTIAL) | `data/v3/deliveries/88d247468cb6d49f/cycle23/verdict.json` | `5cd0afdd674aa583…` | ✓ |
| anchor_preservation_pre.json | `data/v3/deliveries/88d247468cb6d49f/cycle23/anchor_preservation_pre.json` | 178-anchor snapshot | ✓ |
| anchor_preservation_post.json | `data/v3/deliveries/88d247468cb6d49f/cycle23/anchor_preservation_post.json` | 180-anchor snapshot (178 shared, +2 new scratch) | ✓ |
| run.log | `data/v3/deliveries/88d247468cb6d49f/cycle23/run.log` | driver output through stage 3/9 muscriptor drums | ✓ |
| merge_report.md (sandbox fallback) | `data/v3/deliveries/88d247468cb6d49f/cycle23/merge_report.md` | this handoff | ✓ |
| manifest.json (with env_pins block) | (stage 9 assemble_delivery never ran) | — | ✗ |
| env_pin.json (self-anchor) | (stage 9 never ran) | — | ✗ |
| original_ab.wav | (stage 8 mix_match never ran) | — | ✗ |
| reconstruction_ab.wav | (stage 8 never ran) | — | ✗ |
| full_reconstruction.wav | (stage 8 never ran) | — | ✗ |
| merged.mid | (stage 6 merge never ran) | — | ✗ |
| tempo_choice.json | (stage 4 tempo_map never ran) | — | ✗ |
| panel.json / panel.tsv | (stage 9 panel_measure never ran) | — | ✗ |
| per_track/<5>.wav | (stage 7 render_per_track never ran) | — | ✗ |
| muscriptor/{piano,vocals,full_mix}.{json,mid} + muscriptor/other.mid | (stage 3 terminated mid-flight) | — | ✗ |
| run_report.json | (driver never reached `wrote data/v3/deliveries/…/run_report.json`) | — | ✗ |

Scratch state (produced under `data/v3_spine/88d247468cb6d49f/operator_section_c23_unified/`):

| scratch artifact | SHA-16 |
|---|---|
| section.wav | `b278eae61718854b…` |
| rc9_6stem/bass.wav | `cfc36c931cc24972…` |
| rc9_6stem/drums.wav | `5cce25ad039bd4ab…` |
| rc9_6stem/guitar.wav | `70c8b2b41dd737fb…` |
| rc9_6stem/other.wav | `b637cf0f28be3bb9…` |
| rc9_6stem/piano.wav | `bc4452725a27c328…` |
| rc9_6stem/vocals.wav | `31e7513504c2dbdb…` |
| muscriptor/drums.{json,mid} | `59753283a665406d…`, `3553650b23532309…` |
| muscriptor/bass.{json,mid} | `47cf6e6f1e97f709…`, `d5aaf1dbab9875df…` |
| muscriptor/guitar.{json,mid} | `4f53cda18c2baa0c…` (canonical-empty), `b4134d5cce88b904…` |
| muscriptor/other.json (mid pending) | `bd37145f8dbc5187…` |

## §b Three-way rubric chains

Both chains byte-equal to the expected constants pinned in the research brief and the c22 unified-driver spec.

**`rubric_hash_v2` chain (v3-spine, c4 anchor)**:

| element | SHA-256 |
|---|---|
| `docs/v3_spine_rubric_v2.md` (doc SHA) | `c49db5a12e955f26c001165ad6e8f9d191bc26bfd96e24c1b163adc37016451a` |
| `data/v3_spine/rubric_hash_v2.txt` (txt content) | `c49db5a12e955f26c001165ad6e8f9d191bc26bfd96e24c1b163adc37016451a` |
| `verdict.json.rubric_hash_v2` | `c49db5a12e955f26c001165ad6e8f9d191bc26bfd96e24c1b163adc37016451a` |
| **chain_byte_equal** | **true** |

**`rubric_hash_v3` chain (c22 unified-driver spec)**:

| element | SHA-256 |
|---|---|
| `docs/v3_spine_unified_driver_spec.md` (doc SHA) | `bea618721ebb74b125b19b1743bfb42cb0e748a9c941ba5ce58117ba5c99a0d6` |
| `data/v3/recreate_v3/rubric_hash.txt` (txt content) | `bea618721ebb74b125b19b1743bfb42cb0e748a9c941ba5ce58117ba5c99a0d6` |
| `verdict.json.rubric_hash_v3` | `bea618721ebb74b125b19b1743bfb42cb0e748a9c941ba5ce58117ba5c99a0d6` |
| **chain_byte_equal** | **true** |

## §c 178-anchor preservation summary

Pre-snapshot from prior session, `anchor_preservation_pre.json`, contained 178 anchors covering c22 driver + env_pin module + c4 canonical serializer + c33 palette renderer + c5 CG delivery + c20 predecessor + focus_set_v2 + SF2 + both rubric chain docs + c5/c6/c7/c8/c9..c19 heartbeat cycle deliveries + rc7 anchors + baseline stems + locked scripts.

Post-snapshot at `anchor_preservation_post.json` picked up 180 anchors (2 new: fresh scratch files under `operator_section_c23_unified/` created by stage 1-3 execution this session).

**Preservation diff**:
- `n_pre = 178`
- `n_post = 180`
- `n_byte_equal = 178` (every pre-anchor byte-identical post)
- `n_byte_diff = 0`
- `n_missing = 0`
- `all_byte_equal = true`
- `diverged = []`

## §d `env_pin_sha256` — NOT PRESENT this cycle

`env_pin.json` is written by driver stage 9 `assemble_delivery()`; the driver terminated at stage 3/9. Consequently:

- `manifest.json.env_pins.env_pin_sha256`: ABSENT (manifest.json not produced)
- `env_pin.json.env_pin_sha256`: ABSENT (env_pin.json not produced)
- `first_delivery_carrying_env_pins_under_real_operator_directive`: **FALSE** for this cycle

The first-unified-driver-delivery-carrying-env_pins-with-self-anchor contract remains **unclaimed** for Peach Dream. Any future cycle that completes the driver end-to-end on Peach Dream will inherit the contract; alternatively, root conductor may pick a different focus song per escalation Option 3.

## §e 4/4 merged.mid structural gates

| gate | status |
|---|---|
| `drums_track_on_ch10_nonempty` | NOT_EVALUATED (stage 6 merge never ran) |
| `bass_median_pitch_lt_55` | NOT_EVALUATED (stage 6 merge never ran) |
| `vocals_track_present_symbolic` | NOT_EVALUATED (stage 6 merge never ran) |
| `zero_notes_on_gm_program_4` | NOT_EVALUATED (stage 6 merge never ran) |

No merged.mid on disk. `structural_assertions_all_pass_4_of_4 = false` by construction (no file to test).

## §f Byte-det ×2 per-stage

| stage | status | byte_det_x2 | evidence |
|---|---|---|---|
| 1/9 slice | complete | n/a (single write; verify-det evaluates rehtdemucs+) | `section.wav` sha `b278eae61718854b…` |
| 2/9 rehtdemucs | complete | **true** | `data/v3_spine/88d247468cb6d49f/operator_section_c23_unified/htdemucs_determinism.json`: `byte_determinism_holds=true, n_mismatch=0` |
| 3/9 muscriptor | **PARTIAL** — 3 of 7 probes completed json+mid; `other` probe half-complete | UNTESTED (verify-det would have re-run all probes into fresh tempdirs at end of stage 3) | probes on disk drums/bass/guitar json+mid + other.json only |
| 4/9 tempo_map | NOT_STARTED | — | — |
| 5/9 canonicalize | NOT_STARTED | — | — |
| 6/9 merge | NOT_STARTED | — | — |
| 7/9 render_per_track | NOT_STARTED | — | — |
| 8/9 mix_match | NOT_STARTED | — | — |
| 9/9 panel_measure | NOT_STARTED | — | — |

`byte_determinism_all_pass = false` (only rehtdemucs had a chance; muscriptor never re-run under verify-det). This is **not** an FD-1 halt on determinism failure; it is a wall-clock termination — the FD-1 halt block invoked in §j names the failure mode.

## §g Panel 8-key finite

| key | value |
|---|---|
| mel_l1_db | NOT_EVALUATED |
| spectral_centroid_rmse_hz | NOT_EVALUATED |
| rms_env_rmse | NOT_EVALUATED |
| lufs_m_rmse_lu | NOT_EVALUATED |
| embedding_cosine_distance | NOT_EVALUATED |
| sr_hz | NOT_EVALUATED |
| n_samples_compared | NOT_EVALUATED |
| n_keys | 0 |
| all_finite | false (no keys) |

Stage 9 panel_measure never ran. Panel is NEVER a LANDS gate per FD-6, but the LANDS_pending_operator contract required 8-key finite. Not met.

## §h c20 Option-3-terminal retirement note

`data/v3/deliveries/88d247468cb6d49f/cycle20/verdict.json` predecessor SHA `d9bc2f590e1af21455cc3e71932af60b8bcff3f8ddca409df9e8210eac6dc222` — verified byte-identical pre==post on disk.

**Retirement contract per operator directive point 5** required a successful LANDS delivery from the c22 unified driver to retire the c20 Option-3-terminal PARTIAL. This cycle delivered PARTIAL, not LANDS, so **c20 remains active as terminal PARTIAL** (unretired).

Root conductor escalation options for restoring the retirement path:
- **Option 1 (recommended)**: fresh dedicated cycle for Peach Dream with wall-time > 70 min. Driver idempotent; scratch stages 1-3 re-verify or advance.
- **Option 2**: accept c23 PARTIAL as terminal alongside c20 (both under Option-3-parallel semantics). M-V3-FOCUS-1 already satisfied at c21 on Chicken Grease + WIG + Disco A per operator — Peach Dream loss is redundancy only.
- **Option 3**: pick a different focus song (e.g. WIG, Disco A) for the first-unified-driver LANDS with `--reproduce-check` against operator-blessed c21 anchors.

## §i c22 driver + env_pin module SHAs — pre==post

| anchor | expected (from brief) | on-disk live | pre==post |
|---|---|---|---|
| `scripts/v3_spine/recreate_v3.py` | `72e80ee82cd21dbd…` | `72e80ee82cd21dbdc9422ca1ee9770c85e9f42d9085231a90d00d12bb5b2bfc8` | **true** |
| `scripts/v3_spine/v3_pipeline/env_pin.py` | `ab6d54638faeb161…` | `ab6d54638faeb161d75dcecdb5682280155304a5c5d8dea1966d25c204556654` | **true** |
| `scripts/v3_spine/midi_from_json_events.py` (c4) | `bbff015f4f1833f4…` | `bbff015f4f1833f446ad72f9cd5815117b2a744798fe3857edf468de6731a2ea` | **true** |
| `scripts/palette_render/render_stem.py` (c33) | `214372d920a319a9…5b2b` | `214372d920a319a97d6e3fc7b9ee4134c08c0cb4aecb776f4a50c75f965b5b2b` | **true** |

## §j FD-1 halt block — named stage & offending SHAs

**Fixed Decision 1 halt trigger**: wall-clock termination by session-boundary event, not a determinism failure. Named block per research brief REV 3 §5:

- **`failure_mode`**: `session_boundary_termination`
- **`named_block`**: `stage_3_of_9_muscriptor`
- **completed probes before termination**: drums (`json=59753283a665…, mid=3553650b23532309…`), bass (`json=47cf6e6f1e97f709…, mid=d5aaf1dbab9875df…`), guitar (`json=4f53cda18c2baa0c…` canonical empty, `mid=b4134d5cce88b904…`)
- **partial probe at termination**: `other` (`json=bd37145f8dbc5187…` written; `mid` never emitted)
- **unstarted probes**: piano, vocals, full_mix

**Session-boundary chain**:

| attempt | task_id | terminated at |
|---|---|---|
| 1 (prior session) | `bs6ut63f9` / `bwy7tikts` | stage 3/9 muscriptor after drums+bass+guitar completions |
| 2 (this session) | `b717jm3iw` (driver) + `b3t1ugvpt` / `b44o1cn1e` (monitors) | stage 3/9 muscriptor; harness `orphan_summary` on session teardown |
| 3 | **NOT LAUNCHED** per research brief REV 3 §5: "If driver dies again mid-flight for a second time, emit honest PARTIAL per §5 with `failure_mode: session_boundary_termination` rather than restart a third time (per auditor watch item)." |

FD-1 compliance is preserved: no tuning, no retry, no fallback on determinism. The one bounded retry (this session's re-launch after prior session's termination) was permitted by the standard resume contract; the second in-session termination triggered the auditor's honest-PARTIAL rule instead of a third restart.

## §7-required ledger events (4 rows landed)

Per c9 canonical-assessor pattern (`agent="worker"` + `agent_original="worker-clone-1"`); infra families suffixed `-clone-1` per c32 convention; substantive `M-V3-FOCUS-1/*` unsuffixed.

| # | milestone_id | ts | status |
|---|---|---|---|
| 1 | `M-INGEST-1/egress-probe-cycle23-clone-1` | 2026-09-03T00:22:45Z | validated/high |
| 2 | `M-V3-FOCUS-1/peach-dream-first-unified-driver-delivery` | 2026-09-03T00:22:47Z | validated/high (narrative reflects PARTIAL) |
| 3 | `_infra/adopt-cycle23-tests-clone-1` | 2026-09-03T00:22:48Z | validated/high |
| 4 | `_archive/cycle-23-scratch-clone-1` | 2026-09-03T00:22:49Z | validated/high |

Emitted via `scripts/v3_spine/peach_dream_c23_clone1_ledger.py` with strict ts+1s ordering.

## Anti-patterns preserved

- **No** hand-composing songs, no hand-orchestrating per-song scripts, no VST3 state-extraction APIs, no CLAP fetch, no M-EAR-1 Path A audits, no PRNG in pipeline scripts, no `sidecar_nonfactor` imports, no TLS-verify disable, no `HTTPS_PROXY` unset, no `--reproduce-check` on CG or Rome (Branch A scope), no `M-V3-RULES-1/*` events (Branch C scope).
- **`scripts/palette_render/render_stem.py` SHA `214372d920a319a97d6e3fc7b9ee4134c08c0cb4aecb776f4a50c75f965b5b2b` byte-identical pre==post** (do-not-touch invariant honored).
- **c22 driver + env_pin module + c4 canonical serializer** — all SHAs byte-identical pre==post.
- **c5 CG operator-blessed WAV** sha `cc919559b4508b6b…` byte-identical pre==post (not touched).
- **c20 Peach Dream PARTIAL predecessor** sha `d9bc2f590e1af214…` byte-identical pre==post (cycle23/ sibling to cycle20/, does not overwrite).

## Handoff to root conductor / c24

- **c23 PARTIAL is terminal in-session**. No further driver launches this session.
- **Merge report** at `data/v3/deliveries/88d247468cb6d49f/cycle23/merge_report.md` (sandbox fallback — root conductor should `cp` to `/home/user/music-gen-instance-v3/fork-d5530f8d1ccc/clone-1/merge_report.md` during post-merge integration, per c20/c21 clone-2 precedent).
- **Verdict.json** carries a 3-option escalation block with Option 1 (fresh cycle with >70 min wall budget) recommended.
- **M-V3-FOCUS-1** parent gate remains satisfied per c21 (Chicken Grease + WIG + Disco A operator-ear accepts); Peach Dream is a 4th redundant candidate. Non-blocking.
- **`_infra/retire-oneoff-drivers-c22`** catalog stays queued — retirement remains contingent on any focus song's first successful LANDS via the unified driver.
- **Auditor pattern (research brief REV 3 §5 addition)** re-verified in production: after 2 consecutive mid-flight session terminations, honest PARTIAL under `session_boundary_termination` label is the correct move and does not violate FD-1.
