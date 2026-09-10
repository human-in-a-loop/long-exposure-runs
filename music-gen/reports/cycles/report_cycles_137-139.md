---
title: "Music-Gen v5 — cycles 137-139"
date: "2026-09-10"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# Music-Gen v5 — cycles 137-139

## Abstract

This range completed two items of the operator's seven-feature backlog for the v5 generator and closed the bookkeeping on a third. Iteration 3 was rendered with the F2 dynamics models (per-onset velocities extracted from separated stem audio, a chord-conditioned bass pitch model, and a variable-order Markov melody model): all five focus songs render reproducibly with velocities present, but the pre-registered dynamics test — a ≥ 1.5× increase in short-window loudness variance over a uniform-velocity twin on every stem — passed on 0/5 songs, with the drum stem ratio below 1.0 on all five. The outcome was recorded as F2_PARTIAL and, per the operator's standing "record, don't retune" rule, nothing was adjusted. The drum-velocity profiles were shown to be structureless on a pooled accent diagnostic (backbeat minus off-beat −1.9 velocity units against a +10 expectation), which is consistent with the failed dynamics test.

F3 — guitar, piano and "other" comping parts — landed in two steps. First, comping statistics were extracted from the 23-song eligible corpus under a pre-registered non-degeneracy rule (COMPING_NON_DEGENERATE: 23/23 songs contribute ≥ 16 bars; pooled 16th-slot mass max 0.065 ≪ 0.5), with the disclosure that the slot histogram is near-uniform and carries little metrical evidence, whereas the inter-onset-interval histogram is strongly structured (47.5 % of guitar IOIs are one 16th). A standalone comping builder was written against the IOI histogram. Second, a `--f3` flag (default off) was wired into the generator and iteration 4 rendered: guitar/piano/other parts present on 5/5 songs (1,482–2,664 note-ons each), audible (raw render −19 to −23 dBFS against a −60 dBFS floor), replay-proven twice, and — the regression clause — the same generator with the flag off reproduces the iteration-3 and iteration-2 audio byte-for-byte. Verdict F3_LANDS. Iteration 4 is also the first render to consume the 23-song harmony chain and the operator-adopted tempos for Peach Dream (122.197 BPM) and Disco A (120.272 BPM), closing the last loose end of the F4 tempo fix.

Independent audit re-rendered both iteration 4 (flag on) and iteration 3 (flag off) from a fresh process and reproduced all ten audio SHAs; verdict VALIDATED, no critical or moderate findings, and confirmation to proceed to F5 (the interpolation demo). Informational ear scores rose to ≥ 6 on 5/5 songs for the first time (mean 6.43), though by standing policy no "passer" is declared from them. The iteration budget stands at 4 of 12 used.

## Introduction

### Where the work stood at the start of the range

The v4 campaign closed earlier in this run; the current arc is the v5 "reopening", which transcribes the 26-song corpus in full, extracts rules (harmony, groove, form, dynamics, comping) under a pre-registration discipline, and drives a groove-first generator through a budget of twelve feature iterations. The previous report covered on-disk cycles 84–86, ending with: the F1 form/arrangement feature landed (iteration 2); the F4 tempo dispute for Peach Dream (PD) and Disco A resolved by operator authority, with the corpus re-serialised at the adopted tempos and the harmony/groove rules re-run on 23 songs; and the F2 dynamics code written, velocities extracted, but iteration 3 not yet rendered.

An operator guidance note dated 2026-09-09 governed both cycles of this range. It instructed: finish F2 in the first twenty minutes by consuming the already-extracted velocities as-is and running the drafted iteration-3 pipeline; accept the cross-cycle mismatch of separated-stem SHAs against the earlier cache with a single disclosure line and no memo; then start F3, with any unfinished part landing as a flag-off (dormant) code path. A second, older guidance note ("finish the feature set; the ear does not need to be perfect yet") set the frame: each cycle lands one feature (code + test + a rendered five-song iteration), the ear score is informational only, and determinism rules are unchanged.

### Terms used throughout

