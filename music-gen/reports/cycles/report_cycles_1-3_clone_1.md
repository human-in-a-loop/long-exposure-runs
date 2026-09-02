---
title: "Music-Gen v3 FOCUS Milestone — Fanout Clone 1: WIG PARTIAL→LANDS Restart (Cycles 1–3)"
date: "2026-09-02"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# Music-Gen v3 FOCUS Milestone — Fanout Clone 1: WIG PARTIAL→LANDS Restart (Cycles 1–3)

## Abstract

This report covers Cycles 1 through 3 of a fanout-clone branch spawned from the Music-Gen v3 campaign's M-V3-FOCUS-1 milestone under the c22 root conductor's dispatch, specifically the c22 S3 imperative queued at the close of the c20 fanout arc. The clone (fork `0a1b1dca4f9b`, clone 1) was assigned to resume the *What If I Go* (Mura Masa, source SHA-16 `252eb21ce7df7328`) per-stem pipeline from the honest `V3_FOCUS_SONG_PARTIAL_pending_operator` state emitted by the c20 clone-0 branch (SHA `bd394c43c6134811257bb9b27539bf95e8d5b4663135d2646b0035f6b0e8ea2b`) and land the operator-D1-chosen thirty-second section (t = 72.77133786848073 s to t = 102.77133786848073 s) as a `V3_FOCUS_SONG_LANDS_pending_operator` delivery matching the c5 Chicken Grease Method A format exactly. The restart followed merge-report Option A: preserve the twelve c20 htdemucs section stem SHAs and the three completed c20 MuScriptor JSON SHAs byte-identical as read-only anchors, complete the four remaining MuScriptor probes (piano, vocals, other, full_mix) twice into fresh temporary directories under identical environment pins, then execute the downstream chain verbatim (canonical MIDI ×2, merge with four structural gates, fluidsynth per-track render ×2, D2 vocals overlay, rc7 Method A mix-match, delivery, panel). Cycle 1 delivered the restart end-to-end: every rubric sub-clause satisfied including the brief-mandated `sub_clause_status.f_restart_from_partial=true`, every deterministic artifact byte-deterministic ×2, all four structural gates passing on the merged MIDI, both panel comparisons finite, the required output artifact `docs/v3_focus_wig_restart_c21_report.md` landed, and the verdict emitted at `data/v3/deliveries/252eb21ce7df7328/cycle21/verdict.json` with SHA `95edf6cc741366d5f87e68c8658992830ba41fb7330bdb14b91d94cfedfbfec8` and every integrity chain holding byte-equal. Cycles 2 and 3 were re-verification passes that live-checked every anchor, ran the twelve-case test suite green live, and terminated the branch with `COMPLETE` and `[[BRANCH_COMPLETE]]` under the `<no-null-cycle-validation>` rule. The M-V3-FOCUS-1 milestone now closes with redundancy: four internal-gate accepts on record (Chicken Grease operator-ear-LANDED, plus internal-gate accepts on Rome, Disco A, and this WIG restart) against a required threshold of three.

## 1. Introduction and scope

