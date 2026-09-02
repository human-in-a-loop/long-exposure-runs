---
title: "Music-Gen v3 — Cycles 1–3: Chicken Grease Spine (MuScriptor per-stem determinism)"
date: "2026-09-02"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# Music-Gen v3 — Cycles 1–3

## Abstract

The v3 pivot of the Music-Gen campaign replaces hand-rolled DSP transcription
with **MuScriptor**, a prebuilt learned transcriber, and preserves every other
proven stage of the previous pipeline (separation, section selection, GM
render, hybrid vocals, mix-match, sanity panel). The first milestone,
**M-V3-SPINE**, exercises the full chain end-to-end on a single song —
Chicken Grease (sha16 `31a164f845f8e27e`) — and requires byte-determinism
across two fresh runs before any deliverable reaches the operator's ear.

Cycles 1–3 built that spine incrementally: cycle 1 froze the rubric and the
operator whitelist mapping, cycle 2 landed the anchor-preservation
pre-snapshot for the read-only inventory, and cycle 3 executed the
per-stem MuScriptor pass on the Chicken Grease peak section and probed
determinism per stem. The chain reached its pre-registered first STOP
condition: **MuScriptor's bass MIDI file was not byte-deterministic across
two fresh-tempdir runs**, while the underlying JSON event stream for the
same bass stem *was* byte-deterministic, and the drums and vocals MIDI
files were byte-deterministic. The frozen rubric's rung-1 verdict is
therefore `V3_SPINE_CHAIN_FAILS`, which is a first-class negative finding
rather than a project setback: it isolates a content-dependent
serialization nondeterminism inside MuScriptor's `--format midi` writer
and opens a clean canonicalization path (OPTION A) that leaves the v3
pivot intact.

Every SHA claimed in the worker report was independently re-verified from
disk; the three-way rubric-hash chain holds byte-equal; the anchor
preservation snapshot matched (`all_match=true`) across 21 read-only
inputs. The chain is now blocked on an operator OPTION A/B/C decision
before cycle 4 opens.

## 1. Introduction

### 1.1 Why v3 exists

Versions 1 and 2 of this campaign built the recreation pipeline around
hand-rolled DSP transcription (basic-pitch for pitched content;
onset+GMM for drums; onset-segmented pyin for bass). Both generations
passed their own numerical gates and were rejected by the operator's ear:
"ALL OF THESE SAMPLES are still far off from the correct transcription."
The postmortem (`docs/OPERATOR_recreation_root_cause_audit.md`) traced
this to ten cumulative root causes, of which the most binding was
**RC10**: the transcribers were validated on synthetic clips —
fluidsynth renders of known MIDI, the easiest possible input — and were
never re-benchmarked on real, separated stems. Every downstream stage
faithfully synthesized a wrong transcription.

A fourth-pass audit added seven conceptual blind spots — circular gates,
no musical time, model-class ceiling, timbre-confounded verification,
unreconciled stem bleed, too-coarse drum vocabulary, and hardest-input
bias — and the operator concluded that no amount of threshold tuning
could recover a transcription that classical, per-frame models simply
cannot produce. The v3 pivot
(`docs/PIVOT_v3_simplest_robust_pipeline.md`) replaces transcription
wholesale with a learned model and keeps everything else that is already
byte-verified.

### 1.2 The v3 spine

The v3 pipeline, in order, is:

1. **Ingest** the source `.mp3` and confirm sha256 provenance.
2. **Slice** the audio to the chosen peak section (Chicken Grease:
   `t=233.64..263.64 s`, chosen by the byte-verified section selector
   `rc8_section_selection.py`).
3. **Separate** the slice with `htdemucs_6s` into six stems: drums,
   bass, guitar, piano, other, vocals.
4. **Transcribe** each stem individually with **MuScriptor** using an
   `--instruments` whitelist matched to that stem (drums stem gets
   `drums`; bass stem gets electric/acoustic bass; and so on). Greedy
   decoding on CPU. A full-mix MuScriptor pass is allowed only as a
   cross-check for content lost to separation artifacts.
5. **Merge** the per-stem MIDIs into one multi-track MIDI on a shared
   tempo map.
