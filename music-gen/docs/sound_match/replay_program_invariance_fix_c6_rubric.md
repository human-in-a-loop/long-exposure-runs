# Replay program-invariance fix — c6 rubric

## 1. Defect statement (verbatim from c4 auditor)

> scripts/sound_match/replay.py:_replay_sf2 L79-85 builds a program-select
> setup string but discards it via `_ = setup`; fluidsynth uses MIDI-embedded
> program_change instead of profile.identity.program; empirically confirmed by
> bass.replay_proof.json.run1_sha256 == bass_v2.replay_proof.json.run1_sha256
> == 832868d0... despite profile programs 17 vs 33.

## 2. Fix contract

- Replace L85 `_ = setup  # documentation` with real code that forces
  fluidsynth to honor `profile.identity.program`. This cycle implements the
  fix by pre-processing the source MIDI in memory (`mido`), stripping any
  embedded `program_change` events and inserting a fresh `program_change`
  at tick 0 of the first note-carrying track with
  `channel=0, program=profile.identity.program`. The rewritten MIDI is
  written to a stable sibling path next to `out_wav_path` and passed to the
  fluidsynth CLI as the input file.
- Rationale for MIDI-rewrite over `-o synth.default-preset=...`: fluidsynth
  has no `synth.default-preset` CLI setting; the shell command `select` is
  only available in interactive mode (`-i`), which the deterministic-render
  path disables via `-ni`. MIDI rewrite is a pure function of
  `(midi_path, program)`, deterministic, and preserves everything else about
  the source MIDI (note events, timing, meta).
- No behavior change is required for MIDIs whose embedded `program_change`
  already matches `profile.identity.program`. That is a diagnostic:
  bass_v2 (prog 33) against bass.mid (embeds prog 33) may or may not shift
  a few bytes depending on whether fluidsynth's `program_change` handling
  is idempotent on a same-value select.
- Constraint: do NOT restructure `_replay_sf2` further. Do NOT rename
  anything. Do NOT touch any other function or file under
  `scripts/sound_match/`. Preserve existing env-pin handling verbatim.

## 3. Regression test contract

- New test file `tests/test_sound_match_replay_program_invariance.py`.
- Test A (negative-inversion): build two minimal profiles differing ONLY in
  `identity.program` (17 vs 33). Invoke `replay()` on the same stripped
  MIDI (embedded `program_change` removed OR set to a third value like 0).
  Assert the two produced WAVs have DIFFERENT SHA-256.
- Test B (positive determinism): same profile invoked twice into fresh
  tempdirs must produce byte-identical SHA-256 (preserves
  `REPLAY_PROOF_HOLDS` scoping).
- Test C (existing-MIDI-neutrality): replay `bass_v2.json` against
  `bass.mid` (which embeds prog=33) yields the SAME SHA class as the
  program-33 case (i.e. the fix must not silently change output when the
  profile already agrees with the source program).

## 4. Verdict rubric (frozen 3-way)

- `REPLAY_FIX_LANDS`: fix in place AND Test A/B/C all PASS AND both
  refreshed replay proofs recompute `REPLAY_PROOF_HOLDS`.
- `REPLAY_FIX_PARTIAL`: fix in place AND Test A/B/C all PASS BUT exactly
  one of the two refreshed proofs regresses to `REPLAY_PROOF_FAILS`
  (surface honestly per FD-1; do not retry).
- `REPLAY_FIX_FAILS`: fix breaks any of Test A/B/C, OR breaks both proofs
  deterministically.

Rung-3 sanity: post-fix `bass.replay_proof.json.run1_sha256` MUST differ
from `bass_v2.replay_proof.json.run1_sha256`. If they are still equal, the
fix took no effect and the verdict is REPLAY_FIX_FAILS regardless of the
test suite result.

## 5. Env pin

Uses the unified canonical env_pin_sha256 emitted this cycle (see
`data/v4/profiles/31a164f845f8e27e/env_pin_c6.json`). The unified payload
is the 7-key replay-time subset that `scripts/sound_match/replay_proof.py`
already hashes; the sweep-time 9-key superset (adds
`pyloudnorm_available`, `lufs_target_db`) supersedes the c3 stage-2b
manifest for downstream audit but the replay-time SHA is the canonical
one stamped on refreshed proofs.

## 6. Three-way rubric_hash chain

The SHA-256 of this markdown file is pinned to
`data/v4/profiles/31a164f845f8e27e/replay_fix_c6_rubric_hash.txt` BEFORE
`scripts/sound_match/replay.py` is edited (mtime hard, git-log advisory
per c46 path (ii)). The final `replay_fix_verdict.json` carries a
`rubric_hash` field byte-equal to that pinned content and to this doc's
SHA-256 on disk at close-of-cycle. Any drift halts per FD-1.
