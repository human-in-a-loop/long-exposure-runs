---
title: "Music-Gen v5 — cycles 128-130"
date: "2026-09-09"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# Music-Gen v5 — cycles 128-130

## Abstract

This range resumed the v5 arc after a two-day outage and, under a new operator priority ("finish building features, even if the music is still bad"), moved the generator from a 16-bar proof of concept to a feature-driven iteration programme. Three things landed fully. (1) The 26-song corpus finished full-length transcription with lossless canonical MIDI for every song, a pre-registered content gate removed one spoken-word recording, and the harmony and groove rule models were rebuilt on the full eligible corpus (n=21): the harmony Markov chain is non-degenerate (81 functional chord states, largest stationary mass 0.064 on the tonic major), while groove v2 was recorded as over-fitting (singleton-context fraction 0.64) with the mechanism traced to the 24-bit hi-hat context rather than corpus size. (2) Feature F1 — length, form and arrangement — shipped as iteration 2: a corpus form-plan model, a fixed-template fallback after the pre-registered segmentation threshold failed, a section-contrast rule that held on 5/5 songs, and intro/breakdown/outro/fill arrangement; four of five renders satisfied every pre-declared clause (verdict FORM_PLAN_PARTIAL), durations rose from 28–44 s to 65–169 s, and all five renders replay byte-identically. (3) Feature F4 — the tempo of the two blocked focus songs, Peach Dream and Disco A — was first adjudicated under a pre-registered half/double-time check that returned AMBIGUOUS (the 2T candidate out-scored the adopted lag on both songs), then resolved by operator decision: the failing clause is a defect of the criterion for a 4/4 groove with a strong two-bar period. Both songs were re-canonicalised at 122.197 and 120.272 BPM, the harmony chain was re-run at n=23 (still 81 states, max |Δ stationary mass| 0.008), and F4 is closed. Feature F2 — bass and melody models with dynamics — landed its components but not its render: a stem-audio velocity route was chosen within the 10-minute rule and produced per-onset velocities for all five focus songs plus a pooled velocity-profile model; a chord-conditioned bass pitch model and a variable-order melody model were built and reproduce byte-identically; the generator gained a default-off F2 path with a 10/10 flag-off regression. Iteration 3 was not rendered because the worker turn ended with the velocity extraction still running. The independent audit confirmed every landed claim by regeneration, fixed one defect that would have silently dropped the F4-closed record, and returned CONTINUE with instructions to finish iteration 3 first and then begin F3. Two cross-cycle facts are disclosed rather than chased: htdemucs stem separation is deterministic within a cycle but its bytes drift from the c79 cache (torch stack change; operator-accepted), and the pooled drum-accent profile shows no backbeat structure (backbeat − odd-slot mean = −1.9 velocity units; slot-profile std 2.5).

## Introduction

The v5 arc builds a groove-first generator on rules extracted from full-length transcriptions of a 26-song corpus. Every artefact is produced under a fixed environment pin, without pseudo-random number generators (all sampling is SHA-256 inverse-CDF), with pre-registration of any decision rule before its output exists, and with a "regenerate twice into fresh temporary directories" byte-determinism proof for each claim. The corpus is split into five *focus songs* — Chicken Grease (CG), Mura Masa "What If I Go" (WIG), Dojo Cuts "Rome", Peach Dream (PD) and Disco A — which act as donors for the generator's tempo and pinned instrument profiles, and 21 further songs used only for rule extraction.

Terms used throughout:

- **Canonical MIDI / reindexed.** MuScriptor transcribes each separated stem (drums, bass, guitar, other, piano, vocals, plus the full mix) in chunks; the reindex layer repairs an index-collision defect so that note-on events equal transcribed starts exactly ("lossless"). A sidecar file pins the SHA of every MIDI in a song directory.
- **Tempo-blocked.** Two focus songs (PD, Disco A) had no trusted tempo after four pre-registered tempo criteria were falsified in earlier work; they were excluded from rule extraction ("must not consume").
- **Harmony chain.** A beat-level Markov chain over functional chord states (relative root : quality, e.g. `0:maj`, `2:min7`, `N` for no chord). A chain is *degenerate* if any state's stationary mass reaches 0.60.
- **Groove v2.** Per-bar drum/bass conditionals — snare given an 8-bit kick pattern, hi-hat given kick and 16-bit snare, bass given kick — with a SHA-256 hold-out fold. It *over-fits* if the fraction of contexts seen exactly once ≥ 0.5.
- **Replay proof.** The rendered WAV is regenerated from its manifest into a fresh directory and must match byte for byte (`REPLAY_PROOF_HOLDS`).
- **Informational ear score.** A VGGish-embedding similarity score on a 1–7 scale. Since an earlier infeasibility proof, scores ≥ 6 are recorded but never used to declare a "passer"; the operator's own listening governs.
- **Stall counter.** The iteration budget: 12 iterations, target five passers; it stood at 2/12 at the close of this range.

The range opened on 2026-09-09 after the engine had been dead since 2026-09-07 03:32Z (rate-limit outage plus a research session that overflowed its context and was evicted). The operator's recovery note fixed the priorities as: finish transcription, rules on the full corpus, then groove-first generation. Two further operator notes arrived during the range and reshaped it: the feature backlog F1–F7 (below) and the F2 velocity decision with an addendum resolving F4.