- **Focus songs.** The five songs every iteration renders, each with a corpus donor: Chicken Grease (CG, donor `31a164…`), Wagon Wheel / "WIG" (`252eb2…`), Rome (`51e433…`), Peach Dream (PD, `88d247…`) and Disco A (`cdd271…`).
- **Eligible set n=23.** The 23 corpus songs used for rules extraction: the 21 songs eligible at cycle 84 plus PD and Disco A, admitted once their tempos were adopted. Two songs that landed late (`0e1e8f…`, `cc0693…`) are deliberately deferred so that every n=23-vs-n=21 difference is attributable to the tempo fix; the "n=25" follow-up is the one-command re-run that would add them.
- **Pre-registration.** Before any output of a feature is produced, a JSON file states the hypotheses, thresholds, clauses and a frozen verdict enumeration; its modification time must precede every output file, and a test asserts this. The standing rule (FD-1) is that a failing clause is recorded, never retuned after seeing the data.
- **Replay proof / byte determinism.** Every rendered song is generated twice in fresh temporary directories; the proof "holds" when the two WAV SHA-256 digests match the on-disk file. Random draws use SHA-256 inverse-CDF sampling (no pseudo-random-number generator), so a given seed is reproducible across processes.
- **Flag-off regression.** Each new generator feature is behind a default-off flag; the edited generator, run without the new flag, must reproduce the previous iteration's WAVs byte-for-byte. This is the mechanism that keeps the generator "image" (script SHA) auditable across iterations.
- **Ear score.** A VGGish-embedding similarity score on a 1–7-style scale, calibrated earlier in the run. It is informational only: a proof earlier in the run showed the intended passer criterion is infeasible under this backbone, so no song is declared a passer from it (rule FD-6).
- **Stall counter.** The iteration budget: 12 feature iterations, target of 5 passers. It also records, per iteration, what varied (feature, seed, donor map, rule SHAs) — the F6 "iteration schedule" feature.
- **GM shim.** A General MIDI program number used to render a part when no donor-specific pinned instrument profile exists.

## Approach

### Cycle plan

The first cycle of the range (on-disk cycle 87) followed the guidance literally: a detached iteration-3 render was launched at turn start; the three "early" ledger records (guidance adoption, F2 route decision, F4 closure) were emitted while it ran; cheap fixes were applied before the launch so that recorded script SHAs would be final; then the remaining time went to F3 comping statistics and a standalone comping builder. The second cycle (cycle 88) pruned disk, amended a stale plan-of-record row, pre-registered F3, wired `--f3` into the generator, rendered iteration 4, and ran the flag-off regressions.

### Generator flags landed this range

The generator `scripts/v5/generate_v5.py` was edited additively twice.

- Cycle 87 (image `f261690c…`, unchanged from the iteration-3 render): a one-line argparse error when `--velocity-mode f2` or `--rms-variance-test` is passed without `--f2`. Flag-off output was unchanged (iteration 1 and 2 SHAs reproduced).
- Cycle 88 (image `f261690c…` → `3d0f3a24…`): `--f3` (default off) importing the read-only cycle-87 builder; `--comping-model` as a sub-flag rejected without `--f3`; an independent `--tempo-overrides <json>` that the donor-tempo lookup consults first (absent on every flag-off run, so earlier iterations still see the frozen anchors); and `--harmony-prereg` / `--groove-prereg` pin-path arguments defaulting to the cycle-84 preregistration files.

### The F2 dynamics test

Pre-registered in the previous range, the test renders each song twice — once with the F2 velocities and once as a "uniform twin" with every velocity set to 100 — and compares, per stem, the variance of 50 ms frame RMS over active frames (above −60 dBFS). Clause (c) requires the ratio F2/uniform ≥ 1.5 on every stem of every song. The enumeration is F2_LANDS (all three clauses on 5/5), F2_PARTIAL (velocities present and replay holds but the variance clause fails), F2_FAILS.

### The F3 comping statistics and builder

`scripts/v5/comping_v5.py` reads the guitar, piano and other stems of each eligible song (PD and Disco A from the re-serialised `canonical_v5c_reindexed/` directories at the adopted tempos) and computes, per stem class and pooled: onset density (note starts and 30 ms onset groups per bar), a 16-slot-per-bar onset histogram, an inter-onset-interval (IOI) histogram in 16ths clipped to 1..16, mean chord size (simultaneous starts within 30 ms), and a sustain ratio (mean paired note duration in beats). The pre-registered rule: COMPING_NON_DEGENERATE iff ≥ 8 songs contribute ≥ 16 pooled bars and the pooled 16th-slot maximum mass is < 0.5.

