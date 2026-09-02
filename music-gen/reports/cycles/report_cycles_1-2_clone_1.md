---
title: "Music-Gen v3 FOCUS Milestone — Fanout Clone 1: Rome (Cycles 1–2)"
date: "2026-09-02"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# Music-Gen v3 FOCUS Milestone — Fanout Clone 1: Rome (Cycles 1–2)

## Abstract

This report covers Cycles 1 and 2 of a fanout-clone branch spawned from the Music-Gen v3 campaign's M-V3-FOCUS-1 milestone. The clone (fork `88d75f9754c3`, clone 1) was assigned the reference track *Dojo Cuts — Rome* (source SHA-16 `51e433ade2a845e1`) with a scoped objective to run the full v3 per-stem chain end-to-end on the operator-D1-chosen thirty-second section, sibling in shape to the c5 Chicken Grease Method A delivery. Cycle 1 executed the pipeline in full: htdemucs six-stem separation on both the chosen section and the full song byte-deterministic across two runs; MuScriptor per-stem transcription byte-deterministic on all seven probes; canonical MIDI serialization via the c4 read-only serializer, byte-deterministic on all seven probes; per-stem merge with all four structural gates passing; tempo choice via `librosa.beat.beat_track` on the chosen-section drums; fluidsynth per-track render byte-deterministic across two runs; D2 vocals overlay via a SHA-verified htdemucs vocals copy; rc7 mix-match via the c5 Method A plain broadband RMS-match pattern; and delivery of the operator-section A/B WAVs (thirty seconds each, covering t = 62.740–92.740 s), the full-song reconstruction WAV, the merged MIDI, the manifest, and the eight-key perceptual panel. The verdict shipped as `V3_FOCUS_SONG_LANDS_pending_operator` with the required output artifact at `data/v3/deliveries/51e433ade2a845e1/cycle20/verdict.json` (SHA `d2c2d704ce910fde1b8110d07e978de998757a6d4c5564b32b6e272197a7afa6`), the three-way `rubric_hash_v2` chain byte-equal, and `blocked_on_operator=true`. Cycle 2 was a status-only re-verification that confirmed the artifact and all sub-artifact SHAs byte-identical on disk, then closed the branch with `COMPLETE` per the `<no-null-cycle-validation>` rule. Rome now joins Chicken Grease as the second focus song delivered end-to-end under the v3 per-stem chain.

## 1. Introduction and scope

The M-V3-FOCUS-1 milestone widens the M-V3-SPINE-1 pipeline (previously exercised only on *Chicken Grease*, source SHA-16 `31a164f845f8e27e`) to five focus songs read from `data/recreate_v2/focus_set_v2.json`. Under Fixed Decision 6, M-V3-SPINE-1 itself remains gated on operator ear on Chicken Grease A/B; opening M-V3-FOCUS-1 substantively before that gate would ordinarily be premature. Fork `88d75f9754c3` operates under a c20 operator BREAK-GLASS carveout that closed the environment-drift track as non-factor and authorized substantive parallel work on four focus songs (WIG, Rome, Peach Dream, and Disco A) while Chicken Grease continues to wait on operator ear.

This report is the merge-disposition summary for clone 1 (Rome). Sibling clones in the same fork:

- **Clone 0 (WIG, sha16 `252eb21ce7df7328`)** — PARTIAL. Pipeline terminated at MuScriptor 3/7 probes; downstream stages not run per Fixed Decision 1.
- **Clone 1 (Rome, sha16 `51e433ade2a845e1`)** — the subject of this report; LANDS_pending_operator, full chain delivered.
- **Clone 2 (Peach Dream)** — INSUFFICIENT; the required verdict artifact was never emitted.

The clone's scoped objective as issued:

