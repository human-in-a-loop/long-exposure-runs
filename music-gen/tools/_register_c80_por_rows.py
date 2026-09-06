#!/usr/bin/python3
"""c80 one-shot POR registration: insert c80 sub-leaf rows inline in the `## Milestones` parseable region
(before `## Sub-milestones`). Idempotent. Retained in-tree per c14+ emitter-exemption pattern."""
import json, os, sys
from pathlib import Path
os.chdir(Path(__file__).resolve().parent.parent)
POR = Path("plan_of_record.md")
P = "M-V5-CORPUS-1"

ROWS = [
 (f"{P}/transcription-liveness-c80", "G4", "c80 P0: PID 5201 verified ALIVE at cycle open (47:41 elapsed, on CG muscriptor:full_mix); not touched. Liveness record `data/v5/logs/c80_p0_liveness.txt`; stale `dry_run` rows in `transcription_progress.json` overwritten from on-disk state (derived sibling `transcription_progress_c80_derived.json`); disclosure: the driver holds its own in-memory copy and re-emits `dry_run` for not-yet-reached songs until it processes them (self-healing). df 87 % (< 90 abort) throughout; no multi-GB install co-scheduled.", "Liveness file exists; job alive; no df >= 90 %; no install co-scheduled.", f"{P}/full-length-transcription-launched-c79"),
 (f"{P}/tempo_v5b-preregistered-c80", "G4", "c80 P1: `data/v5/corpus/tempo_v5b_preregistration.json` written BEFORE any per-song output (mtime gate verified by the verdict script + test_04). Criterion: candidates = every local maximum of the normalized onset autocorrelation in the [40,240] BPM lag range; s(T) = ac(T) + 0.5 ac(T/2) + 0.5 ac(2T) with out-of-range harmonics contributing 0; argmax over [70,180]; SHA-256 tiebreak. Targets identical to c79's (WIG ∉[45,56] & ±2 of 99.384; CG ±2 of 90.726; Rome ±2 of 151.999; PD ±2 of 123.047; Disco A ±2 of 120.185). `scripts/v5/tempo_v5b.py` new sibling; `tempo_v5.py` + its frozen verdict untouched.", "Prereg mtime precedes every tempo_v5b.json; 26/26 scored; byte-det x2.", f"{P}/tempo-v5-halt-honest-c79"),
 (f"{P}/tempo_v5b-verdict-c80", "G4", "c80 P1 FROZEN VERDICT = **RULES_OUT_HARMONIC_SUM** (`tempo_v5b_falsification.json`). PD 80.75 (s=1.222 vs 1.045 at 123.05) and Disco A 80.75 (s=1.201 vs 0.994) unchanged; Rome REGRESSED 152.00 -> 103.36 (s=1.114 vs 1.094); WIG 99.384 and CG 92.285 hit. Non-anchor flips 7/21 (33 %). Byte-det x2 27/27. MECHANISM DIAGNOSIS (recorded, NOT applied — FD-1): the anchor beat's T/2 harmonic (lag 10.5 = 246 BPM) falls just outside the pre-registered [40,240] candidate range and contributes 0, while the hemiola lag's T/2 (161.5) and 2T (40.4) are both in range; PD's ac at lag 11 is 0.69 — had it counted, s(123.05) ≈ 1.39 > 1.22. Figure `fig_tempo_v5b_scores.png`. A second criterion is c81's decision.", "Verdict ∈ frozen enum; per-song hits recorded verbatim; no retune.", f"{P}/tempo_v5b-preregistered-c80"),
 (f"{P}/recanonicalize-blocked-c80", "G4", "c80 P2 (RULES_OUT branch): `data/v5/corpus/recanonicalization_blocked.json` names Peach Dream + Disco A as MUST-NOT-CONSUME for rules extraction (bpm_v5 80.75 vs anchors 123.05 / 120.19); WIG, CG, Rome not blocked (Rome's on-disk bpm_v5 = anchor; the v5b regression is ruled out, not adopted). Advisory list of 7 non-anchor v5b flippers. M-V5-RULES-1 stays gated on the blocked songs.", "Blocked file exists; M-V5-RULES-1 gate noted in POR.", f"{P}/tempo_v5b-verdict-c80"),
 (f"{P}/canonical-midi-index-collision-c80", "G4", "c80 FIRST-CLASS DEFECT + FIX. READ-ONLY c22 `recreate_v3._merge_chunk_events` re-offsets chunk times but never re-numbers `index`/`start_event_index`; the READ-ONLY c4 serializer keys starts by `index`, so c79's full-length `canonical_midi_full/*.mid` silently dropped most notes (WIG other 1799 JSON starts -> 395 MIDI note_on; CG guitar 2736 -> 486 distinct indices). 30 s v3 sections were single-chunk and unaffected; MuScriptor JSON is intact. `scripts/v5/reindex_canonical_v5.py` re-pairs starts/ends (deterministic greedy: same chunk-local index, end > start, span <= 30 s), re-indexes sequentially and calls the READ-ONLY serializer into `canonical_v5_reindexed/` (lossless: WIG 5642/5642 starts recovered, 9 unpaired -> 100 ms synthetic; CG 9154/9154). Byte-det x2 14/14. c79 lossy dir left untouched as anchor. str-supersedes the canonical-MIDI clause of `M-V5-CORPUS-1/252eb21ce7df7328-transcribed-c79`.", "Reindexed MIDI note_on == JSON starts per stem; byte-det x2; c79 dir untouched.", f"{P}/full-length-transcription-launched-c79"),
 ("M-V5-RULES-1/harmony_v5-gated-c80", "G4", "c80 P3: `scripts/v5/harmony_v5.py` (beat-weighted PCP from bass+guitar+piano+other canonical MIDI — velocity uniform 100 so duration-only, disclosed; 84 root x quality cosine templates maj/min/7/min7/maj7/9/sus; Krumhansl-Kessler key; functional states `(root-tonic)%12:quality`; beat-level Markov incl. self-loops + segment matrix; pre-declared degeneracy: max stationary < 0.60 AND >= 4 qualities with >= 8 segments). Pre-declared >= 3 unblocked-song gate NOT met (2 landed unblocked: WIG, CG; PD lands blocked) -> `data/v5/rules/harmony_v5_gated.json`. Labelled n=2 PREVIEW (`data/v5/rules/preview_n2/`): WIG G major (Em7/C/G top states), CG F# minor (B sus / F#m); 49 states; max stationary N = 0.124; 7 qualities >= 8 segments -> preview NON_DEGENERATE. Nothing fed to a generator.", "Gated record with song count; preview clearly labelled.", f"{P}/recanonicalize-blocked-c80"),
 ("M-V5-EAR-1/ear-venv-headroom-c80", "G3", "c80 P4 (no build): `data/v5/ear/venv_headroom_c80.json` — free 5.21 GB (>= 3.5 GB brief threshold WITHOUT touching /root/.local 2.80 GB), required 2.6 GB, idle margin 2.61 GB (>= 0.9); margin during transcription transient 2.27 GB; margin during pip transient + transcription -0.03 GB (c79 hit 93 %). `build_allowed_next_cycle=false` (transcription ~24 songs x ~27 min will not finish before c81); `build_allowed_if_sequenced_after_transcription=true`. Recommendation: pause the driver at a song boundary (cache-safe) or build right after a song's transient deletion. Mandatory by c81.", "JSON with explicit build_allowed_next_cycle boolean.", "M-V5-EAR-1/ear-venv-probe-c79"),
 ("_plan/register-c80-sub-leaves", "G1", "c80 POR registration row: c80 sub-leaves inserted inline in the `## Milestones` parseable region via `tools/_register_c80_por_rows.py` (idempotent; per-song `<sha16>-transcribed-c80` rows generated from on-disk transcription manifests).", "Rows added.", "—"),
 ("_infra/adopt-cycle80-tests", "G1", "c80 test-adoption: `tests/test_tempo_v5b.py` (6: synthetic 3:2 mechanism; out-of-range harmonics zero incl. on-disk PD lag-21; tiebreak + AST scan; prereg mtime gate + frozen verdict enum + blocked file; anchored songs verbatim; byte-det x2) + `tests/test_harmony_v5.py` (3: C-maj7 recovery; I-vi-IV-V7 transposition invariance; pre-declared degeneracy thresholds + on-disk gated/chain record). Regression 42/42 pre-c80 -> 51/51 cross-cycle.", "9/9 new + 42/42 regression green.", "—"),
 ("_archive/cycle-80-scratch", "G1", "c80 scratch archival: `tools/_emit_c80_ledger_events.py` + `tools/_register_c80_por_rows.py` retained in-tree per emitter-exemption pattern; session scratchpad probes/runners not in workspace; `data/v5/corpus/plot_tempo_v5b_scores.py` co-located with its data + figure.", "No workspace scratch to archive.", "—"),
 ("_run/cycle_80_closed", "G1", "c80 CLOSED — v5 REOPENING cycle 2. See ledger event narrative for the 9-header closing summary.", "Cycle rollup after named sub-leaves.", "—"),
]

