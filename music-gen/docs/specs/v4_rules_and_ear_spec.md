# v4 rules extraction + exemplar ear — implementation spec (operator-decided 2026-09-03)

Not a hardened spec; the decided shape is binding, details refine in place.

## Rules extraction — TWO models built in parallel

**Inputs (both models):** canonical per-stem MIDI + tempo map for the
focus 5 plus additional band-6/7 transcriptions (driver-produced), AND
per-song audio descriptors: energy arc (RMS over bars), spectral-balance
trajectory (band energies over bars), section-level LUFS — so generation
can target an energy SHAPE, not just note statistics. All extraction is
deterministic (same corpus in → same artifacts out, hashed).

**Model A — statistical style model (interpretable, samplable):**
per song and aggregated per rating band: tempo/key/mode distributions,
chord-transition matrices (beat-level harmony from the piano/guitar/bass
tracks), per-instrument groove templates (16th-grid onset histograms +
velocity profiles per bar position), note-density and register profiles,
bar/section-length statistics, and the audio-descriptor arcs above.
Artifact: `data/v4/rules/statistical_model.json` (hashed).

**Model B — learned sequence model (generative texture):** a lightweight
sequence learner suited to ~10–20 songs. First candidate per operator
suggestion: **cellular-automaton sequence model** — represent each
instrument's bar as a binary/velocity vector on the 16th grid; fit local
CA update rules (neighborhood → next-step state, per instrument) from
bar-to-bar transitions in the corpus, with a small parameter count that
suits tiny datasets; generation = seed row + T update steps (seeded ⇒
deterministic). A variable-order Markov model on the same token stream is
fitted as a COMPARISON POINT, but the benchmark is a light sanity check,
NOT a strict selection gate (operator direction 2026-09-03): retain the
CA model unless it clearly fails — degenerate output (static/all-off
patterns), gross Model-A non-conformance — even if Markov edges it on a
metric. Both models remain available to the generator; the generator may
blend them. Artifact: `data/v4/rules/sequence_model.json` + fitting
report.

**How the generator uses them:** Model A supplies global scaffolding
(tempo, key, form, chord path, energy arc targets); Model B supplies
bar-to-bar per-instrument pattern evolution; Model-A conformance acts as
a rejection filter on Model-B output. Both are pure functions of
(rules artifacts, seed, config).

## The exemplar ear (lightweight, no training loop)

**Exemplar set (groove-weighted 6/7 mix, pinned):** Chicken Grease,
Molasses, Essence, Desire, Peach Dream.

**Backbone: CLAP + VGGish ensemble.** Install CLAP (HF weights,
receipts + pins; laion-clap or msclap class); VGGish already proven.
Score = mean of the two backbones' similarities, each computed
identically; both embedding stacks pinned in env_pin. If CLAP cannot be
installed through egress, fall back to VGGish-only and record the
substitution in the ear manifest.

**Scoring shape: top-k window similarity.** Embed 10 s windows (hop 5 s)
of the candidate song; each window's similarity = max cosine over the
exemplar windows; song statistic = mean of the best 50% of windows
(rewards strong stretches, tolerates intros/outros).

**Calibration (operator simplification 2026-09-03 — NO corpus fit):**
the full-corpus isotonic calibration is dropped as unnecessary. Anchor on
the exemplars themselves: compute each exemplar's leave-one-out similarity
(scored against the other four); let `E` = mean of those five values and
`F` = a fixed floor (the similarity statistic of silence/noise, computed
once). Map linearly: score = 1 + 6·(s − F)/(E − F), clipped to [1, 7] —
so the exemplar region defines "7" and the ≥6 pass bar is simply
s ≥ F + (5/6)·(E − F). Sanity check: the five exemplars must self-score
≥ 6 leave-one-out, and two or three band-4 songs (spot check, not a
corpus sweep) must score clearly lower. Whole build target: well under
~1 hour (soft).

**Determinism:** embeddings, windowing, statistic, and calibration are
all deterministic given pinned weights; ship the double-run proof and a
full-corpus scorecard with the milestone.

**Role:** the ear gates M-V4-GEN (5 songs ≥6). It is a similarity ear —
it measures "sounds like the operator's favorite groove material," which
is the intended target, not general musical quality; the completion
report must state this framing honestly.
