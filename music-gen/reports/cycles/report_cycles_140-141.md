---
title: "Music-Gen v5 — cycles 140-141"
date: "2026-09-10"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# Music-Gen v5 — cycles 140-141

## Abstract

This report covers the last two working cycles of the Music-Gen v5 reopening: the interpolation demonstration (feature F5) and the closing documentation (feature F7). Both landed, and the v5 arc re-closed.

The interpolation demo blends two donor songs — Chicken Grease (CG) and Peach Dream (PD) — at weight $t = 0.5$ by mixing the *parameters* of two donor-conditioned models (the groove tables and the harmony Markov chain), then sampling one song from the blended model with the generator's existing SHA-256 inverse-CDF draws. No note-level averaging occurs anywhere. The demo was pre-registered before any code was written, rendered as the sixth song of generation iteration 5 (seed 4), and reproduced byte-for-byte three ways: an in-process second render, an independent second process into a fresh temporary directory, and — with the new flag absent — a re-render of iteration 4 that reproduces all five of its earlier audio files. All three pre-registered audibility clauses held on the raw (pre-normalisation) render. Verdict: **F5_LANDS**. One structural caveat is carried forward: the two donors share almost no exact groove contexts, so the groove half of the blend is a union-vocabulary mixture (each conditional row is half a donor row and half a uniform distribution over the other donor's vocabulary), while the harmony half is a genuine mixture on 53 of 81 states.

The closing cycle appended three documents additively — a v5 section in the completion report, operator-decision entry #21, and a v5 layer in the codebase guide — with byte-equality of every pre-existing prefix asserted by test. Four parent milestones rolled up with frozen-enum verdicts (corpus landed with the tempo axis stopped; rules landed with honest gaps; ear restored as informational only; features F1–F5 landed as an honest best-of at stall 5/12), and the close milestone recorded `V5_CLOSE_LANDS` with every clause computed from disk. An independent audit re-rendered both the flag-on and flag-off runs, reproduced every hash, and found no critical or moderate defects apart from one disclosure-class pointer (a validator record split into a sibling file that no ledger event adopts). The audit's decision was COMPLETE: no further cycle is warranted unless the operator reopens.

## 1. Introduction

### 1.1 State at the opening of this range

The v4 closure campaign closed at on-disk cycle 77 and was reopened on 2026-09-06 by operator guidance for a v5 arc (rules, ear, generation). A later operator instruction of 2026-09-09 set the rule that governs this range: *finish the feature set; the ear does not need to be perfect yet.* Feature landings, not the count of songs scoring ≥ 6 on the automated ear, are the gate for progress. The backlog is seven features:

| Feature | Content | Status at range open |
|---|---|---|
| F1 | length + form + arrangement | `FORM_PLAN_PARTIAL` (4/5 at landing) |
| F2 | bass line + melody models with dynamics | `F2_PARTIAL` (RMS-variance clause unmet) |
| F3 | guitar / piano / other comping parts | `F3_LANDS` |
| F4 | tempo fix for Peach Dream and Disco A | CLOSED by operator addendum (tempi adopted) |
| F5 | interpolation demo, two donors, $t = 0.5$ | open — this range |
| F6 | iteration schedule recorded in the stall counter | entries present since iteration 2 |
| F7 | close documents, only after F1–F5 have landed | open — this range |

Four generation iterations had been rendered (seeds 0–3), each with two-fold byte-determinism proofs. The generator image at range open had SHA-256 prefix `3d0f3a24…`; the stall counter stood at 4 iterations of a 12-iteration budget with zero declared passers.

### 1.2 Terms used throughout