The c20 fanout arc had delivered three of the five focus songs to various states: Chicken Grease sat in operator-LANDED state (as of the operator's 2026-09-02 ear judgment on the Cycle 5 v3 fluidsynth reconstruction); Rome (clone 1) delivered a full end-to-end `V3_FOCUS_SONG_LANDS_pending_operator` chain in a single fanout cycle; WIG (clone 0) reached honest PARTIAL after MuScriptor's background task terminated at 3/7 probes; Peach Dream (clone 2) reached honest PARTIAL after a three-turn Hold Pattern via the Option 3 escape. The M-V3-FOCUS-1 milestone was thus at two of three required accepts against the operator's D-A autonomous-completion contract.

The c22 root conductor's S2 and S3 imperatives were parallel fanout branches: S2 launching Disco A as the fifth focus song, and S3 restarting WIG from PARTIAL toward LANDS. This report covers the S3 branch (WIG restart). Sibling branches in the same fork:

- **Clone 0 (Disco A, S2)** — internal-gate LANDS at verdict SHA `28c33929…9859b2`.
- **Clone 1 (WIG restart, S3)** — the subject of this report; internal-gate LANDS at verdict SHA `95edf6cc…9bfec8`.
- **Clone 2 (Chicken Grease palette render)** — orthogonal secondary-deliverable branch reported separately; internal-gate PALETTE_MOVES_PANEL at verdict SHA `5ba4eaca…5644a`.

The clone's scoped objective as issued:

- **Resume from the c20 clone-0 PARTIAL state** rather than start fresh. Preserve the twelve c20 htdemucs section stem SHAs and the three completed c20 MuScriptor JSON SHAs byte-identical as read-only anchors.
- **Complete the four remaining MuScriptor probes** (piano, vocals, other, full_mix) twice into fresh `tempfile.mkdtemp()` directories under identical environment pins (`PYTHONHASHSEED=0`, `SOURCE_DATE_EPOCH=1756463424`, `TZ=UTC`, `LC_ALL=C.UTF-8`, single-thread BLAS).
- **Execute the downstream chain verbatim**: canonical MIDI ×2 via c4 `midi_from_json_events.py` (read-only), merge with four structural gates, fluidsynth per-track render ×2, D2 vocals overlay via a SHA-verified htdemucs vocals copy, rc7 Method A mix-match via a per-song sibling reading `scripts/v3_spine/mix_match_operator_section.py` read-only, delivery of A/B WAVs plus full-song reconstruction plus manifest.
- **Measure the M-TEX-1 eight-key perceptual panel** on both required comparisons with the c33 rc7 anchor tripwire.
- **Emit** `data/v3/deliveries/252eb21ce7df7328/cycle21/verdict.json` with `V3_FOCUS_SONG_LANDS_pending_operator`, `blocked_on_operator=true`, three-way `rubric_hash_v2` chain byte-equal, `sub_clause_status.f_restart_from_partial=true`, and a c20 backref SHA to the PARTIAL delivery.
- **Land a twelve-case test suite** at `tests/test_v3_focus_wig_c21.py`.
- **Six named plus two housekeeping ledger events** under the `-clone-1` suffix.

The required output artifact is `docs/v3_focus_wig_restart_c21_report.md`.

## 2. Cycle 1: full PARTIAL→LANDS restart

### 2.1 Anchor preservation on inherited c20 state

The nine frozen c20 SHAs — twelve htdemucs section stem SHAs across two runs (byte-deterministic; six stems ×2 = twelve run-scoped SHAs collapsing to six unique) and three completed MuScriptor JSON SHAs (drums, bass, guitar) — were verified byte-identical pre-versus-post at the start of the cycle. The verdict records this explicitly in the `anchor_preservation_c20_shas` block:

- `htdemucs_section_stems_all_match: true`
- `muscriptor_completed_probes_all_match: true`
- `n_frozen_shas_preserved: 9`

### 2.2 MuScriptor completion (four remaining probes)

The four remaining MuScriptor probes were executed twice into fresh temporary directories under the identical environment pins used at c20, and each pair asserted byte-deterministic. The verdict's `sub_clause_status.b_ii_muscriptor_json_det_x2` is `true`, and the honest-partial-reasons array is empty.

### 2.3 Read-only upstream anchors respected

The chosen-section slice at SHA `3d3776fa6e85ff5f8b594a9d8302d387fb9d325da389247fea9fed952bdfefb9` was used as the deterministic input source for the htdemucs re-hash checks. The six inherited section stems reproduce byte-identically:

| Stem | SHA-256 |
|---|---|
| bass | `4878f22d5187de370a91723c097c62cfa5f830b0f7e56daabcd626fa62a5e047` |
| drums | `4ea5bfb2d442e3f74b460ba4a15d9b799a9053d9b7488d217e9b18406db97e83` |
| guitar | `ea6dbc4d7f4a6e03b591490b9d4b514c22ffe95a174b7f1dae08b863ed96c77a` |
| other | `c51b0872087573e36f16973f1cc313a37745b23f67aa2aa08f1e0fac514d4fb4` |
| piano | `5ed59e93204b4b3b48a05e4353d3d1a5cf7a68b16472e080290fa80c4c682156` |
| vocals | `7ddf6e655ea46e3bdbd4f7e6b61f34090994654fb536d89cf709d601cd83108c` |

Downstream anchors (c4 canonical MIDI serializer, c5 mix-match Method A, c33 render_stem, focus set) were all consumed at their locked SHAs unchanged.

### 2.4 Downstream chain (all sub-clauses PASS)

The pipeline executed the entire downstream chain in a single cycle with every rubric sub-clause satisfied:

| Sub-clause | Value |
|---|---|
| `a_delivery_present_nonsilent` | true |
| `b_i_htdemucs_operator_section_det_x2` | true |
| `b_ii_muscriptor_json_det_x2` | true |
| `b_iii_canonical_midi_det_x2` | true |
| `b_iv_per_track_wav_det_x2` | true |
| `b_v_full_reconstruction_wav_det_x2` | true |
| `c_panel_finite.operator_section_panel_ok` | true |
| `c_panel_finite.root_panel_ok` | true |
| `c_panel_tripwire_holds` | true |
| `d_structural_gates_on_merged_mid.drums_track_on_ch10_nonempty` | true |
| `d_structural_gates_on_merged_mid.bass_median_pitch_lt_55` | true |
| `d_structural_gates_on_merged_mid.zero_notes_on_gm_program_4` | true |
| `d_structural_gates_on_merged_mid.vocals_track_present_symbolic` | true |
| `f_blocked_on_operator` | true |
| `f_restart_from_partial` | true (brief-mandated PARTIAL→LANDS transition rationale) |

The merged.mid landed at SHA `a93f5c2ae16e5cace42b98886f6ce3eae4bb47393bef9d2abe631aadbe526578` with all four structural gates passing.

### 2.5 Deliverables

Under `data/v3/deliveries/252eb21ce7df7328/operator_section/`, matching the c5 Chicken Grease format:

- `original_ab_operator_section.wav` — 30-second original A/B on the operator-chosen section.
- `reconstruction_ab_operator_section.wav` — 30-second reconstruction A/B.
- `full_reconstruction_operator_section.wav` — full-section reconstruction.
- `manifest.json` (SHA `9a8a09d0f553a79f9304da0348fa7f1234a91f76f26f1037079bf40b6c414454`).
- `panel.json` and `panel.tsv` — M-TEX-1 eight-key perceptual panel measurements.

The required output artifact `docs/v3_focus_wig_restart_c21_report.md` (8 219 bytes) landed under `docs/` per the directive.

### 2.6 Verdict

`data/v3/deliveries/252eb21ce7df7328/cycle21/verdict.json` (SHA `95edf6cc741366d5f87e68c8658992830ba41fb7330bdb14b91d94cfedfbfec8`) emitted with:

- `verdict = V3_FOCUS_SONG_LANDS_pending_operator`
- `cycle = 21`, `song_sha16 = 252eb21ce7df7328`, `song_title = "Mura Masa — What If I Go"`, `milestone_id = M-V3-FOCUS-1`
- `blocked_on_operator = true`, `honest_partial_reasons = []` (empty because the restart succeeded end-to-end)
- `clone = "1"`, `fork = "0a1b1dca4f9b"`, `schema_version = 1`
- Chosen section: t = 72.77133786848073 s to t = 102.77133786848073 s (duration 30.0 s exactly).
- Three-way `rubric_hash_v2` chain byte-equal at `c49db5a12e955f26c001165ad6e8f9d191bc26bfd96e24c1b163adc37016451a` (document SHA, `rubric_hash_v2.txt` content, and verdict field all identical; `rubric_hash_v2_three_way_chain_holds: true`).
- c20 backref block pins the PARTIAL predecessor at `bd394c43c6134811257bb9b27539bf95e8d5b4663135d2646b0035f6b0e8ea2b` with the restart rationale recorded verbatim.
- All fifteen sub-clause status entries at `true` (see §2.4).
- Wave-sources block pinning the chosen-section slice SHA, six htdemucs run-1 stem SHAs, and the merged MIDI SHA.
- Delivery paths block pinning the six delivery-side artifacts by absolute path.
- `operator_notes` records the restart method verbatim: "Preserve 12 c20 htdemucs stem SHAs + 3 c20 MuScriptor JSON SHAs byte-identical; run remaining 4 MuScriptor probes (piano/vocals/other/full_mix) ×2 under identical env pins; then execute downstream chain verbatim (canonical MIDI ×2, merge with 4 structural gates, fluidsynth per-track ×2, vocals overlay, rc7 mix-match, deliver, panel). LANDS declaration pending operator ear per FD-6; internal-gate criteria per D-A satisfied."

## 3. Cycles 2 and 3: re-verification and branch termination

Cycles 2 and 3 were re-verification passes. In each cycle the auditor performed live disk-state verification on every claimed anchor, three-way rubric hash chain, c20 backref, verdict enum, `blocked_on_operator` flag, the brief-mandated `sub_clause_status.f_restart_from_partial=true` field, the twelve-case test suite (executed live and returning "Ran 12 tests in 0.101 s — OK" with every test 1–12 green), the required output artifact presence, the merge report at the workspace-fallback path, and the six-file delivery tree. Every check passed at every audit; no CRITICAL or MODERATE findings were introduced across the arc.

Under the `<no-null-cycle-validation>` rule the Cycle 3 auditor issued `COMPLETE` with `[[BRANCH_COMPLETE]]`. Continuing further cycles on this clone would violate the no-null-cycle-validation guidance and the anti-Hold-Pattern invariant; the scope is genuinely exhausted; the three remaining MINOR items (shadow-ledger drift, brief-vs-on-disk rubric-hash discrepancy, sub_clause_status shape asymmetry) are all upstream or root-conductor concerns, not actionable at this clone.

The Cycle 3 auditor's rationale enumerated three separable justifications:

1. **Substantive work is done and byte-deterministic.** Re-running would waste tokens and risk perturbing anchors. Every claimed SHA byte-verifies live (verdict `95edf6cc…9bfec8`, c20 backref `bd394c43…7afa6`, three-way rubric chain `c49db5a1…016451a`); all twelve sub-clauses pass including the brief-mandated `f_restart_from_partial=true`; the twelve-case test suite runs 12/12 green live.
2. **Handoffs are upstream.** The three MINOR items are root-conductor concerns.
3. **Peer scope is orthogonal.** Sibling clone 2 (Chicken Grease palette render) does not authorize cross-lane work; manufacturing another cycle would violate the no-null-cycle-validation guidance.

## 4. Handoffs to the root conductor (log-only, not this clone's work)

**MINOR-1 (shadow-ledger drift, recurring, non-blocking).** Standard c33 harness-clone-namespace-guard auto-suffix pattern; the four housekeeping ledger rows under the `-clone-1` suffix land in the fork's shadow ledger via `AGENT_FORK_ID=0a1b1dca4f9b` and are concatenated into primary `promise_ledger.jsonl` at post-merge reconciliation. The root conductor's post-merge reconciliation script handles this class routinely per the `_infra/fanout-namespace-convention-v2` retroactive-registration precedent.

**MINOR-2 (brief-vs-on-disk rubric-hash discrepancy, upstream drift).** The upstream brief-generator template quoted the c50 M-RECREATE-2 v2 rubric SHA `0e11f704e12c62f8…debe1f`, but the correct v3-spine `rubric_hash_v2` on disk is `c49db5a12e955f26…016451a` (the same chain used by every c4–c20 v3-spine delivery). The worker correctly adapted per Fixed Decision 1 and used the on-disk v3-spine hash; the auditor recommends the root conductor patch the brief-generator template so future v3-focus briefs quote the v3-spine `rubric_hash_v2` rather than the recreate_v2 v1 hash.

**OBSERVATION (sub_clause_status shape asymmetry, not a defect).** The WIG c21 verdict carries `b_i_htdemucs_operator_section_det_x2` only, without a separate `b_i_htdemucs_full_song_det_x2`. This matches the Option A restart-from-PARTIAL scope: the c20-frozen twelve section stem SHAs were preserved verbatim as byte-identical anchors, and full-song htdemucs was explicitly not in the restart scope (only the four deferred MuScriptor probes were the deferred work).

## 5. Merge disposition and campaign-level state

**Merge disposition.** This branch merges as `[[BRANCH_COMPLETE]]`. The required output artifact exists on disk at the required path; every hard anchor is byte-identical pre-versus-post live-verified; the three-way rubric hash chain holds byte-equal; the c20 backref resolves live; the twelve-case test suite runs green live; every rubric sub-clause including the brief-mandated `f_restart_from_partial=true` passes. Merge report is on disk at the workspace-fallback path per this session's harness convention; the root conductor will handle any cross-directory copy to the intended fanout path at merge time.

**M-V3-FOCUS-1 milestone: CLOSED WITH REDUNDANCY.** Four internal-gate accepts on record against the operator's D-A autonomous-completion contract's requirement of three:

| Song | sha16 | Verdict SHA | Status |
|---|---|---|---|
| Chicken Grease | `31a164f845f8e27e` | (c5 delivery, operator-blessed) | **operator-ear-LANDED 2026-09-02** (mandatory, authoritative per FD-6) |
| Rome | `51e433ade2a845e1` | `d2c2d704ce910fde1b8110d07e978de998757a6d4c5564b32b6e272197a7afa6` | internal-gate LANDS_pending_operator (c20 clone-1) |
| Disco A | (per c22 S2) | `28c3392934db6071f926e9a8380569970cfbd4b6fa08fff3551e5d63ec9859b2` | internal-gate LANDS (c21 clone-0) |
| **What If I Go** | `252eb21ce7df7328` | `95edf6cc741366d5f87e68c8658992830ba41fb7330bdb14b91d94cfedfbfec8` | **internal-gate LANDS_pending_operator (this clone, PARTIAL→LANDS restart)** |
| Peach Dream | `88d247468cb6d49f` | (c20 clone-2 Option 3 accept) | PARTIAL terminal (Option 3 accept) |

Any three of {Chicken Grease, Rome, Disco A, WIG} satisfy the operator D-A autonomous-completion contract; the four accepts on record provide redundancy against operator ear falling any single non-mandatory candidate.

**M-V3-CORPUS-1 unblock** remains the root conductor's call on the next cycle, gated on (a) operator confirmation of D-D (the palette-becomes-primary decision, pending on the c21 clone-2 palette-render results) and (b) operator ear on M-V3-FOCUS-1 post-hoc per D-A.

## 6. Conclusions

Clone 1 of fork `0a1b1dca4f9b` executed the c22 S3 imperative cleanly. The WIG per-stem chain restarted from the c20 PARTIAL state exactly as Option A prescribed: nine frozen anchors preserved byte-identical, the four deferred MuScriptor probes completed byte-deterministic ×2 under identical environment pins, the downstream chain executed verbatim (canonical MIDI ×2, merge with all four structural gates passing, fluidsynth per-track ×2, D2 vocals overlay, rc7 Method A mix-match, delivery, panel), and the LANDS_pending_operator verdict emitted with every integrity chain byte-equal and the brief-mandated PARTIAL→LANDS transition rationale prominently recorded. Cycles 2 and 3 re-verified byte-identically and closed the branch under `[[BRANCH_COMPLETE]]` per the `<no-null-cycle-validation>` rule.

WIG now joins Chicken Grease, Rome, and Disco A as the fourth internal-gate accept under M-V3-FOCUS-1, closing the milestone with redundancy against the required threshold of three. The one PARTIAL branch (Peach Dream, closed under the Option 3 accept-terminal precedent) does not block: the campaign has more accepts than it strictly needs to advance. The remaining campaign-level questions — operator D-D on palette-becomes-primary, operator ear on M-V3-FOCUS-1 post-hoc — belong to the root conductor and the operator, not to any in-loop cycle.

## Appendix: Implementation Details

### A.1 Delivered artifacts

Required output artifact: `docs/v3_focus_wig_restart_c21_report.md` (8 219 bytes).

Verdict: `data/v3/deliveries/252eb21ce7df7328/cycle21/verdict.json` (SHA `95edf6cc741366d5f87e68c8658992830ba41fb7330bdb14b91d94cfedfbfec8`).

Delivery-side artifacts under `data/v3/deliveries/252eb21ce7df7328/operator_section/`: `original_ab_operator_section.wav`, `reconstruction_ab_operator_section.wav`, `full_reconstruction_operator_section.wav`, `manifest.json` (SHA `9a8a09d0f553a79f9304da0348fa7f1234a91f76f26f1037079bf40b6c414454`), `panel.json`, `panel.tsv`.

Merge report: `docs/v3_focus_wig_restart_c21_merge_report.md` (2 285 bytes) at workspace-fallback path; root-conductor `cp` to fanout path at merge time.

### A.2 Integrity chains

Three-way rubric-v2 chain: `docs/v3_spine_rubric_v2.md` SHA `c49db5a12e955f26c001165ad6e8f9d191bc26bfd96e24c1b163adc37016451a` == `data/v3_spine/rubric_hash_v2.txt` content == verdict `rubric_hash_v2` field.

c20 backref: `data/v3/deliveries/252eb21ce7df7328/cycle20/verdict.json` SHA `bd394c43c6134811257bb9b27539bf95e8d5b4663135d2646b0035f6b0e8ea2b`, live-verified at emit time and again at each of Cycles 2 and 3.

### A.3 Preserved c20 anchors (byte-identical pre==post)

`anchor_preservation_c20_shas`: `htdemucs_section_stems_all_match: true`; `muscriptor_completed_probes_all_match: true`; `n_frozen_shas_preserved: 9` (six htdemucs section stem SHAs, three completed MuScriptor JSON SHAs for drums, bass, and guitar).

### A.4 Wave sources produced this cycle

`chosen_section_slice_sha256: 3d3776fa6e85ff5f8b594a9d8302d387fb9d325da389247fea9fed952bdfefb9`. Six htdemucs run-1 stem SHAs (bass `4878f22d…`, drums `4ea5bfb2…`, guitar `ea6dbc4d…`, other `c51b0872…`, piano `5ed59e93…`, vocals `7ddf6e65…`). Merged MIDI SHA `a93f5c2ae16e5cace42b98886f6ce3eae4bb47393bef9d2abe631aadbe526578`.

### A.5 Rubric sub-clause status

Every reported sub-clause is `true`: `a_delivery_present_nonsilent`, `b_i_htdemucs_operator_section_det_x2`, `b_ii_muscriptor_json_det_x2`, `b_iii_canonical_midi_det_x2`, `b_iv_per_track_wav_det_x2`, `b_v_full_reconstruction_wav_det_x2`, `c_panel_finite.operator_section_panel_ok`, `c_panel_finite.root_panel_ok`, `c_panel_tripwire_holds`, `d_structural_gates_on_merged_mid.{drums_track_on_ch10_nonempty, bass_median_pitch_lt_55, zero_notes_on_gm_program_4, vocals_track_present_symbolic}`, `f_blocked_on_operator`, `f_restart_from_partial`.

### A.6 Chosen section

t = 72.77133786848073 s to t = 102.77133786848073 s (30.0 s). Source: operator's D1-chosen section from `focus_set_v2.json`.

### A.7 Read-only upstream anchors consumed

c4 canonical MIDI serializer (`scripts/v3_spine/midi_from_json_events.py`); c5 mix-match Method A (`scripts/v3_spine/mix_match_operator_section.py`); c33 render_stem (`scripts/palette_render/render_stem.py`); focus set (`data/recreate_v2/focus_set_v2.json`); c20 clone-0 delivery (backref) at `data/v3/deliveries/252eb21ce7df7328/cycle20/verdict.json` SHA `bd394c43…7afa6`.

### A.8 Test suite

`tests/test_v3_focus_wig_c21.py` with the twelve-case shape; live re-run at Cycle 3 audit returned "Ran 12 tests in 0.101 s — OK" with every test 1–12 green.

### A.9 Environment pins

`PYTHONHASHSEED=0`; `SOURCE_DATE_EPOCH=1756463424`; `TZ=UTC`; `LC_ALL=C.UTF-8`; `OMP_NUM_THREADS=1`, `MKL_NUM_THREADS=1`, `OPENBLAS_NUM_THREADS=1`; interpreter `/usr/bin/python3`; `mido==1.3.3`; SoundFont SHA `74594e8f…1cb0`; MuScriptor model SHA `ac80adbd…7fb97ec`. Identical to c20 pins.

### A.10 Handoffs for root conductor (log-only)

MINOR-1 (shadow-ledger drift, recurring non-blocking): standard c33 harness-clone-namespace-guard auto-suffix pattern; `-clone-1` rows land in fork shadow ledger via `AGENT_FORK_ID=0a1b1dca4f9b`; root-conductor post-merge reconciliation handles routinely per `_infra/fanout-namespace-convention-v2`.

MINOR-2 (brief-vs-on-disk rubric-hash discrepancy, upstream drift): brief-generator quoted `0e11f704…debe1f` (c50 M-RECREATE-2 v2 rubric); on-disk v3-spine `rubric_hash_v2` is `c49db5a1…016451a`; worker correctly adapted per FD-1; root conductor may patch the brief-generator template so future v3-focus briefs quote the v3-spine hash.

OBSERVATION (sub_clause_status shape asymmetry, not a defect): verdict carries `b_i_htdemucs_operator_section_det_x2` only; no separate full-song key. Matches Option A restart-from-PARTIAL scope; full-song htdemucs not in restart scope (only the four deferred MuScriptor probes were the deferred work).

### A.11 M-V3-FOCUS-1 accept summary

Four internal-gate accepts on record against required threshold of three: Chicken Grease (operator-ear-LANDED 2026-09-02, mandatory); Rome c20 clone-1 (`d2c2d704…7afa6`); Disco A c21 clone-0 (`28c33929…9859b2`); WIG c21 clone-1 (`95edf6cc…9bfec8`, this clone). Peach Dream c20 clone-2 PARTIAL terminal (Option 3 accept). Milestone closes with redundancy.

### A.12 Source sessions

| Cycle | Researcher | Worker | Auditor |
|---|---|---|---|
| 1 | c1ef1d74-df14-42ec-9d1b-a257864dd2d8 | 16c17ce4-8b87-4ed2-8728-5dd4ea3f4756 | 8733ff4b-6559-4655-ac20-0e41e4639d7f |
| 2 | cd0472e7-dfab-4048-90c7-0485252b290d | 4e1ab100-0f76-4828-9305-25dcd65c897e | c7bf1829-cff1-4abd-bf29-ef7e9e47d5dd |
| 3 | f363704e-4a07-4d23-a77d-3b30fe28ac61 | 70c95419-dbf6-499b-83a8-a5379c9cf661 | 70ad7a19-dfa8-4555-bf7b-08b45b3ec01a |

### A.13 Fanout metadata

Fork `0a1b1dca4f9b`. Clone 1 of the WIG restart assignment. Merge report expected at `/home/user/music-gen-instance-v3/fork-0a1b1dca4f9b/clone-1/merge_report.md` for parent-conductor pickup; workspace-fallback copy at `docs/v3_focus_wig_restart_c21_merge_report.md`. Sibling clones 0 (Disco A) and 2 (Chicken Grease palette) reported separately.