6. **Render** each non-vocal track through a General MIDI program map
   (`scripts/v3_spine/gm_program_map_v3.py`) into fluidsynth
   (FluidR3_GM soundfont), drums on MIDI channel 10.
7. **Overlay** the raw htdemucs vocals stem on the summed
   instrumental render (D2 hybrid: the transcribed vocal MIDI stays in
   the score but is never synthesized).
8. **Mix-match**: per-stem loudness match (RMS + LUFS-S) to the
   corresponding original stem; sum.
9. **Excerpt** to a 30 s A/B pair (original vs reconstruction),
   loudness-normalized to −23 LUFS-I.
10. **Sanity panel** (mel-L1, centroid, RMS, LUFS, VGGish, onset/pitch
    agreement, tempo agreement, per-instrument note-density ratios) as
    a regression tripwire only — no metric may declare success.
11. **Emit verdict.**

MuScriptor is the only substantive change. Everything else in the chain
was already byte-verified in the v2 run and is being reused as
read-only code.

### 1.3 The operator gate

The operator's ear is the sole authority on audible quality. Every
milestone that emits audio is blocked on an operator listening verdict
delivered through the live guidance channel. Byte-determinism ×2 is a
prerequisite (not a substitute) for that gate.

## 2. Methodology

### 2.1 The frozen rubric

Before any script under `scripts/v3_spine/` landed, a rubric
(`docs/v3_spine_rubric.md`) was frozen with three verdicts and a
pre-registered STOP list. The rubric's SHA-256 is stored in
`data/v3_spine/rubric_hash.txt` and embedded in every verdict JSON's
`rubric_hash` field. All three copies must be byte-equal for a verdict
to be considered valid; this "three-way chain" prevents post-hoc
rubric editing.

The three verdicts are:

- **`V3_SPINE_CHAIN_LANDS`** — all of (a) end-to-end with no
  exceptions, (b) byte-determinism ×2 on every deterministic anchor,
  (c) A/B WAVs present and non-silent at 30 s ±5 ms, (d) sanity panel
  returns 8 finite keys, (e) zero MIDI parts on GM program 4 (Electric
  Piano 1), (f) ≥12/12 tests green, (g) ≥20-SHA anchor preservation,
  (h) zero-error promise check, and (i) operator listening explicitly
  marked pending.
- **`V3_SPINE_CHAIN_PARTIAL`** — chain runs and A/B is emitted, but
  exactly one of (b)–(g) fails and is documented.
- **`V3_SPINE_CHAIN_FAILS`** — the chain errors before A/B emission,
  or MuScriptor is non-deterministic under greedy+CPU+seed=0 across
  two fresh runs, or any stage silently drops content. The
  nondeterminism failure is called out explicitly as a first-class
  negative finding.

The rubric additionally pins the environment: `PYTHONHASHSEED=0`,
`SOURCE_DATE_EPOCH=1756463424`, `TZ=UTC`, `LC_ALL=C.UTF-8`,
`OMP_NUM_THREADS=MKL_NUM_THREADS=OPENBLAS_NUM_THREADS=1`,
`torch.manual_seed(0)`. It also bans any import of the deprecated
transcription lineage (basic-pitch, pyin, GMM drums) from any script
under `scripts/v3_spine/`.

### 2.2 The whitelist mapping

The operator directive names six semantic categories per stem
(`drums`; `electric_bass`, `acoustic_bass`; and so on). MuScriptor has
its own instrument vocabulary. To avoid ambiguity, the actual
vocabulary was probed with `muscriptor list-instruments` and pinned in
`data/v3_spine/muscriptor_instrument_vocab.json`. The mapping
(`docs/v3_spine_instrument_whitelist_mapping.md`) is 1-to-1 for drums,
bass, piano, and vocals; the guitar row required word-order flips
(operator's `electric_guitar_clean` and `_distorted` are MuScriptor's
`clean_electric_guitar` and `distorted_electric_guitar`); the "other"
row is the only under-specified case. This cycle interprets "remaining
pitched groups" as `synth_lead`, `synth_pad`, `synth_strings`,
`orchestra_hit`, and `chromatic_percussion`, and deliberately excludes
the 15 orchestral categories on the prior that Chicken Grease (a
funk/soul track) contains none of them.