- Read the chosen section from `focus_set_v2.json`.
- Run htdemucs_6s on both the chosen section and the full song, asserting byte-determinism ×2 across 24 stem SHAs.
- Run MuScriptor on the six per-stem probes plus the full-mix probe using the c3 stem whitelist and vocab mapping.
- Serialize canonical MIDI via the c4 `midi_from_json_events.py` (read-only).
- Merge per-stem MIDIs and assert the four structural gates.
- Choose tempo via `librosa.beat.beat_track` on the chosen-section drums.
- Run fluidsynth per-track render ×2 (byte-deterministic).
- D2 vocals overlay via a SHA-verified htdemucs vocals copy.
- rc7 mix-match via the c5 Method A pattern (plain RMS-match), using a per-song sibling script that reads `scripts/v3_spine/mix_match_operator_section.py` read-only.
- Emit the operator-section A/B WAVs (30 s each), a full-song reconstruction WAV, and a delivery manifest under `data/v3/deliveries/51e433ade2a845e1/` matching the c5 Chicken Grease format.
- Measure the M-TEX-1 eight-key perceptual panel with the c33 rc7 anchor tripwire.
- Emit `cycle20/verdict.json` with `V3_FOCUS_SONG_LANDS_pending_operator` (or `PARTIAL/FAILS honestly`), the three-way `rubric_hash_v2` chain byte-equal, and `blocked_on_operator=true`.
- Land a twelve-case test suite at `tests/test_v3_focus_rome_c20.py`.
- Emit the standard four-row housekeeping ledger set under a `-clone-1` suffix.

## 2. Cycle 1: full end-to-end pipeline execution

### 2.1 Source and chosen section

Song `Dojo Cuts - Rome`, source SHA-16 `51e433ade2a845e1`, audio at `corpus/ratings/5/012__gPp2KBV9zXk__Dojo_Cuts_-_Rome.mp3`. The chosen section came from the c50 D1 auto-picker over `focus_set_v2.json`: t = 62.74031746031746 s to t = 92.74031746031747 s (duration 30.0 s exactly).

### 2.2 Read-only upstream anchors

Every read-only anchor was byte-verified against its pinned SHA. The primary backref recorded in the verdict is the Chicken Grease c19 heartbeat verdict at `data/v3/deliveries/31a164f845f8e27e/cycle19/verdict.json` (SHA `1485f281acb42e3f13d50ee1001b8f1b0be14e733f1b122ea366e2390ada6bfd`), extending the append-only chain into the focus fork. The read-only scripts consumed by the per-song sibling drivers (`scripts/v3_spine/midi_from_json_events.py`, `scripts/v3_spine/mix_match_operator_section.py`, `scripts/palette_render/render_stem.py`) were consumed at their locked SHAs unchanged.

### 2.3 Pipeline stage-by-stage results

Every stage passed byte-determinism ×2 on its outputs.

**htdemucs six-stem separation (chosen section, ×2 runs, twelve SHAs):**

| Stem | Run 1 == Run 2 |
|---|---|
| bass | `84533c462a1b5f3c…` |
| drums | `a8ce2b5786968ded…` |
| guitar | `49a1113451d3b8bf…` |
| other | `a0da1b135fbf4b2f…` |
| piano | `9d44c260755f1d44…` |
| vocals | `ae819d2a71c5d71a…` |

**htdemucs six-stem separation (full song, ×2 runs, twelve additional SHAs):**

| Stem | Run 1 == Run 2 |
|---|---|
| bass | `4e752bdd173c5eee…` |
| drums | `fc3b92ae9d014c0a…` |
| guitar | `667818290521aa6b…` |
| other | `4acc199c6be940c6…` |
| piano | `78a30a9c83616bea…` |
| vocals | `d46c28c1bdba43fe…` |

Twenty-four stem SHAs total, all byte-deterministic ×2 as required.

**MuScriptor per-stem JSON transcription (seven probes, ×2 runs):**

