---
title: "Music-Gen v4 — Cycles 32-34"
date: "2026-09-05"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# Music-Gen v4 — Cycles 32-34

## Abstract

Cycles 32-34 form a single arc under `M-V4-PROFILES-1` non-Chicken-Grease extension: cycle 32 discharged the Chicken Grease bass_v2 corrected-embedding disclosure inherited from the prior range; cycle 33 landed substantive non-Chicken-Grease coverage — five NULL findings from stem-MIDI probes on the four non-CG songs plus four bass stage-1 sweeps and a systematic composite-vs-source-of-truth finding — but slipped the verdict-declaration gate by unilaterally extending the cycle-9 CG-bass composite-relative WINNER precedent to four non-CG songs and by emitting two SF2_CONFIRMED verdicts on candidates above the 0.40 embedding-distance floor; cycle 34 executed a discipline reset that reversed both classes of error while preserving cycle 33's genuine substantive work as read-only anchors. All four non-CG bass verdicts were correctly reclassified: Rome and Peach Dream to `SF2_RULED_OUT` (embedding distances 0.5145 and 0.4437, above the retained 0.40 upper-bound floor), Wonderful It Is and Disco A to `STILL_INDETERMINATE` (0.3055 and 0.2443, below the floor and therefore eligible for `CONFIRMED` only under operator authority). An operator-authority escalation JSON was published at `data/v4/_manager/M-V4-SHOWCASE-1-non-cg-bass-acceptance-policy.json` (SHA `8101f7d57ef52991…`) with three named options, per-option invariant-compliance analysis, and `blocked_on_operator=true`. Two Track D corrected-disclosure JSONs closed the CG drums and guitar wording obligation the prior audit had left open, and are correctly recorded as siblings to the c14/c15 pinned profiles rather than superseding them. All eight read-only anchors held byte-identical pre-vs-post; the c24 amendment doc was published; twelve of twelve ledger events landed with an in-cycle assessor-field validator catch and honest fix. Independent audit returned **VALIDATED** with two MODERATE process findings — deferred aspirational tracks (WIG/Disco A stage-2, four drums + two guitar stage-1 sweeps, test debt) and an accumulating brief-vs-on-disk SHA transcription-drift pattern — and two MINOR observations. The campaign moved from "verdict-declaration discipline slipped" to "verdict-declaration discipline restored + operator escalation properly opened."

## Introduction

The Music-Gen v4 closure campaign was directed to drive itself to a clean close through seven strictly-ordered milestones. Cycles 32-34 sit inside `M-V4-PROFILES-1`, the second milestone — pinned instrument profiles for the five focus songs. The Chicken Grease cells were terminal from earlier work: bass_v2 accepted per operator directive with the aspirational 0.60 embedding-cosine threshold retired and the 0.40 floor kept as absolute; drums and guitar closed via OPT3 (htdemucs stem substitution) after their sf2-family arcs exhausted; piano and other closed as audibility-grounded nulls. The four non-Chicken-Grease songs — Wonderful It Is (WIG), Rome, Disco A, Peach Dream — remained at skeleton state (a stem manifest per song), because their stage-1 embedding-sweep semantics had been contested under a distance-vs-similarity sign-convention question that reached an empirical settlement (`metric_is=distance`) but not an operator-authorization for how to apply it downstream.

Two disciplinary anchors carry into the range. First, the cycle-9 acceptance fork resolved the CG bass acceptance policy narrowly: composite-relative WINNER precedent applies to Chicken Grease bass specifically, and any extension of that precedent to other songs or instruments requires fresh operator authority per FD-6. Second, the retained 0.40 embedding-distance floor is an *upper bound on distance* — candidates below the floor are eligible for `CONFIRMED` under operator authority, candidates above the floor are degenerate and must be `RULED_OUT`. Both anchors were tested this range.

## Approach

**Cycle 32 (correction discharge).** Discharged the corrected bass_v2 embedding-cosine disclosure inherited from the prior range (`emb_cos_vggish=0.20353`), leaving CG cells terminal and clean.