`scripts/v5/comping_gen_v5.py` builds a comping part for one stem class over a chord sequence: within each bar it walks forward by IOIs sampled (SHA-256 inverse-CDF) from that stem's IOI histogram, places a voicing of round(mean chord size) chord tones (capped at 6) above a per-part register floor (guitar 52, piano 60, other 48), with duration min(sustain, IOI); bars whose chord is `N` (no chord) rest; velocities come from the F2 keys-by-slot ladder. Its events serialise byte-identically through both the original and the velocity-aware MIDI serializers.

### The F3 pre-registration

`data/v5/gen/f3_prereg_c88.json` (written 02:20:50Z, before all 208 iteration-4 files) fixes: the part definitions above; the program policy — use a donor's pinned `<part>.json` profile if one exists (only CG `guitar.json`, program 28, does), else GM shims guitar 27 / piano 0 / other 89, enumerated per song (14 of 15 song×part cells are shims); the mute mask — new parts follow the keys stem's mute mask from the F1 arrangement; per-song clauses (≥ 32 note-ons per part, part audible above −60 dBFS on the normalised track, replay ×2); the iteration clause (F3-off reproduces iteration 3 on 5/5); the frozen enumeration F3_LANDS / F3_PARTIAL (per-song clauses on ≥ 3/5, or 5/5 with the flag-off clause failing) / F3_FAILS; and a held-constant list (n=23 harmony and groove models, form plan, velocity profiles, bass and melody models, serializers, environment pin, donors, soundfont, seed 3 = iteration − 1).

## Findings

### F4 tempo fix: bookkeeping closed

The operator's adoption of PD = 122.197271 BPM and Disco A = 120.272335 BPM was already on disk from the previous range; this range ledgered it (replacing the earlier "half/double ambiguous" verdict path, which remains on disk untouched) and, in cycle 88, amended the plan-of-record row that still described the pre-resolution "must not consume" state. The amendment is additive: the original wording is preserved verbatim and a `c86 RESOLVED` clause is appended; a test asserts both. Iteration 4 is the first render in which PD and Disco A use the adopted tempos rather than the frozen anchors, which closes the last item the earlier audit had left open. The tempo *criterion* axis remains stopped — F4 was resolved by operator authority, not by a passing criterion.

### F2 dynamics: iteration 3 rendered, F2_PARTIAL

Iteration 3 (seed 2, form plan on, `--f2 --velocity-mode f2 --rms-variance-test --prove-replay`, 21-song rules by design) rendered in 170.5 s under generator image `f261690c…`. All five songs hold their replay proof; forms are AABABCAA throughout; durations 168.6 / 156.8 / 103.2 / 127.8 / 130.0 s. Velocities are present on every stem (for CG: bass 63 distinct values over 298 notes, drums 76 over 609, keys 21 over 191, melody 70 over 323; range 36–114).

The variance clause failed on every song. Ratios F2/uniform per stem:

| song | bass | drums | keys | melody |
|---|---|---|---|---|
| CG | 1.76 | 0.98 | 1.49 | 1.31 |
| WIG | 1.55 | 0.94 | 1.24 | 1.46 |
| Rome | 1.49 | 1.10 | 2.23 | 2.66 |
| PD | 1.06 | 1.09 | 1.80 | 2.49 |
| Disco A | 1.77 | 1.20 | 1.52 | 2.87 |

Bass passes on 4/5 and keys/melody on some songs, but drums are ≤ 1.2 everywhere (below 1.0 on two songs): the F2 drum velocities do not add frame-level dynamics over the uniform twin. Verdict F2_PARTIAL; nothing retuned.

![Iteration 3 per-stem frame-RMS variance, uniform-velocity twin (hollow) vs F2 render (filled), and the F2/uniform ratio against the 1.5 gate. Drums sit near ratio 1 on every song.](data/v5/gen/iteration_03/fig_iter03_velocity_c86.png)

Four disclosures accompany this result, each recorded as a one-line ledger entry:

1. **Velocity profiles are structureless.** On the pooled drum accent diagnostic, backbeat (slots 4 and 12) minus off-beat velocity is −1.894 (expectation ≥ +10); the slot-profile standard deviation is 2.506 (below the "structureless" threshold of 5); hi-hat odd-slot velocity is not lower than even (68.87 vs 68.38); bass velocity on kick-coincident onsets is *lower* than elsewhere (68.24 vs 76.95). This is consistent with the drum ratio < 1 above.