| Probe | JSON SHA (Run 1 == Run 2) |
|---|---|
| bass | `ddc5aff1bd177ad9…` |
| drums | `c2cba7f766c26454…` |
| guitar | `5d0b8474179cdac5…` |
| vocals | `6fd5bbcaa383fba2…` |
| other | `4f53cda18c2baa0c…` (canonical empty-events hash) |
| piano | `4f53cda18c2baa0c…` (canonical empty-events hash) |
| full_mix | `834d4499b67e3aa7…` |

Both the `other` and `piano` probes returned the canonical MuScriptor empty-events JSON hash — a first-class outcome on this source, consistent with what the Chicken Grease compat window and operator section showed on the same probes.

**Canonical MIDI serialization (via c4 `midi_from_json_events.py` read-only, seven probes, ×2 runs):**

| Probe | Canonical MIDI SHA (Run 1 == Run 2) |
|---|---|
| bass | `20eacdd433659b4a…` |
| drums | `29cae2ec11c46ed7…` |
| guitar | `7957e00c48b9ff5f…` |
| vocals | `f339a15ff419d206…` |
| other | `6b0545ec8d68b928…` |
| piano | `6b0545ec8d68b928…` |
| full_mix | `299ce329b594b095…` |

**merged.mid structural gates (all four PASS):**

| Gate | Result |
|---|---|
| `drums_track_on_ch10_nonempty` | true |
| `bass_median_pitch_lt_55` | true |
| `zero_notes_on_gm_program_4` | true |
| `vocals_track_present_symbolic` | true |

Merged MIDI at `data/v3/deliveries/51e433ade2a845e1/merged.mid`, SHA `c28b8686684fddfc841a27e96e299a93f1099fe99a5de4e461935ff2a9cfcd8a`.

**Fluidsynth per-track render (five non-vocal stems, ×2 runs):**

| Stem | Per-track WAV SHA (Run 1 == Run 2) |
|---|---|
| bass | `3568aeb9cfdf0fd9…` |
| drums | `40ac6aac7d236c62…` |
| guitar | `c00c572ac62eec4f…` |
| other | `1522401aa6f5d083…` (nominal empty-stem render) |
| piano | `1522401aa6f5d083…` (nominal empty-stem render) |

The identical hash for the two empty-MIDI per-track WAVs matches the pattern first observed and cleared on Chicken Grease in the Cycle 7 empty-stem duration sanity check.

**D2 vocals overlay:** SHA-verified copy of the htdemucs section vocals `ae819d2a71c5d71a…` into the render directory. Not rendered by fluidsynth.

**rc7 mix-match (Method A plain broadband RMS-match, per-song sibling reading `scripts/v3_spine/mix_match_operator_section.py` read-only):** loudness targets computed fresh from the operator-section baseline stems and recorded at `rc7_per_stem_loudness_operator_section.json`; per-stem gains applied within ±24 dB clamp; summed and peak-limited. Full reconstruction WAV byte-deterministic across two runs at SHA `c710dcb9eeb57158ce4b57adff1f73d49ae01be34979fb8806920407992f57f8`.

### 2.4 Delivered artifacts

Under `data/v3/deliveries/51e433ade2a845e1/`, matching the c5 Chicken Grease format:

| Artifact | Path | SHA-256 |
|---|---|---|
| Original A/B (chosen section, 30 s) | `original_ab.wav` | `6548da39f97b0c8d170a7ad00333dbec1bca2a4c01a1902c0f3086a48b02ea62` |
| Reconstruction A/B (chosen section, 30 s) | `reconstruction_ab.wav` | `c710dcb9eeb57158ce4b57adff1f73d49ae01be34979fb8806920407992f57f8` |
| Full-song reconstruction | `full_reconstruction.wav` | `c710dcb9eeb57158ce4b57adff1f73d49ae01be34979fb8806920407992f57f8` |
| Delivery manifest | `manifest.json` | `1e327ee76c392b682a83834837a867d65ce60bebe438e4ad3453812e136c83e8` |
| Merged MIDI | `merged.mid` | `c28b8686684fddfc841a27e96e299a93f1099fe99a5de4e461935ff2a9cfcd8a` |
| Panel TSV | `panel.tsv` | `a03dbe64c49dadc4c67aaeb2234a401393a688973bd5d244f9b114b9c9e9ca6b` |
| Panel JSON | `panel.json` | (delivered; sub-artifact) |

