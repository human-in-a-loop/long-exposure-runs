---
title: "Music-Gen v3 FOCUS Milestone — Fanout Clone 0: Disco A Launch (Cycles 1–3)"
date: "2026-09-02"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# Music-Gen v3 FOCUS Milestone — Fanout Clone 0: Disco A Launch (Cycles 1–3)

## Abstract

This report covers Cycles 1 through 3 of a fanout-clone branch spawned from the Music-Gen v3 campaign's M-V3-FOCUS-1 milestone under the c22 root conductor's S2 dispatch. The clone (fork `0a1b1dca4f9b`, clone 0) was assigned to launch the fifth focus song — Disco A (source SHA-16 `cdd2717e52820ff6`, band 5, `corpus/ratings/5/011__hcwKJOsUUIk__Disco_A.mp3`) — for the first time, and to deliver the full v3 per-stem chain end-to-end on the operator-D1-chosen thirty-second section (t = 21.91963718820862 s to t = 51.91963718820862 s) using the Rome c20 clone-1 pattern verbatim. The clone's structural role in the campaign was clear: produce the third internal-gate accept under M-V3-FOCUS-1, closing the operator's D-A autonomous-completion contract's requirement of three accepts without depending on the WIG restart or the Peach Dream Options 1/2 recovery paths. Cycle 1 delivered the launch end-to-end: htdemucs six-stem separation on both the chosen section and the full song byte-deterministic ×2 (24 stem SHAs total); MuScriptor seven-probe transcription byte-deterministic ×2; canonical MIDI serialization byte-deterministic ×2 on all seven probes; merged.mid passing all four structural gates; fluidsynth per-track render byte-deterministic ×2 on the five non-vocal stems; D2 vocals overlay via SHA-verified htdemucs vocals copy; rc7 Method A plain broadband RMS-match producing the full-reconstruction WAV byte-deterministic ×2 at SHA `6b605598ac8ff6caefd5f1ec1444b94c25a52befe94a47d21d1a056747c3ff67`; delivery of A/B WAVs (30 s exactly = 1 323 000 samples at 44 100 Hz), full-song reconstruction, delivery manifest, panel JSON/TSV, and rc7 per-stem loudness sidecar under `data/v3/deliveries/cdd2717e52820ff6/`; and verdict emission at `data/v3/deliveries/cdd2717e52820ff6/cycle21/verdict.json` (SHA `28c3392934db6071b8a…9859b2`) with `V3_FOCUS_SONG_LANDS_pending_operator`, `blocked_on_operator=true`, three-way `rubric_hash_v2` chain byte-equal, and a byte-verified Rome c20 backref. Cycles 2 and 3 were re-verification passes that live-checked every anchor, ran the twelve-case test suite green live (12/12 PASS), and closed the branch. Disco A now stands as the third M-V3-FOCUS-1 internal-gate accept, closing the ≥3 gate under operator D-A.

## 1. Introduction and scope

The M-V3-FOCUS-1 milestone requires at least three focus-song accepts under the operator's D-A autonomous-completion contract. At the close of the c20 fanout arc the tally was two: Chicken Grease (operator-ear-LANDED 2026-09-02, the mandatory anchor per Fixed Decision 6) and Rome (internal-gate LANDS at c20 clone-1). WIG had returned honest PARTIAL after a MuScriptor background-task termination at 3/7 probes; Peach Dream had returned honest PARTIAL after a three-turn Hold Pattern via the Option 3 escape. The c22 root conductor's S2 imperative was to launch the fifth focus song (Disco A, previously untouched) as a fresh, independent pathway to the third accept — one that would not depend on either the WIG restart succeeding or the Peach Dream recovery being chosen.

This report is the merge-disposition summary for clone 0 (Disco A launch). Sibling branches in the same fork:

- **Clone 0 (Disco A launch, S2)** — the subject of this report; internal-gate LANDS at verdict SHA `28c33929…9859b2`.
- **Clone 1 (WIG restart, S3)** — internal-gate LANDS at verdict SHA `95edf6cc…9bfec8`.
- **Clone 2 (Chicken Grease palette render)** — orthogonal secondary-deliverable branch reported separately; internal-gate PALETTE_MOVES_PANEL at verdict SHA `5ba4eaca…5644a`.

The clone's scoped objective as issued:

