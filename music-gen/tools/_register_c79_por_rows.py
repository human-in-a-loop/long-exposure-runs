#!/usr/bin/python3
"""c79 one-shot POR registration: insert M-V5-* parent rows + c79 sub-leaf rows inline in the
`## Milestones` parseable region (before `## Sub-milestones`). Idempotent (skips ids already present).
Retained in-tree per c14+ emitter-exemption pattern (docs/emitter_exemption_policy.md)."""
import os, sys
from pathlib import Path
os.chdir(Path(__file__).resolve().parent.parent)
POR = Path("plan_of_record.md")

ROWS = [
 ("M-V5-CORPUS-1", "G4", "v5 REOPENING foundation (OPERATOR GUIDANCE 2026-09-06 #1). Full-length transcription of the v5 corpus (five focus songs + remaining band-6/7 songs) through the checkpointed stage-cache driver, plus the tempo-estimation fix (BPM validated against onset autocorrelation; half/double-time resolved; WIG must not extract at ~50 BPM). c79 disclosures: corpus receipts enumerate 26 songs (13 band-6 + 10 band-7 + 3 band-5 focus), not ~7; no full-song stems existed on disk; the flat-band autocorrelation criterion FAILED its pre-registered falsification (PD/Disco A 3:2 regression) and was recorded, not retuned.", "(a) `data/v5/corpus/corpus_manifest.json` byte-det x2 with per-song asset inventory; (b) `tempo_v5.json` per song byte-det x2 + frozen falsification verdict; (c) per-song `transcription_manifest.json` with per-stem note counts incl. other/piano, bar count at bpm_v5, stage-cache keys; df <= 90% throughout; (d) transient stems deleted after transcribe.", "M-V3-SPINE-2/stage-checkpointed-driver"),
 ("M-V5-RULES-1", "G4", "v5 rules (OPERATOR #2/#3/#4): harmony reduced to ROOT+QUALITY via template matching (maj/min/7/min7/maj7/9/sus) over beat-weighted PCPs, transposed to a common key, Markov chain over functional chords; JOINT groove conditional model with drums split kick/snare/hat (GM classes) + cross-stem conditionals (snare|kick, hat|kick+snare, bass|kick) validated on backbeat/lock statistics with honest degenerate-model rejection; section FORM PLAN with forced literal repetition. Supersedes M-V4-RULES-1 semantics (raw pitch-set states retired).", "Harmony chain + groove model + form plan artifacts hashed; same-input->same-output proof; degenerate-model check reported honestly.", "M-V5-CORPUS-1"),
 ("M-V5-EAR-1", "G3", "v5 ear (OPERATOR #5): ISOLATED ear venv (own numpy/tensorflow/torch pins; subprocess-invoked; receipts + env pin manifest; main venv pins untouched); restore exemplar-anchored ear and the >=6 gate; fallback band-4-vs-band-7 discrimination check if the venv fails after honest attempts. c79 probe: venv BUILT and import-verified (numpy 1.26.4 / tensorflow 2.21.0 / tensorflow_hub 0.16.1) then REMOVED for disk hygiene (df 93% > 90% ceiling during P3); receipts at `data/v5/ear/`. MANDATORY by c81.", "Isolated venv env-pin manifest + pip-freeze SHA; VGGish (and CLAP if fetchable) subprocess embedding byte-det x2 vs cached rows; >=6 gate restored OR band-4-vs-band-7 fallback reported; main-env pip-freeze SHA pre==post.", "M-V4-EAR-1"),
 ("M-V5-GEN-1", "G5", "v5 generator (OPERATOR #6/#7): GROOVE-FIRST per song (drums+bass from joint groove model -> chords from harmony chain on the form plan -> melody/keys on top); donor profiles + mix match unchanged from v4; 5 novel instrumental songs at ear >=6 + interpolation demo REQUIRED; stall budget 12 iterations (`data/v5/gen/stall_counter.json` reset 0/12 at c79); every iteration's best samples to `data/v4/generated/v5_iter_NN/` for operator listening.", "5 passers >=6 + interpolation demo OR honest best-of at stall; per-song manifests with seed + generator hash + rules hash + donor + env pins + ear score.", "M-V5-RULES-1, M-V5-EAR-1"),
 ("M-V5-CLOSE-1", "G1", "v5 close (OPERATOR #8): amend completion report (v4 amendment), update OPERATOR_DECISIONS + codebase guide, clean re-close.", "Report amendment published; OPERATOR_DECISIONS updated; run re-closed cleanly.", "M-V5-GEN-1"),
 ("_plan/adopt-operator-v5-reopening-directive-2026-09-06", "G1", "c79 adoption of OPERATOR GUIDANCE 2026-09-06 (v5 reopening of RULES/EAR/GEN only; profiles/recreations/showcase/certificates FROZEN). str-supersedes `_run/cycle_78_closed` per c14 lemma (the 'run ends here' clause is superseded by operator resume; c77/c78 verdicts NOT rewritten). Records the operator's 8 decisions + 6-defect diagnosis verbatim, the `c87` (operator note) vs on-disk `c78` cycle-counter disclosure, and the FROZEN list.", "Ledger event with str supersedes_path; OPERATOR_DECISIONS #20 appended; stall counter reset.", "—"),
 ("_plan/operator-decisions-c79-amendment", "G1", "c79 `docs/OPERATOR_DECISIONS.md` entry #20 appended additively (v5 reopening verbatim + c79 first-cycle disclosures). Pre-append sha `b563caee0f81db969035674b20432d018424eb563dbd6102beb4e8b81dd0410b`; post-append sha pinned in the ledger event.", "Additive append; pre/post SHAs pinned.", "—"),
 ("M-V5-CORPUS-1/corpus-manifest-emitted-c79", "G4", "c79 P1: `scripts/v5/corpus_manifest.py` -> `data/v5/corpus/corpus_manifest.json` (sha `73362136…`), 26 songs enumerated (13 band-6 + 10 band-7 + 3 band-5 focus) with sha16/audio_sha256/duration/band/in_v5_corpus/v5_tier/v5_priority_rank + per-song asset inventory (no full-length stems on disk for any song; 30 s section stems + MuScriptor JSONs listed; tempo anchors from on-disk tempo_choice.json; rc5 baseline dir ABSENT per invariant (d)). Byte-det x2. Count discrepancy vs operator's ~7 disclosed; nothing truncated.", "Manifest byte-det x2; >=7 songs; disclosure present.", "M-V5-CORPUS-1"),
 ("M-V5-CORPUS-1/tempo-v5-halt-honest-c79", "G4", "c79 P2: `scripts/v5/tempo_v5.py` (pre-registered flat-band autocorrelation criterion) + `tempo_v5_verdict.py`. 26 per-song `tempo_v5.json` + `tempo_v5_summary.tsv`, byte-det x2 (27/27). FROZEN falsification verdict = **RULES_OUT_CRITERION_TOO_PERMISSIVE**: Peach Dream 123.05 -> 80.75 and Disco A 123.05 -> 80.75 (3:2 lag out-scores the anchored lag; non-octave regression > 2 BPM) while CG (92.29, delta +1.56), Rome (152.00, delta 0) hold. WIG finding: on the FULL-LENGTH mix librosa already returns 99.38 (the c20 50.17 came from the 30 s DRUMS-STEM section); the octave-candidate + plausibility band resolves the drums-stem probe 49.69 -> 99.38 but via the band, not autocorrelation dominance (ac(2T)/ac(T) = 0.32). Criterion NOT retuned (FD-1). Figure `data/v5/corpus/fig_tempo_v5_autocorr.png`.", "Per-song JSON byte-det x2; frozen verdict recorded with failing lag tables; >=6 tests green.", "M-V5-CORPUS-1"),
 ("M-V5-CORPUS-1/full-length-transcription-launched-c79", "G4", "c79 P3: `scripts/v5/transcribe_full_length.py` (composes READ-ONLY `recreate_v3` stage functions + `stage_cache`; per-probe MuScriptor caching; canonicalize at bpm_v5; delete-after-transcribe hygiene; c27 prune step deliberately NOT used because it deletes FROZEN `data/v4/profiles/**` WAVs). Launched detached via c24 `launch_detached` (setsid blocked by sandbox): PID + log pinned in `data/v5/logs/transcribe_full_c79.launch.json`. 26 songs in v5_priority_rank order (WIG first). Exact resume command pinned.", "PID + log pinned; stage-cache manifests for >=1 song; df <= 90% (max observed recorded); frozen anchors byte-identical.", "M-V5-CORPUS-1"),
 ("M-V5-EAR-1/ear-venv-probe-c79", "G3", "c79 P4 (optional): `python3 -m venv workspace/ear_venv` + `pip install \"numpy<2\" tensorflow tensorflow_hub pyloudnorm` FETCH_OK through the proxy (~55 s); import probe OK. Disk then read 93% (> 90% ceiling) with P3 running, so the venv was REMOVED after capturing receipts (`data/v5/ear/ear_venv_pip_freeze.txt` sha `a4d23dea…`, `env_pin_ear_venv.json`, `fetchability_ladder.jsonl`). VGGish inference probe DEFERRED to c80/c81 (rebuild is deterministic from the pinned command). Main-env `pip freeze` sha `90ed1d9f…` pre==post.", "Ladder row present; receipts present; main-env freeze SHA unchanged; deferral reason one line.", "M-V5-EAR-1"),
 ("M-V5-CORPUS-1/252eb21ce7df7328-transcribed-c79", "G4", "c79 P3 first full-length landing: What If I Go (186.1 s) transcribed end-to-end in-cycle — htdemucs_6s 181 s; MuScriptor 7 probes (drums 144 s, bass 71 s, guitar 130 s, other 243 s, piano 137 s, vocals 170 s, full_mix 417 s); note_on counts drums 862 (kick 202 / snare 227 / hat 386 / other 47), bass 83, guitar 384, other 1799 (synth_lead 1730 + synth_pad 69), piano 706 (electric_piano 356 + organ 301 + acoustic_piano 49), vocals 664, full_mix 3144; 77.07 bars at bpm_v5 99.384; 7 transient WAVs (230 MB) deleted; df max 86.6 %. The v4 'other/piano = zero notes' defect does NOT reproduce at full length with the c3 vocab.", "transcription_manifest.json + 7 muscriptor JSON + 7 canonical MIDI + 10 stage-cache manifests on disk; transient audio deleted.", "M-V5-CORPUS-1/full-length-transcription-launched-c79"),
 ("_plan/register-c79-v5-reopening-sub-leaves", "G1", "c79 POR registration row: 5 M-V5-* parent rows + c79 sub-leaves inserted inline in the `## Milestones` parseable region.", "Rows added.", "—"),
 ("_infra/adopt-cycle79-tests", "G1", "c79 test-adoption: `tests/test_tempo_v5.py` 7/7 PASS (WIG not half-time incl. drums-stem probe; CG anchor; PD target recorded halt-honest; octave candidate set; fresh-subprocess byte-det + corpus-wide 27/27; AST discipline scan; env-pin + manifest shape). Regression 35/35 pre-c79 green -> 42/42 cross-cycle.", "7/7 new + 35/35 regression green.", "—"),
 ("_archive/cycle-79-scratch", "G1", "c79 scratch archival: `tools/_emit_c79_ledger_events.py` + `tools/_register_c79_por_rows.py` retained in-tree per emitter-exemption pattern; session scratchpad probes not in workspace; transient full-length audio deleted by the driver per hygiene.", "No workspace scratch to archive.", "—"),
 ("_run/cycle_79_closed", "G1", "c79 CLOSED — v5 REOPENING cycle 1. See ledger event narrative for the 9-header closing summary.", "Cycle rollup after named sub-leaves.", "—"),
]

def main() -> int:
    txt = POR.read_text()
    lines = txt.splitlines(keepends=True)
    idx = next(i for i, l in enumerate(lines) if l.startswith("## Sub-milestones"))
    existing = set()
    for l in lines[:idx]:
        if l.startswith("| "):
            existing.add(l.split("|")[1].strip())
    new = []
    for mid, goal, desc, crit, deps in ROWS:
        if mid in existing:
            continue
        new.append(f"| {mid} | {goal} | {desc} | {crit} | {deps} |\n")
    if not new:
        print("IDEMPOTENT: all c79 POR rows present"); return 0
    # insert before the blank line preceding '## Sub-milestones'
    ins = idx
    while ins > 0 and lines[ins - 1].strip() == "":
        ins -= 1
    lines[ins:ins] = new
    POR.write_text("".join(lines))
    print(f"inserted {len(new)} rows before line {ins + 1}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
