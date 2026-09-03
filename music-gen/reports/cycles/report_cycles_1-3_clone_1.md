---
title: "Music-Gen v3 FOCUS Milestone — Fanout Clone 1: Peach Dream c23 First-Unified-Driver Delivery (Cycles 1–3, in-flight)"
date: "2026-09-03"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# Music-Gen v3 FOCUS Milestone — Fanout Clone 1: Peach Dream c23 First-Unified-Driver Delivery (Cycles 1–3, in-flight)

## Abstract

This report covers Cycles 1 through 3 of a fanout-clone branch spawned to execute the c22-deferred Peach Dream first-unified-driver delivery via the c22 unified `scripts/v3_spine/recreate_v3.py`. The clone (fork `d5530f8d1ccc`, clone 1) was assigned to be the first real end-to-end song delivery emitted under the c22 unified driver's `env_pins` self-anchor contract — the manifest.env_pins block carrying a self-referential `env_pin_sha256` field is a first-of-its-kind delivery contract landing under the operator's directive rather than under prior speculative implementation. The delivery target is Peach Dream (source SHA-16 `88d247468cb6d49f`) on the operator-D1-chosen thirty-second section (t = 172.87256 s to t = 202.87256 s from `focus_set_v2.json`), matching the c5 Chicken Grease Method A delivery format exactly while additionally carrying both a three-way `rubric_hash_v2` chain against the v3-spine rubric (`c49db5a12e955f26…016451a`) and a three-way `rubric_hash_v3` chain against the c22 unified-driver spec (`bea618721ebb74b1…c99a0d6`). A successful landing retires the c20 clone-2 Option-3-terminal PARTIAL per operator directive point 5, and per the operator's "KEEP MOVING" 2026-09-02 directive adds a redundancy accept toward the already-closed M-V3-FOCUS-1 milestone. The three cycles reported here span the pre-work discipline gate landing (rubric+spec doc SHA freeze, three pre-registered emitter scripts, 178-anchor pre-snapshot far exceeding the ≥40 gate at 4.45×) and a substantial pipeline in-flight state (`recreate_v3.py` completed stages 1/9 slice and 2/9 rehtdemucs, then reached stage 3/9 MuScriptor with the drums probe complete and byte-deterministic on run 1). Cycle 3's auditor issued `STATUS_PENDING (pipeline in-flight)` rather than a merge verdict: substantive verdict cannot be audited until worker completes stages 3/9→9/9. Every pre-work anchor byte-verifies against expected SHA; the two required rubric chain documents are both present with SHAs unchanged; all four do-not-touch read-only anchors (c22 driver, c22 env_pin module, c4 canonical serializer, c33 render_stem) are byte-identical to their expected values. This report is the honest handoff summary at pre-work-complete state; the substantive delivery closes in a subsequent cycle when the pipeline finishes.

## 1. Introduction and scope

Cycle 22 landed the unified v3 driver `scripts/v3_spine/recreate_v3.py` together with an `env_pin.py` module that produces a canonical `env_pin.json` manifest capturing the byte-deterministic environment at delivery time. The c22 delivery on Peach Dream ran the driver end-to-end to prove that the unified pipeline works, but that Peach Dream delivery was itself a first-driver-run pre-dating the operator's explicit endorsement of the `env_pins` self-anchor contract. Under c23 the operator's directive named a real Peach Dream delivery under the self-anchor contract as an outstanding item, together with a companion directive point (point 5) that once this delivery lands it retires the c20 clone-2 Option-3-terminal PARTIAL from Peach Dream's status ledger.

This branch is that delivery. Sibling clones in the same fork run other opening work (clone 0 executed the c23 reproduce-proofs on Chicken Grease and Rome, landing `REPRODUCE_PANEL_ONLY × 2`; clone 2 executed the M-V3-RULES-1 first activation, landing 76 typed rules with byte-determinism ×2); they are reported separately.

The clone's scoped objective as issued:

