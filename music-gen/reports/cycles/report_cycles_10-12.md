---
title: "Music-Gen v4 closure campaign — cycles 10–12"
date: "2026-09-04"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# Music-Gen v4 closure campaign — cycles 10–12

## Abstract

Cycles 10–12 close the Chicken Grease drums sub-milestone of the v4
closure campaign. Cycle 10 fixed the cycle-9 disk-check false positive
that had blocked the detached SoundFont drums sweep and launched the
sweep under the canonical replay-time environment pin. Cycle 11 ran
the 216-cell fine-fit stage, emitted the drums profile of record
(program 16 Power Kit, embedding-cosine 0.2374 against the reference
stem), and patched the replay dispatcher to be MIDI-channel aware so
that channel-10 drum programs replay correctly; the SoundFont family
verdict came out **`SF2_RULED_OUT`** because the top-1 embedding
cosine sits below the 0.40 retained honesty floor. Cycle 12 shipped
the family-2 stem-sampled drums arc — spike, builder, render, replay
proof, verdict — and ruled it out as well at embedding cosine 0.0372,
closing the drums arc as **`CG_DRUMS_ARC_EXHAUSTED_NO_CONFIRMED`**
with the same shape as the cycle-7 bass closeout. It also ran an
independent from-fresh-subprocess replay-regression check covering
both the bass-v2 anchor and the new drums anchor (both byte-identical
across two runs), closing the moderate finding the cycle-11 auditor
had left open. A three-option drums acceptance policy has been
escalated to operator authority; unlike the cycle-9 bass case, the
agent did not unilaterally extend the composite-relative acceptance
precedent, because the operator's cycle-9 threshold retirement was
explicitly scoped to Chicken Grease bass. Two of the five Chicken
Grease instrument tracks now have terminal verdicts; the full A/B
render remains gated on the remaining three sub-milestones plus the
drums acceptance decision.

## 1. Where things stood at cycle-10 open

By the close of cycle 9, three loose ends remained under
`M-V4-PROFILES-1`:

1. The detached SoundFont drums coarse sweep had been prepared
   (script `coarse_sweep_sf2_drums.py`, dry-run PASS) but its launch
   had been halted by a false positive in the pre-flight disk-space
   check. The check used a `statvfs`-derived percentage that reported
   the working volume at 97.39 % full, while `df -h` on the same
   volume showed 82.24 % full and 6.6 GB free — comfortably above
   the 500 MB working-audio budget of a single sweep cycle. This was
   the sole gate on running the drums sweep.
2. The reference render family (SoundFont) had been proved replayable
   for bass-only material (MIDI channel 0), but the replay engine
   had not yet been exercised on a channel-10 drum-kit program.
3. The Chicken Grease A/B render scaffold (`deliver_cg_ab_v4.py`)
   had smoke-tested with `n_missing = 4` — drums, piano, guitar, and
   the residual "other" bucket — and was waiting for each of those
   profiles to land.

The cycle-10 auditor also carried forward a broader observation from
prior cycles: percentage-based resource-limit checks were prone to
mismatching the reference tool's numeric intuition (df vs statvfs,
LUFS-I vs RMS-dBFS fallback, sha16 slicing), and a small shared
`long_exposure.tools.resource_check` helper module would prevent the
class of defect recurring. That refactor was noted and deferred; the
concrete cycle-10 work was the point fix.

## 2. Cycle 10 — disk-check repair and drums sweep launch

The `_disk_ok()` predicate in `coarse_sweep_sf2_drums.py` was
rewritten from a percentage-remaining formula to an absolute-budget
formula:

$$\text{ok} \;\Leftrightarrow\; \text{avail\_bytes} \;\geq\; \text{budget\_bytes} \cdot \text{safety\_factor}$$

with `budget_bytes = 500 · 2^20` and `safety_factor = 1.5`. This
matches the operator's stated budget discipline directly (a working
sweep may consume up to 500 MB of audio) rather than backing it out
from a percentage of a volume whose size varies with mount point.
A regression test, `tests/test_coarse_sweep_disk_check.py`, was added
that pins the new formula and asserts the cycle-9 false-positive
scenario (large volume, small percentage-free, ample absolute-free)
now passes the check.

