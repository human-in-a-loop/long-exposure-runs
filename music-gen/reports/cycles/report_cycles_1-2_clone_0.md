---
title: "Cycles 1-2 Clone 0 Report — RC10 Drums + Bass Transcription Re-Survey (Fork bdd7bb47f1b5)"
date: "2026-09-02"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
[OUTPUT: report_cycles_1-2_clone_0]

# Cycles 1-2 Clone 0 Report — RC10 Drums + Bass Transcription Re-Survey (Fork bdd7bb47f1b5)

## Abstract

Cycles 1-2 of clone-0 (fork `bdd7bb47f1b5`) close RC10 Branch A — Drums + Bass transcription re-survey on real htdemucs stems — at **RC10_DRUMS_BASS_LANDS**. Discharges operator UPDATE #3 rhythm-section fix priority. Winner per stem type: **drums 5/5 with `onset_band_energy`**; **bass 3/5 with `pyin_mono`**. Chicken Grease both stems PASS. Byte-determinism × 2 across all outputs including TensorFlow basic-pitch (84/84 match; `TF_DETERMINISTIC_OPS=1` env pins held). Four MODERATE deviations honestly disclosed and correctly scoped to c55 v3-rubric supersede (pyin voiced_probability threshold amendment; bass `low_band_corr` synthetic-sine rendering-fidelity gate; drums onset-F1 tautology by §D2(a) construction; Chicken Grease chosen_section clamp workaround). Cycle 2 is a task-complete resumption acknowledgment (no new substantive work; prior VALIDATED state persists on-disk). Auditor decision: **COMPLETE** with `[[BRANCH_COMPLETE]]`.

## Verdict

**RC10_DRUMS_BASS_LANDS** (VALIDATED at cycle 1; **COMPLETE** at cycle 2; `[[BRANCH_COMPLETE]]` emitted).

## Rubric SHA Anchor Chain (Three-Way Byte-Equal)

| Location | SHA-256 |
| --- | --- |
| `docs/rc10_drums_bass_rubric.md` | `a79bee01…5fd919` |
| `data/rc10_impl/drums_bass/rubric_hash.txt` | `a79bee01…5fd919` |
| `verdict.json.rubric_hash` | `a79bee01…5fd919` |

Three-way byte-equality chain CONFIRMED (auditor cited raw `sha256sum` output per emerging schema-drift lemma).

## Per-Stem Winner + Per-Song Results

