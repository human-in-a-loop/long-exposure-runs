# Verify pass 2 of 5 — Slice B: V3-FOCUS-1 fanout + palette proof

**Delta-audit scope.** Only new-since-baseline (2026-09-02 05:24:25 UTC)
milestones. Verified byte-exact against on-disk deliveries + ledger.

## Rome — c20 clone-1 focus-song LANDS

- `data/v3/deliveries/51e433ade2a845e1/cycle20/verdict.json` sha
  `d2c2d704ce910fde1b8110d0…` — byte-equal to plan-of-record narrative
  pin. `verdict = V3_FOCUS_SONG_LANDS_pending_operator`;
  `rubric_hash_v2 = c49db5a12e955f26c001165ad6e8f9d1…` — matches c4
  spec chain; `blocked_on_operator = true`.
- Delivery tree present: `original_ab.wav`, `reconstruction_ab.wav`,
  `full_reconstruction.wav`, `merged.mid`, `panel.{tsv,json}`,
  `tempo_choice.json`, `rc7_per_stem_loudness_operator_section.json`,
  `manifest.json`, `mix_match_operator_section.json` + per-stem
  muscriptor outputs under `muscriptor_operator_section/`.
- Ledger `M-V3-FOCUS-1/rome-slot-accepted-internal-gate` present per
  operator D-A internal-gate criterion.

## What If I Go — c20 clone-1 PARTIAL → c21 clone-1 LANDS restart

- c20 PARTIAL: `data/v3/deliveries/252eb21ce7df7328/cycle20/verdict.json`
  sha `bd394c43c6134811257bb9b2…` byte-equal to plan-of-record
  narrative pin. `verdict = V3_FOCUS_SONG_PARTIAL_pending_operator`.
  Honestly recorded session-boundary termination at muscriptor stage
  (3/7 probes completed on-disk).
- c21 LANDS restart:
  `data/v3/deliveries/252eb21ce7df7328/cycle21/verdict.json` sha
  `95edf6cc741366d5f87e68c8…` byte-equal to plan-of-record narrative
  pin. `verdict = V3_FOCUS_SONG_LANDS_pending_operator`;
  `rubric_hash_v2` byte-equal to spec chain; `blocked_on_operator =
  true`. c20 anchor SHAs preserved byte-identical per plan-of-record
  `wig-anchor-preservation-c21-verified` sub-leaf.
- Ledger row `M-V3-FOCUS-1/wig-slot-operator-accepted-2026-09-02`
  present.

## Disco A — c21 clone-0 focus-song LANDS

- `data/v3/deliveries/cdd2717e52820ff6/cycle21/verdict.json` sha
  `28c3392934db6071f926e9a8…` — byte-equal to plan-of-record narrative
  pin. `verdict = V3_FOCUS_SONG_LANDS_pending_operator`;
  `rubric_hash_v2` byte-equal to spec chain.
- Delivery tree present (same shape as Rome). c21 clone-0 sub-leaves
  (htdemucs section+full-song completed, muscriptor 7/7 byte-det ×2)
  registered under plan-of-record.
- Ledger row `M-V3-FOCUS-1/disco-a-slot-operator-accepted-2026-09-02`
  present.

## Peach Dream — c20 clone-2 PARTIAL Option 3 escape (terminal)

- `data/v3/deliveries/88d247468cb6d49f/cycle20/verdict.json` sha
  `d9bc2f590e1af21455cc3e71…` — byte-equal to plan-of-record narrative
  pin. `verdict = V3_FOCUS_SONG_PARTIAL`; `blocked_on_operator = true`
  with escalation block for root conductor + 3 named options (Option
  3 recommended). Retired at c24 via checkpointed-driver resume
  policy (`M-V3-FOCUS-1/peach-dream-resume-checkpointed` +
  `_plan/adopt-operator-checkpointed-driver-directive-2026-09-03`).

## Operator ear satisfaction 2026-09-02

- `M-V3-SPINE-1/operator-lands-2026-09-02` present as ledger row —
  Chicken Grease operator-approved verbatim.
- `M-V3-FOCUS-1/chicken-grease-slot-accepted`,
  `M-V3-FOCUS-1/wig-slot-operator-accepted-2026-09-02`,
  `M-V3-FOCUS-1/disco-a-slot-operator-accepted-2026-09-02`,
  `M-V3-FOCUS-1/operator-satisfied-2026-09-02` all landed as ledger
  rows. ≥3 focus-song operator-ear-accept gate satisfied ahead of
  Peach Dream / Rome ear resolution.

## Chicken Grease palette-render PALETTE_MOVES_PANEL (c21 clone-2)

- `data/v3/deliveries/31a164f845f8e27e/cycle21/verdict_palette.json`
  sha `5ba4eaca242fcd29efbbeca9…` — byte-equal to plan-of-record
  narrative pin. `verdict = PALETTE_MOVES_PANEL`;
  `rubric_hash_v2 = 9eb5523cbd090c388e30b0b271cb1dff…` — byte-equal
  to the palette-render rubric doc SHA cited in plan-of-record
  (`docs/v3_spine_chicken_grease_palette_render_c21_rubric.md`);
  `blocked_on_operator = true`.
- Delivery sibling `data/v3/deliveries/31a164f845f8e27e/palette_render/`
  contains `full_reconstruction_palette.wav` (10,584,058 bytes,
  non-silent), `per_stem/`, `manifest.json`,
  `panel_original_vs_palette.tsv`,
  `panel_fluidsynth_vs_palette.tsv`, `byte_determinism.json`,
  `fetchability_ladder.jsonl`, `anchor_preservation.json`.
- Anchor-preservation sanity: c5 operator-blessed
  `full_reconstruction_operator_section.wav` sha
  `cc919559b4508b6bfe868fa5433a50b6…` byte-equal on disk pre==post
  (matches plan-of-record c5 anchor).
- Ledger row
  `M-V3-SPINE-1/chicken-grease-palette-proof-landed-c21` records the
  palette proof landing per operator D-D unlock condition.

## Discipline notes

- All six primary verdict JSONs carry `rubric_hash_v2` matching their
  spec docs (five carry `c49db5a12e955f26…` from c4 spec chain, the
  palette verdict carries `9eb5523cbd090c38…` from the c21
  palette-render rubric).
- No new artifact directly reopens a prior baseline finding.
- Slice-B palette_render/anchor_preservation.json is a pre-snapshot
  (contains `entries` + `phase`, no `all_match` field) — the "61/61
  byte-identical" narrative claim rests on the pre/post pair recorded
  in the palette-render sub-leaf ledger events, which is consistent
  with the on-disk c5 anchor SHA still being byte-identical. Not
  flagged as a defect (delta scope does not re-audit committed
  baseline anchors that a later cycle explicitly preserves and
  re-verifies).

## Findings this slice

None at CRITICAL or MODERATE severity. Slice B chain intact.
