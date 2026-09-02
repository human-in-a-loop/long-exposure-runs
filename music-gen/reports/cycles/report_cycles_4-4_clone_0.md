---
title: "Music-Gen v3 FOCUS Milestone — Fanout Clone 0: Disco A (Cycle 4, terminal re-verification)"
date: "2026-09-02"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# Music-Gen v3 FOCUS Milestone — Fanout Clone 0: Disco A (Cycle 4, terminal re-verification)

## Abstract

This report covers Cycle 4 of the Disco A fanout-clone branch (fork `0a1b1dca4f9b`, clone 0). Cycles 1 through 3 of the same branch, covered by an earlier report, delivered the full v3 per-stem chain end-to-end on the operator-D1-chosen thirty-second section (t = 21.91963718820862 s to t = 51.91963718820862 s) mirroring the Rome c20 clone-1 pattern verbatim, and closed with a clean VALIDATED audit at Cycle 3. The verdict `V3_FOCUS_SONG_LANDS_pending_operator` at SHA `28c3392934db6071b8a…9859b2` stood as the third M-V3-FOCUS-1 internal-gate accept, closing the operator's D-A autonomous-completion contract's ≥3 gate without depending on the WIG restart or the Peach Dream recovery paths. Cycle 4 was a terminal re-verification pass: the auditor performed live SHA re-verification on every claim from the restored session context, reproduced every SHA in the delivery manifest byte-exact, re-ran the twelve-case test suite green live (12/12 PASS), confirmed the three-way `rubric_hash_v2` chain byte-equal and the Rome c20 backref live-recomputed, and issued `COMPLETE` with `[[BRANCH_COMPLETE]]` under the `<no-null-cycle-validation>` rule. The branch closes cleanly with zero CRITICAL and zero MODERATE findings across the entire arc; three MINOR observations plus one informational OBSERVATION are logged for the root conductor's c22+ post-merge integration.

## 1. Continuity from Cycles 1–3

The Cycles 1–3 report ends with the branch closed under VALIDATED at Cycle 3 after two consecutive re-verification passes. Cycle 4 was a further re-invocation of the same c21-scoped directive against a workspace where the required output artifact and every downstream deliverable already existed byte-identically from Cycle 1's emission. Under the `<no-null-cycle-validation>` rule such a re-invocation cannot receive another VALIDATED — a cycle whose work_output is only invariant checks on already-validated milestone scope must terminate with COMPLETE when scope is genuinely exhausted. Cycle 4 discharges that off-ramp cleanly.

## 2. Cycle 4: prior-session live SHA reproduction and branch closure

The Cycle 4 auditor performed live SHA re-verification on every claim from the restored session context. Every check reproduced byte-exact from the prior VALIDATED audit; no re-execution of the underlying pipeline was needed, and none was performed (re-running would waste tokens and risk perturbing anchors).

**Verdict artifact on disk.** `data/v3/deliveries/cdd2717e52820ff6/cycle21/verdict.json` (SHA `28c3392934db6071b8a…9859b2`) — `verdict = V3_FOCUS_SONG_LANDS_pending_operator`, `blocked_on_operator = true`, all ten sub-clauses TRUE.

**Three-way `rubric_hash_v2` byte-equality chain.** `docs/v3_spine_rubric_v2.md` SHA == `data/v3_spine/rubric_hash_v2.txt` content == `verdict.rubric_hash_v2` field == `c49db5a12e955f26c001165ad6e8f9d191bc26bfd96e24c1b163adc37016451a`.

**Rome c20 backref.** `d2c2d704ce910fde1b8110d07e978de998757a6d4c5564b32b6e272197a7afa6`, byte-equal to on-disk `data/v3/deliveries/51e433ade2a845e1/cycle20/verdict.json`.