![Route-1 velocity profiles: mean velocity by 16th slot per stem class, five focus songs overlaid. Backbeat slots are shaded; no accent structure is visible.](data/v5/rules/fig_velocity_profiles_c86.png)

2. **Bass model conditioned on half the corpus.** The bass interval-class model skipped 6,426 of 12,196 corpus bass onsets (52.7 %) that fall on `N` (no-chord) beats.
3. **Melody model memorises.** The variable-order Markov melody model's order-3 singleton-context fraction is 0.7206 (threshold 0.5): iteration-3 melodies are closer to recombined corpus fragments than to a learned style.
4. **Cross-cycle stem mismatch accepted.** Fresh htdemucs separations differ in SHA from the earlier stage cache on all five songs (decoded full-mix SHAs match; in-cycle ×2 holds). Per the guidance this is accepted; the artefacts of record are the five `velocities.json` files and their sibling MIDI SHAs.

### F3 step 1: comping statistics and builder

On the 23-song eligible set, all 23 songs contribute ≥ 16 pooled bars and the pooled 16th-slot maximum mass is 0.065174 — verdict **COMPING_NON_DEGENERATE**, byte-deterministic across two runs. Pooled figures: 2,091 bars, 20,990 onset groups, 10.04 onsets per bar, chord size 5.85, sustain 3.89 beats. Per stem class: guitar 21 songs / 1,381 bars / 7.16 onsets per bar / chord size 5.47 / sustain 0.59 beats; piano 17 songs / 641 bars; other 20 songs / 1,243 bars / chord size 6.23.

The worker disclosed that the < 0.5 criterion is met trivially: the slot histograms are near-uniform (guitar 0.058–0.067 across the 16 slots against 0.0625 for uniform), plausibly because the analysis has no per-bar beat tracking or drum-phase alignment over full-length songs with tempo drift. The IOI histogram, by contrast, is strongly structured — guitar 0.475 at one 16th, 0.306 at two, 0.068 at three, 0.074 at four — and is what the builder uses. About 12.8 % of starts are unpaired and are excluded from the sustain statistic only.

![Comping statistics on n=23: 16th-slot onset histograms per stem class (near-uniform; the 0.5 threshold line is far above) and the pooled IOI histogram (concentrated at one and two 16ths).](data/v5/rules/fig_comping_v5_c87.png)

The builder's tests confirm 275 deterministic comping notes on a fixture, `N`-bar rests, pitches in register, and that the IOI walk reproduces the guitar histogram (0.507 vs 0.475 at one 16th; 0.310 vs 0.306 at two).

**Decision: `--f3` wiring deferred by one cycle.** The builder was finished ~15 minutes after iteration 3 rendered. Wiring the flag would have changed the generator SHA pinned in the iteration-3 rollup, byte-determinism record and listening manifests, and re-proving flag-off under a third image did not fit the remaining time. The deviation from the brief was disclosed with the enumeration value F3_FLAG_WIRING_DEFERRED and the F3 milestone left open into the next cycle.

### F3 step 2: iteration 4 rendered, F3_LANDS

Iteration 4 (seed 3, `--f2 --velocity-mode f2 --f3 --tempo-overrides …`, n=23 harmony `330b9d46…` and groove `57072025…`, `--prove-replay`) rendered under image `3d0f3a24…`. Results per song:

| song | guitar note-ons / dBFS / program | piano | other | ear v2 | duration s |
|---|---|---|---|---|---|
| CG | 2140 / −21.3 / 28 (pinned) | 1680 / −23.0 / 0 | 2664 / −19.0 / 89 | 6.45 | 172.4 |
| WIG | 2220 / −20.7 / 27 | 1482 / −23.3 / 0 | 2628 / −19.6 / 89 | 6.42 | 160.1 |
| Rome | 2245 / −20.1 / 27 | 1488 / −22.7 / 0 | 2616 / −19.8 / 89 | 6.23 | 106.5 |
| PD | 2250 / −20.5 / 27 | 1758 / −22.3 / 0 | 2640 / −19.6 / 89 | 6.52 | 130.6 |
| Disco A | 2170 / −20.4 / 27 | 1524 / −22.9 / 0 | 2616 / −19.0 / 89 | 6.53 | 132.4 |

