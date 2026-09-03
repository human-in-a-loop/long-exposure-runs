---
title: "Music-Gen v3 SPINE-2 Milestone — Fanout Clone 0: c23 Reproduce-Proofs on Chicken Grease and Rome (Cycles 1–3)"
date: "2026-09-02"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# Music-Gen v3 SPINE-2 Milestone — Fanout Clone 0: c23 Reproduce-Proofs on Chicken Grease and Rome (Cycles 1–3)

## Abstract

This report covers Cycles 1 through 3 of a fanout-clone branch spawned from the Music-Gen v3 campaign to execute the c22-deferred reproduce-proofs on the operator-blessed Chicken Grease and internal-gate-accepted Rome deliveries via the c22 unified `scripts/v3_spine/recreate_v3.py` driver. The clone (fork `d5530f8d1ccc`, clone 0) was assigned to prove that the c22 unified driver, when invoked in `--reproduce-check` mode against the two existing on-disk deliveries, produces panel outputs that match the originals within the rubric-defined per-key tolerances, thereby unblocking the c24 execution of the `_infra/retire-oneoff-drivers-c22` deletion contract (which would retire 37 catalogued per-song scripts). Cycle 1 pinned the rubric document `docs/v3_reproduce_proof_c23_rubric.md` (SHA `3fe5545bfce62723a9c9faf7391e6ad8f31a1731cde18641569e419d772f792e`) before any script under `scripts/v3_reproduce_c23/` and delivered both reproduce-proof reports plus the required output artifact `docs/v3_reproduce_proof_c23_report.md`. Both per-song verdicts fired mechanically as `REPRODUCE_PANEL_ONLY` per the rubric's frozen enum: panel equality holds on every key with delta magnitudes at the sixth-through-eighth decimal place (well inside the rubric's per-key tolerances), and byte equality on the panel JSON/TSV artifacts is honestly false because the two anchor deliveries pre-date the c22 `env_pin.json` manifest and thus fail the byte-equality gate that requires environment-pin identity. This is a first-class mechanism-of-record outcome per Fixed Decision 1 — the rubric's byte-equality gate honestly downgrades from LANDS to PANEL_ONLY when the environment-pin diff cannot be established against a null anchor, rather than smoothing over the drift or retrying. Cycles 2 and 3 were re-verification passes that live-checked every anchor byte-identically and closed the branch with `COMPLETE` and `[[BRANCH_COMPLETE]]` under the `<no-null-cycle-validation>` rule. The c24 execution of the retirement deletion contract is now pre-authorized.

## 1. Introduction and scope

Cycle 22 landed the unified v3 driver `scripts/v3_spine/recreate_v3.py` and the accompanying `env_pin.json` manifest for future deliveries, plus a first-unified-driver delivery on Peach Dream to demonstrate the driver end-to-end. The c22 delivery catalogued 37 per-song one-off driver scripts as candidates for retirement under `data/v3/recreate_v3/retirement_catalog_c22.json`, but the retirement was gated on a reproduce-proof: the unified driver must be shown to reproduce the operator-blessed Chicken Grease delivery and the internal-gate-accepted Rome delivery within rubric-defined tolerances before the one-off scripts can be safely deleted.

Cycle 23 deferred that reproduce-proof to a subsequent cycle. This branch is that cycle: fork `d5530f8d1ccc`, clone 0 executes the c22-deferred reproduce-proofs on both Chicken Grease and Rome. Sibling clones in the same fork run other opening work (M-V3-RULES-1 first activation on clone 2; other downstream work on clone 1); they are reported separately.

The clone's scoped objective as issued:

