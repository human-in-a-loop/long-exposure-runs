# c21 clone-0 Disco A merge report (fork 0a1b1dca4f9b)

## Verdict

**`V3_FOCUS_SONG_LANDS_pending_operator`** — Disco A (sha16
`cdd2717e52820ff6`) full v3 per-stem chain end-to-end LANDS on all
internal-gate criteria per operator decision D-A (2026-09-02,
autonomous completion). **Third M-V3-FOCUS-1 internal-gate accept**,
closing the ≥3-song gate independent of WIG restart or Peach Dream
Option 1/2 decisions.

## On-disk verdict SHA

`data/v3/deliveries/cdd2717e52820ff6/cycle21/verdict.json` →
`28c3392934db6071f926e9a8380569970cfbd4b6fa08fff3551e5d63ec9859b2`

## Cross-branch invariants (verified pre==post)

| Anchor | SHA (READ-ONLY, unchanged) |
|--------|----------------------------|
| Chicken Grease c5 operator delivery `full_reconstruction_operator_section.wav` | `cc919559b4508b6bfe868fa5433a50b6805c43bab763665a5f2be367f01bbbd7` (baseline anchor per brief; not this clone's write path) |
| Rome c20 clone-1 verdict `data/v3/deliveries/51e433ade2a845e1/cycle20/verdict.json` | `d2c2d704ce910fde1b8110d07e978de998757a6d4c5564b32b6e272197a7afa6` |
| Rubric v2 doc SHA | `c49db5a12e955f26c001165ad6e8f9d191bc26bfd96e24c1b163adc37016451a` |
| Focus set v2 anchor `data/recreate_v2/focus_set_v2.json` | unchanged |

## This clone's write scope (all under Disco A sha16 prefix — DISJOINT from peer clones)

- `data/v3/deliveries/cdd2717e52820ff6/` (delivery + operator_section + cycle21)
- `data/v3_spine/cdd2717e52820ff6/operator_section/` + `full_song/`
- `scripts/v3_spine/*_song_cdd2717e52820ff6.py` (12 sibling scripts)
- `scripts/v3_spine/verdict_song_cdd2717e52820ff6.py` (edited from Rome template: c20_backref, cycle21, operator_notes)
- `tests/test_v3_focus_disco_a_c21.py` (12/12 PASS, c19_backref → c20_backref fix)
- `docs/v3_focus_disco_a_c21_report.md`
- `logs/c21_disco_a/htdemucs_full.log`
- `scratchpad/emit_c21_events.py` + `tools/stale/emit_c21_events.py`

## Sub-clause result table (rubric v2)

| Clause | Result |
|--------|--------|
| (a) delivery present, non-silent | **PASS** |
| (b.i) htdemucs section byte-det ×2 | **PASS** (n_mismatch=0) |
| (b.i) htdemucs full-song byte-det ×2 | **PASS** (n_mismatch=0) |
| (b.ii) MuScriptor 7 probes byte-det ×2 | **PASS** (7/7) |
| (b.iii) canonical MIDI 7 probes byte-det ×2 | **PASS** (7/7) |
| (b.iv) per-track fluidsynth 5 tracks byte-det ×2 | **PASS** (5/5) |
| (b.v) full reconstruction WAV byte-det ×2 | **PASS** |
| (c) both panels 8-key finite | **PASS** |
| (d) structural gates on merged.mid | **PASS** (4/4) |
| (e) rubric_hash_v2 three-way chain byte-equal | **PASS** |
| (f) blocked_on_operator=true | **PASS** |

## Ledger events emitted (9)

Emitted via `python3 -m long_exposure.tools.ledger_append`
(auto-routed to per-clone shadow ledger via `AGENT_FORK_ID`
env var). 5 substantive `M-V3-FOCUS-1/disco-a-*` labels are
unsuffixed per c32 convention; infra families carry `-clone-0`
suffix per c33 harness auto-suffix.

1. `_plan/register-c21-disco-a-milestones-clone-0`
2. `M-V3-FOCUS-1/disco-a-htdemucs-section-completed`
3. `M-V3-FOCUS-1/disco-a-htdemucs-full-song-completed`
4. `M-V3-FOCUS-1/disco-a-muscriptor-completed`
5. `M-V3-FOCUS-1/disco-a-verdict-emitted`
6. `M-V3-FOCUS-1/disco-a-slot-accepted-internal-gate`
7. `M-INGEST-1/egress-probe-cycle21-clone-0`
8. `_infra/adopt-cycle21-tests-clone-0`
9. `_archive/cycle-21-scratch-clone-0`

## Tests

`tests/test_v3_focus_disco_a_c21.py` — 12/12 PASS.

## promise_check

0-ERROR post-emit (WARNs pre-existing and unchanged by this branch).

## Handoff notes for root conductor

- M-V3-FOCUS-1 now has ≥3 internal-gate accepts:
  1. Chicken Grease (operator-accepted 2026-09-02)
  2. Rome c20 clone-1 (`d2c2d704…7afa6`, `V3_FOCUS_SONG_LANDS_pending_operator`)
  3. **Disco A c21 clone-0 (this)** (`28c33929…9859b2`, `V3_FOCUS_SONG_LANDS_pending_operator`)
- Suggested: emit single batch manifest listing all focus A/B pairs for
  operator review (per c20 auditor precedent).
- WIG restart and Peach Dream Option 1/2/3 remain as separate work
  items; they no longer gate M-V3-FOCUS-1 closure under D-A.
- Halt-list constraints all respected: no `M-EAR-1/*`, `M-GEN-1/*`,
  `M-V3-EAR/*`, `M-V3-GEN/*` events; no CLAP re-fetch; no VST3
  state-extraction; no corpus breadth or ingest touched.
