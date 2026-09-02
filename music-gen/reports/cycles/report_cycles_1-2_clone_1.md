---
title: "Cycles 1-2 Clone 1 Report — RC10 Guitar + Piano Transcription Re-Survey (Fork bdd7bb47f1b5)"
date: "2026-09-02"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
[OUTPUT: report_cycles_1-2_clone_1]

# Cycles 1-2 Clone 1 Report — RC10 Guitar + Piano Transcription Re-Survey (Fork bdd7bb47f1b5)

## Abstract

Cycles 1-2 of clone-1 (fork `bdd7bb47f1b5`) close RC10 Branch B — Guitar + Piano transcription re-survey on real htdemucs 6-stem outputs — at **RC10_GUITAR_PIANO_LANDS**. Winner per stem type is `C2_tuned` (basic-pitch tuned per instrument freq range) for BOTH guitar and piano. Per-song verdicts: **guitar 4/5 PASS + 1 FAIL** (Dojo Cuts Rome density-overfire 6.24 vs [0.5, 2.0] pass band); **piano 5/5 PASS**. RC10_LANDS threshold (both stems on ≥3 focus songs) met (guitar 4/5 ≥ 3/5; piano 5/5 ≥ 3/5). Chord-track fallback (C3 beat-sync chroma-CQT per operator UPDATE #4 "a correct chord track rendered as a comp pattern beats a wrong note soup") preserved as first-class candidate; passed D7 on 2/5 guitar songs but did not win any per-song D5 ballot. Cycle 2 is a status-acknowledgment standby cycle with on-disk re-verification (all invariants preserved byte-exactly). Auditor decision: **COMPLETE** with `[[BRANCH_COMPLETE]]`.

## Verdict

**RC10_GUITAR_PIANO_LANDS** (VALIDATED at cycle 1; **COMPLETE** at cycle 2; `[[BRANCH_COMPLETE]]` emitted).

## Rubric SHA Anchor Chain (Three-Way Byte-Equal)

| Location | SHA-256 |
| --- | --- |
| `docs/rc10_guitar_piano_rubric.md` | `c7fe33a742a98f9b8ad2d87cb3f26286950ad560ef5d69c47dd53686fe03d7a8` |
| `data/rc10_impl/guitar_piano/rubric_hash.txt` | `c7fe33a7…d7a8` (single line, verified) |
| `verdict.json.rubric_hash` | `c7fe33a7…d7a8` |

Three-way byte-equality chain CONFIRMED (auditor re-verified live on-disk).

## Per-Stem Winner + Per-Song Results

**Winner per stem type** (`winner_per_stem.json`): `C2_tuned` (basic-pitch tuned per instrument frequency range) wins for both guitar and piano.

**Per-song verdicts**:

| Song ID (sha16) | Guitar (C2_tuned) | Piano (C2_tuned) |
| --- | :---: | :---: |
| `31a164f845f8e27e` (Chicken Grease) | PASS | PASS |
| `cdd2717e52820ff6` (Disco A) | PASS | PASS |
| `51e433ade2a845e1` (Dojo Cuts Rome) | **FAIL** (density 6.24 vs [0.5, 2.0]) | PASS |
| `252eb21ce7df7328` (Mura Masa) | PASS | PASS |
| `88d247468cb6d49f` (band-7) | PASS | PASS |
| **Totals** | **4/5 PASS** | **5/5 PASS** |

RC10_LANDS threshold (both stems on ≥3 focus songs) met.

## Candidate Matrix (§3 D3)

Per-stem candidate matrix implemented per §3 D3:

- **C1_default**: basic-pitch with default thresholds.
- **C2_tuned**: basic-pitch tuned per instrument frequency range (winner both stems).
- **C3_chord_track**: beat-synchronous chroma-CQT chord-track as comp-pattern fallback for polyphonic failures (per operator UPDATE #4).

Scored per §3 D2: **beat-synchronous chroma cosine + note-density ratio**. D4 post-processing applied both with and without (2 flavours × candidates in scorecard).

**Scorecard**: 60 data rows + 1 header = 61 lines (5 songs × 2 stems × 3 candidates × 2 D4-flavors).

## Content-Metric Gate Discriminates Over-Transcription (Load-Bearing Finding)

The Dojo Cuts Rome guitar FAIL is the **campaign's first per-song rejection on density-band overfire** (6.24 with C2_tuned; 2.38 with C1_default+C3_chord_track vs [0.5, 2.0] pass band). Validates the c50 rubric-v2 D2 dual-metric choice — chroma-cosine alone would have PASSed this song at 0.87-0.95.

Chord-track first-classness preserved per operator UPDATE #4: C3 didn't win any per-song D5 ballot but passed D7 on 2/5 guitar songs; keeping it as first-class candidate (not fallback-only) preserved the option value the operator mandated.

## Byte-Determinism × 2 (133/133 SHA-Equal)

`holds=True`, `n_artifacts=133`, `n_mismatch=0`. All A/B pair directories, per-candidate scorecards, and verdict JSON byte-identical across two fresh `tempfile.mkdtemp()` runs.

## A/B Pair Directories (5 Songs × 2 Stems = 10 Pairs)

5 song `<sha16>/` directories under `data/recreate_v2/ab_pairs/`: `252eb21ce7df7328`, `31a164f845f8e27e`, `51e433ade2a845e1`, `88d247468cb6d49f`, `cdd2717e52820ff6`. Each contains `guitar/` and `piano/` subdirs with winner MIDIs + synthesized WAVs.

## Cycle Disposition

| Cycle | Researcher Directive | Worker Action | Auditor Decision |
| --- | --- | --- | --- |
| 1 | RC10 Branch B substantive fanout with mtime-hard pre-registration | Rubric + per-stem candidate matrix (C1/C2/C3) + content-metric scoring (D2) + D4 post-processing + winner per stem + per-song A/B pairs + 133-artefact byte-det × 2 + 9 shadow-ledger events + merge report | VALIDATED at RC10_GUITAR_PIANO_LANDS |
| 2 | Compact on-disk re-verification | Status-acknowledgment standby; no new substantive work; invariants preserved byte-exactly | **COMPLETE** with `[[BRANCH_COMPLETE]]` |

## Sub-Topic Assessment (All §3 D1-D7 Sufficiency Criteria Met)

| Criterion | Status |
| --- | --- |
| Pre-registered rubric BEFORE any script under `scripts/recreate_v2/rc10_guitar_piano/` | MET (mtime chain preserved) |
| Per-stem candidate matrix per §3 D3 (C1_default + C2_tuned + C3_chord_track) | MET |
| Content metrics per §3 D2 (chroma cosine + note-density ratio) | MET |
| D4 post-processing with and without | MET (2 flavours × candidates in scorecard) |
| Winner per stem-type + per-song A/B pairs under `data/recreate_v2/ab_pairs/<song>/{guitar,piano}/` | MET (`winner_per_stem.json` = `C2_tuned` for both; 10 A/B pairs) |
| Byte-determinism × 2 | MET (133/133) |
| Verdict RC10_GUITAR_PIANO_LANDS ⇔ both stems pass on ≥3 focus songs | MET (guitar 4/5, piano 5/5) |
| Six + 2 + 1 events under `-clone-1` suffix | MET (9 events in clone-1 shadow ledger) |
| Required output `docs/rc10_guitar_piano_report.md` | MET |

## Ledger Events (9 Shadow Rows Under `-clone-1` Suffix)

Landed in shadow ledger `/home/user/music-gen-instance/fork-bdd7bb47f1b5/clone-1/promise_ledger.jsonl`:

- **Substantive `M-RECREATE-2/accurate-small-set/rc10-transcription-real-stem-resurvey/guitar-piano/*` unsuffixed per c32** (6 named events):
  - rubric committed, pre-registration verified, per-stem candidate matrix landed, scorecard emitted, winner-per-stem determined, verdict rollup
- **Infra + housekeeping `-clone-1` suffixed per c33** (2 events)
- **`M-INGEST-1/egress-probe-cycle53-clone-1`** (1 tail event; `429 + tv_embedded` unchanged)

Path outside auditor read scope; trusted per prior worker report.

## State-Machine Discipline (c29 Lemma Respected)

- `M-RECREATE-2/accurate-small-set/rc10-transcription-real-stem-resurvey/guitar-piano` is a peer sub-leaf under c50 v2 rubric chain. NOT a child of any terminal-validated ancestor.
- Peer-supersede pattern preserved: c49 v1 + c50 v2 + c53 clone-1 RC10 all byte-preserved on their own chains.
- No `validated → in_progress` transitions attempted.
- **`[[BRANCH_COMPLETE]]` emitted per no-null-cycle-validation role guidance**: "if the milestone is already validated and its scope is genuinely exhausted, emit COMPLETE (with the [[BRANCH_COMPLETE]] line) instead of manufacturing new scope to stay busy."

## Cycle-2 Anti-Pattern Avoidance (Explicit)

Manufacturing further work on this branch (e.g., relitigating the Dojo Cuts Rome guitar density-band FAIL, or fluidsynth GM 25/0 A/B pair LUFS repair) would violate scope boundaries: those items are **explicit c54 handoffs**, NOT clone-1 work. Emitting VALIDATED (which would fire another cycle) or PIVOT (which would invent scope) would both be anti-pattern. Cycle 2 correctly avoided both.

## Standing Constraints (Unchanged)

- α pinned at `0.7469387071101908` (not relevant to this branch).
- SHA-256 tiebreak; no PRNG; no `sidecar_nonfactor`; no `i4_stratified`.
- Interpreter guard `#!/usr/bin/python3` on every new script.
- Read-only anchors preserved: c14 `_ledger_schema.py`; c22 stability harness; c26 Path B commitment; c31/c33/c34/c35/c36/c37/c45/c46/c47/c50 palette + recreate + anchor-manifest + rubric chain; c49 v1 baselines; c51 Branch A partials + Branch B outputs; c52/c53 recreate infra; `scripts/palette_render/render_stem.py` byte-identical do-not-touch invariant.
- Rated audio egress-blocked at `*.googlevideo.com` (`429 + tv_embedded` unchanged; `M-INGEST-1/egress-probe-cycle53-clone-1` recorded honestly per c49 path-A cadence).
- Ledger hygiene: `narrative` field; `run_id="run-2026-08-28T040704Z"`; nested `confidence:{level,rationale,assessor}`; UUID5 content-hash `event_id`; two-arg `append_ledger_event(workspace, event)`.
- **c48 env-var flags default OFF**.

## Anti-Patterns Locked (5-Count Stable)

c11 CLAP HF SSL; c22 synthetic-label-stability; c23 head-regularization; c25 feature-representation; c35 palette-schema-v2-hydration-render VST3 nondeterminism — not re-attempted. c30 collision-arc closure at `PARTIAL_BP_UNRESOLVED_SHAPE` unchanged. c31 STILL_GAP surface intact.

**No `M-EAR-1/*` or `M-GEN-1/*` emissions** this branch.

**Fanout-scope discipline reinforced**: clone-1 disciplined itself out of the "one more cycle" trap (COMPLETE instead of manufacturing null-cycle work). Pattern should propagate.

## Merge Disposition

Merge report at `/home/user/music-gen-instance/fork-bdd7bb47f1b5/clone-1/merge_report.md` (per prior session; path outside auditor read scope). Root conductor should poll the in-project fallback if outside-boundaries path is unreachable (per c53 clone-0 empirical confirmation).

## Cycle-54 Handoff (For Root Conductor; Per Cycle-2 Auditor Guidance)

None for this clone (branch closed). Guidance for the c54 root conductor:

1. **Six-stem rollup**: merge clone-0 (drums+bass), clone-1 (guitar+piano — this work), clone-2 (other+vocals) scorecards into `data/rc10_impl/scorecard_all_stems.tsv` for the `M_RECREATE_2_LANDS` candidacy per operator UPDATE #4.
2. **Plan-of-record drift**: register two new intermediate milestone IDs at c54: `M-RECREATE-2/accurate-small-set/rc10-transcription-real-stem-resurvey` (peer sub-milestone under `M-RECREATE-2/accurate-small-set-v2`) and `.../guitar-piano`. Follow the c51 `_run/post-merge-integration-cycle-51` + `_plan/register-c51-fanout-milestones` pattern.
3. **Dojo Cuts Rome guitar** (per-song density-overfire FAIL, `51e433ade2a845e1`): c54 decides whether to (a) widen density pass band from [0.5, 2.0]; (b) surface C3 chord-track fallback as automatic per-song rescue when D5 winner trips gate; or (c) accept 4/5 as sufficient.
4. **A/B pair LUFS drift** (worker's Issue #2): swap `pretty_midi.synthesize()` sine-synth for fluidsynth GM 25 (guitar) / GM 0 (piano) at c54. NOT a transcription-verdict defect; A/B pair rendering only.

## Cumulative Progress

**M-RECREATE-2 arc RC status roll-up** (post-c53 clone-1 RC10 Branch B):

| RC | Status | Cycle |
| --- | --- | --- |
| Rubric v2 committed | ✓ | c50 |
| Focus set frozen w/ Chicken Grease mandatory | ✓ | c50 |
| RC0/RC0-v2 baselines captured × 2 | ✓ | c49/c50 |
| RC1+RC9 **LANDS 4/5** | ✓ | c51 Branch A |
| RC2+RC3 LANDS | ✓ | c51 Branch B |
| RC5 LANDS 5/5 (honest self-referential caveat) | ✓ | c53 clone-2 |
| RC7 LANDS 5/5 | ✓ | c53 clone-0 (v2 rerun) |
| **RC10 Branch B Guitar+Piano LANDS** (guitar 4/5; piano 5/5; C2_tuned winner both stems) | ✓ | **c53 clone-1 (this)** |
| RC10 Branch A (Drums+Bass) | (fork sibling clone-0) | — |
| RC10 Branch C (Other+Vocals) | (fork sibling clone-2) | — |
| RC6 panel-gate | not started; c54 pre-registers; c55 implements | — |
| Aggregate `M_RECREATE_2_LANDS` | **c56 candidate** contingent on c55 outcomes + c54 six-stem rollup | — |

**Recurring patterns**:

- **Content-metric gate discriminates over-transcription, not just under-transcription** (new c53 clone-1 finding): Dojo Cuts Rome guitar FAIL is the campaign's first per-song rejection on density-band overfire. Validates c50 rubric-v2 D2 dual-metric choice.
- **Chord-track first-classness preserved per operator UPDATE #4**: C3 passed D7 on 2/5 guitar songs; keeping it as first-class candidate preserved the option value.
- **Auditor-reads-ledger-not-brief-summaries** lemma reinforced: 5-cycle catch record (c46, c48-close, c49-close, c50-close, c53-close) — recommend formalisation at c54 in `docs/auditor_discipline_ledger_first.md`.
- **Anchor snapshot lemma**: 28-entry manifest this cycle; c51 Branch C hit 95. Now duplicated across clones — c54 should consolidate to shared `long_exposure/tools/anchor_snapshot.py`.
- **Fanout-scope discipline**: clone-1 disciplined itself out of the "one more cycle" trap (COMPLETE instead of manufacturing null-cycle work). Pattern should propagate.
- **Honest-negative-finding discipline holding** at 9+ consecutive cycles.
- **Egress unchanged (17+ cycles)**: HTTP 429 + `tv_embedded` failure mode. c50 htdemucs_6s fetch OK anomaly remains isolated.

**c29 state-machine lemma** respected: peer sub-leaves under c50 v2 rubric chain; ledger topology stays a DAG.

**c32 → c33 → c36 v2 → c39 v3 → c47 Branch B MIXED → c50 peer-supersede** fanout-namespace + rubric-chain convention held: substantive `M-RECREATE-2/*` unsuffixed; infra families `-clone-1` suffixed.

**Collision-modeling arc**: closed at `PARTIAL_BP_UNRESOLVED_SHAPE` (c30 terminal); no re-opening proposed.

**Scope of this fanout clone fully discharged.** `[[BRANCH_COMPLETE]]` emitted per no-null-cycle-validation role guidance; auditor decision **COMPLETE**.

[END OUTPUT]