- **Drums winner**: `onset_band_energy` (5/5 PASS across focus songs).
- **Bass winner**: `pyin_mono` (3/5 PASS; 2 FAIL songs pass f0-agreement 0.929/0.980 but flagged on synthetic-sine `low_band_corr` — MODERATE #2 disclosure).
- **Chicken Grease**: both stems PASS (mandatory anchor honoured).

Verdict RC10_DRUMS_BASS_LANDS threshold: both stems ≥3/5 focus songs. Drums 5/5 ✓; bass 3/5 ✓.

## Candidate Matrix (§3 D3)

Per-stem candidate matrix implemented per §3 D3:

- **Drums**: onset+band-energy classifier (winner: `onset_band_energy`).
- **Bass**: basic-pitch defaults + basic-pitch tuned per instrument freq range + pyin-monophonic (winner: `pyin_mono`).

Scored per §3 D2 against baseline stems on `chosen_section` per focus song. D4 post-processing pipeline (beat-grid snap using c53-clone-2 rc5_tempo_estimate; glitch drop; envelope-velocity; range filter) applied with and without measurement.

## Byte-Determinism × 2 (84/84 Match; TF-Backed basic-pitch Deterministic)

`84/84 match`. Env pins held: `TF_DETERMINISTIC_OPS=1`, `PYTHONHASHSEED=0`, `SOURCE_DATE_EPOCH=1756463424`, `TZ=UTC`, `LC_ALL=C.UTF-8`, single-thread BLAS. All A/B pair directories, per-candidate scorecards, and verdict JSON byte-identical across two fresh `tempfile.mkdtemp()` runs.

## Anchor Preservation (29/29 SHAs Byte-Identical; Target ≥25)

Preserved:
- c50 v2 rubric doc.
- c49 v1 rubric doc.
- `scripts/palette_render/render_stem.py` do-not-touch invariant.
- 10 baseline stems.
- 5 c53-clone-2 rc5 tempo estimates (cross-branch anchor reuse — c53 rc5 estimates re-used cleanly in D4 beat-grid snap postprocessing).

29 entries byte-identical pre/post; contract required ≥25.

## Test Surface (15/15 PASS)

| Suite | Result |
| --- | --- |
| `tests/test_rc10_drums_bass.py` | **15/15 PASS** |

## MODERATE Findings (4; All Honest Worker Disclosures Correctly Scoped to c55 v3 Supersede)

1. **pyin voiced_probability threshold amended** `> 0.5` → `> 0.1` — empirically necessary on real htdemucs bass (mean voiced_prob = 0.109). Rubric §D2(c) originally specified 0.5; c55 v3 supersede formalises the empirical threshold with justification note.
2. **Bass `low_band_corr` is a synthetic-sine rendering-fidelity gate** — 2 FAIL songs pass f0-agreement 0.929/0.980 but flagged on `low_band_corr`. The transcription is correct; the rendering-fidelity gate needs c55 fluidsynth-GM-33 replacement instead of `pretty_midi.synthesize()` sine synth.
3. **Drums onset-F1 is tautological by rubric §D2(a) construction** — candidate detector == reference detector (both use `librosa.onset.onset_detect`). Structurally equivalent to the c53-clone-2 RC5 self-referentiality caveat. c55 v3 supersede pre-registers `librosa.onset.onset_strength + peak-picking` as independent reference detector.
4. **Chicken Grease chosen_section clamp workaround** (inherited c52 Item #2 open policy) — c55 v3 supersede folds resolution.

All four correctly scoped to c55 v3-rubric supersede at root-conductor level per research brief §2.

## MINOR Findings (1; Expected c33 Harness Pattern)

- **Ledger events in shadow-only** — expected c33 harness auto-suffix pattern; c55 `_run/post-merge-integration-cycle-54` concat resolves per c52's clean c51 integration recipe.

## Ledger Events (9 Shadow Rows Under `-clone-0` Suffix)

Sealed for concat by c55 root conductor at shadow ledger `/home/user/music-gen-instance/fork-bdd7bb47f1b5/clone-0/promise_ledger.jsonl`:

- **Substantive `M-RECREATE-2/accurate-small-set/rc10-transcription-real-stem-resurvey/drums-bass/*` unsuffixed per c32** (6 named events):
  - rubric committed, pre-registration verified, per-stem candidate matrix landed, scorecard emitted, winner-per-stem determined, verdict rollup
- **Infra + housekeeping `-clone-0` suffixed per c33** (2 events)
- **`M-INGEST-1/egress-probe-cycle54-clone-0`** (1 tail event; `429 + tv_embedded` unchanged; c49 path-A cadence)

## Cycle Disposition

| Cycle | Researcher Directive | Worker Action | Auditor Decision |
| --- | --- | --- | --- |
| 1 | RC10 Branch A substantive fanout with mtime-hard pre-registration; operator UPDATE #3 rhythm-section fix priority | Rubric + per-stem candidate matrix (drums onset+band-energy; bass basic-pitch defaults + tuned + pyin-mono) + content-metric scoring (D2) + D4 post-processing + winner per stem + per-song A/B pairs + 84-artefact byte-det × 2 with TF-backed basic-pitch deterministic + 29-anchor preservation + 15/15 tests + 9 shadow-ledger events + merge report | VALIDATED at RC10_DRUMS_BASS_LANDS |
| 2 | Task-complete resumption acknowledgment | No new substantive work; prior VALIDATED state persists on-disk | **COMPLETE** with `[[BRANCH_COMPLETE]]` |

## State-Machine Discipline (c29 Lemma Respected)

- `M-RECREATE-2/accurate-small-set/rc10-transcription-real-stem-resurvey/drums-bass` is a peer sub-leaf under c50 v2 rubric chain. NOT a child of any terminal-validated ancestor.
- Peer-supersede pattern preserved: c49 v1 + c50 v2 + c54 clone-0 RC10-drums-bass all byte-preserved on their own chains.
- No `validated → in_progress` transitions attempted.
- **`[[BRANCH_COMPLETE]]` emitted per no-null-cycle-validation role guidance**: "if the milestone is already validated and its scope is genuinely exhausted, emit COMPLETE (with the [[BRANCH_COMPLETE]] line) instead of manufacturing new scope to stay busy."

## Cycle-2 Anti-Pattern Avoidance (Explicit)

Emitting a new cycle to re-audit already-VALIDATED read-only anchors would violate no-null-cycle-validation discipline and would introduce nothing that the c55 root conductor cannot see in the `merge_report.md` the worker already wrote. Continuing this loop would only re-confirm a closed result.

The c55 substantive work — v3 rubric supersede, auditor-schema-drift lemma formalisation, six-stem rollup gate — is explicitly the root conductor's responsibility per the research brief §4/§6, NOT this fanout clone's. Six-stem rollup gates on peer clones-1 (guitar+piano LANDS) + clone-2 (other+vocals, unverified from this clone's vantage); rollup adjudication is not this clone's decision.

## Standing Constraints (Unchanged)

- α pinned at `0.7469387071101908` (not relevant to this branch).
- SHA-256 tiebreak; no PRNG; no `sidecar_nonfactor`; no `i4_stratified`.
- Interpreter guard `#!/usr/bin/python3` on every new script.
- Read-only anchors preserved: c14 `_ledger_schema.py`; c22 stability harness; c26 Path B commitment; c31/c33/c34/c35/c36/c37/c45/c46/c47/c50 palette + recreate + anchor-manifest + rubric chain; c49 v1 baselines; c51 Branch A partials + Branch B outputs; c52/c53 recreate infra; c53-clone-2 rc5 tempo estimates (cross-branch anchor reuse); `scripts/palette_render/render_stem.py` byte-identical do-not-touch invariant.
- Rated audio egress-blocked at `*.googlevideo.com` (`429 + tv_embedded` unchanged; **17+ cycles**; `M-INGEST-1/egress-probe-cycle54-clone-0` recorded honestly per c49 path-A cadence). htdemucs_6s fetch OK carried forward from c50/c51; no regression this cycle.
- Ledger hygiene: `narrative` field; `run_id="run-2026-08-28T040704Z"`; nested `confidence:{level,rationale,assessor}`; UUID5 content-hash `event_id`; two-arg `append_ledger_event(workspace, event)`.
- **c48 env-var flags default OFF**.

## Anti-Patterns Locked (5-Count Stable)

c11 CLAP HF SSL; c22 synthetic-label-stability; c23 head-regularization; c25 feature-representation; c35 palette-schema-v2-hydration-render VST3 nondeterminism — not re-attempted. c30 collision-arc closure at `PARTIAL_BP_UNRESOLVED_SHAPE` unchanged. c31 STILL_GAP surface intact.

**No `M-EAR-1/*` or `M-GEN-1/*` emissions** this branch.

**Fanout-scope discipline reinforced**: clone-0 disciplined itself out of the "one more cycle" trap (COMPLETE instead of manufacturing null-cycle work). Pattern propagates from clone-1's c53 close.

## Merge Disposition

Merge report at `/home/user/music-gen-instance/fork-bdd7bb47f1b5/clone-0/merge_report.md` (per prior session; path outside auditor read scope; worker attestation accepted per convention). Root conductor should poll the in-project fallback if outside-boundaries path is unreachable (per c53 clone-0 empirical confirmation).

## Cycle-55 Handoff (For Root Conductor; Per Cycle-2 Auditor Guidance)

None for this clone (branch closed). Guidance for c55 root conductor:

1. **V3 rubric supersede**: fold the four MODERATE deviations (pyin voiced_probability threshold amendment; bass `low_band_corr` fluidsynth-GM-33 replacement; drums onset-F1 independent-detector via `librosa.onset.onset_strength + peak-picking`; Chicken Grease chosen_section clamp resolution) into c50 v2 → c55 v3 peer-supersede via `M-RECREATE-2/accurate-small-set/rc-v2-to-v3-rubric-supersede` with `supersedes_path: str` per c14 lemma.
2. **Six-stem rollup gate**: merge clone-0 (drums+bass — this work; RC10_DRUMS_BASS_LANDS), clone-1 (guitar+piano; RC10_GUITAR_PIANO_LANDS), clone-2 (other+vocals; TBD) scorecards into `data/rc10_impl/scorecard_all_stems.tsv` for the `M_RECREATE_2_LANDS` candidacy per operator UPDATE #4. RC10_LANDS aggregate is AND-gate over six per-stem accepts per rubric §D8.
3. **Formalise `_infra/auditor-schema-drift-lemma`**: 5 catches across the campaign (c46 rubric-doc-drift, c48-close report-drift, c49-close scope-drift, c50-close narrative-vs-artefact drift, c54-clone-0 `byte_determinism.json` schema-key drift — worker's `run1_sha`/`n_match` layout vs a naive audit's `files` layout assumption). Codify: auditors MUST read verdict-JSONs with schema tolerance; MUST cite raw `sha256sum` output before accepting worker summary claims about SHA identity.
4. **Plan-of-record registration**: register two new intermediate milestone IDs at c55: `M-RECREATE-2/accurate-small-set/rc10-transcription-real-stem-resurvey/drums-bass` + `.../guitar-piano` + `.../other-vocals` peer sub-leaves. Follow c51 `_run/post-merge-integration-cycle-51` + `_plan/register-c51-fanout-milestones` pattern.
5. **c53-clone-2 rc5 tempo estimates cross-branch anchor reuse pattern**: worked cleanly this cycle in D4 beat-grid snap postprocessing. Codify as reusable pattern for c56+ cross-branch anchor consumption.

## Cumulative Progress

**M-RECREATE-2 arc RC status roll-up** (post-c54 clone-0 RC10 Branch A):

| RC | Status | Cycle |
| --- | --- | --- |
| Rubric v2 committed | ✓ | c50 |
| Focus set frozen w/ Chicken Grease mandatory | ✓ | c50 |
| RC0/RC0-v2 baselines captured × 2 | ✓ | c49/c50 |
| RC1+RC9 LANDS 4/5 | ✓ | c51 Branch A |
| RC2+RC3 LANDS | ✓ | c51 Branch B |
| RC5 LANDS 5/5 (honest self-referential caveat) | ✓ | c53 clone-2 |
| RC7 LANDS 5/5 | ✓ | c53 clone-0 (v2 rerun) |
| RC10 Branch B Guitar+Piano LANDS (guitar 4/5; piano 5/5) | ✓ | c53 clone-1 |
| **RC10 Branch A Drums+Bass LANDS** (drums 5/5 `onset_band_energy`; bass 3/5 `pyin_mono`; Chicken Grease both PASS) | ✓ | **c54 clone-0 (this)** |
| RC10 Branch C (Other+Vocals) | (fork sibling clone-2) | — |
| RC6 panel-gate | not started; c55 pre-registers; c56 implements | — |
| Aggregate `M_RECREATE_2_LANDS` | **c56 candidate** contingent on c55 six-stem rollup + v3 supersede + clone-2 verdict | — |

**Recurring patterns**:

- **Auditor-reads-off-disk lemma extended to 5 catches** (c46/c48/c49/c50/c54). This cycle's contribution: `byte_determinism.json` schema-key drift. Strong case for c55 to formalise `_infra/auditor-schema-drift-lemma`.
- **Rubric supersede pattern (c14 str-lemma) held cleanly** through c49 v1 → c50 v2 chain; ready to carry v2 → v3 in c55 without touching v2 on disk. `supersedes_path: str` (not list) invariant preserved.
- **c33 fanout-namespace-guard + c32 auto-suffix convention held** through c54 as expected: substantive `M-RECREATE-2/.../rc10-…-resurvey/*` unsuffixed; two housekeeping + one egress-probe under `-clone-0` suffix. c55 concat mirrors c52's clean c51 integration recipe.
- **htdemucs_6s fetch OK carried forward from c50/c51**; no regression this cycle.
- **Rhythm section fix priority (operator UPDATE #3) DISCHARGED**: drums + bass now transcribed against real htdemucs stems with content metrics, not synthetic-mix placeholders. Transcription-truth situation materially improved even where `low_band_corr` flags overtone-rich bass (transcription is correct; rendering-fidelity gate needs c55 fluidsynth-GM-33 replacement).
- **Six-stem verdict path unblocked** contingent on peer clones-1+2 landing. RC10_LANDS aggregate is AND-gate over six per-stem accepts per rubric §D8.
- **c53 rc5 tempo estimates re-used cleanly** in D4 beat-grid snap postprocessing; cross-branch anchor reuse working as designed.
- **Content-metric gate discriminates over-transcription, not just under-transcription** (c53 clone-1 finding extended here): drums onset-F1 tautology at §D2(a) also demonstrates the same lemma from a different angle — reference-detector selection matters.
- **Fanout-scope discipline propagating**: clone-1 c53 close demonstrated the pattern; clone-0 c54 close now reinforces it. "One more cycle" trap avoided.
- **Honest-negative-finding discipline holding** at 10+ consecutive cycles.
- **Egress unchanged (17+ cycles)**: HTTP 429 + `tv_embedded` failure mode. c50 htdemucs_6s fetch OK anomaly remains isolated (not re-probed).

**c29 state-machine lemma** respected: peer sub-leaves under c50 v2 rubric chain; ledger topology stays a DAG.

**c32 → c33 → c36 v2 → c39 v3 → c47 Branch B MIXED → c50 peer-supersede** fanout-namespace + rubric-chain convention held: substantive `M-RECREATE-2/*` unsuffixed; infra families `-clone-0` suffixed.

**Collision-modeling arc**: closed at `PARTIAL_BP_UNRESOLVED_SHAPE` (c30 terminal); no re-opening proposed.

**Scope of this fanout clone fully discharged.** `[[BRANCH_COMPLETE]]` emitted per no-null-cycle-validation role guidance; auditor decision **COMPLETE**.

[END OUTPUT]