With the gate repaired, the detached drums sweep launched under the
canonical seven-key replay-time environment pin (`LC_ALL`,
`MKL_NUM_THREADS`, `OMP_NUM_THREADS`, `OPENBLAS_NUM_THREADS`,
`PYTHONHASHSEED`, `SOURCE_DATE_EPOCH`, `TZ`; SHA
`2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca`).
The coarse sweep enumerated the 15 GM drum-kit programs on MIDI
channel 10 against the reference stem (`stems_6s/drums.wav`, SHA
`34492c03f301b6eac3a75343b61244193889d039ae4ccce4c35cc44d568ac835`)
and the drums MIDI excerpt (channel 10, 186 note-on events, SHA
`0fd71ce70a26365c2acf08b9f87531178f9f9c18cc419d042a3869989c990ef2`).
The stage-1 leaderboard landed at
`drums_sweep_stage1/leaderboard.tsv` with SHA
`dd5544d3bd3a549cab95…`. Two supplementary regression tests
covering the drums-plus-bass cross-check and the drums-family
stage-2 leaderboard structure — `test_rc10_drums_bass.py` and
`test_rc10_drums_v2.py` — were added.

The cycle-10 auditor raised one moderate finding: the replay
engine's `_replay_sf2` had never been exercised on a program on a
MIDI channel other than 0, and the bass-only regression that had
validated the cycle-6 replay fix therefore did not cover the drums
case. That finding was scheduled for cycle-11 closure.

## 3. Cycle 11 — drums fine-fit, channel-aware replay, family verdict

### 3.1 Stage-2 fine-fit and profile emission

A drums-specific fine-fit driver, `fine_fit_sf2_drums.py` (679 lines,
channel-10 aware, LUFS-normalised) was authored as a direct sibling
of the cycle-3 bass driver. It re-scored the top-3 coarse programs
across a 216-cell grid over gain, reverb-send, and post-processing.
The stage-2 leaderboard (`drums_sweep_stage2/leaderboard.tsv`, SHA
`81a441732f7f7d1da615…`) shows a composite spread of 176.7 % across
the 216 cells, indicating that the fine-fit is not degenerate.

The stage-2 top-1 by frozen composite (weights 0.5 mel-L1, 0.25
spectral-centroid RMSE, 0.25 embedding-cosine) came in at:

| field | value |
|---|---|
| GM program | 16 (Power Kit) |
| gain | 1.0 |
| reverb send | 0.7 |
| post-processing | `EQ_only` |
| composite | 475.74 |
| mel-L1 | 10.44 dB |
| spectral-centroid RMSE | 1858.33 Hz |
| embedding-cosine (VGGish) | 0.2374 |

The drums profile was pinned as `drums.json`, UUID
`83728154-6f48-5c5d-a558-b4d82523ac1b`, canonical replay SHA
`dadafcfc0153f002651c23975c3845dd3f8ca7896d263faf1c52eb54d64b8d7c`.

### 3.2 Channel-aware replay fix

To close the cycle-10 moderate finding, `replay.py` was patched
in place at lines 79–93. The pre-patch dispatcher wrote the
program-change event onto channel 0 regardless of the program's
actual GM channel; for a channel-10 drum kit this either silently
mis-routes to a melodic channel or drops the event depending on
the SoundFont's channel mapping. The patched dispatcher reads the
target channel from the profile identity, rewrites the MIDI to
strip any inbound program-changes, and injects a
`program_change(channel=<channel>, program=<program>, time=0)` at
tick 0.

The regression discipline for a replay-engine change requires that
every prior anchor whose MIDI is exercised by the new code path
reproduces byte-identical. Because the bass MIDI is
channel-0-only, the `_replay_sf2` extension collapses to the
pre-patch behaviour on that input; the bass-v2 anchor
`832868d0ea8a81cab2569e60445f80d516d1b5bb958b1b8b0c2e996bdb3aeac5`
is reproduced exactly. The drums anchor is a new render on a new
code path; it is captured in the drums replay proof
(`drums.replay_proof.json`) with `run1 = run2 =
dadafcfc0153f002651c23975c3845dd3f8ca7896d263faf1c52eb54d64b8d7c`
under the canonical seven-key environment pin. The proof file
carries a `bass_regression_check` block that pins the bass-v2
byte-identity outcome explicitly.