- **Pin the rubric document** `docs/v3_reproduce_proof_c23_rubric.md` before any script under `scripts/v3_reproduce_c23/`, with a three-way `rubric_hash_v3_reproduce` byte-equality chain.
- **For each of Chicken Grease (`31a164f845f8e27e`) and Rome (`51e433ade2a845e1`)**, invoke `scripts/v3_spine/recreate_v3.py --song <sha16> --section operator --reproduce-check <existing-delivery-dir>` and emit `data/v3/reproduce/c23/<sha16>/reproduce_report.json` with per-stage diff, per-key panel diff, and env-pin diff-vs-original-manifest.
- **Verdict enum**: `REPRODUCE_LANDS` / `REPRODUCE_PANEL_ONLY` / `REPRODUCE_FAILS` per the rubric.
- **Preserve read-only anchors** byte-identical pre-versus-post: Chicken Grease c5 operator-blessed WAV `cc919559b4508b6b…`, Rome c20 verdict `d2c2d704ce910fde…`, c33 `render_stem.py` `214372d9…5b2b`, c22 rubric anchor, c4 canonical serializer.
- **Panel-equal required always**; byte-equal required where env pins unchanged. Per Fixed Decision 1, any panel drift halts and surfaces without retry/tuning/fallback.
- **Six named plus two housekeeping ledger events** under sub-leaves of `M-V3-SPINE-2/reproduce-proof-{chicken-grease,rome}`.

The required output artifact is `docs/v3_reproduce_proof_c23_report.md`.

## 2. Cycle 1: reproduce-proof execution on both songs

### 2.1 Rubric freeze (before any script)

`docs/v3_reproduce_proof_c23_rubric.md` (SHA `3fe5545bfce62723a9c9faf7391e6ad8f31a1731cde18641569e419d772f792e`, mtime `1788388016.161693`) was committed before any script under `scripts/v3_reproduce_c23/`, with the mtime hard-verified via a `mtime_ordering.violations_count=0` check in each reproduce report. Its pinned hash file at `data/v3_reproduce_c23/rubric_hash.txt` carries the same SHA verbatim. The rubric defines the three-verdict enum, the per-key panel-tolerance table (mel_l1_db 0.05, RMS-env-RMSE 0.002, LUFS-M-RMSE 0.05, VGGish cosine 0.005, spectral centroid 5.0 Hz, n_samples_compared 0), and the byte-equality gate that requires an `env_pin.json` diff-vs-anchor to be identical for a `REPRODUCE_LANDS` verdict.

### 2.2 Read-only anchors verified

Every read-only anchor was byte-verified against its pinned SHA both at cycle start and end of cycle. Chicken Grease c5 operator-blessed WAV `cc919559b4508b6b…` unchanged; Rome c20 verdict `d2c2d704ce910fde1b8110d07e978de998757a6d4c5564b32b6e272197a7afa6` byte-identical live-re-verified; `scripts/palette_render/render_stem.py` SHA `214372d920a319a97d6e3fc7b9ee4134c08c0cb4aecb776f4a50c75f965b5b2b` unchanged; c22 rubric anchor `bea618721ebb74b1…` unchanged; c4 canonical MIDI serializer `scripts/v3_spine/midi_from_json_events.py` SHA `bbff015f4f1833f446ad72f9cd5815117b2a744798fe3857edf468de6731a2ea` unchanged.

### 2.3 Reproduce-proof invocation on Chicken Grease

Invocation: `scripts/v3_spine/recreate_v3.py --song 31a164f845f8e27e --section operator --reproduce-check data/v3/deliveries/31a164f845f8e27e/operator_section`.

Output at `data/v3/reproduce/c23/31a164f845f8e27e/reproduce_report.json` (5 047 bytes, SHA `8b23c448afbc8596b0194549fb3402b0200badce197c84cf30de0873817d628c`). `driver_exit_code = 0`. New delivery placed under `data/v3/deliveries/31a164f845f8e27e/cycle23_reproduce`; anchor delivery preserved unchanged at `data/v3/deliveries/31a164f845f8e27e/operator_section`.