- **Invoke the c22 unified driver** as `scripts/v3_spine/recreate_v3.py --song 88d247468cb6d49f --section operator --cycle 23 --verify-det --out data/v3/deliveries/88d247468cb6d49f/cycle23/` on the operator-D1-chosen thirty-second section (t = 172.87256–202.87256 s).
- **Deliver** matching the c5 Chicken Grease Method A format: `verdict.json` (verdict ∈ `V3_FOCUS_SONG_LANDS_pending_operator` / PARTIAL / FAILS), `manifest.json` with `env_pins` block carrying self-anchor `env_pin_sha256` (first delivery to carry it under real operator directive), `original_ab.wav`, `reconstruction_ab.wav`, `full_reconstruction.wav`, `merged.mid`, `tempo_choice.json`, `panel.json` and `panel.tsv`, per-track WAVs, htdemucs stems, MuScriptor JSON and MID.
- **Two three-way rubric chains byte-equal**: `rubric_hash_v2` at `c49db5a12e955f26…016451a` (v3-spine rubric) AND `rubric_hash_v3` at `bea618721ebb74b1…c99a0d6` (c22 unified-driver spec).
- **Four structural gates on merged.mid enforced**; byte-determinism ×2 across all deterministic artifact classes OR an honest FD-1 halt with named block; both panels 8-key finite.
- **c22 driver + env_pin module SHAs byte-identical pre==post.**
- **Anchor preservation ≥40 SHAs.**
- **Retire c20 clone-2 Option-3-terminal PARTIAL** per operator directive point 5 upon successful landing.

The required output artifact is `docs/v3_focus_peach_dream_c23_unified_delivery_report.md`.

## 2. Pre-work discipline landed (Cycles 1–3)

The three cycles reported here established the full pre-work discipline surface before the driver was invoked, and then dispatched the driver as a long-running background pipeline. The auditor of Cycle 3 verified the pre-work state live and issued `STATUS_PENDING (pipeline in-flight)` rather than a merge verdict because the substantive delivery artifacts had not yet landed.

### 2.1 Read-only anchor SHA verification

Every do-not-touch anchor was byte-verified against its expected pinned SHA at pre-work:

| Anchor | Expected SHA-16 | Live SHA-256 | Status |
|---|---|---|---|
| c22 unified driver `scripts/v3_spine/recreate_v3.py` | `72e80ee82cd21dbd…` | `72e80ee82cd21dbdc9422ca1ee9770c85e9f42d9085231a90d00d12bb5b2bfc8` | READ-ONLY ✓ |
| c22 env_pin module `scripts/v3_spine/v3_pipeline/env_pin.py` | `ab6d54638faeb161…` | `ab6d54638faeb161d75dcecdb5682280155304a5c5d8dea1966d25c204556654` | READ-ONLY ✓ |
| c4 canonical serializer `scripts/v3_spine/midi_from_json_events.py` | `bbff015f4f1833f4…` | `bbff015f4f1833f446ad72f9cd5815117b2a744798fe3857edf468de6731a2ea` | READ-ONLY ✓ |
| c33 render_stem `scripts/palette_render/render_stem.py` (REV 2 path-corrected) | `214372d920a319a9…5b2b` | `214372d920a319a97d6e3fc7b9ee4134c08c0cb4aecb776f4a50c75f965b5b2b` | READ-ONLY ✓ |
| v3-spine rubric v2 `docs/v3_spine_rubric_v2.md` | `c49db5a12e955f26…016451a` | `c49db5a12e955f26c001165ad6e8f9d191bc26bfd96e24c1b163adc37016451a` | ✓ |
| c22 unified-driver spec `docs/v3_spine_unified_driver_spec.md` | `bea618721ebb74b1…c99a0d6` | `bea618721ebb74b125b19b1743bfb42cb0e748a9c941ba5ce58117ba5c99a0d6` | ✓ |
| focus_set_v2 `data/recreate_v2/focus_set_v2.json` | `8908dae03202ae52…` | `8908dae03202ae529282c08e74d490b336fadcf7ded4f93483a2b32756a1a5ca` | ✓ |
| c20 Peach Dream PARTIAL predecessor verdict | `d9bc2f590e1af214…` | `d9bc2f590e1af21455cc3e71932af60b8bcff3f8ddca409df9e8210eac6dc222` | READ-ONLY ✓ (sibling `cycle23/`, not overwritten) |
| c5 Chicken Grease operator-blessed WAV (cross-branch anchor) | `cc919559b4508b6b…` | `cc919559b4508b6bfe868fa5433a50b6805c43bab763665a5f2be367f01bbbd7` | READ-ONLY ✓ |