- **Donor**: one of five focus songs whose transcribed MIDI conditions the generator (CG = Chicken Grease, WIG = What If I Go, Rome, PD = Peach Dream, Disco A). Songs are identified on disk by a 16-hex prefix of their SHA (CG `31a164f845f8e27e`, PD `88d247468cb6d49f`).
- **n=23 models**: the harmony Markov chain (81 functional chord states, relative to the tonic), the groove model (four conditional tables: kick-8th marginal, snare-16th | kick, hat-16th | kick+snare, bass-16th | kick), and the comping statistics, each fitted on the 23 eligible corpus songs. They drive the regular renders.
- **Pre-registration ("prereg")**: a JSON file written before any code edit or output, fixing the verdict vocabulary, the acceptance clauses with tolerances, and the SHA-256 of every held-constant input. A test asserts that its modification time precedes every output.
- **Frozen enum**: a verdict must be one of the pre-declared values; nothing is retuned after seeing the result (the run's "FD-1" rule).
- **Byte-determinism ×2 / replay proof**: every render is produced twice, the second time into a fresh temporary directory; the audio files must be byte-identical (`REPLAY_PROOF_HOLDS`).
- **Flag-off regression**: after any additive generator edit, the *previous* iteration's exact command is re-run under the new image with the new flag absent; it must reproduce the earlier audio SHAs, proving the edit is inert when off.
- **Informational ear score**: an automated VGGish-based score on a 1–7 scale. Earlier work proved that no monotone calibration of this statistic can both pass its sanity gate and discriminate the target band, so scores are recorded but never declare a passer (rule "FD-6": the operator's ear decides).
- **Stall counter**: the v5 generator budget — 12 iterations, target 5 passers; the counter advanced 4 → 5 in this range.
- **Cycle numbering**: the work is recorded on disk as cycles 89 and 90; the workers labelled them harness cycles 133 and 134 under an assumed offset of 44; this report's range is harness 140–141. The offsets are disclosed, not reconciled. Throughout, "the demo cycle" means on-disk cycle 89 and "the close cycle" means on-disk cycle 90.

## 2. Approach

Both cycles followed the discipline established for F1–F3:

1. Write the pre-registration first (verdict enum, clauses, tolerances, held-constant SHAs, expected output counts).
2. Make the generator edit additive behind a default-off flag whose sub-flags error out without the parent flag.
3. Render; prove byte-determinism ×2; run the flag-off regression against the previous iteration; score informationally; deliver SHA-verified listening copies.
4. Record the verdict mechanically from the enum; advance the stall counter with a schedule entry (F6); adopt tests; register plan rows; emit ledger events with `agent=worker`.

The close cycle rendered nothing. It appended documents additively (a prefix byte-equality test guards each pre-existing file), rolled up the parent milestones with frozen enums, triaged validator warnings, decided a housekeeping question about pipeline runners, and computed the close verdict from disk state rather than asserting it.

## 3. Findings

### 3.1 The F5 pre-registration and blend semantics

The prereg `data/v5/gen/f5_prereg_c89.json` (SHA-256 `fb614843…`) was written at 03:14:04 Z, before the generator edit, the new module, and every one of the 250 files it predicted. It fixes:

**Donors and weight.** A = CG (tonic F♯ minor, 92.285156 BPM from the corpus tempo model), B = PD (at the operator-adopted 122.197271 BPM, served from its re-canonicalised MIDI). $t = 0.5$, fixed by the plan; no sweep.

**What "donor-conditioned model" means.** The n=23 construction (same alphabet, phase alignment, $\alpha = 0.5$ smoothing, template matching, functional states relative to the donor tonic) applied to that donor's *own* lossless canonical MIDI — obtained by read-only import of the existing `groove_v5_v2.load_song/table` and `harmony_v5.analyse_song` functions.

**Groove blend.** For each of the four conditional tables, over the *union* of the two donors' outcome vocabularies:

$$P_{\text{mix}}(o \mid c) = t\,P_A(o \mid c) + (1-t)\,P_B(o \mid c),$$

where $P_X(o \mid c)$ is donor X's smoothed row when context $c$ was seen in X, else uniform over X's vocabulary (the generator's existing `row_for` convention); an outcome absent from a donor's vocabulary contributes 0 from that donor; contexts seen in neither donor fall back to uniform over the union. Sampling is unchanged from iteration 4: inverse-CDF on $u$ = SHA-256 of the same per-bar tags. The n=23 corpus tables are *not* consulted for the demo groove.

**Harmony blend.** Over the n=23 chain's 81 functional states, with $n_X(s)$ = donor X's segment count leaving state $s$:

$$\text{row}_{\text{mix}}(s) = t\,P_A(s,\cdot) + (1-t)\,P_B(s,\cdot), \qquad n_{\text{mix}}(s) = t\,n_A(s) + (1-t)\,n_B(s),$$

where $P_X(s,\cdot)$ is donor X's row-normalised segment transitions if $n_X(s) > 0$, else the n=23 chain's row (a *back-off*, counted and disclosed per state). The blended chain stores $n_{\text{mix}}(s)\cdot\text{row}_{\text{mix}}(s)$ as segment-level counts, so the generator's existing matrix builder recovers the mixed row and the F1 section-contrast rule (≥ 8 segments) reads the blended support. Start weights $\pi_{\text{mix}} = t\,\pi_A + (1-t)\,\pi_B$. The tonic is donor A's (states are functional, so the blend is key-independent; a tonic cannot be averaged).

**Declared deviation.** The research brief had recommended argmax decoding with a tiebreak. The prereg declines it: argmax decoding of a Markov chain collapses to a fixed one-or-two-state cycle and is not a chord progression. Decoding stays the SHA-256 inverse-CDF used by every other v5 chord draw. The prereg governs.

**What is not blended.** Tempo, tonic, instrument profiles, F2 velocity/bass/melody models, and F3 comping are donor A's or the standard n=23 assets. No arithmetic mean of two rendered note streams or of two sampled sequences is performed anywhere (the ban inherited from the v4 interpolation demo).

**Verdict enum and clauses.** `F5_LANDS` iff (demo byte-determinism in-process AND in an independent process) AND replay proof ×2 AND flag-off regression 5/5 AND every audibility clause; `F5_PARTIAL` iff determinism and regression pass but an audibility clause fails; else `F5_FAILS`. The audibility clauses are measured on the *raw* render, before RMS normalisation (closing a prior audit's note that a post-normalisation check is tautological):

- (i) every demo stem's raw render RMS > −60 dBFS;
- (ii) drum density: with $d(t)$ = mean drum onsets per composed bar, $|d(0.5) - \tfrac12(d(1) + d(0))| \le 2.0$, where $d(1)$ and $d(0)$ come from re-composing the same tags with the A-only and B-only tables;
- (iii) chord Hamming distance to each donor-only sequence: $0 < h_A, h_B < 1$ and $|h_A - h_B| \le 0.35$ (distinct from both donors, not lopsided).

### 3.2 Generator wiring and a shared repo-root helper

`scripts/v5/generate_v5.py` was edited additively (SHA `3d0f3a24…` → `94c8ba99…`): `--f5` default off, with sub-flags `--interp-a`, `--interp-b`, `--interp-t`, `--f5-prereg` that raise an argparse error without `--f5`; `--f5` itself requires all four plus `--f2 --f3 --form-plan`. With the flag on, the five regular songs render exactly as before and one demo specification is appended with the blended models. The manifest gains an `f5` block: raw render RMS of every stem, the density and Hamming statistics against A-only and B-only compositions on the same tags (via a new `f5_compose` mirror of the section composition, asserted equal to the demo's own composition), and the blend record.

Two new modules: `scripts/v5/interpolate_v5.py` (190 lines, SHA `177ac5c6…`; imported only under `--f5`; ships a self-check on a synthetic donor pair) and `scripts/v5/repo_root.py` (42 lines, SHA `d012e510…`), a marker walk-up that lets plot scripts under `data/` locate the workspace without a hard-coded `parents[N]` — closing a recurring housekeeping note from earlier audits.

One in-cycle slip was disclosed: the smoke render named the demo `t500` ($t \times 1000$); it was corrected to `t050` ($t \times 100$, the prereg identifier) before the real launch, and the smoke directory was pruned.

### 3.3 Iteration 5: five regular songs and the demo

The iteration-5 command (seed 4; `--f2 --velocity-mode f2 --f3 --tempo-overrides … --f5 --interp-a CG --interp-b PD --interp-t 0.5 --prove-replay`) was launched detached and rendered six songs. Every one has form AABABCAA over 64 bars with the bass-only intro and breakdown at section 2.

| Song | Donor | Tempo (BPM) | Duration (s) | `ab_mix.wav` SHA-256 |
|---|---|---|---|---|
| song 1 | CG | 92.285156 | 173.7099 | `eae40e28…` |
| song 2 | WIG | 99.384014 | 159.6111 | `c9b65ce9…` |
| song 3 | Rome | 151.999081 | 106.0600 | `9d91390a…` |
| song 4 | PD | 122.197271 (adopted) | 130.5527 | `28e18c11…` |
| song 5 | Disco A | 120.272335 (adopted) | 132.6498 | `45f10a8a…` |
| demo `gen_v5_interp_CG_PD_t050` | A = CG, B = PD | 92.285156 (donor A) | 171.4808 | `947b348a…` |

Regular-song feature enums were unchanged from iteration 4: F1 `FORM_PLAN_LANDS` 5/5, F2 `F2_PARTIAL` (the RMS-variance clause was not requested this iteration), F3 per-song clauses 5/5 (every comping part ≥ 32 note-ons and audible; guitar 2090–2305, piano 1500–1770, other 2580–2766 note-ons per song).

**Demo statistics** (from the pinned rollup and byte-determinism record):

| Quantity | Value | Clause |
|---|---|---|
| raw render RMS, dBFS — bass / drums / guitar / keys / melody / other / piano | −31.86 / −30.91 / −21.16 / −23.01 / −30.50 / −18.34 / −24.22 | (i) all > −60: **holds** |
| drum density $d(0.5)$ vs $d(1)$ (A-only), $d(0)$ (B-only) | 11.890625 vs 13.0, 12.0; expected mixture 12.5; deviation 0.609 | (ii) ≤ 2.0: **holds** |
| chord Hamming $h_A$, $h_B$, $|h_A - h_B|$ | 0.9375, 0.8125, 0.125 | (iii) in $(0,1)$ and ≤ 0.35: **holds** |
| bass–kick lock (informational) — mix / A-only / B-only | 0.594 / 0.790 / 0.392 | none |
| tonic | 6 (F♯ minor, donor A) | — |
| F3 parts, note-ons — guitar / piano / other | 2160 / 1644 / 2514 | ≥ 32 each |

One bookkeeping inconsistency is noted, not resolved: the cycle-close narrative in the ledger quotes the demo density as 13.6 per bar "above both donors' 12.4 / 11.6", whereas the pinned rollup, the byte-determinism record and the figure all carry 11.89 vs 13.0 / 12.0. The pinned records are what the tests and the audit checked; the narrative numbers have no on-disk source.

**Blend support** (why the caveat in §4 exists). Groove: each of the four tables has exactly one context seen in both donors (the unconditioned kick marginal); the three conditional tables have 55/14, 73/29 and 55/14 A-only/B-only contexts and zero shared. Vocabulary sizes A/B/union: kick 56/15/70, snare 22/9/30, hat 26/25/49, bass 88/34/121. Harmony: donor A contributed 280 segments and B 164; states with donor support A 41, B 27, blended 53 of 81; n=23 back-off rows used for 12 states on the A side and 26 on the B side; 28 states unseen in both keep the uniform-row convention. The demo's section-contrast rule found only 6 allowed start states for B and C sections (the regular songs have 51–55), a direct consequence of the thinner blended support.

![Iteration 5 (seed 4). Left: comping-part note-on counts for the five regular songs and the demo, all far above the pre-registered minimum of 32 (dashed). Middle: raw, pre-normalisation render RMS of every demo stem against the −60 dBFS audibility floor (clause i). Right: demo drum density (dot) at $t = 0.5$ against the line joining the B-only ($t = 0$) and A-only ($t = 1$) densities, with the ±2.0 onsets/bar tolerance band (clause ii); the title carries the Hamming statistics for clause iii.](data/v5/gen/fig_iter05_parts_c89.png)

### 3.4 Determinism three ways, and the verdict

| Check | Result | Wall time |
|---|---|---|
| In-process replay (`--prove-replay`, second render into a fresh temp dir) | 6/6 `REPLAY_PROOF_HOLDS` | — |
| Independent second process (exact command, fresh `mkdtemp`, `--no-stall-update`) | 6/6 equal on `ab_mix.wav`, every per-stem MIDI, every per-track file, and `f5_blend.json` | 188.1 s |
| Flag-off regression: iteration-4 command (seed 3, no `--f5`) under the post-edit image | 5/5 iteration-4 SHAs reproduced (`a501df3c…`, `fe366926…`, `19b0f51d…`, `99e3ee69…`, `313b98bd…`); iteration-4 files on disk byte-identical | 151.9 s |
| Informational score table, two runs | identical (SHA `e8a39319…`) | — |

With every clause true, the byte-determinism record folded in `f5_enum_final = F5_LANDS`, and the ledger recorded the verdict, discharging both the operator's long-owed "decision #7" (a v5 interpolation demo) and an earlier audit note that F5 needed its own prereg.

### 3.5 Ear scores, stall counter, delivery

Informational scores (VGGish, the c76 "wider-linear" calibration through the isolated venv), all ≥ 6 and all inside the 5.70–6.72 band-4 context range that the earlier infeasibility proof showed the statistic cannot separate:

| CG | WIG | Rome | PD | Disco A | demo |
|---|---|---|---|---|---|
| 6.4615 | 6.4201 | 6.2187 | 6.5625 | 6.4967 | 6.4085 |

No passer was declared. The stall counter advanced to **5/12** with the F6 schedule entry (iteration 5, seed 4, feature "F5 interpolation demo", donors CG/PD, $t = 0.5$, the form / harmony / groove / comping / prereg / blend-record SHAs, verdict F5_LANDS). Listening copies of all six renders went to `data/v4/generated/v5_iter_05/` and the demo trio (audio, manifest, replay proof) plus `f5_blend.json` and a copy of the prereg to `data/v4/generated/f5_interp_CG_PD_t050_c89/`, each SHA-verified by a manifest.

### 3.6 Housekeeping and tests in the demo cycle

- Disk: 86 % used at open; 565 MB of regenerable prior-session render temp directories pruned under `/tmp`; 84 % after; never ≥ 90 %.
- Tests: `tests/test_c89_landing.py` (11/11) — prereg mtime gate and not-future-dated stamp, flag guards, byte-determinism ×2 plus the independent process, F5-off reproduces iteration 4, pre/post generator SHAs, audibility statistics recomputed from the render within the prereg bands, blend record and composition reproduced from a fresh build, expected-output count equal to disk including the figure, discipline scan with no `parents[N]`, stall 5/12 and delivery SHAs, verdict/plan-row consistency, iteration 1–4 audio and read-only pins byte-identical. Generator-SHA pins in the c86–c88 suites were re-pinned to the chain (c88 post-edit == c89 pre-edit), and one stall pin was loosened from `== 4` to `>= 4` because the counter advances by design; both re-pins are commented in place. Adopted suite: 11 files, 84 PASS lines, all exit 0.
- Optional n=25 sibling models (the n=23 set plus the two late-landing songs `0e1e8f20…`, `cc0693b4…`) were skipped for the second time; nothing consumes them.
- Ledger 2138 → 2152 (14 events); plan rows registered; the pipeline runners lived only in the session scratchpad (their commands are pinned in the launch JSON and byte-determinism record) — a gap the close cycle addressed.

### 3.7 The close cycle: three documents appended additively

With F1–F5 landed, the F7 clause of the backlog guidance opened. Three documents were appended, each below its existing content; a test asserts `sha256(current[:pre_bytes]) == pre_sha256` for every file:

| Document | Before → after | What was added |
|---|---|---|
| `docs/v4_completion_report_v3.md` | 20 497 → 54 331 B (`b900b0ee…` → `8341e526…`; first 8 KB and title tag unchanged) | "Section: v5 REOPENING (c79–c90)": cycle-counter and outage disclosure; per-milestone narratives for corpus, rules, ear, generation; the F1–F7 table with landing-cycle verdicts; a 26-row render table; the F5 caveat verbatim; carry-forward hygiene; program coverage; determinism receipts and generator lineage; the validator table; the runners decision; a deliverable index of 109 path/SHA pairs (every one resolving on disk); honest gaps; close rationale |
| `docs/OPERATOR_DECISIONS.md` | 16 147 → 19 655 B | Entry #21 "v5 CLEAN RE-CLOSE at c90": verdict matrix, F1–F7 table, the binding F5 caveat, the ear rule, delegation of the 26 v5 renders and 25 v4 A/Bs to the operator's ear, tempo-axis STOP, re-close wording with no finality claim |
| `docs/CODEBASE_GUIDE.md` | 4 536 → 12 997 B | "v5 REOPENING layer": module map with 21 SHAs, generator flag matrix, `data/v5/` layout, v5-specific disciplines, `blend_record_sha256` semantics |

Every number in the v5 section was read from disk at write time; the audit later re-derived each one from the source JSON (harmony max stationary mass 0.069317, groove singleton-context fraction 0.637448, comping pooled max slot mass 0.065174, melody VOMM order-3 singleton 0.720574, the ear-gate values, the demo gains and raw levels, the F3 note-on counts, all 26 informational scores) and found them consistent, with two prose slips noted in §3.10.

### 3.8 Parent roll-ups and the close verdict

Four parent milestones rolled up with frozen enums, each restating recorded verdicts without re-measuring anything:

| Milestone | Enum | Substance |
|---|---|---|
| corpus | `CORPUS_LANDED_TEMPO_AXIS_STOPPED` | 26 songs transcribed full-length and reindexed lossless with sidecars; the index-collision defect fixed; 1 song content-blocked; four tempo criteria each falsified under its own prereg; PD 122.197271 / Disco A 120.272335 BPM by operator adoption |
| rules | `RULES_LANDED_WITH_HONEST_GAPS` | harmony n=23 non-degenerate; groove overfits (0.637); comping non-degenerate but slot histogram structureless; form model failed its test so a fixed template governs; velocity profiles structureless; melody VOMM memorises (0.72) |
| ear | `EAR_RESTORED_INFORMATIONAL_ONLY` | isolated venv rebuilt and amended; leave-one-out gate 5/5 ≥ 6 (min 6.2095); band-4 spot check fails (6.7199 > 5.7095); monotone-infeasibility proof stands |
| generation | `FEATURES_F1_F5_LANDED_HONEST_BEST_OF_AT_STALL_5_OF_12` | F1 partial, F2 partial, F3 lands, F4 closed by operator, F5 lands; F6 entries complete; stall 5/12, passers 0 by design; a sixth iteration is not opened (it would be preservation-spin) |

The close milestone then recorded **`V5_CLOSE_LANDS`** from a check dictionary computed by the emitter from disk: no anchor drift (44 turn-start pins; the only four that moved were the three appended docs and the plan file), docs prefix byte-equal, v3 first 8 KB unchanged, validator ERROR count at baseline, tests green, no render trees touched. The event's wording makes no finality claim: the run re-closes cleanly; the operator verifies post-close; a later guidance file may reopen exactly as the v5 reopening did.

### 3.9 Validators, the adopt event, and the runners decision

**Validator triage.** The project's promise checker reported 156 errors / 8 960 warnings at open. The 156 errors are all pre-existing (98 events missing an `agent` field from an old emitter chain, 40 unregistered milestone ids, 16 out-of-vocabulary statuses, 2 illegal transitions; zero on any line from these cycles). The warning growth (+253 since the previous cycle) was entirely the "orphan artifact in managed path" class fired on the new iteration-5 tree. Since the emitter can carry ≥ 250 paths, a single adopt event registered the iteration-5 tree, the demo delivery and the listening copies (280 paths) under the generation milestone, reducing warnings to 8 731; after the closing events the count was 8 714, then 8 707 after a byte-exact restore of the frozen record, then 8 708 after the record split described next. The organisation checker stayed at 0 errors / 54 warnings (pre-existing workspace-root files).

The warning series c85 → c90: 8 543, not recorded, not recorded, 8 707, 8 960, 8 960 (open) → 8 731 (after adopt).

**Record split.** `data/v5/logs/validators_c90.json` is quoted by SHA in the completion-report deliverable index, so it was frozen at its after-adopt state and the later `final` / `post_close` phases were written to a sibling `validators_c90_close.json`. No ledger event adopts the sibling; the v5 section still points at the original file's `final` phase. This is the audit's one moderate finding (§3.10).

**Runners decision.** A prior audit had noted that the per-cycle pipeline runners (prune → pins/prereg → smoke → detached launch → independent process → flag-off → score ×2 → deliver → figure → byte-det assembly → tests) existed only in a session scratchpad. Option (a) was chosen: check in `scripts/v5/runners/run_from_launch_json.py` — a generic re-executor that prints (default, dry-run) or launches detached the exact command pinned in any launch JSON or byte-determinism entry, refuses to execute on a drifted generator image or without a fresh `--out`, and reproduces the pinned strings byte-for-byte (asserted by test) — plus a README and verbatim copies of the ten c89 runners under `scripts/v5/runners/c89/` as a historical record. Rationale recorded: every command was already pinned, so the cost is one small module and the benefit is a re-run that needs no retyping and refuses drifted images.

**Other close-cycle housekeeping.** Disk 87 % → 85 % after pruning 596 MB of regenerable render temp directories (this session's and, listed by path and size before deletion, the previous auditor's two re-render directories). `tests/test_c90_close.py` (9/9) plus the c84–c89 suites re-run unchanged: 12 files, 93 PASS lines, all exit 0. Ledger 2152 → 2171 (19 events); plan rows for the close milestones amended additively. The n=25 sibling models were skipped a third time and recorded as an honest gap rather than deferred again.

### 3.10 The independent audit of the close cycle

The auditor verified by execution, not by reading claims: prefix byte-equality and post-SHAs of the three docs; all 109 SHA pairs in the deliverable index and 21 in the module map resolving byte-exactly; all 26 render rows matching their rollups; every quoted number against its source JSON; 40 of 44 turn-start pins byte-identical with the four movers accounted for; the generator unedited; no file under any render tree newer than cycle open; all 19 close-cycle ledger events well-formed with every listed artifact present; validators recomputed at 156 / 8 708 and 0 / 54; 12 test files executed (105 PASS lines, all exit 0); the runner's dry-run reproduced both pinned commands byte-for-byte and refused `--execute` without `--out`. The auditor had independently re-rendered iteration 5 (flag on) and iteration 4 (flag off) in the previous audit, reproducing every SHA.

Findings:

- Critical: none.
- Moderate (one, disclosure-class, deliberately not patched): the validator-record split (§3.9). The minimal fix — an auditor-authored adopt event — would break a test asserting every close-cycle event has `agent=worker` and hence the `tests_green` clause of the close verdict; recorded as a recommendation instead.
- Minor (nine, noted): the v5 section's error-composition prose says "42 unregistered ids + 2 transitions" (sums to 158) where disk shows 40 + 2 (the total 156 is correct and test-asserted); the comping IOI figure "47.5 % at one 16th" is the guitar-stem value, pooled is 44.7 % (qualitative claim unaffected); the close narrative lacks an explicit ledger-count and tests line; the sibling validator file is an orphan (+1 warning); the runner's `created` stamp predates its file mtime (not future-dated); 6 830 orphan-artifact warnings remain, mostly pre-v5 sweep renders; several v5 files show as modified or untracked versus the last commit (commit lag; live SHAs equal the pins); the n=25 siblings were never built; a scratch-archive event names its builder scripts differently from the actual builder.

Decision: **COMPLETE**. The directive's "drive itself to a clean close" was satisfied at cycle 77 and is re-satisfied at cycle 90 after the operator's reopening; the operator's rule makes feature landings the gate, and F1–F5 are all landed with their landing-cycle enums. The residuals are operator-side (listening) or too small for a cycle that would not be a null cycle.

## 4. Discussion

**What the demo demonstrates and what it does not.** The F5 result establishes that the v5 generator can consume a blended model built by a documented, pre-registered rule and produce a deterministic, audible, structurally valid song that differs from both donor-only compositions (Hamming 0.94 and 0.81) while sitting within tolerance of the mixture density. It does not establish that the blend is musically "between" the donors: with zero shared conditional groove contexts, half of every conditional row is uniform noise over the other donor's vocabulary, and the harmony blend leaned on n=23 back-off for a third of its states. Operator-decision entry #21 makes the remedy binding for any follow-up: a $t$-sweep or a second donor pair must first pre-declare shared-context conditioning (coarser contexts) or the per-position SHA-256 fallback used by the v4 demo.

**Determinism held under a fifth generator image.** Iterations 1–5 were produced under successive additive edits (`3fbd98ca` → `b3473fd2` → `f261690c` → `3d0f3a24` → `94c8ba99`), and each edit reproduced the previous iteration with its flag off. The independent-process check added this range removes in-process state as a possible explanation for replay agreement. The environment pin has not changed since on-disk cycle 22.

**Where the small slips live.** The audit's two number slips (error composition, IOI percentage) are both in prose, not in SHA tables; every hash-checked value reproduced. The same pattern shows in the density numbers quoted in the demo cycle's closing narrative versus the pinned rollup (§3.3). The audit's recommendation — generate prose counts from the same JSON the tests read — follows directly.

**Honest gaps carried out of the arc.** The tempo axis stopped after four falsified criteria, so PD and Disco A tempi rest on operator adoption. The groove model overfits, the comping slot histogram is structureless, the form model failed its test, and the melody model memorises. F2's RMS-variance clause remains unmet. Fourteen of fifteen (song, comping-part) cells render through General MIDI shims. The demo's bass and drum normalisation gains hit the 4.0 cap, leaving those stems 1–2 dB under target with no clause governing it. The automated ear cannot discriminate this content; no operator listening verdict exists yet on the 26 v5 renders or the 25 v4 A/Bs.

## 5. Open questions and next steps

No further cycle was scheduled. If the operator reopens:

1. First act: one worker event adopting `data/v5/logs/validators_c90_close.json` and a one-line additive correction that the `final` / `post_close` validator phases live in that sibling file; fold in the two prose corrections (40 unregistered ids, not 42; pooled IOI 44.7 %, guitar stem 47.5 %).
2. Any $t$-sweep or second donor pair must pre-declare shared-context conditioning or the per-position fallback before rendering (binding).
3. The n=25 sibling models remain optional and non-consumed.
4. The 26 v5 listening copies and the demo delivery await the operator's ear; no passer can be declared by the automated score.
5. Commit lag: `generate_v5.py`, `MANIFEST.md`, the velocity-aware serializer and the `scripts/v5/{comping_*, interpolate_v5, repo_root, runners/}` files are uncommitted; live SHAs equal the pinned ones.

## Appendix: Implementation Details

### Code organisation (this range)

```
scripts/v5/
  generate_v5.py            1114 lines  (+--f5 and sub-flags; sha 3d0f3a24... -> 94c8ba99...)
  interpolate_v5.py          190 lines  new (sha 177ac5c6...)
  repo_root.py                42 lines  new (sha d012e510...)
  runners/
    run_from_launch_json.py  110 lines  new (sha 9c6f464e...)
    README.md                           new (sha 10c72355...)
    c89/*.py                 10 files, 413 lines, verbatim copies of the demo-cycle runners
data/v5/gen/
  f5_prereg_c89.json                    sha fb614843...  (03:14:04Z, precedes all outputs)
  byte_determinism_c89.json             sha 476269f3...
  byte_determinism_c90.json             turn-start pins for the close cycle
  gen_v5_iter05_ear_scores_c89.json
  stall_counter.json                    sha 4b87958f...  (5/12)
  plot_iter05_parts_c89.py  83 lines -> fig_iter05_parts_c89.png (sha 2668bed3...)
  iteration_05/                         248 files: 5 regular renders + demo (+ f5_blend.json), rollup sha 4787a346...
data/v4/generated/v5_iter_05/           6 listening copies + listening_manifest.json (sha d8647e7a...)
data/v4/generated/f5_interp_CG_PD_t050_c89/   demo delivery, delivery_manifest.json (sha 7cddb63a...)
data/v5/logs/
  gen_iter05_c89.launch.json, gen_iter05_c89.log, indep_c89.log, flagoff_c89.log, bytedet_c89.log,
  deliver_*_c89.log, score_gen_v5_iter05_c89_run{1,2}.log, c89_prune.json, c90_prune.json,
  validators_c90.json (sha 9f0db6e2...), validators_c90_close.json, runners_decision_c90.json,
  test_results_c89.json, test_results_c90.json
docs/
  v4_completion_report_v3.md   +v5 section (20497 -> 54331 B; 8341e526...)
  OPERATOR_DECISIONS.md        +entry #21 (16147 -> 19655 B; 9599b31e...)
  CODEBASE_GUIDE.md            +v5 layer  (4536 -> 12997 B; 4d08a0b5...)
tools/
  _emit_c89_ledger_events.py 229, _register_c89_por_rows.py 115,
  _emit_c90_ledger_events.py 354, _register_c90_por_rows.py 110
tests/
  test_c89_landing.py 286 lines, 11 tests;  test_c90_close.py 223 lines, 9 tests
```

### Test results

- Demo cycle close: 11 files / 84 PASS lines / all rc 0 (`test_results_c89.json`); `test_c89_landing.py` 11/11.
- Close cycle: 12 files / 93 PASS lines / all rc 0 (`test_results_c90.json`); `test_c90_close.py` 9/9; no re-pins.
- Auditor re-execution (close cycle): 12 files, 105 PASS lines, all rc 0; runner dry-runs byte-for-byte; `--execute` without `--out` refused (rc 3).

### Key hashes

| Item | SHA-256 |
|---|---|
| generator (current) | `94c8ba99eac98eee1f88d871cfc520507ddf253d3962287f50a7a368fdaaa055` |
| F5 prereg | `fb6148435c15b8bbff64dc13e4b3d8cd5501f00ab182b4de757dd9897dd2c16e` |
| demo `ab_mix.wav` | `947b348a10ab8c5c89491cf1a88eeabda680dbbb4f7d8620899a846ec0d7ddb8` |
| blend record (compact canonical JSON) / `f5_blend.json` file bytes | `0bc6f353…` / `72d9cdcd…` |
| blended groove model / blended harmony chain | `dcf0af85…` / `bab58797…` |
| n=23 harmony chain / groove / comping / tempo overrides | `330b9d46…` / `57072025…` / `01024254…` / `ef52f2a0…` |
| env pin (unchanged c22 → c90) | `2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca` |

### Ledger and plan

- Ledger lines 2139–2152: demo cycle (14 events, `cycle=89`): `_plan/guidance-continuation-c89`, `_infra/disk-prune-c89`, `M-V5-GEN-1/f5-prereg-written-c89`, `_infra/f5-wiring-and-repo-root-helper-c89`, `M-V5-GEN-1/f5-iter05-rendered-c89`, `M-V5-GEN-1/f5-flagoff-regression-c89`, `M-V5-GEN-1/f5-verdict-c89`, `M-V5-GEN-1/F5-interpolation-demo`, `M-V5-GEN-1/stall-counter-5of12-c89`, `_infra/n25-siblings-deferred-c89`, `_plan/register-c89-sub-leaves`, `_infra/adopt-cycle89-tests`, `_archive/cycle-89-scratch`, `_run/cycle_89_closed`.
- Ledger lines 2153–2171: close cycle (19 events, `cycle=90`): `_infra/adopt-cycle89-gen-artifacts-c90` (280 paths), `_plan/guidance-continuation-c90`, `_infra/disk-prune-c90`, `_infra/warn-growth-triage-c90`, `_infra/runners-decision-c90`, `M-V5-CLOSE-1/completion-report-v5-section-c90`, `_plan/operator-decisions-c90-amendment`, `_plan/codebase-guide-c90-amendment`, `M-V5-CORPUS-1`, `M-V5-RULES-1`, `M-V5-EAR-1`, `M-V5-GEN-1`, `M-V5-GEN-1/F7-close`, `_infra/n25-siblings-skipped-c90`, `_plan/register-c90-sub-leaves`, `M-V5-CLOSE-1` (= `V5_CLOSE_LANDS`), `_infra/adopt-cycle90-tests`, `_archive/cycle-90-scratch`, `_run/cycle_90_closed` (str-supersedes `_run/cycle_89_closed`).
- Plan of record: F5 row `M-V5-GEN-1/F5-interpolation-demo` amended additively (`c89 LANDED`); `M-V5-CLOSE-1` and `M-V5-GEN-1/F7-close` rows amended additively (`c90 CLOSED`); sub-leaves for both cycles.
- Governing guidance: `guidance_2026-09-09_c131_finish_F2_iter3_then_F3.txt` (sha16 `fed27e550e9f7c75`) and `guidance_2026-09-09_finish_features_backlog_F1-F7.txt` (sha16 `cf7296cfcf70c277`); no new guidance file landed in either cycle.

### Session references

- Cycle 140: researcher `43b6ba46-bc47-4e93-9418-9f0f8431736a`, worker `4bd561b5-200a-43b8-9b6e-ac7c19f31e87`, auditor `9281e1ba-d955-4c05-9410-26cf3b378faa`.
- Cycle 141: researcher `ff7559ca-8996-4869-a5ad-aa534d28cd36`, worker `694cc9a7-cecd-40ea-94aa-fb5e6c46257d`, auditor `ba8588cd-00e8-45ac-a4e6-1b362ca2bd04`.
- Mapping used: cycle 140 ≈ on-disk c89 (workers' label harness c133), cycle 141 ≈ on-disk c90 (harness c134); disclosed, not reconciled.

### Gaps in the record

- Session-history retrieval was not permitted in this reporting session; all material was gathered from disk (ledger, records, docs, logs, tests, figure) plus the supplied close-cycle audit. Researcher briefs and the demo-cycle audit report are not on disk; the demo-cycle audit's findings are known only as folded into the close documents and the close-cycle events (runners gap, prune listing, blend-record hash semantics, inherited degeneracy verdict, 4.0 gain cap).
- `REFERENCES.md` does not exist in the workspace; no References section is emitted.
- The demo-cycle closing narrative's density numbers (13.6 / 12.4 / 11.6) differ from the pinned rollup (11.89 / 13.0 / 12.0); the source of the narrative values was not found.
- `MANIFEST.md` was rewritten for this range (Key Files section preserved verbatim); no git commit was made.