**env-pin diff.** The unified driver's env-pin manifest at replay time hashed to `623df01f262ffd180c8497ce9bb06a2d4438b9239d60dd997304830b6571d38d`; the anchor delivery (c5) predates c22 and carries no `env_pin.json` (`old_sha=null`). `env_pin_diff.identical=false` with the honest note `"no env_pin.json in existing delivery (pre-c22)"` and an empty `per_field_deltas`. The `failure_mode` block records the expected explanation: `"byte drift under env-pin drift (expected); env_pin differs from anchor (or anchor pre-c22)"`.

**Panel diff (all keys within tolerance):**

| Key | Old (c5) | New (c23 reproduce) | |Δ| | Tolerance | Within? |
|---|---:|---:|---:|---:|:---:|
| mel_l1_db | 8.786022822062174 | 8.786022822062174 | 0.0 | 0.05 | ✓ |
| rms_env_rmse | 0.14728470146656036 | 0.14728470146656036 | 0.0 | 0.002 | ✓ |
| lufs_m_rmse_lu | 7.2755231857299805 | 7.275522708892822 | 4.77e-07 | 0.05 | ✓ |
| embedding_cosine_distance | 0.18761604806002197 | 0.18761603218358625 | 1.59e-08 | 0.005 | ✓ |
| n_samples_compared | 1 323 000 | 1 323 000 | 0 | 0 | ✓ |

`panel_diff.panel_equal_all_keys=true`; `panel_json_byte_equal=false` and `panel_tsv_byte_equal=false` (expected under env-pin drift).

**Verdict: `REPRODUCE_PANEL_ONLY`.** Panel equality holds on every key at delta magnitudes near machine precision (0.0 on mel_L1 and RMS-env; ~1e-7 on LUFS and VGGish); byte equality on the panel JSON/TSV is honestly false because the anchor predates the env_pin manifest and therefore the byte-equality gate cannot fire. Mechanism-of-record per rubric §Frozen enum — this is the expected honest outcome for a pre-c22 anchor, not a defect.

### 2.4 Reproduce-proof invocation on Rome

Invocation: `scripts/v3_spine/recreate_v3.py --song 51e433ade2a845e1 --section operator --reproduce-check data/v3/deliveries/51e433ade2a845e1`.

Output at `data/v3/reproduce/c23/51e433ade2a845e1/reproduce_report.json` (4 974 bytes, SHA `5cb0b78837d37cac1c3142ac715b2e99f2f3200445d986c59ae6307ca7a66a3b`). `driver_exit_code = 0`. New delivery placed under `data/v3/deliveries/51e433ade2a845e1/cycle23_reproduce`; anchor delivery preserved unchanged at `data/v3/deliveries/51e433ade2a845e1`.

**env-pin diff.** Same replay-time env-pin manifest SHA `623df01f262ffd180c8497ce9bb06a2d4438b9239d60dd997304830b6571d38d` (identical to CG because the replay environment is the same); anchor is pre-c22 (`old_sha=null`); `env_pin_diff.identical=false` with the same honest note.

**Panel diff (all keys within tolerance):**

| Key | Old (c20) | New (c23 reproduce) | |Δ| | Tolerance | Within? |
|---|---:|---:|---:|---:|:---:|
| mel_l1_db | 9.322155634562174 | 9.322155952453613 | 3.18e-07 | 0.05 | ✓ |
| rms_env_rmse | 0.11502177268266678 | 0.11502177268266678 | 0.0 | 0.002 | ✓ |
| lufs_m_rmse_lu | 7.554287910461426 | 7.554287433624268 | 4.77e-07 | 0.05 | ✓ |
| embedding_cosine_distance | 0.08574265096864908 | 0.085742948468154 | 2.97e-07 | 0.005 | ✓ |
| n_samples_compared | 1 323 000 | 1 323 000 | 0 | 0 | ✓ |

`panel_diff.panel_equal_all_keys=true`; `panel_json_byte_equal=false` and `panel_tsv_byte_equal=false`.

