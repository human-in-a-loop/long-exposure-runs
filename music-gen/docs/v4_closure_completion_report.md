# Music-Gen v4 — closure completion report

**Cycle:** c21 (closure)
**Date:** 2026-09-04
**Verdict:** All six closure milestones reached terminal state. Two closed with **honest gaps** (M-V4-PROFILES-1 partial: CG 5/5 terminal, 4 non-CG songs blocked_on_operator on M-V4-METRIC-SEMANTICS-c16 escalation, ×2 replay proofs and delivery per FD-16(c) scope; M-V4-GEN-1 reached the 8-iteration stall rule with 3 of 5 passers). No cycle idled on the operator; the run drove itself to close per campaign prompt directive.

**Model config verbatim throughout:** `claude-opus-4-7`.

---

## Milestone status (strict order)

| # | Milestone | Status | Verdict |
|---|-----------|--------|---------|
| 1 | M-V4-CERT-1 | TERMINAL | `E2E_DETERMINISM_HOLDS` (2026-09-03) — cert_run1/cert_run2 `full_reconstruction.wav` SHA `cc919559b4508b6bfe86…`, `env_pin_sha256=623df01f…` |
| 2 | M-V4-PROFILES-1 | LANDS_partial | CG 5/5 terminal (bass_v2 accepted OPT1-with-OPT3-corrected-threshold; drums OPT3; guitar OPT3; piano/other audibility-grounded NULL). Non-CG 4/5 songs (WIG/Rome/Disco A/Peach Dream) skeleton-only (stem_manifest.json); stage-1 sweeps blocked_on_operator on `_manager/M-V4-METRIC-SEMANTICS-c16` escalation. Per-family replay proofs held under FD-16(c). |
| 3 | M-V4-SHOWCASE-1 | LANDS_pending_operator | `data/v4/deliveries/31a164f845f8e27e/cg_ab_mix.wav` (sha `6e13e007…`) rendered c17; byte-det ×2 `REPLAY_PROOF_HOLDS`; per-cell provenance manifest; operator ear = LANDS authority per FD-6 (post-hoc). |
| 4 | M-V4-RULES-1 | LANDS | Substantive c21 extractor. Model A (statistical style, per-song + aggregated) + Model B (1D CA radius-1 per instrument, VOMM order-2 comparison) + audio-descriptor arcs (energy, spectral balance, LUFS) across 5 focus songs. Byte-determinism ×2 HOLDS. |
| 5 | M-V4-EAR-1 | LANDS | Lightweight exemplar ear via VGGish (CLAP unavailable — `torchvision::nms` missing per `data/texture/embedding_rung.log`; VGGish-only fallback per spec §backbone). 10s windows, hop 5s, top-k window similarity (mean of best 50%). Linear anchor on LOO mean + noise-floor. Byte-determinism ×2 HOLDS. Sanity bar met: 5/5 exemplars ≥6 leave-one-out; none <5.5. |
| 6 | M-V4-GEN-1 | LANDS_stall_rule | Seeded generator over Model A scaffolding + Model B CA/VOMM bar-to-bar; deterministic hash-driven sampling (no PRNG). 8 iterations, 3 passers ≥6 (6.9440/6.7938/6.2886), 2 near-misses (5.3804/5.3196). Best 5 delivered per stall rule. Interpolation-hybrid CG × Peach Dream (donor A key/tempo, donor B CA tables) delivered at 5.9394. |
| 7 | M-V4-CLOSE-1 | LANDS (this document) | Completion report published; final sweep; run ended cleanly. |

---

## Deliverables index (indexed by artifact)

### M-V4-CERT-1
- `docs/v3_determinism_certificate.md` §2 (verdict recorded 2026-09-03)
- `data/v3/deliveries/31a164f845f8e27e/cert_run1/full_reconstruction.wav` sha `cc919559b4508b6bfe868fa5433a50b6805c43bab763665a5f2be367f01bbbd7`
- `data/v3/deliveries/31a164f845f8e27e/cert_run2/full_reconstruction.wav` sha `cc919559b4508b6bfe868fa5433a50b6805c43bab763665a5f2be367f01bbbd7`
- env_pin_sha256 `623df01f262ffd180c8497ce9bb06a2d4438b9239d60dd997304830b6571d38d`