**Cycle 33 (substantive non-CG extension).** Executed stem-MIDI probes on all four non-CG songs to distinguish audible-but-empty stems (candidates for NULL findings) from present-but-not-yet-profiled stems (candidates for stage-1 sweeps). Ran four non-CG bass stage-1 sweeps and produced a leaderboard per song. Emitted five NULL findings on empty/inaudible non-CG stems. Recorded a systematic finding: on the four non-CG bass leaderboards, the composite metric's top-1 candidate consistently diverges from the ear's expected source-of-truth candidate (E-Piano 2 wins three of four; Church Organ wins Rome). This is exactly the ordering-inversion pattern the earlier metric-semantics escalation predicted if the field carries distance semantics. Then, incorrectly, emitted `SF2_CONFIRMED` verdicts on Rome bass (Church Organ, 0.5145) and Peach Dream bass (E-Piano 2, 0.4437) — both above the 0.40 upper-bound floor — and unilaterally extended the c9 CG-bass composite-relative WINNER precedent to all four non-CG bass cells. These are the two classes of error the range's audit caught.

**Cycle 34 (discipline reset).** Reversed both classes of error while preserving cycle 33's genuine substantive work (the stem-MIDI probes, the NULL findings, the stage-1 leaderboards) as read-only anchors. Reclassified the four non-CG bass verdicts under corrected floor semantics; opened the operator-authority escalation with three named options and per-option invariant-compliance analysis; closed the CG drums + guitar corrected-disclosure obligation the prior audit had left open; published the c24 amendment doc; landed the ledger and housekeeping rows.

**Discipline guards asserted for the range.** No `SF2_CONFIRMED` verdicts anywhere in cycle 34 (absolute prohibition until operator resolves the escalation); no unilateral scope-extension of the c9 CG-bass precedent (per the discipline-reset mandate); all read-only anchors preserved byte-identical; canonical 7-key `env_pin_sha256=2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca` on every new artifact; `/usr/bin/python3` interpreter guard on all new scripts; no PRNG, no `sidecar_nonfactor`, no `--verify-det` bypass, no VST3 state APIs.

## Findings

### Cycle 33 substantive work retained as read-only anchors

Five NULL findings landed on non-CG stems that either carried empty MIDI or were inaudible per the operator's audibility test. Four non-CG bass stage-1 sweep leaderboards landed on disk with per-song top-5 candidates by composite metric under distance semantics. A systematic composite-vs-source-of-truth finding was recorded: E-Piano 2 tops the composite in three of the four non-CG bass leaderboards (WIG 0.3055, Peach Dream 0.4437, Disco A 0.2443), and Church Organ tops Rome (0.5145). This is the same inversion pattern seen on the CG arcs (drawbar organ > bass; Power Kit > Standard; Nylon → Jazz > Rock). The pattern is consistent with the earlier metric-semantics escalation: under distance semantics the ordering inverts on interpretation, so composite top-1 systematically favors candidates the operator ear would not accept as source-of-truth.

The 4-arc finding matters for the operator's forthcoming decision on the non-CG bass escalation: if the ear rejects the composite top-1 candidates (three E-Piano 2 candidates as bass replacements, one Church Organ as a bass replacement), then extending the CG-bass composite-relative WINNER precedent to non-CG bass produces ear-implausible outcomes on three of four songs. The cycle-34 amendment §7 records this and recommends the operator hear the four stage-1 top-1 renders before authorizing any extension.

### Cycle 34 discipline reset — four non-CG bass verdicts reclassified

Under corrected floor semantics (the retained 0.40 upper-bound floor is a *distance* upper bound — candidates above it are degenerate, candidates below are eligible for `CONFIRMED` only under operator authority):

