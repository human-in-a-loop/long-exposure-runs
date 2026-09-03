# c21 clone-1 (fork 0a1b1dca4f9b) merge report — WIG restart

Sandbox constraint: cannot write to `/home/user/music-gen-instance-v3/fork-0a1b1dca4f9b/clone-1/merge_report.md` (outside workspace). Root conductor should copy this file to the fanout path.

## Outcome

**Verdict**: `V3_FOCUS_SONG_LANDS_pending_operator` — WIG restart from PARTIAL to LANDS on internal gates. Third M-V3-FOCUS-1 accept.

## Cross-branch conflict scan

- Ledger events land under `-clone-1` suffix on infra families via c33 harness auto-suffix.
- Substantive `M-V3-FOCUS-1/wig-*` unsuffixed per c32 convention.
- No writes to Chicken Grease `data/v3/deliveries/31a164f845f8e27e/*` (verified).
- No writes to Rome `data/v3/deliveries/51e433ade2a845e1/*` (verified).
- No writes to Peach Dream `data/v3/deliveries/88d247468cb6d49f/*` (verified).
- All WIG writes under `data/v3/deliveries/252eb21ce7df7328/` + `data/v3_spine/252eb21ce7df7328/`.
- `scripts/palette_render/render_stem.py` byte-identical pre==post.
- `scripts/v3_spine/midi_from_json_events.py` byte-identical pre==post.

## Anchors preserved

12 c20 htdemucs stem SHAs + 3 c20 MuScriptor JSON SHAs + 2 c20 MuScriptor MID SHAs all byte-identical pre==post. Verified in `data/v3_spine/252eb21ce7df7328/operator_section/anchor_preservation_c21.json` (n_total=11, n_match=11, n_mismatch=0, all_match=true).

## Key SHAs

- c21 verdict.json sha: `95edf6cc741366d5…`
- delivery manifest.json sha: `9a8a09d0f553a79f…`
- merged.mid sha: `a93f5c2ae16e5cac…`
- full_reconstruction_operator_section.wav sha: `f2deaf6aecb5afa5…`
- rubric_hash_v2 (three-way byte-equality): `c49db5a12e955f26…`

## Tests

12/12 PASS in `tests/test_v3_focus_wig_c21.py`.

## promise_check

0-ERROR post-emission.

## Full report

See `docs/v3_focus_wig_restart_c21_report.md` for full detail.

## Handoffs for c22

1. Register 8 clone-1 ledger events + this report + main report in plan-of-record.
2. Emit M-V3-FOCUS-1 parent rollup advancing to `validated/high` (3 substantive accepts land: Chicken Grease, Rome, WIG).
3. Draft batch manifest listing all 3 focus A/B pairs for operator review per operator note in c20 story.
4. Peach Dream Option 3 adjudication (PARTIAL as terminal) — recommended.
5. Disco A now optional 5th focus song; no longer gating.
