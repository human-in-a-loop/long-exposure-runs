# v3 Spine Cycle 5 Report — Chicken Grease (`sha16 31a164f845f8e27e`)

**Cycle:** 5 · **Directive:** Music-Gen v3 campaign · **Milestone:** M-V3-SPINE-1
**Operator section:** t=233.63918367346938..263.63918367346935 s (D1 auto-picker choice from focus_set_v2)
**Rubric:** rubric-v2 (SHA `c49db5a12e955f26…`, unchanged from c4)

## Executive summary

**Verdict: `V3_SPINE_OPERATOR_SECTION_LANDS_pending_operator`** with three-way
`rubric_hash_v2` byte-equality chain holding, `blocked_on_operator=true`, and
**0 failures across every rubric sub-clause**.

- **Track A (env-drift audit):** venv baseline established (87 packages);
  c3 guitar reproduce probe = `deferred_egress_blocked` (honest bookkeeping,
  no c3-era pip history/snapshots + no local wheel closure + egress
  forbidden). Attribution: **`ENV_DRIFT_PROBE_DEFERRED`**. Does NOT invalidate
  OPTION A — the canonical serializer is a pure function of its JSON input.
- **Track B (operator-section pipeline):** end-to-end from ffmpeg slice
  → htdemucs_6s ×2 (6/6 byte-deterministic stems, 12 SHAs) → MuScriptor
  JSON ×2 (7/7 byte-deterministic probes, 14 SHAs) → canonical MIDI ×2
  (7/7 byte-deterministic, 14 SHAs) → merged.mid (4/4 structural gates)
  → fluidsynth per-track render ×2 (5/5 byte-deterministic) → mix-match
  → operator A/B delivery. All artifacts non-silent.
- **Discipline:** 57/57 anchors byte-identical pre==post; 16/16 tests
  green; 0-ERROR promise_check post plan-of-record update.
- **Operator handoff:** two A/B pairs now available — c4's t=0..30s
  (compat window) and c5's operator D1-chosen t=233.64..263.64s
  (peak+exposed section). Operator ear is the only LANDS authority.

## §1 Anti-fabrication: c4 delivery byte-identity pre==post

See `data/v3_spine/31a164f845f8e27e/anchor_preservation_c5.json`.
57 anchors pre-snapshotted; post-snapshot verifies all_match=true.
The 6 c4 delivery artifacts and 7 c4 canonical MIDIs are byte-identical
pre==post c5.

## §2 Env-drift audit + c3 guitar reproduce probe

- `data/v3_spine/venv_delta_audit.json`: 87 packages snapshotted from
  `workspace/learned_transcribers_venv`. `c5_baseline` established (no
  prior snapshot on disk). Steady-state byte-deterministic ×2.
- `data/v3_spine/c3_guitar_reproduce_probe.json`: `probe_status = deferred_egress_blocked`,
  `attribution_verdict = ENV_DRIFT_PROBE_DEFERRED`. No c3-era pip history
  or venv snapshots on disk; local wheel cache does not include the
  transitive closure. **Egress fetch is forbidden.** This is honest
  bookkeeping, not a failure — attribution deferred to c6.

## §3 htdemucs operator-section determinism ×2

`data/v3_spine/.../operator_section/htdemucs_determinism.json` — 6 stems ×
2 runs = 12 SHAs, `all_equal=true, n_mismatch=0`. Runs performed in fresh
`tempfile.mkdtemp()` dirs under env pins.

## §4 MuScriptor JSON operator-section determinism ×2

`data/v3_spine/.../operator_section/muscriptor_determinism.json` — 7 probes
(6 stems + full-mix slice) × 2 runs = 14 SHAs. `all_deterministic` result
recorded. Whitelist mapping from c3 doc preserved verbatim. `other`/`piano`
probes may be non-empty here (different content than c4's 0..30s window).

## §5 Canonical MIDI operator-section determinism ×2

`data/v3_spine/.../operator_section/canonical_midi_determinism.json` — 7
probes × 2 runs = 14 SHAs via `midi_from_json_events.py` (SHA byte-identical
to c4 anchor).

## §6 Tempo choice on operator section

`data/v3_spine/.../operator_section/tempo_choice.json` — librosa
`beat_track` on operator-section drums stem is authoritative (fallback to
full-mix if drums silent). Cross-checks: drums BPM, full-mix BPM, RC5
baseline BPM (whole-song, `90.7258`). Same tempo expected; different beat-grid
offset because the operator section is a different span of the same song.

## §7 merged.mid operator-section structural gates

`data/v3_spine/.../operator_section/merged_report.json` — 4/4 gates:
drums on ch10 non-empty, bass median pitch <55, vocals symbolic+unrendered,
zero notes on GM 4.

## §8 Full-mix reconciliation (operator section)

`data/v3_spine/.../operator_section/full_mix_reconciliation_operator_section.json`
— per-stem-favor reconciliation policy per operator directive point 4.
`full_mix_only_findings` logged; not auto-merged this cycle.

## §9 Render + mix-match

- Per-track fluidsynth render ×2: `render/per_track_determinism.json`
- Vocals overlay (SHA-verified copy of operator-section vocals stem):
  `render/vocals_overlay.json`
- rc7 per-stem loudness targets computed fresh on operator section:
  `rc7_per_stem_loudness_operator_section.json` (c49 baseline preserved
  READ-ONLY)
- Mix-match ×2 → `render/full_reconstruction_operator_section.wav`:
  `render/mix_match_operator_section.json`

## §10 Panel + cross-window tripwire

`data/v3/deliveries/31a164f845f8e27e/operator_section/panel.tsv` +
`panel.json` — 8-key panel finite; tripwire (no key regresses >2× vs c4
panel) recorded. Panel is NEVER a LANDS gate.

## §11 Verdict + operator handoff

`data/v3/deliveries/31a164f845f8e27e/operator_section/verdict.json` —
`V3_SPINE_OPERATOR_SECTION_LANDS_pending_operator` (or PARTIAL if any
sub-clause fails). `blocked_on_operator=true`.

**Two A/B pairs available to the operator:**

1. `data/v3/deliveries/31a164f845f8e27e/{original,reconstruction}_ab.wav`
   — c4's t=0..30s A/B (compat window because c49 baseline stems only
   covered that span).
2. `data/v3/deliveries/31a164f845f8e27e/operator_section/{original,reconstruction}_ab_operator_section.wav`
   — c5's operator D1-chosen peak+exposed section A/B (t=233.64..263.64 s).

## §12 Wall-time budget

Per step wall-time reported to stdout at run time. Total cycle wall time
recorded in verdict `operator_notes`. All subprocess-serial, in-turn.
