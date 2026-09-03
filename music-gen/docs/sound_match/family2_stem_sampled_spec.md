---
created: 2026-09-03T00:00:00Z
cycle: 5
run_id: run-2026-08-28T040704Z
agent: worker
milestone: M-V4-PROFILES-1/cg-bass-family2-stem-sampled
---

# Family-2 (stem-sampled) — spec for CG bass

**Scope.** Spec + spike cycle (c5). Builder implementation lands c6+. This document is
NOT a builder API contract yet; it fixes the reference contract, the render-family
identity, the sketch of the builder, the frozen objective panel + rubric, the replay
proof contract, storage discipline, and the fixed-decision anchors that must hold.

Family-2 is a distinct render family from sf2 (FD-16c). Its replay proof does NOT
cover sf2 and sf2's proof does NOT cover it.

## 1. Reference contract

- **Source stem (READ-ONLY):** `data/v3/deliveries/31a164f845f8e27e/cert_run1/stems_6s/bass.wav`
  sha256 = `1bad871901294395c1b1ad1c97689e07d879f48aa8b9fc953ea6981d76e09ffd`
  (6-second htdemucs bass stem for Chicken Grease).
- **Reference MIDI (READ-ONLY):** the c1 bass MIDI excerpt, sha16 `4863ca285c7db513`
  full sha256 `4863ca285c7db513c8bfc22da5e35e65036b0ecad2538a6d9794c80eb15f8ac9`
  (path resolved from c1 manifests / stage-1 leaderboard row provenance).
- **Reference song sha16:** `31a164f845f8e27e` (Chicken Grease).

## 2. Render family definition

- `render_family = "stem_sampled_v1"`.
- `identity` fields (typed):
  - `stem_source_sha256` (str, 64 hex) — hash of the reference stem consumed.
  - `pitch_mapping` (str) — e.g. `"librosa.effects.pitch_shift"` (spike default; builder
    may replace with a production choice in c6+).
  - `envelope_mode` (str) — ADSR-lite envelope shape name (spike: `"linear_ar"`).
  - `gain` (float) — post-sum broadband gain scalar.
  - `post` (dict) — post-chain descriptor (spike: `{"lufs_target_db": -18}`).
- Distinct from sf2 family; **not interchangeable** in replay proofs. A family-2
  profile carries `render_family = "stem_sampled_v1"`; a distinct family-2
  `replay_proof.json` must be emitted at profile-pin time.

## 3. Builder sketch (spike scope, NOT c5 implementation)

- **Input:** reference stem WAV + MIDI events (note_on/note_off with pitch, velocity,
  time) from `bass.mid`.
- **Approach:**
  1. Detect fundamental frequency of the reference stem (single scalar).
  2. Per MIDI note, pitch-shift the stem to the target MIDI pitch by
     `12 * log2(target_hz / stem_f0)` semitones (spike: `librosa.effects.pitch_shift`).
  3. Window each shifted copy with an ADSR-lite envelope (spike: linear
     attack/release, ~5 ms edges).
  4. Sum shifted copies at note onset times into an output buffer.
- **Explicitly out of scope for c5:** polyphony resolution, velocity-curve fitting,
  reuse of the EQ-v2 post-chain, tempo/beat inference. c5 delivers spec + smallest
  possible spike; c6+ implements the real builder.

## 4. Objective panel

- **Frozen panel** (identical to sf2 family — no reweighting this cycle):
  `mel_l1_db` + `spectral_centroid_rmse_hz` + `embedding_cos_vggish`
  with composite weights **0.5 / 0.25 / 0.25**.
- **Rubric (identical to sf2 family thresholds; pre-registered):**
  - **CONFIRMED** at `embedding_cos_vggish ≥ 0.60`.
  - **RULED_OUT** at `embedding_cos_vggish ≤ 0.40`.
  - **INDETERMINATE** otherwise.
- Composite is discriminative for search ordering only. Family verdict fires on
  `embedding_cos_vggish`.

## 5. Replay proof contract (per FD-16c)

- Family-2 needs its **OWN** `replay_proof.json` emitted at profile-pin time (not this
  cycle — no profile is pinned in c5).
- **Byte-determinism:** two identical renders under the frozen env pin must byte-match
  (`run1_sha256 == run2_sha256`).
- **Regression coverage (mandatory in the builder cycle):** two family-2 profiles
  differing only in `identity` fields (e.g. `envelope_mode` or `pitch_mapping`) MUST
  produce DIFFERENT replay SHAs. This test is the direct lesson from the sf2 defect
  captured in the c5 CRITICAL manager escalation (`_manager/M-V4-PROFILES-1-replay-program-invariance-critical`).

## 6. Storage discipline (from operator 2026-09-03 directive)

- Any candidate sweep in family-2 must obey **SCORE-AND-DELETE**: score each
  candidate render immediately and delete its WAV before rendering the next; keep
  only the running top-5 audio at any moment.
- Working audio ≤ **500 MB** per instrument during search.
- `df` check before each sweep stage; disk must not exceed 90%.
- These are procedure fixes, not findings.

## 7. Fixed-decision anchors

- **FD-1** — no tuning: verdicts fire honestly against the frozen rubric; no fallback,
  no retry against a landed verdict, no post-hoc reweighting.
- **FD-6** — operator ear is LANDS authority; internal-gate verdicts are
  `*_pending_operator`.
- **FD-16(a)** — env-pin re-issue on any change to the 7-key manifest.
- **FD-16(b)** — never pass `--verify-det`.
- **FD-16(c)** — per-family per-song replay proofs; family-2 needs its own.