The feature backlog, in the operator's priority order:

| # | Feature | Status at range close |
|---|---|---|
| F1 | Length + form + arrangement (32–64 bars, ≥ 1:30, 8-bar sections, contrast rule, intro/outro/breakdown, fills) | Landed as iteration 2 (PARTIAL 4/5) |
| F2 | Bass pitch model conditioned on chord; melody VOMM over scale degrees; velocities carried through canonical MIDI | Components landed; iteration 3 not rendered |
| F3 | Guitar / piano / other parts via donor pinned profiles | Not started |
| F4 | Tempo fix for PD and Disco A so the harmony chain covers all five focus songs | Closed by operator adjudication; n=23 chain on disk |
| F5 | Interpolation demo (two donors, t = 0.5 blend) | Pending |
| F6 | Iteration schedule recorded per iteration | Landed |
| F7 | Close-out documentation | Pending (after F1–F5) |

## Approach

The work proceeded as three sequential cycles, each closed by an independent audit that regenerates claimed artefacts rather than accepting them on report.

**First cycle — outage recovery by execution.** Confirm the detached transcription driver is dead (it was: the PID was absent and its log stopped at 2026-09-07 03:42Z with 24/26 songs landed), verify the driver and hook scripts are byte-identical to their pinned SHAs, verify the stage-cache environment-pin key reproduces, and relaunch the pinned command so the last two songs resume from cache. Pre-register and run a content gate. Run harmony and groove on every eligible song. Render iteration 1 of the groove-first generator.

**Second cycle — F1 and the first F4 attempt.** Adopt the operator's F1–F7 backlog. Pre-register the form/arrangement model, build it from the n=21 corpus, extend the generator behind a `--form-plan` flag whose absence reproduces iteration 1 byte-for-byte, render iteration 2, and deliver listening copies. Pre-register and run the operator-mandated half/double-time check on PD and Disco A. Land the F6 iteration-schedule schema and a set of cheap fixes from the previous audit (per-claim byte-determinism records, no 48 MB groove-model copy per iteration, `--cycle` on the scoring and delivery scripts).

**Third cycle — F4 close and F2.** Consume the operator's F4 addendum: amend the blocked-songs file additively, re-canonicalise both songs at the adopted tempi, re-run harmony and groove at n=23. For F2: decide the velocity route within 10 minutes by a scripted gate, pre-register everything, extract velocities from stem audio for the five focus songs (score-and-delete), build the velocity-profile, bass-pitch and melody models, extend the generator behind a default-off `--f2` flag, and render iteration 3 with an RMS-variance test against a uniform-velocity twin.