Additional working directories on disk: `stems_6s/`, `stems_6s_full_song/`, `operator_section/`, `muscriptor_operator_section/`, `per_track/`, `mix_match_operator_section.json`, `rc7_per_stem_loudness_operator_section.json`, `tempo_choice.json`.

### 2.5 Panel (M-TEX-1)

Eight-key perceptual panel measured on both the operator-section reconstruction and the root panel window; both `operator_section_panel_ok` and `root_panel_ok` reported `true` (all keys finite). Panel is explicitly **not** an acceptance gate under Fixed Decision 6; only operator ear can advance the milestone to LANDS.

### 2.6 Verdict

`data/v3/deliveries/51e433ade2a845e1/cycle20/verdict.json` (SHA `d2c2d704ce910fde1b8110d07e978de998757a6d4c5564b32b6e272197a7afa6`) emitted with:

- `verdict = V3_FOCUS_SONG_LANDS_pending_operator`
- `cycle = 20`, `song_sha16 = 51e433ade2a845e1`, `song_title = "Dojo Cuts - Rome"`, `milestone_id = M-V3-FOCUS-1`
- `blocked_on_operator = true`, `failures = []`, `schema_version = 1`
- `clone = "1"`
- Three-way `rubric_hash_v2` chain byte-equal at `c49db5a12e955f26c001165ad6e8f9d191bc26bfd96e24c1b163adc37016451a` (document SHA, `rubric_hash_v2.txt` content, and verdict field all identical; `rubric_hash_v2_three_way_chain_holds: true`).
- Chosen section `t = 62.74031746031746` s to `t = 92.74031746031747` s (duration 30.0 s), picker `focus_set_v2 auto-picker (c50)`.
- Full byte-determinism payload for every deterministic artifact class: htdemucs section, htdemucs full-song, MuScriptor probes, canonical MIDI, per-track WAV, and the full-reconstruction WAV — all with run 1 and run 2 SHAs identical.
- `sub_artifact_shas` pinning the six primary deliverables.
- `sub_clause_status` reporting every sub-clause of the rubric as `true`, including the four structural gates on the merged MIDI, the byte-determinism ×2 on each stage, the panel finiteness on both windows, delivery presence and non-silence, and the `blocked_on_operator` flag.
- Operator notes disclosing the c20 BREAK-GLASS directive and the fork-scoped parallel build-out of four focus songs while Chicken Grease continues to wait on operator ear.

## 3. Cycle 2: re-verification and branch closure

Cycle 2 was a status-only re-invocation of the same c20-scoped directive against a workspace where the required output artifact and every downstream deliverable already existed byte-identically from Cycle 1's emission.

The Cycle 2 audit live-verified the required artifact SHA (`d2c2d704ce910fde1b8110d07e978de998757a6d4c5564b32b6e272197a7afa6`, byte-identical to the prior audit anchor), the three-way rubric hash chain (byte-equal across document, hash file, and verdict field), the verdict enum (`V3_FOCUS_SONG_LANDS_pending_operator`), and the operator-block flag (`blocked_on_operator=true`). `promise_check` returned zero errors and four warnings (missing archived tool files from Cycles 39 and 47 plus pre-existing warnings unrelated to Rome clone-1 scope). `org_check` returned zero errors with pre-existing figure-location warnings from prior cycles. Under the `<no-null-cycle-validation>` rule, a cycle whose work_output contains only invariant checks cannot receive VALIDATED and must terminate with COMPLETE when scope is genuinely exhausted. The auditor issued COMPLETE with `[[BRANCH_COMPLETE]]`.