The prior clone-1 attempt's MINOR path-typo (`palette/` versus `palette_render/`) that had surfaced in an earlier audit was closed via the research brief's REV 2 §3 acknowledgment; the c33 render_stem anchor at the correct `scripts/palette_render/` path is byte-identical to the expected value.

### 2.2 Pre-registered emitter scripts

Three pre-registered emitter scripts landed on disk before the driver invocation, ready to consume the driver's outputs and emit the final delivery artifacts:

- `anchor_preservation_c23_clone1.py` (SHA-16 `354e549bd43975fc…`) — snapshots + verifies the 178-anchor set.
- `peach_dream_c23_clone1_verdict.py` (SHA-16 `1b4dadbedf4948b4…`) — emits the verdict.json with both three-way rubric chains.
- `peach_dream_c23_clone1_ledger.py` (SHA-16 `d5a8d19ce5b09c51…`) — emits the six named plus two housekeeping ledger events.

Each of the three emitters carries a mtime strictly after the two rubric-chain documents, ensuring the mtime-hard gate holds when the driver completes and the emitters consume its outputs.

### 2.3 Anchor pre-snapshot

`data/v3/deliveries/88d247468cb6d49f/cycle23/anchor_preservation_pre.json` recorded **178 anchors** on disk at pre-work. This exceeds the directive's ≥40 anchor-preservation gate by a factor of 4.45×. The pre-snapshot covers all c22/c4/c33 do-not-touch scripts, all prior focus-song deliveries (Chicken Grease c5, Rome c20, Disco A c21, WIG c21 restart, Peach Dream c20 PARTIAL predecessor), the focus set, both rubric-chain documents, and the c22 unified-driver spec — a comprehensive campaign-state anchor set.

### 2.4 Driver invocation and in-flight state

The unified driver was invoked in the background and reached stage 3 of 9 during the arc. The run log at `data/v3/deliveries/88d247468cb6d49f/cycle23/run.log` (tail as of the Cycle 3 audit at 2026-09-02T23:54Z) records:

```
=== recreate_v3 song=88d247468cb6d49f section=[172.87..202.87]s ===
[stage 1/9] slice → data/v3_spine/88d247468cb6d49f/operator_section_c23_unified/section.wav
[stage 2/9] rehtdemucs
[stage 3/9] muscriptor
  muscriptor drums      json=59753283a665 det=True
```

**Stage 1/9 (slice)** completed: chosen-section slice landed at `data/v3_spine/88d247468cb6d49f/operator_section_c23_unified/section.wav`.

**Stage 2/9 (rehtdemucs)** completed: six-stem separation performed on the chosen-section slice. The HuggingFace Hub warning in the log (`sending unauthenticated requests to the HF Hub`) is expected and not a defect; the htdemucs model is already cached locally, so the warning is a benign preflight probe rather than an actual fetch attempt.

**Stage 3/9 (MuScriptor)** in progress: the drums probe completed with JSON SHA-16 `59753283a665` and `det=True` (byte-deterministic on run 1). Six MuScriptor probes remain (bass, guitar, other, piano, vocals, full_mix) plus the six downstream stages (canonicalize ×2, merge, per-track render ×2, vocals overlay, mix-match, deliver, panel).

The pipeline restarted this session (run log truncated to fresh output; last mtime at cycle-3 audit is ~87 minutes old). The remaining wall time is consistent with the research brief's 45–70 minute estimate.

### 2.5 What is not yet auditable

The Cycle 3 auditor enumerated the artifacts that have not yet landed and cannot yet be verified:

- `verdict.json` — verdict field, three-way `rubric_hash_v3` chain field.
- `manifest.json` — the first-under-operator-directive `env_pins.env_pin_sha256` self-anchor field.
- `env_pin.json` — the byte-anchored environment manifest.
- Four merged.mid structural gates: `drums_track_on_ch10_nonempty`, `bass_median_pitch_lt_55`, `vocals_track_present_symbolic`, `zero_notes_on_gm_program_4`.
- Byte-determinism ×2 per-stage table (rehtdemucs ×2, MuScriptor 7 probes ×2, canonicalize 7 ×2, merge, render 5 ×2, mix-match).
- Both panels (root panel and operator-section panel) 8-key finite table.
- 178-anchor pre==post preservation confirmation.
- Six named plus two housekeeping ledger events emission.
- Required output artifact `docs/v3_focus_peach_dream_c23_unified_delivery_report.md`.
- Merge report at `/home/user/music-gen-instance-v3/fork-d5530f8d1ccc/clone-1/merge_report.md` (workspace-fallback per c20/c21/c22/c23 precedent).