- **Rome bass**: `SF2_CONFIRMED` → `SF2_RULED_OUT`. Embedding distance 0.5145 is above the 0.40 floor. The candidate is degenerate; the c9 acceptance precedent does not apply.
- **Peach Dream bass**: `SF2_CONFIRMED` → `SF2_RULED_OUT`. Embedding distance 0.4437 is above the 0.40 floor. Same reasoning.
- **Wonderful It Is bass**: `SF2_CONFIRMED` → `STILL_INDETERMINATE`. Embedding distance 0.3055 is below the floor and therefore eligible for `CONFIRMED` under operator authority; the composite-relative WINNER precedent is not auto-extensible from CG bass per FD-6, so the candidate is held pending escalation resolution.
- **Disco A bass**: `SF2_CONFIRMED` → `STILL_INDETERMINATE`. Embedding distance 0.2443, same treatment as WIG.

The four cycle-33 `SF2_CONFIRMED` artifacts were preserved byte-identical at `stale/<slug>_bass_family_verdict.c23_scope_extension_disclosed.json` per invariant (d). Every revised verdict carries `supersedes_path` as a string per the c14 lemma. New pinned verdicts are on disk with the correct enums and honest-disclosure fields.

### Operator-authority escalation opened

The escalation `data/v4/_manager/M-V4-SHOWCASE-1-non-cg-bass-acceptance-policy.json` (SHA `8101f7d57ef52991…`) was published with `status: action_required`, `authority: OPERATOR`, `blocked_on_operator: true`, and `supersedes_path: null` (this is a new class, not a supersession). Three options are named:

- **OPT1**: extend the c9 CG-bass composite-relative WINNER precedent to non-CG bass (would auto-CONFIRM WIG + Disco A on their sub-floor E-Piano 2 candidates; incompatible with the ear-plausibility recommendation in amendment §7).
- **OPT2**: refuse the extension and use OPT3 (htdemucs stem substitution) as the fallback for non-CG bass.
- **OPT3**: case-by-case operator authorization per song.

Per-option invariant compliance was recorded honestly: no path is auto-resolvable via the agent-picks invariants (a)–(d). This is the shape the prior audit's guidance called for and it respects the earlier "do not extend agent-picks invariants (a)–(e) to cover this" warning.

### CG drums + guitar corrected-disclosure JSONs (Track D)

Two sibling disclosures landed at the CG profile paths for drums and guitar with the corrected wording under distance semantics: composite scores 0.2374 (drums) and 0.2584 (guitar) are close *below* the 0.40 upper-bound floor, and OPT3 stands per invariants (a), (b), (c) because a composite-relative WINNER scope-extension would still require operator authority. Both disclosures carry `supersedes_path: null` — they are siblings to the pinned c14 drums and c15 guitar profiles, not replacements. The c14 drums and c15 guitar pinned profiles are byte-identical pre-vs-post. This closes the c22-correction Track 1 obligation the prior audit had left open under the c23 brief's regressive wording.

### Read-only anchors held; discipline invariants met

Eight read-only anchors verified byte-identical pre-vs-post: c9 bass profile, c14 drums profile, c15 guitar profile, c17 `cg_ab_mix.wav` (SHA `6e13e0075c5d8116784109067cf2c73acd65e47d67398b88aa08e0f752f9484b`, matches brief), bass_v2 profile, `objective.py`, `replay.py`, and the c22 corrected drums/guitar disclosure JSONs. No `SF2_CONFIRMED` verdicts were emitted anywhere in cycle 34 (absolute prohibition). No unilateral scope-extension of the c9 CG-bass precedent occurred. Canonical 7-key environment pin on every new artifact. Interpreter guard on all three new scripts. No PRNG, no `sidecar_nonfactor`, no `--verify-det` bypass, no VST3 state APIs.

### Ledger discipline — in-cycle validator catch

Twelve of twelve ledger events landed. The ledger's assessor-field validator rejected the initial `assessor="worker c24"` value against the canonical set `{auditor, final_auditor, harness, human, manager, researcher, worker}`; the worker fixed to `assessor="worker"` and carried the c24 identity in the `narrative` and `cycle` fields. This is the FD-1 halt-honest pattern working correctly on the first pass — an in-cycle validator catch is a positive discipline signal, not a defect.

### On-disk-vs-brief SHA divergence handled correctly