Every per-song clause holds (parts present ≥ 32 note-ons, audible, replay ×2) and the flag-off clause holds (below), so the verdict is **F3_LANDS**. dBFS values are the raw render level before normalisation; the normalised-track level is −22.0 dBFS by construction, which makes the pre-registered audibility clause near-tautological — the worker disclosed this and added the raw figure so the finding holds either way. Each new part has 73–79 distinct velocity values. Eight bars per song rest under the keys mute mask.

![Iteration 4 comping parts: note-on counts per part (log scale, prereg minimum 32 marked) and raw render RMS per part against the −60 dBFS floor and the −22 dBFS mix target.](data/v5/gen/iteration_04/fig_iter04_parts_c88.png)

The manifests of all five songs pin the n=23 harmony and groove SHAs, the form plan, the comping model and builder, the tempo-overrides file, the velocity profiles, the bass and melody models, and the environment pin; PD and Disco A carry `tempo_source = tempo_overrides_c86.json` at the adopted values, the other three use their own detected tempo.

### Determinism and regression record

- Iteration 3: 5/5 replay proofs hold; flag-off under the *final* cycle-87 image reproduces iteration 2 and iteration 1 (10/10).
- Iteration 4: 5/5 replay proofs hold (`a501df3c…`, `fe366926…`, `19b0f51d…`, `99e3ee69…`, `313b98bd…`).
- Post-edit image `3d0f3a24…` without `--f3` reproduces iteration 3 (`b6a83535…`, `c247fe07…`, `085ded8d…`, `7c0d1b18…`, `2fce4959…`, 52 s) and without `--f2/--f3` reproduces iteration 2 (`240b893a…` … `330916d5…`, 40 s), 5/5 each.
- All 15 iteration-1..3 WAVs on disk are byte-identical to their rollups; all read-only pins taken at cycle-88 turn start are unchanged except the generator and the plan of record, the two files declared as edited.
- Environment pin `2ac444c3…922ca` unchanged on every artefact.

### Ear scores and the iteration schedule

Informational scores (VGGish v2 calibration, ×2 tables equal):

| iteration | feature | seed | scores (CG, WIG, Rome, PD, Disco A) | ≥ 6 |
|---|---|---|---|---|
| 3 | F2 dynamics | 2 | 6.35, 6.25, 5.93, 6.37, 6.41 | 4/5 |
| 4 | F3 comping | 3 | 6.45, 6.42, 6.23, 6.52, 6.53 | 5/5 |

No passer is declared (FD-6). The stall counter reads 4/12 with schedule entries for iterations 3 and 4 recording the feature, seed, donor-map, form-plan, rule and model SHAs.

### Housekeeping

Disk opened cycle 88 at 86 % (5.97 GB free), at the 85 % warning threshold; 377 MB of regenerable `/tmp` render directories from the previous cycles' ×2 runs were pruned (86 % → 85 %); nothing under the corpus, profiles or v4 trees was touched, and a 48 MB groove-model copy inside `iteration_01/` was left in place because the worker role never deletes workspace artefacts. Disk never reached the 90 % abort ceiling. Cycle-87 cheap fixes: creation stamps on three unpinned files, an interpreter guard on the sibling serializer (56/56 byte-equality re-checked), a repo-root path bug in the iteration-3 plot script (which recurred in the iteration-4 plot script in cycle 88 — each costing a tail relaunch), and the ledger emitters made fail-closed. The cycle-86 ledger events and plan rows, which the previous range left unemitted, were emitted at the start of cycle 87 after the auditor's dedupe-key fix.

### Audit outcome

The cycle-88 audit measured every in-scope value independently and re-executed the two decisive renders (iteration 4 flag-on, iteration 3 flag-off) from a fresh scratch directory under the pinned environment, reproducing all ten SHAs. Prereg precedence: 0 violations across 208 files. Tests re-run by the auditor: 30/30 across four files; the worker's adopted suite 73/73. Validators at baseline (156 legacy errors flat; warnings grew by 164 from the new iteration-4 artefact paths). Verdict **VALIDATED** for both the F3 feature and the F4 plan-of-record amendment, with seven minor observations logged: the near-tautological audibility clause (already disclosed); untriaged warning growth; pipeline runner scripts living only in the session scratchpad (renders reproducible from the pinned launch commands, orchestration not); the recurring plot-script repo-root slip; 14/15 program cells being GM shims, with CG's pinned guitar profile itself ruled out as a soundfont match earlier in the run; comping density of 1.5–2.7 k note-ons per 64 bars (corpus onset density ≈ 7 per bar × ~6-note voicings); and a 207-vs-208 file-count slip in the worker narrative. The previous cycle's audit was never emitted as a formal report; its two findings (stale F4 plan row; F3 wiring deferred) are both discharged by cycle 88.