Disk was the binding resource throughout (≈81–84 % used under the driver's accounting; abort ceiling 90 %, never reached). Long jobs were launched detached; the operator's guidance for the next cycle now requires this at turn start after the third cycle's turn ended with work in flight.

## Findings

### Corpus completion and the content gate

The relaunched driver resumed on the Justin Bieber "YUKON" recording with cache hits on decode, separation and six of seven transcription probes (only the full-mix probe re-ran, 747 s), then landed the Allah-Las "Houston" recording. At close, 26/26 songs had full-length transcriptions and 26/26 had lossless reindex sidecars, with hook-at-birth verification on all 17 songs that landed after the previous close (sidecar written 0.02–0.9 s after the manifest; note-on count equals transcribed starts on every probe; zero catch-up reindexing needed). A first-class observation from the relaunch check: the stage-cache key is computed *without* the seven environment pins the driver itself sets, so a naive relaunch check would have looked like key drift; the driver sets the pins before importing the pin module, and cache hits were observed as expected.

The content gate was pre-registered before any output: rule R1 flags a song as non-music if the full mix and all five instrument stems have zero note-on events; rule R2 is a title regex (`commentary|interview|q&a|talk|podcast|lecture|spoken`) that corroborates but does not block on its own. Exactly the pre-registered song fired — "Shaolin Monk Motherfunk Nai Palm Commentary" (441 vocal starts, everything else 0) — giving 25 music songs and one blocked. A `ContentBlockedError` refusal was wired into all three rules scripts and fixture-tested to fire before the missing-reindex check.

Two songs — YUKON and Houston — landed *after* the harmony run of this cycle, so rule extraction used n=21 rather than the 23 then eligible. This is the origin of the "late-landed" pair carried through the rest of the range.

### Full-corpus rules: harmony non-degenerate, groove over-fits

**Harmony (n=21).** Pre-registered rule and exclusion threshold (beats with ≥ 12 simultaneous starts in one stem are excluded) unchanged from the three-song pilot. Result: **NON_DEGENERATE** — 81 functional states, largest stationary mass 0.0639 on `0:maj` (pilot: 0.0956), seven chord qualities with ≥ 8 segments. The per-song excluded-beat fraction averages 0.317 (max 0.96 for "Essence", min 0.002 for "I Want You Back"): the breadth finding from the pilot persists at full corpus and is driven by densely strummed guitar, not only the Rome bass tail. Recorded, not retuned. Chain and 21 per-song files reproduce byte-identically; the pilot chain is unchanged.

![Full-corpus harmony chain (n=21). Left: stationary mass over the 81 states, sorted; the 0.60 degeneracy ceiling and the pilot's 0.096 maximum are marked. Right: per-song fraction of beats removed by the ≥ 12-starts exclusion (orange = the three pilot songs).](data/v5/rules/fig_harmony_full_c84.png)

**Groove v2 (n=21).** Pre-registered SHA-256 fold held out three songs (Mura Masa, Charli xcx "360", Jess Best "Forgetfulness"); training set 18 songs / 1,705 bars. Held-out checks pass — backbeat ratio 0.170 corpus vs 0.122 sampled (Δ 0.048), bass-kick lock 0.568 vs 0.581 (Δ 0.012), both within ± 0.15 — but the singleton-context fraction is 0.643 (1,051/1,635) ≥ 0.5, so the verdict is **GROOVE_V2_OVERFITS**. The mechanism is first-class: the two 8-bit-context tables (snare | kick, bass | kick) fell from 0.74 at n=2 to 0.166, exactly as the "small-n" hypothesis predicted, but hat | kick, snare stays at 0.822 because its 24-bit context (1,189 distinct contexts for 1,705 bars) is nearly one-to-one with bars. The aggregate is dominated by context granularity, not corpus size. Per the pre-registered diagnostic ladder, the next axis (coarser hat context) was named, not changed. Over-fitting discloses; it does not block generation.

![Groove v2 memorisation versus corpus size. Left: singleton-context fraction for the aggregate and each conditional table at n=2 (two earlier configurations) and n=18; the 0.5 threshold is dashed. Right: held-out backbeat ratio and bass-kick lock, corpus versus 64 sampled bars, with the ± 0.15 tolerance band.](data/v5/rules/fig_groove_v2_full_c84.png)

### Iteration 1: the groove-first baseline

`generate_v5.py` produced, per focus-song donor, a fixed A A B A form of 4-bar sections (A generated once and repeated literally), drums and bass bars from the groove conditionals, one chord per bar from the harmony chain (stationary start, segment-level matrix), bass on chord root/fifth at bass onsets, sustained chord tones for keys, and hash-gated chord tones on the eighth-note grid for melody. Rendering used the donor's pinned bass/drums SoundFont profiles (CG drums: GM Standard Kit shim; keys/melody: GM programs 4 and 11, disclosed as unprofiled), per-stem RMS targets −18/−18/−22/−22 dBFS, a 0.99 peak limit, and 16-bit WAV. PD and Disco A donors used their frozen anchor tempi (123.05 / 120.19 BPM) because their transcribed tempo was blocked.

All five renders (28–44 s) hold their replay proof. Informational ear scores: four of five ≥ 6 (Rome 5.82). No passer declared; stall 1/12. Listening copies were delivered to `data/v4/generated/v5_iter_01/`.

### F1: length, form and arrangement (iteration 2)

**Pre-registration** fixed, before any output: the segmentation representation (per-bar 12-D pitch-class profile over the harmonic stems ⊕ 48-D kick/snare/hat 16th-grid ⊕ 6-D per-stem onset density; 8-bar blocks; cosine; single linkage at 0.85; first-appearance labels), the form-plan model (length = round(bars/8) clipped to [4, 8]; label Markov chain; per-label drum-density tercile and harmony-region targets; intro-density quantile; boundary fill pool), the contrast rule, the arrangement, the verdict enum FORM_PLAN_LANDS / PARTIAL / FAILS, and a diagnostic ladder whose rung R1 says: if segmentation at 0.85 fails, use the fixed template A A B A B C A A truncated to the corpus-drawn length — no threshold sweep.

**R1 failed.** At 0.85 single linkage gives CG `ABBBBBBBBBBBB`, Rome `AAAAAAAAAAAAAAAAA` and WIG `ABCDEFGDH` — transcribed-MIDI block features either chain into one cluster or fragment. The threshold is wrong for this representation; per the pre-registration the template fallback governed labels. The corpus model was still recorded: length distribution {4: 1, 6: 1, 7: 1, 8: 18} (86 % of songs clip to 8 sections), repeat-A probability 0.845, density tercile bounds [10.9, 14.0] onsets/bar over 251 blocks, intro-density quantile 0.295 (< 0.33 → bass-only intro), boundary fill pool of 37 patterns from 65 boundary bars.

![Corpus form-plan model (n=21). Left: bar counts at each song's transcribed tempo, with the 32- and 64-bar targets dashed. Centre: section-count distribution after clipping to [4, 8]. Right: label-transition matrix from the failed 0.85 segmentation, shown for the record.](data/v5/rules/fig_form_plan_corpus_c85.png)

**Iteration 2** (seed 1, form plan on, n=21 rules): every label generated once and repeated literally (core-MIDI byte-equality); the contrast rule (a non-A section's harmony start root ≠ A's dominant root at ≥ 8 segments, and its drum-density tercile ≠ A's, via an 8-candidate filter) was TRUE for every non-A section on 5/5 songs with 49–53 allowed start states each; arrangement = bass-only intro, breakdown in the first non-A section of the middle half (drums muted four bars), outro with melody muted and the final bar held, and boundary fills.

| Song | Donor (BPM) | Form | Bars | Duration | Clauses | Ear (info.) |
|---|---|---|---|---|---|---|
| 1 | Chicken Grease (92.3) | AABABCAA | 64 | 168.6 s | 5/5 | 6.32 |
| 2 | What If I Go (99.4) | AABABCAA | 64 | 156.8 s | 5/5 | 6.24 |
| 3 | Rome (152.0) | AABABCAA | 64 | 103.2 s | 5/5 | 6.11 |
| 4 | Peach Dream (123.0) | AABA | 32 | 65.3 s | 3/5 | 6.37 |
| 5 | Disco A (120.2) | AABABCAA | 64 | 130.0 s | 5/5 | 6.41 |

Verdict **FORM_PLAN_PARTIAL** (4/5). Song 4's SHA-256 length draw hit the corpus's 1/21 mass on four sections, giving 32 bars, 65 s (< 90 s) and only two labels; its contrast and A-repeat clauses hold. Not retuned. All five replay proofs hold; with `--form-plan` absent the generator reproduces the five iteration-1 WAV SHAs byte-identically. Ear scores ≥ 6 on 5/5 (informational). Listening copies in `data/v4/generated/v5_iter_02/`; stall 2/12. Disclosed: keys/melody GM shims and the PD/Disco A anchor tempi are unchanged from iteration 1, and the intro's boundary fill is inaudible by construction because drums are muted in a bass-only intro.

![Iteration-2 arrangement: per-stem onsets per bar by section for each of the five renders. M = muted stem, M4 = drums muted for four bars (breakdown), F = boundary fill, H = final bar held.](data/v5/gen/iteration_02/fig_iter02_arrangement_c85.png)

**F6** landed alongside: every stall-history entry now records the feature, donor-map SHA, form-plan SHA, rules SHAs and seed. The schedule is iteration 3 = F2, 4 = F3, 5 = F5; seed = iteration − 1; donors fixed.

### F4: tempo for Peach Dream and Disco A

**Pre-registered adjudication (second cycle).** Under the operator's F4 instruction — and explicitly *not* as a fifth tempo criterion (the tempo axis was frozen after four falsifications) — the adopted mechanism was the read-only refined-lag dominant from the last criterion: PD 122.197271 BPM, Disco A 120.272335 BPM. The check, quoted verbatim into the pre-registration: the refined candidates at T/2 and 2T must both score lower under $s_{\mathrm{ref}} = \mathrm{ac}(T) + \tfrac{1}{2}\mathrm{ac}(T/2) + \tfrac{1}{2}\mathrm{ac}(2T)$; mean drum onsets per beat at the adopted BPM must lie in [0.5, 4]; and the adopted value must be within ± 2 BPM of the independent c22 anchor.

| Song | Adopted BPM ($s_{\mathrm{ref}}$) | T/2 cand. | 2T cand. | Onsets/beat | Anchor Δ | Verdict |
|---|---|---|---|---|---|---|
| Peach Dream | 122.197 (1.352) | 242.2 BPM, 1.190 (lower ✓) | 61.08 BPM, 1.398 (NOT lower) | 2.32 ✓ | −0.85 ✓ | AMBIGUOUS |
| Disco A | 120.272 (1.321) | 239.9 BPM, 1.189 (lower ✓) | 60.04 BPM, 1.401 (NOT lower) | 3.76 ✓ | +0.09 ✓ | AMBIGUOUS |

Verdict **F4_HALF_DOUBLE_AMBIGUOUS** on both songs; nothing retuned; the blocked file stayed byte-identical; iteration 3 was scheduled to proceed on n=21.

![The half/double-time check. Each panel plots $s_{\mathrm{ref}}$ against refined-lag BPM for the earlier candidate set; the adopted value (blue), its T/2 (orange square) and 2T (purple diamond) candidates, the [70, 180] BPM pick band and the c22 anchor (red dashed) are marked. On both songs the 2T candidate sits above the adopted point.](data/v5/corpus/fig_tempo_f4_c85.png)

**Operator resolution (third cycle).** The operator overruled AMBIGUOUS on the recorded evidence: two independent estimators (refined-lag dominant and the c22 anchor) agree within 1 BPM on both songs, and the failing clause cannot pass for a 4/4 groove with a strong two-bar period because $s_{\mathrm{ref}}(2T)$ inherits $\mathrm{ac}(T)$ — a defect of the criterion, not evidence for half-time. Decision: adopt 122.197271 and 120.272335, unblock both songs recording the adjudication as the reason (do not delete the blocked file), re-run harmony at n=23 in the earliest cycle where it costs under 10 minutes, consume the n=23 chain from the next iteration, one test asserting the adopted BPMs and eligibility.

**Close.** The adjudication text was stored verbatim with the adopted values and anchors (PD anchor 123.046875, Δ −0.850; Disco A anchor 120.185, Δ +0.087). The blocked file was copied byte-for-byte to a `stale/` path *before* being amended additively with an `unblocked_c86` block; the original `blocked_songs` list was deliberately kept so that the generator's donor-tempo lookup keeps returning the frozen anchors for PD and Disco A through iteration 3 (the operator said "from the next iteration"). Both songs were re-serialised at the adopted BPM through the read-only reindex and c4 serializer into a new `canonical_v5c_reindexed/` directory per song (the existing lossless directory untouched and SHA-checked): note-on counts equal transcribed starts on all 14 probes (e.g. PD drums 1,051, bass 504, other 2,026; Disco A drums 924, guitar 1,079, full mix 2,710); `set_tempo` equals `bpm2tempo(adopted)` exactly, with the integer-microsecond quantisation (Δ 8.2e-5 / 3.9e-5 BPM) disclosed because the brief's "within 1e-6" is below what Standard MIDI can represent; 30 files + 2 sidecars byte-identical on regeneration; 0.7 s per run.

Harmony and groove were re-run at n=23 (the 21 songs plus PD and Disco A) with an additive `--tempo-overrides` flag that asserts the v5c directory served the two songs. Harmony cost 4.5 s (operator condition met). Result **HARMONY_NONDEGENERATE**: 81 states (no state gained or lost), max stationary `0:maj` 0.0693 (n=21: 0.0639), top-10 transition mass 0.2064 (0.1991), max |Δ stationary| over all states 0.0078. The top-10 differs only in `2:min→2:min` entering, `8:maj7→8:maj7` leaving, and `N→N` rising to first (PD and Disco A contribute 65 + 38 no-chord beats). Per song at the adopted tempo: Peach Dream key A♯ major, 419 beats, 164 chord segments, 63 excluded beats; Disco A key A major, 243 beats, 155 segments, 48 excluded. Groove at n=23 stays **GROOVE_V2_OVERFITS** (singleton fraction 0.637, 1,069/1,677; down from 0.643 as the mechanism predicted; same fold, PD and Disco A rank above the cut; held-out backbeat Δ 0.031, lock Δ 0.024). The post-edit harmony script replays the n=21 chain byte-identically through `--eligible-from`; the n=21 anchors are untouched. Chain, 23 per-song files and groove model reproduce byte-identically. F4 is closed; its record in the running log is owed by the not-yet-run emitter (see below).

![Harmony chain at n=23 versus n=21. Left: stationary mass over the union of 81 states. Centre: union of both top-10 transition sets. Right: PD and Disco A at the adopted tempo. The n=23 chain differs from n=21 only where PD and Disco A contribute; the rule is unchanged.](data/v5/rules/fig_harmony_n23_vs_n21_c86.png)

The n=23 count is a disclosed choice: eligibility on disk is 25 (26 landed − 1 content-blocked − 0 tempo-blocked), but the two late-landed songs were deferred and recorded in the eligibility gate so that every difference between n=23 and n=21 attributes to F4. Adding them is one command (n=25), owed at the next rules re-run.

### F2: bass line, melody and dynamics

The operator pre-empted an infeasibility memo (MuScriptor start events carry no velocity; full-length stem audio is not retained by the stage cache) by naming two routes, worker's choice within the first 10 minutes: **Route 1** — re-run htdemucs on the five focus songs, measure RMS in a 50 ms window at each transcribed onset per stem, map to velocity by per-stem rank normalisation (p5 → 40, p95 → 110), delete the stems; **Route 2** — a rule-based accent model from the groove onset histograms. Either route must yield velocities in generated MIDI for all stems, a rendered iteration, and a test that a uniform-velocity render and the F2 render differ in per-stem RMS variance.

**Route gate.** A script decided Route 1 iff disk ≤ 85 %, htdemucs importable under the pinned interpreter, and a full-song WIG separation completes in ≤ 300 s. Results: 82.06 % used, torch 2.13.0+cpu importable, separation 234 s → **ROUTE_1_STEM_AUDIO**, recorded at 22:55:58Z. The gate also compared the fresh WIG stem SHAs against the cached stems from the original transcription run: all six differ. Same input WAV, same read-only separation path with identical split/overlap/shift settings, so the drift lies in the torch/demucs stack between the original environment pin and the current one. In-cycle repetition (gate run = run 1 = run 2) holds. The operator accepted this: the artefact of record is `velocities.json` plus the sibling MIDI SHAs, not separated-stem bytes.

**Pre-registration** (written before any model, profile or render output; both models record its SHA) fixed the extraction, the mapping, a degenerate guard (spread < 1e-6 dB → all velocities 80), the output layout, diagnostic R1 (drums and bass spread p95 − p5 ≥ 6 dB on ≥ 4/5 songs, else Route-2 fallback for that stem), the velocity-profile grid (16th-note slots at donor tempo; PD and Disco A at the operator-adopted BPM), diagnostic R2 (drums: backbeat slots {4, 12} mean exceeds odd-slot mean by ≥ 10; hats odd < even; bass kick-coincident > non-coincident; if the drum slot-profile std < 5 the model is "structureless — disclosed, still shipped"), and the bass and melody model definitions. One reading was disclosed: the operator's "write velocities into canonical_v5_reindexed" was implemented as a sibling directory `canonical_v5_velocity/` because the reindexed MIDI SHAs are tested anchors.

**Velocity extraction** ran detached (launched 23:09:25Z after an earlier attempt crashed on a path bug after a full WIG separation, ≈ 8 min lost). Per song: separation 162–357 s, disk peak ≤ 84.03 %, stems deleted after measurement, in-cycle ×2 on WIG equal. Per-stem onset counts equal transcribed starts everywhere (WIG 862/83/384/1799/706/664 for drums/bass/guitar/other/piano/vocals). Velocity range 36–114 with 47–79 distinct values per stem MIDI; the sibling MIDI differs from the reindexed MIDI *only* in velocities (identical pitch/tick/channel multiset, note-off stream and tempo), and re-serialising the JSON reproduces every sibling MIDI byte-for-byte. R1 spreads:

| Song | drums | bass | guitar | other | piano | vocals |
|---|---|---|---|---|---|---|
| What If I Go | 33.4 | 27.2 | 28.8 | 25.7 | 49.6 | 22.6 |
| Chicken Grease | 31.5 | 28.4 | 20.3 | — (0 onsets) | 11.3 | 28.5 |
| Rome | 28.9 | 26.3 | 24.1 | 56.3 | 58.6 | 37.1 |
| Peach Dream | 23.9 | 18.7 | — (0) | 18.6 | 8.1 | 22.3 |
| Disco A | 26.4 | 14.8 | 25.8 | 20.1 | 50.5 | — (0) |

(p95 − p5 of onset RMS in dB.) R1 passes: drums 5/5, bass 5/5, ≥ 4/5 on every other stem; no Route-2 fallback needed. The audit closed with four of five songs done and Disco A separating; the job finished afterwards and `velocity_profiles_v5.json` is now on disk for all five songs.

**Velocity profiles (pooled, five songs).** Drum profiles by GM class (kick 35/36, snare 37–40, hat 42/44/46) × slot as quantile ladders sampled by SHA-256 inverse-CDF; bass split by kick-coincidence (± 30 ms); melody by phrase position (first/peak/last/other, phrase = onsets with gaps < 2 beats); keys by slot. R2 fails on every clause: backbeat-slot mean 73.2 vs odd-slot mean 75.1 (Δ −1.9, threshold +10); hat odd 68.9 vs even 68.4 (not lower); bass kick-coincident 68.2 vs non-coincident 77.0 (not greater); drum slot-profile std 2.51 (< 5). By the pre-registration this is a **structureless accent model, disclosed and shipped**. (On WIG alone the audit measured backbeat Δ +6.8 and std 4.3 — closer, but also below threshold.)

**Bass pitch model** (n=21, chord per beat from the per-song harmony records): onsets classified as root / fifth / octave / third / approach (± 1–2 semitones into the next chord's root within the last beat before a change) / other, conditioned on 16th slot within the beat and a chord-change flag, α = 0.5 smoothing. Of 12,196 bass onsets, 6,426 (52.7 %) fall on null-chord beats and are skipped; three songs contribute ≤ 11 events. Over the 5,770 used: other 0.370, root 0.216, fifth 0.131, third 0.119, approach 0.112, octave 0.052. Sampling check: root pitch-class fraction on downbeats 0.336 corpus vs 0.290 sampled (|Δ| 0.046 ≤ 0.15, pass). Register: corpus median MIDI 38, IQR 35–45. Reproduces byte-identically.

**Melody model** (n=21): a variable-order Markov model of maximum order 3 over tokens `<scale degree or c(hromatic)>|<inter-onset bucket ∈ {1,2,3,4,6,8,12} × 16th>` from vocal and synth-lead onsets (simultaneous onsets folded to the highest pitch; 14,570 events; vocabulary 56), escape-to-shorter-context backoff, no smoothing. Order-3 singleton-context fraction 0.7206 ≥ 0.5 → verdict **MEMORIZES** (order 2: 0.386). Phrase structure: 423 phrases, median 8 onsets, mean 34 (one 1,889-onset run). Recorded, not tuned. Reproduces byte-identically. The earlier c72 VOMM generator was not reused (different constructor and sampler; no JSON export) — a sibling with the same escape rule was written.

**Generator extension.** `generate_v5.py` (+291/−35 lines, additive) gained `--f2` (bass pitches from the bass model, melody from the VOMM, velocities from the profiles), `--velocity-mode uniform|f2` (uniform = velocity 100 everywhere, the exact null), and `--rms-variance-test` (renders the uniform twin into a tempdir and compares per-stem frame-RMS variance). A sibling serializer accepts velocities and is byte-equal to the read-only c4 serializer on 56/56 inputs without them. With the flag off, the current script reproduces iteration 2 and iteration 1 WAVs byte-identically (10/10; manifests differ only in cycle and generator hash); the stall counter and everything under `data/v4/` are untouched.

### Iteration 3 status and the audit

Iteration 3 was **not rendered**. The worker turn ended at ≈ 23:17Z with the velocity job in flight; no RMS-variance test, listening copies, figures (`fig_velocity_profiles_c86.png`, `fig_iter03_velocity_c86.png` — plot scripts exist), stall update (still 2/12) or running-log entries for the cycle exist. The route decision was recorded in the gate JSON but the one-line log entry the operator required was never written.

The audit regenerated the F4 chain, the velocity outputs, the sibling serializer, both models and the flag-off regression and found them sound. It fixed three things in place: the cycle's log emitter de-duplicated by milestone name alone against the whole history, so the F4-closed record would have been silently dropped (a record for that feature already exists from the AMBIGUOUS attempt) — the key is now (milestone, cycle); a landing test asserted an exact spread of 90.0 where `np.percentile` gives 89.1; and a sidecar-regex test matched docstring text. Remaining defects it left to the worker: future-dated `created:` stamps on four new scripts (one of them, `velocity_v5.py`, has its SHA pinned in the running job's outputs and must not be edited), a missing interpreter-guard string in the sibling serializer, three older landing tests that now fail by design because they pin the pre-amendment blocked-file SHA, and an emitter that hard-reads 24 iteration-3 paths that do not exist yet. Decision: **CONTINUE**.

Validators: no new errors on any file from this range (the 156 pre-existing errors are the earlier emitter chain's missing `agent` field; warnings rose by 132 orphan entries for the not-yet-logged files). Every frozen anchor — 22 at the second cycle's close, including the determinism certificate, the v3 rules artefact, the CG showcase mix and the pinned profiles — is byte-identical to its recorded prefix; the environment pin `2ac444c3…922ca` is unchanged on every new artefact.

## Discussion

**What the range established.** The v5 pipeline now runs end to end on the full corpus: 26 lossless transcriptions, a content gate, non-degenerate harmony at n=21 and n=23, a groove model whose over-fitting is understood mechanistically, and a generator that produces 1.5–3-minute songs with form, arrangement and (pending render) dynamics, each byte-reproducible from its manifest. Two operator decisions did the heavy lifting: reframing progress as feature landings rather than ear passers, and adjudicating the F4 tempo on estimator agreement rather than on a criterion that cannot pass for two-bar-periodic grooves.

**Determinism boundary.** Everything downstream of `velocities.json` is same-input → same-output, and every claim in this range reproduced on regeneration. The one thing that does not reproduce across cycles is htdemucs separation bytes under a changed torch stack; the operator scoped the artefact of record accordingly. Two smaller non-reproducibilities are disclosed: `velocities.json` embeds wall-clock fields (the velocity arrays and MIDI SHAs are the anchors, not the file bytes), and the byte-determinism record for the F2 models points to an ephemeral scratch path for its "final image" (the script SHA is recorded, so the claim survives).

**Models that memorise.** Three of the four corpus models carry a memorisation or structure disclosure: groove v2 over-fits (context granularity), the melody model memorises at order 3 (0.72), and the pooled drum-accent profile is structureless. The bass model additionally discards 52.7 % of onsets as null-chord. None was tuned; all are recorded against their pre-registration and consumed as-is, consistent with the operator's "the ear does not need to be perfect yet".

**Process pattern.** For the fourth consecutive cycle the whole record of a cycle depended on a single end-of-cycle emission, and the worker turn ended with work in flight. The operator has responded with a binding instruction to launch long jobs detached at turn start and check completion before summarising.

## Open questions and next steps

Binding for the next cycle, in order:

1. Finish F2 in the first 20 minutes: the velocity outputs are now complete for all five songs; render iteration 3 (seed 2, form plan on, `--f2 --velocity-mode f2 --rms-variance-test --prove-replay`, n=21 rules by design), score, deliver to `data/v4/generated/v5_iter_03/`, produce the two velocity figures, advance the stall counter to 3/12 with the schedule entry, and record the post-edit generator SHA in a byte-determinism file.
2. Run the (patched) emitter and registrar only after all artefacts exist; add the route-decision line, the adoption record, the F4-closed record superseding the AMBIGUOUS verdict, and one disclosure line each for: cross-cycle stem drift; n=23 deferring two eligible songs (n=25 owed at the next rules run); structureless drum accents; bass-model null-chord skips; melody-model memorisation; wall-clock fields in `velocities.json`.
3. Test hygiene: fix the future-dated stamps only on files whose SHA is not yet pinned, add the interpreter guard to the sibling serializer, re-pin the three older landing tests to the amended blocked file (stale `2fbabc07…`, live `eb78cfc0…`) and add an assertion pinning the live SHA.
4. Start F3 (guitar/piano/other via donor pinned profiles — Rome piano/other, Disco A guitar/piano, CG guitar; GM shim elsewhere; comping rhythm from corpus onset statistics), landing the code flag-off if unfinished. Iteration 4 consumes the n=23 chain (ideally n=25) and the adopted tempi for PD and Disco A.

Still open beyond the next cycle: F5 (interpolation demo, CG ↔ PD), F7 (close-out documentation), the coarser hat context for groove v2, a segmentation representation for which the 0.85 threshold is meaningful, and whether the pooled accent profile gains structure when computed per song or with phase alignment for PD and Disco A (currently offset 0 because they are absent from the groove model's phase table).

## Appendix: Implementation Details

**Cycle counter.** On-disk cycles c84, c85, c86 correspond to harness cycles 128, 129, 130 (offset 44 after the c100–c127 outage; disclosed in every record, not reconciled).

**Sessions.**

| Cycle | Researcher | Worker | Auditor |
|---|---|---|---|
| 128 (c84) | `5810dbac-e255-4f6d-ba3a-c8c416fce212` | `50ab996c-1292-472d-8b99-816eef05363c` | `a74621b2-44d5-4e57-a817-c1197c4dd14a` |
| 129 (c85) | `d1518d42-9805-43dc-ae18-f90c6f3781ff` | `a2e8d1c3-b468-408e-9e0e-629587099eb7` | `0910982b-95b6-43a1-bc10-e6d8775e6a3b` |
| 130 (c86) | `873161bd-9847-444c-9421-2e495c87f3b3` | `2ec149ae-23fb-4f23-bc58-a38c53f1a7a4` | `efbec95d-6884-464c-82e2-df8a9f4931a2` |

Gap in the record: the session-summary store was not readable while this report was compiled, so the researcher briefs and the c128/c129 audit texts were not consulted directly. Their content is reflected here through the ledger events, plan-of-record rows, the c86 worker report (`data/v5/corpus/f4_close_report_c86.md`), the four operator guidance files under `docs/guidance/` dated 2026-09-09, the c130 audit report supplied as input, and the artefacts themselves. The c128 audit's findings are visible only as the "M1–M5" cheap fixes the c85 worker landed.

**Ledger / plan.** `promise_ledger.jsonl` grew from 2,047 to 2,094 lines (c84: 32 events; c85: 15 events; c86: 0 — emitter `tools/_emit_c86_ledger_events.py` not yet run). `plan_of_record.md` gained 51 rows. Milestones touched: `M-V5-CORPUS-1` (liveness, driver restart, content gate, 17 per-song lossless rows, hook-at-birth, F4 pre-registration + adjudication), `M-V5-RULES-1` (harmony/groove n=21, `--eligible-from`), `M-V5-GEN-1` (iteration 1, F1–F7 rows, form pre-registration/model, iteration 2, F6), `_infra/*`, `_plan/*`, `_archive/*`, `_run/cycle_84_closed`, `_run/cycle_85_closed`. Proposed c86 narratives for `M-V5-CORPUS-1/tempo-f4-operator-resolved-c86`, `M-V5-RULES-1/harmony-n23-c86` and `M-V5-GEN-1/F4-tempo-fix` (validated, CLOSED, `supersedes_path = data/v5/corpus/tempo_f4_verdict_c85.json`) are drafted in the F4 close report.

**Git.** Commits `0359c031` (archive c128 guidance) … `46e85e48` (c131 guidance + c130 close): 37 files, +6,085/−27 lines. Scripts, tests and tools are inventoried in `MANIFEST.md` (updated with this report; the "Key Files" section from the v4 close-out is preserved verbatim).

**Key SHAs (prefixes).** Env pin `2ac444c36298d6ad…922ca`. Harmony n=21 `a984ee17…`; groove n=21 `faa0e76e…`; eligible n=21 `e62c6ef3…`. Form plan `d6c14f9a…`; form prereg `e71eda9b…`. F4 verdict (AMBIGUOUS) `bec3631a…`; operator resolution `793ee0e1…`; blocked file pre `2fbabc07…` → post `eb78cfc0…`; tempo overrides `ef52f2a0…`; harmony n=23 `330b9d46…`; groove n=23 `57072025…`; eligible n=23 `55037c2f…`. F2 prereg `2e17ea57…`; bass model `96d34b3b…` (script `b6887ddd…`); melody model `48157c6f…` (script `329b3ecf…`); `velocity_v5.py` `dd94336d…`; `generate_v5.py` c85 `b3473fd2…` → c86 `85d42d86…`. Iteration-1 WAVs `f4cdb294/953dbffc/0a95411b/2f214128/aa1da38f`; iteration-2 WAVs `240b893a/9b1812c0/ac01eb92/940227fb/330916d5`.

**Tests (status at close).** `test_c84_landing.py` 8 (test_02 fails by design after the F4 amendment); `test_c85_landing.py` 10 (test_01, test_08 likewise; test_05 flag-off replay passes); `test_c85_f4_m5.py` 5/5; `test_c86_f4_close.py` 6/6 (test_01 is the operator-required adopted-BPM + eligibility test); `test_c86_f2_models.py` 5/5; `test_c86_landing.py` 3/10 after the auditor's two fixes (the rest wait on iteration-3 artefacts or the stamp/guard fixes). Adopted-suite regression at c84 close: 93/93 across 16 files.

**Figures embedded in this report** (all with co-located `--out` plot scripts): `data/v5/rules/fig_harmony_full_c84.png`, `data/v5/rules/fig_groove_v2_full_c84.png`, `data/v5/rules/fig_form_plan_corpus_c85.png`, `data/v5/gen/iteration_02/fig_iter02_arrangement_c85.png`, `data/v5/corpus/fig_tempo_f4_c85.png`, `data/v5/rules/fig_harmony_n23_vs_n21_c86.png`.

**References.** No `REFERENCES.md` exists in the workspace and no external sources were cited during these cycles; no references section is emitted.