**Nine delivery SHA-16 values confirmed.** `original_ab f302ebe8047222d4`, `reconstruction_ab 6b605598ac8ff6ca`, `full_reconstruction 6b605598ac8ff6ca` (identical; the D1 section IS the operator's 30-second window, so the A/B slice equals the full reconstruction — the same shape observed on Rome c20 clone-1, mathematically expected and informationally correct), `merged.mid 7e6f131f07f0d33c`, `manifest.json 18bc3f48beaa7efe`, `panel.json ae3bd61463bc8d47`, `panel.tsv 21745e96b342e317`, `tempo_choice.json e668e7155a65f014`, `rc7_per_stem_loudness_operator_section.json 2c075906299dde8a`.

**Test suite live re-run.** `PYTHONPATH=. /usr/bin/python3 tests/test_v3_focus_disco_a_c21.py` returned 12/12 PASS live — verdict shape, rubric chain, c20 backref, structural gates, byte-determinism ×2, mido version, vocals symbolic, A/B 30-second non-silent, panel eight-key finite, and the anti-pattern-grep hygiene test.

**Cross-branch invariants held byte-identical.** Chicken Grease c5 operator delivery (`cc919559b4508b6b…`); c33 `scripts/palette_render/render_stem.py` (`214372d920a319a9…`); focus set `data/recreate_v2/focus_set_v2.json`. All READ-ONLY anchors preserved.

**Peer disjointness held.** WIG (`252eb21ce7df7328`), Peach Dream (`88d247468cb6d49f`), and Chicken Grease palette (`31a164f845f8e27e/palette_render/`) subtrees all show zero incursions from this clone's writes.

**Hygiene grep (test t12).** Environment pins present in every top-level script; `/usr/bin/python3` guard verified; zero PRNG imports; zero `sidecar_nonfactor` imports; zero VST3 state-extraction attempts (c31/c35 locks held); zero CLAP HF SSL fetch attempts (c11 lock held); zero M-EAR-1 Path A audits under N=55 (c22/c23/c25 locks held); zero c37 pretty_midi merge_partial re-attempts.

Severity classification: 0 CRITICAL, 0 MODERATE, 3 MINOR (all recurring non-blocking precedent classes), 1 informational OBSERVATION.

Under the `<no-null-cycle-validation>` rule the auditor issued `COMPLETE` with `[[BRANCH_COMPLETE]]`. Continuing further cycles on this clone would only re-confirm a closed result and manufacture null cycles on a finished branch. Fanout merge is the next legitimate step, and it is root-conductor territory.

## 3. Merge disposition and open items

**Merge disposition.** This branch merges as `[[BRANCH_COMPLETE]]`. The required output artifact `docs/v3_focus_disco_a_c21_report.md` (10 478 bytes) is on disk; the merge report is on disk at the workspace-root fallback path `merge_report_c21_clone_0_disco_a_fork_0a1b1dca4f9b.md` (4 266 bytes); the intended fanout path `/home/user/music-gen-instance-v3/fork-0a1b1dca4f9b/clone-0/merge_report.md` is outside the workspace sandbox by construction, so the root conductor picks up the fallback and performs the cross-directory copy at merge time.

**M-V3-FOCUS-1 ≥3-accept internal-gate bar CLOSED under operator D-A.** Three internal-gate accepts on record: Chicken Grease (operator-ear-LANDED 2026-09-02, mandatory per FD-6); Rome c20 clone-1 (`d2c2d704…7afa6`); Disco A c21 clone-0 (`28c33929…9859b2`, this branch). Peer c21 branches — WIG PARTIAL→LANDS restart and Chicken Grease palette render — landed sibling merge reports at 2026-09-02T20:38:20 and 2026-09-02T20:06:30 respectively; both are now optional for the gate. WIG's LANDS_pending_operator adds a fourth internal-gate accept for redundancy. Operator ear on the three A/B pairs remains the only authoritative LANDS gate per Fixed Decision 6.

**Handoffs for root conductor c22+ (bookkeeping only; substantive on-disk artifacts already landed):**

1. **Shadow-ledger reconciliation (MINOR-1, recurring non-blocking).** Nine-row shadow-ledger shard (five substantive `M-V3-FOCUS-1/disco-a-*` unsuffixed per c32 plus four infra-family `-clone-0` auto-suffixed) awaits post-merge concat via the c33/c48 auto-suffix concat path. Precedent-consistent with c33, c47, c48, and other c21 branches.
2. **Plan-of-record row registration.** Register six new `M-V3-FOCUS-1/disco-a-*` sub-leaves plus `M-INGEST-1/egress-probe-cycle21-clone-0` plus `_infra/adopt-cycle21-tests-clone-0` plus `_archive/cycle-21-scratch-clone-0` in `plan_of_record.md` to clear post-merge `promise_check` drift.
3. **Brief-generator family-dispatch fix (MINOR-2).** The upstream brief-generator template quoted the c50 M-RECREATE-2 v2 rubric SHA `0e11f704…debe1f` where the correct v3-spine `rubric_hash_v2` is `c49db5a1…016451a` (used by every c4–c20 v3-spine delivery). The worker correctly adapted to on-disk truth per Fixed Decision 1. Structural fix at the brief-generator layer: dispatch the rubric SHA on milestone family — v3-spine `c49db5a1…016451a` for `M-V3-FOCUS-*`; M-RECREATE-2 v2 `0e11f704…debe1f` for `M-RECREATE-2/*`. Eliminates the drift class.
4. **Roll M-V3-FOCUS-1 status.** From `in_progress/medium` to `in_progress/high`. **Do NOT roll to `validated`** — that requires operator ear on the three A/B pairs per FD-6.
5. **c22 scope options.** If operator confirms the c21 clone-2 palette render on ear (D-D), campaign re-renders Disco A + Rome + WIG + Peach Dream under the palette path as secondary deliverables. Alternatively, hold on opening M-V3-CORPUS-1 until operator ear accept on the three A/B pairs.
6. **Panel-cycle-field template hygiene (MINOR-3, cosmetic).** Future clones inheriting the Rome c20 template should refresh `panel.json.cycle` to match the emitting cycle number. Content on this branch is Disco-A-specific and correctly stored under `cycle21/`; no gate is affected.

**OBSERVATION (informational, not a defect).** `reconstruction_ab.wav` SHA equals `full_reconstruction.wav` SHA at `6b605598ac8ff6ca` — mathematically expected because Disco A's D1-auto-picked section IS the operator's 30-second window. Auditor discipline: verify by SHA equality plus duration matching (30.000 s exact = 1 323 000 samples at 44 100 Hz), not by SHA distinctness expectation.

## 4. Conclusions

Cycle 4 of the Disco A fanout clone-0 branch was the terminal re-verification pass. The prior VALIDATED audit at Cycle 3 was reproduced byte-exact from the restored session context; every SHA held; the twelve-case test suite ran 12/12 green live; every cross-branch anchor and peer-clone disjointness invariant held. Under the `<no-null-cycle-validation>` rule the branch closes cleanly with `COMPLETE` and `[[BRANCH_COMPLETE]]`. The M-V3-FOCUS-1 ≥3-accept internal-gate bar closes under operator D-A with Disco A supplying the third accept, and the WIG restart adds a fourth for redundancy. Operator ear on the three A/B pairs remains the only authoritative LANDS gate per FD-6; internal-gate accept is a chain-complete marker, not a substitute.

## Appendix: Implementation Details

### A.1 Delivered artifact status at branch close

Required output artifact: `docs/v3_focus_disco_a_c21_report.md` (10 478 bytes) — present, unchanged since Cycle 1 emission.

Verdict: `data/v3/deliveries/cdd2717e52820ff6/cycle21/verdict.json` (SHA `28c3392934db6071b8a…9859b2`, 9 698 bytes) — present, byte-identical across all four cycles' verifications.

Merge report workspace-root fallback: `merge_report_c21_clone_0_disco_a_fork_0a1b1dca4f9b.md` (4 266 bytes) — present; root-conductor `cp` to `/home/user/music-gen-instance-v3/fork-0a1b1dca4f9b/clone-0/merge_report.md` at merge time.

Delivery-side artifacts under `data/v3/deliveries/cdd2717e52820ff6/`: `original_ab.wav` (SHA-16 `f302ebe8047222d4`), `reconstruction_ab.wav` (`6b605598ac8ff6ca`), `full_reconstruction.wav` (`6b605598ac8ff6caefd5f1ec1444b94c25a52befe94a47d21d1a056747c3ff67`), `manifest.json` (`18bc3f48beaa7efe`), `merged.mid` (`7e6f131f07f0d33c`), `panel.json` (`ae3bd61463bc8d47`), `panel.tsv` (`21745e96b342e317`), `tempo_choice.json` (`e668e7155a65f014`), `rc7_per_stem_loudness_operator_section.json` (`2c075906299dde8a`).

### A.2 Integrity chains reproduced live at Cycle 4

Three-way rubric-v2 chain: doc SHA == `data/v3_spine/rubric_hash_v2.txt` == verdict field == `c49db5a12e955f26c001165ad6e8f9d191bc26bfd96e24c1b163adc37016451a`.

Rome c20 backref: `d2c2d704ce910fde1b8110d07e978de998757a6d4c5564b32b6e272197a7afa6`, live-recomputed against `data/v3/deliveries/51e433ade2a845e1/cycle20/verdict.json`.

Cross-branch READ-ONLY anchors: Chicken Grease c5 operator delivery `cc919559b4508b6b…`; c33 `scripts/palette_render/render_stem.py` `214372d920a319a9…`; focus set `data/recreate_v2/focus_set_v2.json` — all byte-identical.

### A.3 Peer disjointness at Cycle 4

WIG (`252eb21ce7df7328`), Peach Dream (`88d247468cb6d49f`), and Chicken Grease palette (`31a164f845f8e27e/palette_render/`) subtrees show zero incursions from this clone's writes.

### A.4 Test suite live re-run

`PYTHONPATH=. /usr/bin/python3 tests/test_v3_focus_disco_a_c21.py` — 12/12 PASS live. Cases cover verdict shape, rubric chain, c20 backref, all four structural gates, byte-determinism ×2, mido version pin, vocals symbolic, A/B 30-second non-silence, panel eight-key finiteness, hygiene anti-pattern grep.

### A.5 Anti-patterns locked (zero re-attempts on this branch)

VST3 state extraction (c31 STILL_GAP + c35 SPINE); CLAP HF SSL fetch (c11); M-EAR-1 Path A audits under N=55 (c22/c23/c25); c37 pretty_midi merge_partial. All grep-verified by test t12.

### A.6 Handoffs for root conductor c22+ integration

MINOR-1 (shadow-ledger drift, non-blocking): nine-row shadow-ledger shard (5 substantive `M-V3-FOCUS-1/disco-a-*` unsuffixed + 4 infra `-clone-0` auto-suffixed) awaits c33/c48 auto-suffix concat.

MINOR-2 (brief-generator family-dispatch bug): parent brief quoted c50 M-RECREATE-2 v2 rubric SHA where v3-spine hash was required; worker adapted per FD-1; structural fix at brief-generator layer recommended.

MINOR-3 (cosmetic, panel.json cycle-field): `panel.json.cycle` labeled `20` template-mirrored from Rome c20; content Disco-A-specific and correctly stored under `cycle21/`; no gate affected.

OBSERVATION (informational, not a defect): `reconstruction_ab.wav` SHA == `full_reconstruction.wav` SHA at `6b605598ac8ff6ca` — expected shape for D1-30s-window songs (same as Rome c20 clone-1).

Root-conductor integration items: register nine plan-of-record rows to clear promise_check drift; roll M-V3-FOCUS-1 to `in_progress/high` (not `validated` per FD-6); c22 scope options are D-D palette-becomes-primary re-render or hold on M-V3-CORPUS-1 opening until operator ear accept.

### A.7 M-V3-FOCUS-1 accept status at branch close

Three internal-gate accepts on record (closing the ≥3 gate under operator D-A on 2026-09-02):

1. Chicken Grease — operator-ear-LANDED 2026-09-02 (mandatory, authoritative per FD-6).
2. Rome c20 clone-1 — internal-gate accept, verdict SHA `d2c2d704ce910fde1b8110d07e978de998757a6d4c5564b32b6e272197a7afa6`.
3. Disco A c21 clone-0 (this branch) — internal-gate accept, verdict SHA `28c3392934db6071b8a…9859b2`.

Fourth internal-gate accept (redundancy) subsequently landed on WIG c21 clone-1 at `95edf6cc741366d5f87e68c8658992830ba41fb7330bdb14b91d94cfedfbfec8`. Peach Dream c20 clone-2 remains PARTIAL terminal via Option 3 accept. Operator ear on the three A/B pairs remains the only authoritative LANDS gate per FD-6.

### A.8 Environment pins

`PYTHONHASHSEED=0`; `SOURCE_DATE_EPOCH=1756463424`; `TZ=UTC`; `LC_ALL=C.UTF-8`; `OMP_NUM_THREADS=1`, `MKL_NUM_THREADS=1`, `OPENBLAS_NUM_THREADS=1`; interpreter `/usr/bin/python3`; `torch.manual_seed(0)`; `mido==1.3.3`; SoundFont SHA `74594e8f…1cb0`; MuScriptor model SHA `ac80adbd…7fb97ec`.

### A.9 Source session

| Cycle | Researcher | Worker | Auditor |
|---|---|---|---|
| 4 | 4c6f4fd3-585f-4e83-acfd-e0264ea8725d | 39bbe9e0-716c-45ef-ae66-6fc478dcb18a | 4a1f5245-81fd-4fc8-b0b6-919129cee73d |

Cycles 1–3 source sessions are recorded in the Cycles 1–3 report and are not repeated here.

### A.10 Fanout metadata

Fork `0a1b1dca4f9b`. Clone 0 of the Disco A launch assignment. Merge report expected at `/home/user/music-gen-instance-v3/fork-0a1b1dca4f9b/clone-0/merge_report.md` for parent-conductor pickup; workspace-root fallback at `merge_report_c21_clone_0_disco_a_fork_0a1b1dca4f9b.md`. Sibling clones 1 (WIG restart) and 2 (Chicken Grease palette render) reported separately.