### M-V4-PROFILES-1 (CG cells terminal)
- `data/v4/profiles/31a164f845f8e27e/bass.json` (drawbar organ top-1 by composite; STILL_INDETERMINATE)
- `data/v4/profiles/31a164f845f8e27e/bass_v2.json` — accepted per operator directive 2026-09-03 (`profile_id d62cd3b6-4521-5d4f-b840-87ef7800c48d`)
- `data/v4/profiles/31a164f845f8e27e/drums.json` (Power Kit top-1 by composite)
- `data/v4/profiles/31a164f845f8e27e/drums_family_verdict.json` (SF2_RULED_OUT)
- `data/v4/profiles/31a164f845f8e27e/drums_arc_closeout.json` (CG_DRUMS_ARC_EXHAUSTED_NO_CONFIRMED)
- `data/v4/profiles/31a164f845f8e27e/guitar.json` (Jazz Guitar top-1 by composite)
- `data/v4/profiles/31a164f845f8e27e/guitar_family_verdict.json` (SF2_RULED_OUT)
- `data/v4/profiles/31a164f845f8e27e/guitar_arc_closeout.json` (CG_GUITAR_ARC_EXHAUSTED_NO_CONFIRMED)
- `data/v4/profiles/31a164f845f8e27e/piano_null_finding.json` (audibility-grounded)
- `data/v4/profiles/31a164f845f8e27e/other_null_finding_c14.json` (audibility-grounded)
- Replay proofs: bass sf2 `832868d0…`, bass_v2 sf2 `832868d0…`, drums sf2 `dadafcfc…`, drums family-2 `69a76c5b…`, guitar sf2 (present), guitar family-2 `f41560714…` — REPLAY_PROOF_HOLDS each

### M-V4-PROFILES-1 (non-CG skeletons)
- `data/v4/profiles/252eb21ce7df7328/stem_manifest.json` (WIG)
- `data/v4/profiles/51e433ade2a845e1/stem_manifest.json` (Rome)
- `data/v4/profiles/88d247468cb6d49f/stem_manifest.json` (Peach Dream)
- `data/v4/profiles/cdd2717e52820ff6/stem_manifest.json` (Disco A)

### M-V4-SHOWCASE-1
- `data/v4/deliveries/31a164f845f8e27e/cg_ab_mix.wav` sha `6e13e0075c5d8116…f9484b`
- `data/v4/deliveries/31a164f845f8e27e/cg_ab_mix.manifest.json`
- `data/v4/deliveries/31a164f845f8e27e/cg_ab_mix.replay_proof.json` (byte-det ×2 HOLDS)
- `data/v4/deliveries/31a164f845f8e27e/cg_ab_mix.lufs_diagnostic.json`

### M-V4-RULES-1
- `data/v4/rules/rules_artifact.jsonl` sha `0503d56ec0ac1a34761d4b51aefba55ae4df5352395ca611a0f89d535b9cf4cf` (97 rules across 5 categories: 23 harmonic + 23 rhythmic + 23 melodic + 23 form + 5 arrangement)
- `data/v4/rules/statistical_model.json` sha `8431f098bb96bc6b7457411dca6f646c412b5bfef393a826e7e36e8497a62030` (Model A per-song + per-band-aggregate)
- `data/v4/rules/sequence_model.json` sha `e2e37e8d9f1a0422e3b30fc037ed35e9abcba64416e99441d7290f6a21ef08be` (Model B CA + VOMM per instrument per song)
- `data/v4/rules/audio_descriptors.jsonl` sha `e93446a3d94baf28d36a1db11796777286ed23066c935c6fa1a76f7940c8f1ed`
- `data/v4/rules/ca_retention_summary.json` (13 of 23 non-empty instrument cells CA-retained; 10 non-retained due to degenerate 8-step generation on short bar sequences; both models remain available per spec)
- `data/v4/rules/manifest.json` sha `4b63feaaf179d46fbdb896b75427c2970abf55beaf8acd4a12606aac3fc36859`
- `data/v4/rules/replay_proof.json` (byte-det ×2 across all 7 artifacts)

### M-V4-EAR-1
- `data/v4/ear/ear_scores.json` sha `b2f5e9bd983ad18a312b9da6fdbb379f29bf28bdab1b10dc42b790f4ca636640`
- `data/v4/ear/exemplar_embeddings.npz` sha `be93d016c7cc0eb39e51fa47c0de11847b43f03a68ae7535cf098daff7e3751f`
- `data/v4/ear/band4_embeddings.npz` sha `4fc8dc828e425d0280733497229d03ca26f23348c61ba001c0c31e7668b26024`
- `data/v4/ear/manifest.json` sha `2ef02815f6019e993c75ae5f778e54ae693e1a86440dbb78550657d050d1c0cf`
- `data/v4/ear/replay_proof.json` (byte-det ×2 HOLDS)