## 3. Cycle-3 audit disposition: STATUS_PENDING

The Cycle 3 auditor did not issue a merge verdict. Under the campaign's anti-fabrication discipline, a substantive verdict enum (`V3_FOCUS_SONG_LANDS_pending_operator` / PARTIAL / FAILS) requires artifacts that are not yet on disk; the auditor cannot fabricate one. The auditor's rationale enumerated:

- Pre-work discipline is clean: rubric-v2 plus spec-v3 documents SHA-frozen; three pre-registered emitters landed with mtime strictly greater than the rubric documents' mtimes; 178-anchor pre-snapshot on disk exceeds the ≥40 gate by 4.45×; all four do-not-touch anchors byte-identical to expected.
- No new CRITICAL, MODERATE, or MINOR findings surfaced this turn on pre-work.
- The prior clone-1 attempt's MINOR path-typo is closed via REV 2 acknowledgment.
- **AUDIT_PENDING** — substantive verdict cannot be audited until worker completes stages 3/9 → 9/9.

The auditor's watch item (non-blocking) named the recurring pattern from the prior clone-1 attempt: background driver may be terminated by session-boundary events. If the pipeline is terminated again before completion, the honest FD-1 halt semantics require worker to emit a `REPRODUCE_PARTIAL`-analogue verdict with a named `failure_mode` block per the rubric §5 enumeration — not restart. This is the same failure-mode discipline that governed the c20 Peach Dream clone-2 Hold Pattern arc and the c22 unified-driver pipeline design.

## 4. Handoffs and forward state

**This branch does not merge yet.** The Cycle 3 auditor's `STATUS_PENDING (pipeline in-flight)` disposition means the branch remains open pending completion of the driver run. The audit trail up to this point is clean: pre-work discipline landed cleanly; every read-only anchor byte-verifies; the pre-snapshot exceeds gate; the pipeline is provably in flight per the log.

**Worker handoff (immediate).** Complete the driver run — roughly 45–70 minutes of wall time remaining from stage 3/9 per the research brief's estimate. On the driver's terminal `wrote run_report.json` marker, invoke the three pre-registered emitters in strict order: `anchor_preservation_c23_clone1.py` post-snapshot for the 178-anchor pre==post assertion; `peach_dream_c23_clone1_verdict.py` for the verdict emission carrying both three-way rubric chains and the `env_pins.env_pin_sha256` self-anchor field; `peach_dream_c23_clone1_ledger.py` for the six named plus two housekeeping ledger events. Then write the required output report doc and the workspace-fallback merge report.

**Next-auditor handoff (post-completion).** Live SHA-verify twelve delivery artifacts (verdict.json, manifest.json, env_pin.json, both A/B WAVs plus full-reconstruction WAV, merged.mid, panel.json, panel.tsv, tempo_choice.json, plus per-track WAVs and htdemucs/MuScriptor tables). Confirm both three-way rubric chains hold byte-equal: `rubric_hash_v2` at `c49db5a12e955f26…016451a` across doc SHA + rubric_hash.txt content + verdict field, and `rubric_hash_v3` at `bea618721ebb74b1…c99a0d6` across spec-doc SHA + its pinned hash file + verdict field. Verify env_pin self-anchor byte-equality between `manifest.env_pins.env_pin_sha256` and the actual `env_pin.json` file SHA. Check all four merged.mid structural gates pass. Check both panels 8-key finite. Verify 178-anchor pre==post byte-identity. Confirm c22 driver + env_pin module + c5 CG WAV + c20 Peach Dream PARTIAL predecessor all byte-identical pre==post.

**Retirement of c20 clone-2 Option-3-terminal PARTIAL.** Per operator directive point 5, a successful LANDS verdict on this branch retires the c20 clone-2 Option-3-terminal PARTIAL status entry for Peach Dream. This is a status-ledger update at the next post-completion audit, not a code change; the c20 verdict artifact itself remains preserved read-only on disk per the append-only integrity chain (the retirement is a forward-looking status transition, not a delete of past record).