def main() -> int:
    prog = json.loads(Path("data/v5/corpus/transcription_progress.json").read_text())
    rows = list(ROWS)
    for s in prog["order"]:
        tmp = Path(f"data/v5/corpus/{s}/transcription_manifest.json")
        if not tmp.exists() or s == "252eb21ce7df7328":
            continue
        tm = json.loads(tmp.read_text())
        nc = {p: tm["note_counts"][p]["n_note_on"] for p in tm["note_counts"]}
        rows.append((f"{P}/{s}-transcribed-c80", "G4",
                     f"c80 full-length landing: {tm.get('title')} ({s}, {tm['duration_s']} s, bpm_v5 {tm['bpm_v5']}): note_on {nc}; drums GM classes {tm['note_counts']['drums'].get('gm_classes')}; bars {tm['bar_count_at_bpm_v5']}; transient deleted; canonical MIDI re-indexed lossless under `canonical_v5_reindexed/` (c79 `canonical_midi_full/` is lossy — see index-collision row).",
                     "transcription_manifest.json + 7 JSON + 7 reindexed MIDI on disk; transient deleted.", f"{P}/full-length-transcription-launched-c79"))
    txt = POR.read_text()
    lines = txt.splitlines(keepends=True)
    idx = next(i for i, l in enumerate(lines) if l.startswith("## Sub-milestones"))
    existing = {l.split("|")[1].strip() for l in lines[:idx] if l.startswith("| ")}
    new = [f"| {mid} | {goal} | {desc} | {crit} | {deps} |\n" for mid, goal, desc, crit, deps in rows if mid not in existing]
    if not new:
        print("IDEMPOTENT: all c80 POR rows present"); return 0
    ins = idx
    while ins > 0 and lines[ins - 1].strip() == "":
        ins -= 1
    lines[ins:ins] = new
    POR.write_text("".join(lines))
    print(f"inserted {len(new)} rows before line {ins + 1}: {[r.split('|')[1].strip() for r in new]}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