Exemplar leave-one-out scores (1–7): Chicken Grease **7.0**, Peach Dream **7.0**, Molasses **7.0**, Essence **7.0**, Desire **6.16**. Band-4 spot check: Aguanile 5.18 (clearly lower), Wagon Wheel 6.12 (close to Desire), Stay (Live) 7.0 (saturates — first-class honest finding: one of three band-4 songs shares enough VGGish embedding characteristics with the exemplar pool to score at exemplar level; CLAP ensemble would likely disambiguate but is unavailable in this environment).

### M-V4-GEN-1
- `data/v4/generated/batch_full/batch_report.json` (8 iterations, 3 passers, top 5 by ear)
- `data/v4/generated/batch_full/iter_*/manifest.json` (per-song seed + generator hash + rules hash + donor + env pin + ear score)
- `data/v4/generated/batch_full/iter_*/merged.mid` (7 tracks, instrumental — vocals empty)
- `data/v4/generated/batch_full/iter_*/song.wav` (fluidsynth-rendered under deterministic pins)
- `data/v4/generated/hybrid_cg_x_pd/manifest.json` + merged.mid + song.wav (interpolation-hybrid demo, donor A = CG for key/tempo, donor B = Peach Dream for CA tables)

Best 5 by ear (batch_full): 6.9440, 6.7938, 6.2886, 5.3804, 5.3196. Passers (≥6): 3 of 5. Hybrid demo: 5.9394.

---

## Certificate status

**End-to-end determinism certificate — v3 spine:** `E2E_DETERMINISM_HOLDS` on Chicken Grease under `env_pin_sha256=623df01f…`; re-issue trigger = env_pin change (FD-16(a)).

**Extended v4 satellite proofs:**
- M-V4-RULES-1 extractor `scripts/v4_rules/extract_v4.py`: byte-determinism ×2 across 7 artifacts under canonical 7-key env-pin `2ac444c3…922ca` (proof `data/v4/rules/replay_proof.json`).
- M-V4-EAR-1 ear `scripts/v4_ear/ear.py`: byte-determinism ×2 across 5 artifacts (JSON + NPZ) under canonical env-pin **with `TF_ENABLE_ONEDNN_OPTS=0`** forced (proof `data/v4/ear/replay_proof.json`).
- M-V4-GEN-1 generator: per-song manifests carry `midi_sha256` + `song_wav_sha256` + `generator_hash` + `rules_hash`; deterministic replay is cache-key-carried per FD-16(a). No PRNG imports; sampling via SHA-256-derived index stream.
- Per-family M-V4-PROFILES-1 replay proofs (CG): sf2 (bass, bass_v2, drums, guitar) + family-2 stem-sampled (drums, guitar) — REPLAY_PROOF_HOLDS each per FD-16(c) per-render-family-per-song scope.

---

## Gaps (honest disclosure)

1. **M-V4-PROFILES-1 partial on 4 songs.** WIG/Rome/Disco A/Peach Dream reached skeleton (stem_manifest.json) at c17/c18/c19 but stage-1 sweeps did not launch. Blocked_on_operator on `data/v4/_manager/M-V4-METRIC-SEMANTICS-c16.json` — a genuine operator-authority sign-convention question about the panel's `embedding_cos_vggish` field (Path A: field is a distance as coded and thresholds need re-derivation; Path B: field name renamed to similarity and composite arithmetic corrected). Both paths violate operator-anchored contracts equally under the agent-picks invariants (auto_resolvable = false). Anti-stall rule (2026-09-03 part 2) BANS wait-on-operator memos, so this cycle proceeded through the remaining milestones without adjudicating. Downstream impact: the CG showcase is unaffected (operator ear = LANDS authority per FD-6); rules/ear/generator all use MIDI+audio corpora that are unaffected by the sign-convention question.

2. **M-V4-GEN-1 3-of-5 passers, not 5-of-5.** The 8-iteration stall rule fired. Scores 6.94/6.79/6.29 clear the ≥6 bar; 5.38/5.32 miss it. Root-cause candidates: (a) VGGish-only ear (no CLAP ensemble) has a narrower discriminating dimensionality on synthesizer-rendered content vs original acoustic exemplars; (b) fluidsynth-rendered generated songs share less timbral space with the exemplars (all human-performed acoustic/electric bands) than the exemplars share with each other; (c) 16-bar generated sections may under-represent the "strong stretches" the top-50% window statistic rewards; (d) the CA + VOMM fallback chain collapses to hash-driven fallback on 10 of 23 stems (see `ca_retention_summary.json`). Per campaign prompt stall rule, delivered best 5 with this analysis and proceeded to close. Do not iterate.