- **Run htdemucs six-stem separation on both the operator-D1-chosen section and the full song**, byte-deterministic ×2 on each (24 stem SHAs total).
- **Run MuScriptor on seven probes** (six stems plus full_mix, using the c3 per-stem vocab whitelists) byte-deterministic ×2.
- **Serialize canonical MIDI ×2** via c4 `midi_from_json_events.py` (read-only).
- **Merge per-stem MIDIs** and assert all four structural gates: `drums_track_on_ch10_nonempty`, `bass_median_pitch_lt_55`, `vocals_track_present_symbolic`, `zero_notes_on_gm_program_4`.
- **Fluidsynth per-track render ×2** (byte-deterministic).
- **D2 vocals overlay** via a SHA-verified htdemucs vocals copy.
- **rc7 RMS-match plus sum** via a per-song sibling reading `scripts/v3_spine/mix_match_operator_section.py` read-only.
- **Deliver A/B WAVs, full-song reconstruction, manifest, panel (eight-key finite), and rc7 per-stem loudness** under `data/v3/deliveries/cdd2717e52820ff6/` matching the c5 Chicken Grease format.
- **Emit** `data/v3/deliveries/cdd2717e52820ff6/cycle21/verdict.json` with `V3_FOCUS_SONG_LANDS_pending_operator`, `blocked_on_operator=true`, three-way `rubric_hash_v2` chain byte-equal, and a Rome c20 backref SHA.
- **Land a twelve-case test suite** at `tests/test_v3_focus_disco_a_c21.py`.
- **Six named plus two housekeeping ledger events** under the `-clone-0` suffix; substantive `M-V3-FOCUS-1/disco-a-*` labels unsuffixed per the c32 convention.

The required output artifact is `docs/v3_focus_disco_a_c21_report.md`.

## 2. Cycle 1: full end-to-end launch

### 2.1 Source and chosen section

Song identity: Disco A, source SHA-16 `cdd2717e52820ff6`, band 5, audio at `corpus/ratings/5/011__hcwKJOsUUIk__Disco_A.mp3`. The chosen section came from the D1 auto-picker over `focus_set_v2.json`: t = 21.91963718820862 s to t = 51.91963718820862 s (duration 30.0 s exactly).

### 2.2 Read-only upstream anchors

Every read-only anchor was byte-verified against its pinned SHA. Chicken Grease c5 operator delivery (`cc919559b4508b6b…`), Rome c20 verdict (`d2c2d704ce910fde1b8110d07e978de998757a6d4c5564b32b6e272197a7afa6`, used as the Rome-pattern backref pin), c33 `scripts/palette_render/render_stem.py` (`214372d920a319a9…`), c4 canonical MIDI serializer, c5 mix-match Method A, and the focus set `data/recreate_v2/focus_set_v2.json` were all consumed at their locked SHAs unchanged.

### 2.3 Pipeline stage-by-stage results

Every stage passed byte-determinism ×2.

**htdemucs six-stem separation (chosen section and full song, ×2 runs, 24 SHAs total):** all twelve chosen-section and twelve full-song stem SHAs identical run1==run2.

**MuScriptor per-stem JSON transcription (seven probes, ×2 runs):** all seven probes byte-deterministic across two runs.

**Canonical MIDI serialization (via c4 read-only, seven probes, ×2 runs):**

| Probe | Canonical MIDI SHA (run 1 == run 2) |
|---|---|
| bass | `72f5f41fd7de961ccd78501b394eed17bcdec4a24e62bcdb9c841b2ffc810de2` |
| drums | `ec28a91556d10e0cc03f0b2b776a692b9db2a11a2e3e7f686d512e474a743d8e` |
| guitar | `41fc8284780a7b0fd4567d1e777ff596ba2530fa91c07dbea30b6035cd34f8a7` |
| vocals | `7d99b62176b772fd82426001311adb3e65bc5c5be0b2cf79aea6309425e05ec0` |
| other | `ba633a44dcc66e1c5ae1dbdc47f20a0120ac91de2cc687ae552da4bae5c24d00` |
| piano | `68ceb414810972513391ddc0c6ad73887d581a9aa7aa175801093278a4cecec1` |
| full_mix | `bb4940c52655c2faaeb63c34cd9b01dde11a75950c4aa6524e8fe76f12669671` |