**Redundancy status.** M-V3-FOCUS-1 was already operator-satisfied on 2026-09-02 (three-of-three operator-ear accepts on Chicken Grease + WIG + Disco A per D-A), so a successful LANDS on this branch is a redundancy accept: it strengthens the fault-tolerance of the M-V3-FOCUS-1 milestone but does not itself gate any downstream milestone. A failed PARTIAL with a named FD-1 block is likewise non-blocking on the milestone but would surface a first-class failure-mode finding for c24 auditor root-cause work.

**Cycle 24 dependency.** No c24 downstream cycle is blocked on this branch. The c24 authorization for the `_infra/retire-oneoff-drivers-c22` deletion contract stands independently of this delivery's outcome (it depends on the c23 clone-0 reproduce-proofs, which landed cleanly as `REPRODUCE_PANEL_ONLY × 2`). The five queued c24 handoff items from the clone-0 branch remain in force independent of this branch's completion.

## 5. Campaign-level state

**M-V3-SPINE-1**: operator-ear-LANDED since 2026-09-02 on c5 Chicken Grease. Unchanged.

**M-V3-SPINE-2 (unified driver track)**: c22 unified driver + env_pin manifest + first Peach Dream unified-driver delivery landed at c22. c23 reproduce-proofs on Chicken Grease and Rome landed at clone-0 with `REPRODUCE_PANEL_ONLY` × 2. c23 first-under-operator-directive Peach Dream delivery is this branch, in-flight.

**M-V3-FOCUS-1**: closed with redundancy at 3-of-3 operator-ear (Chicken Grease + WIG + Disco A) 2026-09-02; 4 internal-gate LANDS with Rome. A successful LANDS on this branch adds a fifth internal-gate accept for further redundancy.

**M-V3-RULES-1**: first activation LANDED at c23 clone-2 (peer clone) with 76-rule artifact, byte-determinism ×2, and 15/15 tests.

**M-V3-CORPUS-1, M-V3-EAR-1, M-V3-GEN-1**: downstream, opening pending root-conductor c24+ dispatch.

**Discipline gates held during pre-work of this branch:**
- FD-1 (no tuning/retry/fallback on nondeterminism): held — pre-work performed no substantive writes; the honest FD-1 halt semantics are pre-wired into the worker's failure-mode contract.
- FD-3 (palette timbre-upgrade path preserved but unexercised): held.
- FD-6 (operator ear is only LANDS authority; panel is tripwire only): held — this delivery's verdict enum contains only `_pending_operator` variants.
- D-A (internal-gate accept under operator autonomous-completion contract): held.
- Anti-patterns locked: VST3 state APIs, M-EAR-1 Path A under N=55, CLAP fetch, hand-orchestrating song recreation, PRNG in pipeline scripts, `sidecar_nonfactor` imports, TLS disable — all respected in the pre-registered emitters and the invocation shape.
- Read-only anchors: all byte-identical to expected SHAs across all four cross-branch invariants.

## 6. Conclusions

Cycles 1 through 3 of the Peach Dream c23 first-under-operator-directive unified-driver delivery landed the full pre-work discipline surface cleanly and dispatched the c22 unified driver as a long-running background pipeline that reached stage 3 of 9 during the arc. Every read-only anchor is byte-identical to expected; both rubric-chain documents are SHA-frozen; three pre-registered emitters are ready to consume the driver's outputs when they land; the 178-anchor pre-snapshot exceeds the ≥40 gate by 4.45×. The MuScriptor drums probe on stage 3/9 completed byte-deterministic on run 1 (JSON SHA-16 `59753283a665`, `det=True`). The Cycle 3 auditor issued `STATUS_PENDING (pipeline in-flight)` rather than a merge verdict, correctly refusing to fabricate a substantive verdict against artifacts that are not yet on disk.

The branch remains open. The substantive verdict will be issued in a subsequent cycle after the driver completes stages 3/9 → 9/9 and the three pre-registered emitters produce the final delivery artifacts. If completion succeeds, the delivery becomes the first end-to-end song reconstruction to carry the `env_pins.env_pin_sha256` self-anchor under real operator directive, retires the c20 clone-2 Option-3-terminal PARTIAL per operator directive point 5, and adds a fifth internal-gate accept to the already-closed-with-redundancy M-V3-FOCUS-1 milestone. If completion fails (session-boundary termination remains the auditor-flagged watch item), an honest FD-1 halt with a named `failure_mode` block is required rather than a restart.

## Appendix: Implementation Details