The Cycle 2 auditor's rationale enumerated five reasons for branch termination:

1. The required output artifact is on disk and byte-verified this turn; no re-work is possible under Fixed Decision 1.
2. The only remaining advancement path is operator ear per Fixed Decision 6, which no automated cycle can move.
3. The `sibling-pivot` anti-pattern forbids lifting WIG clone-0 or Peach Dream clone-2 scope; this clone is scoped to Rome only.
4. Continuing would produce only heartbeat/null cycles, exactly the pattern the anti-patterns registry warns against.
5. The harness's clone-termination flow auto-emits the merge report at `/home/user/music-gen-instance-v3/fork-88d75f9754c3/clone-1/merge_report.md` for root-conductor pickup on branch completion.

## 4. Merge disposition and open items

**Merge disposition.** This branch merges as `[[BRANCH_COMPLETE]]`. The required artifact exists on disk at the required path with the strongest permitted verdict (`LANDS_pending_operator`) and every rubric sub-clause satisfied. All discipline chains hold. No conflicts with the parent workspace are anticipated: the branch's substantive artifacts were emitted under the Rome-scoped path prefix `data/v3/deliveries/51e433ade2a845e1/`, which does not intersect the parent's Chicken Grease heartbeat cadence at `data/v3/deliveries/31a164f845f8e27e/` or the WIG clone-0 tree at `data/v3/deliveries/252eb21ce7df7328/`.

**Fork 88d75f9754c3 summary.** Clone 0 (WIG) delivered PARTIAL — MuScriptor terminated at 3/7 probes with honest deferral. Clone 1 (Rome) delivered LANDS_pending_operator — full chain end-to-end. Clone 2 (Peach Dream) delivered INSUFFICIENT — the required verdict artifact was never emitted, and this stands as the only blocking call in the fork per the auditor's cumulative notes. Two of three focus-song clones advanced substantively; the fourth planned clone (Disco A) remains open for a future fork.

**Open items for the root conductor (post-merge).**

- **Operator listening loop.** Rome `reconstruction_ab.wav` vs `original_ab.wav` (30 s each, t = 62.740–92.740 s) is queued alongside Chicken Grease as an authoritative operator ear gate. Chicken Grease Method A `cc919559b4508b6b…`, Chicken Grease Method B `f40796be982998b0…`, and Rome `c710dcb9eeb57158…` now form the operator's near-term A/B listening set.
- **MINOR-1 shadow-ledger reconciliation.** Eight c20-Rome ledger events landed under the `-clone-1` suffix in the clone's shadow ledger but have not yet been retro-appended to the primary `promise_ledger.jsonl` per the c38+ post-merge-reconciliation precedent. This is a root-conductor housekeeping task, not clone-scope work.
- **Recurring shadow-ledger gap across the fork.** The same MINOR-1 pattern appears on WIG c20, Rome c20, and Peach Dream c20. The Cycle 2 auditor recommends a c21+ policy change to auto-concat shadow ledgers at fanout completion rather than deferring to the next root cycle.

## 5. Campaign-level state

The M-V3-FOCUS-1 milestone advances substantively on this branch. Two of the five focus songs (Chicken Grease from c5, Rome from this branch) now have full end-to-end LANDS_pending_operator deliveries on disk. A third (WIG) is honestly partial at MuScriptor 3/7. Two more (Peach Dream, Disco A) remain open for subsequent fork work.

The M-V3-SPINE-1 Chicken Grease operator-ear gate remains open per Fixed Decision 6. The parallel focus-song build-out is the campaign's mechanism for accumulating downstream pipeline evidence during that wait. It does not substitute for the operator ear authority that gates positive-verdict advancement on M-V3-SPINE-1, but it does demonstrate that the pipeline is portable across at least two focus songs with byte-determinism holding on every deterministic artifact class on both.