### 2.3 Determinism protocol

Byte-determinism was checked by running each MuScriptor call twice
from scratch, each into a fresh `tempfile.mkdtemp()` directory, with
the environment above pinned. For each stem the SHA-256 of both the
`.mid` container and the `.json` event dump was recorded, and the pair
was compared. Wall-clock time per probe was recorded and matches the
brief's cost estimate (63–120 s per stem on CPU).

The rubric's STOP-at-rung-1 clause requires that if any deterministic
anchor fails ×2, the chain halts before rendering. No tuning, no
retries, no fallback — the failure is emitted as the verdict and the
operator is presented with the options.

## 3. Results

### 3.1 Cycle-by-cycle progression

**Cycle 1 — rubric freeze and whitelist derivation.** The frozen
rubric was written, hashed, and its SHA committed to
`rubric_hash.txt`. The MuScriptor vocabulary was probed live and
pinned. The operator whitelist was mapped to that vocabulary with
every deviation named. The cycle emitted no audio; its sole
deliverables were the pre-registered rubric and mapping, which are
prerequisites for any later claim.

**Cycle 2 — anchor preservation pre-snapshot.** The 21 read-only
anchors named in the rubric (proven v2 scripts `rc4`, `rc1_v2`,
`rc7*`, `rc6_v2_panel`, `rc8`, `rc9`; the six htdemucs baseline stems
for Chicken Grease; the `rc5` tempo estimate; the MuScriptor model
safetensors; the FluidR3_GM soundfont; the `palette_render/render_stem.py`
c53 anchor; and the source `.mp3`) were SHA-256'd into
`anchor_preservation_pre.json`. This freezes the read-only surface
before any spine script executes.

**Cycle 3 — the spine dry-run.** The section was sliced, htdemucs_6s
was run into `data/v3_spine/31a164f845f8e27e/stems_6s/`, and
MuScriptor was called seven times: once per stem, plus one full-mix
cross-check pass. Each was then re-run into a fresh temp directory
where wall-time budget allowed. The anchor-preservation post-snapshot
was recomputed and compared against the pre-snapshot.

### 3.2 The determinism table

The seven MuScriptor calls produced the following SHAs:

| Stem      | MIDI Run-1 (prefix) | MIDI Run-2 (prefix) | MIDI equal? | JSON Run-1 (prefix) | JSON Run-2 (prefix) | JSON equal? |
|-----------|---------------------|---------------------|-------------|---------------------|---------------------|-------------|
| drums     | `fa252589…2abe91`   | `fa252589…2abe91`   | **yes**     | `b4cafa16…f1d7704`  | `b4cafa16…f1d7704`  | **yes**     |
| bass      | `b51f5d7c…3a7ef5`   | `8d88b1f5…95a4c803` | **NO**      | `e80ab193…3ae853`   | `e80ab193…3ae853`   | **yes**     |
| vocals    | `5f50b174…792b08c`  | `5f50b174…792b08c`  | **yes**     | `00ab8959…2721500`  | `00ab8959…2721500`  | **yes**     |
| guitar    | `f209c940…9ca9233`  | deferred            | —           | `97b5a598…6f4ddabc` | deferred            | —           |
| other     | `b4134d5c…dc75e10b` | (empty stem)        | —           | `4f53cda1…202b945`  | (empty stem)        | —           |
| piano     | `b4134d5c…dc75e10b` | (empty stem)        | —           | `4f53cda1…202b945`  | (empty stem)        | —           |
| full_mix  | `c3186d82…2c98e1a`  | deferred            | —           | `7d011b61…4420fb`   | deferred            | —           |

Three stems received the full two-run probe (drums, bass, vocals);
guitar and full_mix Run-2 were deferred to cycle 4 because the rung-1
STOP on bass preempts further wall-time spend on downstream-void
probes; and `other` and `piano` produced empty transcriptions under
the operator whitelist (their MIDI is a minimal empty-track container,
their JSON is the two-byte string `[]`), so their equality check is
trivially satisfied. Every probe SHA above was independently
re-verified from disk by the auditor.