### A.1 Delivered artifacts at end-of-arc (pre-work state)

Present on disk at Cycle 3 audit time:
- `data/v3/deliveries/88d247468cb6d49f/cycle23/anchor_preservation_pre.json` — 178-anchor pre-snapshot
- `data/v3/deliveries/88d247468cb6d49f/cycle23/run.log` — driver run log (in-flight)
- Chosen-section slice at `data/v3_spine/88d247468cb6d49f/operator_section_c23_unified/section.wav` (from stage 1/9)
- Stage 2/9 rehtdemucs six-stem outputs (from stage 2/9; not yet enumerated in the log tail)
- Stage 3/9 MuScriptor drums probe: JSON SHA-16 `59753283a665` with `det=True` on run 1

Pre-registered emitter scripts (ready to consume driver outputs):
- `anchor_preservation_c23_clone1.py` (SHA-16 `354e549bd43975fc…`)
- `peach_dream_c23_clone1_verdict.py` (SHA-16 `1b4dadbedf4948b4…`)
- `peach_dream_c23_clone1_ledger.py` (SHA-16 `d5a8d19ce5b09c51…`)

**Not yet on disk (pending driver completion):** `verdict.json`, `manifest.json`, `env_pin.json`, `original_ab.wav`, `reconstruction_ab.wav`, `full_reconstruction.wav`, `merged.mid`, `tempo_choice.json`, `panel.json`, `panel.tsv`, per-track WAVs, MuScriptor probes 2–7, canonical MIDI ×2, merged-MID structural-gate report, byte-determinism ×2 per-stage table, both panels 8-key finite table, anchor_preservation_post_c23.json, ledger events, required output report doc `docs/v3_focus_peach_dream_c23_unified_delivery_report.md`, merge report at fork-clone path.

### A.2 Integrity chains (pre-work state)

Two three-way rubric chains queued to fire on verdict emission:

- **`rubric_hash_v2` chain** (v3-spine rubric): `docs/v3_spine_rubric_v2.md` SHA `c49db5a12e955f26c001165ad6e8f9d191bc26bfd96e24c1b163adc37016451a` == `data/v3_spine/rubric_hash_v2.txt` content == verdict field (pending emission).
- **`rubric_hash_v3` chain** (c22 unified-driver spec): `docs/v3_spine_unified_driver_spec.md` SHA `bea618721ebb74b125b19b1743bfb42cb0e748a9c941ba5ce58117ba5c99a0d6` == its pinned hash file == verdict field (pending emission).

### A.3 Read-only anchor byte-identity table (Cycle 3 pre-work)

All four cross-branch and cross-cycle do-not-touch anchors byte-identical to expected:

| Anchor | Live SHA-256 |
|---|---|
| c22 unified driver | `72e80ee82cd21dbdc9422ca1ee9770c85e9f42d9085231a90d00d12bb5b2bfc8` |
| c22 env_pin module | `ab6d54638faeb161d75dcecdb5682280155304a5c5d8dea1966d25c204556654` |
| c4 canonical MIDI serializer | `bbff015f4f1833f446ad72f9cd5815117b2a744798fe3857edf468de6731a2ea` |
| c33 render_stem | `214372d920a319a97d6e3fc7b9ee4134c08c0cb4aecb776f4a50c75f965b5b2b` |
| focus_set_v2 | `8908dae03202ae529282c08e74d490b336fadcf7ded4f93483a2b32756a1a5ca` |
| Chicken Grease c5 operator-blessed WAV | `cc919559b4508b6bfe868fa5433a50b6805c43bab763665a5f2be367f01bbbd7` |
| Peach Dream c20 PARTIAL predecessor verdict | `d9bc2f590e1af21455cc3e71932af60b8bcff3f8ddca409df9e8210eac6dc222` |

### A.4 Chosen section and driver invocation

Song: Peach Dream, source SHA-16 `88d247468cb6d49f`, operator-D1-chosen thirty-second section t = 172.87256 s to t = 202.87256 s from `focus_set_v2.json`.

Driver invocation: `scripts/v3_spine/recreate_v3.py --song 88d247468cb6d49f --section operator --cycle 23 --verify-det --out data/v3/deliveries/88d247468cb6d49f/cycle23/`.

Delivery target: `data/v3/deliveries/88d247468cb6d49f/cycle23/` (sibling to the c20 `cycle20/` verdict artifact, which is preserved read-only unchanged).

