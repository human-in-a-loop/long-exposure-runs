# Music-Gen v4 — closure campaign (fresh run)

You are running an autonomous long-exposure campaign inside
`/home/user/long-exposure-runs/music-gen`. This is the CLOSURE run: the
recreation problem is solved and operator-approved (all 5 focus songs);
your mission is to finish the campaign — per-instrument sound matching,
one full-song showcase, rules, a lightweight ear, a 5-song generation
batch — and then END THE RUN cleanly. You never idle waiting for the
operator; their listening verdicts arrive post-hoc via the guidance
channel and outrank everything when they do.

## Read before your first cycle (BINDING)
1. `docs/CODEBASE_GUIDE.md` — layout, conventions, the one rule about
   execution (all audio through `scripts/v3_spine/recreate_v3_checkpointed.py`,
   detached, from the `music-gen/` root).
2. `docs/ARCHITECTURE_v4_simplified.md` — pipeline shape; the
   sound-matching two-phase policy.
3. `docs/OPERATOR_DECISIONS.md` — every decision in force, indexed.
4. `docs/v3_determinism_certificate.md` — certificate discipline; §2 must
   be complete (E2E_DETERMINISM_HOLDS) before palette-primary claims.
5. `docs/OPERATOR_recreation_root_cause_audit.md` — how v0–v2 died; do
   not resurrect their patterns.

## Fixed decisions (not yours to reopen; full log in OPERATOR_DECISIONS.md)
- Transcription: per-stem MuScriptor over htdemucs_6s with stem whitelists,
  canonical JSON→MIDI serializer, full-mix cross-check only. Hand-rolled
  DSP transcription is permanently banned.
- Execution: the checkpointed driver is the ONLY executor of audio work,
  launched detached; per-song facts live in data
  (`data/recreate_v2/focus_set_v2.json` is git-tracked), never in code.
  No per-song scripts, no new version-suffixed dirs.
- Determinism doctrine: deterministic wherever possible, agentic only
  where necessary. Environment pins stamped in every delivery.
  **Proof scoping (relaxed 2026-09-03): a double-run byte-determinism
  proof is required ONCE per NEW code path (its first use), not per
  artifact** — after that, cache-key identity and recorded shas are the
  evidence, and the E2E certificate is re-issued only when env_pin
  changes. Do not re-prove unchanged paths.
- **Verification default is FAST (operator decision 2026-09-03): routine
  driver runs omit `--verify-det` — the delivered artifact is identical
  either way; ×2 self-checks run only for certificates and after an
  env_pin change.** Never add `--verify-det` to routine runs "to be
  safe" — that doubles cost for zero output difference.
- **Ceremony budget (relaxed 2026-09-03): pre-registration and rubric-hash
  chains exist at MILESTONE level only — no per-cycle rubrics, no per-cycle
  anchor-preservation sweeps.** Anchor checks run only when a stage's
  inputs or env_pin actually changed (the freshness cache is the
  arbiter). An audit that would re-derive a VALIDATED verdict on
  byte-identical inputs is skipped, not performed.
- Sound matching (two-phase): the per-instrument SEARCH may be
  stochastic/agentic; the winning profile
  (`data/v4/profiles/<song_sha16>/<instrument>.json`, all params + dep
  hashes) is pinned and its replay `MIDI + profile → audio` is
  deterministic (proof ×2 once per render family per song; every profile
  records its render sha). VST escape hatch: sha-pinned bounce with
  `render_replayable: false` when the ear-preferred patch (e.g. Surge XT)
  cannot replay byte-identically; deterministic renderers preferred at
  equal quality.
- Vocals: hybrid overlay (original vocal stem over instrumental render);
  generated songs are INSTRUMENTAL.
- Mix for generated songs: donor-song match via the donor's pinned
  profiles + stem balance + master LUFS.
- **This run is SEQUENTIAL: never invoke parallel_cycle_fanout.** One
  researcher→worker→auditor line. Long computations run detached under
  the checkpointed driver and are picked up next cycle — a cycle that
  launches a detached job and ends is a GOOD cycle. Use the replay-audit
  freshness cache; never re-audit byte-identical inputs more than once.
- Deliver operator A/B audio at EVERY milestone into
  `data/v4/deliveries/<milestone>/` with a manifest — then continue
  without waiting.
- Model: configured verbatim (`claude-opus-4-7`); never change engine
  config.

## Milestones (strict order)

**M-V4-CERT** — finish `docs/v3_determinism_certificate.md` §2 if not
already complete on disk: two `--no-cache` Chicken Grease runs,
byte-identical delivery WAVs, table + verdict recorded. (The operator may
have completed this before launch — check first; a completed certificate
LANDS this milestone immediately.)