Post-patch `replay.py` SHA is `1f43027039c45f5e066c…`. This file
becomes a read-only anchor from cycle 11 forward; any subsequent
change to the replay engine must pass a regression check against
both the bass-v2 and drums anchors (and, from cycle 12, the
family-2 drums anchor as well).

### 3.3 Family verdict

The stage-2 leaderboard was scored against the pre-registered
decision protocol. The CONFIRMED gate (embedding-cosine
$\geq 0.60$ and stage-2 spread $\geq 10\%$ of the cycle-10 coarse
spread) is met on the spread clause (176.7 % ≥ 8.97 %) but not on
the embedding clause (0.2374 < 0.60). The retained absolute
RULED_OUT floor (embedding-cosine $\leq 0.40$) is satisfied
(0.2374 ≤ 0.40). Verdict: **`SF2_RULED_OUT`**.

`drums_family_verdict.json` records the outcome as a first-class
negative finding rather than a failure. In particular it discloses
the honesty context that would otherwise be hidden by a
composite-only summary:

| honesty disclosure | value |
|---|---|
| top-1 embedding-cosine (Power Kit, prog 16) | 0.2374 |
| max embedding-cosine across all 216 stage-2 cells | 0.4645 (program 48 Orchestra Kit, composite rank 76) |
| program 0 Standard Kit best/worst rank | 13 / 216 |
| distinct render SHAs across 216 cells | 216 / 216 |
| EQ v2 zero-mean removal effective | yes |

The verdict pins the decision-protocol scope: the composite-relative
WINNER extension that the operator authorised for Chicken Grease
bass at cycle 9 is explicitly scoped to `STILL_INDETERMINATE`
outcomes and does **not** rescue a `RULED_OUT` — the retained
0.40 floor is a hard honesty gate. Any attempt to accept the
Power Kit as-is would require an explicit operator scope
extension.

The verdict also names a parallel to the cycle-1 bass surprise
(where the frozen composite preferred a Drawbar Organ over any
bass program): the same objective on Chicken Grease drums prefers
the Power Kit over the Orchestra Kit and both over the Standard
Kit, none of which reach the CONFIRMED gate. The pattern is
recorded as a systematic characterisation of the objective on
Chicken Grease content, not a defect.

The cycle-11 auditor raised one moderate finding: the
channel-aware replay fix had been reproduced by the worker but
had not yet been re-run from an independent Python subprocess
under the same environment pins — the strongest form of the
regression check. That finding was scheduled for cycle-12
closure.

## 4. Cycle 12 — family-2 arc, arc closeout, and independent replay regression

Cycle 12 ran three concurrent tracks that closed the drums arc
cleanly.

### 4.1 Independent replay-regression verification