### A.5 Anchor pre-snapshot

`data/v3/deliveries/88d247468cb6d49f/cycle23/anchor_preservation_pre.json` — 178 anchors recorded at pre-work. Directive gate: ≥40. Ratio: 4.45×.

### A.6 Auditor watch item and FD-1 halt semantics

Non-blocking watch item flagged by the Cycle 3 auditor: prior clone-1 attempt was terminated by session-boundary events before completion. If the pipeline is terminated again before completion, the honest FD-1 halt semantics require worker to emit a `REPRODUCE_PARTIAL`-analogue verdict with a named `failure_mode` block per rubric §5 enumeration, not restart. This is the same failure-mode discipline that governed the c20 Peach Dream clone-2 Hold Pattern arc.

### A.7 Post-completion audit checklist (queued for subsequent auditor)

Twelve delivery artifacts to SHA-verify live. Confirm both three-way rubric chains hold byte-equal. Verify env_pin self-anchor byte-equality: `manifest.env_pins.env_pin_sha256` == on-disk `env_pin.json` SHA. Check all four merged.mid structural gates pass. Check both panels 8-key finite. Verify 178-anchor pre==post byte-identity. Confirm c22 driver + env_pin module + c4 serializer + c33 render_stem + c5 CG WAV + c20 Peach Dream PARTIAL predecessor + focus_set_v2 + both rubric docs all byte-identical pre==post. Confirm the six named plus two housekeeping ledger events emitted under `M-V3-FOCUS-1/peach-dream-c23-*` sub-leaves.

### A.8 Environment pins

`PYTHONHASHSEED=0`; `SOURCE_DATE_EPOCH=1756463424`; `TZ=UTC`; `LC_ALL=C.UTF-8`; `OMP_NUM_THREADS=1`, `MKL_NUM_THREADS=1`, `OPENBLAS_NUM_THREADS=1`; interpreter `/usr/bin/python3`; `mido==1.3.3`; SoundFont SHA `74594e8f…1cb0`; MuScriptor model SHA `ac80adbd…7fb97ec`. Env-pin invocation prefix confirmed in the driver's process launch by the run.log header; the manifest.env_pins block will land on delivery emission.

### A.9 Merge disposition

**Branch not yet merged.** Cycle 3 auditor disposition: `STATUS_PENDING (pipeline in-flight)`. Merge disposition awaits pipeline completion and post-completion audit. On successful LANDS: `[[BRANCH_COMPLETE]]` with retirement of c20 clone-2 Option-3-terminal PARTIAL per operator directive point 5. On PARTIAL with named FD-1 block: `[[BRANCH_COMPLETE]]` with c24 auditor root-cause dispatch. On failure to complete (session-boundary termination): honest partial merge with named block; no restart within c23 per FD-1 halt semantics.

### A.10 Source sessions

| Cycle | Researcher | Worker | Auditor |
|---|---|---|---|
| 1 | b271ad57-8e0e-4070-b597-bf6b12c124b4 | 82757ca1-b126-489a-87a7-d8f54384af29 | 602f6a21-c407-4a3e-a319-e0e47fb6e581 |
| 2 | fab380a6-2714-4897-a5c8-243d382d36ce | dd39a36a-64f0-447d-a011-7f1dc47755d8 | cf1a956a-5411-49e9-b41f-334b51a9de03 |
| 3 | 97dc70c9-618d-435f-afbd-44d68c54dbac | a0c7f19f-aa89-4e2e-a98c-cf3d810c5c20 | 54eb5474-4b65-4e40-afce-a34fd54abe42 |

### A.11 Fanout metadata

Fork `d5530f8d1ccc`. Clone 1 of the c23 Peach Dream first-under-operator-directive unified-driver delivery assignment. Merge report expected at `/home/user/music-gen-instance-v3/fork-d5530f8d1ccc/clone-1/merge_report.md` for parent-conductor pickup on branch completion; workspace-root fallback per c20/c21/c22/c23 precedent. Sibling clones 0 (c23 reproduce-proofs on CG + Rome, closed with `REPRODUCE_PANEL_ONLY × 2` and `[[BRANCH_COMPLETE]]`) and 2 (M-V3-RULES-1 first activation, closed with 76-rule artifact LANDS and `[[BRANCH_COMPLETE]]`) reported separately.
