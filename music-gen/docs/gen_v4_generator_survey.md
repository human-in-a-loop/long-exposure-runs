<!--
created: 2026-09-06T00:00:00Z
cycle: 70
run_id: run-2026-09-06T000000Z
agent: worker
milestone: M-V4-GEN-1/generator-survey
-->

# M-V4-GEN-1 Symbolic Generator Survey (c70 scaffold)

Status: **registered** (scaffold only — c71+ iteration 1 uses the winner).

Purpose: enumerate open-source symbolic MIDI generators compatible with
our rules ledger + tempo maps + donor profiles, and pick the one that
best fits our determinism + inference-cost budget. This survey is
READ-ONLY external research; no code fetched or executed at c70.

## Evaluation rubric

Ranked per criterion 1-5 (higher = better). Weighted sum = final score.

| Criterion                | Weight | Rationale                                        |
|--------------------------|--------|--------------------------------------------------|
| Input compatibility      | 0.30   | Consumes canonical MIDI + tempo map + rules JSON |
| Determinism              | 0.30   | Seeded torch.manual_seed + fixed inference       |
| Cache footprint (weights)| 0.15   | Fits under 5 GB free disk after c47+ hygiene     |
| Inference cost / song    | 0.15   | Target < 5 min wall per 30 s song on CPU         |
| License                  | 0.10   | MIT / Apache / equivalent                        |

## Candidates surveyed

### 1. Anticipation (Thickstun et al., 2024)

- Repo: `stanford-crfm/anticipation` (public).
- Input: standard MIDI (multi-track, tempo events).
- Determinism: PyTorch model; `torch.manual_seed` + greedy or
  temperature-0 sampling → byte-deterministic under our BLAS pins.
- Weights: ~450 MB checkpoint.
- Inference: ~2 min/30 s on CPU (their reported figure; unverified).
- License: Apache-2.0.
- Rules-ledger interface: consumes MIDI directly; rules can be applied
  as a post-generation filter OR as a constrained-decoding gate (a
  simple whitelist of allowed pitches per bar per stem).

Score: (0.30·5) + (0.30·5) + (0.15·4) + (0.15·4) + (0.10·5) = **4.7**.

### 2. Music Transformer (Magenta / Huang et al., 2018)

- Repo: `magenta/magenta` (TF 1.x; last active ~2022).
- Input: NoteSequence protobuf, converts from/to MIDI.
- Determinism: TF 1.x graph-mode; seedable but non-trivial to pin
  end-to-end (see c25/c26 v3-ear numpy-downgrade thrash — TF is
  fragile in this env).
- Weights: ~200 MB.
- Inference: ~5 min/30 s on CPU.
- License: Apache-2.0.
- Concern: TF dependency conflicts with our c47+ frozen chassis
  (basic-pitch quarantined venv already used for TF). Would need a
  second quarantined venv.

Score: (0.30·5) + (0.30·3) + (0.15·5) + (0.15·3) + (0.10·5) = **4.0**.

### 3. MMM (Multi-Track Music Machine) / MidiTok + Transformer-XL fork

- Repo: `Natooz/MidiTok` (tokenizer) + community Transformer-XL fine-
  tunes for multi-track continuation.
- Input: MIDI → REMI+ tokens → model → REMI+ → MIDI.
- Determinism: PyTorch; `torch.manual_seed` + greedy → deterministic.
- Weights: variable (fine-tune-dependent); most public checkpoints
  ~300 MB.
- Inference: ~3 min/30 s on CPU.
- License: MIT (MidiTok) + variable (community fine-tunes).
- Concern: fine-tune quality is community-variable; we would need to
  either train a fine-tune ourselves (out of scope for the closure
  window) or pick one and audit it.

Score: (0.30·4) + (0.30·5) + (0.15·4) + (0.15·4) + (0.10·4) = **4.3**.

### 4. VOMM (variable-order Markov model, hand-built)

- No external repo — implementable as ~200 lines of Python from our
  rules ledger + tempo maps.
- Input: rules JSON + tempo map directly (no MIDI ingest).
- Determinism: trivially deterministic (SHA-256-seeded RNG or none).
- Weights: 0.
- Inference: <1 s / 30 s song.
- License: our own code.
- Concern: expressive ceiling is low — no long-range structure
  learning. Good as a **baseline** to compare Anticipation against;
  probably not good enough to hit 5 songs ≥ ear-6 on its own.

Score: (0.30·3) + (0.30·5) + (0.15·5) + (0.15·5) + (0.10·5) = **4.3**.

## Ranking

| Rank | Candidate            | Score |
|-----:|----------------------|------:|
|    1 | Anticipation         |  4.7  |
|    2 | MMM (MidiTok+TX-L)   |  4.3  |
|    3 | VOMM (hand-built)    |  4.3  |
|    4 | Music Transformer    |  4.0  |

## Selected primary + secondary

- **Primary**: Anticipation. Highest determinism × input-compat score;
  license clean; already-published inference cost fits our budget.
- **Secondary (baseline)**: VOMM (hand-built). Ships within one cycle;
  serves as an honest floor comparison for whatever Anticipation
  outputs.

## Interpolation-hybrid demo (per M-V4-GEN-1 target)

Operator target: "5 novel instrumental songs, each ear ≥ 6, plus ONE
interpolation-hybrid demo." Plan: use Anticipation to interpolate
between two accepted focus-song rule-vectors (e.g. Chicken Grease ↔
Peach Dream) via latent-space mix and emit one demo MIDI + render.

## What c71 iteration 1 must do

1. Fetch Anticipation weights + code (fetchability probe first).
2. Wire `generator(rules, seed, config) → MIDI` API.
3. Point it at donor profile 1 (Chicken Grease, per
   `data/v4/gen/donor_profile_map.json`) with seed=0.
4. Render via `deliver_ab_v4.py` shape (bass+drums sf2 replay + vocals
   overlay optional; NEW instrumental songs may omit vocals).
5. Score via M-V4-EAR (per spec — deferred until M-V4-EAR is built).
6. If ear ≥ 6, count as passer 1/5. If iteration budget (8) exhausts
   before 5 passers, STOP + deliver best 5 with honest gap analysis
   per M-V4-GEN-1 spec.

## Notes / caveats

- All candidate compute-cost figures are from public docs; NOT verified
  in this workspace at c70.
- Anticipation weights fetch requires HTTPS proxy access; c71 must run
  a fetchability probe first per c47+ pattern.
- No PRNG in the generator wrapper — all sampling must be
  `torch.manual_seed(seed)` or SHA-256-derived deterministic.