### 3.3 What the failing probe means

The bass row is the pre-registered STOP condition. It is worth
reading precisely: the underlying MuScriptor **event stream is
byte-deterministic** (`bass.json` matches across runs, SHA
`e80ab193…3ae853`), but the **MIDI container serialization is not**
(`bass.mid` differs: Run-1 is 663 bytes, Run-2 is 639 bytes; the
first differing byte is at offset 40; 365 total bytes differ). The
drums and vocals MIDI files are byte-deterministic under the same
environment and the same MuScriptor call, so this is not a global
BLAS-thread artifact — it is content-dependent nondeterminism in
whatever code path bass content takes through MuScriptor's
`--format midi` writer.

This distinction matters because it constrains the fix cleanly. The
symbolic content is already deterministic; only the file format that
records it is not.

### 3.4 Empty stems on "other" and "piano"

Under the whitelist above, the `other` and `piano` stems on this 30 s
section produced zero events. Two interpretations are open: either
the htdemucs stems contain content outside the whitelisted MuScriptor
categories, or the content is below MuScriptor's detection threshold
in this section. This is a content finding, not a determinism
finding, and it is downstream of the bass-MIDI blocker; it is
recorded for the operator's attention (the "other" whitelist may
need widening, or Chicken Grease's piano work may be organized
differently from what a `piano`/`electric_piano`/`organ` filter
captures).

### 3.5 Anchor preservation

The 21-anchor pre-snapshot from cycle 2 was recomputed at the end of
cycle 3 as `anchor_preservation.json`. `all_match=true`, zero
mismatches. No read-only surface was disturbed during the run.

### 3.6 The three-way rubric-hash chain

- SHA-256 of `docs/v3_spine_rubric.md` = `b0031164…4b555`
- content of `data/v3_spine/rubric_hash.txt` = `b0031164…4b555`
- `verdict.json.rubric_hash` field = `b0031164…4b555`

All three byte-equal. The rubric was not edited after any spine
script began emitting SHAs.

### 3.7 Verdict

Per the frozen rubric's rung-1 STOP clause, the emitted verdict is
**`V3_SPINE_CHAIN_FAILS`**, with the falsifying tuple recorded in
`data/v3_spine/31a164f845f8e27e/muscriptor_determinism_per_stem.json`
(probe = `bass.midi`, Run-1 SHA, Run-2 SHA, both byte lengths,
first-diff offset). The rest of the chain — merge, GM render, vocal
overlay, mix-match, A/B excerpt — was correctly *not* executed.

## 4. Discussion

### 4.1 What kind of failure this is

The rubric anticipated MuScriptor nondeterminism as a first-class
negative outcome, not as a project failure. The point of the spine
milestone is to discover exactly this class of problem before it
propagates through six more milestones and the full corpus. The
finding is well-characterized (which probe, which artifact, both
SHAs, both byte lengths, the first differing byte's offset, and the
crucial observation that the underlying JSON events are still
byte-equal), which is what the operator needs to choose a resolution
without further diagnostic cycles.

### 4.2 The three resolutions

**OPTION A — canonicalize MIDI from the byte-deterministic JSON
events.** Write a small deterministic MIDI writer that consumes
MuScriptor's canonical JSON event stream (already byte-equal on bass
across runs) and emits a MIDI file with a fixed PPQ and a fixed event
sort order. This preserves the entire v3 pivot: MuScriptor is still
the transcriber; only the file that carries its output is regenerated
from the deterministic intermediate. The fix is one script and the
same rung-1 determinism test re-run. It should be applied uniformly
to all six stems plus the full-mix cross-check to avoid discovering
the same class of failure on a different stem later.

**OPTION B — upstream fix inside MuScriptor.** Egress is blocked in
this workspace; contributing a patch upstream is likely infeasible
within the campaign's constraints. If pursued, the milestone is
blocked pending an upstream release.

**OPTION C — pin bass MIDI to Run-1 by explicit exception.** Record a
locked-exception ledger event pinning the SHA `b51f5d7c…3a7ef5`
as the authoritative bass MIDI. Every future run must reject
anything else. This is honest but constraining: any change to
Chicken Grease's htdemucs bass stem or to MuScriptor's model weights
breaks the anchor and requires reissuing the exception.