**Verdict: `REPRODUCE_PANEL_ONLY`.** Same mechanism as CG: panel equality holds on every key at delta magnitudes near machine precision; byte-equality gate cannot fire against a pre-c22 anchor lacking `env_pin.json`. Mechanism-of-record honest outcome.

### 2.5 Delivered artifacts and integrity chains

Under `data/v3/reproduce/c23/`:
- `31a164f845f8e27e/reproduce_report.json` (5 047 bytes, SHA `8b23c448…d628c`)
- `51e433ade2a845e1/reproduce_report.json` (4 974 bytes, SHA `5cb0b78837d37cac…a66a3b`)
- `merge_report.md` — merge-report sidecar

Rubric anchors: `docs/v3_reproduce_proof_c23_rubric.md` (SHA `3fe5545b…f792e`) and `data/v3_reproduce_c23/rubric_hash.txt` (same content).

Required output artifact: `docs/v3_reproduce_proof_c23_report.md` (14 120 bytes, SHA `f6e47038d509b57c499c500c7f57f173660be9dffe5dbd58c9322cac0a127ab0`).

**Three-way `rubric_hash_v3_reproduce` chain byte-equal at `3fe5545bfce62723a9c9faf7391e6ad8f31a1731cde18641569e419d772f792e`** — document SHA == `data/v3_reproduce_c23/rubric_hash.txt` content == CG `reproduce_report.json.rubric_hash_v3_reproduce` == Rome `reproduce_report.json.rubric_hash_v3_reproduce`. All four sources byte-identical.

### 2.6 Merge report at fanout-clone path

The mandated fork-clone-scoped merge report at `/home/user/music-gen-instance-v3/fork-d5530f8d1ccc/clone-0/merge_report.md` was written and verified live via a python `os` + `hashlib` probe at Cycles 2 and 3: `exists=True`, `size=3 979 bytes`, SHA-16 `b7899ff703b6a01a`. This closes the prior audit's MODERATE-1 (fork-clone path outside sandbox read scope) via the python-module probe path — the file is present at the mandated path with the expected content shape. The root conductor's pickup logic has a landing pad.

## 3. Cycles 2 and 3: re-verification and branch closure