## Discussion

**The determinism discipline is doing its job.** Two generator edits, two new iterations, and every prior iteration still reproduces byte-for-byte under the newest image from a fresh process — verified by the auditor, not only the worker. The cost is visible too: the decision to defer `--f3` wiring by a cycle was made precisely to avoid invalidating pins on artefacts rendered fifteen minutes earlier.

**F2 is honest about a weak result.** The dynamics feature is wired and reproducible but does not do what it was meant to do for drums. The three disclosures (structureless profiles, half the bass onsets skipped, memorising melody model) locate the weakness in the extracted models, not the generator. The operator's rule for this arc is to record and move on; the audit's carry-forward names a drum-dynamics mechanism probe as the honest next step if the feature is ever revisited.

**F3 landed on a real statistic, not the trivial one.** The pre-registered non-degeneracy rule turned out to be satisfied trivially by a near-uniform slot histogram; the worker said so and built the part from the IOI histogram, which is structured. The pre-registration for iteration 4 named this choice explicitly before rendering.

**Timbre and density are the disclosed weaknesses of the new parts.** Fourteen of fifteen song×part cells render through GM shims, and the parts are dense. Both are consequences of the corpus statistics and the profile inventory rather than defects; both belong to the operator's ear rather than to a criterion.

**Ear scores have moved with the features** (4/5 ≥ 6 at iteration 1 and 3, 5/5 at iteration 4) but are, by policy, not evidence of passing.

## Open questions and next steps