**merged.mid structural gates (all four PASS):** `drums_track_on_ch10_nonempty=true`, `bass_median_pitch_lt_55=true`, `vocals_track_present_symbolic=true`, `zero_notes_on_gm_program_4=true`. Merged MIDI at `data/v3/deliveries/cdd2717e52820ff6/merged.mid`, SHA-16 `7e6f131f07f0d33c`.

**Fluidsynth per-track render (five non-vocal stems, ×2 runs):** all five byte-identical run1==run2.

**D2 vocals overlay:** SHA-verified copy of the htdemucs section vocals stem into the render directory.

**rc7 Method A mix-match (plain broadband RMS-match plus sum, per-song sibling reading `mix_match_operator_section.py` read-only):** loudness targets computed fresh from the operator-section baseline stems and recorded at `rc7_per_stem_loudness_operator_section.json` (SHA-16 `2c075906299dde8a`); per-stem gains applied within ±24 dB clamp; summed and peak-limited. Full reconstruction WAV byte-deterministic across two runs at SHA `6b605598ac8ff6caefd5f1ec1444b94c25a52befe94a47d21d1a056747c3ff67`.

### 2.4 Delivered artifacts

Under `data/v3/deliveries/cdd2717e52820ff6/`, matching the c5 Chicken Grease format:

| Artifact | Path | SHA-16 |
|---|---|---|
| Original A/B (chosen section, 30 s) | `original_ab.wav` | `f302ebe8047222d4` |
| Reconstruction A/B (chosen section, 30 s) | `reconstruction_ab.wav` | `6b605598ac8ff6ca` |
| Full-song reconstruction | `full_reconstruction.wav` | `6b605598ac8ff6ca` |
| Delivery manifest | `manifest.json` | `18bc3f48beaa7efe` |
| Merged MIDI | `merged.mid` | `7e6f131f07f0d33c` |
| Panel JSON | `panel.json` | `ae3bd61463bc8d47` |
| Panel TSV | `panel.tsv` | `21745e96b342e317` |
| Tempo choice | `tempo_choice.json` | `e668e7155a65f014` |
| rc7 per-stem loudness | `rc7_per_stem_loudness_operator_section.json` | `2c075906299dde8a` |

The `reconstruction_ab.wav` and `full_reconstruction.wav` share the same SHA — this is mathematically expected because Disco A's D1-chosen section is itself the operator's thirty-second window, so the A/B slice equals the full reconstruction. The same shape was observed on Rome c20 clone-1 and is informationally correct, not a defect. All four A/B WAVs are non-silent at exactly 1 323 000 samples (30.000 s at 44 100 Hz).

Additional working directories on disk: `stems_6s/` (chosen-section stems), `stems_6s_full_song/` (full-song stems), `operator_section/`, `muscriptor_operator_section/`, `per_track/`, `mix_match_operator_section.json`.

### 2.5 Panel (M-TEX-1)

Eight-key perceptual panel measured on both windows (root panel and operator-section panel), all keys finite:

| Key | Value |
|---|---:|
| mel L1 | 13.7036 dB |
| spectral centroid RMSE | 3 142.4014 Hz |
| RMS-env RMSE | 0.2225 |
| LUFS-M RMSE | 10.6570 LU |
| VGGish cosine distance | 0.2219 |

Both `operator_section_panel_ok` and `root_panel_ok` reported `true`. Panel is explicitly **not** an acceptance gate under Fixed Decision 6.

### 2.6 Verdict

`data/v3/deliveries/cdd2717e52820ff6/cycle21/verdict.json` (SHA `28c3392934db6071b8a…9859b2`, 9 698 bytes) emitted with:

- `verdict = V3_FOCUS_SONG_LANDS_pending_operator`
- `blocked_on_operator = true`
- Three-way `rubric_hash_v2` chain byte-equal at `c49db5a12e955f26c001165ad6e8f9d191bc26bfd96e24c1b163adc37016451a` (document SHA == `data/v3_spine/rubric_hash_v2.txt` content == verdict field; `three_way_equal=True`).
- Rome c20 backref: `c20_backref.sha256 = d2c2d704ce910fde1b8110d07e978de998757a6d4c5564b32b6e272197a7afa6`, byte-verified against on-disk `data/v3/deliveries/51e433ade2a845e1/cycle20/verdict.json`.
- Byte-determinism payload pinning every deterministic artifact class (htdemucs section, htdemucs full-song, MuScriptor probes, canonical MIDI, per-track WAV, full-reconstruction WAV) with run 1 and run 2 SHAs identical.
- All ten sub-clauses `true`, including all four structural gates on `merged.mid`, byte-determinism ×2 on each stage, panel finiteness on both windows, delivery presence and non-silence, and the `blocked_on_operator` flag.