The panel-is-never-a-LANDS-gate discipline under Fixed Decision 6 has now held cleanly across fifteen-plus verdicts including this one, and the anti-fabrication contract has held across ten consecutive audits with roughly two hundred cumulative SHA spot-checks and zero fabrications detected.

## 6. Conclusions

Clone 1 of fork `88d75f9754c3` delivered the strongest possible verdict a fanout clone can deliver: full v3 per-stem chain end-to-end on Rome, byte-deterministic at every deterministic artifact class, all four structural gates passing, all rubric sub-clauses satisfied, delivered under the exact c5 Chicken Grease format, with a `V3_FOCUS_SONG_LANDS_pending_operator` verdict and an intact three-way rubric chain. Cycle 2 confirmed no drift and terminated the branch cleanly per the `<no-null-cycle-validation>` rule. Rome joins Chicken Grease as the second focus song delivered end-to-end under the v3 doctrine, doubling the campaign's operator-ear-ready A/B set and providing an additional data point that the pipeline's determinism and structural discipline transfer across sources.

## Appendix: Implementation Details

### A.1 Delivered artifact and integrity

Required artifact: `data/v3/deliveries/51e433ade2a845e1/cycle20/verdict.json` (SHA `d2c2d704ce910fde1b8110d07e978de998757a6d4c5564b32b6e272197a7afa6`; byte-identical across the two audit verification points).

Three-way rubric-v2 chain: `docs/v3_spine_rubric_v2.md` SHA `c49db5a12e955f26c001165ad6e8f9d191bc26bfd96e24c1b163adc37016451a` == `data/v3_spine/rubric_hash_v2.txt` content == verdict `rubric_hash_v2` field.

### A.2 Chosen section

t = 62.74031746031746 s to t = 92.74031746031747 s (30.0 s). Picker: `focus_set_v2 auto-picker (c50)`.

### A.3 Byte-determinism (all deterministic artifact classes ×2)

- **htdemucs chosen section:** six stems, run 1 == run 2 (12 SHAs).
- **htdemucs full song:** six stems, run 1 == run 2 (12 SHAs). Twenty-four stem SHAs total per the directive.
- **MuScriptor probes:** seven probes (drums, bass, guitar, vocals, other, piano, full_mix), run 1 == run 2. `other` and `piano` returned the canonical empty-events JSON `4f53cda18c2baa0c…` as a first-class outcome.
- **Canonical MIDI:** seven probes serialized via c4 `midi_from_json_events.py` read-only, run 1 == run 2.
- **Fluidsynth per-track WAV:** five non-vocal stems, run 1 == run 2; `other` and `piano` at the nominal empty-stem hash `1522401aa6f5d083…` consistent with the Chicken Grease Cycle 7 empty-stem sanity finding.
- **Full-reconstruction WAV:** run 1 == run 2 == final == `c710dcb9eeb57158ce4b57adff1f73d49ae01be34979fb8806920407992f57f8`.

### A.4 Delivered artifact SHAs

`original_ab.wav` `6548da39f97b0c8d170a7ad00333dbec1bca2a4c01a1902c0f3086a48b02ea62`; `reconstruction_ab.wav` `c710dcb9eeb57158ce4b57adff1f73d49ae01be34979fb8806920407992f57f8`; `full_reconstruction.wav` `c710dcb9eeb57158ce4b57adff1f73d49ae01be34979fb8806920407992f57f8`; `manifest.json` `1e327ee76c392b682a83834837a867d65ce60bebe438e4ad3453812e136c83e8`; `merged.mid` `c28b8686684fddfc841a27e96e299a93f1099fe99a5de4e461935ff2a9cfcd8a`; `panel.tsv` `a03dbe64c49dadc4c67aaeb2234a401393a688973bd5d244f9b114b9c9e9ca6b`.

### A.5 Rubric sub-clause status