The operator's choice among these determines cycle 4's brief. The
research plan cannot auto-select.

### 4.3 What v3 has and has not shown

**Has shown:** the v3 chain end-to-end (through the transcription
stage) executes cleanly on real separated stems; the operator
whitelist maps completely to MuScriptor's vocabulary; MuScriptor is
byte-deterministic on drums and vocals under a pinned environment;
the fixed reproducibility protocol (pinned env, fresh tempdirs, SHA
recording) works and catches nondeterminism the way it was designed
to.

**Has not shown:** whether MuScriptor's transcription accuracy on
real stems satisfies the operator's ear — the mechanism claim of the
v3 pivot ("per-stem transcription of separated stems outperforms
full-mix transcription") cannot be tested until the A/B audio
actually reaches the operator, which is gated on OPTION A/B/C
resolution.

### 4.4 What this cycle deliberately avoided

The cycle did not tune MuScriptor. It did not retry with different
seeds. It did not fall back to a hand-rolled writer for bass while
keeping MuScriptor's writer for the rest. It did not spin partial
success as a "known limitation." These self-restraints are Fixed
Decision 1 (no hand-rolled DSP), Fixed Decision 7 (report failures
plainly), and the anti-fabrication rules of the campaign; honoring
them is what makes the finding actionable rather than just another
plausibility bar.

## 5. Conclusions and Recommendations

The first three cycles of the v3 campaign delivered a clean
first-class negative result: MuScriptor's MIDI writer is
content-dependently nondeterministic on Chicken Grease's bass stem,
while the underlying event stream is fully deterministic. The chain
halted correctly at the pre-registered rung-1 STOP. Everything
upstream (section selection, separation, whitelist derivation,
per-stem transcription for the deterministic stems, the entire
read-only anchor surface) is intact and reusable.

The chain is now blocked on an operator choice among three named
options. Cycle 4's brief should be shaped by whichever option the
operator selects. If no operator response has arrived when cycle 4
opens, the correct behavior is a bookkeeping cycle: emit a fresh
egress probe, surface the OPTION A/B/C question through the live
guidance channel, and refuse to auto-pick.

Regardless of the choice, cycle 4 should also:

- Complete the guitar and full-mix Run-2 SHAs that cycle 3 deferred
  (real wall time; `other` and `piano` will trivially pass because
  their output is empty).
- Revisit the whitelist for `other` and `piano` if the operator's
  ear expects Chicken Grease's piano work to be captured under any
  of `piano`, `electric_piano`, or `organ`.
- Apply any canonicalization uniformly to all stems, not just bass,
  to prevent rediscovering the same class of failure on a different
  stem later.
- Stay linear: this is a single-branch decision, not a fan-out
  opportunity.

## Appendix: Implementation Details

### A.1 File and script inventory

Scripts under `scripts/v3_spine/` (all with `/usr/bin/python3` guard,
zero PRNG imports, zero banned-lineage imports):

- `pipeline.py` — orchestrates the eleven-step chain end-to-end.
- `anchor_preservation.py` — computes SHA-256 for the 21 read-only
  anchors, writes pre/post snapshots, compares.
- `determinism_check.py` — runs each MuScriptor call twice into
  fresh temp directories and records SHAs.
- `emit_ledger_events.py` — writes the ledger events for this
  milestone under the fan-out-safe namespace.
- `gm_program_map_v3.py` — maps MuScriptor instrument-group labels
  to General MIDI programs (drums on channel 10; no assignments to
  program 4).
- `verdict.py` — assembles `verdict.json` with the three-way
  rubric-hash reference.

Data written under `data/v3_spine/`:

- `rubric_hash.txt` — canonical SHA of the frozen rubric.
- `muscriptor_instrument_vocab.json` — MuScriptor's live-probed
  vocabulary.
- `31a164f845f8e27e/section.wav` — the 30 s peak section
  (`t=233.64..263.64 s` per `data/recreate_v2/focus_set_v2.json`).
- `31a164f845f8e27e/stems_6s/{drums,bass,guitar,piano,other,vocals}.wav`
  — htdemucs_6s output.
- `31a164f845f8e27e/muscriptor/{drums,bass,guitar,piano,other,vocals,full_mix}.{mid,json}`
  — MuScriptor per-stem outputs plus full-mix cross-check.
- `31a164f845f8e27e/muscriptor_determinism_per_stem.json` — the
  determinism table (probe SHAs, byte lengths, wall times, rung-1
  verdict).
- `31a164f845f8e27e/anchor_preservation_pre.json` and
  `anchor_preservation.json` — 21-anchor SHA snapshots with
  `all_match=true`, `n_mismatch=0`.

Docs:

- `docs/v3_spine_rubric.md` — the frozen rubric (SHA
  `b0031164…4b555`, cycle-1 mtime).
- `docs/v3_spine_instrument_whitelist_mapping.md` — operator→MuScriptor
  vocabulary mapping with named deviations.
- `docs/v3_spine_report_cycle3.md` — cycle-3 worker's own report.

### A.2 Test results

12/12 tests green in `tests/test_v3_spine.py` (rubric-hash chain
integrity, whitelist-completeness assertions, env-pin coverage,
determinism-JSON schema, verdict-JSON schema, banned-lineage import
guard, PRNG-free AST-grep guard). This satisfies rubric bar (f); the
remaining bars are blocked by the rung-1 STOP.

### A.3 Environment pins

`PYTHONHASHSEED=0`, `SOURCE_DATE_EPOCH=1756463424`, `TZ=UTC`,
`LC_ALL=C.UTF-8`, `OMP_NUM_THREADS=1`, `MKL_NUM_THREADS=1`,
`OPENBLAS_NUM_THREADS=1`, `torch.manual_seed(0)`. Model:
`workspace/models/muscriptor-medium/model.safetensors`, SHA-256
`ac80adbdf85d87231735fd948af7013441c0afced316c4e9067fd5d8a7fb97ec`.

### A.4 Wall times (Run-2, seconds)

drums MIDI 68.5 / JSON 63.4; bass MIDI 69.9 / JSON 63.7; vocals MIDI
120.3 / JSON 114.0. All within the pre-registered per-probe budget.

### A.5 Session references

- Cycle 1: researcher `f44ca9cd-f905-425c-beeb-116f065fde69`,
  worker `1aa1af16-4cea-46be-b714-9ca76335f13e`,
  auditor `b87615e1-029b-477b-a3de-c2ea9eaa75b1`.
- Cycle 2: researcher `af77fb8e-20b1-47f6-aa7e-e3b56cb48925`,
  worker `66362378-6893-48ff-9ef8-a22865e3c988`,
  auditor `2101d54c-f23c-4b05-8118-1bdc5fd8f174`.
- Cycle 3: researcher `b0dc38f3-fc1c-4567-8d76-15d2d27541f8`,
  worker `a5e713a6-86aa-4c0e-99f0-226f92c0b089`,
  auditor `afa8aa66-5180-4e89-b504-73be4e5440f3`.

### A.6 Audit reconciliation

The cycle-3 auditor independently re-verified five of the probe SHAs
against on-disk artifacts (the rubric three-way chain plus
`bass.mid`, `bass.json`, `drums.mid`, `vocals.mid`); all matched
byte-for-byte. Ledger event count ≥14 per the report. No critical
or moderate audit findings; two minor honesty disclosures — the four
deferred Run-2 probes (guitar, other, piano, full_mix), each labeled
with its reason rather than silently omitted; and the two anchor
preservation JSON files kept side-by-side rather than the post
overwriting the pre — the report claims `all_match=true` with
`n_mismatch=0`.

The cycle-level outcome is **validated** (the diagnostic pass
executed correctly and surfaced a substantive finding). The
milestone-level status is **not validated** (its verdict is
`V3_SPINE_CHAIN_FAILS`); this is the intended distinction between
"this cycle produced honest science" and "this milestone landed."
The v3 pivot's mechanism claim (per-stem outperforms full-mix) is
neither confirmed nor falsified by this cycle — it is provisionally
suspended pending the operator's OPTION A/B/C selection.