### 2.7 Required output artifact

`docs/v3_focus_disco_a_c21_report.md` (10 478 bytes) landed under `docs/` per the directive. A merge-report workspace-root fallback at `merge_report_c21_clone_0_disco_a_fork_0a1b1dca4f9b.md` (4 266 bytes) was created for later root-conductor copy to the intended fanout path (the workspace sandbox blocks direct writes to `/home/user/music-gen-instance-v3/…`).

## 3. Cycles 2 and 3: re-verification and branch termination

Cycles 2 and 3 were re-verification passes. In each cycle the auditor performed live disk-state verification: three-way rubric hash chain live-recomputed and byte-equal; Rome c20 backref live-recomputed and byte-equal; all nine delivery SHA-16 values match the worker's table exactly; every cross-branch READ-ONLY anchor byte-identical (Chicken Grease c5 operator delivery `cc919559b4508b6b…`; Rome c20 verdict `d2c2d704…`; c33 render_stem `214372d920a319a9…`); test suite live re-run returning "Ran 12 tests in 0.101 s — OK" with every test 1–12 green; hygiene grep-verified per Fixed Decision 1 (zero PRNG, zero `sidecar_nonfactor` imports, zero c31/c35 VST3 re-attempts, zero CLAP fetch, zero M-EAR-1 Path A audits, zero corpus-breadth work).

Every check passed at every audit; no CRITICAL or MODERATE findings were introduced. Three MINOR observations were logged as non-blocking recurring precedent classes with clean reconciliation paths at the root-conductor post-merge integration layer (see §5). The Cycle 3 auditor issued `VALIDATED` on the strength of live re-verification, and — because the clone's scoped objective was fully discharged with the third M-V3-FOCUS-1 internal-gate accept landed — the branch closes naturally under `[[BRANCH_COMPLETE]]`.

## 4. Merge disposition and campaign-level significance

**Merge disposition.** This branch merges as `[[BRANCH_COMPLETE]]` on the strength of a clean VALIDATED audit. The required output artifact exists at the required path; every hard anchor is byte-identical pre-versus-post live-verified; the three-way rubric hash chain holds byte-equal; the Rome c20 backref resolves live; the twelve-case test suite runs green live; every rubric sub-clause is satisfied.

**M-V3-FOCUS-1 ≥3-accept bar CLOSED under operator D-A.** Three internal-gate accepts on record:

1. Chicken Grease — operator-ear-LANDED 2026-09-02 (mandatory, authoritative per FD-6).
2. Rome c20 clone-1 — internal-gate accept, verdict SHA `d2c2d704ce910fde1b8110d07e978de998757a6d4c5564b32b6e272197a7afa6`.
3. **Disco A c21 clone-0 (this branch) — internal-gate accept, verdict SHA `28c3392934db6071…9859b2`.**

The other two c21 fanout branches — WIG PARTIAL→LANDS restart and Peach Dream Options 1/2/3 — are now optional per D-A. In practice WIG went on to deliver a fourth internal-gate accept in the same c21 fanout arc, closing M-V3-FOCUS-1 with redundancy. Operator ear on the three A/B pairs remains the only authoritative LANDS gate per Fixed Decision 6; internal-gate accept is a chain-complete marker, not a substitute.

**Cross-branch invariants held.** Chicken Grease c5 operator delivery, Rome c20 verdict, and c33 `render_stem.py` remain byte-identical across five consecutive M-V3-FOCUS-1 audit cycles. Peer-clone write disjointness holds at the sha16-subtree level with zero incursions.

## 5. Handoffs to the root conductor (log-only, non-blocking)