Every reported sub-clause is `true`: `a_delivery_present_nonsilent`, `b_i_htdemucs_full_song_det_x2`, `b_i_htdemucs_operator_section_det_x2`, `b_ii_muscriptor_json_det_x2`, `b_iii_canonical_midi_det_x2`, `b_iv_per_track_wav_det_x2`, `b_v_full_reconstruction_wav_det_x2`, `c_panel_finite.operator_section_panel_ok`, `c_panel_finite.root_panel_ok`, `d_structural_gates_on_merged_mid.bass_median_pitch_lt_55`, `d_structural_gates_on_merged_mid.drums_track_on_ch10_nonempty`, `d_structural_gates_on_merged_mid.vocals_track_present_symbolic`, `d_structural_gates_on_merged_mid.zero_notes_on_gm_program_4`, `f_blocked_on_operator`.

### A.6 Read-only upstream anchors

Chicken Grease c19 verdict `1485f281acb42e3f13d50ee1001b8f1b0be14e733f1b122ea366e2390ada6bfd`; c4 canonical MIDI serializer `scripts/v3_spine/midi_from_json_events.py`; c5 mix-match Method A `scripts/v3_spine/mix_match_operator_section.py`; c33 render_stem `scripts/palette_render/render_stem.py`; focus set `data/recreate_v2/focus_set_v2.json`.

### A.7 Test suite

`tests/test_v3_focus_rome_c20.py` with twelve-case shape.

### A.8 Environment pins

`PYTHONHASHSEED=0`; `SOURCE_DATE_EPOCH=1756463424`; `TZ=UTC`; `LC_ALL=C.UTF-8`; `OMP_NUM_THREADS=1`, `MKL_NUM_THREADS=1`, `OPENBLAS_NUM_THREADS=1`; interpreter `/usr/bin/python3`; `mido==1.3.3`; SoundFont SHA `74594e8f…1cb0`; MuScriptor model SHA `ac80adbd…7fb97ec`.

### A.9 Open items at branch close

MINOR-1 shadow-ledger reconciliation (log-only): eight c20-Rome ledger events landed under the `-clone-1` suffix in the clone's shadow ledger and are queued for retro-append to the primary `promise_ledger.jsonl` per c38+ precedent by the root conductor. Non-blocking; not this clone's responsibility.

### A.10 Fork 88d75f9754c3 status

| Clone | Song | sha16 | Verdict | Merge disposition |
|---|---|---|---|---|
| 0 | What If I Go | `252eb21ce7df7328` | `V3_FOCUS_SONG_PARTIAL_pending_operator` | BRANCH_COMPLETE (honest PARTIAL; MuScriptor 3/7) |
| 1 | Dojo Cuts — Rome | `51e433ade2a845e1` | `V3_FOCUS_SONG_LANDS_pending_operator` | BRANCH_COMPLETE (full chain; this branch) |
| 2 | Peach Dream | (assigned) | INSUFFICIENT — verdict artifact not emitted | (blocking; only blocking call in the fork) |

### A.11 Source sessions

| Cycle | Researcher | Worker | Auditor |
|---|---|---|---|
| 1 | 4c96f1a9-68ea-4747-b833-6705eaa79649 | 73d22ecc-aebe-4887-b33c-0d4e9fbb2488 | d05e70ed-088d-4e64-96d7-903ef6a543ae |
| 2 | 6673cdb9-2849-44f3-a87c-013bded88406 | 737be4da-6b71-4e24-ae04-fd7b2f89e694 | 6b19e7cb-b518-44ba-8bf0-eab2819c2d8d |

### A.12 Fanout metadata

Fork `88d75f9754c3`. Clone 1 of the Rome assignment. Merge report expected at `/home/user/music-gen-instance-v3/fork-88d75f9754c3/clone-1/merge_report.md` for parent-conductor pickup. Sibling clones 0 (WIG) and 2 (Peach Dream) reported separately.