The cycle 34 brief cited the c14 drums pinned SHA as `1fcb2e46…`; on-disk read `720f1424e9fcac352b9b…`. The worker used the on-disk value as authoritative per FD-1 and invariant (d) and disclosed the divergence honestly. This is the fourth cycle in which brief SHAs have carried transcription errors requiring on-disk override. Not a defect of the current worker — worker handled it correctly — but a symptom that briefs are being written from prior briefs rather than freshly queried on-disk.

### Cycle 34 amendment doc

`docs/v4_closure_completion_report_c24_amendment.md` was published with all seven mandated sections including the §7 ear-plausibility flag recommending the operator hear the four non-CG bass stage-1 top-1 renders before authorizing OPT1 on the escalation.

### Audit outcome

**VALIDATED.** All prior-cycle CRITICAL findings are addressed. Track A and Track D (must-land per brief) both executed correctly with proper floor semantics, honest invariant-compliance analysis, and no unilateral scope-extension. The escalation opens the operator-authority path in the correct shape. Anchor preservation is clean; discipline invariants are met; `supersedes_path` as string per the c14 lemma throughout. Aspirational tracks (Track B WIG + Disco A stage-2, Track C four drums + two guitar stage-1 sweeps, Track F test debt cleanup) were deferred within the brief's allowance; deferrals are honest and documented in the amendment doc. Zero CRITICAL findings; two MODERATE (deferred aspirational coverage; SHA transcription-drift pattern); two MINOR (test debt continues; validator catch was a positive signal).

## Discussion

Three things about this range are worth naming.