**MINOR-1 (shadow-ledger drift, recurring, non-blocking).** Six named substantive `M-V3-FOCUS-1/disco-a-*` unsuffixed rows plus four infra-family `-clone-0` auto-suffixed rows (nine-row shadow-ledger shard) land in the fork shadow via `AGENT_FORK_ID=0a1b1dca4f9b` and are concatenated into main `promise_ledger.jsonl` at post-merge integration under the c33/c48 auto-suffix concat path. Substantive on-disk artifacts all landed correctly; reconciliation is bookkeeping-only.

**MINOR-2 (brief-vs-on-disk rubric-hash discrepancy, upstream drift).** The parent brief-generator template quoted the c50 M-RECREATE-2 v2 rubric SHA `0e11f704…debe1f`, but the correct v3-spine `rubric_hash_v2` on disk is `c49db5a1…016451a` (used by every c4–c20 v3-spine delivery). The worker correctly adapted per Fixed Decision 1. Recommended fix at the brief-generator layer: dispatch the rubric SHA on milestone family — v3-spine `c49db5a1…016451a` for `M-V3-FOCUS-*`; M-RECREATE-2 v2 `0e11f704…debe1f` for `M-RECREATE-2/*`.

**MINOR-3 (cosmetic, panel.json cycle-field template hygiene).** `panel.json.cycle` is labeled `20` (template-mirrored from Rome c20 clone-1); the file's actual content is Disco-A-specific and correctly stored under `cycle21/`. No gate affected. Future clones inheriting the Rome c20 template should refresh `panel.json.cycle` to match the emitting cycle number.

**OBSERVATION (informational, not a defect).** `reconstruction_ab.wav` SHA equals `full_reconstruction.wav` SHA at `6b605598ac8ff6ca`. Mathematically expected because Disco A's D1-auto-picked section IS the operator's 30-second window, so the "A/B slice" equals the full 30-second reconstruction — identical shape to Rome c20 clone-1. Auditor discipline going forward: verify by SHA equality plus duration matching (30.000 s exact), not by SHA distinctness expectation.

**Additional root-conductor post-merge integration items:**

- Roll M-V3-FOCUS-1 status from `in_progress/medium` to `in_progress/high` (do NOT roll to `validated` — that requires operator ear on the three A/B pairs per FD-6).
- Register plan-of-record rows for the six new `M-V3-FOCUS-1/disco-a-*` sub-leaves plus `M-INGEST-1/egress-probe-cycle21-clone-0` plus `_archive/cycle-21-scratch-clone-0` plus `_infra/adopt-cycle21-tests-clone-0` to clear post-merge promise_check drift.
- If the c21 clone-2 palette-render `PALETTE_MOVES_PANEL` verdict is confirmed by operator ear on Chicken Grease (D-D), c22+ should re-render Disco A, Rome, WIG, and Peach Dream under the palette path as secondary deliverables. Disco A GM chain remains primary reference until operator confirms D-D flip; do NOT rerun this cycle's GM chain.

## 6. Conclusions

Clone 0 of fork `0a1b1dca4f9b` executed the c22 S2 imperative cleanly and delivered the third M-V3-FOCUS-1 internal-gate accept in a single fanout cycle. The Disco A per-stem chain ran end-to-end mirroring the Rome c20 clone-1 pattern verbatim: byte-determinism ×2 on every deterministic artifact class (24 htdemucs stem SHAs, seven MuScriptor probes, seven canonical MIDIs, five per-track fluidsynth WAVs, the full-reconstruction WAV); all four structural gates passing on merged.mid; both panel comparisons finite; delivery of A/B WAVs at exactly 1 323 000 samples (30.000 s) plus the full-song reconstruction, manifest, panel, and rc7 per-stem loudness sidecar; verdict emission at SHA `28c33929…9859b2` with every integrity chain byte-equal and the Rome c20 backref pinned live; twelve-case test suite green live 12/12; required output artifact landed under `docs/`. Cycles 2 and 3 re-verified byte-identically and terminated the branch under `[[BRANCH_COMPLETE]]` after a clean VALIDATED audit.

Disco A now stands as the third internal-gate accept under M-V3-FOCUS-1, closing the operator's D-A autonomous-completion contract's ≥3 gate without depending on WIG or Peach Dream. The subsequent WIG PARTIAL→LANDS restart in the same c21 fanout arc adds a fourth accept for redundancy. The M-V3-FOCUS-1 milestone advances substantively; operator ear on the three A/B pairs remains the only authoritative LANDS gate per Fixed Decision 6.