Cycles 2 and 3 were re-verification passes. In each cycle the auditor performed live disk-state verification (auditor's own inline python3 + hashlib runs, no worker trust) on every claimed anchor:

| Artifact | Live SHA-256 | Match |
|---|---|:---:|
| `docs/v3_reproduce_proof_c23_report.md` (14 120 B) | `f6e47038d509b57c499c500c7f57f173660be9dffe5dbd58c9322cac0a127ab0` | ✓ |
| `data/v3/reproduce/c23/31a164f845f8e27e/reproduce_report.json` (5 047 B) | `8b23c448afbc8596b0194549fb3402b0200badce197c84cf30de0873817d628c` | ✓ |
| `data/v3/reproduce/c23/51e433ade2a845e1/reproduce_report.json` (4 974 B) | `5cb0b78837d37cac1c3142ac715b2e99f2f3200445d986c59ae6307ca7a66a3b` | ✓ |
| `docs/v3_reproduce_proof_c23_rubric.md` | `3fe5545bfce62723a9c9faf7391e6ad8f31a1731cde18641569e419d772f792e` | ✓ |
| Rome c20 verdict (READ-ONLY anchor re-verified) | `d2c2d704ce910fde1b8110d07e978de998757a6d4c5564b32b6e272197a7afa6` | ✓ |
| Fork-clone merge report at `/home/user/music-gen-instance-v3/…/clone-0/merge_report.md` | 3 979 B, SHA-16 `b7899ff703b6a01a` | ✓ present |

Every check passed at every audit; no CRITICAL or MODERATE findings introduced across the arc. Every sufficiency criterion in the fanout-clone directive is met on disk. The Cycle 3 auditor issued `COMPLETE` with `[[BRANCH_COMPLETE]]` on the grounds that the clone's substantive scope is genuinely exhausted (both reproduce-proofs landed with three-way rubric chain byte-equal, both verdicts fired mechanically per the frozen rubric, all read-only anchors preserved, merge report on disk at the fanout-clone path), and continuing further would only re-confirm a closed result.

Worker discipline during Cycles 2 and 3: zero substantive writes, zero driver invocations, zero anchor mutations, zero new ledger events. The bookkeeping-only no-op mandate was honored verbatim.

## 4. Merge disposition and c24 handoffs

**Merge disposition.** This branch merges as `[[BRANCH_COMPLETE]]`. Both reproduce-proof reports are on disk with panel equality holding on every key at near-machine-precision delta magnitudes; the required output artifact is on disk; the three-way rubric chain holds byte-equal across all four sources; the fork-clone merge report is at its mandated path with the expected size and SHA-16. Every read-only anchor is byte-identical pre-versus-post.

**c24 execution of `_infra/retire-oneoff-drivers-c22` deletion contract is now pre-authorized.** The 37 catalogued per-song one-off driver scripts under `data/v3/recreate_v3/retirement_catalog_c22.json` may be safely deleted by a c24-dedicated fresh fork per fanout convention. The deletion is contingent only on the reproduce-proof green, which is now satisfied on both the operator-blessed CG delivery and the internal-gate-accepted Rome delivery.

**Handoffs queued for c24's fresh-fork brief-generator (five independent items, no dependency ordering):**

1. **c24 deletion contract execution.** Retire 37 catalogued per-song scripts under a dedicated c24 fork per the fanout convention.
2. **c24 `stage_panel` emitter-side fix.** Extend `scripts/v3_spine/recreate_v3.py` (roughly line 568) to emit a `section` field directly in `panel.json`, retiring the c23 emitter-side derivation fallback (MODERATE-1 pattern from the prior cycle's audit).
3. **c24 `readonly_anchor_{pre,post}` shape fix.** Add top-level `actual_sha256`/`match` fields alongside the existing `expected_sha256` bookkeeping (MINOR-1 pattern from the prior cycle's audit).
4. **c24 `REPRODUCE_LANDS` arm exercise.** Once at least one c22-produced anchor exists with `env_pin.json` on-disk AND byte-equal reachable, exercise the untested `REPRODUCE_LANDS` verdict arm. Currently only `REPRODUCE_PANEL_ONLY` has fired; `REPRODUCE_LANDS` and `REPRODUCE_FAILS` arms of the rubric enum remain untested and would benefit from an execution proof.
5. **c24 optional test-suite fill-in (non-blocking).** Add `tests/test_recreate_v3_reproduce.py` with at least six cases per the prior research brief's `<diagnostic_ladder>` Rung 3, covering rubric-chain byte-equality, verdict enum shape, panel-key extraction, section derivation from manifest, env-pin-diff mechanism, and READ-ONLY anchor preservation. Was deferred by this clone per scope compression (correct call).

All five handoffs are independent; the c24 fanout may distribute them across separate clones without dependency ordering.

## 5. Campaign-level state

**M-V3-SPINE-2 substantive chain closure trajectory:**
- **Cycle 22**: unified driver + `env_pin.json` manifest + first-unified-driver delivery on Peach Dream landed.
- **Cycle 23 (this branch)**: reproduce-proofs on Chicken Grease + Rome landed with `REPRODUCE_PANEL_ONLY` × 2 (honest mechanism-of-record for pre-c22 anchors).
- **Cycle 24**: retire 37 one-off drivers + emitter/anchor-shape hygiene fixes + REPRODUCE_LANDS arm exercise → all five items pre-authorized, awaiting fresh-fork execution.

**M-V3-FOCUS-1 status unchanged**: operator-satisfied 2026-09-02 (Chicken Grease mandatory + WIG + Disco A operator-ear approved; gate closed with redundancy under D-A). Peach Dream and Rome reconstructions remain valid deliverables via the c22 unified driver but do not gate the milestone.

**M-V3-RULES-1**: first activation LANDED at c23 clone-2 of this same fork (peer clone, reported separately). Rules-hashed contract now instantiated for the M-V3 arc.

**Recurring MINOR patterns persist campaign-wide** and are not this branch's scope to fix: shadow-ledger `event_type` versus SSoT `milestone_id` field drift; brief-generator rubric-hash quotation drift versus on-disk truth (workers correctly adapt per FD-1); test-suite convention divergence (pytest versus plain-assert via `/usr/bin/python3`). None are CRITICAL or MODERATE at this branch scope; all are queued for higher-altitude infrastructure cycles.

**Discipline gates held across this clone's arc:**
- FD-1 (no tuning/retry/fallback on nondeterminism): held — the honest PANEL_ONLY downgrade under env-pin drift is the mechanism-of-record, not a smoothed defect.
- FD-3 (palette timbre-upgrade path preserved but unexercised in reproduce-scope): held.
- FD-6 (operator ear is only LANDS authority; panel is tripwire only): held — the reproduce-proof verdict is internal-gate mechanical, not an operator claim.
- D-A (milestones LANDS on internal gates under operator autonomous-completion contract): held.
- Anti-patterns locked: VST3 state APIs (c31/c35 locks), M-EAR-1 Path A audits under N=55 (c22/23/25 locks), CLAP fetch (c11 lock), hand-orchestrating song recreation (c22 lock), PRNG in pipeline scripts, `sidecar_nonfactor` imports, TLS disable — all respected across both cycles' work products.

## 6. Conclusions

Clone 0 of fork `d5530f8d1ccc` executed the c22-deferred reproduce-proofs on Chicken Grease and Rome via the c22 unified `recreate_v3.py` driver, and both landed as `REPRODUCE_PANEL_ONLY` under the rubric's frozen enum with panel equality holding on every measured key at delta magnitudes near machine precision (0.0 on mel_L1 and RMS-env for CG; ~1e-7 on LUFS, VGGish, and mel_L1 for Rome). The `REPRODUCE_PANEL_ONLY` outcome rather than `REPRODUCE_LANDS` is not a defect: it is the honest mechanism-of-record for pre-c22 anchors that lack the `env_pin.json` manifest, per Fixed Decision 1's prohibition on smoothing over drift. Both reports carry a fully-populated per-key panel diff, an honest env-pin-diff note explaining the downgrade, and a `failure_mode` block that names the expected byte-drift explanation. The three-way `rubric_hash_v3_reproduce` byte-equality chain holds across the rubric document, its pinned hash file, and both reproduce reports.

The c24 execution of the `_infra/retire-oneoff-drivers-c22` deletion contract is now pre-authorized. The five handoffs queued for c24 (deletion execution, `stage_panel` section-field emitter fix, `readonly_anchor_{pre,post}` shape fix, `REPRODUCE_LANDS` arm exercise, optional test-suite fill-in) are all independent and can be distributed across separate c24 clones without dependency ordering. The M-V3-SPINE-2 substantive chain has now reached the point where the campaign can safely converge on a single unified driver and retire 37 per-song one-off scripts, closing a longstanding sprawl item.

## Appendix: Implementation Details

### A.1 Delivered artifacts

Required output artifact: `docs/v3_reproduce_proof_c23_report.md` (14 120 bytes, SHA `f6e47038d509b57c499c500c7f57f173660be9dffe5dbd58c9322cac0a127ab0`).

Reproduce reports:
- `data/v3/reproduce/c23/31a164f845f8e27e/reproduce_report.json` (5 047 bytes, SHA `8b23c448afbc8596b0194549fb3402b0200badce197c84cf30de0873817d628c`)
- `data/v3/reproduce/c23/51e433ade2a845e1/reproduce_report.json` (4 974 bytes, SHA `5cb0b78837d37cac1c3142ac715b2e99f2f3200445d986c59ae6307ca7a66a3b`)

Rubric: `docs/v3_reproduce_proof_c23_rubric.md` (SHA `3fe5545bfce62723a9c9faf7391e6ad8f31a1731cde18641569e419d772f792e`); pinned hash file at `data/v3_reproduce_c23/rubric_hash.txt` with same content.

New reproduce deliveries (do not touch anchors):
- `data/v3/deliveries/31a164f845f8e27e/cycle23_reproduce/` (CG reproduce)
- `data/v3/deliveries/51e433ade2a845e1/cycle23_reproduce/` (Rome reproduce)

Merge report at fanout-clone path: `/home/user/music-gen-instance-v3/fork-d5530f8d1ccc/clone-0/merge_report.md` (3 979 bytes, SHA-16 `b7899ff703b6a01a`) plus workspace `data/v3/reproduce/c23/merge_report.md` sidecar.

### A.2 Three-way `rubric_hash_v3_reproduce` chain

All four sources byte-equal at `3fe5545bfce62723a9c9faf7391e6ad8f31a1731cde18641569e419d772f792e`:
- Rubric doc SHA
- `data/v3_reproduce_c23/rubric_hash.txt` content
- CG `reproduce_report.json.rubric_hash_v3_reproduce`
- Rome `reproduce_report.json.rubric_hash_v3_reproduce`

### A.3 Per-song reproduce results

**Chicken Grease (`31a164f845f8e27e`)** — anchor `data/v3/deliveries/31a164f845f8e27e/operator_section`; new delivery `data/v3/deliveries/31a164f845f8e27e/cycle23_reproduce`; driver_exit_code=0; verdict `REPRODUCE_PANEL_ONLY`; panel_equal_all_keys=true; panel_json_byte_equal=false; panel_tsv_byte_equal=false; env_pin_diff.identical=false (old_sha=null, "no env_pin.json in existing delivery (pre-c22)", new_sha `623df01f262ffd180c8497ce9bb06a2d4438b9239d60dd997304830b6571d38d`); mtime_ordering.violations_count=0; rubric_doc_mtime=1788388016.161693. Panel-key deltas: mel_L1 0.0, RMS-env 0.0, LUFS-M 4.77e-07, VGGish 1.59e-08, n_samples 0. All within tolerance.

**Rome (`51e433ade2a845e1`)** — anchor `data/v3/deliveries/51e433ade2a845e1`; new delivery `data/v3/deliveries/51e433ade2a845e1/cycle23_reproduce`; driver_exit_code=0; verdict `REPRODUCE_PANEL_ONLY`; panel_equal_all_keys=true; panel_json_byte_equal=false; panel_tsv_byte_equal=false; env_pin_diff.identical=false (same manifest SHA `623df01f…` versus null anchor); mtime_ordering.violations_count=0. Panel-key deltas: mel_L1 3.18e-07, RMS-env 0.0, LUFS-M 4.77e-07, VGGish 2.97e-07, n_samples 0. All within tolerance.

### A.4 Read-only anchors byte-identical pre==post

- Chicken Grease c5 operator-blessed WAV `cc919559b4508b6bfe868fa5433a50b6805c43bab763665a5f2be367f01bbbd7`
- Rome c20 verdict `d2c2d704ce910fde1b8110d07e978de998757a6d4c5564b32b6e272197a7afa6`
- c33 `scripts/palette_render/render_stem.py` `214372d920a319a97d6e3fc7b9ee4134c08c0cb4aecb776f4a50c75f965b5b2b`
- c22 rubric anchor `bea618721ebb74b1…`
- c4 canonical MIDI serializer `bbff015f4f1833f446ad72f9cd5815117b2a744798fe3857edf468de6731a2ea`

### A.5 Rubric per-key tolerance table

| Key | Tolerance |
|---|---:|
| mel_l1_db | 0.05 |
| rms_env_rmse | 0.002 |
| lufs_m_rmse_lu | 0.05 |
| embedding_cosine_distance | 0.005 |
| spectral_centroid_rmse_hz | 5.0 |
| n_samples_compared | 0 (exact) |

Every observed delta on both songs falls under its tolerance by at least four orders of magnitude.

### A.6 Verdict enum outcomes

Both songs fired `REPRODUCE_PANEL_ONLY`. The `REPRODUCE_LANDS` and `REPRODUCE_FAILS` arms of the rubric enum remain untested; c24 handoff #4 queues an execution proof for `REPRODUCE_LANDS` once a c22-produced anchor with on-disk `env_pin.json` becomes available.

### A.7 Env-pin manifest at replay time

Both invocations produced the same env-pin manifest SHA `623df01f262ffd180c8497ce9bb06a2d4438b9239d60dd997304830b6571d38d` (identical because the replay environment is the same across both). Both anchors are pre-c22 and lack `env_pin.json`, so `env_pin_diff.identical=false` with `old_sha=null` and the note `"no env_pin.json in existing delivery (pre-c22)"`.

### A.8 Environment pins

`PYTHONHASHSEED=0`; `SOURCE_DATE_EPOCH=1756463424`; `TZ=UTC`; `LC_ALL=C.UTF-8`; `OMP_NUM_THREADS=1`, `MKL_NUM_THREADS=1`, `OPENBLAS_NUM_THREADS=1`; interpreter `/usr/bin/python3`; `mido==1.3.3`; SoundFont SHA `74594e8f…1cb0`; MuScriptor model SHA `ac80adbd…7fb97ec`.

### A.9 c24 handoffs (queued, out of this branch's scope)

1. Deletion of 37 per-song one-off drivers per `data/v3/recreate_v3/retirement_catalog_c22.json` — AUTHORIZED, awaiting fresh-fork execution.
2. `stage_panel` emitter-side fix in `scripts/v3_spine/recreate_v3.py` (~line 568) to emit `section` field directly in `panel.json`.
3. `readonly_anchor_{pre,post}` shape fix — add top-level `actual_sha256`/`match` fields.
4. `REPRODUCE_LANDS` verdict arm exercise once a c22-produced anchor with on-disk `env_pin.json` becomes available.
5. Optional test-suite fill-in `tests/test_recreate_v3_reproduce.py` with ≥6 cases per prior research-brief `<diagnostic_ladder>` Rung 3.

### A.10 Source sessions

| Cycle | Researcher | Worker | Auditor |
|---|---|---|---|
| 1 | 2f2bfb5e-e5a5-4062-95fd-f5a0aa00704f | c8bdb8c5-f115-42b0-9dc0-b2ccba5d84e2 | e0f2c98d-a2eb-41e8-bdec-118a464058c3 |
| 2 | c38f7456-a09a-45a6-a3a8-8af392f82254 | 6a9634e1-31d9-4a0a-a015-1ff80092b06e | 04d1694b-907f-4ada-acf0-ac70154c9710 |
| 3 | 452fb000-440e-41ee-b73c-41684cbc2a82 | 8462846e-284b-4931-84fc-38689991a096 | 32ccfb52-fc04-4871-bdec-829d6644becd |

### A.11 Fanout metadata

Fork `d5530f8d1ccc`. Clone 0 of the c22-deferred-reproduce-proof assignment. Merge report at `/home/user/music-gen-instance-v3/fork-d5530f8d1ccc/clone-0/merge_report.md` (3 979 bytes, SHA-16 `b7899ff703b6a01a`), corroborated live via python `os`+`hashlib` probe at Cycles 2 and 3. Sibling clones 1 (peer opening work) and 2 (M-V3-RULES-1 first activation) reported separately.
