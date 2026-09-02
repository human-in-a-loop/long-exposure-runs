<!--
created: 2026-09-02T00:00:00Z
cycle: 4
run_id: run-2026-09-02T000000Z
agent: worker
milestone: M-V3-SPINE-1/rubric-v2-committed
-->

# M-V3-SPINE-1 — Rubric v2 (OPTION A adopted)

Supersedes: `docs/v3_spine_rubric.md` (rubric-v1, cycle 3).

Preserved: v1 rubric is a READ-ONLY historical anchor. Its SHA
(`b0031164e2a5cf78496a89e23cc9c5fdbbb2a90aa1770ca11ad9b40e8d54b555`)
is byte-identical pre==post this cycle.

Structural change (v1 → v2): the byte-determinism ×2 gate is redefined
per operator OPTION A (2026-09-02). MuScriptor's `--format midi` output
is demoted to a debug artifact and its determinism is NOT gated.

## Verdict rubric (frozen 3-verdict enum)

Three verdicts, exactly one fires per cycle.

### V3_SPINE_CHAIN_LANDS_pending_operator

**All of** the following:

(a) **A/B + full-song delivery artifacts** under
    `data/v3/deliveries/31a164f845f8e27e/` non-silent (`peak > 1e-4`);
    A/B WAVs 30 s ± 5 ms; sample-aligned to the chosen section
    `t = 233.63918367346938 .. 263.63918367346935 s`.

(b) **Byte-determinism ×2** holds across:
    - (i) all 6 stems + full-mix MuScriptor JSON events;
    - (ii) all 6 stems + full-mix canonicalized MIDI (produced by
      `scripts/v3_spine/midi_from_json_events.py` from the JSON events);
    - (iii) `merged.mid` + per-track WAVs + `full_reconstruction.wav` +
      `panel.tsv` + `verdict.json`.

    MuScriptor `--format midi` output is logged as `non_factor_debug`
    sidecar rows in `manifest.json.muscriptor_debug_midi_shas`; its
    determinism is NOT gated and its SHAs carry no action.

(c) **Sanity panel** 8-key finite, **no >2× regression** vs the c33 rc7
    anchor `panel_baseline_old_chain_v2.tsv`.

(d) **Structural gates** on `merged.mid`:
    - zero notes on GM program 4;
    - drums track on GM channel 10 with note count > 0;
    - bass track present with median MIDI pitch < 55;
    - vocals track present + flagged `voice_symbolic_do_not_render` +
      unrendered by fluidsynth.

(e) **Test suite** ≥14/16 tests green; anchor preservation
    ≥21 SHAs pre==post byte-exact; 0-ERROR `promise_check`.

(f) **Ledger event** `M-V3-SPINE-1/verdict-v2-emitted` carries
    `status: action_required` (canonical enum) with
    `blocked_on_operator: true` flag inside `verdict.json`.
    Operator LANDS is the only true gate; the cycle-4 verdict is at
    most `V3_SPINE_CHAIN_LANDS_pending_operator`.

### V3_SPINE_CHAIN_PARTIAL

Pipeline runs end-to-end but ≥1 of (a)–(e) fails in a specific,
honestly-reported way. First-class negative finding. Per-failure
diagnosis lands in `verdict.json.failures[]`.

### V3_SPINE_CHAIN_FAILS

Any of:
- **Rung-0 STOP**: canonical serializer nondeterministic on synthetic
  input (implementation bug vs its own spec).
- **Rung-1 STOP**: MuScriptor JSON events nondeterministic on any of
  the 4 deferred cycle-3 Run-2 probes.
- **Rung-1a STOP**: canonicalized MIDI nondeterministic on any of the
  7 probes despite JSON being deterministic (spec incomplete).
- Pipeline cannot produce non-silent A/B artifacts.

Ledger `status: action_required`; per Fixed Decision 1, no tuning,
no fallback, no retry.

## Rubric-hash chain

Three-way byte-equality required on close:
```
sha256(docs/v3_spine_rubric_v2.md)
  == data/v3_spine/rubric_hash_v2.txt
  == verdict.json.rubric_hash_v2
```

## Fixed Decisions (BINDING)

1. **No hand-rolled transcription; no tuning; no fallback.** OPTION A
   canonicalization is *serialization* of MuScriptor's JSON events, not
   transcription — the operator has explicitly ruled this within scope
   (2026-09-02).
2. htdemucs_6s baseline stems READ-ONLY (per-stem doctrine anchor).
3. FluidR3_GM.sf2 SHA `74594e8f…1cb0` READ-ONLY.
4. `scripts/palette_render/render_stem.py` SHA `214372d9…5b2b`
   READ-ONLY (DO-NOT-TOUCH lock from cycle 33).
5. `scripts/recreate_v2/rc*.py` all READ-ONLY.
6. **Panel is NEVER a LANDS gate.** Operator ear is the only LANDS
   authority.

## Instrument whitelist (per operator directive point 1)

Per-stem canonicalization uses a fixed instrument whitelist per stem
per `docs/v3_spine_instrument_whitelist_mapping.md` (cycle 3 anchor,
35 MuScriptor labels, zero MISSING_LABEL findings). Under OPTION A the
whitelist is unchanged from cycle 3.