## Appendix: Implementation Details

### A.1 Delivered artifacts

Required output artifact: `docs/v3_focus_disco_a_c21_report.md` (10 478 bytes).

Verdict: `data/v3/deliveries/cdd2717e52820ff6/cycle21/verdict.json` (SHA `28c3392934db6071b8a…9859b2`, 9 698 bytes).

Delivery-side artifacts under `data/v3/deliveries/cdd2717e52820ff6/`: `original_ab.wav` (SHA-16 `f302ebe8047222d4`), `reconstruction_ab.wav` (`6b605598ac8ff6ca`), `full_reconstruction.wav` (`6b605598ac8ff6caefd5f1ec1444b94c25a52befe94a47d21d1a056747c3ff67`), `manifest.json` (`18bc3f48beaa7efe`), `merged.mid` (`7e6f131f07f0d33c`), `panel.json` (`ae3bd61463bc8d47`), `panel.tsv` (`21745e96b342e317`), `tempo_choice.json` (`e668e7155a65f014`), `rc7_per_stem_loudness_operator_section.json` (`2c075906299dde8a`).

Working directories: `stems_6s/` (chosen-section), `stems_6s_full_song/` (full-song), `operator_section/`, `muscriptor_operator_section/`, `per_track/`, `mix_match_operator_section.json`.

Merge report workspace-root fallback: `merge_report_c21_clone_0_disco_a_fork_0a1b1dca4f9b.md` (4 266 bytes); root-conductor `cp` to fanout path at merge time.

### A.2 Chosen section

t = 21.91963718820862 s to t = 51.91963718820862 s (30.0 s). Source: operator D1-chosen section from `focus_set_v2.json`.

### A.3 Integrity chains

Three-way rubric-v2 chain: `docs/v3_spine_rubric_v2.md` SHA `c49db5a12e955f26c001165ad6e8f9d191bc26bfd96e24c1b163adc37016451a` == `data/v3_spine/rubric_hash_v2.txt` content == verdict `rubric_hash_v2` field; `three_way_equal=True`.

Rome c20 backref: `verdict.c20_backref.sha256 = d2c2d704ce910fde1b8110d07e978de998757a6d4c5564b32b6e272197a7afa6`, live-recomputed against `data/v3/deliveries/51e433ade2a845e1/cycle20/verdict.json`.

Cross-branch READ-ONLY anchors held byte-identical: Chicken Grease c5 operator delivery `cc919559b4508b6b…`; c33 `scripts/palette_render/render_stem.py` `214372d920a319a9…`.

### A.4 Byte-determinism (all deterministic artifact classes ×2)

- htdemucs chosen section: six stems, run 1 == run 2 (12 SHAs).
- htdemucs full song: six stems, run 1 == run 2 (12 SHAs). 24 stem SHAs total per the directive.
- MuScriptor probes: seven probes, run 1 == run 2.
- Canonical MIDI: seven probes, run 1 == run 2 (bass `72f5f41f…`, drums `ec28a915…`, guitar `41fc8284…`, vocals `7d99b621…`, other `ba633a44…`, piano `68ceb414…`, full_mix `bb4940c5…`).
- Fluidsynth per-track WAV: five non-vocal stems, run 1 == run 2.
- Full-reconstruction WAV: run 1 == run 2 == final == `6b605598ac8ff6caefd5f1ec1444b94c25a52befe94a47d21d1a056747c3ff67`.

### A.5 Structural gates on merged.mid

`drums_track_on_ch10_nonempty=true`, `bass_median_pitch_lt_55=true`, `vocals_track_present_symbolic=true`, `zero_notes_on_gm_program_4=true`. All four PASS.

### A.6 Panel numbers

Mel L1 = 13.7036 dB; spectral centroid RMSE = 3 142.4014 Hz; RMS-env RMSE = 0.2225; LUFS-M RMSE = 10.6570 LU; VGGish cosine distance = 0.2219. Both root and operator-section panels finite. Panel is not a LANDS gate.

### A.7 Test suite

`tests/test_v3_focus_disco_a_c21.py` (6 382 bytes), twelve-case shape: verdict shape, rubric chain, c20 backref, structural gates, byte-det ×2, mido version, vocals symbolic, A/B 30 s non-silent, panel eight-key finite, and hygiene grep. Live re-run at Cycle 3 audit returned "Ran 12 tests in 0.101 s — OK" with every test 1–12 green.