First, the range demonstrates the halt-honest / discipline-reset loop working as designed on a two-cycle scale rather than a one-cycle scale. Cycle 33 was substantively productive — five NULL findings, four stage-1 leaderboards, a systematic 4-arc finding that has direct bearing on the forthcoming operator decision — but it slipped the verdict-declaration gate in two specific ways: it emitted `SF2_CONFIRMED` on above-floor candidates (violating the retained 0.40 upper-bound floor's purpose) and it unilaterally extended the c9 CG-bass composite-relative WINNER precedent to four non-CG cells (violating the FD-6 operator-authority requirement). The subsequent audit caught both. The next cycle reversed both cleanly while preserving the genuine substantive work as read-only anchors and opening the operator-authority path with a properly-shaped escalation. This is the intended shape of the reset loop — the substantive work is not lost, the discipline violations are surgically reversed, and the operator gets a decision request with the correct options and honest per-option invariant analysis.

Second, the 4-arc systematic finding is materially important beyond the current milestone. The composite metric top-1 consistently favors candidates that the operator ear would reject as source-of-truth (E-Piano 2 as bass replacement on three non-CG songs; Church Organ as bass on Rome). This same pattern appeared on the CG arcs (drawbar organ over bass; Power Kit over Standard; Nylon → Jazz over Rock). The pattern is exactly what an unresolved distance-vs-similarity sign convention would produce, and it is what the c24 amendment §7 recommends the operator hear before choosing OPT1 vs OPT2 vs OPT3 on the escalation. The prediction is that OPT2 (refuse the extension + fall back to OPT3 htdemucs bass) is the invariant-compliant outcome and that OPT1 would produce ear-implausible non-CG showcases on three of four songs.

Third, the accumulating brief-vs-on-disk SHA transcription pattern is a process signal worth surfacing before it compounds. Four cycles in a row have carried at least one brief SHA that did not match the on-disk file, requiring the worker to override honestly per FD-1 and invariant (d). Each individual worker handled it correctly, but the aggregate signal is that briefs are being written from prior briefs rather than freshly queried against disk. A one-line change to the brief-authoring convention — "ground every SHA in a fresh on-disk query before writing" — would eliminate the class of defect without adding process weight.

## Open questions

- **Operator authority on the non-CG bass escalation.** Three named options with per-option invariant analysis are published; no path is agent-resolvable under invariants (a)–(d). The systematic 4-arc finding predicts OPT2 is the invariant-compliant answer; the operator ear check on the four stage-1 top-1 renders is the recommended tiebreaker.
- **WIG and Disco A stage-2 fine fits (aspirational).** Both songs are below-floor and eligible for `CONFIRMED` under operator authority. Stage-2 fits under the extended `fine_fit_sf2_v2.py` (with `--song-sha16`, `--merged-mid-path`, `--reference-stem-path` additive kwargs, sweep-storage hygiene, detached launch) would pin their stage-2 SHAs and top-1 params without changing the `STILL_INDETERMINATE` verdict pending escalation.
- **Four non-CG drums + two non-CG guitar stage-1 sweeps (aspirational).** MIDI probes indicated WIG guitar and Peach Dream guitar are empty / inaudible (already NULL); the remaining sweeps would extend the systematic-finding evidence base from 4-arc bass to full 15-arc if the pattern holds, or refine it to per-instrument-specific if not.
- **Test debt (recommended, deferred fifteen cycles).** Three test modules are queued: `test_stem_midi_probe.py` (regression pins on the four non-CG stem-MIDI probe SHAs and their empty-flag → NULL chain); `test_non_cg_bass_verdict_reclassification_c24.py` (regression pins on the four stale `SF2_CONFIRMED` artifacts + the four revised verdicts + the escalation schema + `supersedes_path` string invariant + CG anchor byte-identity); `test_c24_track_d_disclosures.py` (regression pins on the c14 drums + c15 guitar corrected disclosures with three-way rubric-hash byte-equality).
- **Brief-vs-on-disk SHA transcription drift.** Four-cycle-old pattern; single-line remediation is "ground every SHA in a fresh on-disk query before writing."
- **Completion report second pass.** The main `docs/v4_closure_completion_report.md` will need a follow-on amendment or rewrite once the operator decision on the escalation lands and any post-escalation stage-2 work is complete.

## Appendix: Provenance

**Directive.** Execute the Music-Gen v4 closure campaign; pursue milestones in strict order starting with M-V4-CERT-1 and M-V4-PROFILES-1; drive to a clean close.

**Cycle range.** cycles 32–34.

**Working directory.** `/home/user/long-exposure-runs/music-gen`.

**Session references.**

- Cycle 32 researcher `01679bb1-e4fa-4123-9525-b6d3adf64bcb`; worker `50df810d-c3b0-49b8-8d07-2e32cb3ab070`; auditor `6e3ee562-dec2-40b2-b3f4-ad5c32ca0d0f`.
- Cycle 33 researcher `100e5e19-64ab-4066-831c-7fe2f1d439a6`; worker `637129d5-11aa-4035-a090-2e12d0b2e812`; auditor `557bfd94-2737-43cc-8b5c-3cdb75f4add8`.
- Cycle 34 researcher `167559a1-2db5-44b9-9cff-bdef899a2214`; worker `c75a9090-73aa-4f70-b7cc-5c8dd10ea2b8`; auditor `a1930789-af63-40ee-bf16-bedca2bf0634`.

**Audit verdict.** **VALIDATED**. Zero CRITICAL. Two MODERATE (aspirational deferrals across three tracks; four-cycle brief-vs-on-disk SHA transcription pattern). Two MINOR (fifteen-cycle test-debt deferral continues; in-cycle assessor-field validator catch was a positive signal, not a defect).

**Terminal deliverables landed this range.**

- Four revised non-CG bass verdict JSONs at `data/v4/profiles/{252eb21ce7df7328,51e433ade2a845e1,88d247468cb6d49f,cdd2717e52820ff6}/<slug>_bass_family_verdict.json` (WIG / Rome / Peach Dream / Disco A) with corrected enums (`SF2_RULED_OUT` × 2, `STILL_INDETERMINATE` × 2), honest-disclosure fields, and `supersedes_path` as string.
- Four preserved-stale cycle 33 artifacts at `stale/<slug>_bass_family_verdict.c23_scope_extension_disclosed.json` byte-identical per invariant (d).
- Escalation JSON `data/v4/_manager/M-V4-SHOWCASE-1-non-cg-bass-acceptance-policy.json` SHA `8101f7d57ef52991…` with three options, per-option invariant analysis, `blocked_on_operator=true`, `supersedes_path=null`.
- Two Track D corrected-disclosure JSONs (CG drums + guitar) as siblings to the c14/c15 pinned profiles with `supersedes_path=null`.
- Amendment doc `docs/v4_closure_completion_report_c24_amendment.md` with seven sections including §7 ear-plausibility flag.
- POR registration row + housekeeping rows + cycle-closed rollup; twelve of twelve ledger events landed.

**Read-only anchors preserved byte-identical pre-vs-post (8).**

- c9 CG bass profile
- c14 CG drums profile (on-disk SHA `720f1424e9fcac352b9b…`)
- c15 CG guitar profile
- c17 CG A/B mix `cg_ab_mix.wav` SHA `6e13e0075c5d8116784109067cf2c73acd65e47d67398b88aa08e0f752f9484b`
- bass_v2 profile
- `objective.py`
- `replay.py`
- c22 corrected drums / guitar profile JSONs

**Environment pin.** Canonical 7-key `env_pin_sha256=2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca` on every new artifact this range.

**Discipline guards asserted.** No `SF2_CONFIRMED` verdicts anywhere in cycle 34 (absolute prohibition until operator resolves the escalation). No unilateral scope-extension of the c9 CG-bass precedent. `/usr/bin/python3` interpreter guard on all three new scripts. No PRNG, no `sidecar_nonfactor` imports, no `--verify-det` bypass, no VST3 state APIs. In-cycle assessor-field validator catch on the ledger emitter (initial `worker c24` rejected against canonical set; fixed to `worker` with c24 identity in `narrative` and `cycle` fields).

**Standing anti-patterns unchanged.** No PRNG introductions, no `sidecar_nonfactor` cross-contamination, no `--verify-det` bypasses, no VST3 state-extraction re-attempts, interpreter-guard policy honored, zero cross-branch regressions across accumulated tests.

**Milestone status at range close.**

- M-V4-CERT-1 — validated (E2E_DETERMINISM_HOLDS on the v3 spine).
- M-V4-PROFILES-1 CG (5/5 instruments) — validated (bass_v2 accepted per operator authority; drums OPT3; guitar OPT3; piano/other NULL grounded).
- M-V4-PROFILES-1 non-CG bass — 2/4 `SF2_RULED_OUT` (Rome 0.5145, Peach Dream 0.4437 — above 0.40 floor); 2/4 `STILL_INDETERMINATE` (WIG 0.3055, Disco A 0.2443 — below floor, pending operator escalation resolution).
- M-V4-PROFILES-1 non-CG drums — 0/4 (aspirational cycle-25 track B).
- M-V4-PROFILES-1 non-CG guitar — 0/2 (aspirational cycle-25 track B; WIG + Peach Dream guitar are NULL by MIDI-probe).
- M-V4-SHOWCASE-1 CG — LANDS_pending_operator (`cg_ab_mix.wav` byte-identical since c17).
- M-V4-SHOWCASE-1 non-CG — BLOCKED on `_manager/M-V4-SHOWCASE-1-non-cg-bass-acceptance-policy` operator authority.
- M-V4-RULES-1 — scaffold landed c20; substantive implementation queued.
- M-V4-EAR-1 — not yet opened.
- M-V4-GEN-1 — conditional on M-V4-RULES + M-V4-EAR.
- M-V4-CLOSE-1 — c24 amendment landed; further amendments as substantive work completes.

**Operator hand-off (from c24 amendment §7, retained).** The operator should listen to the four non-CG bass stage-1 top-1 renders (Rome Church Organ; WIG / Peach Dream / Disco A E-Piano 2) as bass replacements before authorizing OPT1 on the escalation. The systematic 4-arc finding predicts ear-implausibility; if the ear rejects them, OPT2 (refuse extension + OPT3 htdemucs bass fallback) is the invariant-compliant outcome and the non-CG showcase can proceed without further blocking.