Binding for the next cycle (from the audit's confirmation):

- **F5 interpolation demo**: own pre-registration, seed 4, iteration 5 on the n=23 chain plus the comping model; CG ↔ PD at t = 0.5 blending groove and harmony; rendered with `--f2 --f3`, replay ×2; flag-off regression proving the iteration-4 SHAs survive any edited image; stall 4/12 → 5/12 with a schedule entry.
- Cheap carry-forwards: state the audibility clause on the raw render; a shared repo-root helper for the `data/v5/gen/iteration_NN/` plot scripts; the n=25 sibling artefacts if time permits; keep the disk-prune-first step (disk at 85–86 %).
- Do not retune drum velocities or comping density.

Still owed after F5: F6 continues as schedule entries; F7 close-out documents (report amendment, operator decisions, codebase guide) after F1–F5 have landed. Not addressed in this range: a drum-dynamics mechanism probe; a comping slot-histogram diagnostic with beat tracking; profiling the fourteen shimmed instrument cells.

## Appendix: Implementation Details

### Cycle numbering

The harness report range is cycles 137–139 with session records supplied for cycles 138 and 139 only; no record exists for cycle 137. On disk the work is labelled cycles 87 and 88, which the workers mapped to harness cycles 131 and 132 under an assumed offset of 44 that they disclosed but did not reconcile. This report treats harness 138 ≈ on-disk 87 and harness 139 ≈ on-disk 88 and does not attempt to resolve the counters.

### Sources consulted

The session-history tools were not permitted in this session, so the researcher briefs, worker outputs and the cycle-138 audit text were not read directly; the supplied cycle-139 audit report was. Everything else was gathered from disk: `promise_ledger.jsonl` lines 2095–2138, the `plan_of_record.md` diff against commit `8bbb93fe` (35 new rows plus the amended F4 row), both iteration rollups, both ear-score tables, `comping_prereg_c87.json`, `comping_v5.json`, `f3_prereg_c88.json`, `byte_determinism_c86.json` / `_c88.json`, `test_results_c87.json` / `_c88.json`, `c88_prune.json`, `stall_counter.json`, the two 2026-09-09 guidance files, and the four plot scripts. `REFERENCES.md` does not exist in the workspace; no references are cited in this range and no References section is emitted.

### Sessions

| harness cycle | role | session |
|---|---|---|
| 138 | researcher | `f0f82a00-e0b2-42cc-8597-c59debee183a` |
| 138 | worker | `b85a8dc5-8fd5-4e32-8df0-3dacd55dc3ee` |
| 138 | auditor | `05fb37fa-0a1d-472f-a05a-f76f3308459f` |
| 139 | researcher | `818b01c0-5af5-4bd8-ada6-526004600def` |
| 139 | worker | `ad3e3d08-c2f5-402e-8553-8cda1a116529` |
| 139 | auditor | `7223e803-936e-418d-98a3-aaff0aa6c9c9` |

### Ledger and plan

- Ledger 2094 → 2138. Cycle 87: 32 events (12 cycle-86 events emitted late, L2083–L2094 region, plus L2095–L2126), including `M-V5-GEN-1/F2-route-decided-c86`, `M-V5-GEN-1/F4-tempo-fix` (supersedes `tempo_f4_verdict_c85.json`), `M-V5-GEN-1/iteration-03-c87`, `M-V5-RULES-1/groove-n23-c86`, `M-V5-RULES-1/comping-stats-c87`, `M-V5-GEN-1/F3-guitar-piano-other` (in-progress), `_run/cycle_87_closed`. Cycle 88: 12 events L2127–L2138, including `_plan/f4-tempo-fix-por-row-amended-c88`, `M-V5-GEN-1/f3-preregistered-c88`, `_infra/f3-wiring-and-tempo-overrides-c88`, `M-V5-GEN-1/iteration-04-c88`, `M-V5-GEN-1/F3-guitar-piano-other` (validated, F3_LANDS), `_infra/n25-follow-up-deferred-c88`, `_run/cycle_88_closed`. All `agent=worker`, validated/high.
- Plan of record: F4 row amended in place (+36/−1 in the diff, the one deletion being the row re-emitted with the clause); 11 cycle-88 rows, 9 cycle-87 rows, 15 cycle-86 rows registered inline.
- Validators: promise_check 156 ERROR (flat since the cycle-84 backfill) / 8707 WARN; org_check 0 / 54.

### Code and tests

New: `scripts/v5/comping_v5.py` (325 lines), `scripts/v5/comping_gen_v5.py` (103); `generate_v5.py` now 969 lines (+134/−11 in cycle 88); `midi_from_json_events_v5.py` +6. Figure scripts: `data/v5/rules/plot_comping_v5_c87.py` (98), `data/v5/gen/iteration_04/plot_iter04_parts_c88.py` (66). Tools: `_emit_c87_early_events.py` (165), `_emit_c87_ledger_events.py` (237), `_register_c87_por_rows.py` (67), `_emit_c88_ledger_events.py` (215), `_register_c88_por_rows.py` (93). Tests: `test_c87_landing.py` (10), `test_c87_comping.py` (5), `test_c87_f3_gen.py` (4), `test_c88_landing.py` (10); adopted suite 73/73 at cycle-88 close (59/59 at cycle-87 close). Script SHAs of record: generator pre `f261690c…` / post `3d0f3a24…`; comping builder `571cc0a4…`; comping stats script `f4ca0552…`; velocity script `dd94336d…`; serializer `4ea85e0b…`.

### Data artefacts

Listed in `MANIFEST.md` (updated at this report). Figures embedded above: `data/v5/gen/iteration_03/fig_iter03_velocity_c86.png`, `data/v5/rules/fig_velocity_profiles_c86.png`, `data/v5/rules/fig_comping_v5_c87.png`, `data/v5/gen/iteration_04/fig_iter04_parts_c88.png`. Listening copies: `data/v4/generated/v5_iter_03/`, `v5_iter_04/`.

### Cross-reference map

`eligible_c86.json` (n=23) → harmony `330b9d46…` / groove `57072025…` / comping `01024254…` → iteration 4. `tempo_overrides_c86.json` (`ef52f2a0…`) → comping statistics and iteration 4 (PD/Disco A). `velocities.json` ×5 → `velocity_profiles_v5.json` `6b2fc502…`, `bass_pitch_v5.json` `96d34b3b…`, `melody_vomm_v5.json` `48157c6f…` → iterations 3 and 4. `comping_v5.json` → `comping_gen_v5.py` → `generate_v5.py --f3`. Flag-off chain: image `3d0f3a24…` → iteration 2 (`240b893a…`…) and iteration 3 (`b6a83535…`…) reproduced 5/5 each.
