# Test 2/5 — Adversarial: CG-bass arc closeout (c6–c9) + drums opening (c10–c11)

Scope: Delta test slice covering c6 replay-program-invariance fix, c7 CG-bass arc closeout, c9 OPT1+OPT3 hybrid acceptance fork, c10 CG-drums stage-1 sweep + c11 stage-2/profile/replay-proof/family-verdict and channel-aware replay CRITICAL fix.

## Checks executed

1. `scripts/sound_match/replay.py` c11 channel-aware `_replay_sf2` extension — VERIFIED source has channel-enumerating `program_change` insertion (lines 91–111), backward-compat statement "For pure-ch0 MIDIs this is byte-identical to c6" matches the c11 bass_v2 regression pin (`832868d0…`).
2. `data/v4/deliveries/31a164f845f8e27e/cg_bass_pinned_profile.json` (c9) parses; `acceptance_fork.chosen = "OPT1+OPT3 hybrid per operator 2026-09-03"`; `rejected = ["OPT2_REFUSE_SHOWCASE", "OPT3_THRESHOLD_ONLY"]`; `operator_authority` present. Substantively matches POR c9 OPT1+OPT3 fork.
3. `data/v4/deliveries/31a164f845f8e27e/cg_drums_pinned_profile.json` (c14 revise) `acceptance_option = "OPT3"`, `drums_source_for_showcase = data/v3/deliveries/31a164f845f8e27e/cert_run1/stems_6s/drums.wav`, 5-point invariant rationale (a)–(e) all present. Matches POR c14 canonical shape.
4. `data/v4/profiles/31a164f845f8e27e/drums.json` substantive content matches POR c11 (`profile_id 83728154-…`, `program 16 Power Kit`, `gain 1.0`, `reverb_send 0.7`, `post EQ_only`, `midi_channel 10`).
5. `data/v4/profiles/31a164f845f8e27e/drums.replay_proof.json` verdict `REPLAY_PROOF_HOLDS`, `run1_sha256 == run2_sha256 == dadafcfc0153f002651c23975c3845dd3f8ca7896d263faf1c52eb54d64b8d7c` matches c12 auditor MODERATE disclosure (on-disk authoritative; c11/c12 brief transcription-error already logged in POR).

## Findings

One MINOR appended: POR c11 pins `drums.json` file-level SHA `f48b7d7fb1bf28d3ff6b9c9e17e64f1eef8586fa1e56d4cdbf7d0d7d1a2432ba` and `drums.replay_proof.json` file-level SHA `a7877f2ec1dd67b4a4d1cf9bde8fe12c2b32d95a63a6f2e1ed01f7d67bf2c8a0`. On-disk SHAs differ in the tail (16-hex prefix matches for both). Substantive claims (profile_id, params, verdict, byte-determinism ×2, canonical replay SHA) all intact. Same POR-anchor-drift class as findings 1–4 already logged; on-disk artifacts authoritative per FD-1. Additionally noted: POR c11 `Drums MIDI SHA 0fd71ce70a26365c8fb0f9f87531178f9f9c18cc419d042a3869989c990ef2` is malformed (62 hex chars vs disk `0fd71ce70a26365c2acf08b9f87531178f9f9c18cc419d042a3869989c990ef2` 64 hex chars). Rolled into the same finding.

## No CRITICAL / MODERATE surfaced

- c6 replay-program-invariance fix + c11 channel-aware extension are structurally sound and backward-compat regression is preserved (bass_v2 anchor byte-identical).
- c9 OPT1+OPT3 acceptance fork is operator-directive-anchored; c14 OPT3 revise correctly closes c13 audit findings.
- c11 drums SF2_RULED_OUT verdict (emb_cos 0.2374 < 0.40 retained floor) is internally consistent with c9 threshold-retirement scope (CG-bass ONLY per POR).

## Cumulative findings after this stage: 5 (all MINOR, all POR-anchor-drift)