3. **Ear backbone is VGGish-only, not CLAP+VGGish ensemble.** CLAP install fails on this system (`torchvision::nms` missing per `data/texture/embedding_rung.log` from cycle 4). Per spec §backbone this fallback is allowed and recorded. Downstream discrimination on synthesized vs original content is likely narrower than the ensemble would give.

4. **CA retention 13 of 23 non-empty instrument cells.** 10 cells failed the "not degenerate under 8-step self-generation" retention test (all-off or all-on attractor from the fitted rule table on short bar sequences). Both models remain available to the generator per spec; generator falls back to VOMM order-2 or hash-driven bit sampling when CA is not retained. This is a real corpus-size finding, not a bug.

5. **Band-4 sanity spot check has one saturating song.** Stay (Live) scores 7.0 — the same as most exemplars. This reflects VGGish's timbre-forgiving property on decoded audio: a band-4 song sharing R&B/pop timbral character with the exemplar pool saturates the top-k similarity statistic. The other two band-4 songs (Aguanile 5.18, Wagon Wheel 6.12) show the expected ordering. Per spec, the operator sanity bar (≥4 of 5 exemplars ≥6 LOO, none <5.5) is the LANDS gate, and it PASSES; the band-4 spot check is a soft heuristic.

---

## What was built (files added/edited this cycle)

New:
- `scripts/v4_rules/extract_v4.py` (substantive, replaces c20 scaffold in place)
- `scripts/v4_rules/__init__.py` (re-exports)
- `scripts/v4_ear/__init__.py` + `scripts/v4_ear/ear.py`
- `scripts/v4_gen/__init__.py` + `scripts/v4_gen/gen.py` + `scripts/v4_gen/hybrid.py`
- `data/v4/rules/{rules_artifact.jsonl, rules_artifact.sha256, statistical_model.json, sequence_model.json, audio_descriptors.jsonl, ca_retention_summary.json, manifest.json, env_pin.json, replay_proof.json, run1/, run2/}`
- `data/v4/ear/{ear_scores.json, exemplar_embeddings.npz, band4_embeddings.npz, manifest.json, env_pin.json, replay_proof.json, run1/, run2/}`
- `data/v4/generated/{batch_c21/, batch_full/, hybrid_cg_x_pd/}`
- `docs/v4_closure_completion_report.md` (this file)

Edited:
- `docs/OPERATOR_DECISIONS.md` (adds decision 17 — closure verdict noted)
- `docs/CODEBASE_GUIDE.md` (adds v4_rules / v4_ear / v4_gen locations to the Map)

Not touched (READ-ONLY anchors per FD-1 discipline):
- Entire `scripts/v3_spine/` and `scripts/recreate_v2/` trees
- `docs/v3_determinism_certificate.md` §2 (already terminal)
- Every c1–c15 CG-arc profile, verdict, and replay-proof anchor
- The c17 `cg_ab_mix.wav` showcase render
- `_manager/M-V4-METRIC-SEMANTICS-c16.json` escalation (operator authority)

---

## Operator hand-off

The operator's ear on the c17 CG A/B (`data/v4/deliveries/31a164f845f8e27e/cg_ab_mix.wav`) remains the final LANDS authority on M-V4-SHOWCASE-1 per FD-6.

To resume the 4 non-CG PROFILES cells: adjudicate `data/v4/_manager/M-V4-METRIC-SEMANTICS-c16.json` (choose Path A or Path B), then the queued stage-1 sweeps for WIG/Rome/Disco A/Peach Dream can launch under the resolved semantics.

To improve M-V4-GEN-1 pass rate: enable CLAP (install `torchvision` with matching wheel to fix `nms` operator; then let the ensemble score guide iteration), or extend the corpus so Model B's CA retention rate rises above 13/23. The generator is a pure function of (rules, seed, config); an operator-directed re-run with more seeds against a richer rules artifact should improve pass rate without agent redesign.

---

## Close

Per the campaign prompt final line: "M-V4-CLOSE — completion report (what was built, every deliverable indexed, certificate status, gaps), update docs/OPERATOR_DECISIONS.md and the codebase guide, final sweep, then END THE RUN: declare the topic complete and stop cleanly. The operator verifies everything after close."

**The Music-Gen v4 closure campaign is complete. Run ended cleanly.**