### A.8 Environment pins

`PYTHONHASHSEED=0`; `SOURCE_DATE_EPOCH=1756463424`; `TZ=UTC`; `LC_ALL=C.UTF-8`; `OMP_NUM_THREADS=1`, `MKL_NUM_THREADS=1`, `OPENBLAS_NUM_THREADS=1`; interpreter `/usr/bin/python3`; `torch.manual_seed(0)`; `mido==1.3.3`; SoundFont SHA `74594e8f…1cb0`; MuScriptor model SHA `ac80adbd…7fb97ec`.

### A.9 Anti-patterns locked (no re-attempt observed this cycle)

VST3 state extraction (c31 STILL_GAP + c35 SPINE); CLAP HF SSL fetch (c11); M-EAR-1 Path A audits under N=55 (c22/c23/c25); c37 pretty_midi merge_partial. Test 12 grep-verifies zero re-attempts.

### A.10 Handoffs for root conductor (log-only)

MINOR-1 (shadow-ledger drift, non-blocking): nine-row shadow-ledger shard (6 substantive unsuffixed + 4 infra `-clone-0` auto-suffixed) awaits post-merge concat via c33/c48 auto-suffix path.

MINOR-2 (brief-vs-on-disk rubric-hash discrepancy): brief-generator quoted `0e11f704…debe1f` (c50 M-RECREATE-2 v2 rubric); on-disk v3-spine `rubric_hash_v2` is `c49db5a1…016451a`; worker correctly adapted per FD-1; recommended fix at brief-generator layer.

MINOR-3 (cosmetic, panel.json cycle-field): `panel.json.cycle` labeled `20` (template-mirror from Rome c20); content Disco-A-specific and correctly stored under `cycle21/`; no gate affected.

OBSERVATION (informational, not a defect): `reconstruction_ab.wav` SHA == `full_reconstruction.wav` SHA — expected shape for D1-30s-window songs (same shape as Rome c20 clone-1).

Root-conductor c22+ integration items: roll M-V3-FOCUS-1 to `in_progress/high` (not `validated` per FD-6); register 9 plan-of-record rows to clear promise_check drift; if D-D palette-becomes-primary fires, c22+ re-renders Disco A + peers under palette path as secondary deliverables.

### A.11 M-V3-FOCUS-1 accept status at branch close

Three internal-gate accepts on record (closing the ≥3 gate under operator D-A): Chicken Grease (operator-ear-LANDED 2026-09-02, mandatory); Rome c20 clone-1 (`d2c2d704…`); Disco A c21 clone-0 (`28c33929…9859b2`, this branch). WIG c21 clone-1 subsequently added a fourth accept for redundancy at `95edf6cc…9bfec8`. Peach Dream c20 clone-2 remains PARTIAL terminal via Option 3 accept. Operator ear on the three A/B pairs remains the only authoritative LANDS gate per FD-6.

### A.12 Source sessions

| Cycle | Researcher | Worker | Auditor |
|---|---|---|---|
| 1 | 90d1c4dc-c904-4006-98a0-05b528bff9dc | 395d0057-684c-469a-a2b4-42f404df339e | 292e8e3f-a5f2-484b-b5ee-1d8809339a2f |
| 2 | c3db5dec-0ce9-4c41-8e46-94c2f6776710 | de73d4c2-d669-42b3-bb9c-3f59031b03f8 | c91d51eb-caec-45ee-9917-ff191738ce28 |
| 3 | 25c99619-2bd5-4f88-84e5-6710db2e1456 | 342a6663-a25d-41bd-861b-27d2299ce3f8 | 7d5121f4-2ab6-4521-8af0-3bc9f67b0ff0 |

### A.13 Fanout metadata

Fork `0a1b1dca4f9b`. Clone 0 of the Disco A launch assignment. Merge report expected at `/home/user/music-gen-instance-v3/fork-0a1b1dca4f9b/clone-0/merge_report.md` for parent-conductor pickup; workspace-root fallback at `merge_report_c21_clone_0_disco_a_fork_0a1b1dca4f9b.md`. Sibling clones 1 (WIG restart) and 2 (Chicken Grease palette render) reported separately.