A stand-alone harness `_replay_regression_c12.py` was written to
close the cycle-11 moderate. It forks a fresh Python subprocess for
each anchor (so it inherits none of the parent's imported state),
sets the seven-key canonical environment pin, replays the target
profile into a fresh temporary directory, computes the SHA of the
resulting WAV, and repeats the entire flow a second time into a
second temporary directory. The harness targets both the bass-v2
anchor and the new drums anchor.

The verdict (`_replay_regression_c12.json`) is
**`REPLAY_REGRESSION_HOLDS`**. Both anchors reproduce byte-identical
across two fresh-subprocess runs and match the anchor SHAs on file:

| label | run 1 SHA | run 2 SHA | anchor match |
|---|---|---|---|
| bass_v2 | `832868d0…aeac5` | `832868d0…aeac5` | ✓ |
| drums | `dadafcfc…64b8d7c` | `dadafcfc…64b8d7c` | ✓ |

The harness also caught a transcription error in its own inbound
research brief: the brief had pinned the drums anchor with a wrong
tail (first 16 hex characters `dadafcfc0153f002` correct, remainder
divergent). The harness cited the on-disk canonical value from
`drums.replay_proof.json`, disclosed both variants in a
`brief_anchor_discrepancy_note` block, and reproduced the on-disk
value byte-identical rather than retro-fitting to the incorrect
value. The cycle-12 auditor re-ran the same harness independently
from its own fresh subprocess and reproduced both anchor SHAs,
validating the closure.

### 4.2 Family-2 stem-sampled drums arc

The family-2 shape probe (`family2_stem_sampled_drums_spike.py`,
144 lines) detected 147 onsets in the reference drums stem over a
6.9 s window and classified them by a band-energy argmax into
kick / snare / hihat buckets. The spike verdict was `VIABLE`, but
the classifier produced an asymmetric class distribution
(kick 93, snare 0, hihat 53) versus the MIDI-side pitch histogram
(kick 30, snare 33, hihat 123). This asymmetry was surfaced in the
spike JSON rather than smoothed over.

The builder (`family2_stem_sampled_drums_builder.py`, 271 lines)
rendered the drums MIDI concatenatively by MIDI-pitch → sample-class
dispatch (pitch 36 → kick sample, pitches 37–38 → snare, pitches
42/44/46 → hihat) using the sample bank that the spike had
extracted from the reference stem. The render is
`drums_family2_render/render.wav`, 2 678 664 bytes, SHA
`69a76c5b4498972d1cb878da94e645c8c341675b113cc4ca315435f6bb16ca00`.

Because family-2 is a distinct render family from SoundFont under
the file-determinism policy FD-16(c), it requires its own replay
proof. `drums_family2.replay_proof.json` records `run1 = run2 =
69a76c5b…16ca00` under the canonical seven-key pin. This single
proof covers the family-2 code path for all future stem-sampled
CG drums profiles.

The family-2 profile of record is `drums_family2_v1.json`, UUID
`13aeeea0-934e-5b4c-9a7a-e69e1c0e5fc4`. Scored against the frozen
composite:

| field | value |
|---|---|
| composite | 618.16 |
| mel-L1 | 13.41 dB |
| spectral-centroid RMSE | 2442.08 Hz |
| embedding-cosine (VGGish) | 0.0372 |

The verdict is **`FAMILY2_RULED_OUT`**: embedding-cosine 0.0372 is
well below the 0.40 retained honesty floor. This is the second
family-2 verdict on Chicken Grease content and is even lower than
the cycle-6 family-2 bass score of 0.0896.

A minor observation was recorded for future revisit: the
family-2 profile's `params.classifier` field names the band-energy
spike-side classifier used to *extract* the sample bank, but the
builder's *render-time dispatch* is by MIDI pitch class rather
than by band energy. Both routings are internally consistent, but
the field name is imprecise; a companion `params.render_dispatch`
field would disambiguate. Non-blocking because the arc closes on
`RULED_OUT`.

### 4.3 Arc closeout and manager escalation

With both frozen render families ruled out, the drums arc is
formally closed in `drums_arc_closeout.json` under the verdict
**`CG_DRUMS_ARC_EXHAUSTED_NO_CONFIRMED`**. The closeout parallels
the cycle-7 bass arc closeout in shape:

| dimension | cg-bass (c7) | cg-drums (c12) |
|---|---|---|
| SoundFont top-1 embedding-cosine | 0.4946 (prog 33 Electric Bass Finger) | 0.2374 (prog 16 Power Kit) |
| SoundFont max embedding-cosine across 216 | 0.4946 (prog 19 Church Organ) | 0.4645 (prog 48 Orchestra Kit, composite rank 76) |
| SoundFont verdict | `STILL_INDETERMINATE` | `SF2_RULED_OUT` |
| family-2 embedding-cosine | 0.0896 | 0.0372 |
| family-2 verdict | `FAMILY2_RULED_OUT` | `FAMILY2_RULED_OUT` |
| resolution | operator OPT1+OPT3 hybrid at c9 | manager escalation to operator; no unilateral acceptance |

The closeout carries a `cross_song_parallel_findings` block naming
the bass precedent and a `systematic_finding` block characterising
the pattern: the concatenative stem-sampled render approach as
currently implemented (fixed windows, per-class sample bank
without pitch modelling) is architecturally insufficient to reach
the 0.40 floor on Chicken Grease content across two independent
instrument families. If the pattern holds, piano, guitar, and
other-residual arcs are likely to exhaust similarly and require
comparable operator adjudication.

The drums acceptance policy is escalated to operator authority in
`_manager_M-V4-SHOWCASE-1-cg-drums-acceptance-policy.json` with
three named options:

| option | label | consequence |
|---|---|---|
| OPT1 | Accept SoundFont top-1 as drums WINNER via composite-relative extension | requires operator threshold-retirement scope extension; the cycle-9 retirement is scoped to bass only |
| OPT2 | Accept SoundFont max-embedding-cosine candidate (embedding-first tiebreak) | small cost: single fine-fit lookup + one render + one replay proof for program 48 Orchestra Kit (embedding-cosine 0.4645); does not require composite-relative extension |
| OPT3 | Refuse drums showcase; deliver Chicken Grease A/B without drums recreation | delivers with four instruments (bass_v2 + piano + guitar + other-residual, once profiled) using original htdemucs drums stem |

Unlike cycle 9 — where the agent had unilaterally chosen to accept
the composite-relative WINNER for bass after receiving the operator
directive — the cycle-12 escalation explicitly declines to
pre-empt. The escalation JSON pins
`unilateral_action_taken_this_cycle = "NONE"` and instructs the
next cycle to wait on operator input in `live_guidance`. The reason
is that the cycle-9 operator directive scoped the threshold
retirement to Chicken Grease bass by name; extending it to drums is
a scope decision, not a mechanical follow-through.

### 4.4 Ledger discipline

Nine ledger events were emitted at cycle 12 in strict timestamp
order (00:20 UTC through 00:51 UTC): the family-2 profile, replay
proof, verdict, arc closeout, manager escalation, replay
regression, the plan-of-record registration
(`_plan/register-c12-cg-drums-family2-sub-leaves`), and two
housekeeping entries (`_archive/cycle-12-scratch`,
`_infra/adopt-cycle12-tests`). Every event carries a UUID5
identifier and the manager escalation is emitted with
`status: action_required` as required by the state machine.

## 5. Findings closed across the batch

| finding | opened | closed | resolution |
|---|---|---|---|
| disk-check false positive halts drums sweep | c9 | c10 | `_disk_ok()` rewritten to absolute-budget formula; regression test pins the c9 scenario |
| replay engine not exercised on non-channel-0 program | c10 | c11 | `replay.py` L79–93 channel-aware fix; drums renders replayable; bass-v2 byte-identity preserved |
| channel-aware fix not independently re-verified from fresh subprocess | c11 | c12 | `_replay_regression_c12.py` reproduces bass-v2 and drums anchors byte-identical from fresh subprocesses; auditor independently re-runs and reproduces both |

The cycle-12 auditor's own severity tally was **CRITICAL 0,
MODERATE 0, MINOR 2**. The two minor observations — the
spike-vs-builder classifier-nomenclature drift and the
zero-snare asymmetry in the band-energy classifier — are recorded
in the cycle-12 verdict artefacts and do not gate the arc close.

## 6. Systematic finding across cycles 1–12

Two consecutive Chicken Grease instrument arcs have exhausted the
two frozen render families without reaching the 0.60 CONFIRMED
gate:

| instrument | SoundFont top-1 emb-cos | family-2 emb-cos | resolution |
|---|---|---|---|
| bass | 0.4946 | 0.0896 | operator OPT1+OPT3 hybrid (c9) |
| drums | 0.2374 | 0.0372 | escalation to operator, three named options (c12) |

Family-2 stem-sampled underperforms family-1 SoundFont on
Chicken Grease content by roughly an order of magnitude in
embedding cosine on both instruments. The cycle-12 arc closeout
records this as a characterisation of the objective and the
render families on this piece of source content, not as a defect
of any single component. The convergent expectation is that
piano, guitar, and other-residual will follow the same pattern
and each require operator adjudication of an acceptance policy;
each such adjudication is honest and non-idle, and the campaign
converges even under the pattern.

## 7. Audit-cycle trajectory

The three audits landed cleanly in a convergent trajectory:

| audit | severity summary | closure |
|---|---|---|
| cycle-10 | 1 MODERATE (channel-aware replay coverage gap) | closed cycle 11 |
| cycle-11 | 1 MODERATE (independent from-fresh-subprocess re-verify) | closed cycle 12 |
| cycle-12 | 0 MODERATE, 2 MINOR | non-blocking; carried as observations |

The cycle-12 auditor explicitly re-ran the cycle-12
replay-regression harness from an independent Python subprocess
under the canonical seven-key pin and reproduced both anchor SHAs
byte-identical, which is the strongest form of the Track-1
verification: the worker's report is validated by execution, not
by re-reading their claim.

## 8. Cycle-13 scope

1. Register the drums acceptance-policy outcome. If an operator
   directive arrives, apply it verbatim and pin the resulting
   drums delivery profile. If none arrives, the cycle-9 banned-
   heartbeat rule instructs the agent to pick the option most
   consistent with the binding specifications and best objective
   evidence, disclose the acceptance-fork in the plan of record
   verbatim, and proceed; the cycle-12 auditor guidance names
   OPT1 as consistent with the cycle-9 pattern and OPT2 as the
   embedding-first alternative that does not require scope
   extension.
2. Open the Chicken Grease piano SoundFont coarse sweep as a
   direct sibling of `coarse_sweep_sf2.py` and
   `coarse_sweep_sf2_drums.py`. GM programs 0–7 and 16–19,
   MIDI channel 1, standard 500 MB working-audio budget and
   `--score-and-delete --keep-top 3` hygiene.
3. Back-fill accumulated test debt for the family-2 drums
   concatenative render path — a dedicated
   `tests/test_sound_match_family2_drums.py` pinning the
   family-2 render SHA `69a76c5b…` would close three cycles of
   honestly-deferred test coverage cheaply.

Read-only anchors that must be preserved: `M-V4-CERT-1`,
`bass.json`, `bass_v2.json`, both bass family verdicts, the bass
arc closeout, `drums.json`, `drums.replay_proof.json`,
`drums_family_verdict.json`, `drums_family2_v1.json`,
`drums_family2.replay_proof.json`, `drums_family2_verdict.json`,
`drums_arc_closeout.json`, and the frozen script set in
`scripts/sound_match/` (`coarse_sweep_sf2*.py`,
`fine_fit_sf2*.py`, `family2_stem_sampled_*.py`, `replay.py`).
The 0.60 CONFIRMED and 0.40 RULED_OUT thresholds remain in
force globally; the cycle-9 threshold retirement is scoped to
Chicken Grease bass only.

## Appendix: Implementation Details

### A.1 Files created or extended, cycles 10–12

*Scripts (`scripts/sound_match/`)*:

| file | cycle | lines | role |
|---|---|---|---|
| `coarse_sweep_sf2_drums.py` | patched 10 | 446 | `_disk_ok()` rewritten to absolute-budget check |
| `_launch_cg_drums_sweep_c10.sh` | 10 | — | detached launcher for the drums coarse sweep |
| `fine_fit_sf2_drums.py` | 11 | 679 | 216-cell drums stage-2 fine-fit, channel-10 aware |
| `_launch_cg_drums_stage2_c11.sh` | 11 | — | detached launcher for the drums stage-2 fine-fit |
| `replay.py` | patched 11 | 166 | channel-aware `_replay_sf2` extension; post-patch SHA `1f43027039c45f5e066c…` |
| `family2_stem_sampled_drums_spike.py` | 12 | 144 | family-2 shape probe, band-energy classifier |
| `family2_stem_sampled_drums_builder.py` | 12 | 271 | family-2 concatenative render, MIDI-pitch dispatch |
| `_family2_drums_score_and_emit_c12.py` | 12 | — | scoring + profile + replay-proof + verdict emitter |
| `_family2_drums_closeout_and_escalation_c12.py` | 12 | — | arc closeout + manager escalation emitter |
| `_replay_regression_c12.py` | 12 | — | independent from-fresh-subprocess Track-1 harness |
| `_emit_c12_ledger_events.py` | 12 | — | cycle-12 ledger-event emitter |

*Tests (`tests/`)*:

| file | cycle | role |
|---|---|---|
| `test_coarse_sweep_disk_check.py` | 10 | pins the absolute-budget formula and asserts the c9 false-positive scenario |
| `test_rc10_drums_bass.py` | 10 | drums-plus-bass cross-check under channel-aware replay |
| `test_rc10_drums_v2.py` | 10 | drums-family stage-2 leaderboard structural test |
| `test_verdict_sha_fields_resolve_on_disk.py` | 12 | asserts every SHA field in a verdict/manifest resolves byte-identical on disk |

### A.2 Data artefacts, cycles 10–12

All under `data/v4/profiles/31a164f845f8e27e/` unless noted.

| file | cycle | notes |
|---|---|---|
| `drums_sweep_stage1/leaderboard.tsv` | 10 | 15-preset SoundFont drums coarse-sweep leaderboard, SHA `dd5544d3bd3a549cab95…` |
| `drums_sweep_stage1/drums_excerpt.mid` | 10 | channel-10 drums MIDI, 186 note-on events, SHA `0fd71ce70a26365c2acf…` |
| `drums_sweep_stage2/leaderboard.tsv` | 11 | 216-cell drums stage-2 leaderboard, SHA `81a441732f7f7d1da615…`, composite spread 176.7 % |
| `drums.json` | 11 | drums profile, UUID `83728154-6f48-5c5d-a558-b4d82523ac1b`, program 16 Power Kit, embedding-cosine 0.2374 |
| `drums.replay_proof.json` | 11 | `run1 = run2 = dadafcfc…64b8d7c`; embeds bass-v2 regression PASS |
| `drums_family_verdict.json` | 11 | **`SF2_RULED_OUT`**; disclosure block names max-emb-cos 0.4645 at prog 48 rank 76 |
| `drums_family2_spike_c12.json` | 12 | shape-probe verdict `VIABLE`; 147 onsets, kick 93 / snare 0 / hihat 53 |
| `drums_family2_v1.json` | 12 | family-2 profile, UUID `13aeeea0-934e-5b4c-9a7a-e69e1c0e5fc4`, canonical replay SHA `69a76c5b…16ca00` |
| `drums_family2.replay_proof.json` | 12 | `run1 = run2 = 69a76c5b…16ca00`; covers family-2 code path per FD-16(c) |
| `drums_family2_render/render.wav` | 12 | 2 678 664 B family-2 concatenative render |
| `drums_family2_verdict.json` | 12 | **`FAMILY2_RULED_OUT`**, embedding-cosine 0.0372 |
| `drums_arc_closeout.json` | 12 | **`CG_DRUMS_ARC_EXHAUSTED_NO_CONFIRMED`**; parallels cycle-7 bass closeout shape |
| `_manager_M-V4-SHOWCASE-1-cg-drums-acceptance-policy.json` | 12 | three named options (OPT1/OPT2/OPT3); `authority = OPERATOR`; `unilateral_action_taken_this_cycle = NONE` |
| `_replay_regression_c12.json` | 12 | **`REPLAY_REGRESSION_HOLDS`**; bass-v2 and drums both byte-identical, discloses brief-vs-on-disk tail discrepancy |
| `_c12_track3_summary.json`, `_c12_track4_summary.json` | 12 | per-track sub-milestone summaries |

### A.3 Environment pins in force

The canonical seven-key replay-time pin
`2ac444c36298d6ada0579aba1a9160a5881703a4e628f5cccdd828b842a922ca`
covers every cycle-10–12 render, replay proof, verdict, and
regression check without change. It comprises: `LC_ALL=C.UTF-8`,
`MKL_NUM_THREADS=1`, `OMP_NUM_THREADS=1`,
`OPENBLAS_NUM_THREADS=1`, `PYTHONHASHSEED=0`,
`SOURCE_DATE_EPOCH=1756463424`, `TZ=UTC`. The cycle-11
`replay.py` patch was verified to leave the pin unchanged, and the
cycle-12 independent regression re-verified pin, replay engine,
and anchor SHAs jointly.

### A.4 Read-only anchors preserved

Every prior anchor exercised by cycles 10–12 was re-checked at
audit time and found byte-identical. Highlights:

| anchor | SHA (prefix) | status |
|---|---|---|
| `coarse_sweep_sf2.py` (c1) | `c74c35bc…` | unchanged |
| `fine_fit_sf2_v2.py` (c3) | `dc03007365aa29be…` | unchanged |
| `family2_stem_sampled_spike.py` (c5) | `000c3ef68042f2da6971…` | unchanged |
| `family2_stem_sampled_builder.py` (c6) | `eaa8fb6cb513f342ff71…` | unchanged |
| `replay.py` post-c11 | `1f43027039c45f5e066c…` | unchanged after cycle 11 |
| `stems_6s/drums.wav` | `34492c03f301b6eac3a7…` | unchanged (5 292 044 B) |
| `bass_v2.json` and its replay proof | UUID `d62cd3b6…`, replay SHA `832868d0…aeac5` | unchanged; re-reproduced from fresh subprocess at cycle 12 |
| `bass.json`, `bass_family2_v1.json`, both bass verdicts, bass arc closeout | — | unchanged |
| `FluidR3_GM.sf2` | `74594e8f4250680adf59…` | unchanged |

### A.5 Session references

| cycle | role | session UUID |
|---|---|---|
| 10 | researcher | `67b28d09-ab6b-4c0d-9124-7bc40b5f8b50` |
| 10 | worker | `a46ecebe-098f-47fc-9300-19b34d7f7efe` |
| 10 | auditor | `64ee51ec-9d3b-4512-8f48-0da0c0b79bd4` |
| 11 | researcher | `bcd69ec4-e2f0-4ecf-a989-685050638d1d` |
| 11 | worker | `e90ba69e-0719-4c6c-ae14-4fcdb1c07b60` |
| 11 | auditor | `08439cb4-82d7-4539-9f85-7e2117eb4f54` |
| 12 | researcher | `d07132e4-c307-47c7-a8ee-826ef68184cb` |
| 12 | worker | `1771d189-b272-437c-beab-eae25e55920a` |
| 12 | auditor | `c7ac41d8-ccea-4cde-b324-0abe9dba166d` |

### A.6 Cross-reference map

- cycle-9 disk-check false positive → cycle-10 `_disk_ok()` rewrite
  + `test_coarse_sweep_disk_check.py` → cycle-10 detached
  `coarse_sweep_sf2_drums.py` launch → `drums_sweep_stage1/`
- cycle-10 stage-1 leaderboard → cycle-11 `fine_fit_sf2_drums.py`
  → `drums_sweep_stage2/leaderboard.tsv` → `drums.json`
- cycle-10 auditor moderate (channel-0-only replay coverage) →
  cycle-11 `replay.py` L79–93 patch → cycle-11
  `drums.replay_proof.json` (with embedded bass-v2 regression
  block)
- cycle-11 auditor moderate (independent re-verify) → cycle-12
  `_replay_regression_c12.py` → `_replay_regression_c12.json`
  verdict `REPLAY_REGRESSION_HOLDS` → cycle-12 auditor
  independent re-run reproduces both anchors
- cycle-11 `drums_family_verdict.json` (`SF2_RULED_OUT`) +
  cycle-12 `drums_family2_verdict.json` (`FAMILY2_RULED_OUT`) →
  cycle-12 `drums_arc_closeout.json`
  (`CG_DRUMS_ARC_EXHAUSTED_NO_CONFIRMED`) → cycle-12
  `_manager_M-V4-SHOWCASE-1-cg-drums-acceptance-policy.json`
  (three named options, operator authority) → cycle-13
  acceptance-policy resolution
- cycle-7 bass arc closeout shape → cycle-12 drums arc closeout
  shape (parallel structure); cycle-9 operator directive scope
  ("Chicken Grease bass") → cycle-12 escalation refuses
  unilateral scope extension