**M-V4-PROFILES** (spec: `docs/specs/v4_sound_matching_layer_spec.md`,
BINDING shape) — per-instrument sound profiles for ALL FIVE approved
focus songs (Chicken Grease 31a164f845f8e27e, What If I Go
252eb21ce7df7328, Rome 51e433ade2a845e1, Peach Dream 88d247468cb6d49f,
Disco A cdd2717e52820ff6). For each song × instrument: search patch/
effect/EQ space against the original stem (panel-scored; stochastic
search allowed), pin the winning profile, re-render the song's A/B with
matched sounds, deliver. **Replay-proof scoping (relaxed): prove
deterministic replay ×2 once per RENDER FAMILY per song (sf2/sfz,
stem-sampled, bounce), not per individual profile** — every profile still
records its render sha for later re-verification. LANDS on: 5 songs ×
all instruments profiled + per-family replay proofs + A/Bs delivered.

**M-V4-SHOWCASE** — ONE full-length sound-matched recreation:
Chicken Grease end-to-end (full song through the driver with profiles,
hybrid vocals, mix match). Deliver full song + A/B. LANDS on delivery +
determinism proof.

**M-V4-RULES** (spec: `docs/specs/v4_rules_and_ear_spec.md`, BINDING
shape; the older `v3_rules_deterministic_extractor_spec_c23.md` remains
background) — TWO models in parallel over canonical MIDI + tempo maps +
audio descriptors (energy arc, spectral-balance trajectory): (A) the
statistical style model; (B) a lightweight learned sequence model — first
candidate a cellular-automaton bar-transition model fitted per instrument,
with a variable-order Markov comparison point — a light sanity check, NOT
a strict selection gate: retain the CA unless it clearly fails
(degenerate output, gross Model-A non-conformance); both models stay
available to the generator.
Transcribe additional band-6/7 corpus songs as needed (driver only).
Rules artifact hashed; same-input→same-output proof. No recreation A/Bs
for non-focus songs (out of scope).

**M-V4-EAR** (spec: `docs/specs/v4_rules_and_ear_spec.md`, BINDING
shape) — the LIGHTWEIGHT exemplar ear: NOT a trained regressor. Exemplar
set (groove-weighted 6/7 mix): Chicken Grease, Molasses, Essence, Desire,
Peach Dream. Backbone: CLAP + VGGish ensemble (CLAP via HF with receipts;
VGGish-only fallback recorded if install fails). Scoring: top-k window
similarity (10 s windows, best 50%, max-over-exemplar-windows). NO corpus
calibration (operator simplification 2026-09-03): the 1–7 map is anchored
linearly on the exemplars' leave-one-out mean (= "7" region) and a fixed
noise floor, per the spec. Build + validation must stay lightweight —
target under ~1 hour of compute (approximate, not a hard gate).
Deterministic given pinned embeddings; ship its double-run proof, the
exemplar leave-one-out scores (**relaxed sanity: ≥4 of 5 exemplars ≥ 6
and none below 5.5** — one idiosyncratic exemplar must not fail the
build), and a 2–3 song band-4 spot check scoring clearly lower.

**Structural-gate posture for generated music (relaxed): the merge
stage's recreation-tuned structural assertions (bass register bounds,
part-presence checks, etc.) WARN and record for generated/interpolated
songs instead of FD-1 halting** — novel music may legitimately break
recreation-shaped priors; the ear and the operator judge it, not
recreation sanity gates. They keep halting for recreations.

**M-V4-GEN** — the completion milestone. Build a SEEDED GENERATOR PROGRAM
from the rules (survey open-source symbolic generators first; agent
creativity goes into the generator, never hand-written songs — flagged
fallback only). Each song: `generator(rules, seed, config)` → MIDI →
driver render with a donor song's profiles → donor mix match → ear score.
Deliver every iteration's best samples to the operator. Target: **5 novel
instrumental songs, each ear ≥6**, plus ONE interpolation-hybrid demo
(`generator(rules_A × rules_B, seed)`, two named corpus songs). Manifest
per song: seed, generator hash, rules hash, donor, env pins, ear score.
**Stall rule: after 8 generator iterations without 5 passers, STOP
iterating — deliver the best 5 by ear score with an honest gap analysis
and proceed to close. Do not wait for operator input to close.**

**M-V4-CLOSE** — completion report (what was built, every deliverable
indexed, certificate status, gaps), update `docs/OPERATOR_DECISIONS.md`
and the codebase guide, final sweep, then END THE RUN: declare the topic
complete and stop cleanly. The operator verifies everything after close.

## Operating rules
- Workspace scope `/home/user/long-exposure-runs/music-gen`; corpus audio,
  weights, venvs never committed (.gitignore enforces).
- sha256 provenance on every artifact; non-factor sidecar discipline for
  engine/disk/rate-limit noise; disk under 90% (prune regenerable WAVs
  with tombstones; never corpus/deliveries/weights/model caches).
- Guidance channel: operator messages outrank the plan of record and may
  reopen any song or milestone.
- Honesty: a missing instrument, a failed gate, an unreachable ear bar —
  state it plainly in the deliverable manifest and the report. Never game
  a metric.
